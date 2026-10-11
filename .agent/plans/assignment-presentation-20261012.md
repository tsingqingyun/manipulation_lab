# Create a ten-minute assignment introduction with real simulation evidence

This living ExecPlan follows `.agent/PLANS.md`. Behavior cloning means learning to predict recorded human actions from observations. A policy is the trained function used to choose the robot's next action. The presentation introduces these ideas to Introduction to Robotics students without assuming prior robotics or machine-learning knowledge.

## Goal and observable outcome

Deliver a separate, editable nine-slide English PowerPoint with Chinese speaker notes totaling approximately ten minutes. Include the current Panda PickPlaceCan simulation, a 10–20 second genuine successful sequence, Reach/Grasp/Transport/Place frames, the actual observation/action and student model, notebook workflow, visualizations, submission and grading. Supply a PDF preview, source, separate media and evidence provenance so the material remains usable if an audience's PowerPoint player lacks video support.

## Progress

- [x] 2026-10-12: inspected the current README, student/instructor guides, four notebooks, configurations, model and visualization implementation; recorded pre-existing course-packaging changes without modifying them.
- [x] 2026-10-12: inspected the completed group 01 two-rate run; recorded the consulted working-tree files and hashes in source_contract.json.
- [x] 2026-10-12: delivered nine editable English slides, 600 seconds of Chinese speaker notes, original failure media, 15-second half-speed success media and real plots. The 768-pixel success rendering exactly matches all 149 original logged object/eef/width states.
- [x] 2026-10-12: inspected the rendered nine-page PDF, checked English text and Chinese notes, bounds and PDF text coverage, matching embedded video bytes, full MP4 decoding and Chromium playback/seeking. Native PowerPoint on the instructor laptop remains untested.
- [x] 2026-10-12: published the presentation and this plan in commit 7f9df61 to origin/main; push advanced the remote from a2c58a7. The remaining working-tree deployment/course changes belong to the other session and were not committed by this task.

## Discoveries

The working tree contains ongoing course-packaging changes, including English teaching text and evidence export. The user confirmed that another session owns them and asked for independent presentation work only. A GitHub web fetch failed; an authorized Git remote query verified origin/main at a2c58a7. Browser and LibreOffice needed temporary profiles outside the restricted process sandbox. Final PDF export uses a static poster to avoid codec-dependent PDF video annotations. No local presentation-specific AGENTS.md was found outside third-party packages.

## Decisions

2026-10-12: use the current implemented four-notebook contract, cross-checking it again before final delivery. Do not change robot, dataset, student architecture, evaluation criteria or experiment outcomes. Complete the suggested nine-slide structure after the user's explicitly supplied first two slides with workflow, observation/action, BC, required experiments, evaluation, failure visualization, and submission/grading.

2026-10-12: honor the user's clarification by changing only presentations/assignment_intro_20261012 and this plan. The successful original trajectory is about 7.5 seconds; label its 15-second presentation playback as half speed. Re-render the saved actions, compare every resulting physical snapshot to the source, and never reinterpret this as a new policy evaluation. Keep the horizontally placed can visible and explain that upright orientation is not an acceptance criterion.

## Current outcome

The independent teaching package is complete, acceptance passed, and delivery commit 7f9df61 is published. It includes PowerPoint, static PDF, Chinese narration, separate media, full preview, fonts, reproducible scripts and provenance. Original source/experiment outputs are preserved. No training or policy evaluation was rerun. The only product-platform limitation is untested native PowerPoint playback on the instructor's computer; the browser-tested MP4 and static PDF are included.

## Project context

Work from `/home/jingchen/projects/manipulation_lab`. The fixed contract lives in `configs/`, `src/manipulation_lab/`, `README.md` and `docs/assignment_student.md`. Student model: deterministic multilayer perceptron, three hidden layers of 256 units, 16 state inputs, 7 normalized action outputs. Experiment: learning rates 0.001/0.0003, seed 17, 50 epochs, identical data/initial weights, validation-selected checkpoints, primary lr_a, five standard plus five shifted starts per model. Rubric: 20/25/30/25; submit a 1–2 page PDF and Notebook 04 evidence ZIP.

## Implementation

Add a versioned presentation package under `presentations/assignment_intro_20261012/`, including build script, content and Chinese narration, media provenance and delivery artifacts. Use existing genuine videos and logged trajectories; never label a demonstration as a policy rollout. Re-render a saved trajectory for resolution only when necessary, keeping a source mapping. Extract keyframes from actual recorded frames and record timing. Do not invent success results or certify position shift as outside the training distribution.

## Execution and acceptance

Use a separate presentation tool environment if needed so the locked lab dependencies remain unchanged. Generate editable text/vector slides plus embedded MP4 and a separate MP4 fallback. Export PDF using LibreOffice, render all nine pages, inspect layout and readable labels, inspect PPTX XML for English visible text and Chinese notes on every slide, check timing sum and source paths, and decode the complete media. Record exact checks and real limitations in the presentation manifest. Review staged files before a narrowly scoped commit and ordinary push to origin/main.

## Recovery and repeatability

Create new build output names instead of replacing existing user artifacts. A slide layout correction may regenerate task-created drafts. Keep untouched source media and SHA256 provenance. Do not rerun training or evaluation merely to obtain a successful case. A failed network push must be reported honestly; no force push or inclusion of unrelated work.

## Artifacts and dependencies

PowerPoint, PDF, local video, source script, timing/notes and provenance must share one versioned directory. Presentation dependencies are optional authoring tools only, not new student runtime requirements. No public website or message delivery is authorized by this task.
