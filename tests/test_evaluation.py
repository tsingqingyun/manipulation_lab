import copy
import numpy as np
from manipulation_lab.evaluation import stable_placement

CONFIG = {"stability_window_steps": 20, "stability_max_displacement_m": .01,
          "stability_max_speed_m_s": .05, "release_min_gripper_width_m": .055}


def good():
    return [{"object_position": np.array([0., 0., .83]), "environment_success": True,
             "inside_target_margin": True, "gripper_contact": False, "gripper_width": .08} for _ in range(21)]


def test_stable_released_placement_and_negative_controls():
    assert stable_placement(good(), CONFIG)
    for key, value in [("environment_success", False), ("inside_target_margin", False),
                       ("gripper_contact", True), ("gripper_width", .02)]:
        history = good(); history[10][key] = value
        assert not stable_placement(history, CONFIG)
    history = good(); history[-1]["object_position"][0] += .02
    assert not stable_placement(history, CONFIG)
    assert not stable_placement(good()[:20], CONFIG)


def test_motion_below_displacement_but_above_speed_fails():
    history = good(); history[-1]["object_position"][0] += .004
    assert not stable_placement(history, CONFIG)
