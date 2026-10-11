---
name: roofline-incident
description: "Incident runbook for LLM serving on vLLM/SGLang: endpoint not responding, CUDA OOM, queue growing, TTFT or TPOT p95 above SLO, preemptions, client timeouts, tool calls broken after an upgrade. Use when the server is down or degraded, requests time out, GPU memory is full, latency percentiles spiked, Claude Code or Qwen Code report errors, or to run the triage sequence task health, metrics, gpu, logs."
license: MIT
---

# Incident: triage order

Goal: within five minutes, locate the failure (server, memory, queue, parser, proxy) and pick the least destructive action. Restart comes last.

## Triage

```bash
task -t ${CLAUDE_SKILL_DIR}/../roofline-toolbox/Taskfile.yml health      # is the endpoint alive, does the model answer
task -t ${CLAUDE_SKILL_DIR}/../roofline-toolbox/Taskfile.yml metrics     # queue, KV, preemptions, p95
task -t ${CLAUDE_SKILL_DIR}/../roofline-toolbox/Taskfile.yml gpu         # memory, foreign processes, temperature
task -t ${CLAUDE_SKILL_DIR}/../roofline-toolbox/Taskfile.yml logs INFER_PROFILE=<name> LINES=200
```

Then work the table; the full symptom table is in [references/symptoms.md](references/symptoms.md).

| health | metrics | Diagnosis | Action |
|---|---|---|---|
| `/health` 000 | none | process dead or port closed | `task logs`: last error; `task gpu`: memory released; `task serve` |
| `/health` 200, completion FAIL | no response | engine hung (often after a CUDA error or an NCCL timeout under TP) | search the log for `CUDA error`, `NCCL`, `watchdog`; `task restart` |
| OK | `waiting` growing, KV above 90% | KV cache exhausted, requests are waiting | lower `max-model-len` or fp8 KV in the profile; throttle clients temporarily |
| OK | `waiting` growing, KV below 70% | capped by `max-num-seqs` or decode compute | raise `max-num-seqs` after `task bench`; second replica |
| OK | `preemptions` growing | KV overflows under load, recompute | same as for KV; a preemption doubles prefill |
| OK | TTFT p95 growing, hit rate dropped | clients send a new prefix, cache is not working | verify the system prompt and session-based routing |
| OK | TPOT p95 growing at the same traffic | neighbor process on the GPU, thermal or power throttling | `task gpu`: processes, temp, watts |
| OK, metrics OK | clients see errors | proxy, timeouts, parser | `task smoke-toolcall` against the proxy endpoint; proxy timeout versus e2e p99 |

## OOM: three different cases

| When | Sign | Cause | Action |
|---|---|---|---|
| at startup | `CUDA out of memory` before `/health` | weights do not fit under TP | `task vram`; TP, FP8, a different GPU |
| at startup | `max seq len ... larger than ... KV cache` | no KV left for a single request after the weights | lower `max-model-len`, raise utilization, fp8 KV |
| under load | OOM during prefill of a long prompt, engine crashes | utilization above 0.92 or chunked prefill disabled | utilization 0.88-0.90, enable `chunked prefill`, `max-num-batched-tokens` 8192 |

## After an upgrade

Broke after a change of engine version, model or template: `task smoke-toolcall` first. A parser or template regression is the most common cause of "the model got dumber" with no change in metrics. Rollback: `task stop` the new profile, `task serve` the old one (profiles are not deleted until they pass the gate).

## Operating rules

1. Capture `metrics` and `logs` into the ticket first, then touch the server: the data is gone after a restart
2. One action at a time; `task health` and `task metrics` after each one
3. `task restart` only when the process is dead, hung, or OOM under load; a restart does not fix a queue or a slow p95
4. Every profile change is recorded in the change log with its reason
5. Long log, hours of correlation, several hypotheses: hand off to the `incident-investigator` agent, it returns a verdict and the next step

## Postmortem

Template: [references/postmortem.md](references/postmortem.md). Fields: timeline, symptom, metrics before and after, root cause, what changed, what to add to `task bench` or smoke to catch it earlier.

## Sources

- [vLLM: metrics design](https://docs.vllm.ai/en/latest/design/metrics/), [vLLM: troubleshooting](https://docs.vllm.ai/en/latest/usage/troubleshooting/)
- [SGLang: production metrics](https://docs.sglang.ai/references/production_metrics.html)
- roadmap.sh: [Observability](https://roadmap.sh/inference-engineering/observability@w-dVv5dFNxD7Rqy16m4uL), [Request Queueing](https://roadmap.sh/inference-engineering/request-queueing@k-zXOGynI0B0yyT-n3raa), [Continuous Batching](https://roadmap.sh/inference-engineering/continuous-batching@h_PDOMA-V-n7Pab3epuP3), [Zero-Downtime Deployment](https://roadmap.sh/inference-engineering/zero-downtime-deplo@le4sPQ0h9l-vlmCB4G8ZY)
