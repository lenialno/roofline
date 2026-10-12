#!/usr/bin/env python3
"""Check that the Roofline tables match the runtime installed on this host. Stdlib only.

1. installed vLLM or SGLang version against the version the parser table was checked with
2. parser names from the table against the parser registry of the installed package
   (source files are read as text, the runtime is not imported and no model is loaded)
3. when the endpoint answers: series that metrics.py reads against /metrics, then smoke_toolcall.py

No request leaves the host except to INFER_URL. Output ends with a verdict and, on a mismatch,
the issue template to report it with.
Exit codes: 0 everything matches, 1 mismatch or failed check, 2 no runtime found.
"""
import importlib.util
import os
import re
import subprocess
import sys
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ISSUE_URL = "https://github.com/lenialno/roofline/issues/new?template=mismatch.yml"

# parser registries inside the installed package, newest layout first
REGISTRIES = {
    "vllm": {
        "tool": ["tool_parsers/__init__.py", "entrypoints/openai/tool_parsers/__init__.py"],
        "reasoning": ["reasoning/__init__.py"],
    },
    "sglang": {
        "tool": ["srt/function_call/function_call_parser.py"],
        "reasoning": ["srt/parser/reasoning_parser.py", "srt/reasoning_parser.py"],
    },
}
# series a healthy endpoint of each runtime exposes; metrics.py needs them
CORE_SERIES = {
    "vllm": ["vllm:num_requests_running", "vllm:num_requests_waiting", "vllm:time_to_first_token_seconds"],
    "sglang": ["sglang:num_running_reqs", "sglang:num_queue_reqs", "sglang:time_to_first_token_seconds"],
}


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


def package_dir(name):
    """Directory of an installed package without importing it (find_spec runs no package code)."""
    try:
        spec = importlib.util.find_spec(name)
    except (ImportError, ValueError):
        return None
    if spec and spec.submodule_search_locations:
        return list(spec.submodule_search_locations)[0]
    return None


def installed_version(name):
    try:
        from importlib.metadata import version
        return version(name)
    except Exception:
        return None


def vtuple(v):
    return tuple(int(x) for x in re.findall(r"\d+", v or "")[:3])


def registry_names(pkg, files):
    """Parser names registered in the first existing file: dict keys or register_module(...) calls."""
    for rel in files:
        path = os.path.join(pkg, rel)
        if not os.path.isfile(path):
            continue
        text = open(path, encoding="utf-8", errors="replace").read()
        # the registry is the largest flat dict literal of name: (module, class) or name: Detector
        names = set()
        for block in re.findall(r"\{[^{}]*\}", text):
            found = set(re.findall(r'^\s*"([A-Za-z0-9_.-]+)":\s*(?:\(|_?[A-Z]\w*Detector\b)', block, re.M))
            if len(found) > len(names):
                names = found
        for args in re.findall(r"register_module\(([^)]*)\)", text):
            names |= set(re.findall(r'["\']([A-Za-z0-9_.-]+)["\']', args))
        return rel, names
    return None, set()


def table_names(path):
    """Checked versions and parser names per runtime from references/parsers.md."""
    text = open(path, encoding="utf-8").read()
    checked = {
        "vllm": (re.search(r"vLLM (\d+\.\d+\.\d+)", text) or [None, None])[1],
        "sglang": (re.search(r"SGLang (\d+\.\d+\.\d+)", text) or [None, None])[1],
    }
    want = {rt: {"tool": {}, "reasoning": {}} for rt in ("vllm", "sglang")}

    def names(cell):
        return [n for n in re.findall(r"`([^`]+)`", cell) if re.fullmatch(r"[a-z0-9][a-z0-9_.-]*", n)]

    for line in text.splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) != 5 or not line.startswith("|") or set(cells[0]) <= set("-"):
            continue
        family, _, vt, st, rs = cells
        for n in names(vt):
            want["vllm"]["tool"].setdefault(n, family)
        for n in names(st):
            want["sglang"]["tool"].setdefault(n, family)
        left, _, right = rs.rpartition(" / ") if " / " in rs else ("", "", "")
        for n in names(left):
            want["vllm"]["reasoning"].setdefault(n, family)
        for n in names(right):
            want["sglang"]["reasoning"].setdefault(n, family)
    return checked, want


def find_table():
    for p in (setting("PARSERS_MD", ""),
              os.path.join(HERE, "..", "..", "roofline-toolcall", "references", "parsers.md")):
        if p and os.path.isfile(p):
            return os.path.normpath(p)
    return None


def fetch(url, timeout):
    req = urllib.request.Request(url)
    key = os.environ.get("INFER_API_KEY")
    if key:
        req.add_header("Authorization", "Bearer " + key)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.status, r.read().decode("utf-8", "replace")


def main():
    load_env_file()
    url = setting("INFER_URL", "http://127.0.0.1:8000").rstrip("/")
    if url.endswith("/v1"):
        url = url[:-3]
    timeout = float(setting("CURL_TIMEOUT", "10"))
    problems, notes = [], []

    rt = setting("RUNTIME", "")
    if not rt:
        rt = next((r for r in ("vllm", "sglang") if package_dir(r)), "")
    pkg = package_dir(rt) if rt in REGISTRIES else None
    if not pkg:
        print("doctor: neither vllm nor sglang is importable by %s" % sys.executable, file=sys.stderr)
        print("doctor: activate the runtime's venv or set RUNTIME=vllm|sglang", file=sys.stderr)
        return 2
    ver = installed_version(rt)
    print("== runtime  %s %s (%s)" % (rt, ver or "version unknown", pkg))

    table = find_table()
    if not table:
        notes.append("parser table not found next to the toolbox; set PARSERS_MD=/path/to/parsers.md")
    else:
        checked, want = table_names(table)
        cv = checked.get(rt)
        if not cv:
            notes.append("version comparison skipped: the table header names no checked %s version" % rt)
        elif not ver:
            notes.append("version comparison skipped: installed %s version unknown" % rt)
        elif vtuple(ver) > vtuple(cv):
            notes.append("installed %s %s is newer than the table (checked with %s): new models may need parsers not listed" % (rt, ver, cv))
        elif vtuple(ver) < vtuple(cv):
            notes.append("installed %s %s is older than the table (checked with %s): some listed parsers may not exist yet" % (rt, ver, cv))
        print("== table    %s (checked with %s %s)" % (table, rt, cv or "unknown"))

        for kind in ("tool", "reasoning"):
            rel, have = registry_names(pkg, REGISTRIES[rt][kind])
            if not have:
                notes.append("%s parser registry not found in %s; names not checked" % (kind, rt))
                continue
            missing = sorted(n for n in want[rt][kind] if n not in have)
            extra = sorted(have - set(want[rt][kind]))
            print("== %-9s %d registered in %s, %d in the table" % (kind, len(have), rel, len(want[rt][kind])))
            for n in missing:
                problems.append("%s parser %s (%s) is in the table but not in installed %s" % (kind, n, want[rt][kind][n], rt))
            if extra:
                print("   not in the table: %s" % " ".join(extra))

    try:
        code, _ = fetch(url + "/health", timeout)
        up = code == 200
    except Exception:
        up = False
    if not up:
        notes.append("endpoint %s is down: metrics and smoke-toolcall skipped (task serve first)" % url)
    else:
        try:
            _, body = fetch(url + "/metrics", timeout)
            present = set(re.findall(r"^([a-zA-Z_:][a-zA-Z0-9_:]*?)(?:_bucket|_sum|_count)?(?:\{|\s)", body, re.M))
            for s in CORE_SERIES[rt]:
                if s not in present:
                    problems.append("metric %s missing from /metrics: task metrics will show gaps" % s)
            print("== metrics  %d series, core %d/%d" % (len(present), sum(s in present for s in CORE_SERIES[rt]), len(CORE_SERIES[rt])))
        except Exception as e:
            notes.append("/metrics unreadable: %s (SGLang needs --enable-metrics)" % e)
        if setting("DOCTOR_SMOKE", "1") != "0":
            print("== smoke-toolcall")
            rc = subprocess.call([sys.executable, "-I", os.path.join(HERE, "smoke_toolcall.py")])
            if rc != 0:
                problems.append("smoke-toolcall failed (exit %d): see the lines above" % rc)

    for n in notes:
        print("NOTE %s" % n)
    for p in problems:
        print("FAIL %s" % p)
    if problems:
        print("doctor: %d mismatch(es). Fix the launch flags, or report a table error: %s" % (len(problems), ISSUE_URL))
        print("doctor: paste this whole output into the issue; check it for internal hostnames and paths first")
        return 1
    print("doctor: OK, the tables match %s %s on this host" % (rt, ver or ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
