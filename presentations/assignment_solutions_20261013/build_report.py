"""Produce the two-page instructor answer report from the verified run."""
import json
from pathlib import Path
import pymupdf

HERE = Path(__file__).resolve().parent
d = json.loads((HERE / "results.json").read_text())
doc = pymupdf.open()
css = "body {font-family: sans-serif; font-size: 10.5pt; color: #252c30;} h2 {font-size: 13pt; color: #3f7085; margin: 12px 0 5px;} p {margin: 5px 0 8px;} table {border-collapse:collapse; width:100%;} td,th {border-bottom:1px solid #aaa; padding:5px; text-align:left;} .small {font-size:9pt;}"


def page(title, body, bottom=775):
    p = doc.new_page(width=595, height=842)
    p.insert_text((40, 36), title, fontsize=18, fontname="hebo", color=(.15,.2,.22))
    p.insert_text((40, 53), "Manipulation Learning Lab | Instructor reference | 13 October 2026", fontsize=9, color=(.39,.42,.44))
    spare, scale = p.insert_htmlbox(pymupdf.Rect(40,65,555,bottom), body, css=css, scale_low=1)
    assert spare >= 0 and scale == 1, "Report overflow: edit content instead of shrinking it"
    p.insert_text((40, 820), f"{len(doc)} / 2    Full logs, model hashes, videos and answers are included in the accompanying evidence.", fontsize=8)
    return p


page("Worked solutions: Q1–Q4", """
<p class='small'><b>Run:</b> 20261013T051828Z_5a8ae81c, group_01. Dataset SHA256 prefix: 3f2eb92e0a50.
The original four notebooks completed in 237.65 s; all 20 evaluations completed without runtime errors.</p>
<h2>Q1. What does the policy observe and command?</h2>
<p>The 16 observations are end-effector world position (3), xyzw quaternion (4), two finger joint positions (2),
and can world position plus xyzw quaternion (7). World Z points upward; positions and finger displacement are meters.
The seven actions contain world translation increments (3), axis-angle rotation increments (3), and one gripper command (1).
Normalized [-1,1] commands map to controller limits of ±0.05 m / ±0.5 rad; positive gripper commands close and negative open.
Two observed finger joints still use one open/close action. Control runs at 20 Hz.</p>
<p>A trajectory shows approach, closure, lift and release order and provides observation/action training pairs.
A final image cannot show this sequence. Human playback restores recorded states; it is not policy evaluation.</p>
<h2>Q2. How does behavior cloning learn?</h2>
<p>A deterministic 256/256/256 multilayer perceptron predicts seven expert actions from each observation.
Gradient updates minimize mean squared action error. Whole episodes are split 160/20/20; only training observations set
normalization. Validation loss chooses the checkpoint, and test results never update weights or select the primary model.
Only learning rate changes: seed 17, 50 epochs, batch 256, initialization, data, architecture and test cases are fixed.
All four control checks passed. Both selected epoch 12; lr_a remained primary.</p>
<h2>Q3. Does lower training loss guarantee better manipulation?</h2>
<table><tr><th>Variant</th><th>Final train MSE</th><th>Best val. MSE</th><th>Standard / shifted</th></tr>
<tr><td>lr_a: 0.001</td><td>0.017717</td><td>0.035376</td><td>3/5 / 3/5</td></tr>
<tr><td>lr_b: 0.0003</td><td>0.020919</td><td>0.034123</td><td>5/5 / 5/5</td></tr></table>
<p>No. lr_a has lower final training error but fewer stable placements. These rollouts use epoch-12 selected checkpoints,
not epoch-50 weights. Closed-loop actions change future observations; prediction error on demonstration states does not
measure recovery or task completion. Five cases and one training seed cannot establish a general learning-rate ranking.</p>
<h2>Q4. What changes under the position shift?</h2>
<p>Each paired case keeps its source state and seed, adding 0.04 m to can world X. All success/failure labels stay the same here,
but lr_a on demo_185 / seed 102 takes 141 standard versus 156 shifted steps (+0.75 s). A possible cause is altered approach
geometry; timing alone cannot prove it. The coverage plot contains initial XY positions and paired-start lines, not trajectories
or success labels. Position overlap can remain, and XY omits other inputs: this is not certified out-of-distribution testing.</p>
""")
p = page("Worked solution: Q5 and evidence limits", """
<h2>Q5. Locate a failure; distinguish fact, hypothesis and test</h2>
<p><b>Case:</b> primary student lr_a, standard_00, demo_39, seed 101; 500-step failure.
<b>Stage:</b> grasp retention / beginning of lift. Contact is present at states 49–56 and first disappears at 57,
remaining absent afterward. State 57 is the earliest directly supported contact-loss annotation, not a proven earliest root cause.</p>
<p><b>Measured fact:</b> at state 57, opening is 0.022398 m, end-effector Z is 0.883759 m and can Z is 0.864667 m;
the preceding action commands closure near +1. At 65, end-effector Z rises to 0.962711 m while can Z returns to 0.860271 m.
Maximum lift is just 5.72 mm; the can never enters the target. The arm lifts without retaining it.</p>
<p><b>Timing:</b> a[t−1] leads to s[t]. States 45, 53, 57 and 65 map to video frames 11, 13, 14 and 16, with zero offset.
Videos record after every fourth action; state 0 has no exact video frame. Step 57 means 2.85 seconds of simulated control time.</p>
<p><b>Hypothesis:</b> approach alignment or closure/lift timing may prevent secure retention. Brief contact and a positive close
command do not prove a stable grasp. The trace cannot distinguish these mechanisms or prove distribution shift.</p>
<p><b>Proposed controlled test, not executed:</b> capture identical simulator/controller and random state just before closure.
Compare the unchanged continuation against a predefined five-step closure hold at the pre-lift pose, then resume the same policy.
Change only this timing intervention. Compare contact duration, relative can lift and stable placement on matched cases.
Improvement would support a timing contribution; absence of improvement would leave other causes unresolved.</p>
<p><b>Limits:</b> one fixed training seed, five paired cases per condition, simulation only. Stable placement requires target-margin
containment, open gripper and no contact for a full second of continued policy execution, with displacement ≤1 cm and speed ≤5 cm/s.
The recorded failure supports the fact of lost retention, not a guaranteed fix.</p>
""", bottom=575)
p.insert_image(pymupdf.Rect(40,588,285,775), filename=str(HERE / "assets/keyframe_2.png"), keep_proportion=True)
p.insert_image(pymupdf.Rect(305,588,550,775), filename=str(HERE / "assets/keyframe_3.png"), keep_proportion=True)
p.insert_text((73,794), "State 57 / frame 14: contact lost", fontsize=9)
p.insert_text((328,794), "State 65 / frame 16: empty lift", fontsize=9)
doc.save(HERE / "Instructor_Solution_Report.pdf")
print("Saved two-page report")
