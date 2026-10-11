# Assignment introduction — minimalist revision

This is the current nine-slide revision requested on 2026-10-12. It uses white backgrounds, black text, thin rules and one blue accent. The previous dark cover, rounded cards, shadows, colored chips and repeated decorative headings are removed. All slide text remains English, with Chinese speaker notes totaling ten minutes.

Open [Manipulation_Learning_Lab.pptx](Manipulation_Learning_Lab.pptx) for the editable presentation, [Manipulation_Learning_Lab.pdf](Manipulation_Learning_Lab.pdf) for a static preview, or the [nine-page overview](preview/contact_sheet.png) to review the layout. [speaker_notes_zh.txt](speaker_notes_zh.txt) contains the same narration as PowerPoint's notes. The original version remains in `../assignment_intro_20261012/`.

## Concise principles

Slide 4 introduces action prediction: **âₜ = πθ(oₜ)**. The symbols are explained on the slide and in Chinese notes. Here the observation is normalized using statistics from the training set only, and the learned weights remain fixed during inference. The implemented model takes 16 values, passes through three 256-unit hidden layers and predicts 7 action values.

Slide 5 defines the batch loss as **the sum of squared action differences, divided by 7B**, where B is the number of samples in the current batch. This matches the current robomimic `nn.MSELoss` with only its L2 term enabled. The factor 7 averages over the seven normalized action components; the last batch may contain fewer than the configured 256 samples. The slide gives a single-component example: `(0.15 − 0.10)² = 0.0025`, which is one contribution before averaging, not the complete batch loss.

The weight update is **θ ← θ − η d_Adam**. η is the learning rate, and d_Adam is Adam's adaptive direction computed from loss gradients. The deck deliberately does not describe the actual implementation as plain gradient descent or require students to derive Adam's moving averages. The Chinese notes explain the distinction and connect η directly to the required 0.001 / 0.0003 experiment.

The three equations are editable native PowerPoint text, including the fraction, summation and superscript/subscript runs. They are not screenshots. `slides.json` retains their notation, meanings, source references and revised narration.

## Media and data

The 15-second successful simulation video remains embedded on slide 2; click it in slideshow mode. It is explicitly labeled as half-speed playback. [A standalone copy](assets/success_half_speed.mp4) is included. The original failed rollout and all raw evidence extracts are retained as well.

No training, evaluation or simulation was repeated for this revision. Both videos are byte-identical to version 1. The success re-render's original 149-step state comparison and source identity are documented in [media_provenance.json](media_provenance.json). New plots use the same raw records with restrained blue/gray styling. The sample counts remain 2/5 and 3/5 for lr_a, 5/5 and 5/5 for lr_b; these are an attributed completed example, not promised outcomes or an algorithm ranking.

## Verification and limitations

[verification.json](verification.json) records nine English slides, Chinese notes on all slides, 600 seconds of planned narration, element bounds, PDF text coverage, editable equation presence, and correspondence between the formulas and the current BC/Adam code. All nine pages and the formula pages were rendered and visually inspected. The new PPTX embeds exactly the supplied MP4 bytes. Both videos fully decode; version 1's successful browser playback/seeking checks are carried forward only after byte identity is verified.

The PDF is a static handout and contains a video poster. Native playback on the instructor's Microsoft PowerPoint installation remains untested. The standalone MP4 provides a fallback. Install the supplied DejaVu Sans fonts if the presentation computer lacks them; the PDF needs no font installation.

[source_contract.json](source_contract.json) captures the current consulted working-tree files. Another user session owns the ongoing course deployment changes. This revision changes only this presentation directory and its independent plan, preserving the first deck, notebooks, training code and original results.

## Rebuild

Use the separate authoring dependencies in `authoring-requirements.txt`, keeping the student runtime unchanged. From the repository root:

```bash
uv venv /tmp/manipulation-slide-authoring
uv pip install --python /tmp/manipulation-slide-authoring/bin/python \
  -r presentations/assignment_intro_20261012_v2/authoring-requirements.txt
MPLCONFIGDIR=/tmp/manipulation-slide-mpl \
  /tmp/manipulation-slide-authoring/bin/python \
  presentations/assignment_intro_20261012_v2/build_deck.py \
  --static-output /tmp/manipulation-slide-static-v2/Manipulation_Learning_Lab.pptx
libreoffice -env:UserInstallation=file:///tmp/manipulation-slide-lo-v2 \
  --headless --convert-to pdf \
  --outdir presentations/assignment_intro_20261012_v2 \
  /tmp/manipulation-slide-static-v2/Manipulation_Learning_Lab.pptx
/tmp/manipulation-slide-authoring/bin/python \
  presentations/assignment_intro_20261012_v2/verify_deck.py
```

The slide build uses the included small evidence extracts. Verification of original source provenance additionally requires the recorded local run; carrying forward browser checks requires the retained first-version package. Pass `--browser /absolute/path/to/chrome` for a new playback check. The original high-resolution media generation script remains in the first-version directory and does not need to run for slide edits.
