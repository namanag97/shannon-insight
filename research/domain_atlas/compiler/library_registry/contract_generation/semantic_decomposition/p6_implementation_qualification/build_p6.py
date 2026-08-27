#!/usr/bin/env python3
"""Build implementation/qualification scopes and compiler selection refusal gates."""
from __future__ import annotations

import argparse
import collections
import hashlib
import json
import re
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[6]
QUALIFICATION = REPO / "research/product_ontology/qualification_program"
LIBRARY_REGISTRY = HERE.parents[2]
SUBJECTS = QUALIFICATION / "library-qualification-subjects.jsonl"
GATE_DEFINITIONS = QUALIFICATION / "gate-definitions.jsonl"
GATE_DEPENDENCIES = QUALIFICATION / "gate-dependencies.jsonl"
PRODUCT_PROGRAMS = QUALIFICATION / "product-qualification-programs.jsonl"
VERTICAL_PROGRAMS = QUALIFICATION / "product-vertical-acceptance-programs.jsonl"
VACANCIES = QUALIFICATION / "evidence-vacancies.jsonl"
CONTRIBUTIONS = LIBRARY_REGISTRY / "library-contributions.jsonl"
P5_TEMPLATES = HERE.parent / "p5_exact_contract_adjudication/exact-contract-ratification-packet-templates.jsonl"
AS_OF = "2026-08-27"


RESOLUTION_CLASSES = [
    "P5_OPEN_EXACT_CONTRACT",
    "REGISTERED_SPECIFIED_UNIMPLEMENTED",
    "REGISTERED_CANDIDATE_UNADJUDICATED",
    "UNREGISTERED_CONCRETE_REFERENCE",
]


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def digest(value: Any) -> str:
    return hashlib.sha256(canonical(value).encode()).hexdigest()


def slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def snapshot() -> dict[str, Any]:
    files = []
    for path in (SUBJECTS, GATE_DEFINITIONS, GATE_DEPENDENCIES, PRODUCT_PROGRAMS, VERTICAL_PROGRAMS, VACANCIES, CONTRIBUTIONS, P5_TEMPLATES):
        data = path.read_bytes()
        files.append({
            "path": str(path.relative_to(REPO)),
            "bytes": len(data),
            "sha256": hashlib.sha256(data).hexdigest(),
            "record_count": len(load_jsonl(path)),
        })
    aggregate = digest(files)
    return {"snapshot_id": f"snapshot.p6-input.{aggregate[:16]}", "aggregate_sha256": aggregate, "files": files}


def scope_signature(subject: dict[str, Any]) -> dict[str, Any]:
    return {
        "abstract_library_ref": subject["abstract_library_ref"],
        "contract_digest": digest(subject["contract"]),
        "concrete_library_refs": sorted(subject["compiler_projection"]["concrete_library_refs"]),
        "effect_boundary": subject["effect_boundary"],
        "required_conformance_context_refs": sorted(subject["required_conformance_context_refs"]),
        "required_evidence_classes": sorted(subject["required_evidence_classes"]),
    }


def build_records() -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    snap = snapshot()
    subjects = load_jsonl(SUBJECTS)
    contributions = {row["library_id"]: row for row in load_jsonl(CONTRIBUTIONS)}
    p5_by_library = {row["library_ref"]: row for row in load_jsonl(P5_TEMPLATES)}
    gates = load_jsonl(GATE_DEFINITIONS)
    gate_edges = load_jsonl(GATE_DEPENDENCIES)
    programs = load_jsonl(PRODUCT_PROGRAMS)
    vertical_programs = load_jsonl(VERTICAL_PROGRAMS)
    vacancies = load_jsonl(VACANCIES)

    concrete_refs = sorted({ref for subject in subjects for ref in subject["compiler_projection"]["concrete_library_refs"]})
    resolutions = []
    for ref in concrete_refs:
        contribution = contributions.get(ref)
        p5 = p5_by_library.get(ref)
        if p5:
            resolution_class = "P5_OPEN_EXACT_CONTRACT"
        elif contribution and contribution["status"] == "specified_unimplemented":
            resolution_class = "REGISTERED_SPECIFIED_UNIMPLEMENTED"
        elif contribution:
            resolution_class = "REGISTERED_CANDIDATE_UNADJUDICATED"
        else:
            resolution_class = "UNREGISTERED_CONCRETE_REFERENCE"
        resolutions.append({
            "record_kind": "qualification_concrete_reference_resolution",
            "resolution_id": f"resolution.p6.{slug(ref)}.v1",
            "edition": 1,
            "concrete_library_ref": ref,
            "resolution_class": resolution_class,
            "registry_contribution_status": contribution.get("status") if contribution else None,
            "registry_source_status": contribution.get("source_projection", {}).get("source_status") if contribution else None,
            "p5_exact_contract_template_ref": p5.get("template_id") if p5 else None,
            "selected_exact_contract_ref": None,
            "qualified_implementation_refs": [],
            "status": "BLOCKED_NO_QUALIFIED_IMPLEMENTATION",
            "completion_claim": False,
        })
    resolution_by_ref = {row["concrete_library_ref"]: row for row in resolutions}

    scope_groups: dict[str, list[dict[str, Any]]] = collections.defaultdict(list)
    scope_signatures = {}
    for subject in subjects:
        signature = scope_signature(subject)
        scope_id = f"scope.p6.qualification.{digest(signature)[:20]}.v1"
        scope_signatures[scope_id] = signature
        scope_groups[scope_id].append(subject)
    scope_kernels = []
    for scope_id, members in sorted(scope_groups.items()):
        signature = scope_signatures[scope_id]
        member_ids = sorted(row["subject_id"] for row in members)
        scope_kernels.append({
            "record_kind": "exact_implementation_qualification_scope",
            "scope_id": scope_id,
            "edition": 1,
            "signature": signature,
            "subject_refs": member_ids,
            "candidate_refs": sorted({row["candidate_id"] for row in members}),
            "product_refs": sorted({row["product_ref"] for row in members}),
            "subject_count": len(members),
            "required_independent_implementation_slots": 2,
            "implementation_slot_refs": [f"slot.{scope_id}.primary", f"slot.{scope_id}.independent-secondary"],
            "qualified_implementation_refs": [],
            "portable_offer": False,
            "sharing_law": "A qualification may be reused only for this exact immutable contract, implementation, dependency, target, configuration, evidence and budget scope.",
            "status": "OPEN_NO_BOUND_IMPLEMENTATION",
            "completion_claim": False,
        })
    scope_by_subject = {subject_ref: row for row in scope_kernels for subject_ref in row["subject_refs"]}

    vacancies_by_candidate: dict[str, list[dict[str, Any]]] = collections.defaultdict(list)
    for row in vacancies:
        vacancies_by_candidate[row["candidate_id"]].append(row)
    subject_dockets = []
    selection_gates = []
    for subject in sorted(subjects, key=lambda row: row["subject_id"]):
        local_resolutions = [resolution_by_ref[ref] for ref in subject["compiler_projection"]["concrete_library_refs"]]
        resolution_classes = sorted({row["resolution_class"] for row in local_resolutions})
        blockers = ["NO_BOUND_IMPLEMENTATION_ARTIFACT", "NO_EXECUTED_CONFORMANCE_EVIDENCE", "NO_INDEPENDENT_APPRAISAL", "NO_PORTABLE_OFFER"]
        blocker_by_resolution = {
            "P5_OPEN_EXACT_CONTRACT": "EXACT_CONTRACT_UNRATIFIED",
            "REGISTERED_SPECIFIED_UNIMPLEMENTED": "SPECIFIED_LIBRARY_UNIMPLEMENTED",
            "REGISTERED_CANDIDATE_UNADJUDICATED": "REGISTRY_CANDIDATE_UNADJUDICATED",
            "UNREGISTERED_CONCRETE_REFERENCE": "CONCRETE_REFERENCE_ABSENT_FROM_REGISTRY",
        }
        blockers.extend(blocker_by_resolution[item] for item in resolution_classes)
        docket_id = f"docket.p6.{slug(subject['subject_id'])}.v1"
        subject_dockets.append({
            "record_kind": "implementation_qualification_subject_docket",
            "docket_id": docket_id,
            "edition": 1,
            "subject_ref": subject["subject_id"],
            "qualification_scope_ref": scope_by_subject[subject["subject_id"]]["scope_id"],
            "candidate_ref": subject["candidate_id"],
            "product_ref": subject["product_ref"],
            "abstract_library_ref": subject["abstract_library_ref"],
            "semantic_owner_ref": subject["semantic_owner_ref"],
            "concrete_reference_resolution_refs": [row["resolution_id"] for row in local_resolutions],
            "resolution_classes": resolution_classes,
            "p5_exact_contract_template_refs": [row["p5_exact_contract_template_ref"] for row in local_resolutions if row["p5_exact_contract_template_ref"]],
            "required_conformance_context_refs": subject["required_conformance_context_refs"],
            "required_evidence_classes": subject["required_evidence_classes"],
            "evidence_vacancy_refs": sorted(row["vacancy_id"] for row in vacancies_by_candidate[subject["candidate_id"]]),
            "implementation_slot_refs": scope_by_subject[subject["subject_id"]]["implementation_slot_refs"],
            "qualified_implementation_refs": [],
            "blocker_kinds": sorted(set(blockers)),
            "status": "BLOCKED_IMPLEMENTATION_QUALIFICATION",
            "completion_claim": False,
        })
        selection_gates.append({
            "record_kind": "compiler_implementation_selection_gate",
            "gate_id": f"gate.p6.selection.{slug(subject['subject_id'])}.v1",
            "edition": 1,
            "subject_ref": subject["subject_id"],
            "subject_docket_ref": docket_id,
            "qualification_scope_ref": scope_by_subject[subject["subject_id"]]["scope_id"],
            "implementation_slot_refs": scope_by_subject[subject["subject_id"]]["implementation_slot_refs"],
            "candidate_ref": subject["candidate_id"],
            "abstract_library_ref": subject["abstract_library_ref"],
            "required_capability_refs": subject["provided_capability_refs"],
            "selected_implementation_offer_ref": None,
            "refusal_codes": sorted(set(blockers + ["NO_EXACT_SCOPE_QUALIFICATION_RECEIPT"])),
            "status": "REFUSE_IMPLEMENTATION_SELECTION",
            "completion_claim": False,
        })

    vacancy_packages = []
    vacancies_by_gate: dict[str, list[dict[str, Any]]] = collections.defaultdict(list)
    for row in vacancies:
        vacancies_by_gate[row["gate_ref"]].append(row)
    for gate_ref, rows in sorted(vacancies_by_gate.items()):
        gate = next(item for item in gates if item["gate_id"] == gate_ref)
        vacancy_packages.append({
            "record_kind": "qualification_gate_evidence_vacancy_package",
            "package_id": f"package.p6.{slug(gate_ref)}.v1",
            "edition": 1,
            "gate_ref": gate_ref,
            "plane": gate["plane"],
            "prerequisite_gate_refs": gate["prerequisite_gate_refs"],
            "vacancy_refs": sorted(row["vacancy_id"] for row in rows),
            "candidate_refs": sorted({row["candidate_id"] for row in rows}),
            "vacancy_count": len(rows),
            "shared_evidence_work": sorted({item for row in rows for item in row["evidence_needed"]}),
            "propagation_law": "Evidence methods and fixtures may be shared; every product, implementation, scope and gate receipt remains separately attributable.",
            "status": "OPEN_EVIDENCE_WORK_QUOTIENT",
            "completion_claim": False,
        })

    gate_kernels = []
    incoming = collections.defaultdict(list)
    outgoing = collections.defaultdict(list)
    for edge in gate_edges:
        outgoing[edge["from_gate_ref"]].append(edge["edge_id"])
        incoming[edge["to_gate_ref"]].append(edge["edge_id"])
    for gate in gates:
        gate_ref = gate["gate_id"]
        gate_kernels.append({
            "record_kind": "qualification_gate_execution_kernel",
            "kernel_id": f"kernel.p6.{slug(gate_ref)}.v1",
            "edition": 1,
            "gate_ref": gate_ref,
            "plane": gate["plane"],
            "prerequisite_gate_refs": gate["prerequisite_gate_refs"],
            "incoming_dependency_edge_refs": sorted(incoming[gate_ref]),
            "outgoing_dependency_edge_refs": sorted(outgoing[gate_ref]),
            "evidence_vacancy_package_ref": f"package.p6.{slug(gate_ref)}.v1" if gate_ref in vacancies_by_gate else None,
            "promotion_law": gate["promotion_law"],
            "status": "STRUCTURAL_SATISFIED" if gate_ref in {"gate.qp.boundary_ddd", "gate.qp.contract_decomposition"} else "OPEN_OR_WITHHELD",
            "completion_claim": False,
        })

    product_dockets = []
    subject_refs_by_candidate: dict[str, list[str]] = collections.defaultdict(list)
    for subject in subject_dockets:
        subject_refs_by_candidate[subject["candidate_ref"]].append(subject["docket_id"])
    vertical_by_candidate = {row["candidate_id"]: row for row in vertical_programs}
    for program in sorted(programs, key=lambda row: row["candidate_id"]):
        candidate_ref = program["candidate_id"]
        vertical = vertical_by_candidate[candidate_ref]
        product_dockets.append({
            "record_kind": "product_qualification_execution_docket",
            "docket_id": f"docket.p6.product.{slug(candidate_ref)}.v1",
            "edition": 1,
            "candidate_ref": candidate_ref,
            "product_ref": program["product_ref"],
            "ddd_dossier_ref": program["ddd_dossier_ref"],
            "boundary_verdict": program["boundary_verdict"],
            "declared_library_subject_refs": sorted(program["library_subject_refs"]),
            "subject_docket_refs": sorted(subject_refs_by_candidate[candidate_ref]),
            "gate_states": program["gate_states"],
            "evidence_vacancy_refs": sorted(row["vacancy_id"] for row in vacancies_by_candidate[candidate_ref]),
            "vertical_acceptance_program_ref": vertical["acceptance_program_id"],
            "required_unrelated_vertical_count": vertical["required_unrelated_vertical_count"],
            "vertical_slots": vertical["vertical_slots"],
            "selected_product_offer_ref": None,
            "refusal_codes": [
                "NO_QUALIFIED_LIBRARY_IMPLEMENTATIONS",
                "NO_PORTABLE_PRODUCT_OFFER",
                "NO_EXECUTED_UNRELATED_VERTICAL_ACCEPTANCE",
                "OPEN_QUALIFICATION_EVIDENCE_VACANCIES",
            ],
            "status": program["current_verdict"],
            "completion_claim": False,
        })
    return resolutions, scope_kernels, subject_dockets, vacancy_packages, gate_kernels, selection_gates, product_dockets, snap


def outputs() -> dict[str, str]:
    resolutions, scopes, subjects, packages, gates, selections, products, snap = build_records()
    summary = {
        "program_id": "program.p6-implementation-qualification.v1",
        "edition": 1,
        "as_of": AS_OF,
        "input_snapshot": snap,
        "concrete_reference_resolutions": len(resolutions),
        "resolution_counts": dict(sorted(collections.Counter(row["resolution_class"] for row in resolutions).items())),
        "qualification_scope_kernels": len(scopes),
        "shared_qualification_scope_kernels": sum(row["subject_count"] > 1 for row in scopes),
        "implementation_slots": sum(len(row["implementation_slot_refs"]) for row in scopes),
        "subject_dockets": len(subjects),
        "evidence_vacancy_packages": len(packages),
        "represented_evidence_vacancies": sum(row["vacancy_count"] for row in packages),
        "gate_execution_kernels": len(gates),
        "selection_gates": len(selections),
        "product_qualification_dockets": len(products),
        "qualified_implementations": 0,
        "portable_offers": 0,
        "selected_implementation_offers": 0,
        "build_ready_products": 0,
        "completion_claim": False,
    }
    files = {
        "resolution-ontology.json": json.dumps({"resolution_classes": RESOLUTION_CLASSES}, sort_keys=True, indent=2) + "\n",
        "concrete-reference-resolutions.jsonl": "".join(canonical(row) + "\n" for row in resolutions),
        "qualification-scope-kernels.jsonl": "".join(canonical(row) + "\n" for row in scopes),
        "subject-dockets.jsonl": "".join(canonical(row) + "\n" for row in subjects),
        "evidence-vacancy-packages.jsonl": "".join(canonical(row) + "\n" for row in packages),
        "gate-execution-kernels.jsonl": "".join(canonical(row) + "\n" for row in gates),
        "compiler-selection-gates.jsonl": "".join(canonical(row) + "\n" for row in selections),
        "product-qualification-dockets.jsonl": "".join(canonical(row) + "\n" for row in products),
        "summary.json": json.dumps(summary, sort_keys=True, indent=2) + "\n",
    }
    manifest = {name: {"bytes": len(text.encode()), "sha256": hashlib.sha256(text.encode()).hexdigest()} for name, text in files.items()}
    files["manifest.json"] = json.dumps({"manifest_id": "manifest.p6-implementation-qualification.v1", "as_of": AS_OF, "files": manifest, "completion_claim": False}, sort_keys=True, indent=2) + "\n"
    return files


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    stale = []
    for name, text in outputs().items():
        path = HERE / name
        if args.check:
            if not path.is_file() or path.read_text() != text:
                stale.append(name)
        else:
            path.write_text(text)
    if stale:
        print("STALE " + ", ".join(stale))
        return 1
    summary = json.loads(outputs()["summary.json"])
    print(f"{'CHECK' if args.check else 'BUILD'} PASS P6: {summary['subject_dockets']} subjects become {summary['qualification_scope_kernels']} exact scopes and {summary['represented_evidence_vacancies']} vacancies become {summary['evidence_vacancy_packages']} gate packages; zero qualified or selected implementations")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
