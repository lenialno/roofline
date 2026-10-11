#!/usr/bin/env bash
# Last LINES (default 100) of the runtime log written by serve.sh. FOLLOW=1 to tail -f.
set -uo pipefail
. "$(dirname "$0")/common.sh"
profile="${1:-${INFER_PROFILE:-}}"
if [ -z "$profile" ]; then
  f=$(ls -t "$INFER_STATE_DIR"/*.log 2>/dev/null | head -1)
else
  f="$INFER_STATE_DIR/$profile.log"
fi
[ -n "${f:-}" ] && [ -f "$f" ] || { echo "logs: no log file in $INFER_STATE_DIR (profile: ${profile:-any})" >&2; exit 1; }
echo "== $f"
if [ "${FOLLOW:-0}" = "1" ]; then tail -n "${LINES:-100}" -f "$f"; else tail -n "${LINES:-100}" "$f"; fi
