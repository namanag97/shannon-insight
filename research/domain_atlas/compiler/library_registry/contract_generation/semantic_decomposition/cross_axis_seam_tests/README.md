# Cross-axis seam tests

Twenty declared non-collapse seams are exercised with six deterministic negative twins each:
missing left/right profile, bearer mismatch, profile/edition mismatch, authority/effect/resource/
evidence mismatch, and missing owner decision or refusal precedence.

All 120 cases must fail closed. Passing these tests proves only that structural wiring refuses known
collapse modes. Semantic contradiction appraisal still requires exact bearer-coordinate profiles,
bounded evidence and owner decisions; no compiler binding is permitted by this package.

Run `python3 build_cross_axis_seam_tests.py` and `python3 validate.py`.
