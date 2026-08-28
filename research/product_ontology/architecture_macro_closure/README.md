# Enterprise data + analytics macro architecture closure

Status: **CANDIDATE_STRUCTURALLY_COMPLETE / NOT RATIFIED / NOT QUALIFIED**

This package consolidates the repository's product ontology, context map, source-system universe, data-shape universe, analytical-method corpus, application-behavior model, compiler/planner/reconciler model, runtime/evidence model, economics/capacity constraints and B00-B20 closure DAG into one architecture-level contract.

The purpose is to finish the architecture before spending months on individual vendor claims, implementation receipts, or product-level qualification minutiae.

## Architecture completion meaning

`CANDIDATE_STRUCTURALLY_COMPLETE` means:

- every macro responsibility has one architectural home;
- provider-neutral meaning is separated from provider offers and deployed occurrences;
- source, access surface, connector, acquisition plan and governed cut are distinct;
- semantic value, logical shape, physical representation and storage layout are distinct;
- analytical method, operated analytical lifecycle, result, recommendation, judgment, authorization, effect and outcome are distinct;
- application-domain products and data/analytics-platform products remain distinguishable;
- compiler, planner/synthesizer, authority adjudication, compatibility evaluation, reconciler, runtime, assurance and open-world research are separate mechanisms;
- desired state is separate from workload execution and observed state;
- schema compatibility is separate from semantic compatibility;
- cost/capacity/SLO constraints are explicit during planning, binding, runtime and evolution;
- human work, policy, security, privacy and evidence are not collapsed into algorithm or workflow semantics;
- two-release change, decommission and open-world novelty are first-class architecture stages;
- every remaining unresolved item can be classified as authority, evidence, implementation, provider, occurrence, qualification, vertical acceptance, economics/capacity, or open-world extension rather than an unowned architectural hole.

It does **not** mean the architecture is ratified, implemented, portable, physically proven, vertically accepted, build-ready or commercially validated.

## The 27-plane architecture is a graph, not a pipeline

```text
                         ┌───────────────────────────────┐
                         │ SEMANTIC + AUTHORITY PLANE    │
                         │ A01 mandate/discovery         │
                         │ A02 business/industry meaning │
                         │ A03 product/context ownership │
                         │ A05 human/app requirements    │
                         │ A06 policy/security/safety    │
                         │ A18 adjudication/PackageLock  │
                         └──────────────┬────────────────┘
                                        │
                                        v
┌───────────────────────────────┐   ┌───────────────────────────────┐
│ DATA + ANALYTICS PLANE        │   │ SYNTHESIS + BUILD PLANE       │
│ A04 source requirements       │   │ A17 planner/synthesizer       │
│ A07 source classes            │──►│ A19 deterministic compiler    │
│ A08 offer/occurrence/access   │   │ A25 contract/schema evolution │
│ A09 acquisition/governed cut │   │ A27 economics/capacity/SLO    │
│ A10 values/logical shapes     │   └──────────────┬────────────────┘
│ A11 persistence/representation│                  │
│ A12 metadata/lineage/quality  │                  v
│ A13 query/method kernels      │   ┌───────────────────────────────┐
│ A14 analytical study          │   │ OPERATION + EVIDENCE + CHANGE │
│ A15 result→judgment→auth      │   │ A16 effect/outcome            │
└──────────────┬────────────────┘   │ A20 env binding/runtime       │
               │                    │ A21 assurance/system accept   │
               └───────────────────►│ A22 continuous validity       │
                                    │ A23 migration/decommission    │
                                    │ A26 desired-state reconciler  │
                                    └──────────────┬────────────────┘
                                                   │
                                                   v
                                    ┌───────────────────────────────┐
                                    │ OPEN-WORLD CHALLENGE          │
                                    │ A24 novelty/extension         │
                                    └───────────────────────────────┘
```

The graph is intentionally cyclic at the **program** level but not at artifact identity level: evidence can trigger revalidation and revision, while prior immutable artifacts retain predecessor identity.

## Artifact progression

```text
CustomerMandate
→ DiscoveryDossier
→ SolutionIntent
→ ProductCompositionIntent / ContractGraph
→ SourceBindingPlan / AcquisitionPlan / GovernedDataCut
→ AnalyticalStudyDefinition / Run / Result
→ Recommendation → Judgment → Authorization
→ EffectIntent → ExecutionOccurrence → OutcomeEvidence
→ SolutionPlan
→ PackageLock
→ AppRelease
→ EnvironmentBinding
→ ApplicationOccurrence
→ RuntimeEvidence
→ AcceptanceReceipt
→ ValidityState
→ RevisionMandate
→ next edition
```

Each arrow is directional. No successor overwrites the identity or authority of its predecessor.

## Architectural non-collapse laws

The complete machine-readable set is in `cross-plane-laws.jsonl`. Important examples:

```text
business meaning              != storage representation
logical shape                 != physical format
source-system class           != provider product
deployed occurrence           != access surface
access surface                != connector
connector                     != successful acquisition
acquisition plan              != governed data cut
lineage                       != correctness
provenance                    != truth
method kernel                 != analytical study
result                        != recommendation
recommendation                != judgment
judgment                      != authorization
authorization                 != effect
execution receipt             != accepted business outcome
workflow                      != dataflow
compensation                  != rollback
planner                       != compiler
compiler                      != reconciler
reconciler desired state      != runtime observed state
schema compatibility          != semantic compatibility
SLO objective                 != measured SLI
planning estimate             != billed cost
same-campaign tests           != independent qualification
structural vertical mapping   != executed vertical acceptance
release                       != deployment
successful boot               != accepted system behavior
finite registry               != closed-world completeness
```

## Mechanism separation

`mechanism-separation.jsonl` defines nine deliberately separate mechanisms:

1. open-world research;
2. authority adjudication;
3. planner/synthesizer;
4. deterministic compiler;
5. desired-state reconciler;
6. runtime execution;
7. assurance/appraisal;
8. continuous-validity engine;
9. contract-compatibility engine.

No one mechanism is allowed to absorb the authority or proof obligations of another.

## External architecture anchors

The architecture deliberately imports standards rather than re-owning their semantics. Examples include:

- Apache Arrow for columnar in-memory representation and IPC, while leaving mutation coordination and business semantics elsewhere.
- Apache Iceberg for versioned analytical table-format semantics, schema/partition evolution, snapshots and catalog protocols, without making the table format the owner of business meaning.
- OpenLineage for run/job/dataset lineage event exchange and facets, without treating lineage as correctness or authority.
- OpenTelemetry for technical traces, metrics, logs, profiles and semantic conventions, without making telemetry the business event model.
- W3C PROV-DM for provenance entities/activities/agents, without treating provenance as truth or assurance.
- OCEL 2.0 for object-centric event-log exchange, without making OCEL the owner of enterprise object semantics.
- Cedar / OPA-style policy engines for policy evaluation, while preserving authentication, policy authorship, authorization occurrence and effect execution as separate concerns.
- OpenAPI / CloudEvents-style representation standards for API/event envelopes, without conflating transport schema with domain semantics.

## Existing repository coverage retained

This package does not replace existing corpora. It binds them at architecture level:

- 66 retained products, all with candidate DDD dossiers, explicit library attribution and compiler maps;
- 144 global candidate contexts and 308 relations;
- 171 provider-neutral source-system classes across 17 families;
- 77 semantic value types and 177 logical data shapes across 31 shape families;
- 682 current library signatures across 16 semantic axes;
- B00-B20 dependency-ordered closure program, including open-world novelty, synthesis, application/human authority, multi-product system acceptance and continuous validity.

`architecture-universe-coverage.jsonl` stress-tests the model against these entire universes rather than selected examples.

## What remains after architecture closure

The remaining work is deliberately downstream:

1. named authority ratification;
2. exact evidence replacement and independent verification;
3. implementation identities and reproducible builds;
4. independent conformance and second implementations;
5. provider/occurrence and physical SLO/security/cost evidence;
6. executed vertical acceptance;
7. two-release migration/decommission proof;
8. ongoing open-world challenge campaigns.

Those tasks can change evidence, implementations, provider bindings, acceptance state or even force a future architectural revision. They do not justify leaving the present macro architecture undefined.
