import csv
import base64
import json
import os
import re
from pathlib import Path
import imageio.v2 as imageio
import matplotlib.pyplot as plt
import numpy as np
from .common import write_json


def notebook_report_markdown(path):
    """Embed report PNGs for Notebook display; keep the saved Markdown portable."""
    path = Path(path)
    def embed(match):
        image = (path.parent / match.group(2)).resolve()
        if image.suffix.lower() != ".png":
            raise ValueError("Expected a local PNG report figure")
        data = base64.b64encode(image.read_bytes()).decode("ascii")
        return f"![{match.group(1)}](data:image/png;base64,{data})"
    return re.sub(r"!\[([^\]]*)\]\(([^)]+)\)", embed, path.read_text())


def frame_selection(requested_steps, recorded_steps, total_steps):
    """Map state/control indices to the nearest actually recorded video frame."""
    recorded = np.asarray(recorded_steps)
    if not len(recorded) or np.any(np.diff(recorded) <= 0) or recorded[0] < 0 or recorded[-1] > total_steps:
        raise ValueError("Invalid video/control-step mapping")
    result = []
    for step in requested_steps:
        if isinstance(step, bool) or not isinstance(step, (int, np.integer)) or not 0 <= step <= total_steps:
            raise ValueError(f"Control step must be an integer in [0, {total_steps}]")
        index = int(np.argmin(np.abs(recorded - step)))
        result.append({"requested_control_step": int(step), "video_frame_index": index,
                       "recorded_control_step": int(recorded[index]), "offset_steps": int(recorded[index] - step)})
    return result


def failure_signal_figure(data, first_error_step=None):
    fig, axes = plt.subplots(4, 1, figsize=(8, 10), sharex=True)
    for i, label in enumerate("xyz"):
        axes[0].plot(data["eef_position"][:, i], label=label)
        axes[1].plot(data["object_position"][:, i], label=label)
    axes[0].set_ylabel("End effector (world m)"); axes[0].legend()
    axes[1].set_ylabel("Can (world m)"); axes[1].legend()
    axes[2].plot(data["gripper_width"])
    axes[2].set_ylabel("Gripper opening (m)")
    axes[3].step(np.arange(1, len(data["actions"])+1), data["actions"][:, -1], where="pre")
    axes[3].set(ylabel="Gripper command\n(normalized, +close)", ylim=(-1.1, 1.1),
                xlabel="Control step: action[t-1] leads to state[t]; 20Hz")
    if first_error_step is not None:
        for ax in axes:
            ax.axvline(first_error_step, color="crimson", linestyle="--", label="Student-marked first error")
        axes[3].legend(fontsize=8)
    fig.tight_layout()
    return fig


def failure_evidence(evaluation, episode, output, requested_steps=None, first_error_step=None):
    evaluation, output = Path(evaluation), Path(output)
    rows = json.loads((evaluation / "summary.json").read_text())["episodes"]
    row = next(r for r in rows if r["episode_id"] == episode)
    if row["stable_success"] or row["error"]:
        raise ValueError("Choose a completed, failed rollout for failure analysis")
    with np.load(evaluation / f"{episode}.npz") as archive:
        data = {k: archive[k] for k in archive.files}
    total = len(data["actions"])
    requested_steps = list(requested_steps) if requested_steps is not None else [0, total//2, total]
    if first_error_step is not None:
        frame_selection([first_error_step], [0, total] if total else [0], total)
        if first_error_step not in requested_steps:
            requested_steps.append(first_error_step)
    frames = []
    if row["video"]:
        reader = imageio.get_reader(evaluation / row["video"])
        try:
            n = reader.count_frames()
            if "video_control_steps" in data:
                recorded, mapping_source = data["video_control_steps"], "recorded_in_rollout"
            else:
                config = json.loads((evaluation / "evaluation_config.json").read_text())
                recorded = np.arange(0, total, config["video_stride"]) + 1
                mapping_source = "reconstructed_from_legacy_video_stride_and_post_action_sampling"
            if len(recorded) != n:
                raise ValueError("Video frame count does not match control-step mapping")
            frames = frame_selection(requested_steps, recorded, total)
            for i, frame in enumerate(frames):
                step = frame["requested_control_step"]
                frame["requested_state"] = {
                    "control_step": step, "control_elapsed_s": step / 20,
                    "eef_world_position_m": data["eef_position"][step].tolist(),
                    "object_world_position_m": data["object_position"][step].tolist(),
                    "gripper_opening_m": float(data["gripper_width"][step]),
                    "preceding_normalized_action": data["actions"][step - 1].tolist() if step else None}
                frame.update({"file": f"keyframe_{i}.png", "mapping_source": mapping_source})
                imageio.imwrite(output / frame["file"], reader.get_data(frame["video_frame_index"]))
        finally:
            reader.close()
    else:
        raise ValueError("Selected failure has no recorded video")
    fig = failure_signal_figure(data, first_error_step)
    fig.suptitle(f"{episode} · {row['policy_role']} · simulated world state / normalized command")
    fig.tight_layout(rect=(0, 0, 1, .97))
    fig.savefig(output / "failure_signals.png", dpi=140); plt.close(fig)
    facts = {"episode": episode, "source": "learned_policy_rollout", "environment_success": row["environment_success"],
        "stable_success": row["stable_success"], "initial_object_position_m": data["object_position"][0].tolist(),
        "final_object_position_m": data["object_position"][-1].tolist(),
        "max_object_lift_m": float(data["object_position"][:, 2].max() - data["object_position"][0, 2]),
        "final_gripper_width_m": float(data["gripper_width"][-1]),
        "automatic_failure_stage": "unknown; manual review required",
        "first_error_control_step": first_error_step, "first_error_source": "student_annotation" if first_error_step is not None else "not_marked",
        "keyframes": frames, "policy_role": row["policy_role"], "checkpoint_sha256": row["checkpoint_sha256"],
        "time_domain": "20Hz control indices, not acquisition timestamps; video frame indices differ"}
    write_json(output / "observed_facts.json", facts)
    return facts


def generate_report(run, output, training, evaluation, analysis):
    run, output = Path(run), Path(output)
    summary = json.loads((Path(evaluation) / "summary.json").read_text())
    train = json.loads((Path(training) / "training_summary.json").read_text())
    answers = json.loads((Path(analysis) / "failure_analysis.json").read_text())
    demonstration = json.loads((run / "demonstration_analysis.json").read_text())
    discussion_path = run / "discussion_answers.json"
    discussion = json.loads(discussion_path.read_text()) if discussion_path.exists() else {}
    complete = (all(str(discussion.get(k, "")).strip() for k in ("q2", "q3", "q4")) and all(str(answers.get(k, "")).strip() for k in ("stage", "first_observable_error", "hypothesized_cause", "improvement"))
                and answers.get("first_error_control_step") is not None and demonstration["answers_complete"])
    lines = ["# Manipulation Learning Lab — Group Report", "",
        f"Status: {'student answers provided; instructor review required' if complete else 'DRAFT — complete Q1–Q5 and mark the first observable error before submission'}", "",
        f"Run: `{run.name}`. Policy: **{summary['policy_name']}** ({summary['policy_role']}).",
        f"Training: {train['epochs']} epochs, selected epoch {train['best_epoch']}, validation action MSE {train['best_validation_mse']:.5f}; {train['elapsed_seconds']:.1f}s.", "",
        "| Condition | Episodes | Environment success | Stable released placement |", "|---|---:|---:|---:|"]
    for name, c in summary["conditions"].items():
        lines.append(f"| {name} | {c['episodes']} | {c['environment_success_rate']:.0%} | {c['stable_success_rate']:.0%} |")
    lines += ["", "Five episodes give a coarse classroom estimate. Position Shift Test is not a certified OOD benchmark.", "",
        "## Demonstration understanding", "", f"Q1: {demonstration.get('q1') or '[Complete this answer]'}", "",
        f"Demonstration reflection: {demonstration.get('q2') or '[Complete this answer]'}", "",
        "## Training and evaluation discussion", "",
        f"Q2 — How BC learns: {discussion.get('q2') or '[Complete this answer]'}", "",
        f"Q3 — Loss versus performance: {discussion.get('q3') or '[Complete this answer]'}", "",
        f"Q4 — Initial position: {discussion.get('q4') or '[Complete this answer]'}", "",
        "Q5 is addressed by the failure analysis below.", "",
        "## Failure analysis", "", f"Episode: {answers.get('episode', '')}; evidence policy role: {answers.get('evidence_policy_role', 'unknown')}.", ""]
    for key, title in [("stage", "Failure stage"), ("first_observable_error", "First observable error — fact"),
                       ("hypothesized_cause", "Possible cause — hypothesis"), ("improvement", "Proposed improvement")]:
        lines += [f"**{title}:** {answers.get(key) or '[Complete this answer]'}", ""]
    lines += [f"**First error control step (student annotation):** {answers.get('first_error_control_step')}", "",
              f"![Training curve]({os.path.relpath(Path(training) / 'training_curve.png', output)})", "",
              f"![Failure signals]({os.path.relpath(Path(analysis) / 'failure_signals.png', output)})", "",
              "## Evidence and limits", "",
              f"Checkpoint SHA256: `{summary['checkpoint_sha256']}`.",
              "Positions are simulator world coordinates in meters; logs use 20Hz control steps. No real-robot claim is made.",
              "Attach training_config.json, training_log.csv, evaluation results/config/manifest, and 3 keyframes. Keep raw artifacts separately."]
    facts = json.loads((Path(analysis) / "observed_facts.json").read_text())
    for frame in facts.get("keyframes", []):
        lines += ["", f"Requested control step {frame['requested_control_step']}; recorded step {frame['recorded_control_step']} "
                  f"(offset {frame['offset_steps']:+d}); video frame {frame['video_frame_index']}.",
                  f"![Selected keyframe]({os.path.relpath(Path(analysis) / frame['file'], output)})"]
    experiment = None
    if (run / "experiment_current.json").exists():
        from .notebook import stage_path
        experiment = stage_path(run, "experiment")
        design = json.loads((experiment / "experiment.json").read_text())
        if not design["complete"]:
            raise ValueError("Mandatory controlled experiment is incomplete")
        lines += ["", "## Mandatory learning-rate controlled experiment", "",
                  "Data, initialization, seed, architecture, epochs and evaluation cases are fixed. Both variants are retained; test results do not select the primary model.", "",
                  "| Variant | Learning rate | Validation MSE | Standard stable | Shifted stable |",
                  "|---|---:|---:|---:|---:|"]
        for r in design["comparison"]:
            lines.append(f"| {r['variant']} | {r['learning_rate']} | {r['validation_mse']:.6f} | {r['standard_stable_success_rate']:.0%} | {r['shifted_stable_success_rate']:.0%} |")
        lines += ["", f"![Both training curves]({os.path.relpath(experiment / 'learning_rate_curves.png', output)})", "",
                  f"![Initial positions]({os.path.relpath(Path(evaluation) / 'initial_positions.png', output)})"]
    (output / "report.md").write_text("\n".join(lines) + "\n")
    write_json(output / "submission_manifest.json", {"run": os.path.relpath(run, output), "training": os.path.relpath(training, output),
        "evaluation": os.path.relpath(evaluation, output), "analysis": os.path.relpath(analysis, output),
        "experiment": os.path.relpath(experiment, output) if experiment else None,
        "answers_complete": complete, "checkpoint_sha256": summary["checkpoint_sha256"]})
    return output / "report.md"
