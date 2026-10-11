# Course Packaging Acceptance — 2026-10-12

This record concerns the English course package and independent installation. Historical experiments in `validation.md`, `validation_metrics.json` and `teaching_acceptance_20261012.json` are retained. Actual run artifacts are excluded from Git; the [sanitized machine-readable record](course_acceptance_20261012.json) includes the runtime source hashes, measurements and evidence index.

## Protocol and provenance

The repository and both pinned official submodules were cloned from their public GitHub URLs into a new validation checkout. Current course changes were overlaid without copying the existing environment, dataset, checkpoints or experiment outputs. A new Python 3.12.13 environment installed the declared lock and editable packages; all 163 packages were compatible. Public Python/package caches were allowed. A separate public uv bootstrap was also tested in a local tool directory without changing the user's shell profile.

The public HDF5 dataset was downloaded again, rather than copied. It contains 200 episodes / 23,207 steps and matches SHA256 `3f2eb92e0a5025d0095e866ac16cc8092d6a762abe27dec90dbaff9027282962`. Imports for the lab, both robotics packages, torch, MuJoCo and nbclient all resolve inside the new checkout/environment. System site packages are disabled, and the registered notebook kernel points to that new interpreter.

The host is Ubuntu 22.04 x86-64. Rendering uses OSMesa from the public Ubuntu `libosmesa6` package, extracted into the validation checkout with its existing system-library dependencies checked by `ldd`. This avoids the former implicit developer-home NVIDIA library dependency. Full training uses the available NVIDIA GPU; CPU smoke runs hide all GPUs. This is a fresh Python environment on an existing Linux host, not a freshly provisioned operating system.

## Completed checks

| Check | Observed result |
|---|---|
| Dependency installation | 163 compatible packages; exact robotics/version pins and isolated kernel verified |
| Focused and fresh-environment tests | 13 passed; existing upstream deprecation warnings remain non-blocking |
| Public dataset download | SHA256 and HDF5 structure passed; no local dataset copy |
| CPU-only smoke | 57.42 s; 2 training epochs; checkpoint reload; 2 actual closed-loop rollouts; both unsuccessful placements retained |
| Explicit device selection | Additional bounded smoke with `LAB_DEVICE=cuda`, `--device cpu` and hidden GPUs passed in 50.85 s; actual training recorded CPU |
| Fresh reference generation | Fixed 400-epoch reference trained from public data; standard stable 4/5, shifted stable 2/5; real failure `standard_03` available |
| Jupyter access | Loopback only; unauthenticated API 403, token-authenticated API 200; four notebooks listed and server shut down cleanly |
| Negative cases | Missing environment/reference, absent CUDA and duplicate output fail explicitly; existing checkpoint hash preserved |
| Student entrypoints | English text and all six required teaching sections in each notebook; source cells parse; notebook outputs clean |
| Documentation | 15 shell blocks syntax checked; local links checked; actual install/download/smoke/reference/Jupyter commands exercised |

## Full classroom execution

The single six-process acceptance **passed**: 24 notebooks, 12 real 50-epoch student trainings, 120 student rollouts, 12 aggregate rows and six submission archives. The reference received an additional fixed 10-case classroom evaluation. Total classroom execution took 1024.81 seconds (17.1 minutes), including queues and report/export generation. Maximum queue wait was 543.07 seconds, below the 900-second timeout. At most one training and one evaluation/replay job held their respective shared slots. Peak summed process-tree RSS was 9.68 GiB; this sum includes shared pages and is not unique physical memory. Its protocol fixes student seed 17, 50 epochs, the existing three-layer 256-unit architecture, learning rates 0.001/0.0003, test seeds 101–105 and the same paired initial states. Six same-seed groups are not independent statistical replicates. No seed or model is selected after viewing test scores.


| Student variant | Learning rate | Selected epoch | Validation action MSE | Standard stable | Shifted stable |
|---|---:|---:|---:|---:|---:|
| lr_a | 0.001 | 7 | 0.03473111 | 2/5 | 3/5 |
| lr_b | 0.0003 | 11 | 0.03469041 | 5/5 | 5/5 |

All six groups obtained these same fixed-seed results. Both learning rates and every failed case were retained. Checkpoint selection used validation loss; no test result changed the primary variant or seed. The full run used CUDA for training and OSMesa for rendering. The separate CPU smoke checks are installation tests, not additional assignment replicas.

The saved demonstration-position plot, selected-epoch training curve and separate-axis failure plot were visually inspected. All 120 student videos were checked against their logged frame mapping and decoded at the first/last frame; each selected state's values were compared to the actual NPZ trace. Six ZIPs were checked for integrity, file SHA256 values and relative CSV paths. Generated report images resolve correctly and all automated reports retain DRAFT status. The class CSV uses the same schema as the template and student archives.

Reproduction commands are in [server setup](server_setup.md). Local detailed artifacts are under `outputs/course_acceptance_20261012_v1/`: public clone/install/download logs, CPU smoke runs, fresh reference training, executed notebooks, videos, raw state traces and group outputs. No original run was replaced.

## Preserved corrections and limitations

The first CPU smoke exposed an existing hardcoded `EGL GPU` string in evaluation metadata. Actual execution used OSMesa, as recorded by its launch environment and smoke manifest. Raw files and metrics were not edited. A correction record identifies affected files; subsequent evaluation summaries record the actual backend. A device-argument precedence issue in the new smoke wrapper was corrected and checked with the bounded CPU override test above.

The HTTP probe first encountered an occupied candidate port and then the host proxy. An unused loopback port and a proxy bypass were used for the probe; existing servers and Jupyter authentication settings were not changed. No training was repeated for these probe adjustments.

Not verified here: installation of OS packages with sudo on a clean machine; six distinct Unix accounts and cross-account permissions; institutional JupyterHub/SSH/TLS setup; interactive playback in each student's browser; and a full CPU-only classroom run on lower-resource hardware. Administrative shell commands were syntax-checked but not executed. A single-account concurrent process test does not establish multi-user security isolation. The 2–3 hour schedule includes student discussion and presumes instructor preparation; it is not a universal hardware runtime guarantee.

Automated notebook execution leaves written answers and the first-error annotation blank. Its reports must remain DRAFT. Tests of plotting/time alignment are engineering checks, not claims about the cause of a manipulation failure.
