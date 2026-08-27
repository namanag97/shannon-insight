#!/usr/bin/env python3
"""Derive one explicit product-boundary falsification contract per retained product.

This is structural research evidence, not ratification. It asks what observable evidence would
force merge, split, demotion, rehome or rejection and binds the test to the product's actual DDD.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
ADJ = ROOT / "research/product_ontology/adjudications"


def load_jsonl(path: Path):
    return [json.loads(x) for x in path.read_text(encoding="utf-8").splitlines() if x.strip()]


def main() -> int:
    readiness = load_jsonl(HERE / "product-readiness.jsonl")
    dossier_cache: dict[str, dict[str, dict]] = {}
    rows = []
    for product in readiness:
        bundle = product["adjudication_bundle"]
        dossier_ref = product["product_specific_ddd"]["dossier_ref"]
        if bundle not in dossier_cache:
            path = ADJ / bundle / "product-ddd-dossiers.jsonl"
            dossiers = load_jsonl(path)
            dossier_cache[bundle] = {row["dossier_id"]: row for row in dossiers}
        dossier = dossier_cache[bundle][dossier_ref]
        truth = dossier["product_truth"]
        ddd = dossier["strategic_and_tactical_ddd"]
        context_neighbors = sorted({x["neighbor_ref"] for x in ddd.get("context_map", [])})
        product_neighbors = [x for x in context_neighbors if x.startswith("product.") or x.startswith("candidate.product.")]
        aggregate_roots = ddd.get("aggregate_roots", [])
        commands = ddd.get("commands", [])
        events = ddd.get("domain_events", [])
        published = ddd.get("published_language", [])
        refusals = ddd.get("refusal_failure_catalog", [])
        invariants = ddd.get("aggregate_invariants", [])
        state_machine = ddd.get("state_machine", {})
        boundary = ddd.get("bounded_context_boundary", {})
        capability = product["library_and_compiler"]

        structural_survival = {
            "has_sovereign_question": bool(truth.get("sovereign_question")),
            "has_negative_mission": bool(truth.get("negative_mission")),
            "has_independent_aggregate_roots": bool(aggregate_roots),
            "has_operated_command_event_surface": bool(commands and events),
            "has_state_machine": bool(state_machine),
            "has_published_language": bool(published),
            "has_explicit_refusals": bool(refusals),
            "has_explicit_invariants": bool(invariants),
            "has_inside_outside_boundary": bool(boundary.get("inside") and boundary.get("outside")),
            "has_context_seams": bool(context_neighbors),
            "compiler_surface_fully_mapped": capability["open_structural_binding_gap_count"] == 0 and capability["uncovered_required_capability_count"] == 0,
        }
        rows.append({
            "record_kind": "product_boundary_falsification_contract",
            "falsification_id": "falsify." + product["candidate_id"].removeprefix("candidate.product."),
            "candidate_id": product["candidate_id"],
            "product_name": product["name"],
            "adjudication_bundle": bundle,
            "adjudication_decision_ref": product["adjudication_decision_id"],
            "dossier_ref": dossier_ref,
            "current_boundary_verdict": product["boundary_verdict"],
            "sovereign_question": truth["sovereign_question"],
            "negative_mission": truth["negative_mission"],
            "users": truth.get("users", []),
            "jobs": truth.get("jobs", []),
            "owned_structural_surface": {
                "aggregate_roots": aggregate_roots,
                "commands": commands,
                "domain_events": events,
                "state_machine_roots": sorted(state_machine),
                "published_language": published,
                "invariant_count": len(invariants),
                "refusal_count": len(refusals),
                "inside_boundary": boundary.get("inside", []),
                "outside_boundary": boundary.get("outside", []),
                "provided_capability_refs": capability.get("provided_capability_refs", []),
                "internally_owned_required_capability_refs": capability.get("internally_owned_required_capability_refs", []),
                "imported_provider_or_resource_requirement_refs": capability.get("imported_product_provider_or_resource_requirement_refs", []),
            },
            "candidate_merge_neighbor_refs": product_neighbors,
            "all_context_neighbor_refs": context_neighbors,
            "structural_survival_signals": structural_survival,
            "falsification_tests": [
                {
                    "disposition_if_true": "MERGE",
                    "test_id": "merge_owner_lifecycle_absorption",
                    "falsifier": "A neighboring retained product can absorb every owned aggregate root, command, event, state transition, published term and refusal without introducing a second authority, anti-corruption translation, lifecycle mismatch, adoption seam or information loss.",
                    "required_evidence": ["neighbor DDD comparison", "artifact/command/transition owner matrix", "ACL/loss comparison", "independent adoption and lifecycle evidence"],
                },
                {
                    "disposition_if_true": "SPLIT",
                    "test_id": "split_independent_lifecycles",
                    "falsifier": "The owned aggregate roots partition into two or more subsets with independent users/jobs, authorities, state machines, issue/retract/recall rules and adoption/exit seams, while cross-subset coordination is only asynchronous or imported and no invariant requires one consistency boundary.",
                    "required_evidence": ["aggregate dependency graph", "state/command matrix", "authority matrix", "invariant coupling analysis", "independent adoption evidence"],
                },
                {
                    "disposition_if_true": "DEMOTE_TO_CAPABILITY_OR_LIBRARY",
                    "test_id": "demote_no_operated_product_lifecycle",
                    "falsifier": "After removing provider/runtime details, the candidate owns no durable operated lifecycle, authority-bearing artifact, command/event surface, refusal/evidence lifecycle or independently adoptable user outcome and reduces to a pure/reusable transformation or method contract.",
                    "required_evidence": ["constructor-observer closure", "state-machine absence or eliminability", "pure-function substitution", "adoption boundary evidence"],
                },
                {
                    "disposition_if_true": "REHOME_EXTERNAL_OR_VERTICAL",
                    "test_id": "rehome_domain_authority",
                    "falsifier": "The candidate cannot state its core invariants without owning industry-specific vocabulary, business system-of-record truth, legal/domain decision authority or customer-specific policy that should remain in an application product or vertical solution pack.",
                    "required_evidence": ["two unrelated vertical substitutions", "ubiquitous-language comparison", "authority provenance", "horizontal-contract invariance test"],
                },
                {
                    "disposition_if_true": "REJECT_DUPLICATE_OR_NONPRODUCT",
                    "test_id": "reject_no_unique_sovereignty",
                    "falsifier": "No unique sovereign question, durable identity/lifecycle, authority, refusal boundary or adoption/exit seam remains after exact overlap with existing products/capabilities is removed.",
                    "required_evidence": ["global owner matrix", "semantic diff", "duplicate artifact/command detection", "adoption evidence"],
                },
            ],
            "current_structural_result": "SURVIVES_STRUCTURAL_FALSIFICATION_CANDIDATE" if all(structural_survival.values()) else "STRUCTURAL_FALSIFICATION_GAPS_PRESENT",
            "independent_adoption_evidence_state": "OPEN_PRODUCT_SPECIFIC_EVIDENCE_REQUIRED",
            "economic_and_exit_evidence_state": "OPEN_PRODUCT_SPECIFIC_EVIDENCE_REQUIRED",
            "vertical_generality_evidence_state": "EXECUTION_REQUIRED" if product["vertical_proof"]["executed_acceptance_count"] == 0 else "PARTIAL_OR_PRESENT",
            "ratification": "WITHHELD",
            "completion_claim": False,
        })

    out = HERE / "product-boundary-falsification.jsonl"
    out.write_text("".join(json.dumps(x, sort_keys=True) + "\n" for x in rows), encoding="utf-8")
    summary = {
        "report_id": "retained_product_boundary_falsification",
        "as_of": "2026-08-27",
        "completion_claim": False,
        "retained_product_count": len(readiness),
        "falsification_contract_count": len(rows),
        "structurally_surviving_candidate_count": sum(r["current_structural_result"] == "SURVIVES_STRUCTURAL_FALSIFICATION_CANDIDATE" for r in rows),
        "structural_falsification_gap_count": sum(r["current_structural_result"] != "SURVIVES_STRUCTURAL_FALSIFICATION_CANDIDATE" for r in rows),
        "product_specific_independent_adoption_evidence_complete_count": 0,
        "product_specific_economic_exit_evidence_complete_count": 0,
        "ratified_boundary_count": 0,
        "status": "FALSIFICATION_CONTRACTS_COMPLETE_EXTERNAL_EVIDENCE_AND_RATIFICATION_OPEN",
    }
    (HERE / "product-boundary-falsification-summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(summary, sort_keys=True))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
