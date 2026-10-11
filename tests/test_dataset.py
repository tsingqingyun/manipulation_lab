import h5py
import numpy as np
from manipulation_lab.dataset import split_episodes, load_arrays
from manipulation_lab.common import KEYS


def test_episode_split_is_disjoint_and_reproducible():
    names = [f"demo_{i}" for i in range(200)]
    a = split_episodes(names)
    assert a == split_episodes(names[::-1])
    assert [len(a[k]) for k in ("train", "validation", "test")] == [160, 20, 20]
    assert len(set(a["train"] + a["validation"] + a["test"])) == 200


def test_sequence_padding_never_crosses_episode(tmp_path):
    path = tmp_path / "tiny.hdf5"
    with h5py.File(path, "w") as f:
        for i, length in enumerate([2, 3]):
            g = f.create_group(f"data/demo_{i}")
            g.create_dataset("actions", data=np.full((length, 7), i))
            for key in KEYS:
                g.create_dataset(f"obs/{key}", data=np.full((length, 14 if key == "object" else 3), i))
    data = load_arrays(path, ["demo_0", "demo_1"], 4)
    seq = data["actions"][data["indices"]].numpy()
    assert np.all(seq[:2] == 0) and np.all(seq[2:] == 1)
