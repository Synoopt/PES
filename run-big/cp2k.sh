#!/bin/bash
set -euo pipefail

# Guidance：bash cp2k.sh [cp2k_exec]
# Default Setting: cp2k.psmp

CP2K_EXEC=${1:-cp2k.psmp}

mkdir -p tmp

shopt -s nullglob
for dir in Ne*,H*; do
  if [[ -d "$dir" && -f "$dir/cp2k.inp" ]]; then
    echo "Running CP2K in $dir"
    (cd "$dir" && "$CP2K_EXEC" -i cp2k.inp -o cp2k.out)
  fi
done

echo "CP2K Completed. Output saved as cp2k.out。"


