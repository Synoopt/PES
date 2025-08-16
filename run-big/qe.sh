#!/bin/bash
set -euo pipefail

# 使用方法：bash qe.sh [pw_exec]
# 若未提供，则默认使用 PATH 中的 pw.x

PW_EXEC=${1:-pw.x}

mkdir -p pseudo tmp

shopt -s nullglob
for dir in Ne*,H*; do
  if [[ -d "$dir" && -f "$dir/pw.in" ]]; then
    echo "Running QE in $dir"
    "$PW_EXEC" -in "$dir/pw.in" > "$dir/pw.out"
  fi
done

echo "QE 批量作业完成。输出写入各子目录的 pw.out。"


