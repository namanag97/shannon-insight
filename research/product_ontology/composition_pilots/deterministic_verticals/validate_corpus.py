#!/usr/bin/env python3
"""Validate deterministic vertical composition and fail-closed provider binding."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from build_corpus import ACCEPTANCE_GATE_TEMPLATES, CASE_SPECS, HERE, RESEARCH, build_outputs


def load_jsonl(path: Path, errors: list[str]) -> list[dict[str, Any]]:
    if not path.exists():
        errors.append(f"missing {path}")
        return []
    rows: list[dict[str, Any]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            errors.append(f"{path.name}:{line_number}: blank line")
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError as exc:
            errors.append(f"{path.name}:{line_number}: {exc}")
            continue
        if not isinstance(row, dict):
            errors.append(f"{path.name}:{line_number}: record is not an object")
        else:
            rows.append(row)
    return rows


def keyed(rows: list[dict[str, Any]], key: str, name: str, errors: list[str]) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for line_number, row in enumerate(rows, 1):
        identity = row.get(key)
        if not isinstance(identity, str) or not identity:
            errors.append(f"{name}:{line_number}: missing {key}")
        elif identity in result:
            errors.append(f"{name}:{line_number}: duplicate {key} {identity}")
        else:
            result[identity] = row
    return result


def main() -> int:
    errors: list[str] = []

    # Generated files are deterministic projections of declared inputs.
    for path, expected in build_outputs().items():
        if not path.exists():
            errors.append(f"missing generated file {path.name}")
        elif path.read_text(encoding="utf-8") != expected:
            errors.append(f"stale generated file {path.name}")

    compositions = keyed(
        load_jsonl(HERE / "vertical-compositions.jsonl", errors),
        "composition_id", "vertical-compositions.jsonl", errors,
    )
    substitutions = keyed(
        load_jsonl(HERE / "substitution-trials.jsonl", errors),
        "trial_id", "substitution-trials.jsonl", errors,
    )
    removals = keyed(
        load_jsonl(HERE / "optional-extension-removal-trials.jsonl", errors),
        "trial_id", "optional-extension-removal-trials.jsonl", errors,
    )
    acceptance_contracts = keyed(
        load_jsonl(HERE / "vertical-acceptance-contracts.jsonl", errors),
        "acceptance_contract_id", "vertical-acceptance-contracts.jsonl", errors,
    )
    acceptance_gates = keyed(
        load_jsonl(HERE / "vertical-acceptance-gates.jsonl", errors),
        "acceptance_gate_id", "vertical-acceptance-gates.jsonl", errors,
    )
    reuse = json.loads((HERE / "cross-vertical-reuse.json").read_text(encoding="utf-8"))
    manifest = json.loads((HERE / "manifest.json").read_text(encoding="utf-8"))

    if len(compositions) != 4:
        errors.append(f"expected four unrelated vertical compositions, found {len(compositions)}")
    if len({row.get("industry_id") for row in compositions.values()}) != 4:
        errors.append("vertical compositions do not use four distinct industries")
    if len({row.get("unit_of_analysis") for row in compositions.values()}) != 4:
        errors.append("vertical compositions do not preserve distinct units of analysis")
    if len(acceptance_contracts) != len(compositions):
        errors.append("vertical acceptance contract count does not match compositions")
    if len(acceptance_gates) != len(compositions) * len(ACCEPTANCE_GATE_TEMPLATES):
        errors.append("vertical acceptance gate matrix is incomplete")

    registry = RESEARCH / "domain_atlas/compiler/library_registry"
    libraries = keyed(load_jsonl(registry / "library-contributions.jsonl", errors), "library_id", "library registry", errors)
    requirements = keyed(load_jsonl(registry / "capability-requirements.jsonl", errors), "requirement_id", "requirements", errors)
    requirements_by_subject = {row["subject_ref"]: row for row in requirements.values()}
    offers = keyed(load_jsonl(registry / "capability-offers.jsonl", errors), "offer_id", "portable offers", errors)
    offers_by_subject = {row["subject_ref"]: row for row in offers.values()}
    products = keyed(
        load_jsonl(RESEARCH / "product_ontology/global_boundary_research/product-archetypes.jsonl", errors),
        "record_id", "product archetypes", errors,
    )
    binder_root = RESEARCH / "domain_atlas/compiler/binder_solver"
    binder_requirements = keyed(load_jsonl(binder_root / "requirements.jsonl", errors), "id", "binder requirements", errors)
    binder_offers = keyed(load_jsonl(binder_root / "offers.jsonl", errors), "id", "binder offers", errors)
    binder_evaluations = keyed(load_jsonl(binder_root / "requirement-offer-evaluations.jsonl", errors), "id", "binder evaluations", errors)
    binder_examples = keyed(load_jsonl(binder_root / "examples.jsonl", errors), "id", "binder examples", errors)
    model_class_root = RESEARCH / "domain_atlas/compiler/model_class_adjudication"
    model_classes = keyed(load_jsonl(model_class_root / "model-classes.jsonl", errors), "id", "formal model classes", errors)
    model_class_traces = keyed(load_jsonl(model_class_root / "classification-traces.jsonl", errors), "id", "model-class traces", errors)
    model_class_results = keyed(load_jsonl(model_class_root / "adjudication-results.jsonl", errors), "id", "model-class results", errors)

    specs = {row["composition_id"]: row for row in CASE_SPECS}
    for composition_id, composition in compositions.items():
        spec = specs.get(composition_id)
        if spec is None:
            errors.append(f"{composition_id}: no declared composition specification")
            continue
        cases = keyed(load_jsonl(RESEARCH / spec["case_file"], errors), "record_id", spec["case_file"], errors)
        source_systems = keyed(load_jsonl(RESEARCH / spec["source_file"], errors), "record_id", spec["source_file"], errors)
        shapes = keyed(load_jsonl(RESEARCH / spec["shape_file"], errors), "record_id", spec["shape_file"], errors)
        evidence = keyed(load_jsonl(RESEARCH / spec["evidence_file"], errors), "record_id", spec["evidence_file"], errors)
        case = cases.get(composition.get("vertical_case_ref"))
        if case is None:
            errors.append(f"{composition_id}: unresolved vertical case")
            continue
        if case.get("llm_dependency") not in {"none", "prohibited_core"}:
            errors.append(f"{composition_id}: upstream case has an LLM dependency")
        for field, index in (
            ("source_system_refs", source_systems),
            ("data_shape_refs", shapes),
            ("evidence_refs", evidence),
        ):
            unresolved = sorted(set(case.get(field, [])) - set(index))
            if unresolved:
                errors.append(f"{composition_id}: unresolved {field}: {unresolved}")
            if composition.get(field) != case.get(field):
                errors.append(f"{composition_id}: {field} drifted from upstream case")

        required = set(composition.get("required_library_refs", []))
        conditional = {row["library_ref"] for row in composition.get("conditional_library_bindings", [])}
        unresolved_libraries = sorted((required | conditional) - set(libraries))
        if unresolved_libraries:
            errors.append(f"{composition_id}: unresolved libraries: {unresolved_libraries}")
        forbidden = sorted(ref for ref in required | conditional if ref.startswith("library.mae."))
        if forbidden:
            errors.append(f"{composition_id}: model/agent libraries entered the core: {forbidden}")
        if composition.get("selected_optional_extension_requirement_refs"):
            errors.append(f"{composition_id}: optional model/agent requirements were ambiently selected")

        expected_required_requirements = sorted(requirements_by_subject[ref]["requirement_id"] for ref in required)
        expected_conditional_requirements = sorted(requirements_by_subject[ref]["requirement_id"] for ref in conditional)
        if composition.get("required_requirement_refs") != expected_required_requirements:
            errors.append(f"{composition_id}: required requirement projection is not exact")
        if composition.get("conditional_requirement_refs") != expected_conditional_requirements:
            errors.append(f"{composition_id}: conditional requirement projection is not exact")
        expected_offers = sorted(offers_by_subject[ref]["offer_id"] for ref in required)
        if composition.get("withheld_portable_offer_refs") != expected_offers:
            errors.append(f"{composition_id}: portable-offer projection is not exact")
        for ref in required:
            offer = offers_by_subject[ref]
            if offer.get("portable") is not False or offer.get("observed_independent_qualified_implementations") != 0:
                errors.append(f"{composition_id}: {ref} improperly claims a portable qualified offer")

        unresolved_products = sorted(set(composition.get("product_refs", [])) - set(products))
        if unresolved_products:
            errors.append(f"{composition_id}: unresolved products: {unresolved_products}")
        method_bindings = {row["vertical_method_ref"]: row["exact_library_refs"] for row in composition.get("method_bindings", [])}
        if set(method_bindings) != set(case.get("method_refs", [])):
            errors.append(f"{composition_id}: method bindings do not exactly cover upstream methods")
        for method_ref, bound_libraries in method_bindings.items():
            outside = sorted(set(bound_libraries) - (required | conditional))
            if outside:
                errors.append(f"{composition_id}: {method_ref} binds unselected libraries {outside}")

        physical_requirements = composition.get("physical_binding_requirement_refs", [])
        candidate_physical_offers = composition.get("physical_binding_candidate_offer_refs", [])
        refused_physical_offers = composition.get("physical_binding_refused_offer_refs", [])
        evaluation_refs = composition.get("binder_evaluation_refs", [])
        if physical_requirements != sorted(spec.get("physical_binding_requirement_refs", [])):
            errors.append(f"{composition_id}: physical binding requirement projection drifted")
        if candidate_physical_offers != sorted(spec.get("physical_binding_candidate_offer_refs", [])):
            errors.append(f"{composition_id}: physical binding candidate projection drifted")
        if refused_physical_offers != sorted(spec.get("physical_binding_refused_offer_refs", [])):
            errors.append(f"{composition_id}: physical binding refusal projection drifted")
        if evaluation_refs != sorted(spec.get("binder_evaluation_refs", [])):
            errors.append(f"{composition_id}: binder evaluation projection drifted")
        for ref, index, label in (
            *((ref, binder_requirements, "binder requirement") for ref in physical_requirements),
            *((ref, binder_offers, "binder offer") for ref in candidate_physical_offers + refused_physical_offers),
            *((ref, binder_evaluations, "binder evaluation") for ref in evaluation_refs),
        ):
            if ref not in index:
                errors.append(f"{composition_id}: unresolved {label} {ref}")
        binder_trace_ref = composition.get("binder_vertical_trace_ref")
        if binder_trace_ref != spec.get("binder_vertical_trace_ref"):
            errors.append(f"{composition_id}: binder vertical trace projection drifted")
        elif binder_trace_ref and binder_trace_ref not in binder_examples:
            errors.append(f"{composition_id}: unresolved binder vertical trace {binder_trace_ref}")
        if composition.get("physical_binding_model_class_status") != spec.get("physical_binding_model_class_status", "not_narrowed_to_exact_provider_model_class"):
            errors.append(f"{composition_id}: physical model-class status drifted")
        model_projection_fields = [
            "broad_model_class_adjudication_trace_ref",
            "broad_model_class_adjudication_result_ref",
            "screen_model_class_adjudication_trace_ref",
            "screen_model_class_adjudication_result_ref",
        ]
        for field in model_projection_fields:
            if composition.get(field) != spec.get(field):
                errors.append(f"{composition_id}: {field} projection drifted")
        if composition.get("screen_formal_model_class_refs", []) != sorted(spec.get("screen_formal_model_class_refs", [])):
            errors.append(f"{composition_id}: screen formal model-class projection drifted")
        for field, index, label in [
            ("broad_model_class_adjudication_trace_ref", model_class_traces, "broad model-class trace"),
            ("broad_model_class_adjudication_result_ref", model_class_results, "broad model-class result"),
            ("screen_model_class_adjudication_trace_ref", model_class_traces, "screen model-class trace"),
            ("screen_model_class_adjudication_result_ref", model_class_results, "screen model-class result"),
        ]:
            ref = composition.get(field)
            if ref and ref not in index:
                errors.append(f"{composition_id}: unresolved {label} {ref}")
        for ref in composition.get("screen_formal_model_class_refs", []):
            if ref not in model_classes:
                errors.append(f"{composition_id}: unresolved formal model class {ref}")

        phases = composition.get("compile_phase_verdicts", {})
        if phases.get("library_and_requirement_resolution") != "pass_structural":
            errors.append(f"{composition_id}: structural library resolution did not pass")
        if phases.get("physical_provider_binding") != spec.get("physical_binding_verdict", "refused_no_qualified_offers"):
            errors.append(f"{composition_id}: physical binding did not fail closed")
        if phases.get("execution") != "not_attempted" or phases.get("vertical_acceptance") != "not_executed":
            errors.append(f"{composition_id}: corpus overclaims execution or vertical acceptance")
        qualification = composition.get("qualification_summary", {})
        if qualification.get("qualified_binding_count") != 0 or qualification.get("portable_binding_count") != 0:
            errors.append(f"{composition_id}: unexecuted composition claims qualified bindings")

    contracts_by_composition: dict[str, list[dict[str, Any]]] = {}
    gates_by_composition: dict[str, list[dict[str, Any]]] = {}
    for contract in acceptance_contracts.values():
        contracts_by_composition.setdefault(contract.get("composition_ref"), []).append(contract)
    for gate in acceptance_gates.values():
        gates_by_composition.setdefault(gate.get("composition_ref"), []).append(gate)
    expected_gate_kinds = {row["gate_kind"] for row in ACCEPTANCE_GATE_TEMPLATES}
    for composition_id, composition in compositions.items():
        contracts = contracts_by_composition.get(composition_id, [])
        gates = gates_by_composition.get(composition_id, [])
        if len(contracts) != 1:
            errors.append(f"{composition_id}: expected exactly one vertical acceptance contract")
            continue
        contract = contracts[0]
        if contract.get("vertical_case_ref") != composition["vertical_case_ref"]:
            errors.append(f"{composition_id}: acceptance contract case identity drifted")
        if contract.get("authority_roles") != composition["actors"]:
            errors.append(f"{composition_id}: acceptance authorities drifted from the industry case")
        if contract.get("proposal_or_action_boundary") != composition["decision_or_action"]:
            errors.append(f"{composition_id}: acceptance action boundary drifted")
        if contract.get("binding_prerequisite_verdict") != composition["compile_phase_verdicts"]["physical_provider_binding"]:
            errors.append(f"{composition_id}: acceptance contract lost its physical-binding prerequisite")
        if contract.get("current_verdict") != "not_executed_blocked" or contract.get("receipt_refs"):
            errors.append(f"{composition_id}: acceptance contract fabricated evidence or a verdict")
        expected_gate_refs = sorted(gate["acceptance_gate_id"] for gate in gates)
        if sorted(contract.get("required_gate_refs", [])) != expected_gate_refs:
            errors.append(f"{composition_id}: acceptance contract does not close over its gates")
        if len(gates) != len(ACCEPTANCE_GATE_TEMPLATES):
            errors.append(f"{composition_id}: incomplete acceptance gate set")
            continue
        if {gate.get("gate_kind") for gate in gates} != expected_gate_kinds:
            errors.append(f"{composition_id}: acceptance gate kinds drifted")
        if sorted(gate.get("ordinal") for gate in gates) != list(range(1, len(ACCEPTANCE_GATE_TEMPLATES) + 1)):
            errors.append(f"{composition_id}: acceptance gate order is incomplete")
        for gate in gates:
            if gate.get("vertical_case_ref") != composition["vertical_case_ref"]:
                errors.append(f"{gate.get('acceptance_gate_id')}: vertical case drifted")
            if gate.get("blocking") is not True or gate.get("execution_status") != "not_executed" or gate.get("receipt_refs"):
                errors.append(f"{gate.get('acceptance_gate_id')}: unexecuted blocking gate was weakened")
            if gate.get("evidence_source_refs") != composition["evidence_refs"]:
                errors.append(f"{gate.get('acceptance_gate_id')}: industry evidence refs drifted")
            if not gate.get("required_evidence") or not gate.get("refusal_law"):
                errors.append(f"{gate.get('acceptance_gate_id')}: acceptance obligation is not executable/refusable")

    energy_composition = compositions.get("composition.vertical.energy_pipeline_nomination_capacity", {})
    expected_energy_requirements = ["requirement.bind.lp_precise_terminal"]
    if energy_composition.get("physical_binding_requirement_refs") != expected_energy_requirements:
        errors.append("energy pipeline composition lost its precise terminal-status requirement")
    if energy_composition.get("physical_binding_model_class_status") != "screen_classified_continuous_lp_broad_case_refused":
        errors.append("energy pipeline composition lost the broad-refusal/screen-classification boundary")
    broad_result = model_class_results.get(energy_composition.get("broad_model_class_adjudication_result_ref"), {})
    screen_result = model_class_results.get(energy_composition.get("screen_model_class_adjudication_result_ref"), {})
    if broad_result.get("matched_class_refs") or broad_result.get("disposition") != "requested_class_refused":
        errors.append("energy pipeline broad problem was not deterministically refused as LP")
    if screen_result.get("matched_class_refs") != ["class.mca.continuous_lp"]:
        errors.append("energy pipeline screening cut did not classify exactly as continuous LP")
    if screen_result.get("disposition") != "classified_but_vertical_unaccepted" or screen_result.get("provider_bindable") is not False:
        errors.append("energy pipeline screening classification bypassed provider/vertical fail-closure")
    energy_eval_states = {
        ref: binder_evaluations.get(ref, {}).get("binding_result")
        for ref in energy_composition.get("binder_evaluation_refs", [])
    }
    if energy_eval_states != {
        "evaluation.bind.lp_precise.highspy_highs.1_15_1": "typed_gap",
        "evaluation.bind.lp_precise.ortools_glop_mpsolver_python.9_15_6755": "refused",
    }:
        errors.append("energy pipeline exact provider evaluation states drifted")
    energy_trace = binder_examples.get(energy_composition.get("binder_vertical_trace_ref"), {})
    if energy_trace.get("upstream_case_ref") != energy_composition.get("vertical_case_ref"):
        errors.append("energy pipeline composition and binder trace do not resolve the same industry case")
    if energy_trace.get("model_class_adjudication_result_ref") != energy_composition.get("screen_model_class_adjudication_result_ref"):
        errors.append("energy pipeline composition and binder do not consume the same model-class result")
    energy_physical_gates = [
        gate for gate in acceptance_gates.values()
        if gate.get("composition_ref") == "composition.vertical.energy_pipeline_nomination_capacity"
        and gate.get("gate_kind") == "physical_conformance"
    ]
    expected_energy_physical_obligations = [
        *energy_composition.get("physical_binding_requirement_refs", []),
        *energy_composition.get("physical_binding_candidate_offer_refs", []),
        *energy_composition.get("physical_binding_refused_offer_refs", []),
    ]
    if len(energy_physical_gates) != 1 or energy_physical_gates[0].get("case_specific_obligations") != expected_energy_physical_obligations:
        errors.append("energy acceptance contract lost exact physical requirement/offer obligations")

    manufacturing_composition = compositions.get("composition.vertical.manufacturing_finite_capacity_schedule", {})
    if manufacturing_composition.get("physical_binding_requirement_refs") != ["requirement.bind.cp_sat_exact_scope"]:
        errors.append("manufacturing composition lost its exact CP-SAT requirement")
    if manufacturing_composition.get("physical_binding_model_class_status") != "classified_cp_sat_fragment_enterprise_formulation_unaccepted":
        errors.append("manufacturing composition lost its class/formulation acceptance boundary")
    manufacturing_result = model_class_results.get(manufacturing_composition.get("screen_model_class_adjudication_result_ref"), {})
    if set(manufacturing_result.get("matched_class_refs", [])) != {"class.mca.cp_sat_integer", "class.mca.finite_domain_cp"}:
        errors.append("manufacturing composition did not preserve both finite-domain CP and CP-SAT facets")
    if manufacturing_result.get("provider_bindable") is not False:
        errors.append("manufacturing model-class result bypassed provider fail-closure")
    manufacturing_eval_states = {
        ref: binder_evaluations.get(ref, {}).get("binding_result")
        for ref in manufacturing_composition.get("binder_evaluation_refs", [])
    }
    if manufacturing_eval_states != {
        "evaluation.bind.cp_sat_exact.ortools_cp_sat_python.9_15_6755": "typed_gap",
    }:
        errors.append("manufacturing exact provider evaluation state drifted")
    manufacturing_trace = binder_examples.get(manufacturing_composition.get("binder_vertical_trace_ref"), {})
    if manufacturing_trace.get("upstream_case_ref") != manufacturing_composition.get("vertical_case_ref"):
        errors.append("manufacturing composition and binder trace do not resolve the same industry case")
    if manufacturing_trace.get("model_class_adjudication_result_ref") != manufacturing_composition.get("screen_model_class_adjudication_result_ref"):
        errors.append("manufacturing composition and binder do not consume the same model-class result")
    manufacturing_physical_gates = [
        gate for gate in acceptance_gates.values()
        if gate.get("composition_ref") == "composition.vertical.manufacturing_finite_capacity_schedule"
        and gate.get("gate_kind") == "physical_conformance"
    ]
    expected_manufacturing_physical_obligations = [
        *manufacturing_composition.get("physical_binding_requirement_refs", []),
        *manufacturing_composition.get("physical_binding_candidate_offer_refs", []),
        *manufacturing_composition.get("physical_binding_refused_offer_refs", []),
    ]
    if len(manufacturing_physical_gates) != 1 or manufacturing_physical_gates[0].get("case_specific_obligations") != expected_manufacturing_physical_obligations:
        errors.append("manufacturing acceptance contract lost exact physical requirement/offer obligations")

    # Provider names do not prove replaceability: exact contracts and evidence recompute each verdict.
    provider_rows = (
        load_jsonl(RESEARCH / "domain_atlas/universes/method_kernels/compiler-requirements-offers.jsonl", errors)
        + load_jsonl(RESEARCH / "domain_atlas/universes/operations_research/compiler-requirements-offers.jsonl", errors)
    )
    provider_offers = {row["offer_id"]: row for row in provider_rows if row.get("record_kind") == "capability_offer"}
    for trial_id, trial in substitutions.items():
        incumbent = provider_offers.get(trial.get("incumbent_offer_ref"))
        substitute = provider_offers.get(trial.get("substitute_offer_ref"))
        if incumbent is None or substitute is None:
            errors.append(f"{trial_id}: unresolved provider offer")
            continue
        required_contracts = set(trial.get("required_contract_refs", []))
        incumbent_missing = sorted(required_contracts - set(incumbent.get("contract_refs", [])))
        substitute_missing = sorted(required_contracts - set(substitute.get("contract_refs", [])))
        identity_failures = []
        if incumbent.get("offer_kind") == "provider_project_facade":
            identity_failures.append("incumbent_is_provider_project_facade")
        if substitute.get("offer_kind") == "provider_project_facade":
            identity_failures.append("substitute_is_provider_project_facade")
        if identity_failures:
            verdict = "refused_offer_identity_too_broad"
        elif incumbent_missing or substitute_missing:
            verdict = "refused_capability_mismatch"
        elif not incumbent.get("conformance_receipts") or not substitute.get("conformance_receipts"):
            verdict = "refused_unqualified_evidence"
        else:
            verdict = "eligible_for_scoped_differential_test_not_portability"
        if trial.get("incumbent_missing_contract_refs") != incumbent_missing:
            errors.append(f"{trial_id}: incumbent missing-contract calculation drifted")
        if trial.get("substitute_missing_contract_refs") != substitute_missing:
            errors.append(f"{trial_id}: substitute missing-contract calculation drifted")
        if trial.get("offer_identity_failures") != identity_failures:
            errors.append(f"{trial_id}: offer-identity calculation drifted")
        if trial.get("verdict") != verdict or trial.get("portability_claim") is not False:
            errors.append(f"{trial_id}: substitution verdict does not fail closed")
        if trial.get("executed_test_evidence_is_qualification") is not False:
            errors.append(f"{trial_id}: executed tests were collapsed into qualification")

    forecast_trial = substitutions.get("substitution.health.forecast.sktime_to_statsforecast", {})
    if forecast_trial.get("verdict") != "refused_capability_mismatch":
        errors.append("forecast substitution must refuse because reconciliation is absent")
    expected_trial_verdicts = {
        "substitution.health.optimization.ortools_to_highs": "refused_offer_identity_too_broad",
        "substitution.health.simulation.anylogic_to_simio": "refused_offer_identity_too_broad",
        "substitution.health.forecast.sktime_to_statsforecast": "refused_capability_mismatch",
        "substitution.commerce.process.pm4py_to_prom": "refused_unqualified_evidence",
        "substitution.commerce.document.tika_to_pdfbox": "refused_unqualified_evidence",
        "substitution.health.optimization.ortools_glop_to_highspy.safe_lp_exact_scope": "refused_unqualified_evidence",
        "substitution.health.optimization.ortools_glop_to_highspy.precise_terminal_exact_scope": "refused_capability_mismatch",
        "substitution.energy.pipeline_nomination.ortools_glop_to_highspy.precise_terminal_exact_scope": "refused_capability_mismatch",
    }
    if set(substitutions) != set(expected_trial_verdicts):
        errors.append("provider substitution trial inventory drifted")
    for trial_id, expected_verdict in expected_trial_verdicts.items():
        if substitutions.get(trial_id, {}).get("verdict") != expected_verdict:
            errors.append(f"{trial_id}: expected {expected_verdict}")
    safe_exact = substitutions.get(
        "substitution.health.optimization.ortools_glop_to_highspy.safe_lp_exact_scope", {}
    )
    if not safe_exact.get("incumbent_executed_test_receipt_refs") or not safe_exact.get("substitute_executed_test_receipt_refs"):
        errors.append("exact safe-LP substitution lost its executed-test evidence")
    if safe_exact.get("incumbent_conformance_receipt_refs") or safe_exact.get("substitute_conformance_receipt_refs"):
        errors.append("exact safe-LP executed evidence was promoted to qualification")

    # Optional extensions must be removable and ambient injection must be refused.
    negative_id = "removal.ambient_agent_injection.negative_twin"
    for composition_id in compositions:
        matches = [row for row in removals.values() if row.get("composition_ref") == composition_id and row.get("trial_id") != negative_id]
        if len(matches) != 1:
            errors.append(f"{composition_id}: expected one model/agent removal proof")
        elif matches[0].get("selected_matching_library_refs") or matches[0].get("selected_matching_requirement_refs") or matches[0].get("verdict") != "pass_graph_unchanged":
            errors.append(f"{composition_id}: deterministic graph is not independent of optional extensions")
    negative = removals.get(negative_id)
    if negative is None or negative.get("verdict") != "refused_ambient_extension_without_intent":
        errors.append("ambient agent injection negative twin did not refuse")

    composition_refs = reuse.get("composition_refs", [])
    if set(composition_refs) != set(compositions):
        errors.append("cross-vertical reuse proof does not cover every composition")
    elif all(ref in compositions for ref in composition_refs):
        library_sets = {ref: set(compositions[ref]["required_library_refs"]) for ref in composition_refs}
        shared = set.intersection(*library_sets.values())
        if reuse.get("shared_library_refs") != sorted(shared):
            errors.append("cross-vertical shared-library proof drifted")
        expected_non_shared = {
            ref: sorted(libraries - shared)
            for ref, libraries in sorted(library_sets.items())
        }
        if reuse.get("non_shared_library_refs_by_composition") != expected_non_shared:
            errors.append("cross-vertical non-shared library proof drifted")
        expected_pairwise = {
            f"{left_id}__{right_id}": sorted(library_sets[left_id] & library_sets[right_id])
            for index, left_id in enumerate(sorted(library_sets))
            for right_id in sorted(library_sets)[index + 1:]
        }
        if reuse.get("pairwise_shared_library_refs") != expected_pairwise:
            errors.append("cross-vertical pairwise reuse proof drifted")
        if not shared or any(not refs for refs in expected_non_shared.values()):
            errors.append("cross-vertical proof does not demonstrate shared core plus vertical differences")
    if reuse.get("qualification_verdict") != "not_executed":
        errors.append("cross-vertical structural proof overclaims qualification")

    expected_counts = {
        "vertical_compositions": len(compositions),
        "provider_substitution_trials": len(substitutions),
        "optional_extension_removal_trials": len(removals),
        "vertical_acceptance_contracts": len(acceptance_contracts),
        "vertical_acceptance_gates": len(acceptance_gates),
        "shared_libraries": len(reuse.get("shared_library_refs", [])),
    }
    if manifest.get("counts") != expected_counts:
        errors.append("manifest counts drifted")
    if manifest.get("completion_claim") is not False or manifest.get("status") != "candidate_not_qualified":
        errors.append("manifest overclaims completion or qualification")
    for file_name, expected_digest in manifest.get("file_sha256", {}).items():
        path = HERE / file_name
        if not path.exists() or hashlib.sha256(path.read_bytes()).hexdigest() != expected_digest:
            errors.append(f"manifest digest mismatch for {file_name}")

    if errors:
        print("FAIL deterministic vertical composition corpus")
        for error in errors:
            print(f"- {error}")
        return 1
    print(
        "PASS deterministic vertical composition corpus: "
        f"{len(compositions)} verticals, {manifest['counts']['shared_libraries']} shared libraries, "
        f"{len(substitutions)} fail-closed substitutions, {len(acceptance_contracts)} unexecuted acceptance contracts, "
        f"{len(acceptance_gates)} blocking acceptance gates, 0 qualified provider bindings"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
