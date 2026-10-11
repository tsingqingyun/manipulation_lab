"""One shared CSV schema: one explicitly selected run/learning-rate per row."""
import os
from pathlib import Path
from .common import sha256
from .notebook import stage_path
from .teaching import read_json, validate_control

CLASS_FIELDS = ["group", "run_id", "variant", "status", "error", "policy_role", "architecture", "epochs",
    "learning_rate", "seed", "selected_epoch", "validation_mse", "checkpoint_sha256",
    "standard_episodes", "standard_env_success_rate", "standard_stable_success_rate",
    "shifted_episodes", "shifted_env_success_rate", "shifted_stable_success_rate", "evaluation_errors",
    "failure_evidence_role", "failure_stage", "first_error_control_step", "first_observed_error",
    "hypothesized_cause", "improvement", "training_source", "evaluation_source", "instructor_notes"]


def variant_row(group, run, variant, training, evaluation, relative_to):
    settings = read_json(training / "training_config.json")
    train, result = read_json(training / "training_summary.json"), read_json(evaluation / "summary.json")
    if sha256(training / "student_policy.pth") != result["checkpoint_sha256"]:
        raise ValueError("Training/evaluation checkpoint mismatch")
    row = {"group": group, "run_id": run.name, "variant": variant, "status": "complete" if not result["errors"] else "evaluation_error",
        "error": "", "policy_role": result["policy_role"], "architecture": settings["architecture"],
        "epochs": train["epochs"], "learning_rate": settings["learning_rate"], "seed": settings["seed"],
        "selected_epoch": train["best_epoch"], "validation_mse": train["best_validation_mse"],
        "checkpoint_sha256": result["checkpoint_sha256"], "evaluation_errors": result["errors"],
        "training_source": os.path.relpath(training, relative_to), "evaluation_source": os.path.relpath(evaluation, relative_to)}
    for condition in ("standard", "shifted"):
        metrics = result["conditions"][condition]
        row.update({f"{condition}_episodes": metrics["episodes"],
            f"{condition}_env_success_rate": metrics["environment_success_rate"],
            f"{condition}_stable_success_rate": metrics["stable_success_rate"]})
    return row


def collect_run(run, relative_to):
    run = Path(run).resolve()
    group = read_json(run / "session.json")["group"]
    rows = []
    try:
        experiment = stage_path(run, "experiment")
        design = read_json(experiment / "experiment.json")
        if not design["complete"] or set(design["variants"]) != {"lr_a", "lr_b"}:
            raise ValueError("Mandatory two-learning-rate experiment is incomplete")
        entries = design["variants"]
        validate_control([experiment / entries[v]["training"] for v in ("lr_a", "lr_b")],
                         [experiment / entries[v]["evaluation"] for v in ("lr_a", "lr_b")])
        for variant, paths in entries.items():
            row = variant_row(group, run, variant, experiment / paths["training"], experiment / paths["evaluation"], relative_to)
            if (run / "analysis_current.json").exists():
                analysis = read_json(stage_path(run, "analysis") / "failure_analysis.json")
                if analysis.get("evidence_checkpoint_sha256") == row["checkpoint_sha256"]:
                    row.update({"failure_evidence_role": analysis["evidence_policy_role"], "failure_stage": analysis["stage"],
                        "first_error_control_step": analysis.get("first_error_control_step"),
                        "first_observed_error": analysis["first_observable_error"],
                        "hypothesized_cause": analysis["hypothesized_cause"], "improvement": analysis["improvement"]})
            rows.append(row)
    except (OSError, KeyError, ValueError) as exc:
        return [{"group": group, "run_id": run.name, "variant": v, "status": "incomplete_or_invalid", "error": str(exc)}
                for v in ("lr_a", "lr_b")]
    return rows
