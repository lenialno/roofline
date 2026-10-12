#!/usr/bin/env bash
# Check the parser table against the latest vLLM and SGLang releases without installing them:
# fetch the parser registry files of each release tag into a stub package and run task doctor on it.
# Needs gh (GH_TOKEN) and python3. Exit 1 when doctor finds a mismatch for any runtime.
set -uo pipefail
root=$(cd "$(dirname "$0")/../.." && pwd)
work=$(mktemp -d)
rc=0
check() {  # runtime repo prefix-in-repo files...
  local rt=$1 repo=$2 prefix=$3; shift 3
  local tag ver pkg="$work/$rt/$rt"
  tag=$(gh api "repos/$repo/releases/latest" -q .tag_name) || { echo "drift: no release for $repo"; rc=1; return; }
  ver=${tag#v}
  mkdir -p "$pkg" "$work/$rt/$rt-$ver.dist-info"
  printf 'Metadata-Version: 2.1\nName: %s\nVersion: %s\n' "$rt" "$ver" > "$work/$rt/$rt-$ver.dist-info/METADATA"
  : > "$pkg/__init__.py"
  for f in "$@"; do
    mkdir -p "$(dirname "$pkg/$f")"
    gh api "repos/$repo/contents/$prefix$f?ref=$tag" -H "Accept: application/vnd.github.raw" > "$pkg/$f" 2>/dev/null || rm -f "$pkg/$f"
  done
  echo "######## $rt $tag"
  PYTHONPATH="$work/$rt" RUNTIME=$rt INFER_URL=http://127.0.0.1:9 CURL_TIMEOUT=1 DOCTOR_SMOKE=0 \
    python3 "$root/skills/roofline-toolbox/scripts/doctor.py" || rc=1
}
check vllm vllm-project/vllm vllm/ tool_parsers/__init__.py entrypoints/openai/tool_parsers/__init__.py reasoning/__init__.py
check sglang sgl-project/sglang python/sglang/ srt/function_call/function_call_parser.py srt/parser/reasoning_parser.py srt/reasoning_parser.py
rm -rf "$work"
exit $rc
