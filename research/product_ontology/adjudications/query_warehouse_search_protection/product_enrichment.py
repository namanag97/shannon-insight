#!/usr/bin/env python3
"""Add product-specific DDD and exact library ownership to the query/protection slice."""

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


SPECS: dict[str, dict[str, Any]] = {
    "product.query_execution_service": {
        "slug": "query_execution", "classification": "core_horizontal_analytical_query_execution_product",
        "vision": "Own typed analytical query occurrences from immutable intent through bounded execution and result receipts, including federation and cache semantics, without owning sources or downstream effects.",
        "question": "For an authorized editioned analytical query, exact source cuts and finite execution profile, what bound plan, execution occurrence, result cut and completion evidence can be produced?",
        "users": ["analyst", "application_developer", "query_engineer", "data_scientist", "service_operator", "source_owner", "cost_owner", "auditor"],
        "harmed": ["data_subject", "source_owner", "query_consumer", "concurrent_tenant", "cost_owner", "operator"],
        "jobs": ["parse and bind query intent", "typecheck functions and relations", "prove scoped rewrites", "plan local and federated work", "bind exact source cuts", "execute within finite budgets", "stream partial or complete results", "cancel and reconcile attempts", "reuse cache only under equivalent cuts", "publish result and execution receipts"],
        "outcomes": ["typed_bound_query", "evidence_scoped_logical_and_physical_plan", "explicit_pushdown_and_residual", "finite_cancellable_execution", "cut_bound_result", "typed_partiality_and_completion", "cache_freshness_evidence", "replayable_query_receipt"],
        "negative": "Does not own source facts, catalog identity, semantic metrics, warehouse experience, virtual relation lifecycle, runtime resources, downstream decisions or effects; federation, caching and workload profile do not create new products.",
        "states": ["draft", "parsed", "bound", "typed", "logical_planned", "physical_planned", "provider_unbound", "admitted", "queued", "running", "streaming", "partially_complete", "succeeded", "cancel_requested", "cancelled", "completion_unknown", "failed", "expired", "superseded"],
        "commands": ["open_query_occurrence", "parse_query", "bind_names_and_editions", "typecheck_query", "lower_logical_plan", "apply_proved_rewrites", "negotiate_source_capabilities", "plan_pushdown_and_residual", "bind_source_cuts", "bind_execution_budget", "bind_runtime", "admit_query", "start_query_attempt", "stream_result_partition", "cancel_query", "reconcile_completion", "seal_result_cut", "publish_query_receipt"],
        "events": ["query_occurrence_opened", "query_parsed", "names_and_editions_bound", "query_typechecked", "logical_plan_lowered", "proved_rewrites_applied", "source_capabilities_negotiated", "pushdown_and_residual_planned", "source_cuts_bound", "execution_budget_bound", "runtime_bound", "query_admitted", "query_attempt_started", "result_partition_streamed", "query_cancellation_requested", "query_completion_reconciled", "result_cut_sealed", "query_receipt_published"],
        "invariants": ["query text bound query logical plan physical plan execution attempt result cut and receipt are distinct", "every name function type and source binds an exact edition", "rewrite requires scoped null bag order time overflow and error equivalence evidence", "estimate is not observation", "planned or attempted pushdown is not performed pushdown", "federated queries declare each source cut and consistency posture", "partial result completion freshness and authorization are separate", "timeout cancellation and provider completion remain distinct", "cache identity includes semantic policy source-cut and freshness obligations", "query success never authorizes downstream effects"],
        "refusals": ["syntax_invalid", "name_ambiguous", "edition_unbound", "type_mismatch", "function_unsupported", "rewrite_equivalence_unproved", "source_capability_unknown", "translation_loss_unaccepted", "source_cut_unavailable", "cross_source_consistency_undeclared", "budget_unbounded", "runtime_unqualified", "resource_admission_denied", "result_schema_mismatch", "partiality_unaccepted", "completion_unknown", "cache_equivalence_unproved", "disclosure_denied"],
        "inside": ["query syntax binding types functions and relational semantics", "logical plans rewrites statistics costing and physical plans", "federated source capability type/function translation pushdown residuals and per-source cuts", "execution attempts budgets cancellation result streams and receipts", "cache identity freshness invalidation eviction stampede and evidence contracts"],
        "outside": ["source-domain facts and catalog authority", "semantic metric definition", "virtual relation identity and lifecycle", "warehouse environment experience", "runtime allocation", "search ranking", "business decision and effects", "provider qualification"],
        "terms": ["QueryText", "BoundQuery", "LogicalPlan", "RewriteProof", "PhysicalPlan", "SourceCapability", "PushdownPlan", "ResidualPlan", "SourceCut", "ExecutionProfile", "QueryAttempt", "ResultPartition", "ResultCut", "CompletionDisposition", "CacheEntry", "QueryReceipt"],
        "values": ["QueryId", "QueryEdition", "LanguageEdition", "FunctionEdition", "SchemaCutRef", "PlanDigest", "SourceOccurrenceRef", "SourceCutRef", "Budget", "Deadline", "AttemptId", "PartitionId", "ResultDigest", "CacheKey", "FreshnessBound"],
        "entities": ["QueryOccurrence", "BoundQuery", "LogicalPlanEdition", "PhysicalPlanEdition", "QueryAttempt", "ResultCut", "CacheEntry", "QueryReceipt"],
        "roots": ["QueryOccurrence", "LogicalPlanEdition", "PhysicalPlanEdition", "QueryAttempt", "ResultCut", "CacheEntry"],
        "services": ["QueryBindingService", "QueryTypeService", "RewriteProofService", "FederationPlanningService", "SourceCutService", "ExecutionAdmissionService", "ResultValidationService", "CacheEligibilityService", "CompletionReconciliationService"],
        "neighbors": [("context.catalog_schema", "customer_supplier"), ("context.semantic_metrics", "anti_corruption_layer"), ("product.virtual_data_access", "open_host_service"), ("product.managed_warehouse_experience", "customer_supplier"), ("product.runtime_resource_control", "customer_supplier"), ("context.identity_policy", "customer_supplier"), ("product.lineage_provenance", "published_language")],
        "time": "Separate query declaration, schema validity, source event/commit/visibility cuts, planning, admission, attempt, provider completion, result publication, consumption, cache freshness and expiry times; preserve per-source cuts rather than inventing atomicity.",
    },
    "product.managed_warehouse_experience": {
        "slug": "warehouse_experience", "classification": "core_operated_analytical_warehouse_experience_product",
        "vision": "Own the governed tenant and workload experience for analytical compute environments without collapsing query, catalog, storage or business semantics into the warehouse boundary.",
        "question": "For a tenant, workload class, capacity policy, service objective and budget, what managed analytical environment is available, admitted, scaled, charged, supported and exportable?",
        "users": ["warehouse_administrator", "analyst", "data_engineer", "application_owner", "capacity_planner", "finops_owner", "security_owner", "support_operator"],
        "harmed": ["concurrent_tenant", "budget_owner", "data_owner", "operator", "downstream_consumer"],
        "jobs": ["create isolated analytical environments", "bind workload and resource classes", "assign capacity and priorities", "suspend resume scale and drain", "observe service and cost objectives", "manage tenant support", "export data and control metadata", "decommission without orphaning dependencies"],
        "outcomes": ["editioned_environment", "tenant_and_workload_isolation", "capacity_assignment_receipt", "admission_and_queue_evidence", "scoped_service_and_cost_report", "portable_exit_manifest", "verified_decommission"],
        "negative": "Does not own query semantics, source/catalog truth, lakehouse table lifecycle, storage durability, semantic metrics, application decisions or provider portability; a branded warehouse is an experience over imported capabilities.",
        "states": ["requested", "provisioning", "ready", "active", "scaling", "suspended", "resuming", "degraded", "draining", "exit_pending", "exporting", "decommission_pending", "decommissioned", "failed"],
        "commands": ["request_warehouse_environment", "bind_tenant_and_security", "bind_workload_classes", "bind_capacity_policy", "provision_environment", "assign_capacity", "admit_workload", "scale_environment", "suspend_environment", "resume_environment", "record_service_and_cost_receipt", "request_exit", "export_environment_assets", "verify_exit_manifest", "decommission_environment"],
        "events": ["warehouse_environment_requested", "tenant_and_security_bound", "workload_classes_bound", "capacity_policy_bound", "environment_provisioned", "capacity_assigned", "workload_admitted", "environment_scaled", "environment_suspended", "environment_resumed", "service_and_cost_receipt_recorded", "warehouse_exit_requested", "environment_assets_exported", "exit_manifest_verified", "environment_decommissioned"],
        "invariants": ["warehouse experience query engine catalog storage and semantic layer are distinct", "tenant identity and policy are imported and edition-bound", "workload class is not product identity", "configured capacity is not delivered capacity", "admission queue execution and completion are distinct", "autoscaling action is not service-objective attainment", "cost estimate allocation charge and invoice remain distinct", "row export alone is not complete service exit", "decommission waits for dependency and in-flight-work disposition", "provider brand never owns canonical warehouse semantics"],
        "refusals": ["tenant_unbound", "security_policy_missing", "workload_class_ambiguous", "capacity_policy_invalid", "budget_exceeded", "resource_offer_unqualified", "admission_denied", "isolation_unproved", "service_objective_unmeasured", "cost_allocation_unknown", "export_incomplete", "control_metadata_missing", "dependency_still_live", "in_flight_work_unresolved"],
        "inside": ["warehouse environment identity edition and tenant binding", "workload classes priorities queues and admission", "capacity reservations assignments autoscaling suspension and resume", "service objectives support and operational evidence", "cost attribution inputs and scoped reports", "exit export manifest drain and decommission lifecycle"],
        "outside": ["query-language and engine semantics", "catalog schema and source truth", "storage and table-format ownership", "semantic metric definitions", "generic runtime resource allocation", "billing authority", "business decisions", "provider qualification"],
        "terms": ["WarehouseEnvironment", "TenantBinding", "WorkloadClass", "CapacityPolicy", "CapacityAssignment", "AdmissionDecision", "QueueReceipt", "ServiceObjective", "CostObservation", "ExitManifest", "DecommissionReceipt"],
        "values": ["EnvironmentId", "EnvironmentEdition", "TenantRef", "WorkloadClassId", "CapacityUnit", "Priority", "QueueLimit", "ScalingPolicyEdition", "BudgetRef", "ServiceWindow", "ExportDigest"],
        "entities": ["WarehouseEnvironment", "TenantBinding", "WorkloadClass", "CapacityAssignment", "ServiceWindow", "ExitProcess"],
        "roots": ["WarehouseEnvironment", "WorkloadClass", "CapacityAssignment", "ServiceWindow", "ExitProcess"],
        "services": ["EnvironmentProvisioningService", "WorkloadAdmissionService", "CapacityPolicyService", "IsolationAssuranceService", "ServiceObjectiveService", "CostObservationService", "WarehouseExitService"],
        "neighbors": [("product.query_execution_service", "customer_supplier"), ("context.catalog_schema", "customer_supplier"), ("product.persistence_lakehouse", "customer_supplier"), ("product.runtime_resource_control", "customer_supplier"), ("context.identity_policy", "anti_corruption_layer"), ("context.finops_billing", "published_language")],
        "time": "Separate requested, desired, provisioned, ready, admitted, queued, executing, metered, billed, exit-cut and decommission times; retain capacity and policy validity intervals and observed service windows.",
    },
    "product.virtual_data_access": {
        "slug": "virtual_data_access", "classification": "core_horizontal_virtual_relation_lifecycle_product",
        "vision": "Own governed virtual-relation identity and lifecycle across source bindings while importing query execution and preserving source authority.",
        "question": "For an editioned virtual relation, source bindings, policy, materialization posture and requested cut, what virtual result and provenance may be exposed?",
        "users": ["data_product_author", "data_virtualization_engineer", "analyst", "application_developer", "source_owner", "policy_owner", "service_operator"],
        "harmed": ["data_subject", "source_owner", "virtual_relation_consumer", "policy_rights_holder", "operator"],
        "jobs": ["define stable virtual relations", "bind and translate sources", "version lifecycle and compatibility", "choose live cache or materialized posture", "serve authorized cuts", "trace residual and provenance", "invalidate dependent editions", "export and retire relations"],
        "outcomes": ["immutable_virtual_relation_edition", "explicit_source_binding_graph", "typed_translation_residuals", "declared_live_or_materialized_posture", "cut_bound_access_receipt", "dependency_impact_evidence", "portable_relation_export"],
        "negative": "Does not own source facts, federation engine execution, source identity policy, materialized source truth, semantic metric meaning or application effects; a saved query alone is not a governed virtual relation.",
        "states": ["draft", "sources_bound", "validated", "published", "active", "materializing", "degraded", "invalidation_pending", "deprecated", "revoked", "retired", "superseded"],
        "commands": ["open_virtual_relation", "bind_source_relations", "declare_translation_and_residuals", "validate_virtual_definition", "publish_virtual_edition", "bind_materialization_policy", "request_virtual_cut", "record_access_receipt", "invalidate_dependents", "deprecate_virtual_edition", "export_virtual_contract", "revoke_virtual_edition", "retire_virtual_relation"],
        "events": ["virtual_relation_opened", "source_relations_bound", "translation_and_residuals_declared", "virtual_definition_validated", "virtual_edition_published", "materialization_policy_bound", "virtual_cut_requested", "access_receipt_recorded", "dependent_editions_invalidated", "virtual_edition_deprecated", "virtual_contract_exported", "virtual_edition_revoked", "virtual_relation_retired"],
        "invariants": ["saved query virtual relation edition execution and result are distinct", "virtual relation never becomes source truth", "every source binding and translation loss is explicit", "live cached and materialized modes preserve the same relation identity but different freshness evidence", "cross-source cuts never imply atomicity without proof", "policy and purpose are evaluated at access time", "edition compatibility is explicit", "dependency invalidation propagates without deleting history", "export includes definition bindings policy residual and lineage contracts", "virtual access never authorizes downstream effects"],
        "refusals": ["relation_identity_missing", "source_binding_unresolved", "translation_loss_unaccepted", "definition_invalid", "policy_unbound", "source_cut_unavailable", "consistency_posture_missing", "materialization_state_unknown", "freshness_unsatisfied", "purpose_denied", "dependency_cycle", "compatibility_unproved", "export_incomplete", "edition_revoked"],
        "inside": ["virtual relation identity and immutable editions", "source relation bindings and translation residuals", "lifecycle publication compatibility deprecation revocation and retirement", "live cached and materialized access posture", "requested cuts freshness policy and access receipts", "dependency graph impact and portable exit"],
        "outside": ["source business truth", "query planning and federation runtime", "generic cache implementation", "source authorization policy ownership", "semantic metrics", "warehouse environment", "effects and outcomes", "provider qualification"],
        "terms": ["VirtualRelation", "VirtualRelationEdition", "SourceBinding", "TranslationResidual", "DependencyGraph", "MaterializationPolicy", "VirtualCut", "FreshnessEvidence", "AccessReceipt", "CompatibilityRelation"],
        "values": ["VirtualRelationId", "EditionId", "SourceRelationRef", "SchemaCutRef", "DefinitionDigest", "PolicyEditionRef", "MaterializationMode", "FreshnessBound", "PurposeRef", "ExportDigest"],
        "entities": ["VirtualRelation", "VirtualRelationEdition", "SourceBindingGraph", "MaterializationBinding", "VirtualAccessOccurrence", "ExitPackage"],
        "roots": ["VirtualRelation", "VirtualRelationEdition", "SourceBindingGraph", "VirtualAccessOccurrence", "ExitPackage"],
        "services": ["VirtualDefinitionService", "SourceBindingService", "TranslationResidualService", "VirtualLifecycleService", "MaterializationPolicyService", "VirtualAccessService", "DependencyImpactService", "VirtualExitService"],
        "neighbors": [("product.query_execution_service", "customer_supplier"), ("context.source_truth", "anti_corruption_layer"), ("context.catalog_schema", "customer_supplier"), ("context.identity_policy", "customer_supplier"), ("product.lineage_provenance", "published_language"), ("product.data_product_publication", "open_host_service")],
        "time": "Separate relation-definition validity, source-schema validity, source event/commit/visibility cuts, materialization, access, freshness evaluation, policy validity and retirement times; preserve bitemporal edition and binding history.",
    },
    "product.search_index_service": {
        "slug": "search_index", "classification": "core_horizontal_search_and_index_serving_product",
        "vision": "Own index editions, mutation and visibility cuts, retrieval and ranking evidence across lexical, structured, geospatial and vector mechanisms without acquiring content or decision truth.",
        "question": "For an index edition, content mutation cut, query and ranking profile, what candidates and ordered results are visible, with approximation, score and evidence semantics explicit?",
        "users": ["search_engineer", "application_developer", "content_owner", "relevance_analyst", "service_operator", "policy_owner", "auditor"],
        "harmed": ["content_subject", "content_owner", "search_consumer", "excluded_or_misranked_party", "operator", "policy_rights_holder"],
        "jobs": ["define index and analyzer editions", "ingest versioned mutations", "establish searchable visibility cuts", "execute lexical structured vector or hybrid retrieval", "apply editioned ranking profiles", "report approximation and score semantics", "evaluate relevance", "delete and rebuild safely"],
        "outcomes": ["editioned_index_schema", "mutation_generation_receipt", "explicit_search_visibility_cut", "typed_retrieval_plan", "ranked_result_with_profile", "approximation_and_relevance_evidence", "verified_delete_or_rebuild"],
        "negative": "Does not own source content, catalog truth, feature semantics, embedding-model lifecycle, calibrated probability, business relevance authority, recommendation policy, decision or effects; vector retrieval is one mechanism, not an AI product.",
        "states": ["draft", "schema_bound", "building", "warming", "active", "mutation_pending", "refreshing", "visible", "degraded", "rebuilding", "delete_pending", "deleted", "retired", "failed"],
        "commands": ["open_index", "bind_index_schema", "bind_analysis_chain", "bind_retrieval_and_ranking_profile", "start_index_build", "submit_index_mutation", "record_mutation_acknowledgement", "publish_visibility_cut", "execute_search", "record_search_result", "evaluate_relevance", "delete_content", "rebuild_index", "retire_index"],
        "events": ["index_opened", "index_schema_bound", "analysis_chain_bound", "retrieval_and_ranking_profile_bound", "index_build_started", "index_mutation_submitted", "mutation_acknowledgement_recorded", "visibility_cut_published", "search_executed", "search_result_recorded", "relevance_evaluated", "content_deleted", "index_rebuilt", "index_retired"],
        "invariants": ["source content index document mutation acknowledgement visibility cut query candidate score ranking and decision are distinct", "index schema references but never owns content meaning", "analysis-chain edition participates in index and query identity", "mutation acknowledgement does not imply search visibility", "lexical vector and hybrid scores are profile-scoped and non-interchangeable", "retrieval score is not calibrated probability or business relevance", "approximate nearest-neighbor recall is evidence-scoped", "embedding edition is externally governed", "delete acceptance is not verified disappearance until all visibility cuts close", "ranked result never authorizes action"],
        "refusals": ["content_contract_missing", "index_schema_invalid", "analysis_chain_unbound", "mutation_generation_conflict", "visibility_cut_unknown", "query_type_unsupported", "ranking_profile_missing", "embedding_edition_unbound", "distance_semantics_ambiguous", "approximation_budget_missing", "filter_pushdown_unproved", "relevance_evidence_insufficient", "delete_completion_unknown", "purpose_denied", "decision_authority_requested"],
        "inside": ["index schema and analysis-chain editions", "document and field projection contracts", "mutation generations acknowledgement refresh and visibility", "lexical structured geospatial vector and hybrid retrieval IR", "ranking profiles score semantics approximation and result evidence", "relevance evaluation deletion rebuild and retirement lifecycle"],
        "outside": ["source-content and catalog truth", "feature definitions", "embedding-model training and lifecycle", "semantic metric ownership", "recommendation/business relevance policy", "decision and effects", "provider qualification"],
        "terms": ["Index", "IndexEdition", "IndexSchema", "AnalysisChain", "MutationGeneration", "MutationReceipt", "VisibilityCut", "SearchQuery", "RetrievalPlan", "RankingProfile", "Candidate", "SearchScore", "RankedResult", "RelevanceEvidence"],
        "values": ["IndexId", "IndexEditionId", "SchemaDigest", "AnalyzerEdition", "DocumentId", "MutationId", "Generation", "VisibilityToken", "QueryId", "RankingProfileEdition", "EmbeddingEditionRef", "DistanceMetric", "ApproximationBudget"],
        "entities": ["SearchIndex", "IndexEdition", "MutationBatch", "VisibilityCut", "SearchOccurrence", "RankedResult", "RelevanceEvaluation"],
        "roots": ["SearchIndex", "IndexEdition", "MutationBatch", "VisibilityCut", "SearchOccurrence"],
        "services": ["IndexSchemaService", "AnalysisChainService", "MutationGenerationService", "VisibilityService", "RetrievalPlanningService", "RankingService", "ApproximationEvidenceService", "RelevanceEvaluationService", "DeletionVerificationService"],
        "neighbors": [("context.source_content", "anti_corruption_layer"), ("context.catalog_schema", "customer_supplier"), ("product.model_lifecycle", "customer_supplier"), ("context.identity_policy", "customer_supplier"), ("product.runtime_resource_control", "customer_supplier"), ("product.lineage_provenance", "published_language")],
        "time": "Separate source-content event, index mutation, acknowledgement, refresh, searchable visibility, query, result, relevance judgment, deletion request and verified disappearance times; preserve index and ranking-profile validity intervals.",
    },
    "product.data_protection_recovery": {
        "slug": "data_protection_recovery", "classification": "core_horizontal_data_protection_and_recovery_product",
        "vision": "Own scoped, retained and tested recovery points and service restoration evidence without confusing snapshots, replication or successful copy with recoverability.",
        "question": "For an authority-bound protection scope and consistency objective, which recovery points exist, remain usable, and have demonstrated restoration and service acceptance within measured objectives?",
        "users": ["service_owner", "backup_operator", "database_administrator", "recovery_coordinator", "security_owner", "records_owner", "risk_auditor"],
        "harmed": ["service_user", "data_owner", "data_subject", "dependent_service", "operator", "records_authority"],
        "jobs": ["declare protection scope and dependencies", "establish application-consistent cuts", "produce and retain backup chains", "verify manifests and media", "plan and execute restore", "reconcile dependencies", "accept recovered service", "measure achieved RPO and RTO", "expire recovery points under authority"],
        "outcomes": ["authority_bound_protection_scope", "consistent_recovery_cut", "complete_backup_chain", "verified_recovery_point", "tested_restore_receipt", "service_recovery_acceptance", "measured_rpo_rto_evidence", "authorized_retention_disposition"],
        "negative": "Does not own primary data truth, availability replication, storage snapshots, records retention authority, digital preservation, incident command or application business acceptance; mechanisms are imported and insufficient alone.",
        "states": ["draft", "scope_bound", "scheduled", "capture_running", "captured", "verification_pending", "verified", "unusable", "restore_planned", "restoring", "restored", "service_validation_pending", "accepted", "rejected", "expired", "held", "disposed"],
        "commands": ["open_protection_plan", "bind_scope_dependencies_and_authority", "declare_consistency_and_recovery_objectives", "capture_recovery_cut", "produce_backup_manifest", "close_backup_chain", "verify_recovery_point", "plan_restore", "execute_restore", "reconcile_dependencies", "validate_restored_service", "accept_or_reject_recovery", "measure_achieved_rpo_rto", "place_hold", "expire_or_dispose_recovery_point"],
        "events": ["protection_plan_opened", "scope_dependencies_and_authority_bound", "consistency_and_recovery_objectives_declared", "recovery_cut_captured", "backup_manifest_produced", "backup_chain_closed", "recovery_point_verified", "restore_planned", "restore_executed", "dependencies_reconciled", "restored_service_validated", "recovery_accepted_or_rejected", "achieved_rpo_rto_measured", "recovery_hold_placed", "recovery_point_expired_or_disposed"],
        "invariants": ["snapshot replica backup artifact backup chain recovery point restore and recovered service are distinct", "protection scope includes applications data configuration keys dependencies and exclusions", "consistency cut and crash/application consistency are explicit", "backup success does not imply integrity or restorability", "restore completion does not imply service recovery", "declared RPO/RTO are objectives and measured exercise values are evidence", "replication can propagate corruption and deletion", "retention disposition requires external records and legal authority", "holds override ordinary expiry without erasing schedules", "every recovery claim binds an exact exercised scope environment and time"],
        "refusals": ["protection_scope_incomplete", "dependency_unknown", "consistency_posture_missing", "encryption_key_unavailable", "backup_chain_broken", "manifest_mismatch", "recovery_point_unverified", "restore_target_incompatible", "restore_partial", "dependency_reconciliation_failed", "service_acceptance_missing", "rpo_rto_unmeasured", "retention_authority_missing", "hold_conflict", "provider_completion_unknown"],
        "inside": ["protection plan scope dependency and exclusion identity", "consistency cuts manifests backup chains and recovery points", "integrity media and key verification", "restore plans attempts partiality and receipts", "dependency reconciliation and service-level acceptance", "declared versus measured RPO/RTO", "retention hold expiry and disposition handoff"],
        "outside": ["primary source truth", "high-availability replication ownership", "snapshot and storage providers", "records/legal retention authority", "digital preservation lifecycle", "incident command", "application-domain recovery acceptance criteria", "provider qualification"],
        "terms": ["ProtectionPlan", "ProtectionScope", "ConsistencyCut", "BackupArtifact", "BackupManifest", "BackupChain", "RecoveryPoint", "RestorePlan", "RestoreAttempt", "RestoreReceipt", "ServiceRecoveryAcceptance", "RPO", "RTO", "RetentionDisposition"],
        "values": ["ProtectionPlanId", "ScopeEdition", "DependencyGraphRef", "ConsistencyProfile", "RecoveryPointId", "ManifestDigest", "EncryptionKeyRef", "RestoreAttemptId", "RPOObjective", "RTOObjective", "MeasuredDuration", "HoldRef"],
        "entities": ["ProtectionPlan", "BackupOccurrence", "BackupChain", "RecoveryPoint", "RestoreAttempt", "RecoveryExercise", "RetentionDisposition"],
        "roots": ["ProtectionPlan", "BackupChain", "RecoveryPoint", "RestoreAttempt", "RecoveryExercise", "RetentionDisposition"],
        "services": ["ProtectionScopeService", "ConsistencyCutService", "BackupChainService", "RecoveryPointVerificationService", "RestorePlanningService", "DependencyReconciliationService", "ServiceAcceptanceService", "RecoveryObjectiveMeasurementService", "RetentionBridgeService"],
        "neighbors": [("context.source_system", "customer_supplier"), ("product.runtime_resource_control", "customer_supplier"), ("context.key_management", "customer_supplier"), ("context.records_authority", "anti_corruption_layer"), ("product.digital_preservation_archive", "separate_ways"), ("context.incident_management", "published_language"), ("product.lineage_provenance", "published_language")],
        "time": "Separate source commit, consistency cut, capture, verification, retention validity, incident, restore start/end, dependency readiness, service acceptance and exercise times; measured RPO/RTO never overwrite declared objectives.",
    },
    "product.digital_preservation_archive": {
        "slug": "digital_preservation_archive", "classification": "core_horizontal_digital_preservation_archive_product",
        "vision": "Own long-lived information packages, preservation evidence and designated-community access without confusing immutable storage or fixity with authenticity and future usability.",
        "question": "For a designated community, records authority and preservation horizon, what information package remains authentic, understandable, renderable, accessible and disposition-governed over change?",
        "users": ["archivist", "records_manager", "preservation_specialist", "content_owner", "designated_community_member", "custodian", "rights_reviewer", "auditor"],
        "harmed": ["record_subject", "rights_holder", "content_owner", "designated_community", "future_consumer", "custodian"],
        "jobs": ["negotiate submission packages", "validate representation information", "record provenance custody rights and fixity", "produce archival packages", "monitor format and dependency risk", "execute preservation actions", "serve access packages", "apply holds appraisal and disposition authority", "transfer custody and prove exit"],
        "outcomes": ["accepted_submission_package", "complete_archival_information_package", "fixity_and_provenance_evidence", "representation_dependency_closure", "preservation_action_receipt", "community_usable_access_package", "authority_bound_disposition", "custody_transfer_evidence"],
        "negative": "Does not own business source truth, operational backup/recovery, generic object storage, records appraisal authority, copyright/privacy policy or future authenticity by digest alone; WORM is a mechanism, not the archive.",
        "states": ["offered", "appraisal_pending", "accepted", "rejected", "ingesting", "archival_package_formed", "preserved", "risk_detected", "action_pending", "actioned", "access_restricted", "accessible", "hold", "transfer_pending", "transferred", "disposition_pending", "disposed"],
        "commands": ["offer_submission_package", "appraise_submission", "accept_or_reject_submission", "validate_package_and_metadata", "form_archival_information_package", "record_fixity_provenance_rights_and_custody", "assess_format_and_dependency_risk", "plan_preservation_action", "execute_preservation_action", "produce_access_package", "authorize_access", "place_or_release_hold", "transfer_custody", "authorize_disposition", "dispose_package"],
        "events": ["submission_package_offered", "submission_appraised", "submission_accepted_or_rejected", "package_and_metadata_validated", "archival_information_package_formed", "fixity_provenance_rights_and_custody_recorded", "format_and_dependency_risk_assessed", "preservation_action_planned", "preservation_action_executed", "access_package_produced", "archive_access_authorized", "archive_hold_placed_or_released", "custody_transferred", "archive_disposition_authorized", "archival_package_disposed"],
        "invariants": ["submission archival dissemination and access packages are distinct", "bitstream object representation information metadata and record identity are distinct", "fixity is not authenticity", "format validity is not renderability or designated-community understandability", "preservation action creates a new related representation and never rewrites history", "access copy is not preservation master", "custody is not ownership", "WORM or object lock is not preservation lifecycle", "archive imports appraisal retention privacy and rights authority", "disposition requires authority holds checks and evidence"],
        "refusals": ["designated_community_undefined", "records_authority_missing", "submission_incomplete", "representation_information_missing", "fixity_mismatch", "provenance_gap", "rights_unknown", "format_risk_unassessed", "dependency_unavailable", "preservation_action_unvalidated", "authenticity_argument_insufficient", "access_purpose_denied", "hold_active", "custody_transfer_incomplete", "disposition_authority_missing"],
        "inside": ["submission archival dissemination and access information packages", "descriptive preservation structural technical rights and provenance metadata", "fixity checks and authenticity argument evidence", "representation information format sustainability and dependency closure", "preservation planning actions validation and lineage", "designated-community access copies and disclosure receipts", "custody transfer holds and disposition handoff"],
        "outside": ["operational source truth", "backup restore and service recovery", "generic immutable/object storage", "records appraisal and retention authority", "copyright privacy and access-policy ownership", "emulation/rendering provider qualification", "business outcomes"],
        "terms": ["DesignatedCommunity", "SubmissionInformationPackage", "ArchivalInformationPackage", "DisseminationInformationPackage", "AccessCopy", "RepresentationInformation", "PreservationDescriptionInformation", "FixityCheck", "AuthenticityArgument", "PreservationAction", "Custody", "Hold", "DispositionAuthority"],
        "values": ["ArchivePackageId", "PackageEdition", "ContentDigest", "FixityAlgorithmEdition", "FormatIdentifier", "RepresentationDependencyRef", "RightsPolicyRef", "CustodyRef", "CommunityRef", "PreservationHorizon", "HoldRef"],
        "entities": ["SubmissionPackage", "ArchivalInformationPackage", "RepresentationNetwork", "PreservationAction", "AccessPackage", "CustodyTransfer", "DispositionCase"],
        "roots": ["SubmissionPackage", "ArchivalInformationPackage", "PreservationAction", "AccessPackage", "CustodyTransfer", "DispositionCase"],
        "services": ["SubmissionAppraisalBridge", "PackageValidationService", "FixityService", "AuthenticityEvidenceService", "FormatRiskService", "PreservationPlanningService", "AccessPackageService", "CustodyTransferService", "DispositionAuthorityBridge"],
        "neighbors": [("context.source_records", "customer_supplier"), ("context.records_authority", "anti_corruption_layer"), ("context.rights_privacy_policy", "anti_corruption_layer"), ("product.data_protection_recovery", "separate_ways"), ("context.storage_runtime", "customer_supplier"), ("product.lineage_provenance", "published_language")],
        "time": "Separate record validity, transfer, custody, ingest, archival edition, fixity observation, risk assessment, preservation action, access, hold, retention and disposition times; preserve provenance and bitemporal authority history across migrations.",
    },
}


def automation_law() -> dict[str, Any]:
    return {
        "default": "DETERMINISTIC_CORE_ONLY",
        "postures": ["PROHIBITED", "OPTIONAL", "REQUIRED_BY_INTENT", "UNDETERMINED"],
        "law": "Predictive models, generative models and agents may rank, propose, explain or assist only behind declared qualified contracts; their output owns no source, semantic, authority, completion or acceptance truth.",
        "removal_law": "Removing every optional model or agent preserves parsing, typing, binding, planning, execution, lifecycle, authorization, evidence, recovery and preservation behavior.",
        "hard_work_law": "Automation never replaces exact cuts, invariants, provider qualification, finite budgets, evidence, authority, reconciliation or acceptance.",
    }


def truth(spec: dict[str, Any]) -> dict[str, Any]:
    return {
        "sovereign_question": spec["question"], "users": spec["users"], "harmed_parties": spec["harmed"],
        "jobs": spec["jobs"], "outcomes": spec["outcomes"], "negative_mission": spec["negative"],
        "lifecycle_states": spec["states"], "commands": spec["commands"], "events": spec["events"],
        "invariants": spec["invariants"], "refusals": spec["refusals"], "automation_modality": automation_law(),
    }


def dossier(product: str, spec: dict[str, Any]) -> dict[str, Any]:
    t = truth(spec)
    roots = spec["roots"]
    ddd = {
        "domain_vision_statement": spec["vision"], "subdomain_classification": spec["classification"],
        "bounded_context_boundary": {"inside": spec["inside"], "outside": spec["outside"]},
        "ubiquitous_language_policy": {"canonical_terms": spec["terms"], "law": "One editioned meaning per term inside the boundary; homonyms are translated and non-collapse laws are executable."},
        "context_map": [{"neighbor_ref": ref, "relationship": relationship, "translation": "Import exact editioned identity, policy, evidence or effects without transferring semantic ownership."} for ref, relationship in spec["neighbors"]],
        "anti_corruption_layers": [f"acl.{spec['slug']}.{ref.split('.')[-1]}" for ref, _ in spec["neighbors"]],
        "published_language": spec["terms"] + ["TypedRefusal", "EvidenceRef", "EditionRef"],
        "value_objects": spec["values"], "entities": spec["entities"],
        "aggregates": [{"root": root, "consistency": f"{root} changes only through version-checked commands; identity, evidence, authority and refusal are explicit."} for root in roots],
        "aggregate_roots": roots, "aggregate_invariants": spec["invariants"],
        "commands": spec["commands"], "domain_events": spec["events"],
        "refusal_failure_catalog": spec["refusals"], "domain_services": spec["services"],
        "application_services": [f"{name.removesuffix('Service')}UseCase" for name in spec["services"]],
        "repositories": [f"{root}Repository" for root in roots],
        "factories": [f"{root}Factory" for root in roots],
        "specifications": [f"{name.removesuffix('Service')}Specification" for name in spec["services"]] + ["ProviderQualificationSpecification", "EvidenceValiditySpecification", "ExitCompletenessSpecification"],
        "state_machine": {"states": spec["states"], "transition_law": "A named command may emit its past-tense event only from a legal state with expected version, exact editions, satisfied invariants, valid evidence and external authority where required."},
        "policies_and_reactions": ["on evidence expiry refuse stronger claims", "on revocation invalidate dependent editions", "on uncertain completion reconcile before retry", "on optional assistance failure use deterministic fallback or refuse"],
        "sagas_and_process_managers": [f"{spec['slug'].title().replace('_', '')}LifecycleProcess", "ProviderQualificationProcess", "RevocationPropagationProcess", "ExitAndPortabilityProcess"],
        "read_models_and_projections": [f"{root}StatusProjection" for root in roots] + ["EvidenceAndAuthorityProjection", "OpenRefusalsProjection", "DependencyBlastRadiusProjection"],
        "integration_event_policy": "Only immutable, editioned published-language facts cross the boundary. Provider callbacks, tentative findings and proposals remain internal; source, authority, effect and outcome truth require owning-context receipts.",
        "concurrency_and_idempotency": "Use immutable occurrence and attempt IDs, aggregate versions and command idempotency keys. Retries create or reference explicit attempts, never overwrite evidence, and uncertain remote effects must reconcile before repetition.",
        "time_model": spec["time"],
        "event_storming_swimlanes": {"actors": spec["users"], "commands": spec["commands"], "events": spec["events"], "hotspots": ["identity versus alias", "desired versus observed state", "request versus completion", "evidence versus authority", "copy versus accepted outcome", "revocation propagation"]},
        "nonfunctional_laws": spec["invariants"] + ["finite budgets deadlines payloads retention and recovery objectives are explicit", "determinism or declared nondeterminism is observable", "one provider never proves portability", automation_law()["removal_law"]],
    }
    assert set(ddd) == DDD_FIELDS
    return {
        "dossier_id": f"ddd.query_protection.{spec['slug']}", "product_ref": product,
        "status": "candidate_not_ratified",
        "product_truth": {"sovereign_question": t["sovereign_question"], "users": t["users"], "harmed_parties": t["harmed_parties"], "jobs": t["jobs"], "measurable_outcomes": t["outcomes"], "negative_mission": t["negative_mission"]},
        "strategic_and_tactical_ddd": ddd,
    }


def enrich(source: dict[str, Any]) -> dict[str, Any]:
    capability_owner = {row["capability_ref"]: row["consumer_ref"] for row in source["requirements"]}
    library_owner = {row["library_id"]: capability_owner[row["provides"][0]] for row in source["libraries"]}
    source["ddd_dossiers"] = [row for row in source.get("ddd_dossiers", []) if row.get("product_ref") not in SPECS]
    for artifact in source["artifacts"]:
        if artifact["artifact_id"] in SPECS:
            artifact.update(truth(SPECS[artifact["artifact_id"]]))
    for library in source["libraries"]:
        library["product_refs"] = [library_owner[library["library_id"]]]
    for binding in source["binding_maps"]:
        binding["product_refs"] = [library_owner[binding["abstract_library_ref"]]]
    for gap in source["binding_gaps"]:
        gap["product_refs"] = [library_owner[gap["abstract_library_ref"]]]
        gap["abstract_library_refs"] = [gap["abstract_library_ref"]]
    source["ddd_dossiers"].extend(dossier(product, spec) for product, spec in SPECS.items())
    return source
