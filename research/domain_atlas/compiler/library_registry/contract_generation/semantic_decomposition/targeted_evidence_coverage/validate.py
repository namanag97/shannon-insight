#!/usr/bin/env python3
"""Validate exact, fail-closed coverage of live targeted evidence axes."""
from __future__ import annotations

import hashlib
import json

from build_targeted_evidence_coverage import CAMPAIGNS, HERE, build, outputs


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
    records = built["records"]
    summary = built["summary"]
    assert len(records) == len(CAMPAIGNS) == 6
    assert {row["axis"] for row in records} == set(CAMPAIGNS)
    assert summary["targeted_work_packages"] == 103
    assert summary["targeted_library_occurrences"] == 2805
    assert summary["routed_work_packages"] == summary["targeted_work_packages"]
    assert summary["routed_library_occurrences"] == summary["targeted_library_occurrences"]
    assert summary["unrouted_axes"] == [] and summary["unrouted_work_packages"] == 0
    assert summary["owner_decisions"] == 0
    assert summary["member_applicability_decisions"] == 0
    assert summary["canonical_gaps_closed"] == 0
    assert not summary["completion_claim"]
    assert all(
        row["targeted_work_packages"] == len(row["targeted_work_package_refs"])
        == len(row["targeted_family_refs"])
        == len(row["evidence_candidate_refs"])
        == len(row["evidence_docket_refs"])
        and row["owner_decisions"] == 0
        and row["member_applicability_decisions"] == 0
        and row["canonical_gaps_closed"] == 0
        and not row["completion_claim"]
        for row in records
    )
    print(
        "PASS targeted evidence coverage: all 6 live targeted axes, 103 family-axis packages "
        "and 2,805 library occurrences have exact non-closing campaign routes"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
