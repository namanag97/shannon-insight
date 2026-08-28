# Shannon Python implementation placement

This package records where the checked-in `src/shannon_insight` Python implementation belongs in the broader data-and-analytics architecture.

## Verdict

The Python package is retained as the implementation candidate for a **software-codebase intelligence application product** in the software-engineering domain. It is also a proving implementation from which narrowly scoped pure libraries and analytical method kernels may later be extracted and qualified.

It is **not** the universal enterprise data-and-analytics platform described by the product ontology. Its source-code acquisition, graph, temporal, statistics, semantics, persistence, query, runtime and presentation modules are application-composed implementation parts. Their existence does not create horizontal product sovereignty, semantic authority, provider qualification, portability or cross-industry acceptance.

```text
software repository / Git history
             │
             ▼
   bounded application intake
             │
             ▼
 syntax + identity + relations
             │
             ▼
 graph / temporal / statistical methods
             │
             ▼
 application signals and findings
             │
             ▼
 snapshots / reports / interactive experience
```

This is intentionally different from the universal construction path:

```text
customer and industry intent
      → governed semantic declarations
      → planner/compiler/reconciler decisions
      → qualified provider implementations
      → physical data/analytics solution
      → executed vertical acceptance
```

The Python application may supply evidence to that architecture. It may not silently stand in for it.

## Generated artifacts

- `shannon-python-placement.json` records the application-product boundary, negative charter, owned artifacts, lifecycle, non-collapse laws and qualification posture.
- `shannon-python-module-crosswalk.jsonl` assigns every current top-level Python package/module to one bounded implementation role and zero or more non-authoritative horizontal coverage coordinates. Every source file carries a SHA-256 digest and line count.
- `summary.json` contains computed totals and the projection digest.

The crosswalk is total by construction. A newly added top-level module is retained as bounded application support until an explicit role is added. Unknown code therefore cannot acquire universal platform status through omission, enthusiasm or naming.

## Non-collapse laws

Among the enforced laws:

```text
shannon Python package != universal enterprise data platform
codebase analysis application != horizontal analytics product family
implementation module != semantic authority
algorithm implementation != qualified method contract
local storage/query support != storage/query product
application kernel != solution compiler/planner/reconciler
Git/source-code observation != universal source-system contract
renderer/dashboard != analytical meaning
same-campaign tests != independent qualification
```

## Validation

From the repository root:

```bash
python3 research/product_ontology/implementation_placement/build_shannon_python_placement.py
python3 research/product_ontology/implementation_placement/validate_shannon_python_placement.py
pytest -q tests/research/test_shannon_python_placement.py
```

The validator rebuilds the corpus, checks byte-for-byte determinism, verifies every retained source digest, enforces total module coverage and known crosswalk coordinates, and rejects semantic-authority, implementation-qualification, product-ratification or completion claims.

## Remaining promotion gates

Reusable extraction remains explicitly downstream-gated. Any promoted library or method kernel still needs:

1. an exact abstract contract and sovereign semantic owner;
2. source, artifact, dependency, toolchain and configuration identities;
3. deterministic, adversarial and exact-scope execution receipts;
4. independent appraisal;
5. a second independently controlled implementation wherever portability is claimed; and
6. executed acceptance in unrelated verticals for any promoted horizontal contract.

This package is an architecture correction and evidence surface, not a declaration that those gates have passed.
