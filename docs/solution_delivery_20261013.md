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

## 中文可视化修订版（同日）

按最新要求，保留原浅色底、蓝灰与暖棕配色及衬线标题，正文、图表说明和讲稿
改为中文，公式及变量保持英文记号。新增独立目录
[`assignment_solutions_20261013_zh_v2`](../presentations/assignment_solutions_20261013_zh_v2/README.md)，
保留原版材料；15 页讲稿共 880 秒。补充观察/动作图解、放大的实验曲线、逐案例
配对图、抓取近景以及与数值对齐的失败关键帧。

本次新增训练与策略评测均为 0。重放保存动作只改变相机：成功 141 步、失败前
101 步；核对的物体/末端位置、夹爪关节与开口差均为 0，全部布尔记录一致。
两段半速视频以 960×544 编码，近景静帧为 960×640。首次相机更新额外调用
`sim.forward()` 导致约 0.075 mm 差异，失败尝试保留并排除；修正为只更新相机
变换，没有放宽标准。具体来源、帧映射和失败记录见 `replay_provenance.json`。

原结果和四份 Notebook 做哈希比对，内容未改。制稿验证覆盖 15 页、正文字符
完整性、中文字体、英文公式、媒体解码及嵌入哈希，并检查逐页视觉排版。
随包提供简体中文正文与标题字体，保留许可，核对改名前后全部字形及字符映射一致。
模型、数据、训练/评测逻辑、学生模板均未改。仍未实测授课电脑上的原生
PowerPoint 视频播放，也未执行失败原因干预实验。
