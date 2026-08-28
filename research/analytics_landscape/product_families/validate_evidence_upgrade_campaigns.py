#!/usr/bin/env python3
"""Fail-closed checks for effective B04 evidence-upgrade campaign projections."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
BUILDER = HERE / "build_evidence_upgrade_campaigns.py"
OUTPUTS = (
    HERE / "evidence-upgrade-campaigns.jsonl",
    HERE / "evidence-upgrade-campaign-summary.json",
)


def load_jsonl(path: Path) -> list[dict]:
    return [
        json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()
    ]


def main() -> int:
    before = {path: path.read_bytes() for path in OUTPUTS}
    campaigns = load_jsonl(OUTPUTS[0])
    summary = json.loads(OUTPUTS[1].read_text(encoding="utf-8"))
    upgrades = load_jsonl(HERE / "effective-evidence-upgrade-dispositions.jsonl")
    upgraded_claims = {
        row["claim_id"] for row in upgrades if row["disposition_kind"] == "BASE_CLAIM_UPGRADE"
    }
    base_claims = load_jsonl(HERE / "organization-family-membership-claims.jsonl")
    remaining_claims = [row for row in base_claims if row["claim_id"] not in upgraded_claims]

    assert len(campaigns) == len({row["organization_id"] for row in remaining_claims})
    assert sum(row["weak_membership_count"] for row in campaigns) == len(remaining_claims)
    assert summary["base_membership_claim_count"] == len(base_claims)
    assert summary["exact_membership_upgrade_count"] == len(upgraded_claims)
    assert summary["remaining_weak_membership_count"] == len(remaining_claims)
    assert summary["semantic_authority_promotions"] == summary["qualification_promotions"] == 0
    assert summary["completion_claim"] is False
    assert all(row["completion_claim"] is False for row in campaigns)

    result = subprocess.run(
        [sys.executable, str(BUILDER)], cwd=HERE, capture_output=True, text=True
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert before == {path: path.read_bytes() for path in OUTPUTS}, "campaign outputs are stale"
    print(
        f"PASS B04 evidence-upgrade campaigns: {len(upgraded_claims)} exact upgrades retained; "
        f"{len(remaining_claims)} weak claims routed into {len(campaigns)} organization campaigns"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
