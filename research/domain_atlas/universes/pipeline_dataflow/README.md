# Pipeline and dataflow universe

Status: evidence-backed research candidate; not a completeness claim.

This package models the provider-neutral domain between a typed analytical operation graph and its
observable materializations. A vendor DAG document is only one possible surface syntax. It is not
the domain.

```text
declared pipeline intent
        |
        v
logical dataflow graph --type/progress/law checks--> compiled physical plan
        |                                               |
        |                                               v
        |                                      deployment binding
        |                                               |
        v                                               v
data-cut selection -------------------------------> pipeline run
                                                        |
                    +------------------+----------------+----------------+
                    v                  v                                 v
              task attempts      state/checkpoints              sink transactions
                    |                  |                                 |
                    +------------------+----------------+----------------+
                                                       v
                                            materializations + receipts
```

## Sovereign distinctions

| Concept | Owns | Does not own |
|---|---|---|
| ingestion | observation and extraction from a source boundary | arbitrary business transformation |
| transport | movement through typed channels | meaning-changing transformation |
| transformation | typed logical operations over observations | when or where work runs |
| dataflow runtime | operator execution, progress and data exchange | enterprise scheduling policy |
| orchestration | dependency readiness, triggers, schedules and run coordination | record-level data semantics |
| deployment | binding a compiled plan to qualified targets | the authored pipeline meaning |
| run | one execution under a data cut and plan edition | the reusable definition |
| task attempt | one attempt of one executable task in one run | the logical node itself |
| data cut | the exact bounded or frontier-delimited input selection | a wall-clock execution interval |
| materialization | a named, identifiable output state | proof that its contents are correct |
| lineage receipt | observed derivation evidence | prospective dependency by itself |

The model covers bounded batch, microbatch, continuous streaming, CDC, incremental, federated,
reverse-delivery and cyclic/iterative flows. Cycles are legal only when progress, state bounds,
termination or productive-continuation laws are explicit. “Exactly once” is never a node-local
label: it is an end-to-end proof over source replay, state recovery, execution and sink effect.
Compression is an explicit channel/transport binding with codec capabilities for ratio, CPU,
memory, seekability, splittability, dictionary lifecycle and corruption behavior; it is not a hidden
connector default.

## Package contents

- `context-candidates.jsonl` — bounded-context candidates with DDD boundaries, invariants,
  commands, events, refusals, lifecycles and decision points.
- `schemas/` — provider-neutral JSON Schemas for definitions, nodes, edges, ports, state,
  delivery, recovery and the definition-to-runtime artifact chain.
- `examples/` — one CDC snapshot/change handoff definition and its compiled/runtime artifacts.
- `operation-mappings.jsonl` — explicit mappings to the central typed-operation universe.
- `compiler-requirements.jsonl` and `capability-offer-templates.jsonl` — requirements and offer
  shapes used by binding; they are not vendor selections.
- `library-boundary-candidates.jsonl` — candidate pure and effectful library seams.
- `innovations.jsonl` — non-LLM innovations from 2021–2026 with evidence and limits.
- `sources.jsonl` — primary standards, project specifications, official documentation and seminal
  primary papers.
- `decision-catalog.jsonl` — decisions that must remain data, never hidden defaults.
- `failure-refusal-catalog.jsonl` — typed pre-execution refusals and post-admission failures.
- `artifact-kinds.jsonl` and `lifecycles.jsonl` — machine-readable identity separation and total
  lifecycle candidates for definitions, plans, deployments, runs, attempts, cuts, checkpoints,
  transactions, materializations and recovery processes.
- `gaps.jsonl` — unresolved ownership, evidence and interoperability questions.
- `build_corpus.py` — deterministic corpus generator.
- `validate_corpus.py` — structural, identity, reference and coverage validator.

## Compiler laws

1. Definitions, plans, deployments, runs, attempts, cuts and materializations have different IDs and
   editions; none may be substituted for another.
2. Every edge connects an output port to an input port and proves carrier, schema, update, time,
   order, partition and cardinality compatibility.
3. Every unbounded flow declares progress and state-retention semantics.
4. Every cycle declares feedback delay and either a termination proof, finite iteration budget or
   productive-continuation law.
5. Every stateful node declares state scope, bound, durability, checkpoint participation, expiry and
   migration behavior.
6. Retries occur at a declared effect boundary. Retry safety is proven, not inferred from a verb.
7. Replay and backfill create new runs over explicit data cuts; they never silently mutate history.
8. Cancellation defines propagation, cleanup and disposition of in-flight and externally visible
   effects.
9. A materialization is publishable only after its commit, quality and visibility gates produce
   scoped receipts.
10. Unknown capabilities or semantics are typed compiler gaps and are never guessed.

## Regeneration and validation

```bash
python3 research/domain_atlas/universes/pipeline_dataflow/build_corpus.py
python3 research/domain_atlas/universes/pipeline_dataflow/validate_corpus.py
```
