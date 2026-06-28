#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="${SCRIPT_DIR}/.."
PYTHON="${PROJECT_ROOT}/.venv/bin/python"

if [[ ! -x "${PYTHON}" ]]; then
  echo "가상환경이 없습니다. 먼저 ./scripts/setup_macos.sh 를 실행하세요."
  exit 1
fi

cd "${PROJECT_ROOT}"
"${PYTHON}" spatial_audio_demo.py "$@"
