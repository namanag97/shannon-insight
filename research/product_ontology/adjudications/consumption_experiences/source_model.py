#!/usr/bin/env python3
"""Canonical declarative source for consumption-experience product adjudication."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from remaining_product_enrichment import enrich_remaining_consumption_products


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "source.json"


def evidence(
    ident: str,
    title: str,
    publisher: str,
    uri: str,
    claim: str,
    limit: str,
    source_class: str = "official_specification_or_documentation",
) -> dict[str, Any]:
    return {
        "source_id": ident,
        "source_class": source_class,
        "title": title,
        "publisher": publisher,
        "uri": uri,
        "retrieved_at": "2026-08-26",
        "claim": claim,
        "scope_limit": limit,
    }


def artifact(
    ident: str,
    kind: str,
    name: str,
    status: str,
    definition: str,
    refs: list[str],
    owner: str | None = None,
    adoption: bool = False,
    operated: bool = False,
) -> dict[str, Any]:
    return {
        "artifact_id": ident,
        "kind": kind,
        "name": name,
        "status": status,
        "semantic_owner_ref": owner,
        "adoption_unit": adoption,
        "operated": operated,
        "definition": definition,
        "evidence_refs": refs,
    }


AXES = [
    "user", "job", "adoption", "semantics", "authority",
    "lifecycle", "operation", "economics", "interface", "market_evidence",
]


def split(scores: list[int], refs: list[str], subject: str) -> dict[str, Any]:
    findings = {
        "user": f"{subject} has a distinguishable consumer or operator role.",
        "job": f"{subject} owns a bounded outcome rather than a feature name.",
        "adoption": f"{subject} can be adopted or removed through a versioned interface.",
        "semantics": f"{subject} owns named meanings but imports metric and source truth.",
        "authority": f"{subject} has explicit authoring or delivery authority boundaries.",
        "lifecycle": f"{subject} has version, migration, deprecation and exit state.",
        "operation": f"{subject} has an independently observable runtime or service envelope.",
        "economics": f"{subject} can be costed independently where operated.",
        "interface": f"{subject} exposes a provider-neutral document, API or protocol boundary.",
        "market_evidence": f"{subject} is demonstrated by independently documented implementations.",
    }
    return {
        axis: {"score": score, "finding": findings[axis], "evidence_refs": refs}
        for axis, score in zip(AXES, scores, strict=True)
    }


def library(
    ident: str,
    owner: str,
    provides: list[str],
    types: list[str],
    operations: list[str],
    decisions: list[str],
    invariants: list[str],
    refusals: list[str],
    dependencies: list[str],
    effect: str,
    refs: list[str],
    cls: str = "semantic_pure",
) -> dict[str, Any]:
    return {
        "library_id": ident,
        "class": cls,
        "owner_ref": owner,
        "provides": provides,
        "types": types,
        "operations": operations,
        "decisions": decisions,
        "invariants": invariants,
        "refusals": refusals,
        "dependencies": dependencies,
        "effect_boundary": effect,
        "evidence_refs": refs,
    }


def source() -> dict[str, Any]:
    sources = [
        evidence("evidence.w3c.wcag22", "Web Content Accessibility Guidelines 2.2", "W3C", "https://www.w3.org/TR/WCAG22/", "Defines testable accessibility requirements for perceivable, operable, understandable and robust Web content.", "Conformance does not prove task-specific equivalent analytical understanding."),
        evidence("evidence.w3c.aria12", "Accessible Rich Internet Applications 1.2", "W3C", "https://www.w3.org/TR/wai-aria-1.2/", "Defines roles, states and properties that expose interface semantics to accessibility APIs.", "ARIA cannot repair missing interaction semantics or establish analytical correctness."),
        evidence("evidence.w3c.graphics_aria", "WAI-ARIA Graphics Module", "W3C", "https://www.w3.org/TR/graphics-aria-1.0/", "Defines roles for structured graphical documents and graphics objects.", "A role mapping alone does not establish equivalent navigation or interpretation."),
        evidence("evidence.vega.spec", "Vega Specification", "Vega Project", "https://vega.github.io/vega/docs/specification/", "Defines a declarative visualization grammar compiled into a reactive dataflow and scenegraph.", "A visualization grammar is a library/interface contract, not an operated BI product."),
        evidence("evidence.vega.signals", "Vega Signals", "Vega Project", "https://vega.github.io/vega/docs/signals/", "Defines dynamic variables that parameterize visualization state and interaction.", "Signal state is presentation state, not source data or business meaning."),
        evidence("evidence.vegalite.spec", "Vega-Lite View Specification", "Vega-Lite Project", "https://vega.github.io/vega-lite/docs/spec.html", "Defines JSON view and composition specifications compiled to lower-level Vega.", "Compilation does not validate metric semantics, audience fitness or source truth."),
        evidence("evidence.vegalite.selection", "Vega-Lite Selection Parameters", "Vega-Lite Project", "https://vega.github.io/vega-lite/docs/selection.html", "Defines point and interval selections and their use as predicates and parameters.", "A visual selection is not automatically an authorized domain command."),
        evidence("evidence.observable.plot", "Observable Plot documentation", "Observable", "https://observablehq.com/plot/", "Documents a composable JavaScript plotting library with marks, scales, transforms and facets.", "A plotting implementation does not create report governance or product adoption boundaries."),
        evidence("evidence.observable.runtime", "Observable Runtime", "Observable", "https://github.com/observablehq/runtime", "Documents a dataflow runtime for reactive variables and modules.", "Reactive execution is not notebook reproducibility, query authority or business workflow authority."),
        evidence("evidence.jupyter.nbformat", "The Notebook file format", "Project Jupyter", "https://nbformat.readthedocs.io/en/latest/format_description.html", "Defines versioned JSON notebook documents, cells, metadata and stored rich outputs.", "A notebook document is not the kernel process, environment, execution order or reproducibility proof."),
        evidence("evidence.jupyter.messaging", "Jupyter Messaging Protocol", "Project Jupyter", "https://jupyter-client.readthedocs.io/en/latest/messaging.html", "Defines authenticated message channels and request/reply/publication semantics between clients and kernels.", "Protocol conformance does not qualify a kernel, environment or notebook result."),
        evidence("evidence.jupyter.kernels", "Making kernels for Jupyter", "Project Jupyter", "https://jupyter-client.readthedocs.io/en/latest/kernels.html", "Documents kernel discovery, process launch and connection-file behavior.", "Kernel launch does not prove cell determinism, environment capture or safe effects."),
        evidence("evidence.jupyter.widgets", "Jupyter Widgets protocol", "Project Jupyter", "https://ipywidgets.readthedocs.io/en/latest/examples/Widget%20Custom.html#Comms", "Defines comm-based synchronization of widget state between kernel and front end.", "Widget state is not business object identity or durable application state."),
        evidence("evidence.jupyter.security", "Security in Jupyter notebooks", "Project Jupyter", "https://jupyter-notebook.readthedocs.io/en/stable/security.html", "Documents notebook trust and sanitization behavior for stored outputs.", "Notebook trust does not authorize code execution or prove output provenance."),
        evidence("evidence.superset.embedded", "Embedding Superset", "Apache Superset", "https://superset.apache.org/user-docs/using-superset/embedding/", "Documents embedding dashboards using a client SDK, allowed origins and guest tokens.", "An iframe or guest token is not sufficient evidence of tenant isolation, semantic portability or host-action authority."),
        evidence("evidence.superset.alerts", "Alerts and Reports", "Apache Superset", "https://superset.apache.org/docs/configuration/alerts-reports/", "Documents scheduled queries, reports and alert delivery through configured workers and channels.", "Bundled scheduling does not collapse alert-state, report-snapshot and notification-delivery semantics."),
        evidence("evidence.powerbi.overview", "Power BI documentation", "Microsoft", "https://learn.microsoft.com/en-us/power-bi/", "Separates semantic models, reports, dashboards, authoring, viewing, sharing and administration roles.", "One provider suite does not determine provider-neutral product or semantic boundaries."),
        evidence("evidence.powerbi.embedded", "Power BI embedded analytics documentation", "Microsoft", "https://learn.microsoft.com/en-us/power-bi/developer/embedded/", "Documents embedding APIs, multitenancy, permissions, capacity planning and production operation.", "Provider documentation does not prove portable embedding or qualify a deployment occurrence."),
        evidence("evidence.powerbi.export", "Export data from a Power BI visualization", "Microsoft", "https://learn.microsoft.com/en-us/power-bi/visuals/power-bi-visualization-export-data", "Documents permission-sensitive export modes, limits and sensitivity-label behavior.", "Exported bytes are a new disclosure occurrence and do not retain live-view revocation semantics."),
        evidence("evidence.powerbi.subscription", "Email subscriptions for reports and dashboards", "Microsoft", "https://learn.microsoft.com/en-us/power-bi/collaborate-share/end-user-subscribe", "Documents scheduled report/dashboard snapshots, recipients, licensing, RLS considerations and delivery limits.", "A delivery receipt does not prove recipient comprehension, current source finality or authorized downstream use."),
        evidence("evidence.prometheus.alertmanager", "Prometheus Alertmanager overview", "Prometheus", "https://prometheus.io/docs/alerting/latest/overview/", "Separates alert generation from grouping, inhibition, silencing and routing notifications to receivers.", "Operational alert routing does not own the analytical condition or report semantics."),
        evidence("evidence.grafana.notifications", "Grafana notification policies", "Grafana Labs", "https://grafana.com/docs/grafana/latest/alerting/fundamentals/notifications/notification-policies/", "Defines label-based routing trees, grouping and delivery through contact points.", "A routing policy does not prove that an analytical alert condition is meaningful or actionable."),
        evidence("evidence.grafana.export", "Export alerting resources", "Grafana Labs", "https://grafana.com/docs/grafana/latest/alerting/set-up/provision-alerting-resources/export-alerting-resources/", "Documents JSON, YAML and Terraform export surfaces and their edit/overwrite limitations.", "Configuration export does not prove cross-provider semantic equivalence or lossless migration."),
        evidence("evidence.knock.workflows", "Workflows", "Knock", "https://docs.knock.app/concepts/workflows", "Documents an independently operated notification workflow lifecycle with triggers, steps, conditions, batching and channel delivery.", "Notification orchestration does not own the triggering analytical condition, content meaning or business disposition."),
        evidence("evidence.knock.preferences", "Preferences", "Knock", "https://docs.knock.app/concepts/preferences", "Documents recipient and tenant preference evaluation independently of the producing application.", "Preferences do not grant legal purpose, identity, disclosure or business authority."),
        evidence("evidence.novu.workflow_api", "Create a workflow", "Novu", "https://docs.novu.co/api-reference/workflows/create-a-workflow", "A second independent platform exposes notification workflow create, retrieve, update, delete and preview surfaces.", "Provider API shape is adoption evidence, not a selected portable semantic contract."),
        evidence("evidence.oasis.openformula", "OpenDocument 1.4 Part 4: OpenFormula", "OASIS", "https://docs.oasis-open.org/office/OpenDocument/v1.4/os/part4-formula/OpenDocument-v1.4-os-part4-formula.html", "Defines recalculated spreadsheet formula syntax and semantics under an exact standard edition.", "Formula interchange does not establish workbook governance, recalculation equivalence or external-data provenance."),
        evidence("evidence.unicode.cldr", "Unicode Common Locale Data Repository", "Unicode Consortium", "https://cldr.unicode.org/", "Publishes versioned locale data used for number, date, unit, currency and language presentation.", "Locale formatting cannot change underlying semantic quantities, instants or values."),
        evidence("evidence.unicode.uts35", "Unicode Technical Standard 35", "Unicode Consortium", "https://www.unicode.org/reports/tr35/", "Defines locale data markup and formatting behavior used by internationalized applications.", "A locale profile is not a timezone, calendar or measurement-system policy by implication."),
        evidence("evidence.paper.nested_model", "A Nested Model for Visualization Design and Validation", "IEEE TVCG", "https://doi.org/10.1109/TVCG.2009.111", "Separates domain problem, data/task abstraction, visual encoding/interaction and algorithm validation levels.", "The framework guides validation but does not qualify a particular product or design.", "primary_research"),
        evidence("evidence.paper.olli", "Olli: An Extensible Visualization Library for Screen Reader Accessibility", "IEEE VIS", "https://vis.csail.mit.edu/pubs/olli/", "Demonstrates a structured accessible visualization adapter and navigation model.", "One evaluation does not prove universal accessibility across tasks and audiences.", "primary_research"),
        evidence("evidence.paper.jupyter_repro", "A Large-Scale Study about Quality and Reproducibility of Jupyter Notebooks", "MSR", "https://doi.org/10.1109/MSR.2019.00077", "Provides empirical evidence that notebook presence and stored output do not by themselves guarantee reproducibility.", "The sampled repositories do not establish behavior for every notebook platform.", "primary_research"),
    ]

    artifact_kinds = [
        {"kind": "architecture_pattern", "definition": "A reusable arrangement without adoption or semantic-owner identity."},
        {"kind": "suite", "definition": "Packaging of independently governed products and capabilities."},
        {"kind": "product", "definition": "An independently adopted and operated outcome promise."},
        {"kind": "presentation_artifact", "definition": "A versioned report, dashboard, widget, notebook or snapshot; not automatically a product."},
        {"kind": "capability", "definition": "Typed behavior required or offered by products and implementations."},
        {"kind": "semantic_contract", "definition": "Owner of meaning, identity, state, invariants and refusals."},
        {"kind": "standard", "definition": "An exact external edition specializing a contract."},
        {"kind": "interface", "definition": "A versioned interaction contract without an operated promise."},
        {"kind": "library_contract", "definition": "A pure or effect-bounded reusable implementation boundary."},
        {"kind": "implementation", "definition": "A concrete unqualified project or provider component."},
        {"kind": "provider_class", "definition": "A class of operated offers, never a qualified occurrence."},
        {"kind": "neighboring_product", "definition": "A product outside this slice whose authority is imported."},
        {"kind": "solution_pack", "definition": "A vertical composition carrying industry language, rules and defaults."},
    ]

    artifacts: list[dict[str, Any]] = [
        artifact("pattern.analytical_consumption", "architecture_pattern", "Analytical consumption pattern", "retain_as_composition_pattern", "Arranges governed query, presentation, interaction, delivery, notebook and decision-handoff capabilities.", ["evidence.paper.nested_model", "evidence.powerbi.overview"]),
        artifact("suite.analytics_experience", "suite", "Analytics experience suite", "suite_not_semantic_owner", "Packages BI/reporting, embedded analytics and notebooks without acquiring their imported meanings.", ["evidence.powerbi.overview", "evidence.superset.embedded"]),
        artifact("product.bi_reporting", "product", "Business intelligence and reporting experience", "strong_product_candidate", "Operated authoring, publication, viewing and governed interaction over reports and dashboards.", ["evidence.powerbi.overview", "evidence.superset.alerts"], "semantic.report_lifecycle", True, True),
        artifact("product.embedded_analytics", "product", "Embedded analytics delivery", "presumptive_product", "Operated tenant-aware delivery of analytical surfaces inside a host product with explicit identity, session and exit contracts.", ["evidence.powerbi.embedded", "evidence.superset.embedded"], "semantic.embedded_session", True, True),
        artifact("product.analytical_notebook", "product", "Reproducible analytical notebook environment", "presumptive_product", "Operated notebook document, kernel binding, execution-history and reproducibility evidence experience.", ["evidence.jupyter.nbformat", "evidence.jupyter.messaging", "evidence.paper.jupyter_repro"], "semantic.notebook_document", True, True),
        artifact("artifact.dashboard_widget", "presentation_artifact", "Dashboard widget", "reclassified_component", "A reusable presentation component within a surface; no independent product lifecycle by default.", ["evidence.vegalite.spec", "evidence.powerbi.overview"]),
        artifact("artifact.report_snapshot", "presentation_artifact", "Report snapshot", "candidate", "Immutable output bound to an exact source cut, parameters, presentation edition and export/delivery receipt.", ["evidence.powerbi.export", "evidence.powerbi.subscription"], "semantic.report_snapshot"),
        artifact("standard.jupyter_nbformat", "standard", "Jupyter nbformat", "exact_edition_required", "Versioned notebook document format.", ["evidence.jupyter.nbformat"]),
        artifact("standard.jupyter_messaging", "standard", "Jupyter messaging protocol", "exact_edition_required", "Kernel/client message protocol.", ["evidence.jupyter.messaging"]),
        artifact("standard.vega", "standard", "Vega grammar", "exact_edition_required", "Declarative visualization and reactive scenegraph grammar.", ["evidence.vega.spec"]),
        artifact("standard.vegalite", "standard", "Vega-Lite grammar", "exact_edition_required", "High-level declarative visualization grammar compiled to Vega.", ["evidence.vegalite.spec"]),
        artifact("standard.wcag22", "standard", "WCAG 2.2", "exact_edition_required", "Accessibility conformance requirements.", ["evidence.w3c.wcag22"]),
        artifact("standard.openformula14", "standard", "OpenFormula 1.4", "exact_edition_required", "Spreadsheet formula interchange semantics.", ["evidence.oasis.openformula"]),
        artifact("implementation.power_bi", "implementation", "Microsoft Power BI", "observed_unqualified", "Observed reporting, embedded, export and subscription implementation.", ["evidence.powerbi.overview", "evidence.powerbi.embedded"]),
        artifact("implementation.superset", "implementation", "Apache Superset", "observed_unqualified", "Observed dashboard, embedded and scheduled-report implementation.", ["evidence.superset.embedded", "evidence.superset.alerts"]),
        artifact("implementation.jupyter", "implementation", "Project Jupyter", "observed_unqualified", "Observed notebook format, client/kernel protocol and trust implementation family.", ["evidence.jupyter.nbformat", "evidence.jupyter.messaging"]),
        artifact("implementation.vega", "implementation", "Vega and Vega-Lite", "observed_unqualified", "Observed visualization compiler and runtime implementation.", ["evidence.vega.spec", "evidence.vegalite.spec"]),
        artifact("implementation.observable", "implementation", "Observable Plot and Runtime", "observed_unqualified", "Observed plotting and reactive-runtime implementation.", ["evidence.observable.plot", "evidence.observable.runtime"]),
        artifact("implementation.alertmanager", "implementation", "Prometheus Alertmanager", "observed_unqualified", "Observed notification grouping, inhibition and routing implementation.", ["evidence.prometheus.alertmanager"]),
        artifact("implementation.grafana_alerting", "implementation", "Grafana Alerting", "observed_unqualified", "Observed alert-state and notification policy implementation.", ["evidence.grafana.notifications", "evidence.grafana.export"]),
        artifact("provider.bi_runtime", "provider_class", "BI runtime provider", "unqualified_class", "Operates report authoring, publication, query and interactive viewing.", ["evidence.powerbi.overview"]),
        artifact("provider.embedded_runtime", "provider_class", "Embedded analytics runtime provider", "unqualified_class", "Operates tenant-scoped embedded sessions and capacity.", ["evidence.powerbi.embedded", "evidence.superset.embedded"]),
        artifact("provider.notebook_runtime", "provider_class", "Notebook runtime provider", "unqualified_class", "Operates document storage, kernels, sessions and execution environments.", ["evidence.jupyter.kernels", "evidence.jupyter.security"]),
        artifact("neighbor.semantic_metric", "neighboring_product", "Semantic and metric service", "import_only", "Owns measure, dimension, aggregation and formula meaning.", ["evidence.powerbi.overview"]),
        artifact("neighbor.query_engine", "neighboring_product", "Analytical query engine", "import_only", "Owns query execution and result receipts.", ["evidence.powerbi.overview"]),
        artifact("neighbor.identity_policy", "neighboring_product", "Identity and policy authority", "import_only", "Owns principals, permissions, delegation, purpose and disclosure decisions.", ["evidence.superset.embedded", "evidence.powerbi.export"]),
        artifact("neighbor.notification_delivery", "neighboring_product", "Notification orchestration and delivery", "strong_external_product_candidate_import_only", "Owns workflow, preference projection, channel routing, provider delivery attempts and receipts, but not analytical alert, content-subscription or business-acknowledgment meaning.", ["evidence.knock.workflows", "evidence.knock.preferences", "evidence.novu.workflow_api", "evidence.prometheus.alertmanager"]),
        artifact("neighbor.spreadsheet_application", "neighboring_product", "Spreadsheet application", "provider_outside_slice", "Owns workbook authoring and calculation runtime; governance capabilities remain separable.", ["evidence.oasis.openformula"]),
    ]

    semantics = [
        ("semantic.report_lifecycle", "Report lifecycle", "report definition, edition, publication, audience and retirement"),
        ("semantic.dashboard_definition", "Dashboard definition", "surface composition, layout, parameter and child-artifact references"),
        ("semantic.presentation_ir", "Presentation intermediate representation", "provider-neutral marks, tables, text, layout and interaction intents"),
        ("semantic.visual_encoding", "Visual encoding", "field/channel, scale, guide and mark mappings"),
        ("semantic.presentation_state", "Presentation state", "selection, focus, viewport, drill, filter and navigation state"),
        ("semantic.report_snapshot", "Report snapshot", "immutable source cut, parameter binding, presentation edition and rendered output identity"),
        ("semantic.export", "Export and disclosure", "serialized artifact, loss, label, recipient and disclosure receipt"),
        ("semantic.accessibility", "Accessibility semantics", "equivalent structure, labels, navigation, focus and interaction alternatives"),
        ("semantic.localization", "Localization semantics", "locale-data edition, formatting, language, direction and fallback"),
        ("semantic.notebook_document", "Notebook document", "cell identity, order, source, metadata and stored-output identity"),
        ("semantic.cell_output", "Notebook cell output", "execution-correlated stream, display, result and error occurrence"),
        ("semantic.kernel_session", "Kernel session", "kernel process, protocol, environment, execution count and lifecycle"),
        ("semantic.embedded_session", "Embedded analytical session", "host, tenant, principal, guest grant, resource scope and expiry"),
        ("semantic.interaction_intent", "Analytical interaction intent", "semantic selection, parameter change, drill and action proposal"),
        ("semantic.alert_rule", "Analytical alert rule", "condition, evaluation cut, threshold, hysteresis and evaluation policy"),
        ("semantic.alert_state", "Analytical alert state", "pending, firing, resolved, suppressed and acknowledged occurrences"),
        ("semantic.subscription", "Analytical content subscription", "subscriber intent, exact content, parameter/data cut, schedule and cancellation contract that emits attention intent without owning channel delivery"),
        ("semantic.spreadsheet_governance", "Spreadsheet governance", "workbook identity, formula edition, external links, recalculation and review evidence"),
    ]
    for ident, name, definition in semantics:
        refs = ["evidence.powerbi.overview"]
        if "notebook" in ident or "kernel" in ident or "cell" in ident:
            refs = ["evidence.jupyter.nbformat", "evidence.jupyter.messaging"]
        elif "visual" in ident or "presentation" in ident or "dashboard" in ident:
            refs = ["evidence.vega.spec", "evidence.vegalite.spec"]
        elif "accessibility" in ident:
            refs = ["evidence.w3c.wcag22", "evidence.w3c.aria12"]
        elif "localization" in ident:
            refs = ["evidence.unicode.cldr", "evidence.unicode.uts35"]
        elif "alert" in ident or "subscription" in ident:
            refs = ["evidence.prometheus.alertmanager", "evidence.grafana.notifications"]
        elif "spreadsheet" in ident:
            refs = ["evidence.oasis.openformula"]
        artifacts.append(artifact(ident, "semantic_contract", name, "candidate", definition, refs))

    capabilities = [
        ("capability.author_report", "Author governed report", "semantic.report_lifecycle", ["evidence.powerbi.overview"]),
        ("capability.compose_dashboard", "Compose dashboard", "semantic.dashboard_definition", ["evidence.powerbi.overview"]),
        ("capability.lower_presentation", "Lower presentation IR", "semantic.presentation_ir", ["evidence.vegalite.spec"]),
        ("capability.render_visual", "Render analytical presentation", "semantic.visual_encoding", ["evidence.vega.spec"]),
        ("capability.manage_presentation_state", "Manage presentation state", "semantic.presentation_state", ["evidence.vega.signals"]),
        ("capability.validate_accessibility", "Validate accessibility semantics", "semantic.accessibility", ["evidence.w3c.wcag22", "evidence.w3c.graphics_aria"]),
        ("capability.localize_presentation", "Localize presentation", "semantic.localization", ["evidence.unicode.cldr"]),
        ("capability.materialize_snapshot", "Materialize report snapshot", "semantic.report_snapshot", ["evidence.powerbi.subscription"]),
        ("capability.export_artifact", "Export analytical artifact", "semantic.export", ["evidence.powerbi.export"]),
        ("capability.manage_notebook", "Manage notebook document", "semantic.notebook_document", ["evidence.jupyter.nbformat"]),
        ("capability.execute_notebook", "Execute notebook cell", "semantic.kernel_session", ["evidence.jupyter.messaging", "evidence.jupyter.kernels"]),
        ("capability.embed_surface", "Embed analytical surface", "semantic.embedded_session", ["evidence.powerbi.embedded", "evidence.superset.embedded"]),
        ("capability.evaluate_alert", "Evaluate analytical alert", "semantic.alert_rule", ["evidence.superset.alerts"]),
        ("capability.transition_alert", "Transition analytical alert state", "semantic.alert_state", ["evidence.grafana.notifications"]),
        ("capability.run_subscription", "Run analytical subscription", "semantic.subscription", ["evidence.powerbi.subscription"]),
        ("capability.validate_workbook", "Validate governed workbook", "semantic.spreadsheet_governance", ["evidence.oasis.openformula"]),
    ]
    for ident, name, owner, refs in capabilities:
        artifacts.append(artifact(ident, "capability", name, "candidate", f"Typed capability owned by {owner}.", refs, owner))

    boundary_decisions = [
        {"decision_id":"decision.consumption.bi_reporting","subject_ref":"product.bi_reporting","disposition":"strong_product_candidate","rationale":"Report authors, publishers and consumers adopt an operated lifecycle distinct from metric semantics, query execution and rendering libraries.","split_test":split([2,2,2,2,2,2,2,2,2,2],["evidence.powerbi.overview","evidence.superset.alerts"],"BI/reporting"),"evidence_refs":["evidence.powerbi.overview","evidence.superset.alerts"]},
        {"decision_id":"decision.consumption.embedded","subject_ref":"product.embedded_analytics","disposition":"presumptive_product","rationale":"Host-product developers need tenant/session/capacity/support and exit semantics distinct from the report product, but portable authority allocation and provider substitution evidence remain incomplete.","split_test":split([2,2,1,2,1,2,2,1,2,1],["evidence.powerbi.embedded","evidence.superset.embedded"],"embedded analytics"),"evidence_refs":["evidence.powerbi.embedded","evidence.superset.embedded"]},
        {"decision_id":"decision.consumption.notebook","subject_ref":"product.analytical_notebook","disposition":"presumptive_product","rationale":"An operated notebook environment has a user/job/lifecycle beyond the document and kernel protocols, while repeatability and provider portability remain qualified obligations.","split_test":split([2,2,1,2,1,2,2,1,2,1],["evidence.jupyter.nbformat","evidence.jupyter.messaging","evidence.paper.jupyter_repro"],"analytical notebook"),"evidence_refs":["evidence.jupyter.nbformat","evidence.jupyter.messaging","evidence.paper.jupyter_repro"]},
        {"decision_id":"decision.consumption.visual_runtime","subject_ref":"standard.vega","disposition":"reclassify_as_library_and_runtime_offer","rationale":"A grammar/compiler/renderer is a replaceable library/runtime capability unless an independently adopted operated rendering service is evidenced.","evidence_refs":["evidence.vega.spec","evidence.vegalite.spec","evidence.observable.plot"]},
        {"decision_id":"decision.consumption.dashboard_widget","subject_ref":"artifact.dashboard_widget","disposition":"reclassify_as_presentation_artifact","rationale":"A widget has composition identity but no independent service, support, economics or exit promise by default.","evidence_refs":["evidence.vegalite.spec","evidence.powerbi.overview"]},
        {"decision_id":"decision.consumption.alert_subscription","subject_ref":"semantic.subscription","disposition":"retire_composite_keep_producer_capabilities_import_notification_product","rationale":"Alert evaluation remains with the producing analytical product, content subscription remains with its content product, notification workflow/delivery is an independently adoptable external horizontal product, and business acknowledgment/escalation remains with domain workflow owners.","evidence_refs":["evidence.prometheus.alertmanager","evidence.grafana.notifications","evidence.powerbi.subscription","evidence.knock.workflows","evidence.knock.preferences","evidence.novu.workflow_api"]},
        {"decision_id":"decision.consumption.spreadsheet_governance","subject_ref":"semantic.spreadsheet_governance","disposition":"defer_product_boundary","rationale":"Formula/workbook governance is a real semantic and library surface, but independent product adoption and operation evidence is insufficient in this slice.","evidence_refs":["evidence.oasis.openformula","evidence.powerbi.export"]},
        {"decision_id":"decision.consumption.report_metric_split","subject_ref":"semantic.report_lifecycle","disposition":"retain_split","rationale":"A report references metrics; its layout, audience and publication lifecycle cannot redefine measure meaning.","evidence_refs":["evidence.powerbi.overview","evidence.paper.nested_model"]},
        {"decision_id":"decision.consumption.notebook_kernel_split","subject_ref":"semantic.notebook_document","disposition":"retain_split","rationale":"Document cells/stored outputs are not kernel process, environment or execution history.","evidence_refs":["evidence.jupyter.nbformat","evidence.jupyter.messaging","evidence.paper.jupyter_repro"]},
        {"decision_id":"decision.consumption.embed_iframe_split","subject_ref":"semantic.embedded_session","disposition":"retain_split","rationale":"An iframe transport does not establish tenant, identity, authority, resource or exit semantics.","evidence_refs":["evidence.superset.embedded","evidence.powerbi.embedded"]},
        {"decision_id":"decision.consumption.ai_prefix","subject_ref":"pattern.analytical_consumption","disposition":"reject_ambient_ai_boundary","rationale":"Generative/model assistance is optional at declared use sites; deterministic query, presentation, authority, accessibility and delivery contracts remain authoritative.","evidence_refs":["evidence.paper.nested_model","evidence.w3c.wcag22"]},
    ]

    ownership = []
    for ident, name, _definition in semantics:
        excluded = ["neighbor.semantic_metric", "neighbor.query_engine"]
        if ident == "semantic.embedded_session":
            excluded = ["neighbor.identity_policy"]
        if ident in {"semantic.alert_rule", "semantic.alert_state", "semantic.subscription"}:
            excluded = ["neighbor.notification_delivery"]
        ownership.append({
            "meaning_id": f"meaning.{ident.removeprefix('semantic.')}",
            "term": name,
            "owner_ref": ident,
            "invariant": f"{name} identity and state cannot be inferred from provider packaging, rendered bytes or generated prose.",
            "must_not_be_owned_by": excluded,
        })

    libraries = [
        library("library.consumption.presentation_ir","semantic.presentation_ir",["capability.lower_presentation"],["PresentationIr","PresentationNode","DataBinding"],["validate_ir","lower_ir"],["grammar_edition","unknown_node_policy"],["lowering_preserves_declared_meaning","provider_identity_is_nonsemantic"],["unknown_grammar","unsupported_construct"],[],"pure_no_io",["evidence.vegalite.spec"]),
        library("library.consumption.visual_encoding","semantic.visual_encoding",["capability.render_visual"],["Mark","Channel","Scale","Guide"],["validate_encoding","compile_encoding"],["scale_domain_policy","null_encoding_policy"],["encoding_cannot_define_metric_meaning"],["invalid_channel","unknown_scale"],["library.consumption.presentation_ir"],"pure_no_io",["evidence.vega.spec","evidence.vegalite.spec"]),
        library("library.consumption.dashboard_runtime","semantic.dashboard_definition",["capability.compose_dashboard","capability.manage_presentation_state"],["DashboardDefinition","WidgetRef","PresentationState"],["compose_dashboard","reduce_interaction"],["layout_policy","state_persistence_policy"],["dashboard_is_not_analytical_case"],["unknown_widget","stale_state"],["library.consumption.presentation_ir"],"effect_intents_and_receipts",["evidence.powerbi.overview","evidence.vega.signals"],"runtime_boundary"),
        library("library.consumption.renderer_adapter","semantic.presentation_ir",["capability.render_visual"],["RenderRequest","RenderTarget","RenderReceipt"],["render"],["target_profile","degradation_policy"],["render_receipt_binds_exact_ir_and_target"],["unsupported_target","resource_exhausted"],["library.consumption.presentation_ir","library.consumption.visual_encoding"],"effect_intents_and_receipts",["evidence.vega.spec","evidence.observable.plot"],"adapter_boundary"),
        library("library.consumption.accessibility","semantic.accessibility",["capability.validate_accessibility"],["AccessibleTree","AlternativeRepresentation","ConformanceResult"],["construct_access_tree","test_equivalent_access"],["target_level","audience_profile"],["styling_is_not_accessibility","text_alternative_is_not_full_equivalence"],["missing_semantics","unverified_equivalence"],["library.consumption.presentation_ir"],"pure_no_io",["evidence.w3c.wcag22","evidence.w3c.aria12","evidence.paper.olli"]),
        library("library.consumption.localization","semantic.localization",["capability.localize_presentation"],["LocaleProfile","LocaleDataEdition","LocalizedValue"],["format_value","resolve_fallback"],["locale_data_edition","number_date_unit_policy"],["formatting_cannot_change_semantic_value"],["unknown_locale","missing_calendar"],[],"pure_no_io",["evidence.unicode.cldr","evidence.unicode.uts35"]),
        library("library.consumption.notebook_document","semantic.notebook_document",["capability.manage_notebook"],["NotebookDocument","Cell","StoredOutput","TrustState"],["validate_notebook","canonicalize_document"],["nbformat_edition","unknown_metadata_policy"],["stored_output_is_not_execution_receipt","cell_order_is_explicit"],["invalid_notebook","untrusted_output"],[],"pure_no_io",["evidence.jupyter.nbformat","evidence.jupyter.security"]),
        library("library.consumption.embedded_bridge","semantic.embedded_session",["capability.embed_surface"],["EmbedIntent","GuestGrant","HostOrigin","EmbeddedSession"],["validate_embed_intent","propose_guest_grant"],["tenant_binding","origin_policy","session_expiry"],["iframe_is_not_authority","host_identity_is_not_guest_identity"],["tenant_mismatch","origin_denied","expired_grant"],[],"effect_intents_and_receipts",["evidence.powerbi.embedded","evidence.superset.embedded"],"adapter_boundary"),
        library("library.consumption.alert_state","semantic.alert_state",["capability.evaluate_alert","capability.transition_alert"],["AlertRule","AlertEvaluation","AlertState"],["evaluate_rule","transition_state"],["hysteresis_policy","missing_data_policy"],["alert_state_is_not_notification_delivery"],["unknown_cut","indeterminate_condition"],[],"pure_no_io",["evidence.superset.alerts","evidence.grafana.notifications"]),
        library("library.consumption.subscription_runner","semantic.subscription",["capability.run_subscription"],["ContentSubscription","ScheduleOccurrence","AttentionIntent"],["validate_subscription","evaluate_schedule","emit_attention_intent","cancel_subscription"],["content_cut_policy","schedule_policy","subscriber_audience_intent_policy"],["scheduled_does_not_mean_evaluated","attention_intent_does_not_mean_delivery","delivery_does_not_mean_business_acknowledgment"],["unauthorized_subscriber","expired_subscription","content_cut_unclosed","schedule_ambiguous","attention_intent_invalid"],["library.consumption.report_snapshot","library.consumption.export_writer"],"attention_intents_only_no_channel_io",["evidence.powerbi.subscription","evidence.knock.workflows","evidence.novu.workflow_api"],"runtime_boundary"),
        library("library.consumption.report_snapshot","semantic.report_snapshot",["capability.materialize_snapshot"],["SnapshotIntent","SnapshotBinding","RenditionEvidence","SealedSnapshot"],["open_snapshot","record_rendition","seal_snapshot","supersede_snapshot"],["snapshot_identity_policy","verification_policy","supersession_policy"],["sealed_snapshot_is_immutable","snapshot_integrity_is_not_source_finality"],["unresolved_cut","missing_rendition_evidence","snapshot_already_sealed"],["library.consumption.presentation_ir","library.consumption.renderer_adapter"],"pure_no_io",["evidence.powerbi.export","evidence.powerbi.subscription"]),
        library("library.consumption.export_writer","semantic.export",["capability.export_artifact"],["ExportIntent","ExportFormatOffer","ExportPlan","EncodedExportArtifact","ExportDeliveryReceipt"],["plan_export","encode_export","deliver_export"],["format_profile","loss_policy","disposition_policy"],["export_creates_new_occurrence","loss_is_explicit","delivery_is_not_continuing_access_governance"],["unauthorized_export","unsupported_format","undeclared_loss","unknown_delivery_completion"],["library.consumption.presentation_ir"],"effect_intents_and_receipts",["evidence.powerbi.export","evidence.powerbi.subscription"],"adapter_boundary"),
        library("library.consumption.table_model","semantic.presentation_ir",["capability.lower_presentation","capability.validate_accessibility"],["TableModel","HeaderGraph","CellCoordinate"],["build_table_model","derive_accessible_headers"],["subtotal_policy","sparse_cell_policy"],["visual_position_is_not_header_semantics"],["ambiguous_header","unsupported_span"],["library.consumption.presentation_ir"],"pure_no_io",["evidence.w3c.wcag22","evidence.powerbi.export"]),
    ]
    library_product_refs = {
        "library.consumption.presentation_ir": ["product.bi_reporting", "product.embedded_analytics"],
        "library.consumption.visual_encoding": ["product.bi_reporting", "product.embedded_analytics"],
        "library.consumption.dashboard_runtime": ["product.bi_reporting", "product.embedded_analytics"],
        "library.consumption.renderer_adapter": ["product.bi_reporting", "product.embedded_analytics"],
        "library.consumption.accessibility": ["product.bi_reporting", "product.embedded_analytics"],
        "library.consumption.localization": ["product.bi_reporting", "product.embedded_analytics"],
        "library.consumption.notebook_document": ["product.analytical_notebook"],
        "library.consumption.embedded_bridge": ["product.embedded_analytics"],
        "library.consumption.alert_state": ["product.bi_reporting"],
        "library.consumption.subscription_runner": ["product.bi_reporting"],
        "library.consumption.report_snapshot": ["product.bi_reporting"],
        "library.consumption.export_writer": ["product.bi_reporting"],
        "library.consumption.table_model": ["product.bi_reporting", "product.embedded_analytics"],
    }
    for row in libraries:
        row["product_refs"] = library_product_refs[row["library_id"]]

    requirements = [
        {"requirement_id":f"requirement.consumption.{cap.removeprefix('capability.').replace('.', '_')}","consumer_ref":consumer,"capability_ref":cap,"binding_phase":phase,"minimum_qualified_offers":1,"status":"unbound","refusal":refusal}
        for cap, consumer, phase, refusal in [
            ("capability.author_report","product.bi_reporting","compile_time","no_qualified_report_core"),
            ("capability.compose_dashboard","product.bi_reporting","runtime","no_qualified_dashboard_runtime"),
            ("capability.render_visual","product.bi_reporting","runtime","no_qualified_renderer"),
            ("capability.validate_accessibility","product.bi_reporting","qualification_time","accessibility_not_qualified"),
            ("capability.localize_presentation","product.bi_reporting","runtime","locale_profile_unsupported"),
            ("capability.export_artifact","product.bi_reporting","runtime","no_authorized_export_offer"),
            ("capability.embed_surface","product.embedded_analytics","deployment_time","no_qualified_embed_runtime"),
            ("capability.manage_notebook","product.analytical_notebook","compile_time","no_qualified_notebook_document_core"),
            ("capability.execute_notebook","product.analytical_notebook","runtime","no_qualified_kernel_occurrence"),
            ("capability.evaluate_alert","product.bi_reporting","runtime","no_qualified_alert_evaluator"),
            ("capability.run_subscription","product.bi_reporting","runtime","no_qualified_subscription_runner"),
            ("capability.validate_workbook","semantic.spreadsheet_governance","qualification_time","workbook_governance_not_qualified"),
        ]
    ]

    offers = [
        {"offer_id":"offer.powerbi.consumption","provider_ref":"implementation.power_bi","capability_refs":["capability.author_report","capability.compose_dashboard","capability.render_visual","capability.embed_surface","capability.export_artifact","capability.run_subscription"],"qualified_implementation_count":0,"portable":False,"status":"observed_unqualified","evidence_refs":["evidence.powerbi.overview","evidence.powerbi.embedded","evidence.powerbi.export","evidence.powerbi.subscription"]},
        {"offer_id":"offer.superset.consumption","provider_ref":"implementation.superset","capability_refs":["capability.author_report","capability.compose_dashboard","capability.embed_surface","capability.evaluate_alert","capability.run_subscription"],"qualified_implementation_count":0,"portable":False,"status":"observed_unqualified","evidence_refs":["evidence.superset.embedded","evidence.superset.alerts"]},
        {"offer_id":"offer.jupyter.notebook","provider_ref":"implementation.jupyter","capability_refs":["capability.manage_notebook","capability.execute_notebook"],"qualified_implementation_count":0,"portable":False,"status":"observed_unqualified","evidence_refs":["evidence.jupyter.nbformat","evidence.jupyter.messaging","evidence.jupyter.kernels"]},
        {"offer_id":"offer.vega.render","provider_ref":"implementation.vega","capability_refs":["capability.lower_presentation","capability.render_visual","capability.manage_presentation_state"],"qualified_implementation_count":0,"portable":False,"status":"observed_unqualified","evidence_refs":["evidence.vega.spec","evidence.vegalite.spec"]},
        {"offer_id":"offer.observable.visual","provider_ref":"implementation.observable","capability_refs":["capability.render_visual","capability.manage_presentation_state"],"qualified_implementation_count":0,"portable":False,"status":"observed_unqualified","evidence_refs":["evidence.observable.plot","evidence.observable.runtime"]},
        {"offer_id":"offer.alertmanager.delivery","provider_ref":"implementation.alertmanager","capability_refs":["capability.run_subscription"],"qualified_implementation_count":0,"portable":False,"status":"observed_unqualified","evidence_refs":["evidence.prometheus.alertmanager"]},
        {"offer_id":"offer.grafana.alerting","provider_ref":"implementation.grafana_alerting","capability_refs":["capability.transition_alert","capability.run_subscription"],"qualified_implementation_count":0,"portable":False,"status":"observed_unqualified","evidence_refs":["evidence.grafana.notifications","evidence.grafana.export"]},
    ]

    relations = [
        {"relation_id":f"relation.suite.packages.{product.split('.')[-1]}","from_ref":"suite.analytics_experience","predicate":"packages","to_ref":product,"binding_phase":"authoring"}
        for product in ["product.bi_reporting","product.embedded_analytics","product.analytical_notebook"]
    ] + [
        {"relation_id":"relation.pattern.realizes.suite","from_ref":"pattern.analytical_consumption","predicate":"realizes","to_ref":"suite.analytics_experience","binding_phase":"authoring"},
        {"relation_id":"relation.bi.requires.metric","from_ref":"product.bi_reporting","predicate":"requires","to_ref":"neighbor.semantic_metric","binding_phase":"compile_time"},
        {"relation_id":"relation.bi.requires.query","from_ref":"product.bi_reporting","predicate":"requires","to_ref":"neighbor.query_engine","binding_phase":"runtime"},
        {"relation_id":"relation.embed.requires.identity","from_ref":"product.embedded_analytics","predicate":"requires","to_ref":"neighbor.identity_policy","binding_phase":"runtime"},
        {"relation_id":"relation.subscription.requires.delivery","from_ref":"semantic.subscription","predicate":"requires","to_ref":"neighbor.notification_delivery","binding_phase":"runtime"},
        {"relation_id":"relation.widget.governed_by.dashboard","from_ref":"artifact.dashboard_widget","predicate":"governed_by","to_ref":"semantic.dashboard_definition","binding_phase":"authoring"},
        {"relation_id":"relation.snapshot.governed_by.snapshot","from_ref":"artifact.report_snapshot","predicate":"governed_by","to_ref":"semantic.report_snapshot","binding_phase":"runtime"},
        {"relation_id":"relation.jupyter.specializes.notebook","from_ref":"standard.jupyter_nbformat","predicate":"specializes","to_ref":"semantic.notebook_document","binding_phase":"compile_time"},
        {"relation_id":"relation.vega.specializes.presentation","from_ref":"standard.vega","predicate":"specializes","to_ref":"semantic.presentation_ir","binding_phase":"compile_time"},
        {"relation_id":"relation.vegalite.specializes.presentation","from_ref":"standard.vegalite","predicate":"specializes","to_ref":"semantic.presentation_ir","binding_phase":"compile_time"},
    ]

    crosswalks = [
        {"legacy_ref":"candidate.product.bi_reporting","canonical_refs":["product.bi_reporting"],"disposition":"replace_exact"},
        {"legacy_ref":"candidate.product.embedded_analytics","canonical_refs":["product.embedded_analytics"],"disposition":"replace_exact"},
        {"legacy_ref":"candidate.product.analytical_notebook","canonical_refs":["product.analytical_notebook"],"disposition":"replace_exact"},
        {"legacy_ref":"candidate.product.visualization_runtime","canonical_refs":["library.consumption.presentation_ir","library.consumption.renderer_adapter"],"disposition":"reclassify_library_runtime"},
        {"legacy_ref":"candidate.product.dashboard_widget","canonical_refs":["artifact.dashboard_widget"],"disposition":"reclassify_presentation_artifact"},
        {"legacy_ref":"candidate.product.alert_subscription","canonical_refs":["semantic.alert_rule","semantic.alert_state","semantic.subscription","neighbor.notification_delivery"],"disposition":"retire_composite_split_producer_capabilities_and_external_product"},
        {"legacy_ref":"candidate.product.spreadsheet_governance","canonical_refs":["semantic.spreadsheet_governance","neighbor.spreadsheet_application"],"disposition":"defer_product_retain_contract"},
        {"legacy_ref":"candidate.product.semantic_metric","canonical_refs":["neighbor.semantic_metric"],"disposition":"neighbor_import"},
        {"legacy_ref":"candidate.product.distributed_query","canonical_refs":["neighbor.query_engine"],"disposition":"neighbor_import"},
        {"legacy_ref":"candidate.product.metric_store_bundle","canonical_refs":["neighbor.semantic_metric","neighbor.query_engine"],"disposition":"suite_not_owner"},
    ]

    negative_tests = [
        ("negative.report_metric","Report layout or label cannot redefine a metric.","refuse_semantic_owner_collapse"),
        ("negative.dashboard_case","Dashboard identity cannot substitute for analytical-case identity.","refuse_case_collapse"),
        ("negative.snapshot_live","Snapshot completeness cannot be inferred from a live-view epoch.","refuse_temporal_collapse"),
        ("negative.widget_product","A widget package is not an independent product.","reclassify_component"),
        ("negative.visual_runtime_product","A renderer library is not an operated product by name.","reclassify_library"),
        ("negative.notebook_kernel","Notebook document identity is not kernel-session identity.","refuse_identity_collapse"),
        ("negative.stored_output_receipt","Stored notebook output is not an execution receipt.","refuse_evidence_promotion"),
        ("negative.embed_iframe","An iframe does not prove tenant isolation or authority.","refuse_security_inference"),
        ("negative.guest_host_identity","Host principal and embedded guest grant are distinct.","refuse_identity_collapse"),
        ("negative.alert_notification","Alert condition/state is not notification delivery.","refuse_state_effect_collapse"),
        ("negative.delivery_comprehension","Delivery receipt does not prove recipient comprehension.","refuse_outcome_promotion"),
        ("negative.export_share","Exported bytes are not continuing governed access.","require_disclosure_receipt"),
        ("negative.accessibility_style","Color/theme/alt text alone do not prove equivalent access.","require_accessibility_oracle"),
        ("negative.locale_value","Localization cannot mutate semantic value.","refuse_semantic_mutation"),
        ("negative.formula_governance","Formula syntax compatibility does not prove workbook recalculation equivalence.","require_recalculation_evidence"),
        ("negative.provider_suite","Provider suite packaging cannot transfer semantic ownership.","refuse_suite_collapse"),
        ("negative.agent_authority","Generated explanation or chart proposal has no semantic or effect authority.","require_deterministic_validation"),
        ("negative.ai_prefix","Consumption capabilities do not become separate AI products by automation modality.","remove_optional_extension_and_retest"),
    ]
    negative_tests = [
        {"test_id": ident, "prohibited_claim": claim, "expected_result": result}
        for ident, claim, result in negative_tests
    ]

    compiler_map = {
        "library.consumption.presentation_ir": "library.cbv.presentation_ir",
        "library.consumption.visual_encoding": "library.cbv.visual_encoding",
        "library.consumption.dashboard_runtime": "library.cbv.dashboard_runtime",
        "library.consumption.renderer_adapter": "library.cbv.renderer_adapter",
        "library.consumption.accessibility": "library.cbv.accessibility_semantics",
        "library.consumption.localization": "library.cbv.i18n_format",
        "library.consumption.notebook_document": "library.cbv.notebook_document",
        "library.consumption.embedded_bridge": "library.cbv.embedded_bridge",
        "library.consumption.alert_state": "library.cbv.alert_state",
        "library.consumption.subscription_runner": "library.cbv.subscription_runner",
        "library.consumption.report_snapshot": ["library.cbv.report_snapshot_reducer"],
        "library.consumption.export_writer": ["library.cbv.export_plan", "library.cbv.export_encoder", "library.cbv.export_delivery_port"],
        "library.consumption.table_model": "library.cbv.table_model",
    }
    binding_maps = [
        {
            "binding_map_id": f"binding.consumption.{local.split('.')[-1]}",
            "abstract_library_ref": local,
            "product_refs": library_product_refs[local],
            "concrete_library_refs": concrete if isinstance(concrete, list) else [concrete],
            "compiler_disposition": "structurally_projected_unqualified",
            "portable_offer": False,
        }
        for local, concrete in compiler_map.items()
    ]

    bi_product = next(row for row in artifacts if row["artifact_id"] == "product.bi_reporting")
    bi_product.update({
        "sovereign_question": "How can report authors publish governed analytical reports and dashboards that consumers can inspect, interact with, snapshot, export and subscribe to under explicit semantic, accessibility and disclosure contracts?",
        "users": ["report_author", "publisher", "analytical_consumer", "workspace_administrator"],
        "harmed_parties": ["decision_subject", "data_subject", "misled_consumer", "unauthorized_recipient"],
        "jobs": ["Author, review, publish, interact with, snapshot, export, subscribe to, supersede and retire governed analytical presentations."],
        "outcomes": ["versioned_report_edition", "traceable_interaction_state", "accessible_localized_presentation", "authorized_snapshot_export_and_subscription"],
        "negative_mission": "Does not own metric meaning, source truth, query execution, identity or policy authority, notification delivery, business-case judgment or downstream action.",
        "lifecycle_states": ["draft", "semantics_bound", "review_pending", "approved", "publishing", "published", "suspended", "superseded", "retired"],
        "commands": ["open_report_draft", "bind_semantic_query", "author_report", "compose_dashboard", "submit_report_review", "approve_report", "publish_report_edition", "open_view_session", "apply_interaction", "materialize_report_snapshot", "request_export", "evaluate_alert_rule", "create_subscription", "suspend_report", "supersede_report", "retire_report"],
        "events": ["report_draft_opened", "semantic_query_bound", "report_authored", "dashboard_composed", "report_review_requested", "report_approved", "report_edition_published", "view_session_opened", "interaction_applied", "report_snapshot_materialized", "export_requested", "alert_rule_evaluated", "subscription_created", "report_suspended", "report_superseded", "report_retired"],
        "invariants": ["report layout and labels cannot redefine metric meaning", "report dashboard widget snapshot and view session identities are distinct", "every rendered value binds exact semantic query and data-cut evidence", "accessibility and localization cannot mutate semantic values", "approval publication export disclosure and delivery are separate authorities"],
        "refusals": ["semantic_definition_unbound", "query_offer_unqualified", "presentation_ir_invalid", "accessibility_conformance_unproved", "locale_profile_unsupported", "stale_or_incomplete_data_cut", "publication_authority_missing", "export_policy_refused", "subscription_recipient_unauthorized", "snapshot_loss_unaccepted", "provider_budget_exhausted"],
        "automation_modality": {"default": "DETERMINISTIC_CORE_ONLY", "postures": ["PROHIBITED", "OPTIONAL", "REQUIRED_BY_INTENT", "UNDETERMINED"], "law": "A model or agent may propose a chart, narrative or interaction but cannot define metrics, approve publication, authorize disclosure, perform effects or prove acceptance.", "hard_work_law": "Automation never replaces task analysis, semantic binding, accessibility evaluation, authority, evidence, qualification or consumer/domain acceptance."},
    })

    ddd_dossiers = [{
        "dossier_id": "ddd.consumption.bi_reporting",
        "product_ref": "product.bi_reporting",
        "status": "candidate_not_ratified",
        "product_truth": {
            "sovereign_question": bi_product["sovereign_question"],
            "users": bi_product["users"],
            "harmed_parties": bi_product["harmed_parties"],
            "jobs": bi_product["jobs"],
            "measurable_outcomes": bi_product["outcomes"],
            "negative_mission": bi_product["negative_mission"],
        },
        "strategic_and_tactical_ddd": {
            "domain_vision_statement": "Own the governed lifecycle from a semantically bound report draft to accessible interactive consumption and authorized presentation artifacts without acquiring metric, query, policy or decision authority.",
            "subdomain_classification": "core_horizontal_analytical_consumption_product",
            "bounded_context_boundary": {"inside": ["report and dashboard editions", "presentation IR and visual encodings", "view and interaction state", "accessible and localized representations", "snapshots exports alerts and subscriptions", "publication suspension supersession and retirement"], "outside": ["metric and formula meaning", "source facts", "physical query execution", "principal and policy authority", "notification-channel delivery", "analytical case judgment and downstream action"]},
            "ubiquitous_language_policy": "Report, dashboard, widget, view session, presentation state, snapshot, export, alert rule, alert state, subscription and delivery receipt are separate identities; provider homonyms cross named ACLs.",
            "context_map": [
                {"neighbor_ref": "neighbor.semantic_metric", "relationship": "customer_supplier", "translation": "bind exact semantic definition and query editions"},
                {"neighbor_ref": "neighbor.query_engine", "relationship": "customer_supplier_acl", "translation": "submit typed queries and import results with execution receipts"},
                {"neighbor_ref": "neighbor.identity_policy", "relationship": "conformist_at_authority_gate", "translation": "obtain principal access purpose export and disclosure decisions"},
                {"neighbor_ref": "neighbor.notification_delivery", "relationship": "open_host_service", "translation": "issue delivery intents and receive attempt receipts without owning the channel"},
            ],
            "anti_corruption_layers": ["acl.semantic_metric", "acl.query_result", "acl.identity_and_policy", "acl.notification_delivery", "acl.provider_presentation"],
            "published_language": ["ReportDefinitionEdition", "DashboardDefinition", "PresentationIr", "ViewSession", "ReportSnapshot", "ExportIntent", "AlertOccurrence", "Subscription", "typed refusals and receipts"],
            "value_objects": ["ReportId", "ReportEdition", "DashboardId", "WidgetRef", "SemanticQueryRef", "DataCutRef", "PresentationNode", "VisualEncoding", "LocaleProfile", "AccessibilityProfile", "AudienceRef", "ParameterBinding", "InteractionIntent", "SnapshotDigest", "ExportProfile"],
            "entities": ["ReportDefinition", "DashboardDefinition", "Publication", "ViewSession", "ReportSnapshot", "AlertRule", "AlertOccurrence", "Subscription"],
            "aggregates": [
                {"root": "ReportDefinition", "members": ["semantic_bindings", "presentation_ir", "parameters", "accessibility_profile", "publication_state"], "consistency": "one command advances one immutable report-definition edition"},
                {"root": "ViewSession", "members": ["principal_scope", "report_edition", "parameter_bindings", "presentation_state", "interaction_history"], "consistency": "each accepted interaction advances one session version"},
                {"root": "Subscription", "members": ["recipient", "content_ref", "schedule", "parameters", "channel_intent", "state"], "consistency": "schedule and recipient authority are validated atomically before activation"},
            ],
            "aggregate_roots": ["ReportDefinition", "ViewSession", "Subscription"],
            "aggregate_invariants": bi_product["invariants"],
            "commands": bi_product["commands"],
            "domain_events": bi_product["events"],
            "refusal_failure_catalog": bi_product["refusals"],
            "domain_services": ["SemanticPresentationBindingService", "PresentationLoweringService", "AccessibilityEvaluationService", "LocalizationService", "SnapshotMaterializationService", "AlertEvaluationService"],
            "application_services": ["AuthorReportUseCase", "ReviewAndPublishReportUseCase", "ViewAndInteractUseCase", "ExportReportUseCase", "ManageSubscriptionUseCase", "RetireReportUseCase"],
            "repositories": ["ReportDefinitionRepository", "PublicationRepository", "ViewSessionRepository", "ReportSnapshotRepository", "AlertRuleRepository", "SubscriptionRepository"],
            "factories": ["ReportDefinitionFactory", "DashboardDefinitionFactory", "ViewSessionFactory", "ReportSnapshotFactory", "SubscriptionFactory"],
            "specifications": ["ReportPublicationReadinessSpecification", "SemanticBindingSpecification", "AccessibilityTargetSpecification", "SnapshotCompletenessSpecification", "ExportAuthorizationSpecification", "SubscriptionActivationSpecification"],
            "state_machine": {"report_states": bi_product["lifecycle_states"], "alert_states": ["pending", "firing", "resolved", "suppressed", "acknowledged"], "subscription_states": ["draft", "active", "suspended", "expired", "cancelled"], "transition_policy": "Only named commands under aggregate invariants may emit the corresponding past-tense event; approval is not publication, export, disclosure or delivery."},
            "policies_and_reactions": ["when a report edition is published invalidate incompatible view caches", "when a semantic dependency is recalled suspend affected publications", "when an alert fires issue a delivery intent only if subscription and policy remain valid", "when export is refused retain the live view without emitting bytes"],
            "sagas_and_process_managers": ["ReportPublicationProcess", "ReportSnapshotProcess", "ExportDisclosureProcess", "AlertSubscriptionProcess", "ReportRetirementProcess"],
            "read_models_and_projections": ["ReportCatalogView", "DashboardCompositionView", "PublicationStatusView", "ViewSessionHistory", "AccessibilityConformanceView", "SnapshotLineageView", "AlertAndSubscriptionView"],
            "integration_event_policy": "Only minimized versioned publication suspension retirement snapshot export and alert/subscription events cross the boundary; interaction detail remains scoped to its session and policy.",
            "concurrency_and_idempotency": ["optimistic report-edition compare-and-swap", "idempotency key per publication snapshot export and alert evaluation", "session version on interactions", "deduplicated scheduled subscription occurrence", "single-winner retirement transition"],
            "time_model": ["report-definition validity and recording time are distinct", "every result binds source/query cut time", "view session and interaction time are explicit", "snapshot and export occurrence time do not imply source finality", "alert evaluation and delivery attempt time are separate", "schedules bind calendar timezone and edition"],
            "event_storming_swimlanes": ["report_author", "publisher_or_approver", "consumer", "presentation_runtime", "semantic_and_query_neighbors", "identity_policy_authority", "notification_provider"],
            "nonfunctional_laws": ["deterministic validation and lowering", "bounded rendering interaction and export budgets", "cooperative cancellation", "accessibility and localization profiles are explicit", "no hidden disclosure or downstream action", "every snapshot and export receipt binds report query data cut provider policy and digest", "removing model and agent extensions preserves the complete deterministic core"],
        },
    }]

    return enrich_remaining_consumption_products({
        "contract_id": "contract.product_adjudication.consumption_experiences.v0_1_0",
        "edition": 1,
        "status": "evidence_backed_adjudicated_candidate_not_ratified",
        "scope": "Horizontal BI/reporting, embedded analytics, notebook, visualization, dashboard artifact, alert/subscription, export, accessibility, localization and spreadsheet-governance boundaries.",
        "negative_scope": "Does not ratify products, qualify renderers or BI providers, own metric/query/source truth, grant disclosure or action authority, or infer accessibility and reproducibility from provider claims.",
        "non_collapse_laws": [
            "metric meaning != report definition != visual encoding",
            "analytical case != dashboard != widget",
            "query result != presentation state",
            "report snapshot != live view",
            "notebook document != kernel session != stored output != execution receipt",
            "embedded frame != tenant session != guest grant != host authority",
            "alert rule != alert state != notification delivery",
            "exported bytes != governed live sharing",
            "accessibility semantics != styling",
            "locale formatting cannot mutate semantic value",
            "spreadsheet formula syntax != recalculation equivalence != workbook governance",
            "suite packaging does not transfer semantic ownership",
            "optional model or agent proposal does not create meaning, validation, authority, effect or product identity",
        ],
        "sources": sources,
        "artifact_kinds": artifact_kinds,
        "artifacts": artifacts,
        "boundary_decisions": boundary_decisions,
        "ownership": ownership,
        "libraries": libraries,
        "requirements": requirements,
        "offers": offers,
        "relations": relations,
        "crosswalks": crosswalks,
        "negative_tests": negative_tests,
        "binding_maps": binding_maps,
        "binding_gaps": [],
        "ddd_dossiers": ddd_dossiers,
    })


def source_bytes() -> bytes:
    return (json.dumps(source(), ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode()


if __name__ == "__main__":
    SOURCE.write_bytes(source_bytes())
    print(f"WROTE {SOURCE}")
