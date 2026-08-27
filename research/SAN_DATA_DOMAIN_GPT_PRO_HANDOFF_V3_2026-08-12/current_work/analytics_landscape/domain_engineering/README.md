# Applied DDD model for the data, analytics, and engineering platform

This model applies domain-driven design, explicit temporal/data semantics, and Rust's useful
static guarantees to the platform described by the wider analytics research catalogue.

The domain vision is:

> Given an analytical intent and governed source facts, determine and retain the exact
> reproducible path from source cuts to analytical observations and, only through explicit
> authority, to business action.

Rust is an implementation and verification language for parts of this model. DDD is the method
used to discover the vocabulary, authority, boundaries, behavior, and invariants. A portable IR,
runtime evidence, and independent evidence are also required.

```text
world and experts
       |
       v
DDD discovery and domain specifications
       |
       v
Rust semantic crates + declarative graph/AST
       |
       v
semantic linker and composition compiler
       |
       v
verified application closure and lowered plan
       |
       v
providers, runtime execution, receipts, and evidence
```

The machine-readable companion is `data_platform_domain_model.json`. Validate its identifiers,
context references, relationship contracts, required tactical surfaces, and Rust/IR boundaries
with:

```bash
python3 research/analytics_landscape/domain_engineering/validate_domain_model.py
```

## Strategic decomposition

### Core subdomains

| Subdomain | Sovereign question |
|---|---|
| Sovereign semantics | What does each domain and data product mean, and who owns that meaning? |
| Intent compilation | Can declared analytical intent close into a complete, valid, explainable plan? |
| Analytical semantics | Which domain-neutral machines accept which semantic and structural contracts? |
| Safe decisioning | How may an analytical observation become a proposal, authorized command, and business fact? |

These are the differentiating parts of an intent-to-analytics compiler and should be built.

### Supporting subdomains

| Subdomain | Responsibility |
|---|---|
| Data engineering | Acquisition, admission, transformation, materialization, scheduling, and rebuild |
| Trust and governance | Quality, provenance, use, disclosure, retention, recall, and authority |
| Platform operations | Execution, observability, recovery, deployment, and cost |

### Generic subdomains

Storage engines, compute engines, queues, schedulers, identity authentication, secrets, networking,
and cloud deployment are generic facilities. The platform should buy, adopt, or conform to them
through provider ports. They must not own business or analytical meaning.

## Bounded contexts and semantic owners

| Bounded context | Owns | Explicitly does not own |
|---|---|---|
| Domain Specification | Vertical vocabulary, entities, events, rules, context mappings | Schemas, connectors, execution plans |
| Measurement and Type Semantics | IDs, units, dimensions, rates, probabilities, missingness | Industry-specific vocabulary |
| Source Estate | Source identity, authority, source objects, change semantics | Connector implementation |
| Provider Registry | Port implementations, limits, configuration and capability offers | Business meaning |
| Data Contract | Carrier schema, semantic references, grain, keys, time, quality obligations | Business ontology and physical snapshots |
| Data Product and Asset | Logical product, distribution, immutable snapshot, materialization | Transformation algorithm |
| Ingestion and Admission | Source cursor, hostile carrier, admission and quarantine | Source or contract ownership |
| Transformation and Build | Logical derivation, incremental semantics, build and commit proposal | Scheduling and final publication |
| Orchestration | Workflow, task dependency, trigger, retry, deadline and run | Meaning inside a task |
| Quality and Fitness | Metric, dimension, policy, measurement, assessment and certificate | Universal objective quality |
| Provenance and Lineage | Entity, activity, agent, usage, generation, derivation and attribution | Statistical causality |
| Catalog and Discovery | Searchable catalog projections and consumer feedback | Dataset or lineage truth |
| Metric Semantics | Measure, population, grain, filters, dimensions, aggregation and time | Dashboard and query-engine layout |
| Analytics Machine Registry | Typed machine ports, assumptions, output status and resource profile | Sports, oil, healthcare vocabulary |
| Analytical Intent | Question, population, horizon, constraints, output and human role | Provider or physical-plan selection |
| Composition Compiler | Requirement graph, candidate selection, gap, closure and lowering | Domain meaning and runtime state |
| Runtime Execution | Plan instance, attempts, checkpoints, commits, receipts and recovery | Plan semantics |
| Decision Gateway | Observation, proposal, approval, rejection and authorized command intent | Business aggregate mutation |
| Governance and Data Use | Purpose, classification, use grant, retention, disclosure and recall | Authentication implementation |
| Reliability and Economics | SLOs, budgets, measurements, cost attribution and incidents | Business quality meaning |
| Deployment and Control Plane | Desired/observed state, rollout, rollback, drift and health gates | Business mutation |

## Context map

```text
 DOMAIN SPECIFICATION                    MEASUREMENT SEMANTICS
 vocabulary + business meaning          units + semantic values
          |                                        |
          v                                        v
 ANALYTICAL INTENT -----------------------> DATA CONTRACT
 question + constraints                    schema + grain + time
          |                                        |
          |                                        +----> INGESTION
          |                                        |      raw -> admitted
          v                                        v
 COMPOSITION COMPILER <---- MACHINE REGISTRY   DATA PRODUCT / ASSET
 requirements + selection     typed analytics    logical + snapshot
       ^       ^                                      ^
       |       |                                      |
       |       +---- PROVIDER REGISTRY                |
       |              replaceable offers              |
       |                                              |
 GOVERNANCE POLICY                         TRANSFORMATION / BUILD
       |                                              ^
       v                                              |
 VERIFIED CLOSURE ----> DEPLOYMENT ----> RUNTIME -----+
                                           |
                    +----------------------+-------------------+
                    |                      |                   |
                    v                      v                   v
             PROVENANCE/LINEAGE      QUALITY/FITNESS   RELIABILITY/COST
                    |
                    v
              CATALOG PROJECTION

 ANALYTICS OUTPUT
       |
       v
 observation -> proposal -> DECISION GATEWAY -> authorized command
                                                |
                                                v
                                  owning business bounded context
```

The arrows are contracts, not shared internal data structures. Each crossing requires a
published language or an anti-corruption mapping.

## Canonical vocabulary distinctions

The compiler and all domain packs must preserve these distinctions:

```text
source system       != connector implementation
source object       != logical dataset
logical dataset     != distribution
distribution        != immutable snapshot
snapshot            != materialization location
data product        != table
contract            != observed conformance
schema              != semantics
field carrier       != semantic value type
row                 != declared grain
event occurrence    != transport message
workflow definition != workflow run
job definition      != job run
task                != task instance
transformation      != build run
metric definition   != metric observation
quality metric      != quality measurement
quality measurement != quality certificate
lineage             != statistical causality
catalog record      != sovereign asset
analytical result   != business fact
proposal            != authorized decision
plan                != execution
desired state       != observed state
freshness           != completeness
completeness        != finality
operator-state exactly-once != end-to-end exactly-once
```

## End-to-end behavior

```text
1. Publish domain meaning
2. Register source capability and evidence
3. Publish input/output data contracts
4. Publish analytical machine contracts
5. Declare analytical intent
6. Normalize intent
7. Resolve domain and semantic bindings
8. Select contracts, machines, providers and policies
9. Close resource, evidence and runtime obligations
10. Issue deterministic application closure
11. Lower closure to provider-neutral execution plan
12. Reconcile deployment
13. Acquire hostile source carriers
14. Admit or quarantine source occurrences
15. Transform exact input cuts
16. Commit immutable output snapshot
17. assess quality and record lineage
18. Execute analytics
19. Emit observation or proposal
20. Obtain authority through decision gateway
21. Issue command to the owning business aggregate
22. Retain execution, decision, lineage, quality and cost evidence
```

## Important aggregate state machines

### Data contract

```text
Draft -> Validating -> Validated -> Published -> Deprecated -> Retired
                     |                 |
                     |                 +----> Recalled
                     +----> Refused
```

### Asset snapshot

```text
Proposed -> Committing -> Committed -> Published -> Superseded
               |             |             |
               v             v             +----> Recalled
            Conflict      Quarantined
```

### Compilation

```text
Draft
  -> Normalized
  -> Resolving
       +-> AwaitingSelection
       +-> Gap
       +-> Exhausted
       +-> Refused
       `-> Closed
             -> Lowered
             -> Deployable
```

`Gap`, `AwaitingSelection`, `Exhausted`, and `Refused` are different outcomes.

### Execution

```text
Planned -> Admitted -> Queued -> Running -> Committing -> Succeeded
                                   |   |         |
                                   |   |         +-> CommitConflict
                                   |   +-> Checkpointed -> Recovering
                                   +-> Failed / Cancelled / TimedOut
```

### Analytical proposal

```text
Observation -> Proposal -> AwaitingDecision
                                |
             +------------------+------------------+
             |                  |                  |
          Approved           Rejected           Expired
             |
             v
   Authorized command intent
             |
             v
   business aggregate decides again
```

Approval does not bypass the business aggregate's own invariants or refusals.

## Data-platform constitution

1. Carrier, semantic value, observation role, dataset structure, analytics type, and vertical
   meaning are separate axes.
2. Schema conformance does not establish semantic correctness.
3. A raw carrier becomes an admitted value only through explicit validation with provenance.
4. Every snapshot pins its identity, contract edition, and source or derivation cut.
5. Corrections, retractions, deletion, supersession, and recall never silently overwrite history.
6. Every build pins code, configuration, input cuts, output contract, and assumptions.
7. Lineage establishes derivation, not causality.
8. Quality is assessed against a named purpose, metric, policy, and snapshot cut.
9. Every metric declares population, grain, measure, filters, aggregation, dimensions, and time.
10. Every analytics machine declares typed ports, assumptions, output status, determinism, and
    resource bounds.
11. Analytical observations and proposals cannot directly mutate business aggregates.
12. Compilation cannot succeed while a required semantic, contract, authority, provider,
    resource, or evidence obligation remains unresolved.
13. Exactly-once, freshness, completeness, quality and finality claims name their scope.
14. Provider-specific meaning cannot leak into semantic owners.
15. Every data use is scoped by purpose, subject, tenant, jurisdiction, valid time, and authority.
16. Revocation and recall propagate traceable obligations across derivation lineage.
17. There is no single `complete` boolean; completion is a vector of independently evidenced
    claims.

## Time model

```text
Source occurrence time     when the event happened at the source
Source recording time      when the source recorded it
Valid time                 when the fact applies in the domain
Observation time           when it was observed or measured
Ingestion time             when the platform received it
Processing time            when an operator processed it
Watermark time             the stream's declared progress in event time
Snapshot cut               the exact source/asset frontier included
Build nominal time         the logical interval a build represents
Run start/end              actual execution interval
Publication time           when an asset became available
Decision time              when authority made a decision
Policy effective time      when a policy or grant applies
Retention expiry time      when retention action becomes due
```

These must not be represented by one unqualified `Timestamp` type.

## Rust application

### Use Rust directly for

| Rust feature | Applied use |
|---|---|
| Newtype | `SourceSystemId`, `ContractId`, `SnapshotId`, `RunId`, `PurposeId` |
| Struct with private fields | Admitted value, aggregate state, verified closure, authority token |
| Enum | States, refusals, missingness, finality, update semantics, epistemic status |
| `Result` | Command acceptance or typed refusal |
| Exhaustive `match` | Decisions, reducers, transitions and compiler outcomes |
| Trait | Static capability or provider port |
| Associated types | Aggregate command/event/refusal and machine input/output families |
| Generics | `Observation<Subject, Measure>`, `Quantity<Dimension, Unit>` |
| Typestate | Draft-to-published contracts and unverified-to-deployable plans |
| Procedural macro | Descriptors, stable IDs, IR fragments, source maps and censuses |
| Property tests | Algebra, idempotency, mappings, metric aggregation, batch/stream equivalence |

Example aggregate boundary:

```rust
pub trait Aggregate {
    type Id: DomainId;
    type State;
    type Command;
    type Event;
    type Refusal;

    fn decide(
        state: &Self::State,
        command: Admitted<Self::Command>,
        context: &DecisionContext,
    ) -> Result<Decision<Self::Event>, Self::Refusal>;

    fn evolve(
        state: Self::State,
        event: &Admitted<Self::Event>,
    ) -> Self::State;
}
```

Example analytical output boundary:

```rust
pub enum EpistemicStatus {
    Description,
    Estimate,
    Forecast,
    Scenario,
    Recommendation,
    DecisionProposal,
}

pub struct AnalyticalObservation<T> {
    value: T,
    status: EpistemicStatus,
    subject_cut: SnapshotRef,
    method: MachineEditionRef,
    assumptions: AssumptionSet,
    uncertainty: Uncertainty,
    lineage: ProvenanceRef,
}
```

### Require declarative IR for

- vocabulary and ownership hypergraph;
- context map;
- contracts and schema descriptors;
- transformation DAG;
- predicates, policies and decisions;
- machine ports and wiring;
- provider offers and requirements;
- lineage graph;
- resource expressions;
- lowering plan;
- completion and evidence graph.

Arbitrary Rust functions are not a portable or explainable IR.

### Require runtime evidence for

- source availability;
- actual data quality;
- stream watermark progress;
- provider health;
- commits and effect receipts;
- service-level measurements;
- actual cost and resource use;
- drift, incidents and recovery.

### Require human or independent evidence for

- domain-expert agreement;
- legal authority;
- regulatory interpretation;
- measurement calibration;
- statistical-assumption validity;
- independent certification.

## Recommended crate boundaries

```text
constitution/
    sspec-core
    domain-ir
    domain-macros
    semantic-linker

semantics/
    sem-identity
    sem-time
    sem-measurement
    sem-missingness
    sem-provenance

platform-domain/
    source-estate
    data-contract
    data-product
    ingestion-admission
    transformation-build
    orchestration
    quality-fitness
    provenance-lineage
    metric-semantics
    analytics-machines
    analytical-intent
    composition-compiler
    decision-gateway
    governance-data-use

runtime/
    provider-ports
    execution-kernel
    deployment-control
    reliability-economics

verticals/
    sports-*
    oil-and-gas-*
```

The same context should not be divided into one crate per entity. A crate is useful as a
publishable authority boundary, not as a mechanical synonym for every DDD pattern.

## First executable vertical

Build one vertical twice, once for sports and once for oil and gas:

```text
SPORTS
tracking occurrences -> player-load snapshot -> change detection -> workload proposal

OIL
sensor occurrences -> well-production snapshot -> change detection -> inspection proposal
```

Both must reuse the same domain-neutral machines:

```text
admission
windowing
aggregation
change-point detection
uncertainty calculation
proposal emission
```

Only these should change:

- vocabulary;
- source and field mappings;
- units;
- metric definitions;
- domain thresholds;
- use policies;
- approval authority;
- downstream business command.

The proof is successful only if the horizontal machine definitions remain unchanged and both
verticals produce complete lineage, quality, decision, cost, and runtime receipts.

## Primary research alignment

- OpenLineage separates datasets, jobs, runs, and extensible facets.
- W3C PROV separates entities, activities, agents, generation, usage, and attribution.
- W3C DCAT separates datasets, distributions, data services, series, and catalog records.
- W3C DQV separates quality dimensions, metrics, measurements, policies, and certificates.
- ODCS provides a platform-neutral data-contract vocabulary covering schema, quality, ownership,
  service levels, infrastructure, and extensions.
- Apache Iceberg demonstrates immutable snapshots, atomic metadata commits, stable field identity,
  schema and partition evolution, and time travel.
- Apache Flink makes event time, watermarks, replay, checkpoint scope, and end-to-end guarantees
  explicit.
- OpenTelemetry provides correlated traces, metrics, logs, resources, and semantic conventions for
  runtime evidence.

These standards inform the context contracts. None of them replaces the platform's sovereign
domain model.
