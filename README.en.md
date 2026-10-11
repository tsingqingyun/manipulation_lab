# Manipulation Learning Lab

**Language / 语言:** [简体中文](README.md) | English

## Learning Robot Manipulation from Demonstrations

### 1. Overview

Teach a simulated Panda arm to pick up a can and place it in its target bin using human demonstrations. You will inspect the data, train two behavior cloning policies, compare matched evaluation cases, and explain a real failure using video and logged state.

**Audience:** graduate students with basic Python and machine-learning knowledge. **Time:** 2–3 hours after the instructor has prepared the server, dataset and reference evidence. Installation and downloads are separate from class time. No robotics hardware is required.

The lab uses the existing **robosuite + robomimic + MuJoCo** pipeline. It does not require another project, an existing Conda environment, or a downloaded private model. All reported experiment metrics come from training and simulation.

### 2. Learning Objectives

By the end, you should be able to:

- Inspect a demonstration dataset and distinguish observations from actions.
- Explain behavior cloning (BC): predicting expert actions from observations.
- Train a policy and select a checkpoint using validation episodes.
- Explain closed-loop inference: observing again after every action.
- Design a controlled comparison and interpret evaluation and generalization limits.
- Locate a failure in a video and state trace, separating observations from hypotheses.

### 3. Task Description

The task is **robosuite PickPlaceCan**, with a **Panda** arm and a parallel gripper. The official robomimic **v1.5 Can / proficient-human / low-dimensional** dataset contains 200 human demonstrations and 23,207 control steps. The fixed whole-episode split is 160 training / 20 validation / 20 test. Test data never selects model weights.

| Quantity | Meaning |
|---|---|
| Policy observation: 16 values | End-effector world position (3), xyzw quaternion (4), two gripper joint positions (2), can world position and xyzw quaternion (7) |
| Action: 7 values | World translation increment (3), axis-angle rotation increment (3), gripper command (1) |
| Coordinate and action units | World frame, Z upward; positions in meters; actions normalized to [-1, 1], translation limit ±0.05 m and rotation limit ±0.5 rad |
| Gripper command | Positive closes; negative opens. Command is unitless; measured opening is in meters |
| Timing | 20 Hz control steps. No acquisition timestamps are invented |
| Student model | Existing deterministic BC multilayer perceptron, three 256-unit hidden layers; observation normalization uses training data only |

The unchanged observation adapter uses `object[7:14]` from the dataset's 14-value object vector. This avoids a known cached relative-sensor inconsistency when restoring states and keeps training and inference inputs consistent.

We report both the environment's success flag and **stable released placement**: the can is within the target region with a radius margin, the gripper is open and no longer touching it, and continued policy execution maintains displacement ≤0.01 m and speed ≤0.05 m/s for 20 control intervals (1 second). See [the exact thresholds](configs/evaluation.yaml). This is a classroom placement criterion, not a proof that every point of an arbitrarily oriented object mesh is inside the bin.

The **Position Shift Test** adds 0.04 m along world X to matched test starts that remain inside the source bin. It is **not a certified out-of-distribution (OOD) benchmark**. Position shifts can overlap training support, and a 2D position plot does not establish the full input distribution.

### 4. Installation

Run commands from the repository root unless stated otherwise. Linux x86-64 is the tested platform. Allow at least 15 GB free disk for Python/CUDA dependencies and outputs. A class server needs additional storage per group; see [server setup](docs/server_setup.md).

An administrator installs system prerequisites on Ubuntu 22.04/24.04:

```bash
sudo apt-get update
sudo apt-get install -y git curl build-essential libosmesa6 libgl1 libegl1 libglib2.0-0
```

OSMesa renders without a display or GPU. NVIDIA EGL rendering is also supported when the host has the matching graphics driver libraries; CUDA availability alone does not prove rendering works. See [graphics setup and the no-root alternative](docs/server_setup.md#graphics-backends).

Clone the source and install `uv`, the Python environment manager:

```bash
git clone --recurse-submodules https://github.com/tsingqingyun/manipulation_lab.git
cd manipulation_lab
curl -LsSf https://astral.sh/uv/install.sh | sh
export PATH="$HOME/.local/bin:$PATH"
bash scripts/setup_environment.sh
```

The installer creates `.venv`, obtains Python 3.12.13, installs [the full dependency lock](requirements.lock.txt), checks dependencies, and registers the **Manipulation Lab (Python 3.12)** notebook kernel. It installs both official source submodules at their pinned commits. Do not upgrade them during the assignment.

| Component | Fixed version |
|---|---|
| Python | 3.12.13 |
| PyTorch / torchvision | 2.8.0 / 0.23.0 |
| MuJoCo | 3.2.7 |
| robosuite | 1.5.1, pinned Git commit |
| robomimic | 0.4.0, pinned Git commit |
| NumPy | 1.26.4 |

Exact source commits and the observation contract are in [configs/environment.yaml](configs/environment.yaml). MuJoCo is installed by pip; no separate license key or MuJoCo download is required.

Choose the compute device **before starting Jupyter**. The same locked PyTorch distribution runs on CPU; the CPU path still downloads its CUDA dependencies. It does not require a GPU or CUDA toolkit for CPU execution.

```bash
# Portable CPU computation and software rendering:
export LAB_DEVICE=cpu
export MUJOCO_GL=osmesa

# On a configured NVIDIA server, use these instead for training:
# export LAB_DEVICE=cuda
# export CUDA_VISIBLE_DEVICES=0
# Keep MUJOCO_GL=osmesa, or select egl after the instructor verifies NVIDIA EGL.
```

CPU runs use two threads per job. They are functional, but the 2–3 hour teaching schedule depends on the server and queue; instructors should time their deployment in advance. GPU training needs a driver compatible with PyTorch's CUDA 12.8 wheels. Evaluation policy inference and MuJoCo physics run on CPU; `MUJOCO_GL` selects the rendering backend independently.

Download and verify the public dataset, then run a **real installation smoke test**:

```bash
scripts/lab_python.sh scripts/download_dataset.py
scripts/lab_python.sh scripts/smoke_test.py --output outputs/smoke_v1
```

The download verifies the fixed SHA256 and 200-episode HDF5 structure. The smoke test checks dependency versions, CUDA availability, a headless reset/render, dataset parsing, two real training epochs, checkpoint reload, and one standard + one shifted closed-loop rollout with videos. Expect `PASS` and `outputs/smoke_v1/smoke.json` with `passed: true`. Zero successful placements can still pass this installation test; it is not the assignment budget. Use a **new output name** for a diagnostic rerun and preserve the failed run.

The reference checkpoint is **not distributed with Git**. The instructor generates it from the same public dataset using the fixed reference configuration:

```bash
scripts/lab_python.sh scripts/prepare_reference.py --train --output checkpoints/reference_v1
export LAB_REFERENCE_ROOT="$PWD/checkpoints/reference_v1"
```

This trains the existing reference model, evaluates it and checks for a real failure video. Do this before class. If no real failure is available, preparation fails explicitly; never manufacture one or search seeds for a desired result. [Instructor instructions](docs/instructor_guide.md) explain the reference's separate role.

### 5. Getting Started

On a prepared course server, skip installation and use your instructor's account, group and access instructions. For your own installation:

```bash
export LAB_GROUP=group_01
scripts/lab_python.sh scripts/start_lab.py --group "$LAB_GROUP" --port 8892
```

Jupyter listens on **127.0.0.1**, with normal Jupyter token authentication. From your laptop, forward the port (replace the SSH destination with your assigned login):

```bash
ssh -N -L 8892:127.0.0.1:8892 user@server
```

Open `http://127.0.0.1:8892/lab` locally and use the token from your server startup log. Never publish that token. If port 8892 is already occupied, use an assigned free port in both commands; the launcher will not silently switch ports. Multi-user courses should use the institution's authenticated JupyterHub or separate SSH/system accounts.

Open these notebooks in order and select the lab kernel:

1. [01_demonstrations.ipynb](notebooks/01_demonstrations.ipynb) — start a session and play a demonstration.
2. [02_train_policy.ipynb](notebooks/02_train_policy.ipynb) — run both learning rates and save actual models/evaluations.
3. [03_policy_evaluation.ipynb](notebooks/03_policy_evaluation.ipynb) — inspect those same matched results.
4. [04_failure_analysis.ipynb](notebooks/04_failure_analysis.ipynb) — select steps, mark an error, answer questions and export evidence.

Notebook 01 creates a new timestamped group session. Notebooks 02–04 find that session and its previous-stage outputs automatically. Rerunning a training or analysis stage creates a new version and keeps the old one. To revise written answers, rerun only the answer cells and the final report/export cells. Do not restart Notebook 01 halfway through the assignment.

### 6. Experiments

| Part | Work | Planned class time |
|---|---|---:|
| 1: Understanding Demonstrations | Inspect observations/actions, play recorded states, inspect initial positions, answer Q1 | 20 min |
| 2: Training a BC Policy | Compare learning rates 0.001 and 0.0003 with the same data, network, initialization seed 17, 50 epochs and batch size; save both curves/checkpoints; answer Q2–Q3 | 50–60 min |
| 3: Policy Evaluation and Generalization | Compare 5 standard + 5 shifted cases per model; inspect paired cases, positions and videos; answer Q4 | 40–50 min |
| 4: Failure Analysis | Inspect a real failure, choose at least 3 control steps, mark the first observable error, answer Q5, export evidence | 20–30 min |

Only learning rate changes in the mandatory comparison. The code checks identical initial weights, data splits, dependency versions and evaluation manifests. Each checkpoint is selected using validation loss. The primary variant `lr_a` is fixed before testing. Retain both outcomes, including low success rates. Repeated runs with the same seed are not independent samples.

### 7. Visualization

Every plot, log and video is saved automatically in the group's run directory:

| Evidence | Where to look |
|---|---|
| Human interaction video, observation/action information, initial-position scatter | Notebook 01, `demonstration_*` directory |
| Training/validation losses, selected epoch, configuration, two-rate comparison | Notebook 02, `experiment_*/lr_a` and `lr_b`, plus `learning_rate_curves.png` |
| Rollout videos, success fractions, per-episode and paired results, actual test starts | Notebook 03, each variant's `evaluation` directory |
| Failed rollout, robot/object trajectories, gripper opening and command on separate axes | Notebook 04, `analysis_*` directory |
| Selected frames and exact requested-step state, first-error annotation | `observed_facts.json`, `keyframe_*.png`, `failure_analysis.json` |

Videos are sampled after every fourth action; state zero has no exact video frame. Selected frames identify the requested step, actual recorded step and offset. State values are from the exact requested step. All positions use world-frame meters, commands use normalized units, and time uses 20 Hz control indices. A first-error marker is a student's observation, not an automatic causal diagnosis.

### 8. Assignment Questions

1. **Q1:** What observations and actions are used in this task?
2. **Q2:** How does behavior cloning learn from demonstrations?
3. **Q3:** Does a lower training loss always result in better manipulation performance?
4. **Q4:** How does changing the initial object position affect the learned policy?
5. **Q5:** Identify one failure and propose a possible improvement.

Use your own results and distinguish evidence, hypotheses and limitations. Detailed prompts are in [the student assignment](docs/assignment_student.md).

### 9. Submission Requirements

Each group submits a **1–2 page PDF report** answering Q1–Q5, plus the evidence ZIP generated by Notebook 04. Include both training configurations and loss curves, both checkpoints, evaluation metrics/configurations/case manifests, a representative rollout, and annotated failure keyframes. The generated Markdown report is an evidence appendix; it does not replace your written discussion.

Blank answers keep the generated report marked **DRAFT**. A completed execution is not proof that student answers are complete or correct. Download the ZIP from Jupyter's file browser. It contains the shared `class_results.csv` schema used by the teacher. Keep the original run directory until grading is complete.

### 10. Grading Rubric

| Area | Points | Evidence assessed |
|---|---:|---|
| Demonstration Understanding | 20 | Correct observations/actions, units, playback and split interpretation |
| Policy Training & Experiment | 25 | Both real runs, controlled variables, curves/configurations/checkpoints and Q2–Q3 |
| Policy Evaluation | 30 | Matched standard/shifted cases, complete metrics/videos, position coverage and justified limits |
| Failure Analysis & Discussion | 25 | Real failure, first observable error, supporting state/frames, hypothesis and improvement |
| **Total** | **100** | Completion, reproducibility and reasonable analysis |

**Success rate itself does not determine your grade.** A well-documented failure can receive full credit. See the [detailed rubric](docs/assignment_student.md).

### 11. Troubleshooting

- **Kernel/import missing:** run the installer and choose the lab kernel; do not use another project's Python.
- **Dataset missing or hash mismatch:** run the downloader; preserve the reported file and investigate rather than bypassing the check.
- **CUDA unavailable:** explicitly start with `LAB_DEVICE=cpu`; the same choice applies to both variants.
- **Headless rendering error:** verify OSMesa or the NVIDIA EGL graphics libraries, not just `nvidia-smi`.
- **Reference missing:** the instructor must generate it before class; if a student's primary policy has no failure, Notebook 04 needs real reference evidence.
- **Output already exists:** choose a new versioned directory. **Queue wait:** leave the cell running; jobs share one training and one evaluation slot.

See [troubleshooting](docs/troubleshooting.md) and [measured acceptance and limits](docs/course_acceptance.md).

### 12. References and Acknowledgements

This lab builds on [robomimic](https://robomimic.github.io/), [robosuite](https://robosuite.ai/) and [MuJoCo](https://mujoco.org/). The demonstration download follows the [official robomimic dataset documentation](https://robomimic.github.io/docs/datasets/robomimic_v0.1.html) and its public Hugging Face distribution. The training algorithm is the [official robomimic BC implementation](https://github.com/ARISE-Initiative/robomimic/blob/v0.4.0/robomimic/algo/bc.py). We train compatible lab models instead of mixing older model-zoo weights with this environment. Dependency installation references: [uv](https://docs.astral.sh/uv/getting-started/installation/), [PyTorch 2.8 wheels](https://pytorch.org/get-started/previous-versions/), [MuJoCo Python](https://mujoco.readthedocs.io/en/stable/python.html). See [LICENSE](LICENSE); upstream code and data retain their respective licenses and attribution.

### Project Layout and Configuration

`notebooks/`, `src/`, `scripts/`, `configs/`, `tests/` and `docs/` are maintained source. `third_party/` contains the two pinned upstream submodules. `.venv/` is generated by installation; `data/` by download; `checkpoints/reference_v1/` by instructor preparation; and `outputs/` by experiments. Large generated files are excluded from Git. The instructor must prepare the environment, shared dataset, real reference evidence and account/resource setup before class.

| Environment variable | Default / purpose |
|---|---|
| `LAB_VENV` | Project `.venv`; use an absolute path for an alternate environment |
| `LAB_DATASET` | Project `data/low_dim_v15.hdf5`; optional shared read-only HDF5 |
| `LAB_DEVICE` | Config default `cuda` for full training; explicitly set `cpu` or `cuda` |
| `MUJOCO_GL` | Wrapper default `egl`; set `osmesa` for software rendering |
| `LAB_GROUP` | `group_01`; assigned identities `group_01` through `group_06` |
| `LAB_OUTPUT_ROOT` | Project `outputs`; group/session directories are created below it |
| `LAB_REFERENCE_ROOT` | Project `checkpoints`; directory containing `reference_evaluation/` |
| `LAB_LOCK_DIR` | `/tmp/manipulation-learning-lab-locks`; all groups must share the same administrator-prepared directory |

The [instructor guide](docs/instructor_guide.md) covers aggregation and next-day discussion. [Server setup](docs/server_setup.md) covers deployment, accounts, concurrency and recovery.
