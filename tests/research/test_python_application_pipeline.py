from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
VALIDATOR = (
    ROOT
    / "research"
    / "implementation_architecture"
    / "python_product_fit"
    / "validate_application_pipeline.py"
)


def test_python_application_pipeline_has_total_stage_ownership() -> None:
    result = subprocess.run(
        [sys.executable, str(VALIDATOR)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
