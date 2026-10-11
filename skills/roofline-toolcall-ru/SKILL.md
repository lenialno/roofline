---
name: roofline-toolcall-ru
description: Настроить tool calling и chat template на vLLM/SGLang для Claude Code, Qwen Code и OpenAI-совместимых прокси: выбор --tool-call-parser и --reasoning-parser по семейству модели, проверка шаблона, стриминг tool_calls, make smoke-toolcall. Use when tool calls come back as plain text, arguments are not valid JSON, a client ignores or breaks on tools, the server returns 400 on role tool messages, thinking tags leak into content, or when connecting Claude Code, Qwen Code or a proxy to a local model. Russian-language version; the English skill has the same name without -ru.
license: MIT
---

# Tool calling и chat template

Все `task` ниже: `task -t ${CLAUDE_SKILL_DIR}/../roofline-toolbox/Taskfile.yml <задача>` или include этого Taskfile в проектном (`task infer:<задача>`). Переменные `INFER_URL`, `INFER_PROFILE` берутся из окружения, из аргументов (`task serve INFER_PROFILE=x`) или из `inference.env` в текущем каталоге.

Модель генерирует вызов инструмента текстом в своём формате (Hermes JSON в `<tool_call>`, XML у Qwen3-Coder, `[TOOL_CALLS]` у Mistral). Парсер движка превращает этот текст в OpenAI `tool_calls`. Формат задаёт chat template из `tokenizer_config.json`: он обязан совпадать с форматом обучения (Бурков, с. 164-170, ChatML и роли), иначе никакой парсер не поможет.

## Процедура

1. Семейство модели: `config.json` (`architectures`, `model_type`) и README весов
2. Шаблон поддерживает инструменты: в `tokenizer_config.json` поле `chat_template` содержит `tools`; нет его: взять шаблон из репозитория модели или движка (`--chat-template`), не писать свой
3. Парсеры по таблице в [references/parsers.md](references/parsers.md); имя проверить: `task flags Q=tool-call-parser`
4. В профиль: vLLM `--enable-auto-tool-choice --tool-call-parser <p> [--reasoning-parser <r>]`; SGLang `--tool-call-parser <p> [--reasoning-parser <r>]`
5. `task serve`, затем `task smoke-toolcall`: non-stream, stream, отрицательный тест, round trip с ролью tool, параллельные вызовы
6. Подключить клиента по [references/clients.md](references/clients.md) и прогнать реальную задачу (прочитать файл, сделать правку)

## Что проверяет smoke-toolcall и как читать FAIL

| FAIL | Причина | Действие |
|---|---|---|
| `nonstream`: tool call пришёл текстом (`<tool_call>`, `<function=`) | парсер не включён или не тот | флаги из п. 4, парсер по семейству |
| `nonstream`: модель ответила прозой без вызова | шаблон без tools или квантованная модель потеряла навык | шаблон из репозитория; сравнить с FP8/bf16-версией |
| `stream` падает при рабочем `nonstream` | стриминговый парсер этой версии движка сломан для модели | обновить движок, временно `stream: false` в прокси |
| `arguments are not valid JSON` | 4-битная квантизация или парсер чужого семейства | FP8 вместо AWQ/GPTQ; парсер по таблице |
| `roundtrip`: HTTP 400 | шаблон не принимает `role: tool` или `tool_calls` в assistant | шаблон с поддержкой истории инструментов |
| `negative`: вызов без нужды | `tool_choice: required` в прокси или модель слабая | `tool_choice: auto`; другая модель |
| `parallel`: один вызов на два города (INFO) | модель или парсер без parallel calls | не блокер; клиентам хватает последовательных |

## Reasoning-модели

Thinking-модели (Qwen3, DeepSeek-R1, GLM-4.5) пишут `<think>` до ответа. Без `--reasoning-parser` рассуждение попадает в `content`, клиент показывает его пользователю, а tool call после `</think>` может потеряться. С парсером рассуждение уходит в `reasoning_content`. Отключить размышления на запрос: `chat_template_kwargs: {"enable_thinking": false}` (Qwen3). Для кодовых агентов обычно выгоднее non-thinking режим: ниже TTFT и стоимость.

## Квантование и качество вызовов

Tool calling страдает от квантования первым: аргументы должны быть точным JSON. Порядок предпочтений: bf16, FP8 (Hopper и новее), затем AWQ/GPTQ 4-bit только после `task smoke-toolcall` и своего набора задач. Детали в skill `roofline-perf-ru`.

## Безопасность

Результаты инструментов это внешние данные: инъекция команд через них (Бурков, с. 201-202) исполняется агентом, а не моделью. Движок это не фильтрует; ограничения ставить в клиенте и прокси: allowlist инструментов, подтверждение деструктивных действий.

## Источники

- [vLLM: tool calling](https://docs.vllm.ai/en/latest/features/tool_calling/), [vLLM: reasoning outputs](https://docs.vllm.ai/en/latest/features/reasoning_outputs/)
- [SGLang: tool parser](https://docs.sglang.ai/advanced_features/tool_parser.html)
- [Transformers: chat templates](https://huggingface.co/docs/transformers/chat_templating)
- [Qwen Code](https://github.com/QwenLM/qwen-code), [Claude Code: LLM gateway configuration](https://code.claude.com/docs/en/llm-gateway)
- roadmap.sh: [AI-Native Applications](https://roadmap.sh/inference-engineering/ai-native-applications@ZqFQmNizkU6ykTMCrmTWf), [Measuring Quality Impact](https://roadmap.sh/inference-engineering/measuring-quality-impact@mK_4R8liXtl64iG7ONvgz)
- Бурков: ChatML и роли, с. 164-170; джейлбрейк и prompt injection, с. 201-202
