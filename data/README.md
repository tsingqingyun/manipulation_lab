Shared read-only human demonstrations: `low_dim_v15.hdf5`, official Can PH v1.5, 200 episodes / 23207 control steps.

Download with `scripts/lab_python.sh scripts/download_dataset.py`. SHA256 must be `3f2eb92e0a5025d0095e866ac16cc8092d6a762abe27dec90dbaff9027282962`. The downloader refuses changed bytes. Source: https://huggingface.co/datasets/amandlek/robomimic/resolve/main/v1.5/can/ph/low_dim_v15.hdf5?download=true

Never append learned-policy rollouts, failures or fabricated labels. Outputs and checkpoints are separate. The 160/20/20 episode split is deterministic (seed 20261011) and recorded in each run. Dataset files are intentionally not in Git.
