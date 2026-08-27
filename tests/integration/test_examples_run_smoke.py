import os
import pathlib
import subprocess
import sys

import pytest

pytestmark = pytest.mark.integration

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]


@pytest.mark.skipif(os.environ.get("RUN_INTEGRATION") != "1", reason="Set RUN_INTEGRATION=1 to run example smoke tests")
def test_examples_get_quote_virtual_smoke():
    cfg = REPO_ROOT / "config.example.virtual.yaml"
    script = REPO_ROOT / "examples" / "01_basic" / "get_quote.py"
    proc = subprocess.run([sys.executable, str(script), "--config", str(cfg)], capture_output=True, text=True)
    assert proc.returncode == 0, proc.stderr


@pytest.mark.skipif(os.environ.get("RUN_INTEGRATION") != "1", reason="Set RUN_INTEGRATION=1 to run example smoke tests")
def test_examples_get_balance_virtual_smoke():
    cfg = REPO_ROOT / "config.example.virtual.yaml"
    script = REPO_ROOT / "examples" / "01_basic" / "get_balance.py"
    proc = subprocess.run([sys.executable, str(script), "--config", str(cfg)], capture_output=True, text=True)
    assert proc.returncode == 0, proc.stderr
