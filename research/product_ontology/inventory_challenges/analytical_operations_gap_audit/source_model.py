#!/usr/bin/env python3
"""Evidence-backed challenge of omitted analytical-operation product boundaries."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "source.json"
AS_OF = "2026-08-26"


def evidence(
    ident: str,
    title: str,
    publisher: str,
    uri: str,
    claim: str,
    scope_limit: str,
    family: str,
) -> dict[str, Any]:
    return {
        "source_id": f"evidence.aoga.{ident}",
        "record_kind": "primary_source_evidence",
        "source_class": "official_standard_or_documentation",
        "title": title,
        "publisher": publisher,
        "uri": uri,
        "claim": claim,
        "scope_limit": scope_limit,
        "family": family,
        "retrieved_at": AS_OF,
    }


def refs(*idents: str) -> list[str]:
    return [f"evidence.aoga.{ident}" for ident in idents]


SOURCES = [
    # Interactive data preparation.
    ("openrefine_start", "Starting a project", "OpenRefine", "https://openrefine.org/docs/manual/starting", "A preparation project imports a copy, retains edits and exports a result without mutating the source.", "One implementation does not prove every collaborative, scale or deployment requirement.", "self_service_data_preparation"),
    ("openrefine_history", "Running OpenRefine: History", "OpenRefine", "https://openrefine.org/docs/manual/running/", "Data-changing operations form ordered undo/redo history and extractable JSON recipes.", "Some view state and cell edits are not reusable operations.", "self_service_data_preparation"),
    ("openrefine_facets", "Exploring facets", "OpenRefine", "https://openrefine.org/docs/manual/facets", "Facets expose data variance and select subsets for inspection and correction.", "Facets are exploratory views and do not themselves prove governed publication.", "self_service_data_preparation"),
    ("openrefine_transform", "Transforming data", "OpenRefine", "https://openrefine.org/docs/manual/transforming/", "The workbench supports explicit cleaning, correction, restructuring, clustering and enrichment operations.", "Supported operations and data sizes are implementation-specific.", "self_service_data_preparation"),
    ("openrefine_export", "Exporting your work", "OpenRefine", "https://openrefine.org/docs/manual/exporting", "Projects, histories and reusable operations can be exported; archives can expose prior confidential states.", "Export is not equivalent to downstream data-product acceptance.", "self_service_data_preparation"),
    ("openrefine_architecture", "OpenRefine architecture before version 4", "OpenRefine", "https://openrefine.org/docs/technical-reference/architecture-before-4", "Operations, processes, changes and history entries are distinct runtime identities with ordered apply/revert semantics.", "This documents one architecture edition and not a universal implementation design.", "self_service_data_preparation"),

    # Annotation and ground-truth operations.
    ("cvat_qa", "QA and Analytics", "CVAT", "https://docs.cvat.ai/docs/qa-analytics/", "Annotation work has explicit ground-truth, review, consensus, issue and quality-control concerns.", "Feature availability differs by edition and data shape.", "annotation_operations"),
    ("cvat_manual_review", "Manual QA and Review", "CVAT", "https://docs.cvat.ai/docs/qa-analytics/manual-qa/", "Review has assignable roles, validation stage, issues, correction, comments, resolution and completion.", "The described review mode excludes some 3D work.", "annotation_operations"),
    ("cvat_auto_qa", "Automated QA, Review and Honeypots", "CVAT", "https://docs.cvat.ai/docs/manual/advanced/analytics-and-monitoring/auto-qa/", "Ground-truth jobs, validation sampling, seeds, acceptance state, quality reports and conflicts have separate identities.", "The documented modes have task- and annotation-type limitations.", "annotation_operations"),
    ("cvat_analytics", "Analytics", "CVAT", "https://docs.cvat.ai/docs/qa-analytics/analytics/", "Projects, tasks and jobs expose stage, state, assignee, throughput and ground-truth occurrence data.", "Operational metrics do not prove annotation correctness or ground-truth authority.", "annotation_operations"),
    ("labelstudio_project", "Create and configure projects", "Label Studio", "https://labelstud.io/guide/setup_project.html", "Labeling occurs inside projects with imported data, interfaces, instructions, task sampling and roles.", "Product documentation does not define a portable annotation contract.", "annotation_operations"),
    ("labelstudio_label", "Label and annotate data", "Label Studio", "https://labelstud.io/guide/labeling", "Manual annotations and optional model suggestions are separate; suggestions can be accepted, rejected or refined.", "Some predicted text regions have product-specific acceptance behavior.", "annotation_operations"),
    ("labelstudio_consensus", "Inter-annotator agreement and human consensus", "Label Studio", "https://labelstud.io/tutorials/how_to_measure_inter_annotator_agreement_and_build_human_consensus.html", "Agreement, consensus, ground truth, re-annotation and model comparison are distinct operations and outputs.", "A tutorial is implementation evidence, not a universal adjudication law.", "annotation_operations"),
    ("w3c_annotation", "Web Annotation Data Model", "W3C", "https://www.w3.org/TR/annotation-model/", "Annotation body, target, selector, motivation, creator and lifecycle metadata are separable semantic identities.", "The web model does not define workforce assignment or ground-truth authority.", "annotation_operations"),

    # Document processing and review.
    ("tika_home", "Apache Tika", "Apache Software Foundation", "https://tika.apache.org/", "Detection, metadata extraction and text extraction span many document carrier types behind common interfaces.", "Tika is a toolkit, not a document-case product or human-review workflow.", "document_processing_review"),
    ("tika_detector", "Apache Tika Detector interface", "Apache Software Foundation", "https://tika.apache.org/3.3.1/api/org/apache/tika/detect/Detector.html", "Content detection may use stream bytes and metadata and may return an unknown octet-stream type.", "A detector result is evidence, not unquestionable carrier truth.", "document_processing_review"),
    ("unstructured_partition", "Partitioning", "Unstructured", "https://docs.unstructured.io/open-source/core-functionality/partitioning", "Raw documents are detected and partitioned into typed document elements using format- and strategy-specific paths.", "Element typing and method quality vary by carrier and strategy.", "document_processing_review"),
    ("unstructured_chunk", "Chunking", "Unstructured", "https://docs.unstructured.io/open-source/core-functionality/chunking", "Chunking is a post-partition transformation with explicit size, overlap and boundary decisions.", "Chunking is one downstream representation operation and not the document product itself.", "document_processing_review"),
    ("google_docai_overview", "Document AI overview", "Google Cloud", "https://docs.cloud.google.com/document-ai/docs/overview", "Document processing separates digitization, extraction, classification, splitting, processor selection, training, evaluation and structured output.", "This implementation includes model methods but does not make models authoritative over review or downstream effects.", "document_processing_review"),
    ("google_docai_api", "Cloud Document AI API", "Google Cloud", "https://docs.cloud.google.com/document-ai/docs/reference/rest", "Processors and versions have create, enable, deploy, train, evaluate, process and batch-process lifecycles.", "API surface is provider-specific and human-review support includes deprecated paths.", "document_processing_review"),
    ("google_document", "Document resource", "Google Cloud", "https://docs.cloud.google.com/document-ai/docs/reference/rest/v1/Document", "A processed document includes pages, revisions, provenance and human-review status with requested, succeeded and rejected states.", "The resource model does not by itself authorize business decisions based on extracted fields.", "document_processing_review"),
    ("aws_textract_review", "HumanLoopConfig", "Amazon Web Services", "https://docs.aws.amazon.com/textract/latest/APIReference/API_HumanLoopConfig.html", "Document extraction can route qualifying occurrences into a named human-review workflow.", "Amazon A2I entered maintenance mode in 2026; this is lifecycle evidence and a provider-exit warning, not a recommended dependency.", "document_processing_review"),

    # Visual inspection operations.
    ("merlic_getting_started", "Getting Started with MERLIC", "MVTec", "https://www.mvtec.com/doc/merlic/26.03/manual/en-us/Content/Getting_started/getting_started.html", "A vision application separates acquisition, processing steps, configuration, UI, recipes and runtime integration.", "One vendor bundle may package several boundaries together.", "visual_inspection_operations"),
    ("merlic_tools", "MERLIC Tool Reference", "MVTec", "https://www.mvtec.com/doc/merlic/26.03/manual/en-us/Content/Tool_reference/tool_reference.html", "Acquisition, calibration, alignment, preprocessing, processing, evaluation, file access and system tools are distinct method stages.", "Tool categories do not define business defect taxonomies or acceptance authority.", "visual_inspection_operations"),
    ("merlic_evaluation", "Image Evaluation", "MVTec", "https://www.mvtec.com/doc/merlic/5.8/manual/en-us/Content/Tool_reference/Evaluation/evaluation.html", "Regions, contours, expressions and conditional execution are evaluated after detection methods.", "An evaluation result is not automatically a disposition of the inspected item.", "visual_inspection_operations"),
    ("merlic_checking", "Image Checking", "MVTec", "https://www.mvtec.com/doc/merlic/5.7/manual/en-us/Content/Tool_reference/Processing/Checking/checking.html", "Inspection may use trained or rule-based presence, color and tolerance checks to produce good/bad judgments.", "A good/bad method result is not a universal quality decision or effect authorization.", "visual_inspection_operations"),
    ("merlic_process", "MERLIC Process Integration", "MVTec", "https://www.mvtec.com/doc/merlic/5.6/manual/en-us/Content/Process_integration/merlic_process_integration.html", "Recipes bind application and parameters; machine controllers control execution, observe state and query results through separate integration paths.", "PLC authority and machine effects remain external to the analytical inspection product.", "visual_inspection_operations"),
    ("merlic_results", "Inspecting results", "MVTec", "https://www.mvtec.com/doc/merlic/5.7/manual/en-us/Content/RTE_plugins/Standard_plugins/REST/Built_in_web_app/web_app_results.html", "Inspection results have recipe, result, job and timestamp identities and bounded retention.", "Session-buffered results are insufficient audit or preservation evidence.", "visual_inspection_operations"),
    ("iso_visual", "ISO/TR 14997-2:2022", "ISO", "https://www.iso.org/standard/75056.html", "Machine-vision inspection setup has fidelity, repeatability and reproducibility concerns relative to an inspector-based grading method.", "The technical report is scoped to optical surface imperfections, not all inspection domains.", "visual_inspection_operations"),
    ("genicam", "GenICam Standard", "European Machine Vision Association", "https://www.emva.org/wp-content/uploads/GenICam_Standard_v2_0.pdf", "Camera description and acquisition interoperability are separable from inspection semantics.", "Camera interface conformance does not qualify an inspection recipe or result.", "visual_inspection_operations"),

    # Signal, condition monitoring, diagnostics and prognosis.
    ("iso_17359", "ISO 17359:2018", "ISO", "https://www.iso.org/standard/71194.html", "Condition monitoring begins with a governed monitoring programme applicable across machine types.", "The abstract does not expose every procedure or domain-specific threshold.", "signal_condition_diagnostics"),
    ("iso_13374", "ISO 13374-1:2003", "ISO", "https://www.iso.org/cms/%20render/live/en/sites/isoorg/contents/data/standard/02/18/21832.html", "Condition monitoring software separates data processing, communication and presentation concerns.", "Part 1 is general guidance and not an implementation qualification.", "signal_condition_diagnostics"),
    ("iso_13379", "ISO 13379-1:2025", "ISO", "https://www.iso.org/standard/88027.html", "Diagnostics has common concepts, technical characteristics, system-development guidance and application-specific method selection.", "The diagnostic approach and evidence remain occurrence- and application-specific.", "signal_condition_diagnostics"),
    ("iso_13381", "ISO 13381-1:2025", "ISO", "https://www.iso.org/standard/51436.html", "Prognostics has distinct data, process, behavior and method concerns including trending and remaining-life approaches.", "The URI also exposes prior-edition lifecycle; exact current-edition content requires edition control.", "signal_condition_diagnostics"),
    ("mimosa_osacbm", "MIMOSA OSA-CBM", "MIMOSA", "https://www.mimosa.org/mimosa-osa-cbm/", "A condition-based-maintenance architecture separates acquisition, manipulation, state detection, health assessment, prognosis and advisory information.", "The latest listed OSA-CBM release is old and must not be treated as sufficient current conformance evidence.", "signal_condition_diagnostics"),
    ("mimosa_osaeai", "MIMOSA OSA-EAI", "MIMOSA", "https://www.mimosa.org/mimosa-osa-eai/", "Asset registry, condition, reliability and maintenance information can be exchanged through layered, independently usable components.", "Legacy transports and schemas need current security and interoperability qualification.", "signal_condition_diagnostics"),
    ("ni_condition", "What Is Condition Monitoring?", "NI", "https://www.ni.com/en/solutions/condition-monitoring/what-is-condition-monitoring.html", "Condition monitoring spans vibration, thermal, acoustic and other signals, with analysis, human review and sometimes protective response.", "Vendor solution guidance does not establish universal diagnostic accuracy or effect authority.", "signal_condition_diagnostics"),
    ("scipy_signal", "Signal processing reference", "SciPy", "https://docs.scipy.org/doc/scipy/reference/signal.html", "Filtering, convolution, resampling, spectral estimation and related kernels are method libraries distinct from the monitoring programme and diagnosis lifecycle.", "Kernel availability does not select parameters or prove diagnostic fitness.", "signal_condition_diagnostics"),
]


def scores(**values: int) -> dict[str, int]:
    axes = ["user", "job", "adoption", "semantics", "authority", "lifecycle", "operation", "economics", "interface", "market_evidence"]
    assert set(values) == set(axes)
    return {axis: values[axis] for axis in axes}


HYPOTHESES = [
    {
        "hypothesis_id": "hypothesis.aoga.self_service_data_preparation",
        "proposed_product_id": "candidate.product.self_service_data_preparation",
        "name": "Self-Service Data Preparation Workbench",
        "sovereign_question": "How can a data practitioner inspect, repair and reshape one admitted data cut through a reviewable recipe without mutating its source?",
        "primary_users": ["data_practitioner", "analyst", "data_steward"],
        "owned_job": "interactive profiling, repair, transformation-recipe authoring, replay, diff and prepared-output publication",
        "owned_meanings": ["preparation_project", "admitted_data_cut", "profile_view", "facet_selection", "transformation_recipe", "recipe_history", "prepared_output_edition"],
        "excluded_meanings": ["source_system_fact", "scheduled_pipeline_operation", "production_transform_deployment", "master_identity_authority", "business_metric_definition"],
        "nearest_existing_candidates": ["candidate.product.batch_transform_build", "candidate.product.analytical_notebook", "candidate.product.data_quality_operations"],
        "collision_ruling": "The workbench owns an interactive project and reversible recipe-authoring lifecycle; batch transform owns a deployed build contract, notebook owns a general computational document, and quality owns requirements, validation and defect evidence rather than manual reshaping.",
        "deterministic_core": ["carrier_and_schema_admission", "profiling", "faceting", "typed_transform_execution", "ordered_history", "replay", "diff", "export_and_provenance_receipt"],
        "optional_method_bindings": ["heuristic_clustering", "probabilistic_type_inference", "model_suggested_repairs"],
        "lifecycle_states": ["draft", "data_admitted", "profiling", "recipe_editing", "review_ready", "accepted", "published", "superseded", "withdrawn"],
        "evidence_refs": refs("openrefine_start", "openrefine_history", "openrefine_facets", "openrefine_transform", "openrefine_export", "openrefine_architecture"),
        "split_scores": scores(user=2, job=2, adoption=2, semantics=2, authority=1, lifecycle=2, operation=1, economics=1, interface=2, market_evidence=2),
        "preliminary_disposition": "promote_for_full_adjudication",
        "falsifiers": ["Users cannot adopt it independently from a notebook or transform system.", "The reversible preparation project has no distinct lifecycle or exit artifact.", "All meaningful use is already governed by the deployed transform-build product."],
        "missing_evidence": ["multi-user concurrency and review semantics", "large-data execution split", "two independent portable recipe implementations"],
    },
    {
        "hypothesis_id": "hypothesis.aoga.annotation_operations",
        "proposed_product_id": "candidate.product.annotation_operations",
        "name": "Annotation and Ground-Truth Operations",
        "sovereign_question": "How can an annotation owner turn selected source occurrences into a versioned, reviewed and quality-evidenced annotation dataset?",
        "primary_users": ["annotation_owner", "annotator", "reviewer", "dataset_steward"],
        "owned_job": "schema binding, task allocation, annotation, review, correction, consensus, adjudication, quality sampling and ground-truth release",
        "owned_meanings": ["annotation_project", "label_schema_binding", "annotation_task", "assignment", "annotation_occurrence", "review_issue", "consensus_result", "adjudication_decision", "ground_truth_edition"],
        "excluded_meanings": ["model_training", "model_prediction", "source_content_identity", "business_factual_truth", "downstream_decision_authority"],
        "nearest_existing_candidates": ["candidate.product.model_lifecycle", "candidate.product.data_quality_operations", "candidate.product.data_product_publication"],
        "collision_ruling": "Annotation operations own human/task/ground-truth lifecycle; model lifecycle consumes released datasets, quality imports comparison kernels, and publication distributes an accepted edition without owning its annotation judgments.",
        "deterministic_core": ["target_and_selector_binding", "schema_validation", "assignment_and_role_control", "manual_annotation", "review_issue_lifecycle", "consensus_and_adjudication_rules", "quality_sampling", "versioned_export"],
        "optional_method_bindings": ["classical_prelabeling", "predictive_active_sampling", "generative_preannotation"],
        "lifecycle_states": ["draft", "configured", "sampling", "assigned", "annotating", "reviewing", "correcting", "adjudicating", "accepted", "released", "superseded", "recalled"],
        "evidence_refs": refs("cvat_qa", "cvat_manual_review", "cvat_auto_qa", "cvat_analytics", "labelstudio_project", "labelstudio_label", "labelstudio_consensus", "w3c_annotation"),
        "split_scores": scores(user=2, job=2, adoption=2, semantics=2, authority=2, lifecycle=2, operation=2, economics=2, interface=2, market_evidence=2),
        "preliminary_disposition": "promote_for_full_adjudication",
        "falsifiers": ["Annotation tasks are only an incidental screen inside model training.", "Ground-truth and review authority cannot be separated from the consuming model or application.", "No independent export, recall or workforce lifecycle exists."],
        "missing_evidence": ["portable multimodal selector contract", "adjudication precedence laws", "ground-truth recall propagation", "two independent conformance implementations"],
    },
    {
        "hypothesis_id": "hypothesis.aoga.document_processing_review",
        "proposed_product_id": "candidate.product.document_processing_review",
        "name": "Document Processing and Review Operations",
        "sovereign_question": "How can a document operator convert one admitted document occurrence into typed, provenance-linked structured output with exceptions and review?",
        "primary_users": ["document_operator", "reviewer", "integration_owner", "records_steward"],
        "owned_job": "document admission, carrier detection, rendering, content-graph creation, extraction, validation, exception handling, human review and structured-output release",
        "owned_meanings": ["document_occurrence", "page_occurrence", "document_revision", "content_element", "extraction_schema_binding", "extraction_candidate", "validation_issue", "document_review_case", "structured_output_edition"],
        "excluded_meanings": ["generic_byte_ingestion", "records_retention_authority", "business_fact_acceptance", "search_index", "downstream_case_decision"],
        "nearest_existing_candidates": ["candidate.product.ingestion_delivery", "candidate.product.search_index_serving", "candidate.product.annotation_operations", "candidate.product.model_lifecycle"],
        "collision_ruling": "Ingestion delivers bytes, search indexes admitted content, annotation creates labels, and model lifecycle trains methods; this product owns the per-document processing/review occurrence and its structured-output evidence.",
        "deterministic_core": ["carrier_admission", "bounded_parser_dispatch", "page_and_revision_identity", "content_graph", "schema_validation", "exception_routing", "review_state_machine", "provenance_and_release_receipt"],
        "optional_method_bindings": ["ocr", "layout_model", "document_classifier", "extractive_model", "generative_extraction_proposal"],
        "lifecycle_states": ["received", "admitted", "partitioning", "extracting", "validation_pending", "exception", "human_review", "accepted", "rejected", "released", "reprocessed", "recalled"],
        "evidence_refs": refs("tika_home", "tika_detector", "unstructured_partition", "unstructured_chunk", "google_docai_overview", "google_docai_api", "google_document", "aws_textract_review"),
        "split_scores": scores(user=2, job=2, adoption=2, semantics=2, authority=1, lifecycle=2, operation=2, economics=2, interface=2, market_evidence=2),
        "preliminary_disposition": "promote_for_full_adjudication",
        "falsifiers": ["The only independent job is generic file conversion without review or exception lifecycle.", "Structured output cannot exit independently of one provider processor.", "The boundary duplicates source ingestion or downstream business case processing."],
        "missing_evidence": ["portable document content graph", "encrypted/signed document admission", "review sampling and precedence", "semantic-loss receipts across reprocessing"],
    },
    {
        "hypothesis_id": "hypothesis.aoga.visual_inspection_operations",
        "proposed_product_id": "candidate.product.visual_inspection_operations",
        "name": "Visual Inspection Operations",
        "sovereign_question": "How can an inspection owner configure, execute and review repeatable image-based inspections while preserving each item, recipe, result and disposition boundary?",
        "primary_users": ["inspection_engineer", "quality_operator", "reviewer", "line_integration_owner"],
        "owned_job": "inspection-plan authoring, acquisition binding, calibration, method composition, recipe release, occurrence execution, evidence review and inspection-result publication",
        "owned_meanings": ["inspection_plan", "acquisition_profile", "calibration_edition", "inspection_recipe", "inspected_item_occurrence", "image_evidence", "method_result", "inspection_result", "review_disposition"],
        "excluded_meanings": ["camera_driver", "generic_image_algorithm", "plant_quality_policy", "PLC_command_authority", "physical_reject_effect"],
        "nearest_existing_candidates": ["candidate.product.analytical_notebook", "candidate.product.online_inference", "candidate.product.decision_automation", "candidate.product.model_lifecycle"],
        "collision_ruling": "The product owns the inspection application/recipe and occurrence lifecycle; vision kernels and predictive models are replaceable methods, deterministic decisioning may interpret accepted results, and machine control owns physical effects.",
        "deterministic_core": ["item_and_image_identity", "acquisition_and_calibration_binding", "typed_tool_flow", "recipe_versioning", "threshold_and_tolerance_evaluation", "execution_state_machine", "result_evidence", "review_and_publication"],
        "optional_method_bindings": ["classical_machine_vision", "predictive_defect_model", "anomaly_model", "generative_explanation"],
        "lifecycle_states": ["draft", "calibrating", "recipe_testing", "qualified", "released", "ready", "executing", "result_ready", "review_pending", "accepted", "rejected", "halted", "superseded"],
        "evidence_refs": refs("merlic_getting_started", "merlic_tools", "merlic_evaluation", "merlic_checking", "merlic_process", "merlic_results", "iso_visual", "genicam"),
        "split_scores": scores(user=2, job=2, adoption=2, semantics=2, authority=2, lifecycle=2, operation=2, economics=2, interface=2, market_evidence=2),
        "preliminary_disposition": "promote_for_full_adjudication",
        "falsifiers": ["Every inspection necessarily changes vertical business semantics in the horizontal core.", "The inspection recipe has no adoption or exit boundary apart from a machine controller.", "A generic notebook plus image library owns the complete support and occurrence lifecycle."],
        "missing_evidence": ["cross-provider recipe interchange", "inspection uncertainty and abstention", "traceable item-result-effect separation", "two independent runtime conformance suites"],
    },
    {
        "hypothesis_id": "hypothesis.aoga.signal_condition_diagnostics",
        "proposed_product_id": "candidate.product.signal_condition_diagnostics",
        "name": "Signal Condition Monitoring and Diagnostics",
        "sovereign_question": "How can an asset or process owner operate an editioned monitoring programme that turns admitted signals into state, health, diagnosis and prognosis evidence?",
        "primary_users": ["reliability_engineer", "condition_monitoring_specialist", "maintenance_planner", "operations_reviewer"],
        "owned_job": "monitoring-program design, channel binding, signal preparation, state detection, health assessment, diagnosis, prognosis, advisory evidence and expert review",
        "owned_meanings": ["monitoring_program", "asset_channel_binding", "sampling_profile", "signal_window", "condition_indicator", "detected_state", "health_assessment", "diagnostic_case", "prognostic_case", "advisory"],
        "excluded_meanings": ["generic_telemetry_storage", "service_incident", "maintenance_work_order", "asset_master_identity", "protective_control_effect"],
        "nearest_existing_candidates": ["candidate.product.platform_operations", "candidate.product.forecasting_workbench", "candidate.product.online_inference", "candidate.product.decision_automation"],
        "collision_ruling": "Platform operations owns digital-service health, forecasting owns a forecasting study, inference serves a model, and decisioning interprets accepted claims; this product owns the monitoring programme plus state/health/diagnostic/prognostic case lifecycle.",
        "deterministic_core": ["asset_channel_and_unit_binding", "sampling_and_calibration_validation", "windowing_and_preprocessing", "method_plan", "state_thresholding", "case_state_machine", "confidence_and_uncertainty", "expert_review_and_evidence"],
        "optional_method_bindings": ["spectral_and_statistical_methods", "rules_and_expert_systems", "predictive_diagnostics", "remaining_useful_life_models", "generative_explanation"],
        "lifecycle_states": ["programme_draft", "instrumenting", "baselining", "active", "state_detected", "assessment_pending", "diagnosing", "prognosing", "review_pending", "advisory_issued", "closed", "reopened", "superseded"],
        "evidence_refs": refs("iso_17359", "iso_13374", "iso_13379", "iso_13381", "mimosa_osacbm", "mimosa_osaeai", "ni_condition", "scipy_signal"),
        "split_scores": scores(user=2, job=2, adoption=2, semantics=2, authority=2, lifecycle=2, operation=2, economics=2, interface=2, market_evidence=2),
        "preliminary_disposition": "promote_for_full_adjudication",
        "falsifiers": ["The domain is only a set of signal algorithms without a monitoring-program or case lifecycle.", "Asset condition meanings cannot be separated from one maintenance application.", "No independent adoption, operation, support or export boundary exists."],
        "missing_evidence": ["current portable state/health/diagnostic/prognostic contracts", "sensor and context quality laws", "diagnosis defeaters", "advisory-to-maintenance authority boundary"],
    },
]


DEFERRED = [
    ("statistical_study_workbench", "Statistical Study Workbench", ["candidate.product.analytical_notebook", "candidate.product.experimentation_platform"], "Need evidence for a distinct governed study/protocol/assumption/diagnostic/report lifecycle beyond notebooks and experimentation."),
    ("graph_analytics_workbench", "Graph Analytics Workbench", ["candidate.product.analytical_notebook", "candidate.product.distributed_query"], "Graph representation and algorithms are proven library families; an independent workbench product lifecycle remains unproved."),
    ("data_access_request_provisioning", "Data Access Request and Provisioning", ["candidate.product.data_use_policy", "candidate.product.data_marketplace"], "Need to separate request-case authority, entitlement provisioning, approval, revocation and marketplace fulfillment."),
    ("data_observability_incident_operations", "Data Observability and Incident Operations", ["candidate.product.data_quality_operations", "candidate.product.platform_operations"], "Need to determine whether data incidents have independent adoption, ownership and support or compose existing quality and operations products."),
    ("sensitive_data_discovery", "Sensitive-Data Discovery and Classification", ["candidate.product.metadata_discovery", "candidate.product.data_use_policy"], "Likely a classification capability plus review workflow; product independence and authority remain unproved."),
    ("data_migration_control", "Data Migration and Modernization Control", ["candidate.product.pipeline_orchestration", "candidate.product.data_quality_operations", "candidate.product.reconciliation_control_operations", "candidate.product.data_protection_recovery"], "A migration programme may be a temporary solution composition rather than a durable horizontal product."),
    ("operational_data_api_serving", "Operational Data Application and API Serving", ["candidate.product.virtual_data_access", "candidate.product.data_product_publication"], "This may belong to the application/runtime sovereign domain rather than the analytical-data product portfolio; cross-domain ownership must be adjudicated."),
]


LIBRARY_FAMILIES = {
    "self_service_data_preparation": ["preparation_project", "data_cut_admission", "column_profile", "facet_and_filter", "typed_transform_recipe", "reversible_history", "recipe_replay", "data_diff", "prepared_output_publication"],
    "annotation_operations": ["annotation_schema", "target_selector", "task_sampling", "work_assignment", "annotation_occurrence", "review_issue", "correction", "agreement_metric", "consensus", "adjudication", "ground_truth_edition", "annotation_export"],
    "document_processing_review": ["document_admission", "carrier_detection", "bounded_rendering", "page_revision_identity", "content_graph", "partitioning", "ocr_method", "layout_method", "table_and_form_extraction", "schema_extraction", "validation", "exception_case", "human_review", "structured_output_release"],
    "visual_inspection_operations": ["inspection_plan", "acquisition_profile", "calibration", "region_of_interest", "tool_flow", "recipe", "inspection_execution", "method_result", "tolerance_evaluation", "inspection_result", "review_disposition", "machine_integration_port"],
    "signal_condition_diagnostics": ["monitoring_program", "asset_channel_binding", "sampling_profile", "calibration", "signal_windowing", "filter_and_spectral_kernels", "state_detection", "health_assessment", "diagnostic_case", "prognostic_case", "advisory", "expert_review", "condition_evidence"],
}


NEGATIVES = [
    ("ai_prefix", "Create AI data-prep, AI annotation, AI document, AI inspection and AI diagnostics as parallel product families.", "Refuse: modality is orthogonal to the sovereign job and product boundary."),
    ("agent_research_substitute", "Accept an agent-generated vocabulary or invariant set without evidence and deterministic validation.", "Refuse: proposal must enter the ordinary typed review and acceptance path."),
    ("prelabel_ground_truth", "A model or LLM prelabel is ground truth.", "Refuse: prediction, annotation, consensus, adjudication and accepted ground truth remain distinct."),
    ("extraction_fact", "An extracted document field is an accepted business fact.", "Refuse: extraction candidate, validated output and downstream factual acceptance are distinct."),
    ("vision_effect", "A vision good/bad result directly commands physical rejection.", "Refuse: method result, inspection result, authorized effect intent and machine receipt are distinct."),
    ("diagnosis_work_order", "A diagnostic or prognostic result automatically creates an authorized maintenance effect.", "Refuse: advisory, relying decision, work authorization and maintenance occurrence are distinct."),
    ("kernel_product", "A parser, OCR engine, image algorithm or signal kernel is the complete product.", "Refuse: it is a method/library/provider until the user job and lifecycle split tests pass."),
    ("industry_in_core", "Put every industry defect, document and failure taxonomy in the horizontal library.", "Refuse: horizontal types and extension ports are stable; industry solution packs own vocabulary and thresholds."),
    ("deterministic_means_closed_form", "Ban probabilistic, predictive, heuristic, simulation or approximate methods from the deterministic architecture.", "Refuse: typed stochastic methods are valid when intent selects them and qualification exposes uncertainty and limits."),
    ("human_means_authority", "Any human click is authoritative acceptance.", "Refuse: role, competence, scope, edition, evidence cut and command preconditions must be proven."),
]


def source() -> dict[str, Any]:
    hypotheses = []
    for row in HYPOTHESES:
        item = dict(row)
        item["record_kind"] = "product_inventory_hypothesis"
        item["score_total"] = sum(item["split_scores"].values())
        item["status"] = "candidate_not_ratified"
        item["automation_modality"] = {
            "default": "DETERMINISTIC_CORE_ONLY",
            "allowed": ["PROHIBITED", "OPTIONAL", "REQUIRED_BY_INTENT", "UNDETERMINED"],
            "proposal_law": "Model or agent output is a typed proposal, never semantic ownership, ground truth, authority, executed effect or acceptance evidence by itself.",
            "removal_law": "Removing model and agent extensions preserves the deterministic product lifecycle; an explicitly requested stochastic capability may instead fail capability_unavailable.",
            "hard_work_law": "Automation does not replace vocabulary enumeration, semantic adjudication, invariants, state machines, algorithms, evidence, negative tests, qualification or domain acceptance.",
        }
        hypotheses.append(item)
    deferred = [
        {
            "deferred_id": f"deferred.aoga.{ident}",
            "record_kind": "deferred_inventory_hypothesis",
            "name": name,
            "nearest_existing_candidates": neighbors,
            "disposition": "research_before_promotion",
            "reason": reason,
            "status": "unresolved",
        }
        for ident, name, neighbors, reason in DEFERRED
    ]
    libraries = [
        {
            "library_hypothesis_id": f"library_hypothesis.aoga.{family}.{name}",
            "record_kind": "library_boundary_hypothesis",
            "product_hypothesis_ref": f"hypothesis.aoga.{family}",
            "name": name,
            "required_surface": ["types", "operations", "decisions", "invariants", "refusals", "effect_boundary", "qualification_profile", "law_oracle"],
            "status": "requires_full_adjudication",
        }
        for family, names in LIBRARY_FAMILIES.items()
        for name in names
    ]
    collision_tests = [
        {
            "collision_test_id": f"collision.aoga.{row['hypothesis_id'].removeprefix('hypothesis.aoga.')}",
            "record_kind": "boundary_collision_test",
            "hypothesis_ref": row["hypothesis_id"],
            "neighbor_refs": row["nearest_existing_candidates"],
            "ruling": row["collision_ruling"],
            "status": "preliminary_pass_requires_full_adjudication",
        }
        for row in HYPOTHESES
    ]
    gaps = [
        {
            "gap_id": f"gap.aoga.{row['hypothesis_id'].removeprefix('hypothesis.aoga.')}.{index}",
            "record_kind": "blocking_evidence_gap",
            "hypothesis_ref": row["hypothesis_id"],
            "statement": statement,
            "blocking_for_ratification": True,
            "closure_evidence": "Exact semantic contract, executable negative and positive law oracles, and two independent qualified implementations or bounded exception evidence.",
        }
        for row in HYPOTHESES
        for index, statement in enumerate(row["missing_evidence"], 1)
    ]
    return {
        "contract_id": "contract.product_inventory_challenge.analytical_operations_gap_audit.v0_1_0",
        "edition": 1,
        "as_of": AS_OF,
        "status": "evidence_backed_inventory_challenge_not_adjudicated_or_ratified",
        "scope": "Challenge the finite 66-candidate portfolio for omitted analytical-operation products whose user job, lifecycle and semantic authority are not reducible to existing method, pipeline, notebook, model or governance products.",
        "negative_scope": "Does not ratify products, qualify providers, create AI-prefixed duplicates, define industry-specific defect/failure taxonomies, or claim open-world completeness.",
        "sources": [evidence(*row) for row in SOURCES],
        "hypotheses": hypotheses,
        "deferred_hypotheses": deferred,
        "library_hypotheses": libraries,
        "collision_tests": collision_tests,
        "negative_tests": [
            {"negative_test_id": f"negative.aoga.{ident}", "record_kind": "negative_inventory_test", "prohibited_claim": claim, "expected_result": result}
            for ident, claim, result in NEGATIVES
        ],
        "blocking_gaps": gaps,
        "non_collapse_laws": [
            "interactive data preparation != deployed transformation build != notebook computation != quality assertion",
            "annotation proposal != annotation occurrence != review != consensus != adjudication != accepted ground-truth edition",
            "document carrier != rendered page != content element != extraction candidate != validated structured output != accepted business fact",
            "vision method result != inspection result != review disposition != authorized machine effect != physical effect receipt",
            "signal sample != condition indicator != detected state != health assessment != diagnosis != prognosis != advisory != maintenance authorization",
            "predictive or generative method != agent; modeled simulation agent != LLM tool agent",
            "optional automation != omitted deterministic research, domain modeling, qualification or acceptance work",
        ],
    }


def source_bytes() -> bytes:
    return (json.dumps(source(), ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode()


if __name__ == "__main__":
    SOURCE.write_bytes(source_bytes())
