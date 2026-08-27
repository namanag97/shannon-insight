#!/usr/bin/env python3
"""Deterministically build the global product-boundary research corpus.

This is research, not a product-count generator.  It deliberately keeps semantic
contexts, libraries, providers, capabilities, products, suites, and solution packs
as separate identities.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from functools import lru_cache
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
EDITION = 1
AS_OF = "2026-08-26"

LAKEHOUSE_ADJUDICATION_SUBJECTS = {
    "candidate.product.lakehouse_experience": "product.managed_lakehouse_experience",
    "candidate.product.catalog_commit": "product.catalog_service",
    "candidate.product.managed_table_maintenance": "product.managed_table_maintenance",
    "candidate.product.data_sharing": "product.data_sharing_exchange",
}

MOVEMENT_ADJUDICATION_SUBJECTS = {
    "candidate.product.source_connectivity_control": "product.source_connectivity_control",
    "candidate.product.source_replication_cdc": "product.source_replication_cdc",
    "candidate.product.ingestion_delivery": "product.ingestion_delivery",
    "candidate.product.pipeline_orchestration": "product.pipeline_orchestration",
    "candidate.product.dataflow_execution": "product.dataflow_execution",
    "candidate.product.batch_transform_build": "product.batch_transform_build",
    "candidate.product.event_streaming": "product.event_streaming",
    "candidate.product.operational_activation": "product.operational_activation",
    "candidate.product.connector_brand_sku": "provider.connector_runtime",
}

GOVERNANCE_ADJUDICATION_SUBJECTS = {
    "candidate.product.metadata_discovery": "product.metadata_discovery",
    "candidate.product.business_glossary": "product.business_glossary",
    "candidate.product.ontology_knowledge_model": "product.ontology_knowledge_model",
    "candidate.product.schema_registry": "product.schema_registry",
    "candidate.product.data_contract_registry": "product.data_contract_registry",
    "candidate.product.master_data_governance": "product.master_data_governance",
    "candidate.product.reference_data_governance": "product.reference_data_governance",
    "candidate.product.lineage_provenance": "product.lineage_provenance",
    "candidate.product.data_quality_operations": "product.data_quality_operations",
    "candidate.product.reconciliation_control_operations": "product.reconciliation_control_operations",
    "candidate.product.data_use_policy": "product.data_use_policy",
    "candidate.product.data_product_publication": "product.data_product_publication",
    "candidate.product.data_marketplace": "product.data_marketplace",
}

ANALYTICAL_METHOD_ADJUDICATION_SUBJECTS = {
    "candidate.product.experimentation_platform": "product.experimentation_platform",
    "candidate.product.forecasting_workbench": "product.forecasting_workbench",
    "candidate.product.optimization_solver": "product.optimization_solver",
    "candidate.product.process_mining_workbench": "product.process_mining_workbench",
    "candidate.product.geospatial_workbench": "product.geospatial_workbench",
    "candidate.product.graph_analysis_workbench": "product.graph_analysis_workbench",
    "candidate.product.simulation_environment": "product.simulation_environment",
    "candidate.product.integrated_planning_workbench": "product.integrated_planning_workbench",
    "candidate.product.project_portfolio_controls": "product.project_portfolio_controls",
}

CONSUMPTION_ADJUDICATION_SUBJECTS = {
    "candidate.product.bi_reporting": "product.bi_reporting",
    "candidate.product.embedded_analytics": "product.embedded_analytics",
    "candidate.product.analytical_notebook": "product.analytical_notebook",
    "candidate.product.visualization_runtime": "standard.vega",
    "candidate.product.dashboard_widget": "artifact.dashboard_widget",
    "candidate.product.alert_subscription": "semantic.subscription",
    "candidate.product.spreadsheet_governance": "semantic.spreadsheet_governance",
}

PLATFORM_ADJUDICATION_SUBJECTS = {
    "candidate.product.solution_compiler": "product.solution_compiler",
    "candidate.product.data_product_developer_platform": "product.data_product_developer_platform",
    "candidate.product.runtime_resource_control": "product.runtime_resource_control",
    "candidate.product.finops_allocation": "product.finops_allocation",
    "candidate.product.provider_qualification_broker": "component.provider_qualification",
    "candidate.product.platform_operations": "pattern.platform_operations",
}

MODEL_DECISION_ADJUDICATION_SUBJECTS = {
    "candidate.product.model_lifecycle": "product.model_lifecycle",
    "candidate.product.feature_platform": "product.feature_platform",
    "candidate.product.online_inference": "product.online_inference",
    "candidate.product.model_assurance": "product.model_assurance",
    "candidate.product.decision_automation": "product.decision_automation",
    "candidate.product.optional_model_extension": "product.optional_model_extension",
    "candidate.product.vector_feature_serving": "pattern.model_decision_stack",
}

QUERY_WAREHOUSE_SEARCH_PROTECTION_SUBJECTS = {
    "candidate.product.distributed_query": "product.query_execution_service",
    "candidate.product.warehouse_experience": "product.managed_warehouse_experience",
    "candidate.product.federated_query": "capability.federated_query_execution",
    "candidate.product.virtual_data_access": "product.virtual_data_access",
    "candidate.product.search_index_serving": "product.search_index_service",
    "candidate.product.backup_restore_archive": "pattern.backup_restore_archive",
    "candidate.product.data_protection_recovery": "product.data_protection_recovery",
    "candidate.product.digital_preservation_archive": "product.digital_preservation_archive",
}

SEMANTIC_METRIC_FORMULA_SUBJECTS = {
    "candidate.product.semantic_metric": "product.semantic_metric_formula_service",
    "candidate.product.metric_store_bundle": "pattern.metric_store_query_bundle",
}

COLLABORATION_PRIVACY_RESOLUTION_ASSURANCE_SUBJECTS = {
    "candidate.product.clean_room": "product.controlled_data_collaboration",
    "candidate.product.privacy_rights_retention": "product.privacy_rights_retention",
    "candidate.product.entity_resolution": "product.entity_resolution",
    "candidate.product.independent_assurance": "product.assurance_case_appraisal",
    "candidate.product.all_governance_bundle": "suite.unified_data_governance",
}

REPRESENTATION_CODEC_SUBJECTS = {
    "candidate.product.codec_service": "pattern.codec_as_service",
}

ANALYTICAL_OPERATIONS_SUBJECTS = {
    "candidate.product.self_service_data_preparation": "product.self_service_data_preparation",
    "candidate.product.annotation_operations": "product.annotation_operations",
    "candidate.product.dataset_curation_workbench": "product.dataset_curation_workbench",
    "candidate.product.document_processing_review": "product.document_processing_review",
    "candidate.product.image_analysis_workbench": "product.image_analysis_workbench",
    "candidate.product.visual_inspection_operations": "product.visual_inspection_operations",
    "candidate.product.signal_condition_diagnostics": "product.signal_condition_diagnostics",
}


@lru_cache(maxsize=1)
def lakehouse_adjudication_decisions() -> dict[str, dict[str, Any]]:
    path = ROOT / "research/product_ontology/adjudications/lakehouse/source.json"
    source = json.loads(path.read_text(encoding="utf-8"))
    return {row["subject_ref"]: row for row in source["boundary_decisions"]}


@lru_cache(maxsize=1)
def movement_adjudication_decisions() -> dict[str, dict[str, Any]]:
    path = ROOT / "research/product_ontology/adjudications/movement/source.json"
    source = json.loads(path.read_text(encoding="utf-8"))
    return {row["subject_ref"]: row for row in source["boundary_decisions"]}


@lru_cache(maxsize=1)
def governance_adjudication_decisions() -> dict[str, dict[str, Any]]:
    path = ROOT / "research/product_ontology/adjudications/governance_semantics/source.json"
    source = json.loads(path.read_text(encoding="utf-8"))
    return {row["subject_ref"]: row for row in source["boundary_decisions"]}


@lru_cache(maxsize=1)
def analytical_method_adjudication_decisions() -> dict[str, dict[str, Any]]:
    path = ROOT / "research/product_ontology/adjudications/analytical_methods/source.json"
    source = json.loads(path.read_text(encoding="utf-8"))
    return {row["subject_ref"]: row for row in source["boundary_decisions"]}


@lru_cache(maxsize=1)
def consumption_adjudication_decisions() -> dict[str, dict[str, Any]]:
    path = ROOT / "research/product_ontology/adjudications/consumption_experiences/source.json"
    source = json.loads(path.read_text(encoding="utf-8"))
    return {row["subject_ref"]: row for row in source["boundary_decisions"]}


@lru_cache(maxsize=1)
def platform_adjudication_decisions() -> dict[str, dict[str, Any]]:
    path = ROOT / "research/product_ontology/adjudications/platform_control/source.json"
    source = json.loads(path.read_text(encoding="utf-8"))
    return {row["subject_ref"]: row for row in source["boundary_decisions"]}


@lru_cache(maxsize=1)
def model_decision_adjudication_decisions() -> dict[str, dict[str, Any]]:
    path = ROOT / "research/product_ontology/adjudications/model_decision_serving/source.json"
    source = json.loads(path.read_text(encoding="utf-8"))
    return {row["subject_ref"]: row for row in source["boundary_decisions"]}


@lru_cache(maxsize=1)
def query_warehouse_search_protection_decisions() -> dict[str, dict[str, Any]]:
    path = ROOT / "research/product_ontology/adjudications/query_warehouse_search_protection/source.json"
    source = json.loads(path.read_text(encoding="utf-8"))
    return {row["subject_ref"]: row for row in source["boundary_decisions"]}


@lru_cache(maxsize=1)
def semantic_metric_formula_decisions() -> dict[str, dict[str, Any]]:
    path = ROOT / "research/product_ontology/adjudications/semantic_metrics_formulas/source.json"
    source = json.loads(path.read_text(encoding="utf-8"))
    return {row["subject_ref"]: row for row in source["boundary_decisions"]}


@lru_cache(maxsize=1)
def collaboration_privacy_resolution_assurance_decisions() -> dict[str, dict[str, Any]]:
    path = ROOT / "research/product_ontology/adjudications/collaboration_privacy_resolution_assurance/source.json"
    source = json.loads(path.read_text(encoding="utf-8"))
    return {row["subject_ref"]: row for row in source["boundary_decisions"]}


@lru_cache(maxsize=1)
def representation_codec_decisions() -> dict[str, dict[str, Any]]:
    path = ROOT / "research/product_ontology/adjudications/representation_codec_boundary/source.json"
    source = json.loads(path.read_text(encoding="utf-8"))
    return {row["subject_ref"]: row for row in source["boundary_decisions"]}


@lru_cache(maxsize=1)
def analytical_operations_decisions() -> dict[str, dict[str, Any]]:
    path = ROOT / "research/product_ontology/adjudications/analytical_operations/source.json"
    source = json.loads(path.read_text(encoding="utf-8"))
    return {row["subject_ref"]: row for row in source["boundary_decisions"]}


def slug(value: str) -> str:
    return "_".join("".join(c.lower() if c.isalnum() else " " for c in value).split())


def record_id(prefix: str, value: str) -> str:
    return f"{prefix}.{slug(value)}"


def c(
    ident: str,
    name: str,
    family: str,
    kind: str,
    users: list[str],
    job: str,
    outcome: str,
    meanings: list[str],
    verdict: str,
    traits: list[str],
    sources: list[str],
) -> dict[str, Any]:
    return {
        "candidate_id": f"candidate.product.{ident}",
        "name": name,
        "family": family,
        "archetype_kind": kind,
        "users": users,
        "job": job,
        "outcome": outcome,
        "owned_meanings": meanings,
        "boundary_verdict": verdict,
        "traits": traits,
        "evidence_ids": sources,
    }


CANDIDATES = [
    c("solution_compiler", "Intent-to-Solution Compiler", "platform", "control_plane_product", ["enterprise_architect", "solution_engineer"], "compile declared analytical intent into a closed deployable solution", "a reproducible solution plan or typed refusal", ["intent_ir", "binding_decision", "compiler_gap", "release_evidence"], "presumptive_product", ["operated", "stateful", "authority", "effectful"], ["source.cncf.platform", "source.kubernetes.controller", "source.iso.15288"]),
    c("data_product_developer_platform", "Data Product Developer Platform", "platform", "internal_platform_product", ["data_product_team", "platform_engineer"], "build and operate governed data products through paved paths", "independently deployable data products with conformance evidence", ["data_product_blueprint", "paved_path", "platform_conformance"], "strong_product", ["operated", "stateful", "human_ui", "data", "authority"], ["source.fowler.data_product_design", "source.fowler.data_mesh", "source.cncf.platform"]),
    c("source_connectivity_control", "Source Connectivity Control Plane", "movement", "control_plane_product", ["integration_engineer", "source_owner"], "declare, qualify, deploy and revoke source connections", "portable connection declarations and health evidence", ["connection_declaration", "connector_binding", "source_occurrence_health"], "presumptive_product", ["operated", "stateful", "authority", "data", "effectful"], ["source.openapi", "source.asyncapi", "source.debezium.docs"]),
    c("ingestion_delivery", "Managed Ingestion and Delivery Service", "movement", "control_plane_product", ["data_platform_operator", "source_owner"], "configure and operate source-to-table delivery across independently replaceable connectors and table contracts", "bounded delivery state, recoverable runs and source-to-table receipts", ["ingestion_declaration", "delivery_cursor", "delivery_run", "source_to_table_receipt"], "strong_product", ["operated", "stateful", "authority", "data", "effectful"], ["source.onehouse.ingestion", "source.hudi.spec"]),
    c("operational_activation", "Operational Data Activation Service", "movement", "control_plane_product", ["data_activation_operator", "application_owner"], "map governed analytical results into authorized operational destination effects", "recoverable destination writes with exact matching, purpose authority and effect receipts", ["destination_mapping", "record_match", "activation_effect_intent", "destination_receipt"], "strong_product", ["operated", "stateful", "authority", "data", "effectful"], ["source.hightouch.sync", "source.openapi"]),
    c("pipeline_orchestration", "Pipeline Orchestration Control Plane", "movement", "control_plane_product", ["data_engineer", "operations_engineer"], "schedule and coordinate repeatable data work without owning task semantics", "recoverable workflow runs with explicit state and evidence", ["workflow_definition", "workflow_run", "task_attempt", "backfill"], "strong_product", ["operated", "stateful", "authority", "effectful"], ["source.airflow.docs", "source.dagster.assets", "source.kubernetes.controller"]),
    c("dataflow_execution", "Stateful Dataflow Execution Engine", "movement", "engine_product", ["pipeline_compiler", "data_engineer"], "execute typed batch and streaming graphs under delivery and recovery contracts", "bounded reproducible dataflow outcomes", ["dataflow_plan", "checkpoint", "delivery_receipt", "watermark"], "strong_product", ["operated", "stateful", "data", "effectful"], ["source.flink.checkpoints", "source.beam.model", "source.kafka.protocol"]),
    c("batch_transform_build", "Batch Transformation Build Engine", "movement", "engine_product", ["analytics_engineer", "build_system"], "compile and execute versioned transformations over exact input cuts", "reproducible materializations and build receipts", ["transformation_build", "input_cut_binding", "materialization_receipt"], "presumptive_product", ["operated", "stateful", "data"], ["source.dbt.build", "source.substrait", "source.slsa"]),
    c("event_streaming", "Event Streaming Platform", "movement", "provider_product", ["application_team", "data_engineer"], "publish and consume ordered durable event streams", "bounded delivery, replay and retention guarantees", ["topic", "partition", "offset", "consumer_group"], "strong_product", ["operated", "stateful", "data", "effectful"], ["source.kafka.protocol", "source.cloudevents", "source.flink.checkpoints"]),
    c("runtime_resource_control", "Analytical Runtime Resource Control Plane", "platform", "control_plane_product", ["platform_operator", "workload_owner"], "admit, place and govern finite analytical workloads", "isolated feasible executions with resource receipts", ["resource_demand", "resource_offer", "admission", "placement", "usage_receipt"], "strong_product", ["operated", "stateful", "authority", "effectful"], ["source.kubernetes.api", "source.kubernetes.controller", "source.finops.framework"]),
    c("provider_qualification_broker", "Provider Qualification Broker", "platform", "internal_platform_product", ["compiler", "platform_architect"], "qualify provider offers against declared requirements and fresh evidence", "defensible provider bindings or residual gaps", ["provider_offer", "qualification_receipt", "binding_evidence"], "defer", ["operated", "stateful", "authority"], ["source.oci.distribution", "source.slsa", "source.iso.25010"]),
    c("platform_operations", "Platform Observability and Incident Operations", "platform", "internal_platform_product", ["service_owner", "incident_responder"], "observe product health and coordinate incident recovery", "actionable signals, incidents and recovery evidence", ["service_health", "incident_case", "recovery_evidence"], "presumptive_product", ["operated", "stateful", "human_ui", "effectful"], ["source.opentelemetry.spec", "source.google.sre.slo", "source.prometheus.openmetrics"]),
    c("managed_table_maintenance", "Managed Analytical Table Maintenance", "persistence", "control_plane_product", ["data_platform_operator", "table_owner"], "operate retention-safe compaction, clustering, statistics and cleanup independently of readers and writers", "bounded physical optimization with logical-equivalence and destructive-effect receipts", ["maintenance_plan", "logical_equivalence", "rewrite_receipt", "retention_cut"], "strong_product", ["operated", "stateful", "authority", "data", "effectful"], ["source.hudi.clustering", "source.onehouse.optimizer"]),
    c("catalog_commit", "Catalog and Commit Authority", "persistence", "control_plane_product", ["query_engine", "write_engine", "catalog_operator"], "resolve names and authorize current metadata transitions", "portable discovery and fenced commits", ["catalog", "namespace", "registration", "current_metadata_reference"], "strong_product", ["operated", "stateful", "authority", "data", "effectful"], ["source.iceberg.rest", "source.polaris.docs", "source.nessie.docs"]),
    c("lakehouse_experience", "Managed Lakehouse Experience", "persistence", "experience_product", ["data_platform_team", "data_engineer"], "provision and operate an interoperable lakehouse experience", "a usable environment whose table, catalog and engine parts remain replaceable", ["lakehouse_environment", "supported_component_profile"], "presumptive_product", ["operated", "stateful", "human_ui", "data", "authority"], ["source.iceberg.spec", "source.iceberg.rest", "source.databricks.uniform"]),
    c("warehouse_experience", "Managed Analytical Warehouse Experience", "persistence", "experience_product", ["analytics_team", "warehouse_administrator"], "operate governed elastic SQL analytics", "supported SQL warehouse service with portable exits", ["warehouse_environment", "workload_profile", "warehouse_readiness"], "presumptive_product", ["operated", "stateful", "human_ui", "data", "authority"], ["source.bigquery.export", "source.snowflake.unload", "source.redshift.datashare"]),
    c("distributed_query", "Distributed Analytical Query Engine", "compute", "engine_product", ["analyst", "application", "semantic_compiler"], "execute bounded analytical queries across distributed data", "correct cancellable results with plan evidence", ["logical_query", "physical_plan", "query_run", "result_stream"], "strong_product", ["operated", "data"], ["source.trino.docs", "source.substrait", "source.arrow.flight_sql"]),
    c("federated_query", "Federated Query Engine", "compute", "engine_product", ["analyst", "data_virtualization_team"], "query multiple autonomous sources without materializing ownership centrally", "typed cross-source results with translation losses exposed", ["federated_plan", "pushdown", "source_translation", "federated_result"], "presumptive_product", ["operated", "data"], ["source.bigquery.federation", "source.trino.docs", "source.arrow.adbc"]),
    c("virtual_data_access", "Virtual Data Access", "serving", "control_plane_product", ["data_virtualization_team", "application_developer"], "publish and operate governed virtual relations over autonomous sources", "versioned virtual relations, source bindings, materialization policy and access receipts", ["virtual_relation", "virtual_relation_edition", "source_binding_set", "virtual_access_receipt"], "presumptive_product", ["operated", "stateful", "data", "authority"], ["source.denodo.views", "source.denodo.cache", "source.postgres.fdw"]),
    c("search_index_serving", "Search and Index Serving", "serving", "provider_product", ["application_developer", "analyst"], "serve indexed retrieval with declared freshness and ranking contracts", "bounded relevant retrieval with staleness evidence", ["search_index", "index_cut", "ranking_profile", "search_result"], "presumptive_product", ["operated", "stateful", "data"], ["source.opensearch.docs", "source.elasticsearch.snapshot", "source.iso.25010"]),
    c("vector_feature_serving", "Vector and Feature Serving", "serving", "provider_product", ["model_service", "application_developer"], "serve versioned features and vectors at online latency", "point-in-time-correct feature values with freshness evidence", ["feature_view", "vector_index", "online_feature_cut"], "defer", ["operated", "stateful", "data", "model"], ["source.feast.docs", "source.opensearch.docs", "source.mlflow.registry"]),
    c("backup_restore_archive", "Backup, Restore and Archive Service", "persistence", "provider_product", ["service_owner", "records_manager"], "protect state and prove restoration and archival disposition", "tested recovery within declared RPO/RTO and retention", ["recovery_point", "backup_set", "restore_test", "archive_disposition"], "strong_product", ["operated", "stateful", "data", "authority", "effectful"], ["source.iso.22301", "source.nist.800_53", "source.kubernetes.operator"]),
    c("data_protection_recovery", "Data Protection and Recovery", "persistence", "control_plane_product", ["service_owner", "recovery_operator"], "protect exact state scopes and prove recoverability against tested objectives", "verified backup chains, safe restore plans and accepted recovery evidence", ["protection_scope", "consistency_cut", "backup_chain", "recovery_objective", "recovery_acceptance"], "strong_product", ["operated", "stateful", "data", "authority", "effectful"], ["source.nist.contingency", "source.pgbackrest", "source.velero.restore"]),
    c("digital_preservation_archive", "Digital Preservation Archive", "persistence", "provider_product", ["archivist", "records_manager", "designated_community"], "preserve usable information packages across technology and organizational change", "fixity, representation, custody, access and disposition evidence for a designated community", ["information_package", "representation_information", "preservation_event", "custody_transfer", "access_copy"], "strong_product", ["operated", "stateful", "human_ui", "data", "authority", "effectful"], ["source.iso.oais", "source.premis.v3", "source.loc.sustainability"]),
    c("data_sharing", "Data Sharing Exchange", "governance", "market_product", ["data_provider", "data_consumer", "data_steward"], "publish and consume governed exact data cuts across organizational boundaries", "revocable accountable disclosure", ["share", "subscription", "disclosure_receipt", "revocation"], "strong_product", ["operated", "stateful", "data", "authority", "effectful"], ["source.delta.sharing", "source.redshift.datashare", "source.w3c.odrl"]),
    c("clean_room", "Controlled Data Collaboration", "governance", "market_product", ["collaboration_owner", "privacy_officer", "analyst"], "compute jointly authorized analyses without releasing raw participant data", "policy-bounded aggregate results and disclosure evidence", ["collaboration", "participant_policy", "approved_analysis", "release_review"], "strong_product", ["operated", "stateful", "data", "authority", "security", "effectful"], ["source.nist.privacy", "source.w3c.odrl", "source.nist.800_207"]),
    c("source_replication_cdc", "Source Replication and CDC Engine", "movement", "engine_product", ["integration_engineer", "data_platform"], "capture and replay source changes with explicit ordering and cut semantics", "reconstructable change stream and delivery evidence", ["source_cursor", "change_event", "snapshot_change_stitch", "delivery_receipt"], "strong_product", ["operated", "stateful", "data", "effectful"], ["source.debezium.docs", "source.kafka.protocol", "source.cloudevents"]),
    c("metadata_discovery", "Metadata Discovery Catalog", "governance", "experience_product", ["data_consumer", "data_steward"], "find and understand governed assets without acquiring their authority", "discoverable assets with source-attributed metadata", ["catalog_projection", "discovery_document", "usage_signal"], "presumptive_product", ["operated", "stateful", "human_ui", "data"], ["source.datahub.docs", "source.openmetadata.docs", "source.w3c.dcat"]),
    c("business_glossary", "Business Glossary Service", "governance", "internal_platform_product", ["semantic_owner", "data_steward", "analyst"], "govern business terms, labels, homonyms and explicit mappings", "versioned human language with owner-approved translations", ["business_term", "localized_label", "homonym_scope", "term_mapping"], "strong_product", ["operated", "stateful", "human_ui", "data", "authority"], ["source.w3c.skos", "source.datahub.docs", "source.w3c.dcat"]),
    c("ontology_knowledge_model", "Ontology and Knowledge-Model Service", "governance", "internal_platform_product", ["knowledge_modeler", "semantic_engineer", "compiler"], "govern formal concepts, relations, axioms, inference profiles and graph constraints", "versioned formal knowledge models with scoped entailment and validation", ["ontology_edition", "axiom", "inference_profile", "shape_profile"], "strong_product", ["operated", "stateful", "data", "authority"], ["source.w3c.owl", "source.w3c.shacl", "source.w3c.rdf11"]),
    c("master_data_governance", "Master Data Governance", "governance", "control_plane_product", ["master_data_owner", "domain_steward", "source_owner", "application_consumer"], "govern authority-scoped master identities, source authority, survivorship projections and stewardship lifecycles", "traceable mastered identities and field-provenanced projection editions with explicit residual conflicts", ["master_domain", "master_entity_identity", "source_record_authority", "survivorship_projection", "stewardship_case"], "strong_product", ["operated", "stateful", "human_ui", "data", "authority", "effectful"], ["source.iso.8000", "source.w3c.prov", "source.gleif.cdf"]),
    c("reference_data_governance", "Reference Data Governance", "governance", "control_plane_product", ["reference_data_manager", "code_system_maintainer", "terminology_steward", "application_owner"], "govern reference schemes, set and code editions, designations, replacements and directional crosswalks", "authority-bound reference releases with historically resolvable lifecycle and explicit mapping loss", ["reference_scheme", "reference_set_edition", "code_lifecycle", "designation", "crosswalk_edition"], "strong_product", ["operated", "stateful", "human_ui", "data", "authority", "effectful"], ["source.gs1.standard", "source.w3c.skos", "source.hl7.fhir"]),
    c("schema_registry", "Schema Registry", "governance", "control_plane_product", ["data_producer", "data_consumer", "runtime"], "register exact schema subjects and adjudicate declared reader-writer compatibility", "versioned schemas with explicit compatibility verdicts", ["schema_subject", "schema_edition", "serialization_profile", "compatibility_verdict"], "strong_product", ["operated", "stateful", "data", "authority"], ["source.confluent.schema_compatibility", "source.opendatacontract", "source.asyncapi"]),
    c("data_contract_registry", "Data Contract Registry", "governance", "control_plane_product", ["data_producer", "data_consumer", "compiler"], "publish and adjudicate provider-consumer data promises and acceptance", "resolvable contracts and prevented unaccepted change", ["data_contract", "contract_edition", "acceptance_criterion", "service_promise"], "strong_product", ["operated", "stateful", "data", "authority"], ["source.opendatacontract", "source.opendataproduct", "source.asyncapi"]),
    c("data_use_policy", "Data Access, Purpose and Disclosure Policy", "governance", "control_plane_product", ["data_steward", "security_operator", "runtime"], "decide whether a principal may perform an exact data use", "least-privilege decisions, obligations, refusals and revocations", ["data_use_request", "purpose_scope", "policy_decision", "policy_obligation"], "strong_product", ["operated", "stateful", "data", "authority", "security"], ["source.nist.800_207", "source.oasis.xacml", "source.opa.docs"]),
    c("privacy_rights_retention", "Privacy Rights and Retention Control", "governance", "control_plane_product", ["privacy_officer", "records_manager", "data_subject_operations"], "coordinate retention, hold, access, erasure and disclosure cases", "evidence-bearing lawful dispositions across products", ["privacy_case", "retention_schedule", "legal_hold", "erasure_receipt"], "strong_product", ["operated", "stateful", "human_ui", "data", "authority", "security", "effectful"], ["source.nist.privacy", "source.w3c.dpv", "source.iso.27701"]),
    c("lineage_provenance", "Lineage and Provenance Evidence", "assurance", "internal_platform_product", ["data_engineer", "auditor", "incident_responder"], "trace exact derivations, activities and agents", "portable source-to-result evidence", ["provenance_entity", "activity", "agent", "derivation"], "strong_product", ["operated", "stateful", "data"], ["source.openlineage", "source.w3c.prov", "source.opentelemetry.spec"]),
    c("data_quality_operations", "Data Quality Operations", "assurance", "internal_platform_product", ["data_quality_engineer", "data_owner", "data_steward", "data_product_operator", "consumer_reviewer"], "define purpose-scoped quality requirements, evaluate exact data cuts and govern defect, quarantine, waiver and remediation lifecycles", "cut-bound observations, adjudicated defects and bounded fitness evidence", ["quality_programme", "validation_run", "quality_case", "quarantine_lot", "fitness_verdict"], "strong_product", ["operated", "stateful", "human_ui", "data", "authority", "effectful"], ["source.greatexpectations.docs", "source.soda.contracts", "source.iso.25012"]),
    c("reconciliation_control_operations", "Reconciliation and Control Operations", "assurance", "internal_platform_product", ["reconciliation_analyst", "operations_controller", "finance_or_control_owner", "exception_investigator", "auditor"], "define and execute exact or tolerant comparisons over identified populations and truth roles, investigate material breaks and govern bounded control completion", "matched and residual populations, a material break ledger and evidence-bound control completion", ["reconciliation_definition", "reconciliation_run", "reconciliation_break", "correction_proposal", "control_completion"], "strong_product", ["operated", "stateful", "human_ui", "data", "authority", "effectful"], ["source.bcbs.239", "source.xbrl.formula", "source.data_diff.docs"]),
    c("independent_assurance", "Independent Evidence and Assurance", "assurance", "market_product", ["assurance_reviewer", "risk_owner", "auditor"], "appraise claims without owning the claims or their implementation", "signed bounded verdicts with defeaters and residual gaps", ["assurance_case", "appraisal", "defeater", "bounded_verdict"], "presumptive_product", ["operated", "stateful", "human_ui", "authority"], ["source.iso.25010", "source.nist.800_53a", "source.slsa"]),
    c("finops_allocation", "Usage, Cost and FinOps Allocation", "platform", "internal_platform_product", ["product_owner", "finance_partner", "platform_operator"], "attribute finite resource consumption to products and consumers", "explainable allocation, budgets and unit economics", ["usage_meter", "allocation_rule", "budget", "unit_cost"], "strong_product", ["operated", "stateful", "data", "authority"], ["source.finops.framework", "source.opentelemetry.spec", "source.google.sre.slo"]),
    c("data_product_publication", "Data Product Publication Control Plane", "governance", "control_plane_product", ["domain_data_product_owner", "consumer"], "publish, supersede, recall and retire governed data products", "addressable exact publications with lifecycle and SLO evidence", ["data_product", "publication_edition", "contract_binding", "recall"], "strong_product", ["operated", "stateful", "data", "authority", "effectful"], ["source.fowler.data_product_design", "source.opendataproduct", "source.w3c.dcat"]),
    c("entity_resolution", "Entity Resolution and Identity Mapping Engine", "governance", "engine_product", ["data_steward", "pipeline_compiler"], "propose and adjudicate cross-source identity links", "explainable links, non-links, merges and reversals", ["identity_candidate", "link_hypothesis", "match_decision", "merge_split"], "presumptive_product", ["operated", "stateful", "data", "authority", "model"], ["source.nist.800_63", "source.w3c.prov", "source.iso.8000"]),
    c("semantic_metric", "Semantic Metric and Formula Service", "semantics", "engine_product", ["metric_author", "analyst", "application"], "publish governed metric/formula editions and evaluate them consistently across grains, dimensions, time, units and providers", "provider-neutral semantic queries, values-or-errors and exact observation receipts", ["formula_definition", "metric_definition", "measure", "dimension", "grain", "population", "semantic_query", "metric_observation"], "strong_product", ["operated", "stateful", "data", "authority"], ["source.dbt.semantic", "source.cube.semantic", "source.substrait"]),
    c("bi_reporting", "Business Intelligence and Reporting Experience", "consumption", "experience_product", ["business_user", "analyst", "report_author"], "explore, author and distribute governed analytical views", "accessible decisions and recurring reports with traceable cuts", ["report", "dashboard", "exploration_session", "distribution"], "strong_product", ["operated", "stateful", "human_ui", "data"], ["source.powerbi.docs", "source.tableau.docs", "source.superset.docs"]),
    c("visualization_runtime", "Visualization Rendering Runtime", "consumption", "engine_product", ["application_developer", "reporting_experience"], "render declarative visual specifications across clients", "consistent accessible visual output", ["visual_spec", "render_plan", "interaction_event"], "defer", ["human_ui", "data"], ["source.vegalite.docs", "source.w3c.wcag", "source.superset.docs"]),
    c("embedded_analytics", "Embedded Analytics Delivery", "consumption", "market_product", ["application_developer", "product_manager"], "embed governed analytics into operational applications", "tenant-safe contextual analytics with supported SDKs", ["embed_contract", "host_context", "tenant_session"], "presumptive_product", ["operated", "stateful", "human_ui", "data", "security"], ["source.powerbi.embedded", "source.tableau.embedded", "source.openapi"]),
    c("analytical_notebook", "Reproducible Analytical Notebook", "consumption", "experience_product", ["data_scientist", "analyst", "researcher"], "combine code, narrative, data cuts and evidence reproducibly", "rerunnable governed studies and publications", ["notebook", "cell_run", "environment_lock", "publication"], "presumptive_product", ["operated", "stateful", "human_ui", "data", "model"], ["source.jupyter.docs", "source.oci.image", "source.slsa"]),
    c("spreadsheet_governance", "Spreadsheet Analytics Governance", "consumption", "experience_product", ["business_analyst", "controller", "auditor"], "govern spreadsheet formulas, links, approvals and publication", "traceable spreadsheet decisions without pretending spreadsheets are databases", ["workbook_edition", "formula_graph", "external_link", "approval"], "defer", ["operated", "stateful", "human_ui", "data", "authority"], ["source.oasis.openformula", "source.w3c.prov", "source.iso.25010"]),
    c("alert_subscription", "Analytical Alert and Subscription Delivery", "consumption", "shared_service", ["business_user", "operations_user"], "deliver thresholded analytical notifications with acknowledgment", "timely deduplicated notification and receipt", ["subscription", "alert", "delivery_attempt", "acknowledgment"], "merge", ["operated", "stateful", "human_ui", "effectful"], ["source.cloudevents", "source.asyncapi", "source.google.sre.slo"]),
    c("data_marketplace", "Data Marketplace Experience", "consumption", "experience_product", ["data_consumer", "data_provider", "procurement"], "discover, evaluate and request fulfillment of data-product offers", "transparent selection and governed fulfillment handoff", ["market_listing", "commercial_offer", "eligibility", "subscription_request"], "presumptive_product", ["operated", "stateful", "human_ui", "data", "commercial"], ["source.opendataproduct", "source.w3c.dcat", "source.w3c.odrl"]),
    c("experimentation_platform", "Experimentation Control and Analysis Platform", "methods", "control_plane_product", ["experimenter", "product_analyst", "decision_scientist"], "govern assignment, exposure, metric cuts and versioned experiment conclusions while importing causal methods", "replayable experiments and assumption-bounded effect evidence", ["experiment", "assignment", "exposure", "analysis_edition", "conclusion"], "strong_product", ["operated", "stateful", "human_ui", "data", "authority"], ["source.growthbook.docs", "source.dowhy.docs", "source.nist.handbook"]),
    c("forecasting_workbench", "Forecasting Workbench and Service", "methods", "experience_product", ["planner", "forecaster", "data_scientist"], "govern forecast origins, horizons, backtests, distributions, overrides and publication", "calibrated versioned forecasts with review and revision evidence", ["forecast_project", "forecast_origin", "horizon", "forecast_distribution", "override"], "strong_product", ["operated", "stateful", "human_ui", "data", "model"], ["source.forecastpro.docs", "source.sktime.docs", "source.statsmodels.docs"]),
    c("integrated_planning_workbench", "Integrated Planning Workbench and Service", "methods", "experience_product", ["planning_process_owner", "functional_planner", "finance_partner", "resource_owner", "decision_authority"], "coordinate editioned scenarios and plan alternatives through feasibility, cross-functional reconciliation, review, approval, publication and replanning", "an approved and traceable operating-plan edition or typed residual conflict without absorbing forecast, method, authority or execution ownership", ["plan_definition", "planning_cycle", "scenario_assumption_cut", "plan_alternative", "reconciliation_case", "approval_decision", "plan_publication", "replan_case"], "strong_product", ["operated", "stateful", "human_ui", "data", "authority", "effectful"], ["source.planning.ascm.dictionary", "source.planning.sap.versions_scenarios", "source.planning.oracle.manage_plans", "source.planning.pigment.versions_scenarios"]),
    c("project_portfolio_controls", "Project & Portfolio Controls", "control", "control_plane_product", ["project_controls_manager", "project_manager", "programme_manager", "portfolio_owner", "control_account_manager", "change_control_board", "sponsor"], "operate an authorized delivery baseline and govern status, performance measurement, completion forecast, change, rebaselining, rollup and period close", "traceable controlled performance and change state against an immutable authorized baseline without absorbing planning, finance, contract, analytics or execution authority", ["control_system_edition", "authorized_baseline_edition", "control_account", "status_cut", "performance_measurement", "completion_forecast", "change_control_case", "baseline_revision", "portfolio_rollup", "control_period_close"], "strong_product", ["operated", "stateful", "human_ui", "data", "authority", "effectful"], ["source.project_controls.iso21508", "source.project_controls.gao_schedule", "source.project_controls.doe_evms", "source.project_controls.oracle_unifier"]),
    c("optimization_solver", "Optimization Solver Engine", "methods", "engine_product", ["operations_researcher", "planner", "application_developer"], "solve exact bounded mathematical programs without exercising business authority", "typed solve status, solution, bounds, gaps or infeasibility evidence", ["optimization_model", "solver_profile", "solve_attempt", "solution_status", "certificate"], "strong_product", ["operated", "data", "model"], ["source.gurobi.docs", "source.ortools.docs", "source.scipy.optimize"]),
    c("process_mining_workbench", "Process and Object-Centric Mining Workbench", "methods", "experience_product", ["process_owner", "auditor", "analyst"], "govern source-attributed process projections, discovery, conformance and performance analyses", "evidence-linked models, deviations and bottleneck findings", ["process_project", "log_occurrence", "process_model", "conformance_result", "finding"], "strong_product", ["operated", "stateful", "human_ui", "data", "model"], ["source.pmtk.docs", "source.ocel.spec", "source.pm4py.docs"]),
    c("geospatial_workbench", "Geospatial Analysis Workbench", "methods", "experience_product", ["geospatial_analyst", "application_developer"], "govern spatial projects, CRS-aware workflows, histories and analytical outputs", "reproducible spatial results retaining CRS, support and accuracy", ["spatial_project", "layer_occurrence", "crs_binding", "workflow", "spatial_result"], "strong_product", ["operated", "stateful", "human_ui", "data", "model"], ["source.qgis.docs", "source.ogc.api.features", "source.postgis.docs"]),
    c("graph_analysis_workbench", "Graph and Network Analysis Workbench", "methods", "experience_product", ["graph_analyst", "network_researcher", "data_scientist", "assurance_reviewer"], "govern graph-analysis workspaces, exact graph occurrence/profile bindings, algorithm plans, runs, comparisons, evidence, publication and exit", "reproducible bounded graph results without acquiring ontology, identity, causal, decision or effect authority", ["graph_workspace", "graph_occurrence_binding", "algorithm_plan", "graph_run", "graph_result", "result_comparison", "graph_publication"], "strong_product", ["operated", "stateful", "human_ui", "data", "model"], ["source.gephi.srs", "source.cytoscape.manual", "source.neo4j.gds", "source.graphalytics.spec"]),
    c("model_lifecycle", "Predictive Model Engineering and Lifecycle", "models", "control_plane_product", ["model_owner", "ml_engineer", "data_scientist"], "govern experiments, training specifications, fitted artifacts, model editions, promotion and retirement", "reproducible model editions with explicit lifecycle authority and exit evidence", ["experiment_run", "training_spec", "fitted_artifact", "model_edition", "model_lifecycle_state"], "strong_product", ["operated", "stateful", "human_ui", "data", "model", "authority", "effectful"], ["source.mlflow.registry", "source.nist.ai_rmf", "source.kubeflow.pipelines"]),
    c("feature_platform", "Feature Definition and Serving Platform", "models", "control_plane_product", ["feature_owner", "data_scientist", "model_service"], "govern feature definitions, point-in-time retrieval, materialization and online reads", "time-correct reusable feature values with freshness and exit evidence", ["feature_definition", "feature_service", "historical_feature_cut", "feature_materialization", "online_feature_read"], "strong_product", ["operated", "stateful", "human_ui", "data", "model"], ["source.feast.docs", "source.nist.ai_rmf"]),
    c("online_inference", "Predictive Inference Serving", "models", "provider_product", ["application", "model_owner"], "serve approved predictive model editions under revision, rollout, latency and resource contracts", "version-pinned predictions and inference receipts", ["inference_deployment", "inference_request", "prediction", "inference_receipt"], "strong_product", ["operated", "stateful", "data", "model", "effectful"], ["source.kserve.docs", "source.openinference.spec", "source.opentelemetry.spec"]),
    c("model_assurance", "Predictive Model Evaluation and Monitoring", "models", "assurance_product", ["model_risk_reviewer", "model_owner", "ml_engineer"], "evaluate, validate, monitor and investigate predictive model behavior without self-approving deployment", "scoped evaluation, drift and review evidence with explicit uncertainty", ["evaluation_plan", "evaluation_result", "model_validation", "model_monitor", "drift_finding", "model_review_case"], "strong_product", ["operated", "stateful", "human_ui", "data", "model"], ["source.nist.ai_rmf", "source.evidently.docs", "source.mlflow.evaluation"]),
    c("decision_automation", "Decision Modeling and Execution", "decisioning", "control_plane_product", ["business_analyst", "decision_owner", "application_developer"], "author, version, execute and audit deterministic decision services without exercising downstream effects", "portable decision models and traceable results or typed refusals", ["decision_model", "decision_table", "decision_service", "decision_invocation", "decision_result"], "strong_product", ["operated", "stateful", "human_ui", "data", "authority"], ["source.omg.dmn", "source.kie.dmn", "source.opa.docs"]),
    c("optional_model_extension", "Optional Model and Agent Extension Runtime", "extension", "provider_product", ["application_developer", "solution_compiler", "risk_owner"], "invoke an explicitly requested model/agent stage that produces typed proposals under budgets and fallback", "typed generated claims, plans or tool proposals that remain non-authoritative", ["extension_task", "extension_invocation", "generated_proposal"], "presumptive_product", ["operated", "stateful", "data", "model", "security", "effectful"], ["source.mcp.spec", "source.a2a.spec", "source.nist.ai_rmf"]),
    c("simulation_environment", "Simulation Modeling and Experiment Environment", "methods", "experience_product", ["simulation_modeler", "decision_scientist", "planner"], "govern model editions, scenarios, experiments, seeds, replications, calibration and sensitivity", "reproducible simulation distributions and sensitivity evidence", ["simulation_model", "scenario", "experiment", "replication_plan", "simulation_distribution"], "strong_product", ["operated", "stateful", "human_ui", "data", "model"], ["source.anylogic.docs", "source.fmi.spec", "source.simpy.docs"]),
    c("self_service_data_preparation", "Self-Service Data Preparation Workbench", "preparation", "experience_product", ["data_practitioner", "analyst", "data_steward"], "inspect, repair and reshape one admitted data cut through a reviewable reversible recipe without mutating its source", "a reproducible preparation recipe, reviewed data diff and portable prepared-output edition", ["preparation_project", "admitted_data_cut", "profile_view", "facet_selection", "transformation_recipe", "recipe_history", "prepared_output_edition"], "strong_product", ["operated", "stateful", "human_ui", "data", "authority"], ["source.openrefine.docs"]),
    c("annotation_operations", "Annotation and Ground-Truth Operations", "analytical_operations", "control_plane_product", ["annotation_owner", "annotator", "reviewer", "dataset_steward"], "turn selected source occurrences into a versioned, reviewed and quality-evidenced annotation dataset", "traceable annotation occurrences, measured review quality and a recallable ground-truth edition", ["annotation_project", "annotation_schema", "target_selector", "annotation_task", "annotation_occurrence", "review_issue", "agreement_measurement", "consensus_record", "ground_truth_edition"], "strong_product", ["operated", "stateful", "human_ui", "data", "authority", "effectful"], ["source.cvat.qa", "source.w3c.annotation"]),
    c("dataset_curation_workbench", "Dataset Curation Workbench", "analytical_operations", "control_plane_product", ["dataset_steward", "data_scientist", "research_data_manager", "benchmark_owner", "assurance_reviewer"], "turn admitted source occurrences into a purpose-bound, evidence-bearing, immutable and maintainable dataset edition", "reproducible membership and split decisions, explicit leakage/rights/documentation evidence, and a recallable dataset release", ["dataset_definition", "membership_decision", "curation_recipe", "duplicate_case", "partition_plan", "dataset_audit", "dataset_edition", "dataset_release"], "strong_product", ["operated", "stateful", "human_ui", "data", "authority", "effectful"], ["source.dataset_curation.datasheets", "source.dataset_curation.croissant", "source.dataset_curation.fiftyone_versioning", "source.w3c.dcat"]),
    c("document_processing_review", "Document Processing and Review Operations", "analytical_operations", "control_plane_product", ["document_operator", "reviewer", "integration_owner", "records_steward"], "convert one admitted document occurrence into typed provenance-linked structured output with exceptions and review", "bounded processing, provenance-linked extraction, reviewed exceptions and reprocessable structured output", ["document_occurrence", "carrier_detection", "page_revision", "content_graph", "extraction_candidate", "review_exception", "structured_output_edition"], "strong_product", ["operated", "stateful", "human_ui", "data", "authority", "effectful"], ["source.apache.tika", "source.google.documentai"]),
    c("image_analysis_workbench", "Image Analysis Workbench", "analytical_operations", "experience_product", ["image_analyst", "scientist", "research_engineer", "pathology_analyst", "materials_analyst", "assurance_reviewer"], "turn admitted image occurrences into reproducible inspectable and publishable analytical result evidence without acquiring vertical decision authority", "a purpose-bound project, typed workspace, reproducible recipe, evidence-bearing results, reviewable comparisons and verifiable publication", ["analysis_project", "image_input_cut", "layer_graph", "region_object_graph", "analysis_recipe", "analysis_run", "result_set", "review_case", "evidence_publication"], "strong_product", ["operated", "stateful", "human_ui", "data", "model", "authority"], ["source.image_analysis.cellprofiler", "source.image_analysis.qupath", "source.image_analysis.napari", "source.ome.model"]),
    c("visual_inspection_operations", "Visual Inspection Operations", "analytical_operations", "control_plane_product", ["inspection_engineer", "quality_operator", "reviewer", "line_integration_owner"], "configure, qualify, execute and review repeatable image-based inspections while preserving item, recipe, result and disposition boundaries", "a repeatable inspection recipe, traceable item results, reviewable abstention and controlled effect proposals", ["inspection_plan", "acquisition_profile", "calibration_edition", "inspection_recipe", "inspection_occurrence", "method_result", "inspection_result", "review_disposition"], "strong_product", ["operated", "stateful", "human_ui", "data", "authority", "effectful"], ["source.mvtec.merlic", "source.iso.14997.2", "source.genicam.standard"]),
    c("signal_condition_diagnostics", "Signal Condition Monitoring and Diagnostics", "analytical_operations", "control_plane_product", ["reliability_engineer", "condition_monitoring_specialist", "maintenance_planner", "operations_reviewer"], "operate an editioned monitoring programme that turns admitted signals into state, health, diagnosis and prognosis evidence", "traceable condition indicators, challengeable diagnosis, calibrated prognosis and reviewed advisory evidence", ["monitoring_programme", "asset_channel_binding", "sampling_profile", "calibration_edition", "condition_indicator", "detected_state", "health_assessment", "diagnostic_case", "prognostic_case", "advisory"], "strong_product", ["operated", "stateful", "human_ui", "data", "model", "authority"], ["source.iso.17359", "source.mimosa.osacbm", "source.scipy.signal"]),
    c("dashboard_widget", "Dashboard Widget", "consumption", "module", ["dashboard_author"], "place one visualization in a dashboard", "one rendered tile", ["widget_configuration"], "merge", ["human_ui", "data"], ["source.vegalite.docs"]),
    c("connector_brand_sku", "Vendor Connector SKU", "movement", "module", ["integration_engineer"], "connect one named vendor endpoint", "one adapter binding", ["adapter_configuration"], "merge", ["operated", "data", "effectful"], ["source.openapi"]),
    c("codec_service", "Codec-as-a-Service", "representation", "shared_service", ["runtime"], "encode or decode one carrier", "transformed bytes", ["codec_invocation"], "merge", ["data"], ["source.arrow.format"]),
    c("metric_store_bundle", "Metric Store plus Query Bundle", "semantics", "suite", ["analytics_team"], "buy metrics and physical query together", "one packaged analytics path", ["bundle_configuration"], "defer", ["operated", "stateful", "data"], ["source.dbt.semantic", "source.trino.docs"]),
    c("all_governance_bundle", "Unified Data Governance Product", "governance", "suite", ["chief_data_officer"], "buy all governance concerns as one SKU", "one administrative console", ["suite_entitlement"], "merge", ["operated", "stateful", "human_ui", "data", "authority"], ["source.datahub.docs", "source.openmetadata.docs"]),
]


SOURCE_SPECS = [
    ("source.iso.15288", "ISO/IEC/IEEE 15288:2023", "ISO", "standard", "https://www.iso.org/standard/81702.html", "Covers conception, development, production, utilization, support and retirement across system life cycles."),
    ("source.iso.12207", "ISO/IEC/IEEE 12207:2017", "ISO", "standard", "https://www.iso.org/standard/63712.html", "Defines software life-cycle processes, including supply, operation, maintenance and disposal."),
    ("source.iso.20000", "ISO/IEC 20000-1:2018", "ISO", "standard", "https://www.iso.org/standard/70636.html", "Requires planning, design, transition, delivery, monitoring and improvement of managed services."),
    ("source.iso.25010", "ISO/IEC 25010:2023", "ISO", "standard", "https://www.iso.org/standard/78176.html", "Provides a product-quality model for specifying and evaluating ICT product quality."),
    ("source.iso.25012", "ISO/IEC 25012:2008", "ISO", "standard", "https://www.iso.org/standard/35736.html", "Defines a general data quality model."),
    ("source.bcbs.239", "Principles for effective risk data aggregation and risk reporting", "Basel Committee on Banking Supervision", "supervisory_standard", "https://www.bis.org/publ/bcbs239.htm", "Requires accuracy, integrity, completeness, timeliness and adaptable risk-data aggregation with reconciliation to sources."),
    ("source.xbrl.formula", "XBRL Formula 1.0", "XBRL International", "open_standard", "https://specifications.xbrl.org/work-product-index-formula-formula-1.0.html", "Defines assertions, variables, filters and consistency checks for XBRL facts."),
    ("source.data_diff.docs", "data-diff", "Datafold", "official_product_docs", "https://github.com/datafold/data-diff", "Documents cross-database row comparison and keyed difference workflows."),
    ("source.iso.27001", "ISO/IEC 27001:2022", "ISO", "standard", "https://www.iso.org/standard/27001", "Defines requirements for an information security management system."),
    ("source.iso.27701", "ISO/IEC 27701", "ISO", "standard", "https://www.iso.org/standard/85819.html", "Extends management-system obligations for privacy information management."),
    ("source.iso.22301", "ISO 22301:2019", "ISO", "standard", "https://www.iso.org/standard/75106.html", "Defines business-continuity management requirements relevant to recovery promises."),
    ("source.iso.8000", "ISO 8000 data quality series", "ISO", "standard", "https://www.iso.org/committee/54158/x/catalogue/", "Defines authoritative data-quality and master-data concepts."),
    ("source.gleif.cdf", "GLEIF Level 1 LEI Common Data File 3.1", "GLEIF", "official_specification", "https://www.gleif.org/en/lei-data/access-and-use-lei-data/level-1-data-lei-cdf-3-1-format", "Defines authority-bound reporting, identity, reference-data fields, state transitions and validation for Legal Entity Identifier records; it is a domain instance, not universal master-data semantics."),
    ("source.iso.19115", "ISO 19115-1:2014", "ISO", "standard", "https://www.iso.org/standard/53798.html", "Defines metadata for geographic information and services."),
    ("source.nist.800_53", "NIST SP 800-53 Rev. 5", "NIST", "government_standard", "https://csrc.nist.gov/pubs/sp/800/53/r5/upd1/final", "Catalogs security, privacy, continuity, incident and supply-chain controls."),
    ("source.nist.800_53a", "NIST SP 800-53A Rev. 5", "NIST", "government_standard", "https://csrc.nist.gov/pubs/sp/800/53/a/r5/final", "Defines procedures for independently assessing security and privacy controls."),
    ("source.nist.800_63", "NIST SP 800-63-4", "NIST", "government_standard", "https://pages.nist.gov/800-63-4/", "Defines digital identity proofing, authentication and federation assurance."),
    ("source.nist.800_207", "NIST SP 800-207", "NIST", "government_standard", "https://csrc.nist.gov/pubs/sp/800/207/final", "Defines zero-trust architecture and policy decision/enforcement separation."),
    ("source.nist.privacy", "NIST Privacy Framework 1.0", "NIST", "government_framework", "https://www.nist.gov/privacy-framework", "Provides a risk-based framework for identifying and managing privacy risk."),
    ("source.nist.ai_rmf", "NIST AI RMF 1.0", "NIST", "government_framework", "https://www.nist.gov/itl/ai-risk-management-framework", "Defines govern, map, measure and manage functions for predictive-model risk."),
    ("source.nist.handbook", "NIST/SEMATECH e-Handbook of Statistical Methods", "NIST", "government_reference", "https://www.itl.nist.gov/div898/handbook/", "Authoritative implementation reference for statistical methods and diagnostics."),
    ("source.openapi", "OpenAPI Specification", "OpenAPI Initiative", "open_standard", "https://spec.openapis.org/oas/latest.html", "Defines language-neutral HTTP API descriptions and operation contracts."),
    ("source.asyncapi", "AsyncAPI Specification", "AsyncAPI Initiative", "open_standard", "https://www.asyncapi.com/docs/reference/specification/latest", "Defines event-driven API channels, messages, operations and bindings."),
    ("source.cloudevents", "CloudEvents Specification", "CNCF", "open_standard", "https://github.com/cloudevents/spec/blob/main/cloudevents/spec.md", "Defines interoperable event envelope metadata."),
    ("source.oci.distribution", "OCI Distribution Specification", "Open Container Initiative", "open_standard", "https://github.com/opencontainers/distribution-spec/blob/main/spec.md", "Defines portable content discovery, upload, download and deletion behavior."),
    ("source.oci.image", "OCI Image Format Specification", "Open Container Initiative", "open_standard", "https://github.com/opencontainers/image-spec/blob/main/spec.md", "Defines portable content-addressed image manifests and configurations."),
    ("source.slsa", "SLSA v1.0", "OpenSSF", "open_standard", "https://slsa.dev/spec/v1.0/", "Defines supply-chain provenance levels and verifiable build evidence."),
    ("source.kubernetes.api", "Kubernetes API conventions", "Kubernetes", "official_project", "https://github.com/kubernetes/community/blob/master/contributors/devel/sig-architecture/api-conventions.md", "Separates desired spec, observed status, identity, versions and operations."),
    ("source.kubernetes.controller", "Kubernetes controllers", "Kubernetes", "official_project", "https://kubernetes.io/docs/concepts/architecture/controller/", "Defines reconciliation of desired and observed state through control loops."),
    ("source.kubernetes.operator", "Kubernetes operator pattern", "Kubernetes", "official_project", "https://kubernetes.io/docs/concepts/extend-kubernetes/operator/", "Shows lifecycle automation including deploy, backup, restore and upgrade."),
    ("source.cncf.platform", "CNCF Platform Engineering White Paper", "CNCF", "industry_framework", "https://tag-app-delivery.cncf.io/whitepapers/platforms/", "Frames platforms as curated self-service capabilities treated as products for internal users."),
    ("source.opentelemetry.spec", "OpenTelemetry specifications", "CNCF OpenTelemetry", "open_standard", "https://opentelemetry.io/docs/specs/", "Defines interoperable traces, metrics, logs and telemetry transport."),
    ("source.prometheus.openmetrics", "OpenMetrics Specification", "CNCF", "open_standard", "https://github.com/prometheus/OpenMetrics/blob/main/specification/OpenMetrics.md", "Defines interoperable metric exposition and metadata."),
    ("source.google.sre.slo", "Implementing SLOs", "Google SRE", "authoritative_practice", "https://sre.google/workbook/implementing-slos/", "Connects user-centric SLOs and error budgets to reliability decisions."),
    ("source.finops.framework", "FinOps Framework", "FinOps Foundation", "industry_framework", "https://www.finops.org/framework/", "Defines allocation, accountability, unit economics and cloud-value practices."),
    ("source.w3c.prov", "PROV-O", "W3C", "open_standard", "https://www.w3.org/TR/prov-o/", "Defines entities, activities, agents and derivation relations for provenance."),
    ("source.w3c.dcat", "DCAT 3", "W3C", "open_standard", "https://www.w3.org/TR/vocab-dcat-3/", "Defines catalogs, datasets, distributions, data services and version relationships."),
    ("source.w3c.odrl", "ODRL Information Model 2.2", "W3C", "open_standard", "https://www.w3.org/TR/odrl-model/", "Defines policy offers, agreements, permissions, prohibitions and duties."),
    ("source.w3c.dpv", "Data Privacy Vocabulary", "W3C", "open_standard", "https://www.w3.org/TR/dpv/", "Provides interoperable terms for processing purposes, rights and measures."),
    ("source.w3c.skos", "SKOS Reference", "W3C", "open_standard", "https://www.w3.org/TR/skos-reference/", "Defines concepts, schemes, labels and mappings without conflating source schemes."),
    ("source.w3c.owl", "OWL 2 Overview", "W3C", "open_standard", "https://www.w3.org/TR/owl2-overview/", "Defines ontology constructs and entailment-oriented knowledge representation."),
    ("source.w3c.shacl", "Shapes Constraint Language", "W3C", "open_standard", "https://www.w3.org/TR/shacl/", "Separates data graphs, shapes graphs and validation reports without mutating the validated graph."),
    ("source.w3c.rdf11", "RDF 1.1 Concepts and Abstract Syntax", "W3C", "open_standard", "https://www.w3.org/TR/rdf11-concepts/", "Defines RDF graph and dataset carriers without conferring ontology authority or truth."),
    ("source.w3c.wcag", "WCAG 2.2", "W3C", "open_standard", "https://www.w3.org/TR/WCAG22/", "Defines testable accessibility success criteria for user experiences."),
    ("source.oasis.xacml", "XACML 3.0", "OASIS", "open_standard", "https://docs.oasis-open.org/xacml/3.0/xacml-3.0-core-spec-os-en.html", "Defines policy decision requests, responses, obligations and combining algorithms."),
    ("source.oasis.openformula", "OpenFormula 1.3", "OASIS", "open_standard", "https://docs.oasis-open.org/office/OpenDocument/v1.3/os/part4-formula/OpenDocument-v1.3-os-part4-formula.html", "Defines portable spreadsheet formula syntax and semantics."),
    ("source.fowler.data_mesh", "Data Mesh Principles and Logical Architecture", "Martin Fowler / Zhamak Dehghani", "authoritative_practice", "https://martinfowler.com/articles/data-mesh-principles.html", "Separates domain data products, self-service platform and computational governance."),
    ("source.fowler.data_product_design", "Designing Data Products", "Martin Fowler / Thoughtworks", "authoritative_practice", "https://martinfowler.com/articles/designing-data-products.html", "Requires a cohesive independently valuable data product with users, SLOs, interfaces and lifecycle."),
    ("source.opendataproduct", "Open Data Product Specification", "Linux Foundation / Open Data Product Initiative", "open_standard", "https://opendataproducts.org/", "Provides a machine-readable data-product metadata contract."),
    ("source.opendatacontract", "Open Data Contract Standard", "Bitol", "open_standard", "https://bitol-io.github.io/open-data-contract-standard/latest/", "Defines interoperable data contract structure, quality and service-level terms."),
    ("source.confluent.schema_compatibility", "Schema Evolution and Compatibility Types", "Confluent", "official_product_docs", "https://docs.confluent.io/platform/current/schema-registry/fundamentals/schema-evolution.html", "Defines versioned backward, forward, full and transitive schema compatibility decisions without claiming semantic contract acceptance."),
    ("source.arrow.format", "Apache Arrow Columnar Format", "Apache Arrow", "official_project", "https://arrow.apache.org/docs/format/Columnar.html", "Defines a language-independent columnar memory layout."),
    ("source.arrow.flight_sql", "Arrow Flight SQL", "Apache Arrow", "official_project", "https://arrow.apache.org/docs/format/FlightSql.html", "Defines interoperable high-performance SQL database access over Arrow Flight."),
    ("source.arrow.adbc", "Arrow Database Connectivity", "Apache Arrow", "official_project", "https://arrow.apache.org/adbc/current/format/specification.html", "Defines a cross-language database API with replaceable drivers."),
    ("source.iceberg.spec", "Apache Iceberg Table Specification", "Apache Iceberg", "official_project", "https://iceberg.apache.org/spec/", "Defines portable snapshots, manifests, schema/partition evolution and format versions."),
    ("source.iceberg.rest", "Apache Iceberg REST Catalog Specification", "Apache Iceberg", "official_project", "https://iceberg.apache.org/rest-catalog-spec/", "Defines a common catalog API across languages, engines and catalog implementations."),
    ("source.delta.protocol", "Delta Transaction Log Protocol", "Linux Foundation Delta Lake", "official_project", "https://github.com/delta-io/delta/blob/master/PROTOCOL.md", "Defines transaction-log actions, features and reader/writer compatibility."),
    ("source.delta.sharing", "Delta Sharing Protocol", "Linux Foundation Delta Lake", "open_standard", "https://github.com/delta-io/delta-sharing/blob/main/PROTOCOL.md", "Defines an open protocol for sharing data across products and organizations."),
    ("source.hudi.spec", "Apache Hudi specifications", "Apache Hudi", "official_project", "https://hudi.apache.org/learn/tech-specs/", "Defines table storage, timeline and transactional behavior for Hudi tables."),
    ("source.hudi.clustering", "Apache Hudi clustering", "Apache Hudi", "official_project", "https://hudi.apache.org/docs/clustering/", "Defines separately schedulable physical-layout rewrites and concurrency constraints for table clustering."),
    ("source.onehouse.ingestion", "Onehouse OneFlow", "Onehouse", "official_product_docs", "https://www.onehouse.ai/product/oneflow", "Documents an independently operated ingestion service spanning sources, delivery state and open table targets."),
    ("source.onehouse.optimizer", "Onehouse Table Optimizer", "Onehouse", "official_product_docs", "https://www.onehouse.ai/optimize", "Documents a separately adopted and operated managed service for compaction, clustering and cleaning."),
    ("source.hightouch.sync", "Hightouch syncs", "Hightouch", "official_product_docs", "https://hightouch.com/docs/syncs/overview", "Documents operational destination mapping, record matching, write modes, scheduling, monitoring and recovery."),
    ("source.substrait", "Substrait Specification", "Substrait", "open_standard", "https://substrait.io/spec/specification/", "Defines cross-language serialized query plans while leaving engines replaceable."),
    ("source.openlineage", "OpenLineage Specification", "OpenLineage", "open_standard", "https://openlineage.io/docs/spec/", "Defines extensible job, run and dataset lineage events."),
    ("source.polaris.docs", "Apache Polaris documentation", "Apache Polaris", "official_project", "https://polaris.apache.org/", "Implements an interoperable Iceberg REST catalog with catalog-scoped authority."),
    ("source.nessie.docs", "Project Nessie documentation", "Project Nessie", "official_project", "https://projectnessie.org/", "Implements transactional versioned catalog semantics with branches and tags."),
    ("source.databricks.uniform", "Delta UniForm", "Databricks", "official_product_docs", "https://docs.databricks.com/aws/en/delta/uniform", "Exposes Delta tables through Iceberg-compatible metadata, demonstrating format substitution pressure."),
    ("source.snowflake.unload", "Snowflake data unload", "Snowflake", "official_product_docs", "https://docs.snowflake.com/en/user-guide/data-unload-overview", "Documents export of table/query data into portable file formats."),
    ("source.bigquery.export", "BigQuery data export", "Google Cloud", "official_product_docs", "https://cloud.google.com/bigquery/docs/exporting-data", "Documents table and query export into CSV, JSON, Avro and Parquet."),
    ("source.bigquery.federation", "BigQuery federated queries", "Google Cloud", "official_product_docs", "https://cloud.google.com/bigquery/docs/federated-queries-intro", "Documents source-specific translation, limits and read-only federation."),
    ("source.redshift.datashare", "Amazon Redshift data sharing", "AWS", "official_product_docs", "https://docs.aws.amazon.com/redshift/latest/dg/lf_datashare_overview.html", "Documents cross-account sharing, permission enforcement and revocation lifecycle."),
    ("source.trino.docs", "Trino documentation", "Trino", "official_project", "https://trino.io/docs/current/", "Documents a distributed SQL engine with replaceable catalogs and connectors."),
    ("source.kafka.protocol", "Apache Kafka protocol", "Apache Kafka", "official_project", "https://kafka.apache.org/protocol", "Defines interoperable request, response, offset and version behavior for event streams."),
    ("source.flink.checkpoints", "Apache Flink checkpointing", "Apache Flink", "official_project", "https://nightlies.apache.org/flink/flink-docs-stable/docs/ops/state/checkpoints/", "Documents state checkpoints, retention and recovery for streaming jobs."),
    ("source.beam.model", "Apache Beam programming model", "Apache Beam", "official_project", "https://beam.apache.org/documentation/basics/", "Separates a portable pipeline model from runners that execute it."),
    ("source.airflow.docs", "Apache Airflow core concepts", "Apache Airflow", "official_project", "https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/", "Defines DAG, task, run, scheduling and retry concepts."),
    ("source.dagster.assets", "Dagster software-defined assets", "Dagster", "official_product_docs", "https://docs.dagster.io/guides/build/assets", "Documents asset definitions, dependencies, materializations and checks."),
    ("source.debezium.docs", "Debezium documentation", "Debezium", "official_project", "https://debezium.io/documentation/reference/stable/", "Documents snapshot and change-event capture across source systems."),
    ("source.dbt.build", "dbt build command", "dbt Labs", "official_product_docs", "https://docs.getdbt.com/reference/commands/build", "Documents selection and execution of models, tests, snapshots and seeds in dependency order."),
    ("source.dbt.semantic", "dbt Semantic Layer", "dbt Labs", "official_product_docs", "https://docs.getdbt.com/docs/use-dbt-semantic-layer/dbt-sl", "Documents governed metric definitions and query interfaces separated from physical warehouses."),
    ("source.cube.semantic", "Cube semantic layer", "Cube", "official_product_docs", "https://cube.dev/docs/product/data-modeling/", "Documents measures, dimensions, joins and pre-aggregations over multiple data sources."),
    ("source.datahub.docs", "DataHub architecture", "DataHub", "official_project", "https://docs.datahub.com/docs/architecture/architecture", "Documents metadata ingestion, graph, search and serving components."),
    ("source.openmetadata.docs", "OpenMetadata documentation", "OpenMetadata", "official_project", "https://docs.open-metadata.org/latest/main-concepts/metadata-standard", "Documents a metadata standard and catalog services across heterogeneous systems."),
    ("source.greatexpectations.docs", "Great Expectations expectations", "Great Expectations", "official_product_docs", "https://docs.greatexpectations.io/docs/core/define_expectations/", "Documents declarative data assertions and validation results."),
    ("source.soda.contracts", "Soda data contracts", "Soda", "official_product_docs", "https://docs.soda.io/soda/data-contracts.html", "Documents schema and quality checks bound to data contracts."),
    ("source.opa.docs", "Open Policy Agent documentation", "CNCF OPA", "official_project", "https://www.openpolicyagent.org/docs/latest/", "Documents policy decision as a separable service/library with explicit inputs."),
    ("source.opensearch.docs", "OpenSearch documentation", "OpenSearch", "official_project", "https://docs.opensearch.org/latest/", "Documents distributed search, vector search, indexing, security and snapshot behavior."),
    ("source.elasticsearch.snapshot", "Elasticsearch snapshot and restore", "Elastic", "official_product_docs", "https://www.elastic.co/guide/en/elasticsearch/reference/current/snapshot-restore.html", "Documents cluster backup, compatibility and restore constraints."),
    ("source.feast.docs", "Feast documentation", "Feast", "official_project", "https://docs.feast.dev/", "Documents offline and online feature retrieval with point-in-time correctness."),
    ("source.mlflow.registry", "MLflow Model Registry", "MLflow", "official_project", "https://mlflow.org/docs/latest/ml/model-registry/", "Documents model versions, aliases, tags and lifecycle management."),
    ("source.kserve.docs", "KServe documentation", "KServe", "official_project", "https://kserve.github.io/website/latest/", "Documents declarative model serving, rollout and inference protocols on Kubernetes."),
    ("source.openinference.spec", "OpenInference semantic conventions", "Arize AI", "open_standard", "https://github.com/Arize-ai/openinference/tree/main/spec", "Defines telemetry conventions for model inference spans and attributes."),
    ("source.kubeflow.pipelines", "Kubeflow Pipelines runs", "Kubeflow", "official_project", "https://www.kubeflow.org/docs/components/pipelines/concepts/run/", "Defines reproducible pipeline runs, runtime graphs, artifacts and recurring-run state."),
    ("source.mlflow.evaluation", "MLflow model evaluation", "MLflow", "official_project", "https://mlflow.org/docs/latest/ml/evaluation", "Documents scoped predictive evaluation, diagnostics and threshold validation."),
    ("source.omg.dmn", "Decision Model and Notation 1.5", "Object Management Group", "open_standard", "https://www.omg.org/spec/DMN/1.5/", "Defines decision requirements, logic, FEEL, decision services and normative interchange artifacts."),
    ("source.kie.dmn", "Apache KIE DMN", "Apache KIE", "official_project", "https://kie.apache.org/docs/components/drools/drools_dmn/", "Documents an executable DMN engine, decision graphs, tables, analysis and conformance posture."),
    ("source.mcp.spec", "Model Context Protocol 2025-06-18", "Model Context Protocol", "open_standard", "https://modelcontextprotocol.io/specification/2025-06-18", "Defines optional tool, resource, prompt and sampling interoperability without granting business authority."),
    ("source.a2a.spec", "Agent2Agent Protocol", "A2A Project", "open_standard", "https://a2a-protocol.org/latest/specification/", "Defines task, message and artifact exchange between separately operated optional agent components."),
    ("source.powerbi.docs", "Power BI documentation", "Microsoft", "official_product_docs", "https://learn.microsoft.com/power-bi/", "Documents governed reports, semantic models, sharing and administration."),
    ("source.powerbi.embedded", "Power BI embedded analytics", "Microsoft", "official_product_docs", "https://learn.microsoft.com/power-bi/developer/embedded/", "Documents embedding reports and analytics into host applications."),
    ("source.tableau.docs", "Tableau help", "Salesforce Tableau", "official_product_docs", "https://help.tableau.com/current/pro/desktop/en-us/default.htm", "Documents authoring, data connections, workbooks and publishing."),
    ("source.tableau.embedded", "Tableau Embedding API", "Salesforce Tableau", "official_product_docs", "https://help.tableau.com/current/api/embedding_api/en-us/index.html", "Defines a supported API for embedding analytical views."),
    ("source.superset.docs", "Apache Superset documentation", "Apache Superset", "official_project", "https://superset.apache.org/docs/intro", "Documents an open BI exploration, dashboard and visualization application."),
    ("source.vegalite.docs", "Vega-Lite specification", "Vega", "official_project", "https://vega.github.io/vega-lite/docs/", "Defines a declarative grammar for interactive graphics."),
    ("source.jupyter.docs", "Jupyter documentation", "Project Jupyter", "official_project", "https://docs.jupyter.org/en/latest/", "Documents open notebook documents, kernels and interactive computation."),
    ("source.scipy.stats", "SciPy statistics reference", "SciPy", "official_project", "https://docs.scipy.org/doc/scipy/reference/stats.html", "Documents statistical distributions, tests and descriptive functions."),
    ("source.scipy.optimize", "SciPy optimization reference", "SciPy", "official_project", "https://docs.scipy.org/doc/scipy/reference/optimize.html", "Documents constrained/unconstrained optimization and solver statuses."),
    ("source.scipy.signal", "SciPy signal processing reference", "SciPy", "official_project", "https://docs.scipy.org/doc/scipy/reference/signal.html", "Documents filtering, spectral analysis and signal operations."),
    ("source.openrefine.docs", "OpenRefine user manual", "OpenRefine", "official_project", "https://openrefine.org/docs/manual/starting", "Documents project admission, interactive exploration, transformations, ordered history, replay recipes and export."),
    ("source.cvat.qa", "CVAT quality assurance and analytics", "CVAT", "official_project", "https://docs.cvat.ai/docs/qa-analytics/", "Documents annotation tasks, review, correction, ground truth, quality reports and review conflicts."),
    ("source.w3c.annotation", "Web Annotation Data Model", "W3C", "open_standard", "https://www.w3.org/TR/annotation-model/", "Defines annotation, body, target, selector, motivation and provenance identities."),
    ("source.apache.tika", "Apache Tika", "Apache Software Foundation", "official_project", "https://tika.apache.org/", "Documents media detection and extraction of structured text and metadata from document carriers."),
    ("source.google.documentai", "Document AI overview", "Google Cloud", "official_product_docs", "https://docs.cloud.google.com/document-ai/docs/overview", "Documents processors, document extraction, review-oriented processing and structured document outputs."),
    ("source.mvtec.merlic", "MERLIC manual", "MVTec", "official_product_docs", "https://www.mvtec.com/doc/merlic/26.03/manual/en-us/Content/Getting_started/getting_started.html", "Documents visual-inspection recipes, tool flows, execution, result evaluation and process integration."),
    ("source.iso.14997.2", "ISO/TR 14997-2:2022", "ISO", "standard", "https://www.iso.org/standard/75056.html", "Defines visual inspection guidance for non-destructive testing."),
    ("source.genicam.standard", "GenICam Standard", "European Machine Vision Association", "open_standard", "https://www.emva.org/wp-content/uploads/GenICam_Standard_v2_0.pdf", "Defines generic camera configuration, acquisition and transport interfaces for machine vision."),
    ("source.iso.17359", "ISO 17359:2018", "ISO", "standard", "https://www.iso.org/standard/71194.html", "Provides general procedures for condition monitoring and diagnostics programmes."),
    ("source.mimosa.osacbm", "MIMOSA OSA-CBM", "MIMOSA", "open_standard", "https://www.mimosa.org/mimosa-osa-cbm/", "Defines an open condition-based maintenance information architecture from data acquisition through health assessment, prognostics and advisory generation."),
    ("source.statsmodels.docs", "statsmodels documentation", "statsmodels", "official_project", "https://www.statsmodels.org/stable/index.html", "Documents statistical models, estimation, tests and diagnostics."),
    ("source.sktime.docs", "sktime documentation", "sktime", "official_project", "https://www.sktime.net/en/stable/", "Documents a unified time-series interface for forecasting and evaluation."),
    ("source.ortools.docs", "OR-Tools documentation", "Google", "official_project", "https://developers.google.com/optimization", "Documents optimization solvers and explicit feasible/infeasible statuses."),
    ("source.growthbook.docs", "GrowthBook documentation", "GrowthBook", "official_product_docs", "https://docs.growthbook.io/", "Documents an independently operated experimentation platform over existing data and metric definitions."),
    ("source.forecastpro.docs", "Forecast Pro product documentation", "Business Forecast Systems", "official_product_docs", "https://www.forecastpro.com/products/forecast-pro/", "Documents a forecasting product with model selection, overrides, reporting and collaborative workflow."),
    ("source.planning.ascm.dictionary", "ASCM Supply Chain Dictionary", "Association for Supply Chain Management", "official_professional_standard", "https://learn.ascm.org/sfc/servlet.shepherd/document/download/069R3000006PlDHIA0?operationContext=S1", "Defines integrated business planning as a cross-functional strategic, operational and financial process that balances demand, supply and resources into an enterprise operating plan."),
    ("source.planning.sap.versions_scenarios", "Planning Versions and Scenarios", "SAP", "official_product_docs", "https://help.sap.com/docs/SAP_INTEGRATED_BUSINESS_PLANNING/09154e4f345c46edb1d74f782be4d9bd/8814a357dd6a6b10e10000000a441470.html", "Documents separate planning versions, scenarios, simulations, promotion and planning jobs."),
    ("source.planning.oracle.manage_plans", "Actions to Manage Your Plans", "Oracle", "official_product_docs", "https://docs.oracle.com/en/cloud/saas/supply-chain-and-manufacturing/26a/fasdm/actions-to-manage-your-plans.html", "Documents plan create, duplicate, compare, run, approve, archive, publish, release and status operations."),
    ("source.planning.pigment.versions_scenarios", "Versions and Scenarios", "Pigment", "official_product_docs", "https://kb.pigment.com/docs/versions-scenarios", "Distinguishes repeatable auditable planning versions from ad-hoc what-if scenarios and supports their combined use."),
    ("source.project_controls.iso21508", "ISO 21508:2026 Earned value management in project and programme management", "ISO", "international_standard", "https://www.iso.org/standard/87899.html", "Establishes cross-sector applicability of earned-value management to projects, programmes and portfolios."),
    ("source.project_controls.gao_schedule", "Schedule Assessment Guide: Best Practices for Project Schedules", "U.S. Government Accountability Office", "official_government_guidance", "https://www.gao.gov/products/gao-16-89g", "Separates schedule construction, performance baselines, status updates, risk analysis and controlled baseline changes."),
    ("source.project_controls.doe_evms", "EVMS Implementation Guidance", "U.S. Department of Energy", "official_government_guidance", "https://www.energy.gov/projectmanagement/evms-implementation-guidance", "Treats baseline, performance measurement, scheduling and change control as governed project-control processes."),
    ("source.project_controls.oracle_unifier", "Starting a Project by Using Business Processes", "Oracle Primavera Unifier", "official_product_docs", "https://docs.oracle.com/en/industries/construction-engineering/primavera-unifier/26/accelerator-user/startingaprojectbyusingbusinessprocesses-10302014a.html", "Independently persists schedules and baselines, estimates, budgets, cost sheets, cash flows, change orders and approvals."),
    ("source.dataset_curation.datasheets", "Datasheets for Datasets", "Gebru et al.", "primary_research", "https://www.microsoft.com/en-us/research/uploads/prod/2019/01/1803.09010.pdf", "Defines dataset motivation, composition, collection, preprocessing, distribution, maintenance and legal/ethical documentation questions."),
    ("source.dataset_curation.croissant", "Croissant Format Specification 1.1", "MLCommons", "open_standard", "https://docs.mlcommons.org/croissant/docs/croissant-spec-1.1.html", "Defines machine-readable datasets, record sets, files, fields, provenance, use policies and distribution metadata."),
    ("source.dataset_curation.fiftyone_versioning", "Dataset Versioning", "Voxel51", "official_product_docs", "https://docs.voxel51.com/enterprise/dataset_versioning.html", "Documents mutable dataset HEAD and immutable read-only snapshots with explicit captured and excluded state."),
    ("source.image_analysis.cellprofiler", "CellProfiler projects and pipelines", "CellProfiler", "official_product_docs", "https://cellprofiler-manual.s3.amazonaws.com/CellProfiler-4.2.8/help/pipelines_building.html", "Documents independently operated image-analysis projects, typed module pipelines, test runs, batch execution, measurements and export."),
    ("source.image_analysis.qupath", "QuPath documentation", "QuPath", "official_product_docs", "https://qupath.readthedocs.io/en/stable/", "Documents projects, images, annotations, detections, measurements, workflows, scripts and result export."),
    ("source.image_analysis.napari", "napari layers", "napari", "official_product_docs", "https://napari.org/stable/getting_started/layers.html", "Defines independently operated n-dimensional Image, Labels, Points, Shapes, Surface, Tracks and Vectors layers."),
    ("source.ome.model", "OME Data Model", "Open Microscopy Environment", "official_data_model", "https://ome-model.readthedocs.io/en/latest/", "Separates projects, datasets, images, pixels, channels, planes, instruments, ROIs and structured annotations."),
    ("source.gurobi.docs", "Gurobi Optimizer reference manual", "Gurobi Optimization", "official_product_docs", "https://docs.gurobi.com/projects/optimizer/en/current/", "Documents an independently adopted optimizer with models, environments, parameters, statuses, APIs and numerical diagnostics."),
    ("source.pmtk.docs", "Process Mining Toolkit", "Process Intelligence Solutions", "official_product_docs", "https://processintelligence.solutions/pmtk", "Documents a process-mining workbench distinct from the PM4Py implementation library."),
    ("source.qgis.docs", "QGIS processing framework", "QGIS", "official_product_docs", "https://docs.qgis.org/3.44/en/docs/user_manual/processing/intro.html", "Documents a geospatial workbench with toolbox, model designer, history and batch execution."),
    ("source.gephi.srs", "Gephi Software Requirements Specification", "Gephi Consortium", "official_product_docs", "https://gephi.org/users/gephi_srs_document.pdf", "Documents an independently adopted graph-analysis application with projects, multiple workspaces, algorithms, plugins and import/export."),
    ("source.cytoscape.manual", "Cytoscape User Manual", "Cytoscape Consortium", "official_product_docs", "https://manual.cytoscape.org/en/stable/", "Documents a separately operated network-analysis application with sessions, networks, tables, analysis, apps, sharing and export."),
    ("source.neo4j.gds", "Neo4j Graph Data Science graph management", "Neo4j", "official_product_docs", "https://neo4j.com/docs/graph-data-science/current/management-ops/", "Documents named analytical graph catalogs, projection, mutation, access control, backup/restore, write-back and export lifecycle."),
    ("source.graphalytics.spec", "LDBC Graphalytics Benchmark Specification", "Linked Data Benchmark Council", "open_standard", "https://ldbcouncil.org/ldbc_graphalytics_docs/graphalytics_spec.pdf", "Defines graph analytics workloads, datasets, validation and benchmark reporting with workload-scoped evidence."),
    ("source.anylogic.docs", "AnyLogic experiment documentation", "AnyLogic", "official_product_docs", "https://anylogic.help/anylogic/experiments/about-experiments.html", "Documents simulation, sensitivity, calibration, Monte Carlo and custom experiments in a simulation environment."),
    ("source.fmi.spec", "Functional Mock-up Interface 3.0.2", "Modelica Association Project FMI", "open_standard", "https://fmi-standard.org/docs/3.0.2/", "Defines model-exchange, co-simulation and scheduled-execution containers and interfaces."),
    ("source.simpy.docs", "SimPy documentation", "SimPy", "official_project", "https://simpy.readthedocs.io/en/latest/", "Documents a process-based discrete-event simulation framework."),
    ("source.dowhy.docs", "DoWhy documentation", "PyWhy", "official_project", "https://www.pywhy.org/dowhy/", "Structures causal questions around model, identification, estimation and refutation."),
    ("source.econml.docs", "EconML documentation", "Microsoft Research", "official_project", "https://econml.azurewebsites.net/", "Documents heterogeneous treatment-effect estimators and inference."),
    ("source.evidently.docs", "Evidently documentation", "Evidently AI", "official_product_docs", "https://docs.evidentlyai.com/", "Documents evaluation and monitoring of data and predictive model quality."),
    ("source.ocel.spec", "OCEL 2.0 specification", "Process Mining", "open_standard", "https://www.ocel-standard.org/2.0/", "Defines object-centric event-log interchange for process mining."),
    ("source.pm4py.docs", "PM4Py documentation", "Process Intelligence Solutions", "official_project", "https://processintelligence.solutions/static/api/2.7.17/", "Documents process discovery, conformance and performance analysis algorithms."),
    ("source.apache.tinkerpop", "Apache TinkerPop reference", "Apache TinkerPop", "official_project", "https://tinkerpop.apache.org/docs/current/reference/", "Defines a graph computing framework and Gremlin traversal semantics."),
    ("source.networkx.docs", "NetworkX documentation", "NetworkX", "official_project", "https://networkx.org/documentation/stable/", "Documents graph structures and algorithms with explicit graph kinds."),
    ("source.ogc.api.features", "OGC API Features", "Open Geospatial Consortium", "open_standard", "https://ogcapi.ogc.org/features/", "Defines interoperable discovery and access to geospatial features."),
    ("source.postgis.docs", "PostGIS reference", "PostGIS", "official_project", "https://postgis.net/docs/", "Documents CRS-aware spatial types, predicates and transformations."),
    ("source.lucene.docs", "Apache Lucene documentation", "Apache Lucene", "official_project", "https://lucene.apache.org/core/", "Documents non-LLM text indexing, analysis and search."),
    ("source.scikit_learn.text", "scikit-learn text feature extraction", "scikit-learn", "official_project", "https://scikit-learn.org/stable/modules/feature_extraction.html#text-feature-extraction", "Documents non-LLM bag-of-words and TF-IDF feature extraction."),
    ("source.opencv.docs", "OpenCV documentation", "OpenCV", "official_project", "https://docs.opencv.org/4.x/", "Documents classical computer-vision and image-processing algorithms."),
    ("source.trino.pushdown", "Trino pushdown", "Trino", "official_project", "https://trino.io/docs/current/optimizer/pushdown.html", "Documents connector-specific pushdown and residual local execution rather than an independent federation product."),
    ("source.postgres.fdw", "PostgreSQL foreign-data wrapper", "PostgreSQL", "official_project", "https://www.postgresql.org/docs/17/postgres-fdw.html", "Defines access and planning over remote tables without implying a cross-source atomic cut."),
    ("source.denodo.views", "Denodo virtual views", "Denodo", "official_product_docs", "https://community.denodo.com/docs/html/browse/9.5/en/vdp/administration/creating_derived_views/querying_views/querying_views", "Documents separately governed virtual relations and their access behavior."),
    ("source.denodo.cache", "Denodo cache module", "Denodo", "official_product_docs", "https://community.denodo.com/docs/html/browse/latest/en/vdp/administration/cache_module/cache_module", "Separates virtual source access from optional cache and materialization policy."),
    ("source.elastic.refresh", "Elasticsearch refresh semantics", "Elastic", "official_product_docs", "https://www.elastic.co/docs/reference/elasticsearch/rest-apis/refresh-parameter", "Separates index mutation acknowledgement from search visibility."),
    ("source.nist.contingency", "NIST SP 800-34 Rev.1", "NIST", "standard", "https://csrc.nist.gov/pubs/sp/800/34/r1/upd1/final", "Defines contingency impact analysis, recovery strategies, exercises and maintenance."),
    ("source.pgbackrest", "pgBackRest user guide", "pgBackRest", "official_project", "https://pgbackrest.org/user-guide.html", "Defines full, differential and incremental backup chains, restore, WAL and verification mechanics."),
    ("source.velero.restore", "Velero restore reference", "Velero", "official_project", "https://velero.io/docs/main/restore-reference/", "Defines restore lifecycle and validation while stopping short of service-level recovery acceptance."),
    ("source.iso.oais", "ISO 14721:2025 OAIS", "ISO", "standard", "https://www.iso.org/standard/87471.html", "Defines digital preservation for a designated community through ingest, archival storage, data management and access."),
    ("source.premis.v3", "PREMIS Data Dictionary 3.0", "Library of Congress", "open_standard", "https://www.loc.gov/standards/premis/v3/index.html", "Defines preservation Objects, Events, Rights and Agents."),
    ("source.loc.sustainability", "Sustainability of Digital Formats", "Library of Congress", "official_project", "https://www.loc.gov/preservation/digital/formats/sustain/sustain.shtml", "Defines disclosure, adoption, transparency, dependency and protection factors for long-term formats."),
    ("source.gs1.standard", "GS1 General Specifications", "GS1", "industry_standard", "https://www.gs1.org/standards/barcodes-epcrfid-id-keys/gs1-general-specifications", "Defines globally scoped identification keys and data-carrier rules."),
    ("source.hl7.fhir", "HL7 FHIR R5 ConceptMap", "HL7", "open_standard", "https://hl7.org/fhir/R5/conceptmap.html", "Defines directional concept mappings, explicit relationship kinds, contexts, unmapped handling and the law that reverse mappings cannot be assumed; it is healthcare terminology infrastructure, not a universal reference-data owner."),
]


INNOVATIONS = [
    ("arrow_flight_sql", 2022, "source.arrow.flight_sql", "Portable Arrow-native SQL RPC decouples database clients from engine-specific bulk transports."),
    ("iceberg_rest_catalog", 2022, "source.iceberg.rest", "A common catalog protocol separates table clients from catalog implementations."),
    ("substrait_plans", 2022, "source.substrait", "Serialized cross-engine query plans create a provider-removal seam below SQL text."),
    ("delta_sharing", 2021, "source.delta.sharing", "An open sharing protocol separates disclosure products from a single warehouse vendor."),
    ("openlineage_standard", 2021, "source.openlineage", "Standardized run events allow lineage backends and producers to evolve independently."),
    ("slsa_v1", 2023, "source.slsa", "Stable supply-chain provenance levels make build evidence machine-verifiable."),
    ("otel_logs_stability", 2023, "source.opentelemetry.spec", "A unified telemetry model reduces product-specific observability adapters."),
    ("ocel_2", 2024, "source.ocel.spec", "Object-centric event logs represent multiple business objects without flattening them into one case ID."),
    ("delta_uniform", 2023, "source.databricks.uniform", "Generated Iceberg metadata demonstrates table-format substitution without rewriting product semantics."),
    ("apache_polaris", 2024, "source.polaris.docs", "An open REST catalog implementation supplies concrete multi-engine catalog portability evidence."),
    ("iceberg_v3", 2025, "source.iceberg.spec", "Adopted format v3 adds new semantics behind explicit reader/writer feature negotiation."),
    ("open_data_contract", 2024, "source.opendatacontract", "A vendor-neutral contract format makes schema, quality and SLO obligations portable."),
    ("open_data_product_spec", 2023, "source.opendataproduct", "Machine-readable data-product metadata supports discovery and lifecycle automation."),
    ("kserve_serverless_inference", 2022, "source.kserve.docs", "Declarative predictive serving separates model lifecycle from runtime provider operation."),
    ("feast_point_in_time", 2021, "source.feast.docs", "Point-in-time joins make training/serving temporal correctness an explicit contract."),
    ("dbt_semantic_layer", 2023, "source.dbt.semantic", "Metric definitions and query APIs can remain portable above warehouses."),
    ("adbc_driver_manager", 2023, "source.arrow.adbc", "A cross-language driver manager creates explicit database substitution seams."),
    ("beam_portable_runner", 2021, "source.beam.model", "Portable pipelines separate logical transforms from runner implementations."),
    ("finops_focs", 2024, "source.finops.framework", "Open cost-and-usage normalization strengthens cross-provider allocation evidence."),
    ("spdx_3_supply_chain", 2024, "source.slsa", "Graph-shaped software bills of materials support richer dependency and provenance assertions."),
    ("datafusion_comet", 2024, "source.substrait", "Substrait-backed acceleration shows physical kernels can substitute beneath logical plans."),
    ("flink_disaggregated_state", 2024, "source.flink.checkpoints", "Disaggregated state work separates durable checkpoint concerns from execution slots."),
    ("opentelemetry_profiles", 2025, "source.opentelemetry.spec", "Profiles join traces, metrics and logs as another interoperable operations signal."),
    ("vector_search_open_interfaces", 2022, "source.opensearch.docs", "Vector retrieval became an ordinary declared index capability rather than an LLM-only product."),
    ("privacy_vocabulary", 2022, "source.w3c.dpv", "A standardized privacy vocabulary enables portable purpose and processing declarations."),
]


BOUNDARY_KINDS = [
    ("product", "A governed outcome promise to a defined user with independent adoption, operation, support, economic accountability, lifecycle and exit.", "All six independence gates plus semantic and authority ownership are evidenced.", "A missing exit, support owner or separable job falsifies product status."),
    ("capability", "A selectable behavior offered by one or more products.", "Referenced through requirement/offer contracts.", "A capability does not become a product because it is configurable."),
    ("module", "A code or deployment subdivision hidden behind a product contract.", "Owned and released as an implementation unit.", "No direct user outcome, support or exit promise exists."),
    ("library", "A reusable semantic or algorithmic implementation unit.", "Publishes types, traits, laws and removal seams.", "A crate/package name cannot own a product promise."),
    ("engine", "A computational component; it is a product only if independently embedded/adopted and carries lifecycle, correctness, support and exit promises.", "Run the same six gates as any product.", "Performance or algorithmic novelty alone is insufficient."),
    ("control_plane", "A desired-state, policy or reconciliation authority.", "Must expose spec/status, refusal, convergence, authority and recovery contracts.", "A controller binary without independently adopted service posture is a module."),
    ("shared_service", "An operated reusable service consumed by several products.", "May be a product only when consumers can adopt, allocate, support and exit it independently.", "Internal reach or many callers alone is insufficient."),
    ("provider", "A replaceable implementation or resource occurrence satisfying a typed offer.", "Qualification evidence is scoped by version, target, region and time.", "A vendor or infrastructure resource is not automatically the product that consumes it."),
    ("suite", "Commercial or navigational packaging over products.", "Entitlements and cross-product experience are explicit; semantic owners remain below.", "A suite never acquires all meanings of its contents."),
    ("solution_pack", "A reusable composition of products, mappings, rules, methods and acceptance tests for a class of problems.", "Compiles through typed imports and may span industries.", "It does not become a horizontal engine or re-own imported semantics."),
    ("industry_pack", "Vertical vocabulary, cases, sources, rules and authority bindings composed with horizontal products.", "Industry terms remain owned by vertical domains and are mapped through ACLs.", "Changing industry may not require changing horizontal owned meanings."),
    ("application", "A deployed user-facing composition for a bounded workflow.", "May be an experience product if adoption/support/exit are independent.", "A UI is not proof of an independent product boundary."),
    ("data_product", "A governed, addressable, independently valuable analytical publication with owner, contract, SLO, access and lifecycle.", "Exact cuts, ports, semantics, quality and exit are explicit.", "A table, topic or file without the promise is only an asset or port."),
    ("market_sku", "A price or entitlement package.", "Maps many-to-many to product identities.", "Vendor packaging is implementation evidence, never boundary authority."),
]


EXTRA_OBLIGATIONS = [
    ("adoption", "independent_install", "A consumer can provision or embed the candidate without buying unrelated outcomes.", "A mandatory unrelated suite entitlement fails the gate."),
    ("adoption", "minimum_viable_configuration", "A documented minimum configuration reaches first value.", "Hidden professional-service knowledge fails repeatable adoption."),
    ("adoption", "coexistence", "The candidate can coexist with predecessor and substitute during migration.", "Only hard cutover without evidence fails adoption safety."),
    ("adoption", "consumer_readiness", "Prerequisites, skills and organizational ownership are declared.", "Unbounded consumer-side work invalidates adoption cost."),
    ("adoption", "time_to_first_value", "Time-to-first-value has a measurement definition and target.", "A demo-only measure is not production adoption evidence."),
    ("operation", "declared_state", "Operated products publish desired and observed state separately.", "Status inferred from absence of errors is insufficient."),
    ("operation", "finite_capacity", "Requests carry finite work, memory, concurrency and data budgets.", "Unbounded scan or queue admission is refused."),
    ("operation", "cancellation", "Cancellation distinguishes not-started, safely-stopped and completion-unknown.", "Reporting success after ambiguous cancellation is prohibited."),
    ("operation", "backpressure", "Overload behavior, shedding and retry-after signals are explicit.", "Silent queue growth fails the gate."),
    ("operation", "reconciliation", "Controllers converge idempotently and surface terminal refusal.", "Infinite retry without state evidence fails the gate."),
    ("operation", "restore_drill", "Stateful services test restore against pinned artifacts and record receipts.", "A backup without a verified restore is not recovery evidence."),
    ("operation", "degraded_mode", "Safe degraded modes enumerate retained and prohibited outcomes.", "Partial output presented as complete is prohibited."),
    ("operation", "dependency_failure", "Dependency failures map to owned user-visible behavior and escalation.", "Passing through raw provider failures is insufficient support."),
    ("support", "named_owner", "A named support owner accepts incidents, defects and consumer questions.", "A repository maintainer list is not a service owner."),
    ("support", "severity_model", "Severity, response, communication and restoration targets are published.", "Best-effort support cannot substantiate an enterprise product."),
    ("support", "runbooks", "Supported failure modes have exercised runbooks and escalation paths.", "A document never exercised is not operational evidence."),
    ("support", "compatibility_support", "Supported versions and security-fix windows are published.", "Forced undocumented upgrades fail lifecycle support."),
    ("support", "consumer_support_boundary", "Provider and consumer responsibilities are explicit.", "Ambiguous responsibility produces unowned incidents."),
    ("slo", "user_journey_sli", "SLIs measure user journeys rather than only component uptime.", "Healthy components with failed outcomes consume the product error budget."),
    ("slo", "availability", "Availability defines valid requests, good events and exclusions.", "Undefined denominator makes the SLO non-falsifiable."),
    ("slo", "latency", "Latency targets include percentile, window, payload and concurrency profile.", "A single average cannot support the promise."),
    ("slo", "freshness", "Data products bind freshness to event/record/cut semantics.", "Wall-clock age without source finality is insufficient."),
    ("slo", "correctness", "Correctness indicators detect semantic as well as transport success.", "HTTP success with wrong grain or cut is a bad event."),
    ("slo", "error_budget", "Error-budget policy names decision authority and release consequences.", "A dashboard without policy is not an error budget."),
    ("slo", "dependency_budget", "Composite SLO assumptions and dependency allocations are explicit.", "Multiplying undocumented provider SLAs is prohibited."),
    ("slo", "slo_exit", "SLO history is exportable and retained through provider changes.", "Migration may not erase prior reliability evidence."),
    ("security", "least_privilege", "Every effect uses a purpose-, tenant-, resource- and time-scoped grant.", "Ambient broad credentials fail the gate."),
    ("security", "fail_closed", "Protected decisions fail closed on unknown policy or authority.", "Fallback allow on policy outage is prohibited."),
    ("security", "tenant_isolation", "Tenant identity and isolation are tested at storage, compute, cache and telemetry boundaries.", "UI-only tenant filtering is prohibited."),
    ("security", "secret_reference", "Contracts carry secret references, never secret material.", "Credentials in plans, logs or exports fail the gate."),
    ("security", "supply_chain", "Artifacts have SBOM, provenance, signature and vulnerability disposition.", "An unsigned opaque release cannot be qualified."),
    ("security", "audit_integrity", "Authority and effect receipts are append-only, attributable and retention-bound.", "Mutable administrator logs are insufficient."),
    ("security", "privacy_purpose", "Personal-data use binds purpose, legal basis/authority, place, time and recipients.", "Role-only access does not establish lawful use."),
    ("security", "abuse_case", "Threat and abuse tests include confused deputy, replay, enumeration and exfiltration.", "Happy-path authorization tests are insufficient."),
    ("commercial", "meter", "Usage units are defined independently from invoice presentation.", "A price without measurable consumption cannot allocate cost."),
    ("commercial", "allocation", "Shared costs have versioned allocation rules and residual handling.", "Unattributed shared cost invalidates unit economics."),
    ("commercial", "entitlement", "Entitlements map explicitly to outcomes and interfaces, not implementation modules.", "Packaging must not change semantic ownership."),
    ("commercial", "price_change", "Price and quota changes have notice, simulation and exit impact.", "Unannounced limit changes invalidate adoption assumptions."),
    ("commercial", "consumer_budget", "Consumers can set hard budgets and receive pre-exhaustion signals.", "Post-hoc invoices alone are insufficient control."),
    ("commercial", "internal_chargeback", "Internal products allocate cost even when no external invoice exists.", "Free-at-point-of-use is not zero economic boundary."),
    ("exit", "machine_readable_export", "State, configuration, policy, evidence and data export in documented machine-readable forms.", "Screenshots and support tickets are not an exit path."),
    ("exit", "identity_preservation", "Stable identities and editions survive export or map through declared loss.", "Re-keying without crosswalk breaks historical replay."),
    ("exit", "active_work", "In-flight work, subscriptions, grants and incidents have explicit disposition.", "Abandoning active obligations is prohibited."),
    ("exit", "deletion", "Provider-side deletion and retained exceptions produce evidence.", "Export success does not imply deletion success."),
    ("exit", "egress_cost", "Exit duration, egress volume, fees and throttles are estimable before adoption.", "Unknown exit cost fails commercial transparency."),
    ("exit", "replacement_test", "A substitute passes conformance and historical replay before cutover.", "Format readability alone is insufficient substitution proof."),
    ("exit", "decommission", "Dependencies, credentials, routes, replicas and support duties close in order.", "Orphaned access or state fails retirement."),
    ("exit", "legal_retention", "Exit separates deletion from legally required retention and access restrictions.", "Supplier exit cannot override hold or records authority."),
]


ALTERNATIVES = [
    ("whole_data_platform", ["one all-in-one product", "independent horizontal products plus suites"], 1, "Refuse the monolith: source, policy, table, query, semantics, operations and exit have different authorities and failure domains."),
    ("lakehouse_boundary", ["lakehouse as one product", "table semantic contracts/capabilities plus catalog, query, ingestion, managed-maintenance, sharing and experience products"], 1, "Retain lakehouse as an architecture/suite: table formats are standards and semantic contracts, while independently adopted operated promises may become products."),
    ("warehouse_lakehouse", ["one storage architecture product", "two experience products over shared table/query/policy capabilities"], 1, "Retain alternative experiences until adoption, portability and workload SLO evidence supports merge."),
    ("catalog_governance", ["catalog owns all governance", "discovery projection separate from glossary, policy, lineage, quality and master data"], 1, "Refuse concentrated authority and duplicated semantic ownership."),
    ("glossary_ontology", ["one semantic-governance owner", "business glossary and formal ontology/knowledge-model products"], 1, "Human term stewardship and formal axiom/inference semantics have different equality, lifecycle, failure and adoption boundaries."),
    ("schema_data_contract", ["one schema-and-contract registry", "schema registry plus data-contract registry"], 1, "Syntax and reader-writer compatibility are imported evidence within, but cannot replace, semantic and service acceptance."),
    ("query_semantics", ["query engine owns metrics", "semantic metric service compiles into replaceable query engines"], 1, "Keep business meaning above physical planning and execution."),
    ("bi_semantics", ["BI tool owns metric definitions", "BI imports semantic metric contracts"], 1, "A presentation channel cannot become the sole business-semantic owner."),
    ("pipeline_source", ["pipeline owns source meaning", "source owner publishes contract; pipeline imports through ACL"], 1, "Movement does not create source authority."),
    ("movement_boundary", ["one generic pipeline product", "connectivity, CDC, ingestion, orchestration, dataflow, transform-build, event-streaming and activation products"], 1, "Split by cursor/state, effect authority, lifecycle, failure, support and exit; retain ETL/ELT/CDC/reverse-ETL labels as patterns."),
    ("quality_observability", ["one observability product", "data fitness and platform telemetry remain independent"], 1, "A healthy service can return semantically wrong data and a quality failure need not be a platform outage."),
    ("sharing_clean_room", ["one collaboration feature", "sharing and clean-room products with separate release authority"], 1, "Raw disclosure and aggregate-only computation have materially different trust and exit boundaries."),
    ("ml_platform", ["one AI/ML platform", "model lifecycle + feature platform + inference serving + model assurance + deterministic decisioning + optional extension runtime"], 1, "Training, temporal feature truth, serving SLOs, evaluation evidence, deterministic decision semantics and optional generated proposals have different owners and exit boundaries."),
    ("analytical_method_product", ["one product per analytical method label", "methods and libraries imported into job-specific workbenches, engines and vertical applications"], 1, "A practice such as statistics, anomaly detection, graph analysis or causal inference is not independently a product; adoption, lifecycle, operation, support and exit must be proven separately."),
    ("analytical_automation_modality", ["prefix every analytical capability with AI", "deterministic core with prohibited, optional or intent-required model/LLM/agent ports"], 1, "Automation modality is a typed binding choice, not a domain boundary; assistance never acquires semantic or effect authority."),
    ("connector_products", ["product per vendor connector", "source connectivity product plus adapter/provider registry"], 1, "Vendor adapters are replaceable provider implementations, not product semantics."),
    ("codec_products", ["product per codec or format", "representation libraries and provider offers imported by products"], 1, "Encoding lacks a direct enterprise outcome and support/exit boundary."),
    ("industry_products", ["new horizontal product per industry", "industry solution packs compose unchanged horizontal products"], 1, "Vertical terms, rules and authority stay in packs; horizontal meanings must not branch by industry."),
    ("context_products", ["product per bounded context", "products compose contexts through published languages"], 1, "Semantic ownership and adoption boundaries are orthogonal graphs."),
    ("table_data_product", ["every table is a data product", "only independently valuable governed publications qualify"], 1, "A table without users, SLO, access, lifecycle and exit remains an asset/output port."),
    ("visualization_product", ["every chart/widget is a product", "rendering capability or module within BI/embedded experiences"], 1, "A widget has no independent adoption, support, economic or exit promise."),
]


INCOMPATIBILITIES = [
    ("metric_owner_collision", "semantic_metric", "bi_reporting", "Both may not own the same metric edition; BI must import it."),
    ("metric_query_execution", "semantic_metric", "distributed_query", "Semantic query owns metric, grain, population and formula binding; the query engine owns physical execution and cannot redefine them."),
    ("metric_glossary_authority", "semantic_metric", "business_glossary", "A metric may reference approved terms but cannot silently become the glossary authority or collapse homonyms."),
    ("metric_bundle_trace", "metric_store_bundle", "semantic_metric", "The legacy metric-store/query bundle remains a packaging trace and cannot acquire a second semantic owner."),
    ("metric_generated_authority", "semantic_metric", "optional_model_extension", "Generated formulas, mappings or explanations are proposals until deterministic type, fanout, policy and owner-approval gates pass."),
    ("catalog_policy_collision", "catalog_commit", "data_use_policy", "Catalog authorization cannot silently replace enterprise purpose policy."),
    ("catalog_glossary_collision", "metadata_discovery", "business_glossary", "Search projection may not become the authoritative business term."),
    ("glossary_ontology_collision", "business_glossary", "ontology_knowledge_model", "A business term and a formal ontology class are distinct identities; label equality cannot collapse them."),
    ("schema_contract_collision", "schema_registry", "data_contract_registry", "Schema compatibility cannot assert semantic, quality, service or consumer acceptance."),
    ("ontology_quality_collision", "ontology_knowledge_model", "data_quality_operations", "Shape or ontology validation is a scoped report and cannot certify universal fitness or authorize correction."),
    ("lineage_causality", "lineage_provenance", "experimentation_platform", "Derivation edges cannot satisfy a causal analysis or experiment conclusion."),
    ("quality_truth", "data_quality_operations", "data_product_publication", "A quality attestation is purpose-scoped and cannot assert universal truth."),
    ("quality_reconciliation_noncollapse", "data_quality_operations", "reconciliation_control_operations", "A failed validation or quality signal is not a reconciliation break; each requires distinct populations, truth roles, lifecycle and authority."),
    ("maintenance_catalog_authority", "managed_table_maintenance", "catalog_commit", "A maintenance service cannot forge catalog current-pointer authority while publishing a rewrite."),
    ("query_catalog_identity", "distributed_query", "catalog_commit", "Replacing the query engine must not rewrite catalog identity, current references or table history."),
    ("federation_type_loss", "federated_query", "source_connectivity_control", "Unsupported source types require explicit lossy mapping or refusal."),
    ("federation_virtual_lifecycle", "federated_query", "virtual_data_access", "Pushdown capability cannot own virtual-relation identity, publication, retirement or materialization lifecycle."),
    ("sharing_policy", "data_sharing", "data_use_policy", "A subscription never bypasses purpose-scoped access decisions."),
    ("clean_room_release", "clean_room", "data_sharing", "Aggregate release authority is distinct from raw-share authorization."),
    ("mdm_entity_link", "master_data_governance", "entity_resolution", "A probabilistic link proposal cannot issue or mutate a master identity or projection without master-domain and steward authority."),
    ("master_reference_noncollapse", "master_data_governance", "reference_data_governance", "A mastered entity and a reference value/code have independent identity, authority, lifecycle, publication and exit obligations."),
    ("reference_glossary_noncollapse", "reference_data_governance", "business_glossary", "A reference code or designation cannot silently become an authoritative business term, and label equality cannot merge their owners."),
    ("reference_ontology_noncollapse", "reference_data_governance", "ontology_knowledge_model", "A directional crosswalk does not prove ontology equivalence, reverse mapping or entailment."),
    ("forecast_fact", "forecasting_workbench", "data_product_publication", "Forecasts must remain distinct from observed facts in publications."),
    ("optimization_action", "optimization_solver", "solution_compiler", "Solver feasibility cannot create business command authority."),
    ("model_inference_lifecycle", "online_inference", "model_lifecycle", "Serving may load only approved model editions but cannot approve them."),
    ("feature_leakage", "feature_platform", "model_lifecycle", "Online/offline time semantics must prevent future-feature leakage."),
    ("prediction_decision", "online_inference", "decision_automation", "A score, probability or class is not a governed business decision, authorization or command."),
    ("assurance_approval", "model_assurance", "model_lifecycle", "Evaluation and monitoring evidence cannot self-issue lifecycle approval or deployment authority."),
    ("extension_authority", "optional_model_extension", "data_use_policy", "Generated claims, plans and tool calls cannot create purpose, disclosure or effect authority."),
    ("orchestrator_task", "pipeline_orchestration", "dataflow_execution", "The orchestrator coordinates task state but does not redefine dataflow delivery semantics."),
    ("ingestion_connection_authority", "ingestion_delivery", "source_connectivity_control", "An ingestion service consumes qualified connections but cannot silently create, broaden or retain source authority."),
    ("ingestion_table_authority", "ingestion_delivery", "catalog_commit", "Delivery completion cannot forge catalog current-pointer authority or redefine the analytical table contract."),
    ("capture_transport_cursor", "source_replication_cdc", "event_streaming", "Source-native capture cursors and broker transport offsets are distinct identities with different reset and retention laws."),
    ("activation_effect_authority", "operational_activation", "data_use_policy", "An analytical row or activation mapping cannot authorize an operational insert, update, upsert or delete effect."),
    ("backup_archive", "backup_restore_archive", "privacy_rights_retention", "Restore availability cannot override erasure, hold or retention authority."),
    ("recovery_archive_boundary", "data_protection_recovery", "digital_preservation_archive", "Operational recoverability cannot substitute for designated-community preservation, and preservation custody cannot imply service recovery."),
    ("legacy_protection_umbrella", "backup_restore_archive", "data_protection_recovery", "The legacy umbrella must remain a split trace and cannot reacquire recovery-product authority."),
    ("vector_search_feature", "search_index_serving", "feature_platform", "Vector retrieval belongs to index/search semantics; a feature platform cannot acquire ranking, visibility-cut or index-generation authority."),
    ("search_model_authority", "search_index_serving", "model_lifecycle", "A ranking model may be imported by exact edition, but search cannot train, approve or retire it implicitly."),
    ("recovery_records_authority", "data_protection_recovery", "privacy_rights_retention", "Recovery-copy retention cannot override records holds, erasure or lawful disposition authority."),
    ("archive_records_authority", "digital_preservation_archive", "privacy_rights_retention", "The archive executes governed retention and disposition but cannot invent the underlying authority."),
    ("finops_meter", "finops_allocation", "runtime_resource_control", "Resource receipts are evidence; allocation rules remain separately governed."),
    ("marketplace_authority", "data_marketplace", "data_product_publication", "A listing does not issue or recall the underlying data product."),
    ("spreadsheet_metric", "spreadsheet_governance", "semantic_metric", "Workbook formulas cannot silently fork governed metrics."),
    ("geo_crs_loss", "geospatial_workbench", "federated_query", "CRS or spatial support cannot be dropped during pushdown."),
]


SUBSTITUTIONS = [
    ("operational_activation", "operational_activation", ["Hightouch", "managed reverse-ETL service", "independent conforming activation controller"], "destination object mapping, identity matching, write modes, purpose authority, idempotency, recovery, compensation and receipts"),
    ("ingestion_delivery", "ingestion_delivery", ["Onehouse OneFlow", "managed multi-source ingestion service", "independent conforming ingestion controller"], "source binding, snapshot/change stitching, delivery cursor, table-contract compatibility, recovery, cancellation and receipts"),
    ("table_maintenance", "managed_table_maintenance", ["Onehouse Table Optimizer", "Dremio Open Catalog maintenance", "independent format-native maintenance service"], "maintenance planning, logical-equivalence, concurrency, retention, cancellation and destructive-effect receipts"),
    ("catalog", "catalog_commit", ["Apache Polaris", "Project Nessie", "Iceberg REST-compatible service"], "namespace, commit, credential vending, export and policy conformance"),
    ("distributed_query", "distributed_query", ["Trino", "Apache Spark SQL", "Apache DataFusion"], "typed plans, null/time/numeric semantics, cancellation and result fixtures"),
    ("warehouse", "warehouse_experience", ["BigQuery", "Snowflake", "Amazon Redshift"], "SQL profile, export, security, SLO and economic comparison"),
    ("stream_engine", "dataflow_execution", ["Apache Flink", "Apache Beam runners", "Kafka Streams"], "event time, state, checkpoint, replay and delivery proof"),
    ("orchestrator", "pipeline_orchestration", ["Apache Airflow", "Dagster", "Prefect"], "workflow state, retry, backfill, cancellation and run receipts"),
    ("lineage", "lineage_provenance", ["OpenLineage backend", "DataHub", "OpenMetadata"], "OpenLineage facets, retention, export and graph query"),
    ("quality", "data_quality_operations", ["Great Expectations", "Soda", "custom conforming engine"], "purpose scope, rule semantics, cut binding, partial outcomes, defect adjudication, quarantine, waiver, remediation and evidence"),
    ("reconciliation", "reconciliation_control_operations", ["data-diff", "provider-neutral reconciliation controller", "independent conforming reconciliation service"], "comparison populations, truth roles, keys, transformations, tolerances, materiality, residuals, breaks, dispositions, adjustment proposals and control-completion evidence"),
    ("metadata_catalog", "metadata_discovery", ["DataHub", "OpenMetadata", "Apache Atlas"], "identity, ingestion, search, export and source attribution"),
    ("business_glossary", "business_glossary", ["DataHub glossary", "OpenMetadata glossary", "independent SKOS-conformant service"], "term identity, language, homonyms, mappings, approval, deprecation and export"),
    ("ontology_service", "ontology_knowledge_model", ["OWL 2 service", "SHACL-capable knowledge-model service", "independent conforming reasoner"], "ontology edition, inference profile, constraint semantics, explanation and export"),
    ("schema_registry", "schema_registry", ["Confluent Schema Registry", "Apicurio Registry", "independent conforming registry"], "subject/version identity, serialization profile, compatibility mode and export"),
    ("data_contract_registry", "data_contract_registry", ["ODCS registry", "provider-neutral contract service", "independent conforming registry"], "parties, logical schema, quality, service promises, acceptance, change and termination"),
    ("policy", "data_use_policy", ["Open Policy Agent", "Apache Ranger", "Cedar-compatible service"], "decision semantics, combining, obligations, revocation and receipts"),
    ("semantic_layer", "semantic_metric", ["dbt Semantic Layer", "Cube", "provider-neutral compiler"], "formula and metric identity, grain, population, joins, summarizability, time, units, missingness, uncertainty, policy, observation receipts and multi-engine result equivalence"),
    ("bi", "bi_reporting", ["Apache Superset", "Power BI", "Tableau"], "semantic imports, accessibility, export, embedding and tenant isolation"),
    ("notebook", "analytical_notebook", ["JupyterLab", "managed notebook provider", "IDE notebook"], "document format, kernel environment, data cut and reproducibility"),
    ("feature_store", "feature_platform", ["Feast", "warehouse-native feature platform", "independent conforming feature service"], "feature identity, event/availability/recording time, point-in-time correctness, materialization, freshness, partiality and export"),
    ("model_registry", "model_lifecycle", ["MLflow", "Kubeflow registry", "custom conforming registry"], "model identity, validation, approval, deployment and retirement"),
    ("inference", "online_inference", ["KServe", "Seldon", "custom conforming runtime"], "inference protocol, rollout, latency, resource and receipt semantics"),
    ("model_assurance", "model_assurance", ["Evidently", "independent model-observability service", "custom conforming assurance engine"], "evaluation cuts, slices, metrics, threshold policy, drift semantics, label maturity, review and evidence export"),
    ("decision_runtime", "decision_automation", ["Apache KIE DMN", "DMN-conforming decision service", "custom deterministic decision runtime"], "DMN/FEEL edition, type and hit-policy semantics, determinism, trace, refusal and authority handoff"),
    ("optional_model_extension", "optional_model_extension", ["MCP/A2A-based extension runtime", "provider-neutral model adapter host", "local qualified extension runtime"], "task, schema, fallback, budgets, provider occurrence, proposal taint, tool authority gates, receipts and removal proof"),
    ("experimentation", "experimentation_platform", ["GrowthBook", "independent conforming experimentation controller", "warehouse-native experimentation platform"], "assignment, exposure, metric-cut, stopping, causal-analysis and conclusion lifecycle"),
    ("forecasting", "forecasting_workbench", ["Forecast Pro", "SAS forecasting workbench", "independent conforming forecasting service"], "origin, horizon, information cut, backtest, uncertainty, override and publication semantics"),
    ("optimization", "optimization_solver", ["Gurobi Optimizer", "HiGHS-based conforming engine", "SCIP-based conforming engine"], "model classes, tolerances, statuses, gaps, infeasibility evidence, numerical behavior and cancellation"),
    ("process_mining", "process_mining_workbench", ["Process Mining Toolkit", "commercial process workbench", "custom conforming workbench"], "source-attributed projection, OCEL import, state-aware semantics, discovery, conformance and evidence fixtures"),
    ("geospatial", "geospatial_workbench", ["QGIS", "ArcGIS Pro", "GRASS GIS-based conforming workbench"], "project, CRS, topology, accuracy, workflow history and OGC conformance"),
    ("graph_workbench", "graph_analysis_workbench", ["Gephi", "Cytoscape", "Neo4j Graph Data Science-based conforming workbench"], "workspace, graph cut/profile, algorithm plan, run evidence, comparison, benchmark scope, publication and exit conformance"),
    ("simulation", "simulation_environment", ["AnyLogic", "SIMUL8", "SimPy-based conforming environment"], "model/scenario identity, clocks, seeds, replications, calibration, sensitivity and FMI exchange"),
    ("search", "search_index_serving", ["OpenSearch", "Elasticsearch", "Lucene-based service"], "index mapping, refresh, ranking, snapshot and export"),
    ("virtual_data_access", "virtual_data_access", ["Denodo", "Calcite-based virtual access service", "independent conforming virtualization service"], "virtual relation identity, source bindings, translation loss, materialization policy, lifecycle, access receipts and exit"),
    ("data_protection_recovery", "data_protection_recovery", ["pgBackRest-based service", "Velero-based service", "independent conforming recovery controller"], "protection scope, consistency cuts, backup chains, measured RPO/RTO, restore verification, recovery acceptance and retention conflicts"),
    ("digital_preservation_archive", "digital_preservation_archive", ["OAIS-conformant archive", "PREMIS-capable preservation service", "independent conforming preservation repository"], "information packages, representation information, fixity, custody, preservation actions, designated-community access and governed disposition"),
]


PACKS = [
    ("built_food_environment", "bfe.case.c001", ["geospatial_workbench", "forecasting_workbench", "data_quality_operations", "data_product_publication"], ["semantic.geospatial_analysis", "semantic.time_series", "semantic.statistical_inference"]),
    ("commerce_services", "commerce.case.retail_phantom_inventory_rca", ["entity_resolution", "process_mining_workbench", "data_quality_operations", "reconciliation_control_operations", "bi_reporting"], ["semantic.process_mining", "semantic.anomaly_change", "semantic.statistical_inference"]),
    ("energy_resources", "energy.case.prospect_ranking", ["simulation_environment", "optimization_solver", "geospatial_workbench", "independent_assurance"], ["semantic.simulation_model", "semantic.optimization_model", "semantic.geospatial_analysis"]),
    ("finance_insurance", "fin.case.banking.balancesheet.bridge", ["data_quality_operations", "reconciliation_control_operations", "data_use_policy", "semantic_metric", "independent_assurance", "graph_analysis_workbench"], ["semantic.statistical_inference", "semantic.anomaly_change", "semantic.optimization_model", "semantic.graph_analysis"]),
    ("health_life_sciences", "health.case.acute.deterioration", ["forecasting_workbench", "model_lifecycle", "online_inference", "privacy_rights_retention"], ["semantic.time_series", "semantic.statistical_inference", "semantic.causal_inference"]),
    ("manufacturing_industrial", "mfg.case.loss_tree", ["process_mining_workbench", "semantic_metric", "bi_reporting", "data_quality_operations"], ["semantic.process_mining", "semantic.anomaly_change", "semantic.optimization_model", "semantic.simulation_model"]),
    ("public_education", "case.public.permit_bottleneck", ["process_mining_workbench", "privacy_rights_retention", "bi_reporting", "data_product_publication"], ["semantic.process_mining", "semantic.statistical_inference", "semantic.simulation_model"]),
    ("telecom_media_tech", "case.tmt.tel.alarm_storm_rca", ["platform_operations", "dataflow_execution", "process_mining_workbench", "data_quality_operations", "graph_analysis_workbench"], ["semantic.graph_analysis", "semantic.anomaly_change", "semantic.process_mining", "semantic.media_signal_analysis"]),
    ("transport_logistics", "transport.case.supply.flow_constraint_localization", ["optimization_solver", "process_mining_workbench", "forecasting_workbench", "geospatial_workbench"], ["semantic.optimization_model", "semantic.process_mining", "semantic.time_series", "semantic.geospatial_analysis", "semantic.simulation_model"]),
]


GAPS = [
    ("global_context_map", "context", "The atlas reports the global context map as missing; product semantic imports and ACL loss cannot yet be ratified.", ["all"]),
    ("context_adjudication", "context", "567 context candidates remain enumerated rather than adjudicated with unique semantic owners.", ["all"]),
    ("semantic_owner_uniqueness", "context", "No global proof yet establishes one owner for metric, dataset, identity, policy and authority meanings.", ["governance", "semantics"]),
    ("library_implementation", "library", "Many library boundaries are hypotheses and lack two independent implementations and law-oracle evidence.", ["methods", "compute", "movement"]),
    ("library_cycle_removal", "library", "Global crate/dependency cycle analysis and dependency-removal proof are incomplete.", ["all"]),
    ("provider_occurrences", "provider", "Provider occurrences, regions, versions, quotas, credentials and fresh probes are largely absent.", ["all"]),
    ("provider_qualification", "provider", "Cross-provider conformance and performance receipts do not yet cover two independent implementations per required offer.", ["all"]),
    ("source_occurrence_registry", "provider", "The source occurrence registry is schema-only, preventing real connector adoption and exit proof.", ["movement"]),
    ("compiler_implementation", "compiler", "Compiler stages and bindings are a research contract; no implementation closes all required products and residual gaps.", ["platform"]),
    ("compiler_semantic_diff", "compiler", "Semantic diff, blast-radius and invalidation propagation lack executable implementation evidence.", ["all"]),
    ("compiler_solution_closure", "compiler", "No end-to-end mixed-industry solution proves every product requirement bound without hidden defaults.", ["all"]),
    ("operation_totality", "compiler", "The 1,062 operation hypotheses lack a complete typed signature/law/lowering matrix.", ["methods", "compute", "movement"]),
    ("data_type_totality", "context", "The data-type ontology lacks operation-by-type totality and information-loss proof.", ["compute", "methods", "persistence"]),
    ("slo_baselines", "provider", "No representative workload measurements establish feasible SLO, capacity and unit-cost envelopes.", ["all"]),
    ("exit_drills", "provider", "No complete supplier-exit drill exports state, policies, evidence and in-flight obligations into a substitute.", ["all"]),
    ("security_appraisal", "provider", "Threat models, tenant isolation, privacy purpose and supply-chain evidence lack independent appraisal across the portfolio.", ["all"]),
    ("two_release_vertical", "compiler", "No product has passed a two-release vertical with migration, replay, rollback and retained historical evidence.", ["all"]),
    ("unrelated_domain_generality", "compiler", "Horizontal meanings have not been proven unchanged across two unrelated industries end to end.", ["all"]),
    ("commercial_validation", "provider", "Meter definitions, allocation laws, price sensitivity and exit cost lack buyer/operator validation.", ["all"]),
    ("support_validation", "provider", "Support staffing, escalation, severity and recovery commitments lack exercised operational evidence.", ["all"]),
]


FAMILY_IMPORTS = {
    "platform": ["provider-capability", "resource-budget", "service-level-objective"],
    "movement": ["connector-contract", "delivery-order", "checkpoint-equivalence"],
    "persistence": ["analytical-table-format", "table-catalog", "backup-restore"],
    "compute": ["logical-query", "physical-plan", "query-cancellation"],
    "serving": ["serving-cut", "cache-coherence", "data-use-policy"],
    "governance": ["authority-delegation", "data-owner", "evidence-proof-defeater"],
    "assurance": ["quality-assessment", "provenance-reference", "independent-appraisal"],
    "semantics": ["metric", "grain", "semantic-query"],
    "consumption": ["workspace", "accessibility", "subscription"],
    "methods": ["analytical-study", "analytical-assumption", "analytical-result"],
    "models": ["model-validation", "model-retirement", "analytical-drift"],
    "decisioning": ["decision-model", "decision-result", "authority-decision", "effect-proposal"],
    "extension": ["optional-model-task", "generated-proposal", "deterministic-fallback", "authority-gate"],
    "representation": ["encoding-compression", "carrier-validation", "semantic-loss-accounting"],
    "preparation": ["immutable-data-cut", "typed-transformation-recipe", "profile-and-diff-evidence"],
    "analytical_operations": ["operation-programme", "method-result", "review-and-release-evidence"],
    "control": ["authorized-baseline", "status-and-evidence-cut", "decision-authority", "effect-receipt"],
}


def score_for(candidate: dict[str, Any]) -> dict[str, Any]:
    templates = {
        "strong_product": [2, 2, 2, 2, 2, 2, 2, 2, 2, 2],
        "presumptive_product": [2, 2, 2, 2, 1, 2, 1, 1, 2, 1],
        "defer": [1, 2, 1, 2, 1, 1, 1, 0, 1, 1],
        "merge": [1, 1, 0, 1, 0, 0, 1, 0, 1, 0],
    }
    keys = ["user", "job", "adoption", "semantics", "authority", "lifecycle", "operation", "economics", "interface", "market_evidence"]
    adjudications = (
        ("lakehouse", LAKEHOUSE_ADJUDICATION_SUBJECTS, lakehouse_adjudication_decisions()),
        ("movement", MOVEMENT_ADJUDICATION_SUBJECTS, movement_adjudication_decisions()),
        ("governance_semantics", GOVERNANCE_ADJUDICATION_SUBJECTS, governance_adjudication_decisions()),
        ("analytical_methods", ANALYTICAL_METHOD_ADJUDICATION_SUBJECTS, analytical_method_adjudication_decisions()),
        ("consumption_experiences", CONSUMPTION_ADJUDICATION_SUBJECTS, consumption_adjudication_decisions()),
        ("platform_control", PLATFORM_ADJUDICATION_SUBJECTS, platform_adjudication_decisions()),
        ("model_decision_serving", MODEL_DECISION_ADJUDICATION_SUBJECTS, model_decision_adjudication_decisions()),
        ("query_warehouse_search_protection", QUERY_WAREHOUSE_SEARCH_PROTECTION_SUBJECTS, query_warehouse_search_protection_decisions()),
        ("semantic_metrics_formulas", SEMANTIC_METRIC_FORMULA_SUBJECTS, semantic_metric_formula_decisions()),
        ("collaboration_privacy_resolution_assurance", COLLABORATION_PRIVACY_RESOLUTION_ASSURANCE_SUBJECTS, collaboration_privacy_resolution_assurance_decisions()),
        ("representation_codec_boundary", REPRESENTATION_CODEC_SUBJECTS, representation_codec_decisions()),
        ("analytical_operations", ANALYTICAL_OPERATIONS_SUBJECTS, analytical_operations_decisions()),
    )
    for bundle, subject_map, decisions in adjudications:
        subject_ref = subject_map.get(candidate["candidate_id"])
        if not subject_ref:
            continue
        decision = decisions[subject_ref]
        split = decision.get("split_test")
        if not split:
            disposition = decision["disposition"]
            if disposition.startswith("reclassify") or disposition.startswith("merge"):
                verdict = "merge"
            elif "defer" in disposition or "split" in disposition:
                verdict = "defer"
            else:
                verdict = candidate["boundary_verdict"]
            vals = templates[verdict]
            return {
                "scores": dict(zip(keys, vals)),
                "total": sum(vals),
                "verdict": verdict,
                "adjudication_disposition": decision["disposition"],
                "adjudication_ref": f"research/product_ontology/adjudications/{bundle}/boundary-decisions.jsonl#{decision['decision_id']}",
            }
        scores = {key: split[key]["score"] for key in keys}
        verdict = "presumptive_product" if decision["disposition"] == "presumptive_product" else "strong_product"
        return {
            "scores": scores,
            "total": sum(scores.values()),
            "verdict": verdict,
            "axis_evidence": {key: split[key]["evidence_refs"] for key in keys},
            "adjudication_ref": f"research/product_ontology/adjudications/{bundle}/boundary-decisions.jsonl#{decision['decision_id']}",
        }
    vals = templates[candidate["boundary_verdict"]]
    scores = dict(zip(keys, vals))
    return {"scores": scores, "total": sum(vals), "verdict": candidate["boundary_verdict"]}


def make_candidates() -> list[dict[str, Any]]:
    rows = []
    for item in CANDIDATES:
        ident = item["candidate_id"].split(".")[-1]
        evaluation = score_for(item)
        adopted = evaluation["verdict"] in {"presumptive_product", "strong_product"}
        row = {
            "record_id": item["candidate_id"], "record_kind": "product_boundary_candidate", "edition": EDITION,
            "status": "researched_candidate", "name": item["name"], "family": item["family"],
            "archetype_kind": item["archetype_kind"],
            "sovereign_question": f"How can {item['users'][0]} {item['job']} with an independently governed promise?",
            "positive_promise": item["outcome"],
            "negative_promise": "Does not acquire source-domain business authority, silently select providers, or hide unresolved semantic gaps.",
            "owned_meanings": item["owned_meanings"],
            "excluded_meanings": ["source_business_fact", "enterprise_identity", "unrelated_product_semantics"],
            "adoption_boundary": (f"Adoptable through a versioned {ident} declaration and conformance gate." if adopted else "No independent adoption proven; expected to be adopted with its containing product."),
            "operation_boundary": ("Owns declared SLOs, capacity, observability, incident and recovery behavior for its promise." if "operated" in item["traits"] else "Pure/embedded form owns correctness, determinism, budgets and cancellation; an operator wrapper owns availability."),
            "support_boundary": ("Publishes support versions, severity, response, restoration and escalation responsibility." if adopted else "Support remains with the containing product."),
            "commercial_boundary": ("Usage is metered and allocatable independently; price packaging may still occur in a suite." if adopted else "No independently meaningful usage or allocation unit is proven."),
            "exit_boundary": ("Exports declarations, state, identities, evidence and active-work disposition into a conforming substitute." if adopted else "Removed by replacing or upgrading the containing product without a consumer migration contract."),
            "interfaces": [f"interface.{ident}.declaration", f"interface.{ident}.status", f"interface.{ident}.export"],
            "automation_modality": {
                "default_posture": "DETERMINISTIC_CORE_ONLY",
                "per_use_site_override": ["PROHIBITED", "OPTIONAL", "REQUIRED_BY_INTENT", "UNDETERMINED"],
                "law": "A model or agent may satisfy an explicitly typed capability requirement but does not acquire semantic ownership, authority, effect execution or acceptance-proof responsibility.",
                "fallback": "Removing every model or agent extension leaves deterministic parsing, typing, constraint solving, planning, authorization, qualification, effect execution and evidence behavior intact; only an explicitly requested extension capability may become unavailable.",
                "research_and_construction_law": "Models and agents may accelerate discovery or propose typed artifacts, but do not replace vocabulary enumeration, semantic adjudication, invariant and lifecycle definition, algorithm selection, source evidence, negative testing, provider qualification or human/domain acceptance.",
                "analytical_method_law": "Statistical, probabilistic, predictive, heuristic, simulation and optimization methods remain first-class typed methods; approximation or stochasticity is declared and qualified rather than relabeled as AI or agent behavior.",
            },
            "traits": item["traits"], "evidence_ids": item["evidence_ids"],
            "boundary_evaluation": evaluation,
            "falsifiers": [
                "No real consumer can adopt and exit this boundary independently.",
                "A neighboring candidate must own the same meaning or authority for correctness.",
                "Failure, support and cost cannot be isolated at this boundary.",
            ],
            "ratification": "withheld",
        }
        rows.append(row)
    return rows


def make_user_jobs() -> list[dict[str, Any]]:
    rows = []
    for item in CANDIDATES:
        ident = item["candidate_id"].split(".")[-1]
        rows.append({
            "record_id": f"ujo.{ident}", "record_kind": "user_job_outcome", "edition": EDITION, "status": "candidate",
            "candidate_id": item["candidate_id"], "primary_users": item["users"],
            "job": item["job"], "measurable_outcomes": [item["outcome"], "time_to_first_value", "successful_exit_drill"],
            "harmed_parties": ["data_subject", "downstream_consumer", "on_call_operator", "business_decision_subject"],
            "adoption_trigger": f"A {item['users'][0]} needs the promised outcome under an independently testable contract.",
            "non_consumption_signal": "Consumers use only an incidental implementation API and cannot describe an independent outcome.",
            "falsifier": "Interviews and telemetry show no distinct job, adoption decision or outcome measure.",
        })
    return rows


def make_blueprints() -> list[dict[str, Any]]:
    rows = []
    for item in CANDIDATES:
        ident = item["candidate_id"].split(".")[-1]
        rows.append({
            "record_id": f"blueprint.{ident}", "record_kind": "service_blueprint", "edition": EDITION, "status": "candidate",
            "candidate_id": item["candidate_id"],
            "journey_stages": ["discover", "evaluate", "adopt", "configure", "use", "operate", "support", "exit"],
            "frontstage": ["published promise and limits", "self-service declaration/API", "status and evidence", "support and exit workflow"],
            "backstage": ["requirement/offer binding", "policy and authority decision", "provider operation", "metering", "evidence retention"],
            "supporting_products": ["candidate.product.data_use_policy", "candidate.product.lineage_provenance", "candidate.product.finops_allocation"],
            "evidence_at_handoffs": ["adoption_receipt", "configuration_digest", "runtime_receipt", "incident_record", "exit_receipt"],
            "failures": ["unbound_requirement", "authority_refusal", "provider_failure", "budget_exhausted", "completion_unknown"],
            "recovery": "Resume, retry, compensate, roll forward or refuse according to typed state; never report ambiguous work as complete.",
        })
    return rows


def truth_obligations(truth: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for group in truth["groups"]:
        for item in group["items"]:
            rows.append({
                "record_id": f"obligation.truth.{item['id'].lower()}", "record_kind": "obligation", "edition": EDITION, "status": "candidate",
                "obligation_category": "truth_applicability", "truth_id": item["id"], "truth_group": group["group_id"],
                "name": item["name"],
                "decision_question": f"What is the explicit applicability and evidence posture for {item['name']}?",
                "satisfaction_evidence": ["owned contract or explicit condition", "executable or reviewed evidence", "residual owner and freshness"],
                "falsifier": "Silence, inherited vendor defaults, or an applicability label without reason/evidence.",
            })
    for category, ident, statement, falsifier in EXTRA_OBLIGATIONS:
        rows.append({
            "record_id": f"obligation.{category}.{ident}", "record_kind": "obligation", "edition": EDITION, "status": "candidate",
            "obligation_category": category, "name": ident.replace("_", " "), "decision_question": statement,
            "satisfaction_evidence": ["published contract", "conformance test", "runtime or review receipt"], "falsifier": falsifier,
        })
    return rows


def applicability(candidate: dict[str, Any], truth_id: str, group: str) -> tuple[str, dict[str, str]]:
    n = int(truth_id[1:])
    traits = set(candidate["traits"])
    verdict = candidate["boundary_evaluation"]["verdict"]
    if verdict == "merge" and n > 8:
        return "INAPPLICABLE", {"reason": "The proposed unit fails independent-product gates; these truths belong to its containing product or implementation contract."}
    if 87 <= n <= 96:
        return "CONDITIONAL", {"condition": "REQUIRED only for a Rust implementation or Rust-owned semantic surface; otherwise the chosen language/build contract applies.", "evidence_needed": "implementation owner, language target and build evidence"}
    if n == 43 and "model" not in traits:
        return "INAPPLICABLE", {"reason": "The candidate does not own or operate a predictive/statistical model lifecycle."}
    if n == 44:
        return "CONDITIONAL", {"condition": "REQUIRED if agentic tools are added; any autonomous business effect remains prohibited without explicit oversight.", "evidence_needed": "tool authority, limits, oversight and refusal tests"}
    if n in {33, 34, 35, 36} and "human_ui" not in traits:
        return "CONDITIONAL", {"condition": "REQUIRED only for a first-party human channel; API/embedded forms must publish equivalent consumer obligations.", "evidence_needed": "channel inventory and accessibility/recovery allocation"}
    if n in {37, 38, 39, 40, 41, 42} and "data" not in traits:
        return "CONDITIONAL", {"condition": "REQUIRED when the candidate persists, transforms or publishes enterprise data.", "evidence_needed": "data-flow and ownership inventory"}
    if n in {54, 55} and "data" not in traits:
        return "CONDITIONAL", {"condition": "REQUIRED when personal/regulated data or durable records enter scope.", "evidence_needed": "data classification and processing-purpose inventory"}
    if n == 58:
        return "CONDITIONAL", {"condition": "REQUIRED when cryptography protects an owned boundary; algorithms and keys remain external registries/providers.", "evidence_needed": "crypto purpose, agility and key-owner evidence"}
    if n in {59, 60, 62, 63, 64, 66, 67, 68} and "operated" not in traits:
        return "CONDITIONAL", {"condition": "The embedded engine owns correctness/resource/cancellation contracts; an operating wrapper owns service SLO and incident duties.", "evidence_needed": "deployment topology and operations allocation"}
    if n == 65 and not ({"operated", "stateful"} <= traits):
        return "INAPPLICABLE", {"reason": "The pure or stateless boundary owns no durable service state; its consumer must retain inputs and artifacts."}
    if n in {45, 46, 47, 50} and "authority" not in traits:
        return "CONDITIONAL", {"condition": "REQUIRED if the candidate issues decisions, approvals, grants, publications, recalls or effects.", "evidence_needed": "authority and effect inventory"}
    if n == 100:
        return "PROHIBITED", {"law": "Compatibility aliases that preserve obsolete product names or duplicate semantic owners are prohibited."}
    if n in {97, 98, 99}:
        return "UNDETERMINED", {"owner": "migration_architect", "evidence_needed": "live-source census and disposition cannot be completed before an implementation and predecessor are selected"}
    if n in {106, 107, 108, 109, 110}:
        return "UNDETERMINED", {"owner": "independent_appraiser", "evidence_needed": "independent appraisal, two-release vertical, unrelated-domain proof and residual-gap ownership"}
    return "REQUIRED", {"evidence_needed": "owned contract, scoped test/review evidence, freshness and residual owner"}


def make_truth_profiles(candidates: list[dict[str, Any]], truth: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    items = [(g["group_id"], i) for g in truth["groups"] for i in g["items"]]
    for candidate in candidates:
        ident = candidate["record_id"].split(".")[-1]
        for group, item in items:
            state, extra = applicability(candidate, item["id"], group)
            rows.append({
                "record_id": f"truth_profile.{ident}.{item['id'].lower()}", "record_kind": "truth_applicability", "edition": EDITION,
                "status": "candidate", "candidate_id": candidate["record_id"], "truth_id": item["id"], "truth_group": group,
                "applicability": state, "obligation_id": f"obligation.truth.{item['id'].lower()}", **extra,
            })
    return rows


def source_records() -> list[dict[str, Any]]:
    rows = []
    for ident, title, publisher, kind, uri, claim in SOURCE_SPECS:
        domains = []
        if ident.startswith("source.iso.") or ident.startswith("source.nist."):
            domains.append("product_service_lifecycle_and_assurance")
        if any(token in ident for token in ("kubernetes", "cncf", "opentelemetry", "prometheus", "slsa", "oci.", "kserve", "opa.")):
            domains.append("cloud_native_operator_contracts")
        if kind in {"open_standard", "standard", "industry_standard"} or any(token in ident for token in ("arrow", "iceberg", "delta", "hudi", "substrait", "openlineage")):
            domains.append("interoperability_and_portability")
        if any(token in ident for token in ("fowler", "opendataproduct", "opendatacontract", "cncf.platform")):
            domains.append("data_product_and_platform_literature")
        if kind in {"official_project", "official_product_docs"}:
            domains.append("specialist_implementation_evidence")
        if any(token in ident for token in ("iso.20000", "iso.15288", "google.sre", "finops", "cncf.platform", "nist.800_53a")):
            domains.append("enterprise_adoption_and_operations")
        rows.append({
            "record_id": ident, "record_kind": "evidence_source", "edition": EDITION, "status": "retrieved",
            "title": title, "publisher": publisher, "source_kind": kind, "authority": "primary_or_authoritative",
            "evidence_domains": sorted(set(domains)), "uri": uri, "claim": claim,
            "scope_limit": "Supports only the stated boundary or implementation claim; it does not ratify this portfolio.",
            "retrieved_at": AS_OF,
        })
    return rows


def innovations() -> list[dict[str, Any]]:
    return [{
        "record_id": f"innovation.{ident}", "record_kind": "non_llm_innovation", "edition": EDITION, "status": "researched_candidate",
        "year": year, "non_llm": True, "source_ids": [source], "innovation": claim,
        "boundary_impact": "Changes implementation or interoperability evidence; does not create a product merely by existing.",
    } for ident, year, source, claim in INNOVATIONS]


def boundary_assertions() -> list[dict[str, Any]]:
    rows = []
    for kind, definition, criterion, falsifier in BOUNDARY_KINDS:
        rows.append({
            "record_id": f"boundary_kind.{kind}", "record_kind": "boundary_assertion", "edition": EDITION, "status": "researched_candidate",
            "subject_kind": kind, "definition": definition, "acceptance_criterion": criterion, "falsifier": falsifier,
            "evidence_ids": ["source.iso.15288", "source.iso.20000", "source.fowler.data_product_design"],
        })
    gates = [
        ("independently_adoptable", "A consumer makes a separable adoption decision and reaches value through a stable contract."),
        ("independently_operable", "Health, capacity, failure, recovery and on-call responsibility are attributable to this promise."),
        ("independently_supportable", "Supported versions, severity, response and consumer/provider responsibilities are published."),
        ("billable_or_allocatable", "Usage and shared cost can be attributed without using repository or team proxies."),
        ("independently_exitable", "State, configuration, identity, evidence and active obligations can move to a substitute."),
        ("semantic_authority", "Owned meanings and effect authority are unique and published through stable interfaces."),
    ]
    for ident, criterion in gates:
        rows.append({
            "record_id": f"product_gate.{ident}", "record_kind": "boundary_assertion", "edition": EDITION, "status": "candidate",
            "subject_kind": "product_gate", "definition": criterion,
            "acceptance_criterion": "Named evidence exists and a negative/adversarial twin fails for the expected reason.",
            "falsifier": "The gate is asserted only from a vendor SKU, team, repository, deployment or bounded-context boundary.",
            "evidence_ids": ["source.iso.15288", "source.iso.20000", "source.google.sre.slo"],
        })
    return rows


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def upstream_inventory() -> list[dict[str, Any]]:
    paths: set[Path] = set((ROOT / "research/domain_atlas/universes").rglob("*"))
    paths.update((ROOT / "research/domain_atlas/compiler").rglob("*"))
    paths.update((ROOT / "research/product_ontology/adjudications").rglob("*"))
    paths.update((ROOT / "research/product_ontology/composition_pilots").rglob("*"))
    fixed = [
        ROOT / "research/domain_atlas/coverage-planes.jsonl",
        ROOT / "research/domain_atlas/context-families.json",
        ROOT / "research/domain_atlas/registry/context-candidates.jsonl",
        ROOT / "research/domain_atlas/compiler/compiler-metamodel.json",
        ROOT / "research/domain_atlas/universes/universe-coverage-audit.json",
        ROOT / "research/product_ontology/truth-contract.json",
        ROOT / "research/product_ontology/PRODUCT-BOUNDARY-THEORY.md",
        ROOT / "research/product_ontology/schema/product-graph.schema.json",
        ROOT / "research/product_ontology/registry/nodes.jsonl",
        ROOT / "research/product_ontology/registry/edges.jsonl",
        ROOT / "research/product_ontology/registry/evidence.jsonl",
    ]
    paths.update(fixed)
    for path in (ROOT / "research/domain_atlas").rglob("*"):
        if path.is_file() and any(k in path.name.lower() for k in ("librar", "provider")):
            paths.add(path)
    rows = []
    for path in sorted(p for p in paths if p.is_file() and "__pycache__" not in p.parts and p.suffix != ".pyc"):
        data = path.read_bytes()
        parse_status = "not_json"
        record_count = None
        if path.suffix == ".jsonl":
            try:
                parsed = [json.loads(line) for line in data.decode().splitlines() if line.strip()]
                parse_status, record_count = "valid_jsonl", len(parsed)
            except Exception:
                parse_status = "invalid_jsonl"
        elif path.suffix == ".json":
            try:
                json.loads(data)
                parse_status = "valid_json"
            except Exception:
                parse_status = "invalid_json"
        rows.append({
            "record_id": f"upstream_file.{hashlib.sha256(str(path.relative_to(ROOT)).encode()).hexdigest()[:16]}",
            "record_kind": "upstream_inventory", "edition": EDITION, "status": "observed",
            "path": str(path.relative_to(ROOT)), "sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data),
            "line_count": len(data.splitlines()), "parse_status": parse_status, "record_count": record_count,
        })
    return rows


def packaged_elements() -> list[dict[str, Any]]:
    inputs = [(ROOT / "research/domain_atlas/registry/context-candidates.jsonl", "context")]
    for path in sorted((ROOT / "research/domain_atlas/universes").rglob("*.jsonl")):
        name = path.name.lower()
        if "librar" in name:
            inputs.append((path, "library"))
        elif "provider-capabilit" in name:
            inputs.append((path, "provider"))
    for adjudication_libraries in sorted(
        (ROOT / "research/product_ontology/adjudications").glob("*/library-contracts.jsonl")
    ):
        inputs.append((adjudication_libraries, "library"))
    for compiler_library_file in sorted((ROOT / "research/domain_atlas/compiler").rglob("*.jsonl")):
        if compiler_library_file.name in {"library-boundaries.jsonl", "library-contributions.jsonl"}:
            inputs.append((compiler_library_file, "library"))
    inputs.append((ROOT / "research/domain_atlas/compiler/provider_target_registry/concrete-offers.jsonl", "provider"))
    rows = []
    keys = ["record_id", "library_id", "library_candidate_id", "provider_id", "provider_capability_id", "offer_id", "context_id"]
    for path, kind in inputs:
        for index, row in enumerate(load_jsonl(path), 1):
            upstream_id = next((str(row[k]) for k in keys if row.get(k)), f"line.{index}")
            digest = hashlib.sha256(f"{path.relative_to(ROOT)}:{upstream_id}".encode()).hexdigest()[:16]
            rows.append({
                "record_id": f"packaged.{kind}.{digest}", "record_kind": "packaged_element", "edition": EDITION, "status": "import_candidate",
                "element_kind": kind, "upstream_id": upstream_id, "upstream_ref": f"{path.relative_to(ROOT)}:{index}",
                "product_status": "not_a_product_by_origin",
                "admission_rule": "May be imported through a typed requirement/offer or published-language contract; product status requires independent six-gate evidence.",
                "must_not_own": ["product user outcome by repository placement", "suite packaging", "provider-name dispatch"],
            })
    return rows


def capability_imports(candidates: list[dict[str, Any]]) -> list[dict[str, Any]]:
    context_rows = load_jsonl(ROOT / "research/domain_atlas/registry/context-candidates.jsonl")
    by_term: dict[str, str] = {}
    for row in context_rows:
        by_term.setdefault(row.get("seed_term", ""), row["record_id"])
    rows = []
    for candidate in candidates:
        ident = candidate["record_id"].split(".")[-1]
        for idx, term in enumerate(FAMILY_IMPORTS[candidate["family"]], 1):
            rows.append({
                "record_id": f"capability_import.{ident}.{idx}", "record_kind": "capability_import", "edition": EDITION, "status": "candidate",
                "candidate_id": candidate["record_id"], "capability_id": f"capability.{slug(term)}",
                "semantic_context_ref": by_term.get(term), "requirement": f"Imports {term} through an editioned provider-neutral contract.",
                "binding_phase": "compile_time" if idx < 3 else "deployment_time", "cardinality": "one_or_more_qualified_offers",
                "refusal": "unresolved_context_or_no_qualified_offer", "ownership_law": "Import does not transfer semantic ownership to the product.",
            })
    return rows


def alternatives() -> list[dict[str, Any]]:
    return [{
        "record_id": f"alternative.{ident}", "record_kind": "alternative_decomposition", "edition": EDITION, "status": "adjudicated_candidate",
        "alternatives": options, "selected_index": selected, "decision": reason,
        "reopen_when": "New user/adoption/authority/SLO/exit evidence changes at least two split-test coordinates.",
        "evidence_ids": ["source.fowler.data_mesh", "source.iso.20000", "source.kubernetes.controller"],
    } for ident, options, selected, reason in ALTERNATIVES]


def substitutions() -> list[dict[str, Any]]:
    return [{
        "record_id": f"substitution.{ident}", "record_kind": "substitution", "edition": EDITION, "status": "candidate",
        "candidate_id": f"candidate.product.{candidate}", "provider_class": ident, "alternatives": providers,
        "qualification_contract": contract, "required_evidence": ["semantic conformance", "operational envelope", "security posture", "migration replay", "exit drill"],
        "not_equivalent_until": "All required semantics, versions, limits and evidence freshness close; brand-category similarity is insufficient.",
    } for ident, candidate, providers, contract in SUBSTITUTIONS]


def lifecycle(candidates: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [{
        "record_id": f"lifecycle.{row['record_id'].split('.')[-1]}", "record_kind": "lifecycle", "edition": EDITION, "status": "candidate",
        "candidate_id": row["record_id"], "states": ["hypothesis", "researched", "specified", "validated", "adoptable", "operating", "deprecated", "exiting", "retired"],
        "transitions": ["research_evidence", "boundary_adjudication", "contract_completion", "independent_validation", "adoption_receipt", "operations_receipt", "deprecation_notice", "exit_receipt", "retirement_attestation"],
        "compatibility_relations": ["backward_read", "forward_read", "write", "semantic", "operational", "evidence"],
        "change_gates": ["semantic_diff", "blast_radius", "migration_transform", "canary_or_parallel_run", "rollback_or_roll_forward", "historical_replay"],
        "refusals": ["missing_exit_plan", "unowned_inflight_work", "unproven_migration", "expired_provider_evidence"],
    } for row in candidates]


def incompatibilities() -> list[dict[str, Any]]:
    return [{
        "record_id": f"incompatibility.{ident}", "record_kind": "incompatibility", "edition": EDITION, "status": "candidate",
        "left_candidate_id": f"candidate.product.{left}", "right_candidate_id": f"candidate.product.{right}",
        "incompatibility": reason, "detection": "compiler semantic-owner/authority/compatibility check",
        "resolution": "refuse, narrow, translate through an explicit ACL, or select one authoritative owner; never silently coerce.",
    } for ident, left, right, reason in INCOMPATIBILITIES]


def industry_packs() -> list[dict[str, Any]]:
    rows = []
    for industry, case_id, products, method_contracts in PACKS:
        rows.append({
            "record_id": f"industry_pack.{industry}", "record_kind": "industry_solution_pack", "edition": EDITION, "status": "researched_candidate",
            "industry_id": industry, "example_case_ref": case_id, "horizontal_product": False,
            "composes_candidate_ids": [f"candidate.product.{p}" for p in products],
            "method_contract_refs": method_contracts,
            "method_adjudication_ref": "research/product_ontology/adjudications/analytical_methods/registry.jsonl",
            "owns_vertical": ["vertical vocabulary", "case population and grain", "local rules and thresholds", "decision authority", "acceptance evidence"],
            "imports_horizontal": ["product interfaces", "capability requirements", "provider-neutral methods", "runtime and exit obligations"],
            "non_ownership_law": "The pack cannot rename, fork or acquire horizontal product meanings; the same product contracts must compile for an unrelated industry.",
            "compiler_test": "Bind exact vertical contexts and source occurrences, then prove horizontal contracts unchanged and all authority/evidence gaps explicit.",
        })
    return rows


def gaps() -> list[dict[str, Any]]:
    return [{
        "record_id": f"gap.{ident}", "record_kind": "cannot_ratify_until", "edition": EDITION, "status": "open",
        "gap_class": cls, "statement": statement, "blocking_families": families,
        "closure_evidence": "Named owner, exact artifact/edition, executable or independent evidence, freshness and residual verdict.",
    } for ident, cls, statement, families in GAPS]


def schema_for(kind: str, required: list[str]) -> dict[str, Any]:
    props = {field: {} for field in required}
    props.update({
        "record_id": {"type": "string", "minLength": 3}, "record_kind": {"const": kind},
        "edition": {"type": "integer", "minimum": 1}, "status": {"type": "string", "minLength": 1},
    })
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema", "$id": f"https://san.example/product-boundary/{kind}.schema.json",
        "title": f"Global boundary research: {kind}", "type": "object", "required": required,
        "properties": props, "additionalProperties": True,
    }


DATASET_REQUIRED = {
    "boundary-assertions.jsonl": ("boundary_assertion", ["record_id", "record_kind", "edition", "status", "subject_kind", "definition", "acceptance_criterion", "falsifier", "evidence_ids"]),
    "product-archetypes.jsonl": ("product_boundary_candidate", ["record_id", "record_kind", "edition", "status", "name", "family", "archetype_kind", "sovereign_question", "positive_promise", "owned_meanings", "adoption_boundary", "operation_boundary", "support_boundary", "commercial_boundary", "exit_boundary", "boundary_evaluation", "falsifiers", "ratification"]),
    "user-jobs-outcomes.jsonl": ("user_job_outcome", ["record_id", "record_kind", "edition", "status", "candidate_id", "primary_users", "job", "measurable_outcomes", "harmed_parties", "falsifier"]),
    "service-blueprints.jsonl": ("service_blueprint", ["record_id", "record_kind", "edition", "status", "candidate_id", "journey_stages", "frontstage", "backstage", "evidence_at_handoffs", "failures", "recovery"]),
    "obligations.jsonl": ("obligation", ["record_id", "record_kind", "edition", "status", "obligation_category", "name", "decision_question", "satisfaction_evidence", "falsifier"]),
    "truth-applicability.jsonl": ("truth_applicability", ["record_id", "record_kind", "edition", "status", "candidate_id", "truth_id", "truth_group", "applicability", "obligation_id"]),
    "capability-imports.jsonl": ("capability_import", ["record_id", "record_kind", "edition", "status", "candidate_id", "capability_id", "requirement", "binding_phase", "cardinality", "refusal", "ownership_law"]),
    "packaged-elements.jsonl": ("packaged_element", ["record_id", "record_kind", "edition", "status", "element_kind", "upstream_id", "upstream_ref", "product_status", "admission_rule", "must_not_own"]),
    "substitutions.jsonl": ("substitution", ["record_id", "record_kind", "edition", "status", "candidate_id", "provider_class", "alternatives", "qualification_contract", "required_evidence", "not_equivalent_until"]),
    "lifecycle.jsonl": ("lifecycle", ["record_id", "record_kind", "edition", "status", "candidate_id", "states", "transitions", "compatibility_relations", "change_gates", "refusals"]),
    "incompatibilities.jsonl": ("incompatibility", ["record_id", "record_kind", "edition", "status", "left_candidate_id", "right_candidate_id", "incompatibility", "detection", "resolution"]),
    "evidence.jsonl": ("evidence_source", ["record_id", "record_kind", "edition", "status", "title", "publisher", "source_kind", "authority", "evidence_domains", "uri", "claim", "scope_limit", "retrieved_at"]),
    "innovations.jsonl": ("non_llm_innovation", ["record_id", "record_kind", "edition", "status", "year", "non_llm", "source_ids", "innovation", "boundary_impact"]),
    "alternative-decompositions.jsonl": ("alternative_decomposition", ["record_id", "record_kind", "edition", "status", "alternatives", "selected_index", "decision", "reopen_when", "evidence_ids"]),
    "industry-solution-packs.jsonl": ("industry_solution_pack", ["record_id", "record_kind", "edition", "status", "industry_id", "example_case_ref", "horizontal_product", "composes_candidate_ids", "method_contract_refs", "method_adjudication_ref", "owns_vertical", "imports_horizontal", "non_ownership_law", "compiler_test"]),
    "gaps.jsonl": ("cannot_ratify_until", ["record_id", "record_kind", "edition", "status", "gap_class", "statement", "blocking_families", "closure_evidence"]),
    "upstream-inventory.jsonl": ("upstream_inventory", ["record_id", "record_kind", "edition", "status", "path", "sha256", "bytes", "line_count", "parse_status"]),
}


def dumps_jsonl(rows: list[dict[str, Any]]) -> str:
    return "".join(json.dumps(row, sort_keys=True, separators=(",", ":")) + "\n" for row in rows)


def build_outputs() -> dict[Path, str]:
    truth = json.loads((ROOT / "research/product_ontology/truth-contract.json").read_text(encoding="utf-8"))
    candidates = make_candidates()
    datasets: dict[str, list[dict[str, Any]]] = {
        "boundary-assertions.jsonl": boundary_assertions(),
        "product-archetypes.jsonl": candidates,
        "user-jobs-outcomes.jsonl": make_user_jobs(),
        "service-blueprints.jsonl": make_blueprints(),
        "obligations.jsonl": truth_obligations(truth),
        "truth-applicability.jsonl": make_truth_profiles(candidates, truth),
        "capability-imports.jsonl": capability_imports(candidates),
        "packaged-elements.jsonl": packaged_elements(),
        "substitutions.jsonl": substitutions(),
        "lifecycle.jsonl": lifecycle(candidates),
        "incompatibilities.jsonl": incompatibilities(),
        "evidence.jsonl": source_records(),
        "innovations.jsonl": innovations(),
        "alternative-decompositions.jsonl": alternatives(),
        "industry-solution-packs.jsonl": industry_packs(),
        "gaps.jsonl": gaps(),
        "upstream-inventory.jsonl": upstream_inventory(),
    }
    outputs = {HERE / name: dumps_jsonl(rows) for name, rows in datasets.items()}
    for name, (kind, required) in DATASET_REQUIRED.items():
        schema = schema_for(kind, required)
        outputs[HERE / "schemas" / name.replace(".jsonl", ".schema.json")] = json.dumps(schema, indent=2, sort_keys=True) + "\n"
    counts = {name: len(rows) for name, rows in datasets.items()}
    counts["truth_dimensions"] = 110
    counts["primary_or_authoritative_sources"] = sum(1 for row in datasets["evidence.jsonl"] if row["authority"] == "primary_or_authoritative")
    counts["schemas"] = len(DATASET_REQUIRED)
    report = {
        "report_id": "global_product_boundary_coverage", "edition": EDITION, "as_of": AS_OF,
        "status": "research_candidate_not_ratified", "completion_claim": False,
        "counts": counts,
        "laws": [
            "No candidate record is a ratified product.",
            "Counts describe research records, never a final product count.",
            "Every candidate has exactly one applicability record for T001 through T110.",
            "Industry packs compose horizontal products and do not become horizontal products.",
            "Every product defaults to deterministic core execution; model and agent modalities are explicit per-use-site extensions, never semantic owners or hidden authority.",
            "Removing all model and agent extensions preserves deterministic parsing, typing, planning, authorization, qualification, effects and evidence; explicitly requested assistance may fail as capability_unavailable.",
            "Models and agents may accelerate research and propose typed artifacts, but never replace exhaustive domain work, evidence, qualification, executable laws or acceptance.",
            "Statistical, probabilistic, predictive, heuristic, simulation and optimization methods remain first-class; their uncertainty and approximation are explicit and do not turn them into ambient AI products.",
        ],
    }
    outputs[HERE / "coverage-report.json"] = json.dumps(report, indent=2, sort_keys=True) + "\n"
    return outputs


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="Fail if generated files differ from deterministic output")
    args = parser.parse_args()
    outputs = build_outputs()
    mismatches = []
    for path, content in outputs.items():
        if args.check:
            if not path.exists() or path.read_text(encoding="utf-8") != content:
                mismatches.append(str(path.relative_to(ROOT)))
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
    if mismatches:
        for path in mismatches:
            print(f"STALE {path}")
        return 1
    action = "CHECK" if args.check else "BUILD"
    print(f"{action} PASS: {len(outputs)} deterministic outputs")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
