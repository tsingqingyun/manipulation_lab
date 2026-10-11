"""Obtain the fixed official dataset via HTTPS, a chosen mirror, or an offline copy."""
import _bootstrap
import argparse
import os
from pathlib import Path
import shutil
import urllib.error
import urllib.parse
import urllib.request
import h5py
from manipulation_lab.common import DATA, sha256, write_json

DATASET_PATH = "/datasets/amandlek/robomimic/resolve/main/v1.5/can/ph/low_dim_v15.hdf5?download=true"
URL = "https://huggingface.co" + DATASET_PATH
EXPECTED_SHA256 = "3f2eb92e0a5025d0095e866ac16cc8092d6a762abe27dec90dbaff9027282962"


def dataset_url(explicit=None):
    url = explicit or os.environ.get("LAB_DATASET_URL") or os.environ.get("HF_ENDPOINT", "https://huggingface.co").rstrip("/") + DATASET_PATH
    parsed = urllib.parse.urlsplit(url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError("Dataset URL / HF_ENDPOINT must be an HTTP(S) address; use --from-file for offline data")
    return url


def source_label(url):
    # Do not persist userinfo, signed URL query parameters, or fragments.
    parsed = urllib.parse.urlsplit(url)
    return urllib.parse.urlunsplit((parsed.scheme, parsed.netloc.rsplit("@", 1)[-1], parsed.path, "", ""))


def validate_dataset(path):
    digest = sha256(path)
    if digest != EXPECTED_SHA256:
        raise ValueError(f"Dataset SHA256 mismatch at {path}; file retained. Expected {EXPECTED_SHA256}, got {digest}")
    with h5py.File(path, "r") as f:
        if "data" not in f or len(f["data"]) != 200:
            raise ValueError(f"Expected 200 demonstration episodes in {path}; file retained")
    return digest


def obtain_dataset(path, *, url=None, from_file=None, timeout=120):
    path = Path(path).expanduser().absolute()
    if path.exists():
        digest = validate_dataset(path)
        print(f"Existing validated dataset: {path}; sha256={digest}")
        return path
    path.parent.mkdir(exist_ok=True, parents=True)
    partial = path.with_suffix(path.suffix + ".partial")
    provenance = path.with_suffix(".provenance.json")
    if partial.exists() or provenance.exists():
        raise FileExistsError(f"Preserving existing partial/provenance for {path}; inspect it and choose a new output")
    if from_file is not None:
        source = Path(from_file).expanduser()
        if source.absolute() == partial:
            raise ValueError("Offline source must be different from the output partial file")
        with source.open("rb") as incoming, partial.open("xb") as out:
            shutil.copyfileobj(incoming, out, length=1024 * 1024)
        origin = {"transport": "offline_copy", "source_file": source.name}
    else:
        url = dataset_url(url)
        try:
            with urllib.request.urlopen(url, timeout=timeout) as incoming, partial.open("xb") as out:
                shutil.copyfileobj(incoming, out, length=1024 * 1024)
        except (urllib.error.URLError, TimeoutError, ConnectionError) as exc:
            raise RuntimeError("Dataset download failed. Use an administrator-approved HF_ENDPOINT / LAB_DATASET_URL, "
                "an HTTPS_PROXY, or transfer the official file and use --from-file. "
                f"Any partial file at {partial} is retained; use a new output for a retry.") from exc
        origin = {"transport": "http", "url": source_label(url)}
    digest = validate_dataset(partial)
    partial.chmod(0o444)
    # Publish without replacing another process's completed file.
    os.link(partial, path)
    partial.unlink()
    write_json(provenance, {**origin, "sha256": digest, "kind": "human_demonstrations"})
    print(f"Verified dataset: {path}; sha256={digest}")
    return path


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--output", default=str(DATA))
    source = p.add_mutually_exclusive_group()
    source.add_argument("--url", help="Full HTTP(S) URL; overrides LAB_DATASET_URL and HF_ENDPOINT")
    source.add_argument("--from-file", help="Copy an official HDF5 transferred from another machine; enforce the same SHA256")
    p.add_argument("--timeout", type=float, default=120, help="Network operation timeout in seconds")
    a = p.parse_args()
    if a.timeout <= 0:
        p.error("--timeout must be positive")
    obtain_dataset(a.output, url=a.url, from_file=a.from_file, timeout=a.timeout)
