---
name: roofline-incident-ru
description: "Runbook инцидентов LLM-serving на vLLM/SGLang: endpoint не отвечает, CUDA OOM, очередь растёт, TTFT или TPOT p95 выше SLO, preemptions, таймауты клиентов, tool calls сломались после обновления. Use when the server is down or degraded, requests time out, GPU memory is full, latency percentiles spiked, Claude Code or Qwen Code report errors, or to run the triage sequence make health, metrics, gpu, logs. Russian-language version; the English skill has the same name without -ru."
license: MIT
---

# Инцидент: порядок разбора

Цель: за пять минут понять, где поломка (сервер, память, очередь, парсер, прокси), и выбрать наименее разрушительное действие. Перезапуск последний.

## Триаж

```bash
task -t ${CLAUDE_SKILL_DIR}/../roofline-toolbox/Taskfile.yml health      # жив ли endpoint, отвечает ли модель
task -t ${CLAUDE_SKILL_DIR}/../roofline-toolbox/Taskfile.yml metrics     # очередь, KV, preemptions, p95
task -t ${CLAUDE_SKILL_DIR}/../roofline-toolbox/Taskfile.yml gpu         # память, чужие процессы, температура
task -t ${CLAUDE_SKILL_DIR}/../roofline-toolbox/Taskfile.yml logs INFER_PROFILE=<name> LINES=200
```

Затем по таблице; полная таблица симптомов в [references/symptoms.md](references/symptoms.md).

| health | metrics | Диагноз | Действие |
|---|---|---|---|
| `/health` 000 | нет | процесс мёртв или порт закрыт | `task logs`: последняя ошибка; `task gpu`: память освобождена; `task serve` |
| `/health` 200, completion FAIL | нет ответа | движок завис (часто после CUDA-ошибки или NCCL-таймаута при TP) | лог на `CUDA error`, `NCCL`, `watchdog`; `task restart` |
| OK | `waiting` растёт, KV выше 90% | KV-кеш исчерпан, запросы ждут | ниже `max-model-len` или fp8 KV в профиле; временно ограничить клиентов |
| OK | `waiting` растёт, KV ниже 70% | упор в `max-num-seqs` или compute decode | поднять `max-num-seqs` после `task bench`; вторая реплика |
| OK | `preemptions` растут | под нагрузкой KV переполняется, recompute | как для KV; preemption удваивает prefill |
| OK | TTFT p95 растёт, hit rate упал | клиенты шлют новый префикс, кеш не работает | сверить системный промпт, маршрутизацию по сессии |
| OK | TPOT p95 растёт при том же трафике | соседний процесс на GPU, троттлинг по температуре или мощности | `task gpu`: процессы, temp, watts |
| OK, metrics OK | клиенты видят ошибки | прокси, таймауты, парсер | `task smoke-toolcall` против endpoint прокси; таймаут прокси против e2e p99 |

## OOM: три разных случая

| Когда | Признак | Причина | Действие |
|---|---|---|---|
| при старте | `CUDA out of memory` до `/health` | веса не влезают при TP | `task vram`; TP, FP8, другой GPU |
| при старте | `max seq len ... larger than ... KV cache` | после весов нет KV на один запрос | ниже `max-model-len`, выше utilization, fp8 KV |
| под нагрузкой | OOM в prefill длинного промпта, движок падает | utilization выше 0.92 или chunked prefill выключен | utilization 0.88-0.90, `chunked prefill` включить, `max-num-batched-tokens` 8192 |

## После обновления

Сломалось после смены версии движка, модели или шаблона: `task smoke-toolcall` первым. Регресс парсера или шаблона это самая частая причина "модель поглупела" без изменения метрик. Откат: `task stop` нового профиля, `task serve` старого (профили не удаляются до прохождения gate).

## Правила действий

1. Сначала снять `metrics` и `logs` в тикет, потом трогать сервер: после рестарта данные пропадут
2. Одно действие за раз; после каждого `task health` и `task metrics`
3. `task restart` только когда процесс мёртв, завис или OOM под нагрузкой; очередь и медленный p95 рестарт не лечит
4. Изменение профиля фиксируется в журнале с причиной
5. Длинный лог, корреляция за часы, несколько гипотез: передать агенту `incident-investigator`, он вернёт вердикт и следующий шаг

## Постмортем

Шаблон: [references/postmortem.md](references/postmortem.md). Поля: таймлайн, симптом, метрики до и после, корневая причина, что изменили, что добавить в `task bench` или smoke, чтобы ловить раньше.

## Источники

- [vLLM: metrics design](https://docs.vllm.ai/en/latest/design/metrics/), [vLLM: troubleshooting](https://docs.vllm.ai/en/latest/usage/troubleshooting/)
- [SGLang: production metrics](https://docs.sglang.ai/references/production_metrics.html)
- roadmap.sh: [Observability](https://roadmap.sh/inference-engineering/observability@w-dVv5dFNxD7Rqy16m4uL), [Request Queueing](https://roadmap.sh/inference-engineering/request-queueing@k-zXOGynI0B0yyT-n3raa), [Continuous Batching](https://roadmap.sh/inference-engineering/continuous-batching@h_PDOMA-V-n7Pab3epuP3), [Zero-Downtime Deployment](https://roadmap.sh/inference-engineering/zero-downtime-deplo@le4sPQ0h9l-vlmCB4G8ZY)
