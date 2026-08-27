#!/usr/bin/env python3
"""Validate B04 identity, claim locator, evidence-role and gate projections."""
from __future__ import annotations

import json
import tempfile
from pathlib import Path
from typing import Any, Iterable
from urllib.parse import urlparse

from build_evidence_governance import OUTPUT_FILES, compare_outputs, write_outputs

HERE = Path(__file__).resolve().parent
POLICY_PATH = HERE / "evidence-governance-policy.json"
SCHEMA_PATH = HERE / "evidence-governance.schema.json"


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def ids(rows: Iterable[dict[str, Any]], key: str) -> list[str]:
    return [str(row[key]) for row in rows]


def validate_locator(
    locator: dict[str, Any],
    locator_states: set[str],
    claim_id: str,
    errors: list[str],
) -> None:
    required = {
        "source_url",
        "selector_kind",
        "selector_value",
        "source_state",
        "locator_state",
        "exact_claim_support",
    }
    if set(locator) != required:
        errors.append(f"locator field drift {claim_id}")
        return
    parsed = urlparse(locator["source_url"])
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        errors.append(f"invalid locator URL {claim_id}")
    if locator["locator_state"] not in locator_states:
        errors.append(f"invalid locator state {claim_id}")
    if locator["exact_claim_support"]:
        if locator["locator_state"] != "EXACT_SELECTOR_VERIFIED":
            errors.append(f"exact support without verified state {claim_id}")
        if not locator["selector_kind"] or not locator["selector_value"]:
            errors.append(f"exact support without selector {claim_id}")
        if not locator["source_state"]:
            errors.append(f"exact support without source state {claim_id}")


def validate_policy(errors: list[str]) -> tuple[set[str], set[str]]:
    policy = load(POLICY_PATH)
    schema = load(SCHEMA_PATH)
    roles = {row["role_id"] for row in policy["evidence_roles"]}
    locator_states = set(policy["locator_states"])
    required_roles = {
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
    if roles != required_roles:
        errors.append("controlled evidence-role vocabulary drift")
    if policy.get("status") != "review_candidate_unratified":
        errors.append("policy status must remain review_candidate_unratified")
    if policy.get("completion_claim") is not False:
        errors.append("policy must explicitly deny completion")
    if policy.get("gate_order") != [
        "RESEARCH_PROPOSAL",
        "SEMANTIC_RATIFICATION",
        "IMPLEMENTATION_QUALIFICATION",
        "EXECUTED_ACCEPTANCE",
    ]:
        errors.append("evidence gate order drift")
    if len(policy.get("non_collapse_laws", [])) < 20:
        errors.append("policy has too few non-collapse laws")
    if len(policy.get("entity_kinds", [])) < 10:
        errors.append("entity-kind taxonomy is too narrow")
    if len(policy.get("relationship_kinds", [])) < 12:
        errors.append("identity relationship taxonomy is too narrow")
    if len(policy.get("primary_sources", [])) < 5:
        errors.append("primary-source governance cards are missing")
    for source in policy.get("primary_sources", []):
        required = {
            "source_id",
            "title",
            "url",
            "issuing_authority",
            "evidence_roles",
            "bounded_claims",
            "non_authority_scope",
            "accessed_on",
        }
        if not required <= set(source):
            errors.append(f"primary-source card fields missing {source.get('source_id')}")
        if not source.get("bounded_claims") or not source.get("non_authority_scope"):
            errors.append(f"primary-source card scope missing {source.get('source_id')}")
    if schema.get("$schema") != "https://json-schema.org/draft/2020-12/schema":
        errors.append("evidence-governance schema dialect drift")
    if not schema.get("$defs"):
        errors.append("evidence-governance schema definitions missing")
    return roles, locator_states


def main() -> int:
    errors: list[str] = []
    controlled_roles, locator_states = validate_policy(errors)

    try:
        with tempfile.TemporaryDirectory(prefix="b04-evidence-governance-") as raw:
            rebuilt = Path(raw)
            write_outputs(rebuilt)
            errors.extend(compare_outputs(HERE, rebuilt))
    except (KeyError, TypeError, ValueError) as exc:
        errors.append(f"builder rejected committed source corpus: {exc}")

    manifest = load(HERE / "manifest.json")
    families: list[dict[str, Any]] = []
    for shard_name in manifest["shards"]:
        families.extend(load(HERE / shard_name)["families"])
    if [family["id"] for family in families] != manifest["family_ids"]:
        errors.append("family order or identity differs from manifest")

    refs: dict[str, dict[str, Any]] = {}
    orgs: dict[str, dict[str, Any]] = {}
    ref_families: dict[str, set[str]] = {}
    org_families: dict[str, set[str]] = {}
    expected_research_claims: set[tuple[str, str]] = set()
    expected_org_claims: set[tuple[str, str]] = set()
    for family in families:
        family_id = family["id"]
        for ref in family["research"]:
            refs[ref["id"]] = ref
            ref_families.setdefault(ref["id"], set()).add(family_id)
            expected_research_claims.add((family_id, ref["id"]))
        for org in family["organizations"]:
            orgs[org["id"]] = org
            org_families.setdefault(org["id"], set()).add(family_id)
            expected_org_claims.add((family_id, org["id"]))

    role_rows = load_jsonl(HERE / "research-reference-role-projection.jsonl")
    research_claims = load_jsonl(HERE / "research-reference-family-claims.jsonl")
    org_claims = load_jsonl(HERE / "organization-family-membership-claims.jsonl")
    identities = load_jsonl(HERE / "organization-identity-projection.jsonl")
    identity_gaps = load_jsonl(HERE / "organization-identity-gaps.jsonl")
    frontier = load_jsonl(HERE / "evidence-governance-frontier.jsonl")
    summary = load(HERE / "evidence-governance-summary.json")

    role_ids = ids(role_rows, "reference_id")
    if role_ids != sorted(role_ids) or set(role_ids) != set(refs):
        errors.append("role projection must cover every unique source exactly once in order")
    if len(role_ids) != len(set(role_ids)):
        errors.append("duplicate reference role projection")
    roles_by_ref: dict[str, tuple[list[str], str]] = {}
    for row in role_rows:
        ref_id = row["reference_id"]
        assigned = set(row["roles"])
        if not assigned or not assigned <= controlled_roles:
            errors.append(f"invalid controlled role projection {ref_id}")
        if row["role_state"] not in {
            "PROPOSED_UNRATIFIED",
            "UNCLASSIFIED_EXPLICIT_DEBT",
        }:
            errors.append(f"role state overclaim {ref_id}")
        if row["role_state"] == "UNCLASSIFIED_EXPLICIT_DEBT" and row["roles"] != [
            "unclassified_research_evidence"
        ]:
            errors.append(f"unclassified role coercion {ref_id}")
        if set(row["family_refs"]) != ref_families.get(ref_id, set()):
            errors.append(f"reference family coverage drift {ref_id}")
        if row["semantic_authority"] or row["completion_claim"]:
            errors.append(f"unsupported role authority/completion {ref_id}")
        validate_locator(row["evidence_locator"], locator_states, ref_id, errors)
        roles_by_ref[ref_id] = (row["roles"], row["role_state"])

    got_research_claims = {
        (row["family_id"], row["reference_id"]) for row in research_claims
    }
    if got_research_claims != expected_research_claims:
        errors.append("research-family claim ledger does not cover exact source occurrences")
    if len(research_claims) != len(expected_research_claims):
        errors.append("duplicate research-family claim")
    for row in research_claims:
        claim_id = row["claim_id"]
        expected_roles = roles_by_ref.get(row["reference_id"])
        actual_roles = (
            row["role_assignment"]["roles"],
            row["role_assignment"]["role_state"],
        )
        if actual_roles != expected_roles:
            errors.append(f"research claim role projection drift {claim_id}")
        if row["claim_state"] != "PROPOSED_UNRATIFIED":
            errors.append(f"research claim overstates ratification {claim_id}")
        if (
            row["semantic_authority"]
            or row["implementation_qualification"]
            or row["executed_acceptance"]
            or row["completion_claim"]
        ):
            errors.append(f"research claim overstates a downstream gate {claim_id}")
        validate_locator(row["evidence_locator"], locator_states, claim_id, errors)

    got_org_claims = {(row["family_id"], row["organization_id"]) for row in org_claims}
    if got_org_claims != expected_org_claims:
        errors.append("organization-family claim ledger does not cover exact source occurrences")
    if len(org_claims) != len(expected_org_claims):
        errors.append("duplicate organization-family claim")
    for row in org_claims:
        claim_id = row["claim_id"]
        if row["evidence_role"] != "adoption_evidence":
            errors.append(f"organization claim role drift {claim_id}")
        if row["role_state"] != "CONTROLLED_ADOPTION_ROLE":
            errors.append(f"organization claim role state drift {claim_id}")
        if row["status"] != "UNVERIFIED_EXPLICIT_DEBT":
            errors.append(f"organization claim overstates verification {claim_id}")
        if row["evidence_strength"] not in {
            "WEAK_HOMEPAGE_ONLY",
            "WEAK_ORGANIZATION_RESOURCE_ONLY",
        }:
            errors.append(f"unsupported organization evidence strength {claim_id}")
        if not row["required_upgrade"]:
            errors.append(f"organization claim upgrade debt missing {claim_id}")
        if (
            row["semantic_authority"]
            or row["qualification_claim"]
            or row["implementation_qualification"]
            or row["executed_acceptance"]
            or row["completion_claim"]
        ):
            errors.append(f"organization claim overstates a downstream gate {claim_id}")
        validate_locator(row["evidence_locator"], locator_states, claim_id, errors)

    identity_ids = ids(identities, "organization_id")
    if identity_ids != sorted(identity_ids) or set(identity_ids) != set(orgs):
        errors.append("identity projection must cover every source handle exactly once in order")
    if len(identity_ids) != len(set(identity_ids)):
        errors.append("duplicate organization identity projection")
    for row in identities:
        org_id = row["organization_id"]
        if row["identity_status"] != "PROVISIONAL_INTERNAL_HANDLE":
            errors.append(f"identity resolution overclaim {org_id}")
        if row["canonical_entity_kind"] != "UNRESOLVED":
            errors.append(f"entity-kind resolution overclaim {org_id}")
        if row["authoritative_identifiers"]:
            errors.append(f"authoritative identifier invented {org_id}")
        if set(row["family_refs"]) != org_families.get(org_id, set()):
            errors.append(f"organization family coverage drift {org_id}")
        if row["semantic_authority"] or row["completion_claim"]:
            errors.append(f"identity authority/completion overclaim {org_id}")

    gap_ids = ids(identity_gaps, "organization_id")
    if gap_ids != sorted(gap_ids) or gap_ids != identity_ids:
        errors.append("every provisional identity must have exactly one ordered identity gap")
    for row in identity_gaps:
        if row["status"] != "OPEN_EXPLICIT_DEBT":
            errors.append(f"identity gap state drift {row['organization_id']}")
        if len(row["required_reviews"]) < 6 or len(row["inference_prohibitions"]) < 4:
            errors.append(f"identity gap obligations incomplete {row['organization_id']}")
        if row["completion_claim"]:
            errors.append(f"identity gap completion overclaim {row['organization_id']}")

    expected_frontier = [
        "HR03_CANONICALIZE_ORGANIZATION_IDENTITY",
        "HR04_BIND_EVIDENCE_TO_CLAIMS",
        "HR05_RESEARCH_REFERENCE_ROLES",
    ]
    if ids(frontier, "requirement_id") != expected_frontier:
        errors.append("B04 frontier requirements or dependency order drift")
    if any(row["status"] == "SATISFIED_ENFORCED" for row in frontier):
        errors.append("B04 source debt cannot be marked satisfied by projection generation")
    if any(row["completion_claim"] for row in frontier):
        errors.append("B04 frontier completion fabricated")

    exact_org = sum(
        int(row["evidence_locator"]["exact_claim_support"]) for row in org_claims
    )
    exact_research = sum(
        int(row["evidence_locator"]["exact_claim_support"])
        for row in research_claims
    )
    unclassified = sum(
        row["role_state"] == "UNCLASSIFIED_EXPLICIT_DEBT" for row in role_rows
    )
    expected_counts = {
        "family_count": len(families),
        "unique_research_reference_count": len(refs),
        "research_reference_family_claim_count": len(expected_research_claims),
        "unclassified_research_reference_count": unclassified,
        "unique_organization_count": len(orgs),
        "organization_identity_gap_count": len(orgs),
        "organization_family_membership_claim_count": len(expected_org_claims),
        "weak_membership_claim_count": len(expected_org_claims) - exact_org,
        "strong_exact_product_membership_claim_count": exact_org,
        "exact_research_claim_binding_count": exact_research,
        "exact_claim_binding_count": exact_org + exact_research,
    }
    for key, expected in expected_counts.items():
        if summary.get(key) != expected:
            errors.append(f"summary drift {key}: {summary.get(key)} != {expected}")
    for zero_key in (
        "authoritatively_resolved_identity_count",
        "ratified_evidence_role_count",
        "identity_relationships_fully_adjudicated_count",
        "semantic_ratification_count",
        "implementation_qualification_count",
        "executed_acceptance_count",
    ):
        if summary.get(zero_key) != 0:
            errors.append(f"summary invents gated evidence {zero_key}")
    if set(summary.get("controlled_evidence_roles", [])) != controlled_roles:
        errors.append("summary evidence-role vocabulary drift")
    if summary.get("completion_claim") is not False:
        errors.append("B04 completion fabricated")

    if errors:
        for error in errors:
            print("ERROR: " + error)
        return 1
    print(
        "PASS B04 evidence governance: "
        f"{len(families)} families; {len(refs)} sources; "
        f"{len(research_claims)} source-family claims; {len(orgs)} provisional entities; "
        f"{len(org_claims)} organization-family claims; exact bindings remain explicit debt"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
