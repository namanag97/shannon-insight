# Adversarial data modality and shape gap audit

This directory is an independent coverage audit of `../data_shapes/`. It is **not** a competing
canonical registry. The 193 `fam.*` records are expectations used to challenge coverage, split
layers, and locate gaps. They must not be imported as canonical types by counting or by name.

The frozen audit currently resolves against 177 canonical shapes, 108 canonical carrier/semantic
types, 167 operation records, 62 representation crosswalks, 77 invalid-inference records, and 90
canonical evidence sources. `canonical-snapshot.json` pins the exact content hashes; the validator
refuses a stale crosswalk.

## The taxonomy that must survive compilation

```text
semantic meaning                         money, diagnosis, feature identity, variant assertion
        |
        | is asserted by; never inferred from the layers below
        v
observation / record / collection shape  result, row, message, series, graph, tensor, document
        |
        +--> modality                     text, table, geo, signal, image, audio, video, genomic
        +--> logical topology             sequence, tree, graph, grid, mesh, coverage, scene
        |
        v
carrier                                  integer, decimal, UTF-8 text, bytes, struct, list, map
        v
encoding                                 JSON, XML, YAML, CBOR, Protobuf wire, image/video codec
        v
container / file format                  PDF, OOXML, ODF, ZIP, WARC, BMFF, HDF5, FITS, DICOM
        v
physical layout                          row/column, buffers, pages, chunks, tiles, CSR/CSC/COO
        v
compression / protection                 gzip/zstd, lossy coding, encryption, signatures, digests
```

Every arrow is a binding with preconditions and loss/refusal cases, not an equivalence. In
particular, "unstructured" is only a weak or deferred schema/interpretation posture. Email, PDF,
images, source code, and byte streams all have structure even when an enterprise has not declared
or recovered it.

## Machine-readable artifacts

- `classification-axes.json` defines 26 independent axes and the nine protected abstraction layers.
- `schema-posture-audit.jsonl` normalizes structured, semi-structured, and so-called unstructured
  labels as interpretation postures, never modalities or claims that structure is absent.
- `modality-family-expectations.jsonl` contains 193 non-canonical family expectations across core,
  table, email, document, web/message, graph, event/telemetry, time/signal/media, geo, array,
  scientific, CAD/BIM, genomics/health, finance, packaging, code/config, and metadata/evidence.
- `coverage-tensor.jsonl` contains 5,018 explicit family-axis cells. It is not a Cartesian product;
  each cell is one reviewed expectation plus a canonical coverage state.
- `canonical-crosswalk.jsonl` records exactly one declared comparison for every family using only
  `equivalent`, `narrower`, `broader`, `overlap`, `disjoint`, or `missing`. Equivalence by name is
  forbidden; every comparison cites layer, grain, topology, time/change, and operation surfaces.
- `operation-type-gaps.jsonl` tests valid, partial/lossy, and invalid operations for every family.
  Missing operations and absent precondition profiles stay visible.
- `audit-assertions.jsonl` contains 223 explicit, evidence-linked refusal/coverage assertions.
- `gap-findings.jsonl` records missing, split, merge, and overlap findings. A `merge` finding can say
  a format-specific candidate should merge into an existing logical shape while remaining a
  separate representation binding; it does not assert careless aliasing.
- `representation-layer-findings.jsonl` calls out 30 recurring confusions such as PDF-as-meaning,
  CSV-as-table, Parquet-as-relation, JSON-as-semi-structured, and encryption-as-trust.
- `canonical-representation-audit.jsonl` maps every layer-confusion finding to exact canonical
  `xwalk.*` records where present and reports the remaining representation gaps.
- `standards-sources.jsonl` indexes 172 primary/official evidence records across 162 unique URLs. It
  mirrors the canonical evidence with `A-DSS-*` IDs and adds audit sources for uncovered strata;
  duplicate URLs remain visible when the audit and canonical corpus assigned independent IDs.
- `innovations-2021-2026.jsonl` records 33 recent, non-generative standards changes that pressure
  the taxonomy without treating novelty as a new semantic type.
- `vertical-case-samples.jsonl` exercises 20 cases across unrelated industries.
- `saturation-report.json` records search strata, the novelty curve, the closure rule, and why this
  sweep cannot honestly estimate unseen mass.
- `audit-summary.json`, `canonical-snapshot.json`, and `manifest.json` provide counts and hashes.
- `schemas/` contains Draft 2020-12 schemas for the principal record sets.

## Deterministic build and validation

```bash
python3 research/domain_atlas/universes/data_modality_gap_audit/build_audit.py
python3 research/domain_atlas/universes/data_modality_gap_audit/validate_audit.py --check-determinism
```

The builder uses only explicit declarations in `build_audit.py`; it never fuzzy-matches canonical
names. The validator checks schemas when `jsonschema` is installed, and always checks identities,
references, counts, axis values, all six relations, layer laws, source use, canonical target IDs,
snapshot hashes, manifest hashes, operation coverage, forbidden inference posture, and optional
byte-for-byte regeneration.

## What the audit found

The stabilized canonical corpus now covers email/MIME, paginated/PDF, office workbooks and
presentations, HTML/EPUB, configuration/source/AST/binary artifacts, archives/packages, and spatial
tiles that were absent in an earlier snapshot. The refreshed crosswalk therefore records those
exact canonical IDs rather than reporting stale gaps.

The remaining high-value gaps are concentrated in compound scientific dataset models (HDF5 group
graphs, netCDF datasets, FITS heterogeneous HDUs), exact engineering models (B-rep, scene, CAD
product, BIM facility), reference-aware genomics (sequences, alignments, variants, haplotypes),
symbolic/timed media (musical events and captions), deep images, finance state (order books and
balanced journals), and transport-envelope/calendar semantics. Format-layer records such as PDF,
OOXML, Parquet, GeoParquet, ZIP, codecs, and protected envelopes also require adjudication where a
logical specialization and a representation binding overlap.

## Honest limits

This is one purposive standards sweep, not proof of universe saturation. Source count, family count,
and 5,018 cells demonstrate breadth only. No independent reviewer has completed a disjoint search,
no two consecutive cycles have produced zero new constructors, many proprietary/legacy instrument
formats remain unsampled, and the vertical samples are not universal implementation fixtures.
Canonical records remain candidates too. A schema-valid audit proves internal consistency, not the
truth, completeness, or implementability of every assertion.
