#!/usr/bin/env python3
"""Canonical product adjudication for semantic metrics, formulas and semantic query."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "source.json"
AXES = ["user", "job", "adoption", "semantics", "authority", "lifecycle", "operation", "economics", "interface", "market_evidence"]


def ev(ident: str, title: str, publisher: str, uri: str, claim: str, limit: str, cls: str = "official_specification_or_documentation") -> dict[str, Any]:
    return {"source_id": ident, "source_class": cls, "title": title, "publisher": publisher, "uri": uri, "retrieved_at": "2026-08-26", "claim": claim, "scope_limit": limit}


def art(ident: str, kind: str, name: str, definition: str, refs: list[str], owner: str | None = None, adoption: bool = False, operated: bool = False) -> dict[str, Any]:
    return {"artifact_id": ident, "kind": kind, "name": name, "status": "candidate", "semantic_owner_ref": owner, "adoption_unit": adoption, "operated": operated, "definition": definition, "evidence_refs": refs}


def split(scores: list[int], refs: list[str], label: str) -> dict[str, Any]:
    return {axis: {"score": score, "finding": f"{label}: scoped evidence for the {axis} boundary; no score implies provider qualification or ratification.", "evidence_refs": refs} for axis, score in zip(AXES, scores, strict=True)}


def camel(value: str) -> str:
    return "".join(part.capitalize() for part in value.replace("-", "_").replace(".", "_").split("_"))


SOURCES = [
    ("openformula14", "OpenDocument 1.4 Part 4: OpenFormula", "OASIS", "https://docs.oasis-open.org/office/OpenDocument/v1.4/os/part4-formula/OpenDocument-v1.4-os-part4-formula.html", "Defines formula syntax, types, operators, functions and error semantics.", "Spreadsheet formula exchange does not define enterprise semantic owners, data binding, query execution or authorization."),
    ("sdmx31", "SDMX 3.1 Technical Specifications", "SDMX", "https://sdmx.org/standards-2/", "Defines statistical structures, dimensions, measures, attributes and exchange formats.", "Statistical interchange does not define every business metric or provider conformance."),
    ("sdmx_vtl21", "Validation and Transformation Language 2.1", "SDMX", "https://sdmx.org/?page_id=5096", "Defines typed validation and transformation expressions over statistical data.", "VTL scope and data model are not a universal formula or metric language."),
    ("rdf_cube", "RDF Data Cube Vocabulary", "W3C", "https://www.w3.org/TR/vocab-data-cube/", "Separates data structures, dimensions, measures, attributes, slices and observations with integrity constraints.", "RDF cube validity does not prove summarizability, fanout safety or business fitness."),
    ("prov_dm", "PROV Data Model", "W3C", "https://www.w3.org/TR/prov-dm/", "Defines entities, activities, agents and derivation provenance.", "Provenance does not prove formula correctness, causation or authorization."),
    ("owl_time", "Time Ontology in OWL", "W3C and OGC", "https://www.w3.org/TR/owl-time/", "Defines instants, intervals, temporal positions and reference systems.", "It does not select a fiscal calendar, time-zone edition or metric finality policy."),
    ("shacl", "Shapes Constraint Language", "W3C", "https://www.w3.org/TR/shacl/", "Defines validation constraints over RDF graphs.", "Shape conformance is not semantic truth, calculation correctness or product approval."),
    ("sparql11", "SPARQL 1.1 Query Language", "W3C", "https://www.w3.org/TR/sparql11-query/", "Defines graph pattern matching, solution modifiers and aggregates.", "A query language does not own metric meaning or observation authority."),
    ("odrl", "ODRL Information Model 2.2", "W3C", "https://www.w3.org/TR/odrl-model/", "Defines permission, prohibition, duty and policy expressions.", "Policy modeling does not prove enforcement or disclosure completion."),
    ("qudt35", "QUDT Catalog 3.5", "QUDT", "https://www.qudt.org/catalog/qudt-catalog.html", "Publishes quantity kinds, units, dimension vectors and conversions.", "A unit catalog does not choose valuation purpose, precision or domain authority."),
    ("ucum", "Unified Code for Units of Measure", "UCUM", "https://ucum.org/ucum", "Defines computable unit expressions, canonical forms and conversions.", "Unit-code compatibility does not prove quantity-kind or business-meaning compatibility."),
    ("nist_si", "NIST Guide for the Use of SI", "NIST", "https://www.nist.gov/pml/special-publication-811", "Defines SI quantity and unit usage guidance.", "Guidance does not define enterprise metric formulas or currency valuation."),
    ("rfc3339", "RFC 3339", "IETF", "https://www.rfc-editor.org/rfc/rfc3339.html", "Defines an Internet date-time profile.", "Timestamp syntax does not define valid, recording, event, query or finality roles."),
    ("tzdb", "Time Zone Database", "IANA", "https://www.iana.org/time-zones", "Publishes editioned civil-time rules.", "A zone database does not choose business calendars or correction policy."),
    ("ecb_fx", "Euro Foreign Exchange Reference Rates", "European Central Bank", "https://www.ecb.europa.eu/stats/policy_and_exchange_rates/euro_reference_exchange_rates/html/index.en.html", "Publishes purpose-scoped reference exchange rates.", "A published rate is not automatically appropriate for accounting, risk, settlement or historical restatement."),
    ("gum", "Guide to the Expression of Uncertainty in Measurement", "JCGM and BIPM", "https://www.bipm.org/en/committees/jc/jcgm/publications", "Defines measurement-model uncertainty evaluation and reporting.", "Measurement uncertainty does not cover every statistical or model uncertainty contract."),
    ("ogc_oms", "Observations, Measurements and Samples", "OGC", "https://www.ogc.org/standard/om/", "Defines observation, feature of interest, observed property, result and procedure roles.", "Observation modeling does not make an observed result a governed business metric."),
    ("fhir_measure", "FHIR R5 Measure", "HL7", "https://hl7.org/fhir/R5/measure.html", "Defines versioned clinical quality measure logic, populations and scoring.", "A vertical measure definition remains governed by healthcare vocabulary and authority."),
    ("fhir_report", "FHIR R5 MeasureReport", "HL7", "https://hl7.org/fhir/R5/measurereport.html", "Separates a measure definition from an evaluated report occurrence.", "A report does not prove input quality, authorization or clinical decision correctness."),
    ("cql", "Clinical Quality Language 1.5", "HL7", "https://cql.hl7.org/", "Defines a formal clinical expression language and execution model.", "Clinical formula semantics are a vertical specialization, not the horizontal product owner."),
    ("postgres_aggregate", "PostgreSQL Aggregate Functions", "PostgreSQL", "https://www.postgresql.org/docs/current/functions-aggregate.html", "Documents aggregate behavior including null and order sensitivity.", "One SQL engine's behavior is not a portable aggregation contract."),
    ("postgres_window", "PostgreSQL Window Functions", "PostgreSQL", "https://www.postgresql.org/docs/current/functions-window.html", "Documents window partitions, order and frames.", "Provider syntax does not supply business calendar or metric-grain authority."),
    ("mdx", "Multidimensional Expressions Reference", "Microsoft", "https://learn.microsoft.com/en-us/analysis-services/multidimensional-models/mdx/mdx-reference", "Defines multidimensional expressions over cubes.", "MDX is one provider language and not a universal metric contract."),
    ("dax", "DAX Overview", "Microsoft", "https://learn.microsoft.com/en-us/dax/dax-overview", "Defines formula semantics for tabular analytical models.", "DAX expressions and evaluation context are provider-specific."),
    ("xmla", "XML for Analysis", "Microsoft", "https://learn.microsoft.com/en-us/analysis-services/xmla/xml-for-analysis-xmla-reference", "Defines analytical service discovery and execution messages.", "A wire protocol does not establish cross-provider semantic equivalence."),
    ("gray_cube", "Data Cube: A Relational Aggregation Operator", "Microsoft Research", "https://doi.org/10.1016/S0169-023X(96)00011-1", "Formalizes cube grouping and aggregation operations.", "The operator does not solve semantic ownership, fanout or policy.", "primary_research"),
    ("agg_consistency", "Aggregation Consistency Errors in Semantic Layers", "CIDR", "https://arxiv.org/abs/2307.00417", "Formalizes join-induced aggregation errors and consistency concerns.", "Research results do not qualify current products or solve every holistic aggregate.", "primary_research"),
    ("substrait", "Substrait Specification", "Substrait", "https://substrait.io/spec/specification/", "Defines portable typed relational plans and functions.", "A lowered query plan is not a semantic metric definition or equivalence proof."),
    ("calcite_mv", "Apache Calcite Materialized Views", "Apache Calcite", "https://calcite.apache.org/docs/materialized_views.html", "Documents query rewriting using materialized views.", "Rewrite support does not prove semantic containment under every metric, policy and time posture."),
    ("dbt_semantic_models", "dbt Semantic Models", "dbt Labs", "https://docs.getdbt.com/docs/build/semantic-models", "Defines entities, dimensions, time and simple metrics in a semantic graph.", "Current dbt syntax and supported warehouses are one implementation profile."),
    ("dbt_metrics", "dbt Metrics", "dbt Labs", "https://docs.getdbt.com/docs/build/metrics-overview", "Defines simple, ratio, derived, cumulative and conversion metric types.", "Supported types and defaults do not define universal metric semantics."),
    ("dbt_metricflow", "About MetricFlow", "dbt Labs", "https://docs.getdbt.com/docs/build/about-metricflow", "Documents semantic-model metric query construction and SQL generation.", "SQL generation is not evidence of cross-engine result equivalence."),
    ("cube_measures", "Cube Measures", "Cube", "https://docs.cube.dev/reference/data-modeling/measures", "Defines aggregation types, calculated measures, filters and rolling behavior.", "Provider measure types and preview features are not universal contracts."),
    ("cube_joins", "Cube Joins", "Cube", "https://docs.cube.dev/docs/data-modeling/joins", "Defines directed relationship types and primary-key requirements to control join fanout.", "Declared relationships do not prove real data cardinality or all aggregate safety."),
    ("cube_preagg", "Cube Pre-aggregations", "Cube", "https://docs.cube.dev/docs/pre-aggregations/index", "Defines materialized rollups and query routing to pre-aggregations.", "A cache hit or rewrite does not prove semantic equivalence, freshness or authorized reuse."),
    ("looker_symmetric", "Looker Symmetric Aggregates", "Google Cloud", "https://cloud.google.com/looker/docs/best-practices/understanding-symmetric-aggregates", "Documents fanout-safe aggregation techniques over joined explores.", "Provider-specific rewriting is not a universal proof for every aggregation."),
    ("snowflake_semantic", "Snowflake Semantic Views", "Snowflake", "https://docs.snowflake.com/en/user-guide/views-semantic/overview", "Defines logical tables, facts, metrics, dimensions, relationships and query interfaces.", "A warehouse-native semantic object does not own enterprise vocabulary or prove portable exit."),
    ("databricks_metric", "Unity Catalog Metric Views", "Databricks", "https://docs.databricks.com/aws/en/uc-semantics/metric-views", "Defines YAML metric views, measures, dimensions and materialization-backed rewrites.", "A platform-native metric view is an implementation, not the canonical product model."),
    ("ossie", "Apache Ossie Core Specification", "Apache Software Foundation", "https://github.com/apache/ossie/blob/main/core-spec/osi-schema.json", "Defines an emerging JSON/YAML interchange schema for datasets, relationships and metrics.", "Schema acceptance does not prove semantic completeness, behavioral equivalence or provider qualification."),
    ("openmetrics", "OpenMetrics Specification", "CNCF", "https://github.com/prometheus/OpenMetrics/blob/main/specification/OpenMetrics.md", "Defines operational metric families, samples and exemplars.", "Telemetry samples are not governed business metric definitions or observations by default."),
    ("otel_metrics", "OpenTelemetry Metrics Data Model", "OpenTelemetry", "https://opentelemetry.io/docs/specs/otel/metrics/data-model/", "Defines sums, gauges, histograms, temporality and metric streams.", "Operational telemetry aggregation does not establish business KPI meaning."),
]


# suffix, semantic name, operation, decision, invariant, refusal, evidence ids
LIBRARY_SPECS = [
    ("formula_parser", "Formula syntax", "parse_formula", "formula_language_edition", "parse_preserves_source_and_never_binds_ambient_names", "formula_syntax_invalid", ["openformula14", "sdmx_vtl21"]),
    ("ast_canonicalizer", "Formula AST canonicalization", "canonicalize_formula", "normalization_profile", "canonicalization_preserves_typed_semantics_or_refuses", "canonicalization_unproved", ["openformula14"]),
    ("semantic_type_checker", "Semantic formula types", "type_formula", "coercion_and_partiality", "types_include_nullability_partiality_units_grain_and_time_roles", "type_mismatch", ["openformula14", "ucum"]),
    ("dimension_algebra", "Quantity dimension algebra", "compose_dimensions", "quantity_kind_compatibility", "dimension_vector_compatibility_is_required_but_not_sufficient_for_meaning", "quantity_kind_mismatch", ["qudt35", "ucum"]),
    ("unit_conversion_algebra", "Unit conversion algebra", "convert_unit", "conversion_edition_and_precision", "conversion_rules_are_explicit_editioned_and_loss_accounted", "conversion_unavailable", ["qudt35", "ucum", "nist_si"]),
    ("missingness_algebra", "Missingness and partiality", "propagate_partiality", "absence_reason_policy", "null_absent_unknown_suppressed_not_applicable_error_and_zero_are_distinct", "absence_semantics_unknown", ["openformula14", "rdf_cube"]),
    ("aggregation_algebra", "Aggregation algebra", "aggregate_values", "aggregate_and_empty_input_profile", "mergeable_state_empty_input_null_order_and_exactness_are_declared", "aggregation_undefined", ["gray_cube", "postgres_aggregate"]),
    ("summarizability_checker", "Summarizability proof", "prove_summarizability", "additivity_and_hierarchy_posture", "additivity_and_decomposability_are_independent_and_rollup_requires_proof", "summarizability_unproved", ["gray_cube", "agg_consistency"]),
    ("fanout_analyzer", "Fanout safety", "prove_fanout_safety", "multiplicity_preservation", "every_measure_contribution_multiplicity_is_preserved_or_explicitly_allocated", "fanout_unsafe", ["agg_consistency", "cube_joins", "looker_symmetric"]),
    ("calendar_algebra", "Calendar and period algebra", "bucket_time", "calendar_zone_and_boundary_editions", "period_identity_includes_calendar_zone_boundaries_and_edition", "calendar_unbound", ["owl_time", "rfc3339", "tzdb"]),
    ("bitemporal_algebra", "Bitemporal metric cut", "select_bitemporal_cut", "valid_recording_event_query_time", "valid_recording_event_and_query_time_are_independent_roles", "temporal_cut_ambiguous", ["owl_time", "rdf_cube"]),
    ("uncertainty_algebra", "Metric uncertainty", "propagate_uncertainty", "uncertainty_model_and_dependence", "uncertainty_and_approximation_never_disappear_during_composition", "uncertainty_model_missing", ["gum"]),
    ("semantic_query_canonicalizer", "Semantic query identity", "canonicalize_semantic_query", "query_identity_profile", "identity_covers_editions_grain_population_filters_time_units_uncertainty_and_policy", "semantic_query_incomplete", ["dbt_metricflow", "substrait"]),
    ("cache_equivalence_prover", "Semantic cache equivalence", "prove_cache_reuse", "equivalence_or_containment", "matching_sql_is_neither_necessary_nor_sufficient_for_semantic_reuse", "cache_equivalence_unproved", ["calcite_mv", "cube_preagg"]),
    ("compatibility_diff", "Semantic edition compatibility", "diff_semantic_editions", "directional_compatibility", "version_numbers_do_not_imply_semantic_compatibility", "compatibility_unknown", ["ossie", "sdmx31"]),
    ("semantic_registry", "Semantic definition registry", "publish_semantic_edition", "approval_deprecation_and_recall", "published_definitions_are_immutable_and_corrections_create_new_editions", "publication_unauthorized", ["ossie", "dbt_semantic_models"]),
    ("binding_resolver", "Semantic binding", "bind_semantic_definition", "snapshot_and_owner_resolution", "every_free_reference_binds_to_one_owner_and_exact_edition", "binding_ambiguous", ["dbt_semantic_models", "snowflake_semantic"]),
    ("formula_runtime", "Formula evaluation occurrence", "evaluate_bound_formula", "effect_budget_and_provider", "formula_definition_binding_and_evaluation_are_distinct_identities", "evaluation_failed", ["openformula14", "cql"]),
    ("exchange_rate_gateway", "Currency valuation gateway", "obtain_rate_set", "rate_source_side_purpose_and_cutoff", "unit_conversion_is_not_currency_valuation_and_rate_purpose_is_explicit", "valuation_rate_unavailable", ["ecb_fx"]),
    ("semantic_query_gateway", "Semantic query execution", "execute_semantic_query", "lowering_target_and_budget", "semantic_query_is_not_sql_and_lowering_loss_is_explicit", "no_compatible_query_offer", ["dbt_metricflow", "substrait", "snowflake_semantic"]),
    ("materialization_store", "Semantic materialization", "reconcile_materialization", "refresh_invalidation_and_cut", "materialization_never_acquires_definition_or_source_authority", "materialization_stale", ["cube_preagg", "databricks_metric"]),
    ("observation_ledger", "Metric observation ledger", "append_metric_observation", "correction_supersession_and_recall", "metric_definition_and_metric_observation_are_distinct_and_history_is_append_only", "observation_receipt_incomplete", ["rdf_cube", "fhir_report", "prov_dm"]),
    ("policy_gateway", "Metric use-policy gateway", "obtain_metric_policy", "purpose_population_and_projection", "semantic_service_imports_policy_and_cannot_self_authorize", "policy_refused", ["odrl"]),
    ("disclosure_gateway", "Metric disclosure", "disclose_metric_result", "suppression_rounding_and_evidence", "disclosure_is_an_effect_distinct_from_evaluation", "disclosure_refused", ["odrl", "rdf_cube"]),
]


SEMANTIC_GAPS = [
    ("cross_provider_function_equivalence", "No complete machine-verifiable registry proves function equivalence across formula and semantic-query providers."),
    ("summarizability_automation", "Ragged, non-strict and temporal hierarchy summarizability remains only partially decidable or automated."),
    ("data_dependent_cardinality", "Join cardinality and constraints can change by data cut and lack portable durable proof receipts."),
    ("holistic_fanout", "No general portable fanout-safe decomposition exists for every holistic aggregate."),
    ("semantic_cache_containment", "No broadly adopted decidable containment fragment covers metrics, time, partiality, uncertainty and access together."),
    ("uncertainty_interchange", "Semantic layers lack a broadly adopted covariance and distribution interchange contract."),
    ("fiscal_calendar_interchange", "Fiscal and retail calendars lack one authoritative interoperable definition format."),
    ("currency_valuation_purpose", "Rate source, side, purpose, cutoff and correction policy are inconsistently represented."),
    ("absence_reason_interchange", "Null and missing-reason taxonomies do not port cleanly across SQL, cube and metric specifications."),
    ("semantic_compatibility", "Version labels rarely carry machine-checkable directional semantic-compatibility claims."),
    ("metric_recall", "Recall propagation through observations, materializations, caches and disclosures lacks a common protocol."),
    ("finality_model", "Cross-domain finality, revision horizon and correction vocabulary remains fragmented."),
    ("bitemporal_metrics", "Most metric specifications expose event time without both valid and recording time."),
    ("access_equivalent_cache", "Cache equivalence under row, column, purpose and suppression policy lacks adequate proof systems."),
    ("approximation_authority", "Approximate metric offers rarely expose composable error bounds and authorization contracts."),
    ("fixed_point_formulas", "Safe recursive metric formulas lack a broadly portable bounded monotone fixed-point profile."),
]


def source() -> dict[str, Any]:
    sources = [ev(f"evidence.{ident}", title, publisher, uri, claim, limit, cls) for ident, title, publisher, uri, claim, limit, *rest in SOURCES for cls in [rest[0] if rest else "official_specification_or_documentation"]]
    kinds = [
        {"kind": "architecture_pattern", "definition": "A reusable arrangement without independent adoption or semantic authority."},
        {"kind": "suite", "definition": "Packaging of products and components without transferred ownership."},
        {"kind": "product", "definition": "An independently adopted and operated user-outcome promise."},
        {"kind": "control_component", "definition": "A subsystem without a complete adoption, support and exit promise."},
        {"kind": "capability", "definition": "A typed selectable behavior required or offered at a boundary."},
        {"kind": "semantic_contract", "definition": "Owner of one meaning, identity, lifecycle, invariants and refusals."},
        {"kind": "standard", "definition": "An exact external edition specializing a contract."},
        {"kind": "library_contract", "definition": "A reusable provider-neutral semantic or effect-port seam."},
        {"kind": "implementation", "definition": "An observed provider artifact with no canonical semantic authority."},
        {"kind": "neighbor", "definition": "A separate bounded context imported through an explicit contract."},
    ]
    artifacts = [
        art("product.semantic_metric_formula_service", "product", "Semantic Metric and Formula Service", "Lets metric authors publish governed formula/metric editions and lets consumers evaluate them consistently across dimensions, grains, time, units and providers with evidence.", ["evidence.dbt_semantic_models", "evidence.dbt_metrics", "evidence.cube_measures", "evidence.snowflake_semantic"], adoption=True, operated=True),
        art("pattern.metric_store_query_bundle", "architecture_pattern", "Metric store plus query bundle", "An overloaded packaging label spanning definition registry, evaluation, observations, materializations, query gateway and consumption interfaces; not one additional product.", ["evidence.dbt_metricflow", "evidence.cube_preagg", "evidence.rdf_cube"]),
        art("suite.semantic_layer", "suite", "Semantic layer suite", "Packaging of the semantic metric/formula product with BI, catalog, query and optional model-facing metadata.", ["evidence.ossie", "evidence.snowflake_semantic"]),
        art("component.formula_engine", "control_component", "Formula parser, typer and evaluator", "Pure formula semantics plus explicitly effect-bounded evaluation; not independently a metric product.", ["evidence.openformula14", "evidence.sdmx_vtl21"]),
        art("component.semantic_registry", "control_component", "Semantic definition registry", "Immutable definition editions and lifecycle inside the product.", ["evidence.ossie", "evidence.dbt_semantic_models"]),
        art("component.semantic_query_gateway", "control_component", "Semantic query gateway", "Binds a semantic request, lowers it to a qualified engine and returns evidence.", ["evidence.dbt_metricflow", "evidence.substrait"]),
        art("component.metric_materialization", "control_component", "Metric materialization and cache", "Physical acceleration with explicit semantic-equivalence, cut and policy proofs.", ["evidence.cube_preagg", "evidence.calcite_mv"]),
        art("component.observation_ledger", "control_component", "Metric observation ledger", "Append-only values, errors, corrections, supersessions and recalls distinct from definitions.", ["evidence.rdf_cube", "evidence.fhir_report"]),
        art("component.optional_model_assistance", "control_component", "Optional model or agent assistance", "Intent-selected proposal/explanation surface over typed semantic records; never authoritative.", ["evidence.ossie"]),
        art("semantic.metric_definition", "semantic_contract", "Metric definition", "Versioned business measure semantics, not an evaluated value.", ["evidence.dbt_metrics", "evidence.snowflake_semantic"]),
        art("semantic.metric_observation", "semantic_contract", "Metric observation", "An evaluated value-or-error at an exact population, grain, time and data cut.", ["evidence.rdf_cube", "evidence.fhir_report"]),
        art("semantic.measure", "semantic_contract", "Measure", "An aggregation input with collection, null, empty-input, exactness and merge semantics.", ["evidence.rdf_cube", "evidence.cube_measures"]),
        art("semantic.kpi_target_benchmark", "semantic_contract", "KPI, target and benchmark roles", "Distinct roles that may reference metrics but do not collapse into observed values.", ["evidence.fhir_measure", "evidence.sdmx31"]),
        art("semantic.business_formula", "semantic_contract", "Business formula", "Immutable formula definition with typed AST and dependency contract.", ["evidence.openformula14", "evidence.dbt_metrics"]),
        art("standard.openformula14", "standard", "OpenFormula 1.4", "Editioned spreadsheet-formula interchange language.", ["evidence.openformula14"]),
        art("standard.sdmx31", "standard", "SDMX 3.1", "Editioned statistical-data and metadata interchange family.", ["evidence.sdmx31"]),
        art("standard.ossie", "standard", "Apache Ossie candidate interchange", "Emerging provider-neutral semantic metadata schema.", ["evidence.ossie"]),
        art("implementation.dbt_metricflow", "implementation", "dbt MetricFlow", "Observed semantic-model and metric-query implementation; unqualified here.", ["evidence.dbt_semantic_models", "evidence.dbt_metricflow"]),
        art("implementation.cube", "implementation", "Cube", "Observed measures, joins, materialization and query implementation; unqualified here.", ["evidence.cube_measures", "evidence.cube_joins", "evidence.cube_preagg"]),
        art("implementation.looker", "implementation", "Looker", "Observed multidimensional semantic model and symmetric-aggregate implementation; unqualified here.", ["evidence.looker_symmetric"]),
        art("implementation.snowflake_semantic", "implementation", "Snowflake Semantic Views", "Observed warehouse-native semantic object; unqualified here.", ["evidence.snowflake_semantic"]),
        art("implementation.databricks_metric", "implementation", "Databricks Metric Views", "Observed catalog-native metric view; unqualified here.", ["evidence.databricks_metric"]),
        art("neighbor.business_glossary", "neighbor", "Business glossary", "Owns approved human terminology and homonyms.", ["evidence.sdmx31"]),
        art("neighbor.ontology", "neighbor", "Ontology and knowledge model", "Owns formal concepts, axioms and mappings.", ["evidence.shacl"]),
        art("neighbor.source_truth", "neighbor", "Source-system truth", "Owns operational facts and correction authority.", ["evidence.prov_dm"]),
        art("neighbor.query_execution", "neighbor", "Query execution", "Owns physical planning, engine execution and result-stream mechanics.", ["evidence.substrait"]),
        art("neighbor.data_use_policy", "neighbor", "Data-use policy", "Owns purpose, authorization, suppression and disclosure obligations.", ["evidence.odrl"]),
        art("neighbor.presentation", "neighbor", "BI and presentation", "Owns report, dashboard, visualization and interaction lifecycle.", ["evidence.xmla"]),
        art("neighbor.vertical_solution", "neighbor", "Vertical solution pack", "Owns industry vocabulary, thresholds, populations, targets and acceptance authority.", ["evidence.fhir_measure"]),
    ]

    ownership = []
    libraries = []
    requirements = []
    binding_maps = []
    for suffix, semantic_name, operation, decision, invariant, refusal, source_ids in LIBRARY_SPECS:
        owner = f"semantic.smf.{suffix}"
        capability = f"capability.smf.{suffix}"
        refs = [f"evidence.{source_id}" for source_id in source_ids]
        artifacts.append(art(owner, "semantic_contract", semantic_name, f"Owns {semantic_name.lower()} identity, decisions, laws and refusals.", refs))
        artifacts.append(art(capability, "capability", operation.replace("_", " ").title(), f"Typed capability to {operation.replace('_', ' ')} under the {semantic_name.lower()} contract.", refs, owner=owner))
        ownership.append({"meaning_id": f"meaning.smf.{suffix}", "term": semantic_name, "owner_ref": owner, "invariant": invariant, "must_not_be_owned_by": ["neighbor.query_execution", "neighbor.presentation", "component.optional_model_assistance"]})
        effectful = suffix in {"semantic_registry", "formula_runtime", "exchange_rate_gateway", "semantic_query_gateway", "materialization_store", "observation_ledger", "policy_gateway", "disclosure_gateway"}
        typ = camel(suffix)
        libraries.append({"library_id": f"library.adjudicated.smf.{suffix}", "product_ref": "product.semantic_metric_formula_service", "class": "runtime_boundary" if effectful else "semantic_pure", "owner_ref": owner, "provides": [capability], "types": [typ, f"{typ}Decision", f"{typ}Refusal"], "operations": [operation], "decisions": [decision], "invariants": [invariant, "provider_identity_does_not_change_meaning", "generated_output_never_owns_metric_meaning_or_effect_authority"], "refusals": [refusal, "unsupported_capability", "resource_exhausted"], "dependencies": [], "effect_boundary": "effect_intents_and_receipts" if effectful else "pure_no_io", "evidence_refs": refs})
        requirements.append({"requirement_id": f"requirement.smf.{suffix}", "consumer_ref": "product.semantic_metric_formula_service", "capability_ref": capability, "minimum_qualified_offers": 2, "binding_phase": "compile_time" if not effectful else "deployment_time", "status": "unbound", "refusal": "refuse compilation or execution when no exact qualified compatible offer exists"})
        binding_maps.append({"binding_map_id": f"binding.smf.{suffix}", "product_ref": "product.semantic_metric_formula_service", "abstract_library_ref": f"library.adjudicated.smf.{suffix}", "compiler_disposition": "structurally_projected_unqualified", "concrete_library_refs": [f"library.smf.{suffix}"], "gap_ref": None, "portable_offer": False})

    product_refs = ["evidence.dbt_semantic_models", "evidence.dbt_metricflow", "evidence.cube_measures", "evidence.snowflake_semantic", "evidence.databricks_metric"]
    decisions = [
        {"decision_id": "decision.smf.product", "subject_ref": "product.semantic_metric_formula_service", "disposition": "strong_product_candidate", "rationale": "Metric authors and consumers independently adopt an operated promise for governed definitions and consistent evaluation across tools and engines; semantic ownership, lifecycle, support and exit are distinct from BI and query execution.", "evidence_refs": product_refs, "split_test": split([2, 2, 2, 2, 2, 2, 2, 1, 2, 2], product_refs, "Semantic Metric and Formula Service")},
        {"decision_id": "decision.smf.metric_store_bundle", "subject_ref": "pattern.metric_store_query_bundle", "disposition": "reclassify_as_architecture_pattern", "rationale": "Metric store ambiguously names definition registry, observation ledger, materialization cache and query gateway; packaging them does not create a second product.", "evidence_refs": ["evidence.rdf_cube", "evidence.dbt_metricflow", "evidence.cube_preagg"]},
        {"decision_id": "decision.smf.formula_engine", "subject_ref": "component.formula_engine", "disposition": "retain_as_library_and_runtime_component", "rationale": "Formula parsing, typing and evaluation are reusable contracts without an independent enterprise metric outcome promise.", "evidence_refs": ["evidence.openformula14", "evidence.sdmx_vtl21"]},
        {"decision_id": "decision.smf.registry_component", "subject_ref": "component.semantic_registry", "disposition": "retain_inside_product", "rationale": "Definition lifecycle is a semantic component of the adopted metric service; separate product evidence is currently insufficient.", "evidence_refs": ["evidence.ossie", "evidence.dbt_semantic_models"]},
        {"decision_id": "decision.smf.query_component", "subject_ref": "component.semantic_query_gateway", "disposition": "retain_inside_product", "rationale": "The gateway compiles semantic intent into replaceable query engines and does not own physical execution or form a new product by itself.", "evidence_refs": ["evidence.dbt_metricflow", "evidence.substrait"]},
        {"decision_id": "decision.smf.materialization_component", "subject_ref": "component.metric_materialization", "disposition": "retain_as_acceleration_component", "rationale": "Materialization and cache are replaceable physical mechanisms whose reuse requires semantic equivalence, freshness and policy proofs.", "evidence_refs": ["evidence.cube_preagg", "evidence.calcite_mv"]},
        {"decision_id": "decision.smf.definition_observation", "subject_ref": "semantic.metric_observation", "disposition": "retain_split", "rationale": "A metric definition is an immutable meaning; an observation is one evaluated value-or-error at a scoped cut and may be corrected or recalled.", "evidence_refs": ["evidence.rdf_cube", "evidence.fhir_measure", "evidence.fhir_report"]},
        {"decision_id": "decision.smf.measure_metric_kpi", "subject_ref": "semantic.kpi_target_benchmark", "disposition": "retain_roles_split", "rationale": "Measure, metric, KPI, target, benchmark and observed value have different identity and authority.", "evidence_refs": ["evidence.rdf_cube", "evidence.fhir_measure", "evidence.snowflake_semantic"]},
        {"decision_id": "decision.smf.agent_optional", "subject_ref": "component.optional_model_assistance", "disposition": "optional_non_authoritative_extension", "rationale": "Models and agents may propose definitions or explain results when selected, but deterministic parsing, typing, binding, proofs, policy, execution and receipts remain authoritative and work without them.", "evidence_refs": ["evidence.ossie", "evidence.openformula14"]},
    ]

    offers = [
        ("dbt_metricflow", "implementation.dbt_metricflow", ["formula_parser", "semantic_registry", "binding_resolver", "semantic_query_gateway"], ["dbt_semantic_models", "dbt_metrics", "dbt_metricflow"]),
        ("cube", "implementation.cube", ["aggregation_algebra", "fanout_analyzer", "semantic_query_gateway", "materialization_store"], ["cube_measures", "cube_joins", "cube_preagg"]),
        ("looker", "implementation.looker", ["fanout_analyzer", "semantic_query_gateway"], ["looker_symmetric"]),
        ("snowflake", "implementation.snowflake_semantic", ["semantic_registry", "binding_resolver", "semantic_query_gateway"], ["snowflake_semantic"]),
        ("databricks", "implementation.databricks_metric", ["semantic_registry", "semantic_query_gateway", "materialization_store"], ["databricks_metric"]),
    ]
    offer_rows = [{"offer_id": f"offer.smf.{name}", "provider_ref": provider, "capability_refs": [f"capability.smf.{suffix}" for suffix in caps], "status": "observed_unqualified", "qualified_implementation_count": 0, "portable": False, "evidence_refs": [f"evidence.{ref}" for ref in refs]} for name, provider, caps, refs in offers]

    relations = [
        {"relation_id": "relation.smf.suite_packages_product", "from_ref": "suite.semantic_layer", "predicate": "packages", "to_ref": "product.semantic_metric_formula_service", "binding_phase": "authoring"},
        {"relation_id": "relation.smf.product_requires_query", "from_ref": "product.semantic_metric_formula_service", "predicate": "requires", "to_ref": "neighbor.query_execution", "binding_phase": "deployment_time"},
        {"relation_id": "relation.smf.product_imports_glossary", "from_ref": "product.semantic_metric_formula_service", "predicate": "requires", "to_ref": "neighbor.business_glossary", "binding_phase": "authoring"},
        {"relation_id": "relation.smf.product_imports_policy", "from_ref": "product.semantic_metric_formula_service", "predicate": "governed_by", "to_ref": "neighbor.data_use_policy", "binding_phase": "runtime"},
        {"relation_id": "relation.smf.openformula_specializes_formula", "from_ref": "standard.openformula14", "predicate": "specializes", "to_ref": "semantic.business_formula", "binding_phase": "compile_time"},
        {"relation_id": "relation.smf.sdmx_specializes_observation", "from_ref": "standard.sdmx31", "predicate": "specializes", "to_ref": "semantic.metric_observation", "binding_phase": "compile_time"},
    ]
    crosswalks = [
        {"legacy_ref": "candidate.product.semantic_metric", "canonical_refs": ["product.semantic_metric_formula_service"], "disposition": "rename_and_expand_formula_contract"},
        {"legacy_ref": "candidate.product.metric_store_bundle", "canonical_refs": ["pattern.metric_store_query_bundle", "product.semantic_metric_formula_service"], "disposition": "reclassify_bundle"},
        {"legacy_ref": "term.semantic_layer", "canonical_refs": ["suite.semantic_layer", "product.semantic_metric_formula_service"], "disposition": "suite_and_product_split"},
        {"legacy_ref": "term.metric_store", "canonical_refs": ["component.semantic_registry", "component.observation_ledger", "component.metric_materialization"], "disposition": "split_overloaded_term"},
        {"legacy_ref": "term.headless_bi", "canonical_refs": ["product.semantic_metric_formula_service", "neighbor.presentation"], "disposition": "packaging_not_new_product"},
        {"legacy_ref": "term.business_metric", "canonical_refs": ["semantic.metric_definition", "semantic.metric_observation"], "disposition": "definition_observation_split"},
        {"legacy_ref": "term.kpi", "canonical_refs": ["semantic.kpi_target_benchmark", "semantic.metric_definition"], "disposition": "role_not_synonym"},
        {"legacy_ref": "term.formula", "canonical_refs": ["semantic.business_formula", "component.formula_engine"], "disposition": "definition_engine_split"},
        {"legacy_ref": "term.ai_semantic_layer", "canonical_refs": ["suite.semantic_layer", "component.optional_model_assistance"], "disposition": "remove_ambient_ai_prefix"},
        {"legacy_ref": "standard.apache_ossie", "canonical_refs": ["standard.ossie"], "disposition": "standard_not_product"},
    ]

    negatives = [
        ("measure_metric", "measure equals metric", "retain aggregation input and governed metric definition separately"),
        ("metric_kpi", "every metric is a KPI", "require an explicit KPI role and accountable objective"),
        ("target_observation", "target or benchmark is an observed value", "retain roles and authority separately"),
        ("definition_observation", "metric definition equals metric observation", "bind every observation to a definition edition and evaluation cut"),
        ("formula_binding", "formula expression is a bound definition", "resolve every free reference and exact edition"),
        ("binding_evaluation", "successful binding proves evaluated value", "require an evaluation occurrence and receipt"),
        ("null_zero", "null, absent, unknown, suppressed or error equals zero", "preserve distinct constructors"),
        ("empty_missing", "empty population equals all values missing", "apply explicit empty-input and missingness laws"),
        ("unit_meaning", "convertible units prove equivalent business meaning", "also require quantity kind, grain and semantic compatibility"),
        ("currency_unit", "currency valuation is a static unit conversion", "bind rate source, side, purpose, cutoff and correction"),
        ("event_valid_recording", "event, valid, recording and query time are interchangeable", "type each temporal role independently"),
        ("fresh_final", "freshness proves completeness or finality", "report each coordinate separately"),
        ("join_relation", "declared relation proves an authorized safe join", "require path, cardinality, authority and fanout proofs"),
        ("cardinality_estimate", "estimated cardinality proves actual contribution multiplicity", "bind cut-scoped evidence or refuse"),
        ("many_many", "many-to-many joins are automatically safe", "require allocation, compatible preaggregation, valid deduplication or refusal"),
        ("additive_decomposable", "additive equals decomposable", "declare both independently"),
        ("average_rollup", "averages can be averaged across groups", "merge sufficient sum/count state or recompute"),
        ("percent_rollup", "percentages can be summed or averaged", "reaggregate numerator and denominator under compatible grain"),
        ("holistic_merge", "every aggregate has finite sufficient merge state", "refuse unsupported holistic reaggregation"),
        ("semantic_sql", "semantic query equals SQL text", "retain semantic AST, bindings and lowering separately"),
        ("same_sql", "matching SQL proves same metric", "compare exact semantic identity and policy posture"),
        ("different_sql", "different SQL cannot be semantically equivalent", "permit reuse only with an equivalence proof"),
        ("materialized_truth", "materialization becomes source truth", "preserve definition and source authority"),
        ("cache_hit_current", "semantic cache hit proves freshness and finality", "validate cut, invalidation and finality evidence"),
        ("cache_policy", "equivalent values can be reused across access policies", "require access-equivalent projection proof"),
        ("metric_dashboard", "dashboard tile owns metric meaning", "presentation imports an editioned metric contract"),
        ("metric_query_engine", "query engine owns business metric meaning", "lower semantics into a replaceable engine"),
        ("semantic_ontology", "semantic layer replaces glossary or ontology", "import approved terms and formal concepts through ACLs"),
        ("definition_authority", "provider YAML becomes authoritative by parsing", "require owner approval and lifecycle transition"),
        ("schema_equivalence", "Ossie/schema validity proves semantic equivalence", "require typed directional compatibility and behavior tests"),
        ("provider_qualified", "official docs qualify a semantic implementation", "require exact conformance receipts"),
        ("one_portable", "one implementation proves portable semantics", "require two independent qualified implementations"),
        ("telemetry_business", "OpenMetrics or OTel metric is automatically a business metric", "bind explicit business definition and authority"),
        ("observation_fact", "metric observation is an immutable source fact", "retain derivation, correction and supersession"),
        ("uncertainty_drop", "aggregation may discard uncertainty", "propagate or explicitly refuse unsupported composition"),
        ("approx_exact", "approximate result is exact", "bind error profile, confidence and authorization"),
        ("recursive_formula", "recursive formula may execute without a fixed-point profile", "require monotonicity, convergence and finite budget"),
        ("vertical_threshold", "horizontal service owns industry thresholds and targets", "keep them in the vertical solution pack"),
        ("agent_definition", "agent proposal publishes a metric definition", "require deterministic validation and owner approval"),
        ("agent_query", "agent interpretation replaces typed semantic query", "compile an explicit typed query or refuse"),
        ("agent_authority", "generated text authorizes disclosure", "require deterministic policy and effect gates"),
        ("agent_core", "model or agent is required for formula correctness", "remove all extensions and preserve deterministic core behavior"),
        ("ai_prefix", "adding AI creates a new semantic-layer product", "model the exact optional capability without changing domain boundaries"),
    ]
    negative_tests = [{"test_id": f"negative.smf.{ident}", "prohibited_claim": prohibited, "expected_result": expected} for ident, prohibited, expected in negatives]
    semantic_gaps = [{"gap_id": f"gap.smf.{ident}", "product_ref": "product.semantic_metric_formula_service", "gap_class": "semantic_or_conformance", "statement": statement, "blocking": True, "closure_evidence": "Publish an exact owner, decidable profile or scoped refusal, executable conformance oracle and independent implementation evidence."} for ident, statement in SEMANTIC_GAPS]

    product = artifacts[0]
    product.update({
        "sovereign_question": "How can metric authors publish governed formula and metric editions and let consumers evaluate them consistently across grain, dimensions, time, units, uncertainty and providers?",
        "users": ["metric_author", "semantic_steward", "analyst", "application_developer"],
        "harmed_parties": ["decision_subject", "data_subject", "downstream_consumer", "finance_or_risk_owner"],
        "jobs": ["Author, review, publish, evaluate, observe, materialize, disclose, supersede and recall governed metric editions without transferring source, query or policy authority."],
        "outcomes": ["portable_metric_definition", "fanout_safe_evaluation", "time_and_unit_correct_result", "traceable_observation_and_disclosure"],
        "negative_mission": "Does not own source facts, glossary or ontology authority, physical query execution, BI presentation, data-use policy, industry thresholds or downstream decisions.",
        "lifecycle_states": ["draft", "typechecked", "binding_resolved", "review_pending", "approved", "published", "deprecated", "superseded", "recalled"],
        "commands": ["open_semantic_domain", "draft_formula", "typecheck_formula", "bind_definition", "submit_definition_review", "approve_definition", "publish_metric_edition", "evaluate_semantic_query", "append_metric_observation", "materialize_metric_cut", "request_metric_disclosure", "supersede_metric_edition", "recall_metric_edition"],
        "events": ["semantic_domain_opened", "formula_drafted", "formula_typechecked", "definition_bound", "definition_review_requested", "definition_approved", "metric_edition_published", "semantic_query_evaluated", "metric_observation_appended", "metric_cut_materialized", "metric_disclosure_requested", "metric_edition_superseded", "metric_edition_recalled"],
        "invariants": ["measure metric KPI target benchmark and observation remain distinct", "formula expression definition binding and evaluation remain distinct", "every free reference binds one exact owner and edition", "grain join time unit missingness uncertainty and policy are explicit", "publication approval evaluation observation materialization and disclosure are separate authorities"],
        "refusals": ["formula_syntax_invalid", "semantic_type_mismatch", "definition_binding_ambiguous", "grain_or_population_unbound", "fanout_safety_unproved", "summarizability_unproved", "calendar_or_unit_unbound", "policy_refused", "no_qualified_query_offer", "cache_equivalence_unproved", "publication_authority_missing", "disclosure_authority_missing"],
        "automation_modality": {"default": "DETERMINISTIC_CORE_ONLY", "postures": ["PROHIBITED", "OPTIONAL", "REQUIRED_BY_INTENT", "UNDETERMINED"], "law": "A model or agent may propose or explain typed semantic records but never owns metric meaning, approval, disclosure authority, effects or receipts.", "hard_work_law": "Automation never replaces vocabulary, semantic ownership, formula laws, lifecycle, evidence, conformance, qualification or domain acceptance."},
    })

    ddd_dossiers = [{
        "dossier_id": "ddd.smf.semantic_metric_formula_service",
        "product_ref": "product.semantic_metric_formula_service",
        "status": "candidate_not_ratified",
        "product_truth": {
            "sovereign_question": product["sovereign_question"],
            "users": product["users"],
            "harmed_parties": product["harmed_parties"],
            "jobs": product["jobs"],
            "measurable_outcomes": product["outcomes"],
            "negative_mission": product["negative_mission"],
        },
        "strategic_and_tactical_ddd": {
            "domain_vision_statement": "Own the governed lifecycle from a typed formula or metric draft to portable evaluation and evidence-linked observations without acquiring source, query, policy or decision authority.",
            "subdomain_classification": "core_horizontal_semantic_product",
            "bounded_context_boundary": {
                "inside": ["formula and metric editions", "semantic binding", "grain and join proof", "aggregation and summarizability", "calendar units missingness and uncertainty", "semantic query identity", "evaluation and observation evidence", "materialization equivalence", "definition supersession and recall"],
                "outside": ["source fact correction", "glossary and ontology approval", "physical query planning", "report and dashboard lifecycle", "data-use policy authorship", "industry targets and downstream decisions"],
            },
            "ubiquitous_language_policy": "Measure, metric, KPI, target, benchmark, formula, definition, binding, evaluation, observation, materialization and disclosure each have one non-interchangeable meaning; foreign homonyms cross named ACLs.",
            "context_map": [
                {"neighbor_ref": "neighbor.business_glossary", "relationship": "customer_supplier_acl", "translation": "import approved human terms without acquiring glossary authority"},
                {"neighbor_ref": "neighbor.ontology", "relationship": "published_language", "translation": "import formal concepts and mappings by exact edition"},
                {"neighbor_ref": "neighbor.source_truth", "relationship": "anti_corruption_layer", "translation": "bind immutable source occurrences and correction evidence"},
                {"neighbor_ref": "neighbor.query_execution", "relationship": "customer_supplier", "translation": "lower a typed semantic query to a qualified physical execution offer"},
                {"neighbor_ref": "neighbor.data_use_policy", "relationship": "conformist_at_effect_gate", "translation": "obtain purpose and disclosure decisions without self-authorization"},
                {"neighbor_ref": "neighbor.presentation", "relationship": "open_host_service", "translation": "publish versioned metric definitions observations and result receipts"},
                {"neighbor_ref": "neighbor.vertical_solution", "relationship": "customer_supplier", "translation": "import industry populations thresholds targets and acceptance rules"},
            ],
            "anti_corruption_layers": ["acl.glossary_term", "acl.ontology_concept", "acl.source_occurrence", "acl.physical_query", "acl.use_policy", "acl.presentation", "acl.vertical_metric_profile"],
            "published_language": ["MetricDefinitionEdition", "BoundFormula", "SemanticQuery", "MetricObservation", "MetricEvaluationReceipt", "MetricRecallNotice", "typed refusals"],
            "value_objects": ["MetricId", "MetricEdition", "FormulaAst", "SemanticType", "Grain", "Population", "DimensionSet", "JoinPath", "AggregationProfile", "CalendarEdition", "UnitExpression", "MissingnessProfile", "UncertaintyProfile", "DataCutRef", "PolicyDecisionRef"],
            "entities": ["SemanticDomain", "MetricDefinition", "FormulaDefinition", "DefinitionReview", "EvaluationOccurrence", "MetricObservation", "Materialization", "DisclosureOccurrence"],
            "aggregates": [
                {"root": "MetricDefinition", "members": ["formula", "bindings", "grain", "dimensions", "aggregation", "time", "units", "missingness", "uncertainty", "lifecycle"], "consistency": "one command advances one immutable metric-definition edition"},
                {"root": "EvaluationOccurrence", "members": ["semantic_query", "definition_editions", "data_cut", "provider_binding", "result_or_refusal", "receipt"], "consistency": "one occurrence binds an exact semantic and physical execution cut"},
                {"root": "MetricObservation", "members": ["value_or_error", "definition_ref", "evaluation_ref", "population", "grain", "time", "provenance", "correction_state"], "consistency": "append-only observation history with explicit correction supersession and recall"},
            ],
            "aggregate_roots": ["MetricDefinition", "EvaluationOccurrence", "MetricObservation"],
            "aggregate_invariants": product["invariants"],
            "commands": product["commands"],
            "domain_events": product["events"],
            "refusal_failure_catalog": product["refusals"],
            "domain_services": ["FormulaTypecheckingService", "SemanticBindingService", "SummarizabilityProofService", "FanoutProofService", "SemanticQueryCanonicalizationService", "CacheEquivalenceService", "CompatibilityDiffService"],
            "application_services": ["AuthorMetricUseCase", "ReviewAndPublishMetricUseCase", "EvaluateSemanticQueryUseCase", "RecordObservationUseCase", "MaterializeMetricUseCase", "RecallMetricUseCase"],
            "repositories": ["SemanticDomainRepository", "MetricDefinitionRepository", "EvaluationOccurrenceRepository", "MetricObservationRepository", "MaterializationRepository"],
            "factories": ["TypedFormulaFactory", "MetricDefinitionFactory", "SemanticQueryFactory", "MetricObservationFactory"],
            "specifications": ["PublicationReadinessSpecification", "BindingCompletenessSpecification", "SummarizabilitySpecification", "FanoutSafetySpecification", "EvaluationReadinessSpecification", "MaterializationReuseSpecification", "DisclosureReadinessSpecification"],
            "state_machine": {
                "metric_definition_states": product["lifecycle_states"],
                "observation_states": ["recorded", "corrected", "superseded", "recalled"],
                "transition_policy": "Only named commands satisfying aggregate invariants may emit the corresponding past-tense event; approval is not publication, evaluation, observation or disclosure.",
            },
            "policies_and_reactions": ["when a definition is published invalidate incompatible semantic caches", "when a metric edition is superseded preserve old observations under their bound edition", "when a metric is recalled propagate recall to materializations observations and disclosures", "when policy refuses disclosure retain evaluation evidence but emit no disclosure effect"],
            "sagas_and_process_managers": ["MetricPublicationProcess", "SemanticEvaluationProcess", "MetricMaterializationRefreshProcess", "MetricRecallPropagationProcess"],
            "read_models_and_projections": ["MetricCatalogView", "FormulaDependencyGraph", "CompatibilityDiffView", "EvaluationLineageView", "ObservationHistoryView", "MaterializationFreshnessView", "RecallImpactView"],
            "integration_event_policy": "Only minimized versioned publication supersession recall observation and disclosure events cross the boundary; internal proof and review events remain product-local.",
            "concurrency_and_idempotency": ["optimistic metric-edition compare-and-swap", "idempotency key per command and evaluation occurrence", "append-only observation identity", "single-winner publication per metric edition", "deduplicated recall propagation"],
            "time_model": ["definition validity time is distinct from recording time", "source event valid recording and query time are independent typed roles", "calendar and timezone editions are explicit", "observations carry evaluation and recording times", "supersession recall and finality horizons are explicit"],
            "event_storming_swimlanes": ["metric_author", "semantic_steward_or_approver", "consumer", "semantic_runtime", "query_provider", "policy_authority", "vertical_owner"],
            "nonfunctional_laws": ["deterministic parsing typing binding and canonicalization", "bounded evaluation memory time and result size", "cooperative cancellation and typed partial completion", "no hidden source writes or disclosure", "provider identity cannot change meaning", "every result receipt binds definitions query data cut provider policy and output digest", "removing model and agent extensions preserves the complete deterministic core"],
        },
    }]

    return {
        "contract_id": "contract.product_adjudication.semantic_metrics_formulas.v0_1_0",
        "edition": 1,
        "status": "evidence_backed_adjudicated_candidate_not_ratified",
        "scope": "Business formulas, semantic models, measures, metrics, dimensions, grains, populations, joins, aggregation, units, time, uncertainty, semantic query, observations, materialization, cache equivalence and disclosure.",
        "negative_scope": "Does not own source facts, glossary/ontology authority, physical query execution, BI presentation, data-use policy, vertical targets or ambient model/agent authority.",
        "artifact_kinds": kinds,
        "sources": sources,
        "artifacts": artifacts,
        "boundary_decisions": decisions,
        "ownership": ownership,
        "libraries": libraries,
        "requirements": requirements,
        "offers": offer_rows,
        "relations": relations,
        "crosswalks": crosswalks,
        "negative_tests": negative_tests,
        "binding_maps": binding_maps,
        "binding_gaps": [],
        "semantic_gaps": semantic_gaps,
        "ddd_dossiers": ddd_dossiers,
        "non_collapse_laws": [
            "measure != metric != KPI != target != benchmark != observation",
            "formula expression != formula definition != binding != evaluation",
            "null != absent != unknown != suppressed != not-applicable != error != zero",
            "entity relation != authorized join != fanout proof",
            "additivity != decomposability; aggregate result != sufficient merge state",
            "unit conversion != currency valuation; event time != valid time != recording time != query time",
            "freshness != completeness != validity != finality",
            "semantic query != SQL text; matching SQL != semantic cache equivalence",
            "metric definition and metric observation have different lifecycle and authority",
            "semantic metric service != glossary != ontology != query engine != BI presentation",
            "metric store is an overloaded architecture label, not a second product",
            "standard/schema acceptance != semantic equivalence != provider qualification",
            "optional model or agent output is a proposal, never metric meaning or effect authority",
            "removing all model/agent extensions preserves deterministic parsing, typing, binding, proof, policy, execution and receipts",
        ],
    }


def source_bytes() -> bytes:
    return (json.dumps(source(), ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode()


if __name__ == "__main__":
    SOURCE.write_bytes(source_bytes())
