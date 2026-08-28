#!/usr/bin/env python3
"""Build effective B04 evidence governance by overlaying exact upgrades on weak base claims.

The base claim generator remains an observation of organization-to-family coverage. Exact product
or project evidence lives in a separate source ledger so regeneration cannot erase research. An
upgrade may strengthen exactly one existing claim and never conveys semantic authority,
implementation qualification, or product-boundary ratification.
"""
from __future__ import annotations

import json
from pathlib import Path
from urllib.parse import urlparse

HERE = Path(__file__).resolve().parent
BASE = HERE / "organization-family-membership-claims.jsonl"
UPGRADES = HERE / "organization-family-evidence-upgrades.jsonl"
OUTPUT = HERE / "effective-organization-family-membership-claims.jsonl"
SUMMARY = HERE / "effective-evidence-governance-summary.json"

REQUIRED_UPGRADE_FIELDS = {
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
    if not path.is_file():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def homepage_like(url: str) -> bool:
    parsed = urlparse(url)
    return (parsed.path or "/").strip("/") == ""


def validate_upgrade(row: dict, base: dict) -> None:
    missing = REQUIRED_UPGRADE_FIELDS - row.keys()
    if missing:
        raise ValueError(f"{row.get('upgrade_id')}: missing fields {sorted(missing)}")
    if row["claim_id"] != base["claim_id"]:
        raise ValueError(f"{row['upgrade_id']}: claim identity mismatch")
    if row["organization_id"] != base["organization_id"] or row["family_id"] != base["family_id"]:
        raise ValueError(f"{row['upgrade_id']}: organization/family scope mismatch")
    if row["evidence_role"] != "product_boundary_evidence":
        raise ValueError(f"{row['upgrade_id']}: evidence role must remain product-boundary evidence")
    if row["evidence_strength"] != "STRONG_EXACT_OFFICIAL_PRODUCT_DOCUMENTATION":
        raise ValueError(f"{row['upgrade_id']}: unsupported promotion strength")
    locator = row["official_locator"]
    parsed = urlparse(locator)
    if parsed.scheme != "https" or not parsed.netloc or homepage_like(locator):
        raise ValueError(f"{row['upgrade_id']}: exact non-homepage HTTPS locator required")
    if not row["product_id"] or not row["product_name"] or not row["bounded_claim"]:
        raise ValueError(f"{row['upgrade_id']}: exact product identity and bounded claim required")
    if not row["organization_product_relationship"] or not row["identity_posture"]:
        raise ValueError(f"{row['upgrade_id']}: identity relationship posture required")
    for forbidden in ("semantic_authority", "qualification_claim", "completion_claim"):
        if row.get(forbidden) is not False:
            raise ValueError(f"{row['upgrade_id']}: {forbidden} must remain false")


def main() -> int:
    base_rows = load_jsonl(BASE)
    upgrades = load_jsonl(UPGRADES)
    if not base_rows:
        raise SystemExit("base organization-family membership claims missing")

    by_claim = {row["claim_id"]: row for row in base_rows}
    if len(by_claim) != len(base_rows):
        raise SystemExit("base claim ids are duplicated")

    seen_upgrades: set[str] = set()
    seen_claims: set[str] = set()
    overlay: dict[str, dict] = {}
    for row in upgrades:
        uid = row.get("upgrade_id")
        cid = row.get("claim_id")
        if uid in seen_upgrades:
            raise SystemExit(f"duplicate upgrade id: {uid}")
        if cid in seen_claims:
            raise SystemExit(f"multiple upgrades target one claim: {cid}")
        if cid not in by_claim:
            raise SystemExit(f"upgrade targets unknown base claim: {cid}")
        validate_upgrade(row, by_claim[cid])
        seen_upgrades.add(uid)
        seen_claims.add(cid)
        overlay[cid] = row

    effective: list[dict] = []
    for base in base_rows:
        cid = base["claim_id"]
        upgrade = overlay.get(cid)
        if not upgrade:
            effective.append(dict(base))
            continue
        row = dict(base)
        row.update(
            {
                "claim": upgrade["bounded_claim"],
                "claim_scope": "exact_product_capability_adoption_evidence_only",
                "evidence_locator": upgrade["official_locator"],
                "evidence_locator_kind": "official_product_or_technical_documentation",
                "evidence_strength": upgrade["evidence_strength"],
                "status": "BOUND_STRONG_EXACT_PRODUCT_EVIDENCE_AUTHORITY_WITHHELD",
                "product_id": upgrade["product_id"],
                "product_name": upgrade["product_name"],
                "verified_on": upgrade["verified_on"],
                "organization_product_relationship": upgrade["organization_product_relationship"],
                "identity_posture": upgrade["identity_posture"],
                "acquisition_or_rename_posture": upgrade["acquisition_or_rename_posture"],
                "upgrade_id": upgrade["upgrade_id"],
                "required_upgrade": [],
                "semantic_authority": False,
                "qualification_claim": False,
                "completion_claim": False,
            }
        )
        effective.append(row)

    effective.sort(key=lambda row: row["claim_id"])
    OUTPUT.write_text(
        "".join(json.dumps(row, sort_keys=True) + "\n" for row in effective), encoding="utf-8"
    )
    strong = sum(
        row.get("evidence_strength") == "STRONG_EXACT_OFFICIAL_PRODUCT_DOCUMENTATION"
        for row in effective
    )
    organizations_upgraded = sorted({row["organization_id"] for row in upgrades})
    families_upgraded = sorted({row["family_id"] for row in upgrades})
    summary = {
        "report_id": "effective_horizontal_evidence_governance",
        "as_of": "2026-08-28",
        "base_membership_claim_count": len(base_rows),
        "exact_evidence_upgrade_count": len(upgrades),
        "strong_exact_product_membership_claim_count": strong,
        "remaining_weak_membership_claim_count": len(effective) - strong,
        "organization_count_with_exact_upgrade": len(organizations_upgraded),
        "family_count_with_exact_upgrade": len(families_upgraded),
        "upgraded_organization_ids": organizations_upgraded,
        "upgraded_family_ids": families_upgraded,
        "semantic_authority_promotions": 0,
        "qualification_promotions": 0,
        "completion_claim": False,
        "status": "EXACT_EVIDENCE_OVERLAY_ACTIVE_REMAINING_WEAK_CLAIMS_EXPLICIT",
    }
    SUMMARY.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(summary, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
