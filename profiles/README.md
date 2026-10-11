# Профили запуска

Один файл `<name>.env` = один именованный способ поднять runtime. `task serve INFER_PROFILE=<name>` принимает только файлы из этой папки: произвольные команды через Taskfile не запускаются.

Переменные:

| Переменная | Значение |
|---|---|
| `RUNTIME` | `vllm` или `sglang` |
| `MODEL` | локальный путь к весам (safetensors + config.json + tokenizer) |
| `SERVED_NAME` | id модели в `/v1/models`; клиенты обращаются по нему |
| `HOST`, `PORT` | адрес OpenAI-совместимого сервера |
| `TP` | tensor parallel: число GPU на одну реплику |
| `MAX_MODEL_LEN` | контекст; вместе с `GPU_MEM_UTIL` задаёт бюджет KV-кеша (`task vram`) |
| `GPU_MEM_UTIL` | vLLM `--gpu-memory-utilization`, SGLang `--mem-fraction-static` |
| `EXTRA_ARGS` | парсеры tool-call и reasoning, квантование, chunked prefill, спекуляция |
| `CUDA_VISIBLE_DEVICES` | какие GPU отдать реплике |
| `CMD` | полная команда вместо сборки по полям, например `docker run ...` |

Имена флагов проверяйте на установленной версии: `task flags Q=tool-call`. Перед выкаткой профиля: `task health && task smoke-toolcall && task bench`.
