import torch
import pytest
from manipulation_lab.policy import load_policy


def test_old_checkpoint_is_rejected_before_environment_creation(tmp_path):
    path = tmp_path / "old.pth"
    torch.save({"model": {}}, path)
    with pytest.raises(ValueError, match="compatibility contract"):
        load_policy(path)
