# Подключение клиентов к локальному endpoint

Базовый URL сервера: `http://<host>:<port>` без `/v1` в `INFER_URL`; клиенты получают `http://<host>:<port>/v1`.

## Qwen Code

Говорит по OpenAI-протоколу напрямую.

```bash
export OPENAI_BASE_URL=http://gpu-host:8000/v1
export OPENAI_API_KEY=local-token        # любой непустой, если сервер без --api-key
export OPENAI_MODEL=qwen3-coder-30b      # --served-model-name
```

Нужно от сервера: стриминг `tool_calls` с `index` и `id`, `tool_choice: auto`, контекст от 64k. Проверка: `task smoke-toolcall`, затем задача "прочитай файл и исправь функцию".

## Claude Code

Говорит по Anthropic Messages API. Нужен прокси, который переводит Messages в Chat Completions и обратно: `tool_use` в `tool_calls`, `tool_result` в `role: tool`, стриминг событий. Варианты: claude-code-router, LiteLLM proxy. Прокси живёт в том же контуре.

```bash
export ANTHROPIC_BASE_URL=http://proxy-host:3456
export ANTHROPIC_AUTH_TOKEN=local-token
export ANTHROPIC_MODEL=qwen3-coder-30b   # имя, которое прокси отображает на served-model-name
```

Нужно от сервера и прокси: `id` в каждом стриминговом tool call (Claude Code сопоставляет `tool_result` по id), параллельные вызовы желательны, контекст от 128k (системный промпт Claude Code и история занимают десятки тысяч токенов), стабильный префикс для prefix cache. Reasoning-модели: прокси должен уметь `reasoning_content`, иначе отключить thinking.

Типичные поломки: прокси отбрасывает `tool_calls` без `id`; прокси не передаёт `max_tokens` и получает обрезанные ответы; модель с 32k контекстом падает с 400 `maximum context length` на первом же большом запросе.

## Прокси и балансировщик

- Один served-model-name на обе реплики; клиент не знает про реплики
- Маршрутизация по префиксу (hash системного промпта или session id на одну реплику): без неё hit rate prefix cache падает вдвое при двух репликах
- Таймаут прокси выше `e2e p99` из `task bench`, иначе прокси рвёт длинные ответы
- Токен доступа на сервере (`--api-key`) и в прокси; endpoint не торчит наружу контура

## Что проверить после подключения

1. `task smoke-toolcall` против endpoint, который видит клиент (через прокси, если он есть)
2. В клиенте: прочитать файл, сделать правку, запустить команду; все три шага должны пройти без "модель ответила текстом"
3. `task metrics`: prefix cache hit выше 50% после пары запросов из клиента; ниже: шаблон или прокси меняют системный промпт между запросами
