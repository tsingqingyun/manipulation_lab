import json
from pathlib import Path
import h5py
import numpy as np
from .common import DATA, KEYS, sha256, write_json


def split_episodes(names, seed=20261011):
    names = sorted(names, key=lambda n: int(n.split("_")[-1]))
    order = np.random.default_rng(seed).permutation(names).tolist()
    n = len(order)
    a, b = int(0.8 * n), int(0.9 * n)
    return {"train": order[:a], "validation": order[a:b], "test": order[b:]}


def inspect(path=DATA):
    with h5py.File(path, "r") as f:
        meta = json.loads(f["data"].attrs["env_args"])
        if meta.get("env_version") != "1.5.1" or meta.get("env_name") != "PickPlaceCan":
            raise ValueError("Use the validated robosuite 1.5.1 PickPlaceCan dataset")
        names = sorted(f["data"], key=lambda n: int(n.split("_")[-1]))
        split = split_episodes(names)
        episodes = []
        for name in names:
            d = f["data"][name]
            n = len(d["actions"])
            assert d["actions"].shape == (n, 7), name
            assert np.isfinite(d["actions"][:]).all(), name
            for key in KEYS:
                assert len(d["obs"][key]) == n
                assert np.isfinite(d["obs"][key][:]).all(), (name, key)
            episodes.append({"episode": name, "length": n,
                "initial_object_position_m": d["obs/object"][0, 7:10].tolist(),
                "final_reward": float(d["rewards"][-1]) if "rewards" in d else None,
                "final_done": int(d["dones"][-1]) if "dones" in d else None,
                "timestamp_fields": [k for k in d if "time" in k.lower()]})
        first = f["data"][names[0]]
        train_pos = np.array([f[f"data/{n}/obs/object"][0, 7:10] for n in split["train"]])
        return {"source": "robomimic Can PH v1.5 human demonstrations", "dataset_sha256": sha256(path),
            "episode_count": len(names), "total_steps": sum(e["length"] for e in episodes),
            "observation_shapes": {k: list(v.shape[1:]) for k, v in first["obs"].items()},
            "policy_observations": KEYS, "object_field_layout": "0:3 relative position in eef frame; 3:7 relative quaternion xyzw; 7:10 world position m; 10:14 world quaternion xyzw (robosuite 1.5.1)",
            "policy_observation_shapes": {k: [7] if k == "object" else list(first[f"obs/{k}"].shape[1:]) for k in KEYS},
            "policy_observation_adapter": "world_pose_only_v1: object[7:14], others unchanged; excludes stale cached relative sensors",
            "action_dim": 7, "action_range": [-1, 1],
            "action_meaning": "OSC_POSE normalized delta xyz, delta rotation axis-angle, gripper (+close/-open); physical scaling in env metadata",
            "coordinate_system": "robosuite world, z up; meters; observation quaternion xyzw; simulator free joint quaternion wxyz",
            "time": {"timestamps": "missing unless listed per episode", "index": "control step", "control_hz": meta["env_kwargs"]["control_freq"]},
            "success_labels": "rewards and dones are recorded labels, not independent stable placement proof",
            "env_metadata": meta, "split_seed": 20261011, "splits": split,
            "train_initial_position_min_m": train_pos.min(0).tolist(), "train_initial_position_max_m": train_pos.max(0).tolist(),
            "original_masks": {k: len(v) for k, v in f.get("mask", {}).items()}, "episodes": episodes}


def load_arrays(path, episodes, seq_length=1):
    """Sequences end-pad inside an episode; adjacent episodes never cross."""
    import torch
    obs = {k: [] for k in KEYS}
    actions, indices, offset = [], [], 0
    with h5py.File(path, "r") as f:
        for name in episodes:
            d = f[f"data/{name}"]
            n = len(d["actions"])
            for key in KEYS:
                value = d[f"obs/{key}"][:].astype(np.float32)
                obs[key].append(value[:, 7:14] if key == "object" else value)
            actions.append(d["actions"][:].astype(np.float32))
            indices.append(np.minimum(np.arange(n)[:, None] + np.arange(seq_length), n - 1) + offset)
            offset += n
    return {"obs": {k: torch.from_numpy(np.concatenate(v)) for k, v in obs.items()},
            "actions": torch.from_numpy(np.concatenate(actions)), "indices": torch.from_numpy(np.concatenate(indices))}


def initial_state(path, episode):
    with h5py.File(path, "r") as f:
        d = f[f"data/{episode}"]
        state = {"states": d["states"][0], "model": d.attrs["model_file"]}
        if "ep_meta" in d.attrs:
            state["ep_meta"] = d.attrs["ep_meta"]
        return state
