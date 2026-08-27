# Persistence, storage, lakehouse and serving universe

This corpus decomposes persistent data infrastructure before any product or provider is
selected. It is the persistence/lakehouse contribution to the horizontal domain atlas, not a
claim that a finite list is the whole world.

Current research position:

| Surface | Records |
|---|---:|
| Primary standards/specifications/official implementation sources | 137 |
| Candidate bounded contexts | 124 |
| Typed capabilities | 389 |
| Explicit decisions with no hidden default | 113 |
| Library/format/protocol/implementation/deployment/product/suite candidates | 69 |
| Shared compiler-library projections (actual libraries only) | 38 |
| Compiler requirements | 91 |
| Abstract, deliberately unqualified offers | 86 |
| Profile binding rules | 12 |
| Non-LLM innovations, 2021–2026 | 34 |
| Object-log and object-native durable-state architecture candidates | 21 |
| Object-log compiler decision axes with no default | 14 |
| Object-log requirements, unqualified offers and binding rules | 41 |
| Explicit context-map relations | 21 |
| Detected vocabulary ownership/homonym overlaps | 70 |

All bounded contexts remain `candidate_not_adjudicated`. The counts show coverage and expose
review work; they do not prove completeness or final DDD boundaries.

## What “storage” actually decomposes into

```text
business/application meaning                         (owned elsewhere)
             |
             v
logical persistent model
 relational | document | KV | wide-column | graph/RDF | time-series
 search | vector | cache | event journal | array | warehouse | OLAP segment
             |
             v
analytical table state
 identity | schema/partition evolution | snapshots | mutations | deletes
 isolation/conflicts | change feed | manifests | statistics | format migration
             |
             v
catalog and commit authority
 namespace | asset registry | location | compare-and-swap commit | credentials
 managed/external lifecycle | cache coherence | versioned catalog | migration
             |
             v
portable representation kernels
 logical types -> value encoding -> file layout -> compression -> encryption
                -> checksums/statistics/indexes -> byte/object representation
             |
             v
physical persistence
 block | local/network/distributed file | object | archive | persistent memory
 replication | erasure coding | placement/tiering | retention | backup/restore
 recovery objectives = declared RPO/RTO | ordered source/recovered cuts
                       | named recovery interval | acceptance evidence | residuals

orthogonal operated planes:
  maintenance = compaction | clustering | delete materialization | expiry | GC
                statistics/index build | tier transition | repair | vacuum
  serving     = materializations | indexes | OLAP/search/vector/graph/time-series
                caches | freshness | cutover | bulk result delivery
  exchange    = publication | subscription | delegated delivery | federation
                pushdown | cross-source cuts | portability
```

Search mutation and search visibility are separate deterministic contracts:

```text
source occurrence -> projected index document -> immutable mutation intent
       -> admitted attempt -> epoch-scoped order token -> scoped acknowledgement
       -> journal/durable-commit facts (independent)
       -> per-shard reader/searcher visibility cut -> query result cut

acknowledged != durably committed != refreshed != searchable everywhere
```

The mutation contract owns conflict guards, idempotency, ordered partial batches, delete
tombstones, acknowledgement scope and unknown-outcome reconciliation. The visibility contract owns
reader/searcher publication, per-shard frontiers, partiality, read-after-write waiting and verified
delete disappearance. Refresh may create visibility without a stable commit; a commit may be durable
without the current searcher observing it.

The decomposition prevents several common category errors:

- compression is a reversible byte codec; **compaction** rewrites physical files;
- clustering changes physical layout; **partition evolution** changes a table specification;
- a replica improves availability; a **backup** creates a separately recoverable chain;
- Parquet is a file format; Iceberg is a table-state specification;
- Iceberg REST is a protocol; Polaris is an implementation; a running Polaris service is a
  deployment; catalog operation is a product;
- an object store may supply conditional writes, but it does not thereby own table commits;
- a materialized view, a cluster-local serving index and a result cache have different cuts,
  recovery and sharing laws; and
- vector storage owns vectors, distance, approximation and index state; embedding generation,
  generative retrieval workflows and business similarity remain separately selected neighbors.

Generative models and tool agents are modeled once in the optional model/agent extension universe.
They are not ambient fields, dependencies or laws in these deterministic persistence records. A
typed optional provider may propose configuration or diagnostics, but validation, binding,
execution, evidence and accountable authority remain deterministic and mandatory.

A **data lake** is likewise not a new logical store model or file format. It composes physical
object/distributed-file persistence, namespace/catalog, portable files or tables, ingestion,
maintenance, policy, discovery and query. A **warehouse** may package storage, transactions,
materialization, indexes, query and workload management, but those remain separate semantic and
compiler bindings. Product packaging can join them; it cannot erase their owners, failure modes,
version relations or removal seams.

## Compression and indexing are compiler decisions, not defaults

```text
logical value
   |  value encoding: dictionary / RLE / delta / bit-pack / byte-stream split
   v
encoded page or chunk
   |  compression: none / LZ4 / Snappy / Zstd / gzip / Brotli / extension
   v
compressed independently-decodable unit
   |  optional encryption + authenticated metadata
   v
stored bytes + checksum/digest
```

The compiler must bind codec, level/effort, independent decode unit, format compatibility,
CPU, peak memory, latency, ratio target and hardware target. There is no universally correct
codec. File statistics, Bloom filters, B-trees, bitmap/inverted indexes and approximate vector
indexes are separate decision surfaces because their update cost, precision, privacy leakage,
build time and memory differ. `gap.persistence.compression_kernel_matrix` and
`gap.persistence.index_method_matrix` record the remaining evidence needed for automatic
selection.

## Correct lakehouse boundary

```text
Lakehouse product suite                         commercial/support bundle
└── Managed lakehouse experience                cross-product user journey
    ├── Data ingestion and publication product  adjacent ownership stub here
    ├── Analytical table runtime product
    ├── Catalog and commit authority product
    ├── Analytical query engine product          adjacent ownership stub here
    ├── Table maintenance product
    ├── Materialization and serving product
    ├── Data sharing and exchange product
    ├── Desired-state control-plane product
    └── shared policy/quality/lineage products    owned in neighboring universes
            |
            v
    protocols and formats
    Iceberg/Delta/Hudi/Paimon | Parquet/ORC/Arrow/Zarr
    Iceberg REST | Delta Sharing | Flight SQL | ADBC
            |
            v
    semantic/algorithm/runtime libraries
    identity | schema/partition algebra | snapshot graph | row-change algebra
    commit protocol | scan/compaction/clustering planners | reachability/GC
    encoding/compression/crypto/index kernels | catalog/sharing/federation contracts
            |
            v
    qualified deployments and replaceable providers
    object/file/block storage | catalog servers | table runtimes | serving runtimes
```

The managed experience owns integration, onboarding and cross-product status. It deliberately
has zero data-plane capability references in the registry. The suite owns packaging and
commercial lifecycle. Neither may silently acquire table, catalog, storage, policy, query or
business semantics.

The product candidates are:

1. object storage;
2. transactional data store;
3. analytical table runtime;
4. catalog and commit authority;
5. table maintenance and optimization;
6. materialization and serving;
7. data sharing and exchange;
8. federated data access;
9. backup and recovery;
10. analytical query engine;
11. data ingestion and publication; and
12. persistence desired-state control plane.

These are candidates, not final products. Query execution, compute scheduling, ingestion
pipelines, data quality, lineage, policy and source acquisition require their own full bounded
context universes. Their records here define only the persistence integration boundary.

## Requirement, offer and binding model

```text
intent / vertical analytical case
            |
            v
profile requirements (exact capability + guarantees + decisions + evidence gates)
            |
            v
enumerate offers by capability identity -- never by vendor or suite name
            |
            v
reject unsupported feature/edition/authority/target/resource/evidence
            |
            v
qualify a concrete deployment occurrence
            |
            v
select by declared SLO/cost/portability policy
            |
            v
binding + rejected alternatives + decision trace + receipts + invalidation triggers
```

`compiler-mappings.jsonl` exercises this over 12 profiles: append-only and mutable analytical
tables, regulated immutable analytics, scientific arrays, low-latency OLAP, real-time
time-series, transactional applications, search, vector similarity, external sharing,
federation and supplier exit. Abstract offers remain `candidate`; they are deliberately not
qualified deployments. A compiler that has only a product name encounters the blocking
`gap.persistence.unqualified_deployment`.

## Evidence and innovations

The evidence registry uses primary standards, official format/protocol specifications,
official implementation documentation and release records from standards/projects including
IETF, The Open Group, NVM Express, W3C, OGC, PostgreSQL, SQLite, DuckDB, Apache Cassandra,
Arrow, Parquet, ORC, Avro, Iceberg, Hudi, Paimon, Polaris, XTable, Zarr, Druid and others. Representative
anchors include the [Iceberg table specification](https://iceberg.apache.org/spec/),
[Iceberg REST catalog specification](https://iceberg.apache.org/rest-catalog-spec/),
[Delta protocol](https://github.com/delta-io/delta/blob/master/PROTOCOL.md),
[Hudi technical specification](https://hudi.apache.org/learn/tech-specs/),
[Parquet format](https://parquet.apache.org/docs/file-format/),
[Arrow columnar format](https://arrow.apache.org/docs/format/Columnar.html),
[Zarr v3](https://zarr-specs.readthedocs.io/en/latest/v3/core/index.html) and
[NFSv4.1](https://www.rfc-editor.org/rfc/rfc8881.html).

The innovation registry covers 2021–2026 developments such as NVMe ZNS, Flight SQL, ADBC,
Iceberg REST and v3, Delta feature negotiation/deletion vectors/liquid clustering/kernel,
Paimon primary-key tables, XTable translation, S3 conditional writes, PostgreSQL incremental
backup, Zarr v3/sharding and open catalog implementations. It records boundary/compiler impact
and limitations; it does not turn official project announcements into universal performance
claims.

## Files

- `bounded-contexts.jsonl` and `schemas/bounded-context.schema.json` — 124 candidate contexts
  with vocabulary, invariants, commands/events/refusals, lifecycle, time, concurrency,
  authority, decisions, capabilities and evidence.
- `storage-capabilities.jsonl`, `table-capabilities.jsonl`,
  `catalog-serving-capabilities.jsonl` and `schemas/capability.schema.json` — typed operations,
  guarantees, failure states, effects, information loss, resources, probes and receipt fields.
- `decision-points.jsonl` — 113 records conforming to the shared compiler decision schema;
  every default is forbidden until explicitly selected.
- `boundary-candidates.jsonl` and `schemas/boundary-candidate.schema.json` — libraries, formats,
  protocols, implementations, deployments, products, managed experience and suite.
- `library-boundaries.jsonl` — the 38 semantic, algorithm, policy, oracle, adapter and runtime boundaries projected
  into the shared compiler library contract. Formats, protocols, implementations, deployments,
  products, the managed experience and the suite are deliberately excluded from this file.
- `compiler-mappings.jsonl` and `schemas/compiler-mapping.schema.json` — requirements, abstract
  offers, deterministic binding rules and typed gaps.
- `sources.jsonl` and `schemas/evidence-source.schema.json` — scoped primary/official
  evidence records.
- `innovations.jsonl` and `schemas/innovation.schema.json` — five-year non-LLM innovation records.
- `object-log-architectures.jsonl` and `schemas/object-log-architecture.schema.json` — exact
  commit/read paths, coordination, durable truth, maintenance, enabled capabilities, compiler
  decisions, non-collapse laws, trade-offs and qualification gaps for object-storage WAL/state
  patterns. It distinguishes direct object WAL, shared WAL plus object storage, quorum WAL plus
  object archival, object-native LSM/stream/index/catalog state, checkpointed stream state and
  direct low-latency-object OLTP research.
- `object-log-decision-points.jsonl` and `schemas/object-log-decision.schema.json` — 14
  architecture-selection axes covering acknowledgement, mutation primitive, coordination,
  materialization, freshness, batching, cache, failure domain, metadata authority, garbage
  collection, request economics, recovery, workload isolation and portability. Every selection is
  explicit; the corpus supplies no provider or architecture default.
- `object-log-compiler-contracts.jsonl` and `schemas/object-log-compiler-contract.schema.json` —
  10 workload requirements, 21 architecture-derived offers and 10 deterministic binding rules.
  Architecture offers are evidence-bearing hypotheses only: all are unqualified, non-portable and
  non-selectable until their exact library contracts and deployment evidence gates are satisfied.
- `context-map.jsonl` — explicit strategic relationships; unlisted relationships remain
  unknown rather than being generated by proximity.
- `term-ownership-overlaps.json` — generated ambiguity/adjudication queue.
- `gaps.json` — open research, DDD, provider, conformance, resource, incident and product gates.
- `coverage-report.json` — generated counts and constitutional boundary laws.
- `build_corpus.py` and `validate_corpus.py` — deterministic build and validation.

## Build and validate

```bash
python3 research/domain_atlas/universes/persistence_lakehouse/build_corpus.py
python3 research/domain_atlas/universes/persistence_lakehouse/validate_corpus.py
uv run --with jsonschema python research/domain_atlas/universes/persistence_lakehouse/validate_corpus.py
```

The schema-enabled validator checks closed record shapes as well as cross-file identities,
source/decision/capability ownership, no hidden defaults, profile closure, typed failure and
resource receipts, exact object-log commit stages, explicit unqualified architecture status, the
open-world completion posture, and the lakehouse boundary law. `OLHP` remains an unresolved term;
the corpus recognizes and separately encodes OLTP, OLAP and HTAP rather than silently guessing.
