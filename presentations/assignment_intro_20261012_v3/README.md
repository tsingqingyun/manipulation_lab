# Manipulation Learning Lab — classroom introduction, v3

Nine English slides with Chinese speaker notes timed for ten minutes. This revision keeps the visual teaching approach and restores concise explanations of the workflow, observations/actions, behavior cloning, experimental controls, failure analysis and submission. Earlier versions remain in their original directories.

Open [the PowerPoint](Manipulation_Learning_Lab.pptx) for the presentation, [the PDF](Manipulation_Learning_Lab.pdf) for static viewing, or [the contact sheet](preview/contact_sheet.png) to review all nine pages. Chinese narration is embedded in each slide and also available in [speaker_notes_zh.txt](speaker_notes_zh.txt).

## Presenting

Install the bundled [Source Sans 3 and Source Serif 4 fonts](fonts/) before opening the PPTX to reproduce the layout. Their open font licenses are included. The PDF embeds the fonts and needs no font installation.

Slide 2 contains a 15-second successful student-policy video at half speed. Slide 3 contains a 5.9-second human demonstration replay from recorded simulator states. Click the video while presenting. Both MP4s are embedded; the [original failure video](assets/failure_original.mp4) is also supplied separately. The PDF and preview images are static.

The equation uses high-resolution mathematical typesetting, with its LaTeX source in [slides.json](slides.json). It is an image, not a native editable equation. Slide text, arrows and annotations remain editable. The formula averages squared differences over all seven action components and every sample; its accompanying chart displays only the three translation components for readability.

## What changed

- Real simulation frames explain the task, state input, paired starting positions and failure progression.
- One recorded observation supports a direct human-versus-policy action comparison. It illustrates behavior cloning, not a new generalization result.
- Serif headings and sans-serif explanations replace the previous uniform font treatment.
- Each concept retains a short explanation. The final deck contains 402 words of editable slide text, compared with 598 in v2. Counts exclude mathematical graphics and labels inside chart images; they are not a count of every visible word.
- The four notebooks, mandatory learning rates, 16/7 observation/action dimensions, three 256-unit hidden layers, 20/25/30/25 rubric and PDF-plus-ZIP submission match the current course materials.

## Evidence and checks

[verification.json](verification.json) records the final checks and artifact hashes: nine slides, 600 seconds of Chinese notes, English visible text, slide bounds, PDF text coverage, rendered fonts, two byte-matching embedded MP4s, full decoding of all three supplied videos, and browser playback/seeking of the two embedded video assets.

[media_provenance.json](media_provenance.json) retains the original success/failure source records. [visual_provenance.json](visual_provenance.json) documents new presentation assets. Replaying the original failure actions through step 81 reproduced object position, end-effector position and gripper width with maximum absolute difference 0.0 from the saved trace. Paired starting states were checked against saved evaluation states. No new training or policy-evaluation runs were performed.

The illustrated action comparison uses recorded `demo_0`, step 40, and the existing `lr_a` checkpoint. Its seven-component mean squared error is 0.004584529834045113. This is a same-observation illustration, not a held-out rollout score. The displayed placement counts are one existing completed example and are not target grades.

[source_contract.json](source_contract.json) records the course-source hashes used for the final verification. Repository deployment, student notebooks, course documents, experiment results and earlier presentation packages were not modified by this revision.

## Rebuilding

Use a separate Python environment with [authoring-requirements.txt](authoring-requirements.txt); the student runtime does not need these presentation dependencies. With the bundled fonts available to the PDF renderer:

```bash
python build_deck.py --static-output /tmp/manipulation-deck-static/Manipulation_Learning_Lab.pptx
libreoffice --headless --convert-to pdf --outdir . /tmp/manipulation-deck-static/Manipulation_Learning_Lab.pptx
python verify_deck.py --browser /absolute/path/to/chromium
```

Run these commands from this directory. Building uses the supplied assets; it does not train a model. The static intermediate replaces video objects with posters so the PDF remains clean. Full provenance verification additionally requires the original local experiment files listed in the provenance manifests and the v2 package for comparison. `prepare_visuals.py` documents the original asset recovery and intentionally refuses to replace existing verified assets; it is not needed to rebuild the slides.

Every rendered page has been visually inspected. Native PowerPoint playback and font rendering on the instructor's own computer remain untested; browser playback does not certify PowerPoint behavior.
