# Serving incident postmortem

Filled in on the day of the incident, 15 lines, no judgments about people.

```
Incident: <date, start and end time, profile, model>
Symptom: <what clients saw; one sentence>
Detection: <who noticed and how; alert or complaint>
Timeline:
  hh:mm  <event or action>
  hh:mm  <...>
Metrics before: <waiting, kv usage, preemptions, ttft p95, tpot p95 from task metrics>
Metrics after: <the same>
Root cause: <one sentence; config, version, load, hardware>
What changed: <profile, flag, version; link to the profile commit>
Verification: <task health, smoke-toolcall, bench: result>
To catch it earlier: <which metric threshold, which test in bench or smoke>
Open questions: <what is unknown>
```
