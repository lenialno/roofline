#!/usr/bin/env python3
"""Key Prometheus series from a vLLM or SGLang /metrics endpoint. Stdlib only.

Prints running/waiting requests, KV cache usage, prefix-cache hit rate, preemptions,
and p50/p95 of TTFT, TPOT and e2e latency reconstructed from histogram buckets.
Histograms are cumulative since server start, not a sliding window.
Exit codes: 0 ok, 2 endpoint unreachable, 3 no known series (metrics disabled?).
"""
import os
import re
import sys
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


LINE = re.compile(r'^([a-zA-Z_:][a-zA-Z0-9_:]*)(\{[^}]*\})?\s+([-+0-9.eE]+|NaN|\+Inf)')


def fetch(url):
    req = urllib.request.Request(url)
    key = os.environ.get("INFER_API_KEY")
    if key:
        req.add_header("Authorization", "Bearer " + key)
    with urllib.request.urlopen(req, timeout=10) as r:
        return r.read().decode("utf-8", "replace")


def parse(text):
    """-> {name: [(labels_dict, value)]}"""
    out = {}
    for line in text.splitlines():
        if not line or line[0] == "#":
            continue
        m = LINE.match(line)
        if not m:
            continue
        name, labels, val = m.group(1), m.group(2) or "", m.group(3)
        ld = dict(re.findall(r'(\w+)="([^"]*)"', labels))
        try:
            v = float(val)
        except ValueError:
            continue
        out.setdefault(name, []).append((ld, v))
    return out


def gauge_sum(series, *names):
    for n in names:
        if n in series:
            return sum(v for _, v in series[n]), n
    return None, None


def hist_quantiles(series, base, qs=(0.5, 0.95, 0.99)):
    buckets = series.get(base + "_bucket")
    if not buckets:
        return None
    acc = {}
    for ld, v in buckets:
        le = ld.get("le")
        if le is None:
            continue
        acc[le] = acc.get(le, 0.0) + v
    items = sorted(((float("inf") if k == "+Inf" else float(k)), v) for k, v in acc.items())
    total = items[-1][1] if items else 0
    if total <= 0:
        return {"count": 0}
    res = {"count": int(total)}
    for q in qs:
        target = q * total
        prev_le, prev_c = 0.0, 0.0
        for le, c in items:
            if c >= target:
                if le == float("inf"):
                    res[q] = prev_le
                    break
                if c == prev_c:
                    res[q] = le
                    break
                res[q] = prev_le + (le - prev_le) * (target - prev_c) / (c - prev_c)
                break
            prev_le, prev_c = le, c
    return res


def fmt_ms(x):
    return "-" if x is None else "%.0f ms" % (x * 1000)


def main():
    load_env_file()
    if len(sys.argv) > 1 and sys.argv[1]:
        url = sys.argv[1]
    else:
        base = setting("INFER_URL", "http://127.0.0.1:8000").rstrip("/")
        url = (base[:-3] if base.endswith("/v1") else base) + "/metrics"
    try:
        text = fetch(url)
    except Exception as e:
        print("metrics: %s unreachable: %s" % (url, e), file=sys.stderr)
        return 2
    s = parse(text)
    if any(k.startswith("vllm:") for k in s):
        rt = "vllm"
    elif any(k.startswith("sglang:") for k in s):
        rt = "sglang"
    else:
        print("metrics: no vllm:/sglang: series at %s (SGLang needs --enable-metrics)" % url, file=sys.stderr)
        return 3

    rows = []
    if rt == "vllm":
        running, _ = gauge_sum(s, "vllm:num_requests_running")
        waiting, _ = gauge_sum(s, "vllm:num_requests_waiting")
        kv, kvname = gauge_sum(s, "vllm:kv_cache_usage_perc", "vllm:gpu_cache_usage_perc")
        hits, _ = gauge_sum(s, "vllm:prefix_cache_hits_total")
        queries, _ = gauge_sum(s, "vllm:prefix_cache_queries_total")
        hit_rate = None
        if queries:
            hit_rate = hits / queries
        else:
            hit_rate, _ = gauge_sum(s, "vllm:gpu_prefix_cache_hit_rate")
        preempt, _ = gauge_sum(s, "vllm:num_preemptions_total")
        ptok, _ = gauge_sum(s, "vllm:prompt_tokens_total")
        gtok, _ = gauge_sum(s, "vllm:generation_tokens_total")
        ttft = hist_quantiles(s, "vllm:time_to_first_token_seconds")
        tpot = hist_quantiles(s, "vllm:time_per_output_token_seconds")
        e2e = hist_quantiles(s, "vllm:e2e_request_latency_seconds")
        queue = hist_quantiles(s, "vllm:request_queue_time_seconds")
    else:
        running, _ = gauge_sum(s, "sglang:num_running_reqs")
        waiting, _ = gauge_sum(s, "sglang:num_queue_reqs")
        kv, kvname = gauge_sum(s, "sglang:token_usage")
        hit_rate, _ = gauge_sum(s, "sglang:cache_hit_rate")
        preempt = None
        ptok, _ = gauge_sum(s, "sglang:prompt_tokens_total")
        gtok, _ = gauge_sum(s, "sglang:generation_tokens_total")
        ttft = hist_quantiles(s, "sglang:time_to_first_token_seconds")
        tpot = hist_quantiles(s, "sglang:inter_token_latency_seconds") or hist_quantiles(s, "sglang:time_per_output_token_seconds")
        e2e = hist_quantiles(s, "sglang:e2e_request_latency_seconds")
        queue = None

    def num(x, f="%.0f"):
        return "-" if x is None else f % x

    print("runtime            %s   (%s)" % (rt, url))
    print("requests running   %s" % num(running))
    print("requests waiting   %s" % num(waiting))
    print("kv cache usage     %s%%" % num(None if kv is None else kv * 100, "%.1f"))
    print("prefix cache hit   %s%%" % num(None if hit_rate is None else hit_rate * 100, "%.1f"))
    if preempt is not None:
        print("preemptions total  %s" % num(preempt))
    print("tokens prompt/gen  %s / %s" % (num(ptok), num(gtok)))
    for label, h in (("ttft", ttft), ("tpot", tpot), ("e2e ", e2e), ("queue", queue)):
        if h is None:
            continue
        if h.get("count", 0) == 0:
            print("%-5s              no samples yet" % label)
            continue
        print("%-5s p50/p95/p99   %s / %s / %s   (n=%d)" % (label, fmt_ms(h.get(0.5)), fmt_ms(h.get(0.95)), fmt_ms(h.get(0.99)), h["count"]))

    hints = []
    if waiting and waiting > 0 and kv is not None and kv > 0.9:
        hints.append("queue with KV cache >90%: KV-bound; lower max-model-len, enable fp8 KV, add TP or a replica")
    if waiting and waiting > 0 and (kv is None or kv < 0.7):
        hints.append("queue while KV cache <70%: max-num-seqs or max-num-batched-tokens caps concurrency, or decode is compute-bound")
    if preempt:
        hints.append("preemptions >0: KV cache exhausted under load; requests were evicted and recomputed")
    if hit_rate is not None and hit_rate < 0.3 and (queries if rt == "vllm" else 1):
        hints.append("prefix cache hit <30%: system prompt not stable, prefix caching off, or round-robin across replicas")
    for h in hints:
        print("HINT " + h)
    return 0


if __name__ == "__main__":
    sys.exit(main())
