# Targeted semantic-axis evidence coverage

This audit joins the live targeted-evidence work packages to their concrete P3
campaigns. It is deliberately fail-closed: a newly targeted axis without a
registered campaign, an orphan campaign, a stale work-package digest, a missing
family, or changed library membership fails the build.

The current quotient routes six axes, 103 family-axis packages and 2,805 exact
family-library occurrences through six independently researched campaigns:

- `grain_and_cardinality` → P3E;
- `state_and_change` → P3S;
- `order_and_topology` → P3O;
- `composition_algebra` → P3C;
- `identity_and_equality` → P3I;
- `partiality_and_uncertainty` → P3U.

Coverage is not closure. This audit proves only that the explicitly targeted
evidence lanes have current, reversible routes. All owners, member applicability,
exception clusters, exact contracts, implementations, qualifications and product
acceptance remain independently governed and open.

Build and validate:

```text
python3 build_targeted_evidence_coverage.py
python3 validate.py
```
