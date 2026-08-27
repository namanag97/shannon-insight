#!/usr/bin/env python3
"""Build controlled evidence-role and organization-membership claim projections.

The horizontal family corpus is open-world research evidence, not product authority. This builder
makes the evidence posture machine-readable without upgrading weak evidence. In particular, a
corporate homepage remains weak adoption evidence until an exact product/technical locator is
bound by a later research tranche.
"""
from __future__ import annotations

import json
import re
from collections import defaultdict
from pathlib import Path
from urllib.parse import urlparse

HERE = Path(__file__).resolve().parent

ROLES = {
    "foundational_theory",
    "algorithm",
    "architecture",
    "standard",
    "human_factors",
    "empirical_validation",
    "governance",
    "product_boundary_evidence",
}

THEORY_TAGS = {"statistics", "causal", "time", "risk", "semantics", "optimization", "simulation", "graph", "process"}
ALGORITHM_TAGS = {"ml", "predictive", "query", "optimization", "simulation", "forecast", "graph", "spatial", "search", "process"}
GOVERNANCE_TAGS = {"governance", "privacy", "trust", "security", "policy", "decision", "lineage"}
HUMAN_TAGS = {"human", "accessibility", "visualization", "interaction", "collaboration", "ux", "decision"}
EMPIRICAL_TAGS = {"experiment", "benchmark", "evaluation", "product", "quality", "forecast", "performance"}
ARCH_TAGS = {"architecture", "workflow", "olap", "query", "runtime", "stream", "lakehouse", "catalog", "lineage", "process"}


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def normalize_url(url: str) -> str:
    p = urlparse(url)
    path = re.sub(r"/+", "/", p.path or "/")
    return f"{p.scheme.lower()}://{p.netloc.lower()}{path}".rstrip("/") or "/"


def is_homepage(url: str) -> bool:
    p = urlparse(url)
    path = (p.path or "/").strip("/")
    return path == ""


def roles_for(ref: dict) -> tuple[list[str], list[str]]:
    kind = str(ref.get("kind", "")).casefold()
    tags = {str(x).casefold() for x in ref.get("tags", [])}
    roles: set[str] = set()
    basis: list[str] = []
    if kind == "standard":
        roles.add("standard"); basis.append("source kind is standard")
    if kind in {"peer_reviewed", "paper", "book"}:
        roles.add("foundational_theory"); basis.append("research publication/book supplies theory or method basis")
    if tags & ALGORITHM_TAGS and kind in {"peer_reviewed", "paper", "book"}:
        roles.add("algorithm"); basis.append("method/compute tags identify algorithmic or procedural evidence")
    if tags & ARCH_TAGS or (kind == "standard" and tags & {"workflow", "query", "process", "semantics"}):
        roles.add("architecture"); basis.append("architecture/system-structure tags or standard role")
    if tags & GOVERNANCE_TAGS:
        roles.add("governance"); basis.append("governance/privacy/trust/security/policy tags")
    if tags & HUMAN_TAGS:
        roles.add("human_factors"); basis.append("human/interaction/accessibility/decision tags")
    if tags & EMPIRICAL_TAGS and kind in {"peer_reviewed", "paper"}:
        roles.add("empirical_validation"); basis.append("empirical/evaluation/product/performance tags on research publication")
    # A technical product paper can support a product-boundary observation, but a generic theory
    # paper cannot. The separate organization membership ledger remains the primary adoption surface.
    if "product" in tags and kind in {"peer_reviewed", "paper"}:
        roles.add("product_boundary_evidence"); basis.append("product-tagged technical publication")
    if not roles:
        # Preserve total classification without inventing a strong role: a research publication is at
        # minimum theory evidence, while any other exact source is architecture evidence candidate.
        if kind in {"peer_reviewed", "paper", "book"}:
            roles.add("foundational_theory"); basis.append("fallback bounded to research publication theory role")
        else:
            roles.add("architecture"); basis.append("fallback bounded to technical/source architecture role")
    return sorted(roles), basis


def main() -> int:
    manifest = load(HERE / "manifest.json")
    families = []
    for shard_name in manifest["shards"]:
        families.extend(load(HERE / shard_name)["families"])

    unique_refs: dict[str, dict] = {}
    unique_orgs: dict[str, dict] = {}
    ref_families: dict[str, set[str]] = defaultdict(set)
    membership_rows: list[dict] = []

    for family in families:
        fid = family["id"]
        for ref in family["research"]:
            unique_refs.setdefault(ref["id"], ref)
            ref_families[ref["id"]].add(fid)
        for org in family["organizations"]:
            unique_orgs.setdefault(org["id"], org)
            homepage_only = is_homepage(org["url"])
            membership_rows.append({
                "claim_id": f"claim.membership.{fid}.{org['id']}",
                "record_kind": "organization_family_membership_claim",
                "family_id": fid,
                "organization_id": org["id"],
                "claim": f"{org['name']} is observed as an independently adopted organization relevant to research coverage coordinate {fid}; this does not establish semantic authority, exact product capability, implementation qualification, or product-boundary sovereignty.",
                "claim_scope": "adoption_or_market_boundary_evidence_only",
                "evidence_locator": org["url"],
                "evidence_locator_kind": "corporate_or_project_homepage" if homepage_only else "organization_web_locator",
                "evidence_strength": "WEAK_HOMEPAGE_ONLY" if homepage_only else "WEAK_ORGANIZATION_LOCATOR",
                "evidence_role": "product_boundary_evidence",
                "status": "BOUND_WEAK_EVIDENCE_REPLACEMENT_REQUIRED",
                "required_upgrade": [
                    "exact product or project identity",
                    "exact official product, architecture, technical documentation, specification, or release locator",
                    "bounded falsifiable capability/adoption claim",
                    "last_verified date and identity/acquisition/rename posture",
                ],
                "semantic_authority": False,
                "qualification_claim": False,
                "completion_claim": False,
            })

    role_rows = []
    for rid, ref in sorted(unique_refs.items()):
        roles, basis = roles_for(ref)
        role_rows.append({
            "record_kind": "research_reference_role_projection",
            "reference_id": rid,
            "title": ref["title"],
            "url": ref["url"],
            "source_kind": ref["kind"],
            "roles": roles,
            "decision_basis": basis,
            "family_refs": sorted(ref_families[rid]),
            "status": "CONTROLLED_ROLE_CANDIDATE",
            "semantic_authority": False,
            "completion_claim": False,
        })

    identity_rows = []
    for oid, org in sorted(unique_orgs.items()):
        identity_rows.append({
            "record_kind": "organization_identity_projection",
            "organization_id": oid,
            "canonical_name": org["name"],
            "canonical_url": normalize_url(org["url"]),
            "organization_kind": org["organization_kind"],
            "identity_status": "CANONICAL_WITHIN_CORPUS_RELATIONSHIPS_UNADJUDICATED",
            "parent_organization_ref": None,
            "acquisition_or_rename_refs": [],
            "product_refs": [],
            "foundation_or_project_relationship_refs": [],
            "remaining_identity_debt": [
                "authoritative parent/acquisition/rename history not yet normalized",
                "organization-to-product/project identities not yet enumerated",
            ],
            "completion_claim": False,
        })

    (HERE / "research-reference-role-projection.jsonl").write_text("".join(json.dumps(x, sort_keys=True) + "\n" for x in role_rows), encoding="utf-8")
    (HERE / "organization-family-membership-claims.jsonl").write_text("".join(json.dumps(x, sort_keys=True) + "\n" for x in sorted(membership_rows, key=lambda r: r["claim_id"])), encoding="utf-8")
    (HERE / "organization-identity-projection.jsonl").write_text("".join(json.dumps(x, sort_keys=True) + "\n" for x in identity_rows), encoding="utf-8")
    summary = {
        "report_id": "horizontal_evidence_governance_projection",
        "as_of": manifest["as_of"],
        "completion_claim": False,
        "controlled_evidence_roles": sorted(ROLES),
        "family_count": len(families),
        "unique_research_reference_count": len(role_rows),
        "research_references_with_controlled_roles": len(role_rows),
        "unique_organization_count": len(identity_rows),
        "organization_family_membership_claim_count": len(membership_rows),
        "strong_exact_product_membership_claim_count": 0,
        "weak_membership_claim_count": len(membership_rows),
        "identity_relationships_fully_adjudicated_count": 0,
        "status": "ROLES_ENFORCED_CLAIMS_BOUND_WEAK_EVIDENCE_AND_IDENTITY_RELATIONSHIPS_OPEN",
    }
    (HERE / "evidence-governance-summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(summary, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
