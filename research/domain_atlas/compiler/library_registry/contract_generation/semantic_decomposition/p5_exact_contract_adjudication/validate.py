#!/usr/bin/env python3
"""Validate the P5 exact-contract hypergraph and fail-closed lowering gates."""
from __future__ import annotations

import collections
import hashlib
import json

from build_p5 import (
    ARCHETYPES,
    BOUNDARY_CLUSTERS,
    CLOSURE_QUEUE,
    COLLISIONS,
    CONTRACT_DIMENSIONS,
    DEPENDENCY_EDGES,
    FAMILY_CONSTITUTIONS,
    HERE,
    INSTANCE_PROPOSALS,
    P1B_TEMPLATES,
    P2_OCCURRENCES,
    P2_TEMPLATES,
    P3_DOCKETS,
    P3_TEMPLATES,
    RATIFICATION_CONTRACT,
    RESEARCH_BATCHES,
    load_jsonl,
    outputs,
)


def main() -> int:
    expected = outputs()
    for name, text in expected.items():
        path = HERE / name
        assert path.is_file() and path.read_text() == text, f"stale {name}"
    manifest = json.loads((HERE / "manifest.json").read_text())
    assert manifest["completion_claim"] is False
    for name, claim in manifest["files"].items():
        data = (HERE / name).read_bytes()
        assert len(data) == claim["bytes"]
        assert hashlib.sha256(data).hexdigest() == claim["sha256"], name

    summary = json.loads((HERE / "summary.json").read_text())
    dockets = load_jsonl(HERE / "exact-contract-dockets.jsonl")
    archetype_kernels = load_jsonl(HERE / "archetype-obligation-kernels.jsonl")
    family_kernels = load_jsonl(HERE / "family-semantic-kernels.jsonl")
    packages = load_jsonl(HERE / "execution-packages.jsonl")
    templates = load_jsonl(HERE / "exact-contract-ratification-packet-templates.jsonl")
    gates = load_jsonl(HERE / "compiler-lowering-gates.jsonl")

    assert len(dockets) == summary["exact_contract_dockets"]
    assert len(archetype_kernels) == summary["archetype_obligation_kernels"] == 19
    assert summary["populated_archetype_obligation_kernels"] == 15
    assert len(family_kernels) == summary["family_semantic_kernels"]
    assert len(packages) == summary["execution_packages"]
    assert len(templates) == summary["ratification_packet_templates"] == len(dockets)
    assert len(gates) == summary["compiler_lowering_gates"] == len(dockets)
    assert summary["dockets_with_shared_symbol_dependencies"] == sum(bool(row["shared_symbol_occurrence_proposal_refs"]) for row in dockets)
    assert summary["dockets_with_collision_dependencies"] == sum(bool(row["cross_owner_collision_refs"]) for row in dockets)
    assert summary["verified_prerequisite_bindings"] == 0
    assert summary["ratified_exact_contracts"] == summary["lowered_exact_contract_candidates"] == 0
    assert summary["canonical_mutations_allowed"] == summary["canonical_exact_gaps_closed"] == 0
    assert not summary["completion_claim"]

    for claim in summary["input_snapshot"]["files"]:
        path = HERE.parents[6] / claim["path"]
        data = path.read_bytes()
        assert len(data) == claim["bytes"]
        assert hashlib.sha256(data).hexdigest() == claim["sha256"]
        assert len(load_jsonl(path)) == claim["record_count"]

    closures = {row["closure_id"]: row for row in load_jsonl(CLOSURE_QUEUE)}
    proposals = {row["proposal_id"]: row for row in load_jsonl(INSTANCE_PROPOSALS)}
    archetypes = {row["archetype_id"]: row for row in load_jsonl(ARCHETYPES)}
    families = {row["family_id"]: row for row in load_jsonl(FAMILY_CONSTITUTIONS)}
    batches = {row["batch_id"]: row for row in load_jsonl(RESEARCH_BATCHES)}
    p2_occurrences = {row["relation_proposal_id"]: row for row in load_jsonl(P2_OCCURRENCES)}
    p3_dockets = {row["docket_id"]: row for row in load_jsonl(P3_DOCKETS)}
    p1b_templates = {row["template_id"]: row for row in load_jsonl(P1B_TEMPLATES)}
    p2_templates = {row["ratification_packet_id"]: row for row in load_jsonl(P2_TEMPLATES)}
    p3_templates = {row["template_id"]: row for row in load_jsonl(P3_TEMPLATES)}
    all_prerequisite_templates = set(p1b_templates) | set(p2_templates) | set(p3_templates)
    expected_semantic_axes = {row["semantic_axis"] for row in p3_dockets.values()}
    assert len(expected_semantic_axes) == 16
    collisions = {row["collision_id"]: row for row in load_jsonl(COLLISIONS)}
    boundary_clusters = {row["cluster_id"]: row for row in load_jsonl(BOUNDARY_CLUSTERS)}
    dependency_edges = {row["edge_id"]: row for row in load_jsonl(DEPENDENCY_EDGES)}
    docket_by_id = {row["docket_id"]: row for row in dockets}
    docket_by_library = {row["library_ref"]: row for row in dockets}
    assert len(docket_by_id) == len(docket_by_library) == len(dockets)
    assert {row["closure_ref"] for row in dockets} == set(closures)
    assert {row["instance_proposal_ref"] for row in dockets} == set(proposals)
    assert all(row["contract_dimensions"] == CONTRACT_DIMENSIONS for row in dockets)

    all_p2_refs = [ref for row in dockets for ref in row["shared_symbol_occurrence_proposal_refs"]]
    assert len(all_p2_refs) == len(set(all_p2_refs)) == len(p2_occurrences)
    assert set(all_p2_refs) == set(p2_occurrences)
    all_p3_refs = [ref for row in dockets for ref in row["family_axis_docket_refs"]]
    assert len(all_p3_refs) == len(dockets) * 16
    assert set(all_p3_refs) == set(p3_dockets)
    assert collections.Counter(len(row["family_axis_docket_refs"]) for row in dockets) == {16: len(dockets)}
    assert collections.Counter(len(row["family_axis_ratification_template_refs"]) for row in dockets) == {16: len(dockets)}
    assert collections.Counter(row["boundary_disposition"] for row in dockets) == {"UNADJUDICATED": len(dockets)}
    assert collections.Counter(row["status"] for row in dockets) == {"BLOCKED_EXACT_CONTRACT_LOWERING": len(dockets)}

    for docket in dockets:
        closure = closures[docket["closure_ref"]]
        proposal = proposals[docket["instance_proposal_ref"]]
        assert closure["library_ref"] == proposal["library_ref"] == docket["library_ref"]
        assert proposal["family_id"] == docket["family_ref"]
        assert docket["primary_archetype_ref"] in archetypes
        assert docket["family_ref"] in families
        assert docket["research_batch_ref"] in batches
        boundary = boundary_clusters[docket["boundary_cluster_ref"]]
        assert docket["library_ref"] in boundary["library_refs"]
        assert all(
            docket["library_ref"] in {collisions[ref]["left_library_ref"], collisions[ref]["right_library_ref"]}
            for ref in docket["cross_owner_collision_refs"]
        )
        assert all(
            docket["library_ref"] in {dependency_edges[ref]["from_ref"], dependency_edges[ref]["to_ref"]}
            for ref in docket["dependency_edge_refs"]
        )
        assert all(p2_occurrences[ref]["library_ref"] == docket["library_ref"] for ref in docket["shared_symbol_occurrence_proposal_refs"])
        assert {p3_dockets[ref]["family_ref"] for ref in docket["family_axis_docket_refs"]} == {docket["family_ref"]}
        assert {p3_dockets[ref]["semantic_axis"] for ref in docket["family_axis_docket_refs"]} == expected_semantic_axes
        assert p1b_templates[docket["source_authority_ratification_template_ref"]]["template_kind"] == "P1B_SOURCE_AUTHORITY"
        assert p1b_templates[docket["source_authority_ratification_template_ref"]]["subject_ref"] == docket["family_ref"]
        assert p1b_templates[docket["boundary_ratification_template_ref"]]["template_kind"] == "P1B_BOUNDED_CONTEXT_BOUNDARY"
        assert p1b_templates[docket["boundary_ratification_template_ref"]]["subject_ref"] == docket["boundary_cluster_ref"]
        assert p1b_templates[docket["family_constitution_ratification_template_ref"]]["template_kind"] == "P1B_FAMILY_CONSTITUTION"
        assert p1b_templates[docket["family_constitution_ratification_template_ref"]]["subject_ref"] == docket["family_ref"]
        assert {
            p1b_templates[ref]["subject_ref"] for ref in docket["cross_owner_collision_ratification_template_refs"]
        } == set(docket["cross_owner_collision_refs"])
        assert len(docket["required_prerequisite_template_refs"]) == 19 + len(docket["shared_symbol_ratification_template_refs"]) + len(docket["cross_owner_collision_refs"])
        assert len(docket["required_prerequisite_template_refs"]) == len(set(docket["required_prerequisite_template_refs"]))
        assert set(docket["required_prerequisite_template_refs"]) <= all_prerequisite_templates
        assert not docket["structural_draft_is_canonical"]
        assert docket["selected_exact_contract_ref"] is None and docket["ratification_receipt_ref"] is None
        assert not docket["canonical_mutation_allowed"] and docket["canonical_gaps_closed"] == 0
        assert not docket["completion_claim"]
        assert {
            "SOURCE_AUTHORITY_UNRATIFIED", "BOUNDARY_DISPOSITION_UNRATIFIED",
            "FAMILY_CONSTITUTION_INCOMPLETE", "FAMILY_AXIS_APPLICABILITY_UNRATIFIED",
            "OWNER_AUTHORED_CONTRACT_DIMENSIONS_INCOMPLETE", "EXACT_SOURCE_CONTRACT_UNPUBLISHED",
        } <= set(docket["blocker_kinds"])
        assert docket["verified_prerequisite_template_refs"] == []

    archetype_member_refs = [ref for row in archetype_kernels for ref in row["docket_refs"]]
    assert len(archetype_member_refs) == len(set(archetype_member_refs)) == len(dockets)
    assert set(archetype_member_refs) == set(docket_by_id)
    assert {row["archetype_ref"] for row in archetype_kernels} == set(archetypes)
    for kernel in archetype_kernels:
        archetype = archetypes[kernel["archetype_ref"]]
        assert kernel["member_count"] == len(kernel["docket_refs"])
        assert all(docket_by_id[ref]["primary_archetype_ref"] == kernel["archetype_ref"] for ref in kernel["docket_refs"])
        assert kernel["required_type_roles"] == archetype["required_type_roles"]
        assert kernel["required_operation_roles"] == archetype["required_operation_roles"]

    family_member_refs = [ref for row in family_kernels for ref in row["docket_refs"]]
    assert len(family_member_refs) == len(set(family_member_refs)) == len(dockets)
    assert set(family_member_refs) == set(docket_by_id)
    assert {row["family_ref"] for row in family_kernels} == set(families)
    assert sum(row["member_count"] for row in family_kernels) == len(dockets)
    assert all(len(row["family_axis_docket_refs"]) == 16 for row in family_kernels)

    package_member_refs = [ref for row in packages for ref in row["docket_refs"]]
    assert len(package_member_refs) == len(set(package_member_refs)) == len(dockets)
    assert set(package_member_refs) == set(docket_by_id)
    assert {row["research_batch_ref"] for row in packages} == set(batches)
    assert sum(row["docket_count"] for row in packages) == len(dockets)

    template_by_docket = {row["docket_ref"]: row for row in templates}
    gate_by_docket = {row["docket_ref"]: row for row in gates}
    assert len(template_by_docket) == len(gate_by_docket) == len(dockets)
    assert set(template_by_docket) == set(gate_by_docket) == set(docket_by_id)
    for docket_id, docket in docket_by_id.items():
        template = template_by_docket[docket_id]
        gate = gate_by_docket[docket_id]
        expected_prerequisites = docket["required_prerequisite_template_refs"]
        assert template["required_prerequisite_template_refs"] == expected_prerequisites
        assert template["required_receipt_fields"] == RATIFICATION_CONTRACT["required_receipt_fields"]
        assert all(value is None for value in template["submission"].values())
        assert template["ratification_receipt_ref"] is None and template["ratification_required"]
        assert template["status"] == "BLOCKED_BY_UNRATIFIED_PREREQUISITES"
        assert gate["required_prerequisite_template_refs"] == expected_prerequisites
        assert gate["verified_prerequisite_template_refs"] == []
        assert gate["unresolved_blocker_kinds"] == docket["blocker_kinds"]
        assert gate["selected_exact_contract_ref"] is None and gate["lowered_contract_candidate_ref"] is None
        assert gate["status"] == "REFUSE_EXACT_CONTRACT_LOWERING"
        assert not template["canonical_mutation_allowed"] and not gate["canonical_mutation_allowed"]
        assert template["canonical_gaps_closed"] == gate["canonical_gaps_closed"] == 0
        assert not template["completion_claim"] and not gate["completion_claim"]

    print(f"PASS P5 exact-contract adjudication: {len(dockets)} exact dockets wire losslessly into {len(archetype_kernels)} archetype, {len(family_kernels)} family and {len(packages)} execution quotients; all {len(all_p3_refs)} axis and {len(all_p2_refs)} symbol-occurrence dependencies remain explicit; {len(gates)} lowering gates refuse with 0 ratified or canonical contracts")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
