# Соответствие флагов vLLM и SGLang

Имена меняются между версиями. Перед использованием: `task flags Q=<фрагмент>` (RUNTIME=vllm|sglang). Таблица собрана по документации vLLM 0.10-0.11 и SGLang 0.4-0.5.

| Что настраиваем | vLLM (`vllm serve MODEL ...`) | SGLang (`python -m sglang.launch_server --model-path MODEL ...`) |
|---|---|---|
| Адрес | `--host --port` | `--host --port` |
| Имя модели в API | `--served-model-name` | `--served-model-name` |
| Tensor parallel | `--tensor-parallel-size N` | `--tp N` |
| Pipeline parallel | `--pipeline-parallel-size N` | `--pp N` |
| Expert parallel (MoE) | `--enable-expert-parallel` | `--ep N` |
| Контекст | `--max-model-len` | `--context-length` |
| Доля памяти GPU | `--gpu-memory-utilization 0.9` | `--mem-fraction-static 0.9` |
| Параллельных запросов | `--max-num-seqs` | `--max-running-requests` |
| Токенов в одном шаге батча | `--max-num-batched-tokens` | `--chunked-prefill-size` (и `--max-prefill-tokens`) |
| Chunked prefill | `--enable-chunked-prefill` (по умолчанию включён в V1) | `--chunked-prefill-size N` (`-1` выключает) |
| Prefix cache | `--enable-prefix-caching` / `--no-enable-prefix-caching` | включён; `--disable-radix-cache` выключает |
| Квантование весов | `--quantization fp8\|awq\|gptq\|compressed-tensors` (часто определяется из config) | `--quantization fp8\|awq\|gptq\|...` |
| KV в FP8 | `--kv-cache-dtype fp8` | `--kv-cache-dtype fp8_e5m2\|fp8_e4m3` |
| Tool calling | `--enable-auto-tool-choice --tool-call-parser <name>` | `--tool-call-parser <name>` |
| Reasoning (thinking) | `--reasoning-parser <name>` | `--reasoning-parser <name>` |
| Свой chat template | `--chat-template path.jinja` | `--chat-template path.jinja\|name` |
| Спекуляция | `--speculative-config '{"method":"ngram","num_speculative_tokens":4,"prompt_lookup_max":4}'` или `{"method":"eagle3","model":...}` | `--speculative-algorithm EAGLE3 --speculative-draft-model-path ... --speculative-num-steps --speculative-eagle-topk --speculative-num-draft-tokens` |
| LoRA | `--enable-lora --lora-modules name=path` | `--lora-paths name=path` |
| Метрики | `/metrics` включён | `--enable-metrics` |
| Логи запросов | `--disable-log-requests` для тишины | `--log-requests` для подробностей |
| Токен доступа | `--api-key` | `--api-key` |
| Телеметрия | `VLLM_NO_USAGE_STATS=1` | не отправляет |

Полезные endpoint'ы: `/health`, `/v1/models`, `/metrics`, `/tokenize` (vLLM) для проверки, как шаблон собирает промпт; SGLang: `/get_server_info`, `/health_generate`.
