# Executed instructor solutions — 2026-10-13

Open the four `.ipynb` files in order. All code cells have actual execution
outputs, and Q1–Q5 contain worked reference answers for this particular run.
Videos and plots are embedded; viewing saved results does not require rerunning
training. The original student templates in the parent directory are unchanged.

The first complete execution used the original notebook sources, CPU training,
OSMesa rendering, seed 17, 50 epochs and both required learning rates. All 20
rollouts completed without runtime errors. Both models selected epoch 12.

| Learning rate | Standard stable placement | Shifted stable placement |
|---|---:|---:|
| 0.001 (`lr_a`, preselected primary) | 3/5 | 3/5 |
| 0.0003 (`lr_b`) | 5/5 | 5/5 |

For notebooks 01–03, the original computational outputs were retained and only
the edited answer cells were executed in new kernels, as the assignment allows.
Consequently execution counters need not be monotonic across those saved cells.
Notebook 04 was re-executed to save the four selected frames, step-57 annotation,
complete report and evidence ZIP. No training or policy evaluation was repeated
while adding answers. `solution_execution.json` records both phases.

The first failed EGL attempt, which stopped before training, remains in
`outputs/solutions_20261013_v1`. The successful run is in
`outputs/solutions_20261013_v2/runs/group_01/20261013T051828Z_5a8ae81c`.
Saved absolute output paths identify this host's original run; use the portable
evidence ZIP to inspect the same artifacts on another computer. Rerunning the
notebooks requires the normal project environment and a deliberately chosen
output/group configuration; these are executed teaching artifacts, not an
automatically resumed session on a different machine.

See the [solution presentation and evidence package](../../presentations/assignment_solutions_20261013/README.md).
