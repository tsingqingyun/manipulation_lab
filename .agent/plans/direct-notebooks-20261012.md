# Run the lab directly in an IDE without manual port forwarding

This living plan follows [../PLANS.md](../PLANS.md).

## Goal and context

In `/home/jingchen/projects/manipulation_lab`, make direct `.ipynb` execution the documented default. Users run one preparation command, choose a registered kernel in VS Code, and execute the existing four notebooks. A kernel is the Python process executing notebook cells. Local Linux runs compute locally; Remote SSH runs compute on the server through the IDE's existing authenticated connection. Neither workflow requires a manually launched Jupyter web server or a manual port tunnel. Keep the existing robot, data, algorithm and notebook contents.

## Progress

- [x] (2026-10-12) Inspected clean main at a5fe44f and existing installer/kernel metadata. The current generic kernel does not persist group, device or rendering settings from a terminal into the IDE.
- [x] (2026-10-12) Added preparation wrapper, isolated persistent per-group kernels and extension recommendations; fresh installation and real preflight passed.
- [x] (2026-10-12) Both READMEs and deployment/instructor guidance now default to direct IDE notebooks without manual forwarding.
- [x] (2026-10-12) Sanitized-parent standalone kernel check passed; all four notebooks executed once in 192.05 s. Both real checkpoints, 20 evaluations, failure evidence and a valid two-row CSV submission ZIP are retained.
- [x] (2026-10-12) Recorded results and GUI/platform limits; reviewed scoped changes and documentation. Ready for the authorized commit/push.

## Discoveries

An IDE kernel does not necessarily inherit exports from its integrated terminal. Selecting an unconfigured raw Python interpreter may lose group/device/rendering choices. Therefore a generated kernelspec must carry only the explicit lab settings and renderer paths, not the whole environment or credentials. The current launcher-specific runtime directory setup is not a requirement to start a standalone ipykernel. IDE GUI/video playback itself cannot be claimed tested from a headless kernel test.

## Decisions

2026-10-12: add an additive one-command wrapper around existing scripts, default CPU and OSMesa for portable Linux execution, and register a user-visible kernel with its environment settings saved. Name kernels by project/group/configuration identity to avoid overwriting unrelated kernels. Do not auto-start a service, open ports, edit SSH settings, install IDE extensions globally, or introduce a new model. Keep the browser launcher available for institution-managed deployments, but remove forwarding steps from the student's default workflow.

## Outcome and review

Implementation and one real four-notebook acceptance are complete. Initial full suite: 25 passed; final setup-specific subset: 4 passed after adding the reference-path regression. Fresh setup and sanitized-parent kernel checks passed. Four notebooks completed in 192.05 s; lr_a had 3/5 stable placements in each condition and lr_b had 5/5 in each. All failures and original outputs are retained; reports remain DRAFT. ZIP integrity and two-row CSV schema passed. Results are in docs/direct_notebook_validation_20261012.md and .json. Full browser/IDE UI acceptance and non-Linux native execution remain outside this host's verified scope.

## Implementation and interfaces

Add `scripts/prepare_notebooks.sh` to invoke existing `setup_environment.sh`, followed by `scripts/prepare_notebooks.py`. The Python entry point validates/downloads the unchanged dataset, runs preflight in a fresh output, saves chosen group/device/render backend and paths into a registered Jupyter kernelspec, and prints exactly which kernel and notebook to open. Support an offline dataset input and existing deployment environment overrides. Notebook computation is unchanged; only the final Notebook 04 download instruction now refers to the IDE file explorer. Add a minimal IDE extension recommendation file if absent. Add focused tests for registration isolation/configuration and help behavior, then document the actual commands.

## Acceptance and recovery

Run focused tests before one complete suite. Run the new preparation command against the already validated Python environment with the documented OSMesa library override, keeping preflight outputs versioned. Start the selected kernel directly via jupyter_client with LAB_* and rendering variables removed from the parent; it must still report the intended dataset/device/group/JIT mode. Execute all four unchanged notebooks through it once with frozen training settings; save executed copies and videos in a new ignored directory. No Jupyter HTTP server is launched. Inspect two checkpoints, matched evaluations and submission output. Retain failures and do not change seeds. Existing per-group session/output directories must not be advanced by acceptance: use a new output root.

## Artifacts and dependencies

Reuse ipykernel, jupyter_client, nbclient and the existing installers; no new Python dependency. Generated kernelspec paths are host-local and excluded from Git. Record commands, measurements and unverified IDE GUI/platform details in a short checked-in validation note. Commit only this task's files, then push the configured origin/main and verify its SHA.

2026-10-12 review: retained the reference_v1 path even before the teacher generates it, and corrected the final Notebook download wording. The export-inspection helper initially looked inside the report folder; the existing exporter correctly places ZIPs in the group parent. Correcting the inspection path verified the original ZIP without rerunning or modifying any experiment.
