# Lineage, provenance and evidence universe

This directory is a provider-neutral, open-world **candidate** corpus for enterprise data and
analytics. It covers lineage, provenance, derivation, claim–argument–evidence, attestations,
audit trails, runtime/compiler receipts, impact analysis, disclosure, custody, reproducibility,
correction, retraction, recall and forensic preservation. LLM, generative and agentic semantics
are excluded as core methods. Ordinary analytical model and study provenance is in scope.

No record here is an accepted bounded context, qualified provider, legal conclusion, evidentiary
admissibility decision or completeness proof. A source citation supports only its stated
`authority_scope`.

## Horizontal decomposition

```text
                        DECLARED / PROSPECTIVE
 source contract --> workflow plan --> transform/formula/schema plan
       |                   |                       |
       | acquire           | execute               | bind/compile
       v                   v                       v
 source occurrence --> run / attempt ----------> compiler receipt
       |                   | use/generate            |
       |                   v                         v
       +----------> runtime lineage ----------> runtime receipt
                           |                         |
             +-------------+-------------+           |
             v             v             v           |
       logical edge   physical edge   field edge     |
             \             |             /           |
              +------ provenance assertions --------+
                             |
                       provenance graph
                             |
               +-------------+-------------+
               |                           |
       impact / invalidation          claim / argument
               |                           |
     correction | retraction | recall      v
                                     evidence binding
                                           |
                 +-------------------------+----------------------+
                 |                         |                      |
             attestation            audit event/log/trail   reproduction
                 |                         |                      |
          independent appraisal     custody/preservation    rerun appraisal
                 \_________________________|______________________/
                                           |
                             relying decision / disclosure
```

Audit, provenance and evidence are linked neighbors, not synonyms:

```text
audit event/log/trail     records accountable actions and record changes
provenance graph          asserts entity/activity/agent relations
evidence bundle           packages materials offered for a precise claim
observability telemetry   samples operational behavior; not durable evidence by default
```

## Non-collapsible distinctions

| Left | Right | Boundary law |
|---|---|---|
| prospective lineage | retrospective lineage | Declared possibility does not prove execution. |
| logical lineage | physical lineage | Semantic dependency does not identify bytes or objects. |
| physical lineage | runtime lineage | Materialization identity is not occurrence identity. |
| data derivation | process execution | Entity dependency and activity occurrence need different evidence. |
| audit log | provenance graph | Accountability events and provenance relations keep distinct schemas. |
| provenance bundle | evidence bundle | A named provenance set is not automatically sufficient evidence. |
| assertion | attestation | An assertion need not be authenticated. |
| attestation | independent appraisal | Issuer-authenticated content is not independent evaluation. |
| identity/digest | truth | Integrity and identity do not prove correctness or truth. |
| recording time | validity | Capture time does not say when a claim applies. |
| correction | deletion | Amendment with history is not removal. |
| retraction | recall | Withdrawal from reliance is not downstream disposition. |
| telemetry | durable evidence | Evidence needs identity, integrity, coverage, retention and custody qualification. |

The metamodel also separates event, observation, recording, transaction, signing,
transparency-registration, validity, retrieval, appraisal, decision and disposition times.

## Evidence evaluation posture

`evidence-evaluation-model.json` evaluates one claim–evidence support edge for one relying policy
and decision time. It keeps these dimensions visible instead of publishing a universal score:

- authority: identity resolution, mandate, competence, independence, method authority and conflicts;
- strength: integrity, identity, directness, relevance, method quality, custody, corroboration,
  reproducibility and completeness;
- freshness: event/observation/recording/signing/registration/validity/retrieval/appraisal/decision
  time plus recheck triggers;
- defeaters: rebutting, authority, integrity, method, relevance, custody, freshness, coverage and
  conflict defeaters.

A relying policy may define gates or aggregation, but blocking failures cannot be silently offset.
A valid signature means the protected representation verified under a method; it does not mean the
claim is true or that the signer had authority for it.

## Compiler and runtime path

```text
analytical intent + policy + risk
                |
        derive requirements
                |
      discover versioned offers
                |
     match guarantees and limits
                |
   prove identity / time / authority /
     semantics / failure preservation
        |                     |
       pass                  gap
        |                     |
 insert capture + receipts   +--> refuse or authorized typed degradation
        |
 emit compiler receipt
        |
 execute --> runtime receipt --> evidence qualification/appraisal
```

The cross-plane registry maps source, pipeline, transformation, semantic-formula, model/study,
decision/action, security, governance, quality, runtime and compiler concerns. A mapping retains
each plane's identity, time, authority, granularity and evidence posture.

## Artifacts

- `metamodel.json` — scope, decomposition, time axes and constitutional distinctions.
- `bounded-context-candidates.jsonl` — 60 candidate ownership boundaries.
- `entity-types.jsonl` and `relation-types.jsonl` — 64 entity and 59 relation candidates.
- `capability-candidates.jsonl` — 217 candidates: 13 capability families, 156 operations,
  24 decisions and 24 laws.
- `evidence-evaluation-model.json` — authority, strength, freshness and defeater model.
- `invariants-refusals.jsonl` — 48 explicit invariants and refusals.
- `requirements.jsonl`, `offers.jsonl`, `compiler-mappings.jsonl` — 18 requirement/offer/binding
  patterns. Offers describe provider classes; they do not qualify a product.
- `cross-plane-mappings.jsonl` — 11 required horizontal integrations and receipts.
- `library-boundaries.jsonl` — 35 candidate pure/runtime/adapter/test boundaries.
- `innovations.jsonl` — 27 non-LLM developments from 2021–2026 with limits.
- `sources.jsonl` — 84 authority-scoped standards, specifications, official guidance and primary
  research records.
- `gaps.jsonl` — 25 unresolved semantic, evidence, time, privacy, runtime, forensic and governance
  gaps.
- `schema/` — 13 JSON Schemas for all JSONL record kinds.
- `build_corpus.py` and `validate_corpus.py` — deterministic generator and validator.
- `manifest.json` — exact generated-file counts and the explicit non-completeness claim.

## Generate and validate

From the repository root:

```bash
python3 research/domain_atlas/universes/lineage_provenance_evidence/build_corpus.py
python3 research/domain_atlas/universes/lineage_provenance_evidence/validate_corpus.py
```

The validator checks schemas when `jsonschema` is available, thresholds, uniqueness, references,
source authority breadth, candidate-only status, mandatory distinctions, cross-plane coverage,
evidence-model dimensions, forbidden core dependencies, manifest counts and byte-for-byte
deterministic regeneration.

Validated seed counts for edition 1 (generated 2026-08-25):

```text
84 sources
60 bounded-context candidates
64 entity-type candidates
59 relation-type candidates
217 capability/operation/decision/law candidates
48 invariant/refusal candidates
18 requirements + 18 offers + 18 compiler mappings
11 cross-plane mappings
35 library boundaries
27 innovations (2021-2026)
25 open gaps
13 schemas
```

## Honest limits

This is a finite research seed, not a closed universe. It does not prove that all lineage edges
were observed, that a provenance assertion is true, that evidence is admissible, that a provider
conforms, that a graph path caused an outcome, or that a reproduction target is scientifically
appropriate. Exact record/cell lineage, opaque systems, manual work, streaming retractions,
cross-system identity, sensitive graph disclosure, external-service reproducibility, clock trust,
long-term cryptographic agility and conflicting retention/erasure authorities remain material
gaps. Legal, regulatory, scientific and forensic uses require jurisdiction- and method-specific
expert review.

