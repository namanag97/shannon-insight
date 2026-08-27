#!/usr/bin/env python3
"""Validate the research convergence rebase and its fail-closed boundary."""

from __future__ import annotations

import hashlib
import json

from build_rebase import DELTA, HERE, build, load_jsonl, outputs


def rows(name: str) -> list[dict]:
    return [json.loads(line) for line in (HERE / name).read_text().splitlines() if line.strip()]


def main() -> int:
    expected = outputs()
    for name, text in expected.items():
        assert (HERE / name).is_file() and (HERE / name).read_text() == text, f"stale {name}"
    manifest = json.loads((HERE / "manifest.json").read_text())
    for name, claim in manifest["files"].items():
        data = (HERE / name).read_bytes()
        assert len(data) == claim["bytes"] and hashlib.sha256(data).hexdigest() == claim["sha256"]

    dispositions = rows("rebased-gap-dispositions.jsonl")
    gates = rows("physical-governance-gate-deltas.jsonl")
    summary = build()["summary"]
    assert len(dispositions) == len({row["cluster_ref"] for row in dispositions}) == summary["current_gap_quotients"]
    prior = load_jsonl(DELTA / "gap-dispositions.jsonl")
    assert summary["prior_gap_quotients"] == len(prior)
    assert summary["new_current_gap_quotients"] == sum(row["new_current_quotient"] for row in dispositions)
    research = [row for row in dispositions if row["research_addressable"]]
    physical = [row for row in dispositions if not row["research_addressable"]]
    residuals = [row for row in research if row["research_vacancy"]]
    resolved = [row for row in research if not row["research_vacancy"]]
    prior_research = [row for row in prior if row["research_addressable"] is True]
    assert len(resolved) + sum(not row["new_current_quotient"] for row in residuals) == len(prior_research)
    assert all(row["atom_count_delta"] == 0 and row["candidate_status"] == "REBASED_PROPOSED_UNRATIFIED" for row in resolved)
    assert all(row["research_residual_atoms"] > 0 and row["candidate_status"] in {"NEW_RESEARCH_RESIDUAL_OPEN", "REBASED_WITH_NEW_RESEARCH_RESIDUAL_OPEN"} for row in residuals)
    assert len(residuals) == summary["research_residual_quotients"]
    assert sum(row["research_residual_atoms"] for row in residuals) == summary["research_residual_atoms"]
    assert len(physical) == len(gates) == summary["physical_governance_gate_quotients"]
    assert sum(row["current_atom_count"] for row in physical) == summary["physical_governance_gate_atoms"]
    changed = [row for row in physical if row["atom_count_delta"]]
    assert len(changed) == summary["changed_gate_quotients"]
    assert all(row["gap_kind"] in {"product-gate", "implementation", "qualification"} for row in changed)
    assert sum(row["atom_count_delta"] for row in physical) == summary["physical_gate_atom_growth"]
    assert all(row["canonical_gaps_closed"] == 0 and not row["completion_claim"] for row in dispositions + gates)
    assert summary["canonical_gaps_closed"] == summary["ratified_decisions"] == summary["invented_implementations"] == summary["invented_qualifications"] == summary["invented_vertical_acceptances"] == 0
    print(f"PASS research convergence rebase: {len(resolved)} prior research quotients rebase unchanged while {len(residuals)} new or expanded semantic quotients expose {summary['research_residual_atoms']} new research atoms; {len(physical)} physical/governance gates / {summary['physical_governance_gate_atoms']:,} atoms remain open; zero authority or evidence is fabricated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
