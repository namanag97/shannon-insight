#!/usr/bin/env python3
"""Build exact identity, claim, evidence-role and frontier ledgers from family shards."""

from __future__ import annotations

import argparse
import shutil
import tempfile
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Sequence, Set, Tuple
from urllib.parse import urlparse

from source_model import (
    EntityRecord,
    EvidenceClaim,
    EvidenceLocator,
    EvidenceRoleAssignment,
    load_json,
    record,
    sha256_file,
    stable_claim_id,
    write_json,
    write_jsonl,
)

HERE = Path(__file__).resolve().parent
FAMILY_DIR = HERE.parent
DEFAULT_OUTPUT = HERE / "generated"
GENERATED_FILES = (
    "entity-registry.jsonl",
    "identity-gaps.jsonl",
    "organization-membership-claims.jsonl",
    "research-source-registry.jsonl",
    "research-membership-claims.jsonl",
    "frontier.jsonl",
    "summary.json",
)

CONTROLLED_ROLES = {
    "foundational_theory",
    "algorithm",
    "architecture",
    "standard",
    "empirical_validation",
    "human_factors",
    "governance",
    "product_boundary_evidence",
    "adoption_evidence",
    "implementation_reference",
    "unclassified_research_evidence",
}

GOVERNANCE_TAGS = {"assurance", "audit", "compliance", "governance", "lineage", "policy", "privacy", "provenance", "risk", "security", "trust"}
HUMAN_TAGS = {"accessibility", "alert", "collaboration", "decision", "explanation", "human", "interaction", "narrative", "notification", "reporting", "visualization", "workflow"}
ALGORITHM_TAGS = {"algorithm", "causal", "forecast", "graph", "machine_learning", "ml", "optimization", "process", "query", "search", "simulation", "statistics"}
ARCHITECTURE_TAGS = {"architecture", "catalog", "data_product", "dataflow", "ontology", "orchestration", "runtime", "semantics", "workflow"}
EMPIRICAL_TAGS = {"benchmark", "evaluation", "experiment", "human_factors", "validation"}
THEORY_KINDS = {"book", "paper", "peer_reviewed", "research_paper"}
IMPLEMENTATION_KINDS = {"documentation", "official_documentation", "project_documentation", "technical_documentation"}
ARCHITECTURE_KINDS = {"industry_paper", "technical_report", "whitepaper"}


def load_families() -> Tuple[Dict[str, Any], List[Dict[str, Any]], List[Path]]:
    manifest_path = FAMILY_DIR / "manifest.json"
    manifest = load_json(manifest_path)
    families: List[Dict[str, Any]] = []
    paths = [manifest_path]
    for shard_name in manifest["shards"]:
        path = FAMILY_DIR / shard_name
        families.extend(load_json(path)["families"])
        paths.append(path)
    if [row["id"] for row in families] != manifest["family_ids"]:
        raise ValueError("family order or identity differs from manifest")
    return manifest, families, paths


def locator(url: str) -> EvidenceLocator:
    parsed = urlparse(url)
    if parsed.fragment:
        return EvidenceLocator(url, "uri_fragment", parsed.fragment, None, "FRAGMENT_PRESENT_UNVERIFIED", False)
    if parsed.netloc.casefold() == "doi.org":
        return EvidenceLocator(url, "record_identifier", parsed.path.lstrip("/"), None, "RESOURCE_IDENTIFIER_ONLY", False)
    return EvidenceLocator(url, None, None, None, "RESOURCE_ONLY_EXACT_SELECTOR_MISSING", False)


def proposed_roles(reference: Dict[str, Any]) -> Tuple[List[str], str, str]:
    kind = str(reference.get("kind", "")).casefold()
    tags = {str(tag).casefold() for tag in reference.get("tags", [])}
    roles: Set[str] = set()
    reasons: Set[str] = set()
    if kind == "standard":
        roles.add("standard"); reasons.add("source kind is standard")
    if kind in THEORY_KINDS:
        roles.add("foundational_theory"); reasons.add("source kind is theory-capable literature")
    if kind in IMPLEMENTATION_KINDS:
        roles.add("implementation_reference"); reasons.add("source kind is implementation documentation")
    if kind in ARCHITECTURE_KINDS or tags & ARCHITECTURE_TAGS:
        roles.add("architecture"); reasons.add("metadata indicates architecture or system structure")
    if tags & ALGORITHM_TAGS:
        roles.add("algorithm"); reasons.add("metadata indicates an analytical or computational method")
    if tags & EMPIRICAL_TAGS:
        roles.add("empirical_validation"); reasons.add("metadata explicitly indicates evaluation or validation")
    if tags & HUMAN_TAGS:
        roles.add("human_factors"); reasons.add("metadata indicates human work or experience")
    if tags & GOVERNANCE_TAGS:
        roles.add("governance"); reasons.add("metadata indicates governance, trust or assurance")
    if kind in ARCHITECTURE_KINDS | IMPLEMENTATION_KINDS:
        roles.add("product_boundary_evidence"); reasons.add("source may help falsify a product boundary")
    if not roles:
        return ["unclassified_research_evidence"], "UNCLASSIFIED_EXPLICIT_DEBT", "existing metadata does not support a narrower controlled role"
    if not roles <= CONTROLLED_ROLES:
        raise ValueError("role classifier emitted an uncontrolled role")
    return sorted(roles), "PROPOSED_UNRATIFIED", "; ".join(sorted(reasons))


def source_digests(paths: Sequence[Path]) -> List[Dict[str, str]]:
    return [{"path": path.relative_to(FAMILY_DIR).as_posix(), "sha256": sha256_file(path)} for path in paths]


def build_records() -> Dict[str, Any]:
    manifest, families, source_paths = load_families()
    entity_defs: Dict[str, Tuple[str, str, str]] = {}
    entity_families: Dict[str, Set[str]] = defaultdict(set)
    research_defs: Dict[str, Tuple[Any, ...]] = {}
    research_sources: Dict[str, Dict[str, Any]] = {}
    org_claims: List[Dict[str, Any]] = []
    research_claims: List[Dict[str, Any]] = []

    for family in families:
        family_id = family["id"]
        for organization in family["organizations"]:
            entity_id = organization["id"]
            definition = (organization["name"], organization["url"], organization["organization_kind"])
            if entity_id in entity_defs and entity_defs[entity_id] != definition:
                raise ValueError("conflicting entity definition: {}".format(entity_id))
            entity_defs[entity_id] = definition
            entity_families[entity_id].add(family_id)
            org_claims.append(record(EvidenceClaim(
                stable_claim_id("adoption", family_id, entity_id),
                "organization_family_adoption_membership",
                "entity:" + entity_id,
                "provides_adoption_evidence_for",
                "coverage_family:" + family_id,
                "{} is proposed adoption evidence for horizontal coverage coordinate {}.".format(organization["name"], family_id),
                family_id,
                [locator(organization["url"])],
                EvidenceRoleAssignment(["adoption_evidence"], "CONTROLLED_ADOPTION_ROLE", "independent products and organizations may demonstrate adoption only; they do not define canonical semantics"),
                "UNVERIFIED_EXPLICIT_DEBT",
                False, False, False, False,
            )))

        for reference in family["research"]:
            source_id = reference["id"]
            definition = (reference["title"], reference["url"], reference["kind"], tuple(reference["tags"]), reference.get("year"))
            if source_id in research_defs and research_defs[source_id] != definition:
                raise ValueError("conflicting research definition: {}".format(source_id))
            research_defs[source_id] = definition
            research_sources[source_id] = reference
            roles, role_state, rationale = proposed_roles(reference)
            research_claims.append(record(EvidenceClaim(
                stable_claim_id("research", family_id, source_id),
                "research_family_relevance_membership",
                "source:" + source_id,
                "is_proposed_evidence_for",
                "coverage_family:" + family_id,
                "{} is proposed evidence for horizontal coverage coordinate {}.".format(reference["title"], family_id),
                family_id,
                [locator(reference["url"])],
                EvidenceRoleAssignment(roles, role_state, rationale),
                "PROPOSED_UNRATIFIED",
                False, False, False, False,
            )))

    entities: List[Dict[str, Any]] = []
    gaps: List[Dict[str, Any]] = []
    for entity_id in sorted(entity_defs):
        name, url, declared_kind = entity_defs[entity_id]
        entities.append(record(EntityRecord(
            entity_id, name, url, declared_kind, "UNRESOLVED", "PROVISIONAL_INTERNAL_HANDLE", [], [name], sorted(entity_families[entity_id]), False, False
        )))
        gaps.append({
            "gap_id": "identity_gap_" + entity_id,
            "entity_id": entity_id,
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
        })

    source_registry = [{
        "source_id": source_id,
        "title": research_sources[source_id]["title"],
        "url": research_sources[source_id]["url"],
        "source_kind": research_sources[source_id]["kind"],
        "tags": research_sources[source_id]["tags"],
        "year": research_sources[source_id].get("year"),
        "identity_state": "SOURCE_RECORD_ONLY",
        "exact_locator_required_for_claim_use": True,
        "semantic_authority": False,
        "completion_claim": False,
    } for source_id in sorted(research_sources)]

    exact_bindings = sum(
        binding["exact_claim_support"]
        for claim in org_claims + research_claims
        for binding in claim["evidence_bindings"]
    )
    unclassified = sum(claim["role_assignment"]["role_state"] == "UNCLASSIFIED_EXPLICIT_DEBT" for claim in research_claims)
    frontier = [
        {
            "requirement_id": "HR03_CANONICALIZE_ORGANIZATION_IDENTITY",
            "status": "PARTIAL_EXPLICIT_DEBT",
            "source_unique_entities": len(entities),
            "authoritatively_resolved_entities": 0,
            "provisional_entities": len(entities),
            "explicit_identity_gap_rows": len(gaps),
            "inferred_relationships": 0,
            "exit_condition": "Every entity has a canonical kind, authoritative identifier or exact identity evidence, aliases/history, and claim-bound valid-time relationships where applicable.",
            "completion_claim": False,
        },
        {
            "requirement_id": "HR04_BIND_EVIDENCE_TO_CLAIMS",
            "status": "OPEN_EXPLICIT_DEBT",
            "organization_membership_claims": len(org_claims),
            "research_membership_claims": len(research_claims),
            "exact_claim_bindings": exact_bindings,
            "open_claim_bindings": len(org_claims) + len(research_claims) - exact_bindings,
            "exit_condition": "Every membership claim has a stable selector and source-state binding that a validator can re-resolve to the asserted passage or record.",
            "completion_claim": False,
        },
        {
            "requirement_id": "HR05_RESEARCH_REFERENCE_ROLES",
            "status": "PARTIAL_EXPLICIT_DEBT",
            "unique_research_sources": len(source_registry),
            "research_membership_claims": len(research_claims),
            "controlled_role_assignments": len(research_claims),
            "unclassified_role_claims": unclassified,
            "ratified_role_assignments": 0,
            "exit_condition": "Every source-family claim has a controlled, semantically ratified role checked against the bounded claim and family question.",
            "completion_claim": False,
        },
    ]
    summary = {
        "schema_version": "1.0.0",
        "as_of": manifest["as_of"],
        "status": "review_candidate_unratified",
        "source_manifest_status": manifest["status"],
        "source_files": source_digests(source_paths),
        "counts": {
            "families": len(families),
            "organization_memberships": len(org_claims),
            "unique_entities": len(entities),
            "identity_gaps": len(gaps),
            "research_memberships": len(research_claims),
            "unique_research_sources": len(source_registry),
            "exact_claim_bindings": exact_bindings,
            "ratified_role_assignments": 0,
            "semantic_ratifications": 0,
            "implementation_qualifications": 0,
            "executed_acceptances": 0,
        },
        "frontier_requirements": [row["requirement_id"] for row in frontier],
        "non_completion_claims": [
            "generated ledgers expose source debt; they do not repair it",
            "adoption evidence is not semantic authority",
            "proposed evidence roles are not ratified roles",
            "source URLs without exact selectors do not prove bounded claims",
            "no implementation qualification or executed vertical acceptance is asserted",
        ],
        "completion_claim": False,
    }
    return {
        "entity-registry.jsonl": entities,
        "identity-gaps.jsonl": gaps,
        "organization-membership-claims.jsonl": sorted(org_claims, key=lambda row: row["claim_id"]),
        "research-source-registry.jsonl": source_registry,
        "research-membership-claims.jsonl": sorted(research_claims, key=lambda row: row["claim_id"]),
        "frontier.jsonl": frontier,
        "summary.json": summary,
    }


def build(output: Path) -> None:
    rows = build_records()
    output.mkdir(parents=True, exist_ok=True)
    for name in GENERATED_FILES:
        if name.endswith(".jsonl"):
            write_jsonl(output / name, rows[name])
        else:
            write_json(output / name, rows[name])


def compare_generated(expected: Path, actual: Path) -> List[str]:
    errors: List[str] = []
    required = set(GENERATED_FILES)
    expected_names = {p.name for p in expected.iterdir() if p.is_file()}
    actual_names = {p.name for p in actual.iterdir() if p.is_file()}
    if expected_names != required:
        errors.append("committed generated file set differs: {}".format(sorted(expected_names)))
    if actual_names != required:
        errors.append("builder output file set differs: {}".format(sorted(actual_names)))
    for name in sorted(required & expected_names & actual_names):
        if (expected / name).read_bytes() != (actual / name).read_bytes():
            errors.append("generated file is stale: " + name)
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.check:
        if not DEFAULT_OUTPUT.is_dir():
            print("ERROR: committed generated directory missing: {}".format(DEFAULT_OUTPUT))
            return 1
        with tempfile.TemporaryDirectory(prefix="horizontal-evidence-governance-") as raw:
            rebuilt = Path(raw)
            build(rebuilt)
            errors = compare_generated(DEFAULT_OUTPUT, rebuilt)
        for error in errors:
            print("ERROR: " + error)
        if errors:
            return 1
        print("PASS generated evidence-governance ledgers are current: {} files".format(len(GENERATED_FILES)))
        return 0
    if args.output.exists():
        shutil.rmtree(args.output)
    build(args.output)
    print("PASS generated horizontal evidence-governance ledgers: {}".format(args.output))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
