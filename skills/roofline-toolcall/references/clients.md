# Connecting clients to a local endpoint

Server base URL: `http://<host>:<port>` without `/v1` in `INFER_URL`; clients get `http://<host>:<port>/v1`.

## Qwen Code

Speaks the OpenAI protocol directly.

```bash
export OPENAI_BASE_URL=http://gpu-host:8000/v1
export OPENAI_API_KEY=local-token        # any non-empty value if the server runs without --api-key
export OPENAI_MODEL=qwen3-coder-30b      # --served-model-name
```

Needs from the server: streamed `tool_calls` with `index` and `id`, `tool_choice: auto`, context of 64k or more. Check: `task smoke-toolcall`, then the task "read the file and fix the function".

## Claude Code

Speaks the Anthropic Messages API. Needs a proxy that translates Messages to Chat Completions and back: `tool_use` to `tool_calls`, `tool_result` to `role: tool`, streaming events. Options: claude-code-router, LiteLLM proxy. The proxy lives inside the same network perimeter.

```bash
export ANTHROPIC_BASE_URL=http://proxy-host:3456
export ANTHROPIC_AUTH_TOKEN=local-token
export ANTHROPIC_MODEL=qwen3-coder-30b   # the name the proxy maps to served-model-name
```

Needs from the server and the proxy: an `id` on every streamed tool call (Claude Code matches `tool_result` by id), parallel calls preferred, context of 128k or more (the Claude Code system prompt and history take tens of thousands of tokens), a stable prefix for the prefix cache. Reasoning models: the proxy must handle `reasoning_content`, otherwise disable thinking.

Typical breakages: the proxy drops `tool_calls` without an `id`; the proxy does not pass `max_tokens` and gets truncated responses; a model with a 32k context fails with 400 `maximum context length` on the first large request.

## Proxy and load balancer

- One served-model-name for both replicas; the client knows nothing about replicas
- Prefix routing (hash of the system prompt or session id pinned to one replica): without it the prefix cache hit rate halves with two replicas
- Proxy timeout above `e2e p99` from `task bench`, otherwise the proxy cuts long responses
- Access token on the server (`--api-key`) and in the proxy; the endpoint is not exposed outside the perimeter

## What to check after connecting

1. `task smoke-toolcall` against the endpoint the client sees (through the proxy, if there is one)
2. In the client: read a file, make an edit, run a command; all three steps must pass without "the model answered with text"
3. `task metrics`: prefix cache hit above 50% after a couple of requests from the client; lower means the template or the proxy changes the system prompt between requests
