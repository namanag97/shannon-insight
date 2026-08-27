#!/usr/bin/env python3
"""Build a lossless closure cockpit and the first ratifier-ready decision batch."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
REBASE = ROOT / "research/product_ontology/research_convergence_rebase"
GPT = ROOT / "research/handoffs/gpt-pro-product-ontology-convergence/output-2026-08-27"
P1 = ROOT / "research/domain_atlas/compiler/library_registry/contract_generation/semantic_decomposition/p1_authority_symbols"


def load(path):
    return [json.loads(line) for line in Path(path).read_text().splitlines() if line.strip()]


def write(path, records):
    Path(path).write_text("".join(json.dumps(row, sort_keys=True) + "\n" for row in records))


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    rebased = [
        row for row in load(REBASE / "rebased-gap-dispositions.jsonl")
        if row.get("research_addressable") is True
    ]
    physical = load(REBASE / "physical-governance-gate-deltas.jsonl")
    resolutions = {row["family_ref"]: row for row in load(GPT / "source-authority-resolutions.jsonl")}
    packets = {row["family_id"]: row for row in load(P1 / "source-authority-packets.jsonl")}
    sources = {row["source_id"] for row in load(GPT / "source-register.jsonl")}

    order = [
        ("source-authority", "P01", "named source/schema authority ratification"),
        ("researched-symbol-owner", "P02A", "named semantic-owner ratification"),
        ("symbol-owner-adjudication-batch", "P02B", "collision/challenge adjudication and owner ratification"),
        ("family-axis-evidence", "P03", "member applicability appraisal and owner ratification"),
        ("applicability", "P04", "family-axis applicability ratification"),
        ("exact-contract", "P05", "exact public contract ratification"),
        ("implementation", "P06A", "implementation plus executable-oracle receipts"),
        ("qualification", "P06B", "two independent conformance qualifications"),
        ("product-gate", "P07", "product build, offer, appraisal and vertical acceptance receipts"),
    ]
    all_rows = rebased + physical
    tranches = []
    for gap_kind, tranche_id, closure in order:
        rows = [row for row in all_rows if row["gap_kind"] == gap_kind]
        tranches.append({
            "tranche_id": tranche_id,
            "gap_kind": gap_kind,
            "quotient_count": len(rows),
            "atom_count": sum(row["current_atom_count"] for row in rows),
            "closure_condition": closure,
            "research_only_can_finish": gap_kind not in {"implementation", "qualification", "product-gate"},
            "status": "IN_PROGRESS" if gap_kind == "source-authority" else "BLOCKED_BY_PREDECESSOR",
            "completion_claim": False,
        })

    appraisals = []
    for family, resolution in sorted(resolutions.items()):
        packet = packets[family]
        source_path = ROOT / resolution["input_source_path"]
        unresolved_refs = sorted(set(resolution["source_refs"]) - sources)
        checks = {
            "current_source_digest_matches": sha(source_path) == resolution["input_source_digest"] == packet["source_digest"],
            "packet_identity_matches": resolution["input_packet_ref"] == packet["packet_id"],
            "library_count_matches": resolution["library_count"] == packet["library_count"],
            "all_evidence_refs_resolve": not unresolved_refs,
            "bounded_rationale_present": bool(resolution["bounded_rationale"]),
            "negative_twin_present": bool(resolution["counterexample_or_negative_twin"]),
            "invalidation_condition_present": bool(resolution["invalidation_condition"]),
            "canonical_completion_not_claimed": resolution["completion_claim"] is False,
        }
        appraisals.append({
            "appraisal_id": "appraisal.precheck." + family.removeprefix("constitution.family."),
            "family_ref": family,
            "packet_ref": packet["packet_id"],
            "proposed_decision": resolution["adoption_decision"],
            "checks": checks,
            "unresolved_evidence_refs": unresolved_refs,
            "ratifier_payload": {
                "source_digest": resolution["input_source_digest"],
                "bounded_rationale": resolution["bounded_rationale"],
                "record_level_rule": resolution["record_level_rule"],
                "rejected_inferences": resolution["rejected_inferences"],
                "source_refs": resolution["source_refs"],
                "invalidation_condition": resolution["invalidation_condition"],
            },
            "status": "READY_FOR_NAMED_RATIFIER_REVIEW" if all(checks.values()) else "PRECHECK_REFUSED",
            "canonical_gaps_closed": 0,
            "completion_claim": False,
        })

    write(HERE / "closure-tranches.jsonl", tranches)
    write(HERE / "source-authority-ratification-batch.jsonl", appraisals)
    summary = {
        "gap_quotients": len(all_rows),
        "gap_atoms": sum(row["current_atom_count"] for row in all_rows),
        "research_candidate_quotients": len(rebased),
        "physical_governance_quotients": len(physical),
        "source_authority_prechecks_complete": sum(row["status"] == "READY_FOR_NAMED_RATIFIER_REVIEW" for row in appraisals),
        "source_authority_prechecks_refused": sum(row["status"] == "PRECHECK_REFUSED" for row in appraisals),
        "canonical_gaps_closed": 0,
        "next_required_action": "A named project semantic authority must accept, modify, or reject each of the 23 exact source-family payloads; a separate verifier must attest the resulting receipt before P4 ingestion.",
        "completion_claim": False,
    }
    (HERE / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
