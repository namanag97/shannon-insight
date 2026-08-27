#!/usr/bin/env python3
"""Build non-ratifying family × semantic-axis applicability review packets."""
from __future__ import annotations

import argparse
import collections
import hashlib
import json
import re
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
SEM = HERE.parent
MATRICES = SEM / "applicability_matrices/family-axis-applicability-matrices.jsonl"
CLUSTERS = SEM / "applicability_matrices/family-axis-decision-clusters.jsonl"
MEMBERS = SEM / "applicability_matrices/member-preclassifications.jsonl"
EVIDENCE = SEM / "structured_projection/structured-axis-evidence.jsonl"
TARGETED_PACKAGES = SEM / "structured_projection/targeted-evidence-work-packages.jsonl"
REVIEW_WAVES = SEM / "applicability_matrices/review-waves.jsonl"
AS_OF = "2026-08-27"


REVIEW_ONTOLOGY = {
    "REVIEW_READY_UNIFORM": {
        "meaning": "One evidence-bearing candidate cluster covers the complete family-axis matrix.",
        "required_challenge": "Falsify uniformity with a library-local counterexample before ratifying a family default.",
    },
    "REVIEW_READY_MODAL_EXCEPTIONS": {
        "meaning": "A unique evidence-bearing modal cluster exists and all non-modal clusters remain explicit exception candidates.",
        "required_challenge": "Prove the family default and adjudicate every residual cluster and member exception separately.",
    },
    "BLOCKED_EVIDENCE_VACANCY": {
        "meaning": "At least one member has only generic structural context for this semantic axis.",
        "required_challenge": "Obtain targeted bounded evidence; absence of a discovery signal cannot mean inapplicable.",
    },
    "BLOCKED_NO_UNIQUE_MODAL": {
        "meaning": "The mechanical quotient has no unique modal cluster.",
        "required_challenge": "Choose a justified default, split the family, or declare that no family default exists.",
    },
}


RATIFICATION_CONTRACT = {
    "contract_id": "contract.p3.family-axis-applicability-ratification.v1",
    "edition": 1,
    "required_receipt_fields": [
        "receipt_id",
        "input_snapshot_ref",
        "input_snapshot_sha256",
        "matrix_ref",
        "family_ref",
        "semantic_axis",
        "family_default_applicability_decision",
        "default_cluster_semantic_contract_digest",
        "complete_cluster_decisions",
        "complete_member_exception_decisions",
        "negative_twin_appraisal_digest",
        "evidence_bundle_digest",
        "effective_edition",
        "authority_refs",
        "attestation_ref",
    ],
    "allowed_applicability_decisions": ["REQUIRED", "CONDITIONAL", "INAPPLICABLE", "PROHIBITED", "UNRESOLVED"],
    "refusal_conditions": [
        "input snapshot mismatch",
        "family-axis authority missing or unauthorized",
        "generic context or lexical evidence treated as semantic proof",
        "absence of signal treated as inapplicable",
        "non-modal cluster or member exception omitted",
        "negative twin or source conflict not adjudicated",
        "attestation absent, expired, revoked or unverifiable",
    ],
    "non_claims": [
        "A modal cluster is a review optimization, not a family default.",
        "A completed template is not a ratification receipt.",
        "Applicability ratification does not close an exact library contract, implementation, qualification or product gate.",
    ],
}


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def snapshot() -> dict[str, Any]:
    records = []
    for path in (MATRICES, CLUSTERS, MEMBERS, EVIDENCE, TARGETED_PACKAGES, REVIEW_WAVES):
        data = path.read_bytes()
        records.append({
            "path": str(path.relative_to(HERE.parents[6])),
            "sha256": hashlib.sha256(data).hexdigest(),
            "bytes": len(data),
            "record_count": len(load_jsonl(path)),
        })
    digest = hashlib.sha256(canonical(records).encode()).hexdigest()
    return {"snapshot_id": f"snapshot.p3-input.{digest[:16]}", "aggregate_sha256": digest, "files": records}


def classify(matrix: dict[str, Any], evidence_rows: list[dict[str, Any]]) -> str:
    if any(row["evidence_state"] == "GENERIC_STRUCTURAL_CONTEXT_ONLY_AXIS_EVIDENCE_VACANCY" for row in evidence_rows):
        return "BLOCKED_EVIDENCE_VACANCY"
    if matrix["unique_modal_cluster_ref"] is None:
        return "BLOCKED_NO_UNIQUE_MODAL"
    if matrix["candidate_cluster_count"] == 1:
        return "REVIEW_READY_UNIFORM"
    return "REVIEW_READY_MODAL_EXCEPTIONS"


def build_records() -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    snap = snapshot()
    matrices = load_jsonl(MATRICES)
    clusters = load_jsonl(CLUSTERS)
    members = load_jsonl(MEMBERS)
    evidence = load_jsonl(EVIDENCE)
    targeted = load_jsonl(TARGETED_PACKAGES)
    clusters_by_matrix: dict[tuple[str, str], list[dict[str, Any]]] = collections.defaultdict(list)
    members_by_matrix: dict[tuple[str, str], list[dict[str, Any]]] = collections.defaultdict(list)
    evidence_by_matrix: dict[tuple[str, str], list[dict[str, Any]]] = collections.defaultdict(list)
    targeted_by_matrix = {(row["family_id"], row["axis"]): row for row in targeted}
    for row in clusters:
        clusters_by_matrix[(row["family_id"], row["axis"])].append(row)
    for row in members:
        members_by_matrix[(row["family_id"], row["axis"])].append(row)
    for row in evidence:
        evidence_by_matrix[(row["family_id"], row["axis"])].append(row)

    dockets = []
    for matrix in matrices:
        key = (matrix["family_id"], matrix["axis"])
        local_clusters = sorted(clusters_by_matrix[key], key=lambda row: row["cluster_id"])
        local_members = sorted(members_by_matrix[key], key=lambda row: row["preclassification_id"])
        local_evidence = evidence_by_matrix[key]
        review_class = classify(matrix, local_evidence)
        ready = review_class.startswith("REVIEW_READY")
        modal_ref = matrix["unique_modal_cluster_ref"] if ready else None
        evidence_counts = collections.Counter(row["evidence_state"] for row in local_evidence)
        dockets.append({
            "record_kind": "family_axis_applicability_review_docket",
            "docket_id": f"docket.p3.{slug(matrix['family_id'])}.{slug(matrix['axis'])}.v1",
            "edition": 1,
            "input_snapshot_ref": snap["snapshot_id"],
            "matrix_ref": matrix["matrix_id"],
            "family_ref": matrix["family_id"],
            "semantic_axis": matrix["axis"],
            "phase": matrix["phase"],
            "constitution_ref": matrix["constitution_ref"],
            "module_ref": matrix["module_ref"],
            "review_class": review_class,
            "review_candidate_default_cluster_ref": modal_ref,
            "candidate_exception_cluster_refs": [row["cluster_id"] for row in local_clusters if row["cluster_id"] != modal_ref],
            "cluster_refs": [row["cluster_id"] for row in local_clusters],
            "member_preclassification_refs": [row["preclassification_id"] for row in local_members],
            "member_count": len(local_members),
            "evidence_state_counts": dict(sorted(evidence_counts.items())),
            "targeted_evidence_work_package_ref": targeted_by_matrix.get(key, {}).get("work_package_id"),
            "selected_family_default_decision": "UNRESOLVED",
            "ratification_receipt_ref": None,
            "ratification_required": True,
            "canonical_mutation_allowed": False,
            "canonical_gaps_closed": 0,
            "status": "READY_FOR_FAMILY_AXIS_REVIEW" if ready else "BLOCKED_REQUIRES_EVIDENCE_OR_SPLIT",
            "completion_claim": False,
        })

    packages_by_key: dict[tuple[int, str, str], list[dict[str, Any]]] = collections.defaultdict(list)
    for docket in dockets:
        packages_by_key[(docket["phase"], docket["semantic_axis"], docket["review_class"])].append(docket)
    packages = []
    for (phase, axis, review_class), local_dockets in sorted(packages_by_key.items()):
        local_dockets = sorted(local_dockets, key=lambda row: row["docket_id"])
        packages.append({
            "record_kind": "family_axis_applicability_review_package",
            "review_package_id": f"review-package.p3.phase-{phase}.{slug(axis)}.{slug(review_class)}.v1",
            "edition": 1,
            "phase": phase,
            "semantic_axis": axis,
            "review_class": review_class,
            "meaning": REVIEW_ONTOLOGY[review_class]["meaning"],
            "required_challenge": REVIEW_ONTOLOGY[review_class]["required_challenge"],
            "docket_refs": [row["docket_id"] for row in local_dockets],
            "matrix_refs": [row["matrix_ref"] for row in local_dockets],
            "family_refs": sorted({row["family_ref"] for row in local_dockets}),
            "docket_count": len(local_dockets),
            "member_count": sum(row["member_count"] for row in local_dockets),
            "decision_grain": "PER_FAMILY_AXIS_DEFAULT_PLUS_EVERY_CLUSTER_AND_MEMBER_EXCEPTION",
            "propagation_law": "Research and negative twins may be shared by package; no family inherits another family's default or exception decision.",
            "status": "OPEN_REVIEW_QUOTIENT",
            "completion_claim": False,
        })
    package_by_docket = {ref: row["review_package_id"] for row in packages for ref in row["docket_refs"]}

    templates = []
    for docket in dockets:
        ready = docket["status"] == "READY_FOR_FAMILY_AXIS_REVIEW"
        templates.append({
            "record_kind": "family_axis_applicability_ratification_template",
            "template_id": docket["docket_id"].replace("docket.p3.", "template.p3."),
            "edition": 1,
            "input_snapshot_ref": snap["snapshot_id"],
            "input_snapshot_sha256": snap["aggregate_sha256"],
            "docket_ref": docket["docket_id"],
            "review_package_ref": package_by_docket[docket["docket_id"]],
            "matrix_ref": docket["matrix_ref"],
            "family_ref": docket["family_ref"],
            "semantic_axis": docket["semantic_axis"],
            "review_candidate_default_cluster_ref": docket["review_candidate_default_cluster_ref"],
            "cluster_refs": docket["cluster_refs"],
            "member_preclassification_refs": docket["member_preclassification_refs"],
            "required_authority_roles": ["FAMILY_AXIS_SEMANTIC_AUTHORITY", "AFFECTED_LIBRARY_OWNERS"],
            "required_receipt_fields": RATIFICATION_CONTRACT["required_receipt_fields"],
            "submission": {field: None for field in RATIFICATION_CONTRACT["required_receipt_fields"] if field not in {"input_snapshot_ref", "input_snapshot_sha256", "matrix_ref", "family_ref", "semantic_axis"}},
            "ratification_receipt_ref": None,
            "ratification_required": True,
            "canonical_mutation_allowed": False,
            "canonical_gaps_closed": 0,
            "status": "READY_FOR_NAMED_AUTHORITY_REVIEW" if ready else "BLOCKED_BY_REVIEW_PACKAGE",
            "completion_claim": False,
        })
    return dockets, packages, templates, snap


def outputs() -> dict[str, str]:
    dockets, packages, templates, snap = build_records()
    status_counts = collections.Counter(row["status"] for row in dockets)
    summary = {
        "program_id": "program.p3-family-axis-applicability-adjudication.v1",
        "edition": 1,
        "as_of": AS_OF,
        "input_snapshot": snap,
        "family_axis_dockets": len(dockets),
        "represented_member_axis_cells": sum(row["member_count"] for row in dockets),
        "review_packages": len(packages),
        "ratification_packet_templates": len(templates),
        "review_ready_dockets": status_counts["READY_FOR_FAMILY_AXIS_REVIEW"],
        "blocked_dockets": status_counts["BLOCKED_REQUIRES_EVIDENCE_OR_SPLIT"],
        "authority_review_ready_templates": sum(row["status"] == "READY_FOR_NAMED_AUTHORITY_REVIEW" for row in templates),
        "ratified_family_axis_defaults": 0,
        "ratified_member_exceptions": 0,
        "canonical_exact_gaps_closed": 0,
        "completion_claim": False,
    }
    files = {
        "review-ontology.json": json.dumps(REVIEW_ONTOLOGY, sort_keys=True, indent=2) + "\n",
        "ratification-contract.json": json.dumps(RATIFICATION_CONTRACT, sort_keys=True, indent=2) + "\n",
        "family-axis-review-dockets.jsonl": "".join(canonical(row) + "\n" for row in dockets),
        "family-axis-review-packages.jsonl": "".join(canonical(row) + "\n" for row in packages),
        "family-axis-ratification-packet-templates.jsonl": "".join(canonical(row) + "\n" for row in templates),
        "summary.json": json.dumps(summary, sort_keys=True, indent=2) + "\n",
    }
    manifest = {name: {"bytes": len(text.encode()), "sha256": hashlib.sha256(text.encode()).hexdigest()} for name, text in files.items()}
    files["manifest.json"] = json.dumps({"manifest_id": "manifest.p3-applicability-adjudication.v1", "as_of": AS_OF, "files": manifest, "completion_claim": False}, sort_keys=True, indent=2) + "\n"
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
    print(f"{'CHECK' if args.check else 'BUILD'} PASS P3: {summary['family_axis_dockets']} family-axis dockets, {summary['review_packages']} review packages, {summary['review_ready_dockets']} review-ready; zero ratified defaults or canonical mutations")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
