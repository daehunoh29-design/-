#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="${SCRIPT_DIR}/.."

pushd "${PROJECT_ROOT}" > /dev/null
mkdir -p build
cd build
cmake ..
make -j$(nproc)
popd > /dev/null

echo "Build complete. Run ./scripts/run_demo.sh or ./build/spatial_audio_demo --interactive"
