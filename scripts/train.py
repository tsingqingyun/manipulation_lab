import _bootstrap
import argparse
import json
from manipulation_lab.common import DATA
from manipulation_lab.training import train

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--config", required=True)
    p.add_argument("--output", required=True)
    p.add_argument("--dataset", default=str(DATA))
    a = p.parse_args()
    print(json.dumps(train(json.load(open(a.config)), a.output, a.dataset), indent=2))
