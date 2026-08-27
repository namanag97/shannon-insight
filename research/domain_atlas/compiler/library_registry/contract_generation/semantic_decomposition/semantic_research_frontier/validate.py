#!/usr/bin/env python3
"""Validate the complete 16-axis semantic research frontier."""
from __future__ import annotations

import hashlib
import json

from build_semantic_research_frontier import HERE, LANES, build, outputs


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
    frontier = built["frontier"]
    lanes = built["lanes"]
    summary = built["summary"]
    assert len(frontier) == 16 and [row["frontier_rank"] for row in frontier] == list(range(1, 17))
    assert len({row["axis"] for row in frontier}) == 16
    assert len(lanes) == len(LANES) == 3
    assert {row["lane_ref"] for row in frontier} == {row["lane_id"] for row in lanes}
    assert [row["axis_count"] for row in lanes] == [6, 4, 6]
    assert [row["family_dockets"] for row in lanes] == [138, 92, 138]
    assert [row["member_axis_cells"] for row in lanes] == [4044, 2696, 4044]
    assert summary["family_axis_dockets"] == 368
    assert summary["member_axis_cells"] == 10784
    assert summary["candidate_clusters"] == 1300
    assert summary["review_ready_dockets"] == 258
    assert summary["blocked_dockets"] == 110
    assert summary["targeted_axes_with_campaign_routes"] == 6
    assert summary["targeted_family_packages"] == 103
    assert summary["targeted_library_occurrences"] == 2805
    assert summary["owner_decisions"] == 0
    assert summary["member_applicability_decisions"] == 0
    assert summary["canonical_gaps_closed"] == 0
    assert not summary["completion_claim"]
    assert all(
        row["owner_decisions"] == 0
        and row["member_applicability_decisions"] == 0
        and row["canonical_gaps_closed"] == 0
        and not row["completion_claim"]
        for row in frontier
    )
    print(
        "PASS semantic research frontier: all 16 axes/10,784 cells factor into "
        "6 targeted-evidence rebase, 4 ambiguous-split and 6 owner-review-ready axes; "
        "zero gaps falsely closed"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
