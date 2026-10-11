#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."
LAB_ROOT=$PWD
export LAB_VENV=${LAB_VENV:-"$LAB_ROOT/.venv"}
if [[ -n "${LAB_UV:-}" ]]; then
    UV_BIN=$(command -v "$LAB_UV") || { echo 'LAB_UV must name an executable uv binary.' >&2; exit 1; }
else
    UV_BIN=$(command -v uv || true)
    if [[ -z "$UV_BIN" ]]; then
        for uv_dir in "${UV_INSTALL_DIR:-}" "${XDG_BIN_HOME:-}" "${XDG_DATA_HOME:-$HOME/.local/share}/../bin" "$HOME/.local/bin" "$HOME/.cargo/bin"; do
            if [[ -n "$uv_dir" && -x "$uv_dir/uv" ]]; then UV_BIN="$uv_dir/uv"; break; fi
        done
    fi
fi
if [[ -z "$UV_BIN" || ! -x "$UV_BIN" ]]; then
    echo 'uv not found. Install https://docs.astral.sh/uv/getting-started/installation/ or set LAB_UV to its absolute executable path.' >&2
    exit 1
fi
# Retain an absolute executable path even if shell startup or later PATH changes.
UV_BIN=$(cd "$(dirname "$UV_BIN")" && pwd)/$(basename "$UV_BIN")
if [[ "${1:-}" == --check-uv ]]; then echo "uv executable: $UV_BIN"; "$UV_BIN" --version; exit 0; fi
if [[ $# -ne 0 ]]; then echo 'Usage: bash scripts/setup_environment.sh [--check-uv]' >&2; exit 2; fi
git submodule update --init third_party/robomimic third_party/robosuite
if [[ ! -x "$LAB_VENV/bin/python" ]]; then "$UV_BIN" venv --python 3.12.13 "$LAB_VENV"; fi
"$LAB_VENV/bin/python" -c 'import sys; assert sys.version_info[:3] == (3, 12, 13), "Use a NEW LAB_VENV with Python 3.12.13"'
"$UV_BIN" pip install --python "$LAB_VENV/bin/python" cmake==3.31.6 setuptools==80.9.0 wheel==0.45.1
export PATH="$LAB_VENV/bin:$PATH"
"$UV_BIN" pip install --python "$LAB_VENV/bin/python" -r requirements.lock.txt
"$UV_BIN" pip install --python "$LAB_VENV/bin/python" --no-deps --no-build-isolation -e "$LAB_ROOT/third_party/robomimic" -e "$LAB_ROOT/third_party/robosuite" -e "$LAB_ROOT"
"$UV_BIN" pip check --python "$LAB_VENV/bin/python"
"$LAB_VENV/bin/python" -m ipykernel install --prefix "$LAB_VENV" --name manipulation-lab --display-name 'Manipulation Lab (Python 3.12)'
echo 'Installed. Download the dataset, then run scripts/smoke_test.py. See README.md.'
