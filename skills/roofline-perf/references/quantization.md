# Quantization: choosing and verifying

## What to pick

1. An official FP8 release of the model exists (or Hopper/Blackwell and a bf16 checkpoint): FP8. Half the memory, faster decode, near-lossless quality, tool calling survives
2. The model does not fit even in FP8: AWQ or GPTQ 4-bit (in vLLM via `compressed-tensors`, AWQ, GPTQ-Marlin). Checking tool calling is mandatory
3. KV cache in fp8, independent of the weights: doubles the number of requests held in KV at the same memory; quality loss is small but must be checked on long context
4. QAT models (for example gpt-oss in MXFP4) are already calibrated, do not requantize them
5. Your own PTQ calibration (NVIDIA ModelOpt, llm-compressor): calibration set built from your own prompts (code, tools), not from generic datasets

## Acceptance protocol

| Step | Criterion |
|---|---|
| Perplexity on 50-100 of your own documents, one tokenization | rise of at most 1-2% against bf16 |
| `task smoke-toolcall` | PASS, including stream and roundtrip |
| Agent task set (20-50 real tasks: read, fix, run) | success rate no lower than bf16 minus 2 pp |
| `task bench` at working concurrency | TPOT p95 lower than bf16; TTFT no worse |
| Long context (fp8 KV) | answer to a question over a 50k document matches bf16 |

Signs of quantization degradation: JSON with extra commas or quotes in arguments, repeated tokens, a tool call with parameters mixed up, an empty answer after `</think>`.

## Why tool calling suffers first

Tool arguments must be exact JSON: one wrong token breaks the whole call, whereas in prose the same error goes unnoticed. 4-bit weights shift the distribution on rare tokens (brackets, quotes, parameter names). Perplexity may rise only slightly while the share of valid calls drops noticeably, so smoke and agent tasks are mandatory and perplexity alone is not enough.
