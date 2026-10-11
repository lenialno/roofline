#!/usr/bin/env bash
# Served models from /v1/models with max context when the runtime reports it.
set -uo pipefail
. "$(dirname "$0")/common.sh"
body=$(http_get "$INFER_URL/v1/models") || { echo "models: $INFER_URL/v1/models unreachable" >&2; exit 1; }
printf '%s' "$body" | python3 -I -c '
import sys, json
try:
    d = json.load(sys.stdin)
except Exception as e:
    print("models: response is not JSON: %s" % e, file=sys.stderr); sys.exit(1)
rows = d.get("data") or []
if not rows:
    print("models: no models served", file=sys.stderr); sys.exit(1)
print("%-40s %-10s %-12s %s" % ("id", "max_len", "owned_by", "root"))
for m in rows:
    print("%-40s %-10s %-12s %s" % (m.get("id"), m.get("max_model_len", "?"), m.get("owned_by", ""), m.get("root", "")))
'
