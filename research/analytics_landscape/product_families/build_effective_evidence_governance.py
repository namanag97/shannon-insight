#!/usr/bin/env python3
"""Build sparse effective B04 evidence dispositions over immutable weak base claims."""

from __future__ import annotations

import json
from pathlib import Path
from urllib.parse import urlparse

HERE = Path(__file__).resolve().parent
BASE = HERE / "organization-family-membership-claims.jsonl"
UPGRADE_GLOB = "organization-family-evidence-upgrades*.jsonl"
DISCOVERY_GLOB = "organization-family-evidence-discoveries*.jsonl"
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
DISC_REQ = (REQ - {"upgrade_id"}) | {"discovery_id"}


def load_jsonl(path: Path) -> list[dict]:
    return [
        json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()
    ]


def is_homepage(url: str) -> bool:
    return not (urlparse(url).path or "/").strip("/")


def validate_evidence_record(record: dict, record_id: str) -> None:
    parsed = urlparse(record["official_locator"])
    if parsed.scheme != "https" or not parsed.netloc or is_homepage(record["official_locator"]):
        raise SystemExit(f"non-exact locator: {record_id}")
    if (
        record["evidence_role"] != "product_boundary_evidence"
        or record["evidence_strength"] != "STRONG_EXACT_OFFICIAL_PRODUCT_DOCUMENTATION"
    ):
        raise SystemExit(f"invalid evidence posture: {record_id}")
    for key in ("semantic_authority", "qualification_claim", "completion_claim"):
        if record.get(key) is not False:
            raise SystemExit(f"illegal promotion {key}: {record_id}")


def main() -> int:
    base = load_jsonl(BASE)
    upgrade_paths = sorted(HERE.glob(UPGRADE_GLOB), key=lambda path: path.name)
    if not upgrade_paths:
        raise SystemExit(f"no exact-evidence overlay shards match {UPGRADE_GLOB}")
    upgrades = [row for path in upgrade_paths for row in load_jsonl(path)]
    discovery_paths = sorted(HERE.glob(DISCOVERY_GLOB), key=lambda path: path.name)
    if not discovery_paths:
        raise SystemExit(f"no strong-discovery shards match {DISCOVERY_GLOB}")
    discoveries = [row for path in discovery_paths for row in load_jsonl(path)]
    by_claim = {row["claim_id"]: row for row in base}
    if len(by_claim) != len(base):
        raise SystemExit("duplicate base claims")

    seen_upgrade_ids: set[str] = set()
    seen_claim_ids: set[str] = set()
    output: list[dict] = []
    for upgrade in upgrades:
        missing = REQ - upgrade.keys()
        if missing:
            raise SystemExit(f"{upgrade.get('upgrade_id')}: missing {sorted(missing)}")
        if upgrade["upgrade_id"] in seen_upgrade_ids or upgrade["claim_id"] in seen_claim_ids:
            raise SystemExit("duplicate upgrade or claim target")
        base_claim = by_claim.get(upgrade["claim_id"])
        if not base_claim:
            raise SystemExit(f"unknown base claim: {upgrade['claim_id']}")
        if (upgrade["organization_id"], upgrade["family_id"]) != (
            base_claim["organization_id"],
            base_claim["family_id"],
        ):
            raise SystemExit(f"scope drift: {upgrade['upgrade_id']}")
        validate_evidence_record(upgrade, upgrade["upgrade_id"])
        seen_upgrade_ids.add(upgrade["upgrade_id"])
        seen_claim_ids.add(upgrade["claim_id"])
        output.append(
            {
                **upgrade,
                "disposition_kind": "BASE_CLAIM_UPGRADE",
                "base_evidence_locator": base_claim["evidence_locator"],
                "base_evidence_strength": base_claim["evidence_strength"],
                "effective_status": "BOUND_STRONG_EXACT_PRODUCT_EVIDENCE_AUTHORITY_WITHHELD",
            }
        )

    seen_discovery_ids: set[str] = set()
    base_scopes = {(row["organization_id"], row["family_id"]) for row in base}
    for discovery in discoveries:
        missing = DISC_REQ - discovery.keys()
        if missing:
            raise SystemExit(f"{discovery.get('discovery_id')}: missing {sorted(missing)}")
        if (
            discovery["claim_id"] in seen_claim_ids
            or discovery["discovery_id"] in seen_discovery_ids
        ):
            raise SystemExit("duplicate discovery or claim target")
        if (discovery["organization_id"], discovery["family_id"]) in base_scopes:
            raise SystemExit(f"discovery shadows base scope: {discovery['discovery_id']}")
        validate_evidence_record(discovery, discovery["discovery_id"])
        seen_discovery_ids.add(discovery["discovery_id"])
        seen_claim_ids.add(discovery["claim_id"])
        output.append(
            {
                **discovery,
                "disposition_kind": "STRONG_EVIDENCE_DISCOVERY",
                "base_evidence_locator": None,
                "base_evidence_strength": None,
                "effective_status": "BOUND_STRONG_EXACT_PRODUCT_EVIDENCE_DISCOVERY_AUTHORITY_WITHHELD",
            }
        )

    output.sort(key=lambda row: row["claim_id"])
    OUTPUT.write_text(
        "".join(json.dumps(row, sort_keys=True) + "\n" for row in output), encoding="utf-8"
    )
    organizations = sorted({row["organization_id"] for row in output})
    families = sorted({row["family_id"] for row in output})
    summary = {
        "report_id": "effective_horizontal_evidence_governance",
        "as_of": "2026-08-28",
        "base_membership_claim_count": len(base),
        "effective_membership_claim_count": len(base) + len(discoveries),
        "exact_evidence_upgrade_count": len(upgrades),
        "discovered_strong_membership_claim_count": len(discoveries),
        "strong_exact_product_membership_claim_count": len(output),
        "remaining_weak_membership_claim_count": len(base) - len(upgrades),
        "organization_count_with_exact_upgrade": len(organizations),
        "family_count_with_exact_upgrade": len(families),
        "upgraded_organization_ids": organizations,
        "upgraded_family_ids": families,
        "semantic_authority_promotions": 0,
        "qualification_promotions": 0,
        "completion_claim": False,
        "status": "EXACT_EVIDENCE_OVERLAY_AND_DISCOVERY_ACTIVE_REMAINING_WEAK_CLAIMS_EXPLICIT",
    }
    SUMMARY.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(summary, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
