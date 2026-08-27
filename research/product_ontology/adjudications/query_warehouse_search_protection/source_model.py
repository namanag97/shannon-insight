#!/usr/bin/env python3
"""Canonical source for query, warehouse, virtual access, search and protection boundaries."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "source.json"
AXES = ["user", "job", "adoption", "semantics", "authority", "lifecycle", "operation", "economics", "interface", "market_evidence"]


def ev(ident: str, title: str, publisher: str, uri: str, claim: str, limit: str) -> dict[str, Any]:
    return {"source_id": ident, "source_class": "official_specification_or_documentation", "title": title, "publisher": publisher, "uri": uri, "retrieved_at": "2026-08-26", "claim": claim, "scope_limit": limit}


def art(ident: str, kind: str, name: str, definition: str, refs: list[str], owner: str | None = None, adoption: bool = False, operated: bool = False) -> dict[str, Any]:
    return {"artifact_id": ident, "kind": kind, "name": name, "status": "candidate", "semantic_owner_ref": owner, "adoption_unit": adoption, "operated": operated, "definition": definition, "evidence_refs": refs}


def split(scores: list[int], refs: list[str], label: str) -> dict[str, Any]:
    return {axis: {"score": score, "finding": f"{label}: the {axis} boundary is independently evidenced only to this scoped degree.", "evidence_refs": refs} for axis, score in zip(AXES, scores, strict=True)}


def camel(value: str) -> str:
    return "".join(part.capitalize() for part in value.replace("-", "_").split("_"))


SOURCES = [
    ("substrait.spec", "Substrait Specification", "Substrait", "https://substrait.io/spec/specification/", "Defines typed functions, relations and serialized query plans.", "Pre-1.0 sections and implementation coverage remain incomplete."),
    ("substrait.relations", "Substrait Logical Relations", "Substrait", "https://substrait.io/relations/logical_relations/", "Defines read, filter, project, join and residual-bearing logical relations.", "A portable plan is not execution or behavioral equivalence."),
    ("calcite.algebra", "Apache Calcite Algebra", "Apache Calcite", "https://calcite.apache.org/docs/algebra.html", "Defines relational operators, rewrite rules, traits and cost planning.", "A planner library is not an operated query product."),
    ("calcite.adapters", "Apache Calcite Adapters", "Apache Calcite", "https://calcite.apache.org/docs/adapter.html", "Defines adapters, calling conventions, pushdown and local fallback.", "Adapter presence does not prove faithful translation or source consistency."),
    ("trino.concepts", "Trino Concepts", "Trino", "https://trino.io/docs/current/overview/concepts.html", "Separates coordinator, workers, connectors, stages, tasks and operators.", "Project documentation does not qualify a deployment or provider."),
    ("trino.connectors", "Trino Connector API", "Trino", "https://trino.io/docs/current/develop/connectors.html", "Defines capability negotiation and partial pushdown contracts.", "Connector support is source-, edition- and operation-specific."),
    ("trino.pushdown", "Trino Pushdown", "Trino", "https://trino.io/docs/current/optimizer/pushdown.html", "Documents connector-specific pushdown and remaining local work.", "Attempted pushdown is not proof that an operation was pushed."),
    ("trino.postgres", "Trino PostgreSQL Connector", "Trino", "https://trino.io/docs/current/connector/postgresql.html", "Documents correctness-driven refusal of unsafe textual range pushdown.", "One connector's decisions are not universal federation semantics."),
    ("trino.resource_groups", "Trino Resource Groups", "Trino", "https://trino.io/docs/current/admin/resource-groups.html", "Defines queues, concurrency, memory and CPU policies.", "Configured policy is not a resource or completion receipt."),
    ("trino.resource_props", "Trino Resource Management Properties", "Trino", "https://trino.io/docs/current/admin/properties-resource-management.html", "Defines per-query CPU and memory limits.", "A limit declaration does not prove enforcement under every failure."),
    ("postgres.fdw", "PostgreSQL Foreign Data Wrapper", "PostgreSQL", "https://www.postgresql.org/docs/17/postgres-fdw.html", "Defines access to remote tables and remote planning boundaries.", "Cross-source access does not imply one atomic source cut."),
    ("drill.architecture", "Apache Drill Architecture", "Apache Drill", "https://drill.apache.org/docs/architecture-introduction/", "Defines distributed query over heterogeneous sources and storage plugins.", "Architecture documentation is not provider qualification."),
    ("drill.plans", "Apache Drill Query Plans", "Apache Drill", "https://drill.apache.org/docs/query-plans/", "Separates logical, physical and execution plans.", "A plan is not an execution occurrence or result."),
    ("drill.information_schema", "Drill Information Schema", "Apache Drill", "https://drill.apache.org/docs/querying-the-information-schema/", "Defines metadata discovery across source plugins.", "Discovered metadata can be stale, partial or authority-limited."),
    ("arrow.flight_sql", "Arrow Flight SQL", "Apache Arrow", "https://arrow.apache.org/docs/format/FlightSql.html", "Defines SQL metadata, prepared queries and result streams.", "Protocol compatibility is not query-semantic equivalence."),
    ("arrow.flight", "Arrow Flight", "Apache Arrow", "https://arrow.apache.org/docs/format/Flight.html", "Defines high-throughput data-service streams and cancellation.", "Transport completion is not analytical completeness."),
    ("arrow.adbc", "Arrow Database Connectivity", "Apache Arrow", "https://arrow.apache.org/adbc/", "Defines an Arrow-native cross-language database API.", "API standardization does not qualify a driver."),
    ("arrow.adbc_spec", "ADBC Specification", "Apache Arrow", "https://arrow.apache.org/adbc/15/format/specification.html", "Defines cancellation, partitioned results and bulk ingestion.", "An editioned API is not source authority or transaction equivalence."),
    ("duckdb.clients", "DuckDB Client APIs", "DuckDB", "https://duckdb.org/docs/stable/clients/overview", "Documents an in-process analytical query engine and library interfaces.", "A reusable engine component is not necessarily an operated product."),
    ("bigquery.admin", "BigQuery Administration", "Google Cloud", "https://docs.cloud.google.com/bigquery/docs/admin-intro", "Defines jobs, slots and workload administration.", "Managed-service claims are provider-specific and unqualified here."),
    ("bigquery.reservations", "BigQuery Reservations", "Google Cloud", "https://docs.cloud.google.com/bigquery/docs/reservations-tasks", "Defines capacity reservations, assignments and autoscaling.", "Reservation configuration is not performance or cost proof."),
    ("bigquery.export", "Export BigQuery Data", "Google Cloud", "https://docs.cloud.google.com/bigquery/docs/exporting-data", "Documents export formats, locations and limits.", "Exported rows do not automatically preserve every semantic or control artifact."),
    ("snowflake.warehouse", "Snowflake Warehouses", "Snowflake", "https://docs.snowflake.com/en/user-guide/warehouses-overview", "Defines independently managed compute, queuing, suspension and scaling.", "A branded warehouse does not own catalog, storage or business semantics."),
    ("snowflake.considerations", "Snowflake Warehouse Considerations", "Snowflake", "https://docs.snowflake.com/en/user-guide/warehouses-considerations", "Documents cost, size, cache and performance tradeoffs.", "Provider guidance is not a portable capacity oracle."),
    ("redshift.workgroup", "Redshift Workgroups and Namespaces", "Amazon Web Services", "https://docs.aws.amazon.com/redshift/latest/mgmt/serverless-workgroup-namespace.html", "Separates compute workgroups from storage/security namespaces.", "One provider decomposition is evidence, not canonical ownership."),
    ("redshift.unload", "Redshift UNLOAD", "Amazon Web Services", "https://docs.aws.amazon.com/redshift/latest/dg/r_UNLOAD.html", "Defines governed export to portable tabular formats and manifests.", "Export does not prove full service exit or semantic portability."),
    ("denodo.views", "Querying Virtual Views", "Denodo", "https://community.denodo.com/docs/html/browse/9.5/en/vdp/administration/creating_derived_views/querying_views/querying_views", "Defines virtual views with cache use, bypass and invalidation behavior.", "Product documentation does not qualify its implementation."),
    ("denodo.cache", "Denodo Cache Module", "Denodo", "https://community.denodo.com/docs/html/browse/latest/en/vdp/administration/cache_module/cache_module", "Separates virtual source access from optional materialization.", "Cache modes do not change source truth authority."),
    ("denodo.summary", "Denodo Summary Rewrite", "Denodo", "https://community.denodo.com/docs/html/document/denodoconnects/9.1/en/vdp/administration/optimizing_queries/summary_views/summary_rewrite_optimization/summary_rewrite_optimization", "Documents rewriting virtual queries to summaries.", "Rewrite eligibility does not prove equivalence without scoped laws."),
    ("pinot.concepts", "Apache Pinot Concepts", "Apache Pinot", "https://docs.pinot.apache.org/basics/concepts", "Defines distributed OLAP serving for low-latency high-concurrency workloads.", "Latency and concurrency are workload profiles, not product identity."),
    ("pinot.table", "Apache Pinot Table", "Apache Pinot", "https://docs.pinot.apache.org/basics/concepts/components/table", "Defines offline, realtime and hybrid tables over segments.", "Ingestion mode does not create a separate analytics product."),
    ("pinot.indexing", "Apache Pinot Indexing", "Apache Pinot", "https://docs.pinot.apache.org/indexing", "Documents multiple index families including vector indexes.", "An index is a retrieval mechanism, not a feature store or model."),
    ("druid.architecture", "Apache Druid Architecture", "Apache Druid", "https://druid.apache.org/docs/latest/design/architecture/", "Separates query, data, coordination and deep-storage services.", "A distributed component topology does not define product boundaries alone."),
    ("druid.query", "Apache Druid Query Processing", "Apache Druid", "https://druid.apache.org/docs/latest/querying/query-processing/", "Documents segment pruning and indexed query processing.", "Provider behavior remains configuration- and data-dependent."),
    ("materialize.serve", "Materialize Serving Results", "Materialize", "https://materialize.com/docs/serve-results/", "Defines indexed views, SELECT and change subscriptions.", "Maintained results are not automatically source-authoritative."),
    ("materialize.index", "Materialize CREATE INDEX", "Materialize", "https://materialize.com/docs/sql/create-index/", "Defines incrementally maintained indexes scoped to a cluster.", "Index presence does not prove visibility or freshness for a consumer."),
    ("lucene.overview", "Apache Lucene Core", "Apache Lucene", "https://lucene.apache.org/core/9_9_1/core/index.html", "Defines reusable index writer, reader and searcher libraries.", "A search library is a component rather than an operated product."),
    ("opensearch.analyzers", "OpenSearch Analyzers", "OpenSearch", "https://docs.opensearch.org/latest/analyzers/", "Defines index- and query-time text analysis chains.", "Analyzer equality does not ensure ranking equivalence across editions."),
    ("opensearch.vector", "OpenSearch k-NN Vector", "OpenSearch", "https://docs.opensearch.org/latest/mappings/supported-field-types/knn-vector/", "Defines vector index fields, metrics, methods and compression.", "Vector retrieval is not inherently AI, a feature platform or a decision."),
    ("opensearch.relevance", "OpenSearch Relevance", "OpenSearch", "https://docs.opensearch.org/latest/search-plugins/search-relevance/index/", "Defines relevance evaluation and ranking workflows.", "Evaluation evidence is scoped and does not authorize downstream action."),
    ("elastic.refresh", "Elasticsearch Refresh", "Elastic", "https://www.elastic.co/docs/reference/elasticsearch/rest-apis/refresh-parameter", "Defines when indexed changes become visible to search.", "Mutation acknowledgement and search visibility are different facts."),
    ("vespa.nearest", "Vespa Nearest Neighbor Search", "Vespa", "https://docs.vespa.ai/en/querying/nearest-neighbor-search", "Defines typed tensor distance and hybrid lexical-vector ranking.", "A retrieval score is not calibrated probability or business relevance."),
    ("rfc9111", "HTTP Caching", "IETF", "https://www.rfc-editor.org/rfc/rfc9111.html", "Defines cache freshness, validation and stale-response rules.", "HTTP cache semantics do not cover every analytical cache."),
    ("redis.client_cache", "Redis Client-Side Caching", "Redis", "https://redis.io/docs/latest/develop/reference/client-side-caching/", "Documents invalidation, TTL, disconnect flushing and races.", "Implementation guidance does not establish source truth."),
    ("redis.cache_aside", "Redis Cache-Aside", "Redis", "https://redis.io/docs/latest/develop/use-cases/cache-aside/", "Documents source-authoritative reads, TTLs and invalidation tradeoffs.", "A cache hit does not prove currentness."),
    ("nist.contingency", "NIST SP 800-34 Rev.1", "NIST", "https://csrc.nist.gov/pubs/sp/800/34/r1/upd1/final", "Defines impact analysis, recovery strategies, testing and maintenance.", "A framework does not prove any backup recoverable."),
    ("velero.overview", "Velero Overview", "Velero", "https://velero.io/docs/main/", "Defines Kubernetes backup, restore and migration workflows.", "A tool operation does not prove application-consistent recovery."),
    ("velero.fsb", "Velero File System Backup", "Velero", "https://velero.io/docs/main/file-system-backup", "Separates snapshots from file backup and documents limitations.", "Mechanism support is provider- and workload-specific."),
    ("velero.restore", "Velero Restore Reference", "Velero", "https://velero.io/docs/main/restore-reference/", "Defines restore lifecycle and validation behavior.", "Restore completion is not service recovery acceptance."),
    ("pgbackrest", "pgBackRest User Guide", "pgBackRest", "https://pgbackrest.org/user-guide.html", "Defines full, differential and incremental backup chains, WAL and restore verification.", "PostgreSQL-specific mechanics do not establish universal recovery semantics."),
    ("k8s.snapshots", "Kubernetes Volume Snapshots", "Kubernetes", "https://kubernetes.io/docs/concepts/storage/volume-snapshots/", "Defines persistent-volume snapshot resources and provider integration.", "A snapshot is a mechanism and not independent backup proof."),
    ("iso.oais", "ISO 14721:2025 OAIS", "ISO", "https://www.iso.org/standard/87471.html", "Defines an archive serving a designated community through ingest, preservation and access.", "A reference model does not qualify an archive implementation."),
    ("premis.v3", "PREMIS Data Dictionary 3.0", "Library of Congress", "https://www.loc.gov/standards/premis/v3/index.html", "Defines preservation Objects, Events, Rights and Agents.", "Metadata presence does not prove authenticity or preservation success."),
    ("nara.metadata", "NARA Metadata Guidance", "National Archives", "https://www.archives.gov/records-mgmt/policy/metadata-compiled", "Defines metadata requirements for transferred records.", "Requirements depend on transfer and records authority."),
    ("nara.transfer", "NARA Transfer Guidance", "National Archives", "https://www.archives.gov/records-mgmt/policy/transfer-guidance.html", "Defines accepted formats, metadata and transfer expectations.", "Jurisdiction-specific guidance is not universal records authority."),
    ("loc.sustainability", "Sustainability of Digital Formats", "Library of Congress", "https://www.loc.gov/preservation/digital/formats/sustain/sustain.shtml", "Defines disclosure, adoption, dependencies and protection factors for formats.", "Format factors require local community and risk decisions."),
    ("s3.object_lock", "Amazon S3 Object Lock", "Amazon Web Services", "https://docs.aws.amazon.com/AmazonS3/latest/userguide/object-lock.html", "Defines WORM retention periods and legal holds.", "Immutable storage is not a complete preservation archive."),
]


PRODUCTS = {
    "query": ("product.query_execution_service", "Analytical Query Execution Service", "Accepts typed analytical queries, plans and executes them under finite budgets, and returns result and execution receipts.", ["evidence.trino.concepts", "evidence.arrow.flight_sql"]),
    "warehouse": ("product.managed_warehouse_experience", "Managed Analytical Warehouse Experience", "Operated analytical compute environments, workload classes, capacity controls and governed exit for warehouse users.", ["evidence.bigquery.admin", "evidence.snowflake.warehouse", "evidence.redshift.workgroup"]),
    "virtual": ("product.virtual_data_access", "Virtual Data Access", "Owns virtual-relation identity, source bindings, lifecycle, materialization policy and access receipts across sources.", ["evidence.denodo.views", "evidence.denodo.cache", "evidence.postgres.fdw"]),
    "search": ("product.search_index_service", "Search and Index Serving", "Owns index schemas, mutation generations, visibility cuts, retrieval, ranking profiles and search evidence.", ["evidence.lucene.overview", "evidence.opensearch.analyzers", "evidence.elastic.refresh"]),
    "recovery": ("product.data_protection_recovery", "Data Protection and Recovery", "Owns protection scopes, consistency cuts, backup chains, restore plans, tested recovery objectives and acceptance evidence.", ["evidence.nist.contingency", "evidence.pgbackrest", "evidence.velero.restore"]),
    "archive": ("product.digital_preservation_archive", "Digital Preservation Archive", "Preserves information packages for a designated community with fixity, representation, custody, access and disposition evidence.", ["evidence.iso.oais", "evidence.premis.v3", "evidence.loc.sustainability"]),
}


# suffix, product key, semantic name, operation, decision, invariant, refusal, evidence, concrete mappings, optional typed gap
LIBRARY_SPECS = [
    ("query.syntax", "query", "Query syntax", "parse_query", "language_edition", "syntax_tree_preserves_declared_text_meaning", "syntax_invalid", ["substrait.spec"], ["library.qck.query-syntax"], None),
    ("query.binding", "query", "Query binding", "bind_query", "name_resolution", "every_reference_binds_to_an_exact_edition", "ambiguous_name", ["substrait.spec"], ["library.qck.query-binding"], None),
    ("query.types", "query", "Query type system", "type_query", "coercion_policy", "nullability_and_overflow_are_explicit", "type_mismatch", ["substrait.spec"], ["library.qck.query-types"], None),
    ("query.functions", "query", "Query function contract", "resolve_function", "function_edition", "function_identity_includes_edition_and_options", "function_unsupported", ["substrait.spec"], ["library.qck.function-contracts"], None),
    ("query.logical_plan", "query", "Logical query plan", "lower_logical_plan", "logical_lowering", "logical_plan_is_not_physical_plan", "relation_unsupported", ["substrait.relations"], ["library.qck.logical-plan-ir"], None),
    ("query.relational_semantics", "query", "Relational semantics", "evaluate_relation", "null_and_bag_semantics", "order_is_absent_unless_declared", "semantics_unsupported", ["calcite.algebra"], ["library.qck.relational-semantics"], None),
    ("query.rewrite", "query", "Query rewrite proof", "rewrite_query", "equivalence_oracle", "rewrite_requires_scoped_equivalence_evidence", "equivalence_unproved", ["calcite.algebra"], ["library.qck.rewrite-contracts", "library.qck.query-equivalence-oracles"], None),
    ("query.statistics", "query", "Query statistics", "estimate_cardinality", "unknown_statistics_policy", "estimate_is_not_observed_cardinality", "statistics_insufficient", ["calcite.algebra"], ["library.qck.statistics-properties", "library.qck.cardinality-estimation"], None),
    ("query.cost_search", "query", "Costed plan search", "search_plans", "objective_and_budget", "selected_plan_is_relative_to_declared_search_space", "search_budget_exhausted", ["calcite.algebra"], ["library.qck.cost-plan-search"], None),
    ("query.physical_plan", "query", "Physical query plan", "lower_physical_plan", "target_capabilities", "physical_operators_bind_exact_targets", "target_unsupported", ["drill.plans"], ["library.qck.physical-lowering"], None),
    ("query.execution_runtime", "query", "Query execution occurrence", "execute_plan", "scheduler_and_spill", "attempt_identity_differs_from_plan_identity", "execution_incomplete", ["trino.concepts"], ["library.qck.memory-runtime", "library.qck.spill-runtime", "library.qck.exchange-runtime", "library.qck.execution-scheduler", "library.qck.target-backends"], None),
    ("query.resource_budget", "query", "Query resource budget", "admit_query", "queue_and_budget_policy", "work_starts_only_after_finite_admission", "resource_exhausted", ["trino.resource_groups"], ["library.runtime-resource.admission", "library.runtime-resource.budget-precharge", "library.runtime-resource.quota-ledger"], None),
    ("query.cancellation", "query", "Query cancellation", "cancel_query", "cancellation_deadline", "cancellation_is_a_requested_transition_not_completion", "cancellation_unknown", ["arrow.flight"], ["library.runtime-resource.deadline-cancellation"], None),
    ("query.result_stream", "query", "Query result stream", "stream_result", "partition_and_order", "stream_completion_is_explicit", "partial_stream", ["arrow.flight_sql"], ["library.cbv.result_stream"], None),
    ("query.result_contract", "query", "Query result contract", "validate_result", "schema_and_completeness", "result_shape_is_editioned", "result_contract_failed", ["arrow.flight_sql"], ["library.cbv.result_contracts"], None),
    ("query.receipt", "query", "Query execution receipt", "seal_query_receipt", "evidence_redaction", "receipt_binds_query_plan_target_cut_and_outcome", "receipt_incomplete", ["trino.concepts"], ["library.qck.query-receipts", "library.lpe.runtime-receipt-core"], None),
    ("federation.source_capability", "query", "Federated source capability", "negotiate_source", "capability_profile", "unsupported_capabilities_fail_closed", "capability_unknown", ["trino.connectors"], ["library.qck.federation-adapters", "library.persistence.federation_contract"], None),
    ("federation.type_translation", "query", "Federated type translation", "translate_type", "loss_policy", "translation_loss_is_explicit", "type_translation_unsafe", ["trino.postgres"], ["library.qck.query-types", "library.persistence.federation_contract"], None),
    ("federation.function_translation", "query", "Federated function translation", "translate_function", "remote_semantics", "function_pushdown_requires_semantic_compatibility", "function_translation_unsafe", ["trino.pushdown"], ["library.qck.function-contracts", "library.qck.federation-adapters"], None),
    ("federation.pushdown", "query", "Federated pushdown decision", "plan_pushdown", "pushdown_subset", "pushed_and_residual_operations_partition_the_plan", "pushdown_unsafe", ["trino.pushdown"], ["library.persistence.federation_contract", "library.qck.federation-adapters"], None),
    ("federation.residual", "query", "Federated residual plan", "plan_residual", "fallback_location", "untranslated_work_remains_explicit", "residual_unexecutable", ["calcite.adapters"], ["library.qck.logical-plan-ir", "library.persistence.federation_contract"], None),
    ("federation.source_cut", "query", "Federated source cut set", "close_source_cuts", "consistency_posture", "cross_source_atomicity_is_never_inferred", "cut_inconsistent", ["postgres.fdw"], ["library.persistence.federation_contract", "library.pipeline.data_cut_algebra"], None),
    ("virtual.relation", "virtual", "Virtual relation", "define_virtual_relation", "identity_and_edition", "virtual_identity_is_independent_of_source_path", "relation_identity_ambiguous", ["denodo.views"], ["library.persistence.virtual_relation_identity"], None),
    ("virtual.lifecycle", "virtual", "Virtual relation lifecycle", "transition_virtual_relation", "publication_and_retirement", "published_editions_are_immutable", "invalid_lifecycle_transition", ["denodo.views"], ["library.persistence.virtual_relation_lifecycle"], None),
    ("virtual.materialization_policy", "virtual", "Virtual materialization policy", "choose_materialization", "cache_and_summary_policy", "materialization_does_not_acquire_source_authority", "materialization_unsafe", ["denodo.cache", "denodo.summary"], ["library.persistence.materialization", "library.pipeline.materialization_publisher"], None),
    ("warehouse.environment", "warehouse", "Warehouse environment", "reconcile_environment", "compute_storage_separation", "environment_identity_is_not_provider_endpoint", "environment_unready", ["redshift.workgroup"], ["library.runtime-resource.resource-topology", "library.runtime-resource.reservation-ledger"], None),
    ("warehouse.workload_class", "warehouse", "Warehouse workload class", "classify_workload", "priority_and_concurrency", "class_policy_is_explicit_and_versioned", "workload_unclassified", ["trino.resource_groups"], ["library.runtime-resource.admission", "library.runtime-resource.quota-ledger"], None),
    ("warehouse.capacity_policy", "warehouse", "Warehouse capacity policy", "plan_capacity", "autoscale_and_cost", "capacity_changes_are_receipted", "capacity_unsatisfied", ["bigquery.reservations", "snowflake.considerations"], ["library.runtime-resource.autoscaling-control", "library.runtime-resource.scheduler-policy-spi", "library.runtime-resource.usage-accounting"], None),
    ("warehouse.exit_export", "warehouse", "Warehouse exit export", "plan_exit_export", "format_and_manifest", "exit_gaps_are_reported_not_hidden", "exit_incomplete", ["bigquery.export", "redshift.unload"], ["library.cbv.export_plan", "library.cbv.export_encoder", "library.cbv.export_delivery_port", "library.pipeline.materialization_publisher"], None),
    ("search.index_schema", "search", "Search index schema", "define_index_schema", "field_and_index_policy", "schema_edition_precedes_index_generation", "schema_invalid", ["opensearch.analyzers"], ["library.method_kernels.search_methods"], None),
    ("search.analysis_chain", "search", "Search analysis chain", "analyze_content", "index_query_analysis", "analysis_chain_is_versioned", "analysis_unsupported", ["opensearch.analyzers"], ["library.method_kernels.search_methods"], None),
    ("search.lexical_kernel", "search", "Lexical retrieval kernel", "retrieve_lexical", "similarity_profile", "score_semantics_are_profile_scoped", "kernel_unsupported", ["lucene.overview"], ["library.method_kernels.search_methods"], None),
    ("search.retrieval_ir", "search", "Search retrieval plan", "plan_retrieval", "filter_and_retrieval_order", "retrieval_plan_is_not_ranked_result", "retrieval_unplannable", ["lucene.overview"], ["library.method_kernels.search_methods"], None),
    ("search.ranking_profile", "search", "Search ranking profile", "rank_candidates", "ranking_objective", "ranking_score_is_not_probability_or_decision", "ranking_profile_unknown", ["opensearch.relevance", "vespa.nearest"], ["library.method_kernels.search_methods", "library.predictive.ranking_models"], None),
    ("search.vector_kernel", "search", "Vector retrieval kernel", "retrieve_neighbors", "distance_and_approximation", "vector_retrieval_is_not_feature_or_model_authority", "vector_contract_unsupported", ["opensearch.vector", "vespa.nearest"], ["library.method_kernels.search_methods", "library.predictive.neighbor_search"], None),
    ("search.mutation", "search", "Index mutation generation", "commit_index_mutation", "generation_and_conflict", "acknowledged_mutation_has_exact_generation", "mutation_conflict", ["lucene.overview"], ["library.persistence.index_mutation"], None),
    ("search.visibility_cut", "search", "Search visibility cut", "publish_visibility_cut", "refresh_policy", "mutation_acknowledgement_is_not_search_visibility", "visibility_unknown", ["elastic.refresh"], ["library.persistence.search_visibility"], None),
    ("search.result", "search", "Search result contract", "validate_search_result", "score_and_explanation", "result_binds_index_generation_and_ranking_profile", "result_partial", ["opensearch.relevance"], ["library.cbv.result_contracts", "library.method_kernels.search_methods"], None),
    ("cache.identity_freshness", "query", "Cache identity and freshness", "evaluate_cache_entry", "key_and_freshness", "cache_identity_includes_representation_and_semantic_edition", "entry_stale", ["rfc9111"], ["library.cbv.client_cache_algebra"], None),
    ("cache.invalidation", "query", "Cache invalidation", "apply_invalidation", "disconnect_and_race_policy", "lost_invalidation_forces_safe_revalidation_or_flush", "invalidation_gap", ["redis.client_cache"], ["library.cbv.client_cache_algebra"], None),
    ("cache.eviction", "query", "Cache eviction", "choose_eviction", "capacity_and_expiry", "eviction_never_changes_source_truth", "capacity_exhausted", ["rfc9111"], ["library.cbv.client_cache_algebra"], None),
    ("cache.stampede", "query", "Cache stampede control", "coordinate_single_flight", "coalescing_and_failure", "followers_do_not_infer_leader_completion", "single_flight_unavailable", ["redis.cache_aside"], ["library.persistence.cache_fill_coordination"], None),
    ("cache.receipt", "query", "Cache decision receipt", "seal_cache_receipt", "provenance_and_age", "hit_miss_revalidation_and_staleness_are_explicit", "cache_receipt_incomplete", ["rfc9111"], ["library.cbv.client_cache_algebra", "library.lpe.runtime-receipt-core"], None),
    ("recovery.scope", "recovery", "Protection scope", "define_protection_scope", "included_and_excluded_assets", "protection_scope_is_editioned", "scope_incomplete", ["nist.contingency"], ["library.persistence.backup_manifest", "library.pipeline.recovery_planner"], None),
    ("recovery.consistency_cut", "recovery", "Recovery consistency cut", "close_consistency_cut", "quiesce_or_application_hook", "crash_consistent_is_not_application_consistent", "consistent_cut_unavailable", ["velero.fsb"], ["library.pipeline.data_cut_algebra", "library.pipeline.snapshot_handoff"], None),
    ("recovery.backup_manifest", "recovery", "Backup manifest", "seal_backup_manifest", "coverage_and_digests", "manifest_binds_exact_scope_and_objects", "manifest_incomplete", ["pgbackrest"], ["library.persistence.backup_manifest"], None),
    ("recovery.backup_chain", "recovery", "Backup chain", "validate_backup_chain", "full_differential_incremental", "every_dependency_is_reachable_and_verified", "chain_broken", ["pgbackrest"], ["library.persistence.backup_manifest"], None),
    ("recovery.objectives", "recovery", "Recovery objectives", "evaluate_recovery_objectives", "rpo_rto_measurement", "declared_rpo_rto_are_not_met_until_tested", "objective_unproved", ["nist.contingency"], ["library.persistence.recovery_objectives"], None),
    ("recovery.restore_plan", "recovery", "Restore plan", "plan_restore", "target_and_dependency_order", "restore_plan_is_safe_and_target_explicit", "restore_unplannable", ["velero.restore", "pgbackrest"], ["library.persistence.backup_manifest", "library.pipeline.recovery_planner"], None),
    ("recovery.restore_verification", "recovery", "Restore verification", "verify_restore", "integrity_and_application_checks", "restore_completion_is_not_service_acceptance", "verification_failed", ["velero.restore"], ["library.persistence.integrity", "library.persistence.backup_manifest"], None),
    ("recovery.acceptance", "recovery", "Recovery acceptance", "accept_recovery", "independent_evidence_policy", "acceptance_binds_tests_objectives_and_authority", "acceptance_refused", ["nist.contingency"], ["library.lpe.evidence-evaluation", "library.runtime-resource.runtime-receipts"], None),
    ("recovery.retention", "recovery", "Recovery-copy retention", "plan_recovery_retention", "chain_and_expiry_policy", "backup_retention_does_not_override_records_holds", "retention_conflict", ["pgbackrest"], ["library.lpe.retention-policy", "library.persistence.reachability_gc"], None),
    ("archive.package", "archive", "Archival information package", "assemble_information_package", "package_edition", "package_identity_covers_content_and_representation_information", "package_incomplete", ["iso.oais"], ["library.lpe.preservation-core"], None),
    ("archive.metadata", "archive", "Preservation metadata", "validate_preservation_metadata", "metadata_profile", "events_rights_agents_and_objects_remain_distinct", "metadata_incomplete", ["premis.v3", "nara.metadata"], ["library.lpe.preservation-core"], None),
    ("archive.fixity", "archive", "Preservation fixity evidence", "verify_fixity", "digest_and_sampling_policy", "fixity_proves_bit_consistency_not_authenticity", "fixity_failed", ["premis.v3"], ["library.lpe.digest-core", "library.lpe.preservation-core"], None),
    ("archive.format_sustainability", "archive", "Format sustainability assessment", "assess_format", "community_and_dependency_profile", "format_validity_is_not_future_renderability", "format_risk_unknown", ["loc.sustainability"], ["library.san_representation_planner", "library.lpe.preservation-core"], None),
    ("archive.preservation_action", "archive", "Preservation action", "plan_preservation_action", "migration_and_loss_policy", "every_transformation_declares_loss_and_keeps_prior_evidence", "preservation_action_unsafe", ["iso.oais", "loc.sustainability"], ["library.lpe.preservation-core", "library.san_transcode_plan", "library.san_corruption_recovery"], None),
    ("archive.custody", "archive", "Archival custody", "transfer_custody", "handoff_and_acceptance", "custody_transfer_does_not_change_ownership_by_inference", "custody_unaccepted", ["premis.v3", "nara.transfer"], ["library.lpe.custody-core"], None),
    ("archive.access_disclosure", "archive", "Archival access and disclosure", "produce_access_copy", "community_rights_and_redaction", "access_copy_is_not_preservation_master", "disclosure_refused", ["iso.oais", "nara.transfer"], ["library.lpe.disclosure-core"], None),
    ("archive.disposition", "archive", "Archival disposition", "authorize_disposition", "retention_hold_and_review", "disposition_requires_external_records_authority", "disposition_unauthorized", ["nara.metadata", "s3.object_lock"], ["library.lpe.record-lifecycle", "library.lpe.retention-policy"], None),
]


def source() -> dict[str, Any]:
    sources = [ev(f"evidence.{ident}", title, publisher, uri, claim, limit) for ident, title, publisher, uri, claim, limit in SOURCES]
    kinds = [
        {"kind": "architecture_pattern", "definition": "A reusable arrangement without independent adoption or semantic authority."},
        {"kind": "suite", "definition": "Packaging of multiple products and capabilities."},
        {"kind": "product", "definition": "An independently adopted and operated outcome promise with support and exit."},
        {"kind": "control_component", "definition": "A subsystem without its own full product promise."},
        {"kind": "capability", "definition": "A typed behavior required or offered across a boundary."},
        {"kind": "semantic_contract", "definition": "Owner of one meaning, lifecycle, invariants and refusals."},
        {"kind": "standard", "definition": "An exact external edition specializing a contract."},
        {"kind": "library_contract", "definition": "A provider-independent reusable semantic or effect-bound seam."},
        {"kind": "implementation", "definition": "An observed provider artifact that owns no canonical meaning."},
        {"kind": "neighbor", "definition": "A separate bounded context imported through an explicit contract."},
    ]
    artifacts = [
        art("pattern.analytics_serving_stack", "architecture_pattern", "Analytics serving stack", "A composition of query, warehouse, virtual access, search, cache and protection products; not one product.", ["evidence.trino.concepts", "evidence.iso.oais"]),
        art("suite.analytics_serving_products", "suite", "Analytics serving products", "Commercial or internal packaging of six independently governed products.", ["evidence.bigquery.admin", "evidence.opensearch.analyzers", "evidence.nist.contingency"]),
    ]
    for _key, (ident, name, definition, refs) in PRODUCTS.items():
        artifacts.append(art(ident, "product", name, definition, refs, adoption=True, operated=True))
    artifacts += [
        art("capability.federated_query_execution", "capability", "Federated query execution", "Capability to negotiate and execute a typed pushdown/residual split across sources.", ["evidence.trino.connectors", "evidence.calcite.adapters"]),
        art("profile.operational_analytics", "control_component", "Operational analytics workload profile", "Low-latency, high-concurrency or continuously maintained workload requirements; not a product identity.", ["evidence.pinot.concepts", "evidence.materialize.serve"]),
        art("semantic.cache_contract", "semantic_contract", "Cache contract", "Identity, freshness, validation, invalidation, eviction and evidence without source authority.", ["evidence.rfc9111", "evidence.redis.client_cache"]),
        art("component.vector_index", "control_component", "Vector index", "A search retrieval mechanism with typed distance, approximation and ranking contracts.", ["evidence.opensearch.vector", "evidence.vespa.nearest"]),
        art("pattern.backup_restore_archive", "architecture_pattern", "Backup, restore and archive umbrella", "A legacy umbrella that conflates recoverability with long-term preservation.", ["evidence.nist.contingency", "evidence.iso.oais"]),
        art("component.snapshot", "control_component", "Storage snapshot", "A point-in-time storage mechanism used by protection workflows.", ["evidence.k8s.snapshots"]),
        art("component.replication", "control_component", "Replication mechanism", "Copies state for availability or recovery but does not independently prove backup or restore.", ["evidence.nist.contingency"]),
        art("component.query_compiler", "control_component", "Query compiler and planner", "Parsing, typing, optimization and lowering components that may be embedded or independently operated.", ["evidence.calcite.algebra", "evidence.duckdb.clients"]),
        art("component.cache_provider", "control_component", "Cache storage provider", "A runtime/persistence implementation behind a cache semantic contract.", ["evidence.redis.cache_aside"]),
        art("component.optional_model_extension", "control_component", "Optional model or agent extension", "Intent-selected proposal or explanation component with no query, protection, archive or effect authority.", ["evidence.substrait.spec"]),
        art("standard.substrait", "standard", "Substrait", "Versioned portable query-plan carrier.", ["evidence.substrait.spec"]),
        art("standard.flight_sql", "standard", "Arrow Flight SQL", "Versioned SQL and result-stream protocol.", ["evidence.arrow.flight_sql"]),
        art("standard.oais", "standard", "OAIS", "Digital preservation reference model.", ["evidence.iso.oais"]),
        art("implementation.trino", "implementation", "Trino", "Observed distributed and federated query implementation; unqualified here.", ["evidence.trino.concepts", "evidence.trino.connectors"]),
        art("implementation.calcite", "implementation", "Apache Calcite", "Observed query planning and adapter library; unqualified here.", ["evidence.calcite.algebra", "evidence.calcite.adapters"]),
        art("implementation.bigquery", "implementation", "BigQuery", "Observed managed warehouse implementation; unqualified here.", ["evidence.bigquery.admin"]),
        art("implementation.denodo", "implementation", "Denodo", "Observed virtual data access implementation; unqualified here.", ["evidence.denodo.views"]),
        art("implementation.opensearch", "implementation", "OpenSearch", "Observed search and index implementation; unqualified here.", ["evidence.opensearch.analyzers", "evidence.opensearch.vector"]),
        art("implementation.pgbackrest", "implementation", "pgBackRest", "Observed PostgreSQL protection implementation; unqualified here.", ["evidence.pgbackrest"]),
        art("implementation.velero", "implementation", "Velero", "Observed Kubernetes protection implementation; unqualified here.", ["evidence.velero.overview"]),
        art("implementation.object_lock", "implementation", "S3 Object Lock", "Observed immutable-storage mechanism; not an archive product.", ["evidence.s3.object_lock"]),
        art("neighbor.source_truth", "neighbor", "Source-system truth", "Owns operational facts and transaction authority.", ["evidence.postgres.fdw"]),
        art("neighbor.catalog", "neighbor", "Catalog and metadata authority", "Owns dataset and schema discovery contracts.", ["evidence.drill.information_schema"]),
        art("neighbor.runtime_resource", "neighbor", "Runtime and resource control", "Owns compute, storage, scheduling and resource effects.", ["evidence.trino.resource_groups"]),
        art("neighbor.identity_policy", "neighbor", "Identity and policy", "Owns principals, authorization and disclosure authority.", ["evidence.nara.transfer"]),
        art("neighbor.records_authority", "neighbor", "Records authority", "Owns retention, hold and lawful disposition decisions.", ["evidence.nara.metadata"]),
        art("neighbor.model_lifecycle", "neighbor", "Model lifecycle", "Owns predictive model and ranking-model lifecycle where selected.", ["evidence.opensearch.relevance"]),
    ]

    owner_by_suffix: dict[str, str] = {}
    capability_by_suffix: dict[str, str] = {}
    for suffix, _product_key, semantic_name, operation, _decision, invariant, _refusal, source_ids, _concrete, _gap in LIBRARY_SPECS:
        safe = suffix.replace(".", "_")
        owner = f"semantic.{suffix}"
        capability = f"capability.{suffix}"
        owner_by_suffix[suffix] = owner
        capability_by_suffix[suffix] = capability
        refs = [f"evidence.{source_id}" for source_id in source_ids]
        artifacts.append(art(owner, "semantic_contract", semantic_name, f"Owns {semantic_name.lower()} identity, decisions, lifecycle, invariants and refusals.", refs))
        artifacts.append(art(capability, "capability", operation.replace("_", " ").title(), f"Typed capability to {operation.replace('_', ' ')} under the {semantic_name.lower()} contract; {invariant}.", refs, owner=owner))

    product_scores = {
        "query": ([2, 2, 2, 2, 2, 2, 2, 2, 2, 2], "strong_product_candidate"),
        "warehouse": ([2, 2, 2, 1, 1, 2, 2, 2, 1, 1], "presumptive_product"),
        "virtual": ([2, 2, 2, 2, 1, 2, 1, 1, 2, 1], "presumptive_product"),
        "search": ([2, 2, 2, 2, 2, 2, 2, 1, 2, 2], "strong_product_candidate"),
        "recovery": ([2, 2, 2, 2, 2, 2, 2, 1, 2, 2], "strong_product_candidate"),
        "archive": ([2, 2, 2, 2, 2, 2, 2, 1, 2, 2], "strong_product_candidate"),
    }
    decisions = []
    for key, (ident, name, _definition, refs) in PRODUCTS.items():
        scores, disposition = product_scores[key]
        decisions.append({"decision_id": f"decision.product.{key}", "subject_ref": ident, "disposition": disposition, "rationale": f"{name} has a distinct user job, owned lifecycle, operated promise and exit boundary; lower scores retain evidence gaps rather than fabricate certainty.", "evidence_refs": refs, "split_test": split(scores, refs, name)})
    decisions += [
        {"decision_id": "decision.federation.capability", "subject_ref": "capability.federated_query_execution", "disposition": "reclassify_as_capability", "rationale": "Pushdown and residual execution are query-engine capabilities; only a separately adopted virtual-relation lifecycle justifies a virtual-access product.", "evidence_refs": ["evidence.trino.connectors", "evidence.calcite.adapters"]},
        {"decision_id": "decision.operational.profile", "subject_ref": "profile.operational_analytics", "disposition": "reclassify_as_workload_profile", "rationale": "Latency, concurrency, batch, realtime and continuous maintenance specialize workload requirements rather than create product identities.", "evidence_refs": ["evidence.pinot.concepts", "evidence.pinot.table", "evidence.materialize.serve"]},
        {"decision_id": "decision.cache.mechanism", "subject_ref": "semantic.cache_contract", "disposition": "reclassify_as_cross_product_semantic_contract", "rationale": "Cache semantics are composed by query, virtual access, warehouse and search products; a cache provider remains a runtime/persistence neighbor.", "evidence_refs": ["evidence.rfc9111", "evidence.redis.client_cache"]},
        {"decision_id": "decision.vector.search", "subject_ref": "component.vector_index", "disposition": "retain_as_search_component", "rationale": "Vector retrieval is an index and ranking mechanism, not a feature store, model product or inherently agentic capability.", "evidence_refs": ["evidence.opensearch.vector", "evidence.vespa.nearest"]},
        {"decision_id": "decision.protection.archive_split", "subject_ref": "pattern.backup_restore_archive", "disposition": "split_into_recovery_and_preservation_products", "rationale": "Operational recoverability and designated-community preservation have different users, authorities, lifecycles, evidence and exit promises.", "evidence_refs": ["evidence.nist.contingency", "evidence.iso.oais", "evidence.premis.v3"]},
        {"decision_id": "decision.snapshot.mechanism", "subject_ref": "component.snapshot", "disposition": "retain_as_recovery_mechanism", "rationale": "A point-in-time storage snapshot is neither an independently verified backup nor a recovered service.", "evidence_refs": ["evidence.k8s.snapshots", "evidence.velero.fsb"]},
        {"decision_id": "decision.replication.mechanism", "subject_ref": "component.replication", "disposition": "retain_as_availability_or_recovery_mechanism", "rationale": "Replication can copy corruption or deletion and does not prove independent retained recovery points.", "evidence_refs": ["evidence.nist.contingency"]},
        {"decision_id": "decision.query.component_product", "subject_ref": "component.query_compiler", "disposition": "component_unless_independently_operated", "rationale": "A parser, optimizer or engine becomes a product only when adopted and operated with support, SLO, economics and exit promises.", "evidence_refs": ["evidence.calcite.algebra", "evidence.duckdb.clients", "evidence.trino.concepts"]},
        {"decision_id": "decision.agent.optional", "subject_ref": "component.optional_model_extension", "disposition": "optional_non_authoritative_extension", "rationale": "Agents and models may propose or explain only when selected by intent; removal leaves deterministic core parsing, planning, execution, authorization and evidence unchanged.", "evidence_refs": ["evidence.substrait.spec", "evidence.arrow.flight_sql"]},
    ]

    ownership = []
    libraries = []
    requirements = []
    binding_maps = []
    binding_gaps = []
    for suffix, product_key, semantic_name, operation, decision, invariant, refusal, source_ids, concrete, gap in LIBRARY_SPECS:
        safe = suffix.replace(".", "_")
        owner = owner_by_suffix[suffix]
        capability = capability_by_suffix[suffix]
        refs = [f"evidence.{source_id}" for source_id in source_ids]
        typ = camel(safe)
        ownership.append({"meaning_id": f"meaning.{suffix}", "term": semantic_name, "owner_ref": owner, "invariant": invariant, "must_not_be_owned_by": ["neighbor.source_truth", "neighbor.runtime_resource", "component.optional_model_extension"]})
        libraries.append({"library_id": f"library.{suffix}", "class": "semantic_pure" if not any(word in operation for word in ("execute", "stream", "commit", "reconcile", "cancel", "transfer", "produce")) else "runtime_boundary", "owner_ref": owner, "provides": [capability], "types": [typ, f"{typ}Decision", f"{typ}Refusal"], "operations": [operation], "decisions": [decision], "invariants": [invariant, "provider_identity_does_not_change_meaning"], "refusals": [refusal, "unsupported_capability", "resource_exhausted"], "dependencies": [], "effect_boundary": "pure_no_io" if not any(word in operation for word in ("execute", "stream", "commit", "reconcile", "cancel", "transfer", "produce")) else "effect_intents_and_receipts", "evidence_refs": refs})
        requirements.append({"requirement_id": f"requirement.{suffix}", "consumer_ref": PRODUCTS[product_key][0], "capability_ref": capability, "minimum_qualified_offers": 2, "binding_phase": "compile_time", "status": "unbound", "refusal": "refuse compilation when no exact qualified compatible offer exists"})
        gap_ref = None
        disposition = "structurally_projected_unqualified"
        if gap:
            gap_ref = gap
            disposition = "blocked_typed_gap"
            binding_gaps.append({"gap_id": gap, "abstract_library_ref": f"library.{suffix}", "reason": f"The shared compiler registry has no exact canonical {semantic_name.lower()} contract.", "resolution": "Adjudicate an exact semantic owner, Rust-neutral types, decisions, laws, refusals and two independent conformance-qualified implementations."})
        binding_maps.append({"binding_map_id": f"binding.{suffix}", "abstract_library_ref": f"library.{suffix}", "compiler_disposition": disposition, "concrete_library_refs": concrete, "gap_ref": gap_ref, "portable_offer": False})

    offers = [
        ("trino", "implementation.trino", ["capability.query.execution_runtime", "capability.federation.source_capability"], ["trino.concepts", "trino.connectors"]),
        ("calcite", "implementation.calcite", ["capability.query.logical_plan", "capability.query.rewrite", "capability.federation.pushdown"], ["calcite.algebra", "calcite.adapters"]),
        ("bigquery", "implementation.bigquery", ["capability.warehouse.environment", "capability.warehouse.capacity_policy"], ["bigquery.admin", "bigquery.reservations"]),
        ("denodo", "implementation.denodo", ["capability.virtual.relation", "capability.virtual.materialization_policy"], ["denodo.views", "denodo.cache"]),
        ("opensearch", "implementation.opensearch", ["capability.search.index_schema", "capability.search.vector_kernel"], ["opensearch.analyzers", "opensearch.vector"]),
        ("pgbackrest", "implementation.pgbackrest", ["capability.recovery.backup_manifest", "capability.recovery.restore_plan"], ["pgbackrest"]),
        ("velero", "implementation.velero", ["capability.recovery.consistency_cut", "capability.recovery.restore_verification"], ["velero.overview", "velero.restore"]),
        ("object_lock", "implementation.object_lock", ["capability.archive.disposition"], ["s3.object_lock"]),
    ]
    offer_rows = [{"offer_id": f"offer.{name}", "provider_ref": provider, "capability_refs": caps, "status": "observed_unqualified", "qualified_implementation_count": 0, "portable": False, "evidence_refs": [f"evidence.{ref}" for ref in refs]} for name, provider, caps, refs in offers]

    relations = [
        {"relation_id": "relation.pattern.packages_suite", "from_ref": "pattern.analytics_serving_stack", "predicate": "packaged_as", "to_ref": "suite.analytics_serving_products", "binding_phase": "authoring"},
        {"relation_id": "relation.query.requires_runtime", "from_ref": "product.query_execution_service", "predicate": "requires", "to_ref": "neighbor.runtime_resource", "binding_phase": "deployment_time"},
        {"relation_id": "relation.virtual.requires_query", "from_ref": "product.virtual_data_access", "predicate": "requires", "to_ref": "product.query_execution_service", "binding_phase": "compile_time"},
        {"relation_id": "relation.search.model_neighbor", "from_ref": "product.search_index_service", "predicate": "requires", "to_ref": "neighbor.model_lifecycle", "binding_phase": "compile_time"},
        {"relation_id": "relation.archive.records_authority", "from_ref": "product.digital_preservation_archive", "predicate": "governed_by", "to_ref": "neighbor.records_authority", "binding_phase": "runtime"},
        {"relation_id": "relation.recovery.runtime", "from_ref": "product.data_protection_recovery", "predicate": "requires", "to_ref": "neighbor.runtime_resource", "binding_phase": "deployment_time"},
        {"relation_id": "relation.substrait.specializes_plan", "from_ref": "standard.substrait", "predicate": "specializes", "to_ref": "semantic.query.logical_plan", "binding_phase": "compile_time"},
        {"relation_id": "relation.oais.specializes_archive", "from_ref": "standard.oais", "predicate": "specializes", "to_ref": "semantic.archive.package", "binding_phase": "authoring"},
    ]
    crosswalks = [
        {"legacy_ref": "candidate.product.distributed_query", "canonical_refs": ["product.query_execution_service"], "disposition": "rename"},
        {"legacy_ref": "candidate.product.warehouse_experience", "canonical_refs": ["product.managed_warehouse_experience"], "disposition": "rename"},
        {"legacy_ref": "candidate.product.federated_query", "canonical_refs": ["capability.federated_query_execution", "product.virtual_data_access"], "disposition": "split_capability_from_product"},
        {"legacy_ref": "candidate.product.search_index_serving", "canonical_refs": ["product.search_index_service"], "disposition": "rename"},
        {"legacy_ref": "candidate.product.vector_feature_serving", "canonical_refs": ["component.vector_index", "neighbor.model_lifecycle"], "disposition": "split"},
        {"legacy_ref": "candidate.product.backup_restore_archive", "canonical_refs": ["product.data_protection_recovery", "product.digital_preservation_archive"], "disposition": "split"},
        {"legacy_ref": "term.operational_analytics", "canonical_refs": ["profile.operational_analytics", "product.query_execution_service"], "disposition": "profile_not_product"},
        {"legacy_ref": "term.realtime_analytics", "canonical_refs": ["profile.operational_analytics"], "disposition": "profile_not_product"},
        {"legacy_ref": "term.query_cache", "canonical_refs": ["semantic.cache_contract"], "disposition": "semantic_mechanism"},
        {"legacy_ref": "term.wal_archive", "canonical_refs": ["product.data_protection_recovery"], "disposition": "recovery_log_homonym"},
        {"legacy_ref": "term.immutable_archive", "canonical_refs": ["implementation.object_lock", "product.digital_preservation_archive"], "disposition": "mechanism_not_product"},
        {"legacy_ref": "term.ai_search", "canonical_refs": ["product.search_index_service", "component.vector_index"], "disposition": "remove_ambient_ai_prefix"},
    ]

    negative_pairs = [
        ("query_text_plan", "SQL text is the logical or physical plan", "keep query text, bound query, logical plan and physical plan distinct"),
        ("plan_attempt", "a physical plan proves execution", "require an execution-attempt receipt"),
        ("query_success_complete", "query success proves complete or current results", "bind exact result cut, completion and freshness evidence"),
        ("query_success_authorized", "query success authorizes downstream effects", "require separate policy and effect authority"),
        ("rewrite_equivalence", "a rewrite is equivalent because it parses", "require scoped null, type, time, order and overflow equivalence"),
        ("estimate_observation", "estimated cardinality is observed cardinality", "retain estimate method and uncertainty"),
        ("component_product", "a query compiler library is automatically a product", "require independent adoption, operation, SLO, economics and exit"),
        ("federation_product", "federation pushdown alone is a separate product", "classify it as query capability"),
        ("federation_attempted", "attempted pushdown was performed remotely", "record exact pushed subset and residual"),
        ("federation_loss", "foreign types and functions translate losslessly by default", "refuse or record translation loss"),
        ("federation_atomic", "cross-source query implies one atomic snapshot", "declare exact per-source cuts and consistency posture"),
        ("virtual_view_query", "a saved query is a governed virtual relation", "require identity, edition, lifecycle and source bindings"),
        ("virtual_materialized_truth", "materializing a virtual relation creates source truth", "preserve source authority and provenance"),
        ("warehouse_engine", "a managed warehouse experience owns the query engine", "keep experience, engine, catalog and storage boundaries explicit"),
        ("warehouse_exit", "row export proves complete service exit", "report semantic, policy, history and control-plane exit gaps"),
        ("operational_product", "low latency or realtime creates another product", "encode a workload profile"),
        ("batch_product", "batch mode creates another analytics product", "encode an execution profile"),
        ("vector_feature", "a vector index is a feature store", "retain search retrieval and feature semantics separately"),
        ("vector_ai", "vector retrieval is inherently AI", "model distance, approximation, index and ranking contracts directly"),
        ("search_ack_visible", "index mutation acknowledgement means searchable", "require an explicit visibility cut"),
        ("search_score_probability", "retrieval score is calibrated probability", "scope score to ranking profile"),
        ("search_score_decision", "top-ranked result is an authorized decision", "require separate decision and effect authority"),
        ("index_schema_content", "index schema owns source content meaning", "import source and catalog semantics"),
        ("cache_truth", "cache is source truth", "retain primary authority and entry provenance"),
        ("cache_hit_current", "a cache hit is current", "evaluate freshness and invalidation evidence"),
        ("ttl_invalidation", "TTL proves all mutations invalidated", "keep expiry and invalidation distinct"),
        ("cache_disconnect", "client cache stays safe after invalidation disconnect", "flush or revalidate under an explicit policy"),
        ("cache_stampede", "single-flight leader completion can be inferred", "require a leader receipt or typed failure"),
        ("snapshot_backup", "a storage snapshot is a verified backup", "require independent scope, manifest, retention and restore evidence"),
        ("replication_backup", "replication is a backup", "require independent retained recovery points"),
        ("backup_restorable", "backup success proves restorable", "execute restore and verification tests"),
        ("restore_recovered", "restore completion proves recovered service", "require service-level acceptance"),
        ("rpo_rto_declared", "declared RPO and RTO are met", "measure them in scoped exercises"),
        ("backup_records_retention", "backup expiry overrides record hold", "import records authority and refuse conflict"),
        ("wal_archive", "WAL archive is a digital preservation archive", "treat it as a recovery-log homonym"),
        ("worm_archive", "WORM storage is a preservation archive", "require OAIS lifecycle, metadata, access and preservation evidence"),
        ("storage_preservation", "archival storage alone is preservation", "require active preservation lifecycle"),
        ("fixity_authenticity", "matching digest proves authenticity", "retain provenance, custody and authenticity argument separately"),
        ("valid_renderable", "format-valid data is future renderable", "assess representation dependencies and designated community"),
        ("custody_ownership", "custody transfer changes ownership", "require explicit authority"),
        ("access_master", "access copy is preservation master", "retain distinct derivatives and evidence"),
        ("archive_disposition", "archive invents retention or deletion authority", "import records authority"),
        ("provider_qualified", "official documentation qualifies an implementation", "require exact conformance receipts"),
        ("one_portable", "one implementation proves portable semantics", "require two independent qualified implementations"),
        ("agent_core", "an agent is required for query or protection core", "remove extension and preserve deterministic behavior"),
        ("agent_authority", "agent output authorizes a query, deletion, restore or disclosure", "treat output as a proposal requiring deterministic checks"),
        ("ai_prefix", "search, query, cache or archive becomes AI by branding", "model the exact deterministic or predictive capability"),
        ("predictive_ambient", "predictive ranking is automatically enabled", "require explicit intent, model edition and lifecycle binding"),
        ("agent_simulation", "an agent-based simulation entity is an LLM agent", "retain modeled entity semantics unless explicitly specialized"),
    ]
    negative_tests = [{"test_id": f"negative.{ident}", "prohibited_claim": prohibited, "expected_result": expected} for ident, prohibited, expected in negative_pairs]

    return {
        "contract_id": "contract.product_adjudication.query_warehouse_search_protection.v0_1_0",
        "edition": 1,
        "status": "evidence_backed_adjudicated_candidate_not_ratified",
        "scope": "Analytical query execution, managed warehouse experience, virtual data access, search/index serving, cache semantics, operational profiles, data protection/recovery and digital preservation archive.",
        "negative_scope": "Does not own source business facts, catalog truth, identity policy, records authority, runtime providers, predictive model lifecycle, or any ambient model/agent authority.",
        "artifact_kinds": kinds,
        "sources": sources,
        "artifacts": artifacts,
        "boundary_decisions": decisions,
        "ownership": ownership,
        "libraries": libraries,
        "requirements": requirements,
        "offers": offer_rows,
        "relations": relations,
        "crosswalks": crosswalks,
        "negative_tests": negative_tests,
        "binding_maps": binding_maps,
        "binding_gaps": binding_gaps,
        "non_collapse_laws": [
            "query text != bound query != logical plan != physical plan != execution attempt != result",
            "federation capability != virtual data access product",
            "operational, realtime and batch are workload profiles rather than product identities",
            "warehouse experience != query engine != catalog != storage != semantic metric",
            "vector index != feature platform != model != authorized decision",
            "cache != source truth; hit != current; TTL != invalidation proof",
            "snapshot != backup; replication != backup; restore != recovered service",
            "backup and recovery != digital preservation archive",
            "WAL archive != preservation archive; WORM storage != preservation lifecycle",
            "fixity != authenticity; format validity != future renderability",
            "provider documentation != qualification; one implementation != portability",
            "optional agent or model output is a proposal, never semantic or effect authority",
            "removing every optional model/agent extension leaves deterministic parsing, typing, planning, execution, authorization, qualification and evidence intact",
        ],
    }


def source_bytes() -> bytes:
    from product_enrichment import enrich

    return (json.dumps(enrich(source()), ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode()


if __name__ == "__main__":
    SOURCE.write_bytes(source_bytes())
