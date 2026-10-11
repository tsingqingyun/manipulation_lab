# Revise the assignment deck with restrained design and concise equations

This living ExecPlan follows `.agent/PLANS.md`. The user found the first deck overly styled and requested a minimalist revision with short equations explaining the underlying learning principle. A loss is the numerical disagreement between predicted and demonstrated actions; an optimizer changes model weights to reduce this loss.

## Goal and outcome

Deliver a new independent nine-slide English deck with Chinese notes totaling ten minutes, retaining the verified genuine simulation video. Use white backgrounds, black text, thin rules and a single blue accent. Explain action prediction, the exact mean-squared action loss, and the learning-rate-controlled Adam update, with symbol definitions and one numerical example. Keep the original version and the other session's course-packaging changes untouched.

## Progress

- [x] 2026-10-12: inspected existing slide sources and current student configuration. Confirmed robomimic BC uses nn.MSELoss with only the L2 loss enabled, and Adam, rather than plain gradient descent.
- [x] 2026-10-12: built version 2 in presentations/assignment_intro_20261012_v2. All backgrounds are white; decoration and inherited line shadows removed; original videos and numeric evidence preserved.
- [x] 2026-10-12: inspected all nine rendered pages and the formula pages at full size. Acceptance passed: 600 seconds, English visible text, Chinese notes, bounds, PDF text, editable equations, actual MSE/Adam source and identical embedded MP4 bytes. Browser playback evidence is carried forward after media hash equality; no redundant simulation or browser run.
- [ ] Publish only the version 2 package and this plan; verify the remote commit.

## Discoveries

The original style used dark cover/closing pages, rounded cards with inherited shadows, colored chips, heavy arrows and repeated uppercase labels. Removing those is more useful than changing colors alone. The student optimizer is Adam in third_party/robomimic/robomimic/config/bc_config.py and utils/torch_utils.py. A plain SGD update presented as the actual implementation would be inaccurate.

## Decisions

Use editable PowerPoint text and mathematical symbols for the equations, with proper subscript/superscript runs. Define observations as the normalized policy input in the equation, noting that its normalization statistics come only from training data. Show the loss averaged over B samples and all 7 action components. Show theta_next = theta - eta d_Adam, explaining d_Adam as the optimizer's scaled gradient direction without deriving its moving averages. Keep the two-learning-rate comparison as the reason for introducing eta.

## Current outcome

The minimalist v2 deck, static PDF, separate Chinese narration, preview images and source are complete and verified. The three formulas are editable and have symbol definitions plus a numerical example. Version 1 and the other session's working-tree changes remain intact. Only the narrowly scoped publication step remains.

## Implementation and execution

Reuse the first package's media and small raw evidence extracts, byte-for-byte. Create a fresh build script and revised slides.json under the version 2 directory. Update the Chinese notes on slides 4 and 5 to explain every mathematical symbol in ordinary language; retain the 600-second schedule. Draw loss/position/failure figures from the same raw logs using restrained colors. Export a poster-only PDF with an isolated temporary LibreOffice profile. Use the existing independent authoring tools in /tmp/manipulation-ppt-tools with the lab Python; no student dependency changes.

## Acceptance

Verify all nine rendered pages, English visible text, Chinese notes on every page, 600 seconds total, slide bounds and PDF text coverage. Check editable equations and all symbols in the rendered PDF. Confirm the loss normalization with the current BC source, Adam with the current optimizer factory, and unchanged media hashes. Retain browser playback evidence for the unchanged media; verify the new PPTX embeds the same bytes. Native PowerPoint on the instructor's computer remains untested.

## Recovery and publication

Do not overwrite version 1 or alter the other session's unstaged source/doc changes. Use a new version directory and narrowly scoped commits. Keep exact media provenance and source hashes. Report rendering or publication failures rather than changing experiment outcomes. The final delivery links must point to version 2.
