#!/usr/bin/env python3
"""Prioritize the remaining weak organization-family claims into research campaigns."""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent


def load_jsonl(name: str) -> list[dict]:
    path = HERE / name
    if not path.is_file():
        return []
    return [
        json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()
    ]


def main() -> int:
    base_claims = load_jsonl("organization-family-membership-claims.jsonl")
    identities = load_jsonl("organization-identity-projection.jsonl")
    upgrades = load_jsonl("effective-evidence-upgrade-dispositions.jsonl")
    identity_by_id = {row["organization_id"]: row for row in identities}
    upgraded_claim_ids = {row["claim_id"] for row in upgrades}
    if not upgraded_claim_ids <= {row["claim_id"] for row in base_claims}:
        raise SystemExit("effective evidence overlay targets an unknown base claim")

    remaining_by_organization: dict[str, list[dict]] = defaultdict(list)
    upgraded_by_organization: dict[str, int] = defaultdict(int)
    for claim in base_claims:
        organization_id = claim["organization_id"]
        if claim["claim_id"] in upgraded_claim_ids:
            upgraded_by_organization[organization_id] += 1
        else:
            remaining_by_organization[organization_id].append(claim)

    rows = []
    for organization_id, claims in remaining_by_organization.items():
        identity = identity_by_id[organization_id]
        families = sorted({claim["family_id"] for claim in claims})
        homepage_only = sum(claim["evidence_strength"] == "WEAK_HOMEPAGE_ONLY" for claim in claims)
        rows.append(
            {
                "record_kind": "horizontal_evidence_upgrade_campaign",
                "campaign_id": "evidence-upgrade." + organization_id,
                "organization_id": organization_id,
                "canonical_name": identity["canonical_name"],
                "canonical_url": identity["canonical_url"],
                "organization_kind": identity["organization_kind"],
                "family_refs": families,
                "weak_membership_count": len(claims),
                "homepage_only_count": homepage_only,
                "exact_membership_already_upgraded_count": upgraded_by_organization[
                    organization_id
                ],
                "priority_score": len(claims) * 10 + homepage_only * 3,
                "required_evidence_upgrade": [
                    "exact product/project identity",
                    "official product/technical/specification/release locator",
                    "bounded capability/adoption claim per supported family",
                    "edition/version/effective date when applicable",
                    "organization-product/project relationship",
                    "acquisition/rename/parent identity if applicable",
                ],
                "promotion_law": "A product page may strengthen only the family claims its exact bounded capability statement supports; organization-wide reputation is never transitive evidence.",
                "status": "OPEN_EVIDENCE_RESEARCH",
                "completion_claim": False,
            }
        )
    rows.sort(
        key=lambda row: (
            -row["priority_score"],
            -row["weak_membership_count"],
            row["canonical_name"],
        )
    )

    (HERE / "evidence-upgrade-campaigns.jsonl").write_text(
        "".join(json.dumps(row, sort_keys=True) + "\n" for row in rows), encoding="utf-8"
    )
    remaining_weak_count = sum(row["weak_membership_count"] for row in rows)
    summary = {
        "report_id": "horizontal_evidence_upgrade_campaigns",
        "as_of": "2026-08-28",
        "base_membership_claim_count": len(base_claims),
        "exact_membership_upgrade_count": len(upgraded_claim_ids),
        "remaining_weak_membership_count": remaining_weak_count,
        "organization_campaign_count": len(rows),
        "top_20_campaigns": [
            {
                "organization_id": row["organization_id"],
                "name": row["canonical_name"],
                "weak_membership_count": row["weak_membership_count"],
                "priority_score": row["priority_score"],
            }
            for row in rows[:20]
        ],
        "semantic_authority_promotions": 0,
        "qualification_promotions": 0,
        "completion_claim": False,
        "status": "PRIORITIZED_REMAINING_EXACT_EVIDENCE_RESEARCH",
    }
    (HERE / "evidence-upgrade-campaign-summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
