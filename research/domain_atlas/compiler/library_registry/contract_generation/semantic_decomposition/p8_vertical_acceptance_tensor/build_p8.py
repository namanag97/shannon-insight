#!/usr/bin/env python3
"""Build the product × unrelated-vertical-slot × acceptance-class tensor."""
from __future__ import annotations

import argparse
import collections
import hashlib
import json
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[6]
QUALIFICATION = REPO / "research/product_ontology/qualification_program"
PILOTS = REPO / "research/product_ontology/composition_pilots/deterministic_verticals"
PRODUCT_PROGRAMS = QUALIFICATION / "product-qualification-programs.jsonl"
VERTICAL_PROGRAMS = QUALIFICATION / "product-vertical-acceptance-programs.jsonl"
COMPOSITIONS = PILOTS / "vertical-compositions.jsonl"
ACCEPTANCE_CONTRACTS = PILOTS / "vertical-acceptance-contracts.jsonl"
ACCEPTANCE_GATES = PILOTS / "vertical-acceptance-gates.jsonl"
AS_OF = "2026-08-27"


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def digest(value: Any) -> str:
    return hashlib.sha256(canonical(value).encode()).hexdigest()


def snapshot() -> dict[str, Any]:
    files = []
    for path in (PRODUCT_PROGRAMS, VERTICAL_PROGRAMS, COMPOSITIONS, ACCEPTANCE_CONTRACTS, ACCEPTANCE_GATES):
        data = path.read_bytes()
        files.append({"path": str(path.relative_to(REPO)), "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest(), "record_count": len(load_jsonl(path))})
    aggregate = hashlib.sha256(canonical(files).encode()).hexdigest()
    return {"snapshot_id": f"snapshot.p8-input.{aggregate[:16]}", "aggregate_sha256": aggregate, "files": files}


def build_records() -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    snap = snapshot()
    products = {row["candidate_id"]: row for row in load_jsonl(PRODUCT_PROGRAMS)}
    programs = load_jsonl(VERTICAL_PROGRAMS)
    compositions = load_jsonl(COMPOSITIONS)
    contracts = {row["composition_ref"]: row for row in load_jsonl(ACCEPTANCE_CONTRACTS)}
    pilot_gates = load_jsonl(ACCEPTANCE_GATES)
    pilot_gates_by_composition: dict[str, list[dict[str, Any]]] = collections.defaultdict(list)
    for gate in pilot_gates:
        pilot_gates_by_composition[gate["composition_ref"]].append(gate)

    compositions_by_product: dict[str, list[dict[str, Any]]] = collections.defaultdict(list)
    for composition in compositions:
        for product_ref in composition["product_refs"]:
            compositions_by_product[product_ref].append(composition)

    slot_dockets = []
    intake_templates = []
    obligations_by_class: dict[str, list[dict[str, str]]] = collections.defaultdict(list)
    product_slot_refs: dict[str, list[str]] = collections.defaultdict(list)
    for program in sorted(programs, key=lambda row: row["candidate_id"]):
        candidate_ref = program["candidate_id"]
        candidates = sorted(compositions_by_product[candidate_ref], key=lambda row: row["composition_id"])
        for slot in program["vertical_slots"]:
            slot_name = slot["slot"]
            slot_id = f"slot.p8.{candidate_ref.removeprefix('candidate.product.')}.{slot_name}.v1"
            docket_id = f"docket.p8.{digest(slot_id)[:20]}.v1"
            product_slot_refs[candidate_ref].append(slot_id)
            obligation_refs = []
            for gate_class in program["required_gate_classes"]:
                obligation_id = f"obligation.p8.{digest([slot_id, gate_class])[:20]}.v1"
                obligation_refs.append(obligation_id)
                obligations_by_class[gate_class].append({"obligation_ref": obligation_id, "slot_ref": slot_id, "candidate_ref": candidate_ref})
            slot_dockets.append({
                "record_kind": "product_unrelated_vertical_slot_docket",
                "docket_id": docket_id,
                "edition": 1,
                "slot_id": slot_id,
                "acceptance_program_ref": program["acceptance_program_id"],
                "candidate_ref": candidate_ref,
                "product_ref": products[candidate_ref]["product_ref"],
                "slot_name": slot_name,
                "required_gate_classes": program["required_gate_classes"],
                "acceptance_obligation_refs": obligation_refs,
                "structural_candidate_composition_refs": [row["composition_id"] for row in candidates],
                "structural_candidate_industry_refs": sorted({row["industry_id"] for row in candidates}),
                "structural_candidate_acceptance_contract_refs": [contracts[row["composition_id"]]["acceptance_contract_id"] for row in candidates],
                "selected_composition_ref": None,
                "executed_gate_receipt_refs": [],
                "accepted_vertical_ref": None,
                "blocker_kinds": ["NO_SLOT_SELECTION", "NO_EXACT_PRODUCT_SCOPE_BINDING", "NO_EXECUTED_GATE_RECEIPTS", "NO_VERTICAL_ACCEPTANCE_AUTHORITY_RECEIPT"],
                "status": "BLOCKED_UNRELATED_VERTICAL_ACCEPTANCE",
                "completion_claim": False,
            })
            template_id = f"template.p8.acceptance.{digest(slot_id)[:20]}.v1"
            intake_templates.append({
                "record_kind": "vertical_acceptance_intake_template",
                "template_id": template_id,
                "edition": 1,
                "slot_ref": slot_id,
                "slot_docket_ref": docket_id,
                "candidate_ref": candidate_ref,
                "required_gate_classes": program["required_gate_classes"],
                "required_submission_fields": ["composition_ref", "vertical_case_ref", "industry_ref", "exact_product_scope_digest", "gate_receipt_refs_by_class", "acceptance_authority_ref", "unrelatedness_witness", "validity_interval", "invalidation_triggers"],
                "submission": {
                    "composition_ref": None,
                    "vertical_case_ref": None,
                    "industry_ref": None,
                    "exact_product_scope_digest": None,
                    "gate_receipt_refs_by_class": None,
                    "acceptance_authority_ref": None,
                    "unrelatedness_witness": None,
                    "validity_interval": None,
                    "invalidation_triggers": None,
                },
                "status": "EMPTY_AWAITING_EXECUTED_VERTICAL_ACCEPTANCE",
                "completion_claim": False,
            })

    workstreams = []
    for gate_class, obligations in sorted(obligations_by_class.items()):
        examples = [row for row in pilot_gates if row["gate_kind"] == gate_class]
        workstreams.append({
            "record_kind": "vertical_acceptance_class_workstream",
            "workstream_id": f"workstream.p8.acceptance.{gate_class}.v1",
            "edition": 1,
            "gate_class": gate_class,
            "slot_obligation_refs": sorted(row["obligation_ref"] for row in obligations),
            "slot_refs": sorted(row["slot_ref"] for row in obligations),
            "candidate_refs": sorted({row["candidate_ref"] for row in obligations}),
            "obligation_count": len(obligations),
            "pilot_gate_refs": sorted(row["acceptance_gate_id"] for row in examples),
            "question_candidates": sorted({row["question"] for row in examples}),
            "required_evidence_candidates": sorted({item for row in examples for item in row["required_evidence"]}),
            "refusal_law_candidates": sorted({row["refusal_law"] for row in examples}),
            "sharing_law": "Share gate method, evidence schema and negative-twin design; retain case-specific obligations, execution, authority and verdict per exact product/vertical slot.",
            "status": "OPEN_ACCEPTANCE_CLASS_WORKSTREAM",
            "completion_claim": False,
        })

    product_gates = []
    dockets_by_candidate: dict[str, list[dict[str, Any]]] = collections.defaultdict(list)
    for docket in slot_dockets:
        dockets_by_candidate[docket["candidate_ref"]].append(docket)
    for candidate_ref, product in sorted(products.items()):
        local_dockets = sorted(dockets_by_candidate[candidate_ref], key=lambda row: row["slot_name"])
        candidates = sorted(compositions_by_product[candidate_ref], key=lambda row: row["composition_id"])
        product_gates.append({
            "record_kind": "two_unrelated_vertical_acceptance_gate",
            "gate_id": f"gate.p8.product.{candidate_ref.removeprefix('candidate.product.')}.v1",
            "edition": 1,
            "candidate_ref": candidate_ref,
            "product_ref": product["product_ref"],
            "required_unrelated_vertical_count": 2,
            "slot_refs": [row["slot_id"] for row in local_dockets],
            "structural_candidate_composition_refs": [row["composition_id"] for row in candidates],
            "structural_candidate_industry_refs": sorted({row["industry_id"] for row in candidates}),
            "structural_candidate_count": len(candidates),
            "structural_candidate_unrelated_industry_count": len({row["industry_id"] for row in candidates}),
            "accepted_vertical_refs": [],
            "accepted_unrelated_vertical_count": 0,
            "refusal_codes": ["NO_TWO_EXECUTED_ACCEPTED_VERTICALS", "NO_UNRELATEDNESS_WITNESS", "NO_EXACT_PRODUCT_SCOPE_EQUIVALENCE", "NO_CURRENT_ACCEPTANCE_RECEIPTS"],
            "status": "REFUSE_PRODUCT_VERTICAL_ACCEPTANCE",
            "completion_claim": False,
        })
    return slot_dockets, workstreams, intake_templates, product_gates, snap


def outputs() -> dict[str, str]:
    slots, workstreams, templates, product_gates, snap = build_records()
    summary = {
        "program_id": "program.p8-vertical-acceptance-tensor.v1",
        "edition": 1,
        "as_of": AS_OF,
        "input_snapshot": snap,
        "product_programs": len(product_gates),
        "unrelated_vertical_slots": len(slots),
        "acceptance_gate_classes": len(workstreams),
        "slot_gate_obligations": sum(row["obligation_count"] for row in workstreams),
        "vertical_acceptance_intake_templates": len(templates),
        "pilot_structural_compositions": len(load_jsonl(COMPOSITIONS)),
        "pilot_product_candidate_relations": sum(row["structural_candidate_count"] for row in product_gates),
        "products_with_any_structural_pilot": sum(row["structural_candidate_count"] > 0 for row in product_gates),
        "products_with_two_unrelated_structural_pilots": sum(row["structural_candidate_unrelated_industry_count"] >= 2 for row in product_gates),
        "executed_vertical_acceptances": 0,
        "products_with_two_accepted_unrelated_verticals": 0,
        "completion_claim": False,
    }
    files = {
        "product-vertical-slot-dockets.jsonl": "".join(canonical(row) + "\n" for row in slots),
        "acceptance-class-workstreams.jsonl": "".join(canonical(row) + "\n" for row in workstreams),
        "vertical-acceptance-intake-templates.jsonl": "".join(canonical(row) + "\n" for row in templates),
        "product-two-vertical-acceptance-gates.jsonl": "".join(canonical(row) + "\n" for row in product_gates),
        "summary.json": json.dumps(summary, sort_keys=True, indent=2) + "\n",
    }
    manifest = {name: {"bytes": len(text.encode()), "sha256": hashlib.sha256(text.encode()).hexdigest()} for name, text in files.items()}
    files["manifest.json"] = json.dumps({"manifest_id": "manifest.p8-vertical-acceptance-tensor.v1", "as_of": AS_OF, "files": manifest, "completion_claim": False}, sort_keys=True, indent=2) + "\n"
    return files


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    built = outputs()
    stale = []
    for name, text in built.items():
        path = HERE / name
        if args.check:
            if not path.is_file() or path.read_text() != text:
                stale.append(name)
        else:
            path.write_text(text)
    if stale:
        print("STALE " + ", ".join(stale))
        return 1
    summary = json.loads(built["summary.json"])
    print(f"{'CHECK' if args.check else 'BUILD'} PASS P8: {summary['slot_gate_obligations']} slot×gate obligations factor into {summary['acceptance_gate_classes']} workstreams; {summary['pilot_structural_compositions']} pilots cover {summary['products_with_any_structural_pilot']} products structurally; zero acceptances")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
