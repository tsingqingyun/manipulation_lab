import contextlib
import fcntl
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import platform
import signal
import time

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data/low_dim_v15.hdf5"
KEYS = ["robot0_eef_pos", "robot0_eef_quat", "robot0_gripper_qpos", "object"]


def policy_observation(obs):
    """Use measured world pose, excluding robosuite 1.5.1 cached relative sensors."""
    return {k: obs[k][..., 7:14] if k == "object" else obs[k] for k in KEYS}


def write_json(path, value):
    Path(path).write_text(json.dumps(value, indent=2, allow_nan=False) + "\n")


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def new_output(path):
    path = Path(path).resolve()
    path.mkdir(parents=True, exist_ok=False)
    return path


def versions():
    names = ["robomimic", "robosuite", "mujoco", "torch", "torchvision", "numpy", "h5py", "jupyterlab"]
    return {"python": platform.python_version(), **{n: importlib.metadata.version(n) for n in names}}


@contextlib.contextmanager
def deadline(seconds):
    def expired(*_):
        raise TimeoutError(f"Task exceeded {seconds}s; partial outputs are preserved")
    previous = signal.signal(signal.SIGALRM, expired)
    previous_timer = signal.getitimer(signal.ITIMER_REAL)
    start = time.monotonic()
    limit = min(seconds, previous_timer[0]) if previous_timer[0] > 0 else seconds
    signal.setitimer(signal.ITIMER_REAL, limit)
    try:
        yield
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        signal.signal(signal.SIGALRM, previous)
        if previous_timer[0] > 0:
            signal.setitimer(signal.ITIMER_REAL, max(0.001, previous_timer[0] - (time.monotonic() - start)))


@contextlib.contextmanager
def resource_slot(kind, timeout=900):
    # All groups on a host must use the SAME administrator-owned lock directory.
    directory = Path(os.environ.get("LAB_LOCK_DIR", "/tmp/manipulation-learning-lab-locks"))
    directory.mkdir(exist_ok=True, mode=0o1777)
    path = directory / f"{kind}.lock"
    fd = os.open(path, os.O_CREAT | os.O_RDWR, 0o666)
    start = time.monotonic()
    try:
        while True:
            try:
                fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                break
            except BlockingIOError:
                if time.monotonic() - start > timeout:
                    raise TimeoutError(f"{kind} queue timeout; retry in a new output directory")
                time.sleep(0.5)
        yield
    finally:
        os.close(fd)
