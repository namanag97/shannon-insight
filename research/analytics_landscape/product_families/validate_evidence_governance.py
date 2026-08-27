#!/usr/bin/env python3
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from urllib.parse import urlparse

HERE = Path(__file__).resolve().parent
ALLOWED_ROLES = {
    "foundational_theory", "algorithm", "architecture", "standard",
    "human_factors", "empirical_validation", "governance", "product_boundary_evidence",
}


def load_jsonl(path: Path):
    return [json.loads(x) for x in path.read_text(encoding="utf-8").splitlines() if x.strip()]


def main() -> int:
    errors: list[str] = []
    manifest = json.loads((HERE / "manifest.json").read_text(encoding="utf-8"))
    families = []
    for shard_name in manifest["shards"]:
        families.extend(json.loads((HERE / shard_name).read_text(encoding="utf-8"))["families"])
    refs = {r["id"]: r for f in families for r in f["research"]}
    orgs = {o["id"]: o for f in families for o in f["organizations"]}
    memberships_expected = {(f["id"], o["id"]) for f in families for o in f["organizations"]}

    roles = load_jsonl(HERE / "research-reference-role-projection.jsonl")
    memberships = load_jsonl(HERE / "organization-family-membership-claims.jsonl")
    identities = load_jsonl(HERE / "organization-identity-projection.jsonl")
    summary = json.loads((HERE / "evidence-governance-summary.json").read_text(encoding="utf-8"))

    if {r["reference_id"] for r in roles} != set(refs): errors.append("role projection must cover every unique research ref exactly once")
    if len(roles) != len({r["reference_id"] for r in roles}): errors.append("duplicate role projection")
    for row in roles:
        if not row["roles"] or not set(row["roles"]) <= ALLOWED_ROLES: errors.append(f"bad controlled role {row['reference_id']}")
        if not row["decision_basis"]: errors.append(f"missing role basis {row['reference_id']}")
        if row["semantic_authority"] or row["completion_claim"]: errors.append(f"unsupported authority/completion {row['reference_id']}")
        if not urlparse(row["url"]).scheme: errors.append(f"bad ref URL {row['reference_id']}")

    got_memberships = {(r["family_id"], r["organization_id"]) for r in memberships}
    if got_memberships != memberships_expected or len(memberships) != len(memberships_expected): errors.append("membership ledger must exactly cover all family-organization occurrences")
    for row in memberships:
        if row["organization_id"] not in orgs: errors.append(f"unknown organization {row['organization_id']}")
        if row["evidence_role"] != "product_boundary_evidence": errors.append(f"membership role drift {row['claim_id']}")
        if row["evidence_strength"] not in {"WEAK_HOMEPAGE_ONLY", "WEAK_ORGANIZATION_LOCATOR"}: errors.append(f"unsupported evidence strength {row['claim_id']}")
        if not row["required_upgrade"]: errors.append(f"missing upgrade debt {row['claim_id']}")
        if row["semantic_authority"] or row["qualification_claim"] or row["completion_claim"]: errors.append(f"membership overclaim {row['claim_id']}")

    if {r["organization_id"] for r in identities} != set(orgs) or len(identities) != len(orgs): errors.append("identity projection must cover every unique organization")
    for row in identities:
        if row["identity_status"] != "CANONICAL_WITHIN_CORPUS_RELATIONSHIPS_UNADJUDICATED": errors.append(f"identity state drift {row['organization_id']}")
        if row["completion_claim"]: errors.append(f"identity completion overclaim {row['organization_id']}")
        if not row["remaining_identity_debt"]: errors.append(f"identity debt missing {row['organization_id']}")

    expected = {
        "family_count": len(families),
        "unique_research_reference_count": len(refs),
        "unique_organization_count": len(orgs),
        "organization_family_membership_claim_count": len(memberships_expected),
    }
    for key, value in expected.items():
        if summary.get(key) != value: errors.append(f"summary drift {key}: {summary.get(key)} != {value}")
    if summary.get("strong_exact_product_membership_claim_count") != 0: errors.append("strong membership evidence fabricated")
    if summary.get("completion_claim"): errors.append("B04 completion fabricated")
    if set(summary.get("controlled_evidence_roles", [])) != ALLOWED_ROLES: errors.append("controlled role vocabulary drift")

    if errors:
        for e in errors: print("ERROR: " + e)
        return 1
    print(f"PASS horizontal evidence governance: {len(families)} families; {len(refs)} refs role-classified; {len(orgs)} organizations identity-projected; {len(memberships)} memberships claim-bound; all memberships remain weak evidence")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
