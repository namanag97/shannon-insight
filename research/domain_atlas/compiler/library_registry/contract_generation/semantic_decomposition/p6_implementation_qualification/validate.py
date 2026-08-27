#!/usr/bin/env python3
"""Validate the P6 implementation-qualification hypergraph and refusal gates."""
from __future__ import annotations

import collections
import hashlib
import json

from build_p6 import (
    CONTRIBUTIONS,
    GATE_DEFINITIONS,
    GATE_DEPENDENCIES,
    HERE,
    P5_TEMPLATES,
    PRODUCT_PROGRAMS,
    RESOLUTION_CLASSES,
    SUBJECTS,
    VACANCIES,
    VERTICAL_PROGRAMS,
    load_jsonl,
    outputs,
    scope_signature,
)


def main() -> int:
    for name, text in outputs().items():
        path = HERE / name
        assert path.is_file() and path.read_text() == text, f"stale {name}"

    manifest = json.loads((HERE / "manifest.json").read_text())
    assert manifest["completion_claim"] is False
    for name, claim in manifest["files"].items():
        data = (HERE / name).read_bytes()
        assert len(data) == claim["bytes"]
        assert hashlib.sha256(data).hexdigest() == claim["sha256"], name

    summary = json.loads((HERE / "summary.json").read_text())
    resolutions = load_jsonl(HERE / "concrete-reference-resolutions.jsonl")
    scopes = load_jsonl(HERE / "qualification-scope-kernels.jsonl")
    dockets = load_jsonl(HERE / "subject-dockets.jsonl")
    packages = load_jsonl(HERE / "evidence-vacancy-packages.jsonl")
    gate_kernels = load_jsonl(HERE / "gate-execution-kernels.jsonl")
    selections = load_jsonl(HERE / "compiler-selection-gates.jsonl")
    products = load_jsonl(HERE / "product-qualification-dockets.jsonl")

    assert len(resolutions) == summary["concrete_reference_resolutions"]
    assert set(summary["resolution_counts"]) == set(RESOLUTION_CLASSES)
    assert len(scopes) == summary["qualification_scope_kernels"]
    assert sum(row["subject_count"] > 1 for row in scopes) == summary["shared_qualification_scope_kernels"]
    assert sum(len(row["implementation_slot_refs"]) for row in scopes) == summary["implementation_slots"] == 2 * len(scopes)
    assert len(dockets) == summary["subject_dockets"]
    assert len(packages) == summary["evidence_vacancy_packages"]
    assert sum(row["vacancy_count"] for row in packages) == summary["represented_evidence_vacancies"]
    assert len(gate_kernels) == summary["gate_execution_kernels"] == 16
    assert len(selections) == summary["selection_gates"]
    assert len(products) == summary["product_qualification_dockets"]
    for field in (
        "qualified_implementations",
        "portable_offers",
        "selected_implementation_offers",
        "build_ready_products",
    ):
        assert summary[field] == 0
    assert not summary["completion_claim"]

    for claim in summary["input_snapshot"]["files"]:
        path = HERE.parents[6] / claim["path"]
        data = path.read_bytes()
        assert len(data) == claim["bytes"]
        assert hashlib.sha256(data).hexdigest() == claim["sha256"]
        assert len(load_jsonl(path)) == claim["record_count"]

    source_subjects = {row["subject_id"]: row for row in load_jsonl(SUBJECTS)}
    source_vacancies = {row["vacancy_id"]: row for row in load_jsonl(VACANCIES)}
    source_gates = {row["gate_id"]: row for row in load_jsonl(GATE_DEFINITIONS)}
    source_edges = {row["edge_id"]: row for row in load_jsonl(GATE_DEPENDENCIES)}
    source_programs = {row["candidate_id"]: row for row in load_jsonl(PRODUCT_PROGRAMS)}
    source_verticals = {row["candidate_id"]: row for row in load_jsonl(VERTICAL_PROGRAMS)}
    contributions = {row["library_id"]: row for row in load_jsonl(CONTRIBUTIONS)}
    p5_by_library = {row["library_ref"]: row for row in load_jsonl(P5_TEMPLATES)}

    assert len(source_subjects) == len(dockets)
    assert len(source_gates) == 16 and len(source_edges) == 17
    assert set(source_programs) == set(source_verticals)

    expected_concrete_refs = {
        ref
        for subject in source_subjects.values()
        for ref in subject["compiler_projection"]["concrete_library_refs"]
    }
    resolution_by_ref = {row["concrete_library_ref"]: row for row in resolutions}
    resolution_by_id = {row["resolution_id"]: row for row in resolutions}
    assert len(resolution_by_ref) == len(resolution_by_id) == len(resolutions)
    assert set(resolution_by_ref) == expected_concrete_refs
    assert collections.Counter(row["resolution_class"] for row in resolutions) == {
        key: summary["resolution_counts"][key] for key in RESOLUTION_CLASSES
    }
    for ref, resolution in resolution_by_ref.items():
        contribution = contributions.get(ref)
        if ref in p5_by_library:
            expected_class = "P5_OPEN_EXACT_CONTRACT"
            assert resolution["p5_exact_contract_template_ref"] == p5_by_library[ref]["template_id"]
        elif contribution and contribution["status"] == "specified_unimplemented":
            expected_class = "REGISTERED_SPECIFIED_UNIMPLEMENTED"
        elif contribution:
            expected_class = "REGISTERED_CANDIDATE_UNADJUDICATED"
        else:
            expected_class = "UNREGISTERED_CONCRETE_REFERENCE"
        assert resolution["resolution_class"] == expected_class
        assert resolution["selected_exact_contract_ref"] is None
        assert resolution["qualified_implementation_refs"] == []
        assert resolution["status"] == "BLOCKED_NO_QUALIFIED_IMPLEMENTATION"
        assert not resolution["completion_claim"]

    scope_by_id = {row["scope_id"]: row for row in scopes}
    assert len(scope_by_id) == len(scopes)
    all_scope_members = [ref for row in scopes for ref in row["subject_refs"]]
    assert len(all_scope_members) == len(set(all_scope_members)) == len(source_subjects)
    assert set(all_scope_members) == set(source_subjects)
    all_slots = [ref for row in scopes for ref in row["implementation_slot_refs"]]
    assert len(all_slots) == len(set(all_slots)) == 2 * len(scopes)
    for scope in scopes:
        assert scope["subject_count"] == len(scope["subject_refs"])
        assert scope["required_independent_implementation_slots"] == 2
        assert len(scope["implementation_slot_refs"]) == 2
        assert scope["qualified_implementation_refs"] == [] and not scope["portable_offer"]
        signatures = {json.dumps(scope_signature(source_subjects[ref]), sort_keys=True) for ref in scope["subject_refs"]}
        assert len(signatures) == 1
        assert not scope["completion_claim"]

    docket_by_subject = {row["subject_ref"]: row for row in dockets}
    docket_by_id = {row["docket_id"]: row for row in dockets}
    assert len(docket_by_subject) == len(docket_by_id) == len(source_subjects)
    assert set(docket_by_subject) == set(source_subjects)
    vacancies_by_candidate: dict[str, set[str]] = collections.defaultdict(set)
    for vacancy in source_vacancies.values():
        vacancies_by_candidate[vacancy["candidate_id"]].add(vacancy["vacancy_id"])
    for subject_ref, docket in docket_by_subject.items():
        subject = source_subjects[subject_ref]
        scope = scope_by_id[docket["qualification_scope_ref"]]
        expected_refs = set(subject["compiler_projection"]["concrete_library_refs"])
        local_resolutions = [resolution_by_id[ref] for ref in docket["concrete_reference_resolution_refs"]]
        assert {row["concrete_library_ref"] for row in local_resolutions} == expected_refs
        assert set(docket["resolution_classes"]) == {row["resolution_class"] for row in local_resolutions}
        assert subject_ref in scope["subject_refs"]
        assert docket["implementation_slot_refs"] == scope["implementation_slot_refs"]
        assert docket["candidate_ref"] == subject["candidate_id"]
        assert docket["product_ref"] == subject["product_ref"]
        assert set(docket["evidence_vacancy_refs"]) == vacancies_by_candidate[subject["candidate_id"]]
        assert docket["qualified_implementation_refs"] == []
        assert docket["status"] == "BLOCKED_IMPLEMENTATION_QUALIFICATION"
        assert not docket["completion_claim"]

    package_by_gate = {row["gate_ref"]: row for row in packages}
    assert len(package_by_gate) == len(packages)
    packaged_vacancies = [ref for row in packages for ref in row["vacancy_refs"]]
    assert len(packaged_vacancies) == len(set(packaged_vacancies)) == len(source_vacancies)
    assert set(packaged_vacancies) == set(source_vacancies)
    for gate_ref, package in package_by_gate.items():
        gate = source_gates[gate_ref]
        expected = {ref for ref, row in source_vacancies.items() if row["gate_ref"] == gate_ref}
        assert set(package["vacancy_refs"]) == expected
        assert package["vacancy_count"] == len(expected)
        assert package["prerequisite_gate_refs"] == gate["prerequisite_gate_refs"]
        assert not package["completion_claim"]

    gate_by_ref = {row["gate_ref"]: row for row in gate_kernels}
    assert len(gate_by_ref) == len(gate_kernels) and set(gate_by_ref) == set(source_gates)
    represented_edges = []
    for gate_ref, kernel in gate_by_ref.items():
        gate = source_gates[gate_ref]
        assert kernel["prerequisite_gate_refs"] == gate["prerequisite_gate_refs"]
        assert set(kernel["incoming_dependency_edge_refs"]) == {
            edge_id for edge_id, edge in source_edges.items() if edge["to_gate_ref"] == gate_ref
        }
        assert set(kernel["outgoing_dependency_edge_refs"]) == {
            edge_id for edge_id, edge in source_edges.items() if edge["from_gate_ref"] == gate_ref
        }
        represented_edges.extend(kernel["outgoing_dependency_edge_refs"])
        assert not kernel["completion_claim"]
    assert len(represented_edges) == len(set(represented_edges)) == len(source_edges)
    assert set(represented_edges) == set(source_edges)

    indegree = {gate_ref: 0 for gate_ref in source_gates}
    outgoing: dict[str, list[str]] = collections.defaultdict(list)
    for edge in source_edges.values():
        outgoing[edge["from_gate_ref"]].append(edge["to_gate_ref"])
        indegree[edge["to_gate_ref"]] += 1
    frontier = sorted(ref for ref, degree in indegree.items() if degree == 0)
    visited = []
    while frontier:
        gate_ref = frontier.pop(0)
        visited.append(gate_ref)
        for target in outgoing[gate_ref]:
            indegree[target] -= 1
            if indegree[target] == 0:
                frontier.append(target)
                frontier.sort()
    assert len(visited) == len(source_gates), "qualification gate graph contains a cycle"

    selection_by_subject = {row["subject_ref"]: row for row in selections}
    assert len(selection_by_subject) == len(selections) == len(source_subjects)
    assert set(selection_by_subject) == set(source_subjects)
    for subject_ref, selection in selection_by_subject.items():
        docket = docket_by_subject[subject_ref]
        assert selection["qualification_scope_ref"] == docket["qualification_scope_ref"]
        assert selection["subject_docket_ref"] == docket["docket_id"]
        assert selection["implementation_slot_refs"] == docket["implementation_slot_refs"]
        assert selection["selected_implementation_offer_ref"] is None
        assert selection["status"] == "REFUSE_IMPLEMENTATION_SELECTION"
        assert not selection["completion_claim"]

    product_by_candidate = {row["candidate_ref"]: row for row in products}
    assert len(product_by_candidate) == len(products) and set(product_by_candidate) == set(source_programs)
    product_subject_members = []
    for candidate_ref, product in product_by_candidate.items():
        program = source_programs[candidate_ref]
        vertical = source_verticals[candidate_ref]
        expected_subject_refs = set(program["library_subject_refs"])
        local_dockets = [docket_by_id[ref] for ref in product["subject_docket_refs"]]
        assert {row["subject_ref"] for row in local_dockets} == expected_subject_refs
        product_subject_members.extend(row["subject_ref"] for row in local_dockets)
        assert product["declared_library_subject_refs"] == sorted(expected_subject_refs)
        assert len(product["gate_states"]) == 16
        assert {row["gate_ref"] for row in product["gate_states"]} == set(source_gates)
        assert set(product["evidence_vacancy_refs"]) == vacancies_by_candidate[candidate_ref]
        assert product["vertical_acceptance_program_ref"] == vertical["acceptance_program_id"]
        assert product["required_unrelated_vertical_count"] == 2
        assert product["vertical_slots"] == vertical["vertical_slots"]
        assert product["selected_product_offer_ref"] is None
        assert product["status"] == program["current_verdict"]
        assert not product["completion_claim"]
    assert len(product_subject_members) == len(set(product_subject_members)) == len(source_subjects)
    assert set(product_subject_members) == set(source_subjects)

    print(
        f"PASS P6 implementation qualification: {len(resolutions)} concrete references and "
        f"{len(dockets)} subjects factor losslessly into {len(scopes)} exact scopes with "
        f"{len(all_slots)} independent slots; {len(source_vacancies)} vacancies factor into "
        f"{len(packages)} gate packages; all {len(selections)} compiler selections and "
        f"{len(products)} products refuse"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
