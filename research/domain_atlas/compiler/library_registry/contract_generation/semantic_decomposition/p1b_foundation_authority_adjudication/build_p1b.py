#!/usr/bin/env python3
"""Build ratification surfaces for source, boundary, collision and family authority."""
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
CONTRACT_GENERATION = SEM.parent
AUTHORITY_PACKETS = SEM / "p1_authority_symbols/source-authority-packets.jsonl"
SOURCE_AUDITS = SEM / "source_authority_audit/readiness-audits.jsonl"
BOUNDARY_CLUSTERS = CONTRACT_GENERATION / "boundary-falsification-clusters.jsonl"
COLLISIONS = CONTRACT_GENERATION / "cross-owner-collision-candidates.jsonl"
FAMILY_CONSTITUTIONS = CONTRACT_GENERATION / "family-constitutions.jsonl"
P3_TEMPLATES = SEM / "p3_applicability_adjudication/family-axis-ratification-packet-templates.jsonl"
AS_OF = "2026-08-27"


TEMPLATE_CONTRACTS = {
    "P1B_SOURCE_AUTHORITY": {
        "required_receipt_fields": [
            "receipt_id", "input_snapshot_ref", "input_snapshot_sha256", "subject_ref",
            "source_authority_decision", "authority_scope", "source_schema_digest",
            "conflict_appraisal_digest", "authority_refs", "attestation_ref", "effective_edition",
        ],
        "refusals": ["source snapshot mismatch", "authority scope ambiguous", "conflicting sources unadjudicated", "structural validator treated as semantic authority"],
    },
    "P1B_CROSS_OWNER_COLLISION": {
        "required_receipt_fields": [
            "receipt_id", "input_snapshot_ref", "input_snapshot_sha256", "subject_ref",
            "collision_disposition", "left_owner_decision", "right_owner_decision",
            "meaning_law_lifecycle_comparison_digest", "migration_or_coexistence_plan_digest",
            "authority_refs", "attestation_ref", "effective_edition",
        ],
        "refusals": ["lexical similarity treated as duplicate proof", "one owner decides for another", "meaning/law/lifecycle comparison missing", "permanent compatibility alias required"],
    },
    "P1B_BOUNDED_CONTEXT_BOUNDARY": {
        "required_receipt_fields": [
            "receipt_id", "input_snapshot_ref", "input_snapshot_sha256", "subject_ref",
            "boundary_disposition", "semantic_owner_ref", "sovereign_question",
            "negative_mission", "inside_boundary", "outside_boundary", "owned_meanings",
            "excluded_meanings", "dependency_direction", "collision_receipt_bindings",
            "authority_refs", "attestation_ref", "effective_edition",
        ],
        "refusals": ["semantic owner unresolved", "inside/outside or negative mission missing", "collision prerequisite unratified", "package/team/deployment treated as domain boundary"],
    },
    "P1B_FAMILY_CONSTITUTION": {
        "required_receipt_fields": [
            "receipt_id", "input_snapshot_ref", "input_snapshot_sha256", "subject_ref",
            "constitution_section_payload", "source_authority_receipt_ref",
            "boundary_receipt_bindings", "collision_receipt_bindings",
            "family_axis_receipt_bindings", "negative_twin_appraisal_digest",
            "authority_refs", "attestation_ref", "effective_edition",
        ],
        "refusals": ["source authority unratified", "member boundary or collision unresolved", "sixteen-axis decision set incomplete", "library-local exception erased by family default"],
    },
}


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
    for path in (AUTHORITY_PACKETS, SOURCE_AUDITS, BOUNDARY_CLUSTERS, COLLISIONS, FAMILY_CONSTITUTIONS, P3_TEMPLATES):
        data = path.read_bytes()
        files.append({
            "path": str(path.relative_to(HERE.parents[6])),
            "bytes": len(data),
            "sha256": hashlib.sha256(data).hexdigest(),
            "record_count": len(load_jsonl(path)),
        })
    aggregate = digest(files)
    return {"snapshot_id": f"snapshot.p1b-input.{aggregate[:16]}", "aggregate_sha256": aggregate, "files": files}


def template(
    snap: dict[str, Any],
    template_kind: str,
    template_id: str,
    docket_ref: str,
    subject_ref: str,
    prerequisite_refs: list[str],
    status: str,
) -> dict[str, Any]:
    contract = TEMPLATE_CONTRACTS[template_kind]
    return {
        "record_kind": "foundation_authority_ratification_template",
        "template_id": template_id,
        "template_kind": template_kind,
        "edition": 1,
        "input_snapshot_ref": snap["snapshot_id"],
        "input_snapshot_sha256": snap["aggregate_sha256"],
        "docket_ref": docket_ref,
        "subject_ref": subject_ref,
        "required_prerequisite_template_refs": prerequisite_refs,
        "required_receipt_fields": contract["required_receipt_fields"],
        "refusal_conditions": contract["refusals"],
        "submission": {field: None for field in contract["required_receipt_fields"] if field not in {"input_snapshot_ref", "input_snapshot_sha256", "subject_ref"}},
        "ratification_receipt_ref": None,
        "ratification_required": True,
        "canonical_mutation_allowed": False,
        "canonical_gaps_closed": 0,
        "status": status,
        "completion_claim": False,
    }


def build_records() -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    snap = snapshot()
    packets = {row["family_id"]: row for row in load_jsonl(AUTHORITY_PACKETS)}
    audits = {row["family_id"]: row for row in load_jsonl(SOURCE_AUDITS)}
    boundaries = load_jsonl(BOUNDARY_CLUSTERS)
    collisions = load_jsonl(COLLISIONS)
    families = {row["family_id"]: row for row in load_jsonl(FAMILY_CONSTITUTIONS)}
    p3_by_family: dict[str, list[dict[str, Any]]] = collections.defaultdict(list)
    for row in load_jsonl(P3_TEMPLATES):
        p3_by_family[row["family_ref"]].append(row)

    collision_by_library: dict[str, list[dict[str, Any]]] = collections.defaultdict(list)
    collisions_by_family: dict[str, list[dict[str, Any]]] = collections.defaultdict(list)
    for row in collisions:
        collision_by_library[row["left_library_ref"]].append(row)
        collision_by_library[row["right_library_ref"]].append(row)
        collisions_by_family[row["family_id"]].append(row)
    boundaries_by_family: dict[str, list[dict[str, Any]]] = collections.defaultdict(list)
    for row in boundaries:
        boundaries_by_family[row["family_id"]].append(row)

    source_dockets = []
    collision_dockets = []
    boundary_dockets = []
    family_dockets = []
    templates = []

    for family_ref, packet in sorted(packets.items()):
        audit = audits[family_ref]
        docket_id = f"docket.p1b.source-authority.{slug(family_ref)}.v1"
        template_id = f"template.p1b.source-authority.{slug(family_ref)}.v1"
        source_dockets.append({
            "record_kind": "source_authority_ratification_docket",
            "docket_id": docket_id,
            "edition": 1,
            "family_ref": family_ref,
            "authority_packet_ref": packet["packet_id"],
            "readiness_audit_ref": audit["audit_id"],
            "source_path": packet["source_path"],
            "source_digest": packet["source_digest"],
            "library_refs": packet["library_refs"],
            "structural_readiness": packet["structural_readiness"],
            "selected_authority_decision": "UNRESOLVED",
            "ratification_template_ref": template_id,
            "ratification_receipt_ref": None,
            "status": "READY_FOR_NAMED_AUTHORITY_REVIEW",
            "completion_claim": False,
        })
        templates.append(template(snap, "P1B_SOURCE_AUTHORITY", template_id, docket_id, family_ref, [], "READY_FOR_NAMED_AUTHORITY_REVIEW"))

    for row in sorted(collisions, key=lambda item: item["collision_id"]):
        docket_id = f"docket.p1b.collision.{slug(row['collision_id'])}.v1"
        template_id = f"template.p1b.collision.{slug(row['collision_id'])}.v1"
        collision_dockets.append({
            "record_kind": "cross_owner_collision_ratification_docket",
            "docket_id": docket_id,
            "edition": 1,
            "collision_ref": row["collision_id"],
            "family_ref": row["family_id"],
            "left_library_ref": row["left_library_ref"],
            "right_library_ref": row["right_library_ref"],
            "left_owner_refs": row["left_owner_refs"],
            "right_owner_refs": row["right_owner_refs"],
            "required_adjudication": row["required_adjudication"],
            "selected_collision_disposition": "UNRESOLVED",
            "ratification_template_ref": template_id,
            "ratification_receipt_ref": None,
            "status": "READY_FOR_CONTEXT_OWNER_REVIEW",
            "completion_claim": False,
        })
        templates.append(template(snap, "P1B_CROSS_OWNER_COLLISION", template_id, docket_id, row["collision_id"], [], "READY_FOR_NAMED_AUTHORITY_REVIEW"))

    boundary_template_by_cluster = {}
    for row in sorted(boundaries, key=lambda item: item["cluster_id"]):
        collision_refs = sorted({collision["collision_id"] for library_ref in row["library_refs"] for collision in collision_by_library[library_ref]})
        prerequisite_refs = [f"template.p1b.collision.{slug(ref)}.v1" for ref in collision_refs]
        docket_id = f"docket.p1b.boundary.{slug(row['cluster_id'])}.v1"
        template_id = f"template.p1b.boundary.{slug(row['cluster_id'])}.v1"
        boundary_template_by_cluster[row["cluster_id"]] = template_id
        ready = not prerequisite_refs
        boundary_dockets.append({
            "record_kind": "bounded_context_boundary_ratification_docket",
            "docket_id": docket_id,
            "edition": 1,
            "boundary_cluster_ref": row["cluster_id"],
            "family_ref": row["family_id"],
            "semantic_owner_ref": row["semantic_owner_ref"],
            "library_refs": row["library_refs"],
            "collision_docket_refs": [f"docket.p1b.collision.{slug(ref)}.v1" for ref in collision_refs],
            "collision_ratification_template_refs": prerequisite_refs,
            "selected_boundary_disposition": "UNRESOLVED",
            "ratification_template_ref": template_id,
            "ratification_receipt_ref": None,
            "status": "READY_FOR_SEMANTIC_OWNER_REVIEW" if ready else "BLOCKED_BY_COLLISION_ADJUDICATION",
            "completion_claim": False,
        })
        templates.append(template(snap, "P1B_BOUNDED_CONTEXT_BOUNDARY", template_id, docket_id, row["cluster_id"], prerequisite_refs, "READY_FOR_NAMED_AUTHORITY_REVIEW" if ready else "BLOCKED_BY_UNRATIFIED_PREREQUISITES"))

    for family_ref, family in sorted(families.items()):
        source_template_ref = f"template.p1b.source-authority.{slug(family_ref)}.v1"
        boundary_refs = [boundary_template_by_cluster[row["cluster_id"]] for row in sorted(boundaries_by_family[family_ref], key=lambda item: item["cluster_id"])]
        collision_refs = [f"template.p1b.collision.{slug(row['collision_id'])}.v1" for row in sorted(collisions_by_family[family_ref], key=lambda item: item["collision_id"])]
        axis_refs = [row["template_id"] for row in sorted(p3_by_family[family_ref], key=lambda item: item["semantic_axis"])]
        prerequisites = [source_template_ref] + boundary_refs + collision_refs + axis_refs
        docket_id = f"docket.p1b.family-constitution.{slug(family_ref)}.v1"
        template_id = f"template.p1b.family-constitution.{slug(family_ref)}.v1"
        family_dockets.append({
            "record_kind": "family_constitution_ratification_docket",
            "docket_id": docket_id,
            "edition": 1,
            "family_ref": family_ref,
            "source_authority_template_ref": source_template_ref,
            "boundary_ratification_template_refs": boundary_refs,
            "collision_ratification_template_refs": collision_refs,
            "family_axis_ratification_template_refs": axis_refs,
            "required_constitution_sections": family["required_constitution_sections"],
            "required_truth_planes": family["required_truth_planes"],
            "selected_constitution_ref": None,
            "ratification_template_ref": template_id,
            "ratification_receipt_ref": None,
            "status": "BLOCKED_BY_SOURCE_BOUNDARY_COLLISION_AND_AXIS_PREREQUISITES",
            "completion_claim": False,
        })
        templates.append(template(snap, "P1B_FAMILY_CONSTITUTION", template_id, docket_id, family_ref, prerequisites, "BLOCKED_BY_UNRATIFIED_PREREQUISITES"))

    return source_dockets, collision_dockets, boundary_dockets, family_dockets, templates, snap


def outputs() -> dict[str, str]:
    sources, collisions, boundaries, families, templates, snap = build_records()
    summary = {
        "program_id": "program.p1b-foundation-authority-adjudication.v1",
        "edition": 1,
        "as_of": AS_OF,
        "input_snapshot": snap,
        "source_authority_dockets": len(sources),
        "collision_dockets": len(collisions),
        "boundary_dockets": len(boundaries),
        "boundary_dockets_ready": sum(row["status"] == "READY_FOR_SEMANTIC_OWNER_REVIEW" for row in boundaries),
        "boundary_dockets_blocked": sum(row["status"] == "BLOCKED_BY_COLLISION_ADJUDICATION" for row in boundaries),
        "family_constitution_dockets": len(families),
        "ratification_packet_templates": len(templates),
        "authority_review_ready_templates": sum(row["status"] == "READY_FOR_NAMED_AUTHORITY_REVIEW" for row in templates),
        "blocked_templates": sum(row["status"] != "READY_FOR_NAMED_AUTHORITY_REVIEW" for row in templates),
        "ratified_decisions": 0,
        "canonical_mutations_allowed": 0,
        "canonical_gaps_closed": 0,
        "completion_claim": False,
    }
    files = {
        "template-contracts.json": json.dumps(TEMPLATE_CONTRACTS, sort_keys=True, indent=2) + "\n",
        "source-authority-dockets.jsonl": "".join(canonical(row) + "\n" for row in sources),
        "collision-dockets.jsonl": "".join(canonical(row) + "\n" for row in collisions),
        "boundary-dockets.jsonl": "".join(canonical(row) + "\n" for row in boundaries),
        "family-constitution-dockets.jsonl": "".join(canonical(row) + "\n" for row in families),
        "ratification-packet-templates.jsonl": "".join(canonical(row) + "\n" for row in templates),
        "summary.json": json.dumps(summary, sort_keys=True, indent=2) + "\n",
    }
    manifest = {name: {"bytes": len(text.encode()), "sha256": hashlib.sha256(text.encode()).hexdigest()} for name, text in files.items()}
    files["manifest.json"] = json.dumps({"manifest_id": "manifest.p1b-foundation-authority-adjudication.v1", "as_of": AS_OF, "files": manifest, "completion_claim": False}, sort_keys=True, indent=2) + "\n"
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
    print(f"{'CHECK' if args.check else 'BUILD'} PASS P1B: {summary['source_authority_dockets']} source, {summary['collision_dockets']} collision, {summary['boundary_dockets']} boundary and {summary['family_constitution_dockets']} family dockets; {summary['authority_review_ready_templates']} templates review-ready, zero ratified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
