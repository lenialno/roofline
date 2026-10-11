# Симптомы: расширенная таблица

| Симптом | Где видно | Вероятная причина | Проверка | Действие |
|---|---|---|---|---|
| `Connection refused` | health | процесс не запущен | `task logs`, `ps` | `task serve` |
| `/health` 200, `/v1/models` пусто | health | движок стартует, модель ещё грузится | лог на `Loading`, прогресс | подождать `SERVE_TIMEOUT` |
| Ответы по 30-60 с на короткий промпт сразу после старта | bench | прогрев cudagraph, компиляция | повтор через 2 минуты | ничего |
| `maximum context length` 400 у клиента | лог клиента | промпт длиннее `max-model-len` | `task models` (max_len) | поднять контекст по `task vram` или урезать историю в клиенте |
| `tool_calls` отсутствуют, в `content` есть `<tool_call>` | smoke | парсер не включён | `task flags Q=tool-call` | профиль: парсер по семейству |
| HTTP 400 на сообщение с `role: tool` | smoke roundtrip | шаблон без поддержки истории инструментов | tokenizer_config chat_template | шаблон из репозитория модели |
| `reasoning_content` пустой, `<think>` в `content` | ответ API | нет reasoning parser | флаги | `--reasoning-parser` |
| `waiting` растёт, `running` на потолке | metrics | `max-num-seqs` | профиль | бенч и поднять лимит |
| `kv_cache_usage` 95-100%, `preemptions` растут | metrics | длинные контексты, KV мал | `task vram` | fp8 KV, ниже `max-model-len`, реплика |
| TPOT p95 вырос без роста трафика | metrics, gpu | другой процесс на GPU, троттлинг | `task gpu` (procs, temp, watts) | убрать соседа, охлаждение, power limit |
| TTFT p95 вырос, hit rate упал | metrics | изменился системный промпт или прокси перемешивает реплики | сравнить промпты | стабильный префикс, маршрутизация по сессии |
| NCCL timeout / `watchdog` в логе при TP больше 1 | лог | зависший worker, проблема NVLink | `nvidia-smi topo -m` | `task restart`; проверить topology и `NCCL_P2P` |
| `CUDA error: an illegal memory access` | лог | баг ядра для этой модели или версии | версия движка | откат версии движка, issue upstream |
| Качество ответов упало без изменений метрик | клиенты | обновлён шаблон, квантование или парсер | `task smoke-toolcall`, PPL | откат профиля |
| Клиент рвёт длинные ответы | клиенты | таймаут прокси ниже e2e p99 | `task bench` e2e | поднять таймаут прокси |
| Параллельный `task serve` второго профиля падает | serve | порт занят | `task stop`, `task gpu` | другой порт или остановить старый |
