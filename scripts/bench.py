#!/usr/bin/env python3
"""Fixed SLO benchmark against an OpenAI-compatible endpoint. Stdlib only.

N streaming chat requests at concurrency C, each with ~INPUT_TOKENS prompt and exactly
OUTPUT_TOKENS output (ignore_eos). Reports p50/p95/p99 of TTFT, TPOT and e2e, plus
throughput. Exit 1 when p95 TTFT or p95 TPOT exceeds the SLO or any request fails.
The prompt is deterministic (seeded), so two runs on the same server are comparable.
"""
import argparse
import json
import os
import random
import sys
import threading
import time
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


WORDS = ("inference engine serves tokens batch cache prefill decode latency throughput "
         "memory bandwidth kernel attention quantize router queue replica metric budget").split()


def build_prompt(n_tokens, seed=7):
    rnd = random.Random(seed)
    n_words = max(8, int(n_tokens / 1.3))
    body = " ".join(rnd.choice(WORDS) for _ in range(n_words))
    return "Context:\n" + body + "\n\nTask: continue the text with exactly 300 more words."


def pct(xs, p):
    if not xs:
        return None
    xs = sorted(xs)
    k = (len(xs) - 1) * p
    f = int(k)
    c = min(f + 1, len(xs) - 1)
    return xs[f] + (xs[c] - xs[f]) * (k - f)


def one_request(args, model, prompt, result):
    body = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": args.output_tokens,
        "temperature": 0,
        "stream": True,
        "stream_options": {"include_usage": True},
        "ignore_eos": True,
    }
    req = urllib.request.Request(args.url + "/v1/chat/completions", data=json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json"})
    key = os.environ.get("INFER_API_KEY")
    if key:
        req.add_header("Authorization", "Bearer " + key)
    t0 = time.monotonic()
    t_first = None
    t_last = None
    chunks = 0
    usage_out = None
    try:
        with urllib.request.urlopen(req, timeout=args.timeout) as r:
            for raw in r:
                line = raw.decode("utf-8", "replace").strip()
                if not line.startswith("data:"):
                    continue
                data = line[5:].strip()
                if data == "[DONE]":
                    break
                try:
                    obj = json.loads(data)
                except ValueError:
                    continue
                if obj.get("usage"):
                    usage_out = obj["usage"].get("completion_tokens")
                for ch in obj.get("choices") or []:
                    delta = ch.get("delta") or {}
                    if delta.get("content") or delta.get("reasoning_content") or delta.get("reasoning"):
                        now = time.monotonic()
                        if t_first is None:
                            t_first = now
                        t_last = now
                        chunks += 1
    except urllib.error.HTTPError as e:
        result.append({"error": "HTTP %s: %s" % (e.code, e.read()[:200].decode("utf-8", "replace"))})
        return
    except Exception as e:
        result.append({"error": str(e)})
        return
    t_end = time.monotonic()
    out_tokens = usage_out or chunks
    if t_first is None or out_tokens < 2:
        result.append({"error": "no streamed content (out_tokens=%s)" % out_tokens})
        return
    result.append({
        "ttft": t_first - t0,
        "tpot": (t_last - t_first) / max(out_tokens - 1, 1),
        "e2e": t_end - t0,
        "out": out_tokens,
    })


def main():
    ap = argparse.ArgumentParser()
    load_env_file()
    ap.add_argument("--url", default=setting("INFER_URL", "http://127.0.0.1:8000"))
    ap.add_argument("--model", default=setting("BENCH_MODEL", ""))
    ap.add_argument("--n", type=int, default=int(setting("BENCH_N", 32)))
    ap.add_argument("--concurrency", type=int, default=int(setting("BENCH_C", 8)))
    ap.add_argument("--input-tokens", type=int, default=int(setting("BENCH_IN", 2048)))
    ap.add_argument("--output-tokens", type=int, default=int(setting("BENCH_OUT", 256)))
    ap.add_argument("--slo-ttft-p95-ms", type=float, default=float(setting("SLO_TTFT_P95_MS", 2000)))
    ap.add_argument("--slo-tpot-p95-ms", type=float, default=float(setting("SLO_TPOT_P95_MS", 60)))
    ap.add_argument("--timeout", type=float, default=float(setting("BENCH_TIMEOUT", 300)))
    ap.add_argument("--json", action="store_true", help="print a JSON summary line at the end")
    args = ap.parse_args()
    args.url = args.url.rstrip("/")
    if args.url.endswith("/v1"):
        args.url = args.url[:-3]

    model = args.model
    if not model:
        try:
            req = urllib.request.Request(args.url + "/v1/models")
            key = os.environ.get("INFER_API_KEY")
            if key:
                req.add_header("Authorization", "Bearer " + key)
            with urllib.request.urlopen(req, timeout=10) as r:
                model = json.load(r)["data"][0]["id"]
        except Exception as e:
            print("bench: cannot resolve model from %s/v1/models: %s" % (args.url, e), file=sys.stderr)
            return 2

    prompt = build_prompt(args.input_tokens)
    results = []
    lock = threading.Lock()
    idx = {"i": 0}

    def worker():
        while True:
            with lock:
                if idx["i"] >= args.n:
                    return
                idx["i"] += 1
            local = []
            one_request(args, model, prompt, local)
            with lock:
                results.extend(local)

    print("bench: %s model=%s n=%d c=%d in~%d out=%d" % (args.url, model, args.n, args.concurrency, args.input_tokens, args.output_tokens))
    wall0 = time.monotonic()
    threads = [threading.Thread(target=worker) for _ in range(args.concurrency)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    wall = time.monotonic() - wall0

    errors = [r for r in results if "error" in r]
    okr = [r for r in results if "error" not in r]
    print("requests ok/err    %d / %d   wall %.1f s" % (len(okr), len(errors), wall))
    for e in errors[:3]:
        print("  error: %s" % e["error"])
    if not okr:
        print("bench: no successful requests", file=sys.stderr)
        return 1
    ttft = [r["ttft"] for r in okr]
    tpot = [r["tpot"] for r in okr]
    e2e = [r["e2e"] for r in okr]
    out_tokens = sum(r["out"] for r in okr)
    print("%-6s %10s %10s %10s" % ("metric", "p50", "p95", "p99"))
    for name, xs in (("ttft", ttft), ("tpot", tpot), ("e2e", e2e)):
        print("%-6s %8.0f ms %8.0f ms %8.0f ms" % (name, pct(xs, .5) * 1000, pct(xs, .95) * 1000, pct(xs, .99) * 1000))
    print("throughput         %.0f output tok/s total; %.0f tok/s per stream (median)" % (out_tokens / wall, 1 / pct(tpot, .5)))
    ttft95 = pct(ttft, .95) * 1000
    tpot95 = pct(tpot, .95) * 1000
    verdict = "PASS"
    if ttft95 > args.slo_ttft_p95_ms:
        verdict = "FAIL"
        print("SLO  ttft p95 %.0f ms > %.0f ms" % (ttft95, args.slo_ttft_p95_ms))
    if tpot95 > args.slo_tpot_p95_ms:
        verdict = "FAIL"
        print("SLO  tpot p95 %.0f ms > %.0f ms" % (tpot95, args.slo_tpot_p95_ms))
    if errors:
        verdict = "FAIL"
    print("SLO  %s (ttft p95 <= %.0f ms, tpot p95 <= %.0f ms, 0 errors)" % (verdict, args.slo_ttft_p95_ms, args.slo_tpot_p95_ms))
    if args.json:
        print(json.dumps({"model": model, "n": args.n, "c": args.concurrency, "in": args.input_tokens, "out": args.output_tokens,
                          "ttft_p50_ms": pct(ttft, .5) * 1000, "ttft_p95_ms": ttft95, "tpot_p50_ms": pct(tpot, .5) * 1000,
                          "tpot_p95_ms": tpot95, "e2e_p95_ms": pct(e2e, .95) * 1000, "tok_s": out_tokens / wall,
                          "errors": len(errors), "verdict": verdict}))
    return 0 if verdict == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
