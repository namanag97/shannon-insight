#!/usr/bin/env python3
"""Validate persistence/lakehouse structure, references and boundary laws."""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path

from build_corpus import PROFILE_CAPABILITIES


ROOT = Path(__file__).resolve().parent
GLOBAL_DECISION_SCHEMA = ROOT.parents[1] / "compiler" / "decision-point.schema.json"
GLOBAL_LIBRARY_SCHEMA = ROOT.parents[1] / "compiler" / "library-contribution.schema.json"


def validate_manifest() -> None:
    manifest = json.loads((ROOT / "manifest.json").read_text())
    assert manifest["completion_claim"] is False
    for name, claim in manifest["files"].items():
        data = (ROOT / name).read_bytes()
        assert len(data) == claim["bytes"] and hashlib.sha256(data).hexdigest() == claim["sha256"], name


def load_jsonl(name: str) -> list[dict]:
    rows = []
    for line_no, line in enumerate((ROOT / name).read_text(encoding="utf-8").splitlines(), 1):
        assert line.strip(), f"{name}:{line_no}: blank line"
        try:
            value = json.loads(line)
        except json.JSONDecodeError as exc:
            raise AssertionError(f"{name}:{line_no}: invalid JSON: {exc}") from exc
        assert isinstance(value, dict), f"{name}:{line_no}: expected object"
        rows.append(value)
    return rows


def unique(rows: list[dict], field: str, name: str) -> set[str]:
    values = [row.get(field) for row in rows]
    assert all(isinstance(value, str) and value for value in values), f"{name}: missing {field}"
    repeated = [value for value, count in Counter(values).items() if count > 1]
    assert not repeated, f"{name}: duplicate {field}: {repeated[:5]}"
    return set(values)


def require_refs(rows: list[dict], field: str, allowed: set[str], name: str, nonempty: bool = False) -> None:
    for index, row in enumerate(rows, 1):
        refs = row.get(field)
        assert isinstance(refs, list), f"{name}:{index}: {field} must be array"
        if nonempty:
            assert refs, f"{name}:{index}: {field} must be nonempty"
        unknown = set(refs) - allowed
        assert not unknown, f"{name}:{index}: unknown {field}: {sorted(unknown)[:5]}"


def schema_validate(instance_rows: list[dict], schema_path: Path, name: str) -> None:
    try:
        import jsonschema
    except ImportError:
        return
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    validator = jsonschema.Draft202012Validator(schema)
    for index, row in enumerate(instance_rows, 1):
        errors = sorted(validator.iter_errors(row), key=lambda error: list(error.path))
        assert not errors, f"{name}:{index}: schema error: {errors[0].message}"


def main() -> None:
    validate_manifest()
    sources = load_jsonl("sources.jsonl")
    contexts = load_jsonl("bounded-contexts.jsonl")
    decisions = load_jsonl("decision-points.jsonl")
    capabilities = (
        load_jsonl("storage-capabilities.jsonl")
        + load_jsonl("table-capabilities.jsonl")
        + load_jsonl("catalog-serving-capabilities.jsonl")
    )
    boundaries = load_jsonl("boundary-candidates.jsonl")
    libraries = load_jsonl("library-boundaries.jsonl")
    compiler = load_jsonl("compiler-mappings.jsonl")
    innovations = load_jsonl("innovations.jsonl")
    object_log_decisions = load_jsonl("object-log-decision-points.jsonl")
    object_log_architectures = load_jsonl("object-log-architectures.jsonl")
    object_log_compiler_contracts = load_jsonl("object-log-compiler-contracts.jsonl")
    relations = load_jsonl("context-map.jsonl")
    coverage = json.loads((ROOT / "coverage-report.json").read_text(encoding="utf-8"))
    gaps = json.loads((ROOT / "gaps.json").read_text(encoding="utf-8"))
    overlaps = json.loads((ROOT / "term-ownership-overlaps.json").read_text(encoding="utf-8"))

    source_ids = unique(sources, "source_id", "sources")
    context_ids = unique(contexts, "context_id", "contexts")
    decision_ids = unique(decisions, "decision_id", "decisions")
    capability_ids = unique(capabilities, "capability_id", "capabilities")
    boundary_ids = unique(boundaries, "candidate_id", "boundaries")
    library_ids = unique(libraries, "library_id", "libraries")
    global_library_ids = {
        row["library_id"]
        for row in (
            json.loads(line)
            for line in (ROOT.parents[1] / "compiler/library_registry/library-contributions.jsonl").read_text(encoding="utf-8").splitlines()
            if line.strip()
        )
    }
    innovation_ids = unique(innovations, "innovation_id", "innovations")
    architecture_ids = unique(object_log_architectures, "architecture_id", "object-log architectures")
    object_log_decision_ids = unique(object_log_decisions, "decision_id", "object-log decisions")
    unique(relations, "relation_id", "relations")

    assert len(sources) >= 50, "primary/official evidence regressed below 50 sources"
    assert len(contexts) >= 100, "bounded-context coverage regressed below 100 candidates"
    assert len(capabilities) >= 250, "capability coverage regressed below 250"
    assert len(decisions) >= 60, "decision surface regressed below 60"
    assert len(boundaries) >= 50, "boundary candidate coverage regressed below 50"
    assert len(libraries) == 38, "expected exactly the 38 library-kind boundary projections"
    assert len(innovations) >= 20, "five-year innovations regressed below 20"
    assert len(object_log_architectures) >= 21, "object-log architecture coverage regressed below 21"
    assert all(row["primary_or_official"] is True for row in sources)
    assert all(row["url"].startswith("https://") for row in sources)
    assert len({row["publisher"] for row in sources}) >= 25

    expected_families = {f"persistence.family.{name}" for name in [
        "physical_storage", "store_model", "file_format", "analytical_table",
        "catalog", "maintenance", "serving", "sharing_federation"
    ]}
    actual_families = {row["family_id"] for row in contexts}
    assert expected_families == actual_families, f"family mismatch: {expected_families ^ actual_families}"
    require_refs(contexts, "evidence_refs", source_ids, "contexts", nonempty=True)
    require_refs(contexts, "decision_refs", decision_ids, "contexts")
    require_refs(contexts, "capability_refs", capability_ids, "contexts", nonempty=True)
    for row in contexts:
        assert row["status"] == "candidate_not_adjudicated"
        assert "llm_dependency" not in row, "deterministic contexts must not carry ambient AI metadata"
        assert len(row["inside"]) >= 3 and len(row["outside"]) >= 2
        assert len(row["invariants"]) >= 3

    for row in decisions:
        assert row["owner_context_ref"] in context_ids
        assert row["default_law"] == "forbidden" and row["default_value"] is None
        assert len(row["allowed_values"]) >= 4

    require_refs(capabilities, "evidence_refs", source_ids, "capabilities", nonempty=True)
    require_refs(capabilities, "decision_refs", decision_ids, "capabilities")
    for row in capabilities:
        assert row["owner_context_ref"] in context_ids
        assert "llm_dependency" not in row, "deterministic capabilities must not carry ambient AI metadata"
        assert "result_unknown" in row["failure_states"]
        assert {"bytes_read", "bytes_written", "cpu_time", "memory_peak", "elapsed_time"} <= set(row["resource_dimensions"])
        assert "outcome" in row["receipt_fields"] and "decision_trace" in row["receipt_fields"]

    require_refs(boundaries, "evidence_refs", source_ids, "boundaries", nonempty=True)
    require_refs(boundaries, "decision_refs", decision_ids, "boundaries")
    require_refs(boundaries, "capability_refs", capability_ids, "boundaries")
    require_refs(boundaries, "requires", boundary_ids, "boundaries")
    boundary_by_id = {row["candidate_id"]: row for row in boundaries}
    for expected in [
        "persistence.boundary.format.parquet", "persistence.boundary.format.iceberg",
        "persistence.boundary.protocol.iceberg_rest", "persistence.boundary.implementation.polaris",
        "persistence.boundary.deployment.catalog", "persistence.boundary.product.analytical_table",
        "persistence.boundary.product.catalog_commit", "persistence.boundary.product.table_maintenance",
        "persistence.boundary.experience.lakehouse", "persistence.boundary.suite.lakehouse"
    ]:
        assert expected in boundary_by_id, f"missing anchor boundary {expected}"
    assert boundary_by_id["persistence.boundary.format.parquet"]["record_kind"] == "format"
    assert boundary_by_id["persistence.boundary.format.parquet"]["boundary_verdict"] == "not_a_product"
    assert boundary_by_id["persistence.boundary.protocol.iceberg_rest"]["record_kind"] == "protocol"
    assert boundary_by_id["persistence.boundary.implementation.polaris"]["record_kind"] == "implementation"
    assert boundary_by_id["persistence.boundary.experience.lakehouse"]["boundary_verdict"] == "compose_as_managed_experience"
    assert boundary_by_id["persistence.boundary.suite.lakehouse"]["boundary_verdict"] == "compose_as_suite"
    assert not boundary_by_id["persistence.boundary.experience.lakehouse"]["capability_refs"], "lakehouse experience must not acquire data-plane semantics"

    expected_library_ids = {
        f"library.persistence.{row['candidate_id'].removeprefix('persistence.boundary.lib.')}"
        for row in boundaries
        if row["record_kind"] in {
            "semantic_library", "algorithm_library", "runtime_library", "policy_pure",
            "test_oracle", "provider_adapter",
        }
    }
    assert library_ids == expected_library_ids
    for row in libraries:
        assert row["status"] == "specified"
        assert len(row["semantic_owner_refs"]) == 1
        assert set(row["semantic_owner_refs"]) <= context_ids
        assert set(row["semantic_owner_refs"]) <= set(row["contributes_to_context_refs"])
        assert set(row["contributes_to_context_refs"]) <= context_ids
        assert set(row["decision_refs"]) <= decision_ids
        assert set(row["evidence_refs"]) <= source_ids
        assert row["operation_refs"] and row["public_types"] and row["public_traits"]
        assert all(dep["ref"] in library_ids for dep in row["dependencies"])
        assert all(not ref.startswith("library.mae.") for ref in [
            *row["semantic_owner_refs"], *row["contributes_to_context_refs"],
            *row["requirement_refs"], *row["offer_refs"],
            *(dep["ref"] for dep in row["dependencies"]),
        ])
        assert not any("model" in law.casefold() or "agent" in law.casefold() for law in row["laws"]), (
            f"deterministic library {row['library_id']} contains ambient model/agent law"
        )
    recovery_objectives = next(row for row in libraries if row["library_id"] == "library.persistence.recovery_objectives")
    assert recovery_objectives["effect_boundary"] == "pure_no_io"
    assert {"RpoObjective", "RtoObjective", "RecoveryPointDistance", "RecoveryDuration", "ObjectiveAttainment", "MeasurementResidual"} <= set(recovery_objectives["public_types"])
    assert {"RecoveryObjectiveEvaluator", "RecoveryCutDistance", "RecoveryDurationMeasure"} <= set(recovery_objectives["public_traits"])
    assert any("declared RPO or RTO is an objective" in law for law in recovery_objectives["laws"])
    assert any("partial-scope-no-strengthening" in oracle for oracle in recovery_objectives["oracles"])
    cache_fill = next(row for row in libraries if row["library_id"] == "library.persistence.cache_fill_coordination")
    assert cache_fill["effect_boundary"] == "effectful_runtime"
    assert {"FillEquivalenceKey", "FillGenerationId", "FillLeaderLease", "FencingToken", "WaiterRegistration", "FillReceipt", "FillRefusal"} <= set(cache_fill["public_types"])
    assert {"CacheFillCoordinator", "FillLeasePort", "StaleEligibilityEvaluator"} <= set(cache_fill["public_traits"])
    assert any("one admitted leader" in law for law in cache_fill["laws"])
    assert any("linearizability-history-check" in oracle for oracle in cache_fill["oracles"])
    virtual_identity = next(row for row in libraries if row["library_id"] == "library.persistence.virtual_relation_identity")
    assert {"VirtualRelationId", "VirtualRelationEdition", "DefinitionCarrier", "SourceBindingSet", "SecurityExecutionProfile"} <= set(virtual_identity["public_types"])
    assert any("saved query" in law for law in virtual_identity["laws"])
    virtual_lifecycle = next(row for row in libraries if row["library_id"] == "library.persistence.virtual_relation_lifecycle")
    assert {"VirtualRelationDraft", "PublishedVirtualRelationEdition", "RecallDecision", "RetirementTombstone"} <= set(virtual_lifecycle["public_types"])
    assert any("Publishing an edition" in law for law in virtual_lifecycle["laws"])
    index_mutation = next(row for row in libraries if row["library_id"] == "library.persistence.index_mutation")
    assert index_mutation["effect_boundary"] == "effectful_runtime"
    assert {"IndexMutationId", "WriterEpoch", "MutationOrderToken", "MutationReceipt", "MutationRefusal"} <= set(index_mutation["public_types"])
    assert {"IndexMutationPort", "MutationOutcomeReconciler", "MutationFrontierProjector"} <= set(index_mutation["public_traits"])
    assert any("Source document occurrence" in law for law in index_mutation["laws"])
    assert any("idempotency-retry-and-unknown-outcome" in oracle for oracle in index_mutation["oracles"])
    search_visibility = next(row for row in libraries if row["library_id"] == "library.persistence.search_visibility")
    assert search_visibility["effect_boundary"] == "effectful_runtime"
    assert {"IndexMutationFrontier", "ShardVisibilityCut", "ReaderSnapshotId", "SearchVisibilityCut", "VisibilityRefusal"} <= set(search_visibility["public_types"])
    assert {"SearchVisibilityPublisher", "SearchVisibilityObserver", "DeleteDisappearanceVerifier"} <= set(search_visibility["public_traits"])
    assert any("Refresh may make a mutation searchable" in law for law in search_visibility["laws"])
    assert any("ack-commit-refresh-visibility" in oracle for oracle in search_visibility["oracles"])

    requirements = [row for row in compiler if row["record_kind"] == "capability_requirement"]
    offers = [row for row in compiler if row["record_kind"] == "capability_offer"]
    binding_rules = [row for row in compiler if row["record_kind"] == "binding_rule"]
    compiler_gaps = [row for row in compiler if row["record_kind"] == "compiler_gap"]
    requirement_ids = unique(requirements, "requirement_id", "requirements")
    offer_ids = unique(offers, "offer_id", "offers")
    unique(binding_rules, "binding_rule_id", "binding rules")
    unique(compiler_gaps, "gap_id", "compiler gaps")
    assert len(binding_rules) == len(PROFILE_CAPABILITIES)
    for row in requirements:
        assert row["capability_ref"] in capability_ids
        assert row["fallback_law"] == "refuse"
    for row in offers:
        assert row["capability_ref"] in capability_ids
        assert row["status"] == "candidate", "abstract provider classes must not masquerade as qualified deployments"
    for row in binding_rules:
        assert set(row["requirement_refs"]) <= requirement_ids
        assert set(row["eligible_offer_refs"]) <= offer_ids
        assert len(row["requirement_refs"]) == len(row["eligible_offer_refs"])
    assert any(row["blocking"] for row in compiler_gaps)

    require_refs(innovations, "evidence_refs", source_ids, "innovations", nonempty=True)
    assert innovation_ids
    for row in innovations:
        assert 2021 <= row["year"] <= 2026
        assert row["non_llm"] is True
        assert row["limitations"] and row["compiler_implications"]

    require_refs(object_log_architectures, "evidence_refs", source_ids, "object-log architectures", nonempty=True)
    require_refs(object_log_decisions, "evidence_refs", source_ids, "object-log decisions", nonempty=True)
    assert len(object_log_decisions) == 14
    for row in object_log_decisions:
        assert row["default_law"] == "forbidden" and row["default_value"] is None
        assert len(row["allowed_values"]) >= 5
    expected_architecture_classes = {
        "enabling_object_log_primitive", "direct_object_wal", "object_native_lsm",
        "shared_wal_object_store", "object_native_stream_log", "object_wal_async_index",
        "replicated_wal_object_history", "wal_parquet_object_state",
        "durable_collection_object_persist", "checkpointed_object_state",
        "object_native_search_index", "quorum_wal_object_archive",
        "direct_low_latency_object_oltp", "service_log_object_lsm", "object_native_catalog",
        "write_through_object_wal_checkpoint", "cdc_wal_to_analytical_table",
        "object_native_graph_lsm", "object_wal_columnar_database", "asynchronous_wal_shipping",
    }
    assert expected_architecture_classes <= {row["architecture_class"] for row in object_log_architectures}
    expected_workloads = {"oltp", "olap", "htap", "streaming_log", "vector_search", "full_text_search", "embedded_kv", "time_series", "incremental_view_maintenance", "streaming_database", "lakehouse_catalog"}
    actual_workloads = {workload for row in object_log_architectures for workload in row["workload_classes"]}
    assert expected_workloads <= actual_workloads
    assert "olhp" not in actual_workloads, "unresolved OLHP acronym must not be silently normalized into the workload vocabulary"
    for row in object_log_architectures:
        assert row["qualification_status"] != "qualified_deployment"
        assert [stage["order"] for stage in row["commit_path"]] == list(range(1, len(row["commit_path"]) + 1))
        assert any("boundary" in stage["acknowledgement_role"] for stage in row["commit_path"]), row["architecture_id"]
        assert len(row["compiler_decisions"]) >= 8
        assert set(row["decision_refs"]) == object_log_decision_ids
        assert len(row["non_collapse_laws"]) >= 5
        assert any("Acknowledged durability" in law for law in row["non_collapse_laws"])
        assert row["gaps"] and row["tradeoffs"] and row["enabled_capabilities"]
        assert "llm" not in json.dumps(row).casefold()
    assert architecture_ids

    architecture_requirements = [row for row in object_log_compiler_contracts if row["record_kind"] == "durability_architecture_requirement"]
    architecture_offers = [row for row in object_log_compiler_contracts if row["record_kind"] == "durability_architecture_offer"]
    architecture_rules = [row for row in object_log_compiler_contracts if row["record_kind"] == "durability_architecture_binding_rule"]
    architecture_requirement_ids = unique(architecture_requirements, "requirement_id", "object-log architecture requirements")
    architecture_offer_ids = unique(architecture_offers, "offer_id", "object-log architecture offers")
    unique(architecture_rules, "binding_rule_id", "object-log architecture binding rules")
    assert len(architecture_requirements) == len(architecture_rules) == 10
    assert len(architecture_offers) == len(object_log_architectures) == 21
    for row in architecture_requirements:
        assert set(row["decision_refs"]) == object_log_decision_ids
        assert set(row["required_library_refs"]) <= global_library_ids
        assert not set(row["missing_library_contracts"]) & global_library_ids
        for clause in row["required_capability_clauses"]:
            assert clause["operator"] in {"all", "any"}
            assert set(clause["capability_refs"]) <= capability_ids
        assert row["fallback_law"] == "refuse"
    offer_by_id = {row["offer_id"]: row for row in architecture_offers}
    for row in architecture_offers:
        assert row["architecture_ref"] in architecture_ids
        assert row["capability_claim_refs"] and set(row["capability_claim_refs"]) <= capability_ids
        assert set(row["decision_refs"]) == object_log_decision_ids
        assert row["qualified_deployment_count"] == 0
        assert row["portable"] is False and row["selectable"] is False
    requirement_by_id = {row["requirement_id"]: row for row in architecture_requirements}
    for row in architecture_rules:
        assert row["requirement_ref"] in architecture_requirement_ids
        assert set(row["eligible_architecture_offer_refs"]) <= architecture_offer_ids
        requirement = requirement_by_id[row["requirement_ref"]]
        expected = []
        for offer in architecture_offers:
            if offer["architecture_class"] not in requirement["allowed_architecture_classes"]:
                continue
            if not set(offer["workload_classes"]) & set(requirement["required_workload_classes_any"]):
                continue
            claims = set(offer["capability_claim_refs"])
            if all(
                set(clause["capability_refs"]) <= claims if clause["operator"] == "all"
                else bool(set(clause["capability_refs"]) & claims)
                for clause in requirement["required_capability_clauses"]
            ):
                expected.append(offer["offer_id"])
        assert row["eligible_architecture_offer_refs"] == sorted(expected)
        assert all(not offer_by_id[ref]["selectable"] for ref in row["eligible_architecture_offer_refs"])

    for row in relations:
        assert row["source_context_ref"] in context_ids
        assert row["target_context_ref"] in context_ids
        assert row["source_context_ref"] != row["target_context_ref"]

    assert coverage["completion_claim"] is False
    assert coverage["counts"]["sources"] == len(sources)
    assert coverage["counts"]["bounded_contexts"] == len(contexts)
    assert coverage["counts"]["capabilities"] == len(capabilities)
    assert coverage["counts"]["compiler_library_boundaries"] == len(libraries)
    assert coverage["counts"]["object_log_architectures"] == len(object_log_architectures)
    assert coverage["counts"]["object_log_decision_points"] == len(object_log_decisions)
    assert coverage["counts"]["object_log_compiler_contracts"] == len(object_log_compiler_contracts)
    assert coverage["terminology_findings"]["unresolved_user_term"] == "OLHP"
    assert coverage["terminology_findings"]["recognized_database_workloads"] == ["OLTP", "OLAP", "HTAP"]
    assert coverage["automation_posture"]["default"] == "deterministic_core"
    assert coverage["automation_posture"]["optional_extension_ref"] == "universe.model_agent_extension"
    assert gaps["completion_claim"] is False and len(gaps["gaps"]) >= 10
    assert overlaps["completion_claim"] is False
    assert overlaps["overlap_count"] == len(overlaps["overlaps"])

    schema_validate(sources, ROOT / "schemas/evidence-source.schema.json", "sources")
    schema_validate(contexts, ROOT / "schemas/bounded-context.schema.json", "contexts")
    schema_validate(capabilities, ROOT / "schemas/capability.schema.json", "capabilities")
    schema_validate(boundaries, ROOT / "schemas/boundary-candidate.schema.json", "boundaries")
    schema_validate(libraries, GLOBAL_LIBRARY_SCHEMA, "libraries")
    schema_validate(compiler, ROOT / "schemas/compiler-mapping.schema.json", "compiler")
    schema_validate(innovations, ROOT / "schemas/innovation.schema.json", "innovations")
    schema_validate(object_log_architectures, ROOT / "schemas/object-log-architecture.schema.json", "object-log architectures")
    schema_validate(object_log_decisions, ROOT / "schemas/object-log-decision.schema.json", "object-log decisions")
    schema_validate(object_log_compiler_contracts, ROOT / "schemas/object-log-compiler-contract.schema.json", "object-log compiler contracts")
    schema_validate(decisions, GLOBAL_DECISION_SCHEMA, "decisions")

    print(
        "PASS persistence/lakehouse corpus: "
        f"{len(sources)} sources, {len(contexts)} contexts, {len(capabilities)} capabilities, "
        f"{len(decisions)} decisions, {len(boundaries)} boundaries, {len(requirements)} requirements, "
        f"{len(libraries)} compiler libraries, {len(offers)} offers, {len(binding_rules)} binding rules, "
        f"{len(innovations)} innovations, {len(object_log_architectures)} object-log architectures, "
        f"{len(object_log_decisions)} object-log decisions, {len(object_log_compiler_contracts)} object-log compiler contracts"
    )


if __name__ == "__main__":
    main()
