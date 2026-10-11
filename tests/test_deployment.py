"""Infrastructure regression fixtures; none of these are experiment metrics."""
import functools
import hashlib
import http.server
import importlib.util
import json
import os
from pathlib import Path
import signal
import stat
import subprocess
import sys
import threading

import h5py
import pytest
from manipulation_lab.common import ROOT


@pytest.fixture
def scripts(monkeypatch):
    monkeypatch.syspath_prepend(str(ROOT / "scripts"))
    modules = {}
    for name in ["start_lab", "preflight", "download_dataset"]:
        spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / f"{name}.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        modules[name] = module
    return modules


@pytest.mark.parametrize("via_wrapper", [False, True])
def test_jit_default_is_set_before_native_imports(via_wrapper):
    env = os.environ.copy()
    env.pop("NUMBA_DISABLE_JIT", None)
    code = "import manipulation_lab, numba; assert numba.config.DISABLE_JIT == 1"
    command = [str(ROOT / "scripts/lab_python.sh")] if via_wrapper else [sys.executable]
    subprocess.run([*command, "-c", code], env=env, check=True, timeout=30)
    # Explicit opt-in survives either path; no compilation occurs in this check.
    env["NUMBA_DISABLE_JIT"] = "0"
    subprocess.run([*command, "-c", code.replace("== 1", "== 0")], env=env, check=True, timeout=30)


def test_runtime_default_ignores_shared_data_dir_and_checks_modes(scripts, tmp_path, monkeypatch):
    module = scripts["start_lab"]
    monkeypatch.setattr(module.os, "geteuid", lambda: os.getuid())
    env = {"JUPYTER_DATA_DIR": str(tmp_path / "shared"), "JUPYTER_ALLOW_INSECURE_WRITES": "1"}
    runtime = module.prepare_runtime_dir(env)
    assert runtime.parent == Path('/tmp')
    assert stat.S_IMODE(runtime.stat().st_mode) & ~stat.S_ISVTX == 0o700
    assert runtime.stat().st_uid == os.getuid()
    assert env["JUPYTER_RUNTIME_DIR"] == str(runtime)
    assert "JUPYTER_ALLOW_INSECURE_WRITES" not in env
    # Jupyter adds a sticky bit after the first kernel; a restart must still work.
    private = tmp_path / "used-runtime"
    private.mkdir(mode=0o700)
    private.chmod(0o1700)
    assert module.prepare_runtime_dir({"JUPYTER_RUNTIME_DIR": str(private)}) == private
    assert stat.S_IMODE(private.stat().st_mode) == 0o1700
    bad = tmp_path / "shared-runtime"
    bad.mkdir(mode=0o755)
    with pytest.raises(RuntimeError, match="0700"):
        module.prepare_runtime_dir({"JUPYTER_RUNTIME_DIR": str(bad)})
    assert stat.S_IMODE(bad.stat().st_mode) == 0o755
    symlink = tmp_path / "runtime-link"
    symlink.symlink_to(runtime)
    with pytest.raises(RuntimeError, match="Unsafe"):
        module.prepare_runtime_dir({"JUPYTER_RUNTIME_DIR": str(symlink)})


def test_runtime_rejects_filesystem_that_ignores_file_modes(scripts, tmp_path, monkeypatch):
    module = scripts["start_lab"]
    real_mkstemp = module.tempfile.mkstemp
    def insecure_file(*args, **kwargs):
        fd, name = real_mkstemp(*args, **kwargs)
        os.fchmod(fd, 0o666)
        return fd, name
    monkeypatch.setattr(module.tempfile, "mkstemp", insecure_file)
    with pytest.raises(RuntimeError, match="0600"):
        module.prepare_runtime_dir({"JUPYTER_RUNTIME_DIR": str(tmp_path / "private")})


def test_root_launch_keeps_loopback_and_authentication(scripts):
    root = scripts["start_lab"].server_command(8892, euid=0)
    user = scripts["start_lab"].server_command(8892, euid=1000)
    assert root == user + ["--allow-root"]
    assert "--ip=127.0.0.1" in root and "--ServerApp.port_retries=0" in root
    assert not any("token" in arg.lower() or "password" in arg.lower() for arg in root)


def test_preflight_retains_native_crash_and_last_phase(scripts, tmp_path, monkeypatch):
    module = scripts["preflight"]
    original_run = subprocess.run
    def crash_worker(command, **kwargs):
        (tmp_path / "phase.json").write_text('{"phase": "fixture_native_crash"}')
        return original_run([sys.executable, "-X", "faulthandler", "-c",
            "import os, signal, resource; resource.setrlimit(resource.RLIMIT_CORE, (0, 0)); os.kill(os.getpid(), signal.SIGSEGV)"], **kwargs)
    monkeypatch.setattr(module.subprocess, "run", crash_worker)
    result = module.run_preflight("unused-infrastructure-fixture", tmp_path)
    assert not result["passed"] and result["signal"] == "SIGSEGV"
    assert result["worker_returncode"] == -signal.SIGSEGV
    assert result["last_phase"]["phase"] == "fixture_native_crash"
    assert "NUMBA_DISABLE_JIT=1" in result["recovery"]
    assert json.loads((tmp_path / "preflight.json").read_text()) == result
    assert "Fatal Python error" in (tmp_path / "preflight_worker.log").read_text()


def test_uv_lookup_survives_missing_path_and_explicit_override(tmp_path):
    # Fake executable tests discovery only, never an installation or model run.
    home = tmp_path / "fixture-home"
    uv = home / ".local/bin/uv"
    uv.parent.mkdir(parents=True)
    uv.write_text('#!/bin/sh\nprintf "uv discovery fixture\\n"\n')
    uv.chmod(0o755)
    env = {**os.environ, "HOME": str(home), "PATH": "/usr/bin:/bin"}
    for key in ["LAB_UV", "UV_INSTALL_DIR", "XDG_BIN_HOME", "XDG_DATA_HOME", "BASH_ENV"]:
        env.pop(key, None)
    command = ["/bin/bash", str(ROOT / "scripts/setup_environment.sh"), "--check-uv"]
    result = subprocess.run(command, env=env, capture_output=True, text=True, check=True)
    assert str(uv) in result.stdout
    override = tmp_path / "custom uv"
    override.write_text(uv.read_text()); override.chmod(0o755)
    result = subprocess.run(command, env={**env, "LAB_UV": str(override)}, capture_output=True, text=True, check=True)
    assert str(override) in result.stdout
    result = subprocess.run(command, env={**env, "LAB_UV": str(tmp_path / "missing")}, capture_output=True, text=True)
    assert result.returncode != 0 and "LAB_UV" in result.stderr


@pytest.fixture
def dataset_fixture(scripts, tmp_path, monkeypatch):
    # Tiny synthetic HDF5 only for transport/schema tests; actual dataset checked separately.
    module = scripts["download_dataset"]
    source = tmp_path / "fixture.hdf5"
    with h5py.File(source, "w") as f:
        data = f.create_group("data")
        for i in range(200):
            data.create_group(f"demo_{i}")
    monkeypatch.setattr(module, "EXPECTED_SHA256", hashlib.sha256(source.read_bytes()).hexdigest())
    return module, source


def test_offline_transport_validates_and_preserves_existing_files(dataset_fixture, tmp_path):
    module, source = dataset_fixture
    destination = tmp_path / "imported.hdf5"
    module.obtain_dataset(destination, from_file=source)
    assert destination.read_bytes() == source.read_bytes()
    assert stat.S_IMODE(destination.stat().st_mode) == 0o444
    provenance = json.loads(destination.with_suffix('.provenance.json').read_text())
    assert provenance["transport"] == "offline_copy" and provenance["sha256"] == module.EXPECTED_SHA256
    # Existing valid data needs no network, even if its configured source is unavailable.
    module.obtain_dataset(destination, url="https://unreachable.invalid/")
    corrupt = tmp_path / "corrupt.hdf5"
    corrupt.write_bytes(b"not the official dataset")
    target = tmp_path / "rejected.hdf5"
    with pytest.raises(ValueError, match="SHA256 mismatch"):
        module.obtain_dataset(target, from_file=corrupt)
    assert not target.exists() and target.with_suffix('.hdf5.partial').read_bytes() == corrupt.read_bytes()
    with pytest.raises(FileExistsError, match="Preserving"):
        module.obtain_dataset(target, from_file=source)


def test_http_mirror_and_configuration_precedence(dataset_fixture, tmp_path, monkeypatch):
    module, source = dataset_fixture
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(tmp_path))
    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True); thread.start()
    monkeypatch.setenv("NO_PROXY", "127.0.0.1")
    monkeypatch.setenv("no_proxy", "127.0.0.1")
    url = f"http://127.0.0.1:{server.server_port}/{source.name}"
    try:
        monkeypatch.setenv("HF_ENDPOINT", "https://mirror.example.invalid/")
        monkeypatch.delenv("LAB_DATASET_URL", raising=False)
        assert module.dataset_url().startswith("https://mirror.example.invalid/datasets/")
        monkeypatch.setenv("LAB_DATASET_URL", url)
        assert module.dataset_url() == url and module.dataset_url(url + '?explicit=1') == url + '?explicit=1'
        destination = tmp_path / "http.hdf5"
        module.obtain_dataset(destination)
        assert destination.read_bytes() == source.read_bytes()
        with pytest.raises(RuntimeError, match="--from-file"):
            module.obtain_dataset(tmp_path / "missing.hdf5", url=url + '.missing')
        assert module.source_label("https://name:secret@host/file?token=secret#fragment") == "https://host/file"
    finally:
        server.shutdown(); thread.join(); server.server_close()
