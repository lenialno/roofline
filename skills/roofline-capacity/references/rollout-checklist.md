# Rollout checklist

```
What is rolled out: <model | engine version | template | flag>
Profile: <profiles/<new>.env>, port <N>; old profile <old>, port <M>
Versions: engine <x.y.z>, torch <...>, CUDA <...>, driver <...>, image <digest>
Weights: sha256 verified <yes/no>, safetensors, chat template from the repository <yes/no>

Gate (all PASS, otherwise no rollout):
  task health            <...>
  task smoke-toolcall    <...>
  task bench             ttft p95 <...> / baseline <...>; tpot p95 <...> / baseline <...>
  agent tasks            <N of M>, baseline <N of M>

Canary: <traffic share>, <duration>, metrics of both replicas every 10 minutes
Rollback criteria: client errors > 1%, ttft p95 or tpot p95 worse than baseline by 20%, smoke FAIL
Rollback: traffic to port <M>; task stop INFER_PROFILE=<new>
Full switch: <time>; stop the old profile <when>
Log: entry in the bench log and in the profiles
```
