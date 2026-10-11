import _bootstrap
import argparse
import json
import time
import h5py
import imageio.v2 as imageio
from manipulation_lab.common import DATA, new_output, deadline, resource_slot, write_json, sha256
from manipulation_lab.dataset import initial_state
from manipulation_lab.simulator import create_env

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--dataset", default=str(DATA))
    p.add_argument("--episode", default="demo_0")
    p.add_argument("--output", required=True)
    a = p.parse_args()
    output = new_output(a.output)
    with resource_slot("evaluation"), deadline(180), h5py.File(a.dataset, "r") as f:
        start = time.monotonic()
        meta = json.loads(f["data"].attrs["env_args"])
        env = create_env(meta, video=True)
        try:
            env.reset_to(initial_state(a.dataset, a.episode))
            with imageio.get_writer(output / "demonstration.mp4", fps=10, codec="libx264", pixelformat="yuv420p") as writer:
                for state in f[f"data/{a.episode}/states"][::2]:
                    env.reset_to({"states": state})
                    writer.append_data(env.render(mode="rgb_array", width=384, height=384))
            write_json(output / "provenance.json", {"kind": "human_demonstration_state_playback", "episode": a.episode,
                "dataset_sha256": sha256(a.dataset), "elapsed_seconds": time.monotonic() - start,
                "time_domain": "20Hz control-step index, video subsampled to 10fps; no acquisition timestamps"})
        finally:
            env.env.close()
