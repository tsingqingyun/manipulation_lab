import csv
import json
import os
from pathlib import Path
import imageio.v2 as imageio
import matplotlib.pyplot as plt
import numpy as np
from .common import write_json


def failure_evidence(evaluation, episode, output):
    evaluation, output = Path(evaluation), Path(output)
    rows = json.loads((evaluation / "summary.json").read_text())["episodes"]
    row = next(r for r in rows if r["episode_id"] == episode)
    if row["stable_success"]:
        raise ValueError("Choose a failed rollout for failure analysis")
    data = np.load(evaluation / f"{episode}.npz")
    fig, axes = plt.subplots(3, 1, figsize=(8, 8), sharex=True)
    for i, label in enumerate("xyz"):
        axes[0].plot(data["eef_position"][:, i], label=label)
        axes[1].plot(data["object_position"][:, i], label=label)
    axes[0].set_ylabel("End effector (world m)"); axes[0].legend()
    axes[1].set_ylabel("Can (world m)"); axes[1].legend()
    axes[2].plot(data["gripper_width"], label="width (m)")
    axes[2].plot(np.arange(1, len(data["actions"])+1), data["actions"][:, -1], label="gripper command (+close)")
    axes[2].set_xlabel("Control step (20Hz, no acquisition timestamps)"); axes[2].legend()
    fig.tight_layout(); fig.savefig(output / "failure_signals.png", dpi=140); plt.close(fig)
    if row["video"]:
        reader = imageio.get_reader(evaluation / row["video"])
        n = reader.count_frames()
        for i, step in enumerate([0, n//2, n-1]):
            imageio.imwrite(output / f"keyframe_{i}.png", reader.get_data(step))
        reader.close()
    facts = {"episode": episode, "source": "learned_policy_rollout", "environment_success": row["environment_success"],
        "stable_success": row["stable_success"], "initial_object_position_m": data["object_position"][0].tolist(),
        "final_object_position_m": data["object_position"][-1].tolist(),
        "max_object_lift_m": float(data["object_position"][:, 2].max() - data["object_position"][0, 2]),
        "final_gripper_width_m": float(data["gripper_width"][-1]),
        "automatic_failure_stage": "unknown; manual review required"}
    write_json(output / "observed_facts.json", facts)
    return facts


def generate_report(run, output, training, evaluation, analysis):
    run, output = Path(run), Path(output)
    summary = json.loads((Path(evaluation) / "summary.json").read_text())
    train = json.loads((Path(training) / "training_summary.json").read_text())
    answers = json.loads((Path(analysis) / "failure_analysis.json").read_text())
    demonstration = json.loads((run / "demonstration_analysis.json").read_text())
    complete = all(str(answers.get(k, "")).strip() for k in ("stage", "first_observable_error", "hypothesized_cause", "improvement")) and demonstration["answers_complete"]
    lines = ["# Manipulation Learning Lab — Group Report", "",
        f"Status: {'student answers provided; instructor review required' if complete else 'DRAFT — fill in your failure-analysis answers before submission'}", "",
        f"Run: `{run.name}`. Policy: **{summary['policy_name']}** ({summary['policy_role']}).",
        f"Training: {train['epochs']} epochs, selected epoch {train['best_epoch']}, validation action MSE {train['best_validation_mse']:.5f}; {train['elapsed_seconds']:.1f}s.", "",
        "| Condition | Episodes | Environment success | Stable released placement |", "|---|---:|---:|---:|"]
    for name, c in summary["conditions"].items():
        lines.append(f"| {name} | {c['episodes']} | {c['environment_success_rate']:.0%} | {c['stable_success_rate']:.0%} |")
    lines += ["", "Five episodes give a coarse classroom estimate. Position Shift Test is not a certified OOD benchmark.", "",
        "## Demonstration understanding", "", f"Q1: {demonstration.get('q1') or '[Complete this answer]'}", "",
        f"Q2: {demonstration.get('q2') or '[Complete this answer]'}", "",
        "## Failure analysis", "", f"Episode: {answers.get('episode', '')}; evidence policy role: {answers.get('evidence_policy_role', 'unknown')}.", ""]
    for key, title in [("stage", "Failure stage"), ("first_observable_error", "First observable error — fact"),
                       ("hypothesized_cause", "Possible cause — hypothesis"), ("improvement", "Proposed improvement")]:
        lines += [f"**{title}:** {answers.get(key) or '[Complete this answer]'}", ""]
    lines += [f"![Training curve]({os.path.relpath(Path(training) / 'training_curve.png', output)})", "",
              f"![Failure signals]({os.path.relpath(Path(analysis) / 'failure_signals.png', output)})", "",
              "## Evidence and limits", "",
              f"Checkpoint SHA256: `{summary['checkpoint_sha256']}`.",
              "Positions are simulator world coordinates in meters; logs use 20Hz control steps. No real-robot claim is made.",
              "Attach training_config.json, training_log.csv, evaluation results/config/manifest, and 3 keyframes. Keep raw artifacts separately."]
    (output / "report.md").write_text("\n".join(lines) + "\n")
    write_json(output / "submission_manifest.json", {"run": str(run), "training": str(training), "evaluation": str(evaluation),
        "analysis": str(analysis), "answers_complete": complete, "checkpoint_sha256": summary["checkpoint_sha256"]})
    return output / "report.md"
