#!/usr/bin/env python3
"""Fail-closed validation for sparse B04 exact-evidence dispositions."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlparse

HERE = Path(__file__).resolve().parent
BUILDER = HERE / "build_effective_evidence_governance.py"
BASE = HERE / "organization-family-membership-claims.jsonl"
UPGRADE_GLOB = "organization-family-evidence-upgrades*.jsonl"
DISCOVERY_GLOB = "organization-family-evidence-discoveries*.jsonl"
OUTPUT = HERE / "effective-evidence-upgrade-dispositions.jsonl"
SUMMARY = HERE / "effective-evidence-governance-summary.json"


def load_jsonl(path: Path) -> list[dict]:
    return [
        json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()
    ]


def validate() -> dict:
    before = {path: path.read_bytes() for path in (OUTPUT, SUMMARY) if path.is_file()}
    if len(before) != 2:
        raise AssertionError("effective evidence artifacts missing")
    base = load_jsonl(BASE)
    upgrade_paths = sorted(HERE.glob(UPGRADE_GLOB), key=lambda path: path.name)
    if not upgrade_paths:
        raise AssertionError(f"no exact-evidence overlay shards match {UPGRADE_GLOB}")
    upgrades = [row for path in upgrade_paths for row in load_jsonl(path)]
    discovery_paths = sorted(HERE.glob(DISCOVERY_GLOB), key=lambda path: path.name)
    if not discovery_paths:
        raise AssertionError(f"no strong-discovery shards match {DISCOVERY_GLOB}")
    discoveries = [row for path in discovery_paths for row in load_jsonl(path)]
    output = load_jsonl(OUTPUT)
    summary = json.loads(SUMMARY.read_text(encoding="utf-8"))
    if len(base) != 1012:
        raise AssertionError(f"unexpected base population {len(base)}")
    if len(output) != len(upgrades) + len(discoveries):
        raise AssertionError("sparse disposition count drift")
    by_claim = {row["claim_id"]: row for row in base}
    base_scopes = {(row["organization_id"], row["family_id"]) for row in base}
    if len({row["claim_id"] for row in output}) != len(output):
        raise AssertionError("duplicate disposition claim")

    for row in output:
        base_claim = by_claim.get(row["claim_id"])
        if row["disposition_kind"] == "BASE_CLAIM_UPGRADE":
            if not base_claim or (row["organization_id"], row["family_id"]) != (
                base_claim["organization_id"],
                base_claim["family_id"],
            ):
                raise AssertionError(f"scope drift {row.get('upgrade_id')}")
            if (
                row.get("effective_status")
                != "BOUND_STRONG_EXACT_PRODUCT_EVIDENCE_AUTHORITY_WITHHELD"
            ):
                raise AssertionError(f"status drift {row.get('upgrade_id')}")
        elif row["disposition_kind"] == "STRONG_EVIDENCE_DISCOVERY":
            if base_claim or (row["organization_id"], row["family_id"]) in base_scopes:
                raise AssertionError(f"discovery shadows base {row.get('discovery_id')}")
            if (
                row.get("effective_status")
                != "BOUND_STRONG_EXACT_PRODUCT_EVIDENCE_DISCOVERY_AUTHORITY_WITHHELD"
            ):
                raise AssertionError(f"status drift {row.get('discovery_id')}")
        else:
            raise AssertionError(f"unknown disposition kind {row.get('disposition_kind')}")

        parsed = urlparse(row["official_locator"])
        record_id = row.get("upgrade_id", row.get("discovery_id"))
        if parsed.scheme != "https" or not parsed.netloc or not (parsed.path or "/").strip("/"):
            raise AssertionError(f"non-exact locator {record_id}")
        if row.get("evidence_strength") != "STRONG_EXACT_OFFICIAL_PRODUCT_DOCUMENTATION":
            raise AssertionError(f"strength drift {record_id}")
        for key in ("semantic_authority", "qualification_claim", "completion_claim"):
            if row.get(key) is not False:
                raise AssertionError(f"illegal {key} {record_id}")

    if (
        summary["strong_exact_product_membership_claim_count"] != len(output)
        or summary["exact_evidence_upgrade_count"] != len(upgrades)
        or summary["discovered_strong_membership_claim_count"] != len(discoveries)
        or summary["effective_membership_claim_count"] != len(base) + len(discoveries)
        or summary["remaining_weak_membership_claim_count"] != len(base) - len(upgrades)
    ):
        raise AssertionError("summary drift")
    if (
        summary.get("semantic_authority_promotions") != 0
        or summary.get("qualification_promotions") != 0
        or summary.get("completion_claim") is not False
    ):
        raise AssertionError("illegal summary promotion")

    run = subprocess.run(
        [sys.executable, str(BUILDER)], cwd=HERE, capture_output=True, text=True, check=False
    )
    if run.returncode:
        raise AssertionError(run.stdout + run.stderr)
    if before != {path: path.read_bytes() for path in (OUTPUT, SUMMARY)}:
        raise AssertionError("artifacts stale or nondeterministic")
    return {
        "base_claim_count": len(base),
        "upgrade_count": len(upgrades),
        "discovery_count": len(discoveries),
        "strong_exact_count": len(output),
        "remaining_weak_count": len(base) - len(upgrades),
        "status": "VALID",
        "completion_claim": False,
    }


def main() -> int:
    try:
        print(json.dumps(validate(), sort_keys=True))
        return 0
    except Exception as exc:
        print(f"FAIL effective_evidence_governance: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
