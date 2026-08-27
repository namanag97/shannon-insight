# P3C composition/algebra evidence campaign

This campaign supplies one bounded primary-source evidence candidate and one
negative twin for every family targeted on the `composition_algebra` semantic
axis. The 22 family dockets route all 619 family-library occurrences from the
live targeted-evidence work packages.

The campaign does **not** choose family defaults, decide member applicability,
assign semantic owners, write exact contracts, qualify implementations or close
canonical gaps. Every candidate remains unratified and every docket preserves
those residual decisions explicitly.

The sources show why a universal `compose`, `merge` or `combine` operation would
be false. The campaign keeps at least these distinctions open for adjudication:

- sequential, choice, parallel, loop and graph composition;
- union, join, intersection, aggregation, constraint conjunction and policy combining;
- commutative/idempotent merge versus ordered or precedence-sensitive composition;
- structural composition versus semantic compatibility and behavioral substitutability;
- optimistic commit, field ownership conflict and source-record supersession;
- transaction-local atomicity versus arbitrary external-effect composition;
- exact preservation versus lossy adaptation with explicit residual information;
- successful construction versus validity, authority, execution and acceptance.

Build and validate:

```text
python3 build_p3c.py
python3 validate.py
```

The shared `axis_evidence_campaign.py` module owns only deterministic campaign
mechanics. Evidence meaning, algebraic laws, negative twins, applicability,
owners, exceptions and acceptance remain local and independently reviewable.
