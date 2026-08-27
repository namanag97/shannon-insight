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
        expected_family_count=22,
        expected_library_occurrences=619,
    )
    print(
        "PASS P3C composition/algebra evidence: 22 bounded primary candidates route all "
        "619 family-library occurrences; applicability, ownership, exact contracts "
        "and gap closure remain open"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
