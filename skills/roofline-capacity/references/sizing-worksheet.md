# Sizing worksheet

Example: a team of 20 developers on Claude Code behind a proxy, model Qwen3-32B FP8, 2 x H100 80 GB with NVLink.

| Step | Calculation | Result |
|---|---|---|
| Weights | 32.8B x 1 byte (FP8) | 33 GB |
| KV per token | 2 x 64 x 8 x 128 x 1 byte (fp8 KV) | 128 KB |
| Memory available | 2 x 80 x 0.90 minus 33 minus 2 x 3 (overhead) | 105 GB |
| Tokens in KV | 105 GB / 128 KB | about 860k |
| In flight per request | prompt p95 40k plus response 1k | 41k |
| Concurrency at p95 | 860k / 41k | 21 requests |
| Concurrency at p50 (prompt 20k) | 860k / 21k | 41 requests |
| Load | 20 users x 10 calls/min / 60 = 3.3 RPS; average e2e 6 s | 20 concurrent |
| Verdict | one TP=2 replica holds with headroom at p50, at the limit at p95 | `max-num-seqs 32`, watch `waiting` |

Verification: `task vram MODEL=/models/Qwen3-32B-FP8 GPU_GB=80 TP=2 CTX=65536 KV_DTYPE=fp8 AVG_TOKENS=24000`, then `task bench BENCH_C=16 BENCH_IN=20000 BENCH_OUT=512`.

## When the estimate lies

- Prefix cache: tokens of a shared prefix are stored once; real concurrency is higher than computed when the prefix is stable
- Reasoning models: a response with thinking is 3 to 10 times longer; size by p95 of output tokens
- MoE: all weights stay in memory, the gain is only in per-request decode speed
- Chunked prefill: long prompts no longer block decode, but total compute is the same; TTFT for a cold 50k prompt on one replica is seconds
- Overhead: cudagraph, activations, NCCL buffers; with TP above 1, budget 3-4 GB per GPU
