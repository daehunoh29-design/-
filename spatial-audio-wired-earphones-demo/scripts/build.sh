#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="${SCRIPT_DIR}/.."

echo "이 프로젝트는 이제 macOS용 Python 데모입니다. C++ 빌드는 필요하지 않습니다."
echo "설정을 진행합니다."
"${PROJECT_ROOT}/scripts/setup_macos.sh"
