#!/usr/bin/env python3
"""Build the provider-neutral query/compute/kernel research corpus."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SCHEMA = ROOT / "schema"
EDITION = 1
ACCESSED = "2026-08-25"


def dump_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def dump_jsonl(path: Path, records: list[dict]) -> None:
    path.write_text("".join(json.dumps(record, sort_keys=True) + "\n" for record in records))


METAMODEL = {
    "metamodel_id": "san.query-compute-kernel-universe",
    "edition": EDITION,
    "status": "active_research_contract",
    "completion_claim": False,
    "scope": "Provider-neutral query and compute semantics from language binding to execution receipts; no LLM, generative or agentic semantics.",
    "identity_layers": [
        {"kind": "semantic_operation", "owns": ["meaning", "types", "null_missing_nan", "ordering", "time", "exactness"], "cannot_own": ["algorithm", "provider", "target"]},
        {"kind": "algorithm", "owns": ["method_family", "complexity", "preconditions"], "cannot_own": ["query_language_meaning", "provider_identity"]},
        {"kind": "kernel", "owns": ["executable_contract", "layout", "target_requirements", "resource_behavior"], "cannot_own": ["business_or_query_semantics"]},
        {"kind": "provider", "owns": ["offers", "limits", "evidence_scope", "versions"], "cannot_own": ["canonical_semantics"]},
        {"kind": "target", "owns": ["isa", "device", "runtime", "memory_and_resource_constraints"], "cannot_own": ["selection_policy"]},
    ],
    "planning_stages": [
        "parse", "bind_names", "infer_types", "resolve_functions", "normalize_semantics",
        "build_logical_plan", "rewrite_with_equivalence_proof", "derive_statistics",
        "estimate_cardinality_and_cost", "enumerate_physical_alternatives", "bind_provider_and_target",
        "lower_to_kernels", "insert_resource_and_assurance_controls", "execute", "emit_receipts",
    ],
    "guarantee_lattice": {
        "exactness": ["exact", "bounded_approximation", "empirical_approximation", "unspecified"],
        "reproducibility": ["cross_target_bitwise", "qualified_target_bitwise", "run_deterministic", "tolerance_reproducible", "nondeterministic_declared"],
        "result_completeness": ["complete", "watermark_complete", "bounded_partial", "best_effort_partial", "unknown"],
    },
    "constitutional_laws": [
        "logical meaning is fixed before physical selection",
        "rewrite requires proof, a scoped conformance oracle, or an explicit unproven gap",
        "provider names never determine semantic dispatch",
        "approximation and information loss require declared authorization and receipts",
        "null, missing, NaN, collation, timezone and ordering semantics are never inferred from a target",
        "resource use is finite or compilation refuses",
        "cancellation and partial effects are explicit contracts",
        "adaptive replanning preserves the declared semantics and guarantee posture",
        "UDF volatility, effects, determinism, parallel safety and sandbox are mandatory",
        "compression is an encoding, kernel and physical-policy concern, not a vendor feature flag",
        "unknown provider or target behavior fails closed",
    ],
    "fallback_classes": ["equivalent_alternative", "declared_typed_degradation", "human_authorized_change", "refuse"],
    "forbidden_core_dependencies": ["llm", "large_language_model", "prompt", "rag", "agent_memory", "generative_model"],
}


SOURCE_ROWS = [
    ("sql.standard", "ISO/IEC 9075 database languages SQL", "ISO/IEC", "standard", "https://www.iso.org/standard/76583.html", 2023, ["sql_semantics", "language"]),
    ("substrait.home", "Substrait cross-language serialization for relational algebra", "Substrait", "official_spec", "https://substrait.io/", 2026, ["logical_ir", "interoperability"]),
    ("substrait.spec", "Substrait specification", "Substrait", "official_spec", "https://substrait.io/spec/specification/", 2026, ["types", "functions", "relations", "extensions"]),
    ("substrait.algebra", "Substrait relational algebra protocol", "Substrait", "official_implementation", "https://github.com/substrait-io/substrait/blob/main/proto/substrait/algebra.proto", 2026, ["logical_ir", "exchange", "window"]),
    ("calcite.algebra", "Apache Calcite algebra", "Apache Software Foundation", "official_docs", "https://calcite.apache.org/docs/algebra.html", 2026, ["logical_plan", "rewrite", "cost"]),
    ("calcite.adapters", "Apache Calcite adapters", "Apache Software Foundation", "official_docs", "https://calcite.apache.org/docs/adapter", 2026, ["federation", "pushdown", "calling_convention"]),
    ("postgres.planner", "PostgreSQL planner/optimizer", "PostgreSQL Global Development Group", "official_docs", "https://www.postgresql.org/docs/current/planner-optimizer.html", 2026, ["planning", "join_search", "cost"]),
    ("postgres.explain", "PostgreSQL EXPLAIN", "PostgreSQL Global Development Group", "official_docs", "https://www.postgresql.org/docs/current/using-explain.html", 2026, ["diagnostics", "receipts"]),
    ("postgres.parallel", "PostgreSQL parallel query", "PostgreSQL Global Development Group", "official_docs", "https://www.postgresql.org/docs/current/how-parallel-query-works.html", 2026, ["parallel_execution", "gather"]),
    ("postgres.function", "PostgreSQL CREATE FUNCTION", "PostgreSQL Global Development Group", "official_docs", "https://www.postgresql.org/docs/current/sql-createfunction.html", 2026, ["udf", "parallel_safety"]),
    ("postgres.volatility", "PostgreSQL function volatility categories", "PostgreSQL Global Development Group", "official_docs", "https://www.postgresql.org/docs/current/xfunc-volatility.html", 2026, ["udf", "determinism", "effects"]),
    ("arrow.format", "Apache Arrow format specifications", "Apache Software Foundation", "official_spec", "https://arrow.apache.org/docs/format/index.html", 2026, ["columnar_layout", "ipc", "types"]),
    ("arrow.compute", "Apache Arrow compute functions", "Apache Software Foundation", "official_docs", "https://arrow.apache.org/docs/cpp/compute.html", 2026, ["scalar_kernel", "vector_kernel", "aggregate_kernel"]),
    ("arrow.acero", "Apache Arrow Acero streaming execution engine", "Apache Software Foundation", "official_docs", "https://arrow.apache.org/docs/cpp/acero.html", 2026, ["streaming_execution", "operator_graph"]),
    ("arrow.c_data", "Apache Arrow C Data Interface", "Apache Software Foundation", "official_spec", "https://arrow.apache.org/docs/format/CDataInterface.html", 2026, ["abi", "zero_copy", "columnar_layout"]),
    ("arrow.c_device", "Apache Arrow C Device Data Interface", "Apache Software Foundation", "official_spec", "https://arrow.apache.org/docs/format/CDeviceDataInterface.html", 2026, ["device_abi", "gpu", "zero_copy"]),
    ("arrow.flight_sql", "Apache Arrow Flight SQL protocol", "Apache Software Foundation", "official_spec", "https://arrow.apache.org/docs/format/FlightSql.html", 2026, ["query_protocol", "distributed_results"]),
    ("arrow.adbc", "Arrow Database Connectivity specification", "Apache Software Foundation", "official_spec", "https://arrow.apache.org/adbc/current/format/specification.html", 2026, ["database_abi", "sql", "substrait"]),
    ("datafusion.home", "Apache DataFusion", "Apache Software Foundation", "official_docs", "https://datafusion.apache.org/", 2026, ["query_engine", "rust", "vectorized"]),
    ("datafusion.optimizer", "Apache DataFusion query optimizer", "Apache Software Foundation", "official_docs", "https://datafusion.apache.org/library-user-guide/query-optimizer.html", 2026, ["logical_rewrite", "physical_rewrite"]),
    ("datafusion.features", "Apache DataFusion feature matrix", "Apache Software Foundation", "official_docs", "https://datafusion.apache.org/user-guide/features.html", 2026, ["operators", "spill", "udf"]),
    ("datafusion.config", "Apache DataFusion configuration", "Apache Software Foundation", "official_docs", "https://datafusion.apache.org/user-guide/configs.html", 2026, ["memory", "spill", "planning"]),
    ("datafusion.paper", "Apache Arrow DataFusion: a fast embeddable modular analytic query engine", "ACM SIGMOD", "paper", "https://github.com/apache/arrow-datafusion/files/14789704/DataFusion_Query_Engine___SIGMOD_2024-FINAL.pdf", 2024, ["modular_engine", "physical_plan", "resource_management"]),
    ("velox.paper", "Velox: Meta's unified execution engine", "PVLDB", "paper", "https://www.vldb.org/pvldb/vol15/p3372-pedreira.pdf", 2022, ["modular_execution", "vectorized", "resource_management"]),
    ("velox.functions", "Velox scalar and vector functions", "Velox Project", "official_docs", "https://facebookincubator.github.io/velox/develop/scalar-functions.html", 2026, ["udf", "vector_kernel", "function_resolution"]),
    ("velox.memory", "Velox memory management", "Velox Project", "official_docs", "https://facebookincubator.github.io/velox/develop/memory.html", 2026, ["memory", "arbitration", "pools"]),
    ("velox.spill", "Velox spilling", "Velox Project", "official_docs", "https://facebookincubator.github.io/velox/develop/spilling.html", 2026, ["spill", "external_memory"]),
    ("velox.function_authoring", "Simple yet efficient function authoring for vectorized engines", "PVLDB", "paper", "https://www.vldb.org/pvldb/vol17/p4187-pedreira.pdf", 2024, ["vector_function", "encodings", "function_abi"]),
    ("photon.paper", "Photon: a high-performance query engine for the lakehouse", "CIDR", "paper", "https://vldb.org/cidrdb/papers/2022/a100-behm.pdf", 2022, ["vectorized_execution", "runtime_adaptivity", "hybrid_fallback"]),
    ("photon.aqe", "Adaptive and robust query execution for lakehouses at scale", "PVLDB", "paper", "https://vldb.org/pvldb/vol17/p3947-bu.pdf", 2024, ["adaptive_execution", "join_selection", "parallelism"]),
    ("spark.aqe", "Spark SQL adaptive query execution", "Apache Software Foundation", "official_docs", "https://spark.apache.org/docs/latest/sql-performance-tuning.html#adaptive-query-execution", 2026, ["adaptive_execution", "shuffle", "skew"]),
    ("trino.pushdown", "Trino pushdown", "Trino Software Foundation", "official_docs", "https://trino.io/docs/current/optimizer/pushdown.html", 2026, ["federation", "pushdown"]),
    ("trino.dynamic_filter", "Trino dynamic filtering", "Trino Software Foundation", "official_docs", "https://trino.io/docs/current/admin/dynamic-filtering.html", 2026, ["runtime_filter", "join"]),
    ("trino.adaptive", "Trino adaptive plan optimizations", "Trino Software Foundation", "official_docs", "https://trino.io/docs/current/optimizer/adaptive-plan-optimizations.html", 2026, ["adaptive_execution", "join_reorder"]),
    ("trino.fte", "Trino fault-tolerant execution", "Trino Software Foundation", "official_docs", "https://trino.io/docs/current/admin/fault-tolerant-execution.html", 2026, ["retry", "exchange", "fault_tolerance"]),
    ("trino.resources", "Trino resource groups", "Trino Software Foundation", "official_docs", "https://trino.io/docs/current/admin/resource-groups.html", 2026, ["resource_budget", "scheduling"]),
    ("trino.spill", "Trino spill to disk", "Trino Software Foundation", "official_docs", "https://trino.io/docs/current/admin/spill.html", 2026, ["spill", "memory"]),
    ("beam.model", "Apache Beam model basics", "Apache Software Foundation", "official_docs", "https://beam.apache.org/documentation/basics/", 2026, ["window", "watermark", "trigger"]),
    ("flink.time", "Apache Flink event-time applications", "Apache Software Foundation", "official_docs", "https://flink.apache.org/what-is-flink/flink-applications/", 2026, ["event_time", "watermark", "late_data"]),
    ("differential.arrangements", "Differential Dataflow arrangements", "Differential Dataflow Project", "official_docs", "https://timelydataflow.github.io/differential-dataflow/chapter_5/chapter_5.html", 2026, ["incremental", "indexed_state"]),
    ("dbsp.paper", "DBSP: automatic incremental view maintenance for rich query languages", "PVLDB", "paper", "https://www.vldb.org/pvldb/vol16/p1601-budiu.pdf", 2023, ["incremental_view", "stream_algebra", "recursion"]),
    ("graphblas.spec", "GraphBLAS C API specification 2.1", "GraphBLAS Forum", "standard", "https://graphblas.org/docs/GraphBLAS_API_C_v2.1.0.pdf", 2023, ["graph_kernel", "sparse_linear_algebra"]),
    ("gql.standard", "ISO/IEC 39075:2024 Database languages GQL", "ISO/IEC", "standard", "https://www.iso.org/standard/76120.html", 2024, ["property_graph", "graph_query"]),
    ("opencypher.tck", "openCypher specification and technology compatibility kit", "openCypher", "official_spec", "https://opencypher.org/resources/", 2026, ["graph_query", "conformance"]),
    ("sparql.standard", "SPARQL 1.1 query language", "W3C", "standard", "https://www.w3.org/TR/sparql11-query/", 2013, ["rdf_graph", "federation"]),
    ("ogc.sfa", "OGC Simple Feature Access", "Open Geospatial Consortium", "standard", "https://www.ogc.org/standards/sfa/", 2011, ["spatial_types", "spatial_predicates"]),
    ("ogc.geosparql", "OGC GeoSPARQL 1.1", "Open Geospatial Consortium", "standard", "https://docs.ogc.org/is/22-047r1/22-047r1.html", 2024, ["spatial_graph", "spatial_functions"]),
    ("ogc.cql2", "OGC Common Query Language CQL2", "Open Geospatial Consortium", "standard", "https://docs.ogc.org/is/21-065r2/21-065r2.html", 2024, ["filter", "spatial", "temporal"]),
    ("parquet.encoding", "Apache Parquet encodings", "Apache Software Foundation", "official_spec", "https://parquet.apache.org/docs/file-format/data-pages/encodings/", 2026, ["encoding", "columnar"]),
    ("parquet.compression", "Apache Parquet compression codecs", "Apache Software Foundation", "official_spec", "https://parquet.apache.org/docs/file-format/data-pages/compression/", 2026, ["compression", "codec"]),
    ("btrblocks.paper", "BtrBlocks: efficient columnar compression for data lakes", "ACM SIGMOD", "paper", "https://www.cs.cit.tum.de/fileadmin/w00cfj/dis/papers/btrblocks.pdf", 2023, ["compression", "adaptive_encoding"]),
    ("alp.paper", "ALP: adaptive lossless floating-point compression", "ACM SIGMOD", "paper", "https://ir.cwi.nl/pub/33334/33334.pdf", 2024, ["floating_compression", "lossless"]),
    ("fastlanes.paper", "The FastLanes compression layout", "PVLDB", "paper", "https://www.vldb.org/pvldb/vol16/p2132-afroozeh.pdf", 2023, ["vectorized_decode", "compression_layout"]),
    ("fastlanes.expression", "FastLanes expression encoding and segmented page layout", "PVLDB", "paper", "https://vldb.org/pvldb/vol18/p4629-afroozeh.pdf", 2025, ["expression_encoding", "compressed_execution"]),
    ("wasm.spec", "WebAssembly specifications", "W3C WebAssembly Community Group", "standard", "https://webassembly.org/specs/", 2025, ["sandbox", "portable_target", "abi"]),
    ("cuda.guide", "CUDA programming guide", "NVIDIA", "official_docs", "https://docs.nvidia.com/cuda/cuda-programming-guide/", 2026, ["gpu", "kernel", "streams"]),
    ("hip.model", "HIP programming model", "AMD", "official_docs", "https://rocm.docs.amd.com/projects/HIP/en/latest/understand/programming_model.html", 2026, ["gpu", "kernel", "streams"]),
    ("sycl.spec", "SYCL 2020 specification", "Khronos Group", "standard", "https://registry.khronos.org/SYCL/specs/sycl-2020/html/sycl-2020.html", 2026, ["heterogeneous_compute", "target"]),
    ("openmp.spec", "OpenMP API specification 5.2", "OpenMP ARB", "standard", "https://www.openmp.org/spec-html/5.2/openmp.html", 2021, ["parallel", "simd", "offload"]),
    ("ieee754.standard", "IEEE 754-2019 floating-point arithmetic", "IEEE", "standard", "https://standards.ieee.org/ieee/754/6210/", 2019, ["floating_point", "numeric_semantics"]),
    ("onemkl.repro", "oneMKL numerical reproducibility", "Intel", "official_docs", "https://www.intel.com/content/www/us/en/docs/onemkl/developer-reference-dpcpp/2025-0/numerical-reproducibility.html", 2024, ["reproducibility", "blas"]),
    ("cuda.numeric", "CUDA C++ best practices: floating-point arithmetic", "NVIDIA", "official_docs", "https://docs.nvidia.com/cuda/cuda-c-best-practices-guide/index.html#floating-point-math-is-not-associative", 2026, ["floating_point", "parallel_reduction"]),
    ("blas.spec", "BLAS technical forum standard", "BLAS Technical Forum", "standard", "https://www.netlib.org/blas/blast-forum/blas-report.pdf", 2002, ["dense_kernel", "sparse_kernel"]),
    ("lapack.guide", "LAPACK users guide", "Netlib", "official_docs", "https://www.netlib.org/lapack/lug/", 1999, ["linear_algebra", "numerical_failure"]),
    ("fftw.docs", "FFTW documentation", "FFTW Project", "official_docs", "https://www.fftw.org/", 2026, ["fft", "cpu", "distributed"]),
    ("datasketches.theta", "Apache DataSketches Theta framework", "Apache Software Foundation", "official_docs", "https://datasketches.apache.org/docs/Theta/ThetaSketches.html", 2026, ["approximate_set", "error_bounds"]),
    ("datasketches.quantile", "Apache DataSketches quantile sketches", "Apache Software Foundation", "official_docs", "https://datasketches.apache.org/docs/QuantilesAll/QuantilesOverview.html", 2026, ["approximate_quantile", "error_bounds"]),
    ("cosette.paper", "Cosette: an automated prover for SQL", "CIDR", "paper", "https://www.cs.cmu.edu/~15811/papers/db.pdf", 2017, ["query_equivalence", "proof"]),
    ("verieql.paper", "VeriEQL: bounded equivalence verification for complex SQL queries", "ACM/OOPSLA", "paper", "https://arxiv.org/abs/2403.03193", 2024, ["query_equivalence", "counterexample"]),
    ("duckdb.sorting", "These rows are made for sorting", "DuckDB Foundation", "paper", "https://duckdb.org/library/sorting/", 2023, ["sorting", "row_column_layout"]),
    ("duckdb.optimizer", "DuckDB optimizer examples", "DuckDB Foundation", "official_docs", "https://duckdb.org/2024/11/14/optimizers", 2024, ["rewrite", "join_order"]),
    ("sqlite_he.paper", "Introducing a query acceleration path for analytics in SQLite3", "CIDR", "paper", "https://www.vldb.org/cidrdb/papers/2022/p56-prammer.pdf", 2022, ["hybrid_execution", "embedded"]),
    ("pipeline_group.paper", "Pipeline group optimization on disaggregated systems", "CIDR", "paper", "https://vldb.org/cidrdb/2023/pipeline-group-optimization-on-disaggregated-systems.html", 2023, ["disaggregated_memory", "pipeline"]),
    ("hetcache.paper", "HetCache: synergising NVMe storage and GPU acceleration", "CIDR", "paper", "https://vldb.org/cidrdb/2023/hetcache-synergising-nvme-storage-and-gpu-acceleration-for-memory-efficient-analytics.html", 2023, ["heterogeneous_cache", "gpu", "nvme"]),
    ("openivm.paper", "OpenIVM: a SQL-to-SQL compiler for incremental computations", "ACM SIGMOD", "paper", "https://arxiv.org/abs/2404.16486", 2024, ["incremental_view", "compiler"]),
    ("rulescript.paper", "An extensible and verifiable language for query rewrite rules", "Research paper", "paper", "https://arxiv.org/abs/2605.05536", 2026, ["rewrite_language", "verification"]),
]


SOURCES = [
    {
        "source_id": f"source.qck.{sid}", "edition": EDITION, "status": "reviewed",
        "title": title, "publisher": publisher, "source_kind": kind, "url": url,
        "publication_year": year, "accessed_at": ACCESSED, "supports_topics": topics,
        "authority_scope": "Normative for its own standard or implementation; comparative claims remain source-scoped.",
        "limitations": ["Does not by itself prove universal semantics or cross-provider conformance."],
    }
    for sid, title, publisher, kind, url, year, topics in SOURCE_ROWS
]


CONTEXT_ROWS = [
    ("language", "Query language and syntax", "Parsing and surface-language editions", "Physical planning and execution"),
    ("binding", "Name, scope and catalog binding", "Identifier resolution, scoping and authority", "Provider access mechanics"),
    ("typing", "Type inference and coercion", "Type derivation, casts and overload constraints", "Concrete vector layout"),
    ("function_registry", "Function and extension registry", "Canonical signatures, editions and resolution", "Function implementation code"),
    ("semantic_normalization", "Semantic normalization", "Lower surface constructs into explicit semantic forms", "Performance rewrites"),
    ("relational_algebra", "Relational and collection algebra", "Bag/set, null, ordering and relational operators", "Physical join algorithms"),
    ("stream_time_algebra", "Stream, time and change algebra", "Windows, watermarks, triggers, changelogs and temporal state", "Cluster scheduling"),
    ("graph_algebra", "Graph query algebra", "Pattern, path and graph-result semantics", "Graph storage engine"),
    ("spatial_algebra", "Spatial query algebra", "CRS-aware predicates, measures and transformations", "Geometry kernel implementation"),
    ("numerical_algebra", "Numerical and tensor algebra", "Mathematical operations, shapes, precision and error contracts", "Device kernels"),
    ("logical_plan", "Logical plan IR", "Typed provider-neutral operation hypergraph", "Physical operator implementation"),
    ("rewrite", "Rewrite and equivalence", "Semantics-preserving transformation rules and proof scope", "Cost ranking"),
    ("statistics", "Statistics and properties", "Observed/declared distributions, constraints, ordering and partition properties", "Business metrics"),
    ("cardinality", "Cardinality estimation", "Row/state cardinality distributions and uncertainty", "Plan selection policy"),
    ("cost", "Cost and resource estimation", "Multi-resource estimates, uncertainty and calibration", "Provider billing"),
    ("plan_search", "Physical plan search", "Alternative enumeration, dominance and selection", "Kernel code"),
    ("physical_lowering", "Physical lowering", "Bind logical operators to algorithms, exchanges and kernel requirements", "Deployment orchestration"),
    ("expression", "Expression evaluation", "Scalar/vector expression DAG evaluation", "Language parsing"),
    ("relational_kernels", "Relational kernels", "Join, aggregate, sort, hash and window executable contracts", "Logical result meaning"),
    ("graph_kernels", "Graph kernels", "Sparse and traversal execution primitives", "Graph analytical intent"),
    ("spatial_kernels", "Spatial kernels", "Geometry, index and raster execution primitives", "CRS semantic ownership"),
    ("numerical_kernels", "Numerical kernels", "Dense/sparse/FFT executable primitives", "Mathematical problem formulation"),
    ("codec_kernels", "Encoding and compression kernels", "Reversible/lossy encode/decode contracts", "Table format governance"),
    ("memory", "Memory and buffer runtime", "Allocation, ownership, pools, lifetimes and pressure", "Query semantics"),
    ("spill", "External-memory and spill runtime", "Spill state, encryption, cleanup and resume", "Storage product ownership"),
    ("exchange", "Exchange and shuffle runtime", "Partition, order, framing, backpressure and retry", "Network infrastructure ownership"),
    ("scheduler", "Local and distributed execution scheduling", "Tasks, pipelines, fairness and work placement", "Enterprise job orchestration"),
    ("adaptive", "Adaptive query execution", "Runtime observations and semantics-preserving replanning", "Undeclared result degradation"),
    ("federation", "Federation and pushdown", "Remote capability translation and semantic compatibility", "Source-system governance"),
    ("approximation", "Approximate execution", "Error, confidence, merge and information-loss contracts", "Unauthorized sampling"),
    ("materialization", "Caching and materialization", "Result identity, invalidation, freshness and reuse proofs", "Source of truth ownership"),
    ("extension_host", "UDF and extension host", "ABI, effects, sandbox, volatility and lifecycle", "Function business semantics"),
    ("target_binding", "Target and accelerator binding", "ISA/device/runtime capability matching", "Kernel semantic ownership"),
    ("resource_control", "Query resource control", "Finite budgets, precharge, cancellation and overload", "Organization-wide capacity planning"),
    ("numeric_reproducibility", "Numerical reproducibility", "Precision, rounding, reduction order and repeatability posture", "Scientific interpretation"),
    ("diagnostics", "Plan diagnostics and receipts", "Decision traces, counters, lineage and result guarantees", "General observability platform"),
    ("conformance", "Query and kernel conformance", "Golden, differential, property and equivalence oracles", "Provider certification authority"),
]


CONTEXTS = []
for cid, name, inside, outside in CONTEXT_ROWS:
    CONTEXTS.append({
        "context_id": f"context.qck.{cid}", "edition": EDITION, "status": "candidate",
        "name": name, "domain_vision": f"Determine and govern {inside.lower()} without coupling meaning to a provider.",
        "inside": [inside], "outside": [outside],
        "ubiquitous_terms": [],
        "invariants": ["One semantic meaning has one owner in this boundary.", "Unknown or incompatible behavior becomes a typed gap."],
        "decision_points": [], "neighbor_context_refs": [],
        "evidence_refs": ["source.qck.substrait.spec", "source.qck.datafusion.paper"],
        "gaps": ["Ownership and split/merge status require global context-map adjudication."],
    })


FAMILY_EVIDENCE = {
    "relational": ["source.qck.substrait.spec", "source.qck.calcite.algebra", "source.qck.sql.standard"],
    "stream": ["source.qck.beam.model", "source.qck.flink.time", "source.qck.dbsp.paper"],
    "graph": ["source.qck.gql.standard", "source.qck.opencypher.tck", "source.qck.graphblas.spec"],
    "spatial": ["source.qck.ogc.sfa", "source.qck.ogc.geosparql", "source.qck.ogc.cql2"],
    "numerical": ["source.qck.blas.spec", "source.qck.lapack.guide", "source.qck.fftw.docs"],
    "approximate": ["source.qck.datasketches.theta", "source.qck.datasketches.quantile"],
    "encoding": ["source.qck.parquet.encoding", "source.qck.parquet.compression"],
    "control": ["source.qck.trino.resources", "source.qck.arrow.acero"],
}


LOGICAL_ROWS = [
    # family, id, name, semantics, inputs, output, exactness, information loss
    ("relational", "scan", "Logical scan", "Read a declared snapshot or change relation under a source authority and projection contract.", ["relation_ref", "snapshot_or_change_scope"], "relation", "exact", "none"),
    ("relational", "values", "Literal relation", "Construct a finite relation from typed literal tuples.", ["typed_rows"], "relation", "exact", "none"),
    ("relational", "project", "Projection", "Evaluate named expressions and emit the declared fields in declared order.", ["relation", "expressions"], "relation", "exact", "may_drop_fields"),
    ("relational", "filter", "Selection", "Retain tuples for which the declared predicate satisfies the three-valued truth policy.", ["relation", "predicate"], "relation", "exact", "drops_nonmatching_rows"),
    ("relational", "inner_join", "Inner join", "Produce matching tuple combinations under declared equality, null and multiplicity semantics.", ["left_relation", "right_relation", "condition"], "relation", "exact", "drops_unmatched_rows"),
    ("relational", "left_outer_join", "Left outer join", "Preserve every left tuple and null-extend unmatched right fields under declared semantics.", ["left_relation", "right_relation", "condition"], "relation", "exact", "none"),
    ("relational", "right_outer_join", "Right outer join", "Preserve every right tuple and null-extend unmatched left fields under declared semantics.", ["left_relation", "right_relation", "condition"], "relation", "exact", "none"),
    ("relational", "full_outer_join", "Full outer join", "Preserve unmatched tuples from both sides and matched combinations.", ["left_relation", "right_relation", "condition"], "relation", "exact", "none"),
    ("relational", "semi_join", "Semi join", "Retain left tuples having at least one matching right tuple without multiplying by right matches.", ["left_relation", "right_relation", "condition"], "relation", "exact", "drops_nonmatching_rows"),
    ("relational", "anti_join", "Anti join", "Retain left tuples having no qualifying right match under declared null semantics.", ["left_relation", "right_relation", "condition"], "relation", "exact", "drops_matching_rows"),
    ("relational", "cross_join", "Cartesian product", "Produce every left/right tuple pair while preserving multiplicity.", ["left_relation", "right_relation"], "relation", "exact", "none"),
    ("relational", "asof_join", "As-of join", "Match by key and nearest qualifying ordered value under direction, tolerance and tie laws.", ["left_relation", "right_relation", "keys", "ordered_value"], "relation", "exact", "may_drop_or_null_extend"),
    ("relational", "aggregate", "Grouped aggregation", "Partition tuples by declared key equality and evaluate aggregate state/finalization contracts.", ["relation", "group_keys", "aggregate_functions"], "relation", "exact", "many_to_one_summary"),
    ("relational", "window", "Analytic window", "Evaluate functions over declared partitions, order and frame without collapsing input tuples.", ["relation", "partition", "order", "frame", "functions"], "relation", "exact", "none"),
    ("relational", "distinct", "Duplicate elimination", "Collapse tuples equal under declared row equality to one representative.", ["relation"], "relation", "exact", "multiplicity_loss"),
    ("relational", "sort", "Total or partial ordering", "Order tuples by declared keys, directions, collation, null placement and stability.", ["relation", "sort_keys"], "ordered_relation", "exact", "none"),
    ("relational", "top_k", "Top K", "Return the first K tuples under a declared complete tie and ordering policy.", ["relation", "sort_keys", "k"], "ordered_relation", "exact", "drops_non_top_rows"),
    ("relational", "limit", "Limit", "Return at most N tuples; without a total order membership is explicitly arbitrary.", ["relation", "n", "offset"], "relation", "exact", "drops_rows"),
    ("relational", "union_all", "Bag union", "Concatenate compatible relations while preserving all multiplicities.", ["relations"], "relation", "exact", "none"),
    ("relational", "union_distinct", "Set union", "Union compatible relations and remove duplicates under declared equality.", ["relations"], "relation", "exact", "multiplicity_loss"),
    ("relational", "intersect_all", "Bag intersection", "Emit minimum input multiplicity for each equal tuple.", ["relations"], "relation", "exact", "drops_nonintersection"),
    ("relational", "except_all", "Bag difference", "Subtract tuple multiplicities without going below zero.", ["primary_relation", "subtract_relations"], "relation", "exact", "drops_subtracted_multiplicity"),
    ("relational", "unnest", "Unnest/flatten", "Expand collection-valued fields with explicit empty, null, ordinality and correlation semantics.", ["relation", "collection_expression"], "relation", "exact", "may_drop_empty_collections"),
    ("relational", "correlate", "Correlated apply", "Evaluate a right subplan in the lexical environment of each left tuple.", ["left_relation", "right_subplan"], "relation", "exact", "depends_on_join_kind"),
    ("relational", "recursive_fixpoint", "Recursive fixpoint", "Iterate seed and recursive terms under declared union, termination and cycle semantics.", ["seed_relation", "recursive_term"], "relation", "exact", "none"),
    ("relational", "pivot", "Pivot", "Map row values into a declared output dimension with collision and missing-category laws.", ["relation", "key", "value", "categories"], "relation", "exact", "may_aggregate_or_drop"),
    ("relational", "unpivot", "Unpivot", "Map declared columns to row-valued name/value pairs with null retention law.", ["relation", "columns"], "relation", "exact", "none"),
    ("relational", "match_recognize", "Row pattern recognition", "Match ordered row patterns with explicit skip, partition and measure semantics.", ["ordered_relation", "pattern", "measures"], "relation", "exact", "may_emit_summary_only"),
    ("relational", "write_relation", "Logical relation write", "Declare an effect intent to append, replace, merge or delete under transaction/idempotency laws.", ["relation", "target_ref", "write_mode"], "effect_intent", "exact", "effectful"),
    ("stream", "assign_event_time", "Assign event time", "Attach governed event timestamps with parse, timezone and invalid-time behavior.", ["stream", "timestamp_expression"], "timed_stream", "exact", "none"),
    ("stream", "derive_watermark", "Derive watermark", "Emit progress lower bounds under a declared lateness and idleness policy.", ["timed_stream", "watermark_policy"], "progress_stream", "exact", "declares_completeness_bound"),
    ("stream", "window_assign", "Assign windows", "Map each event to one or more finite logical windows under fixed, sliding, session or custom semantics.", ["timed_stream", "window_function"], "windowed_stream", "exact", "may_duplicate_across_windows"),
    ("stream", "trigger_panes", "Trigger panes", "Determine when early, on-time and late panes become observable and whether they accumulate or retract.", ["windowed_stream", "trigger_policy"], "pane_stream", "exact", "may_emit_partial_results"),
    ("stream", "temporal_join", "Temporal stream join", "Join time-varying relations under interval, version, watermark and state-retention laws.", ["left_stream", "right_stream", "time_condition"], "change_stream", "exact", "late_data_policy_dependent"),
    ("stream", "deduplicate", "Stream deduplication", "Retain representatives by identity within a bounded time or state horizon.", ["stream", "identity", "horizon"], "stream", "exact", "drops_duplicates"),
    ("stream", "changelog_normalize", "Changelog normalization", "Convert supported insert/update/delete encodings while preserving keyed relation evolution.", ["change_stream", "input_mode", "output_mode"], "change_stream", "exact", "none"),
    ("stream", "incrementalize", "Incrementalize", "Derive output changes from input changes for an eligible logical plan.", ["logical_plan", "change_relation"], "incremental_plan", "exact", "none"),
    ("stream", "materialize_updates", "Materialize changes", "Maintain a relation from ordered or commutative changes under key and conflict semantics.", ["change_stream", "key", "conflict_law"], "materialized_relation", "exact", "history_may_be_compacted"),
    ("stream", "stateful_transform", "Stateful transform", "Apply a typed transition function per declared key with timers, TTL and checkpoint semantics.", ["stream", "state_machine"], "stream", "exact", "state_expiry_may_lose_late_effects"),
    ("graph", "node_scan", "Node scan", "Read graph nodes matching declared labels/types and predicates.", ["property_graph", "node_pattern"], "node_relation", "exact", "drops_nonmatching_nodes"),
    ("graph", "edge_scan", "Edge scan", "Read graph edges matching direction, label/type and predicates.", ["property_graph", "edge_pattern"], "edge_relation", "exact", "drops_nonmatching_edges"),
    ("graph", "pattern_match", "Graph pattern match", "Return bindings satisfying a declared property-graph or RDF graph pattern and match mode.", ["graph", "pattern"], "binding_relation", "exact", "none"),
    ("graph", "expand", "Graph expansion", "Traverse one or more edges under direction, label, uniqueness and path-length laws.", ["graph", "frontier", "edge_constraint"], "path_or_node_relation", "exact", "none"),
    ("graph", "reachability", "Reachability", "Determine whether or which vertices are reachable under path constraints.", ["graph", "sources", "path_constraint"], "reachability_relation", "exact", "none"),
    ("graph", "shortest_path", "Shortest path", "Produce paths minimizing a declared weight algebra with tie and negative-cycle policy.", ["graph", "source", "destination", "weight"], "path_relation", "exact", "may_return_one_of_ties"),
    ("graph", "graph_project", "Graph projection", "Construct a derived graph from declared node/edge relations while preserving identity laws.", ["node_relation", "edge_relation"], "property_graph", "exact", "may_drop_properties_or_elements"),
    ("graph", "sparse_semiring_multiply", "Sparse semiring multiply", "Compose sparse matrices/vectors over an explicitly declared semiring.", ["sparse_left", "sparse_right", "semiring"], "sparse_result", "exact", "none"),
    ("spatial", "spatial_predicate", "Spatial predicate", "Evaluate a topological or metric predicate under declared geometry model, CRS and boundary law.", ["geometry_left", "geometry_right", "predicate"], "nullable_boolean", "exact", "none"),
    ("spatial", "spatial_measure", "Spatial measure", "Compute distance, length or area under declared CRS, unit and geodesic/planar model.", ["geometry", "measure_kind"], "quantity", "exact", "numeric_rounding"),
    ("spatial", "spatial_transform", "Coordinate transformation", "Transform geometry between identified CRS editions with axis and error contracts.", ["geometry", "source_crs", "target_crs"], "geometry", "bounded_approximation", "coordinate_rounding"),
    ("spatial", "spatial_overlay", "Spatial overlay", "Compute intersection, union, difference or symmetric difference with validity and precision laws.", ["geometry_left", "geometry_right", "overlay_kind"], "geometry", "exact", "representation_normalization"),
    ("spatial", "spatial_join", "Spatial join", "Join features whose geometries satisfy a declared spatial predicate.", ["left_features", "right_features", "predicate"], "relation", "exact", "drops_nonmatching_features"),
    ("spatial", "spatial_index_query", "Spatial index query", "Return a candidate or exact result set under an explicit false-positive/refinement contract.", ["spatial_index", "query_geometry"], "feature_relation", "bounded_approximation", "candidate_false_positives_possible"),
    ("numerical", "elementwise_map", "Elementwise map", "Apply a typed pure function pointwise with broadcast and missing-value semantics.", ["array_or_tensor", "function"], "array_or_tensor", "exact", "numeric_rounding"),
    ("numerical", "reduce", "Numerical reduction", "Fold values under a declared algebra, order/reassociation permission and error contract.", ["array_or_tensor", "reducer", "axes"], "scalar_or_tensor", "exact", "numeric_rounding"),
    ("numerical", "matrix_multiply", "Matrix multiplication", "Compute a declared dense or sparse matrix product with shape, transpose and precision semantics.", ["matrix_left", "matrix_right"], "matrix", "exact", "numeric_rounding"),
    ("numerical", "linear_solve", "Linear system solve", "Solve a declared linear system and report conditioning, convergence and residual posture.", ["matrix", "right_hand_side"], "solution_and_diagnostics", "bounded_approximation", "numeric_error"),
    ("numerical", "fft", "Discrete Fourier transform", "Compute a declared DFT/DCT/DST with normalization, direction, axes and complex layout semantics.", ["array", "transform_spec"], "complex_or_real_array", "bounded_approximation", "numeric_rounding"),
    ("numerical", "convolution", "Convolution", "Apply discrete convolution with boundary, stride, dilation and numeric semantics.", ["signal_or_tensor", "kernel_values"], "signal_or_tensor", "exact", "numeric_rounding"),
    ("approximate", "approx_distinct", "Approximate distinct count", "Estimate cardinality with declared sketch family, confidence and merge compatibility.", ["collection", "error_contract"], "estimate", "bounded_approximation", "statistical_error"),
    ("approximate", "approx_quantile", "Approximate quantile", "Estimate rank/quantile with declared worst-case or empirical error semantics.", ["collection", "quantile", "error_contract"], "estimate", "bounded_approximation", "rank_error"),
    ("approximate", "heavy_hitters", "Frequent items", "Estimate high-frequency items with declared capacity and error semantics.", ["collection", "capacity"], "estimated_frequency_relation", "bounded_approximation", "frequency_error"),
    ("approximate", "sample", "Governed sampling", "Select units under a declared probability design, seed and inclusion-weight contract.", ["population", "sampling_design"], "sample", "bounded_approximation", "population_information_loss"),
    ("encoding", "encode", "Semantic encoding", "Map logical values to a declared physical encoding while preserving stated laws.", ["logical_values", "encoding_contract"], "encoded_blocks", "exact", "none"),
    ("encoding", "decode", "Semantic decoding", "Recover logical values from a declared physical encoding or refuse malformed input.", ["encoded_blocks", "encoding_contract"], "logical_values", "exact", "none"),
    ("encoding", "compress", "Block compression", "Compress bytes or typed blocks under lossless or explicitly bounded-loss semantics.", ["blocks", "codec_contract"], "compressed_blocks", "exact", "none"),
    ("encoding", "decompress", "Block decompression", "Recover blocks, verify framing/checksums where declared and reject corruption.", ["compressed_blocks", "codec_contract"], "blocks", "exact", "none"),
    ("control", "exchange", "Logical exchange requirement", "Declare partitioning, ordering, delivery and framing requirements between plan regions.", ["relation_or_stream", "distribution_requirement"], "partitioned_relation_or_stream", "exact", "none"),
    ("control", "materialize", "Logical materialization", "Declare reusable result state with identity, freshness, invalidation and retention semantics.", ["logical_plan", "materialization_policy"], "materialized_result", "exact", "none"),
    ("control", "cancel", "Cancellation", "Request bounded termination and produce a receipt describing completed, partial and compensated effects.", ["execution_ref", "cancel_scope"], "cancellation_receipt", "exact", "may_leave_declared_partial_effects"),
]


LOGICAL_OPERATORS = []
for family, oid, name, semantics, inputs, output, exactness, loss in LOGICAL_ROWS:
    LOGICAL_OPERATORS.append({
        "operator_id": f"operator.qck.{family}.{oid}", "edition": EDITION, "status": "candidate",
        "family": family, "name": name, "semantic_owner_ref": f"context.qck.{ {'relational':'relational_algebra','stream':'stream_time_algebra','graph':'graph_algebra','spatial':'spatial_algebra','numerical':'numerical_algebra','approximate':'approximation','encoding':'codec_kernels','control':'logical_plan'}[family] }",
        "semantics": semantics, "input_roles": inputs, "output_contract": output,
        "parameter_contracts": [],
        "collection_semantics": ["bag/set/order and equality are explicit where applicable"],
        "null_missing_nan_semantics": ["must be resolved from owned type and operation contracts"],
        "time_semantics": ["event, validity, recording and processing time are distinct where applicable"],
        "exactness": exactness, "determinism": "semantic_result_deterministic_given_complete_order_and_deterministic_functions",
        "information_loss": loss,
        "laws": ["provider-independent meaning", "physical alternatives may not change declared outputs"],
        "failure_modes": ["type_mismatch", "unsupported_semantics", "resource_infeasible", "provider_gap"],
        "legal_decompositions": [], "evidence_refs": FAMILY_EVIDENCE[family],
        "gaps": ["Formal denotation and exhaustive dialect mappings remain to be completed."],
    })


# kernel id, operation suffixes, algorithm family, role, layouts, devices, exactness
KERNEL_ROWS = [
    ("scalar.arithmetic", ["numerical.elementwise_map"], "typed_arithmetic", "expression", ["scalar", "arrow_array"], ["cpu_scalar", "cpu_simd", "gpu"], "exact"),
    ("scalar.comparison", ["relational.filter", "numerical.elementwise_map"], "typed_comparison", "expression", ["scalar", "arrow_array"], ["cpu_scalar", "cpu_simd", "gpu"], "exact"),
    ("scalar.boolean_3vl", ["relational.filter"], "three_valued_logic", "expression", ["scalar", "validity_bitmap"], ["cpu_scalar", "cpu_simd", "gpu"], "exact"),
    ("scalar.cast", ["relational.project", "numerical.elementwise_map"], "typed_conversion", "expression", ["scalar", "arrow_array"], ["cpu_scalar", "cpu_simd", "gpu"], "exact"),
    ("scalar.decimal", ["numerical.elementwise_map", "numerical.reduce"], "fixed_decimal_arithmetic", "expression", ["fixed_width_array"], ["cpu_scalar", "cpu_simd"], "exact"),
    ("scalar.utf8", ["relational.project", "relational.filter"], "utf8_string", "expression", ["offset_buffer", "byte_buffer"], ["cpu_scalar", "cpu_simd"], "exact"),
    ("scalar.regex", ["relational.filter", "relational.project"], "regular_expression", "expression", ["utf8_array"], ["cpu_scalar", "cpu_simd", "wasm"], "exact"),
    ("scalar.temporal", ["relational.project", "relational.filter"], "calendar_and_timestamp", "expression", ["fixed_width_array", "timezone_dictionary"], ["cpu_scalar", "cpu_simd"], "exact"),
    ("scalar.json_path", ["relational.project", "relational.filter", "relational.unnest"], "json_path_evaluation", "expression", ["utf8_or_binary", "struct_array"], ["cpu_scalar", "cpu_simd"], "exact"),
    ("scalar.hash", ["relational.aggregate", "relational.inner_join", "stream.deduplicate"], "stable_or_seeded_hash", "expression", ["scalar", "arrow_array"], ["cpu_scalar", "cpu_simd", "gpu"], "exact"),
    ("vector.selection_bitmap", ["relational.filter"], "bitmap_selection", "vector", ["arrow_array", "validity_bitmap"], ["cpu_simd", "gpu"], "exact"),
    ("vector.take_gather", ["relational.project", "relational.sort"], "gather", "vector", ["arrow_array", "index_array"], ["cpu_simd", "gpu"], "exact"),
    ("vector.scatter", ["relational.project", "stream.materialize_updates"], "scatter", "vector", ["arrow_array", "index_array"], ["cpu_simd", "gpu"], "exact"),
    ("vector.dictionary_dispatch", ["relational.project", "relational.filter"], "dictionary_aware_vector", "vector", ["dictionary_array"], ["cpu_simd", "gpu"], "exact"),
    ("vector.fused_expression", ["relational.project", "relational.filter"], "fused_vector_expression", "vector", ["record_batch"], ["cpu_simd", "gpu"], "exact"),
    ("aggregate.hash", ["relational.aggregate"], "in_memory_hash_aggregation", "relational", ["record_batch", "hash_table"], ["cpu_simd", "gpu"], "exact"),
    ("aggregate.partitioned_hash", ["relational.aggregate"], "partitioned_hash_aggregation", "relational", ["record_batch", "partitioned_hash_state"], ["cpu_simd", "gpu"], "exact"),
    ("aggregate.sort", ["relational.aggregate"], "sort_based_aggregation", "relational", ["ordered_record_batch"], ["cpu_simd"], "exact"),
    ("aggregate.streaming", ["relational.aggregate", "stream.stateful_transform"], "ordered_stream_aggregation", "relational", ["ordered_stream"], ["cpu_scalar", "cpu_simd"], "exact"),
    ("aggregate.partial_combine", ["relational.aggregate", "control.exchange"], "algebraic_partial_aggregation", "relational", ["aggregate_state_batch"], ["cpu_simd", "gpu"], "exact"),
    ("aggregate.exact_distinct", ["relational.aggregate", "relational.distinct"], "exact_hash_set", "relational", ["record_batch", "hash_set"], ["cpu_simd", "gpu"], "exact"),
    ("aggregate.theta_sketch", ["approximate.approx_distinct"], "theta_sketch", "approximate", ["record_batch", "sketch_state"], ["cpu_scalar", "cpu_simd"], "bounded_approximation"),
    ("aggregate.hll_sketch", ["approximate.approx_distinct"], "hyperloglog", "approximate", ["record_batch", "sketch_state"], ["cpu_scalar", "cpu_simd"], "bounded_approximation"),
    ("aggregate.kll_sketch", ["approximate.approx_quantile"], "kll_quantile_sketch", "approximate", ["record_batch", "sketch_state"], ["cpu_scalar", "cpu_simd"], "bounded_approximation"),
    ("aggregate.tdigest", ["approximate.approx_quantile"], "t_digest", "approximate", ["record_batch", "sketch_state"], ["cpu_scalar", "cpu_simd"], "empirical_approximation"),
    ("aggregate.heavy_hitters", ["approximate.heavy_hitters"], "frequent_items_summary", "approximate", ["record_batch", "summary_state"], ["cpu_scalar", "cpu_simd"], "bounded_approximation"),
    ("window.segmented_scan", ["relational.window"], "segmented_prefix_scan", "relational", ["partitioned_ordered_batch"], ["cpu_simd", "gpu"], "exact"),
    ("window.rank", ["relational.window"], "rank_peer_groups", "relational", ["partitioned_ordered_batch"], ["cpu_simd", "gpu"], "exact"),
    ("window.sliding_aggregate", ["relational.window", "stream.window_assign"], "incremental_sliding_window", "relational", ["partitioned_ordered_stream"], ["cpu_scalar", "cpu_simd"], "exact"),
    ("join.nested_loop", ["relational.inner_join", "relational.left_outer_join", "spatial.spatial_join"], "nested_loop_join", "relational", ["record_batch"], ["cpu_scalar", "cpu_simd", "gpu"], "exact"),
    ("join.hash", ["relational.inner_join", "relational.left_outer_join", "relational.semi_join", "relational.anti_join"], "in_memory_hash_join", "relational", ["record_batch", "hash_table"], ["cpu_simd", "gpu"], "exact"),
    ("join.grace_hash", ["relational.inner_join", "relational.left_outer_join"], "partitioned_grace_hash_join", "relational", ["record_batch", "spill_partition"], ["cpu_simd"], "exact"),
    ("join.sort_merge", ["relational.inner_join", "relational.left_outer_join", "relational.full_outer_join"], "sort_merge_join", "relational", ["ordered_record_batch"], ["cpu_simd"], "exact"),
    ("join.index_nested_loop", ["relational.inner_join", "relational.left_outer_join"], "index_nested_loop", "relational", ["record_batch", "index_lookup"], ["cpu_scalar", "cpu_simd"], "exact"),
    ("join.broadcast_hash", ["relational.inner_join", "control.exchange"], "broadcast_hash_join", "distributed", ["partitioned_record_batch", "broadcast_state"], ["multi_node_cpu", "multi_node_gpu"], "exact"),
    ("join.symmetric_hash_stream", ["stream.temporal_join"], "symmetric_hash_join", "stream", ["keyed_change_stream", "bounded_state"], ["multi_node_cpu"], "exact"),
    ("join.asof_merge", ["relational.asof_join"], "ordered_asof_merge", "relational", ["ordered_record_batch"], ["cpu_simd"], "exact"),
    ("sort.comparison", ["relational.sort"], "comparison_sort", "relational", ["record_batch", "row_or_key_layout"], ["cpu_simd", "gpu"], "exact"),
    ("sort.radix", ["relational.sort"], "radix_sort", "relational", ["fixed_width_keys"], ["cpu_simd", "gpu"], "exact"),
    ("sort.external_merge", ["relational.sort"], "external_merge_sort", "external_memory", ["record_batch", "spill_runs"], ["cpu_simd"], "exact"),
    ("sort.topk_heap", ["relational.top_k"], "bounded_heap_topk", "relational", ["record_batch", "heap"], ["cpu_scalar", "cpu_simd"], "exact"),
    ("sort.distributed_range", ["relational.sort", "control.exchange"], "range_partition_and_merge", "distributed", ["partitioned_record_batch"], ["multi_node_cpu", "multi_node_gpu"], "exact"),
    ("graph.bfs_frontier", ["graph.expand", "graph.reachability"], "breadth_first_frontier", "graph", ["csr", "frontier_bitmap"], ["cpu_simd", "gpu", "multi_node_cpu"], "exact"),
    ("graph.dijkstra", ["graph.shortest_path"], "dijkstra_shortest_path", "graph", ["csr", "priority_queue"], ["cpu_scalar", "cpu_simd"], "exact"),
    ("graph.bellman_ford", ["graph.shortest_path"], "bellman_ford", "graph", ["edge_list", "distance_vector"], ["cpu_simd", "gpu"], "exact"),
    ("graph.pattern_backtrack", ["graph.pattern_match"], "constraint_backtracking_pattern_match", "graph", ["adjacency_index", "binding_table"], ["cpu_scalar", "cpu_simd"], "exact"),
    ("graph.sparse_mxv", ["graph.sparse_semiring_multiply"], "sparse_matrix_vector_semiring", "graph", ["csr", "csc", "sparse_vector"], ["cpu_simd", "gpu", "multi_node_cpu"], "exact"),
    ("graph.sparse_mxm", ["graph.sparse_semiring_multiply"], "sparse_matrix_matrix_semiring", "graph", ["csr", "csc"], ["cpu_simd", "gpu", "multi_node_cpu"], "exact"),
    ("spatial.bbox_filter", ["spatial.spatial_index_query", "spatial.spatial_join"], "minimum_bounding_rectangle_filter", "spatial", ["geometry_array", "bbox_index"], ["cpu_simd", "gpu"], "bounded_approximation"),
    ("spatial.rtree_query", ["spatial.spatial_index_query"], "rtree_search", "spatial", ["rtree", "geometry_or_bbox"], ["cpu_scalar", "cpu_simd"], "bounded_approximation"),
    ("spatial.exact_predicate", ["spatial.spatial_predicate", "spatial.spatial_join"], "robust_topological_predicate", "spatial", ["geometry_array"], ["cpu_scalar", "cpu_simd"], "exact"),
    ("spatial.sweep_join", ["spatial.spatial_join"], "plane_sweep_spatial_join", "spatial", ["geometry_array", "ordered_events"], ["cpu_simd"], "exact"),
    ("spatial.overlay", ["spatial.spatial_overlay"], "robust_geometry_overlay", "spatial", ["geometry_array"], ["cpu_scalar", "cpu_simd"], "exact"),
    ("spatial.reproject", ["spatial.spatial_transform"], "coordinate_operation_pipeline", "spatial", ["coordinate_array"], ["cpu_simd", "gpu"], "bounded_approximation"),
    ("spatial.geodesic", ["spatial.spatial_measure"], "ellipsoidal_geodesic", "spatial", ["coordinate_array"], ["cpu_scalar", "cpu_simd"], "bounded_approximation"),
    ("numerical.blas1", ["numerical.elementwise_map", "numerical.reduce"], "blas_level_1", "numerical", ["strided_vector"], ["cpu_simd", "gpu"], "exact"),
    ("numerical.blas2", ["numerical.matrix_multiply"], "blas_level_2", "numerical", ["dense_matrix", "strided_vector"], ["cpu_simd", "gpu"], "exact"),
    ("numerical.gemm", ["numerical.matrix_multiply"], "blas_gemm", "numerical", ["dense_matrix"], ["cpu_simd", "gpu"], "exact"),
    ("numerical.spmv", ["numerical.matrix_multiply", "graph.sparse_semiring_multiply"], "sparse_matrix_vector", "numerical", ["csr", "csc", "sparse_vector"], ["cpu_simd", "gpu"], "exact"),
    ("numerical.linear_solver", ["numerical.linear_solve"], "factorization_or_iterative_solve", "numerical", ["dense_matrix", "sparse_matrix"], ["cpu_simd", "gpu", "multi_node_cpu"], "bounded_approximation"),
    ("numerical.fft", ["numerical.fft"], "fast_fourier_transform", "numerical", ["strided_tensor", "complex_interleaved", "complex_split"], ["cpu_simd", "gpu", "multi_node_cpu"], "bounded_approximation"),
    ("numerical.direct_convolution", ["numerical.convolution"], "direct_convolution", "numerical", ["strided_tensor"], ["cpu_simd", "gpu"], "exact"),
    ("numerical.fft_convolution", ["numerical.convolution", "numerical.fft"], "fft_convolution", "numerical", ["strided_tensor"], ["cpu_simd", "gpu"], "bounded_approximation"),
    ("codec.dictionary", ["encoding.encode", "encoding.decode"], "dictionary_encoding", "codec", ["typed_page", "dictionary_page"], ["cpu_scalar", "cpu_simd", "gpu"], "exact"),
    ("codec.delta_binary", ["encoding.encode", "encoding.decode"], "delta_binary_packed", "codec", ["integer_page"], ["cpu_simd", "gpu"], "exact"),
    ("codec.rle_bitpack", ["encoding.encode", "encoding.decode"], "run_length_bitpack_hybrid", "codec", ["integer_or_boolean_page"], ["cpu_simd", "gpu"], "exact"),
    ("codec.byte_stream_split", ["encoding.encode", "encoding.decode"], "byte_stream_split", "codec", ["fixed_width_page"], ["cpu_simd", "gpu"], "exact"),
    ("codec.zstd", ["encoding.compress", "encoding.decompress"], "zstandard", "codec", ["byte_block"], ["cpu_scalar", "cpu_simd"], "exact"),
    ("codec.lz4", ["encoding.compress", "encoding.decompress"], "lz4_block_or_frame", "codec", ["byte_block"], ["cpu_scalar", "cpu_simd", "gpu"], "exact"),
    ("codec.snappy", ["encoding.compress", "encoding.decompress"], "snappy", "codec", ["byte_block"], ["cpu_scalar", "cpu_simd"], "exact"),
    ("codec.adaptive_block", ["encoding.encode", "encoding.decode", "encoding.compress", "encoding.decompress"], "adaptive_column_block", "codec", ["typed_page"], ["cpu_simd"], "exact"),
    ("codec.alp_float", ["encoding.encode", "encoding.decode"], "adaptive_lossless_float", "codec", ["floating_page"], ["cpu_simd"], "exact"),
    ("runtime.hash_exchange", ["control.exchange"], "hash_partition_exchange", "runtime_primitive", ["record_batch", "framed_stream"], ["multi_node_cpu", "multi_node_gpu"], "exact"),
    ("runtime.range_exchange", ["control.exchange", "relational.sort"], "range_partition_exchange", "runtime_primitive", ["record_batch", "framed_stream"], ["multi_node_cpu", "multi_node_gpu"], "exact"),
    ("runtime.broadcast_exchange", ["control.exchange"], "broadcast_exchange", "runtime_primitive", ["record_batch", "framed_stream"], ["multi_node_cpu", "multi_node_gpu"], "exact"),
    ("runtime.spill_hash_state", ["relational.aggregate", "relational.inner_join"], "partitioned_hash_spill", "runtime_primitive", ["hash_state", "spill_files"], ["cpu_simd"], "exact"),
    ("runtime.spill_sorted_runs", ["relational.sort"], "sorted_run_spill", "runtime_primitive", ["record_batch", "spill_files"], ["cpu_simd"], "exact"),
    ("runtime.parquet_scan", ["relational.scan", "encoding.decode", "encoding.decompress"], "columnar_scan_with_pruning", "runtime_primitive", ["parquet_pages", "record_batch"], ["cpu_simd", "gpu"], "exact"),
    ("runtime.materialized_cache", ["control.materialize"], "content_or_snapshot_keyed_cache", "runtime_primitive", ["record_batch", "cache_index"], ["cpu_scalar", "multi_node_cpu"], "exact"),
]


KERNELS = []
for kid, op_suffixes, algorithm, role, layouts, devices, exactness in KERNEL_ROWS:
    approximation = exactness != "exact"
    KERNELS.append({
        "kernel_id": f"kernel.qck.{kid}", "edition": EDITION, "status": "candidate",
        "operation_refs": [f"operator.qck.{suffix}" for suffix in op_suffixes],
        "algorithm_family": algorithm, "kernel_role": role,
        "supported_type_contracts": ["exact types and editions are offer-bound"],
        "supported_layouts": layouts, "state_contract": "explicit bounded state, spill path, or refusal",
        "exactness": exactness,
        "determinism_posture": "depends_on_order_parallelism_target_and_function_contracts",
        "numeric_posture": "IEEE-754 behavior, decimal rules, rounding, overflow, reassociation and FMA policy must be bound where numeric",
        "error_model": "declared confidence/error parameters required" if approximation else "none beyond declared numeric representation",
        "information_loss": "declared_and_receipted" if approximation else "none unless referenced logical operation declares loss",
        "ordering_behavior": "preserves, establishes or destroys order only as declared by offer",
        "memory_contract": "finite peak, reservation, growth, spill and cleanup behavior required",
        "complexity_contract": "input-sensitive time, memory and communication estimates required",
        "parallelism_contract": "partitioning, associativity, commutativity, thread safety and merge laws required",
        "supported_target_classes": devices,
        "side_effects": ["none"] if role not in {"runtime_primitive"} else ["bounded_runtime_io_may_apply"],
        "cancellation_contract": "cooperative safe points, cleanup and partial-output status required",
        "failure_modes": ["unsupported_type_or_layout", "resource_exhausted", "cancelled", "target_failure", "invalid_input"],
        "fallback_law": "another kernel only with exact contract compatibility; approximation requires prior authorization; otherwise refuse",
        "evidence_refs": ["source.qck.arrow.compute", "source.qck.datafusion.features"],
        "gaps": ["Concrete benchmark envelopes and provider-specific conformance receipts are not yet populated."],
    })


PROVIDER_ROWS = [
    ("logical_ir", "Logical IR producer/consumer", ["logical_plan", "function_registry"], ["logical_ir_round_trip", "extension_resolution"], ["host_process"], ["source.qck.substrait.spec"]),
    ("rule_optimizer", "Extensible rule and cost optimizer", ["rewrite", "cost", "plan_search"], ["logical_rewrite", "physical_alternative_enumeration"], ["jvm", "native"], ["source.qck.calcite.algebra", "source.qck.datafusion.optimizer"]),
    ("embedded_vector_cpu", "Embedded vectorized CPU engine", ["physical_lowering", "expression", "relational_kernels"], ["columnar_vector_execution", "in_process_results"], ["cpu_scalar", "cpu_simd"], ["source.qck.datafusion.paper", "source.qck.sqlite_he.paper"]),
    ("modular_execution", "Modular execution library", ["expression", "relational_kernels", "memory", "spill"], ["host_integrated_execution", "memory_arbitration"], ["cpu_simd"], ["source.qck.velox.paper"]),
    ("distributed_mpp", "Distributed MPP query engine", ["exchange", "scheduler", "resource_control"], ["distributed_exchange", "fault_scoped_execution"], ["multi_node_cpu"], ["source.qck.trino.fte", "source.qck.trino.resources"]),
    ("stateful_stream", "Stateful stream processor", ["stream_time_algebra", "scheduler", "memory"], ["event_time", "checkpointed_state", "watermarks"], ["multi_node_cpu"], ["source.qck.flink.time", "source.qck.beam.model"]),
    ("incremental_compute", "Incremental computation engine", ["stream_time_algebra", "materialization"], ["delta_evaluation", "maintained_arrangements"], ["cpu_simd", "multi_node_cpu"], ["source.qck.dbsp.paper", "source.qck.differential.arrangements"]),
    ("federated", "Federated query engine", ["federation", "physical_lowering"], ["connector_capability_negotiation", "partial_pushdown"], ["multi_node_cpu"], ["source.qck.calcite.adapters", "source.qck.trino.pushdown"]),
    ("gpu_analytic", "GPU analytical execution provider", ["target_binding", "expression", "relational_kernels"], ["device_resident_batches", "gpu_kernels"], ["cuda_gpu", "rocm_gpu"], ["source.qck.arrow.c_device", "source.qck.cuda.guide", "source.qck.hip.model"]),
    ("graph_compute", "Graph query and kernel provider", ["graph_algebra", "graph_kernels"], ["pattern_and_path_execution", "sparse_semiring_kernels"], ["cpu_simd", "gpu", "multi_node_cpu"], ["source.qck.graphblas.spec", "source.qck.opencypher.tck"]),
    ("spatial_compute", "Spatial query and kernel provider", ["spatial_algebra", "spatial_kernels"], ["crs_qualified_geometry_operations", "spatial_index_refinement"], ["cpu_simd", "gpu"], ["source.qck.ogc.sfa", "source.qck.ogc.cql2"]),
    ("numerical_hpc", "Numerical and HPC kernel provider", ["numerical_algebra", "numerical_kernels", "numeric_reproducibility"], ["dense_sparse_fft_kernels", "numeric_diagnostics"], ["cpu_simd", "gpu", "multi_node_cpu"], ["source.qck.blas.spec", "source.qck.lapack.guide", "source.qck.fftw.docs"]),
    ("codec", "Encoding and codec provider", ["codec_kernels"], ["typed_encode_decode", "block_compress_decompress"], ["cpu_scalar", "cpu_simd", "gpu"], ["source.qck.parquet.encoding", "source.qck.parquet.compression"]),
    ("sandboxed_udf", "Sandboxed extension provider", ["extension_host"], ["versioned_component_abi", "capability_limited_execution"], ["wasm"], ["source.qck.wasm.spec"]),
    ("sketch", "Approximate sketch provider", ["approximation"], ["mergeable_sketches", "error_bound_reporting"], ["cpu_scalar", "cpu_simd"], ["source.qck.datasketches.theta", "source.qck.datasketches.quantile"]),
]


PROVIDERS = []
for pid, name, contexts, capabilities, targets, evidence in PROVIDER_ROWS:
    PROVIDERS.append({
        "provider_capability_id": f"provider_capability.qck.{pid}", "edition": EDITION,
        "status": "capability_class", "name": name,
        "context_refs": [f"context.qck.{c}" for c in contexts],
        "offered_capabilities": capabilities,
        "semantic_contract_refs": [], "operation_refs": [], "kernel_refs": [],
        "supported_target_classes": targets,
        "guarantees": ["offer must be editioned and scoped to exact operations, types, layouts and targets"],
        "limits": ["deployment-specific limits require runtime probes or signed provider evidence"],
        "configuration_decisions": ["parallelism", "memory_budget", "spill_policy", "exactness", "reproducibility"],
        "conformance_requirements": ["semantic oracle", "resource envelope", "failure and cancellation tests"],
        "evidence_refs": evidence,
        "invalidation_triggers": ["provider_version_change", "target_change", "configuration_change", "evidence_expiry"],
        "gaps": ["This is a capability class, not a qualified concrete deployment offer."],
    })


TARGET_ROWS = [
    ("cpu_scalar", "Scalar CPU", "cpu", [], ["host_memory"], ["threads", "memory_bytes"]),
    ("x86_avx2", "x86-64 CPU with AVX2", "cpu", ["avx2"], ["host_memory", "numa"], ["cores", "simd_width", "memory_bytes"]),
    ("x86_avx512", "x86-64 CPU with AVX-512", "cpu", ["avx512"], ["host_memory", "numa"], ["cores", "simd_width", "memory_bytes"]),
    ("arm_neon", "AArch64 CPU with NEON", "cpu", ["neon"], ["host_memory", "numa"], ["cores", "simd_width", "memory_bytes"]),
    ("arm_sve", "AArch64 CPU with SVE", "cpu", ["sve"], ["host_memory", "numa"], ["cores", "runtime_vector_length", "memory_bytes"]),
    ("cuda_gpu", "CUDA GPU", "gpu", ["cuda"], ["device_memory", "pinned_host", "unified_memory"], ["compute_capability", "sm_count", "device_memory_bytes"]),
    ("rocm_gpu", "ROCm/HIP GPU", "gpu", ["hip", "rocm"], ["device_memory", "pinned_host", "managed_memory"], ["gfx_arch", "cu_count", "device_memory_bytes"]),
    ("sycl_device", "SYCL heterogeneous device", "heterogeneous", ["sycl_2020"], ["buffers", "unified_shared_memory"], ["backend", "device_aspects", "memory_bytes"]),
    ("wasm", "WebAssembly sandbox", "portable_vm", ["wasm_core", "wasi_if_enabled"], ["linear_memory"], ["memory_pages", "fuel_or_epoch_budget"]),
    ("multi_node_cpu", "Homogeneous multi-node CPU", "distributed", ["network_exchange"], ["host_memory", "local_spill", "remote_exchange"], ["node_count", "cores", "memory_bytes", "network_bytes_per_second"]),
    ("multi_node_gpu", "Multi-node GPU", "distributed_heterogeneous", ["network_exchange", "device_runtime"], ["device_memory", "host_memory", "remote_exchange"], ["node_count", "device_count", "device_memory_bytes", "network_bytes_per_second"]),
    ("disaggregated", "Disaggregated compute and storage", "distributed_disaggregated", ["object_or_remote_storage"], ["host_memory", "local_cache", "remote_storage"], ["compute_slots", "cache_bytes", "network_bytes_per_second", "remote_iops"]),
]


TARGETS = []
for tid, name, kind, interfaces, memory, resources in TARGET_ROWS:
    TARGETS.append({
        "target_profile_id": f"target.qck.{tid}", "edition": EDITION, "status": "target_class",
        "name": name, "target_kind": kind, "required_interfaces": interfaces,
        "memory_spaces": memory, "resource_dimensions": resources,
        "supported_layouts": ["must be declared by concrete target offer"],
        "numeric_traits": ["floating formats", "rounding", "FMA", "denormal", "reassociation", "atomic reduction behavior"],
        "parallel_traits": ["worker model", "synchronization", "ordering", "atomic and memory consistency"],
        "transfer_traits": ["copy directions", "zero-copy eligibility", "synchronization events", "bandwidth and latency"],
        "isolation_traits": ["process/device/sandbox boundary and available capabilities"],
        "cancellation_traits": ["preemption and cooperative safe-point behavior"],
        "qualification_requirements": ["feature probe", "kernel conformance", "numeric posture", "resource benchmark"],
        "evidence_refs": ["source.qck.arrow.c_device", "source.qck.sycl.spec"],
        "gaps": ["Concrete target instances require versioned feature probes."],
    })


MAPPING_ROWS = [
    ("exact_join", "operator.qck.relational.inner_join", ["exact", "declared_equality", "declared_null_semantics"], ["algorithm_family", "supported_type_contracts", "memory_contract"], "refuse"),
    ("ordered_topk", "operator.qck.relational.top_k", ["total_order_or_explicit_tie_policy", "stable_if_required"], ["ordering_behavior", "supported_layouts"], "refuse"),
    ("stream_temporal_join", "operator.qck.stream.temporal_join", ["event_time", "watermark", "bounded_state", "late_data_policy"], ["state_contract", "cancellation_contract"], "refuse"),
    ("incremental_plan", "operator.qck.stream.incrementalize", ["delta_semantics", "fixpoint_and_recursion_support_if_used"], ["exactness", "state_contract"], "full_recompute_if_equivalent_and_budget_feasible"),
    ("spatial_exact", "operator.qck.spatial.spatial_predicate", ["geometry_model", "crs", "precision", "exact_refinement"], ["supported_type_contracts", "exactness"], "refuse"),
    ("spatial_candidate", "operator.qck.spatial.spatial_index_query", ["false_positive_contract", "refinement_stage"], ["exactness", "information_loss"], "scan_if_budget_feasible"),
    ("graph_path", "operator.qck.graph.shortest_path", ["weight_algebra", "negative_weight_policy", "tie_policy"], ["algorithm_family", "exactness"], "refuse"),
    ("matrix_multiply", "operator.qck.numerical.matrix_multiply", ["shape", "layout", "precision", "numeric_error"], ["supported_layouts", "supported_target_classes", "numeric_posture"], "portable_cpu_kernel_if_qualified"),
    ("reproducible_reduce", "operator.qck.numerical.reduce", ["qualified_target_bitwise_or_stronger", "fixed_reduction_order"], ["determinism_posture", "numeric_posture"], "refuse_or_declared_tolerance_degradation"),
    ("approx_distinct", "operator.qck.approximate.approx_distinct", ["approximation_authorized", "confidence", "merge_compatibility"], ["exactness", "error_model"], "exact_distinct_if_budget_feasible"),
    ("approx_quantile", "operator.qck.approximate.approx_quantile", ["rank_or_value_error_defined", "order_sensitivity_declared"], ["exactness", "error_model"], "exact_quantile_if_budget_feasible"),
    ("lossless_codec", "operator.qck.encoding.compress", ["lossless", "framing", "splittability", "checksum_policy"], ["supported_layouts", "information_loss", "supported_target_classes"], "uncompressed_if_allowed"),
    ("random_access_codec", "operator.qck.encoding.decode", ["page_or_block_addressability", "bounded_decode_amplification"], ["memory_contract", "supported_layouts"], "refuse"),
    ("gpu_offload", "operator.qck.relational.project", ["device_compatible_types", "transfer_budget", "kernel_coverage"], ["supported_target_classes", "supported_layouts"], "qualified_cpu_kernel"),
    ("federated_pushdown", "operator.qck.relational.filter", ["remote_semantic_equivalence", "policy_allows_remote", "remote_snapshot_compatible"], ["semantic_contract_refs", "limits"], "execute_locally"),
    ("spillable_sort", "operator.qck.relational.sort", ["finite_memory", "spill_storage_authorized", "order_preserved"], ["memory_contract", "cancellation_contract"], "refuse"),
    ("fault_tolerant_exchange", "operator.qck.control.exchange", ["retry_scope", "deduplication", "durable_exchange", "ordering"], ["guarantees", "limits"], "fail_query"),
    ("sandboxed_udf", "operator.qck.relational.project", ["function_signature", "volatility", "effects", "parallel_safety", "resource_budget", "sandbox"], ["configuration_decisions", "conformance_requirements"], "refuse"),
    ("materialized_reuse", "operator.qck.control.materialize", ["semantic_identity", "snapshot_compatibility", "freshness", "policy"], ["guarantees", "invalidation_triggers"], "recompute"),
    ("cancel_execution", "operator.qck.control.cancel", ["cancel_scope", "deadline", "effect_disposition"], ["cancellation_contract", "failure_modes"], "force_terminate_with_partial_effect_receipt_if_authorized"),
]


MAPPINGS = []
for mid, subject, guarantees, offer_fields, fallback in MAPPING_ROWS:
    MAPPINGS.append({
        "mapping_id": f"mapping.qck.{mid}", "edition": EDITION, "status": "candidate",
        "subject_ref": subject, "binding_phase": "physical_binding",
        "required_guarantees": guarantees, "required_offer_fields": offer_fields,
        "selection_laws": ["enumerate all structurally compatible offers", "prove semantic and guarantee compatibility before cost ranking", "retain rejected alternatives and reasons"],
        "fallback_law": fallback,
        "refusal_conditions": ["missing_semantics", "unqualified_provider", "resource_infeasible", "evidence_insufficient"],
        "required_receipts": ["binding_decision", "provider_and_target_versions", "guarantee_posture", "resource_estimate", "fallback_or_refusal"],
        "evidence_refs": ["source.qck.substrait.spec", "source.qck.calcite.adapters", "source.qck.datafusion.optimizer"],
        "gaps": ["Machine-checkable cross-provider offer vocabulary remains incomplete."],
    })


LIBRARY_ROWS = [
    ("query-syntax", "semantic_pure", "language", [], ["parse", "format", "surface_ast"], ["dialect selection is not provider selection"]),
    ("query-binding", "semantic_pure", "binding", [], ["bind_names", "resolve_scope", "bind_authority"], ["does not access a source directly"]),
    ("query-types", "semantic_pure", "typing", [], ["infer_type", "coerce", "resolve_overload"], ["does not own physical layout"]),
    ("function-contracts", "semantic_pure", "function_registry", [], ["register_signature", "resolve_function_edition"], ["contains no function implementation"]),
    ("logical-plan-ir", "semantic_pure", "logical_plan", ["operator.qck.relational.project", "operator.qck.relational.filter"], ["construct_plan", "validate_plan"], ["contains no provider node"]),
    ("relational-semantics", "semantic_pure", "relational_algebra", ["operator.qck.relational.inner_join", "operator.qck.relational.aggregate", "operator.qck.relational.window"], ["denote_relation", "typecheck_relation"], ["contains no join algorithm"]),
    ("stream-time-semantics", "semantic_pure", "stream_time_algebra", ["operator.qck.stream.derive_watermark", "operator.qck.stream.temporal_join"], ["denote_change", "validate_progress"], ["contains no scheduler"]),
    ("graph-semantics", "semantic_pure", "graph_algebra", ["operator.qck.graph.pattern_match", "operator.qck.graph.shortest_path"], ["denote_graph_pattern", "validate_path_contract"], ["contains no graph storage"]),
    ("spatial-semantics", "semantic_pure", "spatial_algebra", ["operator.qck.spatial.spatial_predicate", "operator.qck.spatial.spatial_transform"], ["validate_crs", "denote_spatial_operation"], ["contains no geometry implementation"]),
    ("numerical-semantics", "semantic_pure", "numerical_algebra", ["operator.qck.numerical.matrix_multiply", "operator.qck.numerical.reduce"], ["validate_shape", "derive_numeric_contract"], ["contains no device kernel"]),
    ("rewrite-contracts", "semantic_pure", "rewrite", [], ["declare_rewrite", "check_applicability"], ["contains no cost-based selection"]),
    ("query-equivalence-oracles", "test_oracle", "conformance", [], ["prove_or_bound_equivalence", "find_counterexample"], ["inconclusive is not proof"]),
    ("statistics-properties", "algorithm_pure", "statistics", [], ["derive_properties", "merge_statistics"], ["does not select a plan"]),
    ("cardinality-estimation", "algorithm_pure", "cardinality", [], ["estimate_cardinality", "calibrate_uncertainty"], ["estimate is not observed truth"]),
    ("cost-plan-search", "algorithm_pure", "plan_search", [], ["estimate_cost", "enumerate_alternatives", "select_by_law"], ["does not change semantics"]),
    ("physical-lowering", "policy_pure", "physical_lowering", [], ["derive_requirements", "bind_algorithms"], ["does not dispatch by provider name"]),
    ("expression-kernels", "algorithm_pure", "expression", ["operator.qck.relational.project", "operator.qck.relational.filter"], ["evaluate_scalar", "evaluate_vector"], ["does not own expression semantics"]),
    ("relational-kernels", "algorithm_pure", "relational_kernels", ["operator.qck.relational.inner_join", "operator.qck.relational.aggregate", "operator.qck.relational.sort"], ["execute_join", "execute_aggregate", "execute_sort"], ["does not own relation semantics"]),
    ("graph-kernels", "algorithm_pure", "graph_kernels", ["operator.qck.graph.expand", "operator.qck.graph.sparse_semiring_multiply"], ["execute_frontier", "execute_sparse_semiring"], ["does not own graph query meaning"]),
    ("spatial-kernels", "algorithm_pure", "spatial_kernels", ["operator.qck.spatial.spatial_predicate", "operator.qck.spatial.spatial_overlay"], ["execute_predicate", "execute_overlay"], ["does not infer CRS"]),
    ("numerical-kernels", "algorithm_pure", "numerical_kernels", ["operator.qck.numerical.matrix_multiply", "operator.qck.numerical.fft"], ["execute_dense", "execute_sparse", "execute_fft"], ["does not weaken numeric posture"]),
    ("codec-kernels", "algorithm_pure", "codec_kernels", ["operator.qck.encoding.encode", "operator.qck.encoding.decode", "operator.qck.encoding.compress", "operator.qck.encoding.decompress"], ["encode_block", "decode_block", "compress_block", "decompress_block"], ["does not select storage policy"]),
    ("memory-runtime", "runtime_mechanism", "memory", [], ["reserve", "allocate", "reclaim", "arbitrate"], ["does not guess budgets"]),
    ("spill-runtime", "runtime_mechanism", "spill", [], ["spill", "restore", "cleanup"], ["does not own durable storage semantics"]),
    ("exchange-runtime", "runtime_mechanism", "exchange", ["operator.qck.control.exchange"], ["partition", "frame", "send", "receive", "deduplicate"], ["does not claim end-to-end exactly-once alone"]),
    ("execution-scheduler", "runtime_mechanism", "scheduler", [], ["schedule_pipeline", "backpressure", "cancel_task"], ["does not alter logical order"]),
    ("adaptive-execution", "policy_pure", "adaptive", [], ["observe_runtime", "propose_replan", "validate_replan"], ["does not apply an unproved rewrite"]),
    ("federation-adapters", "provider_adapter", "federation", [], ["discover_remote_offer", "lower_pushdown", "adapt_result"], ["does not pretend dialects are equivalent"]),
    ("udf-extension-host", "runtime_mechanism", "extension_host", [], ["load_component", "enforce_capabilities", "invoke", "meter"], ["does not trust undeclared effects"]),
    ("target-backends", "target_backend", "target_binding", [], ["probe_target", "compile_or_load_kernel", "transfer_buffers"], ["does not choose a target without compiler binding"]),
    ("query-receipts", "runtime_mechanism", "diagnostics", [], ["record_plan", "record_resources", "record_guarantees", "record_failures"], ["does not claim evidence beyond captured scope"]),
    ("kernel-conformance", "test_oracle", "conformance", [], ["golden_test", "differential_test", "property_test", "numeric_test"], ["benchmark is not semantic proof"]),
]


LIBRARIES = []
for lid, kind, context, operations, traits, forbidden in LIBRARY_ROWS:
    pure = kind in {"semantic_pure", "algorithm_pure", "policy_pure", "test_oracle"}
    owner_refs = [f"context.qck.{context}"] if kind == "semantic_pure" else []
    LIBRARIES.append({
        "library_id": f"library.qck.{lid}", "edition": EDITION, "status": "hypothesis",
        "library_kind": kind, "semantic_owner_refs": owner_refs,
        "contributes_to_context_refs": [f"context.qck.{context}"],
        "effect_boundary": "pure_no_io" if pure else ("ffi_boundary" if kind in {"provider_adapter", "target_backend"} else "effectful_runtime"),
        "public_types": [f"{lid.replace('-', '_')}_contract", f"{lid.replace('-', '_')}_error"],
        "public_traits": traits, "operation_refs": operations,
        "error_contracts": ["typed_refusal", "resource_exhausted", "cancelled", "incompatible_contract"],
        "decision_refs": [], "requirement_refs": [], "offer_refs": [],
        "configuration_contracts": ["all semantic and physical decisions are explicit inputs"],
        "effect_intents": [] if pure else ["typed runtime intent only"],
        "runtime_receipts": [] if pure else ["invocation, version, target, resources, outcome and residual effects"],
        "laws": ["provider-neutral public contract", "illegal states rejected at construction", "no hidden semantic defaults"],
        "oracles": ["golden", "property", "differential", "conformance"],
        "resource_contracts": ["finite memory, CPU/device, I/O, network and time budget or refusal"],
        "concurrency": ["Send/Sync/thread-safety and ordering posture are explicit"],
        "cancellation": ["safe points, cleanup and partial effects are explicit"],
        "unsafe_ffi_generated_policy": ["unsafe and FFI isolated behind audited adapters"],
        "dependencies": [], "targets": ["provider_neutral_contract"],
        "compatibility": ["editioned semantic compatibility relation"],
        "removal_seams": ["replace through the same conformance-qualified contract"],
        "forbidden_responsibilities": forbidden,
        "evidence_refs": ["source.qck.substrait.spec", "source.qck.arrow.c_data", "source.qck.velox.paper"],
        "gaps": ["Crate/API design and two independent implementations remain future gates."],
    })


INNOVATION_ROWS = [
    ("modular_execution_velox", 2022, "Reusable vectorized execution separated from a full database engine", "A host engine can bind a shared execution library while retaining language and scheduling ownership.", ["source.qck.velox.paper"]),
    ("vectorized_lakehouse_photon", 2022, "Native vectorized execution with runtime micro-batch adaptivity and hybrid fallback", "Kernel selection and fallback must be explicit plan decisions with transition costs and receipts.", ["source.qck.photon.paper"]),
    ("sqlite_analytic_path", 2022, "Alternative analytical execution path for an embedded row-oriented engine", "One semantic plan may bind different physical paths by workload without changing the application API.", ["source.qck.sqlite_he.paper"]),
    ("dbsp_incrementalization", 2023, "Algebraic automatic incrementalization for rich queries", "Incremental execution is a compiler transform with proof obligations, not a separate business semantic type.", ["source.qck.dbsp.paper"]),
    ("btrblocks", 2023, "Adaptive block-level columnar compression for data lakes", "Codec selection can be data-block adaptive while staying behind a typed encode/decode contract.", ["source.qck.btrblocks.paper"]),
    ("fastlanes_layout", 2023, "Vectorization-oriented compression layout", "Layout is an explicit kernel compatibility dimension because decode speed and SIMD access depend on it.", ["source.qck.fastlanes.paper"]),
    ("heterogeneous_cache", 2023, "Joint NVMe, host-memory and GPU data-placement optimization", "Cost models must cover transfer paths and multiple memory spaces rather than CPU time alone.", ["source.qck.hetcache.paper"]),
    ("pipeline_groups", 2023, "Pipeline grouping for disaggregated memory reuse", "Pipeline scheduling and shared-data transfer are physical-plan dimensions distinct from logical operators.", ["source.qck.pipeline_group.paper"]),
    ("gql_standard", 2024, "First international property-graph query language standard", "Graph query semantics and conformance are first-class, not forced into unnamed relational extensions.", ["source.qck.gql.standard"]),
    ("alp_float_compression", 2024, "Adaptive lossless floating-point compression", "Floating-point compression requires bitwise losslessness and typed-value qualification rather than generic byte-codec labels.", ["source.qck.alp.paper"]),
    ("datafusion_modularity", 2024, "Embeddable Rust query engine with reusable planner and execution modules", "Provider offers can be granular libraries, not only whole engines.", ["source.qck.datafusion.paper"]),
    ("vector_function_authoring", 2024, "Simplified function authoring with vector-encoding-aware specialization", "Function semantics, simple implementation and optimized vector specialization need separate identities and precedence rules.", ["source.qck.velox.function_authoring"]),
    ("verieql", 2024, "Bounded equivalence verification for complex SQL with constraints", "Rewrite evidence can include counterexample search and bounded proofs with explicitly limited coverage.", ["source.qck.verieql.paper"]),
    ("openivm", 2024, "SQL-to-SQL incremental view maintenance compiler", "Incrementalization may lower to ordinary provider operations when the target lacks a native incremental runtime.", ["source.qck.openivm.paper"]),
    ("adaptive_robust_execution", 2024, "Runtime plan adaptation for joins, parallelism and data-dependent filters", "Adaptive observations and replan decisions require a stable semantic envelope and a decision trace.", ["source.qck.photon.aqe"]),
    ("arrow_device_abi", 2025, "Cross-runtime Arrow device data interface", "Device memory location and synchronization events belong in buffer and kernel bindings; experimental status must block universal qualification.", ["source.qck.arrow.c_device"]),
    ("fastlanes_expression_encoding", 2025, "Composable expression encoding with segmented pages and compressed execution", "Encoding can be an expression graph; compiler selection needs closure, random-access and vector-decode traits.", ["source.qck.fastlanes.expression"]),
    ("verifiable_rewrite_language", 2026, "Extensible language for portable and verifiable query rewrite rules", "Rewrite definitions should be data with explicit matching, transformation and proof scope rather than engine-private code branches.", ["source.qck.rulescript.paper"]),
]


INNOVATIONS = [
    {
        "innovation_id": f"innovation.qck.{iid}", "edition": EDITION, "status": "evidence_backed_candidate",
        "name": claim, "year": year, "claim": claim, "impact_on_metamodel": impact,
        "non_llm": True, "evidence_refs": evidence,
        "limitations": ["Source-scoped result; independent reproduction and provider qualification may still be required."],
        "gaps": ["Map to concrete decision points and implementation offers in a later phase."],
    }
    for iid, year, claim, impact, evidence in INNOVATION_ROWS
]


GAP_ROWS = [
    ("sql_dialect_semantics", "No complete machine-checkable equivalence map covers SQL dialects, nulls, collations, timestamps and errors.", True, "Publish editioned dialect-to-canonical semantic mappings with counterexamples."),
    ("rewrite_proof_coverage", "Most production rewrite rule sets are tested but not formally proved over their complete semantic domain.", True, "Attach formal proof, bounded proof scope or explicit unproven status to every rewrite."),
    ("cardinality_uncertainty", "Correlation, skew, stale statistics and UDFs make point cardinality estimates dangerously overconfident.", True, "Represent distributions/intervals, calibration evidence and replan thresholds."),
    ("cost_portability", "CPU-centric scalar costs do not compare memory, network, storage, GPU transfer, energy and monetary cost reliably.", True, "Define calibrated multi-resource cost vectors and dominance/selection laws."),
    ("provider_offer_truth", "Static feature matrices do not prove deployed behavior, limits or semantic fidelity.", True, "Require deployment probes, conformance receipts and expiry triggers."),
    ("udf_contract", "UDF signatures commonly omit effects, volatility, failure, parallel safety, cancellation and resource bounds.", True, "Make the full extension contract mandatory and refuse incomplete functions."),
    ("cross_target_numeric", "Parallel reductions, FMA, libm, precision and compiler flags prevent automatic cross-target bitwise identity.", True, "Bind an explicit reproducibility posture and target-qualified numerical oracle."),
    ("adaptive_equivalence", "Adaptive plan changes can alter ordering, failure timing or numerical reduction order even when relational rows match.", True, "Prove the full observable contract for every adaptive transition."),
    ("codec_selection", "No common capability vocabulary compares codecs by logical types, random access, vectorization, energy and corruption behavior.", False, "Qualify codec offers against the kernel schema and benchmark envelopes."),
    ("approximate_receipts", "Approximate results often omit algorithm edition, parameters, seed, merge history and achieved error diagnostics.", True, "Standardize approximation provenance in result receipts."),
    ("graph_semantic_bridge", "GQL, SQL/PGQ, openCypher, SPARQL and GraphBLAS cover different data and result semantics.", False, "Define explicit ACL mappings with information-loss and unsupported-feature gaps."),
    ("spatial_precision", "CRS edition, axis order, antimeridian, validity and robust-predicate behavior vary across providers.", True, "Bind CRS/geometry precision contracts and exact-refinement oracles."),
    ("federation_pushdown", "Remote dialect and snapshot differences can make pushdown observably inequivalent.", True, "Prove operator-by-operator remote equivalence for the concrete connector and deployment."),
    ("distributed_delivery", "Component-local retry or checkpoint claims do not establish end-to-end exactly-once effects.", True, "Compose source, exchange, state and sink delivery contracts with deduplication evidence."),
    ("cancellation", "Cancellation granularity, cleanup, remote propagation and partial effects are inconsistently exposed.", True, "Require cancellation-safe points and partial-effect receipts for every runtime offer."),
    ("resource_receipt", "There is no universal plan/runtime receipt for memory, I/O, network, device, energy and money consumption.", False, "Define versioned estimate and observed-resource receipt schemas."),
    ("device_abi_maturity", "Arrow C Device ABI remains experimental and target synchronization conventions are not uniformly implemented.", False, "Qualify exact implementation versions and retain copy-based fallback when legal."),
    ("kernel_conformance", "Equivalent operator support does not imply identical null, error, overflow, order or numeric behavior.", True, "Create per-kernel semantic, adversarial and cross-target conformance suites."),
]


GAPS = [
    {
        "gap_id": f"gap.qck.{gid}", "edition": EDITION, "status": "open",
        "description": description, "blocking_for_universal_compilation": blocking,
        "affected_context_refs": [], "evidence_refs": [],
        "resolution_condition": resolution,
        "prohibited_fallbacks": ["guess semantics", "dispatch by provider name", "silently weaken exactness or reproducibility"],
        "owner": "query-compute-kernel research program",
    }
    for gid, description, blocking, resolution in GAP_ROWS
]


ID = {"type": "string", "pattern": "^[a-z][a-z0-9_-]*(\\.[a-z0-9_-]+)+$"}
STRINGS = {"type": "array", "items": {"type": "string"}, "uniqueItems": True}
REFS = {"type": "array", "items": ID, "uniqueItems": True}


def object_schema(title: str, properties: dict, required: list[str]) -> dict:
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "title": title, "type": "object", "additionalProperties": False,
        "required": required, "properties": properties,
    }


SCHEMAS = {
    "context-candidate.schema.json": object_schema(
        "Query/compute/kernel bounded-context candidate",
        {
            "context_id": ID, "edition": {"type": "integer", "minimum": 1}, "status": {"const": "candidate"},
            "name": {"type": "string"}, "domain_vision": {"type": "string"}, "inside": STRINGS,
            "outside": STRINGS, "ubiquitous_terms": STRINGS, "invariants": STRINGS,
            "decision_points": STRINGS, "neighbor_context_refs": REFS, "evidence_refs": REFS, "gaps": STRINGS,
        },
        ["context_id", "edition", "status", "name", "domain_vision", "inside", "outside", "ubiquitous_terms", "invariants", "decision_points", "neighbor_context_refs", "evidence_refs", "gaps"],
    ),
    "logical-operator.schema.json": object_schema(
        "Provider-neutral logical operator",
        {
            "operator_id": ID, "edition": {"type": "integer", "minimum": 1}, "status": {"const": "candidate"},
            "family": {"enum": ["relational", "stream", "graph", "spatial", "numerical", "approximate", "encoding", "control"]},
            "name": {"type": "string"}, "semantic_owner_ref": ID, "semantics": {"type": "string"},
            "input_roles": STRINGS, "output_contract": {"type": "string"}, "parameter_contracts": STRINGS,
            "collection_semantics": STRINGS, "null_missing_nan_semantics": STRINGS, "time_semantics": STRINGS,
            "exactness": {"enum": ["exact", "bounded_approximation", "empirical_approximation"]},
            "determinism": {"type": "string"}, "information_loss": {"type": "string"}, "laws": STRINGS,
            "failure_modes": STRINGS, "legal_decompositions": REFS, "evidence_refs": REFS, "gaps": STRINGS,
        },
        ["operator_id", "edition", "status", "family", "name", "semantic_owner_ref", "semantics", "input_roles", "output_contract", "parameter_contracts", "collection_semantics", "null_missing_nan_semantics", "time_semantics", "exactness", "determinism", "information_loss", "laws", "failure_modes", "legal_decompositions", "evidence_refs", "gaps"],
    ),
    "kernel-contract.schema.json": object_schema(
        "Executable kernel contract",
        {
            "kernel_id": ID, "edition": {"type": "integer", "minimum": 1}, "status": {"const": "candidate"},
            "operation_refs": REFS, "algorithm_family": {"type": "string"},
            "kernel_role": {"enum": ["expression", "vector", "relational", "approximate", "distributed", "stream", "external_memory", "graph", "spatial", "numerical", "codec", "runtime_primitive"]},
            "supported_type_contracts": STRINGS, "supported_layouts": STRINGS, "state_contract": {"type": "string"},
            "exactness": {"enum": ["exact", "bounded_approximation", "empirical_approximation"]},
            "determinism_posture": {"type": "string"}, "numeric_posture": {"type": "string"},
            "error_model": {"type": "string"}, "information_loss": {"type": "string"},
            "ordering_behavior": {"type": "string"}, "memory_contract": {"type": "string"},
            "complexity_contract": {"type": "string"}, "parallelism_contract": {"type": "string"},
            "supported_target_classes": STRINGS, "side_effects": STRINGS, "cancellation_contract": {"type": "string"},
            "failure_modes": STRINGS, "fallback_law": {"type": "string"}, "evidence_refs": REFS, "gaps": STRINGS,
        },
        ["kernel_id", "edition", "status", "operation_refs", "algorithm_family", "kernel_role", "supported_type_contracts", "supported_layouts", "state_contract", "exactness", "determinism_posture", "numeric_posture", "error_model", "information_loss", "ordering_behavior", "memory_contract", "complexity_contract", "parallelism_contract", "supported_target_classes", "side_effects", "cancellation_contract", "failure_modes", "fallback_law", "evidence_refs", "gaps"],
    ),
    "provider-capability.schema.json": object_schema(
        "Provider capability class",
        {
            "provider_capability_id": ID, "edition": {"type": "integer", "minimum": 1}, "status": {"const": "capability_class"},
            "name": {"type": "string"}, "context_refs": REFS, "offered_capabilities": STRINGS,
            "semantic_contract_refs": REFS, "operation_refs": REFS, "kernel_refs": REFS,
            "supported_target_classes": STRINGS, "guarantees": STRINGS, "limits": STRINGS,
            "configuration_decisions": STRINGS, "conformance_requirements": STRINGS, "evidence_refs": REFS,
            "invalidation_triggers": STRINGS, "gaps": STRINGS,
        },
        ["provider_capability_id", "edition", "status", "name", "context_refs", "offered_capabilities", "semantic_contract_refs", "operation_refs", "kernel_refs", "supported_target_classes", "guarantees", "limits", "configuration_decisions", "conformance_requirements", "evidence_refs", "invalidation_triggers", "gaps"],
    ),
    "target-profile.schema.json": object_schema(
        "Target capability profile",
        {
            "target_profile_id": ID, "edition": {"type": "integer", "minimum": 1}, "status": {"const": "target_class"},
            "name": {"type": "string"}, "target_kind": {"type": "string"}, "required_interfaces": STRINGS,
            "memory_spaces": STRINGS, "resource_dimensions": STRINGS, "supported_layouts": STRINGS,
            "numeric_traits": STRINGS, "parallel_traits": STRINGS, "transfer_traits": STRINGS,
            "isolation_traits": STRINGS, "cancellation_traits": STRINGS, "qualification_requirements": STRINGS,
            "evidence_refs": REFS, "gaps": STRINGS,
        },
        ["target_profile_id", "edition", "status", "name", "target_kind", "required_interfaces", "memory_spaces", "resource_dimensions", "supported_layouts", "numeric_traits", "parallel_traits", "transfer_traits", "isolation_traits", "cancellation_traits", "qualification_requirements", "evidence_refs", "gaps"],
    ),
    "compiler-mapping.schema.json": object_schema(
        "Compiler requirement/offer mapping pattern",
        {
            "mapping_id": ID, "edition": {"type": "integer", "minimum": 1}, "status": {"const": "candidate"},
            "subject_ref": ID, "binding_phase": {"const": "physical_binding"}, "required_guarantees": STRINGS,
            "required_offer_fields": STRINGS, "selection_laws": STRINGS, "fallback_law": {"type": "string"},
            "refusal_conditions": STRINGS, "required_receipts": STRINGS, "evidence_refs": REFS, "gaps": STRINGS,
        },
        ["mapping_id", "edition", "status", "subject_ref", "binding_phase", "required_guarantees", "required_offer_fields", "selection_laws", "fallback_law", "refusal_conditions", "required_receipts", "evidence_refs", "gaps"],
    ),
    "source.schema.json": object_schema(
        "Primary evidence source",
        {
            "source_id": ID, "edition": {"type": "integer", "minimum": 1}, "status": {"const": "reviewed"},
            "title": {"type": "string"}, "publisher": {"type": "string"},
            "source_kind": {"enum": ["standard", "official_spec", "official_docs", "official_implementation", "paper"]},
            "url": {"type": "string", "format": "uri"}, "publication_year": {"type": "integer", "minimum": 1900, "maximum": 2026},
            "accessed_at": {"type": "string", "format": "date"}, "supports_topics": STRINGS,
            "authority_scope": {"type": "string"}, "limitations": STRINGS,
        },
        ["source_id", "edition", "status", "title", "publisher", "source_kind", "url", "publication_year", "accessed_at", "supports_topics", "authority_scope", "limitations"],
    ),
    "innovation.schema.json": object_schema(
        "Non-LLM innovation record",
        {
            "innovation_id": ID, "edition": {"type": "integer", "minimum": 1}, "status": {"const": "evidence_backed_candidate"},
            "name": {"type": "string"}, "year": {"type": "integer", "minimum": 2021, "maximum": 2026},
            "claim": {"type": "string"}, "impact_on_metamodel": {"type": "string"}, "non_llm": {"const": True},
            "evidence_refs": REFS, "limitations": STRINGS, "gaps": STRINGS,
        },
        ["innovation_id", "edition", "status", "name", "year", "claim", "impact_on_metamodel", "non_llm", "evidence_refs", "limitations", "gaps"],
    ),
    "gap.schema.json": object_schema(
        "Query/compute/kernel research gap",
        {
            "gap_id": ID, "edition": {"type": "integer", "minimum": 1}, "status": {"const": "open"},
            "description": {"type": "string"}, "blocking_for_universal_compilation": {"type": "boolean"},
            "affected_context_refs": REFS, "evidence_refs": REFS, "resolution_condition": {"type": "string"},
            "prohibited_fallbacks": STRINGS, "owner": {"type": "string"},
        },
        ["gap_id", "edition", "status", "description", "blocking_for_universal_compilation", "affected_context_refs", "evidence_refs", "resolution_condition", "prohibited_fallbacks", "owner"],
    ),
}


def main() -> None:
    SCHEMA.mkdir(parents=True, exist_ok=True)
    dump_json(ROOT / "metamodel.json", METAMODEL)
    for filename, schema in SCHEMAS.items():
        dump_json(SCHEMA / filename, schema)
    dump_jsonl(ROOT / "sources.jsonl", SOURCES)
    dump_jsonl(ROOT / "context-candidates.jsonl", CONTEXTS)
    dump_jsonl(ROOT / "logical-operators.jsonl", LOGICAL_OPERATORS)
    dump_jsonl(ROOT / "kernel-contracts.jsonl", KERNELS)
    dump_jsonl(ROOT / "provider-capabilities.jsonl", PROVIDERS)
    dump_jsonl(ROOT / "target-profiles.jsonl", TARGETS)
    dump_jsonl(ROOT / "compiler-mappings.jsonl", MAPPINGS)
    dump_jsonl(ROOT / "library-boundaries.jsonl", LIBRARIES)
    dump_jsonl(ROOT / "innovations.jsonl", INNOVATIONS)
    dump_jsonl(ROOT / "gaps.jsonl", GAPS)
    manifest = {
        "corpus_id": "san.query-compute-kernel-universe", "edition": EDITION,
        "generated_at": ACCESSED, "completion_claim": False,
        "counts": {
            "sources": len(SOURCES), "context_candidates": len(CONTEXTS),
            "logical_operators": len(LOGICAL_OPERATORS), "kernel_contracts": len(KERNELS),
            "provider_capability_classes": len(PROVIDERS), "target_profiles": len(TARGETS),
            "compiler_mapping_patterns": len(MAPPINGS), "library_boundaries": len(LIBRARIES),
            "innovations_2021_2026": len(INNOVATIONS), "open_gaps": len(GAPS),
        },
        "coverage_claim": "Research seed with explicit gaps; not universal completeness or provider qualification.",
        "forbidden_core_dependencies": METAMODEL["forbidden_core_dependencies"],
    }
    dump_json(ROOT / "manifest.json", manifest)


if __name__ == "__main__":
    main()
