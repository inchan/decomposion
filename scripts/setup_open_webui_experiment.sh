#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON="${PYTHON:-$ROOT/.venv/bin/python}"
if [ ! -x "$PYTHON" ]; then
  echo 'Run python3 scripts/bootstrap_lab.py first, or set PYTHON to your installed interpreter.' >&2
  exit 1
fi
exec "$PYTHON" -m decomposion_lab.cli lab init \
  --suite "$ROOT/experiments/open-webui" \
  --workspace "${1:-$HOME/decomposion-lab}" --profile smoke
