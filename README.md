# inference-engineer

Claude Code plugin для роли Inference Engineer: on-prem LLM-serving на vLLM или SGLang с OpenAI-совместимым endpoint, клиенты Claude Code и Qwen Code через прокси, air-gap. Шесть skills, один subagent, Taskfile с детерминированными командами. MCP и hooks отсутствуют намеренно: всё live-состояние даёт `task`.

## Установка

```bash
claude --plugin-dir /path/to/inference-engineer        # на время сессии
claude plugin validate /path/to/inference-engineer     # проверка раскладки и frontmatter
```

Постоянно: добавить каталог в marketplace команды и `claude plugin install inference-engineer@<marketplace>`, либо скопировать `skills/*` в `~/.claude/skills/` (тогда `${CLAUDE_PLUGIN_ROOT}` в текстах заменить на путь к плагину).

Skills в сессии: `/inference-engineer:inference-engineer` (маршрутизатор), `inference-runtime`, `inference-toolcall`, `inference-perf`, `inference-slo-incident`, `inference-capacity`. Claude подхватывает их по описанию: "подними vLLM", "tool calls приходят текстом", "почему медленно", "очередь растёт", "сколько GPU нужно".

## Taskfile

Нужен [go-task](https://taskfile.dev) (`brew install go-task`). Из любого проекта: `task -t /path/to/inference-engineer/Taskfile.yml <задача>`, либо include в проектный Taskfile.yml:

```yaml
version: '3'
includes:
  infer:
    taskfile: /path/to/inference-engineer/Taskfile.yml
```

Тогда `task infer:health`. Команды выполняются в каталоге проекта: там лежат `inference.env` (строки `KEY=value`) и `.inference-state/`. Приоритет настроек: аргумент (`task serve INFER_PROFILE=x`), переменная окружения, `inference.env`, значение по умолчанию. Переменные: `INFER_URL` (без `/v1`), `INFER_API_KEY`, `INFER_PROFILE`, `INFER_STATE_DIR`, `SLO_TTFT_P95_MS`, `SLO_TPOT_P95_MS`, `BENCH_N`, `BENCH_C`, `BENCH_IN`, `BENCH_OUT`.

| Задача | Что делает |
|---|---|
| `gpu` | память, загрузка, процессы по `nvidia-smi` |
| `health` | `/health`, `/v1/models`, одна короткая генерация с замером |
| `models` | список моделей и max context |
| `metrics` | очередь, KV usage, prefix cache hit, preemptions, p50/p95 TTFT и TPOT из `/metrics` |
| `status` | `gpu` плюс `health` плюс `models` |
| `serve INFER_PROFILE=<name>` | запуск по профилю из `profiles/`, ожидание `/health`, pid и лог в `.inference-state/` |
| `stop`, `restart`, `logs` | остановка по pid, перезапуск, хвост лога (`LINES=200 FOLLOW=1`) |
| `bench` | фиксированный SLO-бенч: `BENCH_N`, `BENCH_C`, `BENCH_IN`, `BENCH_OUT`; `-- --json` для строки JSON; exit 1 при нарушении SLO |
| `smoke-toolcall` | контракт tool calling: non-stream, stream, отрицательный тест, round trip, parallel |
| `vram MODEL=/models/x` | бюджет VRAM и KV, concurrency; `GPU_GB`, `TP`, `CTX`, `KV_DTYPE=fp8` |
| `flags Q=<слово>` | grep по `--help` установленного движка (`RUNTIME=vllm` или `sglang`) |

Скрипты в `scripts/` на bash и python3 без зависимостей, идемпотентны, ненулевой exit при ошибке. Профили: [profiles/README.md](profiles/README.md).

## Subagent

`incident-investigator` вызывается skill'ом `inference-slo-incident`, когда разбор требует читать длинные логи или сравнивать метрики за часы. Работает только на чтение (`health`, `metrics`, `gpu`, `logs`, `smoke-toolcall`), возвращает вердикт на 25 строк.

## Документы

- [docs/roadmap-ru/](docs/roadmap-ru/README.md): перевод всех 136 узлов roadmap.sh/inference-engineering со ссылками на источники
- [skills/inference-engineer/references/competency-map.md](skills/inference-engineer/references/competency-map.md): что в роли и что вне, с привязкой к skills
- [skills/inference-engineer/references/theory-from-burkov.md](skills/inference-engineer/references/theory-from-burkov.md): выжимка из книги Буркова "Языковые модели без лишних слов" с номерами страниц
