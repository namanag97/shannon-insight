#!/usr/bin/env python3
"""Build the provider-neutral persistence/lakehouse research corpus.

The registries are intentionally generated from compact, reviewable source definitions.  A
count is a coverage position, never a closed-world completeness claim.
"""

from __future__ import annotations

import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
EDITION = 1
ACCESSED = "2026-08-26"


def dump_jsonl(name: str, rows: list[dict[str, Any]]) -> None:
    with (ROOT / name).open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, sort_keys=True, separators=(",", ":")) + "\n")


def dump_json(name: str, value: Any) -> None:
    (ROOT / name).write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_manifest() -> None:
    artifacts = sorted(p for p in ROOT.rglob("*.json*") if p.name != "manifest.json" and "__pycache__" not in p.parts)
    files = {str(p.relative_to(ROOT)): {"bytes": len(p.read_bytes()), "sha256": hashlib.sha256(p.read_bytes()).hexdigest()} for p in artifacts}
    dump_json("manifest.json", {"manifest_id": "manifest.persistence-lakehouse.v1", "edition": EDITION, "files": files, "completion_claim": False})


# Primary standards, official specifications, official implementation documentation, release
# records and primary research/software.  Authority never extends beyond authority_scope.
SOURCE_SEEDS = [
    ("nist.sp800_34", "Contingency Planning Guide for Federal Information Systems, SP 800-34 Rev. 1", "NIST", "government_standard", "https://csrc.nist.gov/pubs/sp/800/34/r1/upd1/final", "RTO, RPO, impact analysis, recovery strategy, testing and plan maintenance", ["recovery_objective", "recovery_testing", "business_impact"]),
    ("rfc9111.cache", "RFC 9111 HTTP Caching", "IETF / RFC Editor", "internet_standard", "https://www.rfc-editor.org/rfc/rfc9111.html", "Cache key, reuse, freshness, validation, invalidation and collapsed-request requirements", ["cache", "request_collapse", "freshness", "validation"]),
    ("rfc5861.stale", "RFC 5861 HTTP Cache-Control Extensions for Stale Content", "IETF / RFC Editor", "internet_standard", "https://www.rfc-editor.org/rfc/rfc5861.html", "Explicit stale-while-revalidate and stale-if-error bounds", ["cache", "stale_while_revalidate", "stale_if_error"]),
    ("go.singleflight", "golang.org/x/sync/singleflight", "Go Project", "official_library_documentation", "https://pkg.go.dev/golang.org/x/sync/singleflight", "Duplicate function-call suppression, shared result, asynchronous result and explicit forget behavior", ["duplicate_suppression", "single_flight", "runtime_coordination"]),
    ("redis.stampede", "Redis cache-aside stampede protection", "Redis", "official_documentation", "https://redis.io/docs/latest/develop/use-cases/cache-aside/go/", "Cache-aside stampede protection using explicit lock coordination", ["cache_aside", "stampede", "lock_coordination"]),
    ("postgres.create_view", "PostgreSQL CREATE VIEW", "PostgreSQL Global Development Group", "official_documentation", "https://www.postgresql.org/docs/current/sql-createview.html", "View name/schema, defining query, output columns, replacement constraints, security and check options", ["virtual_relation", "view_definition", "view_security", "replacement"]),
    ("trino.create_view", "Trino CREATE VIEW", "Trino", "official_documentation", "https://trino.io/docs/current/sql/create-view.html", "Logical view definition, replacement and definer/invoker security modes", ["virtual_relation", "view_definition", "view_security"]),
    ("trino.alter_view", "Trino ALTER VIEW", "Trino", "official_documentation", "https://trino.io/docs/current/sql/alter-view.html", "View rename, refresh and authorization lifecycle operations", ["virtual_relation", "view_lifecycle", "authorization"]),
    ("lucene.index_writer", "Apache Lucene IndexWriter", "Apache Lucene", "official_api_documentation", "https://lucene.apache.org/core/10_1_0/core/org/apache/lucene/index/IndexWriter.html", "Mutation sequence, buffering, flush, commit, rollback, update/delete and writer-epoch behavior", ["search_index", "mutation", "sequence", "flush", "commit"]),
    ("lucene.point_in_time", "Apache Lucene index package and point-in-time readers", "Apache Lucene", "official_api_documentation", "https://lucene.apache.org/core/10_2_1/core/org/apache/lucene/index/package-summary.html", "Consistent point-in-time reader views, explicit refresh and immutable-segment behavior", ["search_index", "reader_snapshot", "visibility", "segments"]),
    ("elastic.refresh", "Elasticsearch refresh parameter", "Elastic", "official_documentation", "https://www.elastic.co/docs/reference/elasticsearch/rest-apis/refresh-parameter", "Mutation visibility controls, wait-for semantics, forced refresh and bounded listeners", ["search_index", "refresh", "visibility", "resource_bound"]),
    ("elastic.translog", "Elasticsearch translog settings", "Elastic", "official_documentation", "https://www.elastic.co/docs/reference/elasticsearch/index-settings/translog", "Acknowledgement durability, translog persistence, Lucene commit and recovery distinctions", ["search_index", "acknowledgement", "durability", "commit"]),
    ("elastic.index_api", "Elasticsearch create or update document API", "Elastic", "official_api_documentation", "https://www.elastic.co/docs/api/doc/elasticsearch/operation/operation-index", "Sequence-number and primary-term conditional mutation and acknowledgement fields", ["search_index", "mutation", "optimistic_concurrency", "sequence"]),
    ("solr.commits", "Apache Solr commits and transaction logs", "Apache Solr", "official_documentation", "https://solr.apache.org/guide/solr/latest/configuration-guide/commits-transaction-logs.html", "Hard commit, soft commit, searcher opening, transaction-log recovery and visibility/durability tradeoffs", ["search_index", "visibility", "durability", "transaction_log"]),
    ("s3.consistency", "What is Amazon S3?", "Amazon Web Services", "official_documentation", "https://docs.aws.amazon.com/AmazonS3/latest/userguide/Welcome.html", "S3 object identity and documented consistency semantics", ["object_storage", "consistency", "atomic_single_key_update"]),
    ("s3.conditional", "Conditional requests", "Amazon Web Services", "official_documentation", "https://docs.aws.amazon.com/AmazonS3/latest/userguide/conditional-requests.html", "S3 conditional read/write preconditions", ["conditional_write", "optimistic_concurrency"]),
    ("s3.versioning", "S3 Versioning", "Amazon Web Services", "official_documentation", "https://docs.aws.amazon.com/AmazonS3/latest/userguide/Versioning.html", "S3 object-version behavior", ["object_version", "restore"]),
    ("s3.object_lock", "S3 Object Lock", "Amazon Web Services", "official_documentation", "https://docs.aws.amazon.com/AmazonS3/latest/userguide/object-lock.html", "S3 WORM retention and legal hold behavior", ["retention", "immutability", "legal_hold"]),
    ("s3.checksum", "Checking object integrity", "Amazon Web Services", "official_documentation", "https://docs.aws.amazon.com/AmazonS3/latest/userguide/checking-object-integrity.html", "S3 upload/download checksum behavior", ["integrity", "checksum"]),
    ("s3.conditional_release", "Amazon S3 now supports conditional writes", "Amazon Web Services", "official_release", "https://aws.amazon.com/about-aws/whats-new/2024/08/amazon-s3-conditional-writes/", "2024 S3 conditional-write release", ["innovation", "conditional_write"]),
    ("s3.express_append_release", "Amazon S3 Express One Zone supports appending data to an object", "Amazon Web Services", "official_release", "https://aws.amazon.com/about-aws/whats-new/2024/11/amazon-s3-express-one-zone-append-data-object/", "2024 append-to-object release for S3 Express One Zone directory buckets", ["innovation", "append_object", "object_log"]),
    ("s3.express_append", "Appending data to objects in directory buckets", "Amazon Web Services", "official_documentation", "https://docs.aws.amazon.com/AmazonS3/latest/userguide/directory-buckets-objects-append.html", "S3 Express One Zone append preconditions, request accounting and 10,000-part limit", ["append_object", "request_cost", "part_limit", "zonal_storage"]),
    ("chroma.wal3", "wal3: A Write-Ahead Log for Chroma, Built on Object Storage", "Chroma", "official_architecture", "https://www.trychroma.com/engineering/wal3", "Pure object-storage WAL using conditional writes, per-collection logs, asynchronous indexing and self-verifying checksums", ["object_wal", "conditional_write", "setsum", "index_tail_merge"]),
    ("slatedb.introduction", "SlateDB: An Object-Native LSM for Online Systems", "SlateDB", "official_architecture", "https://slatedb.io/blog/introducing-slatedb/", "Object-native embedded LSM architecture, transactions, checkpoints, forks and distributed compaction", ["object_native_lsm", "embedded_store", "snapshot_isolation", "compaction"]),
    ("slatedb.files", "SlateDB files", "SlateDB", "official_documentation", "https://slatedb.io/docs/design/files/", "WAL SST, compacted SST and manifest roles in SlateDB", ["wal_sst", "compacted_sst", "manifest", "recovery"]),
    ("slatedb.source", "SlateDB source repository", "SlateDB", "official_source_code", "https://github.com/slatedb/slatedb", "Open-source Rust implementation and versioned project artifacts", ["object_native_lsm", "implementation", "rust"]),
    ("automq.s3stream", "AutoMQ S3Stream shared streaming storage overview", "AutoMQ", "official_architecture", "https://docs.automq.com/automq/architecture/s3stream-shared-streaming-storage/overview", "Shared WAL plus object-storage streaming architecture and broker/storage separation", ["shared_wal", "object_storage", "stateless_broker", "streaming_log"]),
    ("automq.s3_wal", "Kafka Running on S3 in 100 Lines of Code", "AutoMQ", "official_architecture", "https://www.automq.com/blog/automq-s3-wal-integration", "Vendor architecture and benchmark claims for an S3-compatible WAL backend", ["s3_wal", "stream_batching", "vendor_benchmark"]),
    ("warpstream.architecture", "WarpStream architecture", "WarpStream", "official_architecture", "https://docs.warpstream.com/warpstream/overview/architecture", "Diskless Kafka-compatible agents using object storage and a cloud metadata/control service", ["object_native_stream", "stateless_agent", "workload_isolation"]),
    ("turbopuffer.architecture", "turbopuffer architecture", "turbopuffer", "official_architecture", "https://turbopuffer.com/docs/architecture", "Object storage as durable truth with stateless compute, caches, WAL files and asynchronous indexing", ["object_wal", "vector_search", "full_text_search", "index_tail_merge"]),
    ("turbopuffer.tradeoffs", "turbopuffer tradeoffs", "turbopuffer", "official_documentation", "https://turbopuffer.com/docs/tradeoffs", "Documented object-storage latency, batching, cold-cache and namespace trade-offs", ["cold_start", "write_latency", "batching", "namespace_isolation"]),
    ("neon.architecture", "Neon architecture overview", "Neon", "official_architecture", "https://neon.com/docs/introduction/architecture-overview", "Disaggregated PostgreSQL compute, Safekeeper WAL quorum, page materialization and object-history architecture", ["wal_quorum", "page_server", "object_history", "branching"]),
    ("materialize.architecture", "The Software Architecture of Materialize", "Materialize", "official_architecture", "https://materialize.com/blog/materialize-architecture/", "Persist-backed durable time-varying collections with separate consensus and compute", ["durable_collections", "incremental_view", "object_persist", "consensus"]),
    ("risingwave.architecture", "RisingWave architecture", "RisingWave", "official_architecture", "https://docs.risingwave.com/get-started/architecture", "Streaming compute with barrier checkpoints and persistent object-store state", ["stream_state", "checkpoint", "object_storage", "compaction"]),
    ("s2.architecture", "S2 architecture", "S2", "official_architecture", "https://s2.dev/docs/platform/architecture", "Object-storage-native streams, channel multiplexing, durable acknowledgements and storage-class choices", ["object_stream", "multiplexing", "durable_acknowledgement", "linearizability"]),
    ("s2.lite_source", "S2 lite source repository", "S2", "official_source_code", "https://github.com/s2-streamstore/s2", "Open-source embedded stream implementation using SlateDB", ["embedded_stream", "slatedb", "object_storage"]),
    ("quickwit.architecture", "Quickwit architecture", "Quickwit", "official_architecture", "https://quickwit.io/docs/overview/architecture", "Object-storage-backed immutable search splits with separate metastore and stateless searchers", ["object_native_index", "search_split", "metastore", "range_read"]),
    ("rocklake.source", "RockLake source repository", "Trickle Labs", "official_source_code", "https://github.com/trickle-labs/rocklake", "Early open-source DuckLake catalog implementation backed by SlateDB", ["lakehouse_catalog", "slatedb", "object_storage"]),
    ("btrlog.paper", "BtrLog: Low-Latency Logging for Cloud Database Systems", "BtrLog authors", "primary_research", "https://arxiv.org/abs/2606.27051", "2026 primary research on a reusable quorum-replicated log service with asynchronous object archival", ["wal_service", "quorum", "object_archive", "oltp"]),
    ("milliscale.paper", "Milliscale: Fast Commit on Low-Latency Object Storage", "Milliscale authors", "primary_research", "https://arxiv.org/abs/2603.02108", "2026 primary research on direct OLTP commit using low-latency appendable object storage", ["direct_object_commit", "s3_express", "oltp"]),
    ("oceanbase.bacchus", "OceanBase Bacchus: a High-Performance and Scalable Cloud-Native Shared Storage Architecture for Multi-Cloud", "OceanBase Bacchus authors", "primary_research", "https://arxiv.org/abs/2602.23571", "2026 primary research on an LSM/object-storage architecture with a service-oriented Paxos log and caches", ["shared_storage", "paxos_log", "oltp", "olap", "htap"]),
    ("turso.s3_express", "How Turso built a transactional database using Amazon S3 Express One Zone", "Amazon Web Services and Turso", "official_architecture", "https://aws.amazon.com/blogs/storage/how-turso-built-a-transactional-database-using-amazon-s3-express-one-zone/", "2026 write-through multi-tenant WAL batching, S3 Express commit, NVMe cache and S3 Standard checkpoint architecture", ["direct_object_wal", "sqlite", "multi_tenant_batching", "byoc", "checkpoint"]),
    ("supabase.s3_tables", "Building an open warehouse architecture: Supabase integration with Amazon S3 Tables", "Amazon Web Services and Supabase", "official_architecture", "https://aws.amazon.com/blogs/storage/building-an-open-warehouse-architecture-supabases-integration-with-amazon-s3-tables/", "PostgreSQL WAL capture into Iceberg tables plus query federation", ["cdc", "postgres_wal", "iceberg", "zero_etl", "operational_analytics"]),
    ("hydradb.architecture", "HydraDB architecture", "HydraDB", "official_source_code", "https://github.com/hydra-db/hydradb/blob/main/architecture.md", "Early Rust graph database architecture using SlateDB and object storage with fenced cell writers and index-plus-WAL-tail reads", ["object_native_graph", "slatedb", "writer_fencing", "index_tail_merge"]),
    ("basin.source", "Basin source repository", "vul-os", "official_source_code", "https://github.com/vul-os/basin", "Early Rust PostgreSQL-compatible multi-tenant object-storage database with WAL, columnar files and vector/search indexes", ["postgres_protocol", "object_wal", "columnar_state", "vector_search"]),
    ("walrust.source", "walrust source repository", "walrust", "official_source_code", "https://github.com/russellromney/walrust", "Experimental Rust SQLite WAL replication to S3-compatible storage with compaction and lineage checks", ["sqlite", "wal_shipping", "backup", "read_replica", "object_storage"]),
    ("posix.rename", "rename", "The Open Group", "standard", "https://pubs.opengroup.org/onlinepubs/9799919799/functions/rename.html", "POSIX rename contract", ["filesystem", "atomic_namespace_change"]),
    ("posix.fsync", "fsync", "The Open Group", "standard", "https://pubs.opengroup.org/onlinepubs/9799919799/functions/fsync.html", "POSIX synchronization request contract", ["filesystem", "durability_request"]),
    ("nfs.v41", "RFC 8881: NFS Version 4 Minor Version 1", "IETF", "standard", "https://www.rfc-editor.org/rfc/rfc8881.html", "NFSv4.1 sessions, state, locking and file operations", ["network_filesystem", "locking", "sessions"]),
    ("nvme.spec", "NVM Express specifications", "NVM Express", "standard", "https://nvmexpress.org/specifications/", "NVMe command sets, transports and namespaces", ["block_storage", "namespace", "flush"]),
    ("hdfs.architecture", "HDFS Architecture", "Apache Hadoop", "official_architecture", "https://hadoop.apache.org/docs/current/hadoop-project-dist/hadoop-hdfs/HdfsDesign.html", "HDFS blocks, namespace and replication design", ["distributed_filesystem", "replication"]),
    ("ozone.architecture", "Apache Ozone architecture", "Apache Ozone", "official_architecture", "https://ozone.apache.org/docs/current/concept/ozonearchitecture.html", "Object storage namespace and architecture", ["object_storage", "distributed_storage"]),
    ("ceph.rados", "Ceph storage cluster", "Ceph", "official_architecture", "https://docs.ceph.com/en/latest/rados/", "RADOS object storage, pools and placement", ["object_storage", "replication", "erasure_coding"]),
    ("postgres.isolation", "Transaction Isolation", "PostgreSQL Global Development Group", "official_documentation", "https://www.postgresql.org/docs/current/transaction-iso.html", "PostgreSQL isolation behavior", ["relational_store", "transactions", "isolation"]),
    ("postgres.indexes", "Index Types", "PostgreSQL Global Development Group", "official_documentation", "https://www.postgresql.org/docs/current/indexes-types.html", "PostgreSQL B-tree, hash, GiST, SP-GiST, GIN and BRIN index behavior", ["indexes", "relational_store"]),
    ("postgres.partitioning", "Table Partitioning", "PostgreSQL Global Development Group", "official_documentation", "https://www.postgresql.org/docs/current/ddl-partitioning.html", "PostgreSQL partitioning and pruning", ["partitioning", "relational_store"]),
    ("postgres.backup", "Backup and Restore", "PostgreSQL Global Development Group", "official_documentation", "https://www.postgresql.org/docs/current/backup.html", "PostgreSQL logical and physical backup/restore surfaces", ["backup", "restore", "pitr"]),
    ("postgres.incremental", "PostgreSQL 17 Release", "PostgreSQL Global Development Group", "official_release", "https://www.postgresql.org/docs/17/release-17.html", "PostgreSQL 17 incremental backup and WAL summary release", ["innovation", "incremental_backup"]),
    ("postgres.fdw", "Foreign Data", "PostgreSQL Global Development Group", "official_documentation", "https://www.postgresql.org/docs/current/ddl-foreign-data.html", "PostgreSQL SQL/MED foreign-data access", ["federation", "pushdown"]),
    ("postgres.matview", "Materialized Views", "PostgreSQL Global Development Group", "official_documentation", "https://www.postgresql.org/docs/current/rules-materializedviews.html", "PostgreSQL materialized-view semantics", ["materialization", "refresh"]),
    ("sqlite.file", "Database File Format", "SQLite", "format_specification", "https://www.sqlite.org/fileformat.html", "SQLite database file and page structures", ["embedded_store", "file_format"]),
    ("sqlite.wal", "Write-Ahead Logging", "SQLite", "official_documentation", "https://www.sqlite.org/wal.html", "SQLite WAL concurrency and checkpoint semantics", ["embedded_store", "wal", "checkpoint"]),
    ("mongodb.transactions", "Transactions", "MongoDB", "official_documentation", "https://www.mongodb.com/docs/manual/core/transactions/", "MongoDB multi-document transaction behavior", ["document_store", "transactions"]),
    ("mongodb.sharding", "Sharding", "MongoDB", "official_documentation", "https://www.mongodb.com/docs/manual/sharding/", "MongoDB sharding and distributed-transaction behavior", ["document_store", "sharding"]),
    ("mongodb.changestream", "Change Streams", "MongoDB", "official_documentation", "https://www.mongodb.com/docs/manual/changeStreams/", "MongoDB durable change notification surface", ["document_store", "change_stream"]),
    ("cassandra.overview", "Cassandra architecture overview", "Apache Cassandra", "official_architecture", "https://cassandra.apache.org/doc/latest/cassandra/architecture/overview.html", "Cassandra wide-column, partition and availability model", ["wide_column_store", "replication", "tunable_consistency"]),
    ("cassandra.storage", "Cassandra storage engine", "Apache Cassandra", "official_architecture", "https://cassandra.apache.org/doc/stable/cassandra/architecture/storage-engine.html", "Cassandra LSM, SSTable, commit-log and compaction behavior", ["lsm", "compaction", "wide_column_store"]),
    ("rocksdb.overview", "RocksDB Overview", "Meta RocksDB", "official_documentation", "https://github.com/facebook/rocksdb/wiki/RocksDB-Overview", "RocksDB LSM, write batch and compaction behavior", ["key_value_store", "lsm", "compaction"]),
    ("rocksdb.backup", "RocksDB Backup Engine", "Meta RocksDB", "official_documentation", "https://github.com/facebook/rocksdb/wiki/RocksDB-BackupableDB", "RocksDB backup and restore behavior", ["backup", "key_value_store"]),
    ("redis.persistence", "Redis persistence", "Redis", "official_documentation", "https://redis.io/docs/latest/operate/oss_and_stack/management/persistence/", "Redis RDB/AOF persistence choices", ["cache", "persistence", "wal"]),
    ("redis.replication", "Redis replication", "Redis", "official_documentation", "https://redis.io/docs/latest/operate/oss_and_stack/management/replication/", "Redis primary-replica behavior", ["cache", "replication"]),
    ("neo4j.transactions", "Neo4j transaction management", "Neo4j", "official_documentation", "https://neo4j.com/docs/operations-manual/current/database-internals/transaction-management/", "Neo4j graph transaction behavior", ["property_graph", "transactions"]),
    ("neo4j.clustering", "Neo4j clustering architecture", "Neo4j", "official_architecture", "https://neo4j.com/docs/operations-manual/current/clustering/introduction/", "Neo4j graph replication and causal-consistency behavior", ["property_graph", "replication", "causal_consistency"]),
    ("opensearch.index", "Introduction to OpenSearch indexes", "OpenSearch", "official_documentation", "https://docs.opensearch.org/latest/im-plugin/index-settings/", "OpenSearch index, shard and replica settings", ["search_store", "sharding", "replication"]),
    ("lucene.index", "Apache Lucene index file formats", "Apache Lucene", "format_specification", "https://lucene.apache.org/core/10_3_1/core/org/apache/lucene/codecs/lucene101/package-summary.html", "Lucene index segment and codec behavior", ["inverted_index", "segments", "compression"]),
    ("influx.storage", "InfluxDB 3 Core storage engine", "InfluxData", "official_architecture", "https://docs.influxdata.com/influxdb3/core/reference/internals/storage-engine/", "InfluxDB time-series Parquet storage engine", ["time_series_store", "parquet"]),
    ("influx.durability", "InfluxDB 3 durability", "InfluxData", "official_architecture", "https://docs.influxdata.com/influxdb3/core/reference/internals/durability/", "InfluxDB WAL-to-object-store durability path", ["time_series_store", "wal", "object_storage"]),
    ("ogc.geopackage", "OGC GeoPackage", "Open Geospatial Consortium", "standard", "https://www.ogc.org/standards/geopackage/", "Portable geospatial database standard", ["spatial_store", "embedded_store"]),
    ("qdrant.storage", "Qdrant storage", "Qdrant", "official_architecture", "https://qdrant.tech/documentation/manage-data/storage/", "Qdrant segment, vector and payload storage", ["vector_store", "segments", "index"]),
    ("qdrant.quantization", "Qdrant quantization", "Qdrant", "official_documentation", "https://qdrant.tech/documentation/guides/quantization/", "Vector quantization trade-offs", ["vector_store", "compression", "approximation"]),
    ("milvus.consistency", "Milvus consistency", "Milvus", "official_documentation", "https://milvus.io/docs/consistency.md", "Milvus strong, bounded, session and eventual consistency profiles", ["vector_store", "consistency"]),
    ("milvus.architecture", "Milvus architecture overview", "Milvus", "official_architecture", "https://milvus.io/docs/architecture_overview.md", "Milvus compute/storage separation and persistence architecture", ["vector_store", "object_storage", "compaction"]),
    ("rdf.sparql", "SPARQL 1.1 Query Language", "W3C", "standard", "https://www.w3.org/TR/sparql11-query/", "RDF graph query semantics", ["rdf_store", "query"]),
    ("parquet.format", "Apache Parquet file format", "Apache Parquet", "format_specification", "https://parquet.apache.org/docs/file-format/", "Parquet physical/logical columnar format", ["columnar_file", "row_group", "page"]),
    ("parquet.encoding", "Parquet encodings", "Apache Parquet", "format_specification", "https://parquet.apache.org/docs/file-format/data-pages/encodings/", "Parquet page encoding definitions", ["encoding", "columnar_file"]),
    ("parquet.compression", "Parquet compression", "Apache Parquet", "format_specification", "https://parquet.apache.org/docs/file-format/data-pages/compression/", "Parquet compression-codec bindings", ["compression", "columnar_file"]),
    ("parquet.bloom", "Parquet Bloom filter", "Apache Parquet", "format_specification", "https://parquet.apache.org/docs/file-format/bloomfilter/", "Parquet split-block Bloom-filter format", ["bloom_filter", "predicate_pruning"]),
    ("parquet.encryption", "Parquet modular encryption", "Apache Parquet", "format_specification", "https://parquet.apache.org/docs/file-format/data-pages/encryption/", "Parquet column/footer encryption modules", ["encryption", "columnar_file"]),
    ("orc.spec", "ORC Specification", "Apache ORC", "format_specification", "https://orc.apache.org/specification/ORCv1/", "ORC stripes, indexes, encodings and compression", ["columnar_file", "encoding", "compression"]),
    ("avro.spec", "Apache Avro specification", "Apache Avro", "format_specification", "https://avro.apache.org/docs/current/specification/", "Avro schema resolution and object-container format", ["row_file", "schema_resolution"]),
    ("arrow.columnar", "Arrow Columnar Format", "Apache Arrow", "format_specification", "https://arrow.apache.org/docs/format/Columnar.html", "Arrow in-memory columnar layout and IPC", ["in_memory_columnar", "interchange"]),
    ("arrow.flight", "Arrow Flight RPC", "Apache Arrow", "protocol_specification", "https://arrow.apache.org/docs/format/Flight.html", "Arrow record-batch transport protocol", ["result_delivery", "columnar_transport"]),
    ("arrow.flight_sql", "Arrow Flight SQL", "Apache Arrow", "protocol_specification", "https://arrow.apache.org/docs/format/FlightSql.html", "SQL metadata, query and result transport protocol", ["query_protocol", "result_delivery"]),
    ("arrow.adbc", "Introducing ADBC", "Apache Arrow", "official_release", "https://arrow.apache.org/blog/2023/01/05/introducing-arrow-adbc/", "Arrow-native provider-neutral database API release", ["innovation", "database_api", "interchange"]),
    ("zarr.v3", "Zarr v3 core specification", "Zarr", "format_specification", "https://zarr-specs.readthedocs.io/en/latest/v3/core/index.html", "Chunked multidimensional-array format and codec pipeline", ["array_store", "chunking", "codecs"]),
    ("zarr.v3_2022", "Zarr v3 update: core feature freeze", "Zarr", "official_release", "https://zarr.dev/blog/zep1-update/", "2022 Zarr v3 core-protocol feature-freeze milestone", ["innovation", "array_store", "extension_points"]),
    ("zarr.sharding", "Zarr sharding codec", "Zarr", "format_specification", "https://zarr-specs.readthedocs.io/en/latest/v3/codecs/sharding-indexed/index.html", "Indexed sharding of Zarr chunks", ["array_store", "sharding", "innovation"]),
    ("zarr.python3", "Zarr-Python 3 is here", "Zarr", "official_release", "https://zarr.dev/blog/zarr-python-3-release/", "2025 Zarr-Python v3 implementation release", ["innovation", "array_store"]),
    ("hdf5.format", "HDF5 File Format Specification", "The HDF Group", "format_specification", "https://support.hdfgroup.org/documentation/hdf5/latest/_f_m_t3.html", "HDF5 file, group, dataset and object-header structures", ["array_store", "scientific_store"]),
    ("iceberg.table", "Apache Iceberg Table Specification", "Apache Iceberg", "format_specification", "https://iceberg.apache.org/spec/", "Iceberg table metadata, snapshots, manifests, deletes and evolution", ["table_format", "snapshot", "schema_evolution", "partition_evolution"]),
    ("iceberg.rest", "Iceberg REST Catalog Specification", "Apache Iceberg", "protocol_specification", "https://iceberg.apache.org/rest-catalog-spec/", "Iceberg catalog operations and change-based commits", ["catalog_protocol", "commit_authority", "credential_vending"]),
    ("iceberg.releases", "Apache Iceberg release notes", "Apache Iceberg", "official_release", "https://github.com/apache/iceberg/blob/main/site/docs/releases.md", "Versioned Iceberg release history, including the 0.14 REST catalog client", ["innovation", "catalog_protocol", "release_history"]),
    ("iceberg.view", "Apache Iceberg View Specification", "Apache Iceberg", "format_specification", "https://iceberg.apache.org/view-spec/", "Portable versioned view metadata", ["view_metadata", "catalog"]),
    ("iceberg.v3", "Apache Iceberg specification v3", "Apache Iceberg", "format_specification", "https://iceberg.apache.org/spec/#version-3-row-level-lineage-and-deletion-vectors", "Iceberg v3 row lineage and deletion-vector semantics", ["innovation", "row_lineage", "deletion_vector"]),
    ("iceberg.release_111", "Apache Iceberg 1.11.0 release", "Apache Iceberg", "official_release", "https://iceberg.apache.org/blog/apache-iceberg-1.11.0-release/", "2026 remote scan planning, REST mutation idempotency and metadata-cache release record", ["innovation", "remote_scan_planning", "idempotency", "catalog_cache"]),
    ("iceberg_go_060", "Apache Iceberg Go 0.6.0 release", "Apache Iceberg", "official_release", "https://iceberg.apache.org/blog/apache-iceberg-go-0.6.0-release/", "2026 implementation support for deletion-vector read/write and row lineage", ["innovation", "deletion_vector", "row_lineage", "implementation"]),
    ("delta.protocol", "Delta Transaction Log Protocol", "Delta Lake", "protocol_specification", "https://github.com/delta-io/delta/blob/master/PROTOCOL.md", "Delta table actions, protocol features, checkpoints and deletion vectors", ["table_format", "transaction_log", "feature_negotiation"]),
    ("delta.features", "Delta Lake Table Features", "Delta Lake", "official_release", "https://delta.io/blog/2023-07-27-delta-lake-table-features/", "2023 table-feature protocol negotiation", ["innovation", "feature_negotiation"]),
    ("delta.deletion_vectors", "Delta Lake Deletion Vectors", "Delta Lake", "official_release", "https://delta.io/blog/2023-07-05-deletion-vectors", "2023 Delta deletion-vector release and stated trade-offs", ["innovation", "deletion_vector", "merge_on_read"]),
    ("delta.liquid", "Delta Lake project innovation", "Delta Lake", "official_release", "https://delta.io/blog/state-of-the-project-pt1/", "2023 liquid-clustering and deletion-vector project record", ["innovation", "clustering"]),
    ("delta.kernel", "Delta Lake 3.0", "Delta Lake", "official_release", "https://delta.io/blog/delta-lake-3-0/", "2023 Delta Kernel and checkpoint-v2 release record", ["innovation", "table_kernel"]),
    ("hudi.spec", "Apache Hudi Technical Specification", "Apache Hudi", "format_specification", "https://hudi.apache.org/learn/tech-specs/", "Hudi timeline, table types, storage and concurrency", ["table_format", "timeline", "copy_on_write", "merge_on_read"]),
    ("hudi.release1", "Apache Hudi 1.0.0 release", "Apache Hudi", "official_release", "https://hudi.apache.org/releases/release-1.0/", "Hudi 1.0 non-blocking concurrency control, indexing, partial-update and format release record", ["innovation", "non_blocking_concurrency", "secondary_index", "partial_update"]),
    ("hudi.timeline", "Apache Hudi Timeline", "Apache Hudi", "official_documentation", "https://hudi.apache.org/docs/next/timeline/", "Requested/completed instants and table-action history", ["timeline", "transactions"]),
    ("hudi.metadata", "Apache Hudi Metadata Table", "Apache Hudi", "official_documentation", "https://hudi.apache.org/docs/metadata/", "Hudi scalable table metadata indexes", ["metadata_index", "innovation"]),
    ("paimon.spec", "Apache Paimon file format", "Apache Paimon", "format_specification", "https://paimon.apache.org/docs/master/concepts/spec/overview/", "Paimon snapshot, manifest, data-file and changelog structures", ["table_format", "primary_key_table", "changelog"]),
    ("paimon.primary_key", "Paimon primary-key table", "Apache Paimon", "official_documentation", "https://paimon.apache.org/docs/master/primary-key-table/", "Paimon primary-key merge-engine behavior", ["primary_key_table", "merge_engine"]),
    ("paimon.release1", "Apache Paimon 1.0.1 release", "Apache Paimon", "official_release", "https://paimon.apache.org/releases/1.0.1/", "2025 Paimon object/format tables, deletion vectors, bitmap file indexes and lookup improvements", ["innovation", "table_format", "deletion_vector", "bitmap_index"]),
    ("xtable.interop", "Apache XTable", "Apache XTable", "official_architecture", "https://xtable.apache.org/", "Metadata translation among lakehouse table formats", ["format_interoperability", "metadata_translation", "innovation"]),
    ("xtable.limitations", "XTable features and limitations", "Apache XTable", "official_documentation", "https://xtable.apache.org/docs/features-and-limitations/", "XTable incremental/full sync and limitations", ["format_interoperability", "maintenance"]),
    ("polaris.docs", "Apache Polaris Documentation", "Apache Polaris", "official_documentation", "https://polaris.apache.org/docs/", "Open Iceberg catalog implementation documentation", ["catalog_implementation", "iceberg_rest"]),
    ("polaris.releases", "Apache Polaris releases", "Apache Polaris", "official_release", "https://polaris.apache.org/releases/", "Versioned public releases of the Polaris Iceberg REST catalog implementation", ["innovation", "catalog_implementation", "release_history"]),
    ("polaris.tlp", "Apache Polaris becomes a top-level project", "Apache Software Foundation", "official_release", "https://news.apache.org/foundation/entry/the-apache-software-foundation-graduates-two-open-source-projects-from-incubator", "2026 Apache Polaris project-maturity event", ["innovation", "catalog_implementation"]),
    ("nessie.concepts", "Project Nessie concepts", "Project Nessie", "official_documentation", "https://projectnessie.org/nessie-latest/concepts/", "Versioned catalog branches, tags and commits", ["versioned_catalog", "branches", "tags"]),
    ("unitycatalog.api", "Unity Catalog OpenAPI", "LF AI & Data Unity Catalog", "protocol_specification", "https://github.com/unitycatalog/unitycatalog/blob/main/api/all.yaml", "Experimental open catalog API surface", ["catalog_protocol", "credential_vending", "commit_coordination"]),
    ("hive.metastore", "Apache Hive Metastore Administration", "Apache Hive", "official_documentation", "https://hive.apache.org/docs/latest/admin/adminmanual-metastore-administration/", "Hive metastore service and backing-store architecture", ["catalog_implementation", "metastore"]),
    ("druid.storage", "Apache Druid Storage Overview", "Apache Druid", "official_architecture", "https://druid.apache.org/docs/latest/design/storage/", "Druid immutable segment, metadata and handoff behavior", ["olap_serving", "segments", "deep_storage"]),
    ("druid.deep", "Apache Druid Deep Storage", "Apache Druid", "official_documentation", "https://druid.apache.org/docs/latest/design/deep-storage/", "Druid provider storage boundary", ["olap_serving", "deep_storage"]),
    ("pinot.segment", "Apache Pinot segment", "Apache Pinot", "official_documentation", "https://docs.pinot.apache.org/basics/components/table/segment", "Pinot immutable segment and index structures", ["olap_serving", "segments", "indexes"]),
    ("clickhouse.mergetree", "MergeTree table engines", "ClickHouse", "official_documentation", "https://clickhouse.com/docs/engines/table-engines/mergetree-family/mergetree", "ClickHouse parts, primary index, merges and partitions", ["warehouse", "parts", "merge"]),
    ("timescale.aggregate", "Timescale continuous aggregates", "Timescale", "official_documentation", "https://docs.timescale.com/use-timescale/latest/continuous-aggregates/about-continuous-aggregates/", "Incremental and real-time aggregate materialization", ["time_series_store", "materialization", "incremental_refresh"]),
    ("materialize.views", "Materialize Views", "Materialize", "official_documentation", "https://materialize.com/docs/concepts/views/", "Durable materialized views and cluster-local indexes", ["materialization", "incremental_refresh", "serving"]),
    ("duckdb.release1", "Announcing DuckDB 1.0.0", "DuckDB", "official_release", "https://duckdb.org/2024/06/03/announcing-duckdb-100", "2024 stable storage-format compatibility policy milestone", ["innovation", "embedded_analytics", "storage_compatibility"]),
    ("delta.sharing", "Delta Sharing Protocol", "Delta Lake", "protocol_specification", "https://github.com/delta-io/delta-sharing/blob/main/PROTOCOL.md", "Share, recipient, table-cut and delivery protocol", ["data_sharing", "presigned_access", "change_feed"]),
    ("arrow.flight_sql_release", "Introducing Apache Arrow Flight SQL", "Apache Arrow", "official_release", "https://arrow.apache.org/blog/2022/02/16/introducing-arrow-flight-sql/", "2022 Flight SQL protocol introduction", ["innovation", "query_protocol", "result_delivery"]),
    ("trino.catalog", "CREATE CATALOG", "Trino", "official_documentation", "https://trino.io/docs/current/sql/create-catalog.html", "Trino connector-backed catalog registration", ["federation", "catalog_routing"]),
    ("substrait.serialization", "Substrait serialization", "Substrait", "protocol_specification", "https://substrait.io/serialization/", "Portable relational-plan serialization boundary", ["federation", "pushdown", "query_plan"]),
]


def build_sources() -> list[dict[str, Any]]:
    rows = []
    for slug, title, publisher, kind, url, scope, supports in SOURCE_SEEDS:
        rows.append({
            "source_id": f"source.persistence.{slug}",
            "edition": EDITION,
            "status": "active",
            "title": title,
            "publisher": publisher,
            "source_kind": kind,
            "url": url,
            "authority_scope": scope,
            "supports": supports,
            "limitations": [
                "Supports only the named specification, implementation or release surface.",
                "Does not establish provider-neutral completeness, deployment qualification or universal performance."
            ],
            "primary_or_official": True,
            "accessed_at": ACCESSED,
        })
    return rows


FAMILY_META = {
    "physical_storage": "Bytes, addressing media, durability and lifecycle below logical stores.",
    "store_model": "Persistent logical data models and their transaction/query authority.",
    "file_format": "Portable byte layouts, encodings, compression, indexes and interchange.",
    "analytical_table": "Logical analytical-table identity, snapshots, mutations and evolution.",
    "catalog": "Namespace, metadata, commit and location authority over persistent assets.",
    "maintenance": "Semantics-preserving physical rewrites, expiry, cleanup and optimization.",
    "serving": "Persistent or cached structures operated to satisfy read and freshness objectives.",
    "sharing_federation": "Cross-authority discovery, access, exchange, delegation and pushdown."
}


# family, slug, name, boundary question, inside, outside, evidence slugs, operations
CONTEXT_SEEDS = [
    # Physical storage
    ("physical_storage", "block_device", "Block Device", "What ordered block operations are acknowledged durable within which device namespace?", ["logical block address", "flush/fua", "discard", "namespace", "endurance evidence"], ["file naming", "object listing", "table commits"], ["nvme.spec"], ["read_blocks", "write_blocks", "flush_blocks"]),
    ("physical_storage", "local_filesystem", "Local Filesystem", "What path, inode, rename, lock and synchronization semantics exist on one mounted filesystem?", ["path", "file handle", "directory entry", "rename", "fsync"], ["network lease", "object version", "table snapshot"], ["posix.rename", "posix.fsync"], ["open_file", "atomic_rename", "synchronize_file"]),
    ("physical_storage", "network_filesystem", "Network Filesystem", "What remote file state, session, lease and lock semantics survive retries and partitions?", ["session", "stateid", "open", "byte-range lock", "delegation"], ["database isolation", "object-store consistency"], ["nfs.v41"], ["open_remote_file", "lock_range", "recover_session"]),
    ("physical_storage", "distributed_filesystem", "Distributed Filesystem", "How are a hierarchical namespace and replicated immutable or appendable blocks committed and recovered?", ["namenode authority", "block", "replica", "pipeline", "filesystem snapshot"], ["table snapshot", "business retention"], ["hdfs.architecture"], ["allocate_block", "commit_file", "snapshot_namespace"]),
    ("physical_storage", "object_namespace", "Object Storage Namespace", "What object-key, version, listing, range and conditional-write laws does a bucket expose?", ["bucket", "object key", "object version", "etag/precondition", "range read", "multipart upload"], ["directory atomicity", "cross-key transaction", "table schema"], ["s3.consistency", "s3.conditional", "ozone.architecture", "ceph.rados"], ["put_object", "get_object_range", "conditional_replace", "list_objects"]),
    ("physical_storage", "archival_media", "Archival and Offline Media", "How is a retained object staged to offline media and later recalled with explicit latency and integrity?", ["archive tier", "recall job", "media copy", "retrieval window"], ["logical table expiry", "query planning"], ["s3.object_lock", "s3.versioning"], ["archive_object", "recall_object", "verify_archival_copy"]),
    ("physical_storage", "persistent_memory", "Persistent Byte-Addressable Memory", "Which persistence domain and ordering barriers make memory writes survive failure?", ["persistence domain", "cache-line flush", "ordering barrier", "failure atomicity"], ["database transaction", "filesystem namespace"], ["nvme.spec"], ["persist_range", "recover_persistent_region"]),
    ("physical_storage", "integrity", "Storage Integrity", "Which digest, checksum and verification evidence proves bytes were not silently changed in transit or at rest?", ["checksum algorithm", "content digest", "verification scope", "corruption finding"], ["business authenticity", "semantic equality"], ["s3.checksum", "parquet.encryption"], ["compute_checksum", "verify_checksum", "record_corruption"]),
    ("physical_storage", "encryption", "Storage Encryption", "Which bytes and metadata are encrypted under which key authority, rotation and failure law?", ["encryption envelope", "data key", "key reference", "ciphertext module", "rotation"], ["identity authentication", "business authorization"], ["parquet.encryption", "s3.object_lock"], ["encrypt_payload", "decrypt_payload", "rotate_data_key"]),
    ("physical_storage", "replication", "Storage Replication", "Which acknowledged writes are copied to which failure domains under what lag and consistency?", ["replica", "failure domain", "replication position", "ack quorum", "lag"], ["backup retention", "logical duplicate"], ["ceph.rados", "hdfs.architecture", "redis.replication"], ["replicate_write", "measure_replica_lag", "repair_replica"]),
    ("physical_storage", "erasure_durability", "Erasure-Coded Durability", "How are data/parity fragments placed, reconstructed and scrubbed within a declared fault model?", ["data shard", "parity shard", "coding profile", "fault domain", "scrub"], ["application compression", "logical replication"], ["ceph.rados"], ["encode_fragments", "reconstruct_fragment", "scrub_fragments"]),
    ("physical_storage", "tiering", "Storage Tiering and Placement", "Where should each exact byte cut reside over time given access, residency, durability and cost constraints?", ["storage class", "placement rule", "temperature", "transition", "recall"], ["business retention", "query routing semantics"], ["s3.versioning", "druid.deep"], ["place_object", "transition_tier", "verify_placement"]),
    ("physical_storage", "retention_immutability", "Retention and Immutability", "Until when must an exact version remain undeletable, and under whose hold or expiry authority?", ["retention period", "legal hold", "WORM mode", "protected version", "expiry authority"], ["snapshot reachability", "privacy erasure adjudication"], ["s3.object_lock", "s3.versioning"], ["place_hold", "release_hold", "enforce_retention"]),
    ("physical_storage", "quota_cost", "Storage Quota and Cost Accounting", "Which tenant or workload owns stored bytes, requests, egress and recovery cost under finite limits?", ["quota", "meter", "billing dimension", "budget", "allocation"], ["business chargeback policy", "query optimizer"], ["s3.consistency", "ceph.rados"], ["reserve_capacity", "meter_storage", "refuse_over_quota"]),
    ("physical_storage", "backup", "Backup Capture", "What recoverable cut, dependencies and manifest were captured without claiming restore success?", ["backup cut", "backup manifest", "base backup", "incremental backup", "chain"], ["restore verification", "replica availability"], ["postgres.backup", "postgres.incremental", "rocksdb.backup"], ["capture_full_backup", "capture_incremental_backup", "verify_backup_manifest"]),
    ("physical_storage", "restore", "Restore and Point-in-Time Recovery", "Can a named backup/log chain reconstruct an exact target cut in a clean environment?", ["restore target", "recovery point", "redo log", "restored cut", "restore proof"], ["business reconciliation", "application restart"], ["postgres.backup", "postgres.incremental", "rocksdb.backup"], ["plan_restore", "restore_cut", "verify_restored_cut"]),
    ("physical_storage", "recovery_objectives", "Recovery Objective Evidence", "For one authority-bound scope and measurement profile, what exact recovered cut and accepted service interval were demonstrated relative to declared RPO and RTO?", ["recovery objective set", "disruption reference cut", "accepted recovered cut", "recovery start/end boundaries", "objective measurement evidence", "measurement residual"], ["business impact tolerance authority", "incident declaration authority", "backup or restore execution", "application acceptance criteria"], ["nist.sp800_34", "postgres.backup", "postgres.incremental"], ["bind_recovery_objectives", "measure_achieved_rpo", "measure_achieved_rto", "evaluate_recovery_objective_attainment", "explain_measurement_residuals"]),
    ("physical_storage", "physical_deletion", "Physical Deletion and Media Reclamation", "When may unreachable bytes be physically destroyed, and what evidence proves scope and irreversibility?", ["deletion candidate", "safety horizon", "secure erase", "reclamation receipt"], ["logical row deletion", "snapshot expiry decision"], ["s3.object_lock", "rocksdb.overview"], ["authorize_reclamation", "reclaim_bytes", "verify_reclamation"]),

    # Persistent logical store models
    ("store_model", "relational_store", "Transactional Relational Store", "What relations, constraints and transaction isolation are authoritatively persisted?", ["relation", "tuple", "key", "constraint", "transaction", "isolation level"], ["semantic metric", "analytical table file layout"], ["postgres.isolation", "postgres.indexes"], ["execute_transaction", "enforce_constraint", "read_consistent_cut"]),
    ("store_model", "document_store", "Document Store", "What versioned documents and paths are atomically mutated within which transaction scope?", ["document", "collection", "document key", "path update", "transaction"], ["relational join law", "object blob"], ["mongodb.transactions", "mongodb.sharding"], ["put_document", "patch_document", "read_document_cut"]),
    ("store_model", "key_value_store", "Ordered Key-Value Store", "What key space, ordering, snapshots, batches and merge semantics persist byte values?", ["key", "value", "column family", "snapshot", "write batch", "merge operator"], ["document schema", "business entity"], ["rocksdb.overview"], ["put_key", "atomic_write_batch", "iterate_key_range"]),
    ("store_model", "wide_column_store", "Wide-Column Store", "What partition/clustering-key model and tunable consistency govern sparse rows across replicas?", ["partition key", "clustering key", "cell timestamp", "consistency level", "repair"], ["distributed joins", "cross-partition transaction"], ["cassandra.overview", "cassandra.storage"], ["mutate_partition", "read_at_consistency", "repair_partition"]),
    ("store_model", "property_graph_store", "Property-Graph Store", "What node, relationship, property and graph-transaction state is durably authoritative?", ["node", "relationship", "property", "graph constraint", "bookmark"], ["RDF entailment", "graph analytics result"], ["neo4j.transactions", "neo4j.clustering"], ["commit_graph_transaction", "traverse_graph", "read_after_bookmark"]),
    ("store_model", "rdf_store", "RDF Dataset Store", "What RDF terms, named graphs and entailment regime define the persisted dataset queried by SPARQL?", ["IRI", "blank node", "literal", "triple", "named graph", "dataset"], ["property-graph identity", "ontology governance"], ["rdf.sparql"], ["load_rdf_graph", "update_rdf_dataset", "query_sparql"]),
    ("store_model", "time_series_store", "Time-Series Store", "How are series identity, event time, late updates, retention and downsampling persisted?", ["series key", "sample", "event time", "field", "retention window", "downsample"], ["business metric definition", "stream watermark authority"], ["influx.storage", "influx.durability", "timescale.aggregate"], ["append_sample", "query_time_range", "downsample_series"]),
    ("store_model", "spatial_store", "Spatial Store", "What coordinate reference, geometry identity and spatial index semantics persist and query features?", ["feature", "geometry", "CRS", "spatial extent", "spatial index"], ["map visualization", "geocoding authority"], ["ogc.geopackage", "postgres.indexes"], ["store_feature", "spatial_query", "transform_crs"]),
    ("store_model", "search_store", "Search and Inverted-Index Store", "What analyzed fields, terms, postings, segments and refresh cut define searchable state?", ["document", "field", "analyzer", "term", "posting", "segment", "refresh"], ["source document authority", "vector similarity"], ["opensearch.index", "lucene.index"], ["index_document", "refresh_search_cut", "search_terms"]),
    ("store_model", "index_mutation", "Index Mutation Generation and Acknowledgement", "For one index edition and writer/primary epoch, what immutable add, replace, delete or no-op mutation was admitted, ordered, attempted and acknowledged under which conflict, replication and durability posture?", ["index mutation", "mutation batch", "writer epoch", "mutation order token", "source revision precondition", "idempotency key", "mutation attempt", "acknowledgement scope", "mutation receipt", "mutation residual"], ["source-document truth", "document projection semantics", "search visibility", "ranking policy", "provider storage implementation"], ["lucene.index_writer", "elastic.index_api", "elastic.translog", "solr.commits"], ["bind_index_mutation_contract", "admit_mutation_batch", "submit_index_mutation", "record_mutation_acknowledgement", "reconcile_mutation_outcome", "project_mutation_frontier"]),
    ("store_model", "vector_store", "Vector Similarity Store", "What vector, distance, filter and approximation contract defines persisted nearest-neighbor search?", ["vector", "dimension", "distance function", "point", "payload", "index", "recall target"], ["embedding generation", "LLM semantics", "business similarity"], ["qdrant.storage", "qdrant.quantization", "milvus.consistency"], ["upsert_vector", "build_vector_index", "search_neighbors"]),
    ("store_model", "cache_store", "Cache Store", "Which derived values may be evicted or expire without becoming an authority of record?", ["cache key", "cached value", "TTL", "eviction", "invalidation token"], ["source-of-truth mutation", "durability claim"], ["redis.persistence", "redis.replication"], ["cache_value", "invalidate_key", "evict_value"]),
    ("store_model", "event_journal", "Event Journal Store", "What append order, stream identity, expected version and retention preserve immutable facts?", ["stream", "event", "sequence", "expected version", "tombstone"], ["projection state", "message delivery"], ["mongodb.changestream", "hudi.timeline"], ["append_event", "read_stream", "truncate_stream"]),
    ("store_model", "scientific_array_store", "Scientific Array Store", "How are typed N-dimensional arrays, chunks, fill values and coordinates persistently addressed?", ["array", "shape", "dtype", "chunk grid", "fill value", "coordinate"], ["domain variable meaning", "visualization"], ["zarr.v3", "hdf5.format"], ["create_array", "write_chunk", "read_array_slice"]),
    ("store_model", "content_blob_store", "Content and Blob Store", "How are immutable or versioned opaque payloads, media type and content identity persisted?", ["blob", "content digest", "media type", "version", "metadata"], ["document semantics", "table rows"], ["s3.consistency", "s3.versioning"], ["put_blob", "get_blob", "verify_blob_identity"]),
    ("store_model", "embedded_store", "Embedded and Edge Store", "What local single-process or device-scoped persistence survives crash and disconnected operation?", ["database file", "page", "WAL", "checkpoint", "device cut"], ["distributed consensus", "global source authority"], ["sqlite.file", "sqlite.wal", "ogc.geopackage"], ["commit_local_transaction", "checkpoint_local_wal", "export_edge_cut"]),
    ("store_model", "stream_state_store", "Stream Processor State Store", "What keyed/operator state and timer cut is checkpointed consistently with input progress?", ["operator state", "keyed state", "timer", "checkpoint", "savepoint", "input position"], ["event-source retention", "business record"], ["rocksdb.overview", "hudi.timeline"], ["checkpoint_operator_state", "restore_operator_state", "compact_state"]),
    ("store_model", "analytical_warehouse", "Analytical Warehouse Store", "What governed relational analytical state, workload isolation and durable service level are persisted?", ["warehouse table", "partition", "micro-part", "workload", "cluster", "result cut"], ["business metric meaning", "source ingestion correctness"], ["clickhouse.mergetree", "postgres.partitioning"], ["load_warehouse_table", "serve_warehouse_query", "recluster_warehouse_data"]),
    ("store_model", "olap_segment_store", "OLAP Segment Store", "What immutable indexed segment timeline is published, loaded and served for low-latency aggregation?", ["datasource", "segment", "interval", "version", "handoff", "deep storage"], ["raw-source authority", "general transaction processing"], ["druid.storage", "pinot.segment"], ["publish_segment", "load_segment", "replace_segment_set"]),
    ("store_model", "ledger_store", "Append-Only Ledger Store", "What hash-linked or sequenced entries are authoritative, auditable and correctable without destructive rewrite?", ["ledger entry", "sequence", "prior digest", "correction", "checkpoint"], ["financial-accounting semantics", "distributed-ledger consensus"], ["hudi.timeline", "s3.object_lock"], ["append_ledger_entry", "verify_ledger_chain", "post_correction"]),

    # Analytical files and representation
    ("file_format", "row_file", "Row-Oriented Data File", "How are records, schema identity and block synchronization encoded for sequential interchange?", ["record", "writer schema", "reader schema", "block", "sync marker"], ["table transaction", "storage durability"], ["avro.spec"], ["encode_records", "decode_records", "resolve_reader_schema"]),
    ("file_format", "columnar_file", "Columnar Analytical File", "How are columns divided into row groups/pages with projection and pruning metadata?", ["column chunk", "row group", "page", "footer", "logical type", "statistics"], ["table snapshot", "query semantics"], ["parquet.format", "orc.spec"], ["encode_columnar_file", "decode_projection", "prune_row_groups"]),
    ("file_format", "array_chunk_format", "Chunked Array Format", "How are N-dimensional chunks mapped through codecs to storage keys?", ["chunk grid", "chunk key", "codec pipeline", "fill value", "shard index"], ["scientific coordinate semantics", "object-store guarantee"], ["zarr.v3", "zarr.sharding"], ["encode_array_chunk", "decode_array_region", "map_chunk_key"]),
    ("file_format", "in_memory_columnar", "In-Memory Columnar Interchange", "Which buffers, validity maps, offsets and schemas permit zero-copy columnar interchange?", ["array", "buffer", "validity bitmap", "offset", "record batch", "schema"], ["durable file identity", "database transaction"], ["arrow.columnar"], ["export_record_batch", "import_record_batch", "validate_buffer_layout"]),
    ("file_format", "logical_types", "Portable Logical Types", "How does a physical carrier encode a logical value without losing units, precision, timezone or identity?", ["physical type", "logical annotation", "precision", "scale", "timezone", "field id"], ["industry semantic ownership", "formula semantics"], ["parquet.format", "avro.spec", "arrow.columnar"], ["annotate_logical_type", "validate_type_mapping", "migrate_type"]),
    ("file_format", "encoding", "Column and Value Encoding", "Which reversible transform maps values to bytes with declared applicability and decode law?", ["encoding", "dictionary", "run length", "delta", "bit packing", "byte stream split"], ["general compression", "encryption"], ["parquet.encoding", "orc.spec"], ["select_encoding", "encode_values", "decode_values"]),
    ("file_format", "compression", "Compression Codec", "Which reversible codec chain trades CPU, memory, latency and bytes for a declared unit?", ["codec", "level", "frame", "dictionary", "compression unit", "ratio"], ["logical encoding", "encryption", "table compaction"], ["parquet.compression", "orc.spec", "zarr.v3"], ["compress_bytes", "decompress_bytes", "benchmark_codec"]),
    ("file_format", "modular_encryption", "File and Column Encryption", "Which file modules are encrypted, authenticated and key-addressable without destroying required pruning?", ["encrypted module", "footer key", "column key", "AAD", "ciphertext"], ["principal authorization", "key-management implementation"], ["parquet.encryption"], ["encrypt_file_modules", "decrypt_file_projection", "rotate_file_keys"]),
    ("file_format", "file_statistics", "File Statistics", "Which exact cut, column and page do min/max/null/count summaries describe, with what leakage and validity?", ["statistics scope", "lower bound", "upper bound", "null count", "distinct estimate"], ["business metric", "optimizer cost model"], ["parquet.format", "orc.spec"], ["compute_file_statistics", "validate_statistics", "redact_statistics"]),
    ("file_format", "probabilistic_index", "Probabilistic File Index", "What no-false-negative membership contract and false-positive budget govern a side index?", ["Bloom filter", "hash", "bitset", "false-positive probability", "column scope"], ["exact secondary index", "semantic search"], ["parquet.bloom"], ["build_bloom_filter", "probe_bloom_filter", "measure_false_positive_rate"]),
    ("file_format", "fragmentation", "File Fragmentation and Sizing", "What file/page/chunk shape balances parallelism, metadata requests, pruning and write amplification?", ["target file size", "small file", "row group size", "fragmentation", "request amplification"], ["logical partition meaning", "compute scheduler"], ["parquet.format", "druid.storage"], ["measure_fragmentation", "recommend_file_shape", "verify_file_shape"]),
    ("file_format", "columnar_transport", "Columnar Result Transport", "How are schemas and record batches framed, partitioned, authenticated and resumed across a transport?", ["flight descriptor", "ticket", "endpoint", "record batch", "application metadata"], ["query planning", "storage persistence"], ["arrow.flight", "arrow.flight_sql"], ["publish_result_stream", "consume_result_stream", "resume_result_stream"]),
    ("file_format", "format_compatibility", "Format Capability Negotiation", "Can a reader/writer safely consume this exact format edition and enabled feature set?", ["format edition", "reader feature", "writer feature", "required feature", "compatibility verdict"], ["provider version marketing", "silent downgrade"], ["delta.protocol", "iceberg.table"], ["negotiate_format_features", "refuse_unsupported_feature", "record_compatibility"]),

    # Analytical tables
    ("analytical_table", "table_identity", "Analytical Table Identity", "What stable table identity survives location, schema and snapshot changes?", ["table id", "qualified name", "metadata location", "table edition"], ["business entity identity", "catalog display label"], ["iceberg.table", "delta.protocol"], ["create_table_identity", "resolve_table_identity", "relocate_table"]),
    ("analytical_table", "schema_evolution", "Table Schema Evolution", "Which field-identity-preserving schema changes are compatible for readers and writers?", ["field id", "schema id", "add", "drop", "rename", "type promotion"], ["source schema authority", "business concept migration"], ["iceberg.table", "delta.protocol"], ["propose_schema_change", "validate_schema_change", "commit_schema_change"]),
    ("analytical_table", "partition_evolution", "Partition Evolution", "How may partition transforms change without rewriting or misreading historical files?", ["partition spec", "transform", "spec id", "hidden partitioning"], ["business grouping", "physical clustering"], ["iceberg.table", "paimon.spec"], ["propose_partition_spec", "derive_partition_tuple", "commit_partition_evolution"]),
    ("analytical_table", "snapshot_state", "Table Snapshot State", "Which immutable metadata cut enumerates the exact current table contents?", ["snapshot", "parent snapshot", "manifest list", "data file", "delete file"], ["catalog namespace", "query result"], ["iceberg.table", "delta.protocol"], ["construct_snapshot", "load_snapshot", "diff_snapshots"]),
    ("analytical_table", "append_mutation", "Append Mutation", "How are new files or rows atomically added against an expected table state?", ["append intent", "base snapshot", "new file", "commit requirement"], ["source deduplication", "file writing implementation"], ["iceberg.table", "delta.protocol"], ["plan_append", "validate_append", "commit_append"]),
    ("analytical_table", "overwrite_mutation", "Overwrite Mutation", "How is a declared predicate or partition set atomically replaced without deleting unrelated rows?", ["overwrite predicate", "removed file", "added file", "conflict scope"], ["business correction authority", "physical reclamation"], ["iceberg.table", "delta.protocol"], ["plan_overwrite", "validate_overwrite", "commit_overwrite"]),
    ("analytical_table", "row_level_mutation", "Row-Level Mutation", "How are updates, deletes and merges represented and reconciled at row identity or predicate scope?", ["row delta", "equality delete", "position delete", "deletion vector", "merge"], ["source-of-record mutation", "privacy erasure adjudication"], ["iceberg.table", "delta.protocol", "hudi.spec"], ["plan_row_change", "write_row_delta", "commit_row_change"]),
    ("analytical_table", "copy_on_write", "Copy-on-Write Table State", "When must changed rows be materialized by replacing complete data files before publication?", ["rewrite set", "replacement file", "write amplification", "read-optimized state"], ["delete-vector read", "maintenance scheduling"], ["hudi.spec", "delta.deletion_vectors"], ["plan_copy_on_write", "rewrite_changed_files", "publish_replacement_files"]),
    ("analytical_table", "merge_on_read", "Merge-on-Read Table State", "How are base files and ordered deltas combined into a correct current view?", ["base file", "delta log", "delete vector", "merge order", "compaction debt"], ["generic stream merge", "business conflict resolution"], ["hudi.spec", "delta.deletion_vectors", "paimon.primary_key"], ["write_delta", "merge_at_read", "measure_merge_debt"]),
    ("analytical_table", "commit_protocol", "Table Commit Protocol", "How does an expected base state become exactly one new authoritative table state?", ["commit requirement", "commit update", "compare-and-swap", "conflict", "commit receipt"], ["object upload durability", "multi-table transaction"], ["iceberg.table", "iceberg.rest", "delta.protocol"], ["prepare_table_commit", "commit_table_state", "retry_table_commit"]),
    ("analytical_table", "isolation_conflicts", "Table Isolation and Conflict Detection", "Which concurrent mutations may both commit, retry, rebase or refuse under a declared isolation level?", ["serializable", "snapshot isolation", "conflict filter", "validation", "rebase"], ["database-wide isolation", "job scheduling"], ["iceberg.table", "hudi.spec"], ["detect_table_conflict", "rebase_table_change", "refuse_conflicting_commit"]),
    ("analytical_table", "snapshot_refs", "Table Branches and Tags", "What mutable branches and immutable tags name snapshot histories with retention rules?", ["branch", "tag", "reference", "head snapshot", "reference retention"], ["source-code branch semantics", "catalog-wide branch"], ["iceberg.table", "nessie.concepts"], ["create_snapshot_ref", "advance_branch", "drop_snapshot_ref"]),
    ("analytical_table", "time_travel", "Table Time Travel", "How is an exact historical snapshot resolved by id, reference or time without confusing validity time?", ["as-of snapshot", "snapshot log", "commit timestamp", "historical cut"], ["business valid time", "backup restore"], ["iceberg.table", "delta.protocol", "hudi.spec"], ["resolve_historical_snapshot", "scan_historical_snapshot", "prove_historical_cut"]),
    ("analytical_table", "change_feed", "Table Change Feed", "What added, removed and changed rows/files occurred between exact table states?", ["start snapshot", "end snapshot", "change row", "change file", "before/after"], ["source CDC authority", "event notification delivery"], ["delta.protocol", "hudi.spec", "paimon.spec"], ["plan_incremental_scan", "read_change_feed", "checkpoint_change_consumer"]),
    ("analytical_table", "manifest_inventory", "Table Manifest and File Inventory", "How are files, partitions, bounds and sequence metadata indexed without directory listing?", ["manifest", "manifest list", "file entry", "partition summary", "sequence number"], ["object-store inventory", "catalog asset search"], ["iceberg.table", "hudi.metadata"], ["write_manifest", "scan_manifests", "rewrite_manifests"]),
    ("analytical_table", "table_statistics", "Table Statistics", "Which snapshot-scoped statistics may guide planning without becoming business facts?", ["snapshot statistics", "column statistics", "partition statistics", "NDV estimate", "histogram"], ["business measure", "query-plan choice"], ["iceberg.table", "parquet.format"], ["publish_table_statistics", "validate_statistics_cut", "invalidate_statistics"]),
    ("analytical_table", "multi_table_atomicity", "Multi-Table Atomicity", "Can a set of table-state changes become visible as one catalog transaction, and to which readers?", ["transaction set", "catalog commit", "read cut", "partial visibility"], ["distributed application saga", "cross-catalog atomicity"], ["iceberg.rest", "nessie.concepts"], ["prepare_multi_table_commit", "commit_table_set", "read_atomic_table_set"]),
    ("analytical_table", "table_format_migration", "Table Format Migration", "How is logical table state translated or rewritten across formats with explicit residual loss?", ["source format", "target format", "metadata translation", "feature loss", "dual publication"], ["physical data copy unless required", "provider migration"], ["xtable.interop", "xtable.limitations"], ["assess_format_compatibility", "translate_table_metadata", "verify_migrated_table"]),

    # Catalog and metadata authority
    ("catalog", "namespace", "Catalog Namespace", "Who creates, resolves, renames and drops catalogs, namespaces and asset names?", ["catalog", "namespace", "qualified name", "rename", "drop"], ["table internal identity", "enterprise ontology"], ["iceberg.rest", "unitycatalog.api", "hive.metastore"], ["create_namespace", "resolve_name", "rename_asset"]),
    ("catalog", "asset_registry", "Catalog Asset Registry", "Which tables, views, functions and volumes are registered with exact kind and edition?", ["asset", "asset kind", "registration", "edition", "property"], ["lineage graph", "business glossary ownership"], ["unitycatalog.api", "iceberg.view"], ["register_asset", "get_asset", "list_assets"]),
    ("catalog", "table_location", "Table Location Authority", "Who allocates, validates and transfers physical table locations without aliasing identities?", ["warehouse root", "table location", "managed location", "external location", "ownership transfer"], ["object placement policy", "table schema"], ["iceberg.rest", "unitycatalog.api"], ["allocate_table_location", "validate_external_location", "transfer_location"]),
    ("catalog", "commit_authority", "Catalog Commit Authority", "Which service atomically validates and publishes table metadata transitions?", ["base metadata", "requirement", "update", "commit", "conflict"], ["file writing", "query execution"], ["iceberg.rest", "unitycatalog.api"], ["load_for_commit", "commit_metadata_update", "record_commit_conflict"]),
    ("catalog", "credential_vending", "Storage Credential Vending", "What least-privilege, short-lived storage grant is issued for an exact operation and resource cut?", ["credential request", "scoped credential", "expiry", "storage action", "audit"], ["principal authentication", "business approval"], ["iceberg.rest", "unitycatalog.api"], ["request_storage_credential", "issue_scoped_credential", "revoke_credential"]),
    ("catalog", "managed_external", "Managed vs External Asset", "Which authority owns location allocation, lifecycle and cleanup for this asset?", ["managed asset", "external asset", "lifecycle owner", "drop behavior"], ["data-use policy", "source ownership"], ["unitycatalog.api", "iceberg.rest"], ["classify_asset_ownership", "adopt_external_asset", "drop_managed_asset"]),
    ("catalog", "metadata_cache", "Catalog Metadata Cache", "When may cached catalog state be served, refreshed or invalidated without stale commits?", ["cache entry", "etag", "expiry", "invalidation", "negative cache"], ["table data cache", "provider DNS cache"], ["iceberg.rest", "iceberg.table"], ["cache_catalog_entry", "revalidate_metadata", "invalidate_catalog_entry"]),
    ("catalog", "catalog_versioning", "Versioned Catalog", "How are catalog-wide commits, branches, tags and merges applied to multiple assets?", ["catalog commit", "branch", "tag", "merge", "reference log"], ["table-local branch", "source-code content"], ["nessie.concepts"], ["commit_catalog_change", "merge_catalog_branch", "tag_catalog_cut"]),
    ("catalog", "catalog_routing", "Multi-Catalog Routing", "How is a qualified reference deterministically routed across catalogs and trust boundaries?", ["catalog mount", "route", "priority", "fallback", "ambiguity"], ["query federation planning", "DNS"], ["trino.catalog", "iceberg.rest"], ["mount_catalog", "route_catalog_reference", "refuse_ambiguous_route"]),
    ("catalog", "schema_registry", "Data Schema Registry", "Which schema subject, edition and compatibility law govern encoded payload readers and writers?", ["subject", "schema edition", "compatibility mode", "registration", "fingerprint"], ["table schema evolution", "business ontology"], ["avro.spec", "iceberg.table"], ["register_schema", "check_schema_compatibility", "resolve_schema"]),
    ("catalog", "view_registry", "View Definition Registry", "How are versioned portable view representations, dependencies and dialects registered?", ["view id", "view version", "representation", "dialect", "dependency"], ["materialized result", "query execution"], ["iceberg.view", "unitycatalog.api"], ["create_view_version", "resolve_view_representation", "replace_view"]),
    ("catalog", "catalog_policy_binding", "Catalog Policy Binding", "Which external policy decisions constrain catalog operations without making the catalog the policy owner?", ["resource reference", "principal", "operation", "policy decision", "obligation"], ["policy language semantics", "identity proofing"], ["polaris.docs", "unitycatalog.api"], ["authorize_catalog_operation", "apply_catalog_obligation", "audit_catalog_decision"]),
    ("catalog", "catalog_events", "Catalog Change Events", "What ordered, replayable notification describes a committed metadata change without replacing catalog reads?", ["catalog event", "asset reference", "commit id", "sequence", "replay cursor"], ["source CDC", "business event"], ["nessie.concepts", "hudi.timeline"], ["emit_catalog_event", "subscribe_catalog_events", "replay_catalog_events"]),
    ("catalog", "catalog_migration", "Catalog Migration", "How are identities, locations, histories, grants and in-flight commits moved between catalog authorities?", ["source catalog", "target catalog", "identity map", "cutover", "rollback"], ["table format conversion", "data copy"], ["iceberg.rest", "polaris.docs", "nessie.concepts"], ["plan_catalog_migration", "migrate_catalog_metadata", "verify_catalog_cutover"]),
    ("catalog", "catalog_qualification", "Catalog Conformance Qualification", "Does an implementation satisfy the exact catalog protocol, commit, security and failure laws required?", ["protocol profile", "test suite", "conformance receipt", "unsupported operation"], ["market claim", "deployment SLO"], ["iceberg.rest", "polaris.docs", "unitycatalog.api"], ["probe_catalog_capability", "run_catalog_conformance", "issue_catalog_receipt"]),

    # Maintenance
    ("maintenance", "compaction", "File Compaction", "Which small or delta-bearing files may be combined without changing the logical snapshot?", ["compaction candidate", "rewrite group", "target file", "logical equivalence", "amplification"], ["table commit authority", "retention decision"], ["cassandra.storage", "hudi.spec", "druid.storage"], ["plan_compaction", "execute_compaction", "verify_compaction"]),
    ("maintenance", "clustering", "Physical Clustering", "How may rows/files be reorganized around access keys while preserving logical table meaning?", ["clustering key", "layout curve", "cluster extent", "overlap", "rewrite debt"], ["logical partitioning", "query optimizer"], ["delta.liquid", "clickhouse.mergetree"], ["plan_clustering", "cluster_data", "measure_clustering_quality"]),
    ("maintenance", "manifest_rewrite", "Manifest and Metadata Rewrite", "Which metadata files can be combined or repartitioned without changing referenced content?", ["manifest", "rewrite set", "metadata size", "planning latency"], ["data-file rewrite", "snapshot expiry"], ["iceberg.table", "hudi.metadata"], ["plan_manifest_rewrite", "rewrite_manifests", "verify_manifest_equivalence"]),
    ("maintenance", "delete_materialization", "Delete Materialization", "When are logical delete files/vectors safely applied to base files?", ["delete artifact", "base file", "purge rewrite", "reader compatibility", "debt"], ["privacy erasure authority", "physical media erase"], ["delta.deletion_vectors", "iceberg.v3", "hudi.spec"], ["plan_delete_materialization", "apply_deletes", "verify_deleted_rows"]),
    ("maintenance", "snapshot_expiry", "Snapshot Expiration", "Which historical snapshots may lose reachability under branch, tag, retention and legal-hold constraints?", ["snapshot age", "reference", "retention floor", "reachable file", "expiry candidate"], ["physical deletion", "business record retention"], ["iceberg.table", "xtable.limitations"], ["plan_snapshot_expiry", "expire_snapshots", "verify_reachability"]),
    ("maintenance", "orphan_cleanup", "Orphan File Cleanup", "Which unreferenced bytes are provably safe to delete after race and retention horizons?", ["orphan candidate", "reachability scan", "safety interval", "staged file", "cleanup receipt"], ["logical table deletion", "object lifecycle policy"], ["iceberg.table", "druid.storage"], ["discover_orphans", "authorize_orphan_delete", "delete_orphans"]),
    ("maintenance", "statistics_refresh", "Statistics Refresh", "When are table/file/index statistics stale, missing or unsafe and how are they recomputed?", ["statistics edition", "freshness", "coverage", "sample", "invalidation"], ["business metric", "query execution plan"], ["parquet.format", "iceberg.table"], ["plan_statistics_refresh", "compute_statistics", "publish_statistics"]),
    ("maintenance", "index_build", "Secondary Index Build", "How is an index built and atomically attached to an exact data cut?", ["index definition", "build cut", "index artifact", "coverage", "attach"], ["query predicate semantics", "source data mutation"], ["postgres.indexes", "lucene.index", "qdrant.storage"], ["plan_index_build", "build_index", "attach_index"]),
    ("maintenance", "tier_transition", "Tier Transition", "How are bytes migrated between storage tiers without violating availability, residency or integrity?", ["source tier", "target tier", "copy", "cutover", "recallability"], ["logical table change", "business archival policy"], ["druid.deep", "s3.versioning"], ["plan_tier_transition", "copy_to_tier", "cutover_tier"]),
    ("maintenance", "replica_repair", "Replica Repair and Scrubbing", "How are divergent or corrupted replicas identified, repaired and re-qualified?", ["replica digest", "divergence", "repair source", "scrub", "qualification"], ["logical conflict resolution", "backup restore"], ["cassandra.overview", "ceph.rados"], ["compare_replicas", "repair_replica_cut", "qualify_repaired_replica"]),
    ("maintenance", "vacuum_reclamation", "Vacuum and Space Reclamation", "When may dead versions/pages/segments be reclaimed without violating active readers or recovery?", ["dead version", "reader horizon", "vacuum", "free space", "freeze"], ["business deletion approval", "snapshot retention"], ["postgres.backup", "rocksdb.overview"], ["compute_safe_horizon", "vacuum_storage", "verify_reader_safety"]),
    ("maintenance", "maintenance_coordination", "Maintenance Coordination", "How are destructive or intensive maintenance actions scheduled, cancelled and isolated from foreground SLOs?", ["maintenance plan", "lease", "interference budget", "cancellation", "resume token"], ["compute scheduler internals", "business priority"], ["hudi.timeline", "druid.storage"], ["schedule_maintenance", "pause_maintenance", "resume_maintenance"]),
    ("maintenance", "layout_observability", "Physical Layout Observability", "What evidence quantifies file counts, overlap, skew, amplification, cache locality and maintenance debt?", ["layout measurement", "overlap", "skew", "read amplification", "write amplification", "debt"], ["query correctness", "business KPI"], ["cassandra.storage", "druid.storage", "parquet.format"], ["measure_layout", "detect_layout_debt", "explain_layout_cost"]),

    # Serving
    ("serving", "materialized_view", "Materialized View", "What query result cut is durably stored, refreshed and exposed under a named view identity?", ["view definition", "materialized cut", "refresh", "staleness", "dependency"], ["source-table authority", "business metric ownership"], ["postgres.matview", "materialize.views"], ["create_materialization", "refresh_materialization", "query_materialization"]),
    ("serving", "incremental_materialization", "Incremental Materialization", "How are source changes propagated into a result while preserving retraction and consistency semantics?", ["differential update", "frontier", "retraction", "maintained result", "hydration"], ["source CDC capture", "query language definition"], ["materialize.views", "timescale.aggregate"], ["apply_incremental_change", "advance_materialization_frontier", "rebuild_materialization"]),
    ("serving", "result_cache", "Query Result Cache", "When may a prior result be reused for an equivalent request and exact dependency cut?", ["cache key", "normalized request", "dependency cut", "expiry", "invalidation"], ["semantic-query equivalence", "source authority"], ["redis.persistence", "materialize.views"], ["cache_query_result", "lookup_cached_result", "invalidate_result_cache"]),
    ("serving", "cache_fill_coordination", "Cache Fill Coordination", "How are equivalent concurrent cache misses joined to one fenced fill generation without sharing an ineligible result, inferring completion, leaking authority or creating a retry storm?", ["fill equivalence key", "fill generation", "leader lease", "fencing token", "waiter registration", "fill attempt", "shared outcome", "stale-serve decision", "coordination receipt"], ["request equivalence ownership", "cache storage", "source execution", "source truth", "authorization policy"], ["rfc9111.cache", "rfc5861.stale", "go.singleflight", "redis.stampede"], ["admit_or_join_fill", "publish_fill_outcome", "detach_waiter", "serve_stale_under_policy", "expire_or_supersede_fill", "reconcile_abandoned_fill"]),
    ("serving", "warehouse_serving", "Warehouse Serving", "How are concurrent analytical workloads admitted, isolated and served over durable warehouse state?", ["workload class", "queue", "resource group", "result cut", "spill"], ["business priority authority", "table format ownership"], ["clickhouse.mergetree", "postgres.partitioning"], ["admit_warehouse_query", "serve_warehouse_query", "cancel_warehouse_query"]),
    ("serving", "olap_serving", "OLAP Segment Serving", "Which segment versions are loaded, routed and combined into a complete low-latency result cut?", ["segment timeline", "load rule", "replica", "broker route", "partial result"], ["segment construction", "business aggregation meaning"], ["druid.storage", "pinot.segment"], ["assign_segment", "route_segment_query", "detect_partial_result"]),
    ("serving", "time_series_serving", "Time-Series Serving", "How are raw, downsampled and real-time tails combined without double count or freshness ambiguity?", ["raw tier", "aggregate tier", "invalidation", "real-time tail", "time bucket"], ["metric definition", "event-time authority"], ["timescale.aggregate", "influx.storage"], ["select_time_series_tier", "combine_realtime_tail", "serve_time_range"]),
    ("serving", "search_serving", "Search Serving", "Which refreshed index cut, analyzer edition and shard set answer a search request?", ["search cut", "analyzer edition", "shard", "replica", "score"], ["source-document truth", "ranking business policy"], ["opensearch.index", "lucene.index"], ["route_search_request", "merge_search_results", "report_search_cut"]),
    ("serving", "search_visibility", "Search Visibility Cut and Publication", "Which per-shard mutation frontier, reader/searcher snapshot and publication occurrence prove that an index mutation set is searchable, partially searchable, still invisible or unknown without confusing visibility with durability?", ["visibility request", "mutation frontier", "shard visibility cut", "reader snapshot", "publication attempt", "visibility receipt", "partial visibility", "visibility residual"], ["source-document truth", "index mutation authority", "query/ranking semantics", "durability promise", "cache invalidation"], ["lucene.point_in_time", "elastic.refresh", "elastic.translog", "solr.commits"], ["request_visibility_publication", "publish_search_visibility", "wait_for_mutation_visibility", "observe_search_visibility_cut", "compare_visibility_cuts", "reconcile_visibility_timeout", "verify_delete_disappearance"]),
    ("serving", "vector_serving", "Vector Similarity Serving", "Which vector/index cut, distance and approximation budget produced nearest-neighbor results?", ["vector index cut", "distance", "top-k", "filter", "recall estimate"], ["embedding generation", "LLM/RAG semantics", "business ranking"], ["qdrant.storage", "milvus.consistency"], ["route_vector_search", "search_vector_index", "report_approximation"]),
    ("serving", "graph_serving", "Graph Serving", "Which graph transaction cut and consistency token bound a traversal or pattern query?", ["graph cut", "bookmark", "traversal", "path", "partial result"], ["graph model ownership", "graph analytics jobs"], ["neo4j.clustering", "rdf.sparql"], ["route_graph_query", "serve_graph_traversal", "report_graph_cut"]),
    ("serving", "cache_serving", "Keyed Cache Serving", "What hit, miss, stale and eviction states are observable to callers?", ["cache hit", "cache miss", "stale hit", "TTL", "eviction"], ["source read", "business fallback"], ["redis.persistence", "redis.replication"], ["serve_cache_lookup", "refresh_cache_entry", "report_cache_state"]),
    ("serving", "serving_cutover", "Serving Cutover and Rollback", "How does traffic move between materialization/index editions without mixed or partial visibility?", ["serving edition", "candidate", "active", "traffic split", "rollback"], ["data rebuild", "application release"], ["materialize.views", "druid.storage"], ["stage_serving_edition", "cutover_serving_traffic", "rollback_serving_edition"]),
    ("serving", "freshness_contract", "Serving Freshness Contract", "How are source progress, materialization frontier, publication time and tolerated staleness related?", ["source frontier", "materialization frontier", "freshness lag", "staleness budget", "unknown"], ["source event-time completeness", "query latency"], ["materialize.views", "timescale.aggregate"], ["measure_freshness", "enforce_staleness_budget", "degrade_stale_service"]),
    ("serving", "bulk_result_delivery", "Bulk Result Delivery", "How are a large result's schema, partitions, ordering, checksums and resumability exposed?", ["result manifest", "partition", "schema", "checksum", "resume token", "expiry"], ["query computation", "consumer ingestion"], ["arrow.flight", "arrow.adbc"], ["publish_result_manifest", "download_result_partition", "resume_result_delivery"]),

    # Sharing and federation
    ("sharing_federation", "share_publication", "Data Share Publication", "Which exact asset cut is published to which recipient population under what purpose and expiry?", ["share", "listing", "recipient", "shared table", "published cut", "expiry"], ["source table ownership", "identity proofing"], ["delta.sharing"], ["create_share", "publish_table_cut", "revoke_share"]),
    ("sharing_federation", "share_subscription", "Data Share Subscription", "How does a recipient accept, discover, checkpoint and stop consuming a share?", ["subscription", "recipient profile", "listing", "checkpoint", "termination"], ["provider publication authority", "consumer business use"], ["delta.sharing"], ["subscribe_share", "list_shared_assets", "checkpoint_shared_changes"]),
    ("sharing_federation", "presigned_delivery", "Delegated Object Delivery", "What short-lived URL or directory credential grants only the shared bytes for a bounded interval?", ["presigned URL", "temporary credential", "file id", "expiry", "download audit"], ["long-lived storage credential", "share policy decision"], ["delta.sharing", "iceberg.rest"], ["issue_presigned_access", "download_shared_file", "expire_delivery_grant"]),
    ("sharing_federation", "cross_engine_table_access", "Cross-Engine Table Access", "Can multiple engines read/write the same table feature set without semantic drift?", ["engine profile", "reader feature", "writer feature", "conformance", "interoperability"], ["engine query dialect", "deployment performance"], ["iceberg.table", "delta.protocol", "hudi.spec"], ["qualify_table_reader", "qualify_table_writer", "refuse_incompatible_engine"]),
    ("sharing_federation", "metadata_translation", "Table Metadata Translation", "Which source-format states can be represented in a target format with explicit loss and lag?", ["source commit", "target metadata", "translation checkpoint", "feature loss", "lag"], ["data-file conversion", "multi-writer ownership"], ["xtable.interop", "xtable.limitations"], ["translate_metadata_commit", "reconcile_format_views", "report_translation_loss"]),
    ("sharing_federation", "federated_namespace", "Federated Namespace", "How are remote catalogs and objects mounted without name, identity or authority confusion?", ["foreign server", "mount", "remote object", "local alias", "identity mapping"], ["remote query execution", "business glossary"], ["postgres.fdw", "trino.catalog"], ["mount_foreign_namespace", "resolve_foreign_object", "unmount_namespace"]),
    ("sharing_federation", "virtual_relation_identity", "Virtual Relation Identity and Definition", "What makes a governed virtual relation and its immutable edition the same object despite rename, provider, source path, language carrier or materialization changes?", ["virtual relation id", "relation edition", "qualified alias", "definition carrier", "output schema", "source binding set", "security execution profile", "definition digest", "dependency contract"], ["source relation truth", "query execution", "catalog namespace ownership", "materialization storage", "business semantic model"], ["postgres.create_view", "trino.create_view", "postgres.fdw"], ["construct_virtual_relation", "bind_virtual_sources", "validate_virtual_relation_definition", "compare_virtual_relation_editions", "project_virtual_relation_definition"]),
    ("sharing_federation", "virtual_relation_lifecycle", "Virtual Relation Publication Lifecycle", "Which authority may publish, supersede, deprecate, recall or retire one immutable virtual-relation edition while preserving dependencies and in-flight invocation evidence?", ["virtual relation draft", "publication decision", "published edition", "alias head", "supersession", "deprecation", "recall", "retirement", "dependency impact", "lifecycle receipt"], ["definition semantics", "query attempt lifecycle", "source retirement authority", "consumer migration execution", "materialization refresh"], ["postgres.create_view", "trino.create_view", "trino.alter_view"], ["create_virtual_relation_draft", "publish_virtual_relation_edition", "supersede_virtual_relation_edition", "deprecate_virtual_relation", "recall_virtual_relation_edition", "retire_virtual_relation"]),
    ("sharing_federation", "pushdown", "Federated Operation Pushdown", "Which typed operations may execute remotely with proven semantic equivalence?", ["pushdown candidate", "remote capability", "residual expression", "semantic equivalence", "cost"], ["query optimizer policy", "remote storage internals"], ["postgres.fdw", "substrait.serialization"], ["negotiate_pushdown", "execute_remote_operation", "verify_pushdown_result"]),
    ("sharing_federation", "federated_consistency", "Federated Read Consistency", "What cut relationship exists among independently committed remote sources in one result?", ["source cut", "snapshot token", "skew", "repeatability", "inconsistency declaration"], ["global transaction unless supplied", "business reconciliation"], ["postgres.fdw", "trino.catalog"], ["acquire_source_cuts", "execute_federated_read", "report_cross_source_skew"]),
    ("sharing_federation", "query_protocol", "Database Query Protocol", "How are session, statement, transaction, metadata and cancellation represented across a provider boundary?", ["session", "statement", "transaction", "result set", "cancellation"], ["query language semantics", "storage format"], ["arrow.flight_sql", "arrow.adbc"], ["open_database_session", "execute_statement", "cancel_statement"]),
    ("sharing_federation", "data_portability", "Data Portability and Exit", "Which tables, metadata, grants, histories and evidence can be exported and independently rehydrated?", ["export manifest", "portable format", "identity map", "history", "verification"], ["supplier contract law", "application migration"], ["iceberg.table", "delta.sharing", "arrow.adbc"], ["plan_portable_export", "export_portable_cut", "verify_independent_import"]),
]


def context_id(slug: str) -> str:
    return f"persistence.context.{slug}"


DECISION_SEEDS = [
    # slug, owner context slug, question, allowed values, phase
    ("block_ack", "block_device", "When is a block write acknowledged durable?", ["volatile_cache", "flush_completed", "fua_completed", "provider_proven"], "deployment_binding"),
    ("file_sync", "local_filesystem", "Which file and directory synchronization sequence is required?", ["none", "file_only", "file_then_parent_directory", "provider_proven"], "physical_binding"),
    ("network_lock_recovery", "network_filesystem", "How are remote locks and sessions recovered after partition?", ["lease_reclaim", "session_recreate", "fail_closed", "read_only_degradation"], "runtime_reconciliation"),
    ("object_identity", "object_namespace", "What identifies an immutable object cut?", ["key_only", "key_and_version", "key_and_etag", "content_digest"], "semantic_closure"),
    ("object_conditional", "object_namespace", "Which conditional-write primitive protects updates?", ["if_none_match", "if_match_etag", "version_precondition", "external_commit_authority"], "physical_binding"),
    ("listing_law", "object_namespace", "What listing consistency and pagination law is required?", ["strong_cut", "strong_per_page", "eventual", "inventory_snapshot"], "physical_binding"),
    ("integrity_digest", "integrity", "Which integrity algorithm and scope are required?", ["crc32c_transport", "crc64_transport", "sha256_content", "format_checksum", "multiple_scopes"], "physical_binding"),
    ("encryption_scope", "encryption", "Which storage modules must be encrypted?", ["whole_object", "footer_and_columns", "selected_columns", "metadata_only", "provider_envelope"], "assurance_insertion"),
    ("key_rotation", "encryption", "How is encryption-key rotation performed?", ["rewrap_data_key", "rewrite_ciphertext", "lazy_on_access", "new_writes_only"], "deployment_binding"),
    ("replication_ack", "replication", "Which replicas/failure domains must acknowledge a write?", ["one", "quorum", "all_sync", "local_quorum_remote_async", "provider_proven"], "deployment_binding"),
    ("durability_scheme", "erasure_durability", "Which replication or erasure profile meets the fault model?", ["replicated", "erasure_coded", "hybrid", "external_provider"], "physical_binding"),
    ("placement", "tiering", "What placement dimensions constrain stored bytes?", ["region", "zone", "rack", "device_class", "residency_zone", "multi_constraint"], "deployment_binding"),
    ("tier_transition", "tiering", "What triggers storage-tier transitions?", ["age", "last_access", "declared_temperature", "budget_pressure", "manual_authority"], "runtime_reconciliation"),
    ("retention_mode", "retention_immutability", "What prevents deletion before expiry?", ["governance_worm", "compliance_worm", "legal_hold", "logical_policy_only", "external_archive"], "assurance_insertion"),
    ("quota_enforcement", "quota_cost", "When is finite storage reserved and enforced?", ["precharge", "admission_estimate", "soft_limit", "post_meter_only"], "deployment_binding"),
    ("backup_mode", "backup", "Which backup chain represents recoverable state?", ["full", "full_plus_incremental", "continuous_log", "storage_snapshot_plus_log", "logical_export"], "deployment_binding"),
    ("restore_target", "restore", "How is a restore target selected?", ["latest", "timestamp", "log_position", "transaction_id", "named_backup_cut"], "runtime_reconciliation"),
    ("rpo_reference", "recovery_objectives", "Which disruption/source reference establishes the recovery-point comparison?", ["last_authoritative_source_cut_before_disruption", "incident_authority_named_cut", "transaction_or_log_position", "domain_specific_ordered_cut"], "evidence_verification"),
    ("rto_start", "recovery_objectives", "Which occurrence starts the measured recovery interval?", ["incident_authority_declared_disruption", "service_unavailability_observed", "recovery_authority_activation", "domain_specific_named_occurrence"], "evidence_verification"),
    ("rto_end", "recovery_objectives", "Which accepted occurrence ends the measured recovery interval?", ["all_required_services_accepted", "minimum_service_profile_accepted", "dependency_graph_ready_and_accepted", "domain_specific_named_acceptance"], "evidence_verification"),
    ("recovery_measurement_partiality", "recovery_objectives", "How are missing dependencies, clocks, cuts or acceptance evidence handled?", ["refuse_attainment_claim", "emit_inconclusive_with_residuals", "measure_covered_subset_without_scope_claim", "authority_approved_narrower_scope_edition"], "evidence_verification"),
    ("recovery_clock", "recovery_objectives", "Which clock and uncertainty contract governs elapsed recovery measurement?", ["monotonic_clock_with_wall_correlation", "trusted_distributed_time_with_bound", "externally_attested_timestamps", "domain_specific_order_with_duration_evidence"], "evidence_verification"),
    ("delete_evidence", "physical_deletion", "What evidence is required before irreversible reclamation?", ["reachability_proof", "retention_clearance", "maker_checker", "cryptographic_erasure", "all_required"], "evidence_verification"),
    ("transaction_isolation", "relational_store", "Which transaction isolation level is required?", ["read_committed", "repeatable_read", "snapshot_isolation", "serializable", "provider_declared"], "semantic_closure"),
    ("document_atomicity", "document_store", "What is the maximum atomic document mutation scope?", ["single_document", "single_partition", "multi_document", "cross_shard"], "physical_binding"),
    ("kv_ordering", "key_value_store", "Which key ordering contract is required?", ["byte_lexicographic", "custom_comparator", "hash_only", "unordered"], "semantic_closure"),
    ("wide_consistency", "wide_column_store", "Which per-operation consistency profile is required?", ["one", "local_quorum", "quorum", "all", "serial_lwt"], "physical_binding"),
    ("graph_consistency", "property_graph_store", "Which graph read consistency is required?", ["read_committed", "causal_bookmark", "snapshot", "serializable"], "physical_binding"),
    ("series_lateness", "time_series_store", "How are late and corrected samples persisted?", ["reject_after_horizon", "upsert_by_series_time", "append_revision", "retract_and_replace"], "semantic_closure"),
    ("search_refresh", "search_store", "What refresh visibility contract is required?", ["on_commit", "bounded_interval", "manual", "eventual_unbounded"], "deployment_binding"),
    ("vector_approximation", "vector_store", "Which approximation and recall contract governs similarity search?", ["exact", "minimum_recall_measured", "latency_bounded_best_effort", "provider_declared"], "analytical_design"),
    ("cache_staleness", "cache_store", "What stale-value policy applies?", ["never_serve_stale", "stale_while_revalidate", "bounded_stale", "caller_selects"], "semantic_closure"),
    ("journal_expected_version", "event_journal", "How are concurrent event appends guarded?", ["expected_exact", "expected_any", "idempotency_key", "single_writer_lease"], "semantic_closure"),
    ("array_chunk_grid", "scientific_array_store", "How is an array divided into chunks?", ["regular_grid", "rectilinear_grid", "sharded_grid", "extension_defined"], "logical_planning"),
    ("stream_checkpoint", "stream_state_store", "Which state/input cut is atomically checkpointed?", ["aligned_checkpoint", "unaligned_checkpoint", "savepoint", "provider_snapshot"], "deployment_binding"),
    ("warehouse_workload", "analytical_warehouse", "How are analytical workloads isolated?", ["dedicated_cluster", "resource_group", "queue_priority", "serverless_budget", "external_compute"], "deployment_binding"),
    ("file_format", "columnar_file", "Which analytical file format and edition are emitted?", ["parquet", "orc", "arrow_ipc", "provider_native"], "physical_binding"),
    ("row_group_size", "columnar_file", "What row-group or stripe sizing law applies?", ["fixed_bytes", "fixed_rows", "adaptive_by_column", "provider_optimized_with_receipt"], "physical_binding"),
    ("logical_type_mapping", "logical_types", "How are unsupported logical values represented?", ["refuse", "lossless_extension", "approved_lossy_cast", "opaque_binary"], "semantic_closure"),
    ("encoding_choice", "encoding", "How is a value encoding chosen?", ["schema_fixed", "column_profiled", "page_adaptive", "provider_selected_with_receipt"], "physical_binding"),
    ("compression_codec", "compression", "Which compression codec profile applies?", ["none", "lz4", "snappy", "zstd", "gzip", "brotli", "format_default", "provider_profile"] , "physical_binding"),
    ("compression_level", "compression", "How is compression effort bounded?", ["fixed_level", "latency_budget", "cpu_budget", "ratio_target", "adaptive_with_receipt"], "physical_binding"),
    ("compression_unit", "compression", "At which unit is compression independently decodable?", ["page", "column_chunk", "stripe", "chunk", "shard", "whole_object"] , "logical_planning"),
    ("file_encryption_keys", "modular_encryption", "How are encryption keys scoped?", ["file_key", "footer_plus_column_keys", "per_column_key", "tenant_key", "provider_kms_policy"] , "assurance_insertion"),
    ("statistics_privacy", "file_statistics", "May pruning statistics reveal value bounds?", ["plaintext", "encrypted", "redacted", "suppressed"] , "assurance_insertion"),
    ("bloom_fpp", "probabilistic_index", "What maximum Bloom-filter false-positive probability is accepted?", ["declared_numeric", "size_budget_derived", "provider_measured", "disabled"] , "logical_planning"),
    ("target_file_shape", "fragmentation", "What target file shape balances metadata and parallelism?", ["fixed_target_bytes", "rows_and_bytes", "workload_adaptive", "provider_receipt"] , "physical_binding"),
    ("transport_resume", "columnar_transport", "How are interrupted result streams resumed?", ["restart_query", "partition_retry", "ticket_resume", "not_resumable"] , "deployment_binding"),
    ("field_identity", "schema_evolution", "What makes a field the same across rename/reorder?", ["stable_numeric_id", "stable_name", "path", "external_schema_id"] , "semantic_closure"),
    ("schema_compatibility", "schema_evolution", "Which schema evolution relation is allowed?", ["backward", "forward", "full", "exact", "operation_specific"] , "semantic_closure"),
    ("partition_transform", "partition_evolution", "Which partition transform family is permitted?", ["identity", "bucket", "truncate", "year_month_day_hour", "custom_versioned"] , "logical_planning"),
    ("mutation_model", "row_level_mutation", "How are row-level changes physically represented?", ["copy_on_write", "position_delete", "equality_delete", "deletion_vector", "log_merge", "primary_key_merge"] , "physical_binding"),
    ("table_commit_authority", "commit_protocol", "Who performs the authoritative metadata compare-and-swap?", ["catalog_service", "filesystem_atomic_rename", "object_conditional_write", "external_lock_manager"] , "physical_binding"),
    ("table_isolation", "isolation_conflicts", "Which table mutation isolation profile applies?", ["serializable", "snapshot", "write_serializable", "append_only_concurrent"] , "semantic_closure"),
    ("commit_retry", "commit_protocol", "How may a failed table commit be retried?", ["same_idempotency_key", "rebase_and_validate", "restart_operation", "never_automatic"] , "runtime_reconciliation"),
    ("snapshot_retention", "snapshot_refs", "How many or how long are unreferenced snapshots retained?", ["minimum_count", "minimum_age", "branch_policy", "legal_hold_overrides", "explicit_only"] , "assurance_insertion"),
    ("time_travel_resolution", "time_travel", "How is timestamp-as-of resolved around equal or missing commit times?", ["latest_not_after", "earliest_not_before", "exact_only", "snapshot_id_required"] , "semantic_closure"),
    ("change_feed_mode", "change_feed", "Which change representation is required?", ["file_add_remove", "row_before_after", "row_after_only", "delete_keys", "snapshot_diff"] , "analytical_design"),
    ("multi_table_visibility", "multi_table_atomicity", "Which readers observe a multi-table atomic commit?", ["catalog_aware_only", "all_conforming_clients", "branch_pointer_readers", "unsupported"] , "physical_binding"),
    ("format_migration", "table_format_migration", "How is source-to-target format transition operated?", ["metadata_translation", "dual_write", "full_rewrite", "copy_then_cutover"] , "deployment_binding"),
    ("catalog_protocol", "catalog_qualification", "Which catalog protocol profile must be implemented?", ["iceberg_rest", "hive_metastore", "unity_openapi", "provider_adapter"] , "physical_binding"),
    ("managed_external", "managed_external", "Who owns physical lifecycle after catalog drop?", ["catalog_managed", "external_owner", "shared_authority", "refuse_ambiguous"] , "semantic_closure"),
    ("credential_mode", "credential_vending", "How is storage access delegated?", ["presigned_url", "temporary_directory_credential", "remote_signing", "catalog_proxy", "preconfigured_identity"] , "assurance_insertion"),
    ("metadata_cache_ttl", "metadata_cache", "How is catalog-cache staleness bounded?", ["event_invalidation", "etag_revalidation", "fixed_ttl", "no_cache"] , "deployment_binding"),
    ("catalog_branching", "catalog_versioning", "Are namespace/table changes versioned on catalog branches?", ["none", "catalog_wide_branch", "table_local_refs_only", "provider_defined"] , "semantic_closure"),
    ("catalog_route_conflict", "catalog_routing", "How are duplicate qualified routes handled?", ["refuse", "explicit_mount_priority", "fully_qualified_only", "authority_selected"] , "intent_resolution"),
    ("compaction_trigger", "compaction", "What triggers file compaction?", ["file_count", "size_distribution", "read_amplification", "delete_debt", "budget_window", "manual"] , "runtime_reconciliation"),
    ("clustering_strategy", "clustering", "Which physical clustering strategy applies?", ["sort_keys", "z_order", "hilbert", "range_overlap_reduction", "provider_algorithm"] , "physical_binding"),
    ("delete_purge", "delete_materialization", "When must logical deletes be materialized?", ["read_debt_threshold", "retention_expiry", "privacy_deadline", "manual", "never_before_export"] , "runtime_reconciliation"),
    ("orphan_horizon", "orphan_cleanup", "How long must an unreferenced file wait before deletion?", ["longer_than_max_commit", "catalog_lease_horizon", "fixed_duration", "manual_proof"] , "assurance_insertion"),
    ("index_type", "index_build", "Which index structure satisfies the access contract?", ["btree", "hash", "bitmap", "inverted", "brin", "bloom", "hnsw", "ivf", "provider_extension"] , "physical_binding"),
    ("maintenance_interference", "maintenance_coordination", "How much foreground interference may maintenance consume?", ["reserved_budget", "opportunistic", "maintenance_window", "preemptible", "isolated_resources"] , "deployment_binding"),
    ("materialization_refresh", "materialized_view", "How is a materialized view refreshed?", ["full_manual", "full_scheduled", "incremental", "continuous", "on_demand"] , "physical_binding"),
    ("materialization_consistency", "incremental_materialization", "Which source cut does a materialized result represent?", ["single_source_frontier", "transactional_multi_source", "per_source_frontiers", "best_effort_declared"] , "semantic_closure"),
    ("result_cache_key", "result_cache", "What proves two requests may share a cached result?", ["byte_identical_query", "normalized_logical_plan", "semantic_query_identity", "explicit_cache_key"] , "semantic_closure"),
    ("index_mutation_order", "index_mutation", "What is the validity scope of a mutation order token?", ["writer_epoch_and_sequence", "primary_term_and_sequence", "partition_epoch_and_offset", "provider_neutral_partial_order"], "runtime_reconciliation"),
    ("index_mutation_precondition", "index_mutation", "Which expected state prevents a stale mutation from overwriting a newer one?", ["expected_source_revision", "expected_index_head", "expected_primary_epoch_and_sequence", "create_only_or_absent"], "runtime_reconciliation"),
    ("index_mutation_ack", "index_mutation", "What exact fact does a successful mutation acknowledgement establish?", ["admitted_buffered", "journal_fsynced", "stable_commit_recorded", "declared_replica_set_acknowledged"], "evidence_verification"),
    ("index_mutation_batch", "index_mutation", "What atomicity relation is promised among mutations in a batch?", ["per_document_only", "all_or_none_single_writer", "ordered_partial_with_residual", "provider_profile_with_conformance_proof"], "semantic_closure"),
    ("index_mutation_idempotency", "index_mutation", "How is a retried mutation distinguished from a new mutation?", ["caller_idempotency_key", "content_addressed_mutation_id", "source_revision_and_operation_key", "reconcile_before_new_attempt"], "runtime_reconciliation"),
    ("index_mutation_unknown", "index_mutation", "What happens when provider completion is unknown?", ["reconcile_by_mutation_id", "reconcile_by_order_token", "block_retry_until_epoch_change", "authority_selected_compensation"], "runtime_reconciliation"),
    ("index_delete_semantics", "index_mutation", "How is deletion represented before verified disappearance?", ["editioned_tombstone", "delete_by_stable_document_id", "delete_by_preconditioned_query", "rebuild_without_subject_then_cutover"], "semantic_closure"),
    ("index_replica_ack", "index_mutation", "Which shard and replica scope participates in acknowledgement?", ["primary_only", "declared_active_replicas", "quorum_failure_domains", "provider_profile_with_partial_receipt"], "deployment_binding"),
    ("fill_leadership", "cache_fill_coordination", "How is one fill leader admitted and fenced for an equivalence key and generation?", ["single_process_generation", "fenced_distributed_lease", "partition_owner_generation", "provider_neutral_coordinator_port"], "runtime_reconciliation"),
    ("fill_follower", "cache_fill_coordination", "What may an equivalent follower do while a fill is active?", ["wait_until_deadline", "serve_eligible_stale", "explicit_bypass_new_execution", "refuse_over_budget"], "runtime_reconciliation"),
    ("fill_cancellation", "cache_fill_coordination", "How does caller cancellation affect shared fill work?", ["detach_waiter_only", "cancel_when_last_waiter_leaves", "never_cancel_shared_fill", "authority_selected_deadline_bound"], "runtime_reconciliation"),
    ("fill_failure", "cache_fill_coordination", "How is leader failure observed and how may another generation begin?", ["share_exact_failure_receipt", "eligible_stale_then_backoff", "new_generation_after_closed_receipt", "refuse_until_reconciled"], "runtime_reconciliation"),
    ("fill_late_completion", "cache_fill_coordination", "What happens when an expired or superseded leader completes late?", ["reject_by_fencing_token", "validate_then_publish_to_new_generation", "retain_evidence_without_publish", "authority_selected_compensation"], "runtime_reconciliation"),
    ("fill_capacity", "cache_fill_coordination", "Which finite budgets bound keys, leaders, waiters and coordination time?", ["fixed_per_key_and_tenant", "weighted_by_fill_cost", "global_plus_partition_budget", "caller_declared_with_hard_ceiling"], "deployment_binding"),
    ("serving_partial", "olap_serving", "May a result omit unavailable segments?", ["never", "typed_partial_with_coverage", "caller_selects", "best_effort"] , "semantic_closure"),
    ("serving_freshness", "freshness_contract", "What maximum publication lag is permitted?", ["declared_duration", "source_frontier_bound", "eventual", "caller_selects"] , "analytical_design"),
    ("search_visibility_publication", "search_visibility", "How is a new searchable reader or searcher publication requested?", ["periodic_refresh", "explicit_refresh", "wait_for_refresh", "open_reader_if_changed"], "runtime_reconciliation"),
    ("search_visibility_cut", "search_visibility", "How is a distributed searchable cut represented?", ["per_shard_frontier_vector", "single_writer_reader_snapshot", "replica_qualified_frontier", "provider_token_with_explicit_residual"], "semantic_closure"),
    ("search_visibility_partiality", "search_visibility", "How is missing shard or replica visibility handled?", ["refuse_complete_claim", "typed_partial_with_coverage", "wait_until_deadline", "degraded_profile_with_residual"], "semantic_closure"),
    ("search_visibility_wait", "search_visibility", "What does a read-after-write waiter require before returning?", ["exact_mutation_frontier_visible", "same_document_mutation_visible", "all_target_shards_visible", "deadline_then_unknown_receipt"], "runtime_reconciliation"),
    ("search_visibility_durability", "search_visibility", "What relation between search visibility and durable commit may be claimed?", ["visibility_only_no_durability_claim", "durable_commit_only_not_current_searcher", "both_with_separate_receipts", "provider_profile_with_conformance_proof"], "evidence_verification"),
    ("search_delete_disappearance", "search_visibility", "What proves a deleted document is no longer searchable?", ["all_target_shard_frontiers_beyond_delete", "all_retained_reader_snapshots_expired", "rebuild_and_atomic_cutover_receipt", "typed_residual_for_cache_or_replica"], "evidence_verification"),
    ("search_visibility_capacity", "search_visibility", "Which finite bounds govern refresh listeners, publication frequency and retained readers?", ["fixed_per_index", "weighted_by_shards_and_waiters", "global_plus_tenant_budget", "provider_limit_with_hard_local_ceiling"], "deployment_binding"),
    ("share_access", "presigned_delivery", "Which shared-data access mode is used?", ["url_per_file", "temporary_directory_credentials", "service_stream", "recipient_copy"] , "deployment_binding"),
    ("share_revocation", "share_publication", "What happens to already downloaded bytes after revocation?", ["future_access_only", "consumer_delete_obligation", "cryptographic_expiry", "recall_workflow"] , "assurance_insertion"),
    ("translation_authority", "metadata_translation", "Which table format remains authoritative during metadata translation?", ["single_source_format", "catalog_canonical_model", "scheduled_authority_switch", "refuse_multi_writer"] , "semantic_closure"),
    ("pushdown_semantics", "pushdown", "How is remote-operation semantic equivalence proven?", ["standard_profile", "provider_conformance", "result_differential_test", "no_pushdown"] , "evidence_verification"),
    ("federated_cut", "federated_consistency", "How are cuts acquired across independent sources?", ["no_common_cut_declared", "timestamp_best_effort", "coordinated_snapshot", "source_specific_tokens"] , "logical_planning"),
    ("database_api", "query_protocol", "Which provider-neutral database access API/protocol is required?", ["adbc", "flight_sql", "jdbc", "odbc", "native_adapter"] , "physical_binding"),
    ("virtual_definition_carrier", "virtual_relation_identity", "Which exact carrier defines a virtual relation edition?", ["canonical_logical_plan", "editioned_sql_text_and_language", "provider_ast_with_acl", "standard_plan_plus_extension_set"], "semantic_closure"),
    ("virtual_source_binding", "virtual_relation_identity", "How are source relation identities and editions resolved?", ["fully_pinned_source_editions", "validity_cut_resolved_at_invocation", "version_range_with_compatibility_proof", "mixed_explicit_binding_profile"], "semantic_closure"),
    ("virtual_output_compatibility", "virtual_relation_identity", "Which output-schema relation may preserve a public virtual-relation alias?", ["exact_only", "backward_additive", "declared_compatibility_profile", "new_alias_required"], "semantic_closure"),
    ("virtual_security_mode", "virtual_relation_identity", "Under whose authority are source accesses evaluated?", ["invoker", "definer_with_delegation", "external_policy_decision", "per_source_explicit_profile"], "assurance_insertion"),
    ("virtual_parameter_binding", "virtual_relation_identity", "How are parameters and session-dependent values represented?", ["forbidden_closed_relation", "typed_explicit_parameters", "bound_session_profile", "invocation_context_with_receipt"], "semantic_closure"),
    ("virtual_publish_authority", "virtual_relation_lifecycle", "Who may publish or advance the public alias to an immutable edition?", ["single_owner", "maker_checker", "delegated_steward", "external_governance_receipt"], "assurance_insertion"),
    ("virtual_dependency_break", "virtual_relation_lifecycle", "How is a breaking source/output/security dependency change handled?", ["refuse_publication", "publish_new_major_alias", "parallel_edition_with_migration", "authority_approved_typed_break"], "runtime_reconciliation"),
    ("virtual_inflight", "virtual_relation_lifecycle", "What happens to invocations already bound to a superseded or recalled edition?", ["complete_bound_edition", "cancel_before_effect", "refuse_new_only", "authority_selected_case_disposition"], "runtime_reconciliation"),
    ("virtual_retirement", "virtual_relation_lifecycle", "When may an edition and alias be retired?", ["no_active_dependencies_and_retention_elapsed", "explicit_consumer_release_receipts", "forced_recall_with_tombstone", "external_lifecycle_authority"], "assurance_insertion"),
]


def build_decisions() -> list[dict[str, Any]]:
    rows = []
    for slug, owner, question, values, phase in DECISION_SEEDS:
        rows.append({
            "decision_id": f"decision.persistence.{slug}",
            "edition": EDITION,
            "status": "declared",
            "owner_context_ref": context_id(owner),
            "question": question,
            "value_contract": "One controlled value or an editioned extension value with an explicit compatibility relation.",
            "allowed_values": values,
            "binding_phase": phase,
            "authority_ref": f"authority.{context_id(owner)}.owner",
            "default_law": "forbidden",
            "default_value": None,
            "constraints": ["must be selected before the affected capability is bound", "provider defaults are observations, not semantic defaults"],
            "conflicts": [],
            "implications": ["selection constrains compatible offers and qualification probes"],
            "affects_contracts": [context_id(owner)],
            "evidence_required": ["decision authority", "selected value", "compatibility evidence", "change receipt"],
            "change_semantics": ["recompile affected bindings", "invalidate incompatible evidence", "plan migration if persisted representation changes"],
            "gaps": ["numeric envelopes remain deployment-owned unless the value contract says otherwise"]
        })
    return rows


def build_contexts(decisions: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    decisions_by_owner: dict[str, list[str]] = defaultdict(list)
    for decision in decisions:
        decisions_by_owner[decision["owner_context_ref"]].append(decision["decision_id"])
    source_ids = {slug: f"source.persistence.{slug}" for slug, *_ in SOURCE_SEEDS}
    context_rows: list[dict[str, Any]] = []
    capabilities: list[dict[str, Any]] = []
    for family, slug, name, question, inside, outside, evidence, operations in CONTEXT_SEEDS:
        cid = context_id(slug)
        cap_refs = [f"persistence.capability.{slug}.{operation}" for operation in operations]
        context_rows.append({
            "context_id": cid,
            "edition": EDITION,
            "status": "candidate_not_adjudicated",
            "family_id": f"persistence.family.{family}",
            "name": name,
            "vision": question,
            "boundary_question": question,
            "inside": inside,
            "outside": outside,
            "ubiquitous_terms": [
                {"term": inside[0], "meaning": f"The context-owned meaning of {inside[0]} inside {name}; foreign meanings require an ACL."},
                {"term": inside[1], "meaning": f"The context-owned meaning of {inside[1]} inside {name}; identity and edition are explicit."}
            ],
            "invariants": [
                "no successful operation may silently weaken its declared persistence, consistency, integrity or visibility guarantee",
                "every state-changing command returns a stable refusal/failure or a receipt identifying the resulting cut",
                f"{name} does not acquire ownership of any excluded meaning"
            ],
            "commands": [f"request_{operation}" for operation in operations],
            "events": [f"{operation}_completed" for operation in operations] + [f"{slug}_operation_refused"],
            "refusals": ["unsupported capability or edition", "authority missing", "precondition or concurrency guard failed", "finite resource or policy constraint unsatisfied"],
            "state_machine": ["unresolved -> planned -> authorized -> executing -> completed|refused|failed", "completed -> superseded only through a new editioned operation"],
            "time_model": ["validity/effect time is distinct from commit, observation and receipt time", "retention and expiry use an explicit clock and boundary convention"],
            "concurrency_model": ["concurrent changes require an explicit isolation, expected-version, lease or merge law", "retries require an idempotency or conflict-revalidation contract"],
            "authority": [f"authority.{cid}.owner decides context semantics", "provider capability claims require qualification evidence", "destructive actions require delegated lifecycle authority"],
            "upstream_context_refs": [],
            "downstream_context_refs": [],
            "decision_refs": sorted(decisions_by_owner.get(cid, [])),
            "capability_refs": cap_refs,
            "evidence_refs": [source_ids[item] for item in evidence],
            "compiler_implications": ["resolve this semantic owner before physical provider binding", "bind every required capability independently", "emit a typed gap rather than infer from product or format name"],
            "gaps": ["candidate boundary requires event-storming and two unrelated vertical proofs", "primary-source clauses and conformance vectors require independent review"]
        })
        surface_by_family = {
            "physical_storage": "storage", "store_model": "storage", "file_format": "file_format",
            "analytical_table": "table", "catalog": "catalog", "maintenance": "maintenance",
            "serving": "serving", "sharing_federation": "sharing"
        }
        for operation in operations:
            cap_id = f"persistence.capability.{slug}.{operation}"
            capabilities.append({
                "capability_id": cap_id,
                "edition": EDITION,
                "status": "candidate",
                "surface": surface_by_family[family],
                "owner_context_ref": cid,
                "name": operation.replace("_", " "),
                "semantics": f"Perform {operation.replace('_', ' ')} under the owned laws of {name}, returning an exact result or typed refusal.",
                "input_contracts": [f"{slug}_intent", "authority_token", "finite_resource_budget", "expected_state_or_cut"],
                "output_contracts": [f"{slug}_result", f"{slug}_receipt", "residual_gap_set"],
                "preconditions": ["input identities and editions resolve", "required decisions are bound", "authority and resource budget are valid"],
                "postconditions": ["result identifies its exact state/cut", "all observable effects and residual gaps are receipted"],
                "guarantees": ["no silent semantic downgrade", "provider behavior is bounded by the selected offer contract"],
                "failure_states": ["unsupported_capability", "authority_refused", "concurrency_conflict", "resource_exhausted", "integrity_failed", "provider_failed", "result_unknown"],
                "effects": ["read_or_write effects are explicit in the selected operation profile", "destructive effects require separate authority"],
                "determinism": "deterministic_given_cut_and_policy",
                "idempotency": "idempotent_with_key" if any(word in operation for word in ["put", "write", "commit", "create", "publish", "apply", "execute", "append", "refresh", "build", "reclaim", "delete", "expire", "drop", "replace"]) else "not_applicable",
                "concurrency": ["expected-state or isolation contract is mandatory for mutations", "read cut and staleness are explicit for reads"],
                "information_loss": "declared_irreversible" if any(word in operation for word in ["delete", "drop", "expire", "reclaim", "truncate", "purge"]) else "none",
                "resource_dimensions": ["bytes_read", "bytes_written", "requests", "cpu_time", "memory_peak", "elapsed_time", "egress_bytes"],
                "decision_refs": sorted(decisions_by_owner.get(cid, [])),
                "qualification_probes": ["happy-path conformance", "concurrent mutation/adversarial retry", "failure injection and recovery", "limit and cancellation behavior"],
                "receipt_fields": ["operation_id", "provider_binding", "input_cut", "output_cut", "decision_trace", "resource_usage", "started_at", "completed_at", "outcome"],
                "evidence_refs": [source_ids[item] for item in evidence],
                "gaps": ["exact executable conformance vectors remain to be authored for each selected format/protocol profile"]
            })
    return context_rows, capabilities


# slug, kind, name, promise, owns, requires, excludes, decision slugs,
# capability shorthands (context.operation), evidence slugs, verdict
BOUNDARY_SEEDS = [
    ("lib.storage_identity", "semantic_library", "Storage Identity Types", "Pure types for provider-neutral byte cuts, object/file/block identities and versions.", ["storage cut", "object identity", "byte range", "content digest"], [], ["I/O", "provider credentials", "table semantics"], ["object_identity", "integrity_digest"], ["object_namespace.get_object_range", "integrity.compute_checksum"], ["s3.consistency", "s3.checksum"], "keep_separate"),
    ("lib.persistence_outcome", "semantic_library", "Persistence Outcome Algebra", "Pure total outcomes for durable, visible, stale, partial, refused, failed and unknown states.", ["persistence outcome", "visibility outcome", "durability evidence", "unknown result"], [], ["retry execution", "provider exception strings"], [], ["block_device.flush_blocks", "commit_protocol.retry_table_commit"], ["nvme.spec", "iceberg.rest"], "keep_separate"),
    ("lib.object_contract", "runtime_library", "Object Storage Contract", "Typed effect intents for object reads, ranges, listings, multipart writes and preconditions.", ["object operation", "conditional request", "multipart intent", "listing cursor"], ["lib.storage_identity"], ["provider SDK choice", "table commit"], ["object_conditional", "listing_law"], ["object_namespace.put_object", "object_namespace.get_object_range", "object_namespace.conditional_replace", "object_namespace.list_objects"], ["s3.consistency", "s3.conditional"], "keep_separate"),
    ("lib.filesystem_contract", "runtime_library", "Filesystem Contract", "Typed path, file-handle, lock, rename and synchronization intents.", ["path identity", "file operation", "lock intent", "sync receipt"], ["lib.storage_identity"], ["database isolation", "object listing"], ["file_sync", "network_lock_recovery"], ["local_filesystem.open_file", "local_filesystem.atomic_rename", "local_filesystem.synchronize_file", "network_filesystem.lock_range"], ["posix.rename", "posix.fsync", "nfs.v41"], "keep_separate"),
    ("lib.integrity", "algorithm_library", "Integrity and Digest Kernels", "Pure streaming checksums, digests, combination laws and verification oracles.", ["checksum algorithm", "digest state", "verification", "mismatch"], [], ["encryption", "business authenticity"], ["integrity_digest"], ["integrity.compute_checksum", "integrity.verify_checksum"], ["s3.checksum", "parquet.encryption"], "keep_separate"),
    ("lib.compression", "algorithm_library", "Compression Codec Kernels", "Pure reversible codec implementations behind a stable codec and resource contract.", ["codec id", "codec parameters", "encode/decode", "resource envelope"], [], ["column encoding", "table compaction", "provider tiering"], ["compression_codec", "compression_level", "compression_unit"], ["compression.compress_bytes", "compression.decompress_bytes", "compression.benchmark_codec"], ["parquet.compression", "orc.spec", "zarr.v3"], "keep_separate"),
    ("lib.value_encoding", "algorithm_library", "Value Encoding Kernels", "Pure dictionary, RLE, delta, bit-packing and byte-stream transforms.", ["value encoding", "dictionary", "encoded page", "decode law"], [], ["general compression", "encryption"], ["encoding_choice"], ["encoding.select_encoding", "encoding.encode_values", "encoding.decode_values"], ["parquet.encoding", "orc.spec"], "keep_separate"),
    ("lib.file_crypto", "runtime_library", "File Encryption Modules", "Typed file-module encryption/decryption effects with separate key-provider ports.", ["module encryption", "AAD", "key reference", "crypto receipt"], ["lib.storage_identity"], ["identity system", "key vault implementation", "authorization policy"], ["file_encryption_keys", "encryption_scope"], ["modular_encryption.encrypt_file_modules", "modular_encryption.decrypt_file_projection", "modular_encryption.rotate_file_keys"], ["parquet.encryption"], "keep_separate"),
    ("lib.logical_types", "semantic_library", "Portable Logical Type Algebra", "Pure logical/physical type mappings, compatibility relations and refusal proofs.", ["logical type", "physical carrier", "field id", "compatibility relation"], [], ["industry meaning", "file I/O"], ["logical_type_mapping", "field_identity", "schema_compatibility"], ["logical_types.annotate_logical_type", "logical_types.validate_type_mapping", "schema_evolution.validate_schema_change"], ["parquet.format", "avro.spec", "arrow.columnar", "iceberg.table"], "keep_separate"),
    ("lib.columnar_layout", "semantic_library", "Columnar Layout Types", "Pure types for pages, row groups, stripes, buffers, validity, offsets and projection.", ["columnar layout", "page", "row group", "buffer", "projection"], ["lib.logical_types"], ["compression implementation", "storage I/O", "table snapshot"], ["row_group_size"], ["columnar_file.encode_columnar_file", "columnar_file.decode_projection", "in_memory_columnar.validate_buffer_layout"], ["parquet.format", "orc.spec", "arrow.columnar"], "keep_separate"),
    ("lib.file_statistics", "algorithm_library", "File Statistics and Pruning", "Pure statistics construction, validation and safe predicate-pruning decisions.", ["statistics", "bound", "null count", "pruning verdict"], ["lib.logical_types"], ["business measure", "optimizer cost selection"], ["statistics_privacy"], ["file_statistics.compute_file_statistics", "file_statistics.validate_statistics", "columnar_file.prune_row_groups"], ["parquet.format", "orc.spec"], "keep_separate"),
    ("lib.probabilistic_index", "algorithm_library", "Probabilistic Membership Index", "Pure Bloom-filter construction/probe with explicit false-positive and no-false-negative laws.", ["membership set", "Bloom filter", "false-positive budget", "probe verdict"], ["lib.integrity"], ["exact index", "semantic similarity"], ["bloom_fpp"], ["probabilistic_index.build_bloom_filter", "probabilistic_index.probe_bloom_filter"], ["parquet.bloom"], "keep_separate"),
    ("lib.table_identity", "semantic_library", "Analytical Table Identity", "Pure table, snapshot, schema, partition-spec and reference identities.", ["table id", "snapshot id", "schema id", "partition spec id", "reference"], [], ["catalog storage", "file I/O", "business entity"], ["field_identity"], ["table_identity.create_table_identity", "table_identity.resolve_table_identity"], ["iceberg.table", "delta.protocol"], "keep_separate"),
    ("lib.schema_evolution", "semantic_library", "Schema Evolution Algebra", "Pure schema changes, compatibility proofs and stable-field-identity laws.", ["schema change", "compatibility", "field lineage", "migration refusal"], ["lib.logical_types", "lib.table_identity"], ["source schema authority", "physical rewrite"], ["field_identity", "schema_compatibility"], ["schema_evolution.propose_schema_change", "schema_evolution.validate_schema_change"], ["iceberg.table", "delta.protocol", "avro.spec"], "keep_separate"),
    ("lib.partition_algebra", "semantic_library", "Partition Transform Algebra", "Pure transforms, projection laws and partition-spec evolution.", ["partition transform", "partition tuple", "spec evolution", "predicate projection"], ["lib.logical_types", "lib.table_identity"], ["file placement", "business grouping"], ["partition_transform"], ["partition_evolution.propose_partition_spec", "partition_evolution.derive_partition_tuple"], ["iceberg.table"], "keep_separate"),
    ("lib.snapshot_graph", "semantic_library", "Snapshot and Manifest Graph", "Pure immutable snapshot graph, manifest inventory and reachability semantics.", ["snapshot graph", "manifest", "file entry", "reachability"], ["lib.table_identity"], ["object reads", "catalog commit"], ["snapshot_retention"], ["snapshot_state.construct_snapshot", "snapshot_state.diff_snapshots", "manifest_inventory.scan_manifests"], ["iceberg.table", "delta.protocol"], "keep_separate"),
    ("lib.row_change", "semantic_library", "Row Change and Delete Algebra", "Pure append/update/delete/merge representations across copy-on-write and merge-on-read profiles.", ["row change", "position delete", "equality delete", "deletion vector", "merge order"], ["lib.table_identity"], ["business correction authority", "file writing"], ["mutation_model"], ["row_level_mutation.plan_row_change", "merge_on_read.merge_at_read", "copy_on_write.plan_copy_on_write"], ["iceberg.table", "delta.protocol", "hudi.spec"], "keep_separate"),
    ("lib.commit_protocol", "runtime_library", "Table Commit Protocol", "Pure requirements/updates plus effect intents for atomic expected-state transitions.", ["commit requirement", "commit update", "conflict", "idempotency", "receipt"], ["lib.snapshot_graph", "lib.persistence_outcome"], ["catalog implementation", "file writer", "job scheduling"], ["table_commit_authority", "table_isolation", "commit_retry"], ["commit_protocol.prepare_table_commit", "commit_protocol.commit_table_state", "isolation_conflicts.detect_table_conflict"], ["iceberg.table", "iceberg.rest", "delta.protocol"], "keep_separate"),
    ("lib.scan_planner", "algorithm_library", "Table Scan Planner", "Pure snapshot-to-file/task planning with predicate, projection and delete attachment laws.", ["scan intent", "file task", "delete attachment", "residual predicate", "planning receipt"], ["lib.snapshot_graph", "lib.partition_algebra", "lib.file_statistics"], ["query optimization beyond scan", "compute scheduling"], [], ["manifest_inventory.scan_manifests", "columnar_file.prune_row_groups", "time_travel.scan_historical_snapshot"], ["iceberg.table", "parquet.format"], "keep_separate"),
    ("lib.compaction_planner", "algorithm_library", "Compaction Planner", "Pure candidate grouping and rewrite plans under target shape and interference budgets.", ["compaction plan", "rewrite group", "target shape", "amplification estimate"], ["lib.snapshot_graph"], ["file I/O", "commit authority", "scheduler"], ["compaction_trigger", "target_file_shape", "maintenance_interference"], ["compaction.plan_compaction", "fragmentation.recommend_file_shape"], ["hudi.spec", "cassandra.storage", "druid.storage"], "keep_separate"),
    ("lib.clustering_planner", "algorithm_library", "Clustering Planner", "Pure layout-key selection and rewrite planning with overlap and amplification estimates.", ["clustering plan", "layout strategy", "extent", "quality measure"], ["lib.snapshot_graph"], ["file I/O", "query optimizer policy"], ["clustering_strategy"], ["clustering.plan_clustering", "clustering.measure_clustering_quality"], ["delta.liquid", "clickhouse.mergetree"], "keep_separate"),
    ("lib.reachability_gc", "policy_pure", "Snapshot Reachability and GC Oracle", "Pure proof that a file is unreachable under all refs, retention floors, leases and holds.", ["reachability proof", "safety horizon", "delete authorization", "counterexample"], ["lib.snapshot_graph"], ["physical deletion", "legal-policy ownership"], ["snapshot_retention", "orphan_horizon", "delete_evidence"], ["snapshot_expiry.plan_snapshot_expiry", "orphan_cleanup.discover_orphans", "physical_deletion.authorize_reclamation"], ["iceberg.table", "s3.object_lock"], "keep_separate"),
    ("lib.backup_manifest", "semantic_library", "Backup and Restore Manifest", "Pure identities and dependency chains for backups, logs, restore targets and proof.", ["backup manifest", "incremental dependency", "restore target", "verification result"], ["lib.storage_identity"], ["backup I/O", "database-specific recovery"], ["backup_mode", "restore_target"], ["backup.verify_backup_manifest", "restore.plan_restore"], ["postgres.incremental", "rocksdb.backup"], "keep_separate"),
    ("lib.recovery_objectives", "semantic_library", "Recovery Objective Measurement and Attainment", "Pure declared-versus-achieved RPO/RTO measurement, partiality and attainment evidence over exact source, disruption, recovery and service-acceptance occurrences.", ["recovery objective set", "RPO objective", "RTO objective", "disruption reference", "source commit cut", "accepted recovered cut", "recovery interval boundary", "recovery point distance", "recovery duration", "objective attainment", "measurement residual", "measurement evidence"], ["lib.backup_manifest"], ["business impact tolerance authority", "incident command", "backup capture", "restore execution", "application acceptance criteria", "availability promise"], ["rpo_reference", "rto_start", "rto_end", "recovery_measurement_partiality", "recovery_clock"], ["recovery_objectives.bind_recovery_objectives", "recovery_objectives.measure_achieved_rpo", "recovery_objectives.measure_achieved_rto", "recovery_objectives.evaluate_recovery_objective_attainment", "recovery_objectives.explain_measurement_residuals"], ["nist.sp800_34", "postgres.backup", "postgres.incremental"], "keep_separate"),
    ("lib.catalog_contract", "semantic_library", "Catalog and Commit Contracts", "Pure namespace, asset, location, commit, credential and protocol types.", ["catalog identity", "asset descriptor", "commit request", "storage grant"], ["lib.table_identity", "lib.commit_protocol"], ["catalog server", "policy language", "credential implementation"], ["catalog_protocol", "managed_external", "credential_mode"], ["namespace.resolve_name", "commit_authority.commit_metadata_update", "credential_vending.issue_scoped_credential"], ["iceberg.rest", "unitycatalog.api"], "keep_separate"),
    ("lib.materialization", "semantic_library", "Materialization and Freshness Algebra", "Pure view dependencies, frontiers, cuts, staleness and retraction semantics.", ["materialization", "frontier", "retraction", "freshness", "staleness"], [], ["query execution", "runtime storage", "metric semantics"], ["materialization_refresh", "materialization_consistency", "serving_freshness"], ["materialized_view.create_materialization", "incremental_materialization.advance_materialization_frontier", "freshness_contract.measure_freshness"], ["materialize.views", "timescale.aggregate"], "keep_separate"),
    ("lib.index_mutation", "runtime_library", "Index Mutation Generation and Acknowledgement", "Provider-neutral mutation intents, epoch-scoped order, conflict/idempotency guards, effect attempts, scoped acknowledgements and unknown-outcome reconciliation for add, replace, delete and no-op index changes.", ["index id", "index edition", "index document id", "source revision ref", "index mutation id", "mutation operation", "mutation batch", "writer epoch", "mutation order token", "expected index state", "idempotency key", "mutation attempt", "acknowledgement scope", "mutation receipt", "mutation residual", "mutation refusal"], ["lib.persistence_outcome"], ["source document truth", "document projection semantics", "search visibility", "query or ranking", "provider storage internals"], ["index_mutation_order", "index_mutation_precondition", "index_mutation_ack", "index_mutation_batch", "index_mutation_idempotency", "index_mutation_unknown", "index_delete_semantics", "index_replica_ack"], ["index_mutation.bind_index_mutation_contract", "index_mutation.admit_mutation_batch", "index_mutation.submit_index_mutation", "index_mutation.record_mutation_acknowledgement", "index_mutation.reconcile_mutation_outcome", "index_mutation.project_mutation_frontier"], ["lucene.index_writer", "elastic.index_api", "elastic.translog", "solr.commits"], "keep_separate"),
    ("lib.search_visibility", "runtime_library", "Search Visibility Cut and Publication", "Provider-neutral publication intents and immutable evidence for per-shard mutation frontiers, reader/searcher snapshots, partial visibility, read-after-write waiting and verified delete disappearance without equating visibility with durability.", ["visibility request id", "visibility generation", "mutation frontier", "shard visibility cut", "reader snapshot id", "publication attempt", "search visibility cut", "visibility receipt", "partial visibility", "visibility residual", "visibility refusal"], ["lib.index_mutation"], ["source document truth", "index mutation authority", "query and ranking semantics", "durability promise", "cache invalidation"], ["search_visibility_publication", "search_visibility_cut", "search_visibility_partiality", "search_visibility_wait", "search_visibility_durability", "search_delete_disappearance", "search_visibility_capacity"], ["search_visibility.request_visibility_publication", "search_visibility.publish_search_visibility", "search_visibility.wait_for_mutation_visibility", "search_visibility.observe_search_visibility_cut", "search_visibility.compare_visibility_cuts", "search_visibility.reconcile_visibility_timeout", "search_visibility.verify_delete_disappearance"], ["lucene.point_in_time", "elastic.refresh", "elastic.translog", "solr.commits"], "keep_separate"),
    ("lib.cache_fill_coordination", "runtime_library", "Cache Fill Single-Flight Coordination", "Fenced state and effect contracts for admitting or joining one cache-fill generation, delivering only eligible shared outcomes, detaching waiters and reconciling failure, cancellation, expiry and late completion.", ["fill equivalence key", "fill generation id", "fill leader lease", "fencing token", "waiter id", "waiter registration", "fill attempt", "fill outcome", "fill receipt", "stale serve decision", "coordination policy", "coordination budget", "fill refusal"], [], ["request equivalence", "cache storage", "source computation", "source truth", "authorization", "provider lock implementation"], ["fill_leadership", "fill_follower", "fill_cancellation", "fill_failure", "fill_late_completion", "fill_capacity", "cache_staleness"], ["cache_fill_coordination.admit_or_join_fill", "cache_fill_coordination.publish_fill_outcome", "cache_fill_coordination.detach_waiter", "cache_fill_coordination.serve_stale_under_policy", "cache_fill_coordination.expire_or_supersede_fill", "cache_fill_coordination.reconcile_abandoned_fill"], ["rfc9111.cache", "rfc5861.stale", "go.singleflight", "redis.stampede"], "keep_separate"),
    ("lib.sharing_contract", "semantic_library", "Data Sharing Contracts", "Pure share/listing/recipient/cut/grant/revocation and disclosure types.", ["share", "recipient", "shared cut", "delivery grant", "revocation"], ["lib.table_identity", "lib.storage_identity"], ["identity proofing", "storage download", "business purpose policy"], ["share_access", "share_revocation"], ["share_publication.create_share", "presigned_delivery.issue_presigned_access"], ["delta.sharing"], "keep_separate"),
    ("lib.federation_contract", "semantic_library", "Federation and Pushdown Contracts", "Pure foreign identity, source cuts, remote capabilities, pushdown and residual-result semantics.", ["foreign object", "remote capability", "source cut", "pushdown proof", "residual"], [], ["remote connector I/O", "query optimizer selection"], ["pushdown_semantics", "federated_cut"], ["pushdown.negotiate_pushdown", "federated_consistency.acquire_source_cuts"], ["postgres.fdw", "substrait.serialization"], "keep_separate"),
    ("lib.virtual_relation_identity", "semantic_library", "Virtual Relation Identity and Definition", "Pure stable identity, immutable edition, carrier, output schema, source binding, dependency, security and compatibility contracts for governed virtual relations.", ["virtual relation id", "relation edition", "qualified alias", "definition carrier", "definition digest", "output schema contract", "source binding set", "dependency contract", "security execution profile", "parameter contract", "definition residual"], ["lib.logical_types", "lib.federation_contract"], ["source truth", "query execution", "catalog namespace", "materialization state", "publication authority"], ["virtual_definition_carrier", "virtual_source_binding", "virtual_output_compatibility", "virtual_security_mode", "virtual_parameter_binding"], ["virtual_relation_identity.construct_virtual_relation", "virtual_relation_identity.bind_virtual_sources", "virtual_relation_identity.validate_virtual_relation_definition", "virtual_relation_identity.compare_virtual_relation_editions", "virtual_relation_identity.project_virtual_relation_definition"], ["postgres.create_view", "trino.create_view", "postgres.fdw"], "keep_separate"),
    ("lib.virtual_relation_lifecycle", "policy_pure", "Virtual Relation Publication Lifecycle", "Pure total transition and policy contract for draft, immutable publication, alias advancement, supersession, deprecation, recall, retirement and dependency/in-flight dispositions.", ["virtual relation draft", "publication command", "publication decision", "published relation edition", "public alias head", "supersession relation", "deprecation notice", "recall decision", "retirement tombstone", "dependency impact", "lifecycle receipt", "lifecycle refusal"], ["lib.virtual_relation_identity"], ["definition semantics", "query cancellation execution", "source lifecycle authority", "consumer migration", "materialization lifecycle"], ["virtual_publish_authority", "virtual_dependency_break", "virtual_inflight", "virtual_retirement"], ["virtual_relation_lifecycle.create_virtual_relation_draft", "virtual_relation_lifecycle.publish_virtual_relation_edition", "virtual_relation_lifecycle.supersede_virtual_relation_edition", "virtual_relation_lifecycle.deprecate_virtual_relation", "virtual_relation_lifecycle.recall_virtual_relation_edition", "virtual_relation_lifecycle.retire_virtual_relation"], ["postgres.create_view", "trino.create_view", "trino.alter_view"], "keep_separate"),
    ("lib.conformance_oracles", "algorithm_library", "Persistence Conformance Oracles", "Executable model, property, differential and fault-injection oracles for formats and providers.", ["test vector", "oracle", "fault model", "conformance receipt"], [], ["provider implementation", "marketing certification"], ["catalog_protocol", "compression_codec", "file_format"], ["catalog_qualification.run_catalog_conformance", "format_compatibility.negotiate_format_features", "integrity.verify_checksum"], ["iceberg.rest", "parquet.format", "arrow.columnar"], "keep_separate"),
    ("lib.commit_precondition", "policy_pure", "Commit Precondition Policy", "Pure validation of expected base state, conflict profile, retry/rebase policy and publish authority before any commit effect.", ["commit precondition", "base state", "conflict verdict", "publish intent"], ["lib.snapshot_graph"], ["catalog transport", "provider retry loop", "publication effect"], ["table_isolation", "commit_retry", "table_commit_authority"], ["commit_protocol.prepare_table_commit"], ["iceberg.table", "iceberg.rest", "delta.protocol"], "keep_separate"),
    ("lib.logical_equivalence_oracle", "test_oracle", "Logical Table Equivalence Oracle", "Pure comparison of exact logical cuts, retained history and declared residuals before a rewrite or translation may claim equivalence.", ["logical cut", "equivalence claim", "equivalence verdict", "residual loss"], ["lib.snapshot_graph"], ["physical rewrite", "format translation", "business equivalence"], ["format_migration", "snapshot_retention"], ["format_compatibility.record_compatibility", "table_format_migration.verify_migrated_table"], ["iceberg.table", "hudi.spec", "xtable.limitations"], "keep_separate"),
    ("lib.metadata_codec_spi", "provider_adapter", "Table Metadata Codec SPI", "Editioned pure decode/encode adapter contract for analytical-table metadata with unknown-feature and canonicalization rules.", ["metadata bytes", "decode result", "encode result", "format feature set"], ["lib.snapshot_graph", "lib.logical_types"], ["storage I/O", "table commit authority", "format semantics"], ["file_format", "format_migration", "translation_authority"], ["table_format_migration.translate_table_metadata", "format_compatibility.refuse_unsupported_feature"], ["iceberg.table", "delta.protocol", "hudi.spec"], "keep_separate"),
    ("lib.table_format_acl", "provider_adapter", "Table Format Anti-Corruption Layer", "Loss-aware translation between exact source and target table-format editions without claiming silent equivalence.", ["source format state", "target format state", "feature correspondence", "loss report"], ["lib.snapshot_graph", "lib.metadata_codec_spi", "lib.logical_equivalence_oracle"], ["source format authority", "target commit", "migration approval"], ["format_migration", "translation_authority"], ["table_format_migration.assess_format_compatibility", "table_format_migration.translate_table_metadata", "table_format_migration.verify_migrated_table", "metadata_translation.report_translation_loss"], ["iceberg.table", "delta.protocol", "hudi.spec", "xtable.limitations"], "keep_separate"),

    ("format.parquet", "format", "Apache Parquet", "An interoperable analytical columnar file representation, not a database or table.", ["Parquet physical/logical file layout", "pages", "row groups", "format metadata"], ["lib.columnar_layout", "lib.logical_types"], ["table commit", "catalog", "storage durability", "query service"], ["compression_codec", "row_group_size", "statistics_privacy"], ["columnar_file.encode_columnar_file", "columnar_file.decode_projection"], ["parquet.format", "parquet.encoding", "parquet.compression"], "not_a_product"),
    ("format.orc", "format", "Apache ORC", "An interoperable striped analytical columnar file representation.", ["ORC stripes", "streams", "indexes", "encodings"], ["lib.columnar_layout", "lib.logical_types"], ["table commit", "catalog", "storage service"], ["compression_codec", "row_group_size"], ["columnar_file.encode_columnar_file", "columnar_file.decode_projection"], ["orc.spec"], "not_a_product"),
    ("format.arrow", "format", "Apache Arrow IPC", "An in-memory and IPC columnar interchange representation.", ["Arrow arrays", "record batches", "IPC framing"], ["lib.columnar_layout", "lib.logical_types"], ["durable table", "query service", "catalog"], [], ["in_memory_columnar.export_record_batch", "columnar_transport.publish_result_stream"], ["arrow.columnar"], "not_a_product"),
    ("format.zarr", "format", "Zarr v3", "An extensible chunked N-dimensional array representation.", ["array metadata", "chunk grid", "codec pipeline", "storage-key mapping"], ["lib.compression", "lib.logical_types"], ["scientific variable semantics", "storage durability", "catalog"], ["array_chunk_grid", "compression_codec"], ["array_chunk_format.encode_array_chunk", "array_chunk_format.map_chunk_key"], ["zarr.v3", "zarr.sharding"], "not_a_product"),
    ("format.iceberg", "format", "Apache Iceberg Table Specification", "A portable analytical table-state specification and feature contract.", ["snapshot metadata", "manifests", "schema/partition evolution", "delete files"], ["format.parquet", "lib.snapshot_graph", "lib.commit_protocol"], ["catalog implementation", "query engine", "storage service", "maintenance service"], ["mutation_model", "snapshot_retention", "field_identity"], ["snapshot_state.load_snapshot", "schema_evolution.validate_schema_change", "manifest_inventory.scan_manifests"], ["iceberg.table"], "not_a_product"),
    ("format.delta", "format", "Delta Transaction Log Protocol", "A portable transaction-log table protocol and feature-negotiation contract.", ["Delta actions", "protocol versions", "checkpoints", "table features"], ["format.parquet", "lib.commit_protocol"], ["catalog service", "query engine", "storage service"], ["mutation_model", "commit_retry"], ["snapshot_state.load_snapshot", "format_compatibility.negotiate_format_features"], ["delta.protocol"], "not_a_product"),
    ("format.hudi", "format", "Apache Hudi Table Specification", "A timeline-based analytical table format supporting copy-on-write and merge-on-read.", ["timeline", "file groups", "base/log files", "table services"], ["format.parquet", "lib.row_change"], ["query product", "storage provider", "catalog product"], ["mutation_model", "compaction_trigger"], ["merge_on_read.merge_at_read", "change_feed.read_change_feed"], ["hudi.spec", "hudi.timeline"], "not_a_product"),
    ("format.paimon", "format", "Apache Paimon Table Format", "A table representation for append and primary-key changelog workloads.", ["snapshot", "manifest", "primary-key file", "merge engine"], ["lib.row_change", "lib.snapshot_graph"], ["compute engine", "catalog service", "storage provider"], ["mutation_model"], ["merge_on_read.write_delta", "change_feed.read_change_feed"], ["paimon.spec", "paimon.primary_key"], "not_a_product"),

    ("protocol.iceberg_rest", "protocol", "Iceberg REST Catalog Protocol", "A cross-language catalog and commit protocol, not a catalog deployment.", ["REST operations", "configuration", "change-based commits", "credential vending"], ["lib.catalog_contract"], ["server implementation", "storage provider", "policy owner"], ["catalog_protocol", "credential_mode"], ["commit_authority.commit_metadata_update", "credential_vending.issue_scoped_credential"], ["iceberg.rest"], "not_a_product"),
    ("protocol.delta_sharing", "protocol", "Delta Sharing Protocol", "A provider/recipient data-sharing wire contract, not an exchange operation.", ["share API", "recipient profile", "table query", "delivery modes"], ["lib.sharing_contract"], ["sharing authority", "server deployment", "storage durability"], ["share_access", "share_revocation"], ["share_publication.publish_table_cut", "presigned_delivery.issue_presigned_access"], ["delta.sharing"], "not_a_product"),
    ("protocol.flight_sql", "protocol", "Arrow Flight SQL Protocol", "An Arrow-native SQL client/server protocol.", ["SQL RPC", "metadata RPC", "transactions", "columnar results"], ["format.arrow"], ["SQL semantic profile", "database implementation", "storage"], ["database_api", "transport_resume"], ["query_protocol.execute_statement", "columnar_transport.publish_result_stream"], ["arrow.flight_sql"], "not_a_product"),
    ("protocol.adbc", "protocol", "Arrow Database Connectivity API", "A vendor-neutral Arrow-native client API over pluggable database drivers.", ["driver API", "statement", "result stream", "transaction"], ["format.arrow"], ["server protocol", "database implementation"], ["database_api"], ["query_protocol.open_database_session", "query_protocol.execute_statement"], ["arrow.adbc"], "not_a_product"),

    ("implementation.polaris", "implementation", "Apache Polaris", "One open implementation of an Iceberg REST catalog.", ["catalog server implementation", "Iceberg REST implementation"], ["protocol.iceberg_rest"], ["universal catalog semantics", "deployment SLO", "object storage"], ["catalog_protocol"], ["catalog_qualification.run_catalog_conformance"], ["polaris.docs", "polaris.tlp"], "not_a_product"),
    ("implementation.nessie", "implementation", "Project Nessie", "One implementation of a Git-like versioned data catalog.", ["catalog commit graph", "branches", "tags", "merge"], ["lib.catalog_contract"], ["table data", "query engine", "deployment qualification"], ["catalog_branching"], ["catalog_versioning.commit_catalog_change", "catalog_versioning.merge_catalog_branch"], ["nessie.concepts"], "not_a_product"),
    ("implementation.xtable", "implementation", "Apache XTable", "One metadata translation implementation across table formats.", ["format metadata translation", "sync checkpoint", "target maintenance"], ["format.iceberg", "format.delta", "format.hudi"], ["new table format", "data copy", "multi-writer consensus"], ["translation_authority", "format_migration"], ["metadata_translation.translate_metadata_commit", "metadata_translation.reconcile_format_views"], ["xtable.interop", "xtable.limitations"], "not_a_product"),
    ("deployment.catalog", "deployment", "Qualified Catalog Deployment", "A configured, observed catalog implementation with target-specific SLO, security and limit evidence.", ["endpoint", "edition", "topology", "limits", "SLO evidence", "runbook"], ["protocol.iceberg_rest", "implementation.polaris"], ["catalog semantic ownership", "table data"], ["catalog_protocol", "metadata_cache_ttl", "credential_mode"], ["catalog_qualification.probe_catalog_capability", "catalog_qualification.issue_catalog_receipt"], ["iceberg.rest", "polaris.docs"], "provider_class_only"),
    ("deployment.object_store", "deployment", "Qualified Object Storage Deployment", "A concrete bucket/tenant/region/version with measured consistency, limits, cost and security.", ["bucket occurrence", "region", "observed limits", "credentials", "SLO", "receipts"], ["lib.object_contract"], ["generic object-store class", "table commit semantics"], ["object_identity", "object_conditional", "listing_law", "quota_enforcement"], ["object_namespace.put_object", "object_namespace.conditional_replace"], ["s3.consistency", "s3.conditional"], "provider_class_only"),

    ("product.object_storage", "product", "Object Storage Product", "Operates durable key-addressed objects, versions, lifecycle and access within stated SLOs.", ["object namespace service", "durability operation", "capacity", "lifecycle", "support"], ["lib.object_contract", "deployment.object_store"], ["analytical table identity", "catalog commit", "query semantics"], ["object_identity", "listing_law", "retention_mode", "quota_enforcement"], ["object_namespace.put_object", "object_namespace.get_object_range", "replication.replicate_write"], ["s3.consistency", "ceph.rados", "ozone.architecture"], "compose_as_product"),
    ("product.transactional_store", "product", "Transactional Data Store Product", "Operates one declared logical store model with transaction, recovery, capacity and query guarantees.", ["logical store service", "transaction authority", "recovery", "operational SLO"], ["lib.persistence_outcome"], ["business domain model", "analytics suite", "source connector"], ["transaction_isolation", "backup_mode", "restore_target"], ["relational_store.execute_transaction", "backup.capture_full_backup", "restore.restore_cut"], ["postgres.isolation", "mongodb.transactions", "cassandra.overview"], "compose_as_product"),
    ("product.analytical_table", "product", "Analytical Table Runtime", "Reads, writes and evolves portable analytical table state through stable table/format contracts.", ["table runtime", "reader/writer qualification", "mutation execution", "table API SLO"], ["lib.table_identity", "lib.schema_evolution", "lib.snapshot_graph", "lib.commit_protocol"], ["catalog operation", "query engine", "object storage", "maintenance scheduling"], ["mutation_model", "table_commit_authority", "schema_compatibility"], ["snapshot_state.load_snapshot", "append_mutation.commit_append", "row_level_mutation.commit_row_change"], ["iceberg.table", "delta.protocol", "hudi.spec"], "compose_as_product"),
    ("product.catalog_commit", "product", "Catalog and Commit Authority", "Operates namespace, asset, location, commit and short-lived storage-grant authority.", ["catalog service", "commit serialization", "namespace", "location allocation", "credential vending"], ["lib.catalog_contract"], ["table format", "query engine", "policy language", "object durability"], ["catalog_protocol", "managed_external", "credential_mode", "metadata_cache_ttl"], ["namespace.create_namespace", "commit_authority.commit_metadata_update", "credential_vending.issue_scoped_credential"], ["iceberg.rest", "polaris.docs", "unitycatalog.api"], "compose_as_product"),
    ("product.table_maintenance", "product", "Table Maintenance and Optimization", "Plans, executes and proves semantics-preserving rewrites, expiry, indexing and cleanup under budgets.", ["maintenance backlog", "rewrite operation", "destructive authority", "interference SLO", "receipts"], ["lib.compaction_planner", "lib.clustering_planner", "lib.reachability_gc"], ["table commit ownership", "query service", "business retention policy"], ["compaction_trigger", "clustering_strategy", "orphan_horizon", "maintenance_interference"], ["compaction.execute_compaction", "snapshot_expiry.expire_snapshots", "index_build.build_index"], ["iceberg.table", "hudi.spec", "delta.liquid"], "compose_as_product"),
    ("product.materialization", "product", "Materialization and Serving", "Operates durable/in-memory derived structures with explicit source cuts, freshness, refresh and cutover.", ["materialization lifecycle", "freshness SLO", "serving cut", "cutover", "rebuild"], ["lib.materialization"], ["metric semantics", "source ownership", "general query engine"], ["materialization_refresh", "materialization_consistency", "serving_freshness", "serving_partial"], ["materialized_view.refresh_materialization", "serving_cutover.cutover_serving_traffic", "freshness_contract.enforce_staleness_budget"], ["materialize.views", "timescale.aggregate", "druid.storage"], "compose_as_product"),
    ("product.data_sharing", "product", "Data Sharing and Exchange", "Publishes, delivers, audits and revokes exact data cuts across authority boundaries.", ["share lifecycle", "recipient subscription", "delivery grant", "disclosure evidence", "revocation"], ["lib.sharing_contract"], ["source table ownership", "identity proofing", "business purpose policy"], ["share_access", "share_revocation", "credential_mode"], ["share_publication.publish_table_cut", "share_subscription.subscribe_share", "presigned_delivery.issue_presigned_access"], ["delta.sharing", "iceberg.rest"], "compose_as_product"),
    ("product.federation", "product", "Federated Data Access", "Mounts remote authorities and executes only semantically qualified pushdowns with explicit cross-source cuts.", ["federated namespace", "connector qualification", "pushdown", "cross-source cut", "partial result"], ["lib.federation_contract"], ["remote source truth", "business reconciliation", "local query optimizer"], ["pushdown_semantics", "federated_cut", "database_api"], ["federated_namespace.mount_foreign_namespace", "pushdown.execute_remote_operation", "federated_consistency.execute_federated_read"], ["postgres.fdw", "trino.catalog", "substrait.serialization"], "compose_as_product"),
    ("product.backup_recovery", "product", "Backup and Recovery", "Operates backup chains, restores and recurring clean-room recovery proofs for qualified stores.", ["backup schedule", "backup custody", "restore operation", "RPO/RTO evidence", "runbooks"], ["lib.backup_manifest", "lib.recovery_objectives"], ["source database semantics", "application restart", "business reconciliation"], ["backup_mode", "restore_target", "rpo_reference", "rto_start", "rto_end", "recovery_measurement_partiality", "recovery_clock", "delete_evidence"], ["backup.capture_incremental_backup", "restore.restore_cut", "restore.verify_restored_cut", "recovery_objectives.evaluate_recovery_objective_attainment"], ["nist.sp800_34", "postgres.incremental", "rocksdb.backup"], "compose_as_product"),
    ("product.query", "product", "Analytical Query Engine", "Compiles and executes relational/analytical requests against bound table and serving providers.", ["query service", "planning/execution SLO", "result delivery", "cancellation"], ["lib.scan_planner", "protocol.flight_sql"], ["table ownership", "catalog authority", "semantic metric ownership", "storage durability"], ["database_api", "transport_resume"], ["query_protocol.execute_statement", "bulk_result_delivery.publish_result_manifest"], ["arrow.flight_sql", "arrow.adbc"], "compose_as_product"),
    ("product.ingestion", "product", "Data Ingestion and Publication", "Moves typed source cuts into target tables/stores with reconciliation and publication receipts.", ["ingestion job", "source-target handoff", "reconciliation", "publication"], ["product.analytical_table", "product.catalog_commit"], ["source-system ownership", "table maintenance", "query serving"], [], ["append_mutation.commit_append", "change_feed.checkpoint_change_consumer"], ["druid.storage", "hudi.timeline"], "compose_as_product"),
    ("product.control_plane", "product", "Persistence Desired-State Control Plane", "Reconciles deployments, bindings, editions, policies and health without owning data-plane semantics.", ["desired state", "observed state", "rollout", "drift", "provider binding"], ["deployment.catalog", "deployment.object_store"], ["table state", "query result", "business policy meaning"], ["catalog_protocol", "quota_enforcement", "maintenance_interference"], ["catalog_qualification.probe_catalog_capability", "maintenance_coordination.schedule_maintenance"], ["polaris.docs", "druid.storage"], "compose_as_product"),
    ("experience.lakehouse", "managed_experience", "Managed Lakehouse Experience", "Provides a coherent user journey across independent ingestion, table, catalog, query, maintenance, governance, sharing and control products.", ["cross-product journey", "environment status", "onboarding", "integrated support"], ["product.ingestion", "product.analytical_table", "product.catalog_commit", "product.query", "product.table_maintenance", "product.data_sharing", "product.control_plane"], ["new table semantics", "new catalog authority", "one universal runtime"], ["file_format", "catalog_protocol", "mutation_model", "maintenance_interference"], [], ["iceberg.table", "iceberg.rest", "polaris.docs"], "compose_as_managed_experience"),
    ("suite.lakehouse", "suite", "Lakehouse Product Suite", "Commercially and operationally packages substitutable data products under one lifecycle and support envelope.", ["suite packaging", "commercial plan", "support entry", "cross-product compatibility matrix"], ["experience.lakehouse"], ["semantic ownership of packaged products", "forced single-provider binding"], [], [], ["iceberg.table", "delta.protocol", "hudi.spec", "polaris.docs"], "compose_as_suite"),
]


def expand_capability_ref(shorthand: str) -> str:
    owner, operation = shorthand.split(".", 1)
    return f"persistence.capability.{owner}.{operation}"


def build_boundaries() -> list[dict[str, Any]]:
    source_ids = {slug: f"source.persistence.{slug}" for slug, *_ in SOURCE_SEEDS}
    rows = []
    for slug, kind, name, promise, owns, requires, excludes, decisions, caps, evidence, verdict in BOUNDARY_SEEDS:
        candidate_id = f"persistence.boundary.{slug}"
        rows.append({
            "candidate_id": candidate_id,
            "edition": EDITION,
            "status": "candidate",
            "record_kind": kind,
            "name": name,
            "promise": promise,
            "owns": owns,
            "requires": [f"persistence.boundary.{item}" for item in requires],
            "excludes": excludes,
            "decision_refs": [f"decision.persistence.{item}" for item in decisions],
            "capability_refs": [expand_capability_ref(item) for item in caps],
            "substitutability": "May be replaced independently when a candidate satisfies the same editions, laws, limits, evidence gates and migration contract.",
            "adoption_and_exit": "Adoption binds explicit requirements; exit exports owned state/evidence and never requires semantic ownership to move silently.",
            "authority": "May exercise only the capabilities and resource scopes delegated through its binding; packaged neighbors retain their authority.",
            "failure_isolation": "Failure is contained at this boundary and yields typed unavailable, partial, stale, refused, failed or unknown outcomes as applicable.",
            "versioning": "Public contracts and persisted representations are editioned independently; compatibility is a relation, not a boolean label.",
            "economics": "Meters its own storage, requests, transfer, compute, maintenance and support work without hiding cross-product costs.",
            "qualification": ["exact contract conformance", "fault/retry/cancellation behavior", "finite resource envelope", "migration and removal seam", "two independent implementations where a standard is claimed"],
            "evidence_refs": [source_ids[item] for item in evidence],
            "boundary_verdict": verdict,
            "gaps": ["candidate requires 110-dimension truth-profile completion before final product adjudication", "market packaging is evidence of adoption, not semantic ownership"]
        })
    return rows


LIBRARY_KINDS = {
    "semantic_library": "semantic_pure",
    "algorithm_library": "algorithm_pure",
    "policy_pure": "policy_pure",
    "runtime_library": "runtime_mechanism",
    "test_oracle": "test_oracle",
    "provider_adapter": "provider_adapter",
}

# The source boundary candidates sometimes contribute to several contexts.  The shared library
# contract permits exactly one semantic owner, so the candidate primary owner is stated here rather
# than inferred from list order.  Multi-context ownership remains an explicit adjudication gap in
# the generated record; this projection does not ratify the choice.
LIBRARY_PRIMARY_OWNERS = {
    "lib.storage_identity": "persistence.context.object_namespace",
    "lib.persistence_outcome": "persistence.context.commit_protocol",
    "lib.object_contract": "persistence.context.object_namespace",
    "lib.filesystem_contract": "persistence.context.local_filesystem",
    "lib.integrity": "persistence.context.integrity",
    "lib.compression": "persistence.context.compression",
    "lib.value_encoding": "persistence.context.encoding",
    "lib.file_crypto": "persistence.context.modular_encryption",
    "lib.logical_types": "persistence.context.logical_types",
    "lib.columnar_layout": "persistence.context.columnar_file",
    "lib.file_statistics": "persistence.context.file_statistics",
    "lib.probabilistic_index": "persistence.context.probabilistic_index",
    "lib.table_identity": "persistence.context.table_identity",
    "lib.schema_evolution": "persistence.context.schema_evolution",
    "lib.partition_algebra": "persistence.context.partition_evolution",
    "lib.snapshot_graph": "persistence.context.snapshot_state",
    "lib.row_change": "persistence.context.row_level_mutation",
    "lib.commit_protocol": "persistence.context.commit_protocol",
    "lib.scan_planner": "persistence.context.manifest_inventory",
    "lib.compaction_planner": "persistence.context.compaction",
    "lib.clustering_planner": "persistence.context.clustering",
    "lib.reachability_gc": "persistence.context.snapshot_expiry",
    "lib.backup_manifest": "persistence.context.backup",
    "lib.recovery_objectives": "persistence.context.recovery_objectives",
    "lib.catalog_contract": "persistence.context.commit_authority",
    "lib.materialization": "persistence.context.materialized_view",
    "lib.index_mutation": "persistence.context.index_mutation",
    "lib.search_visibility": "persistence.context.search_visibility",
    "lib.cache_fill_coordination": "persistence.context.cache_fill_coordination",
    "lib.sharing_contract": "persistence.context.share_publication",
    "lib.federation_contract": "persistence.context.pushdown",
    "lib.virtual_relation_identity": "persistence.context.virtual_relation_identity",
    "lib.virtual_relation_lifecycle": "persistence.context.virtual_relation_lifecycle",
    "lib.conformance_oracles": "persistence.context.catalog_qualification",
    "lib.commit_precondition": "persistence.context.commit_protocol",
    "lib.logical_equivalence_oracle": "persistence.context.format_compatibility",
    "lib.metadata_codec_spi": "persistence.context.table_format_migration",
    "lib.table_format_acl": "persistence.context.metadata_translation",
}


def pascal(value: str) -> str:
    return "".join(part[:1].upper() + part[1:] for part in re.split(r"[^a-zA-Z0-9]+", value) if part)


def build_library_boundaries(
    boundaries: list[dict[str, Any]], capabilities: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    """Project only actual libraries into the shared compiler library contract.

    Formats, protocols, implementations, deployments, products, experiences and suites remain in
    ``boundary-candidates.jsonl``.  Treating all 59 boundary candidates as libraries would erase the
    product/provider/representation distinctions this universe exists to preserve.
    """
    capability_by_id = {row["capability_id"]: row for row in capabilities}
    boundary_kind_by_id = {row["candidate_id"]: row["record_kind"] for row in boundaries}
    rows: list[dict[str, Any]] = []
    for boundary in boundaries:
        source_kind = boundary["record_kind"]
        if source_kind not in LIBRARY_KINDS:
            continue
        source_slug = boundary["candidate_id"].removeprefix("persistence.boundary.")
        library_slug = source_slug.removeprefix("lib.")
        library_id = f"library.persistence.{library_slug}"
        capability_rows = [capability_by_id[ref] for ref in boundary["capability_refs"]]
        contributes = sorted({row["owner_context_ref"] for row in capability_rows})
        primary_owner = LIBRARY_PRIMARY_OWNERS[source_slug]
        assert primary_owner in contributes
        pure = source_kind in {"semantic_library", "algorithm_library", "policy_pure", "test_oracle", "provider_adapter"}
        dependency_rows = []
        for ref in boundary["requires"]:
            required_kind = boundary_kind_by_id[ref]
            assert required_kind in LIBRARY_KINDS, (
                f"library {boundary['candidate_id']} cannot depend on non-library boundary {ref}"
            )
            dependency_rows.append({
                "ref": f"library.persistence.{ref.removeprefix('persistence.boundary.lib.')}",
                "kind": {
                    "semantic_library": "semantic",
                    "algorithm_library": "algorithm",
                    "policy_pure": "algorithm",
                    "runtime_library": "runtime",
                    "provider_adapter": "provider",
                    "test_oracle": "test",
                }[required_kind],
                "purpose": "Required typed persistence contribution declared by the source boundary.",
                "optional": False,
                "removable": False,
            })
        operation_refs = sorted({
            ref.replace("persistence.capability.", "operation.persistence.", 1)
            for ref in boundary["capability_refs"]
        })
        decisions = sorted({
            *boundary["decision_refs"],
            *(decision for row in capability_rows for decision in row["decision_refs"]),
        })
        gaps = list(boundary["gaps"])
        if len(contributes) > 1:
            gaps.append(
                f"Primary semantic owner {primary_owner} is a projection candidate; joint owners must adjudicate "
                f"the contribution boundary across {', '.join(contributes)}."
            )
        rows.append({
            "library_id": library_id,
            "edition": EDITION,
            "status": "specified",
            "library_kind": LIBRARY_KINDS[source_kind],
            "semantic_owner_refs": [primary_owner],
            "contributes_to_context_refs": contributes,
            "effect_boundary": "pure_no_io" if pure else "effectful_runtime",
            "public_types": sorted({pascal(item) for item in boundary["owns"]}),
            "public_traits": sorted({pascal(ref.rsplit(".", 1)[-1]) for ref in operation_refs}),
            "operation_refs": operation_refs,
            "error_contracts": sorted({pascal(state) for row in capability_rows for state in row["failure_states"]}),
            "decision_refs": decisions,
            "requirement_refs": [],
            "offer_refs": [],
            "configuration_contracts": [
                "Every referenced decision is selected explicitly and digest-bound; provider defaults are observations only."
            ],
            "effect_intents": [] if pure else operation_refs,
            "runtime_receipts": [] if pure else ["PersistenceOperationReceipt"],
            "laws": [
                boundary["substitutability"],
                boundary["failure_isolation"],
                boundary["versioning"],
                "A format, protocol, implementation, deployment, product, experience or suite is not a library by proximity.",
            ],
            "oracles": list(boundary["qualification"]),
            "resource_contracts": [
                "Bytes, requests, CPU, memory, elapsed time and egress are finite, observed and receipted or the operation refuses."
            ],
            "concurrency": sorted({item for row in capability_rows for item in row["concurrency"]}),
            "cancellation": [
                "Effectful work accepts cancellation and reports whether completion, compensation or result state is still unknown."
            ],
            "unsafe_ffi_generated_policy": [
                "Unsafe, FFI and generated code are isolated behind an independently qualified adapter boundary.",
                "Generated code and model output are never semantic authority.",
            ],
            "dependencies": sorted(dependency_rows, key=lambda row: row["ref"]),
            "targets": ["provider_neutral_contract"],
            "compatibility": [boundary["versioning"]],
            "removal_seams": [boundary["substitutability"]],
            "forbidden_responsibilities": sorted({
                *boundary["excludes"],
                "provider-name dispatch",
                "product or suite outcome promise",
            }),
            "evidence_refs": boundary["evidence_refs"],
            "gaps": gaps,
        })
        if source_slug == "lib.recovery_objectives":
            rows[-1].update({
                "public_types": [
                    "AcceptedRecoveredCut", "ClockEvidence", "DisruptionOccurrenceRef",
                    "MeasurementProfile", "MeasurementResidual", "ObjectiveAttainment",
                    "RecoveryDependencyGraph", "RecoveryDuration", "RecoveryObjectiveEvidence",
                    "RecoveryObjectiveRefusal", "RecoveryObjectiveSet", "RecoveryPointDistance",
                    "RecoveryScopeEdition", "RecoveryStartBoundary", "RpoObjective", "RtoObjective",
                    "ServiceAcceptanceBoundary", "SourceCommitCut",
                ],
                "public_traits": [
                    "RecoveryCutDistance", "RecoveryDurationMeasure",
                    "RecoveryEvidenceValidator", "RecoveryObjectiveEvaluator",
                ],
                "configuration_contracts": [
                    "RpoReferencePolicy", "RtoStartBoundaryPolicy", "RtoEndBoundaryPolicy",
                    "PartialEvidencePolicy", "RecoveryClockPolicy", "DurationBoundaryConvention",
                    "ObjectiveComparisonPolicy",
                ],
                "error_contracts": [
                    "AcceptanceEvidenceMissing", "ClockEvidenceInvalid", "DependencyEvidenceIncomplete",
                    "DisruptionReferenceMissing", "DurationOverflow", "MeasurementProfileUnsupported",
                    "ObjectiveEditionMismatch", "RecoveredCutIncomparable", "RecoveryScopeMismatch",
                    "ResourceBudgetExceeded", "RpoUnmeasurable", "RtoUnmeasurable",
                ],
                "laws": [
                    "A declared RPO or RTO is an objective, not evidence that it was achieved.",
                    "RPO identifies a required recovered point/cut relative to a disruption; an achieved recovery-point distance is computed only under an explicit ordered-cut measurement profile.",
                    "RTO and achieved recovery duration bind named start and service-acceptance end occurrences; backup, restore-job or process duration is not substituted by proximity.",
                    "Source cut, backup cut, restored cut, dependency readiness and accepted recovered-service cut never alias.",
                    "An attainment outcome binds one immutable recovery-scope edition, objective-set edition, disruption occurrence, recovered cut, dependency graph, clock evidence and measurement policy.",
                    "Missing or incomparable cuts, clocks, dependencies or acceptance evidence yield an inconclusive/partial outcome or typed refusal, never a fabricated pass.",
                    "Measurement over a covered subset cannot claim whole-scope attainment; every excluded dependency remains a typed residual.",
                    "A clean-room exercise measurement is evidence for that exact exercised occurrence and does not prove future incident performance.",
                    "Business impact, maximum tolerable downtime, incident declaration and service acceptance criteria remain imported authority and are never invented here.",
                    "Identical frozen inputs, ordered cuts, clock evidence and policies produce the same measurement and canonical evidence digest.",
                ],
                "oracles": [
                    "nist-rpo-rto-definition-fixtures", "declared-versus-achieved-negative-twins",
                    "ordered-cut-distance-properties", "monotonic-duration-boundary-fixtures",
                    "dependency-completeness-and-residual-conservation", "clock-skew-and-uncertainty-cases",
                    "partial-scope-no-strengthening-property", "cross-implementation-differential",
                ],
                "resource_contracts": [
                    "Finite dependency nodes, cut observations, clock events, evidence bytes and findings are required; overflow, deadline or budget exhaustion returns a typed refusal."
                ],
                "compatibility": [
                    "Objective-set, recovery-scope, measurement-profile, ordered-cut and clock-evidence editions are independently versioned; a semantic change invalidates affected attainment evidence."
                ],
                "removal_seams": [
                    "Pure evaluator and ordered-cut/duration traits are provider-neutral; optional proposal providers can be removed without changing measurement or promotion behavior."
                ],
            })
        if source_slug == "lib.index_mutation":
            rows[-1].update({
                "public_types": [
                    "AcknowledgementScope", "ExpectedIndexState", "IdempotencyKey",
                    "IndexDocumentId", "IndexEdition", "IndexId", "IndexMutation",
                    "IndexMutationBatch", "IndexMutationId", "IndexMutationOperation",
                    "MutationAttempt", "MutationFrontier", "MutationOrderToken",
                    "MutationReceipt", "MutationRefusal", "MutationResidual",
                    "ReplicationAcknowledgement", "SourceRevisionRef", "WriterEpoch",
                ],
                "public_traits": [
                    "IndexMutationAdmitter", "IndexMutationPort",
                    "MutationAcknowledgementClassifier", "MutationFrontierProjector",
                    "MutationOutcomeReconciler",
                ],
                "configuration_contracts": [
                    "MutationOrderPolicy", "MutationPreconditionPolicy",
                    "MutationAcknowledgementPolicy", "MutationBatchAtomicityPolicy",
                    "MutationIdempotencyPolicy", "UnknownMutationOutcomePolicy",
                    "IndexDeletePolicy", "ReplicaAcknowledgementPolicy",
                ],
                "error_contracts": [
                    "AcknowledgementScopeInsufficient", "BatchAtomicityUnsupported",
                    "IdempotencyConflict", "IndexEditionMismatch", "MutationBudgetExceeded",
                    "MutationConflict", "MutationOutcomeUnknown", "OrderTokenIncomparable",
                    "ReplicaAcknowledgementIncomplete", "SourceRevisionConflict",
                    "StaleWriterEpoch", "UnsupportedMutationOperation",
                ],
                "laws": [
                    "Source document occurrence, projected index document, mutation intent, mutation attempt, acknowledgement, durable commit, search visibility cut and query result are distinct facts.",
                    "Every mutation binds one stable index id and immutable index edition, stable document id, source revision reference, operation, writer/primary epoch, idempotency identity and expected-state precondition.",
                    "A provider-native sequence is comparable only inside its declared writer, primary or partition epoch unless an independently proved order relation says otherwise.",
                    "A successful acknowledgement states only its exact admitted, journaled, committed and replica scope; it never implies search visibility or source-document acceptance.",
                    "Add, replace, delete and no-op are explicit operations. A provider implementation that realizes replace as delete-plus-add cannot silently weaken the selected batch or document atomicity contract.",
                    "A retried mutation with the same idempotency identity returns the same terminal outcome or enters reconciliation; an unknown outcome blocks blind repetition as a new mutation.",
                    "A stale expected source revision, index head, epoch or sequence yields a typed conflict and cannot overwrite a later admitted mutation.",
                    "Delete acknowledgement creates an editioned mutation/tombstone fact; verified disappearance requires a later visibility proof and explicit residuals for retained readers, replicas and caches.",
                    "Batch partiality is ordered and receipted per member; an all-or-none claim is permitted only for a provider profile that proves it at the declared scope.",
                    "Flush, journal sync, stable commit, replication and visibility remain independently observable occurrences and may be ordered differently by different providers.",
                    "Background segment merge or compaction may change physical representation but cannot create a source mutation, change logical mutation order or strengthen an acknowledgement.",
                    "Identical frozen intent, precondition, epoch, policy and observed provider outcome produce the same canonical receipt and residual set.",
                ],
                "oracles": [
                    "source-projection-mutation-ack-visibility-negative-twins",
                    "writer-epoch-and-sequence-comparability-properties",
                    "optimistic-conflict-and-stale-primary-fixtures",
                    "idempotency-retry-and-unknown-outcome-state-machine",
                    "batch-atomicity-and-ordered-partial-fixtures",
                    "delete-tombstone-versus-disappearance-negative-twins",
                    "acknowledgement-durability-replication-matrix",
                    "lucene-update-delete-and-commit-fixtures",
                    "elasticsearch-sequence-primary-term-fixtures",
                    "crash-recovery-and-fault-injection", "cross-implementation-differential",
                ],
                "resource_contracts": [
                    "Finite mutation bytes, batch members, in-flight attempts, reconciliation probes, retained receipts, journal/commit work and deadline are required; exhaustion refuses before inventing an acknowledgement."
                ],
                "concurrency": [
                    "Expected-state guards and epoch-scoped order tokens prevent stale writers from overwriting later mutations.",
                    "Concurrent mutation outcomes remain a partial order unless the selected writer/primary profile proves a total order at the declared scope.",
                ],
                "cancellation": [
                    "Caller cancellation stops waiting, not necessarily the provider effect; the attempt remains pending or unknown until a terminal receipt or reconciliation evidence exists."
                ],
                "compatibility": [
                    "Index edition, mutation carrier, operation algebra, acknowledgement, order-token, batch and replica-profile editions evolve independently; changing any meaning invalidates affected receipts."
                ],
                "removal_seams": [
                    "Canonical mutation state and receipts are independent of source projection, search engine, transport, journal, replication and segment implementation; provider adapters are removable."
                ],
            })
        if source_slug == "lib.search_visibility":
            rows[-1].update({
                "public_types": [
                    "IndexMutationFrontier", "PartialVisibility", "PublicationAttempt",
                    "ReaderSnapshotId", "SearchVisibilityCut", "ShardVisibilityCut",
                    "VisibilityDeadline", "VisibilityGeneration", "VisibilityReceipt",
                    "VisibilityRefusal", "VisibilityRequestId", "VisibilityResidual",
                ],
                "public_traits": [
                    "DeleteDisappearanceVerifier", "SearchVisibilityObserver",
                    "SearchVisibilityPublisher", "VisibilityCutComparator",
                    "VisibilityOutcomeReconciler", "VisibilityWaiter",
                ],
                "configuration_contracts": [
                    "VisibilityPublicationPolicy", "VisibilityCutShapePolicy",
                    "VisibilityPartialityPolicy", "ReadAfterWritePolicy",
                    "VisibilityDurabilityRelationPolicy", "DeleteDisappearancePolicy",
                    "VisibilityCapacityPolicy",
                ],
                "error_contracts": [
                    "DeleteDisappearanceUnproved", "IndexEditionMismatch",
                    "MutationFrontierIncomparable", "ReaderSnapshotExpired",
                    "RefreshListenerCapacityExceeded", "ShardVisibilityIncomplete",
                    "VisibilityBudgetExceeded", "VisibilityDeadlineExceeded",
                    "VisibilityOutcomeUnknown", "VisibilityPublicationFailed",
                ],
                "laws": [
                    "Mutation admission, mutation acknowledgement, journal durability, stable commit, refresh/reader publication and search visibility are non-collapsible occurrences.",
                    "A SearchVisibilityCut binds one immutable index edition, shard-topology edition, per-shard mutation frontier, reader/searcher snapshot identities, publication occurrence and explicit coverage/residual set.",
                    "A single scalar visibility token cannot claim a distributed cut unless it proves all targeted shard and replica frontiers represented by that token.",
                    "Refresh may make a mutation searchable without a stable index commit, while a durable commit may exist without the currently serving searcher seeing it; neither fact strengthens the other.",
                    "A visibility waiter returns success only when the exact required mutation frontier is observed in the declared target scope; timeout, cancellation or listener exhaustion is not visibility.",
                    "Already-running searches retain their bound point-in-time reader/searcher cut and are not retroactively changed by a later publication.",
                    "Missing shards or replicas yield typed partial coverage, wait or refusal according to policy; they never silently become a complete visibility claim.",
                    "Delete disappearance is proven only beyond the delete frontier for every required searchable cut, with retained-reader, replica and cache residuals explicit.",
                    "Background merges may replace segments while preserving the logical visible frontier; merge completion is not a new business mutation or visibility guarantee by itself.",
                    "Read-your-writes is scoped to an exact mutation identity/frontier, index edition, target shard set and publication receipt; session proximity is not proof.",
                    "Publication frequency, refresh listeners, waiting callers, retained readers, shards, receipts and deadlines are finite and refusal is explicit under exhaustion.",
                    "Identical mutation frontier, reader state, topology, policy, clock evidence and observations produce the same canonical visibility verdict and residuals.",
                ],
                "oracles": [
                    "ack-commit-refresh-visibility-four-way-negative-twins",
                    "per-shard-frontier-vector-order-properties",
                    "point-in-time-reader-refresh-fixtures",
                    "soft-commit-hard-commit-open-searcher-matrix",
                    "wait-for-refresh-timeout-and-capacity-state-machine",
                    "partial-shard-and-replica-coverage-fixtures",
                    "delete-disappearance-retained-reader-properties",
                    "merge-preserves-logical-visible-frontier",
                    "read-your-writes-scope-negative-twins",
                    "crash-partition-and-delayed-refresh-fault-injection",
                    "cross-implementation-differential",
                ],
                "resource_contracts": [
                    "Finite target shards, replica scope, frontier entries, refresh listeners, retained reader snapshots, waiting callers, evidence bytes and deadline are required; exhaustion yields typed partial, refused or unknown."
                ],
                "concurrency": [
                    "Visibility cuts form a per-shard frontier partial order; publication and query binding retain exact reader/searcher generations.",
                    "Concurrent refresh, commit, merge, replica recovery and query execution are separate occurrences whose observed order is retained in evidence."
                ],
                "cancellation": [
                    "Cancelling a waiter does not prove the refresh was cancelled or completed; provider work is reconciled and the caller receives a separate cancellation/unknown receipt."
                ],
                "compatibility": [
                    "Visibility-cut, frontier, topology, publication, reader-snapshot, partiality and durability-relation editions evolve independently and invalidate affected evidence."
                ],
                "removal_seams": [
                    "Canonical visibility evidence is independent of mutation transport, refresh API, Lucene reader, shard router, search executor, cache and durable storage provider."
                ],
            })
        if source_slug == "lib.cache_fill_coordination":
            rows[-1].update({
                "public_types": [
                    "CacheEntryCandidate", "CoalescingPolicy", "CoordinationBudget",
                    "FillAttempt", "FillEquivalenceKey", "FillGenerationId", "FillLeaderLease",
                    "FillOutcome", "FillReceipt", "FillRefusal", "FencingToken", "SourceCutRef",
                    "StaleServeDecision", "WaiterId", "WaiterRegistration",
                ],
                "public_traits": [
                    "CacheFillCoordinator", "FillLeasePort", "FillOutcomePublisher",
                    "StaleEligibilityEvaluator", "WaiterRegistry",
                ],
                "configuration_contracts": [
                    "FillLeadershipPolicy", "FollowerPolicy", "SharedFillCancellationPolicy",
                    "FillFailurePolicy", "LateCompletionPolicy", "StaleWhileFillPolicy",
                    "FillCapacityPolicy", "BackoffAndJitterPolicy",
                ],
                "error_contracts": [
                    "CoordinatorUnavailable", "EquivalenceKeyInvalid", "FillBudgetExceeded",
                    "FillGenerationClosed", "FillOutcomeIneligible", "FillOutcomeUnknown",
                    "FencingTokenStale", "LeaderLeaseExpired", "SourceCutIncompatible",
                    "StaleServingForbidden", "WaitDeadlineExceeded", "WaiterCapacityExceeded",
                ],
                "laws": [
                    "At most one admitted leader may publish for one coordinator scope, fill-equivalence key and generation; distributed leadership requires a monotonically fenced lease.",
                    "Tenant, principal/policy partition, semantic request identity, source dependency cut and result contract participate in equivalence; a convenient string key is not proof of safe sharing.",
                    "A follower receives a shared outcome only when that outcome is reusable for its own exact request and authority scope; otherwise it is detached, forwarded, served eligible stale or refused.",
                    "Leader disappearance, timeout, lease expiry or coordinator failure never implies fill success or cache publication; an exact outcome or unknown/failure receipt is required.",
                    "Cancelling one waiter detaches that waiter and does not cancel shared work unless the selected policy and remaining-waiter state explicitly permit it.",
                    "An expired or superseded leader cannot publish with a stale fencing token; late work is retained as evidence or reconciled under an explicit policy.",
                    "Leader failure cannot trigger unconstrained duplicate retries; a new generation begins only after the prior generation is closed or reconciled and admission/backoff budgets pass.",
                    "Stale data is served during a fill only when the upstream freshness and policy contract permits it; the receipt records age, stale reason and revalidation generation.",
                    "The coordinator owns in-flight identity and delivery, not cached-value truth, cache persistence, request equivalence, authorization, source execution or source mutation.",
                    "Every key, generation, leader, waiter, lease, deadline, retry and retained receipt is finite and tenant/policy scoped; exhaustion yields a typed refusal.",
                    "Identical state, command, clock event, policy and fencing inputs yield the same state transition and receipt; runtime scheduling order remains explicit evidence.",
                ],
                "oracles": [
                    "single-leader-per-key-generation-state-machine", "fencing-aba-and-late-completion-model",
                    "follower-eligibility-and-authority-negative-twins", "waiter-cancellation-interleavings",
                    "leader-failure-and-unknown-outcome-reconciliation", "retry-storm-capacity-property",
                    "rfc9111-collapse-and-reuse-fixtures", "rfc5861-stale-bound-fixtures",
                    "linearizability-history-check", "randomized-schedule-and-fault-injection",
                    "cross-implementation-differential",
                ],
                "resource_contracts": [
                    "Finite active keys, generations, leaders, waiters, lease duration, wait duration, retry count, receipt bytes and coordination memory are required; exhaustion refuses without starting duplicate work."
                ],
                "concurrency": [
                    "State transitions are linearized per equivalence key and generation; cross-key concurrency is independent except for explicit global budgets.",
                    "Fencing tokens prevent ABA and stale-leader publication across lease expiry, failover and partition recovery.",
                ],
                "cancellation": [
                    "Waiter cancellation is separately receipted from shared-fill cancellation; last-waiter and deadline behavior is selected explicitly."
                ],
                "compatibility": [
                    "Equivalence-key, policy, state-machine, receipt and fencing editions are independently versioned; changing any sharing or completion meaning invalidates affected evidence."
                ],
                "removal_seams": [
                    "Coordinator state machine is independent of cache store, lock/lease provider and source executor; each adapter is replaceable under the same fencing, receipt and fault laws."
                ],
            })
        if source_slug == "lib.virtual_relation_identity":
            rows[-1].update({
                "public_types": [
                    "DefinitionCarrier", "DefinitionDigest", "DefinitionResidual",
                    "OutputSchemaContract", "ParameterContract", "QualifiedRelationAlias",
                    "RelationCompatibility", "SecurityExecutionProfile", "SourceBinding",
                    "SourceBindingSet", "VirtualDependencyContract", "VirtualRelationDefinition",
                    "VirtualRelationEdition", "VirtualRelationId", "VirtualRelationRefusal",
                ],
                "public_traits": [
                    "DefinitionCanonicalizer", "SourceBindingResolver",
                    "VirtualRelationCompatibility", "VirtualRelationValidator",
                ],
                "configuration_contracts": [
                    "DefinitionCarrierPolicy", "SourceBindingPolicy", "OutputCompatibilityPolicy",
                    "SecurityExecutionPolicy", "ParameterBindingPolicy", "NameResolutionPolicy",
                ],
                "error_contracts": [
                    "AliasAmbiguous", "DefinitionCarrierUnsupported", "DefinitionNonCanonical",
                    "DependencyCycle", "OutputSchemaIncompatible", "ParameterBindingImplicit",
                    "SecurityProfileMissing", "SourceBindingAmbiguous", "SourceEditionUnavailable",
                    "VirtualRelationIdentityMissing",
                ],
                "laws": [
                    "VirtualRelationId is stable identity; qualified alias, provider object id, source path and definition digest are distinct and may change only through explicit relations.",
                    "A published VirtualRelationEdition is immutable and binds one definition carrier/edition, output-schema contract, source-binding set, parameter contract, security-execution profile and canonical digest.",
                    "A saved query, provider view, virtual relation and materialized result are distinct identities; materialization never becomes source truth or changes the virtual definition.",
                    "Definer, invoker and external-policy execution modes never alias and every delegated authority is explicit and editioned.",
                    "Every source reference resolves to a stable foreign identity and an explicit binding-time/edition policy; a path or display name is not identity proof.",
                    "Replacing a provider view cannot mutate an existing published semantic edition; it proposes a new edition and a separately adjudicated alias transition.",
                    "Definition translation retains carrier and feature residuals; provider SQL or AST is never silently treated as a canonical plan.",
                    "Output compatibility is an explicit relation over names, order, types, nullability, semantics and policy—not a provider's create-or-replace success.",
                    "Identical frozen carriers, bindings, decisions and editions produce the same canonical definition and digest.",
                ],
                "oracles": [
                    "identity-alias-provider-path-negative-twins", "definition-canonicalization-property",
                    "source-binding-ambiguity-and-cycle-fixtures", "output-schema-compatibility-matrix",
                    "definer-invoker-authority-negative-twins", "provider-view-roundtrip-with-loss-report",
                    "rename-and-materialization-identity-properties", "cross-implementation-differential",
                ],
                "compatibility": [
                    "Definition carrier, output schema, source binding, security profile, parameter and public relation editions evolve independently; compatibility is a directional evidence-backed relation."
                ],
                "removal_seams": [
                    "Pure identity/definition core is independent of namespace catalog, SQL parser, query engine, source connector, materialization store and optional proposal provider."
                ],
            })
        if source_slug == "lib.virtual_relation_lifecycle":
            rows[-1].update({
                "public_types": [
                    "AliasHead", "DependencyImpact", "DeprecationNotice", "LifecycleCommand",
                    "LifecycleReceipt", "LifecycleRefusal", "PublishedVirtualRelationEdition",
                    "RecallDecision", "RetirementTombstone", "SupersessionRelation",
                    "VirtualRelationDraft", "VirtualRelationLifecycleState",
                ],
                "public_traits": [
                    "DependencyImpactEvaluator", "VirtualRelationLifecycle",
                    "VirtualRelationPublicationPolicy", "VirtualRelationRecallPolicy",
                ],
                "configuration_contracts": [
                    "PublicationAuthorityPolicy", "DependencyBreakPolicy", "InFlightDispositionPolicy",
                    "DeprecationPolicy", "RecallPolicy", "RetirementPolicy",
                ],
                "error_contracts": [
                    "ActiveDependencyBlocksRetirement", "AliasAdvanceConflict", "DependencyBreakUnresolved",
                    "InFlightDispositionMissing", "InvalidLifecycleTransition", "PublicationAuthorityMissing",
                    "RecallAuthorityMissing", "RetentionNotElapsed", "UnknownRelationEdition",
                ],
                "laws": [
                    "Only a draft may be published, and publication produces a new immutable edition plus an authority-bound receipt.",
                    "Publishing an edition, advancing an alias, deprecating, recalling and retiring are separate decisions and occurrences.",
                    "Supersession preserves the prior edition and records a directional relation; it never rewrites historical invocations or evidence.",
                    "Recall prevents new binding according to its effective cut and requires an explicit disposition for already-bound invocations.",
                    "Retirement requires dependency, retention and consumer-release evidence or an explicit authority-bound forced tombstone.",
                    "Breaking definition, output, source-binding or security changes cannot inherit an alias without the selected compatibility and migration policy.",
                    "Provider rename, replace or drop success is an implementation occurrence, not semantic publication, recall or retirement authority.",
                    "Every transition is total: legal next state plus receipt, or a typed refusal with dependency and authority evidence.",
                ],
                "oracles": [
                    "total-lifecycle-state-machine", "immutable-publication-history-property",
                    "alias-compare-and-swap-concurrency-model", "dependency-break-negative-twins",
                    "recall-effective-cut-and-inflight-fixtures", "retirement-retention-and-dependency-property",
                    "provider-ddl-versus-semantic-lifecycle-negative-twins", "cross-implementation-differential",
                ],
                "compatibility": [
                    "Lifecycle state-machine, authority, alias, dependency and in-flight disposition editions evolve independently and invalidate affected transition evidence."
                ],
                "removal_seams": [
                    "Pure transition/policy core is independent of catalog persistence, provider DDL, notification, query cancellation, migration executor and optional proposal provider."
                ],
            })
    assert set(LIBRARY_PRIMARY_OWNERS) == {
        row["candidate_id"].removeprefix("persistence.boundary.")
        for row in boundaries if row["record_kind"] in LIBRARY_KINDS
    }
    return sorted(rows, key=lambda row: row["library_id"])


PROFILE_CAPABILITIES = {
    "append_only_analytical_table": [
        "object_namespace.put_object", "object_namespace.get_object_range", "columnar_file.encode_columnar_file",
        "schema_evolution.validate_schema_change", "partition_evolution.derive_partition_tuple", "snapshot_state.construct_snapshot",
        "append_mutation.commit_append", "commit_protocol.commit_table_state", "manifest_inventory.scan_manifests"
    ],
    "mutable_lake_table": [
        "object_namespace.conditional_replace", "row_level_mutation.plan_row_change", "row_level_mutation.write_row_delta",
        "row_level_mutation.commit_row_change", "isolation_conflicts.detect_table_conflict", "merge_on_read.merge_at_read",
        "delete_materialization.apply_deletes", "compaction.execute_compaction", "change_feed.read_change_feed"
    ],
    "regulated_immutable_analytics": [
        "retention_immutability.place_hold", "retention_immutability.enforce_retention", "integrity.verify_checksum",
        "backup.capture_full_backup", "restore.verify_restored_cut", "snapshot_refs.create_snapshot_ref",
        "snapshot_expiry.verify_reachability", "physical_deletion.authorize_reclamation"
    ],
    "scientific_array": [
        "scientific_array_store.create_array", "scientific_array_store.write_chunk", "scientific_array_store.read_array_slice",
        "array_chunk_format.encode_array_chunk", "array_chunk_format.decode_array_region", "compression.compress_bytes",
        "integrity.verify_checksum", "object_namespace.get_object_range"
    ],
    "low_latency_olap": [
        "olap_segment_store.publish_segment", "olap_segment_store.load_segment", "olap_serving.assign_segment",
        "olap_serving.route_segment_query", "olap_serving.detect_partial_result", "index_build.build_index",
        "serving_cutover.cutover_serving_traffic", "freshness_contract.measure_freshness"
    ],
    "realtime_time_series": [
        "time_series_store.append_sample", "time_series_store.query_time_range", "time_series_store.downsample_series",
        "incremental_materialization.apply_incremental_change", "time_series_serving.combine_realtime_tail",
        "freshness_contract.enforce_staleness_budget", "backup.capture_incremental_backup"
    ],
    "transactional_application": [
        "relational_store.execute_transaction", "relational_store.enforce_constraint", "relational_store.read_consistent_cut",
        "replication.replicate_write", "backup.capture_incremental_backup", "restore.restore_cut", "quota_cost.reserve_capacity"
    ],
    "search_serving": [
        "search_store.index_document", "search_store.refresh_search_cut", "index_build.build_index",
        "search_serving.route_search_request", "search_serving.merge_search_results", "search_serving.report_search_cut",
        "serving_cutover.rollback_serving_edition"
    ],
    "vector_similarity_serving": [
        "vector_store.upsert_vector", "vector_store.build_vector_index", "vector_store.search_neighbors",
        "vector_serving.route_vector_search", "vector_serving.search_vector_index", "vector_serving.report_approximation",
        "serving_cutover.cutover_serving_traffic"
    ],
    "external_data_share": [
        "share_publication.create_share", "share_publication.publish_table_cut", "share_subscription.subscribe_share",
        "presigned_delivery.issue_presigned_access", "presigned_delivery.download_shared_file", "share_publication.revoke_share",
        "change_feed.checkpoint_change_consumer"
    ],
    "federated_analytics": [
        "federated_namespace.mount_foreign_namespace", "federated_namespace.resolve_foreign_object",
        "pushdown.negotiate_pushdown", "pushdown.execute_remote_operation", "pushdown.verify_pushdown_result",
        "federated_consistency.acquire_source_cuts", "federated_consistency.report_cross_source_skew"
    ],
    "portable_supplier_exit": [
        "data_portability.plan_portable_export", "data_portability.export_portable_cut", "data_portability.verify_independent_import",
        "table_format_migration.assess_format_compatibility", "table_format_migration.verify_migrated_table",
        "bulk_result_delivery.publish_result_manifest", "catalog_migration.verify_catalog_cutover"
    ],
}


def build_compiler_mappings(capabilities: list[dict[str, Any]]) -> list[dict[str, Any]]:
    cap_by_id = {row["capability_id"]: row for row in capabilities}
    rows: list[dict[str, Any]] = []
    offer_by_cap: dict[str, str] = {}
    provider_by_surface = {
        "storage": "provider_class.persistence.storage_runtime",
        "file_format": "provider_class.persistence.format_kernel",
        "table": "provider_class.persistence.table_runtime",
        "catalog": "provider_class.persistence.catalog_runtime",
        "maintenance": "provider_class.persistence.maintenance_runtime",
        "serving": "provider_class.persistence.serving_runtime",
        "sharing": "provider_class.persistence.exchange_runtime",
        "federation": "provider_class.persistence.federation_runtime",
        "assurance": "provider_class.persistence.assurance_runtime",
    }
    required_ids = {expand_capability_ref(item) for values in PROFILE_CAPABILITIES.values() for item in values}
    for cap_id in sorted(required_ids):
        cap = cap_by_id[cap_id]
        suffix = cap_id.removeprefix("persistence.capability.")
        offer_id = f"offer.persistence.{suffix}.abstract"
        offer_by_cap[cap_id] = offer_id
        rows.append({
            "record_kind": "capability_offer",
            "offer_id": offer_id,
            "edition": EDITION,
            "status": "candidate",
            "provider_class_ref": provider_by_surface[cap["surface"]],
            "capability_ref": cap_id,
            "guarantee_claims": cap["guarantees"],
            "decision_refs": cap["decision_refs"],
            "limits_to_probe": cap["resource_dimensions"],
            "qualification_probes": cap["qualification_probes"],
            "exclusions": ["not a deployed occurrence", "not qualified by a class label", "no inferred support beyond the exact capability"],
            "evidence_refs": cap["evidence_refs"],
            "gaps": ["deployment occurrence, version, target, numerical limits and current conformance receipts are required before selection"]
        })
    for profile, shorthands in PROFILE_CAPABILITIES.items():
        requirement_refs = []
        eligible_offer_refs = []
        for shorthand in shorthands:
            cap_id = expand_capability_ref(shorthand)
            suffix = cap_id.removeprefix("persistence.capability.")
            req_id = f"requirement.persistence.profile.{profile}.{suffix}"
            requirement_refs.append(req_id)
            eligible_offer_refs.append(offer_by_cap[cap_id])
            cap = cap_by_id[cap_id]
            rows.append({
                "record_kind": "capability_requirement",
                "requirement_id": req_id,
                "edition": EDITION,
                "status": "declared",
                "subject_ref": f"profile.persistence.{profile}",
                "capability_ref": cap_id,
                "required_guarantees": cap["guarantees"] + ["all selected decision values supported", "finite resource envelope"],
                "decision_refs": cap["decision_refs"],
                "criticality": "blocking",
                "binding_phase": "physical_binding",
                "evidence_gates": ["exact capability conformance", "target/version compatibility", "fault and retry receipt", "current limit probe"],
                "fallback_law": "refuse",
                "gaps": ["intent-specific numerical SLO and budget values are supplied by the vertical/application declaration"]
            })
        rows.append({
            "record_kind": "binding_rule",
            "binding_rule_id": f"binding_rule.persistence.profile.{profile}",
            "edition": EDITION,
            "status": "declared",
            "requirement_refs": requirement_refs,
            "eligible_offer_refs": eligible_offer_refs,
            "compatibility_clauses": [
                "capability identity and edition match exactly",
                "every required decision value is supported without semantic downgrade",
                "provider target, format/protocol feature set and authority scope are compatible",
                "resource/SLO envelope is feasible under the declared finite budget",
                "all required conformance and recovery evidence is current"
            ],
            "rejection_clauses": [
                "provider or product name used as capability proof",
                "unknown format feature, consistency, deletion, compression or retry semantics",
                "missing authority, destructive-operation safety or recovery evidence",
                "unbounded resource use or unsupported cancellation",
                "hidden provider default changes persisted meaning"
            ],
            "selection_law": "Eliminate incompatible offers, qualify remaining deployments, then choose by the declaration's ordered cost/SLO/portability policy while retaining rejected alternatives.",
            "receipts": ["requirement-offer matrix", "selected decisions", "qualification results", "resource feasibility", "rejected alternatives", "invalidation triggers"],
            "invalidation_triggers": ["format/protocol edition change", "provider version or target change", "decision change", "evidence expiry", "limit or SLO breach", "authority revocation"],
            "residual_gap_law": "Any blocking unresolved capability, decision, authority, resource or evidence gap refuses compilation; degradable gaps require an explicit typed degradation accepted by authority."
        })
    rows.append({
        "record_kind": "compiler_gap",
        "gap_id": "gap.persistence.unqualified_deployment",
        "edition": EDITION,
        "status": "open",
        "subject_ref": "provider_class.persistence.any",
        "blocking": True,
        "missing_contracts": ["deployment occurrence", "observed numerical limits", "target/version identity", "conformance receipts", "recovery evidence"],
        "resolution_condition": "Bind and qualify a concrete deployment occurrence against every selected requirement and evidence gate.",
        "prohibited_fallbacks": ["select by vendor name", "inherit undocumented defaults", "treat an official format implementation as a qualified service"]
    })
    return rows


INNOVATION_SEEDS = [
    ("nvme_zns", 2021, "NVMe 2.0 modular specifications and Zoned Namespace command set made placement/endurance semantics more explicit at the device boundary.", ["nvme.spec"], ["Expose device write constraints and endurance as provider capabilities, never as filesystem assumptions."]),
    ("flight_sql", 2022, "Flight SQL introduced an Arrow-native wire protocol for SQL metadata, statements and columnar result delivery.", ["arrow.flight_sql_release", "arrow.flight_sql"], ["Separate query protocol from database API, query engine and storage product."]),
    ("iceberg_rest", 2022, "Iceberg 0.14 introduced a common REST catalog client using change-based commits, replacing the need for every client language to implement every catalog integration.", ["iceberg.releases", "iceberg.rest"], ["Compile catalog protocol and server implementation independently; retain commit requirements and credential modes."]),
    ("zarr_v3_spec", 2022, "Zarr v3 reached a core-protocol feature freeze with explicit extension points for chunk grids, codecs, data types and stores.", ["zarr.v3_2022", "zarr.v3"], ["Represent codec chains and storage mappings as typed decisions, not format-name defaults."]),
    ("delta_deletion_vectors", 2023, "Delta deletion vectors added a merge-on-read row-delete representation that defers file rewrite cost.", ["delta.deletion_vectors", "delta.protocol"], ["Model mutation representation and delete-materialization debt separately from logical delete semantics."]),
    ("delta_table_features", 2023, "Delta table features made reader and writer protocol capabilities individually negotiable.", ["delta.features", "delta.protocol"], ["Require exact feature-set negotiation; never infer compatibility from one protocol number."]),
    ("delta_liquid_clustering", 2023, "Liquid clustering introduced incrementally evolvable physical clustering distinct from static partitioning.", ["delta.liquid"], ["Keep logical partition evolution and physical clustering in separate bounded contexts and decisions."]),
    ("delta_kernel", 2023, "Delta Kernel exposed protocol interpretation behind reusable engine-neutral APIs.", ["delta.kernel"], ["Treat table kernels as runtime libraries beneath products, with conformance and removal seams."]),
    ("adbc", 2023, "ADBC 1.0 introduced a provider-neutral Arrow-native database client API.", ["arrow.adbc"], ["Bind client API independently from server protocol and provider driver."]),
    ("paimon_primary_key", 2025, "Paimon 1.0 combined primary-key merge semantics with deletion vectors, bitmap file indexes, object tables and format-table interoperability.", ["paimon.release1", "paimon.spec", "paimon.primary_key"], ["Expose primary-key merge engine, sequence, index, deletion-vector and changelog decisions instead of treating all tables as append-only."]),
    ("influx_object_parquet", 2023, "InfluxDB 3 separated ingest/query components and persisted time-series data through WAL and Parquet on object storage.", ["influx.storage", "influx.durability"], ["Model WAL durability, object persistence, compaction and query freshness as separate bindings."]),
    ("xtable_translation", 2024, "Apache XTable developed metadata translation among Iceberg, Delta and Hudi without copying data files.", ["xtable.interop", "xtable.limitations"], ["Translation is an operation with source authority, checkpoints, feature-loss reports and reconciliation—not a universal format."]),
    ("s3_conditional_writes", 2024, "S3 added create-if-absent and later ETag-guarded conditional write primitives.", ["s3.conditional_release", "s3.conditional"], ["Probe the exact conditional primitive before using object storage as table commit authority."]),
    ("postgres_incremental_backup", 2024, "PostgreSQL 17 added incremental physical backups and WAL summaries with an explicit combine step.", ["postgres.incremental"], ["Backup-chain capture and restore proof remain separate products and evidence obligations."]),
    ("hudi_1_concurrency_indexing", 2024, "Hudi 1.0 released non-blocking concurrency control, multiple secondary-index types, partial updates and additional base-file format support.", ["hudi.release1", "hudi.spec", "hudi.timeline"], ["Concurrency mode, index maintenance, update granularity and base-file representation are independent compiler decisions; release notes also require known-regression gates."]),
    ("polaris_open_catalog", 2025, "Apache Polaris published versioned releases of an open Iceberg REST catalog implementation.", ["polaris.releases", "polaris.docs"], ["Open implementation evidence supports substitutability but does not collapse protocol, deployment and product boundaries."]),
    ("unity_open_api", 2024, "Unity Catalog published an evolving OpenAPI covering assets, credentials and managed-table commit coordination.", ["unitycatalog.api"], ["Experimental protocol surfaces require edition pinning and cannot be silently treated as stable standards."]),
    ("zarr_python3", 2025, "Zarr-Python 3 delivered v3 support, sharding, extensible stores/codecs and an asynchronous I/O core.", ["zarr.python3", "zarr.sharding"], ["Array representation, codec implementations and provider stores remain separately replaceable."]),
    ("iceberg_v3_row_lineage", 2025, "Iceberg v3 added row lineage and deletion-vector semantics to the adopted table specification.", ["iceberg.v3", "iceberg.table"], ["Feature negotiation must distinguish row identity/lineage from business identity and preserve reader/writer compatibility."]),
    ("duckdb_storage_compatibility", 2024, "DuckDB 1.0 established an explicit storage-format compatibility policy alongside its embedded analytical database milestone.", ["duckdb.release1"], ["A persisted implementation format needs edition and compatibility relations distinct from query/API compatibility and product branding."]),
    ("polaris_tlp", 2026, "Apache Polaris graduated to an Apache top-level project, strengthening independent-governance evidence for an Iceberg REST implementation.", ["polaris.tlp"], ["Project maturity informs provider qualification; it does not prove a deployment's SLO or security posture."]),
    ("iceberg_v3_implementation", 2026, "The Go implementation added deletion-vector read/write and row-lineage support for Iceberg v3.", ["iceberg_go_060", "iceberg.v3"], ["A format feature is selectable only when both required readers and writers provide current conformance receipts."]),
    ("iceberg_remote_planning_idempotency", 2026, "Iceberg 1.11 added remote scan planning, REST-mutation idempotency keys and metadata-cache ETag support.", ["iceberg.release_111", "iceberg.rest"], ["Plan authority, mutation deduplication and cache revalidation require separate protocol decisions and receipts."]),
    ("durable_incremental_materialization", 2021, "Operational systems documented continuously maintained durable materializations separately from cluster-local serving indexes and real-time aggregate tails.", ["materialize.views", "timescale.aggregate"], ["Distinguish a durable materialization, a serving index and a virtual view, including their different recovery and sharing laws."]),
    ("open_table_interoperability", 2024, "Open table formats, catalog protocols and translation tools created practical multi-engine substitution paths.", ["iceberg.rest", "xtable.interop", "polaris.docs"], ["Portability requires exact feature intersections, history treatment and exit verification, not merely common Parquet files."]),
    ("s3_express_append", 2024, "S3 Express One Zone added append-to-object with offset preconditions, making a low-latency object a possible log carrier within explicit zonal, request-cost and part-count limits.", ["s3.express_append_release", "s3.express_append"], ["Compile appendability, locality, part limit, offset conflict, request price and rollover separately from generic object-store durability."]),
    ("chroma_wal3", 2026, "Chroma documented a pure object-storage WAL using conditional writes, per-collection prefixes, asynchronous indexing, index-plus-tail reads and a composable setsum integrity proof.", ["chroma.wal3", "s3.conditional"], ["Object-native log admission, verification, index consumption, read-your-write tail merging and garbage collection are separate contracts."]),
    ("slatedb_object_native_lsm", 2026, "SlateDB introduced an embedded object-native LSM whose WAL SSTs, compacted SSTs, manifests, checkpoints, forks and distributed compaction are designed around object-store economics.", ["slatedb.introduction", "slatedb.files", "slatedb.source"], ["Compile WAL medium, commit mode, manifest concurrency, cache, compaction and garbage collection independently; a library is not a database service."]),
    ("automq_s3_wal", 2025, "AutoMQ documented a shared-stream architecture that separates a selectable WAL backend from shared object storage and can use an S3-compatible store on the acknowledgement path.", ["automq.s3stream", "automq.s3_wal"], ["WAL backend and main object repository are separate bindings; vendor latency claims remain unqualified until reproduced on the target deployment."]),
    ("btrlog_quorum_archive", 2026, "BtrLog proposed a reusable SSD-quorum log service that acknowledges before asynchronously archiving larger segments to object storage.", ["btrlog.paper"], ["Compile hot commit log and cold object history as distinct media with explicit archive lag, recovery and deletion horizons."]),
    ("milliscale_direct_object_oltp", 2026, "Milliscale demonstrated a research OLTP design that commits directly to low-latency appendable object storage while reducing object-request amplification.", ["milliscale.paper", "s3.express_append"], ["Direct object commit is a workload- and provider-qualified option, not a universal replacement for a quorum WAL."]),
    ("bacchus_shared_storage_htap", 2026, "OceanBase Bacchus proposed stateless compute over an object-native LSM, a service-oriented Paxos append log and independent cache layers for OLTP and OLAP workloads.", ["oceanbase.bacchus"], ["HTAP requires explicit log, cache, object-state, isolation and workload-routing decisions; shared bytes do not establish shared transaction semantics."]),
    ("turso_s3_express_wal", 2026, "Turso documented a write-through architecture that batches WAL entries across many SQLite databases, acknowledges after S3 Express One Zone PUT success, caches on local NVMe and checkpoints into S3 Standard.", ["turso.s3_express", "s3.express_append"], ["Multi-tenant batch admission, zonal commit durability, local cache, checkpoint recovery baseline and cross-class retention are separate compiler bindings."]),
    ("postgres_wal_to_iceberg", 2025, "Supabase documented near-real-time capture of PostgreSQL WAL into Iceberg tables on S3 Tables alongside federated access from PostgreSQL.", ["supabase.s3_tables", "iceberg.table"], ["CDC-to-lakehouse enables operational analytics but requires explicit source position, freshness, schema evolution, delete, replay and reconciliation contracts; it is not identical to HTAP shared-state execution."]),
]


def build_innovations() -> list[dict[str, Any]]:
    source_ids = {slug: f"source.persistence.{slug}" for slug, *_ in SOURCE_SEEDS}
    rows = []
    for slug, year, description, evidence, implications in INNOVATION_SEEDS:
        rows.append({
            "innovation_id": f"innovation.persistence.{slug}",
            "edition": EDITION,
            "status": "researched_candidate",
            "year": year,
            "name": slug.replace("_", " "),
            "non_llm": True,
            "problem_and_innovation": description,
            "evidence_refs": [source_ids[item] for item in evidence],
            "boundary_implications": implications,
            "limitations": ["Year denotes the cited public specification/release milestone, not the first invention of every underlying technique.", "Official project evidence does not establish universal superiority or deployment fitness."],
            "compiler_implications": implications,
            "gaps": ["Independent benchmark, incident and migration evidence remains required before SOTA or provider-selection claims."]
        })
    return rows


OBJECT_LOG_DECISION_AXIS_SEEDS = [
    ("acknowledgement_frontier", "Which exact persisted frontier permits acknowledgement?", ["direct_object_admission", "shared_wal_admission", "quorum_log_commit", "local_source_commit_async_ship", "checkpoint_metadata_commit", "multiple_frontiers_explicit"], "logical_planning", ["chroma.wal3", "automq.s3stream", "neon.architecture", "turso.s3_express"]),
    ("object_mutation_primitive", "Which exact object-store mutation primitive is required?", ["immutable_put", "create_if_absent", "etag_conditional_replace", "append_with_offset", "multipart_upload", "provider_extension", "not_on_ack_path"], "physical_binding", ["s3.conditional", "s3.express_append"]),
    ("writer_coordination", "How are concurrent or failed writers ordered and fenced?", ["single_writer_epoch", "conditional_cas", "lease_and_fence", "consensus_quorum", "transactional_metadata", "source_native_order", "unresolved_refuse"], "logical_planning", ["chroma.wal3", "slatedb.files", "neon.architecture", "materialize.architecture"]),
    ("log_state_materialization", "How does admitted log state become read-optimized state?", ["log_is_read_state", "async_index_plus_tail", "wal_to_sst", "wal_to_page_history", "wal_to_columnar", "barrier_checkpoint", "wal_to_stream_segments", "async_replica_only"], "logical_planning", ["chroma.wal3", "slatedb.files", "neon.architecture", "risingwave.architecture", "s2.architecture"]),
    ("read_freshness", "Which frontier must a read observe and how is lag represented?", ["index_plus_tail", "wait_for_index", "eventual_index_with_bound", "quorum_lsn", "checkpoint_cut", "source_and_replica_frontiers", "archive_restore_only"], "runtime_reconciliation", ["turbopuffer.architecture", "neon.architecture", "materialize.architecture", "risingwave.architecture"]),
    ("batching", "How are records batched before durable object requests?", ["per_transaction", "time_window", "size_window", "cross_tenant", "multi_stream", "adaptive_time_and_size", "provider_managed"], "physical_binding", ["turso.s3_express", "automq.s3_wal", "s2.architecture", "s3.express_append"]),
    ("cache_hierarchy", "Which caches may accelerate reads without becoming authority?", ["none", "memory", "local_nvme_disposable", "zonal_read_through", "page_materialization_cache", "multi_layer_explicit"], "deployment_binding", ["turso.s3_express", "turbopuffer.architecture", "neon.architecture", "s2.architecture"]),
    ("failure_domain", "Which failure domains must survive acknowledgement and recovery?", ["single_zone", "multi_az_quorum", "object_provider_scope", "multi_cloud", "hybrid_log_and_object", "unresolved_refuse"], "deployment_binding", ["s3.express_append", "neon.architecture", "oceanbase.bacchus", "btrlog.paper"]),
    ("metadata_authority", "What makes uploaded bytes reachable and current?", ["object_manifest_cas", "transactional_consensus", "metastore_publication", "stream_metadata", "log_quorum", "source_native_catalog", "none_log_self_describing"], "logical_planning", ["slatedb.files", "materialize.architecture", "quickwit.architecture", "s2.architecture"]),
    ("garbage_collection", "Which proof permits log, object or index reclamation?", ["reachability_proof", "archive_watermark", "index_frontier", "checkpoint_coverage", "retention_horizon", "source_replica_ack", "unresolved_refuse"], "runtime_reconciliation", ["chroma.wal3", "slatedb.files", "btrlog.paper", "s2.architecture"]),
    ("request_economics", "How are object request and byte costs bounded?", ["per_append_budget", "batched_put", "range_read_budget", "object_consolidation", "hybrid_wal_object", "explicit_unbounded_refuse"], "physical_binding", ["s3.express_append", "slatedb.introduction", "automq.s3_wal", "turso.s3_express"]),
    ("recovery_baseline", "Which exact artifacts reconstruct an accepted cut?", ["log_only", "checkpoint_plus_log", "page_history", "object_segments", "analytical_snapshot", "async_backup_lineage", "source_replay_plus_state"], "evidence_verification", ["neon.architecture", "turso.s3_express", "risingwave.architecture", "walrust.source"]),
    ("workload_isolation", "How are transactional, analytical, tenant and maintenance workloads isolated?", ["not_applicable", "tenant_prefix", "agent_group", "compute_pool", "cache_pool", "transaction_analytical_split", "explicit_shared_contention"], "deployment_binding", ["chroma.wal3", "warpstream.architecture", "oceanbase.bacchus", "turso.s3_express"]),
    ("portability_profile", "Which object semantics may the architecture require?", ["s3_standard", "s3_express_directory_bucket", "s3_compatible_subset", "multi_provider_subset", "provider_specific_extension", "abstract_object_port"], "physical_binding", ["s3.conditional", "s3.express_append", "slatedb.source", "risingwave.architecture"]),
]


def build_object_log_decision_points() -> list[dict[str, Any]]:
    source_ids = {slug: f"source.persistence.{slug}" for slug, *_ in SOURCE_SEEDS}
    return [{
        "record_kind": "durability_architecture_decision",
        "decision_id": f"decision.persistence.object_log.{slug}",
        "edition": EDITION,
        "status": "candidate",
        "owner_scope_ref": "scope.persistence.object_log_architecture",
        "question": question,
        "value_type": pascal(slug),
        "allowed_values": values,
        "default_law": "forbidden",
        "default_value": None,
        "binding_phase": phase,
        "evidence_refs": [source_ids[item] for item in evidence],
        "compiler_law": "The value is selected explicitly, checked against an exact qualified deployment offer and retained in the binding receipt; absence or provider-name inference refuses compilation.",
    } for slug, question, values, phase, evidence in OBJECT_LOG_DECISION_AXIS_SEEDS]


def build_object_log_architectures() -> list[dict[str, Any]]:
    """Encode object-storage log/state patterns without collapsing unlike commit paths."""
    source_ids = {slug: f"source.persistence.{slug}" for slug, *_ in SOURCE_SEEDS}
    common_laws = [
        "Acknowledged durability is not indexed, materialized or query-visible state unless the selected read contract proves that exact frontier.",
        "A durable log record is not a compacted object, and compaction does not by itself make source log records safe to garbage-collect.",
        "Object-store durability does not imply multi-region availability, transactional scope, latency fitness or recovery fitness.",
        "Conditional or append writes do not by themselves provide multi-key transactions, leader election or consensus.",
    ]
    common_decisions = [
        "acknowledgement boundary and durability evidence",
        "object provider, storage class, region/zone and exact consistency primitives",
        "writer concurrency, ordering, fencing, conditional-write and retry semantics",
        "batching, object/part size, request-rate and monetary budgets",
        "cache hierarchy, cold-start posture and read-after-write strategy",
        "manifest or metadata authority, publication atomicity and recovery",
        "compaction, retention, garbage-collection safety horizon and deletion evidence",
    ]
    decision_refs = [f"decision.persistence.object_log.{slug}" for slug, *_ in OBJECT_LOG_DECISION_AXIS_SEEDS]

    def make(
        slug: str,
        name: str,
        organization: str,
        organization_kind: str,
        startup_relevance: str,
        architecture_class: str,
        workloads: list[str],
        commit_path: list[tuple[str, str, str]],
        read_path: list[str],
        coordination: list[str],
        durable_truth: str,
        maintenance: list[str],
        enabled: list[str],
        decisions: list[str],
        laws: list[str],
        tradeoffs: list[str],
        evidence: list[str],
        qualification_status: str = "unqualified_architecture_claim",
        gaps: list[str] | None = None,
    ) -> dict[str, Any]:
        return {
            "architecture_id": f"architecture.persistence.{slug}",
            "edition": EDITION,
            "status": "researched_candidate",
            "name": name,
            "organization": organization,
            "organization_kind": organization_kind,
            "startup_relevance": startup_relevance,
            "architecture_class": architecture_class,
            "workload_classes": workloads,
            "commit_path": [
                {"order": order, "stage": stage, "medium": medium, "acknowledgement_role": role}
                for order, (stage, medium, role) in enumerate(commit_path, 1)
            ],
            "read_path": read_path,
            "coordination": coordination,
            "durable_truth": durable_truth,
            "maintenance": maintenance,
            "enabled_capabilities": enabled,
            "compiler_decisions": [*common_decisions, *decisions],
            "decision_refs": decision_refs,
            "non_collapse_laws": [*common_laws, *laws],
            "tradeoffs": tradeoffs,
            "evidence_refs": [source_ids[item] for item in evidence],
            "qualification_status": qualification_status,
            "gaps": gaps or [
                "Bind an exact provider version and deployment occurrence.",
                "Reproduce correctness, failure-recovery, performance and cost claims independently.",
                "Qualify portability and exit behavior under provider-semantic differences.",
            ],
        }

    return [
        make(
            "aws_s3_log_primitives", "S3 conditional-write and append object primitives", "Amazon Web Services", "cloud_provider", "enabling_infrastructure",
            "enabling_object_log_primitive", ["object_log_substrate"],
            [("validate create/ETag/offset precondition", "S3 request precondition", "pre_ack"), ("store or append bytes", "S3 object or object part", "ack_boundary")],
            ["read the exact object/version or byte range after successful admission"],
            ["single-key conditional request", "caller-managed writer/order protocol", "temporary directory-bucket session for append"],
            "The admitted S3 object version or successful appended part under the selected storage-class contract.",
            ["roll over or copy objects before the append part limit", "audit versions, checksums, retention and deletion"],
            ["lock-free or optimistic single-key structures", "direct log and media append", "read-while-write workflows", "simpler stateless storage clients"],
            ["conditional primitive: create-if-absent versus ETag match", "S3 Standard versus S3 Express One Zone", "append rollover before 10,000 parts", "5 GiB per-append maximum"],
            ["Append is available only for S3 Express One Zone directory buckets.", "Each successful append is a billed PutObject request and contributes one part."],
            ["zonal scope", "per-request cost", "10,000-part rollover", "CAS conflict and retry amplification", "provider portability"],
            ["s3.conditional_release", "s3.conditional", "s3.express_append_release", "s3.express_append"],
        ),
        make(
            "chroma_wal3", "Chroma wal3 pure object-storage log", "Chroma", "company_product_team", "startup_origin_or_vendor_product",
            "direct_object_wal", ["vector_search", "full_text_search", "object_log"],
            [("form per-collection append", "stateless writer", "pre_ack"), ("admit linked log state with conditional write", "object storage", "ack_boundary"), ("consume acknowledged tail", "asynchronous indexer", "post_ack")],
            ["open the latest index cut", "apply the unindexed log tail", "return a frontier-bound result"],
            ["disjoint object prefixes per collection", "conditional-write linked-list algorithm", "setsum integrity accumulator"],
            "The per-collection object log; a write is acknowledged only after it is readable from that log.",
            ["asynchronous index construction", "trim and reachability-based garbage collection", "continuous setsum verification"],
            ["stateless durability service", "high-cardinality collection isolation", "read-your-write via index-plus-tail", "self-verifying garbage collection"],
            ["collection atomicity and throughput unit", "index lag and tail scan budget", "setsum algorithm and proof scope"],
            ["The index is a derived accelerator; it is not the durable write authority.", "A checksum proves only its declared log-state relation, not business correctness."],
            ["object request latency", "availability coupled to object storage", "tail growth under index lag", "garbage-collection proof complexity"],
            ["chroma.wal3", "s3.conditional"],
        ),
        make(
            "slatedb_object_native_lsm", "SlateDB object-native LSM", "SlateDB", "open_source_project", "enabling_infrastructure",
            "object_native_lsm", ["embedded_kv", "transactional_kv", "cdc", "catalog_state"],
            [("buffer mutations", "memory", "pre_ack"), ("write sequence-ordered WAL SST", "object store", "ack_boundary"), ("publish database-state snapshot", "manifest object", "ack_boundary_or_metadata_publication_by_mode")],
            ["resolve the latest manifest", "consult WAL and compacted SSTs", "serve through block/object caches"],
            ["single-writer epoch", "manifest sequencing", "separate writer and compactor epochs", "snapshot-isolated transaction mode"],
            "Manifest-reachable WAL and compacted SST objects in the configured object store.",
            ["background or distributed compaction", "checkpoints and forks", "garbage-collector boundary maintenance", "cache warming"],
            ["embedded durable KV without managed disks", "database checkpoints and clones", "CDC from sequence-ordered WAL", "object-native catalog/state substrate"],
            ["synchronous versus asynchronous commit", "WAL object store versus compacted-data object store", "manifest polling and cache", "custom comparator and merge operator"],
            ["SlateDB is an embedded library, not a network database or coordination service.", "Sequence-ordered WAL SSTs and key-ordered compacted SSTs have different identities and purposes."],
            ["object PUT/GET latency", "single-writer constraint", "request amplification", "compaction debt", "manifest hot spot", "cache dependence"],
            ["slatedb.introduction", "slatedb.files", "slatedb.source"],
        ),
        make(
            "automq_s3stream", "AutoMQ S3Stream shared WAL and object storage", "AutoMQ", "company_product_team", "startup_origin_or_vendor_product",
            "shared_wal_object_store", ["kafka_compatible_streaming", "streaming_log"],
            [("append and batch records from many streams", "broker/S3Stream library", "pre_ack"), ("persist to selected shared WAL", "S3-compatible store, EBS, NFS or another WAL backend", "ack_boundary"), ("merge/upload larger stream objects", "main object store", "post_ack")],
            ["fetch recent ranges from WAL or caches", "fetch consolidated ranges from object storage", "merge by stream position"],
            ["stream position management", "broker/controller metadata", "shared-WAL ordering"],
            "The selected WAL establishes acknowledged stream durability until main object-store consolidation preserves it.",
            ["stream-object compaction", "WAL trimming after safe upload", "broker-independent reassignment"],
            ["stateless Kafka brokers", "reassignment without copying broker disks", "large shared object batches", "independent compute/storage scaling"],
            ["WAL backend independently from main object store", "stream batching and flush trigger", "Kafka compatibility edition", "controller metadata durability"],
            ["Direct S3 WAL is not the same architecture as tiering Kafka segments after local-disk acknowledgement.", "Vendor benchmark results are not target-deployment qualification evidence."],
            ["WAL latency and request price", "multi-stream noisy neighbors", "metadata/control-plane dependency", "provider-specific failure semantics"],
            ["automq.s3stream", "automq.s3_wal"],
        ),
        make(
            "warpstream_diskless_log", "WarpStream diskless Kafka-compatible log", "WarpStream", "company_product_team", "startup_origin_or_vendor_product",
            "object_native_stream_log", ["kafka_compatible_streaming", "streaming_log", "mixed_streaming_analytics"],
            [("route Kafka-compatible produce request", "stateless agent", "pre_ack"), ("persist log data", "object storage", "ack_boundary"), ("publish/control metadata", "cloud metadata and control service", "coordination_not_payload")],
            ["agents plan reads from metadata", "range-read object log data", "cache and merge requested stream ranges"],
            ["vendor control plane", "cloud metadata store", "stateless agents grouped for workload isolation"],
            "Object storage holds durable log data; metadata/control services hold the reachable stream organization.",
            ["object consolidation and garbage collection", "metadata lifecycle", "agent-group scaling"],
            ["diskless Kafka-compatible streaming", "fast compute replacement", "separate transactional and analytical reader fleets", "customer-cloud data plane"],
            ["control-plane dependency", "agent-group isolation", "Kafka API compatibility subset", "metadata provider"],
            ["Workload isolation does not turn a streaming log into an HTAP database transaction boundary.", "Object payload ownership and metadata/control-plane authority remain separate."],
            ["object latency", "control-plane availability", "closed implementation substitutability", "egress and request cost"],
            ["warpstream.architecture"],
        ),
        make(
            "turbopuffer_object_wal", "turbopuffer object-WAL search architecture", "turbopuffer", "company_product_team", "startup_origin_or_vendor_product",
            "object_wal_async_index", ["vector_search", "full_text_search", "hybrid_search"],
            [("group namespace mutations", "memory buffer", "pre_ack"), ("write a WAL file under the namespace prefix", "object storage", "ack_boundary"), ("build and CAS-publish index state", "asynchronous indexer and object storage", "post_ack")],
            ["read the index cursor", "scan committed-but-unindexed WAL tail", "merge and rank results"],
            ["namespace-scoped write serialization and batching", "CAS index commit point", "shared WAL for internal shards"],
            "Every successful write has a durable WAL object under the namespace prefix.",
            ["asynchronous SPFresh-style indexing", "index compaction", "cache population", "namespace sharding"],
            ["serverless high-cardinality search namespaces", "strong read-after-write through tail scan", "vector/full-text hybrid retrieval", "cold object durability with elastic compute"],
            ["one-WAL-entry-per-namespace batching cadence", "strong versus eventual read mode", "index algorithm and recall budget", "namespace shard fan-out"],
            ["A successful write can be durable and query-visible before it is indexed.", "Approximate index recall is separate from consistency of the committed mutation frontier."],
            ["documented p50 write latency", "cold-cache latency", "per-namespace write cadence", "tail-scan cost", "approximation and index debt"],
            ["turbopuffer.architecture", "turbopuffer.tradeoffs"],
        ),
        make(
            "neon_disaggregated_postgres", "Neon disaggregated PostgreSQL storage", "Neon", "company_product_team", "startup_origin_or_vendor_product",
            "replicated_wal_object_history", ["oltp", "postgresql", "branchable_database"],
            [("generate PostgreSQL WAL", "compute node", "pre_ack"), ("replicate WAL to a Safekeeper quorum", "WAL service", "ack_boundary"), ("materialize pages and immutable layers", "pageserver", "post_ack"), ("upload historical layers", "object storage", "post_ack")],
            ["request pages at an LSN", "reconstruct from image/delta layers and WAL", "cache pages near compute"],
            ["Safekeeper quorum", "tenant timeline and LSN", "pageserver attachment and generation"],
            "Safekeeper quorum establishes commit durability; object storage is the long-term page/WAL-derived history layer.",
            ["page materialization", "immutable-layer compaction", "object upload", "branch/PITR retention"],
            ["stateless replaceable compute", "scale-to-zero", "database branching and point-in-time restore", "elastic read replicas"],
            ["Safekeeper quorum size and placement", "WAL retention until page/object coverage", "branch ancestry and retention", "cache warming"],
            ["PostgreSQL commit at a Safekeeper quorum is not direct WAL-on-S3 commit.", "WAL commit, page materialization and object-history upload are three different frontiers."],
            ["WAL service availability", "cold page reconstruction", "object-upload lag", "branch retention cost", "cache churn"],
            ["neon.architecture"],
        ),
        make(
            "influxdb3_wal_parquet", "InfluxDB 3 WAL-to-Parquet object storage", "InfluxData", "company_product_team", "startup_origin_or_vendor_product",
            "wal_parquet_object_state", ["time_series", "operational_analytics"],
            [("admit line protocol or table mutation", "ingester", "pre_ack"), ("persist WAL record under configured durability mode", "WAL subsystem", "ack_boundary"), ("persist compacted columnar data", "Parquet in object storage", "post_ack")],
            ["combine cached/WAL recent data with persisted Parquet files", "prune and scan object files"],
            ["database/table identity", "WAL sequence", "catalog of persisted Parquet files"],
            "The selected WAL contract protects acknowledged recent writes; object-backed Parquet becomes durable analytical state after persistence.",
            ["WAL snapshot/persistence", "Parquet compaction", "cache and catalog maintenance"],
            ["object-backed time-series retention", "separated ingest and query compute", "columnar analytics", "low-operational-storage fleet"],
            ["WAL flush and acknowledgement mode", "Parquet persistence interval", "late-data and duplicate policy", "query freshness composition"],
            ["WAL durability is not Parquet persistence.", "Parquet object availability is not proof that the latest acknowledged WAL frontier is query-visible."],
            ["recent-tail recovery", "small-file and compaction pressure", "query freshness", "object request and scan cost"],
            ["influx.storage", "influx.durability"],
        ),
        make(
            "materialize_persist", "Materialize Persist durable collections", "Materialize", "company_product_team", "startup_origin_or_vendor_product",
            "durable_collection_object_persist", ["incremental_view_maintenance", "streaming_sql", "operational_analytics"],
            [("produce time-varying collection updates", "storage or compute cluster", "pre_ack"), ("write durable collection data", "Persist in S3", "data_durability_boundary"), ("advance collection metadata", "distributed transactional consensus database", "metadata_commit_boundary")],
            ["select a valid logical timestamp", "read Persist collection bounds/data", "optionally serve a cluster-local index"],
            ["separate consensus database", "logical timestamp frontiers", "collection shard ownership"],
            "Persist data in S3 plus consensus metadata jointly define reachable durable time-varying collections.",
            ["compaction of historical updates", "frontier advancement", "cluster-local index rebuild"],
            ["durable incremental materialized views", "cross-cluster collection sharing", "elastic compute clusters", "deterministic replay"],
            ["consensus provider", "since/upper frontier advancement", "cluster-local index materialization", "retention and compaction"],
            ["An in-memory cluster index is not a durable shared materialized view.", "S3 bytes without consensus metadata are not necessarily a reachable Persist collection."],
            ["consensus dependency", "frontier/compaction mistakes", "object latency", "rebuild latency", "cross-cluster transfer"],
            ["materialize.architecture", "materialize.views"],
        ),
        make(
            "risingwave_object_state", "RisingWave checkpointed object state", "RisingWave", "company_product_team", "startup_origin_or_vendor_product",
            "checkpointed_object_state", ["streaming_database", "streaming_sql", "incremental_view_maintenance"],
            [("process one barrier epoch", "streaming nodes", "pre_ack"), ("upload persistent state for the epoch", "object storage", "checkpoint_data_boundary"), ("commit checkpoint metadata", "meta node", "checkpoint_completion_boundary")],
            ["serve from streaming state and LSM state", "read persistent state from object storage on recovery", "serve ad-hoc queries through stateless serving nodes"],
            ["barrier/checkpoint protocol", "Meta Node coordination", "LSM epochs"],
            "A completed checkpoint binds source progress, streaming state and object-store persistence for a barrier epoch.",
            ["LSM compaction", "checkpoint and recovery", "stream-job rescheduling"],
            ["fault-tolerant streaming database", "materialized views", "compute/storage independent scaling", "stateless SQL serving"],
            ["checkpoint interval and alignment", "state-backend object provider", "compactor capacity", "source/sink exactly-once contract"],
            ["Persistent operator state is not the source event log.", "Object upload alone is not a completed checkpoint until coordinating metadata/frontiers commit."],
            ["checkpoint latency", "state growth", "compaction debt", "Meta Node dependency", "recovery download and cache warmup"],
            ["risingwave.architecture"],
        ),
        make(
            "s2_object_stream", "S2 object-native stream log", "S2", "company_product_team", "startup_origin_or_vendor_product",
            "object_native_stream_log", ["streaming_log", "high_cardinality_streams", "embedded_stream"],
            [("route append to assigned channel", "stateless frontend and channel", "pre_ack"), ("multiplex records into a sequential chunk", "object storage", "ack_boundary"), ("rewrite into larger per-stream segments and metadata", "object storage and stream metadata", "post_ack")],
            ["plan segment ranges from stream metadata", "append recent channel-WAL pointers", "range-read via zonal read-through cache"],
            ["channel sequencing", "stream activation metadata", "channel operator rebalancing"],
            "Associated records must be durable in an object chunk before append acknowledgement.",
            ["WAL-to-segment batching", "garbage collection", "channel migration", "read-cache management"],
            ["object-native durable streams", "many streams multiplexed into economical objects", "elastic frontends and caches", "embedded object-backed streaming via S2 lite"],
            ["S3 Standard versus S3 Express quorum storage class", "channel assignment and migration", "flush size/time", "stream metadata publication"],
            ["A multiplexed channel chunk is not the same object or identity as a per-stream segment.", "Durable append acknowledgement does not mean the per-stream segment rewrite is complete."],
            ["channel hot spots", "object range-read latency", "metadata recovery", "cache dependence", "rewrite and GC safety"],
            ["s2.architecture", "s2.lite_source", "slatedb.source"],
        ),
        make(
            "quickwit_object_index", "Quickwit object-native immutable search index", "Quickwit", "open_source_project", "enabling_infrastructure",
            "object_native_search_index", ["full_text_search", "log_analytics", "observability_search"],
            [("consume source records", "indexer", "pre_publication"), ("build and upload immutable split plus hotcache", "object storage", "data_durable_not_visible"), ("publish split metadata", "metastore", "visibility_boundary")],
            ["obtain searchable split metadata", "prune splits", "open hotcache and range-read split files from object storage"],
            ["metastore split state", "indexer publication protocol", "source queue checkpoints"],
            "Object storage holds immutable index splits; metastore publication determines which splits are searchable.",
            ["split merge/retention", "metastore cleanup", "cache population"],
            ["stateless searchers", "cheap long-retention search", "fast split opening through hotcache", "elastic indexing and search fleets"],
            ["source queue and checkpoint", "split size and merge", "metastore provider", "hotcache layout and cache budget"],
            ["Object-native index storage is adjacent to but not a WAL-on-object-storage architecture.", "Uploaded split bytes are not query-visible until exact metastore publication succeeds."],
            ["metastore dependency", "cold range-read latency", "source queue durability", "split proliferation", "publication recovery"],
            ["quickwit.architecture"],
        ),
        make(
            "btrlog_quorum_archive", "BtrLog quorum log with object archival", "BtrLog research authors", "primary_research", "not_applicable",
            "quorum_wal_object_archive", ["oltp", "database_wal"],
            [("replicate log record in one network round trip", "quorum of SSD-backed log nodes", "ack_boundary"), ("form larger immutable segments", "log service", "post_ack"), ("archive segment", "object storage", "post_ack")],
            ["recover recent log from quorum nodes", "recover archived history from object segments"],
            ["quorum replication", "single-writer database log assignment", "archive-watermark tracking"],
            "The SSD quorum is the hot acknowledged log; archived object segments are the lower-cost historical tier.",
            ["segment formation", "asynchronous archival", "log-node reclamation after archive proof"],
            ["reusable low-latency cloud database log", "reduced database-local replication", "cheap long history", "independent log service scaling"],
            ["quorum and failure domains", "archive segment size and lag", "recovery-source selection", "log-node reclamation horizon"],
            ["Object archival is outside the commit latency path.", "Archive completion is required before reclaiming the only surviving quorum-log copies."],
            ["dedicated log fleet", "archive backlog", "single-region quorum", "research-to-production gap"],
            ["btrlog.paper"], "research_prototype_unqualified",
        ),
        make(
            "milliscale_direct_object_oltp", "Milliscale direct low-latency object OLTP", "Milliscale research authors", "primary_research", "not_applicable",
            "direct_low_latency_object_oltp", ["oltp"],
            [("prepare transaction and decentralized log assignment", "memory-optimized OLTP engine", "pre_ack"), ("append/commit using low-latency mutable object primitives", "S3 Express One Zone class", "ack_boundary")],
            ["reconstruct operational state from object-resident commit/log data and memory structures"],
            ["engine transaction protocol", "append offset/object ownership", "request-reduction techniques"],
            "The low-latency object store participates directly in the transaction commit path under the research protocol.",
            ["object rollover and consolidation", "recovery", "request-amplification control"],
            ["direct OLTP persistence without a separate block/log service", "memory-optimized transactional engine over object storage", "simplified compute replacement"],
            ["object append/mutation capability", "zonal failure posture", "transaction log partitioning", "request-minimization algorithm"],
            ["Results for low-latency mutable object storage do not generalize to ordinary object-store PUT latency.", "A research benchmark is not an independently qualified enterprise deployment."],
            ["zonal dependency", "request price", "append limits", "provider portability", "research maturity"],
            ["milliscale.paper", "s3.express_append"], "research_prototype_unqualified",
        ),
        make(
            "oceanbase_bacchus", "OceanBase Bacchus shared-storage architecture", "OceanBase Bacchus research authors", "primary_research", "not_applicable",
            "service_log_object_lsm", ["oltp", "olap", "htap"],
            [("execute transaction or analytical mutation", "stateless compute", "pre_ack"), ("synchronize append log", "service-oriented Paxos log", "ack_boundary"), ("materialize LSM state", "caches and object storage", "post_ack")],
            ["serve hot data through independent cache tiers", "read LSM objects from shared storage", "route OLTP/OLAP workload to appropriate compute"],
            ["service-oriented Paxos log", "metadata service", "independent compute/cache/storage scaling"],
            "The Paxos append log establishes ordered commit while the object-native LSM and caches provide shared persistent state and serving paths.",
            ["LSM compaction", "cache fill/eviction", "log truncation after object-state proof", "multi-cloud placement"],
            ["stateless compute", "shared OLTP and OLAP storage", "independent cache scaling", "multi-cloud shared-storage deployment", "HTAP workload coverage"],
            ["OLTP versus OLAP workload isolation", "Paxos log deployment", "cache topology", "LSM compaction", "multi-cloud consistency and egress"],
            ["OLTP, OLAP and HTAP are distinct workload contracts; a shared storage layer does not collapse them.", "The log service, object-state engine and caches are independently replaceable and independently qualified."],
            ["log-service dependency", "cache-coherence complexity", "cross-cloud latency/egress", "compaction debt", "research/vendor evaluation bias"],
            ["oceanbase.bacchus"], "research_prototype_unqualified",
        ),
        make(
            "rocklake_slatedb_catalog", "RockLake DuckLake catalog on SlateDB", "Trickle Labs", "open_source_project", "startup_relevance_unverified",
            "object_native_catalog", ["lakehouse_catalog", "embedded_kv"],
            [("apply catalog transaction", "DuckLake-compatible catalog layer", "pre_ack"), ("persist catalog keys and WAL/manifest state", "SlateDB on object storage", "ack_boundary_by_embedded_store_mode")],
            ["read catalog state through SlateDB", "resolve table/file metadata for a DuckLake client"],
            ["catalog transaction semantics", "SlateDB writer/manifest protocol"],
            "Catalog state is represented through SlateDB-reachable object state; table data remains separately owned.",
            ["catalog history compaction", "SlateDB compaction and garbage collection", "schema/version migration"],
            ["single-object-store lakehouse metadata substrate", "embedded catalog deployment", "reusable object-native state library"],
            ["DuckLake compatibility edition", "catalog concurrency", "SlateDB commit mode", "table-data versus catalog-state placement"],
            ["An early source repository is not evidence of production maturity.", "Catalog persistence does not own table data files, query execution or business semantics."],
            ["early-project maturity", "compatibility coverage", "multi-writer behavior", "migration and recovery evidence"],
            ["rocklake.source", "slatedb.files", "slatedb.source"],
        ),
        make(
            "turso_s3_express", "Turso write-through WAL on S3 Express", "Turso", "company_product_team", "startup_origin_or_vendor_product",
            "write_through_object_wal_checkpoint", ["oltp", "sqlite", "multi_tenant_database", "byoc_database"],
            [("execute transactions and batch WAL entries across databases", "compute memory", "pre_ack"), ("PUT the WAL batch", "S3 Express One Zone", "ack_boundary"), ("write/read cache copy", "local NVMe", "post_ack_cache"), ("fold WAL into a database checkpoint", "S3 Standard", "post_ack_recovery_baseline")],
            ["read local NVMe cache", "fetch from S3 Express on cache miss", "repopulate disposable cache"],
            ["compute-node batch ownership", "per-database WAL lineage", "checkpoint frontier"],
            "Successful S3 Express PUT establishes transaction durability; local NVMe is disposable, while periodic S3 Standard checkpoints form longer-term recovery baselines.",
            ["multi-database WAL batching", "WAL-to-database checkpointing", "S3 storage-class transition", "cache refill"],
            ["ephemeral BYOC database pods", "instant compute replacement without persistent volumes", "high-density SQLite tenancy", "request-cost amortization across databases", "elastic scale without data migration"],
            ["batch window and cross-tenant isolation", "same-AZ placement", "S3 Express-to-Standard checkpoint interval", "WAL lineage and checkpoint recovery", "cache capacity"],
            ["The local NVMe copy is a cache and never the durable authority.", "S3 Express WAL commit and S3 Standard checkpoint completion are distinct recovery frontiers.", "Vendor-measured latency on one deployment is not a portable SLO."],
            ["single-AZ commit substrate", "batching latency versus request cost", "cross-tenant batching isolation", "checkpoint lag", "provider lock-in"],
            ["turso.s3_express", "s3.express_append", "s3.versioning"],
        ),
        make(
            "supabase_wal_to_iceberg", "Supabase PostgreSQL WAL to Iceberg", "Supabase", "company_product_team", "startup_origin_or_vendor_product",
            "cdc_wal_to_analytical_table", ["oltp_to_olap_replication", "operational_analytics", "zero_etl", "lakehouse_table"],
            [("commit source transaction", "PostgreSQL WAL", "source_ack_boundary"), ("read logical changes and replication position", "CDC/ETL service", "post_ack_capture"), ("write files and commit table metadata", "Iceberg on S3 Tables", "analytical_visibility_boundary")],
            ["query PostgreSQL operational state", "query Iceberg analytical state", "optionally federate Iceberg tables through a PostgreSQL foreign-data wrapper"],
            ["PostgreSQL replication slot/position", "CDC checkpoint and deduplication", "Iceberg snapshot commit"],
            "PostgreSQL WAL remains source transaction truth; an Iceberg snapshot is a derived analytical cut with its own position and publication receipt.",
            ["CDC checkpointing", "schema/delete translation", "Iceberg file compaction", "source-to-table reconciliation"],
            ["near-real-time operational analytics", "open analytical tables", "reduced pipeline setup", "federated operational and historical SQL access"],
            ["logical-decoding contract", "replication-slot retention", "schema and delete mapping", "Iceberg commit/retry", "freshness SLO", "reconciliation and backfill"],
            ["This is zero-ETL product composition, not zero transformation, zero delay or zero reconciliation.", "A source commit is not an analytical-table commit.", "Federated SQL access is not a shared HTAP transaction or isolation boundary."],
            ["source WAL retention pressure", "CDC lag", "schema-evolution loss", "duplicate/replay handling", "small-file compaction", "cross-system reconciliation"],
            ["supabase.s3_tables", "iceberg.table"],
        ),
        make(
            "hydradb_object_graph", "HydraDB graph database on SlateDB", "HydraDB", "open_source_project", "startup_relevance_unverified",
            "object_native_graph_lsm", ["graph_oltp", "graph_traversal", "vector_search", "full_text_search"],
            [("acquire graph-cell writer lease and fence prior writer", "object-store coordination plus SlateDB epoch", "pre_ack"), ("commit canonical graph mutation through WAL barrier", "SlateDB and object storage", "ack_boundary"), ("build immutable traversal/search generation", "object storage", "post_ack")],
            ["pin one SlateDB snapshot", "combine immutable index base with visible WAL tail", "fall back to canonical snapshot reads"],
            ["one admitted writer per graph cell", "object-store lease", "SlateDB writer epoch and WAL barrier"],
            "Canonical graph records in the pinned SlateDB snapshot are truth; traversal/vector/text indexes are derived generations.",
            ["graph index generation", "WAL-tail coverage", "cell compaction", "lease recovery"],
            ["object-native graph persistence", "disposable query/index workers", "graph plus vector/full-text indexes", "snapshot-consistent index-plus-tail reads"],
            ["graph cell partitioning", "lease duration/fencing", "index generation frontier", "tail-scan fallback", "SlateDB commit mode"],
            ["An index generation is an accelerator and never canonical graph truth.", "A lease record alone is not the final split-writer fence; the writer epoch and WAL barrier also matter."],
            ["single-writer cell throughput", "early-project maturity", "lease/fencing recovery", "cold traversal latency", "index lag"],
            ["hydradb.architecture", "slatedb.files", "slatedb.source"],
        ),
        make(
            "basin_object_postgres", "Basin PostgreSQL-compatible object database", "vul-os", "open_source_project", "startup_relevance_unverified",
            "object_wal_columnar_database", ["postgresql", "multi_tenant_database", "operational_analytics", "vector_search"],
            [("route tenant SQL to shard owner", "stateless router and in-memory shard owner", "pre_ack"), ("flush durable WAL append", "object storage", "ack_boundary_claim"), ("materialize columnar project state", "Vortex or Parquet plus catalog", "post_ack")],
            ["lazy-load project state from WAL and columnar objects", "serve from memory", "use pruning or indexes when qualified and fall back to scans"],
            ["project/shard ownership", "current single-process Raft-WAL simulation", "catalog snapshot publication"],
            "The repository describes object WAL plus columnar catalog state; exact distributed durability remains an early implementation boundary.",
            ["WAL flush", "columnar compaction", "index registry rebuild", "project eviction/lazy load"],
            ["many isolated PostgreSQL-compatible tenants", "columnar operational history", "vector and JSON/search access", "object-store capacity economics"],
            ["distributed WAL maturity", "tenant/shard ownership", "columnar format", "index completeness", "PostgreSQL compatibility edition"],
            ["Repository claims do not establish production durability, compatibility or performance.", "An incomplete index registry may weaken pruning but must not change query correctness."],
            ["early implementation", "single-process replication limitation", "cold project load", "index/compaction debt", "compatibility gaps"],
            ["basin.source"],
        ),
        make(
            "walrust_sqlite_shipping", "walrust SQLite WAL shipping", "walrust", "open_source_project", "startup_relevance_unverified",
            "asynchronous_wal_shipping", ["sqlite_backup", "read_replica", "point_in_time_recovery"],
            [("commit local SQLite transaction", "local SQLite WAL and filesystem", "source_ack_boundary"), ("capture and upload WAL lineage", "S3-compatible object storage", "post_ack_replication"), ("compact lineage into snapshot when configured", "object storage", "post_ack_recovery_baseline")],
            ["restore a snapshot plus ordered WAL lineage", "serve a separately constructed read replica after validation"],
            ["SQLite read transaction pins WAL", "replication lineage identity", "compaction-compatible key layout"],
            "Local SQLite remains commit authority; uploaded WAL/snapshots form an asynchronous recovery and replica lineage.",
            ["WAL shipping", "snapshot/compaction", "retention", "restore validation"],
            ["low-footprint SQLite backup", "point-in-time recovery", "object-backed read replicas", "S3-compatible provider portability"],
            ["shipping interval", "snapshot lineage", "checkpoint pinning", "compaction key layout", "retention and restore target"],
            ["Asynchronous WAL shipping is not remote durability on the source commit path.", "Backup capture is not restore proof or read-replica acceptance."],
            ["replication lag", "local source loss before upload", "experimental maturity", "WAL pinning pressure", "restore time"],
            ["walrust.source", "sqlite.wal"],
        ),
    ]


OBJECT_LOG_CLASS_CAPABILITIES = {
    "enabling_object_log_primitive": ["object_namespace.put_object", "object_namespace.get_object_range", "object_namespace.conditional_replace", "integrity.verify_checksum"],
    "direct_object_wal": ["object_namespace.put_object", "object_namespace.get_object_range", "object_namespace.conditional_replace", "event_journal.append_event", "event_journal.read_stream", "event_journal.truncate_stream", "index_build.build_index", "search_visibility.observe_search_visibility_cut"],
    "object_native_lsm": ["object_namespace.put_object", "object_namespace.get_object_range", "object_namespace.conditional_replace", "key_value_store.put_key", "key_value_store.atomic_write_batch", "key_value_store.iterate_key_range", "manifest_inventory.write_manifest", "manifest_inventory.scan_manifests", "compaction.plan_compaction", "compaction.execute_compaction", "compaction.verify_compaction"],
    "shared_wal_object_store": ["object_namespace.put_object", "object_namespace.get_object_range", "event_journal.append_event", "event_journal.read_stream", "event_journal.truncate_stream", "replication.replicate_write"],
    "object_native_stream_log": ["object_namespace.put_object", "object_namespace.get_object_range", "event_journal.append_event", "event_journal.read_stream", "event_journal.truncate_stream"],
    "object_wal_async_index": ["object_namespace.put_object", "object_namespace.get_object_range", "object_namespace.conditional_replace", "event_journal.append_event", "event_journal.read_stream", "index_mutation.submit_index_mutation", "index_mutation.record_mutation_acknowledgement", "index_build.build_index", "search_visibility.observe_search_visibility_cut", "search_store.refresh_search_cut"],
    "replicated_wal_object_history": ["object_namespace.put_object", "object_namespace.get_object_range", "event_journal.append_event", "event_journal.read_stream", "replication.replicate_write", "restore.restore_cut"],
    "wal_parquet_object_state": ["object_namespace.put_object", "object_namespace.get_object_range", "event_journal.append_event", "event_journal.read_stream", "columnar_file.encode_columnar_file", "columnar_file.decode_projection", "time_series_store.append_sample", "compaction.execute_compaction"],
    "durable_collection_object_persist": ["object_namespace.put_object", "object_namespace.get_object_range", "object_namespace.conditional_replace", "snapshot_state.construct_snapshot", "snapshot_state.load_snapshot", "incremental_materialization.apply_incremental_change", "incremental_materialization.advance_materialization_frontier", "incremental_materialization.rebuild_materialization"],
    "checkpointed_object_state": ["object_namespace.put_object", "object_namespace.get_object_range", "stream_state_store.checkpoint_operator_state", "stream_state_store.restore_operator_state", "stream_state_store.compact_state"],
    "object_native_search_index": ["object_namespace.put_object", "object_namespace.get_object_range", "index_build.build_index", "index_build.attach_index", "search_store.search_terms", "search_visibility.observe_search_visibility_cut"],
    "quorum_wal_object_archive": ["object_namespace.put_object", "object_namespace.get_object_range", "event_journal.append_event", "event_journal.read_stream", "replication.replicate_write", "archival_media.archive_object", "archival_media.recall_object"],
    "direct_low_latency_object_oltp": ["object_namespace.put_object", "object_namespace.get_object_range", "object_namespace.conditional_replace", "event_journal.append_event", "event_journal.read_stream", "relational_store.execute_transaction"],
    "service_log_object_lsm": ["object_namespace.put_object", "object_namespace.get_object_range", "event_journal.append_event", "event_journal.read_stream", "replication.replicate_write", "relational_store.execute_transaction", "compaction.execute_compaction"],
    "object_native_catalog": ["object_namespace.put_object", "object_namespace.get_object_range", "object_namespace.conditional_replace", "manifest_inventory.write_manifest", "manifest_inventory.scan_manifests", "commit_authority.load_for_commit", "commit_authority.commit_metadata_update"],
    "write_through_object_wal_checkpoint": ["object_namespace.put_object", "object_namespace.get_object_range", "event_journal.append_event", "event_journal.read_stream", "embedded_store.commit_local_transaction", "embedded_store.checkpoint_local_wal", "relational_store.execute_transaction", "tiering.transition_tier", "restore.restore_cut"],
    "cdc_wal_to_analytical_table": ["object_namespace.put_object", "object_namespace.get_object_range", "change_feed.plan_incremental_scan", "change_feed.read_change_feed", "change_feed.checkpoint_change_consumer", "append_mutation.commit_append", "commit_protocol.commit_table_state", "compaction.execute_compaction"],
    "object_native_graph_lsm": ["object_namespace.put_object", "object_namespace.get_object_range", "object_namespace.conditional_replace", "property_graph_store.commit_graph_transaction", "property_graph_store.traverse_graph", "index_build.build_index", "search_store.search_terms", "vector_store.search_neighbors", "search_visibility.observe_search_visibility_cut"],
    "object_wal_columnar_database": ["object_namespace.put_object", "object_namespace.get_object_range", "event_journal.append_event", "event_journal.read_stream", "relational_store.execute_transaction", "columnar_file.encode_columnar_file", "columnar_file.decode_projection", "compaction.execute_compaction", "vector_store.search_neighbors"],
    "asynchronous_wal_shipping": ["object_namespace.put_object", "object_namespace.get_object_range", "embedded_store.checkpoint_local_wal", "backup.capture_full_backup", "backup.capture_incremental_backup", "restore.restore_cut", "restore.verify_restored_cut"],
}


OBJECT_LOG_PROFILE_SEEDS = [
    {
        "slug": "object_transaction_commit", "intent": "Commit an operational transaction through object-backed durable state without local durable disk authority.",
        "workloads": ["oltp"], "classes": ["direct_low_latency_object_oltp", "write_through_object_wal_checkpoint", "object_wal_columnar_database"],
        "clauses": [("object_rw", "all", ["object_namespace.put_object", "object_namespace.get_object_range"]), ("transaction_semantics", "any", ["relational_store.execute_transaction", "embedded_store.commit_local_transaction"]), ("ordered_admission", "any", ["object_namespace.conditional_replace", "event_journal.append_event"])],
        "libraries": ["library.persistence.object_contract", "library.persistence.storage_identity", "library.persistence.persistence_outcome", "library.persistence.integrity", "library.persistence.reachability_gc"],
        "missing": ["library.persistence.transaction_contract", "library.persistence.event_journal"],
    },
    {
        "slug": "database_log_service", "intent": "Externalize a low-latency database commit log while retaining recoverable object history.",
        "workloads": ["oltp", "database_wal"], "classes": ["quorum_wal_object_archive", "replicated_wal_object_history", "service_log_object_lsm"],
        "clauses": [("ordered_log", "all", ["event_journal.append_event", "event_journal.read_stream"]), ("durable_redundancy", "all", ["replication.replicate_write"]), ("object_history", "all", ["object_namespace.put_object", "object_namespace.get_object_range"])],
        "libraries": ["library.persistence.object_contract", "library.persistence.persistence_outcome", "library.persistence.storage_identity", "library.persistence.backup_manifest", "library.persistence.recovery_objectives", "library.persistence.reachability_gc"],
        "missing": ["library.persistence.event_journal", "library.persistence.replicated_log"],
    },
    {
        "slug": "object_native_stream_log", "intent": "Provide ordered durable streams using object storage rather than broker-local durable disks.",
        "workloads": ["streaming_log", "kafka_compatible_streaming"], "classes": ["shared_wal_object_store", "object_native_stream_log"],
        "clauses": [("stream_log", "all", ["event_journal.append_event", "event_journal.read_stream", "event_journal.truncate_stream"]), ("object_rw", "all", ["object_namespace.put_object", "object_namespace.get_object_range"])],
        "libraries": ["library.persistence.object_contract", "library.persistence.persistence_outcome", "library.persistence.storage_identity", "library.persistence.reachability_gc"],
        "missing": ["library.persistence.event_journal", "library.persistence.stream_position_contract"],
    },
    {
        "slug": "object_native_embedded_state", "intent": "Persist embedded database, graph or catalog state through an object-native LSM/manifest substrate.",
        "workloads": ["embedded_kv", "catalog_state", "lakehouse_catalog", "graph_oltp"], "classes": ["object_native_lsm", "object_native_catalog", "object_native_graph_lsm"],
        "clauses": [("object_rw", "all", ["object_namespace.put_object", "object_namespace.get_object_range"]), ("authoritative_mutation", "any", ["key_value_store.atomic_write_batch", "commit_authority.commit_metadata_update", "property_graph_store.commit_graph_transaction"]), ("coordination", "any", ["object_namespace.conditional_replace", "manifest_inventory.write_manifest"])],
        "libraries": ["library.persistence.object_contract", "library.persistence.storage_identity", "library.persistence.snapshot_graph", "library.persistence.compaction_planner", "library.persistence.reachability_gc"],
        "missing": ["library.persistence.key_value_state_contract", "library.persistence.manifest_publication"],
    },
    {
        "slug": "object_wal_search", "intent": "Serve search over durable object state while making index lag and recent-tail composition explicit.",
        "workloads": ["vector_search", "full_text_search", "hybrid_search", "log_analytics"], "classes": ["direct_object_wal", "object_wal_async_index", "object_native_search_index", "object_native_graph_lsm"],
        "clauses": [("object_rw", "all", ["object_namespace.put_object", "object_namespace.get_object_range"]), ("index_build", "all", ["index_build.build_index"]), ("visibility", "all", ["search_visibility.observe_search_visibility_cut"])],
        "libraries": ["library.persistence.object_contract", "library.persistence.index_mutation", "library.persistence.search_visibility", "library.persistence.storage_identity", "library.persistence.reachability_gc"],
        "missing": ["library.persistence.index_tail_composition"],
    },
    {
        "slug": "durable_incremental_state", "intent": "Maintain a recoverable incremental analytical or streaming state frontier in object storage.",
        "workloads": ["time_series", "incremental_view_maintenance", "streaming_database"], "classes": ["wal_parquet_object_state", "durable_collection_object_persist", "checkpointed_object_state"],
        "clauses": [("object_rw", "all", ["object_namespace.put_object", "object_namespace.get_object_range"]), ("incremental_frontier", "any", ["incremental_materialization.advance_materialization_frontier", "stream_state_store.checkpoint_operator_state", "time_series_store.append_sample"]), ("recovery_shape", "any", ["snapshot_state.construct_snapshot", "stream_state_store.restore_operator_state", "columnar_file.encode_columnar_file"])],
        "libraries": ["library.persistence.object_contract", "library.persistence.materialization", "library.persistence.snapshot_graph", "library.persistence.compaction_planner", "library.persistence.persistence_outcome"],
        "missing": ["library.persistence.checkpointed_state_frontier"],
    },
    {
        "slug": "operational_to_analytical_replica", "intent": "Derive a governed analytical table cut from an operational WAL with explicit lag and reconciliation.",
        "workloads": ["oltp_to_olap_replication", "operational_analytics"], "classes": ["cdc_wal_to_analytical_table"],
        "clauses": [("change_capture", "all", ["change_feed.read_change_feed", "change_feed.checkpoint_change_consumer"]), ("table_publication", "all", ["append_mutation.commit_append", "commit_protocol.commit_table_state"]), ("object_rw", "all", ["object_namespace.put_object", "object_namespace.get_object_range"])],
        "libraries": ["library.persistence.object_contract", "library.persistence.commit_precondition", "library.persistence.commit_protocol", "library.persistence.snapshot_graph", "library.persistence.schema_evolution", "library.persistence.compaction_planner", "library.source.source_cursor"],
        "missing": ["library.persistence.change_feed_contract", "library.persistence.source_table_reconciliation"],
    },
    {
        "slug": "asynchronous_recovery_lineage", "intent": "Ship local WAL and snapshots into object storage for backup, PITR and separately accepted replicas.",
        "workloads": ["sqlite_backup", "read_replica", "point_in_time_recovery"], "classes": ["asynchronous_wal_shipping"],
        "clauses": [("source_checkpoint", "all", ["embedded_store.checkpoint_local_wal"]), ("object_rw", "all", ["object_namespace.put_object", "object_namespace.get_object_range"]), ("restore", "all", ["restore.restore_cut", "restore.verify_restored_cut"])],
        "libraries": ["library.persistence.object_contract", "library.persistence.backup_manifest", "library.persistence.recovery_objectives", "library.persistence.storage_identity"],
        "missing": ["library.persistence.wal_shipping_lineage"],
    },
    {
        "slug": "object_log_substrate", "intent": "Bind exact object primitives for a higher-level log algorithm without inferring transaction or consensus semantics.",
        "workloads": ["object_log_substrate"], "classes": ["enabling_object_log_primitive"],
        "clauses": [("object_rw", "all", ["object_namespace.put_object", "object_namespace.get_object_range"]), ("conditional_admission", "all", ["object_namespace.conditional_replace"]), ("integrity", "all", ["integrity.verify_checksum"])],
        "libraries": ["library.persistence.object_contract", "library.persistence.storage_identity", "library.persistence.integrity", "library.persistence.conformance_oracles"],
        "missing": [],
    },
    {
        "slug": "object_native_lakehouse_catalog", "intent": "Persist lakehouse catalog state through object-native manifests while preserving table/catalog authority separation.",
        "workloads": ["lakehouse_catalog", "catalog_state"], "classes": ["object_native_catalog", "object_native_lsm"],
        "clauses": [("object_rw", "all", ["object_namespace.put_object", "object_namespace.get_object_range"]), ("manifest", "all", ["manifest_inventory.write_manifest", "manifest_inventory.scan_manifests"]), ("commit_coordination", "any", ["commit_authority.commit_metadata_update", "object_namespace.conditional_replace"])],
        "libraries": ["library.persistence.object_contract", "library.persistence.catalog_contract", "library.persistence.commit_precondition", "library.persistence.commit_protocol", "library.persistence.snapshot_graph", "library.persistence.storage_identity"],
        "missing": ["library.persistence.manifest_publication"],
    },
]


def build_object_log_compiler_contracts(architectures: list[dict[str, Any]]) -> list[dict[str, Any]]:
    decision_refs = [f"decision.persistence.object_log.{slug}" for slug, *_ in OBJECT_LOG_DECISION_AXIS_SEEDS]
    all_capability_refs = {
        f"persistence.capability.{local_ref}"
        for refs in OBJECT_LOG_CLASS_CAPABILITIES.values()
        for local_ref in refs
    }
    offers = []
    for architecture in architectures:
        capability_refs = sorted(
            f"persistence.capability.{local_ref}"
            for local_ref in OBJECT_LOG_CLASS_CAPABILITIES[architecture["architecture_class"]]
        )
        offers.append({
            "record_kind": "durability_architecture_offer",
            "offer_id": f"offer.persistence.object_log.{architecture['architecture_id'].removeprefix('architecture.persistence.')}",
            "edition": EDITION,
            "status": "architecture_candidate_unqualified",
            "architecture_ref": architecture["architecture_id"],
            "architecture_class": architecture["architecture_class"],
            "provider_subject": {"name": architecture["organization"], "kind": architecture["organization_kind"]},
            "workload_classes": architecture["workload_classes"],
            "capability_claim_refs": capability_refs,
            "decision_refs": architecture["decision_refs"],
            "commit_frontier_roles": [stage["acknowledgement_role"] for stage in architecture["commit_path"]],
            "evidence_refs": architecture["evidence_refs"],
            "qualified_deployment_count": 0,
            "portable": False,
            "selectable": False,
            "claim_law": "Capability refs are architecture-level claims inferred from the reviewed design class. They are not implementation conformance or target-deployment evidence.",
            "qualification_gates": ["exact implementation and version identity", "exact deployment occurrence and provider semantics", "decision-value support", "correctness and failure-injection conformance", "finite latency throughput memory request egress and cost budgets", "recovery and garbage-collection proof", "independent appraisal"],
            "gaps": architecture["gaps"],
        })
    offer_by_ref = {row["architecture_ref"]: row for row in offers}
    requirements = []
    rules = []
    for profile in OBJECT_LOG_PROFILE_SEEDS:
        requirement_id = f"requirement.persistence.object_log.{profile['slug']}"
        clauses = [{
            "clause_id": f"clause.persistence.object_log.{profile['slug']}.{clause_slug}",
            "operator": operator,
            "capability_refs": [f"persistence.capability.{ref}" for ref in refs],
        } for clause_slug, operator, refs in profile["clauses"]]
        requirements.append({
            "record_kind": "durability_architecture_requirement",
            "requirement_id": requirement_id,
            "edition": EDITION,
            "status": "declared",
            "intent": profile["intent"],
            "required_workload_classes_any": profile["workloads"],
            "allowed_architecture_classes": profile["classes"],
            "required_capability_clauses": clauses,
            "decision_refs": decision_refs,
            "required_library_refs": profile["libraries"],
            "missing_library_contracts": profile["missing"],
            "evidence_gates": ["architecture evidence current", "exact provider offer", "exact deployment qualification", "all decisions explicit", "resource feasibility", "recovery and exit evidence"],
            "fallback_law": "refuse",
            "gaps": (["Missing exact reusable library contracts block implementation composition."] if profile["missing"] else []) + ["No architecture candidate is a selectable deployment offer until qualification."],
        })
        eligible = []
        for architecture in architectures:
            if architecture["architecture_class"] not in profile["classes"]:
                continue
            if not set(architecture["workload_classes"]) & set(profile["workloads"]):
                continue
            claims = set(offer_by_ref[architecture["architecture_id"]]["capability_claim_refs"])
            satisfied = True
            for clause in clauses:
                refs = set(clause["capability_refs"])
                satisfied = satisfied and (refs <= claims if clause["operator"] == "all" else bool(refs & claims))
            if satisfied:
                eligible.append(offer_by_ref[architecture["architecture_id"]]["offer_id"])
        rules.append({
            "record_kind": "durability_architecture_binding_rule",
            "binding_rule_id": f"binding_rule.persistence.object_log.{profile['slug']}",
            "edition": EDITION,
            "status": "declared",
            "requirement_ref": requirement_id,
            "eligible_architecture_offer_refs": sorted(eligible),
            "compatibility_clauses": ["architecture class is explicitly allowed", "at least one required workload class is evidenced", "every capability clause is satisfied without strengthening claims", "every decision axis resolves to a qualified deployment value", "required libraries are present and semantically owned", "resource recovery safety and exit gates pass"],
            "rejection_clauses": ["provider or product name used as capability proof", "architecture document treated as implementation conformance", "ordinary object-store semantics substituted for a required conditional or append primitive", "acknowledgement frontier inferred", "missing library contract waived", "unqualified architecture selected"],
            "selection_law": "The listed candidates only survive structural architecture filtering. The compiler must still bind exact libraries and a qualified deployment offer; currently every candidate remains non-selectable.",
            "current_outcome": "blocked_missing_libraries_and_or_qualified_deployment" if profile["missing"] else "blocked_no_qualified_deployment",
            "receipts": ["requirement and clause matrix", "candidate eliminations", "selected decision values", "library binding graph", "qualification evidence", "resource feasibility", "recovery and exit evidence"],
        })
    assert all(ref in all_capability_refs for row in requirements for clause in row["required_capability_clauses"] for ref in clause["capability_refs"])
    return [*requirements, *offers, *rules]


def build_context_map(contexts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_id = {row["context_id"]: row for row in contexts}
    relations = [
        ("object_namespace", "table_identity", "customer_supplier", "Object storage supplies byte identity/cuts; table identity remains independent."),
        ("columnar_file", "snapshot_state", "customer_supplier", "File format supplies readable files; table snapshot supplies exact membership."),
        ("commit_protocol", "commit_authority", "open_host_service", "Table commit requirements are published language consumed by catalog authority."),
        ("catalog_policy_binding", "commit_authority", "anti_corruption_layer", "Foreign policy decisions are translated to catalog grants/refusals."),
        ("snapshot_state", "compaction", "customer_supplier", "Maintenance reads table state and proposes a logically equivalent new state."),
        ("retention_immutability", "snapshot_expiry", "partnership", "Business/storage retention and table reachability jointly constrain expiry."),
        ("snapshot_expiry", "physical_deletion", "customer_supplier", "Expiry removes logical reachability; physical deletion requires separate authorization."),
        ("table_format_migration", "metadata_translation", "partnership", "Migration owns transition/cutover; translation owns representational mapping and loss."),
        ("asset_registry", "federated_namespace", "open_host_service", "Catalog assets are mounted through explicit foreign identity maps."),
        ("pushdown", "query_protocol", "anti_corruption_layer", "Remote protocol capabilities are translated into typed operations with residuals."),
        ("materialized_view", "freshness_contract", "customer_supplier", "Materialization publishes source/result frontiers used by freshness assessment."),
        ("share_publication", "presigned_delivery", "customer_supplier", "Publication authorizes a cut; delivery issues bounded byte-access grants."),
        ("schema_evolution", "logical_types", "partnership", "Schema changes rely on type compatibility while type owners do not own table history."),
        ("compression", "columnar_file", "conformist", "A file format selects supported codec profiles; codecs remain independent algorithms."),
        ("index_build", "serving_cutover", "customer_supplier", "An index build produces a qualified artifact; cutover decides visibility."),
        ("index_mutation", "search_visibility", "customer_supplier", "Mutation supplies epoch-scoped acknowledged frontiers; visibility independently proves which frontier a reader/searcher can observe."),
        ("backup", "restore", "customer_supplier", "Backup supplies a declared chain; restore independently proves recoverability."),
        ("replication", "backup", "separate_ways", "Replication protects availability and is never accepted as backup by implication."),
        ("cache_store", "result_cache", "customer_supplier", "Cache storage supplies eviction/TTL mechanics; result cache owns equivalence and dependency cuts."),
        ("vector_store", "vector_serving", "customer_supplier", "Store owns points/index state; serving owns routing, cut and approximation evidence."),
        ("time_series_store", "time_series_serving", "customer_supplier", "Store owns series persistence; serving owns tier/tail composition."),
    ]
    rows = []
    for source, target, relation, rationale in relations:
        sid, tid = context_id(source), context_id(target)
        assert sid in by_id and tid in by_id
        rows.append({
            "relation_id": f"persistence.relation.{source}.{target}",
            "edition": EDITION,
            "status": "candidate_not_adjudicated",
            "source_context_ref": sid,
            "target_context_ref": tid,
            "relationship_type": relation,
            "published_language": ["stable identities and editions", "typed operation intents/results", "receipts and invalidation triggers"],
            "translation_or_conformance": rationale,
            "failure_law": "Unknown, ambiguous or incompatible meaning is a typed compiler gap; no name-based coercion.",
            "gaps": ["direction and relationship type require joint context-owner adjudication"]
        })
    return rows


def build_term_overlaps(contexts: list[dict[str, Any]]) -> dict[str, Any]:
    owners: dict[str, set[str]] = defaultdict(set)
    for row in contexts:
        for term in row["inside"]:
            owners[term.casefold()].add(row["context_id"])
    overlaps = []
    for term, context_refs in sorted(owners.items()):
        if len(context_refs) > 1:
            overlaps.append({
                "term": term,
                "candidate_context_refs": sorted(context_refs),
                "status": "ownership_or_homonym_adjudication_required",
                "compiler_law": "The unqualified term is ambiguous. Resolve an owned qualified meaning or emit gap.persistence.ambiguous_term."
            })
    return {
        "registry_id": "san.domain-atlas.persistence-term-overlaps",
        "edition": EDITION,
        "status": "generated_review_queue",
        "completion_claim": False,
        "overlap_count": len(overlaps),
        "overlaps": overlaps
    }


def main() -> None:
    sources = build_sources()
    decisions = build_decisions()
    contexts, capabilities = build_contexts(decisions)
    boundaries = build_boundaries()
    library_boundaries = build_library_boundaries(boundaries, capabilities)
    compiler_mappings = build_compiler_mappings(capabilities)
    innovations = build_innovations()
    object_log_decisions = build_object_log_decision_points()
    object_log_architectures = build_object_log_architectures()
    object_log_compiler_contracts = build_object_log_compiler_contracts(object_log_architectures)
    context_map = build_context_map(contexts)
    term_overlaps = build_term_overlaps(contexts)

    dump_jsonl("sources.jsonl", sources)
    dump_jsonl("bounded-contexts.jsonl", contexts)
    dump_jsonl("decision-points.jsonl", decisions)
    dump_jsonl("storage-capabilities.jsonl", [row for row in capabilities if row["surface"] in {"storage", "file_format"}])
    dump_jsonl("table-capabilities.jsonl", [row for row in capabilities if row["surface"] == "table"])
    dump_jsonl("catalog-serving-capabilities.jsonl", [row for row in capabilities if row["surface"] not in {"storage", "file_format", "table"}])
    dump_jsonl("boundary-candidates.jsonl", boundaries)
    dump_jsonl("library-boundaries.jsonl", library_boundaries)
    dump_jsonl("compiler-mappings.jsonl", compiler_mappings)
    dump_jsonl("innovations.jsonl", innovations)
    dump_jsonl("object-log-decision-points.jsonl", object_log_decisions)
    dump_jsonl("object-log-architectures.jsonl", object_log_architectures)
    dump_jsonl("object-log-compiler-contracts.jsonl", object_log_compiler_contracts)
    dump_jsonl("context-map.jsonl", context_map)
    dump_json("term-ownership-overlaps.json", term_overlaps)

    family_counts = Counter(row["family_id"] for row in contexts)
    kind_counts = Counter(row["record_kind"] for row in boundaries)
    surface_counts = Counter(row["surface"] for row in capabilities)
    compiler_counts = Counter(row["record_kind"] for row in compiler_mappings)
    dump_json("coverage-report.json", {
        "corpus_id": "san.domain-atlas.persistence-lakehouse",
        "edition": EDITION,
        "status": "open_world_research_candidate",
        "completion_claim": False,
        "automation_posture": {
            "default": "deterministic_core",
            "optional_extension_ref": "universe.model_agent_extension",
            "law": "Generative models and tool agents are modeled once at an optional removable extension boundary. They do not appear as ambient fields, dependencies or laws in deterministic persistence contexts and libraries.",
            "authority": "An optional extension may propose configuration or diagnostics only through typed ports; deterministic validation, binding, execution receipts and accountable authority remain mandatory."
        },
        "counts": {
            "sources": len(sources),
            "bounded_contexts": len(contexts),
            "capabilities": len(capabilities),
            "decisions": len(decisions),
            "boundary_candidates": len(boundaries),
            "compiler_library_boundaries": len(library_boundaries),
            "compiler_mapping_records": len(compiler_mappings),
            "innovations_2021_2026": len(innovations),
            "object_log_architectures": len(object_log_architectures),
            "object_log_decision_points": len(object_log_decisions),
            "object_log_compiler_contracts": len(object_log_compiler_contracts),
            "context_relations": len(context_map),
            "term_ownership_overlaps": term_overlaps["overlap_count"],
        },
        "bounded_contexts_by_family": dict(sorted(family_counts.items())),
        "capabilities_by_surface": dict(sorted(surface_counts.items())),
        "boundary_candidates_by_kind": dict(sorted(kind_counts.items())),
        "compiler_records_by_kind": dict(sorted(compiler_counts.items())),
        "coverage_laws": [
            "format != protocol != implementation != deployment != product != managed experience != suite",
            "compression and encoding are independent kernels; compaction and clustering are maintenance operations",
            "table state does not own catalog authority, object durability, query semantics or business meaning",
            "lakehouse is a composition boundary and never a new semantic owner",
            "unknown capability, feature, limit or authority is a typed blocking gap"
        ],
        "terminology_findings": {
            "recognized_database_workloads": ["OLTP", "OLAP", "HTAP"],
            "unresolved_user_term": "OLHP",
            "law": "OLHP was not established as a recognized database workload acronym by the reviewed primary/official corpus. It must remain unresolved rather than being silently coerced to OLTP, OLAP or HTAP."
        }
    })
    write_manifest()
    print(
        f"built persistence/lakehouse corpus: {len(sources)} sources, {len(contexts)} contexts, "
        f"{len(capabilities)} capabilities, {len(decisions)} decisions, {len(boundaries)} boundaries, "
        f"{len(library_boundaries)} compiler libraries, {len(compiler_mappings)} compiler records, "
        f"{len(innovations)} innovations, {len(object_log_architectures)} object-log architectures, "
        f"{len(object_log_decisions)} object-log decisions, {len(object_log_compiler_contracts)} object-log compiler contracts"
    )


if __name__ == "__main__":
    main()
