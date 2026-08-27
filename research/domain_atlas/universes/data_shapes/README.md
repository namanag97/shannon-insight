# Provider-neutral data type and shape universe

This directory models **what data is**, independently of where it came from, how a vendor stores
it, or which analytical product consumes it. It is an open-world research registry, not a claim
that a finite list has enumerated every future industry field or encoding.

## The separations the compiler must preserve

```text
source system        container/encoding/layout         carrier
mail server          MIME + RFC 5322 bytes             UTF-8 / binary
office suite         ZIP + OOXML parts                 strings / numbers
object store    ->    Parquet row groups          ->    arrays / decimals
GIS service          GeoJSON / coverage / tiles        coordinates / arrays
      |                         |                           |
      |                         +---------------------------+
      |                                      |
      |                                logical shape
      |                 message, workbook, table, tensor, graph,
      |                 event log, time series, raster, trajectory
      |                                      |
      |                            semantic value/observation
      |                 identifier, money, quantity, measurement,
      |                 subject + property + result + time + method
      |                                      |
      +---- connector/integration only       |
                                             v
                                    vertical refinement
                              counterparty exposure, well rate
```

`Source system`, `shape`, `carrier`, `modality`, `encoding`, `container` and `meaning` are distinct
classifications. The compiler must never infer meaning from a carrier, filename, media type or
source name. `decimal(18,2)` does not prove money; a table does not prove its grain; null does not
identify an absence reason; and an ordered file does not prove event-time order.

The familiar words *structured*, *semi-structured* and *unstructured* are only one axis:

```text
structure degree              logical shape              representation
schema-bound structured  x    table / record        x    Arrow / Parquet / SQL
self-describing semi-    x    nested tree / map     x    JSON / CBOR / YAML
grammar-bound semi-      x    message / document    x    MIME / HTML / PDF / Office
perceptual media         x    image / audio / video x    DICOM / WAV / media container
opaque bytes             x    unresolved            x    binary/blob
```

These are not a flat taxonomy. A PDF can contain structured logical tags, weakly structured page
marks, images, forms, scripts and embedded files at once. An email is a message plus a MIME tree,
mail-store metadata and a profile-derived thread—not merely “unstructured text.” Geographic data
may be vector geometry, feature collections, rasters, coverages, tiles, trajectories, point clouds
or meshes; coordinates still require a CRS and axis order.

## Record sets

- `classification-axes.json` defines independent axes. They are not multiplied to manufacture
  fictitious types.
- `type-records.jsonl` defines carrier and semantic-value candidates. Semantic records expose
  equality, order, arithmetic, missingness, uncertainty, time, provenance, canonicalization and
  compatibility laws.
- `shape-records.jsonl` defines structural candidates and their elements, keys, topology,
  order/time/change semantics, constraints, valid operations and evidence.
- `operation-totality-matrix.jsonl` says when commonly named operations are total, partial,
  lossy, stateful or invalid for a type/shape family.
- `representation-crosswalks.jsonl` separates an encoding/container from the provider-neutral
  carrier or logical shape it can preserve, including prerequisites, loss and round-trip tests.
- `invalid-inference-matrix.jsonl` makes common representation-to-meaning errors executable
  compiler refusals and lists the extra evidence needed before the conclusion is legal.
- `bounded-context-candidates.jsonl` proposes semantic ownership boundaries for later global
  context-map adjudication.
- `sources.jsonl` is an evidence index of primary standards and specifications.
- `coverage-gaps.json` records known non-saturation instead of hiding it.
- `coverage-report.json` reports exact counts by shape family and modality. Counts are inventory,
  not completeness claims.
- `schemas/` contains the JSON Schemas for every governed record kind.
- `build_registry.py` regenerates the deterministic registries; `validate_data_shapes.py` enforces
  schemas, references, ownership, evidence, crosswalk, invalid-inference and honest-gap gates.

The current candidate contains 45 independent axes (529 axis values), 31 carrier types, 77
semantic value types, 177 explicit shapes in 31 families, 167 operation-totality records, 62
representation crosswalks, 77 forbidden inferences, 39 bounded-context candidates and 90 primary
standards/specifications from 55 publishers. See `coverage-report.json` for exact family/modality
counts and `coverage-gaps.json` for the 18 known residual areas.

Explicitly seeded families include tabular/nested records; messages, email, MIME, mailboxes and
threads; text, PDF, office, HTML and EPUB documents; arrays/tensors/scientific data; vector/raster
geospatial data, coverages, tiles, trajectories, point clouds, meshes and CRS-bound geometry;
graphs/hypergraphs; time series, streams, changelogs, event/process logs and telemetry; images,
signals, audio and video; uncertainty/distributions/scenarios; optimization/simulation artifacts;
code, configuration, binaries, archives, packages, container images and provenance/evidence.

## Candidate identity

```text
type identity  = owner + semantic laws + parameterization
shape identity = element contract + keys + topology + order/time/change laws
encoding       = a representation binding, never the identity of the meaning or shape
```

Two names are aliases only if their laws agree. Two carriers may represent one semantic type. A
single carrier may represent many incompatible semantic types. A shape specialization is accepted
only when it adds a material invariant, operation contract, or information-preservation boundary.

## Compiler failure posture

Unknown semantic meaning, missing unit, undeclared grain, absent key, unknown coordinate reference
system, unsupported change semantics, or an operation outside its declared domain produces a typed
gap. The compiler must not guess or silently coerce it.

## Scope

The core includes classical mathematical, statistical, optimization and simulation structures.
LLM, prompt, RAG, generative and agent-memory semantics are excluded. Model-artifact records are
provider-neutral and do not imply generative or LLM functionality.

## Validation

Regenerate and run strict schema validation:

```bash
python3 research/domain_atlas/universes/data_shapes/build_registry.py
uv run --with jsonschema python research/domain_atlas/universes/data_shapes/validate_data_shapes.py
```

All records remain `candidate` until evidence review, split/merge adjudication, operation-law
review, two unrelated vertical mappings and independent implementation tests are complete.
