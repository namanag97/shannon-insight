#!/usr/bin/env python3
"""Typed adjudication of the externally proposed 38-family Shannon frontier.

The incoming list is retained losslessly as a coverage challenge.  It is not
allowed to promote every row to a product: rows are classified by ontology
level and mapped to exact retained or candidate product identities.
"""

from __future__ import annotations

from source_model import source


FRONTIER_SOURCES = [
    source("looker_docs", "Looker documentation", "Google Cloud", "https://docs.cloud.google.com/looker/docs", "Looker independently exposes semantic modeling, exploration, dashboards, embedding, scheduling and alerting surfaces.", "One vendor suite does not prove that these surfaces share one product boundary.", "frontier_crosswalk"),
    source("observable_notebooks", "Observable notebook documentation", "Observable", "https://observablehq.com/documentation/notebooks/", "An editable computational document composes code, data, prose, controls and visual results as durable state.", "Notebook adoption does not make every presentation or publishing lifecycle a notebook concern.", "frontier_crosswalk"),
    source("sap_planning", "SAP Analytics Cloud planning documentation", "SAP", "https://help.sap.com/docs/SAP_ANALYTICS_CLOUD/00f68c2e08b941f081002fd3691d86a7/69a370e6cfd84315973101389baacde0.html", "Planning persists versions, assumptions, entry, allocation, actions and process state beyond analytical read views.", "Provider behavior does not define a portable planning contract.", "frontier_crosswalk"),
    source("sigma_input_tables", "Create new input tables", "Sigma Computing", "https://help.sigmacomputing.com/docs/create-new-input-tables", "Governed analytical writeback has durable input-table identity and change behavior rather than being an arbitrary table mutation.", "Input tables do not prove approval, planning or operational-effect authority.", "frontier_crosswalk"),
    source("statsig_experiments", "Experiment options", "Statsig", "https://docs.statsig.com/statsig-warehouse-native/features/experiment-options", "Experiment products independently operate assignment, exposure, analysis choices and experiment-result state.", "One implementation does not select universal estimands or decision policy.", "frontier_crosswalk"),
    source("neo4j_bloom_perspectives", "Bloom perspectives", "Neo4j", "https://neo4j.com/docs/bloom-user-guide/current/bloom-perspectives/bloom-perspectives/", "Graph exploration persists business perspectives and search/visual configuration beyond generic chart marks.", "Bloom does not own graph source truth or establish a universal graph-analysis product boundary.", "frontier_crosswalk"),
    source("looker_conversational", "Conversational analytics in Looker", "Google Cloud", "https://docs.cloud.google.com/looker/docs/conversational-analytics-looker-setup", "Governed conversational analysis is grounded in selected semantic-model and agent configuration state.", "Generated language cannot satisfy deterministic typing, authorization, execution or evidence obligations.", "frontier_crosswalk"),
]


# id, name, incoming status, ontology level, disposition, exact retained refs,
# candidate refs, bounded finding
ROWS = [
    ("H01", "Domain Semantics & Ontology", "STRONG", "PRODUCT_CLUSTER", "COVERED", ["product.ontology_knowledge_model", "product.business_glossary"], [], "Two retained owners cover formal knowledge models and governed business vocabulary; they must not be collapsed."),
    ("H02", "Measurement, Type, Time & Identity Semantics", "STRONG", "SHARED_SEMANTIC_FOUNDATION", "LIBRARY_AND_CONSTITUTION_NOT_ONE_PRODUCT", ["product.semantic_metric_formula_service", "product.schema_registry", "product.reference_data_governance"], [], "Units, time, identity, missingness and uncertainty are shared carrier laws consumed by several products, not sufficient evidence for one operated product."),
    ("H03", "Source Estate & Acquisition", "STRONG", "PRODUCT_CLUSTER", "COVERED", ["product.source_connectivity_control", "product.source_replication_cdc", "product.ingestion_delivery"], [], "Estate/control, change capture and managed delivery have separate lifecycles."),
    ("H04", "Data Contracts & Admission", "STRONG", "PRODUCT_CLUSTER", "COVERED", ["product.data_contract_registry", "product.schema_registry", "product.data_quality_operations"], [], "Contract authority, structural compatibility and executed admission/quality evidence remain distinct."),
    ("H05", "Data Products, Assets & Snapshots", "STRONG", "PRODUCT_CLUSTER", "COVERED", ["product.data_product_publication", "product.catalog_service", "product.managed_table_maintenance", "product.dataset_curation_workbench"], [], "Publication, catalog/commit authority, physical table maintenance and curation are separately owned."),
    ("H06", "Catalog, Glossary, Search & Discovery", "PRESENT", "PRODUCT_CLUSTER", "COVERED", ["product.metadata_discovery", "product.business_glossary", "product.catalog_service", "product.search_index_service"], [], "Discovery, vocabulary, commit authority and index serving are not one product."),
    ("H07", "Semantic Layer & Metric System", "STRONG", "PRODUCT", "COVERED", ["product.semantic_metric_formula_service"], [], "The retained semantic metric/formula owner already covers this boundary."),
    ("H08", "Analytics Engineering & Transformation", "STRONG", "PRODUCT_CLUSTER", "COVERED", ["product.batch_transform_build", "product.data_product_developer_platform", "product.self_service_data_preparation"], [], "Deterministic build, developer experience and human preparation have different actors and state."),
    ("H09", "Orchestration & Continuous Dataflow", "STRONG", "PRODUCT_CLUSTER", "COVERED", ["product.pipeline_orchestration", "product.dataflow_execution", "product.event_streaming"], [], "Control-plane orchestration, stateful execution and event transport remain separate."),
    ("H10", "Analytical Compute, Query & Acceleration", "FRAGMENTED", "PRODUCT_CLUSTER", "COVERED_BUT_BINDINGS_INCOMPLETE", ["product.query_execution_service", "product.runtime_resource_control", "product.managed_warehouse_experience", "product.managed_lakehouse_experience"], [], "Products exist; exact acceleration, cache, federation and browser/local execution contracts remain library/provider work."),
    ("H11", "Runtime, Deployment & Provider Control", "STRONG", "PRODUCT_CLUSTER", "COVERED", ["product.runtime_resource_control", "product.platform_estate_tenancy_administration", "product.solution_compiler"], [], "Runtime resources, estate tenancy and compile/reconcile planning have different authority."),
    ("H12", "Analytical Intent & Compilation", "CORE", "PRODUCT", "COVERED", ["product.solution_compiler"], [], "The retained compiler kernel owns bounded intent-to-solution closure, not all authoring or runtime behavior."),
    ("H13", "Exploration & Ad-hoc Analysis Workspace", "MISSING", "PRODUCT", "SPLIT_CANDIDATE", ["product.bi_reporting"], ["product.interactive_analytics_exploration"], "Independent exploration lifecycle passes the ten-axis split test; canonical migration and ratification remain pending."),
    ("H14", "Notebook & Computational Document", "MISSING", "PRODUCT", "COVERED", ["product.analytical_notebook"], [], "The incoming missing claim is false; Shannon retains a reproducible analytical notebook product."),
    ("H15", "Descriptive & Statistical Analytics", "MACHINES_ONLY", "METHOD_AND_LIBRARY_FAMILY", "DO_NOT_PROMOTE_AS_ONE_PRODUCT", ["product.semantic_metric_formula_service", "product.bi_reporting"], [], "Descriptive methods compose into many products; a method taxonomy is not an operated lifecycle."),
    ("H16", "Diagnostic & Root-Cause Analytics", "MACHINES_ONLY", "METHOD_AND_LIBRARY_FAMILY", "PRODUCT_TESTS_BY_OPERATED_JOB", ["product.signal_condition_diagnostics", "product.process_mining_workbench"], [], "RCA kernels are shared; condition diagnostics and process/case conformance are already distinct operated products."),
    ("H17", "Temporal & Forecast Analytics", "MACHINES_ONLY", "PRODUCT_CLUSTER", "COVERED", ["product.forecasting_workbench", "product.signal_condition_diagnostics"], [], "Forecast lifecycle and signal/change diagnostics have retained owners."),
    ("H18", "Causal & Experimentation Platform", "ANALYSIS_ONLY", "PRODUCT", "COVERED", ["product.experimentation_platform"], [], "The incoming analysis-only claim is false; hypothesis/assignment/exposure/analysis are modeled as a product lifecycle."),
    ("H19", "Simulation & Scenario Analytics", "MACHINE_ONLY", "PRODUCT", "COVERED", ["product.simulation_environment"], [], "A retained simulation environment already owns model, run and scenario evidence."),
    ("H20", "Optimization & Operations Research", "MACHINE_ONLY", "PRODUCT_AND_METHOD_FAMILY", "COVERED", ["product.optimization_solver"], [], "Solver operation is a product; OR formulations and algorithms remain reusable method libraries."),
    ("H21", "Process, Case & Task Intelligence", "MACHINERY", "PRODUCT_CLUSTER", "COVERED_WITH_CASE_BOUNDARY_RESEARCH", ["product.process_mining_workbench", "product.reconciliation_control_operations"], [], "Process mining is retained; generic case/task intelligence must be tested against adjudication, reconciliation and domain cases rather than assumed."),
    ("H22", "Graph & Network Analytics", "PRIMITIVE_ONLY", "PRODUCT", "COVERED", ["product.graph_analysis_workbench"], [], "The incoming primitive-only claim is false; Shannon retains a graph/network workbench."),
    ("H23", "Geospatial & Spatiotemporal Analytics", "PARTIAL", "PRODUCT", "COVERED_BUT_LIBRARY_DEPTH_OPEN", ["product.geospatial_workbench"], [], "The product boundary exists; raster, trajectory, CRS, topology and geo-time conformance remain library-depth work."),
    ("H24", "Risk, Uncertainty & Statistical Decision Science", "FRAGMENTED", "METHOD_FAMILY_AND_DOMAIN_PRODUCTS", "DO_NOT_COLLAPSE", ["product.model_assurance", "product.simulation_environment", "product.decision_automation"], [], "Uncertainty/risk methods are shared; operated enterprise risk/control is a separate candidate elsewhere, not a generic math workbench by default."),
    ("H25", "ML & Predictive Modeling", "MISSING", "PRODUCT_CLUSTER", "COVERED", ["product.feature_platform", "product.model_lifecycle", "product.model_assurance", "product.online_inference"], [], "The incoming major-missing claim is false; features, lifecycle, assurance and serving have separate retained owners."),
    ("H26", "Text, Document, Search & Multimodal Analytics", "MISSING", "PRODUCT_CLUSTER", "COVERED_WITH_METHOD_GAPS", ["product.document_processing_review", "product.image_analysis_workbench", "product.search_index_service", "product.signal_condition_diagnostics"], [], "This label wrongly collapses documents, images, search and signal/audio concerns; products exist while method/library coverage remains uneven."),
    ("H27", "Conversational & Agentic Analytics", "EXCLUDED", "OPTIONAL_EXTENSION_AND_EXPERIENCE", "COVERED_AS_NON_AUTHORITATIVE_EXTENSION", ["product.optional_model_extension"], [], "It is not excluded: Shannon permits removable model/agent extensions while deterministic typing, authority and evidence remain mandatory."),
    ("H28", "Visual Analytics & Presentation Grammar", "UNDERMODELED", "SHARED_SEMANTIC_LIBRARY_FAMILY", "ACTIVE_LIBRARY_RESEARCH", ["product.bi_reporting", "product.embedded_analytics"], [], "Presentation grammar is cross-product semantic infrastructure; it should not automatically become one user-facing product."),
    ("H29", "Interactive Analytical State", "MISSING", "SHARED_LIBRARY_WITH_PRODUCT_OWNER", "SPLIT_CANDIDATE", ["product.bi_reporting"], ["product.interactive_analytics_exploration"], "Selection, filter, drill, parameter and bookmark state require exact libraries under an exploration owner."),
    ("H30", "Dashboard, Monitoring & Scorecard Experience", "PARTIAL", "PRODUCT_BOUNDARY_HYPOTHESIS", "ADJUDICATE_DASHBOARD_VS_SCORECARD_VS_MONITORING", ["product.bi_reporting", "product.signal_condition_diagnostics"], ["product.interactive_analytics_exploration"], "Dashboard composition is supported; scorecard/goals and operational monitoring may have distinct authority and lifecycle and remain open."),
    ("H31", "Reporting, Narrative & Analytical Publishing", "MISSING", "PRODUCT_AND_LIBRARY_CLUSTER", "SPLIT_CANDIDATE", ["product.bi_reporting"], ["product.formal_reporting_publication"], "Formal reporting passes the product split test; narrative/story grammar may remain shared or require a later boundary test."),
    ("H32", "Analytical Applications & Embedded Analytics", "INCOMPLETE", "PRODUCT", "COVERED_BUT_COMPOSITION_DEPTH_OPEN", ["product.embedded_analytics"], [], "The retained embedded delivery product exists; form/workflow/data-app semantics must be imported rather than silently owned."),
    ("H33", "Analytical Content Management & Collaboration", "MISSING", "PRODUCT_BOUNDARY_HYPOTHESIS", "GENUINE_RESEARCH_VACANCY", ["product.data_product_publication"], [], "Workbook/report/notebook ownership, folders, versions, comments, review and publication need a cross-artifact boundary test; data-product publication is not a valid substitute."),
    ("H34", "Subscriptions, Alerts & Insight Delivery", "COLLAPSED", "PRODUCT_BOUNDARY_HYPOTHESIS", "GENUINE_RESEARCH_VACANCY", ["product.bi_reporting"], [], "Alert rule/occurrence, subscription, digest, escalation, transport and acknowledgment must be decomposed and independently adjudicated."),
    ("H35", "Planning, Scenario Management & Writeback", "MISSING", "PRODUCT", "COVERED", ["product.integrated_planning_workbench"], [], "The incoming major-missing claim is false; planning is retained, with writeback contracts still requiring exact authority seams."),
    ("H36", "Investigation, Workflow & Decision Operations", "PARTIAL", "PRODUCT_CLUSTER", "COVERED_WITH_GENERIC_CASE_TEST_OPEN", ["product.decision_automation", "product.reconciliation_control_operations", "product.document_processing_review", "product.annotation_operations"], [], "Several operated lifecycles exist; a generic investigation/case owner needs proof across unrelated domains before promotion."),
    ("H37", "Activation, Automation & Outcome Feedback", "PARTIAL", "PRODUCT_CLUSTER", "COVERED_WITH_EFFECTIVENESS_GAP", ["product.operational_activation", "product.decision_automation"], [], "Activation and decision execution exist; outcome, regret and effectiveness evidence need stronger exact contracts."),
    ("H38", "Trust, Assurance & Analytics Operations", "STRONG", "CROSS_CUTTING_CONSTITUTION_AND_PRODUCT_CLUSTER", "COVERED_DO_NOT_COLLAPSE", ["product.data_use_policy", "product.lineage_provenance", "product.data_quality_operations", "product.model_assurance", "product.assurance_case_appraisal", "product.finops_allocation", "product.data_protection_recovery"], [], "Trust/operations is a constitutional plane plus several authority-separated products, never one omnibus product."),
]


FRONTIER_CROSSWALK = [
    {
        "frontier_id": ident,
        "record_kind": "external_horizontal_frontier_crosswalk",
        "name": name,
        "incoming_status_claim": incoming_status,
        "adjudicated_ontology_level": level,
        "disposition": disposition,
        "retained_product_refs": retained,
        "candidate_product_refs": candidates,
        "bounded_finding": finding,
        "ratification": "WITHHELD" if candidates else "NOT_APPLICABLE_TO_COVERAGE_CROSSWALK",
        "completion_claim": False,
    }
    for ident, name, incoming_status, level, disposition, retained, candidates, finding in ROWS
]


FRONTIER_LAWS = [
    {"law_id": "law.frontier.method-product", "record_kind": "frontier_noncollapse_law", "law": "analytical_method_family != operated_product", "consequence": "A method becomes a library/kernel unless independent actors, lifecycle, adoption, authority, operations and exit prove a product."},
    {"law_id": "law.frontier.cluster-product", "record_kind": "frontier_noncollapse_law", "law": "product_cluster != bounded_context", "consequence": "A convenient market category cannot merge products with different consistency or authority boundaries."},
    {"law_id": "law.frontier.ir-product", "record_kind": "frontier_noncollapse_law", "law": "shared_intermediate_representation != product", "consequence": "Experience, interaction and presentation IRs may be shared by several products without owning their lifecycle."},
    {"law_id": "law.frontier.machine-product", "record_kind": "frontier_noncollapse_law", "law": "machine_or_library != product", "consequence": "Implementation capability does not prove an adopted operated job or sovereign product question."},
    {"law_id": "law.frontier.optional-authority", "record_kind": "frontier_noncollapse_law", "law": "generated_analysis != typed_validated_authorized_effect", "consequence": "LLM/agent removal must leave deterministic semantic, validation, authority, execution and evidence paths intact."},
]
