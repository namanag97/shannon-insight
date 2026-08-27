#!/usr/bin/env python3
"""Adjudicated research proposal for splitting interactive and formal reporting."""

from __future__ import annotations

from typing import Any

from source_model import source


SPLIT_SOURCES = [
    source("superset_explore", "Exploring Data in Superset", "Apache Superset", "https://superset.apache.org/docs/using-superset/exploring-data/", "Explore persists iterative query, metric, chart, filter, pivot and dashboard authoring state for interactive analysis.", "One implementation does not define portable exploration semantics or validate analytical claims.", "interactive_exploration"),
    source("superset_dashboard", "Creating Your First Dashboard", "Apache Superset", "https://superset.apache.org/user-docs/using-superset/creating-your-first-dashboard/", "Charts and dashboards have separate persisted identities, publication state, layout, filters, access and interaction behavior.", "Superset packaging does not prove formal reporting or decision authority.", "interactive_exploration"),
    source("qlik_explore", "Explore, Discover and Analyze", "Qlik", "https://help.qlik.com/en-US/sense/May2025/pdf/Explore%2C%20discover%20and%20analyze.pdf", "Selections, sheets, alternate states and bookmarks form a reversible interactive exploration lifecycle.", "Provider documentation does not define a portable selection algebra or product boundary alone.", "interactive_exploration"),
    source("cognos_formats", "Report Formats", "IBM", "https://www.ibm.com/docs/en/cognos-analytics/12.0.x?topic=cubes-report-formats", "Report outputs have independently secured HTML, CSV, PDF, spreadsheet and XML generation capabilities.", "Format support is implementation evidence and not a portable rendition contract.", "formal_reporting"),
    source("cognos_schedule", "Scheduling a Report", "IBM", "https://www.ibm.com/docs/en/cognos-analytics/12.1.x?topic=sa-scheduling-report", "Schedules have owner credentials, frequency, priority, prompts, format, accessibility, language, delivery and saved-output state.", "A Cognos schedule does not establish universal report authority or delivery semantics.", "formal_reporting"),
    source("oracle_report_jobs", "Manage Report Jobs", "Oracle", "https://docs.oracle.com/en/middleware/bi/analytics-server/user-publisher-oas/manage-report-jobs-page.html", "Future and recurring report jobs can be inspected, edited, suspended, resumed, deleted and linked to run history.", "Provider job state is not a selected portable state machine.", "formal_reporting"),
    source("oracle_report_history", "Report Job History and Saved Output", "Oracle", "https://docs.oracle.com/en/middleware/bi/analytics-server/user-publisher-oas/view-report-job-history-and-saved-output.html", "Report runs, status, cancellation, source data, saved output, republishing and deletion have separate identities and lifecycle.", "Saved output does not prove source finality, approval or authorized downstream use.", "formal_reporting"),
    source("jasper_scheduler", "JasperReports Server REST API Reference", "Jaspersoft", "https://community.jaspersoft.com/documentation/jasperreports-server/tibco-jasperreports-server-rest-api-reference/", "Report jobs bind report, parameters, schedule, output formats, repository/file/FTP/email destinations and run state.", "A provider API is adoption evidence, not portable contract selection or qualification.", "formal_reporting"),
]


INTERACTIVE_REFS = [
    "evidence.presentation.vegalite",
    "evidence.presentation.vegalite_selection",
    "evidence.presentation.tableau_sheets",
    "evidence.presentation.superset_explore",
    "evidence.presentation.superset_dashboard",
    "evidence.presentation.qlik_explore",
]

FORMAL_REFS = [
    "evidence.presentation.powerbi_paginated",
    "evidence.presentation.powerbi_paginated_docs",
    "evidence.presentation.grafana_reporting",
    "evidence.presentation.cognos_formats",
    "evidence.presentation.cognos_schedule",
    "evidence.presentation.oracle_report_jobs",
    "evidence.presentation.oracle_report_history",
    "evidence.presentation.jasper_scheduler",
    "evidence.presentation.xbrl",
    "evidence.presentation.pdfua",
]


def split_axis(subject: str, refs: list[str], findings: dict[str, str]) -> dict[str, Any]:
    axes = ["user", "job", "adoption", "semantics", "authority", "lifecycle", "operation", "economics", "interface", "market_evidence"]
    return {
        axis: {
            "score": 2,
            "finding": findings[axis],
            "evidence_refs": refs,
            "subject": subject,
        }
        for axis in axes
    }


INTERACTIVE_FINDINGS = {
    "user": "Analysts and information consumers iteratively explore; they are not report schedulers, filing publishers or distribution operators.",
    "job": "The owned job is reversible sensemaking through views, selections, comparisons, pivots, drills and bookmarks.",
    "adoption": "Superset, Tableau and Qlik independently expose exploration, chart, sheet and dashboard adoption surfaces.",
    "semantics": "Worksheet, chart, dashboard, selection, filter state and bookmark are first-class meanings distinct from report jobs and output artifacts.",
    "authority": "The product may publish an interactive artifact but does not issue a formal statement, deliver a filing or authorize an operational effect.",
    "lifecycle": "Exploration artifacts move through draft, bound, reviewed, published, superseded and retired while sessions and bookmarks have separate state.",
    "operation": "The runtime optimizes low-latency query, interaction reduction, linked views, rendering, caching and cancellation.",
    "economics": "Interactive BI/exploration is independently deployed, operated, supported and capacity-planned.",
    "interface": "Declarative visualization specs plus chart/dashboard APIs and exported definitions provide explicit integration and exit surfaces.",
    "market_evidence": "At least three independent implementation families persist the same exploration artifacts and job boundaries.",
}

FORMAL_FINDINGS = {
    "user": "Report designers, publishers, schedulers, filing owners and recipients are distinguishable from interactive explorers.",
    "job": "The owned job is to define, validate, execute, render, publish, distribute, correct and withdraw durable report artifacts.",
    "adoption": "Power BI Paginated Reports, Cognos Reporting, Oracle BI Publisher and JasperReports independently expose formal-reporting surfaces.",
    "semantics": "Report definition, template, parameter set, job, run, rendition, output artifact, schedule, delivery and job history are first-class state.",
    "authority": "Publication, issuance, disclosure and recipient selection are explicit authorities separate from source truth and notification transport.",
    "lifecycle": "Definition, job, run, output, publication, supersession, correction, recall and retention have independent state machines.",
    "operation": "The runtime optimizes batch execution, pagination, multi-format rendering, bursting, scheduling, delivery, retention and replay.",
    "economics": "Formal reporting engines and services are independently deployed, licensed, supported and capacity-managed.",
    "interface": "Report definitions, parameters, scheduling APIs, output-format contracts and durable files form explicit adoption and exit surfaces.",
    "market_evidence": "Four independent implementation families and reporting standards exhibit convergent lifecycle state.",
}


SPLIT_ADJUDICATIONS = [
    {
        "adjudication_id": "adjudication.presentation.bi-reporting-split.v1",
        "record_kind": "presentation_product_split_adjudication",
        "source_product_ref": "product.bi_reporting",
        "source_candidate_ref": "candidate.product.bi_reporting",
        "proposed_product_refs": ["product.interactive_analytics_exploration", "product.formal_reporting_publication"],
        "verdict": "PROMOTE_SPLIT_TO_CANONICAL_ADJUDICATION",
        "ratification": "WITHHELD",
        "rationale": "Interactive sensemaking and formal artifact issuance have different users, jobs, state, runtimes, economics, failure modes and independently adopted implementations; retaining one product would make its consistency and authority boundary incoherent.",
        "noncollapse_laws": [
            "interactive_view != formal_report_definition",
            "view_session != report_run",
            "bookmark != report_parameter_set",
            "dashboard_publication != report_issuance",
            "live_refresh != sealed_report_output",
            "interactive_export != governed_report_distribution",
        ],
        "migration_posture": "HARD_CUT_NO_COMPATIBILITY_ALIAS_AFTER_DEPENDENT_GRAPH_REWRITE",
        "completion_claim": False,
    },
    {
        "adjudication_id": "adjudication.presentation.interactive-exploration.v1",
        "record_kind": "presentation_product_boundary_adjudication",
        "subject_ref": "product.interactive_analytics_exploration",
        "name": "Interactive Analytics Exploration",
        "sovereign_question": "How can an analyst iteratively inspect, select, compare and navigate semantically bound analytical results while preserving reversible view state and never mutating source or business state?",
        "split_test": split_axis("interactive_analytics_exploration", INTERACTIVE_REFS, INTERACTIVE_FINDINGS),
        "score_total": 20,
        "verdict": "STRONG_PRODUCT",
        "ratification": "WITHHELD",
        "completion_claim": False,
    },
    {
        "adjudication_id": "adjudication.presentation.formal-reporting.v1",
        "record_kind": "presentation_product_boundary_adjudication",
        "subject_ref": "product.formal_reporting_publication",
        "name": "Formal Reporting & Publication",
        "sovereign_question": "How can a report owner define, validate, execute, render, issue, distribute, correct and withdraw a durable analytical report whose inputs, parameters, renditions, recipients and evidence remain exact?",
        "split_test": split_axis("formal_reporting_publication", FORMAL_REFS, FORMAL_FINDINGS),
        "score_total": 20,
        "verdict": "STRONG_PRODUCT",
        "ratification": "WITHHELD",
        "completion_claim": False,
    },
]


LIBRARY_ALLOCATIONS = [
    ("library.consumption.presentation_ir", "SHARED_SEMANTIC_LIBRARY", ["product.interactive_analytics_exploration", "product.formal_reporting_publication", "product.embedded_analytics"]),
    ("library.consumption.visual_encoding", "INTERACTIVE_PRIMARY_FORMAL_IMPORT", ["product.interactive_analytics_exploration", "product.formal_reporting_publication", "product.embedded_analytics"]),
    ("library.consumption.dashboard_runtime", "INTERACTIVE_OWNED", ["product.interactive_analytics_exploration", "product.embedded_analytics"]),
    ("library.consumption.renderer_adapter", "SHARED_ADAPTER", ["product.interactive_analytics_exploration", "product.formal_reporting_publication", "product.embedded_analytics"]),
    ("library.consumption.accessibility", "SHARED_CONSTITUTIONAL_LIBRARY", ["product.interactive_analytics_exploration", "product.formal_reporting_publication", "product.embedded_analytics"]),
    ("library.consumption.localization", "SHARED_SEMANTIC_LIBRARY", ["product.interactive_analytics_exploration", "product.formal_reporting_publication", "product.embedded_analytics"]),
    ("library.consumption.table_model", "SHARED_SEMANTIC_LIBRARY", ["product.interactive_analytics_exploration", "product.formal_reporting_publication", "product.embedded_analytics"]),
    ("library.presentation.interaction_state", "INTERACTIVE_OWNED_NEW", ["product.interactive_analytics_exploration"]),
    ("library.presentation.selection_algebra", "INTERACTIVE_OWNED_NEW", ["product.interactive_analytics_exploration"]),
    ("library.presentation.bookmark_view_state", "INTERACTIVE_OWNED_NEW", ["product.interactive_analytics_exploration"]),
    ("library.presentation.composition_layout", "INTERACTIVE_PRIMARY_SHARED_NEW", ["product.interactive_analytics_exploration", "product.formal_reporting_publication"]),
    ("library.presentation.encoding_fitness", "INTERACTIVE_PRIMARY_SHARED_NEW", ["product.interactive_analytics_exploration", "product.formal_reporting_publication"]),
    ("library.consumption.report_definition", "FORMAL_OWNED", ["product.formal_reporting_publication"]),
    ("library.presentation.report_run", "FORMAL_OWNED_NEW", ["product.formal_reporting_publication"]),
    ("library.presentation.pagination_layout", "FORMAL_OWNED_NEW", ["product.formal_reporting_publication"]),
    ("library.consumption.report_snapshot", "FORMAL_OWNED", ["product.formal_reporting_publication"]),
    ("library.presentation.publication_lifecycle", "FORMAL_OWNED_NEW", ["product.formal_reporting_publication"]),
    ("library.consumption.export_writer", "FORMAL_OWNED", ["product.formal_reporting_publication"]),
    ("library.consumption.subscription_runner", "FORMAL_REPORT_SUBSCRIPTION_ONLY", ["product.formal_reporting_publication"]),
    ("library.consumption.alert_state", "REMOVE_FROM_SPLIT_DEFER_SEPARATE_ALERT_OWNER", []),
]

LIBRARY_ALLOCATIONS = [
    {
        "allocation_id": f"allocation.presentation.{library_ref.replace('.', '-').replace('_', '-')}",
        "record_kind": "presentation_split_library_allocation",
        "library_ref": library_ref,
        "disposition": disposition,
        "proposed_product_refs": product_refs,
        "authority_law": "Allocation assigns product consumption/ownership posture but does not ratify the semantic contract or qualify an implementation.",
        "status": "PROPOSED_UNRATIFIED",
        "completion_claim": False,
    }
    for library_ref, disposition, product_refs in LIBRARY_ALLOCATIONS
]


MIGRATION_STEPS = [
    (1, "FREEZE_SOURCE_BOUNDARY", "Freeze the current product.bi_reporting dependency graph and enumerate every product, library, capability, relation, DDD, qualification and vertical reference."),
    (2, "ADD_TARGET_CONTRACTS", "Add both new product identities, complete DDD dossiers, libraries, requirements, mappings and refusing qualification gates."),
    (3, "ALLOCATE_OWNERSHIP", "Move every old meaning, capability and library using the adjudicated allocation; unresolved alert ownership remains an explicit gap."),
    (4, "REWRITE_DEPENDENTS", "Rewrite all exact references to one or both targets based on consumed meanings; name-based bulk replacement is prohibited."),
    (5, "MIGRATE_ACTIVE_WORK", "Classify drafts, publications, sessions, report jobs, schedules, snapshots and exports as MOVE, SPLIT, COMPLETE_THEN_MOVE or RETIRE."),
    (6, "RUN_NEGATIVE_AND_REPLAY_TESTS", "Prove selection/report-run, bookmark/parameter, live/snapshot and dashboard/issuance distinctions across historical replay."),
    (7, "HARD_CUT", "Remove product.bi_reporting only when no canonical or in-flight reference remains; do not retain a compatibility alias."),
    (8, "RATIFY_SEPARATELY", "Ratify each new boundary, exact contracts, implementations and vertical acceptances independently."),
]

MIGRATION_STEPS = [
    {
        "step_id": f"migration.presentation.bi-reporting.{order:02d}",
        "record_kind": "presentation_product_split_migration_step",
        "order": order,
        "phase": phase,
        "requirement": requirement,
        "status": "PLANNED_NOT_EXECUTED",
        "completion_claim": False,
    }
    for order, phase, requirement in MIGRATION_STEPS
]


def ddd(product_ref: str, formal: bool) -> dict[str, Any]:
    if formal:
        name = "Formal Reporting & Publication"
        vision = "Own durable report definitions, executions, renditions, publications and distribution evidence without acquiring source, metric, query, filing or notification authority."
        users = ["report_designer", "report_publisher", "schedule_operator", "filing_preparer", "recipient_administrator", "auditor"]
        inside = ["report definitions and templates", "parameters and data-cut bindings", "report jobs and runs", "pagination and renditions", "publication editions", "schedules and report subscriptions", "export/distribution intents and receipts", "correction supersession recall and retention"]
        outside = ["metric and source truth", "physical query execution", "regulator filing acceptance", "notification transport", "recipient downstream use", "interactive exploration sessions"]
        roots = ["ReportDefinition", "ReportRun", "ReportPublication", "ReportSubscription"]
        states = {"ReportDefinition": ["draft", "validated", "approved", "released", "superseded", "retired"], "ReportRun": ["planned", "queued", "running", "rendering", "succeeded", "failed", "cancelled", "unknown"], "ReportPublication": ["draft", "issued", "corrected", "superseded", "recalled", "expired"]}
        commands = ["create_report_definition", "bind_report_data", "set_report_parameters", "validate_report_definition", "approve_report_definition", "schedule_report", "request_report_run", "record_report_result", "render_report", "issue_report", "distribute_report", "correct_report", "supersede_report", "recall_report", "retire_report"]
        events = [command.replace("create_", "").replace("set_", "").replace("validate_", "").replace("approve_", "").replace("request_", "").replace("record_", "").replace("schedule_", "").replace("render_", "").replace("issue_", "").replace("distribute_", "").replace("correct_", "").replace("supersede_", "").replace("recall_", "").replace("retire_", "") + "_completed" for command in commands]
        invariants = ["report definition run rendition publication and delivery identities are distinct", "every run binds exact definition parameter semantic query and data-cut editions", "retry creates a new run attempt", "each rendition declares format profile loss and accessibility evidence", "approval issuance distribution regulator acceptance and downstream use are distinct authorities", "correction never overwrites an issued artifact", "scheduled does not mean executed delivered or acknowledged"]
        refusals = ["report_definition_invalid", "semantic_binding_missing", "parameter_invalid", "data_cut_unavailable", "query_offer_unqualified", "run_budget_exhausted", "render_profile_unsupported", "pagination_totality_failed", "accessibility_unproved", "publication_authority_missing", "recipient_unauthorized", "delivery_outcome_unknown", "correction_precedence_ambiguous"]
    else:
        name = "Interactive Analytics Exploration"
        vision = "Own reversible analytical view composition and interaction state over semantically bound results without acquiring source, metric, decision or effect authority."
        users = ["analyst", "business_consumer", "dashboard_author", "exploration_reviewer", "workspace_publisher"]
        inside = ["worksheets charts and dashboard editions", "result bindings", "visual encodings", "view composition", "selection filter parameter and drill state", "bookmarks and shared view state", "interactive publication", "session freshness and cancellation"]
        outside = ["metric and source truth", "physical query execution", "formal report jobs and issuance", "business workflow state", "approval and operational effects", "notification transport"]
        roots = ["ExplorationDocument", "InteractiveSession", "Bookmark"]
        states = {"ExplorationDocument": ["draft", "bound", "reviewed", "published", "superseded", "retired"], "InteractiveSession": ["opening", "active", "refreshing", "degraded", "stale", "closing", "closed"], "Bookmark": ["private", "shared", "expired", "deleted"]}
        commands = ["create_exploration", "bind_result", "add_view", "set_encoding", "compose_dashboard", "open_session", "apply_selection", "apply_filter", "drill", "reset_view_state", "create_bookmark", "share_bookmark", "publish_exploration", "supersede_exploration", "close_session"]
        events = [command + "_completed" for command in commands]
        invariants = ["exploration document view dashboard session selection and bookmark identities are distinct", "every view binds an exact result and semantic edition", "selection filter and drill only alter scoped view state unless an explicit domain command crosses the ACL", "shared scales and composition resolution are explicit", "missingness uncertainty units time and provenance survive interaction", "session freshness is explicit", "publishing a dashboard does not issue a formal report or authorize an effect"]
        refusals = ["result_binding_missing", "semantic_type_unresolved", "encoding_invalid", "composition_resolution_ambiguous", "selection_projection_invalid", "interaction_not_allowed", "query_offer_unqualified", "result_stale", "render_budget_exhausted", "accessibility_equivalence_unproved", "bookmark_scope_invalid", "publication_authority_missing", "domain_action_authority_missing"]

    return {
        "dossier_id": f"ddd.presentation.{product_ref.split('.')[-1]}",
        "record_kind": "candidate_product_ddd_dossier",
        "product_ref": product_ref,
        "name": name,
        "status": "COMPLETE_CANDIDATE_NOT_RATIFIED",
        "product_truth": {"sovereign_question": next(row["sovereign_question"] for row in SPLIT_ADJUDICATIONS if row.get("subject_ref") == product_ref), "users": users, "harmed_parties": ["data_subject", "decision_subject", "misled_consumer", "unauthorized_recipient"], "jobs": [vision], "measurable_outcomes": ["semantic_binding_completeness", "artifact_lifecycle_traceability", "accessibility_equivalence", "provider_independent_exit"], "negative_mission": "Does not own source facts, metric definitions, physical query execution, identity/policy authority, business decisions, operational effects or acceptance evidence."},
        "strategic_and_tactical_ddd": {
            "domain_vision_statement": vision,
            "subdomain_classification": "core_horizontal_analytical_consumption_product",
            "bounded_context_boundary": {"inside": inside, "outside": outside},
            "ubiquitous_language_policy": "Every artifact, edition, execution, interaction and delivery term has one meaning inside this boundary; provider homonyms cross explicit ACLs.",
            "context_map": [{"neighbor_ref": "product.semantic_metric_formula_service", "relationship": "customer_supplier"}, {"neighbor_ref": "product.query_execution_service", "relationship": "customer_supplier_acl"}, {"neighbor_ref": "product.embedded_analytics", "relationship": "published_language"}, {"neighbor_ref": "identity_policy_authority", "relationship": "conformist_at_authority_gate"}],
            "anti_corruption_layers": ["acl.semantic_metric", "acl.query_result", "acl.identity_policy", "acl.renderer_provider", "acl.notification_delivery"],
            "published_language": roots + ["SemanticResultBinding", "PresentationEvidence", "TypedRefusal"],
            "value_objects": ["ProductId", "ArtifactId", "ArtifactEdition", "SemanticQueryRef", "DataCutRef", "AudienceRef", "LocaleProfile", "AccessibilityProfile", "ResourceBudget", "EvidenceDigest"],
            "entities": roots + ["ReviewCase", "CompatibilityAssessment"],
            "aggregates": [{"root": root, "members": ["identity", "edition", "state", "bindings", "evidence"], "consistency": "one accepted command advances exactly one root version"} for root in roots],
            "aggregate_roots": roots,
            "aggregate_invariants": invariants,
            "commands": commands,
            "domain_events": events,
            "refusal_failure_catalog": refusals,
            "domain_services": ["SemanticBindingService", "PresentationValidationService", "AccessibilityEquivalenceService", "CompatibilityService", "EvidenceService"],
            "application_services": ["AuthorUseCase", "ReviewUseCase", "PublishUseCase", "OperateUseCase", "MigrateUseCase", "RetireUseCase"],
            "repositories": [root + "Repository" for root in roots] + ["EvidenceRepository"],
            "factories": [root + "Factory" for root in roots],
            "specifications": ["SemanticBindingSpecification", "ArtifactReadinessSpecification", "AccessibilityEquivalenceSpecification", "DisclosureSpecification", "CompatibilitySpecification"],
            "state_machine": states,
            "policies_and_reactions": ["when an imported semantic or data edition changes mark dependent artifacts stale", "when authority expires suspend dependent publication or session", "when a provider changes require compatibility and semantic-equivalence evidence"],
            "sagas_and_process_managers": ["AuthorReviewPublicationProcess", "ProviderMigrationProcess", "RecallRetirementProcess"],
            "read_models_and_projections": [root + "View" for root in roots] + ["EvidenceAndCompatibilityView"],
            "integration_event_policy": "Only minimized editioned intents, artifacts, lifecycle facts, refusals and receipts cross the boundary; provider DTOs, secrets and mutable runtime internals do not.",
            "concurrency_and_idempotency": ["optimistic edition compare-and-swap", "idempotency key per execution publication and delivery occurrence", "retry receives a new attempt identity", "single-winner lifecycle transitions"],
            "time_model": ["valid and recording time are distinct", "result cut, interaction/run, publication and delivery time are distinct", "schedule binds timezone calendar and edition", "staleness and expiry are explicit"],
            "event_storming_swimlanes": users + ["semantic_registry", "query_runtime", "presentation_runtime", "authority_service", "artifact_store"],
            "nonfunctional_laws": ["deterministic canonical encoding", "finite resource budgets", "cooperative cancellation", "total typed failures", "provider-neutral ports", "complete evidence chain", "accessibility by construction", "optional model removal preserves deterministic core"],
        },
        "completion_claim": False,
    }


SPLIT_DDD_DOSSIERS = [
    ddd("product.interactive_analytics_exploration", False),
    ddd("product.formal_reporting_publication", True),
]
