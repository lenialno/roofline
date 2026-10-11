# Inference metrics: definitions and formulas

Based on roadmap.sh (Latency Metrics, Inference Phases) and the `/metrics` exposition of vLLM and SGLang.

| Metric | Formula | Source in `/metrics` |
|---|---|---|
| TTFT | t(first token) minus t(request) | `vllm:time_to_first_token_seconds`, `sglang:time_to_first_token_seconds` |
| TPOT, also ITL | (t(last) minus t(first)) / (N_out minus 1) | `vllm:time_per_output_token_seconds`, `sglang:inter_token_latency_seconds` |
| TPS per stream | 1 / TPOT | computed |
| TPS total | sum of output tokens / window length | `*_generation_tokens_total` as a delta over the window |
| e2e | t(end) minus t(request) | `*:e2e_request_latency_seconds` |
| Queue time | wait before scheduling | `vllm:request_queue_time_seconds` |
| Requests | running and queued | `vllm:num_requests_running`, `vllm:num_requests_waiting`; `sglang:num_running_reqs`, `sglang:num_queue_reqs` |
| KV usage | share of occupied KV blocks | `vllm:kv_cache_usage_perc`, `sglang:token_usage` |
| Prefix cache hit | hits / queries | `vllm:prefix_cache_hits_total` / `vllm:prefix_cache_queries_total`; `sglang:cache_hit_rate` |
| Preemptions | evictions caused by KV shortage | `vllm:num_preemptions_total` |

Prometheus histograms are cumulative since start: `task metrics` computes p50/p95 from the buckets over the whole uptime. For a window you need Prometheus with `histogram_quantile(0.95, rate(..._bucket[5m]))`.

## How they relate

- TTFT = queue plus prefill. Prefill is compute-bound: time grows with the number of new (uncached) prompt tokens
- TPOT is set by reading the weights on every step: weight bytes (after quantization) divided by memory bandwidth, plus reading the KV of every request in the batch
- A larger batch shares the weight read across requests (total TPS grows), but each request waits for the whole step (TPOT grows)
- Percentiles: the distribution is right-skewed by long prompts; a p99 in seconds with a good median means one user in a hundred is waiting
- GPU ops:byte versus the arithmetic intensity of the operation: decode at small batch is far below the threshold, so only fewer bytes (quantization) or a larger batch helps

## Starting SLOs for coding agents

| Scenario | TTFT p95 | TPOT p95 | Comment |
|---|---|---|---|
| Claude Code, Qwen Code, warm cache | 2 s | 50 ms | prompt 20-60k, most tokens from the prefix cache |
| cold 50k prompt | 10 s | 50 ms | pure prefill; reduce with chunked prefill and more compute |
| autocomplete | 300 ms | 30 ms | short prompts, n-gram speculation |
| batch processing | not relevant | not relevant | only total TPS and cost |

These are starting numbers; confirm them with `task bench` on your own model and GPU.
