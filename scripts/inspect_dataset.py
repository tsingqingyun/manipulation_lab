import _bootstrap
import argparse
from manipulation_lab.common import DATA, new_output, write_json
from manipulation_lab.dataset import inspect

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--dataset", default=str(DATA))
    p.add_argument("--output", required=True)
    a = p.parse_args()
    output = new_output(a.output)
    result = inspect(a.dataset)
    write_json(output / "dataset_inspection.json", result)
    print({k: result[k] for k in ("episode_count", "total_steps", "observation_shapes", "time")})
