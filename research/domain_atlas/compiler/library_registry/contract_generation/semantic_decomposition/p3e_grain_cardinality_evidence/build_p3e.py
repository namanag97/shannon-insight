#!/usr/bin/env python3
"""Build bounded primary-evidence candidates for the grain/cardinality axis."""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
SEM = HERE.parent
TARGETS = SEM / "structured_projection/targeted-evidence-work-packages.jsonl"
AS_OF = "2026-08-27"
sys.path.insert(0, str(SEM))

from axis_evidence_campaign import (  # noqa: E402
    build_campaign,
    campaign_outputs,
    canonical,
    digest,
    load_jsonl,
    write_outputs,
)


CLAIMS: dict[str, dict[str, Any]] = {
    "constitution.family.connector_protocol": {
        "title": "Debezium signaling and incremental snapshots", "publisher": "Debezium", "url": "https://debezium.io/documentation/reference/stable/configuration/signalling.html",
        "claim": "Incremental snapshot execution distinguishes a requested snapshot, tables, chunks/windows and emitted change records; those grains have different completion and resume semantics.",
        "coordinates": ["request", "table", "chunk_or_window", "change_record"], "limit": "Debezium connector semantics do not define every connector, source transaction or business observation grain.",
        "negative": "one emitted change record is the whole requested snapshot",
    },
    "constitution.family.consumption_bi_visualization": {
        "title": "Vega-Lite aggregation", "publisher": "Vega Project", "url": "https://vega.github.io/vega-lite/docs/aggregate.html",
        "claim": "An aggregate transform changes data-object grain by grouping on declared fields and computing summaries; omitted group-by fields produce a single group.",
        "coordinates": ["input_data_object", "group", "aggregate_result", "view"], "limit": "Vega-Lite specifies visualization transforms, not universal business metric additivity or semantic correctness.",
        "negative": "a rendered mark preserves one-to-one input-record grain",
    },
    "constitution.family.shared_semantic_foundations": {
        "title": "Shapes Constraint Language (SHACL)", "publisher": "W3C", "url": "https://www.w3.org/TR/shacl/",
        "claim": "SHACL minCount and maxCount constrain value nodes reached for a focus node through an exact property path and profile.",
        "coordinates": ["focus_node", "property_path", "value_node_set", "validation_result"], "limit": "A SHACL count does not establish source completeness, real-world entity cardinality or analytical grain.",
        "negative": "schema cardinality proves population completeness",
    },
    "constitution.family.candidate_data_shapes": {
        "title": "FHIR R5 Bundle definitions", "publisher": "HL7", "url": "https://fhir.hl7.org/fhir/bundle-definitions.html",
        "claim": "FHIR distinguishes Bundle, Bundle.entry, contained Resource, search-match total and page entry count; entry order semantics depend on bundle type.",
        "coordinates": ["bundle", "entry", "resource", "search_match_set", "page"], "limit": "FHIR bundle rules govern the named healthcare representation and cannot define other document, media or scientific shapes.",
        "negative": "bundle total equals the number of entries on the current page",
    },
    "constitution.family.representation_codec": {
        "title": "Apache Arrow columnar format", "publisher": "Apache Arrow", "url": "https://arrow.apache.org/docs/format/Columnar.html",
        "claim": "Arrow distinguishes scalar values, arrays with a logical length, equal-length arrays in a record batch and chunked physical buffers.",
        "coordinates": ["scalar", "array", "record_batch", "buffer_or_chunk"], "limit": "Arrow physical and logical layout does not establish business observation grain, completeness or semantic equality.",
        "negative": "physical buffer boundaries define semantic record groups",
    },
    "constitution.family.experimentation_lifecycle": {
        "title": "Statsig Warehouse Native assignment sources", "publisher": "Statsig", "url": "https://docs.statsig.com/statsig-warehouse-native/configuration/assignment-sources",
        "claim": "An assignment source records exposure time, experimental unit identifier, experiment identifier and group identifier as distinct coordinates.",
        "coordinates": ["exposure_occurrence", "experimental_unit", "experiment", "variant_group"], "limit": "Statsig input requirements do not prove randomization integrity, unique exposure, analysis population or causal validity.",
        "negative": "an exposure row is the experimental unit or the experiment itself",
    },
    "constitution.family.forecasting_lifecycle": {
        "title": "Forecasting hierarchical and grouped time series", "publisher": "OTexts", "url": "https://otexts.com/fpp3/hierarchical.html",
        "claim": "Hierarchical and grouped forecasting distinguishes bottom-level series, aggregate series and crossed or nested aggregation structures that require coherent forecasts.",
        "coordinates": ["observation", "series", "bottom_level_series", "aggregate_series", "hierarchy_or_group"], "limit": "The source establishes forecast aggregation structure, not universal forecast selection, acceptance or business hierarchy.",
        "negative": "independently forecast series are automatically coherent at every aggregation level",
    },
    "constitution.family.geospatial_analytics": {
        "title": "OGC Simple Feature Access Part 1", "publisher": "Open Geospatial Consortium", "url": "https://www.ogc.org/standards/sfa/",
        "claim": "Simple Features distinguishes a feature from its geometry-valued attributes and distinguishes Point, Curve, Surface and GeometryCollection under a spatial reference system.",
        "coordinates": ["feature", "geometry", "geometry_component", "feature_collection"], "limit": "Simple Feature geometry does not define raster coverage, trajectory, network, business entity or analytical result grain.",
        "negative": "geometry identity is feature identity",
    },
    "constitution.family.governance_metadata_ontology": {
        "title": "Data Catalog Vocabulary Version 3", "publisher": "W3C", "url": "https://www.w3.org/TR/vocab-dcat-3/",
        "claim": "DCAT distinguishes Catalog, CatalogRecord, Dataset, DatasetSeries, Distribution and DataService; a distribution is an accessible representation rather than the dataset itself.",
        "coordinates": ["catalog", "catalog_record", "dataset", "dataset_series", "distribution", "data_service"], "limit": "DCAT catalog vocabulary does not establish master-data identity, source truth, dataset completeness or domain-specific ownership.",
        "negative": "catalog record, dataset and downloadable file are one identity",
    },
    "constitution.family.lineage_provenance_evidence": {
        "title": "OpenLineage object model", "publisher": "OpenLineage", "url": "https://openlineage.io/docs/next/spec/object-model/",
        "claim": "OpenLineage distinguishes a RunEvent observation from Job metadata updates and Dataset metadata updates, preserving run, job, dataset and event grains.",
        "coordinates": ["event_observation", "run", "job", "dataset"], "limit": "OpenLineage events do not prove causal completeness, domain truth, job acceptance or data correctness.",
        "negative": "one lineage event is a complete lineage graph or accepted run",
    },
    "constitution.family.messaging_coordination": {
        "title": "Apache Kafka message format", "publisher": "Apache Kafka", "url": "https://kafka.apache.org/26/implementation/message-format/",
        "claim": "Kafka distinguishes a record from a record batch containing one or more records and binds offsets within a partitioned log.",
        "coordinates": ["record", "record_batch", "partition_log", "offset"], "limit": "Kafka storage/wire grain does not define business-event identity, global order, delivery acceptance or end-to-end exactly-once effects.",
        "negative": "record batch, transaction and business event are interchangeable",
    },
    "constitution.family.analytical_method_kernels": {
        "title": "OCEL 2.0 specification", "publisher": "OCEL Standard", "url": "https://www.ocel-standard.org/specification/overview/",
        "claim": "OCEL distinguishes events, uniquely identified objects, object types, event-to-object relations, object-to-object relations and time-varying object attributes.",
        "coordinates": ["event", "object", "object_type", "qualified_relation", "object_attribute_change"], "limit": "OCEL supplies event-data semantics for object-centric analysis; it does not define a universal case, process variant, KPI or analytical acceptance grain.",
        "negative": "each event belongs to exactly one inherent case",
    },
    "constitution.family.optional_model_agent_extensions": {
        "title": "Model Context Protocol resources", "publisher": "Model Context Protocol", "url": "https://modelcontextprotocol.io/specification/2025-06-18/server/resources",
        "claim": "MCP distinguishes a URI-identified resource definition, one or more returned content items, a parameterized resource template and paginated listing responses.",
        "coordinates": ["resource_definition", "resource_content_item", "resource_template", "list_page"], "limit": "MCP transport resources do not establish application-domain identity, source authority, truth or safe model use.",
        "negative": "a resource listing page is the resource corpus or a resource URI is its immutable content identity",
    },
    "constitution.family.operations_research": {
        "title": "OR-Tools CP-SAT model protocol", "publisher": "Google OR-Tools", "url": "https://github.com/google/or-tools/blob/v9.15/ortools/sat/cp_model.proto",
        "claim": "The CP-SAT protocol separates indexed variables, constraints, objective terms, assumptions and solution values in a model/result contract.",
        "coordinates": ["decision_variable", "constraint", "objective_term", "assumption", "solution_assignment"], "limit": "The OR-Tools protocol defines one solver representation, not business decision identity, policy authority, scenario semantics or solution acceptance.",
        "negative": "a solver solution assignment is an authorized business action",
    },
    "constitution.family.persistence_lakehouse": {
        "title": "Apache Iceberg specification", "publisher": "Apache Iceberg", "url": "https://iceberg.apache.org/spec/",
        "claim": "Iceberg distinguishes table, snapshot, manifest list, manifest, data/delete file, partition tuple and row; a snapshot's data is the union of files in its manifests.",
        "coordinates": ["table", "snapshot", "manifest_list", "manifest", "data_or_delete_file", "partition_tuple", "row"], "limit": "Iceberg metadata hierarchy does not define business observation grain, catalog authority, query result acceptance or cross-format equivalence.",
        "negative": "partition, data file, manifest and snapshot are the same completeness boundary",
    },
    "constitution.family.pipeline_dataflow": {
        "title": "Apache Beam programming guide", "publisher": "Apache Beam", "url": "https://beam.apache.org/documentation/programming-guide/",
        "claim": "Beam distinguishes PCollection, element, bundle, window and pane; boundedness and windowing change when aggregation can be complete.",
        "coordinates": ["pcollection", "element", "bundle", "window", "pane"], "limit": "Beam execution grain does not establish source completeness, business entity identity or sink effect acceptance.",
        "negative": "bundle, window, pane and complete dataset are interchangeable",
    },
    "constitution.family.platform_commercial_support": {
        "title": "TMF635 Usage Management API", "publisher": "TM Forum", "url": "https://github.com/tmforum-apis/TMF635_UsageManagement",
        "claim": "TMF635 represents usage records and usage specifications as explicit API resources, separating observed usage occurrences from their specification.",
        "coordinates": ["usage_occurrence", "usage_record", "usage_specification"], "limit": "TMF635 vocabulary does not define rating, invoice-line, account, tenant or universally accepted metering grain.",
        "negative": "usage record, rated charge and invoice line are one commercial fact",
    },
    "constitution.family.predictive_analytics": {
        "title": "scikit-learn glossary", "publisher": "scikit-learn", "url": "https://scikit-learn.org/stable/glossary.html",
        "claim": "scikit-learn distinguishes sample count, feature count, target shape and sample properties aligned to n_samples.",
        "coordinates": ["sample", "feature", "target", "sample_property", "dataset_matrix"], "limit": "scikit-learn array conventions do not define population, entity, episode, label authority or deployment scoring grain for all predictive systems.",
        "negative": "array row is always a real-world entity and repeated rows are independent samples",
    },
    "constitution.family.quality_reconciliation": {
        "title": "Data on the Web Best Practices: Data Quality Vocabulary", "publisher": "W3C", "url": "https://www.w3.org/TR/vocab-dqv/",
        "claim": "DQV distinguishes a quality measurement from its metric, measured dataset/distribution and quality annotation, making result grain and assessed-subject grain explicit.",
        "coordinates": ["measurement", "metric", "assessed_dataset_or_distribution", "quality_annotation"], "limit": "DQV vocabulary does not prove measurement validity, source completeness, reconciliation closure or fitness for a particular use.",
        "negative": "one measurement result proves whole-dataset fitness for every use",
    },
    "constitution.family.query_compilation_execution": {
        "title": "Trino SELECT", "publisher": "Trino", "url": "https://trino.io/docs/current/sql/select.html",
        "claim": "SQL SELECT distinguishes input rows, groups of matching rows, output rows and window partitions/frames; grouping and windowing change calculation grain differently.",
        "coordinates": ["input_row", "group", "output_row", "window_partition", "window_frame"], "limit": "Trino documents one engine's SQL behavior and does not establish business metric grain, global row identity or cross-engine equivalence.",
        "negative": "GROUP BY and window PARTITION BY have identical output cardinality",
    },
    "constitution.family.runtime_resource_control": {
        "title": "Kubernetes resource management for Pods and containers", "publisher": "Kubernetes", "url": "https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/",
        "claim": "Kubernetes distinguishes per-container requests/limits, aggregate Pod requests/limits and node capacity; scheduling and runtime enforcement consume different grains.",
        "coordinates": ["container_demand", "pod_demand", "node_capacity", "scheduled_placement", "runtime_usage"], "limit": "Kubernetes resource quantities do not prove application work completion, business cost allocation or provider-neutral performance.",
        "negative": "container limit, Pod request, node capacity and observed usage are one quantity",
    },
    "constitution.family.security_privacy_trust": {
        "title": "NIST SP 800-226 Guidelines for Evaluating Differential Privacy Guarantees", "publisher": "NIST", "url": "https://csrc.nist.gov/pubs/sp/800/226/final",
        "claim": "Differential privacy evaluation depends on an explicit neighboring-dataset relation, often differing by one individual's data, and quantifies privacy loss to entities.",
        "coordinates": ["individual_or_entity", "contribution", "dataset", "neighboring_dataset_pair", "mechanism_output"], "limit": "A neighboring relation and mathematical guarantee do not establish consent, purpose, population identity, implementation correctness or overall privacy sufficiency.",
        "negative": "row-level adjacency is automatically the correct individual-contribution model",
    },
    "constitution.family.semantic_metrics_formulas": {
        "title": "dbt Semantic Layer entities", "publisher": "dbt Labs", "url": "https://docs.getdbt.com/docs/build/entities",
        "claim": "dbt distinguishes semantic-model rows, primary/unique/foreign/natural entities and aggregation to entity granularity; join behavior depends on entity type.",
        "coordinates": ["semantic_model_row", "entity", "join_key", "metric_grouping_grain"], "limit": "dbt entity types do not establish real-world identity, measure additivity, source completeness or correctness outside the bound semantic model.",
        "negative": "table primary key is universal business identity and every measure is additive across every entity",
    },
}


def build() -> dict[str, Any]:
    return build_campaign(
        axis="grain_and_cardinality",
        campaign_key="p3e",
        program_id="program.p3e.grain-cardinality-evidence.v1",
        claims=CLAIMS,
        targets_path=TARGETS,
        as_of=AS_OF,
    )


def outputs() -> dict[str, str]:
    return campaign_outputs(
        built=build(),
        manifest_id="manifest.p3e.grain-cardinality-evidence.v1",
        as_of=AS_OF,
    )


def main() -> int:
    write_outputs(HERE, outputs())
    summary = build()["summary"]
    print(f"BUILD PASS P3E grain/cardinality: {summary['primary_evidence_candidates']} bounded candidates route {summary['represented_library_occurrences']} library occurrences; owner decisions and gap closures remain zero")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
