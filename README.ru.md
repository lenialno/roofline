# roofline

[English](README.md)

Claude Code plugin для роли Inference Engineer: on-prem LLM-serving на vLLM или SGLang с OpenAI-совместимым endpoint, клиенты Claude Code и Qwen Code через прокси, air-gap. Skills на двух языках (английские без суффикса, русские с суффиксом `-ru`), toolbox-skill с Taskfile и скриптами, один subagent. MCP и hooks отсутствуют намеренно: всё live-состояние даёт `task`.

## Установка

```bash
claude --plugin-dir /path/to/roofline        # на время сессии
claude plugin validate /path/to/roofline     # проверка раскладки и frontmatter
```

Постоянно, во всех проектах (user scope), репозиторий сам является marketplace:

```bash
claude plugin marketplace add ssh://git@gitlab.millennial.ninja:2222/roofline/claude-code-skills.git
claude plugin install roofline@leo-skills
```

Обновление после push: `claude plugin marketplace update leo-skills`, затем `claude plugin update roofline@leo-skills` и `/reload-plugins`. Из локального клона (`claude plugin marketplace add ./roofline`) правки подхватываются сразу, без обновления.

Без Claude Code plugin, как обычные Agent Skills (Claude Code, Codex, Cursor и другие): `npx skills add <owner>/<repo> --skill roofline-toolbox --skill roofline-runtime-ru` или `npx skills add <owner>/<repo> --all`; `-g` ставит в `~/.claude/skills/`.

Skills в сессии: `/roofline:roofline-ru` (маршрутизатор), `roofline-runtime-ru`, `roofline-toolcall-ru`, `roofline-perf-ru`, `roofline-incident-ru`, `roofline-capacity-ru`, общий `roofline-toolbox`; те же skills без `-ru` на английском. Claude подхватывает их по описанию: "подними vLLM", "tool calls приходят текстом", "почему медленно", "очередь растёт", "сколько GPU нужно".

## Taskfile

Нужен [go-task](https://taskfile.dev) (`brew install go-task`). Из любого проекта: `task -t /path/to/roofline/Taskfile.yml <задача>` (корневой Taskfile включает toolbox без namespace), либо include в проектный Taskfile.yml:

```yaml
version: '3'
includes:
  infer:
    taskfile: /path/to/roofline/skills/roofline-toolbox/Taskfile.yml
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

Скрипты в `skills/roofline-toolbox/scripts/` на bash и python3 без зависимостей, идемпотентны, ненулевой exit при ошибке. Профили: [profiles/README.md](skills/roofline-toolbox/profiles/README.md).

## Subagent

`incident-investigator` вызывается skill'ом `roofline-incident-ru`, когда разбор требует читать длинные логи или сравнивать метрики за часы. Работает только на чтение (`health`, `metrics`, `gpu`, `logs`, `smoke-toolcall`), возвращает вердикт на 25 строк.

## Документы

- [docs/roadmap-ru/](docs/roadmap-ru/README.md): перевод всех 136 узлов roadmap.sh/inference-engineering со ссылками на источники
- [skills/roofline-ru/references/competency-map.md](skills/roofline-ru/references/competency-map.md): что в роли и что вне, с привязкой к skills
- [skills/roofline-ru/references/theory-from-burkov.md](skills/roofline-ru/references/theory-from-burkov.md): выжимка из книги Буркова "Языковые модели без лишних слов" с номерами страниц

## Лицензия

MIT, см. [LICENSE](LICENSE). Источники каждого skill перечислены в его разделе "Источники".
