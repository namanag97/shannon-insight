#!/usr/bin/env python3
"""Promote horizontal Project & Portfolio Controls without absorbing planning or execution.

Project controls owns an authorized delivery baseline and the governed measurement/change
lifecycle against it. Integrated planning owns alternatives and future selection; scheduling,
finance, contracts, workflow, analytics and execution remain suppliers or neighboring authorities.
"""

from __future__ import annotations

from typing import Any

from planning_enrichment import DDD_FIELDS


PRODUCT = "product.project_portfolio_controls"
SEMANTIC_OWNER = "semantic.project_portfolio_controls"
PRODUCT_FIELDS = {
    "sovereign_question", "users", "harmed_parties", "jobs", "outcomes", "negative_mission",
    "lifecycle_states", "commands", "events", "invariants", "refusals", "automation_modality",
}

AUTOMATION = {
    "default": "DETERMINISTIC_CORE_ONLY",
    "postures": ["PROHIBITED", "OPTIONAL", "REQUIRED_BY_INTENT", "UNDETERMINED"],
    "law": "Analytics, statistical models, learned systems, LLMs and agents may provide attributed findings, forecasts, explanations or proposals only; deterministic baseline, period, authority, change, evidence and effect laws determine admissibility.",
    "removal_law": "Removing every optional model, LLM and agent preserves baseline authorization, status cuts, earned-value arithmetic, variance, forecast-at-completion, change control, rebaselining, rollup, close and audit; an explicitly required unavailable aid yields capability_unavailable.",
    "hard_work_law": "Automation never invents authorized scope, budget, schedule, progress evidence, accounting truth, approval rights, baseline changes, corrective effects or completion truth.",
}

SOURCES = [
    {
        "source_id": "source.project_controls.iso21508", "source_class": "international_standard",
        "title": "ISO 21508:2026 Earned value management in project and programme management",
        "publisher": "ISO", "uri": "https://www.iso.org/standard/87899.html", "retrieved_at": "2026-08-27",
        "claim": "Defines earned-value guidance applicable to any organization and sector and to projects, programmes and portfolios of any size or complexity.",
        "scope_limit": "The catalogue page establishes horizontal applicability and standard scope, not a complete portable software contract or implementation qualification.",
    },
    {
        "source_id": "source.project_controls.gao_schedule", "source_class": "official_government_guidance",
        "title": "Schedule Assessment Guide: Best Practices for Project Schedules", "publisher": "U.S. Government Accountability Office",
        "uri": "https://www.gao.gov/products/gao-16-89g", "retrieved_at": "2026-08-27",
        "claim": "Separates comprehensive schedule construction, performance measurement baselines, schedule updates, risk analysis and controlled baseline changes.",
        "scope_limit": "Audit guidance supports semantic seams and laws but does not dictate provider packaging or qualify a runtime implementation.",
    },
    {
        "source_id": "source.project_controls.doe_evms", "source_class": "official_government_guidance",
        "title": "EVMS Implementation Guidance", "publisher": "U.S. Department of Energy",
        "uri": "https://www.energy.gov/projectmanagement/evms-implementation-guidance", "retrieved_at": "2026-08-27",
        "claim": "Treats EVMS integration, planning/scheduling, performance measurement baselines and change-control management as governed project-control processes.",
        "scope_limit": "DOE guidance carries government capital-project context and does not prove universal workflow, authority or implementation choices.",
    },
    {
        "source_id": "source.project_controls.oracle_unifier", "source_class": "official_product_documentation",
        "title": "Starting a Project by Using Business Processes", "publisher": "Oracle Primavera Unifier",
        "uri": "https://docs.oracle.com/en/industries/construction-engineering/primavera-unifier/26/accelerator-user/startingaprojectbyusingbusinessprocesses-10302014a.html", "retrieved_at": "2026-08-27",
        "claim": "Independently persists project requests, schedules and baselines, estimates, budgets, cost sheets, cash flow, change orders and approval-bearing business processes.",
        "scope_limit": "A provider implementation is adoption evidence for seams, not ownership of their portable semantics or proof that construction-specific DTOs generalize unchanged.",
    },
    {
        "source_id": "source.project_controls.oracle_payment", "source_class": "official_product_documentation",
        "title": "Payment Application Business Process", "publisher": "Oracle Primavera Unifier",
        "uri": "https://docs.oracle.com/en/industries/construction-engineering/primavera-unifier/26/accelerator-user/paymentapplicationbusinessprocess-10296630a.html", "retrieved_at": "2026-08-27",
        "claim": "Separates a payment application lifecycle and approval state from its referenced commitment, change commits, schedule of values and actual payment.",
        "scope_limit": "Supports non-collapse laws only; payment applications remain contract/cost-control imports and do not make project controls the financial-ledger authority.",
    },
]
EVIDENCE = [row["source_id"] for row in SOURCES]


LIBRARIES: dict[str, dict[str, Any]] = {
    "controls_system_definition": {
        "types": ["ControlSystemId", "ControlSystemEdition", "ControlScope", "ControlPolicyRef", "CalendarRef", "CutoffPolicy"],
        "operations": ["open_control_system", "bind_scope_policy_calendar", "publish_control_system_edition"],
        "decisions": ["control_scope", "policy_edition", "calendar", "cutoff", "compatibility"],
        "invariants": ["control-system edition is immutable", "portfolio programme project and control account grains remain explicit"],
        "refusals": ["control_scope_ambiguous", "calendar_unbound", "policy_conflict"], "dependencies": [],
    },
    "authorized_baseline_edition": {
        "types": ["BaselineId", "BaselineEdition", "AuthorizationRef", "ScopeCut", "ScheduleCut", "BudgetCut", "BaselineStatus"],
        "operations": ["propose_baseline", "validate_baseline", "authorize_baseline", "supersede_baseline"],
        "decisions": ["baseline_identity", "scope_schedule_budget_coherence", "authorization", "effective_time"],
        "invariants": ["baseline is not current plan current schedule or forecast", "only authorized editions measure controlled performance"],
        "refusals": ["baseline_incoherent", "authorization_missing", "effective_time_invalid"], "dependencies": ["controls_system_definition"],
    },
    "scope_control_account_structure": {
        "types": ["WorkBreakdownStructure", "OrganizationBreakdownStructure", "ControlAccountId", "WorkPackageId", "ResponsibilityAssignment"],
        "operations": ["bind_work_scope", "assign_control_account", "validate_responsibility_matrix", "version_structure"],
        "decisions": ["scope_completeness", "control_account_grain", "responsible_owner", "rollup_path"],
        "invariants": ["authorized scope and organizational responsibility are distinct", "each controlled work element has an accountable control path"],
        "refusals": ["scope_gap", "control_account_overlap", "responsible_owner_missing"], "dependencies": ["authorized_baseline_edition"],
    },
    "schedule_baseline_control": {
        "types": ["ScheduleEdition", "ActivityId", "Dependency", "Milestone", "CriticalPath", "ScheduleVariance"],
        "operations": ["admit_schedule_edition", "compare_to_schedule_baseline", "record_critical_path", "publish_schedule_variance"],
        "decisions": ["schedule_admission", "logic_quality", "criticality", "variance_semantics"],
        "invariants": ["scheduling calculation is imported", "current schedule never mutates baseline history"],
        "refusals": ["schedule_logic_invalid", "baseline_cut_missing", "variance_semantics_missing"], "dependencies": ["scope_control_account_structure"],
    },
    "cost_baseline_control": {
        "types": ["BudgetEdition", "TimePhasedBudget", "CostElement", "ManagementReserve", "UndistributedBudget", "CostVariance"],
        "operations": ["admit_budget_edition", "time_phase_budget", "reconcile_control_budget", "publish_cost_variance"],
        "decisions": ["budget_admission", "time_phasing", "reserve_classification", "cost_variance_semantics"],
        "invariants": ["control budget is not general ledger truth", "management reserve and distributed budget never collapse"],
        "refusals": ["budget_reconciliation_failed", "reserve_classification_missing", "ledger_cut_unbound"], "dependencies": ["scope_control_account_structure"],
    },
    "resource_baseline_binding": {
        "types": ["ResourceRequirement", "ResourceAssignment", "AvailabilityCut", "RateEdition", "ResourceVariance"],
        "operations": ["bind_resource_requirement", "admit_availability_cut", "bind_rate_edition", "assess_resource_variance"],
        "decisions": ["resource_identity", "availability_validity", "rate_applicability", "variance_semantics"],
        "invariants": ["resource plan is not resource ownership or actual use", "rates and availability are editioned imports"],
        "refusals": ["resource_owner_unbound", "availability_stale", "rate_inapplicable"], "dependencies": ["authorized_baseline_edition"],
    },
    "progress_status_cut": {
        "types": ["StatusCutId", "DataDate", "ProgressObservation", "CompletionEvidence", "ActualCostCut", "StatusAdmission"],
        "operations": ["open_status_cut", "admit_progress_evidence", "admit_actual_cost_cut", "seal_status_cut"],
        "decisions": ["data_date", "evidence_admission", "progress_method", "actual_cut_validity"],
        "invariants": ["progress claim observation admission and earned value are distinct", "sealed status cuts are immutable"],
        "refusals": ["data_date_invalid", "progress_evidence_insufficient", "actual_cost_cut_unbound"], "dependencies": ["schedule_baseline_control", "cost_baseline_control"],
    },
    "earned_value_measurement": {
        "types": ["PlannedValue", "EarnedValue", "ActualCost", "PerformanceIndex", "MeasurementTechnique", "MeasurementReceipt"],
        "operations": ["calculate_planned_value", "calculate_earned_value", "calculate_actual_cost", "derive_performance_indices"],
        "decisions": ["measurement_technique", "formula_edition", "comparability", "rounding"],
        "invariants": ["planned value earned value and actual cost remain distinct", "earned value requires admitted objective progress evidence"],
        "refusals": ["measurement_technique_unbound", "progress_not_admitted", "cuts_incomparable"], "dependencies": ["progress_status_cut"],
    },
    "variance_forecast_at_completion": {
        "types": ["VarianceAnalysis", "EstimateToComplete", "EstimateAtCompletion", "VarianceAtCompletion", "ForecastAssumption", "Uncertainty"],
        "operations": ["analyze_variance", "forecast_completion", "compare_forecast_methods", "publish_control_forecast"],
        "decisions": ["variance_significance", "forecast_method", "assumption_cut", "uncertainty_posture"],
        "invariants": ["variance is not causal explanation", "forecast at completion is not approved change or commitment"],
        "refusals": ["variance_threshold_unbound", "forecast_method_unqualified", "uncertainty_unreported"], "dependencies": ["earned_value_measurement"],
    },
    "change_control_case": {
        "types": ["ChangeCaseId", "ChangeProposal", "ImpactAssessment", "DecisionRightRef", "ChangeDecision", "Disposition"],
        "operations": ["open_change_case", "assess_scope_schedule_cost_impact", "request_change_decision", "approve_reject_or_return_change"],
        "decisions": ["change_class", "impact_scope", "decision_authority", "disposition"],
        "invariants": ["change proposal impact assessment approval and baseline revision are distinct", "approval never rewrites prior baselines"],
        "refusals": ["impact_incomplete", "decision_authority_missing", "maker_checker_violated"], "dependencies": ["variance_forecast_at_completion"],
    },
    "baseline_revision_rebaseline": {
        "types": ["BaselineRevision", "BeforeAfterDelta", "EffectivePeriod", "SupersessionLink", "InFlightDisposition"],
        "operations": ["draft_baseline_revision", "validate_authorized_change", "publish_successor_baseline", "dispose_in_flight_work"],
        "decisions": ["change_incorporation", "effective_period", "history_preservation", "in_flight_disposition"],
        "invariants": ["authorized change does not become baseline until incorporated", "rebaseline supersedes and never erases history"],
        "refusals": ["change_not_authorized", "delta_untraceable", "in_flight_disposition_unknown"], "dependencies": ["change_control_case"],
    },
    "portfolio_program_rollup": {
        "types": ["PortfolioRef", "ProgrammeRef", "ProjectRef", "RollupProfile", "AggregationResidual", "ComparabilityFinding"],
        "operations": ["bind_rollup_profile", "aggregate_control_results", "reconcile_residuals", "publish_portfolio_view"],
        "decisions": ["membership_cut", "aggregation_rule", "comparability", "residual_disposition"],
        "invariants": ["rollup does not mutate source projects", "numeric aggregation never creates semantic comparability"],
        "refusals": ["membership_cut_ambiguous", "projects_incomparable", "residual_unbounded"], "dependencies": ["variance_forecast_at_completion"],
    },
    "control_period_close_reporting": {
        "types": ["ControlPeriod", "CloseChecklist", "Exception", "ControlReportEdition", "DisclosureProfile", "CloseReceipt"],
        "operations": ["open_control_period", "evaluate_close_gates", "resolve_or_carry_exception", "close_period", "publish_control_report"],
        "decisions": ["period_cutoff", "close_readiness", "exception_disposition", "audience_disclosure"],
        "invariants": ["period close freezes a reporting cut not project reality", "reporting never grants corrective-action authority"],
        "refusals": ["required_cut_missing", "close_exception_open", "disclosure_denied"], "dependencies": ["portfolio_program_rollup", "baseline_revision_rebaseline"],
    },
}
KEYS = list(LIBRARIES)


def local_library(key: str) -> str:
    return f"library.project_controls.{key}"


def local_capability(key: str) -> str:
    return f"capability.project_controls.{key}"


def product_truth() -> dict[str, Any]:
    return {
        "sovereign_question": "Given an authorized scope-schedule-cost baseline and an exact status cut, what controlled performance, variance, completion forecast and governed change state exists for a project, programme or portfolio, and what may be reported or revised without rewriting history or acquiring execution authority?",
        "users": ["project_controls_manager", "project_manager", "programme_manager", "portfolio_owner", "control_account_manager", "scheduler", "cost_engineer", "change_control_board", "sponsor", "assurance_reviewer"],
        "harmed_parties": ["worker", "supplier", "contractor", "customer", "sponsor", "public_funder", "community_or_environment", "downstream_operator"],
        "jobs": ["Authorize and preserve a delivery baseline; admit period progress and actual-cost evidence; measure schedule/cost performance; forecast completion; govern change and rebaseline; roll up without corrupting source projects; close and report exact periods."],
        "outcomes": ["authorized_traceable_baseline", "immutable_status_cut", "qualified_performance_measurement", "explicit_variance_and_completion_forecast", "authority_bearing_change_decision", "traceable_successor_baseline", "non_mutating_portfolio_rollup", "auditable_period_close_report"],
        "negative_mission": "Does not choose planning alternatives; own detailed scheduling algorithms; issue identity, delegation or approval authority; own contracts, commitments, invoices, payments or ledger truth; execute work or corrective actions; own raw telemetry; infer causes by default; or treat analytics findings as control effects.",
        "lifecycle_states": ["definition_draft", "baseline_proposed", "baseline_validation", "baseline_authorization_pending", "baseline_authorized", "period_open", "status_collection", "status_sealed", "measurement_pending", "variance_review", "forecast_published", "change_open", "change_decision_pending", "change_approved", "baseline_revision_pending", "successor_baseline_authorized", "period_close_pending", "period_closed", "superseded", "recalled", "refused"],
        "commands": ["open_control_system", "propose_baseline", "authorize_baseline", "open_status_cut", "admit_progress_and_actual_cost", "seal_status_cut", "measure_performance", "forecast_completion", "open_change_case", "record_change_decision", "publish_successor_baseline", "roll_up_portfolio", "close_control_period", "publish_control_report"],
        "events": ["control_system_opened", "baseline_proposed", "baseline_authorized", "status_cut_opened", "progress_and_actual_cost_admitted", "status_cut_sealed", "performance_measured", "completion_forecast_published", "change_case_opened", "change_decision_recorded", "successor_baseline_published", "portfolio_rolled_up", "control_period_closed", "control_report_published"],
        "invariants": ["planning alternative != authorized baseline", "baseline != current schedule != completion forecast", "progress observation != admitted progress != earned value", "variance != causal explanation", "forecast at completion != approved change", "change request != approval != baseline revision", "cost control != financial ledger", "payment application != payment", "analytics service != application logic != control effect", "rollup never mutates source project state"],
        "refusals": ["control_scope_ambiguous", "baseline_incoherent", "authorization_missing", "status_cut_incomplete", "progress_evidence_insufficient", "actual_cost_cut_unbound", "measurement_method_unbound", "cuts_incomparable", "uncertainty_unreported", "change_impact_incomplete", "change_authority_missing", "maker_checker_violated", "baseline_delta_untraceable", "portfolio_membership_ambiguous", "period_close_exception_open", "disclosure_denied"],
        "automation_modality": AUTOMATION,
    }


def artifacts() -> list[dict[str, Any]]:
    truth = product_truth()
    rows = [
        {"artifact_id": SEMANTIC_OWNER, "kind": "semantic_contract", "name": "Project and portfolio control semantics", "status": "candidate", "semantic_owner_ref": None, "adoption_unit": False, "operated": False, "definition": "Owns authorized baseline, status cut, performance measurement, change, supersession, rollup and control-period meanings.", "evidence_refs": EVIDENCE},
        {"artifact_id": PRODUCT, "kind": "product", "name": "Project & Portfolio Controls", "status": "candidate", "semantic_owner_ref": SEMANTIC_OWNER, "adoption_unit": True, "operated": True, "definition": "Operates authorized delivery baselines and governed performance/change lifecycles across projects, programmes and portfolios.", "evidence_refs": EVIDENCE, **truth},
    ]
    rows.extend({"artifact_id": local_capability(key), "kind": "capability", "name": key.replace("_", " ").title(), "status": "specified_candidate", "semantic_owner_ref": SEMANTIC_OWNER, "adoption_unit": False, "operated": False, "definition": f"Provide exact project-control {key.replace('_', ' ')} semantics.", "evidence_refs": EVIDENCE} for key in KEYS)
    return rows


def library(key: str) -> dict[str, Any]:
    spec = LIBRARIES[key]
    return {"library_id": local_library(key), "class": "semantic_policy_pure", "owner_ref": SEMANTIC_OWNER, "provides": [local_capability(key)], "types": spec["types"], "operations": spec["operations"], "decisions": spec["decisions"], "invariants": spec["invariants"], "refusals": spec["refusals"], "dependencies": [local_library(dep) for dep in spec["dependencies"]], "effect_boundary": "pure_no_io", "evidence_refs": EVIDENCE, "product_refs": [PRODUCT]}


def boundary_decision() -> dict[str, Any]:
    axes = {
        "user": [EVIDENCE[0], EVIDENCE[2]], "job": [EVIDENCE[0], EVIDENCE[1]],
        "adoption": [EVIDENCE[3], EVIDENCE[4]], "semantics": [EVIDENCE[0], EVIDENCE[2], EVIDENCE[3]],
        "authority": [EVIDENCE[2], EVIDENCE[4]], "lifecycle": [EVIDENCE[2], EVIDENCE[3]],
        "operation": [EVIDENCE[1], EVIDENCE[3]], "economics": [EVIDENCE[0], EVIDENCE[3]],
        "interface": [EVIDENCE[2], EVIDENCE[3]], "market_evidence": [EVIDENCE[3], EVIDENCE[4]],
    }
    return {"decision_id": "decision.methods.project_portfolio_controls", "subject_ref": PRODUCT, "disposition": "strong_product_candidate", "rationale": "ISO 21508 establishes cross-sector project/programme/portfolio applicability; GAO and DOE independently govern baseline, measurement and change lifecycles; Primavera independently operates the same first-class states. The lifecycle remains distinct from integrated planning, scheduling engines, finance, workflow, analytics and execution.", "evidence_refs": sorted(set(sum(axes.values(), []))), "split_test": {axis: {"score": 2, "evidence_refs": refs} for axis, refs in axes.items()}, "supersedes": ["candidate.product.project_portfolio_controls"]}


def dossier() -> dict[str, Any]:
    truth = product_truth()
    roots = ["ControlSystem", "AuthorizedBaseline", "StatusCut", "PerformanceAssessment", "ChangeControlCase", "BaselineRevision", "PortfolioRollup", "ControlPeriod"]
    ddd = {
        "domain_vision_statement": "Own provider-neutral authorized delivery-baseline, status, performance, change and control-reporting lifecycles without acquiring planning, finance, contract, analytics or execution authority.",
        "subdomain_classification": "core_horizontal_project_programme_portfolio_controls_product",
        "bounded_context_boundary": {"inside": ["control-system editions", "authorized scope schedule cost and resource baselines", "control accounts and responsibility structure", "data dates status cuts and evidence admission", "earned-value and variance measurement", "completion control forecasts", "change cases decisions and successor baselines", "programme and portfolio rollups", "control-period close and reports"], "outside": ["planning alternative selection", "schedule engine algorithms", "contract commitment invoice payment and ledger truth", "generic workflow", "identity delegation and approval issuance", "source telemetry", "root-cause and other analytical method semantics", "corrective action execution and actual outcome truth"]},
        "ubiquitous_language_policy": "Plan alternative, authorized baseline, current schedule, status cut, progress observation, earned value, actual cost, variance, forecast, change proposal, approval, baseline revision, corrective action, execution effect and outcome are non-interchangeable.",
        "context_map": [
            {"neighbor_ref": "product.integrated_planning_workbench", "relationship": "customer_supplier", "translation": "consume selected delivery intent; controls creates an authorized measurement baseline only through its own authority transition"},
            {"neighbor_ref": "context.scheduling_engine", "relationship": "anti_corruption_layer", "translation": "consume schedule calculations and current editions without transferring baseline authority"},
            {"neighbor_ref": "context.finance_ledger", "relationship": "anti_corruption_layer", "translation": "consume exact actual-cost cuts; controls never becomes ledger truth"},
            {"neighbor_ref": "context.contract_procurement", "relationship": "anti_corruption_layer", "translation": "consume commitments changes and payment-application facts without treating approval as payment"},
            {"neighbor_ref": "context.identity_authority_policy", "relationship": "conformist_with_acl", "translation": "consume decision rights delegation maker-checker and revocation evidence"},
            {"neighbor_ref": "context.analytics_services", "relationship": "open_host_service_consumer", "translation": "consume attributed statistics predictions diagnoses and scenarios as findings only"},
            {"neighbor_ref": "context.operational_execution", "relationship": "separate_ways", "translation": "execution owns corrective effects and observed outcomes"},
        ],
        "anti_corruption_layers": ["acl.integrated_planning_to_baseline", "acl.schedule_engine", "acl.finance_actual_cost", "acl.contract_commitment_payment", "acl.progress_evidence", "acl.identity_authority", "acl.analytics_findings", "acl.corrective_effect"],
        "published_language": ["ControlSystemEdition", "AuthorizedBaselineEdition", "ControlAccount", "StatusCut", "ProgressAdmission", "PerformanceMeasurement", "VarianceAnalysis", "CompletionForecast", "ChangeControlCase", "ChangeDecision", "BaselineRevision", "PortfolioRollup", "ControlPeriodClose", "ControlReportEdition", "TypedRefusal"],
        "value_objects": ["ControlSystemId", "EditionId", "ProjectProgrammePortfolioRef", "CalendarRef", "DataDate", "ScopeCut", "ScheduleCut", "BudgetCut", "ResourceCut", "ActualCostCut", "AuthorizationRef", "FormulaEdition", "RollupProfile"],
        "entities": roots + ["ControlAccount", "WorkPackage", "ProgressObservation", "MeasurementOccurrence", "ChangeProposal", "ApprovalDecision", "ControlReportEdition"],
        "aggregates": [{"root": root, "consistency": f"{root} changes only through editioned commands with exact authority, cuts, evidence, version and typed refusals."} for root in roots],
        "aggregate_roots": roots,
        "aggregate_invariants": truth["invariants"] + ["published results bind exact baseline status method provider authority and time cuts", "unknown state remains unknown until reconciled", "optional automation never closes missing evidence or authority"],
        "commands": truth["commands"], "domain_events": truth["events"],
        "refusal_failure_catalog": truth["refusals"] + ["provider_failure", "resource_exhausted", "cancelled", "unknown_terminal_state", "optional_assistance_unavailable"],
        "domain_services": ["BaselineAuthorityService", "StatusAdmissionService", "PerformanceMeasurementService", "VarianceForecastService", "ChangeControlService", "RebaselineService", "PortfolioRollupService", "ControlPeriodCloseService"],
        "application_services": ["AuthorizeBaselineUseCase", "CollectAndSealStatusUseCase", "MeasureAndForecastUseCase", "DecideChangeUseCase", "PublishSuccessorBaselineUseCase", "RollupPortfolioUseCase", "CloseAndReportPeriodUseCase"],
        "repositories": [f"{root}Repository" for root in roots], "factories": [f"{root}Factory" for root in roots],
        "specifications": ["BaselineCoherenceSpecification", "AuthorizationSpecification", "StatusCutCompletenessSpecification", "ProgressEvidenceSpecification", "MeasurementComparabilitySpecification", "ChangeImpactSpecification", "MakerCheckerSpecification", "BaselineDeltaSpecification", "PortfolioRollupSpecification", "PeriodCloseSpecification"],
        "state_machine": {"baseline": ["proposed", "validation", "authorization_pending", "authorized", "active", "revision_pending", "superseded", "recalled"], "status_cut": ["open", "collecting", "admission_review", "sealed", "measured", "closed"], "change_case": ["draft", "impact_assessment", "decision_pending", "approved", "rejected", "returned", "incorporated", "withdrawn"]},
        "policies_and_reactions": ["when baseline authority is missing refuse activation", "when a data date closes freeze its status cut", "when progress evidence is insufficient preserve unknown", "when thresholds are breached open review but do not infer cause", "when change is approved require a traceable successor-baseline transition", "when a baseline changes preserve prior editions and in-flight disposition", "when analytics proposes action require external decision and effect authority", "when optional automation is removed preserve the deterministic control lifecycle"],
        "sagas_and_process_managers": ["BaselineAuthorizationProcess", "StatusPeriodProcess", "MeasurementAndForecastProcess", "ChangeControlProcess", "BaselineRevisionProcess", "PortfolioRollupProcess", "ControlPeriodCloseProcess"],
        "read_models_and_projections": ["AuthorizedBaselineView", "ControlAccountView", "CurrentScheduleAgainstBaselineView", "StatusEvidenceView", "EarnedValueView", "VarianceForecastView", "ChangeCaseView", "BaselineHistoryView", "PortfolioControlView", "PeriodCloseView", "ControlEvidenceView"],
        "integration_event_policy": "Only editioned baseline, status admission, measurement, forecast, change decision, successor baseline, rollup and close/report facts cross the boundary. Planning alternatives, ledger and contract truth, raw provider internals, analytical findings and execution effects remain external.",
        "concurrency_and_idempotency": ["optimistic aggregate editions", "commands bind edition and idempotency key", "authorized baselines and sealed status cuts are immutable", "parallel evidence occurrences retain identity", "unknown external effects reconcile before retry", "rollups use frozen membership and source cuts"],
        "time_model": ["baseline validity and recording time are distinct", "data date observation admission accounting forecast decision and publication times are distinct", "calendars rates authority and policies are editioned", "change effective time never rewrites prior validity", "portfolio rollups bind exact membership and source cuts"],
        "event_storming_swimlanes": ["project_manager", "project_controls_manager", "control_account_manager", "scheduler", "cost_engineer", "progress_evidence_owner", "finance_owner", "contract_owner", "change_control_board", "sponsor", "analytics_provider", "execution_owner", "assurance_reviewer"],
        "nonfunctional_laws": ["finite projects accounts activities periods changes inputs attempts runtime memory output cost and deadlines", "cooperative cancellation and typed partial validity", "determinism rounding currency calendars tolerances and aggregation are explicit", "all receipts bind exact semantic data authority provider and time cuts", "cross-provider differential and negative twins", "provider identity cannot change control meaning", "fail closed on missing baseline evidence or authority", "recovery never duplicates effects or rewrites history", AUTOMATION["removal_law"]],
    }
    assert set(ddd) == DDD_FIELDS
    return {"dossier_id": "ddd.project_controls.project_portfolio_controls", "product_ref": PRODUCT, "status": "candidate_not_ratified", "product_truth": {"sovereign_question": truth["sovereign_question"], "users": truth["users"], "harmed_parties": truth["harmed_parties"], "jobs": truth["jobs"], "measurable_outcomes": truth["outcomes"], "negative_mission": truth["negative_mission"]}, "strategic_and_tactical_ddd": ddd}


def enrich_project_controls(source: dict[str, Any]) -> dict[str, Any]:
    artifact_ids = {SEMANTIC_OWNER, PRODUCT, *[local_capability(key) for key in KEYS]}
    library_ids = {local_library(key) for key in KEYS}
    source["sources"] = [row for row in source["sources"] if row["source_id"] not in set(EVIDENCE)] + SOURCES
    source["artifacts"] = [row for row in source["artifacts"] if row["artifact_id"] not in artifact_ids] + artifacts()
    source["libraries"] = [row for row in source["libraries"] if row["library_id"] not in library_ids] + [library(key) for key in KEYS]
    source["requirements"] = [row for row in source["requirements"] if not row["requirement_id"].startswith("requirement.project_controls.")]
    source["binding_maps"] = [row for row in source.get("binding_maps", []) if not row["binding_map_id"].startswith("binding.project_controls.")]
    source["binding_gaps"] = [row for row in source.get("binding_gaps", []) if not row["gap_id"].startswith("gap.project_controls.")]
    source["boundary_decisions"] = [row for row in source["boundary_decisions"] if row["decision_id"] != "decision.methods.project_portfolio_controls"] + [boundary_decision()]
    source["crosswalks"] = [row for row in source["crosswalks"] if row["legacy_ref"] != "candidate.product.project_portfolio_controls"] + [{"legacy_ref": "candidate.product.project_portfolio_controls", "canonical_refs": [PRODUCT, SEMANTIC_OWNER, *sorted(library_ids)], "disposition": "promote_horizontal_product_and_split_exact_control_libraries", "edition": 1}]
    source["relations"] = [row for row in source["relations"] if not row["relation_id"].startswith("relation.project_controls.")]
    source["relations"].extend([
        {"relation_id": "relation.project_controls.requires.planning", "from_ref": PRODUCT, "predicate": "requires", "to_ref": "product.integrated_planning_workbench", "binding_phase": "compile_time", "edition": 1},
        {"relation_id": "relation.project_controls.requires.forecasting", "from_ref": PRODUCT, "predicate": "requires", "to_ref": "product.forecasting_workbench", "binding_phase": "runtime", "edition": 1},
    ])
    for key in KEYS:
        source["requirements"].append({"requirement_id": f"requirement.project_controls.{key}", "consumer_ref": PRODUCT, "capability_ref": local_capability(key), "binding_phase": "runtime" if key in {"progress_status_cut", "control_period_close_reporting"} else "compile_time", "minimum_qualified_offers": 1, "status": "unbound", "refusal": f"no_qualified_{key}_implementation"})
        source["binding_maps"].append({"binding_map_id": f"binding.project_controls.{key}", "abstract_library_ref": local_library(key), "concrete_library_refs": [], "concrete_requirement_refs": [], "composition_law": "Project-controls semantics are exact and product-owned; planning, scheduling, finance, contract, authority, analytics and execution remain typed imports.", "bindability": "structurally_partial_blocking_gap", "blocking_gap_refs": [f"gap.project_controls.{key}"], "modality_posture": "deterministic_core", "minimum_qualified_implementations_per_required_contract": 1, "portable_claim_minimum_independent_implementations": 2, "qualification_profile_refs": [], "substitution_law": "Baseline identity, status cuts, measurement, change authority, history, reporting evidence and typed refusals survive implementation substitution.", "cross_provider_differential_required": True, "fallback_law": "refuse", "status": "candidate_not_bound", "product_refs": [PRODUCT]})
        source["binding_gaps"].append({"gap_id": f"gap.project_controls.{key}", "status": "open", "product_refs": [PRODUCT], "abstract_library_refs": [local_library(key)], "missing_contracts": [key], "statement": f"No current compiler contribution implements the complete provider-neutral {key.replace('_', ' ')} contract.", "compiler_disposition": f"Add an editioned pure project-controls library for {key} with executable laws, finite bounds, exact refusals and two independently qualified implementations."})
    negative_rows = [
        ("planning_baseline", "A planning alternative is an authorized control baseline.", "require a separate coherent authorization transition"),
        ("baseline_current", "The current schedule or forecast may overwrite the baseline.", "preserve immutable editions and explicit variance"),
        ("progress_earned", "A progress claim automatically earns value.", "require evidence admission and declared measurement technique"),
        ("variance_cause", "Variance proves its root cause.", "publish variance only and invoke a separate diagnostic contract"),
        ("forecast_change", "Forecast at completion changes the authorized baseline.", "require an approved change and successor baseline"),
        ("approval_revision", "Change approval is the revised baseline.", "require traceable incorporation and publication"),
        ("cost_ledger", "Project cost control is financial-ledger truth.", "bind exact ledger cuts through an ACL"),
        ("payment_effect", "An approved payment application proves payment.", "require external payment-effect evidence"),
        ("analytics_control", "An analytics subscription or finding may directly mutate control state.", "require application decision and effect authority"),
        ("rollup_mutation", "Portfolio rollup may repair or overwrite source projects.", "publish residuals without source mutation"),
        ("agent_authority", "A model or agent may supply missing baseline evidence or approval.", "retain proposal provenance and refuse missing authority"),
    ]
    source["negative_tests"] = [row for row in source["negative_tests"] if not row["test_id"].startswith("negative.project_controls.")]
    source["negative_tests"].extend({"test_id": f"negative.project_controls.{key}", "prohibited_claim": claim, "expected_result": result} for key, claim, result in negative_rows)
    laws = set(product_truth()["invariants"])
    source["non_collapse_laws"] = [law for law in source["non_collapse_laws"] if law not in laws] + sorted(laws)
    source["ddd_dossiers"] = [row for row in source.get("ddd_dossiers", []) if row.get("product_ref") != PRODUCT] + [dossier()]
    return source
