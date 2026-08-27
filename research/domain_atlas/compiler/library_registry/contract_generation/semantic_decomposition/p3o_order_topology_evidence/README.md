# P3O order/topology evidence campaign

This campaign supplies one bounded primary-source evidence candidate and one
negative twin for every family targeted on the `order_and_topology` semantic
axis. The 23 family dockets route all 623 family-library occurrences from the
live targeted-evidence work packages.

The campaign does **not** choose family defaults, decide member applicability,
assign semantic owners, write exact contracts, qualify implementations or close
canonical gaps. Every candidate remains unratified and every docket preserves
those residual decisions explicitly.

The sources show why a universal `Order`, `Sequence`, `Hierarchy` or `Graph`
type would be false. The campaign keeps at least these distinctions open for
owner adjudication:

- sequence versus set, bag, map and graph;
- total order versus preorder, partial order and incomparable concurrency;
- dependency topology versus one valid topological serialization;
- event time versus arrival, processing, log and transaction-local order;
- row orderedness versus schema-field, buffer and plan traversal order;
- hierarchy versus polyhierarchy, grouping, partonomy and ordered collection;
- coordinate sequence versus qualitative spatial topology and route order;
- scenegraph nesting versus data sort, render layering and reading order;
- certification path versus graph reachability and relying-party trust;
- aggregation hierarchy versus crossed grouping topology and forecast coherence.

Build and validate:

```text
python3 build_p3o.py
python3 validate.py
```

The shared `axis_evidence_campaign.py` module owns only deterministic campaign
mechanics. Evidence meaning, negative twins, applicability, owners, exceptions
and acceptance remain local and independently reviewable.
