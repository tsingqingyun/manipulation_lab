"""Teaching comparisons layered on the unchanged training/evaluation entrypoints."""
import csv
import copy
import json
import subprocess
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
from .common import ROOT, DATA, new_output, sha256, write_json


def read_json(path):
    return json.loads(Path(path).read_text())


def markdown_table(rows, columns=None):
    columns = columns or list(rows[0])
    lines = ["| " + " | ".join(columns) + " |", "| " + " | ".join(["---"] * len(columns)) + " |"]
    lines += ["| " + " | ".join(str(row.get(k, "")).replace("|", "\\|") for k in columns) + " |" for row in rows]
    return "\n".join(lines)


def controlled_settings(base, rates):
    if len(rates) != 2 or len(set(rates)) != 2 or not all(np.isfinite(x) and x > 0 for x in rates):
        raise ValueError("Choose exactly two distinct positive learning rates")
    return {name: {**copy.deepcopy(base), "learning_rate": rate}
            for name, rate in zip(("lr_a", "lr_b"), rates)}


def validate_control(training_dirs, evaluation_dirs):
    settings = [read_json(p / "training_config.json") for p in training_dirs]
    changed = {k for k in settings[0].keys() | settings[1].keys() if settings[0].get(k) != settings[1].get(k)}
    if changed != {"learning_rate"}:
        raise ValueError(f"Only learning_rate may change, got {changed}")
    summaries = [read_json(p / "training_summary.json") for p in training_dirs]
    for key in ("dataset_sha256", "splits", "versions"):
        if summaries[0]["contract"][key] != summaries[1]["contract"][key]:
            raise ValueError(f"Training contract differs: {key}")
    if summaries[0]["initial_weights_sha256"] != summaries[1]["initial_weights_sha256"]:
        raise ValueError("Initial model weights differ")
    for filename in ("evaluation_config.json", "test_manifest.json"):
        if read_json(evaluation_dirs[0] / filename) != read_json(evaluation_dirs[1] / filename):
            raise ValueError(f"Evaluation differs: {filename}")
    for training, evaluation in zip(training_dirs, evaluation_dirs):
        result = read_json(evaluation / "summary.json")
        if result["errors"] or result["checkpoint_sha256"] != sha256(training / "student_policy.pth"):
            raise ValueError("Incomplete evaluation or checkpoint mismatch")
    return {"only_learning_rate_changed": True, "same_initial_weights": True,
            "same_dataset_split_versions": True, "same_evaluation_config_and_cases": True}


def paired_cases(summary):
    by_key = {}
    for row in summary["episodes"]:
        key = (row["source_episode"], row["seed"])
        pair = by_key.setdefault(key, {})
        condition = row["condition"]
        if condition in pair:
            raise ValueError(f"Duplicate paired case: {key} {condition}")
        pair[condition] = row
    records = []
    for (episode, seed), pair in by_key.items():
        if set(pair) != {"standard", "shifted"}:
            raise ValueError(f"Missing paired condition for {episode}/{seed}")
        record = {"source_episode": episode, "seed": seed}
        for condition, r in pair.items():
            for key in ("episode_id", "environment_success", "stable_success", "steps", "error"):
                record[f"{condition}_{key}"] = r[key]
        records.append(record)
    return records


def write_csv(path, rows, fields=None):
    with open(path, "x", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields or list(rows[0]), lineterminator="\n")
        writer.writeheader(); writer.writerows(rows)


def position_plot(inspection, summary, output):
    lookup = {e["episode"]: e["initial_object_position_m"] for e in inspection["episodes"]}
    train = np.asarray([lookup[e] for e in inspection["splits"]["train"]])
    fig, ax = plt.subplots(figsize=(7, 5))
    ax.scatter(train[:, 0], train[:, 1], s=16, alpha=.45, label="Training demonstration initial positions")
    plotted = {}
    for condition, marker in [("standard", "o"), ("shifted", "x")]:
        rows = [r for r in summary["episodes"] if r["condition"] == condition and r["initial_object_position"] is not None]
        plotted[condition] = {r["source_episode"]: json.loads(r["initial_object_position"]) for r in rows}
        positions = np.asarray(list(plotted[condition].values()))
        if len(positions):
            ax.scatter(positions[:, 0], positions[:, 1], s=70, marker=marker, label=f"Evaluated {condition} starts")
    for case, start in plotted["standard"].items():
        end = plotted["shifted"].get(case)
        if end is not None:
            ax.plot([start[0], end[0]], [start[1], end[1]], color="gray", linewidth=.6)
            ax.annotate(case, start[:2], fontsize=7)
    ax.set(xlabel="Can initial world X (m)", ylabel="Can initial world Y (m)",
           title="2D position coverage does not certify OOD")
    ax.set_aspect("equal", adjustable="datalim"); ax.legend(fontsize=8)
    fig.tight_layout(); fig.savefig(output, dpi=140); plt.close(fig)


def run_experiment(base, design, evaluation_config, output, dataset=DATA):
    output = new_output(output)
    variants = controlled_settings(base, design["learning_rates"])
    if design["primary_variant"] not in variants:
        raise ValueError("Unknown preselected primary variant")
    manifest = {"schema_version": 1, "complete": False, "primary_variant": design["primary_variant"],
                "selection_rule": design["selection_rule"], "variants": {}}
    write_json(output / "experiment.json", manifest)
    import yaml
    (output / "evaluation.yaml").write_text(yaml.safe_dump(evaluation_config))
    training_dirs, evaluation_dirs, comparison = [], [], []
    fig, axes = plt.subplots(1, 2, figsize=(11, 4))
    try:
        for name, settings in variants.items():
            variant = output / name; variant.mkdir()
            write_json(variant / "config.json", settings)
            training, evaluation = variant / "training", variant / "evaluation"
            for script, args in [
                ("train.py", ["--config", variant / "config.json", "--dataset", dataset, "--output", training]),
                ("evaluate.py", ["--checkpoint", training / "student_policy.pth", "--config", output / "evaluation.yaml",
                                  "--dataset", dataset, "--output", evaluation])]:
                subprocess.run([str(ROOT / "scripts/lab_python.sh"), str(ROOT / "scripts" / script), *map(str, args)],
                               cwd=ROOT, check=True)
            train, result = read_json(training / "training_summary.json"), read_json(evaluation / "summary.json")
            manifest["variants"][name] = {"learning_rate": settings["learning_rate"],
                "training": str(training.relative_to(output)), "evaluation": str(evaluation.relative_to(output)),
                "checkpoint_sha256": result["checkpoint_sha256"]}
            write_json(output / "experiment.json", manifest)
            with open(training / "training_log.csv") as f:
                history = list(csv.DictReader(f))
            for ax, metric in zip(axes, ("training_loss", "validation_loss")):
                ax.plot([int(r["epoch"]) for r in history], [float(r[metric]) for r in history], label=f"LR {settings['learning_rate']}")
                ax.set(xlabel="Epoch", ylabel=metric.replace("_", " ") + " (action MSE)", yscale="log"); ax.legend()
            write_csv(evaluation / "paired_results.csv", paired_cases(result))
            position_plot(read_json(training / "dataset_inspection.json"), result, evaluation / "initial_positions.png")
            row = {"variant": name, "learning_rate": settings["learning_rate"], "epochs": train["epochs"],
                   "seed": settings["seed"], "selected_epoch": train["best_epoch"], "validation_mse": train["best_validation_mse"]}
            for condition, metrics in result["conditions"].items():
                row[f"{condition}_stable_success_rate"] = metrics["stable_success_rate"]
            comparison.append(row); training_dirs.append(training); evaluation_dirs.append(evaluation)
        manifest["checks"] = validate_control(training_dirs, evaluation_dirs)
        fig.tight_layout(); fig.savefig(output / "learning_rate_curves.png", dpi=140)
        write_csv(output / "comparison.csv", comparison)
        manifest["comparison"] = comparison
        manifest["complete"] = True
        write_json(output / "experiment.json", manifest)
        return manifest
    finally:
        plt.close(fig)
