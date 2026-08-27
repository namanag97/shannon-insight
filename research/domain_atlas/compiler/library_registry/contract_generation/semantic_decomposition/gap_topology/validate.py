#!/usr/bin/env python3
"""Validate the semantic gap topology against the live canonical graph.

Cardinalities are deliberately derived from the upstream records. Adding a
family, library, symbol, or vertical obligation must expand the topology rather
than require a maintainer to bless a new magic number in this validator.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from build_gap_topology import (
    CONTRACT_GENERATION,
    HERE,
    METHOD_SIGNATURE_FIELDS,
    ONTOLOGY,
    SEM,
    build,
    outputs,
    schema,
)


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def assert_projection(summary: dict[str, Any], prefix: str, source: dict[str, Any], mapping: dict[str, str]) -> None:
    for target_key, source_key in mapping.items():
        assert summary[f"{prefix}{target_key}"] == source[source_key], (
            f"{prefix}{target_key}", summary[f"{prefix}{target_key}"], source[source_key]
        )


def main() -> int:
    # Checked-in projections must be the byte-for-byte deterministic result of
    # the current builders and their digest manifest must describe those bytes.
    for name, text in outputs().items():
        assert (HERE / name).is_file() and (HERE / name).read_text() == text, f"stale {name}"
    manifest = load_json(HERE / "manifest.json")
    for name, claim in manifest["files"].items():
        data = (HERE / name).read_bytes()
        assert len(data) == claim["bytes"] and hashlib.sha256(data).hexdigest() == claim["sha256"], name

    built = build()
    programs = built["programs"]
    clusters = built["clusters"]
    method_kernels = built["method_kernels"]
    bands = built["bands"]
    summary = built["summary"]
    lattice = built["lattice"]

    # Structural losslessness of programs, clusters, reusable closure methods,
    # and dependency bands.
    required = set(schema()["required"])
    program_ids = {row["program_id"] for row in programs}
    assert len(programs) == len(program_ids) == 8 and programs[0]["depends_on_program_refs"] == []
    assert all(set(row["depends_on_program_refs"]) <= program_ids for row in programs)
    assert all(set(row) == required for row in clusters)
    assert [row["execution_rank"] for row in clusters] == list(range(1, len(clusters) + 1))
    assert all(row["program_ref"] in program_ids and row["atom_count"] > 0 for row in clusters)
    assert all(row["canonical_gaps_closed"] == 0 and row["status"] == "OPEN_BATCHABLE_CLUSTER" for row in clusters)

    assert len(method_kernels) == 10
    kernel_members = [ref for row in method_kernels for ref in row["member_cluster_refs"]]
    assert len(kernel_members) == len(set(kernel_members)) == len(clusters)
    assert set(kernel_members) == {row["cluster_id"] for row in clusters}
    cluster_by_id = {row["cluster_id"]: row for row in clusters}
    for kernel in method_kernels:
        members = [cluster_by_id[ref] for ref in kernel["member_cluster_refs"]]
        assert kernel["member_cluster_count"] == len(members)
        assert kernel["represented_atom_count"] == sum(row["atom_count"] for row in members)
        assert all({field: row[field] for field in METHOD_SIGNATURE_FIELDS} == kernel["signature"] for row in members)
        assert not kernel["completion_claim"] and kernel["canonical_gaps_closed"] == 0
    assert sum(row["represented_atom_count"] for row in method_kernels) == sum(row["atom_count"] for row in clusters)

    assert len(ONTOLOGY["classification_axes"]) >= 15 and len(ONTOLOGY["non_collapse_laws"]) >= 7
    assert len(bands) == 10 and [row["order"] for row in bands] == list(range(1, 11))
    band_ids = {row["band_id"] for row in bands}
    assert all(set(row["depends_on_band_refs"]) <= band_ids for row in bands)
    scheduled = [ref for row in bands for ref in row["cluster_refs"]]
    assert len(scheduled) == len(set(scheduled)) == len(clusters)
    assert set(scheduled) == {row["cluster_id"] for row in clusters}
    assert all(not row["completion_claim"] and row["cluster_count"] > 0 for row in bands)
    assert len(lattice["levels"]) == 9

    # Current graph size comes from canonical records, never a validator constant.
    exact_inputs = load_jsonl(SEM / "structured_projection/exact-contract-input-candidates.jsonl")
    family_constitutions = load_jsonl(CONTRACT_GENERATION / "family-constitutions.jsonl")
    axes = load_json(SEM / "semantic-axis-ontology.json")["axes"]
    family_count = len(family_constitutions)
    library_count = len(exact_inputs)
    semantic_cell_count = library_count * len(axes)
    assert lattice["compression_metrics"]["library_contract_atoms"] == library_count
    assert summary["exact_contract_adjudication_dockets"] == library_count
    assert summary["exact_contract_lowering_gates"] == library_count
    assert summary["semantic_frontier_member_axis_cells"] == semantic_cell_count
    assert summary["semantic_decision_member_axis_cells_preserved"] == semantic_cell_count
    assert summary["family_axis_applicability_dockets"] == family_count * len(axes)
    assert summary["semantic_decision_family_axis_factorizations"] == family_count * len(axes)

    # Full coordinate ontologies route every exact library once. Targeted legacy
    # evidence tranches are intentionally allowed to cover subsets.
    full_coordinates = {
        "time_": "time_coordinate_ontology",
        "semantic_object_": "semantic_object_coordinate_ontology",
        "semantic_role_": "semantic_role_coordinate_ontology",
        "authority_trust_": "authority_trust_coordinate_ontology",
        "effect_boundary_": "effect_boundary_coordinate_ontology",
        "evidence_conformance_": "evidence_conformance_coordinate_ontology",
        "representation_": "representation_coordinate_ontology",
        "compatibility_evolution_": "compatibility_evolution_coordinate_ontology",
        "privacy_security_safety_": "privacy_security_safety_coordinate_ontology",
        "resources_failure_": "resources_failure_coordinate_ontology",
    }
    for prefix, directory in full_coordinates.items():
        coordinate = load_json(SEM / directory / "summary.json")
        assert coordinate["structural_family_dockets"] == family_count, directory
        assert coordinate["target_member_routes"] == library_count, directory
        assert summary[f"{prefix}structural_family_dockets"] == family_count, directory
        assert summary[f"{prefix}member_routes"] == library_count, directory

    # Exact projections of independently generated upstream adjudication stages.
    p1 = load_json(SEM / "p1_authority_symbols/summary.json")
    p2 = load_json(SEM / "p2_owner_adjudication/summary.json")
    p3 = load_json(SEM / "p3_applicability_adjudication/summary.json")
    p1b = load_json(SEM / "p1b_foundation_authority_adjudication/summary.json")
    p4 = load_json(SEM / "p4_ratification_ingestion/summary.json")
    p5 = load_json(SEM / "p5_exact_contract_adjudication/summary.json")
    p6 = load_json(SEM / "p6_implementation_qualification/summary.json")
    p7 = load_json(SEM / "p7_offer_binding_qualification/summary.json")
    p8 = load_json(SEM / "p8_vertical_acceptance_tensor/summary.json")

    assert_projection(summary, "symbol_", p2, {
        "owner_execution_units": "owner_decision_units",
        "owner_adjudication_dockets": "symbol_dockets",
        "occurrence_disposition_candidates": "represented_occurrences",
        "owner_decision_waves": "owner_decision_waves",
        "owner_proposals": "owner_proposals",
        "owner_proposals_with_named_candidates": "owner_proposals_with_named_candidates",
        "owner_proposals_blocked": "owner_proposals_blocked",
        "occurrence_relation_proposals": "occurrence_relation_proposals",
        "occurrence_relation_proposals_unresolved": "occurrence_relation_proposals_unresolved",
        "owner_proposal_conflicts": "proposal_conflicts",
        "owner_proposal_counterfactuals": "proposal_counterfactuals",
        "owner_proposal_counterfactual_instabilities": "counterfactually_unstable_owner_proposals",
        "owner_challenge_packages": "owner_adjudication_challenge_packages",
        "owner_ratification_packet_templates": "ratification_packet_templates",
        "owner_ratification_packet_templates_ready_for_review": "ratification_packet_templates_ready_for_authority_review",
    })
    assert summary["symbol_packets_with_bounded_primary_research"] == p1["total_symbol_packets_with_bounded_primary_research"]
    assert summary["symbol_packets_open_primary_research"] == p1["remaining_unresearched_symbol_packets"] == 0
    assert summary["symbol_packets_still_requiring_owner_adjudication"] == p1["total_owner_unratified_symbol_packets"]

    assert_projection(summary, "family_axis_applicability_", p3, {
        "dockets": "family_axis_dockets",
        "review_packages": "review_packages",
        "review_ready": "review_ready_dockets",
        "blocked": "blocked_dockets",
    })
    assert summary["foundation_authority_templates"] == p1b["ratification_packet_templates"]
    assert summary["foundation_authority_templates_ready_for_review"] == p1b["authority_review_ready_templates"]
    assert summary["foundation_authority_templates_blocked"] == p1b["blocked_templates"]
    assert summary["ratification_ingestion_templates"] == p4["total_templates"]
    assert summary["ratification_ingestion_verified"] == p4["verified_ratifications"] == 0
    assert summary["canonical_delta_candidates"] == p4["canonical_delta_candidates"] == 0
    assert summary["exact_contract_adjudication_dockets"] == p5["exact_contract_dockets"]
    assert summary["exact_contract_archetype_kernels"] == p5["archetype_obligation_kernels"]
    assert summary["exact_contract_family_kernels"] == p5["family_semantic_kernels"]
    assert summary["exact_contract_execution_packages"] == p5["execution_packages"]

    assert_projection(summary, "implementation_", p6, {
        "concrete_reference_resolutions": "concrete_reference_resolutions",
        "qualification_scope_kernels": "qualification_scope_kernels",
        "shared_qualification_scopes": "shared_qualification_scope_kernels",
        "independent_slots": "implementation_slots",
        "subject_dockets": "subject_dockets",
        "evidence_vacancy_packages": "evidence_vacancy_packages",
        "compiler_selection_gates": "selection_gates",
        "product_dockets": "product_qualification_dockets",
    })
    assert summary["implementation_qualification_profile_kernels"] == p7["qualification_profile_kernels"]
    assert summary["implementation_conformance_context_workstreams"] == p7["conformance_context_workstreams"]
    assert summary["implementation_represented_context_obligations"] == p7["represented_subject_context_occurrences"]
    assert summary["implementation_offer_intake_templates"] == p7["implementation_offer_intake_templates"]
    assert summary["semantic_physical_binding_gates"] == p7["semantic_physical_binding_gates"]
    assert summary["vertical_acceptance_slots"] == p8["unrelated_vertical_slots"]
    assert summary["vertical_acceptance_gate_classes"] == p8["acceptance_gate_classes"]
    assert summary["vertical_acceptance_slot_gate_obligations"] == p8["slot_gate_obligations"]
    assert summary["vertical_acceptance_products_with_structural_pilots"] == p8["products_with_any_structural_pilot"]
    assert summary["vertical_acceptance_products_with_two_structural_pilots"] == p8["products_with_two_unrelated_structural_pilots"]
    assert lattice["compression_metrics"]["product_evidence_vacancies"] == p6["represented_evidence_vacancies"]

    # Authority/evidence gates are fail-closed. Structural expansion must never
    # manufacture decisions, qualified offers, builds, or vertical acceptance.
    zero_gates = (
        "source_authorities_ratified", "ratification_ingestion_verified", "canonical_delta_candidates",
        "qualified_implementations", "selected_implementation_offers", "build_ready_products",
        "authorized_semantic_physical_bridges", "executed_vertical_acceptances",
        "ratified_symbol_owners", "ratified_symbol_occurrence_dispositions", "canonical_exact_gaps_closed",
    )
    assert all(summary[key] == 0 for key in zero_gates)
    assert summary["open_primary_research_archetypes"] == []
    assert sum(row["atom_count"] for row in clusters if row["gap_kind"] == "symbol-research-batch") == 0
    assert summary["product_gate_execution_units"] == p6["evidence_vacancy_packages"]
    assert summary["closure_method_kernels"] == len(method_kernels) == 10
    assert summary["represented_gap_atoms"] == sum(row["atom_count"] for row in clusters)
    assert not summary["completion_claim"]

    symbol_band = next(row for row in bands if row["band_id"] == "band.semantic-closure.02-symbols")
    assert len(symbol_band["parallel_lane_refs"]) == p2["owner_decision_waves"]
    assert all(ref.startswith("wave.p2.owner.") for ref in symbol_band["parallel_lane_refs"])

    print(
        f"PASS gap topology: {len(clusters)} attributable clusters factor losslessly into "
        f"{len(method_kernels)} closure-method kernels and cover {summary['represented_gap_atoms']} open atoms; "
        f"the live graph contains {family_count} families, {library_count} exact library candidates and "
        f"{semantic_cell_count} member-axis cells; all authority, implementation-selection and vertical "
        "acceptance gates remain fail-closed"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
