"""Verify a trusted instructor checkpoint and prepare fresh, attributed failure evidence."""
import _bootstrap
import argparse
import shutil
import subprocess
import numpy as np
import imageio.v2 as imageio
from manipulation_lab.common import ROOT, DATA, new_output, sha256, write_json
from manipulation_lab.policy import load_policy
from manipulation_lab.teaching import read_json

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--checkpoint", default=str(ROOT / "checkpoints/instructor_reference.pth"))
    p.add_argument("--output", required=True)
    a = p.parse_args()
    output = new_output(a.output)
    _, checkpoint = load_policy(a.checkpoint)
    if checkpoint["lab_contract"]["role"] != "instructor_reference":
        raise ValueError("Expected an explicitly labeled instructor reference")
    if checkpoint["lab_contract"]["dataset_sha256"] != sha256(DATA):
        raise ValueError("Reference dataset mismatch")
    target = output / "instructor_reference.pth"
    shutil.copy2(a.checkpoint, target)
    subprocess.run([str(ROOT / "scripts/lab_python.sh"), str(ROOT / "scripts/evaluate.py"),
        "--checkpoint", str(target), "--config", str(ROOT / "configs/evaluation.yaml"),
        "--output", str(output / "reference_evaluation")], check=True, cwd=ROOT)
    summary = read_json(output / "reference_evaluation/summary.json")
    failure = next((r for r in summary["episodes"] if not r["stable_success"] and not r["error"] and r["video"]), None)
    if failure is None:
        raise RuntimeError("Reference evaluated, but no real failure was available; do not invent one")
    evaluation = output / "reference_evaluation"
    with np.load(evaluation / (failure["episode_id"] + ".npz")) as arrays:
        assert len(arrays["actions"]) == failure["steps"]
    reader = imageio.get_reader(evaluation / failure["video"])
    try:
        assert reader.get_data(0).shape[:2] == (256, 256)
    finally:
        reader.close()
    write_json(output / "reference_manifest.json", {"ready": True, "checkpoint_sha256": sha256(target),
        "role": summary["policy_role"], "conditions": summary["conditions"], "errors": summary["errors"],
        "failure_episode": failure["episode_id"], "failure_video": "reference_evaluation/" + failure["video"],
        "source": "existing real instructor model; fresh fixed-seed evaluation, no retraining"})
    print("Teacher checkpoint, fixed evaluation and real failure evidence are ready")
