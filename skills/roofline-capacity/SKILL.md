---
name: roofline-capacity
description: "Design on-prem LLM serving for a given load and roll it out safely: GPU, VRAM and TP sizing for the model and context, concurrency against the SLO, replica count, model choice driven by evals, canary rollout and rollback plan, version pinning, moving weights into an air-gapped environment. Use when asked how many GPUs are needed, which model fits the hardware, how many concurrent Claude Code or Qwen Code users a server handles, how to roll out a new model or runtime version safely, or to estimate cost of dedicated inference."
license: MIT
---

# Capacity and rollout

Every `task` below runs as `task -t ${CLAUDE_SKILL_DIR}/../roofline-toolbox/Taskfile.yml <task>`, or include that Taskfile in the project one (`task infer:<task>`). `INFER_URL` and `INFER_PROFILE` come from the environment, from arguments (`task serve INFER_PROFILE=x`) or from `inference.env` in the current directory.

## Inputs

Without these the estimate is invalid; when a value is missing, write "unknown" and ask for a measurement.

| Parameter | Source | Typical for coding agents |
|---|---|---|
| Concurrent users | clients, proxy | 5-50 per team |
| Prompt length (p50, p95) | `task metrics` prompt tokens, proxy logs | 10k-60k, system prompt is stable |
| Response length | same place | 200-2000 tokens, more with thinking |
| Requests per user action | client | an agent makes 5-30 calls per task |
| SLO | agreed with the team | TTFT p95 2 s, TPOT p95 50 ms |
| Model and quality | evals, smoke-toolcall | the smallest model that passes evals |
| GPU | `task gpu` | type, count, NVLink between them |

## Sizing

1. Weights: bytes per parameter x parameters; FP8 is about 1 GB per 1B parameters (roadmap: Sizing & Procurement), plus at least 50% on top for KV
2. KV per token: 2 x layers x kv_heads x head_dim x bytes; `task vram` handles MoE and MLA
3. Tokens in KV = (VRAM x utilization x TP minus weights minus overhead) / KV per token
4. Concurrency = tokens in KV / average in-flight request length (prompt plus response); for agents the whole prompt sits in flight
5. Little's law: concurrent requests = RPS x average e2e; RPS = users x calls per minute / 60
6. Replicas = ceil(required concurrency / concurrency of one replica with 30% headroom)
7. Verify: `task bench BENCH_C=<concurrency> BENCH_IN=<p95 prompt>`; p95 must stay inside the SLO, otherwise step back

`task vram MODEL=/models/x GPU_GB=80 TP=2 CTX=65536 KV_DTYPE=fp8 AVG_TOKENS=24000` prints weights, KV per token, in-flight tokens and concurrency. Worksheet with a worked example: [references/sizing-worksheet.md](references/sizing-worksheet.md).

## TP versus replicas

| Need | Choice |
|---|---|
| Model does not fit one GPU | TP equal to the GPU count in the NVLink group (2, 4, 8); never TP across nodes |
| Lower TPOT with the same model | TP (several GPUs read the weights in parallel) |
| More users while the SLO holds | replicas plus session-affinity routing for the prefix cache |
| Different models for different tasks | separate profiles on separate GPUs, `CUDA_VISIBLE_DEVICES` |
| One GPU shared by several small models | MIG, or two replicas with utilization 0.45 each |

## Rollout

1. Profile of the new version next to the old one (different port), versions pinned: engine, torch, CUDA, driver, image digest
2. Gate on the new port: `task health`, `task smoke-toolcall`, `task bench` no worse than baseline at p95
3. Canary through the proxy: 5-10% of traffic for 30-60 minutes, watching `task metrics` on both replicas and client errors
4. Switch the remaining traffic; the old profile stays up until end of day
5. Rollback: traffic back to the old port, `task stop` on the new one. No blue-green on GPUs: it needs double the memory (roadmap: Zero-Downtime Deployment), canary is cheaper

Checklist with fields: [references/rollout-checklist.md](references/rollout-checklist.md).

## Air-gap

- Weights: safetensors only, sha256 per file on both sides, `config.json`, `tokenizer*.json` and `generation_config.json` shipped together
- Images and wheels: by digest, mirror inside the perimeter, `pip install` in production is forbidden
- Telemetry: `VLLM_NO_USAGE_STATS=1`, `HF_HUB_OFFLINE=1`; endpoint locked down by token and network
- New model: smoke test on a rig outside production first, then move the profile

## Cost

Dedicated versus API (roadmap: Cost Estimation): GPU-hour x GPU count x hours against price per token x real traffic over the same window, plus engineer time. For agents with long prompts and a prefix cache, dedicated wins earlier: the API bills every input token, your own server pays only for the uncached ones.

## Sources

- roadmap.sh: [Sizing and Procurement](https://roadmap.sh/inference-engineering/sizing-procurement@da0HGfSDr6_DV4ZJcrcIB), [Cost Estimation](https://roadmap.sh/inference-engineering/cost-estimation@Gof4kW2LbkNCtH68c7Xvq), [Zero-Downtime Deployment](https://roadmap.sh/inference-engineering/zero-downtime-deplo@le4sPQ0h9l-vlmCB4G8ZY), [Dependency Management](https://roadmap.sh/inference-engineering/dependency-management@wEaM8VyAo6MFsc3RXQ7Ar), [Model Parallelism](https://roadmap.sh/inference-engineering/model-parallelism@CiXsdHHL0e2DN4ICI5jeX)
- [vLLM: parallelism and scaling](https://docs.vllm.ai/en/latest/serving/parallelism_scaling/)
- [Little's law](https://en.wikipedia.org/wiki/Little%27s_law): ties RPS, latency and concurrent requests together
- Andriy Burkov, "The Hundred-Page Language Models Book" (page numbers refer to the Russian edition, BHV, 2026): quadratic cost of attention, pp. 149-159; MoE, p. 199
