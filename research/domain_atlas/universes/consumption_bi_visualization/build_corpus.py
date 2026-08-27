#!/usr/bin/env python3
"""Generate the candidate consumption, BI and visualization universe.

This is a research registry for an intent compiler.  It is deliberately provider-neutral,
open-world and split into semantic/presentation/runtime ownership layers.  Generated records are
compact enough for review, while the validator enforces the distinctions that prevent unsafe
compiler shortcuts.
"""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
SCHEMA = ROOT / "schema"
EDITION = 1
ACCESSED = "2026-08-25"
PREFIX = "cbv"


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


# Normative standards, first-party protocol/implementation specifications, and peer-reviewed
# research.  Each source is authoritative only for the scope recorded below; inclusion is never a
# universal conformance claim.
SOURCE_ROWS = [
    ("w3c.wcag22", "Web Content Accessibility Guidelines (WCAG) 2.2", "W3C", "standard", "https://www.w3.org/TR/WCAG22/", 2024, ["accessibility", "perceivable", "operable"]),
    ("w3c.aria12", "Accessible Rich Internet Applications (WAI-ARIA) 1.2", "W3C", "standard", "https://www.w3.org/TR/wai-aria-1.2/", 2023, ["accessibility_semantics", "interaction"]),
    ("w3c.graphics_aria", "WAI-ARIA Graphics Module", "W3C", "standard", "https://www.w3.org/TR/graphics-aria-1.0/", 2018, ["graphics_semantics", "navigation"]),
    ("w3c.graphics_aam", "Graphics Accessibility API Mappings", "W3C", "official_spec", "https://www.w3.org/TR/graphics-aam-1.0/", 2018, ["accessibility_mapping", "graphics"]),
    ("w3c.aria_apg", "ARIA Authoring Practices Guide", "W3C", "official_spec", "https://www.w3.org/WAI/ARIA/apg/", 2026, ["keyboard", "widgets", "focus"]),
    ("w3c.html", "HTML Living Standard", "WHATWG", "standard", "https://html.spec.whatwg.org/", 2026, ["document", "semantics", "forms"]),
    ("w3c.svg2", "Scalable Vector Graphics (SVG) 2", "W3C", "standard", "https://www.w3.org/TR/SVG2/", 2018, ["graphics", "vector", "document"]),
    ("w3c.css_color4", "CSS Color Module Level 4", "W3C", "standard", "https://www.w3.org/TR/css-color-4/", 2022, ["color", "gamut", "contrast"]),
    ("w3c.media_queries5", "Media Queries Level 5", "W3C", "official_spec", "https://www.w3.org/TR/mediaqueries-5/", 2021, ["user_preferences", "responsive", "accessibility"]),
    ("w3c.pointer_events3", "Pointer Events Level 3", "W3C", "official_spec", "https://www.w3.org/TR/pointerevents3/", 2025, ["interaction", "pointer", "input"]),
    ("w3c.service_workers", "Service Workers", "W3C", "official_spec", "https://www.w3.org/TR/service-workers/", 2025, ["offline", "cache", "network"]),
    ("w3c.app_manifest", "Web Application Manifest", "W3C", "official_spec", "https://www.w3.org/TR/appmanifest/", 2026, ["mobile", "installability", "launch"]),
    ("w3c.indexeddb3", "Indexed Database API 3.0", "W3C", "official_spec", "https://www.w3.org/TR/IndexedDB-3/", 2025, ["offline", "client_storage", "transactions"]),
    ("w3c.web_annotation", "Web Annotation Data Model", "W3C", "standard", "https://www.w3.org/TR/annotation-model/", 2017, ["annotation", "targeting", "collaboration"]),
    ("w3c.prov_o", "PROV-O: The PROV Ontology", "W3C", "standard", "https://www.w3.org/TR/prov-o/", 2013, ["provenance", "entity", "activity"]),
    ("w3c.prov_dm", "PROV-DM: The PROV Data Model", "W3C", "standard", "https://www.w3.org/TR/prov-dm/", 2013, ["provenance", "derivation", "responsibility"]),
    ("w3c.csvw", "Model for Tabular Data and Metadata on the Web", "W3C", "standard", "https://www.w3.org/TR/tabular-data-model/", 2015, ["csv", "metadata", "localization"]),
    ("w3c.dcat3", "Data Catalog Vocabulary (DCAT) Version 3", "W3C", "standard", "https://www.w3.org/TR/vocab-dcat-3/", 2024, ["catalog", "distribution", "data_service"]),
    ("w3c.dqv", "Data on the Web Best Practices: Data Quality Vocabulary", "W3C", "standard", "https://www.w3.org/TR/vocab-dqv/", 2016, ["quality", "measurement", "annotation"]),
    ("w3c.data_cube", "The RDF Data Cube Vocabulary", "W3C", "standard", "https://www.w3.org/TR/vocab-data-cube/", 2014, ["cube", "dimension", "measure"]),
    ("w3c.activitystreams2", "Activity Streams 2.0", "W3C", "standard", "https://www.w3.org/TR/activitystreams-core/", 2017, ["activity", "sharing", "collaboration"]),
    ("w3c.web_share", "Web Share API", "W3C", "official_spec", "https://www.w3.org/TR/web-share/", 2023, ["sharing", "client_integration"]),
    ("vega.spec", "Vega Specification", "Vega Project", "official_spec", "https://vega.github.io/vega/docs/specification/", 2026, ["visual_grammar", "reactive_dataflow"]),
    ("vega.signals", "Vega Signals", "Vega Project", "official_spec", "https://vega.github.io/vega/docs/signals/", 2026, ["signals", "interaction_state"]),
    ("vega.events", "Vega Event Streams", "Vega Project", "official_spec", "https://vega.github.io/vega/docs/event-streams/", 2026, ["events", "interaction"]),
    ("vega.scales", "Vega Scales", "Vega Project", "official_spec", "https://vega.github.io/vega/docs/scales/", 2026, ["scale", "encoding", "guide"]),
    ("vegalite.spec", "Vega-Lite Specification", "Vega-Lite Project", "official_spec", "https://vega.github.io/vega-lite/docs/spec.html", 2026, ["visual_grammar", "composition", "encoding"]),
    ("vegalite.selection", "Vega-Lite Selection Parameters", "Vega-Lite Project", "official_spec", "https://vega.github.io/vega-lite/docs/selection.html", 2026, ["selection", "interaction", "predicate"]),
    ("vegalite.paper", "Vega-Lite: A Grammar of Interactive Graphics", "IEEE TVCG", "paper", "https://idl.cs.washington.edu/papers/vega-lite/", 2017, ["visual_grammar", "compiler", "interaction"]),
    ("observable.plot", "Observable Plot documentation", "Observable", "official_docs", "https://observablehq.com/plot/", 2026, ["visualization", "marks", "transforms"]),
    ("observable.runtime", "Observable Runtime", "Observable", "official_implementation", "https://github.com/observablehq/runtime", 2026, ["reactive_runtime", "dataflow", "notebook"]),
    ("observable.framework", "Observable Framework documentation", "Observable", "official_docs", "https://observablehq.com/framework/", 2026, ["static_site", "data_loader", "dashboard"]),
    ("jupyter.nbformat", "The Notebook file format", "Project Jupyter", "official_spec", "https://nbformat.readthedocs.io/en/latest/format_description.html", 2026, ["notebook_document", "cells", "outputs"]),
    ("jupyter.messaging", "Jupyter Messaging Protocol", "Project Jupyter", "official_spec", "https://jupyter-client.readthedocs.io/en/latest/messaging.html", 2026, ["kernel_protocol", "messages", "execution"]),
    ("jupyter.kernels", "Making kernels for Jupyter", "Project Jupyter", "official_docs", "https://jupyter-client.readthedocs.io/en/latest/kernels.html", 2026, ["kernel", "lifecycle", "execution"]),
    ("jupyter.kernelspec", "Kernel specs", "Project Jupyter", "official_spec", "https://jupyter-client.readthedocs.io/en/latest/kernels.html#kernel-specs", 2026, ["kernel_identity", "launch", "environment"]),
    ("jupyter.widgets", "Jupyter Widgets protocol", "Project Jupyter", "official_spec", "https://ipywidgets.readthedocs.io/en/latest/examples/Widget%20Custom.html#Comms", 2026, ["widget_state", "comm", "interaction"]),
    ("jupyter.security", "Security in Jupyter notebooks", "Project Jupyter", "official_docs", "https://jupyter-notebook.readthedocs.io/en/stable/security.html", 2026, ["notebook_trust", "output_security"]),
    ("arrow.columnar", "Apache Arrow Columnar Format", "Apache Software Foundation", "official_spec", "https://arrow.apache.org/docs/format/Columnar.html", 2026, ["result_schema", "columnar_interchange"]),
    ("arrow.flight", "Apache Arrow Flight RPC", "Apache Software Foundation", "official_spec", "https://arrow.apache.org/docs/format/Flight.html", 2026, ["analytical_api", "result_stream"]),
    ("arrow.flight_sql", "Apache Arrow Flight SQL", "Apache Software Foundation", "official_spec", "https://arrow.apache.org/docs/format/FlightSql.html", 2026, ["sql", "metadata", "result_stream"]),
    ("arrow.adbc", "Arrow Database Connectivity specification", "Apache Software Foundation", "official_spec", "https://arrow.apache.org/adbc/current/format/specification.html", 2026, ["query_api", "driver", "result"]),
    ("substrait.spec", "Substrait Specification", "Substrait Project", "official_spec", "https://substrait.io/spec/specification/", 2026, ["query_ir", "types", "relations"]),
    ("iso.sql", "ISO/IEC 9075 Database languages SQL", "ISO/IEC", "standard", "https://www.iso.org/standard/76583.html", 2023, ["sql", "query_semantics"]),
    ("microsoft.mdx", "Multidimensional Expressions (MDX) Reference", "Microsoft", "official_docs", "https://learn.microsoft.com/en-us/analysis-services/mdx/mdx-language-reference-mdx", 2025, ["olap", "cube_query", "calculation"]),
    ("microsoft.xmla", "XML for Analysis protocol specification", "Microsoft", "official_spec", "https://learn.microsoft.com/en-us/openspecs/sql_server_protocols/ms-xmla/", 2024, ["olap_protocol", "discover", "execute"]),
    ("sdmx.standards", "SDMX 3.1 Technical Specifications", "SDMX", "standard", "https://sdmx.org/standards-2/", 2025, ["statistics", "information_model", "dissemination"]),
    ("sdmx.rest", "SDMX REST API specification", "SDMX Technical Working Group", "official_spec", "https://github.com/sdmx-twg/sdmx-rest", 2026, ["statistical_query", "api", "metadata"]),
    ("sdmx.json", "SDMX-JSON specification", "SDMX Technical Working Group", "official_spec", "https://github.com/sdmx-twg/sdmx-json", 2026, ["statistics", "json", "visualization"]),
    ("sdmx.csv", "SDMX-CSV specification", "SDMX Technical Working Group", "official_spec", "https://github.com/sdmx-twg/sdmx-csv", 2026, ["statistics", "csv", "exchange"]),
    ("ogc.maps", "OGC API - Maps - Part 1: Core", "Open Geospatial Consortium", "standard", "https://docs.ogc.org/is/20-058/20-058.html", 2024, ["map", "portrayal", "style"]),
    ("ogc.tiles", "OGC API - Tiles - Part 1: Core", "Open Geospatial Consortium", "standard", "https://docs.ogc.org/is/20-057/20-057.html", 2022, ["tiles", "map", "metadata"]),
    ("ogc.styles", "OGC API - Styles - Part 1: Core", "Open Geospatial Consortium", "standard", "https://docs.ogc.org/is/20-009/20-009.html", 2022, ["style", "portrayal", "resource"]),
    ("ogc.features", "OGC API - Features - Part 1: Core", "Open Geospatial Consortium", "standard", "https://docs.ogc.org/is/17-069r4/17-069r4.html", 2019, ["features", "query", "geospatial"]),
    ("prometheus.alert_rules", "Prometheus alerting rules", "Prometheus", "official_docs", "https://prometheus.io/docs/prometheus/latest/configuration/alerting_rules/", 2026, ["alert_rule", "evaluation", "state"]),
    ("prometheus.alertmanager", "Prometheus Alertmanager overview", "Prometheus", "official_docs", "https://prometheus.io/docs/alerting/latest/overview/", 2026, ["notification", "routing", "inhibition"]),
    ("prometheus.notifications", "Alertmanager notification template reference", "Prometheus", "official_docs", "https://prometheus.io/docs/alerting/latest/notifications/", 2026, ["notification", "template", "delivery"]),
    ("cloudevents.spec", "CloudEvents Specification", "Cloud Native Computing Foundation", "standard", "https://github.com/cloudevents/spec/blob/main/cloudevents/spec.md", 2024, ["event", "delivery", "interoperability"]),
    ("ietf.http", "RFC 9110: HTTP Semantics", "IETF", "standard", "https://www.rfc-editor.org/rfc/rfc9110.html", 2022, ["http", "validators", "content_negotiation"]),
    ("ietf.cache", "RFC 9111: HTTP Caching", "IETF", "standard", "https://www.rfc-editor.org/rfc/rfc9111.html", 2022, ["cache", "freshness", "revalidation"]),
    ("ietf.content_disposition", "RFC 6266: Content-Disposition in HTTP", "IETF", "standard", "https://www.rfc-editor.org/rfc/rfc6266.html", 2011, ["download", "filename", "export"]),
    ("ietf.bcp47", "RFC 5646: Tags for Identifying Languages", "IETF", "standard", "https://www.rfc-editor.org/rfc/rfc5646.html", 2009, ["language_tag", "localization"]),
    ("ietf.csv", "RFC 4180: Common Format and MIME Type for CSV Files", "IETF", "standard", "https://www.rfc-editor.org/rfc/rfc4180.html", 2005, ["csv", "export"]),
    ("ietf.problem", "RFC 9457: Problem Details for HTTP APIs", "IETF", "standard", "https://www.rfc-editor.org/rfc/rfc9457.html", 2023, ["api_error", "refusal", "diagnostics"]),
    ("unicode.cldr", "Unicode Common Locale Data Repository", "Unicode Consortium", "standard", "https://cldr.unicode.org/", 2026, ["locale_data", "formatting", "plural"]),
    ("unicode.uts35", "Unicode Technical Standard #35: LDML", "Unicode Consortium", "standard", "https://www.unicode.org/reports/tr35/", 2026, ["locale", "date_time", "number"]),
    ("unicode.bidi", "Unicode Standard Annex #9: Bidirectional Algorithm", "Unicode Consortium", "standard", "https://www.unicode.org/reports/tr9/", 2026, ["bidi", "text", "layout"]),
    ("unicode.linebreak", "Unicode Standard Annex #14: Line Breaking Algorithm", "Unicode Consortium", "standard", "https://www.unicode.org/reports/tr14/", 2026, ["line_break", "text", "layout"]),
    ("unicode.collation", "Unicode Technical Standard #10: Collation Algorithm", "Unicode Consortium", "standard", "https://www.unicode.org/reports/tr10/", 2026, ["collation", "sorting", "locale"]),
    ("ecma.intl", "ECMA-402 ECMAScript Internationalization API", "Ecma International", "standard", "https://402.ecma-international.org/", 2026, ["formatting", "locale", "time_zone"]),
    ("openapi.spec", "OpenAPI Specification 3.1", "OpenAPI Initiative", "standard", "https://spec.openapis.org/oas/v3.1.1.html", 2024, ["analytical_api", "schema", "security"]),
    ("jsonschema.spec", "JSON Schema Draft 2020-12", "JSON Schema", "standard", "https://json-schema.org/draft/2020-12/json-schema-core", 2022, ["schema", "validation", "contract"]),
    ("rocrate.spec", "RO-Crate Metadata Specification 1.1", "Research Object Crate", "official_spec", "https://www.researchobject.org/ro-crate/1.1/", 2022, ["reproducibility", "package", "provenance"]),
    ("otel.traces", "OpenTelemetry Trace semantic conventions", "OpenTelemetry", "official_spec", "https://opentelemetry.io/docs/specs/semconv/general/trace/", 2026, ["telemetry", "trace", "privacy"]),
    ("paper.nested_model", "A Nested Model for Visualization Design and Validation", "IEEE TVCG", "paper", "https://doi.org/10.1109/TVCG.2009.111", 2009, ["visualization_design", "validation"]),
    ("paper.interaction_taxonomy", "Interactive Dynamics for Visual Analysis", "ACM Queue", "paper", "https://doi.org/10.1145/2133416.2146416", 2012, ["interaction", "taxonomy", "analysis"]),
    ("paper.draco", "Formalizing Visualization Design Knowledge as Constraints", "IEEE TVCG", "paper", "https://doi.org/10.1109/TVCG.2018.2865240", 2019, ["visualization_constraints", "recommendation"]),
    ("paper.uncertainty", "Hypothetical Outcome Plots Outperform Error Bars and Violin Plots", "CHI", "paper", "https://doi.org/10.1145/3025453.3025592", 2017, ["uncertainty", "decision"]),
    ("paper.alt_text", "Accessible Visualization via Natural Language Descriptions: A Four-Level Model", "IEEE TVCG", "paper", "https://doi.org/10.1109/TVCG.2021.3114770", 2022, ["accessibility", "description", "semantics"]),
    ("paper.rich_screenreader", "Rich Screen Reader Experiences for Accessible Data Visualization", "Computer Graphics Forum", "paper", "https://doi.org/10.1111/cgf.14519", 2022, ["accessibility", "navigation", "structure"]),
    ("paper.web_access_audit", "The Accessibility of Data Visualizations on the Web for Screen Reader Users", "ACM TACCESS", "paper", "https://doi.org/10.1145/3557899", 2023, ["accessibility", "audit", "experience"]),
    ("paper.chart_reader", "Chart Reader: Accessible Visualization Experiences Designed with Screen Reader Users", "ACM CHI", "paper", "https://doi.org/10.1145/3544548.3581186", 2023, ["accessibility", "co_design", "interaction"]),
    ("paper.olli", "Olli: An Extensible Visualization Library for Screen Reader Accessibility", "IEEE VIS", "paper", "https://vis.csail.mit.edu/pubs/olli/", 2022, ["accessibility", "tree", "adapter"]),
    ("paper.risk_representation", "Numerical and Visual Representations of Uncertainty Lead to Different Patterns of Decision Making", "IEEE CG&A", "paper", "https://doi.org/10.1109/MCG.2023.3299875", 2024, ["uncertainty", "risk", "decision"]),
    ("paper.charting_eda", "Charting EDA: Characterizing Interactive Visualization Use in Computational Notebooks", "IEEE TVCG", "paper", "https://vis.csail.mit.edu/pubs/charting-eda/", 2025, ["eda", "notebook", "analysis_state"]),
    ("paper.jupyter", "Jupyter Notebooks - a publishing format for reproducible computational workflows", "IOS Press", "paper", "https://doi.org/10.3233/978-1-61499-649-1-87", 2016, ["notebook", "reproducibility", "workflow"]),
    ("paper.notebook_repro", "A Large-Scale Study about Quality and Reproducibility of Jupyter Notebooks", "MSR", "paper", "https://doi.org/10.1109/MSR.2019.00077", 2019, ["notebook", "reproducibility", "quality"]),
]


SOURCES = [
    {
        "source_id": sid(local), "edition": EDITION, "status": "candidate_evidence",
        "title": title, "publisher": publisher, "source_kind": kind, "url": url,
        "publication_year": year, "accessed_at": ACCESSED, "supports_topics": topics,
        "authority_scope": "Normative for the named standard or first-party implementation, or empirical for the named study only.",
        "limitations": ["Does not prove universal product support or settle cross-context ownership."],
    }
    for local, title, publisher, kind, url, year, topics in SOURCE_ROWS
]


# family, local id, name, semantic owner statement, excluded owner, four typed operations,
# evidence locals, cross-plane relationships.
CONTEXT_ROWS = [
    ("meaning", "semantic_query", "Semantic Query Intent", "Meaning of a governed analytical request over metrics, dimensions, filters, grain and time", "SQL generation, rendering and transport", ["declare_query", "bind_members", "validate_grain", "normalize_query"], ["substrait.spec", "iso.sql"], ["semantic_formula", "query_kernel"]),
    ("meaning", "metric_binding", "Metric and Dimension Binding", "Stable metric, dimension, hierarchy, unit and aggregation references at an edition", "Formula evaluation and chart styling", ["resolve_metric", "resolve_dimension", "bind_hierarchy", "bind_semantic_edition"], ["w3c.data_cube", "sdmx.standards"], ["semantic_formula", "governance"]),
    ("meaning", "analytical_case", "Analytical Case", "A durable question, evidence set, assumptions, observations, alternatives and decision posture", "Dashboard layout and action execution", ["open_case", "attach_question", "record_observation", "close_case"], ["w3c.prov_dm", "paper.nested_model"], ["decisions_actions", "lineage"]),
    ("meaning", "query_parameter", "Query Parameter Contract", "Typed caller-controlled values and their semantic binding", "Widget appearance and query engine planning", ["declare_parameter", "validate_value", "bind_default", "serialize_parameter"], ["jsonschema.spec", "vegalite.selection"], ["semantic_formula", "security_privacy"]),
    ("meaning", "olap_model", "OLAP Cube and Hierarchy", "Dimensions, levels, members, measures, coordinates, roll-up and drill laws", "Pivot screen geometry and storage cubes", ["address_cell", "roll_up", "drill_down", "slice_cube"], ["microsoft.mdx", "microsoft.xmla", "w3c.data_cube"], ["semantic_formula", "query_kernel"]),
    ("meaning", "pivot_spec", "Pivot Semantic Layout", "Assignment of semantic axes, measures, totals and subtotal meaning", "Pixel layout and export formatting", ["assign_axis", "pivot_axis", "declare_totals", "expand_member"], ["microsoft.mdx", "sdmx.standards"], ["semantic_formula", "presentation"]),
    ("meaning", "result_contract", "Analytical Query Result", "Typed schema, rows/cells, ordering, completeness, errors and source-cut receipts", "Visual marks and interaction focus", ["accept_result", "validate_schema", "page_result", "declare_completeness"], ["arrow.columnar", "arrow.flight_sql"], ["query_kernel", "quality", "lineage"]),
    ("composition", "dashboard_definition", "Dashboard Definition", "Reusable composition of queries, views, controls and semantic links", "A single analytical case or runtime session", ["compose_dashboard", "link_views", "bind_control", "version_dashboard"], ["vega.spec", "observable.framework"], ["product_truth", "governance"]),
    ("composition", "dashboard_runtime", "Dashboard Runtime", "Instantiation, refresh coordination, partial loading and runtime disclosure", "Definition authorship and source finality", ["instantiate_dashboard", "refresh_view", "coordinate_loading", "dispose_dashboard"], ["vega.spec", "ietf.cache"], ["runtime_resource", "query_kernel"]),
    ("composition", "report_definition", "Report Definition", "Parameterized sections, pagination intent, schedules and output profiles", "Immutable report rendition", ["define_report", "bind_section", "set_pagination", "schedule_report"], ["w3c.html", "w3c.csvw"], ["presentation", "governance"]),
    ("composition", "report_snapshot", "Report Snapshot", "Immutable rendition bound to parameter values, data cuts, locale, code and time", "Live dashboard state and future source corrections", ["render_snapshot", "seal_snapshot", "verify_snapshot", "supersede_snapshot"], ["w3c.prov_o", "rocrate.spec"], ["lineage", "quality"]),
    ("composition", "visual_grammar", "Visualization Grammar", "Provider-neutral marks, encodings, transforms, composition and guide declarations", "Metric meaning and renderer implementation", ["declare_mark", "compose_view", "lower_grammar", "validate_grammar"], ["vega.spec", "vegalite.spec", "vegalite.paper"], ["semantic_formula", "presentation"]),
    ("composition", "visual_encoding", "Visual Encoding", "Mapping of typed data fields or derived values to visual channels", "Field meaning and aesthetic theme tokens", ["bind_channel", "validate_channel", "encode_missingness", "encode_uncertainty"], ["vegalite.spec", "paper.draco"], ["data_shapes", "accessibility"]),
    ("composition", "scales_guides", "Scales, Axes and Legends", "Domain-to-range mapping and truthful guide semantics", "Business thresholds and source units", ["construct_scale", "derive_ticks", "render_axis_contract", "render_legend_contract"], ["vega.scales", "w3c.css_color4"], ["semantic_formula", "i18n"]),
    ("composition", "layout_faceting", "Layout and Faceting", "Spatial composition, repeat, layer, facet and responsive constraint semantics", "Data grouping meaning unless explicitly bound", ["facet_view", "layer_view", "resolve_layout", "adapt_viewport"], ["vegalite.spec", "w3c.media_queries5"], ["presentation", "accessibility"]),
    ("composition", "table_crosstab", "Analytical Table and Crosstab", "Accessible rows, columns, headers, spans, totals, sorting and virtualization contracts", "Underlying metric semantics", ["construct_table", "sort_table", "expand_group", "virtualize_table"], ["w3c.html", "w3c.aria12"], ["accessibility", "i18n"]),
    ("composition", "geospatial_portrayal", "Geospatial Portrayal", "CRS-bound viewport, layer, style, map and tile portrayal contracts", "Feature truth, geometry computation and geocoding", ["bind_map_layer", "apply_style", "request_tiles", "disclose_crs"], ["ogc.maps", "ogc.tiles", "ogc.styles", "ogc.features"], ["query_kernel", "data_shapes"]),
    ("composition", "uncertainty_display", "Uncertainty and Evidence Display", "Visible uncertainty, intervals, sample, quality, provenance and caveat encodings", "Statistical inference and evidence generation", ["bind_uncertainty", "choose_uncertainty_form", "display_evidence", "disclose_caveat"], ["paper.uncertainty", "paper.risk_representation", "w3c.dqv"], ["quality", "decisions_actions"]),
    ("notebook", "notebook_document", "Notebook Document", "Versioned cells, narrative, metadata and stored output references", "Kernel process, environment and trusted execution", ["create_notebook", "insert_cell", "reorder_cell", "serialize_notebook"], ["jupyter.nbformat", "paper.jupyter"], ["lineage", "product_truth"]),
    ("notebook", "execution_kernel", "Notebook Execution Kernel", "Language/runtime process identity, messages, execution ordering and lifecycle", "Notebook narrative and presentation meaning", ["start_kernel", "execute_cell", "interrupt_kernel", "shutdown_kernel"], ["jupyter.messaging", "jupyter.kernels", "jupyter.kernelspec"], ["query_kernel", "runtime_resource", "security_privacy"]),
    ("notebook", "cell_output", "Notebook Cell Output", "Typed stream, display, execute-result and error outputs with trust posture", "Authoritative source truth", ["capture_output", "sanitize_output", "clear_output", "bind_display_update"], ["jupyter.nbformat", "jupyter.security"], ["security_privacy", "presentation"]),
    ("notebook", "exploratory_session", "Exploratory Analysis Session", "Hypothesis, manipulation, observation and branch trace during open-ended analysis", "Production semantic model changes", ["begin_exploration", "record_hypothesis", "record_observation", "branch_analysis"], ["paper.charting_eda", "paper.interaction_taxonomy"], ["decisions_actions", "lineage"]),
    ("notebook", "analysis_history", "Analysis History and Replay", "Ordered semantic actions, state checkpoints and replay compatibility", "Raw UI event telemetry and kernel determinism", ["append_action", "checkpoint_state", "replay_actions", "fork_history"], ["w3c.prov_dm", "paper.charting_eda"], ["lineage", "governance"]),
    ("governed", "self_service", "Governed Self-Service", "Allowed discover-compose-query-publish workflow under policy and competence scopes", "Central metric authorship and identity administration", ["request_access", "compose_analysis", "validate_policy", "promote_asset"], ["w3c.dcat3", "w3c.prov_o"], ["governance", "security_privacy"]),
    ("governed", "catalog_discovery", "Analytical Asset Discovery", "Search, classification, ownership, certification and compatibility metadata for consumable assets", "Asset execution and truth adjudication", ["index_asset", "search_assets", "inspect_asset", "resolve_edition"], ["w3c.dcat3", "w3c.dqv"], ["governance", "product_truth"]),
    ("governed", "policy_projection", "Consumption Policy Projection", "Projection of row, column, purpose, tenant and export constraints into consumption", "Canonical policy decision and credential issuance", ["request_entitlement", "project_policy", "mask_output", "explain_denial"], ["openapi.spec", "w3c.prov_o"], ["governance", "security_privacy"]),
    ("governed", "lineage_quality", "Lineage and Quality Disclosure", "Presentation of origin, transformations, owners, quality measures and limitations", "Lineage capture and quality computation", ["attach_lineage", "attach_quality", "render_disclosure", "acknowledge_limitation"], ["w3c.prov_o", "w3c.dqv"], ["lineage", "quality"]),
    ("delivery", "alert_rule", "Analytical Alert Rule", "Condition, evaluation schedule/window, pending/firing/resolved state and evidence cut", "Receiver routing and message transport", ["define_alert", "evaluate_alert", "transition_alert", "suppress_evaluation"], ["prometheus.alert_rules", "sdmx.standards"], ["query_kernel", "decisions_actions"]),
    ("delivery", "notification_delivery", "Notification Delivery", "Routing, grouping, inhibition, retry, acknowledgement and delivery receipts", "Alert truth evaluation", ["route_notification", "group_notifications", "deliver_notification", "record_acknowledgement"], ["prometheus.alertmanager", "prometheus.notifications", "cloudevents.spec"], ["security_privacy", "decisions_actions"]),
    ("delivery", "subscription", "Analytical Subscription", "Subscriber-scoped trigger, cadence, asset edition, parameters, delivery profile and consent", "Alert evaluation semantics and channel implementation", ["create_subscription", "pause_subscription", "renew_subscription", "cancel_subscription"], ["sdmx.standards", "cloudevents.spec"], ["governance", "security_privacy"]),
    ("exchange", "embedded_analytics", "Embedded Analytics Contract", "Host-child identity, tenant context, sizing, events, capabilities and isolation", "Host application business logic and chart semantics", ["initialize_embed", "negotiate_capabilities", "resize_embed", "dispose_embed"], ["w3c.html", "w3c.pointer_events3", "openapi.spec"], ["security_privacy", "product_truth"]),
    ("exchange", "analytics_api", "Analytical API", "Typed semantic requests, result schemas, pagination/streaming, errors and assurance receipts", "Metric authorship and provider execution plans", ["describe_api", "submit_query", "stream_result", "cancel_request"], ["arrow.flight", "arrow.flight_sql", "arrow.adbc", "openapi.spec"], ["query_kernel", "security_privacy"]),
    ("exchange", "export", "Analytical Export", "One-way serialization of a bounded result or rendition with format and loss receipts", "Continuing access governance after bytes leave", ["select_export_format", "serialize_export", "sign_export", "download_export"], ["w3c.csvw", "ietf.csv", "ietf.content_disposition"], ["encoding_compression", "security_privacy"]),
    ("exchange", "governed_sharing", "Governed Sharing", "Continuing access to an identified asset under revocable policy, audience and audit", "Byte serialization and public publication", ["create_share", "authorize_recipient", "revoke_share", "audit_share"], ["w3c.web_share", "w3c.activitystreams2", "w3c.prov_o"], ["governance", "security_privacy"]),
    ("exchange", "annotation", "Collaborative Annotation", "Targeted comment, reply, status, motivation, selector and immutable authorship", "Underlying evidence modification", ["create_annotation", "reply_annotation", "resolve_annotation", "reanchor_annotation"], ["w3c.web_annotation", "w3c.activitystreams2"], ["governance", "decisions_actions"]),
    ("presentation", "story", "Analytical Story and Presentation", "Ordered scenes, claims, evidence bindings, speaker/audience context and navigation", "Evidence generation and slide-renderer mechanics", ["compose_story", "bind_claim", "sequence_scene", "present_story"], ["w3c.prov_o", "paper.nested_model"], ["decisions_actions", "product_truth"]),
    ("presentation", "accessibility", "Accessibility Semantics", "Programmatic structure, names, relationships, navigation and equivalent access", "Cosmetic styling or a single alternate text string", ["construct_access_tree", "label_graphic", "provide_navigation", "test_equivalent_access"], ["w3c.wcag22", "w3c.aria12", "w3c.graphics_aria", "paper.rich_screenreader"], ["security_privacy", "product_truth"]),
    ("presentation", "localization", "Internationalization and Localization", "Language, locale, direction, plural, collation, number/date/unit formatting and translation edition", "Metric unit conversion and source timezone truth", ["negotiate_locale", "format_value", "layout_bidi", "bind_translation"], ["ietf.bcp47", "unicode.cldr", "unicode.uts35", "unicode.bidi", "ecma.intl"], ["semantic_formula", "product_truth"]),
    ("presentation", "mobile_offline", "Mobile and Offline Consumption", "Install, viewport, connectivity, local persistence, deferred action and synchronization posture", "Source finality and unrestricted offline entitlement", ["install_surface", "enter_offline", "queue_local_action", "reconcile_online"], ["w3c.service_workers", "w3c.app_manifest", "w3c.indexeddb3"], ["runtime_resource", "security_privacy"]),
    ("state", "interaction_intent", "Interaction Intent", "Semantic user action such as filter, select, compare, drill, explain or navigate", "Pointer/keyboard event mechanics and visual styling", ["declare_interaction", "bind_target", "authorize_interaction", "emit_semantic_action"], ["paper.interaction_taxonomy", "vegalite.selection"], ["decisions_actions", "accessibility"]),
    ("state", "interaction_state", "Interaction State", "Selections, brushes, focus, expanded nodes, viewport and parameter state at an edition", "Query result truth and durable analytical conclusions", ["initialize_state", "reduce_event", "serialize_state", "restore_state"], ["vega.signals", "vega.events", "vegalite.selection"], ["product_truth", "query_kernel"]),
    ("state", "session_reproducibility", "Session and Reproducibility", "Identity of inputs, semantic editions, environment, code, actions, seeds and outputs needed to assess replay", "Guarantee that all external sources remain available", ["capture_session", "seal_environment", "replay_session", "compare_replay"], ["rocrate.spec", "paper.notebook_repro", "w3c.prov_dm"], ["lineage", "query_kernel"]),
    ("state", "content_versioning", "Analytical Content Versioning", "Immutable editions, branches, merges, compatibility and publication lifecycle of analytical assets", "Source data versioning", ["commit_asset", "branch_asset", "merge_asset", "publish_asset"], ["w3c.prov_o", "rocrate.spec"], ["governance", "product_truth"]),
    ("state", "client_cache", "Client Cache Freshness", "Cached representation identity, age, revalidation, eviction and offline eligibility", "Source finality or semantic recency", ["cache_representation", "revalidate_cache", "evict_cache", "disclose_cache_age"], ["ietf.cache", "ietf.http", "w3c.service_workers"], ["persistence_lakehouse", "source_systems"]),
    ("state", "source_finality", "Source Finality Disclosure", "Visible source watermark, revision policy, observed-at time, finality class and correction risk", "Client cache validity and business acceptance", ["bind_source_cut", "display_watermark", "display_revision_risk", "acknowledge_provisional"], ["sdmx.standards", "w3c.dqv", "w3c.prov_o"], ["source_systems", "quality"]),
    ("state", "live_view", "Live View Coordination", "Subscription epochs, incremental patches, reorder, reconnect, snapshot handoff and visible staleness", "Report snapshots and source change capture", ["open_live_view", "apply_patch", "resume_stream", "freeze_live_view"], ["arrow.flight", "cloudevents.spec", "ietf.http"], ["pipeline_dataflow", "source_systems"]),
    ("handoff", "explanation_evidence", "Explanation and Evidence", "Human-readable rationale linked to inspectable evidence, assumptions and limitations", "Treating prose as proof or generating analytical evidence", ["compose_explanation", "link_evidence", "challenge_explanation", "supersede_explanation"], ["w3c.prov_o", "w3c.dqv", "paper.risk_representation"], ["quality", "decisions_actions"]),
    ("handoff", "decision_handoff", "Human Decision Handoff", "Decision question, alternatives, recommendation posture, authority, due state and acknowledgement", "Automated business action execution", ["prepare_handoff", "assign_authority", "record_decision", "dispatch_action_request"], ["w3c.prov_dm", "w3c.web_annotation"], ["decisions_actions", "governance"]),
    ("handoff", "telemetry_privacy", "Consumption Telemetry and Privacy", "Purpose-bound minimal operational/interaction telemetry with retention and access controls", "Analytical subject profiling and unrestricted replay", ["declare_telemetry", "minimize_event", "redact_payload", "expire_telemetry"], ["otel.traces", "w3c.prov_o"], ["security_privacy", "governance"]),
    ("handoff", "performance_budget", "Consumption Performance Budget", "Finite latency, memory, bandwidth, mark/row, battery and interaction-response budgets", "Query optimizer internals and business priority", ["declare_budget", "estimate_cost", "apply_degradation", "report_budget"], ["vega.spec", "arrow.flight", "w3c.service_workers"], ["runtime_resource", "query_kernel"]),
    ("handoff", "credential_scope", "Consumption Credential Scope", "Audience, tenant, asset, operation, purpose, duration and delegation constraints", "Identity proofing and canonical policy authorship", ["request_credential", "attenuate_scope", "bind_credential", "revoke_credential"], ["openapi.spec", "w3c.prov_o"], ["security_privacy", "governance"]),
    ("handoff", "case_archive", "Analytical Case Archive", "Retention package of question, evidence, decisions, presentations, receipts and supersession state", "Raw warehouse retention and legal policy ownership", ["package_case", "validate_archive", "export_archive", "restore_archive"], ["rocrate.spec", "w3c.prov_o", "w3c.web_annotation"], ["persistence_lakehouse", "governance"]),
]


CONTEXTS: list[dict[str, Any]] = []
CAPABILITIES: list[dict[str, Any]] = []
DECISIONS: list[dict[str, Any]] = []

for family, local, name, owns, outside, operations, evidence, cross_planes in CONTEXT_ROWS:
    context_id = cid(local)
    decision_id = f"decision.{PREFIX}.{local}.binding"
    operation_ids = [f"capability.{PREFIX}.{local}.{op}" for op in operations]
    CONTEXTS.append({
        "context_id": context_id, "edition": EDITION, "status": "candidate", "family": family,
        "name": name, "owns": owns, "outside": [outside],
        "invariants": ["Meaning and state have one explicit owner.", "Unknown semantics or capability fail closed."],
        "capability_refs": operation_ids, "decision_refs": [decision_id],
        "evidence_refs": [sid(item) for item in evidence], "cross_plane_refs": cross_planes,
        "candidate_limits": ["Boundary awaits global context-map adjudication.", "Enumeration is open-world."],
    })
    DECISIONS.append({
        "decision_id": decision_id, "edition": EDITION, "status": "candidate",
        "context_ref": context_id,
        "question": f"Which declared {name.lower()} contract is compatible with the intent and offered runtime?",
        "options": ["bind_exact", "bind_declared_degradation", "request_human_choice", "refuse"],
        "required_inputs": ["intent requirements", "semantic edition", "policy scope", "runtime offers"],
        "default_policy": "Refuse when meaning, authority, edition, loss or assurance is unknown.",
        "decision_receipt": ["selected option", "matched requirements", "evidence scope", "degradations", "unresolved gaps"],
        "evidence_refs": [sid(item) for item in evidence[:2]],
    })
    for index, operation in enumerate(operations):
        pretty = operation.replace("_", " ")
        CAPABILITIES.append({
            "capability_id": operation_ids[index], "edition": EDITION, "status": "candidate",
            "context_ref": context_id, "family": family, "kind": "typed_operation",
            "name": pretty.title(),
            "meaning": f"{pretty.title()} under the declared {name.lower()} semantics and authority.",
            "typed_inputs": ["intent_ref", "semantic_edition", "authority_scope", "operation_parameters"],
            "typed_outputs": ["owned_state_or_artifact", "operation_receipt"],
            "preconditions": ["Referenced semantics exist at a compatible edition.", "Caller is authorized for the operation and data scope."],
            "postconditions": ["Output identifies its semantic edition and provenance.", "Any loss, partiality or staleness is explicit."],
            "effects": "pure" if operation.startswith(("declare", "validate", "construct", "normalize", "format", "estimate", "describe")) else "state_or_io_explicit",
            "determinism": "deterministic_given_declared_inputs_or_receipted_runtime_variance",
            "information_loss": "none_unless_declared_in_receipt",
            "batch_live_posture": "explicit_snapshot_or_live_epoch_required",
            "decision_refs": [decision_id], "evidence_refs": [sid(item) for item in evidence[:2]],
            "refusals": ["unknown_semantics", "incompatible_edition", "unauthorized_scope", "undeclared_loss", "unbounded_runtime"],
        })


PRESENTATION_ROWS = [
    ("semantic_query_request", "semantic_query", ["semantic_model_ref", "metric_refs", "dimension_refs", "filters", "grain", "time_scope", "parameters"], "semantic meaning remains outside visual encoding", ["substrait.spec"]),
    ("analytical_result", "result_contract", ["schema", "ordered_batches", "completeness", "source_cut", "warnings", "assurance_receipt"], "query result remains outside presentation state", ["arrow.columnar", "arrow.flight_sql"]),
    ("dashboard_definition", "dashboard_definition", ["asset_id", "edition", "view_specs", "query_refs", "control_bindings", "layout_constraints"], "dashboard definition remains outside one analytical case", ["vega.spec", "observable.framework"]),
    ("dashboard_instance", "dashboard_runtime", ["definition_ref", "session_ref", "view_statuses", "refresh_epoch", "visible_disclosures"], "runtime instance remains outside reusable definition", ["vega.signals", "ietf.cache"]),
    ("report_definition", "report_definition", ["sections", "parameters", "pagination", "schedule", "rendition_profiles"], "report definition remains outside rendered snapshot", ["w3c.html"]),
    ("report_snapshot", "report_snapshot", ["definition_ref", "parameter_values", "data_cuts", "render_time", "locale", "digest", "supersession"], "immutable snapshot remains outside live view", ["w3c.prov_o", "rocrate.spec"]),
    ("visual_grammar", "visual_grammar", ["data_refs", "transforms", "marks", "encodings", "scales", "guides", "composition", "parameters"], "grammar remains outside metric semantics and renderer code", ["vega.spec", "vegalite.spec"]),
    ("mark_encoding", "visual_encoding", ["field_ref", "field_type", "channel", "mark", "aggregate_posture", "missingness", "legend_ref"], "encoding remains outside field meaning", ["vegalite.spec", "paper.draco"]),
    ("scale_guide", "scales_guides", ["semantic_domain", "visual_range", "transform", "clamp", "unknown_value", "axis", "legend"], "scale mapping remains outside business threshold definition", ["vega.scales"]),
    ("layout", "layout_faceting", ["viewport", "constraints", "facet_keys", "layers", "responsive_breakpoints", "reading_order"], "screen geometry remains outside semantic grouping", ["vegalite.spec", "w3c.media_queries5"]),
    ("analytical_table", "table_crosstab", ["columns", "header_tree", "row_keys", "cells", "totals", "sort", "virtualization", "accessible_structure"], "table presentation remains outside query relation", ["w3c.html", "w3c.aria12"]),
    ("map_portrayal", "geospatial_portrayal", ["crs", "bbox", "layers", "styles", "tilesets", "attribution", "resolution"], "portrayal remains outside geospatial feature truth", ["ogc.maps", "ogc.tiles", "ogc.styles"]),
    ("uncertainty_display", "uncertainty_display", ["estimate_ref", "uncertainty_kind", "bounds_or_distribution", "encoding", "legend", "decision_warning"], "display remains outside inference and evidence", ["paper.uncertainty", "paper.risk_representation"]),
    ("lineage_disclosure", "lineage_quality", ["result_ref", "source_refs", "activities", "agents", "derivations", "coverage", "limitations"], "disclosure remains outside lineage capture", ["w3c.prov_o"]),
    ("quality_disclosure", "lineage_quality", ["subject_ref", "measure_ref", "value", "method", "time", "authority", "caveat"], "quality display remains outside quality measurement", ["w3c.dqv"]),
    ("freshness_disclosure", "source_finality", ["observed_at", "source_watermark", "cache_age", "finality_class", "revision_policy", "next_expected_update"], "cache age remains outside source finality", ["ietf.cache", "sdmx.standards"]),
    ("explanation", "explanation_evidence", ["claim", "rationale", "assumptions", "evidence_refs", "limitations", "author", "edition"], "explanation remains outside evidence", ["w3c.prov_o", "w3c.dqv"]),
    ("alert_evaluation", "alert_rule", ["rule_ref", "evaluation_time", "data_cut", "condition_result", "state", "labels", "evidence_refs"], "alert evaluation remains outside notification delivery", ["prometheus.alert_rules"]),
    ("notification_message", "notification_delivery", ["alert_refs", "receiver", "route", "template_edition", "attempt", "status", "backlink"], "delivery remains outside alert truth", ["prometheus.notifications", "prometheus.alertmanager"]),
    ("subscription", "subscription", ["subscriber", "asset_ref", "parameters", "trigger", "cadence", "delivery_profile", "consent", "expiry"], "subscription remains outside alert rule", ["sdmx.standards"]),
    ("export_package", "export", ["subject_ref", "data_cut", "format", "schema", "locale", "loss_receipt", "digest", "policy_notice"], "exported bytes remain outside governed sharing", ["w3c.csvw", "ietf.content_disposition"]),
    ("governed_share", "governed_sharing", ["asset_ref", "audience", "policy_ref", "permission", "expiry", "revocation", "audit_ref"], "governed access remains outside byte export", ["w3c.web_share", "w3c.activitystreams2"]),
    ("annotation", "annotation", ["body", "target", "selector", "motivation", "creator", "created", "reply_to", "state"], "annotation remains outside target evidence", ["w3c.web_annotation"]),
    ("story_scene", "story", ["scene_id", "claim_refs", "evidence_refs", "view_state", "speaker_notes", "transition", "audience"], "story claim remains outside evidence generation", ["w3c.prov_o"]),
    ("accessibility_tree", "accessibility", ["roles", "names", "descriptions", "relationships", "navigation_order", "data_refs", "interaction_commands"], "accessibility semantics remain outside styling", ["w3c.graphics_aria", "w3c.graphics_aam", "paper.rich_screenreader"]),
    ("localized_surface", "localization", ["language_tag", "locale", "direction", "numbering_system", "calendar", "time_zone", "translation_edition"], "localized formatting remains outside semantic value", ["unicode.uts35", "ecma.intl"]),
    ("offline_bundle", "mobile_offline", ["asset_editions", "result_cuts", "cache_policy", "credential_scope", "queued_actions", "expiry", "sync_receipt"], "offline availability remains outside source finality", ["w3c.service_workers", "w3c.indexeddb3"]),
    ("decision_packet", "decision_handoff", ["question", "alternatives", "evidence_refs", "uncertainty", "recommendation_posture", "authority", "due_at", "acknowledgement"], "decision handoff remains outside action execution", ["w3c.prov_dm", "w3c.web_annotation"]),
]


PRESENTATION_CONTRACTS = [
    {
        "contract_id": f"presentation.{PREFIX}.{local}", "edition": EDITION, "status": "candidate",
        "contract_kind": "presentation", "owner_context_ref": cid(context_local), "name": local.replace("_", " ").title(),
        "contract_fields": fields, "distinction_preserved": distinction,
        "invariants": ["Every semantic reference identifies an edition.", "Loss, staleness, partiality and uncertainty are visible."],
        "refusals": ["missing_semantic_owner", "undisclosed_loss", "inaccessible_equivalent", "unknown_freshness"],
        "evidence_refs": [sid(item) for item in evidence],
    }
    for local, context_local, fields, distinction, evidence in PRESENTATION_ROWS
]


INTERACTION_ROWS = [
    ("set_filter", "interaction_intent", "Set a typed semantic predicate without mutating the underlying result.", ["predicate", "target_scope"], ["vegalite.selection"]),
    ("clear_filter", "interaction_intent", "Remove a named predicate with explicit empty-selection semantics.", ["filter_ref"], ["vegalite.selection"]),
    ("select_point", "interaction_state", "Select one or more semantic tuples by stable key.", ["tuple_keys", "toggle_policy"], ["vegalite.selection"]),
    ("select_interval", "interaction_state", "Select a continuous semantic interval in declared field space.", ["field_refs", "bounds"], ["vegalite.selection"]),
    ("drill_down", "olap_model", "Move to child hierarchy members under declared roll-up laws.", ["coordinate", "hierarchy_ref"], ["microsoft.mdx"]),
    ("roll_up", "olap_model", "Move to a parent hierarchy level without inventing additive semantics.", ["coordinate", "target_level"], ["microsoft.mdx"]),
    ("pivot", "pivot_spec", "Reassign semantic axes while retaining cell coordinates and total rules.", ["axis_assignment"], ["microsoft.mdx"]),
    ("sort", "table_crosstab", "Apply a declared stable ordering and null/collation policy.", ["sort_keys", "direction", "null_policy"], ["unicode.collation"]),
    ("search", "catalog_discovery", "Search governed assets with visible ranking and scope.", ["query", "facets", "scope"], ["w3c.dcat3"]),
    ("paginate", "result_contract", "Advance a result continuation without implying global completeness.", ["continuation_token", "page_size"], ["arrow.flight_sql"]),
    ("zoom_pan", "geospatial_portrayal", "Change viewport while preserving coordinate reference and visible resolution.", ["viewport_delta"], ["ogc.maps"]),
    ("inspect", "interaction_intent", "Request exact datum, provenance and encoding details for a target.", ["target_ref"], ["paper.interaction_taxonomy"]),
    ("focus_navigate", "accessibility", "Move programmatic focus through semantic graphic structure.", ["direction", "structure_level"], ["w3c.aria_apg", "paper.rich_screenreader"]),
    ("compare", "analytical_case", "Place compatible evidence items into an explicit comparison set.", ["evidence_refs", "comparison_basis"], ["paper.interaction_taxonomy"]),
    ("annotate", "annotation", "Attach a motivated body to a stable target selector.", ["body", "target", "selector"], ["w3c.web_annotation"]),
    ("share", "governed_sharing", "Request governed access for a declared audience and duration.", ["asset_ref", "audience", "permission"], ["w3c.web_share"]),
    ("subscribe", "subscription", "Register consented recurring or event-driven delivery.", ["asset_ref", "trigger", "delivery_profile"], ["sdmx.standards"]),
    ("acknowledge_alert", "notification_delivery", "Record receiver acknowledgement without altering alert truth.", ["notification_ref", "actor"], ["prometheus.alertmanager"]),
    ("change_parameter", "query_parameter", "Validate and bind a typed parameter before recomputation.", ["parameter_ref", "value"], ["jsonschema.spec"]),
    ("run_cell", "execution_kernel", "Request kernel execution with message and environment identity.", ["cell_ref", "kernel_session"], ["jupyter.messaging"]),
    ("cancel_execution", "execution_kernel", "Request interruption and expose whether effects or partial outputs remain.", ["execution_ref"], ["jupyter.kernels"]),
    ("replay_session", "session_reproducibility", "Replay a sealed action/session record under compatibility checks.", ["session_ref", "target_environment"], ["rocrate.spec"]),
    ("restore_state", "interaction_state", "Restore compatible presentation state without treating it as a result.", ["state_ref", "definition_edition"], ["vega.signals"]),
    ("branch_analysis", "analysis_history", "Fork a trace at an identified checkpoint.", ["history_ref", "checkpoint_ref"], ["w3c.prov_dm"]),
    ("freeze_live_view", "live_view", "Convert a live epoch into a receipted immutable view cut.", ["live_view_ref", "epoch"], ["arrow.flight", "w3c.prov_o"]),
    ("handoff_decision", "decision_handoff", "Transfer a decision packet to named authority and capture acknowledgement.", ["decision_packet_ref", "authority_ref"], ["w3c.prov_dm"]),
]


INTERACTION_CONTRACTS = [
    {
        "contract_id": f"interaction.{PREFIX}.{local}", "edition": EDITION, "status": "candidate",
        "contract_kind": "interaction", "owner_context_ref": cid(context_local), "name": local.replace("_", " ").title(),
        "meaning": meaning, "contract_fields": fields + ["actor_scope", "prior_state_ref", "event_time", "idempotency_key"],
        "state_transition": ["validate", "authorize", "reduce", "emit_receipt"],
        "invariants": ["Raw device events are translated into semantic intent.", "Result data and presentation state retain separate identities."],
        "refusals": ["ambiguous_target", "unauthorized_action", "incompatible_state_edition", "unavailable_equivalent_input"],
        "evidence_refs": [sid(item) for item in evidence],
    }
    for local, context_local, meaning, fields, evidence in INTERACTION_ROWS
]


# One requirement/offer decision surface per context ensures the compiler cannot dispatch by a
# renderer, dashboard product or file-format name.  Offers are capability records, not vendors.
REQUIREMENT_OFFER_BINDINGS = []
for context in CONTEXTS:
    local = context["context_id"].split(".")[-1]
    REQUIREMENT_OFFER_BINDINGS.append({
        "binding_id": f"binding.{PREFIX}.{local}", "edition": EDITION, "status": "candidate",
        "context_ref": context["context_id"],
        "requirement": {
            "semantic_owner": context["context_id"], "required_capability_refs": context["capability_refs"],
            "edition_posture": "exact_or_declared_compatible", "snapshot_live_posture": "explicit",
            "accessibility_posture": "equivalent_semantic_access", "loss_posture": "declared_only",
            "assurance": ["authority", "provenance", "freshness", "partiality", "policy"],
        },
        "offer_contract": {
            "must_declare": ["supported capability", "semantic edition", "limits", "loss", "state model", "failure modes", "security scope", "evidence"],
            "provider_names_are_nonsemantic": True,
        },
        "match_keys": ["semantic_owner", "capability", "edition", "types", "snapshot_live", "loss", "accessibility", "policy", "budgets"],
        "success_receipt": ["selected offer", "matched keys", "degradations", "evidence refs"],
        "refusal": "refuse_no_compatible_evidence_backed_offer",
        "evidence_refs": context["evidence_refs"][:2],
    })


MAPPING_ROWS = [
    ("answer_metric", ["semantic_query", "metric_binding", "result_contract"], "pure_then_runtime", ["bind semantic members", "lower query requirement", "execute through qualified gateway", "return result receipt"]),
    ("pivot_cube", ["olap_model", "pivot_spec", "table_crosstab"], "mixed", ["bind cube coordinates", "apply hierarchy law", "derive pivot layout", "emit accessible table"]),
    ("open_dashboard", ["dashboard_definition", "dashboard_runtime", "client_cache", "source_finality"], "runtime", ["resolve definition edition", "instantiate session", "load result cuts", "disclose cache and finality"]),
    ("publish_dashboard", ["dashboard_definition", "self_service", "content_versioning", "policy_projection"], "runtime", ["validate semantic refs", "evaluate policy", "commit edition", "publish governed asset"]),
    ("render_live_report", ["report_definition", "result_contract", "localization", "accessibility"], "mixed", ["bind parameters", "fetch result", "localize values", "render equivalent semantics"]),
    ("seal_report_snapshot", ["report_definition", "report_snapshot", "source_finality", "case_archive"], "runtime", ["resolve data cuts", "render", "digest artifacts", "record supersession posture"]),
    ("compile_chart", ["visual_grammar", "visual_encoding", "scales_guides", "layout_faceting"], "pure", ["type channels", "validate encodings", "construct scales", "lower presentation IR"]),
    ("compile_accessible_chart", ["visual_grammar", "accessibility", "interaction_intent"], "mixed", ["derive semantic structure", "bind navigation", "retain data refs", "test equivalent tasks"]),
    ("portray_map", ["geospatial_portrayal", "scales_guides", "source_finality"], "runtime", ["bind CRS", "resolve style", "request portrayal", "show attribution and cut"]),
    ("show_uncertainty", ["uncertainty_display", "explanation_evidence", "decision_handoff"], "pure", ["validate uncertainty object", "select authorized form", "bind evidence", "warn decision consumer"]),
    ("run_notebook_cell", ["notebook_document", "execution_kernel", "cell_output"], "runtime", ["resolve kernel", "authorize execution", "send execute request", "capture typed output and effects"]),
    ("replay_notebook", ["notebook_document", "session_reproducibility", "execution_kernel"], "runtime", ["verify package", "qualify environment", "execute in recorded order", "compare receipts"]),
    ("begin_exploration", ["exploratory_session", "analysis_history", "interaction_state"], "mixed", ["open trace", "checkpoint state", "record hypotheses and observations", "preserve branches"]),
    ("promote_exploration", ["exploratory_session", "analytical_case", "self_service"], "runtime", ["extract durable question", "separate observations from claims", "validate governance", "publish candidate asset"]),
    ("evaluate_alert", ["alert_rule", "semantic_query", "source_finality"], "runtime", ["bind rule edition", "query declared window", "advance alert state", "attach evidence cut"]),
    ("deliver_alert", ["alert_rule", "notification_delivery", "credential_scope"], "runtime", ["consume alert event", "route and inhibit", "attenuate payload", "record delivery receipt"]),
    ("create_subscription", ["subscription", "policy_projection", "notification_delivery"], "runtime", ["record consent", "authorize asset and channel", "schedule trigger", "return subscription receipt"]),
    ("embed_dashboard", ["embedded_analytics", "dashboard_runtime", "credential_scope", "interaction_intent"], "runtime", ["negotiate host contract", "bind tenant credential", "instantiate", "translate semantic events"]),
    ("serve_analytical_api", ["analytics_api", "semantic_query", "result_contract"], "runtime", ["validate request schema", "bind intent", "stream typed batches", "emit errors and assurance"]),
    ("export_result", ["export", "result_contract", "localization", "policy_projection"], "runtime", ["authorize export", "freeze bounded result", "serialize with loss receipt", "sign and deliver"]),
    ("share_asset", ["governed_sharing", "credential_scope", "content_versioning"], "runtime", ["select immutable edition", "authorize audience", "create revocable grant", "audit access"]),
    ("annotate_evidence", ["annotation", "explanation_evidence", "content_versioning"], "runtime", ["resolve stable target", "create annotation", "notify collaborators", "preserve target edition"]),
    ("present_story", ["story", "analytical_case", "accessibility", "localization"], "mixed", ["bind claims to evidence", "order scenes", "localize", "offer equivalent navigation"]),
    ("consume_offline", ["mobile_offline", "client_cache", "credential_scope"], "runtime", ["select offline-eligible assets", "seal cache policy", "persist locally", "disclose age and expiry"]),
    ("sync_offline_actions", ["mobile_offline", "interaction_state", "annotation"], "runtime", ["validate queued action edition", "reauthorize", "resolve conflicts", "emit reconciliation receipt"]),
    ("restore_interaction", ["interaction_state", "content_versioning", "result_contract"], "pure_then_runtime", ["verify definition compatibility", "restore presentation state", "requery result separately", "report divergence"]),
    ("freeze_live_view", ["live_view", "report_snapshot", "source_finality"], "runtime", ["select stream epoch", "complete or mark partial", "seal rendition", "record source cut"]),
    ("revalidate_client_cache", ["client_cache", "live_view", "source_finality"], "runtime", ["send representation validator", "update cache state", "retain source finality separately", "display both"]),
    ("localize_dashboard", ["localization", "scales_guides", "layout_faceting"], "pure", ["resolve locale", "format labels and values", "apply bidi and line break", "revalidate layout"]),
    ("handoff_decision", ["decision_handoff", "analytical_case", "explanation_evidence"], "runtime", ["package question and alternatives", "link inspectable evidence", "assign authority", "capture acknowledgement"]),
    ("dispatch_action", ["decision_handoff", "credential_scope"], "runtime", ["verify recorded human decision", "construct external action request", "delegate to action owner", "retain action receipt ref"]),
    ("archive_case", ["case_archive", "analytical_case", "report_snapshot", "annotation"], "runtime", ["collect immutable editions", "validate references", "package with provenance", "apply retention policy"]),
    ("measure_experience", ["telemetry_privacy", "performance_budget"], "runtime", ["declare purpose", "minimize event schema", "record budget measures", "expire by policy"]),
    ("degrade_for_budget", ["performance_budget", "visual_grammar", "result_contract"], "mixed", ["compare cost to budget", "select authorized degradation", "preserve semantics", "display degradation receipt"]),
    ("explain_denial", ["policy_projection", "explanation_evidence"], "pure", ["map refusal code", "redact protected policy details", "render actionable explanation", "link appeal path"]),
    ("supersede_snapshot", ["report_snapshot", "content_versioning", "source_finality"], "runtime", ["identify correction", "create successor", "link supersession", "retain prior audit state"]),
]


COMPILER_MAPPINGS = [
    {
        "mapping_id": f"mapping.{PREFIX}.{local}", "edition": EDITION, "status": "candidate",
        "intent_class": local, "consulted_context_refs": [cid(item) for item in contexts],
        "target_runtime": target, "lowering_steps": steps,
        "emitted_requirements": ["semantic edition", "typed capability", "authority", "snapshot/live posture", "loss and accessibility posture", "finite budgets"],
        "success_receipt": ["bound contexts", "selected offers", "source/result cuts", "degradations", "evidence"],
        "refusal_codes": ["unowned_semantics", "no_compatible_offer", "unauthorized", "undeclared_loss", "unknown_freshness", "unbounded_cost"],
        "evidence_refs": list(dict.fromkeys(sum(([row[6][0]] for row in CONTEXT_ROWS if row[1] in contexts), [])))[:3],
    }
    for local, contexts, target, steps in MAPPING_ROWS
]
# Convert compiler evidence locals after construction.
for mapping in COMPILER_MAPPINGS:
    mapping["evidence_refs"] = [sid(item) for item in mapping["evidence_refs"]]


LIBRARY_ROWS = [
    ("semantic_query_types", "pure", ["semantic_query", "metric_binding", "query_parameter"], "Typed semantic-query AST, validation and canonicalization", "No metric authorship or execution planning"),
    ("cube_algebra", "pure", ["olap_model"], "Coordinates, hierarchies, roll-up, drill, slice and cell laws", "No storage cube or UI widgets"),
    ("pivot_algebra", "pure", ["pivot_spec", "table_crosstab"], "Semantic axis assignment, totals and crosstab header algebra", "No pixel layout or metric aggregation policy"),
    ("result_contracts", "pure", ["result_contract", "source_finality"], "Schemas, completeness, cut, partiality and assurance receipts", "No query execution or finality authority"),
    ("presentation_ir", "pure", ["visual_grammar", "dashboard_definition", "report_definition"], "Provider-neutral presentation intermediate representation", "No business semantics or renderer implementation"),
    ("visual_encoding", "pure", ["visual_encoding", "scales_guides"], "Channel typing, scale construction and guide contracts", "No automatic metric inference"),
    ("layout_solver", "pure", ["layout_faceting"], "Constraint-based view composition and responsive layout", "No semantic grouping decisions"),
    ("table_model", "pure", ["table_crosstab", "accessibility"], "Virtualizable header/cell model with semantic reading order", "No data retrieval"),
    ("geo_portrayal_ir", "pure", ["geospatial_portrayal"], "CRS, viewport, layer, style and tileset contracts", "No geometry kernel or feature authority"),
    ("uncertainty_contracts", "pure", ["uncertainty_display", "explanation_evidence"], "Uncertainty carriers, evidence links and decision warnings", "No statistical inference"),
    ("accessibility_semantics", "pure", ["accessibility", "interaction_intent"], "Accessible graphic tree, semantic commands and equivalence checks", "No cosmetic theme ownership"),
    ("i18n_format", "pure", ["localization"], "Locale negotiation, formatting plans, bidi and message identifiers", "No unit conversion or source time-zone truth"),
    ("interaction_reducer", "pure", ["interaction_intent", "interaction_state"], "Semantic event normalization and deterministic state reduction", "No raw device driver or query result mutation"),
    ("session_log", "pure", ["analysis_history", "session_reproducibility"], "Append-only semantic actions, checkpoints and replay compatibility", "No guarantee of external source availability"),
    ("client_cache_algebra", "pure", ["client_cache"], "Representation cache identity, age, revalidation, eviction and disclosure decisions", "No source finality, semantic recency or storage execution"),
    ("content_versioning_algebra", "pure", ["content_versioning"], "Immutable analytical-asset editions, branches, merges, compatibility and publication records", "No source-data versioning, publication authority or artifact storage"),
    ("disclosure_model", "pure", ["lineage_quality", "source_finality", "explanation_evidence"], "Structured quality, lineage, freshness, caveat and evidence disclosures", "No evidence generation"),
    ("notebook_document", "pure", ["notebook_document", "cell_output"], "Notebook serialization, cell/output typing and trust markers", "No kernel launch or execution"),
    ("alert_state", "pure", ["alert_rule"], "Pending, firing, resolved and suppressed analytical alert state machine", "No delivery routing"),
    ("analytical_case_reducer", "pure", ["analytical_case"], "Durable analytical-question, evidence, observation, alternative and lifecycle reduction", "No decision authority, action execution or archive storage"),
    ("decision_handoff_algebra", "pure", ["decision_handoff"], "Decision-packet, external-authority binding, decision-record and action-request-intent algebra", "No authority issuance, automated decision or business action execution"),
    ("case_archive_manifest", "pure", ["case_archive"], "Immutable analytical-case archive manifest, member closure, coverage and integrity validation", "No storage I/O, legal retention authority, truth or replay guarantee"),
    ("policy_projection", "pure", ["policy_projection", "credential_scope"], "Consumption requirements and scope attenuation data types", "No identity proofing or canonical policy decision"),
    ("query_gateway", "runtime", ["semantic_query", "analytics_api", "result_contract"], "Submit, stream, page, cancel and receipt analytical requests", "No semantic dispatch by provider name"),
    ("dashboard_runtime", "runtime", ["dashboard_runtime", "live_view"], "Instantiate view graphs, coordinate refresh epochs and dispose resources", "No dashboard authorship"),
    ("renderer_adapter", "runtime", ["visual_grammar", "accessibility", "localization"], "Lower presentation IR to qualified renderers with semantic equivalence checks", "No metric semantics"),
    ("kernel_client", "runtime", ["execution_kernel", "cell_output"], "Manage Jupyter-compatible kernel lifecycle and typed messages", "No notebook document ownership"),
    ("offline_store", "runtime", ["mobile_offline", "client_cache"], "Persist eligible bundles and reconcile queued actions", "No source finality or entitlement expansion"),
    ("result_stream", "runtime", ["analytics_api", "live_view"], "Arrow-compatible batches, patches, backpressure and continuation", "No result meaning"),
    ("subscription_runner", "runtime", ["subscription", "alert_rule"], "Evaluate schedules/triggers and maintain subscription lifecycle", "No notification transport"),
    ("notification_dispatch", "runtime", ["notification_delivery"], "Route, group, inhibit, retry and receipt deliveries", "No alert evaluation"),
    ("export_plan", "pure", ["export"], "Compile a provider-neutral export plan with an exact representation profile, disposition and declared loss", "No byte encoding, signing, transfer or continuing access governance"),
    ("export_encoder", "runtime", ["export"], "Encode one bounded result or rendition according to an exact export plan and emit integrity and loss receipts", "No format selection, signing authority, transfer or continuing access governance"),
    ("export_delivery_port", "runtime", ["export"], "Deliver one already encoded export artifact under an explicit authority, target and idempotency contract", "No encoding, recipient-policy authorship or continuing access governance"),
    ("report_snapshot_reducer", "pure", ["report_snapshot"], "Reduce the immutable report-snapshot lifecycle from declared cuts and rendition evidence", "No rendering, source-finality inference, export encoding or mutation of sealed snapshots"),
    ("embedded_bridge", "runtime", ["embedded_analytics", "credential_scope"], "Host-child handshake, resize and semantic event channel", "No host application business logic"),
    ("annotation_store", "runtime", ["annotation", "governed_sharing"], "Store version-targeted annotations and collaboration activity", "No mutation of annotated evidence"),
    ("telemetry_sink", "runtime", ["telemetry_privacy", "performance_budget"], "Purpose-bound minimized measures and traces", "No subject profiling"),
    ("case_archive_store_port", "runtime", ["case_archive"], "Persist and retrieve an already validated immutable analytical-case archive", "No archive meaning, content versioning, legal retention authority or acceptance"),
]


CAPS_BY_CONTEXT = {context["context_id"]: context["capability_refs"] for context in CONTEXTS}
EVIDENCE_BY_CONTEXT = {context["context_id"]: context["evidence_refs"] for context in CONTEXTS}
LIBRARIES = []
for local, layer, context_locals, responsibility, no_ownership in LIBRARY_ROWS:
    context_refs = [cid(item) for item in context_locals]
    capability_refs = [cap for ref in context_refs for cap in CAPS_BY_CONTEXT[ref]][:8]
    evidence_refs = list(dict.fromkeys(ref for context_ref in context_refs for ref in EVIDENCE_BY_CONTEXT[context_ref]))[:4]
    LIBRARIES.append({
        "library_id": f"library.{PREFIX}.{local}", "edition": EDITION, "status": "candidate",
        "layer": layer, "responsibility": responsibility,
        "contributes_to_context_refs": context_refs, "capability_refs": capability_refs,
        "input_contracts": ["typed immutable value objects"] if layer == "pure" else ["typed requests", "qualified runtime handles", "finite budgets"],
        "output_contracts": ["typed values and validation diagnostics"] if layer == "pure" else ["runtime receipts", "typed outputs", "resource and failure diagnostics"],
        "forbidden_ownership": [no_ownership, "provider names do not define canonical semantics"],
        "determinism_posture": "deterministic" if layer == "pure" else "runtime_variance_must_be_receipted",
        "evidence_refs": evidence_refs,
    })


EXPORT_REFUSALS = [
    "ExportSubjectUnresolved", "FormatOfferSetEmpty", "NoCompatibleRepresentation",
    "PolicyEditionUnknown", "AuthorityScopeInsufficient", "LossUndeclared",
    "SchemaIncompatible", "FilenameInvalid", "ResourceBudgetExceeded",
]
ENCODING_REFUSALS = [
    "ExportPlanInvalid", "InputCutUnresolved", "EncoderOfferIncompatible",
    "OutputBudgetExceeded", "EncodingFailed", "DigestMismatch", "Cancelled",
    "UnknownCompletionUnreconciled",
]
DELIVERY_REFUSALS = [
    "ArtifactUnresolved", "DeliveryTargetInvalid", "AuthorityScopeInsufficient",
    "DispositionInvalid", "IdempotencyConflict", "DeliveryFailed", "Cancelled",
    "UnknownCompletionUnreconciled",
]
SNAPSHOT_REFUSALS = [
    "SnapshotIdentityMissing", "SnapshotRevisionConflict", "DataCutUnresolved",
    "RenditionEvidenceMissing", "RenditionDigestMismatch", "SnapshotAlreadySealed",
    "SupersessionTargetInvalid", "VerificationIncomplete", "ResourceBudgetExceeded",
]
CASE_REFUSALS = [
    "CaseIdentityMissing", "CaseRevisionConflict", "QuestionInvalid", "EvidenceReferenceUnresolved",
    "ObservationInvalid", "AlternativeInvalid", "IllegalCaseTransition", "CaseAlreadyClosed",
    "PolicyEditionUnknown", "ResourceBudgetExceeded",
]
HANDOFF_REFUSALS = [
    "HandoffIdentityMissing", "HandoffRevisionConflict", "CaseReferenceUnresolved",
    "DecisionQuestionInvalid", "AlternativeSetInvalid", "AuthorityReferenceUnresolved",
    "AuthorityScopeInsufficient", "DecisionRecordInvalid", "IllegalHandoffTransition",
    "ActionRequestUnauthorized", "PolicyEditionUnknown", "ResourceBudgetExceeded",
]
ARCHIVE_MANIFEST_REFUSALS = [
    "ArchiveIdentityMissing", "CaseReferenceUnresolved", "ArchiveMemberUnresolved",
    "ArchiveMemberDigestMismatch", "ArchiveReferenceClosureIncomplete", "ArchiveCoverageUnknown",
    "LossUndeclared", "ArchiveEditionConflict", "PolicyEditionUnknown", "ResourceBudgetExceeded",
]
ARCHIVE_STORE_REFUSALS = [
    "ArchiveReferenceUnresolved", "ArchiveNotValidated", "ArchiveTargetInvalid",
    "AuthorityScopeInsufficient", "IdempotencyConflict", "StoreFailed", "LoadFailed",
    "DigestMismatch", "Cancelled", "UnknownCompletionUnreconciled", "ResourceBudgetExceeded",
]
CACHE_REFUSALS = [
    "RepresentationIdentityMissing", "CachePartitionUnknown", "ValidatorInvalid",
    "DirectiveProfileInvalid", "AgeIndeterminate", "RevalidationRequired", "EntryNotReusable",
    "EvictionPolicyUnresolved", "AuthorizationPartitionMismatch", "ResourceBudgetExceeded",
]
VERSIONING_REFUSALS = [
    "AssetIdentityMissing", "AssetEditionConflict", "ParentEditionUnresolved", "BranchUnresolved",
    "MergeBaseUnresolved", "MergeConflictUnresolved", "CompatibilityUnknown",
    "PublicationAuthorityUnresolved", "PublicationAuthorityInsufficient",
    "IllegalVersionTransition", "PolicyEditionUnknown", "ResourceBudgetExceeded",
]

EXACT_LIBRARY_CONTRACTS = {
    "library.cbv.export_plan": {
        "semantic_owner_ref": "context.cbv.export",
        "effect_boundary": "pure_no_io",
        "capability_refs": ["capability.cbv.export.select_export_format"],
        "public_types": ["ExportSubjectRef", "ExportRequirements", "ExportFormatOffer", "ExportPolicyEdition", "ExportPlan", "ExportLossAssessment", "ExportDisposition", "ContentDispositionProfile", "ExportPlanRefusal"],
        "public_traits": ["ExportPlanningAlgebra"],
        "input_types": ["ExportSubjectRef", "ExportRequirements", "ExportFormatOffer", "ExportPolicyEdition", "ContentDispositionProfile"],
        "output_types": ["ExportPlan", "ExportLossAssessment", "ExportDisposition"],
        "error_contracts": EXPORT_REFUSALS,
        "operations": [
            {"operation_ref": "operation.cbv.export-plan.compile", "name": "compile_export_plan", "input_types": ["ExportSubjectRef", "ExportRequirements", "ExportFormatOffer", "ExportPolicyEdition"], "output_type": "Result<ExportPlan,ExportPlanRefusal>", "purity": "pure", "effect_intent_type": None, "receipt_type": None, "refusal_types": EXPORT_REFUSALS},
            {"operation_ref": "operation.cbv.export-plan.assess-loss", "name": "assess_export_loss", "input_types": ["ExportPlan", "ExportRequirements"], "output_type": "Result<ExportLossAssessment,ExportPlanRefusal>", "purity": "pure", "effect_intent_type": None, "receipt_type": None, "refusal_types": EXPORT_REFUSALS},
            {"operation_ref": "operation.cbv.export-plan.bind-disposition", "name": "bind_export_disposition", "input_types": ["ExportPlan", "ContentDispositionProfile"], "output_type": "Result<ExportDisposition,ExportPlanRefusal>", "purity": "pure", "effect_intent_type": None, "receipt_type": None, "refusal_types": EXPORT_REFUSALS},
        ],
        "laws": [
            "format selection is a function of explicit requirements offers and policy edition, never provider identity or filename",
            "an export plan binds the exact subject cut representation profile schema locale and loss declaration",
            "representation compatibility does not imply semantic completeness",
            "every dropped coerced rounded reordered or redacted feature appears in the loss assessment",
            "content disposition and filename metadata do not change artifact identity or meaning",
        ],
        "oracles": ["format-negotiation-model", "csvw-profile-fixtures", "loss-conservation-properties", "content-disposition-negative-twins", "cross-implementation-differential"],
    },
    "library.cbv.export_encoder": {
        "semantic_owner_ref": "context.cbv.export",
        "effect_boundary": "effectful_runtime",
        "capability_refs": ["capability.cbv.export.serialize_export"],
        "public_types": ["ExportPlan", "ExportInputCut", "QualifiedEncoderRef", "EncodingBudget", "ExportEncodingIntent", "EncodedExportArtifact", "ExportEncodingReceipt", "ExportEncodingRefusal"],
        "public_traits": ["ExportEncoder"],
        "input_types": ["ExportPlan", "ExportInputCut", "QualifiedEncoderRef", "EncodingBudget", "ExportEncodingIntent"],
        "output_types": ["EncodedExportArtifact", "ExportEncodingReceipt"],
        "error_contracts": ENCODING_REFUSALS,
        "operations": [
            {"operation_ref": "operation.cbv.export-encoder.prepare", "name": "prepare_encoding", "input_types": ["ExportPlan", "ExportInputCut", "QualifiedEncoderRef", "EncodingBudget"], "output_type": "Result<ExportEncodingIntent,ExportEncodingRefusal>", "purity": "pure", "effect_intent_type": None, "receipt_type": None, "refusal_types": ENCODING_REFUSALS},
            {"operation_ref": "operation.cbv.export-encoder.encode", "name": "encode_export", "input_types": ["ExportEncodingIntent"], "output_type": "Result<EncodedExportArtifact,ExportEncodingRefusal>", "purity": "effectful_explicit", "effect_intent_type": "ExportEncodingIntent", "receipt_type": "ExportEncodingReceipt", "refusal_types": ENCODING_REFUSALS},
            {"operation_ref": "operation.cbv.export-encoder.verify", "name": "verify_encoded_export", "input_types": ["EncodedExportArtifact", "ExportPlan", "ExportEncodingReceipt"], "output_type": "Result<ExportEncodingReceipt,ExportEncodingRefusal>", "purity": "pure", "effect_intent_type": None, "receipt_type": None, "refusal_types": ENCODING_REFUSALS},
        ],
        "laws": [
            "encoding never selects or silently widens the export plan",
            "the receipt binds plan input cut encoder edition output digest byte count resource use and declared losses",
            "partial output is not a successful artifact",
            "unknown completion remains explicit and reconciles before retry",
            "a digest proves byte identity only and never truth authority or semantic completeness",
        ],
        "oracles": ["rfc4180-fixtures", "csvw-metadata-fixtures", "bounded-output-properties", "cancellation-fault-model", "cross-implementation-differential"],
    },
    "library.cbv.export_delivery_port": {
        "semantic_owner_ref": "context.cbv.export",
        "effect_boundary": "effectful_runtime",
        "capability_refs": ["capability.cbv.export.download_export"],
        "public_types": ["EncodedExportArtifactRef", "ExportDisposition", "ExportDeliveryTarget", "ExportDeliveryAuthorityRef", "ExportDeliveryIntent", "ExportDeliveryAttempt", "ExportDeliveryReceipt", "ExportDeliveryRefusal"],
        "public_traits": ["ExportDeliveryPort"],
        "input_types": ["EncodedExportArtifactRef", "ExportDisposition", "ExportDeliveryTarget", "ExportDeliveryAuthorityRef", "ExportDeliveryIntent"],
        "output_types": ["ExportDeliveryIntent", "ExportDeliveryAttempt", "ExportDeliveryReceipt"],
        "error_contracts": DELIVERY_REFUSALS,
        "operations": [
            {"operation_ref": "operation.cbv.export-delivery.prepare", "name": "prepare_export_delivery", "input_types": ["EncodedExportArtifactRef", "ExportDisposition", "ExportDeliveryTarget", "ExportDeliveryAuthorityRef"], "output_type": "Result<ExportDeliveryIntent,ExportDeliveryRefusal>", "purity": "pure", "effect_intent_type": None, "receipt_type": None, "refusal_types": DELIVERY_REFUSALS},
            {"operation_ref": "operation.cbv.export-delivery.deliver", "name": "deliver_export", "input_types": ["ExportDeliveryIntent"], "output_type": "Result<ExportDeliveryAttempt,ExportDeliveryRefusal>", "purity": "effectful_explicit", "effect_intent_type": "ExportDeliveryIntent", "receipt_type": "ExportDeliveryReceipt", "refusal_types": DELIVERY_REFUSALS},
            {"operation_ref": "operation.cbv.export-delivery.reconcile", "name": "reconcile_export_delivery", "input_types": ["ExportDeliveryIntent", "ExportDeliveryAttempt"], "output_type": "Result<ExportDeliveryReceipt,ExportDeliveryRefusal>", "purity": "effectful_explicit", "effect_intent_type": "ExportDeliveryIntent", "receipt_type": "ExportDeliveryReceipt", "refusal_types": DELIVERY_REFUSALS},
        ],
        "laws": [
            "delivery consumes an immutable encoded artifact and cannot change its bytes or declared meaning",
            "authorization to create an export is distinct from authorization to deliver it to one target",
            "intent attempt transport acknowledgement recipient access and authorized downstream use are distinct",
            "idempotency binds artifact target authority disposition and operation edition",
            "unknown completion remains explicit and reconciles before retry",
        ],
        "oracles": ["content-disposition-fixtures", "authority-attenuation-negative-twins", "idempotency-state-model", "unknown-completion-fault-model", "cross-implementation-differential"],
    },
    "library.cbv.report_snapshot_reducer": {
        "semantic_owner_ref": "context.cbv.report_snapshot",
        "effect_boundary": "pure_no_io",
        "capability_refs": ["capability.cbv.report_snapshot.render_snapshot", "capability.cbv.report_snapshot.seal_snapshot", "capability.cbv.report_snapshot.verify_snapshot", "capability.cbv.report_snapshot.supersede_snapshot"],
        "public_types": ["ReportSnapshotId", "ReportSnapshotRevision", "ReportSnapshotIntent", "SnapshotBinding", "RenditionEvidence", "SnapshotVerification", "SealedReportSnapshot", "SnapshotSupersession", "ReportSnapshotPolicyEdition", "ReportSnapshotRefusal"],
        "public_traits": ["ReportSnapshotAlgebra"],
        "input_types": ["ReportSnapshotIntent", "ReportSnapshotRevision", "SnapshotBinding", "RenditionEvidence", "ReportSnapshotPolicyEdition"],
        "output_types": ["ReportSnapshotRevision", "SnapshotVerification", "SealedReportSnapshot", "SnapshotSupersession"],
        "error_contracts": SNAPSHOT_REFUSALS,
        "operations": [
            {"operation_ref": "operation.cbv.report-snapshot.open", "name": "open_report_snapshot", "input_types": ["ReportSnapshotIntent", "SnapshotBinding", "ReportSnapshotPolicyEdition"], "output_type": "Result<ReportSnapshotRevision,ReportSnapshotRefusal>", "purity": "pure", "effect_intent_type": None, "receipt_type": None, "refusal_types": SNAPSHOT_REFUSALS},
            {"operation_ref": "operation.cbv.report-snapshot.record-rendition", "name": "record_snapshot_rendition", "input_types": ["ReportSnapshotRevision", "RenditionEvidence", "ReportSnapshotPolicyEdition"], "output_type": "Result<ReportSnapshotRevision,ReportSnapshotRefusal>", "purity": "pure", "effect_intent_type": None, "receipt_type": None, "refusal_types": SNAPSHOT_REFUSALS},
            {"operation_ref": "operation.cbv.report-snapshot.seal", "name": "seal_report_snapshot", "input_types": ["ReportSnapshotRevision", "ReportSnapshotPolicyEdition"], "output_type": "Result<SealedReportSnapshot,ReportSnapshotRefusal>", "purity": "pure", "effect_intent_type": None, "receipt_type": None, "refusal_types": SNAPSHOT_REFUSALS},
            {"operation_ref": "operation.cbv.report-snapshot.verify", "name": "verify_report_snapshot", "input_types": ["SealedReportSnapshot", "ReportSnapshotPolicyEdition"], "output_type": "Result<SnapshotVerification,ReportSnapshotRefusal>", "purity": "pure", "effect_intent_type": None, "receipt_type": None, "refusal_types": SNAPSHOT_REFUSALS},
            {"operation_ref": "operation.cbv.report-snapshot.supersede", "name": "supersede_report_snapshot", "input_types": ["SealedReportSnapshot", "SealedReportSnapshot", "ReportSnapshotPolicyEdition"], "output_type": "Result<SnapshotSupersession,ReportSnapshotRefusal>", "purity": "pure", "effect_intent_type": None, "receipt_type": None, "refusal_types": SNAPSHOT_REFUSALS},
        ],
        "laws": [
            "snapshot identity binds report definition parameters semantic and code editions data cuts locale rendition profile and recording time",
            "rendering evidence is an input to the reducer and the reducer performs no rendering or external I/O",
            "sealing makes one snapshot revision immutable and does not imply source finality truth or business acceptance",
            "verification distinguishes manifest completeness byte integrity provenance coverage and semantic equivalence",
            "supersession creates a directed relation and never mutates or erases the superseded snapshot",
        ],
        "oracles": ["snapshot-lifecycle-model", "binding-identity-properties", "rendition-digest-negative-twins", "supersession-dag-properties", "cross-implementation-differential"],
    },
    "library.cbv.analytical_case_reducer": {
        "semantic_owner_ref": "context.cbv.analytical_case",
        "effect_boundary": "pure_no_io",
        "capability_refs": ["capability.cbv.analytical_case.open_case", "capability.cbv.analytical_case.attach_question", "capability.cbv.analytical_case.record_observation", "capability.cbv.analytical_case.close_case"],
        "public_types": ["AnalyticalCaseId", "AnalyticalCaseRevision", "CaseQuestion", "CaseAssumption", "CaseObservationRef", "CaseEvidenceRef", "CaseAlternative", "CaseClosure", "AnalyticalCaseStatus", "AnalyticalCasePolicyEdition", "AnalyticalCaseRefusal"],
        "public_traits": ["AnalyticalCaseAlgebra"],
        "input_types": ["AnalyticalCaseRevision", "CaseQuestion", "CaseObservationRef", "CaseEvidenceRef", "CaseAlternative", "CaseClosure", "AnalyticalCasePolicyEdition"],
        "output_types": ["AnalyticalCaseRevision", "AnalyticalCaseStatus"],
        "error_contracts": CASE_REFUSALS,
        "operations": [
            {"operation_ref": "operation.cbv.analytical-case.open", "name": "open_analytical_case", "input_types": ["AnalyticalCaseId", "CaseQuestion", "AnalyticalCasePolicyEdition"], "output_type": "Result<AnalyticalCaseRevision,AnalyticalCaseRefusal>", "purity": "pure", "effect_intent_type": None, "receipt_type": None, "refusal_types": CASE_REFUSALS},
            {"operation_ref": "operation.cbv.analytical-case.attach-question", "name": "attach_case_question", "input_types": ["AnalyticalCaseRevision", "CaseQuestion", "AnalyticalCasePolicyEdition"], "output_type": "Result<AnalyticalCaseRevision,AnalyticalCaseRefusal>", "purity": "pure", "effect_intent_type": None, "receipt_type": None, "refusal_types": CASE_REFUSALS},
            {"operation_ref": "operation.cbv.analytical-case.record-observation", "name": "record_case_observation", "input_types": ["AnalyticalCaseRevision", "CaseObservationRef", "CaseEvidenceRef", "AnalyticalCasePolicyEdition"], "output_type": "Result<AnalyticalCaseRevision,AnalyticalCaseRefusal>", "purity": "pure", "effect_intent_type": None, "receipt_type": None, "refusal_types": CASE_REFUSALS},
            {"operation_ref": "operation.cbv.analytical-case.record-alternative", "name": "record_case_alternative", "input_types": ["AnalyticalCaseRevision", "CaseAlternative", "AnalyticalCasePolicyEdition"], "output_type": "Result<AnalyticalCaseRevision,AnalyticalCaseRefusal>", "purity": "pure", "effect_intent_type": None, "receipt_type": None, "refusal_types": CASE_REFUSALS},
            {"operation_ref": "operation.cbv.analytical-case.close", "name": "close_analytical_case", "input_types": ["AnalyticalCaseRevision", "CaseClosure", "AnalyticalCasePolicyEdition"], "output_type": "Result<AnalyticalCaseRevision,AnalyticalCaseRefusal>", "purity": "pure", "effect_intent_type": None, "receipt_type": None, "refusal_types": CASE_REFUSALS},
        ],
        "laws": [
            "question assumption observation evidence alternative recommendation decision and action remain distinct typed facts",
            "every mutation produces a new immutable revision and rejects a stale expected revision",
            "recording an observation or evidence reference does not establish truth relevance or acceptance",
            "closing a case does not create a decision authorize an action or prove a business outcome",
            "unknown evidence coverage and unresolved alternatives remain explicit and cannot be erased by closure",
        ],
        "oracles": ["analytical-case-state-model", "revision-conflict-properties", "observation-evidence-negative-twins", "closure-coverage-properties", "cross-implementation-differential"],
    },
    "library.cbv.decision_handoff_algebra": {
        "semantic_owner_ref": "context.cbv.decision_handoff",
        "effect_boundary": "pure_effect_intents",
        "capability_refs": ["capability.cbv.decision_handoff.prepare_handoff", "capability.cbv.decision_handoff.assign_authority", "capability.cbv.decision_handoff.record_decision", "capability.cbv.decision_handoff.dispatch_action_request"],
        "public_types": ["DecisionHandoffId", "DecisionHandoffRevision", "AnalyticalCaseRef", "DecisionQuestionRef", "DecisionAlternativeSetRef", "RecommendationRef", "DecisionAuthorityRef", "DecisionDueState", "HumanDecisionRecord", "ActionRequestIntent", "HandoffAcknowledgement", "DecisionHandoffPolicyEdition", "DecisionHandoffRefusal"],
        "public_traits": ["DecisionHandoffAlgebra"],
        "input_types": ["DecisionHandoffRevision", "AnalyticalCaseRef", "DecisionQuestionRef", "DecisionAlternativeSetRef", "RecommendationRef", "DecisionAuthorityRef", "HumanDecisionRecord", "DecisionHandoffPolicyEdition"],
        "output_types": ["DecisionHandoffRevision", "ActionRequestIntent", "HandoffAcknowledgement"],
        "error_contracts": HANDOFF_REFUSALS,
        "operations": [
            {"operation_ref": "operation.cbv.decision-handoff.prepare", "name": "prepare_decision_handoff", "input_types": ["AnalyticalCaseRef", "DecisionQuestionRef", "DecisionAlternativeSetRef", "RecommendationRef", "DecisionHandoffPolicyEdition"], "output_type": "Result<DecisionHandoffRevision,DecisionHandoffRefusal>", "purity": "pure", "effect_intent_type": None, "receipt_type": None, "refusal_types": HANDOFF_REFUSALS},
            {"operation_ref": "operation.cbv.decision-handoff.bind-authority", "name": "bind_external_decision_authority", "input_types": ["DecisionHandoffRevision", "DecisionAuthorityRef", "DecisionHandoffPolicyEdition"], "output_type": "Result<DecisionHandoffRevision,DecisionHandoffRefusal>", "purity": "pure", "effect_intent_type": None, "receipt_type": None, "refusal_types": HANDOFF_REFUSALS},
            {"operation_ref": "operation.cbv.decision-handoff.record-decision", "name": "record_human_decision", "input_types": ["DecisionHandoffRevision", "HumanDecisionRecord", "DecisionHandoffPolicyEdition"], "output_type": "Result<DecisionHandoffRevision,DecisionHandoffRefusal>", "purity": "pure", "effect_intent_type": None, "receipt_type": None, "refusal_types": HANDOFF_REFUSALS},
            {"operation_ref": "operation.cbv.decision-handoff.form-action-intent", "name": "form_action_request_intent", "input_types": ["DecisionHandoffRevision", "DecisionHandoffPolicyEdition"], "output_type": "Result<ActionRequestIntent,DecisionHandoffRefusal>", "purity": "pure", "effect_intent_type": "ActionRequestIntent", "receipt_type": None, "refusal_types": HANDOFF_REFUSALS},
        ],
        "laws": [
            "recommendation decision approval authority issuance action request action attempt and business effect are distinct",
            "the algebra only binds an externally issued authority reference and can never mint delegate widen or revoke authority",
            "a decision record binds the human actor authority edition input cut alternatives rationale and recording time",
            "forming an action request intent performs no external I O and confers no execution authority",
            "no model or automated agent can satisfy the human decision or authority types",
        ],
        "oracles": ["decision-handoff-state-model", "authority-reference-negative-twins", "recommendation-decision-separation-properties", "action-intent-no-effect-oracle", "cross-implementation-differential"],
    },
    "library.cbv.case_archive_manifest": {
        "semantic_owner_ref": "context.cbv.case_archive",
        "effect_boundary": "pure_no_io",
        "capability_refs": ["capability.cbv.case_archive.package_case", "capability.cbv.case_archive.validate_archive"],
        "public_types": ["CaseArchiveId", "CaseArchiveEdition", "AnalyticalCaseRef", "CaseArchiveMemberDescriptor", "CaseArchiveManifest", "CaseArchiveCoverage", "ArchiveLossDeclaration", "ValidatedCaseArchive", "CaseArchivePolicyEdition", "CaseArchiveRefusal"],
        "public_traits": ["CaseArchiveManifestAlgebra"],
        "input_types": ["CaseArchiveId", "AnalyticalCaseRef", "CaseArchiveMemberDescriptor", "CaseArchiveManifest", "CaseArchivePolicyEdition"],
        "output_types": ["CaseArchiveManifest", "CaseArchiveEdition", "CaseArchiveCoverage", "ValidatedCaseArchive"],
        "error_contracts": ARCHIVE_MANIFEST_REFUSALS,
        "operations": [
            {"operation_ref": "operation.cbv.case-archive.package", "name": "package_case_archive_manifest", "input_types": ["CaseArchiveId", "AnalyticalCaseRef", "CaseArchiveMemberDescriptor", "CaseArchivePolicyEdition"], "output_type": "Result<CaseArchiveManifest,CaseArchiveRefusal>", "purity": "pure", "effect_intent_type": None, "receipt_type": None, "refusal_types": ARCHIVE_MANIFEST_REFUSALS},
            {"operation_ref": "operation.cbv.case-archive.assess-coverage", "name": "assess_case_archive_coverage", "input_types": ["CaseArchiveManifest", "CaseArchivePolicyEdition"], "output_type": "Result<CaseArchiveCoverage,CaseArchiveRefusal>", "purity": "pure", "effect_intent_type": None, "receipt_type": None, "refusal_types": ARCHIVE_MANIFEST_REFUSALS},
            {"operation_ref": "operation.cbv.case-archive.validate", "name": "validate_case_archive", "input_types": ["CaseArchiveManifest", "CaseArchiveCoverage", "CaseArchivePolicyEdition"], "output_type": "Result<ValidatedCaseArchive,CaseArchiveRefusal>", "purity": "pure", "effect_intent_type": None, "receipt_type": None, "refusal_types": ARCHIVE_MANIFEST_REFUSALS},
        ],
        "laws": [
            "an archive edition binds the exact member identities editions media types digests relations and declared omissions",
            "metadata is not an exhaustive inventory unless the selected archive profile explicitly requires and validates closure",
            "byte integrity does not prove truth completeness authority semantic equivalence reproducibility or replayability",
            "archive construction cannot create legal retention deletion disclosure or preservation authority",
            "a validated archive is immutable and correction creates a successor edition with explicit supersession",
        ],
        "oracles": ["ro-crate-profile-fixtures", "manifest-reference-closure-properties", "digest-member-negative-twins", "coverage-loss-properties", "cross-implementation-differential"],
    },
    "library.cbv.case_archive_store_port": {
        "semantic_owner_ref": "context.cbv.case_archive",
        "effect_boundary": "effectful_runtime",
        "capability_refs": ["capability.cbv.case_archive.export_archive", "capability.cbv.case_archive.restore_archive"],
        "public_types": ["ValidatedCaseArchiveRef", "CaseArchiveStoreTarget", "CaseArchiveStoreAuthorityRef", "CaseArchiveStoreIntent", "CaseArchiveLoadIntent", "CaseArchiveStoreAttempt", "CaseArchiveStoreReceipt", "CaseArchiveLoadReceipt", "CaseArchiveStorePolicyEdition", "CaseArchiveStoreRefusal"],
        "public_traits": ["CaseArchiveStorePort"],
        "input_types": ["ValidatedCaseArchiveRef", "CaseArchiveStoreTarget", "CaseArchiveStoreAuthorityRef", "CaseArchiveStoreIntent", "CaseArchiveLoadIntent", "CaseArchiveStorePolicyEdition"],
        "output_types": ["CaseArchiveStoreIntent", "CaseArchiveLoadIntent", "CaseArchiveStoreAttempt", "CaseArchiveStoreReceipt", "CaseArchiveLoadReceipt"],
        "error_contracts": ARCHIVE_STORE_REFUSALS,
        "operations": [
            {"operation_ref": "operation.cbv.case-archive-store.prepare-store", "name": "prepare_case_archive_store", "input_types": ["ValidatedCaseArchiveRef", "CaseArchiveStoreTarget", "CaseArchiveStoreAuthorityRef", "CaseArchiveStorePolicyEdition"], "output_type": "Result<CaseArchiveStoreIntent,CaseArchiveStoreRefusal>", "purity": "pure", "effect_intent_type": None, "receipt_type": None, "refusal_types": ARCHIVE_STORE_REFUSALS},
            {"operation_ref": "operation.cbv.case-archive-store.store", "name": "store_case_archive", "input_types": ["CaseArchiveStoreIntent"], "output_type": "Result<CaseArchiveStoreAttempt,CaseArchiveStoreRefusal>", "purity": "effectful_explicit", "effect_intent_type": "CaseArchiveStoreIntent", "receipt_type": "CaseArchiveStoreReceipt", "refusal_types": ARCHIVE_STORE_REFUSALS},
            {"operation_ref": "operation.cbv.case-archive-store.prepare-load", "name": "prepare_case_archive_load", "input_types": ["ValidatedCaseArchiveRef", "CaseArchiveStoreTarget", "CaseArchiveStoreAuthorityRef", "CaseArchiveStorePolicyEdition"], "output_type": "Result<CaseArchiveLoadIntent,CaseArchiveStoreRefusal>", "purity": "pure", "effect_intent_type": None, "receipt_type": None, "refusal_types": ARCHIVE_STORE_REFUSALS},
            {"operation_ref": "operation.cbv.case-archive-store.load", "name": "load_case_archive", "input_types": ["CaseArchiveLoadIntent"], "output_type": "Result<CaseArchiveLoadReceipt,CaseArchiveStoreRefusal>", "purity": "effectful_explicit", "effect_intent_type": "CaseArchiveLoadIntent", "receipt_type": "CaseArchiveLoadReceipt", "refusal_types": ARCHIVE_STORE_REFUSALS},
        ],
        "laws": [
            "the port stores and returns the exact validated archive edition without changing its manifest or meaning",
            "store intent attempt acknowledgement durable availability load verification and consumer acceptance are distinct",
            "idempotency binds archive edition target authority operation edition and requested disposition",
            "unknown completion remains explicit and reconciles before retry",
            "successful storage does not establish legal retention compliance truth completeness replayability or restored usability",
        ],
        "oracles": ["archive-store-state-model", "idempotency-properties", "unknown-completion-fault-model", "loaded-digest-negative-twins", "cross-implementation-differential"],
    },
    "library.cbv.client_cache_algebra": {
        "semantic_owner_ref": "context.cbv.client_cache",
        "effect_boundary": "pure_no_io",
        "capability_refs": ["capability.cbv.client_cache.cache_representation", "capability.cbv.client_cache.revalidate_cache", "capability.cbv.client_cache.evict_cache", "capability.cbv.client_cache.disclose_cache_age"],
        "public_types": ["RepresentationCacheKey", "RepresentationIdentity", "AuthorizationPartitionRef", "CacheValidator", "CacheEntryMetadata", "CacheAge", "CacheDirectiveProfile", "RevalidationDecision", "EvictionDecision", "CacheDisclosure", "ClientCachePolicyEdition", "ClientCacheRefusal"],
        "public_traits": ["ClientCacheAlgebra"],
        "input_types": ["RepresentationIdentity", "AuthorizationPartitionRef", "CacheValidator", "CacheEntryMetadata", "CacheDirectiveProfile", "ClientCachePolicyEdition"],
        "output_types": ["RepresentationCacheKey", "RevalidationDecision", "EvictionDecision", "CacheDisclosure"],
        "error_contracts": CACHE_REFUSALS,
        "operations": [
            {"operation_ref": "operation.cbv.client-cache.derive-key", "name": "derive_representation_cache_key", "input_types": ["RepresentationIdentity", "AuthorizationPartitionRef", "CacheDirectiveProfile"], "output_type": "Result<RepresentationCacheKey,ClientCacheRefusal>", "purity": "pure", "effect_intent_type": None, "receipt_type": None, "refusal_types": CACHE_REFUSALS},
            {"operation_ref": "operation.cbv.client-cache.evaluate-revalidation", "name": "evaluate_cache_revalidation", "input_types": ["CacheEntryMetadata", "CacheDirectiveProfile", "ClientCachePolicyEdition"], "output_type": "Result<RevalidationDecision,ClientCacheRefusal>", "purity": "pure", "effect_intent_type": None, "receipt_type": None, "refusal_types": CACHE_REFUSALS},
            {"operation_ref": "operation.cbv.client-cache.evaluate-eviction", "name": "evaluate_cache_eviction", "input_types": ["CacheEntryMetadata", "CacheDirectiveProfile", "ClientCachePolicyEdition"], "output_type": "Result<EvictionDecision,ClientCacheRefusal>", "purity": "pure", "effect_intent_type": None, "receipt_type": None, "refusal_types": CACHE_REFUSALS},
            {"operation_ref": "operation.cbv.client-cache.disclose", "name": "disclose_client_cache_state", "input_types": ["CacheEntryMetadata", "CacheAge", "ClientCachePolicyEdition"], "output_type": "Result<CacheDisclosure,ClientCacheRefusal>", "purity": "pure", "effect_intent_type": None, "receipt_type": None, "refusal_types": CACHE_REFUSALS},
        ],
        "laws": [
            "cache identity binds resource representation semantic edition and authorization partition",
            "cache freshness age validation and reuse eligibility do not establish source finality semantic recency or truth",
            "revalidation success does not imply that the underlying source has become final or unrevisable",
            "private or authorization varying representations cannot be reused across partitions",
            "eviction changes only client cache state and never mutates source or analytical asset identity",
        ],
        "oracles": ["rfc9111-cache-model", "authorization-partition-negative-twins", "age-finality-negative-twins", "revalidation-state-properties", "cross-implementation-differential"],
    },
    "library.cbv.content_versioning_algebra": {
        "semantic_owner_ref": "context.cbv.content_versioning",
        "effect_boundary": "pure_no_io",
        "capability_refs": ["capability.cbv.content_versioning.commit_asset", "capability.cbv.content_versioning.branch_asset", "capability.cbv.content_versioning.merge_asset", "capability.cbv.content_versioning.publish_asset"],
        "public_types": ["AnalyticalAssetId", "AnalyticalAssetEditionId", "AnalyticalAssetRevision", "AssetBranchId", "AssetMergeBaseRef", "AssetMergeDecision", "AssetCompatibilityAssessment", "PublicationAuthorityRef", "AuthorizedPublicationRecord", "AssetSupersession", "ContentVersioningPolicyEdition", "ContentVersioningRefusal"],
        "public_traits": ["AnalyticalContentVersioningAlgebra"],
        "input_types": ["AnalyticalAssetRevision", "AnalyticalAssetEditionId", "AssetBranchId", "AssetMergeBaseRef", "AssetMergeDecision", "PublicationAuthorityRef", "ContentVersioningPolicyEdition"],
        "output_types": ["AnalyticalAssetRevision", "AssetCompatibilityAssessment", "AuthorizedPublicationRecord", "AssetSupersession"],
        "error_contracts": VERSIONING_REFUSALS,
        "operations": [
            {"operation_ref": "operation.cbv.content-versioning.commit", "name": "commit_analytical_asset_edition", "input_types": ["AnalyticalAssetRevision", "ContentVersioningPolicyEdition"], "output_type": "Result<AnalyticalAssetEditionId,ContentVersioningRefusal>", "purity": "pure", "effect_intent_type": None, "receipt_type": None, "refusal_types": VERSIONING_REFUSALS},
            {"operation_ref": "operation.cbv.content-versioning.branch", "name": "branch_analytical_asset", "input_types": ["AnalyticalAssetEditionId", "AssetBranchId", "ContentVersioningPolicyEdition"], "output_type": "Result<AnalyticalAssetRevision,ContentVersioningRefusal>", "purity": "pure", "effect_intent_type": None, "receipt_type": None, "refusal_types": VERSIONING_REFUSALS},
            {"operation_ref": "operation.cbv.content-versioning.merge", "name": "merge_analytical_asset", "input_types": ["AssetMergeBaseRef", "AssetMergeDecision", "ContentVersioningPolicyEdition"], "output_type": "Result<AnalyticalAssetRevision,ContentVersioningRefusal>", "purity": "pure", "effect_intent_type": None, "receipt_type": None, "refusal_types": VERSIONING_REFUSALS},
            {"operation_ref": "operation.cbv.content-versioning.record-publication", "name": "record_authorized_asset_publication", "input_types": ["AnalyticalAssetEditionId", "PublicationAuthorityRef", "ContentVersioningPolicyEdition"], "output_type": "Result<AuthorizedPublicationRecord,ContentVersioningRefusal>", "purity": "pure", "effect_intent_type": None, "receipt_type": None, "refusal_types": VERSIONING_REFUSALS},
        ],
        "laws": [
            "an analytical asset edition is immutable and any change creates a distinct edition",
            "branch ancestry merge bases conflicts resolutions and compatibility assessments remain explicit",
            "publication records only an externally authorized fact and cannot issue widen or infer publication authority",
            "publication does not imply consumer acceptance runtime deployment source data finality or business validity",
            "mutable latest aliases are not reproducible identities and cannot replace explicit edition selection",
        ],
        "oracles": ["asset-version-dag-properties", "merge-conflict-state-model", "publication-authority-negative-twins", "edition-identity-properties", "cross-implementation-differential"],
    },
}

for library in LIBRARIES:
    if library["library_id"] in EXACT_LIBRARY_CONTRACTS:
        library.update(EXACT_LIBRARY_CONTRACTS[library["library_id"]])


RETIRED_LIBRARY_COMPOSITIONS = [{
    "decision_id": "decision.cbv.retire-export-writer.v1",
    "retired_library_id": "library.cbv.export_writer",
    "edition": EDITION,
    "status": "retired_composition",
    "reason": "The candidate combined export planning, encoding, delivery and report-snapshot lifecycle under two semantic owners and four independently replaceable effect boundaries.",
    "replacement_library_refs": [
        "library.cbv.export_plan", "library.cbv.export_encoder",
        "library.cbv.export_delivery_port", "library.cbv.report_snapshot_reducer",
    ],
    "capability_partition": {
        "library.cbv.export_plan": ["capability.cbv.export.select_export_format"],
        "library.cbv.export_encoder": ["capability.cbv.export.serialize_export"],
        "library.cbv.export_delivery_port": ["capability.cbv.export.download_export"],
        "library.cbv.report_snapshot_reducer": [
            "capability.cbv.report_snapshot.render_snapshot", "capability.cbv.report_snapshot.seal_snapshot",
            "capability.cbv.report_snapshot.verify_snapshot", "capability.cbv.report_snapshot.supersede_snapshot",
        ],
    },
    "delegated_capability_refs": ["capability.cbv.export.sign_export"],
    "delegated_authority_refs": ["context.lpe.signature-seal"],
    "no_compatibility_alias": True,
    "evidence_refs": ["source.cbv.w3c.csvw", "source.cbv.ietf.csv", "source.cbv.ietf.content_disposition", "source.cbv.w3c.prov_o", "source.cbv.rocrate.spec"],
}, {
    "decision_id": "decision.cbv.retire-decision-case.v1",
    "retired_library_id": "library.cbv.decision_case",
    "edition": EDITION,
    "status": "retired_composition",
    "reason": "The candidate combined analytical-case lifecycle, human decision handoff and archive packaging under three semantic owners; it also incorrectly made authority assignment and action dispatch appear internal and pure.",
    "replacement_library_refs": ["library.cbv.analytical_case_reducer", "library.cbv.decision_handoff_algebra", "library.cbv.case_archive_manifest"],
    "capability_partition": {
        "library.cbv.analytical_case_reducer": ["capability.cbv.analytical_case.open_case", "capability.cbv.analytical_case.attach_question", "capability.cbv.analytical_case.record_observation", "capability.cbv.analytical_case.close_case"],
        "library.cbv.decision_handoff_algebra": ["capability.cbv.decision_handoff.prepare_handoff", "capability.cbv.decision_handoff.assign_authority", "capability.cbv.decision_handoff.record_decision", "capability.cbv.decision_handoff.dispatch_action_request"],
        "library.cbv.case_archive_manifest": ["capability.cbv.case_archive.package_case", "capability.cbv.case_archive.validate_archive"],
    },
    "delegated_capability_refs": ["capability.cbv.case_archive.export_archive", "capability.cbv.case_archive.restore_archive"],
    "delegated_authority_refs": ["context.decisions_actions.authority", "context.governance.retention-policy"],
    "no_compatibility_alias": True,
    "evidence_refs": ["source.cbv.w3c.prov_dm", "source.cbv.w3c.web_annotation", "source.cbv.rocrate.spec"],
}, {
    "decision_id": "decision.cbv.retire-case-archive-store.v1",
    "retired_library_id": "library.cbv.case_archive_store",
    "edition": EDITION,
    "status": "retired_composition",
    "reason": "The candidate combined pure archive-manifest semantics, effectful persistence and unrelated analytical-content versioning under one runtime facade.",
    "replacement_library_refs": ["library.cbv.case_archive_manifest", "library.cbv.case_archive_store_port", "library.cbv.content_versioning_algebra"],
    "capability_partition": {
        "library.cbv.case_archive_manifest": ["capability.cbv.case_archive.package_case", "capability.cbv.case_archive.validate_archive"],
        "library.cbv.case_archive_store_port": ["capability.cbv.case_archive.export_archive", "capability.cbv.case_archive.restore_archive"],
        "library.cbv.content_versioning_algebra": ["capability.cbv.content_versioning.commit_asset", "capability.cbv.content_versioning.branch_asset", "capability.cbv.content_versioning.merge_asset", "capability.cbv.content_versioning.publish_asset"],
    },
    "delegated_capability_refs": ["capability.governance.retention-policy.evaluate"],
    "delegated_authority_refs": ["context.governance.retention-policy"],
    "no_compatibility_alias": True,
    "evidence_refs": ["source.cbv.rocrate.spec", "source.cbv.w3c.prov_o"],
}, {
    "decision_id": "decision.cbv.retire-cache-identity.v1",
    "retired_library_id": "library.cbv.cache_identity",
    "edition": EDITION,
    "status": "retired_composition",
    "reason": "The candidate conflated HTTP representation-cache reuse decisions with the immutable edition and publication lifecycle of analytical assets.",
    "replacement_library_refs": ["library.cbv.client_cache_algebra", "library.cbv.content_versioning_algebra"],
    "capability_partition": {
        "library.cbv.client_cache_algebra": ["capability.cbv.client_cache.cache_representation", "capability.cbv.client_cache.revalidate_cache", "capability.cbv.client_cache.evict_cache", "capability.cbv.client_cache.disclose_cache_age"],
        "library.cbv.content_versioning_algebra": ["capability.cbv.content_versioning.commit_asset", "capability.cbv.content_versioning.branch_asset", "capability.cbv.content_versioning.merge_asset", "capability.cbv.content_versioning.publish_asset"],
    },
    "delegated_capability_refs": ["capability.cbv.source_finality.bind_source_cut"],
    "delegated_authority_refs": ["context.cbv.source_finality"],
    "no_compatibility_alias": True,
    "evidence_refs": ["source.cbv.ietf.cache", "source.cbv.w3c.prov_o", "source.cbv.rocrate.spec"],
}]


CROSS_MAP_ROWS = [
    ("semantic.query", "semantic_query", "semantic_formula", "Consumes governed semantic identities and formulas; does not redefine them", "semantic meaning vs visual encoding"),
    ("semantic.metric", "metric_binding", "semantic_formula", "Binds metric and dimension editions supplied by the semantic plane", "metric definition vs result value"),
    ("query.lowering", "analytics_api", "query_kernel", "Emits typed query requirements and consumes result/assurance receipts", "query result vs presentation state"),
    ("query.notebook", "execution_kernel", "query_kernel", "Uses kernel execution services without assigning notebook-document ownership", "notebook document vs execution kernel"),
    ("quality.disclosure", "lineage_quality", "quality", "Projects quality measurements and limitations into consumption", "explanation vs evidence"),
    ("quality.uncertainty", "uncertainty_display", "quality", "Displays supplied uncertainty and quality carriers without inferring them", "uncertainty computation vs encoding"),
    ("lineage.result", "result_contract", "lineage", "Carries source/result cut and derivation references", "receipt vs proof"),
    ("lineage.session", "session_reproducibility", "lineage", "Records activities, entities, agents and environment identity", "replay package vs reproducibility guarantee"),
    ("governance.publish", "self_service", "governance", "Requests certification and publication decisions from the governance owner", "governed workflow vs policy authorship"),
    ("governance.share", "governed_sharing", "governance", "Consumes revocable policy decisions and provides share audit receipts", "export vs governed sharing"),
    ("security.projection", "policy_projection", "security_privacy", "Consumes canonical authorization and privacy decisions", "masking display vs policy authority"),
    ("security.embed", "embedded_analytics", "security_privacy", "Requires tenant, origin, audience and delegated credential constraints", "host identity vs child session"),
    ("security.telemetry", "telemetry_privacy", "security_privacy", "Submits purpose, minimization and retention requirements", "operational telemetry vs analytical subject data"),
    ("decision.case", "analytical_case", "decisions_actions", "Packages evidence and observations for deliberation", "dashboard vs analytical case"),
    ("decision.handoff", "decision_handoff", "decisions_actions", "Records human decision then delegates action execution", "decision record vs action effect"),
    ("product.asset", "content_versioning", "product_truth", "Publishes immutable analytical asset editions and compatibility", "asset edition vs runtime instance"),
    ("product.dashboard", "dashboard_definition", "product_truth", "Exposes dashboard definition identity and certification state", "dashboard definition vs live instance"),
    ("source.finality", "source_finality", "source_systems", "Consumes source watermark, correction and finality contracts", "client cache freshness vs source finality"),
    ("source.live", "live_view", "source_systems", "Consumes ordered changes and snapshot handoff offers", "stream epoch vs report snapshot"),
    ("cache.storage", "client_cache", "persistence_lakehouse", "Stores representations under explicit validators and expiry", "cache validity vs semantic recency"),
    ("runtime.budget", "performance_budget", "runtime_compute_resource", "Emits finite latency, memory, network, mark and battery budgets", "presentation degradation vs semantic degradation"),
    ("pipeline.patch", "live_view", "pipeline_dataflow", "Consumes incremental patches, epochs and retry boundaries", "patch order vs event-time finality"),
    ("encoding.export", "export", "encoding_compression", "Requests a format/codec with declared loss and compatibility", "serialization vs access governance"),
    ("shape.presentation", "visual_encoding", "data_shapes", "Consumes typed fields, structures and missingness carriers", "carrier shape vs visual channel"),
    ("accessibility.product", "accessibility", "product_truth", "Requires equivalent task semantics as a release criterion", "accessibility semantics vs styling"),
    ("i18n.semantic", "localization", "semantic_formula", "Formats but does not change units, time meaning or aggregation", "localized text vs semantic value"),
]


CROSS_DOMAIN_MAPPINGS = [
    {
        "cross_map_id": f"crossmap.{PREFIX}.{local}", "edition": EDITION, "status": "candidate",
        "local_context_ref": cid(context_local), "external_domain": external, "relationship": relationship,
        "preserved_distinction": distinction,
        "compiler_exchange": ["typed requirement", "qualified offer", "decision receipt", "gap on incompatibility"],
        "evidence_refs": EVIDENCE_BY_CONTEXT[cid(context_local)][:2],
    }
    for local, context_local, external, relationship, distinction in CROSS_MAP_ROWS
]


INVARIANT_ROWS = [
    ("semantic_visual_split", ["semantic_query", "visual_encoding"], "A visual channel may reference semantic meaning but may not define or silently change it.", "refuse_visual_semantic_inference", "A truthful rendering needs both identities."),
    ("result_state_split", ["result_contract", "interaction_state"], "Result data and presentation state have distinct identities, versions and lifecycles.", "refuse_state_as_result", "Selections and focus are not query rows."),
    ("dashboard_case_split", ["dashboard_definition", "analytical_case"], "A reusable dashboard is not itself a durable question/evidence/decision case.", "refuse_dashboard_as_case", "One surface may support many cases."),
    ("report_live_split", ["report_snapshot", "live_view"], "A report snapshot is immutable at a cut; a live view is epoch-bound and changing.", "refuse_live_as_snapshot", "Audit and replay require explicit posture."),
    ("alert_delivery_split", ["alert_rule", "notification_delivery"], "Alert state is evaluated independently of delivery routing, retry and acknowledgement.", "refuse_delivery_as_alert_truth", "Delivery success cannot establish condition truth."),
    ("export_share_split", ["export", "governed_sharing"], "Export serializes bytes; governed sharing maintains revocable access to an asset.", "refuse_export_as_governed_share", "Control after export is not implied."),
    ("notebook_kernel_split", ["notebook_document", "execution_kernel"], "A notebook document does not identify a live kernel, environment or execution state.", "refuse_document_as_execution", "Stored outputs may be stale or untrusted."),
    ("access_style_split", ["accessibility", "visual_encoding"], "Accessibility semantics and equivalent interaction cannot be inferred from styling.", "refuse_style_as_accessibility", "Contrast alone is insufficient."),
    ("explanation_evidence_split", ["explanation_evidence"], "An explanation must link evidence; its prose is not itself proof.", "refuse_explanation_as_evidence", "Rationale and support have distinct authority."),
    ("cache_finality_split", ["client_cache", "source_finality"], "A fresh client cache does not establish that a source value is final or unrevised.", "refuse_cache_as_finality", "HTTP age and source revision policy differ."),
    ("unknown_semantics", ["semantic_query"], "Unknown metric, dimension, formula, unit, grain, time or null meaning fails closed.", "unknown_semantics", "Provider defaults are not canonical meaning."),
    ("provider_neutral", ["analytics_api", "visual_grammar"], "Provider or renderer names are never semantic dispatch keys.", "provider_name_dispatch", "Capabilities and conformance evidence are the dispatch surface."),
    ("edition_required", ["metric_binding", "content_versioning"], "Every semantic and analytical asset reference identifies an edition or governed compatible range.", "missing_edition", "Mutable latest aliases are not reproducible."),
    ("snapshot_live_explicit", ["result_contract", "live_view"], "Every result declares snapshot, live epoch, partial or unknown completeness posture.", "unknown_result_posture", "Consumers need a bounded truth claim."),
    ("loss_disclosed", ["export", "performance_budget"], "Sampling, truncation, aggregation, rasterization and format loss require prior authorization and receipts.", "undeclared_information_loss", "Convenience cannot silently reduce meaning."),
    ("partial_visible", ["dashboard_runtime", "result_contract"], "Partial view loading and partial query results are visible per view and at dashboard level.", "hidden_partial_result", "A complete frame can contain incomplete evidence."),
    ("uncertainty_non_neutral", ["uncertainty_display", "decision_handoff"], "Uncertainty encoding choices and their decision effects must be declared and reviewable.", "undisclosed_uncertainty_encoding", "Equivalent numbers can yield different decisions."),
    ("source_cut_required", ["report_snapshot", "alert_rule"], "A snapshot, alert evaluation or decision packet identifies the source/result cut used.", "missing_source_cut", "Time of rendering is not time of data."),
    ("alert_evidence", ["alert_rule"], "Alert state transitions retain the rule edition, evaluation time and evidence cut.", "unreceipted_alert_transition", "Rules and values change over time."),
    ("notification_idempotency", ["notification_delivery"], "Retries and grouping preserve alert identity and expose duplicate-delivery posture.", "unsafe_delivery_retry", "At-least-once channels may duplicate."),
    ("offline_no_escalation", ["mobile_offline", "credential_scope"], "Offline persistence never expands entitlement and expires with its declared scope.", "offline_scope_escalation", "Disconnected state is not authorization."),
    ("replay_not_guarantee", ["session_reproducibility"], "A captured replay package states compatibility and divergence; it does not promise identical results.", "false_reproducibility_claim", "Sources, libraries and runtimes can change."),
    ("annotation_target", ["annotation"], "Annotations target immutable editions or provide an explicit re-anchoring receipt.", "ambiguous_annotation_target", "Mutable coordinates create orphaned comments."),
    ("localization_no_semantic_change", ["localization"], "Formatting, translation and bidi layout do not convert units or change time/aggregation meaning.", "localization_changed_value", "Presentation locale is not semantic locale."),
    ("accessible_equivalence", ["accessibility"], "Critical analytical tasks have programmatic structure, keyboard operation and equivalent access to underlying data and state.", "inaccessible_critical_task", "A static summary is not equivalent exploration."),
    ("finite_budget", ["performance_budget"], "Runtime work has finite bounds or requires explicit continuation, degradation or refusal.", "unbounded_consumption", "Interactive consumption must remain controllable."),
    ("human_authority", ["decision_handoff"], "A recommendation cannot execute a consequential action unless the declared decision policy authorizes it.", "missing_decision_authority", "Handoff and action are separate boundaries."),
    ("telemetry_minimized", ["telemetry_privacy"], "Interaction telemetry declares purpose, minimizes payload, avoids result values by default and expires.", "excessive_telemetry", "Consumption behavior can be sensitive."),
    ("credential_attenuation", ["credential_scope"], "Embedded, export, share and offline credentials cannot exceed the initiating audience, tenant, purpose or duration.", "credential_scope_widening", "Delegation is monotonic attenuation."),
    ("map_crs", ["geospatial_portrayal"], "Map viewport, features and measures retain explicit CRS and resolution posture.", "unknown_crs", "Portrayal without spatial reference can mislead."),
    ("sort_collation", ["table_crosstab", "localization"], "Sort order declares collation, null placement and stability when order is decision-relevant.", "unknown_sort_semantics", "Locale-sensitive order varies."),
    ("archive_integrity", ["case_archive"], "Archived cases retain digests, editions, provenance and supersession without claiming eternal executability.", "unverifiable_archive", "Integrity and reproducibility are different guarantees."),
]


INVARIANTS_REFUSALS = [
    {
        "invariant_id": f"invariant.{PREFIX}.{local}", "edition": EDITION, "status": "candidate",
        "applies_to_context_refs": [cid(item) for item in contexts], "rule": rule,
        "refusal_code": refusal, "rationale": rationale,
        "fallback_law": "Only a proven equivalent offer or explicitly authorized typed degradation may proceed.",
        "evidence_refs": list(dict.fromkeys(ref for item in contexts for ref in EVIDENCE_BY_CONTEXT[cid(item)]))[:3],
    }
    for local, contexts, rule, refusal, rationale in INVARIANT_ROWS
]


INNOVATION_ROWS = [
    ("wcag22", 2024, "WCAG 2.2 adds testable criteria relevant to focus, target size, dragging and consistent help.", "Accessibility requirements become compiler-checkable constraints.", ["w3c.wcag22"]),
    ("aria12", 2023, "WAI-ARIA 1.2 advances programmatic widget and relationship semantics.", "Presentation lowering can require an accessibility-tree offer.", ["w3c.aria12"]),
    ("rich_screenreader", 2022, "Rich screen-reader visualization research organizes access around structure, navigation and description.", "Accessibility contracts extend beyond alt text to semantic exploration.", ["paper.rich_screenreader"]),
    ("semantic_description_levels", 2022, "A four-level model distinguishes chart construction, statistics, trends and contextual insight in descriptions.", "Description requirements can state semantic level instead of a boolean alternative-text flag.", ["paper.alt_text"]),
    ("olli_adapter", 2022, "Olli demonstrates toolkit-agnostic accessible tree views through adapters.", "Renderer adapters can target a common accessible presentation IR.", ["paper.olli"]),
    ("chart_reader_codesign", 2023, "Chart Reader co-designs autonomous interactive reading experiences with screen-reader users.", "Equivalent task testing becomes a qualification requirement.", ["paper.chart_reader"]),
    ("web_visualization_audit", 2023, "A large accessibility audit and user study documents persistent barriers in web visualizations.", "Provider claims require empirical task checks, not feature flags.", ["paper.web_access_audit"]),
    ("risk_representation", 2024, "Experiments show numerical and visual uncertainty representations can change decisions.", "Decision handoff receipts must retain uncertainty presentation form.", ["paper.risk_representation"]),
    ("charting_eda", 2025, "Charting EDA formalizes notebook analysis as sequences of representations and observations.", "Exploration history can distinguish constructed views from analyst observations.", ["paper.charting_eda"]),
    ("sdmx30", 2021, "SDMX 3.0 expands statistical information and exchange support with REST-centered dissemination.", "Statistical queries and disclosure metadata gain interoperable requirements.", ["sdmx.standards"]),
    ("sdmx31", 2025, "SDMX 3.1 revises information, registry, subscription and exchange specifications.", "Subscription and data-structure editions become explicit compatibility inputs.", ["sdmx.standards"]),
    ("ogc_tiles", 2022, "OGC API Tiles standardizes tileset metadata and RESTful map tile access.", "Map clients can bind tile offers by CRS, matrix set and limits.", ["ogc.tiles"]),
    ("ogc_styles", 2022, "OGC API Styles defines interoperable style resource access.", "Portrayal style becomes an identified resource rather than embedded renderer state.", ["ogc.styles"]),
    ("ogc_maps", 2024, "OGC API Maps separates server-side portrayal from raw coverages and features.", "Compiler contracts preserve map-versus-data distinctions.", ["ogc.maps"]),
    ("http_cache_revision", 2022, "RFC 9111 consolidates modern HTTP caching, freshness and validation semantics.", "Client cache decisions can be compiled independently from source finality.", ["ietf.cache"]),
    ("problem_details", 2023, "RFC 9457 standardizes machine-readable HTTP problem details.", "Analytical APIs can return typed refusal diagnostics.", ["ietf.problem"]),
    ("arrow_flight_sql", 2022, "Flight SQL standardizes high-performance database metadata, query and result transport over Arrow Flight.", "Analytical API offers can expose typed schemas and streams without owning semantics.", ["arrow.flight_sql"]),
    ("adbc", 2023, "ADBC introduces a provider-neutral Arrow-native database driver contract.", "Runtime libraries can bind drivers by capabilities rather than product branches.", ["arrow.adbc"]),
    ("vegalite_parameters", 2021, "Vega-Lite consolidates dynamic variables and selections as parameters.", "Interaction state and data predicates can share explicit typed references while remaining distinct.", ["vegalite.selection"]),
    ("observable_framework", 2024, "Observable Framework compiles data apps and dashboards from source-controlled pages and data loaders.", "Static asset generation and live client state can be modeled as separate stages.", ["observable.framework"]),
    ("service_worker_updates", 2025, "The Service Workers specification continues to formalize programmable request interception and offline caching.", "Offline offers must declare cache control, lifecycle and fallback behavior.", ["w3c.service_workers"]),
    ("indexeddb3", 2025, "IndexedDB 3.0 advances transactional browser storage specification maturity.", "Offline state can bind to a qualified transactional local-store offer.", ["w3c.indexeddb3"]),
    ("pointer_events3", 2025, "Pointer Events Level 3 advances device-neutral input and high-frequency/predicted event handling.", "Raw pointer features remain below semantic interaction intent.", ["w3c.pointer_events3"]),
    ("dcat3", 2024, "DCAT 3 expands catalog modeling for datasets, distributions and data services.", "Analytical assets and access services can be discovered through typed catalog projections.", ["w3c.dcat3"]),
    ("rocrate11", 2022, "RO-Crate 1.1 provides a lightweight package for research objects and contextual metadata.", "Session and case archives can package artifacts without claiming deterministic replay.", ["rocrate.spec"]),
    ("ecma402_2026", 2026, "ECMA-402 2026 expands standardized locale-sensitive formatting behavior.", "Localization lowering can bind resolved locale options and disclose implementation-dependent variance.", ["ecma.intl"]),
]


INNOVATIONS = [
    {
        "innovation_id": f"innovation.{PREFIX}.{local}", "edition": EDITION, "status": "candidate",
        "year": year, "non_llm": True, "advance": advance, "compiler_consequence": consequence,
        "maturity": "standard_or_primary_research_candidate", "evidence_refs": [sid(item) for item in evidence],
        "limits": ["Evidence is source-scoped; implementation conformance is not implied."],
    }
    for local, year, advance, consequence, evidence in INNOVATION_ROWS
]


GAP_ROWS = [
    ("semantic_query_interchange", "semantic_query", "No single open semantic-query interchange fully covers governed metrics, dimensions, time, policies and calculation editions.", "high"),
    ("olap_total_semantics", "olap_model", "MDX/XMLA implementation differences need conformance fixtures for nulls, totals, calculated members and ordering.", "high"),
    ("pivot_accessibility", "pivot_spec", "Accessible semantics for deeply nested pivot headers and virtualized cells lack one interoperable profile.", "high"),
    ("dashboard_case_boundary", "analytical_case", "Global ownership adjudication is needed where a dashboard stores case-like notes and decisions.", "medium"),
    ("report_pagination", "report_definition", "Provider-neutral pagination and widow/orphan rules for analytical reports need a stronger contract.", "medium"),
    ("grammar_conformance", "visual_grammar", "Cross-renderer equivalence for transforms, scales, text metrics and interaction is incompletely tested.", "high"),
    ("encoding_ethics", "visual_encoding", "No closed rule set can establish that an encoding is decision-neutral for every audience.", "high"),
    ("uncertainty_task_fit", "uncertainty_display", "Task- and audience-specific qualification of uncertainty displays remains empirical.", "high"),
    ("accessible_complex_views", "accessibility", "Equivalent nonvisual navigation for dense networks, maps, Sankey and animated views remains uneven.", "high"),
    ("accessible_virtualization", "table_crosstab", "Assistive-technology behavior across virtualized analytical tables needs provider qualification.", "high"),
    ("map_accessibility", "geospatial_portrayal", "Interoperable semantic navigation of spatial layers and topology is unresolved.", "high"),
    ("notebook_hidden_state", "session_reproducibility", "Kernel memory, external services, extensions and nondeterminism prevent universal notebook replay.", "high"),
    ("notebook_trust_portability", "cell_output", "Trust/signature behavior across notebook clients and rich-output MIME handlers is incomplete.", "high"),
    ("eda_observation_schema", "exploratory_session", "A portable schema for analyst observations, hypotheses and branch rationale is immature.", "medium"),
    ("policy_explanation", "policy_projection", "Useful denial explanations can conflict with policy-confidentiality and attack-surface constraints.", "medium"),
    ("alert_missing_data", "alert_rule", "Missing, late, revised and backfilled data semantics require domain-specific rule policies.", "high"),
    ("delivery_exactly_once", "notification_delivery", "Exactly-once human notification is generally unavailable across heterogeneous channels.", "high"),
    ("subscription_consent", "subscription", "Consent, retention and channel rules vary by jurisdiction and enterprise policy.", "high"),
    ("embed_isolation", "embedded_analytics", "Browser, native and server embedding expose different isolation and credential risks.", "high"),
    ("api_cancellation", "analytics_api", "Cancellation and partial-result behavior is not uniform across analytical transports.", "medium"),
    ("export_formula_portability", "export", "Spreadsheet formulas, locale formatting and semantic types are not losslessly portable.", "high"),
    ("share_revocation", "governed_sharing", "Revocation cannot recall prior screenshots, downloads or derived copies.", "high"),
    ("annotation_reanchoring", "annotation", "Robust selectors across changing data, layouts and asset editions remain unresolved.", "medium"),
    ("bidi_chart_layout", "localization", "Bidirectional mixed-script chart labels and collision avoidance need renderer-specific qualification.", "medium"),
    ("offline_conflicts", "mobile_offline", "Semantic merge policies for offline parameters, notes and acknowledgements are domain-dependent.", "high"),
    ("state_migration", "interaction_state", "Presentation-state migration across changed semantic and dashboard editions is only partially automatable.", "medium"),
    ("cache_partitioning", "client_cache", "Shared/private cache partitioning and authorization changes create subtle disclosure hazards.", "high"),
    ("source_revision", "source_finality", "Statistical revisions, corrections and late events require source-specific finality classes.", "high"),
    ("decision_effect", "decision_handoff", "No generic compiler can establish whether a presentation changed a human decision appropriately.", "high"),
    ("telemetry_reidentification", "telemetry_privacy", "Sparse interaction traces can remain identifying after field removal.", "high"),
]


GAPS = [
    {
        "gap_id": f"gap.{PREFIX}.{local}", "edition": EDITION, "status": "candidate",
        "context_ref": cid(context_local), "question": question, "risk": risk,
        "compiler_posture": "emit_typed_gap_and_refuse_or_request_human_policy",
        "closure_evidence_required": ["normative contract or scoped empirical study", "conformance fixtures", "independent review"],
        "evidence_refs": EVIDENCE_BY_CONTEXT[cid(context_local)][:2],
    }
    for local, context_local, question, risk in GAP_ROWS
]


METAMODEL = {
    "metamodel_id": "san.consumption-bi-visualization-universe",
    "edition": EDITION,
    "status": "candidate_research_contract",
    "completion_claim": False,
    "scope": "Horizontal analytical consumption from semantic query intent to human decision handoff, independent of any UI application or vendor product.",
    "core_method_posture": "Deterministic typed contracts, algebras, state machines and qualified runtimes; generative methods are outside the core.",
    "decomposition": [
        "semantic intent and analytical case",
        "query/result exchange",
        "presentation grammar and contracts",
        "interaction intent and state",
        "dashboard/report/notebook composition",
        "governed delivery, sharing and collaboration",
        "accessibility, localization and offline consumption",
        "freshness, disclosure, reproducibility and decision handoff",
    ],
    "identity_splits": [
        {"left": "semantic meaning", "right": "visual encoding", "law": "encoding references but never owns metric, field, unit, time or aggregation meaning"},
        {"left": "query result", "right": "presentation state", "law": "rows/cells and selections/focus/viewports have separate identities and editions"},
        {"left": "dashboard", "right": "analytical case", "law": "a reusable surface does not replace question/evidence/decision provenance"},
        {"left": "report snapshot", "right": "live view", "law": "immutable data cut and changing stream epoch never share one completeness claim"},
        {"left": "alert rule", "right": "notification delivery", "law": "evaluation state and transport state advance independently"},
        {"left": "export", "right": "governed sharing", "law": "serialized bytes do not imply revocable continuing access"},
        {"left": "notebook document", "right": "execution kernel", "law": "cells and stored outputs do not identify process, environment or current memory"},
        {"left": "accessibility semantics", "right": "styling", "law": "equivalent structure/navigation is not inferred from color, theme or alt text alone"},
        {"left": "explanation", "right": "evidence", "law": "prose links inspectable support but is not proof"},
        {"left": "client cache freshness", "right": "source finality", "law": "representation age and source correction posture remain independent"},
    ],
    "compiler_flow": [
        "parse consumption intent", "resolve semantic and asset editions", "type result and presentation requirements",
        "separate semantic, presentation and runtime state", "project governance/security/privacy",
        "match evidence-backed capability offers", "lower to pure presentation/interaction IR",
        "bind finite runtime libraries", "execute or render", "emit result, state, freshness, loss and decision receipts",
    ],
    "guarantee_lattices": {
        "result": ["complete_snapshot", "watermark_complete", "bounded_partial", "live_epoch", "unknown"],
        "freshness": ["source_final_declared", "source_provisional", "representation_fresh", "representation_stale", "offline_unknown"],
        "accessibility": ["task_equivalent_qualified", "programmatic_structure_only", "text_summary_only", "unknown"],
        "reproducibility": ["verified_replay_equivalent", "environment_qualified", "package_complete_unverified", "best_effort", "unknown"],
    },
    "unknown_law": "Unknown owner, semantics, edition, authority, freshness, loss, accessibility or capability becomes a typed gap and fails closed.",
    "candidate_law": "Every finite registry is a candidate research seed; a count never establishes universal completeness or provider conformance.",
}


def id_schema(pattern: str = r"^[a-z][a-z0-9_-]*(\.[a-z0-9_-]+)+$") -> dict[str, Any]:
    return {"type": "string", "pattern": pattern}


STR = {"type": "string", "minLength": 1}
ARR_STR = {"type": "array", "items": STR, "minItems": 1, "uniqueItems": True}
STATUS = {"type": "string", "enum": ["candidate", "candidate_evidence"]}
NULLABLE_STR = {"type": ["string", "null"]}
OPERATION_SCHEMA = {
    "type": "object", "additionalProperties": False,
    "properties": {
        "operation_ref": STR, "name": STR, "input_types": ARR_STR, "output_type": STR,
        "purity": {"enum": ["pure", "effectful_explicit", "unresolved_refuse"]},
        "effect_intent_type": NULLABLE_STR, "receipt_type": NULLABLE_STR,
        "refusal_types": ARR_STR,
    },
    "required": ["operation_ref", "name", "input_types", "output_type", "purity", "effect_intent_type", "receipt_type", "refusal_types"],
}


def object_schema(title: str, properties: dict[str, Any], required: list[str]) -> dict[str, Any]:
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "title": title, "type": "object", "additionalProperties": False,
        "properties": properties, "required": required,
    }


SCHEMAS = {
    "source.schema.json": object_schema("Consumption evidence source", {
        "source_id": id_schema(), "edition": {"type": "integer", "minimum": 1}, "status": {"const": "candidate_evidence"},
        "title": STR, "publisher": STR,
        "source_kind": {"enum": ["standard", "official_spec", "official_docs", "official_implementation", "paper"]},
        "url": {"type": "string", "format": "uri"}, "publication_year": {"type": "integer", "minimum": 1900, "maximum": 2026},
        "accessed_at": {"type": "string", "format": "date"}, "supports_topics": ARR_STR,
        "authority_scope": STR, "limitations": ARR_STR,
    }, ["source_id", "edition", "status", "title", "publisher", "source_kind", "url", "publication_year", "accessed_at", "supports_topics", "authority_scope", "limitations"]),
    "context.schema.json": object_schema("Consumption bounded-context candidate", {
        "context_id": id_schema(), "edition": {"type": "integer", "minimum": 1}, "status": {"const": "candidate"},
        "family": STR, "name": STR, "owns": STR, "outside": ARR_STR, "invariants": ARR_STR,
        "capability_refs": ARR_STR, "decision_refs": ARR_STR, "evidence_refs": ARR_STR,
        "cross_plane_refs": ARR_STR, "candidate_limits": ARR_STR,
    }, ["context_id", "edition", "status", "family", "name", "owns", "outside", "invariants", "capability_refs", "decision_refs", "evidence_refs", "cross_plane_refs", "candidate_limits"]),
    "capability.schema.json": object_schema("Typed consumption capability", {
        "capability_id": id_schema(), "edition": {"type": "integer", "minimum": 1}, "status": {"const": "candidate"},
        "context_ref": id_schema(), "family": STR, "kind": {"const": "typed_operation"}, "name": STR, "meaning": STR,
        "typed_inputs": ARR_STR, "typed_outputs": ARR_STR, "preconditions": ARR_STR, "postconditions": ARR_STR,
        "effects": STR, "determinism": STR, "information_loss": STR, "batch_live_posture": STR,
        "decision_refs": ARR_STR, "evidence_refs": ARR_STR, "refusals": ARR_STR,
    }, ["capability_id", "edition", "status", "context_ref", "family", "kind", "name", "meaning", "typed_inputs", "typed_outputs", "preconditions", "postconditions", "effects", "determinism", "information_loss", "batch_live_posture", "decision_refs", "evidence_refs", "refusals"]),
    "contract.schema.json": object_schema("Presentation or interaction contract", {
        "contract_id": id_schema(), "edition": {"type": "integer", "minimum": 1}, "status": {"const": "candidate"},
        "contract_kind": {"enum": ["presentation", "interaction"]}, "owner_context_ref": id_schema(), "name": STR,
        "meaning": STR, "contract_fields": ARR_STR, "distinction_preserved": STR, "state_transition": ARR_STR,
        "invariants": ARR_STR, "refusals": ARR_STR, "evidence_refs": ARR_STR,
    }, ["contract_id", "edition", "status", "contract_kind", "owner_context_ref", "name", "contract_fields", "invariants", "refusals", "evidence_refs"]),
    "decision.schema.json": object_schema("Consumption decision point", {
        "decision_id": id_schema(), "edition": {"type": "integer", "minimum": 1}, "status": {"const": "candidate"},
        "context_ref": id_schema(), "question": STR, "options": ARR_STR, "required_inputs": ARR_STR,
        "default_policy": STR, "decision_receipt": ARR_STR, "evidence_refs": ARR_STR,
    }, ["decision_id", "edition", "status", "context_ref", "question", "options", "required_inputs", "default_policy", "decision_receipt", "evidence_refs"]),
    "binding.schema.json": object_schema("Requirement/offer binding", {
        "binding_id": id_schema(), "edition": {"type": "integer", "minimum": 1}, "status": {"const": "candidate"},
        "context_ref": id_schema(), "requirement": {"type": "object"}, "offer_contract": {"type": "object"},
        "match_keys": ARR_STR, "success_receipt": ARR_STR, "refusal": STR, "evidence_refs": ARR_STR,
    }, ["binding_id", "edition", "status", "context_ref", "requirement", "offer_contract", "match_keys", "success_receipt", "refusal", "evidence_refs"]),
    "compiler-mapping.schema.json": object_schema("Consumption compiler mapping", {
        "mapping_id": id_schema(), "edition": {"type": "integer", "minimum": 1}, "status": {"const": "candidate"},
        "intent_class": STR, "consulted_context_refs": ARR_STR, "target_runtime": STR, "lowering_steps": ARR_STR,
        "emitted_requirements": ARR_STR, "success_receipt": ARR_STR, "refusal_codes": ARR_STR, "evidence_refs": ARR_STR,
    }, ["mapping_id", "edition", "status", "intent_class", "consulted_context_refs", "target_runtime", "lowering_steps", "emitted_requirements", "success_receipt", "refusal_codes", "evidence_refs"]),
    "library-boundary.schema.json": object_schema("Consumption library boundary", {
        "library_id": id_schema(), "edition": {"type": "integer", "minimum": 1}, "status": {"const": "candidate"},
        "layer": {"enum": ["pure", "runtime"]}, "responsibility": STR, "contributes_to_context_refs": ARR_STR,
        "capability_refs": ARR_STR, "input_contracts": ARR_STR, "output_contracts": ARR_STR,
        "forbidden_ownership": ARR_STR, "determinism_posture": STR, "evidence_refs": ARR_STR,
        "semantic_owner_ref": id_schema(), "effect_boundary": {"enum": ["pure_no_io", "pure_effect_intents", "effectful_runtime"]},
        "public_types": ARR_STR, "public_traits": ARR_STR, "input_types": ARR_STR, "output_types": ARR_STR,
        "error_contracts": ARR_STR, "operations": {"type": "array", "minItems": 1, "items": OPERATION_SCHEMA},
        "laws": ARR_STR, "oracles": ARR_STR,
    }, ["library_id", "edition", "status", "layer", "responsibility", "contributes_to_context_refs", "capability_refs", "input_contracts", "output_contracts", "forbidden_ownership", "determinism_posture", "evidence_refs"]),
    "retired-library-composition.schema.json": object_schema("Retired composite library boundary", {
        "decision_id": id_schema(), "retired_library_id": id_schema(), "edition": {"type": "integer", "minimum": 1},
        "status": {"const": "retired_composition"}, "reason": STR, "replacement_library_refs": ARR_STR,
        "capability_partition": {"type": "object", "minProperties": 1, "additionalProperties": ARR_STR},
        "delegated_capability_refs": ARR_STR, "delegated_authority_refs": ARR_STR,
        "no_compatibility_alias": {"const": True}, "evidence_refs": ARR_STR,
    }, ["decision_id", "retired_library_id", "edition", "status", "reason", "replacement_library_refs", "capability_partition", "delegated_capability_refs", "delegated_authority_refs", "no_compatibility_alias", "evidence_refs"]),
    "cross-map.schema.json": object_schema("Cross-domain mapping", {
        "cross_map_id": id_schema(), "edition": {"type": "integer", "minimum": 1}, "status": {"const": "candidate"},
        "local_context_ref": id_schema(), "external_domain": STR, "relationship": STR, "preserved_distinction": STR,
        "compiler_exchange": ARR_STR, "evidence_refs": ARR_STR,
    }, ["cross_map_id", "edition", "status", "local_context_ref", "external_domain", "relationship", "preserved_distinction", "compiler_exchange", "evidence_refs"]),
    "invariant-refusal.schema.json": object_schema("Constitutional invariant and refusal", {
        "invariant_id": id_schema(), "edition": {"type": "integer", "minimum": 1}, "status": {"const": "candidate"},
        "applies_to_context_refs": ARR_STR, "rule": STR, "refusal_code": STR, "rationale": STR,
        "fallback_law": STR, "evidence_refs": ARR_STR,
    }, ["invariant_id", "edition", "status", "applies_to_context_refs", "rule", "refusal_code", "rationale", "fallback_law", "evidence_refs"]),
    "innovation.schema.json": object_schema("Recent non-generative innovation", {
        "innovation_id": id_schema(), "edition": {"type": "integer", "minimum": 1}, "status": {"const": "candidate"},
        "year": {"type": "integer", "minimum": 2021, "maximum": 2026}, "non_llm": {"const": True},
        "advance": STR, "compiler_consequence": STR, "maturity": STR, "evidence_refs": ARR_STR, "limits": ARR_STR,
    }, ["innovation_id", "edition", "status", "year", "non_llm", "advance", "compiler_consequence", "maturity", "evidence_refs", "limits"]),
    "gap.schema.json": object_schema("Open consumption gap", {
        "gap_id": id_schema(), "edition": {"type": "integer", "minimum": 1}, "status": {"const": "candidate"},
        "context_ref": id_schema(), "question": STR, "risk": {"enum": ["medium", "high"]},
        "compiler_posture": STR, "closure_evidence_required": ARR_STR, "evidence_refs": ARR_STR,
    }, ["gap_id", "edition", "status", "context_ref", "question", "risk", "compiler_posture", "closure_evidence_required", "evidence_refs"]),
}


REGISTRIES = {
    "sources.jsonl": (SOURCES, "source_id", "source.schema.json"),
    "context-candidates.jsonl": (CONTEXTS, "context_id", "context.schema.json"),
    "capabilities.jsonl": (CAPABILITIES, "capability_id", "capability.schema.json"),
    "presentation-contracts.jsonl": (PRESENTATION_CONTRACTS, "contract_id", "contract.schema.json"),
    "interaction-contracts.jsonl": (INTERACTION_CONTRACTS, "contract_id", "contract.schema.json"),
    "decision-points.jsonl": (DECISIONS, "decision_id", "decision.schema.json"),
    "requirements-offers-bindings.jsonl": (REQUIREMENT_OFFER_BINDINGS, "binding_id", "binding.schema.json"),
    "compiler-mappings.jsonl": (COMPILER_MAPPINGS, "mapping_id", "compiler-mapping.schema.json"),
    "library-boundaries.jsonl": (LIBRARIES, "library_id", "library-boundary.schema.json"),
    "retired-library-compositions.jsonl": (RETIRED_LIBRARY_COMPOSITIONS, "decision_id", "retired-library-composition.schema.json"),
    "cross-domain-mappings.jsonl": (CROSS_DOMAIN_MAPPINGS, "cross_map_id", "cross-map.schema.json"),
    "invariants-refusals.jsonl": (INVARIANTS_REFUSALS, "invariant_id", "invariant-refusal.schema.json"),
    "innovations.jsonl": (INNOVATIONS, "innovation_id", "innovation.schema.json"),
    "gaps.jsonl": (GAPS, "gap_id", "gap.schema.json"),
}


def main() -> None:
    SCHEMA.mkdir(parents=True, exist_ok=True)
    for schema_name, schema in SCHEMAS.items():
        dump_json(f"schema/{schema_name}", schema)
    for name, (records, id_field, _) in REGISTRIES.items():
        values = [record[id_field] for record in records]
        duplicates = [value for value, count in Counter(values).items() if count > 1]
        if duplicates:
            raise ValueError(f"{name}: duplicate {id_field}: {duplicates}")
        dump_jsonl(name, records)

    counts = {
        "sources": len(SOURCES), "bounded_context_candidates": len(CONTEXTS),
        "capabilities_operations": len(CAPABILITIES), "presentation_contracts": len(PRESENTATION_CONTRACTS),
        "interaction_contracts": len(INTERACTION_CONTRACTS), "decision_points": len(DECISIONS),
        "requirements_offer_bindings": len(REQUIREMENT_OFFER_BINDINGS),
        "compiler_mappings": len(COMPILER_MAPPINGS), "library_boundaries": len(LIBRARIES),
        "retired_library_compositions": len(RETIRED_LIBRARY_COMPOSITIONS),
        "cross_domain_mappings": len(CROSS_DOMAIN_MAPPINGS), "invariants_refusals": len(INVARIANTS_REFUSALS),
        "innovations_2021_2026": len(INNOVATIONS), "open_gaps": len(GAPS),
    }
    dump_json("metamodel.json", METAMODEL)
    dump_json("manifest.json", {
        "universe_id": "consumption_bi_visualization", "edition": EDITION,
        "status": "candidate", "generated_at": ACCESSED, "completion_claim": False,
        "generator": "build_corpus.py", "validator": "validate_corpus.py", "counts": counts,
        "schema_files": sorted(SCHEMAS), "registry_files": sorted(REGISTRIES),
        "coverage_posture": "Open-world candidate saturation; unknowns extend through typed gaps.",
        "core_exclusions": ["generative methods", "vendor feature survey", "UI application implementation"],
    })
    dump_json("coverage-report.json", {
        "universe_id": "consumption_bi_visualization", "edition": EDITION, "status": "candidate",
        "counts": counts,
        "thresholds": {"sources_min": 45, "contexts_min": 35, "capabilities_operations_decisions_min": 150, "innovations_min": 20},
        "threshold_results": {
            "sources": len(SOURCES) >= 45, "contexts": len(CONTEXTS) >= 35,
            "capabilities_operations_decisions": len(CAPABILITIES) + len(DECISIONS) >= 150,
            "innovations": len(INNOVATIONS) >= 20,
        },
        "families": dict(sorted(Counter(context["family"] for context in CONTEXTS).items())),
        "library_layers": dict(sorted(Counter(library["layer"] for library in LIBRARIES).items())),
        "source_kinds": dict(sorted(Counter(source["source_kind"] for source in SOURCES).items())),
        "honest_limits": [
            "The universe is open and cannot prove enumeration completeness.",
            "Source review does not qualify any provider implementation.",
            "Accessibility and decision effects require human empirical evaluation.",
            "Cross-context ownership remains candidate until atlas adjudication.",
        ],
    })
    print("generated " + ", ".join(f"{key}={value}" for key, value in counts.items()))


if __name__ == "__main__":
    main()
