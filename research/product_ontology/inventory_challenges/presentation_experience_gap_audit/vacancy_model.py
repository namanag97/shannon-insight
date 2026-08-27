#!/usr/bin/env python3
"""Evidence-backed adjudication of the two surviving presentation vacancies."""

from __future__ import annotations

from typing import Any

from source_model import source


VACANCY_SOURCES = [
    source("grafana_alerting_fundamentals", "Introduction to Grafana Alerting", "Grafana Labs", "https://grafana.com/docs/grafana/latest/alerting/fundamentals/", "Alert rules are evaluated into alert instances before notification policies route them through contact points.", "Grafana packaging does not make rule ownership, notification delivery and business escalation one portable authority.", "attention_delivery"),
    source("prometheus_alertmanager", "Alertmanager", "Prometheus", "https://prometheus.io/docs/alerting/latest/alertmanager/", "Alertmanager independently groups, deduplicates, routes, silences and inhibits alerts received from producers.", "Telemetry-alert transport does not define analytical threshold meaning, recipient business authority or incident disposition.", "attention_delivery"),
    source("knock_workflows", "Workflows", "Knock", "https://docs.knock.app/concepts/workflows", "Notification workflows persist triggers, steps, channels, conditions, batching and delivery behavior independently of the producing application.", "A notification workflow does not own the business event or analytical claim that triggered it.", "notification_product"),
    source("knock_preferences", "Preferences", "Knock", "https://docs.knock.app/concepts/preferences", "Recipient and tenant preferences are evaluated separately from workflow definition and trigger occurrence.", "Preferences do not substitute for legal purpose, consent, identity or business authorization.", "notification_product"),
    source("knock_schedules", "Schedules", "Knock", "https://docs.knock.app/concepts/schedules", "Recurring notification-workflow execution has its own schedule identity and lifecycle.", "A notification schedule is not a report subscription or analytical evaluation schedule unless explicitly bound.", "notification_product"),
    source("novu_workflow_api", "Create a workflow", "Novu", "https://docs.novu.co/api-reference/workflows/create-a-workflow", "A second independent notification platform exposes workflow creation, retrieval, update, deletion and step preview as first-class API state.", "Provider API shape is evidence of adoption, not the selected portable contract.", "notification_product"),
    source("tableau_projects", "Use Projects to Manage Content Access", "Tableau", "https://help.tableau.com/current/server/en-us/projects.htm", "Projects organize heterogeneous analytical assets and apply navigation and access management to workbooks, data sources, lenses and nested projects.", "A Tableau project does not prove independent cross-provider analytical content administration economics.", "content_collaboration"),
    source("tableau_comments", "Comment on Views", "Tableau", "https://help.tableau.com/current/pro/desktop/en-us/comment.htm", "Comments are attached to analytical views and participate in a collaboration lifecycle distinct from view computation.", "Comments do not own the analytical artifact edition, approval or publication authority.", "content_collaboration"),
    source("powerbi_workspaces", "Workspaces in Power BI", "Microsoft", "https://learn.microsoft.com/en-us/power-bi/collaborate-share/service-new-workspaces", "Workspaces persist collections, membership roles, access and collaborative authoring of analytical content.", "A Power BI workspace is bundled adoption evidence and not a portable cross-product boundary by itself.", "content_collaboration"),
    source("powerbi_apps", "Publish an app in Power BI", "Microsoft", "https://learn.microsoft.com/en-us/power-bi/collaborate-share/service-create-distribute-apps", "Collaborative workspace content and packaged audience publication are separate states and surfaces.", "Power BI app publication does not define formal report issuance or every analytical content type.", "content_collaboration"),
    source("powerbi_comments", "Add comments to dashboards and reports", "Microsoft", "https://learn.microsoft.com/en-us/power-bi/consumer/end-user-comment", "Comment threads and mentions bind collaboration to report/dashboard context without changing analytical source truth.", "Comments and mentions do not prove review approval or decision authority.", "content_collaboration"),
    source("jupyter_rtc", "Real Time Collaboration", "JupyterLab", "https://jupyterlab.readthedocs.io/en/stable/user/rtc.html", "Notebook/file collaboration has shared editing, awareness and conflict behavior independent of notebook execution semantics.", "Real-time document synchronization does not define analytical publication, access policy or review authority.", "content_collaboration"),
    source("w3c_annotation", "Web Annotation Data Model", "W3C", "https://www.w3.org/TR/annotation-model/", "Annotations have target, body, motivation and provenance semantics that can anchor collaboration without owning the target resource.", "The generic annotation model does not define product-specific review, approval or artifact lifecycle.", "content_collaboration"),
    source("dbt_git", "Git version control", "dbt Labs", "https://docs.getdbt.com/docs/collaborate/git/version-control-basics", "Analytics engineering content uses independent version-control identity, branch and review mechanisms rather than mutable folder state alone.", "Git commits do not define runtime publication, content access or semantic compatibility.", "content_collaboration"),
]


AXES = ["user", "job", "adoption", "semantics", "authority", "lifecycle", "operation", "economics", "interface", "market_evidence"]


def test(subject: str, scores: dict[str, int], findings: dict[str, str], refs: list[str]) -> dict[str, Any]:
    return {
        axis: {"score": scores[axis], "finding": findings[axis], "evidence_refs": refs, "subject": subject}
        for axis in AXES
    }


CONTENT_REFS = [f"evidence.presentation.{name}" for name in ["tableau_projects", "tableau_comments", "powerbi_workspaces", "powerbi_apps", "powerbi_comments", "jupyter_rtc", "w3c_annotation", "dbt_git"]]
NOTIFICATION_REFS = [f"evidence.presentation.{name}" for name in ["knock_workflows", "knock_preferences", "knock_schedules", "novu_workflow_api", "cloudevents"]]
ALERT_REFS = [f"evidence.presentation.{name}" for name in ["grafana_alerting_fundamentals", "prometheus_alertmanager", "cloudevents"]]


CONTENT_SCORES = {"user": 2, "job": 2, "adoption": 1, "semantics": 2, "authority": 2, "lifecycle": 2, "operation": 1, "economics": 0, "interface": 1, "market_evidence": 1}
CONTENT_FINDINGS = {
    "user": "Content administrators, authors, reviewers and consumers are distinguishable, but usually operate inside a containing analytical product.",
    "job": "Organize, share, govern, review, discuss and locate heterogeneous analytical artifacts without owning their internal semantics.",
    "adoption": "Tableau projects, Power BI workspaces and Jupyter collaboration are adopted with their containing products; independent replacement is not proven.",
    "semantics": "Container, membership, ownership, content reference, edition link, annotation anchor, comment thread, review and packaged release are reusable meanings.",
    "authority": "Container access and collaboration moderation are distinct from artifact authorship, semantic approval, formal issuance and business decision authority.",
    "lifecycle": "Containers, memberships, threads, reviews and release collections have state, but artifact lifecycle remains with each producer product.",
    "operation": "Cross-artifact indexing, access projection, collaboration synchronization and retention are operable, though commonly bundled.",
    "economics": "No independently adopted cross-provider analytical content control plane with isolated pricing and support was proven in this pass.",
    "interface": "Generic annotation and version-control contracts exist, while a portable heterogeneous analytical-content export contract remains unselected.",
    "market_evidence": "Multiple suites converge on the state model, but convergence proves reusable seams rather than independent product economics.",
}

NOTIFICATION_SCORES = {axis: 2 for axis in AXES}
NOTIFICATION_FINDINGS = {
    "user": "Notification platform engineers and communication operators are distinct from analytical authors and business decision owners.",
    "job": "Turn typed communication intents into preference-aware, policy-bounded, multi-channel delivery attempts and receipts.",
    "adoption": "Knock and Novu expose independently adoptable notification workflow products; provider/channel services can be replaced behind them.",
    "semantics": "Workflow edition, trigger occurrence, recipient projection, preference snapshot, template edition, schedule, delivery attempt and outcome are first-class state.",
    "authority": "The product owns bounded communication-delivery authority, never source truth, analytical threshold, business acceptance or incident disposition.",
    "lifecycle": "Workflow, schedule, trigger, attempt, suppression and delivery outcome have independent state machines.",
    "operation": "Routing, batching, throttling, retry, provider fallback, rate limits, observability and replay require an independent runtime.",
    "economics": "Notification orchestration is independently priced, capacity-managed, supported and exited across applications.",
    "interface": "Typed trigger APIs, workflow definitions, preference APIs, provider ports and delivery receipts form explicit adoption and exit surfaces.",
    "market_evidence": "At least two independent implementation families converge on workflow, preference, schedule and multi-channel delivery state.",
}


VACANCY_ADJUDICATIONS = [
    {
        "adjudication_id": "adjudication.presentation.content-collaboration.v1",
        "record_kind": "presentation_vacancy_boundary_adjudication",
        "subject_ref": "hypothesis.presentation.analytical_content_collaboration",
        "name": "Analytical Content Management & Collaboration",
        "score_total": sum(CONTENT_SCORES.values()),
        "split_test": test("analytical_content_collaboration", CONTENT_SCORES, CONTENT_FINDINGS, CONTENT_REFS),
        "verdict": "DEFER_PRODUCT_PROMOTION_RETAIN_SHARED_CONTROL_PLANE_AND_LIBRARIES",
        "rationale": "The semantics and lifecycle are real, but independent cross-provider adoption, economics, exit and support remain too weak for a sovereign product boundary.",
        "ratification": "WITHHELD",
        "completion_claim": False,
    },
    {
        "adjudication_id": "adjudication.presentation.notification-orchestration.v1",
        "record_kind": "external_horizontal_product_boundary_adjudication",
        "subject_ref": "external.product.notification_orchestration_delivery",
        "name": "Notification Orchestration & Delivery",
        "score_total": sum(NOTIFICATION_SCORES.values()),
        "split_test": test("notification_orchestration_delivery", NOTIFICATION_SCORES, NOTIFICATION_FINDINGS, NOTIFICATION_REFS),
        "verdict": "STRONG_EXTERNAL_HORIZONTAL_PRODUCT",
        "home_domain": "application_communication_and_attention",
        "analytics_posture": "IMPORTED_NEIGHBOR_NOT_ANALYTICS_OWNED",
        "ratification": "WITHHELD",
        "completion_claim": False,
    },
    {
        "adjudication_id": "adjudication.presentation.alert-subscription-composite.v1",
        "record_kind": "presentation_composite_retirement_adjudication",
        "subject_ref": "candidate.product.alert_subscription",
        "verdict": "RETIRE_COMPOSITE_AND_REALLOCATE_MEANINGS",
        "supersedes_decision_ref": "decision.consumption.alert_subscription",
        "reason": "Alert rule, evaluation, subscription, notification workflow, delivery attempt, interaction receipt and escalation do not share one owner, consistency boundary or authority.",
        "evidence_refs": sorted(set(ALERT_REFS + NOTIFICATION_REFS)),
        "ratification": "WITHHELD",
        "completion_claim": False,
    },
]


OWNERSHIP_ROWS = [
    ("alert_rule", "PRODUCING_ANALYTICAL_PRODUCT", "The producer owns threshold/query meaning and rule edition."),
    ("alert_evaluation", "PRODUCING_ANALYTICAL_PRODUCT", "Evaluation occurs against the producer's typed result and time model."),
    ("alert_occurrence", "PRODUCING_ANALYTICAL_PRODUCT", "An occurrence is evidence from one rule evaluation, not a notification."),
    ("content_subscription", "CONTENT_PRODUCER_PRODUCT", "The report, dashboard or notebook owner defines what edition/cut is subscribed to."),
    ("subscription_schedule", "CONTENT_PRODUCER_PRODUCT", "Content scheduling remains bound to product-specific parameters and run semantics."),
    ("attention_intent", "SHARED_PUBLISHED_LANGUAGE", "A minimized typed request crosses from a producer into communication infrastructure."),
    ("notification_workflow", "EXTERNAL_NOTIFICATION_PRODUCT", "The generic notification product owns channel-independent delivery orchestration."),
    ("recipient_projection", "EXTERNAL_NOTIFICATION_PRODUCT_IMPORTING_IDENTITY_POLICY", "It projects recipients but does not establish enterprise identity or purpose authority."),
    ("preference_snapshot", "EXTERNAL_NOTIFICATION_PRODUCT", "Recipient/channel preferences are evaluated at a versioned occurrence."),
    ("message_template", "EXTERNAL_NOTIFICATION_PRODUCT", "Communication presentation is distinct from analytical content presentation."),
    ("delivery_attempt", "EXTERNAL_NOTIFICATION_PRODUCT", "Each provider/channel attempt has distinct identity and retry state."),
    ("delivery_outcome", "EXTERNAL_NOTIFICATION_PRODUCT", "Accepted, rejected, deferred, bounced and unknown are transport outcomes."),
    ("interaction_receipt", "EXTERNAL_NOTIFICATION_PRODUCT", "Open/click/dismiss/ack interaction can be recorded but is not business acceptance."),
    ("incident_escalation", "IMPORTED_INCIDENT_OR_CASE_WORKFLOW", "Operational escalation changes a case/incident process and needs that owner's authority."),
    ("business_acknowledgment", "DOMAIN_WORKFLOW_OWNER", "A human business acknowledgment is a domain fact, not inferred from delivery or interaction."),
    ("content_artifact", "PRODUCING_ANALYTICAL_PRODUCT", "Notebook/report/dashboard/planning artifacts retain their product-specific aggregate roots."),
    ("content_container", "SHARED_CONTENT_CONTROL_PLANE", "Workspace/project/folder organization is reusable but not yet a standalone product."),
    ("content_membership", "SHARED_CONTENT_CONTROL_PLANE_IMPORTING_IDENTITY_POLICY", "Membership projects policy; it does not author identity or access policy."),
    ("comment_thread", "SHARED_CONTENT_CONTROL_PLANE", "Thread identity and moderation are reusable across analytical content kinds."),
    ("annotation_anchor", "SHARED_CONTENT_LIBRARY", "Anchors bind to exact target identity/edition/region without owning the target."),
    ("review_request", "SHARED_CONTENT_CONTROL_PLANE", "Review state is reusable; product-specific approval remains with the artifact owner."),
    ("formal_issuance", "FORMAL_REPORTING_PRODUCT", "Issuance and recall remain formal-report authority."),
]

OWNERSHIP_MATRIX = [
    {"ownership_id": f"ownership.presentation.{meaning.replace('_', '-')}", "record_kind": "presentation_vacancy_meaning_allocation", "meaning": meaning, "proposed_owner": owner, "law": law, "status": "PROPOSED_UNRATIFIED", "completion_claim": False}
    for meaning, owner, law in OWNERSHIP_ROWS
]


LIBRARY_ROWS = [
    ("library.content.content_ref", "SHARED_CONTENT_LIBRARY", "Stable heterogeneous content identity and kind reference."),
    ("library.content.container_tree", "SHARED_CONTENT_CONTROL_PLANE", "Workspace/project/folder containment with cycle and cardinality laws."),
    ("library.content.membership_roles", "SHARED_CONTENT_CONTROL_PLANE", "Editioned membership and role projection."),
    ("library.content.access_projection", "SHARED_CONTENT_CONTROL_PLANE", "Policy-decision projection with provenance and expiry."),
    ("library.content.ownership_transfer", "SHARED_CONTENT_CONTROL_PLANE", "Explicit transfer, orphan and recovery state."),
    ("library.content.edition_link", "SHARED_CONTENT_LIBRARY", "Links product-owned editions without pretending to version their internals."),
    ("library.content.annotation_anchor", "SHARED_CONTENT_LIBRARY", "Target/body/motivation/selector/provenance binding."),
    ("library.content.comment_thread", "SHARED_CONTENT_CONTROL_PLANE", "Thread, message, mention, resolution and moderation lifecycle."),
    ("library.content.review_request", "SHARED_CONTENT_CONTROL_PLANE", "Reviewer assignment, response and evidence without product approval authority."),
    ("library.content.release_collection", "SHARED_CONTENT_LIBRARY", "Named collection of exact product-owned artifact editions."),
    ("library.content.collaboration_sync", "SHARED_CONTENT_RUNTIME", "Concurrent edit awareness and conflict contract."),
    ("library.content.activity_receipt", "SHARED_CONTENT_LIBRARY", "Append-only collaboration occurrence evidence."),
    ("library.content.portable_export", "SHARED_CONTENT_LIBRARY", "Provider-neutral containers, references, threads, reviews and active-work export."),
    ("library.attention.intent", "SHARED_PUBLISHED_LANGUAGE", "Typed minimized communication request."),
    ("library.attention.dedup_key", "SHARED_PUBLISHED_LANGUAGE", "Producer-scoped occurrence and replacement identity."),
    ("library.notification.workflow", "EXTERNAL_NOTIFICATION_PRODUCT", "Channel-independent workflow and step graph."),
    ("library.notification.preference", "EXTERNAL_NOTIFICATION_PRODUCT", "Recipient/tenant/workflow/channel preference algebra."),
    ("library.notification.schedule", "EXTERNAL_NOTIFICATION_PRODUCT", "Timezone/calendar/recurrence schedule state."),
    ("library.notification.audience_projection", "EXTERNAL_NOTIFICATION_PRODUCT", "Bounded recipient projection importing identity and policy."),
    ("library.notification.template", "EXTERNAL_NOTIFICATION_PRODUCT", "Editioned channel template and localization binding."),
    ("library.notification.routing", "EXTERNAL_NOTIFICATION_PRODUCT", "Condition, channel, fallback and provider routing plan."),
    ("library.notification.batch_digest", "EXTERNAL_NOTIFICATION_PRODUCT", "Batch/window/digest grouping semantics."),
    ("library.notification.throttle_budget", "EXTERNAL_NOTIFICATION_PRODUCT", "Finite rate, quota and interruption budget."),
    ("library.notification.delivery_attempt", "EXTERNAL_NOTIFICATION_PRODUCT", "Attempt identity, idempotency and retry state."),
    ("library.notification.delivery_outcome", "EXTERNAL_NOTIFICATION_PRODUCT", "Typed provider/channel outcome and uncertainty."),
    ("library.notification.interaction_receipt", "EXTERNAL_NOTIFICATION_PRODUCT", "Open, click, dismiss and explicit interaction evidence."),
    ("library.notification.provider_port", "EXTERNAL_NOTIFICATION_PRODUCT", "Qualified email/SMS/push/chat/webhook provider interface."),
    ("library.notification.evidence_bundle", "EXTERNAL_NOTIFICATION_PRODUCT", "Intent-to-attempt-to-outcome provenance chain."),
]

LIBRARY_SEAMS = [
    {"library_ref": ref, "record_kind": "presentation_vacancy_library_seam", "owner_posture": owner, "purpose": purpose, "required_contract_surface": ["types", "operations", "invariants", "state", "time", "authority", "partiality", "failures", "resources", "compatibility", "evidence", "ports", "oracles"], "status": "CANDIDATE_UNRATIFIED", "completion_claim": False}
    for ref, owner, purpose in LIBRARY_ROWS
]


NONCOLLAPSE = [
    ("alert-notification", "alert_occurrence != notification_delivery_attempt"),
    ("rule-workflow", "analytical_alert_rule != notification_workflow"),
    ("subscription-schedule", "content_subscription != notification_schedule"),
    ("delivered-ack", "delivery_outcome != human_acknowledgment"),
    ("interaction-acceptance", "interaction_receipt != business_acceptance"),
    ("escalation-routing", "incident_escalation != notification_channel_fallback"),
    ("preference-consent", "recipient_preference != legal_consent_or_purpose_authority"),
    ("recipient-identity", "recipient_projection != enterprise_identity"),
    ("template-content", "notification_template != analytical_content_artifact"),
    ("retry-occurrence", "delivery_retry != new_analytical_alert_occurrence"),
    ("container-artifact", "content_container != analytical_artifact"),
    ("edition-version", "content_index_version != product_owned_artifact_edition"),
    ("comment-claim", "comment != analytical_claim"),
    ("review-approval", "collaboration_review != product_specific_approval"),
    ("share-disclose", "content_share != authorized_disclosure"),
    ("workspace-policy", "workspace_membership != access_policy_authority"),
    ("release-issuance", "release_collection != formal_report_issuance"),
    ("sync-merge", "collaborative_sync_merge != semantic_compatibility"),
    ("mention-assignment", "mention != accountable_work_assignment"),
    ("presence-authorship", "editor_presence != accepted_authorship"),
]

VACANCY_LAWS = [
    {"law_id": f"law.presentation.vacancy.{ident}", "record_kind": "presentation_vacancy_noncollapse_law", "law": law, "status": "EVIDENCE_BACKED_UNRATIFIED", "completion_claim": False}
    for ident, law in NONCOLLAPSE
]


COMPILER_WIRING = [
    {"transform_id": "transform.presentation.alert-to-attention-intent", "record_kind": "presentation_vacancy_compiler_transform", "owner": "PRODUCING_ANALYTICAL_PRODUCT", "input": ["AlertOccurrence", "AudienceIntent", "Urgency", "PurposeRef"], "output": "AttentionIntent", "refusals": ["alert_occurrence_unproved", "audience_authority_missing", "purpose_missing", "payload_minimization_failed"], "effect": "PURE_INTENT_CONSTRUCTION"},
    {"transform_id": "transform.presentation.subscription-to-attention-intent", "record_kind": "presentation_vacancy_compiler_transform", "owner": "CONTENT_PRODUCER_PRODUCT", "input": ["ContentSubscription", "ContentArtifactEdition", "DataCutRef", "ScheduleOccurrence"], "output": "AttentionIntent", "refusals": ["content_edition_unresolved", "data_cut_unclosed", "schedule_ambiguous", "subscriber_unauthorized"], "effect": "PURE_INTENT_CONSTRUCTION"},
    {"transform_id": "transform.notification.intent-to-routing-plan", "record_kind": "presentation_vacancy_compiler_transform", "owner": "EXTERNAL_NOTIFICATION_PRODUCT", "input": ["AttentionIntent", "RecipientProjection", "PreferenceSnapshot", "PolicyDecision", "WorkflowEdition", "ProviderOffers"], "output": "NotificationRoutingPlan", "refusals": ["recipient_unresolved", "preference_unknown", "policy_denied", "workflow_invalid", "no_qualified_channel", "budget_exhausted"], "effect": "PURE_PLAN"},
    {"transform_id": "transform.notification.plan-to-delivery-attempt", "record_kind": "presentation_vacancy_compiler_transform", "owner": "EXTERNAL_NOTIFICATION_PRODUCT", "input": ["NotificationRoutingPlan", "QualifiedProviderBinding", "IdempotencyKey", "DeliveryBudget"], "output": "DeliveryAttempt", "refusals": ["provider_unqualified", "idempotency_conflict", "rate_limited", "cancelled", "timeout", "provider_outcome_unknown"], "effect": "EXTERNAL_COMMUNICATION_EFFECT"},
    {"transform_id": "transform.notification.attempt-to-receipt", "record_kind": "presentation_vacancy_compiler_transform", "owner": "EXTERNAL_NOTIFICATION_PRODUCT", "input": ["DeliveryAttempt", "ProviderOutcome"], "output": "DeliveryReceipt", "refusals": ["outcome_unverifiable", "attempt_identity_mismatch", "late_conflicting_outcome"], "effect": "EVIDENCE_REDUCTION"},
    {"transform_id": "transform.content.references-to-portable-export", "record_kind": "presentation_vacancy_compiler_transform", "owner": "SHARED_CONTENT_CONTROL_PLANE", "input": ["ContainerGraph", "MembershipEditions", "ContentRefs", "AnnotationThreads", "ReviewCases", "ActiveWorkDisposition"], "output": "PortableContentControlPlaneExport", "refusals": ["containment_cycle", "artifact_ref_unresolved", "policy_projection_missing", "annotation_anchor_invalid", "active_work_unclassified"], "effect": "PURE_EXPORT_CONSTRUCTION"},
]


def notification_ddd() -> dict[str, Any]:
    roots = ["NotificationWorkflow", "NotificationSchedule", "NotificationTrigger", "DeliveryAttempt"]
    commands = ["create_workflow", "revise_workflow", "activate_workflow", "suspend_workflow", "create_schedule", "trigger_notification", "plan_delivery", "attempt_delivery", "record_provider_outcome", "record_interaction", "cancel_trigger", "retire_workflow"]
    return {
        "dossier_id": "ddd.external.notification-orchestration-delivery",
        "record_kind": "external_candidate_product_ddd_dossier",
        "product_ref": "external.product.notification_orchestration_delivery",
        "status": "COMPLETE_CANDIDATE_NOT_RATIFIED",
        "product_truth": {"sovereign_question": "How can an application turn an authorized minimized communication intent into preference-aware multi-channel delivery attempts and evidence without acquiring the triggering domain's meaning or decision authority?", "users": ["notification_platform_engineer", "communication_operator", "application_integrator", "support_operator"], "harmed_parties": ["recipient", "data_subject", "unintended_recipient", "over_notified_user"], "jobs": ["define notification workflows", "project recipients and preferences", "route and deliver through qualified providers", "preserve outcomes and interaction evidence"], "negative_mission": "Does not own analytical rules, source truth, enterprise identity, legal purpose, business acceptance, incident disposition or downstream action."},
        "strategic_and_tactical_ddd": {
            "domain_vision_statement": "Own bounded communication workflow, routing, delivery attempts and receipts across applications.",
            "subdomain_classification": "generic_cross_domain_infrastructure_product",
            "bounded_context_boundary": {"inside": ["workflow and step editions", "trigger occurrences", "preference snapshots", "recipient projections", "templates", "schedules", "routing plans", "delivery attempts and outcomes", "interaction receipts", "provider ports"], "outside": ["triggering domain semantics", "analytical alert evaluation", "content subscription meaning", "identity and access authority", "legal consent and purpose", "business acknowledgment", "incident/case escalation", "provider internals"]},
            "ubiquitous_language_policy": "Intent, workflow, trigger, recipient, preference, template, route, attempt, delivery outcome and interaction receipt each have one non-interchangeable meaning.",
            "context_map": [{"neighbor_ref": "analytical_product_producers", "relationship": "open_host_published_language"}, {"neighbor_ref": "identity_policy_authority", "relationship": "conformist_acl"}, {"neighbor_ref": "incident_case_workflow", "relationship": "customer_supplier"}, {"neighbor_ref": "channel_providers", "relationship": "anti_corruption_layer"}],
            "anti_corruption_layers": ["acl.attention_intent", "acl.identity_policy", "acl.channel_provider", "acl.case_workflow"],
            "published_language": ["AttentionIntent", "NotificationRoutingPlan", "DeliveryAttempt", "DeliveryReceipt", "InteractionReceipt", "TypedRefusal"],
            "value_objects": ["WorkflowId", "WorkflowEdition", "TriggerId", "RecipientRef", "PreferenceSnapshotRef", "TemplateEditionRef", "ChannelKind", "ProviderOfferRef", "IdempotencyKey", "DeliveryBudget", "PurposeRef", "EvidenceDigest"],
            "entities": roots + ["PreferenceProfile", "MessageTemplate", "ProviderBinding"],
            "aggregates": [{"root": root, "consistency": "one accepted command advances exactly one version; cross-root processes use receipts"} for root in roots],
            "aggregate_roots": roots,
            "aggregate_invariants": ["trigger occurrence and delivery attempt identities are distinct", "every attempt binds exact intent workflow preference policy template route and provider editions", "retry creates a new attempt", "recipient preference never grants legal or business authority", "provider acceptance is not recipient delivery", "delivery is not interaction", "interaction is not business acknowledgment", "unknown outcome remains unknown", "revocation and suppression propagate without deleting history"],
            "commands": commands,
            "domain_events": [f"{command}_accepted" for command in commands],
            "refusal_failure_catalog": ["intent_invalid", "purpose_missing", "recipient_unresolved", "preference_unknown", "policy_denied", "workflow_inactive", "template_invalid", "schedule_ambiguous", "no_qualified_channel", "provider_unqualified", "budget_exhausted", "rate_limited", "idempotency_conflict", "cancelled", "timeout", "provider_outcome_unknown", "late_conflicting_outcome"],
            "domain_services": ["RecipientProjectionService", "PreferenceEvaluationService", "RoutingPlanService", "ProviderSelectionService", "DeliveryEvidenceService"],
            "application_services": ["WorkflowAdministrationUseCase", "TriggerUseCase", "DeliveryUseCase", "ReplayUseCase", "ProviderMigrationUseCase", "RetirementUseCase"],
            "repositories": [root + "Repository" for root in roots] + ["EvidenceRepository"],
            "factories": [root + "Factory" for root in roots],
            "specifications": ["IntentAdmissibilitySpecification", "RecipientEligibilitySpecification", "ChannelFitnessSpecification", "DeliveryReadinessSpecification", "ProviderQualificationSpecification"],
            "state_machine": {"NotificationWorkflow": ["draft", "validated", "active", "suspended", "superseded", "retired"], "NotificationTrigger": ["received", "admitted", "planned", "partially_delivered", "completed", "cancelled", "expired"], "DeliveryAttempt": ["planned", "submitted", "provider_accepted", "delivered", "rejected", "bounced", "deferred", "cancelled", "unknown"]},
            "policies_and_reactions": ["when an admitted trigger arrives evaluate preferences and policy before planning", "when a provider attempt fails apply only the editioned retry/fallback policy", "when consent policy or recipient eligibility changes suppress future attempts", "when a late provider outcome conflicts open an evidence conflict"],
            "sagas_and_process_managers": ["MultiChannelDeliveryProcess", "ProviderFallbackProcess", "WorkflowMigrationProcess", "TriggerCancellationProcess"],
            "read_models_and_projections": ["WorkflowStatusView", "TriggerJourneyView", "DeliveryAttemptView", "RecipientPreferenceView", "ProviderHealthView", "EvidenceChainView"],
            "integration_event_policy": "Only minimized typed intents, plans, attempts, outcomes, interaction receipts and refusals cross boundaries; provider DTOs, secrets and triggering-domain internals do not.",
            "concurrency_and_idempotency": ["optimistic workflow edition compare-and-swap", "producer-scoped trigger idempotency", "new identity per delivery attempt", "single-winner terminal outcome with explicit conflict evidence"],
            "time_model": ["intent event and recording time are distinct", "schedule timezone/calendar/edition are explicit", "preference and policy are evaluated as-of an exact cut", "attempt submit provider-accept delivery and interaction times are distinct", "expiry and quiet windows are explicit"],
            "event_storming_swimlanes": ["producer_application", "notification_control_plane", "identity_policy", "recipient_preference", "provider_adapter", "recipient", "case_workflow", "evidence_store"],
            "nonfunctional_laws": ["finite precharged delivery budgets", "cooperative cancellation", "total typed outcomes", "provider-neutral ports", "at-least-once transport never becomes exactly-once human attention", "privacy minimization", "deterministic core", "complete replayable evidence chain"],
        },
        "completion_claim": False,
    }


VACANCY_DDD_DOSSIERS = [notification_ddd()]
