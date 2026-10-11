# Bench protocol

## Before a run

- Server is warm: 1-2 minutes of requests or a single `task bench BENCH_N=8`
- Nobody else is loading the GPU: `task gpu`
- Recorded: engine version, profile, GPU, driver, `task metrics` before the run

## Matrix

| Variable | Fixed | Runs |
|---|---|---|
| concurrency | model, flags | C = 1, 4, 8, 16, 32 at IN=2048, OUT=256 |
| prompt length | C = 8 | IN = 512, 2048, 8192, 32768 |
| quantization | C = 8, IN = 2048 | bf16, FP8, FP8 + fp8 KV, AWQ |
| TP | C = 8 | TP = 1, 2, 4 with the same model |
| speculation | C = 1, 4, 8 | none, n-gram, EAGLE3 |

One variable per run. Each run at least N = 4 x C requests.

## Reading the result

- Decide on p95; p50 only for comparison with the previous run
- Total tok/s grows with C until saturation; the point where TPOT p95 leaves the SLO is the working maximum for `max-num-seqs`
- TTFT grows with C when KV is full: check `waiting` and `preemptions` in `task metrics` after the run
- Errors above 0: the result is invalid, find the cause first

## Log entry

```
date | profile | engine/version | GPU x N, TP | IN/OUT | C | ttft p95 | tpot p95 | tok/s | verdict | what changed
```

`task bench -- --json` also prints a JSON line with the same fields.
