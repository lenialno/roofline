---
name: roofline-perf-ru
description: Ускорить и измерить LLM-инференс на vLLM/SGLang: бюджет VRAM и KV-кеша, continuous batching, prefix/radix cache, квантование (FP8, AWQ, GPTQ, fp8 KV) и его цена для tool calling, спекулятивное декодирование, TTFT/TPOT/p95, методика бенча (make bench, make vram, make metrics). Use when asked why the server is slow, how to raise throughput or concurrency, which quantization to pick, how to size the KV cache, tune max-num-seqs, max-num-batched-tokens or max-model-len, or how to run and read a benchmark. Russian-language version; the English skill has the same name without -ru.
license: MIT
---

# Производительность

Все `task` ниже: `task -t ${CLAUDE_SKILL_DIR}/../roofline-toolbox/Taskfile.yml <задача>` или include этого Taskfile в проектном (`task infer:<задача>`). Переменные `INFER_URL`, `INFER_PROFILE` берутся из окружения, из аргументов (`task serve INFER_PROFILE=x`) или из `inference.env` в текущем каталоге.

## Метрики и цели

| Метрика | Что измеряет | Чем определяется | Цель для кодовых агентов (стартовая) |
|---|---|---|---|
| TTFT | время до первого токена | prefill (compute-bound) плюс очередь | p95 до 2 с при промпте 20k токенов и тёплом prefix cache |
| TPOT (ITL) | время между токенами | decode (memory-bound): каждый токен читает все веса | p95 до 50 мс, то есть от 20 токенов/с на поток |
| TPS на пользователя | скорость потока | обратная TPOT | от 20 до 40 токенов/с |
| TPS общий | пропускная способность | размер батча, ширина памяти | выше при большем батче ценой TPOT |
| p50/p95/p99 | распределение | очередь и длинные промпты | решения по p95, не по среднему |
| e2e | что видит клиент | плюс сеть, прокси, очередь | если e2e велик при быстром сервере, виноват прокси |

Формулы и определения: [references/metrics.md](references/metrics.md). Снять текущее: `task metrics` (гистограммы с момента старта), под нагрузкой: `task bench`.

## Диагностика за одну минуту

| Картина | Узкое место | Рычаг |
|---|---|---|
| TTFT высокий, TPOT в норме | prefill или очередь | prefix cache hit, chunked prefill, меньше `max-num-seqs`, вторая реплика |
| TPOT высокий, TTFT в норме | decode: батч велик или TP мал | меньше `max-num-seqs`, fp8 KV и FP8 веса (меньше байт на токен), TP на NVLink |
| Оба растут, `waiting` больше 0 | очередь: KV или лимит seqs | `task vram`, ниже `max-model-len`, fp8 KV, реплика |
| `preemptions` растут | KV-кеш кончается под нагрузкой | те же меры; preemption это recompute, он удваивает prefill |
| prefix cache hit ниже 50% у агентов | нестабильный префикс или round-robin между репликами | стабильный системный промпт, маршрутизация по сессии |

Prefill compute-bound, decode memory-bound (roadmap, LLM Bottlenecks): квантование весов ускоряет decode, но почти не трогает prefill; prefix cache убирает prefill, но не меняет decode.

## Память

KV на токен = 2 x слои x kv_heads x head_dim x байт. Qwen3-32B: 256 КБ на токен в bf16, 128 КБ в fp8. Веса плюс KV плюс 2-4 ГБ накладных на GPU. Бюджет и concurrency: `task vram MODEL=... GPU_GB=.. TP=.. CTX=.. KV_DTYPE=fp8`.

Рычаги по порядку: `max-model-len` под реальные промпты, fp8 KV, FP8 веса, TP, меньше `max-num-seqs`. MoE: в батче активны почти все эксперты, память под веса считать целиком.

## Батчинг и кеш

- Continuous batching включён всегда; `max-num-seqs` ограничивает параллельные запросы, `max-num-batched-tokens` ограничивает токены на шаг (prefill дробится chunked prefill и не блокирует decode)
- Больше батч, выше общий TPS и выше TPOT; порог ищется бенчем при C = 1, 4, 8, 16, 32
- Prefix cache: vLLM блочный, SGLang radix; выигрыш на длинных системных промптах и многоходовых агентах; hit rate в `task metrics`
- Несколько реплик: маршрутизация по префиксу или сессии, иначе hit rate делится на число реплик

## Квантование

| Вариант | Память | Скорость decode | Риск для tool calling | Когда |
|---|---|---|---|---|
| bf16 | 2 Б/параметр | базовая | нет | эталон для сравнения |
| FP8 (W8A8, Hopper и новее) | 1 Б | заметно выше | минимальный | первый выбор в проде |
| fp8 KV cache | KV вдвое меньше | выше при длинном контексте | малый | вместе с FP8 весами |
| AWQ / GPTQ 4-bit | 0.5 Б | выше при малом батче, ниже при большом | заметный: ломается JSON аргументов | только если модель иначе не влезает |
| FP4 / NVFP4 (Blackwell) | 0.5 Б | высокая | проверять | Blackwell, модели с официальным FP4 |

Протокол проверки (roadmap, Measuring Quality Impact): перплексия на своём тексте до и после (рост больше 1-2% это сигнал), `task smoke-toolcall`, свой набор задач агента, затем `task bench`. Квантованная модель, не прошедшая smoke, в прод не идёт. Детали: [references/quantization.md](references/quantization.md).

## Спекулятивное декодирование

Использует простаивающий compute в memory-bound decode: несколько черновых токенов проверяются одним проходом. Выгода падает с ростом батча и температуры (roadmap, Speculative Decoding), поэтому включать последней и мерить при реальной конкурентности.

- n-gram: без второй модели, хорош для кода и правок текста (вывод повторяет вход); vLLM `--speculative-config '{"method":"ngram",...}'`
- EAGLE3: черновая голова под конкретную модель; выгода при C до 8
- draft-target: отдельная малая модель той же семьи; самый дорогой по памяти

## Бенч

`task bench BENCH_N=32 BENCH_C=8 BENCH_IN=2048 BENCH_OUT=256`: фиксированный промпт, `temperature 0`, `ignore_eos`, p50/p95/p99 TTFT, TPOT, e2e, общий tok/s, вердикт по `SLO_TTFT_P95_MS` и `SLO_TPOT_P95_MS`. Правила: baseline до изменений, одна переменная за прогон, длины как у реальных клиентов, прогрев перед замером, результаты в журнал. Методика и шаблон записи: [references/bench-protocol.md](references/bench-protocol.md).

## Источники

- [vLLM: optimization and tuning](https://docs.vllm.ai/en/latest/configuration/optimization/), [quantization](https://docs.vllm.ai/en/latest/features/quantization/), [speculative decoding](https://docs.vllm.ai/en/latest/features/spec_decode/), [automatic prefix caching](https://docs.vllm.ai/en/latest/features/automatic_prefix_caching/), [metrics design](https://docs.vllm.ai/en/latest/design/metrics/)
- [SGLang: hyperparameter tuning](https://docs.sglang.ai/advanced_features/hyperparameter_tuning.html), [speculative decoding](https://docs.sglang.ai/advanced_features/speculative_decoding.html), [quantization](https://docs.sglang.ai/advanced_features/quantization.html), [production metrics](https://docs.sglang.ai/references/production_metrics.html), [bench_serving](https://docs.sglang.ai/developer_guide/bench_serving.html), [genai-bench](https://github.com/sgl-project/genai-bench)
- roadmap.sh: [Time to First Token](https://roadmap.sh/inference-engineering/time-to-first-token@xCgNhwbS_ELxEyRHD1enO), [Bottleneck Analysis](https://roadmap.sh/inference-engineering/bottleneck-analysis@Gtd4g4MtB9zFfahRpbE2K), [Quantization](https://roadmap.sh/inference-engineering/quantization@DaSqcLHfnJ4_n9utVVTSk), [Speculative Decoding](https://roadmap.sh/inference-engineering/speculative-decoding@gMWgd10cxcQG_RG2oSAEH), [Caching](https://roadmap.sh/inference-engineering/caching@PzEj5yq1lDQ324RWYpDdQ), [Performance Benchmarking](https://roadmap.sh/inference-engineering/performance-benchmarking@XXfjlqd0CYHwBR5-Kdmmi)
- Бурков: перплексия, с. 85-89; KV-кеш, с. 140-141; выборка и температура, с. 174-179
