#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."
if [[ "${1:-}" == --help || "${1:-}" == -h ]]; then
    cat <<'HELP'
Prepare the existing lab for direct .ipynb execution in an IDE; no web server or tunnel.
Usage: bash scripts/prepare_notebooks.sh [options]
  --group group_01..group_06  Assigned group (default: LAB_GROUP or group_01)
  --device cpu|cuda          Training device (default: LAB_DEVICE or cpu)
  --render-backend osmesa|egl Rendering (default: MUJOCO_GL or osmesa)
  --dataset PATH            Official HDF5 (default: LAB_DATASET or data/low_dim_v15.hdf5)
  --from-file PATH          Import an offline copy with the same SHA256 check
Existing LAB_VENV, LAB_OUTPUT_ROOT, LAB_REFERENCE_ROOT, LAB_LOCK_DIR, HF_ENDPOINT,
LAB_DATASET_URL and explicit renderer-library variables are supported.
System graphics libraries and uv must already be installed; see README.
HELP
    exit 0
fi
export MUJOCO_GL=${MUJOCO_GL:-osmesa}
bash scripts/setup_environment.sh
exec scripts/lab_python.sh scripts/prepare_notebooks.py "$@"
