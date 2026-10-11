import _bootstrap
import argparse
import json
import yaml
from manipulation_lab.common import DATA
from manipulation_lab.evaluation import evaluate

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--checkpoint", required=True)
    p.add_argument("--config", required=True)
    p.add_argument("--output", required=True)
    p.add_argument("--dataset", default=str(DATA))
    p.add_argument("--episodes", type=int)
    p.add_argument("--seeds", type=int, nargs="+")
    a = p.parse_args()
    config = yaml.safe_load(open(a.config))
    if a.episodes is not None:
        config["episodes_per_condition"] = a.episodes
    if a.seeds is not None:
        config["seeds"] = a.seeds
    result = evaluate(a.checkpoint, config, a.output, a.dataset)
    print(json.dumps(result["conditions"], indent=2))
    if result["errors"]:
        raise SystemExit("Evaluation completed with recorded errors; do not mark acceptance passed")
