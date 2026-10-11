---
name: roofline-toolbox
description: Operations toolbox for a local vLLM or SGLang server with an OpenAI-compatible API. Taskfile tasks and dependency-free scripts for gpu, health, models, metrics (queue, KV cache, prefix-cache hit rate, TTFT/TPOT p95), serve and stop by named profile, fixed SLO benchmark, tool-calling smoke test, VRAM budget from config.json, runtime flag lookup. Use when asked to check, start, stop, benchmark or probe a local LLM server, or when another roofline-* skill says to run a task.
license: MIT
compatibility: Requires python3 and curl; go-task (task) for the Taskfile, nvidia-smi for the gpu task
---

# Inference toolbox

Every task is idempotent, prints a short table and exits non-zero on failure. Run from the project directory, so `inference.env` and `.inference-state/` stay with the project.

```bash
task -t ${CLAUDE_SKILL_DIR}/Taskfile.yml health
task -t ${CLAUDE_SKILL_DIR}/Taskfile.yml serve INFER_PROFILE=qwen3-32b-fp8-vllm
```

Without go-task, call the scripts directly with the same environment variables: `${CLAUDE_SKILL_DIR}/scripts/health.sh`, `python3 -I ${CLAUDE_SKILL_DIR}/scripts/bench.py --n 16 --concurrency 4`.

## Tasks

| Task | What it does | Exit 0 means |
|---|---|---|
| `gpu` | memory used/free, utilization, temperature, compute processes per GPU | nvidia-smi answered |
| `health` | `/health`, `/v1/models`, one 4-token completion with latency | all three passed |
| `models` | served model ids, max context, owner | at least one model |
| `metrics` | running and waiting requests, KV cache usage, prefix-cache hit rate, preemptions, p50/p95/p99 of TTFT, TPOT and e2e from `/metrics`, plus hints | series parsed |
| `status` | `gpu` (failure tolerated) then `health` then `models` | health and models passed |
| `profiles` | names of launch profiles in `profiles/` | |
| `serve INFER_PROFILE=<name>` | start vLLM or SGLang from `profiles/<name>.env`, wait for `/health`, write pid and log to `.inference-state/` | healthy within `SERVE_TIMEOUT` (900 s) |
| `stop [INFER_PROFILE=<name>]` | SIGTERM the runtime's process group, SIGKILL after 30 s; no profile stops everything | always, even when nothing runs |
| `restart`, `logs LINES=200 FOLLOW=1` | stop then serve; tail the profile log | |
| `bench BENCH_N=32 BENCH_C=8 BENCH_IN=2048 BENCH_OUT=256` | N streaming requests at concurrency C with a fixed prompt, `temperature 0`, `ignore_eos`; p50/p95/p99 TTFT, TPOT, e2e; total tokens/s; `-- --json` adds a JSON line | p95 TTFT and TPOT within `SLO_TTFT_P95_MS` and `SLO_TPOT_P95_MS`, zero errors |
| `smoke-toolcall` | non-stream call, streamed deltas, negative prompt, tool-result round trip, parallel calls (informational); diagnoses parser and template problems | required checks passed |
| `vram MODEL=/models/x GPU_GB=80 TP=2 CTX=65536 KV_DTYPE=fp8` | weights from safetensors sizes, KV bytes per token (GQA and MLA aware), tokens in flight, concurrency, suggested `--max-model-len` and `--max-num-seqs` | weights fit |
| `flags Q=tool-call RUNTIME=vllm` | grep the installed runtime's `--help`, so flag names come from the installed version | match found |

## Settings

Priority, highest first: task variable (`task serve INFER_PROFILE=x`), environment variable, line in `inference.env` in the current directory (or `INFER_ENV_FILE`), default.

| Variable | Default | Meaning |
|---|---|---|
| `INFER_URL` | `http://127.0.0.1:8000` | base URL without `/v1` |
| `INFER_API_KEY` | empty | bearer token when the server was started with `--api-key` |
| `INFER_PROFILE` | empty | profile for serve, stop, logs |
| `INFER_STATE_DIR` | `./.inference-state` | pid files and logs |
| `PROFILES_DIR` | `profiles/` next to the Taskfile | where profiles live; point it at the project's own profiles |
| `SLO_TTFT_P95_MS`, `SLO_TPOT_P95_MS` | 2000, 60 | bench gate |
| `BENCH_N`, `BENCH_C`, `BENCH_IN`, `BENCH_OUT`, `BENCH_MODEL` | 32, 8, 2048, 256, first served model | bench shape |

## Profiles

One `profiles/<name>.env` per way to launch a runtime: `RUNTIME`, `MODEL`, `SERVED_NAME`, `PORT`, `TP`, `MAX_MODEL_LEN`, `GPU_MEM_UTIL`, `EXTRA_ARGS`, `CUDA_VISIBLE_DEVICES`, or a full `CMD` (for docker). `serve` accepts only files from `PROFILES_DIR`, so the agent never composes an arbitrary server command. Air-gap variables are set by `serve.sh`: `HF_HUB_OFFLINE=1`, `TRANSFORMERS_OFFLINE=1`, `VLLM_NO_USAGE_STATS=1`, `DO_NOT_TRACK=1`. Fields and examples: [profiles/README.md](profiles/README.md).

## Reading the output

- `health` FAIL on `/health` with code 000: nothing listens; `serve` or check the port
- `metrics` HINT lines name the bottleneck: queue with KV above 90% is KV-bound, preemptions mean KV exhaustion, prefix hit below 30% means an unstable prefix or round-robin across replicas
- `smoke-toolcall` FAIL with `<tool_call>` text in content: the parser is off or wrong for the model family
- `bench` SLO FAIL lists which percentile missed; rerun with lower `BENCH_C` to find the concurrency the server sustains

## Sources

- [vLLM: metrics design](https://docs.vllm.ai/en/latest/design/metrics/) and [SGLang: production metrics](https://docs.sglang.ai/references/production_metrics.html): series names parsed by `metrics`
- [vLLM: tool calling](https://docs.vllm.ai/en/latest/features/tool_calling/) and [SGLang: tool parser](https://docs.sglang.ai/advanced_features/tool_parser.html): contract checked by `smoke-toolcall`
- [Taskfile](https://taskfile.dev/): task runner syntax
- [roadmap.sh: Inference Engineering](https://roadmap.sh/inference-engineering): metric definitions (TTFT, ITL, TPS, percentiles)
