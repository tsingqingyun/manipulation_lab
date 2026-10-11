"""Re-render a preselected recorded rollout; never retrain or select new cases."""
import hashlib
import json
from pathlib import Path
import shutil

import h5py
import imageio.v2 as imageio
import numpy as np
from manipulation_lab.common import DATA
from manipulation_lab.simulator import create_env, reset_episode, snapshot

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
ASSETS = HERE / "assets"
RUN = ROOT / "outputs/teaching_acceptance_20261012_v1/groups/group_01/20261011T163325Z_131cb6f3"
EXPERIMENT = RUN / "experiment_163342_eb82ae"
EVAL = EXPERIMENT / "lr_a/evaluation"


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    ASSETS.mkdir(exist_ok=True)
    target = ASSETS / "success_half_speed.mp4"
    if target.exists():
        raise FileExistsError("Preserve existing media; inspect before regenerating")
    summary = json.loads((EVAL / "summary.json").read_text())
    case = next(e for e in summary["episodes"] if e["episode_id"] == "standard_01")
    assert case["stable_success"] and not case["error"]
    recorded = np.load(EVAL / "standard_01.npz")
    with h5py.File(DATA) as f:
        meta = json.loads(f["data"].attrs["env_args"])
    env = create_env(meta, video=True)
    errors = {k: 0.0 for k in ["object_position", "eef_position", "gripper_width"]}
    frames, frame_steps = [], []
    selected_steps = [1, 41, 89, 145]
    try:
        obs = reset_episode(env, DATA, case["source_episode"], case["seed"])
        for index, action in enumerate(recorded["actions"]):
            obs, _, _, _ = env.step(action)
            state = snapshot(env, obs)
            for key in errors:
                errors[key] = max(errors[key], float(np.max(np.abs(np.asarray(state[key]) - recorded[key][index + 1]))))
            if index % 2 == 0:
                frame = env.render(mode="rgb_array", width=768, height=768)
                frames.append(frame)
                frame_steps.append(index + 1)
                if index + 1 in selected_steps:
                    imageio.imwrite(ASSETS / f"success_step_{index + 1:03d}.png", frame)
            if index % 40 == 0:
                print("rendered control step", index + 1, flush=True)
        assert max(errors.values()) < 1e-6, errors
        imageio.mimsave(target, frames, fps=5, codec="libx264", pixelformat="yuv420p", quality=8)
        imageio.imwrite(ASSETS / "success_poster.png", frames[0])
    finally:
        env.env.close()
    shutil.copyfile(EVAL / "standard_00.mp4", ASSETS / "failure_original.mp4")
    failure = np.load(EVAL / "standard_00.npz")
    reader = imageio.get_reader(ASSETS / "failure_original.mp4")
    failure_steps = [1, 41, 81]
    for step in failure_steps:
        idx = int(np.where(failure["video_control_steps"] == step)[0][0])
        imageio.imwrite(ASSETS / f"failure_step_{step:03d}.png", reader.get_data(idx))
    reader.close()
    # Small raw records make the figures and their provenance independently auditable.
    for variant in ["lr_a", "lr_b"]:
        for source, dest in [("training/training_log.csv", f"{variant}_training_log.csv"),
                             ("training/training_summary.json", f"{variant}_training_summary.json"),
                             ("evaluation/summary.json", f"{variant}_evaluation_summary.json")]:
            p = EXPERIMENT / variant / source
            if p.exists():
                if p.suffix == '.csv':
                    (ASSETS / dest).write_text(p.read_text())
                else:
                    shutil.copyfile(p, ASSETS / dest)
    shutil.copyfile(EVAL / "standard_00.npz", ASSETS / "failure_trace.npz")
    shutil.copyfile(EVAL / "standard_01.npz", ASSETS / "success_trace.npz")
    sources = [EVAL / "standard_01.mp4", EVAL / "standard_01.npz", EVAL / "standard_00.mp4", EVAL / "standard_00.npz", EVAL / "summary.json"]
    manifest = {
        "source_run": str(RUN.relative_to(ROOT)), "source_experiment": str(EXPERIMENT.relative_to(ROOT)),
        "policy_role": "student", "variant": "lr_a", "checkpoint_sha256": summary["checkpoint_sha256"],
        "success_case": case, "failure_case": next(e for e in summary["episodes"] if e["episode_id"] == "standard_00"),
        "render_kind": "Replay the saved successful action sequence from the identical initial state; no policy/training/evaluation rerun",
        "render_backend": "OSMesa", "max_abs_state_replay_errors": errors,
        "state_comparison": "All 149 post-action states, object xyz, end-effector xyz and gripper width, tolerance 1e-6 m",
        "video": {"file": target.name, "resolution": [768,768], "fps": 5, "playback_speed": 0.5,
                  "source_control_hz": 20, "recorded_control_steps": frame_steps, "duration_seconds": len(frames) / 5},
        "success_keyframes": [{"control_step": s, "simulation_time_seconds": s/20, "file": f"success_step_{s:03d}.png"} for s in selected_steps],
        "failure_keyframes": [{"control_step": s, "simulation_time_seconds": s/20, "file": f"failure_step_{s:03d}.png"} for s in failure_steps],
        "sources": [{"path": str(p.relative_to(ROOT)), "sha256": sha(p)} for p in sources],
        "text_normalization": "CSV copies use LF line endings; all original numeric strings are preserved.",
        "assets": {p.name: sha(p) for p in sorted(ASSETS.iterdir()) if p.is_file()},
        "limitations": ["Re-rendering preserves logged physics states; it is not an independent policy evaluation.",
                        "The selected successful example is not a success-rate estimate.",
                        "Stage labels are visual teaching annotations, not automatically inferred contact labels."]}
    (HERE / "media_provenance.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps({"duration": len(frames)/5, "state_errors": errors}), flush=True)


if __name__ == "__main__":
    main()
