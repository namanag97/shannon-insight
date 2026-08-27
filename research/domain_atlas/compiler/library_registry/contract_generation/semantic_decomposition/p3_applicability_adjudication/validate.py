#!/usr/bin/env python3
"""Validate P3 review compression without ratifying applicability."""
from __future__ import annotations

import collections
import hashlib
import json

from build_p3 import (
    CLUSTERS,
    EVIDENCE,
    HERE,
    MATRICES,
    MEMBERS,
    RATIFICATION_CONTRACT,
    REVIEW_ONTOLOGY,
    TARGETED_PACKAGES,
    classify,
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
    dockets = load_jsonl(HERE / "family-axis-review-dockets.jsonl")
    packages = load_jsonl(HERE / "family-axis-review-packages.jsonl")
    templates = load_jsonl(HERE / "family-axis-ratification-packet-templates.jsonl")
    matrices = load_jsonl(MATRICES)
    clusters = load_jsonl(CLUSTERS)
    members = load_jsonl(MEMBERS)
    evidence = load_jsonl(EVIDENCE)
    targeted = load_jsonl(TARGETED_PACKAGES)

    assert len(dockets) == summary["family_axis_dockets"] == len(matrices) == 368
    assert len(packages) == summary["review_packages"] == 33
    assert len(templates) == summary["ratification_packet_templates"] == 368
    assert summary["represented_member_axis_cells"] == len(members) == 10784
    assert summary["review_ready_dockets"] == summary["authority_review_ready_templates"] == 258
    assert summary["blocked_dockets"] == 110
    assert summary["ratified_family_axis_defaults"] == summary["ratified_member_exceptions"] == 0
    assert summary["canonical_exact_gaps_closed"] == 0 and not summary["completion_claim"]

    for claim in summary["input_snapshot"]["files"]:
        path = HERE.parents[6] / claim["path"]
        data = path.read_bytes()
        assert len(data) == claim["bytes"]
        assert hashlib.sha256(data).hexdigest() == claim["sha256"]
        assert len(load_jsonl(path)) == claim["record_count"]

    matrix_by_id = {row["matrix_id"]: row for row in matrices}
    cluster_by_id = {row["cluster_id"]: row for row in clusters}
    member_by_id = {row["preclassification_id"]: row for row in members}
    evidence_by_matrix: dict[tuple[str, str], list[dict]] = collections.defaultdict(list)
    for row in evidence:
        evidence_by_matrix[(row["family_id"], row["axis"])].append(row)
    targeted_ids = {row["work_package_id"] for row in targeted}
    docket_by_id = {row["docket_id"]: row for row in dockets}
    assert len(matrix_by_id) == len(matrices)
    assert len(cluster_by_id) == len(clusters) == 1300
    assert len(member_by_id) == len(members)
    assert len(docket_by_id) == len(dockets)
    assert {row["matrix_ref"] for row in dockets} == set(matrix_by_id)
    assert collections.Counter(row["review_class"] for row in dockets) == {
        "REVIEW_READY_MODAL_EXCEPTIONS": 204,
        "BLOCKED_EVIDENCE_VACANCY": 103,
        "REVIEW_READY_UNIFORM": 54,
        "BLOCKED_NO_UNIQUE_MODAL": 7,
    }

    docket_cluster_refs = [ref for row in dockets for ref in row["cluster_refs"]]
    docket_member_refs = [ref for row in dockets for ref in row["member_preclassification_refs"]]
    assert len(docket_cluster_refs) == len(set(docket_cluster_refs)) == len(clusters)
    assert set(docket_cluster_refs) == set(cluster_by_id)
    assert len(docket_member_refs) == len(set(docket_member_refs)) == len(members)
    assert set(docket_member_refs) == set(member_by_id)

    for docket in dockets:
        matrix = matrix_by_id[docket["matrix_ref"]]
        key = (docket["family_ref"], docket["semantic_axis"])
        local_evidence = evidence_by_matrix[key]
        assert docket["review_class"] == classify(matrix, local_evidence)
        assert docket["review_class"] in REVIEW_ONTOLOGY
        assert docket["member_count"] == len(docket["member_preclassification_refs"])
        assert docket["member_count"] == matrix["library_count"]
        assert collections.Counter(row["evidence_state"] for row in local_evidence) == docket["evidence_state_counts"]
        assert all(cluster_by_id[ref]["family_id"] == docket["family_ref"] for ref in docket["cluster_refs"])
        assert all(cluster_by_id[ref]["axis"] == docket["semantic_axis"] for ref in docket["cluster_refs"])
        assert all(member_by_id[ref]["family_id"] == docket["family_ref"] for ref in docket["member_preclassification_refs"])
        assert all(member_by_id[ref]["axis"] == docket["semantic_axis"] for ref in docket["member_preclassification_refs"])
        assert docket["targeted_evidence_work_package_ref"] is None or docket["targeted_evidence_work_package_ref"] in targeted_ids
        assert docket["selected_family_default_decision"] == "UNRESOLVED"
        assert docket["ratification_receipt_ref"] is None and docket["ratification_required"]
        assert not docket["canonical_mutation_allowed"] and docket["canonical_gaps_closed"] == 0
        assert not docket["completion_claim"]
        if docket["review_class"].startswith("REVIEW_READY"):
            assert docket["status"] == "READY_FOR_FAMILY_AXIS_REVIEW"
            assert docket["review_candidate_default_cluster_ref"] == matrix["unique_modal_cluster_ref"]
            assert docket["review_candidate_default_cluster_ref"] in docket["cluster_refs"]
        else:
            assert docket["status"] == "BLOCKED_REQUIRES_EVIDENCE_OR_SPLIT"
            assert docket["review_candidate_default_cluster_ref"] is None

    package_docket_refs = [ref for row in packages for ref in row["docket_refs"]]
    assert len(package_docket_refs) == len(set(package_docket_refs)) == len(dockets)
    assert set(package_docket_refs) == set(docket_by_id)
    assert sum(row["docket_count"] for row in packages) == len(dockets)
    assert sum(row["member_count"] for row in packages) == len(members)
    assert len({(row["phase"], row["semantic_axis"], row["review_class"]) for row in packages}) == len(packages)
    package_ids = {row["review_package_id"] for row in packages}
    for package in packages:
        assert package["review_class"] in REVIEW_ONTOLOGY
        assert package["decision_grain"] == "PER_FAMILY_AXIS_DEFAULT_PLUS_EVERY_CLUSTER_AND_MEMBER_EXCEPTION"
        assert package["status"] == "OPEN_REVIEW_QUOTIENT" and not package["completion_claim"]
        for docket_ref in package["docket_refs"]:
            docket = docket_by_id[docket_ref]
            assert (docket["phase"], docket["semantic_axis"], docket["review_class"]) == (
                package["phase"], package["semantic_axis"], package["review_class"]
            )

    template_by_docket = {row["docket_ref"]: row for row in templates}
    assert len(template_by_docket) == len(templates) == len(dockets)
    assert set(template_by_docket) == set(docket_by_id)
    assert collections.Counter(row["status"] for row in templates) == {
        "READY_FOR_NAMED_AUTHORITY_REVIEW": 258,
        "BLOCKED_BY_REVIEW_PACKAGE": 110,
    }
    for docket_id, template in template_by_docket.items():
        docket = docket_by_id[docket_id]
        assert template["review_package_ref"] in package_ids
        assert template["matrix_ref"] == docket["matrix_ref"]
        assert template["family_ref"] == docket["family_ref"]
        assert template["semantic_axis"] == docket["semantic_axis"]
        assert template["cluster_refs"] == docket["cluster_refs"]
        assert template["member_preclassification_refs"] == docket["member_preclassification_refs"]
        assert template["required_receipt_fields"] == RATIFICATION_CONTRACT["required_receipt_fields"]
        assert all(value is None for value in template["submission"].values())
        assert template["ratification_receipt_ref"] is None and template["ratification_required"]
        assert not template["canonical_mutation_allowed"] and template["canonical_gaps_closed"] == 0
        assert not template["completion_claim"]
        expected_status = "READY_FOR_NAMED_AUTHORITY_REVIEW" if docket["status"] == "READY_FOR_FAMILY_AXIS_REVIEW" else "BLOCKED_BY_REVIEW_PACKAGE"
        assert template["status"] == expected_status

    print("PASS P3 applicability adjudication: 10,784 member-axis cells remain exact in 368 dockets; 258 are review-ready, 110 blocked, all factor losslessly into 33 semantic-axis review packages; 0 ratified defaults or canonical mutations")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
