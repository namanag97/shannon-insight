#!/usr/bin/env python3
"""Fail closed between the upstream presentation atlas and canonical adjudication."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
CANONICAL = ROOT / "research/product_ontology/inventory_challenges/presentation_experience_gap_audit"


def rows(name: str) -> list[dict]:
    return [json.loads(line) for line in (HERE / name).read_text(encoding="utf-8").splitlines() if line.strip()]


def main() -> int:
    errors: list[str] = []
    generated = subprocess.run(
        [sys.executable, str(HERE / "build_bundle.py"), "--check"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if generated.returncode:
        errors.append(generated.stdout.strip() or generated.stderr.strip())
    canonical = subprocess.run(
        [sys.executable, str(CANONICAL / "validate.py")],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if canonical.returncode:
        errors.append("canonical presentation audit failed: " + (canonical.stdout.strip() or canonical.stderr.strip()))

    seams = rows("target-seams.jsonl")
    products = rows("products.jsonl")
    source_claims = rows("source-claims.jsonl")
    summary = json.loads((HERE / "summary.json").read_text(encoding="utf-8"))
    if len({row["target_seam_id"] for row in seams}) != 50:
        errors.append("presentation atlas must expose exactly 50 unique upstream target seams")
    if any(row["canonical_contract_ref"] is not None or row["qualified"] or row["ratified"] for row in seams):
        errors.append("upstream atlas seam fabricated canonical ownership or authority")
    if any(row["semantic_authority"] or row["qualified"] for row in products):
        errors.append("provider observation fabricated semantic authority or qualification")
    if len(source_claims) != 2 or summary["machine_readable_evidence_source_count"] != 0:
        errors.append("narrative evidence claims were misrepresented as exact source records")
    if summary["integration_posture"] != "UPSTREAM_RESEARCH_INPUT_ONLY" or summary["completion_claim"]:
        errors.append("presentation atlas integration posture drift")

    if errors:
        for error in errors:
            print("ERROR: " + error)
        return 1
    print(
        "PASS presentation SOTA atlas bridge: 50 upstream seam candidates retained; "
        "canonical presentation-gap adjudication independently validates; "
        "0 source, ownership, qualification or ratification claims fabricated"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
