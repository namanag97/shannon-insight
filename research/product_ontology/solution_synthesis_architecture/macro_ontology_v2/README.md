# Macro ontology v2 — executable solution-synthesis control model

Status: **RESEARCH_CANDIDATE / UNRATIFIED**  
As of: **2026-08-28**

This upgrade turns the solution-synthesis macro model into an ontology-and-control architecture rather than another flat taxonomy. It preserves the existing sovereign-product DDD dossiers and adds the cross-product semantics required to prevent product, capability, implementation, runtime occurrence, authority and acceptance from collapsing into each other.

## Current research build

The full deterministic research artifact for this edition validates at:

```text
12 viewpoints
9 responsibility layers
8 flow lanes
8 active control planes
13 cross-layer fabrics
11 orthogonal state dimensions
24 authority/operating roles

750 noun-sense candidates / 734 noun lexemes
389 verb-sense candidates / 378 verb lexemes
27 explicit lexical ambiguities
211 typed relation candidates
51 non-collapse laws

28 IR stages
20 hypergraph closure joins

219 primary/official sources
  45 standards/specifications
  127 official product/technology documents
  39 primary academic/research publications
  8 first-party expert/architecture sources
433 evidence tags

66 retained-product ontology projections
775 flattened product-noun candidates
493 flattened product-verb candidates
```

These are ratchet counts, not completeness claims. No count implies ratification, product qualification, provider qualification or executed vertical acceptance.

## Seven independent coordinates

```text
viewpoint      whose concern is being answered
layer          where responsibility lives
lane           how meaning/data/work/decision/effect/evidence/economics flows
control plane  what actively governs change, admission, authority and convergence
fabric         what semantic context propagates across affected layers
state vector   which independent lifecycle/control state a subject occupies
role           who owns, supplies, operates, decides, qualifies and accepts
```

A product can participate in several lanes and control planes while remaining one product. A fabric is not a product. A layer is not a compiler pass. A role name grants no authority until bound in scope. A generic `status` field cannot replace independent state machines.

## Eight control planes

1. Semantic authority
2. Compatibility and evolution
3. Service envelope and economics
4. Policy, authorization and disclosure
5. Resource admission and scheduling
6. Runtime reconciliation
7. Qualification and assurance
8. Open-world research and ontology extension

Compatibility does not belong to persistence merely because versions are stored. Economics does not belong to telemetry merely because telemetry measures it. Desired state does not belong to an executor merely because the executor applies it.

## Thirteen fabrics

```text
identity / namespace
temporality
version / edition / digest
provenance / lineage / custody
classification / policy / privacy
trust / security
uncertainty / quality / confidence
observability / telemetry
tenancy / organizational scope
units / currency / locale
ordering / consistency / finality
locality / topology / residency
representation / carrier / fidelity
```

The last three are evidence-backed promotions from the wider data-system and CS research pass.

## Eleven state dimensions

```text
semantic governance
artifact evolution
synthesis / binding
authority / effect
resource admission
runtime execution
visibility / finality
service envelope
reconciliation
assurance / acceptance
migration / exit
```

This prevents `authorized`, `allocated`, `running`, `durable`, `visible`, `final_for_scope`, `within_envelope`, `converged`, `qualified` and `accepted` from becoming aliases for one generic `READY` or `COMPLETE` state.

## High-risk non-collapse laws

Representative laws include:

```text
object type != object occurrence
action type != action occurrence
function interface != function implementation
definition != occurrence
observation != claim != decision
decision != authorization != effect != outcome
schema != data contract
logical view != materialized view
semantic equivalence != physical equivalence
offset != event time
watermark != completeness cut != finality
durability != visibility != finality
consistency model != delivery semantics
checkpoint != backup != retention
region != residency != jurisdiction
tenant != organization != authorization scope
SLO target != metric sample
provenance != audit event != assurance appraisal
qualification != vertical acceptance
prediction/score/forecast != decision/commitment
product != capability != library != implementation
provider offer != qualified offer
```

## IR promotions

The 28-stage IR includes explicit responsibility for:

```text
SemanticAuthorityIR
CompatibilityEvolutionIR
ServiceEnvelopeIR
PolicyAuthorizationIR
ResourceAdmissionIR
ConsistencyVisibilityIR
LocalityResidencyIR
RepresentationFidelityIR
RuntimeReconciliationIR
RuntimeObservationIR
OntologyResearchIR
```

The 20 closure joins require consistency/visibility, locality/residency, representation/fidelity and authority/effect to close across their owning IRs rather than hiding them inside storage, deployment or telemetry.

## Product ontology rule

The canonical source is `research/product_ontology/dossier_readiness/product-readiness.jsonl`. This edition has 66 retained-product projections. The fallback `product_projection_seed.py` exists only for isolated rebuilds and must never override canonical dossier readiness.

A product projection may propose nouns and verbs, but it cannot ratify product ownership, identity, grain, time, lifecycle, invariants or action authority. Homonyms remain explicit until the owning domain/product authority resolves them.

## Research posture

The research sweep spans standards/formal semantics; warehouses/lakehouses/query engines; streaming/CDC/integration/orchestration; governance/catalog/semantic/quality systems; ML/model/feature serving; search/vector/graph/time-series systems; distributed databases; cloud locality/residency; ontology-driven enterprise platforms; foundational database/distributed-systems papers; and first-party expert architecture work.

Vendor packaging is evidence of independently recurring seams, not authority to create a Shannon product boundary. Unknown legitimate meaning is routed through the open-world research control plane rather than silently guessed.

See `RESEARCH-SYNTHESIS.md` for the evidence-derived changes and `macro-model.json` for the compact machine-readable macro summary.
