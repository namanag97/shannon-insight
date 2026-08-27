#!/usr/bin/env python3
"""Validate B04 evidence-upgrade campaigns without promoting open claims."""
from __future__ import annotations

import json
import tempfile
from pathlib import Path
from typing import Any

from build_evidence_upgrade_campaigns import compare_outputs, write_outputs

HERE = Path(__file__).resolve().parent


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def main() -> int:
    errors: list[str] = []
    with tempfile.TemporaryDirectory(prefix="b04-evidence-upgrade-") as raw:
        rebuilt = Path(raw)
        write_outputs(rebuilt)
        errors.extend(compare_outputs(HERE, rebuilt))

    claims = load_jsonl(HERE / "organization-family-membership-claims.jsonl")
    identities = load_jsonl(HERE / "organization-identity-projection.jsonl")
    gaps = load_jsonl(HERE / "organization-identity-gaps.jsonl")
    campaigns = load_jsonl(HERE / "evidence-upgrade-campaigns.jsonl")
    summary = load(HERE / "evidence-upgrade-campaign-summary.json")
    identity_ids = {row["organization_id"] for row in identities}
    gap_ids = {row["organization_id"] for row in gaps}
    campaign_ids = [row["organization_id"] for row in campaigns]

    if set(campaign_ids) != identity_ids or set(campaign_ids) != gap_ids:
        errors.append("campaigns must cover every provisional organization exactly once")
    if len(campaign_ids) != len(set(campaign_ids)):
        errors.append("duplicate organization campaign")
    if campaigns != sorted(
        campaigns,
        key=lambda row: (
            -row["priority_score"],
            -row["weak_membership_count"],
            row["canonical_name"].casefold(),
            row["organization_id"],
        ),
    ):
        errors.append("campaign ordering is not deterministic")
    for row in campaigns:
        if row["status"] != "OPEN_EVIDENCE_AND_IDENTITY_RESEARCH":
            errors.append(f"campaign state overclaim {row['campaign_id']}")
        if row["identity_status"] != "PROVISIONAL_INTERNAL_HANDLE":
            errors.append(f"campaign identity state overclaim {row['campaign_id']}")
        if row["open_exact_locator_count"] != row["weak_membership_count"]:
            errors.append(f"campaign exact locator count drift {row['campaign_id']}")
        if len(row["required_evidence_upgrade"]) < 8:
            errors.append(f"campaign obligations incomplete {row['campaign_id']}")
        if (
            row["semantic_authority"]
            or row["implementation_qualification"]
            or row["executed_acceptance"]
            or row["completion_claim"]
        ):
            errors.append(f"campaign invents downstream evidence {row['campaign_id']}")

    expected = {
        "organization_campaign_count": len(identity_ids),
        "weak_membership_count": len(claims),
        "open_exact_locator_count": len(claims),
        "provisional_identity_campaign_count": len(identity_ids),
    }
    for key, value in expected.items():
        if summary.get(key) != value:
            errors.append(f"campaign summary drift {key}: {summary.get(key)} != {value}")
    for key in (
        "strong_memberships_created",
        "semantic_ratifications_created",
        "implementation_qualifications_created",
        "executed_acceptances_created",
    ):
        if summary.get(key) != 0:
            errors.append("campaign summary invents gated evidence: " + key)
    if summary.get("completion_claim") is not False:
        errors.append("campaign completion fabricated")

    if errors:
        for error in errors:
            print("ERROR: " + error)
        return 1
    print(
        "PASS B04 evidence-upgrade campaigns: "
        f"{len(campaigns)} organizations; {len(claims)} weak claims; no promotion"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
