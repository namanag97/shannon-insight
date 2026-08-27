# Product-ontology closure program

This is the operational cockpit for converting researched proposals into governed contracts,
implementations and accepted products without collapsing unlike evidence classes.

## Complete current frontier

| Tranche | Quotients | Atoms | What actually closes it |
|---|---:|---:|---|
| Source-family authority | 23 | 23 | Named authority accepts/modifies/rejects exact source payload |
| Researched symbol owners | 19 | 19 | Named semantic owner ratifies each stable proposal |
| Symbol-owner challenge batches | 89 | 191 | Resolve collisions and ratify all covered occurrences |
| Family-axis evidence | 103 | 2,805 | Appraise member-level evidence and negative cases |
| Applicability | 368 | 10,784 | Ratify every family × semantic-axis disposition |
| Exact contracts | 23 | 674 | Ratify exact types, operations, laws, refusals and oracles |
| Implementations | 23 | 674 | Supply code, reproducible build and executable-oracle receipts |
| Independent qualification | 23 | 674 | Two independent implementations pass the exact suite |
| Product gates | 15 | 903 | Build, bind, appraise and execute unrelated-vertical acceptance |
| **Total** | **686** | **16,747** | |

The first six tranches are decision/evidence work. The final three require physical artifacts and
executed receipts; more research cannot close them.

`closure-tranches.jsonl` partitions all 686 current quotients and 16,747 atoms exactly once. The
first batch, `source-authority-ratification-batch.jsonl`, performs deterministic prechecks for all
23 proposed source-family decisions: source digests are current, packet identity and library counts
match, every cited source resolves, and every payload retains a rationale, negative twin,
invalidation condition and explicit non-completion claim.

The semantic fixed-point campaign under `semantic_fixed_point_campaign/` separately verifies that
all 625 research-addressable quotients (14,496 atoms) and all research gaps discovered by the
campaign have evidence-bounded proposed-unratified resolutions. This does not change canonical
closure: named project authority and independent verification remain required.

The batch is ready for a **named project authority** to accept, modify or reject. This program does
not invent that decision, signature, independent verification, implementation, qualification or
vertical acceptance. After signed decisions and separate authority-verification receipts exist,
P4 can ingest them and produce canonical delta candidates.

Run:

```text
python3 research/product_ontology/closure_program/build_program.py
python3 research/product_ontology/closure_program/validate.py
python3 research/product_ontology/semantic_fixed_point_campaign/build_fixed_point.py
python3 research/product_ontology/semantic_fixed_point_campaign/validate_fixed_point.py
```
