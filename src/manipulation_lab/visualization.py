from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np


def training_curve(rows, path):
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.plot([r["epoch"] for r in rows], [r["training_loss"] for r in rows], label="Train")
    ax.plot([r["epoch"] for r in rows], [r["validation_loss"] for r in rows], label="Validation episodes")
    ax.set(xlabel="Epoch (full training-set pass)", ylabel="Action MSE", yscale="log")
    ax.legend(); fig.tight_layout(); fig.savefig(path, dpi=140); plt.close(fig)


def success_plot(summary, path):
    names = list(summary["conditions"])
    fig, ax = plt.subplots(figsize=(7, 4))
    x = np.arange(len(names))
    for delta, key, label in [(-.18, "environment_success_rate", "Environment"), (.18, "stable_success_rate", "Stable released placement")]:
        ax.bar(x + delta, [summary["conditions"][n][key] for n in names], .36, label=label)
    ax.set(xticks=x, xticklabels=names, ylim=(0, 1), ylabel="Success fraction")
    ax.legend(); fig.tight_layout(); fig.savefig(path, dpi=140); plt.close(fig)
