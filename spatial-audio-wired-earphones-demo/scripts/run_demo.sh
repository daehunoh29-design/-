#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="${SCRIPT_DIR}/.."

EXECUTABLE="${PROJECT_ROOT}/build/spatial_audio_demo"
if [[ ! -x "${EXECUTABLE}" ]]; then
  echo "Executable not found. Run ./scripts/build.sh first."
  exit 1
fi

echo "Spatial audio wired earphones demo"
echo "Use: --interactive or --demo assets/config/demo_positions.json or --azimuth 45 --distance 1.0 --wav assets/audio/beep.wav"

"${EXECUTABLE}" --interactive
