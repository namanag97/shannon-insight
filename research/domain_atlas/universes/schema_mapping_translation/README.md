# Schema Mapping and Translation

This universe closes the exact structural mapping seam beneath Managed Ingestion and Delivery.
The mandatory lens review rejected a single monolithic library: compilation and per-record
execution have different volatility, resource economics, qualification suites and substitution
boundaries.

```text
exact source schema closure          exact target schema closure
             \                              /
              +---- carrier profiles ------+
                            |
                            v
                 Schema Mapping Compiler
       match rules · type relations · loss · residuals
                            |
                  immutable accepted plan
                            |
                            v
                 Schema Mapping Executor
         record/change evaluation · residuals · trace
                            |
                            v
            translated value + explicit evidence
```

The compiler owns structural correspondence, representability, loss classification and plan
invalidation. The executor evaluates only an already accepted exact plan. Both are pure and perform
no ambient I/O. Schema parsing and registry operations remain adapters or neighboring libraries.
Ontology mapping, master/reference crosswalks, units, currencies, formulas, business equivalence,
source capture, delivery commits and factual acceptance remain outside the boundary.

The corpus contains 20 primary/official sources, one bounded context, 35 decisions with no hidden
defaults, 12 applied boundary lenses, one explicit split verdict, two exact libraries, 14 pure
operations and 26 negative twins. The shared `AcceptedMappingPlan` is a published contract, not
evidence that the libraries should be merged. Current offers have zero qualified implementations
and are neither selectable nor portable.

Run from this directory:

```sh
python3 build_corpus.py
python3 validate_corpus.py
```
