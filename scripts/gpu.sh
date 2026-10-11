#!/usr/bin/env bash
# GPU inventory: memory, utilization, compute processes. Exit 2 when nvidia-smi is absent.
set -uo pipefail
if ! command -v nvidia-smi >/dev/null 2>&1; then
  echo "gpu: nvidia-smi not found; no NVIDIA driver on this host" >&2
  exit 2
fi
q=$(nvidia-smi --query-gpu=index,name,memory.used,memory.total,utilization.gpu,temperature.gpu,power.draw --format=csv,noheader,nounits 2>&1) || { echo "gpu: nvidia-smi failed: $q" >&2; exit 1; }
printf '%-3s %-30s %9s %9s %7s %5s %5s %6s\n' idx name used_MiB total_MiB free_MiB util% temp watts
printf '%s\n' "$q" | awk -F', *' '{printf "%-3s %-30s %9s %9s %7d %5s %5s %6s\n", $1, substr($2,1,30), $3, $4, $4-$3, $5, $6, $7}'
echo "--- compute processes (gpu_uuid, pid, name, used_MiB)"
procs=$(nvidia-smi --query-compute-apps=gpu_uuid,pid,process_name,used_memory --format=csv,noheader,nounits 2>/dev/null)
if [ -z "$procs" ]; then echo "(none)"; else printf '%s\n' "$procs"; fi
# warnings
printf '%s\n' "$q" | awk -F', *' '$4>0 && ($3/$4)>0.97 {printf "WARN gpu %s memory %.0f%% used: no headroom for KV cache or a second runtime\n", $1, 100*$3/$4}'
exit 0
