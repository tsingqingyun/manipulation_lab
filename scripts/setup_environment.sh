#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."
LAB_ROOT=$PWD
LAB_REPO=$LAB_ROOT
command -v uv >/dev/null || { echo 'Install uv first: https://docs.astral.sh/uv/getting-started/installation/'; exit 1; }
git -C "$LAB_REPO" submodule update --init third_party/robomimic third_party/robosuite
if [[ ! -x .venv/bin/python ]]; then uv venv --python 3.12.13 .venv; fi
uv pip install --python .venv/bin/python cmake==3.31.6 setuptools==80.9.0 wheel==0.45.1
export PATH="$LAB_ROOT/.venv/bin:$PATH"
uv pip install --python .venv/bin/python -r requirements.lock.txt
uv pip install --python .venv/bin/python --no-deps -e "$LAB_REPO/third_party/robomimic" -e "$LAB_REPO/third_party/robosuite" -e .
uv pip check --python .venv/bin/python
.venv/bin/python -m ipykernel install --prefix .venv --name manipulation-lab --display-name 'Manipulation Lab (Python 3.12)'
echo 'Installed. Run scripts/lab_python.sh scripts/download_dataset.py then preflight.py with a NEW output path.'
