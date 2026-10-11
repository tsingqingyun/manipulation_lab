"""Manipulation Learning Lab. Real data, explicit provenance, isolated runs."""
import os

# Set before importing MuJoCo / BLAS. Administrators may override these.
os.environ.setdefault("MUJOCO_GL", "egl")
os.environ.setdefault("OMP_NUM_THREADS", "2")
os.environ.setdefault("MKL_NUM_THREADS", "2")
os.environ.setdefault("MPLBACKEND", "Agg")
