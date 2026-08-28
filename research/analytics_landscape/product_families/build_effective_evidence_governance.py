#!/usr/bin/env python3
"""Build sparse effective B04 evidence dispositions over immutable weak base claims."""
from __future__ import annotations

import json
from pathlib import Path
from urllib.parse import urlparse

HERE = Path(__file__).resolve().parent
BASE = HERE / "organization-family-membership-claims.jsonl"
UPGRADE_GLOB = "organization-family-evidence-upgrades*.jsonl"
OUTPUT = HERE / "effective-evidence-upgrade-dispositions.jsonl"
SUMMARY = HERE / "effective-evidence-governance-summary.json"
REQ = {
    "upgrade_id",
    "claim_id",
    "organization_id",
    "family_id",
    "product_id",
    "product_name",
    "official_locator",
    "bounded_claim",
    "evidence_role",
    "evidence_strength",
    "verified_on",
    "organization_product_relationship",
    "identity_posture",
    "acquisition_or_rename_posture",
}


def load_jsonl(path: Path) -> list[dict]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def is_homepage(url: str) -> bool:
    return not (urlparse(url).path or "/").strip("/")


def main() -> int:
    base = load_jsonl(BASE)
    upgrade_paths = sorted(HERE.glob(UPGRADE_GLOB))
    if not upgrade_paths:
        raise SystemExit(f"no exact-evidence overlay shards match {UPGRADE_GLOB}")
    upgrades = [row for path in upgrade_paths for row in load_jsonl(path)]
    by_claim = {row["claim_id"]: row for row in base}
    if len(by_claim) != len(base):
        raise SystemExit("duplicate base claims")

    seen_upgrade_ids: set[str] = set()
    seen_claim_ids: set[str] = set()
    output: list[dict] = []
    for upgrade in upgrades:
        missing = REQ - upgrade.keys()
        if missing:
            raise SystemExit(
                f"{upgrade.get('upgrade_id')}: missing {sorted(missing)}"
            )
        if (
            upgrade["upgrade_id"] in seen_upgrade_ids
            or upgrade["claim_id"] in seen_claim_ids
        ):
            raise SystemExit("duplicate upgrade or claim target across overlay shards")
        base_claim = by_claim.get(upgrade["claim_id"])
        if not base_claim:
            raise SystemExit(f"unknown base claim: {upgrade['claim_id']}")
        if (upgrade["organization_id"], upgrade["family_id"]) != (
            base_claim["organization_id"],
            base_claim["family_id"],
        ):
            raise SystemExit(f"scope drift: {upgrade['upgrade_id']}")
        parsed = urlparse(upgrade["official_locator"])
        if (
            parsed.scheme != "https"
            or not parsed.netloc
            or is_homepage(upgrade["official_locator"])
        ):
            raise SystemExit(f"non-exact locator: {upgrade['upgrade_id']}")
        if (
            upgrade["evidence_role"] != "product_boundary_evidence"
            or upgrade["evidence_strength"]
            != "STRONG_EXACT_OFFICIAL_PRODUCT_DOCUMENTATION"
        ):
            raise SystemExit(f"invalid evidence posture: {upgrade['upgrade_id']}")
        for field in ("semantic_authority", "qualification_claim", "completion_claim"):
            if upgrade.get(field) is not False:
                raise SystemExit(f"illegal promotion {field}: {upgrade['upgrade_id']}")

        seen_upgrade_ids.add(upgrade["upgrade_id"])
        seen_claim_ids.add(upgrade["claim_id"])
        output.append(
            {
                **upgrade,
                "source_overlay_path": str(
                    next(
                        path.relative_to(HERE)
                        for path in upgrade_paths
                        if any(
                            row.get("upgrade_id") == upgrade["upgrade_id"]
                            for row in load_jsonl(path)
                        )
                    )
                ),
                "base_evidence_locator": base_claim["evidence_locator"],
                "base_evidence_strength": base_claim["evidence_strength"],
                "effective_status": (
                    "BOUND_STRONG_EXACT_PRODUCT_EVIDENCE_AUTHORITY_WITHHELD"
                ),
            }
        )

    output.sort(key=lambda row: row["claim_id"])
    OUTPUT.write_text(
        "".join(json.dumps(row, sort_keys=True) + "\n" for row in output),
        encoding="utf-8",
    )
    organizations = sorted({row["organization_id"] for row in output})
    families = sorted({row["family_id"] for row in output})
    summary = {
        "report_id": "effective_horizontal_evidence_governance",
        "as_of": "2026-08-28",
        "base_membership_claim_count": len(base),
        "exact_evidence_overlay_shard_count": len(upgrade_paths),
        "exact_evidence_overlay_paths": [
            str(path.relative_to(HERE)) for path in upgrade_paths
        ],
        "exact_evidence_upgrade_count": len(output),
        "strong_exact_product_membership_claim_count": len(output),
        "remaining_weak_membership_claim_count": len(base) - len(output),
        "organization_count_with_exact_upgrade": len(organizations),
        "family_count_with_exact_upgrade": len(families),
        "upgraded_organization_ids": organizations,
        "upgraded_family_ids": families,
        "semantic_authority_promotions": 0,
        "qualification_promotions": 0,
        "completion_claim": False,
        "status": "EXACT_EVIDENCE_OVERLAY_ACTIVE_REMAINING_WEAK_CLAIMS_EXPLICIT",
    }
    SUMMARY.write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
