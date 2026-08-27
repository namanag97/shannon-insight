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
PHYSICAL_PROGRAMS = {"P06", "P07"}


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def build() -> dict[str, Any]:
    current = {row["cluster_id"]: row for row in load_jsonl(GAPS)}
    prior = {row["input_cluster_ref"]: row for row in load_jsonl(DELTA / "gap-dispositions.jsonl")}
    removed = set(prior) - set(current)
    if removed:
        raise ValueError(f"prior quotient identities disappeared; explicit retirement rebase required: {sorted(removed)}")

    dispositions = []
    gate_deltas = []
    for cluster_ref in sorted(current):
        now = current[cluster_ref]
        old = prior.get(cluster_ref)
        is_new = old is None
        research = (
            now["program_ref"] not in PHYSICAL_PROGRAMS
            if is_new
            else old["disposition"] == "RESEARCH_RESOLVED_TO_PROPOSED_UNRATIFIED_DECISIONS"
        )
        prior_atoms = 0 if is_new else old["original_atom_count"]
        atom_delta = now["atom_count"] - prior_atoms
        if not is_new and atom_delta < 0:
            raise ValueError(f"quotient contraction requires explicit scope migration: {cluster_ref}")
        research_residual_atoms = atom_delta if research else 0
        if research_residual_atoms:
            status = "NEW_RESEARCH_RESIDUAL_OPEN" if is_new else "REBASED_WITH_NEW_RESEARCH_RESIDUAL_OPEN"
        else:
            status = "REBASED_PROPOSED_UNRATIFIED" if research else "CURRENT_EVIDENCE_GATE_OPEN"
        remaining_condition = (
            "Research, counterexample testing and named-owner adjudication are required for this newly introduced or expanded semantic scope; prior convergence claims do not cover these atoms."
            if research_residual_atoms
            else (
                "Implementation, qualification, product build or vertical-acceptance evidence is required for this current physical/governance gate."
                if is_new
                else old["remaining_closure_condition"]
            )
        )
        row = {
            "record_kind": "research_convergence_rebased_gap_disposition",
            "rebase_id": f"rebase.{cluster_ref}",
            "cluster_ref": cluster_ref,
            "gap_kind": now["gap_kind"],
            "program_ref": now["program_ref"],
            "research_addressable": research,
            "new_current_quotient": is_new,
            "prior_atom_count": prior_atoms,
            "current_atom_count": now["atom_count"],
            "atom_count_delta": atom_delta,
            "research_residual_atoms": research_residual_atoms,
            "research_vacancy": research_residual_atoms > 0,
            "prior_disposition_ref": None if is_new else old["gap_disposition_id"],
            "primary_kernel_refs": [] if is_new else old["primary_kernel_refs"],
            "candidate_status": status,
            "current_affected_scope_refs": now["affected_scope_refs"],
            "remaining_closure_condition": remaining_condition,
            "invalidation_condition": (
                "Reopen or refactor when scope, evidence, authority, counterexamples or dependency identity changes."
                if is_new else old["invalidation_condition"]
            ),
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
                "new_current_quotient": is_new,
                "prior_atom_count": prior_atoms,
                "current_atom_count": now["atom_count"],
                "atom_count_delta": atom_delta,
                "required_evidence_kinds": now["required_evidence_kinds"],
                "status": "EVIDENCE_GATE_OPEN",
                "canonical_gaps_closed": 0,
                "completion_claim": False,
            })

    research_rows = [row for row in dispositions if row["research_addressable"]]
    research_residuals = [row for row in research_rows if row["research_vacancy"]]
    evidence_rows = [row for row in dispositions if not row["research_addressable"]]
    summary = {
        "program_id": "program.product-ontology-research-convergence-rebase.v1",
        "as_of": AS_OF,
        "current_gap_quotients": len(dispositions),
        "current_gap_atoms": sum(row["current_atom_count"] for row in dispositions),
        "research_addressable_quotients": len(research_rows),
        "research_addressable_atoms": sum(row["current_atom_count"] for row in research_rows),
        "prior_gap_quotients": len(prior),
        "new_current_gap_quotients": sum(row["new_current_quotient"] for row in dispositions),
        "rebased_research_candidate_dispositions": len(research_rows) - len(research_residuals),
        "research_residual_quotients": len(research_residuals),
        "research_residual_atoms": sum(row["research_residual_atoms"] for row in research_residuals),
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
