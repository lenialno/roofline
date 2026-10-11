<picture>
  <source media="(prefers-color-scheme: dark)" srcset="brand/png/readme-header-dark-1200x400-2x.png">
  <img alt="Roofline" src="brand/png/readme-header-light-1200x400-2x.png" width="1200">
</picture>

# Roofline

<img src="assets/lenialno.svg" alt="Lenialno" height="18" align="top"> Roofline, линейка Lenialno. [English](README.md)

[![skills.sh](https://skills.sh/b/lenialno/roofline)](https://skills.sh/lenialno/roofline)

Claude Code plugin и Agent Skills для роли Inference Engineer: on-prem LLM-serving на vLLM или SGLang с OpenAI-совместимым endpoint, клиенты Claude Code и Qwen Code через прокси, air-gap. Шесть skills со знаниями на английском и на русском (суффикс `-ru`), toolbox-skill с Taskfile и скриптами без зависимостей, один subagent Claude Code для разбора инцидентов. Карта компетенций повторяет [roadmap.sh/inference-engineering](https://roadmap.sh/inference-engineering); каждый skill перечисляет свои источники. MCP и hooks отсутствуют намеренно: всё live-состояние даёт `task`.

## Skills

| Skill | Задача |
|---|---|
| `roofline` | маршрутизатор роли: что делать первым, что в роли и что вне, какой skill или задачу брать |
| `roofline-runtime` | поднять и держать vLLM или SGLang: выбор движка, порядок флагов, профили запуска, air-gap, фейлы при старте |
| `roofline-toolcall` | tool calling и chat template: парсер по семейству модели, стриминг tool_calls, подключение Claude Code и Qwen Code |
| `roofline-perf` | метрики и SLO, бюджет VRAM и KV-кеша, батчинг, prefix cache, квантование с протоколом проверки качества, спекулятивное декодирование, бенч |
| `roofline-incident` | runbook: порядок триажа, виды OOM, очередь, нарушение p95, регресс после обновления, постмортем |
| `roofline-capacity` | расчёт GPU и TP, concurrency под SLO, реплики, canary-выкатка и откат, стоимость |
| `roofline-toolbox` | Taskfile и скрипты: gpu, health, models, metrics, serve, stop, bench, smoke-toolcall, vram, flags |

Русские версии: те же имена с суффиксом `-ru`. Toolbox общий для обоих языков. Claude подхватывает skills по описанию: "подними vLLM", "tool calls приходят текстом", "почему медленно", "очередь растёт", "сколько GPU нужно".

## Установка

Как Agent Skills, для любого агента с их поддержкой (Claude Code, Codex, Cursor, OpenCode и другие):

```bash
npx skills add lenialno/roofline --skill roofline-toolbox --skill roofline-runtime-ru   # выбранные skills
npx skills add lenialno/roofline --all                                                   # все skills, все агенты
npx skills add lenialno/roofline -g -a claude-code --skill roofline-toolbox              # user scope, только Claude Code (~/.claude/skills/)
```

Как Claude Code plugin, во всех проектах на машине (user scope), из каталога Lenialno [lenialno/skills](https://github.com/lenialno/skills):

```bash
claude plugin marketplace add lenialno/skills
claude plugin install roofline@lenialno
```

Обновление после push: `claude plugin marketplace update lenialno`, затем `claude plugin update roofline@lenialno` и `/reload-plugins`. На одну сессию из локального клона: `claude --plugin-dir /path/to/roofline`; проверка клона: `claude plugin validate /path/to/roofline`.

Для toolbox нужны python3 и curl; [go-task](https://taskfile.dev) для `task` (`brew install go-task`); nvidia-smi для `gpu`. Скрипты работают и без task.

## Taskfile

Из любого проекта: `task -t /path/to/roofline/Taskfile.yml <задача>` (корневой Taskfile включает toolbox без namespace), либо include в проектный Taskfile.yml:

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
| `profiles` | список профилей запуска в `profiles/` |
| `metrics` | очередь, KV usage, prefix cache hit, preemptions, p50/p95 TTFT и TPOT из `/metrics` |
| `status` | `gpu`, затем `health`, затем `models` |
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

- [docs/roadmap-ru/](docs/roadmap-ru/README.md): перевод всех 136 узлов roadmap.sh/inference-engineering со ссылками на источники. Одно сознательное отличие от оригинала: узел Writing Custom Kernels адаптирован под Rust (cudarc, CubeCL, Rust-CUDA) вместо C++ и Triton, карта компетенций следует тому же выбору
- [skills/roofline-ru/references/competency-map.md](skills/roofline-ru/references/competency-map.md): что в роли и что вне, с привязкой к skills
- [skills/roofline-ru/references/theory-from-burkov.md](skills/roofline-ru/references/theory-from-burkov.md): выжимка из книги Буркова "Языковые модели без лишних слов" с номерами страниц

## Бренд

Логотип, знак, favicon и шапки README лежат в [brand/](brand/BRAND.md) вместе с правилами цвета и геометрии. Знак для терминала: [brand/ascii.txt](brand/ascii.txt), его печатает `task` без аргументов.

## Источники и лицензия

Основные источники: [roadmap.sh: Inference Engineering](https://roadmap.sh/inference-engineering), [документация vLLM](https://docs.vllm.ai/), [документация SGLang](https://docs.sglang.ai/), [документация Claude Code](https://code.claude.com/docs/en/skills), [спецификация Agent Skills](https://agentskills.io/specification), книга Андрея Буркова. Каждый skill заканчивается своим разделом "Источники". Лицензия MIT, см. [LICENSE](LICENSE).
