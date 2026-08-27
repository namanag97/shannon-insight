#!/usr/bin/env python3
"""Complete notebook and embedded-analytics DDDs and close BI authoring coverage."""

from __future__ import annotations

from typing import Any


DDD_FIELDS = {
    "domain_vision_statement", "subdomain_classification", "bounded_context_boundary",
    "ubiquitous_language_policy", "context_map", "anti_corruption_layers", "published_language",
    "value_objects", "entities", "aggregates", "aggregate_roots", "aggregate_invariants",
    "commands", "domain_events", "refusal_failure_catalog", "domain_services",
    "application_services", "repositories", "factories", "specifications", "state_machine",
    "policies_and_reactions", "sagas_and_process_managers", "read_models_and_projections",
    "integration_event_policy", "concurrency_and_idempotency", "time_model",
    "event_storming_swimlanes", "nonfunctional_laws",
}

AUTOMATION = {
    "default": "DETERMINISTIC_CORE_ONLY",
    "postures": ["PROHIBITED", "OPTIONAL", "REQUIRED_BY_INTENT", "UNDETERMINED"],
    "law": "A model or agent may propose text, code, layout, parameters, narratives or interaction candidates; typed notebook, embed, semantic, authority, execution and evidence contracts decide whether they enter the product.",
    "removal_law": "Removing every optional model or agent extension preserves deterministic document editing, validation, semantic binding, session isolation, authority checks, execution planning, rendering and evidence capture.",
    "hard_work_law": "Automation never replaces domain vocabulary, semantic ownership, invariants, accessibility, tenant isolation, exact execution, qualification, disclosure authority or acceptance.",
}


def _notebook_dossier() -> dict[str, Any]:
    product = "product.analytical_notebook"
    truth = {
        "sovereign_question": "How can an analyst create and reproduce an editioned analytical narrative whose cells, dependencies, environment, data cuts, parameters, executions, outputs and evidence remain distinguishable and inspectable?",
        "users": ["analyst", "data_scientist", "researcher", "reviewer", "notebook_operator", "reproducibility_reviewer"],
        "harmed_parties": ["decision_subject", "data_subject", "misled_consumer", "source_owner", "runtime_operator"],
        "jobs": ["author notebook documents", "bind semantic and data dependencies", "declare executable environments", "plan and request executions", "capture outputs and receipts", "replay compare review publish archive and retire notebook editions"],
        "measurable_outcomes": ["replay_success_for_frozen_inputs", "environment_and_data_cut_closure", "stale_output_detection", "cell_dependency_traceability", "execution_receipt_completeness", "reviewed_publication_rate"],
        "negative_mission": "Does not own metric, method or source truth; a notebook is not a kernel, environment, execution, result truth, model registry, workflow orchestrator, report, or effect authority.",
    }
    ddd = {
        "domain_vision_statement": "Own an editioned analytical document and its reproducibility evidence while importing semantic meaning and runtime execution through explicit contracts.",
        "subdomain_classification": {"core": ["notebook_document_graph", "cell_and_dependency_semantics", "execution_manifest_and_output_binding", "reproducibility_evidence"], "supporting": ["collaboration_review", "publication", "archive_and_retirement", "interactive_session_state"], "generic_or_imported": ["code_editor", "kernel_runtime", "package_resolution", "query_execution", "semantic_metrics", "data_access_policy", "object_storage", "version_control"]},
        "bounded_context_boundary": {"inside": ["notebook and cell identities", "document editions", "cell dependency graph", "parameter and environment declarations", "data-cut bindings", "execution requests and receipts", "output references", "replay comparison", "review publication archive and retirement"], "outside": ["language semantics", "kernel implementation", "package repository truth", "metric and method meaning", "source data", "resource scheduling", "security policy", "downstream business decisions"]},
        "ubiquitous_language_policy": {"terms": {"NotebookDocument": "editioned ordered document graph", "Cell": "identified source narrative query visualization or control node", "KernelSession": "runtime occurrence, not notebook identity", "ExecutionManifest": "frozen code environment parameter data and dependency cut", "ExecutionRun": "one attempt against one manifest", "OutputArtifact": "bytes or structured result bound to a producing receipt", "ReproductionResult": "comparison under an exact oracle"}, "homonym_rules": ["document is not session", "cell order is not dependency order", "stored output is not current result", "rerun is not reproduction proof", "published notebook is not report truth"]},
        "context_map": [{"neighbor_ref": "neighbor.semantic_metric", "relationship": "customer_supplier", "translation": "bind exact semantic query and formula editions"}, {"neighbor_ref": "neighbor.query_engine", "relationship": "customer_supplier_acl", "translation": "submit typed query intents and consume receipts"}, {"neighbor_ref": "product.runtime_resource_control", "relationship": "customer_supplier", "translation": "submit work units and consume attempt receipts"}, {"neighbor_ref": "neighbor.identity_policy", "relationship": "conformist_at_authority_gate", "translation": "import principal purpose access and disclosure decisions"}, {"neighbor_ref": "product.bi_reporting", "relationship": "published_language", "translation": "export reviewed presentation artifacts without transferring notebook identity"}],
        "anti_corruption_layers": ["acl.language_kernel", "acl.package_environment", "acl.semantic_query", "acl.source_data_cut", "acl.runtime_attempt", "acl.identity_policy", "acl.output_renderer"],
        "published_language": ["NotebookId", "NotebookEdition", "CellId", "CellKind", "CellDependency", "ParameterBinding", "EnvironmentManifest", "DataCutManifest", "ExecutionManifest", "ExecutionRequest", "ExecutionRun", "ExecutionReceipt", "OutputArtifactRef", "ReproductionProfile", "ReproductionResult", "NotebookPublication"],
        "value_objects": ["NotebookId", "NotebookEdition", "CellId", "CellPosition", "CellKind", "SourceDigest", "DependencyRef", "ParameterName", "ParameterValue", "EnvironmentDigest", "DataCutRef", "ExecutionManifestDigest", "KernelProfileRef", "OutputDigest", "EvidenceRef"],
        "entities": ["NotebookDocument", "Cell", "ExecutionManifest", "ExecutionRun", "OutputArtifact", "ReviewCase", "NotebookPublication", "ReproductionAssessment"],
        "aggregates": [{"root": "NotebookDocument", "members": ["edition", "cells", "dependency_graph", "parameters", "environment_declaration", "publication_state"], "consistency": "one edit produces one immutable edition whose cell identities and graph are closed"}, {"root": "ExecutionRun", "members": ["manifest", "attempt_ref", "cell_receipts", "outputs", "outcome"], "consistency": "one run binds one immutable manifest and never overwrites a prior attempt"}, {"root": "ReproductionAssessment", "members": ["baseline_run", "candidate_run", "profile", "comparisons", "residuals", "verdict"], "consistency": "equivalence is claimed only under a named exact oracle and tolerances"}],
        "aggregate_roots": ["NotebookDocument", "ExecutionRun", "ReproductionAssessment"],
        "aggregate_invariants": ["notebook document kernel session execution run and output identities are distinct", "cell order never implies an undeclared dependency", "every executable run binds exact document environment parameter dependency and data-cut editions", "stored output never silently becomes current after an upstream change", "retry creates a new execution occurrence", "nondeterminism randomness clock network and ambient state are declared or reproduction is refused", "a narrative or generated cell cannot redefine imported semantic meaning", "publication approval disclosure and downstream action are separate authorities"],
        "commands": ["create_notebook", "add_cell", "edit_cell", "move_cell", "declare_cell_dependency", "bind_semantic_reference", "bind_data_cut", "bind_environment", "set_parameter", "freeze_execution_manifest", "request_execution", "record_cell_receipt", "record_output_artifact", "cancel_execution", "request_reproduction", "compare_runs", "submit_review", "publish_notebook", "archive_notebook", "retire_notebook"],
        "domain_events": ["notebook_created", "cell_added", "cell_edited", "cell_moved", "cell_dependency_declared", "semantic_reference_bound", "data_cut_bound", "environment_bound", "parameter_set", "execution_manifest_frozen", "execution_requested", "cell_receipt_recorded", "output_artifact_recorded", "execution_cancelled", "reproduction_requested", "runs_compared", "notebook_review_submitted", "notebook_published", "notebook_archived", "notebook_retired"],
        "refusal_failure_catalog": ["notebook_edition_conflict", "cell_identity_conflict", "dependency_cycle", "semantic_reference_unresolved", "data_cut_unavailable", "environment_unclosed", "package_lock_missing", "parameter_invalid", "ambient_dependency_undeclared", "kernel_offer_unqualified", "execution_authority_missing", "runtime_outcome_unknown", "output_digest_mismatch", "reproduction_oracle_missing", "numerical_tolerance_undefined", "publication_evidence_incomplete"],
        "domain_services": ["NotebookGraphService", "ExecutionManifestClosureService", "StaleOutputDetectionService", "RuntimeRequestService", "OutputBindingService", "ReproductionEvaluationService", "NotebookPublicationService"],
        "application_services": ["AuthorNotebookUseCase", "ExecuteNotebookUseCase", "CancelNotebookRunUseCase", "ReproduceNotebookUseCase", "ReviewNotebookUseCase", "PublishNotebookUseCase", "ArchiveNotebookUseCase"],
        "repositories": ["NotebookDocumentRepository", "ExecutionManifestRepository", "ExecutionRunRepository", "OutputArtifactRepository", "ReproductionAssessmentRepository", "NotebookPublicationRepository"],
        "factories": ["NotebookDocumentFactory", "CellFactory", "ExecutionManifestFactory", "ExecutionRunFactory", "OutputArtifactFactory", "ReproductionAssessmentFactory"],
        "specifications": ["NotebookGraphClosureSpecification", "ExecutionManifestClosureSpecification", "EnvironmentReproducibilitySpecification", "DataCutAvailabilitySpecification", "CellExecutionReadinessSpecification", "OutputFreshnessSpecification", "ReproductionEquivalenceSpecification", "NotebookPublicationReadinessSpecification"],
        "state_machine": {"NotebookDocument": ["draft", "dependencies_bound", "execution_ready", "review_pending", "published", "suspended", "archived", "retired"], "ExecutionRun": ["planned", "queued", "running", "cancellation_requested", "succeeded", "failed", "cancelled", "unknown"], "ReproductionAssessment": ["requested", "inputs_validated", "running", "comparison_pending", "equivalent", "different", "inconclusive", "refused"], "law": "document edits create new editions, runs are append-only, and provider timeouts remain unknown until reconciled"},
        "policies_and_reactions": ["when a cell source or dependency changes mark supported downstream outputs stale", "when environment or data-cut evidence expires suspend reproducibility claims", "when execution is requested emit a work intent without authorizing the runtime effect", "when a run completes bind outputs only to matching manifest and attempt receipts", "when optional generated content arrives typecheck and review it like any authored cell"],
        "sagas_and_process_managers": ["NotebookExecutionProcess", "LongRunningCellProcess", "CancellationReconciliationProcess", "NotebookReproductionProcess", "NotebookReviewPublicationProcess", "NotebookArchiveProcess"],
        "read_models_and_projections": ["NotebookOutlineView", "CellDependencyGraphView", "ExecutionReadinessView", "RunTimelineView", "StaleOutputView", "EnvironmentAndDataCutView", "ReproductionDiffView", "NotebookPublicationView"],
        "integration_event_policy": "Only editioned document, manifest, execution intent, receipt, output reference, reproduction and publication contracts cross the boundary; live kernel memory, secrets, provider DTOs and unreviewed generated content remain internal or external.",
        "concurrency_and_idempotency": ["document edits use optimistic notebook edition", "cell identities survive moves", "manifest freezing is content-addressed", "execution idempotency binds manifest and request identity", "retries receive new attempt identities", "output writes require manifest attempt and digest match", "publication is single-winner per edition"],
        "time_model": ["document validity and recording time differ", "data-cut validity differs from execution time", "environment evidence and package availability can expire independently", "cell start completion and observation time are explicit", "published outputs retain original run time and later invalidation", "replay time never rewrites historical inputs"],
        "event_storming_swimlanes": ["analyst", "reviewer", "notebook_document_service", "semantic_registry", "data_access_authority", "environment_resolver", "runtime_control", "kernel_backend", "artifact_store", "publication_authority"],
        "nonfunctional_laws": ["canonical deterministic document and manifest encoding", "finite cell graph output runtime and replay budgets", "cooperative cancellation with partial and unknown outcomes", "no hidden network clock filesystem randomness or environment dependency in reproducibility claims", "provider-neutral kernel and runtime ports", "complete source-to-output evidence", "accessible document navigation", "optional model or agent removal preserves the deterministic notebook core"],
    }
    assert set(ddd) == DDD_FIELDS
    return {"dossier_id": "ddd.consumption.analytical_notebook", "product_ref": product, "status": "candidate_not_ratified", "product_truth": truth, "strategic_and_tactical_ddd": ddd}


def _embedded_dossier() -> dict[str, Any]:
    product = "product.embedded_analytics"
    truth = {
        "sovereign_question": "How can a host application expose an analytical surface to the correct tenant principal and purpose with exact semantic, interaction, accessibility, isolation, disclosure and lifecycle contracts without inheriting or granting authority implicitly?",
        "users": ["host_application_team", "analytics_product_owner", "tenant_administrator", "embedded_consumer", "security_reviewer", "support_operator"],
        "harmed_parties": ["data_subject", "cross_tenant_user", "host_application_user", "source_owner", "decision_subject"],
        "jobs": ["define embeddable analytical surfaces", "bind tenant principal purpose and entitlements", "issue short-lived embed grants", "open isolated sessions", "bridge parameters filters interactions and events", "render accessible localized results", "revoke suspend audit and retire integrations"],
        "measurable_outcomes": ["tenant_isolation_test_pass", "embed_session_start_latency", "grant_and_revocation_propagation", "interaction_contract_conformance", "accessibility_target_pass", "cross_origin_and_data_leak_incidents", "host_upgrade_compatibility"],
        "negative_mission": "Does not own host identity, tenant membership, policy, metric meaning, query execution, source data, business workflow, downstream action, or a general BI authoring experience.",
    }
    ddd = {
        "domain_vision_statement": "Own a versioned isolation-safe bridge between a host application and governed analytical presentation sessions.",
        "subdomain_classification": {"core": ["embed_contract", "tenant_and_principal_session_binding", "interaction_bridge", "host_analytics_lifecycle"], "supporting": ["presentation adaptation", "accessibility_and_localization", "session audit", "revocation_and_recovery"], "generic_or_imported": ["identity_provider", "authorization_policy", "semantic_metrics", "query_execution", "browser_or_native_sandbox", "notification", "host_routing"]},
        "bounded_context_boundary": {"inside": ["embed definition editions", "host integration contract", "guest/embed grants", "tenant-principal-purpose session binding", "parameter filter navigation and interaction bridge", "presentation adaptation", "session receipts", "revocation suspension compatibility and retirement"], "outside": ["host authentication truth", "tenant authority", "metric and query meaning", "data access policy", "query engine", "host business workflow", "business decisions and effects"]},
        "ubiquitous_language_policy": {"terms": {"EmbedDefinition": "versioned analytical surface and bridge contract", "HostApplication": "external integrating application, not an authority imported by trust", "EmbedGrant": "short-lived scoped permission reference", "EmbeddedSession": "tenant-principal-purpose-bound presentation occurrence", "InteractionBridge": "allowed host-to-analytics and analytics-to-host messages", "HostActionIntent": "non-authoritative request requiring host validation"}, "homonym_rules": ["frame is not session", "host login is not analytics authorization", "tenant hint is not tenant truth", "interaction event is not action authority", "presentation state is not semantic query state"]},
        "context_map": [{"neighbor_ref": "neighbor.identity_policy", "relationship": "conformist_at_authority_gate", "translation": "verify principal tenant purpose entitlement and revocation"}, {"neighbor_ref": "product.bi_reporting", "relationship": "customer_supplier", "translation": "consume editioned presentation definitions and state reducers"}, {"neighbor_ref": "neighbor.semantic_metric", "relationship": "customer_supplier", "translation": "bind exact semantic query editions"}, {"neighbor_ref": "neighbor.query_engine", "relationship": "customer_supplier_acl", "translation": "submit typed queries under session authority"}, {"neighbor_ref": "host.application", "relationship": "anti_corruption_layer", "translation": "translate routes parameters events and action intents through a versioned bridge"}],
        "anti_corruption_layers": ["acl.host_identity", "acl.tenant_context", "acl.host_route_and_parameter", "acl.semantic_query", "acl.query_result", "acl.browser_native_sandbox", "acl.host_action"],
        "published_language": ["EmbedDefinitionId", "EmbedDefinitionEdition", "HostApplicationRef", "EmbedGrant", "TenantContext", "PrincipalContext", "PurposeRef", "EmbeddedSessionId", "AllowedParameter", "InteractionMessage", "HostActionIntent", "SessionReceipt", "RevocationNotice", "CompatibilityProfile"],
        "value_objects": ["EmbedDefinitionId", "EmbedEdition", "HostApplicationId", "TenantRef", "PrincipalRef", "PurposeRef", "AudienceRef", "GrantId", "GrantExpiry", "SessionId", "OriginRef", "RouteRef", "ParameterBinding", "InteractionKind", "MessageNonce", "PolicyDecisionRef"],
        "entities": ["EmbedDefinition", "HostIntegration", "EmbedGrant", "EmbeddedSession", "InteractionBridge", "CompatibilityAssessment", "RevocationCase"],
        "aggregates": [{"root": "EmbedDefinition", "members": ["surface_ref", "allowed_hosts", "parameters", "interactions", "accessibility_profile", "compatibility"], "consistency": "published edition is immutable and every bridge direction and message is allowlisted"}, {"root": "EmbeddedSession", "members": ["grant", "tenant", "principal", "purpose", "surface_edition", "presentation_state", "interaction_log", "lifecycle"], "consistency": "session authority and tenant scope are fixed or explicitly re-authorized"}, {"root": "HostIntegration", "members": ["host_identity", "origins", "routes", "bridge_edition", "qualification", "status"], "consistency": "only qualified exact host and bridge editions may issue sessions"}],
        "aggregate_roots": ["EmbedDefinition", "EmbeddedSession", "HostIntegration"],
        "aggregate_invariants": ["host identity tenant principal purpose entitlement and session identity never alias", "embed grants are audience origin purpose tenant principal surface and expiry scoped", "client-supplied tenant context is never trusted without authority verification", "all bridge messages are editioned typed direction-scoped and replay protected", "host action intent is not host effect authority", "cross-tenant cache and session reuse is prohibited", "accessibility localization and responsive adaptation cannot change semantic values", "revocation propagates to active sessions and cached grants"],
        "commands": ["register_host_application", "publish_embed_definition", "qualify_host_integration", "issue_embed_grant", "open_embedded_session", "bind_session_parameter", "apply_embedded_interaction", "emit_host_action_intent", "record_session_receipt", "refresh_session_authority", "revoke_embed_grant", "suspend_host_integration", "upgrade_bridge_edition", "close_embedded_session", "retire_embed_definition"],
        "domain_events": ["host_application_registered", "embed_definition_published", "host_integration_qualified", "embed_grant_issued", "embedded_session_opened", "session_parameter_bound", "embedded_interaction_applied", "host_action_intent_emitted", "session_receipt_recorded", "session_authority_refreshed", "embed_grant_revoked", "host_integration_suspended", "bridge_edition_upgraded", "embedded_session_closed", "embed_definition_retired"],
        "refusal_failure_catalog": ["host_identity_unknown", "origin_not_allowed", "bridge_edition_unsupported", "host_integration_unqualified", "tenant_scope_missing", "principal_unauthorized", "purpose_refused", "entitlement_missing", "grant_expired_or_revoked", "audience_mismatch", "parameter_not_allowed", "interaction_not_allowed", "message_replay", "semantic_binding_stale", "query_or_renderer_unqualified", "cross_tenant_cache_risk", "accessibility_target_unproved", "host_action_authority_missing"],
        "domain_services": ["HostQualificationService", "EmbedGrantService", "TenantSessionBindingService", "InteractionBridgeService", "SessionPolicyRefreshService", "CrossTenantIsolationService", "EmbedCompatibilityService"],
        "application_services": ["RegisterHostUseCase", "PublishEmbedDefinitionUseCase", "OpenEmbeddedSessionUseCase", "InteractWithEmbeddedSurfaceUseCase", "RefreshSessionUseCase", "RevokeEmbedAccessUseCase", "UpgradeHostBridgeUseCase", "RetireEmbedUseCase"],
        "repositories": ["EmbedDefinitionRepository", "HostIntegrationRepository", "EmbedGrantRepository", "EmbeddedSessionRepository", "CompatibilityAssessmentRepository", "RevocationCaseRepository"],
        "factories": ["EmbedDefinitionFactory", "HostIntegrationFactory", "EmbedGrantFactory", "EmbeddedSessionFactory", "InteractionMessageFactory"],
        "specifications": ["HostIdentitySpecification", "OriginAllowlistSpecification", "EmbedGrantScopeSpecification", "TenantSessionIsolationSpecification", "BridgeMessageSpecification", "InteractionAuthorizationSpecification", "CrossTenantCacheSpecification", "EmbedCompatibilitySpecification", "AccessibilityTargetSpecification"],
        "state_machine": {"EmbedDefinition": ["draft", "published", "deprecated", "retired"], "HostIntegration": ["registered", "qualification_pending", "active", "degraded", "suspended", "upgrade_pending", "retired"], "EmbeddedSession": ["grant_pending", "opening", "active", "authority_refresh_pending", "revoked", "expired", "degraded", "closing", "closed", "refused"], "law": "revoked or expired authority dominates interaction acceptance and historical receipts are append-only"},
        "policies_and_reactions": ["when a grant expires or is revoked terminate or restrict every dependent session", "when tenant or principal authority changes refresh before accepting another interaction", "when a host bridge edition changes requalify exact compatibility", "when an action intent is emitted require the host to validate authority independently", "when an optional narrative or layout is proposed validate semantics accessibility and disclosure deterministically"],
        "sagas_and_process_managers": ["HostOnboardingProcess", "EmbedGrantIssuanceProcess", "EmbeddedSessionProcess", "AuthorityRefreshProcess", "RevocationPropagationProcess", "BridgeUpgradeProcess", "EmbedRetirementProcess"],
        "read_models_and_projections": ["EmbedCatalogView", "HostIntegrationStatusView", "ActiveSessionScopeView", "GrantExpiryAndRevocationView", "BridgeCompatibilityView", "InteractionAuditView", "TenantIsolationEvidenceView", "AccessibilityConformanceView"],
        "integration_event_policy": "Only minimized editioned embed, grant, session, interaction-intent, receipt, revocation and compatibility contracts cross the boundary; host tokens, secrets, provider DTOs, raw data and mutable presentation internals do not.",
        "concurrency_and_idempotency": ["grant issuance is idempotent by host tenant principal purpose surface and request", "session opening consumes one scoped grant identity", "session interactions use monotonic session editions and message nonces", "authority refresh and revocation serialize per session", "unknown host or provider completion is reconciled before retry", "cross-tenant keys include tenant and host scope"],
        "time_model": ["host qualification grant validity policy validity and session lifetime are independent", "event occurrence recording and delivery times differ", "revocation effective time dominates cached grant expiry", "semantic and presentation editions may expire independently", "historical session receipts retain original authority and bridge editions"],
        "event_storming_swimlanes": ["host_application", "host_application_team", "embedded_consumer", "tenant_administrator", "identity_policy_authority", "embed_gateway", "presentation_runtime", "semantic_query_service", "query_engine", "support_operator"],
        "nonfunctional_laws": ["fail-closed tenant principal purpose and origin isolation", "finite session interaction render and query budgets", "replay-resistant typed bridge messages", "cooperative cancellation and explicit degraded state", "accessible localized responsive presentation without semantic mutation", "provider-neutral host and renderer ports", "complete session authority interaction and result trace", "optional model or agent removal preserves the deterministic embedded core"],
    }
    assert set(ddd) == DDD_FIELDS
    return {"dossier_id": "ddd.consumption.embedded_analytics", "product_ref": product, "status": "candidate_not_ratified", "product_truth": truth, "strategic_and_tactical_ddd": ddd}


def enrich_remaining_consumption_products(source: dict[str, Any]) -> dict[str, Any]:
    notebook = _notebook_dossier()
    embedded = _embedded_dossier()
    truth_by_product = {notebook["product_ref"]: notebook["product_truth"], embedded["product_ref"]: embedded["product_truth"]}
    for row in source["artifacts"]:
        truth = truth_by_product.get(row.get("artifact_id"))
        if truth:
            row.update({
                "sovereign_question": truth["sovereign_question"],
                "users": truth["users"],
                "harmed_parties": truth["harmed_parties"],
                "jobs": truth["jobs"],
                "outcomes": truth["measurable_outcomes"],
                "negative_mission": truth["negative_mission"],
                "automation_modality": AUTOMATION,
            })

    # Report authoring is a product-owned lifecycle seam, not an accidental side effect of rendering.
    if not any(row["library_id"] == "library.consumption.report_definition" for row in source["libraries"]):
        source["libraries"].append({
            "library_id": "library.consumption.report_definition",
            "class": "semantic_pure",
            "owner_ref": "semantic.report_lifecycle",
            "provides": ["capability.author_report"],
            "types": ["ReportId", "ReportDefinitionEdition", "ReportSection", "SemanticBinding", "ParameterDefinition", "PublicationReadiness"],
            "operations": ["open_report_draft", "author_report", "bind_semantics", "validate_publication_readiness"],
            "decisions": ["section_structure_policy", "parameter_policy", "semantic_binding_policy", "publication_readiness_policy"],
            "invariants": ["report_structure_cannot_redefine_metric_meaning", "draft_approval_and_publication_are_distinct"],
            "refusals": ["semantic_binding_missing", "parameter_invalid", "publication_evidence_incomplete"],
            "dependencies": ["library.consumption.presentation_ir"],
            "effect_boundary": "pure_no_io",
            "evidence_refs": ["evidence.vega.spec", "evidence.w3c.wcag22"],
            "product_refs": ["product.bi_reporting"],
        })
        source["binding_maps"].append({
            "binding_map_id": "binding.consumption.report_definition",
            "abstract_library_ref": "library.consumption.report_definition",
            "concrete_library_refs": ["library.cbv.presentation_ir", "library.cbv.semantic_query_types"],
            "compiler_disposition": "structurally_projected_unqualified",
            "gap_ref": None,
            "portable_offer": False,
            "product_refs": ["product.bi_reporting"],
        })

    source["ddd_dossiers"] = [row for row in source.get("ddd_dossiers", []) if row.get("product_ref") not in truth_by_product]
    source["ddd_dossiers"].extend([notebook, embedded])
    source["non_collapse_laws"].extend([
        "notebook document != cell graph != execution manifest != kernel session != attempt != output != reproduction result",
        "host authentication != tenant scope != embed grant != embedded session != analytical authorization",
        "typed host interaction != host action authority or completed host effect",
    ])
    source["negative_tests"].extend([
        {"test_id": "negative.notebook.rerun_reproduction", "prohibited_claim": "A notebook rerun proves reproduction without frozen environment data cut parameters and oracle.", "expected_result": "require closed manifest and scoped comparison"},
        {"test_id": "negative.notebook.generated_truth", "prohibited_claim": "Generated notebook code or narrative defines analytical truth.", "expected_result": "typecheck bind validate review and retain proposal provenance"},
        {"test_id": "negative.embedded.host_tenant", "prohibited_claim": "A host-supplied tenant identifier establishes tenant scope.", "expected_result": "verify tenant principal purpose and audience at authority gate"},
        {"test_id": "negative.embedded.action_effect", "prohibited_claim": "An embedded interaction event authorizes a host business effect.", "expected_result": "emit a typed intent for independent host authorization"},
    ])
    return source

