<picture>
  <source media="(prefers-color-scheme: dark)" srcset="brand/png/readme-header-dark-1200x400-2x.png">
  <img alt="roofline" src="brand/png/readme-header-light-1200x400-2x.png" width="1200">
</picture>

<img src="assets/lenialno-icon.svg" alt="Lenialno" height="22" align="top"> Roofline, a Lenialno product line. [По-русски](README.ru.md)

<!-- skills.sh badge: https://skills.sh/b/lenialno/roofline, add once the page exists -->

Agent Skills for the Inference Engineer role: run vLLM or SGLang on your own GPUs behind an OpenAI-compatible endpoint, serve Claude Code and Qwen Code through a proxy, stay healthy on air-gapped hosts. 13 skills, one Claude Code subagent and a Taskfile toolbox; the competency map follows [roadmap.sh/inference-engineering](https://roadmap.sh/inference-engineering).

## Quick start

As Agent Skills, for any agent that supports them (Claude Code, Codex, Cursor, OpenCode and others):

```bash
npx skills add lenialno/roofline --list                                      # see what is inside
npx skills add lenialno/roofline --skill roofline --skill roofline-toolbox   # pick skills
npx skills add lenialno/roofline --all                                       # everything, all agents
npx skills add lenialno/roofline -g -a claude-code --skill roofline-toolbox  # user scope, Claude Code only
```

As a Claude Code plugin, available in every project on the machine, from the Lenialno catalog [lenialno/skills](https://github.com/lenialno/skills):

```bash
claude plugin marketplace add lenialno/skills
claude plugin install roofline@lenialno
```

> [!TIP]
> Update with `claude plugin marketplace update lenialno`, then `claude plugin update roofline@lenialno` and `/reload-plugins`. To try a local clone for one session: `claude --plugin-dir /path/to/roofline`.

Then ask the agent what to do first with your local LLM server. The `roofline` skill routes the question to the right skill, task or subagent.

The toolbox needs python3 and curl, [go-task](https://taskfile.dev) for `task`, and nvidia-smi for the `gpu` task. The scripts also run without task.

## Skills

| Skill | Covers | Ask it when |
|---|---|---|
| `roofline` | role router: first steps, what is in and out of the role, which skill, task or agent to use | "where do I start", "is this my job", "which skill handles this" |
| `roofline-runtime` | bring up vLLM or SGLang and keep it healthy: engine choice, flag order, launch profiles, air-gap, docker | "start or stop the server", "vLLM or SGLang", "set TP or max-model-len", "it fails to start" |
| `roofline-toolcall` | tool calling and chat template: parsers by model family, streaming `tool_calls`, Claude Code and Qwen Code wiring | "tool calls come back as text", "arguments are not valid JSON", "400 on role tool" |
| `roofline-perf` | VRAM and KV cache budget, batching, prefix cache, quantization and its cost, speculative decoding, benchmark method | "why is it slow", "more throughput", "which quantization", "how to read a benchmark" |
| `roofline-incident` | runbook: triage `health`, `metrics`, `gpu`, `logs`; OOM variants, queue, p95 breaches, regressions after upgrades, postmortem | "server is down", "GPU memory is full", "p95 spiked", "Claude Code reports errors" |
| `roofline-capacity` | GPU, VRAM and TP sizing, concurrency under SLO, replicas, model choice by evals, canary and rollback, cost | "how many GPUs", "which model fits", "how many concurrent users", "roll out safely" |
| `roofline-toolbox` | Taskfile and dependency-free scripts the other skills call | "check, start, stop, benchmark or probe the server", or another skill says to run a task |

Agents pick a skill by its description, so phrases like the ones in the last column are enough. The first six also ship in Russian under the same name with a `-ru` suffix: `roofline-ru`, `roofline-runtime-ru`, `roofline-toolcall-ru`, `roofline-perf-ru`, `roofline-incident-ru`, `roofline-capacity-ru`. The toolbox is language-neutral and shared by both sets.

> [!NOTE]
> No MCP servers and no hooks, by design. Live state comes from `task`: the agent reads GPU memory, health, metrics and logs from the real server instead of guessing.

## Subagent

`incident-investigator` ([agents/incident-investigator.md](agents/incident-investigator.md)) is a Claude Code subagent that `roofline-incident` hands an investigation to when it needs long logs or hours of metrics. It only reads and measures (`health`, `metrics`, `gpu`, `models`, `logs`, `smoke-toolcall`), never runs `serve`, `stop` or `restart`, and returns a verdict of at most 25 lines: cause, evidence, rejected hypotheses, next action.

## Toolbox

A Taskfile plus dependency-free bash and python3 scripts in [skills/roofline-toolbox/](skills/roofline-toolbox/SKILL.md); the root `Taskfile.yml` re-exports it without a namespace. Every task is idempotent and exits non-zero on failure. From any project:

```bash
task -t /path/to/roofline/Taskfile.yml health
```

Or include it in the project Taskfile and call `task infer:health`:

```yaml
version: '3'
includes:
  infer:
    taskfile: /path/to/roofline/skills/roofline-toolbox/Taskfile.yml
```

Commands run in the directory you call `task` from, where `inference.env` (`KEY=value` lines) and `.inference-state/` live. `task` with no arguments prints the task list under the Roofline mark.

> [!NOTE]
> `task serve` starts only a named profile from `profiles/` (or `PROFILES_DIR`). Before promoting a profile: `task health && task smoke-toolcall && task bench`.

<details>
<summary>Tasks</summary>

| Task | What it does |
|---|---|
| `gpu` | memory, utilization, processes from `nvidia-smi` |
| `health` | `/health`, `/v1/models`, one short completion with latency |
| `models` | served model ids and max context from `/v1/models` |
| `profiles` | list launch profiles in `profiles/` |
| `metrics` | queue, KV usage, prefix-cache hit rate, preemptions, p50/p95 TTFT and TPOT from `/metrics` |
| `status` | `gpu`, then `health`, then `models` |
| `serve INFER_PROFILE=<name>` | start from a profile, wait for `/health`, pid and log in `.inference-state/` |
| `stop`, `restart`, `logs` | stop by pid (no profile means all), stop then serve, tail the log (`LINES=200 FOLLOW=1`) |
| `bench` | fixed SLO benchmark: `BENCH_N`, `BENCH_C`, `BENCH_IN`, `BENCH_OUT`; `-- --json` for a JSON line; exit 1 when the SLO is missed |
| `smoke-toolcall` | tool-calling contract: non-stream, stream, negative prompt, round trip, parallel calls |
| `vram MODEL=/models/x` | VRAM and KV budget, concurrency from `config.json`; `GPU_GB`, `TP`, `CTX`, `KV_DTYPE=fp8` |
| `flags Q=<word>` | grep the installed engine's `--help` (`RUNTIME=vllm` or `sglang`) |

Profiles and their variables: [skills/roofline-toolbox/profiles/README.md](skills/roofline-toolbox/profiles/README.md).

</details>

<details>
<summary>Settings</summary>

Priority, highest first: task variable (`task serve INFER_PROFILE=x`), environment, `inference.env` in the current directory, built-in default.

| Variable | Meaning | Default |
|---|---|---|
| `INFER_URL` | OpenAI-compatible base URL, no `/v1` | `http://127.0.0.1:8000` |
| `INFER_API_KEY` | bearer token if the server needs one | empty |
| `INFER_PROFILE` | profile name from `profiles/` for `serve`, `stop`, `logs` | none |
| `INFER_STATE_DIR` | pid files and logs | `./.inference-state` |
| `SLO_TTFT_P95_MS` | bench gate, p95 time to first token | `2000` |
| `SLO_TPOT_P95_MS` | bench gate, p95 time per output token | `60` |
| `BENCH_N`, `BENCH_C`, `BENCH_IN`, `BENCH_OUT` | bench shape: requests, concurrency, input and output tokens | `32`, `8`, `2048`, `256` |

</details>

## Documents

- [docs/roadmap-ru/](docs/roadmap-ru/README.md): Russian translation of all 136 nodes of roadmap.sh/inference-engineering with links to the originals. One deliberate deviation: the node Writing Custom Kernels is adapted to Rust (cudarc, CubeCL, Rust-CUDA) instead of C++ and Triton, and the competency map follows the same choice.
- [skills/roofline/references/competency-map.md](skills/roofline/references/competency-map.md): which roadmap nodes are in the role and which skill covers them.
- [skills/roofline/references/theory-from-burkov.md](skills/roofline/references/theory-from-burkov.md): serving-relevant facts from Andriy Burkov's "The Hundred-Page Language Models Book" with page numbers.

## Sources

[roadmap.sh: Inference Engineering](https://roadmap.sh/inference-engineering), [vLLM docs](https://docs.vllm.ai/), [SGLang docs](https://docs.sglang.ai/), [Claude Code docs](https://code.claude.com/docs/en/skills), [Agent Skills specification](https://agentskills.io/specification), Andriy Burkov's book. Each skill ends with its own Sources section. Brand files with the colour and geometry rules: [brand/BRAND.md](brand/BRAND.md); terminal mark in [brand/ascii.txt](brand/ascii.txt). MIT license, see [LICENSE](LICENSE).
