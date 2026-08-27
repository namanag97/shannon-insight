#!/usr/bin/env python3
"""Structural checks for the domain-atlas enumeration seed.

Passing this validator means only that candidate enumeration and known ambiguity accounting are
internally consistent. It does not certify that any seed is a valid bounded context.
"""

from __future__ import annotations

import json
import re
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parent


def load(name: str) -> dict:
    with (ROOT / name).open(encoding="utf-8") as handle:
        return json.load(handle)


def load_jsonl(name: str) -> list[dict]:
    records = []
    with (ROOT / name).open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            if not line.strip():
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise ValueError(f"{name}:{line_number}: {exc}") from exc
    return records


def main() -> int:
    errors: list[str] = []
    axes = load("axis-taxonomy.json")
    families = load("context-families.json")
    ambiguities = load("ownership-ambiguities.json")
    semantic_cluster = load("clusters/semantic-layer-formula.contexts.json")
    analytics_families = load("universes/analytics_types/family-catalog.json")
    analytics_candidates = load_jsonl("universes/analytics_types/candidate-practices.jsonl")
    operation_families = load("universes/operations/family-catalog.json")
    operation_candidates = load_jsonl("universes/operations/operation-candidates.jsonl")
    operation_deep_specs = load("universes/operations/deep-specifications.json")
    universe_audit = load("universes/universe-coverage-audit.json")
    universe_contract = load("universes/universe-contract.json")

    modality_contract = universe_contract.get("automation_modality_contract", {})
    if modality_contract.get("default_posture") != "DETERMINISTIC_CORE_ONLY":
        errors.append("automation modality default must remain DETERMINISTIC_CORE_ONLY")
    if set(modality_contract.get("use_site_postures", [])) != {
        "PROHIBITED", "OPTIONAL", "REQUIRED_BY_INTENT", "UNDETERMINED",
    }:
        errors.append("automation modality use-site postures are incomplete or widened")
    required_modality_laws = {
        "selection_law", "non_authority_law", "removal_law", "naming_law", "hard_work_law",
    }
    if not required_modality_laws.issubset(modality_contract):
        errors.append("automation modality contract lacks deterministic constitutional laws")

    if len(axes.get("axes", {})) < 10:
        errors.append("coverage tensor must retain at least ten independent axes")

    family_ids: set[str] = set()
    occurrences: dict[str, list[str]] = defaultdict(list)
    for family in families.get("families", []):
        family_id = family.get("family_id")
        if not family_id or family_id in family_ids:
            errors.append(f"invalid or duplicate family_id: {family_id!r}")
            continue
        family_ids.add(family_id)
        seeds = family.get("seed_contexts", [])
        if len(seeds) != len(set(seeds)):
            errors.append(f"duplicate seed within family {family_id}")
        for seed in seeds:
            occurrences[seed].append(family_id)

    if len(occurrences) < 100:
        errors.append("fewer than 100 distinct context candidates; enumeration is too shallow")

    actual_ambiguous = {term: sorted(where) for term, where in occurrences.items() if len(where) > 1}
    declared_ambiguous: dict[str, list[str]] = {}
    for item in ambiguities.get("ambiguities", []):
        term = item.get("term")
        where = sorted(item.get("occurs_in", []))
        if not term or term in declared_ambiguous:
            errors.append(f"invalid or duplicate ambiguity term: {term!r}")
            continue
        if item.get("disposition") not in {
            "adjudicate",
            "presumptive_split",
            "presumptive_single_owner",
            "presumptive_authority_plus_reaction",
        }:
            errors.append(f"unknown ambiguity disposition for {term}")
        declared_ambiguous[term] = where

    if actual_ambiguous != declared_ambiguous:
        missing = sorted(set(actual_ambiguous) - set(declared_ambiguous))
        stale = sorted(set(declared_ambiguous) - set(actual_ambiguous))
        mismatched = sorted(
            term
            for term in set(actual_ambiguous) & set(declared_ambiguous)
            if actual_ambiguous[term] != declared_ambiguous[term]
        )
        if missing:
            errors.append(f"undeclared ownership ambiguities: {missing}")
        if stale:
            errors.append(f"declared ambiguities no longer duplicated: {stale}")
        if mismatched:
            errors.append(f"ambiguity occurrence mismatch: {mismatched}")

    context_ids: set[str] = set()
    required_context_fields = {
        "context_id",
        "name",
        "classification",
        "sovereign_question",
        "owns",
        "excludes",
        "imports",
        "exports",
        "invariants",
        "refusals",
    }
    owned_terms: dict[str, str] = {}
    for context in semantic_cluster.get("contexts", []):
        missing_fields = sorted(required_context_fields - set(context))
        context_id = context.get("context_id", "<missing>")
        if missing_fields:
            errors.append(f"semantic cluster context {context_id} missing {missing_fields}")
        if context_id in context_ids:
            errors.append(f"duplicate semantic cluster context_id: {context_id}")
        context_ids.add(context_id)
        if not context.get("invariants") or not context.get("refusals"):
            errors.append(f"semantic cluster context {context_id} lacks laws or refusals")
        for term in context.get("owns", []):
            if term in owned_terms:
                errors.append(
                    f"semantic cluster duplicate owner for {term}: "
                    f"{owned_terms[term]} and {context_id}"
                )
            owned_terms[term] = context_id

    allowed_relationships = {
        "customer_supplier",
        "conformist",
        "anti_corruption_layer",
        "open_host_service",
        "published_language",
        "shared_kernel",
        "separate_ways",
        "independent_appraisal",
        "authority_delegation",
        "evidence_submission",
        "compiler_requirement",
        "provider_offer",
        "runtime_receipt",
    }
    for index, relationship in enumerate(semantic_cluster.get("context_relationships", []), 1):
        if not isinstance(relationship, list) or len(relationship) != 3:
            errors.append(f"invalid semantic cluster relationship #{index}")
            continue
        source, kind, target = relationship
        if source not in context_ids or target not in context_ids:
            errors.append(f"unknown context in semantic cluster relationship #{index}")
        if kind not in allowed_relationships:
            errors.append(f"unknown relationship kind {kind!r} in semantic cluster")

    required_practice_fields = {
        "practice_id", "edition", "status", "family_id", "name", "aliases", "definition",
        "practice_kind", "distinctiveness_basis", "intent_verbs", "input_contracts",
        "output_contracts", "assumptions", "uncertainty_contract", "evaluation_contract",
        "decision_proximity", "domain_portability", "evidence_refs", "llm_dependency", "gaps",
    }
    practice_ids: set[str] = set()
    practice_labels: dict[str, list[str]] = defaultdict(list)
    forbidden = re.compile(
        r"(?:large language|\\bllms?\\b|prompt engineering|\\brag analytics\\b|agent memory|generative)"
    )
    for candidate in analytics_candidates:
        practice_id = candidate.get("practice_id", "<missing>")
        missing_fields = sorted(required_practice_fields - set(candidate))
        if missing_fields:
            errors.append(f"analytical practice {practice_id} missing {missing_fields}")
        if practice_id in practice_ids:
            errors.append(f"duplicate analytical practice id: {practice_id}")
        practice_ids.add(practice_id)
        label = candidate.get("name", "").lower()
        practice_labels[label].append(practice_id)
        searchable = f"{practice_id} {label}".lower()
        if forbidden.search(searchable):
            errors.append(f"forbidden LLM/generative core analytical practice: {practice_id}")
        if candidate.get("status") == "hypothesis" and not candidate.get("gaps"):
            errors.append(f"hypothesis practice lacks explicit gaps: {practice_id}")

    if len(practice_ids) < 500:
        errors.append("analytical-practice hypothesis queue has fewer than 500 candidates")
    if analytics_families.get("candidate_count") != len(analytics_candidates):
        errors.append("analytics family catalog candidate count differs from JSONL")
    actual_duplicate_labels = {
        label: refs for label, refs in sorted(practice_labels.items()) if len(refs) > 1
    }
    if analytics_families.get("duplicate_label_review_queue") != actual_duplicate_labels:
        errors.append("analytics duplicate-label review queue is stale")
    if analytics_families.get("completion_claim") is not False:
        errors.append("analytics hypothesis queue must not claim completeness")

    required_operation_fields = {
        "operation_id", "edition", "status", "family_id", "name", "operation_kind",
        "semantic_owner_candidate", "signature", "effect_class", "determinism", "idempotency",
        "totality", "information_loss", "order_sensitivity", "time_sensitivity", "statefulness",
        "execution_modes", "preconditions", "postconditions", "laws", "refusals", "failures",
        "resource_model", "provider_requirements", "evidence_refs", "llm_dependency", "gaps",
    }
    operation_ids: set[str] = set()
    operation_labels: dict[str, list[str]] = defaultdict(list)
    for candidate in operation_candidates:
        operation_id = candidate.get("operation_id", "<missing>")
        missing_fields = sorted(required_operation_fields - set(candidate))
        if missing_fields:
            errors.append(f"operation candidate {operation_id} missing {missing_fields}")
        if operation_id in operation_ids:
            errors.append(f"duplicate operation id: {operation_id}")
        operation_ids.add(operation_id)
        operation_labels[candidate.get("name", "").lower()].append(operation_id)
        searchable = f"{operation_id} {candidate.get('name', '')}".lower()
        if forbidden.search(searchable):
            errors.append(f"forbidden LLM/generative core operation: {operation_id}")
        if candidate.get("status") == "hypothesis" and not candidate.get("gaps"):
            errors.append(f"hypothesis operation lacks explicit gaps: {operation_id}")
    if len(operation_ids) < 500:
        errors.append("operation hypothesis queue has fewer than 500 candidates")
    if operation_families.get("candidate_count") != len(operation_candidates):
        errors.append("operation family catalog candidate count differs from JSONL")
    actual_duplicate_operations = {
        label: refs for label, refs in sorted(operation_labels.items()) if len(refs) > 1
    }
    if operation_families.get("duplicate_label_review_queue") != actual_duplicate_operations:
        errors.append("operation duplicate-label review queue is stale")
    if operation_families.get("completion_claim") is not False:
        errors.append("operation hypothesis queue must not claim completeness")

    deep_ids: set[str] = set()
    for spec in operation_deep_specs.get("operations", []):
        operation_id = spec.get("operation_id", "<missing>")
        missing_fields = sorted(required_operation_fields - set(spec))
        if missing_fields:
            errors.append(f"deep operation {operation_id} missing {missing_fields}")
        if operation_id not in operation_ids:
            errors.append(f"deep operation has no hypothesis identity: {operation_id}")
        if operation_id in deep_ids:
            errors.append(f"duplicate deep operation specification: {operation_id}")
        deep_ids.add(operation_id)
        for surface in ("preconditions", "postconditions", "laws", "refusals", "provider_requirements", "evidence_refs"):
            if not spec.get(surface):
                errors.append(f"deep operation {operation_id} has empty {surface}")
        signature = spec.get("signature", {})
        if not signature.get("inputs") or not signature.get("outputs") or signature.get("error_type") == "UnadjudicatedOperationError":
            errors.append(f"deep operation {operation_id} lacks a typed signature")
    if len(deep_ids) < 10:
        errors.append("fewer than ten operation hypotheses have deep specification overlays")
    if operation_deep_specs.get("completion_claim") is not False:
        errors.append("deep operation overlay set must not claim completeness")
    if universe_audit.get("completion_claim") is not False:
        errors.append("universe audit must not claim completeness")

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    seed_count = sum(len(family["seed_contexts"]) for family in families["families"])
    print(
        "PASS domain-atlas seed: "
        f"{len(axes['axes'])} axes, {len(family_ids)} families, "
        f"{seed_count} occurrences, {len(occurrences)} distinct candidates, "
        f"{len(actual_ambiguous)} declared ownership ambiguities, "
        f"{len(context_ids)} deeply seeded semantic/formula contexts, "
        f"{len(practice_ids)} analytical-practice hypotheses, "
        f"{len(operation_ids)} operation hypotheses/{len(deep_ids)} deep overlays"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
