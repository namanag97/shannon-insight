# Product qualification and vertical-acceptance program

Status: deterministic generated proof program; no implementation, provider, product or vertical is
promoted by this corpus.

Current generated snapshot: 59 products, 470 product-attributed library subjects, 814 open
evidence vacancies and zero qualified, portable, accepted, build-ready or ratified products.

This layer answers the question left open by complete DDD and compiler decomposition:

> What exact evidence must exist before a specified product can be called implemented, qualified,
> portable, physically bindable, vertically accepted, build-ready or ratified?

It is not another product catalog and not an application. It projects every retained product and
each of its attributed library contracts into the existing executable-conformance and
provider/target systems.

```text
product boundary + complete DDD
            |
            v
exact product -> library -> compiler contracts
            |
            v
authority-approved laws and executable oracles
            |
            v
artifact + source + dependency + build identity
            |
            v
exact target/configuration/population execution receipts
            |
            v
independent appraisal -> first exact-scope qualification
            |
            +--> exact physical binding and operational envelope ------+
            |                                                          |
            v                                                          v
second independent implementation -> differential + exit -> portable offer
                                                                       |
two unrelated structural verticals -----------------------------------+
            |
            v
executed domain-owner acceptance -> build-ready -> ratification
```

The states do not collapse:

```text
specified != implemented != built != executed != appraised != qualified
          != portable != physically bound != vertically accepted
          != build-ready != ratified
```

Models, LLMs and agents are optional proposal tools. They may suggest a typed profile, generate
candidate cases, search for a counterexample, summarize retained evidence or emit a diagnostic.
They may not approve a law, invent a fact, waive a refusal, qualify an implementation, authorize an
effect, accept a vertical outcome or ratify a product. Removing all such extensions leaves the
entire qualification DAG and deterministic evidence path intact.

Generated artifacts:

- `metamodel.json` — non-collapse and automation laws plus reused authority registries;
- `gate-definitions.jsonl` and `gate-dependencies.jsonl` — the closed 16-gate proof DAG;
- `product-qualification-programs.jsonl` — one exact gate vector per retained product;
- `library-qualification-subjects.jsonl` — product-attributed semantic contracts, compiler
  projections and required conformance contexts;
- `evidence-vacancies.jsonl` — every missing proof as an open, blocking typed vacancy;
- `product-vertical-acceptance-programs.jsonl` — two unrelated vertical slots and eight acceptance
  gate classes per product;
- `summary.json` and `manifest.json` — counts and deterministic digests.

Rebuild and validate from the repository root:

```bash
python3 research/product_ontology/qualification_program/build_program.py
python3 research/product_ontology/qualification_program/validate.py
python3 research/product_ontology/qualification_program/build_program.py --check
```
