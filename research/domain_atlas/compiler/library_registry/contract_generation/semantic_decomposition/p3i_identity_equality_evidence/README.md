# P3I identity/equality evidence campaign

This campaign supplies one bounded primary-source evidence candidate and one
negative twin for every family targeted on the `identity_and_equality` semantic
axis. The seven family dockets route all 223 family-library occurrences from the
live targeted-evidence work packages.

The campaign does **not** choose family defaults, decide member applicability,
assign semantic owners, write exact contracts, qualify implementations or close
canonical gaps. Every candidate remains unratified and every docket preserves
those residual decisions explicitly.

The sources show why a universal identifier or equality predicate would be
false. The campaign keeps at least these distinctions open for adjudication:

- name versus namespace-qualified identifier versus occurrence UID;
- object identity versus carrier/value equality versus semantic equivalence;
- graph-, plan-, model-, table-, tenant- and aggregate-scoped identifiers;
- stable field identity versus mutable display name and ordinal position;
- decision-variable identity versus domain membership and assigned value;
- canonical representation or digest versus domain identity and truth;
- entity identifier versus version, snapshot, state, receipt and authority;
- equality evidence versus uniqueness enforcement and acceptance.

Build and validate:

```text
python3 build_p3i.py
python3 validate.py
```

The shared `axis_evidence_campaign.py` module owns only deterministic campaign
mechanics. Evidence meaning, identity laws, negative twins, applicability,
owners, exceptions and acceptance remain local and independently reviewable.
