#!/usr/bin/env python3
"""Validate the all-axis semantic decision-locus factorization."""
from __future__ import annotations

import hashlib
import json

from build_decision_locus_ontology import AXIS_REFINEMENTS, HERE, build, outputs


def main() -> int:
    expected = outputs()
    for name, text in expected.items():
        assert (HERE / name).is_file(), f"missing {name}"
        assert (HERE / name).read_text() == text, f"stale {name}"
    manifest = json.loads((HERE / "manifest.json").read_text())
    for name, claim in manifest["files"].items():
        data = (HERE / name).read_bytes()
        assert len(data) == claim["bytes"]
        assert hashlib.sha256(data).hexdigest() == claim["sha256"]

    built = build()
    profiles = built["profiles"]
    factorizations = built["factorizations"]
    summary = built["summary"]
    assert len(built["bearers"]) == len({row["archetype_id"] for row in built["bearers"]}) == 10
    assert len(profiles) == len({row["axis"] for row in profiles}) == 16
    assert len(factorizations) == 368
    assert len({row["factorization_id"] for row in factorizations}) == 368
    assert all(row["member_count"] == len(row["member_preclassification_refs"]) for row in factorizations)
    member_refs = [ref for row in factorizations for ref in row["member_preclassification_refs"]]
    assert len(member_refs) == len(set(member_refs)) == 10784
    assert all(row["selected_family_default_decision"] == row["owner_decision"] == "UNRESOLVED" for row in factorizations)
    assert all(row["member_applicability_decisions"] == row["canonical_gaps_closed"] == 0 for row in factorizations)
    assert summary["member_axis_cells_preserved"] == 10784
    assert summary["initial_family_axis_quotient"] == 368
    assert summary["raw_cell_to_family_axis_ratio"] == round(10784 / 368, 6)
    assert summary["coordinate_refined_axes"] == len(AXIS_REFINEMENTS) == 16
    assert summary["coordinate_refined_target_member_routes"] == 9545
    assert summary["coordinate_unrefined_axes"] == 0
    assert {
        row["axis"] for row in factorizations if row["coordinate_refinement_ref"] is not None
    } == set(AXIS_REFINEMENTS)
    assert summary["family_default_decisions"] == summary["member_applicability_decisions"] == summary["owner_decisions"] == 0
    assert summary["canonical_gaps_closed"] == 0 and not summary["completion_claim"]
    print(
        "PASS semantic decision locus: all 10,784 cells retain exact identity while "
        "16 bearer-aware axis profiles route 368 family-axis quotients and explicit residuals"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
