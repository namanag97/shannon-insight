#!/usr/bin/env python3
"""Validate the semantic gap topology and its dependency order."""
from __future__ import annotations

import hashlib
import json

from build_gap_topology import HERE, METHOD_SIGNATURE_FIELDS, ONTOLOGY, build, outputs, schema


def main() -> int:
    for name, text in outputs().items():
        assert (HERE / name).is_file() and (HERE / name).read_text() == text, f"stale {name}"
    manifest = json.loads((HERE / "manifest.json").read_text())
    for name, claim in manifest["files"].items():
        data = (HERE / name).read_bytes()
        assert len(data) == claim["bytes"] and hashlib.sha256(data).hexdigest() == claim["sha256"], name
    built = build(); programs = built["programs"]; clusters = built["clusters"]; method_kernels = built["method_kernels"]; bands = built["bands"]
    p6 = json.loads((HERE.parent / "p6_implementation_qualification/summary.json").read_text())
    p7 = json.loads((HERE.parent / "p7_offer_binding_qualification/summary.json").read_text())
    p8 = json.loads((HERE.parent / "p8_vertical_acceptance_tensor/summary.json").read_text())
    required = set(schema()["required"]); program_ids = {row["program_id"] for row in programs}
    assert len(programs) == len(program_ids) == 8 and programs[0]["depends_on_program_refs"] == []
    assert all(set(row["depends_on_program_refs"]) <= program_ids for row in programs)
    assert all(set(row) == required for row in clusters)
    assert [row["execution_rank"] for row in clusters] == list(range(1, len(clusters) + 1))
    assert all(row["program_ref"] in program_ids and row["atom_count"] > 0 and row["canonical_gaps_closed"] == 0 for row in clusters)
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
    assert len(built["lattice"]["levels"]) == 9
    assert built["lattice"]["compression_metrics"]["library_contract_atoms"] == 674
    assert built["lattice"]["compression_metrics"]["product_evidence_vacancies"] == p6["represented_evidence_vacancies"]
    assert built["summary"]["symbol_owner_execution_units"] == 108
    assert built["summary"]["symbol_research_coordination_programs"] == 17
    assert built["summary"]["symbol_research_coordination_lanes"] == 36
    assert built["summary"]["archetype_semantic_axis_research_lanes"] == 157
    assert built["summary"]["symbol_packets_with_bounded_primary_research"] == 210
    assert built["summary"]["symbol_packets_open_primary_research"] == 0
    assert built["summary"]["symbol_packets_still_requiring_owner_adjudication"] == 210
    assert built["summary"]["symbol_owner_adjudication_dockets"] == 210
    assert built["summary"]["symbol_occurrence_disposition_candidates"] == 666
    assert built["summary"]["symbol_owner_decision_waves"] == 4
    assert built["summary"]["symbol_owner_proposals"] == 210
    assert built["summary"]["symbol_owner_proposals_with_named_candidates"] == 116
    assert built["summary"]["symbol_owner_proposals_blocked"] == 94
    assert built["summary"]["symbol_occurrence_relation_proposals"] == 666
    assert built["summary"]["symbol_occurrence_relation_proposals_unresolved"] == 345
    assert built["summary"]["symbol_owner_proposal_conflicts"] == 118
    assert built["summary"]["symbol_owner_proposal_counterfactuals"] == 210
    assert built["summary"]["symbol_owner_proposal_counterfactual_instabilities"] == 15
    assert built["summary"]["symbol_owner_challenge_packages"] == 29
    assert built["summary"]["symbol_owner_ratification_packet_templates"] == 210
    assert built["summary"]["symbol_owner_ratification_packet_templates_ready_for_review"] == 92
    assert built["summary"]["family_axis_applicability_dockets"] == 368
    assert built["summary"]["family_axis_applicability_review_packages"] == 33
    assert built["summary"]["family_axis_applicability_review_ready"] == 258
    assert built["summary"]["family_axis_applicability_blocked"] == 110
    assert built["summary"]["grain_cardinality_evidence_candidates"] == 23
    assert built["summary"]["grain_cardinality_evidence_dockets"] == 23
    assert built["summary"]["grain_cardinality_evidence_represented_library_occurrences"] == 638
    assert built["summary"]["grain_coordinate_transformation_kernels"] == 24
    assert built["summary"]["grain_coordinate_member_routes"] == 638
    assert built["summary"]["grain_coordinate_research_clusters"] == 78
    assert built["summary"]["grain_coordinate_operation_profiles_supplied"] == 0
    assert built["summary"]["state_change_evidence_candidates"] == 23
    assert built["summary"]["state_change_evidence_dockets"] == 23
    assert built["summary"]["state_change_evidence_represented_library_occurrences"] == 629
    assert built["summary"]["state_change_subject_archetypes"] == 12
    assert built["summary"]["state_change_transition_kernels"] == 31
    assert built["summary"]["state_change_member_routes"] == 629
    assert built["summary"]["state_change_research_clusters"] == 58
    assert built["summary"]["state_change_subject_profiles_supplied"] == 0
    assert built["summary"]["order_topology_evidence_candidates"] == 23
    assert built["summary"]["order_topology_evidence_dockets"] == 23
    assert built["summary"]["order_topology_evidence_represented_library_occurrences"] == 623
    assert built["summary"]["order_topology_relation_archetypes"] == 20
    assert built["summary"]["order_topology_relation_kernels"] == 32
    assert built["summary"]["order_topology_member_routes"] == 623
    assert built["summary"]["order_topology_research_clusters"] == 58
    assert built["summary"]["order_topology_relation_profiles_supplied"] == 0
    assert built["summary"]["composition_algebra_evidence_candidates"] == 22
    assert built["summary"]["composition_algebra_evidence_dockets"] == 22
    assert built["summary"]["composition_algebra_evidence_represented_library_occurrences"] == 619
    assert built["summary"]["composition_algebra_operator_archetypes"] == 28
    assert built["summary"]["composition_algebra_operator_kernels"] == 41
    assert built["summary"]["composition_algebra_member_routes"] == 619
    assert built["summary"]["composition_algebra_research_clusters"] == 76
    assert built["summary"]["composition_algebra_operator_profiles_supplied"] == 0
    assert built["summary"]["identity_equality_evidence_candidates"] == 7
    assert built["summary"]["identity_equality_evidence_dockets"] == 7
    assert built["summary"]["identity_equality_evidence_represented_library_occurrences"] == 223
    assert built["summary"]["identity_equality_bearer_archetypes"] == 24
    assert built["summary"]["identity_equality_kernels"] == 42
    assert built["summary"]["identity_equality_member_routes"] == 223
    assert built["summary"]["identity_equality_research_clusters"] == 24
    assert built["summary"]["identity_equality_relation_profiles_supplied"] == 0
    assert built["summary"]["partiality_uncertainty_evidence_candidates"] == 5
    assert built["summary"]["partiality_uncertainty_evidence_dockets"] == 5
    assert built["summary"]["partiality_uncertainty_evidence_represented_library_occurrences"] == 73
    assert built["summary"]["partiality_uncertainty_bearer_archetypes"] == 20
    assert built["summary"]["partiality_uncertainty_kernels"] == 42
    assert built["summary"]["partiality_uncertainty_member_routes"] == 73
    assert built["summary"]["partiality_uncertainty_research_clusters"] == 6
    assert built["summary"]["partiality_uncertainty_profiles_supplied"] == 0
    assert built["summary"]["time_temporal_bearer_archetypes"] == 25
    assert built["summary"]["time_temporal_operation_kernels"] == 48
    assert built["summary"]["time_structural_family_dockets"] == 23
    assert built["summary"]["time_member_routes"] == 674
    assert built["summary"]["time_research_clusters"] == 52
    assert built["summary"]["time_family_source_evidence_bindings_supplied"] == 0
    assert built["summary"]["time_coordinate_profiles_supplied"] == 0
    assert built["summary"]["semantic_object_bearer_archetypes"] == 33
    assert built["summary"]["semantic_object_operation_kernels"] == 55
    assert built["summary"]["semantic_object_structural_family_dockets"] == 23
    assert built["summary"]["semantic_object_member_routes"] == 674
    assert built["summary"]["semantic_object_research_clusters"] == 186
    assert built["summary"]["semantic_object_family_source_evidence_bindings_supplied"] == 0
    assert built["summary"]["semantic_object_coordinate_profiles_supplied"] == 0
    assert built["summary"]["semantic_role_archetypes"] == 46
    assert built["summary"]["semantic_role_operation_kernels"] == 54
    assert built["summary"]["semantic_role_structural_family_dockets"] == 23
    assert built["summary"]["semantic_role_member_routes"] == 674
    assert built["summary"]["semantic_role_research_clusters"] == 201
    assert built["summary"]["semantic_role_family_source_evidence_bindings_supplied"] == 0
    assert built["summary"]["semantic_role_coordinate_profiles_supplied"] == 0
    assert built["summary"]["authority_trust_bearer_archetypes"] == 44
    assert built["summary"]["authority_trust_operation_kernels"] == 55
    assert built["summary"]["authority_trust_structural_family_dockets"] == 23
    assert built["summary"]["authority_trust_member_routes"] == 674
    assert built["summary"]["authority_trust_research_clusters"] == 38
    assert built["summary"]["authority_trust_family_source_evidence_bindings_supplied"] == 0
    assert built["summary"]["authority_trust_coordinate_profiles_supplied"] == 0
    assert built["summary"]["effect_boundary_bearer_archetypes"] == 42
    assert built["summary"]["effect_boundary_operation_kernels"] == 60
    assert built["summary"]["effect_boundary_structural_family_dockets"] == 23
    assert built["summary"]["effect_boundary_member_routes"] == 674
    assert built["summary"]["effect_boundary_research_clusters"] == 53
    assert built["summary"]["effect_boundary_family_source_evidence_bindings_supplied"] == 0
    assert built["summary"]["effect_boundary_coordinate_profiles_supplied"] == 0
    assert built["summary"]["evidence_conformance_bearer_archetypes"] == 44
    assert built["summary"]["evidence_conformance_operation_kernels"] == 59
    assert built["summary"]["evidence_conformance_structural_family_dockets"] == 23
    assert built["summary"]["evidence_conformance_member_routes"] == 674
    assert built["summary"]["evidence_conformance_research_clusters"] == 69
    assert built["summary"]["evidence_conformance_family_source_evidence_bindings_supplied"] == 0
    assert built["summary"]["evidence_conformance_coordinate_profiles_supplied"] == 0
    assert built["summary"]["representation_bearer_archetypes"] == 48
    assert built["summary"]["representation_operation_kernels"] == 60
    assert built["summary"]["representation_structural_family_dockets"] == 23
    assert built["summary"]["representation_member_routes"] == 674
    assert built["summary"]["representation_research_clusters"] == 90
    assert built["summary"]["representation_family_source_evidence_bindings_supplied"] == 0
    assert built["summary"]["representation_directional_preservation_profiles_supplied"] == 0
    assert built["summary"]["compatibility_evolution_bearer_archetypes"] == 50
    assert built["summary"]["compatibility_evolution_operation_kernels"] == 72
    assert built["summary"]["compatibility_evolution_structural_family_dockets"] == 23
    assert built["summary"]["compatibility_evolution_member_routes"] == 674
    assert built["summary"]["compatibility_evolution_research_clusters"] == 40
    assert built["summary"]["compatibility_evolution_family_source_evidence_bindings_supplied"] == 0
    assert built["summary"]["compatibility_evolution_directional_vectors_supplied"] == 0
    assert built["summary"]["compatibility_evolution_change_lifecycle_profiles_supplied"] == 0
    assert built["summary"]["privacy_security_safety_bearer_archetypes"] == 60
    assert built["summary"]["privacy_security_safety_operation_kernels"] == 80
    assert built["summary"]["privacy_security_safety_structural_family_dockets"] == 23
    assert built["summary"]["privacy_security_safety_member_routes"] == 674
    assert built["summary"]["privacy_security_safety_research_clusters"] == 60
    assert built["summary"]["privacy_security_safety_family_source_evidence_bindings_supplied"] == 0
    assert built["summary"]["privacy_profiles_supplied"] == 0
    assert built["summary"]["security_profiles_supplied"] == 0
    assert built["summary"]["safety_profiles_supplied"] == 0
    assert built["summary"]["resources_failure_bearer_archetypes"] == 55
    assert built["summary"]["resources_failure_operation_kernels"] == 80
    assert built["summary"]["resources_failure_structural_family_dockets"] == 23
    assert built["summary"]["resources_failure_member_routes"] == 674
    assert built["summary"]["resources_failure_research_clusters"] == 61
    assert built["summary"]["resources_failure_family_source_evidence_bindings_supplied"] == 0
    assert built["summary"]["finite_resource_profiles_supplied"] == 0
    assert built["summary"]["total_failure_profiles_supplied"] == 0
    assert built["summary"]["targeted_evidence_axes"] == 6
    assert built["summary"]["targeted_evidence_work_packages"] == 103
    assert built["summary"]["targeted_evidence_library_occurrences"] == 2805
    assert built["summary"]["targeted_evidence_unrouted_axes"] == 0
    assert built["summary"]["targeted_evidence_unrouted_work_packages"] == 0
    assert built["summary"]["semantic_frontier_axes"] == 16
    assert built["summary"]["semantic_frontier_lanes"] == 3
    assert built["summary"]["semantic_frontier_member_axis_cells"] == 10784
    assert built["summary"]["semantic_frontier_review_ready_dockets"] == 258
    assert built["summary"]["semantic_frontier_blocked_dockets"] == 110
    assert built["summary"]["semantic_decision_bearer_archetypes"] == 10
    assert built["summary"]["semantic_decision_axis_profiles"] == 16
    assert built["summary"]["semantic_decision_family_axis_factorizations"] == 368
    assert built["summary"]["semantic_decision_member_axis_cells_preserved"] == 10784
    assert built["summary"]["semantic_decision_coordinate_refined_axes"] == 16
    assert built["summary"]["semantic_decision_coordinate_refined_target_member_routes"] == 9545
    assert built["summary"]["foundation_authority_templates"] == 652
    assert built["summary"]["foundation_authority_templates_ready_for_review"] == 527
    assert built["summary"]["foundation_authority_templates_blocked"] == 125
    assert built["summary"]["ratification_ingestion_templates"] == 1904
    assert built["summary"]["ratification_ingestion_verified"] == 0
    assert built["summary"]["canonical_delta_candidates"] == 0
    assert built["summary"]["exact_contract_adjudication_dockets"] == 674
    assert built["summary"]["exact_contract_archetype_kernels"] == 19
    assert built["summary"]["exact_contract_family_kernels"] == 23
    assert built["summary"]["exact_contract_execution_packages"] == 57
    assert built["summary"]["exact_contract_lowering_gates"] == 674
    assert built["summary"]["implementation_concrete_reference_resolutions"] == p6["concrete_reference_resolutions"]
    assert built["summary"]["implementation_qualification_scope_kernels"] == p6["qualification_scope_kernels"]
    assert built["summary"]["implementation_shared_qualification_scopes"] == p6["shared_qualification_scope_kernels"]
    assert built["summary"]["implementation_independent_slots"] == p6["implementation_slots"]
    assert built["summary"]["implementation_subject_dockets"] == p6["subject_dockets"]
    assert built["summary"]["implementation_evidence_vacancy_packages"] == p6["evidence_vacancy_packages"]
    assert built["summary"]["implementation_compiler_selection_gates"] == p6["selection_gates"]
    assert built["summary"]["implementation_product_dockets"] == p6["product_qualification_dockets"]
    assert built["summary"]["qualified_implementations"] == 0
    assert built["summary"]["selected_implementation_offers"] == 0
    assert built["summary"]["build_ready_products"] == 0
    assert built["summary"]["implementation_qualification_profile_kernels"] == p7["qualification_profile_kernels"]
    assert built["summary"]["implementation_conformance_context_workstreams"] == p7["conformance_context_workstreams"]
    assert built["summary"]["implementation_represented_context_obligations"] == p7["represented_subject_context_occurrences"]
    assert built["summary"]["implementation_offer_intake_templates"] == p7["implementation_offer_intake_templates"]
    assert built["summary"]["semantic_physical_binding_gates"] == p7["semantic_physical_binding_gates"]
    assert built["summary"]["authorized_semantic_physical_bridges"] == 0
    assert built["summary"]["vertical_acceptance_slots"] == p8["unrelated_vertical_slots"]
    assert built["summary"]["vertical_acceptance_gate_classes"] == p8["acceptance_gate_classes"]
    assert built["summary"]["vertical_acceptance_slot_gate_obligations"] == p8["slot_gate_obligations"]
    assert built["summary"]["vertical_acceptance_products_with_structural_pilots"] == p8["products_with_any_structural_pilot"]
    assert built["summary"]["vertical_acceptance_products_with_two_structural_pilots"] == p8["products_with_two_unrelated_structural_pilots"]
    assert built["summary"]["executed_vertical_acceptances"] == 0
    assert built["summary"]["ratified_symbol_owners"] == 0
    assert built["summary"]["ratified_symbol_occurrence_dispositions"] == 0
    assert set(built["summary"]["open_primary_research_archetypes"]) == set()
    assert sum(row["atom_count"] for row in clusters if row["gap_kind"] == "symbol-research-batch") == 0
    assert sum(row["atom_count"] for row in clusters if row["gap_kind"] == "symbol-owner-adjudication-batch") == 191
    assert built["summary"]["product_gate_execution_units"] == p6["evidence_vacancy_packages"]
    assert built["summary"]["closure_method_kernels"] == 10
    symbol_band = next(row for row in bands if row["band_id"] == "band.semantic-closure.02-symbols")
    assert len(symbol_band["parallel_lane_refs"]) == 4
    assert all(ref.startswith("wave.p2.owner.") for ref in symbol_band["parallel_lane_refs"])
    assert built["summary"]["represented_gap_atoms"] == sum(row["atom_count"] for row in clusters)
    assert built["summary"]["completion_claim"] is False and built["summary"]["canonical_exact_gaps_closed"] == 0
    print(f"PASS gap topology: {len(clusters)} attributable clusters factor losslessly into {len(method_kernels)} closure-method kernels and cover {built['summary']['represented_gap_atoms']} open atoms in 10 dependency bands; contract work joins {p7['qualification_profile_kernels']} qualification profiles/{p7['conformance_context_workstreams']} conformance workstreams and {p8['slot_gate_obligations']} vertical obligations join {p8['acceptance_gate_classes']} acceptance workstreams; all bindings and acceptances refuse; zero gaps falsely closed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
