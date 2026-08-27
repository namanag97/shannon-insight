"""Regression tests for the application-behavior research corpus."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = ROOT / "research/domain_atlas/universes/application_behavior"


def run_validator(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(PACKAGE / "validate_corpus.py"), *args],
        cwd=PACKAGE,
        capture_output=True,
        text=True,
        check=False,
    )


def test_application_behavior_corpus_is_deterministic_and_fail_closed() -> None:
    result = run_validator("--determinism")
    assert result.returncode == 0, result.stdout + result.stderr

    coverage = json.loads((PACKAGE / "coverage-report.json").read_text(encoding="utf-8"))
    assert coverage["completion_claim"] is False
    assert coverage["qualification"]["qualified_implementations"] == 0
    assert coverage["qualification"]["binding_eligible_offers"] == 0
    assert coverage["qualification"]["executed_conformance_tests"] == 0
    assert len(coverage["assembly_mechanisms"]) >= 3


def test_application_behavior_has_one_open_gap_for_each_unresolved_promotion_class() -> None:
    gaps = [
        json.loads(line)
        for line in (PACKAGE / "gaps.jsonl").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    categories = {gap["category"] for gap in gaps}
    assert {
        "semantic_ownership",
        "implementation",
        "portability",
        "vertical",
        "authority",
        "coverage",
    } <= categories
    assert all(gap["status"] == "OPEN" and gap["completion_claim"] is False for gap in gaps)
