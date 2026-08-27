# Consumption, BI and visualization universe

This directory is a candidate, provider-neutral research universe for compiling analytical
consumption intent. It is not a UI application, component catalog or vendor feature survey. The
core uses typed contracts, algebras, deterministic state transitions and qualified runtimes;
generative methods are outside its dependency boundary.

```text
governed meaning / analytical question
                 |
                 v
 semantic query + OLAP coordinate + parameter contract
                 |
                 v
 query/kernel requirement -------> typed result + source-cut receipt
                                           |
                     +---------------------+----------------------+
                     |                                            |
                     v                                            v
      presentation grammar / report                    notebook document
      dashboard / table / map / story                         |
                     |                                  kernel protocol
                     v                                            |
       accessible + localized surface                           output
                     |
                     v
 semantic interaction -> presentation state -> session/history
                     |
       +-------------+--------------+----------------+
       |                            |                |
       v                            v                v
 alert evaluation           governed share      export bytes
       |                            |                |
 notification delivery      collaboration       loss receipt
       +----------------------------+----------------+
                                    |
                                    v
                explanation + inspectable evidence + uncertainty
                                    |
                                    v
                     human decision handoff -> action owner
```

## Constitutional distinctions

| Keep separate | Compiler consequence |
|---|---|
| semantic meaning / visual encoding | a field-to-channel mapping cannot define a metric, unit, time or aggregation |
| query result / presentation state | rows and cells do not share identity with selection, focus or viewport |
| dashboard / analytical case | a reusable surface does not replace question, evidence and decision provenance |
| report snapshot / live view | an immutable cut and a changing epoch cannot share a completeness claim |
| alert rule / notification delivery | condition state is independent of routing, retry and acknowledgement |
| export / governed sharing | serialized bytes do not imply continuing, revocable access |
| notebook document / execution kernel | cells and stored outputs do not identify process or environment state |
| accessibility semantics / styling | color, theme and alternate text alone do not establish equivalent access |
| explanation / evidence | rationale must link support; prose is not proof |
| client cache freshness / source finality | representation age cannot establish correction or finality posture |

These are executable invariants in `invariants-refusals.jsonl`. Unknown ownership, semantics,
edition, authority, freshness, loss, accessibility or runtime capability emits a typed gap and
fails closed. Fallback is allowed only for a proven equivalent or an explicitly authorized typed
degradation with a receipt.

## Registry surfaces

- `context-candidates.jsonl` — 52 candidate ownership boundaries across meaning, composition,
  notebooks, governed consumption, delivery, exchange, presentation, state and handoff.
- `capabilities.jsonl` and `decision-points.jsonl` — typed operation and compiler-choice surfaces.
- `presentation-contracts.jsonl` and `interaction-contracts.jsonl` — provider-neutral artifact,
  presentation-state and semantic-interaction records.
- `requirements-offers-bindings.jsonl` — capability matching keys and fail-closed rules; provider
  names are deliberately nonsemantic.
- `compiler-mappings.jsonl` — intent-to-context lowering and receipt patterns.
- `library-boundaries.jsonl` — pure value/IR libraries and effectful runtime adapters with explicit
  forbidden ownership.
- `cross-domain-mappings.jsonl` — typed exchanges with semantic/formula, query/kernel, quality,
  lineage, governance, security/privacy, decisions/actions, product truth, source, persistence,
  pipeline, encoding, shape and runtime-resource planes.
- `sources.jsonl` — standards, first-party specifications and peer-reviewed primary research with
  source-scoped authority and limitations.
- `innovations.jsonl` — evidence-backed 2021–2026 non-generative advances.
- `gaps.jsonl` — open questions that block silent compilation.
- `schema/` — JSON Schema records for every registry class.
- `metamodel.json`, `manifest.json` and `coverage-report.json` — closed compiler distinctions,
  exact counts and open-world coverage posture.

## Rebuild and validate

From the repository root:

```bash
python3 research/domain_atlas/universes/consumption_bi_visualization/build_corpus.py
python3 research/domain_atlas/universes/consumption_bi_visualization/validate_corpus.py
```

The validator checks schema shape, identifier uniqueness, referential closure, evidence use,
candidate-only status, quantitative floors, all ten identity splits, cross-plane coverage,
pure/runtime boundaries, recent-innovation dates, forbidden core dependencies, manifest counts and
exact equality between the checked-in outputs and the deterministic generator projection.

## Honest limits

The 87-source, 52-context and 208-capability edition is a saturation seed, not proof that every
future consumption practice has been enumerated. A standard proves only its own contract; it does
not qualify a particular renderer, BI engine, notebook client or delivery provider. Accessibility,
uncertainty communication and decision effects require task- and audience-specific human studies.
Internationalization behavior varies with locale-data editions. Offline authorization, source
revisions and notification guarantees remain deployment-specific. Cross-context ownership remains
candidate until the global atlas adjudicates it, and every unresolved case stays in `gaps.jsonl`.
