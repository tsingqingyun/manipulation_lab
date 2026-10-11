import copy
import csv
import json
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
import pytest
from manipulation_lab.common import ROOT, sha256, write_json
from manipulation_lab.teaching import controlled_settings, paired_cases, validate_control
from manipulation_lab.reporting import frame_selection, failure_signal_figure, notebook_report_markdown
from manipulation_lab.classroom import CLASS_FIELDS, collect_run, variant_row


@pytest.fixture
def comparison(tmp_path):
    configs = controlled_settings({"seed": 17, "epochs": 50, "hidden_dims": [256, 256, 256]}, [.001, .0003])
    training, evaluation = [], []
    for i, config in enumerate(configs.values()):
        t, e = tmp_path / f"train{i}", tmp_path / f"eval{i}"
        t.mkdir(); e.mkdir()
        (t / "student_policy.pth").write_bytes(f"different model {i}".encode())
        write_json(t / "training_config.json", config)
        write_json(t / "training_summary.json", {"initial_weights_sha256": "same-initial-model",
            "contract": {"dataset_sha256": "same-data", "splits": {"train": [1], "test": [2]}, "versions": {"simulator": "fixed"}}})
        write_json(e / "evaluation_config.json", {"seeds": [101], "shift": [.04, 0]})
        write_json(e / "test_manifest.json", {"episodes": ["demo_2"]})
        write_json(e / "summary.json", {"errors": 0, "checkpoint_sha256": sha256(t / "student_policy.pth")})
        training.append(t); evaluation.append(e)
    return training, evaluation


def test_control_rejects_confounded_training_and_test_changes(comparison):
    training, evaluation = comparison
    assert all(validate_control(training, evaluation).values())
    path = training[1] / "training_config.json"
    config = json.loads(path.read_text()); config["epochs"] = 51; write_json(path, config)
    with pytest.raises(ValueError, match="Only learning_rate"):
        validate_control(training, evaluation)
    config["epochs"] = 50; write_json(path, config)
    write_json(evaluation[1] / "evaluation_config.json", {"seeds": [999], "shift": [.04, 0]})
    with pytest.raises(ValueError, match="Evaluation differs"):
        validate_control(training, evaluation)


def test_control_checks_initial_weights_and_actual_checkpoint(comparison):
    training, evaluation = comparison
    path = training[1] / "training_summary.json"
    summary = json.loads(path.read_text()); summary["initial_weights_sha256"] = "other"; write_json(path, summary)
    with pytest.raises(ValueError, match="Initial model"):
        validate_control(training, evaluation)
    summary["initial_weights_sha256"] = "same-initial-model"; write_json(path, summary)
    (training[1] / "student_policy.pth").write_bytes(b"replaced model")
    with pytest.raises(ValueError, match="checkpoint mismatch"):
        validate_control(training, evaluation)


def test_pairing_uses_episode_and_seed_not_row_order():
    rows = [{"source_episode": case, "seed": seed, "condition": condition,
             "episode_id": f"{condition}_{seed}", "environment_success": True, "stable_success": condition == "shifted",
             "steps": 100, "error": ""}
            for condition in ("standard", "shifted") for case, seed in [("demo_9", 102), ("demo_2", 101)]]
    result = paired_cases({"episodes": list(reversed(rows))})
    assert len(result) == 2 and all(not r["standard_stable_success"] and r["shifted_stable_success"] for r in result)
    with pytest.raises(ValueError, match="Missing paired"):
        paired_cases({"episodes": rows[:-1]})
    with pytest.raises(ValueError, match="Duplicate"):
        paired_cases({"episodes": rows + [rows[0]]})


def test_keyframes_expose_post_action_offset_and_reject_missing_steps():
    selected = frame_selection([0, 5, 10], [1, 5, 9], 10)
    assert [r["recorded_control_step"] for r in selected] == [1, 5, 9]
    assert [r["offset_steps"] for r in selected] == [1, 0, -1]
    assert frame_selection([3], [1, 5, 9], 10)[0]["recorded_control_step"] == 1
    for value in [-1, 11, 2.5, True]:
        with pytest.raises(ValueError):
            frame_selection([value], [1, 5, 9], 10)


def test_width_and_command_have_different_axes_and_shared_mark():
    data = {"eef_position": np.zeros((4, 3)), "object_position": np.zeros((4, 3)),
            "gripper_width": np.array([.08, .07, .03, .02]), "actions": np.ones((3, 7))}
    fig = failure_signal_figure(data, first_error_step=2)
    try:
        assert len(fig.axes) == 4
        assert "(m)" in fig.axes[2].get_ylabel() and "normalized" in fig.axes[3].get_ylabel()
        np.testing.assert_array_equal(fig.axes[2].lines[0].get_ydata(), data["gripper_width"])
        np.testing.assert_array_equal(fig.axes[3].lines[0].get_xdata(), [1, 2, 3])
        assert all(list(ax.lines[-1].get_xdata()) == [2, 2] for ax in fig.axes)
    finally:
        plt.close(fig)


def test_class_template_and_missing_experiment_never_fabricate_zero_scores(tmp_path):
    with open(ROOT / "docs/class_results.csv") as f:
        reader = csv.DictReader(f)
        assert reader.fieldnames == CLASS_FIELDS
        assert len(list(reader)) == 12
    write_json(tmp_path / "session.json", {"group": "group_03"})
    rows = collect_run(tmp_path, tmp_path)
    assert len(rows) == 2 and all(r["status"] == "incomplete_or_invalid" for r in rows)
    assert all("standard_stable_success_rate" not in r for r in rows)


def test_notebook_report_figures_use_report_directory_not_notebook_cwd(tmp_path, monkeypatch):
    import base64
    assets, report, unrelated = tmp_path / "assets", tmp_path / "report", tmp_path / "notebooks"
    for folder in (assets, report, unrelated):
        folder.mkdir()
    payload = b"fixture bytes for image embedding, not an experiment figure"
    (assets / "curve.png").write_bytes(payload)
    path = report / "report.md"
    original = "# Report\n![Curve](../assets/curve.png)"
    path.write_text(original)
    monkeypatch.chdir(unrelated)
    rendered = notebook_report_markdown(path)
    assert base64.b64encode(payload).decode() in rendered and "data:image/png;base64," in rendered
    assert path.read_text() == original
    (assets / "curve.png").unlink()
    with pytest.raises(FileNotFoundError):
        notebook_report_markdown(path)
