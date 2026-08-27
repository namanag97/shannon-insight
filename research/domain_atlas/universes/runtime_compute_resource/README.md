# Runtime, compute and resource-control universe

This corpus defines the horizontal language and compiler boundary for executable work and finite
resources. It is intentionally independent of query meaning, analytical method meaning, business
workflow meaning, provider product names and LLM/generative/agentic semantics.

It is a research candidate, not a completeness claim. The current edition provides enumeration
pressure, explicit ownership, executable validation and evidence-backed hypotheses that still need
cross-domain adjudication and two-implementation conformance.

## The essential separation

```text
business / analytical / pipeline intent
                 |
                 | requires executable work, effects and SLOs
                 v
       SEMANTIC EXECUTION CONTRACT
       WorkUnit + Artifact + EntryPoint
       completion/cancel/retry/checkpoint laws
                 |
                 | derives finite demand
                 v
          RESOURCE DEMAND VECTOR
       min / target / max + constraints
                 |
                 | admission is not placement
                 v
     quota + budget/precharge + admission
                 |
                 | matches qualified supply
                 v
   RESOURCE OFFER ---- topology/inventory/health
                 |
                 | scheduler policy, not vendor name
                 v
  placement -> reservation -> allocation -> lease/fence
                 |
                 | target/backend/provider binding
                 v
        DEPLOYMENT OCCURRENCE
          worker/executor/attempt
                 |
                 | observations, never invented claims
                 v
   runtime + usage + cost + energy + SLO receipts
```

The following are different identities and cannot share one `Resource` struct:

```text
ResourceClass       CPU time, exclusive GPU, memory capacity, network rate
ResourceId          one identifiable physical/logical allocatable resource
ResourceDemand      what a workload needs
ResourceOffer       what an allocator may offer during a validity window
ResourcePool        governed inventory and capacity ledger
Quota               authority limit; not physical availability
Budget/Precharge    finite consumption authority; not capacity
Reservation         temporary capacity hold
Allocation          committed assignment
Lease/FencingToken  temporary authority and stale-writer exclusion
UsageReceipt        observed consumption; not request or invoice
ProviderResource    provider-controlled identity
DeploymentOccurrence one realized deployment of a compiled plan
ControlPlaneProduct user-facing package; owns none of the above meanings
```

## Where pipelines, kernels, methods and compression belong

This runtime universe is necessary but does not absorb its neighbors:

```text
pipeline/workflow domain
    owns DAG meaning, data dependencies, triggers, backfills and business stage policy
    emits WorkUnits + dependency constraints
                         |
                         v
runtime domain owns attempts, workers, cancellation, checkpoint and receipts

algorithm/query/method domain
    owns the mathematical or query meaning
    compiles to immutable executable artifact + compute-kernel entry point
                         |
                         v
device runtime owns discovery, context, queue, dispatch, synchronization and resource use

encoding/compression domain
    owns codec, format, loss, ratio, fidelity, dictionary and compatibility semantics
    publishes kernel capabilities + CPU/memory/I-O cost model
                         |
                         v
runtime may place/execute the codec kernel but never chooses an undeclared lossy codec
```

“Kernel” is therefore two homonyms that must be separated:

- **compute kernel**: an executable entry point dispatched to CPU/GPU/accelerator;
- **operating-system kernel**: the privileged runtime enforcing processes, memory and I/O.

Scheduling methods such as bin packing, dominant-resource fairness, gang scheduling, min-cost flow,
backfill and randomized sampling are policy implementations. Their mathematical owners may live in
the operations-research universe; this universe owns the scheduler-policy contract, inputs,
guarantee vocabulary, decision receipt and effect boundary.

## Machine-readable contents

| Artifact | Meaning |
|---|---|
| `contexts.jsonl` | Bounded contexts with positive/negative scope and invariants |
| `types.jsonl` | Owned semantic types, equality, canonicalization and confusions |
| `state-machines.jsonl` | Total lifecycle candidates and race/outcome precedence |
| `resource-classes.jsonl` | Dimensions, units, shareability, divisibility, compressibility, topology and hazards |
| `scheduling-policies.jsonl` | Policy families with objective, inputs, guarantee and tradeoffs |
| `decision-points.jsonl` | Compiler-visible configurable choices using the shared decision contract |
| `libraries.jsonl` | Pure/mechanism/backend library boundaries and forbidden responsibilities |
| `requirements-offers-bindings.jsonl` | Reference compiler requirements, offers and deliberately unproven candidate bindings |
| `compiler-contract.json` | Runtime IR stages, proof gates, binding algorithm and forbidden shortcuts |
| `boundary-matrix.json` | Intent/mechanism/resource/provider/occurrence/product separation |
| `evidence.jsonl` | Scoped primary standards, official implementations and research papers |
| `innovations.jsonl` | Non-LLM innovations from 2021–2026 and compiler implications |
| `gaps.jsonl` | Blocking/degradable gaps with exact resolution conditions |
| `schemas/` | Context/type/lifecycle/resource-demand/resource-offer/receipt schemas |

All decision and library records are shaped to the shared contracts in
`research/domain_atlas/compiler/`. The reference bindings are `candidate`, not `proven`: primary
documentation is necessary evidence but does not substitute for exact target probes, conformance,
fault injection, adversarial races or production receipts.

## Library quality laws

Every reusable library boundary must satisfy these laws:

1. Pure semantic, policy and algorithm libraries perform no hidden I/O.
2. Runtime mechanisms accept explicit effect intents and emit typed receipts.
3. Provider adapters translate through an anti-corruption layer; provider names never enter owned
   semantic types.
4. All decision points have an owner, binding phase, allowed values, default law, consequences and
   invalidation semantics.
5. Every queue, retry loop, attempt count, time horizon and resource dimension is finite or refused.
6. Cancellation request, acknowledgement, stopping and terminal outcome remain separate.
7. Retry creates a new `AttemptId`; it never edits history.
8. Scheduler results state their assurance: optimal with proof, bounded gap, feasible, heuristic at
   budget, probabilistic, infeasible, timeout with/without incumbent, or failure.
9. Hard constraints are filtered before scoring and are never weakened to obtain a placement.
10. Requested, reserved, allocated, consumed, rated and billed quantities are separately typed.
11. A heartbeat proves observability, not useful progress.
12. A lease without enforcement at the protected effect is not fencing.

## Validation

```bash
python3 research/domain_atlas/universes/runtime_compute_resource/build_corpus.py
python3 research/domain_atlas/universes/runtime_compute_resource/validate_corpus.py
```

The validator checks identity uniqueness, internal references, lifecycle reachability, shared
decision/library shapes, requirement/offer/binding closure, evidence references, primary-source and
recent-innovation gates, explicit gaps and the non-LLM core boundary.

## Remaining research, not hidden by the passing validator

- cross-context ownership adjudication with pipeline/workflow, persistence, messaging, security,
  observability, FinOps, compression/encoding and operations-research universes;
- separate schemas for every aggregate command/event/refusal, not only the core carrier contracts;
- formal resource-vector algebra for substitutable, complementary, coupled and topology-dependent
  capacity;
- target-specific probes for NUMA, GPU partitions, CXL pools, WASI components, containers, VMs,
  edge devices and serverless runtimes;
- interference and tail-latency models for overcommit and shared accelerators;
- model checking for reservation/allocation/lease/fencing/cancellation races;
- benchmark envelopes and two independent implementations for each library contribution;
- product-boundary adjudication only after the horizontal context map is reconciled.

