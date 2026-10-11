# Competency map by roadmap.sh/inference-engineering

Source: 136 roadmap nodes (snapshot of 2026-10-07), translated in `docs/roadmap-ru/`. The "Here" column shows what the engineer does in this product (on-prem, vLLM/SGLang, Taskfile).

## In scope

| Roadmap group | Nodes | Here | Skill / task |
|---|---|---|---|
| Latency Metrics | TTFT, ITL, TPS, latency vs throughput, p50/p95/p99, end-to-end | set SLOs, measure p95 TTFT and TPOT, not the mean | perf, `task bench`, `task metrics` |
| Inference Phases | prefill (compute-bound), decode (memory-bound), online/offline/async | diagnose the bottleneck by phase | perf, incident |
| Application Context | AI-native apps, reasoning models | agents (Claude Code) produce many calls and long prompts; reasoning makes answers longer | capacity, toolcall |
| Model Strategy | model selection, evaluation | pick the smallest model that passes product evals and the tool-calling smoke test | capacity, perf |
| LLMs | transformer blocks, attention, KV cache, MoE | compute KV per token, understand MoE in a batch (all experts active) | perf, `task vram` |
| Bottleneck Analysis | ops:byte, arithmetic intensity, roofline | decode is memory-bound: quantization and batching help, FLOPS do not | perf |
| Attention Optimization | FlashAttention, PagedAttention, variants | built into the engines; check the backend, do not write your own | runtime |
| GPU Architecture | compute, memory, NVLink, MIG, sizing | sizing: 1 GB per 1B parameters in FP8 plus 50% for KV | capacity, `task gpu` |
| GPU Models | Hopper, Blackwell | FP8 on Hopper+, FP4 on Blackwell | perf |
| Model Formats | safetensors | safetensors only in air-gap, checksums | runtime, capacity |
| Inference Engines | vLLM, SGLang, TensorRT-LLM | vLLM and SGLang; TRT-LLM is not used | runtime |
| Benchmarking & Profiling | genai-bench, GenAI-Perf, Locust | our own fixed bench `task bench`, one variable at a time | perf |
| Quantization | PTQ, QAT, ModelOpt, quality | FP8 first, AWQ/GPTQ with a tool-calling check | perf |
| Speculative Decoding | draft-target, EAGLE, n-gram | n-gram for code, EAGLE at low concurrency | perf |
| Caching | prefix cache, KV storage, cache-aware routing, long context | stable system prompt, hit rate in metrics, routing when there are several replicas | perf, capacity |
| Model Parallelism | TP, PP, EP, multi-node | TP within a node over NVLink; multi-node is outside the product | runtime, capacity |
| Containerization | pinned deps, images | pin vLLM/CUDA/driver versions, image by digest | runtime, capacity |
| Autoscaling | continuous batching, cold starts, routing, LoRA-aware, queue | batch limits, queue in metrics, warm-up before rollout | perf, incident |
| Testing & Deployment | zero-downtime, cost, observability | canary on a second port, gate: health, smoke, bench | capacity, incident |
| Security and Compliance | protecting weights and data | air-gap, no telemetry, token-based access | runtime |

## Out of scope (know it, do not do it)

| Roadmap group | Why out of scope |
|---|---|
| Fine-Tuning, Distillation | the roadmap files them under model strategy: the engineer orders them when a small model fails evals |
| CUDA: custom kernels | the engines pick kernels themselves; a kernel of your own is Rust through cudarc (CUDA C compiled by NVRTC at runtime), CubeCL or Rust-CUDA, while production kernels stay CUDA C++ behind FFI |
| Multi-Cloud, GPU procurement in the cloud, geo-aware LB | on-prem, a single perimeter |
| Disaggregation, NVIDIA Dynamo | needed with dozens of GPUs and prefill-heavy traffic on a cluster |
| Image & Video, Speech, Embeddings, VLM | separate pipelines; translated in roadmap-ru for reference |
| Local & Edge (Ollama, llama.cpp, mobile) | the product is server-side |
