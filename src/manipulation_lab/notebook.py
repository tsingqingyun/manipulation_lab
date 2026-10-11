"""Small notebook helpers; simulation and training remain separate processes."""
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import subprocess
import uuid
from .common import ROOT, write_json


def workspace(group=None, fresh=False):
    group = group or os.environ.get("LAB_GROUP", "group_01")
    if not re.fullmatch(r"group_0[1-6]", group):
        raise ValueError("Choose group_01 .. group_06")
    base = Path(os.environ.get("LAB_OUTPUT_ROOT", ROOT / "outputs")).resolve() / group
    base.mkdir(parents=True, exist_ok=True)
    pointer = base / "current_session.json"
    if fresh:
        run = base / (datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "_" + uuid.uuid4().hex[:8])
        run.mkdir()
        write_json(pointer, {"run": str(run), "group": group})
        write_json(run / "session.json", {"group": group, "run": str(run)})
    elif pointer.exists():
        run = Path(json.loads(pointer.read_text())["run"]).resolve()
        if run.parent != base:
            raise ValueError("Session pointer outside group workspace")
    else:
        raise FileNotFoundError("Run Notebook 01 first")
    print(f"{group} → {run}")
    return run


def command(script, *args, timeout=7500):
    # Argument list avoids shell interpolation of paths / student inputs.
    cmd = [str(ROOT / "scripts/lab_python.sh"), str(ROOT / "scripts" / script), *map(str, args)]
    print("Running", script, flush=True)
    subprocess.run(cmd, cwd=ROOT, check=True, timeout=timeout)


def next_stage(run, name):
    """Re-running a notebook keeps earlier results, then advances this session pointer."""
    suffix = datetime.now(timezone.utc).strftime("%H%M%S") + "_" + uuid.uuid4().hex[:6]
    stage = Path(run) / f"{name}_{suffix}"
    write_json(Path(run) / f"{name}_current.json", {"path": str(stage)})
    return stage


def stage_path(run, name):
    p = Path(json.loads((Path(run) / f"{name}_current.json").read_text())["path"]).resolve()
    if p.parent != Path(run).resolve():
        raise ValueError("Stage path outside session")
    return p
