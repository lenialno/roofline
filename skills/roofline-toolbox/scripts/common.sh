# Shared helpers for roofline scripts. Source, do not execute.
# Contract: INFER_URL is the OpenAI-compatible base URL without /v1.
# Settings priority: environment (task vars arrive here too) > inference.env in the
# current directory (or $INFER_ENV_FILE) > defaults. Empty counts as unset.
_envfile="${INFER_ENV_FILE:-$PWD/inference.env}"
if [ -f "$_envfile" ]; then
  while IFS= read -r _line || [ -n "$_line" ]; do
    case "$_line" in ''|\#*) continue;; esac
    case "$_line" in *=*) ;; *) continue;; esac
    _k="${_line%%=*}"; _v="${_line#*=}"
    case "$_k" in ''|*[!A-Za-z0-9_]*) continue;; esac
    _v="${_v%\"}"; _v="${_v#\"}"; _v="${_v%\'}"; _v="${_v#\'}"
    if [ -z "${!_k:-}" ]; then export "$_k=$_v"; fi
  done < "$_envfile"
fi
INFER_URL="${INFER_URL:-http://127.0.0.1:8000}"
INFER_URL="${INFER_URL%/}"
INFER_URL="${INFER_URL%/v1}"
INFER_API_KEY="${INFER_API_KEY:-}"
INFER_STATE_DIR="${INFER_STATE_DIR:-$PWD/.inference-state}"
CURL_TIMEOUT="${CURL_TIMEOUT:-10}"

auth_args() {
  if [ -n "$INFER_API_KEY" ]; then printf '%s\n' -H "Authorization: Bearer $INFER_API_KEY"; fi
}

# http_code URL -> prints status code (000 when unreachable)
http_code() {
  local c
  c=$(curl -s -o /dev/null -w '%{http_code}' --max-time "$CURL_TIMEOUT" $(auth_args) "$1" 2>/dev/null)
  printf '%s' "${c:-000}"
}

# http_get URL -> body on stdout, non-zero exit on transport error
http_get() {
  curl -sS --max-time "$CURL_TIMEOUT" $(auth_args) "$1"
}

ok()   { printf 'OK   %s\n' "$*"; }
fail() { printf 'FAIL %s\n' "$*" >&2; }
