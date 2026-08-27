# Research artifact → compiler/library knowledge graph

This is a governed **candidate** corpus for turning data/analytics-relevant research into
domain, compiler, library, qualification, and product knowledge. It is not a paper ranking,
an expert ranking, a claim that every paper is correct, or a closed enumeration of computer
science.

The deterministic v0.1.0 candidate contains:

- 126 primary research artifacts or technical standards across 12 fields;
- 88 foundational artifacts through 2020 and 38 non-LLM artifacts from 2021–2026;
- 126 distinct work, edition, venue-occurrence, artifact, source, and evidence-scope records;
- 525 candidate contributor identities and 575 ordered credit occurrences;
- 19 deeply extracted examples with 19 scoped claims, 83 artifact-scoped concept candidates,
  20 method candidates, 20 algorithm candidates, and compiler/library mappings; and
- 107 full-text review items. Metadata-only records are coverage candidates, not compiler truth.

The fields are database/query/transaction, distributed/streaming, compression/storage,
programming languages/compilers, information retrieval, visualization/HCI,
statistics/ML/predictive analytics, process mining, graph/spatial/scientific data,
optimization/control, security/privacy, and quality/governance/provenance.

## The non-collapsible graph

```text
abstract work
    |
    +-- edition/version -- venue occurrence -- exact artifact/file/URL
                                                   |
                                                   +-- ordered contributor credit
                                                   +-- definitions ---> concept candidates
                                                   +-- scoped claims ---> evidence + assumptions
                                                   +-- method ---> algorithm ---> implementation
                                                   |                  |
                                                   |                  +-- complexity/guarantee
                                                   |                  +-- kernel/target needs
                                                   +-- benchmark ---> protocol ---> result
                                                   |                  |
                                                   |                  +-- uncertainty/threats
                                                   +-- limitation/negative result
                                                   +-- contradiction/replication/supersession
                                                   +-- compiler/library mapping candidate
```

The separation matters. A paper is not a claim. A claim is not a universal law. A method is
not an algorithm. Pseudocode is not an implementation. A repository name is not a qualified
version. A benchmark score is not a production guarantee. An author is not automatically the
sole inventor. A citation is not authorship.

## Process-mining attribution example

The graph expressly prevents an easy but material mistake:

```text
Dirk Fahland
  authored 2022 Event Knowledge Graph chapter
  coauthored 2024 OCED-PG implementation paper
  coauthored 2024 OCED core/design-space preprint

Khayatbashi + Hartig + Jalali
  authored 2024 OCEL -> Temporal Event Knowledge Graph transformation

Kretzschmann + Berti + van der Aalst
  authored 2026 State-Aware OCPM / explicit state-transition paper
```

These works form a useful research lineage, but lineage is not shared authorship and similarity
is not identity. The machine-readable adjudication is in `case.fahland_attribution` and
`case.ocel_oced_tekg` in `conflict-replication.jsonl`.

Their compiler consequences are also different:

```text
OCEL 2.0
  -> exchange/profile/serialization contracts
  -> event/object/relation/qualifier/time-varying-attribute types

OCED core/design space
  -> minimal core + explicit extension/profile decisions

OCED-PG + semantic header
  -> domain mapping declaration -> generated ELT/graph construction
  -> source truth is supplied, not magically discovered

Temporal EKG
  -> OCEL temporal values -> entity snapshots/temporal relations
  -> transformation and information-loss receipt

State-aware OCPM
  -> domain-owned state function + valid-time policy
  -> explicit transition events + perspective-dependent state labels
```

## Predictive analytics conversion

“Predictive analytics” is not one library or one model. A compiler-facing declaration must
separate at least:

```text
business decision
  -> prediction task / target / population / unit
  -> observation cutoff / horizon / censoring / leakage rules
  -> available-at-decision-time features
  -> model family + estimator + training algorithm
  -> loss / utility / constraints
  -> split/backtest protocol + benchmark occurrence
  -> calibration + uncertainty + abstention
  -> robustness / fairness / shift / drift
  -> fitted-model artifact + exact implementation/target qualification
  -> prediction/result identity + human/automated action policy
  -> monitoring / retraining / rollback / evidence receipt
```

The seed graph includes Kalman prediction, survival regression, gradient boosting, random
forests, conformal prediction, XGBoost, LightGBM, double/debiased ML, hierarchical time-series
forecasting, patch-based time-series transformers (non-LLM), conformal time-series intervals,
and predictive object-centric process monitoring. This is a **seed**, not a complete predictive
method atlas; the gap record enumerates missing survival, competing-risk, count, intermittent,
hierarchical, spatial-temporal, graph, anomaly, maintenance, and decision-aware research.

## Research-to-library gate

```text
research artifact
     |
     v
scoped extraction -- assumptions missing? --> review/refuse
     |
     v
concept/method/algorithm adjudication
     |
     +-- competing definitions? --> preserve contexts; do not alias
     +-- unsupported claim? -----> evidence gap
     +-- benchmark mismatch? ----> target qualification plan
     |
     v
semantic type / operation / proof-obligation candidates
     |
     v
algorithm IR + representation/kernel requirements
     |
     v
library contribution candidate
     |
     +-- license/version/API/failure/resource/unsafe missing? --> refuse
     |
     v
qualified target binding + evidence receipt
```

The constitutional rules live in `conversion-rules.jsonl`. All current mappings have
`binding_status = research_candidate_not_bindable`.

## Files

- `works.jsonl`, `editions.jsonl`, `venue-occurrences.jsonl`, `artifacts.jsonl` — publication
  identity ladder;
- `people.jsonl`, `institutions.jsonl`, `contributions.jsonl` — name-safe identities and exact
  ordered credit occurrences;
- `sources.jsonl`, `evidence.jsonl`, `claims.jsonl` — source and scoped evidence;
- `concepts.jsonl`, `formalisms.jsonl`, `research-types.jsonl`, `methods.jsonl`,
  `models.jsonl`, `estimators.jsonl`, `algorithms.jsonl`, `guarantees.jsonl`,
  `implementations.jsonl`, `benchmarks.jsonl` — non-collapsed knowledge objects;
- `evaluations.jsonl`, `supplementary-artifacts.jsonl`, `limitations-threats.jsonl`,
  `replications.jsonl`, `contradictions-supersessions.jsonl` — protocols, results/effect-size and
  uncertainty posture, code/data, threats, reproduction, and change of scientific status;
- `relations.jsonl`, `relation-ontology.jsonl` — typed evidence graph;
- `compiler-library-mappings.jsonl`, `conversion-rules.jsonl` — conversion candidates/laws;
- `conflict-replication.jsonl` — attribution, incompatibility, and benchmark examples;
- `review-queue.jsonl`, `gaps.jsonl` — explicit incompleteness;
- `metamodel.json`, `manifest.json`, `schemas/` — machine contract and inventory;
- `EXTRACTION-ADJUDICATION.md` — repeatable research workflow; and
- `build_corpus.py`, `validate_corpus.py` — deterministic generation and validation.

## Build and validate

```bash
python3 research/domain_atlas/ecosystem/research_artifact_graph/build_corpus.py
python3 research/domain_atlas/ecosystem/research_artifact_graph/validate_corpus.py --rebuild
```

The validator enforces the 120-artifact/35-foundational/35-recent floors, 12-field coverage,
identity references, contributor order, evidence scope, deep-extraction mappings, constitutional
conversion laws, explicit gaps, and byte-for-byte deterministic regeneration.

## Open-world coverage law

No finite list can truthfully contain “all CS research.” Extension is governed by a coverage
tensor rather than a fake total count:

```text
field × research question × artifact kind × time × evidence depth
      × method/algorithm/representation/kernel × target × replication status
      × compiler phase × library boundary × product capability
```

A cell is `unsearched`, `candidate`, `extracted`, `adjudicated`, `replicated`, `superseded`, or
`saturated_for_declared_scope`. “Saturated” is always scoped and dated. New evidence enters the
review queue; it cannot silently rewrite a canonical concept or qualified binding.
