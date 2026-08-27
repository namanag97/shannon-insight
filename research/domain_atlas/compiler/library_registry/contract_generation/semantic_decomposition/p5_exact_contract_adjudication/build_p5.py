#!/usr/bin/env python3
"""Build the exact-contract hypergraph and fail-closed lowering gates."""
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
LIBRARY_REGISTRY = CONTRACT_GENERATION.parent
EXACT_CLOSURE = LIBRARY_REGISTRY / "exact_api_closure"

CLOSURE_QUEUE = EXACT_CLOSURE / "closure-queue.jsonl"
RESEARCH_BATCHES = EXACT_CLOSURE / "research-batches.jsonl"
INSTANCE_PROPOSALS = CONTRACT_GENERATION / "library-instance-proposals.jsonl"
ARCHETYPES = CONTRACT_GENERATION / "contract-archetypes.jsonl"
FAMILY_CONSTITUTIONS = CONTRACT_GENERATION / "family-constitutions.jsonl"
BOUNDARY_CLUSTERS = CONTRACT_GENERATION / "boundary-falsification-clusters.jsonl"
COLLISIONS = CONTRACT_GENERATION / "cross-owner-collision-candidates.jsonl"
WORK_PACKAGES = CONTRACT_GENERATION / "work-packages.jsonl"
EXACT_INPUTS = SEM / "structured_projection/exact-contract-input-candidates.jsonl"
SOURCE_AUDITS = SEM / "source_authority_audit/readiness-audits.jsonl"
P1_AUTHORITY = SEM / "p1_authority_symbols/source-authority-packets.jsonl"
P2_OCCURRENCES = SEM / "p2_owner_adjudication/occurrence-relation-proposals.jsonl"
P2_TEMPLATES = SEM / "p2_owner_adjudication/owner-ratification-packet-templates.jsonl"
P3_DOCKETS = SEM / "p3_applicability_adjudication/family-axis-review-dockets.jsonl"
P3_TEMPLATES = SEM / "p3_applicability_adjudication/family-axis-ratification-packet-templates.jsonl"
P4_LEDGER = SEM / "p4_ratification_ingestion/verified-ratification-ledger.jsonl"
P1B_TEMPLATES = SEM / "p1b_foundation_authority_adjudication/ratification-packet-templates.jsonl"
DEPENDENCY_EDGES = LIBRARY_REGISTRY / "dependency-edges.jsonl"
AS_OF = "2026-08-27"


CONTRACT_DIMENSIONS = [
    "boundary_and_negative_mission",
    "semantic_owner_and_context_map",
    "ubiquitous_language_and_public_names",
    "identity_equality_and_canonicalization",
    "types_traits_operations_and_queries",
    "commands_events_state_and_time",
    "laws_invariants_and_refusal_precedence",
    "authority_policy_and_effect_boundary",
    "partiality_uncertainty_and_information_loss",
    "finite_resources_concurrency_and_cancellation",
    "representation_dto_acl_and_compatibility",
    "dependencies_features_and_removal_seams",
    "evidence_negative_twins_and_conformance",
    "platform_supply_chain_and_code_risk",
    "migration_deprecation_and_historical_replay",
]


RATIFICATION_CONTRACT = {
    "contract_id": "contract.p5.exact-library-contract-ratification.v1",
    "edition": 1,
    "required_receipt_fields": [
        "receipt_id",
        "input_snapshot_ref",
        "input_snapshot_sha256",
        "exact_contract_docket_ref",
        "library_ref",
        "boundary_disposition_receipt_ref",
        "source_authority_receipt_ref",
        "family_constitution_edition_ref",
        "family_axis_applicability_receipt_refs",
        "shared_symbol_owner_receipt_refs",
        "exact_contract_payload",
        "exact_contract_payload_digest",
        "contract_dimension_completion_map",
        "collision_adjudication_receipt_refs",
        "negative_twin_and_conformance_digest",
        "migration_plan_digest",
        "authority_refs",
        "attestation_ref",
        "effective_edition",
    ],
    "refusal_conditions": [
        "boundary, source authority or family constitution is unratified",
        "any of the sixteen semantic-axis decisions is absent or unresolved",
        "a repeated public symbol lacks a ratified owner and exact occurrence relation",
        "a cross-owner collision is unadjudicated",
        "owner-authored contract dimensions are missing or inherited from an archetype",
        "types, traits, operations, refusals, effects, bounds or oracles are partial",
        "payload is not bound to the exact input snapshot and authority attestation",
    ],
    "non_claims": [
        "An archetype supplies structural obligations, never domain semantics.",
        "A family kernel supplies reusable decisions, never library-local exceptions.",
        "A ratified exact contract is not an implementation, qualification, portability or product-acceptance receipt.",
        "This stage emits lowering candidates and never mutates the canonical registry.",
    ],
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
    paths = (
        CLOSURE_QUEUE, RESEARCH_BATCHES, INSTANCE_PROPOSALS, ARCHETYPES, FAMILY_CONSTITUTIONS,
        BOUNDARY_CLUSTERS, COLLISIONS, WORK_PACKAGES, EXACT_INPUTS, SOURCE_AUDITS, P1_AUTHORITY,
        P1B_TEMPLATES, P2_OCCURRENCES, P2_TEMPLATES, P3_DOCKETS, P3_TEMPLATES, P4_LEDGER, DEPENDENCY_EDGES,
    )
    files = []
    for path in paths:
        data = path.read_bytes()
        files.append({
            "path": str(path.relative_to(HERE.parents[6])),
            "bytes": len(data),
            "sha256": hashlib.sha256(data).hexdigest(),
            "record_count": len(load_jsonl(path)),
        })
    aggregate = digest(files)
    return {"snapshot_id": f"snapshot.p5-input.{aggregate[:16]}", "aggregate_sha256": aggregate, "files": files}


def build_records() -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    snap = snapshot()
    queue = load_jsonl(CLOSURE_QUEUE)
    batches = {row["batch_id"]: row for row in load_jsonl(RESEARCH_BATCHES)}
    proposals = {row["library_ref"]: row for row in load_jsonl(INSTANCE_PROPOSALS)}
    archetypes = {row["archetype_id"]: row for row in load_jsonl(ARCHETYPES)}
    families = {row["family_id"]: row for row in load_jsonl(FAMILY_CONSTITUTIONS)}
    boundary_rows = load_jsonl(BOUNDARY_CLUSTERS)
    collision_rows = load_jsonl(COLLISIONS)
    work_packages = {row["research_batch_ref"]: row for row in load_jsonl(WORK_PACKAGES)}
    exact_inputs = {row["library_ref"]: row for row in load_jsonl(EXACT_INPUTS)}
    source_audits = {row["family_id"]: row for row in load_jsonl(SOURCE_AUDITS)}
    authority_packets = {row["family_id"]: row for row in load_jsonl(P1_AUTHORITY)}
    p2_occurrences = load_jsonl(P2_OCCURRENCES)
    p2_templates = {row["proposal_ref"]: row for row in load_jsonl(P2_TEMPLATES)}
    p3_dockets = load_jsonl(P3_DOCKETS)
    p3_templates = {row["docket_ref"]: row for row in load_jsonl(P3_TEMPLATES)}
    verified_template_refs = {row["template_ref"] for row in load_jsonl(P4_LEDGER)}
    p1b_templates = load_jsonl(P1B_TEMPLATES)
    dependency_edges = load_jsonl(DEPENDENCY_EDGES)

    boundary_by_library = {
        library_ref: row
        for row in boundary_rows
        for library_ref in row["library_refs"]
    }
    collisions_by_library: dict[str, list[dict[str, Any]]] = collections.defaultdict(list)
    for row in collision_rows:
        collisions_by_library[row["left_library_ref"]].append(row)
        collisions_by_library[row["right_library_ref"]].append(row)
    p2_by_library: dict[str, list[dict[str, Any]]] = collections.defaultdict(list)
    for row in p2_occurrences:
        p2_by_library[row["library_ref"]].append(row)
    p3_by_family: dict[str, list[dict[str, Any]]] = collections.defaultdict(list)
    for row in p3_dockets:
        p3_by_family[row["family_ref"]].append(row)
    edges_by_library: dict[str, list[dict[str, Any]]] = collections.defaultdict(list)
    for row in dependency_edges:
        edges_by_library[row["from_ref"]].append(row)
        edges_by_library[row["to_ref"]].append(row)
    p1b_by_kind_subject = {(row["template_kind"], row["subject_ref"]): row for row in p1b_templates}

    dockets = []
    for closure in sorted(queue, key=lambda row: row["library_ref"]):
        library_ref = closure["library_ref"]
        proposal = proposals[library_ref]
        family_ref = proposal["family_id"]
        batch = batches[proposal["research_batch_ref"]]
        boundary = boundary_by_library[library_ref]
        collision_refs = sorted(row["collision_id"] for row in collisions_by_library[library_ref])
        p2_rows = sorted(p2_by_library[library_ref], key=lambda row: row["relation_proposal_id"])
        p2_template_refs = sorted({p2_templates[row["owner_proposal_ref"]]["ratification_packet_id"] for row in p2_rows})
        family_axis_dockets = sorted(p3_by_family[family_ref], key=lambda row: row["semantic_axis"])
        p3_template_refs = [p3_templates[row["docket_id"]]["template_id"] for row in family_axis_dockets]
        source_authority_template_ref = p1b_by_kind_subject[("P1B_SOURCE_AUTHORITY", family_ref)]["template_id"]
        boundary_template_ref = p1b_by_kind_subject[("P1B_BOUNDED_CONTEXT_BOUNDARY", boundary["cluster_id"])]["template_id"]
        family_constitution_template_ref = p1b_by_kind_subject[("P1B_FAMILY_CONSTITUTION", family_ref)]["template_id"]
        collision_template_refs = [p1b_by_kind_subject[("P1B_CROSS_OWNER_COLLISION", ref)]["template_id"] for ref in collision_refs]
        prerequisite_template_refs = [source_authority_template_ref, boundary_template_ref, family_constitution_template_ref] + collision_template_refs + p3_template_refs + p2_template_refs
        blockers = [
            "SOURCE_AUTHORITY_UNRATIFIED",
            "BOUNDARY_DISPOSITION_UNRATIFIED",
            "FAMILY_CONSTITUTION_INCOMPLETE",
            "FAMILY_AXIS_APPLICABILITY_UNRATIFIED",
            "OWNER_AUTHORED_CONTRACT_DIMENSIONS_INCOMPLETE",
            "EXACT_SOURCE_CONTRACT_UNPUBLISHED",
        ]
        if p2_template_refs:
            blockers.append("SHARED_SYMBOL_OWNERSHIP_UNRATIFIED")
        if collision_refs:
            blockers.append("CROSS_OWNER_COLLISION_UNADJUDICATED")
        if proposal["classification_confidence"] == "HEURISTIC_REVIEW_REQUIRED":
            blockers.append("ARCHETYPE_CLASSIFICATION_HEURISTIC")
        challenge_flags = [
            flag for flag, active in (
                ("BOUNDARY_FIRST", batch["research_lane"] == "boundary_first"),
                ("CROSS_OWNER_COLLISIONS", bool(collision_refs)),
                ("REPEATED_PUBLIC_SYMBOLS", bool(p2_template_refs)),
                ("HEURISTIC_ARCHETYPE", proposal["classification_confidence"] == "HEURISTIC_REVIEW_REQUIRED"),
                ("EFFECT_OR_PROVIDER_BOUNDARY", batch["research_lane"] == "effect_runtime_provider"),
            ) if active
        ]
        docket_id = f"docket.p5.exact-contract.{slug(library_ref)}.v1"
        dockets.append({
            "record_kind": "exact_library_contract_adjudication_docket",
            "docket_id": docket_id,
            "edition": 1,
            "input_snapshot_ref": snap["snapshot_id"],
            "library_ref": library_ref,
            "family_ref": family_ref,
            "closure_ref": closure["closure_id"],
            "source_gap_ref": closure["source_gap_ref"],
            "instance_proposal_ref": proposal["proposal_id"],
            "exact_input_candidate_ref": exact_inputs[library_ref]["contract_input_id"],
            "research_batch_ref": proposal["research_batch_ref"],
            "work_package_ref": work_packages[proposal["research_batch_ref"]]["work_package_id"],
            "research_lane": batch["research_lane"],
            "priority_band": closure["priority_band"],
            "library_class": closure["library_class"],
            "effect_boundary": closure["effect_boundary"],
            "primary_archetype_ref": proposal["primary_archetype_proposal"],
            "alternate_archetype_refs": proposal["alternate_archetype_proposals"],
            "archetype_classification_confidence": proposal["classification_confidence"],
            "boundary_cluster_ref": boundary["cluster_id"],
            "boundary_disposition": proposal["boundary_disposition"],
            "source_authority_audit_ref": source_audits[family_ref]["audit_id"],
            "source_authority_packet_ref": authority_packets[family_ref]["packet_id"],
            "source_authority_ratification_template_ref": source_authority_template_ref,
            "family_constitution_ref": family_ref,
            "family_constitution_ratification_template_ref": family_constitution_template_ref,
            "family_axis_docket_refs": [row["docket_id"] for row in family_axis_dockets],
            "family_axis_ratification_template_refs": p3_template_refs,
            "shared_symbol_occurrence_proposal_refs": [row["relation_proposal_id"] for row in p2_rows],
            "shared_symbol_ratification_template_refs": p2_template_refs,
            "cross_owner_collision_refs": collision_refs,
            "cross_owner_collision_ratification_template_refs": collision_template_refs,
            "boundary_ratification_template_ref": boundary_template_ref,
            "dependency_edge_refs": sorted(row["edge_id"] for row in edges_by_library[library_ref]),
            "contract_dimensions": CONTRACT_DIMENSIONS,
            "owner_authored_slots": proposal["owner_authored_slots"],
            "placeholder_dimensions": closure["placeholder_dimensions"],
            "currently_missing_dimensions": proposal["currently_missing_dimensions"],
            "structural_draft_digest": digest(exact_inputs[library_ref]),
            "structural_draft_is_canonical": False,
            "challenge_flags": challenge_flags,
            "blocker_kinds": blockers,
            "required_prerequisite_template_refs": prerequisite_template_refs,
            "verified_prerequisite_template_refs": sorted(ref for ref in prerequisite_template_refs if ref in verified_template_refs),
            "selected_exact_contract_ref": None,
            "ratification_receipt_ref": None,
            "canonical_mutation_allowed": False,
            "canonical_gaps_closed": 0,
            "status": "BLOCKED_EXACT_CONTRACT_LOWERING",
            "completion_claim": False,
        })

    dockets_by_archetype: dict[str, list[dict[str, Any]]] = collections.defaultdict(list)
    dockets_by_family: dict[str, list[dict[str, Any]]] = collections.defaultdict(list)
    dockets_by_batch: dict[str, list[dict[str, Any]]] = collections.defaultdict(list)
    for docket in dockets:
        dockets_by_archetype[docket["primary_archetype_ref"]].append(docket)
        dockets_by_family[docket["family_ref"]].append(docket)
        dockets_by_batch[docket["research_batch_ref"]].append(docket)

    archetype_kernels = []
    for archetype_ref, archetype in sorted(archetypes.items()):
        members = sorted(dockets_by_archetype[archetype_ref], key=lambda row: row["library_ref"])
        archetype_kernels.append({
            "record_kind": "contract_archetype_obligation_kernel",
            "kernel_id": f"kernel.p5.{slug(archetype_ref)}.v1",
            "edition": 1,
            "archetype_ref": archetype_ref,
            "docket_refs": [row["docket_id"] for row in members],
            "library_refs": [row["library_ref"] for row in members],
            "member_count": len(members),
            "required_type_roles": archetype["required_type_roles"],
            "required_operation_roles": archetype["required_operation_roles"],
            "required_refusal_roles": archetype["required_refusal_roles"],
            "required_oracle_roles": archetype["required_oracle_roles"],
            "inherited_structural_laws": archetype["inherited_structural_laws"],
            "authority_limit": "The kernel shares structural questions and law slots only; it cannot author a semantic name, default, owner, boundary, refusal precedence or library exception.",
            "status": "STRUCTURAL_OBLIGATION_QUOTIENT",
            "completion_claim": False,
        })

    family_kernels = []
    for family_ref, family in sorted(families.items()):
        members = sorted(dockets_by_family[family_ref], key=lambda row: row["library_ref"])
        axis_refs = sorted({ref for row in members for ref in row["family_axis_docket_refs"]})
        family_kernels.append({
            "record_kind": "family_semantic_contract_kernel",
            "kernel_id": f"kernel.p5.family.{slug(family_ref)}.v1",
            "edition": 1,
            "family_ref": family_ref,
            "docket_refs": [row["docket_id"] for row in members],
            "library_refs": [row["library_ref"] for row in members],
            "member_count": len(members),
            "source_authority_audit_ref": members[0]["source_authority_audit_ref"],
            "source_authority_packet_ref": members[0]["source_authority_packet_ref"],
            "family_axis_docket_refs": axis_refs,
            "research_batch_refs": sorted({row["research_batch_ref"] for row in members}),
            "constitution_sections": family["required_constitution_sections"],
            "member_shared_symbol_count": sum(bool(row["shared_symbol_ratification_template_refs"]) for row in members),
            "member_collision_count": sum(bool(row["cross_owner_collision_refs"]) for row in members),
            "authority_limit": "The family kernel may publish family decisions by exact edition; it cannot erase library-local exceptions or absorb shared-symbol ownership.",
            "status": "FAMILY_SEMANTIC_QUOTIENT_UNRATIFIED",
            "completion_claim": False,
        })

    execution_packages = []
    for batch_ref, batch in sorted(batches.items()):
        members = sorted(dockets_by_batch[batch_ref], key=lambda row: row["library_ref"])
        execution_packages.append({
            "record_kind": "exact_contract_execution_package",
            "execution_package_id": f"execution-package.p5.{slug(batch_ref)}.v1",
            "edition": 1,
            "research_batch_ref": batch_ref,
            "family_ref": members[0]["family_ref"],
            "research_lane": batch["research_lane"],
            "docket_refs": [row["docket_id"] for row in members],
            "library_refs": [row["library_ref"] for row in members],
            "docket_count": len(members),
            "archetype_kernel_refs": sorted({f"kernel.p5.{slug(row['primary_archetype_ref'])}.v1" for row in members}),
            "family_kernel_ref": f"kernel.p5.family.{slug(members[0]['family_ref'])}.v1",
            "shared_research_law": "Evidence, family decisions and archetype obligations may be authored once; every docket retains its exact boundary, owner slots, exceptions and receipt.",
            "status": "OPEN_EXECUTION_QUOTIENT",
            "completion_claim": False,
        })

    templates = []
    gates = []
    for docket in dockets:
        template_id = docket["docket_id"].replace("docket.p5.", "template.p5.")
        templates.append({
            "record_kind": "exact_library_contract_ratification_template",
            "template_id": template_id,
            "edition": 1,
            "input_snapshot_ref": snap["snapshot_id"],
            "input_snapshot_sha256": snap["aggregate_sha256"],
            "docket_ref": docket["docket_id"],
            "library_ref": docket["library_ref"],
            "family_ref": docket["family_ref"],
            "archetype_kernel_ref": f"kernel.p5.{slug(docket['primary_archetype_ref'])}.v1",
            "family_kernel_ref": f"kernel.p5.family.{slug(docket['family_ref'])}.v1",
            "execution_package_ref": f"execution-package.p5.{slug(docket['research_batch_ref'])}.v1",
            "required_prerequisite_template_refs": docket["required_prerequisite_template_refs"],
            "blocker_kinds": docket["blocker_kinds"],
            "required_receipt_fields": RATIFICATION_CONTRACT["required_receipt_fields"],
            "submission": {field: None for field in RATIFICATION_CONTRACT["required_receipt_fields"] if field not in {"input_snapshot_ref", "input_snapshot_sha256", "exact_contract_docket_ref", "library_ref"}},
            "ratification_receipt_ref": None,
            "ratification_required": True,
            "canonical_mutation_allowed": False,
            "canonical_gaps_closed": 0,
            "status": "BLOCKED_BY_UNRATIFIED_PREREQUISITES",
            "completion_claim": False,
        })
        gates.append({
            "record_kind": "exact_contract_compiler_lowering_gate",
            "gate_id": f"gate.p5.lowering.{slug(docket['library_ref'])}.v1",
            "edition": 1,
            "docket_ref": docket["docket_id"],
            "ratification_template_ref": template_id,
            "library_ref": docket["library_ref"],
            "required_source_gap_ref": docket["source_gap_ref"],
            "required_prerequisite_template_refs": docket["required_prerequisite_template_refs"],
            "verified_prerequisite_template_refs": docket["verified_prerequisite_template_refs"],
            "unresolved_blocker_kinds": docket["blocker_kinds"],
            "selected_exact_contract_ref": None,
            "lowered_contract_candidate_ref": None,
            "canonical_mutation_allowed": False,
            "canonical_gaps_closed": 0,
            "status": "REFUSE_EXACT_CONTRACT_LOWERING",
            "completion_claim": False,
        })
    return dockets, archetype_kernels, family_kernels, execution_packages, templates, gates, snap


def outputs() -> dict[str, str]:
    dockets, archetypes, families, packages, templates, gates, snap = build_records()
    summary = {
        "program_id": "program.p5-exact-contract-adjudication.v1",
        "edition": 1,
        "as_of": AS_OF,
        "input_snapshot": snap,
        "exact_contract_dockets": len(dockets),
        "archetype_obligation_kernels": len(archetypes),
        "populated_archetype_obligation_kernels": sum(row["member_count"] > 0 for row in archetypes),
        "family_semantic_kernels": len(families),
        "execution_packages": len(packages),
        "ratification_packet_templates": len(templates),
        "compiler_lowering_gates": len(gates),
        "dockets_with_shared_symbol_dependencies": sum(bool(row["shared_symbol_ratification_template_refs"]) for row in dockets),
        "dockets_with_collision_dependencies": sum(bool(row["cross_owner_collision_refs"]) for row in dockets),
        "verified_prerequisite_bindings": sum(len(row["verified_prerequisite_template_refs"]) for row in dockets),
        "ratified_exact_contracts": 0,
        "lowered_exact_contract_candidates": 0,
        "canonical_mutations_allowed": 0,
        "canonical_exact_gaps_closed": 0,
        "completion_claim": False,
    }
    files = {
        "contract-dimension-ontology.json": json.dumps({"contract_dimensions": CONTRACT_DIMENSIONS}, sort_keys=True, indent=2) + "\n",
        "ratification-contract.json": json.dumps(RATIFICATION_CONTRACT, sort_keys=True, indent=2) + "\n",
        "exact-contract-dockets.jsonl": "".join(canonical(row) + "\n" for row in dockets),
        "archetype-obligation-kernels.jsonl": "".join(canonical(row) + "\n" for row in archetypes),
        "family-semantic-kernels.jsonl": "".join(canonical(row) + "\n" for row in families),
        "execution-packages.jsonl": "".join(canonical(row) + "\n" for row in packages),
        "exact-contract-ratification-packet-templates.jsonl": "".join(canonical(row) + "\n" for row in templates),
        "compiler-lowering-gates.jsonl": "".join(canonical(row) + "\n" for row in gates),
        "summary.json": json.dumps(summary, sort_keys=True, indent=2) + "\n",
    }
    manifest = {name: {"bytes": len(text.encode()), "sha256": hashlib.sha256(text.encode()).hexdigest()} for name, text in files.items()}
    files["manifest.json"] = json.dumps({"manifest_id": "manifest.p5-exact-contract-adjudication.v1", "as_of": AS_OF, "files": manifest, "completion_claim": False}, sort_keys=True, indent=2) + "\n"
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
    print(f"{'CHECK' if args.check else 'BUILD'} PASS P5: {summary['exact_contract_dockets']} exact dockets over {summary['archetype_obligation_kernels']} archetype, {summary['family_semantic_kernels']} family and {summary['execution_packages']} execution quotients; zero lowered or canonical contracts")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
