#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."
LAB_ROOT=$PWD
export LAB_VENV=${LAB_VENV:-"$LAB_ROOT/.venv"}
command -v uv >/dev/null || { echo 'Install uv: https://docs.astral.sh/uv/getting-started/installation/'; exit 1; }
git submodule update --init third_party/robomimic third_party/robosuite
if [[ ! -x "$LAB_VENV/bin/python" ]]; then uv venv --python 3.12.13 "$LAB_VENV"; fi
"$LAB_VENV/bin/python" -c 'import sys; assert sys.version_info[:3] == (3, 12, 13), "Use a NEW LAB_VENV with Python 3.12.13"'
uv pip install --python "$LAB_VENV/bin/python" cmake==3.31.6 setuptools==80.9.0 wheel==0.45.1
export PATH="$LAB_VENV/bin:$PATH"
uv pip install --python "$LAB_VENV/bin/python" -r requirements.lock.txt
uv pip install --python "$LAB_VENV/bin/python" --no-deps --no-build-isolation -e "$LAB_ROOT/third_party/robomimic" -e "$LAB_ROOT/third_party/robosuite" -e "$LAB_ROOT"
uv pip check --python "$LAB_VENV/bin/python"
"$LAB_VENV/bin/python" -m ipykernel install --prefix "$LAB_VENV" --name manipulation-lab --display-name 'Manipulation Lab (Python 3.12)'
echo 'Installed. Download the dataset, then run scripts/smoke_test.py. See README.md.'
