# vLLM and SGLang flag mapping

Names change between versions. Before use: `task flags Q=<fragment>` (RUNTIME=vllm|sglang). The table follows the vLLM 0.10-0.11 and SGLang 0.4-0.5 documentation.

| Setting | vLLM (`vllm serve MODEL ...`) | SGLang (`python -m sglang.launch_server --model-path MODEL ...`) |
|---|---|---|
| Bind address | `--host --port` | `--host --port` |
| Model name in the API | `--served-model-name` | `--served-model-name` |
| Tensor parallel | `--tensor-parallel-size N` | `--tp N` |
| Pipeline parallel | `--pipeline-parallel-size N` | `--pp N` |
| Expert parallel (MoE) | `--enable-expert-parallel` | `--ep N` |
| Context | `--max-model-len` | `--context-length` |
| GPU memory share | `--gpu-memory-utilization 0.9` | `--mem-fraction-static 0.9` |
| Concurrent requests | `--max-num-seqs` | `--max-running-requests` |
| Tokens per batch step | `--max-num-batched-tokens` | `--chunked-prefill-size` (and `--max-prefill-tokens`) |
| Chunked prefill | `--enable-chunked-prefill` (on by default in V1) | `--chunked-prefill-size N` (`-1` disables) |
| Prefix cache | `--enable-prefix-caching` / `--no-enable-prefix-caching` | on; `--disable-radix-cache` turns it off |
| Weight quantization | `--quantization fp8\|awq\|gptq\|compressed-tensors` (often detected from config; since vLLM 0.31 online quantization via `fp8` redirects to `fp8_per_tensor`) | `--quantization fp8\|awq\|gptq\|...` |
| KV in FP8 | `--kv-cache-dtype fp8` | `--kv-cache-dtype fp8_e5m2\|fp8_e4m3` |
| Tool calling | `--enable-auto-tool-choice --tool-call-parser <name>` | `--tool-call-parser <name>` |
| Reasoning (thinking) | `--reasoning-parser <name>` | `--reasoning-parser <name>` |
| Custom chat template | `--chat-template path.jinja` | `--chat-template path.jinja\|name` |
| Speculation | `--speculative-config '{"method":"ngram","num_speculative_tokens":4,"prompt_lookup_max":4}'` or `{"method":"eagle3","model":...}` | `--speculative-algorithm EAGLE3 --speculative-draft-model-path ... --speculative-num-steps --speculative-eagle-topk --speculative-num-draft-tokens` |
| LoRA | `--enable-lora --lora-modules name=path` | `--lora-paths name=path` |
| Metrics | `/metrics` on | `--enable-metrics` |
| Request logs | `--disable-log-requests` to silence | `--log-requests` for detail |
| Access token | `--api-key` | `--api-key` |
| Telemetry | `VLLM_NO_USAGE_STATS=1` | does not send |

Useful endpoints: `/health`, `/v1/models`, `/metrics`, `/tokenize` (vLLM) to check how the template assembles the prompt; SGLang: `/get_server_info`, `/health_generate`.
