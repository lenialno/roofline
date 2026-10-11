---
name: roofline-capacity-ru
description: Спроектировать on-prem LLM-serving под нагрузку и безопасно выкатить: расчёт GPU, VRAM и TP под модель и контекст, concurrency под SLO, число реплик, выбор модели под evals, план canary-выкатки и отката, фиксация версий, перенос весов в air-gap. Use when asked how many GPUs are needed, which model fits the hardware, how many concurrent Claude Code or Qwen Code users a server handles, how to roll out a new model or runtime version safely, or to estimate cost of dedicated inference. Russian-language version; the English skill has the same name without -ru.
license: MIT
---

# Capacity и выкатка

Все `task` ниже: `task -t ${CLAUDE_SKILL_DIR}/../roofline-toolbox/Taskfile.yml <задача>` или include этого Taskfile в проектном (`task infer:<задача>`). Переменные `INFER_URL`, `INFER_PROFILE` берутся из окружения, из аргументов (`task serve INFER_PROFILE=x`) или из `inference.env` в текущем каталоге.

## Входные данные

Без них расчёт недействителен; нет данных, пишем "неизвестно" и просим измерить.

| Параметр | Откуда | Типично для кодовых агентов |
|---|---|---|
| Пользователи одновременно | клиенты, прокси | 5-50 на команду |
| Длина промпта (p50, p95) | `task metrics` prompt tokens, логи прокси | 10k-60k, системный промпт стабилен |
| Длина ответа | там же | 200-2000 токенов, с thinking больше |
| Запросов на действие пользователя | клиент | агент делает 5-30 вызовов на задачу |
| SLO | договор с командой | TTFT p95 2 с, TPOT p95 50 мс |
| Модель и качество | evals, smoke-toolcall | наименьшая модель, проходящая evals |
| GPU | `task gpu` | тип, число, NVLink между ними |

## Расчёт

1. Веса: байт на параметр x параметры; FP8 даёт около 1 ГБ на 1B параметров (roadmap: Sizing & Procurement) плюс не менее 50% на KV
2. KV на токен: 2 x слои x kv_heads x head_dim x байт; MoE и MLA считает `task vram`
3. Токены в KV = (VRAM x utilization x TP минус веса минус накладные) / KV на токен
4. Concurrency = токены в KV / средняя длина запроса в полёте (промпт плюс ответ); у агентов в полёте висит промпт целиком
5. Закон Литтла: одновременных запросов = RPS x средняя e2e; RPS = пользователи x вызовов в минуту / 60
6. Реплики = ceil(нужная concurrency / concurrency одной реплики с запасом 30%)
7. Проверка: `task bench BENCH_C=<concurrency> BENCH_IN=<p95 промпта>`; p95 внутри SLO, иначе шаг назад

`task vram MODEL=/models/x GPU_GB=80 TP=2 CTX=65536 KV_DTYPE=fp8 AVG_TOKENS=24000` печатает веса, KV на токен, токены в полёте и concurrency. Рабочий лист с примером: [references/sizing-worksheet.md](references/sizing-worksheet.md).

## TP против реплик

| Нужно | Выбор |
|---|---|
| Модель не влезает в один GPU | TP по числу GPU в NVLink-группе (2, 4, 8); TP между узлами не делать |
| Ниже TPOT при той же модели | TP (веса читают несколько GPU параллельно) |
| Больше пользователей при SLO в норме | реплики плюс маршрутизация по сессии для prefix cache |
| Разные модели для разных задач | отдельные профили на отдельных GPU, `CUDA_VISIBLE_DEVICES` |
| Один GPU на несколько маленьких моделей | MIG или две реплики с utilization 0.45 каждая |

## Выкатка

1. Профиль новой версии рядом со старым (другой порт), версии зафиксированы: движок, torch, CUDA, драйвер, digest образа
2. Gate на новом порту: `task health`, `task smoke-toolcall`, `task bench` не хуже baseline по p95
3. Canary через прокси: 5-10% трафика, 30-60 минут, смотреть `task metrics` обеих реплик и ошибки клиентов
4. Переключение остального трафика; старый профиль живёт до конца дня
5. Откат: трафик на старый порт, `task stop` нового. Blue-green на GPU не делаем: он требует удвоенной памяти (roadmap: Zero-Downtime Deployment), canary дешевле

Чеклист с полями: [references/rollout-checklist.md](references/rollout-checklist.md).

## Air-gap

- Веса: только safetensors, sha256 по каждому файлу на обеих сторонах, `config.json`, `tokenizer*.json`, `generation_config.json` в комплекте
- Образы и колёса: по digest, зеркало внутри контура, `pip install` в проде запрещён
- Телеметрия: `VLLM_NO_USAGE_STATS=1`, `HF_HUB_OFFLINE=1`; endpoint закрыт токеном и сетью
- Новая модель: сначала smoke на стенде вне прода, затем перенос профиля

## Стоимость

Dedicated против API (roadmap: Cost Estimation): GPU-час x число GPU x часы против цены за токен x реальный трафик за то же окно, плюс время инженера. Для агентов с длинными промптами и prefix cache dedicated выигрывает раньше: API считает все входные токены, свой сервер считает только некешированные.

## Источники

- roadmap.sh: [Sizing and Procurement](https://roadmap.sh/inference-engineering/sizing-procurement@da0HGfSDr6_DV4ZJcrcIB), [Cost Estimation](https://roadmap.sh/inference-engineering/cost-estimation@Gof4kW2LbkNCtH68c7Xvq), [Zero-Downtime Deployment](https://roadmap.sh/inference-engineering/zero-downtime-deplo@le4sPQ0h9l-vlmCB4G8ZY), [Dependency Management](https://roadmap.sh/inference-engineering/dependency-management@wEaM8VyAo6MFsc3RXQ7Ar), [Model Parallelism](https://roadmap.sh/inference-engineering/model-parallelism@CiXsdHHL0e2DN4ICI5jeX)
- [vLLM: parallelism and scaling](https://docs.vllm.ai/en/latest/serving/parallelism_scaling/)
- [Закон Литтла](https://en.wikipedia.org/wiki/Little%27s_law): связь RPS, задержки и одновременных запросов
- Бурков: квадратичная стоимость внимания, с. 149-159; MoE, с. 199
