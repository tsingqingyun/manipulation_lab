"""Verify a trusted instructor checkpoint and prepare fresh, attributed failure evidence."""
import _bootstrap
import argparse
import os
from pathlib import Path
import shutil
import subprocess
import numpy as np
import imageio.v2 as imageio
from manipulation_lab.common import ROOT, DATA, new_output, sha256, write_json
from manipulation_lab.policy import load_policy
from manipulation_lab.teaching import read_json

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    source = p.add_mutually_exclusive_group()
    source.add_argument("--checkpoint", help="Existing trusted lab instructor checkpoint")
    source.add_argument("--train", action="store_true", help="Generate the fixed reference from the public dataset")
    p.add_argument("--dataset", default=str(DATA))
    p.add_argument("--device", choices=["cpu", "cuda"], default=os.environ.get("LAB_DEVICE", "cuda"))
    p.add_argument("--output", required=True)
    a = p.parse_args()
    output = new_output(a.output)
    if a.train:
        subprocess.run([str(ROOT / "scripts/lab_python.sh"), str(ROOT / "scripts/train.py"),
            "--config", str(ROOT / "configs/bc_reference.json"), "--dataset", a.dataset,
            "--device", a.device, "--output", str(output / "training")], check=True, cwd=ROOT)
        a.checkpoint = str(output / "training/student_policy.pth")
    else:
        a.checkpoint = a.checkpoint or str(ROOT / "checkpoints/instructor_reference.pth")
        if not Path(a.checkpoint).is_file():
            raise FileNotFoundError("Reference missing. Use --train --output with a NEW path to generate it from public data.")
    _, checkpoint = load_policy(a.checkpoint)
    if checkpoint["lab_contract"]["role"] != "instructor_reference":
        raise ValueError("Expected an explicitly labeled instructor reference")
    if checkpoint["lab_contract"]["dataset_sha256"] != sha256(a.dataset):
        raise ValueError("Reference dataset mismatch")
    target = output / "instructor_reference.pth"
    shutil.copy2(a.checkpoint, target)
    subprocess.run([str(ROOT / "scripts/lab_python.sh"), str(ROOT / "scripts/evaluate.py"),
        "--checkpoint", str(target), "--config", str(ROOT / "configs/evaluation.yaml"),
        "--dataset", a.dataset, "--output", str(output / "reference_evaluation")], check=True, cwd=ROOT)
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
        "source": "fixed reference trained from public data" if a.train else "existing trusted instructor model; fresh fixed evaluation"})
    print("Teacher checkpoint, fixed evaluation and real failure evidence are ready")
