#!/usr/bin/env python3
"""Build bounded primary-evidence candidates for the state/change axis."""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
SEM = HERE.parent
TARGETS = SEM / "structured_projection/targeted-evidence-work-packages.jsonl"
AS_OF = "2026-08-27"
sys.path.insert(0, str(SEM))

from axis_evidence_campaign import build_campaign, campaign_outputs, write_outputs  # noqa: E402


CLAIMS: dict[str, dict[str, Any]] = {
    "constitution.family.application_behavior": {
        "title": "State Chart XML (SCXML) 1.0",
        "publisher": "W3C",
        "url": "https://www.w3.org/TR/scxml/",
        "claim": "SCXML transition processing distinguishes current configuration, enabled transitions, exit and entry sets, executable content, event queues and the resulting stable configuration.",
        "coordinates": ["current_configuration", "triggering_event", "enabled_transition_set", "exit_set", "entry_set", "resulting_configuration"],
        "limit": "SCXML defines a state-machine notation and processing algorithm; it does not prove domain invariants, storage durability, business authorization, exactly-once effects or equivalence with an application's aggregate lifecycle.",
        "negative": "receiving an event, selecting a transition, persisting aggregate state and completing every external effect are one atomic state change",
    },
    "constitution.family.analytical_method_kernels": {
        "title": "OCEL 2.0 Specification",
        "publisher": "OCEL Standard",
        "url": "https://www.ocel-standard.org/2.0/ocel20_specification.pdf",
        "claim": "OCEL 2.0 records object-attribute values with timestamps so an object's attribute value can be reconstructed at a time; events and object-to-object or event-to-object relations remain distinct from those state observations.",
        "coordinates": ["object", "attribute", "time_stamped_attribute_value", "event", "qualified_relation"],
        "limit": "OCEL specifies an event-log representation for object-centric analysis; it does not prove that reconstructed attribute values are complete world state, or define every case, diagnosis, causal transition or business lifecycle.",
        "negative": "a time-stamped object attribute value is the same thing as an event, a process case, or an authorized domain-state transition",
    },
    "constitution.family.predictive_analytics": {
        "title": "Model Registry Workflows",
        "publisher": "MLflow",
        "url": "https://mlflow.org/docs/latest/ml/model-registry/workflow/",
        "claim": "MLflow creates distinct numbered model versions and permits mutable aliases and tags to be assigned, updated or deleted independently; loading by alias resolves whichever version currently owns that alias.",
        "coordinates": ["registered_model", "immutable_version_reference", "mutable_alias_assignment", "mutable_tag", "loaded_artifact"],
        "limit": "MLflow registry behavior does not establish model validity, approval authority, deployment truth, prediction correctness, drift state or universal MLOps lifecycle semantics.",
        "negative": "reassigning a champion alias mutates the underlying model version or proves that it is approved and deployed",
    },
    "constitution.family.shared_semantic_foundations": {
        "title": "Constraints of the PROV Data Model",
        "publisher": "W3C",
        "url": "https://www.w3.org/TR/prov-constraints/",
        "claim": "PROV distinguishes Entity generation and invalidation, Activity start and end, use, derivation, specialization and revision, with ordering constraints that delimit entity and activity lifetimes.",
        "coordinates": ["entity", "activity", "generation", "usage", "invalidation", "specialization_or_revision"],
        "limit": "PROV constrains provenance descriptions; it does not make a described event true, define domain authorization, or equate revision, invalidation, deletion and legal erasure.",
        "negative": "entity revision, invalidation, physical deletion and retraction of an assertion are one universal transition",
    },
    "constitution.family.quality_reconciliation": {
        "title": "Shapes Constraint Language (SHACL)",
        "publisher": "W3C",
        "url": "https://www.w3.org/TR/shacl/",
        "claim": "SHACL validation maps a data graph and shapes graph to a separate validation report containing a conformance result and validation results; the report may guide fixes but validation itself is not a repair operation.",
        "coordinates": ["data_graph_edition", "shapes_graph_edition", "validation_execution", "validation_report", "repair_or_waiver"],
        "limit": "SHACL defines RDF graph validation, not source correction authority, reconciliation finality, fitness for every use, or the lifecycle of non-RDF quality cases.",
        "negative": "producing a non-conforming validation report mutates the data graph or authorizes a repair",
    },
    "constitution.family.candidate_data_shapes": {
        "title": "FHIR R5 RESTful API",
        "publisher": "HL7",
        "url": "https://hl7.org/fhir/R5/http.html",
        "claim": "FHIR separates a resource logical id from version ids, current-state read from version-specific read, and create, update, patch, delete and history interactions; update creates a new current version when versioning is supported.",
        "coordinates": ["logical_resource", "resource_version", "current_version", "history_entry", "interaction_outcome"],
        "limit": "FHIR specifies lifecycle behavior for FHIR server resources and permits servers without full version support; it does not define the clinical subject's real-world state or every document and media lifecycle.",
        "negative": "a FHIR resource version is the patient or clinical event itself, and deleting the resource proves deletion of all underlying information",
    },
    "constitution.family.optional_model_agent_extensions": {
        "title": "Model Context Protocol resources",
        "publisher": "Model Context Protocol",
        "url": "https://modelcontextprotocol.io/specification/2025-06-18/server/resources",
        "claim": "MCP distinguishes the resource list from an individual resource and defines optional list-changed notifications and subscriptions to resource updates; notification support is explicitly capability-negotiated.",
        "coordinates": ["resource_list", "resource_definition", "resource_content", "list_changed_notification", "resource_updated_notification", "subscription"],
        "limit": "MCP signals transport-visible resource changes; it does not define content identity, immutable versions, source truth, domain mutation, authorization or safe model action.",
        "negative": "receiving resources/updated proves that the represented business object changed correctly or that an agent may act on it",
    },
    "constitution.family.query_compilation_execution": {
        "title": "Trino client protocol",
        "publisher": "Trino",
        "url": "https://trino.io/docs/current/client/client-protocol.html",
        "claim": "A Trino query progresses through submitted processing and paged result retrieval until a final response; failure to fetch can cancel a query, while spooling can make cluster execution completion independent of client retrieval completion.",
        "coordinates": ["query_submission", "query_execution", "result_page_or_segment", "query_terminal_outcome", "client_consumption_completion"],
        "limit": "Trino client protocol states do not define transaction commit, downstream delivery acceptance, semantic result correctness or cross-engine query lifecycle equivalence.",
        "negative": "query execution finished, all result data consumed and downstream business effect accepted are the same terminal state",
    },
    "constitution.family.consumption_bi_visualization": {
        "title": "Vega Signals",
        "publisher": "Vega Project",
        "url": "https://vega.github.io/vega/docs/signals/",
        "claim": "Vega signals are scoped reactive variables whose values can update from event streams, external calls or upstream signals, then propagate through the specification and trigger re-rendering.",
        "coordinates": ["input_event", "signal_value", "signal_dependency", "view_re_evaluation", "rendered_view"],
        "limit": "Vega defines visualization interaction state; it does not establish source-data mutation, persisted user intent, analytical truth or domain workflow completion.",
        "negative": "a reactive signal update mutates the source dataset or records an authorized business decision",
    },
    "constitution.family.lineage_provenance_evidence": {
        "title": "The OpenLineage Run Cycle",
        "publisher": "OpenLineage",
        "url": "https://openlineage.io/docs/spec/run-cycle/",
        "claim": "OpenLineage run-state updates distinguish START, RUNNING, COMPLETE, ABORT, FAIL and OTHER; terminality and event completeness vary by processing type, and accumulative events may require combination to reconstruct run information.",
        "coordinates": ["job_definition", "run", "run_state_update", "terminal_event", "accumulated_or_snapshot_evidence"],
        "limit": "OpenLineage captures reported run lifecycle and metadata; it does not prove that execution effects occurred, datasets are correct, lineage is complete, or a business process accepted the result.",
        "negative": "a COMPLETE RunEvent proves complete lineage, correct outputs and accepted downstream effects",
    },
    "constitution.family.persistence_lakehouse": {
        "title": "Apache Iceberg Specification",
        "publisher": "Apache Iceberg",
        "url": "https://iceberg.apache.org/spec/",
        "claim": "Iceberg changes table state by atomically replacing table metadata, producing snapshots with append, replace, overwrite or delete operation summaries while retaining immutable data and metadata files until lifecycle cleanup.",
        "coordinates": ["table_metadata_edition", "current_snapshot", "snapshot_operation", "manifest_entry_status", "physical_file_retention"],
        "limit": "Iceberg defines table-format state and optimistic commit behavior; it does not define business-event semantics, source authorization, logical deletion outside the table or acceptance of derived data.",
        "negative": "an Iceberg replace operation changes table data, or a logical delete means every referenced physical byte was immediately erased",
    },
    "constitution.family.runtime_resource_control": {
        "title": "Kubernetes Controllers",
        "publisher": "Kubernetes",
        "url": "https://kubernetes.io/docs/concepts/architecture/controller/",
        "claim": "Kubernetes controllers continuously compare resource spec desired state with observed current state, request effects to reduce the difference, and report current state; several controllers may manage different aspects without global stability.",
        "coordinates": ["desired_state", "observed_state", "reconciliation_iteration", "requested_effect", "reported_status"],
        "limit": "Kubernetes reconciliation describes cluster-resource control, not application-domain acceptance, business transaction success, irreversible external effects or universal convergence.",
        "negative": "writing desired state proves the effect occurred, and reported status proves the application outcome was accepted",
    },
    "constitution.family.representation_codec": {
        "title": "Apache Arrow Columnar Format: IPC",
        "publisher": "Apache Arrow",
        "url": "https://arrow.apache.org/docs/format/Columnar.html#serialization-and-interprocess-communication-ipc",
        "claim": "An Arrow IPC stream starts with a schema followed by record and dictionary batches; the schema governs following record batches, while dictionary replacement and delta behavior differs between stream and file encodings.",
        "coordinates": ["ipc_stream_or_file", "schema_message", "record_batch_message", "dictionary_edition", "end_of_stream_or_footer"],
        "limit": "Arrow defines representation sequencing and compatibility constraints, not domain-object mutation, source history, record truth or business schema governance.",
        "negative": "receiving another record batch changes the domain schema, and dictionary replacement is a business-state transition",
    },
    "constitution.family.semantic_metrics_formulas": {
        "title": "Creating metrics",
        "publisher": "dbt Labs",
        "url": "https://docs.getdbt.com/docs/build/metrics-overview",
        "claim": "dbt represents metric definitions as YAML nodes with named types, expressions and dependencies, while MetricFlow evaluates those definitions over semantic models; simple, cumulative, derived, ratio and conversion definitions have different dependency structures.",
        "coordinates": ["metric_definition", "formula_or_aggregation", "dependency_graph", "query_evaluation", "computed_metric_value"],
        "limit": "dbt configuration documents one semantic-layer implementation; it does not supply universal formula version identity, approval workflow, observation validity or compatibility law between definition editions.",
        "negative": "recomputing a metric value changes its formula definition, or editing a formula retroactively mutates prior observations without an explicit edition policy",
    },
    "constitution.family.platform_commercial_support": {
        "title": "TMF622 Product Ordering Management API v5.0.0",
        "publisher": "TM Forum",
        "url": "https://github.com/tmforum-apis/TMF622_ProductOrder/blob/main/TMF622-ProductOrdering-v5.0.0.oas.yaml",
        "claim": "TMF622 models ProductOrder and order-item state, cancellation tasks, partial updates and lifecycle notifications separately from the product offering referenced by the order and the product action requested.",
        "coordinates": ["product_offering_reference", "product_order", "order_item", "order_state_change_event", "cancellation_task", "requested_product_action"],
        "limit": "TMF622 specifies telecom ordering API resources; order state does not prove fulfillment, realized product-inventory state, billing settlement or universal commercial lifecycle semantics.",
        "negative": "an order marked complete is the realized product, proves service activation and establishes payment settlement",
    },
    "constitution.family.messaging_coordination": {
        "title": "KafkaConsumer offsets and consumer position",
        "publisher": "Apache Kafka",
        "url": "https://kafka.apache.org/41/javadoc/org/apache/kafka/clients/consumer/KafkaConsumer.html",
        "claim": "Kafka distinguishes immutable partition record offsets, the consumer's current fetch position and the separately persisted committed position used for recovery; applications choose when processing is sufficient to commit progress.",
        "coordinates": ["partition_record_offset", "consumer_fetch_position", "application_processing", "committed_recovery_position", "rebalance_or_restart"],
        "limit": "Kafka consumer positions describe log progress, not business-effect atomicity, recipient acceptance, global ordering, record truth or universal exactly-once outcomes.",
        "negative": "fetching a record, processing it, committing its offset and accepting every downstream effect are one atomic state transition",
    },
    "constitution.family.operations_research": {
        "title": "CP-SAT Solver",
        "publisher": "Google OR-Tools",
        "url": "https://developers.google.com/optimization/cp/cp_solver",
        "claim": "CP-SAT returns distinct OPTIMAL, FEASIBLE, INFEASIBLE, MODEL_INVALID and UNKNOWN statuses; FEASIBLE does not prove optimality and UNKNOWN does not prove infeasibility.",
        "coordinates": ["model_definition", "solve_attempt", "solver_status", "feasible_assignment", "optimality_or_infeasibility_proof"],
        "limit": "CP-SAT status describes one solver run over an encoded model; it does not establish model fidelity, scenario authority, policy compliance or authorization to enact a solution.",
        "negative": "FEASIBLE means OPTIMAL, UNKNOWN means INFEASIBLE, or any returned assignment is an authorized business action",
    },
    "constitution.family.security_privacy_trust": {
        "title": "RFC 7009: OAuth 2.0 Token Revocation",
        "publisher": "IETF",
        "url": "https://www.rfc-editor.org/rfc/rfc7009.html",
        "claim": "OAuth token revocation lets a client request invalidation of an access or refresh token and may invalidate related tokens or the underlying authorization grant, with propagation behavior constrained by the authorization server.",
        "coordinates": ["authorization_grant", "access_or_refresh_token", "revocation_request", "invalidated_credential", "propagation_to_related_tokens"],
        "limit": "RFC 7009 defines OAuth credential revocation, not deletion of protected resources, retraction of historical claims, consent semantics, legal erasure or universal authorization lifecycle.",
        "negative": "revoking a token deletes the protected data, retracts prior actions or proves immediate enforcement in every downstream system",
    },
    "constitution.family.pipeline_dataflow": {
        "title": "Apache Beam Programming Guide",
        "publisher": "Apache Beam",
        "url": "https://beam.apache.org/documentation/programming-guide/",
        "claim": "Beam PCollections are logically immutable and transforms create new output PCollections; bounded and unbounded collections, windows, triggers, state and timers govern when runtime results are emitted or revisited.",
        "coordinates": ["pipeline_definition", "input_pcollection", "transform_application", "output_pcollection", "keyed_window_state", "runner_job"],
        "limit": "Beam specifies dataflow construction and runtime semantics; replay, trigger firing or runner completion does not establish source mutation, sink-effect acceptance or domain-event finality.",
        "negative": "a transform mutates its input PCollection, or replaying a bundle means the source business event happened again",
    },
    "constitution.family.governance_metadata_ontology": {
        "title": "Data Catalog Vocabulary Version 3",
        "publisher": "W3C",
        "url": "https://www.w3.org/TR/vocab-dcat-3/",
        "claim": "DCAT distinguishes abstract resources, versioned snapshots, current and previous versions, ordered dataset-series members and catalog records whose registration metadata can change independently of the described resource.",
        "coordinates": ["abstract_cataloged_resource", "resource_version", "current_version_relation", "dataset_series_member", "catalog_record_edition"],
        "limit": "DCAT describes catalog metadata and version relations; it does not prove dataset contents, source-system history, semantic compatibility, ownership or that catalog-record modification changed the dataset.",
        "negative": "the previous member of a dataset series is necessarily the previous version of one resource, or changing a catalog record changes the dataset",
    },
    "constitution.family.geospatial_analytics": {
        "title": "OGC API - Features - Part 4: Create, Replace, Update and Delete",
        "publisher": "Open Geospatial Consortium",
        "url": "https://github.com/opengeospatial/ogcapi-features/blob/master/extensions/transactions/create-replace-update-delete/standard/20-002.adoc",
        "claim": "OGC API Features Part 4 separates collection-level creation from resource-level replacement, property update and deletion of geospatial feature resources, each with distinct HTTP preconditions and outcomes.",
        "coordinates": ["feature_collection", "feature_resource", "create", "replace", "partial_update", "delete"],
        "limit": "The candidate transaction specification governs feature-resource API operations; it does not equate feature representation with the real-world feature, define all geometry histories or authorize physical-world change.",
        "negative": "replacing a feature resource proves the real-world feature changed, and deleting it proves all historical geometry and evidence were erased",
    },
    "constitution.family.connector_protocol": {
        "title": "Debezium connector for PostgreSQL: incremental snapshots",
        "publisher": "Debezium",
        "url": "https://debezium.io/documentation/reference/stable/connectors/postgresql.html",
        "claim": "Debezium incremental snapshots are requested by a signal, process table chunks inside snapshot windows, reconcile concurrent change-stream events and can resume without treating the snapshot as one indivisible event.",
        "coordinates": ["snapshot_request", "snapshot_execution", "chunk_window", "concurrent_change_event", "resume_position", "snapshot_completion"],
        "limit": "Debezium documents one connector's capture lifecycle; snapshot progress does not establish source-transaction truth, target application, global consistency or business-process state.",
        "negative": "snapshot completion is source-system quiescence, and replay or resume means the business transaction occurred again",
    },
    "constitution.family.forecasting_lifecycle": {
        "title": "Time series cross-validation",
        "publisher": "Forecasting: Principles and Practice (3rd ed.)",
        "url": "https://otexts.com/fpp3/tscv.html",
        "claim": "Rolling-origin evaluation creates successive training sets using only prior observations, produces forecasts at a defined origin and evaluates them against later test observations; the origin and evidence available therefore change over time.",
        "coordinates": ["observation_history_as_of", "forecast_origin", "forecast_edition", "later_actual_observation", "evaluation_error"],
        "limit": "The method defines evaluation timing, not forecast publication, override, approval, supersession, reconciliation or enterprise decision lifecycle.",
        "negative": "a later actual observation mutates the earlier forecast, or an ex-post evaluation is the same artifact as the ex-ante forecast",
    },
    "constitution.family.experimentation_lifecycle": {
        "title": "Make a Decision",
        "publisher": "Statsig",
        "url": "https://docs.statsig.com/experiments/ending/make-decision",
        "claim": "Statsig separates collecting and updating experiment results from making a decision; the decision can ship a selected group, after which results remain accessible but stop updating.",
        "coordinates": ["experiment_definition", "assignment_or_exposure", "evidence_accumulation", "decision", "shipped_group", "retained_results"],
        "limit": "Statsig describes one platform's experiment-ending workflow; it does not prove causal validity, decision authority, rollout safety or that an exposure event is a lifecycle transition.",
        "negative": "an exposure or statistically favorable result is itself a ship decision, and concluding an experiment is identical to deploying code everywhere",
    },
}


def build() -> dict[str, Any]:
    return build_campaign(
        axis="state_and_change",
        campaign_key="p3s",
        program_id="program.p3s.state-change-evidence.v1",
        claims=CLAIMS,
        targets_path=TARGETS,
        as_of=AS_OF,
    )


def outputs() -> dict[str, str]:
    return campaign_outputs(
        built=build(),
        manifest_id="manifest.p3s.state-change-evidence.v1",
        as_of=AS_OF,
    )


def main() -> int:
    write_outputs(HERE, outputs())
    summary = build()["summary"]
    print(
        "BUILD PASS P3S state/change: "
        f"{summary['primary_evidence_candidates']} bounded candidates route "
        f"{summary['represented_library_occurrences']} library occurrences; "
        "owner decisions and gap closures remain zero"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
