---
name: inference-engineer
description: Маршрутизатор роли Inference Engineer для on-prem LLM-serving (vLLM/SGLang, OpenAI-совместимый endpoint, air-gap). Use when the user asks what to do first with a local LLM server, how to approach a serving task, which skill, make target or agent to use, what is inside or outside the inference engineer role, or talks about LLM serving, GPU inference, inference engineering in general terms.
---

# Inference Engineer: с чего начать

Роль по roadmap.sh: делать так, чтобы модель отвечала быстро, дёшево и предсказуемо в проде. Стек этого пакета: on-prem GPU, vLLM или SGLang, OpenAI-совместимый endpoint, клиенты Claude Code и Qwen Code через прокси. Код и веса не покидают контур.

## Первые пять минут

```bash
task -t ${CLAUDE_PLUGIN_ROOT}/Taskfile.yml status     # gpu + health + models
task -t ${CLAUDE_PLUGIN_ROOT}/Taskfile.yml metrics    # очередь, KV, prefix cache, p95
```

Нет сервера: skill `inference-runtime`. Сервер есть, но не отвечает или деградировал: `inference-slo-incident`. Всё работает и нужно быстрее: `inference-perf`.

## Куда идти по запросу

| Запрос | Носитель |
|---|---|
| поднять, перезапустить, выбрать vLLM или SGLang, написать профиль | skill `inference-runtime`, `task serve/stop/logs/flags` |
| tool calls приходят текстом, parser, chat template, подключить Claude Code или Qwen Code | skill `inference-toolcall`, `task smoke-toolcall` |
| медленно, OOM под нагрузкой, квантование, KV, batching, бенч | skill `inference-perf`, `task bench/vram/metrics` |
| сервер лежит, очередь, p95 выше SLO, после обновления сломалось | skill `inference-slo-incident`, затем агент `incident-investigator` для долгого разбора логов |
| сколько GPU, сколько пользователей, план выкатки и отката | skill `inference-capacity`, `task vram` |
| что умеет GPU прямо сейчас, какие модели подняты | `task gpu`, `task models` |

Агент `incident-investigator` нужен только когда разбор требует читать длинные логи или сравнивать метрики за часы: он работает в своём контексте и возвращает выжимку.

## Границы роли

В роли: serving, runtime-флаги, KV-кеш и батчинг, квантование с проверкой качества, SLO и метрики, GPU-память и TP, observability, capacity, выкатка. Полная карта по 136 узлам roadmap: [references/competency-map.md](references/competency-map.md).

Вне роли: обучение и research, fine-tuning и дистилляция как основная работа (знаем, когда их заказать), облачный serving (GKE, SageMaker, HF Endpoints), кастомные CUDA-ядра, image/video/speech-пайплайны, NVIDIA Dynamo и дезагрегация prefill/decode (нужны при многоузловом кластере, не при одном-двух серверах).

## Правила работы

- Сначала измерить, потом менять: `task metrics` и `task bench` до и после, одна переменная за раз
- Флаги брать с установленной версии: `task flags Q=<слово>`, не из памяти
- После любого изменения конфигурации: `task health`, `task smoke-toolcall`, `task bench`
- Профили запуска только из `profiles/`; произвольные команды сервера через Taskfile не выполняются
- Нет данных по SLO или нагрузке: спросить, не додумывать

Теория, на которую опираются остальные skills (KV-кеш, выборка, chat-формат, перплексия) с номерами страниц книги Буркова: [references/theory-from-burkov.md](references/theory-from-burkov.md).
