#!/usr/bin/env python3
"""Fail-closed deterministic validation for reusable product-evidence packets."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlparse

HERE = Path(__file__).resolve().parent
BUILDER = HERE / "build_product_evidence_packets.py"
OUTPUTS = (
    HERE / "organization-family-evidence-upgrades.generated.jsonl",
    HERE / "organization-family-evidence-discoveries.jsonl",
    HERE / "organization-product-identity-evidence.jsonl",
    HERE / "product-evidence-packet-summary.json",
)


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def main() -> int:
    before = {path: path.read_bytes() for path in OUTPUTS}
    upgrades, discoveries, identities = (load_jsonl(path) for path in OUTPUTS[:3])
    summary = json.loads(OUTPUTS[3].read_text(encoding="utf-8"))
    base_scopes = {
        (row["organization_id"], row["family_id"])
        for row in load_jsonl(HERE / "organization-family-membership-claims.jsonl")
    }
    upgrade_scopes = {(row["organization_id"], row["family_id"]) for row in upgrades}
    discovery_scopes = {(row["organization_id"], row["family_id"]) for row in discoveries}
    assert len(upgrade_scopes) == len(upgrades)
    assert len(discovery_scopes) == len(discoveries)
    assert not upgrade_scopes & discovery_scopes
    assert upgrade_scopes <= base_scopes
    assert not discovery_scopes & base_scopes
    for row in upgrades + discoveries:
        parsed = urlparse(row["official_locator"])
        assert parsed.scheme == "https" and parsed.netloc and (parsed.path or "/").strip("/")
        assert row["evidence_strength"] == "STRONG_EXACT_OFFICIAL_PRODUCT_DOCUMENTATION"
        assert row["bounded_claim"] and row["packet_ref"]
        assert row["semantic_authority"] is row["qualification_claim"] is row["completion_claim"] is False
    assert len({row["product_id"] for row in identities}) == len(identities)
    assert all(row["packet_refs"] and row["official_locators"] for row in identities)
    assert all(
        row["semantic_authority"] is row["qualification_claim"] is row["completion_claim"] is False
        for row in identities
    )
    assert summary["base_claim_upgrade_count"] == len(upgrades)
    assert summary["new_strong_membership_discovery_count"] == len(discoveries)
    assert summary["product_identity_evidence_count"] == len(identities)
    assert summary["bounded_family_claim_count"] == len(upgrades) + len(discoveries)
    assert summary["semantic_authority_promotions"] == summary["qualification_promotions"] == 0
    assert summary["completion_claim"] is False

    result = subprocess.run([sys.executable, str(BUILDER)], cwd=HERE, capture_output=True, text=True)
    assert result.returncode == 0, result.stdout + result.stderr
    assert before == {path: path.read_bytes() for path in OUTPUTS}, "packet outputs are stale"
    print(
        "PASS product evidence packets: "
        f"{summary['packet_count']} packets / {summary['product_count']} products -> "
        f"{len(upgrades)} base upgrades + {len(discoveries)} strong discoveries; "
        "authority, qualification and complete identity history withheld"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
