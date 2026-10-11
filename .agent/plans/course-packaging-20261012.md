# Package the existing pipeline as an independently deployable graduate lab

This living plan follows `.agent/PLANS.md`. Behavior cloning (BC) means learning expert actions from recorded observations. A checkpoint stores the learned model. Headless rendering creates simulation images without a desktop.

## Goal and observable outcome

A new student can follow the English README, install from public resources, run four notebooks, compare two fixed learning rates, inspect real videos and state logs, and submit reproducible evidence with a short report in a planned 2–3 hour class. Preserve the task, dataset, architecture, algorithm, seeds, and previous outputs.

## Progress

- [x] 2026-10-12: recorded clean main at a2c58a7c606794233cdc1f24523ae11f29197788 and origin tsingqingyun/manipulation_lab; inspected installation, notebooks, reporting and public dependency pins.
- [x] 2026-10-12: made venv/data/device/graphics inputs explicit; added real smoke testing, reference training and evidence export.
- [x] 2026-10-12: completed English README, assignment/rubric, instructor/server/troubleshooting guides and all four structured notebooks; saved demonstration plots and exact selected-step state.
- [x] 2026-10-12: fresh-environment acceptance passed: 13 tests, 24 notebooks, 12 real student trainings, 120 student rollouts, six verified ZIPs, 12 class rows and authenticated loopback Jupyter. Classroom duration 1024.81 s; queue max 543.07 s; summed process RSS peak 9.68 GiB.
- [x] 2026-10-12: restored full filesystem access and wrote final acceptance records to the target checkout; verified all runtime-source hashes against the tested source.
- [x] 2026-10-12: reviewed the complete course change and prepared an explicit file list for publication to origin/main. The final delivery reply records the commit identifier and remote verification result.

## Discoveries

The old wrapper implicitly reads graphics libraries from the developer home directory. The host has Mesa EGL but no system NVIDIA EGL or OSMesa library. A Python-only install cannot supply the system graphics driver. The original notebooks were mostly Chinese and did not save demonstration figures. Both issues are now addressed. Existing six-process validation does not establish separate-user permissions or JupyterHub authentication. The fresh CPU smoke exposed an old hardcoded EGL label in evaluation metadata; subsequent evaluations now record the actual MUJOCO_GL backend. Earlier raw results are retained with a correction note, without changing metrics. The HTTP authentication test initially hit a local port conflict and then the host proxy; an unused loopback port and explicit proxy bypass allowed the actual authentication check, without changing the Jupyter service security settings.

## Decisions

2026-10-12: keep the existing uv lock and pinned Git submodules, add an explicit environment path and device override, and remove implicit home-directory driver discovery. Describe supported system graphics packages and an explicit no-root Mesa installation path. Validate using public packages, never a copied private checkpoint. Separate automatic execution acceptance from student-written answers and real multi-user server acceptance.

## Concurrent workspace activity

During validation, a separate `presentations/` directory and `.agent/plans/assignment-presentation-20261012.md` appeared. They are not part of this task. Preserve them, do not read unrelated content, and exclude them from staging and the source manifest. Recheck branch/index state before publishing.

## Current outcome

Fresh public checkout and a second isolated Python environment installed successfully (163 compatible packages). Public dataset downloaded and SHA256 verified. CPU-only smoke completed in 57.42 seconds with two actual unsuccessful rollouts retained. All 13 tests passed in the fresh environment. Authenticated loopback Jupyter returned 403 without a token and 200 with a token; all four notebooks were listed. Fresh reference generation and full classroom acceptance passed. The reference trained 400 epochs in 50.41 s and supplied a real failure. All videos, requested-state mappings, report links and submission hashes passed. A temporary read-only session scope delayed publication. Full access was subsequently restored, final records were written back, and the already-tested runtime source hashes matched. No experiment was rerun or result changed during publication. Original experiments remain read-only.

## Context and implementation

The checkout is the standalone `manipulation_lab` Git repository. `src/manipulation_lab` already implements real robomimic BC, fixed episode splits, stable placement evaluation, paired position shifts, reporting and class aggregation. `scripts` contains public entrypoints; notebooks call these in separate processes. Add only installation, teaching, reporting and validation glue. Update `README.md`, student assignment, instructor guide, server setup and troubleshooting in English. Add exact-state information alongside the nearest recorded keyframe; keep units and time indices distinct.

## Execution and acceptance

From the repository root, run `scripts/lab_python.sh -m pytest -q tests` for relevant contracts. Install the working source in a new isolated checkout and fresh venv using `bash scripts/setup_environment.sh`. Download the public dataset and verify its frozen SHA256. Run `scripts/smoke_test.py` with a new output path; expect finite losses, a reloadable checkpoint, actual MP4/NPZ rollouts and zero runtime errors, with no minimum success rate. Generate the reference from `configs/bc_reference.json`. Execute all four notebooks for six queued groups through `scripts/validate_classroom.py`; expect 24 executed notebooks, 12 trained models, fixed evaluation manifests and 12 aggregate rows. Check notebook images, videos, report draft labels, all student English text, authentication on loopback, and README command entrypoints. A new Python environment on this host is not a clean operating-system installation. Missing administrator/multi-user checks must remain explicitly unverified.

## Recovery and artifacts

All execution outputs use new versioned directories under ignored `outputs/` or a new isolated validation checkout. Never delete previous runs or repeat seeds to improve outcomes. Interrupted runs and logs remain available; targeted software-fix checks may reuse existing trained models. Publish only source, English documentation and sanitized acceptance records, not datasets, credentials, model weights or large experiment artifacts.

## Interfaces and dependencies

Preserve `train.py`, `evaluate.py`, the fixed dependency lock, both pinned official submodules, and current class CSV schema. Environment variables select dataset, venv, device, output root and shared reference directory. The smoke test and reference generation must use these same public entrypoints. No new learning architecture or external service is required.

## Publication status

Filesystem access was restored on 2026-10-12. Final acceptance documents are now in `docs/course_acceptance.md` and `docs/course_acceptance_20261012.json`. The preserved validation root is `outputs/course_acceptance_20261012_v1`; it includes the independent public checkout, new environment, downloaded dataset and all original run evidence. Temporary handoff files remain preserved. All runtime source hashes match the completed acceptance, so publication requires no repeated training or evaluation.

Before publication, local HEAD and origin/main were both `50cc9c13b5ab91fbb95fccf85a2539605ab97888`, with an empty index. Separate presentation work remains outside this task's staging scope. This plan records the completed implementation and validation; Git history and the final delivery reply record publication and remote verification.
