---
name: roofline
description: "Router for the Inference Engineer role on on-prem LLM serving (vLLM/SGLang, OpenAI-compatible endpoint, air-gap). Use when the user asks what to do first with a local LLM server, how to approach a serving task, which skill, task or agent to use, what is inside or outside the inference engineer role, or talks about LLM serving, GPU inference, inference engineering in general terms."
license: MIT
---

# Inference Engineer: where to start

The role as roadmap.sh defines it: make the model answer fast, cheaply and predictably in production. The stack in this package: on-prem GPU, vLLM or SGLang, an OpenAI-compatible endpoint, Claude Code and Qwen Code clients through a proxy. Code and weights never leave the perimeter.

## First five minutes

```bash
task -t ${CLAUDE_SKILL_DIR}/../roofline-toolbox/Taskfile.yml status     # gpu + health + models
task -t ${CLAUDE_SKILL_DIR}/../roofline-toolbox/Taskfile.yml metrics    # queue, KV, prefix cache, p95
```

No server yet: skill `roofline-runtime`. The server exists but does not respond or has degraded: `roofline-incident`. Everything works and you need it faster: `roofline-perf`.

## Where to go for each request

| Request | Handled by |
|---|---|
| bring up, restart, choose vLLM or SGLang, write a profile | skill `roofline-runtime`, `task serve/stop/logs/flags` |
| tool calls arrive as plain text, parser, chat template, connect Claude Code or Qwen Code | skill `roofline-toolcall`, `task smoke-toolcall` |
| slow, OOM under load, quantization, KV, batching, bench | skill `roofline-perf`, `task bench/vram/metrics` |
| server is down, queue, p95 above SLO, broke after an upgrade | skill `roofline-incident`, then the `incident-investigator` agent for a long log review |
| how many GPUs, how many users, rollout and rollback plan | skill `roofline-capacity`, `task vram` |
| what the GPU can do right now, which models are up | `task gpu`, `task models` |

The `incident-investigator` agent is only for investigations that need long log reads or metric comparisons over hours: it runs in its own context and returns a digest.

## Role boundaries

In scope: serving, runtime flags, KV cache and batching, quantization with quality checks, SLOs and metrics, GPU memory and TP, observability, capacity, rollout. Full map across the 136 roadmap nodes: [references/competency-map.md](references/competency-map.md).

Out of scope: training and research, fine-tuning and distillation as the main job (we know when to order them), cloud serving (GKE, SageMaker, HF Endpoints), custom CUDA kernels, image/video/speech pipelines, NVIDIA Dynamo and prefill/decode disaggregation (needed for a multi-node cluster, not for one or two servers).

## Working rules

- Measure first, then change: `task metrics` and `task bench` before and after, one variable at a time
- Take flags from the installed version: `task flags Q=<word>`, not from memory
- After any configuration change: `task health`, `task smoke-toolcall`, `task bench`
- Launch profiles come only from `profiles/`; the Taskfile does not run arbitrary server commands
- No SLO or load data: ask, do not guess

Theory the other skills rely on (KV cache, sampling, chat format, perplexity), with page numbers from Andriy Burkov, "The Hundred-Page Language Models Book" (page numbers refer to the Russian edition, BHV, 2026): [references/theory-from-burkov.md](references/theory-from-burkov.md).

## Sources

- [roadmap.sh: Inference Engineering](https://roadmap.sh/inference-engineering): the role map; every node translated in `docs/roadmap-ru/`
- [Claude Code: skills](https://code.claude.com/docs/en/skills), [plugins](https://code.claude.com/docs/en/plugins): package format
- [Agent Skills specification](https://agentskills.io/specification): SKILL.md format
- Andriy Burkov, "The Hundred-Page Language Models Book" (Russian edition: BHV-Petersburg, 2026, [buy on Ozon](https://www.ozon.ru/product/yazykovye-modeli-bez-lishnih-slov-burkov-andrey-4678629427/?at=1iao1Xu0NlUIcfcFRZUKWGxeT6SFLpfc&sh=YcvAR88O_Q)): theory in [references/theory-from-burkov.md](references/theory-from-burkov.md)
