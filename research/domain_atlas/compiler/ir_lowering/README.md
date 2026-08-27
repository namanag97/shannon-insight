# Candidate deterministic intent-to-solution IR and lowering universe

This package specifies a research candidate, not a working compiler and not a completeness claim.
It models deterministic compilation from authored intent to evidence-bearing artifacts while refusing
unresolved meaning. LLM, generative, prompt, RAG, and agent-memory semantics are excluded from the
compiler core. Provider and target bindings are deliberately absent unless occurrence-scoped
qualification evidence exists; the miniature traces therefore stop at unbound physical requirements.

```text
source text / imports / registry snapshot
              |
              v
 [declaration AST] --parse/resolution receipts--> [resolved declaration IR]
              |                                         |
              | unresolved symbol/edition               | canonical assertions
              +----------------> typed gap <-------------+
                                                        v
 [language + bounded contexts + authority + explicit defaults]
              |
              v
 [analytical design: case -> method requirements -> rejected alternatives]
              |
              v
 [observation + semantic type + shape + identity/time/unit + representation]
              |
              v
 [typed logical operation/dataflow IR] ----equivalence proof----+
              |                                                  |
              v                                                  v
 [assurance/policy/proof IR]       [optimization-only alternatives + trace]
              |                                                  |
              +---------------------- merge proved meaning ------+
                                         |
                                         v
 [algorithm requirements -> kernel/layout/ABI requirements -> finite resources]
                                         |
                         qualified occurrence evidence? --no--> typed binding gap
                                         | yes
                                         v
 [physical bindings] -> [deployment/operations IR] -> [evidence/release IR]
                                         |
                                         v
 artifacts + pass/proof/binding/runtime/release receipts + retained rejections
```

## Separation laws

- Semantic lowering refines authored meaning between stages. Optimization selects only among
  proved-equivalent forms. A cost argument is never an equivalence proof.
- Method, algorithm, kernel, provider offer, and target occurrence are distinct identities.
- Semantic type, carrier, encoding, framing, layout, container, codec, and protection are distinct.
- Every applied default is a record with authority, applicability, precedence, provenance, and
  invalidation triggers. Missing or conflicting authority-bound values stop compilation.
- Every pass preserves source anchors, authorities, assumptions, rejected alternatives, and gaps.
- A proof/check/receipt is scoped to exact subjects, editions, inputs, checker, and environment.
- Stable identity is not a content digest. Both are carried because they answer different questions.

## Files

`contexts.jsonl` holds bounded-context candidates. `ir-nodes.jsonl` and `ir-edges.jsonl` enumerate
the staged model. Passes, invariants, diagnostics, proofs, rewrites, incremental rules, migrations,
extensions, artifacts/receipts, libraries, and Rust applicability are separate JSONL registries.
`lowering-traces.jsonl` contains two unrelated positive traces and their negative twins.
`sources.jsonl` contains primary/official evidence; `innovations.jsonl` isolates non-LLM 2021-2026
developments. `conformance-plan.json` states evaluation gates. `schemas/` contains machine contracts.
`upstream-alignment.json` records the compiler metamodel, proof catalog, and universe contracts read
as immutable research inputs; the local proof catalog refines but never replaces those obligations.

## Deterministic build and validation

```text
python3 research/domain_atlas/compiler/ir_lowering/build_corpus.py
python3 research/domain_atlas/compiler/ir_lowering/validate_corpus.py
```

The generator sorts every JSONL file by stable identity, emits sorted-key JSON with LF endings, and
uses no clock, network, filesystem enumeration order, random value, locale, or provider discovery.
The validator checks schemas as JSON, record shapes, reference closure, pass separation, candidate
status, forbidden generative terms, trace refusals, thresholds, manifest digests, and a clean
regeneration byte-comparison.

## Honest limits

This is an enumerated candidate universe. It does not supply a normative grammar, formal semantics
for every node, qualified rewrite/proof/migration checker, provider catalog, live provider evidence,
kernel qualification, concrete runtime ABI, or independent review. Those are blocking gaps recorded
in `gaps.jsonl`; they must not be filled by inference.
