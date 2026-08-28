#!/usr/bin/env python3
"""Fail-closed validation for the B04 exact-evidence overlay."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlparse

HERE = Path(__file__).resolve().parent
BUILDER = HERE / "build_effective_evidence_governance.py"
BASE = HERE / "organization-family-membership-claims.jsonl"
UPGRADES = HERE / "organization-family-evidence-upgrades.jsonl"
OUTPUT = HERE / "effective-organization-family-membership-claims.jsonl"
SUMMARY = HERE / "effective-evidence-governance-summary.json"


def load_jsonl(path: Path) -> list[dict]:
    if not path.is_file():
        raise AssertionError(f"missing artifact: {path.name}")
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def validate() -> dict:
    before = {p: p.read_bytes() for p in (OUTPUT, SUMMARY) if p.is_file()}
    if len(before) != 2:
        raise AssertionError("effective evidence artifacts are missing")
    base = load_jsonl(BASE)
    upgrades = load_jsonl(UPGRADES)
    effective = load_jsonl(OUTPUT)
    summary = json.loads(SUMMARY.read_text(encoding="utf-8"))

    if len(base) != 1012:
        raise AssertionError(f"unexpected base membership population: {len(base)}")
    if len(effective) != len(base):
        raise AssertionError("effective overlay changed membership population")
    if len({r['claim_id'] for r in effective}) != len(effective):
        raise AssertionError("effective claim ids are duplicated")
    base_by_id = {r["claim_id"]: r for r in base}
    effective_by_id = {r["claim_id"]: r for r in effective}

    for upgrade in upgrades:
        claim = effective_by_id.get(upgrade["claim_id"])
        if claim is None:
            raise AssertionError(f"upgrade missing from effective claims: {upgrade['upgrade_id']}")
        if claim["organization_id"] != upgrade["organization_id"] or claim["family_id"] != upgrade["family_id"]:
            raise AssertionError(f"upgrade scope drift: {upgrade['upgrade_id']}")
        if claim.get("upgrade_id") != upgrade["upgrade_id"]:
            raise AssertionError(f"upgrade identity drift: {upgrade['upgrade_id']}")
        if claim.get("evidence_strength") != "STRONG_EXACT_OFFICIAL_PRODUCT_DOCUMENTATION":
            raise AssertionError(f"upgrade not strong-exact: {upgrade['upgrade_id']}")
        parsed = urlparse(claim["evidence_locator"])
        if parsed.scheme != "https" or not parsed.netloc or not (parsed.path or "/").strip("/"):
            raise AssertionError(f"upgrade locator is not exact: {upgrade['upgrade_id']}")
        if not claim.get("product_id") or not claim.get("product_name"):
            raise AssertionError(f"upgrade lacks exact product identity: {upgrade['upgrade_id']}")
        for forbidden in ("semantic_authority", "qualification_claim", "completion_claim"):
            if claim.get(forbidden) is not False:
                raise AssertionError(f"upgrade illegally promotes {forbidden}: {upgrade['upgrade_id']}")

    upgraded_ids = {r["claim_id"] for r in upgrades}
    for cid, row in effective_by_id.items():
        if cid in upgraded_ids:
            continue
        original = base_by_id[cid]
        for field in (
            "evidence_locator",
            "evidence_locator_kind",
            "evidence_strength",
            "status",
            "claim",
        ):
            if row.get(field) != original.get(field):
                raise AssertionError(f"non-upgraded claim changed field {field}: {cid}")

    strong = sum(
        r.get("evidence_strength") == "STRONG_EXACT_OFFICIAL_PRODUCT_DOCUMENTATION"
        for r in effective
    )
    if summary.get("strong_exact_product_membership_claim_count") != strong:
        raise AssertionError("strong evidence summary drift")
    if summary.get("remaining_weak_membership_claim_count") != len(effective) - strong:
        raise AssertionError("remaining weak evidence summary drift")
    if summary.get("semantic_authority_promotions") != 0 or summary.get("qualification_promotions") != 0:
        raise AssertionError("effective summary illegally promotes authority or qualification")
    if summary.get("completion_claim") is not False:
        raise AssertionError("effective evidence summary claims completion")

    result = subprocess.run([sys.executable, str(BUILDER)], cwd=HERE.parents[2], capture_output=True, text=True)
    if result.returncode != 0:
        raise AssertionError(result.stdout + result.stderr)
    after = {p: p.read_bytes() for p in (OUTPUT, SUMMARY)}
    if before != after:
        raise AssertionError("effective evidence artifacts are stale or nondeterministic")
    return {
        "claim_count": len(effective),
        "upgrade_count": len(upgrades),
        "strong_exact_count": strong,
        "remaining_weak_count": len(effective) - strong,
        "status": "VALID",
        "completion_claim": False,
    }


def main() -> int:
    try:
        print(json.dumps(validate(), sort_keys=True))
    except Exception as exc:
        print(f"FAIL effective_evidence_governance: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
