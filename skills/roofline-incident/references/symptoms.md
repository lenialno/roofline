# Symptoms: extended table

| Symptom | Where seen | Likely cause | Check | Action |
|---|---|---|---|---|
| `Connection refused` | health | process not running | `task logs`, `ps` | `task serve` |
| `/health` 200, `/v1/models` empty | health | engine starting, model still loading | log for `Loading`, progress | wait for `SERVE_TIMEOUT` |
| 30-60 s responses to a short prompt right after startup | bench | cudagraph warmup, compilation | retry after 2 minutes | nothing |
| `maximum context length` 400 on the client | client log | prompt longer than `max-model-len` | `task models` (max_len) | raise the context per `task vram` or trim history in the client |
| `tool_calls` missing, `<tool_call>` present in `content` | smoke | parser not enabled | `task flags Q=tool-call` | profile: parser by model family |
| HTTP 400 on a message with `role: tool` | smoke roundtrip | template does not support tool history | tokenizer_config chat_template | template from the model repository |
| `reasoning_content` empty, `<think>` in `content` | API response | no reasoning parser | flags | `--reasoning-parser` |
| `waiting` growing, `running` at the ceiling | metrics | `max-num-seqs` | profile | bench and raise the limit |
| `kv_cache_usage` 95-100%, `preemptions` growing | metrics | long contexts, KV too small | `task vram` | fp8 KV, lower `max-model-len`, replica |
| TPOT p95 up without traffic growth | metrics, gpu | another process on the GPU, throttling | `task gpu` (procs, temp, watts) | remove the neighbor, cooling, power limit |
| TTFT p95 up, hit rate dropped | metrics | system prompt changed or the proxy shuffles replicas | compare prompts | stable prefix, session-based routing |
| NCCL timeout / `watchdog` in the log at TP above 1 | log | hung worker, NVLink problem | `nvidia-smi topo -m` | `task restart`; check topology and `NCCL_P2P` |
| `CUDA error: an illegal memory access` | log | kernel bug for this model or version | engine version | roll back the engine version, upstream issue |
| Answer quality dropped with no change in metrics | clients | template, quantization or parser was updated | `task smoke-toolcall`, PPL | roll back the profile |
| Client cuts off long responses | clients | proxy timeout below e2e p99 | `task bench` e2e | raise the proxy timeout |
| Parallel `task serve` of a second profile fails | serve | port in use | `task stop`, `task gpu` | different port or stop the old one |
