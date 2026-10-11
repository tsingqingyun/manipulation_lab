import _bootstrap
import argparse
import json
from manipulation_lab.common import new_output
from manipulation_lab.notebook import stage_path
from manipulation_lab.reporting import generate_report

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--run", required=True)
    p.add_argument("--output", required=True)
    a = p.parse_args()
    output = new_output(a.output)
    from pathlib import Path
    if (Path(a.run) / "experiment_current.json").exists():
        experiment = stage_path(a.run, "experiment")
        manifest = json.loads((experiment / "experiment.json").read_text())
        primary = manifest["variants"][manifest["primary_variant"]]
        training, evaluation = experiment / primary["training"], experiment / primary["evaluation"]
    else:
        training, evaluation = stage_path(a.run, "training"), stage_path(a.run, "evaluation")
    print(generate_report(a.run, output, training, evaluation, stage_path(a.run, "analysis")))
