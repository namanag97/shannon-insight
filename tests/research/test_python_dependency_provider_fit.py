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
    / "validate_dependency_provider_crosswalk.py"
)


def test_python_dependencies_remain_unqualified_providers() -> None:
    result = subprocess.run(
        [sys.executable, str(VALIDATOR), "--determinism"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
