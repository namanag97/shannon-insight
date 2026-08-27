from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

pytest.importorskip("jsonschema")

ROOT = Path(__file__).resolve().parents[2]
VALIDATOR = (
    ROOT
    / "research"
    / "implementation_architecture"
    / "python_product_fit"
    / "validate.py"
)


def test_python_implementation_fit_is_deterministic_and_fail_closed() -> None:
    result = subprocess.run(
        [sys.executable, str(VALIDATOR), "--determinism"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
