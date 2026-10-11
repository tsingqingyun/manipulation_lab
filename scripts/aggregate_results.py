import _bootstrap
import argparse
from pathlib import Path
from manipulation_lab.classroom import CLASS_FIELDS, collect_run
from manipulation_lab.teaching import read_json, write_csv

if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Aggregate explicit runs, retaining both learning rates and incomplete rows")
    source = p.add_mutually_exclusive_group(required=True)
    source.add_argument("--runs", nargs="+", help="Explicit group run directories; never auto-select the best run")
    source.add_argument("--selection", help="JSON mapping six groups to run paths, relative to that JSON")
    p.add_argument("--output", required=True)
    a = p.parse_args()
    if a.selection:
        selection = Path(a.selection).resolve()
        chosen = read_json(selection)
        if set(chosen) != {f"group_{i:02d}" for i in range(1, 7)}:
            p.error("Selection must explicitly list all six groups")
        runs = [selection.parent / path for path in chosen.values()]
        for group, run in zip(chosen, runs):
            if read_json(run / "session.json")["group"] != group:
                p.error(f"Group identity mismatch for {group}")
    else:
        runs = [Path(x).resolve() for x in a.runs]
    if len({str(p.resolve()) for p in runs}) != len(runs):
        p.error("Duplicate run selection")
    rows = [row for run in runs for row in collect_run(run, Path(a.output).resolve().parent)]
    write_csv(a.output, rows, CLASS_FIELDS)
    print(f"Saved {len(rows)} rows with the class_results.csv schema")
    if any(r["status"] != "complete" for r in rows):
        raise SystemExit("Incomplete/invalid results retained in CSV; classroom acceptance did not pass")
