# Student Assignment

Complete four notebooks in order in your assigned group. Plan 130–160 minutes for execution and discussion, plus time to polish your report. Installation is prepared before class. All student results must come from your own actual training and simulator rollouts.

## Part 1 — Understanding Demonstrations (20 points)

Play one human demonstration. Identify the 16-value policy observation and 7-value normalized action, their coordinate frame and units. Inspect the 160/20/20 whole-episode split and the initial-position plot. Explain why a trajectory supplies information that a successful final image does not.

Deliver: Q1, demonstration video/provenance, observation/action inspection and initial-position figure.

## Part 2 — Training a Behavior Cloning Policy (25 points)

Complete the mandatory learning-rate comparison: 0.001 versus 0.0003. Keep the dataset, whole-episode split, three 256-unit hidden layers, seed 17, initialization, 50 epochs, batch size, normalization and device identical. The code verifies these controls. Each model is selected at its best validation epoch; the primary model remains `lr_a`, chosen before test results.

Deliver: both configurations, checkpoints, raw training/validation loss CSVs, curves with selected epochs, comparison table and Q2–Q3. Explain how the two curves relate to actual manipulation outcomes. Do not change seeds, discard an unsuccessful variant or use the test set for model selection.

## Part 3 — Policy Evaluation and Generalization (30 points)

Each checkpoint must execute the same 5 standard and 5 Position Shift cases. Compare each paired case using its source episode and seed. Inspect actual test initial states relative to training demonstration initial states. Watch representative videos. Distinguish environment success from stable released placement.

Deliver: both `summary.json` and `results.csv` files, evaluation configurations, test manifests, paired CSVs, position/success plots, representative rollout and Q4. Discuss that five cases per condition provide a coarse estimate. A +0.04 m world-X shift is not a certified OOD benchmark, even when the 2D scatter points differ.

## Part 4 — Failure Analysis (25 points)

Choose a completed real failure from the primary student model. If it has no failure, use explicitly attributed instructor evidence. Do not report the instructor model's outcome as yours. Inspect at least three control steps, mark the first observable error, and inspect the requested-step state alongside the nearest actual video frame. Explain any frame offset.

Deliver: failure video, signal plot, selected frames, `observed_facts.json`, your first-error annotation, failure stage, hypothesis and improvement proposal. The proposal should describe a future controlled test; you do not need to implement another algorithm. Use `unknown` for the failure stage if the evidence is inconclusive, and explain why.

## Report (1–2 pages)

Include your group, run identifier, dataset/checkpoint identifiers and the following answers:

- **Q1. What observations and actions are used in this task?** Include dimensions, units, frame and gripper sign.
- **Q2. How does behavior cloning learn from demonstrations?** Identify input, expert target, loss, weight update and validation selection.
- **Q3. Does a lower training loss always result in better manipulation performance?** Cite your two learning-rate curves and success counts; distinguish open-loop prediction error from closed-loop behavior.
- **Q4. How does changing the initial object position affect the learned policy?** Cite a paired case and the coverage figure, including the generalization limitation.
- **Q5. Identify one failure and propose a possible improvement.** Cite its control step/frame and state; separate the observed error from the hypothesized cause and proposed test.

A compact comparison table and one annotated failure figure are sufficient in the report. Put full curves, videos and raw records in the evidence appendix. The generated `report.md` is an evidence appendix, not a replacement for your discussion. Fill notebook answer cells in your own words; regenerate the final report after edits. Empty answers or no error marker keep it marked DRAFT.

## Submission

Submit your PDF and the ZIP produced by Notebook 04. It includes both model variants, training configurations, curves/logs, evaluation configurations/manifests/results, videos, failure evidence and class-summary CSV rows. Keep the original output directory. Do not submit environment packages, the public dataset, Jupyter tokens or unrelated files. The archive's local session pointers document the original run; report figure links are relative and work after extraction.

If interrupted by an infrastructure failure, retain its logs and partial output, notify the instructor and record any authorized rerun in your report. Do not hide failed experiments. A low policy success rate alone is not a reason to rerun or lose points.

## Detailed Grading

| Area | Points | Allocation |
|---|---:|---|
| Demonstration Understanding | 20 | 10 observation/action interpretation; 5 playback evidence; 5 split/trajectory explanation |
| Policy Training & Experiment | 25 | 10 both real runs/checkpoints; 8 valid controls/configuration; 7 curves and Q2–Q3 interpretation |
| Policy Evaluation | 30 | 10 complete paired metrics/manifests; 8 videos and position plot; 7 success-criterion interpretation; 5 Q4 and limits |
| Failure Analysis & Discussion | 25 | 8 real attributed case and steps; 7 earliest observable error supported by state/frames; 7 plausible hypothesis/test; 3 concise reproducible report |
| **Total** | **100** | Evidence, reproducibility and analysis; no points awarded solely for a higher success rate |

Incomplete evidence can receive partial credit with an honest explanation. Runtime failures are distinct from valid unsuccessful rollouts. A documented failed manipulation can receive full marks when the experiment and analysis meet the requirements.
