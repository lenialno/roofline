# Parsers by model family

Verify parser names on the installed version: `task flags Q=tool-call-parser`, `task flags Q=reasoning-parser`. The table follows the vLLM 0.10-0.11 and SGLang 0.4-0.5 docs; for newer models the parser name is given in the README of the weights.

| Family | Call format | vLLM `--tool-call-parser` | SGLang `--tool-call-parser` | Reasoning parser (vLLM / SGLang) |
|---|---|---|---|---|
| Qwen3 (thinking and instruct, dense and MoE) | Hermes JSON inside `<tool_call>` | `hermes` | `qwen25` | `qwen3` / `qwen3` |
| Qwen3-Coder | XML `<tool_call><function=...><parameter=...>` | `qwen3_coder` | `qwen3_coder` | none (non-thinking) |
| Qwen2.5 and Qwen2.5-Coder | Hermes JSON | `hermes` | `qwen25` | none |
| DeepSeek-V3 / V3.1 | own format with markers | `deepseek_v3` (V3.1: `deepseek_v31`) | `deepseekv3` | `deepseek_r1` / `deepseek-r1` |
| DeepSeek-R1 | same as V3 | `deepseek_v3` | `deepseekv3` | `deepseek_r1` / `deepseek-r1` |
| GLM-4.5 / 4.6 | XML-like | `glm45` | `glm45` | `glm45` / `glm45` |
| Llama 3.1 / 3.3 | JSON in text | `llama3_json` | `llama3` | none |
| Llama 4 | pythonic | `llama4_pythonic` | `pythonic` | none |
| Mistral / Mixtral / Devstral | `[TOOL_CALLS]` | `mistral` (plus `--tokenizer-mode mistral`) | `mistral` | none |
| gpt-oss | Harmony | `openai` (together with `--reasoning-parser openai_gptoss`) | built in, parser `gpt-oss` | `openai_gptoss` / `gpt-oss` |
| Hermes / NousResearch | Hermes JSON | `hermes` | `hermes` | none |
| Gemma 3 | JSON in text | no built-in parser; via a template with tools | `gemma` | none |
| Kimi K2 | own | `kimi_k2` | `kimi_k2` | none |

Signs of the wrong parser in a response: `content` contains `<tool_call>`, `<function=`, `[TOOL_CALLS]`, `<|python_tag|>`; `finish_reason` is `stop` instead of `tool_calls`; `arguments` arrive as a string with escaped quotes inside the JSON.

## Checking the template without a client

vLLM: `POST /tokenize` with `messages` and `tools` returns the tokens of the assembled prompt; `"return_token_strs": true` shows whether the tools made it into the prompt. SGLang: `GET /get_server_info` shows the active template and parser.

Signs of a template without tool support: the prompt contains no function descriptions; HTTP 400 mentioning `tool` or `tool_calls` on a history with the tool role; the model answers in prose with "I would call the function".
