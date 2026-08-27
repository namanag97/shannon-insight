# Universal data and analytics domain atlas

This is the upstream semantic/domain map required before product boundaries can be derived. Its
scope is every reusable horizontal concern needed to produce trustworthy analytics for arbitrary
enterprise domains. It does not attempt to hard-code every industry's vocabulary or every
possible formula.

## The universality strategy

Literal knowledge of every enterprise and future analytical need is impossible. The achievable
contract is:

```text
small closed metamodel
+ versioned horizontal bounded-context contracts
+ open vertical ontology/domain packs
+ open formula/method/provider registries
+ deterministic closure and explicit gaps
= extensible analytical solution compiler
```

Unknown meaning is a typed compiler gap or human-resolution obligation, never a guessed mapping.

## Analytical solution closure

For an analytical solution to close, the compiler must retain evidence for all of these:

```text
01 intent closure          question, decision, outcome, actors
02 vocabulary closure      every term has one owner in context
03 identity closure        subjects, objects, events, datasets, editions
04 type closure            carrier, semantic type, unit, missingness
05 observation closure     feature, property, procedure, result, uncertainty
06 grain closure           population, entity, event, grouping, cardinality
07 time closure            valid, occurrence, recording, ingestion, cut, horizon
08 source closure          authority, cursor, change mode, completeness/finality
09 transformation closure  mapping, operators, loss, incremental/rebuild behavior
10 data-product closure    contract, exact cut, snapshot, distribution, publication
11 semantic closure        facts, dimensions, measures, metrics, joins, formulas
12 study closure           design, population, assumptions, estimator/method
13 decision closure        objective, constraints, alternatives, proposal/action path
14 authority closure       purpose, tenant, jurisdiction, grant, approval, revocation
15 execution closure       provider capabilities, ordering, retries, commits, recovery
16 resource closure        capacity, quotas, latency, throughput, cost, cancellation
17 trust closure           quality, lineage, reconciliation, uncertainty, disclosure
18 evidence closure        claims, sources, runtime receipts, proofs, defeaters
19 evolution closure       compatibility, migration, backfill, replay, recall, exit
20 human closure           judgment, explanations, appeals, accessibility, support
```

“Compilation succeeded” is illegal while any required closure dimension is unresolved.

## Orthogonal graphs

```text
Vertical domain graph      enterprise meaning: claim, patient, order, well, player...
Horizontal context graph   reusable semantic and operational ownership
Analytical method graph    formulas, estimators, solvers, assumptions and evidence
Data estate graph          sources, cuts, contracts, assets and lineage
Product graph              user/outcome/adoption/lifecycle promises
Implementation graph       machines, libraries, modules, providers and targets
Research graph             people, exact artifacts, claims, algorithms, evidence, limitations
Change graph               monitored subjects, observations, verified changes, invalidations
```

These graphs are linked by explicit mappings. They must never be collapsed into a single `type`
or inheritance tree.

## Predictive models and optional agents

Classical and modern predictive/statistical machine learning belongs in the analytical-method
graph. It is decomposed from prediction target and study design through model, estimator,
objective, training/inference algorithm, kernels, fitted artifact, calibration, evaluation,
deployment decision and monitoring. A model family name is not a complete analytical contract.

Generative models, LLMs and tool-using agents are covered by a separate optional extension graph.
The extension imports the deterministic core; the core does not import it. Model output, agent
plan, validated claim, authorized effect intent and effect receipt remain separate states. This
prevents an `AI` branch from being copied into every bounded context while still allowing the
capability to be selected where an intent actually requires it.

Formal optimization, constraint, control and simulation models have a separate deterministic
classification graph under `compiler/model_class_adjudication/`. It derives multi-axis class facets
from closed typed facts and keeps every transformation's equivalence, relaxation, approximation or
statistical relation explicit. Predictive artifacts may supply governed inputs and optional agents
may propose models or rewrites; neither can prove a class, transformation, provider qualification or
effect authority.

## Current files

- `DOMAIN-ATLAS-METAMODEL.md` — candidate bounded-context identity and DDD requirements.
- `axis-taxonomy.json` — enumeration and coverage axes used to find missing contexts.
- `context-families.json` — first-pass families and expected candidate counts.
- `coverage-planes.jsonl` — governed horizontal coverage and honest per-plane status.
- `RESEARCH-EXECUTION-DAG.md` — research waves, promotion gates and budget-allocation law.
- `industries/` — classification foundation, vertical analytical cases and reference-adjudication queue.
- `universes/` — open registries for sources, types/shapes, operations, methods and execution concerns.
- `universes/application_behavior/` — candidate application commands, queries, state, workflow,
  event, projection, effect-handoff and execution-evidence contracts, with explicit non-compiler
  assembly edges and fail-closed qualification accounting.
- `compiler/` — closed requirement/offer/binding metamodel and proof obligations.
- `ecosystem/` — specialists, exact expert/research contributions and recurring change intelligence.

The next registry iterations must adjudicate candidate identity and ownership, bind vertical
references loss-aware, and produce executable conformance evidence. Family membership is not proof
that a candidate deserves its own bounded context.
