# Make the assignment introduction visual and easier to teach

This living plan follows `.agent/PLANS.md`. The user's third revision asks for less visible text, better typography and mathematical typesetting, more genuine visual explanation, and a natural classroom voice. The goal is a clearer teaching sequence, not another palette change.

## Outcome

Create a separate v3 package with nine English slides, ten minutes of Chinese notes, real simulation media and a single well-typeset BC equation. Use task close-ups, observation callouts, an actual same-observation human/policy action comparison, paired initial-state images, visible failure progression and pictorial submission requirements. Following the user's live correction that the visual draft was too simplified, retain one or two short explanatory statements per concept, especially input/output dimensions, learning, experimental controls and submission. Keep detailed derivations in speaker notes.

## Progress

- [x] 2026-10-12: inspected v2 and current source state; confirmed a real failure trace and available human demonstration video. Other session's course-packaging changes remain outside scope.
- [x] Prepare traceable visual assets, open-license fonts and an actual single-state action comparison without training or selecting new rollouts.
- [x] Build the visual deck, concise slide text and updated Chinese narration; restore supporting explanation following the user's live feedback.
- [x] Inspect every rendered page; verify media, formula, word reduction and source contracts.
- [ ] Commit and push only the v3 package and this plan; record delivery.

## Findings and decisions

V2 still resembles a written handout, and manually positioned mathematical characters look uneven. Use Adobe Source Sans 3 for body copy and Source Serif 4 for calm headings. Render the single displayed equation with mathematical typesetting and preserve its LaTeX source. Mathematical notation becomes a supporting visual: loss = mean squared difference between robot and human actions. The first v3 draft reduced editable text from 598 to 237 words, but the user explicitly found it too simplified. Restore concise explanations rather than treating maximum text reduction as the goal; verification should record the actual revised count, not enforce the earlier 35% reduction target. Prediction, exact 7B normalization and Adam updates remain explained in Chinese notes.

Use the same successful and failed student episodes as v1/v2. Re-render only saved failure actions through step 81 for clear images, checking every resulting state against the original trace. Render two fixed evaluation initial states from the saved manifest, comparing against logged states. This is presentation asset recovery, not another evaluation. For the BC teaching example, query the existing student checkpoint once on one recorded observation and compare all seven predictions with that exact demonstration's expert action; never infer a component error from closed-loop behavior.

## Current result

The balanced v3 deck, static PDF, nine page previews and Chinese narration are complete. Final editable text is 402 words versus 598 in v2; the earlier 237-word draft was too terse. Counts exclude equation/chart-internal labels. Nine slides, 600 seconds of notes, English text, shape bounds, PDF text coverage, intended fonts, video byte identity, decoding and browser playback/seeking passed. The existing failure replay matched all 81 recovered states exactly for the checked quantities; the seven-component same-observation action MSE is 0.004584529834045113. No new training or policy-evaluation runs were performed. Native PowerPoint on the instructor's machine remains untested. No grading, notebook, training, environment, top-level README or older-deck changes were made.

## Implementation

Work under `/home/jingchen/projects/manipulation_lab/presentations/assignment_intro_20261012_v3`. Reuse verified MP4s and raw logs, add provenance for new stills and the same-state action example. Draw callouts and arrows as editable native PowerPoint objects, preserving source photos. Move detailed text into the notes. Keep the required task, workflow, 16/7 input-output contract, BC model, two-rate experiment, visualization, submission and rubric across the nine pages.

## Verification and recovery

Use the independent authoring tools in `/tmp/manipulation-ppt-tools`; leave student dependencies and older decks untouched. Compare new re-rendered state values to original arrays, check direct predicted-action MSE, inspect all pages and the mathematical expression, and record visible-word counts versus v2. Check nine English slides, notes totaling 600 seconds, embedded MP4 identity, complete video decoding and static PDF coverage. Native PowerPoint playback on the instructor machine remains untested. Use new output files, preserve failures and avoid broad experiment reruns.
