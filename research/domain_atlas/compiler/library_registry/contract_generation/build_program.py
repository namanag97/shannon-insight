#!/usr/bin/env python3
"""Build a deterministic, non-authoritative bulk exact-contract generation program.

This program scales research and specification work without manufacturing domain truth.  It
classifies open candidates into structural archetype proposals, creates one constitution work item
per research family, and expands structural obligations.  Only owner-published source contracts can
close the canonical exact-API gaps.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
REGISTRY = HERE.parent
EXACT = REGISTRY / "exact_api_closure"
AS_OF = "2026-08-26"

EXECUTION_WAVES = [
    ("wave0_boundary_and_shapes", ["candidate_data_shapes"]),
    ("wave1_shared_foundations", ["shared_semantic_foundations", "representation_codec"]),
    ("wave2_execution_spine", ["connector_protocol", "messaging_coordination", "persistence_lakehouse", "pipeline_dataflow", "query_compilation_execution", "runtime_resource_control"]),
    ("wave3_assurance_and_control", ["governance_metadata_ontology", "lineage_provenance_evidence", "quality_reconciliation", "security_privacy_trust"]),
    ("wave4_analytical_methods", ["analytical_method_kernels", "experimentation_lifecycle", "forecasting_lifecycle", "geospatial_analytics", "operations_research", "predictive_analytics", "semantic_metrics_formulas"]),
    ("wave5_consumption_and_commercial", ["consumption_bi_visualization", "platform_commercial_support"]),
    ("wave6_optional_model_extensions", ["optional_model_agent_extensions"]),
]


def rows(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


TRUTH_PLANES = [
    "product_truth", "domain_truth", "semantic_truth", "human_process_truth",
    "data_intelligence_truth", "authority_trust_truth", "security_safety_truth",
    "production_truth", "ecosystem_truth", "change_delivery_truth", "rust_build_truth",
    "migration_proof_truth",
]


COMMON_SLOTS = [
    "sovereign_question", "negative_mission", "semantic_owner", "inside_boundary",
    "outside_boundary", "ubiquitous_language", "identity_and_equality", "time_model",
    "authority_model", "decisions_and_configuration", "invariants", "refusal_catalog",
    "refusal_precedence", "finite_bounds", "dependency_direction", "compatibility",
    "evidence_claims", "negative_twins", "conformance_oracles", "removal_seam",
]


def archetype(
    short: str,
    question: str,
    type_roles: list[str],
    operation_roles: list[str],
    laws: list[str],
    refusal_roles: list[str],
    oracle_roles: list[str],
    permitted_classes: list[str],
    permitted_effects: list[str],
) -> dict[str, Any]:
    return {
        "record_kind": "contract_archetype",
        "archetype_id": f"archetype.contract.{short}",
        "edition": 1,
        "status": "STRUCTURAL_PATTERN_NOT_DOMAIN_AUTHORITY",
        "structural_question": question,
        "required_type_roles": type_roles,
        "required_operation_roles": operation_roles,
        "inherited_structural_laws": laws,
        "required_refusal_roles": refusal_roles,
        "required_oracle_roles": oracle_roles,
        "permitted_library_classes": permitted_classes,
        "permitted_effect_boundaries": permitted_effects,
        "owner_authored_slots": COMMON_SLOTS,
        "generation_law": "The archetype generates obligations and test slots only; it never supplies domain vocabulary, authority, semantic laws, defaults or acceptance.",
    }


ARCHETYPES = [
    archetype("semantic_algebra", "Which immutable meanings and total operations form one algebra?",
        ["identity", "edition", "input", "value", "relation", "result", "refusal", "resource_budget"],
        ["construct", "compare", "compose", "validate", "explain", "diff"],
        ["operations are total over typed outcomes", "equality and identity are explicit", "no ambient effects or hidden defaults"],
        ["invalid_identity", "unsupported_edition", "undefined_operation", "incomparable", "resource_exhausted"],
        ["algebraic_properties", "boundary_negative_twins", "differential_implementation"],
        ["semantic_pure"], ["pure_no_io"]),
    archetype("value_type_system", "Which carrier values are valid and what does equality mean?",
        ["raw_carrier", "validated_value", "identity", "edition", "normal_form", "refusal"],
        ["construct", "validate", "compare", "canonicalize", "project"],
        ["invalid states are unrepresentable after construction", "representation equality is not automatically semantic equality"],
        ["invalid_carrier", "out_of_domain", "ambiguous_equality", "unsupported_edition"],
        ["constructor_boundaries", "equality_properties", "roundtrip_fixtures"],
        ["semantic_pure"], ["pure_no_io"]),
    archetype("lifecycle_reducer", "Which immutable events permit which state transitions?",
        ["aggregate_id", "revision", "state", "command", "event", "transition", "refusal"],
        ["decide", "evolve", "validate_transition", "fold", "diff", "explain"],
        ["illegal transitions refuse", "events are facts and commands are requests", "replay is deterministic for an exact edition"],
        ["stale_revision", "illegal_transition", "duplicate_event", "history_incomplete"],
        ["state_model", "event_replay", "concurrency_negative_twins"],
        ["semantic_pure", "policy_pure"], ["pure_no_io", "pure_effect_intents"]),
    archetype("policy_evaluator", "Does an exact subject satisfy an exact policy edition under supplied witnesses?",
        ["policy_edition", "subject", "context", "witness_set", "decision", "explanation", "refusal"],
        ["validate_policy", "evaluate", "explain", "compare_editions", "recheck"],
        ["policy selection is external", "indeterminate is distinct from deny", "no authority or observation is invented"],
        ["policy_missing", "witness_missing", "policy_conflict", "indeterminate", "authority_unresolved"],
        ["decision_tables", "precedence_model", "policy_mutation", "negative_twins"],
        ["policy_pure"], ["pure_no_io", "pure_effect_intents"]),
    archetype("specification_predicate", "Which reusable predicates describe admissible subjects?",
        ["specification", "subject", "evaluation", "composition", "explanation", "refusal"],
        ["evaluate", "and", "or", "not", "implies", "explain"],
        ["predicate composition preserves partiality", "failure to prove satisfaction is not proof of negation"],
        ["subject_unresolved", "predicate_undefined", "composition_invalid", "budget_exhausted"],
        ["predicate_algebra", "three_valued_logic", "composition_properties"],
        ["semantic_pure", "policy_pure"], ["pure_no_io"]),
    archetype("conformance_oracle", "Does an artifact or behavior conform to an exact profile?",
        ["profile_edition", "subject", "witness", "finding", "report", "coverage", "refusal"],
        ["validate_profile", "check", "aggregate_findings", "certify_coverage", "explain"],
        ["validation does not publish accept or authorize", "pass is scoped to exact profile evidence and coverage"],
        ["profile_invalid", "witness_missing", "coverage_incomplete", "resource_exhausted"],
        ["positive_fixtures", "negative_fixtures", "mutation_tests", "cross_implementation"],
        ["test_oracle", "algorithm_pure"], ["pure_no_io"]),
    archetype("parser_decoder", "Can an external representation be decoded without silent meaning or information loss?",
        ["source_edition", "input_bytes", "syntax_tree", "decoded_value", "diagnostic", "loss_report", "refusal"],
        ["detect_edition", "parse", "decode", "validate", "explain_loss"],
        ["parse success is not semantic validity", "unknown material is preserved or refused", "resource bounds are explicit"],
        ["malformed_input", "unsupported_edition", "ambiguous_decode", "limit_exceeded"],
        ["malformed_corpus", "fuzz", "resource_bombs", "roundtrip"],
        ["algorithm_pure", "provider_adapter"], ["pure_no_io", "effectful_runtime"]),
    archetype("encoder_serializer", "Can a semantic value be encoded under an exact external edition and loss policy?",
        ["target_edition", "semantic_value", "encoded_representation", "loss_report", "refusal"],
        ["validate_target", "encode", "serialize", "measure_loss", "roundtrip_check"],
        ["serialization identity is distinct from semantic identity", "loss is explicit and authority-scoped"],
        ["unrepresentable", "loss_unaccepted", "unsupported_edition", "resource_exhausted"],
        ["golden_bytes", "roundtrip_properties", "cross_encoder_differential"],
        ["algorithm_pure", "provider_adapter"], ["pure_no_io", "effectful_runtime"]),
    archetype("canonicalizer_normalizer", "Which deterministic normal form represents an exact equivalence domain?",
        ["input", "profile_edition", "normal_form", "mapping", "complexity_budget", "refusal"],
        ["validate_profile", "normalize", "verify_normal_form", "compare", "explain_mapping"],
        ["canonicalization is scoped to one equivalence relation", "normal form does not prove truth"],
        ["profile_unsupported", "poison_input", "nontermination_risk", "budget_exhausted"],
        ["idempotence", "equivalence_properties", "poison_inputs", "differential"],
        ["algorithm_pure", "semantic_pure"], ["pure_no_io"]),
    archetype("planner_compiler_pass", "How is declared intent lowered into a typed immutable plan without executing it?",
        ["intent", "input_contract", "decision_edition", "logical_plan", "diagnostic", "residual", "refusal"],
        ["validate_inputs", "analyze", "lower", "verify_plan", "explain", "diff"],
        ["compile success is not execution", "every loss residual and unresolved binding remains explicit", "no provider selected by name"],
        ["input_unbound", "decision_missing", "lowering_loss", "plan_invalid", "capability_unsatisfied"],
        ["golden_plans", "semantic_differential", "mutation", "metamorphic"],
        ["semantic_pure", "algorithm_pure", "target_backend"], ["pure_no_io"]),
    archetype("optimizer_solver", "Which feasible or best-supported result follows from an exact model and objective policy?",
        ["model", "objective", "constraint_set", "solver_profile", "solution", "bound", "certificate", "refusal"],
        ["validate_model", "solve", "verify_feasibility", "verify_bound", "explain_solution"],
        ["feasible is not optimal", "unknown is not infeasible", "solver output requires independent verification"],
        ["model_invalid", "infeasible", "unbounded", "unknown", "timeout", "certificate_invalid"],
        ["known_optima", "independent_checker", "metamorphic", "benchmark"],
        ["algorithm_pure", "runtime_mechanism", "provider_adapter"], ["pure_no_io", "effectful_runtime"]),
    archetype("effect_port", "Which effect may be requested and which observations can establish its outcome?",
        ["intent_id", "intent", "attempt_id", "observation", "completion_state", "receipt", "refusal"],
        ["form_intent", "validate_attempt", "classify_observation", "reconcile_unknown", "seal_receipt"],
        ["intent is not effect", "acknowledgement is not accepted outcome", "unknown completion reconciles before retry"],
        ["authority_missing", "attempt_duplicate", "observation_unbound", "unknown_completion", "receipt_incomplete"],
        ["fault_injection", "unknown_completion_model", "idempotency_boundaries"],
        ["effect_port_contract", "policy_pure", "semantic_pure"], ["pure_effect_intents"]),
    archetype("runtime_mechanism", "How is an explicit runtime contract executed under bounded resources and failures?",
        ["request", "configuration_edition", "runtime_state", "attempt", "outcome", "observation", "refusal"],
        ["prepare", "start", "poll", "cancel", "recover", "close"],
        ["effects are explicit", "cancellation and partial completion are total states", "resource exhaustion never weakens semantics silently"],
        ["not_admitted", "cancelled", "timeout", "overloaded", "partial_failure", "provider_failure"],
        ["failure_injection", "race_model", "overload", "recovery"],
        ["runtime_mechanism"], ["effectful_runtime", "ffi_boundary"]),
    archetype("provider_adapter", "How is one provider edition translated behind an anti-corruption boundary?",
        ["provider_edition", "canonical_request", "provider_request", "provider_response", "canonical_observation", "loss_report", "refusal"],
        ["negotiate_capability", "encode_request", "execute", "decode_response", "translate_error", "reconcile"],
        ["provider vocabulary never owns canonical semantics", "unsupported behavior refuses", "all translation loss is explicit"],
        ["capability_stale", "translation_loss", "provider_error", "protocol_violation", "unknown_completion"],
        ["wire_fixtures", "fault_injection", "provider_differential", "version_skew"],
        ["provider_adapter"], ["effectful_runtime", "ffi_boundary"]),
    archetype("registry_resolver", "How are versioned identities registered and resolved without confusing names with meanings?",
        ["registry_edition", "identity", "query", "registration", "resolution", "conflict", "refusal"],
        ["register", "resolve", "compare_editions", "detect_conflict", "explain"],
        ["name equality is not identity equality", "resolution is scoped by authority edition and time", "conflicts are retained"],
        ["identity_ambiguous", "edition_missing", "conflict", "authority_missing", "not_found"],
        ["identity_negative_twins", "version_skew", "conflict_model"],
        ["semantic_pure", "runtime_mechanism", "provider_adapter"], ["pure_no_io", "pure_effect_intents", "effectful_runtime"]),
    archetype("repository_query_port", "Which aggregate or projection can be loaded or queried under explicit consistency?",
        ["query", "consistency_requirement", "cut", "page", "result", "continuation", "refusal"],
        ["validate_query", "load", "query", "continue", "observe_consistency"],
        ["repository is per aggregate root", "read model is not aggregate authority", "continuation tokens are scoped and opaque"],
        ["not_found", "stale_cut", "consistency_unavailable", "continuation_invalid", "resource_exhausted"],
        ["consistency_fixtures", "pagination_properties", "concurrent_change_model"],
        ["effect_port_contract", "runtime_mechanism", "provider_adapter"], ["pure_effect_intents", "effectful_runtime"]),
    archetype("target_backend", "How is a verified logical plan lowered to one exact target capability profile?",
        ["logical_plan", "target_profile", "target_plan", "artifact", "diagnostic", "loss_report", "refusal"],
        ["validate_target", "lower", "verify_artifact", "explain_loss", "diff"],
        ["target lowering does not redefine source semantics", "unsupported capability refuses or emits an authorized degradation"],
        ["target_unsupported", "capability_missing", "lowering_loss", "artifact_invalid"],
        ["golden_artifacts", "target_differential", "capability_mutation"],
        ["target_backend", "generated_support"], ["pure_no_io", "generated_boundary"]),
    archetype("evidence_receipt_protocol", "Which exact evidence supports which scoped fact and what remains unproved?",
        ["subject_ref", "evidence_ref", "policy_edition", "assessment", "residual", "receipt_intent", "receipt", "refusal"],
        ["bind_evidence", "assess", "form_receipt_intent", "verify_receipt", "invalidate", "explain"],
        ["evidence integrity is not truth", "receipt is not acceptance", "coverage gaps and defeaters remain explicit"],
        ["evidence_missing", "scope_mismatch", "coverage_unknown", "defeater_unresolved", "receipt_invalid"],
        ["claim_evidence_negative_twins", "coverage_model", "tamper_fixtures", "invalidation_model"],
        ["semantic_pure", "policy_pure", "test_oracle"], ["pure_no_io", "pure_effect_intents"]),
    archetype("boundary_unresolved", "Does this candidate own any coherent independently replaceable contract?",
        ["candidate_ref", "owner_claim", "responsibility_claim", "boundary_decision"],
        ["falsify_boundary", "compare_neighbors", "adjudicate"],
        ["no API may be generated before boundary adjudication", "package vendor and vocabulary count are not boundaries"],
        ["owner_unresolved", "cohesion_unproved", "overlap_unresolved"],
        ["neighbor_collision", "unrelated_vertical_test", "removal_test"],
        ["candidate_unclassified"], ["unresolved_refuse"]),
]


ARCHETYPE_BY_ID = {row["archetype_id"]: row for row in ARCHETYPES}
BASE_ARCHETYPE = {
    "semantic_pure": "semantic_algebra", "algorithm_pure": "semantic_algebra",
    "policy_pure": "policy_evaluator", "test_oracle": "conformance_oracle",
    "effect_port_contract": "effect_port", "runtime_mechanism": "runtime_mechanism",
    "provider_adapter": "provider_adapter", "target_backend": "target_backend",
    "generated_support": "target_backend", "candidate_unclassified": "boundary_unresolved",
}
KEYWORD_ARCHETYPES = [
    (r"\b(parser|decoder|reader)\b", "parser_decoder"),
    (r"\b(encoder|serializer|codec|compression)\b", "encoder_serializer"),
    (r"\b(canonical|canonicalizer|normalizer)\b", "canonicalizer_normalizer"),
    (r"\b(optimizer|optimiser|solver|optimization)\b", "optimizer_solver"),
    (r"\b(compiler|planner|planning|lowering)\b", "planner_compiler_pass"),
    (r"\b(lifecycle|reducer|state-machine|state_machine)\b", "lifecycle_reducer"),
    (r"\b(registry|resolver|catalog)\b", "registry_resolver"),
    (r"\b(repository|store|query-port)\b", "repository_query_port"),
    (r"\b(receipt|evidence|attestation)\b", "evidence_receipt_protocol"),
]


def propose_archetypes(library: dict[str, Any]) -> tuple[list[str], str, list[str]]:
    # Names can refine a structural class, but operation vocabulary is deliberately excluded:
    # a semantic algebra that offers `normalize_event` is not thereby a canonicalizer boundary.
    text = (library["library_id"] + " " + library["name"]).lower().replace(".", " ").replace("_", "-")
    base = BASE_ARCHETYPE[library["library_class"]]
    refinements: list[tuple[str, str]] = []
    for pattern, short in KEYWORD_ARCHETYPES:
        if re.search(pattern, text):
            refinements.append((short, f"name_pattern:{pattern}"))
    primary = base
    primary_reason = f"library_class:{library['library_class']}"
    # Runtime/provider/port/backend classes already express the dominant executable boundary.
    # Pure semantic/algorithm candidates may be refined by a strong boundary noun. Policy remains
    # policy-first except for an explicit lifecycle/reducer.
    if library["library_class"] in {"semantic_pure", "algorithm_pure"} and refinements:
        primary, primary_reason = refinements[0]
    elif library["library_class"] == "policy_pure":
        lifecycle = next((item for item in refinements if item[0] == "lifecycle_reducer"), None)
        if lifecycle:
            primary, primary_reason = lifecycle
    candidates: list[str] = [primary]
    reasons: list[str] = [primary_reason]
    for short, reason in refinements:
        if short != primary:
            candidates.append(short)
            reasons.append(reason)
    if library["effects"]["boundary"] == "pure_effect_intents":
        candidates.append("effect_port")
        reasons.append("effect_boundary:pure_effect_intents")
    if base != primary:
        candidates.append(base)
        reasons.append(f"library_class:{library['library_class']}")
    unique = []
    for short in candidates:
        ref = f"archetype.contract.{short}"
        if ref not in unique:
            unique.append(ref)
    confidence = "MECHANICAL_HIGH" if len(unique) == 1 else "HEURISTIC_REVIEW_REQUIRED"
    return unique, confidence, reasons


TOKEN_STOP = {
    "a", "an", "and", "any", "as", "by", "candidate", "coherent", "context", "contract",
    "core", "define", "for", "from", "in", "independently", "into", "laws", "library",
    "neutral", "of", "on", "operation", "operations", "or", "own", "provider", "pure",
    "invariants", "refusal", "refusals", "requirements", "semantic", "semantics", "the", "to",
    "transformations", "typed", "types", "under", "validation", "vocabulary", "with", "without",
}


def boundary_tokens(library: dict[str, Any]) -> set[str]:
    text = " ".join([library["name"], *library["scope"]["responsibilities"]]).lower()
    return {token for token in re.findall(r"[a-z][a-z0-9]+", text) if len(token) >= 3 and token not in TOKEN_STOP}


def build() -> dict[str, Any]:
    queue = rows(EXACT / "closure-queue.jsonl")
    batches = rows(EXACT / "research-batches.jsonl")
    libraries = {row["library_id"]: row for row in rows(REGISTRY / "library-contributions.jsonl")}
    batch_by_library = {ref: batch for batch in batches for ref in batch["library_refs"]}

    family_members: dict[str, list[dict[str, Any]]] = defaultdict(list)
    proposals = []
    for item in queue:
        library = libraries[item["library_ref"]]
        batch = batch_by_library[item["library_ref"]]
        candidates, confidence, reasons = propose_archetypes(library)
        primary = ARCHETYPE_BY_ID[candidates[0]]
        proposal = {
            "record_kind": "library_contract_instance_proposal",
            "proposal_id": "proposal.contract-instance." + item["library_ref"].removeprefix("library."),
            "edition": 1,
            "status": "PROPOSAL_NOT_AUTHORITY_DOES_NOT_CLOSE_GAP",
            "library_ref": item["library_ref"],
            "family_id": f"constitution.family.{batch['research_family']}",
            "research_batch_ref": batch["batch_id"],
            "semantic_owner_refs": item["semantic_owner_refs"],
            "primary_archetype_proposal": candidates[0],
            "alternate_archetype_proposals": candidates[1:],
            "classification_confidence": confidence,
            "classification_reasons": reasons,
            "inherited_structural_obligations": {
                "type_roles": primary["required_type_roles"],
                "operation_roles": primary["required_operation_roles"],
                "structural_laws": primary["inherited_structural_laws"],
                "refusal_roles": primary["required_refusal_roles"],
                "oracle_roles": primary["required_oracle_roles"],
            },
            "owner_authored_slots": primary["owner_authored_slots"],
            "currently_missing_dimensions": item["placeholder_dimensions"],
            "boundary_disposition": "UNADJUDICATED",
            "allowed_dispositions": ["retain", "retain_but_narrow", "split", "merge", "rename", "replace", "retire"],
            "generation_prohibition": "No exact public name signature law refusal default or authority may be synthesized from this proposal.",
            "source_gap_ref": item["source_gap_ref"],
        }
        proposals.append(proposal)
        family_members[batch["research_family"]].append(proposal)

    constitutions = []
    for family, members in sorted(family_members.items()):
        batch_set = sorted({row["research_batch_ref"] for row in members})
        family_batches = [batch for batch in batches if batch["research_family"] == family]
        constitutions.append({
            "record_kind": "family_constitution_work_item",
            "family_id": f"constitution.family.{family}",
            "edition": 1,
            "status": "OWNER_RESEARCH_AND_ADJUDICATION_REQUIRED",
            "open_library_count": len(members),
            "research_batch_refs": batch_set,
            "semantic_owner_refs": sorted({ref for row in members for ref in row["semantic_owner_refs"]}),
            "required_truth_planes": TRUTH_PLANES,
            "required_constitution_sections": [
                "vision_and_negative_mission", "bounded_contexts_and_context_map", "ubiquitous_language",
                "identity_equality_and_canonicalization", "time_state_concurrency_and_idempotency",
                "authority_policy_and_refusal_precedence", "shared_value_types_and_semantic_relations",
                "dependency_direction_and_anti_corruption", "effects_intents_observations_and_receipts",
                "finite_resource_and_failure_laws", "compatibility_migration_and_evidence_invalidation",
                "primary_evidence_claims_counterexamples_and_conflicts", "negative_twins_and_conformance_oracles",
            ],
            "evidence_program": family_batches[0]["evidence_program"],
            "primary_evidence_seeds": family_batches[0]["primary_evidence_seeds"],
            "evidence_seed_status": "DISCOVERY_ONLY_NOT_ADOPTED_AUTHORITY",
            "constitution_laws": [
                "Shared carriers are imported by identity and edition; a family does not silently acquire their meaning.",
                "An archetype supplies structure only; every semantic name law default refusal and precedence remains owner-authored.",
                "A family constitution may close repeated decisions once but cannot erase library-specific exceptions.",
                "Conflicting primary sources are recorded and adjudicated rather than blended.",
                "No generated artifact establishes implementation qualification portability or product acceptance.",
            ],
            "completion_gate": "Every section has owner-authored machine-readable content, bounded primary evidence, collision tests, and explicit unresolved items; all member boundaries are adjudicated before API expansion.",
        })

    owner_groups: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for proposal in proposals:
        for owner in proposal["semantic_owner_refs"]:
            owner_groups[(proposal["family_id"], owner)].append(proposal)
    clusters = []
    for index, ((family_id, owner), members) in enumerate(sorted(owner_groups.items()), 1):
        refs = sorted(row["library_ref"] for row in members)
        clusters.append({
            "record_kind": "boundary_falsification_cluster",
            "cluster_id": f"cluster.boundary-owner.{index:04d}",
            "edition": 1,
            "status": "UNADJUDICATED",
            "family_id": family_id,
            "semantic_owner_ref": owner,
            "library_refs": refs,
            "collision_risk": "HIGH_SAME_OWNER_MULTIPLE_CANDIDATES" if len(refs) > 1 else "SINGLETON_STILL_REQUIRES_REMOVAL_TEST",
            "required_tests": [
                "one coherent sovereign question per retained boundary",
                "responsibility overlap and law overlap matrix",
                "independent removal and substitution test",
                "dependency cycle and shared-type ownership test",
                "two unrelated vertical composition test",
                "package vendor service and vocabulary-count boundary rejection",
            ],
            "closure_law": "Every member receives an explicit retain/narrow/split/merge/rename/replace/retire decision with no compatibility alias for retired meanings.",
        })

    cross_owner_collisions = []
    proposals_by_family: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for proposal in proposals:
        proposals_by_family[proposal["family_id"]].append(proposal)
    for family_id, members in sorted(proposals_by_family.items()):
        for left_index, left in enumerate(sorted(members, key=lambda row: row["library_ref"])):
            left_owner = tuple(left["semantic_owner_refs"])
            left_tokens = boundary_tokens(libraries[left["library_ref"]])
            for right in sorted(members, key=lambda row: row["library_ref"])[left_index + 1:]:
                if tuple(right["semantic_owner_refs"]) == left_owner:
                    continue
                right_tokens = boundary_tokens(libraries[right["library_ref"]])
                shared = sorted(left_tokens & right_tokens)
                union = left_tokens | right_tokens
                score = len(shared) / len(union) if union else 0.0
                if len(shared) < 2 or score < 0.45:
                    continue
                pair_digest = hashlib.sha256((left["library_ref"] + "\0" + right["library_ref"]).encode()).hexdigest()[:16]
                cross_owner_collisions.append({
                    "record_kind": "cross_owner_boundary_collision_candidate",
                    "collision_id": f"collision.boundary.{pair_digest}",
                    "edition": 1,
                    "status": "LEXICAL_SIGNAL_REVIEW_REQUIRED_NOT_DUPLICATE_PROOF",
                    "family_id": family_id,
                    "left_library_ref": left["library_ref"],
                    "right_library_ref": right["library_ref"],
                    "left_owner_refs": left["semantic_owner_refs"],
                    "right_owner_refs": right["semantic_owner_refs"],
                    "shared_responsibility_tokens": shared,
                    "jaccard_similarity": round(score, 6),
                    "required_adjudication": [
                        "compare sovereign questions and negative missions",
                        "compare owned meanings laws refusals and lifecycle",
                        "determine whether owner split is legitimate published-language translation or accidental duplication",
                        "record merge split rename retain-narrow or explicit-coexistence decision",
                    ],
                    "non_inference": "Lexical similarity is a discovery signal only and proves neither duplicate meaning nor a valid merge.",
                })

    work_packages = []
    for batch in batches:
        batch_proposals = [row for row in proposals if row["research_batch_ref"] == batch["batch_id"]]
        work_packages.append({
            "record_kind": "family_lane_contract_work_package",
            "work_package_id": batch["batch_id"].replace("batch.exact-api", "work-package.contract"),
            "edition": 1,
            "status": "BOUNDARY_FIRST_THEN_GENERATE",
            "family_id": f"constitution.family.{batch['research_family']}",
            "research_batch_ref": batch["batch_id"],
            "library_instance_proposal_refs": [row["proposal_id"] for row in batch_proposals],
            "item_count": len(batch_proposals),
            "execution_dag": [
                "adjudicate_boundary_clusters", "complete_family_constitution", "bind_bounded_evidence_claims",
                "owner_fill_library_instance_slots", "expand_structural_archetype_obligations",
                "run_family_collision_and_dependency_tests", "run_unrelated_vertical_compositions",
                "publish_source_contracts", "regenerate_canonical_registry", "verify_exact_gaps_removed",
            ],
            "parallelism_law": "Libraries with disjoint semantic owners and dependency closures may proceed concurrently after their family constitution edition is frozen for the batch.",
            "batch_acceptance": "Every listed library is explicitly retired/replaced or has an owner-published exact source contract; generated proposals alone close nothing.",
        })

    package_by_family: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for package in work_packages:
        package_by_family[package["family_id"].removeprefix("constitution.family.")].append(package)
    execution_waves = []
    prior_wave_refs: list[str] = []
    for wave_index, (wave_name, families) in enumerate(EXECUTION_WAVES):
        wave_ref = f"execution-wave.contract-generation.{wave_index}"
        package_refs = sorted(
            package["work_package_id"]
            for family in families
            for package in package_by_family[family]
        )
        execution_waves.append({
            "record_kind": "contract_generation_execution_wave",
            "wave_id": wave_ref,
            "edition": 1,
            "status": "PLANNED_INCOMPLETE",
            "name": wave_name,
            "research_families": families,
            "work_package_refs": package_refs,
            "depends_on_wave_refs": prior_wave_refs[-1:] if prior_wave_refs else [],
            "global_entry_gates": [
                "relevant owner-scoped boundary clusters adjudicated",
                "relevant cross-owner collision signals adjudicated or explicitly dismissed with rationale",
                "upstream family constitution editions frozen for this wave",
                "no unresolved dependency identity or cycle hidden by generation",
            ],
            "parallelism": "Work packages inside the wave may run concurrently only when their semantic owners and dependency closures are disjoint.",
            "exit_gate": "Every work package is owner-published or explicitly retired/replaced; downstream waves consume only editioned source contracts and unresolved residuals.",
        })
        prior_wave_refs.append(wave_ref)

    return {
        "archetypes": sorted(ARCHETYPES, key=lambda row: row["archetype_id"]),
        "constitutions": constitutions,
        "proposals": sorted(proposals, key=lambda row: row["library_ref"]),
        "clusters": clusters,
        "cross_owner_collisions": sorted(cross_owner_collisions, key=lambda row: (-row["jaccard_similarity"], row["collision_id"])),
        "work_packages": sorted(work_packages, key=lambda row: row["work_package_id"]),
        "execution_waves": execution_waves,
    }


def outputs() -> dict[str, str]:
    built = build()
    files = {
        "contract-archetypes.jsonl": "".join(canonical(row) + "\n" for row in built["archetypes"]),
        "family-constitutions.jsonl": "".join(canonical(row) + "\n" for row in built["constitutions"]),
        "library-instance-proposals.jsonl": "".join(canonical(row) + "\n" for row in built["proposals"]),
        "boundary-falsification-clusters.jsonl": "".join(canonical(row) + "\n" for row in built["clusters"]),
        "cross-owner-collision-candidates.jsonl": "".join(canonical(row) + "\n" for row in built["cross_owner_collisions"]),
        "work-packages.jsonl": "".join(canonical(row) + "\n" for row in built["work_packages"]),
        "execution-waves.jsonl": "".join(canonical(row) + "\n" for row in built["execution_waves"]),
    }
    archetypes = Counter(row["primary_archetype_proposal"] for row in built["proposals"])
    confidence = Counter(row["classification_confidence"] for row in built["proposals"])
    summary = {
        "program_id": "program.bulk-contract-generation.v1", "edition": 1, "as_of": AS_OF,
        "status": "ACTIVE_INCOMPLETE", "completion_claim": False,
        "counts": {key: len(value) for key, value in built.items()},
        "proposal_counts_by_primary_archetype": dict(sorted(archetypes.items())),
        "proposal_counts_by_confidence": dict(sorted(confidence.items())),
        "laws": [
            "Every open exact-API gap has exactly one non-authoritative library-instance proposal.",
            "Every proposal belongs to exactly one family constitution and one family-lane work package.",
            "Archetypes generate structural obligations only and never domain truth.",
            "Boundary adjudication precedes API generation.",
            "Only owner-published source projections can remove canonical exact-API gaps.",
        ],
    }
    files["summary.json"] = json.dumps(summary, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
    manifest_files = {
        name: {"sha256": hashlib.sha256(text.encode()).hexdigest(), "bytes": len(text.encode())}
        for name, text in files.items()
    }
    files["manifest.json"] = json.dumps({
        "manifest_id": "manifest.bulk-contract-generation.v1", "as_of": AS_OF,
        "files": manifest_files,
    }, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
    return files


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    stale = []
    for name, text in outputs().items():
        path = HERE / name
        if args.check:
            if not path.is_file() or path.read_text(encoding="utf-8") != text:
                stale.append(name)
        else:
            path.write_text(text, encoding="utf-8")
    if stale:
        print("STALE " + ", ".join(stale))
        return 1
    built = build()
    print(f"{'CHECK' if args.check else 'BUILD'} PASS bulk contract program: {len(built['archetypes'])} archetypes, {len(built['constitutions'])} families, {len(built['proposals'])} proposals, {len(built['clusters'])} owner clusters, {len(built['cross_owner_collisions'])} cross-owner signals, {len(built['work_packages'])} work packages in {len(built['execution_waves'])} waves")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
