import _bootstrap
import argparse
import json
import shutil
import time
import psutil
import torch
from manipulation_lab.common import DATA, new_output, versions, write_json
from manipulation_lab.simulator import compatibility_check

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--dataset", default=str(DATA))
    p.add_argument("--output", required=True)
    a = p.parse_args()
    output = new_output(a.output)
    start = time.monotonic()
    result = compatibility_check(a.dataset, output)
    result.update({"elapsed_seconds": time.monotonic() - start, "available_ram_gib": psutil.virtual_memory().available / 2**30,
        "free_disk_gib": shutil.disk_usage(output).free / 2**30, "cuda_available": torch.cuda.is_available(),
        "gpu": torch.cuda.get_device_name() if torch.cuda.is_available() else None})
    write_json(output / "preflight.json", result)
    print(json.dumps(result, indent=2))
