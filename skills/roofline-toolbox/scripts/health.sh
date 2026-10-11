#!/usr/bin/env bash
# Liveness and readiness of the OpenAI-compatible endpoint. Exit 1 on any failed check.
set -uo pipefail
. "$(dirname "$0")/common.sh"
rc=0
code=$(http_code "$INFER_URL/health")
if [ "$code" = "200" ]; then ok "/health 200"; else fail "/health -> $code ($INFER_URL)"; rc=1; fi

body=$(http_get "$INFER_URL/v1/models" 2>/dev/null)
model=$(printf '%s' "$body" | python3 -I -c 'import sys,json
try:
    d=json.load(sys.stdin); m=d.get("data") or []
    print(m[0]["id"] if m else "")
except Exception: print("")')
if [ -n "$model" ]; then ok "/v1/models -> $model"; else fail "/v1/models empty or unreachable"; rc=1; fi

if [ -n "$model" ]; then
  t0=$(python3 -I -c 'import time;print(time.time())')
  resp=$(curl -sS --max-time 60 $(auth_args) -H 'Content-Type: application/json' \
    -d "{\"model\":\"$model\",\"messages\":[{\"role\":\"user\",\"content\":\"Reply with the single word: pong\"}],\"max_tokens\":4,\"temperature\":0}" \
    "$INFER_URL/v1/chat/completions" 2>&1)
  t1=$(python3 -I -c 'import time;print(time.time())')
  content=$(printf '%s' "$resp" | python3 -I -c 'import sys,json
try:
    d=json.load(sys.stdin); print((d["choices"][0]["message"].get("content") or "").strip()[:40])
except Exception as e: print("")')
  ms=$(python3 -I -c "print(int(($t1-$t0)*1000))")
  if [ -n "$content" ]; then ok "chat completion ${ms} ms -> \"$content\""; else fail "chat completion: $(printf '%s' "$resp" | head -c 300)"; rc=1; fi
fi
exit $rc
