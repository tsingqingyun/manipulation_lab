"""Start a token-authenticated loopback JupyterLab. Use JupyterHub for class users."""
import _bootstrap
import argparse
import os
import subprocess
from manipulation_lab.common import ROOT

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--port", type=int, default=8892)
    p.add_argument("--group", choices=[f"group_{i:02d}" for i in range(1, 7)], default="group_01")
    a = p.parse_args()
    env = os.environ.copy(); env["LAB_GROUP"] = a.group
    # Jupyter's random token remains enabled. Loopback access via SSH tunnel.
    subprocess.run([str(ROOT / "scripts/lab_python.sh"), "-m", "jupyterlab", "--no-browser", "--ip=127.0.0.1",
        f"--port={a.port}", "--ServerApp.port_retries=0", f"--ServerApp.root_dir={ROOT}",
        "--ServerApp.terminals_enabled=False"], env=env, check=True)
