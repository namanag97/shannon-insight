# Research synthesis — why the macro model changed

This note summarizes the evidence-derived changes in the macro ontology v2 research pass. The complete generated deliverable contains the source registry and source-to-topic evidence projection as JSONL.

## 1. The architecture needs an upper ontology, not only product dossiers

Across formal ontology standards, semantic systems and enterprise ontology products, the same rule recurs: types, occurrences, links/relations, actions and functions/interfaces require different identity and lifecycle semantics. A product dossier can own a bounded language, but the portfolio also needs an upper vocabulary that prevents two products from independently using the same word for incompatible things without an explicit mapping.

The model therefore separates noun senses, verb senses and relation types. Shared surface words are explicit lexical ambiguities; string equality never proves semantic equality.

## 2. Definition, occurrence and representation are three different planes of meaning

Database formats, schema systems, semantic layers, materialized views, indexes, streams and codecs repeatedly show that a definition is not a runtime occurrence and neither is identical to its physical representation. Physical forms may be lossless, lossy, canonical, indexed, cached or materialized while preserving only some semantic contract.

This becomes the **Representation / Carrier / Fidelity fabric** and `RepresentationFidelityIR`.

## 3. Ordering, consistency, visibility and finality cannot be hidden inside streaming/storage

Lamport ordering, distributed snapshots, Kafka delivery/commit semantics, Beam/Flink event time and watermarks, MongoDB resume/majority-commit behavior, Cassandra consistency, Milvus visibility levels and Paimon snapshot/changelog semantics expose separate concepts:

```text
source order
happens-before
event time
delivery semantics
read/write consistency
durability
visibility
watermark/completeness frontier
scoped finality
```

The corpus therefore adds the **Ordering / Consistency / Finality fabric**, `ConsistencyVisibilityIR`, a visibility/finality state dimension, and non-collapse laws such as `watermark != finality` and `durability != visibility`.

## 4. Locality and residency participate in correctness

Cloud regions/zones, distributed database placement, geo-replication, regional endpoints and data-residency controls show that topology is not one string called `region`. Failure domain, latency locality, storage/processing residency, sovereignty boundary and legal jurisdiction can diverge.

The corpus therefore adds the **Locality / Topology / Residency fabric** and `LocalityResidencyIR` so physical binding cannot close until these obligations reconcile with policy and resource placement.

## 5. Service objectives are declarations, not telemetry

Google SRE/OpenSLO plus warehouse/streaming/runtime systems distinguish objective, indicator, measurement window, error budget, resource envelope and observed samples. A target cannot be inferred from current telemetry, and a current measurement cannot silently become acceptance.

The Service Envelope control plane remains first class and now has its own state dimension from target declaration through indicator binding, measurement, budget burn, violation, waiver and remediation.

## 6. Resource admission is not runtime execution

Schedulers, Kubernetes-style controllers, query engines and distributed runtimes distinguish demand, offer, reservation, allocation, placement, execution and accounting. The earlier runtime state vector mixed several of these phases.

The corpus separates **resource-admission state** from **runtime-execution state**, while Runtime Reconciliation remains a third independent state machine over desired versus observed configuration.

## 7. Decision, authorization and effect must be independently attributable

Policy engines, decision models and enterprise action systems repeatedly separate a proposal or analytical result from a decision, a decision from authorization, and authorization from an external side effect. This is essential for auditability, revocation, compensation and human authority.

The corpus therefore adds an explicit authority/effect state dimension and a closure join spanning application behavior, policy authorization, effect semantics and receipts.

## 8. Compatibility is a semantic/evolution responsibility

Schema registries, data contracts, ingestion systems, APIs and versioned storage all expose compatibility, but storage/versioning alone cannot decide whether a change preserves a consumer promise. Compatibility therefore remains a macro control plane with its own IR and migration/exit state rather than a persistence feature.

## 9. Provenance, audit, conformance, qualification and acceptance remain separate

PROV/OpenLineage-style derivation evidence, runtime telemetry, audit records, conformance tests, independent appraisal and domain acceptance answer different questions. The macro model keeps evidence production from becoming its own verdict and refuses qualification as a substitute for executed vertical acceptance.

## 10. Product ontologies are projections, not copies of the upper ontology

Every retained product projects a candidate noun/verb vocabulary from its canonical dossier/capability references plus family semantics. The projection records all shared fabrics/control planes/state applicability, but only the product/domain authority can ratify exact identities, grains, lifecycles, invariants, action authority and mappings.

The shared ontology prevents accidental collapse; the product ontology owns bounded meaning; vertical packs specialize it; implementations realize exact contracts. None of those layers is allowed to impersonate another.

## Research posture

This edition surveyed 219 primary or official sources: 45 standards/specifications, 127 first-party product/technology documents, 39 primary academic/research publications, and 8 first-party expert architecture sources. It is a broad saturation pass, not a claim that every data company or paper on Earth has been read. New evidence remains admissible through the open-world research control plane.
