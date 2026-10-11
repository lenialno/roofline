#!/usr/bin/env bash
# Start vLLM or SGLang from a named profile (profiles/<name>.env). Idempotent: a running
# profile is reported, not restarted. Only files inside PROFILES_DIR are accepted.
set -uo pipefail
. "$(dirname "$0")/common.sh"
PROFILES_DIR="${PROFILES_DIR:-$(cd "$(dirname "$0")/.." && pwd)/profiles}"
profile="${1:-${INFER_PROFILE:-}}"
[ -n "$profile" ] || { echo "serve: profile name required: task serve INFER_PROFILE=<name>; see task profiles" >&2; exit 2; }
case "$profile" in *[!A-Za-z0-9._-]*|.*) echo "serve: invalid profile name '$profile'" >&2; exit 2;; esac
pf="$PROFILES_DIR/$profile.env"
[ -f "$pf" ] || { echo "serve: profile not found: $pf" >&2; exit 2; }

mkdir -p "$INFER_STATE_DIR"
pidf="$INFER_STATE_DIR/$profile.pid"; logf="$INFER_STATE_DIR/$profile.log"
if [ -f "$pidf" ] && kill -0 "$(cat "$pidf")" 2>/dev/null; then
  echo "serve: profile '$profile' already running (pid $(cat "$pidf")), log $logf"
  exit 0
fi
rm -f "$pidf"

# profile variables
RUNTIME=""; MODEL=""; SERVED_NAME=""; HOST="0.0.0.0"; PORT="8000"; TP="1"; MAX_MODEL_LEN=""
GPU_MEM_UTIL="0.90"; EXTRA_ARGS=""; CMD=""; CUDA_VISIBLE_DEVICES="${CUDA_VISIBLE_DEVICES:-}"; SERVE_TIMEOUT="${SERVE_TIMEOUT:-900}"
# shellcheck disable=SC1090
. "$pf"

# air-gap defaults: nothing leaves the host
export HF_HUB_OFFLINE="${HF_HUB_OFFLINE:-1}" TRANSFORMERS_OFFLINE="${TRANSFORMERS_OFFLINE:-1}"
export VLLM_NO_USAGE_STATS="${VLLM_NO_USAGE_STATS:-1}" DO_NOT_TRACK="${DO_NOT_TRACK:-1}"
[ -n "$CUDA_VISIBLE_DEVICES" ] && export CUDA_VISIBLE_DEVICES

if [ -z "$CMD" ]; then
  [ -n "$MODEL" ] || { echo "serve: MODEL is empty in $pf" >&2; exit 2; }
  [ -e "$MODEL" ] || echo "serve: WARN MODEL path '$MODEL' does not exist locally (ok only if the runtime resolves it from its own cache)" >&2
  case "$RUNTIME" in
    vllm)
      command -v vllm >/dev/null 2>&1 || { echo "serve: vllm not on PATH" >&2; exit 2; }
      CMD="vllm serve \"$MODEL\" --host $HOST --port $PORT --tensor-parallel-size $TP --gpu-memory-utilization $GPU_MEM_UTIL"
      [ -n "$SERVED_NAME" ] && CMD="$CMD --served-model-name $SERVED_NAME"
      [ -n "$MAX_MODEL_LEN" ] && CMD="$CMD --max-model-len $MAX_MODEL_LEN"
      ;;
    sglang)
      python3 -c 'import sglang' >/dev/null 2>&1 || { echo "serve: sglang not importable" >&2; exit 2; }
      CMD="python3 -m sglang.launch_server --model-path \"$MODEL\" --host $HOST --port $PORT --tp $TP --mem-fraction-static $GPU_MEM_UTIL --enable-metrics"
      [ -n "$SERVED_NAME" ] && CMD="$CMD --served-model-name $SERVED_NAME"
      [ -n "$MAX_MODEL_LEN" ] && CMD="$CMD --context-length $MAX_MODEL_LEN"
      ;;
    *) echo "serve: RUNTIME must be vllm or sglang (or set CMD) in $pf" >&2; exit 2 ;;
  esac
  CMD="$CMD $EXTRA_ARGS"
fi

url="http://127.0.0.1:$PORT"
if [ "$(http_code "$url/health")" = "200" ]; then
  echo "serve: something already answers on $url/health but no pid file for '$profile'; refusing to start a second runtime on the same port" >&2
  exit 1
fi

echo "serve: $profile"
echo "serve: $CMD"
echo "serve: log $logf"
{ echo "=== $(date -u +%FT%TZ) serve $profile"; echo "$CMD"; } >> "$logf"
# own process group, so that stop.sh can kill the runtime and its workers without touching the caller
if command -v setsid >/dev/null 2>&1; then
  setsid nohup bash -c "$CMD" >> "$logf" 2>&1 < /dev/null &
else
  set -m; nohup bash -c "$CMD" >> "$logf" 2>&1 < /dev/null & set +m
fi
pid=$!
echo "$pid" > "$pidf"

t=0
while [ "$t" -lt "$SERVE_TIMEOUT" ]; do
  if ! kill -0 "$pid" 2>/dev/null; then
    echo "serve: process exited early; last log lines:" >&2; tail -n 40 "$logf" >&2; rm -f "$pidf"; exit 1
  fi
  if [ "$(http_code "$url/health")" = "200" ]; then
    echo "serve: healthy after ${t}s on $url (pid $pid)"; exit 0
  fi
  sleep 5; t=$((t+5))
done
echo "serve: not healthy after ${SERVE_TIMEOUT}s; process still running (pid $pid). Check: task logs INFER_PROFILE=$profile" >&2
exit 1
