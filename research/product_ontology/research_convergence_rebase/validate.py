#!/usr/bin/env python3
"""Validate the research convergence rebase and its fail-closed boundary."""

from __future__ import annotations

import hashlib
import json

from build_rebase import HERE, build, outputs


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
    assert len(dispositions) == len({row["cluster_ref"] for row in dispositions}) == 686
    research = [row for row in dispositions if row["research_addressable"]]
    physical = [row for row in dispositions if not row["research_addressable"]]
    assert len(research) == 625 and sum(row["current_atom_count"] for row in research) == 14496
    assert all(row["atom_count_delta"] == 0 and row["candidate_status"] == "REBASED_PROPOSED_UNRATIFIED" for row in research)
    assert len(physical) == len(gates) == 61
    assert sum(row["current_atom_count"] for row in physical) == summary["physical_governance_gate_atoms"]
    changed = [row for row in physical if row["atom_count_delta"]]
    assert len(changed) == 15 and all(row["gap_kind"] == "product-gate" for row in changed)
    by_gate = {row["cluster_ref"].removeprefix("gap-cluster.product-gate."): row["atom_count_delta"] for row in changed}
    downstream_growth = {delta for gate, delta in by_gate.items() if gate != "contract-decomposition"}
    assert len(downstream_growth) == 1
    retained_product_growth = next(iter(downstream_growth))
    assert 0 < by_gate["contract-decomposition"] <= retained_product_growth
    # A structurally decomposed newly retained product adds downstream evidence gates without
    # adding a contract-decomposition vacancy. All other product gates grow once per product.
    assert sum(row["atom_count_delta"] for row in physical) == summary["physical_gate_atom_growth"]
    assert all(row["canonical_gaps_closed"] == 0 and not row["completion_claim"] for row in dispositions + gates)
    assert summary["canonical_gaps_closed"] == summary["ratified_decisions"] == summary["invented_implementations"] == summary["invented_qualifications"] == summary["invented_vertical_acceptances"] == 0
    print(f"PASS research convergence rebase: all 625 research quotients / 14,496 atoms rebase losslessly as proposed-unratified; 61 physical/governance gates / {summary['physical_governance_gate_atoms']:,} atoms remain open; {summary['physical_gate_atom_growth']} added atoms are exactly the newly retained products across fifteen product gates")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
