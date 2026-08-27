#!/usr/bin/env python3
"""Build bounded primary-evidence candidates for the composition/algebra axis."""
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
    "constitution.family.analytical_method_kernels": {
        "title": "Hierarchical process mining for scalable software analysis",
        "publisher": "Sander J. J. Leemans, Eindhoven University of Technology",
        "url": "https://research.tue.nl/files/109318783/Leemans_thesis_normal.pdf",
        "claim": "Process trees compose behavioral languages with distinct sequence, exclusive-choice, parallel/interleaving and loop operators; the language of a parent depends on the chosen operator and the languages of its children.",
        "coordinates": ["sequential_composition", "exclusive_choice", "parallel_interleaving", "loop_composition", "behavioral_language"],
        "limit": "The thesis formalizes process-tree behavior and discovery. It does not make these operators universal for statistical, causal, optimization, simulation or diagnostic methods, or prove that a discovered model is accepted domain truth.",
        "negative": "all analytical methods compose by associative function chaining and sequence, choice, concurrency and iteration are interchangeable",
    },
    "constitution.family.predictive_analytics": {
        "title": "Open Neural Network Exchange Intermediate Representation (ONNX IR) Specification",
        "publisher": "ONNX",
        "url": "https://onnx.ai/onnx/repo-docs/IR.html",
        "claim": "ONNX functions define operators by expansion into subgraphs, and composed graphs must satisfy typed operator signatures, acyclicity, namespace uniqueness and SSA output-name constraints.",
        "coordinates": ["function_expansion", "subgraph_composition", "typed_operator_binding", "namespace_collision", "ssa_dependency"],
        "limit": "ONNX specifies computation-graph interchange. It does not prove that model ensembles, feature pipelines, calibrators or decision policies are semantically compatible or preserve predictive validity when composed.",
        "negative": "any two models with matching tensor shapes can be composed without name, type, calibration, distribution or lifecycle obligations",
    },
    "constitution.family.shared_semantic_foundations": {
        "title": "RDF 1.1 Concepts and Abstract Syntax",
        "publisher": "W3C",
        "url": "https://www.w3.org/TR/rdf11-concepts/",
        "claim": "RDF graph merge is set union after keeping blank nodes from different input graphs distinct; shared IRIs may join statements, while local blank-node labels cannot be used as cross-graph identity.",
        "coordinates": ["graph_union", "blank_node_standardization_apart", "shared_iri_join", "duplicate_triple_idempotence", "dataset_named_graph_boundary"],
        "limit": "RDF graph merge composes assertions at the abstract-syntax layer. It does not resolve contradictory claims, choose an authority, perform ontology imports, merge domain entities, or accept information loss.",
        "negative": "concatenating RDF serializations is a semantic entity merge and equal blank-node labels identify the same thing across sources",
    },
    "constitution.family.quality_reconciliation": {
        "title": "Shapes Constraint Language (SHACL)",
        "publisher": "W3C",
        "url": "https://www.w3.org/TR/shacl/",
        "claim": "SHACL composes shape conformance with distinct `and`, `or`, `xone`, `not` and nested-node constraints; recursion and processor failures have separate semantics from an ordinary non-conformance result.",
        "coordinates": ["constraint_conjunction", "constraint_disjunction", "exclusive_conformance", "constraint_negation", "nested_shape_reference"],
        "limit": "SHACL combines RDF validation conditions. It does not define repair merging, waiver precedence, source reconciliation, severity aggregation or fitness-for-use composition outside its validation semantics.",
        "negative": "combining validation rules is boolean folding with no failure, recursion, result-attribution or repair-order distinctions",
    },
    "constitution.family.candidate_data_shapes": {
        "title": "JSON Schema Core, Draft 2020-12",
        "publisher": "JSON Schema",
        "url": "https://json-schema.org/draft/2020-12/json-schema-core.html",
        "claim": "JSON Schema applicators apply referenced or embedded subschemas and combine assertion and annotation results under keyword-specific rules such as all-of, any-of and one-of; references remain transparent to validation but may matter to generators.",
        "coordinates": ["subschema_application", "all_of_conjunction", "any_of_disjunction", "one_of_exclusivity", "annotation_accumulation"],
        "limit": "JSON Schema composes validation/evaluation constraints. `allOf` is not object-oriented inheritance or data merge, annotations have vocabulary-specific combination rules, and arbitrary recursive cycles may be undefined.",
        "negative": "allOf merges object properties like class inheritance and any schema references can be flattened without changing generation or annotation behavior",
    },
    "constitution.family.persistence_lakehouse": {
        "title": "Apache Iceberg Specification",
        "publisher": "Apache Iceberg",
        "url": "https://iceberg.apache.org/spec/",
        "claim": "Iceberg composes table state through optimistic snapshot commits, manifest lists, data files and position/equality delete files; delete applicability depends on sequence numbers, partition scope and row matching rather than file concatenation alone.",
        "coordinates": ["optimistic_snapshot_commit", "manifest_set_composition", "data_delete_file_application", "sequence_scoped_merge", "commit_conflict"],
        "limit": "Iceberg specifies table-format composition and conflict behavior. It does not merge business transactions across tables, settle source-of-truth conflicts, make every concurrent change commutative, or authorize destructive compaction.",
        "negative": "lakehouse composition is unioning files and every concurrent append, overwrite, delete and schema change can be merged by the same commutative operator",
    },
    "constitution.family.runtime_resource_control": {
        "title": "Kubernetes Server-Side Apply",
        "publisher": "Kubernetes",
        "url": "https://kubernetes.io/docs/reference/using-api/server-side-apply/",
        "claim": "Server-Side Apply composes declarative object fragments using schema-declared atomic, set and map field topologies while tracking field managers; conflicting ownership changes fail unless the caller explicitly forces transfer.",
        "coordinates": ["field_ownership", "schema_directed_merge", "atomic_field", "set_or_map_list", "conflict_or_forced_transfer"],
        "limit": "Server-Side Apply governs Kubernetes API object fields. It does not make forced overwrite semantically safe, merge external effects, establish application-domain invariants, or supply one merge law for all CRDs and list types.",
        "negative": "declarative runtime state is last-writer-wins JSON merge and a forced apply proves that ownership transfer and downstream effects are safe",
    },
    "constitution.family.lineage_provenance_evidence": {
        "title": "Linking Across Provenance Bundles",
        "publisher": "W3C",
        "url": "https://www.w3.org/TR/prov-links/",
        "claim": "PROV bundles are named sets of provenance descriptions validated independently; `mentionOf` lets a consumer specialize an entity as described in a particular foreign bundle without copying or mutating that bundle.",
        "coordinates": ["independent_bundle", "provenance_of_provenance", "cross_bundle_mention", "contextual_specialization", "foreign_bundle_reference"],
        "limit": "PROV-Links is an experimental provenance extension. It does not merge bundles into one authority, infer a mention from specialization, resolve contradictory descriptions, or prove the producer's evidence true.",
        "negative": "provenance composition is copying all bundles into one graph and equal entity URIs allow claims, authorities and contexts to collapse",
    },
    "constitution.family.optional_model_agent_extensions": {
        "title": "Model Context Protocol Architecture",
        "publisher": "Model Context Protocol",
        "url": "https://modelcontextprotocol.io/specification/2025-06-18/architecture",
        "claim": "An MCP host composes multiple focused servers through isolated one-to-one client sessions, capability negotiation and host-controlled context aggregation; servers do not automatically see one another or the full conversation.",
        "coordinates": ["host_aggregation", "isolated_client_server_session", "capability_negotiation", "cross_server_boundary", "consent_control"],
        "limit": "MCP specifies protocol architecture, not a semantic algebra for combining tool effects, resource truth, model outputs or agent plans. Host coordination does not make server capabilities interchangeable or safe to chain.",
        "negative": "MCP server composition is unrestricted tool chaining and all connected servers share context, authority, state and failure semantics",
    },
    "constitution.family.representation_codec": {
        "title": "WebAssembly Interface Types (WIT)",
        "publisher": "WebAssembly Component Model project",
        "url": "https://github.com/WebAssembly/component-model/blob/main/design/mvp/WIT.md",
        "claim": "WIT composes interfaces and worlds through typed use/import/export and world inclusion; included-world union de-duplicates compatible names, requires explicit renaming for collisions and does not imply subtyping.",
        "coordinates": ["interface_type_import", "world_union", "name_deduplication", "collision_rename", "resource_handle_boundary"],
        "limit": "WIT describes component interface composition. It does not prove behavioral substitutability, semantic compatibility, lossless codec adaptation, shared resource ownership or end-to-end effect preservation.",
        "negative": "interface union is subtype inheritance and equal names or wire-compatible value types guarantee semantic and resource compatibility",
    },
    "constitution.family.query_compilation_execution": {
        "title": "Substrait Logical Relations",
        "publisher": "Substrait",
        "url": "https://substrait.io/relations/logical_relations/",
        "claim": "Substrait composes relations with operator-specific input arity, schema propagation and property maintenance; joins, set operations, aggregates, references and writes have different output and multiplicity semantics.",
        "coordinates": ["unary_relation_composition", "binary_join", "set_operation", "schema_emit_mapping", "property_propagation"],
        "limit": "Substrait composes portable relational plans. It does not make join equal union, preserve ordering/distribution through every operator, validate domain join meaning, or authorize write effects merely because a plan type-checks.",
        "negative": "relational composition is associative function piping and joins, unions, cross products and writes share one multiplicity and effect law",
    },
    "constitution.family.security_privacy_trust": {
        "title": "eXtensible Access Control Markup Language (XACML) Version 3.0",
        "publisher": "OASIS",
        "url": "https://docs.oasis-open.org/xacml/3.0/xacml-3.0-core-spec-cos01-en.html",
        "claim": "XACML policies and rules compose under explicit combining algorithms including deny-overrides, permit-overrides, ordered variants, first-applicable and only-one-applicable, preserving Permit, Deny, NotApplicable and Indeterminate distinctions.",
        "coordinates": ["deny_overrides", "permit_overrides", "first_applicable", "only_one_applicable", "indeterminate_propagation"],
        "limit": "XACML defines access-control decision combination. It does not reduce every policy domain to booleans, prove that an obligation executed, merge identities or consent, or make differently ordered algorithms equivalent.",
        "negative": "security policy composition is commutative boolean OR and Permit, Deny, NotApplicable and Indeterminate can be folded without algorithm-specific precedence",
    },
    "constitution.family.consumption_bi_visualization": {
        "title": "Vega Transforms",
        "publisher": "Vega Project",
        "url": "https://vega.github.io/vega/docs/transforms/",
        "claim": "Vega data definitions compose ordered transform arrays whose operators may filter, derive, aggregate, reshape, spatially transform or generate data before scenegraph encoding; transform order can therefore change outputs.",
        "coordinates": ["ordered_transform_pipeline", "dataflow_dependency", "aggregation_transform", "reshape_transform", "scenegraph_input"],
        "limit": "Vega transform composition governs visualization dataflow. It does not validate business semantics, make all transforms commute, preserve grain or uncertainty automatically, or turn a rendered view into persisted analytical truth.",
        "negative": "visualization transforms are freely reorderable presentation steps that cannot change analytical grain, membership or meaning",
    },
    "constitution.family.platform_commercial_support": {
        "title": "TMF622 Product Ordering Management API v5.0.0",
        "publisher": "TM Forum",
        "url": "https://github.com/tmforum-apis/TMF622_ProductOrder/blob/main/TMF622-ProductOrdering-v5.0.0.oas.yaml",
        "claim": "TMF622 composes a commercial order from identified order items, offerings, products, prices, actions and typed item relationships rather than flattening catalog, order, fulfillment and realized product into one object.",
        "coordinates": ["order_item_composition", "offering_reference", "typed_item_relationship", "price_component", "requested_action"],
        "limit": "TMF622 defines telecom order API resources. It does not establish universal bundle pricing, fulfillment dependency, entitlement, settlement or provider-selection algebras, and an accepted order is not a realized product.",
        "negative": "commercial composition is nesting line items and therefore catalog inclusion, order dependency, fulfillment, entitlement and billing all share one containment relation",
    },
    "constitution.family.pipeline_dataflow": {
        "title": "Apache Beam Programming Guide",
        "publisher": "Apache Beam",
        "url": "https://beam.apache.org/documentation/programming-guide/",
        "claim": "Beam supports composite transforms built from core transforms and explicit multi-input operations; flattening collections requires compatible element coders and windowing strategies rather than treating every pipeline edge as simple concatenation.",
        "coordinates": ["composite_transform", "transform_chaining", "multi_input_flatten", "window_compatibility", "coder_compatibility"],
        "limit": "Beam defines dataflow composition. It does not make transform ordering commutative, merge external sink effects, preserve domain invariants automatically, or guarantee that runner-specific behavior composes portably beyond the Beam model.",
        "negative": "any PCollections can be flattened and any transforms can be reordered when their element types look similar",
    },
    "constitution.family.messaging_coordination": {
        "title": "Apache Kafka Design",
        "publisher": "Apache Kafka",
        "url": "https://kafka.apache.org/41/design/design/",
        "claim": "Kafka can atomically compose produced records across partitions with consumer-offset updates in a transaction for consume-transform-produce workflows, subject to committed isolation and explicit abort/reset handling.",
        "coordinates": ["multi_partition_transaction", "offset_output_atomicity", "read_committed_visibility", "abort_recovery", "external_sink_boundary"],
        "limit": "Kafka transactions compose Kafka log writes and offsets, not arbitrary external effects. Exactly-once behavior outside Kafka requires cooperation, and transaction abort does not automatically rewind all application state.",
        "negative": "messaging composition makes every downstream effect exactly once and chaining idempotent producers, consumers and connectors creates one global transaction",
    },
    "constitution.family.operations_research": {
        "title": "CP-SAT Solver",
        "publisher": "Google OR-Tools",
        "url": "https://developers.google.com/optimization/cp/cp_solver",
        "claim": "A CP-SAT model composes integer/Boolean variables, conjunctive constraints and an optional objective into one feasibility or optimization problem whose combined status may be optimal, feasible, infeasible, invalid or unknown.",
        "coordinates": ["variable_domain_composition", "constraint_conjunction", "objective_function", "model_validation", "solver_status"],
        "limit": "CP-SAT composition applies to an encoded constraint model. It does not prove the model reflects the world, make incompatible objectives commensurable, authorize a solution, or permit independent optima to be merged into a global optimum.",
        "negative": "optimization composition is adding scores and constraints without unit, priority, feasibility, model-validity or authorization conflicts",
    },
    "constitution.family.semantic_metrics_formulas": {
        "title": "MetricFlow metric semantics",
        "publisher": "dbt Labs",
        "url": "https://github.com/dbt-labs/dbt-core/blob/main/crates/dbt-metricflow/docs/metric-semantics.md",
        "claim": "MetricFlow distinguishes simple aggregation, derived expression, ratio and cumulative-window composition while requiring the result to retain one value per requested output grain after metric and query filters.",
        "coordinates": ["derived_metric_expression", "ratio_composition", "cumulative_window", "filter_scope", "output_grain_preservation"],
        "limit": "MetricFlow documents one metric compiler. It does not make arbitrary units composable, guarantee denominator validity, permit grain-changing operands without reconciliation, or prove that formula algebra matches accepted business meaning.",
        "negative": "metric composition is string arithmetic and any measures, grains, filters, units and time windows can be combined when SQL can be generated",
    },
    "constitution.family.geospatial_analytics": {
        "title": "OGC GeoSPARQL 1.1",
        "publisher": "Open Geospatial Consortium",
        "url": "https://www.ogc.org/standards/geosparql/",
        "claim": "GeoSPARQL composes geospatial queries with topological predicates and geometry operations such as intersection, union, buffer and distance over geometries whose spatial reference and dimensional properties constrain valid interpretation.",
        "coordinates": ["topological_predicate", "geometry_intersection", "geometry_union", "buffer_operation", "crs_compatibility"],
        "limit": "GeoSPARQL defines geospatial RDF/query operations. It does not guarantee every geometry union is valid, erase CRS and precision obligations, equate topological union with feature/entity merge, or preserve all attributes through geometry operations.",
        "negative": "geospatial composition is set union of coordinates and matching geometry encodings imply compatible CRS, precision, topology and feature identity",
    },
    "constitution.family.governance_metadata_ontology": {
        "title": "OWL 2 Structural Specification and Functional-Style Syntax",
        "publisher": "W3C",
        "url": "https://www.w3.org/TR/owl2-syntax/",
        "claim": "OWL 2 ontology modularization uses a transitive imports closure and an axiom closure that unions imported axioms while standardizing anonymous individuals apart; incompatible ontology versions should not coexist in one import closure.",
        "coordinates": ["direct_import", "transitive_import_closure", "axiom_union", "anonymous_individual_standardization", "version_incompatibility"],
        "limit": "OWL imports compose formal ontologies under OWL semantics. They do not merge governance authority, resolve inconsistent axioms automatically, equate import with endorsement, or define catalog/package dependency behavior generally.",
        "negative": "ontology composition is textual concatenation and importing an ontology endorses it, merges anonymous individuals and resolves version conflicts",
    },
    "constitution.family.connector_protocol": {
        "title": "Debezium connector for PostgreSQL",
        "publisher": "Debezium",
        "url": "https://debezium.io/documentation/reference/stable/connectors/postgresql.html",
        "claim": "Debezium composes incremental snapshot READ records with concurrent change-stream events through primary-key collision handling: a matching streamed update/delete supersedes the buffered snapshot record within the snapshot window.",
        "coordinates": ["snapshot_stream_composition", "primary_key_collision", "superseding_change", "snapshot_window", "remaining_read_emission"],
        "limit": "This is a connector-specific reconciliation algorithm. It does not merge arbitrary sources, handle concurrent schema changes, prove target application, or make snapshot and stream records commutative outside the defined window.",
        "negative": "connector composition is concatenating snapshot and CDC streams and duplicates can be removed without source-key, window, operation or supersession semantics",
    },
    "constitution.family.experimentation_lifecycle": {
        "title": "Statsig Layers",
        "publisher": "Statsig",
        "url": "https://docs.statsig.com/experiments/layers-overview",
        "claim": "Statsig layers compose related experiments through mutually exclusive allocation and shared layer parameters, so adding an experiment changes allocation topology without requiring all experiments to share treatment logic.",
        "coordinates": ["mutual_exclusion_layer", "allocation_partition", "shared_parameter", "experiment_membership", "layer_exposure"],
        "limit": "Statsig documents one experimentation platform. It does not define causal interaction algebra for arbitrary overlapping tests, combine statistical evidence, authorize rollout, or prove that layered experiments are independent.",
        "negative": "experiments compose by running every treatment simultaneously and shared parameters or mutual exclusion prove causal independence and compatible decisions",
    },
}


def build() -> dict[str, Any]:
    return build_campaign(
        axis="composition_algebra",
        campaign_key="p3c",
        program_id="program.p3c.composition-algebra-evidence.v1",
        claims=CLAIMS,
        targets_path=TARGETS,
        as_of=AS_OF,
    )


def outputs() -> dict[str, str]:
    return campaign_outputs(
        built=build(),
        manifest_id="manifest.p3c.composition-algebra-evidence.v1",
        as_of=AS_OF,
    )


def main() -> int:
    write_outputs(HERE, outputs())
    summary = build()["summary"]
    print(
        "BUILD PASS P3C composition/algebra: "
        f"{summary['primary_evidence_candidates']} bounded candidates route "
        f"{summary['represented_library_occurrences']} library occurrences; "
        "owner decisions and gap closures remain zero"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
