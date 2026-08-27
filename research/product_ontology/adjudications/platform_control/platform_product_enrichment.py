#!/usr/bin/env python3
"""Deep product/library decomposition for developer platform, runtime control, and FinOps.

The horizontal research universes remain the owners of reusable runtime/resource and
commercial semantics.  This module defines the independently adopted product facades, splits
their local library seams at semantic/effect boundaries, and projects every seam to existing
research contracts without claiming implementation qualification.
"""

from __future__ import annotations

from typing import Any

from solution_compiler_enrichment import AUTOMATION, CENTRAL_REGISTRY, CONFORMANCE_REGISTRY, DDD_FIELDS


DEVELOPER = "product.data_product_developer_platform"
RUNTIME = "product.runtime_resource_control"
FINOPS = "product.finops_allocation"
PRODUCTS = {DEVELOPER, RUNTIME, FINOPS}

DEVELOPER_LIBRARIES = {
    "library.platform.blueprint",
    "library.platform.developer.paved_path_plan",
    "library.platform.paved_path_runtime",
    "library.platform.developer.platform_conformance",
}
RUNTIME_LIBRARIES = {
    "library.platform.runtime.work_contract",
    "library.platform.resource_vector",
    "library.platform.runtime.resource_offer",
    "library.platform.runtime.demand_offer_compatibility",
    "library.platform.runtime.quota_ledger",
    "library.platform.admission",
    "library.platform.runtime.scheduler_policy",
    "library.platform.placement",
    "library.platform.runtime.reservation_ledger",
    "library.platform.runtime.allocation_ledger",
    "library.platform.runtime.lease_fencing",
    "library.platform.runtime.preemption_control",
    "library.platform.runtime.autoscaling_control",
    "library.platform.runtime.backpressure_control",
    "library.platform.runtime.deadline_cancellation",
    "library.platform.runtime.checkpoint_contract",
    "library.platform.runtime.backend_spi",
    "library.platform.runtime_attempt",
    "library.platform.runtime.receipt_contract",
    "library.platform.runtime.usage_accounting",
    "library.platform.runtime.energy_accounting",
    "library.platform.runtime.conformance_oracles",
}
FINOPS_LIBRARIES = {
    "library.platform.meter",
    "library.platform.finops.cost_occurrence",
    "library.platform.finops.cost_attribution",
    "library.platform.cost_normalization",
    "library.platform.cost_allocation",
    "library.platform.finops.allocation_reconciliation",
    "library.platform.budget_precharge",
    "library.platform.finops.unit_cost",
}
PRODUCT_LIBRARIES = {
    DEVELOPER: DEVELOPER_LIBRARIES,
    RUNTIME: RUNTIME_LIBRARIES,
    FINOPS: FINOPS_LIBRARIES,
}


def artifact(ident: str, kind: str, name: str, owner: str | None, definition: str, refs: list[str]) -> dict[str, Any]:
    return {
        "artifact_id": ident,
        "kind": kind,
        "name": name,
        "status": "candidate",
        "semantic_owner_ref": owner,
        "adoption_unit": False,
        "operated": False,
        "definition": definition,
        "evidence_refs": refs,
    }


def library(
    ident: str,
    product: str,
    owner: str,
    provides: list[str],
    types: list[str],
    operations: list[str],
    decisions: list[str],
    invariants: list[str],
    refusals: list[str],
    dependencies: list[str],
    effect_boundary: str,
    refs: list[str],
    class_: str = "semantic_pure",
) -> dict[str, Any]:
    return {
        "library_id": ident,
        "class": class_,
        "owner_ref": owner,
        "provides": provides,
        "types": types,
        "operations": operations,
        "decisions": decisions,
        "invariants": invariants,
        "refusals": refusals,
        "dependencies": dependencies,
        "effect_boundary": effect_boundary,
        "evidence_refs": refs,
        "product_refs": [product],
    }


def requirement(ident: str, product: str, capability: str, phase: str, refusal: str) -> dict[str, Any]:
    return {
        "requirement_id": ident,
        "consumer_ref": product,
        "capability_ref": capability,
        "binding_phase": phase,
        "minimum_qualified_offers": 1,
        "status": "unbound",
        "refusal": refusal,
    }


def binding(local: str, refs: list[str], product: str, origin: str = CENTRAL_REGISTRY) -> dict[str, Any]:
    return {
        "binding_map_id": f"binding.platform.product.{local.removeprefix('library.platform.').replace('.', '_')}",
        "abstract_library_ref": local,
        "concrete_library_refs": refs,
        "concrete_library_origins": {ref: origin for ref in refs},
        "compiler_disposition": "structurally_projected_unqualified",
        "gap_ref": None,
        "portable_offer": False,
        "product_refs": [product],
    }


def _developer_dossier() -> dict[str, Any]:
    truth = {
        "sovereign_question": "How can a data-product team discover, instantiate, evolve, verify, escape, and retire a supported paved path without mistaking a portal, template render, or provider reconciliation for a conformant service?",
        "users": ["data_product_team", "platform_product_manager", "platform_engineer", "service_owner", "assurance_reviewer", "support_operator"],
        "harmed_parties": ["service_user", "data_subject", "source_owner", "runtime_operator", "downstream_consumer"],
        "jobs": ["publish editioned blueprints", "plan and instantiate paved paths", "expose supported decisions and escape hatches", "evaluate exact-profile conformance", "upgrade rollback and retire instances with evidence"],
        "measurable_outcomes": ["time_to_first_conformant_instance", "successful_self_service_rate", "upgrade_and_rollback_success", "escape_hatch_visibility", "conformance_evidence_freshness", "verified_exit_rate"],
        "negative_mission": "Does not own business-domain meaning, source data, compiler semantics, runtime scheduling, provider qualification, security authority, production acceptance, or every developer tool; a portal is only a projection.",
    }
    ddd = {
        "domain_vision_statement": "Own the supported self-service contract from an editioned platform blueprint to an evidence-bearing platform instance and its reversible lifecycle.",
        "subdomain_classification": {"core": ["blueprint_and_paved_path_product_semantics", "decision_and_escape_hatch_exposure"], "supporting": ["instance_lifecycle", "platform_conformance_coordination", "developer_feedback"], "generic_or_imported": ["identity_and_policy", "compiler", "runtime_control", "catalog_storage", "observability", "incident_management", "build_and_deployment"]},
        "bounded_context_boundary": {"inside": ["blueprint editions", "paved-path contracts", "instantiation plans", "supported interfaces", "guardrails and escape hatches", "instance lifecycle", "platform conformance profiles and results"], "outside": ["business solution intent", "provider qualification", "resource admission and placement", "effect authorization", "service SLO truth", "vertical acceptance", "billing"]},
        "ubiquitous_language_policy": {"terms": {"Blueprint": "versioned desired platform capability and decision contract", "PavedPath": "supported workflow plus interfaces guardrails ownership and escape hatch", "InstantiationPlan": "pure proposed realization, not executed effects", "PlatformInstance": "identified lifecycle occurrence of one blueprint edition", "EscapeHatch": "explicit supported deviation with owner and consequences", "ConformanceResult": "exact-profile assessment, never universal fitness"}, "homonym_rules": ["template is not blueprint edition", "portal catalog is not service truth", "instance is not ready service", "conformance is not business acceptance"]},
        "context_map": [{"neighbor_ref": "product.solution_compiler", "relationship": "customer_supplier", "translation": "consume closed solution and artifact plans"}, {"neighbor_ref": RUNTIME, "relationship": "customer_supplier", "translation": "submit effect intents and consume runtime receipts"}, {"neighbor_ref": "component.provider_qualification", "relationship": "customer_supplier", "translation": "consume scoped qualification receipts"}, {"neighbor_ref": "neighbor.identity_policy", "relationship": "conformist_with_acl", "translation": "import authority decisions without copying policy meaning"}, {"neighbor_ref": "context.codegen_build", "relationship": "effect_port", "translation": "submit build intents and retain receipts"}],
        "anti_corruption_layers": ["acl.authored_solution_to_blueprint", "acl.catalog_projection", "acl.template_engine", "acl.provider_composition", "acl.runtime_receipt", "acl.conformance_evidence", "acl.identity_policy"],
        "published_language": ["BlueprintId", "BlueprintEdition", "CapabilityRequirement", "DecisionPoint", "PavedPathId", "EscapeHatch", "InstantiationRequest", "InstantiationPlan", "PlatformInstanceId", "InstanceLifecycleReceipt", "PlatformConformanceProfile", "PlatformConformanceResult", "UpgradePlan", "ExitManifest"],
        "value_objects": ["BlueprintId", "BlueprintEdition", "PavedPathId", "CapabilityRef", "DecisionPointId", "InterfaceEdition", "GuardrailRef", "EscapeHatchId", "InstanceId", "ConformanceProfileRef", "EvidenceRef", "PlanDigest", "AuthorityRef"],
        "entities": ["Blueprint", "PavedPath", "InstantiationPlan", "PlatformInstance", "ConformanceAssessment", "UpgradeCampaign", "RetirementCase"],
        "aggregates": [{"root": "Blueprint", "members": ["editions", "requirements", "decision_points", "paved_paths", "compatibility_policy"], "consistency": "published edition is immutable and every default, constraint, escape hatch and owner is explicit"}, {"root": "PlatformInstance", "members": ["blueprint_ref", "bindings", "effects", "receipts", "lifecycle", "deviations"], "consistency": "desired, submitted, observed and accepted states remain distinct"}, {"root": "ConformanceAssessment", "members": ["profile", "subject", "environment", "checks", "counterexamples", "result", "validity"], "consistency": "result is scoped to exact subject profile environment evidence and time"}],
        "aggregate_roots": ["Blueprint", "PlatformInstance", "ConformanceAssessment"],
        "aggregate_invariants": ["blueprint edition is immutable after publication", "every configurable decision has owner allowed values default law consequences and invalidators", "template render is not effect execution", "reconciliation success is not readiness or acceptance", "escape hatches are visible attributable and reversible or explicitly irreversible", "portal projections never become semantic owners", "conformance result cannot exceed its profile subject environment evidence or validity"],
        "commands": ["draft_blueprint", "publish_blueprint", "deprecate_blueprint", "plan_paved_path", "request_instantiation", "record_effect_receipt", "reconcile_instance", "declare_escape_hatch", "request_upgrade", "request_rollback", "evaluate_platform_conformance", "suspend_instance", "request_retirement", "verify_exit"],
        "domain_events": ["blueprint_drafted", "blueprint_published", "blueprint_deprecated", "paved_path_planned", "instantiation_requested", "effect_receipt_recorded", "instance_reconciled", "escape_hatch_declared", "upgrade_requested", "rollback_requested", "platform_conformance_evaluated", "instance_suspended", "retirement_requested", "exit_verified"],
        "refusal_failure_catalog": ["blueprint_invalid", "edition_conflict", "capability_unresolved", "decision_owner_missing", "default_law_missing", "escape_hatch_unsupported", "provider_binding_unqualified", "effect_authority_missing", "reconciliation_unknown", "conformance_profile_incomplete", "evidence_stale", "counterexample_unresolved", "rollback_semantics_unknown", "exit_incomplete"],
        "domain_services": ["BlueprintCompatibilityService", "PavedPathPlanningService", "DecisionExposureService", "InstanceReconciliationService", "PlatformConformanceService", "UpgradePlanningService", "ExitVerificationService"],
        "application_services": ["PublishBlueprintUseCase", "InstantiatePavedPathUseCase", "ExplainPlatformDecisionUseCase", "UpgradeInstanceUseCase", "EvaluateConformanceUseCase", "RetireInstanceUseCase"],
        "repositories": ["BlueprintRepository", "PlatformInstanceRepository", "ConformanceAssessmentRepository", "UpgradeCampaignRepository", "RetirementCaseRepository"],
        "factories": ["BlueprintFactory", "PavedPathFactory", "InstantiationPlanFactory", "PlatformInstanceFactory", "ConformanceAssessmentFactory", "ExitManifestFactory"],
        "specifications": ["BlueprintClosureSpecification", "DecisionExposureSpecification", "PavedPathSupportSpecification", "ProviderBindingQualificationSpecification", "InstanceConvergenceSpecification", "PlatformConformanceScopeSpecification", "UpgradeCompatibilitySpecification", "ExitCompletenessSpecification"],
        "state_machine": {"Blueprint": ["draft", "published", "deprecated", "withdrawn"], "PlatformInstance": ["planned", "effects_pending", "reconciling", "conformance_pending", "operable", "degraded", "upgrade_pending", "rollback_pending", "suspended", "retiring", "retired", "unknown", "refused"], "law": "unknown provider outcomes are reconciled; no timeout is rewritten as failure and historical editions are never mutated"},
        "policies_and_reactions": ["when blueprint compatibility changes compute affected instances", "when an effect receipt is unknown reconcile before retry", "when conformance expires remove the scoped readiness claim", "when a deviation is declared evaluate its exact guardrail and ownership consequences", "when retirement starts require export dependency and residual-obligation evidence"],
        "sagas_and_process_managers": ["PavedPathInstantiationProcess", "PlatformConformanceProcess", "BlueprintUpgradeCampaign", "RollbackProcess", "ProviderRebindingProcess", "PlatformExitProcess"],
        "read_models_and_projections": ["BlueprintCatalogProjection", "SupportedDecisionMatrix", "PavedPathJourneyView", "InstanceDesiredObservedDiff", "ConformanceEvidenceView", "UpgradeImpactView", "EscapeHatchRegister", "ExitReadinessView"],
        "integration_event_policy": "Only editioned blueprint, plan, instance-lifecycle, conformance, upgrade and exit contracts cross the boundary; provider DTOs, secrets, mutable domain models and unreviewed proposals do not.",
        "concurrency_and_idempotency": ["publication uses optimistic blueprint edition", "instantiation idempotency binds blueprint plan target and authority digests", "effect retries create new occurrences while preserving the logical request", "reconciliation uses observed editions", "upgrade and retirement commands serialize per instance"],
        "time_model": ["blueprint validity differs from recording time", "support windows and deprecation deadlines are editioned", "conformance evidence has observed valid and expiry times", "instance desired and observed time differ", "retirement retains residual obligations until separately discharged"],
        "event_storming_swimlanes": ["data_product_team", "platform_product_manager", "platform_engineer", "solution_compiler", "provider_qualification", "runtime_control", "conformance_authority", "support_operator", "vertical_acceptance_authority"],
        "nonfunctional_laws": ["deterministic planning for frozen inputs", "finite template action reconciliation and evidence budgets", "no hidden effects in semantic libraries", "cooperative cancellation with explicit unknown outcome", "provider-neutral public contracts", "accessible and automatable interfaces", "complete decision and evidence trace", "optional model or agent removal preserves all deterministic platform functions"],
    }
    assert set(ddd) == DDD_FIELDS
    return {"dossier_id": "ddd.platform.data_product_developer_platform", "record_kind": "product_ddd_dossier", "edition": 1, "product_ref": DEVELOPER, "status": "candidate_not_ratified", "product_truth": truth, "strategic_and_tactical_ddd": ddd}


def _runtime_dossier() -> dict[str, Any]:
    truth = {
        "sovereign_question": "Given a finite work contract and qualified resource offers, may it run, where and under what reservation, allocation, lease, cancellation, checkpoint, retry, and accounting guarantees, and what actually occurred?",
        "users": ["workload_owner", "platform_engineer", "scheduler_operator", "runtime_operator", "capacity_planner", "assurance_reviewer"],
        "harmed_parties": ["co_tenant", "downstream_consumer", "infrastructure_owner", "budget_owner", "data_subject", "service_user"],
        "jobs": ["normalize finite resource demand and offers", "admit without weakening hard constraints", "place with declared scheduler assurance", "reserve allocate and fence resources", "execute cancel retry checkpoint and recover attempts", "emit attributable usage energy and runtime receipts"],
        "measurable_outcomes": ["admission_decision_latency", "placement_feasibility_and_assurance", "queue_wait_distribution", "resource_utilization", "deadline_and_cancellation_compliance", "recovery_success", "receipt_completeness", "fencing_violation_count"],
        "negative_mission": "Does not own business job meaning, pipeline DAG semantics, algorithm correctness, physical provider truth, financial allocation, security authority, service acceptance, or invoice truth.",
    }
    ddd = {
        "domain_vision_statement": "Own deterministic control of executable work over finite qualified resources from demand through observed terminal and accounting receipts.",
        "subdomain_classification": {"core": ["resource_contract_algebra", "admission", "placement_and_scheduler_contract", "reservation_allocation_lease_fencing", "attempt_control_and_receipts"], "supporting": ["quota", "preemption", "autoscaling", "backpressure", "checkpointing", "runtime_backend_ports", "usage_and_energy_accounting", "conformance_oracles"], "generic_or_imported": ["identity_and_authority", "budget_precharge", "provider_qualification", "telemetry_transport", "persistence", "messaging", "workflow", "operations_research_algorithms"]},
        "bounded_context_boundary": {"inside": ["work-unit execution contract", "resource classes quantities demand offers and topology", "quota and admission", "placement and scheduler assurance", "reservation allocation lease fencing", "attempt worker executor cancellation retry checkpoint", "backpressure preemption autoscaling", "runtime usage energy and effect receipts"], "outside": ["business or analytical meaning", "workflow dependencies", "algorithm semantics", "provider commercial claims", "cost allocation and billing", "security policy", "vertical acceptance"]},
        "ubiquitous_language_policy": {"terms": {"WorkUnit": "immutable executable artifact entry point and completion contract", "ResourceDemand": "minimum target maximum and hard or soft constraints", "ResourceOffer": "validity-scoped allocatable capacity and topology", "Admission": "permission to enter controlled execution, not placement", "Placement": "constraint-satisfying assignment with assurance", "Reservation": "temporary hold", "Allocation": "committed assignment", "Lease": "time-bounded authority", "FencingToken": "stale-writer exclusion credential", "Attempt": "one execution incarnation", "RuntimeReceipt": "observed occurrence, never inferred completion"}, "homonym_rules": ["quota is not capacity", "budget is not quota", "admission is not placement", "reservation is not allocation", "lease is not fencing", "retry is not same attempt", "timeout is not terminal fact", "heartbeat is not progress"]},
        "context_map": [{"neighbor_ref": "product.solution_compiler", "relationship": "customer_supplier", "translation": "consume typed work and target plans"}, {"neighbor_ref": DEVELOPER, "relationship": "customer_supplier", "translation": "accept authorized instantiation effects and publish receipts"}, {"neighbor_ref": FINOPS, "relationship": "customer_supplier", "translation": "consume budget/precharge decisions and publish observed usage"}, {"neighbor_ref": "component.provider_qualification", "relationship": "customer_supplier", "translation": "consume target-scoped qualification receipts"}, {"neighbor_ref": "neighbor.identity_policy", "relationship": "conformist_with_acl", "translation": "import authority and tenant scope"}],
        "anti_corruption_layers": ["acl.work_intent", "acl.workflow_work_unit", "acl.resource_provider", "acl.budget_precharge", "acl.security_authority", "acl.runtime_backend", "acl.telemetry_transport", "acl.persistence_checkpoint"],
        "published_language": ["WorkUnitId", "AttemptId", "WorkerId", "ResourceClass", "ResourceQuantity", "ResourceDemand", "ResourceOffer", "QuotaDecision", "AdmissionDecision", "PlacementProblem", "PlacementResult", "SchedulerAssurance", "Reservation", "Allocation", "Lease", "FencingToken", "CancellationState", "CheckpointRef", "RuntimeReceipt", "UsageReceipt", "EnergyReceipt"],
        "value_objects": ["WorkUnitId", "JobId", "AttemptId", "WorkerId", "ExecutorId", "ResourceClass", "Unit", "Quantity", "TopologyConstraint", "OfferValidity", "QuotaRef", "Priority", "Deadline", "LeaseId", "FencingToken", "CheckpointDigest", "TargetProfileRef", "EvidenceRef"],
        "entities": ["WorkUnit", "ResourceOffer", "QuotaLedger", "AdmissionCase", "PlacementCase", "Reservation", "Allocation", "Lease", "Attempt", "Worker", "Executor", "Checkpoint", "RuntimeReceipt"],
        "aggregates": [{"root": "AdmissionCase", "members": ["demand", "offers", "quota", "budget_receipt", "compatibility", "decision"], "consistency": "hard constraints and higher-authority refusals precede policy scoring"}, {"root": "PlacementCase", "members": ["admitted_work", "candidates", "constraints", "scheduler_policy", "assurance", "result"], "consistency": "feasible optimal heuristic timeout unknown and infeasible stay distinct"}, {"root": "Allocation", "members": ["reservation_ref", "resource_assignments", "lease", "fencing", "release_state"], "consistency": "allocation and effect authority are committed atomically or refused"}, {"root": "Attempt", "members": ["work_unit_ref", "allocation_ref", "backend", "worker", "cancellation", "checkpoints", "observations", "terminal_outcome"], "consistency": "one attempt has one append-only lifecycle and retry always creates another identity"}],
        "aggregate_roots": ["AdmissionCase", "PlacementCase", "Allocation", "Attempt"],
        "aggregate_invariants": ["every resource quantity is dimension and unit aware", "demand offer compatibility is explicit", "all queues buffers retries attempts and horizons are finite or refused", "hard constraints are filtered before scoring", "quota budget capacity and entitlement never alias", "reservation allocation lease and fencing remain separate", "lease without enforcement at the protected effect is not fencing", "timeout cancellation request acknowledgement stopping and terminal outcome remain separate", "heartbeat proves observability not useful progress", "requested reserved allocated consumed rated and billed quantities remain distinct"],
        "commands": ["register_work_unit", "publish_resource_offer", "set_quota", "request_admission", "select_scheduler_policy", "solve_placement", "reserve_capacity", "commit_allocation", "issue_lease", "renew_lease", "preempt_allocation", "start_attempt", "request_cancellation", "acknowledge_cancellation", "record_checkpoint", "restore_checkpoint", "record_runtime_observation", "record_terminal_outcome", "account_usage", "account_energy", "release_allocation", "evaluate_runtime_conformance"],
        "domain_events": ["work_unit_registered", "resource_offer_published", "quota_set", "admission_requested", "work_admitted", "admission_refused", "scheduler_policy_selected", "placement_solved", "capacity_reserved", "allocation_committed", "lease_issued", "lease_renewed", "allocation_preempted", "attempt_started", "cancellation_requested", "cancellation_acknowledged", "checkpoint_recorded", "checkpoint_restored", "runtime_observation_recorded", "attempt_succeeded", "attempt_failed", "attempt_cancelled", "attempt_outcome_unknown", "usage_accounted", "energy_accounted", "allocation_released", "runtime_conformance_evaluated"],
        "refusal_failure_catalog": ["work_contract_invalid", "resource_class_unknown", "unit_unknown", "demand_unbounded", "offer_expired", "topology_incompatible", "authority_missing", "quota_exhausted", "budget_precharge_missing", "capacity_unknown", "hard_constraints_infeasible", "scheduler_unsupported", "placement_timeout_without_incumbent", "reservation_conflict", "allocation_conflict", "lease_expired", "stale_fencing_token", "backend_unqualified", "attempt_limit_exhausted", "checkpoint_incompatible", "cancellation_unknown", "provider_outcome_unknown", "receipt_incomplete", "accounting_attribution_unknown"],
        "domain_services": ["ResourceCompatibilityService", "AdmissionService", "PlacementService", "SchedulerPolicyService", "ReservationAllocationService", "LeaseFencingService", "AttemptControlService", "CheckpointService", "BackpressureService", "AutoscalingService", "RuntimeAccountingService", "RuntimeConformanceService"],
        "application_services": ["SubmitWorkUseCase", "ExplainAdmissionUseCase", "PlaceWorkUseCase", "ExecuteAttemptUseCase", "CancelWorkUseCase", "RecoverAttemptUseCase", "ScaleResourcePoolUseCase", "InspectRuntimeReceiptsUseCase", "ReleaseResourcesUseCase"],
        "repositories": ["ResourceOfferRepository", "QuotaLedgerRepository", "AdmissionCaseRepository", "PlacementCaseRepository", "ReservationRepository", "AllocationRepository", "AttemptRepository", "CheckpointRepository", "RuntimeReceiptRepository"],
        "factories": ["WorkUnitFactory", "ResourceDemandFactory", "ResourceOfferFactory", "AdmissionCaseFactory", "PlacementProblemFactory", "ReservationFactory", "AllocationFactory", "AttemptFactory", "RuntimeReceiptFactory"],
        "specifications": ["FiniteDemandSpecification", "DemandOfferCompatibilitySpecification", "QuotaAvailabilitySpecification", "AdmissionPreconditionSpecification", "HardConstraintIntegritySpecification", "PlacementFeasibilitySpecification", "SchedulerAssuranceSpecification", "ReservationValiditySpecification", "FencingEnforcementSpecification", "AttemptTransitionSpecification", "CancellationSafetySpecification", "CheckpointCompatibilitySpecification", "ReceiptCompletenessSpecification"],
        "state_machine": {"AdmissionCase": ["requested", "checking_authority", "checking_quota", "checking_budget", "checking_compatibility", "admitted", "refused", "unknown", "expired"], "Allocation": ["proposed", "reserved", "committed", "leased", "preempting", "releasing", "released", "expired", "conflicted"], "Attempt": ["created", "starting", "running", "checkpointing", "cancellation_requested", "stopping", "succeeded", "failed", "cancelled", "lost", "unknown"], "law": "terminal facts are append-only and provider timeouts remain unknown until reconciled"},
        "policies_and_reactions": ["when offer validity expires invalidate dependent admissions and placements", "when quota or budget changes re-evaluate only uncommitted work", "when a lease expires fence protected effects before reuse", "when cancellation is requested propagate it without inventing completion", "when retry is allowed create a new attempt identity", "when backpressure crosses a bound shed delay or refuse according to declared policy", "when receipts arrive reconcile usage without editing history"],
        "sagas_and_process_managers": ["AdmissionPlacementProcess", "ReservationAllocationProcess", "LeaseRenewalProcess", "AttemptExecutionProcess", "CancellationReconciliationProcess", "CheckpointRecoveryProcess", "PreemptionProcess", "AutoscalingProcess", "ResourceReleaseProcess"],
        "read_models_and_projections": ["ResourceInventoryView", "DemandOfferCompatibilityView", "AdmissionQueueView", "PlacementDecisionView", "ReservationAllocationLedgerView", "LeaseAndFenceView", "AttemptTimelineView", "CheckpointInventoryView", "RuntimeUsageView", "EnergyAttributionView", "CapacityAndSaturationView"],
        "integration_event_policy": "Only editioned work, demand, offer, admission, placement, reservation, allocation, lease, attempt, checkpoint, accounting and receipt contracts cross the boundary; provider DTOs and scheduler internal state do not.",
        "concurrency_and_idempotency": ["admission binds immutable demand offer quota budget and policy editions", "reservation and allocation use compare-and-swap editions", "leases use monotonic fencing tokens", "attempt start is idempotent per attempt identity and target", "retry receives a new attempt identity", "unknown effect completion is reconciled before replay", "accounting deduplicates occurrence identities"],
        "time_model": ["demand validity offer validity quota validity and budget validity are independent", "queue time scheduling time reservation time execution time and observation time remain distinct", "deadlines use explicit clocks", "lease expiry and fencing enforcement time differ", "runtime and accounting receipts carry occurrence recording and correction time", "historical outcomes retain original policy editions"],
        "event_storming_swimlanes": ["workload_owner", "solution_compiler", "authority_service", "finops_precharge", "admission_controller", "scheduler", "allocator", "runtime_backend", "worker_executor", "checkpoint_store", "accounting_sink", "runtime_operator"],
        "nonfunctional_laws": ["finite resource work queue retry and output budgets", "deterministic decisions for frozen snapshots and deterministic policies", "declared assurance for optimal bounded heuristic probabilistic timeout unknown and infeasible results", "cooperative cancellation and explicit ambiguity", "no provider names in owned semantic types", "target and backend isolation behind versioned ports", "fault and race evidence for fencing and cancellation", "optional model or agent removal preserves all admission placement allocation execution and accounting laws"],
    }
    assert set(ddd) == DDD_FIELDS
    return {"dossier_id": "ddd.platform.runtime_resource_control", "record_kind": "product_ddd_dossier", "edition": 1, "product_ref": RUNTIME, "status": "candidate_not_ratified", "product_truth": truth, "strategic_and_tactical_ddd": ddd}


def _finops_dossier() -> dict[str, Any]:
    truth = {
        "sovereign_question": "What usage and cost occurred, how is it normalized and attributed, which explicit policy allocates shared idle and overhead cost, what finite spend authority remains, and what reconciled unit economics may be shown without claiming invoice or accounting truth?",
        "users": ["finops_practitioner", "engineering_owner", "product_owner", "finance_analyst", "budget_owner", "platform_operator"],
        "harmed_parties": ["cost_center_owner", "tenant", "customer", "service_team", "finance_ledger_owner", "data_subject"],
        "jobs": ["ingest and deduplicate usage and cost occurrences", "normalize exact source editions with residuals", "attribute costs to governed scopes", "allocate shared idle and overhead cost", "reconcile totals and corrections", "precharge and reconcile budgets", "compute governed unit costs and showback views"],
        "measurable_outcomes": ["cost_coverage", "unallocated_and_unattributed_cost", "allocation_reconciliation_residual", "normalization_loss_rate", "correction_latency", "budget_overrun_and_precharge_accuracy", "unit_cost_denominator_coverage"],
        "negative_mission": "Does not own runtime usage occurrence truth, provider invoices, general ledger postings, payment, tax, commercial pricing, resource capacity, entitlement, business value, or automatic cost optimization authority.",
    }
    ddd = {
        "domain_vision_statement": "Own evidence-preserving usage and cost normalization, attribution, allocation, budget control, reconciliation, and unit economics without promoting them to billing or accounting truth.",
        "subdomain_classification": {"core": ["meter_contract", "cost_normalization_with_residuals", "cost_attribution", "allocation_policy_and_reconciliation", "budget_precharge", "unit_cost_semantics"], "supporting": ["showback_projections", "correction_workflow", "allocation_explanation", "anomaly_input_contracts"], "generic_or_imported": ["money_and_quantity", "identity_and_tenant_scope", "runtime_usage_receipts", "provider_cost_exports", "billing_invoice_and_ledger", "forecasting", "optimization"]},
        "bounded_context_boundary": {"inside": ["usage events and meter definitions", "cost occurrences and normalization residuals", "attribution evidence", "allocation rules bases and outputs", "reconciliation and corrections", "budget reservation and spend reconciliation", "unit-cost definitions and projections"], "outside": ["resource execution", "provider invoice authority", "contract pricing", "general ledger and payment", "tax", "business value judgment", "autonomous remediation"]},
        "ubiquitous_language_policy": {"terms": {"UsageEvent": "one observed metered occurrence", "UsageAggregate": "windowed result under one meter edition", "CostOccurrence": "source-scoped cost record, not invoice line", "NormalizedCost": "mapped cost under an exact schema edition plus residuals", "Attribution": "evidence-backed association to governed scopes", "AllocationRule": "versioned policy for distributing cost", "AllocatedCost": "allocation output, not charge", "Precharge": "finite provisional spend authority", "UnitCost": "cost divided by an exact governed useful-output denominator"}, "homonym_rules": ["usage is not cost", "cost is not price or charge", "normalized is not allocated", "showback is not chargeback posting", "budget is not capacity", "forecast is not actual"]},
        "context_map": [{"neighbor_ref": RUNTIME, "relationship": "customer_supplier", "translation": "consume observed usage and energy receipts"}, {"neighbor_ref": "neighbor.billing_finance", "relationship": "anti_corruption_layer", "translation": "import provider cost and export approved finance-facing projections without claiming ledger authority"}, {"neighbor_ref": "neighbor.identity_policy", "relationship": "conformist_with_acl", "translation": "import tenant account organization workspace and authority scope"}, {"neighbor_ref": "product.forecasting", "relationship": "customer_supplier", "translation": "publish governed historical series and consume forecast distributions as advisory inputs"}, {"neighbor_ref": "product.optimization", "relationship": "customer_supplier", "translation": "publish decision problems and consume non-authoritative recommendations"}],
        "anti_corruption_layers": ["acl.runtime_usage", "acl.provider_billing_export", "acl.focus_edition", "acl.identity_and_scope", "acl.finance_ledger", "acl.currency_rates", "acl.analytics_recommendation"],
        "published_language": ["UsageEventId", "MeterDefinitionEdition", "UsageAggregate", "CostOccurrenceId", "NormalizationProfile", "NormalizedCost", "NormalizationResidual", "AttributionAssertion", "AllocationPolicyEdition", "AllocationBasis", "AllocatedCost", "ReconciliationResult", "Budget", "Precharge", "BudgetReceipt", "UnitCostDefinition", "UnitCostObservation"],
        "value_objects": ["UsageEventId", "MeterId", "Measure", "Window", "CostOccurrenceId", "Money", "Currency", "ProviderInvoiceRef", "TenantRef", "AccountRef", "WorkspaceRef", "CostCenterRef", "AllocationRuleId", "AllocationBasis", "BudgetId", "PrechargeId", "DenominatorRef", "EvidenceRef"],
        "entities": ["MeterDefinition", "UsageOccurrence", "CostOccurrence", "NormalizationRun", "AttributionCase", "AllocationPolicy", "AllocationRun", "Budget", "Precharge", "UnitCostDefinition"],
        "aggregates": [{"root": "MeterDefinition", "members": ["subject", "measure", "aggregation", "window", "dedup", "correction_policy", "edition"], "consistency": "one aggregate is reproducible from occurrence identities and one immutable meter edition"}, {"root": "AllocationRun", "members": ["source_costs", "attributions", "policy_edition", "bases", "outputs", "residuals", "reconciliation"], "consistency": "allocated plus declared residual exactly reconciles to eligible input under one currency and time policy"}, {"root": "Budget", "members": ["scope", "period", "limit", "reservations", "actuals", "corrections", "remaining"], "consistency": "precharge and final actual are separately recorded and never double-spend authority"}],
        "aggregate_roots": ["MeterDefinition", "AllocationRun", "Budget"],
        "aggregate_invariants": ["occurrence aggregate rated usage normalized cost allocated cost charge invoice and payment remain distinct", "all quantities money currencies scopes and time windows are explicit", "normalization retains source identity edition and every unmapped residual", "attribution is evidence not identity", "allocation policy explicitly treats shared idle overhead credits and unknown cost", "allocation reconciles or reports a typed residual", "precharge is neither final cost nor physical capacity", "unit cost requires governed numerator denominator period scope and uncertainty", "corrections append and restate rather than erase history"],
        "commands": ["define_meter", "record_usage_event", "correct_usage_event", "register_cost_occurrence", "normalize_cost", "assert_cost_attribution", "publish_allocation_policy", "run_allocation", "reconcile_allocation", "open_budget", "reserve_precharge", "release_precharge", "record_actual_spend", "correct_cost", "define_unit_cost", "compute_unit_cost", "publish_showback_projection"],
        "domain_events": ["meter_defined", "usage_event_recorded", "usage_event_corrected", "cost_occurrence_registered", "cost_normalized", "normalization_residual_recorded", "cost_attribution_asserted", "allocation_policy_published", "allocation_run_completed", "allocation_reconciled", "budget_opened", "precharge_reserved", "precharge_released", "actual_spend_recorded", "cost_corrected", "unit_cost_defined", "unit_cost_computed", "showback_projection_published"],
        "refusal_failure_catalog": ["usage_event_duplicate", "meter_edition_unknown", "window_unbounded", "cost_source_unsupported", "currency_unknown", "normalization_profile_missing", "semantic_loss_unknown", "attribution_scope_unknown", "allocation_basis_missing", "allocation_policy_ambiguous", "shared_cost_policy_missing", "unreconciled_total", "correction_conflict", "budget_scope_mismatch", "insufficient_budget", "stale_precharge", "denominator_missing_or_zero", "finance_authority_missing"],
        "domain_services": ["MeterAggregationService", "CostNormalizationService", "CostAttributionService", "AllocationService", "AllocationReconciliationService", "BudgetPrechargeService", "UnitCostService", "CorrectionService"],
        "application_services": ["IngestUsageUseCase", "NormalizeCostUseCase", "AllocateCostUseCase", "ExplainAllocationUseCase", "ReserveBudgetUseCase", "ReconcileSpendUseCase", "ComputeUnitEconomicsUseCase", "PublishShowbackUseCase"],
        "repositories": ["MeterDefinitionRepository", "UsageOccurrenceRepository", "CostOccurrenceRepository", "NormalizationRunRepository", "AttributionCaseRepository", "AllocationPolicyRepository", "AllocationRunRepository", "BudgetRepository", "UnitCostDefinitionRepository"],
        "factories": ["MeterDefinitionFactory", "UsageEventFactory", "CostOccurrenceFactory", "NormalizationRunFactory", "AttributionAssertionFactory", "AllocationPolicyFactory", "AllocationRunFactory", "BudgetFactory", "UnitCostDefinitionFactory"],
        "specifications": ["MeterDefinitionClosureSpecification", "UsageDeduplicationSpecification", "NormalizationEditionSpecification", "ResidualPreservationSpecification", "AttributionEvidenceSpecification", "AllocationPolicyClosureSpecification", "AllocationReconciliationSpecification", "PrechargeAvailabilitySpecification", "CorrectionLegalitySpecification", "UnitCostDenominatorSpecification"],
        "state_machine": {"CostOccurrence": ["recorded", "normalization_pending", "normalized", "partially_normalized", "attribution_pending", "attributed", "allocation_pending", "allocated", "corrected", "superseded", "refused"], "AllocationRun": ["draft", "inputs_frozen", "running", "reconciliation_pending", "reconciled", "residual", "failed", "invalidated"], "Precharge": ["requested", "reserved", "partially_consumed", "reconciled", "released", "expired", "refused"], "law": "corrections and restatements create new editions and never rewrite prior finance-facing evidence"},
        "policies_and_reactions": ["when late usage arrives apply the declared correction policy", "when provider schema edition changes invalidate affected normalization profiles", "when attribution evidence expires route cost to an explicit unknown bucket", "when allocation fails reconciliation publish no balanced claim", "when precharge expires release unused authority", "when actual spend arrives reconcile but retain provisional history", "when an analytic recommendation arrives require human or policy authority before any effect"],
        "sagas_and_process_managers": ["UsageToCostProcess", "NormalizationAndAttributionProcess", "AllocationAndReconciliationProcess", "BudgetPrechargeProcess", "LateCorrectionProcess", "ShowbackPublicationProcess"],
        "read_models_and_projections": ["UsageByScopeView", "CostCoverageView", "NormalizationResidualView", "AttributionConfidenceView", "SharedIdleOverheadView", "AllocationExplanationView", "BudgetBurnView", "UnitEconomicsView", "ShowbackView", "CorrectionAndRestatementView"],
        "integration_event_policy": "Only editioned usage, normalized cost, attribution, allocation, reconciliation, budget and unit-cost contracts cross the boundary; raw provider DTOs, secrets, invoices, ledger entries and unapproved recommendations remain external.",
        "concurrency_and_idempotency": ["usage deduplication scopes source subject occurrence and meter edition", "normalization binds source and profile digests", "allocation freezes eligible inputs and policy edition", "budget reservations use optimistic edition and idempotency key", "corrections reference the exact superseded occurrence", "unknown external publication is reconciled before retry"],
        "time_model": ["usage occurrence recording and correction times differ", "provider billing period service period and ingestion period remain distinct", "allocation policy validity is bitemporal", "budget period differs from invoice and accounting period", "currency conversion carries source instant and rate edition", "historical showback retains original inputs and later restatements"],
        "event_storming_swimlanes": ["runtime_accounting", "provider_cost_source", "finops_practitioner", "engineering_owner", "budget_owner", "finance_analyst", "identity_scope_authority", "allocation_engine", "showback_consumer"],
        "nonfunctional_laws": ["deterministic aggregation normalization and allocation for frozen inputs", "exact decimal money and unit arithmetic", "finite event window correction and allocation budgets", "complete residual and reconciliation evidence", "tenant and purpose isolation", "provider schema isolation behind versioned ACLs", "no automatic charge invoice or ledger effect", "optional model or agent removal preserves metering normalization allocation reconciliation budget and unit-cost behavior"],
    }
    assert set(ddd) == DDD_FIELDS
    return {"dossier_id": "ddd.platform.finops_allocation", "record_kind": "product_ddd_dossier", "edition": 1, "product_ref": FINOPS, "status": "candidate_not_ratified", "product_truth": truth, "strategic_and_tactical_ddd": ddd}


def enrich_platform_products(source: dict[str, Any]) -> dict[str, Any]:
    """Apply the three product models and preserve all qualification gaps."""

    product_truth = {
        DEVELOPER: _developer_dossier()["product_truth"],
        RUNTIME: _runtime_dossier()["product_truth"],
        FINOPS: _finops_dossier()["product_truth"],
    }
    for row in source["artifacts"]:
        if row.get("artifact_id") in PRODUCTS:
            truth = product_truth[row["artifact_id"]]
            row.update({
                "sovereign_question": truth["sovereign_question"],
                "users": truth["users"],
                "harmed_parties": truth["harmed_parties"],
                "jobs": truth["jobs"],
                "outcomes": truth["measurable_outcomes"],
                "negative_mission": truth["negative_mission"],
                "automation_modality": AUTOMATION,
            })

    additions = [
        artifact("capability.plan_paved_path", "capability", "Plan paved path", "semantic.paved_path", "Derive a pure edition-bound instantiation plan with every decision, requirement and escape hatch exposed.", ["evidence.backstage.templates", "evidence.crossplane.composition"]),
        artifact("capability.publish_resource_offer", "capability", "Publish resource offer", "semantic.resource_offer", "Publish a validity-scoped allocatable capacity and topology contract.", ["evidence.kubernetes.dra"]),
        artifact("capability.evaluate_demand_offer_compatibility", "capability", "Evaluate resource compatibility", "semantic.resource_admission", "Evaluate dimension, topology, target and hard-constraint compatibility before admission.", ["evidence.kubernetes.resources", "evidence.kubernetes.dra"]),
        artifact("capability.manage_quota", "capability", "Manage quota ledger", "semantic.resource_admission", "Reserve and release explicit technical consumption authority without claiming capacity.", ["evidence.kubernetes.quota"]),
        artifact("capability.select_scheduler_policy", "capability", "Select scheduler policy", "semantic.placement", "Bind an explicit scheduler policy and assurance vocabulary to a placement problem.", ["evidence.kubernetes.scheduling", "evidence.paper.drf"]),
        artifact("capability.reserve_capacity", "capability", "Reserve capacity", "semantic.reservation_allocation", "Create an expiring capacity hold distinct from committed assignment.", ["evidence.kubernetes.dra"]),
        artifact("capability.commit_allocation", "capability", "Commit allocation", "semantic.reservation_allocation", "Commit resource assignments and preserve their release lifecycle.", ["evidence.kubernetes.dra"]),
        artifact("capability.manage_lease_fencing", "capability", "Manage lease and fencing", "semantic.lease_fencing", "Issue time-bounded authority and enforce monotonic stale-writer exclusion.", ["evidence.kubernetes.controllers"]),
        artifact("capability.control_preemption", "capability", "Control preemption", "semantic.resource_admission", "Select and execute an explicit victim and compensation policy.", ["evidence.kubernetes.scheduling"]),
        artifact("capability.control_autoscaling", "capability", "Control autoscaling", "semantic.resource_admission", "Produce bounded scale intents from declared signals and constraints.", ["evidence.kubernetes.resources"]),
        artifact("capability.apply_backpressure", "capability", "Apply backpressure", "semantic.runtime_attempt", "Propagate bounded demand, shed, delay or refuse according to a declared policy.", ["evidence.cncf.operational_excellence"]),
        artifact("capability.control_deadline_cancellation", "capability", "Control deadlines and cancellation", "semantic.runtime_attempt", "Keep deadline, cancellation request, acknowledgement, stopping and terminal fact distinct.", ["evidence.oci.runtime"]),
        artifact("capability.manage_checkpoint", "capability", "Manage checkpoints", "semantic.runtime_attempt", "Record and restore exact artifact state and target compatibility evidence.", ["evidence.oci.runtime"]),
        artifact("capability.bind_runtime_backend", "capability", "Bind runtime backend", "semantic.runtime_attempt", "Bind a qualified process async actor device container WebAssembly or provider runtime port.", ["evidence.oci.runtime", "evidence.wasi.p2"]),
        artifact("capability.account_runtime_usage", "capability", "Account runtime usage", "semantic.runtime_receipt", "Derive occurrence-scoped usage receipts without promoting them to cost or invoice.", ["evidence.opentelemetry.semconv", "evidence.opencost.spec"]),
        artifact("capability.account_energy", "capability", "Account runtime energy", "semantic.runtime_receipt", "Record measured or modeled energy attribution with method and uncertainty.", ["evidence.opencost.spec"]),
        artifact("capability.evaluate_runtime_conformance", "capability", "Evaluate runtime conformance", "semantic.runtime_receipt", "Apply exact target and profile oracles to runtime artifacts and receipts.", ["evidence.kubernetes.conformance", "evidence.oci.runtime"]),
        artifact("capability.register_cost_occurrence", "capability", "Register cost occurrence", "semantic.cost_normalization", "Register source, subject, period, currency, edition and evidence before normalization.", ["evidence.focus12"]),
        artifact("capability.attribute_cost", "capability", "Attribute cost", "semantic.cost_allocation", "Associate eligible cost with governed tenant account organization workspace service and cost-center scopes.", ["evidence.focus12", "evidence.finops.framework"]),
        artifact("capability.reconcile_cost_allocation", "capability", "Reconcile cost allocation", "semantic.cost_allocation", "Prove allocated plus residual cost equals eligible input under one policy edition.", ["evidence.opencost.spec", "evidence.finops.framework"]),
        artifact("capability.compute_unit_cost", "capability", "Compute unit cost", "semantic.unit_cost", "Compute cost per governed useful-output denominator with exact scope time and uncertainty.", ["evidence.finops.framework"]),
    ]
    known_artifacts = {row["artifact_id"] for row in source["artifacts"]}
    source["artifacts"].extend(row for row in additions if row["artifact_id"] not in known_artifacts)

    # Remove the earlier collapsed allocation/lease facade and repair the original facades.
    source["libraries"] = [row for row in source["libraries"] if row["library_id"] != "library.platform.allocation_lease"]
    by_library = {row["library_id"]: row for row in source["libraries"]}
    by_library["library.platform.blueprint"]["product_refs"] = [DEVELOPER]
    by_library["library.platform.paved_path_runtime"].update({
        "types": ["InstantiationEffectIntent", "PlatformInstance", "ReconciliationReceipt", "ExitManifestRef"],
        "operations": ["submit_instantiation_effects", "reconcile_instance", "supersede_instance", "decommission_instance"],
        "decisions": ["provider_binding", "rollback_policy", "reconciliation_policy", "exit_policy"],
        "dependencies": ["library.platform.developer.paved_path_plan", "library.platform.release_evidence"],
        "product_refs": [DEVELOPER],
    })
    by_library["library.platform.resource_vector"].update({
        "types": ["ResourceClass", "ResourceQuantity", "ResourceDemand", "DemandConstraint"],
        "operations": ["normalize_quantity", "validate_finite_demand", "compare_demand_vectors"],
        "decisions": ["unit_profile", "hardness", "unknown_dimension_policy"],
        "product_refs": [RUNTIME],
    })
    by_library["library.platform.admission"].update({
        "types": ["AdmissionRequest", "CompatibilityDecisionRef", "QuotaDecisionRef", "BudgetDecisionRef", "AdmissionDecision"],
        "operations": ["admit"],
        "decisions": ["authority_precedence", "quota_policy", "compatibility_policy", "unknown_capacity_policy"],
        "dependencies": ["library.platform.runtime.demand_offer_compatibility", "library.platform.runtime.quota_ledger", "library.platform.budget_precharge"],
        "product_refs": [RUNTIME],
    })
    by_library["library.platform.placement"].update({
        "dependencies": ["library.platform.admission", "library.platform.runtime.scheduler_policy"],
        "product_refs": [RUNTIME],
    })
    by_library["library.platform.runtime_attempt"].update({
        "types": ["WorkUnitRef", "Attempt", "Worker", "Executor", "AttemptOutcome"],
        "operations": ["start_attempt", "record_observation", "record_terminal_outcome"],
        "decisions": ["target_profile", "retry_policy", "unknown_outcome_policy"],
        "provides": ["capability.execute_attempt"],
        "dependencies": ["library.platform.runtime.backend_spi", "library.platform.runtime.lease_fencing", "library.platform.runtime.deadline_cancellation", "library.platform.runtime.checkpoint_contract"],
        "product_refs": [RUNTIME],
    })
    for ident in ["library.platform.meter", "library.platform.cost_normalization", "library.platform.cost_allocation", "library.platform.budget_precharge"]:
        by_library[ident]["product_refs"] = [FINOPS]

    source["libraries"].extend([
        library("library.platform.developer.paved_path_plan", DEVELOPER, "semantic.paved_path", ["capability.plan_paved_path"], ["PavedPathContract", "InstantiationRequest", "InstantiationPlan", "EscapeHatch"], ["validate_request", "derive_instantiation_plan", "explain_decisions"], ["default_policy", "escape_hatch_policy", "provider_requirement_policy"], ["plan_is_not_effect", "every_decision_is_exposed", "unsupported_deviation_is_refused"], ["blueprint_incompatible", "decision_unbound", "escape_hatch_unsupported"], ["library.platform.blueprint", "library.platform.intent_contract"], "pure_no_io", ["evidence.backstage.templates", "evidence.crossplane.composition"]),
        library("library.platform.developer.platform_conformance", DEVELOPER, "semantic.platform_conformance", ["capability.evaluate_platform_conformance"], ["PlatformConformanceProfile", "PlatformInstanceSnapshot", "CheckResult", "Counterexample", "PlatformConformanceResult"], ["derive_checks", "evaluate_snapshot", "retain_counterexample", "invalidate_result"], ["evidence_ladder", "independence_policy", "waiver_policy", "expiry_policy"], ["schema_valid_is_not_conformant", "result_is_exact_scope_only", "waiver_is_not_pass"], ["profile_incomplete", "subject_mismatch", "evidence_stale", "counterexample_unresolved"], ["library.platform.paved_path_runtime", "library.platform.compiler.conformance_coordination"], "pure_effect_intents", ["evidence.kubernetes.conformance", "evidence.slsa12"], "assurance_boundary"),
        library("library.platform.runtime.work_contract", RUNTIME, "semantic.work_unit", ["capability.execute_attempt"], ["WorkUnitId", "ExecutableArtifactRef", "EntryPoint", "AttemptPolicy", "CompletionContract"], ["validate_work_contract", "canonicalize_work_contract"], ["attempt_limit", "completion_policy", "effect_profile"], ["work_identity_is_not_attempt_identity", "artifact_entrypoint_and_completion_are_explicit"], ["artifact_missing", "entrypoint_unsupported", "attempt_policy_unbounded"], [], "pure_no_io", ["evidence.oci.runtime", "evidence.wasi.p2"]),
        library("library.platform.runtime.resource_offer", RUNTIME, "semantic.resource_offer", ["capability.publish_resource_offer"], ["ResourceOfferId", "ResourcePoolRef", "CapacityVector", "Topology", "ValidityWindow", "TargetProfileRef"], ["validate_offer", "publish_offer_snapshot", "expire_offer"], ["health_policy", "overcommit_policy", "staleness_policy"], ["offer_is_not_resource_or_allocation", "expired_offer_cannot_admit"], ["capacity_unbounded", "topology_unknown", "offer_expired"], ["library.platform.resource_vector"], "pure_effect_intents", ["evidence.kubernetes.dra", "evidence.kubernetes.resources"]),
        library("library.platform.runtime.demand_offer_compatibility", RUNTIME, "semantic.resource_admission", ["capability.evaluate_demand_offer_compatibility"], ["DemandOfferPair", "CompatibilityPredicate", "CompatibilityDecision", "CompatibilityResidual"], ["evaluate_dimensions", "evaluate_topology", "evaluate_target", "explain_incompatibility"], ["substitution_policy", "unknown_dimension_policy", "soft_constraint_policy"], ["hard_constraints_never_weaken", "unknown_is_not_compatible"], ["dimension_incomparable", "topology_incompatible", "target_unsupported"], ["library.platform.resource_vector", "library.platform.runtime.resource_offer"], "pure_no_io", ["evidence.kubernetes.dra", "evidence.kubernetes.resources"]),
        library("library.platform.runtime.quota_ledger", RUNTIME, "semantic.resource_admission", ["capability.manage_quota"], ["QuotaId", "QuotaScope", "QuotaLimit", "QuotaReservation", "QuotaDecision"], ["check_quota", "reserve_quota", "release_quota", "reconcile_quota"], ["hierarchy_policy", "borrowing_policy", "expiry_policy"], ["quota_is_not_capacity_or_budget", "reserved_quota_cannot_double_spend"], ["quota_exhausted", "scope_mismatch", "stale_reservation"], ["library.platform.resource_vector"], "pure_effect_intents", ["evidence.kubernetes.quota"]),
        library("library.platform.runtime.scheduler_policy", RUNTIME, "semantic.placement", ["capability.select_scheduler_policy"], ["SchedulerPolicyRef", "PlacementObjective", "SchedulerGuarantee", "SchedulerResult"], ["bind_policy", "validate_policy_support", "classify_assurance"], ["fifo_drf_binpack_min_cost_flow_gang_policy", "tie_break_policy", "time_budget"], ["policy_name_is_not_guarantee", "timeout_with_incumbent_is_not_optimal"], ["policy_unsupported", "objective_incompatible", "assurance_unknown"], ["library.platform.runtime.demand_offer_compatibility"], "pure_no_io", ["evidence.kubernetes.scheduling", "evidence.paper.drf"]),
        library("library.platform.runtime.reservation_ledger", RUNTIME, "semantic.reservation_allocation", ["capability.reserve_capacity"], ["ReservationId", "CapacityHold", "ReservationExpiry", "ReservationReceipt"], ["reserve", "renew_reservation", "release_reservation"], ["hold_duration", "oversubscription_policy", "conflict_policy"], ["reservation_is_not_allocation", "expired_hold_cannot_commit"], ["capacity_changed", "reservation_conflict", "reservation_expired"], ["library.platform.placement"], "pure_effect_intents", ["evidence.kubernetes.dra"]),
        library("library.platform.runtime.allocation_ledger", RUNTIME, "semantic.reservation_allocation", ["capability.reserve_allocate", "capability.commit_allocation"], ["AllocationId", "ResourceAssignment", "AllocationEdition", "AllocationReceipt"], ["commit_allocation", "amend_allocation", "release_allocation"], ["commit_policy", "partial_allocation_policy", "release_policy"], ["allocation_is_not_reservation_or_usage", "assignment_conflict_is_refused"], ["reservation_missing", "allocation_conflict", "partial_commit_unsupported"], ["library.platform.runtime.reservation_ledger"], "pure_effect_intents", ["evidence.kubernetes.dra"]),
        library("library.platform.runtime.lease_fencing", RUNTIME, "semantic.lease_fencing", ["capability.manage_lease_fencing"], ["LeaseId", "LeaseTerm", "FencingToken", "ProtectedEffectRef"], ["issue_lease", "renew_lease", "revoke_lease", "validate_fence"], ["lease_duration", "renewal_policy", "fence_scope"], ["lease_is_not_fencing", "fencing_token_is_monotonic", "stale_writer_is_refused_at_effect"], ["lease_expired", "stale_fencing_token", "effect_not_fenced"], ["library.platform.runtime.allocation_ledger"], "pure_effect_intents", ["evidence.kubernetes.controllers"]),
        library("library.platform.runtime.preemption_control", RUNTIME, "semantic.resource_admission", ["capability.control_preemption"], ["PreemptionRequest", "VictimSet", "CompensationPlan", "PreemptionReceipt"], ["select_victims", "plan_compensation", "issue_preemption_intents"], ["priority_policy", "fairness_policy", "disruption_budget"], ["preemption_is_not_cancellation_completion", "victims_and_consequences_are_attributable"], ["victim_policy_unsatisfied", "disruption_budget_exhausted", "compensation_unknown"], ["library.platform.runtime.lease_fencing"], "pure_effect_intents", ["evidence.kubernetes.scheduling"]),
        library("library.platform.runtime.autoscaling_control", RUNTIME, "semantic.resource_admission", ["capability.control_autoscaling"], ["ScalingSignal", "ScalingPolicy", "ScaleIntent", "ScaleReceipt"], ["evaluate_scale_policy", "bound_scale_intent", "reconcile_scale"], ["signal_policy", "stabilization_window", "min_max_capacity", "cooldown"], ["signal_is_not_demand_truth", "scale_intent_is_not_capacity"], ["signal_stale", "capacity_bound_invalid", "scale_outcome_unknown"], ["library.platform.runtime.usage_accounting", "library.platform.runtime.resource_offer"], "pure_effect_intents", ["evidence.kubernetes.resources"]),
        library("library.platform.runtime.backpressure_control", RUNTIME, "semantic.runtime_attempt", ["capability.apply_backpressure"], ["DemandSignal", "CapacitySignal", "BackpressurePolicy", "FlowDecision"], ["request_capacity", "grant_capacity", "shed_delay_or_refuse"], ["buffer_bound", "overflow_policy", "fairness_policy"], ["every_buffer_and_demand_is_bounded", "silent_drop_is_forbidden"], ["unbounded_demand", "buffer_exhausted", "policy_unsupported"], [], "pure_effect_intents", ["evidence.cncf.operational_excellence"]),
        library("library.platform.runtime.deadline_cancellation", RUNTIME, "semantic.runtime_attempt", ["capability.control_deadline_cancellation"], ["Deadline", "CancellationRequest", "CancellationAcknowledgement", "StoppingState"], ["evaluate_deadline", "request_cancel", "acknowledge_cancel", "reconcile_stop"], ["clock_policy", "propagation_policy", "force_stop_policy"], ["timeout_is_not_terminal_fact", "request_acknowledgement_stopping_and_terminal_are_distinct"], ["deadline_clock_unknown", "cancellation_unsupported", "completion_unknown"], ["library.platform.runtime.work_contract"], "pure_effect_intents", ["evidence.oci.runtime"]),
        library("library.platform.runtime.checkpoint_contract", RUNTIME, "semantic.runtime_attempt", ["capability.manage_checkpoint"], ["CheckpointId", "CheckpointManifest", "ArtifactDigest", "CompatibilityProfile", "RestoreReceipt"], ["plan_checkpoint", "record_checkpoint", "validate_restore", "restore"], ["consistency_policy", "portability_profile", "retention_policy"], ["checkpoint_is_not_success", "restore_requires_exact_compatibility"], ["checkpoint_incomplete", "artifact_mismatch", "target_incompatible"], ["library.platform.runtime.work_contract"], "pure_effect_intents", ["evidence.oci.runtime"]),
        library("library.platform.runtime.backend_spi", RUNTIME, "semantic.runtime_attempt", ["capability.bind_runtime_backend"], ["RuntimeBackendRequirement", "BackendOffer", "BackendBinding", "BackendEffectIntent", "BackendReceipt"], ["enumerate_backends", "bind_backend", "submit_effect", "reconcile_effect"], ["process_async_actor_device_container_wasm_provider_profile", "thread_safety", "cancellation_safety"], ["provider_dto_never_leaks", "binding_is_not_qualification", "unknown_completion_is_preserved"], ["backend_unqualified", "target_unsupported", "effect_authority_missing", "provider_unknown"], ["library.platform.runtime.work_contract"], "effectful_runtime", ["evidence.oci.runtime", "evidence.wasi.p2"], "backend_spi"),
        library("library.platform.runtime.receipt_contract", RUNTIME, "semantic.runtime_receipt", ["capability.record_runtime_receipt"], ["RuntimeReceiptId", "AttemptRef", "TargetOccurrenceRef", "EffectOutcome", "ObservationSet"], ["validate_receipt", "canonicalize_receipt", "reconcile_receipts"], ["receipt_edition", "unknown_outcome_policy", "correlation_policy"], ["observation_is_not_inferred_fact", "receipt_scope_and_source_are_retained"], ["receipt_subject_mismatch", "outcome_conflict", "evidence_incomplete"], ["library.platform.runtime_attempt"], "pure_effect_intents", ["evidence.opentelemetry.semconv", "evidence.in_toto"]),
        library("library.platform.runtime.usage_accounting", RUNTIME, "semantic.runtime_receipt", ["capability.account_runtime_usage"], ["UsageOccurrence", "ResourceConsumption", "AttributionMethod", "UsageReceipt"], ["derive_usage", "attribute_usage", "correct_usage"], ["sampling_policy", "attribution_policy", "correction_policy"], ["observed_usage_is_not_requested_or_billed", "modeled_usage_declares_method_and_uncertainty"], ["measurement_missing", "attribution_unknown", "correction_conflict"], ["library.platform.runtime.receipt_contract"], "pure_effect_intents", ["evidence.opencost.spec", "evidence.focus12"]),
        library("library.platform.runtime.energy_accounting", RUNTIME, "semantic.runtime_receipt", ["capability.account_energy"], ["EnergyObservation", "EnergyModelRef", "AllocationBasis", "EnergyReceipt", "Uncertainty"], ["measure_or_model_energy", "attribute_energy", "reconcile_energy"], ["measurement_model_policy", "shared_energy_policy", "uncertainty_policy"], ["energy_estimate_is_not_measurement", "allocation_method_and_uncertainty_are_retained"], ["energy_source_missing", "allocation_basis_missing", "uncertainty_unbounded"], ["library.platform.runtime.receipt_contract"], "pure_effect_intents", ["evidence.opencost.spec"]),
        library("library.platform.runtime.conformance_oracles", RUNTIME, "semantic.runtime_receipt", ["capability.evaluate_runtime_conformance"], ["RuntimeConformanceProfile", "TargetProbe", "RaceFixture", "FaultFixture", "ConformanceResult"], ["probe_target", "evaluate_lifecycle", "test_cancellation", "test_fencing", "test_receipts"], ["profile_edition", "fault_population", "independence_policy"], ["documentation_is_not_conformance", "one_target_pass_is_not_universal_portability"], ["profile_incomplete", "probe_unsupported", "race_counterexample", "evidence_stale"], ["library.platform.runtime.receipt_contract"], "pure_effect_intents", ["evidence.kubernetes.conformance", "evidence.oci.runtime"], "assurance_boundary"),
        library("library.platform.finops.cost_occurrence", FINOPS, "semantic.cost_normalization", ["capability.register_cost_occurrence"], ["CostOccurrenceId", "SourceSystemRef", "ProviderRecordRef", "ServicePeriod", "Money", "CostEvidenceRef"], ["validate_cost_occurrence", "canonicalize_source_identity", "record_cost_occurrence"], ["source_edition", "currency_policy", "correction_policy"], ["cost_occurrence_is_not_invoice_line", "source_identity_and_evidence_are_retained"], ["source_edition_unknown", "currency_unknown", "cost_identity_conflict"], [], "pure_effect_intents", ["evidence.focus12"]),
        library("library.platform.finops.cost_attribution", FINOPS, "semantic.cost_allocation", ["capability.attribute_cost"], ["AttributionAssertion", "AttributionSubject", "TenantRef", "AccountRef", "WorkspaceRef", "CostCenterRef", "AttributionEvidence"], ["assert_attribution", "evaluate_attribution", "expire_attribution"], ["scope_precedence", "split_attribution_policy", "unknown_bucket_policy"], ["attribution_is_not_identity", "cross_scope_attribution_requires_authority"], ["subject_unknown", "authority_missing", "evidence_stale", "ambiguous_attribution"], ["library.platform.finops.cost_occurrence"], "pure_no_io", ["evidence.focus12", "evidence.finops.framework"]),
        library("library.platform.finops.allocation_reconciliation", FINOPS, "semantic.cost_allocation", ["capability.reconcile_cost_allocation"], ["AllocationRunRef", "EligibleInputTotal", "AllocatedTotal", "ResidualCost", "ReconciliationResult"], ["sum_inputs", "sum_outputs", "classify_residual", "reconcile"], ["rounding_policy", "residual_policy", "currency_policy"], ["input_equals_allocated_plus_declared_residual", "rounding_is_explicit"], ["currency_mismatch", "unexplained_residual", "input_set_changed"], ["library.platform.cost_allocation"], "pure_no_io", ["evidence.opencost.spec", "evidence.finops.framework"]),
        library("library.platform.finops.unit_cost", FINOPS, "semantic.unit_cost", ["capability.compute_unit_cost"], ["UnitCostDefinition", "CostNumerator", "UsefulOutputDenominator", "UnitCostObservation", "Uncertainty"], ["validate_definition", "compute_unit_cost", "propagate_uncertainty"], ["zero_denominator_policy", "allocation_policy_ref", "period_alignment_policy"], ["unit_cost_requires_governed_numerator_denominator_scope_and_period", "missing_or_zero_is_not_zero_cost"], ["denominator_missing", "denominator_zero", "period_mismatch", "uncertainty_unbounded"], ["library.platform.finops.allocation_reconciliation"], "pure_no_io", ["evidence.finops.framework"]),
    ])

    new_requirements = [
        requirement("requirement.platform.plan_paved_path", DEVELOPER, "capability.plan_paved_path", "compile_time", "paved_path_plan_unbound"),
        requirement("requirement.platform.publish_resource_offer", RUNTIME, "capability.publish_resource_offer", "runtime", "resource_offer_unbound"),
        requirement("requirement.platform.evaluate_demand_offer_compatibility", RUNTIME, "capability.evaluate_demand_offer_compatibility", "runtime", "compatibility_evaluator_unbound"),
        requirement("requirement.platform.manage_quota", RUNTIME, "capability.manage_quota", "runtime", "quota_ledger_unbound"),
        requirement("requirement.platform.select_scheduler_policy", RUNTIME, "capability.select_scheduler_policy", "compile_time", "scheduler_policy_unbound"),
        requirement("requirement.platform.reserve_capacity", RUNTIME, "capability.reserve_capacity", "runtime", "reservation_ledger_unbound"),
        requirement("requirement.platform.commit_allocation", RUNTIME, "capability.commit_allocation", "runtime", "allocation_ledger_unbound"),
        requirement("requirement.platform.manage_lease_fencing", RUNTIME, "capability.manage_lease_fencing", "runtime", "lease_fencing_unbound"),
        requirement("requirement.platform.control_preemption", RUNTIME, "capability.control_preemption", "runtime", "preemption_control_unbound"),
        requirement("requirement.platform.control_autoscaling", RUNTIME, "capability.control_autoscaling", "runtime", "autoscaling_control_unbound"),
        requirement("requirement.platform.apply_backpressure", RUNTIME, "capability.apply_backpressure", "runtime", "backpressure_control_unbound"),
        requirement("requirement.platform.control_deadline_cancellation", RUNTIME, "capability.control_deadline_cancellation", "runtime", "deadline_cancellation_unbound"),
        requirement("requirement.platform.manage_checkpoint", RUNTIME, "capability.manage_checkpoint", "runtime", "checkpoint_contract_unbound"),
        requirement("requirement.platform.bind_runtime_backend", RUNTIME, "capability.bind_runtime_backend", "target_binding", "runtime_backend_unbound"),
        requirement("requirement.platform.account_runtime_usage", RUNTIME, "capability.account_runtime_usage", "runtime", "usage_accounting_unbound"),
        requirement("requirement.platform.account_energy", RUNTIME, "capability.account_energy", "runtime", "energy_accounting_unbound"),
        requirement("requirement.platform.evaluate_runtime_conformance", RUNTIME, "capability.evaluate_runtime_conformance", "qualification", "runtime_conformance_unbound"),
        requirement("requirement.platform.register_cost_occurrence", FINOPS, "capability.register_cost_occurrence", "runtime", "cost_occurrence_contract_unbound"),
        requirement("requirement.platform.attribute_cost", FINOPS, "capability.attribute_cost", "runtime", "cost_attribution_unbound"),
        requirement("requirement.platform.reconcile_cost_allocation", FINOPS, "capability.reconcile_cost_allocation", "runtime", "allocation_reconciliation_unbound"),
        requirement("requirement.platform.compute_unit_cost", FINOPS, "capability.compute_unit_cost", "query_time", "unit_cost_contract_unbound"),
    ]
    known_requirements = {row["requirement_id"] for row in source["requirements"]}
    source["requirements"].extend(row for row in new_requirements if row["requirement_id"] not in known_requirements)

    # Replace product maps so every abstract seam carries one exact product attribution.
    product_library_union = set().union(*PRODUCT_LIBRARIES.values())
    source["binding_maps"] = [
        row for row in source["binding_maps"]
        if row["abstract_library_ref"] not in product_library_union and row["abstract_library_ref"] != "library.platform.allocation_lease"
    ]
    exact: dict[str, list[str]] = {
        "library.platform.blueprint": ["library.platform-commercial-support.catalog-repository-port"],
        "library.platform.developer.paved_path_plan": ["library.platform-commercial-support.exit-manifest"],
        "library.platform.paved_path_runtime": ["library.platform-commercial-support.exit-manifest", "library.platform-commercial-support.export-transfer-port"],
        "library.platform.runtime.work_contract": ["library.runtime-resource.identity-types"],
        "library.platform.resource_vector": ["library.runtime-resource.resource-quantity"],
        "library.platform.runtime.resource_offer": ["library.runtime-resource.resource-topology"],
        "library.platform.runtime.demand_offer_compatibility": ["library.runtime-resource.demand-offer-compatibility"],
        "library.platform.runtime.quota_ledger": ["library.runtime-resource.quota-ledger"],
        "library.platform.admission": ["library.runtime-resource.admission"],
        "library.platform.runtime.scheduler_policy": ["library.runtime-resource.scheduler-policy-spi", "library.runtime-resource.scheduler-fifo", "library.runtime-resource.scheduler-drf", "library.runtime-resource.scheduler-binpack", "library.runtime-resource.scheduler-min-cost-flow", "library.runtime-resource.scheduler-gang"],
        "library.platform.placement": ["library.runtime-resource.placement-constraints"],
        "library.platform.runtime.reservation_ledger": ["library.runtime-resource.reservation-ledger"],
        "library.platform.runtime.allocation_ledger": ["library.runtime-resource.reservation-ledger"],
        "library.platform.runtime.lease_fencing": ["library.runtime-resource.lease-fencing"],
        "library.platform.runtime.preemption_control": ["library.runtime-resource.preemption-policy"],
        "library.platform.runtime.autoscaling_control": ["library.runtime-resource.autoscaling-control"],
        "library.platform.runtime.backpressure_control": ["library.runtime-resource.backpressure"],
        "library.platform.runtime.deadline_cancellation": ["library.runtime-resource.deadline-cancellation"],
        "library.platform.runtime.checkpoint_contract": ["library.runtime-resource.checkpoint-contract"],
        "library.platform.runtime.backend_spi": ["library.runtime-resource.process-backend", "library.runtime-resource.async-executor", "library.runtime-resource.actor-runtime-spi", "library.runtime-resource.device-runtime-spi", "library.runtime-resource.container-runtime-adapter", "library.runtime-resource.wasm-runtime-adapter", "library.runtime-resource.provider-adapter-spi"],
        "library.platform.runtime_attempt": ["library.runtime-resource.attempt-state"],
        "library.platform.runtime.receipt_contract": ["library.runtime-resource.runtime-receipts"],
        "library.platform.runtime.usage_accounting": ["library.runtime-resource.usage-accounting"],
        "library.platform.runtime.energy_accounting": ["library.runtime-resource.energy-accounting"],
        "library.platform.runtime.conformance_oracles": ["library.runtime-resource.conformance-oracles"],
        "library.platform.meter": ["library.platform-commercial-support.meter_definition", "library.platform-commercial-support.usage_event", "library.platform-commercial-support.usage_aggregation", "library.platform-commercial-support.usage-journal-port"],
        "library.platform.finops.cost_occurrence": ["library.csp.quantity.money-core", "library.csp.time.interval-algebra", "library.platform-commercial-support.usage-journal-port"],
        "library.platform.finops.cost_attribution": [
            "library.platform-commercial-support.account_identity",
            "library.platform-commercial-support.customer_party_identity",
            "library.platform-commercial-support.billing_account_identity",
            "library.platform-commercial-support.legal_entity_binding",
            "library.platform-commercial-support.allocation-core",
        ],
        "library.platform.cost_normalization": ["library.platform-commercial-support.focus-normalization"],
        "library.platform.cost_allocation": ["library.platform-commercial-support.allocation-core"],
        "library.platform.finops.allocation_reconciliation": ["library.platform-commercial-support.allocation-core"],
        "library.platform.budget_precharge": ["library.platform-commercial-support.commercial-credit-preauthorization"],
        "library.platform.finops.unit_cost": ["library.csp.quantity.money-core", "library.platform-commercial-support.allocation-core"],
    }
    source["binding_maps"].extend(binding(local, refs, product) for product, libs in PRODUCT_LIBRARIES.items() for local in sorted(libs - {"library.platform.developer.platform_conformance"}) for refs in [exact[local]])
    source["binding_maps"].append(binding("library.platform.developer.platform_conformance", ["library.ce.conformance", "library.ce.receipt", "library.ce.evidence", "library.ce.composition", "library.ce.invalidation"], DEVELOPER, CONFORMANCE_REGISTRY))
    telemetry_refs = [
        "library.telemetry.attribution_core",
        "library.telemetry.schema_conventions",
        "library.telemetry.trace_graph",
        "library.telemetry.metric_stream",
        "library.telemetry.log_event",
        "library.telemetry.profile_sample",
        "library.telemetry.propagation_context",
        "library.telemetry.observation_reduction",
        "library.telemetry.cross_signal_correlation",
        "library.telemetry.export_delivery",
    ]
    telemetry_map = next(row for row in source["binding_maps"] if row["abstract_library_ref"] == "library.platform.telemetry")
    telemetry_map.update({
        "concrete_library_refs": telemetry_refs,
        "concrete_library_origins": {ref: CENTRAL_REGISTRY for ref in telemetry_refs},
        "compiler_disposition": "structurally_projected_unqualified",
        "gap_ref": None,
        "portable_offer": False,
        "product_refs": [],
    })
    source["binding_gaps"] = [
        row for row in source["binding_gaps"]
        if row["gap_id"] not in {"gap.platform.focus_normalization_library", "gap.platform.generic_telemetry_library"}
    ]

    source["ddd_dossiers"] = [row for row in source.get("ddd_dossiers", []) if row.get("product_ref") not in PRODUCTS]
    source["ddd_dossiers"].extend([_developer_dossier(), _runtime_dossier(), _finops_dossier()])
    source["non_collapse_laws"].extend([
        "platform blueprint != template != instantiation plan != effect occurrence != conformant instance != accepted service",
        "work unit != job != attempt != worker != executor != deployment occurrence",
        "resource demand != resource offer != quota != budget != admission != placement != reservation != allocation != lease != consumed usage",
        "usage event != usage aggregate != cost occurrence != normalized cost != attributed cost != allocated cost != charge != invoice != payment",
        "scheduler policy result states its assurance and never converts hard constraints to preferences",
        "optional model or agent proposal is removable and has no admission allocation cost finance or effect authority",
    ])
    source["negative_tests"].extend([
        {"test_id": "negative.platform.portal_truth", "prohibited_claim": "A developer portal projection is the authoritative platform or service catalog.", "expected_result": "resolve the owning blueprint and service contracts"},
        {"test_id": "negative.platform.render_ready", "prohibited_claim": "A successful template or composition render proves a ready service.", "expected_result": "require effects runtime conformance and acceptance receipts"},
        {"test_id": "negative.runtime.quota_capacity", "prohibited_claim": "Available quota proves resource capacity or placement.", "expected_result": "evaluate exact offers compatibility and placement"},
        {"test_id": "negative.runtime.lease_fence", "prohibited_claim": "A valid lease prevents a stale writer without enforcement at the effect.", "expected_result": "require monotonic effect-side fencing"},
        {"test_id": "negative.runtime.timeout_failure", "prohibited_claim": "A caller timeout proves an attempt failed.", "expected_result": "retain unknown and reconcile receipts"},
        {"test_id": "negative.runtime.retry_identity", "prohibited_claim": "A retry may overwrite or reuse the prior attempt identity.", "expected_result": "create a new append-only attempt"},
        {"test_id": "negative.finops.normalized_allocated", "prohibited_claim": "A normalized cost record is already attributed or allocated.", "expected_result": "apply evidence-backed attribution allocation and reconciliation"},
        {"test_id": "negative.finops.showback_invoice", "prohibited_claim": "A showback or unit-cost projection is an invoice or ledger posting.", "expected_result": "retain finance authority boundary"},
        {"test_id": "negative.platform.agent_authority", "prohibited_claim": "An agent proposal may fill missing platform runtime or FinOps evidence and execute the result.", "expected_result": "retain proposal taint and deterministic authority proof and effect gates"},
    ])
    return source
