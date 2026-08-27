#!/usr/bin/env python3
"""Build the evidence-backed BI, visualization, semantic-metric and formula slice."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
SEM = HERE.parent
REGISTRY = SEM.parents[1]
ATLAS = REGISTRY.parents[1]
AS_OF = "2026-08-27"
PRODUCTS = {"product.bi_reporting", "product.embedded_analytics", "product.semantic_metric_formula_service"}
AXES = ["semantic_object", "semantic_role", "identity_and_equality", "grain_and_cardinality",
        "state_and_change", "time", "order_and_topology", "partiality_and_uncertainty",
        "authority_and_trust", "effect_boundary", "representation", "composition_algebra",
        "compatibility_and_evolution", "resources_and_failure", "evidence_and_conformance",
        "privacy_security_safety"]
NEIGHBORS = {
    "library.cbv.cube_algebra", "library.cbv.pivot_algebra", "library.cbv.result_contracts",
    "library.cbv.layout_solver", "library.cbv.uncertainty_contracts",
    "library.cbv.interaction_reducer", "library.cbv.session_log",
    "library.cbv.client_cache_algebra", "library.cbv.content_versioning_algebra",
    "library.cbv.disclosure_model", "library.cbv.policy_projection", "library.cbv.query_gateway",
    "library.cbv.offline_store", "library.cbv.result_stream", "library.cbv.notification_dispatch",
    "library.qck.query-binding", "library.qck.query-types", "library.qck.relational-semantics",
    "library.qck.logical-plan-ir", "library.qck.function-contracts",
    "library.qck.query-equivalence-oracles", "library.qck.query-receipts",
    "library.pipeline.data_cut_algebra", "library.lpe.prov-statement-algebra",
    "library.lpe.provenance-assertion", "library.csp.quantity.quantity-core",
    "library.csp.quantity.unit-registry", "library.csp.quantity.ratio-rate",
    "library.csp.quantity.money-core", "library.csp.quantity.partial-information",
    "library.csp.quantity.uncertainty-propagation",
}


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def slug(value: str) -> str:
    return value.replace("_", "-").replace(".", "-").replace("/", "-")


def product_rows() -> list[dict[str, Any]]:
    return load_jsonl(SEM / "product_coordinate_binding_projection/subject-coordinate-binding-projections.jsonl")


def declared_product_libraries() -> set[str]:
    return {edge["concrete_library_ref"] for row in product_rows() if row["product_ref"] in PRODUCTS for edge in row["concrete_bindings"]}


LIBRARIES = sorted(declared_product_libraries() | NEIGHBORS)


# Each row deliberately re-bounds a live source record. The upstream universe is discovery input;
# its claim is not inherited. The source URL and metadata are replayed by exact registry ID.
SOURCE_SELECTION = [
    ("openformula", "source.smf.oasis.openformula14", "Defines editioned formula syntax, types, operators, functions and error semantics for interchange.", "Spreadsheet formula semantics do not define enterprise metrics, data binding, query execution or policy."),
    ("sdmx", "source.smf.sdmx.31", "Defines current statistical data/metadata exchange editions and registries.", "SDMX structures do not establish business ownership, provider support or analytical correctness."),
    ("sdmx-model", "source.smf.sdmx.im31", "Separates data structure definitions, dimensions, measures, attributes and representations.", "An information model does not prove summarizability or metric fitness."),
    ("vtl", "source.smf.sdmx.vtl21", "Defines typed validation and transformation expressions over statistical data.", "VTL is one language and does not own every formula, query or decision semantic."),
    ("rdf-cube", "source.smf.w3c.data_cube", "Defines datasets, observations, dimensions, attributes, measures, slices and structure definitions.", "RDF representation does not prove observation truth, hierarchy validity or aggregation safety."),
    ("prov", "source.smf.w3c.prov_dm", "Defines entity, activity, agent and derivation structures for provenance claims.", "Provenance is not correctness, authorization, lineage completeness or causal proof."),
    ("owl-time", "source.smf.w3c.owl_time", "Defines instants, intervals, temporal positions and reference systems.", "Generic time representation does not choose metric validity, recording, fiscal or query-time roles."),
    ("shacl", "source.smf.w3c.shacl", "Defines graph-shape constraints and validation results.", "Shape conformance is not semantic acceptance or business truth."),
    ("qudt", "source.smf.qudt.catalog", "Provides editioned quantities, units, dimensions and conversion metadata.", "Catalog membership does not prove a quantity mapping or conversion is applicable."),
    ("ucum", "source.smf.ucum.spec", "Defines machine-processable unit expressions and conversions.", "UCUM syntax does not own measurands, currency valuation or business rounding."),
    ("nist-si", "source.smf.nist.si", "Provides official SI usage and quantity/unit guidance.", "SI guidance does not define domain measures or exchange-rate valuation."),
    ("iso-time", "source.smf.iso.8601", "Defines editioned date/time representations.", "Representation does not select time zone, calendar, period boundary, validity or recording semantics."),
    ("currency", "source.smf.iso.4217", "Defines currency-code identifiers.", "A currency code does not supply an exchange-rate source, valuation time or rounding policy."),
    ("fx", "source.smf.ecb.fx", "Defines a bounded official methodology for euro reference exchange rates.", "One rate methodology is not a universal valuation authority or trading price."),
    ("gum", "source.smf.jcgm.gum100", "Defines model-based measurement uncertainty and propagation.", "Measurement uncertainty is not sampling uncertainty, visualization uncertainty or decision risk."),
    ("oms", "source.smf.ogc.oms", "Separates observations, observed properties, procedures, results, features of interest and samples.", "Observation structures do not make facts, metrics or interpretations true."),
    ("sql", "source.smf.iso.sql2023", "Provides the current SQL/Foundation language edition imported by semantic-query lowering.", "SQL text does not identify governed metric meaning or semantic cache equivalence."),
    ("gray-cube", "source.smf.paper.gray_cube", "Defines cube/grouping as multidimensional relational aggregation.", "Cube algebra does not define business dimensions, measures or valid roll-up."),
    ("summarizability-survey", "source.smf.paper.summarizability_survey", "Surveys structural, measure and hierarchy conditions for summarizability.", "Surveyed conditions still need domain-specific grain and hierarchy evidence."),
    ("summarizability-detect", "source.smf.paper.detect_summarizability", "Provides methods for detecting invalid OLAP summarization conditions.", "Detection is scoped to modeled assumptions and is not universal acceptance."),
    ("aggregate-views", "source.smf.paper.aggregate_views", "Defines conditions for rewriting aggregate queries using materialized views.", "A rewrite algorithm does not prove freshness, policy equivalence or provider qualification."),
    ("aggregation-consistency", "source.smf.paper.agg_consistency", "Documents semantic-layer aggregation consistency failure modes and protective transformations.", "A paper result does not establish complete coverage of every join, aggregate or provider."),
    ("metricflow", "source.smf.dbt.metricflow_semantics", "Documents one implementation's metric, entity, dimension, time and semantic-query model.", "Provider terminology and defaults are not universal semantic authority."),
    ("cube-joins", "source.smf.cube.joins", "Documents explicit relationship/join declarations in one semantic-layer provider.", "A declared relationship does not alone prove fanout-safe aggregation."),
    ("cube-preagg", "source.smf.cube.rollup_match", "Documents one provider's pre-aggregation matching and roll-up reuse.", "Provider matching does not prove universal semantic containment or policy equivalence."),
    ("looker-symmetric", "source.smf.looker.symmetric", "Documents one provider's symmetric-aggregate response to fanout.", "A provider algorithm cannot infer measure grain or every valid allocation rule."),
    ("otel-metrics", "source.smf.otel.metrics", "Defines metric streams, data points, temporality and aggregation in telemetry.", "Telemetry metric streams are not automatically business metrics or KPIs."),
    ("wcag", "source.cbv.w3c.wcag22", "Defines testable web-content accessibility success criteria including non-text alternatives and interaction.", "WCAG conformance does not prove equivalent analytical understanding for every user/task."),
    ("aria", "source.cbv.w3c.aria12", "Defines accessibility roles, states and properties for interactive content.", "ARIA metadata cannot repair incorrect semantics, interaction design or inaccessible task structure."),
    ("graphics-aria", "source.cbv.w3c.graphics_aria", "Defines roles for graphical documents and graphical objects.", "Graphics roles do not create equivalent data access or analytical navigation by themselves."),
    ("svg", "source.cbv.w3c.svg2", "Defines an interoperable vector-graphics representation.", "SVG geometry and paint do not own data, visual encoding, accessibility or report meaning."),
    ("vega", "source.cbv.vega.spec", "Defines a declarative visualization specification and dataflow/runtime surface.", "One grammar/provider does not establish perceptual effectiveness or business meaning."),
    ("vega-signals", "source.cbv.vega.signals", "Defines reactive named values that parameterize visualization state and interaction.", "Signals are implementation-level state, not report aggregates or source facts."),
    ("vegalite", "source.cbv.vegalite.paper", "Defines high-level visual encoding, view composition and interaction selections with compilation.", "A grammar can express invalid or misleading designs and does not qualify renderers."),
    ("nested-model", "source.cbv.paper.nested_model", "Separates domain problem, data/task abstraction, visual encoding/interaction and algorithm layers with layer-specific validation.", "The model guides validation but does not choose domain semantics or prove a design correct."),
    ("interaction", "source.cbv.paper.interaction_taxonomy", "Separates data/view specification, view manipulation and analysis process/provenance interactions.", "A taxonomy does not define every device, collaboration or business workflow."),
    ("draco", "source.cbv.paper.draco", "Represents visualization design knowledge as explicit constraints and preferences.", "Constraint satisfaction or ranking is not semantic truth or audience fitness."),
    ("hop", "source.cbv.paper.uncertainty", "Empirically compares uncertainty visualizations for bounded judgment tasks.", "A study result does not generalize to all audiences, tasks, distributions or decisions."),
    ("alt-text", "source.cbv.paper.alt_text", "Defines a four-level model for natural-language descriptions of visualizations.", "Descriptions do not automatically provide equivalent interactive or statistical access."),
    ("screenreader", "source.cbv.paper.rich_screenreader", "Studies richer screen-reader navigation and data access for visualizations.", "One prototype/study does not establish universal accessibility conformance."),
    ("web-access-audit", "source.cbv.paper.web_access_audit", "Empirically audits barriers faced by screen-reader users on web visualizations.", "Observed web samples do not enumerate every barrier or implementation."),
    ("chart-reader", "source.cbv.paper.chart_reader", "Co-designs accessible visualization experiences with screen-reader users.", "Co-design evidence remains task, participant and implementation scoped."),
    ("olli", "source.cbv.paper.olli", "Defines an extensible structure-first accessible representation for visualization specifications.", "Generated structure does not prove semantic correctness or equal comprehension."),
    ("risk-representation", "source.cbv.paper.risk_representation", "Shows that numerical and visual uncertainty representations can alter decision patterns.", "One study does not supply decision authority or a universal best encoding."),
    ("cldr", "source.cbv.unicode.cldr", "Provides versioned locale data for formatting languages, numbers, dates and currencies.", "Locale formatting does not alter underlying values or supply unit/currency semantics."),
    ("ecma-intl", "source.cbv.ecma.intl", "Defines ECMAScript internationalization APIs over locale data.", "An API/provider does not guarantee every locale, accessibility or semantic requirement."),
    ("alert-rules", "source.cbv.prometheus.alert_rules", "Documents deterministic alert-rule state evaluation over expressions.", "Telemetry alert semantics do not own business thresholds, recipients or notification delivery."),
    ("alertmanager", "source.cbv.prometheus.alertmanager", "Separates alert grouping/routing/silencing and delivery from rule evaluation.", "Delivery tooling does not authorize recipients or prove business action."),
    ("cloudevents", "source.cbv.cloudevents.spec", "Defines an interoperable event envelope for integration events.", "An event envelope does not define report, metric or subscription meaning."),
    ("http-cache", "source.cbv.ietf.cache", "Defines HTTP cache freshness, validation and invalidation semantics.", "HTTP freshness is not source finality, semantic equivalence or authorization equivalence."),
]


def source_catalog() -> dict[str, dict[str, Any]]:
    rows = load_jsonl(ATLAS / "universes/semantic_metrics_formulas/sources.jsonl")
    rows += load_jsonl(ATLAS / "universes/consumption_bi_visualization/sources.jsonl")
    return {row["source_id"]: row for row in rows}


def sources() -> list[dict[str, Any]]:
    catalog = source_catalog()
    result = []
    for alias, registry_ref, claim, limit in SOURCE_SELECTION:
        row = catalog[registry_ref]
        result.append({"source_id": f"source.bi.{alias}", "source_registry_ref": registry_ref,
                       "title": row["title"], "publisher": row["publisher"],
                       "year": row["publication_year"], "source_kind": row["source_kind"],
                       "url": row["url"], "supported_claim": claim, "authority_limit": limit,
                       "primary_or_official": row["source_kind"] != "community_spec",
                       "status": "INDEPENDENTLY_REBOUNDED_PRIMARY_OR_OFFICIAL"})
    return result


MODULE_ROWS = [
    ("business-concept-import", "Which approved business concept, owner, edition and allowed analytical role does a semantic definition import?", "published-language ACL", ["sdmx-model", "rdf-cube"], []),
    ("analytical-entity-role", "Which entity, event, fact, snapshot or observation role is projected for analysis without claiming business identity?", "role projection", ["rdf-cube", "oms"], ["business-concept-import"]),
    ("observation", "What phenomenon/property was observed, for which feature/population, by what procedure and with which result status?", "observation model", ["rdf-cube", "oms"], ["analytical-entity-role"]),
    ("population", "Which target/captured population and inclusion/exclusion predicate bound a metric or report?", "set/predicate contract", ["sdmx-model", "rdf-cube"], ["analytical-entity-role"]),
    ("grain", "What combination of dimensions identifies one fact, observation or metric value occurrence?", "grain/key algebra", ["rdf-cube", "summarizability-survey"], ["population"]),
    ("dimension", "Which analytical dimension, member domain, role and edition organize observations?", "dimension algebra", ["sdmx-model", "rdf-cube"], ["grain"]),
    ("member", "Which dimension-member identity, code list, label, validity and parentage apply?", "member identity/lifecycle", ["sdmx-model", "rdf-cube"], ["dimension"]),
    ("hierarchy", "Which level/hierarchy path, completeness, strictness, coverage and temporal validity permit navigation or roll-up?", "hierarchy/topology contract", ["summarizability-survey", "summarizability-detect"], ["member"]),
    ("measure", "Which phenomenon/property and quantity kind does a base measure represent at what grain and unit?", "measure definition", ["rdf-cube", "oms", "qudt"], ["observation", "grain"]),
    ("metric", "Which governed calculation over measures/populations/dimensions defines a metric edition?", "metric-definition aggregate", ["metricflow", "sdmx-model"], ["measure", "population"]),
    ("kpi-target-benchmark", "Which metric is designated as KPI, which target is desired, and which benchmark is an external/comparative reference?", "typed designation/reference", ["sdmx-model", "otel-metrics"], ["metric"]),
    ("formula-expression", "Which parsed expression tree denotes operations independently of definition identity and bindings?", "typed AST", ["openformula", "vtl"], []),
    ("formula-definition", "Which immutable formula edition, dependencies, variables, types and declared effects form a definition?", "definition aggregate", ["openformula", "vtl"], ["formula-expression"]),
    ("formula-binding", "How does every free reference resolve to one exact semantic owner/edition, grain, type, time and unit?", "total binding relation", ["openformula", "metricflow"], ["formula-definition", "metric"]),
    ("formula-evaluation", "Which bound formula, inputs, cut, budgets and provider produce value/error plus receipt?", "pure/effectful evaluation algebra", ["openformula", "vtl"], ["formula-binding"]),
    ("semantic-types", "Which nominal/structural types, quantity dimensions, units, scales, currencies and partiality states constrain values?", "semantic type system", ["openformula", "qudt", "ucum"], ["formula-expression"]),
    ("missingness", "How do null, absent, unknown, suppressed, not-applicable, empty population and zero propagate?", "partial-information algebra", ["openformula", "rdf-cube"], ["semantic-types"]),
    ("units", "Which quantity kind, dimension, unit edition and exact/rounded conversion preserve meaning?", "quantity/unit algebra", ["qudt", "ucum", "nist-si"], ["semantic-types"]),
    ("money-valuation", "Which currency, rate source, rate time, direction, market posture and rounding define valuation?", "money/valuation contract", ["currency", "fx"], ["units"]),
    ("ratio-rate", "Which numerator/denominator populations, units, zero-domain behavior and weighting define a ratio or rate?", "partial ratio algebra", ["openformula", "qudt"], ["measure", "missingness"]),
    ("calendar", "Which calendar, locale, week/fiscal rules, time zone and boundary editions define periods?", "calendar algebra", ["iso-time", "cldr"], ["semantic-types"]),
    ("bitemporal-cut", "Which event, valid, recording, publication, query and as-of times identify the evaluated data cut?", "bitemporal cut model", ["owl-time", "sdmx-model"], ["calendar"]),
    ("aggregation", "Which input collection, null/empty handling, ordering, exactness, sufficient state and merge law define an aggregate?", "aggregation algebra", ["gray-cube", "openformula"], ["grain", "missingness"]),
    ("additivity", "Across which dimensions and levels is a measure additive, semi-additive or non-additive?", "dimension-indexed property", ["summarizability-survey", "gray-cube"], ["aggregation", "hierarchy"]),
    ("decomposability", "Which sufficient state can be partitioned, merged and finalized without changing the aggregate?", "monoid/partial algebra", ["gray-cube", "aggregate-views"], ["aggregation"]),
    ("summarizability", "Which grain, hierarchy, population and aggregation conditions authorize roll-up?", "constraint/proof system", ["summarizability-survey", "summarizability-detect"], ["additivity", "decomposability"]),
    ("analytical-join", "Which declared entity relation may be used as an analytical join at what cardinality and validity?", "join-path contract", ["cube-joins", "metricflow"], ["grain", "dimension"]),
    ("fanout-proof", "How is source contribution multiplicity preserved across joins, allocation, preaggregation or deduplication?", "multiplicity proof", ["looker-symmetric", "aggregation-consistency"], ["analytical-join", "aggregation"]),
    ("semantic-model", "Which metric, measure, dimension, relation, formula and policy editions compose one published semantic model?", "versioned module graph", ["metricflow", "sdmx-model"], ["metric", "formula-binding", "fanout-proof"]),
    ("semantic-compatibility", "Which changes preserve reference, evaluation, observation and presentation compatibility?", "directional compatibility relation", ["sdmx", "openformula"], ["semantic-model"]),
    ("semantic-query", "Which measures, metrics, dimensions, filters, grouping, time, units, uncertainty and purpose define a semantic query?", "typed semantic-query algebra", ["metricflow", "rdf-cube"], ["semantic-model"]),
    ("query-canonicalization", "Which normalization preserves semantic-query identity without erasing editions, policy or partiality?", "canonicalization algebra", ["shacl", "sql"], ["semantic-query"]),
    ("query-lowering", "Which qualified query-engine contract lowers a semantic query with equivalence and residual evidence?", "compiler ACL", ["sql", "aggregate-views"], ["query-canonicalization", "summarizability"]),
    ("semantic-cache", "Which semantic query, definitions, cut, policy, uncertainty and disclosure posture identify reusable cached results?", "semantic equivalence relation", ["aggregate-views", "cube-preagg", "http-cache"], ["query-canonicalization", "bitemporal-cut"]),
    ("materialization", "Which covering query, sufficient state, refresh cut and legal reaggregation proof define a metric materialization?", "materialization identity", ["aggregate-views", "cube-preagg"], ["semantic-cache", "decomposability"]),
    ("metric-observation", "Which definition, evaluation, population, grain, time, value/error, uncertainty and correction state identify an observation?", "append-only observation", ["rdf-cube", "otel-metrics", "prov"], ["formula-evaluation", "bitemporal-cut"]),
    ("uncertainty", "Which measurement, sampling, model, computational or approximation uncertainty attaches to what result?", "typed uncertainty contract", ["gum", "risk-representation"], ["metric-observation"]),
    ("policy-disclosure", "Which purpose, audience, suppression, disclosure and authority decision permits which semantic result surface?", "external authority request", ["rdf-cube", "wcag"], ["semantic-query", "metric-observation"]),
    ("query-result", "Which schema, grain, multiplicity, order, cut, uncertainty, disclosure and receipt define a consumable result?", "result envelope", ["sql", "sdmx"], ["query-lowering", "policy-disclosure"]),
    ("presentation-artifact", "Which report/dashboard/widget/table/chart edition binds which semantic result and author intent?", "presentation aggregate", ["nested-model", "vegalite"], ["query-result"]),
    ("presentation-ir", "Which provider-neutral marks, channels, scales, guides, layouts and interactions form a presentation program?", "presentation IR", ["vega", "vegalite"], ["presentation-artifact"]),
    ("data-task-abstraction", "Which domain question is abstracted into which data and analytical tasks before encoding?", "task/data abstraction", ["nested-model", "interaction"], ["presentation-artifact"]),
    ("visual-encoding", "Which data fields/semantic roles map to which marks and visual channels under which constraints?", "visual encoding grammar", ["vegalite", "draco"], ["data-task-abstraction", "presentation-ir"]),
    ("scale-guide", "Which domain/range, transform, zero/baseline, clamp, tick, axis, legend and formatting semantics apply?", "scale/guide algebra", ["vega", "draco"], ["visual-encoding"]),
    ("layout-composition", "How do layer, facet, concatenate, repeat, responsive layout and multi-view coordination compose?", "view composition algebra", ["vegalite", "vega"], ["scale-guide"]),
    ("table-pivot", "Which header hierarchy, cell coordinates, totals, pivot operations, sort and selection define an analytical table?", "table/pivot algebra", ["rdf-cube", "gray-cube"], ["summarizability", "query-result"]),
    ("interaction-intent", "Which semantic action—filter, select, navigate, drill, annotate, compare or parameterize—is requested?", "semantic interaction command", ["interaction", "vegalite"], ["presentation-ir"]),
    ("presentation-state", "Which selection, focus, viewport, parameters, expansion, sort and disclosure state advance per interaction?", "total state reducer", ["vega-signals", "vegalite"], ["interaction-intent"]),
    ("interaction-history", "Which actor, artifact/query edition, prior state, command, result and evidence identify analysis history?", "session/provenance log", ["interaction", "prov"], ["presentation-state"]),
    ("dashboard", "Which widget/panel definitions, shared parameters, coordination and publication edition compose a dashboard?", "dashboard composition", ["vegalite", "interaction"], ["layout-composition", "interaction-history"]),
    ("report-lifecycle", "Which draft, review, approval, publication, suspension, supersession and retirement states govern reports?", "artifact lifecycle", ["nested-model", "prov"], ["presentation-artifact"]),
    ("report-snapshot", "Which immutable report/query/data-cut/policy/presentation editions and completeness posture form a snapshot?", "sealed snapshot", ["prov", "http-cache"], ["report-lifecycle", "query-result"]),
    ("alert-state", "Which metric condition, evaluation cut, pending/firing/resolved state and dedup identity define an analytical alert?", "alert state machine", ["alert-rules", "cloudevents"], ["metric-observation"]),
    ("subscription", "Which content/query, schedule, recipient, parameters, channel intent, policy and occurrence state define a subscription?", "subscription aggregate", ["alertmanager", "cloudevents"], ["report-snapshot", "policy-disclosure"]),
    ("notification-handoff", "How does alert/subscription evaluation issue delivery intent without owning routing, retry or acknowledgement?", "effect-intent/receipt boundary", ["alertmanager", "cloudevents"], ["alert-state", "subscription"]),
    ("export", "Which artifact/cut, format, loss, recipient, policy, encoding and delivery receipt define an export?", "export process", ["prov", "http-cache"], ["report-snapshot", "policy-disclosure"]),
    ("embedded-bridge", "Which host/guest identity, entitlement, context, sizing, navigation and event contract embeds analytics?", "host/guest protocol", ["aria", "cloudevents"], ["dashboard", "policy-disclosure"]),
    ("offline-cache", "Which encrypted artifact/result editions, authority lease, freshness and reconciliation rules permit offline use?", "offline replica contract", ["http-cache", "prov"], ["semantic-cache", "presentation-state"]),
    ("accessibility", "Which semantic structure, names, descriptions, navigation, focus, alternatives and conformance evidence provide access?", "accessibility semantics", ["wcag", "aria", "graphics-aria", "olli"], ["presentation-ir"]),
    ("localization", "Which locale, language, number/date/currency formats, bidi and label editions render without changing values?", "i18n formatting ACL", ["cldr", "ecma-intl"], ["units", "calendar"]),
    ("uncertainty-communication", "Which uncertainty object, audience/task and visual/textual representation disclose uncertainty without changing it?", "communication mapping", ["hop", "risk-representation"], ["uncertainty", "visual-encoding"]),
    ("accessible-equivalence", "Which structural table, description and interactive navigation evidence supports equivalent analytical access?", "human/task conformance relation", ["alt-text", "screenreader", "web-access-audit", "chart-reader", "olli"], ["accessibility", "table-pivot"]),
    ("rendering", "Which qualified renderer maps presentation IR to SVG/canvas/HTML or native output with declared degradation?", "provider adapter", ["svg", "vega"], ["presentation-ir", "accessibility"]),
    ("decision-handoff", "Which question, finding, uncertainty, evidence, limitations and authority request leave analytics without authorizing action?", "non-authoritative handoff", ["nested-model", "risk-representation"], ["metric-observation", "interaction-history"]),
    ("conformance-evidence", "Which formula, aggregation, fanout, query, rendering, accessibility, interaction and replay oracles support each bounded claim?", "evidence envelope", ["shacl", "wcag", "draco"], ["semantic-model", "presentation-ir"]),
]


def modules() -> list[dict[str, Any]]:
    return [{"module_id": f"module.bi.{mid}", "owned_question": question, "formalism": formalism,
             "source_refs": [f"source.bi.{ref}" for ref in refs],
             "dependency_refs": [f"module.bi.{ref}" for ref in deps],
             "research_status": "EVIDENCE_BACKED_UNRATIFIED",
             "authority_limit": "The module proposes bounded BI/metric/visualization semantics; it does not ratify an owner, select a contract, qualify a provider or close a canonical gap."}
            for mid, question, formalism, refs, deps in MODULE_ROWS]


LAW_ROWS = [
    ("term-member", "A business term or ontology concept is not a dimension member."),
    ("entity-role", "An analytical entity role is not business identity authority."),
    ("observation-fact", "Observation, event, fact, record and snapshot must not collapse."),
    ("row-grain", "A storage row is not analytical grain."),
    ("population-filter", "A population definition is not an incidental query filter."),
    ("dimension-column", "A dimension is not merely a physical column."),
    ("member-label", "A dimension member is not its display label."),
    ("hierarchy-sort", "A hierarchy is not generic ordering or a convenient UI tree."),
    ("measure-metric", "Measure, metric, KPI, target, benchmark and observation remain distinct."),
    ("metric-tile", "A governed metric is not a dashboard tile or chart series."),
    ("target-value", "A target or threshold is not an observed value or forecast."),
    ("benchmark-authority", "A benchmark does not authorize acceptance or action."),
    ("expression-definition", "Formula text/AST is not a formula definition, binding or evaluation."),
    ("definition-binding", "A formula definition with free references is not executable until exact binding succeeds."),
    ("binding-evaluation", "Binding success is not evaluation success or result correctness."),
    ("provider-function", "Equal function names across providers do not imply equal semantics."),
    ("pure-effectful", "Pure formula evaluation must not hide clock, registry, data, randomness, policy or network effects."),
    ("null-zero", "Null, absent, unknown, suppressed, not-applicable, empty and zero remain distinct."),
    ("empty-all-missing", "Empty population and nonempty population with all values missing must not collapse."),
    ("unit-label", "A unit label is not an editioned unit identity or conversion proof."),
    ("unit-currency", "Unit conversion and currency valuation remain distinct."),
    ("currency-code-rate", "A currency code does not supply rate source, time, direction or rounding."),
    ("ratio-average", "Ratio of sums, sum of ratios and average of ratios are generally distinct."),
    ("zero-denominator", "A zero denominator must not silently become zero, infinity or missing."),
    ("event-valid-record-query", "Event, valid, recording, publication and query time remain distinct."),
    ("calendar-timezone", "Calendar/fiscal period and time zone are independently editioned."),
    ("fresh-final", "Freshness, completeness, validity and finality remain distinct."),
    ("correction-rewrite", "A correction/supersession must not rewrite historical observation identity."),
    ("additive-decomposable", "Additivity and decomposability remain independent properties."),
    ("aggregate-state-result", "Aggregate result and sufficient merge state are not interchangeable."),
    ("rollup-sum", "Roll-up is not universally SUM."),
    ("summarizable-valid", "Structural query validity does not prove semantic summarizability."),
    ("relation-join", "Entity relation existence does not authorize an analytical join."),
    ("cardinality-rowcount", "Join cardinality semantics are not row-count estimates."),
    ("many-many-safe", "Many-to-many joins are not fanout-safe without allocation, compatible preaggregation, valid deduplication or refusal."),
    ("dedup-universal", "Deduplication is not a universal remedy for fanout."),
    ("semantic-query-sql", "A semantic query is not SQL text."),
    ("semantic-cache-sql", "Matching SQL text is neither necessary nor sufficient for semantic cache equivalence."),
    ("materialization-cache", "Materialization identity, cache entry and metric observation remain distinct."),
    ("query-result-presentation", "A query result is not presentation state or a report artifact."),
    ("data-task-encoding", "Domain question, data/task abstraction, visual encoding and rendering algorithm are distinct validation layers."),
    ("field-channel-meaning", "Mapping a field to a visual channel cannot define metric meaning."),
    ("chart-truth", "A syntactically valid chart is not evidence of truthful or effective communication."),
    ("scale-data", "Scale transform and display range do not mutate underlying semantic values."),
    ("axis-unit", "An axis label does not establish unit, grain, population or time semantics."),
    ("color-category", "Color assignment is not category identity and color alone cannot carry essential meaning."),
    ("layout-grouping", "Visual proximity or layout does not create semantic grouping."),
    ("table-dataset", "An analytical table model is not the source dataset or query result identity."),
    ("pivot-aggregation", "Pivoting is not automatically valid aggregation or summarization."),
    ("interaction-source", "Interaction state does not mutate source facts or metric definitions."),
    ("selection-filter", "Visual selection, semantic filter and source predicate remain distinct."),
    ("drill-navigation", "Drill navigation does not prove hierarchy validity or authorization."),
    ("session-result", "A view session and its interaction history are not a query result."),
    ("dashboard-report", "Dashboard, report, widget, chart, table and snapshot remain distinct artifacts."),
    ("live-snapshot", "A live view and immutable report snapshot cannot share a completeness claim."),
    ("approval-publication", "Approval, publication, disclosure, export and delivery are distinct authorities/effects."),
    ("alert-notification", "Alert condition evaluation and notification delivery remain distinct."),
    ("pending-firing", "Alert pending, firing, resolved, silenced and acknowledged states must not collapse."),
    ("subscription-delivery", "A subscription schedule is not a delivery attempt, acknowledgement or business outcome."),
    ("export-share", "Exported bytes do not imply governed, continuing or revocable access."),
    ("encoding-delivery", "Export encoding and delivery are separate failure/evidence boundaries."),
    ("embedded-host", "An embedded guest surface does not inherit host identity, policy or business authority implicitly."),
    ("offline-finality", "Offline cache freshness does not establish source finality or entitlement continuation."),
    ("accessibility-style", "Accessibility semantics are not styling, color theme or alternate text alone."),
    ("wcag-task", "WCAG conformance does not by itself prove equivalent analytical task performance."),
    ("description-data", "A chart description is not the underlying data, interaction model or evidence."),
    ("localization-value", "Localization and bidi formatting must not change semantic values."),
    ("uncertainty-decoration", "Uncertainty is not an optional decorative channel."),
    ("uncertainty-risk", "Measurement/statistical uncertainty, visual perception and decision risk remain distinct."),
    ("rendering-semantics", "Renderer success does not prove semantic, perceptual or accessibility conformance."),
    ("fallback-equivalence", "A fallback is acceptable only with proven semantic and task equivalence or explicit degradation receipt."),
    ("provenance-correctness", "Provenance and replay evidence do not prove metric correctness or decision fitness."),
    ("finding-decision", "An analytical finding, dashboard insight or alert is not authority to decide or act."),
    ("ai-authority", "AI or agents may propose formulas/charts/narratives but cannot infer hidden grain, choose defaults, waive evidence or authorize effects."),
]


def laws() -> list[dict[str, Any]]:
    return [{"law_id": f"law.bi.non-collapse.{lid}", "statement": statement,
             "status": "EVIDENCE_BACKED_UNRATIFIED", "canonical_gaps_closed": 0}
            for lid, statement in LAW_ROWS]


METHOD_GROUPS = {
    "semantic_modeling": ["business-concept import", "analytical entity-role projection", "fact/event/observation modeling", "population definition", "grain declaration", "dimension modeling", "member/code-list binding", "hierarchy modeling", "measure definition", "metric definition", "KPI designation", "target definition", "benchmark binding", "semantic model publication", "compatibility diff", "recall propagation"],
    "formula": ["formula parsing", "AST canonicalization", "semantic typechecking", "free-variable analysis", "definition editioning", "reference binding", "effect analysis", "unit checking", "missingness checking", "calendar checking", "formula evaluation", "partial-function refusal", "fixed-point evaluation", "evaluation receipt construction"],
    "quantity_time_uncertainty": ["unit conversion", "quantity-dimension checking", "ratio/rate evaluation", "currency valuation", "calendar bucketing", "fiscal-period projection", "timezone conversion", "bitemporal as-of evaluation", "uncertainty propagation", "approximation-error composition", "correction/supersession", "finality appraisal"],
    "aggregation_and_join": ["sum/count/min/max", "average/weighted average", "distinct aggregation", "quantile/holistic aggregation", "algebraic sufficient-state aggregation", "ordered aggregation", "additivity checking", "decomposability checking", "summarizability checking", "join-path selection", "fanout analysis", "allocation weighting", "grain-compatible preaggregation", "stable-key deduplication", "aggregation consistency testing"],
    "semantic_query": ["semantic query construction", "query canonicalization", "policy projection", "physical query lowering", "equivalence checking", "residual validation", "materialization containment", "legal reaggregation", "semantic cache lookup", "materialization refresh", "metric observation append", "observation correction", "disclosure evaluation", "result receipt binding"],
    "presentation": ["data/task abstraction", "visual mark selection", "channel encoding", "scale construction", "axis/legend construction", "layout solving", "layering", "faceting", "concatenation", "repeat/small multiples", "responsive layout", "analytical table construction", "pivot/unpivot", "subtotal rendering", "uncertainty encoding", "annotation and explanation", "presentation IR lowering", "renderer adaptation"],
    "interaction": ["semantic filtering", "selection", "highlighting", "parameter binding", "sort", "pan/zoom", "drill-down/roll-up", "details-on-demand", "brushing and linking", "cross-filtering", "focus navigation", "view coordination", "interaction reduction", "session history", "undo/redo", "shareable view state"],
    "report_dashboard": ["report authoring", "dashboard composition", "widget binding", "review", "approval", "publication", "suspension", "supersession", "retirement", "snapshot sealing", "snapshot replay", "subscription creation", "schedule evaluation", "alert evaluation", "alert deduplication", "notification-intent emission"],
    "delivery_embedding": ["export planning", "CSV/table encoding", "vector/raster/document encoding", "loss accounting", "export delivery", "embedded host handshake", "guest entitlement binding", "host/guest event exchange", "offline cache fill", "offline lease validation", "reconciliation after reconnect"],
    "accessibility_i18n": ["semantic structure projection", "accessible naming", "multi-level description", "screen-reader navigation", "keyboard/focus navigation", "non-color alternatives", "contrast validation", "reflow/zoom validation", "accessible table projection", "localization", "number/date/currency formatting", "bidi handling", "equivalent-task evaluation"],
    "assurance": ["formula fixture testing", "property-based aggregation testing", "fanout negative twins", "query differential testing", "materialization metamorphic testing", "visual constraint checking", "perceptual task study", "accessibility conformance testing", "assistive-technology testing", "interaction model testing", "snapshot replay", "export round-trip testing", "independent renderer differential testing"],
}


def methods() -> list[dict[str, Any]]:
    return [{"method_type_id": f"method.bi.{slug(group)}.{slug(name)}", "method_group": group,
             "name": name,
             "selection_law": "Selection requires explicit semantic intent, audience/task, grain/time/unit/uncertainty, authority, representation, effect, resource and conformance decisions; method-family membership is not substitutability.",
             "status": "TAXONOMY_CANDIDATE_UNRATIFIED"}
            for group, names in METHOD_GROUPS.items() for name in names]


EXPERT_ROWS = [
    ("gray", "Jim Gray", ["gray-cube"], ["Model grouping/cube operations explicitly.", "Keep aggregation algebra separate from measure meaning and summarizability."]),
    ("lenz", "Hans-Joachim Lenz", ["summarizability-survey", "summarizability-detect"], ["Treat summarizability as a formal precondition, not a UI convenience.", "Make hierarchy and aggregation compatibility testable."]),
    ("shoshani", "Arie Shoshani", ["summarizability-survey"], ["Bind statistical objects to normalized dimensional context.", "Refuse roll-up when context is incomplete."]),
    ("munzner", "Tamara Munzner", ["nested-model"], ["Separate domain problem, data/task abstraction, encoding/interaction and algorithm layers.", "Validate at the layer where the claim is made."]),
    ("heer", "Jeffrey Heer", ["vegalite", "interaction"], ["Make visualization and interaction declarative and composable.", "Capture analysis history and provenance, not only final pixels."]),
    ("shneiderman", "Ben Shneiderman", ["interaction"], ["Treat interaction as data/view specification, manipulation and analysis process.", "Design for iterative human inquiry without transferring decision authority."]),
    ("satyanarayan", "Arvind Satyanarayan", ["vegalite"], ["Compile high-level interaction selections into lower-level dataflow explicitly.", "Keep specification, compiled IR and renderer occurrence distinct."]),
    ("moritz", "Dominik Moritz", ["vegalite", "draco"], ["Represent visualization design spaces and constraints as machine-readable structures.", "Preference ranking does not replace semantic or human validation."]),
    ("wongsuphasawat", "Kanit Wongsuphasawat", ["vegalite"], ["Factor multi-view composition and interaction into enumerable semantics.", "Do not hide shared scale/dataflow choices."]),
    ("mackinlay", "Jock Mackinlay", ["vegalite", "draco"], ["Match visual channels to data types and tasks.", "Expressiveness and effectiveness are separate constraints."]),
    ("hullman", "Jessica Hullman", ["hop", "risk-representation"], ["Model uncertainty communication as a task/audience problem.", "Visual representation can change judgment and therefore needs empirical evidence."]),
    ("bennett", "Cynthia Bennett", ["screenreader", "chart-reader"], ["Co-design accessible analytical interactions with disabled users.", "Accessibility cannot be reduced to generated alt text."]),
    ("zong", "Jonathan Zong", ["olli", "web-access-audit"], ["Expose visualization structure for nonvisual navigation.", "Test real task paths with assistive technology and users."]),
    ("lundgard", "Alan Lundgard", ["alt-text"], ["Structure descriptions by chart construction and analytical content levels.", "Descriptions supplement but do not replace interactive data access."]),
    ("lee", "Bongshin Lee", ["interaction", "risk-representation"], ["Treat interaction and communication as evidence-sensitive design surfaces.", "A visualization is part of an analytical process, not merely output styling."]),
    ("sdmx-community", "SDMX Technical Working Group", ["sdmx", "sdmx-model"], ["Publish dimensions, measures, attributes, code lists and structures as editioned contracts.", "Separate exchange conformance from statistical fitness."]),
    ("w3c-cube", "W3C RDF Data Cube working group", ["rdf-cube"], ["Keep observation, dimension, measure and attribute roles explicit.", "Representation choice must not erase structural metadata."]),
    ("oasis-formula", "OASIS OpenFormula technical committee", ["openformula"], ["Specify formula syntax and evaluation behavior portably.", "Formula portability still requires explicit semantic binding and provider conformance."]),
    ("metricflow", "MetricFlow maintainers", ["metricflow"], ["Make metrics, entities, dimensions and time spines explicit in semantic query planning.", "Provider models are evidence for implementation seams, not universal authority."]),
    ("cube-team", "Cube maintainers", ["cube-joins", "cube-preagg"], ["Expose joins and pre-aggregation matching as explicit model/runtime contracts.", "Require independent fanout and containment proof."]),
    ("looker-team", "Looker semantic-model team", ["looker-symmetric"], ["Treat fanout-safe aggregation as a first-class compiler concern.", "Symmetric aggregates do not infer missing grain or business rules."]),
    ("w3c-accessibility", "W3C Accessibility Guidelines Working Group", ["wcag", "aria", "graphics-aria"], ["Represent perceivability, operability, structure and interaction as conformance obligations.", "Standards compliance remains distinct from equivalent analytical comprehension."]),
    ("unicode", "Unicode CLDR technical committee", ["cldr", "ecma-intl"], ["Version locale data and formatting rules.", "Formatting must not mutate semantic values or supply business units."]),
    ("prometheus", "Prometheus and Alertmanager maintainers", ["alert-rules", "alertmanager"], ["Separate alert evaluation state from routing, silencing and notification delivery.", "Telemetry thresholds are not universal business policies."]),
]


def experts() -> list[dict[str, Any]]:
    return [{"expert_id": f"expert.bi.{eid}", "name": name,
             "source_refs": [f"source.bi.{ref}" for ref in refs],
             "lessons_for_composable_platform": lessons,
             "authority_limit": "Expert work constrains candidate semantics; the expert is not the SAN owner, acceptance authority or provider qualifier.",
             "status": "RESEARCHED_PROFILE"} for eid, name, refs, lessons in EXPERT_ROWS]


INNOVATION_ROWS = [
    ("accessible-description-levels", 2021, "A four-level model made visualization description scope and analytical content more explicit.", ["alt-text"]),
    ("rich-screenreader", 2022, "Research moved accessible visualization beyond alt text toward structured navigation and richer data access.", ["screenreader"]),
    ("web-access-audit", 2022, "Empirical audits exposed widespread screen-reader barriers in real web visualizations.", ["web-access-audit"]),
    ("olli", 2022, "Olli demonstrated an extensible structure-first accessible representation derived from visualization specifications.", ["olli"]),
    ("aggregation-consistency", 2023, "Research made aggregation consistency failures in semantic layers and corrective rewrites explicit.", ["aggregation-consistency"]),
    ("chart-reader", 2023, "Chart Reader used co-design with screen-reader users to expand interactive accessible chart experiences.", ["chart-reader"]),
    ("risk-representation", 2023, "Studies showed visual and numerical uncertainty representations can produce different decision patterns.", ["risk-representation"]),
    ("wcag22", 2024, "WCAG 2.2 added and consolidated testable accessibility obligations for modern interactive content.", ["wcag"]),
    ("sdmx31", 2025, "SDMX 3.1 updated the editioned information/registry surface for statistical structures and exchange.", ["sdmx", "sdmx-model"]),
    ("openformula14", 2025, "ODF/OpenFormula 1.4 refreshed open, editioned formula interchange semantics.", ["openformula"]),
    ("semantic-layer-interchange", 2025, "Provider semantic models increasingly expose metrics, entities, dimensions, joins and pre-aggregations as inspectable contracts.", ["metricflow", "cube-joins", "cube-preagg"]),
    ("semantic-cache-proof", 2025, "Modern semantic runtimes increasingly separate semantic-query identity and roll-up containment from matching SQL text.", ["cube-preagg", "aggregate-views"]),
    ("accessibility-equivalence", 2025, "The research frontier increasingly evaluates task-equivalent nonvisual navigation rather than alt-text presence alone.", ["chart-reader", "olli", "wcag"]),
    ("deterministic-core", 2026, "Current formula, visualization and accessibility standards preserve deterministic contract surfaces independent of optional generative assistance.", ["openformula", "vega", "wcag"]),
]


def innovations() -> list[dict[str, Any]]:
    return [{"innovation_id": f"innovation.bi.{iid}", "year": year, "summary": summary,
             "source_refs": [f"source.bi.{ref}" for ref in refs], "ai_or_llm_dependency": False,
             "status": "EVIDENCE_BACKED_BOUNDED_INNOVATION"} for iid, year, summary, refs in INNOVATION_ROWS]


AXIS_QUESTIONS = {
    "semantic_object": "Which concept, population, grain, dimension, measure, metric, formula, query, result, presentation, session, report, alert, subscription, export and receipt objects exist?",
    "semantic_role": "Which object is definition, binding, observation, target, evidence, policy request, visual encoding, interaction state, effect intent or receipt?",
    "identity_and_equality": "What identifies definitions, observations, semantic queries, cache entries, views, reports, dashboards, sessions, snapshots and deliveries; which equivalence applies?",
    "grain_and_cardinality": "What fact/observation/cell/result/widget/audience grain and zero/one/many relationships apply, including join fanout?",
    "state_and_change": "Which draft/review/publish/evaluate/observe/correct/recall/view/interact/snapshot/alert/export/retire transitions are legal?",
    "time": "Which event, valid, recording, publication, query, calendar, schedule, cache, alert, session and delivery times apply?",
    "order_and_topology": "Which formula/model dependencies, dimension hierarchies, view layouts, interaction graphs, result/table orders and delivery routes apply?",
    "partiality_and_uncertainty": "How do missing/suppressed/undefined, empty populations, approximate values, uncertainty, stale/incomplete cuts, degraded renderings and partial deliveries propagate?",
    "authority_and_trust": "Who owns business meaning, semantic definitions, approval, source truth, query execution, policy, publication, disclosure, recipients, decision and action?",
    "effect_boundary": "How are pure parsing/typing/proof/presentation reduction separated from query I/O, materialization, rendering, notification, export and business effects?",
    "representation": "Which formula AST, semantic model/query, SQL/Substrait, result, presentation IR, SVG/HTML/table, report/export and accessibility representations are used at what loss?",
    "composition_algebra": "How do definitions, units, time, aggregation, fanout, queries, results, encodings, interactions, reports, alerts and effects compose and refuse?",
    "compatibility_and_evolution": "Which definition, formula, dimension, hierarchy, provider, query, visual, interaction, accessibility, report and export changes preserve compatibility?",
    "resources_and_failure": "Which parse/proof/query/result/render/interaction/cache/export/delivery budgets and total failures apply?",
    "evidence_and_conformance": "Which fixtures, properties, negative twins, differential engines/renderers, human-task studies, accessibility tests and replay receipts support each claim?",
    "privacy_security_safety": "How are metric/query/result confidentiality, inference, suppression, embedding, cache, telemetry, export, misleading encodings and unauthorized decisions controlled?",
}


VACANCIES = [
    ("library.smf.metric-definition-contract", "Own measure/metric/KPI/target/benchmark distinctions and immutable metric-edition identity."),
    ("library.smf.analytical-grain-population", "Own population predicates, fact/observation grain and dimension-key completeness independently of storage rows."),
    ("library.smf.semantic-join-path", "Own analytical relation paths, role binding, cardinality and validity before fanout proof."),
    ("library.smf.metric-observation-receipt", "Own exact definition/evaluation/cut/value-or-error/uncertainty/correction evidence for observations."),
    ("library.cbv.visualization-task-abstraction", "Own domain-question to data/task abstraction without metric or renderer ownership."),
    ("library.cbv.scale-guide-contract", "Own scale, baseline, domain/range, axis, legend and formatting semantics independently of marks."),
    ("library.cbv.interaction-history-provenance", "Own actor/artifact/query/state/command/result history while importing provenance authority."),
    ("library.cbv.dashboard-report-artifact-identity", "Own dashboard/report/widget/snapshot identity and containment without rendering or query ownership."),
    ("library.cbv.accessibility-equivalence-evidence", "Own task/audience/assistive-technology evidence for equivalent analytical access."),
    ("library.cbv.uncertainty-communication", "Own typed uncertainty-to-visual/text mapping and task-specific communication evidence."),
    ("library.cbv.embedded-entitlement-contract", "Own explicit host/guest identity, entitlement, context and event boundaries for embedding."),
    ("library.cbv.report-authoring-lifecycle", "Own draft/review/approval/publication/suspension/supersession/retirement transitions and evidence."),
]


def binding_modules(ref: str) -> list[str]:
    suffix = ref.rsplit(".", 1)[-1].replace("_", "-")
    mids = {"conformance-evidence"}
    rules = [
        (("formula-parser", "ast-canonicalizer"), ["formula-expression", "formula-definition"]),
        (("semantic-type-checker",), ["semantic-types", "formula-binding"]),
        (("binding-resolver",), ["formula-binding"]), (("formula-runtime",), ["formula-evaluation"]),
        (("dimension-algebra",), ["dimension", "member", "hierarchy"]),
        (("aggregation-algebra",), ["aggregation", "additivity", "decomposability"]),
        (("summarizability-checker",), ["summarizability"]), (("fanout-analyzer",), ["analytical-join", "fanout-proof"]),
        (("calendar-algebra",), ["calendar"]), (("bitemporal-algebra",), ["bitemporal-cut"]),
        (("missingness-algebra", "partial-information"), ["missingness"]),
        (("uncertainty-algebra", "uncertainty-propagation"), ["uncertainty"]),
        (("unit-conversion", "unit-registry", "quantity-core"), ["semantic-types", "units"]),
        (("exchange-rate", "money-core"), ["money-valuation"]), (("ratio-rate",), ["ratio-rate"]),
        (("semantic-registry",), ["semantic-model", "semantic-compatibility"]),
        (("compatibility-diff",), ["semantic-compatibility"]),
        (("semantic-query-canonicalizer",), ["semantic-query", "query-canonicalization"]),
        (("semantic-query-gateway",), ["semantic-query", "query-lowering"]),
        (("cache-equivalence",), ["semantic-cache"]), (("materialization-store",), ["materialization"]),
        (("observation-ledger",), ["metric-observation"]), (("policy-gateway", "disclosure-gateway"), ["policy-disclosure"]),
        (("semantic-query-types",), ["semantic-query"]), (("cube-algebra",), ["aggregation", "summarizability"]),
        (("pivot-algebra", "table-model"), ["table-pivot"]), (("presentation-ir",), ["presentation-artifact", "presentation-ir"]),
        (("visual-encoding",), ["visual-encoding", "scale-guide"]), (("layout-solver",), ["layout-composition"]),
        (("interaction-reducer",), ["interaction-intent", "presentation-state"]), (("session-log",), ["interaction-history"]),
        (("dashboard-runtime",), ["dashboard", "rendering"]), (("renderer-adapter",), ["rendering"]),
        (("report-snapshot",), ["report-lifecycle", "report-snapshot"]), (("alert-state",), ["alert-state"]),
        (("subscription-runner",), ["subscription"]), (("notification-dispatch",), ["notification-handoff"]),
        (("export-plan", "export-encoder", "export-delivery"), ["export"]), (("embedded-bridge",), ["embedded-bridge"]),
        (("offline-store",), ["offline-cache"]), (("accessibility-semantics",), ["accessibility", "accessible-equivalence"]),
        (("i18n-format",), ["localization"]), (("uncertainty-contracts",), ["uncertainty-communication"]),
        (("disclosure-model", "policy-projection"), ["policy-disclosure"]), (("content-versioning",), ["report-lifecycle"]),
        (("client-cache",), ["semantic-cache", "offline-cache"]), (("result-contracts",), ["query-result"]),
        (("result-stream",), ["query-result"]), (("query-gateway",), ["query-lowering"]),
        (("query-binding", "query-types", "relational-semantics", "logical-plan", "function-contracts", "query-equivalence"), ["query-lowering"]),
        (("query-receipts",), ["query-result", "conformance-evidence"]), (("data-cut",), ["bitemporal-cut"]),
        (("prov-statement", "provenance-assertion"), ["metric-observation", "interaction-history"]),
    ]
    for needles, add in rules:
        if any(needle in suffix for needle in needles):
            mids.update(add)
    return sorted(f"module.bi.{mid}" for mid in mids)


def boundary_findings(consumers: dict[str, set[str]]) -> list[dict[str, Any]]:
    direct = declared_product_libraries()
    rows = [
        {"finding_id": "finding.bi.metric-product.v1", "library_refs": sorted(ref for ref in direct if ref.startswith("library.smf.")), "current_product_refs": ["product.semantic_metric_formula_service"], "candidate_disposition": "SEMANTIC_METRIC_SERVICE_OWNS_GOVERNED_DEFINITION_BINDING_EVALUATION_AND_OBSERVATION_NOT_BUSINESS_SOURCE_QUERY_PRESENTATION_OR_DECISION_AUTHORITY", "reason": "The 24 SMF libraries cohere around governed semantic definition and evaluation, while source truth, query execution, presentation, vertical targets and effects cross ACLs.", "owner_decision": "UNRATIFIED"},
        {"finding_id": "finding.bi.reporting-product.v1", "library_refs": sorted(ref for ref in direct if ref.startswith("library.cbv.") and "embedded_bridge" not in ref), "current_product_refs": ["product.bi_reporting"], "candidate_disposition": "BI_REPORTING_OWNS_REPORT_DASHBOARD_VIEW_SNAPSHOT_ALERT_SUBSCRIPTION_AND_EXPORT_LIFECYCLES_NOT_METRIC_QUERY_POLICY_OR_NOTIFICATION_AUTHORITY", "reason": "Report artifacts and interaction/publication lifecycles form a product boundary; imported metrics and results retain their owners.", "owner_decision": "UNRATIFIED"},
        {"finding_id": "finding.bi.embedded-product.v1", "library_refs": sorted(ref for ref in direct if ref.startswith("library.cbv.")), "current_product_refs": ["product.embedded_analytics"], "candidate_disposition": "EMBEDDED_ANALYTICS_OWNS_HOST_GUEST_DELIVERY_AND_RUNTIME_CONTRACT_NOT_REPORT_METRIC_QUERY_OR_HOST_BUSINESS_LOGIC", "reason": "Host integration, entitlement projection and embedded runtime are independently adoptable but reuse presentation semantics.", "owner_decision": "UNRATIFIED"},
        {"finding_id": "finding.bi.query-foundation.v1", "library_refs": sorted(ref for ref in LIBRARIES if ref.startswith("library.qck.") or ref == "library.pipeline.data_cut_algebra"), "current_product_refs": [], "candidate_disposition": "IMPORT_QUERY_SEMANTICS_AND_DATA_CUTS_WITHOUT_REOWNING_PHYSICAL_EXECUTION", "reason": "Semantic queries and presentations require exact result semantics, but query planning/execution remain the query-service boundary.", "owner_decision": "UNRATIFIED"},
        {"finding_id": "finding.bi.quantity-foundation.v1", "library_refs": sorted(ref for ref in LIBRARIES if ref.startswith("library.csp.quantity.")), "current_product_refs": [], "candidate_disposition": "IMPORT_QUANTITY_UNIT_MONEY_RATIO_PARTIALITY_AND_UNCERTAINTY_ALGEBRAS", "reason": "Metric semantics specialize shared mathematical carriers and must not redefine quantities or conversions ad hoc.", "owner_decision": "UNRATIFIED"},
        {"finding_id": "finding.bi.visualization-library.v1", "library_refs": sorted(ref for ref in LIBRARIES if ref.startswith("library.cbv.") and ref not in direct), "current_product_refs": [], "candidate_disposition": "RETAIN_VISUAL_INTERACTION_RESULT_AND_DELIVERY_LIBRARIES_AS_COMPOSABLE_CONTRACTS_NOT_EXTRA_PRODUCTS", "reason": "Cube, pivot, interaction, layout, cache, result, offline and notification seams are reusable libraries/runtimes unless independent product economics and lifecycle evidence emerges.", "owner_decision": "UNRATIFIED"},
        {"finding_id": "finding.bi.alert-delivery.v1", "library_refs": ["library.cbv.alert_state", "library.cbv.notification_dispatch", "library.cbv.subscription_runner"], "current_product_refs": ["product.bi_reporting"], "candidate_disposition": "ALERT_EVALUATION_AND_SUBSCRIPTION_BELONG_TO_REPORTING_WHILE_NOTIFICATION_DELIVERY_REMAINS_IMPORTED_RUNTIME", "reason": "Condition state and scheduled content are product semantics; channel routing/retry/acknowledgement remain a delivery provider contract.", "owner_decision": "UNRATIFIED"},
        {"finding_id": "finding.bi.decision-seam.v1", "library_refs": [], "current_product_refs": sorted(PRODUCTS), "candidate_disposition": "ANALYTICAL_PRESENTATION_AND_METRIC_FINDINGS_STOP_BEFORE_DECISION_AND_EFFECT_AUTHORITY", "reason": "Reports, alerts and observations publish bounded evidence and authority requests; vertical/application owners decide and act.", "owner_decision": "UNRATIFIED"},
    ]
    rows.extend({"finding_id": f"finding.bi.vacancy.{slug(ref)}.v1", "library_refs": [], "proposed_library_ref": ref,
                 "current_product_refs": [], "candidate_disposition": "NEW_LIBRARY_BOUNDARY_CANDIDATE_UNRATIFIED",
                 "reason": reason, "owner_decision": "UNRATIFIED"} for ref, reason in VACANCIES)
    return rows


def build() -> dict[str, Any]:
    ss, ms, ls, method_rows, expert_rows, innovation_rows = sources(), modules(), laws(), methods(), experts(), innovations()
    contributions = {row["library_id"]: row for row in load_jsonl(REGISTRY / "library-contributions.jsonl")}
    assert set(LIBRARIES) <= contributions.keys()
    coord = {row["library_ref"]: row for row in load_jsonl(SEM / "library_coordinate_binding_projection/library-coordinate-binding-dockets.jsonl")}
    exact = {row["library_ref"]: row for row in load_jsonl(SEM / "p5_exact_contract_adjudication/exact-contract-dockets.jsonl")}
    consumers = {ref: set() for ref in LIBRARIES}; subjects = {ref: set() for ref in LIBRARIES}
    for row in product_rows():
        for edge in row["concrete_bindings"]:
            ref = edge["concrete_library_ref"]
            if ref in consumers:
                consumers[ref].add(row["product_ref"]); subjects[ref].add(row["subject_ref"])
    targeted = {(row["axis"], row["library_ref"]): row for row in load_jsonl(SEM / "targeted_evidence_cluster_adjudication/member-adjudication-occurrences.jsonl")}
    module_by_id = {row["module_id"]: row for row in ms}
    bindings, axes = [], []
    direct = declared_product_libraries()
    for ref in LIBRARIES:
        module_refs = binding_modules(ref)
        evidence_refs = sorted({source for module_ref in module_refs for source in module_by_id[module_ref]["source_refs"]})
        exact_row, coord_row = exact.get(ref), coord.get(ref); routed = bool(exact_row and coord_row)
        bindings.append({"record_kind": "bi_visualization_metrics_library_semantic_binding_candidate",
                         "binding_id": f"binding.bi-semantic-slice.{slug(ref)}.v1", "library_ref": ref,
                         "library_name": contributions[ref]["name"], "semantic_module_refs": module_refs,
                         "evidence_refs": evidence_refs,
                         "exact_contract_docket_ref": exact_row["docket_id"] if exact_row else None,
                         "coordinate_binding_docket_ref": coord_row["binding_docket_id"] if coord_row else None,
                         "downstream_contract_route": "ROUTED" if routed else "MISSING_P5_AND_COORDINATE_DOCKET_TYPED_VACANCY",
                         "downstream_subject_refs": sorted(subjects[ref]), "downstream_product_refs": sorted(consumers[ref]),
                         "boundary_disposition_candidate": "RETAIN_DECLARED_PRODUCT_DEPENDENCY_WITH_NARROW_OWNER" if ref in direct else "RETAIN_FORMALISM_OR_ACL_NEIGHBOR_WITH_EXPLICIT_OWNER_SEAM",
                         "compiler_binding": "REFUSED",
                         "refusal_reasons": ([] if routed else ["DOWNSTREAM_CONTRACT_ROUTE_MISSING"]) + ["OWNER_RATIFICATION_MISSING", "MEMBER_AXIS_APPLICABILITY_UNRATIFIED", "EXACT_CONTRACT_UNSELECTED", "IMPLEMENTATIONS_UNQUALIFIED"],
                         "completion_claim": False})
        for axis in AXES:
            target = targeted.get((axis, ref))
            axes.append({"record_kind": "bi_visualization_metrics_library_axis_decision_candidate",
                         "decision_candidate_id": f"decision-candidate.bi-axis.{slug(ref)}.{axis.replace('_', '-')}.v1",
                         "library_ref": ref, "axis": axis, "semantic_module_refs": module_refs,
                         "coordinate_question": AXIS_QUESTIONS[axis], "applicability_candidate": "REQUIRED_EXPLICIT_PROFILE",
                         "evidence_refs": evidence_refs, "targeted_member_adjudication_occurrence_ref": target["occurrence_id"] if target else None,
                         "coordinate_answers": [], "member_applicability": "PROPOSED_OWNER_REVIEW_REQUIRED",
                         "owner_decision": "UNRATIFIED", "status": "EVIDENCE_BACKED_DECISION_QUESTION_NOT_ANSWER",
                         "canonical_gaps_closed": 0, "completion_claim": False})
    findings = boundary_findings(consumers)
    context = {"record_kind": "bounded_context_candidate", "context_id": "context.bi-visualization-metrics-semantic-slice.v1", "as_of": AS_OF,
               "vision": "How can governed measures, metrics and formulas be evaluated into evidence-bound observations and composed into accessible interactive reports, dashboards and embedded surfaces without collapsing semantic meaning into SQL, visual encoding, provider behavior, publication, notification or business decision authority?",
               "inside": ["analytical fact/observation/population/grain/dimension/measure/metric semantics", "formula AST, definition, binding, evaluation, types, units, time, missingness and uncertainty", "aggregation, decomposability, summarizability, analytical joins and fanout proofs", "semantic model/query, lowering ACL, cache/materialization and observation evidence", "presentation artifacts/IR, visual encoding, scale, layout, table/pivot and interaction state", "dashboard/report/snapshot/alert/subscription/export/embedded/offline lifecycles", "accessibility, localization and uncertainty communication"],
               "outside": ["business glossary/ontology approval", "source fact correction and master identity", "physical query planning/execution", "data-use policy authorship and identity authority", "notification channel delivery implementation", "vertical target/threshold ownership", "business judgment, decision and action", "LLM or agent authority"],
               "neighbors": [{"context_ref": "context.business-glossary", "relationship": "anti_corruption_layer"}, {"context_ref": "context.query-olap-warehouse-semantic-slice", "relationship": "customer_supplier"}, {"context_ref": "context.statistical-inference-semantic-slice", "relationship": "conditional_customer_supplier"}, {"context_ref": "context.data-use-policy", "relationship": "conformist_at_authority_gate"}, {"context_ref": "context.notification-delivery", "relationship": "open_host_service"}, {"context_ref": "context.decision-effect-authority", "relationship": "anti_corruption_layer"}],
               "published_language": ["MetricDefinitionEdition", "BoundFormula", "SemanticQuery", "MetricObservation", "MetricEvaluationReceipt", "PresentationDefinitionEdition", "PresentationIr", "ViewSession", "ReportSnapshot", "AlertOccurrence", "Subscription", "ExportIntent", "EmbeddedContext", "AccessibilityEvidence"],
               "ratification": "WITHHELD", "completion_claim": False}
    summary = {"program_id": "program.bi-visualization-metrics-semantic-slice.v1", "as_of": AS_OF,
               "primary_or_official_sources": len(ss), "semantic_modules": len(ms), "non_collapse_laws": len(ls),
               "method_types": len(method_rows), "expert_learning_profiles": len(expert_rows), "recent_non_llm_innovations": len(innovation_rows),
               "bound_libraries": len(bindings), "declared_product_libraries": len(direct), "formalism_and_acl_neighbor_libraries": len(NEIGHBORS),
               "candidate_new_library_vacancies": len(VACANCIES), "libraries_without_declared_product_consumer": sum(not consumers[ref] for ref in LIBRARIES),
               "missing_downstream_contract_routes": sum(row["downstream_contract_route"].startswith("MISSING") for row in bindings),
               "library_axis_decision_candidates": len(axes), "product_capability_boundary_findings": len(findings),
               "owner_decisions": 0, "exact_contracts_selected": 0, "qualified_implementations": 0,
               "canonical_gaps_closed": 0, "completion_claim": False}
    return {"context": context, "sources": ss, "modules": ms, "laws": ls, "methods": method_rows,
            "experts": expert_rows, "innovations": innovation_rows, "libraries": bindings,
            "axes": axes, "findings": findings, "summary": summary}


def outputs() -> dict[str, str]:
    built = build()
    files = {"bounded-context.json": json.dumps(built["context"], ensure_ascii=False, sort_keys=True, indent=2) + "\n",
             "primary-sources.jsonl": "".join(canonical(r) + "\n" for r in built["sources"]),
             "semantic-modules.jsonl": "".join(canonical(r) + "\n" for r in built["modules"]),
             "non-collapse-laws.jsonl": "".join(canonical(r) + "\n" for r in built["laws"]),
             "bi-method-taxonomy.jsonl": "".join(canonical(r) + "\n" for r in built["methods"]),
             "expert-learning-profiles.jsonl": "".join(canonical(r) + "\n" for r in built["experts"]),
             "innovation-records.jsonl": "".join(canonical(r) + "\n" for r in built["innovations"]),
             "library-semantic-bindings.jsonl": "".join(canonical(r) + "\n" for r in built["libraries"]),
             "library-axis-decision-candidates.jsonl": "".join(canonical(r) + "\n" for r in built["axes"]),
             "product-capability-boundary-findings.jsonl": "".join(canonical(r) + "\n" for r in built["findings"]),
             "summary.json": json.dumps(built["summary"], ensure_ascii=False, sort_keys=True, indent=2) + "\n"}
    claims = {name: {"bytes": len(value.encode()), "sha256": hashlib.sha256(value.encode()).hexdigest()} for name, value in files.items()}
    files["manifest.json"] = json.dumps({"manifest_id": "manifest.bi-visualization-metrics-semantic-slice.v1", "as_of": AS_OF, "files": claims, "completion_claim": False}, sort_keys=True, indent=2) + "\n"
    return files


def main() -> int:
    for name, value in outputs().items(): (HERE / name).write_text(value)
    s = build()["summary"]
    print(f"BUILD PASS BI/visualization/metrics slice: {s['semantic_modules']} modules, {s['method_types']} methods, {s['bound_libraries']} libraries and {s['library_axis_decision_candidates']} unresolved axis decisions")
    return 0


if __name__ == "__main__": raise SystemExit(main())
