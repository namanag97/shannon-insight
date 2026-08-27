#!/usr/bin/env python3
"""Validate horizontal evidence identity, claim-binding and role ledgers."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path
from typing import Any, Dict, Iterable, List, Set
from urllib.parse import urlparse

from build import GENERATED_FILES, build, compare_generated
from source_model import load_json, load_jsonl

HERE = Path(__file__).resolve().parent
DEFAULT_GENERATED = HERE / "generated"
REQUIRED_ROLES = {
    "foundational_theory", "algorithm", "architecture", "standard",
    "empirical_validation", "human_factors", "governance",
    "product_boundary_evidence", "adoption_evidence",
    "implementation_reference", "unclassified_research_evidence",
}


def ids(rows: Iterable[Dict[str, Any]], key: str) -> List[str]:
    return [str(row[key]) for row in rows]


def validate_static(errors: List[str]) -> Set[str]:
    package_manifest = load_json(HERE / "manifest.json")
    policy = load_json(HERE / "policy.json")
    role_taxonomy = load_json(HERE / "evidence-role-taxonomy.json")
    identity_taxonomy = load_json(HERE / "entity-identity-taxonomy.json")
    if package_manifest.get("status") != "review_candidate_unratified" or package_manifest.get("completion_claim") is not False:
        errors.append("package manifest must remain an unratified non-completion candidate")
    for relative in package_manifest.get("primary_source_cards", []):
        if not (HERE / relative).is_file():
            errors.append("package manifest refers to missing source card: " + relative)
    roles = {row["role_id"] for row in role_taxonomy["roles"]}
    if roles != REQUIRED_ROLES:
        errors.append("evidence-role taxonomy differs from controlled role set")
    if policy.get("status") != "review_candidate_unratified" or policy.get("completion_claim") is not False:
        errors.append("policy must remain an unratified non-completion candidate")
    if len(policy.get("non_collapse_laws", [])) < 10:
        errors.append("policy has too few non-collapse laws")
    if len(identity_taxonomy.get("entity_kinds", [])) < 8 or len(identity_taxonomy.get("relationship_kinds", [])) < 8:
        errors.append("identity taxonomy is too narrow")
    cards = sorted((HERE / "sources").glob("*.json"))
    if len(cards) < 5:
        errors.append("at least five primary-source cards are required")
    required = {"source_id", "title", "url", "issuing_authority", "evidence_roles", "bounded_claims", "non_authority_scope", "accessed_on"}
    for path in cards:
        row = load_json(path)
        if not required <= set(row):
            errors.append("source card missing fields: " + path.name)
            continue
        parsed = urlparse(row["url"])
        if parsed.scheme != "https" or not parsed.netloc:
            errors.append("source card URL is not HTTPS: " + path.name)
        if not row["bounded_claims"] or not row["non_authority_scope"]:
            errors.append("source card lacks bounded scope: " + path.name)
    return roles


def validate_generated(generated: Path, errors: List[str], roles: Set[str]) -> None:
    found = {path.name for path in generated.iterdir() if path.is_file()}
    if found != set(GENERATED_FILES):
        errors.append("generated file set differs: {}".format(sorted(found)))
        return
    entities = load_jsonl(generated / "entity-registry.jsonl")
    gaps = load_jsonl(generated / "identity-gaps.jsonl")
    org_claims = load_jsonl(generated / "organization-membership-claims.jsonl")
    sources = load_jsonl(generated / "research-source-registry.jsonl")
    research_claims = load_jsonl(generated / "research-membership-claims.jsonl")
    frontier = load_jsonl(generated / "frontier.jsonl")
    summary = load_json(generated / "summary.json")

    entity_ids = ids(entities, "entity_id")
    source_ids = ids(sources, "source_id")
    if entity_ids != sorted(entity_ids) or len(entity_ids) != len(set(entity_ids)):
        errors.append("entity registry is not sorted and unique")
    if sorted(ids(gaps, "entity_id")) != entity_ids:
        errors.append("every provisional entity must have one identity gap")
    if source_ids != sorted(source_ids) or len(source_ids) != len(set(source_ids)):
        errors.append("research source registry is not sorted and unique")
    if len(ids(org_claims, "claim_id")) != len(set(ids(org_claims, "claim_id"))):
        errors.append("organization claim ids are not unique")
    if len(ids(research_claims, "claim_id")) != len(set(ids(research_claims, "claim_id"))):
        errors.append("research claim ids are not unique")

    entity_set, source_set = set(entity_ids), set(source_ids)
    for entity in entities:
        if entity["canonical_entity_kind"] != "UNRESOLVED" or entity["identity_state"] != "PROVISIONAL_INTERNAL_HANDLE":
            errors.append("entity overclaims identity resolution: " + entity["entity_id"])
        if entity["authoritative_identifiers"] or entity["semantic_authority"] or entity["completion_claim"]:
            errors.append("entity invents authority or completion: " + entity["entity_id"])

    exact_bindings = 0
    for claim in org_claims + research_claims:
        if claim["semantic_authority"] or claim["implementation_qualification"] or claim["executed_acceptance"] or claim["completion_claim"]:
            errors.append("claim overstates a gated result: " + claim["claim_id"])
        assigned = set(claim["role_assignment"]["roles"])
        if not assigned or not assigned <= roles:
            errors.append("claim has an invalid controlled role: " + claim["claim_id"])
        if len(claim["evidence_bindings"]) != 1:
            errors.append("claim must have one source binding: " + claim["claim_id"])
            continue
        binding = claim["evidence_bindings"][0]
        exact_bindings += int(binding["exact_claim_support"])
        if binding["exact_claim_support"] and not (binding["selector_kind"] and binding["selector_value"] and binding["source_state"] and binding["locator_state"] == "EXACT_SELECTOR_VERIFIED"):
            errors.append("exact claim support is incomplete: " + claim["claim_id"])

    for claim in org_claims:
        if claim["subject_id"].removeprefix("entity:") not in entity_set:
            errors.append("organization claim refers to unknown entity: " + claim["claim_id"])
        if claim["role_assignment"]["roles"] != ["adoption_evidence"] or claim["claim_state"] != "UNVERIFIED_EXPLICIT_DEBT":
            errors.append("organization claim overstates adoption evidence: " + claim["claim_id"])
    for claim in research_claims:
        if claim["subject_id"].removeprefix("source:") not in source_set:
            errors.append("research claim refers to unknown source: " + claim["claim_id"])
        if claim["claim_state"] != "PROPOSED_UNRATIFIED":
            errors.append("research claim overstates ratification: " + claim["claim_id"])

    expected_frontier = ["HR03_CANONICALIZE_ORGANIZATION_IDENTITY", "HR04_BIND_EVIDENCE_TO_CLAIMS", "HR05_RESEARCH_REFERENCE_ROLES"]
    if ids(frontier, "requirement_id") != expected_frontier:
        errors.append("frontier must cover HR03..HR05 in dependency order")
    if any(row["completion_claim"] for row in frontier):
        errors.append("frontier must not claim completion")

    counts = summary["counts"]
    expected_counts = {
        "organization_memberships": len(org_claims),
        "unique_entities": len(entities),
        "identity_gaps": len(gaps),
        "research_memberships": len(research_claims),
        "unique_research_sources": len(sources),
        "exact_claim_bindings": exact_bindings,
    }
    for key, expected in expected_counts.items():
        if counts.get(key) != expected:
            errors.append("summary count is stale: " + key)
    for key in ("ratified_role_assignments", "semantic_ratifications", "implementation_qualifications", "executed_acceptances"):
        if counts.get(key) != 0:
            errors.append("summary invents gated evidence: " + key)
    if summary.get("completion_claim") is not False:
        errors.append("summary must explicitly deny completion")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--generated", type=Path)
    parser.add_argument("--check-committed", action="store_true")
    args = parser.parse_args()
    errors: List[str] = []
    roles = validate_static(errors)
    if args.generated:
        if not args.generated.is_dir():
            errors.append("generated directory missing: {}".format(args.generated))
        else:
            validate_generated(args.generated, errors, roles)
    elif args.check_committed:
        if not DEFAULT_GENERATED.is_dir():
            errors.append("committed generated directory missing: {}".format(DEFAULT_GENERATED))
        else:
            with tempfile.TemporaryDirectory(prefix="horizontal-evidence-governance-") as raw:
                rebuilt = Path(raw)
                build(rebuilt)
                errors.extend(compare_generated(DEFAULT_GENERATED, rebuilt))
            validate_generated(DEFAULT_GENERATED, errors, roles)
    else:
        with tempfile.TemporaryDirectory(prefix="horizontal-evidence-governance-") as raw:
            generated = Path(raw)
            build(generated)
            validate_generated(generated, errors, roles)
    for error in errors:
        print("ERROR: " + error)
    if errors:
        return 1
    print("PASS horizontal evidence governance; unresolved gates remain explicit")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
