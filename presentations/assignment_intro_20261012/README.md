# Manipulation Learning Lab — Assignment Introduction

Nine editable English slides for a ten-minute Introduction to Robotics assignment introduction. Every slide contains timed Chinese PowerPoint speaker notes. The deck explains the current Panda PickPlaceCan task, demonstration-to-training-to-inference workflow, behavior cloning, four student notebooks, visual evidence, submission and grading.

## Present the lesson

Open **[Manipulation_Learning_Lab.pptx](Manipulation_Learning_Lab.pptx)** in PowerPoint. In slideshow mode, click the large simulation scene on slide 2 to play the embedded 15-second H.264 video. It shows the complete successful movement at **0.5× speed**. The four stills show Reach → Grasp → Transport → Place. Use Presenter View to read the Chinese notes; [speaker_notes_zh.txt](speaker_notes_zh.txt) contains the same script separately.

The video is embedded, so PowerPoint does not depend on local experiment paths. The package also contains [the standalone video](assets/success_half_speed.mp4) as a playback fallback and a [static PDF handout](Manipulation_Learning_Lab.pdf). The PDF intentionally shows a poster and says “VIDEO IN PPTX”; it does not claim to play the video. View the [nine-page contact sheet](preview/contact_sheet.png) for a quick design review.

The editable text uses DejaVu Sans. If unavailable on the presentation computer, install the two supplied fonts in `fonts/` before opening PowerPoint, or use the PDF for an exact static layout. Font attribution and redistribution terms accompany the fonts. No font installation is required for the PDF or video.

| Slide | Topic | Time |
|---|---|---:|
| 1 | Title and learning goal | 0:30 |
| 2 | Actual task, complete video, four stages and success | 1:00 |
| 3 | Demonstration → Training → Inference | 1:10 |
| 4 | 16 state values → policy → 7 action values | 1:10 |
| 5 | Behavior cloning and actual learning curves | 1:20 |
| 6 | The four required notebooks | 1:10 |
| 7 | Paired evaluation and position-shift limits | 1:20 |
| 8 | Failure visualization and evidence-based explanation | 1:20 |
| 9 | PDF + ZIP submission and the 20/25/30/25 rubric | 1:00 |
| **Total** | | **10:00** |

## Evidence and scope

The deck was checked against the **implemented working tree on 2026-10-12**, including the current README, student assignment, instructor guide, all four notebooks, configurations and consuming code. Another user session owns the ongoing environment/course-packaging changes. This directory neither modifies that work nor certifies its deployment as complete. [source_contract.json](source_contract.json) records the exact consulted file hashes and base Git commit so future changes can be reconciled.

Videos and figures come from the existing completed `teaching_acceptance_20261012_v1` group 01 run, not invented values or new seed selection. The success video is the preselected primary student policy `lr_a`, case `standard_01`, source demonstration `demo_185`, seed 102. The failure is the same policy's `standard_00`, source `demo_39`, seed 101. Slide 7 reports actual stable-placement counts: `lr_a` 2/5 standard and 3/5 shifted; `lr_b` 5/5 and 5/5. These are one completed example, not promised student outcomes or a statistically established learning-rate ranking.

The high-resolution success media replays the **original saved action sequence from the identical initial state**. It does not call the policy again or change any outcome. All 149 post-action object positions, end-effector positions and gripper widths exactly match the original logs (maximum absolute error 0.0 for each). Rendering is 768 × 768; saved frames correspond to steps 1, 3, …, 149, displayed at 5 fps for half-speed playback. The 15-second duration includes no synthesized intermediate frames. The four stage images correspond to steps 1, 41, 89 and 145. Stage names are teaching annotations. The original 256 × 256 failure video remains unchanged. [media_provenance.json](media_provenance.json) records source paths, hashes, steps, checkpoint identity and replay checks.

The final can lies on its side. This satisfies the existing lab's stable released placement criterion, which does not require an upright can. The Chinese notes explain the target-margin approximation and avoid claiming full object-mesh containment. Both the environment's success flag and stable released placement remain distinct. The +0.04 m world-X test is not described as a certified out-of-distribution benchmark.

## Validation and real limitations

[verification.json](verification.json) records the final acceptance:

- Nine slides, 600 seconds of planned narration, English visible text, Chinese notes on every page, and all slide elements inside the canvas.
- All editable textbox words present in the exported nine-page PDF; every page was rendered and visually inspected. The PDF has no video annotations.
- Embedded MP4 bytes match the standalone asset. Both MP4s fully decode. Chromium playback, seeking to the end and completion succeeded.
- Student architecture, required experimental controls, paired initial states and displayed numerical results match the current configuration and raw records.

Native Microsoft PowerPoint playback has **not** been tested on the instructor's computer. Browser video verification and PPTX media structure checks do not replace that platform-specific check. A standalone MP4 and four task frames provide usable fallbacks.

The first LibreOffice export was blocked by sandbox desktop-state access; a temporary isolated profile outside that sandbox completed export. Its first video-bearing PDF attempted to load an unavailable local H.264 decoder, so the final PDF is exported from a poster-only copy. Chromium likewise needed a temporary process outside the restricted socket sandbox. These were authoring-environment limitations; no classroom experiment was repeated and no success threshold was changed.

## Rebuild

`slides.json` holds the timing, Chinese narration and slide source references. `build_deck.py` produces the editable layout and draws plots from the small raw records in `assets/`. `prepare_media.py` documents the original resolution-improvement step; it requires the source dataset/run and refuses to overwrite existing media. Normal slide editing does not need to rerun it.

From the repository root, install optional authoring dependencies into a separate environment, keeping the student environment unchanged:

```bash
uv venv /tmp/manipulation-slide-authoring
uv pip install --python /tmp/manipulation-slide-authoring/bin/python \
  -r presentations/assignment_intro_20261012/authoring-requirements.txt
MPLCONFIGDIR=/tmp/manipulation-slide-mpl \
  /tmp/manipulation-slide-authoring/bin/python \
  presentations/assignment_intro_20261012/build_deck.py \
  --static-output /tmp/manipulation-slide-static/Manipulation_Learning_Lab.pptx
libreoffice -env:UserInstallation=file:///tmp/manipulation-slide-lo \
  --headless --convert-to pdf \
  --outdir presentations/assignment_intro_20261012 \
  /tmp/manipulation-slide-static/Manipulation_Learning_Lab.pptx
```

Run `verify_deck.py --browser /absolute/path/to/chrome` with the authoring Python for delivery checks. Verification of original media provenance requires the recorded local run; the supplied PPTX/PDF/MP4 and slide build itself do not. Rebuild only task-created deliverables or copy this directory to a new version first. Do not retrain or change experiment settings to alter example results.

The `.pptx`, `.pdf`, notes, media, figures, raw evidence extracts, source scripts and fonts are the complete independent teaching package. The repository's robot, learning algorithm, student notebooks and grading code are untouched by this presentation task.
