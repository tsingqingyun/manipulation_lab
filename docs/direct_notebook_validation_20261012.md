# Direct Notebook execution validation — 2026-10-12

The default entry is `bash scripts/prepare_notebooks.sh --group group_01`, followed by opening the four `.ipynb` files in an IDE and selecting the printed kernel. No separately launched Jupyter web server or manual port forwarding is part of this workflow. System graphics libraries and uv remain prerequisites.

## What changed

The new shell wrapper reuses the existing pinned installer. Its Python preparation step validates/downloads the same official dataset, runs native preflight, and registers a per-group Jupyter kernel carrying the selected device, renderer, dataset/output/reference paths and runtime settings. The default is CPU with OSMesa. Registration is repeatable; different groups/configurations get separate names, and an unexpected existing kernelspec is preserved. It saves only declared lab/renderer settings, not credentials or the whole process environment.

The Chinese and optional English README now put direct IDE use first. The repository recommends the Python/Jupyter extensions. Local Linux executes on the local computer; Remote SSH executes on the Linux server through the IDE connection. Students choose the exact registered Jupyter kernel, so they do not depend on exports from an integrated terminal.

## Validation record

The one-command entry created a fresh Python 3.12.13 environment with 163 compatible packages, checked the unchanged official HDF5, passed real headless preflight, and registered the configured kernel. This host used the documented public Ubuntu OSMesa extraction through an explicit renderer-library environment setting.

The kernel was then started with lab/rendering variables removed from its parent environment. It still reported the saved group, CPU device, OSMesa renderer, dataset and disabled JIT. All four notebooks executed sequentially through that kernel in **192.05 seconds**, without a Jupyter HTTP server. Notebook times were 7.33, 180.97, 0.87 and 2.01 seconds. This measures automated computation on this host, not student discussion time or a six-group deployment.

| Variant | Learning rate | Training | Standard stable placement | Position Shift stable placement |
|---|---:|---|---:|---:|
| lr_a | 0.001 | 50 epochs, seed 17 | 3/5 | 3/5 |
| lr_b | 0.0003 | 50 epochs, seed 17 | 5/5 | 5/5 |

Both checkpoints, all 20 actual evaluation cases and their videos were saved with zero execution errors. The fixed primary policy remains `lr_a`; its real failures were used for analysis. No seed was changed and no run was repeated to select a success rate. The exported ZIP passed its integrity check and contained two rows using the existing class-results schema. The generated report remains DRAFT because automated execution does not supply student answers.

The complete test suite passed **25 tests**. A subsequent focused reference-path correction added one regression case, and the final kernel-setup subset passed **4 tests**. This ensures a kernel registered before teacher preparation will still point to the documented future `checkpoints/reference_v1` location. Notebook 04's final download instruction was changed to refer to the IDE file explorer; this text-only edit was reviewed without repeating training.

Machine-readable results and source hashes are in [direct_notebook_validation_20261012.json](direct_notebook_validation_20261012.json). Raw setup logs, the fresh environment, executed notebooks, group outputs and ZIP are preserved in `outputs/direct_notebooks_20261012_v1/` and excluded from Git. Prior runs and source notebook outputs were not overwritten.

## Boundaries

This verifies actual standalone kernel execution using jupyter_client/nbclient on Linux. It does not claim that the VS Code GUI, its extension discovery menus, or interactive video playback were clicked and tested on this headless host. Follow the linked official [Notebook](https://code.visualstudio.com/docs/datascience/jupyter-notebooks) and [kernel picker](https://code.visualstudio.com/docs/datascience/jupyter-kernel-management) instructions. Native Windows/macOS, WSL2 and institution-specific SSH/extension installation policies remain unverified. Existing Linux system graphics prerequisites still apply.

The task, dataset, two learning rates, 50-epoch budgets, initialization seed, model architecture and evaluation criteria remain unchanged. Automated execution leaves student answers blank and reports DRAFT; students must still complete the written work.
