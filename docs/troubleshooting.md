# Troubleshooting

Run commands from the repository root using `scripts/lab_python.sh`. Preserve the failed output and use a new directory for a justified rerun. Never change seeds to improve a displayed success rate.

| Symptom | Check and recovery |
|---|---|
| `uv` not found | Install uv as in README and add its installation directory to PATH before setup |
| Python version mismatch | Set `LAB_VENV` to a NEW absolute directory and rerun setup; do not overwrite an unrelated environment |
| Optional robosuite warning | Messages about private macros, extra robot models or whole-body IK do not block the configured Panda OSC_POSE task. Do not install another architecture to suppress them; inspect actual exceptions and smoke results |
| Missing lab import/kernel | Run setup; choose **Manipulation Lab (Python 3.12)**. Launch Jupyter through the wrapper with the same `LAB_VENV` |
| Dataset absent | Run `scripts/lab_python.sh scripts/download_dataset.py`; ensure `LAB_DATASET` is the intended location |
| Dataset hash or partial-file error | Retain the unexpected file, inspect download/network errors, and download to a new location; do not bypass SHA256 |
| `libOSMesa` missing | Install system `libosmesa6`, or use the documented public-package extraction and verify all `ldd` dependencies in server setup |
| EGL initialization fails | Verify matching graphics libraries and EGL vendor configuration. CUDA/nvidia-smi alone is insufficient. Use documented OSMesa rendering if available |
| CUDA is unavailable | Explicitly export `LAB_DEVICE=cpu` before Jupyter. Both learning-rate runs must use the same device |
| GPU out of memory | Check unrelated workloads and the assigned device. Release only your affected process, retain its logs, fix allocation and use a new run |
| Missing previous stage | Complete Notebook 01 then 02 using the same group/output root. Restarting Notebook 01 changes the current session |
| Long-running cell | Training/evaluation may be queued. The server permits one job of each kind. Inspect queue/resource logs before interrupting |
| Lock permission denied | Ask the administrator to prepare the same lock directory/files and shared group for all accounts; never delete live lock files |
| Output already exists | Intentional preservation. Supply a new versioned output path |
| Missing success/failure video | No episode of that type occurred. Use actual per-episode videos; do not invent results |
| Missing instructor reference | Instructor runs `prepare_reference.py --train --output checkpoints/reference_v1`, exports `LAB_REFERENCE_ROOT`, and restarts affected kernels |
| Report remains DRAFT | Fill Q1 and reflection, Q2–Q4, the four failure fields, and `FIRST_ERROR_STEP`; rerun answer and report/export cells |
| Video/frame does not match selected step exactly | Video is sampled every four post-action steps. Check the recorded step and offset; logged state is from the exact requested step |
| Jupyter port occupied | Use an assigned free port on both server launch and SSH forwarding. Do not stop another user's server |
| Browser cannot connect | Keep SSH tunnel open, check loopback port, then use your Jupyter token. Do not disable authentication |
| CSV command exits nonzero | The CSV retains invalid/missing rows. Read `status`/`error`; do not treat blank metrics as zero success |

For an isolated version/reset/render check:

```bash
scripts/lab_python.sh scripts/preflight.py --output outputs/diagnostic_v1
```

Inspect its `preflight.json`, saved render and recorded versions. The broader `smoke_test.py` also trains, loads a checkpoint and executes actual rollouts. Neither test proves a high-quality policy or a fully isolated multi-user deployment.
