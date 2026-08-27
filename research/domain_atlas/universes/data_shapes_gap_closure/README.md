# Data-shape gap-closure candidate

Status: **candidate extension and adjudication bundle; not canonical and not a
completeness claim**.

This bundle closes the exact modality and representation gaps reported by
`data_modality_gap_audit/` without silently editing `data_shapes/`.  It is deliberately
open-world: passing the validator proves structural and stated-law coverage, not that the
world's data universe has been exhausted.

## The boundary that matters

```text
domain meaning
    │  e.g. "executed order", "clinical finding", "city object"
    ▼
semantic qualifiers
    │  authority, units/codes, purpose, uncertainty, validity
    ▼
logical / observation shape
    │  identity · grain · time · order · topology · change
    ▼
representation profile
    │  exact standard + edition + extension / market-practice profile
    ▼
carrier / encoding / container / physical layout
    │
    ▼
implementation occurrence on an exact runtime target

No arrow may be inferred from a filename, vendor name, parse success, or schema success.
Each arrow is a compiler binding with proof/refusal obligations.
```

“Unstructured” is only a weak statement about available schema or interpretation.  It is
not a data type.  Email, for example, is not one blob:

```text
SMTP envelope ──delivers──> Internet message
                              ├── ordered header multimap
                              └── MIME entity graph
                                   ├── text / HTML body
                                   ├── nested multipart
                                   ├── attachments
                                   └── embedded messages

mailbox occurrence ≠ Message-ID ≠ content digest ≠ SMTP transaction
header From ≠ envelope reverse-path ≠ authenticated actor
```

The same separation is applied to scientific, engineering, genomic, financial and catalog
data:

```text
HDF5 file  -> linked groups/datasets/datatypes/attributes (not one tensor)
FITS file  -> ordered heterogeneous HDUs              (not one image)
DICOM      -> patient-study-series-instance-frame graph (not pixel bytes)
glTF       -> runtime scene asset                       (not CAD/BIM truth)
AP242      -> product/configuration/geometry/PMI model   (not just geometry)
VCF        -> reference-qualified variant assertions     (not rows alone)
FIX        -> session + application lifecycle stream      (not global market order)
```

## Compiler meaning

```text
intent
  │
  ├─ resolve candidate logical shape + semantic qualifiers
  ├─ bind exact representation/profile edition
  ├─ type-check requested operation against operation-totality cells
  ├─ compute preservation, residual and accepted-loss obligations
  ├─ require exact implementation/provider qualification
  └─ emit plan OR a typed refusal

format support ─X─> semantic support
schema valid   ─X─> domain valid
round trip     ─X─> meaning preserved (unless the preservation set is proved)
signature OK   ─X─> payload true or actor authorized
```

The proposed compiler chain is:

```text
candidate shape contract
    -> representation binding IR
    -> conversion proof obligations
    -> library requirements/offers
    -> provider occurrence + target qualification
    -> executable plan / typed unresolved-semantic refusal
```

## Contents

- `sources.jsonl` — a self-contained snapshot of 182 primary/authoritative source
  records, including ten gap-closure additions.
- `context-candidates.jsonl` — sovereign boundaries for every missing family.
- `shape-type-candidates.jsonl` — separately typed logical shapes, qualifier sets,
  identity contracts and representation profiles.
- `canonical-adjudications.jsonl` — exact proposed relation to the canonical candidate;
  all remain open for manual law comparison.
- `representation-crosswalks.jsonl` — GeoParquet, FITS, OpenEXR, glTF, IFC, STEP AP242,
  CMS, COSE, VCF, FHIR, ISO 20022, FIX and adjacent bindings.
- `operation-totality.jsonl` and `invalid-inferences.jsonl` — legal domains, preconditions,
  loss/residual obligations and mandatory refusals.
- `compiler-requirements.jsonl` — intent fields, IR outputs and proof obligations.
- `library-boundaries.jsonl` — pure, composable domain-library boundaries with exposed
  decisions and explicit non-ownership.
- `provider-qualifications.jsonl` — unexecuted fixture suites; no provider is prequalified.
- `innovations-2021-2026.jsonl` — non-LLM change signals that trigger requalification,
  never taxonomy-by-release-name.
- `gaps.jsonl` — honest residual work that prevents closure claims.

## Deterministic use

```bash
python3 research/domain_atlas/universes/data_shapes_gap_closure/validate_candidate.py
```

The validator rebuilds all generated artifacts, checks source and owner references,
minimum independent coverage, required representation terms, non-canonical status,
non-LLM innovation scope, operation refusals and unexecuted provider qualification.

## Constitutional laws

1. Carrier, encoding, container, layout, representation profile, logical shape and semantic
   meaning are different types.
2. Equality is owned by a semantic/profile contract, never inferred from bytes or names.
3. Identity, time, order, topology, change, uncertainty and security qualifiers are
   independently typed; one does not imply another.
4. A conversion either proves its preservation set, emits typed residual/loss, or refuses.
5. A provider/library name is not a qualification.  Only an exact implementation version
   passing an exact profile suite on an exact target is an offer the compiler may bind.
6. Syntax/schema/signature success never proves business, clinical, scientific or legal
   truth.
7. New releases are change signals that invalidate assumptions; they do not automatically
   create new semantic types.
8. No record in this bundle may become canonical by name matching or generator output.

## Remaining high-risk gaps

The executable round-trip/adversarial fixtures, timezone recurrence oracles, scientific
discipline conventions, DICOM private-tag/de-identification corpus, cross-kernel B-rep
tolerance tests, genomic reference registry, venue-specific order-book replay corpora and
market-practice profiles are still open.  See `gaps.jsonl`; these are not editorial TODOs,
they are blockers to a compiler truth claim.
