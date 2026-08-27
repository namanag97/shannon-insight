# Product-ontology closure program

This package is the operational cockpit for converting researched proposals into governed contracts, implementations and accepted products without collapsing unlike evidence classes.

## Two projections, deliberately distinct

`closure-tranches.jsonl` is the historical semantic-convergence quotient projection produced from `research_convergence_rebase`. It remains trace evidence for the 686 quotient campaign and MUST NOT be used as the live downstream readiness headline after newer corpora reclassify work.

`master-batches.jsonl` and `master-summary.json` are the current dependency-ordered closure frontier. They consume the latest committed dossier-readiness, effective qualification, industry integration, context-map, source-system, data-shape, analytical-method and provider-target summaries.

Current live facts include:

- 66 retained product candidates with complete candidate DDD and structural compiler maps;
- 539 exact product-attributed library qualification subjects;
- 0 open structural compiler gaps after the canonical 59-gap rebase;
- 912 effective qualification evidence vacancies, not the older 917 raw-snapshot vacancies;
- 1,613 researched industry analytical cases across 9 broad challenge packs;
- 4,169 raw canonical-reference review records, of which 3 are research-resolved candidates and
  4,166 remain effectively open across industry/method/operation/source identities;
- 137 conservative exact-alias candidates covering 127 methods, 8 typed operations and 2 source
  classes, representing 644 occurrences and factored into 31 owner-review batches; exact matching
  is explicitly prohibited from closing a semantic decision;
- 171 open-world source-system classes;
- 177 logical data shapes;
- 144 candidate global contexts and 308 context relations;
- 59 provider implementation artifacts / concrete offers as unqualified seeds;
- 0 portable, vertically accepted, build-ready or ratified products.

No count is a completeness claim.

## Dependency-ordered batches

The live queue is divided into 16 batches:

```text
B00 truth convergence
 |
 +--> B01 source authority --> B02 sovereign ownership --> B03 context-map ratification --+
 |                                                                                       |
 +--> B04 evidence governance ------------------------------------------------------------+
                                                                                          v
                                                                               B05 product falsification
                                                                                          |
                                                                               B06 library authority
                                                                                 /        |        \
                                                                                v         v         v
                                                                    B07 vertical refs   B09 shapes  B10 implementation/build
                                                                        |                  \        /
                                                                        v                   v      v
                                                                    B08 sources          B11 exact execution/appraisal
                                                                                              /     \
                                                                                             v       v
                                                                                   B12 portability  B13 physical proof
                                                                                             \       /
                                                                                              v     v
                                                                                     B14 two-vertical acceptance
                                                                                              |
                                                                                              v
                                                                                     B15 two-release + ratification
```

B01 and final ratification are intentionally authority-blocked. Research and automation may prepare exact decision payloads but cannot invent named human authority, independent appraisal or physical execution receipts.

## Ownership convergence

`research/domain_atlas/ownership-adjudications.jsonl` resolves all eight legacy `ownership-ambiguities.json` terms at the research-decision layer. The rows distinguish, among other things, optimizer plan cost from measured/billed cost, publication entitlement from notification subscription, event-time window firing from workflow initiation, and deployment rollback from semantic/data reversal. These decisions remain candidate-not-ratified until a named semantic authority accepts/modifies/rejects them.

## Validation

Run from the repository root:

```text
python3 research/product_ontology/closure_program/build_program.py
python3 research/product_ontology/closure_program/validate.py
python3 research/product_ontology/closure_program/build_master_frontier.py
python3 research/product_ontology/closure_program/validate_master_frontier.py
python3 research/domain_atlas/validate_ownership_adjudications.py
python3 research/product_ontology/semantic_fixed_point_campaign/build_fixed_point.py
python3 research/product_ontology/semantic_fixed_point_campaign/validate_fixed_point.py
```

The historical quotient projection and the live batched frontier answer different questions and are both retained intentionally. A validator passing proves only the laws encoded by that validator.
