import csv
import hashlib
import json
import random
import resource
import time
from pathlib import Path
import numpy as np
import torch
from robomimic.utils.train_utils import save_model
from .common import DATA, KEYS, deadline, new_output, resource_slot, versions, write_json
from .dataset import inspect, load_arrays
from .policy import make_config, make_model, load_policy


def train(settings, output, dataset=DATA):
    output = new_output(output)
    write_json(output / "training_config.json", settings)
    with resource_slot("training"), deadline(settings["timeout_seconds"]):
        start = time.monotonic()
        torch.set_num_threads(settings["cpu_threads"])
        torch.manual_seed(settings["seed"])
        np.random.seed(settings["seed"])
        random.seed(settings["seed"])
        torch.backends.cudnn.benchmark = False
        device = torch.device(settings["device"])
        if device.type == "cuda" and not torch.cuda.is_available():
            raise RuntimeError("CUDA unavailable. Select device='cpu' explicitly; do not silently change the run")
        if device.type == "cuda":
            torch.cuda.reset_peak_memory_stats()
        inspection = inspect(dataset)
        write_json(output / "dataset_inspection.json", inspection)
        config = make_config(settings)
        write_json(output / "robomimic_config.json", json.loads(config.dump()))
        arrays = {part: load_arrays(dataset, inspection["splits"][part], settings["sequence_length"]) for part in ("train", "validation")}
        stats = None
        if settings.get("normalize_obs", True):
            stats = {k: {"mean": arrays["train"]["obs"][k].mean(0, keepdim=True).numpy(),
                         "std": (arrays["train"]["obs"][k].std(0, keepdim=True, correction=0) + 1e-3).numpy()} for k in KEYS}
        for arr in arrays.values():
            arr["actions"] = arr["actions"].to(device)
            arr["indices"] = arr["indices"].to(device)
            for k in KEYS:
                if stats:
                    arr["obs"][k] = (arr["obs"][k] - torch.from_numpy(stats[k]["mean"])) / torch.from_numpy(stats[k]["std"])
                arr["obs"][k] = arr["obs"][k].to(device)
        shapes = inspection["policy_observation_shapes"]
        shape_meta = {"all_shapes": shapes, "ac_dim": 7, "all_obs_keys": KEYS, "use_images": False, "use_depths": False}
        model = make_model(config, shapes, device)
        initial_hash = hashlib.sha256()
        for name, value in sorted(model.nets.state_dict().items()):
            initial_hash.update(name.encode())
            initial_hash.update(value.detach().cpu().numpy().tobytes())
        best, best_epoch, history = float("inf"), 0, []
        target = output / "student_policy.pth"
        contract = {"versions": versions(), "dataset_sha256": inspection["dataset_sha256"],
                    "splits": inspection["splits"], "policy_name": settings["name"], "architecture": settings["architecture"],
                    "observation_adapter": "world_pose_only_v1", "loss": "MSE", "role": "instructor_reference" if settings["name"].startswith("instructor") else "student"}
        with open(output / "training_log.csv", "x", newline="") as log:
            writer = csv.DictWriter(log, fieldnames=["epoch", "training_loss", "validation_loss", "elapsed_seconds"])
            writer.writeheader()
            for epoch in range(1, settings["epochs"] + 1):
                losses = {}
                for part in ("train", "validation"):
                    validation = part == "validation"
                    model.set_eval() if validation else model.set_train()
                    arr = arrays[part]
                    n = len(arr["indices"])
                    order = torch.arange(n, device=device) if validation else torch.randperm(n, device=device)
                    total = 0.
                    for ids in order.split(settings["batch_size"]):
                        idx = arr["indices"][ids]
                        batch = {"obs": {k: v[idx] for k, v in arr["obs"].items()}, "actions": arr["actions"][idx]}
                        batch = model.process_batch_for_training(batch)
                        info = model.train_on_batch(batch, epoch, validate=validation)
                        total += float(info["losses"]["action_loss"]) * len(ids)
                    losses[part] = total / n
                model.on_epoch_end(epoch)
                row = {"epoch": epoch, "training_loss": losses["train"], "validation_loss": losses["validation"], "elapsed_seconds": time.monotonic() - start}
                if not all(np.isfinite(v) for v in row.values()):
                    raise ValueError("Non-finite training result")
                history.append(row)
                writer.writerow(row)
                log.flush()
                if losses["validation"] < best:
                    best, best_epoch = losses["validation"], epoch
                    # Best validation selection is explicit; test rollouts never choose weights.
                    save_model(model, config, inspection["env_metadata"], shape_meta, str(target), stats)
                    ckpt = torch.load(target, map_location="cpu", weights_only=False)
                    ckpt["lab_contract"] = {**contract, "selected_epoch": epoch}
                    torch.save(ckpt, target)
                if epoch % 10 == 0 or epoch == 1:
                    print(json.dumps(row), flush=True)
        policy, _ = load_policy(target)
        policy.start_episode()
        sample = {k: arrays["validation"]["obs"][k][0].cpu().numpy() for k in KEYS}
        if stats:
            sample = {k: sample[k] * stats[k]["std"][0] + stats[k]["mean"][0] for k in KEYS}
        action = policy(sample)
        assert action.shape == (7,) and np.isfinite(action).all()
        from .visualization import training_curve
        training_curve(history, output / "training_curve.png")
        summary = {"elapsed_seconds": time.monotonic() - start, "epochs": settings["epochs"], "best_epoch": best_epoch,
            "initial_weights_sha256": initial_hash.hexdigest(),
            "best_validation_mse": best, "last_training_mse": history[-1]["training_loss"],
            "checkpoint_reload_passed": True, "peak_rss_mib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024,
            "peak_cuda_allocated_mib": torch.cuda.max_memory_allocated() / 2**20 if device.type == "cuda" else 0,
            "device": str(device), "gpu_name": torch.cuda.get_device_name() if device.type == "cuda" else None,
            "cpu_threads": torch.get_num_threads(), "versions": versions(), "contract": contract}
        write_json(output / "training_summary.json", summary)
        return summary
