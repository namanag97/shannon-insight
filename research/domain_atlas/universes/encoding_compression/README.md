# Representation, encoding, layout and compression universe

This corpus models the physical-representation domain that sits between semantic data and executable
storage/transport/compute plans. It includes compression, but compression is only one bounded part of
the domain.

The current edition is an evidence-backed **open-world candidate atlas**. It is not a claim that every
future file format, codec, provider or accelerator is enumerated. Its completeness claim is instead:

1. an encountered artifact maps to distinct governed layers or produces a typed gap;
2. every compiler-relevant decision is explicit and owned;
3. implementations bind through versioned capability offers and scoped evidence;
4. unknown meaning, profile, loss, dependency or resource behavior fails closed; and
5. new formats/providers extend registries without adding vendor-name branches to the compiler.

This edition contains 73 primary/official sources, 22 classification axes, 34 bounded-context
candidates, 122 representation/format/layout/codec records, 39 typed operations, 36 decision points,
20 compiler mappings, 27 library candidates, 13 kernel contracts, 20 non-LLM innovation records from
2021–2026 and 20 explicit gaps.

## The distinction the compiler must preserve

```text
semantic value/type
        |
        | represented by
        v
carrier (buffer, stream, seekable source, device memory)
        |
        +-- scalar/character encoding (endianness, UTF, varint, bit width)
        |
        +-- schema serialization (JSON, CBOR, Avro, Protobuf, ...)
        |
        +-- framing (length, TLV, sync marker, independently decoded block)
        |
        +-- physical layout (row, column, page, row group, stripe, tile, chunk)
        |
        +-- value/column encoding (null levels, dictionary, RLE, delta, FOR, bit-pack)
        |
        +-- compression algorithm (DEFLATE, Zstandard, LZ4, SZ3, zfp, ...)
        |
        +-- codec (image/audio/video/scientific sample model -> codestream)
        |
        +-- container/file format (members, metadata, offsets, footer, indexes)
        |
        +-- integrity/content identity/protection (checksum, digest, AEAD, signature)
        |
        v
implementation offer (library + version + configuration)
        |
        v
kernel offer (ports + memory spaces + alignment + target + resource bounds)
        |
        v
execution target (scalar/SIMD/multicore CPU, GPU, accelerator, object store, embedded)
```

These are not aliases:

- `UTF-8` is a character encoding, not a semantic text type or file format.
- `Zstandard` is a compression format/algorithm family, not a row-group layout.
- `Parquet` is a container and columnar physical-format specification; it does not own a business
  table's semantics or table-transaction lifecycle.
- `PNG` binds an image model, filters, compression and a chunked format; the compiler still preserves
  the bundled subcontracts.
- a GPU library is an implementation/provider offer; it does not own the Zstandard or LZ4 semantics.
- a checksum detects accidental corruption within a stated scope; it is not a signature.
- a digest identifies exact bytes within a stated scope; it is not business identity.
- encryption provides no authorization or semantic validity by itself.

## Why this is part of a data and analytics platform

Representation decisions change whether an analytical plan is executable and correct:

```text
analytical requirement
  population + grain + time + fidelity + access + latency + cost + target
                                  |
                                  v
                    RepresentationRequirements
                                  |
        +-------------------------+-------------------------+
        |                         |                         |
        v                         v                         v
 logical value/layout      fidelity and loss        access and assurance
 null/nesting/schema       equality/error/bound     split/random/prune/integrity
        |                         |                         |
        +-------------------------+-------------------------+
                                  v
                enumerate capability-compatible offers
                                  |
                                  v
                    qualify on exact edition/target
                                  |
                                  v
                   choose by declared objective law
                                  |
                                  v
 PhysicalRepresentationPlan + inverse plan + rejected offers + proof obligations
                                  |
                                  v
            kernels/jobs execute -> receipts -> decoded-result verification
```

Examples of incorrect collapses that this model rejects:

- choosing gzip for distributed split processing merely because it compresses;
- choosing a dictionary codec without distributing the exact dictionary artifact;
- signing non-canonical JSON while expecting stable semantic identity;
- treating Protocol Buffers deterministic serialization as universally canonical;
- encrypting Parquet metadata without deciding whether pruning metadata may leak;
- using a GPU decompressor because the library name is familiar, without proving that its exact
  profile, memory space, limits and cancellation contract match;
- applying a floating-point quantizer without units, error scope or downstream-observable tests; or
- interpreting a `.csv`, `.parquet` or magic number as proof of semantic type.

## The main bounded-context candidates

```text
Meaning boundary
  carrier | byte order | character | scalar | schema wire | null/nesting

Structure boundary
  framing | chunking | physical layout | container | edition compatibility

Reduction boundary
  column encoding | dictionary lifecycle | compression algorithm | codec
  loss contract | compression selection | transform pipeline

Access boundary
  splittability | random access | pruning metadata | streaming

Trust boundary
  canonicalization | content identity | integrity | protection envelope
  detection | corruption recovery | transcode

Execution boundary
  target capability | kernel contract | resource model | provider qualification
```

The records remain candidates until the global context map adjudicates overlaps with semantic data
types, storage, query planning, streaming, security/key management, runtime scheduling, artifacts and
migration. An algorithm name is not automatically a bounded context.

## Layout is an access contract

```text
logical records
  |
  +-- row layout ----------> point update / whole-record locality
  |
  +-- column layout -------> projection / SIMD / analytical scan
  |       |
  |       +-- page
  |       +-- column chunk
  |       +-- row group (Parquet-style coordination grain)
  |       +-- stripe (ORC-style streams and indexes)
  |
  +-- N-D chunks ----------> coordinate hyperslabs / scientific arrays
  |       +-- optional indexed shard to reduce small objects
  |
  +-- raster tiles --------> spatial windows
          +-- overviews ---> progressive/multiresolution reads
```

Page, row-group, stripe, tile and chunk sizes are decisions with coupled effects on write buffering,
compression ratio, parallelism, metadata size, request count, read amplification, memory, recovery and
latency. No globally correct constant is hidden in a library.

## Column encodings are not general-purpose compressors

The corpus keeps these physical transforms distinct and composable:

```text
typed values
  -> null/nesting representation
  -> optional dictionary / RLE / run-end
  -> optional delta / prefix / frame-of-reference
  -> optional bit packing / byte-stream split / exception patch
  -> optional general entropy/LZ compression
  -> frame/container placement
```

An encoding planner may select per column, block or page using type, cardinality, sortedness, run
length, range, distribution, access pattern and target. The selected plan and corpus evidence are a
receipt. A vendor-specific automatic mode is represented as a provider capability with observed
behavior, never as the semantic selection law.

## Loss is a first-class contract

```text
LossProfile
  = source semantic type and equality
  + lossy scope and transform profile
  + metric (absolute / relative / pointwise / digits / rate / perceptual / task)
  + finite bound or finite quality profile
  + units, population and protected observables
  + original-retention rule
  + approving authority
  + decoded-output verification oracle
  + breach/refusal/remediation semantics
```

```text
lossless mode
  encode -> decode -> equality oracle == true

lossy mode
  original + decoded + LossProfile
       -> numeric/signal metrics
       -> downstream protected-observable tests
       -> human/task acceptance when required
       -> Pass | Refuse(error evidence)
```

Every `error_bounded_lossy`, `perceptual_lossy` or mixed lossless/lossy record has a non-empty error
contract, finite declared profile, approval requirement and verification method. Unknown or unbounded
loss is not a default. Scientific compressors such as SZ3/zfp and image/audio/video codecs therefore
fit the same metamodel without pretending they share one error metric.

## Splittability and random access are independent traits

```text
streamable       can consume incrementally with bounded state
restartable      has a point from which decode can restart
splittable       independent ranges can decode in parallel with dependencies available
random-access    a named logical range can be located and decoded with a stated bound
range-readable   the carrier can fetch byte ranges
progressive      a useful lower-fidelity/partial result appears before complete transfer
```

A range-readable object does not make its compression stream random-access. An LZ window, preceding
dictionary, nested-level stream, shared media reference frame or encrypted metadata can invalidate an
otherwise plausible split. Every access claim therefore names the independent decode unit,
prerequisite metadata/dictionary/reference and worst-case bytes/work.

## Conservative pruning

Statistics and indexes used for skipping are modeled through a three-valued contract:

```text
may_prune(predicate, summary) -> DefinitelyNo | Maybe

DefinitelyNo => skipping cannot remove a matching value
Maybe        => read and evaluate the actual values
```

Min/max ordering, NaN/null rules, truncation, collation, Bloom-filter false-positive rate, dictionary
scope and page offsets belong in the summary profile. Pruning must not introduce false negatives.

## Integrity, identity and cryptographic protection

```text
semantic value
   -> canonical bytes? ---- digest A (semantic-canonical scope)
   -> encoded bytes ------- digest B (wire scope)
   -> compressed bytes ---- checksum/digest C (stored-member scope)
   -> encrypted bytes ----- digest D (ciphertext/content-address scope)
   -> transport coding ---- Content-Digest / Repr-Digest as protocol defines
```

All scopes may legitimately differ. A transform invalidates downstream identities and may or may not
preserve upstream semantic identity. Signing requires an exact canonical byte scope. AEAD associated
data, nonce, tag, key handle and algorithm profile are explicit. Key generation, custody, rotation and
authorization remain outside this universe in their owning security contexts.

## Compute kernels

The compiler does not lower `compress(zstd)` directly to a crate call. It binds a logical operation to
a qualified kernel contract:

```text
KernelOffer
  algorithm/profile editions
  + input/output representation
  + host/device memory spaces
  + alignment, aliasing and overlap
  + supported sizes/dictionaries/windows
  + scalar/SIMD/thread/device/offload target
  + sync/async/cancellation/thread-safety
  + worst-case output/work/memory
  + fallback and failure algebra
  + conformance and benchmark evidence
  + implementation/version/target identity
```

The 13 seed kernel contracts cover portable scalar codecs, SIMD bit packing/column decoding,
multicore chunk compression, bounded streaming, GPU batch/device decompression, dedicated offload,
media decoding, checksum/digest, AEAD and decoded-loss verification. Kernels are mechanisms; their
reference algorithm and semantic contexts remain the owners.

## Proposed pure-library decomposition

```text
Semantic/policy libraries (own language and laws)
  san-carrier             san-wire-schema          san-content-identity
  san-layout              san-dictionary           san-compression-contract
  san-loss-contract       san-protection-envelope  san-transcode-plan
  san-representation-planner

Pure algorithm libraries (no I/O)
  san-byte-order          san-text-encoding        san-scalar-encoding
  san-framing             san-canonical            san-chunking
  san-nested-layout       san-column-encoding      san-integrity
  san-pruning-metadata

Effectful mechanisms (do not own meaning)
  san-codec-runtime       san-stream-codec         san-random-access-reader
  san-corruption-recovery san-format-probe

Replaceable boundaries
  san-codec-provider      san-codec-kernel
```

These are candidate library boundaries, not final Rust crates. Final splitting must wait for global
semantic ownership, dependency-cycle and change-coupling adjudication. Each candidate exposes public
types, operations, decisions, errors, laws, oracles, resource contracts, cancellation, FFI policy and
removal seams in `library-candidates.jsonl`.

## Provider qualification

`library-provider-qualification.json` requires offers to state exact implementation/profile versions,
loss modes, access traits, dictionaries, memory spaces, limits, concurrency, cancellation, target,
licenses, advisories and expiring evidence. Qualification includes:

- normative vectors and independent round trips;
- property, differential, cross-version and cross-implementation tests;
- lossy boundary/error checks;
- malformed, truncated, nested, oversized and decompression-bomb cases;
- stream fragmentation, flush, concatenation, restart and cancellation;
- dictionary/reference missing and mismatch behavior;
- integrity, tamper and protection-scope cases;
- FFI lifetime, aliasing, alignment, thread and memory-space safety;
- exact-target work, memory, latency, throughput and amplification evidence; and
- licensing, provenance and current security-advisory review.

The binding algorithm filters by semantics, fidelity, access, compatibility, security, resource and
target before optimizing any declared objective. It never switches on provider, vendor, crate or
product name.

## Five-year non-LLM innovation themes

The 2021–2026 evidence supports several real, separable developments:

- ALP, Chimp and Elf improved lossless floating-point encoding approaches;
- BtrBlocks explored adaptive cascading encodings for lake-oriented column blocks;
- Zarr v3 formalized composable codec/storage-transformer layers and indexed sharding;
- OGC standardized Cloud Optimized GeoTIFF, while GeoParquet and PMTiles matured cloud-geospatial
  access formats;
- JPEG XL, PNG Third Edition, the FLAC RFC and AV2 advanced media/interchange profiles;
- GDeflate, Intel IAA and nvCOMP made target-specific parallel/offload decompression a compiler-visible
  concern;
- Lance, Nimble, Vortex and F3 explored alternatives to fixed Parquet/ORC layout and encoding coupling;
- RFC 9530 clarified that transmitted content and selected representation have different digest scopes.

The corpus distinguishes invention, standardization of an older method, implementation
productization, project roadmap and performance claim. None becomes a universal best choice.

## Artifacts

- `manifest.json` — edition, laws, exclusion boundary and authoritative counts.
- `axes.json` — 22 independent classification axes.
- `bounded-context-candidates.jsonl` — 34 ownership hypotheses.
- `format-layout-codec-records.jsonl` — 122 layered carrier/encoding/layout/format/codec records.
- `typed-operations.jsonl` — typed operations with totality, loss, refusal, failure and resource laws.
- `decision-points.jsonl` — every current compiler-visible choice; defaults are forbidden.
- `compiler-mappings.jsonl` — 20 intent patterns lowered by capabilities rather than provider names.
- `library-candidates.jsonl` — 27 proposed pure/runtime/adapter/backend library boundaries.
- `kernel-contracts.jsonl` — 13 target-neutral kernel requirement contracts.
- `library-provider-qualification.json` — offer surface, gates, selection law and result states.
- `sources.jsonl` — 73 primary standards, official implementations and primary research sources.
- `innovations.jsonl` — 20 non-LLM 2021–2026 innovation candidates with limitations.
- `gaps.jsonl` — 20 open gaps and the compiler's fail-closed behavior.
- `build_corpus.py` — deterministic authoring/generation source.
- `validate_corpus.py` — structural, referential, loss, exclusion and coverage gates.

Regenerate and validate:

```bash
python3 research/domain_atlas/universes/encoding_compression/build_corpus.py
python3 research/domain_atlas/universes/encoding_compression/validate_corpus.py
```

## Honest remaining gaps

The largest blockers are not more names. They are proof and integration:

- globally adjudicate context ownership against data types, storage, query, runtime and security;
- bind every representation to semantic equality and invalid-inference laws;
- populate concrete provider/version/target offers with expiring evidence;
- assemble normative, malformed and decompression-bomb fixture registries;
- prove two independent implementations and two unrelated vertical bindings per capability;
- deepen specialized seismic, microscopy, astronomy, CAD, point-cloud, genomics and industrial codecs;
- model patented media profiles and licensing posture at exact editions;
- integrate dictionary/reference retention, key management and crypto agility;
- measure side channels, energy and worst-case amplification; and
- derive Rust traits/typestates/crates only after ownership and dependency-cycle adjudication.

Until those are closed, any compiler branch that depends on them emits a typed gap. Product and suite
boundaries remain deliberately deferred.
