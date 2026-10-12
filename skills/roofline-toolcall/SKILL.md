---
name: roofline-toolcall
description: "Configure tool calling and the chat template on vLLM/SGLang for Claude Code, Qwen Code and OpenAI-compatible proxies: pick --tool-call-parser and --reasoning-parser by model family, verify the template, stream tool_calls, run task smoke-toolcall. Use when tool calls come back as plain text, arguments are not valid JSON, a client ignores or breaks on tools, the server returns 400 on role tool messages, thinking tags leak into content, or when connecting Claude Code, Qwen Code or a proxy to a local model."
license: MIT
---

# Tool calling and chat templates

Every `task` below means `task -t ${CLAUDE_SKILL_DIR}/../roofline-toolbox/Taskfile.yml <task>`, or include that Taskfile in your project Taskfile and run `task infer:<task>`. `INFER_URL` and `INFER_PROFILE` come from the environment, from arguments (`task serve INFER_PROFILE=x`) or from `inference.env` in the current directory.

The model emits a tool call as text in its own format (Hermes JSON inside `<tool_call>`, XML for Qwen3-Coder, `[TOOL_CALLS]` for Mistral). The engine's parser turns that text into OpenAI `tool_calls`. The format is dictated by the chat template in `tokenizer_config.json`: it must match the format the model was trained on (Burkov, pp. 164-170, ChatML and roles), otherwise no parser will help.

## Procedure

1. Model family: `config.json` (`architectures`, `model_type`) and the README of the weights
2. The template supports tools: the `chat_template` field in `tokenizer_config.json` mentions `tools`; if it does not, take the template from the model repo or the engine (`--chat-template`), do not write your own
3. Parsers from the table in [references/parsers.md](references/parsers.md); confirm the name: `task flags Q=tool-call-parser`. After an engine upgrade `task doctor` checks every name in the table against the installed version
4. Into the profile: vLLM `--enable-auto-tool-choice --tool-call-parser <p> [--reasoning-parser <r>]`; SGLang `--tool-call-parser <p> [--reasoning-parser <r>]`
5. `task serve`, then `task smoke-toolcall`: non-stream, stream, negative test, round trip with the tool role, parallel calls
6. Connect the client per [references/clients.md](references/clients.md) and run a real task (read a file, make an edit)

## What smoke-toolcall checks and how to read a FAIL

| FAIL | Cause | Action |
|---|---|---|
| `nonstream`: the tool call came back as text (`<tool_call>`, `<function=`) | parser not enabled, or the wrong one | flags from step 4, parser by family |
| `nonstream`: the model answered in prose without a call | template without tools, or a quantized model lost the skill | template from the repo; compare with the FP8/bf16 version |
| `stream` fails while `nonstream` works | the streaming parser in this engine version is broken for the model | upgrade the engine; temporarily `stream: false` in the proxy |
| `arguments are not valid JSON` | 4-bit quantization or a parser from another family | FP8 instead of AWQ/GPTQ; parser from the table |
| `roundtrip`: HTTP 400 | the template rejects `role: tool` or `tool_calls` in assistant | a template that supports tool history |
| `negative`: a call where none was needed | `tool_choice: required` in the proxy, or a weak model | `tool_choice: auto`; another model |
| `parallel`: one call for two cities (INFO) | the model or parser has no parallel calls | not a blocker; sequential calls are enough for clients |

## Reasoning models

Thinking models (Qwen3, DeepSeek-R1, GLM-4.5) write `<think>` before the answer. Without `--reasoning-parser` the reasoning lands in `content`, the client shows it to the user, and a tool call after `</think>` can get lost. With the parser the reasoning goes to `reasoning_content`. Disable thinking per request: `chat_template_kwargs: {"enable_thinking": false}` (Qwen3). For coding agents the non-thinking mode usually wins: lower TTFT and cost.

## Quantization and call quality

Tool calling is the first thing quantization breaks: arguments must be exact JSON. Order of preference: bf16, FP8 (Hopper and newer), then AWQ/GPTQ 4-bit only after `task smoke-toolcall` and your own task set. Details in the `roofline-perf` skill.

## Security

Tool results are external data: command injection through them (Burkov, pp. 201-202) is executed by the agent, not the model. The engine does not filter it; put the limits in the client and the proxy: a tool allowlist, confirmation for destructive actions.

## Sources

- [vLLM: tool calling](https://docs.vllm.ai/en/latest/features/tool_calling/), [vLLM: reasoning outputs](https://docs.vllm.ai/en/latest/features/reasoning_outputs/)
- [SGLang: tool parser](https://docs.sglang.ai/advanced_features/tool_parser.html)
- [Transformers: chat templates](https://huggingface.co/docs/transformers/chat_templating)
- [Qwen Code](https://github.com/QwenLM/qwen-code), [Claude Code: LLM gateway configuration](https://code.claude.com/docs/en/llm-gateway)
- roadmap.sh: [AI-Native Applications](https://roadmap.sh/inference-engineering/ai-native-applications@ZqFQmNizkU6ykTMCrmTWf), [Measuring Quality Impact](https://roadmap.sh/inference-engineering/measuring-quality-impact@mK_4R8liXtl64iG7ONvgz)
- Andriy Burkov, "The Hundred-Page Language Models Book" (page numbers refer to the Russian edition, BHV, 2026): ChatML and roles, pp. 164-170; jailbreak and prompt injection, pp. 201-202
