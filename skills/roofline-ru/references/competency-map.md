# Карта компетенций по roadmap.sh/inference-engineering

Источник: 136 узлов roadmap (снимок от 2026-10-07), перевод в `docs/roadmap-ru/`. Колонка "у нас" показывает, что делает инженер в этом продукте (on-prem, vLLM/SGLang, Taskfile).

## В роли

| Группа roadmap | Узлы | У нас | Skill / task |
|---|---|---|---|
| Latency Metrics | TTFT, ITL, TPS, latency vs throughput, p50/p95/p99, end-to-end | задать SLO, измерять p95 TTFT и TPOT, не среднее | perf, `task bench`, `task metrics` |
| Inference Phases | prefill (compute-bound), decode (memory-bound), online/offline/async | диагностировать узкое место по фазе | perf, incident |
| Application Context | AI-native apps, reasoning models | агенты (Claude Code) дают много вызовов и длинные промпты; reasoning удлиняет ответ | capacity, toolcall |
| Model Strategy | model selection, evaluation | выбрать наименьшую модель, которая проходит продуктовые evals и tool-calling smoke | capacity, perf |
| LLMs | transformer blocks, attention, KV cache, MoE | считать KV на токен, понимать MoE в батче (все эксперты активны) | perf, `task vram` |
| Bottleneck Analysis | ops:byte, arithmetic intensity, roofline | decode упирается в память: квантование и батч помогают, FLOPS нет | perf |
| Attention Optimization | FlashAttention, PagedAttention, варианты | включены в движках; проверить backend, не писать своё | runtime |
| GPU Architecture | compute, memory, NVLink, MIG, sizing | sizing: 1 GB на 1B параметров в FP8 плюс 50% на KV | capacity, `task gpu` |
| GPU Models | Hopper, Blackwell | FP8 на Hopper+, FP4 на Blackwell | perf |
| Model Formats | safetensors | только safetensors в air-gap, контрольные суммы | runtime, capacity |
| Inference Engines | vLLM, SGLang, TensorRT-LLM | vLLM и SGLang; TRT-LLM не используем | runtime |
| Benchmarking & Profiling | genai-bench, GenAI-Perf, Locust | свой фиксированный бенч `task bench`, одна переменная за раз | perf |
| Quantization | PTQ, QAT, ModelOpt, качество | FP8 первым, AWQ/GPTQ с проверкой tool-calling | perf |
| Speculative Decoding | draft-target, EAGLE, n-gram | n-gram для кода, EAGLE при низкой конкурентности | perf |
| Caching | prefix cache, KV storage, cache-aware routing, long context | стабильный системный промпт, hit rate в метриках, routing при нескольких репликах | perf, capacity |
| Model Parallelism | TP, PP, EP, multi-node | TP внутри узла по NVLink; multi-node вне продукта | runtime, capacity |
| Containerization | pinned deps, образы | pin версий vLLM/CUDA/драйвера, образ по digest | runtime, capacity |
| Autoscaling | continuous batching, cold starts, routing, LoRA-aware, queue | лимиты батча, очередь в метриках, прогрев перед выкаткой | perf, incident |
| Testing & Deployment | zero-downtime, cost, observability | canary на втором порту, gate: health, smoke, bench | capacity, incident |
| Security and Compliance | защита весов и данных | air-gap, нет телеметрии, доступ по токену | runtime |

## Вне роли (знать, не делать)

| Группа roadmap | Почему вне |
|---|---|
| Fine-Tuning, Distillation | roadmap относит к стратегии модели: инженер заказывает, когда маленькая модель не проходит evals |
| CUDA: custom kernels | движки выбирают ядра сами; своё ядро пишут при contributing в движок |
| Multi-Cloud, GPU procurement в облаке, geo-aware LB | on-prem, один контур |
| Disaggregation, NVIDIA Dynamo | нужны при десятках GPU и prefill-тяжёлом трафике на кластере |
| Image & Video, Speech, Embeddings, VLM | отдельные пайплайны; переведено в roadmap-ru для справки |
| Local & Edge (Ollama, llama.cpp, mobile) | продукт серверный |
