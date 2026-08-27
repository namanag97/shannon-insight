#!/usr/bin/env python3
"""Project a complete forecasting-workbench boundary into the analytical corpus.

Four method seams bind exactly.  Selection governance, forecast lifecycle, judgmental override and
publication/recall remain honest compiler-library gaps; generic artifacts cannot silently fill them.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
METHOD_ROOT = ROOT / "research/domain_atlas/universes/method_kernels"
FGL_ROOT = ROOT / "research/domain_atlas/universes/forecast_governance_lifecycle"
PRODUCT = "product.forecasting_workbench"
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
    "law": "Statistical, machine-learned, deep or foundation forecasters are interchangeable only through qualified estimator contracts. LLMs or agents may propose targets, covariates, candidate methods, overrides or explanations; deterministic temporal semantics, information-cut checks, evaluation, approval, publication and evidence determine admissibility.",
    "removal_law": "Removing every optional learned model, LLM or agent preserves time-series validation, declared classical/statistical estimator execution when selected, rolling-origin evaluation, reconciliation, forecast lifecycle, governed human override and publication/recall; an explicitly required unavailable method yields capability_unavailable.",
    "hard_work_law": "Automation never replaces target and unit meaning, observation/revision identity, origin/horizon/as-of cuts, covariate availability, missingness and censoring policy, baseline design, scoring and calibration law, hierarchy authority, override accountability, provider qualification, publication authority or realized-outcome evaluation.",
}

EXACT = [
    "library.method_kernels.time_series_semantics",
    "library.method_kernels.forecast_estimators",
    "library.method_kernels.forecast_evaluation",
    "library.method_kernels.forecast_reconciliation",
]
GAP_KEYS = [
    "forecast_selection_governance",
    "forecast_lifecycle_registry",
    "forecast_override_governance",
    "forecast_publication_recall",
]
EXACT_COMPILER_OVERRIDES = {
    "forecast_selection_governance": ["library.forecast.selection.profile.compiler", "library.forecast.selection.appraiser"],
    "forecast_lifecycle_registry": ["library.forecast.definition.compiler", "library.forecast.edition.lifecycle"],
    "forecast_override_governance": ["library.forecast.override.policy.compiler", "library.forecast.override.lifecycle", "library.forecast.override.value.evaluator"],
    "forecast_publication_recall": ["library.forecast.publication.profile.compiler"],
}
ALL_KEYS = [ref.rsplit(".", 1)[-1] for ref in EXACT] + GAP_KEYS
DEPENDENCIES = {
    "time_series_semantics": [],
    "forecast_estimators": ["time_series_semantics"],
    "forecast_evaluation": ["time_series_semantics", "forecast_estimators"],
    "forecast_reconciliation": ["time_series_semantics", "forecast_estimators"],
    "forecast_selection_governance": ["forecast_evaluation"],
    "forecast_lifecycle_registry": ["time_series_semantics", "forecast_estimators", "forecast_evaluation", "forecast_reconciliation", "forecast_selection_governance"],
    "forecast_override_governance": ["forecast_lifecycle_registry"],
    "forecast_publication_recall": ["forecast_lifecycle_registry", "forecast_override_governance"],
}
GAP_DETAILS = {
    "forecast_selection_governance": {
        "types": ["CandidateForecasterSet", "SelectionObjective", "BaselinePolicy", "EvaluationSlice", "SelectionDecision", "SelectionEvidence"],
        "operations": ["declare_candidate_set", "compare_against_baselines", "apply_selection_policy", "record_selection_decision"],
        "decisions": ["candidate_admission", "baseline_policy", "metric_precedence", "slice_robustness", "selection_approval"],
        "invariants": ["selection evidence binds exact origins horizons cuts metrics and candidates", "best historical score is not universal future superiority", "selection policy cannot grant publication authority"],
        "refusals": ["candidate_set_unbound", "baseline_missing", "metric_precedence_ambiguous", "evaluation_slice_insufficient", "selection_not_approved"],
        "statement": "No current compiler contribution owns forecast-specific candidate/baseline admission, metric precedence, slice robustness and accountable selection decisions without collapsing into generic study design or an estimator provider.",
    },
    "forecast_lifecycle_registry": {
        "types": ["ForecastDefinitionId", "ForecastEdition", "ForecastOrigin", "InformationCut", "ForecastArtifactRef", "ForecastStatus", "SupersessionLink"],
        "operations": ["register_forecast_definition", "open_forecast_edition", "attach_forecast_artifact", "transition_forecast_state", "supersede_forecast_edition"],
        "decisions": ["edition_identity", "state_transition", "artifact_admission", "revision_policy", "supersession_policy"],
        "invariants": ["forecast definition edition run and artifact occurrence are distinct", "published editions are immutable", "revisions preserve exact predecessor and information cut"],
        "refusals": ["definition_ambiguous", "edition_conflict", "artifact_cut_mismatch", "illegal_state_transition", "supersession_chain_invalid"],
        "statement": "No current compiler contribution owns the complete forecast-definition, edition, artifact, revision and supersession lifecycle with exact temporal identity and total state transitions.",
    },
    "forecast_override_governance": {
        "types": ["BaseForecastRef", "OverrideProposal", "OverrideScope", "OverrideReason", "OverrideAuthority", "OverrideDecision", "OverrideEvaluation"],
        "operations": ["propose_override", "validate_override_scope", "approve_or_reject_override", "apply_authorized_override", "evaluate_override_value"],
        "decisions": ["override_eligibility", "maker_checker", "scope_and_expiry", "conflict_precedence", "override_evaluation"],
        "invariants": ["base and overridden forecasts remain separately addressable", "proposal approval application and value evidence are distinct", "human judgment and generated proposal obey the same authority and evaluation laws"],
        "refusals": ["base_forecast_missing", "override_scope_invalid", "authority_missing", "maker_checker_violated", "override_conflict", "override_expired"],
        "statement": "No current compiler contribution owns forecast-specific override proposal, scope, authority, maker-checker, application and ex-post value evaluation while preserving the base forecast.",
    },
    "forecast_publication_recall": {
        "types": ["ForecastPublicationEdition", "AudienceScope", "DisclosurePolicy", "PublicationDecision", "ForecastSubscription", "RecallNotice", "RetractionReason"],
        "operations": ["approve_publication", "publish_forecast_edition", "deliver_subscription", "retract_or_recall_forecast", "propagate_supersession"],
        "decisions": ["publication_authority", "audience_and_purpose", "disclosure_policy", "expiry", "recall_scope"],
        "invariants": ["approval is not publication and publication is not consumption", "publication preserves origin horizon information cut uncertainty and status", "recall and supersession propagate without deleting history"],
        "refusals": ["publication_authority_missing", "audience_scope_invalid", "disclosure_denied", "forecast_not_publishable", "delivery_unknown", "recall_scope_ambiguous"],
        "statement": "No current compiler contribution owns forecast-specific publication, subscription, expiry, supersession, retraction and recall semantics with uncertainty and vintage preserved end to end.",
    },
}


def jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


UPSTREAM = {row["library_id"]: row for row in jsonl(METHOD_ROOT / "library-boundaries.jsonl")}
SOURCE_ROWS = {row["source_id"]: row for row in jsonl(METHOD_ROOT / "sources.jsonl")}
SELECTED_SOURCE_REFS = sorted({ref for ident in EXACT for ref in UPSTREAM[ident]["evidence_refs"]})
FGL_SOURCES = jsonl(FGL_ROOT / "sources.jsonl")
FGL_LIBRARIES = {row["library_id"]: row for row in jsonl(FGL_ROOT / "library-contracts.jsonl")}
FGL_COMPILER = jsonl(FGL_ROOT / "compiler-contracts.jsonl")
FGL_REQUIREMENTS = {row["subject_ref"]: row["requirement_id"] for row in FGL_COMPILER if row.get("record_kind") == "capability_requirement"}
FGL_PROFILES = {row["subject_ref"]: row["receipt_id"] for row in jsonl(FGL_ROOT / "qualification-profiles.jsonl")}
FGL_EVIDENCE_REFS = [row["source_id"] for row in FGL_SOURCES]


def key_of(ref: str) -> str:
    return ref.rsplit(".", 1)[-1]


def local_library(key: str) -> str:
    return f"library.analytics_forecasting.{key}"


def local_capability(key: str) -> str:
    return f"capability.analytics_forecasting.{key}"


def source_rows() -> list[dict[str, Any]]:
    result = []
    for ref in SELECTED_SOURCE_REFS:
        row = SOURCE_ROWS[ref]
        result.append({
            "source_id": ref,
            "source_class": "primary_research" if row["kind"] == "primary_research" else "official_specification_or_documentation",
            "title": row["title"], "publisher": row["publisher"], "uri": row["url"],
            "retrieved_at": row["accessed_at"], "claim": row["authority_scope"], "scope_limit": row["limitations"],
        })
    result.extend({"source_id": row["source_id"], "source_class": "primary_research" if any(token in row["authority"] for token in ("et al", "Hyndman", "Gneiting", "Fildes", "Makridakis", "Diebold", "Tashman")) else "official_specification_or_documentation", "title": row["title"], "publisher": row["authority"], "uri": row["url"], "retrieved_at": row["retrieved"], "claim": row["supports"], "scope_limit": row["does_not_prove"]} for row in FGL_SOURCES)
    return result


def exact_library(ref: str) -> dict[str, Any]:
    row = UPSTREAM[ref]
    key = key_of(ref)
    laws = list(row["laws"])
    laws.extend({
        "time_series_semantics": ["Event time, availability time, recording time, revision/vintage, origin, horizon and outcome-finality are non-interchangeable."],
        "forecast_estimators": ["Statistical, ML, deep and foundation forecasters share one qualified estimator contract; a method family or provider label never strengthens evidence."],
        "forecast_evaluation": ["Every score joins the exact forecast vintage to the declared outcome vintage; future information and revised actuals cannot leak silently."],
        "forecast_reconciliation": ["Base and reconciled forecasts remain traceable; coherence constraints never manufacture accuracy or business authority."],
    }[key])
    provides = [local_capability(key)]
    if key == "forecast_estimators":
        provides.append("capability.produce_forecast")
    return {
        "library_id": local_library(key), "class": row["library_kind"],
        "owner_ref": "semantic.time_series", "provides": provides,
        "types": row["public_types"], "operations": row["operation_refs"], "decisions": row["decision_refs"],
        "invariants": laws, "refusals": row["error_contracts"],
        "dependencies": [local_library(dep) for dep in DEPENDENCIES[key]],
        "effect_boundary": row["effect_boundary"], "evidence_refs": row["evidence_refs"], "product_refs": [PRODUCT],
    }


def gap_library(key: str) -> dict[str, Any]:
    spec = GAP_DETAILS[key]
    return {
        "library_id": local_library(key), "class": "semantic_policy_pure" if key != "forecast_publication_recall" else "semantic_effect_intent_port",
        "owner_ref": "semantic.forecast_lifecycle", "provides": [local_capability(key)],
        "types": spec["types"], "operations": spec["operations"], "decisions": spec["decisions"],
        "invariants": spec["invariants"], "refusals": spec["refusals"],
        "dependencies": [local_library(dep) for dep in DEPENDENCIES[key]],
        "effect_boundary": "pure_no_io" if key != "forecast_publication_recall" else "pure_effect_intents_only",
        "evidence_refs": FGL_EVIDENCE_REFS, "product_refs": [PRODUCT],
    }


def capability(key: str) -> dict[str, Any]:
    exact_ref = next((ref for ref in EXACT if key_of(ref) == key), None)
    evidence = UPSTREAM[exact_ref]["evidence_refs"] if exact_ref else FGL_EVIDENCE_REFS
    return {
        "artifact_id": local_capability(key), "kind": "capability", "name": key.replace("_", " ").title(),
        "status": "specified_candidate", "semantic_owner_ref": "semantic.time_series" if exact_ref else "semantic.forecast_lifecycle",
        "adoption_unit": False, "operated": False,
        "definition": f"Expose forecast {key.replace('_', ' ')} with origin, horizon, information, uncertainty, authority, refusal and evidence decisions explicit.",
        "evidence_refs": evidence,
    }


def product_truth() -> dict[str, Any]:
    return {
        "sovereign_question": "For an editioned target and observation history at an exact information cut, what origin/horizon-qualified forecast distribution may be produced, evaluated, selected, reconciled, responsibly overridden and published—with uncertainty, vintage and accountability intact—without becoming a fact, plan, decision or effect?",
        "users": ["forecaster", "data_scientist", "demand_or_capacity_planner", "finance_analyst", "domain_judgment_contributor", "forecast_approver", "forecast_consumer", "service_operator", "assurance_reviewer"],
        "harmed_parties": ["person_represented_in_target", "customer_or_counterparty", "worker_or_operator", "supplier_or_partner", "resource_owner", "decision_affected_party", "environment_or_public_interest"],
        "jobs": ["Define forecast targets and information availability; compare qualified forecasters against baselines; generate point/quantile/distribution forecasts; evaluate rolling origins and calibration; reconcile hierarchies; govern overrides; publish, revise, supersede or recall exact forecast vintages."],
        "outcomes": ["typed_target_series_and_vintage", "leakage_safe_temporal_design", "qualified_forecaster_selection_evidence", "origin_horizon_qualified_distribution", "rolling_origin_score_and_calibration_evidence", "traceable_coherent_reconciliation", "accountable_base_preserving_override", "editioned_publication_and_recall_receipt", "realized_outcome_evaluation_without_hindsight_rewrite"],
        "negative_mission": "Does not own source-fact truth, target business meaning, source-data quality, generic feature or predictive-model lifecycle, provider qualification, simulation or causal semantics, planning objectives and constraints, decision approval, operational action, realized outcome authority or vertical acceptance.",
        "lifecycle_states": ["draft", "target_bound", "information_contract_bound", "design_sealed", "candidate_evaluation", "selection_pending", "selected", "fit_pending", "fitted", "forecast_generated", "reconciliation_pending", "reconciled", "override_pending", "approved", "publication_pending", "published", "partially_realized", "evaluated", "retracted", "recalled", "superseded", "expired", "failed"],
        "commands": ["open_forecast_definition", "bind_target_and_unit", "bind_observation_and_revision_policy", "seal_temporal_design", "register_candidate_forecasters", "run_rolling_origin_evaluation", "select_forecaster", "fit_or_update_forecaster", "produce_forecast_distribution", "reconcile_forecast", "propose_override", "approve_or_reject_override", "approve_publication", "publish_forecast_edition", "join_realized_outcomes", "evaluate_forecast_and_override", "retract_or_recall_forecast", "supersede_forecast_definition"],
        "events": ["forecast_definition_opened", "target_and_unit_bound", "observation_and_revision_policy_bound", "temporal_design_sealed", "candidate_forecasters_registered", "rolling_origin_evaluation_completed", "forecaster_selected", "forecaster_fitted_or_updated", "forecast_distribution_produced", "forecast_reconciled", "override_proposed", "override_approved_or_rejected", "forecast_publication_approved", "forecast_edition_published", "realized_outcomes_joined", "forecast_and_override_evaluated", "forecast_retracted_or_recalled", "forecast_definition_superseded"],
        "invariants": ["target definition observation forecast plan decision action and realized outcome are distinct", "event availability recording revision origin horizon and publication times remain distinct", "forecast vintage and outcome vintage are immutable and explicit", "no future information enters training selection evaluation or production cuts", "point quantile interval sample path and full distribution are non-interchangeable output forms", "statistical ML deep and foundation models obey identical information evidence and qualification laws", "base selected reconciled overridden approved published and consumed forecasts remain separately traceable", "hierarchical coherence does not imply accuracy", "override proposal approval application and ex-post value are distinct", "a published forecast never authorizes a business action"],
        "refusals": ["target_or_unit_ambiguous", "observation_revision_identity_missing", "frequency_or_index_invalid", "information_availability_unknown", "future_information_leakage", "history_insufficient", "candidate_or_baseline_unbound", "evaluation_design_invalid", "provider_unqualified", "forecast_output_form_unsupported", "hierarchy_or_constraint_invalid", "reconciliation_failed", "override_authority_missing", "maker_checker_violated", "publication_authority_missing", "outcome_not_final_for_evaluation", "recall_scope_ambiguous", "decision_or_effect_authority_requested"],
        "automation_modality": AUTOMATION,
    }


def dossier() -> dict[str, Any]:
    truth = product_truth()
    ddd = {
        "domain_vision_statement": "Own the provider-neutral forecast-definition-to-publication lifecycle, preserving temporal information, uncertainty, method evidence, human judgment and revision identity without turning forecasts into facts, decisions or effects.",
        "subdomain_classification": "core_horizontal_forecasting_workbench_and_service_product",
        "bounded_context_boundary": {
            "inside": ["forecast target and unit binding", "time-series index observation availability revision and finality semantics", "origin horizon and information-cut contracts", "temporal train validation backtest and production cuts", "candidate forecaster and baseline selection governance", "fit update and point quantile sample or distribution production", "rolling-origin scoring calibration and stability evaluation", "hierarchical/grouped/temporal reconciliation and coherence residuals", "forecast definition edition artifact and supersession lifecycle", "base-preserving judgmental override proposal approval application and evaluation", "forecast approval publication subscription expiry retraction recall and supersession"],
            "outside": ["source-fact and target business meaning", "source-data quality lineage and feature engineering", "generic predictive-model registry deployment and serving", "method-provider qualification and portability", "causal inference simulation and optimization", "planning objective constraint and policy authority", "business decision approval and operational execution", "realized outcome ownership", "vertical acceptance"],
        },
        "ubiquitous_language_policy": "Target, observation, availability, revision, actual/final outcome, origin, horizon, information cut, forecast definition, forecaster spec, fitted forecaster, forecast run, forecast distribution, base forecast, reconciled forecast, override proposal, approved forecast, publication edition, plan, decision, action and outcome are non-interchangeable. Classical, statistical, machine-learned, deep and foundation forecasters are method/provider choices—not separate truth regimes or an ambient AI product.",
        "context_map": [
            {"neighbor_ref": "context.vertical_target_semantics", "relationship": "customer_supplier_acl", "translation": "consume target population grain unit calendar hierarchy purpose and authority without owning business meaning"},
            {"neighbor_ref": "product.data_quality", "relationship": "customer_supplier", "translation": "consume purpose-scoped history and outcome quality evidence"},
            {"neighbor_ref": "product.lineage_provenance", "relationship": "published_language", "translation": "bind exact source/model/configuration/vintage lineage and publish evaluation/override/publication receipts"},
            {"neighbor_ref": "product.model_lifecycle", "relationship": "customer_supplier_acl", "translation": "reference generic fitted artifacts and deployment evidence without surrendering forecast-specific semantics"},
            {"neighbor_ref": "product.feature_platform", "relationship": "customer_supplier", "translation": "consume time-available features under an explicit as-of contract"},
            {"neighbor_ref": "product.simulation_environment", "relationship": "anti_corruption_layer", "translation": "scenario is not forecast; simulated observations never become actuals"},
            {"neighbor_ref": "product.optimization_solver", "relationship": "published_language", "translation": "publish attributed uncertainty inputs; solver plans remain external"},
            {"neighbor_ref": "context.decision_execution", "relationship": "effect_port", "translation": "publish forecasts only; selection of action and execution remain external"},
            {"neighbor_ref": "context.provider_qualification", "relationship": "customer_supplier", "translation": "consume occurrence-scoped semantic numeric resource reproducibility and target receipts"},
        ],
        "anti_corruption_layers": ["acl.vertical_target", "acl.source_observation_and_revision", "acl.feature_availability", "acl.model_lifecycle", "acl.forecaster_provider", "acl.simulation_scenario", "acl.planning_and_decision", "acl.publication_delivery"],
        "published_language": ["ForecastDefinitionId", "ForecastDefinitionEdition", "TargetContract", "ObservationRevisionPolicy", "ForecastOrigin", "ForecastHorizon", "InformationCut", "TemporalDesignEdition", "CandidateForecasterSet", "SelectionDecision", "FittedForecasterRef", "ForecastRunId", "ForecastDistribution", "ReconciliationReceipt", "OverrideDecision", "ForecastPublicationEdition", "ForecastEvaluation", "ForecastRecallNotice", "TypedRefusal"],
        "value_objects": ["ForecastDefinitionId", "ForecastEditionId", "TargetRef", "UnitRef", "CalendarRef", "ObservationCut", "RevisionIdentity", "OutcomeFinalityPolicy", "ForecastOrigin", "ForecastHorizon", "InformationCut", "TemporalSplit", "ForecasterSpecRef", "ScoringProfile", "HierarchyRef", "OverrideScope", "PublicationAudience", "ForecastDigest"],
        "entities": ["ForecastDefinition", "TemporalDesign", "CandidateForecaster", "ForecasterSelection", "FittedForecasterOccurrence", "ForecastRun", "ForecastArtifact", "ReconciliationOccurrence", "OverrideCase", "ForecastPublication", "ForecastEvaluationOccurrence"],
        "aggregates": [
            {"root": "ForecastDefinition", "members": ["target", "unit", "calendar", "observation_policy", "horizons", "information_contract", "hierarchy", "authority_refs", "state"], "consistency": "behaviorally or semantically relevant changes create a new immutable definition edition"},
            {"root": "ForecastStudy", "members": ["definition_ref", "temporal_design", "candidates", "baselines", "metrics", "evaluations", "selection"], "consistency": "selection binds exact candidates cuts origins horizons metrics and evidence"},
            {"root": "ForecastRun", "members": ["definition_ref", "forecaster_occurrence", "origin", "horizons", "information_cut", "configuration", "output", "receipt"], "consistency": "one run binds one exact information cut and immutable output occurrence"},
            {"root": "ForecastDecisionCase", "members": ["base", "reconciliation", "override_proposals", "approval", "final_artifact"], "consistency": "base reconciled and overridden artifacts remain separately addressable and authority-bound"},
            {"root": "ForecastPublication", "members": ["approved_artifact", "audience", "purpose", "edition", "expiry", "deliveries", "recall", "supersession"], "consistency": "publication never mutates the approved forecast and recall never deletes history"},
            {"root": "ForecastEvaluationOccurrence", "members": ["forecast_vintage", "outcome_vintage", "join", "scores", "calibration", "override_value", "limitations"], "consistency": "evaluation cannot rewrite the forecast or use an undeclared actual/revision cut"},
        ],
        "aggregate_roots": ["ForecastDefinition", "ForecastStudy", "ForecastRun", "ForecastDecisionCase", "ForecastPublication", "ForecastEvaluationOccurrence"],
        "aggregate_invariants": truth["invariants"] + ["every result binds exact data model configuration provider origin horizon and information-cut digests", "manual and generated overrides obey identical authority and evidence laws", "forecaster updates create new fitted occurrences or explicit state transitions", "publication and recall operations are idempotent and receipt-bearing", "provider identity cannot change forecast meaning"],
        "commands": truth["commands"], "domain_events": truth["events"],
        "refusal_failure_catalog": truth["refusals"] + ["numerical_failure", "resource_exhausted", "cancelled", "provider_failure", "publication_delivery_unknown", "optional_assistance_unavailable"],
        "domain_services": ["TemporalSemanticsService", "InformationCutService", "ForecasterSelectionService", "ForecastProductionService", "ForecastEvaluationService", "ForecastReconciliationService", "OverrideGovernanceService", "ForecastPublicationService", "ForecastRecallService"],
        "application_services": ["OpenForecastDefinitionUseCase", "SealTemporalDesignUseCase", "EvaluateAndSelectForecasterUseCase", "ProduceForecastUseCase", "ReconcileForecastUseCase", "ReviewOverrideUseCase", "PublishForecastUseCase", "EvaluateRealizationUseCase", "RecallOrSupersedeForecastUseCase"],
        "repositories": ["ForecastDefinitionRepository", "ForecastStudyRepository", "FittedForecasterReferenceRepository", "ForecastRunRepository", "ForecastDecisionCaseRepository", "ForecastPublicationRepository", "ForecastEvaluationRepository"],
        "factories": ["ForecastDefinitionFactory", "TemporalDesignFactory", "ForecastStudyFactory", "ForecastRunFactory", "ForecastDecisionCaseFactory", "ForecastPublicationFactory", "ForecastEvaluationFactory"],
        "specifications": ["TargetAndUnitSpecification", "ObservationRevisionSpecification", "InformationAvailabilitySpecification", "LeakageSafetySpecification", "CandidateAndBaselineSpecification", "ForecastOutputFormSpecification", "EvaluationMetricSpecification", "CalibrationSpecification", "ReconciliationCoherenceSpecification", "OverrideAuthoritySpecification", "PublicationEligibilitySpecification", "RecallScopeSpecification"],
        "state_machine": {"definition": truth["lifecycle_states"], "study": ["draft", "sealed", "evaluating", "selection_pending", "selected", "refused", "superseded"], "run": ["created", "fit_pending", "fitted", "forecasting", "produced", "failed", "cancelled", "sealed"], "publication": ["draft", "approval_pending", "approved", "published", "partially_delivered", "expired", "retracted", "recalled", "superseded"]},
        "policies_and_reactions": ["when target unit calendar or outcome policy is ambiguous refuse", "when a feature was unavailable at the information cut exclude it and record the refusal", "when candidate evidence lacks a baseline prohibit selection", "when a fitted forecaster or provider changes create a new occurrence", "when hierarchy reconciliation changes values retain base values and residuals", "when an override is proposed preserve the base and require reason scope expiry and authority", "when actuals revise evaluate against declared vintages rather than rewrite history", "when publication scope or authority is missing refuse", "when material defects are found retract or recall exact editions and propagate supersession", "when a forecast is consumed for action require external planning and decision authority"],
        "sagas_and_process_managers": ["ForecastStudyProcess", "ForecasterSelectionProcess", "ForecastProductionProcess", "ForecastOverrideReviewProcess", "ForecastPublicationDeliveryProcess", "ForecastRecallProcess", "RealizationEvaluationProcess", "CrossProviderDifferentialProcess"],
        "read_models_and_projections": ["ForecastDefinitionView", "InformationAvailabilityView", "TemporalDesignView", "CandidateScorecardView", "SelectionEvidenceView", "ForecastVintageView", "HierarchyCoherenceView", "OverrideAuditView", "PublicationAndDeliveryView", "CalibrationAndAccuracyView", "RecallAndSupersessionView"],
        "integration_event_policy": "Only editioned target-binding, temporal-design, selection, fit/update, forecast, reconciliation, override, publication, realization-evaluation and recall facts cross the boundary. Source truth, provider internals, planning decisions, action effects and outcomes remain external.",
        "concurrency_and_idempotency": ["optimistic definition study decision-case and publication editions", "sealed designs and forecast artifacts are immutable", "idempotency binds definition forecaster occurrence origin horizon information cut configuration and run identity", "parallel candidate evaluations have distinct attempt identities", "override maker and checker cannot collapse when separation is required", "publication delivery is reconciled before retry", "recall and supersession are monotone append-only facts"],
        "time_model": ["target event time availability time recording time revision time origin time horizon target time publication time consumption time and evaluation time are distinct", "information cuts are closed under declared availability semantics", "forecast and actual vintages are separately immutable", "publication and override have validity and expiry", "outcome finality is policy-bound and revisable", "all scores state the forecast and outcome cuts used"],
        "event_storming_swimlanes": ["vertical_target_owner", "source_data_owner", "forecaster", "model_provider", "domain_judgment_contributor", "forecast_approver", "publication_authority", "forecast_consumer", "planning_decision_owner", "affected_party", "assurance_reviewer"],
        "nonfunctional_laws": ["finite history candidates horizons work memory threads external cost and output volume", "cooperative cancellation with typed partial-artifact validity", "numeric precision tolerances randomness and determinism are explicit", "rolling-origin leakage and revised-actual negative twins", "probabilistic calibration coverage and proper-scoring oracles", "hierarchy coherence and base/reconciled identity oracles", "unsafe FFI generated code and provider failures remain isolated", "receipts bind data model configuration provider target origin horizon information cut authority and output", "provider identity cannot change semantics", AUTOMATION["removal_law"]],
    }
    assert set(ddd) == DDD_FIELDS
    return {"dossier_id": "ddd.analytics.forecasting_workbench", "product_ref": PRODUCT, "status": "candidate_not_ratified", "product_truth": {"sovereign_question": truth["sovereign_question"], "users": truth["users"], "harmed_parties": truth["harmed_parties"], "jobs": truth["jobs"], "measurable_outcomes": truth["outcomes"], "negative_mission": truth["negative_mission"]}, "strategic_and_tactical_ddd": ddd}


def enrich_forecasting(source: dict[str, Any]) -> dict[str, Any]:
    caps = {local_capability(key) for key in ALL_KEYS}
    libs = {local_library(key) for key in ALL_KEYS}
    reqs = {f"requirement.analytics_forecasting.{key}" for key in ALL_KEYS}
    maps = {f"binding.analytics_forecasting.{key}" for key in ALL_KEYS}
    gaps = {f"gap.analytics_forecasting.{key}" for key in GAP_KEYS}
    negative_ids = {f"negative.forecast.{key}" for key in ["observation_forecast", "scenario_forecast", "point_distribution", "leakage", "provider_method", "selection_truth", "coherence_accuracy", "override_authority", "publication_action", "agent_authority"]}
    laws = {"observation != forecast != plan != decision != action != outcome", "scenario != forecast and forecast != fact", "point estimate != quantile != interval != sample path != distribution", "model family != algorithm != fitted forecaster != provider != forecast run", "base forecast != reconciled forecast != override proposal != approved forecast != publication", "coherence != accuracy and historical best != future truth", "model or agent proposal != accepted target method override evidence or authority"}

    source["sources"] = [row for row in source["sources"] if row["source_id"] not in set(SELECTED_SOURCE_REFS) | set(FGL_EVIDENCE_REFS)] + source_rows()
    source["artifacts"] = [row for row in source["artifacts"] if row["artifact_id"] not in caps]
    source["libraries"] = [row for row in source["libraries"] if row["library_id"] not in libs | {"library.forecasting_core"}]
    source["requirements"] = [row for row in source["requirements"] if row["requirement_id"] not in reqs]
    source["binding_maps"] = [row for row in source.get("binding_maps", []) if row["binding_map_id"] not in maps | {"binding.analytics.forecasting"}]
    source["binding_gaps"] = [row for row in source.get("binding_gaps", []) if row["gap_id"] not in gaps]
    source["negative_tests"] = [row for row in source["negative_tests"] if row["test_id"] not in negative_ids]
    source["non_collapse_laws"] = [law for law in source["non_collapse_laws"] if law not in laws]
    source["ddd_dossiers"] = [row for row in source.get("ddd_dossiers", []) if row.get("product_ref") != PRODUCT]

    next(row for row in source["artifacts"] if row["artifact_id"] == PRODUCT).update(product_truth())
    source["artifacts"].extend(capability(key) for key in ALL_KEYS)
    source["libraries"].extend(exact_library(ref) for ref in EXACT)
    source["libraries"].extend(gap_library(key) for key in GAP_KEYS)
    exact_by_key = {key_of(ref): ref for ref in EXACT}
    for key in ALL_KEYS:
        source["requirements"].append({"requirement_id": f"requirement.analytics_forecasting.{key}", "consumer_ref": PRODUCT, "capability_ref": local_capability(key), "binding_phase": "runtime" if key in {"forecast_estimators", "forecast_publication_recall"} else "compile_time", "minimum_qualified_offers": 1, "status": "unbound", "refusal": f"no_qualified_{key}_implementation"})
        concrete_refs = [exact_by_key[key]] if key in exact_by_key else EXACT_COMPILER_OVERRIDES.get(key, [])
        concrete_requirement_refs = (list(UPSTREAM[exact_by_key[key]]["requirement_refs"]) if key in exact_by_key else [FGL_REQUIREMENTS[ref] for ref in concrete_refs])
        qualification_profile_refs = ([f"receipt.method_kernel.{key}"] if key in exact_by_key else [FGL_PROFILES[ref] for ref in concrete_refs])
        gap_id = f"gap.analytics_forecasting.{key}"
        source["binding_maps"].append({
            "binding_map_id": f"binding.analytics_forecasting.{key}", "abstract_library_ref": local_library(key),
            "concrete_library_refs": concrete_refs,
            "concrete_requirement_refs": concrete_requirement_refs,
            "composition_law": "Exact forecast contribution; generic study, artifact, model-lifecycle, publication and provider utilities remain imports and cannot substitute for missing forecast semantics.",
            "bindability": "structurally_bindable_unqualified" if concrete_refs else "structurally_partial_blocking_gap",
            "blocking_gap_refs": [] if concrete_refs else [gap_id], "modality_posture": "deterministic_core",
            "minimum_qualified_implementations_per_required_contract": 1, "portable_claim_minimum_independent_implementations": 2,
            "qualification_profile_refs": qualification_profile_refs,
            "substitution_law": "Target unit index vintage origin horizon information cut output uncertainty selection reconciliation override authority publication revision and failure semantics survive substitution.",
            "cross_provider_differential_required": True, "fallback_law": "refuse", "status": "candidate_not_bound", "product_refs": [PRODUCT],
        })
        if not concrete_refs:
            source["binding_gaps"].append({"gap_id": gap_id, "status": "open", "product_refs": [PRODUCT], "abstract_library_refs": [local_library(key)], "missing_contracts": [key], "statement": GAP_DETAILS[key]["statement"], "compiler_disposition": f"Add an editioned compiler library contribution for {key} with exact public types, operations, decisions, laws, refusals, finite bounds, removal seams, conformance profiles and at least two independently qualified implementations."})
    source["ddd_dossiers"].append(dossier())
    source["negative_tests"].extend([
        {"test_id": "negative.forecast.observation_forecast", "prohibited_claim": "An observation, forecast, plan, decision, action and outcome are interchangeable.", "expected_result": "retain every occurrence and authority boundary"},
        {"test_id": "negative.forecast.scenario_forecast", "prohibited_claim": "A scenario is a forecast or a forecast is a fact.", "expected_result": "require attributed forecast method and vintage"},
        {"test_id": "negative.forecast.point_distribution", "prohibited_claim": "A point, quantile, interval, sample path and distribution carry the same uncertainty.", "expected_result": "preserve the declared output form"},
        {"test_id": "negative.forecast.leakage", "prohibited_claim": "Record time or revised actuals may be used even when unavailable at the forecast origin.", "expected_result": "refuse the contaminated cut"},
        {"test_id": "negative.forecast.provider_method", "prohibited_claim": "A statistical, ML, deep, foundation or vendor label proves method fitness or qualification.", "expected_result": "bind exact estimator capability and evidence"},
        {"test_id": "negative.forecast.selection_truth", "prohibited_claim": "The historically best candidate is universally best or future truth.", "expected_result": "publish scoped selection evidence and uncertainty"},
        {"test_id": "negative.forecast.coherence_accuracy", "prohibited_claim": "A coherent hierarchy proves accurate component forecasts.", "expected_result": "report coherence and accuracy separately"},
        {"test_id": "negative.forecast.override_authority", "prohibited_claim": "A human or generated override proposal is approved and beneficial.", "expected_result": "require authority application receipt and ex-post evaluation"},
        {"test_id": "negative.forecast.publication_action", "prohibited_claim": "A published forecast is a selected plan or authorized action.", "expected_result": "require external planning and decision authority"},
        {"test_id": "negative.forecast.agent_authority", "prohibited_claim": "An agent closes missing target semantics, information availability, evidence or authority.", "expected_result": "retain proposal taint and deterministic obligations"},
    ])
    source["non_collapse_laws"].extend(sorted(laws))
    crosswalk = next(row for row in source["crosswalks"] if row["legacy_ref"] == "candidate.product.forecasting")
    crosswalk["canonical_refs"] = [PRODUCT, "semantic.time_series", "semantic.forecast_lifecycle", *[local_library(key) for key in ALL_KEYS]]
    crosswalk["disposition"] = "split_product_exact_method_and_lifecycle_libraries"
    return source
