#!/usr/bin/env python3
"""Build the provider-neutral semantic metrics and formula research corpus."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
SCHEMA = ROOT / "schemas"
EDITION = 1
ACCESSED = "2026-08-25"
PREFIX = "smf"


def dump_json(name: str, value: Any) -> None:
    (ROOT / name).write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def dump_jsonl(name: str, rows: list[dict[str, Any]]) -> None:
    (ROOT / name).write_text(
        "".join(json.dumps(row, sort_keys=True, separators=(",", ":")) + "\n" for row in rows),
        encoding="utf-8",
    )


def sid(local: str) -> str:
    return f"source.{PREFIX}.{local}"


def cid(local: str) -> str:
    return f"context.{PREFIX}.{local}"


SOURCE_ROWS = [
    ("oasis.openformula14", "OpenDocument 1.4 Part 4: OpenFormula", "OASIS", "standard", "https://docs.oasis-open.org/office/OpenDocument/v1.4/os/part4-formula/OpenDocument-v1.4-os-part4-formula.html", 2025, ["formula_syntax", "types", "functions", "errors"]),
    ("oasis.odf14", "OpenDocument Format 1.4", "OASIS", "standard", "https://docs.oasis-open.org/office/OpenDocument/v1.4/OpenDocument-v1.4.html", 2025, ["formula_binding", "document_values"]),
    ("sdmx.31", "SDMX 3.1 Technical Specifications", "SDMX Sponsors", "standard", "https://sdmx.org/standards-2/", 2025, ["observation", "dimension", "measure", "structure"]),
    ("sdmx.im31", "SDMX 3.1 Information Model", "SDMX Technical Working Group", "official_spec", "https://sdmx.org/wp-content/uploads/SDMX_3-1-0_SECTION_2_FINAL.pdf", 2025, ["data_structure", "concept", "constraint", "version"]),
    ("sdmx.rest", "SDMX REST API", "SDMX Technical Working Group", "official_spec", "https://github.com/sdmx-twg/sdmx-rest", 2026, ["semantic_query", "availability", "data_cut"]),
    ("sdmx.vtl21", "Validation and Transformation Language 2.1", "SDMX", "standard", "https://sdmx.org/wp-content/uploads/VTL-2.1-Reference-Manual.pdf", 2024, ["formula", "transformation", "aggregation"]),
    ("w3c.data_cube", "The RDF Data Cube Vocabulary", "W3C", "recommendation", "https://www.w3.org/TR/vocab-data-cube/", 2014, ["observation", "dimension", "measure", "slice"]),
    ("w3c.dcat3", "Data Catalog Vocabulary Version 3", "W3C", "recommendation", "https://www.w3.org/TR/vocab-dcat-3/", 2024, ["catalog", "dataset", "distribution", "version"]),
    ("w3c.prov_dm", "PROV Data Model", "W3C", "recommendation", "https://www.w3.org/TR/prov-dm/", 2013, ["provenance", "entity", "activity", "derivation"]),
    ("w3c.prov_o", "PROV-O", "W3C", "recommendation", "https://www.w3.org/TR/prov-o/", 2013, ["provenance", "version", "evidence"]),
    ("w3c.owl_time", "Time Ontology in OWL", "W3C and OGC", "candidate_recommendation", "https://www.w3.org/TR/owl-time/", 2022, ["instant", "interval", "calendar", "temporal_reference_system"]),
    ("w3c.skos", "SKOS Simple Knowledge Organization System", "W3C", "recommendation", "https://www.w3.org/TR/skos-reference/", 2009, ["concept", "label", "code_list", "hierarchy"]),
    ("w3c.shacl", "Shapes Constraint Language", "W3C", "recommendation", "https://www.w3.org/TR/shacl/", 2017, ["constraint", "validation", "shape"]),
    ("w3c.rdf11", "RDF 1.1 Concepts and Abstract Syntax", "W3C", "recommendation", "https://www.w3.org/TR/rdf11-concepts/", 2014, ["identity", "graph", "literal"]),
    ("w3c.sparql11", "SPARQL 1.1 Query Language", "W3C", "recommendation", "https://www.w3.org/TR/sparql11-query/", 2013, ["semantic_query", "expression", "aggregation", "missingness"]),
    ("w3c.ssn", "Semantic Sensor Network Ontology", "W3C and OGC", "recommendation", "https://www.w3.org/TR/vocab-ssn/", 2017, ["observation", "observable_property", "procedure", "result"]),
    ("w3c.odrl", "ODRL Information Model 2.2", "W3C", "recommendation", "https://www.w3.org/TR/odrl-model/", 2018, ["permission", "purpose", "duty", "prohibition"]),
    ("qudt.catalog", "QUDT Catalog 3.5", "QUDT.org", "official_spec", "https://www.qudt.org/catalog/qudt-catalog.html", 2026, ["quantity_kind", "unit", "dimension_vector", "conversion"]),
    ("qudt.schema", "QUDT Schema", "QUDT.org", "official_spec", "https://qudt.org/schema/qudt/", 2026, ["quantity", "unit", "conversion_multiplier"]),
    ("ucum.spec", "Unified Code for Units of Measure", "UCUM", "standard", "https://ucum.org/ucum", 2024, ["unit_code", "conversion", "quantity"]),
    ("nist.si", "NIST Guide for the Use of the International System of Units", "NIST", "official_guide", "https://www.nist.gov/pml/special-publication-811", 2008, ["si_unit", "quantity", "rounding"]),
    ("iso.80000", "ISO 80000 Quantities and Units", "ISO", "standard_catalog", "https://www.iso.org/standard/76921.html", 2022, ["quantity", "unit", "dimension"]),
    ("iso.8601", "ISO 8601 Date and Time Format", "ISO", "standard", "https://www.iso.org/iso-8601-date-and-time-format.html", 2019, ["date", "time", "interval", "recurrence"]),
    ("ietf.rfc3339", "RFC 3339 Date and Time on the Internet", "IETF", "standard", "https://www.rfc-editor.org/rfc/rfc3339.html", 2002, ["timestamp", "offset", "representation"]),
    ("iana.tzdb", "Time Zone Database", "IANA", "official_registry", "https://www.iana.org/time-zones", 2026, ["time_zone", "civil_time", "version"]),
    ("iso.4217", "ISO 4217 Currency Codes", "ISO", "standard", "https://www.iso.org/standard/64758.html", 2015, ["currency", "minor_unit", "code"]),
    ("six.currency", "ISO 4217 Maintenance Agency Currency Lists", "SIX", "official_registry", "https://www.six-group.com/en/products-services/financial-information/data-standards.html", 2026, ["currency", "effective_date", "code"]),
    ("ecb.fx", "Framework for Euro Foreign Exchange Reference Rates", "European Central Bank", "official_methodology", "https://www.ecb.europa.eu/stats/pdf/exchange/Frameworkfortheeuroforeignexchangereferencerates.en.pdf", 2023, ["exchange_rate", "valuation_time", "purpose"]),
    ("jcgm.gum100", "Guide to the Expression of Uncertainty in Measurement", "JCGM and BIPM", "official_guide", "https://www.bipm.org/documents/20126/2071204/JCGM_100_2008_E.pdf", 2008, ["measurement_uncertainty", "covariance", "propagation"]),
    ("jcgm.gum6", "Developing and Using Measurement Models", "JCGM and BIPM", "official_guide", "https://doi.org/10.59161/JCGMGUM-6-2020", 2020, ["measurement_model", "uncertainty", "partial_derivative"]),
    ("jcgm.montecarlo", "GUM Supplement 1: Monte Carlo Propagation", "JCGM and BIPM", "official_guide", "https://doi.org/10.59161/JCGM101-2008", 2008, ["uncertainty", "monte_carlo", "distribution"]),
    ("jcgm.vim", "International Vocabulary of Metrology", "JCGM and BIPM", "official_vocabulary", "https://doi.org/10.59161/JCGM200-2012", 2012, ["measurement", "quantity", "uncertainty", "result"]),
    ("ogc.oms", "Observations, Measurements and Samples", "OGC", "standard", "https://www.ogc.org/standard/om/", 2023, ["observation", "result", "procedure", "feature"]),
    ("ogc.sensorthings", "OGC SensorThings API Part 1", "OGC", "standard", "https://docs.ogc.org/is/18-088/18-088.html", 2021, ["observation", "datastream", "phenomenon_time", "result_time"]),
    ("hl7.fhir.measure", "FHIR R5 Measure", "HL7 International", "standard", "https://hl7.org/fhir/R5/measure.html", 2023, ["measure_definition", "population", "stratifier", "version"]),
    ("hl7.fhir.report", "FHIR R5 MeasureReport", "HL7 International", "standard", "https://hl7.org/fhir/R5/measurereport.html", 2023, ["measure_observation", "period", "status", "evaluated_resource"]),
    ("hl7.cql", "Clinical Quality Language 1.5", "HL7 International", "standard", "https://cql.hl7.org/", 2023, ["expression", "type", "interval", "population"]),
    ("iso.sql2023", "ISO/IEC 9075-2:2023 SQL/Foundation", "ISO and IEC", "standard_catalog", "https://www.iso.org/standard/76583.html", 2023, ["query", "aggregate", "null", "window"]),
    ("postgres.aggregate", "PostgreSQL Aggregate Functions", "PostgreSQL Global Development Group", "official_docs", "https://www.postgresql.org/docs/current/functions-aggregate.html", 2026, ["aggregate", "null", "partial_mode", "ordered_set"]),
    ("postgres.window", "PostgreSQL Window Functions", "PostgreSQL Global Development Group", "official_docs", "https://www.postgresql.org/docs/current/functions-window.html", 2026, ["window", "frame", "ordering", "partition"]),
    ("sqlserver.temporal", "SQL Server Temporal Tables", "Microsoft", "official_docs", "https://learn.microsoft.com/en-us/sql/relational-databases/tables/temporal-tables", 2026, ["system_time", "history", "as_of"]),
    ("microsoft.mdx", "Multidimensional Expressions Reference", "Microsoft", "official_docs", "https://learn.microsoft.com/en-us/analysis-services/mdx/mdx-language-reference-mdx", 2026, ["cube", "measure", "calculated_member", "time_intelligence"]),
    ("microsoft.dax", "DAX Overview", "Microsoft", "official_docs", "https://learn.microsoft.com/en-us/dax/dax-overview", 2026, ["measure", "filter_context", "row_context", "calculation"]),
    ("microsoft.xmla", "XML for Analysis Protocol", "Microsoft", "official_spec", "https://learn.microsoft.com/en-us/openspecs/sql_server_protocols/ms-xmla/", 2024, ["semantic_query", "metadata", "execution"]),
    ("paper.gray_cube", "Data Cube: A Relational Aggregation Operator", "Microsoft Research", "primary_paper", "https://doi.org/10.1016/S0169-023X(96)00011-1", 1997, ["cube", "grouping", "aggregation"]),
    ("paper.summarizability_survey", "A Survey on Summarizability Issues in Multidimensional Modeling", "Data and Knowledge Engineering", "primary_paper", "https://doi.org/10.1016/j.datak.2009.07.010", 2010, ["summarizability", "hierarchy", "additivity"]),
    ("paper.detect_summarizability", "Detecting Summarizability in OLAP", "Data and Knowledge Engineering", "primary_paper", "https://doi.org/10.1016/j.datak.2013.11.001", 2014, ["summarizability", "measure", "dimension"]),
    ("paper.aggregate_views", "Algorithms for Rewriting Aggregate Queries Using Views", "Bell Labs", "primary_paper", "https://arxiv.org/abs/cs/0011024", 2001, ["materialized_view", "query_equivalence", "aggregation"]),
    ("paper.view_selection", "Implementing Data Cubes Efficiently", "ACM SIGMOD", "primary_paper", "https://doi.org/10.1145/223784.223813", 1996, ["materialization", "cube", "view_selection"]),
    ("paper.semantic_optimization", "Semantic Query Optimization in Expert Systems and Database Systems", "University of Maryland", "primary_paper", "https://dl.acm.org/doi/10.5555/102616.102621", 1986, ["semantic_query", "constraint", "optimization"]),
    ("paper.rdf_cube_olap", "Modeling and Querying Data Cubes on the Semantic Web", "Semantic Web Journal", "primary_paper", "https://doi.org/10.3233/SW-160235", 2017, ["rdf_cube", "olap", "algebra"]),
    ("paper.agg_consistency", "Aggregation Consistency Errors in Semantic Layers", "CIDR", "primary_paper", "https://arxiv.org/abs/2307.00417", 2024, ["fanout", "aggregation_consistency", "semantic_layer"]),
    ("substrait.spec", "Substrait Specification", "Substrait Project", "official_spec", "https://substrait.io/spec/specification/", 2026, ["query_ir", "functions", "types", "aggregation"]),
    ("calcite.materialized", "Apache Calcite Materialized Views", "Apache Software Foundation", "official_docs", "https://calcite.apache.org/docs/materialized_views.html", 2026, ["materialized_view", "rewrite", "query_equivalence"]),
    ("calcite.algebra", "Apache Calcite Algebra", "Apache Software Foundation", "official_docs", "https://calcite.apache.org/docs/algebra.html", 2026, ["relational_algebra", "aggregate", "join"]),
    ("dbt.metricflow_semantics", "dbt MetricFlow Metric Semantics", "dbt Labs", "official_implementation_spec", "https://github.com/dbt-labs/dbt-core/blob/main/crates/dbt-metricflow/docs/metric-semantics.md", 2026, ["metric", "scope", "grouping", "time"]),
    ("dbt.metricflow", "MetricFlow", "dbt Labs", "official_implementation", "https://github.com/dbt-labs/metricflow", 2026, ["metric_compiler", "join", "ratio", "cumulative"]),
    ("dbt.semantic_models", "dbt Semantic Models", "dbt Labs", "official_docs", "https://docs.getdbt.com/docs/build/semantic-models", 2026, ["entity", "dimension", "measure", "grain"]),
    ("dbt.metrics", "dbt Metrics", "dbt Labs", "official_docs", "https://docs.getdbt.com/docs/build/metrics-overview", 2026, ["metric", "ratio", "derived", "cumulative"]),
    ("dbt.saved_queries", "dbt Saved Queries", "dbt Labs", "official_docs", "https://docs.getdbt.com/docs/build/saved-queries", 2026, ["semantic_query", "export", "materialization"]),
    ("cube.measures", "Cube Measures", "Cube Dev", "official_docs", "https://cube.dev/docs/product/data-modeling/concepts/calculated-members", 2026, ["measure", "calculation", "aggregation"]),
    ("cube.joins", "Cube Joins", "Cube Dev", "official_docs", "https://cube.dev/docs/product/data-modeling/reference/joins", 2026, ["join", "relationship", "fanout"]),
    ("cube.preaggregations", "Cube Pre-aggregations", "Cube Dev", "official_docs", "https://cube.dev/docs/product/caching", 2026, ["preaggregation", "cache", "refresh"]),
    ("cube.rollup_match", "Cube Matching Pre-aggregations", "Cube Dev", "official_docs", "https://cube.dev/docs/product/caching/using-pre-aggregations", 2026, ["rollup", "matching", "join"]),
    ("cube.semantic_sql", "Cube Semantic SQL", "Cube Dev", "official_docs", "https://cube.dev/docs/product/apis-integrations/sql-api", 2026, ["semantic_query", "measure", "access"]),
    ("malloy.language", "Malloy Language", "Malloy Project", "official_docs", "https://docs.malloydata.dev/documentation/language", 2026, ["semantic_model", "query", "relationship"]),
    ("malloy.expressions", "Malloy Expressions", "Malloy Project", "official_docs", "https://docs.malloydata.dev/documentation/language/expressions", 2026, ["expression", "measure", "aggregation"]),
    ("malloy.repo", "Malloy Open Source Repository", "Malloy Project", "official_implementation", "https://github.com/malloydata/malloy", 2026, ["semantic_language", "compiler", "query"]),
    ("looker.measure", "LookML Measure Parameter", "Google", "official_docs", "https://cloud.google.com/looker/docs/reference/param-field-measure", 2026, ["measure", "aggregation", "filter"]),
    ("looker.symmetric", "Looker Symmetric Aggregates", "Google", "official_docs", "https://cloud.google.com/looker/docs/best-practices/understanding-symmetric-aggregates", 2026, ["fanout", "join", "aggregation"]),
    ("looker.aggregate_awareness", "Looker Aggregate Awareness", "Google", "official_docs", "https://cloud.google.com/looker/docs/aggregate_awareness", 2026, ["aggregate_table", "query_matching", "freshness"]),
    ("lightdash.metrics", "Lightdash Metrics", "Lightdash", "official_docs", "https://docs.lightdash.com/references/metrics", 2026, ["metric", "dimension", "format"]),
    ("superset.metrics", "Apache Superset Semantic Layer", "Apache Software Foundation", "official_docs", "https://superset.apache.org/docs/using-superset/creating-your-first-dashboard/#adding-a-metric", 2026, ["metric", "dataset", "calculated_column"]),
    ("gooddata.maql", "MAQL Analytical Query Language", "GoodData", "official_docs", "https://www.gooddata.com/docs/cloud/create-metrics/maql/", 2026, ["metric", "aggregation", "dimensionality"]),
    ("powerbi.star", "Power BI Star Schema Guidance", "Microsoft", "official_docs", "https://learn.microsoft.com/en-us/power-bi/guidance/star-schema", 2026, ["fact", "dimension", "grain"]),
    ("powerbi.relationships", "Power BI Model Relationships", "Microsoft", "official_docs", "https://learn.microsoft.com/en-us/power-bi/transform-model/desktop-relationships-understand", 2026, ["cardinality", "filter_propagation", "relationship"]),
    ("powerbi.aggregations", "Power BI User-defined Aggregations", "Microsoft", "official_docs", "https://learn.microsoft.com/en-us/power-bi/transform-model/aggregations-advanced", 2026, ["aggregation", "query_rewrite", "detail_table"]),
    ("snowflake.semantic_views", "Snowflake Semantic Views", "Snowflake", "official_docs", "https://docs.snowflake.com/en/user-guide/views-semantic/overview", 2026, ["semantic_view", "metric", "relationship", "query"]),
    ("databricks.metric_views", "Databricks Metric Views", "Databricks", "official_docs", "https://docs.databricks.com/aws/en/metric-views/", 2026, ["metric_view", "measure", "dimension", "version"]),
    ("kylin.model", "Apache Kylin Data Model", "Apache Software Foundation", "official_docs", "https://kylin.apache.org/docs/model/manual/model_design/", 2026, ["model", "dimension", "measure", "join"]),
    ("mondrian.schema", "Mondrian Schema", "Eclipse Foundation", "official_docs", "https://mondrian.pentaho.com/documentation/schema.php", 2020, ["cube", "measure", "dimension", "virtual_cube"]),
    ("openmetrics.spec", "OpenMetrics Specification", "CNCF", "standard", "https://openmetrics.io/", 2021, ["metric_family", "sample", "label", "timestamp"]),
    ("otel.metrics", "OpenTelemetry Metrics Data Model", "OpenTelemetry", "official_spec", "https://opentelemetry.io/docs/specs/otel/metrics/data-model/", 2026, ["metric", "aggregation_temporality", "exemplar"]),
    ("prometheus.model", "Prometheus Data Model", "Prometheus", "official_docs", "https://prometheus.io/docs/concepts/data_model/", 2026, ["time_series", "sample", "label"]),
    ("apache.ossie", "Apache Open Semantic Interchange Schema", "Apache Software Foundation", "official_implementation_spec", "https://github.com/apache/ossie/blob/main/core-spec/osi-schema.json", 2026, ["semantic_model", "dataset", "relationship", "metric"]),
    ("schema.quantitative", "Schema.org QuantitativeValue", "Schema.org", "community_spec", "https://schema.org/QuantitativeValue", 2026, ["quantity", "unit", "range"]),
    ("basel.saccr", "Standardised Approach for Counterparty Credit Risk", "Basel Committee on Banking Supervision", "official_standard", "https://www.bis.org/publ/bcbs279.pdf", 2014, ["exposure", "netting_set", "replacement_cost", "multiplier"]),
    ("basel.framework", "Basel Framework CRE52", "Basel Committee on Banking Supervision", "official_standard", "https://www.bis.org/baselframework/chapter/CRE/52.htm", 2026, ["counterparty_credit_risk", "ead", "collateral", "currency"]),
    ("who.capacity", "Primary Health Care Measurement Framework and Indicators", "World Health Organization and UNICEF", "official_guide", "https://iris.who.int/handle/10665/352201", 2022, ["bed_occupancy", "capacity", "numerator", "denominator"]),
    ("fhir.location", "FHIR R5 Location", "HL7 International", "standard", "https://hl7.org/fhir/R5/location.html", 2023, ["location", "status", "operational_status"]),
    ("fhir.encounter", "FHIR R5 Encounter", "HL7 International", "standard", "https://hl7.org/fhir/R5/encounter.html", 2023, ["encounter", "period", "subject", "location"]),
]


SOURCES = [
    {
        "source_id": sid(local), "edition": EDITION, "status": "candidate_evidence",
        "title": title, "publisher": publisher, "source_kind": kind, "url": url,
        "publication_year": year, "accessed_at": ACCESSED, "supports_topics": topics,
        "authority_scope": "Authoritative only for the named standard, implementation, registry, methodology, or study.",
        "limitations": ["Inclusion does not imply universal support or transfer semantic ownership to the source."],
    }
    for local, title, publisher, kind, url, year, topics in SOURCE_ROWS
]


CONTEXT_ROWS = [
    ("analytical_entity", "Analytical Entity Role", "Which owned domain concept plays an analytical entity role?", ["entity_role", "semantic_key"], ["business_identity", "physical_table"]),
    ("fact_role", "Fact Occurrence", "What assertion is treated as a fact occurrence at an exact grain?", ["fact_role", "fact_occurrence"], ["event_truth", "observation_procedure"]),
    ("event_semantics", "Event Semantics", "What happened, when, and with which event identity and correction posture?", ["event_role", "event_identity", "event_time"], ["fact_row", "recording_time"]),
    ("observation_assertion", "Observation Assertion", "Who observed which property of which feature using which procedure and result?", ["observation", "observable_property", "result_role"], ["metric_definition", "accepted_business_fact"]),
    ("grain_population", "Grain and Population", "What does one occurrence represent and which occurrences are eligible?", ["grain", "population_contract", "uniqueness"], ["primary_key", "sample_estimator"]),
    ("measure_definition", "Measure Definition", "What quantity or value is recorded and what aggregation posture accompanies it?", ["measure", "measure_kind", "aggregation_posture"], ["metric", "kpi"]),
    ("dimension_definition", "Dimension Definition", "Along which governed attribute may results be sliced or grouped?", ["dimension", "dimension_value_domain"], ["business_term", "chart_axis"]),
    ("member_code_list", "Dimension Member and Code List", "Which governed member denotes which domain concept during which interval?", ["dimension_member", "code_list_binding"], ["business_concept_owner", "display_label"]),
    ("hierarchy_rollup", "Hierarchy and Roll-up", "Which levels and parent relations permit which roll-ups?", ["hierarchy", "level", "rollup_relation"], ["taxonomy_owner", "sort_order"]),
    ("semantic_relationship", "Semantic Relationship", "Which domain relation is projected into the analytical model?", ["analytical_relationship", "endpoint_role"], ["domain_relation", "foreign_key"]),
    ("join_path", "Valid Join Path", "Which path may connect semantic roles under exact predicates and temporal alignment?", ["join_path", "join_predicate", "path_precedence"], ["physical_join_algorithm", "entity_relation"]),
    ("fanout_safety", "Fanout Safety", "Does joining preserve aggregation identity, and what proof or rewrite is required?", ["fanout_effect", "join_safety_proof", "deduplication_key"], ["join_cost", "symmetric_aggregate_vendor_feature"]),
    ("formula_ast", "Pure Formula AST", "What does a provider-neutral expression mean as a typed syntax tree?", ["formula_ast", "node_kind", "source_span"], ["named_formula", "query_plan"]),
    ("semantic_type_system", "Formula Semantic Type System", "Which types, dimensions, refinements and coercions make expressions well formed?", ["semantic_type", "type_rule", "coercion"], ["physical_carrier_type", "display_format"]),
    ("operator_registry", "Operator Registry", "Which pure operators exist with which signatures and algebraic laws?", ["operator_signature", "operator_law"], ["runtime_function_provider", "enterprise_formula"]),
    ("function_registry", "Function Registry", "Which named functions and editions exist with which effects and partiality?", ["function_signature", "function_edition", "effect_contract"], ["formula_definition", "provider_udf"]),
    ("variable_parameter", "Variable and Parameter", "Which free inputs exist, who supplies them, and what defaults and constraints apply?", ["variable", "parameter", "default_policy"], ["dimension_member", "ambient_session_state"]),
    ("formula_definition", "Formula Definition Registry", "Which immutable named formula edition is approved, deprecated, or recalled?", ["formula_definition", "formula_edition", "dependency"], ["formula_expression", "metric_definition"]),
    ("formula_binding", "Formula Binding", "To which exact semantic owners and editions does every reference bind?", ["formula_binding", "reference_resolution"], ["physical_column_mapping", "evaluation"]),
    ("formula_evaluation", "Formula Evaluation", "How is a bound formula evaluated for explicit inputs, cut, budgets and effects?", ["evaluation_request", "evaluation_receipt", "value_or_error"], ["formula_meaning", "metric_publication"]),
    ("partiality_missingness", "Partiality and Missingness", "How are absent, null, unknown, suppressed, not-applicable, error and zero distinguished?", ["absence_reason", "partial_value", "error_value"], ["zero", "empty_population"]),
    ("unit_quantity", "Quantity and Unit", "Which quantity kind, dimension vector and unit govern a value and conversion?", ["quantity", "unit", "conversion_rule"], ["currency_valuation", "display_suffix"]),
    ("currency_valuation", "Currency Valuation", "Which monetary amount is valued into which currency using which source, side and time?", ["money", "exchange_rate", "valuation_policy"], ["unit_conversion", "accounting_recognition"]),
    ("ratio_rate_index", "Ratio, Rate and Index", "What numerator, denominator, scale, base and interpretation define a quotient-like value?", ["ratio", "rate", "percentage", "index"], ["plain_decimal", "target"]),
    ("aggregation_algebra", "Aggregation Algebra", "Which fold maps a bag or ordered collection to a typed result?", ["aggregate_signature", "state_algebra", "empty_input_policy"], ["statistical_estimator_authority", "grouping"]),
    ("reaggregation", "Reaggregation and Roll-up", "Can an aggregate state or result be combined at a coarser grain without meaning loss?", ["reaggregation_rule", "sufficient_state", "rollup_proof"], ["recompute", "additivity"]),
    ("additivity_posture", "Additivity and Summarizability", "Across which dimensions and levels is a measure additive, semi-additive or non-additive?", ["additivity_posture", "summarizability_constraint"], ["decomposability", "format"]),
    ("decomposable_state", "Decomposable Aggregate State", "What mergeable sufficient state preserves an aggregation under partitioning?", ["partial_state", "merge_law", "finalizer"], ["displayed_result", "additivity"]),
    ("population_cohort", "Population and Cohort", "Which entities or occurrences enter, exit and remain in a metric population?", ["population", "cohort", "eligibility", "index_event"], ["filter_only", "sample"]),
    ("filter_predicate", "Filter and Predicate", "Which typed predicate restricts which semantic scope and at what evaluation phase?", ["predicate", "filter_scope", "filter_phase"], ["access_policy", "visual_selection"]),
    ("metric_definition", "Metric Definition", "What measure over what population, grain, filter, aggregation, dimensions and time is meant?", ["metric", "metric_coordinate", "metric_dependency"], ["measure", "kpi", "metric_observation"]),
    ("kpi_target", "KPI and Target", "Which governed metric is designated key for a purpose and compared with which target?", ["kpi_designation", "target", "threshold"], ["metric", "observed_value", "benchmark"]),
    ("benchmark_reference", "Benchmark Reference", "Which external or internal reference population and edition supplies a comparison value?", ["benchmark", "reference_population", "comparison_policy"], ["target", "observed_metric"]),
    ("calendar_time", "Calendar and Time Intelligence", "Which calendar, time zone, bucket, window and alignment semantics apply?", ["calendar", "time_bucket", "window", "timezone_policy"], ["valid_time", "fiscal_policy"]),
    ("fiscal_period", "Fiscal Period", "How are governed fiscal years, quarters, weeks and adjustment periods identified?", ["fiscal_calendar", "fiscal_period", "close_policy"], ["gregorian_month", "recording_time"]),
    ("bitemporal_interpretation", "Bitemporal Interpretation", "What was valid in the domain and what was recorded by the system at independently chosen instants?", ["valid_time", "recording_time", "bitemporal_cut"], ["event_time", "query_time"]),
    ("asof_cut", "As-of and Data Cut", "Which editions and occurrences are visible at an exact semantic and data cut?", ["as_of", "data_cut", "watermark"], ["wall_clock_now", "cache_age"]),
    ("validity_finality", "Validity and Finality", "Is a value provisional, complete, revised, corrected, superseded or recalled?", ["validity_status", "finality_status", "revision_policy"], ["freshness", "truth"]),
    ("uncertainty", "Metric Uncertainty", "Which uncertainty representation, dependence and propagation method accompanies a value?", ["uncertainty", "covariance", "confidence_interval", "distribution"], ["missingness", "quality_score"]),
    ("semantic_model", "Semantic Model", "Which versioned entities, facts, measures, dimensions, joins, formulas and metrics compose?", ["semantic_model", "component_reference"], ["business_ontology", "physical_schema"]),
    ("model_publication", "Semantic Publication", "Which validated semantic model edition is available to which consumer contract?", ["semantic_publication", "consumer_contract"], ["data_publication", "dashboard"]),
    ("metric_governance", "Metric Governance", "Who may propose, approve, publish, deprecate or recall a metric for a purpose?", ["metric_authority", "approval", "publication", "recall"], ["data_access", "formula_registry_authority"]),
    ("semantic_query", "Semantic Query", "Which governed metrics, dimensions, filters, time and cut are requested?", ["semantic_query", "selection", "grouping"], ["sql_text", "dashboard_tile"]),
    ("query_validation", "Semantic Query Validation", "Is the query type-safe, grain-safe, join-safe, authorized and temporally determinate?", ["query_validation", "proof_obligation", "refusal"], ["query_optimization", "syntax_parsing"]),
    ("semantic_lowering", "Semantic Lowering", "Can a validated request be lowered without changing result meaning?", ["lowering_plan", "preservation_evidence"], ["physical_optimization", "metric_definition"]),
    ("materialization", "Metric Materialization", "Which metric states or observations are persisted for which cuts and invalidation policy?", ["materialization", "refresh_policy", "coverage_region"], ["source_fact", "dashboard_extract"]),
    ("semantic_cache", "Semantic Cache Equivalence", "When does a cached result semantically answer a request despite different query text?", ["semantic_fingerprint", "coverage_containment", "cache_reuse_proof"], ["sql_text_match", "client_cache"]),
    ("observation_receipt", "Metric Observation and Receipt", "What value was produced under which metric, formula, model, cut and execution evidence?", ["metric_observation", "evaluation_receipt", "supersession"], ["metric_definition", "business_fact"]),
    ("disclosure", "Semantic Disclosure", "Which definition, cut, unit, uncertainty, finality, target and limitations must accompany a result?", ["disclosure_contract", "explanation_payload"], ["visualization", "provenance_capture"]),
    ("access_purpose", "Access and Purpose", "May an actor evaluate or disclose a metric for an explicit purpose and population?", ["semantic_access_requirement", "purpose_binding", "projection_policy"], ["metric_authority", "data_entitlement"]),
    ("lifecycle_version", "Semantic Lifecycle and Version", "How do identity, edition, state and compatibility evolve without rewriting history?", ["semantic_identity", "edition", "lifecycle_state"], ["mutable_name", "data_cut"]),
    ("compatibility_migration", "Compatibility and Migration", "Can consumers move between semantic editions and what transformations are required?", ["compatibility_relation", "migration_plan", "consumer_obligation"], ["provider_upgrade", "silent_alias"]),
]


CONTEXT_EVIDENCE = {
    "formula": ["oasis.openformula14", "sdmx.vtl21", "substrait.spec"],
    "time": ["w3c.owl_time", "iso.8601", "iana.tzdb"],
    "metric": ["sdmx.31", "hl7.fhir.measure", "dbt.metricflow_semantics"],
    "join": ["paper.agg_consistency", "cube.joins", "looker.symmetric"],
    "unit": ["qudt.catalog", "ucum.spec", "jcgm.vim"],
    "query": ["w3c.sparql11", "dbt.metricflow_semantics", "substrait.spec"],
    "default": ["sdmx.31", "w3c.data_cube", "w3c.prov_dm"],
}


def context_evidence(local: str) -> list[str]:
    if "formula" in local or local in {"semantic_type_system", "operator_registry", "function_registry", "variable_parameter", "partiality_missingness"}:
        key = "formula"
    elif "time" in local or local in {"fiscal_period", "asof_cut", "validity_finality"}:
        key = "time"
    elif "metric" in local or local in {"measure_definition", "kpi_target", "benchmark_reference", "population_cohort"}:
        key = "metric"
    elif local in {"semantic_relationship", "join_path", "fanout_safety", "aggregation_algebra", "reaggregation", "additivity_posture", "decomposable_state"}:
        key = "join"
    elif local in {"unit_quantity", "currency_valuation", "ratio_rate_index", "uncertainty"}:
        key = "unit"
    elif local in {"semantic_query", "query_validation", "semantic_lowering", "materialization", "semantic_cache"}:
        key = "query"
    else:
        key = "default"
    return [sid(x) for x in CONTEXT_EVIDENCE[key]]


CONTEXTS = [
    {
        "context_id": cid(local), "edition": EDITION, "status": "candidate",
        "candidate_status": "split_merge_adjudication_required", "name": name,
        "sovereign_question": question, "owns": owns, "excludes": excludes,
        "imports": ["owned_domain_concept", "typed_data_shape", "authority", "evidence"],
        "exports": [f"{local}_contract"],
        "invariants": ["Every exported reference has one owner and positive edition.", "Unknown meaning is refused rather than inferred from names or carriers."],
        "refusals": ["unknown_owner", "ambiguous_reference", "unproven_semantics"],
        "evidence_refs": context_evidence(local),
    }
    for local, name, question, owns, excludes in CONTEXT_ROWS
]


TYPE_ROWS = [
    ("boolean", "Boolean", "logical", "two-valued truth after any missingness has been resolved"),
    ("three_valued_truth", "Three-valued truth", "logical", "true, false or unknown with explicit truth tables"),
    ("integer", "Integer", "numeric", "unbounded mathematical integer or bounded carrier with declared overflow"),
    ("decimal", "Decimal", "numeric", "base-ten value with declared precision, scale and rounding"),
    ("rational", "Rational", "numeric", "exact numerator and nonzero denominator reduced by a canonical law"),
    ("real_approximation", "Real approximation", "numeric", "finite representation with explicit error and special-value posture"),
    ("text", "Text", "lexical", "Unicode scalar sequence with declared normalization and collation when compared"),
    ("code", "Governed code", "nominal", "code plus code-list owner and edition"),
    ("identifier", "Identifier", "nominal", "opaque identity scoped by assigning authority"),
    ("date", "Calendar date", "temporal", "date in a named calendar without time of day"),
    ("instant", "Instant", "temporal", "position on a named time scale"),
    ("local_datetime", "Local date-time", "temporal", "calendar and clock fields without a unique instant"),
    ("zoned_instant", "Zoned instant", "temporal", "instant plus time-zone database edition and presentation zone"),
    ("interval", "Temporal interval", "temporal", "ordered endpoints with declared open or closed bounds"),
    ("duration", "Duration", "temporal", "elapsed quantity on a time scale"),
    ("calendar_period", "Calendar period", "temporal", "calendar-relative amount whose duration depends on anchor"),
    ("quantity", "Quantity", "quantity", "numeric magnitude plus quantity kind and unit"),
    ("unit", "Unit", "quantity", "identified scale for a quantity kind and dimension vector"),
    ("money", "Money", "monetary", "decimal amount plus currency code and minor-unit policy"),
    ("exchange_rate", "Exchange rate", "monetary", "directed source-to-target currency ratio with valuation context"),
    ("ratio", "Ratio", "quotient", "numerator and denominator meanings with scale and zero-denominator law"),
    ("percentage", "Percentage", "quotient", "dimensionless ratio presented with scale one hundred"),
    ("rate", "Rate", "quotient", "quantity per exposure, population or time denominator"),
    ("index", "Index", "quotient", "relative value against an identified base edition and base period"),
    ("count", "Count", "quantity", "nonnegative integer number of eligible occurrences"),
    ("probability", "Probability", "uncertainty", "dimensionless value constrained to the closed unit interval"),
    ("estimate", "Estimate", "uncertainty", "point value paired with estimator and population interpretation"),
    ("standard_uncertainty", "Standard uncertainty", "uncertainty", "standard deviation associated with a measured quantity"),
    ("covariance_matrix", "Covariance matrix", "uncertainty", "symmetric positive semidefinite dependence representation"),
    ("confidence_interval", "Confidence interval", "uncertainty", "interval plus confidence level and construction method"),
    ("distribution", "Probability distribution", "uncertainty", "law with parameters, support and conditioning context"),
    ("absence", "Absence", "partial", "typed absence carrying a governed reason"),
    ("error", "Formula error", "partial", "typed failure value distinct from absence"),
    ("dimension_member", "Dimension member", "semantic", "member identity in one dimension and code-list edition"),
    ("grain", "Analytical grain", "semantic", "set of semantic roles that identify one occurrence"),
    ("population", "Population", "semantic", "eligibility predicate plus entry, exit and temporal interpretation"),
    ("metric_reference", "Metric reference", "semantic", "metric identity and exact edition"),
    ("metric_observation", "Metric observation", "semantic", "evaluated metric value pinned to cut and receipt"),
    ("data_cut", "Data cut", "semantic", "source editions, temporal visibility and completeness boundary"),
    ("semantic_version", "Semantic version", "semantic", "positive edition with lifecycle and compatibility metadata"),
    ("purpose", "Purpose", "policy", "governed intended-use concept and edition"),
    ("access_scope", "Access scope", "policy", "authorized semantic and population projection"),
]


TYPE_CONTEXT = {
    "temporal": "calendar_time", "quantity": "unit_quantity", "monetary": "currency_valuation",
    "quotient": "ratio_rate_index", "uncertainty": "uncertainty", "partial": "partiality_missingness",
    "semantic": "semantic_type_system", "policy": "access_purpose",
}


def type_laws(family: str) -> list[str]:
    common = ["Equality is semantic and never inferred from carrier byte equality.", "Any coercion is explicit and editioned."]
    specific = {
        "numeric": ["Overflow, precision and rounding posture are explicit."],
        "temporal": ["Calendar, clock, time scale and zone ambiguity are refused."],
        "quantity": ["Addition requires compatible quantity kind and unit conversion."],
        "monetary": ["Arithmetic never performs ambient exchange-rate lookup."],
        "quotient": ["The denominator meaning and zero law are part of the type."],
        "uncertainty": ["Dependence assumptions accompany any propagated result."],
        "partial": ["Absence, error and present zero are disjoint constructors."],
        "nominal": ["Codes from different owner editions are not equal by lexical spelling alone."],
    }
    return common + specific.get(family, ["Ordering and arithmetic are unavailable unless declared."])


SEMANTIC_RECORDS: list[dict[str, Any]] = []
for local, name, family, meaning in TYPE_ROWS:
    SEMANTIC_RECORDS.append({
        "record_id": f"type.{PREFIX}.{local}", "record_kind": "semantic_type", "edition": EDITION,
        "status": "candidate", "name": name, "owner_context_ref": cid(TYPE_CONTEXT.get(family, "semantic_type_system")),
        "meaning": meaning, "signature": {"family": family, "parameters": ["semantic_owner", "edition"]},
        "effects": [], "partiality": "total_construction_after_validation", "laws": type_laws(family),
        "refusal_conditions": ["ambiguous_owner", "invalid_parameter", "implicit_lossy_coercion"],
        "evidence_refs": context_evidence(TYPE_CONTEXT.get(family, "semantic_type_system"))[:2],
    })


AST_ROWS = [
    ("literal", "literal value with exact semantic type"), ("variable_ref", "lexical variable reference resolved by binding"),
    ("parameter_ref", "caller parameter reference with declared constraints"), ("measure_ref", "versioned measure reference"),
    ("metric_ref", "versioned metric reference"), ("dimension_ref", "versioned dimension reference"),
    ("member_ref", "versioned dimension-member reference"), ("unary_call", "unary operator application"),
    ("binary_call", "binary operator application"), ("function_call", "versioned function application"),
    ("if_then_else", "conditional with type-compatible branches"), ("case_when", "ordered guarded branches plus else"),
    ("let_binding", "lexically scoped immutable binding"), ("lambda", "pure typed function abstraction when profile permits"),
    ("list_literal", "ordered homogeneous collection"), ("set_literal", "unordered duplicate-free collection under semantic equality"),
    ("record_literal", "named product fields"), ("field_access", "total or explicitly partial product-field access"),
    ("interval_literal", "bounded interval with endpoint closure"), ("quantity_literal", "magnitude and governed unit"),
    ("error_literal", "declared formula error constructor"), ("absence_literal", "declared absence reason constructor"),
    ("aggregate_call", "aggregation over an explicitly scoped population"), ("window_call", "windowed evaluation with partition, order and frame"),
    ("as_of_scope", "subexpression evaluated under a pinned bitemporal cut"), ("annotation", "non-semantic source metadata excluded from equivalence"),
]
for local, meaning in AST_ROWS:
    SEMANTIC_RECORDS.append({
        "record_id": f"ast.{PREFIX}.{local}", "record_kind": "formula_ast_node", "edition": EDITION,
        "status": "candidate", "name": local.replace("_", " ").title(), "owner_context_ref": cid("formula_ast"),
        "meaning": meaning, "signature": {"node_kind": local, "required_fields": ["source_span", "inferred_type", "children"]},
        "effects": [] if local not in {"aggregate_call", "window_call", "as_of_scope"} else ["semantic_data_read"],
        "partiality": "declared_by_node_and_children",
        "laws": ["Child order is semantic only where the node declares it.", "Source formatting is excluded from normalized AST identity."],
        "refusal_conditions": ["missing_child", "type_error", "unbounded_depth", "unresolved_reference"],
        "evidence_refs": [sid("oasis.openformula14"), sid("sdmx.vtl21")],
    })


OPERATOR_ROWS = [
    ("unary_plus", "+x", "Numeric<T> -> T", 90, "right", "typed identity"),
    ("unary_minus", "-x", "AdditiveGroup<T> -> T", 90, "right", "additive inverse"),
    ("power", "x ^ y", "Numeric<T>,Integer -> T", 80, "right", "integer exponentiation under dimensional rules"),
    ("multiply", "x * y", "T,U -> Product<T,U>", 70, "left", "multiplication with quantity-dimension composition"),
    ("divide", "x / y", "T,U -> Quotient<T,U>", 70, "left", "partial division with explicit zero law"),
    ("add", "x + y", "Compatible<T>,Compatible<T> -> T", 60, "left", "addition after exact compatibility proof"),
    ("subtract", "x - y", "Compatible<T>,Compatible<T> -> T", 60, "left", "subtraction after exact compatibility proof"),
    ("concatenate", "x || y", "Text,Text -> Text", 55, "left", "Unicode text concatenation without collation inference"),
    ("range", "x .. y", "Ordered<T>,Ordered<T> -> Interval<T>", 50, "none", "interval construction with declared endpoint closure"),
    ("equal", "x = y", "Comparable<T>,Comparable<T> -> Truth", 40, "none", "semantic equality"),
    ("not_equal", "x != y", "Comparable<T>,Comparable<T> -> Truth", 40, "none", "semantic inequality"),
    ("less", "x < y", "Ordered<T>,Ordered<T> -> Truth", 40, "none", "strict semantic order"),
    ("less_equal", "x <= y", "Ordered<T>,Ordered<T> -> Truth", 40, "none", "nonstrict semantic order"),
    ("greater", "x > y", "Ordered<T>,Ordered<T> -> Truth", 40, "none", "reverse strict semantic order"),
    ("greater_equal", "x >= y", "Ordered<T>,Ordered<T> -> Truth", 40, "none", "reverse nonstrict semantic order"),
    ("set_intersection", "x INTERSECT y", "Set<T>,Set<T> -> Set<T>", 35, "left", "set intersection under semantic equality"),
    ("set_union", "x UNION y", "Set<T>,Set<T> -> Set<T>", 30, "left", "set union under semantic equality"),
    ("logical_not", "NOT x", "Truth -> Truth", 25, "right", "declared truth-table negation"),
    ("logical_and", "x AND y", "Truth,Truth -> Truth", 20, "left", "declared truth-table conjunction"),
    ("logical_or", "x OR y", "Truth,Truth -> Truth", 15, "left", "declared truth-table disjunction"),
    ("coalesce", "x ?? y", "Partial<T>,T -> T", 10, "right", "reason-scoped fallback; never implicit zero fill"),
]
for local, syntax, signature, precedence, associativity, meaning in OPERATOR_ROWS:
    SEMANTIC_RECORDS.append({
        "record_id": f"operator.{PREFIX}.{local}", "record_kind": "formula_operator", "edition": EDITION,
        "status": "candidate", "name": local.replace("_", " ").title(), "owner_context_ref": cid("operator_registry"),
        "meaning": meaning, "signature": {"syntax": syntax, "type_signature": signature, "precedence": precedence, "associativity": associativity},
        "effects": [], "partiality": "declared_by_signature_and_operand_types",
        "laws": ["Precedence and associativity are syntax laws, not evaluation algorithms.", "Operator edition and truth/absence profile participate in normalized identity."],
        "refusal_conditions": ["type_mismatch", "ambiguous_precedence", "unsupported_truth_or_absence_profile"],
        "evidence_refs": [sid("oasis.openformula14"), sid("sdmx.vtl21")],
    })


FUNCTION_ROWS = [
    ("add", "T,T -> T", "add compatible numeric or quantity values", "total_after_typecheck"),
    ("subtract", "T,T -> T", "subtract compatible numeric or quantity values", "total_after_typecheck"),
    ("multiply", "T,U -> Product<T,U>", "multiply values and compose quantity dimensions", "total_after_typecheck"),
    ("divide", "T,U -> Quotient<T,U>", "divide values and compose dimensions", "partial_zero_denominator"),
    ("negate", "T -> T", "additive inverse", "partial_overflow_if_bounded"),
    ("absolute", "OrderedRing<T> -> T", "absolute magnitude", "partial_minimum_bounded_integer"),
    ("power_integer", "T,Integer -> T", "integer exponentiation under dimension rules", "partial_domain_or_overflow"),
    ("sqrt", "Quantity<D^2> -> Quantity<D>", "principal square root", "partial_negative_or_dimension"),
    ("exp", "Dimensionless -> Dimensionless", "natural exponential", "partial_range"),
    ("log", "Dimensionless -> Dimensionless", "natural logarithm", "partial_nonpositive"),
    ("floor", "Decimal -> Integer", "greatest integer not exceeding input", "total"),
    ("ceiling", "Decimal -> Integer", "least integer not below input", "total"),
    ("round", "Decimal,Scale,RoundingMode -> Decimal", "round with explicit scale and mode", "total_after_validation"),
    ("clamp", "Ordered<T>,T,T -> T", "bound a value to a valid closed interval", "partial_invalid_bounds"),
    ("min_scalar", "Ordered<T>,T -> T", "select the lesser of two scalar values under a declared order", "partial_unordered"),
    ("max_scalar", "Ordered<T>,T -> T", "select the greater of two scalar values under a declared order", "partial_unordered"),
    ("equal", "T,T -> Boolean", "semantic equality", "total_after_typecheck"),
    ("compare", "Ordered<T>,T -> Ordering", "semantic total or declared partial ordering", "partial_unordered"),
    ("logical_and", "Truth,Truth -> Truth", "declared truth-table conjunction", "total"),
    ("logical_or", "Truth,Truth -> Truth", "declared truth-table disjunction", "total"),
    ("logical_not", "Truth -> Truth", "declared truth-table negation", "total"),
    ("if_then_else", "Boolean,T,T -> T", "select one branch without evaluating the other", "branch_partiality"),
    ("coalesce_by_reason", "Partial<T>,Set<AbsenceReason>,T -> T", "replace only enumerated absence reasons", "partial_unhandled_error"),
    ("is_absent", "Partial<T> -> Boolean", "test absence constructor", "total"),
    ("absence_reason", "Partial<T> -> AbsenceReason", "extract absence reason", "partial_present_value"),
    ("safe_divide", "T,T,ZeroPolicy -> Partial<Ratio>", "divide using an explicit zero-denominator policy", "declared_by_policy"),
    ("ratio", "T,T,Scale -> Ratio", "construct a governed ratio", "partial_zero_denominator"),
    ("convert_unit", "Quantity,Unit,ConversionEdition -> Quantity", "convert compatible units using explicit rule", "partial_incompatible_dimension"),
    ("value_currency", "Money,Currency,Rate,ValuationTime -> Money", "value money through an explicit directed exchange rate", "partial_missing_rate"),
    ("interval_contains", "Interval<T>,T -> Boolean", "test endpoint-aware interval membership", "total_after_validation"),
    ("interval_overlaps", "Interval<T>,Interval<T> -> Boolean", "test endpoint-aware overlap", "total_after_validation"),
    ("date_add_period", "Date,CalendarPeriod,CalendarPolicy -> Date", "calendar-relative date arithmetic", "partial_invalid_date_policy"),
    ("instant_add_duration", "Instant,Duration -> Instant", "time-scale duration arithmetic", "partial_range"),
    ("date_diff", "Date,Date,CalendarUnit,Calendar -> Integer", "calendar-boundary difference", "total_after_binding"),
    ("bucket_start", "Instant,BucketSpec -> Instant", "map an instant to a governed bucket start", "partial_zone_transition"),
    ("bucket_end", "Instant,BucketSpec -> Instant", "map an instant to a governed bucket end", "partial_zone_transition"),
    ("period_offset", "Period,Count,Calendar -> Period", "offset a governed period by calendar positions", "partial_calendar_gap"),
    ("as_of", "Expression,BitemporalCut -> T", "evaluate an expression under explicit temporal visibility", "effect_semantic_data_read"),
    ("member_of", "DimensionMember,DimensionEdition -> Boolean", "test exact dimension membership", "partial_unknown_member"),
    ("ancestor_at", "Member,Level,ValidTime -> Member", "resolve a hierarchy ancestor at valid time", "partial_non_strict_or_missing_path"),
    ("code_map", "Code,MappingEdition,ValidTime -> Code", "apply an editioned code mapping", "partial_unmapped_or_ambiguous"),
    ("cast_checked", "S,SemanticType -> T", "perform only an explicitly admitted coercion", "partial_invalid_representation"),
    ("parse_date", "Text,Pattern,Calendar -> Date", "parse without ambient locale", "partial_invalid_text"),
    ("normalize_text", "Text,UnicodeForm -> Text", "apply explicit Unicode normalization", "total"),
    ("set_contains", "Set<T>,T -> Boolean", "membership under semantic equality", "total_after_typecheck"),
    ("set_union", "Set<T>,Set<T> -> Set<T>", "union under semantic equality", "total_after_typecheck"),
    ("population_filter", "Population,Predicate -> Population", "derive a population with traceable eligibility refinement", "effect_semantic_data_read"),
    ("cohort_entry", "Entity,CohortDefinition -> Partial<Instant>", "derive the declared cohort entry instant", "effect_semantic_data_read"),
    ("lag_value", "T,OrderSpec,Offset -> Partial<T>", "obtain a prior ordered value", "effect_window_state"),
    ("lead_value", "T,OrderSpec,Offset -> Partial<T>", "obtain a following ordered value", "effect_window_state"),
    ("rolling_scope", "Population,WindowSpec -> Population", "derive a bounded rolling population", "effect_window_state"),
    ("uncertainty_linear", "Expression,Covariance -> StandardUncertainty", "first-order uncertainty propagation", "partial_missing_dependence"),
    ("uncertainty_monte_carlo", "Expression,Distributions,Seed,Trials -> Distribution", "Monte Carlo propagation with explicit reproducibility inputs", "effect_bounded_random_sampling"),
]
for local, signature, meaning, partiality in FUNCTION_ROWS:
    effects = []
    if partiality.startswith("effect_"):
        effects = [partiality.removeprefix("effect_")]
    SEMANTIC_RECORDS.append({
        "record_id": f"function.{PREFIX}.{local}", "record_kind": "formula_function", "edition": EDITION,
        "status": "candidate", "name": local.replace("_", " ").title(), "owner_context_ref": cid("function_registry"),
        "meaning": meaning, "signature": signature, "effects": effects, "partiality": partiality,
        "laws": ["Arguments are evaluated under declared strictness and order.", "Function edition participates in formula identity."],
        "refusal_conditions": ["signature_mismatch", "undeclared_effect", "unsupported_partiality"],
        "evidence_refs": [sid("oasis.openformula14"), sid("jcgm.gum6") if "uncertainty" in local else sid("sdmx.vtl21")],
    })


AGG_ROWS = [
    ("sum", "exact", "commutative_monoid_when_present_policy_and_numeric_algebra_allow", "zero_or_absent_by_policy", ["sum"]),
    ("count_rows", "exact", "commutative_monoid", "zero", ["count"]),
    ("count_present", "exact", "commutative_monoid", "zero", ["count"]),
    ("count_distinct", "exact", "set_union_state", "zero", ["set"]),
    ("minimum", "exact", "commutative_idempotent_semigroup", "absent", ["candidate_min"]),
    ("maximum", "exact", "commutative_idempotent_semigroup", "absent", ["candidate_max"]),
    ("arithmetic_mean", "exact_subject_to_numeric_posture", "algebraic", "absent", ["sum", "count"]),
    ("weighted_mean", "exact_subject_to_numeric_posture", "algebraic", "absent_or_error_zero_weight", ["weighted_sum", "weight_sum"]),
    ("variance_population", "exact_subject_to_numeric_posture", "algebraic_mergeable", "absent", ["count", "mean", "m2"]),
    ("variance_sample", "exact_subject_to_numeric_posture", "algebraic_mergeable", "absent_if_count_lt_2", ["count", "mean", "m2"]),
    ("standard_deviation", "exact_subject_to_numeric_posture", "algebraic_via_variance", "absent", ["count", "mean", "m2"]),
    ("covariance", "exact_subject_to_numeric_posture", "algebraic_mergeable", "absent", ["count", "mean_x", "mean_y", "co_moment"]),
    ("correlation", "exact_subject_to_numeric_posture", "algebraic_via_covariance", "absent_zero_variance", ["covariance_state"]),
    ("median", "exact", "holistic", "absent", ["ordered_multiset"]),
    ("percentile_cont", "exact", "holistic_ordered", "absent", ["ordered_multiset", "interpolation_policy"]),
    ("percentile_disc", "exact", "holistic_ordered", "absent", ["ordered_multiset", "tie_policy"]),
    ("mode", "exact", "algebraic_frequency_map", "absent", ["frequency_map", "tie_policy"]),
    ("boolean_all", "exact", "commutative_monoid_under_declared_truth_table", "identity_or_absent_by_policy", ["truth_state"]),
    ("boolean_any", "exact", "commutative_monoid_under_declared_truth_table", "identity_or_absent_by_policy", ["truth_state"]),
    ("first_by", "exact", "ordered_noncommutative", "absent", ["value", "order_key", "tie_key"]),
    ("last_by", "exact", "ordered_noncommutative", "absent", ["value", "order_key", "tie_key"]),
    ("arg_min", "exact", "algebraic_with_tie_state", "absent", ["value", "key", "tie_key"]),
    ("arg_max", "exact", "algebraic_with_tie_state", "absent", ["value", "key", "tie_key"]),
    ("collect_list", "exact", "ordered_noncommutative", "empty_list_or_absent_by_policy", ["ordered_list"]),
    ("collect_set", "exact", "set_union_state", "empty_set", ["set"]),
    ("histogram", "exact_if_fixed_bins", "algebraic_bin_counts", "zero_bins", ["bin_spec", "counts"]),
    ("approx_distinct_hll", "bounded_approximation", "mergeable_sketch", "zero", ["precision", "registers"]),
    ("approx_quantile_tdigest", "empirical_approximation", "mergeable_sketch_order_sensitive", "absent", ["compression", "centroids"]),
    ("ratio_of_sums", "exact_subject_to_numeric_posture", "algebraic", "absent_or_error_zero_denominator", ["numerator_sum", "denominator_sum"]),
    ("index_chain", "exact_subject_to_method", "method_specific", "absent", ["base_value", "link_factors", "chain_method"]),
]
for local, exactness, decomposability, empty_policy, state in AGG_ROWS:
    SEMANTIC_RECORDS.append({
        "record_id": f"aggregation.{PREFIX}.{local}", "record_kind": "aggregation", "edition": EDITION,
        "status": "candidate", "name": local.replace("_", " ").title(), "owner_context_ref": cid("aggregation_algebra"),
        "meaning": f"Aggregate eligible inputs using the governed {local.replace('_', ' ')} contract.",
        "signature": {"input": "Bag<T> or OrderedBag<T> as declared", "output": "typed_result", "sufficient_state": state},
        "effects": [], "partiality": empty_policy, "exactness": exactness, "decomposability": decomposability,
        "laws": ["Merge is permitted only for the declared sufficient state.", "Null and absence filtering is an input policy, not an implicit aggregate convention."],
        "refusal_conditions": ["undeclared_empty_input_policy", "incompatible_reaggregation", "missing_order_or_tie_policy"],
        "evidence_refs": [sid("postgres.aggregate"), sid("paper.summarizability_survey")],
    })


JOIN_ROWS = [
    ("one_to_one_preserving", "one_to_one", "both", "preserves both endpoint grains if predicates are total and unique"),
    ("many_to_one_preserving_left", "many_to_one", "left", "preserves left grain when the right match is at most one"),
    ("one_to_many_fanout_left", "one_to_many", "right", "duplicates left occurrences and is unsafe for naive left aggregation"),
    ("many_to_many_fanout", "many_to_many", "neither", "requires bridge allocation, preaggregation, or refusal"),
    ("optional_many_to_one", "many_to_zero_or_one", "left", "preserves left rows but introduces typed absence for unmatched right values"),
    ("inner_loss", "any", "conditional", "may remove unmatched occurrences and changes population"),
    ("outer_padding", "any", "conditional", "introduces padded absence distinct from source null"),
    ("temporal_asof_join", "many_to_one_at_cut", "left", "requires exactly one valid right version at the selected cut"),
    ("interval_overlap_join", "many_to_many_temporal", "neither", "fanout depends on interval overlap multiplicity"),
    ("slowly_changing_dimension_join", "many_to_one_per_valid_time", "left", "requires non-overlapping member validity or precedence"),
    ("bridge_equal_allocation", "many_to_many", "allocated", "allocates each source amount with weights summing to one"),
    ("bridge_distinct_membership", "many_to_many", "set_semantics", "safe only for distinct entity counts under exact keys"),
    ("preaggregate_then_join", "mixed", "proven", "reduces each fact to common conformed grain before joining"),
    ("aggregate_after_join", "mixed", "conditional", "safe only when join multiplicity preserves aggregate contribution"),
    ("symmetric_deduplication", "fanout", "measure_keyed", "deduplicates measure contributions by stable fact key"),
    ("join_path_ambiguity", "graph", "none", "two valid paths with different semantics require caller selection"),
    ("cycle_path", "graph_cycle", "none", "cyclic traversal requires bounded path and duplicate semantics"),
    ("role_playing_dimension", "many_to_one", "fact", "same dimension owner appears under distinct semantic roles"),
    ("conformed_dimension", "fact_to_shared_dimension", "facts", "permits cross-fact comparison only at compatible levels and versions"),
    ("degenerate_dimension", "same_fact", "fact", "dimension value is carried at fact grain without a separate entity relation"),
    ("unknown_cardinality", "unknown", "none", "compilation refuses aggregate-bearing joins without bounded multiplicity"),
    ("data_dependent_cardinality", "conditional", "proof_scoped", "requires validated constraints at the exact data cut"),
]
for local, cardinality, safe_side, meaning in JOIN_ROWS:
    SEMANTIC_RECORDS.append({
        "record_id": f"join_law.{PREFIX}.{local}", "record_kind": "join_law", "edition": EDITION,
        "status": "candidate", "name": local.replace("_", " ").title(), "owner_context_ref": cid("fanout_safety"),
        "meaning": meaning, "signature": {"cardinality": cardinality, "grain_preserved": safe_side, "requires": ["join_predicate", "endpoint_grains", "key_evidence"]},
        "effects": ["semantic_data_read"], "partiality": "refuse_when_proof_missing",
        "laws": ["Entity relation does not by itself authorize an analytical join.", "A fanout-safe rewrite preserves contribution multiplicity for every selected measure."],
        "refusal_conditions": ["unknown_cardinality", "ambiguous_path", "unproven_contribution_multiplicity"],
        "evidence_refs": [sid("paper.agg_consistency"), sid("looker.symmetric")],
    })


TIME_ROWS = [
    ("event_time", "time when the represented occurrence happened"),
    ("valid_time", "interval when an assertion is true in the modeled domain"),
    ("recording_time", "interval when a system retained a version as current"),
    ("query_time", "instant at which a semantic request is evaluated"),
    ("observation_phenomenon_time", "time at which an observed property applied"),
    ("observation_result_time", "time when the observation result became available"),
    ("ingestion_time", "time when a source occurrence entered a receiving system"),
    ("publication_time", "time when a semantic definition or result became available"),
    ("as_of_valid", "selection by domain valid time"),
    ("as_of_recorded", "selection by system recording time"),
    ("bitemporal_cut", "pair of independently selected valid-time and recording-time coordinates"),
    ("closed_open_interval", "interval including start and excluding end"),
    ("calendar_day", "day in a named calendar and zone"),
    ("iso_week", "ISO week-based year and week"),
    ("fiscal_period", "governed organization period not inferred from Gregorian month"),
    ("business_day", "calendar date admitted by an editioned business calendar"),
    ("fixed_duration_window", "window measured on a time scale by elapsed duration"),
    ("calendar_window", "window advanced by calendar-relative periods"),
    ("tumbling_bucket", "non-overlapping exhaustive buckets under an origin and zone"),
    ("sliding_window", "overlapping windows with declared width and step"),
    ("session_window", "data-dependent window separated by an inactivity gap"),
    ("period_to_date", "interval from governed period start through cut"),
    ("prior_comparable_period", "previous period selected by a declared comparability policy"),
    ("late_arrival_horizon", "bounded interval during which revisions remain expected"),
    ("watermark", "claim that events up to a boundary satisfy a declared completeness posture"),
    ("timezone_database_edition", "edition of civil-time transition rules used in interpretation"),
]
for local, meaning in TIME_ROWS:
    SEMANTIC_RECORDS.append({
        "record_id": f"time.{PREFIX}.{local}", "record_kind": "time_semantic", "edition": EDITION,
        "status": "candidate", "name": local.replace("_", " ").title(), "owner_context_ref": cid("bitemporal_interpretation" if "valid" in local or "record" in local or "bitemporal" in local else "calendar_time"),
        "meaning": meaning, "signature": {"requires": ["temporal_role", "reference_system", "precision", "edition"]},
        "effects": [], "partiality": "partial_when_reference_system_or_boundary_missing",
        "laws": ["Event, valid, recording and query time are independent roles.", "Calendar bucketing includes calendar and time-zone edition in identity."],
        "refusal_conditions": ["ambiguous_temporal_role", "missing_zone", "missing_boundary_policy"],
        "evidence_refs": [sid("w3c.owl_time"), sid("iso.8601")],
    })


OPERATION_GROUPS = {
    "analytical_entity": ["declare_entity_role", "bind_semantic_key", "resolve_entity_role", "retire_entity_role"],
    "grain_population": ["declare_grain", "prove_uniqueness", "refine_population", "compare_grains", "project_grain"],
    "measure_definition": ["declare_measure", "bind_quantity_kind", "set_aggregation_posture", "deprecate_measure"],
    "dimension_definition": ["declare_dimension", "bind_member_domain", "declare_hierarchy", "validate_rollup"],
    "join_path": ["declare_relationship", "enumerate_join_paths", "select_join_path", "prove_cardinality", "reject_fanout"],
    "formula_ast": ["parse_formula", "normalize_ast", "alpha_rename", "serialize_canonical_ast"],
    "semantic_type_system": ["infer_type", "check_dimension", "resolve_coercion", "check_effects", "check_totality"],
    "formula_definition": ["register_formula", "publish_formula", "deprecate_formula", "recall_formula", "diff_formula_editions"],
    "formula_binding": ["resolve_variable", "bind_measure", "bind_metric", "bind_function_edition", "seal_binding"],
    "formula_evaluation": ["plan_evaluation", "evaluate_formula", "capture_evaluation_receipt", "cancel_evaluation"],
    "partiality_missingness": ["classify_absence", "propagate_partial_value", "coalesce_selected_reason", "separate_zero_from_absence"],
    "unit_quantity": ["check_unit_compatibility", "convert_quantity", "compose_dimension_vector", "canonicalize_unit"],
    "currency_valuation": ["select_rate_source", "bind_valuation_time", "invert_exchange_rate", "triangulate_rate", "value_money"],
    "aggregation_algebra": ["aggregate_population", "derive_partial_state", "merge_partial_states", "finalize_aggregate", "validate_empty_input"],
    "reaggregation": ["test_reaggregability", "rollup_state", "recompute_from_detail", "reject_invalid_rollup"],
    "population_cohort": ["define_population", "derive_cohort_entry", "derive_cohort_exit", "freeze_population_cut"],
    "filter_predicate": ["typecheck_predicate", "scope_filter", "compose_filters", "normalize_predicate"],
    "metric_definition": ["draft_metric", "validate_metric_coordinates", "publish_metric", "derive_metric", "diff_metric_editions"],
    "kpi_target": ["designate_kpi", "bind_target", "evaluate_threshold", "compare_benchmark"],
    "calendar_time": ["bucket_time", "align_periods", "evaluate_period_to_date", "select_prior_period"],
    "bitemporal_interpretation": ["select_valid_time", "select_recording_time", "evaluate_bitemporal_cut", "apply_correction"],
    "uncertainty": ["attach_uncertainty", "propagate_covariance", "simulate_propagation", "disclose_dependence_assumption"],
    "semantic_model": ["compose_semantic_model", "validate_model_references", "publish_model", "diff_model_editions"],
    "semantic_query": ["declare_semantic_query", "bind_query_members", "normalize_semantic_query", "fingerprint_query"],
    "query_validation": ["prove_grain_safety", "prove_join_safety", "check_purpose_access", "issue_query_refusal"],
    "semantic_lowering": ["emit_provider_requirements", "match_provider_offer", "lower_semantic_query", "prove_preservation"],
    "materialization": ["declare_materialization", "match_rollup", "refresh_materialization", "invalidate_materialization"],
    "semantic_cache": ["compute_semantic_fingerprint", "prove_cache_equivalence", "prove_cache_containment", "reject_stale_cache"],
    "observation_receipt": ["record_metric_observation", "supersede_observation", "recall_observation", "verify_receipt"],
    "disclosure": ["build_disclosure", "project_authorized_disclosure", "explain_metric", "emit_limitation_notice"],
    "compatibility_migration": ["classify_compatibility", "plan_migration", "verify_consumer_obligation", "close_deprecation_window"],
}
for context_local, operations in OPERATION_GROUPS.items():
    for local in operations:
        SEMANTIC_RECORDS.append({
            "record_id": f"operation.{PREFIX}.{local}", "record_kind": "operation", "edition": EDITION,
            "status": "candidate", "name": local.replace("_", " ").title(), "owner_context_ref": cid(context_local),
            "meaning": f"Perform {local.replace('_', ' ')} under the {context_local.replace('_', ' ')} contract.",
            "signature": {"inputs": ["typed_request", "semantic_editions", "authority_context"], "output": "typed_result_or_refusal"},
            "effects": [] if context_local in {"formula_ast", "semantic_type_system", "aggregation_algebra", "reaggregation", "filter_predicate"} else ["registry_or_data_effect"],
            "partiality": "total_result_sum_type_success_or_refusal",
            "laws": ["Success returns an edition-pinned result.", "Failure returns a typed refusal without guessed defaults."],
            "refusal_conditions": ["unknown_semantics", "missing_authority", "failed_proof_obligation"],
            "evidence_refs": context_evidence(context_local)[:2],
        })


DECISION_ROWS = [
    ("fact_or_observation", "fact_role", "Is the input an asserted business fact role or an observation with procedure and result?"),
    ("event_or_snapshot", "event_semantics", "Does the occurrence denote a transition or state at a cut?"),
    ("measure_or_metric", "metric_definition", "Is the object a recorded value field or a governed calculation over a population?"),
    ("metric_or_kpi", "kpi_target", "Has authority designated the metric key for an explicit purpose?"),
    ("definition_or_observation", "observation_receipt", "Is the object a reusable definition or an evaluated value at a cut?"),
    ("business_term_or_member", "member_code_list", "Does the object own domain meaning or participate as a member of one analytical dimension?"),
    ("formula_definition_or_expression", "formula_definition", "Does identity and lifecycle attach, or is this only an AST value?"),
    ("formula_binding_or_evaluation", "formula_binding", "Are references being resolved or values being computed?"),
    ("variable_or_parameter", "variable_parameter", "Is input lexically bound by the formula or supplied by the caller contract?"),
    ("pure_or_effectful_function", "function_registry", "Does evaluation depend on data, time, randomness, registry or I/O?"),
    ("total_or_partial", "partiality_missingness", "Can every well-typed input produce a value without absence or error?"),
    ("null_absent_zero", "partiality_missingness", "Which disjoint constructor actually applies?"),
    ("implicit_or_explicit_coercion", "semantic_type_system", "Is the coercion admitted by a declared loss and compatibility rule?"),
    ("unit_conversion_or_valuation", "currency_valuation", "Is this scale conversion within a quantity kind or market/policy valuation between currencies?"),
    ("ratio_or_percentage", "ratio_rate_index", "Is scale one or one hundred, and are numerator and denominator semantics preserved?"),
    ("rate_or_ratio", "ratio_rate_index", "Does denominator denote time, exposure or population extent?"),
    ("target_or_observation", "kpi_target", "Is the value desired/thresholded or actually measured?"),
    ("target_or_benchmark", "benchmark_reference", "Is the comparator normative aspiration or observed reference-population value?"),
    ("additive_or_semi_additive", "additivity_posture", "Across which exact dimensions and levels may summation occur?"),
    ("additivity_or_decomposability", "decomposable_state", "May values sum meaningfully, or may sufficient states merely merge?"),
    ("result_or_sufficient_state", "decomposable_state", "Can the displayed result alone be reaggregated?"),
    ("reaggregate_or_recompute", "reaggregation", "Does the retained state prove equivalence at the requested coarser grain?"),
    ("empty_population_policy", "aggregation_algebra", "Does empty input yield identity, absence or error?"),
    ("null_input_policy", "aggregation_algebra", "Are nulls excluded, propagated, counted or refused?"),
    ("ordered_or_unordered_aggregate", "aggregation_algebra", "Does result depend on input order or tie-breaking?"),
    ("exact_or_approximate", "aggregation_algebra", "What error guarantee and authorization apply?"),
    ("entity_relation_or_join", "semantic_relationship", "Does the domain relation authorize a specific analytical join at this grain?"),
    ("cardinality_known_or_assumed", "fanout_safety", "Is multiplicity proven from semantic constraints at the cut?"),
    ("fanout_rewrite_or_refusal", "fanout_safety", "Is there a contribution-preserving rewrite for every selected measure?"),
    ("ambiguous_join_path", "join_path", "Do multiple paths encode materially different roles or populations?"),
    ("cohort_or_filter", "population_cohort", "Does the definition include entry, exit and temporal anchoring beyond a predicate?"),
    ("filter_or_access_policy", "access_purpose", "Does the predicate define metric scope or enforce authorization?"),
    ("event_valid_record_query_time", "bitemporal_interpretation", "Which independent temporal role is intended?"),
    ("duration_or_calendar_period", "calendar_time", "Is arithmetic elapsed-time or calendar-relative?"),
    ("calendar_or_fiscal", "fiscal_period", "Is grouping governed by civil calendar or organization fiscal edition?"),
    ("as_of_or_latest", "asof_cut", "Is a cut explicit or is an unstable latest selection being requested?"),
    ("fresh_or_final", "validity_finality", "Is the value recently produced or no longer expected to revise?"),
    ("correction_or_redefinition", "lifecycle_version", "Did source truth change or did metric meaning change?"),
    ("compatible_or_breaking", "compatibility_migration", "Can every prior valid request retain meaning and result contract?"),
    ("semantic_query_or_sql", "semantic_query", "Does the request name governed semantics or a physical query language text?"),
    ("governed_metric_or_tile", "metric_governance", "Is identity owned independently of one presentation artifact?"),
    ("cache_equivalent_or_text_match", "semantic_cache", "Are normalized semantics, editions, cut and guarantees equivalent?"),
    ("cache_hit_or_materialization_rewrite", "materialization", "Is an exact prior result reused or is a covering aggregate rewritten?"),
    ("uncertainty_or_quality", "uncertainty", "Does metadata quantify dispersion/dependence or assess process fitness?"),
    ("publish_or_approve", "metric_governance", "Has authority only approved content or made it available for use?"),
    ("deprecate_or_recall", "lifecycle_version", "May existing consumers continue temporarily or must use cease?"),
    ("access_or_metric_authority", "access_purpose", "May an actor see/evaluate data, or may the actor define authoritative meaning?"),
    ("semantic_equivalence_or_numeric_closeness", "semantic_lowering", "Are results definitionally equal or only within a tolerance?"),
]
for local, owner, question in DECISION_ROWS:
    SEMANTIC_RECORDS.append({
        "record_id": f"decision.{PREFIX}.{local}", "record_kind": "decision_point", "edition": EDITION,
        "status": "candidate", "name": local.replace("_", " ").title(), "owner_context_ref": cid(owner),
        "meaning": question, "signature": {"decision_inputs": ["owned_semantics", "editions", "evidence"], "outcomes": ["admit", "transform_with_proof", "refuse"]},
        "effects": [], "partiality": "refuse_if_evidence_insufficient",
        "laws": ["Decision outcome and evidence are retained in a receipt.", "A name match is never sufficient evidence."],
        "refusal_conditions": ["missing_decision_coordinate", "conflicting_authority", "unproven_assumption"],
        "evidence_refs": context_evidence(owner)[:2],
    })


TERM_ROWS = [
    ("business_term", "An owned domain-language concept independent of any analytical projection.", "dimension_definition", ["dimension_member", "display_label"]),
    ("analytical_entity", "A role played by a domain concept in a semantic model.", "analytical_entity", ["business_entity", "table"]),
    ("fact", "An assertion admitted at an analytical grain; not proof that an event occurred.", "fact_role", ["event", "observation"]),
    ("event", "An identified occurrence or transition with event-time semantics.", "event_semantics", ["fact_row", "snapshot"]),
    ("observation", "An act or assertion relating feature, observable property, procedure, result and time.", "observation_assertion", ["fact", "metric_observation"]),
    ("grain", "The semantic roles whose joint values identify one fact or observation occurrence.", "grain_population", ["primary_key", "group_by"]),
    ("population", "The eligible universe under entry, exit and temporal rules.", "population_cohort", ["sample", "filter"]),
    ("cohort", "A population anchored by entry, exit and follow-up time semantics.", "population_cohort", ["filter", "segment"]),
    ("measure", "A recorded or derived value contract with type, unit and aggregation posture.", "measure_definition", ["metric", "measurement"]),
    ("measurement", "The process and result of obtaining a quantity value.", "observation_assertion", ["measure", "metric"]),
    ("metric", "A governed calculation over explicit population, grain, filters, aggregation, dimensions and time.", "metric_definition", ["measure", "kpi", "observation"]),
    ("kpi", "A metric designated key by an authority for an explicit purpose and interval.", "kpi_target", ["metric", "target"]),
    ("metric_observation", "An evaluated metric value pinned to semantic editions, inputs and data cut.", "observation_receipt", ["metric_definition", "dashboard_value"]),
    ("dimension", "A governed analytical attribute along which results may be selected or grouped.", "dimension_definition", ["axis", "member"]),
    ("dimension_member", "A governed value in one dimension and code-list edition.", "member_code_list", ["business_term", "label"]),
    ("hierarchy", "An editioned set of levels and roll-up relations.", "hierarchy_rollup", ["taxonomy", "sort_order"]),
    ("level", "A governed position in a hierarchy with roll-up laws.", "hierarchy_rollup", ["grain", "rank"]),
    ("relationship", "A semantic association between analytical roles.", "semantic_relationship", ["join", "foreign_key"]),
    ("join", "An analytical combination under a predicate, cardinality, grain and temporal policy.", "join_path", ["relationship", "join_algorithm"]),
    ("join_path", "An ordered sequence of analytical relationships selected for one semantic role.", "join_path", ["graph_path", "physical_plan"]),
    ("cardinality", "A constraint on match multiplicity at a declared scope and time.", "fanout_safety", ["row_count", "selectivity"]),
    ("fanout", "Duplication of an endpoint contribution caused by join multiplicity.", "fanout_safety", ["large_result", "many_to_many_relation"]),
    ("formula_expression", "A typed AST value without registry identity or lifecycle.", "formula_ast", ["formula_definition", "sql_expression"]),
    ("formula_definition", "An immutable named and editioned formula expression plus contract.", "formula_definition", ["formula_expression", "metric"]),
    ("formula_binding", "Exact resolution of free references to semantic owners and editions.", "formula_binding", ["column_mapping", "evaluation"]),
    ("formula_evaluation", "Computation of a bound formula for explicit inputs and cut.", "formula_evaluation", ["binding", "definition"]),
    ("variable", "A lexically scoped symbolic input in an expression.", "variable_parameter", ["parameter", "dimension"]),
    ("parameter", "A typed caller-supplied input governed by constraints and default policy.", "variable_parameter", ["variable", "filter"]),
    ("function", "A versioned signature, meaning, effects and partiality contract.", "function_registry", ["formula", "provider_udf"]),
    ("operator", "A pure algebraic form with declared signature, precedence and laws.", "operator_registry", ["function", "physical_kernel"]),
    ("semantic_type", "A value identity determined by meaning and laws, not carrier representation.", "semantic_type_system", ["sql_type", "display_format"]),
    ("effect", "An observable dependency or action beyond pure value calculation.", "semantic_type_system", ["error", "cost"]),
    ("partiality", "The posture that some admitted inputs produce absence or error instead of a value.", "partiality_missingness", ["nullability", "failure_rate"]),
    ("null", "A carrier-level or logic-level marker whose semantic absence reason remains unresolved.", "partiality_missingness", ["absent", "zero"]),
    ("absent", "A semantic sum-type constructor with a governed reason.", "partiality_missingness", ["null", "empty"]),
    ("unknown", "An absence or truth state indicating the value is not known.", "partiality_missingness", ["suppressed", "not_applicable"]),
    ("suppressed", "A value intentionally withheld under a disclosure rule.", "partiality_missingness", ["unknown", "missing"]),
    ("not_applicable", "A value that has no meaning for the subject or population.", "partiality_missingness", ["zero", "missing"]),
    ("zero", "A present additive identity or numeric value, never an absence marker.", "partiality_missingness", ["null", "empty_population"]),
    ("empty_population", "A population with no eligible occurrences at the cut.", "aggregation_algebra", ["zero", "all_missing"]),
    ("unit", "A scale for a quantity kind and dimension vector.", "unit_quantity", ["currency", "format"]),
    ("quantity", "A magnitude interpreted under quantity kind and unit.", "unit_quantity", ["number", "money"]),
    ("unit_conversion", "A scale/offset transformation between compatible units.", "unit_quantity", ["currency_valuation", "normalization"]),
    ("money", "An amount paired with currency and minor-unit policy.", "currency_valuation", ["quantity", "price"]),
    ("currency_valuation", "A directed conversion using an identified rate source, side and valuation time.", "currency_valuation", ["unit_conversion", "redenomination"]),
    ("ratio", "A quotient retaining numerator, denominator and scale meanings.", "ratio_rate_index", ["percentage", "rate"]),
    ("rate", "A quotient whose denominator denotes time, exposure or population extent.", "ratio_rate_index", ["ratio", "exchange_rate"]),
    ("percentage", "A ratio presented at scale one hundred.", "ratio_rate_index", ["percentage_point", "fraction"]),
    ("index", "A relative value tied to an identified base and method.", "ratio_rate_index", ["ratio", "rank"]),
    ("aggregation", "A governed fold over eligible values with missing, order and empty-input laws.", "aggregation_algebra", ["grouping", "estimator"]),
    ("reaggregation", "Combination of retained aggregate state or results at a coarser grain.", "reaggregation", ["recompute", "rollup"]),
    ("additive", "Summable across every declared dimension and admitted level.", "additivity_posture", ["decomposable", "linear"]),
    ("semi_additive", "Summable only across an explicit subset of dimensions or levels.", "additivity_posture", ["non_additive", "decomposable"]),
    ("non_additive", "Not meaningfully summable across the specified coordinate.", "additivity_posture", ["holistic", "ratio"]),
    ("decomposable", "Computable from mergeable sufficient states over partitions.", "decomposable_state", ["additive", "reaggregable"]),
    ("summarizability", "Correct derivability of coarser results from finer multidimensional data under structural and measure laws.", "additivity_posture", ["aggregation", "compression"]),
    ("filter", "A typed predicate restricting metric or query scope.", "filter_predicate", ["cohort", "access_policy"]),
    ("segment", "A reusable named predicate or population refinement, depending on declared owner.", "filter_predicate", ["cohort", "dimension_member"]),
    ("target", "A desired, required or threshold value for a governed metric and interval.", "kpi_target", ["observed_value", "benchmark"]),
    ("benchmark", "A comparison value derived from an identified reference population and method.", "benchmark_reference", ["target", "baseline"]),
    ("baseline", "A selected reference observation, period or scenario.", "benchmark_reference", ["benchmark", "target"]),
    ("calendar", "A system for organizing dates and periods, identified by edition.", "calendar_time", ["timezone", "fiscal_period"]),
    ("time_zone", "Rules mapping civil-time labels to instants, pinned to a database edition.", "calendar_time", ["offset", "calendar"]),
    ("fiscal_period", "An organization-governed reporting period.", "fiscal_period", ["calendar_month", "close_date"]),
    ("event_time", "When the represented event happened.", "event_semantics", ["valid_time", "recording_time"]),
    ("valid_time", "When an assertion applies in the modeled domain.", "bitemporal_interpretation", ["event_time", "recording_time"]),
    ("recording_time", "When a system version is current in recorded history.", "bitemporal_interpretation", ["valid_time", "ingestion_time"]),
    ("query_time", "When a semantic request is evaluated.", "bitemporal_interpretation", ["as_of", "event_time"]),
    ("as_of", "An explicit temporal visibility coordinate, not a synonym for latest.", "asof_cut", ["latest", "query_time"]),
    ("data_cut", "The exact source editions, visibility times and completeness boundaries used.", "asof_cut", ["snapshot", "cache_key"]),
    ("freshness", "Age or update recency relative to a declared policy.", "validity_finality", ["finality", "validity"]),
    ("finality", "Posture describing whether further ordinary revisions are expected.", "validity_finality", ["freshness", "truth"]),
    ("uncertainty", "Quantified doubt represented with method and dependence assumptions.", "uncertainty", ["missingness", "data_quality"]),
    ("semantic_model", "A versioned composition of owned semantic contracts.", "semantic_model", ["ontology", "physical_schema"]),
    ("semantic_query", "A governed analytical request expressed in semantic members and coordinates.", "semantic_query", ["sql", "dashboard"]),
    ("semantic_lowering", "Meaning-preserving translation from semantic request to logical provider requirements.", "semantic_lowering", ["query_optimization", "sql_generation"]),
    ("materialization", "Persisted aggregate state or observation over a declared semantic coverage region.", "materialization", ["cache", "source_fact"]),
    ("semantic_cache_equivalence", "Proof that normalized meaning, editions, cut and guarantees allow reuse.", "semantic_cache", ["sql_text_match", "cache_freshness"]),
    ("governed_metric", "A published metric edition under explicit authority and purpose policy.", "metric_governance", ["dashboard_tile", "calculated_field"]),
    ("dashboard_tile", "A presentation artifact that may reference a metric but never owns its meaning.", "disclosure", ["metric", "metric_observation"]),
    ("disclosure", "Consumer-facing statement of definition, cut, unit, uncertainty, finality and limitations.", "disclosure", ["visualization", "provenance"]),
    ("purpose", "A governed intended-use concept used in authorization and publication policy.", "access_purpose", ["user_intent", "metric_name"]),
    ("edition", "An immutable positive version of a semantic identity.", "lifecycle_version", ["revision_time", "display_version"]),
    ("deprecation", "Lifecycle posture permitting bounded migration before withdrawal.", "lifecycle_version", ["recall", "deletion"]),
    ("recall", "Lifecycle posture prohibiting new use while preserving historical interpretation.", "lifecycle_version", ["deprecation", "correction"]),
    ("compatibility", "A directional relation stating which prior contracts retain meaning under a new edition.", "compatibility_migration", ["equality", "provider_support"]),
]


TERMS = [
    {
        "term_id": f"term.{PREFIX}.{term}", "edition": EDITION, "status": "candidate",
        "canonical_term": term.replace("_", " "), "definition": definition,
        "owner_context_ref": cid(owner), "distinguish_from": distinctions,
        "homonym_policy": "Use only with the owning context qualifier when another context uses the same surface word.",
        "evidence_refs": context_evidence(owner)[:2],
    }
    for term, definition, owner, distinctions in TERM_ROWS
]


LAW_ROWS = [
    ("formula_alpha_equivalence", "algebra_law", "Renaming bound variables without capture preserves formula meaning."),
    ("formula_substitution", "algebra_law", "Capture-avoiding substitution of an equal typed value preserves evaluation result and effects."),
    ("formula_purity", "invariant", "Pure formula evaluation has no ambient clock, data access, I/O, randomness or mutable registry lookup."),
    ("formula_cycles", "refusal", "Dependency cycles are refused unless a declared fixed-point domain, monotonicity law, convergence test and budget exist."),
    ("formula_binding_total", "proof_obligation", "Every free reference resolves exactly once to an owner and edition with compatible type, unit, grain and time."),
    ("function_effect_subtyping", "proof_obligation", "A caller effect allowance must cover every transitive function effect."),
    ("partiality_exhaustive", "invariant", "Every partial operation declares domain, absence/error constructors and propagation law."),
    ("no_implicit_zero", "refusal", "Null, absent, unknown, suppressed, not-applicable and empty input may not be coerced to zero without an explicit policy."),
    ("quantity_addition", "algebra_law", "Addition and subtraction require compatible quantity kind and proven unit conversion."),
    ("quantity_multiplication", "algebra_law", "Multiplication and division compose dimension vectors and units."),
    ("currency_no_ambient_rate", "refusal", "Currency valuation without rate source, direction, rate edition and valuation time is refused."),
    ("currency_triangulation", "proof_obligation", "Triangulated valuation identifies every leg, side, rounding step and arbitrage tolerance."),
    ("ratio_denominator", "invariant", "A ratio retains denominator meaning and explicit zero-denominator posture."),
    ("sum_associativity_scope", "proof_obligation", "Parallel sum requires a numeric posture whose reassociation guarantee satisfies the requested reproducibility."),
    ("aggregate_empty_input", "invariant", "Every aggregate declares identity, absence or error for empty eligible input."),
    ("aggregate_missing_policy", "invariant", "Every aggregate declares treatment of each absence reason and carrier null."),
    ("aggregate_order", "proof_obligation", "Order-sensitive aggregates require total ordering, collation, null order and tie policy."),
    ("decomposable_merge_identity", "algebra_law", "Merge(identity, state) equals state for a declared decomposable aggregate."),
    ("decomposable_merge_associative", "algebra_law", "Merge grouping does not change finalized semantics under the declared guarantee posture."),
    ("reaggregation_state_not_result", "refusal", "A displayed non-sufficient result may not be reaggregated merely because its carrier is numeric."),
    ("semi_additive_dimensions", "invariant", "A semi-additive measure enumerates admitted dimensions and hierarchy levels."),
    ("summarizability_hierarchy", "proof_obligation", "Roll-up requires compatible completeness, disjointness/weighting and level mappings at valid time."),
    ("grain_exact", "invariant", "Every fact occurrence, measure and metric declares one semantic grain."),
    ("grain_change_breaking", "invariant", "A grain change is semantic and cannot be released as a metadata-only edit."),
    ("join_cardinality_declared", "invariant", "Every analytical join path declares endpoint cardinality and grain effect."),
    ("join_path_ambiguity", "refusal", "Equally admissible paths with different semantic roles are not silently chosen."),
    ("fanout_contribution", "proof_obligation", "For every selected measure, a join rewrite preserves each source occurrence contribution multiplicity."),
    ("fanout_unknown", "refusal", "Aggregate-bearing queries refuse joins whose cardinality is assumed rather than proven or bounded."),
    ("preaggregate_join", "proof_obligation", "Preaggregated facts may join only at a compatible conformed grain and semantic edition."),
    ("bridge_weights", "algebra_law", "Allocation weights for each source occurrence sum to one under the declared tolerance and cut."),
    ("metric_coordinates_complete", "invariant", "A metric declares population, grain, measure/formula, filter, aggregation, dimensions, time, unit and missingness."),
    ("metric_definition_not_value", "invariant", "A metric definition never contains an observed value as its identity."),
    ("kpi_designation", "invariant", "KPI status is a purpose-bound authority designation over a metric edition."),
    ("target_separate", "invariant", "A target is versioned separately from the observed metric value."),
    ("benchmark_population", "proof_obligation", "A benchmark identifies reference population, method, period, source and uncertainty."),
    ("cohort_time_zero", "invariant", "A cohort declares index event, eligibility lookback, entry, exit and follow-up semantics."),
    ("filter_scope", "invariant", "A filter identifies whether it applies before aggregation, after aggregation, to population, or to query presentation."),
    ("event_valid_record_query_distinct", "invariant", "Event, valid, recording and query time remain separate coordinates."),
    ("bitemporal_cut_complete", "proof_obligation", "Bitemporal evaluation pins both valid-time and recording-time selection policies."),
    ("calendar_edition", "invariant", "Calendar and time-zone database editions participate in bucket identity."),
    ("period_duration_distinct", "refusal", "A calendar period is not substituted for an elapsed duration without an anchor and calendar policy."),
    ("fiscal_not_inferred", "refusal", "Fiscal periods are never inferred from Gregorian labels or source column names."),
    ("asof_not_latest", "invariant", "As-of is an explicit cut; latest is an unstable selection policy."),
    ("watermark_scope", "invariant", "A watermark states scope, time role, lateness policy and completeness claim."),
    ("freshness_not_finality", "invariant", "Recent production does not imply revision finality."),
    ("correction_preserves_history", "invariant", "Corrections append or supersede; they do not overwrite historical observations."),
    ("uncertainty_dependence", "proof_obligation", "Propagation declares covariance, independence, bounds or simulation assumptions."),
    ("uncertainty_nonlinearity", "proof_obligation", "Linear propagation outside its qualified regime requires nonlinear or simulation evidence."),
    ("metric_publication_authority", "invariant", "Formula registry authority does not grant metric publication authority or data access."),
    ("publication_immutable", "invariant", "Published semantic editions are immutable."),
    ("recall_no_erasure", "invariant", "Recall prevents new use but preserves historical interpretation and receipts."),
    ("semantic_query_pins_model", "invariant", "Every semantic query identifies one published model edition or a deterministic compatibility range."),
    ("semantic_lowering_preservation", "proof_obligation", "Successful lowering carries source mapping and semantic-preservation evidence."),
    ("lossy_lowering", "refusal", "Unsupported semantics cannot be approximated or dropped without declared authorization and receipt."),
    ("semantic_cache_identity", "invariant", "Cache identity includes normalized semantics, owner editions, cut, access projection and guarantee posture."),
    ("sql_text_not_cache_identity", "refusal", "Matching SQL text or display name is insufficient for semantic cache reuse."),
    ("cache_containment", "proof_obligation", "Reuse from a covering materialization proves predicate, grouping, time, unit, missingness and aggregate-state containment."),
    ("cache_access_non_escalation", "invariant", "Cache reuse never broadens the requester's authorized population or disclosure scope."),
    ("materialization_invalidation", "invariant", "Invalidation responds separately to data revision, semantic edition, policy, calendar/rate edition and provider guarantee changes."),
    ("observation_pins_everything", "invariant", "A metric observation pins metric, formula, binding, model, policy, cut, provider and receipt editions."),
    ("observation_not_business_fact", "refusal", "An evaluated metric observation is not silently admitted as a domain-owned fact."),
    ("disclosure_minimum", "invariant", "Disclosure includes definition edition, population/grain, unit, period/cut, finality, missingness, uncertainty and limitations."),
    ("suppression_nonleakage", "proof_obligation", "Disclosure and cache reuse cannot reconstruct suppressed values through subtraction or differencing."),
    ("purpose_bound_access", "invariant", "Evaluation and disclosure authorization include actor, purpose, population, fields, interval and obligations."),
    ("metric_governance_not_access", "invariant", "Authority to define a metric is distinct from entitlement to underlying data."),
    ("compatibility_directional", "algebra_law", "Compatibility is directional and scoped to consumer operations and guarantees."),
    ("deprecation_window", "invariant", "Deprecation retains stated consumer obligations until migration, expiry or recall."),
    ("unknown_owner", "refusal", "Unknown semantic owner or edition fails closed."),
    ("provider_name_nonsemantic", "refusal", "Provider, column, table or dashboard names never determine semantic dispatch."),
]


LAWS = [
    {
        "law_id": f"law.{PREFIX}.{local}", "edition": EDITION, "status": "candidate", "law_kind": kind,
        "statement": statement, "scope": "semantic_metrics_formulas",
        "proof_inputs": ["semantic_owners", "editions", "typed_contracts", "evidence_refs"],
        "failure_posture": "typed_refusal_and_no_silent_fallback",
        "evidence_refs": [sid("oasis.openformula14"), sid("paper.agg_consistency") if "join" in local or "fanout" in local else sid("sdmx.31")],
    }
    for local, kind, statement in LAW_ROWS
]


LIFECYCLE_ROWS = [
    ("formula_definition", "formula_definition", ["draft", "validated", "approved", "published", "deprecated", "recalled", "superseded"]),
    ("metric_definition", "metric_definition", ["proposed", "specified", "validated", "approved", "published", "deprecated", "recalled", "superseded"]),
    ("semantic_model", "semantic_model", ["draft", "composed", "validated", "published", "deprecated", "withdrawn"]),
    ("dimension_member", "member_code_list", ["proposed", "active", "deprecated", "retired", "mapped"]),
    ("function_edition", "function_registry", ["draft", "qualified", "published", "deprecated", "recalled"]),
    ("calendar_edition", "calendar_time", ["draft", "validated", "effective", "expired", "corrected"]),
    ("exchange_rate_set", "currency_valuation", ["observed", "validated", "published", "corrected", "superseded"]),
    ("materialization", "materialization", ["declared", "building", "ready", "stale", "invalid", "rebuilding", "retired"]),
    ("metric_observation", "observation_receipt", ["requested", "evaluating", "provisional", "final", "corrected", "superseded", "recalled"]),
    ("semantic_publication", "model_publication", ["planned", "validated", "published", "deprecated", "withdrawn"]),
    ("consumer_migration", "compatibility_migration", ["identified", "planned", "dual_run", "verified", "cut_over", "closed"]),
    ("benchmark", "benchmark_reference", ["proposed", "qualified", "published", "revised", "retired"]),
]
LIFECYCLES = [
    {
        "lifecycle_id": f"lifecycle.{PREFIX}.{local}", "edition": EDITION, "status": "candidate",
        "artifact_kind": local, "owner_context_ref": cid(owner), "states": states,
        "transition_contract": {"requires": ["authority", "from_state", "to_state", "reason", "effective_time", "evidence"], "append_only_history": True},
        "forbidden_transitions": ["published_to_draft", "recalled_to_published_without_new_edition", "superseded_to_mutated"],
        "evidence_refs": [sid("w3c.prov_dm"), sid("w3c.dcat3")],
    }
    for local, owner, states in LIFECYCLE_ROWS
]


MAPPING_ROWS = [
    ("bind_formula", "formula_binding", ["typed_ast", "exact_semantic_refs", "function_editions"], ["name_resolution", "type_unit_grain_time_checks"]),
    ("evaluate_formula", "formula_evaluation", ["bound_formula", "input_cut", "effect_budget"], ["qualified_evaluator", "receipt_writer"]),
    ("compile_metric", "metric_definition", ["complete_metric_coordinates", "bound_formula"], ["semantic_query_ir"]),
    ("query_metric", "semantic_query", ["published_model", "selected_metrics", "groupings", "cut"], ["semantic_query_validator"]),
    ("lower_query", "semantic_lowering", ["validated_query", "guarantee_posture"], ["logical_query_offer", "preservation_prover"]),
    ("safe_join", "fanout_safety", ["endpoint_grains", "cardinality", "selected_measures"], ["join_path_offer", "fanout_proof"]),
    ("temporal_join", "join_path", ["valid_time_policy", "non_overlap_or_precedence"], ["temporal_join_offer"]),
    ("roll_up_additive", "reaggregation", ["additivity_posture", "hierarchy_mapping"], ["rollup_offer"]),
    ("merge_aggregate_state", "decomposable_state", ["sufficient_state_schema", "merge_laws"], ["state_merge_offer"]),
    ("reaggregate_ratio", "reaggregation", ["numerator_state", "denominator_state"], ["ratio_of_sums_offer"]),
    ("convert_unit", "unit_quantity", ["quantity_kind", "source_unit", "target_unit"], ["editioned_conversion_offer"]),
    ("value_currency", "currency_valuation", ["source_currency", "target_currency", "valuation_time", "rate_purpose"], ["rate_set_offer"]),
    ("evaluate_cohort", "population_cohort", ["eligibility", "index_event", "entry_exit"], ["population_evaluator_offer"]),
    ("bucket_fiscal_time", "fiscal_period", ["calendar_edition", "zone", "boundary_policy"], ["calendar_service_offer"]),
    ("evaluate_bitemporal", "bitemporal_interpretation", ["valid_cut", "recording_cut"], ["bitemporal_source_offer"]),
    ("propagate_uncertainty", "uncertainty", ["measurement_model", "input_uncertainty", "dependence"], ["qualified_propagator_offer"]),
    ("compare_target", "kpi_target", ["metric_observation", "target_edition", "comparison_direction"], ["typed_comparator_offer"]),
    ("compare_benchmark", "benchmark_reference", ["metric_observation", "reference_population", "method"], ["benchmark_offer"]),
    ("publish_metric", "metric_governance", ["approved_metric", "authority", "purpose"], ["metric_registry_offer"]),
    ("publish_model", "model_publication", ["validated_model", "consumer_contract"], ["publication_registry_offer"]),
    ("materialize_metric", "materialization", ["semantic_coverage", "cut", "refresh_policy"], ["materialization_store_offer"]),
    ("reuse_exact_cache", "semantic_cache", ["semantic_fingerprint", "cut", "access_projection"], ["exact_cache_offer"]),
    ("reuse_covering_rollup", "semantic_cache", ["coverage_containment", "reaggregation_proof"], ["rollup_cache_offer"]),
    ("invalidate_on_revision", "materialization", ["source_revision", "dependency_graph"], ["invalidation_offer"]),
    ("record_observation", "observation_receipt", ["value_or_error", "all_editions", "cut", "receipt"], ["observation_ledger_offer"]),
    ("disclose_metric", "disclosure", ["observation", "consumer_purpose", "disclosure_minimum"], ["disclosure_renderer_offer"]),
    ("enforce_semantic_access", "access_purpose", ["actor", "purpose", "population", "operation"], ["policy_decision_offer"]),
    ("migrate_metric_edition", "compatibility_migration", ["source_edition", "target_edition", "consumers"], ["migration_planner_offer"]),
    ("recall_metric", "metric_governance", ["published_metric", "recall_authority", "reason"], ["registry_and_notification_offer"]),
    ("correct_observation", "observation_receipt", ["prior_observation", "corrected_cut", "reason"], ["append_only_ledger_offer"]),
    ("normalize_query", "semantic_query", ["bound_query", "commutativity_and_scope_laws"], ["canonicalizer_offer"]),
    ("fingerprint_query", "semantic_cache", ["normalized_query", "editions", "guarantees"], ["stable_digest_offer"]),
    ("validate_missingness", "partiality_missingness", ["absence_taxonomy", "operation_policy"], ["partiality_checker_offer"]),
    ("evaluate_window_metric", "calendar_time", ["partition", "order", "frame", "cut"], ["window_semantics_offer"]),
    ("align_cross_fact_metrics", "grain_population", ["metric_grains", "conformed_dimensions"], ["common_grain_offer"]),
    ("prove_suppression_safety", "disclosure", ["released_cells", "suppression_policy"], ["disclosure_safety_offer"]),
]
COMPILER_MAPPINGS = [
    {
        "mapping_id": f"mapping.{PREFIX}.{local}", "edition": EDITION, "status": "candidate",
        "intent_class": local, "owner_context_ref": cid(owner),
        "requirement": {"semantic_requirements": requirements, "must_pin": ["owner", "edition", "cut", "guarantee_posture"], "finite_budgets": True},
        "offer_contract": {"required_capabilities": offers, "must_declare": ["supported_semantics", "limits", "effects", "partiality", "evidence", "fallback"]},
        "match_keys": ["semantic_identity", "types", "units", "grain", "time", "missingness", "effects", "guarantees", "access"],
        "proof_obligations": ["type_and_semantic_compatibility", "no_undeclared_loss", "authority_and_access", "resource_feasibility"],
        "success_receipt": ["selected_offer", "matched_coordinates", "proof_refs", "rejected_alternatives", "cut"],
        "refusal_codes": ["no_compatible_offer", "proof_failed", "unauthorized", "ambiguous_semantics", "unbounded_cost"],
        "evidence_refs": context_evidence(owner)[:2],
    }
    for local, owner, requirements, offers in MAPPING_ROWS
]


LIBRARY_ROWS = [
    ("formula_parser", "pure", "formula_ast", ["parse source to lossless syntax and normalized AST"], ["registry", "clock", "network"]),
    ("ast_canonicalizer", "pure", "formula_ast", ["alpha-normalize and canonicalize expressions"], ["provider", "data_access"]),
    ("semantic_type_checker", "pure", "semantic_type_system", ["infer/check types and coercions"], ["runtime_values", "registry_mutation"]),
    ("dimension_algebra", "pure", "unit_quantity", ["compose and compare quantity dimensions"], ["exchange_rate_lookup"]),
    ("unit_conversion_algebra", "pure", "unit_quantity", ["apply supplied conversion rules"], ["ambient_unit_registry"]),
    ("missingness_algebra", "pure", "partiality_missingness", ["propagate explicit absence and error constructors"], ["implicit_zero_fill"]),
    ("aggregation_algebra", "pure", "aggregation_algebra", ["fold, merge and finalize supplied values/states"], ["source_scan", "storage"]),
    ("summarizability_checker", "pure", "additivity_posture", ["prove roll-up constraints from supplied contracts"], ["database_statistics_lookup"]),
    ("fanout_analyzer", "pure", "fanout_safety", ["prove contribution multiplicity from supplied graph constraints"], ["query_execution"]),
    ("calendar_algebra", "pure", "calendar_time", ["bucket and align using supplied calendar and zone editions"], ["ambient_clock", "timezone_update"]),
    ("bitemporal_algebra", "pure", "bitemporal_interpretation", ["evaluate interval predicates over supplied histories"], ["history_store"]),
    ("uncertainty_algebra", "pure", "uncertainty", ["propagate supplied uncertainty models with explicit seed if sampled"], ["unseeded_randomness"]),
    ("semantic_query_canonicalizer", "pure", "semantic_query", ["normalize and fingerprint bound semantic queries"], ["sql_renderer", "cache_store"]),
    ("cache_equivalence_prover", "pure", "semantic_cache", ["prove exact equivalence or coverage containment"], ["cache_read", "materialization_refresh"]),
    ("compatibility_diff", "pure", "compatibility_migration", ["classify semantic edition differences"], ["registry_mutation"]),
    ("semantic_registry", "effectful", "lifecycle_version", ["persist immutable definitions and lifecycle events"], ["formula_evaluation"]),
    ("binding_resolver", "effectful", "formula_binding", ["resolve names against pinned registry snapshots"], ["silent_latest_binding"]),
    ("formula_runtime", "effectful", "formula_evaluation", ["evaluate bound formulas and emit receipts"], ["meaning_ownership"]),
    ("exchange_rate_gateway", "effectful", "currency_valuation", ["fetch and attest rate sets by purpose and time"], ["unit_conversion_rules"]),
    ("semantic_query_gateway", "effectful", "semantic_lowering", ["bind provider offers and execute lowered requests"], ["metric_definition_authority"]),
    ("materialization_store", "effectful", "materialization", ["build, refresh, invalidate and read semantic materializations"], ["cache_equivalence_proof"]),
    ("observation_ledger", "effectful", "observation_receipt", ["append observations, corrections, supersessions and recalls"], ["history_overwrite"]),
    ("policy_gateway", "effectful", "access_purpose", ["obtain purpose-bound authorization decisions"], ["metric_meaning"]),
    ("disclosure_gateway", "effectful", "disclosure", ["project authorized disclosures and record delivery"], ["visual_design", "metric_evaluation"]),
]
LIBRARIES = [
    {
        "library_id": f"library.{PREFIX}.{local}", "edition": EDITION, "status": "candidate",
        "boundary_kind": kind, "owner_context_ref": cid(owner), "responsibilities": responsibilities,
        "allowed_dependencies": [],
        "allowed_dependency_kinds": ["typed_contract", "immutable_value", "evidence_contract" if kind == "effectful" else "pure_algebra"],
        "forbidden_dependencies": forbidden + (["ambient_clock", "network_io", "mutable_registry", "storage_io"] if kind == "pure" else []),
        "determinism": "deterministic_for_identical_explicit_inputs" if kind == "pure" else "receipt_required_for_external_effects",
        "evidence_refs": context_evidence(owner)[:2],
    }
    for local, kind, owner, responsibilities, forbidden in LIBRARY_ROWS
]


INNOVATION_ROWS = [
    ("sdmx_30_model", 2021, "SDMX 3.0 expanded the statistical information model, including microdata and geospatial support.", "sdmx.31"),
    ("openmetrics_10", 2021, "OpenMetrics 1.0 standardized metric families, samples, labels and exemplars for interchange.", "openmetrics.spec"),
    ("sensorthings_11", 2021, "OGC SensorThings 1.1 sharpened interoperable observation, phenomenon-time and result-time exchange.", "ogc.sensorthings"),
    ("malloy_open_source", 2022, "Malloy emerged as an open semantic modeling and query language over existing SQL engines.", "malloy.repo"),
    ("metricflow_open", 2022, "MetricFlow established an open metric compiler around semantic models, multi-hop joins and metric types.", "dbt.metricflow"),
    ("owl_time_update", 2022, "The updated OWL-Time candidate recommendation clarified calendars, clocks and temporal reference systems.", "w3c.owl_time"),
    ("iso_80000_revision", 2022, "The ISO 80000 quantity-and-unit family received current revisions usable for semantic dimensional checks.", "iso.80000"),
    ("fhir_r5_measure", 2023, "FHIR R5 advanced computable Measure definitions and receipted MeasureReport results as separate artifacts.", "hl7.fhir.measure"),
    ("gum1_2023", 2023, "JCGM GUM-1 refreshed the conceptual introduction to measurement models and uncertainty evaluation.", "jcgm.gum100"),
    ("ecb_fx_framework", 2023, "The ECB published a governance and methodology framework that makes rate purpose and valuation context explicit.", "ecb.fx"),
    ("sql_2023", 2023, "SQL/Foundation 2023 provided a current standards baseline for aggregate, window and null semantics.", "iso.sql2023"),
    ("dbt_semantic_layer", 2023, "dbt integrated semantic models and MetricFlow-style governed metric compilation into its product surface.", "dbt.semantic_models"),
    ("dcat3", 2024, "DCAT 3 added stronger dataset-series, version and catalog interoperability useful to semantic publication.", "w3c.dcat3"),
    ("aggregation_consistency", 2024, "Recent research formalized aggregation consistency errors caused by semantic-layer joins.", "paper.agg_consistency"),
    ("saved_query_exports", 2024, "dbt saved queries made reusable semantic requests materializable as governed exports.", "dbt.saved_queries"),
    ("semantic_views_preview", 2024, "Snowflake introduced first-class semantic views for metrics, facts, dimensions and relationships.", "snowflake.semantic_views"),
    ("openformula_14_candidate", 2024, "OpenFormula 1.4 progressed an updated interoperable formula language with typed function semantics.", "oasis.openformula14"),
    ("sdmx_31", 2025, "SDMX 3.1 added horizontally complex data-structure support and availability constraints.", "sdmx.31"),
    ("openformula_14_standard", 2025, "OASIS approved OpenDocument 1.4 and its OpenFormula part as a standard.", "oasis.openformula14"),
    ("databricks_metric_views", 2025, "Databricks metric views introduced governed measures and dimensions as a queryable SQL-facing object.", "databricks.metric_views"),
    ("semantic_views_general", 2025, "Snowflake advanced semantic views from preview toward governed first-class semantic objects.", "snowflake.semantic_views"),
    ("cube_semantic_sql", 2025, "Cube expanded a SQL-compatible semantic query surface with measure-aware compilation.", "cube.semantic_sql"),
    ("apache_ossie", 2025, "The Open Semantic Interchange effort published a portable schema candidate for datasets, relationships and metrics.", "apache.ossie"),
    ("metricflow_core_integration", 2025, "MetricFlow development moved toward deeper dbt compiler integration and explicit documented metric semantics.", "dbt.metricflow_semantics"),
    ("qudt_35", 2026, "QUDT 3.5 published current schema and vocabulary graphs for quantities, units and dimension vectors.", "qudt.catalog"),
    ("semantic_cache_rollups", 2026, "Open semantic-layer implementations document query-to-rollup matching across joins and aggregate coverage.", "cube.rollup_match"),
]
INNOVATIONS = [
    {
        "innovation_id": f"innovation.{PREFIX}.{local}", "edition": EDITION, "status": "observed_candidate",
        "year": year, "description": description, "innovation_class": "non_language_model_semantic_layer_advance",
        "compiler_relevance": ["new_or_changed_semantic_capability", "provider_offer_or_interchange_evidence"],
        "caveat": "Date, novelty, maturity and interoperability scope require independent review before qualification.",
        "evidence_refs": [sid(source)],
    }
    for local, year, description, source in INNOVATION_ROWS
]


VERTICAL_EXAMPLES = [
    {
        "example_id": "example.smf.counterparty_credit_exposure", "edition": EDITION, "status": "worked_candidate",
        "vertical_label": "counterparty credit risk exposure", "engine_profile": "generic_semantic_metric_compiler",
        "source_shapes": [
            {"role": "netting_set_valuation", "grain": ["counterparty", "netting_set", "valuation_instant", "scenario", "recording_edition"]},
            {"role": "eligible_collateral", "grain": ["netting_set", "collateral_item", "valuation_instant", "recording_edition"]},
        ],
        "metric": {
            "identity": "ccr_exposure_at_default", "population": "active in-scope netting sets at valid and recording cut",
            "grain": ["counterparty", "netting_set", "valuation_date", "scenario"],
            "measure_inputs": ["replacement_cost", "potential_future_exposure", "eligible_collateral_value"],
            "formula_ast": {"call": "max_scalar", "args": [{"literal": {"value": 0, "currency": "reporting_currency"}}, {"call": "subtract", "args": [{"call": "add", "args": [{"ref": "replacement_cost"}, {"ref": "potential_future_exposure"}]}, {"ref": "eligible_collateral_value"}]}]},
            "aggregation": "sum only after per-netting-set formula evaluation; scenario aggregation forbidden without scenario policy",
            "time": {"event": "trade event time", "valid": "economic applicability", "recording": "booked/corrected history", "query": "evaluation request", "as_of": "both valid and recording cut"},
            "currency": "value every input through explicit rate source, direction and valuation instant before addition",
            "missingness": "missing collateral valuation is unknown, never zero; zero EAD is a present floored result",
            "target": "counterparty limit is a separate target edition, never the observed exposure",
        },
        "join_proof": ["collateral items aggregate to netting-set grain before joining", "each netting-set valuation contributes exactly once", "temporal versions are non-overlapping or resolved by precedence"],
        "uncertainty": {"inputs": ["market valuation", "model parameter uncertainty"], "method": "declared scenario distribution or covariance-aware propagation"},
        "expected_refusals": ["ambiguous netting agreement", "missing currency valuation policy", "collateral fanout", "unbound scenario semantics", "incomplete bitemporal cut"],
        "branch_independence": "Uses only generic grain, join, formula, unit, time, uncertainty, target and receipt contracts.",
        "evidence_refs": [sid("basel.saccr"), sid("basel.framework"), sid("ecb.fx")],
    },
    {
        "example_id": "example.smf.hospital_capacity", "edition": EDITION, "status": "worked_candidate",
        "vertical_label": "hospital staffed-bed capacity", "engine_profile": "generic_semantic_metric_compiler",
        "source_shapes": [
            {"role": "bed_availability_interval", "grain": ["facility", "service", "bed", "valid_interval", "recording_edition"]},
            {"role": "bed_occupancy_interval", "grain": ["facility", "service", "bed", "encounter", "valid_interval", "recording_edition"]},
        ],
        "metric": {
            "identity": "staffed_bed_occupancy_ratio", "population": "staffed and operational beds eligible at census instant",
            "grain": ["facility", "service", "census_instant"],
            "measure_inputs": ["occupied_eligible_bed_count", "staffed_operational_bed_count"],
            "formula_ast": {"call": "safe_divide", "args": [{"ref": "occupied_eligible_bed_count"}, {"ref": "staffed_operational_bed_count"}, {"literal": "undefined_on_zero_denominator"}]},
            "aggregation": "ratio of separately reaggregated numerator and denominator counts, never average of facility percentages",
            "time": {"event": "admission/discharge and bed-status transition", "valid": "occupancy/availability interval", "recording": "reported/corrected history", "query": "census request", "as_of": "valid census instant plus recording cut"},
            "unit": "dimensionless ratio disclosed as percent; bed counts remain counts",
            "missingness": "unreported staffed status is unknown; zero staffed beds makes ratio undefined rather than zero",
            "target": "occupancy target band is a separately governed target, not an observation",
        },
        "join_proof": ["occupancy is interval-matched to one eligible bed at the census cut", "multiple encounter overlaps for one bed are refused", "counts aggregate to facility-service before ratio"],
        "uncertainty": {"inputs": ["reporting latency", "status misclassification"], "method": "bounded provisional interval until finality horizon"},
        "expected_refusals": ["unknown bed eligibility", "overlapping occupancy intervals", "zero denominator without policy", "averaging percentages", "missing recording cut"],
        "branch_independence": "Uses the same generic grain, join, formula, unit, time, uncertainty, target and receipt contracts as the financial example.",
        "evidence_refs": [sid("who.capacity"), sid("hl7.fhir.measure"), sid("hl7.fhir.report"), sid("fhir.location"), sid("fhir.encounter")],
    },
]


GAP_ROWS = [
    ("cross_provider_function_equivalence", "No complete machine-verifiable equivalence registry spans formula and semantic-query providers."),
    ("summarizability_proof_automation", "Automated proofs remain incomplete for ragged, non-strict and temporal hierarchies."),
    ("data_dependent_cardinality", "Constraint validity and cardinality may change by cut; durable evidence formats need qualification."),
    ("fanout_safe_holistic", "Portable fanout-safe treatment for holistic aggregates is not generally available."),
    ("semantic_cache_containment", "A decidable portable containment fragment covering metrics, time, missingness and access remains open."),
    ("uncertainty_interchange", "Metric semantic layers lack a broadly adopted covariance/distribution interchange contract."),
    ("fiscal_calendar_interchange", "Fiscal and retail calendar definitions lack a single authoritative interoperable schema."),
    ("currency_valuation_purpose", "Providers vary in representing rate source, side, purpose, cut-off and correction policy."),
    ("absence_reason_interchange", "Null and missing-reason taxonomies are not portable across SQL, cube and metric specifications."),
    ("semantic_version_compatibility", "Version numbers rarely carry machine-checkable directional compatibility claims."),
    ("metric_recall_propagation", "Recall propagation through materializations, caches and disclosures lacks a common protocol."),
    ("finality_model", "Cross-domain finality and revision-horizon vocabulary remains fragmented."),
    ("bitemporal_metrics", "Most metric specifications expose event time but not both valid and recording time."),
    ("access_equivalent_cache", "Equivalence under row, column, purpose and suppression policies needs stronger proof systems."),
    ("approximation_authorization", "Approximate metric offers rarely expose composable error and authorization contracts."),
    ("weighted_hierarchy", "Allocation-weight provenance and temporal validity are inconsistently modeled."),
    ("open_formula_binding", "OpenFormula defines expression semantics but not enterprise semantic-owner binding."),
    ("semantic_query_interchange", "No single open query protocol covers metrics, cohorts, as-of, uncertainty and disclosure."),
    ("provider_conformance", "First-party documentation is not conformance evidence across all versions and dialects."),
    ("innovation_date_audit", "Several 2021-2026 implementation advances require release-note and artifact-level date verification."),
    ("vertical_adjudication", "The two examples demonstrate reuse but require independent industry-owner review."),
    ("fixed_point_formulas", "Safe monotone recursive metric formulas need a bounded portable fixed-point profile."),
    ("semantic_privacy_composition", "Differencing and composition risk across cached metric disclosures needs formal integration."),
    ("benchmark_transferability", "Reference-population transportability and uncertainty are not consistently computable."),
]
GAPS = [
    {
        "gap_id": f"gap.{PREFIX}.{local}", "edition": EDITION, "status": "open",
        "statement": statement, "impact": "Compiler must refuse, narrow the supported profile, or require explicit human qualification.",
        "closure_evidence_required": ["authoritative_semantics", "two_independent_implementations", "negative_tests", "adjudicated_owner"],
        "evidence_refs": [sid("apache.ossie"), sid("paper.agg_consistency")],
    }
    for local, statement in GAP_ROWS
]


CONTEXT_RELATION_ROWS = [
    ("analytical_entity", "published_language", "semantic_model"),
    ("fact_role", "published_language", "measure_definition"),
    ("event_semantics", "published_language", "fact_role"),
    ("observation_assertion", "published_language", "fact_role"),
    ("grain_population", "published_language", "fact_role"),
    ("grain_population", "published_language", "measure_definition"),
    ("grain_population", "published_language", "metric_definition"),
    ("measure_definition", "published_language", "metric_definition"),
    ("dimension_definition", "customer_supplier", "member_code_list"),
    ("member_code_list", "published_language", "hierarchy_rollup"),
    ("dimension_definition", "published_language", "metric_definition"),
    ("hierarchy_rollup", "published_language", "reaggregation"),
    ("semantic_relationship", "customer_supplier", "join_path"),
    ("join_path", "customer_supplier", "fanout_safety"),
    ("fanout_safety", "published_language", "query_validation"),
    ("formula_ast", "published_language", "semantic_type_system"),
    ("semantic_type_system", "published_language", "operator_registry"),
    ("semantic_type_system", "published_language", "function_registry"),
    ("operator_registry", "open_host_service", "formula_ast"),
    ("function_registry", "open_host_service", "formula_ast"),
    ("variable_parameter", "published_language", "formula_ast"),
    ("formula_ast", "customer_supplier", "formula_definition"),
    ("formula_definition", "customer_supplier", "formula_binding"),
    ("formula_binding", "customer_supplier", "formula_evaluation"),
    ("partiality_missingness", "published_language", "semantic_type_system"),
    ("unit_quantity", "published_language", "semantic_type_system"),
    ("currency_valuation", "customer_supplier", "formula_evaluation"),
    ("ratio_rate_index", "published_language", "metric_definition"),
    ("aggregation_algebra", "published_language", "metric_definition"),
    ("aggregation_algebra", "customer_supplier", "decomposable_state"),
    ("decomposable_state", "published_language", "reaggregation"),
    ("additivity_posture", "published_language", "reaggregation"),
    ("population_cohort", "published_language", "metric_definition"),
    ("filter_predicate", "published_language", "population_cohort"),
    ("filter_predicate", "published_language", "metric_definition"),
    ("formula_binding", "published_language", "metric_definition"),
    ("metric_definition", "customer_supplier", "metric_governance"),
    ("metric_definition", "customer_supplier", "kpi_target"),
    ("benchmark_reference", "published_language", "kpi_target"),
    ("calendar_time", "published_language", "metric_definition"),
    ("fiscal_period", "conformist", "calendar_time"),
    ("bitemporal_interpretation", "published_language", "asof_cut"),
    ("asof_cut", "published_language", "metric_definition"),
    ("validity_finality", "published_language", "observation_receipt"),
    ("uncertainty", "published_language", "metric_definition"),
    ("metric_governance", "published_language", "semantic_model"),
    ("semantic_model", "customer_supplier", "model_publication"),
    ("model_publication", "open_host_service", "semantic_query"),
    ("semantic_query", "customer_supplier", "query_validation"),
    ("query_validation", "customer_supplier", "semantic_lowering"),
    ("semantic_lowering", "published_language", "formula_evaluation"),
    ("semantic_lowering", "customer_supplier", "materialization"),
    ("materialization", "customer_supplier", "semantic_cache"),
    ("semantic_cache", "customer_supplier", "formula_evaluation"),
    ("formula_evaluation", "runtime_receipt", "observation_receipt"),
    ("observation_receipt", "published_language", "disclosure"),
    ("access_purpose", "policy_projection", "semantic_query"),
    ("access_purpose", "policy_projection", "semantic_cache"),
    ("access_purpose", "policy_projection", "disclosure"),
    ("lifecycle_version", "shared_kernel", "formula_definition"),
    ("lifecycle_version", "shared_kernel", "metric_definition"),
    ("lifecycle_version", "shared_kernel", "semantic_model"),
    ("compatibility_migration", "customer_supplier", "model_publication"),
    ("metric_governance", "authority_delegation", "model_publication"),
]
CONTEXT_RELATIONS = [
    {
        "relation_id": f"relation.{PREFIX}.{index:03d}", "edition": EDITION, "status": "candidate",
        "upstream_context_ref": cid(upstream), "relationship_kind": kind,
        "downstream_context_ref": cid(downstream),
        "translation_rule": "Consume the upstream exported contract by exact identity and edition; do not duplicate its owner.",
        "failure_posture": "refuse_unresolved_or_incompatible_contract",
        "evidence_refs": list(dict.fromkeys(context_evidence(upstream)[:1] + context_evidence(downstream)[:1])),
    }
    for index, (upstream, kind, downstream) in enumerate(CONTEXT_RELATION_ROWS, 1)
]


EVIDENCE = [
    {
        "evidence_id": f"evidence.{PREFIX}.{local}", "edition": EDITION, "status": "candidate_assertion",
        "source_ref": sid(local),
        "claim_scope": topics,
        "assertion": f"The named source is evidence for its declared {', '.join(topics)} scope, not for universal semantic ownership or provider conformance.",
        "evidence_strength": "primary_or_official" if kind != "community_spec" else "community_specification",
        "limitations": ["Applicability outside the source's conformance target requires an explicit mapping.", "Publication metadata and current URL require periodic re-verification."],
    }
    for local, _title, _publisher, kind, _url, _year, topics in SOURCE_ROWS
]


def schema(title: str, id_field: str, required: list[str], properties: dict[str, Any] | None = None) -> dict[str, Any]:
    props = {
        id_field: {"type": "string", "minLength": 1},
        "edition": {"type": "integer", "minimum": 1},
        "status": {"type": "string", "minLength": 1},
        **(properties or {}),
    }
    for field in required:
        props.setdefault(field, {})
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema", "title": title, "type": "object",
        "required": [id_field, "edition", "status", *required], "properties": props, "additionalProperties": True,
    }


SCHEMAS = {
    "source.schema.json": schema("Semantic evidence source", "source_id", ["title", "url", "supports_topics"], {"title": {"type": "string"}, "url": {"type": "string", "format": "uri"}, "supports_topics": {"type": "array", "minItems": 1}}),
    "bounded-context-candidate.schema.json": schema("Bounded context candidate", "context_id", ["name", "sovereign_question", "owns", "excludes", "evidence_refs"], {"owns": {"type": "array", "minItems": 1}, "excludes": {"type": "array", "minItems": 1}}),
    "semantic-record.schema.json": schema("Semantic type, operation, decision, formula, aggregate, join or time record", "record_id", ["record_kind", "owner_context_ref", "meaning", "signature", "laws", "refusal_conditions", "evidence_refs"], {"record_kind": {"enum": ["semantic_type", "formula_ast_node", "formula_operator", "formula_function", "aggregation", "join_law", "time_semantic", "operation", "decision_point"]}, "laws": {"type": "array", "minItems": 1}}),
    "ubiquitous-language.schema.json": schema("Ubiquitous language candidate", "term_id", ["canonical_term", "definition", "owner_context_ref", "distinguish_from"], {"distinguish_from": {"type": "array", "minItems": 1}}),
    "invariant-refusal.schema.json": schema("Invariant, algebra law, proof obligation or refusal", "law_id", ["law_kind", "statement", "failure_posture"], {"law_kind": {"enum": ["invariant", "algebra_law", "proof_obligation", "refusal"]}}),
    "lifecycle.schema.json": schema("Semantic lifecycle", "lifecycle_id", ["artifact_kind", "owner_context_ref", "states", "transition_contract"], {"states": {"type": "array", "minItems": 2}}),
    "compiler-mapping.schema.json": schema("Requirement offer compiler mapping", "mapping_id", ["intent_class", "owner_context_ref", "requirement", "offer_contract", "proof_obligations", "refusal_codes"]),
    "library-boundary.schema.json": schema("Pure or effectful library boundary", "library_id", ["boundary_kind", "owner_context_ref", "responsibilities", "forbidden_dependencies"], {"boundary_kind": {"enum": ["pure", "effectful"]}}),
    "innovation.schema.json": schema("2021-2026 non-language-model innovation", "innovation_id", ["year", "description", "evidence_refs"], {"year": {"type": "integer", "minimum": 2021, "maximum": 2026}}),
    "vertical-example.schema.json": schema("Vertical semantic model example", "example_id", ["vertical_label", "engine_profile", "metric", "join_proof", "branch_independence", "evidence_refs"]),
    "gap.schema.json": schema("Open coverage gap", "gap_id", ["statement", "impact", "closure_evidence_required"]),
    "context-relation.schema.json": schema("Bounded context relation", "relation_id", ["upstream_context_ref", "relationship_kind", "downstream_context_ref", "translation_rule"]),
    "evidence.schema.json": schema("Evidence assertion", "evidence_id", ["source_ref", "claim_scope", "assertion", "evidence_strength"]),
}


OUTPUTS = {
    "sources.jsonl": SOURCES,
    "bounded-context-candidates.jsonl": CONTEXTS,
    "semantic-records.jsonl": SEMANTIC_RECORDS,
    "ubiquitous-language.jsonl": TERMS,
    "invariants-refusals.jsonl": LAWS,
    "lifecycles.jsonl": LIFECYCLES,
    "compiler-mappings.jsonl": COMPILER_MAPPINGS,
    "library-boundaries.jsonl": LIBRARIES,
    "innovations-2021-2026.jsonl": INNOVATIONS,
    "vertical-examples.jsonl": VERTICAL_EXAMPLES,
    "gaps.jsonl": GAPS,
    "context-relations.jsonl": CONTEXT_RELATIONS,
    "evidence.jsonl": EVIDENCE,
}


def build() -> None:
    SCHEMA.mkdir(exist_ok=True)
    for filename, value in SCHEMAS.items():
        (SCHEMA / filename).write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    for filename, rows in OUTPUTS.items():
        dump_jsonl(filename, rows)
    counts = {name: len(rows) for name, rows in OUTPUTS.items()}
    kinds = Counter(row["record_kind"] for row in SEMANTIC_RECORDS)
    manifest = {
        "universe_id": "san.domain-atlas.semantic-metrics-formulas", "edition": EDITION,
        "status": "active_research_candidates", "completion_claim": False,
        "scope": "Provider-neutral meaning layer for facts, dimensions, measures, metrics, formulas, aggregation, joins, time, units, uncertainty, semantic queries and metric observations.",
        "exclusions": ["analytical_case_and_method_universe", "business_intelligence_visualization", "physical_query_kernel_ownership", "language_model_semantics"],
        "generated_files": sorted(OUTPUTS), "schema_files": sorted(SCHEMAS),
        "counts": counts, "semantic_record_kinds": dict(sorted(kinds.items())),
        "thresholds": {"sources_min": 60, "contexts_min": 45, "semantic_records_min": 200, "innovations_min": 20, "vertical_examples_exact": 2},
    }
    dump_json("manifest.json", manifest)
    dump_json("coverage-report.json", {
        "edition": EDITION, "status": "candidate_coverage", "counts": counts,
        "semantic_record_kinds": dict(sorted(kinds.items())),
        "distinctions_checked": [
            "business_term_vs_dimension_member", "observation_vs_fact", "measure_vs_metric_vs_kpi",
            "formula_definition_vs_binding_vs_evaluation", "null_vs_absent_vs_zero",
            "event_vs_valid_vs_recording_vs_query_time", "entity_relation_vs_analytical_join",
            "additivity_vs_decomposability", "target_vs_observed_value",
            "unit_conversion_vs_currency_valuation", "semantic_cache_equivalence_vs_sql_text",
            "governed_metric_vs_dashboard_tile",
        ],
        "open_world_notice": "Counts demonstrate bounded coverage, not proof of completeness. All records remain candidates unless separately qualified.",
    })


if __name__ == "__main__":
    build()
