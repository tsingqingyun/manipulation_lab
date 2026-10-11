"""Prepare and register a configured kernel for direct IDE notebook execution."""
import _bootstrap
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import sys
import tempfile
import uuid
from jupyter_core.paths import jupyter_data_dir
from manipulation_lab.common import ROOT, DATA, new_output, write_json
from manipulation_lab.notebook import command
from download_dataset import obtain_dataset

# Deliberately exclude authentication, proxy credentials and unrelated environment state.
PASSTHROUGH = ("LD_LIBRARY_PATH", "__EGL_VENDOR_LIBRARY_FILENAMES", "MUJOCO_EGL_DEVICE_ID",
               "CUDA_VISIBLE_DEVICES", "OMP_NUM_THREADS", "MKL_NUM_THREADS", "NUMBA_DISABLE_JIT")


def kernel_environment(group, device, backend, dataset):
    env = {key: os.environ[key] for key in PASSTHROUGH if key in os.environ}
    env.update(LAB_GROUP=group, LAB_DEVICE=device, MUJOCO_GL=backend,
               LAB_VENV=str(Path(sys.prefix).absolute()), LAB_DATASET=str(Path(dataset).expanduser().resolve()))
    reference = ROOT / "checkpoints/reference_v1"
    if (not (reference / "reference_evaluation/summary.json").is_file()
            and (ROOT / "checkpoints/reference_evaluation/summary.json").is_file()):
        reference = ROOT / "checkpoints"
    for key, default in [("LAB_OUTPUT_ROOT", ROOT / "outputs"), ("LAB_REFERENCE_ROOT", reference),
                         ("LAB_LOCK_DIR", "/tmp/manipulation-learning-lab-locks")]:
        env[key] = str(Path(os.environ.get(key, default)).expanduser().resolve())
    env.setdefault("NUMBA_DISABLE_JIT", "1")
    return env


def register_kernel(env, registry=None):
    """Identical settings are idempotent; other projects/groups remain untouched."""
    identity = json.dumps({"root": str(ROOT), "python": sys.executable, "env": env}, sort_keys=True)
    suffix = hashlib.sha256(identity.encode()).hexdigest()[:10]
    name = f"manipulation-lab-{env['LAB_GROUP'].replace('_', '-')}-{suffix}"
    display = f"Manipulation Lab ({env['LAB_GROUP']}, {env['LAB_DEVICE']}, {suffix[:4]})"
    spec = {"argv": [sys.executable, "-m", "ipykernel_launcher", "-f", "{connection_file}"],
            "display_name": display, "language": "python", "env": env}
    registry = Path(registry) if registry is not None else Path(jupyter_data_dir()) / "kernels"
    registry.mkdir(parents=True, exist_ok=True)
    destination = registry / name
    if destination.exists():
        if destination.is_symlink() or json.loads((destination / 'kernel.json').read_text()) != spec:
            raise FileExistsError(f"Preserving an unexpected existing kernel: {destination}")
    else:
        # Publish a complete spec so an editor never discovers a half-written kernel.
        with tempfile.TemporaryDirectory(prefix='.lab-kernel-', dir=registry) as staging:
            stage = Path(staging) / name
            stage.mkdir()
            write_json(stage / 'kernel.json', spec)
            stage.rename(destination)
    return {"name": name, "display_name": display, "directory": str(destination)}


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--group', choices=[f'group_{i:02d}' for i in range(1, 7)], default=os.environ.get('LAB_GROUP', 'group_01'))
    p.add_argument('--device', choices=['cpu', 'cuda'], default=os.environ.get('LAB_DEVICE', 'cpu'))
    # The shell wrapper defaults to EGL; the one-command wrapper sets the portable default.
    p.add_argument('--render-backend', choices=['osmesa', 'egl'], default=os.environ.get('MUJOCO_GL', 'osmesa'))
    p.add_argument('--dataset', default=str(DATA))
    p.add_argument('--from-file')
    a = p.parse_args()
    env = kernel_environment(a.group, a.device, a.render_backend, a.dataset)
    os.environ.update(env)
    output = new_output(Path(env['LAB_OUTPUT_ROOT']) / a.group / 'setup' /
                        (datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ') + '_' + uuid.uuid4().hex[:8]))
    write_json(output / 'setup.json', {'ready': False, 'group': a.group})
    obtain_dataset(a.dataset, from_file=a.from_file)
    command('preflight.py', '--dataset', a.dataset, '--output', output / 'preflight')
    preflight = json.loads((output / 'preflight/preflight.json').read_text())
    if a.device == 'cuda' and not preflight['cuda_available']:
        raise RuntimeError('CUDA requested but unavailable. Choose --device cpu and run preparation again; failed output is retained.')
    kernel = register_kernel(env)
    reference_ready = (Path(env['LAB_REFERENCE_ROOT']) / 'reference_evaluation/summary.json').is_file()
    write_json(output / 'setup.json', {'ready': True, 'group': a.group, 'kernel': kernel,
               'environment': env, 'reference_evidence_available': reference_ready})
    print(f"\nREADY: open notebooks/01_demonstrations.ipynb in your IDE.\n"
          f"Select Kernel -> Jupyter Kernels -> {kernel['display_name']}\n"
          f"Kernel ID: {kernel['name']}\nSetup record: {output / 'setup.json'}\n"
          "Run notebooks 01 -> 02 -> 03 -> 04. No browser server or manual port forwarding is needed.")
    if not reference_ready:
        print('Instructor reference evidence is not prepared. It is needed if the primary student policy has no failure; see docs/instructor_guide.md.')
