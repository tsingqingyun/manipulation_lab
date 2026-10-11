# Linux Server Setup

This guide is for the instructor or administrator. Student instructions are in the root README. The supported target is Linux x86-64; Ubuntu 22.04 was used for acceptance. A fresh Python environment is tested separately from a clean operating-system installation. Consult [the current acceptance record](course_acceptance.md) for the exact verified scope.

## 1. Prepare the host

Use an existing institution-managed Linux server. Install `git`, `curl`, a C/C++ build toolchain, and the graphics packages listed in the README. The Python environment is pinned to Python 3.12.13, PyTorch 2.8.0, MuJoCo 3.2.7, robosuite 1.5.1 and robomimic 0.4.0. Source commit pins and the full transitive lock are version controlled. The project uses uv; it does not depend on Conda or another project's environment.

For six groups, provision at least 32 GB RAM and 30 GB free disk as a starting allocation, then measure on the actual host. Keep at least two CPU threads per active training/evaluation process. One CUDA-capable NVIDIA GPU is recommended for faster training; 8 GB of free VRAM is a practical starting allocation, not a measured minimum. Reserve a device using `CUDA_VISIBLE_DEVICES`. Do not evict unrelated workloads.

Follow README Installation through `setup_environment.sh`. The installer verifies the exact Python patch version and refuses to silently reuse a different one. To test a new environment without overwriting an old one:

```bash
export LAB_VENV="$PWD/outputs/install_check_v1/venv"
bash scripts/setup_environment.sh
```

Use the same exported `LAB_VENV` for every subsequent command and Jupyter launch. Kernels are installed under that environment's prefix. Install paths should be absolute and readable by the intended accounts.

## Graphics backends

MuJoCo physics and policy inference are distinct from image rendering. Choose the backend before launching Python/Jupyter:

- `MUJOCO_GL=osmesa`: software rendering through the system `libosmesa6`; works with either CPU or CUDA training.
- `MUJOCO_GL=egl`: headless hardware rendering; requires a functional host EGL implementation and, for NVIDIA rendering, graphics libraries matching the installed NVIDIA kernel driver. A compute-only driver or `nvidia-smi` success is insufficient.

The wrapper does not discover or load graphics libraries from a developer home directory. Administrators should install the matching system driver through their normal distribution/driver-management process. If they intentionally supply a nonstandard graphics directory, they must configure `LD_LIBRARY_PATH` and EGL vendor selection explicitly before starting the lab. Never mix driver releases.

For an **existing Ubuntu host without root access**, the following optional OSMesa extraction obtains a public distribution package in the project. It does not install missing transitive system libraries; `ldd` must show no `not found` entries. Use administrator package installation if dependencies are missing.

```bash
mkdir -p outputs/osmesa_runtime_v1
cd outputs/osmesa_runtime_v1
apt-get download libosmesa6
for package in libosmesa6_*.deb; do dpkg-deb -x "$package" runtime; done
ldd runtime/usr/lib/x86_64-linux-gnu/libOSMesa.so.8
export LD_LIBRARY_PATH="$PWD/runtime/usr/lib/x86_64-linux-gnu${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
cd ../..
export MUJOCO_GL=osmesa
```

Record the downloaded package version in the deployment log. The system package depends on the OS release; Python and robotics dependencies remain fixed. This path was used for the current fresh-environment validation because the host did not have system NVIDIA EGL/OSMesa packages.

## 2. Prepare public data and reference evidence

From the repository root:

```bash
export MUJOCO_GL=osmesa
export LAB_DEVICE=cuda
export CUDA_VISIBLE_DEVICES=0
scripts/lab_python.sh scripts/download_dataset.py
scripts/lab_python.sh scripts/smoke_test.py --output outputs/instructor_smoke_v1
scripts/lab_python.sh scripts/prepare_reference.py --train --output checkpoints/reference_v1
export LAB_REFERENCE_ROOT="$PWD/checkpoints/reference_v1"
```

For CPU-only execution, use `LAB_DEVICE=cpu`. The download URL, HDF5 shape check and frozen SHA256 are in `scripts/download_dataset.py`. A successful download is made read-only. The existing-file path also verifies the hash; a partial file is never silently reused. Set `LAB_DATASET` before downloading to place it in an administrator-owned shared directory instead. The CLI also accepts `--output` for the dataset download and `--dataset` for training/evaluation.

Reference generation uses the existing fixed `configs/bc_reference.json`: three 512-unit layers, 400 epochs, seed 29, learning rate 0.0003. It is an instructor illustration, not the student architecture or an alternative student score. The script produces a checkpoint, real evaluation, videos and `reference_manifest.json`. Require `ready: true` and inspect the actual failure. If no failure exists, keep that outcome and prepare an explicitly attributed existing real failure; do not search seeds or fabricate evidence. A trusted existing compatible lab reference can instead be supplied with `--checkpoint`.

After preparation, make the shared dataset, reference and source environment readable but not writable by students. Each group needs its own writable notebooks (a separate checkout or copy), outputs and Jupyter runtime directory. Teachers must retain the authoritative source/configuration pins.

## 3. Assign accounts and output directories

Use existing JupyterHub authentication or separate Linux/SSH accounts. A `LAB_GROUP` string prevents accidental output collisions; it is not a security boundary. Six notebooks under one Unix account do not establish permission isolation.

For each group's account, set its assigned group and its own writable output root. Example for the first group, from its project checkout:

```bash
export LAB_GROUP=group_01
export LAB_OUTPUT_ROOT="$PWD/outputs"
export LAB_LOCK_DIR=/var/lock/manipulation-lab
scripts/lab_python.sh scripts/start_lab.py --group "$LAB_GROUP" --port 8892
```

Set `LAB_DATASET`, `LAB_REFERENCE_ROOT` and, if sharing a read-only environment, `LAB_VENV` to the administrator's actual deployment locations. These are deployment choices, not hardcoded developer paths. For an existing JupyterHub, configure the same variables in its spawner and select the installed lab kernel; follow the institution's authentication and TLS policy.

The standalone launcher uses loopback only, Jupyter's default token authentication, disables terminals, and fails on port conflict. Use SSH forwarding as shown in README. Do not set an empty token/password, bind an unauthenticated server to `0.0.0.0`, or publish a shared Jupyter login. Disabling terminals does not sandbox notebook Python.

## 4. Prepare shared resource locks

All accounts must point to the **same** `LAB_LOCK_DIR`. An administrator should create both lock files in advance with a shared course Unix group (example group name: `manipulation-lab`):

```bash
sudo groupadd -f manipulation-lab
sudo install -d -m 2770 -g manipulation-lab /var/lock/manipulation-lab
sudo touch /var/lock/manipulation-lab/training.lock /var/lock/manipulation-lab/evaluation.lock
sudo chgrp manipulation-lab /var/lock/manipulation-lab/*.lock
sudo chmod 660 /var/lock/manipulation-lab/*.lock
```

Add the institution's actual student accounts to this group using its normal account-management procedure, then start new login sessions. Verify each account can open both locks. Never delete or replace live lock files; processes could then lock different inodes. Processes release their advisory lock on exit. The code allows **one training job and one evaluation/replay job at a time**, with two CPU threads per job and a 900-second queue timeout. These two job types may overlap. Advisory locks are cooperative scheduling, not hard resource/security limits; use JupyterHub/container/cgroup limits where required.

## 5. Validate before class

Run the smoke test, inspect `preflight.json`, and run the full notebook/concurrency acceptance once with a NEW output path:

```bash
scripts/lab_python.sh -m pytest -q tests
scripts/lab_python.sh scripts/validate_classroom.py \
  --checkpoint "$LAB_REFERENCE_ROOT/instructor_reference.pth" \
  --output outputs/classroom_acceptance_v1
```

This launches six student processes concurrently, each executing all four notebooks with its own group output. It re-evaluates the supplied reference and records actual lock overlap, queue waits, memory usage, notebook completion and aggregated rows. It does not fabricate student answers: automated reports remain DRAFT. Test actual separate accounts, shared-file permissions, login/logout, SSH/JupyterHub access, quota recovery and browser playback separately with the institution's administrator. Do not promote the single-account process test to formal multi-user acceptance.

## 6. Recovery

If a job fails, retain its versioned directory and error log. Check RAM/VRAM, free disk, driver libraries and `preflight.json`. Fix the infrastructure cause, then use a new output path and record the reason for the rerun. Do not repeatedly train or change seeds to improve success rates. For a notebook kernel restart, rerun setup cells in that notebook; keep the current session from Notebook 01. Regenerate reports from existing checkpoints/evaluations when only presentation changes.

Stop only the affected server/process; do not kill unrelated GPU jobs or Jupyter services. Port conflicts are intentional errors. For a dataset hash failure, preserve the file for inspection and download to a new location. For a missing reference, run reference preparation, set `LAB_REFERENCE_ROOT`, and restart the affected kernel. See [troubleshooting](troubleshooting.md).
