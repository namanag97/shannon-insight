#!/usr/bin/env python3
"""Build the evidence-backed query, OLAP, warehouse and lakehouse-seam semantic slice."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
SEM = HERE.parent
REGISTRY = SEM.parents[1]
AS_OF = "2026-08-27"
PRODUCTS = {
    "product.query_execution_service",
    "product.managed_warehouse_experience",
    "product.managed_lakehouse_experience",
    "product.virtual_data_access",
}
AXES = [
    "semantic_object", "semantic_role", "identity_and_equality", "grain_and_cardinality",
    "state_and_change", "time", "order_and_topology", "partiality_and_uncertainty",
    "authority_and_trust", "effect_boundary", "representation", "composition_algebra",
    "compatibility_and_evolution", "resources_and_failure", "evidence_and_conformance",
    "privacy_security_safety",
]
NEIGHBORS = {
    "library.qck.adaptive-execution", "library.qck.codec-kernels",
    "library.qck.expression-kernels", "library.qck.kernel-conformance",
    "library.qck.numerical-kernels", "library.qck.numerical-semantics",
    "library.qck.relational-kernels", "library.qck.udf-extension-host",
    "library.persistence.catalog_contract", "library.persistence.columnar_layout",
    "library.persistence.file_statistics", "library.persistence.logical_equivalence_oracle",
    "library.persistence.logical_types", "library.persistence.partition_algebra",
    "library.persistence.scan_planner", "library.persistence.schema_evolution",
    "library.persistence.snapshot_graph", "library.persistence.table_format_acl",
    "library.persistence.table_identity", "library.persistence.value_encoding",
}


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def slug(value: str) -> str:
    return value.replace("_", "-").replace(".", "-")


def product_rows() -> list[dict[str, Any]]:
    return load_jsonl(SEM / "product_coordinate_binding_projection/subject-coordinate-binding-projections.jsonl")


def declared_product_libraries() -> set[str]:
    return {
        edge["concrete_library_ref"]
        for row in product_rows() if row["product_ref"] in PRODUCTS
        for edge in row["concrete_bindings"]
    }


LIBRARIES = sorted(declared_product_libraries() | NEIGHBORS)


SOURCE_ROWS = [
    ("codd-relational", "A Relational Model of Data for Large Shared Data Banks", ["E. F. Codd"], 1970, "peer_reviewed_foundational_paper", "https://doi.org/10.1145/362384.362685", "Defines relations and data independence from physical representation.", "Does not define SQL bags, nulls, distributed execution, table formats or product packaging."),
    ("sql-2023", "ISO/IEC 9075-2:2023 SQL/Foundation", ["ISO/IEC JTC 1/SC 32"], 2023, "international_standard", "https://www.iso.org/standard/76584.html", "Current published SQL foundation edition for SQL data structures and operations.", "The public ISO page proves edition and scope, not implementation conformance or every clause's detailed semantics."),
    ("sql-corrigendum-2026", "ISO/IEC 9075-2:2023/Cor 1:2026", ["ISO/IEC JTC 1/SC 32"], 2026, "international_standard_corrigendum", "https://www.iso.org/standard/93691.html", "Establishes the current corrigendum as a separate editioned correction input.", "A corrigendum identifier alone does not prove that a provider has implemented it."),
    ("selinger", "Access Path Selection in a Relational Database Management System", ["Patricia G. Selinger", "Morton M. Astrahan", "Donald D. Chamberlin", "Raymond A. Lorie", "Thomas G. Price"], 1979, "peer_reviewed_primary_paper", "https://doi.org/10.1145/582095.582099", "Separates nonprocedural query intent from cost-based join order and access-path selection.", "System R's cost model and search space are not universal optimizer semantics."),
    ("volcano-optimizer", "The Volcano Optimizer Generator: Extensibility and Efficient Search", ["Goetz Graefe", "William J. McKenna"], 1993, "peer_reviewed_primary_paper", "https://www.cs.cornell.edu/~mshong/DDG_Fall05/Volcano.pdf", "Separates logical algebra, physical algebra, transformations, properties, costs and search.", "One optimizer framework does not establish equivalence, cost accuracy or fitness for every workload."),
    ("calcite-algebra", "Apache Calcite Algebra", ["Apache Calcite project"], 2026, "official_implementation_specification", "https://calcite.apache.org/docs/algebra.html", "Documents relational expression trees, semantics-preserving planner rules and cost-guided alternatives.", "Calcite APIs and rules are an implementation surface, not universal query authority."),
    ("calcite-adapters", "Apache Calcite Adapters", ["Apache Calcite project"], 2026, "official_implementation_specification", "https://calcite.apache.org/docs/adapter.html", "Documents adapter-mediated access and pushdown across heterogeneous stores.", "Adapter availability does not prove lossless translation or source capability for a particular invocation."),
    ("gray-cube", "Data Cube: A Relational Aggregation Operator Generalizing Group-By, Cross-Tab, and Sub-Totals", ["Jim Gray", "Surajit Chaudhuri", "Adam Bosworth", "Andrew Layman", "Don Reichart", "Murali Venkatrao", "Frank Pellow", "Hamid Pirahesh"], 1997, "peer_reviewed_primary_paper", "https://www.cs.cmu.edu/~natassa/courses/15-721/papers/cube_op.pdf", "Defines multidimensional cube aggregation as a relational generalization of grouping and subtotals.", "Cube syntax does not supply business measure ownership, hierarchy validity or summarizability."),
    ("warehouse-olap", "An Overview of Data Warehousing and OLAP Technology", ["Surajit Chaudhuri", "Umeshwar Dayal"], 1997, "peer_reviewed_survey", "https://sigmodrecord.org/1997/03/15/an-overview-of-data-warehousing-and-olap-technology/", "Separates warehouse acquisition, multidimensional models, front ends, query processing and metadata management.", "The survey is an architecture decomposition, not a current product contract."),
    ("summarizability", "Summarizability in OLAP and Statistical Data Bases", ["Hans-Joachim Lenz", "Arie Shoshani"], 1997, "peer_reviewed_primary_paper", "https://doi.org/10.1109/SSDM.1997.621175", "Shows that valid roll-up requires explicit statistical-object context and summarizability conditions.", "Its conditions require domain-specific grain, hierarchy and measure semantics."),
    ("isolation-critique", "A Critique of ANSI SQL Isolation Levels", ["Hal Berenson", "Philip A. Bernstein", "Jim Gray", "Jim Melton", "Elizabeth O'Neil", "Patrick O'Neil"], 1995, "peer_reviewed_primary_paper", "https://www.microsoft.com/en-us/research/publication/a-critique-of-ansi-sql-isolation-levels/", "Separates named isolation levels, phenomena, histories, snapshot isolation and serializability.", "The taxonomy does not bind a query to a provider's actual concurrency implementation."),
    ("postgres-isolation", "PostgreSQL Transaction Isolation", ["PostgreSQL Global Development Group"], 2026, "official_provider_documentation", "https://www.postgresql.org/docs/current/transaction-iso.html", "Documents provider-specific snapshot timing and anomaly behavior for isolation levels.", "PostgreSQL behavior is not a universal SQL or federation guarantee."),
    ("postgres-select", "PostgreSQL SELECT", ["PostgreSQL Global Development Group"], 2026, "official_provider_documentation", "https://www.postgresql.org/docs/current/sql-select.html", "Documents ordering, grouping, set operations, limits, locking and evaluation stages for one provider.", "Provider syntax and defaults do not define a portable result contract."),
    ("substrait", "Substrait Specification", ["Substrait project"], 2026, "official_interchange_specification", "https://substrait.io/spec/specification/", "Defines cross-language serialized types, expressions and relational plans with extension points.", "The specification is pre-1.0 and serialization does not prove semantic completeness, implementability or equivalence."),
    ("substrait-physical", "Substrait Physical Relations", ["Substrait project"], 2026, "official_interchange_specification", "https://substrait.io/relations/physical_relations/", "Makes join, exchange, aggregate, window, ordering and residual properties explicit in physical relation candidates.", "Substrait itself states that logical/physical classification is consumer convention, not intrinsic plan truth."),
    ("arrow-columnar", "Apache Arrow Columnar Format", ["Apache Arrow project"], 2026, "official_data_format_specification", "https://arrow.apache.org/docs/format/Columnar.html", "Defines arrays, schemas, record batches, physical layouts, null buffers and IPC carriers.", "Physical layout and transport do not define relational meaning, business types or query correctness."),
    ("arrow-flight-sql", "Apache Arrow Flight SQL", ["Apache Arrow project"], 2026, "official_protocol_specification", "https://arrow.apache.org/docs/format/FlightSql.html", "Defines SQL commands, metadata, sessions and Arrow result transport over Flight.", "Protocol interoperability does not prove identical SQL semantics, snapshots, ordering or provider qualification."),
    ("adbc", "ADBC API Standard", ["Apache Arrow project"], 2026, "official_api_specification", "https://arrow.apache.org/adbc/main/format/specification.html", "Defines a cross-language Arrow-native database access API including partitioned/incremental results.", "A client API does not own query language semantics or remote transaction guarantees."),
    ("parquet", "Apache Parquet File Format", ["Apache Parquet project"], 2026, "official_data_format_specification", "https://parquet.apache.org/docs/file-format/", "Defines columnar file layout, metadata and encodings used by analytical scans.", "A file format is not a table, catalog, snapshot, transaction or query result contract."),
    ("trino-connectors", "Trino Connector Developer Guide", ["Trino Software Foundation"], 2026, "official_provider_documentation", "https://trino.io/docs/current/develop/connectors.html", "Defines invocation-specific connector capabilities and partial predicate residual return.", "Connector methods and handles are provider contracts, not source semantic authority."),
    ("trino-pushdown", "Trino Pushdown", ["Trino Software Foundation"], 2026, "official_provider_documentation", "https://trino.io/docs/current/optimizer/pushdown.html", "Documents connector-specific predicate, projection, aggregation, join and limit pushdown.", "A pushed operation is not automatically lossless; capability and residuals remain invocation-specific."),
    ("trino-dynamic", "Trino Dynamic Filtering", ["Trino Software Foundation"], 2026, "official_provider_documentation", "https://trino.io/docs/current/admin/dynamic-filtering.html", "Documents runtime-derived filters, collection thresholds and connector-specific application.", "Runtime filtering is a physical optimization and must not change logical result semantics."),
    ("iceberg", "Apache Iceberg Table Specification", ["Apache Iceberg project"], 2026, "official_table_format_specification", "https://iceberg.apache.org/spec/", "Defines table metadata, stable IDs, schemas, partition specs, snapshots, manifests and delete semantics.", "Table state semantics do not own SQL, catalog authority, query planning or managed lakehouse lifecycle."),
    ("iceberg-rest", "Apache Iceberg REST Catalog OpenAPI", ["Apache Iceberg project"], 2026, "official_protocol_specification", "https://github.com/apache/iceberg/blob/main/open-api/rest-catalog-open-api.yaml", "Defines an interoperable catalog protocol separately from table files and engines.", "Protocol conformance does not establish catalog governance, authorization, availability or table-format correctness."),
    ("delta-protocol", "Delta Transaction Log Protocol", ["Delta Lake project"], 2026, "official_table_protocol_specification", "https://github.com/delta-io/delta/blob/master/PROTOCOL.md", "Defines protocol versions, log actions, atomic table versions, features and deletion vectors.", "A Delta table protocol is neither a generic relational engine nor a complete lakehouse product."),
    ("hudi-spec", "Apache Hudi Technical Specifications", ["Apache Hudi project"], 2026, "official_table_format_specification", "https://hudi.apache.org/tech-specs/", "Defines timeline instants, file groups/slices and copy-on-write/merge-on-read table mechanics.", "Hudi storage/timeline semantics do not define universal snapshot isolation or query meaning."),
    ("lakehouse-paper", "Lakehouse: A New Generation of Open Platforms that Unify Data Warehousing and Advanced Analytics", ["Michael Armbrust", "Ali Ghodsi", "Reynold Xin", "Matei Zaharia"], 2021, "peer_reviewed_architecture_paper", "https://www.vldb.org/cidrdb/2021/lakehouse-a-new-generation-of-open-platforms-that-unify-data-warehousing-and-advanced-analytics.html", "Proposes lakehouse as an architecture pattern based on open direct-access formats, multiple workloads and warehouse-class performance.", "One paper and benchmark do not establish a monolithic product, universal superiority or semantic ownership."),
    ("velox", "Velox: Meta's Unified Execution Engine", ["Meta Velox authors"], 2022, "peer_reviewed_system_paper", "https://www.vldb.org/pvldb/vol15/p3372-pedreira.pdf", "Demonstrates a reusable composable execution engine across analytical systems.", "An execution provider does not own SQL, OLAP, table, catalog or business semantics."),
    ("x100", "MonetDB/X100: Hyper-Pipelining Query Execution", ["Peter Boncz", "Marcin Zukowski", "Niels Nes"], 2005, "peer_reviewed_system_paper", "https://www.cidrdb.org/cidr2005/papers/P19.pdf", "Establishes vector-at-a-time execution as a CPU-efficient alternative to tuple interpretation and full-column materialization.", "The execution model is a performance choice, not a logical semantics or universal optimum."),
    ("morsel", "Morsel-Driven Parallelism", ["Viktor Leis", "Peter Boncz", "Alfons Kemper", "Thomas Neumann"], 2014, "peer_reviewed_system_paper", "https://doi.org/10.1145/2588555.2610507", "Defines fine-grained NUMA-aware task scheduling with elastic execution parallelism.", "Scheduling technique does not define workload admission, fairness or query meaning."),
    ("duckdb", "DuckDB: an Embeddable Analytical Database", ["Mark Raasveldt", "Hannes Mühleisen"], 2019, "peer_reviewed_system_paper", "https://doi.org/10.1145/3299869.3320212", "Demonstrates an in-process vectorized analytical DBMS and tight data-frame integration.", "An embeddable provider remains an implementation, not the semantic owner of portable queries."),
    ("tpc-h", "TPC-H Benchmark", ["Transaction Processing Performance Council"], 2026, "official_benchmark_specification", "https://www.tpc.org/tpch/", "Defines a decision-support benchmark workload and audited result rules.", "TPC-H is one synthetic workload; benchmark success is not general fitness or semantic conformance."),
    ("tpc-ds", "TPC-DS Benchmark", ["Transaction Processing Performance Council"], 2026, "official_benchmark_specification", "https://www.tpc.org/tpcds/", "Defines a decision-support suite with reporting, interactive and data-mining query classes.", "TPC-DS cannot qualify every workload, scale, data distribution, failure mode or cost posture."),
]


def sources() -> list[dict[str, Any]]:
    return [{"source_id": f"source.query.{sid}", "title": title, "authors": authors, "year": year,
             "source_kind": kind, "url": url, "supported_claim": claim,
             "authority_limit": limit, "primary_or_official": True,
             "status": "INDEPENDENTLY_LOCATED_PRIMARY_OR_OFFICIAL"}
            for sid, title, authors, year, kind, url, claim, limit in SOURCE_ROWS]


MODULE_ROWS = [
    ("query-intent", "Which editioned query occurrence states what requested relation/result independently of execution strategy?", "declarative query contract", ["codd-relational", "sql-2023"], []),
    ("session-context", "Which catalog, schema, role, timezone, collation, locale, parameters and defaults bind one query occurrence?", "editioned environment value", ["sql-2023", "arrow-flight-sql"], ["query-intent"]),
    ("name-binding", "How do identifiers resolve to exact catalog objects, columns, functions and editions without lexical guessing?", "name-resolution relation", ["sql-2023", "calcite-algebra"], ["session-context"]),
    ("catalog-capability", "Which catalog can resolve which table/view/function identities under which authority and freshness?", "catalog capability contract", ["iceberg-rest", "trino-connectors"], ["name-binding"]),
    ("relation-schema", "What relation occurrence, heading/schema, tuple/row and attribute/column are denoted?", "relational model", ["codd-relational", "sql-2023"], ["name-binding"]),
    ("type-value", "Which logical type, domain, precision, scale, timezone, collation and value semantics apply?", "typed value algebra", ["sql-2023", "substrait", "arrow-columnar"], ["relation-schema"]),
    ("bag-multiplicity", "Are results sets, bags or ordered sequences, and how do duplicates arise or disappear?", "bag/set algebra", ["sql-2023", "substrait"], ["relation-schema"]),
    ("null-three-valued", "How do null, unknown, absent, inapplicable and SQL three-valued predicates propagate?", "partial-information logic", ["sql-2023", "postgres-select"], ["type-value"]),
    ("equality-comparison", "Which equality, distinctness, comparison, NaN, collation and hashing relation applies?", "typed comparison algebra", ["sql-2023", "substrait"], ["type-value", "null-three-valued"]),
    ("ordering-topn", "Which total/partial ordering, tie policy, null placement and stable key make order, limit and top-N deterministic?", "order/topology contract", ["postgres-select", "substrait-physical", "trino-connectors"], ["equality-comparison"]),
    ("function-semantics", "Which scalar, aggregate, window or table function edition, null behavior, volatility, error and numerical guarantees apply?", "function contract", ["sql-2023", "substrait"], ["type-value"]),
    ("relational-operators", "What are the typed semantics of scan, select, project, join, aggregate, window, set and recursive operations?", "relational algebra", ["codd-relational", "calcite-algebra", "substrait"], ["bag-multiplicity", "null-three-valued", "function-semantics"]),
    ("olap-cube", "Which facts, dimensions, levels, hierarchies, grouping sets, cube cells, roll-ups, drill-downs and slices are denoted?", "multidimensional algebra", ["gray-cube", "warehouse-olap"], ["relational-operators"]),
    ("analytical-grain", "What is the fact occurrence grain and which dimensional keys are complete, exclusive and temporally valid?", "grain/cardinality model", ["warehouse-olap", "summarizability"], ["olap-cube"]),
    ("aggregation-algebra", "Which aggregate is distributive, algebraic, holistic, approximate, order-sensitive or non-decomposable?", "aggregation algebra", ["gray-cube", "substrait-physical"], ["function-semantics", "analytical-grain"]),
    ("summarizability", "When may measures be rolled across hierarchies without double counting, omissions or semantic invalidity?", "summarizability constraint system", ["summarizability", "gray-cube"], ["aggregation-algebra", "analytical-grain"]),
    ("logical-plan", "Which typed logical plan represents bound query meaning independently of physical execution?", "logical plan IR", ["calcite-algebra", "substrait"], ["relational-operators"]),
    ("plan-equivalence", "Under which bag, null, error, volatility and order laws are two plans equivalent?", "equivalence relation/oracle", ["calcite-algebra", "volcano-optimizer"], ["logical-plan", "ordering-topn"]),
    ("rewrite-contract", "Which preconditions, preserved properties, counterexamples and proof obligations authorize each rewrite?", "conditional rewrite algebra", ["calcite-algebra", "volcano-optimizer"], ["plan-equivalence"]),
    ("statistics-properties", "Which row-count, distinctness, null, range, distribution, correlation and ordering claims describe an exact data cut?", "bounded property evidence", ["selinger", "trino-dynamic"], ["logical-plan"]),
    ("cardinality-estimate", "Which estimator predicts intermediate cardinality with what uncertainty and stale-statistics posture?", "cost-model estimate", ["selinger", "volcano-optimizer"], ["statistics-properties"]),
    ("cost-search", "Which plan search space, objective vector, resource model, pruning rule and uncertainty posture select candidates?", "multiobjective optimization", ["selinger", "volcano-optimizer"], ["cardinality-estimate", "rewrite-contract"]),
    ("physical-properties", "Which order, partition, distribution, materialization, vector width and locality properties are required or delivered?", "physical property lattice", ["volcano-optimizer", "substrait-physical"], ["logical-plan"]),
    ("physical-plan", "Which operators, algorithms, exchanges, kernels and target capabilities lower a logical plan?", "physical plan IR", ["substrait-physical", "velox"], ["cost-search", "physical-properties"]),
    ("scan-snapshot", "Which exact table identity, schema, partition spec, snapshot/version, delete semantics and file set does a scan bind?", "table-format ACL contract", ["iceberg", "delta-protocol", "hudi-spec"], ["catalog-capability", "physical-plan"]),
    ("transaction-isolation", "Which statement/transaction snapshot, history constraints and anomalies bound a query result?", "transaction history model", ["isolation-critique", "postgres-isolation"], ["scan-snapshot"]),
    ("connector-capability", "Which operation, type, snapshot, ordering and failure guarantees can a connector offer for this invocation?", "capability negotiation", ["trino-connectors", "calcite-adapters"], ["physical-plan", "catalog-capability"]),
    ("pushdown-residual", "What exact predicate/operator was translated, what loss occurred and what residual must execute locally?", "translation-with-residual algebra", ["trino-connectors", "trino-pushdown"], ["connector-capability", "plan-equivalence"]),
    ("federated-data-cut", "Which per-source snapshots, clocks, transaction scopes and cross-source consistency claim compose one federated result?", "federated cut model", ["trino-connectors", "postgres-isolation"], ["transaction-isolation", "pushdown-residual"]),
    ("materialized-view", "Which query, data cut, refresh state and equivalence proof define a materialization usable for rewrite?", "materialization identity/equivalence", ["calcite-algebra", "warehouse-olap"], ["plan-equivalence", "scan-snapshot"]),
    ("virtual-relation", "Which declared query and dependency editions identify a virtual relation across lifecycle changes?", "virtual relation lifecycle", ["sql-2023", "calcite-algebra"], ["logical-plan", "catalog-capability"]),
    ("cache-identity", "Which normalized query, session, authority, snapshot, result contract and freshness policy identify a reusable cache entry?", "cache key/invalidation algebra", ["isolation-critique", "postgres-isolation"], ["federated-data-cut", "ordering-topn"]),
    ("columnar-carrier", "Which logical schema maps to Arrow arrays or Parquet columns at what edition and declared loss?", "physical carrier/ACL", ["arrow-columnar", "parquet"], ["type-value"]),
    ("vector-kernels", "Which vector/batch kernels preserve function, null, error, order and numerical semantics?", "kernel algebra", ["x100", "velox", "arrow-columnar"], ["function-semantics", "columnar-carrier"]),
    ("codec-encoding", "Which encoding, dictionary, compression, endian and corruption behavior preserves or refuses values?", "codec contract", ["arrow-columnar", "parquet"], ["columnar-carrier"]),
    ("exchange-runtime", "Which partitioning, broadcast, shuffle, merge and capture operation preserves required properties?", "distributed exchange algebra", ["substrait-physical", "morsel"], ["physical-properties"]),
    ("scheduling-admission", "Which workload class, quota, reservation, fairness, deadline and precharge govern admission and scheduling?", "resource-control policy import", ["morsel", "trino-dynamic"], ["physical-plan"]),
    ("memory-spill", "Which memory ownership, revocation, spill, backpressure, disk budget and failure semantics apply?", "resource state machine", ["velox", "x100"], ["vector-kernels", "scheduling-admission"]),
    ("adaptive-execution", "Which observations may trigger runtime filters, replanning or parallelism changes without changing semantics?", "observed policy/state machine", ["trino-dynamic", "morsel"], ["plan-equivalence", "statistics-properties", "physical-plan"]),
    ("result-contract", "Which schema, multiplicity, order, data cut, partiality, warnings and completion state define the result?", "result envelope", ["sql-2023", "arrow-flight-sql", "adbc"], ["ordering-topn", "federated-data-cut"]),
    ("result-stream", "Which partitions/batches, ordering, resume, cancellation and terminal state constitute one result stream?", "stream lifecycle protocol", ["arrow-flight-sql", "adbc", "arrow-columnar"], ["result-contract", "exchange-runtime"]),
    ("query-receipt", "Which intent, bindings, plan editions, source cuts, translations, resources, diagnostics and result digest form evidence?", "provenance/evidence envelope", ["substrait", "trino-connectors"], ["result-contract", "physical-plan"]),
    ("export-materialization", "How is a result handed to export/publication without collapsing query completion into delivery or publication?", "effect-intent boundary", ["arrow-flight-sql", "warehouse-olap"], ["result-contract"]),
    ("warehouse-experience", "Which managed environment, workload, export, resource and lifecycle profile composes a warehouse experience?", "product composition", ["warehouse-olap", "tpc-ds"], ["scheduling-admission", "export-materialization"]),
    ("lakehouse-pattern", "Which open table, catalog, engine, maintenance, sharing and workload contracts compose a lakehouse architecture?", "architecture pattern/composition", ["lakehouse-paper", "iceberg", "delta-protocol", "hudi-spec"], ["scan-snapshot", "warehouse-experience"]),
    ("benchmark-evidence", "Which workload edition, scale, data generator, run rules, hardware, price and audit scope support a performance claim?", "bounded benchmark evidence", ["tpc-h", "tpc-ds", "lakehouse-paper"], ["physical-plan", "result-contract"]),
]


def modules() -> list[dict[str, Any]]:
    return [{"module_id": f"module.query.{mid}", "owned_question": question, "formalism": formalism,
             "source_refs": [f"source.query.{ref}" for ref in refs],
             "dependency_refs": [f"module.query.{ref}" for ref in deps],
             "research_status": "EVIDENCE_BACKED_UNRATIFIED",
             "authority_limit": "The module proposes bounded query/OLAP semantics; it does not ratify an owner, select a contract, qualify an implementation or close a canonical gap."}
            for mid, question, formalism, refs, deps in MODULE_ROWS]


LAW_ROWS = [
    ("relation-storage", "A logical relation is not its row, column, file, object or memory representation."),
    ("query-plan", "A declarative query is not a logical plan, physical plan, execution attempt or result occurrence."),
    ("logical-physical", "Logical operators and physical algorithms must not collapse."),
    ("syntax-semantics", "Successful parsing or serialization does not establish binding, meaning or executability."),
    ("plan-equivalence-cost", "Lower estimated cost does not prove semantic equivalence or lower realized cost."),
    ("estimate-fact", "Cardinality and cost estimates are not observed cardinalities or resource facts."),
    ("set-bag-sequence", "Set, bag/multiset and ordered sequence semantics must remain distinct."),
    ("row-entity", "A row occurrence is not automatically a business entity or event."),
    ("column-attribute", "A physical column is not automatically one logical attribute or semantic measure."),
    ("null-zero", "Null, unknown, absent, inapplicable, empty and numerical zero must not collapse."),
    ("null-false", "SQL unknown is not Boolean false."),
    ("equality-distinctness", "Equality, not-distinct, ordering equality, hash equality and identity are separate relations."),
    ("collation-bytes", "Collation equality/order is not byte equality/order."),
    ("nan-null", "NaN and null are different partiality/value states."),
    ("unordered-stable", "A result without a complete ordering key has no stable row order guarantee."),
    ("limit-topn", "LIMIT without a total order is not deterministic top-N."),
    ("tie-order", "A partial sort key does not decide order among ties."),
    ("function-name-edition", "Equal function names do not imply equal null, error, volatility, numerical or timezone semantics."),
    ("deterministic-immutable", "Deterministic for one invocation is not immutable across data, session or edition changes."),
    ("aggregate-measure", "A SQL aggregate is not a governed business measure definition."),
    ("cube-product", "A data cube is an analytical algebra/result space, not a vendor product or lakehouse."),
    ("dimension-table", "An OLAP dimension is not merely a table named dimension."),
    ("hierarchy-order", "A dimension hierarchy is not generic sort order or arbitrary parent-child edges."),
    ("rollup-sum", "Roll-up is not universally SUM and is invalid when grain/hierarchy/measure summarizability fails."),
    ("grain-rowcount", "Analytical grain is not row count."),
    ("additive-universal", "A measure additive over one dimension is not necessarily additive over all dimensions."),
    ("grouping-detail", "A subtotal cell and a detail row remain different semantic occurrences even when values coincide."),
    ("rewrite-similarity", "Syntactic similarity is not query equivalence."),
    ("rewrite-success", "A provider accepting a rewritten plan does not prove semantic preservation."),
    ("statistics-truth", "Catalog/table statistics are scoped observations or estimates, not timeless truth."),
    ("physical-property-logical", "Ordering, partitioning, locality and vector width are physical properties unless explicitly visible in the result contract."),
    ("format-table", "Parquet/Arrow files or batches are not tables, snapshots, transactions or catalogs."),
    ("table-catalog", "Table-format state and catalog authority are separate bounded contexts."),
    ("snapshot-latest", "A bound snapshot/version is not the moving notion of latest."),
    ("snapshot-serializable", "Snapshot isolation and serializability must not collapse."),
    ("statement-transaction-snapshot", "Statement and transaction snapshot cuts must not collapse."),
    ("source-cuts-global", "Independent source snapshots do not automatically form one globally consistent federated cut."),
    ("connector-capability", "A connector's general feature support is not proof that a particular invocation was lossless or guaranteed."),
    ("pushdown-equivalence", "Pushdown is an optimization only when translated semantics plus residual equal the original operation."),
    ("residual-empty", "An omitted residual is not evidence that translation was complete."),
    ("virtual-materialized", "Virtual relation, materialized view, result cache and exported dataset identities must remain distinct."),
    ("cache-result", "A cache hit is not proof of freshness, authorization equivalence or snapshot equivalence."),
    ("carrier-meaning", "Arrow/Substrait/Parquet representation compatibility does not imply semantic compatibility."),
    ("kernel-api-semantics", "A successful kernel call does not prove the requested null, error, precision or determinism contract."),
    ("exchange-order", "Shuffle/capture may destroy order; distribution equality is not sequence equality."),
    ("parallelism-determinism", "Parallel execution may preserve relational results while changing order, timing and floating-point reduction outcomes."),
    ("adaptive-semantic", "Adaptive execution may change physical strategy but must not silently change query meaning."),
    ("spill-success", "Successful spill does not establish bounded latency, confidentiality or durable result completion."),
    ("admission-execution", "Admission, scheduling, execution start, execution completion and result delivery are distinct states."),
    ("query-delivery", "Query completion is not export delivery, publication, downstream adoption or business outcome."),
    ("receipt-proof", "A query receipt is bounded execution evidence, not proof that inputs or business semantics were correct."),
    ("benchmark-conformance", "Benchmark performance is not semantic conformance or fitness for unrelated workloads."),
    ("benchmark-universal", "TPC-H/TPC-DS performance does not establish universal performance, cost, reliability or scale."),
    ("warehouse-engine", "A managed warehouse experience is not the query engine, table format, catalog or resource substrate it composes."),
    ("lakehouse-product", "Lakehouse is an architecture pattern; a suite may package products but does not become one semantic owner."),
    ("lakehouse-table", "An open table format alone is not a lakehouse."),
    ("lakehouse-warehouse", "Lakehouse and warehouse packaging must not erase independent table, catalog, query, maintenance, sharing and governance contracts."),
    ("ai-authority", "AI or agents may propose queries/plans but cannot infer hidden grain, choose semantic defaults, waive residuals or authorize effects."),
]


def laws() -> list[dict[str, Any]]:
    return [{"law_id": f"law.query.non-collapse.{lid}", "statement": statement,
             "status": "EVIDENCE_BACKED_UNRATIFIED", "canonical_gaps_closed": 0}
            for lid, statement in LAW_ROWS]


METHOD_GROUPS = {
    "language_and_binding": ["SQL parsing", "parameter binding", "catalog resolution", "schema resolution", "column binding", "function overload resolution", "type coercion", "collation binding", "session-context binding", "authorization-context projection"],
    "relational_operations": ["scan", "selection/filter", "projection", "inner join", "outer join", "semi/anti join", "cross join", "aggregation", "window evaluation", "sort", "limit/top-N", "set union/intersection/difference", "unnest/table function", "recursive query"],
    "olap": ["grouping sets", "rollup", "cube", "slice", "dice", "pivot/unpivot", "drill-down", "roll-up", "hierarchy navigation", "subtotal construction", "summarizability validation", "aggregate decomposition"],
    "optimization": ["normalization", "constant folding", "predicate simplification", "decorrelation", "predicate pushdown", "projection pruning", "join reordering", "aggregate pushdown", "limit/top-N pushdown", "partition pruning", "statistics derivation", "cardinality estimation", "cost estimation", "memoized plan search", "materialized-view substitution", "runtime-filter planning", "adaptive reoptimization"],
    "physical_execution": ["sequential scan", "index scan", "columnar scan", "nested-loop join", "hash join", "merge join", "hash aggregation", "streaming aggregation", "external sort", "vectorized expression evaluation", "compiled expression evaluation", "exchange/shuffle", "broadcast", "ordered merge capture", "morsel scheduling", "spill/reload", "fault-tolerant stage retry"],
    "federation_and_virtualization": ["connector capability negotiation", "type translation", "function translation", "predicate translation", "residual evaluation", "source snapshot binding", "cross-source cut construction", "virtual relation resolution", "remote query fragmentation", "remote result reconciliation"],
    "result_and_delivery": ["result schema construction", "result ordering validation", "partitioned result streaming", "Arrow IPC delivery", "Flight SQL delivery", "ADBC retrieval", "cache lookup", "cache fill coordination", "materialization publication", "export encoding", "query receipt construction", "cancellation and terminal-state handling"],
    "table_and_carrier_acl": ["Iceberg snapshot scan binding", "Delta log-version scan binding", "Hudi timeline scan binding", "Parquet decoding", "Arrow batch construction", "dictionary decoding", "compression decoding", "delete-file application", "schema evolution projection", "partition transform evaluation"],
    "assurance": ["equivalence property testing", "rewrite negative twins", "differential engine testing", "SQL logic testing", "kernel conformance testing", "connector residual testing", "isolation-history testing", "summarizability testing", "benchmark execution", "result replay verification"],
}


def methods() -> list[dict[str, Any]]:
    return [{"method_type_id": f"method.query.{slug(group)}.{slug(name)}", "method_group": group,
             "name": name,
             "selection_law": "Selection requires bound semantics, target capabilities, equivalence/residual proof, exact data cut, physical properties, resource budget and conformance evidence; category membership is not substitutability.",
             "status": "TAXONOMY_CANDIDATE_UNRATIFIED"}
            for group, names in METHOD_GROUPS.items() for name in names]


EXPERT_ROWS = [
    ("codd", "Edgar F. Codd", ["codd-relational"], ["Keep logical relation semantics independent of storage and access paths.", "Do not let provider layout become the public query model."]),
    ("selinger", "Patricia G. Selinger", ["selinger"], ["Separate declarative intent from access-path and join-order choice.", "Make statistics, costs, interesting orders and search assumptions explicit."]),
    ("graefe", "Goetz Graefe", ["volcano-optimizer"], ["Factor logical algebra, physical algebra, transformations, properties and cost.", "Extensibility still requires explicit equivalence and search contracts."]),
    ("gray", "Jim Gray", ["gray-cube", "isolation-critique"], ["Model multidimensional aggregation and transaction phenomena precisely.", "Keep analytical algebra separate from physical execution and isolation claims."]),
    ("chaudhuri", "Surajit Chaudhuri", ["gray-cube", "warehouse-olap"], ["Treat warehouses as composed acquisition, metadata, OLAP and query-management concerns.", "A cube or optimizer is only one layer of decision support."]),
    ("dayal", "Umeshwar Dayal", ["warehouse-olap"], ["Preserve the boundary between back-end preparation, multidimensional semantics and front-end consumption.", "Workload differences should shape products without collapsing owners."]),
    ("shoshani", "Arie Shoshani", ["summarizability"], ["Require normalized statistical context before aggregation.", "Reject roll-up when grain, hierarchy or measure conditions fail."]),
    ("bernstein", "Philip A. Bernstein", ["isolation-critique"], ["Define isolation by histories and anomalies, not labels alone.", "Bind every result to the provider's actual snapshot/transaction contract."]),
    ("boncz", "Peter Boncz", ["x100", "morsel"], ["Treat vectorization, cache locality and scheduling as composable execution decisions.", "Performance architecture must not leak into logical semantics."]),
    ("neumann", "Thomas Neumann", ["morsel"], ["Expose elastic task scheduling and NUMA locality explicitly.", "Parallelism is a runtime policy, not a semantic default."]),
    ("leis", "Viktor Leis", ["morsel"], ["Model fine-grained work units and runtime resource adaptation.", "Validate execution choices under actual hardware and workload evidence."]),
    ("raasveldt", "Mark Raasveldt", ["duckdb"], ["Design analytical engines as embeddable components with explicit ownership and data interchange.", "In-process deployment is a packaging/runtime choice, not query meaning."]),
    ("muhleisen", "Hannes Mühleisen", ["duckdb"], ["Reduce data movement while retaining explicit type and ownership boundaries.", "Interoperability requires contracts beyond convenient APIs."]),
    ("armbrust", "Michael Armbrust", ["lakehouse-paper"], ["Treat lakehouse as an open-format architecture pattern supporting multiple workloads.", "Evidence for one implementation does not create one universal product boundary."]),
    ("ghodsi", "Ali Ghodsi", ["lakehouse-paper"], ["Expose openness, direct access and workload composition as testable requirements.", "Packaging claims require independent qualification and exit evidence."]),
    ("xin", "Reynold Xin", ["lakehouse-paper"], ["Co-design table state and execution performance through explicit public seams.", "Do not collapse table protocol with engine or managed experience."]),
    ("zaharia", "Matei Zaharia", ["lakehouse-paper"], ["Make the storage format part of the public interoperability surface.", "Multiple workload support is a composition problem, not an AI default."]),
    ("velox-team", "Velox research team", ["velox"], ["Extract reusable vector, expression, memory and operator kernels from engines.", "A reusable execution engine remains a provider behind semantic contracts."]),
    ("calcite-community", "Apache Calcite community", ["calcite-algebra", "calcite-adapters"], ["Represent relational plans and rewrites independently from storage adapters.", "Every adapter pushdown needs residual and equivalence discipline."]),
    ("trino-community", "Trino community", ["trino-connectors", "trino-pushdown", "trino-dynamic"], ["Negotiate connector capabilities per invocation and retain unapplied residuals.", "Runtime filters and pushdown must be observable physical optimizations."]),
]


def experts() -> list[dict[str, Any]]:
    return [{"expert_id": f"expert.query.{eid}", "name": name,
             "source_refs": [f"source.query.{ref}" for ref in refs],
             "lessons_for_composable_platform": lessons,
             "authority_limit": "Expert work constrains candidate semantics; the expert is not the SAN owner or implementation qualification authority.",
             "status": "RESEARCHED_PROFILE"}
            for eid, name, refs, lessons in EXPERT_ROWS]


INNOVATION_ROWS = [
    ("lakehouse-pattern", 2021, "Lakehouse was articulated as an open direct-access architecture pattern spanning warehouse and advanced analytical workloads.", ["lakehouse-paper"]),
    ("substrait-ir", 2022, "Substrait advanced a cross-language typed relational-plan interchange with explicit extensions and incomplete/pre-1.0 boundaries.", ["substrait"]),
    ("velox-composable-engine", 2022, "Velox demonstrated a reusable vectorized execution engine shared across distinct analytical systems.", ["velox"]),
    ("adbc-1", 2023, "ADBC introduced a standardized Arrow-native client API distinct from both SQL semantics and Flight SQL transport.", ["adbc"]),
    ("flight-sql-session", 2023, "Flight SQL expanded portable Arrow result transport and explicit session/metadata commands.", ["arrow-flight-sql"]),
    ("delta-deletion-vectors", 2023, "Delta protocol features made deletion vectors an editioned table-protocol capability rather than an engine-local assumption.", ["delta-protocol"]),
    ("iceberg-rest", 2024, "Iceberg REST catalog work made the engine/catalog seam a published protocol surface.", ["iceberg-rest"]),
    ("trino-dynamic-filtering", 2024, "Connector-aware dynamic filtering made runtime-derived scan pruning and its finite thresholds explicit.", ["trino-dynamic"]),
    ("hudi-table-services", 2024, "Hudi's timeline and file-slice specifications kept merge-on-read and copy-on-write lifecycle mechanics explicit.", ["hudi-spec"]),
    ("substrait-physical-relations", 2025, "Substrait physical relations exposed join, exchange, aggregate and window property contracts while retaining consumer-defined logical/physical classification.", ["substrait-physical"]),
    ("arrow-format-1-5", 2025, "Arrow format evolution added editioned carrier capabilities while preserving that physical layouts do not own value semantics.", ["arrow-columnar"]),
    ("sql-corrigendum", 2026, "The SQL/Foundation technical corrigendum reinforced that language semantics are editioned and provider adoption must be independently bound.", ["sql-corrigendum-2026"]),
]


def innovations() -> list[dict[str, Any]]:
    return [{"innovation_id": f"innovation.query.{iid}", "year": year, "summary": summary,
             "source_refs": [f"source.query.{ref}" for ref in refs],
             "ai_or_llm_dependency": False, "status": "EVIDENCE_BACKED_BOUNDED_INNOVATION"}
            for iid, year, summary, refs in INNOVATION_ROWS]


AXIS_QUESTIONS = {
    "semantic_object": "Which query, relation, plan, table/view, snapshot, batch, result, receipt, materialization and environment objects exist without collapsing identities?",
    "semantic_role": "Which object is intent, binding, evidence, capability, estimate, plan, carrier, effect proposal or managed composition?",
    "identity_and_equality": "What identifies queries, plans, relations, snapshots, cache entries, materializations and results; which equivalence relation applies?",
    "grain_and_cardinality": "What row/fact/cell/batch/partition/result grain and zero/one/many cardinalities are guaranteed?",
    "state_and_change": "Which bind, optimize, admit, execute, stream, cancel, fail, retry, refresh, invalidate, drift and retire transitions are legal?",
    "time": "Which session, statement, transaction, source-snapshot, validity, recording, refresh, cache, deadline and replay times apply?",
    "order_and_topology": "Which relation/plan DAG, hierarchy, partition/distribution and total/partial order properties are required or destroyed?",
    "partiality_and_uncertainty": "How do null/unknown, partial pushdown, stale statistics, approximate results, incomplete streams and unknown completion propagate?",
    "authority_and_trust": "Who may define language/function editions, catalog bindings, table snapshots, policies, resource offers, result acceptance and corrections?",
    "effect_boundary": "How are pure parsing/planning/evaluation separated from reads, writes, materialization, export, publication and business effects?",
    "representation": "Which SQL, Substrait, Arrow, Parquet, table-protocol, plan, batch, result and receipt representations are used at what edition/loss?",
    "composition_algebra": "How do bindings, rewrites, properties, residuals, source cuts, kernels, resources and result contracts compose and refuse?",
    "compatibility_and_evolution": "Which language, type, function, plan, connector, table, carrier, snapshot and provider changes preserve meaning or require replay?",
    "resources_and_failure": "Which planning, scan, memory, spill, exchange, CPU, network, quota, deadline and result budgets apply, with what failures?",
    "evidence_and_conformance": "Which equivalence, SQL logic, isolation-history, residual, kernel, benchmark, replay and independent-provider evidence supports each claim?",
    "privacy_security_safety": "How are query text/parameters/results, row-level authority, side channels, spills, caches, exports and unsafe analytical claims controlled?",
}


VACANCIES = [
    ("library.qck.multidimensional-olap-semantics", "Own cube, dimension, level, hierarchy, grouping, roll-up/drill-down and cell semantics independently of business measure ownership."),
    ("library.qck.summarizability-contracts", "Own explicit grain/hierarchy/measure conditions and refusals for valid analytical roll-up."),
    ("library.qck.session-context-semantics", "Own editioned catalog/schema/role/timezone/collation/parameter context and default prohibition."),
    ("library.qck.transaction-snapshot-binding", "Own query-to-statement/transaction/table/source-cut binding without claiming storage transaction authority."),
    ("library.qck.result-determinism-contract", "Own complete order/tie/volatility/parallel-reduction conditions for reproducible results."),
    ("library.qck.materialized-view-equivalence", "Own query/materialization identity, freshness and rewrite-equivalence evidence."),
    ("library.qck.federation-residual-algebra", "Own translation loss, applied fragments, residual obligations and cross-source cut composition."),
    ("library.qck.query-evidence-contract", "Own query intent/binding/plan/source-cut/result receipt structure while importing provenance authority."),
    ("library.qck.workload-benchmark-contract", "Own workload/scale/run/environment/cost/audit identity and bounded fitness claims."),
    ("library.qck.carrier-interchange-acl", "Own loss-declared mappings among logical values/plans and Substrait, Arrow, Parquet or provider carriers."),
]


def binding_modules(ref: str) -> list[str]:
    mids = {"query-intent"}
    suffix = ref.rsplit(".", 1)[-1].replace("_", "-")
    rules = [
        (("query-syntax",), ["query-intent"]), (("query-binding",), ["session-context", "name-binding"]),
        (("query-types", "logical-types"), ["type-value", "null-three-valued"]),
        (("relational-semantics",), ["relational-operators", "bag-multiplicity"]),
        (("logical-plan",), ["logical-plan"]), (("equivalence", "rewrite"), ["plan-equivalence", "rewrite-contract"]),
        (("statistics", "cardinality"), ["statistics-properties", "cardinality-estimate"]),
        (("cost-plan-search",), ["cost-search"]), (("physical-lowering", "target-backends"), ["physical-plan", "physical-properties"]),
        (("function-contracts",), ["function-semantics"]), (("expression-kernels", "numerical-kernels", "numerical-semantics"), ["function-semantics", "vector-kernels"]),
        (("relational-kernels", "kernel-conformance"), ["relational-operators", "vector-kernels"]),
        (("codec-kernels", "value-encoding"), ["codec-encoding", "columnar-carrier"]),
        (("adaptive-execution",), ["adaptive-execution"]), (("federation",), ["connector-capability", "pushdown-residual", "federated-data-cut"]),
        (("exchange-runtime",), ["exchange-runtime"]), (("execution-scheduler",), ["scheduling-admission"]),
        (("memory-runtime", "spill-runtime"), ["memory-spill"]), (("udf-extension-host",), ["function-semantics", "physical-plan"]),
        (("query-receipts", "runtime-receipt-core"), ["query-receipt"]),
        (("result-contracts",), ["result-contract"]), (("result-stream",), ["result-stream"]),
        (("client-cache", "cache-fill"), ["cache-identity"]),
        (("export",), ["export-materialization", "result-contract"]),
        (("materialization-publisher",), ["export-materialization", "materialized-view"]),
        (("materialization",), ["materialized-view"]), (("virtual-relation",), ["virtual-relation"]),
        (("catalog-contract",), ["catalog-capability"]), (("table-identity", "snapshot-graph", "schema-evolution", "partition-algebra", "table-format-acl", "scan-planner"), ["scan-snapshot"]),
        (("columnar-layout", "file-statistics"), ["columnar-carrier", "statistics-properties"]),
        (("logical-equivalence-oracle",), ["plan-equivalence"]), (("data-cut-algebra",), ["federated-data-cut"]),
        (("admission", "quota-ledger", "budget-precharge", "reservation-ledger", "scheduler-policy-spi", "resource-topology", "autoscaling-control", "usage-accounting", "deadline-cancellation"), ["scheduling-admission"]),
        (("environment-lifecycle",), ["lakehouse-pattern", "warehouse-experience"]),
    ]
    for needles, add in rules:
        if any(needle in suffix for needle in needles):
            mids.update(add)
    return sorted(f"module.query.{mid}" for mid in mids)


def boundary_findings(consumers: dict[str, set[str]]) -> list[dict[str, Any]]:
    direct = sorted(declared_product_libraries())
    rows = [
        {"finding_id": "finding.query.query-service-owner.v1", "library_refs": sorted(ref for ref in direct if ref.startswith("library.qck.")), "current_product_refs": ["product.query_execution_service"], "candidate_disposition": "QUERY_SERVICE_OWNS_BOUND_QUERY_PLAN_EXECUTION_AND_RESULT_NOT_TABLE_OR_BUSINESS_MEANING", "reason": "Relational/query semantics, planning and result contracts cohere in the query service while table/catalog/business semantics cross explicit ACLs.", "owner_decision": "UNRATIFIED"},
        {"finding_id": "finding.query.warehouse-experience.v1", "library_refs": sorted(ref for ref in direct if "runtime-resource" in ref or "export" in ref or "materialization_publisher" in ref), "current_product_refs": ["product.managed_warehouse_experience"], "candidate_disposition": "WAREHOUSE_EXPERIENCE_COMPOSES_WORKLOAD_RESOURCE_EXPORT_AND_LIFECYCLE_CONTRACTS", "reason": "A managed experience packages qualified services but does not absorb query, table, catalog, storage or semantic-metric ownership.", "owner_decision": "UNRATIFIED"},
        {"finding_id": "finding.query.lakehouse-pattern.v1", "library_refs": ["library.product_composition.environment_lifecycle"], "current_product_refs": ["product.managed_lakehouse_experience"], "candidate_disposition": "LAKEHOUSE_REMAINS_ARCHITECTURE_PATTERN_AND_SUITE_NOT_MONOLITHIC_SEMANTIC_PRODUCT", "reason": "The managed experience owns environment declaration/readiness/lifecycle; table format, catalog, query, ingestion, maintenance, sharing, quality, lineage, policy and business semantics remain independent products/contexts.", "owner_decision": "UNRATIFIED"},
        {"finding_id": "finding.query.virtual-access.v1", "library_refs": ["library.persistence.materialization", "library.persistence.virtual_relation_identity", "library.persistence.virtual_relation_lifecycle", "library.pipeline.materialization_publisher"], "current_product_refs": ["product.virtual_data_access"], "candidate_disposition": "VIRTUAL_ACCESS_OWNS_DECLARED_RELATION_LIFECYCLE_NOT_QUERY_OR_SOURCE_AUTHORITY", "reason": "Virtual/materialized relation lifecycle composes query plans and source bindings but does not own their semantics or authority.", "owner_decision": "UNRATIFIED"},
        {"finding_id": "finding.query.table-format-acl.v1", "library_refs": sorted(ref for ref in LIBRARIES if ref.startswith("library.persistence.") and any(x in ref for x in ["table_", "snapshot", "schema_", "partition", "scan_", "catalog"])), "current_product_refs": sorted({p for ref in LIBRARIES for p in consumers[ref]}), "candidate_disposition": "QUERY_IMPORTS_TABLE_AND_CATALOG_READ_CONTRACTS_THROUGH_ACL", "reason": "Query binds scans to exact table/catalog editions but table state and catalog authority remain separate contexts.", "owner_decision": "UNRATIFIED"},
        {"finding_id": "finding.query.carrier-seam.v1", "library_refs": sorted(ref for ref in LIBRARIES if any(x in ref for x in ["columnar", "codec", "value_encoding"])), "current_product_refs": [], "candidate_disposition": "CARRIER_AND_CODEC_LIBRARIES_DO_NOT_OWN_RELATIONAL_OR_BUSINESS_SEMANTICS", "reason": "Arrow/Parquet-like carriers and codecs require loss-declared ACLs and kernel conformance.", "owner_decision": "UNRATIFIED"},
        {"finding_id": "finding.query.olap-metric-seam.v1", "library_refs": ["library.qck.relational-semantics", "library.qck.function-contracts"], "current_product_refs": ["product.query_execution_service"], "candidate_disposition": "OLAP_ALGEBRA_SEPARATE_FROM_GOVERNED_MEASURE_FORMULA_OWNERSHIP", "reason": "The engine can evaluate aggregations/cubes only after semantic-metric contexts supply measure, dimension, grain and hierarchy meaning.", "owner_decision": "UNRATIFIED"},
        {"finding_id": "finding.query.runtime-seam.v1", "library_refs": sorted(ref for ref in LIBRARIES if ref.startswith("library.runtime-resource.")), "current_product_refs": sorted({p for ref in LIBRARIES for p in consumers[ref]}), "candidate_disposition": "QUERY_REQUESTS_RESOURCE_OFFERS_BUT_DOES_NOT_OWN_GLOBAL_RESOURCE_POLICY", "reason": "Admission, quota and scheduling are imported runtime services; a query plan supplies requirements and receives bounded offers/receipts.", "owner_decision": "UNRATIFIED"},
    ]
    rows.extend({"finding_id": f"finding.query.vacancy.{slug(ref)}.v1", "library_refs": [], "proposed_library_ref": ref, "current_product_refs": [], "candidate_disposition": "NEW_LIBRARY_BOUNDARY_CANDIDATE_UNRATIFIED", "reason": reason, "owner_decision": "UNRATIFIED"} for ref, reason in VACANCIES)
    return rows


def build() -> dict[str, Any]:
    ss, ms, ls, method_rows, expert_rows, innovation_rows = sources(), modules(), laws(), methods(), experts(), innovations()
    contributions = {row["library_id"]: row for row in load_jsonl(REGISTRY / "library-contributions.jsonl")}
    assert set(LIBRARIES) <= contributions.keys()
    coord = {row["library_ref"]: row for row in load_jsonl(SEM / "library_coordinate_binding_projection/library-coordinate-binding-dockets.jsonl")}
    exact = {row["library_ref"]: row for row in load_jsonl(SEM / "p5_exact_contract_adjudication/exact-contract-dockets.jsonl")}
    consumers = {ref: set() for ref in LIBRARIES}
    subjects = {ref: set() for ref in LIBRARIES}
    for row in product_rows():
        for edge in row["concrete_bindings"]:
            ref = edge["concrete_library_ref"]
            if ref in consumers:
                consumers[ref].add(row["product_ref"])
                subjects[ref].add(row["subject_ref"])
    targeted = {(row["axis"], row["library_ref"]): row for row in load_jsonl(SEM / "targeted_evidence_cluster_adjudication/member-adjudication-occurrences.jsonl")}
    module_by_id = {row["module_id"]: row for row in ms}
    bindings, axes = [], []
    direct = declared_product_libraries()
    for ref in LIBRARIES:
        module_refs = binding_modules(ref)
        evidence_refs = sorted({source for module_ref in module_refs for source in module_by_id[module_ref]["source_refs"]})
        exact_row, coord_row = exact.get(ref), coord.get(ref)
        routed = bool(exact_row and coord_row)
        bindings.append({
            "record_kind": "query_olap_warehouse_library_semantic_binding_candidate",
            "binding_id": f"binding.query-semantic-slice.{slug(ref)}.v1", "library_ref": ref,
            "library_name": contributions[ref]["name"], "semantic_module_refs": module_refs,
            "evidence_refs": evidence_refs,
            "exact_contract_docket_ref": exact_row["docket_id"] if exact_row else None,
            "coordinate_binding_docket_ref": coord_row["binding_docket_id"] if coord_row else None,
            "downstream_contract_route": "ROUTED" if routed else "MISSING_P5_AND_COORDINATE_DOCKET_TYPED_VACANCY",
            "downstream_subject_refs": sorted(subjects[ref]), "downstream_product_refs": sorted(consumers[ref]),
            "boundary_disposition_candidate": "RETAIN_DECLARED_PRODUCT_DEPENDENCY_WITH_NARROW_OWNER" if ref in direct else "RETAIN_FORMALISM_OR_ACL_NEIGHBOR_WITH_EXPLICIT_OWNER_SEAM",
            "compiler_binding": "REFUSED",
            "refusal_reasons": ([] if routed else ["DOWNSTREAM_CONTRACT_ROUTE_MISSING"]) + ["OWNER_RATIFICATION_MISSING", "MEMBER_AXIS_APPLICABILITY_UNRATIFIED", "EXACT_CONTRACT_UNSELECTED", "IMPLEMENTATIONS_UNQUALIFIED"],
            "completion_claim": False,
        })
        for axis in AXES:
            targeted_row = targeted.get((axis, ref))
            axes.append({
                "record_kind": "query_olap_warehouse_library_axis_decision_candidate",
                "decision_candidate_id": f"decision-candidate.query-axis.{slug(ref)}.{axis.replace('_', '-')}.v1",
                "library_ref": ref, "axis": axis, "semantic_module_refs": module_refs,
                "coordinate_question": AXIS_QUESTIONS[axis], "applicability_candidate": "REQUIRED_EXPLICIT_PROFILE",
                "evidence_refs": evidence_refs,
                "targeted_member_adjudication_occurrence_ref": targeted_row["occurrence_id"] if targeted_row else None,
                "coordinate_answers": [], "member_applicability": "PROPOSED_OWNER_REVIEW_REQUIRED",
                "owner_decision": "UNRATIFIED", "status": "EVIDENCE_BACKED_DECISION_QUESTION_NOT_ANSWER",
                "canonical_gaps_closed": 0, "completion_claim": False,
            })
    findings = boundary_findings(consumers)
    context = {
        "record_kind": "bounded_context_candidate", "context_id": "context.query-olap-warehouse-semantic-slice.v1", "as_of": AS_OF,
        "vision": "How can a bound relational or multidimensional query be planned and executed over exact source cuts to produce a typed, ordered and evidenced result without collapsing logical meaning into physical strategy, table state, catalog authority, managed warehouse/lakehouse packaging or business decision authority?",
        "inside": ["query/session/name/type/value and relational semantics", "set/bag/null/equality/order/function semantics", "OLAP cube/grain/hierarchy/aggregation/summarizability semantics", "logical plans, equivalence, rewrites, statistics, cardinality and cost", "physical properties, lowering, kernels, exchange, adaptive execution and result contracts", "connector capability, pushdown residuals, federated data cuts, virtual/materialized relations and cache identity", "query receipts and bounded benchmark evidence"],
        "outside": ["table-format mutation and maintenance ownership", "catalog governance and authorization authority", "ingestion/delivery and source replication", "semantic metric/formula and business dimension ownership", "quality, lineage, privacy-policy and decision/effect authority", "storage/object/compute resource ownership", "managed environment lifecycle except as an imported composition seam", "LLM or agent authority"],
        "neighbors": [
            {"context_ref": "context.analytical-table-state", "relationship": "anti_corruption_layer"},
            {"context_ref": "context.catalog-service", "relationship": "customer_supplier"},
            {"context_ref": "context.semantic-metrics", "relationship": "customer_supplier"},
            {"context_ref": "context.runtime-resource-control", "relationship": "customer_supplier"},
            {"context_ref": "context.lineage-provenance", "relationship": "customer_supplier"},
            {"context_ref": "context.virtual-data-access", "relationship": "published_language"},
            {"context_ref": "context.managed-warehouse-experience", "relationship": "published_language"},
            {"context_ref": "context.managed-lakehouse-experience", "relationship": "anti_corruption_layer"},
        ],
        "published_language": ["QueryOccurrence", "SessionContextEdition", "BoundQuery", "LogicalPlan", "PhysicalPlanCandidate", "RewriteEvidence", "SourceCut", "ConnectorCapabilityOffer", "PushdownFragment", "ResidualPlan", "SnapshotBinding", "ResultContract", "ResultStreamState", "QueryReceipt", "MaterializationIdentity", "BenchmarkEvidence"],
        "ratification": "WITHHELD", "completion_claim": False,
    }
    summary = {
        "program_id": "program.query-olap-warehouse-semantic-slice.v1", "as_of": AS_OF,
        "primary_or_official_sources": len(ss), "semantic_modules": len(ms), "non_collapse_laws": len(ls),
        "method_types": len(method_rows), "expert_learning_profiles": len(expert_rows),
        "recent_non_llm_innovations": len(innovation_rows), "bound_libraries": len(bindings),
        "declared_product_libraries": len(direct), "formalism_and_acl_neighbor_libraries": len(NEIGHBORS),
        "candidate_new_library_vacancies": len(VACANCIES),
        "libraries_without_declared_product_consumer": sum(not consumers[ref] for ref in LIBRARIES),
        "missing_downstream_contract_routes": sum(row["downstream_contract_route"].startswith("MISSING") for row in bindings),
        "library_axis_decision_candidates": len(axes), "product_capability_boundary_findings": len(findings),
        "owner_decisions": 0, "exact_contracts_selected": 0, "qualified_implementations": 0,
        "canonical_gaps_closed": 0, "completion_claim": False,
    }
    return {"context": context, "sources": ss, "modules": ms, "laws": ls, "methods": method_rows,
            "experts": expert_rows, "innovations": innovation_rows, "libraries": bindings,
            "axes": axes, "findings": findings, "summary": summary}


def outputs() -> dict[str, str]:
    built = build()
    files = {
        "bounded-context.json": json.dumps(built["context"], ensure_ascii=False, sort_keys=True, indent=2) + "\n",
        "primary-sources.jsonl": "".join(canonical(row) + "\n" for row in built["sources"]),
        "semantic-modules.jsonl": "".join(canonical(row) + "\n" for row in built["modules"]),
        "non-collapse-laws.jsonl": "".join(canonical(row) + "\n" for row in built["laws"]),
        "query-method-taxonomy.jsonl": "".join(canonical(row) + "\n" for row in built["methods"]),
        "expert-learning-profiles.jsonl": "".join(canonical(row) + "\n" for row in built["experts"]),
        "innovation-records.jsonl": "".join(canonical(row) + "\n" for row in built["innovations"]),
        "library-semantic-bindings.jsonl": "".join(canonical(row) + "\n" for row in built["libraries"]),
        "library-axis-decision-candidates.jsonl": "".join(canonical(row) + "\n" for row in built["axes"]),
        "product-capability-boundary-findings.jsonl": "".join(canonical(row) + "\n" for row in built["findings"]),
        "summary.json": json.dumps(built["summary"], ensure_ascii=False, sort_keys=True, indent=2) + "\n",
    }
    claims = {name: {"bytes": len(value.encode()), "sha256": hashlib.sha256(value.encode()).hexdigest()} for name, value in files.items()}
    files["manifest.json"] = json.dumps({"manifest_id": "manifest.query-olap-warehouse-semantic-slice.v1", "as_of": AS_OF, "files": claims, "completion_claim": False}, sort_keys=True, indent=2) + "\n"
    return files


def main() -> int:
    for name, value in outputs().items():
        (HERE / name).write_text(value)
    s = build()["summary"]
    print(f"BUILD PASS query/OLAP/warehouse slice: {s['semantic_modules']} modules, {s['method_types']} methods, {s['bound_libraries']} libraries and {s['library_axis_decision_candidates']} unresolved axis decisions")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
