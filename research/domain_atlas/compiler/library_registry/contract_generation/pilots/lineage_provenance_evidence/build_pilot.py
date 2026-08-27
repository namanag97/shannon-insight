#!/usr/bin/env python3
"""Materialize the first owner-reviewable family constitution pilot."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
GENERATION = HERE.parents[1]
WORKSPACE = HERE.parents[6]
UNIVERSE = WORKSPACE / "research/domain_atlas/universes/lineage_provenance_evidence"
AS_OF = "2026-08-26"
FAMILY = "constitution.family.lineage_provenance_evidence"


def rows(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def canonical(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def build() -> tuple[dict, list[dict], dict]:
    metamodel = json.loads((UNIVERSE / "metamodel.json").read_text(encoding="utf-8"))
    evaluation = json.loads((UNIVERSE / "evidence-evaluation-model.json").read_text(encoding="utf-8"))
    contexts = rows(UNIVERSE / "bounded-context-candidates.jsonl")
    proposals = [row for row in rows(GENERATION / "library-instance-proposals.jsonl") if row["family_id"] == FAMILY]
    work_item = next(row for row in rows(GENERATION / "family-constitutions.jsonl") if row["family_id"] == FAMILY)

    shared_slots = [
        "negative_mission", "identity_and_equality", "time_model", "authority_model",
        "refusal_precedence", "finite_bounds", "dependency_direction", "compatibility",
        "evidence_claims", "negative_twins", "conformance_oracles", "removal_seam",
    ]
    local_slots = [
        "sovereign_question", "semantic_owner", "inside_boundary", "outside_boundary",
        "ubiquitous_language", "decisions_and_configuration", "invariants", "refusal_catalog",
    ]
    constitution = {
        "record_kind": "family_constitution_candidate",
        "family_id": FAMILY,
        "edition": 1,
        "as_of": AS_OF,
        "status": "OWNER_REVIEW_REQUIRED_NOT_CANONICAL",
        "vision_and_negative_mission": {
            "vision": "Represent how exact data, claims, processes, evidence and effects came to be and what scoped reliance they can support.",
            "negative_mission": [
                "does not decide business truth", "does not manufacture authority", "does not equate integrity with truth",
                "does not equate provenance reachability with causation or confirmed impact", "does not execute disclosed retained corrected recalled or deleted effects",
            ],
        },
        "bounded_contexts": [{"context_ref": row["context_id"], "name": row["name"], "inside": row["inside"], "outside": row["outside"]} for row in contexts],
        "shared_distinctions": metamodel["distinction_matrix"],
        "open_world_law": metamodel["open_world_law"],
        "time_model": {"axes": metamodel["time_axes"], "freshness": evaluation["freshness_model"]},
        "roles_and_authority": {"roles": evaluation["roles"], "authority_dimensions": evaluation["authority_dimensions"]},
        "evidence_strength_dimensions": evaluation["strength_dimensions"],
        "defeater_model": evaluation["defeater_model"],
        "forbidden_inferences": sorted(set(metamodel["forbidden_automatic_inferences"] + evaluation["non_inferences"])),
        "shared_dependency_direction": [
            "representation identity and time carriers are imported from their semantic owners",
            "propositions precede issuer assertions; assertions precede evidence binding; evidence binding precedes appraisal",
            "authority status freshness integrity and custody are independent imported witnesses",
            "policy evaluation may form effect intents; qualified adapters execute; observations and receipts return inward",
            "product and provider layers package or implement these meanings but never own them",
        ],
        "shared_refusal_precedence": [
            "identity scope and edition failures precede semantic evaluation",
            "authority and validity failures precede policy aggregation",
            "integrity and binding failures precede evidence sufficiency",
            "blocking defeaters and coverage gaps precede reliance recommendations",
            "resource exhaustion refuses rather than silently weakening evidence or guarantees",
        ],
        "finite_bounds": ["explicit graph or collection cut", "finite traversal or evaluation budget", "bounded output and diagnostics", "no ambient clock network filesystem randomness identity policy or mutable global state in pure contracts"],
        "compatibility_dimensions": ["semantic edition", "identity/equality", "behavior", "policy", "evidence validity", "wire representation", "ABI", "target", "feature graph"],
        "evidence_program": work_item["evidence_program"],
        "evidence_seed_status": work_item["evidence_seed_status"],
        "evidence_refs": evaluation["evidence_refs"],
        "shared_negative_twin_classes": [
            "assertion_vs_attestation", "attestation_vs_independent_appraisal", "integrity_vs_truth",
            "recording_time_vs_validity", "prospective_vs_observed_lineage", "logical_vs_physical_vs_runtime_lineage",
            "audit_log_vs_provenance_graph", "bundle_membership_vs_endorsement", "receipt_vs_acceptance",
            "omission_vs_absence", "retraction_vs_deletion_vs_recall", "reachability_vs_confirmed_impact",
        ],
        "shared_conformance_classes": ["positive fixtures", "negative twins", "property laws", "state models", "fuzz and malformed inputs", "resource boundaries", "cross-implementation differential"],
        "shared_slot_coverage": shared_slots,
        "library_local_slots": local_slots,
        "non_authority_law": "This candidate factors repeated review obligations; every library owner must affirm applicability and publish library-specific semantics before any canonical gap closes.",
    }

    coverage = []
    for proposal in proposals:
        coverage.append({
            "record_kind": "family_constitution_instance_coverage",
            "coverage_id": "coverage.family-pilot." + proposal["library_ref"].removeprefix("library."),
            "edition": 1,
            "status": "OWNER_ATTESTATION_REQUIRED",
            "library_ref": proposal["library_ref"],
            "archetype_proposal": proposal["primary_archetype_proposal"],
            "family_shared_slots": shared_slots,
            "library_local_slots": local_slots,
            "applicability_attestation": "UNRESOLVED",
            "boundary_disposition": proposal["boundary_disposition"],
            "canonical_gap_closed": False,
        })

    total_naive = len(proposals) * len(proposals[0]["owner_authored_slots"])
    shared_review_units = len(shared_slots)
    local_review_units = len(proposals) * (len(local_slots) + 1)
    summary = {
        "pilot_id": "pilot.contract-generation.lineage-provenance-evidence.v1",
        "edition": 1, "as_of": AS_OF, "status": "ACTIVE_INCOMPLETE", "completion_claim": False,
        "open_library_instances": len(proposals), "family_shared_slots": len(shared_slots),
        "library_local_slots": len(local_slots), "naive_repeated_slot_reviews": total_naive,
        "factored_review_units_before_exceptions": shared_review_units + local_review_units,
        "projected_repeated_review_reduction": total_naive - (shared_review_units + local_review_units),
        "canonical_exact_gaps_closed": 0,
        "measurement_law": "Reduction counts factored review units only; it is not evidence that a shared rule applies to a library until its owner attests applicability.",
    }
    return constitution, coverage, summary


def outputs() -> dict[str, str]:
    constitution, coverage, summary = build()
    files = {
        "family-constitution-candidate.json": json.dumps(constitution, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
        "instance-coverage.jsonl": "".join(canonical(row) + "\n" for row in coverage),
        "summary.json": json.dumps(summary, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
    }
    file_claims = {name: {"sha256": hashlib.sha256(text.encode()).hexdigest(), "bytes": len(text.encode())} for name, text in files.items()}
    files["manifest.json"] = json.dumps({"manifest_id": "manifest.contract-generation-lpe-pilot.v1", "as_of": AS_OF, "files": file_claims}, sort_keys=True, indent=2) + "\n"
    return files


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    stale = []
    for name, text in outputs().items():
        path = HERE / name
        if args.check:
            if not path.is_file() or path.read_text(encoding="utf-8") != text:
                stale.append(name)
        else:
            path.write_text(text, encoding="utf-8")
    if stale:
        print("STALE " + ", ".join(stale))
        return 1
    _, coverage, summary = build()
    print(f"{'CHECK' if args.check else 'BUILD'} PASS LPE family pilot: {len(coverage)} instances, {summary['projected_repeated_review_reduction']} repeated review units factored, 0 canonical gaps closed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
