# Deployment portability validation — 2026-10-12

The deployment fixes passed a fresh Python installation, real CPU training/evaluation, official dataset transport checks, and authenticated Jupyter/kernel execution. The original server's native JIT crash has not been reproduced here; disabling JIT is a compatibility default, not a diagnosed LLVM fix.

## Changes and causes

| Reported issue | Fix | Verification |
|---|---|---|
| Numba/llvmlite JIT segfault; initialization order affects execution | Retain Numba 0.61.2 / llvmlite 0.44.0; explicitly pin and report both. Set `NUMBA_DISABLE_JIT=1` before native imports. Preflight isolates native work, delays CUDA probing, and preserves failure diagnostics | Actual reset/step/render and CPU smoke passed; JIT-on fixed-case preflight also passed on this host. An intentional infrastructure SIGSEGV fixture verifies signal/log/phase reporting |
| Root Jupyter launch rejected | Add `--allow-root` only for effective UID 0 | Actual root-namespace Jupyter and kernel executed with UID 0; authentication retained |
| Shared storage cannot enforce connection-file permissions | Default runtime to local `/tmp/manipulation-lab-jupyter-<UID>`; verify owner, directory access 0700 and files 0600; accept Jupyter's additional sticky bit | Both real kernels used private connection files; unsafe directory/file-mode fixtures rejected; insecure-write bypass removed |
| Bash resets PATH and cannot find uv | Resolve uv to an absolute executable path using `LAB_UV`, PATH and standard installer directories | Fresh environment installed with PATH restricted to `/usr/bin:/bin`; 163 packages compatible |
| Server cannot reach Hugging Face | Add explicit URL/endpoint/proxy and offline-copy transports with unchanged hash/schema checks | Official 46,889,752-byte file accepted through offline copy and a loopback HTTP endpoint; corruption and partial-file preservation tested |

## Measured results

The new environment uses Python 3.12.13 and the existing pinned dependency lock. The installer used public package caches on the existing Linux host. OSMesa uses the previously verified public Ubuntu package extraction described in [server setup](server_setup.md). This is not a clean-OS or fully offline Python installation.

The complete test suite passed **22 tests in 6.56 s** with 14 dependency deprecation warnings. The deployment subset passed **9 tests** again after the sticky-bit correction; unrelated experiments were not repeated.

One genuine CPU smoke took **52.75 s**: data parsing, native preflight, two training epochs, a saved/reloaded student checkpoint, and standard/shifted closed-loop rollouts with videos. GPUs were hidden. Both cases had environment success and stable-placement success **0/1**. These failures are retained, and no seed was changed. Smoke acceptance checks functioning execution, not a capable final policy.

A separate JIT-enabled preflight completed in **6.33 s** using the same three fixed state/action inputs. Restored-observation error summaries matched the JIT-disabled run; the largest difference between their recorded one-step error summaries was **1.37e-12**. This is a check of those inputs and summaries, not proof of bitwise equivalence for arbitrary trajectories or a reproduction of the user's server crash.

Ordinary-user and root-namespace launches each returned **HTTP 403 without a token**, **HTTP 200 with a token**, listed all four notebooks, and started a real kernel through the authenticated API (HTTP 201). Each kernel executed code, reported the expected effective UID and disabled JIT, and had no insecure-write bypass. Connection files were `0600`; runtime directories became `1700` after Jupyter added a sticky bit, preserving owner-only access.

## Preserved failure and correction

The first Jupyter integration check failed after kernel creation because `jupyter_client/connect.py` adds a sticky bit to the runtime directory. The initial exact `0700` check would also reject the next launch. The fix accepts `0700` access plus that sticky bit, while still rejecting group/other access, symlinks, wrong owners and non-0600 files. The failed check and private log remain in the original artifact directory; the corrected Jupyter acceptance is in `jupyter_v2`. No training or evaluation was repeated for this correction.

## Evidence and reproduction

Machine-readable results and source hashes: [deployment_validation_20261012.json](deployment_validation_20261012.json). Raw logs, the new environment, official data copies, checkpoint, videos and JSON are retained locally under `outputs/deployment_portability_20261012_v1/` and excluded from Git. Jupyter logs are private because they may contain tokens; they are not published.

Run from the repository root, with the graphics backend configured as in [server setup](server_setup.md):

```bash
# Verify uv discovery even with a reduced PATH.
PATH=/usr/bin:/bin bash scripts/setup_environment.sh --check-uv

# Default JIT-disabled path; choose a new output for every diagnostic run.
export NUMBA_DISABLE_JIT=1
scripts/lab_python.sh scripts/preflight.py --output outputs/deployment_preflight_v1
scripts/lab_python.sh scripts/smoke_test.py --device cpu --output outputs/deployment_smoke_v1
scripts/lab_python.sh -m pytest -q tests
```

The installer and [dataset transfer instructions](server_setup.md#restricted-network-dataset-transfer) contain the commands for a new environment and restricted network. Keep both learning-rate variants on the same runtime settings. Restart existing Jupyter servers/kernels after changing JIT settings.

## Verification boundaries

- The original server's native JIT failure and initialization-order dependence remain unverified locally. Logs from that host are needed to identify the underlying native-library cause.
- Root testing used effective UID 0 inside an unprivileged user namespace; unrestricted host-root and institution-specific container configurations were not tested.
- Permission rejection was tested with controlled filesystem-mode fixtures and a shared-data-directory override, not the affected remote mount itself.
- Official bytes were served through a local HTTP endpoint. Public mirror/proxy reachability on the affected server is not established; offline import remains available.
- This task did not repeat the full four-notebook, six-group classroom run or remeasure its 2–3 hour schedule. The earlier [course acceptance](course_acceptance.md) remains a historical record from before the JIT-default change. Measure classroom throughput on the final deployment host.
- robosuite, robomimic, MuJoCo, task, dataset bytes, model architectures, training seeds and evaluation rules are unchanged. No performance result was selected by repeated training.
