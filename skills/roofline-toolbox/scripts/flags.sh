#!/usr/bin/env bash
# Grep the installed runtime's CLI help so flags come from the installed version, not from memory.
# RUNTIME=vllm|sglang (default: whichever is installed). Q=<pattern>.
set -uo pipefail
q="${1:-${Q:-}}"
rt="${RUNTIME:-}"
if [ -z "$rt" ]; then
  if command -v vllm >/dev/null 2>&1; then rt=vllm
  elif python3 -c 'import sglang' >/dev/null 2>&1; then rt=sglang
  else echo "flags: neither vllm nor sglang importable on this host" >&2; exit 2; fi
fi
case "$rt" in
  vllm)   help=$(vllm serve --help 2>&1) ;;
  sglang) help=$(python3 -m sglang.launch_server --help 2>&1) ;;
  *) echo "flags: RUNTIME must be vllm or sglang" >&2; exit 2 ;;
esac
echo "== $rt ($( [ "$rt" = vllm ] && vllm --version 2>/dev/null | tail -1 || python3 -c 'import sglang;print(sglang.__version__)' 2>/dev/null ))"
if [ -z "$q" ]; then printf '%s\n' "$help"; else printf '%s\n' "$help" | grep -i -E -B1 -A3 -- "$q" || { echo "flags: no match for '$q'" >&2; exit 1; }; fi
