#!/bin/zsh
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT_DIR"

if [ "${1:-}" = "gui" ]; then
  echo "[INFO] Starting Streamlit GUI..."
  streamlit run "$ROOT_DIR/gui.py" --server.port 8501 --server.address 0.0.0.0
else
  echo "[INFO] Using CLI entrypoint..."
  python "$ROOT_DIR/main.py" "$@"
fi

