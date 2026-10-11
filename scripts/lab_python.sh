#!/usr/bin/env bash
set -euo pipefail
LAB_ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
export LAB_VENV=${LAB_VENV:-"$LAB_ROOT/.venv"}
export MUJOCO_GL=${MUJOCO_GL:-egl}
export OMP_NUM_THREADS=${OMP_NUM_THREADS:-2}
export MKL_NUM_THREADS=${MKL_NUM_THREADS:-2}
# Set before any Numba / robosuite import; JIT may crash on some server builds.
export NUMBA_DISABLE_JIT=${NUMBA_DISABLE_JIT:-1}
# Graphics drivers are system prerequisites. No implicit developer-home fallback.
if [[ ! -x "$LAB_VENV/bin/python" ]]; then
    echo 'Environment missing. Run bash scripts/setup_environment.sh first.' >&2
    exit 1
fi
exec "$LAB_VENV/bin/python" "$@"
