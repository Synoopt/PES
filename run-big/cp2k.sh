#!/bin/bash
set -euo pipefail

# 使用方法：bash cp2k.sh [cp2k_exec]
# 若未提供，则默认使用 PATH 中的 cp2k.psmp

CP2K_EXEC=${1:-cp2k.psmp}

mkdir -p tmp

shopt -s nullglob
for dir in Ne*,H*; do
  if [[ -d "$dir" && -f "$dir/cp2k.inp" ]]; then
    echo "Running CP2K in $dir"
    (cd "$dir" && "$CP2K_EXEC" -i cp2k.inp -o cp2k.out)
  fi
done

echo "CP2K 批量作业完成。输出写入各子目录的 cp2k.out。"


