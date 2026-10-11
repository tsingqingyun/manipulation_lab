import json
import h5py
import numpy as np
from robomimic.utils.env_utils import create_env_from_metadata
import robomimic.utils.obs_utils as ObsUtils
from .common import KEYS, policy_observation
from .dataset import initial_state


def create_env(metadata, video=False):
    ObsUtils.initialize_obs_utils_with_obs_specs({"obs": {"low_dim": KEYS}})
    if metadata["env_name"] != "PickPlaceCan":
        raise ValueError(f"Expected PickPlaceCan, got {metadata['env_name']}")
    return create_env_from_metadata(metadata, render=False, render_offscreen=video, use_image_obs=False)


def reset_episode(env, dataset, episode, seed, shift=(0., 0.)):
    np.random.seed(seed)
    obs = env.reset_to(initial_state(dataset, episode))
    raw = env.env
    obj = raw.objects[raw.object_id]
    if np.any(shift):
        qpos = raw.sim.data.get_joint_qpos(obj.joints[0]).copy()
        qpos[:2] += np.asarray(shift)
        # Certified source-bin interior is a conservative reachable task region.
        margin = obj.horizontal_radius + 0.005
        lower = raw.bin1_pos[:2] - raw.bin_size[:2] / 2 + margin
        upper = raw.bin1_pos[:2] + raw.bin_size[:2] / 2 - margin
        if np.any(qpos[:2] < lower) or np.any(qpos[:2] > upper):
            raise ValueError(f"Shifted position {qpos[:2]} outside source-bin interior {lower}..{upper}")
        raw.sim.data.set_joint_qpos(obj.joints[0], qpos)
        raw.sim.forward()
        obs = env.get_observation()
    return obs


def snapshot(env, obs):
    raw = env.env
    obj = raw.objects[raw.object_id]
    pos = raw.sim.data.body_xpos[raw.obj_body_id[obj.name]].copy()
    center = raw.target_bin_placements[raw.object_id]
    half = raw.bin_size[:2] / 4
    margin = float(obj.horizontal_radius)
    inside = bool(np.all(np.abs(pos[:2] - center[:2]) < half - margin) and center[2] < pos[2] < center[2] + 0.1)
    gripper = raw.robots[0].gripper[raw.robots[0].arms[0]]
    contact = bool(raw.check_contact(gripper, obj))
    return {"object_position": pos, "eef_position": np.asarray(obs["robot0_eef_pos"]),
            "gripper_qpos": np.asarray(obs["robot0_gripper_qpos"]),
            "gripper_width": float(abs(obs["robot0_gripper_qpos"][0] - obs["robot0_gripper_qpos"][1])),
            "gripper_contact": contact, "inside_target_margin": inside,
            "environment_success": bool(env.is_success()["task"])}


def compatibility_check(dataset, output):
    """Compare same states and one-step expert actions, never closed-loop errors."""
    from .common import write_json, versions
    with h5py.File(dataset, "r") as f:
        metadata = json.loads(f["data"].attrs["env_args"])
        env = create_env(metadata, video=True)
        results = []
        try:
            reset_episode(env, dataset, "demo_0", 0)
            for episode, step in [("demo_0", 0), ("demo_0", 50), ("demo_1", 100)]:
                d = f[f"data/{episode}"]
                env.reset_to(initial_state(dataset, episode))
                obs = env.reset_to({"states": d["states"][step]})
                stored = {k: d[f"obs/{k}"][step] for k in KEYS}
                selected, expected = policy_observation(obs), policy_observation(stored)
                errors = {k: float(np.max(np.abs(selected[k] - expected[k]))) for k in KEYS}
                excluded_error = float(np.max(np.abs(obs["object"][:7] - stored["object"][:7])))
                assert max(errors.values()) < 1e-5, errors
                assert np.allclose(obs["object"][7:10], snapshot(env, obs)["object_position"], atol=1e-8)
                action = d["actions"][step]
                assert env.action_dimension == 7 and np.isfinite(action).all() and np.max(np.abs(action)) <= 1.00001
                nxt, _, _, _ = env.step(action)
                # Stored next_obs enables a same-input controller / one-step dynamics check.
                selected_next = policy_observation(nxt)
                expected_next = policy_observation({k: d[f"next_obs/{k}"][step] for k in KEYS})
                next_errors = {k: float(np.max(np.abs(selected_next[k] - expected_next[k]))) for k in KEYS}
                results.append({"episode": episode, "step": step, "observation_max_abs_error": errors,
                    "excluded_cached_relative_sensor_max_error": excluded_error, "expert_one_step_max_abs_error": next_errors})
            frame = env.render(mode="rgb_array", width=256, height=256)
            assert frame.shape == (256, 256, 3) and frame.std() > 5
            import imageio.v2 as imageio
            imageio.imwrite(output / "environment.png", frame)
            controller = env.env.robots[0].part_controllers["right"]
            result = {"versions": versions(), "env_metadata": metadata, "state_comparisons": results,
                "controller": {"class": type(controller).__name__, "input_type": controller.input_type, "input_ref_frame": controller.input_ref_frame,
                    "input_min": np.asarray(controller.input_min).tolist(), "input_max": np.asarray(controller.input_max).tolist(),
                    "output_min": np.asarray(controller.output_min).tolist(), "output_max": np.asarray(controller.output_max).tolist()},
                "render_passed": True, "reset_step_passed": True}
            write_json(output / "compatibility.json", result)
            return result
        finally:
            env.env.close()
