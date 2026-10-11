import _bootstrap
import argparse
import os
import urllib.request
from pathlib import Path
import h5py
from manipulation_lab.common import DATA, sha256, write_json

URL = "https://huggingface.co/datasets/amandlek/robomimic/resolve/main/v1.5/can/ph/low_dim_v15.hdf5?download=true"
EXPECTED_SHA256 = "3f2eb92e0a5025d0095e866ac16cc8092d6a762abe27dec90dbaff9027282962"

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--output", default=str(DATA))
    a = p.parse_args()
    path = Path(a.output)
    if path.exists():
        if sha256(path) != EXPECTED_SHA256:
            raise ValueError("Existing dataset hash differs from the validated teaching dataset")
        print(f"Existing read-only dataset: {path}; sha256={sha256(path)}")
    else:
        path.parent.mkdir(exist_ok=True, parents=True)
        partial = path.with_suffix(path.suffix + ".partial")
        if partial.exists():
            raise FileExistsError(f"Preserving previous partial download: {partial}; choose a new output")
        with urllib.request.urlopen(URL, timeout=120) as source, open(partial, "xb") as out:
            while block := source.read(1024 * 1024):
                out.write(block)
        with h5py.File(partial, "r") as f:
            assert len(f["data"]) == 200
        if sha256(partial) != EXPECTED_SHA256:
            raise ValueError("Downloaded dataset hash mismatch; partial retained for inspection")
        os.rename(partial, path)
        path.chmod(0o444)
        write_json(path.with_suffix(".provenance.json"), {"url": URL, "sha256": sha256(path), "kind": "human_demonstrations"})
        print(path)
