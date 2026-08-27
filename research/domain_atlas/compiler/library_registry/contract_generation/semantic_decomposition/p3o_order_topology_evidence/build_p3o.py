#!/usr/bin/env python3
"""Build bounded primary-evidence candidates for the order/topology axis."""
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
        "title": "Business Process Model and Notation (BPMN) 2.0.2",
        "publisher": "Object Management Group",
        "url": "https://www.omg.org/spec/BPMN/2.0.2",
        "claim": "BPMN distinguishes sequence flow within a process from message flow between participants and uses gateways to express branching, merging, forking and joining rather than treating every drawn edge as one order relation.",
        "coordinates": ["process", "participant", "activity", "sequence_flow", "message_flow", "gateway_split_or_join"],
        "limit": "BPMN specifies process notation and execution-related semantics; it does not establish domain-event global order, message delivery guarantees, aggregate consistency or provider portability.",
        "negative": "sequence flow, message flow, causal order, delivery order and transaction commit order are interchangeable",
    },
    "constitution.family.analytical_method_kernels": {
        "title": "Transforming Object-Centric Event Logs to Temporal Event Knowledge Graphs (Extended Version)",
        "publisher": "Shahrzad Khayatbashi, Olaf Hartig and Amin Jalali",
        "url": "https://arxiv.org/abs/2406.07596",
        "claim": "The tEKG paper represents events, objects, their relationships and time-varying object-attribute snapshots as a temporal graph and gives a conversion from OCEL 2.0; temporal snapshots and graph adjacency therefore carry different ordering information from a flat event sequence.",
        "coordinates": ["event_object_incidence", "object_relation_topology", "attribute_snapshot_time", "event_sequence_candidate", "derived_process_order"],
        "limit": "The paper proposes one process-mining representation and conversion. It does not establish that timestamp order is causal order, choose a case notion, prove completeness of captured state, or define every directly-follows and conformance topology.",
        "negative": "sorting all events by timestamp yields the one true case order, causal order and object-state transition order",
    },
    "constitution.family.predictive_analytics": {
        "title": "Open Neural Network Exchange Intermediate Representation (ONNX IR) Specification",
        "publisher": "ONNX",
        "url": "https://onnx.ai/onnx/repo-docs/IR.html",
        "claim": "ONNX represents a computation as an acyclic data-dependency graph whose serialized node list must be topologically sorted and whose output names satisfy single static assignment; ordered lists, sets and bags remain distinct container kinds in the IR.",
        "coordinates": ["data_dependency_dag", "topological_serialization", "single_producer_name", "ordered_operand_or_result_list", "unordered_collection_kind"],
        "limit": "ONNX constrains portable model representation. It does not prove that one valid topological serialization is the only execution schedule, encode business causality, establish model quality, or order independent predictions.",
        "negative": "the serialized node order is a total causal order and every reorder changes the predictive model's meaning",
    },
    "constitution.family.shared_semantic_foundations": {
        "title": "RDF 1.1 Concepts and Abstract Syntax",
        "publisher": "W3C",
        "url": "https://www.w3.org/TR/rdf11-concepts/",
        "claim": "An RDF graph is a set of triples rather than a sequence; when order is part of meaning it must be represented explicitly, for example with RDF collections rather than inferred from an RDF serialization's statement order.",
        "coordinates": ["unordered_graph", "directed_labeled_edge", "explicit_collection_order", "serialization_order", "graph_isomorphism"],
        "limit": "RDF supplies a graph data model and explicit collection vocabulary. It does not choose a domain hierarchy, causal relation, workflow order, graph traversal order, or canonical serialization for SAN.",
        "negative": "the order of triples in Turtle or JSON-LD is semantic graph order and therefore supplies workflow or causal precedence",
    },
    "constitution.family.quality_reconciliation": {
        "title": "Shapes Constraint Language (SHACL)",
        "publisher": "W3C",
        "url": "https://www.w3.org/TR/shacl/",
        "claim": "SHACL distinguishes ordered sequence paths from alternative and repeated graph paths, while a validation report contains the set of all validation results linked to focus nodes, source shapes and result paths.",
        "coordinates": ["constraint_path_sequence", "alternative_graph_path", "focus_node", "validation_result_set", "result_detail_relation"],
        "limit": "SHACL defines RDF graph validation topology. It does not make validation-result enumeration order significant, order repairs, choose reconciliation precedence, or establish causal root-cause chains.",
        "negative": "the order in which a validator emits failures is constraint precedence, repair order or severity order",
    },
    "constitution.family.candidate_data_shapes": {
        "title": "JSON Schema: A Media Type for Describing JSON Documents, Draft 2020-12",
        "publisher": "JSON Schema",
        "url": "https://json-schema.org/draft/2020-12/json-schema-core.html",
        "claim": "The JSON data model treats arrays as ordered sequences and object properties as unordered name-value members; schema references and applicators add a separate schema-resource graph from instance containment.",
        "coordinates": ["array_position", "unordered_object_member", "instance_containment", "schema_reference_graph", "evaluation_path"],
        "limit": "JSON Schema constrains JSON instances and schema evaluation. It does not make object serialization order meaningful, define domain aggregation hierarchies, or infer causal and temporal order from nested structure.",
        "negative": "JSON object member order is semantic and object nesting automatically means ownership, chronology or workflow precedence",
    },
    "constitution.family.persistence_lakehouse": {
        "title": "Apache Iceberg Specification",
        "publisher": "Apache Iceberg",
        "url": "https://iceberg.apache.org/spec/",
        "claim": "Iceberg snapshot sequence numbers monotonically track the order of committed table changes, while data and file sequence numbers capture different relative ages and sort-order identifiers separately describe ordering within data files.",
        "coordinates": ["snapshot_commit_sequence", "snapshot_parent_relation", "data_sequence_age", "file_addition_sequence", "declared_sort_order"],
        "limit": "These are table-format ordering coordinates. They do not establish source transaction order across tables, row causality, business-event order, physical file-list significance, or one global lakehouse timeline.",
        "negative": "snapshot sequence, file sequence, data age, manifest position, row sort order and business-event time are one universal order",
    },
    "constitution.family.lineage_provenance_evidence": {
        "title": "Constraints of the PROV Data Model",
        "publisher": "W3C",
        "url": "https://www.w3.org/TR/prov-constraints/",
        "claim": "PROV uses a preorder and strict-precedence constraints among generation, usage, invalidation, start and end events, allowing consistency checking without requiring a physical-clock total order.",
        "coordinates": ["precedes_preorder", "strict_precedence", "activity_lifetime", "entity_lifetime", "derivation_order_constraint"],
        "limit": "PROV constrains credible provenance descriptions. It does not guarantee that recorded provenance is complete or true, turn influence into direct causation, or impose a total order on concurrent events.",
        "negative": "a provenance edge or timestamp defines a complete causal total order and every pair of events must be comparable",
    },
    "constitution.family.optional_model_agent_extensions": {
        "title": "Model Context Protocol: Resources",
        "publisher": "Model Context Protocol",
        "url": "https://modelcontextprotocol.io/specification/2025-06-18/server/resources",
        "claim": "MCP resources are individually identified by URIs and discovered through cursor-paginated lists or URI templates; optional subscriptions relate a client to changes of a specific resource independently of list position.",
        "coordinates": ["resource_identity_uri", "opaque_pagination_position", "resource_template_expansion", "subscription_relation", "list_membership"],
        "limit": "MCP defines a context-exchange protocol. It does not give URI path segments or pagination order ontology semantics, rank resources by truth, or define agent-plan causality and tool-call dependency graphs.",
        "negative": "resource list order, cursor position or URI path is a semantic hierarchy, relevance ranking or agent execution plan",
    },
    "constitution.family.query_compilation_execution": {
        "title": "Substrait Logical Relations",
        "publisher": "Substrait",
        "url": "https://substrait.io/relations/logical_relations/",
        "claim": "Substrait separates relation-input topology, ordinal field order and declared row orderedness: Sort explicitly changes orderedness, Fetch preserves it, and several operators may clear or remap it.",
        "coordinates": ["relation_input_graph", "field_ordinal_order", "row_orderedness_property", "sort_key_precedence", "distribution_topology"],
        "limit": "Substrait specifies portable relational plans. It does not make plan serialization order equal row order, preserve orderedness through every operator, or encode business causality and transaction order.",
        "negative": "relation-tree traversal order, output column order and result-row order are the same contract",
    },
    "constitution.family.consumption_bi_visualization": {
        "title": "Vega Marks",
        "publisher": "Vega Project",
        "url": "https://vega.github.io/vega/docs/marks/",
        "claim": "Vega distinguishes scenegraph item sort from z-index layering and group-mark nesting; mark sort can set default rendering order while z-index changes layering without changing item order.",
        "coordinates": ["scenegraph_containment", "mark_item_order", "render_layer_zindex", "data_binding_key", "visual_group_scope"],
        "limit": "Vega defines visualization scenegraph and rendering behavior. It does not make screen layering a data sort, business priority, analytical rank, accessibility reading order, or source-system hierarchy.",
        "negative": "z-index, scenegraph nesting, data order, analytical ranking and user reading order are interchangeable",
    },
    "constitution.family.runtime_resource_control": {
        "title": "Kubernetes Controllers",
        "publisher": "Kubernetes",
        "url": "https://kubernetes.io/docs/concepts/architecture/controller/",
        "claim": "Kubernetes uses many control loops that each manage a particular aspect of state and may observe one another's reported data; the cluster can keep changing without reaching one globally stable or serially ordered state.",
        "coordinates": ["controller_dependency", "desired_observed_relation", "reconciliation_iteration", "managed_resource_topology", "concurrent_control_loops"],
        "limit": "Kubernetes documents cluster control architecture. It does not define a universal controller execution order, business-workflow precedence, causal proof of an external effect, or convergence for arbitrary controllers.",
        "negative": "manifest order or controller observation order supplies a global serial execution plan and proves stable convergence",
    },
    "constitution.family.representation_codec": {
        "title": "Apache Arrow Columnar Format",
        "publisher": "Apache Arrow",
        "url": "https://arrow.apache.org/docs/format/Columnar.html",
        "claim": "Arrow arrays and record-batch fields are ordered sequences, nested fields and buffers are serialized by a defined pre-order traversal, and IPC streams constrain schema, dictionary and record-batch message dependencies.",
        "coordinates": ["array_logical_position", "schema_field_order", "nested_field_traversal", "buffer_layout_order", "ipc_message_dependency"],
        "limit": "Arrow specifies logical and physical representation. It does not establish domain order, table sort guarantees, event causality, record-batch arrival finality, or equivalence between buffer adjacency and semantic proximity.",
        "negative": "physical buffer order, schema field order, row order, event time and business precedence are one ordering relation",
    },
    "constitution.family.semantic_metrics_formulas": {
        "title": "MetricFlow metric semantics",
        "publisher": "dbt Labs",
        "url": "https://github.com/dbt-labs/dbt-core/blob/main/crates/dbt-metricflow/docs/metric-semantics.md",
        "claim": "MetricFlow metrics form a dependency and join topology: entities connect semantic models, dimensions choose grouping paths, and derived metrics depend on other metric results while producing values at requested grouping grains.",
        "coordinates": ["metric_dependency_graph", "semantic_model_join_path", "entity_join_key", "grouping_key_order", "formula_operand_relation"],
        "limit": "This documentation specifies one semantic-query compiler. It does not prove that an available join path is semantically valid, that operand listing supplies evaluation order, or that query result order follows hierarchy or formula dependency.",
        "negative": "configuration order or any reachable entity path uniquely determines a valid business join, formula evaluation schedule and result sort",
    },
    "constitution.family.platform_commercial_support": {
        "title": "TMF622 Product Ordering Management API v5.0.0",
        "publisher": "TM Forum",
        "url": "https://github.com/tmforum-apis/TMF622_ProductOrder/blob/main/TMF622-ProductOrdering-v5.0.0.oas.yaml",
        "claim": "TMF622 represents a product order as identified order items plus explicit item relationships, actions and lifecycle data; relationship identifiers and types carry cross-item topology rather than the incidental position of an item in a JSON array.",
        "coordinates": ["order_item_identity", "order_item_relationship_graph", "requested_action", "order_lifecycle_relation", "collection_position"],
        "limit": "TMF622 is a telecom product-order API schema. It does not define one universal fulfillment precedence algebra, prove that order-item relations are acyclic, or make response collection order operationally significant.",
        "negative": "the array position of a product-order item is its fulfillment sequence, dependency rank or bundle hierarchy",
    },
    "constitution.family.messaging_coordination": {
        "title": "Apache Kafka Introduction",
        "publisher": "Apache Kafka",
        "url": "https://kafka.apache.org/documentation/",
        "claim": "Kafka guarantees write/read order within a topic partition and routes equal keys to the same partition under a compatible partitioning strategy; a topic with multiple partitions is not one totally ordered log.",
        "coordinates": ["partition_local_total_order", "record_offset", "key_partition_topology", "cross_partition_partial_order", "consumer_group_assignment"],
        "limit": "Kafka ordering is scoped to broker log partitions and configured routing. It does not prove event-time order, causal order across partitions, business-effect order, or stable key placement after arbitrary repartitioning.",
        "negative": "Kafka provides one global total order across a topic and offset comparison across partitions establishes causality",
    },
    "constitution.family.operations_research": {
        "title": "OR-Tools: Vehicle routing with pickups and deliveries",
        "publisher": "Google OR-Tools",
        "url": "https://developers.google.com/optimization/routing/pickup_delivery",
        "claim": "OR-Tools routing models locations as graph nodes and arcs and expresses pickup-before-delivery plus same-vehicle and cumulative-distance constraints explicitly; a solver route is an ordered decision variable subject to a model, not an inherent input order.",
        "coordinates": ["routing_graph", "route_visit_sequence", "pickup_delivery_precedence", "same_vehicle_constraint", "cumulative_dimension_order"],
        "limit": "The example describes one optimization formulation and solver API. It does not establish model fidelity, make every feasible route optimal, or turn source row order into operational precedence.",
        "negative": "input list order is the route, graph reachability is precedence, or any feasible sequence is the authorized optimum",
    },
    "constitution.family.security_privacy_trust": {
        "title": "RFC 5280: Internet X.509 Public Key Infrastructure Certificate and CRL Profile",
        "publisher": "IETF",
        "url": "https://www.rfc-editor.org/rfc/rfc5280.html",
        "claim": "RFC 5280 validates a prospective certification path as an ordered sequence from a certificate issued by a trust anchor to the target certificate, with issuer-subject adjacency, no repeated certificate and application-sensitive policy constraints.",
        "coordinates": ["certification_path_sequence", "issuer_subject_adjacency", "trust_anchor_input", "target_certificate", "policy_tree"],
        "limit": "RFC 5280 governs PKIX certificate-path validation. It does not make graph reachability sufficient for trust, choose the same path for every relying party, order authorization decisions, or prove an end entity is trustworthy in all contexts.",
        "negative": "any chain-shaped certificate graph is valid and a valid path supplies universal transitive trust or delegation authority",
    },
    "constitution.family.pipeline_dataflow": {
        "title": "Basics of the Apache Beam model",
        "publisher": "Apache Beam",
        "url": "https://beam.apache.org/documentation/basics/",
        "claim": "A Beam pipeline is a directed acyclic graph of transforms and PCollections, while each PCollection is an unordered bag; event timestamps, windows, watermarks and runner execution add scoped temporal relations without a general element-processing order.",
        "coordinates": ["pipeline_dependency_dag", "unordered_pcollection", "event_timestamp", "window_membership", "watermark_progress"],
        "limit": "Beam defines portable data-processing semantics. It does not make source order portable through arbitrary transforms, equate watermark progress with completeness, or turn pipeline graph order into business causality.",
        "negative": "pipeline construction order, runner execution order, event-time order and element arrival order are identical",
    },
    "constitution.family.governance_metadata_ontology": {
        "title": "SKOS Simple Knowledge Organization System Primer",
        "publisher": "W3C",
        "url": "https://www.w3.org/TR/skos-primer/",
        "claim": "SKOS separates broader/narrower semantic links, their transitive super-properties, ordinary collections and explicitly ordered collections; a concept can have several broader concepts, so a concept scheme need not be a tree.",
        "coordinates": ["broader_narrower_graph", "transitive_ancestor_relation", "multi_parent_hierarchy", "unordered_collection", "ordered_member_list"],
        "limit": "SKOS represents knowledge-organization systems. It does not equate broader/narrower with OWL subclassing, partonomy, ownership, workflow precedence or display order, and direct broader is not declared transitive.",
        "negative": "every SKOS hierarchy is a tree and broader, subclass-of, part-of, display order and dependency mean the same relation",
    },
    "constitution.family.geospatial_analytics": {
        "title": "OGC GeoSPARQL 1.1",
        "publisher": "Open Geospatial Consortium",
        "url": "https://www.ogc.org/standards/geosparql/",
        "claim": "GeoSPARQL defines qualitative topological relations and quantitative spatial computation over features and geometries, separately from the coordinate sequences used to encode a geometry.",
        "coordinates": ["feature_geometry_relation", "qualitative_spatial_topology", "topological_dimension", "coordinate_dimension", "geometry_serialization_order"],
        "limit": "GeoSPARQL standardizes geospatial RDF representation and queries. It does not make coordinate tuple order a feature-network topology, infer movement chronology, or define business containment and jurisdiction hierarchy.",
        "negative": "coordinate order, spatial adjacency, containment, route order and administrative hierarchy are one topology",
    },
    "constitution.family.connector_protocol": {
        "title": "Debezium connector for PostgreSQL",
        "publisher": "Debezium",
        "url": "https://debezium.io/documentation/reference/stable/connectors/postgresql.html",
        "claim": "Debezium records PostgreSQL WAL positions and transaction identifiers and can enrich change events with transaction-total and per-collection order, while snapshot READ events may interleave with streaming changes and require collision resolution.",
        "coordinates": ["wal_position", "transaction_local_total_order", "data_collection_order", "snapshot_stream_interleaving", "topic_partition_order"],
        "limit": "These coordinates describe one CDC connector and source log. They do not provide a global order across databases and topics, prove business causality, or make processing time equivalent to transaction commit order.",
        "negative": "LSN, transaction event index, Kafka offset, snapshot emission order and business-event time are globally comparable",
    },
    "constitution.family.forecasting_lifecycle": {
        "title": "Forecasting hierarchical and grouped time series",
        "publisher": "Forecasting: Principles and Practice (3rd ed.)",
        "url": "https://otexts.com/fpp3/hierarchical.html",
        "claim": "Hierarchical time series use nested aggregation structures, grouped series use crossed attributes with alternative aggregation paths, and coherent forecasts must satisfy the resulting summing constraints across all levels.",
        "coordinates": ["nested_aggregation_hierarchy", "crossed_grouping_topology", "bottom_level_series", "summing_matrix", "forecast_coherence_relation"],
        "limit": "The chapter defines aggregation topology and reconciliation for collections of forecasts. It does not require every grouping to be a tree, make hierarchy order temporal, or prove that independently generated forecasts are coherent.",
        "negative": "every forecast aggregation topology is a single tree and a collection of individually valid forecasts is automatically coherent",
    },
    "constitution.family.experimentation_lifecycle": {
        "title": "Statsig Layers",
        "publisher": "Statsig",
        "url": "https://docs.statsig.com/experiments/layers-overview",
        "claim": "Statsig layers define mutually exclusive experiment universes and layer-scoped parameters: assignment to one experiment excludes assignment to another in the same layer, independently of configuration or display order.",
        "coordinates": ["experiment_layer_membership", "mutual_exclusion_relation", "allocation_partition", "shared_parameter_scope", "exposure_relation"],
        "limit": "Statsig documents one experimentation platform's allocation topology. It does not prove causal validity, define all overlapping-experiment designs, or make layer membership, experiment priority and rollout sequence equivalent.",
        "negative": "experiment list order determines assignment and layer membership is the same as causal independence, rollout precedence or exposure order",
    },
}


def build() -> dict[str, Any]:
    return build_campaign(
        axis="order_and_topology",
        campaign_key="p3o",
        program_id="program.p3o.order-topology-evidence.v1",
        claims=CLAIMS,
        targets_path=TARGETS,
        as_of=AS_OF,
    )


def outputs() -> dict[str, str]:
    return campaign_outputs(
        built=build(),
        manifest_id="manifest.p3o.order-topology-evidence.v1",
        as_of=AS_OF,
    )


def main() -> int:
    write_outputs(HERE, outputs())
    summary = build()["summary"]
    print(
        "BUILD PASS P3O order/topology: "
        f"{summary['primary_evidence_candidates']} bounded candidates route "
        f"{summary['represented_library_occurrences']} library occurrences; "
        "owner decisions and gap closures remain zero"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
