"""Isolate native simulation checks so crashes retain a diagnostic record."""
import _bootstrap
import argparse
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import time
from manipulation_lab.common import DATA, new_output, versions, write_json


def run_worker(dataset, output):
    def phase(name):
        write_json(output / "phase.json", {"phase": name})
        print(f"Preflight: {name}", flush=True)

    phase("import_numba")
    import numba
    runtime = {"numba_disable_jit_requested": os.environ["NUMBA_DISABLE_JIT"],
               "numba_disable_jit_effective": bool(numba.config.DISABLE_JIT),
               "render_backend": os.environ.get("MUJOCO_GL")}
    write_json(output / "runtime.json", runtime)
    phase("import_simulator")
    from manipulation_lab.simulator import compatibility_check
    phase("simulation_reset_step_render")
    result = compatibility_check(dataset, output)
    # CUDA probing comes after the CPU simulation/render check, never before it.
    phase("cuda_probe")
    import torch
    import psutil
    cuda = torch.cuda.is_available()
    result.update({"runtime": runtime, "available_ram_gib": psutil.virtual_memory().available / 2**30,
        "free_disk_gib": shutil.disk_usage(output).free / 2**30, "cuda_available": cuda,
        "gpu": torch.cuda.get_device_name() if cuda else None})
    write_json(output / "worker_result.json", result)
    phase("complete")


def run_preflight(dataset, output, timeout=300):
    start = time.monotonic()
    result = {"passed": False, "status": "started", "versions": versions(),
        "runtime": {"numba_disable_jit_requested": os.environ["NUMBA_DISABLE_JIT"],
                    "render_backend": os.environ.get("MUJOCO_GL")},
        "worker_log": "preflight_worker.log"}
    write_json(output / "preflight.json", result)
    command = [sys.executable, "-X", "faulthandler", "-u", str(Path(__file__).resolve()),
               "--worker", "--dataset", str(dataset), "--output", str(output)]
    try:
        with (output / "preflight_worker.log").open("x") as log:
            completed = subprocess.run(command, stdout=log, stderr=subprocess.STDOUT, timeout=timeout)
        result["worker_returncode"] = completed.returncode
        if completed.returncode < 0:
            result["signal"] = signal.Signals(-completed.returncode).name
        if completed.returncode == 0:
            result.update(json.loads((output / "worker_result.json").read_text()))
            result.update(passed=True, status="passed")
        else:
            result.update(status="failed", error="Native worker exited unsuccessfully; inspect preflight_worker.log.")
    except subprocess.TimeoutExpired:
        result.update(status="timeout", error=f"Preflight worker exceeded {timeout}s and was stopped.")
    except (OSError, ValueError) as exc:
        result.update(status="failed", error=str(exc))
    for filename, key in [("phase.json", "last_phase"), ("runtime.json", "runtime")]:
        if (output / filename).exists():
            result[key] = json.loads((output / filename).read_text())
    result["elapsed_seconds"] = time.monotonic() - start
    if not result["passed"]:
        result["recovery"] = ("Keep this output. Check the last phase, log and pinned versions. For a JIT crash, "
            "set NUMBA_DISABLE_JIT=1 before launching a NEW Python/kernel and use a new output directory. "
            "For rendering errors, check the configured system OSMesa/EGL libraries. No automatic retry was made.")
    write_json(output / "preflight.json", result)
    return result


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--dataset", default=str(DATA))
    p.add_argument("--output", required=True)
    p.add_argument("--timeout", type=float, default=300)
    p.add_argument("--worker", action="store_true", help=argparse.SUPPRESS)
    a = p.parse_args()
    if a.timeout <= 0:
        p.error("--timeout must be positive")
    if a.worker:
        run_worker(a.dataset, Path(a.output))
    else:
        result = run_preflight(a.dataset, new_output(a.output), a.timeout)
        print(json.dumps(result, indent=2))
        sys.exit(0 if result["passed"] else 1)
