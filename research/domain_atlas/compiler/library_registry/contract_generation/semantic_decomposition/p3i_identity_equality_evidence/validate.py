#!/usr/bin/env python3
"""Validate the complete bounded identity/equality evidence campaign."""
from __future__ import annotations

from build_p3i import CLAIMS, HERE, TARGETS, build, outputs
from axis_evidence_campaign import validate_common


def main() -> int:
    built = build()
    validate_common(
        output_dir=HERE,
        targets_path=TARGETS,
        claims=CLAIMS,
        axis="identity_and_equality",
        built=built,
        outputs=outputs(),
        expected_family_count=7,
        expected_library_occurrences=223,
    )
    print(
        "PASS P3I identity/equality evidence: 7 bounded primary candidates route all "
        "223 family-library occurrences; applicability, ownership, exact contracts "
        "and gap closure remain open"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
