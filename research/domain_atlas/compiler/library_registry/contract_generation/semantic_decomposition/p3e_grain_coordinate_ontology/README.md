# P3E grain-coordinate ontology and member rebase

This package corrects a category error in the original `grain_and_cardinality`
axis. A library does not possess one globally applicable grain. Grain belongs to
an externally meaningful position of an operation, state, event, evidence item,
receipt or sink effect. The operation then declares how it transforms the input
coordinate tuple into its output tuple.

The current flat facets (`record_or_tuple`, `partitioned`, `graph_or_network`,
and so on) are retained as a lossy discovery index. They may route research but
cannot establish member applicability or an exact contract.

The coordinate contract separates:

- semantic position;
- semantic unit;
- container scope;
- multiplicity semantics;
- cardinality bounds and count basis;
- boundedness and completeness scope;
- dependencies on identity, order, state, time, partiality and authority;
- the transformation kernel between positioned coordinates.

`member-operation-routes.jsonl` losslessly routes all 638 P3E target members.
`member-research-clusters.jsonl` factors those routes into reusable research
clusters without copying a family default into members. The reusable kernel
catalog prevents recurring proofs such as filter, aggregate, join, window,
partition, snapshot and encode/decode from being rediscovered library by
library.

No record in this package chooses an owner, supplies an operation-positioned
member profile, decides applicability or closes a canonical gap.

Run:

```bash
python3 build_grain_coordinate_ontology.py
python3 validate.py
```
