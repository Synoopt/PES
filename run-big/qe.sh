#!/bin/bash
set -euo pipefail

# Usage: bash qe.sh [pw_exec]
# If not provided, defaults to pw.x in PATH

PW_EXEC=${1:-pw.x}

mkdir -p pseudo tmp

shopt -s nullglob
for dir in Ne*,H*; do
  if [[ -d "$dir" && -f "$dir/pw.in" ]]; then
    echo "Running QE in $dir"
    "$PW_EXEC" -in "$dir/pw.in" > "$dir/pw.out"
  fi
done

echo "QE batch job completed. Output written to pw.out in each subdirectory."
