# Linux Server Setup

This guide is for the instructor or administrator. Student instructions are in the root README. The supported target is Linux x86-64; Ubuntu 22.04 was used for acceptance. A fresh Python environment is tested separately from a clean operating-system installation. Consult [the current acceptance record](course_acceptance.md) for the exact verified scope.

## 1. Prepare the host

Use an existing institution-managed Linux server. Install `git`, `curl`, a C/C++ build toolchain, and the graphics packages listed in the README. The Python environment is pinned to Python 3.12.13, PyTorch 2.8.0, MuJoCo 3.2.7, robosuite 1.5.1 and robomimic 0.4.0. Source commit pins and the full transitive lock are version controlled. The project uses uv; it does not depend on Conda or another project's environment.

For six groups, provision at least 32 GB RAM and 30 GB free disk as a starting allocation, then measure on the actual host. Keep at least two CPU threads per active training/evaluation process. One CUDA-capable NVIDIA GPU is recommended for faster training; 8 GB of free VRAM is a practical starting allocation, not a measured minimum. Reserve a device using `CUDA_VISIBLE_DEVICES`. Do not evict unrelated workloads.

The default student interface is direct `.ipynb` execution in an IDE. After system prerequisites and uv are installed, `bash scripts/prepare_notebooks.sh --group group_01` performs the existing environment installation, dataset check/download, headless preflight and persistent per-group kernel registration. It starts no Jupyter HTTP server and requires no manual port tunnel. Use `--device cuda` only on a verified GPU host; default computation is CPU and rendering is OSMesa. Follow README Installation for prerequisites. The installer verifies the exact Python patch version and refuses to silently reuse a different one. To test a new environment without overwriting an old one:

```bash
export LAB_VENV="$PWD/outputs/install_check_v1/venv"
bash scripts/setup_environment.sh
```

The installer resolves uv once to an absolute executable path. It accepts `LAB_UV`, then searches PATH, `UV_INSTALL_DIR`, `XDG_BIN_HOME`, the XDG user bin directory, `~/.local/bin` and the legacy `~/.cargo/bin`. This works even when Bash startup replaces PATH. An invalid explicit `LAB_UV` is an error, not a silent fallback. Check discovery without installing anything:

```bash
LAB_UV="$HOME/.local/bin/uv" bash scripts/setup_environment.sh --check-uv
```

Use the same exported `LAB_VENV` for every subsequent command and Jupyter launch. Kernels are installed under that environment's prefix. Install paths should be absolute and readable by the intended accounts.

## Native runtime and preflight

Numba 0.61.2 and llvmlite 0.44.0 are explicitly pinned, consistent with the [Numba compatibility table](https://numba.readthedocs.io/en/0.61.2/user/installing.html). The lab defaults to `NUMBA_DISABLE_JIT=1` in the shell wrapper and package initialization **before** simulator imports. As documented by [Numba](https://numba.readthedocs.io/en/0.61.2/reference/envvars.html#envvar-NUMBA_DISABLE_JIT), this executes the original Python functions. It avoids the reported JIT compilation crash path; it does not diagnose an LLVM/driver/native-library root cause. CPU/GPU training settings, data and model architecture are unchanged. Measure simulation throughput on the deployment host again.

For an existing JupyterHub, also set `NUMBA_DISABLE_JIT=1` in the spawner environment so it applies before any preloaded library. Restart kernels after changing it. An administrator can explicitly set `NUMBA_DISABLE_JIT=0` before launch for host validation; never switch modes between the two controlled learning-rate runs.

```bash
export NUMBA_DISABLE_JIT=1
scripts/lab_python.sh scripts/preflight.py --output outputs/preflight_portable_v1
```

Preflight starts a fresh native worker with Python fault tracing. The parent writes `preflight.json` before launch and records pass/fail, exit signal, elapsed time and the last phase even if the worker crashes. `preflight_worker.log` holds its output/trace; `runtime.json` records effective JIT mode. CUDA probing follows the simulator reset/step/render check. This is a deliberate initialization sequence, not proof that import order alone fixes native crashes. A failed worker returns a nonzero exit status, with no automatic retry. Default timeout is 300 seconds; use `--timeout` for an intentionally slower host. Preserve failed runs and use a new output path after fixing the cause.

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

## Restricted-network dataset transfer

Choose one transport for the same official `low_dim_v15.hdf5`. All paths enforce SHA256 `3f2eb92e0a5025d0095e866ac16cc8092d6a762abe27dec90dbaff9027282962` and the 200-episode HDF5 structure. Existing files are checked without a network connection. No alternate dataset, automatic third-party mirror, or checksum bypass is used.

For a mirror, set `HF_ENDPOINT` to your administrator's actual endpoint before running the normal download command. It receives the same `/datasets/amandlek/robomimic/resolve/main/v1.5/can/ph/low_dim_v15.hdf5` path. `LAB_DATASET_URL` supplies a full URL instead; CLI `--url` has highest precedence. The downloader also respects standard `HTTPS_PROXY`/`HTTP_PROXY` and `NO_PROXY` variables through Python urllib. Do not put proxy credentials or signed links in committed configuration. Provenance omits URL credentials/query strings. Network operations time out after 120 seconds by default (`--timeout` overrides this).

For an offline transfer, on a connected computer run:

```bash
curl -fL --retry 2 -o low_dim_v15.hdf5 \
  'https://huggingface.co/datasets/amandlek/robomimic/resolve/main/v1.5/can/ph/low_dim_v15.hdf5?download=true'
sha256sum low_dim_v15.hdf5
scp low_dim_v15.hdf5 user@server:~/low_dim_v15.hdf5
```

Replace `user@server` with the assigned SSH destination. On the server, from the repository root:

```bash
scripts/lab_python.sh scripts/download_dataset.py --from-file "$HOME/low_dim_v15.hdf5"
```

The importer copies and validates the unchanged file, records provenance and makes the accepted copy read-only. Keep the original HDF5 bytes; rebuilding it from equivalent arrays changes its hash. A failed/corrupt partial is retained and never silently reused. After diagnosing a failure, choose a new `--output` path and set `LAB_DATASET` to it for later training. Missing sources and network failures include actionable recovery instructions. A mirror's reachability is a deployment check, not guaranteed by this repository.

## 3. Assign accounts and output directories

Use existing JupyterHub authentication or separate Linux/SSH accounts. A `LAB_GROUP` string prevents accidental output collisions; it is not a security boundary. Six notebooks under one Unix account do not establish permission isolation.

For each group's account, set its assigned group and its own writable output root. Example for the first group, from its project checkout:

```bash
export LAB_GROUP=group_01
export LAB_OUTPUT_ROOT="$PWD/outputs"
export LAB_LOCK_DIR=/var/lock/manipulation-lab
bash scripts/prepare_notebooks.sh --group "$LAB_GROUP" --device cpu
```

Set `LAB_DATASET`, `LAB_REFERENCE_ROOT` and, if sharing a read-only environment, `LAB_VENV` to the administrator's actual deployment locations. These are deployment choices, not hardcoded developer paths. For an existing JupyterHub, configure the same variables in its spawner and select the installed lab kernel; follow the institution's authentication and TLS policy.

For the default IDE workflow, each group opens its own checkout locally on Linux or through VS Code Remote - SSH, installs Python/Jupyter extensions on the execution host, and selects the exact configured kernel label printed by preparation. The kernelspec persists the approved lab paths, group, device and rendering settings; terminal exports alone do not reconfigure an existing editor kernel. Register under each actual student account. Rerunning with different settings creates a separate kernel instead of overwriting another group's entry. No SSH `-L` command or Jupyter web-server address is needed.

Use `scripts/lab_python.sh scripts/prepare_notebooks.py --group "$LAB_GROUP" --device cpu --render-backend osmesa` to register/check a group against a previously installed read-only environment without reinstalling it. Each account still needs writable output and user kernel-registration directories. `LAB_OUTPUT_ROOT` selects where its setup records and experiment outputs are written. The teacher prepares the reference once; preparation reports missing reference evidence without inventing a failure.

Existing institution-managed JupyterHub deployments may continue to use their authenticated interface. The optional `start_lab.py` launcher retains loopback-only binding, token authentication, disabled terminals and fixed-port behavior. Do not bind an unauthenticated server to a public interface. The direct IDE workflow does not use this launcher.

### Optional Jupyter server runtime files and root containers

The launcher automatically uses `/tmp/manipulation-lab-jupyter-<effective UID>` instead of placing runtime files on a shared home/data mount. It verifies directory ownership and `0700` access permissions (also accepting Jupyter's sticky-bit `1700` on restart), rejects symlinks, and probes file creation with exact `0600` mode before starting Jupyter. These follow [Jupyter runtime and secure-write requirements](https://jupyter-core.readthedocs.io/en/latest/api/jupyter_core.html). Notebook files and experiment outputs stay in their configured project directories. The launcher removes `JUPYTER_ALLOW_INSECURE_WRITES`; it never bypasses secure writes.

If setting `JUPYTER_RUNTIME_DIR` explicitly, choose a local filesystem that supports those permissions. For a fresh private directory:

```bash
export JUPYTER_RUNTIME_DIR="$(mktemp -d /tmp/manipulation-lab-jupyter.XXXXXXXX)"
scripts/lab_python.sh scripts/start_lab.py --group "$LAB_GROUP" --port 8892
```

An unsafe existing directory is rejected rather than chmodded behind your back. In JupyterHub, configure each user's private runtime directory in the spawner; do not share it between users. Runtime files are temporary: after a reboot, restart Jupyter and retrieve its new token. Do not delete connection files while kernels are running.

Inside a root container, the launcher adds `--allow-root` only when effective UID is 0. Loopback binding, token authentication and fixed-port behavior remain in place. A root kernel executes as root, so this option is container compatibility, not multi-user isolation; use ordinary separate accounts or the institution's managed isolation for students.

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
