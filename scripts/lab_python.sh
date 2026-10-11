#!/usr/bin/env bash
set -euo pipefail
LAB_ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
export MUJOCO_GL=${MUJOCO_GL:-egl}
export OMP_NUM_THREADS=${OMP_NUM_THREADS:-2}
export MKL_NUM_THREADS=${MKL_NUM_THREADS:-2}
# Some compute-only hosts have a matching user-installed NVIDIA graphics stack.
# Use it only when the system EGL vendor configuration is missing.
if [[ ! -f /usr/share/glvnd/egl_vendor.d/10_nvidia.json ]] && command -v nvidia-smi >/dev/null; then
    LAB_DRIVER=$(nvidia-smi --query-gpu=driver_version --format=csv,noheader | head -1)
    LAB_NVIDIA_LIB="$HOME/.local/lib/nvidia-$LAB_DRIVER"
    LAB_EGL_JSON="$HOME/.local/share/glvnd/egl_vendor.d/10_nvidia.json"
    if [[ -f "$LAB_NVIDIA_LIB/libEGL_nvidia.so.0" && -f "$LAB_EGL_JSON" ]]; then
        export LD_LIBRARY_PATH="$LAB_NVIDIA_LIB${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
        export __EGL_VENDOR_LIBRARY_FILENAMES="${__EGL_VENDOR_LIBRARY_FILENAMES:-$LAB_EGL_JSON}"
    fi
fi
exec "$LAB_ROOT/.venv/bin/python" "$@"
