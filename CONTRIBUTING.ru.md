# Как участвовать в Roofline

[English](CONTRIBUTING.md)

Issues и pull requests приветствуются. Быстрее всего помогает устаревшее имя парсера, флага или метрики: запусти `task doctor` и открой issue с его выводом.

## Issues

Сначала поищи в [открытых issues](https://github.com/lenialno/roofline/issues), потом выбери шаблон:

| Шаблон | Когда | Метка |
|---|---|---|
| Bug | task или скрипт падает, или совет из skill не работает | `bug`, `needs triage` |
| Outdated parser, flag or metric | `task doctor` или движок показывает, что имени из таблиц больше нет | `outdated` |
| Documentation | ошибка или пробел в тексте skill, README или `docs/roadmap-ru` | `documentation` |
| Proposal | новый skill, task, семейство моделей или профиль | `enhancement`, `needs triage` |
| Question | как сделать что-то с Roofline | `question` |

Из вывода перед публикацией убери внутренние хосты, пути, API-ключи и промпты.

## Структура

| Путь | Что там |
|---|---|
| `skills/roofline*/SKILL.md` | skills; у каждого английского есть русская копия с суффиксом `-ru` |
| `skills/*/references/` | таблицы, которые читают skills: парсеры, флаги, метрики, клиенты |
| `skills/roofline-toolbox/` | общий Taskfile, скрипты и профили запуска; только английский |
| `agents/` | субагент Claude Code `incident-investigator` |
| `docs/roadmap-ru/` | перевод карты Inference Engineering с roadmap.sh |
| `.claude-plugin/plugin.json` | манифест плагина; поля `version` нет намеренно, установки следуют за коммитами |
| `.github/scripts/` | проверки репозитория (`check.py`) и еженедельная сверка с релизами (`drift.sh`) |

## Локальные проверки

Запусти перед push, CI делает то же самое:

```bash
python3 .github/scripts/check.py
npx -y @anthropic-ai/claude-code@latest plugin validate .
DISABLE_TELEMETRY=1 npx -y skills@latest add . --list
task --list
```

`check.py` проверяет frontmatter skills, пары EN и RU, относительные ссылки и типографику. Валидатор плагина выводит одно предупреждение про отсутствие `version`, так и задумано.

## Правила для текста

- Английский и русский skill меняются парно, в одном pull request.
- Имена парсеров, флагов и метрик берутся из исходников или документации движка на теге релиза, ссылка на тег идёт в pull request. По памяти не пишем.
- Версии, с которыми сверена таблица, пишем в её шапку, например "сверена с vLLM 0.31.0 и SGLang 0.5.21".
- Новый или изменённый профиль до слияния проходит `task health && task smoke-toolcall && task bench` на реальном железе. Вывод прикладываем к pull request.
- Скрипты только на стандартной библиотеке: `python3` и `bash`, без pip. Python запускается с `-I`.
- В прозе нет длинного и короткого тире, стрелок и типографских кавычек, только прямые. Это проверяет `check.py`.
- Сначала вывод, потом детали. Короткие предложения, конкретные числа.

## Коммиты

[Conventional Commits](https://www.conventionalcommits.org/) на английском, по [семи правилам](https://cbea.ms/git-commit/): повелительное наклонение, заголовок до 72 символов без точки в конце, в теле что и зачем.

| Тип | Для чего |
|---|---|
| `feat` | новый skill, task, скрипт или профиль |
| `fix` | неверное имя, сломанный скрипт, неверное число |
| `docs` | README, формулировки skills, перевод |
| `ci` | workflows и проверки репозитория |
| `chore` | всё остальное |

Scope это имя skill без префикса `roofline-` или область: `feat(toolbox): task doctor`, `fix(toolcall): kimi_k3 parser name`, `docs(roadmap-ru): hardware chapter`.

## Pull requests

1. Для нового skill, task или большой правки сначала открой Proposal.
2. Одна тема на pull request. Пока работаешь, держи его в draft.
3. Заголовок в формате коммита. Заполни шаблон: что и зачем, связанный issue, тег источника, чеклист.
4. CI должен быть зелёным. Слияние через squash, заголовок становится коммитом в `main`.

## Лицензия

Отправляя вклад, ты соглашаешься выпустить его под [лицензией MIT](LICENSE).
