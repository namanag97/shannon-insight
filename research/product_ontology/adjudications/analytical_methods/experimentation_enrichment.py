#!/usr/bin/env python3
"""Project the exact experimentation-platform boundary into the analytical corpus."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
METHOD_ROOT = ROOT / "research/domain_atlas/universes/method_kernels"
EIAC_ROOT = ROOT / "research/domain_atlas/universes/experiment_integrity_analysis_conclusion"
PRODUCT = "product.experimentation_platform"
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
    "law": "Models, LLMs or agents may propose hypotheses, eligibility rules, variants, metrics, analysis plans or explanations only. Protocol authority, assignment and exposure identity, randomization, locked cuts, multiplicity, stopping, causal assumptions, conclusion appraisal and release authority remain deterministic and evidence-bound.",
    "removal_law": "Removing every optional learned model, LLM or agent preserves protocol authoring, eligibility, assignment replay, reproducible randomization, exposure recording, integrity monitoring, immutable analysis cuts, imported statistical/causal analysis, conclusion lifecycle and evidence publication; explicitly required assistance may instead yield capability_unavailable.",
    "hard_work_law": "Automation never replaces unit identity, population and eligibility, intervention meaning, interference assumptions, allocation ratio and random stream, persistence and override authority, actual exposure, metric grain and availability, missingness/noncompliance, sample-size and stopping law, multiplicity, estimand, uncertainty, harms review, provider qualification or vertical acceptance.",
}

EXACT = [
    "library.method_kernels.experiment_protocol_semantics",
    "library.method_kernels.experiment_assignment_state",
    "library.method_kernels.experiment_randomization_methods",
    "library.method_kernels.experiment_exposure_occurrence",
    "library.method_kernels.experiment_analysis_cut_stopping",
]
GAP_KEYS = ["experiment_monitoring_integrity", "experiment_analysis_binding", "experiment_conclusion_lifecycle"]
EXACT_COMPILER_OVERRIDES = {
    "experiment_monitoring_integrity": ["library.experiment.integrity.profile.compiler", "library.experiment.integrity.evaluator"],
    "experiment_analysis_binding": ["library.experiment.analysis_binding.compiler", "library.experiment.analysis_result.sealer"],
    "experiment_conclusion_lifecycle": ["library.experiment.conclusion.appraiser", "library.experiment.conclusion.lifecycle"],
}
ALL_KEYS = [ref.rsplit(".", 1)[-1] for ref in EXACT] + GAP_KEYS
DEPENDENCIES = {
    "experiment_protocol_semantics": [],
    "experiment_assignment_state": ["experiment_protocol_semantics"],
    "experiment_randomization_methods": ["experiment_protocol_semantics"],
    "experiment_exposure_occurrence": ["experiment_assignment_state"],
    "experiment_analysis_cut_stopping": ["experiment_protocol_semantics", "experiment_assignment_state", "experiment_exposure_occurrence"],
    "experiment_monitoring_integrity": ["experiment_assignment_state", "experiment_exposure_occurrence"],
    "experiment_analysis_binding": ["experiment_protocol_semantics", "experiment_exposure_occurrence", "experiment_analysis_cut_stopping"],
    "experiment_conclusion_lifecycle": ["experiment_analysis_binding", "experiment_monitoring_integrity"],
}
GAP_DETAILS = {
    "experiment_monitoring_integrity": {
        "types": ["IntegrityMonitorProfile", "AssignmentBalanceFinding", "ExposureMismatchFinding", "MetricPipelineFinding", "GuardrailFinding", "PauseProposal"],
        "operations": ["monitor_assignment_balance", "monitor_exposure_integrity", "monitor_metric_availability", "raise_guardrail_finding", "propose_pause"],
        "decisions": ["integrity_threshold", "guardrail_scope", "alert_severity", "pause_escalation", "monitoring_cut"],
        "invariants": ["monitoring finding is not a stopping decision", "assignment imbalance exposure mismatch and outcome effect remain distinct", "pause proposal has no release or safety authority"],
        "refusals": ["monitoring_profile_missing", "population_cut_ambiguous", "assignment_balance_uncomputable", "exposure_integrity_unknown", "guardrail_authority_missing"],
        "statement": "No current compiler contribution owns experiment-specific assignment, exposure, metric-pipeline and guardrail integrity monitoring with typed findings and non-authoritative pause escalation.",
    },
    "experiment_analysis_binding": {
        "types": ["ExperimentAnalysisEdition", "ProtocolRef", "AssignmentCutRef", "ExposureCutRef", "MetricCutRef", "EstimandBinding", "EstimatorBinding", "AnalysisResultRef"],
        "operations": ["bind_analysis_edition", "validate_protocol_cut_alignment", "bind_estimand_and_estimator", "execute_imported_analysis", "seal_analysis_result"],
        "decisions": ["analysis_population", "estimand_binding", "method_admission", "missingness_noncompliance", "result_admission"],
        "invariants": ["protocol cut estimand estimator and result edition remain traceable", "imported estimator never owns experiment lifecycle", "post-cut mutation creates a new analysis edition"],
        "refusals": ["protocol_cut_mismatch", "metric_grain_invalid", "estimand_unbound", "estimator_unqualified", "assumption_unmet", "result_cut_mismatch"],
        "statement": "No current compiler contribution owns the experiment-specific binding from sealed protocol/assignment/exposure/metric cuts to imported estimands, estimators and immutable analysis-result editions.",
    },
    "experiment_conclusion_lifecycle": {
        "types": ["ExperimentConclusion", "EpistemicStatus", "ConclusionScope", "DecisionHandoff", "ConclusionPublication", "RetractionNotice", "SupersessionLink"],
        "operations": ["draft_conclusion", "appraise_conclusion", "publish_conclusion", "handoff_decision_evidence", "retract_or_supersede_conclusion"],
        "decisions": ["claim_strength", "scope_and_limitations", "publication_authority", "decision_handoff", "retraction_recall"],
        "invariants": ["estimate conclusion decision and release are distinct", "claim strength never exceeds design and evidence", "retraction and supersession preserve history and propagate"],
        "refusals": ["analysis_not_sealed", "claim_exceeds_evidence", "scope_ambiguous", "publication_authority_missing", "decision_authority_requested", "retraction_scope_ambiguous"],
        "statement": "No current compiler contribution owns experiment-specific conclusion appraisal, epistemic status, publication, decision handoff, retraction and supersession without absorbing release authority.",
    },
}


def jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


UPSTREAM = {row["library_id"]: row for row in jsonl(METHOD_ROOT / "library-boundaries.jsonl")}
SOURCE_ROWS = {row["source_id"]: row for row in jsonl(METHOD_ROOT / "sources.jsonl")}
SELECTED_SOURCE_REFS = sorted({ref for ident in EXACT for ref in UPSTREAM[ident]["evidence_refs"]})
EIAC_SOURCES = jsonl(EIAC_ROOT / "sources.jsonl")
EIAC_LIBRARIES = {row["library_id"]: row for row in jsonl(EIAC_ROOT / "library-contracts.jsonl")}
EIAC_COMPILER = jsonl(EIAC_ROOT / "compiler-contracts.jsonl")
EIAC_REQUIREMENTS = {row["subject_ref"]: row["requirement_id"] for row in EIAC_COMPILER if row.get("record_kind") == "capability_requirement"}
EIAC_PROFILES = {row["subject_ref"]: row["receipt_id"] for row in jsonl(EIAC_ROOT / "qualification-profiles.jsonl")}
EIAC_EVIDENCE_REFS = [row["source_id"] for row in EIAC_SOURCES]


def key_of(ref: str) -> str:
    return ref.rsplit(".", 1)[-1]


def local_library(key: str) -> str:
    return f"library.analytics_experimentation.{key}"


def local_capability(key: str) -> str:
    return f"capability.analytics_experimentation.{key}"


def source_rows() -> list[dict[str, Any]]:
    result = []
    for ref in SELECTED_SOURCE_REFS:
        row = SOURCE_ROWS[ref]
        result.append({"source_id": ref, "source_class": "primary_research" if row["kind"] == "primary_research" else "official_specification_or_documentation", "title": row["title"], "publisher": row["publisher"], "uri": row["url"], "retrieved_at": row["accessed_at"], "claim": row["authority_scope"], "scope_limit": row["limitations"]})
    result.extend({"source_id": row["source_id"], "source_class": "primary_research" if "Research" in row["authority"] or "et al" in row["authority"] else "official_specification_or_documentation", "title": row["title"], "publisher": row["authority"], "uri": row["url"], "retrieved_at": row["retrieved"], "claim": row["supports"], "scope_limit": row["does_not_prove"]} for row in EIAC_SOURCES)
    return result


def capability(key: str) -> dict[str, Any]:
    exact = next((ref for ref in EXACT if key_of(ref) == key), None)
    evidence = UPSTREAM[exact]["evidence_refs"] if exact else EIAC_EVIDENCE_REFS
    return {"artifact_id": local_capability(key), "kind": "capability", "name": key.replace("_", " ").title(), "status": "specified_candidate", "semantic_owner_ref": "semantic.experiment_lifecycle", "adoption_unit": False, "operated": False, "definition": f"Expose experiment {key.replace('_', ' ')} with exact identity, time, authority, refusal and evidence contracts.", "evidence_refs": evidence}


def exact_library(ref: str) -> dict[str, Any]:
    row = UPSTREAM[ref]
    key = key_of(ref)
    laws = list(row["laws"])
    laws.extend({
        "experiment_protocol_semantics": ["A hypothesis is not a protocol; a sealed protocol is prospective and immutable."],
        "experiment_assignment_state": ["Eligibility, assignment decision, persistent assignment, override and exposure remain distinct."],
        "experiment_randomization_methods": ["Randomization receipt binds unit, epoch, strata/cluster, allocation, algorithm and random stream; assignment storage is separate."],
        "experiment_exposure_occurrence": ["Assignment is not treatment delivery or actual exposure; deduplication and event time are explicit."],
        "experiment_analysis_cut_stopping": ["Interim look, stopping decision, assignment/exposure/metric cut and final conclusion remain distinct; post-cut mutation is refused."],
    }[key])
    provides = [local_capability(key)]
    if key == "experiment_assignment_state":
        provides.append("capability.manage_experiment")
    return {"library_id": local_library(key), "class": row["library_kind"], "owner_ref": "semantic.experiment_lifecycle", "provides": provides, "types": row["public_types"], "operations": row["operation_refs"], "decisions": row["decision_refs"], "invariants": laws, "refusals": row["error_contracts"], "dependencies": [local_library(dep) for dep in DEPENDENCIES[key]], "effect_boundary": row["effect_boundary"], "evidence_refs": row["evidence_refs"], "product_refs": [PRODUCT]}


def gap_library(key: str) -> dict[str, Any]:
    spec = GAP_DETAILS[key]
    return {"library_id": local_library(key), "class": "semantic_policy_pure", "owner_ref": "semantic.experiment_lifecycle", "provides": [local_capability(key)], "types": spec["types"], "operations": spec["operations"], "decisions": spec["decisions"], "invariants": spec["invariants"], "refusals": spec["refusals"], "dependencies": [local_library(dep) for dep in DEPENDENCIES[key]], "effect_boundary": "pure_effect_intents_only" if key == "experiment_conclusion_lifecycle" else "pure_no_io", "evidence_refs": EIAC_EVIDENCE_REFS, "product_refs": [PRODUCT]}


def product_truth() -> dict[str, Any]:
    return {
        "sovereign_question": "For a prospective, authorized experiment protocol and exact unit population, what assignment, actual exposure, immutable analysis cut, scoped estimate and evidence-bounded conclusion can be established without confusing feature delivery, monitoring, inference, decision or release authority?",
        "users": ["experiment_owner", "researcher_or_data_scientist", "product_or_operations_analyst", "metric_owner", "assignment_runtime_operator", "domain_safety_or_ethics_reviewer", "decision_owner", "affected_party_representative", "assurance_reviewer"],
        "harmed_parties": ["eligible_or_excluded_unit", "experiment_participant", "customer_or_counterparty", "worker_or_operator", "nonparticipant_affected_by_interference", "decision_affected_party", "environment_or_public_interest"],
        "jobs": ["Author and seal prospective protocols; bind units, eligibility, arms, interference and metrics; generate reproducible assignments; record actual exposure; monitor integrity and guardrails; lock analysis cuts; bind qualified inferential/causal methods; appraise, publish, retract and hand off scoped conclusions."],
        "outcomes": ["sealed_prospective_protocol", "replayable_assignment_receipt", "assignment_exposure_noncollapse", "typed_noncompliance_and_integrity_findings", "immutable_assignment_exposure_metric_cut", "multiplicity_and_stopping_compliance", "estimand_and_method_bound_analysis_edition", "claim_strength_bounded_conclusion", "decision_handoff_without_release_authority"],
        "negative_mission": "Does not own treatment or feature implementation, generic metric meaning, identity/master data, source quality, generic statistical or causal estimators, consent/ethics/legal authority, business release decision, operational activation, observed downstream outcomes or vertical acceptance.",
        "lifecycle_states": ["idea", "proposal", "protocol_draft", "review_pending", "approved_to_enroll", "protocol_sealed", "assignment_ready", "enrolling", "running", "integrity_warning", "pause_proposed", "paused", "stopping_pending", "stopped", "analysis_cut_locked", "analysis_pending", "analyzed", "conclusion_review", "concluded", "published", "retracted", "superseded", "cancelled", "failed"],
        "commands": ["open_experiment_proposal", "author_protocol", "bind_unit_population_and_eligibility", "bind_arms_metrics_and_interference", "approve_and_seal_protocol", "open_assignment_epoch", "assign_eligible_unit", "record_actual_exposure", "record_noncompliance", "monitor_integrity_and_guardrails", "propose_pause_or_stop", "adjudicate_pause_or_stop", "lock_analysis_cut", "bind_estimand_and_method", "execute_analysis", "appraise_conclusion", "publish_conclusion", "handoff_decision_evidence", "retract_or_supersede_conclusion"],
        "events": ["experiment_proposal_opened", "protocol_authored", "unit_population_and_eligibility_bound", "arms_metrics_and_interference_bound", "protocol_approved_and_sealed", "assignment_epoch_opened", "eligible_unit_assigned", "actual_exposure_recorded", "noncompliance_recorded", "integrity_or_guardrail_finding_raised", "pause_or_stop_proposed", "pause_or_stop_adjudicated", "analysis_cut_locked", "estimand_and_method_bound", "experiment_analysis_executed", "conclusion_appraised", "conclusion_published", "decision_evidence_handed_off", "conclusion_retracted_or_superseded"],
        "invariants": ["hypothesis protocol assignment treatment delivery exposure metric observation estimate conclusion decision and release are distinct", "unit population eligibility arm and interference semantics are prospective and editioned", "assignment is stable and replayable within an epoch but never proves exposure", "randomization method random stream persistence and override are separately receipted", "actual exposure has event time identity deduplication and noncompliance state", "assignment exposure and metric cuts are immutable once locked", "interim looks stopping multiplicity and post-cut mutation policies are explicit", "estimate and conclusion strength never exceed protocol estimand assumptions cut and method evidence", "integrity finding or agent proposal is not pause stop or release authority", "feature flag provider is not the experiment platform and experiment conclusion never executes release"],
        "refusals": ["protocol_or_authority_missing", "unit_identity_ambiguous", "eligibility_as_of_unknown", "interference_profile_missing", "metric_grain_or_availability_invalid", "randomization_plan_invalid", "assignment_conflict", "assignment_persistence_unknown", "exposure_unlinked_or_duplicated", "guardrail_cut_ambiguous", "stopping_or_multiplicity_policy_missing", "analysis_cut_not_locked", "estimand_unbound", "method_unqualified", "assumption_unmet", "claim_exceeds_evidence", "publication_authority_missing", "release_authority_requested"],
        "automation_modality": AUTOMATION,
    }


def dossier() -> dict[str, Any]:
    truth = product_truth()
    ddd = {
        "domain_vision_statement": "Own the provider-neutral prospective experiment lifecycle from sealed protocol through assignment, actual exposure, locked analysis and scoped conclusion while preserving every identity, authority and evidence boundary.",
        "subdomain_classification": "core_horizontal_experimentation_control_and_analysis_product",
        "bounded_context_boundary": {"inside": ["experiment proposal and prospective protocol editions", "unit population eligibility arms interventions and interference profiles", "metric and guardrail references with grain and availability contracts", "assignment epochs persistence overrides and reproducible randomization", "actual exposure occurrences deduplication and noncompliance", "assignment exposure and metric integrity monitoring", "interim looks pause/stop proposals and adjudicated stopping", "immutable assignment exposure metric and information cuts", "binding imported estimands inferential tests and causal estimators to analysis editions", "conclusion epistemic status publication retraction supersession and decision handoff"], "outside": ["intervention or feature implementation and delivery runtime", "generic metric/source/master identity and quality ownership", "generic statistical and causal method semantics", "provider qualification and compute admission", "consent ethics safety legal and policy authority", "release or business decision authority", "operational activation and actual outcomes", "vertical acceptance"]},
        "ubiquitous_language_policy": "Idea, hypothesis, proposal, protocol, protocol edition, unit, population, eligibility, arm, intervention, assignment, randomization, persistence, override, exposure, noncompliance, metric observation, guardrail finding, interim look, pause proposal, stopping decision, locked cut, estimand, estimator, estimate, conclusion, publication, decision and release are non-interchangeable. Model or agent is a proposal mechanism, never a protocol or authority class.",
        "context_map": [
            {"neighbor_ref": "context.vertical_intervention_domain", "relationship": "customer_supplier_acl", "translation": "consume intervention meaning affected parties risks constraints and acceptance without owning domain policy"},
            {"neighbor_ref": "product.semantic_metric_formula", "relationship": "customer_supplier", "translation": "consume editioned metric grain population time and uncertainty contracts"},
            {"neighbor_ref": "context.identity_and_master_data", "relationship": "customer_supplier", "translation": "consume exact unit identities and equivalence authority"},
            {"neighbor_ref": "context.causal_and_statistical_methods", "relationship": "customer_supplier_acl", "translation": "bind imported estimands estimators assumptions and result algebra without absorbing them"},
            {"neighbor_ref": "context.feature_or_treatment_delivery", "relationship": "anti_corruption_layer", "translation": "assignment intent and actual treatment/exposure are recorded separately from delivery provider state"},
            {"neighbor_ref": "context.consent_ethics_safety_policy", "relationship": "customer_supplier", "translation": "consume external approvals prohibitions and revocations"},
            {"neighbor_ref": "product.lineage_provenance", "relationship": "published_language", "translation": "publish protocol assignment exposure cut analysis and conclusion evidence"},
            {"neighbor_ref": "context.release_and_decision_authority", "relationship": "effect_port", "translation": "handoff conclusion evidence only; release selection and activation remain external"},
        ],
        "anti_corruption_layers": ["acl.vertical_intervention", "acl.metric_contract", "acl.unit_identity", "acl.assignment_provider", "acl.exposure_capture", "acl.imported_analysis_method", "acl.ethics_safety_policy", "acl.release_decision"],
        "published_language": ["ExperimentId", "ProtocolEdition", "ExperimentUnitRef", "EligibilityDecision", "TreatmentArm", "InterferenceProfile", "AssignmentEpoch", "AssignmentDecision", "RandomizationReceipt", "ExposureOccurrence", "NonCompliance", "IntegrityFinding", "StoppingDecision", "LockedAnalysisCut", "ExperimentAnalysisEdition", "ExperimentConclusion", "DecisionEvidenceHandoff", "TypedRefusal"],
        "value_objects": ["ExperimentId", "ProtocolEditionId", "UnitRef", "PopulationRef", "EligibilityAsOf", "ArmId", "AllocationRatio", "AssignmentEpochId", "RandomStreamRef", "ExposureDeduplicationKey", "MetricDefinitionRef", "GuardrailProfile", "InterimLookIndex", "StoppingPolicyRef", "AnalysisCutDigest", "EstimandRef", "EstimatorRef", "EpistemicStatus"],
        "entities": ["Experiment", "ProtocolEdition", "AssignmentEpoch", "AssignmentOccurrence", "ExposureOccurrence", "IntegrityFinding", "StoppingCase", "ExperimentAnalysisEdition", "ExperimentConclusion", "ConclusionPublication"],
        "aggregates": [
            {"root": "Experiment", "members": ["proposal", "current_protocol", "epoch_refs", "analysis_refs", "conclusion_refs", "state"], "consistency": "one experiment retains immutable protocol/analysis/conclusion editions and explicit supersession"},
            {"root": "ProtocolEdition", "members": ["hypotheses", "population", "eligibility", "units", "arms", "interference", "metrics", "sample_size", "stopping", "authority", "seal"], "consistency": "a sealed protocol is prospective and immutable"},
            {"root": "AssignmentEpoch", "members": ["protocol_ref", "randomization_plan", "stream", "assignments", "persistence", "overrides", "state"], "consistency": "unit assignment is unique/stable under the declared epoch and override law"},
            {"root": "ExposureLedger", "members": ["assignment_refs", "exposures", "deduplication", "noncompliance", "capture_coverage"], "consistency": "exposure records actual delivery separately from assignment and preserve gaps/duplicates"},
            {"root": "ExperimentAnalysisEdition", "members": ["protocol_ref", "locked_cut", "estimand", "method", "result", "assumptions", "receipt"], "consistency": "analysis binds exact assignment exposure metric and information cuts and is immutable once sealed"},
            {"root": "ExperimentConclusion", "members": ["analysis_ref", "claim", "scope", "epistemic_status", "limitations", "publication", "handoff", "retraction"], "consistency": "claim strength cannot exceed design and evidence and grants no release authority"},
        ],
        "aggregate_roots": ["Experiment", "ProtocolEdition", "AssignmentEpoch", "ExposureLedger", "ExperimentAnalysisEdition", "ExperimentConclusion"],
        "aggregate_invariants": truth["invariants"] + ["all decisions and evidence bind exact protocol assignment epoch exposure cut metric edition and provider occurrences", "unknown assignment or exposure outcome is reconciled before retry", "manual and generated proposals obey identical admission laws", "revoked external authority prevents new assignments without rewriting history", "provider identity cannot change experiment semantics"],
        "commands": truth["commands"], "domain_events": truth["events"],
        "refusal_failure_catalog": truth["refusals"] + ["resource_exhausted", "cancelled", "provider_failure", "unknown_assignment_outcome", "partial_exposure_capture", "optional_assistance_unavailable"],
        "domain_services": ["ProtocolValidationService", "EligibilityService", "AssignmentAndRandomizationService", "ExposureLinkageService", "IntegrityMonitoringService", "StoppingPolicyService", "AnalysisBindingService", "ConclusionAppraisalService", "DecisionEvidenceHandoffService"],
        "application_services": ["OpenExperimentUseCase", "AuthorAndSealProtocolUseCase", "OperateAssignmentEpochUseCase", "RecordExposureUseCase", "MonitorExperimentUseCase", "PauseOrStopExperimentUseCase", "LockAndAnalyzeExperimentUseCase", "PublishConclusionUseCase", "RetractOrSupersedeConclusionUseCase"],
        "repositories": ["ExperimentRepository", "ProtocolEditionRepository", "AssignmentEpochRepository", "ExposureLedgerRepository", "IntegrityFindingRepository", "AnalysisEditionRepository", "ExperimentConclusionRepository"],
        "factories": ["ExperimentFactory", "ProtocolEditionFactory", "AssignmentEpochFactory", "ExposureOccurrenceFactory", "LockedAnalysisCutFactory", "ExperimentAnalysisEditionFactory", "ExperimentConclusionFactory"],
        "specifications": ["ProtocolCompletenessSpecification", "EligibilityAsOfSpecification", "InterferenceSpecification", "RandomizationPlanSpecification", "AssignmentUniquenessSpecification", "ExposureLinkageSpecification", "MetricAvailabilitySpecification", "IntegrityGuardrailSpecification", "StoppingMultiplicitySpecification", "AnalysisCutSpecification", "EstimandMethodSpecification", "ConclusionClaimStrengthSpecification"],
        "state_machine": {"experiment": truth["lifecycle_states"], "protocol": ["draft", "review_pending", "approved", "sealed", "superseded", "withdrawn"], "assignment_epoch": ["planned", "open", "paused", "closed", "reconciliating", "sealed"], "analysis": ["draft", "cut_pending", "cut_locked", "method_bound", "running", "analyzed", "sealed", "invalidated"], "conclusion": ["draft", "appraisal_pending", "appraised", "published", "retracted", "superseded"]},
        "policies_and_reactions": ["when protocol authority or required semantics are missing refuse enrollment", "when eligibility changes evaluate under the bound as-of policy", "when assignment outcome is unknown reconcile rather than reassign", "when exposure is missing record noncompliance or capture uncertainty rather than infer delivery", "when integrity/guardrail finding occurs create a pause proposal without silently stopping or releasing", "when interim look occurs apply declared spending/multiplicity and stopping policy", "when analysis cut locks reject mutation and create a new edition for corrections", "when imported method assumptions fail narrow or refuse the conclusion", "when external approval is revoked stop new assignment under authority while preserving history", "when conclusion is handed off require external release and activation authority"],
        "sagas_and_process_managers": ["ProtocolApprovalProcess", "AssignmentEpochProcess", "UnknownAssignmentReconciliationProcess", "ExposureCaptureProcess", "IntegrityAndGuardrailProcess", "InterimStoppingProcess", "ExperimentAnalysisProcess", "ConclusionPublicationProcess", "RetractionSupersessionProcess"],
        "read_models_and_projections": ["ExperimentPortfolioView", "ProtocolAndAuthorityView", "EligibilityAndPopulationView", "AssignmentBalanceView", "AssignmentExposureJoinView", "IntegrityGuardrailView", "InterimLookView", "LockedAnalysisCutView", "AnalysisEvidenceView", "ConclusionScopeView", "DecisionHandoffView"],
        "integration_event_policy": "Only editioned protocol, assignment, exposure, integrity, stopping, cut, analysis and conclusion facts cross the boundary. Provider internals, metric/source truth, consent/ethics/legal decisions, release commands, operational effects and outcomes remain external.",
        "concurrency_and_idempotency": ["optimistic experiment protocol epoch analysis and conclusion editions", "sealed protocols/cuts/results are immutable", "assignment idempotency binds experiment protocol epoch unit and eligibility cut", "exposure deduplication binds treatment occurrence and event time", "randomization uses explicit stream and deterministic receipt", "parallel assignments preserve allocation policy or declare imbalance", "unknown assignment/exposure outcomes reconcile before retry", "pause stop and release are external/explicit authority decisions"],
        "time_model": ["eligibility time assignment time delivery time exposure event time metric event/availability time cut time analysis time conclusion time publication time and decision time are distinct", "protocol and authority have validity/recording time", "assignment epoch bounds persistence and crossover", "late exposure/metric policies are explicit", "interim looks and stopping spend are ordered", "revocation affects future eligibility without rewriting past occurrences"],
        "event_storming_swimlanes": ["experiment_owner", "domain_intervention_owner", "unit_identity_owner", "metric_owner", "assignment_runtime", "exposure_capture", "researcher_analyst", "ethics_safety_policy_authority", "conclusion_reviewer", "release_decision_owner", "affected_party"],
        "nonfunctional_laws": ["finite population work memory concurrency cost exposure and result volume", "cooperative cancellation with typed partial validity", "assignment determinism random stream and replay are explicit", "malformed unit duplicate exposure late metric and post-cut mutation negative twins", "allocation balance attrition noncompliance multiplicity and calibration oracles", "cross-provider assignment/exposure/method differential tests", "unsafe FFI generated code and provider failures remain isolated", "receipts bind protocol unit epoch stream provider exposure cut method result and authority", "provider identity cannot change semantics", AUTOMATION["removal_law"]],
    }
    assert set(ddd) == DDD_FIELDS
    return {"dossier_id": "ddd.analytics.experimentation_platform", "product_ref": PRODUCT, "status": "candidate_not_ratified", "product_truth": {"sovereign_question": truth["sovereign_question"], "users": truth["users"], "harmed_parties": truth["harmed_parties"], "jobs": truth["jobs"], "measurable_outcomes": truth["outcomes"], "negative_mission": truth["negative_mission"]}, "strategic_and_tactical_ddd": ddd}


def enrich_experimentation(source: dict[str, Any]) -> dict[str, Any]:
    caps = {local_capability(key) for key in ALL_KEYS}
    libs = {local_library(key) for key in ALL_KEYS}
    reqs = {f"requirement.analytics_experimentation.{key}" for key in ALL_KEYS}
    maps = {f"binding.analytics_experimentation.{key}" for key in ALL_KEYS}
    gaps = {f"gap.analytics_experimentation.{key}" for key in GAP_KEYS}
    negatives = {f"negative.experiment.{key}" for key in ["hypothesis_protocol", "assignment_exposure", "flag_experiment", "randomization_persistence", "monitoring_authority", "interim_peeking", "estimate_conclusion", "conclusion_release", "provider_name", "agent_authority"]}
    laws = {"hypothesis != prospective protocol != analysis plan", "eligibility != assignment != treatment delivery != exposure != outcome", "feature flag or delivery provider != experiment platform", "randomization != assignment persistence != exposure capture", "integrity finding != pause decision != stopping decision != release decision", "estimate != conclusion != selected decision != release != outcome", "model or agent proposal != protocol evidence authority or approval"}

    source["sources"] = [row for row in source["sources"] if row["source_id"] not in set(SELECTED_SOURCE_REFS) | set(EIAC_EVIDENCE_REFS)] + source_rows()
    source["artifacts"] = [row for row in source["artifacts"] if row["artifact_id"] not in caps]
    source["libraries"] = [row for row in source["libraries"] if row["library_id"] not in libs | {"library.experiment_assignment_core"}]
    source["requirements"] = [row for row in source["requirements"] if row["requirement_id"] not in reqs]
    source["binding_maps"] = [row for row in source.get("binding_maps", []) if row["binding_map_id"] not in maps | {"binding.analytics.experiment_assignment"}]
    source["binding_gaps"] = [row for row in source.get("binding_gaps", []) if row["gap_id"] not in gaps]
    source["negative_tests"] = [row for row in source["negative_tests"] if row["test_id"] not in negatives]
    source["non_collapse_laws"] = [law for law in source["non_collapse_laws"] if law not in laws]
    source["ddd_dossiers"] = [row for row in source.get("ddd_dossiers", []) if row.get("product_ref") != PRODUCT]

    next(row for row in source["artifacts"] if row["artifact_id"] == PRODUCT).update(product_truth())
    source["artifacts"].extend(capability(key) for key in ALL_KEYS)
    source["libraries"].extend(exact_library(ref) for ref in EXACT)
    source["libraries"].extend(gap_library(key) for key in GAP_KEYS)
    exact_by_key = {key_of(ref): ref for ref in EXACT}
    for key in ALL_KEYS:
        concrete_refs = [exact_by_key[key]] if key in exact_by_key else EXACT_COMPILER_OVERRIDES.get(key, [])
        concrete_requirement_refs = ([ref for ref in UPSTREAM[exact_by_key[key]]["requirement_refs"]] if key in exact_by_key else [EIAC_REQUIREMENTS[ref] for ref in concrete_refs])
        qualification_profile_refs = ([f"receipt.method_kernel.{key.replace('semantics','').replace('methods','').replace('occurrence','').rstrip('_')}"] if key in exact_by_key else [EIAC_PROFILES[ref] for ref in concrete_refs])
        gap_id = f"gap.analytics_experimentation.{key}"
        source["requirements"].append({"requirement_id": f"requirement.analytics_experimentation.{key}", "consumer_ref": PRODUCT, "capability_ref": local_capability(key), "binding_phase": "deployment_time" if key in {"experiment_assignment_state", "experiment_exposure_occurrence", "experiment_monitoring_integrity"} else "compile_time", "minimum_qualified_offers": 1, "status": "unbound", "refusal": f"no_qualified_{key}_implementation"})
        source["binding_maps"].append({"binding_map_id": f"binding.analytics_experimentation.{key}", "abstract_library_ref": local_library(key), "concrete_library_refs": concrete_refs, "concrete_requirement_refs": concrete_requirement_refs, "composition_law": "Exact experiment-lifecycle contribution; generic analysis design, estimators, result algebra, feature delivery, policy authority and release execution remain imported.", "bindability": "structurally_bindable_unqualified" if concrete_refs else "structurally_partial_blocking_gap", "blocking_gap_refs": [] if concrete_refs else [gap_id], "modality_posture": "deterministic_core", "minimum_qualified_implementations_per_required_contract": 1, "portable_claim_minimum_independent_implementations": 2, "qualification_profile_refs": qualification_profile_refs, "substitution_law": "Protocol unit eligibility assignment randomization persistence exposure cut stopping analysis conclusion authority and failure semantics survive substitution.", "cross_provider_differential_required": True, "fallback_law": "refuse", "status": "candidate_not_bound", "product_refs": [PRODUCT]})
        if not concrete_refs:
            source["binding_gaps"].append({"gap_id": gap_id, "status": "open", "product_refs": [PRODUCT], "abstract_library_refs": [local_library(key)], "missing_contracts": [key], "statement": GAP_DETAILS[key]["statement"], "compiler_disposition": f"Add an editioned compiler library contribution for {key} with exact types, operations, decisions, laws, refusals, finite bounds, removal seams, conformance profiles and two independently qualified implementations."})
    source["ddd_dossiers"].append(dossier())
    source["negative_tests"].extend([
        {"test_id": "negative.experiment.hypothesis_protocol", "prohibited_claim": "A hypothesis or generated analysis plan is an approved prospective protocol.", "expected_result": "require sealed protocol edition and authority"},
        {"test_id": "negative.experiment.assignment_exposure", "prohibited_claim": "Assignment proves treatment delivery, exposure or outcome.", "expected_result": "retain separate linked occurrences and capture gaps"},
        {"test_id": "negative.experiment.flag_experiment", "prohibited_claim": "A feature-flag provider is the entire experiment platform.", "expected_result": "bind only exact assignment/delivery capabilities"},
        {"test_id": "negative.experiment.randomization_persistence", "prohibited_claim": "A randomization algorithm proves persistent assignment and replay.", "expected_result": "require epoch state and receipts"},
        {"test_id": "negative.experiment.monitoring_authority", "prohibited_claim": "An integrity or guardrail finding automatically pauses, stops or releases.", "expected_result": "open an externally authorized decision case"},
        {"test_id": "negative.experiment.interim_peeking", "prohibited_claim": "Any interim look may be interpreted without stopping or multiplicity policy.", "expected_result": "refuse or apply sealed policy"},
        {"test_id": "negative.experiment.estimate_conclusion", "prohibited_claim": "A statistically significant estimate is the complete experiment conclusion.", "expected_result": "appraise effect uncertainty assumptions scope harms and practical relevance"},
        {"test_id": "negative.experiment.conclusion_release", "prohibited_claim": "A published conclusion authorizes treatment or feature release.", "expected_result": "handoff evidence to external release authority"},
        {"test_id": "negative.experiment.provider_name", "prohibited_claim": "A platform brand proves protocol, assignment, exposure, analysis or qualification.", "expected_result": "bind and qualify exact occurrence capabilities"},
        {"test_id": "negative.experiment.agent_authority", "prohibited_claim": "An agent fills missing eligibility, interference, metric, evidence or authority.", "expected_result": "retain proposal taint and deterministic obligations"},
    ])
    source["non_collapse_laws"].extend(sorted(laws))
    crosswalk = next(row for row in source["crosswalks"] if row["legacy_ref"] == "candidate.product.causal_experimentation")
    crosswalk["canonical_refs"] = [PRODUCT, "semantic.experiment_lifecycle", "semantic.causal_inference", *[local_library(key) for key in ALL_KEYS], "library.causal_inference_core"]
    crosswalk["disposition"] = "split_experiment_product_exact_libraries_from_imported_causal_methods"
    return source
