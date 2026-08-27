#!/usr/bin/env python3
"""Dependency-free structural checks for the product-boundary pilot."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent


def load_jsonl(path: Path) -> list[dict]:
    records: list[dict] = []
    with path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            if not line.strip():
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError as error:
                raise ValueError(f"{path}:{line_number}: {error}") from error
    return records


def main() -> int:
    errors: list[str] = []
    nodes = load_jsonl(ROOT / "registry/nodes.jsonl")
    edges = load_jsonl(ROOT / "registry/edges.jsonl")
    evidence = load_jsonl(ROOT / "registry/evidence.jsonl")
    all_records = nodes + edges + evidence

    by_id: dict[str, dict] = {}
    for record in all_records:
        record_id = record.get("record_id")
        if not record_id or record_id in by_id:
            errors.append(f"missing or duplicate record_id: {record_id!r}")
        else:
            by_id[record_id] = record

    required_product_fields = {
        "product_kind", "sovereign_question", "users", "jobs", "outcomes", "owned_meanings",
        "excluded_meanings", "adoption_boundary", "exit_boundary", "lifecycle_boundary",
        "authority_boundary", "slo_boundary", "failure_boundary", "economic_boundary", "interfaces",
        "truth_contract_id", "truth_profile_status", "boundary_evaluation", "evidence_ids", "confidence",
    }
    products = [record for record in nodes if record.get("record_kind") == "product"]
    for product in products:
        product_id = product["record_id"]
        missing = sorted(required_product_fields - set(product))
        if missing:
            errors.append(f"product {product_id} missing fields: {missing}")
        evaluation = product.get("boundary_evaluation", {})
        scores = evaluation.get("scores", {})
        if sum(scores.values()) != evaluation.get("total"):
            errors.append(f"product {product_id} boundary score total mismatch")
        for interface_id in product.get("interfaces", []):
            if interface_id not in by_id or by_id[interface_id].get("record_kind") != "interface":
                errors.append(f"product {product_id} references unknown interface {interface_id}")
        truth_id = product.get("truth_contract_id")
        if truth_id not in by_id or by_id[truth_id].get("record_kind") != "truth_contract":
            errors.append(f"product {product_id} references unknown truth contract {truth_id}")
        for evidence_id in product.get("evidence_ids", []):
            if evidence_id not in by_id or by_id[evidence_id].get("record_kind") != "evidence":
                errors.append(f"product {product_id} references unknown evidence {evidence_id}")

    for edge in edges:
        for endpoint in ("from", "to"):
            if edge.get(endpoint) not in by_id:
                errors.append(f"edge {edge.get('record_id')} has unknown {endpoint}: {edge.get(endpoint)}")
        for evidence_id in edge.get("evidence_ids", []):
            if evidence_id not in by_id or by_id[evidence_id].get("record_kind") != "evidence":
                errors.append(f"edge {edge.get('record_id')} references unknown evidence {evidence_id}")

    with (ROOT / "truth-contract.json").open(encoding="utf-8") as handle:
        truth = json.load(handle)
    truth_items = [item for group in truth.get("groups", []) for item in group.get("items", [])]
    expected_truth_ids = [f"T{index:03d}" for index in range(1, 111)]
    actual_truth_ids = [item.get("id") for item in truth_items]
    if actual_truth_ids != expected_truth_ids:
        errors.append("truth contract must contain exactly ordered T001 through T110")
    if truth.get("contract_id") not in by_id:
        errors.append("truth contract JSON has no corresponding graph node")

    adjudication_outputs: list[str] = []
    for adjudication in ("lakehouse", "movement", "governance_semantics", "analytical_methods", "consumption_experiences", "platform_control", "model_decision_serving", "query_warehouse_search_protection", "semantic_metrics_formulas", "collaboration_privacy_resolution_assurance", "representation_codec_boundary", "analytical_operations", "shared_owner_boundaries"):
        validator = ROOT / f"adjudications/{adjudication}/validate.py"
        if not validator.is_file():
            errors.append(f"{adjudication} adjudication validator is missing")
            continue
        completed = subprocess.run(
            [sys.executable, str(validator)],
            cwd=ROOT.parent.parent,
            text=True,
            capture_output=True,
            check=False,
        )
        output = completed.stdout.strip()
        if completed.returncode != 0:
            errors.append(f"{adjudication} adjudication failed: " + (output or completed.stderr.strip()))
        elif output:
            adjudication_outputs.append(output)

    global_validator = ROOT / "global_boundary_research/validate_corpus.py"
    if not global_validator.is_file():
        errors.append("global product-boundary validator is missing")
    else:
        completed = subprocess.run(
            [sys.executable, str(global_validator)],
            cwd=ROOT.parent.parent,
            text=True,
            capture_output=True,
            check=False,
        )
        output = completed.stdout.strip()
        if completed.returncode != 0:
            errors.append(
                "global product-boundary corpus failed: "
                + (output or completed.stderr.strip())
            )
        elif output:
            adjudication_outputs.append(output)

    readiness_validator = ROOT / "dossier_readiness/validate.py"
    if not readiness_validator.is_file():
        errors.append("retained-product dossier-readiness validator is missing")
    else:
        completed = subprocess.run(
            [sys.executable, str(readiness_validator)],
            cwd=ROOT.parent.parent,
            text=True,
            capture_output=True,
            check=False,
        )
        output = completed.stdout.strip()
        if completed.returncode != 0:
            errors.append(
                "retained-product dossier readiness failed: "
                + (output or completed.stderr.strip())
            )
        elif output:
            adjudication_outputs.append(output)

    boundary_migration_validator = ROOT / "boundary_migration_projection/validate.py"
    if not boundary_migration_validator.is_file():
        errors.append("non-retained product-boundary migration validator is missing")
    else:
        completed = subprocess.run(
            [sys.executable, str(boundary_migration_validator)],
            cwd=boundary_migration_validator.parent,
            text=True,
            capture_output=True,
            check=False,
        )
        output = completed.stdout.strip()
        if completed.returncode != 0:
            errors.append(
                "non-retained product-boundary migration projection failed: "
                + (output or completed.stderr.strip())
            )
        elif output:
            adjudication_outputs.append(output)

    qualification_validator = ROOT / "qualification_program/validate.py"
    if not qualification_validator.is_file():
        errors.append("product qualification-program validator is missing")
    else:
        completed = subprocess.run(
            [sys.executable, str(qualification_validator)],
            cwd=ROOT.parent.parent,
            text=True,
            capture_output=True,
            check=False,
        )
        output = completed.stdout.strip()
        if completed.returncode != 0:
            errors.append(
                "product qualification program failed: "
                + (output or completed.stderr.strip())
            )
        elif output:
            adjudication_outputs.append(output)

    data_sharing_execution_validator = (
        ROOT.parent
        / "domain_atlas/compiler/conformance_evaluation/executions/data_sharing_exact_scope/validate_execution.py"
    )
    if not data_sharing_execution_validator.is_file():
        errors.append("data-sharing exact-scope execution validator is missing")
    else:
        completed = subprocess.run(
            [sys.executable, str(data_sharing_execution_validator)],
            cwd=ROOT.parent.parent,
            text=True,
            capture_output=True,
            check=False,
        )
        output = completed.stdout.strip()
        if completed.returncode != 0:
            errors.append(
                "data-sharing exact-scope execution failed: "
                + (output or completed.stderr.strip())
            )
        elif output:
            adjudication_outputs.append(output)

    convergence_rebase_validator = ROOT / "research_convergence_rebase/validate.py"
    if not convergence_rebase_validator.is_file():
        errors.append("research-convergence rebase validator is missing")
    else:
        completed = subprocess.run(
            [sys.executable, str(convergence_rebase_validator)],
            cwd=convergence_rebase_validator.parent,
            text=True,
            capture_output=True,
            check=False,
        )
        output = completed.stdout.strip()
        if completed.returncode != 0:
            errors.append("research-convergence rebase failed: " + (output or completed.stderr.strip()))
        elif output:
            adjudication_outputs.append(output)

    exact_api_validator = ROOT.parent / "domain_atlas/compiler/library_registry/exact_api_closure/validate.py"
    if not exact_api_validator.is_file():
        errors.append("exact-API closure-program validator is missing")
    else:
        completed = subprocess.run(
            [sys.executable, str(exact_api_validator)],
            cwd=ROOT.parent.parent,
            text=True,
            capture_output=True,
            check=False,
        )
        output = completed.stdout.strip()
        if completed.returncode != 0:
            errors.append("exact-API closure program failed: " + (output or completed.stderr.strip()))
        elif output:
            adjudication_outputs.append(output)

    bulk_contract_validator = ROOT.parent / "domain_atlas/compiler/library_registry/contract_generation/validate.py"
    if not bulk_contract_validator.is_file():
        errors.append("bulk contract-generation validator is missing")
    else:
        completed = subprocess.run(
            [sys.executable, str(bulk_contract_validator)],
            cwd=ROOT.parent.parent,
            text=True,
            capture_output=True,
            check=False,
        )
        output = completed.stdout.strip()
        if completed.returncode != 0:
            errors.append("bulk contract-generation program failed: " + (output or completed.stderr.strip()))
        elif output:
            adjudication_outputs.append(output)

    contract_pilot_validator = ROOT.parent / "domain_atlas/compiler/library_registry/contract_generation/pilots/lineage_provenance_evidence/validate.py"
    if not contract_pilot_validator.is_file():
        errors.append("lineage/provenance/evidence contract-generation pilot validator is missing")
    else:
        completed = subprocess.run(
            [sys.executable, str(contract_pilot_validator)],
            cwd=ROOT.parent.parent,
            text=True,
            capture_output=True,
            check=False,
        )
        output = completed.stdout.strip()
        if completed.returncode != 0:
            errors.append("lineage/provenance/evidence contract-generation pilot failed: " + (output or completed.stderr.strip()))
        elif output:
            adjudication_outputs.append(output)

    wave0_shape_validator = ROOT.parent / "domain_atlas/compiler/library_registry/contract_generation/wave0_data_shape_boundaries/validate.py"
    if not wave0_shape_validator.is_file():
        errors.append("Wave-0 data-shape boundary validator is missing")
    else:
        completed = subprocess.run(
            [sys.executable, str(wave0_shape_validator)],
            cwd=ROOT.parent.parent,
            text=True,
            capture_output=True,
            check=False,
        )
        output = completed.stdout.strip()
        if completed.returncode != 0:
            errors.append("Wave-0 data-shape boundary adjudication failed: " + (output or completed.stderr.strip()))
        elif output:
            adjudication_outputs.append(output)

    semantic_axis_validator = ROOT.parent / "domain_atlas/compiler/library_registry/contract_generation/semantic_decomposition/validate.py"
    if not semantic_axis_validator.is_file():
        errors.append("semantic-axis decomposition validator is missing")
    else:
        completed = subprocess.run(
            [sys.executable, str(semantic_axis_validator)],
            cwd=ROOT.parent.parent,
            text=True,
            capture_output=True,
            check=False,
        )
        output = completed.stdout.strip()
        if completed.returncode != 0:
            errors.append("semantic-axis decomposition failed: " + (output or completed.stderr.strip()))
        elif output:
            adjudication_outputs.append(output)

    phase1_semantic_validator = ROOT.parent / "domain_atlas/compiler/library_registry/contract_generation/semantic_decomposition/phase1_subject_grain/validate.py"
    if not phase1_semantic_validator.is_file():
        errors.append("Phase-1 subject/identity/grain semantic validator is missing")
    else:
        completed = subprocess.run(
            [sys.executable, str(phase1_semantic_validator)],
            cwd=ROOT.parent.parent,
            text=True,
            capture_output=True,
            check=False,
        )
        output = completed.stdout.strip()
        if completed.returncode != 0:
            errors.append("Phase-1 subject/identity/grain semantic constitution failed: " + (output or completed.stderr.strip()))
        elif output:
            adjudication_outputs.append(output)

    phase2_semantic_validator = ROOT.parent / "domain_atlas/compiler/library_registry/contract_generation/semantic_decomposition/phase2_dynamics_information/validate.py"
    if not phase2_semantic_validator.is_file():
        errors.append("Phase-2 dynamics/information semantic validator is missing")
    else:
        completed = subprocess.run(
            [sys.executable, str(phase2_semantic_validator)],
            cwd=ROOT.parent.parent,
            text=True,
            capture_output=True,
            check=False,
        )
        output = completed.stdout.strip()
        if completed.returncode != 0:
            errors.append("Phase-2 dynamics/information semantic constitution failed: " + (output or completed.stderr.strip()))
        elif output:
            adjudication_outputs.append(output)

    phase3_semantic_validator = ROOT.parent / "domain_atlas/compiler/library_registry/contract_generation/semantic_decomposition/phase3_authority_effect_safety/validate.py"
    if not phase3_semantic_validator.is_file():
        errors.append("Phase-3 authority/effect/safety semantic validator is missing")
    else:
        completed = subprocess.run(
            [sys.executable, str(phase3_semantic_validator)],
            cwd=ROOT.parent.parent,
            text=True,
            capture_output=True,
            check=False,
        )
        output = completed.stdout.strip()
        if completed.returncode != 0:
            errors.append("Phase-3 authority/effect/safety semantic constitution failed: " + (output or completed.stderr.strip()))
        elif output:
            adjudication_outputs.append(output)

    phase4_semantic_validator = ROOT.parent / "domain_atlas/compiler/library_registry/contract_generation/semantic_decomposition/phase4_representation_evolution/validate.py"
    if not phase4_semantic_validator.is_file():
        errors.append("Phase-4 representation/evolution semantic validator is missing")
    else:
        completed = subprocess.run(
            [sys.executable, str(phase4_semantic_validator)],
            cwd=ROOT.parent.parent,
            text=True,
            capture_output=True,
            check=False,
        )
        output = completed.stdout.strip()
        if completed.returncode != 0:
            errors.append("Phase-4 representation/evolution semantic constitution failed: " + (output or completed.stderr.strip()))
        elif output:
            adjudication_outputs.append(output)

    phase5_semantic_validator = ROOT.parent / "domain_atlas/compiler/library_registry/contract_generation/semantic_decomposition/phase5_behavior_resources_proof/validate.py"
    if not phase5_semantic_validator.is_file():
        errors.append("Phase-5 behavior/resources/proof semantic validator is missing")
    else:
        completed = subprocess.run(
            [sys.executable, str(phase5_semantic_validator)],
            cwd=ROOT.parent.parent,
            text=True,
            capture_output=True,
            check=False,
        )
        output = completed.stdout.strip()
        if completed.returncode != 0:
            errors.append("Phase-5 behavior/resources/proof semantic constitution failed: " + (output or completed.stderr.strip()))
        elif output:
            adjudication_outputs.append(output)

    semantic_coverage_validator = ROOT.parent / "domain_atlas/compiler/library_registry/contract_generation/semantic_decomposition/validate_constitution_coverage.py"
    if not semantic_coverage_validator.is_file():
        errors.append("semantic constitution coverage validator is missing")
    else:
        completed = subprocess.run(
            [sys.executable, str(semantic_coverage_validator)],
            cwd=ROOT.parent.parent,
            text=True,
            capture_output=True,
            check=False,
        )
        output = completed.stdout.strip()
        if completed.returncode != 0:
            errors.append("semantic constitution coverage failed: " + (output or completed.stderr.strip()))
        elif output:
            adjudication_outputs.append(output)

    semantic_applicability_validator = ROOT.parent / "domain_atlas/compiler/library_registry/contract_generation/semantic_decomposition/applicability_matrices/validate.py"
    if not semantic_applicability_validator.is_file():
        errors.append("semantic applicability matrix validator is missing")
    else:
        completed = subprocess.run(
            [sys.executable, str(semantic_applicability_validator)],
            cwd=ROOT.parent.parent,
            text=True,
            capture_output=True,
            check=False,
        )
        output = completed.stdout.strip()
        if completed.returncode != 0:
            errors.append("semantic applicability matrices failed: " + (output or completed.stderr.strip()))
        elif output:
            adjudication_outputs.append(output)

    method_kernel_semantic_pilot_validator = ROOT.parent / "domain_atlas/compiler/library_registry/contract_generation/semantic_decomposition/applicability_matrices/pilot_analytical_method_kernels/validate.py"
    if not method_kernel_semantic_pilot_validator.is_file():
        errors.append("analytical method-kernel semantic pilot validator is missing")
    else:
        completed = subprocess.run(
            [sys.executable, str(method_kernel_semantic_pilot_validator)],
            cwd=ROOT.parent.parent,
            text=True,
            capture_output=True,
            check=False,
        )
        output = completed.stdout.strip()
        if completed.returncode != 0:
            errors.append("analytical method-kernel semantic pilot failed: " + (output or completed.stderr.strip()))
        elif output:
            adjudication_outputs.append(output)

    global_structured_semantic_validator = ROOT.parent / "domain_atlas/compiler/library_registry/contract_generation/semantic_decomposition/structured_projection/validate.py"
    if not global_structured_semantic_validator.is_file():
        errors.append("global structured semantic projection validator is missing")
    else:
        completed = subprocess.run(
            [sys.executable, str(global_structured_semantic_validator)],
            cwd=ROOT.parent.parent,
            text=True,
            capture_output=True,
            check=False,
        )
        output = completed.stdout.strip()
        if completed.returncode != 0:
            errors.append("global structured semantic projection failed: " + (output or completed.stderr.strip()))
        elif output:
            adjudication_outputs.append(output)

    source_authority_audit_validator = ROOT.parent / "domain_atlas/compiler/library_registry/contract_generation/semantic_decomposition/source_authority_audit/validate.py"
    if not source_authority_audit_validator.is_file():
        errors.append("family source-authority audit validator is missing")
    else:
        completed = subprocess.run(
            [sys.executable, str(source_authority_audit_validator)],
            cwd=ROOT.parent.parent,
            text=True,
            capture_output=True,
            check=False,
        )
        output = completed.stdout.strip()
        if completed.returncode != 0:
            errors.append("family source-authority audit failed: " + (output or completed.stderr.strip()))
        elif output:
            adjudication_outputs.append(output)

    p0_identity_grain_validator = ROOT.parent / "domain_atlas/compiler/library_registry/contract_generation/semantic_decomposition/p0_identity_grain/validate.py"
    if not p0_identity_grain_validator.is_file():
        errors.append("P0 identity/grain semantic validator is missing")
    else:
        completed = subprocess.run(
            [sys.executable, str(p0_identity_grain_validator)],
            cwd=ROOT.parent.parent,
            text=True,
            capture_output=True,
            check=False,
        )
        output = completed.stdout.strip()
        if completed.returncode != 0:
            errors.append("P0 identity/grain semantic corpus failed: " + (output or completed.stderr.strip()))
        elif output:
            adjudication_outputs.append(output)

    p3e_grain_evidence_validator = ROOT.parent / "domain_atlas/compiler/library_registry/contract_generation/semantic_decomposition/p3e_grain_cardinality_evidence/validate.py"
    if not p3e_grain_evidence_validator.is_file():
        errors.append("P3E grain/cardinality evidence validator is missing")
    else:
        completed = subprocess.run(
            [sys.executable, str(p3e_grain_evidence_validator)],
            cwd=ROOT.parent.parent,
            text=True,
            capture_output=True,
            check=False,
        )
        output = completed.stdout.strip()
        if completed.returncode != 0:
            errors.append("P3E grain/cardinality evidence campaign failed: " + (output or completed.stderr.strip()))
        elif output:
            adjudication_outputs.append(output)

    p3e_grain_coordinate_validator = ROOT.parent / "domain_atlas/compiler/library_registry/contract_generation/semantic_decomposition/p3e_grain_coordinate_ontology/validate.py"
    if not p3e_grain_coordinate_validator.is_file():
        errors.append("P3E operation-positioned grain coordinate validator is missing")
    else:
        completed = subprocess.run(
            [sys.executable, str(p3e_grain_coordinate_validator)],
            cwd=ROOT.parent.parent,
            text=True,
            capture_output=True,
            check=False,
        )
        output = completed.stdout.strip()
        if completed.returncode != 0:
            errors.append("P3E operation-positioned grain coordinate rebase failed: " + (output or completed.stderr.strip()))
        elif output:
            adjudication_outputs.append(output)

    p3s_state_change_evidence_validator = ROOT.parent / "domain_atlas/compiler/library_registry/contract_generation/semantic_decomposition/p3s_state_change_evidence/validate.py"
    if not p3s_state_change_evidence_validator.is_file():
        errors.append("P3S state/change evidence validator is missing")
    else:
        completed = subprocess.run(
            [sys.executable, str(p3s_state_change_evidence_validator)],
            cwd=ROOT.parent.parent,
            text=True,
            capture_output=True,
            check=False,
        )
        output = completed.stdout.strip()
        if completed.returncode != 0:
            errors.append("P3S state/change evidence campaign failed: " + (output or completed.stderr.strip()))
        elif output:
            adjudication_outputs.append(output)

    p3s_state_change_coordinate_validator = ROOT.parent / "domain_atlas/compiler/library_registry/contract_generation/semantic_decomposition/p3s_state_change_coordinate_ontology/validate.py"
    if not p3s_state_change_coordinate_validator.is_file():
        errors.append("P3S subject-positioned state/change coordinate validator is missing")
    else:
        completed = subprocess.run(
            [sys.executable, str(p3s_state_change_coordinate_validator)],
            cwd=ROOT.parent.parent,
            text=True,
            capture_output=True,
            check=False,
        )
        output = completed.stdout.strip()
        if completed.returncode != 0:
            errors.append("P3S subject-positioned state/change coordinate rebase failed: " + (output or completed.stderr.strip()))
        elif output:
            adjudication_outputs.append(output)

    p3o_order_topology_evidence_validator = ROOT.parent / "domain_atlas/compiler/library_registry/contract_generation/semantic_decomposition/p3o_order_topology_evidence/validate.py"
    if not p3o_order_topology_evidence_validator.is_file():
        errors.append("P3O order/topology evidence validator is missing")
    else:
        completed = subprocess.run(
            [sys.executable, str(p3o_order_topology_evidence_validator)],
            cwd=ROOT.parent.parent,
            text=True,
            capture_output=True,
            check=False,
        )
        output = completed.stdout.strip()
        if completed.returncode != 0:
            errors.append("P3O order/topology evidence campaign failed: " + (output or completed.stderr.strip()))
        elif output:
            adjudication_outputs.append(output)

    p3o_order_topology_coordinate_validator = ROOT.parent / "domain_atlas/compiler/library_registry/contract_generation/semantic_decomposition/p3o_order_topology_coordinate_ontology/validate.py"
    if not p3o_order_topology_coordinate_validator.is_file():
        errors.append("P3O relation-positioned order/topology coordinate validator is missing")
    else:
        completed = subprocess.run(
            [sys.executable, str(p3o_order_topology_coordinate_validator)],
            cwd=ROOT.parent.parent,
            text=True,
            capture_output=True,
            check=False,
        )
        output = completed.stdout.strip()
        if completed.returncode != 0:
            errors.append("P3O relation-positioned order/topology coordinate rebase failed: " + (output or completed.stderr.strip()))
        elif output:
            adjudication_outputs.append(output)

    p3c_composition_algebra_evidence_validator = ROOT.parent / "domain_atlas/compiler/library_registry/contract_generation/semantic_decomposition/p3c_composition_algebra_evidence/validate.py"
    if not p3c_composition_algebra_evidence_validator.is_file():
        errors.append("P3C composition/algebra evidence validator is missing")
    else:
        completed = subprocess.run(
            [sys.executable, str(p3c_composition_algebra_evidence_validator)],
            cwd=ROOT.parent.parent,
            text=True,
            capture_output=True,
            check=False,
        )
        output = completed.stdout.strip()
        if completed.returncode != 0:
            errors.append("P3C composition/algebra evidence campaign failed: " + (output or completed.stderr.strip()))
        elif output:
            adjudication_outputs.append(output)

    p3c_composition_algebra_coordinate_validator = ROOT.parent / "domain_atlas/compiler/library_registry/contract_generation/semantic_decomposition/p3c_composition_algebra_coordinate_ontology/validate.py"
    if not p3c_composition_algebra_coordinate_validator.is_file():
        errors.append("P3C operator-positioned composition/algebra coordinate validator is missing")
    else:
        completed = subprocess.run(
            [sys.executable, str(p3c_composition_algebra_coordinate_validator)],
            cwd=ROOT.parent.parent,
            text=True,
            capture_output=True,
            check=False,
        )
        output = completed.stdout.strip()
        if completed.returncode != 0:
            errors.append("P3C operator-positioned composition/algebra coordinate rebase failed: " + (output or completed.stderr.strip()))
        elif output:
            adjudication_outputs.append(output)

    p3i_identity_equality_evidence_validator = ROOT.parent / "domain_atlas/compiler/library_registry/contract_generation/semantic_decomposition/p3i_identity_equality_evidence/validate.py"
    if not p3i_identity_equality_evidence_validator.is_file():
        errors.append("P3I identity/equality evidence validator is missing")
    else:
        completed = subprocess.run(
            [sys.executable, str(p3i_identity_equality_evidence_validator)],
            cwd=ROOT.parent.parent,
            text=True,
            capture_output=True,
            check=False,
        )
        output = completed.stdout.strip()
        if completed.returncode != 0:
            errors.append("P3I identity/equality evidence campaign failed: " + (output or completed.stderr.strip()))
        elif output:
            adjudication_outputs.append(output)

    p3i_identity_equality_coordinate_validator = ROOT.parent / "domain_atlas/compiler/library_registry/contract_generation/semantic_decomposition/p3i_identity_equality_coordinate_ontology/validate.py"
    if not p3i_identity_equality_coordinate_validator.is_file():
        errors.append("P3I subject/relation-positioned identity/equality coordinate validator is missing")
    else:
        completed = subprocess.run(
            [sys.executable, str(p3i_identity_equality_coordinate_validator)],
            cwd=ROOT.parent.parent,
            text=True,
            capture_output=True,
            check=False,
        )
        output = completed.stdout.strip()
        if completed.returncode != 0:
            errors.append("P3I subject/relation-positioned identity/equality coordinate rebase failed: " + (output or completed.stderr.strip()))
        elif output:
            adjudication_outputs.append(output)

    p3u_partiality_uncertainty_evidence_validator = ROOT.parent / "domain_atlas/compiler/library_registry/contract_generation/semantic_decomposition/p3u_partiality_uncertainty_evidence/validate.py"
    if not p3u_partiality_uncertainty_evidence_validator.is_file():
        errors.append("P3U partiality/uncertainty evidence validator is missing")
    else:
        completed = subprocess.run(
            [sys.executable, str(p3u_partiality_uncertainty_evidence_validator)],
            cwd=ROOT.parent.parent,
            text=True,
            capture_output=True,
            check=False,
        )
        output = completed.stdout.strip()
        if completed.returncode != 0:
            errors.append("P3U partiality/uncertainty evidence campaign failed: " + (output or completed.stderr.strip()))
        elif output:
            adjudication_outputs.append(output)

    p3u_partiality_uncertainty_coordinate_validator = ROOT.parent / "domain_atlas/compiler/library_registry/contract_generation/semantic_decomposition/p3u_partiality_uncertainty_coordinate_ontology/validate.py"
    if not p3u_partiality_uncertainty_coordinate_validator.is_file():
        errors.append("P3U bearer-positioned partiality/uncertainty coordinate validator is missing")
    else:
        completed = subprocess.run(
            [sys.executable, str(p3u_partiality_uncertainty_coordinate_validator)],
            cwd=ROOT.parent.parent,
            text=True,
            capture_output=True,
            check=False,
        )
        output = completed.stdout.strip()
        if completed.returncode != 0:
            errors.append("P3U bearer-positioned partiality/uncertainty coordinate rebase failed: " + (output or completed.stderr.strip()))

    time_coordinate_validator = ROOT.parent / "domain_atlas/compiler/library_registry/contract_generation/semantic_decomposition/time_coordinate_ontology/validate.py"
    if not time_coordinate_validator.is_file():
        errors.append("bearer-positioned time coordinate validator is missing")
    else:
        completed = subprocess.run(
            [sys.executable, str(time_coordinate_validator)],
            cwd=time_coordinate_validator.parent,
            text=True,
            capture_output=True,
        )
        output = completed.stdout.strip()
        if output:
            print(output)
        if completed.returncode:
            errors.append("bearer-positioned time coordinate rebase failed: " + (output or completed.stderr.strip()))

    semantic_object_coordinate_validator = ROOT.parent / "domain_atlas/compiler/library_registry/contract_generation/semantic_decomposition/semantic_object_coordinate_ontology/validate.py"
    if not semantic_object_coordinate_validator.is_file():
        errors.append("bearer-positioned semantic-object coordinate validator is missing")
    else:
        completed = subprocess.run(
            [sys.executable, str(semantic_object_coordinate_validator)],
            cwd=semantic_object_coordinate_validator.parent,
            text=True,
            capture_output=True,
        )
        output = completed.stdout.strip()
        if output:
            print(output)
        if completed.returncode:
            errors.append("bearer-positioned semantic-object coordinate rebase failed: " + (output or completed.stderr.strip()))

    semantic_role_coordinate_validator = ROOT.parent / "domain_atlas/compiler/library_registry/contract_generation/semantic_decomposition/semantic_role_coordinate_ontology/validate.py"
    if not semantic_role_coordinate_validator.is_file():
        errors.append("interaction-positioned semantic-role coordinate validator is missing")
    else:
        completed = subprocess.run(
            [sys.executable, str(semantic_role_coordinate_validator)],
            cwd=semantic_role_coordinate_validator.parent,
            text=True,
            capture_output=True,
        )
        output = completed.stdout.strip()
        if output:
            print(output)
        if completed.returncode:
            errors.append("interaction-positioned semantic-role coordinate rebase failed: " + (output or completed.stderr.strip()))

    authority_trust_coordinate_validator = ROOT.parent / "domain_atlas/compiler/library_registry/contract_generation/semantic_decomposition/authority_trust_coordinate_ontology/validate.py"
    if not authority_trust_coordinate_validator.is_file():
        errors.append("bearer-positioned authority/trust coordinate validator is missing")
    else:
        completed = subprocess.run(
            [sys.executable, str(authority_trust_coordinate_validator)],
            cwd=authority_trust_coordinate_validator.parent,
            text=True,
            capture_output=True,
        )
        output = completed.stdout.strip()
        if output:
            print(output)
        if completed.returncode:
            errors.append("bearer-positioned authority/trust coordinate rebase failed: " + (output or completed.stderr.strip()))

    effect_boundary_coordinate_validator = ROOT.parent / "domain_atlas/compiler/library_registry/contract_generation/semantic_decomposition/effect_boundary_coordinate_ontology/validate.py"
    if not effect_boundary_coordinate_validator.is_file():
        errors.append("stage-positioned effect-boundary coordinate validator is missing")
    else:
        completed = subprocess.run(
            [sys.executable, str(effect_boundary_coordinate_validator)],
            cwd=effect_boundary_coordinate_validator.parent,
            text=True,
            capture_output=True,
        )
        output = completed.stdout.strip()
        if output:
            print(output)
        if completed.returncode:
            errors.append("stage-positioned effect-boundary coordinate rebase failed: " + (output or completed.stderr.strip()))

    evidence_conformance_coordinate_validator = ROOT.parent / "domain_atlas/compiler/library_registry/contract_generation/semantic_decomposition/evidence_conformance_coordinate_ontology/validate.py"
    if not evidence_conformance_coordinate_validator.is_file():
        errors.append("claim-positioned evidence/conformance coordinate validator is missing")
    else:
        completed = subprocess.run(
            [sys.executable, str(evidence_conformance_coordinate_validator)],
            cwd=evidence_conformance_coordinate_validator.parent,
            text=True,
            capture_output=True,
        )
        output = completed.stdout.strip()
        if output:
            print(output)
        if completed.returncode:
            errors.append("claim-positioned evidence/conformance coordinate rebase failed: " + (output or completed.stderr.strip()))
        elif output:
            adjudication_outputs.append(output)

    representation_coordinate_validator = ROOT.parent / "domain_atlas/compiler/library_registry/contract_generation/semantic_decomposition/representation_coordinate_ontology/validate.py"
    if not representation_coordinate_validator.is_file():
        errors.append("layer-positioned representation coordinate validator is missing")
    else:
        completed = subprocess.run(
            [sys.executable, str(representation_coordinate_validator)],
            cwd=representation_coordinate_validator.parent,
            text=True,
            capture_output=True,
        )
        output = completed.stdout.strip()
        if output:
            print(output)
        if completed.returncode:
            errors.append("layer-positioned representation coordinate rebase failed: " + (output or completed.stderr.strip()))
        elif output:
            adjudication_outputs.append(output)

    compatibility_evolution_coordinate_validator = ROOT.parent / "domain_atlas/compiler/library_registry/contract_generation/semantic_decomposition/compatibility_evolution_coordinate_ontology/validate.py"
    if not compatibility_evolution_coordinate_validator.is_file():
        errors.append("directional compatibility/evolution coordinate validator is missing")
    else:
        completed = subprocess.run(
            [sys.executable, str(compatibility_evolution_coordinate_validator)],
            cwd=compatibility_evolution_coordinate_validator.parent,
            text=True,
            capture_output=True,
        )
        output = completed.stdout.strip()
        if output:
            print(output)
        if completed.returncode:
            errors.append("directional compatibility/evolution coordinate rebase failed: " + (output or completed.stderr.strip()))
        elif output:
            adjudication_outputs.append(output)

    privacy_security_safety_coordinate_validator = ROOT.parent / "domain_atlas/compiler/library_registry/contract_generation/semantic_decomposition/privacy_security_safety_coordinate_ontology/validate.py"
    if not privacy_security_safety_coordinate_validator.is_file():
        errors.append("cross-concern privacy/security/safety coordinate validator is missing")
    else:
        completed = subprocess.run(
            [sys.executable, str(privacy_security_safety_coordinate_validator)],
            cwd=privacy_security_safety_coordinate_validator.parent,
            text=True,
            capture_output=True,
        )
        output = completed.stdout.strip()
        if output:
            print(output)
        if completed.returncode:
            errors.append("cross-concern privacy/security/safety coordinate rebase failed: " + (output or completed.stderr.strip()))
        elif output:
            adjudication_outputs.append(output)

    resources_failure_coordinate_validator = ROOT.parent / "domain_atlas/compiler/library_registry/contract_generation/semantic_decomposition/resources_failure_coordinate_ontology/validate.py"
    if not resources_failure_coordinate_validator.is_file():
        errors.append("finite-resource/total-failure coordinate validator is missing")
    else:
        completed = subprocess.run(
            [sys.executable, str(resources_failure_coordinate_validator)],
            cwd=resources_failure_coordinate_validator.parent,
            text=True,
            capture_output=True,
        )
        output = completed.stdout.strip()
        if output:
            print(output)
        if completed.returncode:
            errors.append("finite-resource/total-failure coordinate rebase failed: " + (output or completed.stderr.strip()))
        elif output:
            adjudication_outputs.append(output)

    coordinate_route_completion_validator = ROOT.parent / "domain_atlas/compiler/library_registry/contract_generation/semantic_decomposition/coordinate_route_completion/validate.py"
    if not coordinate_route_completion_validator.is_file():
        errors.append("all-cell coordinate route completion validator is missing")
    else:
        completed = subprocess.run(
            [sys.executable, str(coordinate_route_completion_validator)],
            cwd=coordinate_route_completion_validator.parent,
            text=True,
            capture_output=True,
        )
        output = completed.stdout.strip()
        if output:
            print(output)
        if completed.returncode:
            errors.append("all-cell coordinate route completion failed: " + (output or completed.stderr.strip()))
        elif output:
            adjudication_outputs.append(output)

    coordinate_compiler_ir_normalization_validator = ROOT.parent / "domain_atlas/compiler/library_registry/contract_generation/semantic_decomposition/coordinate_compiler_ir_normalization/validate.py"
    if not coordinate_compiler_ir_normalization_validator.is_file():
        errors.append("coordinate compiler-IR normalization validator is missing")
    else:
        completed = subprocess.run(
            [sys.executable, str(coordinate_compiler_ir_normalization_validator)],
            cwd=coordinate_compiler_ir_normalization_validator.parent,
            text=True,
            capture_output=True,
        )
        output = completed.stdout.strip()
        if output:
            print(output)
        if completed.returncode:
            errors.append("coordinate compiler-IR normalization failed: " + (output or completed.stderr.strip()))
        elif output:
            adjudication_outputs.append(output)

    cross_axis_seam_tests_validator = ROOT.parent / "domain_atlas/compiler/library_registry/contract_generation/semantic_decomposition/cross_axis_seam_tests/validate.py"
    if not cross_axis_seam_tests_validator.is_file():
        errors.append("cross-axis seam negative-twin validator is missing")
    else:
        completed = subprocess.run(
            [sys.executable, str(cross_axis_seam_tests_validator)],
            cwd=cross_axis_seam_tests_validator.parent,
            text=True,
            capture_output=True,
        )
        output = completed.stdout.strip()
        if output:
            print(output)
        if completed.returncode:
            errors.append("cross-axis seam negative-twin validation failed: " + (output or completed.stderr.strip()))
        elif output:
            adjudication_outputs.append(output)

    cross_axis_coordinate_audit_validator = ROOT.parent / "domain_atlas/compiler/library_registry/contract_generation/semantic_decomposition/cross_axis_coordinate_audit/validate.py"
    if not cross_axis_coordinate_audit_validator.is_file():
        errors.append("cross-axis coordinate coverage/compiler-surface audit validator is missing")
    else:
        completed = subprocess.run(
            [sys.executable, str(cross_axis_coordinate_audit_validator)],
            cwd=cross_axis_coordinate_audit_validator.parent,
            text=True,
            capture_output=True,
        )
        output = completed.stdout.strip()
        if output:
            print(output)
        if completed.returncode:
            errors.append("cross-axis coordinate coverage/compiler-surface audit failed: " + (output or completed.stderr.strip()))
        elif output:
            adjudication_outputs.append(output)

    library_coordinate_binding_projection_validator = ROOT.parent / "domain_atlas/compiler/library_registry/contract_generation/semantic_decomposition/library_coordinate_binding_projection/validate.py"
    if not library_coordinate_binding_projection_validator.is_file():
        errors.append("per-library coordinate compiler-binding projection validator is missing")
    else:
        completed = subprocess.run(
            [sys.executable, str(library_coordinate_binding_projection_validator)],
            cwd=library_coordinate_binding_projection_validator.parent,
            text=True,
            capture_output=True,
        )
        output = completed.stdout.strip()
        if output:
            print(output)
        if completed.returncode:
            errors.append("per-library coordinate compiler-binding projection failed: " + (output or completed.stderr.strip()))
        elif output:
            adjudication_outputs.append(output)

    product_coordinate_binding_projection_validator = ROOT.parent / "domain_atlas/compiler/library_registry/contract_generation/semantic_decomposition/product_coordinate_binding_projection/validate.py"
    if not product_coordinate_binding_projection_validator.is_file():
        errors.append("product/capability/solution-pack coordinate compiler-binding projection validator is missing")
    else:
        completed = subprocess.run(
            [sys.executable, str(product_coordinate_binding_projection_validator)],
            cwd=product_coordinate_binding_projection_validator.parent,
            text=True,
            capture_output=True,
        )
        output = completed.stdout.strip()
        if output:
            print(output)
        if completed.returncode:
            errors.append("product/capability/solution-pack coordinate compiler-binding projection failed: " + (output or completed.stderr.strip()))
        elif output:
            adjudication_outputs.append(output)

    targeted_evidence_coverage_validator = ROOT.parent / "domain_atlas/compiler/library_registry/contract_generation/semantic_decomposition/targeted_evidence_coverage/validate.py"
    if not targeted_evidence_coverage_validator.is_file():
        errors.append("targeted semantic-axis evidence coverage validator is missing")
    else:
        completed = subprocess.run(
            [sys.executable, str(targeted_evidence_coverage_validator)],
            cwd=ROOT.parent.parent,
            text=True,
            capture_output=True,
            check=False,
        )
        output = completed.stdout.strip()
        if completed.returncode != 0:
            errors.append("targeted semantic-axis evidence coverage failed: " + (output or completed.stderr.strip()))
        elif output:
            adjudication_outputs.append(output)

    targeted_evidence_cluster_adjudication_validator = ROOT.parent / "domain_atlas/compiler/library_registry/contract_generation/semantic_decomposition/targeted_evidence_cluster_adjudication/validate.py"
    if not targeted_evidence_cluster_adjudication_validator.is_file():
        errors.append("targeted evidence coordinate-cluster adjudication validator is missing")
    else:
        completed = subprocess.run(
            [sys.executable, str(targeted_evidence_cluster_adjudication_validator)],
            cwd=targeted_evidence_cluster_adjudication_validator.parent,
            text=True,
            capture_output=True,
        )
        output = completed.stdout.strip()
        if output:
            print(output)
        if completed.returncode:
            errors.append("targeted evidence coordinate-cluster adjudication failed: " + (output or completed.stderr.strip()))
        elif output:
            adjudication_outputs.append(output)

    process_analytics_semantic_slice_validator = ROOT.parent / "domain_atlas/compiler/library_registry/contract_generation/semantic_decomposition/process_analytics_semantic_slice/validate.py"
    if not process_analytics_semantic_slice_validator.is_file():
        errors.append("process analytics evidence-backed semantic-slice validator is missing")
    else:
        completed = subprocess.run(
            [sys.executable, str(process_analytics_semantic_slice_validator)],
            cwd=process_analytics_semantic_slice_validator.parent,
            text=True,
            capture_output=True,
        )
        output = completed.stdout.strip()
        if output:
            print(output)
        if completed.returncode:
            errors.append("process analytics evidence-backed semantic slice failed: " + (output or completed.stderr.strip()))
        elif output:
            adjudication_outputs.append(output)

    operations_research_semantic_slice_validator = ROOT.parent / "domain_atlas/compiler/library_registry/contract_generation/semantic_decomposition/operations_research_semantic_slice/validate.py"
    if not operations_research_semantic_slice_validator.is_file():
        errors.append("operations research evidence-backed semantic-slice validator is missing")
    else:
        completed = subprocess.run(
            [sys.executable, str(operations_research_semantic_slice_validator)],
            cwd=operations_research_semantic_slice_validator.parent,
            text=True,
            capture_output=True,
        )
        output = completed.stdout.strip()
        if output:
            print(output)
        if completed.returncode:
            errors.append("operations research evidence-backed semantic slice failed: " + (output or completed.stderr.strip()))
        elif output:
            adjudication_outputs.append(output)

    predictive_analytics_semantic_slice_validator = ROOT.parent / "domain_atlas/compiler/library_registry/contract_generation/semantic_decomposition/predictive_analytics_semantic_slice/validate.py"
    if not predictive_analytics_semantic_slice_validator.is_file():
        errors.append("predictive analytics evidence-backed semantic-slice validator is missing")
    else:
        completed = subprocess.run(
            [sys.executable, str(predictive_analytics_semantic_slice_validator)],
            cwd=predictive_analytics_semantic_slice_validator.parent,
            text=True,
            capture_output=True,
        )
        output = completed.stdout.strip()
        if output:
            print(output)
        if completed.returncode:
            errors.append("predictive analytics evidence-backed semantic slice failed: " + (output or completed.stderr.strip()))
        elif output:
            adjudication_outputs.append(output)

    causal_inference_semantic_slice_validator = ROOT.parent / "domain_atlas/compiler/library_registry/contract_generation/semantic_decomposition/causal_inference_semantic_slice/validate.py"
    if not causal_inference_semantic_slice_validator.is_file():
        errors.append("causal inference evidence-backed semantic-slice validator is missing")
    else:
        completed = subprocess.run(
            [sys.executable, str(causal_inference_semantic_slice_validator)],
            cwd=causal_inference_semantic_slice_validator.parent,
            text=True,
            capture_output=True,
        )
        output = completed.stdout.strip()
        if output:
            print(output)
        if completed.returncode:
            errors.append("causal inference evidence-backed semantic slice failed: " + (output or completed.stderr.strip()))
        elif output:
            adjudication_outputs.append(output)

    geospatial_analytics_semantic_slice_validator = ROOT.parent / "domain_atlas/compiler/library_registry/contract_generation/semantic_decomposition/geospatial_analytics_semantic_slice/validate.py"
    if not geospatial_analytics_semantic_slice_validator.is_file():
        errors.append("geospatial analytics evidence-backed semantic-slice validator is missing")
    else:
        completed = subprocess.run(
            [sys.executable, str(geospatial_analytics_semantic_slice_validator)],
            cwd=geospatial_analytics_semantic_slice_validator.parent,
            text=True,
            capture_output=True,
        )
        output = completed.stdout.strip()
        if output:
            print(output)
        if completed.returncode:
            errors.append("geospatial analytics evidence-backed semantic slice failed: " + (output or completed.stderr.strip()))
        elif output:
            adjudication_outputs.append(output)

    document_processing_semantic_slice_validator = ROOT.parent / "domain_atlas/compiler/library_registry/contract_generation/semantic_decomposition/document_processing_semantic_slice/validate.py"
    if not document_processing_semantic_slice_validator.is_file():
        errors.append("document processing evidence-backed semantic-slice validator is missing")
    else:
        completed = subprocess.run(
            [sys.executable, str(document_processing_semantic_slice_validator)],
            cwd=document_processing_semantic_slice_validator.parent,
            text=True,
            capture_output=True,
        )
        output = completed.stdout.strip()
        if output:
            print(output)
        if completed.returncode:
            errors.append("document processing evidence-backed semantic slice failed: " + (output or completed.stderr.strip()))
        elif output:
            adjudication_outputs.append(output)

    signal_condition_semantic_slice_validator = ROOT.parent / "domain_atlas/compiler/library_registry/contract_generation/semantic_decomposition/signal_condition_semantic_slice/validate.py"
    if not signal_condition_semantic_slice_validator.is_file():
        errors.append("signal condition evidence-backed semantic-slice validator is missing")
    else:
        completed = subprocess.run(
            [sys.executable, str(signal_condition_semantic_slice_validator)],
            cwd=signal_condition_semantic_slice_validator.parent,
            text=True,
            capture_output=True,
        )
        output = completed.stdout.strip()
        if output:
            print(output)
        if completed.returncode:
            errors.append("signal condition evidence-backed semantic slice failed: " + (output or completed.stderr.strip()))
        elif output:
            adjudication_outputs.append(output)

    statistical_inference_semantic_slice_validator = ROOT.parent / "domain_atlas/compiler/library_registry/contract_generation/semantic_decomposition/statistical_inference_semantic_slice/validate.py"
    if not statistical_inference_semantic_slice_validator.is_file():
        errors.append("statistical inference evidence-backed semantic-slice validator is missing")
    else:
        completed = subprocess.run(
            [sys.executable, str(statistical_inference_semantic_slice_validator)],
            cwd=statistical_inference_semantic_slice_validator.parent,
            text=True,
            capture_output=True,
        )
        output = completed.stdout.strip()
        if output:
            print(output)
        if completed.returncode:
            errors.append("statistical inference evidence-backed semantic slice failed: " + (output or completed.stderr.strip()))
        elif output:
            adjudication_outputs.append(output)

    query_olap_warehouse_semantic_slice_validator = ROOT.parent / "domain_atlas/compiler/library_registry/contract_generation/semantic_decomposition/query_olap_warehouse_semantic_slice/validate.py"
    if not query_olap_warehouse_semantic_slice_validator.is_file():
        errors.append("query/OLAP/warehouse evidence-backed semantic-slice validator is missing")
    else:
        completed = subprocess.run(
            [sys.executable, str(query_olap_warehouse_semantic_slice_validator)],
            cwd=query_olap_warehouse_semantic_slice_validator.parent,
            text=True,
            capture_output=True,
        )
        output = completed.stdout.strip()
        if output:
            print(output)
        if completed.returncode:
            errors.append("query/OLAP/warehouse evidence-backed semantic slice failed: " + (output or completed.stderr.strip()))
        elif output:
            adjudication_outputs.append(output)

    bi_visualization_metrics_semantic_slice_validator = ROOT.parent / "domain_atlas/compiler/library_registry/contract_generation/semantic_decomposition/bi_visualization_metrics_semantic_slice/validate.py"
    if not bi_visualization_metrics_semantic_slice_validator.is_file():
        errors.append("BI/visualization/metrics evidence-backed semantic-slice validator is missing")
    else:
        completed = subprocess.run(
            [sys.executable, str(bi_visualization_metrics_semantic_slice_validator)],
            cwd=bi_visualization_metrics_semantic_slice_validator.parent,
            text=True,
            capture_output=True,
        )
        output = completed.stdout.strip()
        if output:
            print(output)
        if completed.returncode:
            errors.append("BI/visualization/metrics evidence-backed semantic slice failed: " + (output or completed.stderr.strip()))
        elif output:
            adjudication_outputs.append(output)

    quality_reconciliation_controls_semantic_slice_validator = ROOT.parent / "domain_atlas/compiler/library_registry/contract_generation/semantic_decomposition/quality_reconciliation_controls_semantic_slice/validate.py"
    if not quality_reconciliation_controls_semantic_slice_validator.is_file():
        errors.append("quality/reconciliation/controls evidence-backed semantic-slice validator is missing")
    else:
        completed = subprocess.run(
            [sys.executable, str(quality_reconciliation_controls_semantic_slice_validator)],
            cwd=quality_reconciliation_controls_semantic_slice_validator.parent,
            text=True,
            capture_output=True,
        )
        output = completed.stdout.strip()
        if output:
            print(output)
        if completed.returncode:
            errors.append("quality/reconciliation/controls evidence-backed semantic slice failed: " + (output or completed.stderr.strip()))
        elif output:
            adjudication_outputs.append(output)

    graph_network_knowledge_semantic_slice_validator = ROOT.parent / "domain_atlas/compiler/library_registry/contract_generation/semantic_decomposition/graph_network_knowledge_semantic_slice/validate.py"
    if not graph_network_knowledge_semantic_slice_validator.is_file():
        errors.append("graph/network/knowledge evidence-backed semantic-slice validator is missing")
    else:
        completed = subprocess.run(
            [sys.executable, str(graph_network_knowledge_semantic_slice_validator)],
            cwd=graph_network_knowledge_semantic_slice_validator.parent,
            text=True,
            capture_output=True,
        )
        output = completed.stdout.strip()
        if output:
            print(output)
        if completed.returncode:
            errors.append("graph/network/knowledge evidence-backed semantic slice failed: " + (output or completed.stderr.strip()))
        elif output:
            adjudication_outputs.append(output)

    visual_image_inspection_semantic_slice_validator = ROOT.parent / "domain_atlas/compiler/library_registry/contract_generation/semantic_decomposition/visual_image_inspection_semantic_slice/validate.py"
    if not visual_image_inspection_semantic_slice_validator.is_file():
        errors.append("visual/image inspection evidence-backed semantic-slice validator is missing")
    else:
        completed = subprocess.run(
            [sys.executable, str(visual_image_inspection_semantic_slice_validator)],
            cwd=visual_image_inspection_semantic_slice_validator.parent,
            text=True,
            capture_output=True,
        )
        output = completed.stdout.strip()
        if output:
            print(output)
        if completed.returncode:
            errors.append("visual/image inspection evidence-backed semantic slice failed: " + (output or completed.stderr.strip()))
        elif output:
            adjudication_outputs.append(output)

    forecasting_planning_semantic_slice_validator = ROOT.parent / "domain_atlas/compiler/library_registry/contract_generation/semantic_decomposition/forecasting_planning_semantic_slice/validate.py"
    if not forecasting_planning_semantic_slice_validator.is_file():
        errors.append("forecasting/planning evidence-backed semantic-slice validator is missing")
    else:
        completed = subprocess.run(
            [sys.executable, str(forecasting_planning_semantic_slice_validator)],
            cwd=forecasting_planning_semantic_slice_validator.parent,
            text=True,
            capture_output=True,
        )
        output = completed.stdout.strip()
        if output:
            print(output)
        if completed.returncode:
            errors.append("forecasting/planning evidence-backed semantic slice failed: " + (output or completed.stderr.strip()))
        elif output:
            adjudication_outputs.append(output)

    annotation_labeling_evaluation_semantic_slice_validator = ROOT.parent / "domain_atlas/compiler/library_registry/contract_generation/semantic_decomposition/annotation_labeling_evaluation_semantic_slice/validate.py"
    if not annotation_labeling_evaluation_semantic_slice_validator.is_file():
        errors.append("annotation/labeling/evaluation evidence-backed semantic-slice validator is missing")
    else:
        completed = subprocess.run(
            [sys.executable, str(annotation_labeling_evaluation_semantic_slice_validator)],
            cwd=annotation_labeling_evaluation_semantic_slice_validator.parent,
            text=True,
            capture_output=True,
        )
        output = completed.stdout.strip()
        if output:
            print(output)
        if completed.returncode:
            errors.append("annotation/labeling/evaluation evidence-backed semantic slice failed: " + (output or completed.stderr.strip()))
        elif output:
            adjudication_outputs.append(output)

    entity_resolution_mastering_semantic_slice_validator = ROOT.parent / "domain_atlas/compiler/library_registry/contract_generation/semantic_decomposition/entity_resolution_mastering_semantic_slice/validate.py"
    if not entity_resolution_mastering_semantic_slice_validator.is_file():
        errors.append("entity-resolution/master/reference evidence-backed semantic-slice validator is missing")
    else:
        completed = subprocess.run(
            [sys.executable, str(entity_resolution_mastering_semantic_slice_validator)],
            cwd=entity_resolution_mastering_semantic_slice_validator.parent,
            text=True,
            capture_output=True,
        )
        output = completed.stdout.strip()
        if output:
            print(output)
        if completed.returncode:
            errors.append("entity-resolution/master/reference evidence-backed semantic slice failed: " + (output or completed.stderr.strip()))
        elif output:
            adjudication_outputs.append(output)

    data_preparation_profiling_semantic_slice_validator = ROOT.parent / "domain_atlas/compiler/library_registry/contract_generation/semantic_decomposition/data_preparation_profiling_semantic_slice/validate.py"
    if not data_preparation_profiling_semantic_slice_validator.is_file():
        errors.append("data-preparation/profiling evidence-backed semantic-slice validator is missing")
    else:
        completed = subprocess.run(
            [sys.executable, str(data_preparation_profiling_semantic_slice_validator)],
            cwd=data_preparation_profiling_semantic_slice_validator.parent,
            text=True,
            capture_output=True,
        )
        output = completed.stdout.strip()
        if output:
            print(output)
        if completed.returncode:
            errors.append("data-preparation/profiling evidence-backed semantic slice failed: " + (output or completed.stderr.strip()))
        elif output:
            adjudication_outputs.append(output)

    decision_automation_assurance_semantic_slice_validator = ROOT.parent / "domain_atlas/compiler/library_registry/contract_generation/semantic_decomposition/decision_automation_assurance_semantic_slice/validate.py"
    if not decision_automation_assurance_semantic_slice_validator.is_file():
        errors.append("decision-automation/assurance evidence-backed semantic-slice validator is missing")
    else:
        completed = subprocess.run(
            [sys.executable, str(decision_automation_assurance_semantic_slice_validator)],
            cwd=decision_automation_assurance_semantic_slice_validator.parent,
            text=True,
            capture_output=True,
        )
        output = completed.stdout.strip()
        if output:
            print(output)
        if completed.returncode:
            errors.append("decision-automation/assurance evidence-backed semantic slice failed: " + (output or completed.stderr.strip()))
        elif output:
            adjudication_outputs.append(output)

    search_information_retrieval_semantic_slice_validator = ROOT.parent / "domain_atlas/compiler/library_registry/contract_generation/semantic_decomposition/search_information_retrieval_semantic_slice/validate.py"
    if not search_information_retrieval_semantic_slice_validator.is_file():
        errors.append("search/information-retrieval evidence-backed semantic-slice validator is missing")
    else:
        completed = subprocess.run(
            [sys.executable, str(search_information_retrieval_semantic_slice_validator)],
            cwd=search_information_retrieval_semantic_slice_validator.parent,
            text=True,
            capture_output=True,
        )
        output = completed.stdout.strip()
        if output:
            print(output)
        if completed.returncode:
            errors.append("search/information-retrieval evidence-backed semantic slice failed: " + (output or completed.stderr.strip()))
        elif output:
            adjudication_outputs.append(output)

    analytical_formalism_frontier_validator = ROOT.parent / "domain_atlas/compiler/library_registry/contract_generation/semantic_decomposition/analytical_formalism_frontier/validate.py"
    if not analytical_formalism_frontier_validator.is_file():
        errors.append("analytical formalism coverage frontier validator is missing")
    else:
        completed = subprocess.run(
            [sys.executable, str(analytical_formalism_frontier_validator)],
            cwd=analytical_formalism_frontier_validator.parent,
            text=True,
            capture_output=True,
        )
        output = completed.stdout.strip()
        if output:
            print(output)
        if completed.returncode:
            errors.append("analytical formalism coverage frontier failed: " + (output or completed.stderr.strip()))
        elif output:
            adjudication_outputs.append(output)

    cross_slice_boundary_frontier_validator = ROOT.parent / "domain_atlas/compiler/library_registry/contract_generation/semantic_decomposition/cross_slice_boundary_frontier/validate.py"
    if not cross_slice_boundary_frontier_validator.is_file():
        errors.append("cross-slice boundary frontier validator is missing")
    else:
        completed = subprocess.run(
            [sys.executable, str(cross_slice_boundary_frontier_validator)],
            cwd=cross_slice_boundary_frontier_validator.parent,
            text=True,
            capture_output=True,
            check=False,
        )
        output = completed.stdout.strip()
        if completed.returncode != 0:
            errors.append("cross-slice boundary frontier failed: " + (output or completed.stderr.strip()))
        elif output:
            adjudication_outputs.append(output)

    semantic_research_frontier_validator = ROOT.parent / "domain_atlas/compiler/library_registry/contract_generation/semantic_decomposition/semantic_research_frontier/validate.py"
    if not semantic_research_frontier_validator.is_file():
        errors.append("semantic research frontier validator is missing")
    else:
        completed = subprocess.run(
            [sys.executable, str(semantic_research_frontier_validator)],
            cwd=ROOT.parent.parent,
            text=True,
            capture_output=True,
            check=False,
        )
        output = completed.stdout.strip()
        if completed.returncode != 0:
            errors.append("semantic research frontier failed: " + (output or completed.stderr.strip()))
        elif output:
            adjudication_outputs.append(output)

    semantic_decision_locus_validator = ROOT.parent / "domain_atlas/compiler/library_registry/contract_generation/semantic_decomposition/semantic_decision_locus_ontology/validate.py"
    if not semantic_decision_locus_validator.is_file():
        errors.append("semantic decision-locus ontology validator is missing")
    else:
        completed = subprocess.run(
            [sys.executable, str(semantic_decision_locus_validator)],
            cwd=ROOT.parent.parent,
            text=True,
            capture_output=True,
            check=False,
        )
        output = completed.stdout.strip()
        if completed.returncode != 0:
            errors.append("semantic decision-locus factorization failed: " + (output or completed.stderr.strip()))
        elif output:
            adjudication_outputs.append(output)

    semantic_gap_topology_validator = ROOT.parent / "domain_atlas/compiler/library_registry/contract_generation/semantic_decomposition/gap_topology/validate.py"
    if not semantic_gap_topology_validator.is_file():
        errors.append("semantic gap-topology validator is missing")
    else:
        completed = subprocess.run(
            [sys.executable, str(semantic_gap_topology_validator)],
            cwd=ROOT.parent.parent,
            text=True,
            capture_output=True,
            check=False,
        )
        output = completed.stdout.strip()
        if completed.returncode != 0:
            errors.append("semantic gap topology failed: " + (output or completed.stderr.strip()))
        elif output:
            adjudication_outputs.append(output)

    p1_authority_symbol_validator = ROOT.parent / "domain_atlas/compiler/library_registry/contract_generation/semantic_decomposition/p1_authority_symbols/validate.py"
    if not p1_authority_symbol_validator.is_file():
        errors.append("P1 source-authority/public-symbol validator is missing")
    else:
        completed = subprocess.run(
            [sys.executable, str(p1_authority_symbol_validator)],
            cwd=ROOT.parent.parent,
            text=True,
            capture_output=True,
            check=False,
        )
        output = completed.stdout.strip()
        if completed.returncode != 0:
            errors.append("P1 source-authority/public-symbol corpus failed: " + (output or completed.stderr.strip()))
        elif output:
            adjudication_outputs.append(output)

    p2_owner_adjudication_validator = ROOT.parent / "domain_atlas/compiler/library_registry/contract_generation/semantic_decomposition/p2_owner_adjudication/validate.py"
    p1b_foundation_authority_validator = ROOT.parent / "domain_atlas/compiler/library_registry/contract_generation/semantic_decomposition/p1b_foundation_authority_adjudication/validate.py"
    if not p1b_foundation_authority_validator.is_file():
        errors.append("P1B foundation-authority adjudication validator is missing")
    else:
        completed = subprocess.run(
            [sys.executable, str(p1b_foundation_authority_validator)],
            cwd=ROOT.parent.parent,
            text=True,
            capture_output=True,
            check=False,
        )
        output = completed.stdout.strip()
        if completed.returncode != 0:
            errors.append("P1B foundation-authority adjudication corpus failed: " + (output or completed.stderr.strip()))
        elif output:
            adjudication_outputs.append(output)

    if not p2_owner_adjudication_validator.is_file():
        errors.append("P2 public-symbol owner-adjudication validator is missing")
    else:
        completed = subprocess.run(
            [sys.executable, str(p2_owner_adjudication_validator)],
            cwd=ROOT.parent.parent,
            text=True,
            capture_output=True,
            check=False,
        )
        output = completed.stdout.strip()
        if completed.returncode != 0:
            errors.append("P2 public-symbol owner-adjudication corpus failed: " + (output or completed.stderr.strip()))
        elif output:
            adjudication_outputs.append(output)

    p3_applicability_adjudication_validator = ROOT.parent / "domain_atlas/compiler/library_registry/contract_generation/semantic_decomposition/p3_applicability_adjudication/validate.py"
    if not p3_applicability_adjudication_validator.is_file():
        errors.append("P3 family-axis applicability-adjudication validator is missing")
    else:
        completed = subprocess.run(
            [sys.executable, str(p3_applicability_adjudication_validator)],
            cwd=ROOT.parent.parent,
            text=True,
            capture_output=True,
            check=False,
        )
        output = completed.stdout.strip()
        if completed.returncode != 0:
            errors.append("P3 family-axis applicability-adjudication corpus failed: " + (output or completed.stderr.strip()))
        elif output:
            adjudication_outputs.append(output)

    p4_ratification_ingestion_validator = ROOT.parent / "domain_atlas/compiler/library_registry/contract_generation/semantic_decomposition/p4_ratification_ingestion/validate.py"
    if not p4_ratification_ingestion_validator.is_file():
        errors.append("P4 ratification-ingestion validator is missing")
    else:
        completed = subprocess.run(
            [sys.executable, str(p4_ratification_ingestion_validator)],
            cwd=ROOT.parent.parent,
            text=True,
            capture_output=True,
            check=False,
        )
        output = completed.stdout.strip()
        if completed.returncode != 0:
            errors.append("P4 ratification-ingestion corpus failed: " + (output or completed.stderr.strip()))
        elif output:
            adjudication_outputs.append(output)

    p5_exact_contract_adjudication_validator = ROOT.parent / "domain_atlas/compiler/library_registry/contract_generation/semantic_decomposition/p5_exact_contract_adjudication/validate.py"
    if not p5_exact_contract_adjudication_validator.is_file():
        errors.append("P5 exact-contract adjudication validator is missing")
    else:
        completed = subprocess.run(
            [sys.executable, str(p5_exact_contract_adjudication_validator)],
            cwd=ROOT.parent.parent,
            text=True,
            capture_output=True,
            check=False,
        )
        output = completed.stdout.strip()
        if completed.returncode != 0:
            errors.append("P5 exact-contract adjudication corpus failed: " + (output or completed.stderr.strip()))
        elif output:
            adjudication_outputs.append(output)

    p6_implementation_qualification_validator = ROOT.parent / "domain_atlas/compiler/library_registry/contract_generation/semantic_decomposition/p6_implementation_qualification/validate.py"
    if not p6_implementation_qualification_validator.is_file():
        errors.append("P6 implementation-qualification validator is missing")
    else:
        completed = subprocess.run(
            [sys.executable, str(p6_implementation_qualification_validator)],
            cwd=ROOT.parent.parent,
            text=True,
            capture_output=True,
            check=False,
        )
        output = completed.stdout.strip()
        if completed.returncode != 0:
            errors.append("P6 implementation-qualification corpus failed: " + (output or completed.stderr.strip()))
        elif output:
            adjudication_outputs.append(output)

    p7_offer_binding_qualification_validator = ROOT.parent / "domain_atlas/compiler/library_registry/contract_generation/semantic_decomposition/p7_offer_binding_qualification/validate.py"
    if not p7_offer_binding_qualification_validator.is_file():
        errors.append("P7 offer-binding qualification validator is missing")
    else:
        completed = subprocess.run(
            [sys.executable, str(p7_offer_binding_qualification_validator)],
            cwd=ROOT.parent.parent,
            text=True,
            capture_output=True,
            check=False,
        )
        output = completed.stdout.strip()
        if completed.returncode != 0:
            errors.append("P7 offer-binding qualification corpus failed: " + (output or completed.stderr.strip()))
        elif output:
            adjudication_outputs.append(output)

    p8_vertical_acceptance_tensor_validator = ROOT.parent / "domain_atlas/compiler/library_registry/contract_generation/semantic_decomposition/p8_vertical_acceptance_tensor/validate.py"
    if not p8_vertical_acceptance_tensor_validator.is_file():
        errors.append("P8 vertical-acceptance tensor validator is missing")
    else:
        completed = subprocess.run(
            [sys.executable, str(p8_vertical_acceptance_tensor_validator)],
            cwd=ROOT.parent.parent,
            text=True,
            capture_output=True,
            check=False,
        )
        output = completed.stdout.strip()
        if completed.returncode != 0:
            errors.append("P8 vertical-acceptance tensor failed: " + (output or completed.stderr.strip()))
        elif output:
            adjudication_outputs.append(output)

    composition_validator = ROOT / "composition_pilots/deterministic_verticals/validate_corpus.py"
    if not composition_validator.is_file():
        errors.append("deterministic vertical-composition validator is missing")
    else:
        completed = subprocess.run(
            [sys.executable, str(composition_validator)],
            cwd=ROOT.parent.parent,
            text=True,
            capture_output=True,
            check=False,
        )
        output = completed.stdout.strip()
        if completed.returncode != 0:
            errors.append(
                "deterministic vertical composition failed: "
                + (output or completed.stderr.strip())
            )
        elif output:
            adjudication_outputs.append(output)

    inventory_challenges = {
        "analytical-operations inventory challenge": ROOT / "inventory_challenges/analytical_operations_gap_audit/validate.py",
        "presentation-experience inventory challenge": ROOT / "inventory_challenges/presentation_experience_gap_audit/validate.py",
        "presentation SOTA atlas upstream bridge": ROOT / "adjudications/consumption_experiences/presentation_semantics/bridge_validate.py",
        "quality/reconciliation split audit": ROOT / "inventory_challenges/quality_reconciliation_split_audit/validate.py",
        "upstream demand-surface sweep": ROOT / "upstream_demand_surface_sweep/validate.py",
        "solution-synthesis architecture": ROOT / "solution_synthesis_architecture/validate.py",
        "corpus build protocol": ROOT / "corpus_build_protocol/validate.py",
        "semantic fixed-point campaign": ROOT / "semantic_fixed_point_campaign/validate_fixed_point.py",
        "horizontal coverage-family research corpus": ROOT.parent / "analytics_landscape/product_families/validate.py",
        "corpus architecture router": ROOT / "corpus_architecture_router/validate.py",
    }
    for challenge_name, inventory_challenge_validator in inventory_challenges.items():
        if not inventory_challenge_validator.is_file():
            errors.append(f"{challenge_name} validator is missing")
            continue
        completed = subprocess.run(
            [sys.executable, str(inventory_challenge_validator)],
            cwd=ROOT.parent.parent,
            text=True,
            capture_output=True,
            check=False,
        )
        output = completed.stdout.strip()
        if completed.returncode != 0:
            errors.append(
                f"{challenge_name} failed: "
                + (output or completed.stderr.strip())
            )
        elif output:
            adjudication_outputs.append(output)

    closure_validator = ROOT / "closure_program/validate.py"
    if not closure_validator.is_file():
        errors.append("product-ontology closure-program validator is missing")
    else:
        completed = subprocess.run(
            [sys.executable, str(closure_validator)],
            cwd=ROOT.parent.parent,
            text=True,
            capture_output=True,
            check=False,
        )
        output = completed.stdout.strip()
        if completed.returncode != 0:
            errors.append(
                "product-ontology closure program failed: "
                + (output or completed.stderr.strip())
            )
        elif output:
            adjudication_outputs.append(output)

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    for output in adjudication_outputs:
        print(output)

    print(
        "PASS product-boundary pilot: "
        f"{len(nodes)} nodes, {len(products)} product candidates, {len(edges)} relations, "
        f"{len(evidence)} evidence records, {len(truth_items)} truth dimensions"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
