# Manipulation Learning Lab — worked solutions

The 15-slide editable presentation answers Q1–Q5 using a new complete execution
of the four assignment notebooks. Visible slide text is English; all slides have
Chinese presenter notes, totaling about **14 minutes 35 seconds**.

## Open these files

- [PowerPoint with two embedded rollout videos](Manipulation_Lab_Worked_Solutions.pptx)
- [Static PDF preview](Manipulation_Lab_Worked_Solutions.pdf)
- [All-slide preview](preview/contact_sheet.png)
- [Two-page instructor answer report](Instructor_Solution_Report.pdf)
- [Chinese speaker notes](speaker_notes_zh.txt)
- [Four executed solution notebooks](../../notebooks/solutions_20261013/README.md)
- [Full experiment evidence ZIP](Experiment_Evidence.zip): both model checkpoints,
  training configurations and logs, all 20 rollouts/traces, complete answers,
  report appendix, failure evidence and classroom CSV. The active report is
  identified in `export_manifest.json`; earlier draft analysis/report versions
  remain in the ZIP as execution history.

`Solution_Complete_Package.zip` is the local convenience bundle containing the
presentation, PDF, report, notebooks and evidence. It is ignored by Git to avoid
duplicating all the already tracked artifacts.

## Actual results and interpretation

| Variant | Learning rate | Selected epoch | Best validation MSE | Standard stable | Shifted stable |
|---|---:|---:|---:|---:|---:|
| lr_a (preselected primary) | 0.001 | 12 | 0.03537583 | 3/5 | 3/5 |
| lr_b | 0.0003 | 12 | 0.03412256 | 5/5 | 5/5 |

Each model trained for 50 epochs with seed 17 and identical controlled settings.
All four control checks passed, and all 20 evaluations completed without runtime
errors. The original four notebooks took **237.65 s** on this host, excluding
installation, answer editing and deck preparation. Environment-success counts
match stable-placement counts for this run, but the predicates differ.

The five paired cases retain the same success labels after the shift, while
completion times change. For example, `lr_a / demo_185 / seed 102` takes 141 versus
156 steps. A +0.04 m world-X shift and an initial-XY plot do not certify strict
out-of-distribution generalization.

Failure evidence comes from the primary student model's `standard_00`, not an
instructor checkpoint. Contact exists at steps 49–56 and disappears at 57. Frames
11, 13, 14 and 16 correspond exactly to requested states 45, 53, 57 and 65.
The annotation identifies first directly supported contact loss; the earliest
causal error and a remedy remain hypotheses. No proposed intervention was run.

## Rebuild and provenance

The existing lab runtime supplies NumPy, Matplotlib, imageio and nbformat.
Optional authoring dependencies are listed in `authoring-requirements.txt`; keep
them separate from student runtime requirements. Install the supplied fonts for
consistent PowerPoint/LibreOffice rendering. Their licenses are in `fonts/`.

From the repository root, using an authoring Python with the dependencies:

```bash
python presentations/assignment_solutions_20261013/build_deck.py
python presentations/assignment_solutions_20261013/build_deck.py --static
python presentations/assignment_solutions_20261013/build_report.py
libreoffice --headless --convert-to pdf --outdir /tmp/solution-pdf \
  presentations/assignment_solutions_20261013/Manipulation_Lab_Worked_Solutions_static.pptx
```

Copy the resulting static PDF to `Manipulation_Lab_Worked_Solutions.pdf` in this
package. A static deck supplies actual poster frames to the PDF export; the main
PPTX keeps both original MP4s. `build_deck.py --run <original-run>` refreshes the
packaged evidence from an existing run without training or evaluation.

`results.json`, `slides.json`, `answers.json`, `media_provenance.json` and
`evidence/` preserve the content and its sources. The original source execution
is in `evidence/original_execution.json`; edited-answer execution is in
`solution_execution.json`. Source paths refer to this repository or the original
local run. `verification.json` records notebook execution, two actual 50-epoch
runs, 20 rollouts, matched media hashes, full MP4 decoding, PDF text/font checks,
and ZIP CRC/hash checks. The original local run is needed to repeat provenance
comparisons in `verify_delivery.py`; the packaged evidence remains inspectable
without that absolute path.

## Limits

The first attempt failed at EGL display initialization before training; its
output is preserved. The completed run uses the already available Ubuntu OSMesa
runtime explicitly. Models, simulator logic, data split and student templates
are unchanged. Notebook answer completeness is not automatic scientific approval.
Only one training seed and five cases per condition are reported. No real robot,
strict OOD claim or tested causal improvement is implied. Native PowerPoint video
playback on the teaching computer has not been exercised; MP4 bytes and decoding,
LibreOffice PDF layout and saved notebook outputs were checked.
