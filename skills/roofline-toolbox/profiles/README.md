# Launch profiles

One `<name>.env` file is one named way to start a runtime. `task serve INFER_PROFILE=<name>` accepts only files from this directory (or `PROFILES_DIR`), so no arbitrary server command runs through the toolbox.

| Variable | Meaning |
|---|---|
| `RUNTIME` | `vllm` or `sglang` |
| `MODEL` | local path with safetensors, `config.json`, tokenizer files |
| `SERVED_NAME` | model id in `/v1/models`; clients use this name |
| `HOST`, `PORT` | address of the OpenAI-compatible server |
| `TP` | tensor parallel: GPUs per replica |
| `MAX_MODEL_LEN` | context length; with `GPU_MEM_UTIL` it sets the KV cache budget (`task vram`) |
| `GPU_MEM_UTIL` | vLLM `--gpu-memory-utilization`, SGLang `--mem-fraction-static` |
| `EXTRA_ARGS` | tool-call and reasoning parsers, quantization, chunked prefill, speculation |
| `CUDA_VISIBLE_DEVICES` | GPUs given to this replica |
| `CMD` | full command instead of the assembled one, for example `docker run ...` |

Check flag names on the installed version: `task flags Q=tool-call`. Before promoting a profile: `task health && task smoke-toolcall && task bench`.
