#!/usr/bin/env bash
# Stop the runtime started by serve.sh. Without a profile, stop every pid file in the state dir.
# Exit 0 when nothing is running.
set -uo pipefail
. "$(dirname "$0")/common.sh"
profile="${1:-${INFER_PROFILE:-}}"
stop_one() {
  local pidf="$1" name pid i
  name=$(basename "$pidf" .pid)
  pid=$(cat "$pidf" 2>/dev/null || true)
  if [ -z "$pid" ] || ! kill -0 "$pid" 2>/dev/null; then
    echo "stop: '$name' not running (stale pid file removed)"; rm -f "$pidf"; return 0
  fi
  # kill the whole process group when possible (vllm spawns workers)
  pgid=$(ps -o pgid= -p "$pid" 2>/dev/null | tr -d ' ')
  mypgid=$(ps -o pgid= -p "$$" 2>/dev/null | tr -d ' ')
  # signal the group only when it is the runtime's own group (serve.sh starts it detached); never our own group
  if [ -n "$pgid" ] && [ "$pgid" != "$mypgid" ] && [ "$pgid" = "$pid" ]; then kill -TERM -- "-$pgid" 2>/dev/null || kill -TERM "$pid" 2>/dev/null; else pgid=""; kill -TERM "$pid" 2>/dev/null; fi
  for i in $(seq 1 30); do kill -0 "$pid" 2>/dev/null || break; sleep 1; done
  if kill -0 "$pid" 2>/dev/null; then
    echo "stop: '$name' pid $pid ignored SIGTERM for 30s, sending SIGKILL" >&2
    if [ -n "$pgid" ]; then kill -KILL -- "-$pgid" 2>/dev/null; else kill -KILL "$pid" 2>/dev/null; fi
    sleep 1
  fi
  rm -f "$pidf"
  echo "stop: '$name' stopped (pid $pid)"
}
if [ -n "$profile" ]; then
  f="$INFER_STATE_DIR/$profile.pid"
  [ -f "$f" ] || { echo "stop: '$profile' not running (no pid file)"; exit 0; }
  stop_one "$f"
else
  found=0
  for f in "$INFER_STATE_DIR"/*.pid; do [ -f "$f" ] || continue; found=1; stop_one "$f"; done
  [ "$found" = 1 ] || echo "stop: nothing running (no pid files in $INFER_STATE_DIR)"
fi
exit 0
