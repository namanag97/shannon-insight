# Solution synthesis architecture

This package prevents **compiler** from becoming an absolute metaphor. It classifies every
requirement into one of five resolution frontiers and places deterministic compilation inside a
larger architecture with constraint planning, owner adjudication, desired-state reconciliation,
independent assurance and governed open-world research.

The pattern deliberately promotes no product. The existing Intent-to-Solution Compiler remains a
bounded product candidate whose success is either an immutable evidence-bearing blueprint or an
exact actionable residual. A blueprint is not applied state; a product is not the sum of its
libraries; and an unknown concept is not silently treated as an unsupported known construct.

## The synthesis shape is a hypergraph

The architecture is not a single `intent -> pipeline` chain. Several separately owned planes must
join, and any missing join produces a typed residual:

```text
 business intent ---------> domain contexts ---------> semantic intent
      |                          |                          |
      |                          +--> application behavior +--> authority/effects
      |                                                     \
      +--> product promises --> capability requirements --> exact contracts
                                  ^                         /
 semantic intent --> analytical design -------------------+
        |                   |                 \
        +--> source estate  +--> logical dataflow --> experience/delivery
                    \                  |                    /
                     +-----------------+-------------------+
                                       v
 exact contracts --> implementation offers --> qualification evidence
                                       |                     |
                                       +----------+----------+
                                                  v
                                  qualified physical bindings
                                       |
                              deployment blueprint
                                       |
                         evidence + vertical acceptance
```

Product composition, semantic ownership, analytical design, application behavior and provider
binding are deliberately not collapsed. Product planning may feed new capability requirements;
authority adjudication and open-world research may suspend and later resume synthesis.

## How Python fits

Python is the deterministic research and corpus toolchain: collectors, authored candidate models,
pure builders, validators, routers/indexes, execution harnesses, an explicit build orchestrator and
prototype solvers. It is not automatically the final domain-library language or production runtime.
The interchange contract is governed JSONL plus schemas. Rust can later implement typed compiler
and runtime libraries, while exact contract identity and semantic authority remain language-neutral.

The toolchain distinguishes:

- immutable historical snapshots, whose exact counts and digests are part of their identity;
- live canonical projections, whose counts must derive from declared current inputs;
- authored candidate records, which remain proposed until a named authority ratifies them;
- execution receipts, which are evidence but not qualification;
- independently appraised qualification receipts, which remain exact-scope and revocable.

Generic Python plumbing may normalize, route and check. It must not hide semantic ownership,
defaults, product boundaries or binding decisions inside filename rules or hard-coded cardinalities.
Every package should ultimately declare authored inputs, generated outputs, dependencies, builder,
validator, authority status and support-set invalidation triggers.

The generated `data-analytics-planes.jsonl`, `python-toolchain-roles.jsonl`,
`artifact-classes.jsonl`, `build-policies.jsonl` and `ir-join-rules.jsonl` make these boundaries
machine-readable.

Rebuild and validate:

```bash
python3 research/product_ontology/solution_synthesis_architecture/build_corpus.py
python3 research/product_ontology/solution_synthesis_architecture/validate.py
```
