"""Kernel registration tests; fixtures are not student experiment evidence."""
import importlib.util
import json
import os
from pathlib import Path
import subprocess

import pytest
from manipulation_lab.common import ROOT


@pytest.fixture
def setup(monkeypatch):
    monkeypatch.syspath_prepend(str(ROOT / 'scripts'))
    spec = importlib.util.spec_from_file_location('prepare_notebooks', ROOT / 'scripts/prepare_notebooks.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_kernel_registration_is_repeatable_and_preserves_other_groups(setup, tmp_path):
    env = setup.kernel_environment('group_01', 'cpu', 'osmesa', tmp_path / 'data.hdf5')
    first = setup.register_kernel(env, tmp_path / 'kernels')
    original = (Path(first['directory']) / 'kernel.json').read_bytes()
    assert setup.register_kernel(env, tmp_path / 'kernels') == first
    second = setup.register_kernel({**env, 'LAB_GROUP': 'group_02'}, tmp_path / 'kernels')
    changed = setup.register_kernel({**env, 'MUJOCO_GL': 'egl'}, tmp_path / 'kernels')
    assert len({first['name'], second['name'], changed['name']}) == 3
    assert (Path(first['directory']) / 'kernel.json').read_bytes() == original
    assert json.loads(original)['argv'][-1] == '{connection_file}'
    # Preserve a user-edited spec instead of overwriting it on the next setup.
    (Path(first['directory']) / 'kernel.json').write_text('{}')
    with pytest.raises(FileExistsError, match='Preserving'):
        setup.register_kernel(env, tmp_path / 'kernels')


def test_kernel_saves_only_lab_configuration_not_secrets(setup, tmp_path, monkeypatch):
    monkeypatch.setenv('HTTPS_PROXY', 'http://credential-fixture.invalid')
    monkeypatch.setenv('EXAMPLE_API_TOKEN', 'unit-fixture-not-a-real-secret')
    monkeypatch.setenv('LAB_OUTPUT_ROOT', str(tmp_path / 'outputs'))
    monkeypatch.setenv('LAB_REFERENCE_ROOT', str(tmp_path / 'reference'))
    monkeypatch.setenv('LD_LIBRARY_PATH', '/example/renderer-libraries')
    env = setup.kernel_environment('group_03', 'cpu', 'osmesa', tmp_path / 'data.hdf5')
    assert env['LAB_OUTPUT_ROOT'] == str(tmp_path / 'outputs')
    assert env['LAB_REFERENCE_ROOT'] == str(tmp_path / 'reference')
    assert env['LD_LIBRARY_PATH'] == '/example/renderer-libraries'
    assert env['LAB_GROUP'] == 'group_03' and env['MUJOCO_GL'] == 'osmesa'
    assert env['LAB_DEVICE'] == 'cpu' and env['NUMBA_DISABLE_JIT'] == '1'
    assert 'HTTPS_PROXY' not in env and 'EXAMPLE_API_TOKEN' not in env


def test_one_command_help_does_not_install_or_download():
    result = subprocess.run(['bash', str(ROOT / 'scripts/prepare_notebooks.sh'), '--help'],
                            check=True, capture_output=True, text=True)
    assert '--from-file' in result.stdout and '--group' in result.stdout
    assert 'no web server or tunnel' in result.stdout


def test_kernel_can_be_registered_before_reference_is_generated(setup, tmp_path, monkeypatch):
    monkeypatch.setattr(setup, 'ROOT', tmp_path)
    monkeypatch.delenv('LAB_REFERENCE_ROOT', raising=False)
    env = setup.kernel_environment('group_01', 'cpu', 'osmesa', tmp_path / 'data.hdf5')
    assert env['LAB_REFERENCE_ROOT'] == str(tmp_path / 'checkpoints/reference_v1')
