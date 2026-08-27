#!/usr/bin/env python3
"""Validate the P1B foundation-authority ratification surface."""
from __future__ import annotations

import collections
import hashlib
import json

from build_p1b import (
    AUTHORITY_PACKETS,
    BOUNDARY_CLUSTERS,
    COLLISIONS,
    FAMILY_CONSTITUTIONS,
    HERE,
    P3_TEMPLATES,
    SOURCE_AUDITS,
    TEMPLATE_CONTRACTS,
    load_jsonl,
    outputs,
)


def main() -> int:
    expected = outputs()
    for name, text in expected.items():
        path = HERE / name
        assert path.is_file() and path.read_text() == text, f"stale {name}"
    manifest = json.loads((HERE / "manifest.json").read_text())
    for name, claim in manifest["files"].items():
        data = (HERE / name).read_bytes()
        assert len(data) == claim["bytes"]
        assert hashlib.sha256(data).hexdigest() == claim["sha256"], name

    summary = json.loads((HERE / "summary.json").read_text())
    sources = load_jsonl(HERE / "source-authority-dockets.jsonl")
    collision_dockets = load_jsonl(HERE / "collision-dockets.jsonl")
    boundary_dockets = load_jsonl(HERE / "boundary-dockets.jsonl")
    family_dockets = load_jsonl(HERE / "family-constitution-dockets.jsonl")
    templates = load_jsonl(HERE / "ratification-packet-templates.jsonl")

    assert len(sources) == summary["source_authority_dockets"]
    assert len(collision_dockets) == summary["collision_dockets"]
    assert len(boundary_dockets) == summary["boundary_dockets"]
    assert summary["boundary_dockets_ready"] + summary["boundary_dockets_blocked"] == len(boundary_dockets)
    assert len(family_dockets) == summary["family_constitution_dockets"] == len(sources)
    assert len(templates) == summary["ratification_packet_templates"]
    assert summary["authority_review_ready_templates"] + summary["blocked_templates"] == len(templates)
    assert summary["ratified_decisions"] == summary["canonical_mutations_allowed"] == summary["canonical_gaps_closed"] == 0
    assert not summary["completion_claim"]

    for claim in summary["input_snapshot"]["files"]:
        path = HERE.parents[6] / claim["path"]
        data = path.read_bytes()
        assert len(data) == claim["bytes"]
        assert hashlib.sha256(data).hexdigest() == claim["sha256"]
        assert len(load_jsonl(path)) == claim["record_count"]

    packets = {row["packet_id"]: row for row in load_jsonl(AUTHORITY_PACKETS)}
    audits = {row["audit_id"]: row for row in load_jsonl(SOURCE_AUDITS)}
    collisions = {row["collision_id"]: row for row in load_jsonl(COLLISIONS)}
    boundaries = {row["cluster_id"]: row for row in load_jsonl(BOUNDARY_CLUSTERS)}
    families = {row["family_id"]: row for row in load_jsonl(FAMILY_CONSTITUTIONS)}
    p3_templates = {row["template_id"]: row for row in load_jsonl(P3_TEMPLATES)}
    template_by_id = {row["template_id"]: row for row in templates}
    assert len(template_by_id) == len(templates)

    assert {row["authority_packet_ref"] for row in sources} == set(packets)
    assert {row["readiness_audit_ref"] for row in sources} == set(audits)
    assert all(row["selected_authority_decision"] == "UNRESOLVED" for row in sources)
    assert all(row["status"] == "READY_FOR_NAMED_AUTHORITY_REVIEW" for row in sources)

    assert {row["collision_ref"] for row in collision_dockets} == set(collisions)
    assert all(row["selected_collision_disposition"] == "UNRESOLVED" for row in collision_dockets)
    assert all(row["status"] == "READY_FOR_CONTEXT_OWNER_REVIEW" for row in collision_dockets)

    assert {row["boundary_cluster_ref"] for row in boundary_dockets} == set(boundaries)
    boundary_library_refs = [ref for row in boundary_dockets for ref in row["library_refs"]]
    assert len(boundary_library_refs) == len(set(boundary_library_refs))
    assert collections.Counter(row["status"] for row in boundary_dockets) == {
        "READY_FOR_SEMANTIC_OWNER_REVIEW": summary["boundary_dockets_ready"],
        "BLOCKED_BY_COLLISION_ADJUDICATION": summary["boundary_dockets_blocked"],
    }
    collision_template_ids = {
        row["collision_ref"]: row["ratification_template_ref"] for row in collision_dockets
    }
    for docket in boundary_dockets:
        expected_collisions = sorted({
            collision_template_ids[collision_id]
            for library_ref in docket["library_refs"]
            for collision_id, collision in collisions.items()
            if library_ref in {collision["left_library_ref"], collision["right_library_ref"]}
        })
        assert docket["collision_ratification_template_refs"] == expected_collisions
        assert docket["selected_boundary_disposition"] == "UNRESOLVED"

    assert {row["family_ref"] for row in family_dockets} == set(families)
    assert all(len(row["family_axis_ratification_template_refs"]) == 16 for row in family_dockets)
    for docket in family_dockets:
        family = families[docket["family_ref"]]
        assert docket["required_constitution_sections"] == family["required_constitution_sections"]
        assert docket["required_truth_planes"] == family["required_truth_planes"]
        assert all(ref in p3_templates for ref in docket["family_axis_ratification_template_refs"])
        assert {p3_templates[ref]["family_ref"] for ref in docket["family_axis_ratification_template_refs"]} == {docket["family_ref"]}
        assert docket["selected_constitution_ref"] is None
        assert docket["status"] == "BLOCKED_BY_SOURCE_BOUNDARY_COLLISION_AND_AXIS_PREREQUISITES"

    assert collections.Counter(row["template_kind"] for row in templates) == {
        "P1B_SOURCE_AUTHORITY": len(sources),
        "P1B_CROSS_OWNER_COLLISION": len(collision_dockets),
        "P1B_BOUNDED_CONTEXT_BOUNDARY": len(boundary_dockets),
        "P1B_FAMILY_CONSTITUTION": len(family_dockets),
    }
    assert collections.Counter(row["status"] for row in templates) == {
        "READY_FOR_NAMED_AUTHORITY_REVIEW": summary["authority_review_ready_templates"],
        "BLOCKED_BY_UNRATIFIED_PREREQUISITES": summary["blocked_templates"],
    }
    for row in templates:
        assert row["required_receipt_fields"] == TEMPLATE_CONTRACTS[row["template_kind"]]["required_receipt_fields"]
        assert all(value is None for value in row["submission"].values())
        assert row["ratification_receipt_ref"] is None and row["ratification_required"]
        assert not row["canonical_mutation_allowed"] and row["canonical_gaps_closed"] == 0
        assert not row["completion_claim"]
        assert all(ref in template_by_id or ref in p3_templates for ref in row["required_prerequisite_template_refs"])

    print(f"PASS P1B foundation authority: {len(sources)} source, {len(collision_dockets)} collision, {len(boundary_dockets)} boundary and {len(family_dockets)} family decisions yield {len(templates)} exact templates; {summary['authority_review_ready_templates']} review-ready, {summary['blocked_templates']} prerequisite-blocked, 0 ratified or canonical decisions")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
