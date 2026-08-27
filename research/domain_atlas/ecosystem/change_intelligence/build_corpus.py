#!/usr/bin/env python3
"""Deterministically build the non-LLM change-intelligence candidate corpus.

The compact constants in this file are the review surface.  Generated JSONL is
deliberately reproducible; network collection is performed by a separate,
scheduled collector and never by this builder.
"""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ATLAS = ROOT.parents[1]
AS_OF = "2026-08-25"
EDITION = 1


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


PLANES = load_jsonl(ATLAS / "coverage-planes.jsonl")
PROOFS = json.loads((ATLAS / "compiler" / "proof-obligations.json").read_text(encoding="utf-8"))["proofs"]
PLANE_IDS = [row["plane_id"] for row in PLANES]
PROOF_IDS = [row["proof_id"] for row in PROOFS]


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_jsonl(path: Path, rows: list[dict]) -> None:
    text = "".join(json.dumps(row, sort_keys=True, separators=(",", ":")) + "\n" for row in rows)
    path.write_text(text, encoding="utf-8")


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def sid(slug: str) -> str:
    return f"source.{slug}"


def subj(slug: str) -> str:
    return f"subject.{slug}"


# Ordered to correspond to the atlas coverage-plane registry for the first 84
# entries.  Later entries add direct sources for the supplied monitoring briefs.
SOURCE_CATALOG = [
    ("json_schema_2020_12", "JSON Schema Draft 2020-12", "JSON Schema", "specification", "https://json-schema.org/draft/2020-12/json-schema-core"),
    ("un_isic_rev5", "ISIC Revision 5", "United Nations Statistics Division", "official_registry", "https://unstats.un.org/unsd/classifications/Econ/isic"),
    ("informs_analytics_framework", "INFORMS Analytics Framework", "INFORMS", "professional_standard", "https://www.informs.org/Professional-Development/INFORMS-Analytics-Framework/Explore"),
    ("iso_42010", "ISO/IEC/IEEE 42010 architecture descriptions", "ISO", "standard", "https://www.iso.org/standard/74393.html"),
    ("omg_uml_2_5_1", "UML 2.5.1 specification", "Object Management Group", "specification", "https://www.omg.org/spec/UML/2.5.1"),
    ("w3c_prov_o", "PROV-O", "W3C", "recommendation", "https://www.w3.org/TR/prov-o/"),
    ("omg_bmm_1_3", "Business Motivation Model 1.3", "Object Management Group", "specification", "https://www.omg.org/spec/BMM/1.3"),
    ("w3c_did_core", "Decentralized Identifiers Core 1.0", "W3C", "recommendation", "https://www.w3.org/TR/did-core/"),
    ("rfc3339", "Date and Time on the Internet", "IETF", "rfc", "https://www.rfc-editor.org/rfc/rfc3339"),
    ("bipm_si_9", "SI Brochure, 9th edition", "BIPM", "standard", "https://www.bipm.org/en/publications/si-brochure"),
    ("w3c_owl2", "OWL 2 Web Ontology Language", "W3C", "recommendation", "https://www.w3.org/TR/owl2-overview/"),
    ("metricflow_docs", "MetricFlow semantic models", "dbt Labs", "official_documentation", "https://docs.getdbt.com/docs/build/semantic-models"),
    ("xacml_3", "XACML 3.0", "OASIS", "standard", "https://docs.oasis-open.org/xacml/3.0/xacml-3.0-core-spec-os-en.html"),
    ("openapi_3_1", "OpenAPI Specification 3.1", "OpenAPI Initiative", "specification", "https://spec.openapis.org/oas/v3.1.0"),
    ("otel_resource_semconv", "OpenTelemetry resource semantic conventions", "OpenTelemetry", "specification", "https://opentelemetry.io/docs/specs/semconv/resource/"),
    ("debezium_releases", "Debezium releases", "Debezium", "release_feed", "https://debezium.io/releases/"),
    ("rfc9110", "HTTP Semantics", "IETF", "rfc", "https://www.rfc-editor.org/rfc/rfc9110"),
    ("arrow_format", "Apache Arrow columnar format", "Apache Arrow", "specification", "https://arrow.apache.org/docs/format/Columnar.html"),
    ("avro_spec", "Apache Avro specification", "Apache Avro", "specification", "https://avro.apache.org/docs/current/specification/"),
    ("rfc8878", "Zstandard Compression and the application/zstd media type", "IETF", "rfc", "https://www.rfc-editor.org/rfc/rfc8878"),
    ("parquet_format", "Apache Parquet format", "Apache Parquet", "specification", "https://parquet.apache.org/docs/file-format/"),
    ("arrow_c_data", "Arrow C Data Interface", "Apache Arrow", "specification", "https://arrow.apache.org/docs/format/CDataInterface.html"),
    ("ogc_geotiff", "OGC GeoTIFF standard", "Open Geospatial Consortium", "standard", "https://www.ogc.org/standard/geotiff/"),
    ("beam_model", "Apache Beam programming model", "Apache Beam", "official_documentation", "https://beam.apache.org/documentation/programming-guide/"),
    ("flink_1_20", "Apache Flink 1.20 release", "Apache Flink", "official_release", "https://flink.apache.org/2024/08/02/apache-flink-1.20.0-release-announcement/"),
    ("kafka_4_0", "Apache Kafka 4.0 release", "Apache Kafka", "official_release", "https://kafka.apache.org/blog/2025/03/18/apache-kafka-4.0.0-release-announcement"),
    ("airflow_releases", "Apache Airflow releases", "Apache Airflow", "release_feed", "https://airflow.apache.org/docs/apache-airflow/stable/release_notes.html"),
    ("aws_s3_whats_new", "Amazon S3 What's New", "Amazon Web Services", "release_feed", "https://aws.amazon.com/about-aws/whats-new/storage/?whats-new-content-all.sort-by=item.additionalFields.postDateTime"),
    ("postgres_18", "PostgreSQL 18 release notes", "PostgreSQL Global Development Group", "official_release", "https://www.postgresql.org/docs/18/release-18.html"),
    ("iceberg_v3_spec", "Apache Iceberg v3 specification", "Apache Iceberg", "specification", "https://iceberg.apache.org/spec/#version-3-analytic-data-tables"),
    ("iceberg_rest_spec", "Apache Iceberg REST catalog specification", "Apache Iceberg", "specification", "https://github.com/apache/iceberg/blob/main/open-api/rest-catalog-open-api.yaml"),
    ("lucene_10_changes", "Apache Lucene 10 changes", "Apache Lucene", "official_release", "https://lucene.apache.org/core/10_0_0/changes/Changes.html"),
    ("postgres_backup", "PostgreSQL continuous archiving and point-in-time recovery", "PostgreSQL Global Development Group", "official_documentation", "https://www.postgresql.org/docs/current/continuous-archiving.html"),
    ("delta_4_0", "Delta Lake 4.0 release", "Delta Lake", "official_release", "https://github.com/delta-io/delta/releases/tag/v4.0.0"),
    ("iso_sql_2023", "ISO/IEC 9075-1:2023 SQL framework", "ISO", "standard", "https://www.iso.org/standard/76583.html"),
    ("calcite_1_40", "Apache Calcite 1.40 release", "Apache Calcite", "official_release", "https://calcite.apache.org/news/2025/03/16/release-1.40.0/"),
    ("velox_releases", "Velox releases", "LF Projects", "release_feed", "https://github.com/facebookincubator/velox/releases"),
    ("spark_4_0", "Apache Spark 4.0.0 release", "Apache Spark", "official_release", "https://spark.apache.org/releases/spark-release-4-0-0.html"),
    ("rapids_25_08", "RAPIDS 25.08 release selector", "NVIDIA RAPIDS", "official_release", "https://docs.rapids.ai/release-selector/"),
    ("wasm_component_model", "WebAssembly Component Model", "Bytecode Alliance", "specification", "https://github.com/WebAssembly/component-model"),
    ("wasi_preview2", "WASI Preview 2", "Bytecode Alliance", "official_release", "https://bytecodealliance.org/articles/WASI-0.2"),
    ("kubernetes_dra", "Dynamic Resource Allocation", "Kubernetes", "official_documentation", "https://kubernetes.io/docs/concepts/scheduling-eviction/dynamic-resource-allocation/"),
    ("cloudevents_1_0", "CloudEvents 1.0 specification", "CNCF", "specification", "https://github.com/cloudevents/spec/blob/v1.0.2/cloudevents/spec.md"),
    ("kubernetes_etcd_restore", "Operating etcd clusters for Kubernetes", "Kubernetes", "official_documentation", "https://kubernetes.io/docs/tasks/administer-cluster/configure-upgrade-etcd/"),
    ("otel_spec", "OpenTelemetry specification", "OpenTelemetry", "specification", "https://opentelemetry.io/docs/specs/otel/"),
    ("finops_focus_1_2", "FOCUS 1.2 specification", "FinOps Foundation", "specification", "https://focus.finops.org/focus-specification/"),
    ("substrait_functions", "Substrait function specification", "Substrait", "specification", "https://substrait.io/extensions/"),
    ("dbt_1_11_14", "dbt-core 1.11.14", "dbt Labs", "official_release", "https://github.com/dbt-labs/dbt-core/releases/tag/v1.11.14"),
    ("iso_8000_61", "ISO 8000-61 data quality management", "ISO", "standard", "https://www.iso.org/standard/63086.html"),
    ("great_expectations_releases", "Great Expectations releases", "Great Expectations", "release_feed", "https://github.com/great-expectations/great_expectations/releases"),
    ("openlineage_spec", "OpenLineage specification", "OpenLineage", "specification", "https://openlineage.io/docs/spec/"),
    ("informs_certification", "INFORMS Certified Analytics Professional", "INFORMS", "professional_standard", "https://www.certifiedanalytics.org/"),
    ("scipy_1_15", "SciPy 1.15.0 release notes", "SciPy", "official_release", "https://docs.scipy.org/doc/scipy/release/1.15.0-notes.html"),
    ("ortools_9_12", "OR-Tools 9.12 release", "Google OR-Tools", "official_release", "https://github.com/google/or-tools/releases/tag/v9.12"),
    ("dowhy_0_13", "DoWhy 0.13 release", "PyWhy", "official_release", "https://github.com/py-why/dowhy/releases/tag/v0.13"),
    ("statsmodels_0_14_4", "statsmodels 0.14.4 release", "statsmodels", "official_release", "https://www.statsmodels.org/stable/release/version0.14.4.html"),
    ("ocel_2", "OCEL 2.0 specification", "OCEL standard authors", "specification", "https://www.ocel-standard.org/2.0/ocel20_specification.pdf"),
    ("ogc_api_features", "OGC API Features", "Open Geospatial Consortium", "standard", "https://www.ogc.org/standard/ogcapi-features/"),
    ("mlflow_3", "MLflow 3.0 release", "MLflow", "official_release", "https://mlflow.org/releases/3.0.0"),
    ("openfeature_spec", "OpenFeature specification", "OpenFeature", "specification", "https://openfeature.dev/specification/"),
    ("opa_releases", "Open Policy Agent releases", "Open Policy Agent", "release_feed", "https://github.com/open-policy-agent/opa/releases"),
    ("nist_privacy_framework", "NIST Privacy Framework", "NIST", "government_standard", "https://www.nist.gov/privacy-framework"),
    ("otel_metrics_model", "OpenTelemetry metrics data model", "OpenTelemetry", "specification", "https://opentelemetry.io/docs/reference/specification/metrics/data-model/"),
    ("openmetadata_2", "OpenMetadata 2.0 releases", "OpenMetadata", "official_release", "https://github.com/open-metadata/OpenMetadata/releases"),
    ("nist_ssdf", "Secure Software Development Framework 1.1", "NIST", "government_standard", "https://csrc.nist.gov/pubs/sp/800/218/final"),
    ("cube_1_7", "Cube Core v1.7", "Cube", "official_release", "https://cube.dev/blog/cube-core-v1-7-tesseract-ga-data-modeling-performance"),
    ("jupyterlab_4_4", "JupyterLab 4.4 release", "Project Jupyter", "official_release", "https://jupyterlab.readthedocs.io/en/stable/getting_started/changelog.html"),
    ("graphql_2025", "GraphQL September 2025 specification", "GraphQL Foundation", "specification", "https://spec.graphql.org/September2025/"),
    ("opensearch_3", "OpenSearch 3.0 release notes", "OpenSearch", "official_release", "https://opensearch.org/docs/latest/version-history/"),
    ("kubernetes_multitenancy", "Kubernetes multi-tenancy", "Kubernetes", "official_documentation", "https://kubernetes.io/docs/concepts/security/multi-tenancy/"),
    ("google_sre_monitoring", "Monitoring Distributed Systems", "Google SRE", "official_handbook", "https://sre.google/sre-book/monitoring-distributed-systems/"),
    ("oci_distribution", "OCI Distribution Specification", "Open Container Initiative", "specification", "https://github.com/opencontainers/distribution-spec"),
    ("w3c_skos", "SKOS Simple Knowledge Organization System", "W3C", "recommendation", "https://www.w3.org/TR/skos-reference/"),
    ("python_packaging_specs", "Python packaging specifications", "Python Packaging Authority", "specification", "https://packaging.python.org/en/latest/specifications/"),
    ("oci_image", "OCI Image Format Specification", "Open Container Initiative", "specification", "https://github.com/opencontainers/image-spec"),
    ("llvm_20", "LLVM 20 release notes", "LLVM Project", "official_release", "https://releases.llvm.org/20.1.0/docs/ReleaseNotes.html"),
    ("bazel_8", "Bazel 8.0 release", "Bazel", "official_release", "https://blog.bazel.build/2024/12/09/bazel-8-release.html"),
    ("w3c_test_rules", "W3C Automated WCAG Monitoring community rules", "W3C", "specification", "https://www.w3.org/WAI/standards-guidelines/act/rules/"),
    ("rust_1_85", "Rust 1.85.0", "Rust Project", "official_release", "https://blog.rust-lang.org/2025/02/20/Rust-1.85.0/"),
    ("cncf_project_lifecycle", "CNCF project lifecycle", "CNCF", "governance_policy", "https://github.com/cncf/toc/blob/main/process/project_proposals.md"),
    ("helm_4", "Helm 4 release notes", "Helm", "official_release", "https://helm.sh/blog/helm-4-released/"),
    ("cncf_landscape", "CNCF Landscape", "CNCF", "official_registry", "https://landscape.cncf.io/"),
    ("github_releases_api", "GitHub Releases REST API", "GitHub", "official_api", "https://docs.github.com/en/rest/releases/releases"),
    ("tpc_ds", "TPC-DS benchmark specification", "Transaction Processing Performance Council", "benchmark_specification", "https://www.tpc.org/tpcds/"),
    ("google_spark_release_notes", "Google Cloud Managed Service for Apache Spark release notes", "Google Cloud", "release_feed", "https://docs.cloud.google.com/managed-spark/docs/release-notes"),
    ("google_spark_images", "Managed Spark image version lists", "Google Cloud", "official_documentation", "https://docs.cloud.google.com/managed-spark/docs/concepts/versioning/image-version-lists"),
    ("snowflake_iceberg_blog", "Streaming ingestion into Iceberg tables", "Snowflake", "official_architecture_post", "https://www.snowflake.com/en/blog/snowpipe-streaming-iceberg-tables/"),
    ("snowflake_iceberg_docs", "High-performance Snowpipe Streaming for Iceberg", "Snowflake", "official_documentation", "https://docs.snowflake.com/en/user-guide/snowpipe-streaming/snowpipe-streaming-high-performance-iceberg"),
    ("fabric_runtime_2", "Microsoft Fabric Runtime 2.0", "Microsoft", "official_documentation", "https://learn.microsoft.com/en-us/fabric/data-engineering/runtime-2-0"),
    ("snowflake_10_30", "Snowflake 10.30 release notes", "Snowflake", "official_release", "https://docs.snowflake.com/en/release-notes/2026/10_30"),
    ("snowflake_code_exec_release", "Cortex Agents code execution tool preview", "Snowflake", "official_release", "https://docs.snowflake.com/en/release-notes/2026/other/2026-08-20-cortex-agents-code-execution-tool-preview"),
    ("snowflake_code_exec_docs", "Cortex Agents code execution tool", "Snowflake", "official_documentation", "https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-agents-code-execution-tool"),
    ("snowflake_coco_release", "CoCo automations preview", "Snowflake", "official_release", "https://docs.snowflake.com/en/release-notes/2026/other/2026-08-21-cortex-code-automations-preview"),
    ("snowflake_coco_docs", "Cortex Code automations", "Snowflake", "official_documentation", "https://docs.snowflake.com/en/user-guide/cortex-code/cortex-code-automations"),
    ("snowflake_parse_release", "AI_EXTRACT and AI_PARSE_DOCUMENT restricted-account GA", "Snowflake", "official_release", "https://docs.snowflake.com/en/release-notes/2026/other/2026-08-20-ai-extract-parse-document-cse-network-restrictions-ga"),
    ("snowflake_parse_docs", "AI_PARSE_DOCUMENT limits", "Snowflake", "official_documentation", "https://docs.snowflake.com/en/user-guide/snowflake-cortex/parse-document"),
    ("snowflake_dcr", "Snowflake Data Clean Rooms update", "Snowflake", "official_release", "https://docs.snowflake.com/en/release-notes/2026/other/2026-08-20-dcr"),
    ("dagster_1_13_19", "Dagster 1.13.19", "Dagster", "official_release", "https://github.com/dagster-io/dagster/releases/tag/1.13.19"),
    ("typeorm_1_1", "TypeORM 1.1.0", "TypeORM", "official_release", "https://github.com/typeorm/typeorm/releases/tag/1.1.0"),
    ("redpanda_26_2", "Redpanda 26.2 release notes", "Redpanda", "official_release", "https://docs.redpanda.com/streaming/current/release-notes/v26.2.x/"),
    ("redpanda_compaction", "Redpanda log-compaction correctness analysis", "Redpanda", "official_engineering_post", "https://www.redpanda.com/blog/kafka-log-compaction-bug-fix-streaming"),
    ("cloudera_nvidia_spark", "Cloudera and NVIDIA Spark 4.1 GPU announcement", "Cloudera", "press_release", "https://www.cloudera.com/about/news-and-blogs/press-releases.html"),
    ("nvd_cve_2026_59893", "CVE-2026-59893", "NIST NVD", "government_advisory", "https://nvd.nist.gov/vuln/detail/CVE-2026-59893"),
    ("sqlparse_advisories", "sqlparse security advisories", "sqlparse maintainers", "maintainer_advisory", "https://github.com/andialbrecht/sqlparse/security/advisories"),
    ("redpanda_26_1", "Redpanda 26.1 release", "Redpanda", "official_release", "https://www.redpanda.com/blog/26-1-r1-cloud-topics"),
    ("cube_releases", "Cube releases", "Cube", "release_feed", "https://github.com/cube-js/cube/releases"),
    ("typeorm_releases", "TypeORM releases", "TypeORM", "release_feed", "https://github.com/typeorm/typeorm/releases"),
    ("snowflake_new_features", "Snowflake new feature release index", "Snowflake", "release_feed", "https://docs.snowflake.com/en/release-notes/new-features"),
    ("cisa_kev", "Known Exploited Vulnerabilities Catalog", "CISA", "government_advisory_feed", "https://www.cisa.gov/known-exploited-vulnerabilities-catalog"),
    ("osv_api", "Open Source Vulnerability API", "Google Open Source Security", "advisory_api", "https://osv.dev/docs/"),
    ("fmi_3_release", "FMI 3.0 release", "Modelica Association", "official_release", "https://fmi-standard.org/news/2022-05-10-fmi-3.0-release/"),
    ("slsa_1_release", "SLSA v1.0 final", "SLSA Community", "official_release", "https://slsa.dev/blog/2023/04/slsa-v1-final"),
    ("kafka_3_3_1", "Apache Kafka 3.3.1 release", "Apache Kafka", "official_release", "https://kafka.apache.org/blog/2022/10/03/apache-kafka-3.3.1-release-announcement"),
    ("crossref_rest_api", "Crossref REST API", "Crossref", "official_api", "https://www.crossref.org/documentation/retrieve-metadata/rest-api/"),
]

# The atlas can grow while this corpus is being rebuilt.  Name-based overrides
# keep the late compiler/ecosystem/change planes semantically routed instead of
# relying on a brittle positional coincidence.
PRIMARY_SOURCE_BY_PLANE = {
    plane_id: SOURCE_CATALOG[index][0]
    for index, plane_id in enumerate(PLANE_IDS)
    if index < len(SOURCE_CATALOG)
}
PRIMARY_SOURCE_BY_PLANE.update({
    "plane.compiler.binder_solver": "calcite_1_40",
    "plane.compiler.codegen_build": "bazel_8",
    "plane.compiler.conformance_eval": "w3c_test_rules",
    "plane.compiler.implementation": "rust_1_85",
    "plane.product.boundaries": "cncf_project_lifecycle",
    "plane.product.suites_solution_packs": "helm_4",
    "plane.ecosystem.companies_experts": "cncf_landscape",
    "plane.ecosystem.expert_portfolios": "informs_certification",
    "plane.ecosystem.research_artifacts": "crossref_rest_api",
    "plane.ecosystem.innovations": "github_releases_api",
    "plane.change.source_monitoring": "github_releases_api",
    "plane.change.invalidation_migration": "google_spark_release_notes",
    "plane.proof.mixed_vertical": "tpc_ds",
})
LAYER_FALLBACK_SOURCE = {
    "foundation": "json_schema_2020_12", "semantics": "w3c_owl2",
    "sources": "openapi_3_1", "representation": "arrow_format",
    "movement": "beam_model", "persistence": "iceberg_v3_spec",
    "compute": "substrait_functions", "runtime": "otel_spec",
    "operations": "openlineage_spec", "analytics": "informs_analytics_framework",
    "security": "opa_releases", "assurance": "nist_ssdf",
    "consumption": "graphql_2025", "platform": "kubernetes_multitenancy",
    "compiler": "llvm_20", "product": "cncf_project_lifecycle",
    "ecosystem": "github_releases_api", "change_intelligence": "github_releases_api",
    "proof": "tpc_ds",
}
for plane in PLANES:
    PRIMARY_SOURCE_BY_PLANE.setdefault(
        plane["plane_id"], LAYER_FALLBACK_SOURCE.get(plane["layer"], "github_releases_api")
    )

LLM_EXTENSION_SOURCE_SLUGS = {
    "snowflake_code_exec_release", "snowflake_code_exec_docs",
    "snowflake_coco_release", "snowflake_coco_docs",
    "snowflake_parse_release", "snowflake_parse_docs", "cube_releases",
}


def subject_kind(kind: str) -> str:
    if kind in {"standard", "specification", "recommendation", "rfc", "government_standard", "benchmark_specification"}:
        return "standard_or_specification"
    if "advisory" in kind:
        return "advisory_registry"
    if kind in {"release_feed", "official_release"}:
        return "release_stream"
    return "maintained_authority_surface"


SOURCES = []
SUBJECTS = []
OCCURRENCES = []
for index, (slug, title, publisher, kind, url) in enumerate(SOURCE_CATALOG):
    plane_ids = [plane for plane, source_slug in PRIMARY_SOURCE_BY_PLANE.items() if source_slug == slug]
    if not plane_ids:
        plane_ids = ["plane.ecosystem.innovations"]
    proof_ids = [PROOF_IDS[index % len(PROOF_IDS)]]
    SOURCES.append({
        "source_id": sid(slug), "title": title, "publisher": publisher,
        "source_kind": kind, "authority_tier": "primary", "canonical_url": url,
        "coverage_plane_ids": plane_ids, "proof_obligation_ids": proof_ids,
        "retrieved_at": AS_OF, "content_digest": None,
        "digest_posture": "locator_registered_digest_pending",
        "limitations": ["Primary authority for the scoped artifact only; not canonical atlas semantics or deployed-behavior proof."],
    })
    SUBJECTS.append({
        "subject_id": subj(slug), "name": title, "publisher": publisher,
        "subject_kind": subject_kind(kind),
        "core_scope": "extension_only" if slug in LLM_EXTENSION_SOURCE_SLUGS else "non_llm",
        "lifecycle_status": "monitored", "source_ids": [sid(slug)],
        "coverage_plane_ids": plane_ids, "canonical_semantics_authority": False,
        "monitoring_reason": "Detect edition, behavior, security, maturity, compatibility, cost, or availability changes without granting vendor taxonomy authority.",
    })
    OCCURRENCES.append({
        "source_occurrence_id": f"occurrence.{slug}.primary", "source_id": sid(slug),
        "subject_id": subj(slug), "endpoint": url,
        "endpoint_kind": "feed" if "feed" in kind or "release" in kind or "advisory" in kind else "document",
        "protocol": "https", "collector": "deterministic_http_conditional_get",
        "expected_cadence": "weekly", "freshness_slo_days": 14,
        "authentication": "public", "enabled": True,
        "last_observation": "unknown_until_successful_collection",
    })


CHANGE_TYPE_SPECS = [
    ("release", "Versioned artifact release", "release_note", "behavior_not_proven"),
    ("rollout", "Observed deployed rollout", "deployed_observation", "behavior_observed"),
    ("behavior_change", "Documented behavior change", "behavior_change_notice", "behavior_claimed"),
    ("documentation", "Documentation-only change", "documentation_diff", "behavior_not_proven"),
    ("deprecation", "Deprecation announcement", "release_note", "migration_candidate"),
    ("removal", "Feature or artifact removal", "release_note", "migration_required"),
    ("eol", "Support end-of-life", "lifecycle_notice", "migration_required"),
    ("default_change", "Default configuration change", "behavior_change_notice", "requalification_required"),
    ("alias_retarget", "Mutable alias retargeting", "release_note", "requalification_required"),
    ("dependency_floor", "Minimum dependency version raised", "release_note", "lockfile_review_required"),
    ("security_advisory", "Security advisory publication", "advisory", "exploit_not_proven"),
    ("exploit_evidence", "Observed exploitation evidence", "incident_or_kev", "exploitation_supported"),
    ("cve_enrichment", "CVE metadata enrichment", "advisory", "exploit_not_proven"),
    ("security_fix", "Security remediation release", "release_note", "patch_candidate"),
    ("availability", "Regional or service availability change", "release_note", "deployment_not_proven"),
    ("preview", "Preview feature announcement", "release_note", "not_ga"),
    ("ga", "General availability announcement", "release_note", "ga_claimed_not_deployed"),
    ("region_expansion", "Region or cloud expansion", "release_note", "topology_review_required"),
    ("limit_change", "Quota or finite-limit change", "documentation_diff", "capacity_review_required"),
    ("cost_change", "Pricing or billing semantic change", "official_pricing", "cost_model_review_required"),
    ("protocol_change", "Protocol edition or subset change", "spec_or_release", "conformance_required"),
    ("schema_change", "Schema or compatibility change", "spec_or_release", "migration_required"),
    ("api_change", "API contract change", "spec_or_release", "consumer_retest_required"),
    ("runtime_change", "Runtime or image change", "release_note", "target_requalification_required"),
    ("orchestration_change", "Scheduler or trigger behavior change", "release_note", "recovery_retest_required"),
    ("correctness_fix", "Correctness defect fix", "release_note", "historical_reconciliation_required"),
    ("performance_claim", "Vendor performance claim", "vendor_benchmark", "independent_confirmation_missing"),
    ("independent_benchmark", "Independent reproducible performance result", "independent_benchmark", "scoped_result"),
    ("provider_offer", "Provider feature claim", "product_documentation", "not_qualified_offer"),
    ("qualification_receipt", "Executed qualification evidence", "test_receipt", "qualified_for_exact_scope"),
    ("feed_failure", "Collection endpoint failure", "collector_receipt", "observability_gap"),
    ("no_news", "Successful bounded scan with no qualifying item", "collector_receipt", "bounded_negative_observation"),
    ("supersession", "Artifact or evidence superseded", "lifecycle_decision", "prior_evidence_retained"),
    ("llm_wrapper", "LLM or agent-specific wrapper feature", "release_note", "quarantine_from_core"),
    ("generic_substrate", "Reusable sandbox, identity, package, stage, cost or orchestration substrate", "bounded_claim", "eligible_for_core_review"),
]
CHANGE_TYPES = [
    {"change_type_id": f"change_type.{slug}", "name": name, "evidence_form": form,
     "decision_effect": effect, "canonical_semantics_authority": False}
    for slug, name, form, effect in CHANGE_TYPE_SPECS
]


SIGNAL_SPECS = [
    ("google_spark_image_cutover", "Google Managed Spark image aliases cut over to channel-free images and old images become unavailable", "google_spark_release_notes", "default_change", "ga", "admitted_core", "non_llm", ["plane.runtime.execution_model", "plane.compiler.provider_target_registry"], ["proof.deployment.identity", "proof.migration.safety"]),
    ("google_spark_cluster_recreation", "Existing clusters on old Managed Spark images may require replacement", "google_spark_images", "runtime_change", "ga", "admitted_core", "non_llm", ["plane.runtime.failure_recovery", "plane.pipeline.orchestration"], ["proof.recovery.safety", "proof.target.support"]),
    ("openmetadata_dynamic_sampling", "OpenMetadata 2.0 dynamic sampling replaces default full scans and cardinality distribution is not collected by default", "openmetadata_2", "default_change", "ga", "admitted_core", "non_llm", ["plane.assurance.quality_observability", "plane.runtime.economics"], ["proof.quality.coverage", "proof.resource.feasible"]),
    ("openmetadata_mcp_pagination", "OpenMetadata 2.0 enables MCP server with cursor pagination", "openmetadata_2", "api_change", "ga", "admitted_substrate", "llm_wrapper_generic_pagination_retained", ["plane.consumption.api_embed_share", "plane.sources.protocols"], ["proof.protocol.conformance", "proof.operation.signature"]),
    ("openmetadata_databricks_auth", "OpenMetadata Databricks pipeline authentication moves to structured authType configuration", "openmetadata_2", "schema_change", "ga", "admitted_core", "non_llm", ["plane.security.policy_enforcement", "plane.sources.connectors"], ["proof.policy.enforcement", "proof.migration.safety"]),
    ("snowflake_iceberg_v3_ingest", "Snowflake documents high-performance Snowpipe Streaming into managed Iceberg v2/v3 tables", "snowflake_iceberg_docs", "provider_offer", "ga", "admitted_core", "non_llm", ["plane.pipeline.batch_incremental_stream", "plane.persistence.analytical_formats_tables"], ["proof.offer.evidence", "proof.protocol.conformance"]),
    ("snowflake_iceberg_benchmark", "Snowflake reports more than one million rows per second in a vendor synthetic demo", "snowflake_iceberg_blog", "performance_claim", "ga", "admitted_as_vendor_claim_only", "non_llm", ["plane.runtime.economics", "plane.compute.parallel_distributed"], ["proof.resource.feasible", "proof.guarantee.posture"]),
    ("fabric_runtime_2", "Microsoft Fabric Runtime 2.0 and Python 3.13 compatibility", "fabric_runtime_2", "preview", "preview", "watchlist", "non_llm", ["plane.runtime.execution_model", "plane.compiler.provider_target_registry"], ["proof.target.support", "proof.offer.evidence"]),
    ("snowflake_period", "Snowflake PERIOD data type", "snowflake_10_30", "preview", "preview", "watchlist", "non_llm", ["plane.semantics.time", "plane.data.types_shapes"], ["proof.type.semantic", "proof.time.safety"]),
    ("snowflake_agent_code_wrapper", "Cortex Agents code_execution wrapper", "snowflake_code_exec_release", "llm_wrapper", "preview", "quarantined_llm", "llm_specific", ["plane.ecosystem.innovations"], ["proof.reference.adjudication"]),
    ("snowflake_sandbox_substrate", "Isolated Python 3.12 execution, package policy, thread scope and mounted-stage boundary", "snowflake_code_exec_docs", "generic_substrate", "preview", "admitted_substrate", "llm_wrapper_generic_substrate_retained", ["plane.compute.udf_extension", "plane.security.policy_enforcement", "plane.runtime.resource_control"], ["proof.target.support", "proof.policy.enforcement", "proof.resource.demand"]),
    ("snowflake_coco_wrapper", "Cortex Code unattended agent automations", "snowflake_coco_release", "llm_wrapper", "preview", "quarantined_llm", "llm_specific", ["plane.ecosystem.innovations"], ["proof.reference.adjudication"]),
    ("snowflake_automation_substrate", "Hourly task schedule, creator-role execution, billing and thread receipts", "snowflake_coco_docs", "generic_substrate", "preview", "admitted_substrate", "llm_wrapper_generic_substrate_retained", ["plane.pipeline.orchestration", "plane.runtime.economics", "plane.semantics.authority_policy"], ["proof.authority.complete", "proof.usage.reconciliation", "proof.slo.coverage"]),
    ("snowflake_parse_wrapper", "AI_EXTRACT and AI_PARSE_DOCUMENT functions", "snowflake_parse_release", "llm_wrapper", "ga", "quarantined_llm", "llm_specific", ["plane.ecosystem.innovations"], ["proof.reference.adjudication"]),
    ("snowflake_restricted_stage_substrate", "Encrypted-stage, PrivateLink, network restriction, file-size, page and region boundaries", "snowflake_parse_docs", "generic_substrate", "ga", "admitted_substrate", "llm_wrapper_generic_substrate_retained", ["plane.security.policy_enforcement", "plane.runtime.resource_control", "plane.data.file_container_formats"], ["proof.policy.enforcement", "proof.resource.demand", "proof.representation.layers"]),
    ("snowflake_dcr_iceberg", "Data Clean Rooms permit external and Iceberg tables within owner-region topology but not cross-cloud or cross-region sharing", "snowflake_dcr", "region_expansion", "ga", "admitted_core", "non_llm", ["plane.security.privacy_use", "plane.persistence.lakehouse_boundary"], ["proof.privacy.budget", "proof.product.exit"]),
    ("dbt_sqlparse_floor", "dbt-core 1.11.14 raises sqlparse floor to address parser denial-of-service vulnerabilities", "dbt_1_11_14", "dependency_floor", "ga", "admitted_core", "non_llm", ["plane.operations.transformation", "plane.security.policy_enforcement"], ["proof.offer.evidence", "proof.resource.feasible"]),
    ("dbt_azure_artifact_fix", "dbt-core 1.11.14 fixes Azure Blob Storage artifact uploads", "dbt_1_11_14", "correctness_fix", "ga", "admitted_core", "non_llm", ["plane.operations.lineage_provenance", "plane.persistence.object_file_block"], ["proof.lineage.closure", "proof.delivery.safety"]),
    ("sqlparse_cve", "CVE-2026-59893 records quadratic CPU denial of service in sqlparse", "nvd_cve_2026_59893", "security_advisory", "published", "admitted_advisory_only", "non_llm", ["plane.assurance.safety_compliance", "plane.runtime.resource_control"], ["proof.resource.feasible", "proof.offer.evidence"]),
    ("dagster_sensor_dry_run", "Dagster 1.13.19 fixes a sensor dry-run path that could launch runs after dynamic-partition permission failures", "dagster_1_13_19", "correctness_fix", "ga", "admitted_core", "non_llm", ["plane.pipeline.orchestration", "plane.semantics.authority_policy"], ["proof.authority.complete", "proof.delivery.safety"]),
    ("cloudera_gpu_spark", "Cloudera and NVIDIA announce Spark 4.1 GPU acceleration", "cloudera_nvidia_spark", "performance_claim", "announcement", "watchlist", "non_llm", ["plane.compute.acceleration", "plane.compiler.provider_target_registry"], ["proof.kernel.qualification", "proof.resource.feasible"]),
    ("redpanda_26_2_operator", "Redpanda Operator 26.2 adds multi-region Stretch Cluster support and safer rolling restarts", "redpanda_26_2", "ga", "ga", "admitted_core", "non_llm", ["plane.runtime.failure_recovery", "plane.pipeline.state_delivery"], ["proof.recovery.safety", "proof.migration.safety"]),
    ("redpanda_compaction_correctness", "Redpanda documents and repairs a log-compaction correctness defect", "redpanda_compaction", "correctness_fix", "ga", "admitted_core", "non_llm", ["plane.pipeline.state_delivery", "plane.persistence.operational_stores"], ["proof.operation.incremental", "proof.correction.retest"]),
    ("redpanda_cloud_topics", "Redpanda 26.1 makes Cloud Topics generally available", "redpanda_26_1", "ga", "ga", "admitted_core", "non_llm", ["plane.persistence.object_file_block", "plane.runtime.economics"], ["proof.provider.occurrence", "proof.resource.feasible"]),
    ("cube_tesseract_ga", "Cube Core 1.7 makes the Tesseract semantic query engine generally available", "cube_1_7", "ga", "ga", "admitted_core", "non_llm", ["plane.consumption.semantic_query_bi", "plane.compute.query_planning"], ["proof.offer.semantic", "proof.qualification.executed"]),
    ("cube_ai_wrappers", "Cube agent connectors and agentic analytics wrappers", "cube_releases", "llm_wrapper", "preview", "quarantined_llm", "llm_specific", ["plane.ecosystem.innovations"], ["proof.reference.adjudication"]),
    ("typeorm_write_safety", "TypeORM 1.1 defaults invalid where values to throw on write paths and rejects empty update/delete criteria", "typeorm_1_1", "default_change", "ga", "admitted_core", "non_llm", ["plane.persistence.operational_stores", "plane.operations.transformation"], ["proof.operation.laws", "proof.delivery.safety"]),
    ("typeorm_uuid_advisory", "A reported vulnerable uuid transitive dependency remains under maintainer review for the 0.3 branch", "typeorm_releases", "security_advisory", "reported", "watchlist", "non_llm", ["plane.assurance.safety_compliance", "plane.compiler.library_registry"], ["proof.offer.evidence", "proof.qualification.executed"]),
]

EXTENSION_SIGNAL_SLUGS = {
    "snowflake_agent_code_wrapper", "snowflake_coco_wrapper",
    "snowflake_parse_wrapper", "cube_ai_wrappers",
}
EXTENSION_SIGNAL_SPECS = [spec for spec in SIGNAL_SPECS if spec[0] in EXTENSION_SIGNAL_SLUGS]
SIGNAL_SPECS = [spec for spec in SIGNAL_SPECS if spec[0] not in EXTENSION_SIGNAL_SLUGS]


CANDIDATE_SIGNALS = []
for index, (slug, title, source_slug, ctype, maturity, admission, llm_posture, planes, proofs) in enumerate(SIGNAL_SPECS, 1):
    CANDIDATE_SIGNALS.append({
        "signal_id": f"signal.{slug}", "title": title,
        "source_ids": [sid(source_slug)], "change_type_ids": [f"change_type.{ctype}"],
        "observed_at": AS_OF, "coverage_plane_ids": planes,
        "proof_obligation_ids": proofs, "maturity": maturity,
        "admission_status": admission, "llm_posture": llm_posture,
        "canonical_semantics_authority": False,
        "release_vs_rollout": "release_or_documentation_observed_deployment_not_observed",
        "documentation_vs_behavior": "behavior_requires_deployed_or_conformance_evidence",
        "security_evidence_posture": "advisory_not_exploit_evidence" if ctype == "security_advisory" else "not_an_exploit_claim",
        "benchmark_posture": "vendor_synthetic_not_independent" if ctype == "performance_claim" else "not_a_benchmark_claim",
    })


VERIFIED_EVENTS = []
for signal in CANDIDATE_SIGNALS:
    if signal["admission_status"] in {"watchlist", "quarantined_llm"}:
        continue
    VERIFIED_EVENTS.append({
        "change_event_id": signal["signal_id"].replace("signal.", "change_event."),
        "signal_ids": [signal["signal_id"]], "title": signal["title"],
        "source_ids": signal["source_ids"], "verified_at": AS_OF,
        "verification_status": "primary_source_claim_verified",
        "deployed_rollout_status": "not_observed",
        "canonical_semantics_authority": False,
        "coverage_plane_ids": signal["coverage_plane_ids"],
        "proof_obligation_ids": signal["proof_obligation_ids"],
        "maturity": signal["maturity"], "llm_posture": signal["llm_posture"],
        "claim_boundary": "Confirms the primary publisher's scoped statement; does not prove deployment, universal behavior, interoperability, performance, or canonical semantics.",
    })


CLAIMS = []
for index, signal in enumerate(CANDIDATE_SIGNALS, 1):
    CLAIMS.append({
        "claim_id": f"claim.{index:03d}", "signal_id": signal["signal_id"],
        "statement": signal["title"], "source_ids": signal["source_ids"],
        "evidence_relation": "direct_primary_statement",
        "claim_scope": "publisher_artifact_or_service",
        "confidence": "high" if signal["admission_status"] not in {"watchlist", "admitted_as_vendor_claim_only"} else "medium",
        "valid_from": AS_OF, "valid_until": None,
        "counterevidence_required": True,
    })
    CLAIMS.append({
        "claim_id": f"claim.{index:03d}.boundary", "signal_id": signal["signal_id"],
        "statement": "This evidence does not establish deployed rollout, independent performance, universal applicability, or canonical domain semantics.",
        "source_ids": signal["source_ids"], "evidence_relation": "scope_boundary",
        "claim_scope": "negative_boundary", "confidence": "high",
        "valid_from": AS_OF, "valid_until": None, "counterevidence_required": False,
    })

DETAIL_CLAIM_SPECS = [
    ("google_spark_conda", "signal.google_spark_image_cutover", "Channel-free subminor images require workloads using Conda to declare channels explicitly; alias-based provisioning, init actions, custom images, CI and notebooks require migration review.", "source.google_spark_release_notes"),
    ("google_spark_scope", "signal.google_spark_cluster_recreation", "The documentation says old clusters may need replacement; it does not claim that every job fails.", "source.google_spark_images"),
    ("openmetadata_profile", "signal.openmetadata_dynamic_sampling", "Distinct-value rules can lose coverage when cardinality distribution is no longer collected by default; cost reduction and quality coverage must be evaluated separately.", "source.openmetadata_2"),
    ("openmetadata_cursor", "signal.openmetadata_mcp_pagination", "The API uses nextCursor and documents cursor stability under concurrent writes; clients still require pagination, expiry, duplicate and resume tests.", "source.openmetadata_2"),
    ("openmetadata_auth", "signal.openmetadata_databricks_auth", "External YAML using legacy Databricks authentication fields may require manual conversion to structured authType configuration.", "source.openmetadata_2"),
    ("snowflake_iceberg_limits", "signal.snowflake_iceberg_v3_ingest", "Iceberg v3 requires the high-performance ingestion path, while partitioned tables, schema evolution and external catalogs remain documented limitations.", "source.snowflake_iceberg_docs"),
    ("snowflake_benchmark_scope", "signal.snowflake_iceberg_benchmark", "The reported one-million-plus throughput is a vendor synthetic demo and has no independent-result identity in this corpus.", "source.snowflake_iceberg_blog"),
    ("snowflake_sandbox_limits", "signal.snowflake_sandbox_substrate", "Execution is thread-scoped, in-memory state is not persistent, only mounted workspace stages are reachable, owner-rights agents cannot use the tool, and broader PyPI or always_allow access widens risk.", "source.snowflake_code_exec_docs"),
    ("snowflake_automation_limits", "signal.snowflake_automation_substrate", "Automations use the creator's default roles, can run without a warehouse, have a one-hour minimum cadence, incur task and token costs, and lack event triggers or interactive approval.", "source.snowflake_coco_docs"),
    ("snowflake_parse_limits", "signal.snowflake_restricted_stage_substrate", "Restricted-account document processing retains a 100 MB and 2,000-page per-file ceiling, page-based cost, regional restrictions and limited extracted-image behavior.", "source.snowflake_parse_docs"),
    ("snowflake_dcr_topology", "signal.snowflake_dcr_iceberg", "External and Iceberg tables can participate when parties are in the owner region, but unsupported object replication prevents sharing those tables to other clouds or regions.", "source.snowflake_dcr"),
    ("dbt_sqlparse_constraint", "signal.dbt_sqlparse_floor", "dbt-core requires sqlparse >=0.5.5,<0.7.0; adapter lockfiles and externally supplied SQL parsing require scoped retest.", "source.dbt_1_11_14"),
    ("sqlparse_advisory_scope", "signal.sqlparse_cve", "The advisory describes a high-severity quadratic-CPU denial-of-service attack shape; it is not evidence that a bound dbt occurrence was exploited.", "source.nvd_cve_2026_59893"),
    ("dagster_dry_run_scope", "signal.dagster_sensor_dry_run", "The fixed path could launch runs after a dynamic-partition permission failure during a sensor dry run, so negative authorization tests and effect receipts must be separate.", "source.dagster_1_13_19"),
    ("redpanda_compaction_scope", "signal.redpanda_compaction_correctness", "The vendor engineering analysis reports compaction/replication races affecting tombstones and transaction control batches; affected-version and independent repair evidence remain open.", "source.redpanda_compaction"),
    ("cube_tesseract_scope", "signal.cube_tesseract_ga", "Tesseract and the native query pipeline become defaults and deprecated options are removed; vendor performance figures remain synthetic claims pending independent receipts.", "source.cube_1_7"),
    ("typeorm_write_scope", "signal.typeorm_write_safety", "The safer write defaults can break callers that relied on permissive null, undefined or empty criteria; negative update/delete tests are migration obligations.", "source.typeorm_1_1"),
]
for slug, signal_id, statement, source_id in DETAIL_CLAIM_SPECS:
    CLAIMS.append({
        "claim_id": f"claim.detail.{slug}", "signal_id": signal_id,
        "statement": statement, "source_ids": [source_id],
        "evidence_relation": "direct_primary_detail",
        "claim_scope": "publisher_artifact_or_service", "confidence": "high",
        "valid_from": AS_OF, "valid_until": None, "counterevidence_required": True,
    })


COVERAGE_MAPPINGS = []
for index, plane in enumerate(PLANES):
    source_slug = PRIMARY_SOURCE_BY_PLANE[plane["plane_id"]]
    source = next(row for row in SOURCES if row["source_id"] == sid(source_slug))
    proof = PROOFS[index % len(PROOFS)]
    COVERAGE_MAPPINGS.append({
        "coverage_mapping_id": f"coverage_mapping.{index + 1:03d}",
        "coverage_plane_id": plane["plane_id"], "source_ids": [source["source_id"]],
        "subject_ids": [subj(source_slug)],
        "proof_obligation_ids": [proof["proof_id"]],
        "monitoring_effect": "candidate_change_reopens_proof_and_routes_to_plane_owner",
        "authority_rule": "Source evidence may invalidate or reopen a proof; it never defines canonical semantics.",
    })


IMPACT_MAPPINGS = []
for index, signal in enumerate(CANDIDATE_SIGNALS, 1):
    IMPACT_MAPPINGS.append({
        "impact_mapping_id": f"impact.{index:03d}", "signal_id": signal["signal_id"],
        "coverage_plane_ids": signal["coverage_plane_ids"],
        "proof_obligation_ids": signal["proof_obligation_ids"],
        "affected_capability_ids": [f"capability.change.{signal['change_type_ids'][0].split('.')[-1]}"],
        "affected_contract_ids": [f"contract.monitor.{p.split('.')[-1]}" for p in signal["proof_obligation_ids"]],
        "affected_provider_ids": [f"provider.{signal['source_ids'][0].split('.')[1]}"],
        "affected_target_ids": ["target.deployed_occurrence_unknown"],
        "effect": "requalify_or_retain_gap" if signal["admission_status"] != "quarantined_llm" else "quarantine",
        "canonical_semantics_authority": False,
    })
    IMPACT_MAPPINGS.append({
        "impact_mapping_id": f"impact.{index:03d}.invalidation", "signal_id": signal["signal_id"],
        "coverage_plane_ids": signal["coverage_plane_ids"],
        "proof_obligation_ids": signal["proof_obligation_ids"],
        "affected_capability_ids": ["capability.evidence_freshness"],
        "affected_contract_ids": ["contract.provider_offer_currentness"],
        "affected_provider_ids": [f"provider.{signal['source_ids'][0].split('.')[1]}"],
        "affected_target_ids": ["target.any_bound_occurrence"],
        "effect": "invalidate_cached_assumption_until_scoped_review",
        "canonical_semantics_authority": False,
    })


REVIEW_DECISIONS = []
for index, signal in enumerate(CANDIDATE_SIGNALS, 1):
    status = signal["admission_status"]
    decision = "admit_bounded_claim"
    if status == "watchlist":
        decision = "defer_pending_evidence"
    elif status == "quarantined_llm":
        decision = "quarantine_llm_specific_wrapper"
    elif status == "admitted_as_vendor_claim_only":
        decision = "admit_vendor_claim_not_result"
    REVIEW_DECISIONS.append({
        "review_decision_id": f"review.{index:03d}", "signal_id": signal["signal_id"],
        "decision": decision, "decided_at": AS_OF,
        "authority_role": "change_intelligence_reviewer",
        "rationale": "Preserve evidence scope, maturity, non-LLM boundary, and compiler proof impact.",
        "coverage_plane_ids": signal["coverage_plane_ids"],
        "proof_obligation_ids": signal["proof_obligation_ids"],
        "revisit_trigger_ids": [f"trigger.{index:03d}"],
    })
for index, ctype in enumerate(CHANGE_TYPES[:20], 1):
    REVIEW_DECISIONS.append({
        "review_decision_id": f"review.policy.{index:03d}", "signal_id": None,
        "decision": "adopt_change_classification_policy", "decided_at": AS_OF,
        "authority_role": "change_intelligence_steward",
        "rationale": f"Keep {ctype['name'].lower()} distinct in evidence and downstream invalidation.",
        "coverage_plane_ids": [PLANE_IDS[(index - 1) % len(PLANE_IDS)]],
        "proof_obligation_ids": [PROOF_IDS[(index - 1) % len(PROOF_IDS)]],
        "revisit_trigger_ids": [],
    })


TRIGGERS = []
for index, signal in enumerate(CANDIDATE_SIGNALS, 1):
    TRIGGERS.append({
        "trigger_id": f"trigger.{index:03d}", "signal_id": signal["signal_id"],
        "trigger_kind": "migration_and_invalidation",
        "condition": "A bound artifact, mutable alias, default, dependency, security posture, limit, region, protocol, or maturity matches this signal.",
        "actions": ["freeze affected evidence", "identify deployed occurrences", "rerun mapped proofs", "issue migration or refusal decision"],
        "invalidates": ["provider_offer_qualification", "target_compatibility_receipt", "cached_compiler_decision"],
        "rollback_required": True,
        "proof_obligation_ids": signal["proof_obligation_ids"],
    })


TRADEOFF_SPECS = [
    ("package_egress", "External package access expands capability and supply-chain/egress exposure", "deny by default; mirror and pin packages"),
    ("owner_rights", "Owner-rights execution improves unattended availability while widening inherited authority", "use least-privilege execution identities"),
    ("stage_mount", "Mounted stages enable artifact exchange while increasing data disclosure paths", "mount explicit read/write prefixes"),
    ("network_restriction", "Private connectivity reduces exposure while constraining regional availability", "prove regional failover topology"),
    ("fips_cost", "FIPS mode strengthens cryptographic posture with possible performance and compatibility cost", "benchmark exact FIPS artifact"),
    ("multi_region_consistency", "Multi-region availability may increase latency and consistency coordination", "declare recovery and consistency objectives"),
    ("automatic_restart", "Automated restarts improve recovery but may act without approval", "require fencing and auditable policy"),
    ("dynamic_sampling", "Sampling reduces profiler cost but can reduce rule coverage", "bind sampling error and critical-field exceptions"),
    ("cardinality_default", "Disabling cardinality lowers work while removing distinct-value evidence", "retain explicit cardinality controls where required"),
    ("cursor_pagination", "Stable cursors improve availability under writes but require expiry and replay semantics", "test resume and duplicate behavior"),
    ("stream_buffering", "Server buffering raises throughput while changing latency and failure windows", "measure flush and recovery semantics"),
    ("tiered_storage", "Object-backed topics reduce local cost while adding remote dependency and restore paths", "test remote read and supplier exit"),
    ("gpu_acceleration", "GPU acceleration may reduce latency but adds target, driver and cost coupling", "qualify workload and CPU fallback"),
    ("parser_rejection", "Strict invalid-where rejection improves write safety but can break permissive callers", "stage migration with negative tests"),
    ("hourly_automation", "Managed hourly automation reduces operator toil but lacks event triggers and interactive approval", "route irreversible effects through separate approval"),
    ("encrypted_parse", "In-place encrypted-stage parsing reduces data movement but retains region, page and size limits", "enforce finite admission before execution"),
    ("clean_room_region", "Regional restrictions reduce replication exposure but constrain collaborator availability", "model region topology as hard constraint"),
    ("security_patch", "Rapid dependency patching reduces exposure but may introduce adapter incompatibility", "lock, test, canary and retain rollback"),
]
TRADEOFFS = [
    {"tradeoff_id": f"tradeoff.{slug}", "security_or_control_gain": gain,
     "availability_cost_or_risk": risk, "required_control": control,
     "coverage_plane_ids": ["plane.security.policy_enforcement", "plane.runtime.slo_observability"],
     "proof_obligation_ids": ["proof.policy.enforcement", "proof.slo.coverage"]}
    for slug, gain, control in TRADEOFF_SPECS
    for risk in [gain.split(" while ", 1)[1] if " while " in gain else "Requires explicit availability evaluation."]
]


WATCHLIST_SPECS = [
    ("fabric_runtime_2", "signal.fabric_runtime_2", "GA status, Python 3.13 compatibility matrix, regional rollout, workload receipts"),
    ("snowflake_period", "signal.snowflake_period", "final temporal semantics, client interoperability and GA evidence"),
    ("cloudera_gpu", "signal.cloudera_gpu_spark", "public runtime matrix and reproducible workload/cost benchmarks"),
    ("typeorm_uuid", "signal.typeorm_uuid_advisory", "maintainer fix, exact affected path and exploitability decision"),
    ("snowflake_code_exec", "signal.snowflake_sandbox_substrate", "GA, sandbox escape testing, package provenance and owner-rights posture"),
    ("snowflake_coco", "signal.snowflake_automation_substrate", "event triggers, approval boundary, billing and GA"),
    ("snowflake_parse", "signal.snowflake_restricted_stage_substrate", "finite stage, region, page and file-size conformance receipts"),
    ("cube_engine", "signal.cube_tesseract_ga", "breaking-change migration, semantic equivalence and exact-target qualification"),
    ("redpanda_compaction", "signal.redpanda_compaction_correctness", "affected versions, repair tooling and independent reconciliation"),
    ("google_spark_cutover", "signal.google_spark_image_cutover", "regional alias resolution and deployed job results before cutoff"),
    ("openmetadata_2", "signal.openmetadata_dynamic_sampling", "production profiler recall and cost receipts"),
    ("snowflake_iceberg", "signal.snowflake_iceberg_v3_ingest", "partitioning, evolution, external catalog and independent throughput evidence"),
]
WATCHLIST = [
    {"watch_id": f"watch.{slug}", "signal_id": signal_id, "missing_evidence": missing,
     "priority": "high", "next_review_at": "2026-09-01",
     "exit_criteria": "Required primary documentation and scoped execution evidence are captured and adjudicated."}
    for slug, signal_id, missing in WATCHLIST_SPECS
]


SUPERSESSION_SPECS = [
    ("google_spark_alias", "mutable image alias", "pinned image digest", "Alias movement reopens target qualification."),
    ("openmetadata_profiler", "100 percent scan default", "dynamic sampling default", "Prior coverage assumption is invalid."),
    ("openmetadata_auth", "legacy authentication fields", "structured authType", "External YAML may require manual migration."),
    ("dbt_sqlparse", "sqlparse below 0.5.5", "sqlparse 0.5.5 or later under dbt constraint", "Prior dependency qualification expires."),
    ("typeorm_write", "permissive invalid where values", "throw on invalid write criteria", "Call-site behavior changes."),
    ("cube_engine", "pre-Tesseract engine qualification", "Tesseract GA qualification candidate", "GA does not inherit old receipts."),
    ("redpanda_cluster", "single-region operator assumptions", "26.2 multi-region topology", "Recovery and fencing proofs reopen."),
    ("iceberg_v2", "Iceberg v2 ingestion assumption", "Iceberg v3 high-performance path", "Format and connector conformance reopen."),
    ("snowflake_parse", "unrestricted-stage-only posture", "restricted encrypted-stage GA", "Security topology may expand after review."),
    ("snowflake_automation", "interactive-only run assumption", "unattended hourly task preview", "Authority and cost controls reopen."),
    ("dagster_sensor", "pre-1.13.19 dry-run trust", "1.13.19 patched behavior", "Prior negative test receipt expires."),
    ("evidence_age", "fresh source claim", "expired source claim", "Expiration creates unknown, not false."),
]
SUPERSESSION = [
    {"supersession_id": f"supersession.{slug}", "prior_identity": prior,
     "successor_identity": successor, "reason": reason, "effective_at": AS_OF,
     "prior_evidence_retained": True, "automatic_semantic_replacement": False}
    for slug, prior, successor, reason in SUPERSESSION_SPECS
]


INNOVATION_SPECS = [
    ("kafka_kraft", 2022, "Kafka KRaft production-ready posture", "kafka_3_3_1", "plane.pipeline.state_delivery"),
    ("fmi_3", 2022, "FMI 3.0 clocks, terminals and binary data", "fmi_3_release", "plane.analytics.operations_research"),
    ("ocel_2", 2023, "Object-centric event log 2.0", "ocel_2", "plane.analytics.process_case"),
    ("slsa_1", 2023, "SLSA provenance 1.0", "slsa_1_release", "plane.assurance.safety_compliance"),
    ("wasi_preview2", 2024, "WASI Preview 2 component interfaces", "wasi_preview2", "plane.runtime.execution_model"),
    ("openfeature", 2023, "OpenFeature vendor-neutral feature flag evaluation", "openfeature_spec", "plane.analytics.decision_action_feedback"),
    ("arrow_c_stream", 2022, "Arrow C Stream interface adoption", "arrow_c_data", "plane.data.memory_layout"),
    ("substrait_extensions", 2024, "Portable Substrait extension declarations", "substrait_functions", "plane.operations.typed_registry"),
    ("iceberg_v3", 2025, "Iceberg v3 deletion vectors and row lineage", "iceberg_v3_spec", "plane.persistence.analytical_formats_tables"),
    ("delta_4", 2025, "Delta Lake 4.0 kernel-centered interoperability", "delta_4_0", "plane.persistence.lakehouse_boundary"),
    ("spark_4", 2025, "Spark 4.0 ANSI mode and runtime evolution", "spark_4_0", "plane.compute.parallel_distributed"),
    ("kafka_4", 2025, "Kafka 4.0 KRaft-only operation", "kafka_4_0", "plane.pipeline.state_delivery"),
    ("flink_1_20", 2024, "Flink 1.20 state and streaming evolution", "flink_1_20", "plane.pipeline.batch_incremental_stream"),
    ("focus_1_2", 2025, "FOCUS 1.2 cloud cost schema", "finops_focus_1_2", "plane.runtime.economics"),
    ("otel_semconv", 2024, "OpenTelemetry stable semantic conventions", "otel_spec", "plane.runtime.slo_observability"),
    ("openlineage", 2022, "OpenLineage extensible run/job/dataset facets", "openlineage_spec", "plane.operations.lineage_provenance"),
    ("cube_tesseract", 2026, "Cube Tesseract semantic query engine GA", "cube_1_7", "plane.consumption.semantic_query_bi"),
    ("typeorm_1", 2026, "TypeORM 1.x safer write defaults", "typeorm_1_1", "plane.persistence.operational_stores"),
    ("spark_image_control", 2026, "Managed Spark channel-free image lifecycle", "google_spark_release_notes", "plane.compiler.provider_target_registry"),
    ("dynamic_sampling", 2026, "OpenMetadata dynamic profiler sampling", "openmetadata_2", "plane.assurance.quality_observability"),
    ("snowpipe_iceberg_v3", 2026, "Streaming ingestion into Iceberg v3", "snowflake_iceberg_docs", "plane.persistence.analytical_formats_tables"),
    ("redpanda_cloud_topics", 2026, "Topic-level object-backed streaming storage", "redpanda_26_1", "plane.persistence.object_file_block"),
    ("redpanda_stretch", 2026, "Operator-managed stretch clusters", "redpanda_26_2", "plane.runtime.failure_recovery"),
    ("dagster_permission_fix", 2026, "Permission-safe sensor dry-run behavior", "dagster_1_13_19", "plane.pipeline.orchestration"),
    ("dbt_parser_floor", 2026, "Security-driven SQL parser floor", "dbt_1_11_14", "plane.operations.transformation"),
    ("graphql_2025", 2025, "GraphQL September 2025 edition", "graphql_2025", "plane.consumption.api_embed_share"),
    ("rust_2024_edition", 2025, "Rust 2024 language edition", "rust_1_85", "plane.compiler.codegen_build"),
    ("bazel_8", 2024, "Bazel 8 symbolic macros and dependency changes", "bazel_8", "plane.compiler.codegen_build"),
]
INNOVATIONS = [
    {"innovation_id": f"innovation.{slug}", "year": year, "name": name,
     "source_ids": [sid(source_slug)], "coverage_plane_ids": [plane],
     "proof_obligation_ids": [PROOF_IDS[index % len(PROOF_IDS)]],
     "llm_dependency": "none", "admission_status": "candidate",
     "canonical_semantics_authority": False,
     "implementation_evidence": "primary specification or maintained release; deployed and independent receipts remain separate"}
    for index, (slug, year, name, source_slug, plane) in enumerate(INNOVATION_SPECS)
]


GAP_SPECS = [
    ("dns_observability", "All 40 feed endpoints failed DNS in each supplied run; this is missing observation, never no change."),
    ("content_digests", "Primary locators are registered but most content digests await successful collection."),
    ("deployment_rollout", "Release notes do not establish which deployed occurrences received a rollout."),
    ("independent_benchmarks", "Vendor throughput claims lack independent reproducible confirmation."),
    ("provider_qualification", "Feature availability is not an executed provider-offer qualification receipt."),
    ("regional_rollout", "Regional rollout timing is incomplete for several managed services."),
    ("preview_stability", "Preview features lack GA stability and compatibility contracts."),
    ("exploit_evidence", "Advisories do not alone establish exploitation in a bound occurrence."),
    ("artifact_inventory", "Deployed artifact and lockfile inventories are not connected."),
    ("target_receipts", "Exact target, runtime, driver and architecture receipts are missing."),
    ("migration_rehearsal", "Rollback, replay and historical repair rehearsals are missing."),
    ("cost_receipts", "Observed billing and resource usage are missing for managed features."),
    ("security_testing", "Sandbox escape, egress and package provenance tests are missing."),
    ("feed_etag", "ETag and Last-Modified state cannot be established until DNS succeeds."),
    ("schema_diff", "Machine-readable release-note schema diffs are unavailable for some vendors."),
    ("semantic_owner_review", "Plane owners have not adjudicated candidate semantic impact."),
    ("vertical_acceptance", "No mixed-industry acceptance case has rerun against these changes."),
    ("supplier_exit", "Portability and supplier-exit exercises are not current for changed offers."),
    ("archive_retention", "Historical release-note retention guarantees differ by source."),
    ("clock_skew", "Publisher timestamps and rollout timestamps may differ and need separate observation clocks."),
    ("llm_substrate_split", "Some vendor documents bundle generic substrate with model-specific behavior."),
    ("coverage_saturation", "One source per plane proves routing coverage, not source or innovation completeness."),
]
GAPS = [
    {"gap_id": f"gap.{slug}", "description": description, "status": "open",
     "effect": "retain_unknown_and_block_overclaim", "owner_role": "change_intelligence_steward",
     "coverage_plane_ids": [PLANE_IDS[index % len(PLANE_IDS)]],
     "proof_obligation_ids": [PROOF_IDS[index % len(PROOF_IDS)]]}
    for index, (slug, description) in enumerate(GAP_SPECS)
]


SCHEDULES = [
    {"schedule_id": "schedule.release_feeds.daily", "cadence": "0 3 * * *", "timezone": "UTC", "scope": "release and changelog endpoints", "non_llm_filter": True, "on_failure": "emit_collection_gap", "on_success_no_candidates": "emit_bounded_no_news"},
    {"schedule_id": "schedule.security_feeds.six_hourly", "cadence": "17 */6 * * *", "timezone": "UTC", "scope": "CISA, OSV, NVD and maintainer advisories", "non_llm_filter": True, "on_failure": "emit_collection_gap", "on_success_no_candidates": "emit_bounded_no_news"},
    {"schedule_id": "schedule.specifications.weekly", "cadence": "31 4 * * 1", "timezone": "UTC", "scope": "standards and specification editions", "non_llm_filter": True, "on_failure": "emit_collection_gap", "on_success_no_candidates": "emit_bounded_no_news"},
    {"schedule_id": "schedule.docs.weekly", "cadence": "13 5 * * 2", "timezone": "UTC", "scope": "documentation behavior, limits, defaults and regions", "non_llm_filter": True, "on_failure": "emit_collection_gap", "on_success_no_candidates": "emit_bounded_no_news"},
    {"schedule_id": "schedule.rollout_receipts.daily", "cadence": "47 2 * * *", "timezone": "UTC", "scope": "bound deployment occurrences", "non_llm_filter": True, "on_failure": "emit_collection_gap", "on_success_no_candidates": "emit_bounded_no_news"},
    {"schedule_id": "schedule.watchlist.weekly", "cadence": "23 6 * * 3", "timezone": "UTC", "scope": "preview, disputed, incomplete and quarantined-substrate watch items", "non_llm_filter": False, "on_failure": "emit_collection_gap", "on_success_no_candidates": "emit_bounded_no_news"},
    {"schedule_id": "schedule.supersession.monthly", "cadence": "7 7 1 * *", "timezone": "UTC", "scope": "edition, EOL, deprecation and evidence expiration", "non_llm_filter": True, "on_failure": "emit_collection_gap", "on_success_no_candidates": "emit_bounded_no_news"},
    {"schedule_id": "schedule.coverage.audit.monthly", "cadence": "41 8 2 * *", "timezone": "UTC", "scope": "all atlas planes and compiler proof obligations", "non_llm_filter": True, "on_failure": "emit_collection_gap", "on_success_no_candidates": "emit_bounded_no_news"},
]


COLLECTION_RUNS = [
    {"collection_run_id": "run.supplied_brief.google_spark", "started_at": "2026-08-25T00:00:00Z", "feed_attempts": 40, "feed_successes": 0, "dns_failures": 40, "manual_pages_opened": 30, "feed_candidates_reviewed": 0, "scope_beats": 9, "result_posture": "manual_primary_review_with_feed_observability_gap", "no_news_claim": False},
    {"collection_run_id": "run.supplied_brief.snowflake", "started_at": "2026-08-25T01:00:00Z", "feed_attempts": 40, "feed_successes": 0, "dns_failures": 40, "manual_pages_opened": 30, "feed_candidates_reviewed": 0, "scope_beats": 9, "result_posture": "manual_primary_review_with_feed_observability_gap", "no_news_claim": False},
]


COLLECTION_ATTEMPTS = []
feed_occurrences = OCCURRENCES[:40]
manual_occurrences = OCCURRENCES[84:]
for run_index, run in enumerate(COLLECTION_RUNS):
    for index, occurrence in enumerate(feed_occurrences, 1):
        COLLECTION_ATTEMPTS.append({
            "collection_attempt_id": f"attempt.{run_index + 1}.feed.{index:02d}",
            "collection_run_id": run["collection_run_id"],
            "source_occurrence_id": occurrence["source_occurrence_id"],
            "attempted_at": run["started_at"], "outcome": "failure",
            "failure_class": "dns_resolution", "http_status": None,
            "content_changed": None, "candidate_count": 0,
            "interpretation": "observability_gap_not_evidence_of_no_change",
        })
    for index in range(30):
        occurrence = manual_occurrences[index % len(manual_occurrences)]
        COLLECTION_ATTEMPTS.append({
            "collection_attempt_id": f"attempt.{run_index + 1}.manual.{index + 1:02d}",
            "collection_run_id": run["collection_run_id"],
            "source_occurrence_id": occurrence["source_occurrence_id"],
            "attempted_at": run["started_at"], "outcome": "success",
            "failure_class": None, "http_status": 200,
            "content_changed": None, "candidate_count": None,
            "interpretation": "manual_primary_page_opened_candidate_count_not_reconstructed",
        })


OFFER_OBSERVATIONS = []
for index, event in enumerate(VERIFIED_EVENTS, 1):
    OFFER_OBSERVATIONS.append({
        "offer_observation_id": f"offer_observation.{index:03d}",
        "change_event_id": event["change_event_id"],
        "provider_id": f"provider.{event['source_ids'][0].split('.')[1]}",
        "feature_claim_observed": True, "qualified_offer": False,
        "deployed_occurrence_id": None, "qualification_receipt_ids": [],
        "decision": "requalify_before_selection",
        "proof_obligation_ids": ["proof.provider.occurrence", "proof.qualification.executed", "proof.offer.evidence"],
    })


EXTENSION_CORE_MAPPINGS = {
    "snowflake_agent_code_wrapper": ["signal.snowflake_sandbox_substrate"],
    "snowflake_coco_wrapper": ["signal.snowflake_automation_substrate"],
    "snowflake_parse_wrapper": ["signal.snowflake_restricted_stage_substrate"],
    "cube_ai_wrappers": ["signal.cube_tesseract_ga"],
    "openmetadata_mcp_wrapper": ["signal.openmetadata_mcp_pagination"],
}
EXTENSION_CAPABILITY_NAMES = {
    "snowflake_agent_code_wrapper": "Model-directed code-execution tool invocation",
    "snowflake_coco_wrapper": "Agent-authored unattended task automation",
    "snowflake_parse_wrapper": "Model-assisted document extraction and parsing",
    "cube_ai_wrappers": "Agent connectors over governed semantic queries",
    "openmetadata_mcp_wrapper": "Agent-facing metadata protocol server",
}

EXTENSION_SIGNALS = []
for slug, title, source_slug, ctype, maturity, _admission, llm_posture, planes, proofs in EXTENSION_SIGNAL_SPECS:
    EXTENSION_SIGNALS.append({
        "extension_signal_id": f"extension_signal.{slug}",
        "extension_namespace": "llm_agent_optional", "title": title,
        "source_ids": [sid(source_slug)], "change_type_ids": [f"change_type.{ctype}"],
        "maturity": maturity, "llm_posture": llm_posture,
        "capability_ids": [f"extension_capability.{slug}"],
        "core_substrate_signal_ids": EXTENSION_CORE_MAPPINGS[slug],
        "dependency_direction": "extension_imports_deterministic_core",
        "coverage_plane_ids": planes, "proof_obligation_ids": proofs,
        "canonical_semantics_authority": False,
        "release_vs_rollout": "release_or_documentation_observed_deployment_not_observed",
        "documentation_vs_behavior": "behavior_requires_deployed_or_conformance_evidence",
        "qualified_provider_offer": False,
    })
EXTENSION_SIGNALS.append({
    "extension_signal_id": "extension_signal.openmetadata_mcp_wrapper",
    "extension_namespace": "llm_agent_optional",
    "title": "OpenMetadata exposes an agent-facing MCP server enabled by default",
    "source_ids": [sid("openmetadata_2")], "change_type_ids": ["change_type.llm_wrapper"],
    "maturity": "ga", "llm_posture": "llm_specific",
    "capability_ids": ["extension_capability.openmetadata_mcp_wrapper"],
    "core_substrate_signal_ids": EXTENSION_CORE_MAPPINGS["openmetadata_mcp_wrapper"],
    "dependency_direction": "extension_imports_deterministic_core",
    "coverage_plane_ids": ["plane.ecosystem.innovations"],
    "proof_obligation_ids": ["proof.reference.adjudication"],
    "canonical_semantics_authority": False,
    "release_vs_rollout": "release_or_documentation_observed_deployment_not_observed",
    "documentation_vs_behavior": "behavior_requires_deployed_or_conformance_evidence",
    "qualified_provider_offer": False,
})

EXTENSION_CAPABILITIES = [
    {
        "extension_capability_id": f"extension_capability.{slug}",
        "extension_namespace": "llm_agent_optional", "name": name,
        "input_boundary": "validated structured context and explicitly granted deterministic core tools",
        "output_boundary": "untrusted model output or proposed agent plan",
        "effect_authority": "none_without_separate_authorized_tool_intent",
        "core_substrate_signal_ids": core_ids,
        "dependency_direction": "extension_imports_deterministic_core",
    }
    for slug, name in EXTENSION_CAPABILITY_NAMES.items()
    for core_ids in [EXTENSION_CORE_MAPPINGS[slug]]
]

EFFECT_STATE_SPECS = [
    ("model_output", "Untrusted generated content", ["agent_plan", "validated_claim", "authorized_tool_intent", "effect_receipt"]),
    ("agent_plan", "Proposed ordered actions without execution authority", ["validated_claim", "authorized_tool_intent", "effect_receipt"]),
    ("validated_claim", "Claim checked against named evidence and validation policy", ["authorized_tool_intent", "effect_receipt"]),
    ("authorized_tool_intent", "Scoped, policy-authorized request to a deterministic tool", ["effect_receipt"]),
    ("effect_receipt", "Observed tool/effect outcome with occurrence identity", []),
]
EXTENSION_EFFECT_STATES = [
    {
        "effect_state_id": f"effect_state.{slug}", "name": name,
        "does_not_imply_state_ids": [f"effect_state.{value}" for value in does_not_imply],
        "authority_required": "separate_policy_decision" if slug == "authorized_tool_intent" else "none_or_not_applicable",
        "receipt_required": slug == "effect_receipt",
        "invariant": "State identity cannot be promoted by naming, model confidence, plan acceptance, or tool invocation alone.",
    }
    for slug, name, does_not_imply in EFFECT_STATE_SPECS
]

EXTENSION_MAPPINGS = [
    {
        "extension_mapping_id": f"extension_mapping.{row['extension_signal_id'].split('.', 1)[1]}",
        "extension_signal_id": row["extension_signal_id"],
        "extension_capability_ids": row["capability_ids"],
        "core_substrate_signal_ids": row["core_substrate_signal_ids"],
        "dependency_direction": "extension_imports_deterministic_core",
        "forbidden_reverse_dependency": True,
        "admission_rule": "Only the referenced generic deterministic substrate may inform core; model-dependent semantics remain optional extension content.",
    }
    for row in EXTENSION_SIGNALS
]

EXTENSION_DECISIONS = [
    {
        "extension_decision_id": f"extension_decision.{row['extension_signal_id'].split('.', 1)[1]}",
        "extension_signal_id": row["extension_signal_id"],
        "decision": "admit_optional_extension_only",
        "rationale": "Exact model/agent capability is retained without injecting model-dependent semantics into deterministic core domains.",
        "required_effect_state_ids": [
            "effect_state.model_output", "effect_state.agent_plan", "effect_state.validated_claim",
            "effect_state.authorized_tool_intent", "effect_state.effect_receipt",
        ],
        "decided_at": AS_OF,
    }
    for row in EXTENSION_SIGNALS
]

EXTENSION_DATASETS = {
    "change-signals": EXTENSION_SIGNALS,
    "capabilities": EXTENSION_CAPABILITIES,
    "substrate-mappings": EXTENSION_MAPPINGS,
    "effect-state-kinds": EXTENSION_EFFECT_STATES,
    "review-decisions": EXTENSION_DECISIONS,
}


SCHEMA_SPECS = {
    "monitored-subjects": ("subject_id", ["name", "subject_kind", "coverage_plane_ids"]),
    "sources": ("source_id", ["title", "canonical_url", "coverage_plane_ids", "proof_obligation_ids"]),
    "source-occurrences": ("source_occurrence_id", ["source_id", "subject_id", "endpoint"]),
    "change-types": ("change_type_id", ["name", "evidence_form", "decision_effect"]),
    "collection-runs": ("collection_run_id", ["feed_attempts", "dns_failures", "no_news_claim"]),
    "collection-attempts": ("collection_attempt_id", ["collection_run_id", "source_occurrence_id", "outcome", "interpretation"]),
    "candidate-signals": ("signal_id", ["source_ids", "coverage_plane_ids", "proof_obligation_ids", "admission_status"]),
    "verified-change-events": ("change_event_id", ["signal_ids", "coverage_plane_ids", "proof_obligation_ids", "deployed_rollout_status"]),
    "claims-evidence": ("claim_id", ["signal_id", "statement", "source_ids", "evidence_relation"]),
    "coverage-proof-mappings": ("coverage_mapping_id", ["coverage_plane_id", "source_ids", "proof_obligation_ids"]),
    "impact-mappings": ("impact_mapping_id", ["signal_id", "coverage_plane_ids", "proof_obligation_ids", "effect"]),
    "review-decisions": ("review_decision_id", ["decision", "coverage_plane_ids", "proof_obligation_ids"]),
    "migration-invalidation-triggers": ("trigger_id", ["signal_id", "actions", "invalidates", "proof_obligation_ids"]),
    "security-availability-tradeoffs": ("tradeoff_id", ["security_or_control_gain", "availability_cost_or_risk", "required_control"]),
    "watchlist": ("watch_id", ["signal_id", "missing_evidence", "exit_criteria"]),
    "supersession": ("supersession_id", ["prior_identity", "successor_identity", "prior_evidence_retained"]),
    "innovations": ("innovation_id", ["year", "source_ids", "coverage_plane_ids", "proof_obligation_ids"]),
    "gaps": ("gap_id", ["description", "status", "coverage_plane_ids", "proof_obligation_ids"]),
    "offer-observations": ("offer_observation_id", ["change_event_id", "provider_id", "qualified_offer", "proof_obligation_ids"]),
    "recurring-schedules": ("schedule_id", ["cadence", "timezone", "scope", "on_failure", "on_success_no_candidates"]),
}

EXTENSION_SCHEMA_SPECS = {
    "change-signals": ("extension_signal_id", ["capability_ids", "core_substrate_signal_ids", "dependency_direction"]),
    "capabilities": ("extension_capability_id", ["input_boundary", "output_boundary", "effect_authority", "core_substrate_signal_ids"]),
    "substrate-mappings": ("extension_mapping_id", ["extension_signal_id", "extension_capability_ids", "core_substrate_signal_ids", "dependency_direction"]),
    "effect-state-kinds": ("effect_state_id", ["name", "does_not_imply_state_ids", "invariant"]),
    "review-decisions": ("extension_decision_id", ["extension_signal_id", "decision", "required_effect_state_ids"]),
}


DATASETS = {
    "monitored-subjects": SUBJECTS,
    "sources": SOURCES,
    "source-occurrences": OCCURRENCES,
    "change-types": CHANGE_TYPES,
    "collection-runs": COLLECTION_RUNS,
    "collection-attempts": COLLECTION_ATTEMPTS,
    "candidate-signals": CANDIDATE_SIGNALS,
    "verified-change-events": VERIFIED_EVENTS,
    "claims-evidence": CLAIMS,
    "coverage-proof-mappings": COVERAGE_MAPPINGS,
    "impact-mappings": IMPACT_MAPPINGS,
    "review-decisions": REVIEW_DECISIONS,
    "migration-invalidation-triggers": TRIGGERS,
    "security-availability-tradeoffs": TRADEOFFS,
    "watchlist": WATCHLIST,
    "supersession": SUPERSESSION,
    "innovations": INNOVATIONS,
    "gaps": GAPS,
    "offer-observations": OFFER_OBSERVATIONS,
    "recurring-schedules": SCHEDULES,
}


def schema_for(title: str, identity: str, required: list[str], rows: list[dict]) -> dict:
    def type_name(value: object) -> str:
        if value is None:
            return "null"
        if isinstance(value, bool):
            return "boolean"
        if isinstance(value, int):
            return "integer"
        if isinstance(value, float):
            return "number"
        if isinstance(value, str):
            return "string"
        if isinstance(value, list):
            return "array"
        if isinstance(value, dict):
            return "object"
        raise TypeError(value)

    all_fields = sorted({field for row in rows for field in row})
    common_fields = set.intersection(*(set(row) for row in rows)) if rows else set()
    properties = {}
    for field in all_fields:
        values = [row[field] for row in rows if field in row]
        types = sorted({type_name(value) for value in values})
        declaration: dict = {"type": types[0] if len(types) == 1 else types}
        if "string" in types and len(types) == 1:
            declaration["minLength"] = 1
            if field in {"canonical_url", "endpoint"}:
                declaration["format"] = "uri"
        if "array" in types:
            item_values = [item for value in values if isinstance(value, list) for item in value]
            item_types = sorted({type_name(value) for value in item_values}) or (["string"] if field.endswith("_ids") else [])
            if item_types:
                declaration["items"] = {"type": item_types[0] if len(item_types) == 1 else item_types}
            if field.endswith("_ids"):
                declaration["uniqueItems"] = True
        properties[field] = declaration
    required_fields = sorted(common_fields | {identity, *required})
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": f"https://shannon.invalid/domain-atlas/change-intelligence/{title}.schema.json",
        "title": title, "type": "object", "additionalProperties": False,
        "required": required_fields, "properties": properties,
    }


def main() -> None:
    schema_dir = ROOT / "schemas"
    schema_dir.mkdir(parents=True, exist_ok=True)
    for name, rows in DATASETS.items():
        write_jsonl(ROOT / f"{name}.jsonl", rows)
        identity, required = SCHEMA_SPECS[name]
        write_json(schema_dir / f"{name}.schema.json", schema_for(name, identity, required, rows))

    extension_root = ROOT / "extensions" / "llm_agent"
    extension_schema_dir = extension_root / "schemas"
    extension_schema_dir.mkdir(parents=True, exist_ok=True)
    for name, rows in EXTENSION_DATASETS.items():
        write_jsonl(extension_root / f"{name}.jsonl", rows)
        identity, required = EXTENSION_SCHEMA_SPECS[name]
        write_json(
            extension_schema_dir / f"{name}.schema.json",
            schema_for(f"llm-agent-{name}", identity, required, rows),
        )
    extension_metamodel = {
        "extension_id": "san.domain-atlas.change-intelligence.extension.llm-agent",
        "edition": EDITION, "optional": True,
        "dependency_direction": "extension_imports_deterministic_core",
        "forbidden_reverse_dependency": True,
        "effect_chain_law": "model output != agent plan != validated claim != authorized tool intent != effect receipt",
        "core_imports": sorted({value for values in EXTENSION_CORE_MAPPINGS.values() for value in values}),
        "completion_claim": False,
    }
    write_json(extension_root / "metamodel.json", extension_metamodel)

    metamodel = {
        "corpus_id": "san.domain-atlas.change-intelligence", "edition": EDITION,
        "status": "candidate_open_world", "completion_claim": False,
        "laws": [
            "vendor releases are observations and never canonical semantics",
            "release note is distinct from deployed rollout",
            "documentation change is distinct from behavior change",
            "advisory is distinct from exploit evidence",
            "feature claim is distinct from qualified offer and deployed occurrence",
            "synthetic vendor benchmark is distinct from independent result",
            "collection failure is an observability gap and never no news",
            "preview is distinct from general availability",
            "LLM-specific wrappers exist only in the optional extension namespace; reusable non-LLM substrate is admitted only as a bounded core claim",
            "supersession retains prior identity and evidence",
            "unknowns remain typed gaps and block completeness claims",
        ],
        "external_registries": {
            "coverage_planes": "../../coverage-planes.jsonl",
            "compiler_proof_obligations": "../../compiler/proof-obligations.json",
        },
        "record_kinds": sorted(DATASETS),
        "optional_extension_namespaces": ["extensions/llm_agent"],
    }
    write_json(ROOT / "metamodel.json", metamodel)

    files = [ROOT / f"{name}.jsonl" for name in DATASETS]
    files += [schema_dir / f"{name}.schema.json" for name in DATASETS]
    files += [extension_root / f"{name}.jsonl" for name in EXTENSION_DATASETS]
    files += [extension_schema_dir / f"{name}.schema.json" for name in EXTENSION_DATASETS]
    files.append(extension_root / "metamodel.json")
    files.append(ROOT / "metamodel.json")
    counts = {name: len(rows) for name, rows in DATASETS.items()}
    manifest = {
        "corpus_id": metamodel["corpus_id"], "edition": EDITION,
        "generated_at": AS_OF, "generated_by": "build_corpus.py",
        "status": "candidate_open_world", "completion_claim": False,
        "false_completeness_posture": "Passing thresholds proves a reviewable finite seed and routing coverage only. It does not prove ecosystem saturation, deployed behavior, offer qualification, or canonical correctness.",
        "counts": counts,
        "optional_extension_counts": {name: len(rows) for name, rows in EXTENSION_DATASETS.items()},
        "derived_counts": {
            "authoritative_primary_sources": sum(s["authority_tier"] == "primary" for s in SOURCES),
            "source_subject_records": len(SOURCES) + len(SUBJECTS),
            "change_type_decision_mapping_records": len(CHANGE_TYPES) + len(REVIEW_DECISIONS) + len(COVERAGE_MAPPINGS) + len(IMPACT_MAPPINGS),
            "innovations_2021_2026_non_llm": sum(2021 <= i["year"] <= 2026 and i["llm_dependency"] == "none" for i in INNOVATIONS),
            "coverage_planes_mapped": len({m["coverage_plane_id"] for m in COVERAGE_MAPPINGS}),
            "proof_obligations_referenced": len({p for rows in DATASETS.values() for row in rows for p in row.get("proof_obligation_ids", [])}),
            "dns_failures": sum(a["failure_class"] == "dns_resolution" for a in COLLECTION_ATTEMPTS),
            "admitted_signals": sum(s["admission_status"].startswith("admitted") for s in CANDIDATE_SIGNALS),
            "core_llm_specific_signals": sum(s["llm_posture"] == "llm_specific" for s in CANDIDATE_SIGNALS),
            "optional_extension_signals": len(EXTENSION_SIGNALS),
        },
        "quality_gates": {
            "authoritative_primary_sources_min": 60,
            "source_subject_records_min": 80,
            "change_type_decision_mapping_records_min": 100,
            "innovations_2021_2026_non_llm_min": 20,
            "coverage_planes_exact": len(PLANE_IDS),
        },
        "file_sha256": {str(path.relative_to(ROOT)): digest(path) for path in sorted(files)},
    }
    write_json(ROOT / "manifest.json", manifest)


if __name__ == "__main__":
    main()
