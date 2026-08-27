# Product qualification and vertical-acceptance program

Status: deterministic generated proof program; no implementation, provider, product or vertical is
promoted by this corpus.

The retained base snapshot contains 66 products, 539 product-attributed library subjects and 917
open evidence vacancies. That snapshot intentionally preserves the qualification state at the time
it was generated. A later canonical compiler-gap rebase proved that the five remaining
`BLOCKED_MISSING_CONTRACT` product cells were not missing semantic contracts: all 59 source gaps have
exact abstract contracts and are downstream implementation/provider-qualification vacancies.

The current effective projection is therefore 66 products, 539 library subjects, **912 effective
open evidence vacancies**, 144 structurally satisfied gate cells, zero missing-contract cells and
zero qualified, portable, accepted, build-ready or ratified products. One data-sharing exact-scope
gate has retained execution evidence but remains open because law authority, implementation
identity, reproducible build, independent appraisal and qualification prerequisites are not
satisfied. `effective-summary.json` is the current machine-readable status projection;
`summary.json` remains the immutable base snapshot used to prove the rebase rather than being
silently rewritten.

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

A source compiler gap also does not stay a semantic gap after an exact contract is established:

```text
source compiler gap
    -> exact abstract contract established
    -> research-resolved compiler-gap rebase
    -> implementation-binding / provider-qualification vacancy
```

`build_effective_state.py` enforces that transition. It only rebases a product when every raw gap
reference matches a canonical `compiler-gap-rebase.jsonl` record whose disposition is
`EXACT_ABSTRACT_CONTRACT_PRESENT`, whose remaining gate is concrete implementation/provider
qualification, and which carries no bound or qualified implementation. The effective manifest
binds the projection to exact upstream SHA-256 digests so stale downstream status is detectable. It
also discovers explicit `qualification-binding.json` records beneath the conformance-execution
registry, verifies their subject/gate/evidence scope, and records evidence-present-but-open states
without rewriting the retained base snapshot or promoting an implementation.

Models, LLMs and agents are optional proposal tools. They may suggest a typed profile, generate
candidate cases, search for a counterexample, summarize retained evidence or emit a diagnostic.
They may not approve a law, invent a fact, waive a refusal, qualify an implementation, authorize an
effect, accept a vertical outcome or ratify a product. Removing all such extensions leaves the
entire qualification DAG and deterministic evidence path intact.

Generated and retained artifacts:

- `metamodel.json` — non-collapse and automation laws plus reused authority registries;
- `gate-definitions.jsonl` and `gate-dependencies.jsonl` — the closed 16-gate proof DAG;
- `product-qualification-programs.jsonl` — retained base gate vector per product;
- `library-qualification-subjects.jsonl` — product-attributed semantic contracts, compiler
  projections and required conformance contexts;
- `evidence-vacancies.jsonl` — retained base missing-proof snapshot;
- `product-vertical-acceptance-programs.jsonl` — two unrelated vertical slots and eight acceptance
  gate classes per product;
- `summary.json` and `manifest.json` — deterministic base-snapshot counts and digests;
- `effective-gate-state-rebase.jsonl` — five exact product gate-state corrections derived from the
  59 canonical compiler-gap rebase records plus bounded evidence-presence projections;
- `execution-evidence-bindings.jsonl` — digest-bound retained execution evidence registered against
  exact qualification subjects and gates without implying a pass;
- `effective-summary.json` — current effective qualification counts;
- `effective-manifest.json` — exact input/output digests for the effective projection;
- `build_effective_state.py` — deterministic builder/checker for that projection.

Rebuild and validate from the repository root:

```bash
python3 research/product_ontology/qualification_program/build_program.py
python3 research/product_ontology/qualification_program/build_effective_state.py
python3 research/product_ontology/qualification_program/validate.py
python3 research/product_ontology/qualification_program/build_program.py --check
python3 research/product_ontology/qualification_program/build_effective_state.py --check
```
