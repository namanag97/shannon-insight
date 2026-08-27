#!/usr/bin/env python3
"""Project exact simulation seams into the Simulation Environment product.

Simulation is a deterministic/stochastic analytical-method domain, not an AI synonym.  A model,
run, output estimate, validation claim, real system, prediction, decision and effect remain distinct.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
OR_ROOT = ROOT / "research/domain_atlas/universes/operations_research"
PRODUCT = "product.simulation_environment"
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
    "law": "Models or agents may propose conceptual structures, parameters, scenarios, calibration candidates, experiment designs or explanations only; typed model semantics, experiment sealing, random-stream control, bounded execution, output analysis and verification/validation decide admissibility.",
    "removal_law": "Removing every optional predictive model, LLM or agent preserves simulation-model typechecking, experiment design, random-stream allocation and replay, bounded execution, output analysis, comparison and verification/validation; explicitly required assistance may instead yield capability_unavailable.",
    "hard_work_law": "Automation never replaces system vocabulary, model scope, state/event/clock semantics, initial conditions, input evidence, random distributions, warm-up and replication policy, resource bounds, uncertainty estimation, validation evidence, provider qualification or vertical acceptance.",
}

CONCRETE = [
    "library.operations_research.simulation_model_semantics",
    "library.operations_research.simulation_experiment_design",
    "library.operations_research.simulation_random_stream_control",
    "library.operations_research.simulation_execution",
    "library.operations_research.simulation_output_analysis",
    "library.operations_research.simulation_verification_validation",
]
DEPENDENCIES = {
    "simulation_model_semantics": [],
    "simulation_experiment_design": ["simulation_model_semantics"],
    "simulation_random_stream_control": ["simulation_experiment_design"],
    "simulation_execution": ["simulation_model_semantics", "simulation_experiment_design", "simulation_random_stream_control"],
    "simulation_output_analysis": ["simulation_experiment_design", "simulation_execution"],
    "simulation_verification_validation": ["simulation_model_semantics", "simulation_experiment_design", "simulation_execution", "simulation_output_analysis"],
}


def jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


UPSTREAM = {row["library_id"]: row for row in jsonl(OR_ROOT / "library-boundaries.jsonl")}
SOURCE_ROWS = {row["source_id"]: row for row in jsonl(OR_ROOT / "sources.jsonl")}
SELECTED_SOURCE_REFS = sorted({ref for ident in CONCRETE for ref in UPSTREAM[ident]["evidence_refs"]})


def suffix(ref: str) -> str:
    return ref.rsplit(".", 1)[-1]


def local_library(ref: str) -> str:
    return f"library.analytics_simulation.{suffix(ref)}"


def local_capability(ref: str) -> str:
    return f"capability.analytics_simulation.{suffix(ref)}"


def source_rows() -> list[dict[str, Any]]:
    rows = []
    for ref in SELECTED_SOURCE_REFS:
        row = SOURCE_ROWS[ref]
        rows.append({
            "source_id": ref,
            "source_class": "primary_research" if row["kind"] == "primary_research" else "official_specification_or_documentation",
            "title": row["title"],
            "publisher": row["publisher"],
            "uri": row["url"],
            "retrieved_at": row["accessed_at"],
            "claim": row["authority_scope"],
            "scope_limit": row["limitations"],
        })
    return rows


def capability(ref: str) -> dict[str, Any]:
    row = UPSTREAM[ref]
    key = suffix(ref)
    owner = "semantic.simulation_model" if key in {"simulation_model_semantics", "simulation_random_stream_control", "simulation_execution"} else "semantic.simulation_experiment"
    return {
        "artifact_id": local_capability(ref),
        "kind": "capability",
        "name": key.replace("_", " ").title(),
        "status": "specified_candidate",
        "semantic_owner_ref": owner,
        "adoption_unit": False,
        "operated": False,
        "definition": f"Expose provider-neutral {key.replace('_', ' ')} with model, time, randomness, resource, uncertainty, refusal and evidence decisions explicit.",
        "evidence_refs": row["evidence_refs"],
    }


def library(ref: str) -> dict[str, Any]:
    row = UPSTREAM[ref]
    key = suffix(ref)
    owner = "semantic.simulation_model" if key in {"simulation_model_semantics", "simulation_random_stream_control", "simulation_execution"} else "semantic.simulation_experiment"
    provides = [local_capability(ref)]
    if key == "simulation_execution":
        provides.append("capability.run_simulation")
    laws = list(row["laws"])
    laws.extend({
        "simulation_model_semantics": ["A simulation model is a scoped executable representation, not the real system, a digital-twin identity or a prediction."],
        "simulation_experiment_design": ["A scenario is not a forecast, and a prospective design is not an observed run."],
        "simulation_random_stream_control": ["A seed alone is not a random-stream allocation, independence proof or replay receipt."],
        "simulation_execution": ["Run completion proves execution only; it proves neither output validity nor reality fit."],
        "simulation_output_analysis": ["A replication observation, estimator, interval, scenario comparison and causal claim are distinct."],
        "simulation_verification_validation": ["Verification addresses implementation against specification; validation addresses scoped intended-use evidence; neither proves universal truth."],
    }[key])
    return {
        "library_id": local_library(ref),
        "class": row["library_kind"],
        "owner_ref": owner,
        "provides": provides,
        "types": row["public_types"],
        "operations": row["operation_refs"],
        "decisions": row["decision_refs"],
        "invariants": laws,
        "refusals": row["error_contracts"],
        "dependencies": [f"library.analytics_simulation.{dep}" for dep in DEPENDENCIES[key]],
        "effect_boundary": row["effect_boundary"],
        "evidence_refs": row["evidence_refs"],
        "product_refs": [PRODUCT],
    }


def product_truth() -> dict[str, Any]:
    return {
        "sovereign_question": "For an explicit simulation-model edition, scenario set, experiment design, random-stream plan and finite execution profile, what reproducible simulated observations, uncertainty-bounded comparisons and scoped verification/validation claims can be established without claiming that the model is reality or authorizing an external effect?",
        "users": ["simulation_modeler", "operations_research_scientist", "systems_engineer", "domain_analyst", "experiment_designer", "runtime_operator", "verification_validation_reviewer", "decision_owner"],
        "harmed_parties": ["person_represented_by_model", "worker_or_operator", "customer_or_counterparty", "resource_owner", "decision_affected_party", "environment_or_public_interest"],
        "jobs": ["Define and typecheck a scoped simulation model; design immutable experiments; allocate replayable random streams; execute finite cancellable replications; estimate output uncertainty; compare scenarios; and publish bounded verification and validation evidence."],
        "outcomes": ["typed_scoped_model_edition", "sealed_experiment_design", "replayable_randomness_receipt", "bounded_cancellable_run_receipts", "replication_level_observations", "uncertainty_bounded_output_estimates", "scoped_scenario_comparisons", "separate_verification_and_validation_claims"],
        "negative_mission": "Does not own the real system or digital-twin identity, source-data truth, domain policy, forecast truth, causal identification, optimization, model-provider qualification, compute admission, business decision authority, real-world execution, observed outcomes or vertical acceptance.",
        "lifecycle_states": ["draft", "conceptualized", "specified", "typechecked", "verified", "experiment_designed", "sealed", "provider_unbound", "ready", "queued", "running", "partially_observed", "cancel_requested", "cancelled", "completed", "analysis_pending", "analyzed", "validation_pending", "validated_for_scope", "validation_refused", "published", "superseded"],
        "commands": ["open_simulation_project", "register_model_edition", "typecheck_model", "verify_model_implementation", "define_scenario", "design_experiment", "bind_initialization_and_warmup", "allocate_random_streams", "seal_experiment", "bind_provider_occurrence", "start_replication_set", "record_simulation_progress", "cancel_replication_set", "seal_run_receipts", "analyze_outputs", "compare_scenarios", "submit_validation_evidence", "adjudicate_validation_claim", "publish_simulation_evidence", "supersede_model_or_experiment"],
        "events": ["simulation_project_opened", "model_edition_registered", "model_typechecked", "model_implementation_verified", "scenario_defined", "experiment_designed", "initialization_and_warmup_bound", "random_streams_allocated", "experiment_sealed", "provider_occurrence_bound", "replication_set_started", "simulation_progress_recorded", "replication_cancellation_requested", "replication_set_cancelled", "run_receipts_sealed", "outputs_analyzed", "scenarios_compared", "validation_evidence_submitted", "validation_claim_adjudicated", "simulation_evidence_published", "model_or_experiment_superseded"],
        "invariants": ["real system, conceptual model, executable model, provider artifact, experiment, run, observation, estimate, validation claim, decision and effect are distinct", "simulation paradigm, clock, state, event, resource, interaction and equation semantics are explicit", "scenario is not forecast and simulated observation is not real observation", "seed is not stream partition or independence evidence", "initialization, warm-up, run length, stopping and replication count are explicit", "cancelled, partial, completed, failed and unknown runs remain distinct", "verification is not validation and validation is scoped to intended use and evidence cut", "scenario difference is not causal effect without a separate causal design", "calibration is not validation or truth", "simulation output never authorizes a business effect"],
        "refusals": ["system_scope_unbound", "model_semantics_ambiguous", "unsupported_paradigm_composition", "clock_or_ordering_undefined", "initial_state_missing", "input_distribution_unjustified", "experiment_design_unsealed", "random_stream_plan_missing", "provider_unqualified", "resource_budget_unbounded", "replication_plan_invalid", "partial_output_invalid_for_estimand", "uncertainty_not_estimable", "verification_failed", "validation_scope_missing", "validation_evidence_insufficient", "reality_claim_exceeds_evidence", "effect_authority_requested"],
        "automation_modality": AUTOMATION,
    }


def dossier() -> dict[str, Any]:
    truth = product_truth()
    ddd = {
        "domain_vision_statement": "Own provider-neutral simulation model and experiment lifecycles that yield reproducible, uncertainty-bounded simulated evidence while preserving the boundary between representation, execution, validation, reality and action.",
        "subdomain_classification": "core_horizontal_simulation_modeling_and_experiment_product",
        "bounded_context_boundary": {
            "inside": ["conceptual and executable simulation model editions", "discrete-event agent-based continuous system-dynamics Monte-Carlo and hybrid paradigm declarations", "state event resource interaction equation and clock semantics", "scenarios parameters initial states initialization warm-up horizons and stopping", "prospective experiment and replication design", "seed family substream common-random-number and replay control", "provider-bound finite cancellable execution and run receipts", "replication observations estimands uncertainty and scenario comparison", "implementation verification and intended-use-scoped validation claims"],
            "outside": ["real-system and digital-twin identity", "source observation quality and lineage", "domain ontology policy and authority", "forecast and causal truth", "optimization and plan selection", "generic predictive-model lifecycle", "provider qualification and portability", "compute admission and placement", "business approval action execution and actual outcomes", "vertical acceptance"],
        },
        "ubiquitous_language_policy": "Real system, digital twin, conceptual model, executable simulation model, model edition, paradigm, clock, state, event, entity, resource, stock/flow, interaction, parameter, scenario, forecast, experiment, initialization, warm-up, seed, stream, substream, replication, run, simulated observation, estimand, output estimate, interval, verification, calibration, validation claim, decision and effect are non-interchangeable. Stochastic, heuristic or learned components are declared methods, not an AI status upgrade.",
        "context_map": [
            {"neighbor_ref": "context.vertical_domain_model", "relationship": "customer_supplier_acl", "translation": "consume system vocabulary behavior assumptions units scope authority and acceptance without owning them"},
            {"neighbor_ref": "product.lineage_provenance", "relationship": "published_language", "translation": "consume input/model provenance and publish exact model experiment provider seed run analysis and validation receipts"},
            {"neighbor_ref": "product.data_quality", "relationship": "customer_supplier", "translation": "consume purpose-scoped input-quality evidence without converting it into model validity"},
            {"neighbor_ref": "product.optimization_solver", "relationship": "anti_corruption_layer", "translation": "exchange candidate policies or response estimates without treating simulation as optimization proof"},
            {"neighbor_ref": "product.forecasting_workbench", "relationship": "anti_corruption_layer", "translation": "consume forecast distributions as attributed inputs; scenarios never silently become forecasts"},
            {"neighbor_ref": "context.causal_analysis", "relationship": "anti_corruption_layer", "translation": "scenario differences remain model-conditional unless a separate causal design is established"},
            {"neighbor_ref": "context.provider_qualification", "relationship": "customer_supplier", "translation": "consume occurrence-scoped paradigm numeric target resource and reproducibility receipts"},
            {"neighbor_ref": "product.runtime_resource_control", "relationship": "customer_supplier", "translation": "request finite compute and cancellation without owning scheduling"},
            {"neighbor_ref": "context.decision_execution", "relationship": "effect_port", "translation": "publish simulated evidence only; selection authorization and external effect remain outside"},
        ],
        "anti_corruption_layers": ["acl.vertical_system_model", "acl.source_evidence", "acl.forecast_input", "acl.optimization", "acl.causal_claim", "acl.simulation_provider", "acl.runtime_resource", "acl.decision_effect"],
        "published_language": ["SimulationProjectRef", "SimulationModelEdition", "ModelScope", "ParadigmProfile", "SimulationClock", "ScenarioEdition", "ExperimentDesignEdition", "InitializationProfile", "WarmupPolicy", "ReplicationPlan", "RandomStreamPlan", "ProviderOccurrenceRef", "SimulationRunId", "SimulationObservation", "OutputEstimand", "OutputEstimate", "ScenarioComparison", "VerificationReceipt", "ValidationClaim", "SimulationEvidenceBundle", "TypedRefusal"],
        "value_objects": ["SimulationProjectId", "ModelEditionId", "ModelDigest", "ModelScope", "ParadigmProfile", "ClockPolicy", "StateSchema", "EventOrderingPolicy", "ParameterCut", "ScenarioId", "ExperimentEditionId", "InitializationProfile", "WarmupPolicy", "StoppingRule", "ReplicationBudget", "SeedSet", "SubstreamPlan", "ProviderOccurrenceRef", "RunId", "OutputEstimand", "ValidationScope"],
        "entities": ["SimulationProject", "SimulationModelEdition", "ScenarioEdition", "SimulationExperiment", "RandomStreamAllocation", "ReplicationSet", "SimulationRun", "OutputAnalysis", "VerificationOccurrence", "ValidationAppraisal"],
        "aggregates": [
            {"root": "SimulationProject", "members": ["scope", "model_refs", "experiment_refs", "authority_refs", "state"], "consistency": "one project preserves immutable editions and explicit supersession"},
            {"root": "SimulationModelEdition", "members": ["scope", "paradigms", "state_schema", "event_and_clock_semantics", "equations_and_rules", "parameters", "interfaces", "digest"], "consistency": "identity changes when any behaviorally relevant semantic changes"},
            {"root": "SimulationExperiment", "members": ["model_ref", "scenarios", "initialization", "warmup", "horizon", "replication_plan", "estimands", "random_stream_plan", "seal"], "consistency": "a sealed design is immutable and binds all interpretation-relevant choices"},
            {"root": "ReplicationSet", "members": ["experiment_ref", "provider_occurrence", "runs", "progress", "termination", "receipts"], "consistency": "each run has unique identity and exact provider configuration seed/substream and resource bounds"},
            {"root": "SimulationEvidence", "members": ["run_refs", "observations", "estimates", "comparisons", "verification", "validation_claims", "limitations"], "consistency": "no claim exceeds its model scope, completed valid runs, uncertainty method and external validation evidence"},
        ],
        "aggregate_roots": ["SimulationProject", "SimulationModelEdition", "SimulationExperiment", "ReplicationSet", "SimulationEvidence"],
        "aggregate_invariants": truth["invariants"] + ["all behaviorally relevant configuration participates in model experiment or run identity", "parallel execution declares schedule-dependent determinism", "common random numbers are paired only under an explicit coupling plan", "partial and censored runs contribute only to estimands that declare their validity", "provider identity cannot change simulation meaning"],
        "commands": truth["commands"],
        "domain_events": truth["events"],
        "refusal_failure_catalog": truth["refusals"] + ["cancelled", "resource_exhausted", "numerical_failure", "provider_failure", "unknown_terminal_state", "optional_assistance_unavailable"],
        "domain_services": ["SimulationModelTypecheckingService", "ParadigmCompositionService", "ExperimentDesignService", "RandomStreamAllocationService", "SimulationExecutionService", "OutputAnalysisService", "ScenarioComparisonService", "VerificationService", "ValidationAppraisalService"],
        "application_services": ["OpenSimulationProjectUseCase", "RegisterModelEditionUseCase", "DesignAndSealExperimentUseCase", "ExecuteReplicationSetUseCase", "CancelAndReconcileRunsUseCase", "AnalyzeSimulationOutputsUseCase", "VerifySimulationUseCase", "AppraiseValidationUseCase", "PublishSimulationEvidenceUseCase"],
        "repositories": ["SimulationProjectRepository", "SimulationModelEditionRepository", "SimulationExperimentRepository", "ReplicationSetRepository", "SimulationEvidenceRepository"],
        "factories": ["SimulationProjectFactory", "SimulationModelEditionFactory", "SimulationExperimentFactory", "ReplicationSetFactory", "SimulationEvidenceFactory"],
        "specifications": ["ModelScopeSpecification", "ParadigmCompositionSpecification", "ClockOrderingSpecification", "InputDistributionEvidenceSpecification", "ExperimentSealSpecification", "RandomStreamIndependenceSpecification", "ReplicationAdequacySpecification", "OutputEstimandSpecification", "VerificationSpecification", "ValidationClaimScopeSpecification"],
        "state_machine": {"project": truth["lifecycle_states"], "model": ["draft", "specified", "typechecked", "verification_pending", "verified", "verification_failed", "superseded"], "experiment": ["draft", "designed", "randomness_bound", "sealed", "running", "completed", "analysis_pending", "analyzed", "superseded"], "run": ["created", "queued", "running", "partially_observed", "cancel_requested", "cancelled", "completed", "failed", "unknown", "sealed"]},
        "policies_and_reactions": ["when system meaning or model scope is unbound refuse rather than infer", "when paradigm or clock composition is unsupported refuse", "when a design is sealed create a new edition for any interpretive change", "when randomness is required allocate streams before execution", "when a caller deadline expires request cancellation and reconcile terminal provider state", "when runs are partial include them only under declared estimand validity", "when scenario outputs differ report model-conditional comparison and uncertainty", "when verification fails prohibit validation publication", "when validation evidence does not cover intended use narrow or refuse the claim", "when an output is proposed for action require external selection and authority"],
        "sagas_and_process_managers": ["ModelVerificationProcess", "ExperimentSealingProcess", "ReplicationExecutionProcess", "CancellationReconciliationProcess", "OutputQualificationProcess", "ValidationAppraisalProcess", "CrossProviderDifferentialProcess"],
        "read_models_and_projections": ["SimulationProjectView", "ModelSemanticDiffView", "ExperimentDesignView", "RandomStreamAllocationView", "ReplicationProgressView", "RunReceiptView", "OutputEstimateView", "ScenarioComparisonView", "VerificationEvidenceView", "ValidationScopeAndLimitationsView"],
        "integration_event_policy": "Only editioned model, experiment, randomness, run, output, verification, validation and evidence facts cross the boundary. Real-system truth, source-data verdicts, provider internals, resource effects, causal claims, selected decisions and actual outcomes remain external.",
        "concurrency_and_idempotency": ["optimistic project model and experiment editions", "model and sealed experiment records are immutable", "idempotency binds experiment provider configuration seed/substream and run identity", "each retry is a new run unless exact-once replay is proved", "observations and progress are append-only", "parallel execution declares ordering and determinism", "unknown completion reconciles before retry", "cancellation is a request until terminal provider evidence arrives"],
        "time_model": ["real-system event time simulated time wall-clock runtime recording time and publication time are distinct", "simulation clock scale ordering and tie breaking are explicit", "initialization warm-up horizon stopping and observation windows are separate", "scenario and parameter validity cuts are immutable inputs", "validation evidence has applicability and expiry", "results bind exact as-of model experiment input and provider cuts"],
        "event_storming_swimlanes": ["domain_system_owner", "simulation_modeler", "experiment_designer", "source_evidence_owner", "provider_qualifier", "simulation_runtime", "runtime_resource_control", "verification_reviewer", "validation_authority", "decision_owner", "affected_party"],
        "nonfunctional_laws": ["finite work time memory threads external cost replications and output volume", "cooperative cancellation with typed partial-result validity", "numeric precision tolerances integration step and event ordering are explicit", "randomness partition and replay receipts are mandatory for stochastic claims", "cross-provider differential and exact-small-model oracles", "unsafe FFI provider crashes and generated code are isolated and qualified", "receipts bind model experiment input provider artifact target configuration random streams budget and outputs", "provider identity cannot change semantic meaning", AUTOMATION["removal_law"]],
    }
    assert set(ddd) == DDD_FIELDS
    return {
        "dossier_id": "ddd.analytics.simulation_environment",
        "product_ref": PRODUCT,
        "status": "candidate_not_ratified",
        "product_truth": {"sovereign_question": truth["sovereign_question"], "users": truth["users"], "harmed_parties": truth["harmed_parties"], "jobs": truth["jobs"], "measurable_outcomes": truth["outcomes"], "negative_mission": truth["negative_mission"]},
        "strategic_and_tactical_ddd": ddd,
    }


def enrich_simulation(source: dict[str, Any]) -> dict[str, Any]:
    caps = {local_capability(ref) for ref in CONCRETE}
    libs = {local_library(ref) for ref in CONCRETE}
    reqs = {f"requirement.analytics_simulation.{suffix(ref)}" for ref in CONCRETE}
    maps = {f"binding.analytics_simulation.{suffix(ref)}" for ref in CONCRETE}
    negative_ids = {f"negative.simulation.{key}" for key in ["model_reality", "scenario_forecast", "seed_stream", "run_validity", "verification_validation", "calibration_truth", "comparison_cause", "simulation_optimization", "provider_name", "agent_authority"]}
    laws = {"real system != digital twin != conceptual model != executable simulation model != provider artifact", "scenario != forecast != observed future", "seed != random-stream partition != independence evidence != replay receipt", "run completion != valid output estimate != validation", "verification != calibration != validation != universal truth", "scenario comparison != causal effect != optimized decision != authorized action", "model or agent proposal != accepted simulation semantics or evidence"}

    source["sources"] = [row for row in source["sources"] if row["source_id"] not in SELECTED_SOURCE_REFS] + source_rows()
    source["artifacts"] = [row for row in source["artifacts"] if row["artifact_id"] not in caps]
    source["libraries"] = [row for row in source["libraries"] if row["library_id"] not in libs | {"library.simulation_core"}]
    source["requirements"] = [row for row in source["requirements"] if row["requirement_id"] not in reqs]
    source["binding_maps"] = [row for row in source.get("binding_maps", []) if row["binding_map_id"] not in maps | {"binding.analytics.simulation"}]
    source["negative_tests"] = [row for row in source["negative_tests"] if row["test_id"] not in negative_ids]
    source["non_collapse_laws"] = [law for law in source["non_collapse_laws"] if law not in laws]
    source["ddd_dossiers"] = [row for row in source.get("ddd_dossiers", []) if row.get("product_ref") != PRODUCT]

    next(row for row in source["artifacts"] if row["artifact_id"] == PRODUCT).update(product_truth())
    source["artifacts"].extend(capability(ref) for ref in CONCRETE)
    source["libraries"].extend(library(ref) for ref in CONCRETE)
    for ref in CONCRETE:
        key = suffix(ref)
        source["requirements"].append({
            "requirement_id": f"requirement.analytics_simulation.{key}",
            "consumer_ref": PRODUCT,
            "capability_ref": local_capability(ref),
            "binding_phase": "runtime" if UPSTREAM[ref]["effect_boundary"] == "effectful_runtime" else "compile_time",
            "minimum_qualified_offers": 1,
            "status": "unbound",
            "refusal": f"no_qualified_{key}_implementation",
        })
        source["binding_maps"].append({
            "binding_map_id": f"binding.analytics_simulation.{key}",
            "abstract_library_ref": local_library(ref),
            "concrete_library_refs": [ref],
            "concrete_requirement_refs": UPSTREAM[ref]["requirement_refs"],
            "composition_law": "Exact one-owner simulation contribution; real-system semantics, source evidence, provider qualification, decision authority and external effects remain imported.",
            "bindability": "structurally_bindable_unqualified",
            "blocking_gap_refs": [],
            "modality_posture": "deterministic_core",
            "minimum_qualified_implementations_per_required_contract": 1,
            "portable_claim_minimum_independent_implementations": 2,
            "qualification_profile_refs": [f"receipt.operations_research.{key}"],
            "substitution_law": "Paradigm state event resource equation clock initialization warm-up randomness replication resource output uncertainty verification validation and failure semantics survive provider substitution.",
            "cross_provider_differential_required": True,
            "fallback_law": "refuse",
            "status": "candidate_not_bound",
            "product_refs": [PRODUCT],
        })
    source["ddd_dossiers"].append(dossier())
    source["negative_tests"].extend([
        {"test_id": "negative.simulation.model_reality", "prohibited_claim": "A simulation model or digital representation is the real system.", "expected_result": "retain scope assumptions representation loss and external identity"},
        {"test_id": "negative.simulation.scenario_forecast", "prohibited_claim": "A scenario is a forecast or observed future.", "expected_result": "retain scenario and forecast provenance separately"},
        {"test_id": "negative.simulation.seed_stream", "prohibited_claim": "A seed proves stream independence pairing or replay.", "expected_result": "require stream-allocation and randomness receipt"},
        {"test_id": "negative.simulation.run_validity", "prohibited_claim": "A completed run proves a valid output estimate.", "expected_result": "require replication estimand uncertainty and validity checks"},
        {"test_id": "negative.simulation.verification_validation", "prohibited_claim": "Code verification proves the model is valid for reality.", "expected_result": "appraise a separately scoped validation claim"},
        {"test_id": "negative.simulation.calibration_truth", "prohibited_claim": "Calibration proves structural truth or future validity.", "expected_result": "retain calibration scope and independent validation evidence"},
        {"test_id": "negative.simulation.comparison_cause", "prohibited_claim": "A scenario difference proves a real-world causal effect.", "expected_result": "publish model-conditional comparison only"},
        {"test_id": "negative.simulation.simulation_optimization", "prohibited_claim": "Simulation output is an optimized selected or authorized decision.", "expected_result": "require external optimization selection and authority"},
        {"test_id": "negative.simulation.provider_name", "prohibited_claim": "A simulator brand proves paradigm support reproducibility or qualification.", "expected_result": "match occurrence-scoped capabilities and receipts"},
        {"test_id": "negative.simulation.agent_authority", "prohibited_claim": "An agent-proposed model parameter scenario or explanation is accepted semantics or evidence.", "expected_result": "retain proposal taint and deterministic review obligations"},
    ])
    source["non_collapse_laws"].extend(sorted(laws))
    crosswalk = next(row for row in source["crosswalks"] if row["legacy_ref"] == "candidate.product.simulation_scenario")
    crosswalk["canonical_refs"] = [PRODUCT, "semantic.simulation_model", *[local_library(ref) for ref in CONCRETE], "standard.fmi302"]
    crosswalk["disposition"] = "split_product_exact_simulation_libraries_and_standard"
    return source
