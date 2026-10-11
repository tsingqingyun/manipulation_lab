# Fix deployment startup across Linux server environments

This living ExecPlan follows [../PLANS.md](../PLANS.md).

## Goal and observable outcome

In `/home/jingchen/projects/manipulation_lab`, fix the reported native JIT crash, root Jupyter launch, shared-filesystem runtime permissions, missing uv after PATH changes, and blocked Hugging Face downloads. JIT means Numba's native just-in-time compilation. Preserve the existing robot, dataset bytes, models and training/evaluation algorithms. Installation must find a declared uv executable; startup must use authenticated loopback Jupyter with private local runtime files; failed preflight workers must leave actionable diagnostics; alternate dataset transport must pass the original SHA256.

## Progress

- [x] (2026-10-12) Inspected entry points, dependency pins and repository state. Started on main at f8ad3ef with a clean index/worktree and no unpublished commits.
- [x] (2026-10-12) Implemented runtime initialization and crash diagnostics; native signal fixture passes.
- [x] (2026-10-12) Implemented root/private-runtime startup, uv resolution and dataset transports; initial 9 targeted tests and all 22 suite tests passed.
- [x] (2026-10-12) Updated both READMEs and deployment guidance. Fresh install, official offline/HTTP transport, real CPU smoke (52.75 s), fixed-input JIT comparison, and ordinary/root-namespace authenticated Jupyter kernels passed.
- [x] (2026-10-12) Recorded measured evidence and limits; verified 49 local links/anchors, 31 shell blocks, bilingual command parity, source hashes and scoped differences. Implementation is ready for the authorized commit/push.

## Discoveries

The existing lock already pairs Numba 0.61.2 with llvmlite 0.44.0, but only Numba is directly pinned and neither is recorded in preflight versions. The preflight imports torch and the simulator in its main process, so a native crash prevents its final JSON. Neither the shell wrapper nor package initialization sets NUMBA_DISABLE_JIT. Jupyter inherits a possibly shared runtime path. The downloader has one hardcoded URL; setup requires uv in PATH. The reported JIT crash is user evidence; its native root cause has not yet been reproduced here. This host runs as a non-root user, so actual root acceptance requires a suitable isolated environment or must remain unverified.

Jupyter integration discovery: the first actual kernel made its runtime directory 1700 via jupyter_client/connect.py. The exact-mode assertion then failed; `outputs/deployment_portability_20261012_v1/jupyter.json` and its private log are preserved. Accepting only 0700 access bits plus the upstream sticky bit preserves the security requirement and permits restart; no group/other access is allowed.

## Decisions

2026-10-12: Default NUMBA_DISABLE_JIT=1 before imports in both supported entry paths; keep the compatible pinned versions and an explicit administrator opt-in to JIT. Do not claim an import-order change fixes an unidentified native crash. Run native preflight work in a child process and retain status, exit signal and log on failure. Probe exact directory/file modes, without enabling insecure Jupyter writes. Use an explicit URL/endpoint or an offline copy for identical dataset bytes, never an automatic untrusted mirror. Do not re-run experiments to select success rates.

## Current outcome and review

Fresh Python installation succeeded with PATH restricted to /usr/bin:/bin: 163 compatible packages. Official offline and HTTP transport, one CPU smoke (52.75 s; both rollouts unsuccessful), and ordinary/root-namespace authenticated Jupyter/kernel checks passed. Full suite: 22 passed; deployment subset after sticky-bit fix: 9 passed. JIT-enabled fixed-case preflight also passed on this host, so the reported native crash root cause remains undiagnosed. Preserved the initial Jupyter sticky-bit assertion failure and repeated only that affected acceptance in jupyter_v2. Public records are docs/deployment_validation_20261012.md and .json; raw artifacts remain ignored. Documentation and scoped diff checks passed. Only the authorized commit/push remains; no further experiment is needed.

## Context and implementation

`scripts/lab_python.sh` and `src/manipulation_lab/__init__.py` set process defaults; scripts import `_bootstrap.py` first. Add JIT defaults there, record actual versions/runtime mode, and isolate `scripts/preflight.py`. Update `scripts/start_lab.py` for UID-aware root arguments and a private `/tmp` runtime directory with owner/mode and secure-file checks. Update `scripts/setup_environment.sh` to resolve uv once by explicit override, PATH and standard installer directories. Update `scripts/download_dataset.py` with configurable endpoint/URL and offline file input, retaining checksum, HDF5 validation and no-overwrite behavior. Add focused regression tests, then update deployment documentation.

## Execution and acceptance

From the repository root, run `scripts/lab_python.sh -m pytest -q tests/test_deployment.py` first, then the complete test suite once. Test PATH loss with a controlled installer subprocess, crash recording with a signal-terminated child fixture, private runtime modes and root argument construction, and local HTTP/offline download paths including corrupt and interrupted payloads. Fixtures are infrastructure tests, not experiment data. Execute the repaired installer in a fresh project-local environment if feasible. Use one new output directory under `outputs/deployment_portability_20261012_v1` for the real dataset transport, preflight, 2-epoch CPU training, checkpoint reload, two closed-loop rollouts and video checks. Launch loopback Jupyter, verify unauthenticated rejection, authenticated access and a real kernel using private connection files; never print a token. Preserve all failure evidence. The original server's filesystem/network/native crash and actual root UID may remain unverified locally; label these boundaries explicitly.

## Repeatability and recovery

Every actual experiment uses a new output path. Existing datasets, partial downloads, checkpoints and prior results are not overwritten. Default runtime directories are private per UID; reject unsafe user-selected paths with a clear local-directory remedy rather than weakening file modes. A failed preflight is a failed result, not an automatic fallback/retry. Stage only this task's changed files and do not touch unrelated presentation work.

## Artifacts and interfaces

Keep existing CLI flags compatible. New transport and uv overrides must be documented with executable commands. Record actual checks and limitations in a new deployment validation document and link it from troubleshooting. No new runtime library is required.

2026-10-12 revision: actual kernel creation revealed upstream sticky-bit behavior; updated the directory check, regression case and documentation without weakening owner-only permissions. Root acceptance used unprivileged user namespaces, not host-root privileges. All original experimental results remain unchanged.
