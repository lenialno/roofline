---
name: roofline-perf
description: "Speed up and measure LLM inference on vLLM/SGLang: VRAM and KV cache budget, continuous batching, prefix/radix cache, quantization (FP8, AWQ, GPTQ, fp8 KV) and what it costs tool calling, speculative decoding, TTFT/TPOT/p95, benchmark method (task bench, task vram, task metrics). Use when asked why the server is slow, how to raise throughput or concurrency, which quantization to pick, how to size the KV cache, tune max-num-seqs, max-num-batched-tokens or max-model-len, or how to run and read a benchmark."
license: MIT
---

# Performance

Every `task` below runs as `task -t ${CLAUDE_SKILL_DIR}/../roofline-toolbox/Taskfile.yml <task>` or through an include of that Taskfile in the project one (`task infer:<task>`). `INFER_URL` and `INFER_PROFILE` come from the environment, from arguments (`task serve INFER_PROFILE=x`) or from `inference.env` in the current directory.

## Metrics and targets

| Metric | What it measures | What sets it | Starting target for coding agents |
|---|---|---|---|
| TTFT | time to first token | prefill (compute-bound) plus queue | p95 under 2 s on a 20k-token prompt with a warm prefix cache |
| TPOT (ITL) | time between tokens | decode (memory-bound): every token reads all the weights | p95 under 50 ms, that is 20 tokens/s or more per stream |
| TPS per user | stream speed | inverse of TPOT | 20 to 40 tokens/s |
| TPS total | throughput | batch size, memory bandwidth | higher with a larger batch, paid for in TPOT |
| p50/p95/p99 | distribution | queue and long prompts | decide on p95, not on the mean |
| e2e | what the client sees | plus network, proxy, queue | large e2e on a fast server points at the proxy |

Formulas and definitions: [references/metrics.md](references/metrics.md). Current numbers: `task metrics` (histograms since server start); under load: `task bench`.

## One-minute diagnosis

| Picture | Bottleneck | Lever |
|---|---|---|
| TTFT high, TPOT normal | prefill or queue | prefix cache hit, chunked prefill, lower `max-num-seqs`, a second replica |
| TPOT high, TTFT normal | decode: batch too large or TP too small | lower `max-num-seqs`, fp8 KV and FP8 weights (fewer bytes per token), TP over NVLink |
| Both grow, `waiting` above 0 | queue: KV or the seqs limit | `task vram`, lower `max-model-len`, fp8 KV, a replica |
| `preemptions` growing | KV cache runs out under load | same levers; a preemption is a recompute, it doubles prefill |
| prefix cache hit below 50% for agents | unstable prefix or round-robin across replicas | stable system prompt, session-based routing |

Prefill is compute-bound, decode is memory-bound (roadmap, LLM Bottlenecks): weight quantization speeds up decode but barely touches prefill; prefix cache removes prefill but does not change decode.

## Memory

KV per token = 2 x layers x kv_heads x head_dim x bytes. Qwen3-32B: 256 KB per token in bf16, 128 KB in fp8. Weights plus KV plus 2-4 GB of overhead per GPU. Budget and concurrency: `task vram MODEL=... GPU_GB=.. TP=.. CTX=.. KV_DTYPE=fp8`.

Levers in order: `max-model-len` sized to real prompts, fp8 KV, FP8 weights, TP, lower `max-num-seqs`. MoE: nearly all experts are active across a batch, so count weight memory in full.

## Batching and cache

- Continuous batching is always on; `max-num-seqs` caps concurrent requests, `max-num-batched-tokens` caps tokens per step (prefill is split by chunked prefill and does not block decode)
- Larger batch, higher total TPS and higher TPOT; find the threshold with a bench at C = 1, 4, 8, 16, 32
- Prefix cache: block-based in vLLM, radix in SGLang; pays off on long system prompts and multi-turn agents; hit rate in `task metrics`
- Several replicas: route by prefix or session, otherwise the hit rate is divided by the number of replicas

## Quantization

| Option | Memory | Decode speed | Tool calling risk | When |
|---|---|---|---|---|
| bf16 | 2 bytes/param | baseline | none | reference for comparison |
| FP8 (W8A8, Hopper and newer) | 1 byte | noticeably higher | minimal | first choice in production |
| fp8 KV cache | KV halved | higher on long context | small | together with FP8 weights |
| AWQ / GPTQ 4-bit | 0.5 byte | higher at small batch, lower at large batch | noticeable: breaks argument JSON | only if the model does not fit otherwise |
| FP4 / NVFP4 (Blackwell) | 0.5 byte | high | verify | Blackwell, models with an official FP4 release |

Acceptance protocol (roadmap, Measuring Quality Impact): perplexity on your own text before and after (a rise above 1-2% is a signal), `task smoke-toolcall`, your own agent task set, then `task bench`. A quantized model that fails smoke does not go to production. Details: [references/quantization.md](references/quantization.md).

## Speculative decoding

Uses the idle compute of memory-bound decode: several draft tokens are verified in a single pass. The gain drops as batch size and temperature grow (roadmap, Speculative Decoding), so enable it last and measure at real concurrency.

- n-gram: no second model, good for code and text edits (output repeats input); vLLM `--speculative-config '{"method":"ngram",...}'`
- EAGLE3: a draft head trained for the specific model; gain at C up to 8
- draft-target: a separate small model of the same family; the most expensive in memory

## Bench

`task bench BENCH_N=32 BENCH_C=8 BENCH_IN=2048 BENCH_OUT=256`: fixed prompt, `temperature 0`, `ignore_eos`, p50/p95/p99 TTFT, TPOT, e2e, total tok/s, verdict against `SLO_TTFT_P95_MS` and `SLO_TPOT_P95_MS`. Rules: baseline before any change, one variable per run, lengths matching real clients, warm-up before measuring, results in the log. Method and log entry template: [references/bench-protocol.md](references/bench-protocol.md).

## Sources

- [vLLM: optimization and tuning](https://docs.vllm.ai/en/latest/configuration/optimization/), [quantization](https://docs.vllm.ai/en/latest/features/quantization/), [speculative decoding](https://docs.vllm.ai/en/latest/features/spec_decode/), [automatic prefix caching](https://docs.vllm.ai/en/latest/features/automatic_prefix_caching/), [metrics design](https://docs.vllm.ai/en/latest/design/metrics/)
- [SGLang: hyperparameter tuning](https://docs.sglang.ai/advanced_features/hyperparameter_tuning.html), [speculative decoding](https://docs.sglang.ai/advanced_features/speculative_decoding.html), [quantization](https://docs.sglang.ai/advanced_features/quantization.html), [production metrics](https://docs.sglang.ai/references/production_metrics.html), [bench_serving](https://docs.sglang.ai/developer_guide/bench_serving.html), [genai-bench](https://github.com/sgl-project/genai-bench)
- roadmap.sh: [Time to First Token](https://roadmap.sh/inference-engineering/time-to-first-token@xCgNhwbS_ELxEyRHD1enO), [Bottleneck Analysis](https://roadmap.sh/inference-engineering/bottleneck-analysis@Gtd4g4MtB9zFfahRpbE2K), [Quantization](https://roadmap.sh/inference-engineering/quantization@DaSqcLHfnJ4_n9utVVTSk), [Speculative Decoding](https://roadmap.sh/inference-engineering/speculative-decoding@gMWgd10cxcQG_RG2oSAEH), [Caching](https://roadmap.sh/inference-engineering/caching@PzEj5yq1lDQ324RWYpDdQ), [Performance Benchmarking](https://roadmap.sh/inference-engineering/performance-benchmarking@XXfjlqd0CYHwBR5-Kdmmi)
- Andriy Burkov, "The Hundred-Page Language Models Book" (page numbers refer to the Russian edition, BHV, 2026): perplexity, pp. 85-89; KV cache, pp. 140-141; sampling and temperature, pp. 174-179
