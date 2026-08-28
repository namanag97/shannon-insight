#!/usr/bin/env python3
"""Expand exact product-evidence packets into upgrades, discoveries and identity evidence."""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from urllib.parse import urlparse

HERE = Path(__file__).resolve().parent
PACKETS = HERE / "organization-product-evidence-packets.jsonl"
BASE = HERE / "organization-family-membership-claims.jsonl"
IDENTITIES = HERE / "organization-identity-projection.jsonl"
UPGRADES = HERE / "organization-family-evidence-upgrades.generated.jsonl"
DISCOVERIES = HERE / "organization-family-evidence-discoveries.jsonl"
PRODUCT_IDENTITIES = HERE / "organization-product-identity-evidence.jsonl"
SUMMARY = HERE / "product-evidence-packet-summary.json"


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.write_text("".join(json.dumps(row, sort_keys=True) + "\n" for row in rows), encoding="utf-8")


def exact_https_locator(value: str) -> bool:
    parsed = urlparse(value)
    return parsed.scheme == "https" and bool(parsed.netloc) and bool((parsed.path or "/").strip("/"))


def main() -> int:
    packets = load_jsonl(PACKETS)
    base = load_jsonl(BASE)
    identities = {row["organization_id"]: row for row in load_jsonl(IDENTITIES)}
    family_ids = set(json.loads((HERE / "manifest.json").read_text(encoding="utf-8"))["family_ids"])
    base_by_scope = {(row["organization_id"], row["family_id"]): row for row in base}
    if len(base_by_scope) != len(base):
        raise SystemExit("duplicate organization-family scope in base claims")

    packet_ids: set[str] = set()
    claim_scopes: set[tuple[str, str]] = set()
    upgrades: list[dict] = []
    discoveries: list[dict] = []
    products: dict[tuple[str, str], dict] = {}
    product_packets: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for packet in packets:
        packet_id = packet["packet_id"]
        if packet_id in packet_ids:
            raise SystemExit(f"duplicate product evidence packet: {packet_id}")
        packet_ids.add(packet_id)
        organization_id = packet["organization_id"]
        if organization_id not in identities:
            raise SystemExit(f"unknown organization: {packet_id}")
        if not exact_https_locator(packet["official_locator"]):
            raise SystemExit(f"non-exact official locator: {packet_id}")
        if (
            packet.get("evidence_role") != "product_boundary_evidence"
            or packet.get("evidence_strength") != "STRONG_EXACT_OFFICIAL_PRODUCT_DOCUMENTATION"
        ):
            raise SystemExit(f"invalid evidence posture: {packet_id}")
        for prohibited in ("semantic_authority", "qualification_claim", "completion_claim"):
            if packet.get(prohibited) is not False:
                raise SystemExit(f"illegal promotion {prohibited}: {packet_id}")
        if not packet.get("family_claims"):
            raise SystemExit(f"packet has no bounded family claims: {packet_id}")

        product_key = (organization_id, packet["product_id"])
        definition = {
            "organization_id": organization_id,
            "product_id": packet["product_id"],
            "product_name": packet["product_name"],
        }
        if product_key in products and products[product_key] != definition:
            raise SystemExit(f"conflicting product identity: {packet['product_id']}")
        products[product_key] = definition
        product_packets[product_key].append(packet)

        for family_claim in packet["family_claims"]:
            family_id = family_claim["family_id"]
            scope = (organization_id, family_id)
            if family_id not in family_ids:
                raise SystemExit(f"unknown family {family_id}: {packet_id}")
            if scope in claim_scopes:
                raise SystemExit(f"duplicate packet claim scope: {scope}")
            claim_scopes.add(scope)
            common = {
                "organization_id": organization_id,
                "family_id": family_id,
                "product_id": packet["product_id"],
                "product_name": packet["product_name"],
                "official_locator": packet["official_locator"],
                "bounded_claim": family_claim["bounded_claim"],
                "evidence_role": packet["evidence_role"],
                "evidence_strength": packet["evidence_strength"],
                "verified_on": packet["verified_on"],
                "organization_product_relationship": packet["organization_product_relationship"],
                "identity_posture": packet["identity_posture"],
                "acquisition_or_rename_posture": packet["acquisition_or_rename_posture"],
                "packet_ref": packet_id,
                "semantic_authority": False,
                "qualification_claim": False,
                "completion_claim": False,
            }
            base_claim = base_by_scope.get(scope)
            if base_claim:
                upgrades.append(
                    {
                        **common,
                        "upgrade_id": f"evidence-upgrade.packet.{organization_id}.{family_id}",
                        "claim_id": base_claim["claim_id"],
                    }
                )
            else:
                discoveries.append(
                    {
                        **common,
                        "record_kind": "strong_organization_family_membership_discovery",
                        "discovery_id": f"evidence-discovery.{organization_id}.{family_id}",
                        "claim_id": f"claim.discovery.{family_id}.{organization_id}",
                        "discovery_posture": "NEW_STRONG_EXACT_MEMBERSHIP_OUTSIDE_WEAK_SEED",
                    }
                )

    identity_rows = []
    for key, definition in sorted(products.items()):
        rows = product_packets[key]
        identity_rows.append(
            {
                **definition,
                "record_kind": "organization_product_identity_evidence",
                "packet_refs": sorted(row["packet_id"] for row in rows),
                "official_locators": sorted({row["official_locator"] for row in rows}),
                "organization_product_relationships": sorted(
                    {row["organization_product_relationship"] for row in rows}
                ),
                "identity_postures": sorted({row["identity_posture"] for row in rows}),
                "acquisition_or_rename_postures": sorted(
                    {row["acquisition_or_rename_posture"] for row in rows}
                ),
                "status": "EXACT_CURRENT_PRODUCT_RELATIONSHIP_EVIDENCE_PARTIAL_HISTORY",
                "semantic_authority": False,
                "qualification_claim": False,
                "completion_claim": False,
            }
        )

    upgrades.sort(key=lambda row: row["claim_id"])
    discoveries.sort(key=lambda row: row["claim_id"])
    write_jsonl(UPGRADES, upgrades)
    write_jsonl(DISCOVERIES, discoveries)
    write_jsonl(PRODUCT_IDENTITIES, identity_rows)
    summary = {
        "report_id": "organization_product_evidence_packet_projection",
        "as_of": "2026-08-28",
        "packet_count": len(packets),
        "organization_count": len({row["organization_id"] for row in packets}),
        "product_count": len(products),
        "bounded_family_claim_count": len(claim_scopes),
        "base_claim_upgrade_count": len(upgrades),
        "new_strong_membership_discovery_count": len(discoveries),
        "product_identity_evidence_count": len(identity_rows),
        "semantic_authority_promotions": 0,
        "qualification_promotions": 0,
        "completion_claim": False,
        "status": "EXACT_PRODUCT_PACKETS_EXPANDED_AUTHORITY_AND_QUALIFICATION_WITHHELD",
    }
    SUMMARY.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(summary, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
