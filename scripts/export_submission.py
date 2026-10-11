"""Package a group's current run and attributed failure video without altering evidence."""
import _bootstrap
import argparse
import json
from pathlib import Path
import zipfile
from manipulation_lab.common import sha256
from manipulation_lab.notebook import workspace, stage_path
from manipulation_lab.classroom import collect_run, CLASS_FIELDS
from manipulation_lab.teaching import read_json
import csv
import io

if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--run", help="Explicit run directory; defaults to the selected group's current session")
    p.add_argument("--output", required=True, help="NEW ZIP file")
    a = p.parse_args()
    run = Path(a.run).resolve() if a.run else workspace()
    report = stage_path(run, "report")
    manifest = read_json(report / "submission_manifest.json")
    rows = collect_run(run, run)
    if any(r["status"] != "complete" for r in rows):
        raise ValueError("Complete both training/evaluation variants before exporting")
    for row in rows:
        for key in ("training_source", "evaluation_source"):
            row[key] = "run/" + row[key]
    analysis = stage_path(run, "analysis")
    answers = read_json(analysis / "failure_analysis.json")
    source = (analysis / answers["evidence_directory"]).resolve()
    result = read_json(source / "summary.json")
    case = next(r for r in result["episodes"] if r["episode_id"] == answers["episode"])
    entries = {"run/" + str(f.relative_to(run)): f for f in run.rglob("*") if f.is_file() and not f.is_symlink()}
    entries["failure_source/rollout.mp4"] = source / case["video"]
    entries["failure_source/trace.npz"] = source / (case["episode_id"] + ".npz")
    entries["failure_source/summary.json"] = source / "summary.json"
    output = Path(a.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "x", compression=zipfile.ZIP_DEFLATED) as archive:
        for name, path in sorted(entries.items()):
            archive.write(path, name)
        text = io.StringIO()
        writer = csv.DictWriter(text, fieldnames=CLASS_FIELDS, lineterminator="\n")
        writer.writeheader(); writer.writerows(rows)
        archive.writestr("class_results.csv", text.getvalue())
        archive.writestr("export_manifest.json", json.dumps({"answers_complete": manifest["answers_complete"],
            "report": "run/" + str((report / "report.md").relative_to(run)),
            "failure_role": result["policy_role"], "files_sha256": {name: sha256(path) for name, path in entries.items()},
            "note": "Local session pointers are provenance; plots and report links are relative. Add your 1–2 page report."}, indent=2))
    print(f"Saved {output}; answers_complete={manifest['answers_complete']}. Add your 1–2 page report before submission.")
