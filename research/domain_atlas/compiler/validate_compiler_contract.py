#!/usr/bin/env python3
"""Structural validation for the corpus/compiler closure metamodel."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent


def load(name: str) -> dict:
    with (ROOT / name).open(encoding="utf-8") as handle:
        return json.load(handle)


def main() -> int:
    errors: list[str] = []
    metamodel = load("compiler-metamodel.json")
    proofs = load("proof-obligations.json")
    for schema in ("requirement-offer-binding.schema.json", "decision-point.schema.json", "library-contribution.schema.json"):
        load(schema)

    node_kinds = metamodel.get("closed_node_kinds", [])
    if len(node_kinds) != len(set(node_kinds)):
        errors.append("duplicate closed node kinds")
    required_nodes = {
        "analytical_practice", "study_definition", "study_plan", "estimand", "formula_definition",
        "analytical_model", "estimator", "analytical_method", "algorithm", "kernel_contract",
        "qualification_profile", "fitted_artifact", "analytical_result", "evaluation_result",
        "analytical_execution_environment", "product_boundary_decision", "automation_modality_requirement",
        "representation_contract", "protocol_contract",
        "capability_requirement", "capability_offer", "provider_capability_class",
        "provider_occurrence", "capability_binding", "compiler_gap",
        "canonical_reference_assertion", "library_contribution", "runtime_receipt", "evidence",
        "runtime_mechanism", "resource_class", "resource_demand", "resource_offer",
        "quota", "budget", "reservation", "allocation", "lease",
        "deployment_occurrence", "usage_receipt",
        "implementation_artifact", "product", "managed_experience", "suite",
        "data_contract", "quality_requirement", "quality_observation", "fitness_verdict",
        "detection_signal", "adjudication_decision", "gate_disposition", "correction_intent",
        "reconciliation_contract", "reconciliation_break", "certificate",
        "governed_asset", "metadata_assertion", "catalog_listing", "semantic_concept",
        "taxonomy_assertion", "ontology_axiom", "technical_schema", "semantic_model",
        "metric_definition", "identity_assertion", "match_candidate", "identity_decision",
        "master_record", "golden_projection", "reference_dataset", "code_set",
        "role_assignment", "governance_issue", "policy_decision", "enforcement_receipt",
        "monitored_subject", "monitoring_source_occurrence", "collection_attempt", "observation_window",
        "change_signal", "verified_change_event", "dependency_artifact", "vulnerability_claim",
        "rollout_occurrence", "behavior_default", "migration_obligation", "invalidation_trigger",
        "watchlist_entry", "requalification_request", "effect_contract", "execution_attempt",
        "event_fact", "object_attribute_history", "state_definition", "state_derivation_rule",
        "derived_state", "state_transition", "generated_state_change_event", "event_label_projection",
        "representation_transform", "temporal_entity_snapshot", "case_definition", "case_projection",
        "optional_model_capability", "model_artifact", "prompt_artifact", "context_bundle",
        "tool_contract", "model_invocation", "model_output_claim", "agent_plan",
        "tool_invocation_intent", "human_review_decision",
        "person_identity", "organization_identity", "research_work", "research_work_edition",
        "contribution_claim", "contributor_role", "formal_concept", "theorem_claim",
        "experiment_contract", "benchmark_contract", "dataset_artifact", "replication_result",
        "limitation_claim", "attribution_assertion",
        "prediction_target", "feature_definition", "label_definition", "information_cutoff",
        "dataset_split_contract", "training_objective", "loss_function", "regularization_contract",
        "hyperparameter_space", "tuning_result", "calibration_contract", "calibrated_predictor",
        "prediction_result", "decision_rule", "model_drift_signal", "retraining_policy",
        "model_monitoring_receipt",
    }
    if not required_nodes.issubset(node_kinds):
        errors.append(f"missing compiler node kinds: {sorted(required_nodes - set(node_kinds))}")

    stages = metamodel.get("ir_stages", [])
    ordinals = [stage.get("ordinal") for stage in stages]
    stage_ids = [stage.get("stage_id") for stage in stages]
    if ordinals != list(range(len(stages))):
        errors.append("IR stage ordinals are not contiguous from zero")
    if len(stage_ids) != len(set(stage_ids)):
        errors.append("duplicate IR stage ids")
    for stage in stages:
        if not stage.get("owns") or not stage.get("exit_gates"):
            errors.append(f"IR stage lacks ownership or gates: {stage.get('stage_id')}")

    edge_ids = [edge.get("edge_kind") for edge in metamodel.get("edge_kinds", [])]
    if len(edge_ids) != len(set(edge_ids)):
        errors.append("duplicate edge kinds")
    for edge in metamodel.get("edge_kinds", []):
        if len(edge.get("roles", [])) < 2:
            errors.append(f"edge lacks typed roles: {edge.get('edge_kind')}")

    proof_ids: set[str] = set()
    for proof in proofs.get("proofs", []):
        proof_id = proof.get("proof_id")
        if proof_id in proof_ids:
            errors.append(f"duplicate proof id: {proof_id}")
        proof_ids.add(proof_id)
        if proof.get("stage") not in stage_ids:
            errors.append(f"proof references unknown stage: {proof_id}")
        if not proof.get("claim") or not proof.get("failure_kind"):
            errors.append(f"incomplete proof: {proof_id}")
    if len(proof_ids) < 40:
        errors.append("proof catalog contains fewer than 40 obligations")
    required_proofs = {
        "proof.method.layer_separation", "proof.vertical.product_method_binding",
        "proof.automation.modality_posture", "proof.extension.model_agent_isolation",
    }
    if not required_proofs.issubset(proof_ids):
        errors.append(f"missing analytical/automation proofs: {sorted(required_proofs - proof_ids)}")

    if metamodel.get("completion_claim") is not False or proofs.get("completion_claim") is not False:
        errors.append("research metamodel or proof catalog claims completion")
    for law in (
        "unknown meaning is a typed gap and is never guessed",
        "requirements and offers bind only through exact contracts and evidence",
        "business question, analytical practice, formal method, algorithm, kernel, library, execution environment and product remain separate identities",
        "semantic operation, analytical method, algorithm, kernel, provider offer and target remain separate identities",
        "analytical practice, study design, estimand, formula, model, estimator, method, algorithm, kernel, fitted artifact, result and evidence remain separate identities",
        "semantic type, carrier, encoding, framing, layout, container, codec and protection envelope remain separate identities",
        "resource class, demand, offer, quota, budget, reservation, allocation, lease, occurrence and observed usage remain separate identities",
        "format contract, protocol contract, implementation artifact, deployment occurrence, product, managed experience and suite remain separate identities",
        "quality requirement, observation, detection, adjudication, disposition, correction and certification remain separate identities",
        "source truth, accounting truth and independent control truth may lawfully differ and require explicit reconciliation roles",
        "an asset, metadata assertion, catalog listing, certification, technical schema and semantic model remain separate identities",
        "identity assertion, match candidate, authorized identity decision and merge remain separate states and authorities",
        "authoritative master, survivorship-derived golden projection, reference dataset and code set remain separate identities",
        "policy statement, policy decision and enforcement receipt remain separate identities",
        "accountability, delegation, stewardship, custody, approval and entitlement are qualified roles rather than one owner field",
        "a monitored subject, monitoring source occurrence, collection attempt, observation window, change signal and verified change event remain separate identities",
        "collector failure is evidence about observation coverage and never evidence that no change occurred",
        "a product release note is scoped evidence about a provider occurrence and never becomes canonical domain semantics by publication alone",
        "package identity, dependency version, vulnerability claim, deployed occurrence and observed behavior remain separate identities",
        "security exposure and availability behavior are independent requirements whose trade-off requires explicit authority and evidence",
        "a changed default is a versioned decision input and may not silently alter generated behavior",
        "dry-run, simulation, validation and effectful execution have distinct effect contracts and receipts",
        "an observed event fact, object attribute history, declared state definition, derived state, state transition and generated state-change event remain separate identities",
        "an entity, a time-qualified entity snapshot and an event correlated to that snapshot remain separate identities",
        "OCED semantic concepts, OCEL exchange profiles, event-knowledge-graph projections and temporal graph projections remain distinct representation contracts",
        "case selection and object-centric-to-case-centric projection are explicit potentially lossy transforms rather than implicit preprocessing",
        "optional model and agent capabilities import the deterministic core; no core semantic, binding, authorization or proof obligation depends on them",
        "automation modality is selected per typed use site and never creates an AI-prefixed semantic owner or default product boundary",
        "a model output, agent plan, validated claim, authorized effect intent and executed effect receipt remain separate identities",
        "a person, research work, work edition, contribution claim, formal concept, method, algorithm, implementation, dataset, experiment, benchmark and result remain separate identities",
        "authorship, invention, formalization, implementation, maintenance, standardization, supervision, advocacy and independent replication are distinct contributor relations",
        "citation count, reputation and topic proximity confer neither semantic ownership nor contribution attribution",
        "a prediction target, observed label, feature definition, information cutoff, model family, estimator, training objective, optimization algorithm, fitted artifact, calibrated predictor, prediction result, decision rule and action remain separate identities",
        "training, tuning, model selection, calibration, evaluation and production-monitoring populations and receipts remain separate identities",
        "a score, calibrated probability, uncertainty statement, causal effect estimate, recommendation and authorized decision are not interchangeable",
    ):
        if law not in metamodel.get("constitution", []):
            errors.append(f"missing constitutional law: {law}")

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print(
        "PASS compiler closure contract: "
        f"{len(node_kinds)} node kinds, {len(edge_ids)} edge kinds, "
        f"{len(stages)} IR stages, {len(proof_ids)} proof obligations"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
