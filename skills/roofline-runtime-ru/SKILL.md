---
name: roofline-runtime-ru
description: "Поднять vLLM или SGLang on-prem и держать его в порядке: выбор движка, порядок флагов, профили запуска, air-gap, docker, task serve/stop/logs/flags. Use when asked to start, launch, configure, restart or stop a vLLM or SGLang server, choose between vLLM and SGLang, write a launch profile, set tensor parallel, max-model-len, gpu-memory-utilization, or when the server fails to start (OOM at load, port busy, unsupported model, missing tokenizer). Russian-language version; the English skill has the same name without -ru."
license: MIT
---

# Runtime: vLLM и SGLang

Все `task` ниже: `task -t ${CLAUDE_SKILL_DIR}/../roofline-toolbox/Taskfile.yml <задача>` или include этого Taskfile в проектном (`task infer:<задача>`). Переменные `INFER_URL`, `INFER_PROFILE` берутся из окружения, из аргументов (`task serve INFER_PROFILE=x`) или из `inference.env` в текущем каталоге.

## Выбор движка

| Критерий | vLLM | SGLang |
|---|---|---|
| Поддержка архитектур, day-0 новые модели | шире, быстрее | уже, но MoE (DeepSeek, Qwen3-MoE) часто быстрее |
| Prefix cache | блочный, включён по умолчанию (V1) | RadixAttention, включён по умолчанию |
| Tool-call и reasoning parsers | `--enable-auto-tool-choice --tool-call-parser`, `--reasoning-parser` | `--tool-call-parser`, `--reasoning-parser` |
| Метрики | `/metrics` всегда | `/metrics` только с `--enable-metrics` |
| Когда брать | дефолт для dense-моделей и новых релизов | MoE под высокой конкурентностью, radix cache на многоходовых агентах |

TensorRT-LLM даёт максимум на NVIDIA, но узкая поддержка моделей и дорогая сборка движков: в этом продукте не используем. Выбирать оба на одной модели можно только по `task bench` с одинаковыми параметрами.

## Процедура запуска

1. `task gpu`: свободная память на нужных GPU; чужих процессов нет
2. `task vram MODEL=/models/<x> GPU_GB=80 TP=<n> CTX=<len>`: веса влезают, KV-бюджет даёт нужную конкурентность
3. Профиль `profiles/<name>.env`: поля в [profiles/README.md](../roofline-toolbox/profiles/README.md); флаги проверить на установленной версии: `task flags Q=max-model-len`
4. `task serve INFER_PROFILE=<name>`: ждёт `/health` до `SERVE_TIMEOUT` (900 с), пишет pid и лог в `.inference-state/`
5. `task health`, затем `task smoke-toolcall`, затем `task bench`
6. Запись в журнал профилей: версия движка, драйвер, CUDA, digest образа, результат bench

Повторный `task serve` того же профиля ничего не перезапускает. Другой профиль на тот же порт не стартует.

## Порядок флагов

Задавать в этом порядке, каждый следующий только после проверки предыдущего:

1. Модель и имя: путь к весам, `--served-model-name`; клиенты ходят по имени, не по пути
2. Параллелизм: `--tensor-parallel-size` (vLLM) / `--tp` (SGLang) по числу GPU в NVLink-группе
3. Контекст: `--max-model-len` / `--context-length`; не ставить максимум модели по привычке, брать из `task vram`
4. Память: `--gpu-memory-utilization` / `--mem-fraction-static`, 0.85-0.92; выше 0.95 ловит OOM в prefill
5. Парсеры: tool-call и reasoning по семейству модели, см. skill `roofline-toolcall-ru`
6. Квантование и KV: `--quantization`, `--kv-cache-dtype fp8`; только после измерения качества (skill `roofline-perf-ru`)
7. Батч: `--max-num-seqs`, `--max-num-batched-tokens` / `--max-running-requests`, `--chunked-prefill-size`
8. Спекуляция: последней, после бенча без неё

Соответствие флагов между движками: [references/flags-map.md](references/flags-map.md).

## Air-gap

- Переменные ставит `serve.sh`: `HF_HUB_OFFLINE=1`, `TRANSFORMERS_OFFLINE=1`, `VLLM_NO_USAGE_STATS=1`, `DO_NOT_TRACK=1`
- Веса только safetensors с `config.json`, `tokenizer.json`, `tokenizer_config.json` (там chat template) и `generation_config.json`; sha256 на каждый файл при переносе
- Версии зафиксированы: движок, torch, CUDA toolkit, драйвер; образ docker по digest, не по тегу `latest`
- Новая модель часто требует pre-release движка: держать два профиля, старый не удалять до прохождения gate

## Типичные фейлы при старте

| Симптом в логе | Причина | Действие |
|---|---|---|
| `CUDA out of memory` при загрузке весов | веса не влезают при текущем TP | `task vram`, поднять TP или взять FP8/AWQ-версию |
| `The model's max seq len ... is larger than the maximum number of tokens that can be stored in KV cache` | после весов не остался KV даже на один запрос | снизить `--max-model-len`, поднять utilization, `--kv-cache-dtype fp8` |
| `Address already in use` | старый процесс или другой профиль на порту | `task stop`, `task gpu` на чужие процессы |
| `does not appear to have a file named config.json` / tokenizer | неполный перенос весов | проверить sha256 и состав директории |
| `Model architectures [...] are not supported` | движок старее модели | профиль с новой версией движка, старый оставить |
| `torch.cuda ... no kernel image` / `CUDA driver version is insufficient` | несовместимость драйвера, CUDA и колеса torch | восстановить закреплённые версии из журнала |
| healthy, но `task smoke-toolcall` FAIL | парсер или chat template | skill `roofline-toolcall-ru` |
| healthy, TTFT секунды на коротком промпте | cudagraph и kernel warmup не прошли или `--enforce-eager` | дать прогрев 1-2 минуты, убрать eager, повторить bench |

Если сервер жив, но ведёт себя неверно: `task logs INFER_PROFILE=<name>` и дальше по skill `roofline-incident-ru`.

## Источники

- [vLLM: vllm serve](https://docs.vllm.ai/en/latest/cli/serve/), [vLLM: parallelism and scaling](https://docs.vllm.ai/en/latest/serving/parallelism_scaling/), [vLLM: troubleshooting](https://docs.vllm.ai/en/latest/usage/troubleshooting/)
- [SGLang: server arguments](https://docs.sglang.ai/advanced_features/server_arguments.html)
- roadmap.sh: [Inference Engines](https://roadmap.sh/inference-engineering/inference-engines@01j1KkEB-nIXxP-rENcJ3), [vLLM](https://roadmap.sh/inference-engineering/vllm@wcAtbab81IJdpFh6L-heP), [SGLang](https://roadmap.sh/inference-engineering/sglang@YtlAf6qloKMmaSr9Bkkl_), [Dependency Management](https://roadmap.sh/inference-engineering/dependency-management@wEaM8VyAo6MFsc3RXQ7Ar), [safetensors](https://roadmap.sh/inference-engineering/safetensors@jkbrf0_JDljWmVq_o9XE-)
