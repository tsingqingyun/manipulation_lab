"""Start a token-authenticated loopback JupyterLab. Use JupyterHub for class users."""
import _bootstrap
import argparse
import os
from pathlib import Path
import stat
import subprocess
import tempfile
from manipulation_lab.common import ROOT


def prepare_runtime_dir(env):
    """Keep connection secrets off shared mounts and verify POSIX permissions."""
    directory = Path(env.get("JUPYTER_RUNTIME_DIR") or f"/tmp/manipulation-lab-jupyter-{os.geteuid()}").expanduser().absolute()
    remedy = "Set JUPYTER_RUNTIME_DIR to a private local directory (0700, owned by this user), then restart."
    try:
        directory.mkdir(mode=0o700, parents=True, exist_ok=True)
        info = directory.lstat()
        # jupyter_client adds the sticky bit when writing a kernel connection file.
        # Accept its 1700 directory on restart; owner-only access remains mandatory.
        mode = stat.S_IMODE(info.st_mode) & ~stat.S_ISVTX
        if not stat.S_ISDIR(info.st_mode) or info.st_uid != os.geteuid() or mode != 0o700:
            raise RuntimeError(f"Unsafe Jupyter runtime directory: {directory}. {remedy}")
        fd, probe = tempfile.mkstemp(prefix=".permissions-", dir=directory)
        try:
            if stat.S_IMODE(os.fstat(fd).st_mode) != 0o600:
                raise RuntimeError(f"Runtime filesystem cannot provide 0600 files. {remedy}")
        finally:
            os.close(fd)
            Path(probe).unlink()
    except OSError as exc:
        raise RuntimeError(f"Cannot prepare Jupyter runtime directory: {directory}. {remedy}") from exc
    env["JUPYTER_RUNTIME_DIR"] = str(directory)
    # Never bypass Jupyter's secure connection-file checks.
    env.pop("JUPYTER_ALLOW_INSECURE_WRITES", None)
    return directory


def server_command(port, *, euid=None):
    command = [str(ROOT / "scripts/lab_python.sh"), "-m", "jupyterlab", "--no-browser", "--ip=127.0.0.1",
        f"--port={port}", "--ServerApp.port_retries=0", f"--ServerApp.root_dir={ROOT}",
        "--ServerApp.terminals_enabled=False"]
    if (os.geteuid() if euid is None else euid) == 0:
        command.append("--allow-root")
    return command


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--port", type=int, default=8892)
    p.add_argument("--group", choices=[f"group_{i:02d}" for i in range(1, 7)], default="group_01")
    a = p.parse_args()
    env = os.environ.copy()
    env["LAB_GROUP"] = a.group
    runtime = prepare_runtime_dir(env)
    print(f"Jupyter runtime directory: {runtime} (owner-only access)", flush=True)
    # Jupyter's random token remains enabled. Loopback access via SSH tunnel.
    subprocess.run(server_command(a.port), env=env, check=True)
