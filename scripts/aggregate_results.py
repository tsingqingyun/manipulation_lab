import _bootstrap
import argparse
import csv
import json
from pathlib import Path

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--summaries", nargs="+", required=True, help="Explicit summary.json files; no implicit best-run selection")
    p.add_argument("--output", required=True)
    a = p.parse_args()
    rows = []
    for path in a.summaries:
        s = json.loads(Path(path).read_text())
        for condition, c in s["conditions"].items():
            rows.append({"source": str(Path(path).resolve()), "policy": s["policy_name"], "role": s["policy_role"],
                "checkpoint_sha256": s["checkpoint_sha256"], "condition": condition, **c,
                "observed_failure": "", "hypothesized_cause": "", "improvement": "", "instructor_notes": ""})
    with open(a.output, "x", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0])); writer.writeheader(); writer.writerows(rows)
