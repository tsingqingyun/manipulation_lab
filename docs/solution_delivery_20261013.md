# Instructor solution delivery — 2026-10-13

Status: four notebooks executed, reference answers completed, presentation and
evidence accepted. Delivery files are linked below.

Scope: the four first-party assignment notebooks, complete answers Q1–Q5,
actual two-learning-rate training and 20 paired simulator rollouts, followed by
an English solution presentation with Chinese speaker notes. Third-party example
notebooks are outside the assignment. Student templates and existing runs remain
unchanged.

The first execution attempt is preserved at `outputs/solutions_20261013_v1`.
Notebook 01 failed during EGL display initialization, before policy training.
The second attempt uses CPU training, OSMesa rendering and disabled Numba JIT,
with the existing verified Ubuntu OSMesa runtime explicitly configured. It uses
`outputs/solutions_20261013_v2`, the unchanged seed 17, both prescribed learning
rates, and 50 epochs per variant. No scores are selected through repeated runs.

`scripts/execute_notebooks.py` performs the original notebook execution.
`scripts/finalize_solution_notebooks.py` then executes only edited answer cells
for 01–03 and re-executes 04 to create annotated failure evidence and the final
report/archive. It does not repeat training or evaluation. Source execution and
answer-edit records are kept separately; no cell outputs are invented.

## Completed artifacts

- [15-slide editable English PPT with Chinese notes](../presentations/assignment_solutions_20261013/Manipulation_Lab_Worked_Solutions.pptx)
- [Static slide PDF](../presentations/assignment_solutions_20261013/Manipulation_Lab_Worked_Solutions.pdf)
- [Four executed instructor-solution notebooks](../notebooks/solutions_20261013/README.md)
- [Two-page reference report](../presentations/assignment_solutions_20261013/Instructor_Solution_Report.pdf)
- [Experiment evidence, including both checkpoints and all 20 rollouts](../presentations/assignment_solutions_20261013/Experiment_Evidence.zip)
- [Verification record](../presentations/assignment_solutions_20261013/verification.json)

The deck includes 875 seconds of Chinese speaker notes (about 14:35), two embedded
actual policy videos, both loss curves, the complete paired-case table, and four
failure frames. Frame extraction does not rerun the simulator or generate images.

## Results

The original notebook execution took **237.65 seconds**, excluding setup, answer
editing and presentation preparation. Notebook times were 10.07, 223.85, 1.22 and
2.52 seconds. All 20 code cells have execution records in the completed notebooks.
Both variants trained for 50 epochs and selected epoch 12 using validation loss.

| Variant | Learning rate | Epoch-50 training MSE | Selected validation MSE | Standard stable | Shifted stable |
|---|---:|---:|---:|---:|---:|
| lr_a | 0.001 | 0.01771696 | 0.03537583 | 3/5 | 3/5 |
| lr_b | 0.0003 | 0.02091872 | 0.03412256 | 5/5 | 5/5 |

All four controlled-experiment checks passed: only learning rate changed,
identical initial weights, identical dataset/splits/versions, and identical
evaluation configuration/cases. There were **20 completed evaluations and zero
runtime errors**. Environment-success counts match stable-placement counts here.

In `lr_a / standard_00` (`demo_39`, seed 101), contact is present at states 49–56
and absent from 57 onward. Requested states 45, 53, 57 and 65 have exact frames
11, 13, 14 and 16, with zero offset. Step 57 marks the earliest directly supported
loss of retention; it is not a proven earliest causal deviation. The can lifts
only 5.72 mm. Alignment or closure timing remains a hypothesis; the proposed
same-state timing intervention has not been executed.

Position Shift preserves every success/failure label in this run but changes
completion times. `lr_a / demo_185 / seed 102` takes 141 versus 156 steps (+0.75 s).
The solution explicitly distinguishes initial-position coverage from trajectories
and avoids claiming certified out-of-distribution generalization.

## Validation and unchanged components

Notebook format, all executed cells, absence of cell errors, answer completeness,
both checkpoint identities, 50-row training logs, 20 evaluations, video/frame
mapping, source/media hashes, embedded MP4 identity and full video decoding passed.
The PPT/PDF have 15 pages with complete text coverage, English visible text,
Chinese notes and embedded Source Sans/Serif fonts. The two-page answer report
and evidence ZIP CRC/content hashes passed. Visual review caught spacing issues
on slides 4 and 13; those two layouts were corrected and rechecked without
repeating training, evaluation or unrelated acceptance checks.

Student template notebooks, dataset, network, training/evaluation implementation,
seeds, thresholds and existing outputs were not modified. Added code is limited
to solution-answer execution and presentation/report construction/validation.

The first infrastructure failure is retained. Native PowerPoint playback on the
teaching computer remains untested. Results cover one training seed, five paired
cases per condition and simulation only. Saved notebook absolute paths refer to
the original host; the evidence ZIP is the portable record. Earlier draft report
versions remain as history, while the ZIP export manifest selects the completed
report. Git publication is verified separately from artifact correctness.
