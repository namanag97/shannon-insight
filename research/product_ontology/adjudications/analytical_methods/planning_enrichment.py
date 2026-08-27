#!/usr/bin/env python3
"""Add the horizontal Integrated Planning Workbench product without absorbing its suppliers.

Planning owns the editioned scenario-to-commitment coordination lifecycle. Forecasting owns future
estimates; optimization and simulation own method results; vertical contexts own business meaning;
authority owners approve decisions; execution systems own effects and observed outcomes.
"""

from __future__ import annotations

from typing import Any


PRODUCT = "product.integrated_planning_workbench"
SEMANTIC_OWNER = "semantic.integrated_planning"
PRODUCT_FIELDS = {
    "sovereign_question", "users", "harmed_parties", "jobs", "outcomes", "negative_mission",
    "lifecycle_states", "commands", "events", "invariants", "refusals", "automation_modality",
}
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
    "law": "Statistical, learned, generative or agentic systems may supply attributed forecasts, proposals, scenarios, explanations or candidate repairs only. Deterministic identity, time, assumption, constraint, authority, transition, publication and evidence laws decide admissibility.",
    "removal_law": "Removing every optional model, LLM or agent preserves plan definition, scenario and assumption management, alternative comparison, cross-functional reconciliation, governed review, approval, publication, variance and replanning; an explicitly required unavailable aid yields capability_unavailable.",
    "hard_work_law": "Automation never invents vertical vocabulary, actual truth, objective authority, hard constraints, resource ownership, approval rights, commitment, release permission, effect completion or outcome truth.",
}

SOURCES = [
    {
        "source_id": "source.planning.ascm.dictionary", "source_class": "official_professional_standard",
        "title": "ASCM Supply Chain Dictionary", "publisher": "Association for Supply Chain Management",
        "uri": "https://learn.ascm.org/sfc/servlet.shepherd/document/download/069R3000006PlDHIA0?operationContext=S1",
        "retrieved_at": "2026-08-27",
        "claim": "Defines integrated business planning as cross-functional strategic, operational and financial planning that balances demand, supply and resources to form an enterprise operating plan.",
        "scope_limit": "Defines professional vocabulary and process scope; it does not specify a software architecture, provider qualification or enterprise decision authority.",
    },
    {
        "source_id": "source.planning.afp.pbf", "source_class": "official_professional_guidance",
        "title": "Planning, Budgeting and Forecasting", "publisher": "Association for Financial Professionals",
        "uri": "https://www.afponline.org/topics/fp-a-topics/planning-budgeting-and-forecasting",
        "retrieved_at": "2026-08-27",
        "claim": "Separates planning and resource-allocation coordination from forecasting and budgeting inputs.",
        "scope_limit": "Financial-planning guidance does not define supply, workforce, project or operational planning semantics and does not prove a software boundary alone.",
    },
    {
        "source_id": "source.planning.sap.versions_scenarios", "source_class": "official_product_documentation",
        "title": "Planning Versions and Scenarios", "publisher": "SAP",
        "uri": "https://help.sap.com/docs/SAP_INTEGRATED_BUSINESS_PLANNING/09154e4f345c46edb1d74f782be4d9bd/8814a357dd6a6b10e10000000a441470.html",
        "retrieved_at": "2026-08-27",
        "claim": "Documents separate planning versions, scenarios, version-specific figures and data, simulations, scenario promotion and planning jobs.",
        "scope_limit": "Documents one provider's semantics; its packaging and implementation details are not the portable contract.",
    },
    {
        "source_id": "source.planning.sap.integrated_process", "source_class": "official_product_documentation",
        "title": "Example: Integrated Planning Process with Unified Planning Area", "publisher": "SAP",
        "uri": "https://help.sap.com/docs/SAP_INTEGRATED_BUSINESS_PLANNING/feae3cea3cc549aaa9d9de7d363a83e6/bea60e563f3e787fe10000000a441470.html",
        "retrieved_at": "2026-08-27",
        "claim": "Documents demand, inventory, supply and S&OP stages that exchange plans and culminate in consensus review.",
        "scope_limit": "A sample process is evidence of lifecycle and composition, not universal sequencing or authority.",
    },
    {
        "source_id": "source.planning.oracle.manage_plans", "source_class": "official_product_documentation",
        "title": "Actions to Manage Your Plans", "publisher": "Oracle",
        "uri": "https://docs.oracle.com/en/cloud/saas/supply-chain-and-manufacturing/26a/fasdm/actions-to-manage-your-plans.html",
        "retrieved_at": "2026-08-27",
        "claim": "Documents create, duplicate, compare, run, approve, archive, publish, release and inspect-status operations over plan identities.",
        "scope_limit": "Oracle action names and plan types are provider DTOs, not portable semantic ownership.",
    },
    {
        "source_id": "source.planning.oracle.sop_flow", "source_class": "official_product_documentation",
        "title": "Business Flows for Sales and Operations Planning", "publisher": "Oracle",
        "uri": "https://docs.oracle.com/en/cloud/saas/supply-chain-and-manufacturing/26a/fasop/business-flows-for-sales-and-operations-planning.html",
        "retrieved_at": "2026-08-27",
        "claim": "Documents product, demand, supply, financial and executive review stages, comparison of simulation plans, consensus approval and handoff toward execution.",
        "scope_limit": "Does not prove that approval caused an external execution effect or that the documented flow fits every vertical.",
    },
    {
        "source_id": "source.planning.pigment.versions_scenarios", "source_class": "official_product_documentation",
        "title": "Versions and Scenarios", "publisher": "Pigment",
        "uri": "https://kb.pigment.com/docs/versions-scenarios",
        "retrieved_at": "2026-08-27",
        "claim": "Distinguishes repeatable auditable planning versions from ad-hoc what-if scenarios and supports their combined use.",
        "scope_limit": "Product guidance does not establish a universal data model or qualification of the implementation.",
    },
    {
        "source_id": "source.planning.pigment.version_implementation", "source_class": "official_product_documentation",
        "title": "Implement Versions and Plans in Pigment", "publisher": "Pigment",
        "uri": "https://kb.pigment.com/docs/managing-versions-in-pigment",
        "retrieved_at": "2026-08-27",
        "claim": "Documents planning-cycle editions, switchover between actuals and plan periods, locking after approval, scenario labels, variance comparison and rolling reforecast initialization.",
        "scope_limit": "Recommended model configuration is implementation evidence, not a mandatory portable representation.",
    },
    {
        "source_id": "source.planning.anaplan.workflow", "source_class": "official_product_documentation",
        "title": "Workflow", "publisher": "Anaplan",
        "uri": "https://help.anaplan.com/workflow-d3ef84e7-e883-4b38-af79-889ea825df9f",
        "retrieved_at": "2026-08-27",
        "claim": "Documents separately entitled repeatable task, approval, delegation, notification, monitoring and audit workflow capabilities used by planning processes.",
        "scope_limit": "Supports the seam that generic workflow is an imported product capability; it does not make all workflow planning-owned.",
    },
    {
        "source_id": "source.planning.oracle.approvals", "source_class": "official_product_documentation",
        "title": "Setting Up Approvals in Planning", "publisher": "Oracle",
        "uri": "https://docs.oracle.com/en/cloud/saas/planning-budgeting-cloud/pln-tutorial-approvals/index.html",
        "retrieved_at": "2026-08-27",
        "claim": "Documents approval units, scenario/version review cycles, owners, reviewers, validation rules, annotations, promotion paths and audit trails.",
        "scope_limit": "A provider-specific approval implementation does not supply real-world authority or prove that approval produced an effect.",
    },
]
EVIDENCE = [row["source_id"] for row in SOURCES]


LIBRARIES: dict[str, dict[str, Any]] = {
    "plan_definition_edition": {
        "types": ["PlanDefinitionId", "PlanEdition", "PlanPurpose", "PlanScope", "PlanningHorizon", "PlanningGrain", "Cadence", "PlanStatus"],
        "operations": ["open_plan_definition", "bind_scope_horizon_and_grain", "publish_plan_definition_edition", "supersede_plan_definition"],
        "decisions": ["plan_identity", "purpose", "scope", "grain", "horizon", "cadence", "edition_compatibility"],
        "invariants": ["plan definition edition scenario alternative and publication are distinct", "scope horizon grain calendar and purpose are explicit", "published editions are immutable"],
        "refusals": ["plan_identity_ambiguous", "purpose_unbound", "scope_invalid", "grain_incompatible", "horizon_invalid", "edition_conflict"],
        "dependencies": [],
    },
    "scenario_assumption_contract": {
        "types": ["ScenarioId", "ScenarioEdition", "AssumptionId", "AssumptionValue", "AssumptionSource", "ControlClassification", "InheritanceRule", "Incompatibility"],
        "operations": ["create_scenario", "bind_assumption", "fork_scenario", "compare_assumption_cuts", "supersede_scenario"],
        "decisions": ["baseline", "inheritance", "exogenous_or_controllable", "assumption_validity", "scenario_compatibility"],
        "invariants": ["scenario is not forecast fact target plan or commitment", "inherited and overridden assumptions remain traceable", "contradictory assumptions cannot silently coexist"],
        "refusals": ["baseline_missing", "assumption_owner_unknown", "assumption_cut_invalid", "scenario_incompatible", "inheritance_cycle"],
        "dependencies": ["plan_definition_edition"],
    },
    "plan_alternative_algebra": {
        "types": ["PlanAlternativeId", "AlternativeEdition", "DecisionVariableBinding", "ResourceAssignment", "PlanOutput", "Residual", "AlternativeStatus"],
        "operations": ["open_alternative", "bind_choices", "attach_method_result", "seal_alternative", "supersede_alternative"],
        "decisions": ["alternative_identity", "choice_scope", "method_result_admission", "partiality", "seal_policy"],
        "invariants": ["alternative is not selected plan or commitment", "inputs outputs residuals and provider occurrences bind exact cuts", "partial alternatives never masquerade as complete"],
        "refusals": ["scenario_unbound", "choice_scope_invalid", "provider_result_unqualified", "residual_undeclared", "alternative_incomplete"],
        "dependencies": ["scenario_assumption_contract"],
    },
    "objective_constraint_resource_binding": {
        "types": ["ObjectiveRef", "PreferenceRef", "ConstraintRef", "ConstraintKind", "ResourceRef", "CapacityCut", "PolicyRef", "AuthorityRef"],
        "operations": ["bind_objective", "bind_constraint", "bind_resource_capacity", "classify_hard_soft_and_preference", "validate_binding_authority"],
        "decisions": ["objective_precedence", "hard_or_soft", "resource_scope", "capacity_validity", "policy_applicability", "binding_authority"],
        "invariants": ["goal objective preference policy hard constraint and resource capacity are distinct", "solver input never grants business authority", "relaxation requires its owning authority"],
        "refusals": ["objective_ambiguous", "constraint_kind_unknown", "resource_owner_unbound", "capacity_cut_stale", "policy_conflict", "relaxation_unauthorized"],
        "dependencies": ["plan_alternative_algebra"],
    },
    "hierarchy_allocation_disaggregation": {
        "types": ["PlanningHierarchy", "AggregationRule", "AllocationRule", "DisaggregationRule", "RoundingPolicy", "ResidualAllocation", "ReconciliationReceipt"],
        "operations": ["aggregate_plan", "allocate_target", "disaggregate_plan", "reconcile_hierarchy", "publish_residuals"],
        "decisions": ["hierarchy_authority", "allocation_basis", "disaggregation_method", "rounding", "residual_precedence"],
        "invariants": ["aggregation allocation disaggregation and reconciliation are distinct", "totals detail and residuals remain traceable", "numeric coherence does not imply feasibility or approval"],
        "refusals": ["hierarchy_invalid", "allocation_basis_missing", "disaggregation_ambiguous", "rounding_residual_unbounded", "reconciliation_failed"],
        "dependencies": ["plan_alternative_algebra"],
    },
    "feasibility_assessment": {
        "types": ["FeasibilityAssessment", "AssessmentScope", "MethodResultRef", "Violation", "Risk", "Limitation", "AssessmentStatus"],
        "operations": ["request_feasibility_assessment", "admit_method_result", "classify_violation", "record_limitations", "publish_assessment"],
        "decisions": ["assessment_scope", "evidence_admission", "violation_severity", "uncertainty_posture", "assessment_status"],
        "invariants": ["feasibility assessment is not solver status selection approval or effect", "every finding binds exact alternative assumptions constraints resources method and data cut", "unknown remains distinct from infeasible"],
        "refusals": ["assessment_scope_missing", "method_result_unqualified", "input_cut_mismatch", "violation_unclassified", "uncertainty_unreported"],
        "dependencies": ["objective_constraint_resource_binding", "hierarchy_allocation_disaggregation"],
    },
    "cross_functional_reconciliation": {
        "types": ["PlanContribution", "ContributionOwner", "SemanticMapping", "PlanConflict", "ConflictDisposition", "Escalation", "ReconciliationCase"],
        "operations": ["submit_plan_contribution", "translate_contribution", "detect_conflict", "propose_resolution", "escalate_or_resolve", "seal_reconciliation"],
        "decisions": ["contribution_admission", "semantic_mapping", "conflict_kind", "precedence", "resolution_authority", "escalation_path"],
        "invariants": ["demand supply capacity inventory workforce project and financial meanings remain owned by their vertical contexts", "conflict resolution is not numeric averaging", "unresolved conflicts remain visible"],
        "refusals": ["contribution_owner_missing", "semantic_mapping_missing", "incomparable_grain_or_time", "conflict_unclassified", "resolution_authority_missing", "reconciliation_open"],
        "dependencies": ["feasibility_assessment"],
    },
    "alternative_comparison_selection": {
        "types": ["ComparisonSet", "ComparisonProfile", "Criterion", "Tradeoff", "DominanceFinding", "SelectionProposal", "SelectionEvidence"],
        "operations": ["register_comparison_set", "bind_criteria", "compare_alternatives", "publish_tradeoffs", "propose_selection"],
        "decisions": ["candidate_admission", "criterion_semantics", "tradeoff_policy", "robustness_scope", "selection_proposal"],
        "invariants": ["comparison is not selection and selection proposal is not approval", "criteria preserve units directions uncertainty and authority", "one scalar score cannot silently erase tradeoffs"],
        "refusals": ["comparison_set_invalid", "criterion_ambiguous", "units_incomparable", "tradeoff_policy_missing", "evidence_insufficient"],
        "dependencies": ["cross_functional_reconciliation"],
    },
    "review_consensus_approval_commitment": {
        "types": ["ReviewCycle", "ReviewStage", "ContributionDecision", "ConsensusFinding", "ApprovalRequest", "ApprovalDecision", "Commitment", "DecisionRightRef"],
        "operations": ["open_review_cycle", "submit_for_review", "record_contribution_decision", "record_consensus", "request_approval", "approve_reject_or_return", "record_commitment"],
        "decisions": ["review_participants", "stage_entry_exit", "consensus_rule", "maker_checker", "approval_authority", "commitment_scope"],
        "invariants": ["proposal review consensus approval commitment release and effect are distinct", "consensus never manufactures authority", "maker checker and delegation rules are imported and enforced"],
        "refusals": ["review_scope_invalid", "required_contribution_missing", "consensus_rule_unbound", "approval_authority_missing", "maker_checker_violated", "commitment_scope_ambiguous"],
        "dependencies": ["alternative_comparison_selection"],
    },
    "plan_publication_release": {
        "types": ["PlanPublicationEdition", "Audience", "Purpose", "DisclosureProfile", "ReleaseIntent", "ExecutionPortRef", "RecallNotice", "DeliveryReceipt"],
        "operations": ["approve_publication", "publish_plan_edition", "emit_release_intent", "record_delivery", "retract_or_recall", "supersede_publication"],
        "decisions": ["publication_authority", "audience_and_purpose", "disclosure", "release_scope", "expiry", "recall_scope"],
        "invariants": ["approval is not publication release delivery execution or effect", "publication preserves plan scenario assumptions constraints authority and edition", "recall never deletes history"],
        "refusals": ["publication_authority_missing", "audience_invalid", "disclosure_denied", "execution_port_unqualified", "delivery_unknown", "recall_scope_ambiguous"],
        "dependencies": ["review_consensus_approval_commitment"],
    },
    "plan_variance_replan": {
        "types": ["ActualCutRef", "PlanActualJoin", "Variance", "AssumptionBreach", "ReplanTrigger", "ReplanCase", "SupersessionLink", "InFlightDisposition"],
        "operations": ["join_plan_to_actuals", "calculate_variance", "evaluate_assumption_breach", "open_replan_case", "supersede_plan", "dispose_in_flight_work"],
        "decisions": ["actual_cut", "variance_semantics", "trigger_policy", "reforecast_or_replan", "supersession", "in_flight_disposition"],
        "invariants": ["actual forecast plan commitment execution and outcome remain distinct", "variance binds exact plan and actual editions", "replanning never rewrites prior plan history"],
        "refusals": ["actual_cut_unbound", "grain_or_time_mismatch", "variance_definition_missing", "trigger_ambiguous", "replan_authority_missing", "in_flight_disposition_unknown"],
        "dependencies": ["plan_publication_release"],
    },
    "planning_cycle_calendar": {
        "types": ["PlanningCycleId", "CycleEdition", "StageSchedule", "BusinessCalendarRef", "Deadline", "DependencyGate", "EscalationPolicy", "CycleStatus"],
        "operations": ["open_planning_cycle", "schedule_stage", "evaluate_gate", "record_deadline_status", "escalate_cycle", "close_cycle"],
        "decisions": ["cycle_cadence", "calendar", "stage_dependency", "deadline", "late_input_policy", "escalation"],
        "invariants": ["generic workflow task and planning semantic stage are distinct", "calendar and deadline editions are explicit", "late or missing inputs remain visible"],
        "refusals": ["cycle_edition_missing", "calendar_unbound", "stage_dependency_cycle", "deadline_invalid", "required_input_late", "escalation_owner_missing"],
        "dependencies": ["plan_definition_edition"],
    },
    "vertical_vocabulary_acl": {
        "types": ["VerticalProfileRef", "TermMapping", "MeasureMapping", "DimensionMapping", "UnitMapping", "AuthorityMapping", "LossDeclaration"],
        "operations": ["bind_vertical_profile", "translate_vertical_term", "translate_measure_and_dimension", "validate_unit_mapping", "publish_translation_loss"],
        "decisions": ["profile_edition", "term_mapping", "grain_mapping", "unit_conversion", "authority_translation", "loss_acceptance"],
        "invariants": ["horizontal planning never owns finance demand supply capacity inventory workforce or project vocabulary", "translation loss is explicit", "same spelling never implies same meaning"],
        "refusals": ["vertical_profile_missing", "term_ambiguous", "grain_mapping_invalid", "unit_conversion_unsupported", "authority_mapping_missing", "loss_unaccepted"],
        "dependencies": ["plan_definition_edition"],
    },
}
KEYS = list(LIBRARIES)


def local_library(key: str) -> str:
    return f"library.analytics_planning.{key}"


def local_capability(key: str) -> str:
    return f"capability.analytics_planning.{key}"


def product_truth() -> dict[str, Any]:
    return {
        "sovereign_question": "Given editioned vertical objectives, forecasts, assumptions, constraints, resources, actuals and decision rights, which explicitly compared plan alternative may progress through reconciliation, review, approval, commitment, publication and replanning—with every tradeoff, residual, authority and handoff preserved—without becoming an observed fact or executed effect?",
        "users": ["planning_process_owner", "functional_planner", "finance_partner", "operations_planner", "resource_owner", "scenario_analyst", "plan_reviewer", "decision_authority", "execution_coordinator", "assurance_reviewer"],
        "harmed_parties": ["worker", "customer", "supplier", "resource_owner", "budget_owner", "community_or_environment", "decision_affected_party"],
        "jobs": ["Define an editioned planning cycle; bind vertical inputs and decision rights; create scenarios and alternatives; assess feasibility; reconcile cross-functional conflicts; compare tradeoffs; review and approve a plan; publish or release it; join actuals, detect variance and replan without rewriting history."],
        "outcomes": ["editioned_plan_definition", "traceable_scenario_assumption_cut", "comparable_plan_alternatives", "qualified_feasibility_assessment", "explicit_cross_functional_conflict_resolution", "authority_bearing_review_and_approval_record", "immutable_plan_publication", "typed_release_intent", "plan_actual_variance_and_replan_evidence"],
        "negative_mission": "Does not own source or actual truth, vertical business vocabulary, forecast generation, statistical inference, simulation or optimization method semantics, generic workflow execution, identity or authority issuance, budget/resource ownership, operational execution, effect completion or outcome truth.",
        "lifecycle_states": ["draft", "definition_bound", "cycle_open", "inputs_pending", "scenario_building", "alternatives_building", "feasibility_pending", "reconciliation_pending", "comparison_pending", "review_pending", "consensus_recorded", "approval_pending", "approved", "committed", "publication_pending", "published", "release_pending", "released", "active", "variance_review", "replan_pending", "superseded", "retracted", "recalled", "closed", "refused"],
        "commands": ["open_plan_definition", "open_planning_cycle", "bind_vertical_profile", "bind_forecast_and_actual_cuts", "create_scenario", "bind_assumptions_objectives_constraints_and_resources", "create_plan_alternative", "request_feasibility_assessment", "submit_functional_contribution", "reconcile_plan_conflicts", "compare_alternatives", "open_review", "record_consensus", "request_plan_approval", "approve_reject_or_return_plan", "record_commitment", "publish_plan_edition", "emit_release_intent", "join_actuals_and_evaluate_variance", "open_replan_case", "supersede_retract_or_recall_plan"],
        "events": ["plan_definition_opened", "planning_cycle_opened", "vertical_profile_bound", "forecast_and_actual_cuts_bound", "scenario_created", "assumptions_objectives_constraints_and_resources_bound", "plan_alternative_created", "feasibility_assessed", "functional_contribution_submitted", "plan_conflicts_reconciled", "alternatives_compared", "plan_review_opened", "consensus_recorded", "plan_approval_requested", "plan_approved_rejected_or_returned", "commitment_recorded", "plan_edition_published", "release_intent_emitted", "actuals_joined_and_variance_evaluated", "replan_case_opened", "plan_superseded_retracted_or_recalled"],
        "invariants": ["observation actual forecast scenario assumption target budget plan alternative selected plan approval commitment publication release execution effect and outcome are distinct", "plan definition edition cycle scenario alternative and publication identities never collapse", "vertical vocabulary and authority remain imported and attributable", "all alternatives bind exact forecasts actuals assumptions constraints resources methods and provider occurrences", "hard constraints never silently become soft preferences", "cross-functional reconciliation preserves conflicts and responsible owners", "comparison never implies selection and consensus never implies approval", "approval never implies publication release delivery execution or effect", "variance binds exact plan and actual editions", "replanning supersedes rather than rewrites history"],
        "refusals": ["vertical_profile_unbound", "plan_scope_horizon_or_grain_invalid", "forecast_or_actual_cut_unbound", "scenario_assumption_conflict", "objective_or_constraint_authority_missing", "resource_capacity_stale", "alternative_incomplete", "method_result_unqualified", "feasibility_unknown", "cross_functional_conflict_open", "comparison_criteria_ambiguous", "required_review_input_missing", "consensus_rule_unbound", "approval_authority_missing", "maker_checker_violated", "publication_or_release_scope_invalid", "execution_port_unqualified", "delivery_or_effect_unknown", "variance_semantics_missing", "replan_authority_missing"],
        "automation_modality": AUTOMATION,
    }


def artifact_rows() -> list[dict[str, Any]]:
    truth = product_truth()
    rows = [{
        "artifact_id": SEMANTIC_OWNER, "kind": "semantic_contract", "name": "Integrated planning lifecycle semantics",
        "status": "candidate", "semantic_owner_ref": None, "adoption_unit": False, "operated": False,
        "definition": "Owns portable plan definition, scenario, alternative, reconciliation, review, commitment, publication, variance and replanning identities while importing vertical meaning, method results, authority and effects.",
        "evidence_refs": EVIDENCE,
    }, {
        "artifact_id": PRODUCT, "kind": "product", "name": "Integrated Planning Workbench and Service",
        "status": "candidate", "semantic_owner_ref": SEMANTIC_OWNER, "adoption_unit": True, "operated": True,
        "definition": "Coordinates editioned cross-functional planning from scenarios and alternatives through reconciliation, approval, publication and replanning.",
        "evidence_refs": EVIDENCE,
        **truth,
    }]
    rows.extend({
        "artifact_id": local_capability(key), "kind": "capability", "name": key.replace("_", " ").title(),
        "status": "specified_candidate", "semantic_owner_ref": SEMANTIC_OWNER, "adoption_unit": False, "operated": False,
        "definition": f"Provide planning {key.replace('_', ' ')} with exact identity, time, authority, refusal and evidence semantics.",
        "evidence_refs": EVIDENCE,
    } for key in KEYS)
    return rows


def library_row(key: str) -> dict[str, Any]:
    spec = LIBRARIES[key]
    return {
        "library_id": local_library(key), "class": "semantic_policy_pure" if key != "plan_publication_release" else "semantic_effect_intent_port",
        "owner_ref": SEMANTIC_OWNER, "provides": [local_capability(key)],
        "types": spec["types"], "operations": spec["operations"], "decisions": spec["decisions"],
        "invariants": spec["invariants"], "refusals": spec["refusals"],
        "dependencies": [local_library(dep) for dep in spec["dependencies"]],
        "effect_boundary": "pure_effect_intents_only" if key == "plan_publication_release" else "pure_no_io",
        "evidence_refs": EVIDENCE, "product_refs": [PRODUCT],
    }


def boundary_decision() -> dict[str, Any]:
    axis_sources = {
        "user": ["source.planning.ascm.dictionary", "source.planning.oracle.sop_flow"],
        "job": ["source.planning.ascm.dictionary", "source.planning.oracle.sop_flow"],
        "adoption": ["source.planning.sap.versions_scenarios", "source.planning.pigment.versions_scenarios"],
        "semantics": ["source.planning.sap.versions_scenarios", "source.planning.pigment.versions_scenarios", "source.planning.oracle.manage_plans"],
        "authority": ["source.planning.oracle.approvals", "source.planning.oracle.sop_flow"],
        "lifecycle": ["source.planning.oracle.manage_plans", "source.planning.pigment.version_implementation"],
        "operation": ["source.planning.sap.integrated_process", "source.planning.oracle.manage_plans"],
        "economics": ["source.planning.sap.integrated_process", "source.planning.anaplan.workflow"],
        "interface": ["source.planning.oracle.manage_plans", "source.planning.sap.versions_scenarios"],
        "market_evidence": ["source.planning.sap.versions_scenarios", "source.planning.oracle.manage_plans", "source.planning.pigment.versions_scenarios"],
    }
    return {
        "decision_id": "decision.methods.integrated_planning_workbench", "subject_ref": PRODUCT,
        "disposition": "strong_product_candidate",
        "rationale": "ASCM defines a cross-functional enterprise operating-plan process, while SAP, Oracle and Pigment independently expose stable scenario/version, comparison, review, approval, publication and replanning lifecycles. These remain adoptable and replaceable above forecasting, optimization, simulation, workflow and execution suppliers.",
        "evidence_refs": sorted(set(sum(axis_sources.values(), []))),
        "split_test": {axis: {"score": 2, "evidence_refs": refs} for axis, refs in axis_sources.items()},
        "supersedes": ["candidate.product.integrated_planning_workbench"],
    }


def dossier() -> dict[str, Any]:
    truth = product_truth()
    roots = ["PlanDefinition", "PlanningCycle", "PlanningScenario", "PlanAlternative", "ReconciliationCase", "PlanDecisionCase", "PlanPublication", "ReplanCase"]
    ddd = {
        "domain_vision_statement": "Own a provider-neutral, cross-functional plan lifecycle from editioned scenarios and alternatives through reconciliation, accountable approval, publication and replanning without acquiring vertical, method, authority or execution ownership.",
        "subdomain_classification": "core_horizontal_integrated_planning_workbench_and_service_product",
        "bounded_context_boundary": {
            "inside": ["plan definition scope grain horizon cadence and editions", "planning cycles stages deadlines and semantic gates", "scenario assumptions inheritance and incompatibility", "plan alternatives and exact imported method results", "objective constraint resource and authority bindings", "hierarchy allocation disaggregation and residuals", "feasibility assessment and limitations", "cross-functional contribution conflict and reconciliation cases", "alternative comparison tradeoffs and selection proposals", "review consensus approval commitment and maker-checker states", "plan publication release intent recall and supersession", "plan-actual variance trigger and replanning history"],
            "outside": ["actual and source truth", "finance demand supply capacity inventory workforce project and industry vocabulary", "forecast estimation", "simulation experiment and optimization solve semantics", "generic workflow task execution", "identity authority policy and delegation issuance", "resource or budget ownership", "operational execution effect and outcome truth", "provider qualification and vertical acceptance"],
        },
        "ubiquitous_language_policy": "Observation, actual, forecast, scenario, assumption, target, budget, plan definition, plan edition, alternative, feasibility assessment, contribution, conflict, reconciliation, comparison, selection proposal, consensus, approval, commitment, publication, release intent, execution, effect, outcome, variance and replan are non-interchangeable. Vertical homonyms are translated through editioned profiles.",
        "context_map": [
            {"neighbor_ref": "product.forecasting_workbench", "relationship": "customer_supplier", "translation": "consume origin/horizon/information-cut qualified forecast artifacts without turning them into selected plans"},
            {"neighbor_ref": "product.optimization_solver", "relationship": "anti_corruption_layer", "translation": "consume qualified solve results and certificates as alternative evidence only"},
            {"neighbor_ref": "product.simulation_environment", "relationship": "anti_corruption_layer", "translation": "consume scenario experiment outputs and limitations without equating simulation with forecast or approval"},
            {"neighbor_ref": "product.semantic_metric_formula_service", "relationship": "customer_supplier", "translation": "consume editioned measures dimensions formulas units and comparability rules"},
            {"neighbor_ref": "product.master_data_governance", "relationship": "customer_supplier", "translation": "consume governed entity and hierarchy references"},
            {"neighbor_ref": "product.reference_data_governance", "relationship": "customer_supplier", "translation": "consume governed code sets calendars units and classifications"},
            {"neighbor_ref": "context.vertical_business_domains", "relationship": "anti_corruption_layer", "translation": "import vertical terms rules objective owners resources and acceptance profiles"},
            {"neighbor_ref": "context.identity_authority_policy", "relationship": "conformist_with_acl", "translation": "consume principal delegation maker-checker policy and revocation evidence"},
            {"neighbor_ref": "context.generic_workflow", "relationship": "customer_supplier", "translation": "compile planning stages into generic tasks timers notifications and escalations without transferring plan meaning"},
            {"neighbor_ref": "product.operational_activation", "relationship": "effect_port", "translation": "emit approved release intents and reconcile deliveries; activation owns downstream delivery"},
            {"neighbor_ref": "context.operational_execution", "relationship": "separate_ways", "translation": "execution owns commands resources effects and actual outcomes"},
        ],
        "anti_corruption_layers": ["acl.vertical_planning_vocabulary", "acl.actual_and_forecast_inputs", "acl.optimization_and_simulation_results", "acl.metric_and_formula", "acl.master_reference_hierarchy", "acl.identity_authority_policy", "acl.generic_workflow", "acl.execution_release_and_effect"],
        "published_language": ["PlanDefinitionId", "PlanEdition", "PlanningCycleId", "PlanScope", "PlanningHorizon", "PlanningGrain", "ScenarioEdition", "AssumptionCut", "PlanAlternative", "FeasibilityAssessment", "PlanContribution", "ReconciliationCase", "AlternativeComparison", "PlanReview", "ConsensusFinding", "ApprovalDecision", "Commitment", "PlanPublicationEdition", "ReleaseIntent", "PlanActualVariance", "ReplanCase", "RecallNotice", "TypedRefusal"],
        "value_objects": ["PlanDefinitionId", "PlanEditionId", "PurposeRef", "VerticalProfileRef", "Scope", "Grain", "Horizon", "Cadence", "BusinessCalendarRef", "ForecastCutRef", "ActualCutRef", "ScenarioId", "AssumptionCut", "ObjectiveRef", "ConstraintRef", "ResourceCapacityRef", "AuthorityRef", "ComparisonProfile", "PublicationAudience", "ReleaseScope", "VarianceProfile"],
        "entities": roots + ["FunctionalContribution", "FeasibilityAssessment", "ReviewStage", "ApprovalRequest", "Commitment", "ReleaseOccurrence", "VarianceAssessment"],
        "aggregates": [{"root": root, "consistency": f"{root} changes only through editioned commands with exact inputs, authority, evidence, refusals and optimistic versioning."} for root in roots],
        "aggregate_roots": roots,
        "aggregate_invariants": truth["invariants"] + ["every published result binds exact vertical profile, input cuts, assumptions, methods, provider occurrences and authority receipts", "unknown delivery and effect states remain unknown until reconciled", "optional generated proposals retain provenance and never close authority or evidence"],
        "commands": truth["commands"],
        "domain_events": truth["events"],
        "refusal_failure_catalog": truth["refusals"] + ["planning_cycle_deadline_exceeded", "provider_failure", "resource_budget_exhausted", "cancelled", "unknown_terminal_state", "optional_assistance_unavailable"],
        "domain_services": ["PlanDefinitionService", "PlanningCycleService", "ScenarioAssumptionService", "AlternativeService", "FeasibilityAssessmentService", "HierarchyAllocationService", "CrossFunctionalReconciliationService", "AlternativeComparisonService", "PlanReviewAuthorityService", "PlanPublicationService", "PlanVarianceReplanService"],
        "application_services": ["OpenPlanningCycleUseCase", "BuildScenarioAndAlternativesUseCase", "AssessAndReconcilePlanUseCase", "CompareAndReviewAlternativesUseCase", "ApproveAndPublishPlanUseCase", "ReleasePlanUseCase", "EvaluateVarianceAndReplanUseCase", "RecallOrSupersedePlanUseCase"],
        "repositories": [f"{root}Repository" for root in roots],
        "factories": [f"{root}Factory" for root in roots],
        "specifications": ["PlanIdentitySpecification", "ScopeGrainHorizonSpecification", "ScenarioAssumptionConsistencySpecification", "ObjectiveConstraintAuthoritySpecification", "AlternativeCompletenessSpecification", "FeasibilityEvidenceSpecification", "HierarchyResidualSpecification", "CrossFunctionalConflictSpecification", "ComparisonTradeoffSpecification", "ReviewConsensusSpecification", "ApprovalAuthoritySpecification", "PublicationReleaseSpecification", "VarianceReplanSpecification"],
        "state_machine": {
            "plan": truth["lifecycle_states"],
            "scenario": ["draft", "assumptions_pending", "ready", "shared", "promoted", "superseded", "discarded"],
            "alternative": ["draft", "inputs_bound", "method_pending", "partial", "assessed", "reconciled", "comparison_ready", "selected_proposal", "rejected", "superseded"],
            "review": ["not_started", "contributions_pending", "conflict_open", "reconciled", "consensus_pending", "approval_pending", "approved", "rejected", "returned", "committed"],
            "release": ["not_requested", "authorized", "submitted", "acknowledged", "delivered", "partially_delivered", "failed", "cancelled", "unknown", "reconciled"],
        },
        "policies_and_reactions": ["when an input edition changes mark dependent alternatives stale", "when assumptions conflict refuse scenario sealing", "when a hard constraint is violated retain infeasibility unless authorized relaxation is supplied", "when functional plans disagree open a typed conflict with named owners", "when comparison hides units uncertainty or tradeoffs refuse selection proposal", "when consensus lacks required contributors record incomplete consensus", "when approval authority is absent refuse commitment", "when a plan is published freeze its exact edition", "when release completion is unknown reconcile before retry", "when actuals breach assumptions or thresholds open a replan case", "when a plan is superseded preserve in-flight disposition and full history", "when optional automation is removed preserve the deterministic planning lifecycle"],
        "sagas_and_process_managers": ["PlanningCycleProcess", "ScenarioAlternativeProcess", "FeasibilityAndReconciliationProcess", "CrossFunctionalReviewProcess", "PlanApprovalProcess", "PlanPublicationAndReleaseProcess", "VarianceAndReplanProcess", "RecallAndSupersessionProcess"],
        "read_models_and_projections": ["PlanningCycleStatusView", "ScenarioAssumptionView", "AlternativeComparisonView", "ConstraintResourceView", "FeasibilityAndRiskView", "CrossFunctionalConflictView", "ReviewConsensusView", "ApprovalCommitmentView", "PublicationReleaseView", "PlanActualVarianceView", "ReplanAndSupersessionView", "PlanningEvidenceView"],
        "integration_event_policy": "Only editioned plan-definition, scenario, alternative, assessment, conflict, reconciliation, review, approval, commitment, publication, release-intent, variance, replan and recall facts cross the boundary. Vertical truths, method internals, raw authority evidence, provider callbacks, execution effects and actual outcomes remain external.",
        "concurrency_and_idempotency": ["optimistic aggregate editions with explicit conflict refusals", "sealed alternatives approvals and publications are immutable", "commands bind aggregate edition and idempotency key", "parallel method and contribution attempts have occurrence identities", "maker checker and quorum decisions use frozen participant cuts", "release attempts reconcile unknown outcomes before retry", "recall supersession and variance facts are append-only"],
        "time_model": ["source event availability recording forecast origin horizon target plan validity review approval publication release execution effect outcome and evaluation times are distinct", "planning horizon grain cadence and business calendar are editioned", "scenario assumptions objectives constraints capacities policies and authority are bitemporal inputs", "plan and actual cuts are immutable and separately addressable", "deadlines expiry freezes and time fences are explicit", "replanning creates a successor edition and preserves predecessor validity"],
        "event_storming_swimlanes": ["planning_process_owner", "vertical_data_owner", "forecaster", "functional_planner", "optimization_or_simulation_provider", "resource_owner", "finance_partner", "review_participant", "approval_authority", "execution_coordinator", "affected_party", "assurance_reviewer"],
        "nonfunctional_laws": ["finite scenarios alternatives dimensions grains horizons inputs conflicts attempts runtime memory output cost and review deadlines", "cooperative cancellation and typed partial-artifact validity", "determinism randomness approximation schedule dependence and numeric tolerance are explicit", "all receipts bind exact semantic data method provider authority and time cuts", "cross-provider differential and negative-twin fixtures", "provider identity cannot alter planning meaning", "fail closed on missing vertical meaning hard constraints authority publication or release scope", "recovery never duplicates release effects or rewrites plan history", AUTOMATION["removal_law"]],
    }
    assert set(ddd) == DDD_FIELDS
    return {
        "dossier_id": "ddd.analytics.integrated_planning_workbench", "product_ref": PRODUCT,
        "status": "candidate_not_ratified",
        "product_truth": {"sovereign_question": truth["sovereign_question"], "users": truth["users"], "harmed_parties": truth["harmed_parties"], "jobs": truth["jobs"], "measurable_outcomes": truth["outcomes"], "negative_mission": truth["negative_mission"]},
        "strategic_and_tactical_ddd": ddd,
    }


def enrich_planning(source: dict[str, Any]) -> dict[str, Any]:
    artifact_ids = {SEMANTIC_OWNER, PRODUCT, *[local_capability(key) for key in KEYS]}
    library_ids = {local_library(key) for key in KEYS}
    requirement_ids = {f"requirement.analytics_planning.{key}" for key in KEYS}
    map_ids = {f"binding.analytics_planning.{key}" for key in KEYS}
    gap_ids = {f"gap.analytics_planning.{key}" for key in KEYS}
    negative_ids = {f"negative.planning.{key}" for key in ["fact_forecast_plan", "scenario_plan", "objective_authority", "feasibility_selection", "comparison_approval", "consensus_authority", "approval_effect", "variance_rewrite", "vertical_ownership", "agent_authority"]}
    laws = {"actual != forecast != scenario != plan alternative != approved plan != release != execution != effect != outcome", "goal != objective != preference != policy != hard constraint != resource capacity", "comparison != selection proposal != consensus != approval != commitment", "approval != publication != delivery != execution", "replan != mutation of historical plan"}

    source["sources"] = [row for row in source["sources"] if row["source_id"] not in set(EVIDENCE)] + SOURCES
    source["artifacts"] = [row for row in source["artifacts"] if row["artifact_id"] not in artifact_ids] + artifact_rows()
    source["libraries"] = [row for row in source["libraries"] if row["library_id"] not in library_ids] + [library_row(key) for key in KEYS]
    source["requirements"] = [row for row in source["requirements"] if row["requirement_id"] not in requirement_ids]
    source["binding_maps"] = [row for row in source.get("binding_maps", []) if row["binding_map_id"] not in map_ids]
    source["binding_gaps"] = [row for row in source.get("binding_gaps", []) if row["gap_id"] not in gap_ids]
    source["boundary_decisions"] = [row for row in source["boundary_decisions"] if row["decision_id"] != "decision.methods.integrated_planning_workbench"] + [boundary_decision()]
    source["crosswalks"] = [row for row in source["crosswalks"] if row["legacy_ref"] != "candidate.product.integrated_planning_workbench"]
    source["crosswalks"].append({"legacy_ref": "candidate.product.integrated_planning_workbench", "canonical_refs": [PRODUCT, SEMANTIC_OWNER, *sorted(library_ids)], "disposition": "promote_product_and_split_exact_planning_libraries", "edition": 1})
    source["relations"] = [row for row in source["relations"] if not row["relation_id"].startswith("relation.planning.")]
    source["relations"].extend([
        {"relation_id": "relation.planning.requires.forecast", "from_ref": PRODUCT, "predicate": "requires", "to_ref": "product.forecasting_workbench", "binding_phase": "compile_time", "edition": 1},
        {"relation_id": "relation.planning.requires.optimization", "from_ref": PRODUCT, "predicate": "requires", "to_ref": "product.optimization_solver", "binding_phase": "runtime", "edition": 1},
        {"relation_id": "relation.planning.requires.simulation", "from_ref": PRODUCT, "predicate": "requires", "to_ref": "product.simulation_environment", "binding_phase": "runtime", "edition": 1},
        {"relation_id": "relation.planning.packaged", "from_ref": "suite.decision_intelligence", "predicate": "packages", "to_ref": PRODUCT, "binding_phase": "authoring", "edition": 1},
    ])
    for key in KEYS:
        source["requirements"].append({"requirement_id": f"requirement.analytics_planning.{key}", "consumer_ref": PRODUCT, "capability_ref": local_capability(key), "binding_phase": "runtime" if key in {"plan_publication_release", "planning_cycle_calendar"} else "compile_time", "minimum_qualified_offers": 1, "status": "unbound", "refusal": f"no_qualified_{key}_implementation"})
        source["binding_maps"].append({
            "binding_map_id": f"binding.analytics_planning.{key}", "abstract_library_ref": local_library(key),
            "concrete_library_refs": [], "concrete_requirement_refs": [],
            "composition_law": "Planning semantics are exact and product-owned; forecasting, optimization, simulation, workflow, vertical vocabulary, authority and execution remain typed imports.",
            "bindability": "structurally_partial_blocking_gap", "blocking_gap_refs": [f"gap.analytics_planning.{key}"],
            "modality_posture": "deterministic_core", "minimum_qualified_implementations_per_required_contract": 1,
            "portable_claim_minimum_independent_implementations": 2, "qualification_profile_refs": [],
            "substitution_law": "Plan identity scope grain horizon scenario assumptions alternatives conflicts authority state publication variance evidence and typed refusals survive implementation substitution.",
            "cross_provider_differential_required": True, "fallback_law": "refuse", "status": "candidate_not_bound", "product_refs": [PRODUCT],
        })
        source["binding_gaps"].append({
            "gap_id": f"gap.analytics_planning.{key}", "status": "open", "product_refs": [PRODUCT],
            "abstract_library_refs": [local_library(key)], "missing_contracts": [key],
            "statement": f"No current compiler contribution implements the complete provider-neutral {key.replace('_', ' ')} contract with its exact public types, decisions, laws and refusals.",
            "compiler_disposition": f"Add an editioned pure planning library for {key} with conformance oracles, finite bounds, exact refusal contracts, removal seams and at least two independently qualified implementations.",
        })
    source["negative_tests"] = [row for row in source["negative_tests"] if row["test_id"] not in negative_ids]
    source["negative_tests"].extend([
        {"test_id": "negative.planning.fact_forecast_plan", "prohibited_claim": "Actuals forecasts scenarios plans and outcomes are interchangeable.", "expected_result": "preserve exact identity method time and authority cuts"},
        {"test_id": "negative.planning.scenario_plan", "prohibited_claim": "A what-if scenario is the selected or approved plan.", "expected_result": "require comparison review and authority transitions"},
        {"test_id": "negative.planning.objective_authority", "prohibited_claim": "A solver objective or hard constraint invents business authority.", "expected_result": "require imported objective constraint resource and authority owners"},
        {"test_id": "negative.planning.feasibility_selection", "prohibited_claim": "A feasible alternative is selected desirable or approved.", "expected_result": "publish assessment and tradeoffs only"},
        {"test_id": "negative.planning.comparison_approval", "prohibited_claim": "The highest scalar score is an approved commitment.", "expected_result": "preserve criteria uncertainty tradeoffs selection proposal and authority"},
        {"test_id": "negative.planning.consensus_authority", "prohibited_claim": "Consensus creates authority or unanimity.", "expected_result": "record contributors rule dissents and separate approval"},
        {"test_id": "negative.planning.approval_effect", "prohibited_claim": "Approval or release proves downstream execution and effect.", "expected_result": "require delivery execution and outcome receipts"},
        {"test_id": "negative.planning.variance_rewrite", "prohibited_claim": "New actuals may rewrite the historical plan edition.", "expected_result": "open variance and successor replan records"},
        {"test_id": "negative.planning.vertical_ownership", "prohibited_claim": "A horizontal planner owns finance supply workforce or other vertical meanings.", "expected_result": "require exact vertical profile and ACL"},
        {"test_id": "negative.planning.agent_authority", "prohibited_claim": "A model or agent proposal closes missing assumptions constraints evidence or authority.", "expected_result": "retain proposal provenance and deterministic refusal"},
    ])
    source["non_collapse_laws"] = [law for law in source["non_collapse_laws"] if law not in laws] + sorted(laws)
    source["ddd_dossiers"] = [row for row in source.get("ddd_dossiers", []) if row.get("product_ref") != PRODUCT] + [dossier()]
    return source
