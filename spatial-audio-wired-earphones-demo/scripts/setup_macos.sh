#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="${SCRIPT_DIR}/.."
VENV_DIR="${PROJECT_ROOT}/.venv"

cd "${PROJECT_ROOT}"

if ! command -v python3 >/dev/null 2>&1; then
  echo "python3를 찾을 수 없습니다. macOS에 Python 3를 설치한 뒤 다시 실행하세요."
  exit 1
fi

python3 -m venv "${VENV_DIR}"
"${VENV_DIR}/bin/python" -m pip install --upgrade pip setuptools wheel
if ! "${VENV_DIR}/bin/python" -m pip install -r requirements.txt; then
  echo
  echo "의존성 설치에 실패했습니다."
  echo "macOS에서 Python 3.11 또는 3.12를 사용하면 pyroomacoustics 설치가 더 안정적입니다."
  echo "예: python3.12 -m venv .venv"
  exit 1
fi
"${VENV_DIR}/bin/python" scripts/generate_audio.py

echo
echo "설정 완료"
echo "실행: ./scripts/run_macos.sh"
