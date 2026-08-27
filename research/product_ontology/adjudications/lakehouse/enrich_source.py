#!/usr/bin/env python3
"""Deterministically enrich the lakehouse adjudication with product DDD and compiler maps.

The base lakehouse source owns evidence, boundary decisions and the shared table-state library
slice.  This file owns the exact retained-product fields, five product-owned library
attributions, product requirements, full DDD dossiers, and normalized compiler maps/gaps.
It deliberately does not turn query, ingestion, object storage, compute, governance or table
formats into meanings owned by the managed lakehouse experience.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "source.json"
REPO = HERE.parents[3]

PRODUCT_FIELDS = {
    "sovereign_question", "users", "harmed_parties", "jobs", "outcomes",
    "negative_mission", "lifecycle_states", "commands", "events", "invariants",
    "refusals", "automation_modality",
}

MANAGED_REQUIREMENT_IDS = {
    "requirement.experience.environment",
    "requirement.catalog.namespace_registry",
    "requirement.catalog.commit_coordination",
    "requirement.catalog.credential_vending",
    "requirement.maintenance.plan",
    "requirement.maintenance.compaction",
    "requirement.maintenance.clustering",
    "requirement.maintenance.snapshot_expiry",
    "requirement.sharing.publish_consume_revoke",
}

MANAGED_LIBRARY_IDS = {
    "library.lakehouse_environment_lifecycle",
    "library.data_sharing_contract",
}

AUTOMATION = {
    "default": "DETERMINISTIC_CORE_ONLY",
    "postures": ["PROHIBITED", "OPTIONAL", "REQUIRED_BY_INTENT", "UNDETERMINED"],
    "law": "Models and agents may propose typed configurations, plans, mappings or diagnoses but never own lakehouse semantics, authority, effects, receipts, qualification or acceptance.",
    "hard_work_law": "Automation never replaces vocabulary, boundary adjudication, invariants, lifecycle design, evidence, conformance, provider qualification or domain acceptance.",
}

DDD_IMPORT_SPECS = {
    "product.ingestion_delivery": {
        "bundle": "movement",
        "dossier_id": "ddd.movement.ingestion_delivery",
    },
    "product.query_execution_service": {
        "bundle": "query_warehouse_search_protection",
        "dossier_id": "ddd.query_protection.query_execution",
    },
}


def canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True)


def record_digest(value: Any) -> str:
    return "sha256:" + hashlib.sha256(canonical(value).encode()).hexdigest()


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def ddd_delegations() -> list[dict[str, Any]]:
    rows = []
    for product_ref, spec in sorted(DDD_IMPORT_SPECS.items()):
        bundle_dir = REPO / "research/product_ontology/adjudications" / spec["bundle"]
        dossier_path = bundle_dir / "product-ddd-dossiers.jsonl"
        maps_path = bundle_dir / "product-library-binding-maps.jsonl"
        dossier = next(row for row in load_jsonl(dossier_path) if row["dossier_id"] == spec["dossier_id"])
        maps = sorted(
            (row for row in load_jsonl(maps_path) if product_ref in row.get("product_refs", [])),
            key=lambda row: row["binding_map_id"],
        )
        if dossier["product_ref"] != product_ref or not maps:
            raise ValueError(f"invalid canonical DDD import for {product_ref}")
        rows.append({
            "delegation_id": f"delegation.lakehouse.{product_ref.removeprefix('product.')}",
            "suite_ref": "suite.lakehouse",
            "imported_product_ref": product_ref,
            "authoritative_bundle": spec["bundle"],
            "authoritative_dossier_ref": dossier["dossier_id"],
            "authoritative_dossier_digest": record_digest(dossier),
            "authoritative_dossier_file": str(dossier_path.relative_to(REPO)),
            "authoritative_dossier_file_sha256": "sha256:" + hashlib.sha256(dossier_path.read_bytes()).hexdigest(),
            "imported_binding_map_refs": [row["binding_map_id"] for row in maps],
            "imported_binding_map_digests": [record_digest(row) for row in maps],
            "imported_binding_map_set_digest": record_digest(maps),
            "authoritative_binding_map_file": str(maps_path.relative_to(REPO)),
            "authoritative_binding_map_file_sha256": "sha256:" + hashlib.sha256(maps_path.read_bytes()).hexdigest(),
            "relationship": "conformist_import_with_anti_corruption_boundary",
            "local_redefinition_forbidden": True,
            "status": "candidate_not_ratified",
            "completion_claim": False,
        })
    return rows


def product_spec(
    *, key: str, question: str, classification: str, users: list[str], harmed: list[str],
    job: str, outcomes: list[str], negative: str, inside: list[str], outside: list[str],
    values: list[str], entities: list[str], aggregates: list[dict[str, Any]],
    invariants: list[str], commands: list[str], events: list[str], states: list[str],
    refusals: list[str], services: list[str], specifications: list[str],
    policies: list[str], sagas: list[str], reads: list[str], time: list[str],
    neighbors: list[tuple[str, str, str]], nfr: list[str], language: str,
    integration: str,
) -> dict[str, Any]:
    return locals()


SPECS = {
    "product.managed_lakehouse_experience": product_spec(
        key="managed_lakehouse_experience",
        question="How can a platform owner declare, qualify, reconcile, operate, upgrade and exit a supported analytical environment assembled from replaceable table, catalog, query, ingestion, maintenance, governance and resource products?",
        classification="core_horizontal_platform_experience_product",
        users=["data_platform_owner", "environment_operator", "data_product_team", "security_reviewer", "finops_owner"],
        harmed=["data_subject", "data_consumer", "platform_tenant", "on_call_operator", "resource_owner"],
        job="Declare and operate a supported analytical environment while retaining exact component contracts, qualification evidence, costs, drift, rollback and exit.",
        outcomes=["typed_environment_declaration", "closed_qualified_component_plan", "readiness_and_drift_evidence", "bounded_rollout_and_rollback", "portable_exit_package"],
        negative="Does not own table-format semantics, catalog authority, query meaning, ingestion delivery, maintenance algorithms, data quality, lineage, policy, business semantics, identity, compute or storage resources.",
        inside=["environment declarations and editions", "supported component profiles", "capability requirements and compatibility constraints", "qualified component bindings", "desired and observed environment state", "readiness and drift classification", "rollout rollback suspension and exit orchestration", "environment evidence and cost envelope"],
        outside=["table snapshot and commit meaning", "catalog namespace and disclosure authority", "query and ingestion execution", "maintenance planning", "quality lineage policy and semantic-query meaning", "identity and secret custody", "compute scheduling and object persistence", "vertical business acceptance"],
        values=["EnvironmentId", "EnvironmentEdition", "SupportedProfileEdition", "CapabilityRequirement", "ComponentBindingRef", "DesiredEnvironmentState", "ObservedEnvironmentState", "DriftSet", "ReadinessVerdict", "RolloutPlan", "RollbackPlan", "ExitPlan", "EnvironmentEvidenceCut"],
        entities=["EnvironmentDeclaration", "SupportedComponentProfile", "ComponentBinding", "EnvironmentOccurrence", "ReconciliationOccurrence", "RolloutOccurrence", "ExitOccurrence"],
        aggregates=[
            {"root": "EnvironmentDeclaration", "members": ["profile", "requirements", "constraints", "budgets", "lifecycle"], "consistency": "one immutable edition fixes requested semantics and budgets"},
            {"root": "EnvironmentOccurrence", "members": ["declaration_ref", "bindings", "desired_state", "observed_state", "readiness", "drift", "fence"], "consistency": "one fenced occurrence owns reconciliation and rollout state"},
            {"root": "ExitOccurrence", "members": ["environment_ref", "export_cut", "active_work_disposition", "provider_release_receipts"], "consistency": "exit completion requires evidence for every bound component and resource"},
        ],
        invariants=["environment declaration and physical occurrence identities are distinct", "desired state is never inferred from observed provider state", "provider or suite name cannot select semantic contracts", "readiness requires every blocking capability and compatibility constraint to close", "component health is not environment readiness", "rollout requires a bounded rollback or explicit irreversible authority", "exit preserves declarations state evidence and active-work disposition", "generated proposals cannot qualify providers or authorize effects"],
        commands=["draft_environment", "select_supported_profile", "declare_capability_requirement", "resolve_component_plan", "bind_qualified_component", "approve_environment_plan", "request_environment_rollout", "record_component_observation", "reconcile_environment", "approve_repair_intent", "request_rollback", "suspend_environment", "plan_environment_exit", "complete_environment_exit", "retire_environment"],
        events=["environment_drafted", "supported_profile_selected", "capability_requirement_declared", "component_plan_resolved", "qualified_component_bound", "environment_plan_approved", "environment_rollout_requested", "component_observation_recorded", "environment_reconciled", "repair_intent_approved", "rollback_requested", "environment_suspended", "environment_exit_planned", "environment_exit_completed", "environment_retired"],
        states=["draft", "requirements_open", "binding", "plan_ready", "approval_pending", "rolling_out", "ready", "degraded", "drifted", "repair_pending", "rolling_back", "suspended", "exiting", "exited", "retired"],
        refusals=["profile_unresolved", "capability_gap", "semantic_edition_conflict", "component_offer_unqualified", "provider_constraint_hidden", "resource_budget_unclosed", "policy_or_authority_unresolved", "readiness_unproved", "drift_classification_unknown", "rollback_unavailable", "irreversible_change_unapproved", "exit_evidence_incomplete", "active_work_disposition_missing"],
        services=["EnvironmentTypingService", "ComponentCompatibilityService", "BindingClosureService", "ReadinessEvaluationService", "DriftClassificationService", "RolloutPlanningService", "ExitPlanningService"],
        specifications=["EnvironmentDeclarationCompletenessSpecification", "ComponentQualificationSpecification", "CompatibilityClosureSpecification", "ReadinessSpecification", "RolloutSafetySpecification", "RollbackFeasibilitySpecification", "ExitCompletenessSpecification"],
        policies=["when a required capability has no qualified offer refuse plan closure", "when observed state differs from desired state classify drift before proposing repair", "when a component edition changes re-evaluate compatibility and qualification", "when readiness evidence expires mark the occurrence unready", "when rollback is impossible require named irreversible-change authority", "when exit begins freeze incompatible new work and disposition every active occurrence"],
        sagas=["EnvironmentBindingProcess", "EnvironmentRolloutProcess", "EnvironmentRepairProcess", "EnvironmentRollbackProcess", "EnvironmentExitProcess"],
        reads=["EnvironmentCatalogView", "CapabilityClosureView", "ComponentBindingGraph", "ReadinessView", "DriftView", "RolloutEvidenceView", "CostEnvelopeView", "ExitProgressView"],
        time=["declaration validity and recording time are distinct", "desired and observed state have independent cuts", "qualification readiness and credential evidence expire explicitly", "rollout and rollback occurrences carry fenced sequence time", "exit cut and completion time are distinct"],
        neighbors=[("semantic.analytical_table_state", "customer_supplier_acl", "import exact table-state contracts without acquiring them"), ("product.catalog_service", "customer_supplier", "bind a qualified catalog product"), ("product.query_execution_service", "customer_supplier", "bind a qualified query product"), ("product.ingestion_delivery", "customer_supplier", "bind a qualified ingestion product"), ("product.managed_table_maintenance", "customer_supplier", "bind a qualified maintenance product"), ("neighbor.data_quality", "conformist_published_language", "consume quality contracts and evidence"), ("neighbor.lineage", "published_language", "exchange component and result lineage"), ("neighbor.data_use_policy", "anti_corruption_layer", "obtain policy decisions and obligations"), ("neighbor.semantic_query", "anti_corruption_layer", "bind business semantics without redefining them"), ("resource.object_storage", "customer_supplier", "bind capacity and occurrence receipts"), ("resource.compute", "customer_supplier", "bind capacity and occurrence receipts")],
        nfr=["deterministic plan resolution", "bounded reconciliation and rollout work", "cooperative cancellation", "fail-closed readiness and authority", "no hidden provider defaults", "complete observability and evidence by environment edition and occurrence"],
        language="Environment, profile, component, requirement, offer, binding, desired state, observed state, drift, readiness, rollout, rollback, repair, suspension, exit and receipt are non-interchangeable terms; product and provider homonyms cross named ACLs.",
        integration="Only minimized editioned environment, binding, readiness, drift, rollout, suspension and exit facts cross the boundary; component-internal state and foreign provider DTOs remain behind ACLs.",
    ),
    "product.catalog_service": product_spec(
        key="catalog_service",
        question="How can a catalog authority govern namespaces, table registrations, current metadata references, atomic commit coordination and scoped credential vending without owning table contents or business semantics?",
        classification="core_horizontal_catalog_authority_product",
        users=["catalog_administrator", "table_writer", "query_engine", "data_platform_operator", "security_reviewer"],
        harmed=["table_owner", "data_consumer", "data_subject", "concurrent_writer", "credential_owner"],
        job="Register and resolve analytical tables, adjudicate concurrent metadata commits, and vend least-privilege credentials under explicit authority and evidence.",
        outcomes=["stable_namespace_and_registration_identity", "atomic_current_reference_transition", "auditable_commit_refusal_or_receipt", "scoped_expiring_credentials", "portable_catalog_export"],
        negative="Does not define table-format state, write data files, execute queries, own source facts, decide business-use policy, custody long-lived secrets or perform maintenance rewrites.",
        inside=["catalog and namespace identity", "table registration lifecycle", "current metadata reference authority", "commit request adjudication and atomic publication", "catalog principals roles and operation grants", "scoped credential leases", "catalog export and migration evidence"],
        outside=["table snapshot interpretation", "data-file and metadata-file persistence", "query planning", "business glossary and ontology", "enterprise identity proofing", "business data-use policy", "maintenance plan execution"],
        values=["CatalogId", "NamespaceId", "TableRegistrationId", "TableIdentityRef", "MetadataReference", "BaseReference", "CommitToken", "CatalogPrincipalRef", "CatalogOperation", "CredentialScope", "CredentialExpiry", "CatalogEvidenceCut"],
        entities=["Catalog", "Namespace", "TableRegistration", "CommitRequest", "CatalogPrincipalBinding", "CredentialLease", "CatalogExport"],
        aggregates=[
            {"root": "NamespaceRegistry", "members": ["catalog_id", "namespaces", "registrations", "policies", "edition"], "consistency": "namespace and registration uniqueness is enforced atomically"},
            {"root": "TableRegistration", "members": ["table_identity", "current_reference", "commit_fence", "lifecycle"], "consistency": "one authorized compare-and-swap advances the current reference"},
            {"root": "CredentialLease", "members": ["principal_ref", "operation", "resource_scope", "expiry", "revocation"], "consistency": "issued scope cannot exceed the adjudicated catalog operation"},
        ],
        invariants=["namespace and registration identity are stable and unambiguous", "catalog current reference is not the table snapshot itself", "commit requires exact base reference and table-state preconditions", "concurrent commit resolution is atomic and evidence-bearing", "registration authority is distinct from data-use authority", "credential scope is least privilege and time bounded", "revocation prevents new use and propagates to outstanding leases", "provider identity cannot change catalog meaning"],
        commands=["create_namespace", "rename_namespace", "register_table", "resolve_table_registration", "submit_commit_request", "adjudicate_commit", "publish_current_reference", "bind_catalog_principal", "grant_catalog_operation", "vend_scoped_credential", "revoke_credential", "export_catalog", "drop_registration", "retire_catalog"],
        events=["namespace_created", "namespace_renamed", "table_registered", "table_registration_resolved", "commit_request_submitted", "commit_adjudicated", "current_reference_published", "catalog_principal_bound", "catalog_operation_granted", "scoped_credential_vended", "credential_revoked", "catalog_exported", "registration_dropped", "catalog_retired"],
        states=["unregistered", "registered", "active", "commit_pending", "commit_conflicted", "current", "suspended", "dropping", "dropped", "retired"],
        refusals=["namespace_conflict", "registration_conflict", "table_identity_unresolved", "base_reference_stale", "table_precondition_failed", "commit_conflict", "catalog_authority_missing", "operation_grant_missing", "credential_scope_excessive", "credential_expired_or_revoked", "export_cut_incomplete", "provider_offer_unqualified"],
        services=["NamespaceValidationService", "RegistrationResolutionService", "CommitAdjudicationService", "CatalogAuthorizationService", "CredentialScopeService", "CatalogExportService"],
        specifications=["NamespaceUniquenessSpecification", "RegistrationCompletenessSpecification", "CommitPreconditionSpecification", "CommitAtomicitySpecification", "CredentialLeastPrivilegeSpecification", "CatalogExportCompletenessSpecification"],
        policies=["when a commit base reference is stale refuse or invoke an explicit rebase policy", "when a registration changes publish an editioned catalog fact", "when catalog authority is revoked fence new commits and credentials", "when a credential expires refuse new operations", "when export begins bind one immutable catalog evidence cut"],
        sagas=["TableRegistrationProcess", "CatalogCommitProcess", "CredentialVendingProcess", "CatalogMigrationProcess", "CatalogRetirementProcess"],
        reads=["NamespaceTreeView", "TableRegistrationView", "CurrentReferenceView", "CommitConflictView", "PrincipalGrantView", "CredentialLeaseView", "CatalogMigrationView"],
        time=["catalog fact validity and recording time are distinct", "base and current references identify exact logical cuts", "commit request adjudication and publication times are separate", "credential issue expiry use and revocation times are explicit", "catalog export cut and replay time are distinct"],
        neighbors=[("semantic.analytical_table_state", "anti_corruption_layer", "validate table-state identities and commit preconditions"), ("resource.object_storage", "customer_supplier", "resolve metadata locations and scoped access"), ("neighbor.enterprise_identity", "anti_corruption_layer", "resolve principals without importing identity lifecycle"), ("neighbor.data_use_policy", "customer_supplier", "obtain business-use decisions and obligations"), ("product.query_execution_service", "open_host_service", "publish catalog resolution and credential contracts"), ("product.managed_table_maintenance", "open_host_service", "adjudicate maintenance commit requests")],
        nfr=["linearizable or explicitly weaker current-reference semantics", "bounded namespace and commit operations", "idempotent mutation commands", "least-privilege credential handling", "fail-closed authority", "complete audit and migration evidence"],
        language="Catalog, namespace, registration, table identity, current reference, base reference, commit request, commit receipt, principal, grant, credential lease, revocation and export cut each have one meaning; table-format and identity-provider homonyms cross ACLs.",
        integration="Only versioned namespace, registration, current-reference, commit, credential-revocation and export facts cross the boundary; authorization internals, table state and provider DTOs remain private.",
    ),
    "product.managed_table_maintenance": product_spec(
        key="managed_table_maintenance",
        question="How can a table owner plan, authorize, execute, validate and recover physical maintenance while proving logical equivalence, concurrency safety, retention safety and bounded resource use?",
        classification="core_horizontal_table_maintenance_product",
        users=["table_owner", "lakehouse_operator", "performance_engineer", "data_governance_reviewer", "recovery_operator"],
        harmed=["data_consumer", "concurrent_writer", "data_subject", "retention_authority", "resource_tenant"],
        job="Operate compaction, clustering, statistics, snapshot expiry and orphan cleanup over exact table cuts with reversible or explicitly authorized destructive effects.",
        outcomes=["typed_maintenance_plan", "logical_equivalence_evidence", "retention_safe_cleanup", "bounded_resource_and_cost_receipts", "recoverable_commit_or_explicit_unknown"],
        negative="Does not own table-format meaning, catalog current-reference authority, query workload intent, legal retention policy, compute scheduling, object-store deletion mechanics or source business facts.",
        inside=["maintenance programmes and policies", "candidate discovery over exact table cuts", "compaction clustering statistics expiry and cleanup plans", "logical-equivalence and reachability proofs", "concurrency and commit premises", "execution attempts validation compensation and receipts", "maintenance SLO budget and lifecycle"],
        outside=["table snapshot semantics", "catalog commit authority", "query execution", "legal retention decision", "resource scheduling", "object storage implementation", "business quality acceptance"],
        values=["MaintenanceProgrammeId", "MaintenancePolicyEdition", "TableCutRef", "CandidateSet", "RewritePlan", "ClusteringObjective", "ReachabilityCut", "RetentionDecisionRef", "ResourceBudget", "EquivalenceVerdict", "MaintenanceReceipt"],
        entities=["MaintenanceProgramme", "MaintenanceRun", "MaintenanceCandidate", "RewriteAttempt", "CleanupAttempt", "ValidationOccurrence", "CompensationOccurrence"],
        aggregates=[
            {"root": "MaintenanceProgramme", "members": ["table_ref", "policy", "objectives", "budgets", "schedule", "lifecycle"], "consistency": "one edition fixes admitted maintenance semantics and authority"},
            {"root": "MaintenanceRun", "members": ["base_cut", "candidate_set", "plan", "attempts", "validation", "commit_state"], "consistency": "all effects and validation bind one immutable base cut and plan digest"},
            {"root": "CleanupAttempt", "members": ["reachability_cut", "retention_decisions", "delete_intents", "receipts", "unknowns"], "consistency": "no object is eligible unless unreachable under every admitted protected reference"},
        ],
        invariants=["maintenance changes physical representation without changing admitted logical results", "every plan binds an exact table cut and policy edition", "new concurrent snapshots cannot be overwritten by a stale plan", "compaction and clustering success require equivalence evidence", "snapshot expiry and orphan cleanup require reachability plus retention authority", "unknown delete or commit completion is reconciled before retry", "resource and cost budgets are precharged or refused", "maintenance approval is not catalog commit authority"],
        commands=["create_maintenance_programme", "bind_table_and_policy", "discover_candidates", "plan_compaction", "plan_clustering", "plan_statistics_refresh", "plan_snapshot_expiry", "prove_reachability", "approve_maintenance_plan", "start_maintenance_run", "record_rewrite_attempt", "validate_logical_equivalence", "submit_maintenance_commit", "record_cleanup_attempt", "compensate_maintenance", "close_maintenance_run", "suspend_programme", "retire_programme"],
        events=["maintenance_programme_created", "table_and_policy_bound", "candidates_discovered", "compaction_planned", "clustering_planned", "statistics_refresh_planned", "snapshot_expiry_planned", "reachability_proved", "maintenance_plan_approved", "maintenance_run_started", "rewrite_attempt_recorded", "logical_equivalence_validated", "maintenance_commit_submitted", "cleanup_attempt_recorded", "maintenance_compensated", "maintenance_run_closed", "programme_suspended", "programme_retired"],
        states=["draft", "bound", "candidate_discovery", "planning", "approval_pending", "approved", "running", "validating", "commit_pending", "cleanup_pending", "compensating", "completed", "failed", "unknown", "suspended", "retired"],
        refusals=["table_cut_unresolved", "maintenance_policy_missing", "candidate_set_stale", "objective_conflict", "resource_budget_exceeded", "concurrent_snapshot_conflict", "equivalence_unproved", "retention_authority_missing", "reachability_incomplete", "protected_snapshot_reachable", "catalog_commit_refused", "effect_completion_unknown", "compensation_unavailable", "provider_offer_unqualified"],
        services=["MaintenanceCandidateService", "RewritePlanningService", "ClusteringPlanningService", "LogicalEquivalenceService", "ReachabilityService", "MaintenanceCommitService", "RecoveryAndCompensationService"],
        specifications=["CandidateFreshnessSpecification", "RewritePlanSpecification", "ConcurrencySafetySpecification", "LogicalEquivalenceSpecification", "RetentionAuthoritySpecification", "ReachabilityCompletenessSpecification", "BudgetAdmissionSpecification", "MaintenanceCompletionSpecification"],
        policies=["when the base cut changes invalidate or explicitly rebase the plan", "when equivalence cannot be proved refuse publication", "when an object remains reachable exclude it from cleanup", "when retention authority is unresolved refuse destructive work", "when completion is unknown reconcile before retry", "when budgets are exceeded suspend additional work and retain partial evidence"],
        sagas=["MaintenancePlanningProcess", "RewriteAndValidationProcess", "MaintenanceCommitProcess", "RetentionSafeCleanupProcess", "UnknownCompletionRecoveryProcess"],
        reads=["MaintenanceProgrammeView", "CandidateInventoryView", "PlanAndObjectiveView", "RunProgressView", "EquivalenceEvidenceView", "ReachabilityAndRetentionView", "ResourceCostView", "RecoveryView"],
        time=["table cut validity and recording time are distinct", "policy and retention decisions have explicit validity intervals", "candidate discovery plan execution and commit times are independent", "reachability is evaluated at a named cut", "unknown completion and reconciliation times remain explicit"],
        neighbors=[("semantic.analytical_table_state", "customer_supplier_acl", "interpret table cuts and validate logical equivalence premises"), ("product.catalog_service", "customer_supplier", "submit authorized current-reference transitions"), ("neighbor.retention_policy", "anti_corruption_layer", "obtain protected-reference and expiry authority"), ("resource.compute", "customer_supplier", "bind qualified bounded execution capacity"), ("resource.object_storage", "effect_port", "submit rewrite and delete intents and receive occurrence receipts"), ("neighbor.lineage", "published_language", "publish plan derivation and maintenance receipts"), ("neighbor.data_quality", "customer_supplier", "consume bounded post-maintenance assertions without transferring maintenance acceptance")],
        nfr=["deterministic semantic planning given declared inputs", "bounded candidates memory time compute and cost", "backpressure and cooperative cancellation", "fail-safe destructive effects", "idempotent fenced attempts", "evidence binds exact cuts policies plans providers and outcomes"],
        language="Programme, policy, candidate, plan, rewrite, compaction, clustering, statistics refresh, expiry, orphan, reachability, retention, equivalence, commit, cleanup, compensation and receipt are non-interchangeable terms; table-format and provider homonyms cross ACLs.",
        integration="Only minimized maintenance lifecycle, plan, equivalence, commit, cleanup, compensation and receipt events cross the boundary; candidates, provider internals and destructive details remain private unless evidence policy requires disclosure.",
    ),
    "product.data_sharing_exchange": product_spec(
        key="data_sharing_exchange",
        question="How can a provider publish and a recipient consume an exact governed data cut under versioned purpose-bound grants, disclosure evidence, revocation, recall and portable exit?",
        classification="core_horizontal_data_sharing_product",
        users=["data_provider", "data_recipient", "sharing_administrator", "privacy_or_policy_reviewer", "auditor"],
        harmed=["data_subject", "source_owner", "recipient_organization", "unauthorized_recipient", "downstream_consumer"],
        job="Create, discover, subscribe to, resolve, disclose, revoke, recall and exit governed shares without transferring source semantic ownership.",
        outcomes=["versioned_share_definition", "exact_shared_cut", "purpose_and_recipient_bound_grant", "disclosure_and_consumption_receipts", "effective_revocation_and_recall", "portable_share_export"],
        negative="Does not own source table meaning, identity proofing, business-use policy, consent, data transformation, transport implementation, recipient analytics or downstream action authority.",
        inside=["share and shared-object lifecycle", "provider and recipient bindings", "exact data-cut references", "purpose-bound grants and subscriptions", "listing and resolution contracts", "disclosure and consumption receipts", "revocation recall and downstream-notice evidence", "share export and exit"],
        outside=["source table state and business semantics", "enterprise identity lifecycle", "privacy and data-use policy decisions", "physical storage and transfer", "recipient query execution", "commercial marketplace settlement", "recipient business decisions"],
        values=["ShareId", "ShareEdition", "SharedObjectId", "SharedCutRef", "ProviderRef", "RecipientRef", "PurposeRef", "GrantId", "GrantScope", "SubscriptionId", "DisclosureReceipt", "RevocationRef", "RecallRef", "ShareExportCut"],
        entities=["Share", "SharedObject", "RecipientBinding", "AccessGrant", "Subscription", "DisclosureOccurrence", "RevocationOccurrence", "RecallOccurrence", "ShareExport"],
        aggregates=[
            {"root": "Share", "members": ["provider", "objects", "cut_policy", "listing", "lifecycle", "edition"], "consistency": "a published edition fixes objects, cut semantics and provider authority"},
            {"root": "AccessGrant", "members": ["share_ref", "recipient_ref", "purpose_ref", "scope", "validity", "revocation"], "consistency": "grant scope never exceeds policy and share authority"},
            {"root": "Subscription", "members": ["share_ref", "recipient_ref", "grant_ref", "cursor", "deliveries", "state"], "consistency": "every resolved cut and disclosure binds one valid grant edition"},
            {"root": "RecallOccurrence", "members": ["affected_cuts", "recipient_notices", "acknowledgements", "residuals"], "consistency": "recall completion retains every known downstream residual"},
        ],
        invariants=["share identity is distinct from shared object grant subscription and disclosure", "every disclosure binds an exact data cut, recipient, purpose, grant and policy decision", "grant is not disclosure and subscription is not consumption", "source semantic ownership never transfers to the sharing service", "revoked grants cannot authorize new disclosures", "recall propagates to known recipients and retains unresolved downstream residuals", "well-formed protocol messages do not prove authorization or truthful content", "provider identity cannot change share semantics"],
        commands=["draft_share", "bind_provider_authority", "add_shared_object", "bind_shared_cut_policy", "submit_share_review", "publish_share_edition", "register_recipient", "request_access_grant", "issue_access_grant", "create_subscription", "resolve_shared_cut", "record_disclosure", "record_consumption_acknowledgement", "revoke_access_grant", "recall_shared_cut", "record_recall_acknowledgement", "export_share", "retire_share"],
        events=["share_drafted", "provider_authority_bound", "shared_object_added", "shared_cut_policy_bound", "share_review_requested", "share_edition_published", "recipient_registered", "access_grant_requested", "access_grant_issued", "subscription_created", "shared_cut_resolved", "disclosure_recorded", "consumption_acknowledgement_recorded", "access_grant_revoked", "shared_cut_recalled", "recall_acknowledgement_recorded", "share_exported", "share_retired"],
        states=["draft", "authority_bound", "review_pending", "published", "grant_pending", "active", "suspended", "revoking", "revoked", "recalling", "recalled", "exporting", "retired"],
        refusals=["provider_authority_missing", "shared_object_unresolved", "shared_cut_unresolvable", "recipient_identity_unresolved", "purpose_unbound", "policy_refused", "grant_scope_excessive", "grant_expired_or_revoked", "subscription_incompatible", "disclosure_evidence_incomplete", "recall_propagation_incomplete", "export_cut_incomplete", "protocol_profile_unsupported", "provider_offer_unqualified"],
        services=["ShareDefinitionService", "RecipientBindingService", "GrantAdjudicationService", "SharedCutResolutionService", "DisclosureEvidenceService", "RevocationPropagationService", "RecallCoordinationService", "ShareExportService"],
        specifications=["SharePublicationSpecification", "ProviderAuthoritySpecification", "RecipientPurposeSpecification", "GrantScopeSpecification", "SharedCutResolutionSpecification", "DisclosureAuthorizationSpecification", "RevocationEffectivenessSpecification", "RecallCompletenessSpecification", "ShareExportCompletenessSpecification"],
        policies=["when provider authority expires suspend new disclosures", "when a grant is revoked fence every new cut resolution and disclosure", "when a shared cut is recalled notify every known recipient and retain unresolved residuals", "when policy obligations change re-evaluate active grants", "when protocol or schema compatibility fails refuse rather than silently narrow the share", "when exit begins export definitions grants subscriptions receipts and active-work disposition"],
        sagas=["SharePublicationProcess", "AccessGrantProcess", "SubscriptionLifecycleProcess", "RevocationPropagationProcess", "SharedCutRecallProcess", "ShareExitProcess"],
        reads=["ShareCatalogView", "SharedObjectView", "RecipientGrantView", "SubscriptionView", "DisclosureLedgerView", "RevocationImpactView", "RecallProgressView", "ShareExitView"],
        time=["share and grant validity time are distinct from recording time", "shared cut identifies exact source-valid and recording cuts", "grant issue expiry use and revocation times are explicit", "disclosure and acknowledgement times are independent", "recall effective time and downstream acknowledgement time remain distinct"],
        neighbors=[("semantic.analytical_table_state", "anti_corruption_layer", "resolve exact shared table cuts without importing table meaning"), ("neighbor.enterprise_identity", "anti_corruption_layer", "resolve provider and recipient identities"), ("neighbor.data_use_policy", "customer_supplier", "obtain purpose, disclosure and obligation decisions"), ("neighbor.privacy_rights", "customer_supplier", "receive revocation erasure or restriction obligations"), ("resource.object_storage", "customer_supplier", "bind qualified delivery or presigned-access mechanisms"), ("product.query_execution_service", "open_host_service", "expose recipient-readable cut contracts"), ("neighbor.lineage", "published_language", "publish disclosure revocation and recall evidence")],
        nfr=["deterministic grant and cut resolution", "bounded listing and disclosure", "fail-closed authorization and revocation", "replay-safe idempotent occurrences", "residency privacy and egress constraints are explicit", "complete evidence by share grant cut recipient purpose provider and policy edition"],
        language="Share, shared object, shared cut, provider, recipient, purpose, grant, subscription, listing, resolution, disclosure, consumption, revocation, recall and export are non-interchangeable terms; source, identity, policy and transport homonyms cross named ACLs.",
        integration="Only minimized share-publication, grant, subscription, disclosure, revocation, recall and export facts cross the boundary; identity proofs, policy internals, source semantics and provider DTOs remain behind ACLs.",
    ),
}


PRODUCT_LIBRARIES = {
    "library.lakehouse_environment_lifecycle": ["product.managed_lakehouse_experience"],
    "library.catalog_protocol_types": ["product.catalog_service"],
    "library.maintenance_plan": ["product.managed_table_maintenance"],
    "library.logical_equivalence_oracle": ["product.managed_table_maintenance"],
    "library.data_sharing_contract": ["product.data_sharing_exchange"],
}


def requirement(requirement_id: str, consumer: str, capability: str, phase: str, refusal: str) -> dict[str, Any]:
    return {
        "requirement_id": requirement_id,
        "consumer_ref": consumer,
        "capability_ref": capability,
        "binding_phase": phase,
        "minimum_qualified_offers": 1,
        "status": "unbound",
        "refusal": refusal,
    }


PRODUCT_REQUIREMENTS = [
    requirement("requirement.experience.environment", "product.managed_lakehouse_experience", "capability.environment_reconciliation", "compile_time", "environment_reconciliation_contract_missing"),
    requirement("requirement.catalog.namespace_registry", "product.catalog_service", "capability.catalog_namespace_registry", "compile_time", "catalog_namespace_contract_missing"),
    requirement("requirement.catalog.commit_coordination", "product.catalog_service", "capability.catalog_commit_coordination", "runtime", "catalog_commit_contract_missing"),
    requirement("requirement.catalog.credential_vending", "product.catalog_service", "capability.credential_vending", "runtime", "credential_vending_contract_missing"),
    requirement("requirement.maintenance.plan", "product.managed_table_maintenance", "capability.table_maintenance_plan", "compile_time", "maintenance_plan_contract_missing"),
    requirement("requirement.maintenance.compaction", "product.managed_table_maintenance", "capability.table_compaction", "runtime", "compaction_contract_missing"),
    requirement("requirement.maintenance.clustering", "product.managed_table_maintenance", "capability.table_clustering", "runtime", "clustering_contract_missing"),
    requirement("requirement.maintenance.snapshot_expiry", "product.managed_table_maintenance", "capability.table_snapshot_expiry", "runtime", "snapshot_expiry_contract_missing"),
    requirement("requirement.sharing.publish_consume_revoke", "product.data_sharing_exchange", "capability.data_sharing", "runtime", "data_sharing_contract_missing"),
]


NEW_LIBRARIES = [
    {
        "library_id": "library.lakehouse_environment_lifecycle",
        "owner_ref": "semantic.managed_lakehouse_experience",
        "class": "semantic_pure",
        "types": ["EnvironmentDeclaration", "SupportedComponentProfile", "CapabilityClosure", "DesiredEnvironmentState", "ObservedEnvironmentState", "DriftSet", "ReadinessVerdict", "RolloutPlan", "RollbackPlan", "ExitPlan"],
        "operations": ["type_environment", "resolve_capability_closure", "compare_desired_observed", "classify_drift", "evaluate_readiness", "plan_rollout", "plan_rollback", "plan_exit"],
        "decisions": ["profile_selection", "binding_precedence", "compatibility_policy", "drift_policy", "readiness_policy", "rollout_policy", "rollback_policy", "exit_policy"],
        "invariants": ["provider names cannot select semantics", "readiness requires closed qualified bindings", "desired and observed state remain distinct", "rollback or irreversible authority is explicit", "exit dispositions every active occurrence"],
        "refusals": ["capability_gap", "semantic_edition_conflict", "offer_unqualified", "readiness_unproved", "drift_unknown", "rollback_unavailable", "exit_incomplete"],
        "dependencies": [],
        "effect_boundary": "pure_effect_intents",
        "provides": ["capability.environment_reconciliation"],
        "evidence_refs": ["evidence.cncf.platforms"],
    },
    {
        "library_id": "library.data_sharing_contract",
        "owner_ref": "semantic.data_sharing",
        "class": "semantic_pure",
        "types": ["Share", "ShareEdition", "SharedObject", "SharedCut", "Recipient", "Purpose", "DeliveryGrant", "Subscription", "DisclosureReceipt", "Revocation", "Recall"],
        "operations": ["draft_share", "publish_share", "resolve_shared_cut", "adjudicate_grant", "create_subscription", "record_disclosure", "revoke_grant", "recall_cut", "export_share"],
        "decisions": ["cut_resolution_policy", "recipient_binding_policy", "purpose_binding_policy", "grant_scope_policy", "revocation_policy", "recall_policy", "export_policy"],
        "invariants": ["share grant subscription disclosure and consumption are distinct", "every disclosure binds exact cut recipient purpose grant and policy", "revoked grants authorize no new disclosure", "source semantic ownership never transfers", "recall retains unresolved downstream residuals"],
        "refusals": ["provider_authority_missing", "shared_cut_unresolved", "recipient_unresolved", "purpose_unbound", "policy_refused", "grant_expired_or_revoked", "recall_incomplete", "export_incomplete"],
        "dependencies": [],
        "effect_boundary": "pure_effect_intents",
        "provides": ["capability.data_sharing"],
        "evidence_refs": ["evidence.delta.sharing"],
    },
]


def pascal(value: str) -> str:
    return "".join(part.capitalize() for part in value.replace("-", "_").split("_"))


def dossier(product_ref: str, spec: dict[str, Any]) -> dict[str, Any]:
    roots = [row["root"] for row in spec["aggregates"]]
    return {
        "dossier_id": f"ddd.lakehouse.{spec['key']}",
        "product_ref": product_ref,
        "status": "candidate_not_ratified",
        "product_truth": {
            "sovereign_question": spec["question"],
            "users": spec["users"],
            "harmed_parties": spec["harmed"],
            "jobs": [spec["job"]],
            "measurable_outcomes": spec["outcomes"],
            "negative_mission": spec["negative"],
        },
        "strategic_and_tactical_ddd": {
            "domain_vision_statement": spec["question"].replace("How can ", "Own how ").rstrip("?"),
            "subdomain_classification": spec["classification"],
            "bounded_context_boundary": {"inside": spec["inside"], "outside": spec["outside"]},
            "ubiquitous_language_policy": spec["language"],
            "context_map": [{"neighbor_ref": ref, "relationship": relationship, "translation": translation} for ref, relationship, translation in spec["neighbors"]],
            "anti_corruption_layers": [f"acl.{ref.split('.')[-1]}" for ref, _, _ in spec["neighbors"]],
            "published_language": spec["values"] + ["TypedCommand", "DomainEvent", "TypedRefusal", "EvidenceReceipt"],
            "value_objects": spec["values"],
            "entities": spec["entities"],
            "aggregates": spec["aggregates"],
            "aggregate_roots": roots,
            "aggregate_invariants": spec["invariants"],
            "commands": spec["commands"],
            "domain_events": spec["events"],
            "refusal_failure_catalog": spec["refusals"],
            "domain_services": spec["services"],
            "application_services": [pascal(command) + "UseCase" for command in spec["commands"][:8]],
            "repositories": [root + "Repository" for root in roots],
            "factories": [root + "Factory" for root in roots] + [pascal(spec["key"]) + "EditionFactory"],
            "specifications": spec["specifications"],
            "state_machine": {"states": spec["states"], "transition_policy": "Only named commands satisfying aggregate invariants may emit the corresponding past-tense event; unknown completion remains explicit and must be reconciled."},
            "policies_and_reactions": spec["policies"],
            "sagas_and_process_managers": spec["sagas"],
            "read_models_and_projections": spec["reads"],
            "integration_event_policy": spec["integration"],
            "concurrency_and_idempotency": ["optimistic aggregate edition", "idempotency key per command and effect attempt", "fenced provider and runtime occurrences", "append-only attempt and receipt identities", "unknown completion reconciles before retry"],
            "time_model": spec["time"],
            "event_storming_swimlanes": spec["users"] + ["runtime_provider", "external_authority", "affected_party"],
            "nonfunctional_laws": spec["nfr"] + ["provider identity cannot change semantic meaning", "removing every model and agent extension preserves the complete deterministic core"],
        },
    }


def strip_managed(source: dict[str, Any]) -> dict[str, Any]:
    source = json.loads(json.dumps(source))
    for key in ("ddd_dossiers", "ddd_delegations", "binding_maps", "binding_gaps"):
        source.pop(key, None)
    for row in source.get("artifacts", []):
        if row.get("artifact_id") in SPECS:
            for field in PRODUCT_FIELDS:
                row.pop(field, None)
    source["requirements"] = [
        row for row in source.get("requirements", [])
        if row.get("requirement_id") not in MANAGED_REQUIREMENT_IDS
    ]
    source["libraries"] = [
        row for row in source.get("libraries", [])
        if row.get("library_id") not in MANAGED_LIBRARY_IDS
    ]
    for row in source["libraries"]:
        row.pop("product_ref", None)
        row.pop("product_refs", None)
    source["compiler_library_bindings"] = [
        row for row in source.get("compiler_library_bindings", [])
        if row.get("binding_id") not in {
            "binding.lakehouse.data_sharing_contract",
            "binding.lakehouse.environment_lifecycle",
        }
    ]
    return source


def normalize_binding_maps(source: dict[str, Any]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    maps: list[dict[str, Any]] = []
    gaps: list[dict[str, Any]] = []
    exact = {row["local_library_ref"]: row for row in source["compiler_library_bindings"]}
    for library in sorted(source["libraries"], key=lambda row: row["library_id"]):
        library_ref = library["library_id"]
        suffix = library_ref.removeprefix("library.")
        product_refs = PRODUCT_LIBRARIES.get(library_ref, [])
        legacy = exact.get(library_ref)
        if legacy:
            maps.append({
                "binding_map_id": f"binding.map.lakehouse.{suffix}",
                "product_refs": product_refs,
                "abstract_library_ref": library_ref,
                "concrete_library_refs": legacy["exact_library_refs"],
                "required_requirement_refs": legacy["required_requirement_refs"],
                "portable_offer_refs": legacy["portable_offer_refs"],
                "compiler_disposition": "structurally_projected_unqualified",
                "gap_ref": None,
                "portable_offer": False,
            })
            continue
        gap_ref = f"gap.lakehouse.binding.{suffix}"
        maps.append({
            "binding_map_id": f"binding.map.lakehouse.{suffix}",
            "product_refs": product_refs,
            "abstract_library_ref": library_ref,
            "concrete_library_refs": [],
            "required_requirement_refs": [],
            "portable_offer_refs": [],
            "compiler_disposition": "missing_exact_compiler_library_contract",
            "gap_ref": gap_ref,
            "portable_offer": False,
        })
        gaps.append({
            "gap_id": gap_ref,
            "product_refs": product_refs,
            "abstract_library_ref": library_ref,
            "blocking": True,
            "statement": "No compiler contribution currently owns the full declarative lakehouse environment lifecycle: capability closure, desired/observed comparison, readiness, drift, rollout, rollback and exit without absorbing component semantics.",
            "closure_evidence": "Add one semantic-owner compiler library with exact types, operations, decisions, laws, refusals, finite bounds, removal seams and executable conformance oracles; provider qualification remains separate.",
        })
    return maps, gaps


def enrich(source: dict[str, Any]) -> dict[str, Any]:
    source = strip_managed(source)
    source["crosswalks"] = [
        row for row in source.get("crosswalks", [])
        if row.get("legacy_ref") != "product.ingestion_delivery_service"
    ]
    source["crosswalks"].append({
        "legacy_ref": "product.ingestion_delivery_service",
        "canonical_refs": ["product.ingestion_delivery"],
        "disposition": "completed_rename",
    })
    artifacts = {row["artifact_id"]: row for row in source["artifacts"]}
    for product_ref, spec in SPECS.items():
        artifacts[product_ref].update({
            "sovereign_question": spec["question"],
            "users": spec["users"],
            "harmed_parties": spec["harmed"],
            "jobs": [spec["job"]],
            "outcomes": spec["outcomes"],
            "negative_mission": spec["negative"],
            "lifecycle_states": spec["states"],
            "commands": spec["commands"],
            "events": spec["events"],
            "invariants": spec["invariants"],
            "refusals": spec["refusals"],
            "automation_modality": AUTOMATION,
        })
    source["requirements"].extend(PRODUCT_REQUIREMENTS)
    source["libraries"].extend(NEW_LIBRARIES)
    for row in source["libraries"]:
        if row["library_id"] in PRODUCT_LIBRARIES:
            row["product_refs"] = PRODUCT_LIBRARIES[row["library_id"]]
    source["compiler_library_bindings"].append({
        "binding_id": "binding.lakehouse.data_sharing_contract",
        "local_library_ref": "library.data_sharing_contract",
        "exact_library_refs": ["library.persistence.sharing_contract"],
        "required_requirement_refs": ["requirement.persistence.sharing_contract.implementation"],
        "portable_offer_refs": ["offer.persistence.sharing_contract.portable"],
        "status": "structurally_mapped_unqualified",
        "portability_claim": False,
    })
    source["compiler_library_bindings"].append({
        "binding_id": "binding.lakehouse.environment_lifecycle",
        "local_library_ref": "library.lakehouse_environment_lifecycle",
        "exact_library_refs": ["library.product_composition.environment_lifecycle"],
        "required_requirement_refs": ["requirement.product_composition.environment_lifecycle.implementation"],
        "portable_offer_refs": ["offer.product_composition.environment_lifecycle.portable"],
        "status": "structurally_mapped_unqualified",
        "portability_claim": False,
    })
    maps, gaps = normalize_binding_maps(source)
    source["binding_maps"] = maps
    source["binding_gaps"] = gaps
    source["ddd_dossiers"] = [dossier(product_ref, spec) for product_ref, spec in SPECS.items()]
    source["ddd_delegations"] = ddd_delegations()
    return source


def source_bytes() -> bytes:
    current = json.loads(SOURCE.read_text(encoding="utf-8"))
    return (json.dumps(enrich(current), ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    expected = source_bytes()
    if args.check:
        if SOURCE.read_bytes() != expected:
            print("ERROR lakehouse source.json enrichment is stale")
            return 1
        print("CHECK PASS lakehouse source enrichment")
        return 0
    SOURCE.write_bytes(expected)
    print("BUILD PASS lakehouse source enrichment")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
