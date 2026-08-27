#!/usr/bin/env python3
"""Validate lossless B07 review factoring and its non-authoritative posture."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def rows(name: str) -> list[dict]:
    return [json.loads(line) for line in (HERE / name).read_text(encoding="utf-8").splitlines() if line.strip()]


def main() -> int:
    check = subprocess.run(
        [sys.executable, str(HERE / "build_canonical_reference_review_batches.py"), "--check"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if check.returncode:
        print("ERROR: " + (check.stdout.strip() or check.stderr.strip()))
        return 1
    candidates = rows("canonical-reference-auto-alias-candidates.jsonl")
    batches = rows("canonical-reference-machine-review-batches.jsonl")
    summary = json.loads((HERE / "canonical-reference-machine-review-summary.json").read_text(encoding="utf-8"))
    candidate_ids = {row["candidate_id"] for row in candidates}
    represented = [ref for batch in batches for ref in batch["candidate_refs"]]
    assert len(candidate_ids) == len(candidates) == len(represented) == len(set(represented))
    assert set(represented) == candidate_ids
    assert sum(row["candidate_count"] for row in batches) == len(candidates)
    assert sum(row["occurrence_count"] for row in batches) == sum(row["occurrence_count"] for row in candidates)
    assert all(row["status"] == "OPEN_MACHINE_FACTORED_SEMANTIC_REVIEW" for row in batches)
    assert all(row["completion_claim"] is False for row in batches)
    assert summary["semantic_decisions_created"] == summary["authority_receipts_created"] == 0
    assert summary["completion_claim"] is False
    print(
        f"PASS B07 semantic-review batching: {len(candidates)} exact candidates factor losslessly "
        f"into {len(batches)} owner-review batches; 0 decisions or authority receipts inferred"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
