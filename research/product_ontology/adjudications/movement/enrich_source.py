#!/usr/bin/env python3
"""Deterministically enrich the movement adjudication with product DDD and compiler maps.

The original source.json remains the evidence/boundary corpus.  This script owns only the
explicit product fields, product-library attribution, DDD dossiers, and compiler maps/gaps.
It strips those managed fields before deriving the expected enriched source, so --check catches
manual drift without requiring a second copy of the large base corpus.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "source.json"
PRODUCT_FIELDS = {
    "sovereign_question", "users", "harmed_parties", "jobs", "outcomes", "negative_mission",
    "lifecycle_states", "commands", "events", "invariants", "refusals", "automation_modality",
}


def pascal(value: str) -> str:
    return "".join(part.capitalize() for part in value.replace("-", "_").split("_"))


def product_spec(
    *, key: str, question: str, users: list[str], harmed: list[str], job: str,
    outcomes: list[str], negative: str, inside: list[str], outside: list[str],
    values: list[str], entities: list[str], aggregates: list[dict[str, Any]],
    invariants: list[str], commands: list[str], events: list[str], states: list[str],
    refusals: list[str], services: list[str], specifications: list[str],
    policies: list[str], sagas: list[str], reads: list[str], time: list[str],
    neighbors: list[tuple[str, str, str]], nfr: list[str],
) -> dict[str, Any]:
    return locals()


SPECS = {
    "product.source_connectivity_control": product_spec(
        key="source_connectivity_control",
        question="How can source owners declare, qualify, deploy, observe, upgrade and revoke source connections without transferring source meaning or credential custody?",
        users=["integration_engineer", "source_owner", "platform_operator", "security_reviewer"],
        harmed=["data_subject", "source_operator", "downstream_consumer", "credential_owner"],
        job="Declare, qualify, reconcile, observe, upgrade, suspend and revoke portable source-connection bindings.",
        outcomes=["portable_connection_declaration", "qualified_binding", "health_and_transition_evidence", "provable_revocation"],
        negative="Does not own source data meaning, credential secret values, capture semantics, pipeline scheduling or downstream delivery.",
        inside=["connection declarations", "source occurrence binding", "protocol and network profiles", "credential references", "connector desired/observed state", "health", "upgrade coexistence", "suspension and revocation"],
        outside=["secret custody", "source business facts", "snapshot/change capture", "workflow scheduling", "sink delivery", "provider internals"],
        values=["ConnectionId", "ConnectionEdition", "SourceOccurrenceRef", "CredentialRef", "ProtocolProfile", "NetworkPathProfile", "HealthClassification", "RevocationRef"],
        entities=["ConnectionDeclaration", "ConnectionBinding", "ConnectorOccurrence", "QualificationOccurrence", "RevocationOccurrence"],
        aggregates=[{"root": "ConnectionDeclaration", "members": ["source_ref", "protocol_profile", "credential_ref", "network_profile", "lifecycle"], "consistency": "one command advances one connection edition"}, {"root": "ConnectionBinding", "members": ["declaration_ref", "provider_occurrence", "desired_state", "observed_state", "health", "fence"], "consistency": "binding transitions are fenced and total"}],
        invariants=["credential values never enter declarations or receipts", "source occurrence and connector occurrence identities are distinct", "provider identity does not change connection meaning", "revoked bindings cannot restart", "qualification evidence is scoped to exact editions and expires"],
        commands=["draft_connection", "bind_source_occurrence", "request_qualification", "approve_binding", "deploy_connector", "record_connector_observation", "request_upgrade", "suspend_binding", "revoke_binding", "retire_connection"],
        events=["connection_drafted", "source_occurrence_bound", "qualification_requested", "binding_approved", "connector_deployed", "connector_observation_recorded", "upgrade_requested", "binding_suspended", "binding_revoked", "connection_retired"],
        states=["draft", "source_bound", "qualification_pending", "qualified", "deploying", "active", "degraded", "suspended", "revoked", "retired"],
        refusals=["source_occurrence_unknown", "credential_reference_invalid", "protocol_profile_unsupported", "network_path_forbidden", "provider_offer_unqualified", "qualification_expired", "illegal_transition", "revocation_pending", "upgrade_incompatible"],
        services=["ConnectionValidationService", "ProviderQualificationService", "LifecycleReconciliationService", "RevocationPlanningService"],
        specifications=["ConnectionCompletenessSpecification", "ProtocolCompatibilitySpecification", "BindingQualificationSpecification", "UpgradeCoexistenceSpecification", "RevocationCompletionSpecification"],
        policies=["when qualification expires suspend new deployment", "when health crosses the failure threshold reconcile under the declared restart policy", "when authority revokes a binding fence every connector occurrence", "when an upgrade is incompatible retain coexistence or refuse"],
        sagas=["ConnectionQualificationProcess", "ConnectorDeploymentProcess", "ConnectorUpgradeProcess", "ConnectionRevocationProcess"],
        reads=["ConnectionCatalogView", "BindingStatusView", "ConnectorHealthView", "QualificationEvidenceView", "RevocationImpactView"],
        time=["declaration validity and recording time are distinct", "qualification and credential-reference expiry are explicit", "observations carry occurrence time and recording time", "revocation effective time is fenced"],
        neighbors=[("neighbor.source_system", "customer_supplier_acl", "resolve source occurrence and authority without importing business meaning"), ("neighbor.secret_custody", "anti_corruption_layer", "exchange credential references and access outcomes only"), ("product.source_replication_cdc", "published_language", "publish qualified connection binding references"), ("neighbor.runtime_resource", "customer_supplier", "submit connector runtime demands and receive occurrence receipts")],
        nfr=["no secret material in semantic state", "bounded validation and reconciliation", "cooperative cancellation", "fail-closed qualification and revocation", "health and transition receipts bind exact editions"],
    ),
    "product.source_replication_cdc": product_spec(
        key="source_replication_cdc",
        question="How can a replication operator produce a reconstructable snapshot-plus-change stream from source-native history without gaps, silent duplicates or cursor ambiguity?",
        users=["replication_engineer", "source_dba", "data_platform_operator", "recovery_operator"],
        harmed=["source_operator", "downstream_consumer", "data_subject", "recovery_owner"],
        job="Configure, snapshot, capture, stitch, checkpoint, resume and retire source replication with reconstructability evidence.",
        outcomes=["provable_snapshot_cut", "ordered_change_stream", "gap_and_duplicate_evidence", "resumable_source_cursor"],
        negative="Does not own connection qualification, source business truth, target delivery commits, transformation meaning or consumer replay policy.",
        inside=["source epochs and partitions", "source cursors", "snapshot cuts and chunks", "change envelopes", "snapshot/change stitching", "gap and duplicate classification", "capture checkpoint and resume"],
        outside=["connection deployment", "sink acknowledgement", "schema business meaning", "workflow scheduling", "target materialization", "source mutation"],
        values=["CaptureId", "SourceEpoch", "SourcePartition", "SourceCursor", "SnapshotCut", "SnapshotChunk", "ChangeEnvelope", "CursorGap", "StitchResidual"],
        entities=["CaptureDefinition", "CaptureRun", "SnapshotOccurrence", "ChangePartition", "CaptureCheckpoint"],
        aggregates=[{"root": "CaptureDefinition", "members": ["source_binding", "capture_profile", "snapshot_strategy", "schema_change_policy", "lifecycle"], "consistency": "capture semantics change only through a new definition edition"}, {"root": "CaptureRun", "members": ["source_epoch", "snapshot_cut", "partition_cursors", "stitch_state", "residuals"], "consistency": "every accepted change is classified relative to the snapshot cut"}],
        invariants=["cursors from different source epochs are never silently ordered", "every accepted change is before inside or after the snapshot cut", "snapshot completeness is evidenced per chunk and partition", "duplicates gaps and schema transitions are explicit", "resume never advances beyond durably evidenced progress"],
        commands=["draft_capture", "bind_source_epoch", "start_snapshot", "record_snapshot_chunk", "start_change_capture", "advance_source_cursor", "stitch_snapshot_and_changes", "record_capture_checkpoint", "resume_capture", "reset_cursor", "complete_snapshot", "retire_capture"],
        events=["capture_drafted", "source_epoch_bound", "snapshot_started", "snapshot_chunk_recorded", "change_capture_started", "source_cursor_advanced", "snapshot_and_changes_stitched", "capture_checkpoint_recorded", "capture_resumed", "cursor_reset", "snapshot_completed", "capture_retired"],
        states=["draft", "epoch_bound", "snapshotting", "catching_up", "streaming", "gap_detected", "paused", "recovering", "completed", "retired"],
        refusals=["source_epoch_unknown", "cursor_incomparable", "cursor_reset_not_authorized", "snapshot_cut_unprovable", "log_history_missing", "chunk_identity_ambiguous", "schema_transition_unsupported", "gap_unresolved", "resume_checkpoint_invalid"],
        services=["CursorAlgebraService", "SnapshotPlanningService", "SnapshotChangeStitchingService", "CaptureRecoveryService"],
        specifications=["SourceEpochSpecification", "SnapshotCutSpecification", "CursorAdvanceSpecification", "StitchCompletenessSpecification", "ResumeSafetySpecification"],
        policies=["when source epoch changes pause and require explicit cursor translation or reset", "when a gap appears stop progress beyond the gap", "when snapshot completes retain the exact overlap evidence", "when schema transition is unsupported emit a typed residual and pause"],
        sagas=["SnapshotCaptureProcess", "SnapshotChangeHandoffProcess", "CaptureRecoveryProcess", "CaptureRetirementProcess"],
        reads=["CaptureTopologyView", "SnapshotProgressView", "PartitionCursorView", "GapDuplicateView", "ReconstructabilityView"],
        time=["source event time recording time and capture time remain distinct", "source epoch scopes cursor order", "snapshot cut is an exact logical boundary", "checkpoint recording and resume time are explicit"],
        neighbors=[("product.source_connectivity_control", "customer_supplier", "import a qualified source binding"), ("neighbor.source_system", "anti_corruption_layer", "translate source-native log and snapshot identities"), ("product.ingestion_delivery", "published_language", "publish snapshot and change envelopes with source-position evidence"), ("neighbor.schema_contract", "customer_supplier", "resolve schema editions without acquiring field meaning")],
        nfr=["bounded snapshot chunks", "backpressure against source and downstream", "cooperative cancellation", "no silent cursor reset", "recovery evidence binds source epoch cut cursors and provider"],
    ),
    "product.ingestion_delivery": product_spec(
        key="ingestion_delivery",
        question="How can a delivery operator move admitted source records into an analytical target with explicit schema loss, acknowledgement, retry and recoverable progress?",
        users=["data_platform_operator", "source_owner", "target_owner", "data_engineer"],
        harmed=["source_owner", "target_consumer", "data_subject", "on_call_operator"],
        job="Declare, validate, run, acknowledge, reconcile, recover and retire source-to-target deliveries across replaceable adapters.",
        outcomes=["portable_delivery_declaration", "explicit_schema_residuals", "recoverable_delivery_progress", "source_to_target_receipts"],
        negative="Does not own source capture history, target table semantics, business transformations, workflow scheduling or target fact acceptance.",
        inside=["delivery declarations", "source and target shape bindings", "field mappings and loss residuals", "delivery batches", "sink acknowledgements", "retry dedup and recovery", "delivery receipts"],
        outside=["source cursor generation", "target catalog authority", "business transformation", "workflow dependencies", "data quality acceptance", "consumer use authority"],
        values=["DeliveryId", "DeliveryEdition", "SourceStreamRef", "TargetContractRef", "FieldMapping", "LossResidual", "DeliveryCursor", "SinkAcknowledgement", "DeliveryReceipt"],
        entities=["DeliveryDefinition", "DeliveryRun", "DeliveryAttempt", "SchemaMappingEdition", "DeliveryCheckpoint"],
        aggregates=[{"root": "DeliveryDefinition", "members": ["source_ref", "target_ref", "schema_mapping", "delivery_profile", "lifecycle"], "consistency": "one edition fixes mapping and delivery semantics"}, {"root": "DeliveryRun", "members": ["input_cut", "attempts", "acknowledgements", "progress", "residuals"], "consistency": "progress advances only after an accepted acknowledgement"}],
        invariants=["source target and mapping editions are explicit", "schema loss is attributable and accepted or refused", "acknowledgement meaning is target-contract scoped", "retry never converts unknown completion into success", "delivery completion is not target factual acceptance"],
        commands=["draft_delivery", "bind_source_stream", "bind_target_contract", "compile_schema_mapping", "approve_loss_profile", "start_delivery", "submit_delivery_batch", "record_sink_acknowledgement", "retry_delivery", "resume_delivery", "reconcile_delivery", "complete_delivery", "retire_delivery"],
        events=["delivery_drafted", "source_stream_bound", "target_contract_bound", "schema_mapping_compiled", "loss_profile_approved", "delivery_started", "delivery_batch_submitted", "sink_acknowledgement_recorded", "delivery_retried", "delivery_resumed", "delivery_reconciled", "delivery_completed", "delivery_retired"],
        states=["draft", "bindings_resolved", "mapping_review", "ready", "running", "partially_acknowledged", "retrying", "paused", "reconciling", "completed", "failed", "retired"],
        refusals=["source_stream_unresolved", "target_contract_missing", "unrepresentable_type", "identity_field_lost", "schema_evolution_policy_missing", "ambiguous_acknowledgement", "dedup_key_missing", "resume_cut_invalid", "target_offer_unqualified", "completion_unknown"],
        services=["SchemaMappingService", "DeliveryPlanningService", "AcknowledgementInterpretationService", "DeliveryReconciliationService"],
        specifications=["DeliveryReadinessSpecification", "SchemaLossAcceptanceSpecification", "AcknowledgementSpecification", "RetrySafetySpecification", "CompletionSpecification"],
        policies=["when schema loss is unaccepted refuse execution", "when completion is unknown reconcile before retry", "when acknowledgement is partial retain the unacknowledged cut", "when target schema changes compile a new mapping edition"],
        sagas=["DeliveryBindingProcess", "DeliveryRunProcess", "UnknownCompletionReconciliationProcess", "DeliveryRetirementProcess"],
        reads=["DeliveryCatalogView", "SchemaMappingDiffView", "RunProgressView", "AcknowledgementLedgerView", "DeliveryLineageView"],
        time=["source event time and delivery occurrence time are distinct", "target acknowledgement time is recorded independently", "mapping validity and recording time are explicit", "retry and resume bind an exact progress cut"],
        neighbors=[("product.source_replication_cdc", "customer_supplier", "import source-positioned records"), ("neighbor.target_catalog", "anti_corruption_layer", "resolve target shape and commit contract"), ("product.pipeline_orchestration", "open_host_service", "expose idempotent run commands and status"), ("neighbor.lineage_provenance", "published_language", "publish delivery lineage and receipts")],
        nfr=["bounded batches and buffers", "backpressure and cancellation", "idempotent attempts", "failure-visible acknowledgements", "receipts bind source cut mapping target provider and outcome"],
    ),
    "product.pipeline_orchestration": product_spec(
        key="pipeline_orchestration",
        question="How can operators coordinate scheduled and triggered data work, retries, backfills and cancellation without owning the semantics of the work being invoked?",
        users=["data_engineer", "operations_engineer", "workflow_owner", "incident_responder"],
        harmed=["downstream_consumer", "on_call_operator", "resource_tenant", "data_subject"],
        job="Author, schedule, trigger, run, retry, backfill, cancel, recover and retire data workflows under explicit state and concurrency laws.",
        outcomes=["portable_workflow_definition", "total_run_state", "bounded_retry_and_backfill", "recoverable_orchestration_receipts"],
        negative="Does not own task business semantics, data transformation correctness, worker implementation, source truth or effect authorization.",
        inside=["workflow definitions", "dependency and trigger rules", "schedules and logical intervals", "workflow runs and task attempts", "concurrency admission", "retry backfill cancellation and run recovery"],
        outside=["task implementation", "record processing", "resource placement", "source and sink semantics", "business approval", "external effect meaning"],
        values=["WorkflowId", "WorkflowEdition", "TaskId", "LogicalInterval", "ScheduleEdition", "Trigger", "RetryPolicy", "BackfillSet", "CancellationMode"],
        entities=["WorkflowDefinition", "WorkflowRun", "TaskAttempt", "Schedule", "BackfillCampaign"],
        aggregates=[{"root": "WorkflowDefinition", "members": ["tasks", "dependencies", "triggers", "schedule", "policies", "lifecycle"], "consistency": "published workflow editions are immutable"}, {"root": "WorkflowRun", "members": ["logical_interval", "task_attempts", "dependency_states", "run_state", "cancellation"], "consistency": "run and attempt state transitions are total and fenced"}],
        invariants=["attempt identity is never reused", "logical interval differs from wall-clock run time", "terminal states are total", "retry does not erase the failed attempt", "cancellation completion and external effect completion are distinct"],
        commands=["draft_workflow", "publish_workflow", "bind_schedule", "trigger_run", "admit_task_attempt", "record_task_outcome", "retry_task", "plan_backfill", "start_backfill", "cancel_run", "resume_run", "close_run", "retire_workflow"],
        events=["workflow_drafted", "workflow_published", "schedule_bound", "run_triggered", "task_attempt_admitted", "task_outcome_recorded", "task_retried", "backfill_planned", "backfill_started", "run_cancelled", "run_resumed", "run_closed", "workflow_retired"],
        states=["draft", "published", "scheduled", "queued", "running", "waiting", "retrying", "backfilling", "cancelling", "cancelled", "succeeded", "failed", "retired"],
        refusals=["workflow_invalid", "dependency_cycle", "calendar_unresolved", "dependency_unsatisfied", "concurrency_exceeded", "retry_budget_exhausted", "interval_overlap_forbidden", "illegal_transition", "cancellation_unsupported", "task_completion_unknown"],
        services=["WorkflowValidationService", "ScheduleEvaluationService", "RunCoordinationService", "BackfillPlanningService"],
        specifications=["WorkflowPublicationSpecification", "RunAdmissionSpecification", "TaskReadinessSpecification", "RetryEligibilitySpecification", "BackfillSafetySpecification", "RunClosureSpecification"],
        policies=["when dependencies become satisfied admit the next attempt under concurrency limits", "when an attempt fails evaluate retry without rewriting history", "when a backfill overlaps active work apply the declared overlap policy", "when cancellation is requested stop new admissions and track in-flight disposition"],
        sagas=["ScheduledRunProcess", "WorkflowRunProcess", "BackfillCampaignProcess", "RunCancellationProcess"],
        reads=["WorkflowGraphView", "ScheduleCalendarView", "RunTimelineView", "TaskAttemptView", "BackfillImpactView"],
        time=["logical interval trigger time queue time start time and completion time are distinct", "schedules bind calendar timezone and edition", "misfire and catch-up policies are explicit", "retry delays use a finite budget"],
        neighbors=[("neighbor.task_catalog", "anti_corruption_layer", "import typed idempotent task commands and outcomes"), ("neighbor.runtime_resource", "customer_supplier", "request attempt admission and receive runtime receipts"), ("neighbor.lineage_provenance", "published_language", "publish run and attempt evidence"), ("neighbor.incident_operations", "open_host_service", "surface failed and stuck runs without transferring run authority")],
        nfr=["total deterministic state machine", "bounded scheduling and backfill enumeration", "cooperative cancellation", "finite concurrency and retry budgets", "append-only run and attempt evidence"],
    ),
    "product.dataflow_execution": product_spec(
        key="dataflow_execution",
        question="How can a compiler and operator execute typed bounded or unbounded dataflow graphs with explicit event time, state, checkpoint, recovery and end-to-end effect guarantees?",
        users=["pipeline_compiler", "data_engineer", "runtime_operator", "state_recovery_operator"],
        harmed=["downstream_consumer", "data_subject", "resource_tenant", "on_call_operator"],
        job="Typecheck, plan, deploy, execute, checkpoint, recover, drain, cancel and retire stateful dataflow graphs.",
        outcomes=["typed_portable_dataflow_plan", "bounded_time_and_state_contract", "recoverable_execution", "scoped_delivery_guarantee_receipt"],
        negative="Does not own business transformation meaning, workflow scheduling, source or sink authority, physical provider selection without qualification, or downstream action.",
        inside=["typed dataflow IR", "ports and carriers", "boundedness update and time contracts", "event time watermarks windows and lateness", "operator state", "checkpoints", "recovery", "end-to-end commit premises"],
        outside=["business formula meaning", "workflow scheduling", "source capture policy", "target catalog commits", "resource-provider internals", "external effect authority"],
        values=["DataflowId", "GraphEdition", "PortType", "CarrierContract", "EventTime", "Watermark", "Window", "StateContract", "CheckpointCut", "RunnerRequirement", "DeliveryGuarantee"],
        entities=["DataflowDefinition", "ExecutionPlan", "Deployment", "DataflowRun", "OperatorOccurrence", "CheckpointOccurrence"],
        aggregates=[{"root": "DataflowDefinition", "members": ["graph", "ports", "time_contracts", "state_contracts", "requirements", "lifecycle"], "consistency": "one graph edition is immutable after publication"}, {"root": "DataflowRun", "members": ["plan_ref", "deployment_ref", "operator_occurrences", "progress_frontier", "checkpoints", "run_state"], "consistency": "checkpoint publication requires all declared premises"}],
        invariants=["every edge has one carrier update order cardinality and time contract", "watermarks are monotone within one source epoch", "state scope bound TTL durability and migration are explicit", "operator exactly-once is not external-effect exactly-once", "recovery cannot claim a guarantee stronger than source replay and sink commit premises"],
        commands=["draft_dataflow", "typecheck_dataflow", "derive_runner_requirements", "compile_execution_plan", "qualify_runner", "deploy_dataflow", "start_dataflow_run", "advance_progress", "form_checkpoint", "publish_checkpoint", "restore_checkpoint", "drain_run", "cancel_run", "retire_dataflow"],
        events=["dataflow_drafted", "dataflow_typechecked", "runner_requirements_derived", "execution_plan_compiled", "runner_qualified", "dataflow_deployed", "dataflow_run_started", "progress_advanced", "checkpoint_formed", "checkpoint_published", "checkpoint_restored", "run_drained", "run_cancelled", "dataflow_retired"],
        states=["draft", "typed", "planned", "qualification_pending", "deploying", "running", "checkpointing", "recovering", "draining", "cancelled", "completed", "failed", "retired"],
        refusals=["port_type_mismatch", "unbounded_operation", "time_domain_missing", "lateness_policy_missing", "state_bound_missing", "runner_capability_gap", "source_not_replayable", "sink_not_idempotent_or_transactional", "state_serializer_incompatible", "checkpoint_incomplete", "resource_budget_exhausted"],
        services=["DataflowTypecheckingService", "LogicalPlanningService", "EventTimeService", "CheckpointProofService", "RecoveryPlanningService"],
        specifications=["GraphWellFormedSpecification", "PortCompatibilitySpecification", "StateBoundSpecification", "RunnerQualificationSpecification", "CheckpointPublicationSpecification", "EndToEndGuaranteeSpecification"],
        policies=["when a port contract is unresolved refuse planning", "when a watermark regresses pause the affected epoch", "when checkpoint premises are incomplete retain it as uncommitted", "when recovery changes provider requalify state and serialization compatibility"],
        sagas=["DataflowCompilationProcess", "DataflowDeploymentProcess", "CheckpointPublicationProcess", "DataflowRecoveryProcess"],
        reads=["DataflowGraphView", "PortCompatibilityView", "RunProgressView", "StateInventoryView", "CheckpointLineageView", "GuaranteePremiseView"],
        time=["event processing ingestion and recording time are independent", "watermark and progress frontiers are partial orders", "checkpoint cut and publication time are distinct", "state TTL and recovery horizon are explicit"],
        neighbors=[("product.pipeline_orchestration", "customer_supplier", "accept typed run and cancellation commands"), ("neighbor.runtime_resource", "customer_supplier", "bind qualified execution and state-backend offers"), ("product.source_replication_cdc", "anti_corruption_layer", "import replay and cursor premises"), ("neighbor.target_commit", "anti_corruption_layer", "import sink commit and idempotency premises"), ("neighbor.lineage_provenance", "published_language", "publish plan run checkpoint and delivery receipts")],
        nfr=["bounded resources and backpressure", "cooperative cancellation", "deterministic semantic planning", "explicit permitted nondeterminism", "checkpoint and recovery evidence bind exact graph plan providers and cuts"],
    ),
    "product.batch_transform_build": product_spec(
        key="batch_transform_build",
        question="How can analytics engineers compile, select, test and materialize versioned transformation resources over exact input and target cuts with reproducible build evidence?",
        users=["analytics_engineer", "data_product_developer", "build_operator", "reviewer"],
        harmed=["downstream_consumer", "source_owner", "target_owner", "on_call_operator"],
        job="Resolve, select, test, plan, execute, publish, backfill and retire versioned batch transformation builds.",
        outcomes=["reproducible_transform_manifest", "typed_dependency_selection", "bounded_materialization_plan", "build_and_publication_receipts"],
        negative="Does not own interactive data preparation, source facts, query-engine internals, target catalog authority or workflow scheduling.",
        inside=["project and package editions", "resource manifests", "references and macros", "dependency and selection graphs", "tests", "materialization and incremental plans", "build outcomes", "publication candidates"],
        outside=["interactive preparation history", "physical query execution", "target commit authority", "workflow schedules", "business metric approval", "source correction"],
        values=["ProjectEdition", "PackageEdition", "ResourceId", "ManifestDigest", "Selection", "InputCutRef", "MaterializationIntent", "IncrementalState", "BuildPlan", "BuildReceipt"],
        entities=["TransformProject", "TransformResource", "BuildInvocation", "MaterializationOccurrence", "PublicationCandidate"],
        aggregates=[{"root": "TransformProject", "members": ["manifest", "packages", "resource_graph", "tests", "lifecycle"], "consistency": "manifest digest covers all semantic build inputs"}, {"root": "BuildInvocation", "members": ["selection", "input_cuts", "plan", "attempts", "results", "receipt"], "consistency": "every result binds exact selected resource and input editions"}],
        invariants=["manifest digest identifies all semantic inputs", "selection is evaluated over one resolved graph edition", "skipped differs from passed", "incremental plan is valid under full refresh", "build success is not target publication authority"],
        commands=["open_transform_project", "resolve_packages", "parse_manifest", "resolve_resource_graph", "select_resources", "compile_tests", "plan_materialization", "start_build", "record_resource_result", "plan_incremental_backfill", "submit_publication_candidate", "supersede_project", "retire_project"],
        events=["transform_project_opened", "packages_resolved", "manifest_parsed", "resource_graph_resolved", "resources_selected", "tests_compiled", "materialization_planned", "build_started", "resource_result_recorded", "incremental_backfill_planned", "publication_candidate_submitted", "project_superseded", "project_retired"],
        states=["draft", "resolved", "parsed", "selected", "planned", "building", "testing", "publication_pending", "completed", "failed", "superseded", "retired"],
        refusals=["package_edition_missing", "reference_unresolved", "dependency_cycle", "selection_invalid", "input_cut_unresolved", "target_capability_missing", "unique_key_invalid", "schema_change_unhandled", "test_failed", "publication_authority_missing"],
        services=["ManifestResolutionService", "ResourceSelectionService", "TransformPlanningService", "MaterializationPlanningService", "BuildResultService"],
        specifications=["ManifestCompletenessSpecification", "SelectionSpecification", "InputCutSpecification", "IncrementalValiditySpecification", "BuildCompletionSpecification", "PublicationCandidateSpecification"],
        policies=["when a reference is unresolved refuse selection", "when a test fails withhold publication", "when incremental validity is unproved require full refresh or refuse", "when project edition changes create a new build identity"],
        sagas=["ProjectResolutionProcess", "TransformBuildProcess", "IncrementalBackfillProcess", "PublicationCandidateProcess"],
        reads=["ResourceGraphView", "SelectionPreview", "BuildTimelineView", "TestResultView", "MaterializationDiffView", "InputOutputLineageView"],
        time=["project validity and recording time are distinct", "input data cuts are exact", "build attempt time differs from logical target interval", "incremental state and supersession horizons are explicit"],
        neighbors=[("neighbor.source_catalog", "anti_corruption_layer", "resolve exact input cuts"), ("neighbor.query_execution", "customer_supplier", "submit typed physical work and import receipts"), ("neighbor.target_commit", "customer_supplier", "submit publication candidates without acquiring commit authority"), ("product.pipeline_orchestration", "open_host_service", "expose idempotent build commands and status")],
        nfr=["deterministic manifest resolution and selection", "bounded graph and plan construction", "cooperative cancellation", "reproducible build inputs", "receipts bind project selection inputs provider target and results"],
    ),
    "product.event_streaming": product_spec(
        key="event_streaming",
        question="How can application and data teams publish and consume durable addressable event logs with explicit partition, ordering, retention, replay and progress guarantees?",
        users=["application_team", "data_engineer", "stream_operator", "consumer_owner"],
        harmed=["publisher", "consumer", "data_subject", "on_call_operator"],
        job="Declare, provision, publish, consume, retain, replay, rebalance and retire governed event channels.",
        outcomes=["versioned_channel_contract", "durable_ordered_event_log", "replayable_retention_cut", "consumer_progress_evidence"],
        negative="Does not own payload business meaning, source CDC cursor semantics, downstream processing state, notification semantics or business effect authority.",
        inside=["channels topics and partitions", "event envelope transport metadata", "ordering scope", "retention", "producer acknowledgement", "consumer groups and progress", "replay and rebalancing"],
        outside=["payload domain schema authority", "CDC snapshot stitching", "stream transformations", "alert notification delivery", "downstream business action"],
        values=["ChannelId", "ChannelEdition", "PartitionId", "TransportOffset", "ProducerSequence", "EventEnvelope", "OrderingScope", "RetentionProfile", "ConsumerGroupId", "ConsumerProgress"],
        entities=["ChannelDefinition", "PartitionLog", "ProducerSession", "ConsumerGroup", "ReplaySession"],
        aggregates=[{"root": "ChannelDefinition", "members": ["message_contract", "partitioning", "ordering", "retention", "lifecycle"], "consistency": "channel semantic changes create a new edition"}, {"root": "ConsumerGroup", "members": ["membership", "assignments", "progress", "rebalance_epoch"], "consistency": "progress is fenced by group and partition epoch"}],
        invariants=["transport metadata remains separate from payload meaning", "ordering promises are scoped and never implied globally", "offsets from different channel epochs are not silently comparable", "retention promises bound replayability", "acknowledgement is not downstream processing completion"],
        commands=["draft_channel", "bind_message_contract", "provision_channel", "publish_event", "acknowledge_publish", "join_consumer_group", "assign_partitions", "advance_consumer_progress", "start_replay", "rebalance_group", "change_retention", "seal_channel", "retire_channel"],
        events=["channel_drafted", "message_contract_bound", "channel_provisioned", "event_published", "publish_acknowledged", "consumer_group_joined", "partitions_assigned", "consumer_progress_advanced", "replay_started", "consumer_group_rebalanced", "retention_changed", "channel_sealed", "channel_retired"],
        states=["draft", "contract_bound", "provisioning", "active", "degraded", "rebalancing", "replay_active", "sealed", "retention_expired", "retired"],
        refusals=["message_contract_missing", "partition_key_invalid", "ordering_scope_unsupported", "retention_insufficient", "publish_epoch_stale", "progress_regression", "consumer_fence_stale", "replay_cut_expired", "provider_offer_unqualified", "resource_budget_exhausted"],
        services=["ChannelValidationService", "PartitionAssignmentService", "OrderingValidationService", "ConsumerProgressService", "ReplayPlanningService"],
        specifications=["ChannelProvisioningSpecification", "PublishAdmissionSpecification", "OrderingSpecification", "ProgressAdvanceSpecification", "ReplayEligibilitySpecification", "RetentionChangeSpecification"],
        policies=["when retention cannot satisfy declared replay horizon refuse provisioning", "when group epoch changes fence stale consumers", "when progress regresses refuse acknowledgement", "when a channel is sealed reject new publishes but permit bounded replay"],
        sagas=["ChannelProvisioningProcess", "ConsumerRebalanceProcess", "ReplaySessionProcess", "ChannelRetirementProcess"],
        reads=["ChannelCatalogView", "PartitionHealthView", "ProducerAcknowledgementView", "ConsumerLagView", "ReplayEligibilityView"],
        time=["event time and transport append time are distinct", "partition offset is ordered only within its epoch", "retention and replay horizons are explicit", "consumer progress recording time is independent"],
        neighbors=[("neighbor.message_schema", "customer_supplier", "bind exact payload schema editions"), ("neighbor.runtime_resource", "customer_supplier", "bind qualified broker storage and network offers"), ("product.dataflow_execution", "published_language", "publish channel and progress contracts"), ("neighbor.data_use_policy", "conformist_at_authority_gate", "apply retention and access obligations")],
        nfr=["bounded message and batch sizes", "backpressure", "fenced producer and consumer epochs", "durability and availability profiles explicit", "publish and progress receipts bind exact channel partition epoch and provider"],
    ),
    "product.operational_activation": product_spec(
        key="operational_activation",
        question="How can governed analytical records be mapped into authorized operational destination effects with explicit identity matching, purpose, idempotency, partial failure and receipts?",
        users=["data_activation_operator", "application_owner", "policy_owner", "operations_reviewer"],
        harmed=["destination_subject", "data_subject", "application_owner", "downstream_operator"],
        job="Define, review, authorize, execute, reconcile, compensate, suspend and retire analytical-to-operational activation mappings.",
        outcomes=["versioned_destination_mapping", "evidence_bound_record_match", "authorized_effect_intent", "reconciled_destination_receipt"],
        negative="Does not own analytical result meaning, enterprise identity truth, destination business rules, policy authority or the downstream outcome caused by a write.",
        inside=["destination object mappings", "record match evidence", "field and null mappings", "write modes", "effect intents", "authority grants", "idempotency", "attempts outcomes receipts and compensation"],
        outside=["analytical computation", "master identity authority", "destination domain invariants", "policy authorship", "human business approval", "downstream outcome attribution"],
        values=["ActivationId", "ActivationEdition", "SourceRecordRef", "DestinationObjectRef", "RecordMatch", "FieldMapping", "WriteMode", "EffectIntent", "AuthorityGrantRef", "IdempotencyKey", "DestinationReceipt"],
        entities=["ActivationDefinition", "ActivationRun", "EffectAttempt", "DestinationOutcome", "CompensationCase"],
        aggregates=[{"root": "ActivationDefinition", "members": ["source_contract", "destination_contract", "match_profile", "field_mapping", "write_policy", "lifecycle"], "consistency": "one edition fixes mapping and effect semantics"}, {"root": "ActivationRun", "members": ["input_cut", "effect_intents", "authority_decisions", "attempts", "outcomes", "receipts"], "consistency": "every attempted effect binds exact authority and idempotency evidence"}],
        invariants=["proposal is not authorization and authorization is not execution", "source record destination object and record match identities are distinct", "destination mapping is explicit and versioned", "unknown completion is never reported as success", "a destination receipt is not proof of intended business outcome"],
        commands=["draft_activation", "bind_source_contract", "bind_destination_contract", "compile_record_mapping", "submit_activation_review", "approve_activation", "open_activation_run", "propose_effect", "authorize_effect", "execute_effect", "record_destination_outcome", "reconcile_unknown_completion", "compensate_effect", "suspend_activation", "retire_activation"],
        events=["activation_drafted", "source_contract_bound", "destination_contract_bound", "record_mapping_compiled", "activation_review_requested", "activation_approved", "activation_run_opened", "effect_proposed", "effect_authorized", "effect_executed", "destination_outcome_recorded", "unknown_completion_reconciled", "effect_compensated", "activation_suspended", "activation_retired"],
        states=["draft", "bindings_resolved", "review_pending", "approved", "active", "effect_pending", "executing", "partially_completed", "reconciling", "compensating", "suspended", "retired"],
        refusals=["source_contract_unresolved", "destination_contract_unresolved", "match_key_ambiguous", "field_unrepresentable", "write_mode_unsupported", "purpose_forbidden", "authority_missing", "provider_offer_unqualified", "idempotency_key_missing", "destination_unavailable", "completion_unknown", "compensation_unsupported"],
        services=["ActivationMappingService", "RecordMatchingService", "EffectAuthorizationService", "EffectExecutionPort", "OutcomeReconciliationService"],
        specifications=["ActivationReadinessSpecification", "RecordMatchSpecification", "EffectAuthorizationSpecification", "IdempotencySpecification", "CompletionSpecification", "CompensationSpecification"],
        policies=["when record match is ambiguous open review and emit no effect", "when authority expires refuse execution", "when completion is unknown reconcile before retry", "when partial failure violates the accepted profile execute compensation or suspend"],
        sagas=["ActivationApprovalProcess", "ActivationRunProcess", "UnknownCompletionProcess", "EffectCompensationProcess"],
        reads=["ActivationCatalogView", "MappingDiffView", "RecordMatchEvidenceView", "EffectAttemptLedgerView", "DestinationOutcomeView", "CompensationStatusView"],
        time=["source cut time authorization validity attempt time and destination recording time are distinct", "idempotency scope and expiry are explicit", "unknown completion and reconciliation intervals are retained", "retirement preserves effect evidence"],
        neighbors=[("neighbor.semantic_result", "anti_corruption_layer", "import exact analytical result editions"), ("neighbor.identity_master", "customer_supplier", "obtain scoped match evidence without acquiring identity authority"), ("neighbor.data_use_policy", "conformist_at_authority_gate", "obtain purpose and effect decisions"), ("neighbor.destination_application", "anti_corruption_layer", "translate destination contracts outcomes and errors"), ("neighbor.audit_provenance", "published_language", "publish effect intent authority attempt outcome and compensation receipts")],
        nfr=["fail-closed authority", "bounded effect batches and rates", "idempotent attempts", "cooperative cancellation before irreversible boundary", "immutable effect and outcome receipts"],
    ),
}


LIBRARY_PRODUCTS = {
    "library.connection_contract": ["product.source_connectivity_control"],
    "library.connector_lifecycle": ["product.source_connectivity_control"],
    "library.source_cursor": ["product.source_replication_cdc"],
    "library.snapshot_stitch": ["product.source_replication_cdc"],
    "library.delivery_protocol": ["product.ingestion_delivery"],
    "library.schema_mapping": ["product.ingestion_delivery"],
    "library.workflow_state": ["product.pipeline_orchestration"],
    "library.schedule_backfill": ["product.pipeline_orchestration"],
    "library.dataflow_ir": ["product.dataflow_execution"],
    "library.event_time": ["product.dataflow_execution"],
    "library.checkpoint_contract": ["product.dataflow_execution"],
    "library.transform_manifest": ["product.batch_transform_build"],
    "library.materialization": ["product.batch_transform_build"],
    "library.event_metadata_envelope": ["product.event_streaming"],
    "library.retained_event_log": ["product.event_streaming"],
    "library.consumer_progress": ["product.event_streaming"],
    "library.activation_mapping": ["product.operational_activation"],
    "library.effect_receipt": ["product.operational_activation"],
}


COMPILER_MAPS = {
    "library.connection_contract": ["library.cp.connection_contract"],
    "library.connector_lifecycle": ["library.cp.connector_lifecycle"],
    "library.source_cursor": ["library.source.source_cursor"],
    "library.snapshot_stitch": ["library.pipeline.snapshot_handoff"],
    "library.delivery_protocol": ["library.pipeline.delivery_proof", "library.pipeline.sink_committer", "library.pipeline.recovery_planner"],
    "library.schema_mapping": ["library.schema_mapping.compiler", "library.schema_mapping.executor"],
    "library.workflow_state": ["library.pipeline.orchestration_kernel", "library.pipeline.task_lease"],
    "library.schedule_backfill": ["library.pipeline.schedule_calculus", "library.pipeline.retry_policy", "library.pipeline.recovery_planner"],
    "library.dataflow_ir": ["library.pipeline.graph_algebra", "library.pipeline.graph_validator", "library.pipeline.port_typechecker", "library.pipeline.logical_planner"],
    "library.event_time": ["library.pipeline.progress_algebra", "library.pipeline.window_trigger"],
    "library.checkpoint_contract": ["library.pipeline.checkpoint_coordinator", "library.pipeline.state_contracts", "library.pipeline.recovery_planner", "library.pipeline.sink_committer"],
    "library.transform_manifest": ["library.transform_definition.compiler", "library.transform_selection.closure"],
    "library.materialization": ["library.materialization.incremental_planner", "library.materialization.mutation_protocol", "library.transform_build.evidence"],
    "library.event_metadata_envelope": ["library.msg.envelope_kernel"],
    "library.retained_event_log": ["library.msg.retained_log_contract"],
    "library.consumer_progress": ["library.msg.consumer_progress_contract"],
    "library.activation_mapping": [
        "library.activation.destination_profile.compiler",
        "library.activation.mapping.compiler",
        "library.activation.mapping.evaluator",
    ],
    "library.effect_receipt": ["library.csp.decision.effect-port", "library.spt.policy_enforcer", "library.lpe.runtime-receipt-core"],
}


ABSTRACT_LIBRARY_PATCHES = {
    "library.transform_manifest": {
        "name": "Transformation definition compilation and selection closure",
        "class": "semantic_pure",
        "owner_ref": "semantic.transform_build",
        "provides": ["capability.transform_parse_select"],
        "types": [
            "ProjectSourceClosureRef", "PackageClosureRef", "ProjectEdition", "ResourceId",
            "ResolvedResourceGraph", "CompiledTransformationManifest", "ManifestDigest",
            "SelectorExpression", "SelectedTransformationClosure", "SelectionDigest",
        ],
        "operations": [
            "validate_project_closure", "parse_resource_declarations", "resolve_configuration",
            "resolve_resource_references", "bind_test_declarations", "compile_logical_definitions",
            "compare_manifest_editions", "parse_selector", "evaluate_selection_methods",
            "apply_graph_operators", "apply_set_and_exclusion_operators",
            "resolve_indirect_tests", "form_selected_closure",
        ],
        "decisions": [
            "exact project source and package closures", "resource namespace identity and kinds",
            "definition and query language editions", "macro and template editions",
            "configuration precedence and variables", "environment nondeterminism and secrets",
            "reference and external source resolution", "disabled and ephemeral resources",
            "test declaration binding", "manifest canonicalization and digest",
            "selector language and method vocabulary", "graph and set operator precedence",
            "exclusion and indirect tests", "state comparison and deferral",
            "empty selection and dependency closure", "finite compilation and selection budgets",
        ],
        "invariants": [
            "a manifest represents the complete exact resolved project while a selection is invocation specific",
            "every meaning-affecting input is explicit editioned and digest bound",
            "selection evaluates over exactly one manifest edition under explicit operator precedence",
            "package retrieval query-language ownership scheduling execution quality authority and target mutation remain outside",
        ],
        "refusals": [
            "project_closure_unbound", "package_closure_unbound", "resource_identity_collision",
            "definition_syntax_invalid", "configuration_precedence_ambiguous", "reference_unresolved",
            "dependency_cycle", "environment_capture_forbidden", "query_compiler_unbound",
            "selector_syntax_invalid", "selection_resource_unknown", "state_comparison_unbound",
            "deferred_resolution_ambiguous", "selection_closure_incomplete", "resource_budget_exceeded",
        ],
        "effect_boundary": "pure_no_io",
        "dependencies": [],
        "evidence_refs": ["evidence.dbt.build"],
    },
    "library.materialization": {
        "name": "Incremental materialization planning, mutation protocol and build evidence",
        "class": "policy_pure",
        "owner_ref": "semantic.transform_build",
        "provides": ["capability.materialization_plan", "capability.build_receipt"],
        "types": [
            "SelectedTransformationClosure", "InputCutSet", "TargetStateRef", "MaterializationState",
            "CoverageDelta", "IncrementalEligibility", "RestatementPlan", "SchemaTransitionPlan",
            "MaterializationPlan", "TargetMutationIntentSet", "TargetMutationEffectRequest",
            "ProviderMutationReceipt", "MutationReconciliationResult", "ResourceBuildResult",
            "TransformationBuildProvenance", "TransformationPublicationCandidate",
        ],
        "operations": [
            "validate_materialization_context", "classify_definition_change",
            "derive_incremental_eligibility", "compute_coverage_delta",
            "plan_late_data_and_lookback", "plan_restatement", "plan_schema_transition",
            "compile_materialization_plan", "validate_incremental_equivalence_claim",
            "lower_plan_to_mutation_intents", "validate_mutation_preconditions",
            "form_mutation_effect_request", "classify_mutation_receipt",
            "reconcile_unknown_mutation", "plan_cleanup_or_compensation",
            "classify_resource_result", "assemble_derivation_claims",
            "assemble_build_provenance", "form_publication_candidate",
        ],
        "decisions": [
            "materialization kind and exact input and target cuts", "full refresh and incremental eligibility",
            "progress frontier key grain and strategy", "append merge replace overwrite and delete semantics",
            "time partition microbatch coverage lookback and late data", "restatement backfill and logic change impact",
            "schema change deletion and retraction", "target capabilities isolation idempotency and budgets",
            "full versus incremental equivalence domain", "target mutation operations preconditions and transaction scope",
            "staging swap visibility retry unknown completion cancellation compensation and receipts",
            "build attempt and provider identity", "resource result precedence and imported tests",
            "derivation provenance publication candidate and reproducibility claims",
        ],
        "invariants": [
            "full and incremental execution are equivalent only over an explicit evidenced domain",
            "late data correction deletion retraction schema change restatement and backfill remain distinct",
            "the semantic boundary emits effect requests and reconciles receipts but performs no target I/O",
            "provider success materialization commit quality pass publication approval and business acceptance remain distinct",
            "unknown mutation completion is reconciled before retry and all attempts remain append only",
        ],
        "refusals": [
            "selected_closure_unbound", "input_cut_unbound", "target_state_unbound",
            "target_capability_missing", "incremental_eligibility_unproved", "unique_key_invalid",
            "coverage_incomparable", "late_data_policy_missing", "restatement_range_invalid",
            "schema_change_unhandled", "retraction_unsupported", "incremental_equivalence_unproved",
            "expected_target_state_missing", "idempotency_scope_missing", "effect_authority_missing",
            "provider_receipt_invalid", "completion_unknown", "reconciliation_evidence_insufficient",
            "provenance_incomplete", "publication_candidate_incomplete", "resource_budget_exceeded",
        ],
        "effect_boundary": "pure_effect_intents",
        "dependencies": ["library.transform_manifest"],
        "evidence_refs": ["evidence.dbt.build", "evidence.dbt.incremental"],
    },
    "library.schema_mapping": {
        "name": "Carrier schema mapping and translation",
        "class": "semantic_pure",
        "owner_ref": "semantic.ingestion_delivery",
        "provides": ["capability.schema_mapping"],
        "types": [
            "SourceSchemaClosureRef", "TargetSchemaClosureRef", "CarrierProfilePair",
            "FieldMappingDeclaration", "CompiledSchemaMapping", "MappingResidual",
            "AcceptedMappingPlan", "SourceRecord", "SourceChangeEnvelope",
            "TranslationResult", "TranslationTrace",
        ],
        "operations": [
            "validate_mapping_context", "derive_field_candidates", "compile_mapping_plan",
            "evaluate_mapping_totality", "classify_mapping_residuals",
            "validate_loss_acceptance", "evaluate_schema_evolution_impact",
            "translate_record", "translate_record_batch", "translate_change_envelope",
            "validate_translation_result",
        ],
        "decisions": [
            "exact source and target schema closures", "carrier profiles",
            "field identity and path matching", "mapping cardinality",
            "logical and physical type relations", "null missing empty and default distinction",
            "unknown fields enums and union branches", "numeric decimal and floating value domains",
            "temporal kind precision offset zone DST and leap seconds",
            "text encoding Unicode normalization and collation",
            "collection ordering and duplicate keys", "identity and key preservation",
            "change operation delete and tombstone semantics", "loss taxonomy and acceptance",
            "schema evolution invalidation", "determinism and finite resource budgets",
        ],
        "invariants": [
            "source target mapping and execution identities are explicit and edition bound",
            "loss ambiguity default construction and runtime residuals are attributable",
            "mapping compilation and execution perform no ambient I/O",
            "schema mapping never acquires ontology reference-data formula unit currency delivery or acceptance authority",
        ],
        "refusals": [
            "schema_closure_unbound", "carrier_profile_unbound", "field_identity_ambiguous",
            "mapping_cardinality_unsupported", "type_relation_unrepresentable",
            "null_missing_default_ambiguous", "unknown_value_posture_missing",
            "numeric_policy_missing", "temporal_policy_missing", "text_policy_missing",
            "identity_field_loss_unaccepted", "change_operation_loss_unaccepted",
            "loss_decision_missing", "schema_evolution_impact_unknown",
            "mapping_plan_unaccepted", "source_record_schema_mismatch",
            "target_constraint_violated", "resource_budget_exceeded",
        ],
        "effect_boundary": "pure_no_io",
        "dependencies": [],
        "evidence_refs": ["evidence.airbyte.protocol"],
    },
    "library.activation_mapping": {
        "name": "Destination-profile compilation, activation-plan compilation and pure proposal evaluation",
        "class": "semantic_pure",
        "owner_ref": "semantic.operational_activation",
        "provides": ["capability.activation_mapping"],
        "types": [
            "DestinationContractClosureRef", "DestinationActivationProfile",
            "SourceActivationContractRef", "ActivationMappingDeclaration",
            "CompiledRecordMatchPlan", "CompiledActivationFieldPlan",
            "CompiledActivationOperationPlan", "ActivationMappingResidualSet",
            "ActivationMappingPlan", "AcceptedActivationMappingPlanRef",
            "SourceRecordOccurrence", "ExternalMatchObservationSet",
            "ActivationRecordMatchResult", "ProposedDestinationOperation",
            "ActivationIdempotencyMaterial", "ActivationAuthorityRequest",
            "ActivationEffectProposal", "ActivationProposalBatch",
        ],
        "operations": [
            "validate_destination_contract_closure", "extract_destination_objects_and_actions",
            "extract_match_and_field_capabilities", "extract_write_and_failure_semantics",
            "extract_authority_requirements", "compile_destination_activation_profile",
            "compare_destination_profiles", "validate_activation_mapping_context",
            "compile_record_match_plan", "compile_field_mapping_plan",
            "compile_operation_plan", "classify_mapping_residuals",
            "validate_loss_acceptance", "compile_activation_mapping_plan",
            "evaluate_mapping_compatibility", "validate_evaluation_context",
            "evaluate_record_match", "translate_activation_fields",
            "derive_activation_operation", "derive_idempotency_material",
            "form_authority_request", "form_activation_effect_proposal",
            "evaluate_activation_batch",
        ],
        "decisions": [
            "exact provider contract offer destination and capability editions",
            "destination objects actions identifiers fields constraints and authority requirements",
            "write delete patch batch atomicity partial-failure idempotency concurrency and receipt semantics",
            "source and destination record identity and match keys",
            "match relation cardinality uniqueness nullability and external evidence requirements",
            "field correspondence type translation constants null missing empty default redaction and omission",
            "create update upsert add remove clear archive delete patch replace and merge",
            "change classification reprocessing ordering loss purpose compatibility and plan digest",
            "match-evidence issuer freshness and zero one many posture",
            "proposal identity idempotency material authority request batch partitioning diagnostics and budgets",
        ],
        "invariants": [
            "provider contract profile mapping plan source occurrence proposal authorization execution receipt and business outcome are distinct",
            "source identity destination identity and externally issued record-match evidence are distinct",
            "null missing empty default clear archive and delete never collapse without an exact declared correspondence",
            "ambiguous record matching emits no effect proposal",
            "the evaluator performs no lookup or provider I/O and emits a non-authoritative proposal plus authority request",
            "unknown completion retry compensation receipt reconciliation and outcome acceptance remain outside this library",
        ],
        "refusals": [
            "destination_contract_unbound", "provider_offer_unbound", "capability_profile_stale",
            "source_contract_unbound", "mapping_declaration_incomplete",
            "destination_object_unsupported", "match_key_ambiguous",
            "match_cardinality_unsupported", "match_evidence_requirement_missing",
            "field_unrepresentable", "null_semantics_ambiguous",
            "write_mode_unsupported", "delete_semantics_unsupported",
            "idempotency_basis_missing", "partial_failure_posture_missing",
            "loss_unaccepted", "purpose_requirement_missing",
            "mapping_plan_unaccepted", "match_evidence_stale",
            "match_evidence_issuer_untrusted", "no_destination_match",
            "ambiguous_destination_match", "authority_request_incomplete",
            "proposal_nondeterministic", "resource_budget_exceeded",
        ],
        "effect_boundary": "pure_effect_proposals",
        "dependencies": ["library.schema_mapping"],
        "evidence_refs": ["evidence.hightouch.sync", "evidence.openapi.spec"],
    },
}


STREAMING_LIBRARY_SPLIT = [
    {
        "library_id": "library.event_metadata_envelope",
        "name": "Event metadata envelope",
        "class": "semantic_pure",
        "owner_ref": "semantic.event_envelope",
        "provides": ["capability.event_envelope"],
        "types": ["MessageEnvelope", "EnvelopeProfile", "EnvelopeProjection", "EnvelopeResidual"],
        "operations": ["compose_envelope", "validate_envelope", "project_envelope"],
        "decisions": ["envelope profile", "required attributes", "extensions", "event time", "payload binding", "projection loss"],
        "invariants": ["event metadata remains separate from payload meaning, transport position, ordering and delivery evidence"],
        "refusals": ["message_contract_missing", "envelope_profile_unsupported", "projection_loss_unaccepted"],
        "effect_boundary": "pure_no_io",
        "dependencies": [],
        "evidence_refs": ["evidence.cloudevents.spec", "evidence.asyncapi.spec"],
    },
    {
        "library_id": "library.retained_event_log",
        "name": "Retained event log contract",
        "class": "semantic_pure",
        "owner_ref": "semantic.retained_log",
        "provides": ["capability.event_log"],
        "types": ["RetainedLog", "LogEpoch", "LogPartition", "LogPosition", "LogRange", "RetentionPolicy", "AppendIntent", "FetchRangeIntent"],
        "operations": ["validate_log_contract", "compare_position", "form_append_intent", "form_fetch_intent", "evaluate_retention"],
        "decisions": ["partitioning", "ordering scope", "acknowledgement", "retention", "compaction", "truncation", "replay", "epoch transition"],
        "invariants": ["log positions are scoped by log edition epoch and partition", "publication acknowledgement is not reader visibility or downstream completion"],
        "refusals": ["ordering_scope_unsupported", "retention_insufficient", "position_incomparable", "range_expired"],
        "effect_boundary": "pure_effect_intents",
        "dependencies": ["library.event_metadata_envelope"],
        "evidence_refs": ["evidence.kafka.protocol"],
    },
    {
        "library_id": "library.consumer_progress",
        "name": "Consumer progress contract",
        "class": "semantic_pure",
        "owner_ref": "semantic.consumer_progress",
        "provides": ["capability.consumer_progress"],
        "types": ["ConsumerGroup", "GroupGeneration", "AssignmentEpoch", "PartitionAssignment", "TransportProgress", "CommitProgressIntent", "RebalanceOutcome"],
        "operations": ["validate_assignment", "compare_progress", "form_commit_intent", "apply_rebalance", "validate_resume"],
        "decisions": ["assignment", "commit boundary", "rebalance", "fencing", "reset", "retention", "delivery posture"],
        "invariants": ["transport progress remains separate from source cursor checkpoint handler completion and business effect", "stale generations cannot commit progress"],
        "refusals": ["generation_stale", "assignment_revoked", "progress_regression", "commit_beyond_acknowledged"],
        "effect_boundary": "pure_effect_intents",
        "dependencies": ["library.retained_event_log"],
        "evidence_refs": ["evidence.kafka.protocol"],
    },
]

STREAMING_CAPABILITY = {
    "artifact_id": "capability.event_envelope",
    "kind": "capability",
    "name": "Event metadata envelope",
    "definition": "Compose, validate and loss-account for provider-neutral event metadata separately from payload and transport semantics.",
    "semantic_owner_ref": "semantic.event_envelope",
    "adoption_unit": False,
    "operated": False,
    "status": "candidate",
    "evidence_refs": ["evidence.cloudevents.spec", "evidence.asyncapi.spec"],
}

STREAMING_ENVELOPE_REQUIREMENT = {
    "requirement_id": "requirement.streaming.envelope",
    "consumer_ref": "product.event_streaming",
    "capability_ref": "capability.event_envelope",
    "binding_phase": "authoring_time",
    "minimum_qualified_offers": 1,
    "refusal": "event_envelope_contract_unresolved",
    "status": "unbound",
}

STREAMING_ENVELOPE_RELATION = {
    "relation_id": "relation.streaming.envelope",
    "from_ref": "product.event_streaming",
    "predicate": "offers",
    "to_ref": "capability.event_envelope",
    "binding_phase": "authoring",
}

STREAMING_OWNERSHIP = [
    {
        "meaning_id": "meaning.event_envelope_metadata",
        "owner_ref": "semantic.event_envelope",
        "invariant": "The envelope owner governs provider-neutral event metadata, not payload truth, log position, delivery or business acceptance.",
        "must_not_be_owned_by": ["semantic.event_transport", "semantic.change_capture", "suite.data_integration"],
    },
    {
        "meaning_id": "meaning.retained_log_position",
        "owner_ref": "semantic.retained_log",
        "invariant": "The retained-log owner governs log identity, epoch, partition, position and retained ranges, not source cursors or consumer progress.",
        "must_not_be_owned_by": ["semantic.event_transport", "semantic.change_capture", "semantic.consumer_progress"],
    },
    {
        "meaning_id": "meaning.consumer_transport_progress",
        "owner_ref": "semantic.consumer_progress",
        "invariant": "The consumer-group owner governs assignment-fenced transport progress, not source capture, operator checkpoints or business effects.",
        "must_not_be_owned_by": ["semantic.event_transport", "semantic.change_capture", "semantic.dataflow_execution"],
    },
]

STREAMING_SEMANTIC_ARTIFACTS = [
    {
        "artifact_id": "semantic.event_envelope",
        "kind": "semantic_contract",
        "name": "Event envelope semantics",
        "definition": "Owns provider-neutral event metadata identity, attributes, extensions, payload binding and loss-accounted projection; imports its published language from msg.envelope.",
        "semantic_owner_ref": None,
        "adoption_unit": False,
        "operated": False,
        "status": "candidate",
        "evidence_refs": ["evidence.cloudevents.spec", "evidence.asyncapi.spec"],
    },
    {
        "artifact_id": "semantic.retained_log",
        "kind": "semantic_contract",
        "name": "Retained event log semantics",
        "definition": "Owns provider-neutral log identity, edition, epoch, partition, position, retained range, ordering scope and retention; imports its published language from msg.retained_log.",
        "semantic_owner_ref": None,
        "adoption_unit": False,
        "operated": False,
        "status": "candidate",
        "evidence_refs": ["evidence.kafka.protocol"],
    },
    {
        "artifact_id": "semantic.consumer_progress",
        "kind": "semantic_contract",
        "name": "Consumer progress semantics",
        "definition": "Owns provider-neutral group generation, assignment fence, transport progress, commit boundary, rebalance and reset; imports its published language from msg.consumer_group.",
        "semantic_owner_ref": None,
        "adoption_unit": False,
        "operated": False,
        "status": "candidate",
        "evidence_refs": ["evidence.kafka.protocol"],
    },
]


AUTOMATION = {
    "default": "DETERMINISTIC_CORE_ONLY",
    "postures": ["PROHIBITED", "OPTIONAL", "REQUIRED_BY_INTENT", "UNDETERMINED"],
    "law": "Models and agents may propose typed configurations or diagnoses but never own movement semantics, qualification, authority, effects, receipts or acceptance.",
    "hard_work_law": "Automation never replaces source research, vocabulary, invariant and lifecycle definition, conformance, provider qualification or domain acceptance.",
}


def strip_managed(source: dict[str, Any]) -> dict[str, Any]:
    source = json.loads(json.dumps(source))
    for key in ("ddd_dossiers", "binding_maps", "binding_gaps"):
        source.pop(key, None)
    for row in source.get("artifacts", []):
        if row.get("artifact_id") in SPECS:
            for field in PRODUCT_FIELDS:
                row.pop(field, None)
    for row in source.get("libraries", []):
        row.pop("product_ref", None)
        row.pop("product_refs", None)
    managed_library_ids = {"library.event_envelope"} | {row["library_id"] for row in STREAMING_LIBRARY_SPLIT}
    source["libraries"] = [row for row in source.get("libraries", []) if row.get("library_id") not in managed_library_ids]
    managed_artifact_ids = {STREAMING_CAPABILITY["artifact_id"]} | {row["artifact_id"] for row in STREAMING_SEMANTIC_ARTIFACTS}
    source["artifacts"] = [row for row in source.get("artifacts", []) if row.get("artifact_id") not in managed_artifact_ids]
    source["requirements"] = [row for row in source.get("requirements", []) if row.get("requirement_id") != STREAMING_ENVELOPE_REQUIREMENT["requirement_id"]]
    source["relations"] = [row for row in source.get("relations", []) if row.get("relation_id") != STREAMING_ENVELOPE_RELATION["relation_id"]]
    managed_meaning_ids = {row["meaning_id"] for row in STREAMING_OWNERSHIP}
    source["ownership"] = [row for row in source.get("ownership", []) if row.get("meaning_id") not in managed_meaning_ids]
    return source


def dossier(product_ref: str, spec: dict[str, Any]) -> dict[str, Any]:
    roots = [row["root"] for row in spec["aggregates"]]
    key_pascal = pascal(spec["key"])
    application_services = [pascal(command) + "UseCase" for command in spec["commands"][:6]]
    return {
        "dossier_id": f"ddd.movement.{spec['key']}",
        "product_ref": product_ref,
        "status": "candidate_not_ratified",
        "product_truth": {
            "sovereign_question": spec["question"], "users": spec["users"],
            "harmed_parties": spec["harmed"], "jobs": [spec["job"]],
            "measurable_outcomes": spec["outcomes"], "negative_mission": spec["negative"],
        },
        "strategic_and_tactical_ddd": {
            "domain_vision_statement": spec["question"].replace("How can ", "Own how ").rstrip("?"),
            "subdomain_classification": "core_horizontal_data_movement_product",
            "bounded_context_boundary": {"inside": spec["inside"], "outside": spec["outside"]},
            "ubiquitous_language_policy": "Every named movement identity, state, cut, acknowledgement, authority and receipt has one meaning inside this context; provider and neighboring homonyms cross named ACLs.",
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
            "application_services": application_services,
            "repositories": [root + "Repository" for root in roots],
            "factories": [root + "Factory" for root in roots] + [key_pascal + "EditionFactory"],
            "specifications": spec["specifications"],
            "state_machine": {"states": spec["states"], "transition_policy": "Only named commands satisfying aggregate invariants may emit the corresponding past-tense event; unknown completion remains explicit."},
            "policies_and_reactions": spec["policies"],
            "sagas_and_process_managers": spec["sagas"],
            "read_models_and_projections": spec["reads"],
            "integration_event_policy": "Only minimized, editioned lifecycle and evidence events cross the boundary; internal planning, provider and review events remain product-local.",
            "concurrency_and_idempotency": ["optimistic aggregate edition", "idempotency key per command and effect attempt", "fenced provider and run occurrences", "append-only attempt and receipt identity", "unknown completion requires reconciliation before retry"],
            "time_model": spec["time"],
            "event_storming_swimlanes": spec["users"] + ["runtime_provider", "external_authority"],
            "nonfunctional_laws": spec["nfr"] + ["provider identity cannot change semantic meaning", "removing model and agent extensions preserves the complete deterministic core"],
        },
    }


def enrich(source: dict[str, Any]) -> dict[str, Any]:
    source = strip_managed(source)
    source["libraries"].extend(json.loads(json.dumps(STREAMING_LIBRARY_SPLIT)))
    source["artifacts"].append(json.loads(json.dumps(STREAMING_CAPABILITY)))
    source["artifacts"].extend(json.loads(json.dumps(STREAMING_SEMANTIC_ARTIFACTS)))
    source["requirements"].append(json.loads(json.dumps(STREAMING_ENVELOPE_REQUIREMENT)))
    source["relations"].append(json.loads(json.dumps(STREAMING_ENVELOPE_RELATION)))
    source["ownership"].extend(json.loads(json.dumps(STREAMING_OWNERSHIP)))
    artifacts_by_id = {row["artifact_id"]: row for row in source["artifacts"]}
    artifacts_by_id["semantic.event_transport"]["definition"] = "Owns the Event Streaming product's channel lifecycle composition while importing envelope, retained-log and consumer-progress meanings from their separate semantic contracts."
    artifacts = {row["artifact_id"]: row for row in source["artifacts"]}
    for product_ref, spec in SPECS.items():
        artifacts[product_ref].update({
            "sovereign_question": spec["question"], "users": spec["users"],
            "harmed_parties": spec["harmed"], "jobs": [spec["job"]],
            "outcomes": spec["outcomes"], "negative_mission": spec["negative"],
            "lifecycle_states": spec["states"], "commands": spec["commands"],
            "events": spec["events"], "invariants": spec["invariants"],
            "refusals": spec["refusals"], "automation_modality": AUTOMATION,
        })
    for row in source["libraries"]:
        if row["library_id"] in ABSTRACT_LIBRARY_PATCHES:
            row.update(json.loads(json.dumps(ABSTRACT_LIBRARY_PATCHES[row["library_id"]])))
        row["product_refs"] = LIBRARY_PRODUCTS[row["library_id"]]

    maps = []
    gaps = []
    for library_ref, concrete_refs in COMPILER_MAPS.items():
        suffix = library_ref.removeprefix("library.")
        gap_ref = None
        disposition = "structurally_projected_unqualified"
        if concrete_refs is None:
            gap_ref = f"gap.movement.binding.{suffix}"
            concrete_refs = []
            disposition = "missing_exact_compiler_library_contract"
            gaps.append({
                "gap_id": gap_ref,
                "product_refs": LIBRARY_PRODUCTS[library_ref],
                "abstract_library_ref": library_ref,
                "blocking": True,
                "statement": f"No exact compiler contribution currently owns the full {library_ref} contract without semantic loss or transferred authority.",
                "closure_evidence": "Add one semantic-owner compiler library with exact types, operations, decisions, invariants, refusals, effects and executable conformance oracles; provider qualification remains separate.",
            })
        maps.append({
            "binding_map_id": f"binding.movement.{suffix}",
            "product_refs": LIBRARY_PRODUCTS[library_ref],
            "abstract_library_ref": library_ref,
            "concrete_library_refs": concrete_refs,
            "compiler_disposition": disposition,
            "gap_ref": gap_ref,
            "portable_offer": False,
        })
    source["binding_maps"] = maps
    source["binding_gaps"] = gaps
    source["ddd_dossiers"] = [dossier(product_ref, spec) for product_ref, spec in SPECS.items()]
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
            print("ERROR movement source.json enrichment is stale")
            return 1
        print("CHECK PASS movement source enrichment")
        return 0
    SOURCE.write_bytes(expected)
    print("BUILD PASS movement source enrichment")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
