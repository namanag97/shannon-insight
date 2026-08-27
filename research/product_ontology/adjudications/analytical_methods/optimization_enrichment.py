#!/usr/bin/env python3
"""Deterministically enrich the analytical-method slice with the optimization product DDD.

The solver product starts at an exact mathematical model and ends at a qualified result.  Business
decision framing, semantic model-class adjudication, provider qualification, plan authorization and
execution of a business action remain external boundaries.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from experimentation_enrichment import enrich_experimentation
from forecasting_enrichment import enrich_forecasting
from geospatial_enrichment import enrich_geospatial
from graph_workbench_enrichment import enrich_graph_workbench
from planning_enrichment import enrich_planning
from process_mining_enrichment import enrich_process
from simulation_enrichment import enrich_simulation


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
SOURCE = HERE / "source.json"
OR_ROOT = ROOT / "research/domain_atlas/universes/operations_research"
PRODUCT = "product.optimization_solver"
PRODUCT_FIELDS = {
    "sovereign_question", "users", "harmed_parties", "jobs", "outcomes", "negative_mission",
    "lifecycle_states", "commands", "events", "invariants", "refusals", "automation_modality",
}
DDD_FIELDS = {
    "domain_vision_statement", "subdomain_classification", "bounded_context_boundary",
    "ubiquitous_language_policy", "context_map", "anti_corruption_layers", "published_language",
    "value_objects", "entities", "aggregates", "aggregate_roots", "aggregate_invariants",
    "commands", "domain_events", "refusal_failure_catalog", "domain_services",
    "application_services", "repositories", "factories", "specifications", "state_machine",
    "policies_and_reactions", "sagas_and_process_managers", "read_models_and_projections",
    "integration_event_policy", "concurrency_and_idempotency", "time_model",
    "event_storming_swimlanes", "nonfunctional_laws",
}
AUTOMATION = {
    "default": "DETERMINISTIC_CORE_ONLY",
    "postures": ["PROHIBITED", "OPTIONAL", "REQUIRED_BY_INTENT", "UNDETERMINED"],
    "law": "Models or agents may propose formulations, decompositions, warm starts, parameter profiles, explanations or repair candidates only; deterministic typechecking, capability matching, solve execution, result algebra and validation decide admissibility and status.",
    "removal_law": "Removing every optional model or agent preserves exact model validation, solver matching, bounded exact or heuristic execution, cancellation, result interpretation, solution validation and infeasibility diagnosis; explicitly required assistance may instead yield capability_unavailable.",
    "hard_work_law": "Automation never substitutes for decision vocabulary, units, objective and constraint authority, uncertainty semantics, algorithm contracts, budgets, tolerances, certificates, provider qualification or vertical acceptance.",
}

CONCRETE = [
    "library.operations_research.objective_preference_algebra",
    "library.operations_research.constraint_policy_algebra",
    "library.operations_research.optimization_model_ir",
    "library.operations_research.solver_capability_contract",
    "library.operations_research.optimization_solve_execution",
    "library.operations_research.optimization_result_algebra",
    "library.operations_research.optimization_solution_validation",
    "library.operations_research.infeasibility_diagnosis",
    "library.operations_research.heuristic_search_contract",
]
DEPENDENCIES = {
    "objective_preference_algebra": [],
    "constraint_policy_algebra": [],
    "optimization_model_ir": ["objective_preference_algebra", "constraint_policy_algebra"],
    "solver_capability_contract": ["optimization_model_ir"],
    "optimization_solve_execution": ["optimization_model_ir", "solver_capability_contract"],
    "optimization_result_algebra": ["optimization_model_ir"],
    "optimization_solution_validation": ["optimization_model_ir", "optimization_result_algebra"],
    "infeasibility_diagnosis": ["optimization_model_ir", "optimization_result_algebra"],
    "heuristic_search_contract": ["optimization_model_ir", "optimization_result_algebra"],
}


def jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


UPSTREAM = {row["library_id"]: row for row in jsonl(OR_ROOT / "library-boundaries.jsonl")}
SOURCE_ROWS = {row["source_id"]: row for row in jsonl(OR_ROOT / "sources.jsonl")}
SELECTED_SOURCE_REFS = sorted({ref for ident in CONCRETE for ref in UPSTREAM[ident]["evidence_refs"]})


def suffix(concrete_ref: str) -> str:
    return concrete_ref.rsplit(".", 1)[-1]


def local_library(concrete_ref: str) -> str:
    return f"library.analytics_optimization.{suffix(concrete_ref)}"


def local_capability(concrete_ref: str) -> str:
    return f"capability.analytics_optimization.{suffix(concrete_ref)}"


def source_rows() -> list[dict[str, Any]]:
    result = []
    for ref in SELECTED_SOURCE_REFS:
        row = SOURCE_ROWS[ref]
        result.append({
            "source_id": ref,
            "source_class": "primary_research" if row["kind"] == "primary_research" else "official_specification_or_documentation",
            "title": row["title"], "publisher": row["publisher"], "uri": row["url"],
            "retrieved_at": row["accessed_at"], "claim": row["authority_scope"],
            "scope_limit": row["limitations"],
        })
    return result


def library(concrete_ref: str) -> dict[str, Any]:
    row = UPSTREAM[concrete_ref]
    key = suffix(concrete_ref)
    provides = [local_capability(concrete_ref)]
    if key == "optimization_solve_execution":
        provides.append("capability.solve_optimization")
    laws = list(row["laws"])
    if key == "objective_preference_algebra":
        laws.append("The library validates declared objective precedence and Pareto policy; it never chooses business preference authority.")
    if key == "constraint_policy_algebra":
        laws.append("Hardness, chance level and relaxation authority are imported declarations; infeasibility never silently weakens them.")
    if key == "heuristic_search_contract":
        laws.append("Heuristic feasibility or empirical quality never implies optimality, approximation ratio or universal superiority.")
    return {
        "library_id": local_library(concrete_ref), "class": row["library_kind"],
        "owner_ref": "semantic.solver_session" if key == "optimization_solve_execution" else "semantic.optimization_model",
        "provides": provides, "types": row["public_types"], "operations": row["operation_refs"],
        "decisions": row["decision_refs"], "invariants": laws,
        "refusals": row["error_contracts"],
        "dependencies": [f"library.analytics_optimization.{dep}" for dep in DEPENDENCIES[key]],
        "effect_boundary": row["effect_boundary"], "evidence_refs": row["evidence_refs"],
        "product_refs": [PRODUCT],
    }


def capability(concrete_ref: str) -> dict[str, Any]:
    row = UPSTREAM[concrete_ref]
    key = suffix(concrete_ref)
    return {
        "artifact_id": local_capability(concrete_ref), "kind": "capability",
        "name": key.replace("_", " ").title(), "status": "specified_candidate",
        "semantic_owner_ref": "semantic.solver_session" if key == "optimization_solve_execution" else "semantic.optimization_model",
        "adoption_unit": False, "operated": False,
        "definition": f"Expose the provider-neutral {key.replace('_', ' ')} contract with all semantic, numeric, resource, cancellation and result decisions explicit.",
        "evidence_refs": row["evidence_refs"],
    }


def product_truth() -> dict[str, Any]:
    return {
        "sovereign_question": "For an exact, authorized mathematical-program occurrence and finite solve profile, what feasible, bounded-quality, proved-optimal, infeasible, unbounded, unknown, cancelled or failed result can be established without executing the business decision?",
        "users": ["operations_research_scientist", "optimization_engineer", "decision_analyst", "planning_application_owner", "runtime_operator", "assurance_reviewer"],
        "harmed_parties": ["affected_person", "customer_or_counterparty", "resource_owner", "worker_or_operator", "downstream_decision_maker", "environment_or_public_interest"],
        "jobs": ["Validate an exact mathematical model, bind a capable solver profile, execute within finite numeric and resource budgets, preserve termination/result truth, validate solutions, and diagnose infeasibility without authorizing business effects."],
        "outcomes": ["canonical_typed_model", "explicit_solver_capability_match_or_refusal", "bounded_cancellable_solve_attempt", "noncollapsed_termination_and_solution_status", "independently_recomputed_solution_validation", "scoped_infeasibility_or_conflict_evidence", "replayable_exact_or_heuristic_receipt"],
        "negative_mission": "Does not own industry vocabulary, decision alternatives, objective preference or constraint-relaxation authority, source forecasts, causal claims, model-class adjudication, provider qualification, resource admission, business action authorization, execution outcomes or vertical acceptance.",
        "lifecycle_states": ["draft", "model_bound", "typechecked", "capability_matching", "provider_unbound", "ready", "queued", "running", "incumbent_available", "validation_pending", "feasible_unproved", "bounded_quality", "proved_optimal", "infeasible", "unbounded", "infeasible_or_unbounded", "unknown", "numerical_failure", "resource_exhausted", "cancelled", "provider_failure", "superseded"],
        "commands": ["open_solver_session", "bind_model_occurrence", "typecheck_model", "canonicalize_model", "bind_solve_profile", "match_solver_offer", "bind_provider_occurrence", "start_solve_attempt", "record_progress", "submit_incumbent", "cancel_solve", "interpret_result", "validate_solution", "check_certificate", "diagnose_infeasibility", "propose_feasibility_relaxation", "publish_solve_receipt", "supersede_session"],
        "events": ["solver_session_opened", "model_occurrence_bound", "model_typechecked", "model_canonicalized", "solve_profile_bound", "solver_offer_matched", "provider_occurrence_bound", "solve_attempt_started", "solve_progress_recorded", "incumbent_submitted", "solve_cancelled", "result_interpreted", "solution_validated", "certificate_checked", "infeasibility_diagnosed", "feasibility_relaxation_proposed", "solve_receipt_published", "solver_session_superseded"],
        "invariants": ["business decision problem is distinct from mathematical model occurrence", "objective precedence and constraint hardness are imported authority-bound declarations", "model method algorithm provider attempt result and business action are distinct", "hard constraints never silently become penalties", "feasible selected qualified and authorized remain distinct", "termination reason primal status dual status bounds gap rays certificates and result count remain distinct", "heuristic result never implies optimality", "unknown cancelled resource-exhausted numerical-failure and provider-failure remain distinct", "result claims never exceed validation and certificate evidence", "solve output never executes a business effect"],
        "refusals": ["decision_authority_missing", "model_occurrence_unbound", "model_type_invalid", "unit_or_domain_ambiguous", "unsupported_model_class", "solver_capability_mismatch", "provider_unqualified", "tolerance_profile_missing", "resource_budget_unbounded", "numerically_invalid", "certificate_required_but_unavailable", "solution_validation_failed", "infeasibility_not_distinguished", "random_seed_or_replay_contract_missing", "effect_authority_requested"],
        "automation_modality": AUTOMATION,
    }


def dossier() -> dict[str, Any]:
    truth = product_truth()
    ddd = {
        "domain_vision_statement": "Own provider-neutral bounded solve sessions over exact mathematical-program occurrences, preserving every model, numeric, resource, termination and validation distinction without acquiring business decision authority.",
        "subdomain_classification": "core_horizontal_mathematical_optimization_solver_product",
        "bounded_context_boundary": {
            "inside": ["mathematical model occurrence identity and canonical IR", "variable domains expressions constraints objectives and explicit parameters", "declared objective precedence constraint hardness tolerance and certificate requirements", "solver capability requirements and offer matching", "solve profile budgets seeds stopping and cancellation", "attempt progress incumbents bounds gaps rays certificates and receipts", "termination primal and dual result algebra", "solution feasibility objective and certificate validation", "infeasibility conflict and relaxation proposals", "exact and explicitly heuristic search contracts"],
            "outside": ["industry and enterprise vocabulary", "decision owner alternatives and horizon authority", "objective preference selection and constraint relaxation authorization", "forecast distribution and scenario truth", "semantic model-class adjudication and transformations", "provider qualification and portability", "compute admission placement and allocation", "business-plan selection approval and action execution", "actual outcomes harms and vertical acceptance"],
        },
        "ubiquitous_language_policy": "Decision problem, mathematical model, model occurrence, variable, domain, parameter, objective, preference, constraint, hardness, tolerance, relaxation, solver requirement, solver offer, provider occurrence, solve profile, attempt, incumbent, bound, gap, ray, certificate, termination reason, primal status, dual status, validation, conflict and business action are non-interchangeable. AI is not a model class or evidence status.",
        "context_map": [
            {"neighbor_ref": "context.vertical_decision_domain", "relationship": "customer_supplier_acl", "translation": "consume exact actors actions units objectives constraints authority and acceptance without owning business meaning"},
            {"neighbor_ref": "context.model_class_adjudication", "relationship": "customer_supplier", "translation": "consume proved class facets and transformation obligations"},
            {"neighbor_ref": "context.solution_compiler", "relationship": "published_language", "translation": "consume exact model and capability requirements and return typed results or refusals"},
            {"neighbor_ref": "context.provider_qualification", "relationship": "customer_supplier", "translation": "consume occurrence-scoped feature numeric target and resource receipts"},
            {"neighbor_ref": "product.runtime_resource_control", "relationship": "customer_supplier", "translation": "request finite compute and cancellation without owning placement"},
            {"neighbor_ref": "product.simulation_environment", "relationship": "anti_corruption_layer", "translation": "simulation may estimate response or validate policy but never becomes optimality proof"},
            {"neighbor_ref": "context.decision_execution", "relationship": "effect_port", "translation": "publish candidate plan only; authorization and execution remain external"},
            {"neighbor_ref": "product.lineage_provenance", "relationship": "published_language", "translation": "publish model provider configuration seed result and validation receipts"},
        ],
        "anti_corruption_layers": ["acl.vertical_decision_problem", "acl.model_class_and_transform", "acl.solver_provider", "acl.runtime_resource", "acl.simulation", "acl.decision_execution", "acl.lineage_evidence"],
        "published_language": ["OptimizationModelRef", "OptimizationModelDigest", "VariableDomain", "ObjectiveSet", "ConstraintSet", "SolveProfileEdition", "SolverRequirement", "SolverOfferRef", "ProviderOccurrenceRef", "SolveAttemptId", "TerminationReason", "PrimalStatus", "DualStatus", "Incumbent", "Bound", "Gap", "Ray", "Certificate", "ValidationReceipt", "ConflictSet", "RelaxationProposal", "SolveReceipt", "TypedRefusal"],
        "value_objects": ["SolverSessionId", "OptimizationModelRef", "ModelDigest", "VariableRef", "VariableDomain", "ParameterCut", "ExpressionDigest", "ObjectivePriority", "ConstraintHardness", "ToleranceProfile", "SolveBudget", "RandomSeed", "ProviderOccurrenceRef", "AttemptId", "TerminationReason", "PrimalStatus", "DualStatus", "Bound", "Gap", "CertificateRef", "ValidationProfile"],
        "entities": ["SolverSession", "OptimizationModelOccurrence", "SolverBinding", "SolveAttempt", "IncumbentOccurrence", "OptimizationResult", "ValidationOccurrence", "InfeasibilityDiagnosis"],
        "aggregates": [
            {"root": "SolverSession", "members": ["model_ref", "solve_profile", "requirements", "binding", "attempt_refs", "selected_result", "state"], "consistency": "one session binds one immutable model occurrence and profile edition; retries create new attempts"},
            {"root": "OptimizationModelOccurrence", "members": ["variables", "parameters", "objectives", "constraints", "feature_set", "authority_refs", "digest"], "consistency": "canonical identity includes domains coefficients units objective precedence constraint hardness and uncertainty representation"},
            {"root": "SolveAttempt", "members": ["provider_occurrence", "configuration", "seed", "budget", "progress", "incumbents", "termination", "raw_receipt"], "consistency": "termination and partial-result validity are append-only and bound to exact provider target configuration and budget"},
            {"root": "QualifiedOptimizationResult", "members": ["termination", "primal_status", "dual_status", "solution", "bound", "gap", "rays", "certificates", "validation"], "consistency": "no result claim is stronger than termination, validation and certificate evidence"},
            {"root": "InfeasibilityDiagnosis", "members": ["model_ref", "attempt_ref", "conflicts", "iis", "relaxation_candidates", "authority_status"], "consistency": "diagnosis and relaxation proposals never mutate or weaken the original model"},
        ],
        "aggregate_roots": ["SolverSession", "OptimizationModelOccurrence", "SolveAttempt", "QualifiedOptimizationResult", "InfeasibilityDiagnosis"],
        "aggregate_invariants": truth["invariants"] + ["same frozen model profile provider and deterministic configuration produce an equivalent canonical result or declared schedule-dependent variance", "every stochastic or heuristic run binds seed stream stopping and replay contracts", "provider identity cannot change mathematical semantics"],
        "commands": truth["commands"], "domain_events": truth["events"],
        "refusal_failure_catalog": truth["refusals"] + ["infeasible", "unbounded", "infeasible_or_unbounded", "unknown", "cancelled", "resource_exhausted", "numerical_failure", "provider_failure", "optional_assistance_unavailable"],
        "domain_services": ["ModelTypecheckingService", "SolverCapabilityMatchingService", "SolveBudgetService", "ResultInterpretationService", "SolutionValidationService", "CertificateCheckingService", "InfeasibilityDiagnosisService", "HeuristicReplayService"],
        "application_services": ["OpenSolverSessionUseCase", "BindModelUseCase", "MatchSolverUseCase", "ExecuteSolveUseCase", "CancelSolveUseCase", "ValidateResultUseCase", "DiagnoseInfeasibilityUseCase", "PublishSolveReceiptUseCase", "CompareQualifiedResultsUseCase"],
        "repositories": ["SolverSessionRepository", "ModelOccurrenceRepository", "SolveAttemptRepository", "QualifiedResultRepository", "DiagnosisRepository"],
        "factories": ["SolverSessionFactory", "ModelOccurrenceFactory", "SolveAttemptFactory", "QualifiedResultFactory", "InfeasibilityDiagnosisFactory"],
        "specifications": ["ModelWellFormedSpecification", "ObjectiveAuthoritySpecification", "ConstraintHardnessSpecification", "SolverCapabilitySpecification", "SolveBudgetSpecification", "ToleranceSpecification", "ResultClaimSpecification", "SolutionValidationSpecification", "CertificateRequirementSpecification", "HeuristicReplaySpecification"],
        "state_machine": {"session": truth["lifecycle_states"], "attempt": ["created", "queued", "running", "incumbent_available", "termination_observed", "cancel_requested", "cancelled", "failed", "sealed"], "result": ["raw", "interpreted", "validation_pending", "validated", "invalid", "published", "superseded"]},
        "policies_and_reactions": ["when model semantics or authority are unbound refuse rather than infer", "when provider features do not cover the exact model refuse or require an authorized proved transformation", "when a hard constraint conflicts retain infeasibility rather than add penalty", "when a caller deadline expires request cancellation and reconcile final provider status", "when an incumbent exists at cancellation publish it only with its feasibility and proof status", "when provider reports success independently recompute feasibility and objective", "when infeasible or unbounded is not distinguished preserve the combined status", "when a heuristic terminates prohibit optimality claims unless separately proved"],
        "sagas_and_process_managers": ["SolverBindingProcess", "BoundedSolveProcess", "CancellationReconciliationProcess", "SolutionQualificationProcess", "InfeasibilityDiagnosisProcess", "CrossProviderDifferentialProcess"],
        "read_models_and_projections": ["SolverSessionView", "CanonicalModelView", "CapabilityMatchView", "SolveProgressView", "IncumbentBoundGapView", "QualifiedResultView", "ValidationEvidenceView", "InfeasibilityConflictView", "CrossProviderComparisonView"],
        "integration_event_policy": "Only editioned model-binding, capability-match, attempt-progress, termination, result, validation, diagnosis and receipt facts cross the boundary. Business semantics, authority decisions, provider internals, resource effects, selected plans and actual outcomes remain external.",
        "concurrency_and_idempotency": ["optimistic solver-session edition", "idempotency keys bind model profile provider configuration and attempt identity", "each retry or portfolio branch has a distinct attempt identity", "progress and incumbents are append-only", "parallel search declares determinism and schedule-dependence", "unknown completion reconciles before retry", "cancellation is a request until terminal provider evidence arrives"],
        "time_model": ["model parameter validity and recording time are distinct", "decision horizon and information-revelation time are imported", "session creation queue start incumbent termination cancellation validation and publication times are separate", "time limit is a solve budget not proof status", "provider evidence has retrieval validity and expiry", "results bind exact as-of model and parameter cuts"],
        "event_storming_swimlanes": ["vertical_domain_owner", "operations_research_scientist", "solution_compiler", "provider_qualifier", "solver_runtime", "runtime_resource_control", "solution_validator", "business_decision_authority", "affected_party"],
        "nonfunctional_laws": ["finite work time memory threads external cost and result count", "cooperative cancellation with typed partial-result validity", "numeric tolerances precision scaling and determinism are explicit", "cross-provider differential and exact-small-fixture oracles", "unsafe FFI and provider crashes are isolated behind process boundaries where required", "receipts bind model provider artifact target configuration seed budget and result", "provider identity cannot change semantic meaning", AUTOMATION["removal_law"]],
    }
    assert set(ddd) == DDD_FIELDS
    return {"dossier_id": "ddd.analytics.optimization_solver", "product_ref": PRODUCT, "status": "candidate_not_ratified", "product_truth": {"sovereign_question": truth["sovereign_question"], "users": truth["users"], "harmed_parties": truth["harmed_parties"], "jobs": truth["jobs"], "measurable_outcomes": truth["outcomes"], "negative_mission": truth["negative_mission"]}, "strategic_and_tactical_ddd": ddd}


def enrich(source: dict[str, Any]) -> dict[str, Any]:
    generated_capabilities = {local_capability(ref) for ref in CONCRETE}
    generated_libraries = {local_library(ref) for ref in CONCRETE}
    generated_requirements = {f"requirement.analytics_optimization.{suffix(ref)}" for ref in CONCRETE}
    generated_maps = {f"binding.analytics_optimization.{suffix(ref)}" for ref in CONCRETE}
    generated_negatives = {f"negative.optimizer.{key}" for key in ["decision_model", "hard_soft", "success_status", "feasible_optimal", "heuristic_proof", "timeout_terminal", "diagnosis_relaxation", "provider_name", "solution_effect", "agent_authority"]}
    generated_laws = {"decision problem != mathematical model != solver provider != solve attempt != result != selected plan != authorized action != outcome", "hard constraint != soft constraint != objective", "feasible != bounded-quality != proved-optimal", "unknown != infeasible != unbounded != numerical failure != cancelled", "heuristic quality != optimality proof", "model or agent proposal != accepted formulation or authority"}
    source["sources"] = [row for row in source["sources"] if row["source_id"] not in SELECTED_SOURCE_REFS] + source_rows()
    source["artifacts"] = [row for row in source["artifacts"] if row["artifact_id"] not in generated_capabilities]
    source["libraries"] = [row for row in source["libraries"] if row["library_id"] not in generated_libraries | {"library.optimization_core"}]
    source["requirements"] = [row for row in source["requirements"] if row["requirement_id"] not in generated_requirements]
    source["binding_maps"] = [row for row in source.get("binding_maps", []) if row["binding_map_id"] not in generated_maps | {"binding.analytics.optimization"}]
    source["negative_tests"] = [row for row in source["negative_tests"] if row["test_id"] not in generated_negatives]
    source["ddd_dossiers"] = [row for row in source.get("ddd_dossiers", []) if row.get("product_ref") != PRODUCT]
    source["non_collapse_laws"] = [law for law in source["non_collapse_laws"] if law not in generated_laws]

    for row in source["crosswalks"]:
        if row["legacy_ref"] == "candidate.product.optimization":
            row["canonical_refs"] = [ref for ref in row["canonical_refs"] if ref != "library.optimization_core"]

    next(row for row in source["artifacts"] if row["artifact_id"] == PRODUCT).update(product_truth())
    source["artifacts"].extend(capability(ref) for ref in CONCRETE)
    source["libraries"].extend(library(ref) for ref in CONCRETE)
    for ref in CONCRETE:
        key = suffix(ref)
        source["requirements"].append({"requirement_id": f"requirement.analytics_optimization.{key}", "consumer_ref": PRODUCT, "capability_ref": local_capability(ref), "binding_phase": "runtime" if UPSTREAM[ref]["effect_boundary"] == "effectful_runtime" else "compile_time", "minimum_qualified_offers": 1, "status": "unbound", "refusal": f"no_qualified_{key}_implementation"})
        source["binding_maps"].append({
            "binding_map_id": f"binding.analytics_optimization.{key}", "abstract_library_ref": local_library(ref),
            "concrete_library_refs": [ref], "concrete_requirement_refs": UPSTREAM[ref]["requirement_refs"],
            "composition_law": "Exact one-owner projection; business authority and provider qualification remain external.",
            "bindability": "structurally_bindable_unqualified", "blocking_gap_refs": [],
            "modality_posture": "deterministic_core", "minimum_qualified_implementations_per_required_contract": 1,
            "portable_claim_minimum_independent_implementations": 2,
            "qualification_profile_refs": [f"receipt.operations_research.{key}"],
            "substitution_law": "All semantic, numeric, failure, resource, cancellation, target and result claims survive provider substitution.",
            "cross_provider_differential_required": True, "fallback_law": "refuse", "status": "candidate_not_bound",
            "product_refs": [PRODUCT],
        })
    source["ddd_dossiers"].append(dossier())
    source["negative_tests"].extend([
        {"test_id": "negative.optimizer.decision_model", "prohibited_claim": "A mathematical model owns the business decision vocabulary and authority.", "expected_result": "require exact vertical decision-domain imports"},
        {"test_id": "negative.optimizer.hard_soft", "prohibited_claim": "An infeasible hard constraint may silently become a penalty.", "expected_result": "retain infeasibility or require authorized relaxation"},
        {"test_id": "negative.optimizer.success_status", "prohibited_claim": "Provider success is a sufficient result status.", "expected_result": "preserve termination primal dual bound gap ray certificate and validation states"},
        {"test_id": "negative.optimizer.feasible_optimal", "prohibited_claim": "A feasible incumbent is selected, qualified or optimal.", "expected_result": "return exact feasibility and proof status only"},
        {"test_id": "negative.optimizer.heuristic_proof", "prohibited_claim": "A heuristic result proves optimality or a universal approximation guarantee.", "expected_result": "publish empirical/bounded quality and no stronger claim"},
        {"test_id": "negative.optimizer.timeout_terminal", "prohibited_claim": "Caller timeout proves the provider stopped and no incumbent exists.", "expected_result": "request cancellation and reconcile terminal state"},
        {"test_id": "negative.optimizer.diagnosis_relaxation", "prohibited_claim": "An infeasibility diagnosis authorizes model relaxation.", "expected_result": "emit proposal requiring external authority"},
        {"test_id": "negative.optimizer.provider_name", "prohibited_claim": "A solver brand name proves support or qualification.", "expected_result": "match exact occurrence capability and qualification evidence"},
        {"test_id": "negative.optimizer.solution_effect", "prohibited_claim": "A published solution is an authorized or executed business action.", "expected_result": "emit candidate plan only"},
        {"test_id": "negative.optimizer.agent_authority", "prohibited_claim": "An agent-generated formulation, parameter set or repair closes missing semantics or authority.", "expected_result": "retain proposal taint and deterministic obligations"},
    ])
    source["non_collapse_laws"].extend(sorted(generated_laws))
    return source


def source_bytes() -> bytes:
    source = json.loads(SOURCE.read_text(encoding="utf-8"))
    return (json.dumps(enrich_planning(enrich_graph_workbench(enrich_geospatial(enrich_experimentation(enrich_forecasting(enrich_simulation(enrich_process(enrich(source)))))))), ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    expected = source_bytes()
    if args.check:
        if SOURCE.read_bytes() != expected:
            print("ERROR analytical-method source differs from canonical optimization enrichment")
            return 1
        print("CHECK PASS analytical optimization enrichment")
        return 0
    SOURCE.write_bytes(expected)
    print("BUILD PASS analytical optimization enrichment")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
