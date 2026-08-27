# Loss-aware canonical-reference mapper

This directory contains the first deterministic mapping and triage pass over every record in
`industries/canonical-reference-review-queue.jsonl`. It is a review aid, not an adjudication
engine. It does not edit a vertical pack, rewrite a raw reference, promote a candidate, or declare
semantic equivalence from a label.

## Boundary and process

```text
read-only inputs
  |
  +-- 4,169 unresolved queue identities -----------------------------+
  +-- 20,176 exact vertical source occurrences                        |
  +-- source questions / decisions / grains / evidence                |
  +-- ISIC Rev.5 foundation and official seed crosswalks              |
  +-- analytical practices + method kernels + OR methods              |
  +-- typed operations + source-system classes + data shapes/types    |
  +-- all identifier fields and references under universes/           |
                                                                      v
                         deterministic extraction
                         +-----------------------+
                         | source occurrences    |  exact raw text + digest
                         | source definitions    |  contextual meaning, not a verdict
                         | canonical index       |  definitions, laws, evidence, digests
                         | universe ID census    |  identity/reference visibility
                         +-----------+-----------+
                                     |
                    +----------------+----------------+
                    |                                 |
                    v                                 v
          mechanical namespace                semantic authoring review
          alignment / retrieval               checked-in manual seeds only
          (no semantic effect)                definition + law + evidence
                    |                                 |
                    +---------------+-----------------+
                                    v
                         proposal + loss envelope
                     equivalent | narrower | broader
                       overlap | disjoint | missing
                                    |
                                    v
                       independent reviewer batches
                                    |
                                    v
                      adjudication outside this pass
```

The relation direction is always **raw vertical source concept -> canonical target**. A `narrower`
proposal means the vertical use is narrower than the target family. One-to-many records preserve a
compound reference as an explicit decomposition; they are never flattened to one convenient label.

## Mechanical and semantic separation

`namespace-alignments.jsonl` contains NFKC/case/separator normalization matches. Each record says
`semantic_effect: none` and `proves_equivalence: false`. `triage-records.jsonl` may also contain up
to five token-overlap retrieval candidates, each marked `semantic_evidence: false`.

`candidate-mappings.jsonl` is produced only from `manual-proposal-seeds.json`. The seeds were
reviewed against extracted source contexts and canonical definitions/contracts/evidence. Generated
proposals remain `proposed`, require independent review, retain loss and uncertainty, and set
`adjudicated: false`. The generator never turns an alignment or score into a semantic proposal.

## Artifacts

- `source-occurrences.jsonl` — every exact occurrence that contributed to the current queue.
- `source-definitions.jsonl` — one contextual, non-adjudicated definition record per queue item.
- `canonical-candidate-index.jsonl` — 3,806 candidate targets from the required canonical corpora.
- `universe-id-census.jsonl` — every ID-shaped declaration/reference read from all universe JSON.
- `alias-assertions.jsonl` — only aliases declared by source records and inherited official
  crosswalk assertions; a crosswalk is explicitly not mislabeled as an alias.
- `namespace-alignments.jsonl` — mechanical matching only.
- `candidate-mappings.jsonl` — evidence/law-reviewed proposals with relation, loss and uncertainty.
- `missing-concept-proposals.jsonl` — open vertical-extension and universe-gap proposals.
- `collisions-homonyms.jsonl` — raw normalization collisions, canonical homonyms and ambiguous
  alignments.
- `triage-records.jsonl` — the exactly-once 4,169-record ledger; every relation remains unresolved.
- `review-batches.jsonl` — an exactly-once primary-pack partition for independent review.
- `negative-tests.jsonl` — false twins the validator must continue to refuse.
- `coverage-report.json` and `coverage-report.jsonl` — exact counts by domain, pack, relation,
  confidence and review focus.
- `schemas/` — JSON Schema contracts for every generated record family.
- `manifest.json` — input digest plus artifact byte/digest/count receipts.

The 398 local industry identities all receive open extension/missing-concept proposals even when a
broader ISIC candidate is also proposed. This is intentional: a broad horizontal mapping must not
erase a case-specific vertical boundary. The corpus also preserves source-system surface
decompositions, method/practice layer distinctions and explicit gaps such as a CCR limit engine.

## Rebuild and validate

The generator and the mandatory validator require only the Python standard library:

```bash
python3 research/domain_atlas/compiler/canonical_reference_mapper/build_mapper.py
python3 research/domain_atlas/compiler/canonical_reference_mapper/build_mapper.py --check
python3 research/domain_atlas/compiler/canonical_reference_mapper/validate_mapper.py
```

Optional full JSON Schema validation uses an already available `jsonschema` installation:

```bash
python3 research/domain_atlas/compiler/canonical_reference_mapper/validate_mapper.py --schemas
```

A normal rebuild is deterministic. `--check` compares bytes without writing. The validator fails on
missing/duplicate queue coverage, source drift, target drift, silent rewrites, undeclared aliases,
semantic force attached to string matching, missing evidence, false twins, incomplete review-focus
coverage, fewer than 100 manual proposals, or any `adjudicated` output status.

## Current edition posture

The exact current counts live in `coverage-report.json`; they are derived, not hand-maintained. The
edition deliberately reports `completion_claim: false`. Open triage records and missing concepts are
first-class output, not omitted failures.
