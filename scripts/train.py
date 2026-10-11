import _bootstrap
import argparse
import os
import json
from manipulation_lab.common import DATA
from manipulation_lab.training import train

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--config", required=True)
    p.add_argument("--output", required=True)
    p.add_argument("--dataset", default=str(DATA))
    p.add_argument("--device", choices=["cpu", "cuda"], default=os.environ.get("LAB_DEVICE"))
    a = p.parse_args()
    settings = json.load(open(a.config))
    if a.device:
        settings["device"] = a.device
    print(json.dumps(train(settings, a.output, a.dataset), indent=2))
