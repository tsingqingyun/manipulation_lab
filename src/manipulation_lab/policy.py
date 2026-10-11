"""Official robomimic deterministic BC, with an explicit train/inference contract."""
import json
import torch
from robomimic.algo import algo_factory
from robomimic.config import config_factory
import robomimic.utils.obs_utils as ObsUtils
from robomimic.utils.file_utils import policy_from_checkpoint
from .common import KEYS, versions


def make_config(settings):
    config = config_factory("bc")
    with config.values_unlocked():
        config.observation.modalities.obs.low_dim = KEYS
        config.algo.actor_layer_dims = settings["hidden_dims"]
        config.algo.optim_params.policy.learning_rate.initial = settings["learning_rate"]
        config.algo.rnn.enabled = settings["architecture"] == "bc_rnn"
        config.algo.rnn.hidden_dim = settings.get("rnn_hidden_dim", 256)
        config.algo.rnn.num_layers = settings.get("rnn_layers", 2)
        config.algo.rnn.horizon = settings.get("sequence_length", 10)
        config.train.seq_length = settings.get("sequence_length", 1)
        config.train.hdf5_normalize_obs = settings.get("normalize_obs", True)
    ObsUtils.initialize_obs_utils_with_config(config)
    return config


def make_model(config, shapes, device):
    return algo_factory("bc", config, obs_key_shapes=shapes, ac_dim=7, device=device)


def load_policy(path, device="cpu"):
    # Only load checkpoints produced by this lab or another trusted instructor.
    checkpoint = torch.load(path, map_location="cpu", weights_only=False)
    contract = checkpoint.get("lab_contract")
    if contract is None:
        raise ValueError("Missing lab compatibility contract; old model-zoo weights are not accepted")
    if contract.get("observation_adapter") != "world_pose_only_v1":
        raise ValueError("Checkpoint observation adapter mismatch")
    current = versions()
    for key in ("robomimic", "robosuite", "mujoco"):
        if current[key] != contract["versions"][key]:
            raise ValueError(f"Version mismatch: {key}: {current[key]} != {contract['versions'][key]}")
    return policy_from_checkpoint(ckpt_dict=checkpoint, device=torch.device(device))
