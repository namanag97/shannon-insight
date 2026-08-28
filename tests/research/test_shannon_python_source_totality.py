from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
VALIDATOR = (
    ROOT
    / "research"
    / "product_ontology"
    / "implementation_placement"
    / "validate_shannon_python_source_totality.py"
)


def test_shannon_python_source_placement_is_total() -> None:
    result = subprocess.run(
        [sys.executable, str(VALIDATOR)],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
