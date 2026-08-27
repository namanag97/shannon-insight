#!/usr/bin/env python3
"""Validate the complete bounded state/change evidence campaign."""
from __future__ import annotations

from build_p3s import CLAIMS, HERE, TARGETS, build, outputs
from axis_evidence_campaign import validate_common


def main() -> int:
    built = build()
    validate_common(
        output_dir=HERE,
        targets_path=TARGETS,
        claims=CLAIMS,
        axis="state_and_change",
        built=built,
        outputs=outputs(),
        expected_family_count=23,
        expected_library_occurrences=629,
    )
    print(
        "PASS P3S state/change evidence: 23 bounded primary candidates route all "
        "629 family-library occurrences; applicability, ownership, exact contracts "
        "and gap closure remain open"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
