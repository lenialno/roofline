<p align="center"><img src="assets/lenialno.svg" alt="Lenialno" width="220"></p>

# Roofline

Roofline, a Lenialno product line. [По-русски](README.ru.md)

[![skills.sh](https://skills.sh/b/lenialno/roofline)](https://skills.sh/lenialno/roofline)

Agent Skills for the Inference Engineer role: on-prem LLM serving with vLLM or SGLang behind an OpenAI-compatible endpoint, clients such as Claude Code and Qwen Code through a proxy, air-gapped hosts. Six knowledge skills in English and in Russian (`-ru` suffix), one toolbox skill with a Taskfile and dependency-free scripts, one Claude Code subagent for incident investigation. The competency map follows [roadmap.sh/inference-engineering](https://roadmap.sh/inference-engineering); every skill lists its sources. No MCP servers and no hooks by design: live state comes from `task`.

## Skills

| Skill | Job |
|---|---|
| `roofline` | role router: what to do first, what is in and out of scope, which skill or task to use |
| `roofline-runtime` | start and keep vLLM or SGLang: engine choice, flag order, launch profiles, air-gap, startup failures |
| `roofline-toolcall` | tool calling and chat templates: parser per model family, streaming tool_calls, Claude Code and Qwen Code wiring |
| `roofline-perf` | metrics and SLO, VRAM and KV cache budget, batching, prefix cache, quantization with a quality protocol, speculative decoding, benchmarking |
| `roofline-incident` | runbook: triage sequence, OOM variants, queue, p95 breaches, regressions after upgrades, postmortem |
| `roofline-capacity` | sizing GPUs and TP, concurrency under SLO, replicas, canary rollout and rollback, cost |
| `roofline-toolbox` | Taskfile and scripts: gpu, health, models, metrics, serve, stop, bench, smoke-toolcall, vram, flags |

Russian versions: the same names with `-ru`. The toolbox is language-neutral and used by both.

## Install

As Agent Skills, for any agent that supports them (Claude Code, Codex, Cursor, OpenCode and others):

```bash
npx skills add lenialno/roofline --skill roofline-toolbox --skill roofline-runtime   # pick skills
npx skills add lenialno/roofline --all                                                 # everything, all agents
npx skills add lenialno/roofline -g -a claude-code --skill roofline-toolbox            # user scope, Claude Code only
```

As a Claude Code plugin, in every project on the machine, from the Lenialno catalog [lenialno/skills](https://github.com/lenialno/skills):

```bash
claude plugin marketplace add lenialno/skills
claude plugin install roofline@lenialno
```

Updates: `claude plugin marketplace update lenialno`, then `claude plugin update roofline@lenialno` and `/reload-plugins`. For one session from a local clone: `claude --plugin-dir /path/to/roofline`.

Requirements for the toolbox: python3 and curl; [go-task](https://taskfile.dev) for `task`; nvidia-smi for `gpu`. Scripts also run without task.

## Toolbox

From any project, `task -t /path/to/roofline/Taskfile.yml <task>` (the root Taskfile re-exports the toolbox without a namespace), or include it in the project Taskfile:

```yaml
version: '3'
includes:
  infer:
    taskfile: /path/to/roofline/skills/roofline-toolbox/Taskfile.yml
```

Commands run in the project directory, where `inference.env` (`KEY=value` lines) and `.inference-state/` live. Setting priority: task variable (`task serve INFER_PROFILE=x`), environment, `inference.env`, default. Variables: `INFER_URL` (no `/v1`), `INFER_API_KEY`, `INFER_PROFILE`, `INFER_STATE_DIR`, `SLO_TTFT_P95_MS`, `SLO_TPOT_P95_MS`, `BENCH_N`, `BENCH_C`, `BENCH_IN`, `BENCH_OUT`.

| Task | What it does |
|---|---|
| `gpu` | memory, utilization, processes from `nvidia-smi` |
| `health` | `/health`, `/v1/models`, one short completion with latency |
| `models` | served model ids and max context |
| `profiles` | list launch profiles in `profiles/` |
| `metrics` | queue, KV usage, prefix-cache hit rate, preemptions, p50/p95 TTFT and TPOT from `/metrics` |
| `status` | `gpu`, then `health`, then `models` |
| `serve INFER_PROFILE=<name>` | start from a profile in `profiles/`, wait for `/health`, pid and log in `.inference-state/` |
| `stop`, `restart`, `logs` | stop by pid, restart, tail the log (`LINES=200 FOLLOW=1`) |
| `bench` | fixed SLO benchmark: `BENCH_N`, `BENCH_C`, `BENCH_IN`, `BENCH_OUT`; `-- --json` for a JSON line; exit 1 when the SLO is missed |
| `smoke-toolcall` | tool-calling contract: non-stream, stream, negative prompt, round trip, parallel calls |
| `vram MODEL=/models/x` | VRAM and KV budget, concurrency; `GPU_GB`, `TP`, `CTX`, `KV_DTYPE=fp8` |
| `flags Q=<word>` | grep the installed engine's `--help` (`RUNTIME=vllm` or `sglang`) |

Profiles: [skills/roofline-toolbox/profiles/README.md](skills/roofline-toolbox/profiles/README.md).

## Subagent

`incident-investigator` is a Claude Code subagent used by `roofline-incident` when an investigation needs long logs or hours of metrics. It is read-only (`health`, `metrics`, `gpu`, `logs`, `smoke-toolcall`) and returns a 25-line verdict.

## Documents

- [docs/roadmap-ru/](docs/roadmap-ru/README.md): Russian translation of all 136 nodes of roadmap.sh/inference-engineering with links to the originals
- [skills/roofline/references/competency-map.md](skills/roofline/references/competency-map.md): which roadmap nodes are in the role and which skill covers them
- [skills/roofline/references/theory-from-burkov.md](skills/roofline/references/theory-from-burkov.md): serving-relevant facts from Andriy Burkov's "The Hundred-Page Language Models Book" (Russian edition, BHV 2026) with page numbers

## Sources and license

Primary sources: [roadmap.sh: Inference Engineering](https://roadmap.sh/inference-engineering), [vLLM docs](https://docs.vllm.ai/), [SGLang docs](https://docs.sglang.ai/), [Claude Code docs](https://code.claude.com/docs/en/skills), [Agent Skills specification](https://agentskills.io/specification), Andriy Burkov's book. Each skill ends with its own Sources section. MIT license, see [LICENSE](LICENSE).
