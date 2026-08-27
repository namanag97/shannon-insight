# Provenance/evidence and quality/reconciliation research lane — output

## Scope

Independent boundary/provenance/quality research for the two complete families
`lineage_provenance_evidence` (31 libraries) and `quality_reconciliation` (37 libraries):
68 assigned `library_ref` values from the exact-API closure program's `research-batches.jsonl`.
The lane produces evidence packs, falsifiable semantic modules, per-library applicability
projections, changed-boundary migrations, semantic contract *requirements* (not APIs), a
conflict/vacancy register, an acyclic gap dependency graph and a machine-readable
(non-authoritative) merge-candidate queue. Nothing is ratified, implemented or qualified.

## Method

1. Input snapshot: 15 authoritative inputs digested (`input_snapshot` in coverage-report.json).
2. Ontology-first: 37 reusable propositions (7 global primitives, 7 cross-family, 17 family-axis,
   6 local refinements) researched against primary standards/papers; every module carries bounded
   claims, counterexamples and an authority limit; statuses stay CANDIDATE_UNRATIFIED/BLOCKED.
3. Projection: each library receives one boundary adjudication plus explicit rows for every
   considered module (no silent NOT_APPLICABLE by absence).
4. Falsification: counterexamples recorded per decision; checkpoint defects found via live web
   verification were repaired rather than inherited (see corrections below).
5. Deterministic regeneration: `python3 build_corpus.py` then `python3 validate.py`.

## Verification of sources (accessed 2026-08-26)

Primary pages fetched live: OpenLineage object model shows version **1.52.0** with
RunEvent runtime vs JobEvent/DatasetEvent design-time separation; W3C RDFC-1.0 is a
Recommendation of 21 May 2024; OMG SACM 2.3 formal October 2023; RFC 9943 SCITT +
RFC 9942 COSE Receipts are Proposed Standards (2026); FDA CGMP data-integrity Q&A final
December 2018; XBRL Formula 1.0 Recommendation **22 June 2009**; RO-Crate 1.1 published
**30 October 2020** (superseded by later editions); PREMIS 3.0 official LOC v3 landing.
ISO/IEC 25012/2859-1/27037 full texts remain paywalled and are carried as typed vacancies,
never as fabricated content. An earlier secondary ISO-25012 portal source was dropped after
returning HTTP 404 during this run.

## Checkpoint repairs applied by this completion stage

Falsified CSAF-recall clauses replaced (CSAF 2.0 has no recall product status); XBRL Formula
date corrected to 2009; RO-Crate date corrected to 2020-10-30; iso25000.com overview source
removed; PREMIS URI moved to LOC v3 landing; added CSAF 2.0, RFC 9942, RFC 5424 and GDPR
sources underwriting lifecycle/receipt/custody adjudications.

## Ten most consequential boundary corrections

1. `library.lpe.lineage-core` SPLIT: logical statements vs vendor encoding helpers vs field grain
   had different owners and change cadences; responsibilities mapped with no aliases.
2. `library.lpe.record-lifecycle` SPLIT: correction/supersession separated from retraction and from
   erasure/recall dispositions that import external legal authorities (GDPR vs retention regimes).
3. `library.qor.quality_dimension_metric_kernel` SPLIT into DQV's Dimension/Metric/Measurement trio.
4. `library.qor.completeness_timeliness_kernel` SPLIT blocked on ISO 25012 full text but never
   collapsed into one "DeliveryQuality" score.
5. `library.lpe.openlineage-adapter` RENAME to `runtime-lineage-event-adapter`: a project name on an
   adapter can masquerade as a semantic owner.
6. `library.qor.certification_attestation_kernel` NARROWED: quality certification must not own
   cryptographic Statement construction (cross-family Attestation homonym quarantine).
7. `library.qor.evidence_receipt_kernel` NARROWED: quality evaluation evidence is not a PVD receipt;
   inclusion proofs stay in `receipt-store` (RFC 9942/9943 vs DQV annotation traditions).
8. `library.lpe.evidence-evaluation` NARROWED to SACM-style strength scoring; RATS message typing
   migrated out, keeping two appraisal traditions non-collapsed.
9. `library.qor.duplicate_entity_resolution_kernel` NARROWED: confidence scores can never authorize
   merges; execution moves behind the authorized-change boundary.
10. `library.qor.lineage_quality_impact_kernel` NARROWED: staleness invalidation consumes LPE slice
    witnesses instead of sharing one "Impact" public type.

## Ten most dangerous unresolved gaps

1. `gap.owner.erasure-retention-precedence` — GDPR-class erasure vs WORM preservation vs holds.
2. `gap.symbol.cross-context-homonyms` — 27 p0 collisions touching assigned libraries, all UNRESOLVED.
3. `gap.owner.contract-ir-selection` — ODCS/OpenAPI/data-contract-spec competition blocks declaration kernels.
4. `gap.conflict.two-appraisal-traditions` — RATS protocol appraisal vs SACM scoring vocabularies.
5. `gap.evidence.iso25012-fulltext` — paywalled standard text freezes three kernel splits.
6. `gap.coverage.runtime-receipts-universe-only` — owner-universe receipt libraries absent from queue.
7. `gap.auth.materiality-policy-sources` — no ratified materiality policy register.
8. `gap.owner.match-merge-authorization` — approved-match authority lives outside both families.
9. `gap.auth.audit-admissibility-jurisdictions` — audit trails lack jurisdiction authority bindings.
10. `gap.semantic.freshness-currentness-vocabulary` — terminology cannot freeze pre-review.

## Five findings most likely to change compiler/library architecture

1. Boundary grammar is unified across families: RETAIN/SPLIT/RENAME/REPLACE adjudications produce
   responsibility-migration graphs the compiler can execute as deterministic re-plans without aliases.
2. Receipt/evidence/attestation carriers need family-qualified names because RFC 9942 receipts,
   in-toto statements and DQV certificates are different publics sharing vocabulary.
3. Effect discipline (`pure_effect_intents`) proved uniform: every governance kernel is pure between
   editions and effect-bearing only at authority-imported commit ports.
4. Homonym governance (p0) is upstream of contract generation: until symbol owners are ratified,
   any shared-type optimization collapses distinct semantics.
5. The QOR/LPE split is real at impact boundaries: lineage topology services witness quality-staleness
   propagation but never compute it, implying cross-family ports rather than merged kernels.

## Validation

`python3 validate.py` proves ref coverage/uniqueness, source resolution, evidence-or-vacancy on
nontrivial decisions, migration completeness for changed boundaries, applicability completeness,
module boundedness, acyclic gap graph, homonym guards, effect separation, authority naming,
deterministic ordering, snapshot digest binding, merge-candidate atomicity/digests, no-standard-as-SAN-owner,
and completion_claim=false. Failures are reported, never silenced by weakening laws.

## Limitations

Paywalled ISO texts are vacancies, not assumptions; ISO 27037/2859 numbers cite landing pages only.
Legal precedence questions are registered, not resolved. The telemetry-family target owner lies
outside assigned lanes. Queue-level coverage of universe receipt libraries is asserted incomplete.
All artifacts are CANDIDATE_UNRATIFIED research output.
