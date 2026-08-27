#!/usr/bin/env python3
"""Deterministically build the provider/target physical-binding research registry."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SCHEMA = ROOT / "schema"
EDITION = 1
RETRIEVED = "2026-08-25"
LP_RECEIPTS_PATH = "research/domain_atlas/compiler/conformance_evaluation/executions/lp_solver_exact_scope/runs/run-20260826-macos-arm64-python3_14-001/qualification-receipts.jsonl"
LP_COHABITATION_PATH = "research/domain_atlas/compiler/conformance_evaluation/executions/lp_solver_exact_scope/runs/run-20260826-macos-arm64-python3_14-001/cohabitation-negative-twin.json"
CPSAT_RECEIPTS_FAILED_ENUMERATION_PATH = "research/domain_atlas/compiler/conformance_evaluation/executions/cp_sat_exact_scope/runs/run-20260826-cpsat-macos-arm64-python3_14-001/qualification-receipts.jsonl"
CPSAT_RECEIPTS_CORRECTED_PATH = "research/domain_atlas/compiler/conformance_evaluation/executions/cp_sat_exact_scope/runs/run-20260826-cpsat-macos-arm64-python3_14-002/qualification-receipts.jsonl"


def dump_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def dump_jsonl(path: Path, records: list[dict]) -> None:
    path.write_text("".join(json.dumps(record, sort_keys=True) + "\n" for record in records))


def strings() -> dict:
    return {"type": "array", "items": {"type": "string"}, "uniqueItems": True}


def record_schema(title: str, id_field: str, required: list[str], properties: dict) -> dict:
    common = {
        id_field: {"type": "string", "pattern": "^[a-z][a-z0-9_.-]+$"},
        "edition": {"type": "integer", "minimum": 1},
        "status": {"type": "string", "minLength": 1},
    }
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": f"https://san.example/spec/provider-target/{id_field}-v1.schema.json",
        "title": title,
        "type": "object",
        "additionalProperties": False,
        "required": [id_field, "edition", "status", *required],
        "properties": {**common, **properties},
    }


def build_schemas() -> None:
    SCHEMA.mkdir(exist_ok=True)
    date = {"type": "string", "format": "date"}
    ref = {"type": "string", "pattern": "^[a-z][a-z0-9_.-]+$"}
    refs = {"type": "array", "items": ref, "uniqueItems": True}
    schemas = {
        "source": record_schema("Primary or official evidence source", "source_id", ["title", "publisher", "url", "source_kind", "primary_official", "authority_scope", "supports", "retrieved_at", "mutable"], {
            "title": {"type": "string", "minLength": 1}, "publisher": {"type": "string", "minLength": 1},
            "url": {"type": "string", "format": "uri"}, "source_kind": {"enum": ["standard", "official_specification", "official_documentation", "official_release", "official_pricing", "official_source"]},
            "primary_official": {"const": True}, "authority_scope": {"type": "string", "minLength": 1}, "supports": strings(),
            "retrieved_at": date, "published_at": {"type": ["string", "null"], "format": "date"}, "mutable": {"type": "boolean"},
            "limitations": strings(),
        }),
        "context": record_schema("Provider-target bounded-context candidate", "context_id", ["name", "inside", "outside", "invariants", "evidence_refs", "gaps"], {
            "name": {"type": "string"}, "inside": strings(), "outside": strings(), "invariants": strings(), "evidence_refs": refs, "gaps": strings(),
        }),
        "capability-class": record_schema("Provider-neutral capability class", "capability_class_id", ["family", "name", "definition", "required_surfaces", "non_semantic_owner", "evidence_refs"], {
            "family": {"type": "string"}, "name": {"type": "string"}, "definition": {"type": "string"}, "required_surfaces": strings(),
            "non_semantic_owner": {"const": True}, "evidence_refs": refs, "parent_refs": refs,
        }),
        "provider-class": record_schema("Provider-neutral provider class", "provider_class_id", ["name", "role", "may_offer", "must_not_own", "evidence_refs"], {
            "name": {"type": "string"}, "role": {"type": "string"}, "may_offer": refs, "must_not_own": strings(), "evidence_refs": refs,
        }),
        "provider-organization": record_schema("Provider organization identity", "provider_organization_id", ["name", "organization_kind", "provider_class_refs", "semantic_ownership_forbidden", "evidence_refs"], {
            "name": {"type": "string"}, "organization_kind": {"type": "string"}, "provider_class_refs": refs, "semantic_ownership_forbidden": {"const": True}, "evidence_refs": refs,
        }),
        "implementation-artifact": record_schema("Implementation artifact identity", "artifact_id", ["name", "artifact_kind", "maintainer_ref", "version_scheme", "capability_class_refs", "library_or_engine_or_service", "evidence_refs"], {
            "name": {"type": "string"}, "artifact_kind": {"type": "string"}, "maintainer_ref": ref, "version_scheme": {"type": "string"},
            "capability_class_refs": refs, "library_or_engine_or_service": {"enum": ["library", "engine", "runtime", "orchestrator", "protocol", "service", "hardware_isa", "storage_system"]}, "evidence_refs": refs,
        }),
        "concrete-offer": record_schema("Versioned concrete capability offer", "offer_id", ["provider_organization_ref", "provider_class_ref", "artifact_ref", "artifact_version", "offer_snapshot", "offer_kind", "capability_class_refs", "target_profile_refs", "guarantees", "exclusions", "documented_limit_refs", "evidence_refs", "retrieved_at", "observed_at", "validity", "binding_eligible"], {
            "provider_organization_ref": ref, "provider_class_ref": ref, "artifact_ref": ref, "artifact_version": {"type": "string", "minLength": 1}, "offer_snapshot": {"type": "string", "minLength": 1},
            "offer_kind": {"type": "string"}, "capability_class_refs": refs, "target_profile_refs": refs, "guarantees": strings(), "exclusions": strings(),
            "documented_limit_refs": refs, "evidence_refs": refs, "retrieved_at": date, "observed_at": date, "binding_eligible": {"type": "boolean"},
            "validity": {"type": "object", "additionalProperties": False, "required": ["scope", "recheck_triggers"], "properties": {"scope": {"type": "string"}, "recheck_triggers": strings()}},
        }),
        "target-profile": record_schema("Provider-neutral target profile", "target_profile_id", ["name", "target_class", "runtime_layers", "resource_dimensions", "location_posture", "binding_requirements", "evidence_refs"], {
            "name": {"type": "string"}, "target_class": {"type": "string"}, "runtime_layers": strings(), "resource_dimensions": strings(), "location_posture": {"type": "string"}, "binding_requirements": strings(), "evidence_refs": refs,
        }),
        "target-occurrence": record_schema("Concrete target occurrence or evidence snapshot", "target_occurrence_id", ["target_profile_ref", "provider_organization_ref", "offer_ref", "occurrence_kind", "location", "configuration_fingerprint", "artifact_versions", "finite_budget", "availability_regions", "residency_guarantee", "observed_at", "retrieved_at", "evidence_refs", "binding_eligible"], {
            "target_profile_ref": ref, "provider_organization_ref": ref, "offer_ref": ref, "occurrence_kind": {"enum": ["documented_offer_snapshot", "registered_deployment", "probe_fixture"]},
            "location": {"type": "object"}, "configuration_fingerprint": {"type": "string"}, "artifact_versions": {"type": "object"},
            "finite_budget": {"type": "object", "additionalProperties": {"type": ["number", "integer", "string"]}}, "availability_regions": strings(),
            "residency_guarantee": {"type": ["string", "null"]}, "observed_at": date, "retrieved_at": date, "evidence_refs": refs, "binding_eligible": {"type": "boolean"},
        }),
        "resource-evidence": record_schema("Resource, limit or cost evidence", "resource_evidence_id", ["evidence_kind", "subject_ref", "metric", "value", "unit", "scope", "method", "source_refs", "observed_at", "retrieved_at", "binding_eligible", "recheck_triggers"], {
            "evidence_kind": {"enum": ["documented_limit", "probed_limit", "list_price", "measured_cost", "observed_usage", "quota_observation"]}, "subject_ref": ref,
            "metric": {"type": "string"}, "value": {"type": ["number", "integer", "string", "null"]}, "unit": {"type": "string"}, "scope": {"type": "string"}, "method": {"type": "string"},
            "source_refs": refs, "observed_at": date, "retrieved_at": date, "binding_eligible": {"type": "boolean"}, "recheck_triggers": strings(),
        }),
        "qualification-receipt": record_schema("Scoped qualification receipt", "qualification_receipt_id", ["subject_ref", "target_occurrence_ref", "capability_class_refs", "semantic_conformance", "performance_result", "outcome", "evidence_class", "independent_appraisal", "test_or_oracle", "evidence_refs", "evidence_object_refs", "execution_receipt_refs", "observed_at", "invalidation_triggers"], {
            "subject_ref": ref, "target_occurrence_ref": ref, "capability_class_refs": refs, "semantic_conformance": {"enum": ["pass", "fail", "inconclusive", "not_tested"]},
            "performance_result": {"enum": ["pass", "fail", "inconclusive", "not_tested"]}, "outcome": {"enum": ["qualified", "rejected", "inconclusive"]},
            "evidence_class": {"enum": ["documentation_review", "executed_test", "independently_appraised_test"]}, "independent_appraisal": {"type": "boolean"},
            "test_or_oracle": {"type": "string"}, "evidence_refs": refs, "evidence_object_refs": strings(), "execution_receipt_refs": refs,
            "observed_at": date, "invalidation_triggers": strings(),
        }),
        "compatibility": record_schema("Scoped compatibility matrix cell", "compatibility_id", ["left_ref", "right_ref", "capability_class_ref", "result", "conditions", "evidence_refs", "evidence_object_refs", "observed_at", "invalidation_triggers"], {
            "left_ref": ref, "right_ref": ref, "capability_class_ref": ref, "result": {"enum": ["compatible", "incompatible", "conditional", "unknown"]}, "conditions": strings(), "evidence_refs": refs, "observed_at": date, "invalidation_triggers": strings(),
            "evidence_object_refs": strings(),
        }),
        "decision": record_schema("Physical-binding decision point", "decision_id", ["question", "allowed_values", "binding_phase", "authority", "default_law", "required_evidence", "change_semantics"], {
            "question": {"type": "string"}, "allowed_values": strings(), "binding_phase": {"enum": ["physical_binding", "deployment_binding", "runtime_reconciliation", "evidence_verification"]},
            "authority": {"type": "string"}, "default_law": {"enum": ["forbidden", "explicit_safe_constant", "runtime_observed_with_receipt"]}, "required_evidence": strings(), "change_semantics": strings(),
        }),
        "rule": record_schema("Refusal or invalidation rule", "rule_id", ["rule_kind", "when", "must", "otherwise", "typed_degradation"], {
            "rule_kind": {"enum": ["refusal", "invalidation"]}, "when": {"type": "string"}, "must": {"type": "string"}, "otherwise": {"type": "string"}, "typed_degradation": {"enum": ["forbidden", "only_if_declared"]},
        }),
        "compiler-mapping": record_schema("Compiler requirement/offer mapping", "mapping_id", ["requirement_id", "capability_class_refs", "required_guarantees", "prohibited_traits", "finite_budget_dimensions", "offer_candidate_refs", "evidence_gates", "fallback_law", "invalidation_rule_refs"], {
            "requirement_id": ref, "capability_class_refs": refs, "required_guarantees": strings(), "prohibited_traits": strings(), "finite_budget_dimensions": strings(),
            "offer_candidate_refs": refs, "evidence_gates": strings(), "fallback_law": {"enum": ["refuse", "typed_degradation_only_if_declared"]}, "invalidation_rule_refs": refs,
        }),
        "library-boundary": record_schema("Library or provider-adapter boundary", "boundary_id", ["name", "boundary_kind", "owns", "must_not_own", "effects", "configuration_surface", "receipt_surface", "evidence_refs"], {
            "name": {"type": "string"}, "boundary_kind": {"enum": ["pure_library", "runtime_library", "provider_adapter", "engine_integration"]}, "owns": strings(), "must_not_own": strings(),
            "effects": {"type": "string"}, "configuration_surface": strings(), "receipt_surface": strings(), "evidence_refs": refs,
        }),
        "innovation": record_schema("Recent non-generative innovation", "innovation_id", ["name", "year", "why_material", "affected_capability_refs", "non_llm", "evidence_refs"], {
            "name": {"type": "string"}, "year": {"type": "integer", "minimum": 2021, "maximum": 2026}, "why_material": {"type": "string"}, "affected_capability_refs": refs, "non_llm": {"const": True}, "evidence_refs": refs,
        }),
        "gap": record_schema("Open physical-binding gap", "gap_id", ["gap_kind", "subject_ref", "blocking", "known", "unknown", "resolution_condition", "prohibited_assumption", "evidence_refs"], {
            "gap_kind": {"type": "string"}, "subject_ref": ref, "blocking": {"type": "boolean"}, "known": {"type": "string"}, "unknown": {"type": "string"}, "resolution_condition": {"type": "string"}, "prohibited_assumption": {"type": "string"}, "evidence_refs": refs,
        }),
    }
    for name, schema in schemas.items():
        dump_json(SCHEMA / f"{name}.schema.json", schema)


SOURCE_ROWS = [
    # id, publisher, title, url, kind, mutable, topics
    ("src.ptr.posix.process", "The Open Group", "POSIX process interfaces", "https://pubs.opengroup.org/onlinepubs/9799919799/functions/exec.html", "standard", False, ["native", "process"]),
    ("src.ptr.posix.fsync", "The Open Group", "POSIX fsync", "https://pubs.opengroup.org/onlinepubs/9799919799/functions/fsync.html", "standard", False, ["file_storage", "durability"]),
    ("src.ptr.posix.rename", "The Open Group", "POSIX rename", "https://pubs.opengroup.org/onlinepubs/9799919799/functions/rename.html", "standard", False, ["file_storage", "atomic_namespace"]),
    ("src.ptr.linux.cgroup2", "Linux kernel", "Control Group v2", "https://docs.kernel.org/admin-guide/cgroup-v2.html", "official_documentation", True, ["resources", "isolation"]),
    ("src.ptr.linux.io_uring", "Linux kernel", "io_uring", "https://docs.kernel.org/io_uring/", "official_documentation", True, ["io", "async"]),
    ("src.ptr.linux.seccomp", "Linux kernel", "Seccomp BPF", "https://docs.kernel.org/userspace-api/seccomp_filter.html", "official_documentation", True, ["sandbox", "process"]),
    ("src.ptr.oci.runtime", "Open Container Initiative", "OCI Runtime Specification", "https://specs.opencontainers.org/runtime/", "official_specification", True, ["container", "runtime"]),
    ("src.ptr.oci.image", "Open Container Initiative", "OCI Image Specification", "https://specs.opencontainers.org/image-spec/", "official_specification", True, ["container", "artifact"]),
    ("src.ptr.k8s.resources", "Kubernetes", "Resource management for pods and containers", "https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/", "official_documentation", True, ["kubernetes", "resource_limits"]),
    ("src.ptr.k8s.scheduler", "Kubernetes", "Kubernetes scheduler", "https://kubernetes.io/docs/concepts/scheduling-eviction/kube-scheduler/", "official_documentation", True, ["kubernetes", "scheduler"]),
    ("src.ptr.k8s.job", "Kubernetes", "Jobs", "https://kubernetes.io/docs/concepts/workloads/controllers/job/", "official_documentation", True, ["kubernetes", "batch"]),
    ("src.ptr.k8s.device", "Kubernetes", "Device plugins", "https://kubernetes.io/docs/concepts/extend-kubernetes/compute-storage-net/device-plugins/", "official_documentation", True, ["kubernetes", "accelerator"]),
    ("src.ptr.k8s.topology", "Kubernetes", "Node topology manager", "https://kubernetes.io/docs/tasks/administer-cluster/topology-manager/", "official_documentation", True, ["kubernetes", "numa"]),
    ("src.ptr.k8s.dra", "Kubernetes", "Dynamic Resource Allocation", "https://kubernetes.io/docs/concepts/scheduling-eviction/dynamic-resource-allocation/", "official_documentation", True, ["kubernetes", "accelerator", "innovation"]),
    ("src.ptr.wasm.core3", "WebAssembly Community Group", "WebAssembly Core Specification 3.0", "https://webassembly.github.io/spec/core/index.html", "official_specification", False, ["wasm", "runtime"]),
    ("src.ptr.wasi", "Bytecode Alliance", "WASI specifications", "https://wasi.dev/", "official_specification", True, ["wasm", "io"]),
    ("src.ptr.component", "Bytecode Alliance", "WebAssembly Component Model", "https://component-model.bytecodealliance.org/", "official_specification", True, ["wasm", "component"]),
    ("src.ptr.wasmtime", "Bytecode Alliance", "Wasmtime documentation", "https://docs.wasmtime.dev/", "official_documentation", True, ["wasm", "runtime"]),
    ("src.ptr.java25", "Oracle", "Java SE and JDK 25 specifications", "https://docs.oracle.com/en/java/javase/25/docs/specs/index.html", "official_specification", False, ["jvm", "java"]),
    ("src.ptr.java26", "Oracle", "Java SE 26 specification index", "https://docs.oracle.com/javase/specs/", "official_specification", True, ["jvm", "java"]),
    ("src.ptr.java.virtual_threads", "OpenJDK", "JEP 444 Virtual Threads", "https://openjdk.org/jeps/444", "official_specification", False, ["jvm", "scheduler", "innovation"]),
    ("src.ptr.java.vector", "OpenJDK", "JEP 460 Vector API", "https://openjdk.org/jeps/460", "official_specification", False, ["jvm", "simd", "innovation"]),
    ("src.ptr.python314", "Python Software Foundation", "Python 3.14 documentation", "https://docs.python.org/3.14/", "official_documentation", True, ["python", "runtime"]),
    ("src.ptr.python.capi", "Python Software Foundation", "Python 3.14 C API", "https://docs.python.org/3.14/c-api/index.html", "official_documentation", True, ["python", "native_extension"]),
    ("src.ptr.python.free_threading", "Python Software Foundation", "Python free-threading HOWTO", "https://docs.python.org/3.14/howto/free-threading-python.html", "official_documentation", True, ["python", "parallelism", "innovation"]),
    ("src.ptr.openmp", "OpenMP ARB", "OpenMP API specification", "https://www.openmp.org/specifications/", "standard", True, ["cpu", "parallelism"]),
    ("src.ptr.mpi", "MPI Forum", "MPI standard", "https://www.mpi-forum.org/docs/", "standard", True, ["distributed", "message_passing"]),
    ("src.ptr.x86", "Intel", "Intel 64 and IA-32 architectures manuals", "https://www.intel.com/content/www/us/en/developer/articles/technical/intel-sdm.html", "official_specification", True, ["cpu", "simd"]),
    ("src.ptr.arm", "Arm", "Arm architecture reference manuals", "https://developer.arm.com/Architectures", "official_specification", True, ["cpu", "simd"]),
    ("src.ptr.riscv", "RISC-V International", "RISC-V ISA specifications", "https://riscv.org/specifications/ratified/", "standard", True, ["cpu", "vector"]),
    ("src.ptr.llvm.vectorizer", "LLVM Project", "LLVM auto-vectorization", "https://llvm.org/docs/Vectorizers.html", "official_documentation", True, ["compiler", "simd"]),
    ("src.ptr.cuda", "NVIDIA", "CUDA C++ programming guide", "https://docs.nvidia.com/cuda/cuda-c-programming-guide/", "official_documentation", True, ["gpu", "accelerator"]),
    ("src.ptr.cuda.mig", "NVIDIA", "Multi-Instance GPU", "https://docs.nvidia.com/datacenter/tesla/mig-user-guide/", "official_documentation", True, ["gpu", "partitioning", "innovation"]),
    ("src.ptr.rocm", "AMD", "ROCm documentation", "https://rocm.docs.amd.com/", "official_documentation", True, ["gpu", "accelerator"]),
    ("src.ptr.levelzero", "oneAPI", "Level Zero specification", "https://oneapi-src.github.io/level-zero-spec/level-zero/latest/index.html", "official_specification", True, ["accelerator", "api"]),
    ("src.ptr.sycl", "Khronos Group", "SYCL specification", "https://registry.khronos.org/SYCL/", "standard", True, ["accelerator", "portability"]),
    ("src.ptr.opencl", "Khronos Group", "OpenCL specification", "https://registry.khronos.org/OpenCL/", "standard", True, ["accelerator", "portability"]),
    ("src.ptr.metal", "Apple", "Metal documentation", "https://developer.apple.com/documentation/metal", "official_documentation", True, ["gpu", "accelerator"]),
    ("src.ptr.nvme", "NVM Express", "NVMe specifications", "https://nvmexpress.org/specifications/", "standard", True, ["block_storage", "io"]),
    ("src.ptr.nfs41", "IETF", "RFC 8881 NFSv4.1", "https://www.rfc-editor.org/rfc/rfc8881.html", "standard", False, ["file_storage", "network"]),
    ("src.ptr.s3", "Amazon Web Services", "Amazon S3 user guide", "https://docs.aws.amazon.com/AmazonS3/latest/userguide/Welcome.html", "official_documentation", True, ["object_storage", "managed_service"]),
    ("src.ptr.s3.conditional", "Amazon Web Services", "Amazon S3 conditional requests", "https://docs.aws.amazon.com/AmazonS3/latest/userguide/conditional-requests.html", "official_documentation", True, ["object_storage", "conditional_write"]),
    ("src.ptr.s3.pricing", "Amazon Web Services", "Amazon S3 pricing", "https://aws.amazon.com/s3/pricing/", "official_pricing", True, ["object_storage", "list_price"]),
    ("src.ptr.gcs.consistency", "Google Cloud", "Cloud Storage consistency", "https://cloud.google.com/storage/docs/consistency", "official_documentation", True, ["object_storage", "consistency"]),
    ("src.ptr.gcs.pricing", "Google Cloud", "Cloud Storage pricing", "https://cloud.google.com/storage/pricing", "official_pricing", True, ["object_storage", "list_price"]),
    ("src.ptr.azure.blob", "Microsoft", "Azure Blob Storage introduction", "https://learn.microsoft.com/en-us/azure/storage/blobs/storage-blobs-introduction", "official_documentation", True, ["object_storage", "managed_service"]),
    ("src.ptr.azure.storage.pricing", "Microsoft", "Azure Blob Storage pricing", "https://azure.microsoft.com/en-us/pricing/details/storage/blobs/", "official_pricing", True, ["object_storage", "list_price"]),
    ("src.ptr.ceph", "Ceph", "Ceph architecture", "https://docs.ceph.com/en/latest/architecture/", "official_documentation", True, ["object_storage", "block_storage", "file_storage"]),
    ("src.ptr.ebs", "Amazon Web Services", "Amazon EBS volumes", "https://docs.aws.amazon.com/ebs/latest/userguide/ebs-volumes.html", "official_documentation", True, ["block_storage", "managed_service"]),
    ("src.ptr.gcp.pd", "Google Cloud", "Persistent Disk", "https://cloud.google.com/compute/docs/disks/persistent-disks", "official_documentation", True, ["block_storage", "managed_service"]),
    ("src.ptr.azure.disks", "Microsoft", "Azure managed disk types", "https://learn.microsoft.com/en-us/azure/virtual-machines/disks-types", "official_documentation", True, ["block_storage", "managed_service"]),
    ("src.ptr.kafka", "Apache Software Foundation", "Apache Kafka documentation", "https://kafka.apache.org/documentation/", "official_documentation", True, ["messaging", "stream"]),
    ("src.ptr.pulsar", "Apache Software Foundation", "Apache Pulsar concepts", "https://pulsar.apache.org/docs/next/concepts-overview/", "official_documentation", True, ["messaging", "stream"]),
    ("src.ptr.rabbitmq", "Broadcom RabbitMQ", "RabbitMQ reliability guide", "https://www.rabbitmq.com/docs/reliability", "official_documentation", True, ["messaging", "queue"]),
    ("src.ptr.nats", "Synadia", "JetStream documentation", "https://docs.nats.io/nats-concepts/jetstream", "official_documentation", True, ["messaging", "stream"]),
    ("src.ptr.flink", "Apache Software Foundation", "Apache Flink architecture", "https://nightlies.apache.org/flink/flink-docs-stable/docs/concepts/flink-architecture/", "official_documentation", True, ["stream", "batch"]),
    ("src.ptr.flink2", "Apache Software Foundation", "Apache Flink 2.0 release", "https://flink.apache.org/2025/03/24/apache-flink-2.0.0-a-new-era-of-real-time-data-processing/", "official_release", False, ["stream", "innovation"]),
    ("src.ptr.spark", "Apache Software Foundation", "Apache Spark documentation", "https://spark.apache.org/docs/latest/", "official_documentation", True, ["batch", "stream", "engine"]),
    ("src.ptr.spark4", "Apache Software Foundation", "Apache Spark 4.0.0 release", "https://spark.apache.org/releases/spark-release-4-0-0.html", "official_release", False, ["batch", "engine", "innovation"]),
    ("src.ptr.beam", "Apache Software Foundation", "Apache Beam model", "https://beam.apache.org/documentation/basics/", "official_documentation", True, ["batch", "stream", "portability"]),
    ("src.ptr.ray", "Anyscale Ray project", "Ray Core documentation", "https://docs.ray.io/en/latest/ray-core/walkthrough.html", "official_documentation", True, ["distributed", "scheduler"]),
    ("src.ptr.airflow", "Apache Software Foundation", "Apache Airflow scheduler", "https://airflow.apache.org/docs/apache-airflow/stable/administration-and-deployment/scheduler.html", "official_documentation", True, ["scheduler", "batch"]),
    ("src.ptr.argo", "Cloud Native Computing Foundation", "Argo Workflows", "https://argo-workflows.readthedocs.io/en/latest/", "official_documentation", True, ["scheduler", "kubernetes"]),
    ("src.ptr.postgres18", "PostgreSQL Global Development Group", "PostgreSQL 18 documentation", "https://www.postgresql.org/docs/18/", "official_documentation", True, ["relational", "engine"]),
    ("src.ptr.duckdb", "DuckDB Foundation", "DuckDB documentation", "https://duckdb.org/docs/stable/", "official_documentation", True, ["relational", "query_engine"]),
    ("src.ptr.datafusion", "Apache Software Foundation", "Apache DataFusion documentation", "https://datafusion.apache.org/", "official_documentation", True, ["query_engine", "library"]),
    ("src.ptr.trino", "Trino Software Foundation", "Trino documentation", "https://trino.io/docs/current/", "official_documentation", True, ["distributed_query", "federation"]),
    ("src.ptr.clickhouse", "ClickHouse", "ClickHouse documentation", "https://clickhouse.com/docs", "official_documentation", True, ["warehouse", "query_engine"]),
    ("src.ptr.iceberg", "Apache Software Foundation", "Apache Iceberg specification", "https://iceberg.apache.org/spec/", "official_specification", True, ["lakehouse", "table_format"]),
    ("src.ptr.delta", "Linux Foundation", "Delta Lake protocol", "https://github.com/delta-io/delta/blob/master/PROTOCOL.md", "official_specification", True, ["lakehouse", "table_format"]),
    ("src.ptr.hudi", "Apache Software Foundation", "Apache Hudi technical specification", "https://hudi.apache.org/tech-specs/", "official_specification", True, ["lakehouse", "table_format"]),
    ("src.ptr.lambda.quotas", "Amazon Web Services", "Lambda quotas", "https://docs.aws.amazon.com/lambda/latest/dg/gettingstarted-limits.html", "official_documentation", True, ["serverless", "documented_limit"]),
    ("src.ptr.lambda.pricing", "Amazon Web Services", "AWS Lambda pricing", "https://aws.amazon.com/lambda/pricing/", "official_pricing", True, ["serverless", "list_price"]),
    ("src.ptr.cloudrun.quotas", "Google Cloud", "Cloud Run quotas and limits", "https://cloud.google.com/run/quotas", "official_documentation", True, ["serverless", "container", "documented_limit"]),
    ("src.ptr.cloudrun.pricing", "Google Cloud", "Cloud Run pricing", "https://cloud.google.com/run/pricing", "official_pricing", True, ["serverless", "list_price"]),
    ("src.ptr.azure.functions", "Microsoft", "Azure Functions scale and hosting", "https://learn.microsoft.com/en-us/azure/azure-functions/functions-scale", "official_documentation", True, ["serverless", "documented_limit"]),
    ("src.ptr.azure.functions.pricing", "Microsoft", "Azure Functions pricing", "https://azure.microsoft.com/en-us/pricing/details/functions/", "official_pricing", True, ["serverless", "list_price"]),
    ("src.ptr.awsbatch", "Amazon Web Services", "AWS Batch user guide", "https://docs.aws.amazon.com/batch/latest/userguide/what-is-batch.html", "official_documentation", True, ["managed_batch", "scheduler"]),
    ("src.ptr.gcpbatch", "Google Cloud", "Batch documentation", "https://cloud.google.com/batch/docs/get-started", "official_documentation", True, ["managed_batch", "scheduler"]),
    ("src.ptr.azurebatch", "Microsoft", "Azure Batch overview", "https://learn.microsoft.com/en-us/azure/batch/batch-technical-overview", "official_documentation", True, ["managed_batch", "scheduler"]),
    ("src.ptr.bigquery.quotas", "Google Cloud", "BigQuery quotas and limits", "https://cloud.google.com/bigquery/quotas", "official_documentation", True, ["warehouse", "documented_limit"]),
    ("src.ptr.bigquery.locations", "Google Cloud", "BigQuery locations", "https://cloud.google.com/bigquery/docs/locations", "official_documentation", True, ["warehouse", "availability_region"]),
    ("src.ptr.redshift.quotas", "Amazon Web Services", "Amazon Redshift quotas", "https://docs.aws.amazon.com/redshift/latest/mgmt/amazon-redshift-limits.html", "official_documentation", True, ["warehouse", "documented_limit"]),
    ("src.ptr.snowflake.limits", "Snowflake", "Snowflake limits", "https://docs.snowflake.com/en/user-guide/limitations", "official_documentation", True, ["warehouse", "documented_limit"]),
    ("src.ptr.databricks.sql", "Databricks", "SQL warehouse types", "https://docs.databricks.com/aws/en/compute/sql-warehouse/warehouse-types", "official_documentation", True, ["warehouse", "managed_service"]),
    ("src.ptr.eks", "Amazon Web Services", "Amazon EKS user guide", "https://docs.aws.amazon.com/eks/latest/userguide/what-is-eks.html", "official_documentation", True, ["managed_kubernetes", "cloud"]),
    ("src.ptr.gke", "Google Cloud", "GKE documentation", "https://cloud.google.com/kubernetes-engine/docs/concepts/kubernetes-engine-overview", "official_documentation", True, ["managed_kubernetes", "cloud"]),
    ("src.ptr.aks", "Microsoft", "AKS core concepts", "https://learn.microsoft.com/en-us/azure/aks/core-aks-concepts", "official_documentation", True, ["managed_kubernetes", "cloud"]),
    ("src.ptr.tcp", "IETF", "RFC 9293 TCP", "https://www.rfc-editor.org/rfc/rfc9293.html", "standard", False, ["network", "transport"]),
    ("src.ptr.quic", "IETF", "RFC 9000 QUIC", "https://www.rfc-editor.org/rfc/rfc9000.html", "standard", False, ["network", "transport", "innovation"]),
    ("src.ptr.dpdk", "DPDK Project", "DPDK programmer guide", "https://doc.dpdk.org/guides/prog_guide/", "official_documentation", True, ["network", "userspace_io"]),
    ("src.ptr.spdk", "SPDK Project", "SPDK documentation", "https://spdk.io/doc/", "official_documentation", True, ["storage", "userspace_io"]),
    ("src.ptr.aws.regions", "Amazon Web Services", "AWS Regions and Availability Zones", "https://docs.aws.amazon.com/global-infrastructure/latest/regions/aws-regions-availability-zones.html", "official_documentation", True, ["availability_region", "cloud"]),
    ("src.ptr.gcp.locations", "Google Cloud", "Cloud locations", "https://cloud.google.com/about/locations", "official_documentation", True, ["availability_region", "cloud"]),
    ("src.ptr.azure.geographies", "Microsoft", "Azure geographies", "https://azure.microsoft.com/en-us/explore/global-infrastructure/geographies/", "official_documentation", True, ["availability_region", "cloud"]),
    ("src.ptr.aws.residency", "Amazon Web Services", "AWS data residency", "https://aws.amazon.com/compliance/data-residency/", "official_documentation", True, ["residency", "cloud"]),
    ("src.ptr.gcp.residency", "Google Cloud", "Data residency", "https://cloud.google.com/security/compliance/data-residency", "official_documentation", True, ["residency", "cloud"]),
    ("src.ptr.azure.residency", "Microsoft", "Azure data residency", "https://learn.microsoft.com/en-us/azure/security/fundamentals/data-residency", "official_documentation", True, ["residency", "cloud"]),
    ("src.ptr.outposts", "Amazon Web Services", "AWS Outposts", "https://docs.aws.amazon.com/outposts/latest/userguide/what-is-outposts.html", "official_documentation", True, ["edge", "on_prem"]),
    ("src.ptr.gdc.airgap", "Google Cloud", "Google Distributed Cloud air-gapped", "https://cloud.google.com/distributed-cloud/hosted/docs/latest/gdch/overview", "official_documentation", True, ["air_gapped", "sovereign"]),
    ("src.ptr.azure.stack", "Microsoft", "Azure Stack Hub overview", "https://learn.microsoft.com/en-us/azure-stack/operator/azure-stack-overview", "official_documentation", True, ["edge", "on_prem"]),
    ("src.ptr.cxl3", "Compute Express Link Consortium", "CXL 3.0 specification release", "https://computeexpresslink.org/cxl-specification/", "standard", True, ["memory", "fabric", "innovation"]),
    ("src.ptr.pcie6", "PCI-SIG", "PCI Express 6.0 specification", "https://pcisig.com/pci-express-6.0-specification", "standard", False, ["io", "fabric", "innovation"]),
    ("src.ptr.arrow.device", "Apache Software Foundation", "Arrow C Device Data Interface", "https://arrow.apache.org/docs/format/CDeviceDataInterface.html", "official_specification", True, ["gpu", "zero_copy", "innovation"]),
    ("src.ptr.substrait", "Substrait", "Substrait specification", "https://substrait.io/spec/specification/", "official_specification", True, ["query_ir", "portability"]),
    ("src.ptr.ortools.release.9_15", "Google OR-Tools", "OR-Tools v9.15 release", "https://github.com/google/or-tools/releases/tag/v9.15", "official_release", False, ["optimization", "linear_programming", "release"]),
    ("src.ptr.ortools.glop_mpsolver_status.9_15", "Google OR-Tools", "GLOP to MPSolver status mapping at v9.15", "https://github.com/google/or-tools/blob/v9.15/ortools/linear_solver/proto_solver/glop_proto_solver.cc", "official_source", False, ["optimization", "linear_programming", "status_mapping"]),
    ("src.ptr.ortools.cp_sat.9_15", "Google OR-Tools", "CP-SAT solver documentation", "https://developers.google.com/optimization/cp/cp_solver", "official_documentation", True, ["optimization", "constraint_programming", "integer_model", "status_mapping"]),
    ("src.ptr.ortools.cp_model_proto.9_15", "Google OR-Tools", "CP-SAT model and response protocol at v9.15", "https://github.com/google/or-tools/blob/v9.15/ortools/sat/cp_model.proto", "official_source", False, ["optimization", "constraint_programming", "model_protocol"]),
    ("src.ptr.ortools.sat_parameters.9_15", "Google OR-Tools", "CP-SAT parameter protocol at v9.15", "https://github.com/google/or-tools/blob/v9.15/ortools/sat/sat_parameters.proto", "official_source", False, ["optimization", "constraint_programming", "enumeration", "limits"]),
    ("src.ptr.highs.release.1_15_1", "HiGHS", "HiGHS v1.15.1 release", "https://github.com/ERGO-Code/HiGHS/releases/tag/v1.15.1", "official_release", False, ["optimization", "linear_programming", "release"]),
    ("src.ptr.highs.python", "HiGHS", "HiGHS Python interface", "https://ergo-code.github.io/HiGHS/stable/interfaces/python/", "official_documentation", True, ["optimization", "linear_programming", "python"]),
    ("src.ptr.highs.model_status", "HiGHS", "HiGHS model-status enumeration", "https://ergo-code.github.io/HiGHS/stable/interfaces/python/enums/", "official_documentation", True, ["optimization", "linear_programming", "status_mapping"]),
]


def source_records() -> list[dict]:
    return [{
        "source_id": sid, "edition": EDITION, "status": "reviewed", "title": title, "publisher": publisher,
        "url": url, "source_kind": kind, "primary_official": True,
        "authority_scope": "Authoritative only for the named standard, implementation, release, service documentation or price page at the retrieved date.",
        "supports": topics, "retrieved_at": RETRIEVED, "published_at": None, "mutable": mutable,
        "limitations": ["Does not prove cross-provider equivalence or universal support.", "Mutable claims require retrieval and occurrence qualification before binding."],
    } for sid, publisher, title, url, kind, mutable, topics in SOURCE_ROWS]


CONTEXT_ROWS = [
    ("identity", "Provider and artifact identity", "Provider organization, provider class, artifact, edition and offer identities", "Domain semantics and deployment occurrence state"),
    ("capability", "Capability taxonomy", "Provider-neutral physical capability classes and required surfaces", "Provider product naming and semantic operations"),
    ("offer", "Offer catalog", "Versioned, scoped capability declarations", "Observed deployment qualification"),
    ("qualification", "Provider qualification", "Conformance probes, evidence scope and qualification receipts", "Vendor certification and performance ranking"),
    ("target.profile", "Target profiles", "Abstract runtime, resource and location constraints", "Concrete capacity and current health"),
    ("target.occurrence", "Target occurrences", "Deployment or evidence-snapshot identity and configuration fingerprint", "Abstract target classification"),
    ("native", "Native execution", "Machine-code ABI, process and OS requirements", "Language semantics"),
    ("wasm", "WebAssembly execution", "Core module, component and host-interface requirements", "Application semantics"),
    ("jvm", "JVM execution", "Bytecode, JVM edition, GC and native-interface requirements", "Java business semantics"),
    ("python", "Python execution", "Interpreter, ABI, extension and isolation requirements", "Python package business meaning"),
    ("process", "Process isolation", "Process lifecycle, credentials, namespaces and resource envelope", "Container image distribution"),
    ("container", "Container runtime", "Image/runtime bundle, namespaces, cgroups and lifecycle", "Cluster scheduling policy"),
    ("kubernetes", "Kubernetes workload", "Pod, Job, device, topology and controller surfaces", "Managed-service promises"),
    ("serverless", "Serverless execution", "Invocation, concurrency, duration, scaling and ephemeral state", "Function business semantics"),
    ("batch", "Batch engines", "Finite jobs, retries, checkpoints, queues and terminal outcomes", "Analytical result meaning"),
    ("stream", "Stream engines", "Continuous work, state, watermarks, checkpoints and backpressure", "Event business meaning"),
    ("relational", "Relational engines", "Transactional/query physical capabilities and limits", "Canonical relational semantics"),
    ("warehouse", "Warehouse engines", "Elastic distributed analytical execution and documented limits", "Metric semantics"),
    ("lakehouse", "Lakehouse engines", "Table-format protocol, catalog, compute and object-store compatibility", "Data-product governance"),
    ("federated.query", "Federated query", "Pushdown translation, remote capability and fallback", "Source authority"),
    ("object.storage", "Object storage", "Object identity, consistency, conditional update and pricing surfaces", "Table transaction semantics"),
    ("block.storage", "Block storage", "Volume, attachment, durability, IOPS and throughput surfaces", "Filesystem semantics"),
    ("file.storage", "File storage", "Namespace, locking, rename, persistence and sharing surfaces", "Object-store semantics"),
    ("messaging.log", "Partitioned logs", "Partition order, offsets, retention, replication and transactions", "End-to-end delivery semantics"),
    ("messaging.queue", "Work queues", "Acknowledgement, redelivery, ordering and dead-letter behavior", "Workflow completion"),
    ("cpu", "CPU targets", "ISA, cores, topology, privilege and feature discovery", "Kernel algorithm meaning"),
    ("simd", "SIMD targets", "Vector widths, instruction subsets and numeric behavior", "Selection policy"),
    ("gpu", "GPU targets", "Device ISA/API, memory, streams, partitioning and kernel launch", "Analytical semantics"),
    ("accelerator", "Accelerator targets", "Device discovery, allocation, ABI and memory transfer", "Vendor selection"),
    ("memory", "Memory resources", "Capacity, NUMA, page size, bandwidth and pressure", "Persistent storage"),
    ("network", "Networking", "Transport, reachability, bandwidth, latency and egress policy", "Application protocol semantics"),
    ("io", "I/O runtime", "Async submission, queues, DMA, zero-copy and completion", "Storage durability"),
    ("scheduler", "Scheduling", "Eligibility, priorities, preemption, topology, reservations and fairness", "Work semantics"),
    ("managed", "Managed services", "Control-plane offer, tenancy, quotas, locations and support surface", "Canonical semantics"),
    ("edge", "Edge deployment", "Intermittent connectivity, local control and constrained capacity", "Cloud-region equivalence"),
    ("onprem", "On-premises deployment", "Operator-owned hardware, network and lifecycle", "Provider managed-service claims"),
    ("sovereign", "Sovereign target", "Legal/control/operator/location evidence requirements", "Residency inferred from region labels"),
    ("airgap", "Air-gapped target", "Offline supply chain, update, identity and evidence transfer", "Ordinary private networking"),
    ("cost", "Cost evidence", "Rate cards, meters, measured cost, currency and effective dates", "Resource consumption"),
    ("invalidation", "Binding invalidation", "Version, configuration, target, price, quota and evidence changes", "Silent fallback"),
]


def context_records() -> list[dict]:
    return [{
        "context_id": f"context.ptr.{cid}", "edition": EDITION, "status": "candidate", "name": name,
        "inside": [inside], "outside": [outside],
        "invariants": ["Unknown behavior is a typed gap.", "Provider names do not own semantic dispatch."],
        "evidence_refs": ["src.ptr.oci.runtime", "src.ptr.k8s.resources"],
        "gaps": ["Boundary remains a candidate pending global context-map adjudication."],
    } for cid, name, inside, outside in CONTEXT_ROWS]


CAPABILITY_FAMILIES = {
    "runtime": ["native_machine_code", "posix_process", "wasm_core_module", "wasm_component", "wasi_host_io", "jvm_bytecode", "jni_extension", "python_interpreter", "python_c_extension", "runtime_sandbox"],
    "isolation": ["process_credentials", "namespace_isolation", "cgroup_accounting", "seccomp_filter", "container_bundle", "virtual_machine", "tenant_isolation", "confidential_compute"],
    "deployment": ["local_in_process", "local_worker_pool", "container_process", "kubernetes_pod", "kubernetes_job", "distributed_service", "immutable_artifact", "rolling_update", "health_probe", "service_discovery"],
    "execution_mode": ["bounded_batch", "microbatch", "continuous_stream", "request_response", "event_triggered", "distributed_dag", "cyclic_dataflow", "checkpoint_resume", "retry_with_fence", "preemptible_attempt", "autoscale_to_zero"],
    "query_engine": ["relational_sql", "transactional_relational", "vectorized_query", "distributed_query", "federated_pushdown", "warehouse_compute", "lakehouse_table_protocol", "columnar_scan", "external_spill", "udf_host", "adaptive_replan"],
    "storage": ["object_get_put", "object_conditional_write", "object_versioning", "object_retention", "block_volume", "block_snapshot", "file_namespace", "atomic_rename", "durability_flush", "shared_filesystem", "local_ephemeral_storage", "integrity_checksum", "encryption_at_rest"],
    "messaging": ["partitioned_append_log", "partition_order", "consumer_offset", "consumer_group", "idempotent_publish", "transactional_publish", "durable_subscription", "work_queue", "ack_redelivery", "dead_letter", "backpressure", "retention_policy"],
    "compute": ["cpu_scalar", "cpu_simd", "cpu_vector_extension", "gpu_kernel", "accelerator_device", "device_partition", "numa_affinity", "huge_pages", "unified_memory", "device_dma", "zero_copy_device_abi"],
    "network_io": ["tcp_transport", "quic_transport", "rdma_transport", "async_io_ring", "userspace_packet_io", "userspace_storage_io", "bandwidth_limit", "egress_meter", "private_network", "service_mesh"],
    "scheduler": ["os_thread_scheduler", "local_dag_scheduler", "kubernetes_scheduler", "batch_queue_scheduler", "fair_share", "priority_preemption", "bin_packing", "gang_scheduling", "topology_aware_placement", "device_allocation", "quota_admission"],
    "location": ["developer_local", "edge_site", "on_premises", "public_cloud_region", "multi_zone", "sovereign_control", "air_gapped", "availability_declaration", "residency_guarantee", "failure_domain"],
    "managed_service": ["managed_kubernetes", "managed_batch", "managed_function", "managed_container", "managed_relational", "managed_warehouse", "managed_object_store", "managed_block_store", "managed_message_service", "managed_control_plane"],
    "evidence": ["documented_limit", "probed_limit", "list_price", "measured_cost", "semantic_conformance", "performance_measurement", "resource_usage_receipt", "configuration_fingerprint", "version_attestation", "location_attestation"],
    "optimization_solver": [
        "continuous_linear_program_execution", "solution_and_objective_reporting", "safe_terminal_classification",
        "precise_infeasible_unbounded_classification", "bounded_integer_cp_sat_execution", "boolean_cp_sat_execution",
        "all_different_and_exactly_one", "fixed_interval_no_overlap_scheduling", "complete_solution_enumeration",
        "canonical_integer_model_validation", "provider_model_invalid_preservation", "unknown_limit_status_preservation",
    ],
}


CAPABILITY_EVIDENCE = {
    "runtime": "src.ptr.oci.runtime", "isolation": "src.ptr.linux.cgroup2", "deployment": "src.ptr.k8s.job",
    "execution_mode": "src.ptr.beam", "query_engine": "src.ptr.substrait", "storage": "src.ptr.nvme",
    "messaging": "src.ptr.kafka", "compute": "src.ptr.x86", "network_io": "src.ptr.tcp",
    "scheduler": "src.ptr.k8s.scheduler", "location": "src.ptr.aws.regions", "managed_service": "src.ptr.eks", "evidence": "src.ptr.cloudrun.quotas",
    "optimization_solver": "src.ptr.highs.python",
}


def capability_records() -> list[dict]:
    records = []
    for family, names in CAPABILITY_FAMILIES.items():
        for name in names:
            records.append({
                "capability_class_id": f"capability.ptr.{family}.{name}", "edition": EDITION, "status": "candidate", "family": family,
                "name": name.replace("_", " "), "definition": f"Provider-neutral physical capability for {name.replace('_', ' ')}; exact guarantees are supplied only by a scoped offer and qualification receipt.",
                "required_surfaces": ["version or edition", "configuration", "limits", "target scope", "failure behavior", "evidence scope"],
                "non_semantic_owner": True, "evidence_refs": [CAPABILITY_EVIDENCE[family]], "parent_refs": [],
            })
    return records


PROVIDER_CLASS_ROWS = [
    ("local_operator", "Local deployment operator", "Operates a developer or single-host target", ["runtime.native_machine_code", "deployment.local_in_process"]),
    ("enterprise_platform", "Enterprise platform operator", "Operates an internal shared compute platform", ["deployment.distributed_service", "managed_service.managed_control_plane"]),
    ("open_source_project", "Open-source implementation steward", "Maintains a reusable implementation artifact", ["evidence.version_attestation"]),
    ("standards_body", "Standards organization", "Publishes normative interfaces or protocols", ["evidence.version_attestation"]),
    ("cloud_infrastructure", "Cloud infrastructure operator", "Offers regional compute, network and storage resources", ["location.public_cloud_region", "managed_service.managed_control_plane"]),
    ("managed_compute", "Managed compute service operator", "Operates serverless, batch or cluster compute", ["managed_service.managed_batch", "managed_service.managed_function", "managed_service.managed_container"]),
    ("managed_database", "Managed database or warehouse operator", "Operates a versioned query/storage service", ["managed_service.managed_relational", "managed_service.managed_warehouse"]),
    ("managed_storage", "Managed storage operator", "Operates object, block or file storage", ["managed_service.managed_object_store", "managed_service.managed_block_store"]),
    ("managed_messaging", "Managed messaging operator", "Operates log, pub/sub or queue infrastructure", ["managed_service.managed_message_service"]),
    ("hardware_vendor", "Hardware implementation provider", "Publishes and supplies CPU, GPU or accelerator artifacts", ["compute.cpu_scalar", "compute.gpu_kernel", "compute.accelerator_device"]),
    ("runtime_vendor", "Language/runtime implementation provider", "Maintains a language or portable runtime artifact", ["runtime.jvm_bytecode", "runtime.python_interpreter", "runtime.wasm_core_module"]),
    ("edge_operator", "Edge infrastructure operator", "Operates constrained or intermittently connected sites", ["location.edge_site"]),
    ("sovereign_operator", "Sovereign infrastructure operator", "Operates under declared legal, personnel and location controls", ["location.sovereign_control"]),
    ("airgap_operator", "Air-gapped infrastructure operator", "Operates targets without ordinary network dependency", ["location.air_gapped"]),
    ("telecom_network", "Network service operator", "Offers transport, private connectivity and egress", ["network_io.private_network", "network_io.bandwidth_limit"]),
]


def provider_class_records() -> list[dict]:
    return [{
        "provider_class_id": f"provider.class.ptr.{pid}", "edition": EDITION, "status": "candidate", "name": name, "role": role,
        "may_offer": [f"capability.ptr.{cap}" for cap in caps],
        "must_not_own": ["canonical operation semantics", "analytical intent", "domain policy", "selection by vendor name"],
        "evidence_refs": ["src.ptr.oci.runtime"],
    } for pid, name, role, caps in PROVIDER_CLASS_ROWS]


ORG_ROWS = [
    ("local", "Local deployment authority", "internal_operator", "local_operator", "src.ptr.posix.process"),
    ("linux", "Linux kernel project", "open_source_project", "open_source_project", "src.ptr.linux.cgroup2"),
    ("oci", "Open Container Initiative", "standards_body", "standards_body", "src.ptr.oci.runtime"),
    ("cncf", "Cloud Native Computing Foundation", "open_source_foundation", "open_source_project", "src.ptr.k8s.scheduler"),
    ("bytecode", "Bytecode Alliance", "open_source_foundation", "runtime_vendor", "src.ptr.wasmtime"),
    ("w3c_wasm", "WebAssembly Community Group", "standards_body", "standards_body", "src.ptr.wasm.core3"),
    ("oracle_java", "Oracle Java specification steward", "runtime_steward", "runtime_vendor", "src.ptr.java25"),
    ("python", "Python Software Foundation", "open_source_foundation", "runtime_vendor", "src.ptr.python314"),
    ("apache", "Apache Software Foundation", "open_source_foundation", "open_source_project", "src.ptr.flink"),
    ("postgres", "PostgreSQL Global Development Group", "open_source_project", "open_source_project", "src.ptr.postgres18"),
    ("duckdb", "DuckDB Foundation", "open_source_foundation", "open_source_project", "src.ptr.duckdb"),
    ("trino", "Trino Software Foundation", "open_source_foundation", "open_source_project", "src.ptr.trino"),
    ("khronos", "Khronos Group", "standards_body", "standards_body", "src.ptr.sycl"),
    ("intel", "Intel", "hardware_vendor", "hardware_vendor", "src.ptr.x86"),
    ("arm", "Arm", "hardware_vendor", "hardware_vendor", "src.ptr.arm"),
    ("riscv", "RISC-V International", "standards_body", "standards_body", "src.ptr.riscv"),
    ("nvidia", "NVIDIA", "hardware_vendor", "hardware_vendor", "src.ptr.cuda"),
    ("amd", "AMD", "hardware_vendor", "hardware_vendor", "src.ptr.rocm"),
    ("apple", "Apple", "hardware_vendor", "hardware_vendor", "src.ptr.metal"),
    ("aws", "Amazon Web Services", "cloud_service_operator", "cloud_infrastructure", "src.ptr.aws.regions"),
    ("google_cloud", "Google Cloud", "cloud_service_operator", "cloud_infrastructure", "src.ptr.gcp.locations"),
    ("microsoft", "Microsoft Azure", "cloud_service_operator", "cloud_infrastructure", "src.ptr.azure.geographies"),
    ("snowflake", "Snowflake", "managed_service_operator", "managed_database", "src.ptr.snowflake.limits"),
    ("databricks", "Databricks", "managed_service_operator", "managed_database", "src.ptr.databricks.sql"),
    ("clickhouse", "ClickHouse", "implementation_steward", "open_source_project", "src.ptr.clickhouse"),
    ("rabbitmq", "RabbitMQ project", "implementation_steward", "open_source_project", "src.ptr.rabbitmq"),
    ("synadia", "Synadia NATS project", "implementation_steward", "open_source_project", "src.ptr.nats"),
    ("ceph", "Ceph Foundation", "open_source_foundation", "open_source_project", "src.ptr.ceph"),
    ("google_ortools", "Google OR-Tools project", "open_source_project", "open_source_project", "src.ptr.ortools.release.9_15"),
    ("ergo_code_highs", "ERGO-Code HiGHS project", "open_source_project", "open_source_project", "src.ptr.highs.release.1_15_1"),
]


ORG_EXTRA_PROVIDER_CLASSES = {
    "aws": ["managed_compute", "managed_database", "managed_storage", "edge_operator"],
    "google_cloud": ["managed_compute", "managed_database", "managed_storage", "airgap_operator", "sovereign_operator"],
    "microsoft": ["managed_compute", "managed_database", "managed_storage", "edge_operator", "sovereign_operator"],
    "databricks": ["open_source_project"],
}


def provider_organization_records() -> list[dict]:
    return [{
        "provider_organization_id": f"provider.org.ptr.{oid}", "edition": EDITION, "status": "candidate", "name": name,
        "organization_kind": kind,
        "provider_class_refs": [f"provider.class.ptr.{candidate}" for candidate in [pclass, *ORG_EXTRA_PROVIDER_CLASSES.get(oid, [])]],
        "semantic_ownership_forbidden": True,
        "evidence_refs": [source],
    } for oid, name, kind, pclass, source in ORG_ROWS]


# id, name, kind, org, version scheme, boundary kind, capabilities, source
ARTIFACT_ROWS = [
    ("linux", "Linux kernel", "operating_system_kernel", "linux", "semantic version and distribution build", "runtime", ["runtime.posix_process", "isolation.cgroup_accounting", "network_io.async_io_ring"], "src.ptr.linux.cgroup2"),
    ("oci_runtime", "OCI Runtime Specification", "runtime_contract", "oci", "specification release", "protocol", ["deployment.container_process", "isolation.container_bundle"], "src.ptr.oci.runtime"),
    ("oci_image", "OCI Image Specification", "artifact_contract", "oci", "specification release", "protocol", ["deployment.immutable_artifact", "isolation.container_bundle"], "src.ptr.oci.image"),
    ("kubernetes", "Kubernetes", "cluster_orchestrator", "cncf", "minor release", "orchestrator", ["deployment.kubernetes_pod", "deployment.kubernetes_job", "scheduler.kubernetes_scheduler", "scheduler.device_allocation"], "src.ptr.k8s.scheduler"),
    ("wasm_core", "WebAssembly Core", "virtual_isa", "w3c_wasm", "specification release", "protocol", ["runtime.wasm_core_module"], "src.ptr.wasm.core3"),
    ("wasi", "WebAssembly System Interface", "host_interface", "bytecode", "proposal and interface world version", "protocol", ["runtime.wasi_host_io"], "src.ptr.wasi"),
    ("wasmtime", "Wasmtime", "wasm_runtime", "bytecode", "semantic version", "runtime", ["runtime.wasm_core_module", "runtime.wasm_component", "runtime.runtime_sandbox"], "src.ptr.wasmtime"),
    ("java_vm", "Java Virtual Machine", "virtual_machine_spec", "oracle_java", "Java SE edition", "runtime", ["runtime.jvm_bytecode", "runtime.jni_extension"], "src.ptr.java25"),
    ("cpython", "CPython", "language_runtime", "python", "major.minor.patch", "runtime", ["runtime.python_interpreter", "runtime.python_c_extension"], "src.ptr.python314"),
    ("spark", "Apache Spark", "distributed_data_engine", "apache", "project release", "engine", ["execution_mode.bounded_batch", "execution_mode.microbatch", "query_engine.distributed_query"], "src.ptr.spark"),
    ("flink", "Apache Flink", "distributed_data_engine", "apache", "project release", "engine", ["execution_mode.continuous_stream", "execution_mode.bounded_batch", "execution_mode.checkpoint_resume"], "src.ptr.flink"),
    ("beam", "Apache Beam", "portable_dataflow_sdk", "apache", "project release", "library", ["execution_mode.bounded_batch", "execution_mode.continuous_stream"], "src.ptr.beam"),
    ("kafka", "Apache Kafka", "partitioned_log", "apache", "project release", "storage_system", ["messaging.partitioned_append_log", "messaging.consumer_group", "messaging.transactional_publish"], "src.ptr.kafka"),
    ("pulsar", "Apache Pulsar", "partitioned_messaging", "apache", "project release", "storage_system", ["messaging.partitioned_append_log", "messaging.durable_subscription"], "src.ptr.pulsar"),
    ("airflow", "Apache Airflow", "workflow_orchestrator", "apache", "project release", "orchestrator", ["scheduler.batch_queue_scheduler", "execution_mode.distributed_dag"], "src.ptr.airflow"),
    ("argo", "Argo Workflows", "workflow_orchestrator", "cncf", "project release", "orchestrator", ["scheduler.kubernetes_scheduler", "execution_mode.distributed_dag"], "src.ptr.argo"),
    ("postgresql", "PostgreSQL", "relational_engine", "postgres", "major release plus minor patch", "engine", ["query_engine.relational_sql", "query_engine.transactional_relational"], "src.ptr.postgres18"),
    ("duckdb", "DuckDB", "embedded_query_engine", "duckdb", "semantic version", "engine", ["query_engine.relational_sql", "query_engine.vectorized_query", "query_engine.columnar_scan"], "src.ptr.duckdb"),
    ("datafusion", "Apache DataFusion", "query_engine_library", "apache", "project release", "library", ["query_engine.relational_sql", "query_engine.vectorized_query", "query_engine.external_spill"], "src.ptr.datafusion"),
    ("trino", "Trino", "distributed_query_engine", "trino", "integer release", "engine", ["query_engine.distributed_query", "query_engine.federated_pushdown"], "src.ptr.trino"),
    ("clickhouse", "ClickHouse", "columnar_database_engine", "clickhouse", "year.month.patch", "engine", ["query_engine.warehouse_compute", "query_engine.vectorized_query"], "src.ptr.clickhouse"),
    ("iceberg", "Apache Iceberg", "table_format", "apache", "specification version and implementation release", "protocol", ["query_engine.lakehouse_table_protocol", "storage.object_conditional_write"], "src.ptr.iceberg"),
    ("delta", "Delta Lake", "table_format", "databricks", "protocol reader/writer feature set", "protocol", ["query_engine.lakehouse_table_protocol"], "src.ptr.delta"),
    ("hudi", "Apache Hudi", "table_format_and_engine", "apache", "table version and project release", "engine", ["query_engine.lakehouse_table_protocol"], "src.ptr.hudi"),
    ("x86_64", "x86-64 ISA", "cpu_isa", "intel", "ISA manual edition and CPUID features", "hardware_isa", ["compute.cpu_scalar", "compute.cpu_simd"], "src.ptr.x86"),
    ("arm64", "Arm A-profile ISA", "cpu_isa", "arm", "architecture revision and ID registers", "hardware_isa", ["compute.cpu_scalar", "compute.cpu_simd"], "src.ptr.arm"),
    ("riscv64", "RISC-V 64-bit ISA", "cpu_isa", "riscv", "ratified base and extension versions", "hardware_isa", ["compute.cpu_scalar", "compute.cpu_vector_extension"], "src.ptr.riscv"),
    ("cuda", "CUDA runtime and driver API", "gpu_runtime", "nvidia", "toolkit, driver and compute capability", "runtime", ["compute.gpu_kernel", "compute.device_dma", "compute.device_partition"], "src.ptr.cuda"),
    ("rocm", "ROCm", "gpu_runtime", "amd", "platform release and GPU architecture", "runtime", ["compute.gpu_kernel", "compute.device_dma"], "src.ptr.rocm"),
    ("level_zero", "oneAPI Level Zero", "accelerator_api", "intel", "specification and driver version", "runtime", ["compute.accelerator_device", "compute.device_dma"], "src.ptr.levelzero"),
    ("metal", "Metal", "gpu_runtime", "apple", "OS SDK and GPU family", "runtime", ["compute.gpu_kernel", "compute.device_dma"], "src.ptr.metal"),
    ("s3", "Amazon S3", "managed_object_service", "aws", "API behavior snapshot", "service", ["managed_service.managed_object_store", "storage.object_get_put", "storage.object_conditional_write"], "src.ptr.s3"),
    ("gcs", "Google Cloud Storage", "managed_object_service", "google_cloud", "API behavior snapshot", "service", ["managed_service.managed_object_store", "storage.object_get_put"], "src.ptr.gcs.consistency"),
    ("azure_blob", "Azure Blob Storage", "managed_object_service", "microsoft", "API and account feature snapshot", "service", ["managed_service.managed_object_store", "storage.object_get_put"], "src.ptr.azure.blob"),
    ("ebs", "Amazon EBS", "managed_block_service", "aws", "volume type and API snapshot", "service", ["managed_service.managed_block_store", "storage.block_volume", "storage.block_snapshot"], "src.ptr.ebs"),
    ("gcp_pd", "Google Persistent Disk", "managed_block_service", "google_cloud", "disk type and API snapshot", "service", ["managed_service.managed_block_store", "storage.block_volume", "storage.block_snapshot"], "src.ptr.gcp.pd"),
    ("azure_disks", "Azure Managed Disks", "managed_block_service", "microsoft", "disk type and API snapshot", "service", ["managed_service.managed_block_store", "storage.block_volume", "storage.block_snapshot"], "src.ptr.azure.disks"),
    ("lambda", "AWS Lambda", "managed_function_service", "aws", "runtime/architecture/region documentation snapshot", "service", ["managed_service.managed_function", "execution_mode.event_triggered", "execution_mode.autoscale_to_zero"], "src.ptr.lambda.quotas"),
    ("cloud_run", "Google Cloud Run", "managed_container_service", "google_cloud", "generation/region documentation snapshot", "service", ["managed_service.managed_container", "execution_mode.request_response", "execution_mode.autoscale_to_zero"], "src.ptr.cloudrun.quotas"),
    ("azure_functions", "Azure Functions", "managed_function_service", "microsoft", "hosting-plan/runtime/region documentation snapshot", "service", ["managed_service.managed_function", "execution_mode.event_triggered"], "src.ptr.azure.functions"),
    ("aws_batch", "AWS Batch", "managed_batch_service", "aws", "compute environment and region snapshot", "service", ["managed_service.managed_batch", "scheduler.batch_queue_scheduler"], "src.ptr.awsbatch"),
    ("gcp_batch", "Google Cloud Batch", "managed_batch_service", "google_cloud", "region and API snapshot", "service", ["managed_service.managed_batch", "scheduler.batch_queue_scheduler"], "src.ptr.gcpbatch"),
    ("azure_batch", "Azure Batch", "managed_batch_service", "microsoft", "pool/VM/region snapshot", "service", ["managed_service.managed_batch", "scheduler.batch_queue_scheduler"], "src.ptr.azurebatch"),
    ("bigquery", "BigQuery", "managed_warehouse", "google_cloud", "location and service behavior snapshot", "service", ["managed_service.managed_warehouse", "query_engine.warehouse_compute"], "src.ptr.bigquery.quotas"),
    ("redshift", "Amazon Redshift", "managed_warehouse", "aws", "engine/node/API snapshot", "service", ["managed_service.managed_warehouse", "query_engine.warehouse_compute"], "src.ptr.redshift.quotas"),
    ("snowflake", "Snowflake", "managed_warehouse", "snowflake", "bundle/region/edition snapshot", "service", ["managed_service.managed_warehouse", "query_engine.warehouse_compute"], "src.ptr.snowflake.limits"),
    ("databricks_sql", "Databricks SQL warehouse", "managed_warehouse", "databricks", "channel/runtime/cloud/region snapshot", "service", ["managed_service.managed_warehouse", "query_engine.warehouse_compute", "query_engine.lakehouse_table_protocol"], "src.ptr.databricks.sql"),
    ("eks", "Amazon EKS", "managed_kubernetes", "aws", "Kubernetes/platform/region snapshot", "service", ["managed_service.managed_kubernetes", "scheduler.kubernetes_scheduler"], "src.ptr.eks"),
    ("gke", "Google Kubernetes Engine", "managed_kubernetes", "google_cloud", "Kubernetes/release-channel/region snapshot", "service", ["managed_service.managed_kubernetes", "scheduler.kubernetes_scheduler"], "src.ptr.gke"),
    ("aks", "Azure Kubernetes Service", "managed_kubernetes", "microsoft", "Kubernetes/region snapshot", "service", ["managed_service.managed_kubernetes", "scheduler.kubernetes_scheduler"], "src.ptr.aks"),
    ("rabbitmq", "RabbitMQ", "message_broker", "rabbitmq", "major.minor.patch", "engine", ["messaging.work_queue", "messaging.ack_redelivery", "messaging.dead_letter"], "src.ptr.rabbitmq"),
    ("nats_jetstream", "NATS JetStream", "message_broker", "synadia", "server release and stream configuration", "engine", ["messaging.partitioned_append_log", "messaging.durable_subscription", "messaging.ack_redelivery"], "src.ptr.nats"),
    ("ceph", "Ceph", "distributed_storage_system", "ceph", "named release and cluster configuration", "storage_system", ["storage.object_get_put", "storage.block_volume", "storage.file_namespace"], "src.ptr.ceph"),
    ("outposts", "AWS Outposts", "hybrid_infrastructure_service", "aws", "hardware/service/software snapshot", "service", ["location.edge_site", "location.on_premises", "managed_service.managed_control_plane"], "src.ptr.outposts"),
    ("gdc_airgap", "Google Distributed Cloud air-gapped", "air_gapped_infrastructure_service", "google_cloud", "release and appliance configuration", "service", ["location.air_gapped", "location.sovereign_control"], "src.ptr.gdc.airgap"),
    ("azure_stack", "Azure Stack Hub", "hybrid_infrastructure_system", "microsoft", "integrated-system update version", "service", ["location.on_premises", "location.edge_site"], "src.ptr.azure.stack"),
    ("ortools_glop_mpsolver_python", "OR-Tools GLOP through MPSolver Python", "optimization_solver_python_interface", "google_ortools", "OR-Tools release plus Python wheel and dependency lock", "library", ["optimization_solver.continuous_linear_program_execution", "optimization_solver.solution_and_objective_reporting", "optimization_solver.safe_terminal_classification"], "src.ptr.ortools.glop_mpsolver_status.9_15"),
    ("highspy_highs", "HiGHS through highspy", "optimization_solver_python_interface", "ergo_code_highs", "HiGHS release plus highspy wheel and dependency lock", "library", ["optimization_solver.continuous_linear_program_execution", "optimization_solver.solution_and_objective_reporting", "optimization_solver.safe_terminal_classification", "optimization_solver.precise_infeasible_unbounded_classification"], "src.ptr.highs.python"),
    ("ortools_cp_sat_python", "OR-Tools CP-SAT through Python", "optimization_solver_python_interface", "google_ortools", "OR-Tools release plus Python wheel, CP-SAT interface and dependency lock", "library", ["optimization_solver.bounded_integer_cp_sat_execution", "optimization_solver.boolean_cp_sat_execution", "optimization_solver.all_different_and_exactly_one", "optimization_solver.fixed_interval_no_overlap_scheduling", "optimization_solver.complete_solution_enumeration", "optimization_solver.canonical_integer_model_validation", "optimization_solver.provider_model_invalid_preservation", "optimization_solver.unknown_limit_status_preservation", "optimization_solver.solution_and_objective_reporting"], "src.ptr.ortools.cp_sat.9_15"),
]


def artifact_records() -> list[dict]:
    return [{
        "artifact_id": f"artifact.ptr.{aid}", "edition": EDITION, "status": "candidate", "name": name, "artifact_kind": kind,
        "maintainer_ref": f"provider.org.ptr.{org}", "version_scheme": versions,
        "capability_class_refs": [f"capability.ptr.{cap}" for cap in caps], "library_or_engine_or_service": boundary,
        "evidence_refs": [source],
    } for aid, name, kind, org, versions, boundary, caps, source in ARTIFACT_ROWS]


# id, name, class, runtime layers, resources, location posture, evidence
TARGET_ROWS = [
    ("local.native.x86_64", "Local native x86-64 process", "local_native", ["native", "POSIX process", "x86-64"], ["cpu", "memory", "file_descriptors", "wall_time"], "operator-selected local host", "src.ptr.x86"),
    ("local.native.arm64", "Local native Arm64 process", "local_native", ["native", "POSIX process", "Arm64"], ["cpu", "memory", "file_descriptors", "wall_time"], "operator-selected local host", "src.ptr.arm"),
    ("local.wasm", "Local WebAssembly sandbox", "local_sandbox", ["Wasm Core", "WASI host", "runtime"], ["fuel", "memory_pages", "wall_time", "host_calls"], "operator-selected local host", "src.ptr.wasm.core3"),
    ("local.jvm", "Local JVM", "managed_runtime", ["native", "JVM", "Java bytecode"], ["cpu", "heap", "direct_memory", "threads", "wall_time"], "operator-selected local host", "src.ptr.java25"),
    ("local.python", "Local CPython", "managed_runtime", ["native", "CPython", "Python bytecode/extensions"], ["cpu", "rss", "threads", "processes", "wall_time"], "operator-selected local host", "src.ptr.python314"),
    ("process.linux", "Linux isolated process", "process", ["Linux process", "namespaces", "cgroup v2"], ["cpu", "memory", "pids", "io", "wall_time"], "site-owned", "src.ptr.linux.cgroup2"),
    ("container.oci", "OCI container", "container", ["OCI image", "OCI runtime", "host kernel"], ["cpu", "memory", "pids", "ephemeral_storage", "wall_time"], "site-owned", "src.ptr.oci.runtime"),
    ("kubernetes.pod.cpu", "Kubernetes CPU pod", "kubernetes", ["OCI container", "kubelet", "scheduler"], ["cpu_request", "cpu_limit", "memory_request", "memory_limit", "ephemeral_storage"], "cluster location inherited, not residency proof", "src.ptr.k8s.resources"),
    ("kubernetes.job.cpu", "Kubernetes CPU Job", "kubernetes_batch", ["Kubernetes Job", "pod", "container"], ["parallelism", "completions", "cpu", "memory", "deadline"], "cluster location inherited, not residency proof", "src.ptr.k8s.job"),
    ("kubernetes.pod.gpu", "Kubernetes GPU pod", "kubernetes_accelerated", ["pod", "device plugin or DRA", "GPU runtime"], ["cpu", "memory", "gpu_count", "gpu_memory", "deadline"], "cluster location inherited, not residency proof", "src.ptr.k8s.device"),
    ("serverless.function", "Managed serverless function", "serverless_function", ["provider invocation", "managed runtime", "function artifact"], ["memory", "duration", "concurrency", "requests", "egress", "cost"], "documented region availability separate from residency", "src.ptr.lambda.quotas"),
    ("serverless.container", "Managed serverless container", "serverless_container", ["managed service", "OCI container"], ["vcpu", "memory", "duration", "concurrency", "network", "cost"], "documented region availability separate from residency", "src.ptr.cloudrun.quotas"),
    ("managed.batch", "Managed batch job", "managed_batch", ["managed scheduler", "VM or container", "job artifact"], ["vcpu", "memory", "accelerator", "duration", "retries", "cost"], "provider region availability", "src.ptr.awsbatch"),
    ("engine.embedded", "Embedded query engine", "query_local", ["host process", "query engine library"], ["cpu", "memory", "threads", "spill", "wall_time"], "host occurrence", "src.ptr.duckdb"),
    ("engine.distributed.query", "Distributed query engine", "query_cluster", ["coordinator", "workers", "exchange", "storage connectors"], ["workers", "cpu", "memory", "network", "spill", "query_time"], "cluster occurrence", "src.ptr.trino"),
    ("engine.stream", "Distributed stream engine", "stream_cluster", ["job manager", "workers", "state backend", "checkpoint store"], ["workers", "cpu", "memory", "state", "network", "checkpoint_time"], "cluster occurrence", "src.ptr.flink"),
    ("engine.warehouse", "Managed warehouse", "managed_query", ["service control plane", "warehouse compute", "storage"], ["slots_or_clusters", "query_time", "bytes_scanned", "concurrency", "cost"], "service locations; residency needs separate guarantee", "src.ptr.bigquery.locations"),
    ("storage.object", "Object storage target", "storage", ["object API", "durability domain"], ["bytes", "requests", "throughput", "egress", "cost"], "bucket/account location policy", "src.ptr.s3"),
    ("storage.block", "Block volume target", "storage", ["block device", "attachment", "host filesystem optional"], ["bytes", "iops", "throughput", "latency", "cost"], "volume failure domain", "src.ptr.nvme"),
    ("storage.file", "Shared file target", "storage", ["filesystem client", "server", "network"], ["bytes", "iops", "throughput", "open_files", "cost"], "server/site failure domain", "src.ptr.nfs41"),
    ("messaging.log", "Partitioned log target", "messaging", ["brokers", "replication", "consumer groups"], ["partitions", "bytes", "retention", "throughput", "lag"], "cluster occurrence", "src.ptr.kafka"),
    ("messaging.queue", "Durable work queue target", "messaging", ["broker", "queues", "consumers"], ["messages", "bytes", "retention", "throughput", "redeliveries"], "broker occurrence", "src.ptr.rabbitmq"),
    ("cpu.x86.avx2", "x86-64 with AVX2", "cpu", ["x86-64", "AVX2"], ["logical_cores", "frequency", "memory", "thermal_budget"], "host occurrence", "src.ptr.x86"),
    ("cpu.arm.neon", "Arm64 with Neon", "cpu", ["AArch64", "Advanced SIMD"], ["logical_cores", "frequency", "memory", "thermal_budget"], "host occurrence", "src.ptr.arm"),
    ("cpu.riscv.vector", "RISC-V with Vector extension", "cpu", ["RV64", "V extension"], ["logical_cores", "vlen", "memory", "thermal_budget"], "host occurrence", "src.ptr.riscv"),
    ("gpu.cuda", "CUDA GPU", "gpu", ["CUDA driver", "CUDA runtime", "device"], ["device_count", "device_memory", "compute_capability", "power", "time"], "host/cluster occurrence", "src.ptr.cuda"),
    ("gpu.rocm", "ROCm GPU", "gpu", ["kernel driver", "ROCm runtime", "device"], ["device_count", "device_memory", "gfx_arch", "power", "time"], "host/cluster occurrence", "src.ptr.rocm"),
    ("accelerator.levelzero", "Level Zero accelerator", "accelerator", ["Level Zero loader", "driver", "device"], ["device_count", "device_memory", "queues", "power", "time"], "host/cluster occurrence", "src.ptr.levelzero"),
    ("edge.connected", "Connected edge site", "edge", ["local control plane", "constrained network", "local compute"], ["cpu", "memory", "storage", "network", "power", "maintenance_window"], "edge site", "src.ptr.outposts"),
    ("onprem.cluster", "On-premises cluster", "on_premises", ["site control plane", "local compute/network/storage"], ["nodes", "cpu", "memory", "storage", "network", "power"], "enterprise site", "src.ptr.azure.stack"),
    ("sovereign.cloud", "Sovereign-controlled cloud target", "sovereign", ["declared operator", "location controls", "supply-chain controls"], ["compute", "storage", "network", "cost", "evidence_age"], "requires legal and operational evidence", "src.ptr.gcp.residency"),
    ("airgap.cluster", "Air-gapped cluster", "air_gapped", ["offline control plane", "local registry", "local identity", "local evidence export"], ["compute", "storage", "network_internal", "update_media", "evidence_age"], "no ordinary external network dependency", "src.ptr.gdc.airgap"),
    ("confidential.vm", "Confidential virtual machine", "confidential_compute", ["VM", "hardware isolation", "attestation"], ["vcpu", "memory", "attestation_age", "time", "cost"], "occurrence-specific", "src.ptr.k8s.device"),
    ("network.userspace", "User-space high-throughput I/O", "network_io", ["huge pages", "poll-mode driver", "NIC/storage device"], ["cpu_cores", "huge_pages", "queues", "bandwidth", "latency"], "host occurrence", "src.ptr.dpdk"),
    ("hybrid.controlled", "Hybrid controlled target", "hybrid", ["on-prem data plane", "optional cloud control plane", "private connectivity"], ["compute", "storage", "network", "egress", "control_plane_dependency"], "multiple independently evidenced locations", "src.ptr.outposts"),
    ("gpu.metal", "Metal GPU", "gpu", ["Metal runtime", "OS driver", "device"], ["device_count", "device_memory", "gpu_family", "power", "time"], "host occurrence", "src.ptr.metal"),
]


def target_profile_records() -> list[dict]:
    return [{
        "target_profile_id": f"target.profile.ptr.{tid}", "edition": EDITION, "status": "candidate", "name": name,
        "target_class": target_class, "runtime_layers": layers, "resource_dimensions": resources, "location_posture": location,
        "binding_requirements": ["Every blocking budget dimension is finite.", "Exact occurrence and configuration fingerprint are fixed.", "Current qualification receipt covers the artifact version and capability."],
        "evidence_refs": [source],
    } for tid, name, target_class, layers, resources, location, source in TARGET_ROWS]


# id, org, provider class, artifact, version, kind, capability suffixes, target suffixes, source, guarantee, exclusion
OFFER_ROWS = [
    ("linux.process.20260825", "local", "local_operator", "linux", "kernel+distribution exact version required", "self_managed_runtime", ["runtime.posix_process", "isolation.cgroup_accounting"], ["process.linux"], "src.ptr.linux.cgroup2", "cgroup v2 exposes hierarchical accounting/control when configured", "No isolation guarantee inferred without configuration probes"),
    ("oci.runtime.20260825", "oci", "standards_body", "oci_runtime", "specification-current@2026-08-25", "standard_contract", ["deployment.container_process", "isolation.container_bundle"], ["container.oci"], "src.ptr.oci.runtime", "Defines a portable runtime bundle/configuration contract", "Does not promise a particular runtime implementation or isolation strength"),
    ("kubernetes.1_35", "cncf", "open_source_project", "kubernetes", "1.35", "self_managed_or_distribution", ["deployment.kubernetes_pod", "scheduler.kubernetes_scheduler", "scheduler.device_allocation"], ["kubernetes.pod.cpu", "kubernetes.pod.gpu"], "src.ptr.k8s.resources", "Requests inform scheduling and limits are delegated to runtimes/kernel", "No capacity, managed-service support or residency guarantee"),
    ("kubernetes.job.1_35", "cncf", "open_source_project", "kubernetes", "1.35", "self_managed_or_distribution", ["deployment.kubernetes_job", "execution_mode.bounded_batch", "execution_mode.retry_with_fence"], ["kubernetes.job.cpu"], "src.ptr.k8s.job", "Job controller manages finite completion attempts", "Exactly-once side effects are not implied"),
    ("wasm.core.3_0", "w3c_wasm", "standards_body", "wasm_core", "3.0 (2026-07-28)", "standard_contract", ["runtime.wasm_core_module", "runtime.runtime_sandbox"], ["local.wasm"], "src.ptr.wasm.core3", "Validated modules execute under the core abstract machine", "Host I/O and deployment isolation are outside core Wasm"),
    ("wasi.snapshot.20260825", "bytecode", "runtime_vendor", "wasi", "interface snapshot@2026-08-25", "standard_contract", ["runtime.wasi_host_io", "runtime.wasm_component"], ["local.wasm"], "src.ptr.wasi", "Host capabilities are interface-scoped", "Support varies by runtime and proposal maturity"),
    ("wasmtime.snapshot.20260825", "bytecode", "runtime_vendor", "wasmtime", "exact semver required; docs snapshot@2026-08-25", "runtime_implementation", ["runtime.wasm_core_module", "runtime.wasm_component", "runtime.runtime_sandbox"], ["local.wasm"], "src.ptr.wasmtime", "Implements documented Wasm/WASI surfaces subject to configuration", "No offer is qualified until an exact binary and host are probed"),
    ("java.25", "oracle_java", "runtime_vendor", "java_vm", "Java SE 25", "runtime_standard", ["runtime.jvm_bytecode", "runtime.jni_extension"], ["local.jvm"], "src.ptr.java25", "Defines JVM bytecode and execution requirements", "Does not identify a concrete JVM build or GC behavior"),
    ("cpython.3_14_7", "python", "runtime_vendor", "cpython", "3.14.7", "runtime_implementation", ["runtime.python_interpreter", "runtime.python_c_extension"], ["local.python"], "src.ptr.python314", "Documents interpreter and C API for this patch line", "Extension ABI, free-threading safety and platform support remain package-specific"),
    ("spark.4_0_0", "apache", "open_source_project", "spark", "4.0.0", "engine_distribution", ["execution_mode.bounded_batch", "execution_mode.microbatch", "query_engine.distributed_query"], ["engine.distributed.query"], "src.ptr.spark4", "Versioned engine distribution supports documented batch/SQL/streaming surfaces", "Connector and cluster-manager compatibility are separately qualified"),
    ("flink.2_0_0", "apache", "open_source_project", "flink", "2.0.0", "engine_distribution", ["execution_mode.continuous_stream", "execution_mode.bounded_batch", "execution_mode.checkpoint_resume"], ["engine.stream"], "src.ptr.flink2", "Versioned engine distribution documents stream/batch execution and state changes", "End-to-end delivery depends on sources, sinks and checkpoint configuration"),
    ("beam.snapshot.20260825", "apache", "open_source_project", "beam", "exact SDK+runner versions required", "portable_sdk", ["execution_mode.bounded_batch", "execution_mode.continuous_stream"], ["engine.stream", "engine.distributed.query"], "src.ptr.beam", "Portable model separates pipeline from runner", "Runner capability matrices are not universal"),
    ("kafka.snapshot.20260825", "apache", "open_source_project", "kafka", "exact broker/client versions required", "engine_distribution", ["messaging.partitioned_append_log", "messaging.consumer_group", "messaging.transactional_publish"], ["messaging.log"], "src.ptr.kafka", "Partition-scoped order and offset-based consumption are documented", "End-to-end exactly-once is not implied"),
    ("pulsar.snapshot.20260825", "apache", "open_source_project", "pulsar", "exact broker/client versions required", "engine_distribution", ["messaging.partitioned_append_log", "messaging.durable_subscription"], ["messaging.log", "messaging.queue"], "src.ptr.pulsar", "Documents persistent messaging and subscription models", "Ordering and delivery depend on subscription and configuration"),
    ("airflow.snapshot.20260825", "apache", "open_source_project", "airflow", "exact release+executor required", "orchestrator_distribution", ["scheduler.batch_queue_scheduler", "execution_mode.distributed_dag"], ["managed.batch"], "src.ptr.airflow", "Schedules declared DAG tasks through configured executors", "Task idempotency and data completion are not implied"),
    ("argo.snapshot.20260825", "cncf", "open_source_project", "argo", "exact release+Kubernetes version required", "orchestrator_distribution", ["scheduler.kubernetes_scheduler", "execution_mode.distributed_dag"], ["kubernetes.job.cpu"], "src.ptr.argo", "Maps workflow nodes to Kubernetes workload executions", "Cluster capacity and side-effect semantics are external"),
    ("postgresql.18", "postgres", "open_source_project", "postgresql", "18.x exact patch required", "engine_distribution", ["query_engine.relational_sql", "query_engine.transactional_relational", "query_engine.udf_host"], ["engine.embedded"], "src.ptr.postgres18", "Documents PostgreSQL 18 SQL, transactions and extension surfaces", "Extension support and deployed settings remain occurrence-specific"),
    ("duckdb.snapshot.20260825", "duckdb", "open_source_project", "duckdb", "exact semver required; docs snapshot@2026-08-25", "engine_distribution", ["query_engine.relational_sql", "query_engine.vectorized_query", "query_engine.columnar_scan"], ["engine.embedded"], "src.ptr.duckdb", "Embedded analytical query engine capabilities are documented", "No concurrency, memory or extension claim beyond an exact occurrence"),
    ("datafusion.snapshot.20260825", "apache", "open_source_project", "datafusion", "exact crate release required; docs snapshot@2026-08-25", "library_offer", ["query_engine.relational_sql", "query_engine.vectorized_query", "query_engine.external_spill"], ["engine.embedded"], "src.ptr.datafusion", "Reusable query-engine library exposes documented operators", "A library is not a managed engine or deployment service"),
    ("trino.snapshot.20260825", "trino", "open_source_project", "trino", "exact integer release required; docs snapshot@2026-08-25", "engine_distribution", ["query_engine.distributed_query", "query_engine.federated_pushdown", "query_engine.external_spill"], ["engine.distributed.query"], "src.ptr.trino", "Distributed query and connector surfaces are documented", "Pushdown semantic compatibility is connector/source scoped"),
    ("clickhouse.snapshot.20260825", "clickhouse", "open_source_project", "clickhouse", "exact version required; docs snapshot@2026-08-25", "engine_distribution", ["query_engine.warehouse_compute", "query_engine.vectorized_query"], ["engine.distributed.query"], "src.ptr.clickhouse", "Columnar engine offers documented query and storage capabilities", "No universal SQL or durability equivalence is claimed"),
    ("iceberg.snapshot.20260825", "apache", "open_source_project", "iceberg", "spec and implementation versions required", "protocol_offer", ["query_engine.lakehouse_table_protocol", "storage.object_conditional_write"], ["storage.object"], "src.ptr.iceberg", "Table-format protocol defines snapshot and metadata behavior", "Catalog, object store and engine compatibility remain separate"),
    ("delta.snapshot.20260825", "databricks", "open_source_project", "delta", "reader/writer protocol features required", "protocol_offer", ["query_engine.lakehouse_table_protocol"], ["storage.object"], "src.ptr.delta", "Protocol gates reader/writer features", "Product branding does not prove protocol compatibility"),
    ("hudi.snapshot.20260825", "apache", "open_source_project", "hudi", "table+project versions required", "engine_distribution", ["query_engine.lakehouse_table_protocol"], ["storage.object"], "src.ptr.hudi", "Documents versioned table and service behavior", "Engine and object-store compatibility remain scoped"),
    ("x86.avx2.snapshot.20260825", "intel", "hardware_vendor", "x86_64", "manual snapshot+CPUID occurrence", "hardware_contract", ["compute.cpu_scalar", "compute.cpu_simd"], ["cpu.x86.avx2"], "src.ptr.x86", "CPUID-discoverable ISA features can constrain kernels", "Vendor name or architecture label alone does not prove AVX2"),
    ("arm.neon.snapshot.20260825", "arm", "hardware_vendor", "arm64", "architecture revision+ID registers", "hardware_contract", ["compute.cpu_scalar", "compute.cpu_simd"], ["cpu.arm.neon"], "src.ptr.arm", "Architecture documentation defines Advanced SIMD", "Concrete core and OS exposure require probing"),
    ("riscv.vector.snapshot.20260825", "riscv", "standards_body", "riscv64", "ratified extension set+occurrence probe", "hardware_contract", ["compute.cpu_scalar", "compute.cpu_vector_extension"], ["cpu.riscv.vector"], "src.ptr.riscv", "Ratified ISA extensions define vector execution", "Vector length and deployed support are occurrence-specific"),
    ("cuda.snapshot.20260825", "nvidia", "hardware_vendor", "cuda", "exact toolkit+driver+compute capability", "runtime_implementation", ["compute.gpu_kernel", "compute.device_dma", "compute.device_partition"], ["gpu.cuda"], "src.ptr.cuda", "Documents CUDA execution and memory model for supported combinations", "No kernel semantic or performance claim without qualification"),
    ("rocm.snapshot.20260825", "amd", "hardware_vendor", "rocm", "exact ROCm+driver+gfx architecture", "runtime_implementation", ["compute.gpu_kernel", "compute.device_dma"], ["gpu.rocm"], "src.ptr.rocm", "Documents ROCm runtime/toolchain surfaces", "Compatibility is device and release scoped"),
    ("levelzero.snapshot.20260825", "intel", "hardware_vendor", "level_zero", "spec+loader+driver+device versions", "runtime_implementation", ["compute.accelerator_device", "compute.device_dma"], ["accelerator.levelzero"], "src.ptr.levelzero", "Defines low-level accelerator discovery and execution interfaces", "Support and limits require a concrete driver/device probe"),
    ("metal.snapshot.20260825", "apple", "hardware_vendor", "metal", "OS SDK+GPU family snapshot", "runtime_implementation", ["compute.gpu_kernel", "compute.device_dma"], ["gpu.metal"], "src.ptr.metal", "Documents Metal GPU programming surfaces", "A concrete OS, device family and binary still require qualification"),
    ("s3.snapshot.20260825", "aws", "managed_storage", "s3", "service documentation snapshot 2026-08-25", "managed_service", ["managed_service.managed_object_store", "storage.object_get_put", "storage.object_conditional_write", "storage.object_versioning"], ["storage.object"], "src.ptr.s3", "Documented object API behavior at retrieval date", "Region availability is not a residency guarantee; quotas and prices may change"),
    ("gcs.snapshot.20260825", "google_cloud", "managed_storage", "gcs", "service documentation snapshot 2026-08-25", "managed_service", ["managed_service.managed_object_store", "storage.object_get_put", "storage.integrity_checksum"], ["storage.object"], "src.ptr.gcs.consistency", "Documented object consistency behavior at retrieval date", "Location selection alone is not legal residency proof"),
    ("azure_blob.snapshot.20260825", "microsoft", "managed_storage", "azure_blob", "service documentation snapshot 2026-08-25", "managed_service", ["managed_service.managed_object_store", "storage.object_get_put"], ["storage.object"], "src.ptr.azure.blob", "Documented blob service surfaces at retrieval date", "Account configuration and region need occurrence evidence"),
    ("ebs.snapshot.20260825", "aws", "managed_storage", "ebs", "volume/API snapshot 2026-08-25", "managed_service", ["managed_service.managed_block_store", "storage.block_volume", "storage.block_snapshot"], ["storage.block"], "src.ptr.ebs", "Documented managed block-volume surface", "IOPS/throughput/durability depend on type and configuration"),
    ("gcp_pd.snapshot.20260825", "google_cloud", "managed_storage", "gcp_pd", "disk/API snapshot 2026-08-25", "managed_service", ["managed_service.managed_block_store", "storage.block_volume", "storage.block_snapshot"], ["storage.block"], "src.ptr.gcp.pd", "Documented managed disk surface", "Limits depend on machine, disk type and location"),
    ("azure_disks.snapshot.20260825", "microsoft", "managed_storage", "azure_disks", "disk/API snapshot 2026-08-25", "managed_service", ["managed_service.managed_block_store", "storage.block_volume", "storage.block_snapshot"], ["storage.block"], "src.ptr.azure.disks", "Documented managed disk types and surfaces", "Limits depend on SKU, VM and region"),
    ("lambda.snapshot.20260825", "aws", "managed_compute", "lambda", "service/runtime/architecture snapshot 2026-08-25", "managed_service", ["managed_service.managed_function", "execution_mode.event_triggered", "execution_mode.autoscale_to_zero"], ["serverless.function"], "src.ptr.lambda.quotas", "Published quotas and runtime behavior at retrieval date", "Regional availability, account quota, price and measured cost require current evidence"),
    ("cloudrun.snapshot.20260825", "google_cloud", "managed_compute", "cloud_run", "service generation/region snapshot 2026-08-25", "managed_service", ["managed_service.managed_container", "execution_mode.request_response", "execution_mode.autoscale_to_zero"], ["serverless.container"], "src.ptr.cloudrun.quotas", "Published per-instance limits at retrieval date", "Regional quota and residency are separately evidenced"),
    ("azure_functions.snapshot.20260825", "microsoft", "managed_compute", "azure_functions", "plan/runtime/region snapshot 2026-08-25", "managed_service", ["managed_service.managed_function", "execution_mode.event_triggered"], ["serverless.function"], "src.ptr.azure.functions", "Published hosting and scaling modes at retrieval date", "Plan-specific limits and price require exact region and subscription evidence"),
    ("aws_batch.snapshot.20260825", "aws", "managed_compute", "aws_batch", "compute-environment/region snapshot 2026-08-25", "managed_service", ["managed_service.managed_batch", "scheduler.batch_queue_scheduler"], ["managed.batch"], "src.ptr.awsbatch", "Managed batch control plane schedules jobs to configured compute environments", "Capacity and instance availability are not guaranteed by the class"),
    ("gcp_batch.snapshot.20260825", "google_cloud", "managed_compute", "gcp_batch", "API/region snapshot 2026-08-25", "managed_service", ["managed_service.managed_batch", "scheduler.batch_queue_scheduler"], ["managed.batch"], "src.ptr.gcpbatch", "Managed batch job scheduling surface is documented", "Quota and VM capacity are occurrence-specific"),
    ("azure_batch.snapshot.20260825", "microsoft", "managed_compute", "azure_batch", "pool/VM/region snapshot 2026-08-25", "managed_service", ["managed_service.managed_batch", "scheduler.batch_queue_scheduler"], ["managed.batch"], "src.ptr.azurebatch", "Managed pool and job surfaces are documented", "Quota and VM capacity are subscription/region-specific"),
    ("bigquery.snapshot.20260825", "google_cloud", "managed_database", "bigquery", "service/location snapshot 2026-08-25", "managed_service", ["managed_service.managed_warehouse", "query_engine.warehouse_compute"], ["engine.warehouse"], "src.ptr.bigquery.quotas", "Published service quotas and location surface at retrieval date", "SQL semantic conformance, quota, reservation and cost require scoped evidence"),
    ("redshift.snapshot.20260825", "aws", "managed_database", "redshift", "engine/node/region snapshot 2026-08-25", "managed_service", ["managed_service.managed_warehouse", "query_engine.warehouse_compute"], ["engine.warehouse"], "src.ptr.redshift.quotas", "Published service quota surface at retrieval date", "Node type, engine version, region and configuration remain exact binding inputs"),
    ("snowflake.snapshot.20260825", "snowflake", "managed_database", "snowflake", "bundle/edition/cloud/region snapshot 2026-08-25", "managed_service", ["managed_service.managed_warehouse", "query_engine.warehouse_compute"], ["engine.warehouse"], "src.ptr.snowflake.limits", "Published limits for named service surface at retrieval date", "Account edition, release bundle, cloud and region must be fixed"),
    ("databricks_sql.snapshot.20260825", "databricks", "managed_database", "databricks_sql", "channel/runtime/cloud/region snapshot 2026-08-25", "managed_service", ["managed_service.managed_warehouse", "query_engine.warehouse_compute", "query_engine.lakehouse_table_protocol"], ["engine.warehouse"], "src.ptr.databricks.sql", "Published warehouse type surface at retrieval date", "Runtime channel, cloud, region, table protocol and connector versions remain scoped"),
    ("eks.snapshot.20260825", "aws", "managed_compute", "eks", "Kubernetes/platform/region snapshot 2026-08-25", "managed_service", ["managed_service.managed_kubernetes", "scheduler.kubernetes_scheduler"], ["kubernetes.pod.cpu", "kubernetes.pod.gpu"], "src.ptr.eks", "Managed Kubernetes control plane surface is documented", "Kubernetes version, add-ons, nodes, quotas and residency are separate"),
    ("gke.snapshot.20260825", "google_cloud", "managed_compute", "gke", "release-channel/region snapshot 2026-08-25", "managed_service", ["managed_service.managed_kubernetes", "scheduler.kubernetes_scheduler"], ["kubernetes.pod.cpu", "kubernetes.pod.gpu"], "src.ptr.gke", "Managed Kubernetes distribution surface is documented", "Mode, channel, version, nodes, quotas and residency are separate"),
    ("aks.snapshot.20260825", "microsoft", "managed_compute", "aks", "Kubernetes/region snapshot 2026-08-25", "managed_service", ["managed_service.managed_kubernetes", "scheduler.kubernetes_scheduler"], ["kubernetes.pod.cpu", "kubernetes.pod.gpu"], "src.ptr.aks", "Managed Kubernetes control plane surface is documented", "Version, node pools, quotas, policy and residency are separate"),
    ("rabbitmq.snapshot.20260825", "rabbitmq", "open_source_project", "rabbitmq", "exact server/client versions required", "engine_distribution", ["messaging.work_queue", "messaging.ack_redelivery", "messaging.dead_letter"], ["messaging.queue"], "src.ptr.rabbitmq", "Documents acknowledgement, recovery and queue reliability surfaces", "End-to-end completion and exactly-once effects are not implied"),
    ("nats.snapshot.20260825", "synadia", "open_source_project", "nats_jetstream", "exact server/client versions and stream configuration required", "engine_distribution", ["messaging.partitioned_append_log", "messaging.durable_subscription", "messaging.ack_redelivery"], ["messaging.log", "messaging.queue"], "src.ptr.nats", "Documents persisted stream and consumer behavior", "Durability and delivery depend on configuration and quorum"),
    ("ceph.snapshot.20260825", "ceph", "open_source_project", "ceph", "exact named release and cluster map required", "storage_distribution", ["storage.object_get_put", "storage.block_volume", "storage.file_namespace"], ["storage.object", "storage.block", "storage.file"], "src.ptr.ceph", "One implementation exposes separately scoped object, block and file surfaces", "Those surfaces are not one semantic capability and require separate qualification"),
    ("outposts.snapshot.20260825", "aws", "edge_operator", "outposts", "hardware/service/software snapshot 2026-08-25", "managed_hybrid_service", ["location.edge_site", "location.on_premises", "managed_service.managed_control_plane"], ["edge.connected", "hybrid.controlled"], "src.ptr.outposts", "Documents provider-managed infrastructure installed at a customer site", "Control-plane dependency, services, capacity and residency remain configuration-specific"),
    ("gdc_airgap.snapshot.20260825", "google_cloud", "airgap_operator", "gdc_airgap", "release/appliance snapshot 2026-08-25", "managed_airgap_system", ["location.air_gapped", "location.sovereign_control"], ["airgap.cluster", "sovereign.cloud"], "src.ptr.gdc.airgap", "Documents an air-gapped distributed-cloud product surface", "Air-gap qualification requires occurrence network and supply-chain probes"),
    ("azure_stack.snapshot.20260825", "microsoft", "edge_operator", "azure_stack", "integrated-system update snapshot 2026-08-25", "managed_hybrid_system", ["location.on_premises", "location.edge_site"], ["onprem.cluster", "hybrid.controlled"], "src.ptr.azure.stack", "Documents on-premises integrated infrastructure surface", "Available services, versions and connectivity depend on the integrated system"),
    ("ortools.glop_mpsolver_python.9_15_6755", "google_ortools", "open_source_project", "ortools_glop_mpsolver_python", "9.15.6755", "exact_library_interface_offer", ["optimization_solver.continuous_linear_program_execution", "optimization_solver.solution_and_objective_reporting", "optimization_solver.safe_terminal_classification"], ["local.python"], "src.ptr.ortools.glop_mpsolver_status.9_15", "Executed safe-status/objective profile passes only when ambiguous provider status is conservatively weakened at the adapter boundary", "Does not satisfy precise infeasible-versus-unbounded classification and requires a process-isolated occurrence for the tested provider pair"),
    ("highspy.highs.1_15_1", "ergo_code_highs", "open_source_project", "highspy_highs", "1.15.1", "exact_library_interface_offer", ["optimization_solver.continuous_linear_program_execution", "optimization_solver.solution_and_objective_reporting", "optimization_solver.safe_terminal_classification", "optimization_solver.precise_infeasible_unbounded_classification"], ["local.python"], "src.ptr.highs.model_status", "Executed safe-status/objective and precise terminal-classification profiles passed on the recorded isolated target", "No portability, performance, production, security, licensing or vertical-acceptance qualification is implied"),
    ("ortools.cp_sat_python.9_15_6755", "google_ortools", "open_source_project", "ortools_cp_sat_python", "9.15.6755", "exact_library_interface_offer", ["optimization_solver.bounded_integer_cp_sat_execution", "optimization_solver.boolean_cp_sat_execution", "optimization_solver.all_different_and_exactly_one", "optimization_solver.fixed_interval_no_overlap_scheduling", "optimization_solver.complete_solution_enumeration", "optimization_solver.canonical_integer_model_validation", "optimization_solver.provider_model_invalid_preservation", "optimization_solver.unknown_limit_status_preservation", "optimization_solver.solution_and_objective_reporting"], ["local.python"], "src.ptr.ortools.cp_sat.9_15", "Five exact-scope deterministic profiles passed on the corrected isolated adapter configuration", "No arbitrary CP/MILP/SAT semantics, portability, performance, production, security, licensing or vertical-acceptance qualification is implied"),
]


def offer_records() -> list[dict]:
    records = [{
        "offer_id": f"offer.ptr.{oid}", "edition": EDITION, "status": "candidate",
        "provider_organization_ref": f"provider.org.ptr.{org}", "provider_class_ref": f"provider.class.ptr.{pclass}",
        "artifact_ref": f"artifact.ptr.{artifact}", "artifact_version": version, "offer_snapshot": f"retrieved:{RETRIEVED}", "offer_kind": kind,
        "capability_class_refs": [f"capability.ptr.{cap}" for cap in caps], "target_profile_refs": [f"target.profile.ptr.{target}" for target in targets],
        "guarantees": [guarantee], "exclusions": [exclusion, "No universal support claim; exact version, configuration and target must be qualified."],
        "documented_limit_refs": [], "evidence_refs": [source], "retrieved_at": RETRIEVED, "observed_at": RETRIEVED,
        "binding_eligible": False,
        "validity": {"scope": "Candidate documentation snapshot only; not a qualified deployed occurrence.", "recheck_triggers": ["artifact version changes", "configuration changes", "target occurrence changes", "provider documentation or region changes", "evidence expires"]},
    } for oid, org, pclass, artifact, version, kind, caps, targets, source, guarantee, exclusion in OFFER_ROWS]
    for record in records:
        if record["offer_kind"] == "exact_library_interface_offer":
            record["validity"]["scope"] = "Executed-test evidence on one exact isolated target; still not independently appraised, portable, production-qualified or binding eligible."
    return records


# id, profile, org, offer, location, finite budget, availability, residency, source
OCCURRENCE_ROWS = [
    ("doc.kubernetes.1_35.cpu", "kubernetes.pod.cpu", "cncf", "kubernetes.1_35", {"kind": "documentation_scope", "value": "upstream"}, {"cpu_millicores": 1000, "memory_bytes": 1073741824, "wall_time_seconds": 3600}, [], None, "src.ptr.k8s.resources"),
    ("doc.kubernetes.1_35.gpu", "kubernetes.pod.gpu", "cncf", "kubernetes.1_35", {"kind": "documentation_scope", "value": "upstream"}, {"cpu_millicores": 4000, "memory_bytes": 17179869184, "gpu_count": 1, "wall_time_seconds": 3600}, [], None, "src.ptr.k8s.device"),
    ("doc.wasm.core3.local", "local.wasm", "w3c_wasm", "wasm.core.3_0", {"kind": "documentation_scope", "value": "host-unspecified"}, {"fuel": 1000000000, "memory_pages": 65536, "wall_time_seconds": 60, "host_calls": 1000000}, [], None, "src.ptr.wasm.core3"),
    ("doc.cpython.3_14_7.local", "local.python", "python", "cpython.3_14_7", {"kind": "documentation_scope", "value": "platform-unspecified"}, {"cpu_seconds": 60, "rss_bytes": 1073741824, "processes": 4, "wall_time_seconds": 120}, [], None, "src.ptr.python314"),
    ("doc.postgresql.18.local", "engine.embedded", "postgres", "postgresql.18", {"kind": "documentation_scope", "value": "deployment-unspecified"}, {"cpu_seconds": 3600, "memory_bytes": 8589934592, "spill_bytes": 107374182400, "wall_time_seconds": 7200}, [], None, "src.ptr.postgres18"),
    ("doc.lambda.public", "serverless.function", "aws", "lambda.snapshot.20260825", {"kind": "region", "value": "not-bound"}, {"duration_seconds": 900, "memory_mebibytes": 10240, "concurrency": 100, "cost_minor_units": 10000}, ["source-enumerated; exact region not bound"], None, "src.ptr.lambda.quotas"),
    ("doc.cloudrun.public", "serverless.container", "google_cloud", "cloudrun.snapshot.20260825", {"kind": "region", "value": "not-bound"}, {"vcpu": 8, "memory_gibibytes": 32, "duration_seconds": 3600, "concurrency": 80, "cost_minor_units": 10000}, ["source-enumerated; exact region not bound"], None, "src.ptr.cloudrun.quotas"),
    ("doc.azure_functions.public", "serverless.function", "microsoft", "azure_functions.snapshot.20260825", {"kind": "region", "value": "not-bound"}, {"duration_seconds": 600, "memory_mebibytes": 2048, "instances": 100, "cost_minor_units": 10000}, ["source-enumerated; exact plan and region not bound"], None, "src.ptr.azure.functions"),
    ("doc.s3.public", "storage.object", "aws", "s3.snapshot.20260825", {"kind": "region", "value": "not-bound"}, {"storage_bytes": 1099511627776, "requests": 1000000, "egress_bytes": 1099511627776, "cost_minor_units": 100000}, ["source-enumerated; bucket region not bound"], None, "src.ptr.s3"),
    ("doc.gcs.public", "storage.object", "google_cloud", "gcs.snapshot.20260825", {"kind": "location", "value": "not-bound"}, {"storage_bytes": 1099511627776, "requests": 1000000, "egress_bytes": 1099511627776, "cost_minor_units": 100000}, ["source-enumerated; bucket location not bound"], None, "src.ptr.gcs.consistency"),
    ("doc.bigquery.public", "engine.warehouse", "google_cloud", "bigquery.snapshot.20260825", {"kind": "location", "value": "not-bound"}, {"query_bytes": 1099511627776, "queries": 1000, "wall_time_seconds": 86400, "cost_minor_units": 100000}, ["source-enumerated; dataset/job location not bound"], None, "src.ptr.bigquery.locations"),
    ("doc.eks.public", "kubernetes.pod.cpu", "aws", "eks.snapshot.20260825", {"kind": "region", "value": "not-bound"}, {"nodes": 10, "cpu_millicores": 100000, "memory_bytes": 107374182400, "cost_minor_units": 100000}, ["source-enumerated; cluster region not bound"], None, "src.ptr.eks"),
    ("doc.gke.public", "kubernetes.pod.cpu", "google_cloud", "gke.snapshot.20260825", {"kind": "region", "value": "not-bound"}, {"nodes": 10, "cpu_millicores": 100000, "memory_bytes": 107374182400, "cost_minor_units": 100000}, ["source-enumerated; cluster location not bound"], None, "src.ptr.gke"),
    ("doc.aks.public", "kubernetes.pod.cpu", "microsoft", "aks.snapshot.20260825", {"kind": "region", "value": "not-bound"}, {"nodes": 10, "cpu_millicores": 100000, "memory_bytes": 107374182400, "cost_minor_units": 100000}, ["source-enumerated; cluster region not bound"], None, "src.ptr.aks"),
    ("doc.gdc.airgap", "airgap.cluster", "google_cloud", "gdc_airgap.snapshot.20260825", {"kind": "customer_site", "value": "not-registered"}, {"nodes": 10, "cpu_millicores": 100000, "memory_bytes": 107374182400, "offline_update_days": 90}, [], "Documentation describes an air-gapped product; no occurrence-level legal guarantee is registered.", "src.ptr.gdc.airgap"),
    ("doc.outposts.site", "hybrid.controlled", "aws", "outposts.snapshot.20260825", {"kind": "customer_site", "value": "not-registered"}, {"nodes": 4, "cpu_millicores": 64000, "memory_bytes": 274877906944, "network_bytes": 1099511627776}, [], None, "src.ptr.outposts"),
]


def occurrence_records() -> list[dict]:
    records = [{
        "target_occurrence_id": f"target.occurrence.ptr.{oid}", "edition": EDITION, "status": "candidate",
        "target_profile_ref": f"target.profile.ptr.{profile}", "provider_organization_ref": f"provider.org.ptr.{org}", "offer_ref": f"offer.ptr.{offer}",
        "occurrence_kind": "documented_offer_snapshot", "location": location,
        "configuration_fingerprint": "unbound-documentation-snapshot-2026-08-25", "artifact_versions": {"offer_snapshot": "2026-08-25", "deployment": "not_registered"},
        "finite_budget": budget, "availability_regions": availability, "residency_guarantee": residency,
        "observed_at": RETRIEVED, "retrieved_at": RETRIEVED, "evidence_refs": [source], "binding_eligible": False,
    } for oid, profile, org, offer, location, budget, availability, residency, source in OCCURRENCE_ROWS]
    records.extend([
        {
            "target_occurrence_id": "target.occurrence.ptr.probe.ortools_glop_mpsolver_python.9_15_6755.local_darwin_arm64_python3_14_7.isolated",
            "edition": EDITION, "status": "candidate", "target_profile_ref": "target.profile.ptr.local.python",
            "provider_organization_ref": "provider.org.ptr.google_ortools", "offer_ref": "offer.ptr.ortools.glop_mpsolver_python.9_15_6755",
            "occurrence_kind": "probe_fixture", "location": {"kind": "local_probe", "value": "macOS-26.5.2-arm64"},
            "configuration_fingerprint": "sha256:f24d2ab49a4077202b162d7454539fcf63ceaaff38f645663cbb97116625afdb",
            "artifact_versions": {"python": "3.14.7", "ortools": "9.15.6755", "architecture": "arm64", "process_policy": "isolated"},
            "finite_budget": {"cpu_seconds": 60, "rss_bytes": 1073741824, "processes": 1, "wall_time_seconds": 120},
            "availability_regions": [], "residency_guarantee": None, "observed_at": RETRIEVED, "retrieved_at": RETRIEVED,
            "evidence_refs": ["src.ptr.ortools.release.9_15", "src.ptr.python314"], "binding_eligible": False,
        },
        {
            "target_occurrence_id": "target.occurrence.ptr.probe.highspy_highs.1_15_1.local_darwin_arm64_python3_14_7.isolated",
            "edition": EDITION, "status": "candidate", "target_profile_ref": "target.profile.ptr.local.python",
            "provider_organization_ref": "provider.org.ptr.ergo_code_highs", "offer_ref": "offer.ptr.highspy.highs.1_15_1",
            "occurrence_kind": "probe_fixture", "location": {"kind": "local_probe", "value": "macOS-26.5.2-arm64"},
            "configuration_fingerprint": "sha256:b87fc040f883da83dd14501b8ab790854d65b69efcb91bbcde86ad581f3e8e7c",
            "artifact_versions": {"python": "3.14.7", "highspy": "1.15.1", "architecture": "arm64", "process_policy": "isolated"},
            "finite_budget": {"cpu_seconds": 60, "rss_bytes": 1073741824, "processes": 1, "wall_time_seconds": 120},
            "availability_regions": [], "residency_guarantee": None, "observed_at": RETRIEVED, "retrieved_at": RETRIEVED,
            "evidence_refs": ["src.ptr.highs.release.1_15_1", "src.ptr.python314"], "binding_eligible": False,
        },
        {
            "target_occurrence_id": "target.occurrence.ptr.probe.ortools_cp_sat_python.9_15_6755.local_darwin_arm64_python3_14_7.adapter_pre_enumeration",
            "edition": EDITION, "status": "candidate", "target_profile_ref": "target.profile.ptr.local.python",
            "provider_organization_ref": "provider.org.ptr.google_ortools", "offer_ref": "offer.ptr.ortools.cp_sat_python.9_15_6755",
            "occurrence_kind": "probe_fixture", "location": {"kind": "local_probe", "value": "macOS-26.5.2-arm64"},
            "configuration_fingerprint": "sha256:ec9813705b4e0ed2f34f6801b902cb74dd88dd3a94c842bcfb46cfe8e556ba20",
            "artifact_versions": {"python": "3.14.7", "ortools": "9.15.6755", "architecture": "arm64", "adapter": "pre-enumeration-parameter", "process_policy": "isolated"},
            "finite_budget": {"cpu_seconds": 60, "rss_bytes": 1073741824, "processes": 1, "wall_time_seconds": 120},
            "availability_regions": [], "residency_guarantee": None, "observed_at": RETRIEVED, "retrieved_at": RETRIEVED,
            "evidence_refs": ["src.ptr.ortools.cp_sat.9_15", "src.ptr.ortools.sat_parameters.9_15", "src.ptr.python314"], "binding_eligible": False,
        },
        {
            "target_occurrence_id": "target.occurrence.ptr.probe.ortools_cp_sat_python.9_15_6755.local_darwin_arm64_python3_14_7.adapter_enumeration_v2",
            "edition": EDITION, "status": "candidate", "target_profile_ref": "target.profile.ptr.local.python",
            "provider_organization_ref": "provider.org.ptr.google_ortools", "offer_ref": "offer.ptr.ortools.cp_sat_python.9_15_6755",
            "occurrence_kind": "probe_fixture", "location": {"kind": "local_probe", "value": "macOS-26.5.2-arm64"},
            "configuration_fingerprint": "sha256:0b3d43cee80b617ff4efb5fb4465640a3ed8cd8a507f32ce91a1068aae6a3aca",
            "artifact_versions": {"python": "3.14.7", "ortools": "9.15.6755", "architecture": "arm64", "adapter": "enumeration-parameter-v2", "process_policy": "isolated"},
            "finite_budget": {"cpu_seconds": 60, "rss_bytes": 1073741824, "processes": 1, "wall_time_seconds": 120},
            "availability_regions": [], "residency_guarantee": None, "observed_at": RETRIEVED, "retrieved_at": RETRIEVED,
            "evidence_refs": ["src.ptr.ortools.cp_sat.9_15", "src.ptr.ortools.sat_parameters.9_15", "src.ptr.python314"], "binding_eligible": False,
        },
    ])
    return records


# id, kind, subject suffix, metric, value, unit, source, method
RESOURCE_ROWS = [
    ("k8s.cpu.limit.semantics", "documented_limit", "offer.ptr.kubernetes.1_35", "container CPU limit", "cgroup-enforced CPU-time ceiling", "cpu units", "src.ptr.k8s.resources", "official documentation review"),
    ("k8s.memory.limit.semantics", "documented_limit", "offer.ptr.kubernetes.1_35", "container memory limit", "reactive OOM enforcement depends on kernel", "bytes", "src.ptr.k8s.resources", "official documentation review"),
    ("cloudrun.vcpu.max", "documented_limit", "offer.ptr.cloudrun.snapshot.20260825", "per-instance vCPU maximum", 8, "vCPU", "src.ptr.cloudrun.quotas", "official quota page retrieved 2026-08-25"),
    ("cloudrun.memory.max", "documented_limit", "offer.ptr.cloudrun.snapshot.20260825", "per-instance memory maximum", 32, "GiB", "src.ptr.cloudrun.quotas", "official quota page retrieved 2026-08-25"),
    ("cloudrun.job.tasks.max", "documented_limit", "offer.ptr.cloudrun.snapshot.20260825", "tasks in one job execution", 10000, "tasks", "src.ptr.cloudrun.quotas", "official quota page retrieved 2026-08-25"),
    ("cloudrun.job.timeout.max", "documented_limit", "offer.ptr.cloudrun.snapshot.20260825", "non-GPU task timeout maximum", 168, "hours", "src.ptr.cloudrun.quotas", "official quota page retrieved 2026-08-25"),
    ("lambda.duration.max", "documented_limit", "offer.ptr.lambda.snapshot.20260825", "invocation duration maximum", 900, "seconds", "src.ptr.lambda.quotas", "official quota page retrieved 2026-08-25"),
    ("lambda.memory.max", "documented_limit", "offer.ptr.lambda.snapshot.20260825", "configured memory maximum", 10240, "MiB", "src.ptr.lambda.quotas", "official quota page retrieved 2026-08-25"),
    ("azure.functions.scale", "documented_limit", "offer.ptr.azure_functions.snapshot.20260825", "scale-out maximum", "plan-dependent; lookup required", "instances", "src.ptr.azure.functions", "official hosting-plan table retrieved 2026-08-25"),
    ("bigquery.quotas", "documented_limit", "offer.ptr.bigquery.snapshot.20260825", "service quotas", "project/location/configuration lookup required", "mixed", "src.ptr.bigquery.quotas", "official quota page retrieved 2026-08-25"),
    ("redshift.quotas", "documented_limit", "offer.ptr.redshift.snapshot.20260825", "service quotas", "account/region/node lookup required", "mixed", "src.ptr.redshift.quotas", "official quota page retrieved 2026-08-25"),
    ("snowflake.limits", "documented_limit", "offer.ptr.snowflake.snapshot.20260825", "service limits", "account/edition/bundle lookup required", "mixed", "src.ptr.snowflake.limits", "official limitation page retrieved 2026-08-25"),
    ("s3.list.price", "list_price", "offer.ptr.s3.snapshot.20260825", "published rate card", "lookup required for region, tier, requests and transfer", "currency per meter", "src.ptr.s3.pricing", "official price page snapshot; not a bill"),
    ("gcs.list.price", "list_price", "offer.ptr.gcs.snapshot.20260825", "published rate card", "lookup required for location, class, operations and transfer", "currency per meter", "src.ptr.gcs.pricing", "official price page snapshot; not a bill"),
    ("azure.blob.list.price", "list_price", "offer.ptr.azure_blob.snapshot.20260825", "published rate card", "lookup required for region, tier, redundancy, operations and transfer", "currency per meter", "src.ptr.azure.storage.pricing", "official price page snapshot; not a bill"),
    ("lambda.list.price", "list_price", "offer.ptr.lambda.snapshot.20260825", "published rate card", "lookup required for region, architecture, duration, memory and requests", "currency per meter", "src.ptr.lambda.pricing", "official price page snapshot; not a bill"),
    ("cloudrun.list.price", "list_price", "offer.ptr.cloudrun.snapshot.20260825", "published rate card", "lookup required for region, CPU, memory, requests, GPU and network", "currency per meter", "src.ptr.cloudrun.pricing", "official price page snapshot; not a bill"),
    ("azure.functions.list.price", "list_price", "offer.ptr.azure_functions.snapshot.20260825", "published rate card", "lookup required for region, plan, executions, duration and memory", "currency per meter", "src.ptr.azure.functions.pricing", "official price page snapshot; not a bill"),
    ("lambda.measured.cost.gap", "measured_cost", "target.occurrence.ptr.doc.lambda.public", "measured workload cost", None, "currency", "src.ptr.lambda.pricing", "not measured; explicit evidence gap"),
    ("cloudrun.measured.cost.gap", "measured_cost", "target.occurrence.ptr.doc.cloudrun.public", "measured workload cost", None, "currency", "src.ptr.cloudrun.pricing", "not measured; explicit evidence gap"),
    ("bigquery.measured.cost.gap", "measured_cost", "target.occurrence.ptr.doc.bigquery.public", "measured workload cost", None, "currency", "src.ptr.bigquery.quotas", "not measured; explicit evidence gap"),
    ("s3.measured.cost.gap", "measured_cost", "target.occurrence.ptr.doc.s3.public", "measured workload cost", None, "currency", "src.ptr.s3.pricing", "not measured; explicit evidence gap"),
    ("cpython.limit.gap", "probed_limit", "target.occurrence.ptr.doc.cpython.3_14_7.local", "maximum resident set under representative workload", None, "bytes", "src.ptr.python314", "not probed; explicit evidence gap"),
    ("postgres.limit.gap", "probed_limit", "target.occurrence.ptr.doc.postgresql.18.local", "spill and memory behavior under representative query", None, "bytes", "src.ptr.postgres18", "not probed; explicit evidence gap"),
    ("wasm.limit.gap", "probed_limit", "target.occurrence.ptr.doc.wasm.core3.local", "fuel-to-work calibration", None, "operations per fuel", "src.ptr.wasm.core3", "not probed; embedder-specific"),
    ("eks.quota.gap", "quota_observation", "target.occurrence.ptr.doc.eks.public", "current account/region quota", None, "mixed", "src.ptr.eks", "not observed; account occurrence unavailable"),
    ("gke.quota.gap", "quota_observation", "target.occurrence.ptr.doc.gke.public", "current project/location quota", None, "mixed", "src.ptr.gke", "not observed; project occurrence unavailable"),
    ("aks.quota.gap", "quota_observation", "target.occurrence.ptr.doc.aks.public", "current subscription/region quota", None, "mixed", "src.ptr.aks", "not observed; subscription occurrence unavailable"),
    ("airgap.update.budget", "documented_limit", "offer.ptr.gdc_airgap.snapshot.20260825", "offline update and evidence-transfer budget", "deployment-specific; explicit finite value required", "days", "src.ptr.gdc.airgap", "official product documentation; occurrence probe required"),
    ("outposts.network.budget", "documented_limit", "offer.ptr.outposts.snapshot.20260825", "control-plane/network dependency", "deployment-specific; explicit finite outage budget required", "seconds", "src.ptr.outposts", "official product documentation; occurrence probe required"),
]


def resource_records() -> list[dict]:
    records = []
    for rid, kind, subject, metric, value, unit, source, method in RESOURCE_ROWS:
        binding_eligible = kind == "documented_limit" and value is not None and not (isinstance(value, str) and ("required" in value or "dependent" in value))
        records.append({
            "resource_evidence_id": f"resource.evidence.ptr.{rid}", "edition": EDITION,
            "status": "candidate" if value is not None else "unobserved_gap", "evidence_kind": kind, "subject_ref": subject,
            "metric": metric, "value": value, "unit": unit, "scope": "Only the exact named subject and retrieval/observation date.", "method": method,
            "source_refs": [source], "observed_at": RETRIEVED, "retrieved_at": RETRIEVED, "binding_eligible": binding_eligible,
            "recheck_triggers": ["version changes", "configuration changes", "target or region changes", "provider rate or quota changes", "measurement method changes"],
        })
    return records


QUALIFICATION_ROWS = [
    ("kubernetes.cpu.doc_only", "offer.ptr.kubernetes.1_35", "doc.kubernetes.1_35.cpu", ["deployment.kubernetes_pod", "scheduler.kubernetes_scheduler"]),
    ("kubernetes.gpu.doc_only", "offer.ptr.kubernetes.1_35", "doc.kubernetes.1_35.gpu", ["scheduler.device_allocation", "compute.gpu_kernel"]),
    ("wasm.core3.doc_only", "offer.ptr.wasm.core.3_0", "doc.wasm.core3.local", ["runtime.wasm_core_module", "runtime.runtime_sandbox"]),
    ("cpython.3_14_7.doc_only", "offer.ptr.cpython.3_14_7", "doc.cpython.3_14_7.local", ["runtime.python_interpreter"]),
    ("postgresql.18.doc_only", "offer.ptr.postgresql.18", "doc.postgresql.18.local", ["query_engine.relational_sql", "query_engine.transactional_relational"]),
    ("lambda.doc_only", "offer.ptr.lambda.snapshot.20260825", "doc.lambda.public", ["managed_service.managed_function"]),
    ("cloudrun.doc_only", "offer.ptr.cloudrun.snapshot.20260825", "doc.cloudrun.public", ["managed_service.managed_container"]),
    ("azure_functions.doc_only", "offer.ptr.azure_functions.snapshot.20260825", "doc.azure_functions.public", ["managed_service.managed_function"]),
    ("s3.doc_only", "offer.ptr.s3.snapshot.20260825", "doc.s3.public", ["managed_service.managed_object_store", "storage.object_conditional_write"]),
    ("gcs.doc_only", "offer.ptr.gcs.snapshot.20260825", "doc.gcs.public", ["managed_service.managed_object_store"]),
    ("bigquery.doc_only", "offer.ptr.bigquery.snapshot.20260825", "doc.bigquery.public", ["managed_service.managed_warehouse"]),
    ("eks.doc_only", "offer.ptr.eks.snapshot.20260825", "doc.eks.public", ["managed_service.managed_kubernetes"]),
    ("gke.doc_only", "offer.ptr.gke.snapshot.20260825", "doc.gke.public", ["managed_service.managed_kubernetes"]),
    ("aks.doc_only", "offer.ptr.aks.snapshot.20260825", "doc.aks.public", ["managed_service.managed_kubernetes"]),
    ("gdc_airgap.doc_only", "offer.ptr.gdc_airgap.snapshot.20260825", "doc.gdc.airgap", ["location.air_gapped", "location.sovereign_control"]),
]


def qualification_records() -> list[dict]:
    records = [{
        "qualification_receipt_id": f"qualification.ptr.{qid}", "edition": EDITION, "status": "candidate", "subject_ref": subject,
        "target_occurrence_ref": f"target.occurrence.ptr.{occurrence}", "capability_class_refs": [f"capability.ptr.{cap}" for cap in caps],
        "semantic_conformance": "not_tested", "performance_result": "not_tested", "outcome": "inconclusive",
        "evidence_class": "documentation_review", "independent_appraisal": False,
        "test_or_oracle": "Documentation review only; no deployed occurrence was available for conformance or performance probes.",
        "evidence_refs": [], "evidence_object_refs": [], "execution_receipt_refs": [], "observed_at": RETRIEVED,
        "invalidation_triggers": ["artifact version", "configuration fingerprint", "target occurrence", "provider region", "test oracle edition", "evidence age"],
    } for qid, subject, occurrence, caps in QUALIFICATION_ROWS]
    executed_rows = [
        (
            "ortools.glop_mpsolver_python.9_15_6755.safe_status_and_objective", "offer.ptr.ortools.glop_mpsolver_python.9_15_6755",
            "target.occurrence.ptr.probe.ortools_glop_mpsolver_python.9_15_6755.local_darwin_arm64_python3_14_7.isolated",
            ["optimization_solver.continuous_linear_program_execution", "optimization_solver.solution_and_objective_reporting", "optimization_solver.safe_terminal_classification"],
            "pass", "inconclusive", "oracle.lp.safe_status_and_objective.v1",
            "receipt.run-20260826-macos-arm64-python3_14-001.ortools_glop_mpsolver.safe_status_and_objective", "src.ptr.ortools.glop_mpsolver_status.9_15",
        ),
        (
            "ortools.glop_mpsolver_python.9_15_6755.precise_terminal_classification", "offer.ptr.ortools.glop_mpsolver_python.9_15_6755",
            "target.occurrence.ptr.probe.ortools_glop_mpsolver_python.9_15_6755.local_darwin_arm64_python3_14_7.isolated",
            ["optimization_solver.precise_infeasible_unbounded_classification"], "fail", "rejected", "oracle.lp.precise_terminal_classification.v1",
            "receipt.run-20260826-macos-arm64-python3_14-001.ortools_glop_mpsolver.precise_terminal_classification", "src.ptr.ortools.glop_mpsolver_status.9_15",
        ),
        (
            "highspy.highs.1_15_1.safe_status_and_objective", "offer.ptr.highspy.highs.1_15_1",
            "target.occurrence.ptr.probe.highspy_highs.1_15_1.local_darwin_arm64_python3_14_7.isolated",
            ["optimization_solver.continuous_linear_program_execution", "optimization_solver.solution_and_objective_reporting", "optimization_solver.safe_terminal_classification"],
            "pass", "inconclusive", "oracle.lp.safe_status_and_objective.v1",
            "receipt.run-20260826-macos-arm64-python3_14-001.highspy_highs.safe_status_and_objective", "src.ptr.highs.model_status",
        ),
        (
            "highspy.highs.1_15_1.precise_terminal_classification", "offer.ptr.highspy.highs.1_15_1",
            "target.occurrence.ptr.probe.highspy_highs.1_15_1.local_darwin_arm64_python3_14_7.isolated",
            ["optimization_solver.precise_infeasible_unbounded_classification"], "pass", "inconclusive", "oracle.lp.precise_terminal_classification.v1",
            "receipt.run-20260826-macos-arm64-python3_14-001.highspy_highs.precise_terminal_classification", "src.ptr.highs.model_status",
        ),
    ]
    for qid, subject, occurrence, caps, semantic, outcome, oracle, external_receipt, source in executed_rows:
        records.append({
            "qualification_receipt_id": f"qualification.ptr.{qid}", "edition": EDITION, "status": "candidate", "subject_ref": subject,
            "target_occurrence_ref": occurrence, "capability_class_refs": [f"capability.ptr.{cap}" for cap in caps],
            "semantic_conformance": semantic, "performance_result": "not_tested", "outcome": outcome,
            "evidence_class": "executed_test", "independent_appraisal": False, "test_or_oracle": oracle,
            "evidence_refs": [source], "evidence_object_refs": [LP_RECEIPTS_PATH], "execution_receipt_refs": [external_receipt],
            "observed_at": RETRIEVED,
            "invalidation_triggers": ["artifact version", "configuration fingerprint", "target occurrence", "provider region", "test oracle edition", "evidence age"],
        })
    cp_sat_rows = [
        (
            "ortools.cp_sat_python.9_15_6755.pre_enumeration.enumeration",
            "target.occurrence.ptr.probe.ortools_cp_sat_python.9_15_6755.local_darwin_arm64_python3_14_7.adapter_pre_enumeration",
            ["optimization_solver.complete_solution_enumeration"], "fail", "rejected", "profile.cpsat.enumeration",
            "receipt.run-20260826-cpsat-macos-arm64-python3_14-001.ortools_cp_sat_python.enumeration",
            CPSAT_RECEIPTS_FAILED_ENUMERATION_PATH,
        ),
        (
            "ortools.cp_sat_python.9_15_6755.core", "target.occurrence.ptr.probe.ortools_cp_sat_python.9_15_6755.local_darwin_arm64_python3_14_7.adapter_enumeration_v2",
            ["optimization_solver.bounded_integer_cp_sat_execution", "optimization_solver.boolean_cp_sat_execution", "optimization_solver.canonical_integer_model_validation", "optimization_solver.provider_model_invalid_preservation", "optimization_solver.solution_and_objective_reporting"], "pass", "inconclusive", "profile.cpsat.core",
            "receipt.run-20260826-cpsat-macos-arm64-python3_14-002.ortools_cp_sat_python.core", CPSAT_RECEIPTS_CORRECTED_PATH,
        ),
        (
            "ortools.cp_sat_python.9_15_6755.global_constraints", "target.occurrence.ptr.probe.ortools_cp_sat_python.9_15_6755.local_darwin_arm64_python3_14_7.adapter_enumeration_v2",
            ["optimization_solver.all_different_and_exactly_one"], "pass", "inconclusive", "profile.cpsat.global_constraints",
            "receipt.run-20260826-cpsat-macos-arm64-python3_14-002.ortools_cp_sat_python.global_constraints", CPSAT_RECEIPTS_CORRECTED_PATH,
        ),
        (
            "ortools.cp_sat_python.9_15_6755.scheduling", "target.occurrence.ptr.probe.ortools_cp_sat_python.9_15_6755.local_darwin_arm64_python3_14_7.adapter_enumeration_v2",
            ["optimization_solver.fixed_interval_no_overlap_scheduling"], "pass", "inconclusive", "profile.cpsat.scheduling",
            "receipt.run-20260826-cpsat-macos-arm64-python3_14-002.ortools_cp_sat_python.scheduling", CPSAT_RECEIPTS_CORRECTED_PATH,
        ),
        (
            "ortools.cp_sat_python.9_15_6755.enumeration", "target.occurrence.ptr.probe.ortools_cp_sat_python.9_15_6755.local_darwin_arm64_python3_14_7.adapter_enumeration_v2",
            ["optimization_solver.complete_solution_enumeration"], "pass", "inconclusive", "profile.cpsat.enumeration",
            "receipt.run-20260826-cpsat-macos-arm64-python3_14-002.ortools_cp_sat_python.enumeration", CPSAT_RECEIPTS_CORRECTED_PATH,
        ),
        (
            "ortools.cp_sat_python.9_15_6755.limit_no_strengthening", "target.occurrence.ptr.probe.ortools_cp_sat_python.9_15_6755.local_darwin_arm64_python3_14_7.adapter_enumeration_v2",
            ["optimization_solver.unknown_limit_status_preservation"], "pass", "inconclusive", "profile.cpsat.limit_no_strengthening",
            "receipt.run-20260826-cpsat-macos-arm64-python3_14-002.ortools_cp_sat_python.limit_no_strengthening", CPSAT_RECEIPTS_CORRECTED_PATH,
        ),
    ]
    for qid, occurrence, caps, semantic, outcome, oracle, external_receipt, evidence_path in cp_sat_rows:
        records.append({
            "qualification_receipt_id": f"qualification.ptr.{qid}", "edition": EDITION, "status": "candidate",
            "subject_ref": "offer.ptr.ortools.cp_sat_python.9_15_6755", "target_occurrence_ref": occurrence,
            "capability_class_refs": [f"capability.ptr.{cap}" for cap in caps], "semantic_conformance": semantic,
            "performance_result": "not_tested", "outcome": outcome, "evidence_class": "executed_test",
            "independent_appraisal": False, "test_or_oracle": oracle,
            "evidence_refs": ["src.ptr.ortools.cp_sat.9_15", "src.ptr.ortools.cp_model_proto.9_15", "src.ptr.ortools.sat_parameters.9_15"],
            "evidence_object_refs": [evidence_path], "execution_receipt_refs": [external_receipt], "observed_at": RETRIEVED,
            "invalidation_triggers": ["artifact version", "configuration fingerprint", "target occurrence", "provider region", "test oracle edition", "evidence age"],
        })
    return records


COMPATIBILITY_ROWS = [
    ("wasm3.local_wasm", "offer.ptr.wasm.core.3_0", "target.profile.ptr.local.wasm", "runtime.wasm_core_module", "conditional", ["Runtime must implement required core features", "Host imports must close"] , "src.ptr.wasm.core3"),
    ("wasi.local_wasm", "offer.ptr.wasi.snapshot.20260825", "target.profile.ptr.local.wasm", "runtime.wasi_host_io", "conditional", ["Exact interface world and runtime component support match"], "src.ptr.wasi"),
    ("java25.local_jvm", "offer.ptr.java.25", "target.profile.ptr.local.jvm", "runtime.jvm_bytecode", "conditional", ["Concrete JVM build implements Java SE 25", "Native dependencies match host ABI"], "src.ptr.java25"),
    ("cpython314.local_python", "offer.ptr.cpython.3_14_7", "target.profile.ptr.local.python", "runtime.python_interpreter", "conditional", ["Platform build and extension ABI match"], "src.ptr.python314"),
    ("k8s135.cpu_pod", "offer.ptr.kubernetes.1_35", "target.profile.ptr.kubernetes.pod.cpu", "deployment.kubernetes_pod", "conditional", ["API server, kubelet and runtime versions are compatible", "Requests and finite limits supplied"], "src.ptr.k8s.resources"),
    ("k8s135.gpu_pod", "offer.ptr.kubernetes.1_35", "target.profile.ptr.kubernetes.pod.gpu", "scheduler.device_allocation", "conditional", ["Device plugin or DRA driver is qualified", "Node driver/runtime versions match"], "src.ptr.k8s.device"),
    ("spark4.distributed", "offer.ptr.spark.4_0_0", "target.profile.ptr.engine.distributed.query", "execution_mode.bounded_batch", "conditional", ["Cluster manager and connector matrix passes"], "src.ptr.spark4"),
    ("flink2.stream", "offer.ptr.flink.2_0_0", "target.profile.ptr.engine.stream", "execution_mode.continuous_stream", "conditional", ["State backend, checkpoint store, source and sink versions qualify"], "src.ptr.flink2"),
    ("postgres18.embedded", "offer.ptr.postgresql.18", "target.profile.ptr.engine.embedded", "query_engine.relational_sql", "conditional", ["Server build, collation, timezone, extensions and settings fixed"], "src.ptr.postgres18"),
    ("datafusion.embedded", "offer.ptr.datafusion.snapshot.20260825", "target.profile.ptr.engine.embedded", "query_engine.vectorized_query", "conditional", ["Exact crate graph and feature flags fixed"], "src.ptr.datafusion"),
    ("cuda.cuda_gpu", "offer.ptr.cuda.snapshot.20260825", "target.profile.ptr.gpu.cuda", "compute.gpu_kernel", "conditional", ["Driver/toolkit/device compute capability matrix passes"], "src.ptr.cuda"),
    ("rocm.rocm_gpu", "offer.ptr.rocm.snapshot.20260825", "target.profile.ptr.gpu.rocm", "compute.gpu_kernel", "conditional", ["Driver/runtime/gfx architecture matrix passes"], "src.ptr.rocm"),
    ("metal.metal_gpu", "offer.ptr.metal.snapshot.20260825", "target.profile.ptr.gpu.metal", "compute.gpu_kernel", "conditional", ["OS SDK and GPU family are supported"], "src.ptr.metal"),
    ("iceberg.object", "offer.ptr.iceberg.snapshot.20260825", "target.profile.ptr.storage.object", "query_engine.lakehouse_table_protocol", "conditional", ["Catalog and object conditional-update contracts qualify", "Engine supports exact spec features"], "src.ptr.iceberg"),
    ("s3.residency", "offer.ptr.s3.snapshot.20260825", "target.profile.ptr.sovereign.cloud", "location.residency_guarantee", "unknown", ["Availability region alone is insufficient", "Legal/operator/control evidence required"], "src.ptr.aws.residency"),
    ("gdc.airgap", "offer.ptr.gdc_airgap.snapshot.20260825", "target.profile.ptr.airgap.cluster", "location.air_gapped", "conditional", ["Occurrence proves no ordinary external dependency", "Offline update and evidence paths tested"], "src.ptr.gdc.airgap"),
    ("rabbitmq.queue", "offer.ptr.rabbitmq.snapshot.20260825", "target.profile.ptr.messaging.queue", "messaging.ack_redelivery", "conditional", ["Queue durability, confirms, acknowledgements and recovery settings fixed"], "src.ptr.rabbitmq"),
    ("ceph.object", "offer.ptr.ceph.snapshot.20260825", "target.profile.ptr.storage.object", "storage.object_get_put", "conditional", ["Exact release and RADOS Gateway configuration qualify"], "src.ptr.ceph"),
]


def compatibility_records() -> list[dict]:
    records = [{
        "compatibility_id": f"compatibility.ptr.{cid}", "edition": EDITION, "status": "candidate", "left_ref": left, "right_ref": right,
        "capability_class_ref": f"capability.ptr.{cap}", "result": result, "conditions": conditions, "evidence_refs": [source],
        "evidence_object_refs": [],
        "observed_at": RETRIEVED, "invalidation_triggers": ["left version changes", "right target/configuration changes", "required capability changes", "evidence expires"],
    } for cid, left, right, cap, result, conditions, source in COMPATIBILITY_ROWS]
    records.extend([
        {
            "compatibility_id": "compatibility.ptr.ortools_glop_mpsolver_python.9_15_6755.local_python3_14_7",
            "edition": EDITION, "status": "candidate", "left_ref": "offer.ptr.ortools.glop_mpsolver_python.9_15_6755",
            "right_ref": "target.occurrence.ptr.probe.ortools_glop_mpsolver_python.9_15_6755.local_darwin_arm64_python3_14_7.isolated",
            "capability_class_ref": "capability.ptr.optimization_solver.safe_terminal_classification", "result": "conditional",
            "conditions": ["Exact dependency lock and configuration digests match the retained receipt", "Provider executes in its isolated Python process"],
            "evidence_refs": ["src.ptr.ortools.release.9_15", "src.ptr.ortools.glop_mpsolver_status.9_15"],
            "evidence_object_refs": [LP_RECEIPTS_PATH], "observed_at": RETRIEVED,
            "invalidation_triggers": ["left version changes", "right target/configuration changes", "required capability changes", "evidence expires"],
        },
        {
            "compatibility_id": "compatibility.ptr.highspy_highs.1_15_1.local_python3_14_7",
            "edition": EDITION, "status": "candidate", "left_ref": "offer.ptr.highspy.highs.1_15_1",
            "right_ref": "target.occurrence.ptr.probe.highspy_highs.1_15_1.local_darwin_arm64_python3_14_7.isolated",
            "capability_class_ref": "capability.ptr.optimization_solver.precise_infeasible_unbounded_classification", "result": "conditional",
            "conditions": ["Exact dependency lock and configuration digests match the retained receipt", "Provider executes in its isolated Python process"],
            "evidence_refs": ["src.ptr.highs.release.1_15_1", "src.ptr.highs.model_status"],
            "evidence_object_refs": [LP_RECEIPTS_PATH], "observed_at": RETRIEVED,
            "invalidation_triggers": ["left version changes", "right target/configuration changes", "required capability changes", "evidence expires"],
        },
        {
            "compatibility_id": "compatibility.ptr.ortools_highspy.same_python_process.local_darwin_arm64_python3_14_7",
            "edition": EDITION, "status": "candidate", "left_ref": "offer.ptr.ortools.glop_mpsolver_python.9_15_6755",
            "right_ref": "offer.ptr.highspy.highs.1_15_1", "capability_class_ref": "capability.ptr.runtime.python_c_extension",
            "result": "incompatible", "conditions": ["Observed only for the exact dependency locks and macOS arm64 Python 3.14.7 process", "Separate provider processes avoid this observed native-library symbol collision"],
            "evidence_refs": ["src.ptr.ortools.release.9_15", "src.ptr.highs.release.1_15_1"],
            "evidence_object_refs": [LP_COHABITATION_PATH], "observed_at": RETRIEVED,
            "invalidation_triggers": ["left version changes", "right target/configuration changes", "required capability changes", "evidence expires"],
        },
        {
            "compatibility_id": "compatibility.ptr.ortools_cp_sat_python.9_15_6755.pre_enumeration_adapter",
            "edition": EDITION, "status": "candidate", "left_ref": "offer.ptr.ortools.cp_sat_python.9_15_6755",
            "right_ref": "target.occurrence.ptr.probe.ortools_cp_sat_python.9_15_6755.local_darwin_arm64_python3_14_7.adapter_pre_enumeration",
            "capability_class_ref": "capability.ptr.optimization_solver.complete_solution_enumeration", "result": "incompatible",
            "conditions": ["Callback observed solutions but exhaustive enumeration parameter was absent", "Failure is scoped to this exact adapter configuration"],
            "evidence_refs": ["src.ptr.ortools.cp_sat.9_15", "src.ptr.ortools.sat_parameters.9_15"],
            "evidence_object_refs": [CPSAT_RECEIPTS_FAILED_ENUMERATION_PATH], "observed_at": RETRIEVED,
            "invalidation_triggers": ["left version changes", "right target/configuration changes", "required capability changes", "evidence expires"],
        },
        {
            "compatibility_id": "compatibility.ptr.ortools_cp_sat_python.9_15_6755.enumeration_adapter_v2",
            "edition": EDITION, "status": "candidate", "left_ref": "offer.ptr.ortools.cp_sat_python.9_15_6755",
            "right_ref": "target.occurrence.ptr.probe.ortools_cp_sat_python.9_15_6755.local_darwin_arm64_python3_14_7.adapter_enumeration_v2",
            "capability_class_ref": "capability.ptr.optimization_solver.complete_solution_enumeration", "result": "conditional",
            "conditions": ["Exact adapter digest carries enumeration intent into the provider parameter", "All five exact-scope profiles pass but independent appraisal and vertical acceptance remain absent"],
            "evidence_refs": ["src.ptr.ortools.cp_sat.9_15", "src.ptr.ortools.sat_parameters.9_15"],
            "evidence_object_refs": [CPSAT_RECEIPTS_CORRECTED_PATH], "observed_at": RETRIEVED,
            "invalidation_triggers": ["left version changes", "right target/configuration changes", "required capability changes", "evidence expires"],
        },
    ])
    return records


DECISION_ROWS = [
    ("artifact.version", "Which exact artifact edition/version is bound?", ["exact immutable version or digest", "refuse"], "physical_binding"),
    ("provider.offer.snapshot", "Which dated provider offer snapshot is eligible?", ["fresh scoped snapshot", "refuse"], "physical_binding"),
    ("target.occurrence", "Which exact target occurrence and configuration fingerprint is used?", ["registered occurrence", "refuse"], "deployment_binding"),
    ("runtime.native_wasm_jvm_python", "Which runtime family satisfies the declared ABI and effect contract?", ["native", "wasm", "jvm", "python", "refuse"], "physical_binding"),
    ("process.isolation", "What process/container/VM isolation posture is required?", ["process", "container", "vm", "wasm_sandbox", "refuse"], "physical_binding"),
    ("deployment.mode", "What deployment mechanism is selected?", ["local", "process", "container", "kubernetes", "managed_service", "refuse"], "physical_binding"),
    ("execution.mode", "Which bounded, microbatch, streaming, request or event mode is authorized?", ["bounded_batch", "microbatch", "continuous_stream", "request_response", "event_triggered", "refuse"], "physical_binding"),
    ("engine.class", "Which engine class can implement the physical contract?", ["relational", "warehouse", "lakehouse", "federated_query", "stream", "batch", "refuse"], "physical_binding"),
    ("storage.class", "Which object, block or file storage semantics are required?", ["object", "block", "file", "none", "refuse"], "physical_binding"),
    ("messaging.class", "Which log, pub/sub or queue contract is required?", ["partitioned_log", "durable_subscription", "work_queue", "none", "refuse"], "physical_binding"),
    ("cpu.isa", "Which CPU ISA and extensions are required?", ["x86_64", "arm64", "riscv64", "portable_scalar", "refuse"], "physical_binding"),
    ("simd.posture", "May SIMD-specific kernels be selected?", ["required", "allowed_with_scalar_equivalence", "forbidden", "refuse"], "physical_binding"),
    ("accelerator.posture", "Is an accelerator required or optional?", ["required_exact_api", "optional_equivalent_fallback", "forbidden", "refuse"], "physical_binding"),
    ("gpu.partition", "May a partitioned GPU device satisfy the request?", ["whole_device", "qualified_partition", "either", "refuse"], "deployment_binding"),
    ("memory.budget", "What finite memory minimum, target and maximum apply?", ["explicit finite vector", "refuse"], "physical_binding"),
    ("spill.policy", "Is external spill authorized and where?", ["qualified_encrypted_spill", "no_spill", "refuse"], "physical_binding"),
    ("network.egress", "What finite egress and connectivity posture is authorized?", ["no_egress", "private_only", "bounded_public", "refuse"], "deployment_binding"),
    ("scheduler.policy", "Which scheduler policy and quality posture are authorized?", ["deterministic_rule", "optimizer_with_receipt", "heuristic_with_receipt", "refuse"], "physical_binding"),
    ("preemption", "May an attempt be preempted?", ["forbidden", "checkpoint_resume_proven", "restart_safe_proven", "refuse"], "physical_binding"),
    ("serverless.concurrency", "What finite concurrency and backpressure limits apply?", ["explicit_finite_limits", "refuse"], "deployment_binding"),
    ("location.availability", "Which locations currently advertise the offer?", ["dated availability evidence", "refuse"], "deployment_binding"),
    ("location.residency", "What separately evidenced residency guarantee is required?", ["none", "contractual_residency", "sovereign_control", "air_gapped", "refuse"], "deployment_binding"),
    ("cost.budget", "What finite currency, period and meter budget applies?", ["explicit finite budget", "cost_not_selection_axis", "refuse"], "physical_binding"),
    ("price.evidence", "Which dated list-price schedule is used?", ["fresh rate card", "negotiated rate receipt", "refuse"], "deployment_binding"),
    ("measured.cost", "Is measured workload cost required before release?", ["required", "not_required", "refuse"], "evidence_verification"),
    ("semantic.conformance", "Which semantic conformance oracle must pass?", ["declared oracle and edition", "refuse"], "evidence_verification"),
    ("performance.gate", "Which performance SLO and workload fixture must pass?", ["declared workload and thresholds", "not_a_selection_gate", "refuse"], "evidence_verification"),
    ("degradation", "Which typed degradations were declared by intent?", ["enumerated declared degradations", "none", "refuse"], "physical_binding"),
    ("evidence.freshness", "What maximum evidence age applies per evidence kind?", ["explicit finite durations", "refuse"], "evidence_verification"),
    ("adapter.selection", "Which exact adapter version translates the canonical contract?", ["qualified adapter and receipt", "refuse"], "physical_binding"),
    ("solver.status_precision", "Which terminal-status precision does the analytical contract require?", ["safe_ambiguous_terminal_class", "precise_infeasible_vs_unbounded", "refuse"], "physical_binding"),
    ("solver.model_class", "Which closed provider-neutral formal-model class must the offer implement?", ["continuous_lp", "bounded_integer_cp_sat", "other_exact_declared_class", "refuse"], "physical_binding"),
    ("solver.solution_enumeration", "Does intent require one solution or complete finite enumeration?", ["one_solution", "complete_enumeration_with_completion_proof", "refuse"], "physical_binding"),
    ("native_extension.cohabitation", "May the selected native Python extensions share one process?", ["qualified_same_process", "isolated_processes", "refuse"], "deployment_binding"),
]


def decision_records() -> list[dict]:
    return [{
        "decision_id": f"decision.ptr.{did}", "edition": EDITION, "status": "candidate", "question": question,
        "allowed_values": values, "binding_phase": phase, "authority": "declared deployment or assurance authority; provider defaults are not authoritative",
        "default_law": "forbidden", "required_evidence": ["versioned offer", "target occurrence", "finite budgets", "current scoped evidence"],
        "change_semantics": ["Re-run physical binding.", "Invalidate qualification when artifact, configuration or target scope changes."],
    } for did, question, values, phase in DECISION_ROWS]


RULE_ROWS = [
    ("refuse.unknown_capability", "refusal", "a requirement references an unknown capability class", "emit a typed missing-capability gap", "refuse compilation"),
    ("refuse.vendor_dispatch", "refusal", "selection depends on provider organization or product spelling", "restate selection as capability, guarantees, budgets and evidence gates", "refuse vendor-name dispatch"),
    ("refuse.unversioned_artifact", "refusal", "an implementation artifact version/digest is not exact", "resolve an immutable version", "refuse binding"),
    ("refuse.unbounded_budget", "refusal", "any blocking resource, time, state, network or cost budget is unbounded", "supply finite min/target/max values", "refuse binding"),
    ("refuse.stale_offer", "refusal", "a mutable concrete offer lacks current observed/retrieved dates", "refresh official evidence and occurrence probes", "refuse binding"),
    ("refuse.unqualified_occurrence", "refusal", "only a target profile or documentation snapshot exists", "register and qualify a concrete target occurrence", "refuse deployment"),
    ("refuse.limit_substitution", "refusal", "a documented limit is used as if it were a probed occurrence limit", "probe the deployed configuration", "refuse limit-dependent plan"),
    ("refuse.price_as_cost", "refusal", "a list-price record is used as measured workload cost", "measure and reconcile workload meters", "refuse cost proof"),
    ("refuse.performance_as_semantics", "refusal", "a benchmark pass is used as semantic conformance", "run the declared semantic oracle", "refuse conformance claim"),
    ("refuse.library_as_service", "refusal", "a library contribution is treated as an engine or managed service", "bind host, lifecycle, effects and operations separately", "refuse incomplete deployment"),
    ("refuse.availability_as_residency", "refusal", "region availability is used as a residency guarantee", "attach separately scoped legal and operational residency evidence", "refuse residency-sensitive binding"),
    ("refuse.silent_degradation", "refusal", "fallback changes exactness, completeness, latency, durability, isolation or location without prior declaration", "carry an authorized typed degradation into plan and receipt", "refuse fallback"),
    ("invalidate.artifact_version", "invalidation", "artifact, driver, firmware, runtime, engine or adapter version changes", "re-run compatibility and qualification", "invalidate affected binding and receipts"),
    ("invalidate.configuration", "invalidation", "a semantically or physically relevant configuration value changes", "recompute fingerprint and qualification", "invalidate affected binding and receipts"),
    ("invalidate.target", "invalidation", "target occurrence, hardware, region, zone or failure domain changes", "re-run target qualification", "invalidate affected binding and receipts"),
    ("invalidate.quota", "invalidation", "quota, account entitlement or capacity reservation changes", "re-run feasibility and admission", "invalidate capacity proof"),
    ("invalidate.price", "invalidation", "rate card, currency, discount or meter definition changes", "re-price and re-precharge finite budget", "invalidate cost proof"),
    ("invalidate.evidence_age", "invalidation", "evidence exceeds its declared maximum age", "refresh documentation or probe evidence", "invalidate evidence-dependent binding"),
    ("invalidate.oracle", "invalidation", "semantic oracle, workload fixture or threshold edition changes", "repeat the affected tests", "invalidate qualification receipt"),
    ("invalidate.location_control", "invalidation", "operator, legal, personnel, connectivity or location control changes", "repeat residency/sovereignty/air-gap assurance", "invalidate location-sensitive binding"),
    ("invalidate.health", "invalidation", "occurrence health or reservation is lost", "reconcile or choose another already-qualified occurrence", "invalidate current placement"),
    ("refuse.no_llm_dependency", "refusal", "core physical binding requires an LLM, prompt, RAG, agent memory or generative model", "replace it with deterministic data, code and declared evidence", "refuse core dependency"),
    ("refuse.status_strengthening", "refusal", "a provider terminal status is translated into a more precise canonical claim than its documented and tested surface supports", "preserve the ambiguity or select an offer qualified for the required precision", "refuse the strengthened result"),
    ("refuse.native_extension_collision", "refusal", "native extensions have an incompatible same-process dependency or symbol graph on the selected target", "select a qualified cohabiting pair or isolate them in separate processes", "refuse same-process binding"),
    ("refuse.model_class_collapse", "refusal", "CP-SAT, generic constraint programming, MILP, SAT or another formal-model class is selected as if provider interfaces were interchangeable", "preserve the classified model facets and require an exact offer mapping", "refuse class substitution"),
    ("refuse.callback_as_enumeration", "refusal", "a solution callback is used as evidence that complete enumeration was requested and completed", "bind the exact enumeration parameter and require a completion-status/count oracle", "refuse completeness claim"),
]


def rule_records() -> list[dict]:
    return [{
        "rule_id": f"rule.ptr.{rid}", "edition": EDITION, "status": "candidate", "rule_kind": kind,
        "when": when, "must": must, "otherwise": otherwise, "typed_degradation": "only_if_declared" if "degradation" in rid else "forbidden",
    } for rid, kind, when, must, otherwise in RULE_ROWS]


# id, capability suffixes, offer suffixes, budget dims
MAPPING_ROWS = [
    ("native.process", ["runtime.posix_process"], ["linux.process.20260825"], ["cpu", "memory", "pids", "wall_time"]),
    ("oci.container", ["deployment.container_process", "isolation.container_bundle"], ["oci.runtime.20260825"], ["cpu", "memory", "pids", "ephemeral_storage", "wall_time"]),
    ("kubernetes.pod", ["deployment.kubernetes_pod", "scheduler.kubernetes_scheduler"], ["kubernetes.1_35", "eks.snapshot.20260825", "gke.snapshot.20260825", "aks.snapshot.20260825"], ["cpu_request", "cpu_limit", "memory_request", "memory_limit", "deadline"]),
    ("kubernetes.job", ["deployment.kubernetes_job", "execution_mode.bounded_batch"], ["kubernetes.job.1_35", "argo.snapshot.20260825"], ["parallelism", "cpu", "memory", "deadline", "retries"]),
    ("wasm.core", ["runtime.wasm_core_module"], ["wasm.core.3_0", "wasmtime.snapshot.20260825"], ["fuel", "memory_pages", "host_calls", "wall_time"]),
    ("wasi.component", ["runtime.wasm_component", "runtime.wasi_host_io"], ["wasi.snapshot.20260825", "wasmtime.snapshot.20260825"], ["fuel", "memory_pages", "host_calls", "wall_time"]),
    ("jvm.bytecode", ["runtime.jvm_bytecode"], ["java.25"], ["cpu", "heap", "direct_memory", "threads", "wall_time"]),
    ("python.runtime", ["runtime.python_interpreter"], ["cpython.3_14_7"], ["cpu", "rss", "processes", "threads", "wall_time"]),
    ("batch.engine", ["execution_mode.bounded_batch", "execution_mode.distributed_dag"], ["spark.4_0_0", "flink.2_0_0", "aws_batch.snapshot.20260825", "gcp_batch.snapshot.20260825", "azure_batch.snapshot.20260825"], ["workers", "cpu", "memory", "network", "storage", "deadline", "cost"]),
    ("stream.engine", ["execution_mode.continuous_stream", "execution_mode.checkpoint_resume"], ["flink.2_0_0", "beam.snapshot.20260825"], ["workers", "cpu", "memory", "state", "checkpoint_interval", "recovery_time", "cost"]),
    ("relational.engine", ["query_engine.relational_sql", "query_engine.transactional_relational"], ["postgresql.18"], ["cpu", "memory", "connections", "storage", "deadline"]),
    ("embedded.query", ["query_engine.vectorized_query", "query_engine.columnar_scan"], ["duckdb.snapshot.20260825", "datafusion.snapshot.20260825"], ["cpu", "memory", "threads", "spill", "deadline"]),
    ("distributed.query", ["query_engine.distributed_query", "query_engine.external_spill"], ["trino.snapshot.20260825", "spark.4_0_0"], ["workers", "cpu", "memory", "network", "spill", "deadline"]),
    ("warehouse.query", ["query_engine.warehouse_compute"], ["clickhouse.snapshot.20260825", "bigquery.snapshot.20260825", "redshift.snapshot.20260825", "snowflake.snapshot.20260825", "databricks_sql.snapshot.20260825"], ["concurrency", "query_time", "bytes_scanned", "storage", "cost"]),
    ("lakehouse.protocol", ["query_engine.lakehouse_table_protocol", "storage.object_conditional_write"], ["iceberg.snapshot.20260825", "delta.snapshot.20260825", "hudi.snapshot.20260825"], ["metadata_objects", "commit_retries", "retention", "scan_bytes", "cost"]),
    ("object.storage", ["storage.object_get_put", "storage.integrity_checksum"], ["s3.snapshot.20260825", "gcs.snapshot.20260825", "azure_blob.snapshot.20260825", "ceph.snapshot.20260825"], ["bytes", "requests", "throughput", "egress", "cost"]),
    ("block.storage", ["storage.block_volume", "storage.block_snapshot"], ["ebs.snapshot.20260825", "gcp_pd.snapshot.20260825", "azure_disks.snapshot.20260825", "ceph.snapshot.20260825"], ["bytes", "iops", "throughput", "latency", "cost"]),
    ("file.storage", ["storage.file_namespace", "storage.atomic_rename", "storage.durability_flush"], ["ceph.snapshot.20260825"], ["bytes", "iops", "throughput", "open_files", "cost"]),
    ("partitioned.log", ["messaging.partitioned_append_log", "messaging.consumer_offset", "messaging.partition_order"], ["kafka.snapshot.20260825", "pulsar.snapshot.20260825", "nats.snapshot.20260825"], ["partitions", "bytes", "retention", "throughput", "lag"]),
    ("work.queue", ["messaging.work_queue", "messaging.ack_redelivery", "messaging.dead_letter"], ["rabbitmq.snapshot.20260825", "pulsar.snapshot.20260825", "nats.snapshot.20260825"], ["messages", "bytes", "retention", "redeliveries", "deadline"]),
    ("cpu.simd", ["compute.cpu_scalar", "compute.cpu_simd"], ["x86.avx2.snapshot.20260825", "arm.neon.snapshot.20260825"], ["cores", "vector_width", "memory", "power", "deadline"]),
    ("cpu.vector", ["compute.cpu_scalar", "compute.cpu_vector_extension"], ["riscv.vector.snapshot.20260825"], ["cores", "vlen", "memory", "power", "deadline"]),
    ("gpu.cuda", ["compute.gpu_kernel", "compute.device_dma"], ["cuda.snapshot.20260825"], ["devices", "device_memory", "host_memory", "transfer_bytes", "power", "deadline"]),
    ("gpu.rocm", ["compute.gpu_kernel", "compute.device_dma"], ["rocm.snapshot.20260825"], ["devices", "device_memory", "host_memory", "transfer_bytes", "power", "deadline"]),
    ("accelerator.levelzero", ["compute.accelerator_device", "compute.device_dma"], ["levelzero.snapshot.20260825"], ["devices", "device_memory", "queues", "transfer_bytes", "power", "deadline"]),
    ("serverless.function", ["managed_service.managed_function", "execution_mode.event_triggered"], ["lambda.snapshot.20260825", "azure_functions.snapshot.20260825"], ["memory", "duration", "concurrency", "requests", "egress", "cost"]),
    ("serverless.container", ["managed_service.managed_container", "execution_mode.request_response"], ["cloudrun.snapshot.20260825"], ["vcpu", "memory", "duration", "concurrency", "network", "cost"]),
    ("managed.kubernetes", ["managed_service.managed_kubernetes", "scheduler.kubernetes_scheduler"], ["eks.snapshot.20260825", "gke.snapshot.20260825", "aks.snapshot.20260825"], ["nodes", "cpu", "memory", "accelerators", "network", "cost"]),
    ("edge.hybrid", ["location.edge_site", "location.on_premises"], ["outposts.snapshot.20260825", "azure_stack.snapshot.20260825"], ["cpu", "memory", "storage", "network", "power", "maintenance_window"]),
    ("airgap.sovereign", ["location.air_gapped", "location.sovereign_control"], ["gdc_airgap.snapshot.20260825"], ["cpu", "memory", "storage", "internal_network", "offline_update_age", "evidence_age"]),
    ("optimization.lp.safe", ["optimization_solver.continuous_linear_program_execution", "optimization_solver.solution_and_objective_reporting", "optimization_solver.safe_terminal_classification"], ["ortools.glop_mpsolver_python.9_15_6755", "highspy.highs.1_15_1"], ["variables", "constraints", "coefficients", "cpu", "memory", "wall_time"]),
    ("optimization.lp.precise_terminal", ["optimization_solver.continuous_linear_program_execution", "optimization_solver.precise_infeasible_unbounded_classification"], ["highspy.highs.1_15_1"], ["variables", "constraints", "coefficients", "cpu", "memory", "wall_time"]),
    ("optimization.cp_sat.bounded_integer", ["optimization_solver.bounded_integer_cp_sat_execution", "optimization_solver.canonical_integer_model_validation", "optimization_solver.provider_model_invalid_preservation", "optimization_solver.unknown_limit_status_preservation", "optimization_solver.solution_and_objective_reporting"], ["ortools.cp_sat_python.9_15_6755"], ["variables", "domain_cardinality", "constraints", "coefficients", "deterministic_time", "cpu", "memory", "wall_time"]),
    ("optimization.cp_sat.complete_enumeration", ["optimization_solver.bounded_integer_cp_sat_execution", "optimization_solver.complete_solution_enumeration"], ["ortools.cp_sat_python.9_15_6755"], ["variables", "domain_cardinality", "solutions", "deterministic_time", "cpu", "memory", "wall_time"]),
]


def mapping_records() -> list[dict]:
    return [{
        "mapping_id": f"mapping.ptr.{mid}", "edition": EDITION, "status": "candidate", "requirement_id": f"requirement.ptr.{mid}",
        "capability_class_refs": [f"capability.ptr.{cap}" for cap in caps],
        "required_guarantees": ["Exact semantics remain owned upstream.", "Every selected offer passes structural, semantic, policy, resource and evidence gates."],
        "prohibited_traits": ["vendor-name dispatch", "unversioned artifact", "undated mutable offer", "unqualified target", "implicit degradation"],
        "finite_budget_dimensions": budgets, "offer_candidate_refs": [f"offer.ptr.{offer}" for offer in offers],
        "evidence_gates": ["current official offer evidence", "exact artifact/configuration identity", "occurrence qualification", "semantic conformance distinct from performance", "list price distinct from measured cost"],
        "fallback_law": "typed_degradation_only_if_declared" if mid in {"cpu.simd", "gpu.cuda", "gpu.rocm", "accelerator.levelzero"} else "refuse",
        "invalidation_rule_refs": ["rule.ptr.invalidate.artifact_version", "rule.ptr.invalidate.configuration", "rule.ptr.invalidate.target", "rule.ptr.invalidate.evidence_age"],
    } for mid, caps, offers, budgets in MAPPING_ROWS]


BOUNDARY_ROWS = [
    ("capability.matcher", "Capability matcher", "pure_library", ["structural requirement/offer matching"], ["provider API calls", "semantic ownership", "ranking by name"], "none", ["registry snapshot", "selection law"], ["candidate and rejection trace"], "src.ptr.substrait"),
    ("budget.algebra", "Finite budget algebra", "pure_library", ["typed dimensions", "normalization", "dominance"], ["price lookup", "resource reservation"], "none", ["unit registry", "hardness"], ["feasibility derivation"], "src.ptr.k8s.resources"),
    ("target.matcher", "Target profile matcher", "pure_library", ["profile compatibility predicates"], ["target probes", "deployment"], "none", ["profile edition"], ["compatibility trace"], "src.ptr.wasm.core3"),
    ("offer.registry", "Offer registry library", "runtime_library", ["versioned offer storage", "freshness evaluation"], ["semantic inference", "provider selection policy"], "registry read/write effects", ["source retrieval time", "expiry law"], ["registry revision receipt"], "src.ptr.aws.regions"),
    ("qualification.harness", "Qualification harness", "runtime_library", ["probe orchestration", "oracle invocation", "receipt formation"], ["certification authority", "undeclared destructive probes"], "explicit target test effects", ["oracle edition", "probe budget", "target fixture"], ["qualification receipt"], "src.ptr.k8s.device"),
    ("cost.reconciler", "Cost evidence reconciler", "runtime_library", ["meter normalization", "list/contract/measured reconciliation"], ["billing authority", "silent currency conversion"], "price and meter evidence reads", ["currency", "effective time", "account terms"], ["cost proof receipt"], "src.ptr.cloudrun.pricing"),
    ("oci.adapter", "OCI runtime adapter", "provider_adapter", ["typed container intent translation"], ["application semantics", "hidden runtime defaults"], "container lifecycle effects", ["runtime binary", "bundle config", "limits"], ["container occurrence receipt"], "src.ptr.oci.runtime"),
    ("kubernetes.adapter", "Kubernetes workload adapter", "provider_adapter", ["typed pod/job/device translation"], ["scheduler semantics", "exactly-once claims"], "Kubernetes API effects", ["API version", "requests", "limits", "selectors", "deadline"], ["object UID and observed status"], "src.ptr.k8s.job"),
    ("wasmtime.adapter", "Wasmtime runtime adapter", "provider_adapter", ["module/component instantiation and finite fuel/epoch limits"], ["guest semantics", "ambient host access"], "declared host imports", ["runtime semver", "WASI worlds", "fuel", "memory"], ["module digest and termination receipt"], "src.ptr.wasmtime"),
    ("jvm.adapter", "JVM process adapter", "provider_adapter", ["JVM launch and resource options"], ["Java application semantics", "GC performance guarantees"], "process and filesystem effects", ["JVM build", "heap", "GC", "threads", "JNI"], ["process and runtime configuration receipt"], "src.ptr.java25"),
    ("cpython.adapter", "CPython process adapter", "provider_adapter", ["interpreter launch, environment and extension identity"], ["package semantics", "thread-safety inference"], "process, filesystem and declared network effects", ["interpreter build", "ABI", "packages", "limits"], ["environment lock and process receipt"], "src.ptr.python314"),
    ("spark.integration", "Spark engine integration", "engine_integration", ["physical plan translation and job submission"], ["canonical query semantics", "cluster capacity"], "engine and storage effects", ["Spark version", "extensions", "cluster manager", "connectors"], ["plan/job/stage receipts"], "src.ptr.spark"),
    ("flink.integration", "Flink engine integration", "engine_integration", ["stream graph translation and checkpoint controls"], ["event meaning", "end-to-end delivery inference"], "engine, state and sink effects", ["Flink version", "state backend", "checkpoint store", "connectors"], ["job/checkpoint/savepoint receipts"], "src.ptr.flink"),
    ("postgres.integration", "PostgreSQL engine integration", "engine_integration", ["SQL/parameter translation and transaction control"], ["canonical relational semantics", "schema authority"], "database effects", ["server version", "settings", "extensions", "collation", "timezone"], ["query/transaction/EXPLAIN receipts"], "src.ptr.postgres18"),
    ("object.adapter", "Object-store adapter", "provider_adapter", ["object API translation", "conditional requests", "checksums"], ["table transaction semantics", "residency inference"], "object read/write/delete effects", ["endpoint", "region", "credentials", "retry", "consistency expectations"], ["request/version/checksum receipts"], "src.ptr.s3.conditional"),
    ("block.adapter", "Block-volume adapter", "provider_adapter", ["provision, attach, snapshot and release intents"], ["filesystem semantics", "database durability"], "control-plane and block-device effects", ["volume type", "size", "IOPS", "throughput", "zone"], ["volume/attachment/snapshot receipts"], "src.ptr.ebs"),
    ("messaging.adapter", "Messaging adapter", "provider_adapter", ["publish, consume, ack and transaction translation"], ["business completion", "exactly-once effect inference"], "broker effects", ["broker/client versions", "topic/queue", "acks", "transactions", "retention"], ["offset/message/ack receipts"], "src.ptr.kafka"),
    ("gpu.adapter", "Accelerator adapter", "provider_adapter", ["device discovery, allocation, transfer and kernel launch"], ["kernel semantics", "performance ranking"], "device effects", ["driver", "runtime", "device", "memory", "stream"], ["device/kernel/timing receipts"], "src.ptr.cuda"),
    ("serverless.adapter", "Serverless service adapter", "provider_adapter", ["deploy, invoke, scale and concurrency configuration"], ["function semantics", "price as measured cost"], "provider API and invocation effects", ["region", "runtime", "memory", "timeout", "concurrency"], ["revision/invocation/usage receipts"], "src.ptr.cloudrun.quotas"),
    ("location.assurance", "Location assurance adapter", "provider_adapter", ["availability, residency, operator and connectivity evidence collection"], ["legal conclusions without authority", "region-to-residency inference"], "control-plane evidence reads", ["location", "operator", "contract", "network boundary", "evidence age"], ["location assurance receipt"], "src.ptr.gcp.residency"),
    ("lp_solver.adapter", "Continuous-LP solver adapter", "provider_adapter", ["finite-input refusal", "canonical LP translation", "no-strengthening status mapping", "solution and objective normalization"], ["optimization-model semantics", "provider qualification", "performance equivalence", "business authorization"], "isolated provider-process invocation", ["provider offer", "dependency lock", "numeric tolerance", "status precision", "process isolation"], ["provider result", "oracle result", "executed-test receipt", "binding refusal"], "src.ptr.ortools.glop_mpsolver_status.9_15"),
    ("cp_sat_solver.adapter", "Bounded-integer CP-SAT solver adapter", "provider_adapter", ["integer-only input refusal", "canonical CP-SAT translation", "exact status mapping", "enumeration intent propagation", "independent solution and schedule checking"], ["formal-model classification", "provider qualification", "vertical scheduling semantics", "business authorization"], "isolated provider-process invocation", ["provider offer", "dependency lock", "adapter digest", "random seed", "worker count", "deterministic-work budget", "enumeration posture"], ["provider result", "oracle result", "executed-test receipt", "binding refusal"], "src.ptr.ortools.cp_sat.9_15"),
]


def boundary_records() -> list[dict]:
    return [{
        "boundary_id": f"boundary.ptr.{bid}", "edition": EDITION, "status": "candidate", "name": name, "boundary_kind": kind,
        "owns": owns, "must_not_own": not_own, "effects": effects, "configuration_surface": config, "receipt_surface": receipts,
        "evidence_refs": [source],
    } for bid, name, kind, owns, not_own, effects, config, receipts, source in BOUNDARY_ROWS]


INNOVATION_ROWS = [
    ("quic.rfc9000", "QUIC v1 standardization", 2021, "User-space encrypted transport changes connection migration and multiplexing options.", ["network_io.quic_transport"], "src.ptr.quic"),
    ("riscv.vector", "Ratified RISC-V Vector extension", 2021, "Scalable vector length becomes an explicit kernel-target binding dimension.", ["compute.cpu_vector_extension"], "src.ptr.riscv"),
    ("nvme2", "NVMe 2.x specification family", 2021, "Refactored command-set and transport specifications broaden block and fabric binding surfaces.", ["storage.block_volume", "network_io.userspace_storage_io"], "src.ptr.nvme"),
    ("cuda.mig", "Multi-Instance GPU operations", 2021, "Hardware partition identity must be distinguished from a whole GPU target.", ["compute.device_partition"], "src.ptr.cuda.mig"),
    ("io_uring.growth", "io_uring asynchronous I/O expansion", 2021, "Submission/completion rings expand explicit async I/O kernel choices.", ["network_io.async_io_ring"], "src.ptr.linux.io_uring"),
    ("pcie6", "PCI Express 6.0", 2022, "PAM4 and new link behavior affect accelerator and storage fabric envelopes.", ["compute.device_dma", "network_io.userspace_storage_io"], "src.ptr.pcie6"),
    ("cxl3", "Compute Express Link 3.0", 2022, "Memory pooling and fabrics introduce new topology and coherence constraints.", ["compute.numa_affinity", "compute.unified_memory"], "src.ptr.cxl3"),
    ("wasm.component", "WebAssembly Component Model emergence", 2022, "Typed component interfaces separate portable modules from host capabilities.", ["runtime.wasm_component", "runtime.wasi_host_io"], "src.ptr.component"),
    ("gdc.airgap", "Managed distributed cloud for air-gapped sites", 2023, "Air-gapped infrastructure becomes a separately qualifiable deployment product class.", ["location.air_gapped", "location.sovereign_control"], "src.ptr.gdc.airgap"),
    ("java.virtual_threads", "Java virtual threads", 2023, "Lightweight JVM scheduling changes concurrency envelopes without changing task semantics.", ["runtime.jvm_bytecode", "scheduler.os_thread_scheduler"], "src.ptr.java.virtual_threads"),
    ("delta.deletion_vectors", "Delta protocol deletion vectors", 2023, "Row deletion can be represented physically without rewriting all data files, gated by protocol features.", ["query_engine.lakehouse_table_protocol"], "src.ptr.delta"),
    ("s3.express", "Directory-bucket and low-latency object-storage class evolution", 2023, "Object-store offers now require bucket-class and location-type distinctions.", ["storage.object_get_put", "location.failure_domain"], "src.ptr.s3"),
    ("python.free_threading", "CPython free-threaded build", 2024, "The interpreter build and extension safety posture become explicit parallelism binding inputs.", ["runtime.python_interpreter", "runtime.python_c_extension"], "src.ptr.python.free_threading"),
    ("s3.conditional_write", "Amazon S3 conditional writes", 2024, "Conditional creation/update changes the set of object-store coordination primitives available to table protocols.", ["storage.object_conditional_write"], "src.ptr.s3.conditional"),
    ("arrow.device", "Arrow C Device Data Interface", 2024, "Device-resident columnar buffers gain a portable ABI boundary for zero-copy exchange.", ["compute.zero_copy_device_abi", "compute.device_dma"], "src.ptr.arrow.device"),
    ("java.vector", "Continued Java Vector API incubation", 2024, "JVM kernels can express explicit SIMD operations while remaining edition and platform scoped.", ["compute.cpu_simd", "runtime.jvm_bytecode"], "src.ptr.java.vector"),
    ("kafka.kraft", "Kafka KRaft control-plane transition", 2024, "Broker/controller topology and upgrade compatibility become independent binding evidence.", ["messaging.partitioned_append_log", "managed_service.managed_control_plane"], "src.ptr.kafka"),
    ("azure.functions.flex", "Azure Functions Flex Consumption", 2024, "Per-function scaling and plan-specific concurrency expand serverless target distinctions.", ["managed_service.managed_function", "execution_mode.autoscale_to_zero"], "src.ptr.azure.functions"),
    ("iceberg.rest", "Iceberg REST catalog protocol expansion", 2024, "Catalog interoperability becomes a versioned protocol boundary separate from table files and compute engines.", ["query_engine.lakehouse_table_protocol"], "src.ptr.iceberg"),
    ("flink2.async_state", "Flink 2.0 asynchronous state and disaggregated-state direction", 2025, "State access and placement can change physically while event-time semantics remain fixed.", ["execution_mode.continuous_stream", "execution_mode.checkpoint_resume"], "src.ptr.flink2"),
    ("spark4", "Apache Spark 4.0", 2025, "A major engine edition forces explicit connector, SQL and cluster compatibility requalification.", ["execution_mode.bounded_batch", "query_engine.distributed_query"], "src.ptr.spark4"),
    ("k8s.dra", "Kubernetes Dynamic Resource Allocation", 2025, "Structured device claims improve accelerator discovery and allocation beyond opaque scalar resources.", ["scheduler.device_allocation", "compute.accelerator_device"], "src.ptr.k8s.dra"),
    ("k8s.pod_resources", "Kubernetes pod-level resource specification", 2025, "Shared pod budgets add a distinct enforcement/configuration scope beyond per-container limits.", ["isolation.cgroup_accounting", "scheduler.quota_admission"], "src.ptr.k8s.resources"),
    ("wasm3", "WebAssembly Core 3.0", 2026, "A new core edition adds typed references and changes runtime/feature compatibility requirements.", ["runtime.wasm_core_module"], "src.ptr.wasm.core3"),
    ("k8s.in_place_resize", "Stable in-place pod resource resize", 2026, "A running target can change CPU/memory configuration and therefore invalidate prior resource qualification.", ["deployment.kubernetes_pod", "isolation.cgroup_accounting"], "src.ptr.k8s.resources"),
    ("java26", "Java SE 26", 2026, "A new JVM language/specification edition creates an explicit artifact and compatibility boundary.", ["runtime.jvm_bytecode"], "src.ptr.java26"),
]


def innovation_records() -> list[dict]:
    return [{
        "innovation_id": f"innovation.ptr.{iid}", "edition": EDITION, "status": "candidate", "name": name, "year": year,
        "why_material": why, "affected_capability_refs": [f"capability.ptr.{cap}" for cap in caps], "non_llm": True, "evidence_refs": [source],
    } for iid, name, year, why, caps, source in INNOVATION_ROWS]


GAP_ROWS = [
    ("provider_completeness", "provider.class.ptr.cloud_infrastructure", False, "The registry samples multiple implementation and managed-service forms.", "Open-world provider and offer enumeration is not complete.", "Recurring evidence harvest and independent review adds classes without changing compiler code.", "Do not infer completeness from record count.", "src.ptr.aws.regions"),
    ("offer_freshness", "offer.ptr.cloudrun.snapshot.20260825", True, "A dated documentation snapshot exists.", "Future quotas, regions, prices and runtime changes are unknown.", "Refresh mutable evidence within the deployment authority's maximum age.", "Do not bind stale snapshots.", "src.ptr.cloudrun.quotas"),
    ("occurrence_absence", "target.occurrence.ptr.doc.lambda.public", True, "A public offer snapshot is represented.", "No account, region, runtime build or function occurrence was available.", "Register and probe the concrete occurrence.", "Do not treat documentation as deployment qualification.", "src.ptr.lambda.quotas"),
    ("measured_cost", "resource.evidence.ptr.lambda.measured.cost.gap", True, "A current list-price source exists.", "Measured workload cost is absent.", "Run the declared workload, capture provider meters and reconcile the bill.", "Do not substitute list price for measured cost.", "src.ptr.lambda.pricing"),
    ("semantic_conformance", "qualification.ptr.bigquery.doc_only", True, "Service documentation and quotas are available.", "No declared SQL semantic oracle was run.", "Run the exact semantic conformance suite against a versioned occurrence.", "Do not substitute performance or marketing compatibility.", "src.ptr.bigquery.quotas"),
    ("performance", "qualification.ptr.postgresql.18.doc_only", False, "PostgreSQL 18 documentation is scoped.", "No workload performance result exists.", "Run a finite, versioned workload on the registered target.", "Do not infer performance from semantic conformance.", "src.ptr.postgres18"),
    ("residency", "target.profile.ptr.sovereign.cloud", True, "Availability and residency are separate registry fields.", "No universal legal or operational residency contract exists.", "Bind authority-reviewed contract, operator, data-flow and control-plane evidence.", "Do not infer residency from a region label.", "src.ptr.gcp.residency"),
    ("airgap_probe", "target.occurrence.ptr.doc.gdc.airgap", True, "Official product documentation describes an air-gapped offer.", "No occurrence network, update or evidence-export probe exists.", "Qualify the installed occurrence under finite offline budgets.", "Do not infer an air gap from product naming.", "src.ptr.gdc.airgap"),
    ("gpu_matrix", "offer.ptr.cuda.snapshot.20260825", True, "Official programming documentation defines compatibility surfaces.", "Exact driver/toolkit/device/kernel matrix is unprobed.", "Probe the immutable artifact on the device occurrence.", "Do not infer support from GPU vendor name.", "src.ptr.cuda"),
    ("rocm_matrix", "offer.ptr.rocm.snapshot.20260825", True, "Official runtime documentation exists.", "Exact driver/runtime/gfx/kernel matrix is unprobed.", "Probe the immutable artifact on the device occurrence.", "Do not infer cross-device compatibility.", "src.ptr.rocm"),
    ("metal_matrix", "offer.ptr.metal.snapshot.20260825", True, "Official API documentation exists.", "Exact OS/SDK/GPU/kernel matrix is unprobed.", "Probe the immutable artifact on the device occurrence.", "Do not infer portability from API family.", "src.ptr.metal"),
    ("wasm_host", "offer.ptr.wasi.snapshot.20260825", True, "Core Wasm and host interfaces are separated.", "Runtime support for exact worlds and proposals is unprobed.", "Fix runtime semver and interface world versions, then test imports/effects.", "Do not infer WASI from core Wasm support.", "src.ptr.wasi"),
    ("python_extensions", "offer.ptr.cpython.3_14_7", True, "Interpreter patch version is named.", "Native extension ABI and free-threading safety are package/platform specific.", "Lock packages, wheels, build flags and run extension safety tests.", "Do not infer extension safety from Python compatibility.", "src.ptr.python.free_threading"),
    ("jvm_implementation", "offer.ptr.java.25", True, "The Java SE 25 specification is identified.", "No concrete JVM vendor build, GC or flags are registered.", "Register exact runtime binary, host and flags.", "Do not treat a specification as a deployed runtime.", "src.ptr.java25"),
    ("k8s_distribution", "offer.ptr.kubernetes.1_35", True, "Upstream Kubernetes behavior is represented.", "Managed distributions, feature gates, runtime and add-ons vary.", "Qualify exact distribution and cluster occurrence.", "Do not infer managed-service parity from upstream version.", "src.ptr.k8s.resources"),
    ("lakehouse_interop", "offer.ptr.iceberg.snapshot.20260825", True, "Table protocol evidence exists.", "Catalog, engine, object-store and feature compatibility is incomplete.", "Run protocol and failure-injection matrix on exact components.", "Do not treat table-format name as interoperability proof.", "src.ptr.iceberg"),
    ("messaging_e2e", "offer.ptr.kafka.snapshot.20260825", True, "Broker transaction and offset surfaces are documented.", "Source/sink/end-to-end effect conformance is not proven.", "Test the composed pipeline with failure injection and fencing.", "Do not claim exactly-once from one broker.", "src.ptr.kafka"),
    ("object_semantics", "offer.ptr.ceph.snapshot.20260825", True, "Ceph exposes object, block and file implementations.", "Their exact configured semantics and performance are unqualified.", "Qualify each surface independently on the cluster occurrence.", "Do not collapse multiple service surfaces into one capability.", "src.ptr.ceph"),
    ("quota_capacity", "resource.evidence.ptr.eks.quota.gap", True, "Managed control-plane documentation exists.", "Quota, capacity and reservation for an account/region are unknown.", "Read quota and reserve capacity for the exact occurrence.", "Do not treat quota as physical capacity.", "src.ptr.eks"),
    ("energy", "target.profile.ptr.gpu.cuda", False, "Power is a declared finite resource dimension.", "No calibrated energy or carbon evidence is present.", "Attach device power measurements and an authority-approved accounting method.", "Do not optimize on undocumented carbon estimates.", "src.ptr.cuda"),
    ("lp_independent_appraisal", "qualification.ptr.highspy.highs.1_15_1.precise_terminal_classification", True, "A deterministic executed test passed on one exact isolated target.", "No independent appraisal, portability assessment, production fitness, security, license or vertical acceptance exists.", "Have an independent authority reproduce the locked protocol and complete the omitted assurance profiles.", "Do not promote an executed-test pass to a qualified or portable offer.", "src.ptr.highs.release.1_15_1"),
    ("lp_status_precision", "qualification.ptr.ortools.glop_mpsolver_python.9_15_6755.precise_terminal_classification", True, "The safe ambiguous-status profile passed and the precise-status profile failed.", "No evidence supports distinguishing infeasible from unbounded through this exact GLOP/MPSolver surface.", "Keep the canonical ambiguity or bind a separately qualified precise-status offer.", "Do not strengthen MPSolver INFEASIBLE into a precise canonical claim.", "src.ptr.ortools.glop_mpsolver_status.9_15"),
    ("lp_native_cohabitation", "compatibility.ptr.ortools_highspy.same_python_process.local_darwin_arm64_python3_14_7", True, "An exact same-process native-library symbol collision was retained as a negative twin.", "Other operating systems, architectures, Python builds or dependency graphs were not tested.", "Qualify a same-process dependency graph or retain process isolation for the pair.", "Do not infer global incompatibility or ignore the observed target-specific collision.", "src.ptr.highs.release.1_15_1"),
    ("cp_sat_independent_appraisal", "qualification.ptr.ortools.cp_sat_python.9_15_6755.core", True, "Five deterministic exact-scope profiles passed on one corrected isolated adapter occurrence.", "No independent appraisal, portability, performance, production, security, license or manufacturing acceptance exists.", "Have an independent authority reproduce the locked protocol and complete omitted provider and vertical profiles.", "Do not promote executed tests to a qualified, portable or manufacturing-accepted offer.", "src.ptr.ortools.cp_sat.9_15"),
    ("cp_sat_enumeration_configuration", "compatibility.ptr.ortools_cp_sat_python.9_15_6755.pre_enumeration_adapter", False, "The first retained adapter occurrence failed enumeration and the corrected occurrence passed.", "No evidence generalizes either result across other adapter, provider or target configurations.", "Retain both receipts, bind the exact configuration digest and rerun the enumeration oracle after any relevant change.", "Do not treat a callback, one observed solution or provider OPTIMAL status alone as proof of complete enumeration.", "src.ptr.ortools.sat_parameters.9_15"),
]


def gap_records() -> list[dict]:
    return [{
        "gap_id": f"gap.ptr.{gid}", "edition": EDITION, "status": "open", "gap_kind": gid, "subject_ref": subject,
        "blocking": blocking, "known": known, "unknown": unknown, "resolution_condition": resolution, "prohibited_assumption": prohibited,
        "evidence_refs": [source],
    } for gid, subject, blocking, known, unknown, resolution, prohibited, source in GAP_ROWS]


def metamodel() -> dict:
    return {
        "metamodel_id": "san.provider-target-physical-binding-registry", "edition": EDITION, "status": "candidate_research_contract", "completion_claim": False,
        "scope": "Provider-neutral physical binding from capability requirements to versioned offers and qualified target occurrences; optional model/LLM/agent assistance may propose inputs but is never required by or authoritative over this deterministic core.",
        "identity_separations": [
            "provider organization != provider class != implementation artifact",
            "implementation artifact != edition/version != concrete offer != deployed occurrence",
            "capability class != observed offer", "target class/profile != target occurrence",
            "documented limit != probed limit", "list price != measured cost",
            "semantic conformance != performance", "library != engine != managed service",
            "availability region != residency guarantee",
        ],
        "binding_chain": ["capability requirement", "provider-neutral capability class", "versioned concrete offer", "target profile", "target occurrence", "compatibility cell", "qualification receipt", "finite resource/cost proof", "binding or typed refusal"],
        "constitutional_laws": [
            "Provider and vendor names never own semantics or determine dispatch.", "Every blocking resource, state, time, network and cost dimension is finite.",
            "Mutable offers and limits are dated and scope-bound.", "Binding evidence is invalidated by relevant artifact, configuration, target, region, rate, quota or oracle changes.",
            "Degradation is legal only when declared by intent, typed, authorized and receipted.", "Unknown or stale behavior fails closed as a typed gap.",
            "All core generation and validation are deterministic and have no LLM or generative dependency.",
            "Removing every model, LLM or agent extension leaves parsing, typing, constraint solving, execution, authorization and receipt verification intact.",
            "A model or agent output is a typed proposal until deterministic validation and the owning authority accept it.",
            "Formal-model classification, provider-offer matching, model validation, terminal status and result verification remain deterministic even when an optional agent proposed the candidate model.",
            "A solution callback is not complete-enumeration intent or proof; the exact adapter configuration and completion oracle are binding inputs.",
        ],
        "reconciled_contracts": [
            "research/domain_atlas/compiler/compiler-metamodel.json",
            "research/domain_atlas/compiler/requirement-offer-binding.schema.json",
            "research/domain_atlas/universes/universe-contract.json",
            "research/domain_atlas/universes/query_compute_kernels/metamodel.json",
            "research/domain_atlas/universes/runtime_compute_resource/compiler-contract.json",
            "research/domain_atlas/universes/source_systems/compiler-contract.json",
            "research/domain_atlas/universes/pipeline_dataflow/manifest.json",
            "research/domain_atlas/universes/encoding_compression/manifest.json",
            "research/domain_atlas/universes/persistence_lakehouse/coverage-report.json",
            "research/domain_atlas/universes/universe-coverage-audit.json",
            "research/domain_atlas/compiler/model_class_adjudication/manifest.json",
            "research/domain_atlas/compiler/conformance_evaluation/executions/cp_sat_exact_scope/protocol.json",
            "research/domain_atlas/compiler/conformance_evaluation/executions/cp_sat_exact_scope/runs/run-20260826-cpsat-macos-arm64-python3_14-002/manifest.json",
        ],
    }


def main() -> None:
    build_schemas()
    groups = {
        "sources.jsonl": source_records(), "context-candidates.jsonl": context_records(), "capability-classes.jsonl": capability_records(),
        "provider-classes.jsonl": provider_class_records(), "provider-organizations.jsonl": provider_organization_records(),
        "implementation-artifacts.jsonl": artifact_records(), "concrete-offers.jsonl": offer_records(), "target-profiles.jsonl": target_profile_records(),
        "target-occurrences.jsonl": occurrence_records(), "resource-limit-cost-evidence.jsonl": resource_records(),
        "qualification-receipts.jsonl": qualification_records(), "compatibility-matrix.jsonl": compatibility_records(),
        "decisions.jsonl": decision_records(), "refusal-invalidation-rules.jsonl": rule_records(),
        "compiler-requirement-offer-mappings.jsonl": mapping_records(), "library-adapter-boundaries.jsonl": boundary_records(),
        "innovations.jsonl": innovation_records(), "gaps.jsonl": gap_records(),
    }
    # Link evidence records back into offers without conflating documented/probed limits or list/measured cost.
    evidence_by_subject: dict[str, list[str]] = {}
    for record in groups["resource-limit-cost-evidence.jsonl"]:
        evidence_by_subject.setdefault(record["subject_ref"], []).append(record["resource_evidence_id"])
    for offer in groups["concrete-offers.jsonl"]:
        offer["documented_limit_refs"] = sorted(evidence_by_subject.get(offer["offer_id"], []))
    for name, records in groups.items():
        dump_jsonl(ROOT / name, records)
    dump_json(ROOT / "metamodel.json", metamodel())
    core_count = sum(len(groups[name]) for name in ["capability-classes.jsonl", "concrete-offers.jsonl", "target-profiles.jsonl", "target-occurrences.jsonl", "decisions.jsonl"])
    manifest = {
        "registry_id": "san.provider-target-physical-binding-registry", "edition": EDITION, "status": "candidate", "completion_claim": False,
        "generated_by": "build_registry.py", "retrieved_at": RETRIEVED,
        "counts": {name.removesuffix(".jsonl").replace("-", "_"): len(records) for name, records in groups.items()},
        "capability_offer_target_decision_records": core_count,
        "thresholds": {"primary_official_sources": 60, "context_candidates": 30, "capability_offer_target_decision_records": 180, "innovations_2021_2026": 20},
        "completion_note": "Finite candidate seed only; enumeration is not proof of provider, engine, service or target completeness.",
    }
    dump_json(ROOT / "manifest.json", manifest)


if __name__ == "__main__":
    main()
