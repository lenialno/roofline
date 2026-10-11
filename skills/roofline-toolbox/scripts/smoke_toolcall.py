#!/usr/bin/env python3
"""Tool-calling contract check for an OpenAI-compatible endpoint. Stdlib only.

Checks (required unless marked optional):
  1. non-stream: a prompt that needs a tool returns finish_reason=tool_calls with valid JSON arguments
  2. stream: tool_calls arrive as deltas and assemble into the same valid call
  3. negative: a prompt that needs no tool returns content and no tool_calls
  4. round trip: assistant tool_call + tool result produce a final answer that uses the result
  5. parallel (optional, informational): two cities produce two calls
Exit 1 on any required failure. Diagnoses the usual parser misconfigurations from the raw output.
"""
import argparse
import json
import os
import sys
import urllib.error
import urllib.request


def load_env_file():
    """KEY=value lines from $INFER_ENV_FILE or ./inference.env fill variables that are unset or empty."""
    path = os.environ.get("INFER_ENV_FILE") or os.path.join(os.getcwd(), "inference.env")
    try:
        with open(path) as fh:
            for line in fh:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                k, v = k.strip(), v.strip().strip('"').strip("'")
                if k and not os.environ.get(k):
                    os.environ[k] = v
    except OSError:
        pass


def setting(name, default):
    v = os.environ.get(name)
    return v if v not in (None, "") else default


TOOLS = [{
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": "Get the current weather for a city",
        "parameters": {
            "type": "object",
            "properties": {"city": {"type": "string", "description": "City name"}},
            "required": ["city"],
        },
    },
}]

MARKERS = ("<tool_call>", "<function=", "<|tool_call", "```json", "[TOOL_CALLS]", "<function_call>", "<tool_call", "<|python_tag|>")


class Client:
    def __init__(self, url, model, timeout):
        self.url, self.model, self.timeout = url, model, timeout

    def post(self, body, stream=False):
        body = dict(body, model=self.model, temperature=0)
        req = urllib.request.Request(self.url + "/v1/chat/completions", data=json.dumps(body).encode(),
                                     headers={"Content-Type": "application/json"})
        key = os.environ.get("INFER_API_KEY")
        if key:
            req.add_header("Authorization", "Bearer " + key)
        try:
            r = urllib.request.urlopen(req, timeout=self.timeout)
        except urllib.error.HTTPError as e:
            raise RuntimeError("HTTP %s: %s" % (e.code, e.read()[:400].decode("utf-8", "replace")))
        if not stream:
            return json.load(r)
        chunks = []
        for raw in r:
            line = raw.decode("utf-8", "replace").strip()
            if line.startswith("data:"):
                data = line[5:].strip()
                if data == "[DONE]":
                    break
                try:
                    chunks.append(json.loads(data))
                except ValueError:
                    pass
        return chunks


def assemble_stream(chunks):
    content, finish = "", None
    calls = {}
    for ch in chunks:
        for c in ch.get("choices") or []:
            d = c.get("delta") or {}
            if d.get("content"):
                content += d["content"]
            for tc in d.get("tool_calls") or []:
                i = tc.get("index", 0)
                slot = calls.setdefault(i, {"id": None, "name": "", "arguments": ""})
                if tc.get("id"):
                    slot["id"] = tc["id"]
                fn = tc.get("function") or {}
                if fn.get("name"):
                    slot["name"] += fn["name"]
                if fn.get("arguments"):
                    slot["arguments"] += fn["arguments"]
            if c.get("finish_reason"):
                finish = c["finish_reason"]
    return content, finish, [calls[k] for k in sorted(calls)]


def check_call(calls, want_city):
    """-> (ok, detail)"""
    if not calls:
        return False, "no tool_calls in response"
    c = calls[0]
    name = c.get("name") or (c.get("function") or {}).get("name")
    args = c.get("arguments") if "arguments" in c else (c.get("function") or {}).get("arguments")
    if name != "get_weather":
        return False, "wrong function name %r" % name
    try:
        parsed = json.loads(args) if isinstance(args, str) else args
    except ValueError as e:
        return False, "arguments are not valid JSON (%s): %r" % (e, args)
    if not isinstance(parsed, dict) or "city" not in parsed:
        return False, "arguments lack required 'city': %r" % parsed
    if want_city.lower() not in str(parsed["city"]).lower():
        return False, "city mismatch: %r" % parsed["city"]
    return True, "get_weather(%s)" % json.dumps(parsed)


def diagnose(content):
    c = content or ""
    if any(m in c for m in MARKERS):
        return ("model emitted the tool call as text: parser not enabled or wrong parser. "
                "vLLM: --enable-auto-tool-choice --tool-call-parser <name>; SGLang: --tool-call-parser <name>. "
                "Pick the parser for this model family (see roofline-toolcall skill).")
    if c.strip():
        return "model answered in prose instead of calling the tool: chat template may lack tool support, or the quantized model lost tool-use quality"
    return "empty content and no tool_calls: check server log for template or parser errors"


def main():
    ap = argparse.ArgumentParser()
    load_env_file()
    ap.add_argument("--url", default=setting("INFER_URL", "http://127.0.0.1:8000"))
    ap.add_argument("--model", default=setting("BENCH_MODEL", ""))
    ap.add_argument("--timeout", type=float, default=float(setting("SMOKE_TIMEOUT", 120)))
    args = ap.parse_args()
    url = args.url.rstrip("/")
    if url.endswith("/v1"):
        url = url[:-3]
    model = args.model
    if not model:
        try:
            req = urllib.request.Request(url + "/v1/models")
            key = os.environ.get("INFER_API_KEY")
            if key:
                req.add_header("Authorization", "Bearer " + key)
            with urllib.request.urlopen(req, timeout=10) as r:
                model = json.load(r)["data"][0]["id"]
        except Exception as e:
            print("smoke-toolcall: cannot resolve model: %s" % e, file=sys.stderr)
            return 2
    cl = Client(url, model, args.timeout)
    print("smoke-toolcall: %s model=%s" % (url, model))
    failed = 0

    def report(name, ok, detail, required=True):
        nonlocal failed
        tag = "PASS" if ok else ("FAIL" if required else "INFO")
        if not ok and required:
            failed += 1
        print("%s %-10s %s" % (tag, name, detail))

    sys_msg = {"role": "system", "content": "You are a helpful assistant. Use tools when they are needed."}
    ask = {"role": "user", "content": "What is the weather in Paris right now? Use the get_weather tool."}

    # 1 non-stream
    try:
        resp = cl.post({"messages": [sys_msg, ask], "tools": TOOLS, "tool_choice": "auto", "max_tokens": 256})
        msg = resp["choices"][0]["message"]
        calls = msg.get("tool_calls") or []
        ok, detail = check_call(calls, "Paris")
        fr = resp["choices"][0].get("finish_reason")
        if ok and fr != "tool_calls":
            detail += "  (finish_reason=%r, expected 'tool_calls')" % fr
        if not ok:
            detail += " | " + diagnose(msg.get("content"))
        report("nonstream", ok, detail)
        first_call = calls[0] if ok else None
    except Exception as e:
        report("nonstream", False, str(e)[:300] + " | if the error mentions tools or tool_choice: enable auto tool choice on the server")
        first_call = None

    # 2 stream
    try:
        chunks = cl.post({"messages": [sys_msg, ask], "tools": TOOLS, "tool_choice": "auto", "max_tokens": 256, "stream": True}, stream=True)
        content, finish, calls = assemble_stream(chunks)
        ok, detail = check_call(calls, "Paris")
        if ok and not calls[0].get("id"):
            detail += "  (no id in streamed tool_call; some clients require it)"
        if ok and finish != "tool_calls":
            detail += "  (finish_reason=%r)" % finish
        if not ok:
            detail += " | streamed %d chunks | " % len(chunks) + diagnose(content)
        report("stream", ok, detail)
    except Exception as e:
        report("stream", False, str(e)[:300])

    # 3 negative
    try:
        resp = cl.post({"messages": [sys_msg, {"role": "user", "content": "Reply with the single word: hello"}], "tools": TOOLS, "tool_choice": "auto", "max_tokens": 32})
        msg = resp["choices"][0]["message"]
        calls = msg.get("tool_calls") or []
        content = (msg.get("content") or "").strip()
        ok = not calls and bool(content)
        report("negative", ok, "no false tool call, content=%r" % content[:40] if ok else "called a tool without need (%d calls) or empty content %r" % (len(calls), content[:40]))
    except Exception as e:
        report("negative", False, str(e)[:300])

    # 4 round trip
    try:
        call_id = (first_call or {}).get("id") or "call_smoke_1"
        msgs = [sys_msg, ask,
                {"role": "assistant", "content": None, "tool_calls": [{"id": call_id, "type": "function", "function": {"name": "get_weather", "arguments": json.dumps({"city": "Paris"})}}]},
                {"role": "tool", "tool_call_id": call_id, "content": json.dumps({"city": "Paris", "temperature_c": 21, "condition": "sunny"})}]
        resp = cl.post({"messages": msgs, "tools": TOOLS, "tool_choice": "auto", "max_tokens": 128})
        msg = resp["choices"][0]["message"]
        content = (msg.get("content") or "")
        calls = msg.get("tool_calls") or []
        ok = bool(content.strip()) and not calls and ("21" in content or "sunny" in content.lower())
        report("roundtrip", ok, "final answer uses tool result: %r" % content.strip()[:60] if ok else "answer=%r tool_calls=%d (expected prose using 21/sunny, no new call) | if HTTP 400: chat template rejects role=tool messages" % (content.strip()[:60], len(calls)))
    except Exception as e:
        report("roundtrip", False, str(e)[:300] + " | HTTP 400 here usually means the chat template has no tool-message support")

    # 5 parallel (informational)
    try:
        resp = cl.post({"messages": [sys_msg, {"role": "user", "content": "Get the weather in Paris and in Berlin using the tool."}], "tools": TOOLS, "tool_choice": "auto", "max_tokens": 256})
        calls = resp["choices"][0]["message"].get("tool_calls") or []
        report("parallel", len(calls) >= 2, "%d tool call(s) for two cities%s" % (len(calls), "" if len(calls) >= 2 else " (parallel calls not produced; fine unless clients rely on them)"), required=False)
    except Exception as e:
        report("parallel", False, str(e)[:200], required=False)

    print("smoke-toolcall: %s" % ("PASS" if failed == 0 else "FAIL (%d required checks failed)" % failed))
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
