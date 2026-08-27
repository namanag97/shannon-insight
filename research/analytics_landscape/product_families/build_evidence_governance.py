#!/usr/bin/env python3
"""Build claim-level horizontal evidence-governance projections.

The source corpus is open-world research evidence. This builder exposes identity, locator,
role and gate debt without upgrading a homepage or heuristic classification into authority.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import tempfile
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable, Sequence
from urllib.parse import urlparse

HERE = Path(__file__).resolve().parent
POLICY_PATH = HERE / "evidence-governance-policy.json"
OUTPUT_FILES = (
    "research-reference-role-projection.jsonl",
    "research-reference-family-claims.jsonl",
    "organization-family-membership-claims.jsonl",
    "organization-identity-projection.jsonl",
    "organization-identity-gaps.jsonl",
    "evidence-governance-frontier.jsonl",
    "evidence-governance-summary.json",
)

THEORY_KINDS = {
    "book",
    "conference_paper",
    "journal_article",
    "paper",
    "peer_reviewed",
    "research_paper",
}
IMPLEMENTATION_KINDS = {
    "documentation",
    "official_documentation",
    "project_documentation",
    "technical_documentation",
}
ARCHITECTURE_KINDS = {"industry_paper", "technical_report", "whitepaper"}
THEORY_TAGS = {
    "causal",
    "graph",
    "optimization",
    "process",
    "risk",
    "semantics",
    "simulation",
    "statistics",
    "time",
}
ALGORITHM_TAGS = {
    "algorithm",
    "causal",
    "forecast",
    "graph",
    "machine_learning",
    "ml",
    "optimization",
    "predictive",
    "process",
    "query",
    "search",
    "simulation",
    "spatial",
    "statistics",
}
ARCHITECTURE_TAGS = {
    "architecture",
    "catalog",
    "data_product",
    "dataflow",
    "lakehouse",
    "lineage",
    "olap",
    "ontology",
    "orchestration",
    "process",
    "query",
    "runtime",
    "semantics",
    "stream",
    "workflow",
}
GOVERNANCE_TAGS = {
    "assurance",
    "audit",
    "compliance",
    "decision",
    "governance",
    "lineage",
    "policy",
    "privacy",
    "provenance",
    "risk",
    "security",
    "trust",
}
HUMAN_TAGS = {
    "accessibility",
    "collaboration",
    "decision",
    "explanation",
    "human",
    "human_factors",
    "interaction",
    "narrative",
    "notification",
    "reporting",
    "ux",
    "visualization",
    "workflow",
}
EMPIRICAL_TAGS = {
    "benchmark",
    "evaluation",
    "experiment",
    "human_factors",
    "performance",
    "quality",
    "validation",
}


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True)


def write_json(path: Path, value: Any) -> None:
    path.write_text(canonical_json(value) + "\n", encoding="utf-8")


def write_jsonl(path: Path, rows: Iterable[dict[str, Any]]) -> None:
    path.write_text(
        "".join(canonical_json(row) + "\n" for row in rows),
        encoding="utf-8",
    )


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def normalize_url(url: str) -> str:
    parsed = urlparse(url)
    path = re.sub(r"/+", "/", parsed.path or "/")
    normalized = f"{parsed.scheme.lower()}://{parsed.netloc.lower()}{path}"
    return normalized.rstrip("/") or "/"


def is_homepage(url: str) -> bool:
    parsed = urlparse(url)
    return (parsed.path or "/").strip("/") == "" and not parsed.query


def evidence_locator(url: str) -> dict[str, Any]:
    parsed = urlparse(url)
    if parsed.fragment:
        selector_kind = "uri_fragment"
        selector_value = parsed.fragment
        locator_state = "FRAGMENT_PRESENT_UNVERIFIED"
    elif parsed.netloc.casefold() == "doi.org" and parsed.path.strip("/"):
        selector_kind = "record_identifier"
        selector_value = parsed.path.strip("/")
        locator_state = "RESOURCE_IDENTIFIER_ONLY"
    else:
        selector_kind = None
        selector_value = None
        locator_state = "RESOURCE_ONLY_EXACT_SELECTOR_MISSING"
    return {
        "source_url": url,
        "selector_kind": selector_kind,
        "selector_value": selector_value,
        "source_state": None,
        "locator_state": locator_state,
        "exact_claim_support": False,
    }


def role_projection(ref: dict[str, Any]) -> tuple[list[str], str, list[str]]:
    kind = str(ref.get("kind", "")).casefold()
    tags = {str(tag).casefold() for tag in ref.get("tags", [])}
    roles: set[str] = set()
    basis: set[str] = set()

    if kind == "standard":
        roles.add("standard")
        basis.add("source kind is standard")
    if kind in THEORY_KINDS:
        roles.add("foundational_theory")
        basis.add("source kind is theory-capable research literature")
    if kind in IMPLEMENTATION_KINDS:
        roles.add("implementation_reference")
        basis.add("source kind is implementation documentation")
    if kind in ARCHITECTURE_KINDS or tags & ARCHITECTURE_TAGS:
        roles.add("architecture")
        basis.add("source metadata indicates architecture or system structure")
    if tags & ALGORITHM_TAGS and (kind in THEORY_KINDS or kind == "standard"):
        roles.add("algorithm")
        basis.add("source metadata indicates an analytical or computational method")
    if tags & THEORY_TAGS and kind in THEORY_KINDS:
        roles.add("foundational_theory")
        basis.add("source metadata indicates a theoretical or mathematical concern")
    if tags & EMPIRICAL_TAGS and kind in THEORY_KINDS:
        roles.add("empirical_validation")
        basis.add("source metadata explicitly indicates evaluation or validation")
    if tags & HUMAN_TAGS:
        roles.add("human_factors")
        basis.add("source metadata indicates human work or experience")
    if tags & GOVERNANCE_TAGS:
        roles.add("governance")
        basis.add("source metadata indicates governance, trust or assurance")
    if "product" in tags and kind in THEORY_KINDS | ARCHITECTURE_KINDS:
        roles.add("product_boundary_evidence")
        basis.add("product-tagged technical or research source may falsify a boundary")

    if not roles:
        return (
            ["unclassified_research_evidence"],
            "UNCLASSIFIED_EXPLICIT_DEBT",
            ["committed kind and tags do not support a narrower controlled role"],
        )
    return sorted(roles), "PROPOSED_UNRATIFIED", sorted(basis)


def load_corpus() -> tuple[dict[str, Any], list[dict[str, Any]], list[Path]]:
    manifest_path = HERE / "manifest.json"
    manifest = load(manifest_path)
    families: list[dict[str, Any]] = []
    source_paths = [manifest_path, POLICY_PATH]
    for shard_name in manifest["shards"]:
        path = HERE / shard_name
        families.extend(load(path)["families"])
        source_paths.append(path)
    if [family["id"] for family in families] != manifest["family_ids"]:
        raise ValueError("family order or identity differs from manifest")
    return manifest, families, source_paths


def definition_tuple(row: dict[str, Any], fields: Sequence[str]) -> tuple[Any, ...]:
    values: list[Any] = []
    for field in fields:
        value = row.get(field)
        values.append(tuple(value) if isinstance(value, list) else value)
    return tuple(values)


def build_records() -> dict[str, Any]:
    policy = load(POLICY_PATH)
    controlled_roles = {row["role_id"] for row in policy["evidence_roles"]}
    manifest, families, source_paths = load_corpus()

    unique_refs: dict[str, dict[str, Any]] = {}
    unique_orgs: dict[str, dict[str, Any]] = {}
    ref_families: dict[str, set[str]] = defaultdict(set)
    org_families: dict[str, set[str]] = defaultdict(set)
    research_occurrences: set[tuple[str, str]] = set()
    organization_occurrences: set[tuple[str, str]] = set()

    for family in families:
        family_id = family["id"]
        for ref in family["research"]:
            ref_id = ref["id"]
            if ref_id in unique_refs:
                previous = definition_tuple(
                    unique_refs[ref_id],
                    ("title", "url", "kind", "tags", "year"),
                )
                current = definition_tuple(ref, ("title", "url", "kind", "tags", "year"))
                if previous != current:
                    raise ValueError(f"conflicting research definition: {ref_id}")
            unique_refs[ref_id] = ref
            ref_families[ref_id].add(family_id)
            research_occurrences.add((family_id, ref_id))
        for org in family["organizations"]:
            org_id = org["id"]
            if org_id in unique_orgs:
                previous = definition_tuple(
                    unique_orgs[org_id],
                    ("name", "url", "organization_kind"),
                )
                current = definition_tuple(org, ("name", "url", "organization_kind"))
                if previous != current:
                    raise ValueError(f"conflicting organization definition: {org_id}")
            unique_orgs[org_id] = org
            org_families[org_id].add(family_id)
            organization_occurrences.add((family_id, org_id))

    role_rows: list[dict[str, Any]] = []
    roles_by_ref: dict[str, tuple[list[str], str, list[str]]] = {}
    for ref_id, ref in sorted(unique_refs.items()):
        roles, role_state, basis = role_projection(ref)
        if not set(roles) <= controlled_roles:
            raise ValueError(f"uncontrolled evidence role emitted for {ref_id}")
        roles_by_ref[ref_id] = (roles, role_state, basis)
        role_rows.append(
            {
                "record_kind": "research_reference_role_projection",
                "reference_id": ref_id,
                "title": ref["title"],
                "url": ref["url"],
                "source_kind": ref["kind"],
                "tags": ref["tags"],
                "year": ref.get("year"),
                "roles": roles,
                "role_state": role_state,
                "decision_basis": basis,
                "family_refs": sorted(ref_families[ref_id]),
                "evidence_locator": evidence_locator(ref["url"]),
                "semantic_authority": False,
                "completion_claim": False,
            }
        )

    research_claim_rows: list[dict[str, Any]] = []
    for family_id, ref_id in sorted(research_occurrences):
        ref = unique_refs[ref_id]
        roles, role_state, basis = roles_by_ref[ref_id]
        research_claim_rows.append(
            {
                "record_kind": "research_reference_family_claim",
                "claim_id": f"claim.research.{family_id}.{ref_id}",
                "family_id": family_id,
                "reference_id": ref_id,
                "claim": (
                    f"{ref['title']} is proposed evidence for horizontal research coverage "
                    f"coordinate {family_id}; relevance and role remain unratified."
                ),
                "claim_scope": "research_relevance_candidate_only",
                "role_assignment": {
                    "roles": roles,
                    "role_state": role_state,
                    "decision_basis": basis,
                },
                "evidence_locator": evidence_locator(ref["url"]),
                "claim_state": "PROPOSED_UNRATIFIED",
                "semantic_authority": False,
                "implementation_qualification": False,
                "executed_acceptance": False,
                "completion_claim": False,
            }
        )

    identity_rows: list[dict[str, Any]] = []
    identity_gap_rows: list[dict[str, Any]] = []
    for org_id, org in sorted(unique_orgs.items()):
        identity_rows.append(
            {
                "record_kind": "organization_identity_projection",
                "organization_id": org_id,
                "corpus_handle": f"entity:{org_id}",
                "canonical_name": org["name"],
                "canonical_name_scope": "corpus_source_label_only",
                "canonical_url": normalize_url(org["url"]),
                "organization_kind": org["organization_kind"],
                "source_declared_kind": org["organization_kind"],
                "canonical_entity_kind": "UNRESOLVED",
                "identity_status": "PROVISIONAL_INTERNAL_HANDLE",
                "authoritative_identifiers": [],
                "aliases": [org["name"]],
                "family_refs": sorted(org_families[org_id]),
                "parent_organization_ref": None,
                "acquisition_or_rename_refs": [],
                "product_refs": [],
                "foundation_or_project_relationship_refs": [],
                "semantic_authority": False,
                "completion_claim": False,
            }
        )
        identity_gap_rows.append(
            {
                "record_kind": "organization_identity_gap",
                "gap_id": f"identity-gap.{org_id}",
                "organization_id": org_id,
                "status": "OPEN_EXPLICIT_DEBT",
                "required_reviews": [
                    "canonical_entity_kind",
                    "authoritative_external_identifier_or_exact_identity_evidence",
                    "legal_name_brand_product_project_foundation_distinction",
                    "aliases_renames_and_predecessor_successor_history",
                    "parent_acquisition_merger_and_control_relationships",
                    "relationship_valid_time_and_evidence_locator",
                ],
                "inference_prohibitions": [
                    "name_similarity_does_not_prove_identity",
                    "shared_branding_does_not_prove_legal_entity_identity",
                    "homepage_does_not_prove_product_family_membership",
                    "acquisition_or_rename_is_not_inferred_without_claim_bound_evidence",
                ],
                "completion_claim": False,
            }
        )

    membership_rows: list[dict[str, Any]] = []
    for family_id, org_id in sorted(organization_occurrences):
        org = unique_orgs[org_id]
        homepage_only = is_homepage(org["url"])
        membership_rows.append(
            {
                "record_kind": "organization_family_membership_claim",
                "claim_id": f"claim.membership.{family_id}.{org_id}",
                "family_id": family_id,
                "organization_id": org_id,
                "claim": (
                    f"{org['name']} is a proposed candidate for adoption or market-boundary "
                    f"research relevant to horizontal coordinate {family_id}; the source does not "
                    "verify an exact product capability, adoption occurrence, semantic authority, "
                    "implementation qualification or product-boundary sovereignty."
                ),
                "claim_scope": "candidate_adoption_or_market_boundary_research_only",
                "evidence_locator": evidence_locator(org["url"]),
                "evidence_locator_url": org["url"],
                "evidence_locator_kind": (
                    "corporate_or_project_homepage"
                    if homepage_only
                    else "organization_web_resource"
                ),
                "evidence_strength": (
                    "WEAK_HOMEPAGE_ONLY"
                    if homepage_only
                    else "WEAK_ORGANIZATION_RESOURCE_ONLY"
                ),
                "evidence_role": "adoption_evidence",
                "role_state": "CONTROLLED_ADOPTION_ROLE",
                "status": "UNVERIFIED_EXPLICIT_DEBT",
                "required_upgrade": [
                    "exact product or project identity",
                    "exact official product, architecture, technical documentation, specification, or release locator",
                    "stable selector and recoverable source-state identifier",
                    "bounded falsifiable capability or adoption claim",
                    "last_verified date and identity/acquisition/rename posture",
                ],
                "semantic_authority": False,
                "qualification_claim": False,
                "implementation_qualification": False,
                "executed_acceptance": False,
                "completion_claim": False,
            }
        )

    exact_org_claims = sum(
        int(row["evidence_locator"]["exact_claim_support"])
        for row in membership_rows
    )
    exact_research_claims = sum(
        int(row["evidence_locator"]["exact_claim_support"])
        for row in research_claim_rows
    )
    unclassified_roles = sum(
        row["role_state"] == "UNCLASSIFIED_EXPLICIT_DEBT" for row in role_rows
    )
    frontier_rows = [
        {
            "requirement_id": "HR03_CANONICALIZE_ORGANIZATION_IDENTITY",
            "status": "PARTIAL_EXPLICIT_DEBT",
            "source_unique_entities": len(identity_rows),
            "authoritatively_resolved_entities": 0,
            "provisional_entities": len(identity_rows),
            "explicit_identity_gap_rows": len(identity_gap_rows),
            "inferred_relationships": 0,
            "exit_condition": (
                "Every entity has a canonical kind, authoritative identifier or exact identity "
                "evidence, aliases/history, and claim-bound valid-time relationships where applicable."
            ),
            "completion_claim": False,
        },
        {
            "requirement_id": "HR04_BIND_EVIDENCE_TO_CLAIMS",
            "status": "PARTIAL_EXPLICIT_DEBT",
            "organization_membership_claims": len(membership_rows),
            "research_membership_claims": len(research_claim_rows),
            "exact_organization_claim_bindings": exact_org_claims,
            "exact_research_claim_bindings": exact_research_claims,
            "open_claim_bindings": (
                len(membership_rows)
                + len(research_claim_rows)
                - exact_org_claims
                - exact_research_claims
            ),
            "exit_condition": (
                "Every membership claim has a stable selector and source-state binding that a "
                "validator can re-resolve to the asserted passage or record."
            ),
            "completion_claim": False,
        },
        {
            "requirement_id": "HR05_RESEARCH_REFERENCE_ROLES",
            "status": "PARTIAL_EXPLICIT_DEBT",
            "unique_research_sources": len(role_rows),
            "research_family_claims": len(research_claim_rows),
            "proposed_role_assignments": len(role_rows),
            "unclassified_role_sources": unclassified_roles,
            "ratified_role_assignments": 0,
            "exit_condition": (
                "Every source-family claim has a controlled, semantically ratified role checked "
                "against the bounded claim and family question."
            ),
            "completion_claim": False,
        },
    ]

    source_files = [
        {
            "path": path.relative_to(HERE).as_posix(),
            "sha256": sha256_file(path),
        }
        for path in source_paths
    ]
    summary = {
        "report_id": "horizontal_evidence_governance_projection",
        "schema_version": "2.0.0",
        "as_of": manifest["as_of"],
        "status": (
            "CLAIMS_AND_DEBT_PROJECTED_EXACT_EVIDENCE_IDENTITY_AND_RATIFICATION_OPEN"
        ),
        "source_files": source_files,
        "controlled_evidence_roles": sorted(controlled_roles),
        "family_count": len(families),
        "unique_research_reference_count": len(role_rows),
        "research_references_with_controlled_roles": len(role_rows) - unclassified_roles,
        "research_reference_family_claim_count": len(research_claim_rows),
        "unclassified_research_reference_count": unclassified_roles,
        "ratified_evidence_role_count": 0,
        "unique_organization_count": len(identity_rows),
        "organization_identity_gap_count": len(identity_gap_rows),
        "authoritatively_resolved_identity_count": 0,
        "organization_family_membership_claim_count": len(membership_rows),
        "weak_membership_claim_count": len(membership_rows) - exact_org_claims,
        "strong_exact_product_membership_claim_count": exact_org_claims,
        "exact_research_claim_binding_count": exact_research_claims,
        "exact_claim_binding_count": exact_org_claims + exact_research_claims,
        "identity_relationships_fully_adjudicated_count": 0,
        "semantic_ratification_count": 0,
        "implementation_qualification_count": 0,
        "executed_acceptance_count": 0,
        "frontier_requirement_ids": [row["requirement_id"] for row in frontier_rows],
        "non_completion_claims": [
            "generated projections expose source debt; they do not repair it",
            "candidate adoption evidence is not verified adoption or semantic authority",
            "proposed evidence roles are not ratified roles",
            "source URLs without verified selectors do not prove bounded claims",
            "no implementation qualification or executed vertical acceptance is asserted",
        ],
        "completion_claim": False,
    }
    return {
        "research-reference-role-projection.jsonl": role_rows,
        "research-reference-family-claims.jsonl": research_claim_rows,
        "organization-family-membership-claims.jsonl": membership_rows,
        "organization-identity-projection.jsonl": identity_rows,
        "organization-identity-gaps.jsonl": identity_gap_rows,
        "evidence-governance-frontier.jsonl": frontier_rows,
        "evidence-governance-summary.json": summary,
    }


def write_outputs(output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    records = build_records()
    for name in OUTPUT_FILES:
        path = output_dir / name
        if name.endswith(".jsonl"):
            write_jsonl(path, records[name])
        else:
            write_json(path, records[name])


def compare_outputs(expected: Path, actual: Path) -> list[str]:
    errors: list[str] = []
    for name in OUTPUT_FILES:
        expected_path = expected / name
        actual_path = actual / name
        if not expected_path.is_file():
            errors.append(f"committed generated output missing: {name}")
        elif expected_path.read_bytes() != actual_path.read_bytes():
            errors.append(f"generated output is stale: {name}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=HERE)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    if args.check:
        with tempfile.TemporaryDirectory(prefix="b04-evidence-governance-") as raw:
            rebuilt = Path(raw)
            write_outputs(rebuilt)
            errors = compare_outputs(HERE, rebuilt)
        for error in errors:
            print("ERROR: " + error)
        if errors:
            return 1
        print(f"PASS B04 generated projections are current: {len(OUTPUT_FILES)} files")
        return 0

    write_outputs(args.output_dir)
    summary = load(args.output_dir / "evidence-governance-summary.json")
    print(canonical_json(summary))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
