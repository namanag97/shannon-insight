#!/usr/bin/env python3
"""Validate the lineage/provenance/evidence family-constitution pilot."""

from __future__ import annotations

import hashlib
import json

from build_pilot import HERE, build, outputs, rows


def main() -> int:
    for name, text in outputs().items():
        assert (HERE / name).is_file() and (HERE / name).read_text(encoding="utf-8") == text, f"stale {name}"
    manifest = json.loads((HERE / "manifest.json").read_text(encoding="utf-8"))
    for name, claim in manifest["files"].items():
        data = (HERE / name).read_bytes()
        assert len(data) == claim["bytes"] and hashlib.sha256(data).hexdigest() == claim["sha256"], name
    constitution, coverage, summary = build()
    assert constitution["status"] == "OWNER_REVIEW_REQUIRED_NOT_CANONICAL"
    assert len(constitution["bounded_contexts"]) >= 60
    assert len(constitution["shared_distinctions"]) >= 13
    assert len(constitution["roles_and_authority"]["authority_dimensions"]) >= 6
    assert len(constitution["evidence_strength_dimensions"]) >= 9
    assert len(constitution["defeater_model"]) >= 9
    assert len(constitution["shared_slot_coverage"]) == 12
    assert len(constitution["library_local_slots"]) == 8
    assert len(coverage) == 31 and len({row["library_ref"] for row in coverage}) == 31
    assert all(row["applicability_attestation"] == "UNRESOLVED" for row in coverage)
    assert all(row["canonical_gap_closed"] is False for row in coverage)
    assert summary["canonical_exact_gaps_closed"] == 0 and summary["completion_claim"] is False
    assert summary["projected_repeated_review_reduction"] > 300
    print(f"PASS LPE family constitution pilot: {len(coverage)} open instances; {summary['projected_repeated_review_reduction']} repeated review units factored; owner applicability and all exact gaps remain explicit")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
