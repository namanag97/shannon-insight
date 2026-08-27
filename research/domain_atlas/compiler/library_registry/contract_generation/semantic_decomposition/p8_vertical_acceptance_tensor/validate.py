#!/usr/bin/env python3
"""Validate the lossless P8 product × vertical slot × acceptance-class tensor."""
from __future__ import annotations

import collections
import hashlib
import json

from build_p8 import (
    ACCEPTANCE_CONTRACTS,
    ACCEPTANCE_GATES,
    COMPOSITIONS,
    HERE,
    PRODUCT_PROGRAMS,
    VERTICAL_PROGRAMS,
    load_jsonl,
    outputs,
)


def main() -> int:
    for name, text in outputs().items():
        path = HERE / name
        assert path.is_file() and path.read_text() == text, f"stale {name}"
    manifest = json.loads((HERE / "manifest.json").read_text())
    assert not manifest["completion_claim"]
    for name, claim in manifest["files"].items():
        data = (HERE / name).read_bytes()
        assert len(data) == claim["bytes"]
        assert hashlib.sha256(data).hexdigest() == claim["sha256"]

    summary = json.loads((HERE / "summary.json").read_text())
    slots = load_jsonl(HERE / "product-vertical-slot-dockets.jsonl")
    workstreams = load_jsonl(HERE / "acceptance-class-workstreams.jsonl")
    templates = load_jsonl(HERE / "vertical-acceptance-intake-templates.jsonl")
    product_gates = load_jsonl(HERE / "product-two-vertical-acceptance-gates.jsonl")
    assert len(product_gates) == summary["product_programs"]
    assert len(slots) == summary["unrelated_vertical_slots"] == 2 * len(product_gates)
    assert len(workstreams) == summary["acceptance_gate_classes"]
    assert sum(row["obligation_count"] for row in workstreams) == summary["slot_gate_obligations"]
    assert len(templates) == summary["vertical_acceptance_intake_templates"] == len(slots)
    assert summary["executed_vertical_acceptances"] == 0
    assert summary["products_with_two_accepted_unrelated_verticals"] == 0
    assert not summary["completion_claim"]

    for claim in summary["input_snapshot"]["files"]:
        path = HERE.parents[6] / claim["path"]
        data = path.read_bytes()
        assert len(data) == claim["bytes"]
        assert hashlib.sha256(data).hexdigest() == claim["sha256"]
        assert len(load_jsonl(path)) == claim["record_count"]

    products = {row["candidate_id"]: row for row in load_jsonl(PRODUCT_PROGRAMS)}
    programs = {row["candidate_id"]: row for row in load_jsonl(VERTICAL_PROGRAMS)}
    compositions = {row["composition_id"]: row for row in load_jsonl(COMPOSITIONS)}
    contracts = {row["composition_ref"]: row for row in load_jsonl(ACCEPTANCE_CONTRACTS)}
    pilot_gates = load_jsonl(ACCEPTANCE_GATES)
    assert set(products) == set(programs)
    assert len(compositions) == len(contracts) == summary["pilot_structural_compositions"]
    required_gate_classes = programs[next(iter(programs))]["required_gate_classes"]
    assert len(required_gate_classes) == len(workstreams)
    assert len(pilot_gates) == len(compositions) * len(required_gate_classes)
    assert collections.Counter(row["gate_kind"] for row in pilot_gates) == {
        kind: len(compositions) for kind in required_gate_classes
    }
    assert all(row["execution_status"] == "not_executed" and row["receipt_refs"] == [] for row in pilot_gates)

    slots_by_candidate: dict[str, list[dict]] = collections.defaultdict(list)
    slot_by_id = {}
    all_obligations = []
    for slot in slots:
        assert slot["slot_id"] not in slot_by_id
        slot_by_id[slot["slot_id"]] = slot
        slots_by_candidate[slot["candidate_ref"]].append(slot)
        program = programs[slot["candidate_ref"]]
        assert slot["required_gate_classes"] == program["required_gate_classes"]
        assert len(slot["acceptance_obligation_refs"]) == len(required_gate_classes)
        all_obligations.extend(slot["acceptance_obligation_refs"])
        expected_compositions = {ref for ref, row in compositions.items() if slot["candidate_ref"] in row["product_refs"]}
        assert set(slot["structural_candidate_composition_refs"]) == expected_compositions
        assert set(slot["structural_candidate_industry_refs"]) == {compositions[ref]["industry_id"] for ref in expected_compositions}
        assert slot["selected_composition_ref"] is None
        assert slot["executed_gate_receipt_refs"] == [] and slot["accepted_vertical_ref"] is None
        assert slot["status"] == "BLOCKED_UNRELATED_VERTICAL_ACCEPTANCE" and not slot["completion_claim"]
    assert all(len(rows) == 2 for rows in slots_by_candidate.values()) and set(slots_by_candidate) == set(products)
    assert len(all_obligations) == len(set(all_obligations)) == len(slots) * len(required_gate_classes)

    represented_obligations = [ref for row in workstreams for ref in row["slot_obligation_refs"]]
    assert len(represented_obligations) == len(set(represented_obligations)) == len(all_obligations)
    assert set(represented_obligations) == set(all_obligations)
    for workstream in workstreams:
        assert workstream["obligation_count"] == len(workstream["slot_obligation_refs"]) == len(slots)
        assert len(workstream["slot_refs"]) == len(slots) and set(workstream["slot_refs"]) == set(slot_by_id)
        assert len(workstream["candidate_refs"]) == len(products) and set(workstream["candidate_refs"]) == set(products)
        expected_pilot_gates = {row["acceptance_gate_id"] for row in pilot_gates if row["gate_kind"] == workstream["gate_class"]}
        assert set(workstream["pilot_gate_refs"]) == expected_pilot_gates
        assert not workstream["completion_claim"]

    template_by_slot = {row["slot_ref"]: row for row in templates}
    assert len(template_by_slot) == len(templates) and set(template_by_slot) == set(slot_by_id)
    for slot_ref, template in template_by_slot.items():
        slot = slot_by_id[slot_ref]
        assert template["slot_docket_ref"] == slot["docket_id"]
        assert template["required_gate_classes"] == slot["required_gate_classes"]
        assert set(template["required_submission_fields"]) == set(template["submission"])
        assert all(value is None for value in template["submission"].values())
        assert template["status"] == "EMPTY_AWAITING_EXECUTED_VERTICAL_ACCEPTANCE"
        assert not template["completion_claim"]

    gate_by_candidate = {row["candidate_ref"]: row for row in product_gates}
    assert len(gate_by_candidate) == len(product_gates) and set(gate_by_candidate) == set(products)
    candidate_relation_count = 0
    covered = 0
    two_unrelated = 0
    for candidate_ref, gate in gate_by_candidate.items():
        expected = {ref for ref, row in compositions.items() if candidate_ref in row["product_refs"]}
        candidate_relation_count += len(expected)
        covered += bool(expected)
        two_unrelated += len({compositions[ref]["industry_id"] for ref in expected}) >= 2
        assert set(gate["structural_candidate_composition_refs"]) == expected
        assert set(gate["slot_refs"]) == {row["slot_id"] for row in slots_by_candidate[candidate_ref]}
        assert gate["accepted_vertical_refs"] == [] and gate["accepted_unrelated_vertical_count"] == 0
        assert gate["status"] == "REFUSE_PRODUCT_VERTICAL_ACCEPTANCE"
        assert not gate["completion_claim"]
    assert candidate_relation_count == summary["pilot_product_candidate_relations"]
    assert covered == summary["products_with_any_structural_pilot"]
    assert two_unrelated == summary["products_with_two_unrelated_structural_pilots"]
    print(
        f"PASS P8 vertical acceptance: {len(products)} products × 2 unrelated slots × "
        f"{len(required_gate_classes)} gate classes remain lossless as {len(all_obligations)} "
        f"obligations in {len(workstreams)} workstreams; {len(compositions)} structural pilots "
        f"cover {covered} products but zero acceptance gates are executed"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
