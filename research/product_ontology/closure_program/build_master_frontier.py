#!/usr/bin/env python3
"""Build the current machine-readable closure frontier from committed authority corpora."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_jsonl(path: Path, rows: list[dict]):
    path.write_text("".join(json.dumps(r, sort_keys=True) + "\n" for r in rows), encoding="utf-8")


def main() -> int:
    readiness = read_json(ROOT / "research/product_ontology/dossier_readiness/summary.json")
    qualification = read_json(ROOT / "research/product_ontology/qualification_program/effective-summary.json")
    industries = read_json(ROOT / "research/domain_atlas/industries/integration-audit.json")
    industry_effective = read_json(ROOT / "research/domain_atlas/industries/canonical-reference-effective-summary.json")
    industry_review = read_json(ROOT / "research/domain_atlas/industries/canonical-reference-machine-review-summary.json")
    context_map = read_json(ROOT / "research/domain_atlas/context_map/manifest.json")
    source_systems = read_json(ROOT / "research/domain_atlas/universes/source_systems/coverage-report.json")
    data_shapes = read_json(ROOT / "research/domain_atlas/universes/data_shapes/coverage-report.json")
    providers = read_json(ROOT / "research/domain_atlas/compiler/provider_target_registry/manifest.json")
    methods = read_json(ROOT / "research/product_ontology/adjudications/analytical_methods/manifest.json")
    horizontal_audit = [json.loads(x) for x in (ROOT / "research/analytics_landscape/product_families/consolidation-hardening-audit.jsonl").read_text(encoding="utf-8").splitlines() if x.strip()]
    ownership = read_json(ROOT / "research/domain_atlas/ownership-ambiguities.json")
    evidence_governance = read_json(ROOT / "research/analytics_landscape/product_families/evidence-governance-summary.json")
    boundary_falsification = read_json(ROOT / "research/product_ontology/dossier_readiness/product-boundary-falsification-summary.json")
    contract_scopes = read_json(ROOT / "research/product_ontology/qualification_program/contract-scope-summary.json")
    canonical_refs = read_json(ROOT / "research/domain_atlas/industries/canonical-reference-effective-summary.json")
    source_occurrences = read_json(ROOT / "research/domain_atlas/universes/source_systems/occurrence-registry-summary.json")
    source_topology = read_json(ROOT / "research/domain_atlas/universes/source_systems/source-acquisition-topology.json")
    source_reference_chain = read_json(ROOT / "research/domain_atlas/universes/source_systems/source-acquisition-reference-summary.json")
    effective_shape_gaps = read_json(ROOT / "research/domain_atlas/universes/data_shapes/effective-gap-summary.json")
    synthesis = read_json(ROOT / "research/product_ontology/solution_synthesis_architecture/summary.json")
    human_work = read_json(ROOT / "research/domain_atlas/universes/human_work_review_adjudication/manifest.json")
    effect_boundary = read_json(ROOT / "research/domain_atlas/compiler/library_registry/contract_generation/semantic_decomposition/effect_boundary_coordinate_ontology/summary.json")
    vertical_acceptance = read_json(ROOT / "research/domain_atlas/compiler/library_registry/contract_generation/semantic_decomposition/p8_vertical_acceptance_tensor/summary.json")
    change_intelligence = read_json(ROOT / "research/domain_atlas/ecosystem/change_intelligence/manifest.json")
    coverage_planes = [json.loads(x) for x in (ROOT / "research/domain_atlas/coverage-planes.jsonl").read_text(encoding="utf-8").splitlines() if x.strip()]

    vertical_cases = sum(p["cases"] for p in industries["packs"])
    vertical_shapes = sum(p["data_shape_needs"] for p in industries["packs"])
    vertical_sources = sum(p["source_system_needs"] for p in industries["packs"])
    vertical_evidence = sum(p["sources"] for p in industries["packs"])

    batches = [
        {
            "batch_id": "B00_TRUTH_CONVERGENCE",
            "depends_on": [],
            "scope": "Make all top-level status projections consume current committed authority artifacts and reject stale downstream state.",
            "current": {"retained_products": readiness["retained_product_count"], "effective_vacancies": qualification["effective_evidence_vacancy_count"], "stale_contract_blocks": 0},
            "exit_condition": "No authoritative summary contradicts dossier-readiness or effective qualification state; every derived status is digest-bound or validator-recomputed.",
            "status": "PARTIAL_ACTIVE",
            "authority_refs": ["research/product_ontology/dossier_readiness/summary.json", "research/product_ontology/qualification_program/effective-summary.json"],
        },
        {
            "batch_id": "B01_SOURCE_AUTHORITY",
            "depends_on": ["B00_TRUTH_CONVERGENCE"],
            "scope": "Named source/schema authority decisions for the 23 prepared source-family payloads and independent verification receipts.",
            "current": {"ratifier_ready_payloads": 23, "ratified": 0},
            "exit_condition": "Each source family has accept/modify/reject authority receipt plus independent verifier receipt; no agent assertion substitutes.",
            "status": "AWAITING_HUMAN_AUTHORITY",
            "authority_refs": ["research/product_ontology/closure_program/source-authority-ratification-batch.jsonl"],
        },
        {
            "batch_id": "B02_SEMANTIC_OWNER_UNIQUENESS",
            "depends_on": ["B01_SOURCE_AUTHORITY"],
            "scope": "Adjudicate semantic-owner collisions and prove exactly-one sovereign owner or explicit exception.",
            "current": {"legacy_ambiguities": len(ownership["ambiguities"]), "context_candidates": context_map["counts"]["contexts"], "context_relations": context_map["counts"]["relations"]},
            "exit_condition": "Every durable meaning, artifact, command, transition and decision has one sovereign owner or an editioned exception with authority and loss law.",
            "status": "OPEN",
            "authority_refs": ["research/domain_atlas/ownership-ambiguities.json", "research/domain_atlas/context_map/"],
        },
        {
            "batch_id": "B03_CONTEXT_MAP_RATIFICATION",
            "depends_on": ["B02_SEMANTIC_OWNER_UNIQUENESS"],
            "scope": "Ratify/narrow the existing global context map rather than treating it as absent.",
            "current": {"contexts": context_map["counts"]["contexts"], "relations": context_map["counts"]["relations"], "acl_decisions": context_map["counts"]["acl_decisions"], "explicit_gaps": context_map["counts"]["gaps"]},
            "exit_condition": "Every retained context and relation has owner, translation/loss/refusal semantics and ratification disposition; remaining open-world extension points remain explicit.",
            "status": "OPEN",
            "authority_refs": ["research/domain_atlas/context_map/manifest.json"],
        },
        {
            "batch_id": "B04_HORIZONTAL_EVIDENCE_GOVERNANCE",
            "depends_on": ["B00_TRUTH_CONVERGENCE"],
            "scope": "Normalize organization/product identity, bind evidence to falsifiable claims, classify evidence roles, and preserve candidate status.",
            "current": {"audit_requirements": len(horizontal_audit), "open_or_partial": sum(r["status"] != "SATISFIED_ENFORCED" for r in horizontal_audit), "organization_family_membership_claims": evidence_governance["organization_family_membership_claim_count"], "weak_membership_claims": evidence_governance["weak_membership_claim_count"], "organization_identities": evidence_governance["unique_organization_count"], "identity_relationships_fully_adjudicated": evidence_governance["identity_relationships_fully_adjudicated_count"]},
            "exit_condition": "Every company/product-family membership is claim-bound to exact evidence; research refs have controlled roles; acquisition/rename/project identities are normalized; validator enforces all rules.",
            "status": "OPEN",
            "authority_refs": ["research/analytics_landscape/product_families/consolidation-hardening-audit.jsonl"],
        },
        {
            "batch_id": "B05_PRODUCT_BOUNDARY_FALSIFICATION",
            "depends_on": ["B03_CONTEXT_MAP_RATIFICATION", "B04_HORIZONTAL_EVIDENCE_GOVERNANCE"],
            "scope": "Challenge every retained product boundary with merge/split/demotion/rehome/reject falsifiers and independent adoption/lifecycle evidence.",
            "current": {"retained_products": readiness["retained_product_count"], "complete_candidate_ddd": readiness["full_product_specific_ddd_count"], "falsification_contracts": boundary_falsification["falsification_contract_count"], "structural_falsification_gaps": boundary_falsification["structural_falsification_gap_count"], "independent_adoption_evidence_complete": boundary_falsification["product_specific_independent_adoption_evidence_complete_count"], "economic_exit_evidence_complete": boundary_falsification["product_specific_economic_exit_evidence_complete_count"], "ratified_boundaries": boundary_falsification["ratified_boundary_count"]},
            "exit_condition": "Every retained product has explicit merge falsifier, independent adoption/lifecycle/economic/exit evidence, and non-collapse laws; rejected/demoted candidates are crosswalked.",
            "status": "OPEN",
            "authority_refs": ["research/product_ontology/dossier_readiness/", "research/product_ontology/adjudications/"],
        },
        {
            "batch_id": "B06_LIBRARY_CONTRACT_AUTHORITY",
            "depends_on": ["B05_PRODUCT_BOUNDARY_FALSIFICATION"],
            "scope": "Ratify exact library contracts, compatibility/evolution rules, operations, decisions, refusals and compiler bindings.",
            "current": {"qualification_subjects": qualification["library_qualification_subject_count"], "exact_semantic_contract_scopes": contract_scopes["semantic_contract_scope_count"], "shared_semantic_contract_scopes": contract_scopes["shared_semantic_contract_scope_count"], "ratified_contract_scopes": contract_scopes["ratified_contract_scope_count"], "open_structural_compiler_gaps": readiness["open_structural_compiler_gap_count"], "analytical_method_library_contracts": methods["counts"]["library_contract"]},
            "exit_condition": "All retained product libraries have editioned law authority, exact compiler projection and no unresolved semantic contract ambiguity.",
            "status": "OPEN",
            "authority_refs": ["research/product_ontology/qualification_program/library-qualification-subjects.jsonl"],
        },
        {
            "batch_id": "B07_INDUSTRY_CANONICAL_REFERENCE_CLOSURE",
            "depends_on": ["B03_CONTEXT_MAP_RATIFICATION", "B06_LIBRARY_CONTRACT_AUTHORITY"],
            "scope": "Resolve industry/subindustry, method, operation, source-class and data-shape references for all existing analytical cases.",
            "current": {"industry_packs": industries["pack_count"], "analytical_cases": vertical_cases, "evidence_sources": vertical_evidence, "raw_review_queue_records": industry_effective["raw_queue_records"], "research_resolved_candidate_records": industry_effective["research_resolved_candidate_records"], "effective_open_review_records": industry_effective["remaining_open_research_records"], "unresolved_industry_refs": industry_effective["other_reference_frontiers_unchanged"]["industry_or_subindustry"], "unresolved_method_refs": industry_effective["method_reference_frontier"]["remaining_open_research_distinct"], "unresolved_operation_refs": industry_effective["other_reference_frontiers_unchanged"]["typed_operation"], "unresolved_source_class_refs": industry_effective["other_reference_frontiers_unchanged"]["source_system_class"], "machine_review_batches": industry_review["review_batch_count"], "machine_exact_alias_review_candidates": industry_review["source_candidate_records"], "machine_exact_alias_candidate_occurrences": industry_review["source_candidate_occurrences"], "data_shape_needs": vertical_shapes, "source_system_needs": vertical_sources},
            "exit_condition": "Every analytical case resolves to canonical industry, method, typed operation, source-system class and data-shape identities or emits a typed extension gap without silent coercion.",
            "status": "OPEN_HIGH_LEVERAGE",
            "authority_refs": ["research/domain_atlas/industries/integration-audit.json", "research/domain_atlas/industries/canonical-reference-effective-summary.json", "research/domain_atlas/industries/canonical-reference-machine-review-summary.json", "research/domain_atlas/industries/canonical-reference-review-queue.jsonl"],
        },
        {
            "batch_id": "B08_SOURCE_SYSTEM_AND_OCCURRENCE_CLOSURE",
            "depends_on": ["B07_INDUSTRY_CANONICAL_REFERENCE_CLOSURE"],
            "scope": "Bind vertical source needs to the 171-class open-world source universe, then add real source occurrences and connector adoption/exit evidence.",
            "current": {"source_classes": source_systems["class_records"], "source_families": len(source_systems["families"]), "primary_evidence_records": source_systems["primary_evidence_records"], "source_acquisition_identity_stages": len(source_topology["nodes"]), "complete_reference_chains": source_reference_chain["governed_data_cuts"], "retained_occurrences": source_occurrences["retained_occurrence_count"], "source_classes_with_occurrences": source_occurrences["source_class_count_with_retained_occurrence"], "production_qualified_occurrences": source_occurrences["production_qualified_occurrence_count"], "independently_appraised_occurrences": source_occurrences["independently_appraised_occurrence_count"]},
            "exit_condition": "All vertical source needs classify or emit extension gaps; representative real occurrences bind version/region/auth/config/cursor/cut/limits and executed connector/exit evidence.",
            "status": "OPEN",
            "authority_refs": ["research/domain_atlas/universes/source_systems/"],
        },
        {
            "batch_id": "B09_DATA_SHAPE_OPERATION_TOTALITY",
            "depends_on": ["B06_LIBRARY_CONTRACT_AUTHORITY", "B07_INDUSTRY_CANONICAL_REFERENCE_CLOSURE"],
            "scope": "Close type/shape operation totality, information-loss and representation crosswalk obligations.",
            "current": {"semantic_value_types": data_shapes["counts"]["semantic_value_types"], "logical_shapes": data_shapes["counts"]["logical_shapes"], "operation_totality_records": data_shapes["counts"]["operation_totality_records"], "crosswalks": data_shapes["counts"]["representation_crosswalks"], "historical_coverage_gaps": effective_shape_gaps["historical_gap_count"], "end_to_end_closed_gaps": effective_shape_gaps["end_to_end_closed_gap_count"], "effective_gap_status_counts": effective_shape_gaps["effective_status_counts"]},
            "exit_condition": "Every canonical operation used by product/vertical demand has per-type defined/refused/partial semantics and every representation conversion declares loss, authority and refusal behavior.",
            "status": "OPEN",
            "authority_refs": ["research/domain_atlas/universes/data_shapes/"],
        },
        {
            "batch_id": "B10_IMPLEMENTATION_IDENTITY_AND_BUILD",
            "depends_on": ["B06_LIBRARY_CONTRACT_AUTHORITY"],
            "scope": "Bind concrete implementation identities and reproducible-build evidence to library subjects.",
            "current": {"implementation_binding_vacancies": readiness["implementation_binding_vacancy_count"], "provider_registry_implementation_artifacts": providers["counts"]["implementation_artifacts"]},
            "exit_condition": "Each selected implementation has source/artifact/dependency/toolchain/config digests, SBOM/provenance and independent rebuild evidence for exact contract scope.",
            "status": "OPEN",
            "authority_refs": ["research/domain_atlas/compiler/provider_target_registry/", "research/product_ontology/qualification_program/"],
        },
        {
            "batch_id": "B11_EXACT_SCOPE_CONFORMANCE_AND_INDEPENDENT_APPRAISAL",
            "depends_on": ["B10_IMPLEMENTATION_IDENTITY_AND_BUILD", "B09_DATA_SHAPE_OPERATION_TOTALITY"],
            "scope": "Execute exact-scope suites, retain counterexamples, and obtain independent appraisal.",
            "current": {"qualification_receipts_seed": providers["counts"]["qualification_receipts"], "effective_vacancies": qualification["effective_evidence_vacancy_count"], "data_sharing_execution_slice_present": True},
            "exit_condition": "Required subjects have current exact-scope receipts and independent appraisal; failures remain counterexamples; no same-author evidence is mislabeled independent.",
            "status": "OPEN",
            "authority_refs": ["research/domain_atlas/compiler/conformance_evaluation/", "research/product_ontology/qualification_program/"],
        },
        {
            "batch_id": "B12_SECOND_IMPLEMENTATION_PORTABILITY_EXIT",
            "depends_on": ["B11_EXACT_SCOPE_CONFORMANCE_AND_INDEPENDENT_APPRAISAL"],
            "scope": "Qualify a second independently controlled implementation and execute differential/migration/exit drills.",
            "current": {"portable_products": qualification["portable_product_count"], "concrete_offers_seed": providers["counts"]["concrete_offers"]},
            "exit_condition": "Portable contracts have two independent qualified implementations plus differential, export/import, migration, rollback/loss and substitution evidence.",
            "status": "OPEN",
            "authority_refs": ["research/domain_atlas/compiler/provider_target_registry/", "research/product_ontology/qualification_program/"],
        },
        {
            "batch_id": "B13_PHYSICAL_BINDING_SLO_SECURITY_COST",
            "depends_on": ["B11_EXACT_SCOPE_CONFORMANCE_AND_INDEPENDENT_APPRAISAL"],
            "scope": "Bind exact physical occurrences and execute resource, SLO, failure, recovery, security/privacy/residency and cost evidence.",
            "current": {"target_occurrences_seed": providers["counts"]["target_occurrences"], "resource_cost_records_seed": providers["counts"]["resource_limit_cost_evidence"]},
            "exit_condition": "Selected offers have exact occurrence, finite budgets, measured SLO/cost, threat/isolation/privacy/residency evidence and failure/cancellation/recovery receipts.",
            "status": "OPEN",
            "authority_refs": ["research/domain_atlas/compiler/provider_target_registry/"],
        },
        {
            "batch_id": "B14_TWO_VERTICAL_EXECUTED_ACCEPTANCE",
            "depends_on": ["B07_INDUSTRY_CANONICAL_REFERENCE_CLOSURE", "B12_SECOND_IMPLEMENTATION_PORTABILITY_EXIT", "B13_PHYSICAL_BINDING_SLO_SECURITY_COST"],
            "scope": "Execute two unrelated vertical acceptance programs per retained product across eight gate classes.",
            "current": {"retained_products": qualification["retained_product_count"], "structurally_two_vertical_products": readiness["two_vertical_structural_product_count"], "executed_vertical_acceptance_products": qualification["executed_vertical_acceptance_product_count"], "nominal_gate_obligations": qualification["retained_product_count"] * 2 * 8},
            "exit_condition": "Each retained product has two unrelated domain-owner accepted physical occurrences with unchanged horizontal semantics and all eight acceptance classes passed or explicitly refused.",
            "status": "OPEN",
            "authority_refs": ["research/product_ontology/qualification_program/product-vertical-acceptance-programs.jsonl", "research/domain_atlas/industries/"],
        },
        {
            "batch_id": "B15_TWO_RELEASE_CHANGE_AND_RATIFICATION",
            "depends_on": ["B12_SECOND_IMPLEMENTATION_PORTABILITY_EXIT", "B14_TWO_VERTICAL_EXECUTED_ACCEPTANCE"],
            "scope": "Prove N-to-N+1 migration/replay/rollback/recall, then accountable product build-readiness and ratification.",
            "current": {"build_ready_products": qualification["build_ready_product_count"], "ratified_products": qualification["ratified_product_count"]},
            "exit_condition": "Each product has two-release retained evidence, migration/rollback/exit safety, current support/economics, build-ready verdict and bounded accountable ratification.",
            "status": "OPEN_PRODUCT_FINAL",
            "authority_refs": ["research/product_ontology/qualification_program/"],
        },
        {
            "batch_id": "B16_OPEN_WORLD_COVERAGE_AND_NOVELTY",
            "depends_on": ["B07_INDUSTRY_CANONICAL_REFERENCE_CLOSURE", "B08_SOURCE_SYSTEM_AND_OCCURRENCE_CLOSURE", "B09_DATA_SHAPE_OPERATION_TOTALITY"],
            "scope": "Challenge corpus coverage with held-out industries, professions, business lifecycles, analytical questions, source modalities and adversarial novelty; route every discovery to an existing contract or typed extension gap.",
            "current": {"coverage_planes": len(coverage_planes), "industry_challenge_packs": industries["pack_count"], "held_out_challenge_programs_executed": 0, "coverage_saturation_claimed": False},
            "exit_condition": "Repeated unrelated held-out challenges predominantly compose existing identities; every novelty is classified as missing evidence, missing member, missing library, missing product/context or vertical-only extension, with no silent coercion and no false closed-world claim.",
            "status": "OPEN_PROGRAM_GATE",
            "authority_refs": ["research/domain_atlas/coverage-planes.jsonl", "research/domain_atlas/industries/", "research/product_ontology/global_boundary_research/"],
        },
        {
            "batch_id": "B17_INTENT_TO_SOLUTION_SYNTHESIS",
            "depends_on": ["B12_SECOND_IMPLEMENTATION_PORTABILITY_EXIT", "B13_PHYSICAL_BINDING_SLO_SECURITY_COST", "B16_OPEN_WORLD_COVERAGE_AND_NOVELTY"],
            "scope": "Prove that declared enterprise intent can be elaborated, planned, compiled or human-completed into a governed solution while preserving semantic, authority, evidence and effect boundaries.",
            "current": {"architecture_components": synthesis["components"], "operating_modes": synthesis["operating_modes"], "ir_stages": synthesis["ir_stages"], "typed_transforms": synthesis["ir_transforms"], "binding_phases": synthesis["binding_phases"], "executed_solution_syntheses": 0, "products_promoted_by_architecture": synthesis["products_promoted"]},
            "exit_condition": "Representative intents lower through exact requirements/offers, compatibility solving, configuration, policy, implementation and physical binding into reproducible executable plans or typed refusals; unresolved judgment is surfaced rather than guessed.",
            "status": "OPEN_PROGRAM_GATE",
            "authority_refs": ["research/product_ontology/solution_synthesis_architecture/", "research/domain_atlas/compiler/"],
        },
        {
            "batch_id": "B18_APPLICATION_HUMAN_AUTHORITY_AND_EFFECT",
            "depends_on": ["B11_EXACT_SCOPE_CONFORMANCE_AND_INDEPENDENT_APPRAISAL", "B13_PHYSICAL_BINDING_SLO_SECURITY_COST", "B17_INTENT_TO_SOLUTION_SYNTHESIS"],
            "scope": "Qualify the application side: workflow/case, UI and documents, human review, accessibility/offline behavior, authorization, effect execution, compensation, appeal, recall and evidence presentation.",
            "current": {"human_work_contexts": human_work["files"]["bounded-contexts.jsonl"]["records"], "human_work_library_contracts": human_work["files"]["library-contracts.jsonl"]["records"], "human_work_decision_points": human_work["files"]["decision-points.jsonl"]["records"], "effect_boundary_routes": effect_boundary["target_member_routes"], "effect_profiles_supplied": effect_boundary["effect_boundary_coordinate_profiles_supplied"], "qualified_human_work_implementations": human_work["qualified_implementation_count"]},
            "exit_condition": "Executed application journeys preserve analytic result != recommendation != judgment != authorization != effect != outcome; accessibility, offline/recovery, refusal, compensation, appeal and recall behavior have exact evidence.",
            "status": "OPEN_PROGRAM_GATE",
            "authority_refs": ["research/domain_atlas/universes/human_work_review_adjudication/", "research/domain_atlas/compiler/library_registry/contract_generation/semantic_decomposition/effect_boundary_coordinate_ontology/"],
        },
        {
            "batch_id": "B19_MULTI_PRODUCT_SYSTEM_ACCEPTANCE",
            "depends_on": ["B14_TWO_VERTICAL_EXECUTED_ACCEPTANCE", "B17_INTENT_TO_SOLUTION_SYNTHESIS", "B18_APPLICATION_HUMAN_AUTHORITY_AND_EFFECT"],
            "scope": "Execute system-of-systems solutions across multiple products and verify cross-product identity, time, transaction, retry, authority, lineage, deletion/recall, recovery and version behavior.",
            "current": {"structural_composition_pilots": vertical_acceptance["pilot_structural_compositions"], "products_with_any_structural_pilot": vertical_acceptance["products_with_any_structural_pilot"], "executed_solution_acceptances": 0, "executed_fault_injection_campaigns": 0},
            "exit_condition": "Unrelated end-to-end solutions execute under normal and faulted paths with traceable requirements-to-effects evidence; product-local success cannot mask cross-product semantic, authority or recovery failure.",
            "status": "OPEN_PROGRAM_GATE",
            "authority_refs": ["research/product_ontology/composition_pilots/deterministic_verticals/", "research/domain_atlas/context_map/", "research/product_ontology/qualification_program/"],
        },
        {
            "batch_id": "B20_CONTINUOUS_VALIDITY_AND_DECOMMISSION",
            "depends_on": ["B15_TWO_RELEASE_CHANGE_AND_RATIFICATION", "B19_MULTI_PRODUCT_SYSTEM_ACCEPTANCE"],
            "scope": "Keep contracts, bindings, evidence and deployed solutions current under standards, provider, dependency, pricing, limit, security, schema and behavioral change; execute safe requalification and decommission.",
            "current": {"monitored_subjects": change_intelligence["counts"]["monitored-subjects"], "verified_change_events": change_intelligence["counts"]["verified-change-events"], "migration_invalidation_triggers": change_intelligence["counts"]["migration-invalidation-triggers"], "open_change_intelligence_gaps": change_intelligence["counts"]["gaps"], "executed_end_to_end_invalidation_propagations": 0, "executed_solution_decommissions": 0},
            "exit_condition": "Material changes invalidate every affected claim, contract, binding, build, qualification and solution; migration/requalification or typed suspension follows, and data/effects/support can be safely exited and decommissioned.",
            "status": "OPEN_FINAL_PROGRAM_GATE",
            "authority_refs": ["research/domain_atlas/ecosystem/change_intelligence/", "research/product_ontology/qualification_program/"],
        },
    ]

    write_jsonl(HERE / "master-batches.jsonl", batches)
    summary = {
        "report_id": "master_batched_closure_frontier",
        "as_of": "2026-08-27",
        "completion_claim": False,
        "batch_count": len(batches),
        "open_batch_count": sum(b["status"] not in {"CLOSED", "SATISFIED"} for b in batches),
        "retained_product_count": readiness["retained_product_count"],
        "library_subject_count": qualification["library_qualification_subject_count"],
        "effective_evidence_vacancy_count": qualification["effective_evidence_vacancy_count"],
        "industry_analytical_case_count": vertical_cases,
        "industry_canonical_reference_raw_queue_count": industry_effective["raw_queue_records"],
        "industry_canonical_reference_queue_count": industry_effective["remaining_open_research_records"],
        "industry_canonical_reference_research_resolved_count": industry_effective["research_resolved_candidate_records"],
        "industry_canonical_reference_machine_review_candidate_count": industry_review["source_candidate_records"],
        "source_system_class_count": source_systems["class_records"],
        "data_shape_logical_count": data_shapes["counts"]["logical_shapes"],
        "context_count": context_map["counts"]["contexts"],
        "provider_offer_seed_count": providers["counts"]["concrete_offers"],
        "program_level_gate_count": 5,
        "final_product_gate": "B15_TWO_RELEASE_CHANGE_AND_RATIFICATION",
        "final_program_gate": "B20_CONTINUOUS_VALIDITY_AND_DECOMMISSION",
        "next_machine_addressable_batch": "B07_INDUSTRY_CANONICAL_REFERENCE_CLOSURE",
        "next_authority_blocked_batch": "B01_SOURCE_AUTHORITY",
    }
    (HERE / "master-summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
