#!/usr/bin/env python3
"""Build unrelated, AI-independent vertical composition proof candidates.

The output proves structural reuse and fail-closed binding only.  It deliberately does not claim
that any provider is qualified or that either vertical solution is accepted for production.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
RESEARCH = HERE.parents[2]
EDITION = 1
AS_OF = "2026-08-26"


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def jsonl_text(rows: list[dict[str, Any]], identity: str) -> str:
    return "".join(canonical_json(row) + "\n" for row in sorted(rows, key=lambda row: row[identity]))


def record_label(row: dict[str, Any]) -> str:
    """Return a display label without imposing one on every upstream record contract."""
    for key in ("name", "system_name", "shape_name", "title", "description"):
        value = row.get(key)
        if isinstance(value, str) and value.strip():
            return value
    return row["record_id"]


COMMON_LAYERS = {
    "semantic_foundation": [
        "library.csp.identity.scoped-identifier",
        "library.csp.time.bitemporal-ledger",
        "library.smf.bitemporal_algebra",
        "library.smf.missingness_algebra",
        "library.smf.uncertainty_algebra",
        "library.smf.unit_conversion_algebra",
    ],
    "connectivity_pipeline": [
        "library.pipeline.identity_types",
        "library.pipeline.connector_spi",
        "library.pipeline.change_envelope",
        "library.pipeline.data_cut_algebra",
        "library.pipeline.graph_algebra",
        "library.pipeline.graph_validator",
        "library.pipeline.port_typechecker",
        "library.pipeline.logical_planner",
        "library.pipeline.orchestration_kernel",
        "library.pipeline.checkpoint_coordinator",
        "library.pipeline.delivery_proof",
        "library.pipeline.lineage_receipts",
    ],
    "persistence_query": [
        "library.persistence.storage_identity",
        "library.persistence.object_contract",
        "library.persistence.logical_types",
        "library.persistence.table_identity",
        "library.persistence.schema_evolution",
        "library.persistence.partition_algebra",
        "library.persistence.snapshot_graph",
        "library.persistence.commit_precondition",
        "library.persistence.commit_protocol",
        "library.persistence.scan_planner",
        "library.persistence.conformance_oracles",
        "library.qck.query-types",
        "library.qck.logical-plan-ir",
        "library.qck.query-binding",
        "library.qck.relational-semantics",
        "library.qck.relational-kernels",
        "library.qck.query-receipts",
    ],
    "governance_quality_evidence": [
        "library.san_wire_schema",
        "library.schema_registry.subject_identity",
        "library.schema_registry.version_registry",
        "library.schema_registry.compatibility",
        "library.schema_registry.reference_closure",
        "library.gmo.vertical_profiles",
        "library.qor.schema_conformance_kernel",
        "library.qor.completeness_timeliness_kernel",
        "library.qor.validation_execution_kernel",
        "library.qor.fitness_for_use_kernel",
        "library.qor.evidence_receipt_kernel",
        "library.lpe.lineage-core",
        "library.lpe.runtime-receipt-core",
        "library.lpe.evidence-bundle",
    ],
    "semantic_consumption": [
        "library.smf.semantic_registry",
        "library.smf.semantic_type_checker",
        "library.smf.formula_parser",
        "library.smf.formula_runtime",
        "library.smf.observation_ledger",
        "library.smf.aggregation_algebra",
        "library.cbv.result_contracts",
        "library.cbv.uncertainty_contracts",
        "library.cbv.analytical_case_reducer",
        "library.cbv.decision_handoff_algebra",
        "library.cbv.policy_projection",
    ],
}


ACCEPTANCE_GATE_TEMPLATES = [
    {
        "gate_kind": "source_and_cut_fitness",
        "question": "Are the exact source occurrences, identities, time cuts, corrections, lineage and fitness-for-use evidence accepted for this case?",
        "required_evidence": ["source occurrence receipts", "identity/time/unit reconciliation", "quality and lineage receipts", "declared exclusions and unresolved gaps"],
        "refusal": "refuse when source authority, cut identity, correction semantics or fitness is unknown",
    },
    {
        "gate_kind": "semantic_and_policy_fitness",
        "question": "Do the compiled meanings, populations, grains, invariants, policies and precedence rules match the vertical authority's contract?",
        "required_evidence": ["semantic conformance receipt", "invariant oracle results", "policy/precedence edition", "loss and exception approvals"],
        "refusal": "refuse semantic drift, silent loss or unowned policy defaults",
    },
    {
        "gate_kind": "method_and_model_validity",
        "question": "Are every selected analytical method, model class, assumption, uncertainty posture and failure slice valid for the declared population and use?",
        "required_evidence": ["method applicability adjudication", "model-class proof", "validation and adversarial results", "uncertainty and limitation disclosure"],
        "refusal": "refuse unproved applicability, model-class collapse or material untested failure slices",
    },
    {
        "gate_kind": "physical_conformance",
        "question": "Do exact artifacts, adapters, target occurrences and compatibility cells satisfy the complete compiled capability contract?",
        "required_evidence": ["qualified exact offers", "target occurrence and configuration", "independent conformance appraisal", "dependency and compatibility closure"],
        "refusal": "refuse documentation-only, internal-test-only, stale, mismatched or rejected physical evidence",
    },
    {
        "gate_kind": "operational_envelope",
        "question": "Are finite latency, throughput, capacity, cost, recovery, cancellation, overload and degraded-mode envelopes accepted?",
        "required_evidence": ["workload/SLO results", "finite resource and cost proof", "failure injection and recovery", "runbook and support ownership"],
        "refusal": "refuse unbounded budgets, absent recovery evidence or undeclared degradation",
    },
    {
        "gate_kind": "authority_safety_and_effect",
        "question": "Does the owning vertical authority approve the proposal-to-decision-to-effect boundary, safety posture and separation of duties?",
        "required_evidence": ["named authority and delegation", "maker-checker or review record", "effect prohibition/permission", "revocation and emergency-stop behavior"],
        "refusal": "refuse self-authorization, proposal-to-effect collapse or missing accountable authority",
    },
    {
        "gate_kind": "outcome_monitoring_and_reconciliation",
        "question": "Can accepted decisions and later outcomes be observed, reconciled, challenged and used to invalidate the solution?",
        "required_evidence": ["decision and effect receipts", "outcome observation contract", "monitoring and drift thresholds", "appeal/correction/reconciliation path"],
        "refusal": "refuse when later outcomes, harms, drift or corrections cannot be attributed and reconciled",
    },
    {
        "gate_kind": "change_rollback_and_exit",
        "question": "Are version change, in-flight work, rollback/roll-forward, historical replay, decommission and supplier exit governed?",
        "required_evidence": ["semantic diff and blast radius", "migration/parallel-run evidence", "rollback or roll-forward plan", "state/data/evidence portability and deletion disposition"],
        "refusal": "refuse irreversible cutover or supplier lock-in without authorized disposition",
    },
]


CASE_SPECS = [
    {
        "composition_id": "composition.vertical.health_acute_bed_flow",
        "case_file": "domain_atlas/industries/health_life_sciences/analytics-cases.jsonl",
        "source_file": "domain_atlas/industries/health_life_sciences/source-systems.jsonl",
        "shape_file": "domain_atlas/industries/health_life_sciences/data-shapes.jsonl",
        "evidence_file": "domain_atlas/industries/health_life_sciences/sources.jsonl",
        "vertical_case_ref": "health.case.acute.bed_flow",
        "product_refs": [
            "candidate.product.source_connectivity_control",
            "candidate.product.ingestion_delivery",
            "candidate.product.pipeline_orchestration",
            "candidate.product.dataflow_execution",
            "candidate.product.lakehouse_experience",
            "candidate.product.lineage_provenance",
            "candidate.product.data_quality_operations",
            "candidate.product.semantic_metric",
            "candidate.product.process_mining_workbench",
            "candidate.product.forecasting_workbench",
            "candidate.product.simulation_environment",
            "candidate.product.optimization_solver",
            "candidate.product.bi_reporting",
        ],
        "specific_layers": {
            "process_projection_analysis": [
                "library.method_kernels.process_event_projection",
                "library.method_kernels.process_case_projection",
                "library.method_kernels.process_performance_methods",
            ],
            "forecasting": [
                "library.method_kernels.time_series_semantics",
                "library.method_kernels.forecast_estimators",
                "library.method_kernels.forecast_evaluation",
                "library.method_kernels.forecast_reconciliation",
                "library.method_kernels.result_algebra",
            ],
            "queueing": [
                "library.operations_research.queue_model_semantics",
                "library.operations_research.queue_performance_methods",
                "library.operations_research.queue_network_methods",
                "library.operations_research.queue_inference_calibration",
                "library.operations_research.queue_model_validation",
            ],
            "simulation": [
                "library.operations_research.simulation_model_semantics",
                "library.operations_research.simulation_experiment_design",
                "library.operations_research.simulation_random_stream_control",
                "library.operations_research.simulation_execution",
                "library.operations_research.simulation_output_analysis",
                "library.operations_research.simulation_verification_validation",
            ],
            "optimization": [
                "library.operations_research.decision_problem_semantics",
                "library.operations_research.objective_preference_algebra",
                "library.operations_research.constraint_policy_algebra",
                "library.operations_research.optimization_model_ir",
                "library.operations_research.solver_capability_contract",
                "library.operations_research.optimization_solve_execution",
                "library.operations_research.optimization_result_algebra",
                "library.operations_research.optimization_solution_validation",
                "library.operations_research.infeasibility_diagnosis",
            ],
        },
        "conditional_libraries": [],
        "method_bindings": {
            "method.queue_and_flow_decomposition": [
                "library.operations_research.queue_model_semantics",
                "library.operations_research.queue_performance_methods",
                "library.method_kernels.process_performance_methods",
            ],
            "method.queueing_theory": [
                "library.operations_research.queue_model_semantics",
                "library.operations_research.queue_performance_methods",
                "library.operations_research.queue_network_methods",
                "library.operations_research.queue_model_validation",
            ],
            "method.probabilistic_forecasting": [
                "library.method_kernels.time_series_semantics",
                "library.method_kernels.forecast_estimators",
                "library.method_kernels.forecast_evaluation",
                "library.method_kernels.forecast_reconciliation",
            ],
            "method.discrete_event_or_microsimulation": [
                "library.operations_research.simulation_model_semantics",
                "library.operations_research.simulation_experiment_design",
                "library.operations_research.simulation_random_stream_control",
                "library.operations_research.simulation_execution",
                "library.operations_research.simulation_output_analysis",
                "library.operations_research.simulation_verification_validation",
            ],
            "method.constrained_optimization": [
                "library.operations_research.decision_problem_semantics",
                "library.operations_research.objective_preference_algebra",
                "library.operations_research.constraint_policy_algebra",
                "library.operations_research.optimization_model_ir",
                "library.operations_research.solver_capability_contract",
                "library.operations_research.optimization_solve_execution",
                "library.operations_research.optimization_result_algebra",
                "library.operations_research.optimization_solution_validation",
            ],
        },
    },
    {
        "composition_id": "composition.vertical.commerce_tender_cash_reconciliation",
        "case_file": "domain_atlas/industries/commerce_services/analytics-cases.jsonl",
        "source_file": "domain_atlas/industries/commerce_services/source-systems.jsonl",
        "shape_file": "domain_atlas/industries/commerce_services/data-shapes.jsonl",
        "evidence_file": "domain_atlas/industries/commerce_services/sources.jsonl",
        "vertical_case_ref": "commerce.case.retail_tender_cash_reconciliation",
        "product_refs": [
            "candidate.product.source_connectivity_control",
            "candidate.product.ingestion_delivery",
            "candidate.product.pipeline_orchestration",
            "candidate.product.dataflow_execution",
            "candidate.product.lakehouse_experience",
            "candidate.product.lineage_provenance",
            "candidate.product.data_quality_operations",
            "candidate.product.reconciliation_control_operations",
            "candidate.product.semantic_metric",
            "candidate.product.process_mining_workbench",
            "candidate.product.bi_reporting",
        ],
        "specific_layers": {
            "reconciliation": [
                "library.qor.reconciliation_definition_kernel",
                "library.qor.reconciliation_execution_kernel",
                "library.qor.reconciliation_break_kernel",
                "library.qor.accounting_control_reconciliation_kernel",
                "library.qor.reference_master_alignment_kernel",
            ],
            "process_diagnostics": [
                "library.method_kernels.process_event_projection",
                "library.method_kernels.process_case_projection",
                "library.method_kernels.process_conformance_methods",
                "library.method_kernels.process_performance_methods",
            ],
            "anomaly_change": [
                "library.method_kernels.anomaly_baseline",
                "library.method_kernels.anomaly_detectors",
                "library.method_kernels.change_point_detectors",
                "library.method_kernels.analytical_finding_contract",
            ],
            "causal_diagnostic": [
                "library.method_kernels.causal_graph_identification",
                "library.method_kernels.causal_effect_estimators",
                "library.method_kernels.causal_refutation_sensitivity",
                "library.method_kernels.descriptive_statistics",
                "library.method_kernels.result_algebra",
            ],
            "deterministic_document_evidence": [
                "library.method_kernels.document_container_semantics",
                "library.method_kernels.document_content_graph",
                "library.method_kernels.document_parser_adapters",
                "library.method_kernels.document_layout_methods",
                "library.method_kernels.document_table_extraction",
                "library.method_kernels.document_provenance_loss",
                "library.method_kernels.document_information_extraction",
                "library.method_kernels.document_extraction_evaluation",
            ],
        },
        "conditional_libraries": [
            {
                "library_ref": "library.method_kernels.document_ocr_methods",
                "activation_predicate": "An admitted evidence document has no trustworthy text layer and the declared OCR language/script profile resolves.",
            },
            {
                "library_ref": "library.method_kernels.document_form_extraction",
                "activation_predicate": "The admitted document profile contains native or rendered form fields required by the reconciliation schema.",
            },
        ],
        "method_bindings": {
            "analytics.method.stratified_drilldown_and_decomposition": [
                "library.method_kernels.descriptive_statistics",
                "library.method_kernels.result_algebra",
            ],
            "analytics.method.causal_graph_and_root_cause_analysis": [
                "library.method_kernels.causal_graph_identification",
                "library.method_kernels.causal_effect_estimators",
                "library.method_kernels.causal_refutation_sensitivity",
            ],
            "analytics.method.change_point_and_anomaly_detection": [
                "library.method_kernels.anomaly_baseline",
                "library.method_kernels.anomaly_detectors",
                "library.method_kernels.change_point_detectors",
                "library.method_kernels.analytical_finding_contract",
            ],
            "analytics.method.process_mining_and_conformance": [
                "library.method_kernels.process_event_projection",
                "library.method_kernels.process_case_projection",
                "library.method_kernels.process_conformance_methods",
                "library.method_kernels.process_performance_methods",
            ],
        },
    },
    {
        "composition_id": "composition.vertical.energy_pipeline_nomination_capacity",
        "case_file": "domain_atlas/industries/energy_resources/analytics-cases.jsonl",
        "source_file": "domain_atlas/industries/energy_resources/source-systems.jsonl",
        "shape_file": "domain_atlas/industries/energy_resources/data-shapes.jsonl",
        "evidence_file": "domain_atlas/industries/energy_resources/sources.jsonl",
        "vertical_case_ref": "energy.case.nomination_capacity_optimization",
        "product_refs": [
            "candidate.product.source_connectivity_control",
            "candidate.product.ingestion_delivery",
            "candidate.product.pipeline_orchestration",
            "candidate.product.dataflow_execution",
            "candidate.product.lakehouse_experience",
            "candidate.product.lineage_provenance",
            "candidate.product.data_quality_operations",
            "candidate.product.semantic_metric",
            "candidate.product.simulation_environment",
            "candidate.product.optimization_solver",
            "candidate.product.bi_reporting",
        ],
        "specific_layers": {
            "scenario_analysis": [
                "library.operations_research.simulation_model_semantics",
                "library.operations_research.simulation_experiment_design",
                "library.operations_research.simulation_execution",
                "library.operations_research.simulation_output_analysis",
                "library.operations_research.simulation_verification_validation",
            ],
            "optimization": [
                "library.operations_research.decision_problem_semantics",
                "library.operations_research.objective_preference_algebra",
                "library.operations_research.constraint_policy_algebra",
                "library.operations_research.optimization_model_ir",
                "library.operations_research.solver_capability_contract",
                "library.operations_research.optimization_solve_execution",
                "library.operations_research.optimization_result_algebra",
                "library.operations_research.optimization_solution_validation",
                "library.operations_research.infeasibility_diagnosis",
            ],
        },
        "conditional_libraries": [],
        "method_bindings": {
            "network flow optimization": [
                "library.operations_research.decision_problem_semantics",
                "library.operations_research.objective_preference_algebra",
                "library.operations_research.constraint_policy_algebra",
                "library.operations_research.optimization_model_ir",
                "library.operations_research.solver_capability_contract",
                "library.operations_research.optimization_solve_execution",
                "library.operations_research.optimization_result_algebra",
                "library.operations_research.optimization_solution_validation",
                "library.operations_research.infeasibility_diagnosis",
            ],
            "scenario scheduling": [
                "library.operations_research.simulation_model_semantics",
                "library.operations_research.simulation_experiment_design",
                "library.operations_research.simulation_execution",
                "library.operations_research.simulation_output_analysis",
                "library.operations_research.simulation_verification_validation",
                "library.operations_research.optimization_model_ir",
                "library.operations_research.optimization_solve_execution",
            ],
            "contract priority rules": [
                "library.operations_research.decision_problem_semantics",
                "library.operations_research.objective_preference_algebra",
                "library.operations_research.constraint_policy_algebra",
            ],
        },
        "physical_binding_requirement_refs": ["requirement.bind.lp_precise_terminal"],
        "physical_binding_candidate_offer_refs": ["offer.bind.ptr.highspy.highs.1_15_1"],
        "physical_binding_refused_offer_refs": ["offer.bind.ptr.ortools.glop_mpsolver_python.9_15_6755"],
        "binder_evaluation_refs": [
            "evaluation.bind.lp_precise.highspy_highs.1_15_1",
            "evaluation.bind.lp_precise.ortools_glop_mpsolver_python.9_15_6755",
        ],
        "binder_vertical_trace_ref": "example.bind.pipeline_nomination.lp_screening.positive",
        "broad_model_class_adjudication_trace_ref": "trace.mca.pipeline.broad_unclosed",
        "broad_model_class_adjudication_result_ref": "result.trace.mca.pipeline.broad_unclosed",
        "screen_model_class_adjudication_trace_ref": "trace.mca.pipeline.lp_screen",
        "screen_model_class_adjudication_result_ref": "result.trace.mca.pipeline.lp_screen",
        "screen_formal_model_class_refs": ["class.mca.continuous_lp"],
        "physical_binding_model_class_status": "screen_classified_continuous_lp_broad_case_refused",
        "physical_binding_verdict": "refused_qualification_and_vertical_acceptance_gaps",
        "additional_gaps": [
            "The broad network-flow, hydraulic, scheduling and contract-priority case is deterministically refused as a continuous LP; only the closed screening cut is classified as continuous LP.",
            "Any screening-boundary change, including reintroducing hydraulic, integer, stochastic or hybrid semantics, invalidates the LP classification and all downstream bindings.",
            "The exact precise-status provider pass lacks independent appraisal, production target qualification and vertical acceptance.",
        ],
    },
    {
        "composition_id": "composition.vertical.manufacturing_finite_capacity_schedule",
        "case_file": "domain_atlas/industries/manufacturing_industrial/analytics-cases.jsonl",
        "source_file": "domain_atlas/industries/manufacturing_industrial/source-systems.jsonl",
        "shape_file": "domain_atlas/industries/manufacturing_industrial/data-shapes.jsonl",
        "evidence_file": "domain_atlas/industries/manufacturing_industrial/sources.jsonl",
        "vertical_case_ref": "mfg.case.finite_schedule",
        "product_refs": [
            "candidate.product.source_connectivity_control",
            "candidate.product.ingestion_delivery",
            "candidate.product.pipeline_orchestration",
            "candidate.product.dataflow_execution",
            "candidate.product.lakehouse_experience",
            "candidate.product.lineage_provenance",
            "candidate.product.data_quality_operations",
            "candidate.product.semantic_metric",
            "candidate.product.optimization_solver",
            "candidate.product.bi_reporting",
        ],
        "specific_layers": {
            "finite_capacity_optimization": [
                "library.operations_research.decision_problem_semantics",
                "library.operations_research.objective_preference_algebra",
                "library.operations_research.constraint_policy_algebra",
                "library.operations_research.optimization_model_ir",
                "library.operations_research.solver_capability_contract",
                "library.operations_research.optimization_solve_execution",
                "library.operations_research.optimization_result_algebra",
                "library.operations_research.optimization_solution_validation",
                "library.operations_research.infeasibility_diagnosis",
            ],
            "heuristic_search": [
                "library.operations_research.heuristic_search_contract",
            ],
        },
        "conditional_libraries": [],
        "method_bindings": {
            "constraint programming": [
                "library.operations_research.decision_problem_semantics",
                "library.operations_research.constraint_policy_algebra",
                "library.operations_research.optimization_model_ir",
                "library.operations_research.solver_capability_contract",
                "library.operations_research.optimization_solve_execution",
                "library.operations_research.optimization_solution_validation",
            ],
            "mixed-integer optimization": [
                "library.operations_research.decision_problem_semantics",
                "library.operations_research.objective_preference_algebra",
                "library.operations_research.constraint_policy_algebra",
                "library.operations_research.optimization_model_ir",
                "library.operations_research.solver_capability_contract",
                "library.operations_research.optimization_solve_execution",
                "library.operations_research.optimization_result_algebra",
                "library.operations_research.optimization_solution_validation",
                "library.operations_research.infeasibility_diagnosis",
            ],
            "large-neighborhood search": [
                "library.operations_research.heuristic_search_contract",
                "library.operations_research.optimization_model_ir",
                "library.operations_research.optimization_solve_execution",
                "library.operations_research.optimization_solution_validation",
            ],
        },
        "physical_binding_requirement_refs": ["requirement.bind.cp_sat_exact_scope"],
        "physical_binding_candidate_offer_refs": ["offer.bind.ptr.ortools.cp_sat_python.9_15_6755"],
        "physical_binding_refused_offer_refs": [],
        "binder_evaluation_refs": ["evaluation.bind.cp_sat_exact.ortools_cp_sat_python.9_15_6755"],
        "binder_vertical_trace_ref": "example.bind.manufacturing_schedule.cp_sat.positive",
        "screen_model_class_adjudication_trace_ref": "trace.mca.manufacturing.cp_sat",
        "screen_model_class_adjudication_result_ref": "result.trace.mca.manufacturing.cp_sat",
        "screen_formal_model_class_refs": ["class.mca.cp_sat_integer", "class.mca.finite_domain_cp"],
        "physical_binding_model_class_status": "classified_cp_sat_fragment_enterprise_formulation_unaccepted",
        "physical_binding_verdict": "refused_qualification_and_vertical_acceptance_gaps",
        "additional_gaps": [
            "The classification admits a closed bounded-integer CP-SAT facet; it does not prove that every enterprise scheduling rule is represented by the exact tested fragment.",
            "The exact provider profiles are internal executed evidence without independent appraisal, production resource qualification or portability proof.",
            "No plant authority has accepted the input cut, formulation, objective precedence, schedule publication or dispatch effect.",
        ],
    },
]


SUBSTITUTION_SPECS = [
    {
        "trial_id": "substitution.health.optimization.ortools_to_highs",
        "composition_ref": "composition.vertical.health_acute_bed_flow",
        "incumbent_offer_ref": "offer.operations_research.ortools",
        "substitute_offer_ref": "offer.operations_research.highs",
        "required_contract_refs": [
            "contract.operations_research.solver_capability_contract",
            "contract.operations_research.optimization_solve_execution",
            "contract.operations_research.optimization_result_algebra",
        ],
    },
    {
        "trial_id": "substitution.health.optimization.ortools_glop_to_highspy.safe_lp_exact_scope",
        "composition_ref": "composition.vertical.health_acute_bed_flow",
        "incumbent_offer_ref": "offer.operations_research.ortools.glop.mpsolver_python.9_15_6755",
        "substitute_offer_ref": "offer.operations_research.highspy.highs.1_15_1",
        "required_contract_refs": [
            "contract.operations_research.lp.safe_status_and_objective.v1",
        ],
    },
    {
        "trial_id": "substitution.health.optimization.ortools_glop_to_highspy.precise_terminal_exact_scope",
        "composition_ref": "composition.vertical.health_acute_bed_flow",
        "incumbent_offer_ref": "offer.operations_research.ortools.glop.mpsolver_python.9_15_6755",
        "substitute_offer_ref": "offer.operations_research.highspy.highs.1_15_1",
        "required_contract_refs": [
            "contract.operations_research.lp.precise_terminal_classification.v1",
        ],
    },
    {
        "trial_id": "substitution.energy.pipeline_nomination.ortools_glop_to_highspy.precise_terminal_exact_scope",
        "composition_ref": "composition.vertical.energy_pipeline_nomination_capacity",
        "incumbent_offer_ref": "offer.operations_research.ortools.glop.mpsolver_python.9_15_6755",
        "substitute_offer_ref": "offer.operations_research.highspy.highs.1_15_1",
        "required_contract_refs": [
            "contract.operations_research.lp.precise_terminal_classification.v1",
        ],
    },
    {
        "trial_id": "substitution.health.simulation.anylogic_to_simio",
        "composition_ref": "composition.vertical.health_acute_bed_flow",
        "incumbent_offer_ref": "offer.operations_research.anylogic",
        "substitute_offer_ref": "offer.operations_research.simio",
        "required_contract_refs": [
            "contract.operations_research.simulation_model_semantics",
            "contract.operations_research.simulation_experiment_design",
            "contract.operations_research.simulation_execution",
            "contract.operations_research.simulation_output_analysis",
        ],
    },
    {
        "trial_id": "substitution.health.forecast.sktime_to_statsforecast",
        "composition_ref": "composition.vertical.health_acute_bed_flow",
        "incumbent_offer_ref": "offer.method_kernels.sktime",
        "substitute_offer_ref": "offer.method_kernels.statsforecast",
        "required_contract_refs": [
            "contract.method_kernel.time_series_semantics",
            "contract.method_kernel.forecast_estimators",
            "contract.method_kernel.forecast_evaluation",
            "contract.method_kernel.forecast_reconciliation",
        ],
    },
    {
        "trial_id": "substitution.commerce.process.pm4py_to_prom",
        "composition_ref": "composition.vertical.commerce_tender_cash_reconciliation",
        "incumbent_offer_ref": "offer.method_kernels.pm4py",
        "substitute_offer_ref": "offer.method_kernels.prom",
        "required_contract_refs": [
            "contract.method_kernel.process_conformance_methods",
            "contract.method_kernel.process_performance_methods",
        ],
    },
    {
        "trial_id": "substitution.commerce.document.tika_to_pdfbox",
        "composition_ref": "composition.vertical.commerce_tender_cash_reconciliation",
        "incumbent_offer_ref": "offer.method_kernels.tika",
        "substitute_offer_ref": "offer.method_kernels.pdfbox",
        "required_contract_refs": [
            "contract.method_kernel.document_container_semantics",
            "contract.method_kernel.document_content_graph",
            "contract.method_kernel.document_parser_adapters",
            "contract.method_kernel.document_provenance_loss",
        ],
    },
]


def build_outputs() -> dict[Path, str]:
    registry_root = RESEARCH / "domain_atlas/compiler/library_registry"
    libraries = {row["library_id"]: row for row in load_jsonl(registry_root / "library-contributions.jsonl")}
    requirements_by_subject = {
        row["subject_ref"]: row for row in load_jsonl(registry_root / "capability-requirements.jsonl")
    }
    offers_by_subject = {
        row["subject_ref"]: row for row in load_jsonl(registry_root / "capability-offers.jsonl")
    }
    products = {
        row["record_id"]: row
        for row in load_jsonl(RESEARCH / "product_ontology/global_boundary_research/product-archetypes.jsonl")
    }

    compositions = []
    for spec in CASE_SPECS:
        cases = {row["record_id"]: row for row in load_jsonl(RESEARCH / spec["case_file"])}
        source_systems = {row["record_id"]: row for row in load_jsonl(RESEARCH / spec["source_file"])}
        shapes = {row["record_id"]: row for row in load_jsonl(RESEARCH / spec["shape_file"])}
        evidence = {row["record_id"]: row for row in load_jsonl(RESEARCH / spec["evidence_file"])}
        case = cases[spec["vertical_case_ref"]]
        layers = {**COMMON_LAYERS, **spec["specific_layers"]}
        required_library_refs = sorted({ref for refs in layers.values() for ref in refs})
        conditional_library_refs = sorted(row["library_ref"] for row in spec["conditional_libraries"])
        required_requirement_refs = sorted(requirements_by_subject[ref]["requirement_id"] for ref in required_library_refs)
        conditional_requirement_refs = sorted(requirements_by_subject[ref]["requirement_id"] for ref in conditional_library_refs)
        portable_offer_refs = sorted(offers_by_subject[ref]["offer_id"] for ref in required_library_refs)
        compositions.append({
            "record_kind": "vertical_composition_proof_candidate",
            "composition_id": spec["composition_id"],
            "edition": EDITION,
            "as_of": AS_OF,
            "status": "structurally_resolved_physical_binding_refused",
            "vertical_case_ref": case["record_id"],
            "industry_id": case["industry_id"],
            "sovereign_question": case["sovereign_question"],
            "decision_or_action": case["decision_or_action"],
            "actors": case["actors"],
            "unit_of_analysis": case["unit_of_analysis"],
            "grain": case["grain"],
            "case_invariants": case["invariants"],
            "case_failure_modes": case["failure_modes"],
            "case_limitations": case["limitations"],
            "operation_refs": case["operation_refs"],
            "source_system_refs": case["source_system_refs"],
            "data_shape_refs": case["data_shape_refs"],
            "evidence_refs": case["evidence_refs"],
            "resolved_source_systems": sorted(record_label(source_systems[ref]) for ref in case["source_system_refs"]),
            "resolved_data_shapes": sorted(record_label(shapes[ref]) for ref in case["data_shape_refs"]),
            "resolved_evidence_titles": sorted(record_label(evidence[ref]) for ref in case["evidence_refs"]),
            "product_refs": sorted(spec["product_refs"]),
            "layers": [
                {"layer_id": layer_id, "required_library_refs": sorted(refs)}
                for layer_id, refs in sorted(layers.items())
            ],
            "required_library_refs": required_library_refs,
            "conditional_library_bindings": spec["conditional_libraries"],
            "required_requirement_refs": required_requirement_refs,
            "conditional_requirement_refs": conditional_requirement_refs,
            "withheld_portable_offer_refs": portable_offer_refs,
            "method_bindings": [
                {"vertical_method_ref": method_ref, "exact_library_refs": sorted(refs)}
                for method_ref, refs in sorted(spec["method_bindings"].items())
            ],
            "physical_binding_requirement_refs": sorted(spec.get("physical_binding_requirement_refs", [])),
            "physical_binding_candidate_offer_refs": sorted(spec.get("physical_binding_candidate_offer_refs", [])),
            "physical_binding_refused_offer_refs": sorted(spec.get("physical_binding_refused_offer_refs", [])),
            "binder_evaluation_refs": sorted(spec.get("binder_evaluation_refs", [])),
            "binder_vertical_trace_ref": spec.get("binder_vertical_trace_ref"),
            "broad_model_class_adjudication_trace_ref": spec.get("broad_model_class_adjudication_trace_ref"),
            "broad_model_class_adjudication_result_ref": spec.get("broad_model_class_adjudication_result_ref"),
            "screen_model_class_adjudication_trace_ref": spec.get("screen_model_class_adjudication_trace_ref"),
            "screen_model_class_adjudication_result_ref": spec.get("screen_model_class_adjudication_result_ref"),
            "screen_formal_model_class_refs": sorted(spec.get("screen_formal_model_class_refs", [])),
            "physical_binding_model_class_status": spec.get("physical_binding_model_class_status", "not_narrowed_to_exact_provider_model_class"),
            "selected_optional_extension_requirement_refs": [],
            "optional_extension_policy": "forbidden_unless_explicit_intent_adds_a_removable_non_authoritative_stage",
            "deterministic_core_laws": [
                "All industry identities, time, units, constraints, formulas, methods, authority and effects resolve without an LLM or agent.",
                "Generated proposals cannot satisfy parsing, typing, validation, optimization, authorization, execution or receipt requirements.",
                "Removing every optional model/agent extension leaves this composition graph structurally unchanged.",
            ],
            "compile_phase_verdicts": {
                "industry_reference_resolution": "pass",
                "product_boundary_resolution": "pass_candidate",
                "library_and_requirement_resolution": "pass_structural",
                "optional_extension_removal": "pass",
                "physical_provider_binding": spec.get("physical_binding_verdict", "refused_no_qualified_offers"),
                "execution": "not_attempted",
                "vertical_acceptance": "not_executed",
            },
            "qualification_summary": {
                "required_library_count": len(required_library_refs),
                "qualified_binding_count": 0,
                "portable_binding_count": 0,
                "unqualified_requirement_refs": required_requirement_refs,
            },
            "gaps": [
                "Every physical requirement lacks a current qualified deployed implementation receipt.",
                "End-to-end source occurrence, target, SLO, authority and vertical acceptance evidence is not executed.",
                "This structural composition does not prove clinical, financial, operational or product fitness.",
                *spec.get("additional_gaps", []),
            ],
            "resolved_library_names": {ref: libraries[ref]["name"] for ref in required_library_refs},
            "resolved_product_names": {ref: products[ref]["name"] for ref in spec["product_refs"]},
        })

    acceptance_gates = []
    acceptance_contracts = []
    for composition in compositions:
        slug = composition["composition_id"].removeprefix("composition.vertical.")
        gate_refs = []
        for ordinal, template in enumerate(ACCEPTANCE_GATE_TEMPLATES, 1):
            gate_ref = f"acceptance.gate.{slug}.{template['gate_kind']}"
            gate_refs.append(gate_ref)
            if template["gate_kind"] == "source_and_cut_fitness":
                case_obligations = [
                    *composition["source_system_refs"],
                    *composition["data_shape_refs"],
                ]
            elif template["gate_kind"] == "semantic_and_policy_fitness":
                case_obligations = composition["case_invariants"]
            elif template["gate_kind"] == "method_and_model_validity":
                case_obligations = [
                    *[row["vertical_method_ref"] for row in composition["method_bindings"]],
                    *composition["case_failure_modes"],
                ]
            elif template["gate_kind"] == "physical_conformance":
                case_obligations = [
                    *composition["physical_binding_requirement_refs"],
                    *composition["physical_binding_candidate_offer_refs"],
                    *composition["physical_binding_refused_offer_refs"],
                ]
            elif template["gate_kind"] == "authority_safety_and_effect":
                case_obligations = [composition["decision_or_action"], *composition["actors"]]
            elif template["gate_kind"] == "outcome_monitoring_and_reconciliation":
                case_obligations = composition["operation_refs"]
            elif template["gate_kind"] == "change_rollback_and_exit":
                case_obligations = composition["case_limitations"]
            else:
                case_obligations = composition["gaps"]
            acceptance_gates.append({
                "record_kind": "vertical_acceptance_gate",
                "acceptance_gate_id": gate_ref,
                "edition": EDITION,
                "status": "candidate_unexecuted",
                "ordinal": ordinal,
                "composition_ref": composition["composition_id"],
                "vertical_case_ref": composition["vertical_case_ref"],
                "gate_kind": template["gate_kind"],
                "blocking": True,
                "question": template["question"],
                "required_evidence": template["required_evidence"],
                "case_specific_obligations": case_obligations,
                "evidence_source_refs": composition["evidence_refs"],
                "execution_status": "not_executed",
                "receipt_refs": [],
                "refusal_law": template["refusal"],
            })
        acceptance_contracts.append({
            "record_kind": "vertical_acceptance_contract",
            "acceptance_contract_id": f"acceptance.contract.{slug}",
            "edition": EDITION,
            "status": "candidate_blocked_unexecuted",
            "composition_ref": composition["composition_id"],
            "vertical_case_ref": composition["vertical_case_ref"],
            "acceptance_subject": "exact compiled solution graph plus exact physical binding plan and observed operational occurrence",
            "authority_roles": composition["actors"],
            "proposal_or_action_boundary": composition["decision_or_action"],
            "required_gate_refs": gate_refs,
            "minimum_acceptance_law": "Every blocking gate passes under its named authority on the same immutable composition, physical occurrence and evidence cut.",
            "binding_prerequisite_verdict": composition["compile_phase_verdicts"]["physical_provider_binding"],
            "current_verdict": "not_executed_blocked",
            "receipt_refs": [],
            "prohibited_shortcuts": [
                "structural composition as vertical acceptance",
                "provider test or qualification as vertical acceptance",
                "model or agent proposal as authority",
                "metric improvement without harm, policy and population review",
                "historical benchmark as production occurrence evidence",
            ],
        })

    provider_offer_rows = (
        load_jsonl(RESEARCH / "domain_atlas/universes/method_kernels/compiler-requirements-offers.jsonl")
        + load_jsonl(RESEARCH / "domain_atlas/universes/operations_research/compiler-requirements-offers.jsonl")
    )
    provider_offers = {
        row["offer_id"]: row for row in provider_offer_rows if row.get("record_kind") == "capability_offer"
    }
    substitutions = []
    for spec in SUBSTITUTION_SPECS:
        incumbent = provider_offers[spec["incumbent_offer_ref"]]
        substitute = provider_offers[spec["substitute_offer_ref"]]
        required = set(spec["required_contract_refs"])
        incumbent_missing = sorted(required - set(incumbent["contract_refs"]))
        substitute_missing = sorted(required - set(substitute["contract_refs"]))
        identity_failures = []
        if incumbent.get("offer_kind") == "provider_project_facade":
            identity_failures.append("incumbent_is_provider_project_facade")
        if substitute.get("offer_kind") == "provider_project_facade":
            identity_failures.append("substitute_is_provider_project_facade")
        if identity_failures:
            verdict = "refused_offer_identity_too_broad"
        elif incumbent_missing or substitute_missing:
            verdict = "refused_capability_mismatch"
        elif not incumbent["conformance_receipts"] or not substitute["conformance_receipts"]:
            verdict = "refused_unqualified_evidence"
        else:
            verdict = "eligible_for_scoped_differential_test_not_portability"
        substitutions.append({
            "record_kind": "provider_substitution_trial",
            "edition": EDITION,
            **spec,
            "incumbent_missing_contract_refs": incumbent_missing,
            "substitute_missing_contract_refs": substitute_missing,
            "incumbent_offer_kind": incumbent.get("offer_kind", "legacy_unadjudicated_offer"),
            "substitute_offer_kind": substitute.get("offer_kind", "legacy_unadjudicated_offer"),
            "offer_identity_failures": identity_failures,
            "incumbent_conformance_receipt_refs": incumbent["conformance_receipts"],
            "substitute_conformance_receipt_refs": substitute["conformance_receipts"],
            "incumbent_executed_test_receipt_refs": incumbent.get("executed_test_receipt_refs", []),
            "substitute_executed_test_receipt_refs": substitute.get("executed_test_receipt_refs", []),
            "verdict": verdict,
            "portability_claim": False,
            "executed_test_evidence_is_qualification": False,
            "law": "Name or common API shape never proves substitutability; exact contracts and current scoped evidence decide.",
        })

    removal_trials = [
        {
            "record_kind": "optional_extension_removal_trial",
            "trial_id": f"removal.{row['composition_id'].removeprefix('composition.vertical.')}.all_model_agent_extensions",
            "edition": EDITION,
            "composition_ref": row["composition_id"],
            "removed_library_prefix": "library.mae.",
            "selected_matching_library_refs": [ref for ref in row["required_library_refs"] if ref.startswith("library.mae.")],
            "selected_matching_requirement_refs": row["selected_optional_extension_requirement_refs"],
            "verdict": "pass_graph_unchanged",
            "proof_law": "The vertical compiles to the same deterministic requirements after the optional extension family is removed.",
        }
        for row in compositions
    ]
    removal_trials.append({
        "record_kind": "optional_extension_removal_trial",
        "trial_id": "removal.ambient_agent_injection.negative_twin",
        "edition": EDITION,
        "composition_ref": "composition.vertical.health_acute_bed_flow",
        "removed_library_prefix": "library.mae.",
        "selected_matching_library_refs": ["library.mae.effect_intent_bridge"],
        "selected_matching_requirement_refs": [],
        "verdict": "refused_ambient_extension_without_intent",
        "proof_law": "A model/agent library cannot enter a composition merely because a provider is available.",
    })

    library_sets = {
        row["composition_id"]: set(row["required_library_refs"])
        for row in compositions
    }
    product_sets = {
        row["composition_id"]: set(row["product_refs"])
        for row in compositions
    }
    shared_libraries = set.intersection(*library_sets.values())
    shared_products = set.intersection(*product_sets.values())
    reuse = {
        "record_kind": "cross_vertical_reuse_proof_candidate",
        "proof_id": "reuse.deterministic_verticals.health_commerce_energy_manufacturing",
        "edition": EDITION,
        "status": "structural_reuse_demonstrated_not_qualified",
        "composition_refs": [row["composition_id"] for row in compositions],
        "industry_ids": [row["industry_id"] for row in compositions],
        "units_of_analysis": [row["unit_of_analysis"] for row in compositions],
        "shared_library_refs": sorted(shared_libraries),
        "non_shared_library_refs_by_composition": {
            composition_id: sorted(libraries - shared_libraries)
            for composition_id, libraries in sorted(library_sets.items())
        },
        "pairwise_shared_library_refs": {
            f"{left_id}__{right_id}": sorted(library_sets[left_id] & library_sets[right_id])
            for index, left_id in enumerate(sorted(library_sets))
            for right_id in sorted(library_sets)[index + 1:]
        },
        "shared_product_refs": sorted(shared_products),
        "laws": [
            "Shared horizontal libraries preserve one meaning; vertical vocabulary and configuration remain data, not source-code name branches.",
            "Different industry cases may select different products, libraries, methods and authority policies without changing shared contracts.",
            "Structural reuse does not qualify a provider or prove either vertical outcome.",
        ],
        "qualification_verdict": "not_executed",
    }

    metamodel = {
        "metamodel_id": "metamodel.deterministic_vertical_composition.v1",
        "edition": EDITION,
        "status": "candidate",
        "record_kinds": [
            "vertical_composition_proof_candidate",
            "provider_substitution_trial",
            "optional_extension_removal_trial",
            "cross_vertical_reuse_proof_candidate",
            "vertical_acceptance_contract",
            "vertical_acceptance_gate",
        ],
        "phase_order": [
            "industry_reference_resolution",
            "product_boundary_resolution",
            "library_and_requirement_resolution",
            "optional_extension_removal",
            "physical_provider_binding",
            "execution",
            "vertical_acceptance",
        ],
        "non_collapse_laws": [
            "industry case != product != capability != library != provider offer != deployed occurrence",
            "structural mapping != provider qualification != vertical acceptance",
            "provider substitution != API similarity",
            "model or agent proposal != deterministic result or effect receipt",
            "broad optimization label != exact solver model class",
            "formal model-class match != provider qualification != vertical acceptance != effect authority",
            "generative or agent proposal != formal model-class proof",
            "executed provider test != independent appraisal != vertical acceptance",
        ],
    }

    payloads = {
        HERE / "vertical-compositions.jsonl": jsonl_text(compositions, "composition_id"),
        HERE / "substitution-trials.jsonl": jsonl_text(substitutions, "trial_id"),
        HERE / "optional-extension-removal-trials.jsonl": jsonl_text(removal_trials, "trial_id"),
        HERE / "vertical-acceptance-contracts.jsonl": jsonl_text(acceptance_contracts, "acceptance_contract_id"),
        HERE / "vertical-acceptance-gates.jsonl": jsonl_text(acceptance_gates, "acceptance_gate_id"),
        HERE / "cross-vertical-reuse.json": json.dumps(reuse, indent=2, sort_keys=True) + "\n",
        HERE / "metamodel.json": json.dumps(metamodel, indent=2, sort_keys=True) + "\n",
    }
    manifest = {
        "manifest_id": "manifest.deterministic_vertical_composition.v1",
        "edition": EDITION,
        "as_of": AS_OF,
        "status": "candidate_not_qualified",
        "completion_claim": False,
        "counts": {
            "vertical_compositions": len(compositions),
            "provider_substitution_trials": len(substitutions),
            "optional_extension_removal_trials": len(removal_trials),
            "vertical_acceptance_contracts": len(acceptance_contracts),
            "vertical_acceptance_gates": len(acceptance_gates),
            "shared_libraries": len(reuse["shared_library_refs"]),
        },
        "file_sha256": {
            path.name: hashlib.sha256(content.encode()).hexdigest()
            for path, content in sorted(payloads.items(), key=lambda item: item[0].name)
        },
    }
    payloads[HERE / "manifest.json"] = json.dumps(manifest, indent=2, sort_keys=True) + "\n"
    return payloads


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    outputs = build_outputs()
    stale = []
    for path, content in outputs.items():
        if args.check:
            if not path.exists() or path.read_text(encoding="utf-8") != content:
                stale.append(str(path))
        else:
            path.write_text(content, encoding="utf-8")
    if stale:
        print("STALE " + ", ".join(stale))
        return 1
    print("PASS deterministic vertical composition build: " + ", ".join(path.name for path in outputs))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
