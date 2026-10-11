from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np


def training_curve(rows, path):
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.plot([r["epoch"] for r in rows], [r["training_loss"] for r in rows], label="Train")
    ax.plot([r["epoch"] for r in rows], [r["validation_loss"] for r in rows], label="Validation episodes")
    best = min(rows, key=lambda r: r["validation_loss"])
    ax.axvline(best["epoch"], linestyle="--", color="gray", label=f"Selected epoch {best['epoch']}")
    ax.set(xlabel="Epoch (full training-set pass)", ylabel="Action MSE (normalized action units squared)", yscale="log")
    ax.legend(); fig.tight_layout(); fig.savefig(path, dpi=140); plt.close(fig)


def success_plot(summary, path):
    names = list(summary["conditions"])
    fig, ax = plt.subplots(figsize=(7, 4))
    x = np.arange(len(names))
    for delta, key, label in [(-.18, "environment_success_rate", "Environment"), (.18, "stable_success_rate", "Stable released placement")]:
        ax.bar(x + delta, [summary["conditions"][n][key] for n in names], .36, label=label)
    ax.set(xticks=x, xticklabels=names, ylim=(0, 1), ylabel="Success fraction")
    ax.legend(); fig.tight_layout(); fig.savefig(path, dpi=140); plt.close(fig)


def demonstration_figures(inspection, episode, positions, actions, output):
    """Save actual recorded demonstration signals and split-specific initial positions."""
    output = Path(output)
    fig, axes = plt.subplots(2, 1, figsize=(8, 5), sharex=True)
    for i, axis in enumerate("XYZ"):
        axes[0].plot(positions[:, i], label=axis)
    axes[0].set(ylabel="Can world position (m)", title=f"Human demonstration {episode}")
    axes[0].legend()
    axes[1].plot(actions[:, -1])
    axes[1].set(ylabel="Gripper command (normalized)", xlabel="Recorded control step (20 Hz)", ylim=(-1.1, 1.1))
    fig.tight_layout(); fig.savefig(output / "demonstration_signals.png", dpi=140); plt.close(fig)
    lookup = {e["episode"]: e["initial_object_position_m"] for e in inspection["episodes"]}
    fig, ax = plt.subplots(figsize=(7, 5))
    for split, episodes in inspection["splits"].items():
        xy = np.asarray([lookup[e][:2] for e in episodes])
        ax.scatter(xy[:, 0], xy[:, 1], s=20, alpha=.65, label=f"{split}: {len(episodes)} episodes")
    ax.set(xlabel="Can initial world X (m)", ylabel="Can initial world Y (m)", title="Recorded initial positions by fixed episode split")
    ax.set_aspect("equal", adjustable="datalim"); ax.legend()
    fig.tight_layout(); fig.savefig(output / "demonstration_positions.png", dpi=140); plt.close(fig)
