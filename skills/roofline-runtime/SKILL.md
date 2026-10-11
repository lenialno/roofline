---
name: roofline-runtime
description: Bring up vLLM or SGLang on-prem and keep it healthy: engine choice, flag order, launch profiles, air-gap, docker, make serve/stop/logs/flags. Use when asked to start, launch, configure, restart or stop a vLLM or SGLang server, choose between vLLM and SGLang, write a launch profile, set tensor parallel, max-model-len, gpu-memory-utilization, or when the server fails to start (OOM at load, port busy, unsupported model, missing tokenizer).
license: MIT
---

# Runtime: vLLM and SGLang

Every `task` below means `task -t ${CLAUDE_SKILL_DIR}/../roofline-toolbox/Taskfile.yml <task>`, or include that Taskfile in the project one (`task infer:<task>`). `INFER_URL` and `INFER_PROFILE` come from the environment, from arguments (`task serve INFER_PROFILE=x`) or from `inference.env` in the current directory.

## Choosing the engine

| Criterion | vLLM | SGLang |
|---|---|---|
| Architecture coverage, day-0 support for new models | wider, faster | narrower, but MoE (DeepSeek, Qwen3-MoE) is often faster |
| Prefix cache | block-level, on by default (V1) | RadixAttention, on by default |
| Tool-call and reasoning parsers | `--enable-auto-tool-choice --tool-call-parser`, `--reasoning-parser` | `--tool-call-parser`, `--reasoning-parser` |
| Metrics | `/metrics` always on | `/metrics` only with `--enable-metrics` |
| When to pick it | default for dense models and fresh releases | MoE under high concurrency, radix cache for multi-turn agents |

TensorRT-LLM gets the most out of NVIDIA, but model support is narrow and engine builds are expensive: not used in this product. Comparing the two engines on one model is done only through `task bench` with identical parameters.

## Launch procedure

1. `task gpu`: free memory on the target GPUs; no foreign processes
2. `task vram MODEL=/models/<x> GPU_GB=80 TP=<n> CTX=<len>`: weights fit, the KV budget covers the required concurrency
3. Profile `profiles/<name>.env`: fields in [profiles/README.md](../roofline-toolbox/profiles/README.md); check flags against the installed version: `task flags Q=max-model-len`
4. `task serve INFER_PROFILE=<name>`: waits for `/health` up to `SERVE_TIMEOUT` (900 s), writes pid and log to `.inference-state/`
5. `task health`, then `task smoke-toolcall`, then `task bench`
6. Profile journal entry: engine version, driver, CUDA, image digest, bench result

Running `task serve` again for the same profile restarts nothing. A different profile will not start on the same port.

## Flag order

Set flags in this order, each one only after the previous one is verified:

1. Model and name: path to the weights, `--served-model-name`; clients address the model by name, not by path
2. Parallelism: `--tensor-parallel-size` (vLLM) / `--tp` (SGLang), matching the GPU count in the NVLink group
3. Context: `--max-model-len` / `--context-length`; do not set the model maximum out of habit, take the value from `task vram`
4. Memory: `--gpu-memory-utilization` / `--mem-fraction-static`, 0.85-0.92; above 0.95 you hit OOM in prefill
5. Parsers: tool-call and reasoning per model family, see skill `roofline-toolcall`
6. Quantization and KV: `--quantization`, `--kv-cache-dtype fp8`; only after measuring quality (skill `roofline-perf`)
7. Batching: `--max-num-seqs`, `--max-num-batched-tokens` / `--max-running-requests`, `--chunked-prefill-size`
8. Speculation: last, after a bench without it

Flag mapping between the engines: [references/flags-map.md](references/flags-map.md).

## Air-gap

- `serve.sh` sets the variables: `HF_HUB_OFFLINE=1`, `TRANSFORMERS_OFFLINE=1`, `VLLM_NO_USAGE_STATS=1`, `DO_NOT_TRACK=1`
- Weights are safetensors only, with `config.json`, `tokenizer.json`, `tokenizer_config.json` (holds the chat template) and `generation_config.json`; sha256 per file when transferring
- Versions pinned: engine, torch, CUDA toolkit, driver; docker image by digest, not by the `latest` tag
- A new model often needs a pre-release engine: keep two profiles, do not delete the old one until the gate passes

## Common startup failures

| Log symptom | Cause | Action |
|---|---|---|
| `CUDA out of memory` while loading weights | weights do not fit at the current TP | `task vram`, raise TP or take the FP8/AWQ build |
| `The model's max seq len ... is larger than the maximum number of tokens that can be stored in KV cache` | no KV left after the weights, not even for one request | lower `--max-model-len`, raise utilization, `--kv-cache-dtype fp8` |
| `Address already in use` | an old process or another profile on the port | `task stop`, `task gpu` for foreign processes |
| `does not appear to have a file named config.json` / tokenizer | incomplete weight transfer | verify sha256 and the directory contents |
| `Model architectures [...] are not supported` | engine older than the model | profile with the newer engine version, keep the old one |
| `torch.cuda ... no kernel image` / `CUDA driver version is insufficient` | driver, CUDA and torch wheel mismatch | restore the pinned versions from the journal |
| healthy, but `task smoke-toolcall` FAIL | parser or chat template | skill `roofline-toolcall` |
| healthy, TTFT in seconds on a short prompt | cudagraph and kernel warmup did not complete, or `--enforce-eager` | allow 1-2 minutes of warmup, drop eager, rerun bench |

If the server is up but misbehaving: `task logs INFER_PROFILE=<name>`, then follow skill `roofline-incident`.

## Sources

- [vLLM: vllm serve](https://docs.vllm.ai/en/latest/cli/serve/), [vLLM: parallelism and scaling](https://docs.vllm.ai/en/latest/serving/parallelism_scaling/), [vLLM: troubleshooting](https://docs.vllm.ai/en/latest/usage/troubleshooting/)
- [SGLang: server arguments](https://docs.sglang.ai/advanced_features/server_arguments.html)
- roadmap.sh: [Inference Engines](https://roadmap.sh/inference-engineering/inference-engines@01j1KkEB-nIXxP-rENcJ3), [vLLM](https://roadmap.sh/inference-engineering/vllm@wcAtbab81IJdpFh6L-heP), [SGLang](https://roadmap.sh/inference-engineering/sglang@YtlAf6qloKMmaSr9Bkkl_), [Dependency Management](https://roadmap.sh/inference-engineering/dependency-management@wEaM8VyAo6MFsc3RXQ7Ar), [safetensors](https://roadmap.sh/inference-engineering/safetensors@jkbrf0_JDljWmVq_o9XE-)
