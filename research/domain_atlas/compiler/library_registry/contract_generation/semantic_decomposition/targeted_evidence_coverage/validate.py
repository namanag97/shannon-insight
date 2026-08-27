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
    assert summary["targeted_work_packages"] == sum(row["targeted_work_packages"] for row in records)
    assert summary["targeted_library_occurrences"] == sum(row["targeted_library_occurrences"] for row in records)
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
        f"PASS targeted evidence coverage: all {len(records)} live targeted axes, "
        f"{summary['targeted_work_packages']} family-axis packages and "
        f"{summary['targeted_library_occurrences']} library occurrences have exact non-closing campaign routes"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
