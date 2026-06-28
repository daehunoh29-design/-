#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="${SCRIPT_DIR}/.."
PYTHON="${PROJECT_ROOT}/.venv/bin/python"
PORT="${PORT:-8765}"

if [[ ! -x "${PYTHON}" ]]; then
  echo "가상환경이 없습니다. 먼저 ./scripts/setup_macos.sh 를 실행하세요."
  exit 1
fi

cd "${PROJECT_ROOT}"
echo "브라우저에서 열기: http://127.0.0.1:${PORT}"
"${PYTHON}" web_server.py --host 127.0.0.1 --port "${PORT}"
