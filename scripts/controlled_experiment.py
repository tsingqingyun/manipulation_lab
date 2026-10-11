import _bootstrap
import argparse
import os
import json
from pathlib import Path
import yaml
from manipulation_lab.common import ROOT, DATA
from manipulation_lab.teaching import read_json, run_experiment

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--config", default=str(ROOT / "configs/bc_student.json"))
    p.add_argument("--design", default=str(ROOT / "configs/controlled_experiment.json"))
    p.add_argument("--evaluation-config", default=str(ROOT / "configs/evaluation.yaml"))
    p.add_argument("--dataset", default=str(DATA))
    p.add_argument("--output", required=True)
    p.add_argument("--device", choices=["cpu", "cuda"], default=os.environ.get("LAB_DEVICE"))
    a = p.parse_args()
    settings = read_json(a.config)
    if a.device:
        settings["device"] = a.device
    result = run_experiment(settings, read_json(a.design),
                            yaml.safe_load(Path(a.evaluation_config).read_text()), a.output, a.dataset)
    print(json.dumps(result["comparison"], indent=2))
