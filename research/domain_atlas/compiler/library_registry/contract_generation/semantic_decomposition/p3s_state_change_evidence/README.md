# P3S state/change evidence campaign

This campaign supplies one bounded primary-source evidence candidate and one
negative twin for every family targeted on the `state_and_change` semantic axis.
The 23 family dockets route all 629 family-library occurrences from the live
targeted-evidence work packages.

The campaign does **not** choose family defaults, decide member applicability,
assign semantic owners, write exact contracts, qualify implementations or close
canonical gaps. Every candidate remains unratified and every docket preserves
those residual decisions explicitly.

The sources show why a universal `Status` or `StateChanged` type would be false.
The campaign keeps at least these distinctions open for owner adjudication:

- domain state versus representation or metadata version;
- desired state versus observed state versus requested effect;
- definition edition versus evaluation or computed observation;
- run terminality versus result consumption, delivery and acceptance;
- validation report versus repair proposal versus authorized mutation;
- log fetch position versus committed recovery position versus business effect;
- model version versus mutable alias, approval and deployment;
- experiment exposure versus evidence accumulation, decision and rollout;
- revocation versus retraction, deletion and legal erasure;
- replay or reconstruction versus another occurrence of the world event.

Build and validate:

```text
python3 build_p3s.py
python3 validate.py
```

The shared `axis_evidence_campaign.py` module owns only deterministic campaign
mechanics. Evidence meaning, negative twins, applicability, owners, exceptions
and acceptance remain local and independently reviewable.
