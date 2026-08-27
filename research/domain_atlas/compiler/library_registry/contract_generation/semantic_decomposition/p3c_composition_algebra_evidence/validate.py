#!/usr/bin/env python3
"""Validate the complete bounded composition/algebra evidence campaign."""
from __future__ import annotations

from build_p3c import CLAIMS, HERE, TARGETS, build, outputs
from axis_evidence_campaign import validate_common


def main() -> int:
    built = build()
    validate_common(
        output_dir=HERE,
        targets_path=TARGETS,
        claims=CLAIMS,
        axis="composition_algebra",
        built=built,
        outputs=outputs(),
        expected_family_count=None,
        expected_library_occurrences=None,
    )
    print(
        f"PASS P3C composition/algebra evidence: {built['summary']['primary_evidence_candidates']} bounded primary candidates route all "
        f"{built['summary']['represented_library_occurrences']} family-library occurrences; applicability, ownership, exact contracts "
        "and gap closure remain open"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
