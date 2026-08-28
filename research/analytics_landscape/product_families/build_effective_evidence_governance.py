#!/usr/bin/env python3
"""Build sparse effective B04 evidence dispositions over immutable weak base claims."""

from __future__ import annotations

import json
from pathlib import Path
from urllib.parse import urlparse

HERE = Path(__file__).resolve().parent
BASE = HERE / "organization-family-membership-claims.jsonl"
UPGRADE_PATTERN = "organization-family-evidence-upgrades*.jsonl"
OUTPUT = HERE / "effective-evidence-upgrade-dispositions.jsonl"
SUMMARY = HERE / "effective-evidence-governance-summary.json"
REQUIRED_FIELDS = {
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


def load_upgrade_shards() -> tuple[list[dict], list[str]]:
    paths = sorted(HERE.glob(UPGRADE_PATTERN), key=lambda path: path.name)
    if not paths:
        raise SystemExit(f"no evidence-upgrade inputs match {UPGRADE_PATTERN}")
    rows: list[dict] = []
    for path in paths:
        rows.extend(load_jsonl(path))
    return rows, [path.name for path in paths]


def is_homepage(url: str) -> bool:
    return not (urlparse(url).path or "/").strip("/")


def main() -> int:
    base = load_jsonl(BASE)
    upgrades, upgrade_files = load_upgrade_shards()
    claims_by_id = {row["claim_id"]: row for row in base}
    if len(claims_by_id) != len(base):
        raise SystemExit("duplicate base claims")

    seen_upgrade_ids: set[str] = set()
    seen_claim_ids: set[str] = set()
    output_rows: list[dict] = []
    for upgrade in upgrades:
        missing = REQUIRED_FIELDS - upgrade.keys()
        if missing:
            raise SystemExit(
                f"{upgrade.get('upgrade_id')}: missing {sorted(missing)}"
            )
        if (
            upgrade["upgrade_id"] in seen_upgrade_ids
            or upgrade["claim_id"] in seen_claim_ids
        ):
            raise SystemExit("duplicate upgrade or claim target")

        base_claim = claims_by_id.get(upgrade["claim_id"])
        if not base_claim:
            raise SystemExit(f"unknown base claim: {upgrade['claim_id']}")
        if (upgrade["organization_id"], upgrade["family_id"]) != (
            base_claim["organization_id"],
            base_claim["family_id"],
        ):
            raise SystemExit(f"scope drift: {upgrade['upgrade_id']}")

        locator = urlparse(upgrade["official_locator"])
        if (
            locator.scheme != "https"
            or not locator.netloc
            or is_homepage(upgrade["official_locator"])
        ):
            raise SystemExit(f"non-exact locator: {upgrade['upgrade_id']}")
        if (
            upgrade["evidence_role"] != "product_boundary_evidence"
            or upgrade["evidence_strength"]
            != "STRONG_EXACT_OFFICIAL_PRODUCT_DOCUMENTATION"
        ):
            raise SystemExit(f"invalid evidence posture: {upgrade['upgrade_id']}")
        for field in (
            "semantic_authority",
            "qualification_claim",
            "completion_claim",
        ):
            if upgrade.get(field) is not False:
                raise SystemExit(
                    f"illegal promotion {field}: {upgrade['upgrade_id']}"
                )

        seen_upgrade_ids.add(upgrade["upgrade_id"])
        seen_claim_ids.add(upgrade["claim_id"])
        output_rows.append(
            {
                **upgrade,
                "base_evidence_locator": base_claim["evidence_locator"],
                "base_evidence_strength": base_claim["evidence_strength"],
                "effective_status": (
                    "BOUND_STRONG_EXACT_PRODUCT_EVIDENCE_AUTHORITY_WITHHELD"
                ),
            }
        )

    output_rows.sort(key=lambda row: row["claim_id"])
    OUTPUT.write_text(
        "".join(json.dumps(row, sort_keys=True) + "\n" for row in output_rows),
        encoding="utf-8",
    )
    organization_ids = sorted({row["organization_id"] for row in output_rows})
    family_ids = sorted({row["family_id"] for row in output_rows})
    summary = {
        "report_id": "effective_horizontal_evidence_governance",
        "as_of": "2026-08-28",
        "base_membership_claim_count": len(base),
        "upgrade_input_file_count": len(upgrade_files),
        "upgrade_input_files": upgrade_files,
        "exact_evidence_upgrade_count": len(output_rows),
        "strong_exact_product_membership_claim_count": len(output_rows),
        "remaining_weak_membership_claim_count": len(base) - len(output_rows),
        "organization_count_with_exact_upgrade": len(organization_ids),
        "family_count_with_exact_upgrade": len(family_ids),
        "upgraded_organization_ids": organization_ids,
        "upgraded_family_ids": family_ids,
        "semantic_authority_promotions": 0,
        "qualification_promotions": 0,
        "completion_claim": False,
        "status": (
            "EXACT_EVIDENCE_OVERLAY_ACTIVE_REMAINING_WEAK_CLAIMS_EXPLICIT"
        ),
    }
    SUMMARY.write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(summary, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
