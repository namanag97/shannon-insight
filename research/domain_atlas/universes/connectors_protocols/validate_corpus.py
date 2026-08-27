#!/usr/bin/env python3
"""Dependency-free integrity checks plus optional Draft 2020-12 validation."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


FILE_SCHEMAS = {
    "bounded-context-candidates.jsonl": "bounded-context.schema.json",
    "protocols.jsonl": "protocol.schema.json",
    "capabilities.jsonl": "capability.schema.json",
    "operations.jsonl": "operation.schema.json",
    "decisions.jsonl": "decision.schema.json",
    "lifecycles.jsonl": "lifecycle.schema.json",
    "connector-classes.jsonl": "connector-class.schema.json",
    "implementation-artifacts.jsonl": "implementation-artifact.schema.json",
    "deployed-connector-occurrences.jsonl": "deployed-connector-occurrence.schema.json",
    "evidence.jsonl": "evidence.schema.json",
    "innovations-2021-2026.jsonl": "innovation.schema.json",
    "compiler-requirements.jsonl": "compiler-contract.schema.json",
    "capability-offer-templates.jsonl": "compiler-contract.schema.json",
    "compiler-mappings.jsonl": "compiler-contract.schema.json",
    "library-boundaries.jsonl": "library-boundary.schema.json",
    "conformance-tests.jsonl": "conformance-test.schema.json",
    "cross-universe-mappings.jsonl": "crosswalk.schema.json",
    "gaps.jsonl": "gap.schema.json",
    "negative-twins.jsonl": "negative-twin.schema.json",
}


ID_FIELDS = {
    "bounded-context-candidates.jsonl": "context_id", "protocols.jsonl": "protocol_id",
    "capabilities.jsonl": "capability_id", "operations.jsonl": "operation_id", "decisions.jsonl": "decision_id",
    "lifecycles.jsonl": "lifecycle_id", "connector-classes.jsonl": "connector_class_id",
    "implementation-artifacts.jsonl": "artifact_id", "deployed-connector-occurrences.jsonl": "occurrence_id",
    "evidence.jsonl": "evidence_id", "innovations-2021-2026.jsonl": "innovation_id",
    "compiler-requirements.jsonl": "compiler_record_id", "capability-offer-templates.jsonl": "compiler_record_id",
    "compiler-mappings.jsonl": "compiler_record_id", "library-boundaries.jsonl": "library_id",
    "conformance-tests.jsonl": "test_id", "cross-universe-mappings.jsonl": "crosswalk_id",
    "gaps.jsonl": "gap_id", "negative-twins.jsonl": "twin_id",
}


def load_json(path: Path):
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def load_jsonl(path: Path) -> list[dict]:
    values = []
    with path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            if not line.strip():
                continue
            try:
                value = json.loads(line)
            except json.JSONDecodeError as error:
                raise ValueError(f"{path}:{line_number}: {error}") from error
            if not isinstance(value, dict):
                raise ValueError(f"{path}:{line_number}: record must be an object")
            values.append(value)
    return values


def file_digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_id_set(path: Path, field: str) -> set[str]:
    return {item[field] for item in load_jsonl(path)}


def main() -> int:
    errors: list[str] = []
    records = {filename: load_jsonl(HERE / filename) for filename in FILE_SCHEMAS}
    schemas = {name: load_json(HERE / "schemas" / name) for name in set(FILE_SCHEMAS.values())}
    coverage = load_json(HERE / "coverage-report.json")
    manifest = load_json(HERE / "manifest.json")
    matrix = load_json(HERE / "coverage-matrix.json")
    harness = load_json(HERE / "examples/conformance-harness.json")
    hostile = load_json(HERE / "examples/hostile-scenarios.json")

    for schema_name, schema in schemas.items():
        if schema.get("$schema") != "https://json-schema.org/draft/2020-12/schema":
            errors.append(f"{schema_name}: must declare JSON Schema Draft 2020-12")

    all_local_ids: set[str] = set()
    ids_by_file: dict[str, set[str]] = {}
    for filename, values in records.items():
        field = ID_FIELDS[filename]
        identifiers = [item.get(field) for item in values]
        if None in identifiers:
            errors.append(f"{filename}: missing {field}")
        if len(identifiers) != len(set(identifiers)):
            errors.append(f"{filename}: duplicate identifiers")
        overlap = all_local_ids & set(identifiers)
        if overlap:
            errors.append(f"{filename}: IDs collide across record kinds: {sorted(overlap)[:3]}")
        ids_by_file[filename] = set(identifiers)
        all_local_ids.update(identifiers)

    contexts = ids_by_file["bounded-context-candidates.jsonl"]
    protocols = ids_by_file["protocols.jsonl"]
    capabilities = ids_by_file["capabilities.jsonl"]
    operations = ids_by_file["operations.jsonl"]
    decisions = ids_by_file["decisions.jsonl"]
    classes = ids_by_file["connector-classes.jsonl"]
    artifacts = ids_by_file["implementation-artifacts.jsonl"]
    evidence = ids_by_file["evidence.jsonl"]
    tests = ids_by_file["conformance-tests.jsonl"]
    compiler_ids = ids_by_file["compiler-requirements.jsonl"] | ids_by_file["capability-offer-templates.jsonl"] | ids_by_file["compiler-mappings.jsonl"]

    source_path = ROOT / "domain_atlas/universes/source_systems/source-classes.jsonl"
    source_classes = load_id_set(source_path, "class_id")
    external_materialized: set[str] = set(source_classes)
    for relative, field in [
        ("domain_atlas/universes/pipeline_dataflow/context-candidates.jsonl", "context_id"),
        ("domain_atlas/universes/data_shapes/bounded-context-candidates.jsonl", "context_id"),
        ("domain_atlas/universes/security_privacy_trust/bounded-context-candidates.jsonl", "context_id"),
        ("domain_atlas/universes/quality_observability_reconciliation/bounded-context-candidates.jsonl", "context_id"),
    ]:
        external_materialized.update(load_id_set(ROOT / relative, field))

    def require_subset(label: str, refs: list[str], allowed: set[str]) -> None:
        unknown = sorted(set(refs) - allowed)
        if unknown:
            errors.append(f"{label}: unknown refs {unknown[:6]}")

    for item in records["bounded-context-candidates.jsonl"]:
        require_subset(item["context_id"] + ".decisions", item["decision_refs"], decisions)
        require_subset(item["context_id"] + ".evidence", item["evidence_refs"], evidence)
    for item in records["protocols.jsonl"]:
        require_subset(item["protocol_id"] + ".sources", item["source_class_refs"], source_classes)
        require_subset(item["protocol_id"] + ".contexts", item["context_refs"], contexts)
        require_subset(item["protocol_id"] + ".evidence", item["evidence_refs"], evidence)
        if item.get("not_data_model") is not True:
            errors.append(f"{item['protocol_id']}: protocol/data-model distinction absent")
        if item["change_and_resume"].get("read_cursor") != "not_interchangeable_with_cdc_resume":
            errors.append(f"{item['protocol_id']}: read cursor/CDC token distinction absent")
        if item["delivery_semantics"].get("transport_success") != "not_source_acceptance":
            errors.append(f"{item['protocol_id']}: transport/source acceptance distinction absent")
        if item["delivery_semantics"].get("exactly_once") != "not_claimed_end_to_end":
            errors.append(f"{item['protocol_id']}: unsafe exactly-once claim")
    for item in records["capabilities.jsonl"]:
        require_subset(item["capability_id"] + ".context", [item["owner_context_ref"]], contexts)
        require_subset(item["capability_id"] + ".operations", item["operation_refs"], operations)
        require_subset(item["capability_id"] + ".decisions", item["decision_refs"], decisions)
        require_subset(item["capability_id"] + ".evidence", item["evidence_refs"], evidence)
    for item in records["operations.jsonl"]:
        require_subset(item["operation_id"] + ".context", [item["owner_context_ref"]], contexts)
        require_subset(item["operation_id"] + ".evidence", item["evidence_refs"], evidence)
    for item in records["decisions.jsonl"]:
        require_subset(item["decision_id"] + ".context", [item["owner_context_ref"]], contexts)
        if item["default_law"] != "forbidden":
            errors.append(f"{item['decision_id']}: material unknowns must fail closed")
    for item in records["connector-classes.jsonl"]:
        require_subset(item["connector_class_id"] + ".sources", item["source_class_refs"], source_classes)
        require_subset(item["connector_class_id"] + ".protocols", item["protocol_refs"], protocols)
        require_subset(item["connector_class_id"] + ".capabilities", item["required_capability_refs"], capabilities)
        require_subset(item["connector_class_id"] + ".operations", item["operation_refs"], operations)
        require_subset(item["connector_class_id"] + ".evidence", item["evidence_refs"], evidence)
    for item in records["implementation-artifacts.jsonl"]:
        require_subset(item["artifact_id"] + ".classes", item["connector_class_refs"], classes)
        require_subset(item["artifact_id"] + ".protocols", item["protocol_profiles"], protocols)
        require_subset(item["artifact_id"] + ".declared", item["declared_capability_refs"], capabilities)
        require_subset(item["artifact_id"] + ".qualified", item["qualified_capability_refs"], capabilities)
        if item["binding_eligible"] or item["qualified_capability_refs"]:
            errors.append(f"{item['artifact_id']}: unexecuted reference fixture cannot be binding-eligible or qualified")
    for item in records["deployed-connector-occurrences.jsonl"]:
        require_subset(item["occurrence_id"] + ".class", [item["connector_class_ref"]], classes)
        require_subset(item["occurrence_id"] + ".artifact", [item["artifact_ref"]], artifacts)
        require_subset(item["occurrence_id"] + ".operations", item["enabled_operations"], operations)
        if item["occurrence_kind"] == "registered_deployment_candidate":
            errors.append(f"{item['occurrence_id']}: corpus must not fabricate a registered deployment")
        if item["binding_eligible"] or item["qualification"].get("live_probe") or item["qualification"].get("qualified"):
            errors.append(f"{item['occurrence_id']}: fixture cannot be live, qualified, or binding eligible")
        if item.get("credential_references_only") is not True:
            errors.append(f"{item['occurrence_id']}: credentials must be references only")
    for item in records["innovations-2021-2026.jsonl"]:
        require_subset(item["innovation_id"] + ".protocols", item["protocol_refs"], protocols)
        require_subset(item["innovation_id"] + ".evidence", item["evidence_refs"], evidence)
        if item["non_llm"] is not True or not 2021 <= item["year"] <= 2026:
            errors.append(f"{item['innovation_id']}: innovation window/non-LLM law failed")
    for filename in ["compiler-requirements.jsonl", "capability-offer-templates.jsonl", "compiler-mappings.jsonl"]:
        expected_kind = {"compiler-requirements.jsonl": "requirement", "capability-offer-templates.jsonl": "offer_template", "compiler-mappings.jsonl": "mapping"}[filename]
        for item in records[filename]:
            if item["record_kind"] != expected_kind:
                errors.append(f"{item['compiler_record_id']}: wrong record kind for {filename}")
            require_subset(item["compiler_record_id"] + ".capabilities", item["capability_refs"], capabilities)
            require_subset(item["compiler_record_id"] + ".operations", item["operation_refs"], operations)
            if item["record_kind"] == "mapping":
                require_subset(item["compiler_record_id"] + ".subject", [item["subject_ref"]], compiler_ids)
            else:
                require_subset(item["compiler_record_id"] + ".subject", [item["subject_ref"]], contexts)
            if item["fallback_law"] != "refuse":
                errors.append(f"{item['compiler_record_id']}: fallback must fail closed")
    for item in records["library-boundaries.jsonl"]:
        require_subset(item["library_id"] + ".evidence", item["evidence_refs"], evidence)
    for item in records["conformance-tests.jsonl"]:
        require_subset(item["test_id"] + ".evidence", item["evidence_refs"], evidence)
        if set(item["allowed_outcomes"]) != {"pass", "fail", "not_supported", "not_authorized", "inconclusive"}:
            errors.append(f"{item['test_id']}: conformance outcome vocabulary incomplete")
    for item in records["negative-twins.jsonl"]:
        require_subset(item["twin_id"] + ".tests", item["test_refs"], tests)
    for item in records["gaps.jsonl"]:
        require_subset(item["gap_id"] + ".subject", [item["subject_ref"]], all_local_ids)
        require_subset(item["gap_id"] + ".evidence", item["evidence_refs"], evidence)
    for item in records["cross-universe-mappings.jsonl"]:
        require_subset(item["crosswalk_id"] + ".local", item["local_refs"], all_local_ids)
        external_path = ROOT.parent / item["external_path"] if item["external_path"].startswith("research/") else ROOT / item["external_path"]
        if not external_path.exists():
            errors.append(f"{item['crosswalk_id']}: external path missing: {external_path}")
        if item["reference_status"] == "materialized_validated":
            require_subset(item["crosswalk_id"] + ".external", item["external_refs"], external_materialized)

    evidence_rows = records["evidence.jsonl"]
    if any(item["authority"] != "primary" for item in evidence_rows):
        errors.append("evidence: every source must be primary/official")
    if len({item["url"] for item in evidence_rows}) != len(evidence_rows):
        errors.append("evidence: duplicate URLs weaken exact source accounting")
    if any(not item["url"].startswith("https://") for item in evidence_rows):
        errors.append("evidence: all URLs must use HTTPS")

    core_files = ["protocols.jsonl", "capabilities.jsonl", "operations.jsonl", "decisions.jsonl", "lifecycles.jsonl", "connector-classes.jsonl"]
    forbidden = ("large language model", "generative model", "prompt store", "rag store", "agent memory")
    for filename in core_files:
        text = (HERE / filename).read_text(encoding="utf-8").lower()
        for token in forbidden:
            if token in text:
                errors.append(f"{filename}: forbidden core dependency {token!r}")

    core_count = sum(len(records[name]) for name in ["protocols.jsonl", "capabilities.jsonl", "operations.jsonl", "decisions.jsonl", "lifecycles.jsonl"])
    thresholds = [
        (len(records["bounded-context-candidates.jsonl"]) >= 45, "expected >=45 bounded contexts"),
        (core_count >= 220, "expected >=220 protocol/capability/operation/decision/lifecycle records"),
        (len(evidence_rows) >= 70, "expected >=70 primary/official evidence sources"),
        (len(records["innovations-2021-2026.jsonl"]) >= 20, "expected >=20 innovations from 2021-2026"),
        (len(records["connector-classes.jsonl"]) >= 45, "expected >=45 connector classes"),
        (len(records["conformance-tests.jsonl"]) >= 30, "expected >=30 conformance tests"),
    ]
    errors.extend(message for passed, message in thresholds if not passed)

    expected_counts = {filename.removesuffix(".jsonl").replace("-", "_"): len(values) for filename, values in sorted(records.items())}
    if coverage.get("counts") != expected_counts:
        errors.append("coverage-report.json counts are stale")
    if coverage.get("core_protocol_capability_operation_decision_lifecycle_records") != core_count:
        errors.append("coverage-report.json core count is stale")
    if coverage.get("completion_claim") is not False or manifest.get("completion_claim") is not False:
        errors.append("open-world candidate must not claim completeness")
    if coverage.get("real_deployed_occurrences") != 0 or coverage.get("live_probes") != 0 or coverage.get("credentials") != 0:
        errors.append("coverage report must not claim deployments, probes, or credentials")
    if set(harness.get("test_refs", [])) != tests:
        errors.append("conformance harness test references are stale")
    if hostile.get("no_credentials") is not True or hostile.get("no_live_probes") is not True:
        errors.append("hostile scenarios must explicitly exclude credentials/live probes")
    required_dimensions = {
        "database_wire_query_change", "file_object_transfer", "rest_graphql_grpc_soap_odata", "webhooks",
        "event_messaging", "bulk_export_import", "saas_apis", "industrial_ot_iot", "healthcare",
        "finance_market_messaging", "geospatial_scientific", "edi", "email_collaboration", "mainframe_legacy",
        "filesystem_object_block", "browser_client_telemetry", "command_writeback", "discovery_introspection",
        "authentication_authorization_secrets", "snapshot_cut_cursor_resume_change", "schema_type_time_order_finality",
        "limits_rate_quota_cost", "retry_idempotency_cancellation", "partition_recovery", "observability_receipts",
        "versioning_deprecation", "licensing_supply_chain",
    }
    matrix_dimensions = {item["dimension"] for item in matrix.get("dimensions", [])}
    if matrix_dimensions != required_dimensions:
        errors.append(f"coverage matrix dimensions disagree: missing={sorted(required_dimensions - matrix_dimensions)}, extra={sorted(matrix_dimensions - required_dimensions)}")
    for item in matrix.get("dimensions", []):
        require_subset("coverage." + item["dimension"] + ".protocols", item["protocol_refs"], protocols)
        require_subset("coverage." + item["dimension"] + ".classes", item["connector_class_refs"], classes)
        require_subset("coverage." + item["dimension"] + ".contexts", item["context_refs"], contexts)

    try:
        import jsonschema  # type: ignore
    except ImportError:
        jsonschema = None
    if jsonschema:
        for filename, schema_name in FILE_SCHEMAS.items():
            validator = jsonschema.Draft202012Validator(schemas[schema_name])
            for item in records[filename]:
                for error in validator.iter_errors(item):
                    errors.append(f"{filename}:{item.get(ID_FIELDS[filename])}: schema: {error.message}")

    # Prove regeneration is byte deterministic for every generated artifact.
    generated_paths = [HERE / filename for filename in FILE_SCHEMAS]
    generated_paths += [HERE / "coverage-report.json", HERE / "coverage-matrix.json", HERE / "manifest.json", HERE / "examples/conformance-harness.json", HERE / "examples/hostile-scenarios.json"]
    generated_paths += sorted((HERE / "schemas").glob("*.schema.json"))
    before = {path: file_digest(path) for path in generated_paths}
    result = subprocess.run([sys.executable, str(HERE / "build_corpus.py")], cwd=ROOT.parent, capture_output=True, text=True, check=False)
    if result.returncode:
        errors.append(f"deterministic rebuild failed: {result.stderr or result.stdout}")
    after = {path: file_digest(path) for path in generated_paths}
    changed = [str(path.relative_to(HERE)) for path in generated_paths if before[path] != after[path]]
    if changed:
        errors.append(f"generator is not deterministic: {changed}")

    if errors:
        print("FAIL connectors/protocols corpus")
        for error in errors:
            print(f"- {error}")
        return 1
    print(
        "PASS connectors/protocols corpus: "
        f"{len(contexts)} contexts, {len(protocols)} protocols, {len(capabilities)} capabilities, "
        f"{len(operations)} operations, {len(decisions)} decisions, {len(records['lifecycles.jsonl'])} lifecycles, "
        f"{core_count} core records, {len(classes)} connector classes, {len(evidence)} primary/official sources, "
        f"{len(records['innovations-2021-2026.jsonl'])} innovations, {len(tests)} conformance tests; deterministic rebuild PASS"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
