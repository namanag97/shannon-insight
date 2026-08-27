#!/usr/bin/env python3
"""Project exact process/object-centric method seams into the process-mining product.

OCED, OCEL 2.0, case projection, State-Aware OCEL, temporal EKG, discovery, conformance
and performance remain distinct.  Predictive models, causal conclusions and operational
interventions remain imported or external.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
METHOD_ROOT = ROOT / "research/domain_atlas/universes/method_kernels"
PRODUCT = "product.process_mining_workbench"
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
    "law": "Models or agents may propose event mappings, activity abstractions, correlations, process hypotheses, explanations or interventions only; deterministic identity, projection, loss, method, validation, authority and evidence checks decide admissibility.",
    "removal_law": "Removing every optional predictive model or agent preserves OCED/OCEL projection, case projection, State-Aware OCEL, temporal-EKG projection, discovery, conformance, performance analysis and evidence production; explicitly requested assistance may instead yield capability_unavailable.",
    "hard_work_law": "Automation never replaces source-event semantics, object identity, correlation rules, state definitions, time/ordering policy, projection-loss accounting, method assumptions, conformance cost, performance estimands, provider qualification or vertical acceptance.",
}

CONCRETE = [
    "library.method_kernels.process_event_projection",
    "library.method_kernels.process_case_projection",
    "library.method_kernels.process_state_aware_projection",
    "library.method_kernels.process_temporal_graph_projection",
    "library.method_kernels.process_discovery_methods",
    "library.method_kernels.process_conformance_methods",
    "library.method_kernels.process_performance_methods",
]
DEPENDENCIES = {
    "process_event_projection": [],
    "process_case_projection": ["process_event_projection"],
    "process_state_aware_projection": ["process_event_projection"],
    "process_temporal_graph_projection": ["process_event_projection"],
    "process_discovery_methods": ["process_event_projection"],
    "process_conformance_methods": ["process_event_projection"],
    "process_performance_methods": ["process_event_projection"],
}
RECEIPTS = {
    "process_event_projection": "receipt.method_kernel.process_event_projection",
    "process_case_projection": "receipt.method_kernel.process_case_projection",
    "process_state_aware_projection": "receipt.method_kernel.process_state_aware_projection",
    "process_temporal_graph_projection": "receipt.method_kernel.process_temporal_graph_projection",
    "process_discovery_methods": "receipt.method_kernel.process_discovery",
    "process_conformance_methods": "receipt.method_kernel.process_conformance",
    "process_performance_methods": "receipt.method_kernel.process_performance",
}


def jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


UPSTREAM = {row["library_id"]: row for row in jsonl(METHOD_ROOT / "library-boundaries.jsonl")}
SOURCE_ROWS = {row["source_id"]: row for row in jsonl(METHOD_ROOT / "sources.jsonl")}
SELECTED_SOURCE_REFS = sorted({ref for ident in CONCRETE for ref in UPSTREAM[ident]["evidence_refs"]})


def suffix(ref: str) -> str:
    return ref.rsplit(".", 1)[-1]


def local_library(ref: str) -> str:
    return f"library.analytics_process.{suffix(ref)}"


def local_capability(ref: str) -> str:
    return f"capability.analytics_process.{suffix(ref)}"


def source_rows() -> list[dict[str, Any]]:
    return [{
        "source_id": row["source_id"],
        "source_class": "primary_research" if row["kind"] == "primary_paper" else "official_specification_or_documentation",
        "title": row["title"], "publisher": row["publisher"], "uri": row["url"],
        "retrieved_at": row["accessed_at"], "claim": row["authority_scope"],
        "scope_limit": row["limitations"],
    } for ref in SELECTED_SOURCE_REFS for row in [SOURCE_ROWS[ref]]]


def capability(ref: str) -> dict[str, Any]:
    row = UPSTREAM[ref]
    return {
        "artifact_id": local_capability(ref), "kind": "capability",
        "name": suffix(ref).replace("_", " ").title(), "status": "specified_candidate",
        "semantic_owner_ref": "semantic.process_mining", "adoption_unit": False, "operated": False,
        "definition": f"Expose exact {suffix(ref).replace('_', ' ')} semantics, decisions, losses, budgets and evidence without provider defaults.",
        "evidence_refs": row["evidence_refs"],
    }


def library(ref: str) -> dict[str, Any]:
    row = UPSTREAM[ref]
    key = suffix(ref)
    provides = [local_capability(ref)]
    if key == "process_event_projection":
        provides.append("capability.project_process_log")
    if key == "process_discovery_methods":
        provides.append("capability.discover_process_model")
    if key == "process_conformance_methods":
        provides.append("capability.check_process_conformance")
    laws = list(row["laws"])
    laws.extend({
        "process_event_projection": ["OCED core, OCEL conceptual model, exchange serialization and provider occurrence remain distinct.", "Event/object correlation is an explicit potentially many-to-many decision."],
        "process_case_projection": ["A case projection is a lossy analytical view, not canonical object-centric truth.", "Leading-object and convergence/divergence choices remain attributable."],
        "process_state_aware_projection": ["State-Aware OCEL is a derived model and not an OCEL standard edition.", "Generated state events remain distinguishable from source events."],
        "process_temporal_graph_projection": ["EKG and temporal EKG remain distinct; snapshots and successor edges are explicit derivations.", "Graph reachability does not imply causation."],
        "process_discovery_methods": ["A discovered process model is a hypothesis over an exact projection and profile, not process truth."],
        "process_conformance_methods": ["Deviation, nonconformance, defect, violation and root cause are separate judgments."],
        "process_performance_methods": ["Observed delay or bottleneck association does not prove a causal constraint or authorize intervention."],
    }[key])
    return {
        "library_id": local_library(ref), "class": row["library_kind"],
        "owner_ref": "semantic.process_mining", "provides": provides,
        "types": row["public_types"], "operations": row["operation_refs"],
        "decisions": row["decision_refs"], "invariants": laws,
        "refusals": row["error_contracts"],
        "dependencies": [f"library.analytics_process.{dep}" for dep in DEPENDENCIES[key]],
        "effect_boundary": row["effect_boundary"], "evidence_refs": row["evidence_refs"],
        "product_refs": [PRODUCT],
    }


def product_truth() -> dict[str, Any]:
    return {
        "sovereign_question": "Given source-attributed event/object occurrences and declared projection and analysis profiles, what process models, deviations, performance patterns and limitations can be established without converting association into cause or analysis into operational authority?",
        "users": ["process_analyst", "process_owner", "operations_analyst", "data_engineer", "internal_controller", "continuous_improvement_lead", "assurance_reviewer"],
        "harmed_parties": ["process_participant", "worker", "customer", "data_subject", "case_or_object_owner", "downstream_decision_subject"],
        "jobs": ["Construct governed case- and object-centric analytical projections; discover process-model hypotheses; compare observed and expected behavior; measure performance and bottlenecks; and publish evidence-linked findings with loss, uncertainty and authority limits."],
        "outcomes": ["source_attributed_oced_or_ocel_projection", "explicit_case_state_or_temporal_graph_view", "projection_loss_and_coverage_report", "versioned_discovered_model_hypothesis", "alignment_and_conformance_evidence", "performance_and_bottleneck_observation", "reviewed_process_finding_with_residuals"],
        "negative_mission": "Does not own source extraction or mutation, enterprise object identity, operational-system truth, process policy, causal root cause, quality defect adjudication, predictive model lifecycle, worker evaluation, intervention authorization, workflow execution or vertical acceptance.",
        "lifecycle_states": ["draft", "source_cut_bound", "projection_profile_pending", "projecting", "projection_partial", "projection_ready", "analysis_configured", "running", "finding_review_pending", "accepted_as_observation", "rejected", "superseded", "archived_reference"],
        "commands": ["open_process_analysis_project", "bind_source_event_cut", "define_object_identity", "define_event_object_correlation", "select_process_perspective", "project_oced_or_ocel", "define_case_projection", "derive_state_aware_ocel", "project_temporal_ekg", "configure_discovery", "discover_process_model", "configure_conformance", "check_conformance", "configure_performance_analysis", "measure_process_performance", "open_process_finding", "review_process_finding", "publish_process_evidence", "supersede_project"],
        "events": ["process_analysis_project_opened", "source_event_cut_bound", "object_identity_defined", "event_object_correlation_defined", "process_perspective_selected", "oced_or_ocel_projected", "case_projection_defined", "state_aware_ocel_derived", "temporal_ekg_projected", "discovery_configured", "process_model_discovered", "conformance_configured", "conformance_checked", "performance_analysis_configured", "process_performance_measured", "process_finding_opened", "process_finding_reviewed", "process_evidence_published", "process_project_superseded"],
        "invariants": ["person paper contribution method representation algorithm implementation dataset and standard remain distinct", "OCED core is not OCEL 2.0 or a serialization", "source event and generated event remain distinct", "case projection is not object-centric truth", "State-Aware OCEL is a derived representation not an OCEL edition", "EKG and temporal EKG remain distinct", "projection loss missingness ordering multiplicity and correlation decisions are explicit", "discovered model is a hypothesis not process truth", "conformance deviation is not defect or root cause", "performance bottleneck is not causal proof or intervention authority", "provider or expert identity cannot change semantics"],
        "refusals": ["source_cut_unbound", "event_identity_missing", "object_identity_ambiguous", "correlation_policy_missing", "incomparable_clocks", "ordering_or_multiplicity_unknown", "projection_loss_undeclared", "state_definition_missing", "temporal_snapshot_policy_missing", "discovery_assumption_unmet", "alignment_cost_profile_missing", "analysis_budget_exhausted", "performance_estimand_ambiguous", "provider_unqualified", "finding_authority_overclaimed"],
        "automation_modality": AUTOMATION,
    }


def dossier() -> dict[str, Any]:
    truth = product_truth()
    ddd = {
        "domain_vision_statement": "Own governed process-analysis projects from exact event/object projections through discovery, conformance and performance findings while preserving representation loss, evidence limits and external action authority.",
        "subdomain_classification": "core_horizontal_process_and_object_centric_mining_workbench_product",
        "bounded_context_boundary": {
            "inside": ["process-analysis project and immutable source-cut references", "event object relationship identity and correlation profiles", "OCED/OCEL case State-Aware OCEL and temporal-EKG projections", "ordering multiplicity missingness state and projection-loss records", "process perspectives variants and model editions", "discovery configurations algorithms model hypotheses and diagnostics", "alignment replay conformance cost fitness precision and deviation evidence", "performance waiting service sojourn throughput batching queue resource and bottleneck observations", "finding review supersession and evidence publication"],
            "outside": ["source connector extraction and operational mutation", "enterprise master identity and business-object authority", "source quality defect and reconciliation adjudication", "workflow/process policy ownership", "causal root-cause identification", "predictive process monitoring model lifecycle", "worker surveillance or employment decision authority", "recommendation intervention workflow execution and measured effect", "provider qualification and vertical acceptance"],
        },
        "ubiquitous_language_policy": "Source event, event occurrence, object, relation, OCED, OCEL, serialization, case, process perspective, object state, generated state event, EKG, temporal EKG, snapshot, process model, discovered hypothesis, alignment, replay, deviation, conformance, performance observation, bottleneck, finding, cause and intervention have distinct meanings. Expert authorship is evidence attribution, never runtime or semantic authority.",
        "context_map": [
            {"neighbor_ref": "product.connectivity_and_ingestion", "relationship": "customer_supplier_acl", "translation": "consume immutable source occurrence cuts and capture evidence without owning extraction"},
            {"neighbor_ref": "product.master_data_governance", "relationship": "anti_corruption_layer", "translation": "consume object identity mappings without acquiring master-domain or survivorship authority"},
            {"neighbor_ref": "product.data_quality_operations", "relationship": "open_host_service", "translation": "consume scoped quality evidence without converting projection gaps into defects"},
            {"neighbor_ref": "product.lineage_provenance", "relationship": "published_language", "translation": "bind every projection model result and finding to exact source and method cuts"},
            {"neighbor_ref": "product.semantic_metric_formula", "relationship": "customer_supplier", "translation": "consume governed measures units dimensions and formulas for performance estimands"},
            {"neighbor_ref": "product.predictive_model_lifecycle", "relationship": "anti_corruption_layer", "translation": "predictive process monitoring remains an optional separate model product"},
            {"neighbor_ref": "product.reconciliation_control_operations", "relationship": "customer_supplier", "translation": "exchange deviations and control evidence without collapsing them into breaks"},
            {"neighbor_ref": "context.causal_analysis", "relationship": "anti_corruption_layer", "translation": "submit diagnostic hypotheses for a separate causal design"},
            {"neighbor_ref": "context.operational_decision_authority", "relationship": "effect_port", "translation": "publish findings or intervention proposals only"},
        ],
        "anti_corruption_layers": ["acl.source_occurrence", "acl.master_identity", "acl.quality_reconciliation", "acl.lineage_evidence", "acl.semantic_measure", "acl.predictive_model", "acl.causal_analysis", "acl.operational_authority"],
        "published_language": ["ProcessAnalysisProjectId", "SourceEventCutRef", "EventIdentity", "ObjectIdentity", "QualifiedRelation", "CorrelationProfileEdition", "ProcessPerspective", "OcedView", "OcelView", "CaseDefinition", "ProjectionLoss", "StateAwareOcel", "TemporalEventKnowledgeGraph", "ProcessModelEdition", "DiscoveryProfile", "AlignmentProfile", "ConformanceResult", "PerformanceProfile", "ProcessFinding", "EvidenceReceipt", "TypedRefusal"],
        "value_objects": ["ProjectId", "SourceCutRef", "EventOccurrenceRef", "ObjectRef", "ActivityRef", "QualifiedRelation", "CorrelationProfileEdition", "OrderingPolicy", "MultiplicityPolicy", "MissingnessPolicy", "ProcessPerspective", "ProjectionDigest", "ProjectionLoss", "StateDefinitionEdition", "TemporalSnapshotPolicy", "ModelDigest", "AlignmentCostProfile", "PerformanceEstimand", "WorkBudget"],
        "entities": ["ProcessAnalysisProject", "ProjectionOccurrence", "ProcessModelEdition", "AnalysisRun", "AlignmentOccurrence", "ConformanceAssessment", "PerformanceAssessment", "ProcessFinding", "FindingReview"],
        "aggregates": [
            {"root": "ProcessAnalysisProject", "members": ["question", "source_cuts", "projection_profiles", "analysis_profiles", "runs", "findings", "state"], "consistency": "one project edition fixes its analytical question, perspectives, authority posture and acceptance criteria"},
            {"root": "ProjectionOccurrence", "members": ["source_cut", "identity_rules", "correlation", "ordering", "multiplicity", "state_rules", "output", "loss", "receipt"], "consistency": "every derived view binds exact source and profile editions and retains partiality and loss"},
            {"root": "ProcessModelEdition", "members": ["model_language", "structure", "discovery_run", "input_projection", "diagnostics", "status"], "consistency": "a model edition is an immutable hypothesis over one projection and discovery profile"},
            {"root": "ProcessAnalysisRun", "members": ["method", "projection_ref", "model_ref", "configuration", "budget", "partial_results", "result", "receipt"], "consistency": "results never exceed method assumptions input coverage and execution evidence"},
            {"root": "ProcessFinding", "members": ["observation", "witness", "limitations", "candidate_explanations", "review", "authority", "state"], "consistency": "observation hypothesis cause recommendation intervention and effect remain separate"},
        ],
        "aggregate_roots": ["ProcessAnalysisProject", "ProjectionOccurrence", "ProcessModelEdition", "ProcessAnalysisRun", "ProcessFinding"],
        "aggregate_invariants": truth["invariants"] + ["same frozen inputs profiles algorithms and deterministic configuration produce the same canonical projection and finding", "all random streams approximations and cancellation limits are declared", "no result claim is stronger than source coverage projection loss and method evidence"],
        "commands": truth["commands"], "domain_events": truth["events"],
        "refusal_failure_catalog": truth["refusals"] + ["analysis_cancelled", "partial_result_only", "causal_claim_unsupported", "intervention_authority_missing", "optional_assistance_unavailable"],
        "domain_services": ["EventObjectIdentityService", "ProjectionPlanningService", "ProjectionLossService", "StateDerivationService", "TemporalGraphProjectionService", "DiscoveryEvaluationService", "ConformanceAssessmentService", "PerformanceAnalysisService", "FindingAppraisalService"],
        "application_services": ["OpenProcessProjectUseCase", "BindEventDataUseCase", "ProjectObjectCentricViewUseCase", "ProjectCaseViewUseCase", "DeriveStateAwareViewUseCase", "ProjectTemporalEkgUseCase", "DiscoverModelUseCase", "CheckConformanceUseCase", "AnalyzePerformanceUseCase", "ReviewFindingUseCase", "PublishEvidenceUseCase"],
        "repositories": ["ProcessAnalysisProjectRepository", "ProjectionOccurrenceRepository", "ProcessModelRepository", "ProcessAnalysisRunRepository", "ProcessFindingRepository"],
        "factories": ["ProcessAnalysisProjectFactory", "ProjectionOccurrenceFactory", "ProcessModelEditionFactory", "ProcessAnalysisRunFactory", "ProcessFindingFactory"],
        "specifications": ["SourceCutCompletenessSpecification", "ObjectIdentitySpecification", "CorrelationProfileSpecification", "ProjectionLossSpecification", "StateDefinitionSpecification", "TemporalSnapshotSpecification", "DiscoveryApplicabilitySpecification", "AlignmentCostSpecification", "ConformanceEvidenceSpecification", "PerformanceEstimandSpecification", "FindingClaimSpecification"],
        "state_machine": {"project": truth["lifecycle_states"], "projection": ["planned", "running", "partial", "ambiguous", "ready", "rejected", "superseded"], "finding": ["draft", "observation_supported", "hypothesis_only", "review_pending", "accepted_as_observation", "rejected", "superseded"]},
        "policies_and_reactions": ["when event/object identity is ambiguous quarantine rather than guess", "when a case view is requested record convergence divergence and excluded behavior", "when state events are generated mark their derivation and never present them as source events", "when temporal snapshots are projected preserve entity-time and successor semantics", "when discovery completes publish a hypothesis with diagnostics rather than process truth", "when conformance deviation appears open a finding without declaring defect or cause", "when a bottleneck is observed publish scope and uncertainty and require separate intervention authority", "when optional predictive or agent assistance is removed retain the complete descriptive diagnostic and conformance path"],
        "sagas_and_process_managers": ["EventDataProjectionProcess", "StateAwareProjectionProcess", "TemporalEkgProjectionProcess", "DiscoveryEvaluationProcess", "ConformanceAnalysisProcess", "PerformanceFindingProcess", "FindingReviewAndPublicationProcess"],
        "read_models_and_projections": ["ProjectOverview", "EventObjectIdentityView", "ProjectionCoverageLossView", "ObjectCentricGraphView", "CaseVariantView", "StateEvolutionView", "TemporalEkgView", "DiscoveredModelView", "AlignmentDeviationView", "PerformanceBottleneckView", "FindingEvidenceView"],
        "integration_event_policy": "Only editioned projection, model, analysis, deviation, performance, finding, limitation and evidence facts cross the boundary. Source mutations, quality/defect judgments, causal claims, personnel decisions, intervention authorizations and operational effects remain external.",
        "concurrency_and_idempotency": ["optimistic project and finding editions", "idempotency keys bind source cut projection profile algorithm configuration and run identity", "retries create distinct run occurrences", "projections models analyses and findings are immutable editions", "parallel projection declares partition and merge laws", "partial cancellation results retain validity scope", "late source events create new cuts rather than rewrite published evidence"],
        "time_model": ["source event validity observation recording ingestion and availability times are distinct", "object attribute validity differs from event time", "generated state-event time and derivation recording time are explicit", "temporal-EKG snapshots bind entity-valid time and snapshot sequence", "case duration waiting service sojourn and calendar time remain distinct", "model discovery conformance analysis review and publication times are separate", "all results bind exact bitemporal source and projection cuts"],
        "event_storming_swimlanes": ["source_owner", "data_engineer", "process_analyst", "process_owner", "operations_controller", "method_provider", "finding_reviewer", "causal_analyst", "decision_authority", "affected_participant"],
        "nonfunctional_laws": ["deterministic identity projection loss and exact-profile analysis", "finite event object edge state graph alignment time memory and cost budgets", "cooperative cancellation and typed partial artifacts", "declared randomness approximation and schedule dependence", "cross-provider differential and negative-twin fixtures", "receipts bind source projection model algorithm provider configuration and result", "provider or expert identity cannot change semantic meaning", AUTOMATION["removal_law"]],
    }
    assert set(ddd) == DDD_FIELDS
    return {"dossier_id": "ddd.analytics.process_mining_workbench", "product_ref": PRODUCT, "status": "candidate_not_ratified", "product_truth": {"sovereign_question": truth["sovereign_question"], "users": truth["users"], "harmed_parties": truth["harmed_parties"], "jobs": truth["jobs"], "measurable_outcomes": truth["outcomes"], "negative_mission": truth["negative_mission"]}, "strategic_and_tactical_ddd": ddd}


def enrich_process(source: dict[str, Any]) -> dict[str, Any]:
    caps = {local_capability(ref) for ref in CONCRETE}
    libs = {local_library(ref) for ref in CONCRETE}
    reqs = {f"requirement.analytics_process.{suffix(ref)}" for ref in CONCRETE}
    maps = {f"binding.analytics_process.{suffix(ref)}" for ref in CONCRETE}
    negative_ids = {f"negative.process.{key}" for key in ["person_semantics", "oced_ocel", "case_truth", "state_source", "ekg_tekg", "model_truth", "deviation_cause", "bottleneck_cause", "predictive_core", "agent_authority"]}
    laws = {"person != paper != contribution != method != representation != algorithm != implementation != dataset != standard", "OCED core != OCEL 2.0 != serialization != provider occurrence", "source event != generated state event", "case projection != object-centric truth", "EKG != temporal EKG", "discovered model != process truth", "deviation != defect != root cause", "bottleneck association != causal constraint != intervention authority", "predictive model or agent proposal != deterministic process evidence"}
    source["sources"] = [row for row in source["sources"] if row["source_id"] not in SELECTED_SOURCE_REFS] + source_rows()
    source["artifacts"] = [row for row in source["artifacts"] if row["artifact_id"] not in caps]
    source["libraries"] = [row for row in source["libraries"] if row["library_id"] not in libs | {"library.process_projection_core", "library.process_analysis_core"}]
    source["requirements"] = [row for row in source["requirements"] if row["requirement_id"] not in reqs]
    source["binding_maps"] = [row for row in source.get("binding_maps", []) if row["binding_map_id"] not in maps | {"binding.analytics.process_projection", "binding.analytics.process_analysis"}]
    source["negative_tests"] = [row for row in source["negative_tests"] if row["test_id"] not in negative_ids]
    source["non_collapse_laws"] = [law for law in source["non_collapse_laws"] if law not in laws]
    source["ddd_dossiers"] = [row for row in source.get("ddd_dossiers", []) if row.get("product_ref") != PRODUCT]

    next(row for row in source["artifacts"] if row["artifact_id"] == PRODUCT).update(product_truth())
    source["artifacts"].extend(capability(ref) for ref in CONCRETE)
    source["libraries"].extend(library(ref) for ref in CONCRETE)
    for ref in CONCRETE:
        key = suffix(ref)
        source["requirements"].append({"requirement_id": f"requirement.analytics_process.{key}", "consumer_ref": PRODUCT, "capability_ref": local_capability(ref), "binding_phase": "compile_time" if "projection" in key else "runtime", "minimum_qualified_offers": 1, "status": "unbound", "refusal": f"no_qualified_{key}_implementation"})
        source["binding_maps"].append({
            "binding_map_id": f"binding.analytics_process.{key}", "abstract_library_ref": local_library(ref),
            "concrete_library_refs": [ref], "concrete_requirement_refs": UPSTREAM[ref]["requirement_refs"],
            "composition_law": "Exact single-owner process contribution; generic artifact, result, qualification, prediction and effect contracts remain imported.",
            "bindability": "structurally_bindable_unqualified", "blocking_gap_refs": [], "modality_posture": "deterministic_core",
            "minimum_qualified_implementations_per_required_contract": 1, "portable_claim_minimum_independent_implementations": 2,
            "qualification_profile_refs": [RECEIPTS[key]],
            "substitution_law": "Identity correlation ordering multiplicity time projection loss method assumptions resource behavior partiality and evidence survive provider substitution.",
            "cross_provider_differential_required": True, "fallback_law": "refuse", "status": "candidate_not_bound", "product_refs": [PRODUCT],
        })
    source["ddd_dossiers"].append(dossier())
    source["negative_tests"].extend([
        {"test_id": "negative.process.person_semantics", "prohibited_claim": "An expert name, paper or tool owns product semantics.", "expected_result": "resolve exact contribution and canonical owner"},
        {"test_id": "negative.process.oced_ocel", "prohibited_claim": "OCED core, OCEL 2.0, serialization and provider occurrence are interchangeable.", "expected_result": "retain separate identities and explicit mappings"},
        {"test_id": "negative.process.case_truth", "prohibited_claim": "One case projection is canonical object-centric truth.", "expected_result": "publish perspective and projection loss"},
        {"test_id": "negative.process.state_source", "prohibited_claim": "A generated State-Aware OCEL event occurred in the source system.", "expected_result": "retain generated-event derivation"},
        {"test_id": "negative.process.ekg_tekg", "prohibited_claim": "An EKG and temporal EKG have identical snapshot and succession semantics.", "expected_result": "require the exact temporal representation contract"},
        {"test_id": "negative.process.model_truth", "prohibited_claim": "A discovered process model is the true process.", "expected_result": "publish a scoped model hypothesis"},
        {"test_id": "negative.process.deviation_cause", "prohibited_claim": "A conformance deviation proves defect or root cause.", "expected_result": "open a bounded observation/finding"},
        {"test_id": "negative.process.bottleneck_cause", "prohibited_claim": "An observed bottleneck proves the causal constraint and authorizes intervention.", "expected_result": "require causal appraisal and external authority"},
        {"test_id": "negative.process.predictive_core", "prohibited_claim": "A predictive or GNN model is required for deterministic process mining.", "expected_result": "remove optional predictor and retain projection/discovery/conformance/performance"},
        {"test_id": "negative.process.agent_authority", "prohibited_claim": "An agent-proposed mapping, abstraction, cause or intervention is accepted evidence.", "expected_result": "retain proposal taint and deterministic review obligations"},
    ])
    source["non_collapse_laws"].extend(sorted(laws))
    process_crosswalk = next(
        row for row in source["crosswalks"]
        if row["legacy_ref"] == "candidate.product.process_mining"
    )
    process_crosswalk["canonical_refs"] = [
        PRODUCT,
        "semantic.process_mining",
        *[local_library(ref) for ref in CONCRETE],
        "standard.ocel20",
    ]
    process_crosswalk["disposition"] = "split_workbench_exact_libraries_and_carrier"
    return source
