#!/usr/bin/env python3
"""Rebase external research dispositions onto the current fail-closed gap topology."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
DELTA = ROOT / "research/handoffs/gpt-pro-product-ontology-convergence/output-2026-08-27"
GAPS = ROOT / "research/domain_atlas/compiler/library_registry/contract_generation/semantic_decomposition/gap_topology/gap-clusters.jsonl"
AS_OF = "2026-08-27"


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def build() -> dict[str, Any]:
    current = {row["cluster_id"]: row for row in load_jsonl(GAPS)}
    prior = {row["input_cluster_ref"]: row for row in load_jsonl(DELTA / "gap-dispositions.jsonl")}
    if set(current) != set(prior):
        raise ValueError("stable quotient identities drifted; manual boundary rebase required")

    dispositions = []
    gate_deltas = []
    for cluster_ref in sorted(current):
        now = current[cluster_ref]
        old = prior[cluster_ref]
        research = old["disposition"] == "RESEARCH_RESOLVED_TO_PROPOSED_UNRATIFIED_DECISIONS"
        atom_delta = now["atom_count"] - old["original_atom_count"]
        if research and atom_delta:
            raise ValueError(f"research quotient atom drift requires residual adjudication: {cluster_ref}")
        status = "REBASED_PROPOSED_UNRATIFIED" if research else "CURRENT_EVIDENCE_GATE_OPEN"
        row = {
            "record_kind": "research_convergence_rebased_gap_disposition",
            "rebase_id": f"rebase.{cluster_ref}",
            "cluster_ref": cluster_ref,
            "gap_kind": now["gap_kind"],
            "program_ref": now["program_ref"],
            "research_addressable": research,
            "prior_atom_count": old["original_atom_count"],
            "current_atom_count": now["atom_count"],
            "atom_count_delta": atom_delta,
            "prior_disposition_ref": old["gap_disposition_id"],
            "primary_kernel_refs": old["primary_kernel_refs"],
            "candidate_status": status,
            "current_affected_scope_refs": now["affected_scope_refs"],
            "remaining_closure_condition": old["remaining_closure_condition"],
            "invalidation_condition": old["invalidation_condition"],
            "canonical_gaps_closed": 0,
            "completion_claim": False,
        }
        dispositions.append(row)
        if not research:
            gate_deltas.append({
                "record_kind": "current_physical_governance_gate_delta",
                "gate_delta_id": f"gate-delta.{cluster_ref}",
                "cluster_ref": cluster_ref,
                "gap_kind": now["gap_kind"],
                "prior_atom_count": old["original_atom_count"],
                "current_atom_count": now["atom_count"],
                "atom_count_delta": atom_delta,
                "required_evidence_kinds": now["required_evidence_kinds"],
                "status": "EVIDENCE_GATE_OPEN",
                "canonical_gaps_closed": 0,
                "completion_claim": False,
            })

    research_rows = [row for row in dispositions if row["research_addressable"]]
    evidence_rows = [row for row in dispositions if not row["research_addressable"]]
    summary = {
        "program_id": "program.product-ontology-research-convergence-rebase.v1",
        "as_of": AS_OF,
        "current_gap_quotients": len(dispositions),
        "current_gap_atoms": sum(row["current_atom_count"] for row in dispositions),
        "research_addressable_quotients": len(research_rows),
        "research_addressable_atoms": sum(row["current_atom_count"] for row in research_rows),
        "rebased_research_candidate_dispositions": len(research_rows),
        "physical_governance_gate_quotients": len(evidence_rows),
        "physical_governance_gate_atoms": sum(row["current_atom_count"] for row in evidence_rows),
        "physical_gate_atom_growth": sum(row["atom_count_delta"] for row in evidence_rows),
        "changed_gate_quotients": sum(bool(row["atom_count_delta"]) for row in evidence_rows),
        "canonical_gaps_closed": 0,
        "ratified_decisions": 0,
        "invented_implementations": 0,
        "invented_qualifications": 0,
        "invented_vertical_acceptances": 0,
        "completion_claim": False,
    }
    return {"dispositions": dispositions, "gate_deltas": gate_deltas, "summary": summary}


def outputs() -> dict[str, str]:
    built = build()
    files = {
        "rebased-gap-dispositions.jsonl": "".join(canonical(row) + "\n" for row in built["dispositions"]),
        "physical-governance-gate-deltas.jsonl": "".join(canonical(row) + "\n" for row in built["gate_deltas"]),
        "summary.json": json.dumps(built["summary"], ensure_ascii=False, indent=2, sort_keys=True) + "\n",
    }
    manifest = {name: {"bytes": len(text.encode()), "sha256": hashlib.sha256(text.encode()).hexdigest()} for name, text in files.items()}
    files["manifest.json"] = json.dumps({"manifest_id": "manifest.product-ontology-research-convergence-rebase.v1", "as_of": AS_OF, "files": manifest, "completion_claim": False}, indent=2, sort_keys=True) + "\n"
    return files


def main() -> int:
    for name, text in outputs().items():
        (HERE / name).write_text(text, encoding="utf-8")
    summary = build()["summary"]
    print(f"BUILD PASS research convergence rebase: {summary['rebased_research_candidate_dispositions']} research quotients rebase losslessly; {summary['physical_governance_gate_quotients']} evidence gates preserve {summary['physical_governance_gate_atoms']} open atoms; zero canonical closures")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

