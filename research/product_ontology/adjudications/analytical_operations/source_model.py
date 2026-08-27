#!/usr/bin/env python3
"""Full product and library adjudication for five analytical-operation products.

This module deliberately imports the evidence-backed inventory challenge rather
than copying its claims.  The adjudication adds exact product boundaries, DDD
dossiers, semantic ownership, library contracts, compiler crosswalks and
fail-closed gaps.  No provider is qualified and no model or agent is ambient.
"""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from typing import Any

from dataset_curation_enrichment import enrich_dataset_curation
from image_analysis_enrichment import enrich_image_analysis


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "source.json"
ROOT = HERE.parents[1]
AUDIT_MODEL = ROOT / "inventory_challenges/analytical_operations_gap_audit/source_model.py"
AUDIT_SPEC = importlib.util.spec_from_file_location("analytical_operations_gap_audit_source", AUDIT_MODEL)
if AUDIT_SPEC is None or AUDIT_SPEC.loader is None:
    raise RuntimeError(f"cannot load inventory audit: {AUDIT_MODEL}")
audit_module = importlib.util.module_from_spec(AUDIT_SPEC)
AUDIT_SPEC.loader.exec_module(audit_module)
AUDIT = audit_module.source()
AXES = ["user", "job", "adoption", "semantics", "authority", "lifecycle", "operation", "economics", "interface", "market_evidence"]


def refs(*idents: str) -> list[str]:
    return [f"evidence.aoga.{ident}" for ident in idents]


def art(
    ident: str,
    kind: str,
    name: str,
    definition: str,
    evidence_refs: list[str],
    owner: str | None = None,
    adoption: bool = False,
    operated: bool = False,
    **extra: Any,
) -> dict[str, Any]:
    return {
        "artifact_id": ident,
        "kind": kind,
        "name": name,
        "status": "candidate",
        "semantic_owner_ref": owner,
        "adoption_unit": adoption,
        "operated": operated,
        "definition": definition,
        "evidence_refs": evidence_refs,
        **extra,
    }


def split(scores: dict[str, int], evidence_refs: list[str], label: str) -> dict[str, Any]:
    return {
        axis: {
            "score": scores[axis],
            "finding": f"{label}: bounded evidence for the {axis} boundary; this score neither ratifies the product nor qualifies a provider.",
            "evidence_refs": evidence_refs,
        }
        for axis in AXES
    }


def camel(value: str) -> str:
    return "".join(part.capitalize() for part in value.replace("-", "_").replace(".", "_").split("_"))


def ddd(
    vision: str,
    subdomain: str,
    inside: list[str],
    outside: list[str],
    value_objects: list[str],
    entities: list[str],
    aggregates: list[dict[str, Any]],
    services: list[str],
    application_services: list[str],
    repositories: list[str],
    factories: list[str],
    specifications: list[str],
    policies: list[str],
    sagas: list[str],
    read_models: list[str],
    context_map: list[dict[str, str]],
    time_model: list[str],
    concurrency: list[str],
    nonfunctional_laws: list[str],
) -> dict[str, Any]:
    return {
        "domain_vision_statement": vision,
        "subdomain_classification": subdomain,
        "bounded_context_boundary": {"inside": inside, "outside": outside},
        "ubiquitous_language_policy": "Every owned term has one meaning in this context; external homonyms cross a named anti-corruption layer.",
        "context_map": context_map,
        "anti_corruption_layers": [f"acl.{row['neighbor_ref'].split('.')[-1]}" for row in context_map],
        "published_language": ["versioned commands", "past-tense domain events", "typed refusals", "immutable evidence and effect receipts"],
        "value_objects": value_objects,
        "entities": entities,
        "aggregates": aggregates,
        "aggregate_roots": [row["root"] for row in aggregates],
        "domain_services": services,
        "application_services": application_services,
        "repositories": repositories,
        "factories": factories,
        "specifications": specifications,
        "policies_and_reactions": policies,
        "sagas_and_process_managers": sagas,
        "read_models_and_projections": read_models,
        "integration_event_policy": "Only explicitly published, minimized events cross the boundary; internal events retain product-local semantic ownership.",
        "concurrency_and_idempotency": concurrency,
        "time_model": time_model,
        "event_storming_swimlanes": ["author_or_owner", "operator", "reviewer", "runtime", "external_authority"],
        "nonfunctional_laws": nonfunctional_laws,
    }


PRODUCTS: dict[str, dict[str, Any]] = {
    "preparation": {
        "id": "product.self_service_data_preparation",
        "legacy": "candidate.product.self_service_data_preparation",
        "name": "Self-Service Data Preparation Workbench",
        "question": "How can a data practitioner inspect, repair and reshape one admitted data cut through a reviewable recipe without mutating its source?",
        "users": ["data_practitioner", "analyst", "data_steward"],
        "harmed_parties": ["source_owner", "downstream_consumer", "data_subject"],
        "job": "Profile, repair, reshape, replay, compare and publish one prepared data edition interactively.",
        "outcomes": ["reproducible_preparation_recipe", "source_preservation", "reviewable_data_diff", "portable_prepared_output"],
        "sources": refs("openrefine_start", "openrefine_history", "openrefine_facets", "openrefine_transform", "openrefine_export", "openrefine_architecture"),
        "scores": {"user": 2, "job": 2, "adoption": 2, "semantics": 2, "authority": 1, "lifecycle": 2, "operation": 1, "economics": 1, "interface": 2, "market_evidence": 2},
        "states": ["draft", "data_admitted", "profiling", "recipe_editing", "review_ready", "accepted", "publishing", "published", "superseded", "withdrawn"],
        "commands": ["open_preparation_project", "admit_data_cut", "create_profile", "apply_facet", "append_transform", "undo_transform", "redo_transform", "replay_recipe", "compare_output", "submit_for_review", "accept_recipe", "publish_prepared_output", "supersede_project", "withdraw_output"],
        "events": ["preparation_project_opened", "data_cut_admitted", "profile_created", "facet_applied", "transform_appended", "transform_undone", "transform_redone", "recipe_replayed", "output_compared", "review_requested", "recipe_accepted", "prepared_output_published", "project_superseded", "output_withdrawn"],
        "invariants": ["the admitted source occurrence is immutable", "view selection is not a data mutation", "every transform binds exact input and output editions", "history is ordered and replay cannot invent omitted operations", "publication is distinct from recipe acceptance"],
        "refusals": ["source_identity_unresolved", "carrier_or_schema_unadmitted", "transform_type_error", "partial_operation_unacknowledged", "history_branch_conflict", "replay_input_incompatible", "output_diff_unreviewed", "publication_authority_missing"],
        "negative_mission": "Does not own source truth, scheduled production transformation, business metrics, master identity or downstream factual acceptance.",
        "ddd": ddd(
            "Own the reversible journey from an admitted data cut to a reviewed prepared-output edition.",
            "core_for_interactive_preparation_supporting_to_downstream_data_products",
            ["preparation projects", "data-cut admission", "profiles and facets", "typed recipes", "ordered reversible history", "replay and diff", "prepared-output publication"],
            ["source mutation", "production pipeline scheduling", "business semantic definitions", "master-data authority", "downstream use acceptance"],
            ["PreparationProjectId", "DataCutRef", "ColumnRef", "ProfileEdition", "FacetPredicate", "TransformExpression", "RecipeEdition", "OperationIndex", "DataDiff", "PublicationRef"],
            ["PreparationProject", "Recipe", "HistoryBranch", "PreparedOutputEdition", "ReviewOccurrence"],
            [
                {"root": "PreparationProject", "members": ["admitted_data_cut", "active_recipe_ref", "project_state", "review_ref"], "consistency": "one command advances one project edition"},
                {"root": "Recipe", "members": ["ordered_operations", "input_contract", "output_contract", "history_branches"], "consistency": "operation order and type validity are atomic"},
                {"root": "PreparedOutputEdition", "members": ["output_identity", "recipe_ref", "data_diff", "publication_status"], "consistency": "published identity binds exact recipe and input cut"},
            ],
            ["ProfilingService", "TransformTypecheckingService", "RecipeReplayService", "DataDiffService"],
            ["OpenProjectUseCase", "EditRecipeUseCase", "ReviewRecipeUseCase", "PublishPreparedOutputUseCase"],
            ["PreparationProjectRepository", "RecipeRepository", "PreparedOutputRepository"],
            ["PreparationProjectFactory", "TypedRecipeFactory", "PreparedOutputFactory"],
            ["SourceAdmissionSpecification", "TransformCompatibilitySpecification", "ReplayCompatibilitySpecification", "PublicationReadinessSpecification"],
            ["when a transform is appended recompute the derived output profile", "when review refuses publication return the project to recipe_editing", "when a published output is withdrawn emit a recall integration event"],
            ["PreparedOutputPublicationProcess", "PublishedOutputRecallProcess"],
            ["ProjectHistoryView", "ColumnProfileView", "RecipeDiffView", "PreparedOutputLineageView"],
            [
                {"neighbor_ref": "neighbor.source_truth", "relationship": "customer_supplier_acl", "translation": "admit immutable source occurrence and schema evidence"},
                {"neighbor_ref": "neighbor.transform_build", "relationship": "published_language", "translation": "export accepted recipe as a candidate production transform declaration"},
                {"neighbor_ref": "neighbor.quality", "relationship": "open_host_service", "translation": "import profiles and quality assertions without transferring recipe authority"},
            ],
            ["event time belongs to source values", "recording time versions project/history", "publication validity and supersession are explicit"],
            ["optimistic project edition", "idempotency key per command", "branch-on-edit after undo", "publication compare-and-swap"],
            ["bounded profiling and transform execution", "cooperative cancellation", "no hidden source writes", "replay receipt binds input recipe provider and output digests"],
        ),
    },
    "annotation": {
        "id": "product.annotation_operations",
        "legacy": "candidate.product.annotation_operations",
        "name": "Annotation and Ground-Truth Operations",
        "question": "How can an annotation owner turn selected source occurrences into a versioned, reviewed and quality-evidenced annotation dataset?",
        "users": ["annotation_owner", "annotator", "reviewer", "dataset_steward"],
        "harmed_parties": ["annotation_subject", "annotator", "downstream_model_subject", "dataset_consumer"],
        "job": "Configure, assign, annotate, review, correct, adjudicate and release trustworthy annotation editions.",
        "outcomes": ["traceable_annotation_occurrences", "measured_review_quality", "versioned_ground_truth", "recallable_dataset_release"],
        "sources": refs("cvat_qa", "cvat_manual_review", "cvat_auto_qa", "cvat_analytics", "labelstudio_project", "labelstudio_label", "labelstudio_consensus", "w3c_annotation"),
        "scores": {axis: 2 for axis in AXES},
        "states": ["draft", "configured", "sampling", "assigned", "annotating", "reviewing", "correcting", "adjudicating", "accepted", "releasing", "released", "superseded", "recalled"],
        "commands": ["open_annotation_project", "bind_annotation_schema", "select_targets", "sample_tasks", "assign_task", "submit_annotation", "open_review_issue", "correct_annotation", "measure_agreement", "record_consensus", "adjudicate_conflict", "accept_ground_truth", "release_annotation_dataset", "supersede_edition", "recall_edition"],
        "events": ["annotation_project_opened", "annotation_schema_bound", "targets_selected", "tasks_sampled", "task_assigned", "annotation_submitted", "review_issue_opened", "annotation_corrected", "agreement_measured", "consensus_recorded", "conflict_adjudicated", "ground_truth_accepted", "annotation_dataset_released", "edition_superseded", "edition_recalled"],
        "invariants": ["target and selector identity are preserved", "a prediction is not an annotation occurrence", "an annotation is not accepted ground truth", "reviewer and adjudicator authority are scoped", "released ground truth binds schema task population and evidence cut"],
        "refusals": ["target_unresolvable", "schema_incompatible", "assignee_unqualified", "annotation_invalid", "review_conflict_unresolved", "agreement_metric_inapplicable", "adjudicator_authority_missing", "release_quality_gate_failed", "recall_propagation_unknown"],
        "negative_mission": "Does not own model training, prediction truth, source-content authority, downstream business decisions or general workforce management.",
        "ddd": ddd(
            "Own the accountable conversion of selected targets into reviewed annotation and ground-truth editions.",
            "core_for_annotation_operations_supporting_to_model_and_analytical_products",
            ["annotation projects", "schemas and selectors", "sampling and assignment", "annotation occurrences", "review/correction", "agreement/consensus", "adjudication", "ground-truth release and recall"],
            ["model training", "prediction serving", "source content mutation", "business truth", "downstream decision authority"],
            ["AnnotationProjectId", "TargetRef", "Selector", "SchemaEdition", "LabelValue", "AssignmentScope", "AnnotationBody", "AgreementMeasure", "ConsensusRule", "GroundTruthEdition"],
            ["AnnotationProject", "AnnotationTask", "Assignment", "AnnotationOccurrence", "ReviewIssue", "AdjudicationOccurrence", "GroundTruthRelease"],
            [
                {"root": "AnnotationProject", "members": ["schema_ref", "target_population", "quality_policy", "project_state"], "consistency": "schema changes create a new project edition"},
                {"root": "AnnotationTask", "members": ["target_refs", "assignment", "annotations", "task_state"], "consistency": "submission respects assignment and schema edition"},
                {"root": "ReviewIssue", "members": ["subject_annotation", "finding", "comments", "resolution"], "consistency": "resolution is append-only and attributable"},
                {"root": "GroundTruthRelease", "members": ["accepted_annotations", "quality_evidence", "release_state", "recall_refs"], "consistency": "release binds immutable population schema and evidence cut"},
            ],
            ["SelectorResolutionService", "AgreementService", "ConsensusService", "AnnotationAdjudicationService"],
            ["ConfigureProjectUseCase", "DispatchAnnotationWorkUseCase", "ReviewAndCorrectUseCase", "ReleaseGroundTruthUseCase"],
            ["AnnotationProjectRepository", "AnnotationTaskRepository", "ReviewIssueRepository", "GroundTruthReleaseRepository"],
            ["AnnotationProjectFactory", "AnnotationTaskFactory", "GroundTruthReleaseFactory"],
            ["AnnotatorEligibilitySpecification", "AnnotationValiditySpecification", "ReviewIndependenceSpecification", "GroundTruthReadinessSpecification"],
            ["when an issue opens move the task to reviewing", "when correction is submitted re-evaluate conflicts", "when release is recalled notify every known consumer"],
            ["AnnotationCampaignProcess", "ConsensusAdjudicationProcess", "GroundTruthRecallProcess"],
            ["AssignmentQueueView", "AnnotationHistoryView", "ReviewConflictView", "AgreementMatrixView", "GroundTruthReleaseView"],
            [
                {"neighbor_ref": "neighbor.source_truth", "relationship": "conformist_acl", "translation": "resolve immutable target occurrence and lawful display scope"},
                {"neighbor_ref": "neighbor.model_lifecycle", "relationship": "published_language", "translation": "publish accepted dataset edition without transferring ground-truth authority"},
                {"neighbor_ref": "neighbor.quality", "relationship": "customer_supplier", "translation": "import sampling and metric kernels under annotation-specific meaning"},
            ],
            ["target occurrence validity is source-scoped", "annotation recording time is immutable", "schema/release validity and recall time are distinct"],
            ["task lease and assignment version", "idempotent submissions", "review issue optimistic version", "one accepted release transition per edition"],
            ["segregation of annotation review and adjudication roles when required", "bounded worker exposure", "accessible annotation UI", "complete attribution and recall evidence"],
        ),
    },
    "document": {
        "id": "product.document_processing_review",
        "legacy": "candidate.product.document_processing_review",
        "name": "Document Processing and Review Operations",
        "question": "How can a document operator convert one admitted document occurrence into typed, provenance-linked structured output with exceptions and review?",
        "users": ["document_operator", "reviewer", "integration_owner", "records_steward"],
        "harmed_parties": ["document_subject", "source_owner", "downstream_case_subject", "reviewer"],
        "job": "Admit, detect, render, partition, extract, validate, review and release structured document outputs.",
        "outcomes": ["bounded_document_processing", "provenance_linked_extraction", "reviewed_exceptions", "reprocessable_structured_output"],
        "sources": refs("tika_home", "tika_detector", "unstructured_partition", "unstructured_chunk", "google_docai_overview", "google_docai_api", "google_document", "aws_textract_review"),
        "scores": {"user": 2, "job": 2, "adoption": 2, "semantics": 2, "authority": 1, "lifecycle": 2, "operation": 2, "economics": 2, "interface": 2, "market_evidence": 2},
        "states": ["received", "admission_pending", "admitted", "partitioning", "extracting", "validating", "exception", "human_review", "accepted", "rejected", "releasing", "released", "reprocessed", "recalled"],
        "commands": ["receive_document", "admit_document", "detect_carrier", "render_pages", "partition_content", "execute_extraction", "validate_extraction", "open_exception", "submit_human_review", "accept_structured_output", "reject_document", "release_structured_output", "reprocess_document", "recall_output"],
        "events": ["document_received", "document_admitted", "carrier_detected", "pages_rendered", "content_partitioned", "extraction_executed", "extraction_validated", "exception_opened", "human_review_submitted", "structured_output_accepted", "document_rejected", "structured_output_released", "document_reprocessed", "output_recalled"],
        "invariants": ["carrier detection may be unknown or disputed", "page region and revision provenance are preserved", "extraction candidates are not business facts", "method/provider edition is recorded", "release requires schema validation and resolved review policy"],
        "refusals": ["document_identity_missing", "carrier_unknown", "encrypted_or_malformed_input", "render_budget_exhausted", "parser_profile_unsupported", "extraction_schema_unbound", "validation_failed", "review_authority_missing", "semantic_loss_unaccepted", "release_policy_refused"],
        "negative_mission": "Does not own generic byte transport, record-retention authority, search indexing, downstream factual acceptance or business-case disposition.",
        "ddd": ddd(
            "Own one document-processing occurrence from carrier admission through reviewed structured-output release.",
            "core_for_document_processing_supporting_to_industry_case_products",
            ["document occurrence and revision", "carrier admission", "page/content graph", "extraction schema binding", "method execution", "validation and exceptions", "human review", "output release/reprocess/recall"],
            ["generic file ingestion", "records retention", "search index lifecycle", "business fact acceptance", "downstream case decision"],
            ["DocumentCaseId", "DocumentOccurrenceRef", "CarrierProfile", "PageRef", "RegionRef", "ContentElement", "ExtractionSchemaEdition", "FieldCandidate", "Confidence", "ValidationFinding", "OutputEdition"],
            ["DocumentCase", "DocumentRevision", "ProcessingAttempt", "ExtractionCandidateSet", "DocumentReviewCase", "StructuredOutputEdition"],
            [
                {"root": "DocumentCase", "members": ["source_occurrence", "active_revision", "processing_profile", "case_state"], "consistency": "one active processing attempt per declared concurrency policy"},
                {"root": "ProcessingAttempt", "members": ["carrier_evidence", "page_graph", "method_receipts", "candidate_set", "findings"], "consistency": "attempt evidence is immutable after completion"},
                {"root": "DocumentReviewCase", "members": ["exception_findings", "review_assignments", "corrections", "review_outcome"], "consistency": "accepted corrections retain prior candidates and reviewer attribution"},
                {"root": "StructuredOutputEdition", "members": ["schema_ref", "accepted_values", "provenance", "release_state"], "consistency": "every value traces to document region method and review"},
            ],
            ["CarrierDetectionService", "ParserDispatchService", "ContentGraphService", "ExtractionValidationService", "DocumentReviewService"],
            ["ReceiveAndAdmitDocumentUseCase", "ProcessDocumentUseCase", "ResolveDocumentExceptionUseCase", "ReleaseStructuredOutputUseCase"],
            ["DocumentCaseRepository", "ProcessingAttemptRepository", "DocumentReviewCaseRepository", "StructuredOutputRepository"],
            ["DocumentCaseFactory", "ProcessingAttemptFactory", "StructuredOutputFactory"],
            ["CarrierAdmissionSpecification", "ProcessingProfileCompatibilitySpecification", "ExtractionValiditySpecification", "ReviewRequiredSpecification", "ReleaseReadinessSpecification"],
            ["when validation fails open a typed exception", "when review changes a value preserve candidate provenance", "when a processor edition changes require bounded reprocessing analysis"],
            ["DocumentProcessingProcess", "HumanReviewProcess", "DocumentReprocessingAndRecallProcess"],
            ["DocumentQueueView", "PageContentGraphView", "ExtractionCandidateView", "ExceptionReviewView", "StructuredOutputProvenanceView"],
            [
                {"neighbor_ref": "neighbor.ingestion", "relationship": "customer_supplier_acl", "translation": "receive immutable carrier occurrence and transport receipt"},
                {"neighbor_ref": "neighbor.records_authority", "relationship": "conformist", "translation": "apply retention/hold constraints without owning them"},
                {"neighbor_ref": "neighbor.business_case", "relationship": "published_language", "translation": "publish structured candidates and evidence, never accepted business truth"},
            ],
            ["document creation/effective time remains source metadata", "processing and review recording time is append-only", "processor/profile validity and output release validity are editioned"],
            ["case edition fencing", "attempt idempotency key", "provider retry creates a new attempt", "review compare-and-swap", "release once per output edition"],
            ["bounded parsing/rendering against hostile documents", "privacy-minimized review", "accessible review UI", "complete method and semantic-loss receipts", "reprocessing blast-radius evidence"],
        ),
    },
    "inspection": {
        "id": "product.visual_inspection_operations",
        "legacy": "candidate.product.visual_inspection_operations",
        "name": "Visual Inspection Operations",
        "question": "How can an inspection owner configure, execute and review repeatable image-based inspections while preserving each item, recipe, result and disposition boundary?",
        "users": ["inspection_engineer", "quality_operator", "reviewer", "line_integration_owner"],
        "harmed_parties": ["product_user", "line_worker", "asset_owner", "safety_operator"],
        "job": "Author, qualify, execute and review image-based inspection recipes and publish bounded inspection results.",
        "outcomes": ["repeatable_inspection_recipe", "traceable_item_result", "reviewable_abstention_and_defect_evidence", "controlled_machine_integration"],
        "sources": refs("merlic_getting_started", "merlic_tools", "merlic_evaluation", "merlic_checking", "merlic_process", "merlic_results", "iso_visual", "genicam"),
        "scores": {axis: 2 for axis in AXES},
        "states": ["draft", "calibrating", "recipe_testing", "qualification_pending", "qualified", "released", "ready", "executing", "result_ready", "review_pending", "accepted", "rejected", "halted", "superseded"],
        "commands": ["open_inspection_plan", "bind_acquisition_profile", "record_calibration", "compose_tool_flow", "test_recipe", "qualify_recipe", "release_recipe", "start_inspection", "record_method_result", "evaluate_tolerance", "request_review", "accept_inspection_result", "reject_inspection_result", "propose_machine_effect", "halt_runtime", "supersede_recipe"],
        "events": ["inspection_plan_opened", "acquisition_profile_bound", "calibration_recorded", "tool_flow_composed", "recipe_tested", "recipe_qualified", "recipe_released", "inspection_started", "method_result_recorded", "tolerance_evaluated", "review_requested", "inspection_result_accepted", "inspection_result_rejected", "machine_effect_proposed", "runtime_halted", "recipe_superseded"],
        "invariants": ["item occurrence and acquired evidence are bound before evaluation", "calibration and recipe editions are explicit", "method result is not inspection disposition", "inspection result is not machine effect authorization", "uncertainty abstention and missing evidence are representable"],
        "refusals": ["item_identity_unresolved", "acquisition_profile_incompatible", "calibration_expired", "recipe_unqualified", "evidence_quality_insufficient", "method_provider_unqualified", "tolerance_profile_unbound", "review_required", "machine_authority_missing", "runtime_halted"],
        "negative_mission": "Does not own camera drivers, universal defect taxonomies, plant quality authority, PLC command authorization or the physical reject effect.",
        "ddd": ddd(
            "Own repeatable inspection recipes and per-item visual inspection evidence/results without acquiring machine-effect authority.",
            "core_for_visual_inspection_operations_with_vertical_solution_pack_extensions",
            ["inspection plans", "acquisition/calibration bindings", "tool flows and recipes", "inspection occurrences", "method/tolerance results", "review disposition", "effect proposals"],
            ["camera/device driver", "industry defect vocabulary", "plant acceptance policy", "PLC authorization", "physical reject action"],
            ["InspectionPlanId", "RecipeEdition", "AcquisitionProfile", "CalibrationRef", "RegionOfInterest", "ItemOccurrenceRef", "ImageEvidenceRef", "ToleranceProfile", "MethodResult", "InspectionResult", "EffectProposal"],
            ["InspectionPlan", "InspectionRecipe", "CalibrationOccurrence", "InspectionRun", "InspectionReview", "EffectProposalOccurrence"],
            [
                {"root": "InspectionPlan", "members": ["purpose", "vertical_profile_ref", "quality_policy_ref", "plan_state"], "consistency": "plan changes create a new qualification scope"},
                {"root": "InspectionRecipe", "members": ["acquisition_profile", "calibration_requirements", "tool_flow", "tolerance_profile", "release_state"], "consistency": "released recipe is immutable"},
                {"root": "InspectionRun", "members": ["item_ref", "recipe_ref", "evidence_refs", "method_results", "inspection_result"], "consistency": "result binds one item occurrence and recipe edition"},
                {"root": "InspectionReview", "members": ["run_ref", "findings", "reviewer", "disposition"], "consistency": "review never rewrites method evidence"},
            ],
            ["AcquisitionCompatibilityService", "CalibrationValidityService", "ToolFlowTypecheckingService", "ToleranceEvaluationService", "InspectionReviewService"],
            ["AuthorInspectionRecipeUseCase", "QualifyAndReleaseRecipeUseCase", "ExecuteInspectionUseCase", "ReviewInspectionUseCase", "ProposeMachineEffectUseCase"],
            ["InspectionPlanRepository", "InspectionRecipeRepository", "InspectionRunRepository", "InspectionReviewRepository"],
            ["InspectionPlanFactory", "InspectionRecipeFactory", "InspectionRunFactory"],
            ["AcquisitionFitnessSpecification", "CalibrationValiditySpecification", "RecipeQualificationSpecification", "EvidenceSufficiencySpecification", "ReviewRequirementSpecification"],
            ["when evidence is insufficient emit abstention not good/bad", "when review is required withhold effect proposal", "when calibration expires halt affected recipe executions"],
            ["RecipeQualificationProcess", "InspectionExecutionProcess", "InspectionReviewAndEffectProposalProcess"],
            ["RecipeGraphView", "RuntimeStateView", "InspectionResultView", "DefectEvidenceView", "CalibrationImpactView"],
            [
                {"neighbor_ref": "neighbor.device_runtime", "relationship": "customer_supplier_acl", "translation": "bind qualified acquisition/device offers"},
                {"neighbor_ref": "neighbor.vertical_quality", "relationship": "customer_supplier", "translation": "import defect taxonomy tolerances and acceptance authority"},
                {"neighbor_ref": "neighbor.machine_control", "relationship": "published_language", "translation": "emit typed effect proposal; receive separate authorization and physical receipt"},
            ],
            ["capture and item occurrence times are distinct", "calibration validity interval gates runs", "recording/review/disposition times are append-only"],
            ["recipe edition fencing", "one run identity per trigger/item", "deduplicate result delivery", "review optimistic version", "halt wins over start"],
            ["bounded latency and fail-safe abstention", "calibration traceability", "deterministic rule-path replay", "declared stochastic uncertainty", "machine effects fail closed"],
        ),
    },
    "condition": {
        "id": "product.signal_condition_diagnostics",
        "legacy": "candidate.product.signal_condition_diagnostics",
        "name": "Signal Condition Monitoring and Diagnostics",
        "question": "How can an asset or process owner operate an editioned monitoring programme that turns admitted signals into state, health, diagnosis and prognosis evidence?",
        "users": ["reliability_engineer", "condition_monitoring_specialist", "maintenance_planner", "operations_reviewer"],
        "harmed_parties": ["asset_operator", "maintenance_worker", "public_or_environment", "production_owner"],
        "job": "Design and operate a monitoring programme from signal admission through state, health, diagnosis, prognosis and reviewed advisory evidence.",
        "outcomes": ["traceable_condition_indicators", "challengeable_diagnosis", "calibrated_prognosis", "reviewed_advisory_without_ambient_effects"],
        "sources": refs("iso_17359", "iso_13374", "iso_13379", "iso_13381", "mimosa_osacbm", "mimosa_osaeai", "ni_condition", "scipy_signal"),
        "scores": {axis: 2 for axis in AXES},
        "states": ["programme_draft", "instrumenting", "baselining", "active", "state_detected", "assessment_pending", "diagnosing", "prognosing", "review_pending", "advisory_issued", "closed", "reopened", "superseded"],
        "commands": ["open_monitoring_programme", "bind_asset_channel", "admit_sampling_profile", "record_calibration", "establish_baseline", "process_signal_window", "detect_state", "assess_health", "open_diagnostic_case", "record_diagnosis", "open_prognostic_case", "record_prognosis", "request_expert_review", "issue_advisory", "close_case", "reopen_case", "supersede_programme"],
        "events": ["monitoring_programme_opened", "asset_channel_bound", "sampling_profile_admitted", "calibration_recorded", "baseline_established", "signal_window_processed", "state_detected", "health_assessed", "diagnostic_case_opened", "diagnosis_recorded", "prognostic_case_opened", "prognosis_recorded", "expert_review_requested", "advisory_issued", "case_closed", "case_reopened", "programme_superseded"],
        "invariants": ["asset channel unit sampling and calibration identities are explicit", "condition indicator is not detected state", "state is not diagnosis", "diagnosis is not prognosis or advisory", "advisory is not maintenance authorization", "defeaters and uncertainty remain visible"],
        "refusals": ["asset_identity_unresolved", "channel_semantics_ambiguous", "sampling_profile_inadequate", "calibration_invalid", "baseline_unfit", "window_quality_insufficient", "method_unqualified", "diagnostic_evidence_conflicted", "prognostic_horizon_unbound", "expert_review_required", "advisory_authority_missing"],
        "negative_mission": "Does not own generic telemetry storage, service incidents, asset master data, maintenance work orders or protective-control effects.",
        "ddd": ddd(
            "Own the monitoring programme and condition/health/diagnostic/prognostic evidence lifecycles for physical assets and processes.",
            "core_for_condition_monitoring_with_vertical_failure_and_maintenance_extensions",
            ["monitoring programme", "asset/channel/sampling/calibration bindings", "baselines and windows", "condition indicators and states", "health assessments", "diagnostic/prognostic cases", "reviewed advisory"],
            ["telemetry storage", "asset master authority", "maintenance planning/work orders", "protective control", "digital-service incident management"],
            ["MonitoringProgrammeId", "AssetRef", "ChannelRef", "UnitRef", "SamplingProfile", "CalibrationRef", "SignalWindow", "BaselineEdition", "ConditionIndicator", "DetectedState", "HealthAssessment", "Diagnosis", "Prognosis", "Advisory"],
            ["MonitoringProgramme", "AssetChannelBinding", "Baseline", "ConditionOccurrence", "DiagnosticCase", "PrognosticCase", "ExpertReview", "AdvisoryOccurrence"],
            [
                {"root": "MonitoringProgramme", "members": ["asset_scope", "channel_bindings", "method_plan", "programme_state"], "consistency": "scope/method changes create a new programme edition"},
                {"root": "ConditionOccurrence", "members": ["signal_window", "indicator_set", "detected_state", "health_assessment"], "consistency": "assessment binds exact signal and baseline editions"},
                {"root": "DiagnosticCase", "members": ["symptoms", "hypotheses", "evidence", "defeaters", "diagnosis", "review_state"], "consistency": "diagnosis preserves alternatives and contrary evidence"},
                {"root": "PrognosticCase", "members": ["condition_ref", "horizon", "assumptions", "prognosis", "uncertainty", "review_state"], "consistency": "prognosis identity includes horizon and assumptions"},
                {"root": "AdvisoryOccurrence", "members": ["case_refs", "recommendation", "limitations", "authority", "status"], "consistency": "advisory never mutates maintenance or control systems directly"},
            ],
            ["SignalPreparationService", "StateDetectionService", "HealthAssessmentService", "DiagnosticReasoningService", "PrognosticEvaluationService"],
            ["ConfigureMonitoringProgrammeUseCase", "ProcessConditionWindowUseCase", "InvestigateDiagnosisUseCase", "EvaluatePrognosisUseCase", "IssueReviewedAdvisoryUseCase"],
            ["MonitoringProgrammeRepository", "ConditionOccurrenceRepository", "DiagnosticCaseRepository", "PrognosticCaseRepository", "AdvisoryRepository"],
            ["MonitoringProgrammeFactory", "ConditionOccurrenceFactory", "DiagnosticCaseFactory", "PrognosticCaseFactory"],
            ["ChannelFitnessSpecification", "SamplingAdequacySpecification", "CalibrationValiditySpecification", "BaselineFitnessSpecification", "DiagnosisSufficiencySpecification", "PrognosisFitnessSpecification", "AdvisoryReadinessSpecification"],
            ["when a state is detected open assessment not diagnosis", "when material defeater appears reopen the case", "when programme edition changes invalidate affected baselines and advisories"],
            ["MonitoringProgrammeActivationProcess", "DiagnosticInvestigationProcess", "PrognosticReviewProcess", "AdvisoryToMaintenanceHandoffProcess"],
            ["ProgrammeCoverageView", "ChannelQualityView", "ConditionTimelineView", "DiagnosticArgumentView", "PrognosticHorizonView", "AdvisoryEvidenceView"],
            [
                {"neighbor_ref": "neighbor.telemetry", "relationship": "customer_supplier_acl", "translation": "admit signal occurrences with channel/unit/timing evidence"},
                {"neighbor_ref": "neighbor.asset_master", "relationship": "conformist", "translation": "resolve asset configuration without taking master authority"},
                {"neighbor_ref": "neighbor.maintenance", "relationship": "published_language", "translation": "publish advisory and evidence, not work authorization"},
                {"neighbor_ref": "neighbor.protective_control", "relationship": "anti_corruption_layer", "translation": "separate diagnostic evidence from safety-control command authority"},
            ],
            ["sample/event time", "arrival/recording time", "calibration/baseline validity", "diagnostic knowledge time", "prognostic horizon", "advisory expiry"],
            ["programme edition fencing", "window identity deduplication", "late-data policy", "case optimistic version", "append-only evidence", "reopen beats terminal presentation state"],
            ["bounded latency where declared", "unit/time correctness", "uncertainty and abstention", "defeater preservation", "fail-safe handoff", "no ambient maintenance or control effect"],
        ),
    },
}


def lib(
    product: str,
    suffix: str,
    name: str,
    operation: str,
    decision: str,
    invariant: str,
    refusal: str,
    concrete: list[str],
    evidence_refs: list[str],
    effectful: bool = False,
) -> tuple[Any, ...]:
    return (product, suffix, name, operation, decision, invariant, refusal, concrete, evidence_refs, effectful)


LIBRARY_SPECS = [
    # Preparation: 9.
    lib("preparation", "preparation_project", "Preparation project", "govern_preparation_project", "project_identity_owner_and_lifecycle", "a_project_has_one_admitted_input_scope_and_editioned_recipe_history", "preparation_project_invalid", [], refs("openrefine_start", "openrefine_history"), True),
    lib("preparation", "data_cut_admission", "Preparation data-cut admission", "admit_preparation_data_cut", "source_occurrence_schema_and_cut", "admission_copies_or_references_without_mutating_source_authority", "data_cut_unadmitted", ["library.pipeline.data_cut_algebra"], refs("openrefine_start", "openrefine_export")),
    lib("preparation", "column_profile", "Interactive column profile", "profile_columns", "population_missingness_types_and_budget", "a_profile_binds_the_exact_data_cut_and_selection", "profile_incomplete", ["library.qor.data_profiling_kernel"], refs("openrefine_facets", "openrefine_transform")),
    lib("preparation", "facet_and_filter", "Facet and filter state", "evaluate_facet", "predicate_selection_view_and_materialization_scope", "a_facet_is_a_view_selection_until_an_explicit_transform_uses_it", "facet_predicate_invalid", [], refs("openrefine_facets")),
    lib("preparation", "typed_transform_recipe", "Typed preparation recipe", "typecheck_preparation_recipe", "operation_order_types_partiality_and_loss", "each_operation_has_explicit_input_output_and_failure_semantics", "recipe_type_error", ["library.pipeline.graph_algebra", "library.pipeline.graph_validator", "library.pipeline.port_typechecker"], refs("openrefine_transform", "openrefine_history")),
    lib("preparation", "reversible_history", "Reversible preparation history", "apply_or_revert_operation", "history_index_branch_and_reversibility", "undo_and_redo_follow_the_exact_ordered_history_and_preserve_abandoned_branches_as_evidence", "history_transition_invalid", [], refs("openrefine_history", "openrefine_architecture"), True),
    lib("preparation", "recipe_replay", "Preparation recipe replay", "replay_preparation_recipe", "input_compatibility_provider_profile_and_partial_results", "replay_never_silently_skips_or_reinterprets_an_operation", "recipe_replay_incompatible", [], refs("openrefine_history", "openrefine_export")),
    lib("preparation", "data_diff", "Prepared data diff", "compare_prepared_data", "row_column_value_identity_order_and_tolerance", "a_diff_reports_unmatched_and_uncomparable_values_explicitly", "data_diff_unresolved", ["library.pipeline.differential_algebra"], refs("openrefine_export", "openrefine_architecture")),
    lib("preparation", "prepared_output_publication", "Prepared output publication", "publish_prepared_output", "output_identity_recipe_lineage_policy_and_destination", "publication_binds_exact_input_recipe_diff_and_export_profile", "prepared_output_publication_refused", ["library.pipeline.materialization_publisher", "library.lpe.prov-statement-algebra","library.lpe.provenance-assertion", "library.cbv.export_plan", "library.cbv.export_encoder", "library.cbv.export_delivery_port"], refs("openrefine_export", "openrefine_start"), True),

    # Annotation: 12.
    lib("annotation", "annotation_schema", "Annotation schema", "validate_annotation_schema", "label_types_attributes_relations_cardinality_and_version", "schema_identity_is_distinct_from_ui_labels_and_model_targets", "annotation_schema_invalid", ["library.predictive.label_contracts", "library.gmo.taxonomy_core"], refs("labelstudio_project", "labelstudio_label", "w3c_annotation")),
    lib("annotation", "target_selector", "Annotation target selector", "resolve_annotation_target", "target_occurrence_fragment_selector_and_revision", "an_annotation_never_floats_free_of_a_resolvable_versioned_target", "annotation_target_unresolved", [], refs("w3c_annotation", "labelstudio_label")),
    lib("annotation", "task_sampling", "Annotation task sampling", "sample_annotation_tasks", "population_frame_method_seed_weights_and_overlap", "sample_membership_and_randomness_are_reproducible_or_explicitly_nondeterministic", "task_sample_invalid", ["library.predictive.sampling_weights", "library.qor.sampling_measurement_kernel"], refs("cvat_auto_qa", "labelstudio_project")),
    lib("annotation", "work_assignment", "Annotation work assignment", "assign_annotation_task", "role_competence_scope_lease_and_blinding", "only_one_valid_assignment_lease_may_authorize_a_submission_unless_overlap_is_declared", "annotation_assignment_refused", [], refs("cvat_manual_review", "cvat_analytics"), True),
    lib("annotation", "annotation_occurrence", "Annotation occurrence", "record_annotation", "body_target_creator_schema_time_and_provenance", "prediction_suggestion_and_human_annotation_remain_distinct_occurrences", "annotation_occurrence_invalid", ["library.cbv.annotation_store", "library.lpe.prov-statement-algebra","library.lpe.provenance-assertion"], refs("w3c_annotation", "labelstudio_label"), True),
    lib("annotation", "review_issue", "Annotation review issue", "open_or_resolve_annotation_issue", "finding_location_severity_comments_and_resolution", "issue_resolution_is_attributable_and_never_erases_the_original_annotation", "annotation_review_issue_invalid", [], refs("cvat_manual_review"), True),
    lib("annotation", "correction", "Annotation correction", "correct_annotation", "corrector_scope_prior_occurrence_and_change_reason", "correction_creates_a_new_occurrence_linked_to_the_superseded_one", "annotation_correction_refused", ["library.qor.correction_proposal_kernel", "library.qor.correction_execution_kernel"], refs("cvat_manual_review"), True),
    lib("annotation", "agreement_metric", "Annotation agreement metric", "measure_annotation_agreement", "metric_type_applicability_population_and_missingness", "agreement_is_metric_and_population_specific_not_universal_truth", "agreement_metric_inapplicable", [], refs("labelstudio_consensus", "cvat_auto_qa")),
    lib("annotation", "consensus", "Annotation consensus", "derive_annotation_consensus", "eligible_votes_weights_quorum_ties_and_abstention", "consensus_never_silently_converts_disagreement_into_ground_truth", "annotation_consensus_unresolved", [], refs("labelstudio_consensus", "cvat_qa")),
    lib("annotation", "adjudication", "Annotation adjudication", "adjudicate_annotation_conflict", "adjudicator_authority_evidence_precedence_and_reason", "adjudication_is_a_scoped_judgment_occurrence_not_a_metric", "annotation_adjudication_refused", ["library.qor.defect_adjudication_kernel", "library.csp.decision.judgment-port", "library.csp.decision.decision-ledger"], refs("cvat_manual_review", "labelstudio_consensus"), True),
    lib("annotation", "ground_truth_edition", "Ground-truth edition", "accept_ground_truth_edition", "schema_population_evidence_cut_quality_and_recall", "ground_truth_is_versioned_scoped_challengeable_and_recallable", "ground_truth_acceptance_refused", ["library.predictive.target_contracts", "library.csp.identity.version-identity"], refs("cvat_auto_qa", "labelstudio_consensus"), True),
    lib("annotation", "annotation_export", "Annotation dataset export", "export_annotation_dataset", "carrier_schema_provenance_policy_and_loss", "export_preserves_target_annotation_schema_and_release_identity_or_reports_loss", "annotation_export_refused", ["library.cbv.export_plan", "library.cbv.export_encoder", "library.cbv.export_delivery_port", "library.lpe.prov-interchange"], refs("cvat_auto_qa", "labelstudio_project"), True),

    # Document: 14.
    lib("document", "document_admission", "Document admission", "admit_document", "carrier_identity_integrity_policy_and_resource_profile", "untrusted_documents_are_bounded_and_never_parsed_before_admission", "document_admission_refused", ["library.method_kernels.document_container_semantics", "library.san_format_probe", "library.san_integrity"], refs("tika_home", "tika_detector", "unstructured_partition")),
    lib("document", "carrier_detection", "Document carrier detection", "detect_document_carrier", "detector_order_evidence_confidence_and_unknown", "extension_mime_and_detector_results_are_evidence_not_unquestionable_truth", "document_carrier_unknown", ["library.san_format_probe", "library.method_kernels.document_container_semantics"], refs("tika_detector", "unstructured_partition")),
    lib("document", "bounded_rendering", "Bounded document rendering", "render_document_pages", "renderer_profile_fonts_external_resources_and_budgets", "rendering_never_fetches_or_executes_ambient_resources", "document_render_refused", [], refs("unstructured_partition", "google_docai_overview"), True),
    lib("document", "page_revision_identity", "Document page and revision identity", "identify_pages_and_revisions", "document_revision_page_order_shard_and_parentage", "page_and_region_references_are_stable_only_within_an_explicit_revision_profile", "page_revision_identity_unresolved", ["library.csp.identity.version-identity", "library.method_kernels.document_content_graph"], refs("google_document", "unstructured_partition")),
    lib("document", "content_graph", "Document content graph", "construct_document_content_graph", "elements_regions_reading_order_relations_and_provenance", "content_elements_retain_page_region_and_method_provenance", "document_content_graph_invalid", ["library.method_kernels.document_content_graph"], refs("unstructured_partition", "google_document")),
    lib("document", "partitioning", "Document partitioning", "partition_document", "format_strategy_element_types_order_and_fallback", "fallback_strategy_and_result_loss_are_recorded_not_hidden", "document_partition_failed", ["library.method_kernels.document_parser_adapters", "library.method_kernels.document_content_graph"], refs("unstructured_partition", "tika_home")),
    lib("document", "ocr_method", "Document OCR method", "execute_document_ocr", "language_script_region_image_quality_and_method_profile", "ocr_output_is_a_candidate_text_layer_with_uncertainty_and_provenance", "document_ocr_unavailable", ["library.method_kernels.document_ocr_methods"], refs("unstructured_partition", "google_docai_overview")),
    lib("document", "layout_method", "Document layout method", "infer_document_layout", "layout_vocabulary_reading_order_regions_and_method_profile", "layout_inference_never_overwrites_physical_page_evidence", "document_layout_unresolved", ["library.method_kernels.document_layout_methods"], refs("unstructured_partition", "google_docai_overview")),
    lib("document", "table_and_form_extraction", "Document table and form extraction", "extract_tables_and_forms", "cell_key_value_geometry_spans_and_missingness", "table_or_form_structure_preserves_region_provenance_and_ambiguity", "table_form_extraction_failed", ["library.method_kernels.document_table_extraction", "library.method_kernels.document_form_extraction"], refs("unstructured_partition", "google_docai_overview")),
    lib("document", "schema_extraction", "Schema-bound document extraction", "extract_document_fields", "schema_field_cardinality_normalization_and_candidate_policy", "extracted_values_remain_candidates_until_validation_and_acceptance", "document_extraction_schema_unbound", ["library.method_kernels.document_information_extraction", "library.method_kernels.document_classification_methods"], refs("google_docai_overview", "google_docai_api")),
    lib("document", "validation", "Document extraction validation", "validate_document_extraction", "schema_rules_cross_field_constraints_confidence_and_evidence", "validation_result_does_not_create_downstream_business_truth", "document_extraction_validation_failed", ["library.method_kernels.document_extraction_evaluation", "library.qor.validation_execution_kernel"], refs("google_docai_api", "google_document")),
    lib("document", "exception_case", "Document exception case", "govern_document_exception", "finding_severity_assignment_deadline_and_resolution", "unresolved_material_exception_blocks_structured_output_release", "document_exception_unresolved", ["library.cbv.analytical_case_reducer", "library.cbv.decision_handoff_algebra"], refs("google_document", "aws_textract_review"), True),
    lib("document", "human_review", "Document human review", "review_document_candidates", "reviewer_scope_evidence_changes_and_outcome", "human_review_is_a_scoped_judgment_not_automatic_truth", "document_review_refused", ["library.csp.decision.judgment-port", "library.csp.decision.decision-ledger"], refs("google_document", "aws_textract_review"), True),
    lib("document", "structured_output_release", "Structured document output release", "release_document_output", "output_schema_values_provenance_policy_loss_and_destination", "every_released_value_traces_to_document_region_method_validation_and_review", "document_output_release_refused", ["library.cbv.export_plan", "library.cbv.export_encoder", "library.cbv.export_delivery_port", "library.pipeline.materialization_publisher", "library.method_kernels.document_provenance_loss", "library.lpe.prov-statement-algebra","library.lpe.provenance-assertion"], refs("google_document", "unstructured_partition"), True),

    # Visual inspection: 12.
    lib("inspection", "inspection_plan", "Visual inspection plan", "compile_inspection_plan", "purpose_population_defect_profile_costs_and_authority", "plan_scope_and_vertical_profile_are_explicit", "inspection_plan_incomplete", ["library.method_kernels.analysis_design"], refs("merlic_getting_started", "iso_visual")),
    lib("inspection", "acquisition_profile", "Inspection acquisition profile", "bind_inspection_acquisition", "camera_lens_lighting_trigger_geometry_format_and_timing", "camera_interoperability_does_not_prove_evidence_fitness", "inspection_acquisition_unqualified", [], refs("merlic_getting_started", "genicam"), True),
    lib("inspection", "calibration", "Inspection calibration", "validate_inspection_calibration", "method_artifact_environment_validity_and_uncertainty", "calibration_is_editioned_scoped_and_expirable", "inspection_calibration_invalid", [], refs("iso_visual", "merlic_tools")),
    lib("inspection", "region_of_interest", "Inspection region of interest", "resolve_inspection_region", "coordinate_frame_geometry_mask_and_alignment", "roi_identity_requires_image_and_coordinate_frame", "inspection_roi_unresolved", ["library.method_kernels.image_methods", "library.method_kernels.coordinate_transform_methods"], refs("merlic_tools", "merlic_checking")),
    lib("inspection", "tool_flow", "Inspection tool flow", "typecheck_inspection_tool_flow", "ports_order_parallelism_branches_and_failures", "tool_flow_connections_are_typed_and_error_paths_are_total", "inspection_tool_flow_invalid", ["library.pipeline.graph_algebra", "library.pipeline.graph_validator", "library.pipeline.port_typechecker"], refs("merlic_getting_started", "merlic_tools")),
    lib("inspection", "recipe", "Inspection recipe", "govern_inspection_recipe", "tool_flow_parameters_calibration_requirements_and_release", "released_recipe_is_immutable_and_bound_to_qualification_evidence", "inspection_recipe_unqualified", [], refs("merlic_getting_started", "merlic_process"), True),
    lib("inspection", "inspection_execution", "Inspection execution", "execute_visual_inspection", "item_trigger_recipe_runtime_budget_and_attempt", "each_run_binds_one_item_occurrence_recipe_and_evidence_set", "inspection_execution_failed", ["library.runtime-resource.async-executor", "library.runtime-resource.runtime-receipts"], refs("merlic_process", "merlic_results"), True),
    lib("inspection", "method_result", "Visual method result", "record_visual_method_result", "method_profile_output_uncertainty_and_evidence", "method_result_is_not_inspection_disposition", "visual_method_result_invalid", ["library.method_kernels.result_algebra", "library.method_kernels.image_methods"], refs("merlic_evaluation", "merlic_checking")),
    lib("inspection", "tolerance_evaluation", "Inspection tolerance evaluation", "evaluate_inspection_tolerance", "feature_units_limits_inclusivity_uncertainty_and_abstention", "missing_or_uncertain_evidence_cannot_silently_pass", "inspection_tolerance_unresolved", ["library.csp.intent.acceptance-predicate", "library.csp.quantity.quantity-conformance"], refs("merlic_evaluation", "iso_visual")),
    lib("inspection", "inspection_result", "Visual inspection result", "issue_inspection_result", "item_recipe_method_results_evaluation_and_limit", "inspection_result_preserves_abstention_limitations_and_evidence", "inspection_result_withheld", ["library.method_kernels.analytical_finding_contract", "library.lpe.evidence-bundle"], refs("merlic_results", "iso_visual"), True),
    lib("inspection", "review_disposition", "Inspection review disposition", "review_inspection_result", "reviewer_scope_findings_reason_and_disposition", "review_does_not_rewrite_method_or_image_evidence", "inspection_review_refused", ["library.csp.decision.judgment-port", "library.csp.decision.decision-ledger"], refs("merlic_results", "iso_visual"), True),
    lib("inspection", "machine_integration_port", "Inspection machine-integration port", "propose_inspection_effect", "effect_type_target_preconditions_authority_and_receipt", "inspection_product_emits_a_proposal_not_an_authorized_physical_effect", "inspection_effect_not_authorized", ["library.csp.decision.action-proposal", "library.csp.decision.effect-port"], refs("merlic_process", "merlic_results"), True),

    # Condition monitoring/diagnostics: 13.
    lib("condition", "monitoring_program", "Condition monitoring programme", "govern_monitoring_programme", "asset_scope_criticality_channels_methods_reviews_and_exit", "programme_scope_and_method_plan_are_editioned", "monitoring_programme_incomplete", ["library.method_kernels.analysis_design"], refs("iso_17359", "iso_13379"), True),
    lib("condition", "asset_channel_binding", "Asset and signal-channel binding", "bind_asset_signal_channel", "asset_configuration_sensor_channel_unit_location_and_validity", "channel_values_have_no_condition_meaning_without_asset_unit_and_context_binding", "asset_channel_binding_unresolved", [], refs("mimosa_osaeai", "ni_condition")),
    lib("condition", "sampling_profile", "Condition sampling profile", "validate_condition_sampling", "rate_clock_window_trigger_aliasing_and_missingness", "sampling_profile_is_part_of_method_fitness_not_transport_metadata_only", "condition_sampling_inadequate", ["library.qor.sampling_measurement_kernel", "library.pipeline.window_trigger"], refs("ni_condition", "scipy_signal")),
    lib("condition", "calibration", "Condition sensor calibration", "validate_condition_calibration", "artifact_method_traceability_environment_uncertainty_and_expiry", "invalid_or_expired_calibration_blocks_scoped_assessment", "condition_calibration_invalid", [], refs("iso_17359", "ni_condition")),
    lib("condition", "signal_windowing", "Condition signal windowing", "construct_condition_window", "event_time_duration_overlap_lateness_alignment_and_gap_policy", "window_identity_and_late_data_policy_are_explicit", "condition_window_invalid", ["library.pipeline.window_trigger", "library.method_kernels.signal_methods"], refs("iso_13374", "scipy_signal")),
    lib("condition", "filter_and_spectral_kernels", "Condition filter and spectral kernels", "execute_signal_method", "filter_spectral_estimator_parameters_units_edges_and_numerics", "kernel_output_binds_exact_sampling_window_and_method_profile", "signal_method_unsupported", ["library.method_kernels.signal_methods", "library.method_kernels.numerical_kernel_facade"], refs("scipy_signal", "ni_condition")),
    lib("condition", "state_detection", "Condition state detection", "detect_condition_state", "baseline_feature_threshold_change_and_abstention", "condition_indicator_is_not_state_and_state_is_not_diagnosis", "condition_state_unresolved", ["library.method_kernels.anomaly_baseline", "library.method_kernels.anomaly_detectors", "library.method_kernels.change_point_detectors"], refs("mimosa_osacbm", "iso_13379")),
    lib("condition", "health_assessment", "Asset health assessment", "assess_asset_health", "state_configuration_criticality_evidence_uncertainty_and_scale", "health_assessment_is_scoped_timed_and_challengeable", "health_assessment_insufficient", ["library.method_kernels.analytical_finding_contract", "library.cbv.uncertainty_contracts"], refs("mimosa_osacbm", "iso_13379")),
    lib("condition", "diagnostic_case", "Condition diagnostic case", "adjudicate_diagnostic_case", "symptoms_hypotheses_evidence_defeaters_method_and_review", "diagnosis_preserves_alternatives_contrary_evidence_and_scope", "diagnosis_unresolved", ["library.cbv.analytical_case_reducer", "library.cbv.decision_handoff_algebra", "library.method_kernels.analytical_finding_contract"], refs("iso_13379", "mimosa_osacbm"), True),
    lib("condition", "prognostic_case", "Condition prognostic case", "evaluate_prognostic_case", "horizon_assumptions_covariates_method_uncertainty_and_validity", "prognosis_identity_includes_horizon_assumptions_and_information_cut", "prognosis_unfit", ["library.method_kernels.forecast_estimators", "library.method_kernels.survival_event_history_estimators", "library.predictive.survival_models"], refs("iso_13381", "mimosa_osacbm"), True),
    lib("condition", "advisory", "Condition advisory", "issue_condition_advisory", "recommendation_evidence_limitations_expiry_and_authority", "advisory_is_not_work_order_or_protective_control_authorization", "condition_advisory_refused", ["library.csp.decision.action-proposal", "library.method_kernels.analytical_finding_contract"], refs("mimosa_osacbm", "ni_condition"), True),
    lib("condition", "expert_review", "Condition expert review", "review_condition_case", "competence_scope_findings_defeaters_and_outcome", "expert_review_is_attributable_scoped_and_never_erases_method_evidence", "condition_expert_review_refused", ["library.csp.decision.judgment-port", "library.csp.decision.decision-ledger"], refs("iso_13379", "iso_13381"), True),
    lib("condition", "condition_evidence", "Condition evidence bundle", "publish_condition_evidence", "programme_asset_channels_windows_methods_cases_and_advisory", "evidence_bundle_preserves_exact_provenance_uncertainty_defeaters_and_limitations", "condition_evidence_incomplete", ["library.lpe.evidence-bundle", "library.lpe.prov-statement-algebra","library.lpe.provenance-assertion", "library.lpe.provenance-bundle", "library.lpe.runtime-receipt-core"], refs("iso_13374", "mimosa_osaeai"), True),
]


SEMANTIC_GAPS = [
    ("preparation_recipe_interchange", "No portable contract yet preserves interactive preparation operations, view selections, partiality, loss and history across independent workbenches."),
    ("preparation_history_branch", "Reversible history, branching after undo and replay compatibility need an exact algebra and executable model oracle."),
    ("preparation_large_data", "Interactive authoring and distributed execution need one typed plan split without changing recipe meaning."),
    ("annotation_selector_portability", "Multimodal target selectors and revision anchoring are not uniformly portable across annotation systems."),
    ("annotation_consensus", "Agreement, consensus, adjudication and accepted ground truth need separate portable contracts and precedence laws."),
    ("annotation_recall", "Ground-truth recall propagation to derived datasets, models and evaluations lacks complete machine-readable evidence."),
    ("annotation_workforce_safety", "Exposure limits, competence, blinding, accessibility and harmed-party protections need a portable operational profile."),
    ("document_content_graph", "Document page/region/content graphs lack one interchange preserving reading order, uncertainty, revisions and method provenance."),
    ("document_hostile_input", "Carrier-specific resource, sandbox, external-resource and decompression limits remain provider-dependent."),
    ("document_reprocessing", "Processor-edition changes need semantic diff, blast-radius, replay and downstream recall contracts."),
    ("document_fact_boundary", "Downstream applications need a portable distinction between extracted candidate, reviewed output and accepted business fact."),
    ("inspection_acquisition", "Camera, lens, illumination, trigger, geometry and evidence-quality profiles lack one qualified acquisition contract."),
    ("inspection_calibration", "Calibration validity, traceability, environmental envelope and uncertainty lack a complete compiler-owned library seam."),
    ("inspection_recipe_portability", "Inspection recipes do not port across providers while preserving tool semantics, calibration, error paths and timing."),
    ("inspection_abstention", "Good, bad, unknown, not-inspected and review-required outcomes need portable total-state conformance."),
    ("inspection_effect_handoff", "Inspection result, quality disposition, effect authorization and physical machine receipt need end-to-end exact boundary tests."),
    ("condition_asset_channel", "Asset/channel/configuration/unit/location bindings lack one portable cross-vendor semantic contract."),
    ("condition_calibration", "Signal calibration, uncertainty and expiry are not yet exact compiler libraries for the condition domain."),
    ("condition_state_health", "Indicator, detected state, health assessment, diagnosis and prognosis vocabularies remain inconsistently collapsed across providers."),
    ("condition_defeaters", "Diagnostic alternatives, contrary evidence, causal assumptions and defeaters lack portable case semantics."),
    ("condition_prognostic_validation", "Prognostic horizon, censoring, operating regime, calibration and uncertainty acceptance need exact validation profiles."),
    ("condition_authority_handoff", "Advisory-to-maintenance and advisory-to-protective-control handoffs need typed authority, compensation and receipt contracts."),
    ("two_implementations", "Every new library contract still lacks two independent qualified implementations and shared law-oracle receipts."),
    ("product_exit", "Each product needs exercised full-fidelity export, in-flight-work disposition and provider-exit drills."),
    ("vertical_profiles", "Industry solution packs must prove that defect, document, annotation and failure vocabularies extend the horizontal core without name branches."),
]


NEGATIVES = [
    ("ai_prefix", "Create parallel AI-prefixed versions of all five products.", "refuse_modality_is_orthogonal"),
    ("agent_research", "Accept agent-generated vocabulary, invariants or mappings without ordinary evidence and deterministic validation.", "refuse_unaccepted_proposal"),
    ("deterministic_closed_form", "Deterministic architecture bans probabilistic, predictive, heuristic or approximate methods.", "retain_typed_qualified_stochastic_methods"),
    ("prep_source_mutation", "Interactive preparation may silently mutate the source system.", "refuse_source_authority_violation"),
    ("prep_view_transform", "A facet selection is automatically a permanent transform.", "separate_view_from_mutation"),
    ("prep_undo_delete", "Undo may erase the abandoned history branch from evidence.", "preserve_branch_or_explicitly_dispose"),
    ("prep_replay_skip", "Replay may skip an unsupported operation and still publish.", "refuse_incomplete_replay"),
    ("prep_notebook", "A generic notebook necessarily owns preparation recipe semantics.", "retain_independent_preparation_boundary"),
    ("annotation_prediction", "A model or LLM prediction is an annotation occurrence.", "separate_prediction_and_annotation"),
    ("annotation_truth", "A submitted annotation is ground truth.", "require_review_consensus_or_adjudication_policy"),
    ("annotation_agreement", "One agreement score proves all labels are correct.", "bind_metric_population_and_failure_modes"),
    ("annotation_consensus", "Majority consensus automatically defeats qualified dissent.", "apply_explicit_adjudication_precedence"),
    ("annotation_human", "Any human click has annotation or adjudication authority.", "qualify_role_scope_competence_and_assignment"),
    ("document_suffix", "File extension proves document type.", "treat_suffix_as_bounded_evidence"),
    ("document_parse", "Successful parsing proves complete and correct content.", "validate_content_graph_loss_and_coverage"),
    ("document_extraction", "Extracted value is accepted business fact.", "separate_candidate_reviewed_output_and_fact"),
    ("document_review", "Human review removes the need for provenance and validation.", "retain_evidence_and_scoped_judgment"),
    ("document_reprocess", "Reprocessing may overwrite the prior output edition.", "append_new_attempt_and_supersession"),
    ("inspection_camera", "A GenICam-compatible camera proves inspection fitness.", "qualify_acquisition_and_evidence_profile"),
    ("inspection_model", "A defect model is the visual inspection product.", "retain_model_as_replaceable_method"),
    ("inspection_good", "Good method result authorizes physical acceptance.", "separate_method_result_disposition_and_effect"),
    ("inspection_unknown", "Missing evidence defaults to good.", "abstain_or_refuse"),
    ("inspection_plc", "Inspection runtime may directly command PLC effects.", "require_external_effect_authority_and_receipt"),
    ("condition_signal", "Any telemetry series is a condition-monitoring signal.", "require_asset_channel_unit_sampling_and_programme_binding"),
    ("condition_indicator", "A threshold crossing is a diagnosis.", "separate_indicator_state_health_and_diagnosis"),
    ("condition_prediction", "A predicted failure time is a maintenance order.", "separate_prognosis_advisory_and_authorization"),
    ("condition_root_cause", "Highest-scoring hypothesis is proven root cause.", "preserve_alternatives_defeaters_and_review"),
    ("condition_service_ops", "Digital service observability and physical condition diagnostics are one semantic owner.", "retain_separate_asset_and_service_health_contexts"),
    ("vertical_core", "Put every industry label threshold and failure mode in horizontal libraries.", "bind_vertical_solution_pack_extensions"),
    ("provider_docs", "Official documentation qualifies a provider.", "require_executable_conformance_and_occurrence_evidence"),
    ("one_provider", "One working provider proves portability.", "require_two_independent_qualified_implementations"),
    ("model_authority", "A predictive or generative method acquires review or effect authority from accuracy.", "refuse_authority_escalation"),
    ("agent_effect", "A tool agent may publish ground truth, document facts, inspection effects or maintenance orders from prose.", "require_typed_authorized_command_and_effect_gate"),
    ("hidden_partial", "Partial result may be reported as complete.", "make_partiality_total_and_explicit"),
    ("suite_merge", "One vendor suite implies one bounded context for all five products.", "retain_independent_semantic_lifecycle_and_exit_boundaries"),
]


# Exact shared measurement seams adjudicated after the initial analytical-operations pass.
# Product authority remains local; only reusable binding, acquisition and calibration semantics
# cross the boundary.
EXACT_COMPILER_OVERRIDES = {
    ("annotation", "target_selector"): [
        "library.addressable_content.selector.compiler",
        "library.addressable_content.selector.resolver",
    ],
    ("annotation", "work_assignment"): [
        "library.human_work.task_definition.compiler",
        "library.human_work.assignment.reducer",
    ],
    ("annotation", "review_issue"): [
        "library.review.issue.lifecycle",
    ],
    ("annotation", "agreement_metric"): [
        "library.agreement.measurement.evaluator",
    ],
    ("annotation", "consensus"): [
        "library.consensus.rule.compiler",
        "library.consensus.evaluator",
    ],
    ("annotation", "adjudication"): [
        "library.review.adjudication.reducer",
    ],
    ("document", "bounded_rendering"): [
        "library.document.rendition.profile.compiler",
        "library.document.rendition.evaluator",
    ],
    ("preparation", "preparation_project"): [
        "library.analytical_workspace.definition.compiler",
        "library.analytical_workspace.lifecycle.reducer",
    ],
    ("preparation", "facet_and_filter"): [
        "library.selection.predicate.compiler",
        "library.selection.state.reducer",
        "library.selection.facet.evaluator",
    ],
    ("condition", "asset_channel_binding"): [
        "library.measurement.observation_binding.compiler",
    ],
    ("condition", "calibration"): [
        "library.measurement.calibration_record.compiler",
        "library.measurement.calibration.evaluator",
    ],
    ("inspection", "acquisition_profile"): [
        "library.measurement.observation_binding.compiler",
        "library.measurement.acquisition_profile.compiler",
    ],
    ("inspection", "calibration"): [
        "library.measurement.calibration_record.compiler",
        "library.measurement.calibration.evaluator",
    ],
    ("inspection", "recipe"): [
        "library.recipe.definition.compiler",
        "library.recipe.lifecycle.registry",
        "library.recipe.target_preparation.protocol",
    ],
    ("preparation", "recipe_replay"): [
        "library.recipe.definition.compiler",
        "library.recipe.replay.planner",
        "library.recipe.replay.evaluator",
    ],
    ("preparation", "reversible_history"): [
        "library.recipe.edit_history.algebra",
    ],
}


def source() -> dict[str, Any]:
    sources = [
        {key: value for key, value in row.items() if key not in {"record_kind", "edition"}}
        for row in AUDIT["sources"]
    ]
    kinds = [
        {"kind": "product", "definition": "Independently adopted, operated, supported and replaceable outcome promise."},
        {"kind": "semantic_contract", "definition": "Owner of exact identities, decisions, invariants and refusals."},
        {"kind": "capability", "definition": "Typed operation offered under one semantic contract."},
        {"kind": "implementation", "definition": "Observed provider or implementation; unqualified until conformance evidence exists."},
        {"kind": "neighbor", "definition": "Adjacent owner imported through a named anti-corruption layer."},
        {"kind": "optional_extension", "definition": "Removable predictive, generative or agent proposal/method surface."},
        {"kind": "standard", "definition": "External editioned specification; neither product nor provider qualification."},
    ]

    artifacts: list[dict[str, Any]] = []
    ddd_dossiers: list[dict[str, Any]] = []
    for key, product in PRODUCTS.items():
        artifacts.append(art(
            product["id"], "product", product["name"], product["question"], product["sources"],
            adoption=True, operated=True,
            sovereign_question=product["question"], users=product["users"], harmed_parties=product["harmed_parties"],
            jobs=[product["job"]], outcomes=product["outcomes"],
            lifecycle_states=product["states"], commands=product["commands"], events=product["events"],
            invariants=product["invariants"], refusals=product["refusals"], negative_mission=product["negative_mission"],
            automation_modality={
                "default": "DETERMINISTIC_CORE_ONLY",
                "postures": ["PROHIBITED", "OPTIONAL", "REQUIRED_BY_INTENT", "UNDETERMINED"],
                "law": "Models and agents may satisfy typed method/proposal requirements but never own semantics, acceptance, authority, effects or receipts.",
                "hard_work_law": "Automation never replaces vocabulary, boundary adjudication, invariants, state machines, evidence, law oracles, qualification or domain acceptance.",
            },
        ))
        ddd_dossiers.append({
            "dossier_id": f"ddd.ao.{key}",
            "product_ref": product["id"],
            "status": "candidate_not_ratified",
            "product_truth": {
                "sovereign_question": product["question"],
                "users": product["users"],
                "harmed_parties": product["harmed_parties"],
                "jobs": [product["job"]],
                "measurable_outcomes": product["outcomes"],
                "negative_mission": product["negative_mission"],
            },
            "strategic_and_tactical_ddd": {
                **product["ddd"],
                "aggregate_invariants": product["invariants"],
                "commands": product["commands"],
                "domain_events": product["events"],
                "refusal_failure_catalog": product["refusals"],
                "state_machine": {"states": product["states"], "transition_policy": "Only named commands under aggregate invariants may emit the corresponding past-tense event."},
            },
        })

    artifacts.extend([
        art("component.ao.optional_model_agent_extension", "optional_extension", "Optional model or agent extension", "Intent-selected predictive, generative or tool-agent method/proposal port. Removal preserves every deterministic product lifecycle.", refs("labelstudio_label", "google_docai_overview", "merlic_getting_started", "iso_13379")),
        art("implementation.ao.openrefine", "implementation", "OpenRefine", "Observed interactive data-preparation workbench; unqualified here.", refs("openrefine_start", "openrefine_history", "openrefine_transform")),
        art("implementation.ao.cvat", "implementation", "CVAT", "Observed annotation, review and ground-truth operations implementation; unqualified here.", refs("cvat_qa", "cvat_manual_review", "cvat_auto_qa")),
        art("implementation.ao.labelstudio", "implementation", "Label Studio", "Observed annotation and optional prelabeling implementation; unqualified here.", refs("labelstudio_project", "labelstudio_label", "labelstudio_consensus")),
        art("implementation.ao.tika", "implementation", "Apache Tika", "Observed document detection and parser toolkit; a method provider rather than the complete document product.", refs("tika_home", "tika_detector")),
        art("implementation.ao.unstructured", "implementation", "Unstructured", "Observed document partitioning/content-element implementation; unqualified here.", refs("unstructured_partition", "unstructured_chunk")),
        art("implementation.ao.google_docai", "implementation", "Google Document AI", "Observed document processor lifecycle and output model; unqualified here.", refs("google_docai_overview", "google_docai_api", "google_document")),
        art("implementation.ao.aws_textract", "implementation", "Amazon Textract", "Observed document extraction and legacy human-review integration; unqualified and lifecycle-limited here.", refs("aws_textract_review")),
        art("implementation.ao.mvtec_merlic", "implementation", "MVTec MERLIC", "Observed visual-inspection authoring/runtime implementation; unqualified here.", refs("merlic_getting_started", "merlic_process", "merlic_results")),
        art("implementation.ao.scipy_signal", "implementation", "SciPy signal", "Observed signal-processing method library; not the monitoring/diagnostic product.", refs("scipy_signal")),
        art("standard.ao.web_annotation", "standard", "W3C Web Annotation", "External body/target/selector/motivation model.", refs("w3c_annotation")),
        art("standard.ao.iso_condition_family", "standard", "ISO condition monitoring family", "External programme, processing, diagnostics and prognostics guidance.", refs("iso_17359", "iso_13374", "iso_13379", "iso_13381")),
        art("standard.ao.osa_cbm", "standard", "MIMOSA OSA-CBM", "External condition-monitoring functional architecture and information interfaces.", refs("mimosa_osacbm", "mimosa_osaeai")),
    ])

    neighbors = {
        "source_truth": "Owns source-system occurrences, corrections and mutation semantics.",
        "transform_build": "Owns production transformation build, deployment and scheduled execution contracts.",
        "quality": "Owns reusable data-quality assertions, measurements, incidents and remediation semantics.",
        "model_lifecycle": "Owns model training, evaluation, release, monitoring and retirement.",
        "ingestion": "Owns byte/object delivery and delivery receipts.",
        "records_authority": "Owns retention, hold and disposition authority.",
        "business_case": "Owns downstream factual acceptance and business-case decisions.",
        "device_runtime": "Owns physical acquisition device offers, resource control and runtime receipts.",
        "vertical_quality": "Owns industry defect vocabulary, tolerances, harms and acceptance authority.",
        "machine_control": "Owns PLC/control authorization, safety interlocks and physical effect receipts.",
        "telemetry": "Owns signal transport/storage occurrences and delivery semantics.",
        "asset_master": "Owns asset identity, configuration and reference-data authority.",
        "maintenance": "Owns maintenance plans, work orders, dispatch and completion.",
        "protective_control": "Owns safety/protective control decisions and effects.",
    }
    for suffix, definition in neighbors.items():
        family = "condition" if suffix in {"telemetry", "asset_master", "maintenance", "protective_control"} else "inspection" if suffix in {"device_runtime", "vertical_quality", "machine_control"} else "document" if suffix in {"ingestion", "records_authority", "business_case"} else "preparation"
        artifacts.append(art(f"neighbor.{suffix}", "neighbor", suffix.replace("_", " ").title(), definition, PRODUCTS[family]["sources"][:2]))

    ownership: list[dict[str, Any]] = []
    libraries: list[dict[str, Any]] = []
    requirements: list[dict[str, Any]] = []
    binding_maps: list[dict[str, Any]] = []
    binding_gaps: list[dict[str, Any]] = []
    for product_key, suffix, name, operation, decision, invariant, refusal, concrete, evidence_refs, effectful in LIBRARY_SPECS:
        concrete = EXACT_COMPILER_OVERRIDES.get((product_key, suffix), concrete)
        product = PRODUCTS[product_key]
        owner = f"semantic.ao.{product_key}.{suffix}"
        capability = f"capability.ao.{product_key}.{suffix}"
        abstract = f"library.adjudicated.ao.{product_key}.{suffix}"
        artifacts.append(art(owner, "semantic_contract", name, f"Owns {name.lower()} identity, decisions, invariants and refusals.", evidence_refs))
        artifacts.append(art(capability, "capability", operation.replace("_", " ").title(), f"Typed capability to {operation.replace('_', ' ')}.", evidence_refs, owner=owner))
        ownership.append({
            "meaning_id": f"meaning.ao.{product_key}.{suffix}",
            "term": name,
            "owner_ref": owner,
            "invariant": invariant,
            "must_not_be_owned_by": ["component.ao.optional_model_agent_extension", "neighbor.source_truth", "neighbor.machine_control", "neighbor.maintenance"],
        })
        type_name = camel(f"{product_key}_{suffix}")
        libraries.append({
            "library_id": abstract,
            "class": "runtime_boundary" if effectful else "semantic_pure",
            "product_ref": product["id"],
            "owner_ref": owner,
            "provides": [capability],
            "types": [type_name, f"{type_name}Decision", f"{type_name}Refusal", f"{type_name}Receipt"],
            "operations": [operation],
            "decisions": [decision],
            "invariants": [
                invariant,
                "provider_identity_does_not_change_semantics",
                "partiality_uncertainty_and_abstention_are_explicit",
                "generated_or_agent_output_is_non_authoritative_until_typed_validated_and_accepted",
                "removing_model_and_agent_extensions_preserves_the_deterministic_core_contract",
            ],
            "refusals": [refusal, "unsupported_capability", "unresolved_authority", "resource_exhausted", "cancelled"],
            "dependencies": [],
            "effect_boundary": "effect_intents_attempts_and_receipts" if effectful else "pure_no_io",
            "evidence_refs": evidence_refs,
        })
        requirements.append({
            "requirement_id": f"requirement.ao.{product_key}.{suffix}",
            "consumer_ref": product["id"],
            "capability_ref": capability,
            "minimum_qualified_offers": 2,
            "binding_phase": "deployment_time" if effectful else "compile_time",
            "status": "unbound",
            "refusal": "refuse compilation or execution when no exact compatible qualified offer exists",
        })
        gap_ref = None
        disposition = "registry_contract_present_unqualified"
        if not concrete:
            gap_ref = f"gap.ao.binding.{product_key}.{suffix}"
            disposition = "missing_exact_compiler_library_contract"
            binding_gaps.append({
                "gap_id": gap_ref,
                "product_ref": product["id"],
                "abstract_library_ref": abstract,
                "statement": f"No exact compiler registry contract currently owns {name.lower()}.",
                "blocking": True,
                "closure_evidence": "Add one exact semantic-owner library contribution with typed decisions, invariants, refusals, effect boundary and executable law oracles; qualification remains separate.",
            })
        binding_maps.append({
            "binding_map_id": f"binding.ao.{product_key}.{suffix}",
            "product_ref": product["id"],
            "abstract_library_ref": abstract,
            "compiler_disposition": disposition,
            "concrete_library_refs": concrete,
            "gap_ref": gap_ref,
            "portable_offer": False,
        })

    decisions = [{
        "decision_id": f"decision.ao.{key}.product",
        "subject_ref": product["id"],
        "disposition": "strong_product_candidate",
        "rationale": f"{product['name']} has a separate adopted job, ubiquitous language, aggregate lifecycle, authority/support boundary, operation and full-fidelity exit. It imports rather than absorbs adjacent source, model, device, quality, business, maintenance and effect authority.",
        "evidence_refs": product["sources"],
        "split_test": split(product["scores"], product["sources"], product["name"]),
    } for key, product in PRODUCTS.items()]
    decisions.extend([
        {"decision_id": "decision.ao.method_families", "subject_ref": "component.ao.optional_model_agent_extension", "disposition": "retain_as_optional_typed_method_or_proposal_extension", "rationale": "Rule-based, statistical, predictive, generative and agent-assisted mechanisms bind behind product-owned contracts. None creates a parallel product or acquires acceptance/effect authority.", "evidence_refs": refs("labelstudio_label", "google_docai_overview", "merlic_getting_started", "iso_13379")},
        {"decision_id": "decision.ao.provider_bundles", "subject_ref": "implementation.ao.mvtec_merlic", "disposition": "observed_bundle_not_semantic_owner", "rationale": "Provider bundles may combine authoring, kernels, runtimes and UI, but package shape cannot merge the exact semantic and authority boundaries.", "evidence_refs": refs("merlic_getting_started", "merlic_process")},
    ])

    offer_specs = [
        ("openrefine", "implementation.ao.openrefine", "preparation", ["preparation_project", "column_profile", "facet_and_filter", "typed_transform_recipe", "reversible_history", "recipe_replay", "data_diff", "prepared_output_publication"]),
        ("cvat", "implementation.ao.cvat", "annotation", ["annotation_schema", "task_sampling", "work_assignment", "annotation_occurrence", "review_issue", "correction", "agreement_metric", "adjudication", "ground_truth_edition", "annotation_export"]),
        ("labelstudio", "implementation.ao.labelstudio", "annotation", ["annotation_schema", "target_selector", "work_assignment", "annotation_occurrence", "review_issue", "agreement_metric", "consensus", "ground_truth_edition", "annotation_export"]),
        ("tika", "implementation.ao.tika", "document", ["document_admission", "carrier_detection", "partitioning"]),
        ("unstructured", "implementation.ao.unstructured", "document", ["document_admission", "carrier_detection", "content_graph", "partitioning", "ocr_method", "layout_method", "table_and_form_extraction"]),
        ("google_docai", "implementation.ao.google_docai", "document", ["document_admission", "bounded_rendering", "page_revision_identity", "content_graph", "ocr_method", "layout_method", "table_and_form_extraction", "schema_extraction", "validation", "human_review", "structured_output_release"]),
        ("aws_textract", "implementation.ao.aws_textract", "document", ["ocr_method", "table_and_form_extraction", "human_review"]),
        ("mvtec_merlic", "implementation.ao.mvtec_merlic", "inspection", ["inspection_plan", "acquisition_profile", "calibration", "region_of_interest", "tool_flow", "recipe", "inspection_execution", "method_result", "tolerance_evaluation", "inspection_result", "machine_integration_port"]),
        ("scipy_signal", "implementation.ao.scipy_signal", "condition", ["signal_windowing", "filter_and_spectral_kernels"]),
    ]
    artifact_by_id = {row["artifact_id"]: row for row in artifacts}
    offers = [{
        "offer_id": f"offer.ao.{name}",
        "provider_ref": provider,
        "capability_refs": [f"capability.ao.{product_key}.{suffix}" for suffix in suffixes],
        "status": "observed_unqualified",
        "qualified_implementation_count": 0,
        "portable": False,
        "evidence_refs": artifact_by_id[provider]["evidence_refs"],
    } for name, provider, product_key, suffixes in offer_specs]

    relations = []
    for key, product in PRODUCTS.items():
        for row in product["ddd"]["context_map"]:
            relations.append({
                "relation_id": f"relation.ao.{key}.{row['neighbor_ref'].split('.')[-1]}",
                "from_ref": product["id"],
                "predicate": "requires",
                "to_ref": row["neighbor_ref"],
                "binding_phase": "runtime" if row["neighbor_ref"] in {"neighbor.machine_control", "neighbor.maintenance", "neighbor.protective_control"} else "compile_time",
            })
        relations.append({
            "relation_id": f"relation.ao.optional_extension.{key}",
            "from_ref": "component.ao.optional_model_agent_extension",
            "predicate": "offers",
            "to_ref": product["id"],
            "binding_phase": "deployment_time",
        })

    crosswalks = [{
        "legacy_ref": product["legacy"],
        "canonical_refs": [product["id"]],
        "disposition": "promote_inventory_hypothesis_to_strong_product_candidate_pending_ratification",
    } for product in PRODUCTS.values()]
    crosswalks.extend([
        {"legacy_ref": "semantic.media_signal_analysis", "canonical_refs": ["product.visual_inspection_operations", "product.signal_condition_diagnostics", "component.ao.optional_model_agent_extension"], "disposition": "split_job_products_from_method_family"},
        {"legacy_ref": "term.intelligent_document_processing", "canonical_refs": ["product.document_processing_review", "component.ao.optional_model_agent_extension"], "disposition": "remove_ai_packaging_from_product_identity"},
        {"legacy_ref": "term.training_data_platform", "canonical_refs": ["product.annotation_operations", "neighbor.model_lifecycle"], "disposition": "split_annotation_operations_from_model_lifecycle"},
        {"legacy_ref": "term.data_wrangling", "canonical_refs": ["product.self_service_data_preparation", "neighbor.transform_build"], "disposition": "split_interactive_workbench_from_production_transform"},
    ])

    negative_tests = [{"test_id": f"negative.ao.{ident}", "prohibited_claim": claim, "expected_result": result} for ident, claim, result in NEGATIVES]
    semantic_gaps = [{
        "gap_id": f"gap.ao.semantic.{ident}",
        "gap_class": "semantic_or_conformance",
        "statement": statement,
        "blocking": True,
        "closure_evidence": "Publish an exact semantic owner and profile, typed refusal, executable law/conformance oracle, and evidence from two independent implementations or accepted occurrences.",
    } for ident, statement in SEMANTIC_GAPS]

    return {
        "contract_id": "contract.product_adjudication.analytical_operations.v0_1_0",
        "edition": 1,
        "status": "evidence_backed_adjudicated_candidates_not_ratified",
        "scope": "Five job-specific analytical-operation products: self-service data preparation, annotation/ground-truth operations, document processing/review, visual inspection operations, and signal condition monitoring/diagnostics.",
        "negative_scope": "Does not qualify providers, ratify products, create AI-prefixed duplicates, own industry vocabularies, accept extracted/predicted values as truth, or authorize downstream machine/maintenance effects.",
        "artifact_kinds": kinds,
        "sources": sources,
        "artifacts": artifacts,
        "boundary_decisions": decisions,
        "ownership": ownership,
        "libraries": libraries,
        "requirements": requirements,
        "offers": offers,
        "relations": relations,
        "crosswalks": crosswalks,
        "negative_tests": negative_tests,
        "binding_maps": binding_maps,
        "binding_gaps": binding_gaps,
        "semantic_gaps": semantic_gaps,
        "ddd_dossiers": ddd_dossiers,
        "non_collapse_laws": [
            "interactive preparation != production transform build != notebook != data-quality assertion",
            "prediction != annotation occurrence != review != consensus != adjudication != ground-truth edition",
            "document carrier != page/content graph != extraction candidate != reviewed structured output != accepted business fact",
            "vision method result != inspection result != quality disposition != authorized machine effect != physical receipt",
            "signal sample != indicator != state != health assessment != diagnosis != prognosis != advisory != maintenance authorization",
            "statistical predictive heuristic and generative methods are modalities behind typed contracts, not ambient semantic owners",
            "tool agent proposal != accepted command != authority != executed effect != receipt != business outcome",
            "removing every model and agent extension preserves the complete deterministic product lifecycle",
            "automation never replaces vocabulary, invariants, state machines, algorithms, evidence, negative tests, qualification or domain acceptance",
            "horizontal product semantics != industry taxonomy threshold workflow or authority; those bind through solution packs",
            "official documentation != conformance != qualification != portability",
        ],
    }


def source_bytes() -> bytes:
    return (json.dumps(enrich_image_analysis(enrich_dataset_curation(source())), ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode()


if __name__ == "__main__":
    SOURCE.write_bytes(source_bytes())
