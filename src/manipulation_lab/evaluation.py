import csv
import json
from pathlib import Path
import resource
import shutil
import time
import traceback
import h5py
import imageio.v2 as imageio
import numpy as np
import torch
from .common import DATA, deadline, new_output, resource_slot, sha256, write_json, policy_observation
from .dataset import inspect
from .policy import load_policy
from .simulator import create_env, reset_episode, snapshot
from .visualization import success_plot


def stable_placement(history, config, hz=20):
    n = config["stability_window_steps"]
    if len(history) < n + 1:
        return False
    window = history[-n-1:]
    if not all(s["environment_success"] and s["inside_target_margin"] and not s["gripper_contact"] and
               s["gripper_width"] >= config["release_min_gripper_width_m"] for s in window):
        return False
    pos = np.array([s["object_position"] for s in window])
    return bool(np.linalg.norm(pos - pos[0], axis=1).max() <= config["stability_max_displacement_m"] and
                (np.linalg.norm(np.diff(pos, axis=0), axis=1) * hz).max() <= config["stability_max_speed_m_s"])


def make_test_manifest(env, dataset, inspection, config):
    n = config["episodes_per_condition"]
    if n < 1 or len(config["seeds"]) < n:
        raise ValueError("Provide at least one episode and one explicit seed per episode")
    records = []
    for episode in inspection["splits"]["test"]:
        try:
            reset_episode(env, dataset, episode, 0, config["shift_xy_m"])
        except ValueError:
            continue
        records.append(episode)
    if len(records) < n:
        raise ValueError(f"Only {len(records)} held-out initial states fit the fixed shift; requested {n}")
    return [{"episode_id": f"{condition}_{i:02d}", "condition": condition, "source_episode": episode,
             "seed": config["seeds"][i], "shift_xy_m": config["shift_xy_m"] if condition == "shifted" else [0., 0.]}
            for condition in config["conditions"] for i, episode in enumerate(records[:n])]


def evaluate(checkpoint, config, output, dataset=DATA):
    output = new_output(output)
    write_json(output / "evaluation_config.json", config)
    torch.set_num_threads(2)
    with resource_slot("evaluation"), deadline(config["timeout_seconds"]):
        start = time.monotonic()
        policy, ckpt = load_policy(checkpoint, device="cpu")
        inspection = inspect(dataset)
        if inspection["dataset_sha256"] != ckpt["lab_contract"]["dataset_sha256"]:
            raise ValueError("Dataset differs from checkpoint training contract")
        if inspection["splits"] != ckpt["lab_contract"]["splits"]:
            raise ValueError("Split differs from checkpoint training contract")
        env = create_env(ckpt["env_metadata"], video=True)
        checkpoint_hash = sha256(checkpoint)
        rows = []
        try:
            manifest = make_test_manifest(env, dataset, inspection, config)
            write_json(output / "test_manifest.json", {"dataset_sha256": inspection["dataset_sha256"], "episodes": manifest})
            hz = inspection["time"]["control_hz"]
            for case in manifest:
                episode_start = time.monotonic()
                video = output / f"{case['episode_id']}.mp4"
                history, actions, frames, error = [], [], [], None
                try:
                    with deadline(config["episode_timeout_seconds"]):
                        torch.manual_seed(case["seed"])
                        obs = reset_episode(env, dataset, case["source_episode"], case["seed"], case["shift_xy_m"])
                        initial = snapshot(env, obs)
                        history.append(initial)
                        policy.start_episode()
                        for step in range(config["horizon"]):
                            action = policy(policy_observation(obs))
                            if not np.isfinite(action).all() or np.max(np.abs(action)) > 1.00001:
                                raise ValueError("Policy emitted invalid normalized action")
                            obs, _, _, _ = env.step(action)
                            actions.append(action)
                            history.append(snapshot(env, obs))
                            if step % config["video_stride"] == 0:
                                frames.append(env.render(mode="rgb_array", width=config["video_size"], height=config["video_size"]))
                            if stable_placement(history, config, hz):
                                break
                except Exception as exc:
                    error = f"{type(exc).__name__}: {exc}"
                    (output / f"{case['episode_id']}.error.txt").write_text(traceback.format_exc())
                if frames:
                    imageio.mimsave(video, frames, fps=hz / config["video_stride"], codec="libx264", pixelformat="yuv420p")
                stable = bool(not error and stable_placement(history, config, hz))
                env_success = bool(any(s["environment_success"] for s in history))
                final = history[-1] if history else None
                row = {**{k: case[k] for k in ("episode_id", "condition", "source_episode", "seed")},
                    "policy_name": ckpt["lab_contract"]["policy_name"], "policy_role": ckpt["lab_contract"]["role"],
                    "checkpoint": str(Path(checkpoint).resolve()), "checkpoint_sha256": checkpoint_hash,
                    "initial_object_position": json.dumps(history[0]["object_position"].tolist()) if history else None,
                    "final_object_position": json.dumps(final["object_position"].tolist()) if final else None,
                    "steps": len(actions), "environment_success": env_success, "stable_success": stable,
                    "failure_stage": "none" if stable else "manual_review_required", "error": error or "",
                    "elapsed_seconds": time.monotonic() - episode_start, "video": video.name if frames else ""}
                rows.append(row)
                if history:
                    np.savez_compressed(output / f"{case['episode_id']}.npz", actions=np.array(actions),
                        **{k: np.array([s[k] for s in history]) for k in history[0]})
                with open(output / "results.csv", "w", newline="") as f:
                    writer = csv.DictWriter(f, fieldnames=list(rows[0])); writer.writeheader(); writer.writerows(rows)
                print(json.dumps(row), flush=True)
            summary = {"policy_name": ckpt["lab_contract"]["policy_name"], "policy_role": ckpt["lab_contract"]["role"],
                "checkpoint_sha256": checkpoint_hash, "conditions": {}, "elapsed_seconds": time.monotonic() - start,
                "peak_rss_mib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024,
                "rollout_device": "CPU; EGL GPU for rendering", "position_test_name": "Position Shift Test (not certified OOD)",
                "success_definition": "environment ever-success; separately: continuing policy for >=1s with target-margin containment, open gripper, no gripper contact, displacement<=1cm, speed<=5cm/s",
                "errors": sum(bool(r["error"]) for r in rows), "episodes": rows}
            for condition in config["conditions"]:
                subset = [r for r in rows if r["condition"] == condition]
                summary["conditions"][condition] = {"episodes": len(subset),
                    "environment_success_rate": float(np.mean([r["environment_success"] for r in subset])),
                    "stable_success_rate": float(np.mean([r["stable_success"] for r in subset]))}
            for success, name in [(True, "successful_rollout.mp4"), (False, "failed_rollout.mp4")]:
                match = next((r for r in rows if r["stable_success"] == success and r["video"]), None)
                if match:
                    shutil.copyfile(output / match["video"], output / name)
            match = next((r for r in rows if r["video"]), None)
            if match:
                shutil.copyfile(output / match["video"], output / "rollout.mp4")
            write_json(output / "summary.json", summary)
            shutil.copyfile(output / "summary.json", output / "evaluation_summary.json")
            shutil.copyfile(output / "results.csv", output / "evaluation_results.csv")
            success_plot(summary, output / "success_rate_plot.png")
            return summary
        finally:
            env.env.close()
