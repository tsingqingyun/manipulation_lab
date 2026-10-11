"""Real, deliberately small installation test; success rate is not a pass criterion."""
import _bootstrap
import argparse
import os
import time
import imageio.v2 as imageio
import numpy as np
from manipulation_lab.common import ROOT, DATA, new_output, write_json, versions
from manipulation_lab.notebook import command
from manipulation_lab.teaching import read_json

if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--output", required=True)
    p.add_argument("--dataset", default=str(DATA))
    p.add_argument("--device", choices=["cpu", "cuda"], default=os.environ.get("LAB_DEVICE", "cpu"))
    a = p.parse_args()
    output = new_output(a.output)
    start = time.monotonic()
    write_json(output / "smoke.json", {"passed": False, "status": "started"})
    command("preflight.py", "--dataset", a.dataset, "--output", output / "preflight")
    settings = read_json(ROOT / "configs/bc_student.json")
    settings.update(epochs=2, device=a.device)
    write_json(output / "config.json", settings)
    command("train.py", "--config", output / "config.json", "--device", a.device,
            "--dataset", a.dataset, "--output", output / "training")
    # evaluate.py's --episodes also freezes one shared test case for both conditions.
    command("evaluate.py", "--checkpoint", output / "training/student_policy.pth", "--dataset", a.dataset,
            "--config", ROOT / "configs/evaluation.yaml", "--episodes", 1, "--seeds", 101,
            "--output", output / "evaluation")
    result = read_json(output / "evaluation/summary.json")
    assert not result["errors"] and len(result["episodes"]) == 2
    for row in result["episodes"]:
        with np.load(output / "evaluation" / (row["episode_id"] + ".npz")) as trace:
            assert len(trace["actions"]) > 0 and np.isfinite(trace["actions"]).all()
            assert len(trace["object_position"]) == len(trace["actions"]) + 1
        reader = imageio.get_reader(output / "evaluation" / row["video"])
        try:
            assert reader.get_data(0).shape == (256, 256, 3)
        finally:
            reader.close()
    write_json(output / "smoke.json", {"passed": True, "device": a.device, "render_backend": os.environ.get("MUJOCO_GL"),
        "elapsed_seconds": time.monotonic() - start, "versions": versions(), "conditions": result["conditions"],
        "scope": "2 training epochs; real checkpoint loading and 2 closed-loop rollouts; not assignment completion"})
    print("PASS: dataset -> training -> checkpoint loading -> closed-loop simulation -> videos and metrics")
