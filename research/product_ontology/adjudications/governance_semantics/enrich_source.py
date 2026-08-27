#!/usr/bin/env python3
"""Canonically split quality operations from reconciliation/control operations.

This deterministic enrichment replaces the obsolete combined product, imports the already
researched QOR subdomain/library vocabulary, creates product-specific DDD dossiers and maps each
selected local library to the exact compiler contribution.  Accounting/control reconciliation
remains a vertical specialization; data-contract, master/reference and entity-resolution meanings
remain imported from their existing products.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from lineage_enrichment import enrich_lineage
from governance_product_enrichment import enrich_governance_products
from master_reference_split_enrichment import (
    enrich_master_reference_split,
    prepare_master_reference_regeneration,
)


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
SOURCE = HERE / "source.json"
QOR = ROOT / "research/domain_atlas/universes/quality_observability_reconciliation"
AUDIT = ROOT / "research/product_ontology/inventory_challenges/quality_reconciliation_split_audit/source.json"

OLD_REFS = {
    "product.quality_reconciliation",
    "semantic.quality_reconciliation",
    "capability.evaluate_quality",
    "capability.reconcile_discrepancy",
    "library.quality_core",
    "library.reconciliation_core",
}
PRODUCTS = {
    "product.data_quality_operations": "candidate.product.data_quality_operations",
    "product.reconciliation_control_operations": "candidate.product.reconciliation_control_operations",
}
GENERATED_PREFIXES = (
    "semantic.governance_qor.", "capability.governance_qor.", "library.governance_qor.",
    "requirement.governance_qor.", "relation.governance_qor.", "binding.governance_qor.",
    "negative.qrs.", "meaning.data_quality_", "meaning.reconciliation_control_",
)
PRODUCT_FIELDS = {
    "sovereign_question", "users", "harmed_parties", "jobs", "outcomes", "negative_mission",
    "lifecycle_states", "commands", "events", "invariants", "refusals", "automation_modality",
}

AUTOMATION = {
    "default": "DETERMINISTIC_CORE_ONLY",
    "postures": ["PROHIBITED", "OPTIONAL", "REQUIRED_BY_INTENT", "UNDETERMINED"],
    "law": "Models and agents may propose rules, matches, explanations or correction plans but never own quality or reconciliation meaning, defect/break adjudication, authority, effects, receipts, qualification or acceptance.",
    "hard_work_law": "Automation never replaces vocabulary, truth-role and population binding, invariants, lifecycle design, evidence, conformance, provider qualification or domain acceptance.",
}


def jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def pascal(value: str) -> str:
    return "".join(part.capitalize() for part in value.replace("-", "_").split("_"))


def product_spec(**kwargs: Any) -> dict[str, Any]:
    return kwargs


SPECS = {
    "product.data_quality_operations": product_spec(
        key="data_quality_operations",
        question="How can a data owner define purpose-scoped quality requirements, evaluate exact data cuts, observe change, adjudicate defects and govern quarantine, waiver, remediation and release evidence?",
        classification="core_horizontal_data_quality_operations_product",
        users=["data_quality_engineer", "data_owner", "data_steward", "data_product_operator", "consumer_reviewer"],
        harmed=["data_subject", "data_consumer", "source_owner", "decision_subject", "on_call_operator"],
        job="Operate requirements, rules, validation, profiling, change detection, quality incidents, adjudication, quarantine, waiver and remediation over exact purpose-bound data cuts.",
        outcomes=["purpose_scoped_quality_requirements", "cut_bound_validation_and_profile_evidence", "calibrated_quality_signals_and_slos", "adjudicated_defects_and_cases", "governed_quarantine_waiver_and_remediation", "fitness_verdict_with_residuals"],
        negative="Does not own source business facts, data-contract declarations, schema authority, lineage truth, master identity, entity-link decisions, reconciliation truth roles, source correction authority, independent assurance or vertical acceptance.",
        inside=["quality requirement and intended-use profiles", "quality dimensions metrics rules and test cases", "validation runs profiles baselines anomaly shift and change signals", "quality instrumentation SLOs alerts and cases", "defect adjudication quarantine release waivers and product-issued quality attestations", "quality policy sampling completeness timeliness lineage-impact and remediation verification", "evidence receipts and explicit partial or unknown outcomes"],
        outside=["data-contract and schema publication authority", "source and master-record mutation", "lineage semantic ownership", "entity resolution", "reconciliation populations truth roles and breaks", "independent assurance", "business decision and effect authority", "industry thresholds and acceptance"],
        values=["QualityRequirementId", "QualityPolicyEdition", "IntendedUseRef", "EvaluationScope", "DataCutRef", "QualityDimension", "QualityMetric", "QualityRuleEdition", "ValidationPlan", "ProfileCut", "BaselineEdition", "QualitySignal", "QualitySlo", "DefectDecision", "WaiverRef", "EvidenceReceiptRef", "FitnessVerdict"],
        entities=["QualityProgramme", "QualityRequirement", "QualityRule", "ValidationRun", "ProfileOccurrence", "Baseline", "QualityAlert", "QualityCase", "DefectAdjudication", "QuarantineLot", "Waiver", "RemediationVerification"],
        aggregates=[
            {"root": "QualityProgramme", "members": ["intended_use", "requirements", "policy", "metrics", "slos", "lifecycle"], "consistency": "one edition fixes the purpose, population, grain, measures and authority posture"},
            {"root": "ValidationRun", "members": ["plan", "data_cut", "rule_editions", "observations", "violations", "result", "receipt"], "consistency": "all outcomes bind one immutable cut and rule/policy editions"},
            {"root": "QualityCase", "members": ["signals", "evidence", "defect_decisions", "work_items", "waivers", "remediation", "state"], "consistency": "signal, adjudication, waiver, remediation and closure remain separate transitions"},
            {"root": "QuarantineLot", "members": ["subject_cut", "reason", "release_criteria", "authority", "state"], "consistency": "release requires explicit criteria, authority and evidence over the quarantined cut"},
        ],
        invariants=["quality is purpose and population scoped", "validity quality measurement and fitness verdict remain distinct", "declared contract is not observed contract", "pass fail skip error and gate disposition remain distinct", "signal is not defect and defect is not correction authority", "sampling baseline and uncertainty are explicit", "waiver does not rewrite the failed observation", "product-issued quality attestation is not independent assurance", "all effects remain typed intents behind external authority"],
        commands=["open_quality_programme", "define_intended_use", "define_quality_requirement", "register_quality_dimension", "define_quality_metric", "publish_quality_rule", "plan_validation_run", "execute_validation_run", "record_quality_observation", "publish_profile", "publish_baseline", "record_quality_signal", "evaluate_quality_slo", "open_quality_case", "adjudicate_defect", "place_quarantine", "request_waiver", "approve_waiver", "propose_remediation", "verify_remediation", "grant_release", "issue_quality_attestation", "supersede_quality_programme"],
        events=["quality_programme_opened", "intended_use_defined", "quality_requirement_defined", "quality_dimension_registered", "quality_metric_defined", "quality_rule_published", "validation_run_planned", "validation_run_executed", "quality_observation_recorded", "profile_published", "baseline_published", "quality_signal_recorded", "quality_slo_evaluated", "quality_case_opened", "defect_adjudicated", "quarantine_placed", "waiver_requested", "waiver_approved", "remediation_proposed", "remediation_verified", "release_granted", "quality_attestation_issued", "quality_programme_superseded"],
        states=["draft", "requirements_defined", "rules_ready", "active", "evaluating", "signal_open", "case_open", "adjudication_pending", "defect_confirmed", "quarantined", "waiver_pending", "remediation_pending", "retest_pending", "released", "suspended", "superseded"],
        refusals=["intended_use_missing", "population_or_grain_unbound", "data_cut_unresolved", "rule_type_invalid", "metric_unit_ambiguous", "sampling_plan_unfit", "baseline_unqualified", "provider_offer_unqualified", "evidence_incomplete", "defect_authority_missing", "quarantine_authority_missing", "waiver_scope_excessive", "remediation_effect_unauthorized", "release_criteria_unproved", "fitness_generalization_forbidden"],
        services=["QualityRequirementService", "RuleTypecheckingService", "ValidationPlanningService", "ProfilingAndBaselineService", "QualitySignalService", "FitnessEvaluationService", "DefectAdjudicationService", "QuarantineReleaseService", "WaiverService", "RemediationVerificationService"],
        specifications=["QualityProgrammeCompletenessSpecification", "EvaluationScopeSpecification", "RuleWellFormedSpecification", "SamplingFitnessSpecification", "BaselineQualificationSpecification", "DefectEvidenceSpecification", "WaiverScopeSpecification", "RemediationAcceptanceSpecification", "ReleaseReadinessSpecification"],
        policies=["when intended use or population is absent refuse fitness evaluation", "when a validation result is partial preserve skip error and unknown outcomes", "when a signal fires open or update a case without self-adjudicating a defect", "when quarantine is placed fence publication under the named authority", "when a waiver expires re-evaluate the affected cut", "when remediation occurs execute targeted and regression verification before release"],
        sagas=["QualityProgrammePublicationProcess", "ValidationExecutionProcess", "QualityIncidentProcess", "DefectAdjudicationProcess", "QuarantineReleaseProcess", "WaiverLifecycleProcess", "RemediationVerificationProcess"],
        reads=["QualityProgrammeView", "RequirementRuleGraph", "ValidationRunView", "ProfileBaselineView", "SignalSloView", "QualityCaseView", "QuarantineWaiverView", "RemediationEvidenceView", "FitnessVerdictView"],
        time=["requirement policy rule and baseline validity differ from recording time", "data cut event availability recording and evaluation times are distinct", "signal detection and case-opening times are independent", "waiver issue validity expiry and revocation are explicit", "remediation and retest cuts remain separate"],
        neighbors=[("product.data_contract_registry", "customer_supplier_acl", "import declared obligations without owning the contract"), ("product.schema_registry", "customer_supplier_acl", "import exact schemas and compatibility verdicts"), ("product.lineage_provenance", "published_language", "consume and publish scoped lineage evidence"), ("product.reference_data_governance", "anti_corruption_layer", "resolve exact reference-set editions without acquiring publication authority"), ("product.master_data_governance", "anti_corruption_layer", "resolve mastered identities without acquiring survivorship authority"), ("neighbor.entity_resolution", "anti_corruption_layer", "consume adjudicated identity links"), ("product.reconciliation_control_operations", "open_host_service", "exchange quality evidence without collapsing breaks into defects"), ("neighbor.effect_authority", "effect_port", "submit quarantine correction or release intents"), ("neighbor.independent_assurance", "customer_supplier", "submit evidence for separate appraisal")],
        nfr=["deterministic rule and policy evaluation", "declared permitted statistical approximation and uncertainty", "finite scans samples state memory time and cost", "cooperative cancellation and typed partial results", "fail-closed authority", "receipts bind programme cut rules methods providers policy and outcome"],
        language="Validity, quality, fitness, requirement, dimension, metric, rule, test, validation, observation, profile, baseline, signal, SLO, alert, case, defect, quarantine, waiver, remediation, release and attestation are non-interchangeable terms; foreign contracts, schemas, lineage and identity cross named ACLs.",
        integration="Only minimized editioned requirement, rule, validation, signal, case, defect, quarantine, waiver, remediation, release and evidence events cross the boundary; provider internals, source mutation and independent appraisal remain external.",
    ),
    "product.reconciliation_control_operations": product_spec(
        key="reconciliation_control_operations",
        question="How can a controller define and execute comparisons over identified populations and truth roles, investigate material breaks, govern adjustments and certify a bounded control occurrence without rewriting source observations?",
        classification="core_horizontal_reconciliation_control_product",
        users=["reconciliation_analyst", "operations_controller", "finance_or_control_owner", "exception_investigator", "auditor"],
        harmed=["source_owner", "accountable_controller", "customer_or_counterparty", "data_subject", "downstream_decision_maker"],
        job="Define, execute and review exact or tolerant reconciliations over immutable population cuts, manage break lifecycles and submit evidence-bound adjustment or restatement proposals to external authority.",
        outcomes=["versioned_reconciliation_definition", "matched_unmatched_and_residual_populations", "material_break_ledger", "reviewed_disposition_and_adjustment_proposal", "bounded_control_completion_evidence"],
        negative="Does not own source facts, master identity, quality fitness, industry accounting/counterparty vocabulary, book-of-record selection by default, adjustment authorization, effect execution or independent assurance.",
        inside=["comparison-side and truth-role declarations", "population cuts keys transformations match strategies tolerances and materiality", "reconciliation planning execution and residual computation", "break identity classification aging splitting merging and investigation", "defect or exception adjudication handoff", "correction proposal blast-radius and approval workflow", "waiver remediation and bounded control-completion evidence"],
        outside=["source and accounting fact ownership", "master/reference and entity-link authority", "generic quality programmes", "industry-specific control definitions", "posting or source-mutation effects", "policy and segregation-of-duties authority", "independent assurance and vertical acceptance"],
        values=["ReconciliationDefinitionId", "ReconciliationEdition", "ComparisonSide", "TruthRole", "PopulationCut", "MatchKey", "TransformationProfile", "ToleranceProfile", "MaterialityProfile", "MatchResult", "ResidualSet", "BreakId", "Disposition", "AdjustmentProposal", "ControlCompletionReceipt"],
        entities=["ReconciliationDefinition", "ReconciliationRun", "MatchOccurrence", "ReconciliationBreak", "InvestigationCase", "CorrectionProposal", "Waiver", "ControlCompletion"],
        aggregates=[
            {"root": "ReconciliationDefinition", "members": ["sides", "truth_roles", "population_selectors", "keys", "transformations", "tolerances", "materiality", "lifecycle"], "consistency": "one immutable edition fixes comparison semantics and authority assumptions"},
            {"root": "ReconciliationRun", "members": ["definition_ref", "population_cuts", "attempts", "matches", "residuals", "balance_summary", "receipt"], "consistency": "all results bind exact side cuts and one definition edition"},
            {"root": "ReconciliationBreak", "members": ["residual_ref", "classification", "materiality", "age", "evidence", "disposition", "state"], "consistency": "break history is append-only and disposition never rewrites the residual"},
            {"root": "CorrectionProposal", "members": ["break_refs", "candidate_adjustments", "blast_radius", "approvals", "effect_intents"], "consistency": "proposal approval and external effect authorization remain distinct"},
        ],
        invariants=["comparison sides populations cuts and truth roles are explicit", "exact equality and tolerant match are different relations", "balanced aggregate does not prove row equality", "break is not defect incident waiver or correction", "source accounting and control truth may lawfully disagree", "retry does not erase prior match attempts or breaks", "adjustment proposal has no posting or mutation authority", "accounting and counterparty semantics enter through vertical packs", "control completion binds residuals waivers evidence and authority scope"],
        commands=["draft_reconciliation_definition", "bind_comparison_side", "declare_truth_role", "bind_population_selector", "define_match_strategy", "define_tolerance", "define_materiality", "publish_reconciliation_edition", "plan_reconciliation_run", "execute_reconciliation_run", "record_match_result", "open_reconciliation_break", "classify_break", "split_or_merge_break", "assign_investigation", "record_break_disposition", "draft_adjustment_proposal", "assess_adjustment_blast_radius", "submit_adjustment_approval", "record_external_effect_receipt", "waive_break", "verify_remediation", "certify_control_completion", "close_reconciliation_run"],
        events=["reconciliation_definition_drafted", "comparison_side_bound", "truth_role_declared", "population_selector_bound", "match_strategy_defined", "tolerance_defined", "materiality_defined", "reconciliation_edition_published", "reconciliation_run_planned", "reconciliation_run_executed", "match_result_recorded", "reconciliation_break_opened", "break_classified", "break_split_or_merged", "investigation_assigned", "break_disposition_recorded", "adjustment_proposal_drafted", "adjustment_blast_radius_assessed", "adjustment_approval_requested", "external_effect_receipt_recorded", "break_waived", "remediation_verified", "control_completion_certified", "reconciliation_run_closed"],
        states=["definition_draft", "definition_review", "published", "run_planned", "running", "residuals_ready", "breaks_open", "investigating", "disposition_pending", "adjustment_pending", "external_effect_pending", "remediation_pending", "control_review", "completed", "completed_with_residuals", "failed", "unknown", "retired"],
        refusals=["comparison_side_missing", "truth_role_ambiguous", "population_cut_unresolved", "key_or_transformation_invalid", "tolerance_unbound", "materiality_policy_missing", "populations_incompatible", "provider_offer_unqualified", "result_completion_unknown", "break_identity_ambiguous", "disposition_authority_missing", "segregation_of_duties_violated", "adjustment_effect_unauthorized", "waiver_scope_excessive", "control_completion_unproved"],
        services=["ReconciliationDefinitionService", "PopulationCompatibilityService", "MatchPlanningService", "ResidualComputationService", "BreakLifecycleService", "MaterialityService", "CorrectionProposalService", "ControlCompletionService"],
        specifications=["ReconciliationDefinitionCompletenessSpecification", "PopulationCutSpecification", "TruthRoleSpecification", "MatchStrategySpecification", "ToleranceSpecification", "MaterialitySpecification", "BreakDispositionSpecification", "SegregationOfDutiesSpecification", "ControlCompletionSpecification"],
        policies=["when population cuts or truth roles are unresolved refuse execution", "when tolerance is absent use exact equality rather than infer a tolerance", "when a break is detected open a case without declaring a defect", "when materiality changes preserve the prior classification edition", "when an adjustment is approved submit an effect intent to external authority", "when completion is unknown reconcile provider state before retry", "when control completion is requested retain every open waived and unresolved residual"],
        sagas=["ReconciliationDefinitionPublicationProcess", "ReconciliationExecutionProcess", "BreakInvestigationProcess", "AdjustmentApprovalProcess", "UnknownCompletionRecoveryProcess", "ControlCompletionProcess"],
        reads=["ReconciliationCatalogView", "ComparisonPopulationView", "RunMatchResidualView", "BreakAgingView", "InvestigationQueueView", "AdjustmentProposalView", "WaiverRemediationView", "ControlCompletionView"],
        time=["definition and policy validity differ from recording time", "each comparison side has an exact independent cut", "event accounting and control periods remain typed", "break open materiality aging disposition and closure times are explicit", "external effect occurrence and receipt times remain separate"],
        neighbors=[("product.data_quality_operations", "open_host_service", "consume scoped validation and evidence without converting failures into breaks"), ("product.master_data_governance", "anti_corruption_layer", "resolve mastered identities without acquiring survivorship authority"), ("product.reference_data_governance", "anti_corruption_layer", "resolve exact classifications and code editions without acquiring publication authority"), ("neighbor.entity_resolution", "anti_corruption_layer", "consume adjudicated links without making match scores identity truth"), ("product.lineage_provenance", "published_language", "bind side and result derivation evidence"), ("neighbor.vertical_solution_pack", "customer_supplier", "import accounting counterparty clinical energy or other truth-role vocabulary"), ("neighbor.policy_authority", "customer_supplier", "obtain materiality waiver segregation and adjustment decisions"), ("neighbor.effect_runtime", "effect_port", "submit approved posting mutation or restatement intents"), ("neighbor.independent_assurance", "customer_supplier", "submit bounded control evidence for separate appraisal")],
        nfr=["deterministic matching under declared profiles", "explicit probabilistic matching and uncertainty when selected", "bounded population memory time cost and residual size", "backpressure cancellation and resumable partitions", "idempotent fenced attempts", "fail-closed authority", "receipts bind definitions cuts algorithms providers residuals dispositions and authority"],
        language="Side, truth role, population, cut, key, transformation, equality, tolerance, match, residual, balance, break, materiality, investigation, disposition, adjustment proposal, waiver, remediation and control completion are non-interchangeable terms; vertical, master, identity and effect meanings cross named ACLs.",
        integration="Only minimized editioned definition, run, residual, break, disposition, proposal, waiver, remediation and completion facts cross the boundary; source facts, vertical control vocabulary and external effects remain outside.",
    ),
}


DEPENDENCIES = {
    "validation_execution_kernel": ["rule_specification_kernel"],
    "test_case_management_kernel": ["validation_execution_kernel"],
    "statistical_baseline_kernel": ["data_profiling_kernel"],
    "anomaly_detection_kernel": ["statistical_baseline_kernel"],
    "distribution_shift_kernel": ["statistical_baseline_kernel"],
    "change_point_detection_kernel": ["statistical_baseline_kernel"],
    "signal_correlation_kernel": ["observability_instrumentation_kernel"],
    "quality_alerting_kernel": ["quality_slo_kernel"],
    "quality_incident_case_kernel": ["quality_alerting_kernel"],
    "defect_adjudication_kernel": ["quality_incident_case_kernel"],
    "reconciliation_execution_kernel": ["reconciliation_definition_kernel"],
    "reconciliation_break_kernel": ["reconciliation_execution_kernel"],
    "correction_proposal_kernel": ["defect_adjudication_kernel", "reconciliation_break_kernel"],
    "correction_execution_kernel": ["correction_proposal_kernel"],
    "quarantine_release_kernel": ["defect_adjudication_kernel"],
    "certification_attestation_kernel": ["evidence_receipt_kernel"],
    "remediation_verification_kernel": ["validation_execution_kernel"],
}


def local_suffix(qor_library_ref: str) -> str:
    return qor_library_ref.removeprefix("library.qor.")


def local_library_ref(suffix: str) -> str:
    return f"library.governance_qor.{suffix}"


def local_capability_ref(suffix: str) -> str:
    return f"capability.governance_qor.{suffix}"


def local_semantic_ref(suffix: str) -> str:
    return f"semantic.governance_qor.{suffix}"


def selected_assignments() -> list[dict[str, Any]]:
    audit = json.loads(AUDIT.read_text(encoding="utf-8"))
    return [
        row for row in audit["library_assignments"]
        if row["disposition"].startswith("owned_by_quality_product")
        or row["disposition"] == "owned_by_reconciliation_product"
        or row["disposition"].startswith("shared_")
    ]


def product_refs(disposition: str) -> list[str]:
    refs = []
    if disposition.startswith("owned_by_quality_product") or disposition.startswith("shared_"):
        refs.append("product.data_quality_operations")
    if disposition == "owned_by_reconciliation_product" or disposition.startswith("shared_"):
        refs.append("product.reconciliation_control_operations")
    return refs


def convert_qor_source(row: dict[str, Any]) -> dict[str, Any]:
    class_by_role = {
        "normative_authority": "official_specification",
        "open_specification": "official_specification",
        "regulatory_authority": "official_industry_framework",
        "original_research": "primary_paper",
        "implementation_evidence": "official_project_documentation",
    }
    return {
        "source_id": row["source_id"],
        "source_class": class_by_role[row["evidence_role"]],
        "title": row["title"],
        "publisher": row["publisher"],
        "uri": row["url"],
        "retrieved_at": row["accessed_at"],
        "claim": " ".join(row["claims_supported"]),
        "scope_limit": row["limitations"],
    }


def strip_managed(source: dict[str, Any]) -> dict[str, Any]:
    source = json.loads(json.dumps(source))
    for key in ("ddd_dossiers", "binding_maps", "binding_gaps", "non_collapse_laws"):
        source.pop(key, None)
    source["sources"] = [row for row in source["sources"] if not row["source_id"].startswith("qor.src.")]
    source["artifacts"] = [
        row for row in source["artifacts"]
        if row.get("artifact_id") not in OLD_REFS
        and row.get("artifact_id") not in PRODUCTS
        and row.get("artifact_id") not in {"semantic.data_quality_operations", "semantic.reconciliation_control_operations"}
        and not row.get("artifact_id", "").startswith(("semantic.governance_qor.", "capability.governance_qor."))
    ]
    source["libraries"] = [
        row for row in source["libraries"]
        if row.get("library_id") not in OLD_REFS and not row.get("library_id", "").startswith("library.governance_qor.")
    ]
    source["requirements"] = [
        row for row in source["requirements"]
        if row.get("consumer_ref") != "product.quality_reconciliation"
        and not row.get("requirement_id", "").startswith("requirement.governance_qor.")
    ]
    source["relations"] = [
        row for row in source["relations"]
        if row.get("from_ref") not in OLD_REFS | set(PRODUCTS)
        and row.get("to_ref") not in OLD_REFS | set(PRODUCTS)
        and not row.get("relation_id", "").startswith("relation.governance_qor.")
    ]
    source["boundary_decisions"] = [
        row for row in source["boundary_decisions"]
        if row.get("decision_id") not in {
            "decision.governance.quality", "decision.governance.data_quality_operations",
            "decision.governance.reconciliation_control_operations", "decision.governance.quality_reconciliation_split",
        }
    ]
    source["ownership"] = [
        row for row in source["ownership"]
        if row.get("owner_ref") != "semantic.quality_reconciliation"
        and not row.get("meaning_id", "").startswith(("meaning.data_quality_", "meaning.reconciliation_control_"))
    ]
    for row in source["ownership"]:
        excluded = row.get("must_not_be_owned_by", [])
        if "semantic.quality_reconciliation" in excluded:
            row["must_not_be_owned_by"] = [
                ref for ref in excluded if ref != "semantic.quality_reconciliation"
            ] + [
                "semantic.data_quality_operations",
                "semantic.reconciliation_control_operations",
            ]
    source["negative_tests"] = [
        row for row in source["negative_tests"] if not row.get("test_id", "").startswith("negative.qrs.")
    ]
    source["crosswalks"] = [
        row for row in source["crosswalks"]
        if row.get("legacy_ref") not in {
            "candidate.product.quality_reconciliation", "legacy.data_observability", "legacy.quality_score",
        }
    ]
    for row in source["offers"]:
        row["capability_refs"] = [ref for ref in row["capability_refs"] if ref not in OLD_REFS]
    return source


def split_test(scores: dict[str, int], evidence_refs: list[str]) -> dict[str, Any]:
    return {axis: {"score": score, "evidence_refs": evidence_refs} for axis, score in scores.items()}


def dossier(product_ref: str, spec: dict[str, Any]) -> dict[str, Any]:
    roots = [row["root"] for row in spec["aggregates"]]
    return {
        "dossier_id": f"ddd.governance.{spec['key']}",
        "product_ref": product_ref,
        "status": "candidate_not_ratified",
        "product_truth": {"sovereign_question": spec["question"], "users": spec["users"], "harmed_parties": spec["harmed"], "jobs": [spec["job"]], "measurable_outcomes": spec["outcomes"], "negative_mission": spec["negative"]},
        "strategic_and_tactical_ddd": {
            "domain_vision_statement": spec["question"].replace("How can ", "Own how ").rstrip("?"),
            "subdomain_classification": spec["classification"],
            "bounded_context_boundary": {"inside": spec["inside"], "outside": spec["outside"]},
            "ubiquitous_language_policy": spec["language"],
            "context_map": [{"neighbor_ref": ref, "relationship": rel, "translation": translation} for ref, rel, translation in spec["neighbors"]],
            "anti_corruption_layers": [f"acl.{ref.split('.')[-1]}" for ref, _, _ in spec["neighbors"]],
            "published_language": spec["values"] + ["TypedCommand", "DomainEvent", "TypedRefusal", "EvidenceReceipt"],
            "value_objects": spec["values"], "entities": spec["entities"], "aggregates": spec["aggregates"],
            "aggregate_roots": roots, "aggregate_invariants": spec["invariants"],
            "commands": spec["commands"], "domain_events": spec["events"], "refusal_failure_catalog": spec["refusals"],
            "domain_services": spec["services"],
            "application_services": [pascal(command) + "UseCase" for command in spec["commands"][:10]],
            "repositories": [root + "Repository" for root in roots],
            "factories": [root + "Factory" for root in roots] + [pascal(spec["key"]) + "EditionFactory"],
            "specifications": spec["specifications"],
            "state_machine": {"states": spec["states"], "transition_policy": "Only named commands satisfying aggregate invariants emit the corresponding past-tense event; partial and unknown completion remain explicit."},
            "policies_and_reactions": spec["policies"], "sagas_and_process_managers": spec["sagas"],
            "read_models_and_projections": spec["reads"], "integration_event_policy": spec["integration"],
            "concurrency_and_idempotency": ["optimistic aggregate edition", "idempotency key per command and effect attempt", "immutable input cuts", "append-only observations attempts decisions and receipts", "unknown completion reconciles before retry"],
            "time_model": spec["time"],
            "event_storming_swimlanes": spec["users"] + ["runtime_provider", "external_authority", "affected_party"],
            "nonfunctional_laws": spec["nfr"] + ["provider identity cannot change semantic meaning", "removing every model and agent extension preserves the complete deterministic core"],
        },
    }


def enrich(source: dict[str, Any]) -> dict[str, Any]:
    source = strip_managed(source)
    source = prepare_master_reference_regeneration(source)
    audit = json.loads(AUDIT.read_text(encoding="utf-8"))
    hypotheses = {row["local_product_ref"]: row for row in audit["replacement_hypotheses"]}
    assignments = selected_assignments()
    qor_library_rows = {
        row["library_id"].replace("qor.library.", "library.qor."): row
        for row in jsonl(QOR / "library-boundary-candidates.jsonl")
    }
    guards = {row["owner_context"]: row for row in jsonl(QOR / "invariants-refusals.jsonl")}
    selected_source_refs: set[str] = set()
    for assignment in assignments:
        selected_source_refs.update(qor_library_rows[assignment["library_ref"]]["source_refs"])
    qor_sources = {row["source_id"]: row for row in jsonl(QOR / "sources.jsonl")}
    source["sources"].extend(convert_qor_source(qor_sources[ref]) for ref in sorted(selected_source_refs))

    for product_ref, spec in SPECS.items():
        hypothesis = hypotheses[product_ref]
        source["artifacts"].append({
            "artifact_id": product_ref, "kind": "product", "name": hypothesis["name"],
            "status": "strong_product_candidate", "semantic_owner_ref": f"semantic.{spec['key']}",
            "adoption_unit": True, "operated": True, "definition": spec["question"],
            "evidence_refs": ["qor.src.w3c-dqv", "qor.src.iso25012"] if "quality" in spec["key"] else ["qor.src.bcbs239", "qor.src.xbrl-formula", "qor.src.data-diff"],
            "sovereign_question": spec["question"], "users": spec["users"], "harmed_parties": spec["harmed"],
            "jobs": [spec["job"]], "outcomes": spec["outcomes"], "negative_mission": spec["negative"],
            "lifecycle_states": spec["states"], "commands": spec["commands"], "events": spec["events"],
            "invariants": spec["invariants"], "refusals": spec["refusals"], "automation_modality": AUTOMATION,
        })
        source["artifacts"].append({
            "artifact_id": f"semantic.{spec['key']}", "kind": "semantic_contract",
            "name": hypothesis["name"] + " product semantics", "status": "candidate",
            "semantic_owner_ref": None, "adoption_unit": False, "operated": False,
            "definition": "Owns the product-level lifecycle and published language while delegating fine-grained meanings to explicit QOR bounded contexts.",
            "evidence_refs": ["qor.src.w3c-dqv"] if "quality" in spec["key"] else ["qor.src.bcbs239", "qor.src.xbrl-formula"],
        })

    source["boundary_decisions"].extend([
        {
            "decision_id": "decision.governance.data_quality_operations", "subject_ref": "product.data_quality_operations",
            "disposition": "strong_product_candidate", "rationale": "Purpose-scoped requirements, validation, profiling, signals, cases, defect adjudication, quarantine, waiver and remediation form one independently operated quality promise distinct from reconciliation.",
            "split_test": split_test(hypotheses["product.data_quality_operations"]["split_scores"], ["qor.src.iso25012", "qor.src.iso25024", "qor.src.w3c-dqv"]),
            "supersedes": ["candidate.product.quality_reconciliation"], "evidence_refs": ["qor.src.iso25012", "qor.src.iso25024", "qor.src.w3c-dqv", "evidence.great_expectations"],
        },
        {
            "decision_id": "decision.governance.reconciliation_control_operations", "subject_ref": "product.reconciliation_control_operations",
            "disposition": "strong_product_candidate", "rationale": "Comparison populations, truth roles, match/tolerance policy, material break lifecycle and control completion have distinct users, authority, lifecycle, effects and vertical applicability from quality validation.",
            "split_test": split_test(hypotheses["product.reconciliation_control_operations"]["split_scores"], ["qor.src.bcbs239", "qor.src.xbrl-formula", "qor.src.data-diff"]),
            "supersedes": ["candidate.product.quality_reconciliation"], "evidence_refs": ["qor.src.bcbs239", "qor.src.xbrl-formula", "qor.src.data-diff", "qor.src.omg-cmmn"],
        },
        {
            "decision_id": "decision.governance.quality_reconciliation_split", "subject_ref": "suite.data_governance",
            "disposition": "split_overloaded_product", "rationale": audit["ruling"],
            "evidence_refs": ["qor.src.w3c-dqv", "qor.src.bcbs239", "qor.src.data-diff"],
        },
    ])

    source["ownership"].extend([
        {"meaning_id": "meaning.data_quality_expectation", "owner_ref": "semantic.data_quality_operations", "invariant": "Requirement, intended use, population, grain, cut, measure and severity are explicit; a quality value is not universal fitness.", "must_not_be_owned_by": ["semantic.data_contract", "semantic.metadata_discovery", "semantic.reconciliation_control_operations"]},
        {"meaning_id": "meaning.reconciliation_control_disposition", "owner_ref": "semantic.reconciliation_control_operations", "invariant": "Comparison sides, truth roles, match/tolerance semantics, residual and disposition remain explicit; a break is not a defect or authorized adjustment.", "must_not_be_owned_by": ["semantic.data_quality_operations", "semantic.master_reference_data", "neighbor.identity_resolution"]},
    ])

    libraries: list[dict[str, Any]] = []
    maps: list[dict[str, Any]] = []
    for assignment in assignments:
        exact_ref = assignment["library_ref"]
        suffix = local_suffix(exact_ref)
        qor = qor_library_rows[exact_ref]
        guard = guards[qor["owner_context"]]
        refs = product_refs(assignment["disposition"])
        semantic_ref = local_semantic_ref(suffix)
        capability_ref = local_capability_ref(suffix)
        source["artifacts"].extend([
            {"artifact_id": semantic_ref, "kind": "semantic_contract", "name": qor["name"] + " semantics", "status": "candidate", "semantic_owner_ref": None, "adoption_unit": False, "operated": False, "definition": "Owns " + ", ".join(guard["invariants"]), "evidence_refs": qor["source_refs"]},
            {"artifact_id": capability_ref, "kind": "capability", "name": qor["name"] + " contract", "status": "specified_candidate", "semantic_owner_ref": semantic_ref, "adoption_unit": False, "operated": False, "definition": "Expose the typed " + qor["name"] + " operations, laws and refusals without provider defaults.", "evidence_refs": qor["source_refs"]},
        ])
        dependencies = [local_library_ref(dep) for dep in DEPENDENCIES.get(suffix, [])]
        operations = [ref.rsplit(".", 1)[-1] for ref in qor["pure_operation_refs"] + qor["effect_operation_refs"]]
        libraries.append({
            "library_id": local_library_ref(suffix), "owner_ref": semantic_ref,
            "class": "effect_port_contract" if qor["effect_operation_refs"] else ("test_oracle" if any(term in suffix for term in ("validation", "conformance", "verification")) else "semantic_pure"),
            "types": qor["input_types"] + qor["output_types"], "operations": operations,
            "decisions": [f"{suffix}_semantic_policy", "null_missing_error_policy", "evidence_and_authority_policy"],
            "invariants": guard["invariants"] + guard["must_not_collapse"],
            "refusals": [row["code"] for row in guard["refusals"]], "dependencies": dependencies,
            "effect_boundary": "pure_effect_intents" if qor["effect_operation_refs"] else "pure_no_io",
            "provides": [capability_ref], "evidence_refs": qor["source_refs"], "product_refs": refs,
        })
        for product_ref in refs:
            source["requirements"].append({
                "requirement_id": f"requirement.governance_qor.{product_ref.rsplit('.', 1)[-1]}.{suffix}",
                "consumer_ref": product_ref, "capability_ref": capability_ref,
                "binding_phase": "runtime" if qor["effect_operation_refs"] else "compile_time",
                "minimum_qualified_offers": 1, "status": "unbound", "refusal": f"no_qualified_{suffix}_implementation",
            })
            source["relations"].append({
                "relation_id": f"relation.governance_qor.{product_ref.rsplit('.', 1)[-1]}.{suffix}",
                "from_ref": product_ref, "predicate": "offers", "to_ref": capability_ref,
                "binding_phase": "compile_time", "authority_effect": "product composes the bounded context but does not acquire neighboring or provider authority",
            })
        maps.append({
            "binding_map_id": f"binding.governance_qor.{suffix}", "product_refs": refs,
            "abstract_library_ref": local_library_ref(suffix), "concrete_library_refs": [exact_ref],
            "required_requirement_refs": [f"requirement.qor.{suffix}.implementation"],
            "portable_offer_refs": [f"offer.qor.{suffix}.portable"],
            "compiler_disposition": "structurally_projected_unqualified", "gap_ref": None, "portable_offer": False,
        })
    source["libraries"].extend(libraries)
    source["binding_maps"] = maps
    source["binding_gaps"] = []
    source["ddd_dossiers"] = [dossier(product_ref, spec) for product_ref, spec in SPECS.items()]

    source["relations"].extend([
        {"relation_id": "relation.governance_qor.suite.packages_data_quality", "from_ref": "suite.data_governance", "predicate": "packages", "to_ref": "product.data_quality_operations", "binding_phase": "authoring", "authority_effect": "packaging transfers no semantic or decision authority"},
        {"relation_id": "relation.governance_qor.suite.packages_reconciliation", "from_ref": "suite.data_governance", "predicate": "packages", "to_ref": "product.reconciliation_control_operations", "binding_phase": "authoring", "authority_effect": "packaging transfers no semantic or decision authority"},
    ])
    source["crosswalks"].extend([
        {"legacy_ref": "candidate.product.quality_reconciliation", "disposition": "split_without_compatibility_alias", "canonical_refs": ["product.data_quality_operations", "product.reconciliation_control_operations"], "loss_or_warning": "Consumers must select quality, reconciliation or both from actual intent; the old combined identity is removed."},
        {"legacy_ref": "legacy.data_observability", "disposition": "split_fitness_from_derivation_and_reconciliation", "canonical_refs": ["product.data_quality_operations", "product.lineage_provenance", "product.reconciliation_control_operations"], "loss_or_warning": "Signals, derivation assertions and reconciliation breaks remain different records and authorities."},
        {"legacy_ref": "legacy.quality_score", "disposition": "narrow_to_purpose_scoped_verdict", "canonical_refs": ["semantic.data_quality_operations"], "loss_or_warning": "One score never implies universal fitness or reconciliation completion."},
    ])
    audit_negatives = json.loads(AUDIT.read_text(encoding="utf-8"))["negative_tests"]
    source["negative_tests"].extend({"test_id": row["test_id"], "input_claim": row["prohibited_claim"], "expected_refusal": row["expected_refusal"]} for row in audit_negatives)
    source["non_collapse_laws"] = audit["non_collapse_laws"] + [
        "models and agents are removable non-authoritative proposal mechanisms",
        "provider documentation and structural compiler maps do not establish qualification or portability",
    ]

    capability_by_suffix = {suffix: local_capability_ref(suffix) for suffix in [local_suffix(row["library_ref"]) for row in assignments]}
    for offer in source["offers"]:
        if offer["offer_id"] == "offer.openmetadata.quality":
            offer["capability_refs"].extend(capability_by_suffix[suffix] for suffix in ["rule_specification_kernel", "validation_execution_kernel", "data_profiling_kernel", "quality_slo_kernel", "quality_alerting_kernel", "quality_incident_case_kernel"])
        if offer["offer_id"] == "offer.gx.quality":
            offer["capability_refs"].extend(capability_by_suffix[suffix] for suffix in ["rule_specification_kernel", "validation_execution_kernel", "test_case_management_kernel", "data_profiling_kernel"])
        offer["capability_refs"] = sorted(set(offer["capability_refs"]))
    return enrich_master_reference_split(enrich_governance_products(enrich_lineage(source)))


def source_bytes() -> bytes:
    source = json.loads(SOURCE.read_text(encoding="utf-8"))
    return (json.dumps(enrich(source), ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    expected = source_bytes()
    if args.check:
        if SOURCE.read_bytes() != expected:
            print("ERROR governance source differs from canonical quality/reconciliation split enrichment")
            return 1
        print("CHECK PASS governance quality/reconciliation split enrichment")
        return 0
    SOURCE.write_bytes(expected)
    print("BUILD PASS governance quality/reconciliation split enrichment")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
