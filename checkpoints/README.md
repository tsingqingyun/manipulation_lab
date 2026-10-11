# Generated Checkpoints

No trained model is distributed in Git. Notebook 02 saves both student checkpoints in the group's versioned output directory. An instructor generates the existing fixed reference from public data with:

```bash
scripts/lab_python.sh scripts/prepare_reference.py --train --output checkpoints/reference_v1
export LAB_REFERENCE_ROOT="$PWD/checkpoints/reference_v1"
```

The directory contains the reference checkpoint, fixed evaluation, real failure evidence and a readiness manifest. Set the compute/rendering variables first as described in README. Checkpoints are ignored by Git; preserve them with their configuration and dataset/version contract.
