# Парсеры по семействам моделей

Имена парсеров проверять на установленной версии: `task flags Q=tool-call-parser`, `task flags Q=reasoning-parser`. Таблица по документации vLLM 0.10-0.11 и SGLang 0.4-0.5; у новых моделей имя парсера указано в README весов.

| Семейство | Формат вызова | vLLM `--tool-call-parser` | SGLang `--tool-call-parser` | Reasoning parser (vLLM / SGLang) |
|---|---|---|---|---|
| Qwen3 (thinking и instruct, dense и MoE) | Hermes JSON в `<tool_call>` | `hermes` | `qwen25` | `qwen3` / `qwen3` |
| Qwen3-Coder | XML `<tool_call><function=...><parameter=...>` | `qwen3_coder` | `qwen3_coder` | нет (non-thinking) |
| Qwen2.5 и Qwen2.5-Coder | Hermes JSON | `hermes` | `qwen25` | нет |
| DeepSeek-V3 / V3.1 | свой формат с маркерами | `deepseek_v3` (V3.1: `deepseek_v31`) | `deepseekv3` | `deepseek_r1` / `deepseek-r1` |
| DeepSeek-R1 | как V3 | `deepseek_v3` | `deepseekv3` | `deepseek_r1` / `deepseek-r1` |
| GLM-4.5 / 4.6 | XML-подобный | `glm45` | `glm45` | `glm45` / `glm45` |
| Llama 3.1 / 3.3 | JSON в тексте | `llama3_json` | `llama3` | нет |
| Llama 4 | pythonic | `llama4_pythonic` | `pythonic` | нет |
| Mistral / Mixtral / Devstral | `[TOOL_CALLS]` | `mistral` (плюс `--tokenizer-mode mistral`) | `mistral` | нет |
| gpt-oss | Harmony | `openai` (вместе с `--reasoning-parser openai_gptoss`) | встроен, парсер `gpt-oss` | `openai_gptoss` / `gpt-oss` |
| Hermes / NousResearch | Hermes JSON | `hermes` | `hermes` | нет |
| Gemma 3 | JSON в тексте | нет штатного; через шаблон с tools | `gemma` | нет |
| Kimi K2 | свой | `kimi_k2` | `kimi_k2` | нет |

Признаки неверного парсера в ответе: `content` содержит `<tool_call>`, `<function=`, `[TOOL_CALLS]`, `<|python_tag|>`; `finish_reason` равен `stop` вместо `tool_calls`; `arguments` приходят строкой с экранированными кавычками внутри JSON.

## Проверка шаблона без клиента

vLLM: `POST /tokenize` с `messages` и `tools` возвращает токены собранного промпта; `"return_token_strs": true` показывает, попали ли инструменты в промпт. SGLang: `GET /get_server_info` показывает активный шаблон и парсер.

Признаки шаблона без поддержки инструментов: промпт не содержит описания функций; HTTP 400 с текстом про `tool` или `tool_calls` при истории с ролью tool; модель отвечает прозой "я бы вызвал функцию".
