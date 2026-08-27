#!/usr/bin/env python3
"""Add product truth, full DDD dossiers and exact product attribution to the model slice.

Predictive methods are ordinary declared computational methods.  Generative models and agents are
confined to one optional, removable, non-authoritative extension product; they do not rename or
weaken any deterministic contract in the other five products.
"""

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


PRODUCT_LIBRARIES = {
    "product.model_lifecycle": [
        "library.model.experiment_ledger", "library.model.training_contract",
        "library.model.training_attempt", "library.model.artifact_contract",
        "library.model.lifecycle_state", "library.model.registry_port", "library.model.portability",
    ],
    "product.feature_platform": [
        "library.model.feature_contract", "library.model.feature_historical_retrieval",
        "library.model.feature_materialization", "library.model.feature_online_retrieval",
    ],
    "product.online_inference": [
        "library.model.inference_contract", "library.model.inference_routing",
        "library.model.inference_receipt",
    ],
    "product.model_assurance": [
        "library.model.assurance_evaluation", "library.model.assurance_validation",
        "library.model.assurance_monitoring", "library.model.review_case",
        "library.model.evidence_report",
    ],
    "product.decision_automation": [
        "library.model.decision_contract", "library.model.decision_table",
        "library.model.decision_runtime", "library.model.decision_ledger",
        "library.model.decision_authority_bridge",
    ],
    "product.optional_model_extension": [
        "library.model.extension_contract", "library.model.extension_invocation",
        "library.model.generated_proposal",
    ],
}


SPECS: dict[str, dict[str, Any]] = {
    "product.model_lifecycle": {
        "slug": "model_lifecycle", "classification": "core_horizontal_predictive_model_engineering_product",
        "vision": "Own the reproducible predictive-task-to-retired-model-edition lifecycle while keeping methods, attempts, artifacts, evidence, approval, deployment and outcomes distinct.",
        "question": "For an exact predictive task, data cut, feature/label contract and training specification, what fitted artifact and model edition was produced, evidenced, governed, promoted, superseded or retired without claiming deployment, prediction quality or decision authority?",
        "users": ["model_developer", "statistician", "data_scientist", "model_owner", "model_reviewer", "registry_operator", "platform_operator", "auditor"],
        "harmed": ["represented_data_subject", "decision_affected_party", "operator", "model_consumer", "source_owner", "risk_owner"],
        "jobs": ["declare predictive task and estimand", "seal training specification and data cut", "execute traceable attempts", "assemble complete fitted artifacts", "register immutable editions", "govern lifecycle transitions", "export with explicit conversion residuals", "retire and revoke editions"],
        "outcomes": ["sealed_training_spec", "replayable_attempt_manifest", "complete_fitted_artifact", "immutable_model_edition", "evidence_bound_transition", "portable_carrier_with_residuals", "retirement_and_revocation_receipt"],
        "negative": "Does not own source facts, feature computation, generic experiment causal conclusions, runtime compute, assurance independence, deployment state, inference, business decisions, effects, outcomes or provider qualification.",
        "states": ["draft", "task_bound", "data_contract_bound", "training_spec_sealed", "queued", "training", "attempt_failed", "artifact_pending", "artifact_verified", "registered", "validation_pending", "candidate", "approved", "rejected", "promoted", "deprecated", "revoked", "retired", "superseded"],
        "commands": ["open_model_project", "bind_predictive_task", "bind_feature_label_and_data_cut", "seal_training_spec", "start_training_attempt", "record_attempt_receipt", "assemble_fitted_artifact", "verify_artifact_manifest", "register_model_edition", "request_lifecycle_transition", "approve_or_refuse_transition", "export_model_carrier", "deprecate_model_edition", "revoke_model_edition", "retire_model_edition"],
        "events": ["model_project_opened", "predictive_task_bound", "feature_label_and_data_cut_bound", "training_spec_sealed", "training_attempt_started", "training_attempt_completed_or_failed", "fitted_artifact_assembled", "artifact_manifest_verified", "model_edition_registered", "lifecycle_transition_requested", "lifecycle_transition_approved_or_refused", "model_carrier_exported", "model_edition_deprecated", "model_edition_revoked", "model_edition_retired"],
        "invariants": ["predictive task method family algorithm training specification attempt fitted artifact model edition registry alias validation verdict approval deployment and prediction are distinct", "every attempt binds immutable code environment parameters seed data feature and label cuts", "retry creates a new attempt identity", "weights alone are not a complete fitted artifact", "registered model editions are immutable", "alias mutation never changes edition identity or lifecycle truth", "transition evidence and authority are explicit and revocable", "serialization parse success is not numerical or semantic equivalence", "retirement and revocation propagate without deleting history", "a model edition never authorizes deployment or business action"],
        "refusals": ["predictive_task_ambiguous", "target_or_label_contract_missing", "data_cut_unclosed", "leakage_status_unknown", "training_spec_incomplete", "runtime_unbound", "attempt_identity_conflict", "artifact_manifest_incomplete", "digest_conflict", "unsupported_serialization", "equivalence_unproved", "transition_evidence_missing", "transition_authority_missing", "illegal_lifecycle_transition", "edition_revoked", "deployment_or_effect_authority_requested"],
        "inside": ["predictive task and estimand reference", "training specification and attempt identity", "feature label split data and code cuts", "algorithm estimator hyperparameter seed and environment binding", "artifact manifest digest signature and dependency closure", "model edition registry alias and lifecycle state", "evidence-bound promotion deprecation revocation and retirement", "model-carrier export and conversion residuals"],
        "outside": ["source-domain fact ownership", "feature materialization and serving", "runtime scheduling and resources", "independent evaluation and monitoring", "deployment and traffic routing", "inference occurrence", "decision and effect authority", "realized outcome ownership", "provider qualification"],
        "language": ["PredictiveTask", "Estimand", "TrainingSpec", "DataCut", "FeatureCut", "LabelCut", "SplitPlan", "EstimatorSpec", "TrainingAttempt", "FittedArtifact", "ArtifactManifest", "ModelEdition", "RegistryAlias", "LifecycleTransition", "ModelCarrier", "ConversionResidual"],
        "values": ["ModelProjectId", "PredictiveTaskRef", "TrainingSpecDigest", "DataCutRef", "FeatureCutRef", "LabelCutRef", "CodeDigest", "EnvironmentDigest", "Seed", "AttemptId", "ArtifactDigest", "ModelEditionId", "AliasName", "TransitionPolicyEdition", "CarrierEdition"],
        "entities": ["ModelProject", "TrainingSpecification", "TrainingAttempt", "FittedArtifact", "ModelEdition", "AliasBinding", "LifecycleTransitionRequest", "CarrierExport"],
        "roots": ["ModelProject", "TrainingAttempt", "FittedArtifact", "ModelEdition", "LifecycleTransitionRequest"],
        "services": ["TrainingSpecificationService", "AttemptIdentityService", "ArtifactAssemblyService", "EditionRegistrationService", "LifecyclePolicyService", "CarrierConversionService", "RevocationPropagationService"],
        "neighbors": [("context.predictive_method_catalog", "published_language"), ("product.feature_platform", "customer_supplier"), ("product.runtime_resource_control", "customer_supplier"), ("product.model_assurance", "customer_supplier"), ("product.online_inference", "open_host_service"), ("product.lineage_provenance", "published_language"), ("context.authority_policy", "customer_supplier")],
        "time": "Separate source event, availability, recording, feature-cut, label-maturity, attempt-start/end, artifact-created, evidence-valid, transition-effective, revocation and retirement times; preserve bitemporal registry history.",
    },
    "product.feature_platform": {
        "slug": "feature_platform", "classification": "core_horizontal_feature_definition_and_serving_product",
        "vision": "Own governed feature definitions and temporally correct historical and online retrieval without acquiring source-fact or model authority.",
        "question": "For an entity set, feature edition, purpose and exact information time, what feature values can be computed, materialized and retrieved with point-in-time correctness, freshness, lineage and partiality explicit?",
        "users": ["feature_author", "model_developer", "analyst", "data_engineer", "online_service_owner", "feature_operator", "data_steward", "assurance_reviewer"],
        "harmed": ["represented_data_subject", "source_owner", "model_consumer", "decision_affected_party", "operator", "privacy_rights_holder"],
        "jobs": ["define entity-bound features", "bind source and transformation contracts", "reconstruct historical point-in-time cuts", "materialize versioned values", "serve online values", "evaluate freshness and parity", "backfill and reconcile", "deprecate features safely"],
        "outcomes": ["editioned_feature_definition", "leakage_safe_historical_cut", "materialization_receipt", "freshness_scoped_online_result", "training_serving_parity_evidence", "lineage_and_quality_residual", "safe_feature_deprecation"],
        "negative": "Does not own source business facts, entity identity truth, vector similarity, general transformation orchestration, predictive task meaning, model lifecycle, decision authority or downstream outcome truth.",
        "states": ["draft", "source_bound", "time_semantics_bound", "validated", "published", "backfill_pending", "materializing", "online", "degraded", "reconciling", "deprecated", "disabled", "revoked", "retired"],
        "commands": ["open_feature_definition", "bind_entity_and_source", "bind_temporal_semantics", "validate_feature_definition", "publish_feature_edition", "request_historical_cut", "plan_point_in_time_join", "start_materialization", "record_materialization_receipt", "retrieve_online_features", "evaluate_freshness", "compare_training_serving_parity", "reconcile_feature_state", "deprecate_feature_edition", "revoke_feature_edition"],
        "events": ["feature_definition_opened", "entity_and_source_bound", "temporal_semantics_bound", "feature_definition_validated", "feature_edition_published", "historical_cut_requested", "point_in_time_join_planned", "materialization_started", "materialization_receipt_recorded", "online_features_retrieved", "freshness_evaluated", "training_serving_parity_compared", "feature_state_reconciled", "feature_edition_deprecated", "feature_edition_revoked"],
        "invariants": ["feature definition source fact feature value historical cut materialized value online read and embedding entry are distinct", "feature definitions reference rather than own source-domain meaning", "event availability recording and processing times never collapse", "historical joins exclude information unavailable at each observation time", "latest online value is not historical point-in-time truth", "materialization is derived cache state and never source truth", "freshness completeness correctness and parity are separate findings", "missing stale denied and not-applicable remain distinct", "backfill preserves editions and correction policy", "feature retrieval never grants use purpose or decision authority"],
        "refusals": ["entity_identity_unbound", "source_contract_missing", "feature_definition_invalid", "availability_time_unknown", "future_information_risk", "join_tie_break_ambiguous", "late_data_policy_missing", "materialization_cursor_conflict", "stale_value", "partial_result", "purpose_denied", "parity_unproved", "lineage_missing", "feature_revoked", "vector_search_contract_requested"],
        "inside": ["feature definition and edition identity", "entity-key and source references", "event availability recording and TTL semantics", "historical point-in-time join plans and residuals", "materialization cursors backfills retries and reconciliation", "online lookup partiality freshness and deadlines", "training-serving parity evidence", "feature publication deprecation disablement and revocation"],
        "outside": ["source fact and master identity ownership", "generic pipelines and compute scheduling", "vector embeddings and similarity indexes", "predictive task training and model registry", "inference deployment", "business decision or effect authority", "provider qualification"],
        "language": ["FeatureDefinition", "FeatureEdition", "EntityKey", "SourceFactRef", "EventTime", "AvailabilityTime", "RecordingTime", "HistoricalFeatureRequest", "HistoricalFeatureCut", "PointInTimeJoin", "MaterializationCursor", "OnlineFeatureRead", "FreshnessReceipt", "ParityFinding"],
        "values": ["FeatureId", "FeatureEditionId", "EntityTypeRef", "EntityKey", "SourceContractRef", "TransformationDigest", "TimeSemanticsEdition", "TTL", "FreshnessBound", "MaterializationCursor", "HistoricalCutRef", "RequestDeadline"],
        "entities": ["FeatureDefinition", "FeatureEdition", "HistoricalFeatureCut", "MaterializationRun", "OnlineFeatureRead", "ParityReview"],
        "roots": ["FeatureDefinition", "FeatureEdition", "HistoricalFeatureCut", "MaterializationRun", "OnlineFeatureRead"],
        "services": ["FeatureDefinitionService", "TemporalJoinPlanningService", "MaterializationPlanningService", "FreshnessEvaluationService", "ParityEvaluationService", "FeatureReconciliationService", "FeatureRetirementService"],
        "neighbors": [("context.source_truth", "anti_corruption_layer"), ("context.master_identity", "customer_supplier"), ("product.pipeline_dataflow", "customer_supplier"), ("product.model_lifecycle", "open_host_service"), ("product.online_inference", "open_host_service"), ("product.search_index_serving", "separate_ways"), ("product.lineage_provenance", "published_language")],
        "time": "Separate source event, source availability, recording, correction, historical observation, materialization, online read, freshness-evaluation and expiry times; retain bitemporal feature editions and values where corrections matter.",
    },
    "product.online_inference": {
        "slug": "online_inference", "classification": "core_horizontal_predictive_inference_serving_product",
        "vision": "Own version-pinned, bounded and observable predictive inference occurrences without converting readiness or predictions into validation, decisions or effects.",
        "question": "For a qualified model deployment revision and typed request, what prediction occurrence was routed, executed and observed under declared latency, resource, rollout and receipt contracts?",
        "users": ["application_developer", "model_deployer", "service_operator", "reliability_engineer", "model_owner", "assurance_monitor", "auditor"],
        "harmed": ["request_subject", "decision_affected_party", "application_consumer", "operator", "risk_owner", "privacy_rights_holder"],
        "jobs": ["declare deployment revision", "validate request and response contracts", "route traffic by editioned policy", "execute bounded inference", "record prediction occurrence", "observe latency and failures", "roll back safely", "reconcile uncertain completion"],
        "outcomes": ["version_pinned_deployment", "typed_inference_contract", "route_receipt", "bounded_prediction_occurrence", "latency_and_completion_receipt", "safe_canary_or_rollback", "reconciled_uncertain_completion"],
        "negative": "Does not train, validate, approve or register models; define features; infer business decisions; authorize effects; own outcome truth; or equate endpoint readiness with semantic fitness.",
        "states": ["draft", "revision_bound", "contract_validated", "deploying", "warming", "ready", "canary", "serving", "degraded", "draining", "rollback_pending", "rolled_back", "failed", "retired"],
        "commands": ["open_inference_deployment", "bind_model_edition", "bind_runtime_and_protocol", "validate_inference_contract", "deploy_revision", "mark_revision_ready", "start_canary", "shift_traffic", "invoke_inference", "record_inference_receipt", "cancel_request", "reconcile_completion", "rollback_revision", "drain_revision", "retire_deployment"],
        "events": ["inference_deployment_opened", "model_edition_bound", "runtime_and_protocol_bound", "inference_contract_validated", "revision_deployed", "revision_marked_ready", "canary_started", "traffic_shifted", "inference_invoked", "inference_receipt_recorded", "request_cancelled", "completion_reconciled", "revision_rolled_back", "revision_drained", "deployment_retired"],
        "invariants": ["model edition deployment revision route request inference attempt prediction response receipt decision and effect are distinct", "every request binds exact protocol model revision tensor shape and deadline", "readiness is operational state not model validity", "traffic shift is not model promotion", "timeout or cancellation does not prove provider non-completion", "retry identity and idempotency posture are explicit", "prediction payload and telemetry have independent retention and privacy policies", "protocol conformance is not numerical or semantic equivalence", "fallback behavior is declared and observable", "prediction output never grants decision or effect authority"],
        "refusals": ["model_edition_unapproved_or_revoked", "deployment_revision_unknown", "runtime_unqualified", "protocol_edition_unsupported", "request_shape_invalid", "feature_input_unavailable", "deadline_invalid", "capacity_unavailable", "route_policy_unsatisfied", "revision_unready", "provider_completion_unknown", "response_invalid", "privacy_purpose_denied", "receipt_gap", "decision_or_effect_authority_requested"],
        "inside": ["deployment and revision desired/observed state", "protocol model and tensor contracts", "runtime binding and readiness", "traffic allocation sticky routing canary and rollback", "request attempt prediction response and receipt identity", "deadline timeout cancellation retry and uncertain completion", "latency throughput capacity and overload posture", "telemetry sampling payload retention and reconciliation"],
        "outside": ["training artifact creation and lifecycle approval", "feature definition and source truth", "model assurance verdicts", "business decision models", "authorization and effect execution", "outcome truth", "generic compute resource ownership", "provider qualification"],
        "language": ["ModelEdition", "Deployment", "DeploymentRevision", "DesiredState", "ObservedState", "TrafficPolicy", "RouteReceipt", "InferenceRequest", "InferenceAttempt", "PredictionOccurrence", "InferenceResponse", "InferenceReceipt", "CompletionDisposition", "Rollback"],
        "values": ["DeploymentId", "RevisionId", "ModelEditionRef", "ProtocolEdition", "TensorContractDigest", "TrafficWeight", "StickyKeyPolicy", "RequestId", "AttemptId", "Deadline", "TargetRef", "CompletionDisposition", "ReceiptDigest"],
        "entities": ["InferenceDeployment", "DeploymentRevision", "TrafficPolicy", "InferenceRequest", "InferenceAttempt", "PredictionOccurrence", "InferenceReceipt"],
        "roots": ["InferenceDeployment", "DeploymentRevision", "InferenceRequest", "InferenceAttempt", "InferenceReceipt"],
        "services": ["InferenceContractService", "RevisionRoutingService", "ReadinessService", "RequestAdmissionService", "InferenceExecutionPort", "CompletionReconciliationService", "RollbackService"],
        "neighbors": [("product.model_lifecycle", "customer_supplier"), ("product.feature_platform", "customer_supplier"), ("product.model_assurance", "published_language"), ("product.runtime_resource_control", "customer_supplier"), ("context.decision_execution", "open_host_service"), ("product.lineage_provenance", "published_language")],
        "time": "Separate model approval, deployment desired/observed, readiness, route-effective, request, attempt, provider completion, response, receipt-recording and outcome times; preserve uncertain completion and revision intervals.",
    },
    "product.model_assurance": {
        "slug": "model_assurance", "classification": "core_horizontal_predictive_model_assurance_product",
        "vision": "Own independent, scoped evidence and review over predictive models without letting evaluators self-authorize lifecycle or business effects.",
        "question": "Against an editioned model, task, population, data cut, slice, metric and policy, what evaluation, validation, monitoring or review finding is supported, defeated, expired or unresolved?",
        "users": ["model_validator", "risk_reviewer", "model_owner", "data_scientist", "monitoring_operator", "compliance_reviewer", "incident_investigator", "auditor"],
        "harmed": ["decision_affected_party", "represented_group", "model_consumer", "risk_owner", "operator", "public_interest"],
        "jobs": ["design independent evaluation", "compute slice and uncertainty evidence", "apply validation policy", "monitor production windows", "distinguish drift from degradation", "open and resolve review cases", "publish limitations", "expire or invalidate evidence"],
        "outcomes": ["scoped_evaluation_result", "uncertainty_and_slice_evidence", "policy_bound_validation_verdict", "drift_or_performance_finding", "governed_review_case", "claim_evidence_report", "expired_or_defeated_verdict"],
        "negative": "Does not own training, model edition identity, deployment approval, source or outcome truth, causal diagnosis, business authority, effect execution or provider qualification; metrics and reports cannot validate themselves.",
        "states": ["draft", "scope_bound", "evidence_pending", "evaluation_running", "evaluated", "validation_pending", "validated", "refused", "monitoring", "finding_open", "review_open", "remediation_pending", "resolved", "invalidated", "expired", "superseded"],
        "commands": ["open_assurance_plan", "bind_model_task_population_and_cut", "seal_metric_slice_and_uncertainty_policy", "run_evaluation", "compare_baseline_or_challenger", "apply_validation_policy", "publish_validation_verdict", "open_monitor_window", "evaluate_drift_and_performance", "open_review_case", "record_defeater", "record_response", "close_review_case", "publish_model_report", "invalidate_or_expire_verdict"],
        "events": ["assurance_plan_opened", "model_task_population_and_cut_bound", "metric_slice_and_uncertainty_policy_sealed", "evaluation_completed", "baseline_or_challenger_compared", "validation_policy_applied", "validation_verdict_published", "monitor_window_opened", "drift_and_performance_evaluated", "review_case_opened", "defeater_recorded", "response_recorded", "review_case_closed", "model_report_published", "verdict_invalidated_or_expired"],
        "invariants": ["metric evaluation result finding validation verdict approval monitoring alert review case and incident are distinct", "every claim binds exact model task population data cut slice metric estimator uncertainty and threshold editions", "evaluation data and training data roles are explicit", "missing or immature labels never become passing evidence", "drift is not degradation and neither is root cause", "correlation or subgroup disparity is not causal attribution", "evidence producer cannot self-grant deployment or effect authority", "waiver reason scope authority and expiry are explicit", "model report claims link to evidence and limitations", "verdict revocation and expiry propagate without erasing history"],
        "refusals": ["model_or_task_unbound", "evaluation_cut_invalid", "label_missing_or_immature", "slice_underpowered", "metric_undefined", "uncertainty_policy_missing", "baseline_unbound", "multiplicity_uncontrolled", "threshold_authority_missing", "evidence_conflicted", "monitor_baseline_invalid", "drift_cause_unproved", "review_owner_unknown", "closure_evidence_missing", "verdict_expired", "approval_authority_requested"],
        "inside": ["assurance plan scope and edition", "evaluation data role cuts slices metrics uncertainty and baselines", "performance calibration robustness fairness and stability findings", "validation policy verdict defeaters waivers and expiry", "production observation windows label maturity and drift", "review cases responses closure and residual risk", "evidence reports intended use limitations and provenance"],
        "outside": ["training execution and artifact registry", "deployment approval and serving", "source or outcome truth", "generic data-quality ownership", "causal root-cause conclusion", "business decision and effect authority", "provider qualification"],
        "language": ["AssurancePlan", "EvaluationCut", "EvaluationSlice", "MetricProfile", "UncertaintyPolicy", "EvaluationResult", "Finding", "ValidationPolicy", "ValidationVerdict", "Defeater", "Waiver", "MonitorWindow", "DriftFinding", "ReviewCase", "ModelReport"],
        "values": ["AssurancePlanId", "ModelEditionRef", "TaskRef", "PopulationRef", "DataCutRef", "SliceRef", "MetricEdition", "ThresholdPolicyEdition", "ConfidenceLevel", "WindowInterval", "VerdictId", "EvidenceDigest", "ExpiryInstant"],
        "entities": ["AssurancePlan", "EvaluationOccurrence", "ValidationVerdict", "MonitorWindow", "Finding", "ReviewCase", "ModelReport"],
        "roots": ["AssurancePlan", "EvaluationOccurrence", "ValidationVerdict", "MonitorWindow", "ReviewCase"],
        "services": ["EvaluationDesignService", "MetricEvaluationService", "UncertaintyService", "ValidationPolicyService", "DriftEvaluationService", "ReviewCaseService", "EvidenceReportService"],
        "neighbors": [("product.model_lifecycle", "customer_supplier"), ("product.online_inference", "customer_supplier"), ("product.data_quality", "customer_supplier"), ("context.outcome_truth", "anti_corruption_layer"), ("context.lifecycle_authority", "published_language"), ("product.lineage_provenance", "published_language")],
        "time": "Separate data event/availability/recording, label maturity, evaluation cut, evidence production, verdict validity, deployment observation window, alert, review, waiver expiry and revocation times; bitemporally retain corrected outcomes.",
    },
    "product.decision_automation": {
        "slug": "decision_automation", "classification": "core_horizontal_deterministic_decision_modeling_product",
        "vision": "Own editioned deterministic decision models and traceable invocations that produce results or action proposals but never self-authorize effects.",
        "question": "For an exact decision model edition, typed inputs and invocation context, what deterministic decision result and trace follow, and what proposal may be submitted to an external authority boundary?",
        "users": ["decision_analyst", "policy_author", "business_rule_owner", "application_developer", "decision_service_operator", "authority_reviewer", "auditor"],
        "harmed": ["decision_subject", "customer_or_counterparty", "worker", "policy_rights_holder", "operator", "appeal_party"],
        "jobs": ["model decision requirements", "compile and analyze decision logic", "detect table gaps and overlaps", "execute typed deterministic invocations", "record decision traces", "submit action proposals", "version and retire policies", "support explanation and appeal evidence"],
        "outcomes": ["typed_decision_model", "gap_and_overlap_analysis", "deterministic_decision_result", "replayable_decision_trace", "non_authoritative_action_proposal", "authority_verdict_link", "versioned_policy_retirement"],
        "negative": "Does not predict facts, train models, own identity or policy authority, approve actors, execute effects, assert outcome completion, or treat a rule-engine/provider result as authorization.",
        "states": ["draft", "requirements_bound", "typed", "analysis_failed", "compiled", "published", "invokable", "invocation_running", "result_produced", "proposal_submitted", "authority_pending", "authorized", "refused", "superseded", "revoked", "retired"],
        "commands": ["open_decision_model", "bind_decision_requirements", "typecheck_decision_model", "analyze_gaps_and_overlaps", "compile_decision_model", "publish_decision_edition", "invoke_decision_service", "record_decision_trace", "form_action_proposal", "submit_proposal_to_authority", "record_authority_verdict", "supersede_decision_edition", "revoke_decision_edition", "retire_decision_model"],
        "events": ["decision_model_opened", "decision_requirements_bound", "decision_model_typechecked", "gaps_and_overlaps_analyzed", "decision_model_compiled", "decision_edition_published", "decision_service_invoked", "decision_trace_recorded", "action_proposal_formed", "proposal_submitted_to_authority", "authority_verdict_recorded", "decision_edition_superseded", "decision_edition_revoked", "decision_model_retired"],
        "invariants": ["decision requirement model table rule invocation result trace proposal authority verdict effect and outcome are distinct", "all decision inputs and external functions are typed and edition-bound", "null unknown not-applicable denied and error remain distinct", "hit policy overlap order and conflict precedence are explicit", "same model edition and canonical input produce the same decision result", "schema validity is not semantic conformance", "decision log is not effect receipt", "prediction may be an input but is not the decision", "decision result never grants actor or effect authority", "revocation and supersession preserve historical replay"],
        "refusals": ["decision_requirement_ambiguous", "input_type_invalid", "dependency_unbound", "unsupported_expression_profile", "decision_table_gap", "ambiguous_overlap", "hit_policy_missing", "nondeterministic_function_prohibited", "model_revoked", "invocation_context_missing", "decision_undefined", "trace_storage_denied", "authority_context_missing", "purpose_denied", "effect_execution_requested"],
        "inside": ["decision requirements graph and service boundary", "typed decision model expressions tables rules and hit policies", "static gap overlap and dependency analysis", "editioned compilation and deterministic invocation", "decision result and trace identity", "sensitive-log redaction", "action proposal formation and authority handoff", "model supersession revocation retirement and historical replay"],
        "outside": ["predictive model training and inference", "identity proof and entitlement authority", "workflow/case ownership", "effect execution and completion", "outcome truth", "generic policy enforcement points", "provider qualification"],
        "language": ["DecisionRequirement", "DecisionModel", "DecisionEdition", "DecisionService", "DecisionTable", "Rule", "HitPolicy", "DecisionInvocation", "DecisionResult", "DecisionTrace", "ActionProposal", "AuthorityVerdict", "EffectReceipt"],
        "values": ["DecisionModelId", "DecisionEditionId", "ExpressionProfileEdition", "RuleId", "HitPolicy", "InputSchemaDigest", "InvocationId", "DecisionId", "PurposeRef", "PrincipalRef", "TraceDigest", "AuthorityVerdictRef"],
        "entities": ["DecisionModel", "DecisionEdition", "DecisionTable", "DecisionInvocation", "DecisionResult", "DecisionTrace", "ActionProposal"],
        "roots": ["DecisionModel", "DecisionEdition", "DecisionInvocation", "DecisionTrace", "ActionProposal"],
        "services": ["DecisionTypecheckingService", "TableAnalysisService", "DecisionCompilationService", "DecisionEvaluationService", "TraceRedactionService", "AuthorityBridgeService", "HistoricalReplayService"],
        "neighbors": [("context.vertical_policy_authority", "customer_supplier"), ("context.identity_and_entitlement", "anti_corruption_layer"), ("product.online_inference", "customer_supplier"), ("product.workflow_case", "open_host_service"), ("context.effect_runtime", "effect_port"), ("product.lineage_provenance", "published_language")],
        "time": "Separate policy validity, model recording, edition publication, invocation effective, decision result, authority verdict, effect and outcome times; preserve bitemporal policy editions and replay against exact historical inputs.",
    },
    "product.optional_model_extension": {
        "slug": "optional_model_extension", "classification": "supporting_optional_non_authoritative_model_and_agent_extension_product",
        "vision": "Provide removable model or agent invocations that return typed, tainted proposals to deterministic gates and own no domain truth, validation or effect authority.",
        "question": "When intent explicitly permits an optional model or agent extension, what bounded invocation produced which typed claim, plan or tool-call proposal, with provenance, uncertainty and deterministic acceptance or refusal?",
        "users": ["application_designer", "analyst", "operator", "reviewer", "tool_owner", "security_owner", "auditor"],
        "harmed": ["represented_person", "tool_effect_subject", "data_owner", "application_user", "operator", "downstream_decision_party"],
        "jobs": ["declare a narrow extension task", "bind provider and budgets", "invoke with cancellation", "parse typed output", "preserve taint and provenance", "validate claims and proposals deterministically", "submit authorized tool proposals", "remove extension and execute declared fallback"],
        "outcomes": ["editioned_extension_task", "bounded_invocation_receipt", "typed_tainted_proposal", "claim_validation_result", "per_effect_authority_request", "deterministic_fallback_or_refusal", "successful_removal_test"],
        "negative": "Does not supply ambient intelligence, canonical vocabulary, business truth, deterministic compilation, model assurance, policy decisions, tool authorization, effect execution or acceptance evidence; absence must not break the deterministic core.",
        "states": ["undeclared", "draft", "intent_bound", "fallback_bound", "provider_unbound", "ready", "invoking", "cancelled", "completion_unknown", "proposal_received", "validation_pending", "accepted_as_input", "refused", "expired", "removed"],
        "commands": ["declare_extension_task", "bind_use_site_and_fallback", "bind_provider_edition", "set_budget_and_tool_scope", "invoke_extension", "cancel_extension", "record_completion", "parse_generated_proposal", "validate_generated_claims", "request_tool_authority", "accept_proposal_as_untrusted_input", "refuse_proposal", "execute_fallback", "remove_extension"],
        "events": ["extension_task_declared", "use_site_and_fallback_bound", "provider_edition_bound", "budget_and_tool_scope_set", "extension_invoked", "extension_cancelled", "completion_recorded", "generated_proposal_parsed", "generated_claims_validated", "tool_authority_requested", "proposal_accepted_as_untrusted_input", "proposal_refused", "fallback_executed", "extension_removed"],
        "invariants": ["extension task invocation generated claim plan tool proposal decision authorization effect and outcome are distinct", "extension use is prohibited unless declared optional or required by intent", "removal preserves deterministic parsing typing binding decisions and effects", "well-formed output is not true valid safe or authorized", "generated output retains untrusted taint until each deterministic gate succeeds", "a provider cannot self-validate its claims", "tool visibility is not tool-call authority", "authority is checked per principal purpose resource operation and effect", "retry creates a new invocation identity", "unavailable optional extension uses deterministic fallback or typed refusal"],
        "refusals": ["extension_not_declared", "deterministic_fallback_missing", "provider_unqualified", "provider_edition_unbound", "budget_unbounded", "tool_scope_ambiguous", "prompt_or_input_tainted", "schema_invalid", "claim_evidence_missing", "proposal_validation_failed", "completion_unknown", "authority_missing", "purpose_denied", "effect_scope_exceeded", "removal_test_failed"],
        "inside": ["extension task use-site and intent posture", "provider protocol model edition sampling and budget binding", "invocation retry cancellation and completion receipts", "typed claim plan and tool-call proposal carriers", "taint provenance evidence and deterministic validation hooks", "per-effect authority requests", "fallback execution and extension removal tests"],
        "outside": ["domain vocabulary and source truth", "deterministic compiler semantics", "predictive lifecycle and assurance", "business decision logic", "identity and authorization decisions", "tool effect execution", "outcome truth", "vertical acceptance"],
        "language": ["ExtensionTask", "UseSite", "IntentPosture", "FallbackPlan", "ProviderEdition", "ExtensionInvocation", "InvocationReceipt", "GeneratedClaim", "GeneratedPlan", "ToolCallProposal", "Taint", "ValidationResult", "AuthorityRequest", "RemovalTest"],
        "values": ["ExtensionTaskId", "UseSiteRef", "ProviderEditionRef", "ProtocolEdition", "InvocationId", "Budget", "Deadline", "SamplingProfile", "SchemaDigest", "ToolScope", "EvidenceRef", "TaintLabel"],
        "entities": ["ExtensionTask", "ProviderBinding", "ExtensionInvocation", "GeneratedProposal", "ValidationOccurrence", "AuthorityRequest", "RemovalTest"],
        "roots": ["ExtensionTask", "ExtensionInvocation", "GeneratedProposal", "AuthorityRequest", "RemovalTest"],
        "services": ["ExtensionIntentService", "ProviderBindingService", "BoundedInvocationService", "ProposalParsingService", "ClaimValidationBridge", "ToolAuthorityBridge", "RemovalConformanceService"],
        "neighbors": [("context.solution_compiler", "conformist"), ("context.domain_validation", "customer_supplier"), ("context.identity_and_authority", "anti_corruption_layer"), ("context.effect_runtime", "effect_port"), ("product.lineage_provenance", "published_language"), ("context.provider_qualification", "customer_supplier")],
        "time": "Separate task-edition, provider-edition, invocation-start, provider-completion, receipt, proposal, validation, authority and effect times; timeout and cancellation preserve unknown remote completion until reconciled.",
    },
}


def automation(product: str) -> dict[str, Any]:
    optional = product == "product.optional_model_extension"
    return {
        "default": "PROHIBITED_UNLESS_DECLARED" if optional else "DETERMINISTIC_CORE_ONLY",
        "postures": ["PROHIBITED", "OPTIONAL", "REQUIRED_BY_INTENT", "UNDETERMINED"],
        "law": (
            "Models and agents are invoked only at an editioned declared use site and return untrusted proposals; deterministic validation and authority remain external."
            if optional else
            "Statistical or learned methods are declared computational providers behind typed contracts; labels such as AI, deep, foundation or agent confer no truth, fitness, qualification or authority."
        ),
        "removal_law": (
            "Removing the extension preserves the complete deterministic compiler and every domain, evidence, decision, authority and effect contract; optional use falls back or refuses."
            if optional else
            "Removing every optional generative or agent helper preserves the product's vocabulary, typechecking, invariants, lifecycle, evidence, refusals and core execution."
        ),
        "hard_work_law": "Automation never substitutes for vocabulary, temporal cuts, invariants, provider qualification, evidence, authority, acceptance, effects or reconciliation.",
    }


def product_truth(product: str, spec: dict[str, Any]) -> dict[str, Any]:
    return {
        "sovereign_question": spec["question"], "users": spec["users"],
        "harmed_parties": spec["harmed"], "jobs": spec["jobs"], "outcomes": spec["outcomes"],
        "negative_mission": spec["negative"], "lifecycle_states": spec["states"],
        "commands": spec["commands"], "events": spec["events"], "invariants": spec["invariants"],
        "refusals": spec["refusals"], "automation_modality": automation(product),
    }


def dossier(product: str, spec: dict[str, Any]) -> dict[str, Any]:
    truth = product_truth(product, spec)
    roots = spec["roots"]
    ddd = {
        "domain_vision_statement": spec["vision"],
        "subdomain_classification": spec["classification"],
        "bounded_context_boundary": {"inside": spec["inside"], "outside": spec["outside"]},
        "ubiquitous_language_policy": {"canonical_terms": spec["language"], "law": "Terms are editioned inside this boundary; homonyms are translated at anti-corruption layers and every non-collapse invariant is testable."},
        "context_map": [{"neighbor_ref": ref, "relationship": relationship, "translation": f"Translate through {ref}; imported identity, truth, authority and receipts remain externally owned."} for ref, relationship in spec["neighbors"]],
        "anti_corruption_layers": [f"acl.{spec['slug']}.{ref.split('.')[-1]}" for ref, _ in spec["neighbors"]],
        "published_language": spec["language"] + ["TypedRefusal", "EvidenceRef", "EditionRef"],
        "value_objects": spec["values"], "entities": spec["entities"],
        "aggregates": [{"root": root, "consistency": f"{root} changes only through editioned commands; identity, state, evidence and refusals remain explicit."} for root in roots],
        "aggregate_roots": roots, "aggregate_invariants": spec["invariants"],
        "commands": spec["commands"], "domain_events": spec["events"],
        "refusal_failure_catalog": spec["refusals"], "domain_services": spec["services"],
        "application_services": [f"{name.removesuffix('Service')}UseCase" for name in spec["services"]],
        "repositories": [f"{root}Repository" for root in roots],
        "factories": [f"{root}Factory" for root in roots],
        "specifications": [f"{name.removesuffix('Service')}Specification" for name in spec["services"]] + ["ProviderQualificationSpecification", "EvidenceValiditySpecification", "RemovalConformanceSpecification"],
        "state_machine": {"states": spec["states"], "transition_law": "Only named commands with current edition, expected version, satisfied invariants, evidence and authority may emit the corresponding past-tense event; terminal and revocation semantics fail closed."},
        "policies_and_reactions": ["on evidence expiry open review or refuse transition", "on revocation propagate invalidation to dependent editions", "on uncertain remote completion reconcile before retrying effects", "on optional automation failure use declared fallback or typed refusal"],
        "sagas_and_process_managers": [f"{spec['slug'].title().replace('_', '')}LifecycleProcess", "ProviderQualificationProcess", "RevocationPropagationProcess", "ExitAndPortabilityProcess"],
        "read_models_and_projections": [f"{root}StatusProjection" for root in roots] + ["OpenRefusalsProjection", "EvidenceAndAuthorityProjection", "DependencyBlastRadiusProjection"],
        "integration_event_policy": "Only editioned published-language facts cross the boundary. Internal provider callbacks, tentative findings and proposals remain internal; authority, effect and outcome claims require their owning external receipts.",
        "concurrency_and_idempotency": "Use immutable occurrence IDs, aggregate versions, command idempotency keys, provider-attempt IDs and append-only receipts. Optimistic conflicts refuse; retries never overwrite prior attempts; uncertain effect completion must reconcile.",
        "time_model": spec["time"],
        "event_storming_swimlanes": {"actors": spec["users"], "commands": spec["commands"], "events": spec["events"], "hotspots": ["identity versus alias", "desired versus observed state", "evidence versus authority", "retry versus new occurrence", "proposal versus accepted fact", "revocation propagation"]},
        "nonfunctional_laws": spec["invariants"] + ["finite budgets deadlines payloads and retention are declared", "all public behavior is deterministic for fixed declared inputs or explicitly reports nondeterminism", "no provider brand owns canonical semantics", "one implementation never proves portability", automation(product)["removal_law"]],
    }
    assert set(ddd) == DDD_FIELDS
    return {
        "dossier_id": f"ddd.model_decision.{spec['slug']}", "product_ref": product,
        "status": "candidate_not_ratified",
        "product_truth": {"sovereign_question": truth["sovereign_question"], "users": truth["users"], "harmed_parties": truth["harmed_parties"], "jobs": truth["jobs"], "measurable_outcomes": truth["outcomes"], "negative_mission": truth["negative_mission"]},
        "strategic_and_tactical_ddd": ddd,
    }


def enrich(source: dict[str, Any]) -> dict[str, Any]:
    owner_by_library = {library: product for product, libraries in PRODUCT_LIBRARIES.items() for library in libraries}
    source["ddd_dossiers"] = [row for row in source.get("ddd_dossiers", []) if row.get("product_ref") not in SPECS]
    for artifact in source["artifacts"]:
        product = artifact["artifact_id"]
        if product in SPECS:
            artifact.update(product_truth(product, SPECS[product]))
    for library in source["libraries"]:
        product = owner_by_library.get(library["library_id"])
        if product:
            library["product_refs"] = [product]
    for binding in source.get("binding_maps", []):
        product = owner_by_library.get(binding["abstract_library_ref"])
        if product:
            binding["product_refs"] = [product]
    for gap in source.get("binding_gaps", []):
        product = owner_by_library.get(gap["abstract_library_ref"])
        if product:
            gap["product_refs"] = [product]
            gap["abstract_library_refs"] = [gap["abstract_library_ref"]]
    source["ddd_dossiers"].extend(dossier(product, spec) for product, spec in SPECS.items())
    source["non_collapse_laws"].extend([
        "statistical or learned method != ambient AI truth class",
        "model or agent capability != vocabulary invariant evidence qualification authority or acceptance",
        "optional extension removal preserves deterministic core behavior",
    ])
    return source
