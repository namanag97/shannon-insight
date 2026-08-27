#!/usr/bin/env python3
"""Validate source-system corpus structure, axes, references and inherited coverage."""

from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
LEGACY = ROOT / "research/SAN_DATA_ANALYTICS_GPT_PRO_HANDOFF_2026-08-12/current_work/analytics_landscape/compiler/source_system_taxonomy.json"


def load(path: Path):
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def load_jsonl(path: Path) -> list[dict]:
    values = []
    with path.open(encoding="utf-8") as handle:
        for number, line in enumerate(handle, 1):
            if line.strip():
                try:
                    values.append(json.loads(line))
                except json.JSONDecodeError as error:
                    raise ValueError(f"{path}:{number}: {error}") from error
    return values


def main() -> int:
    errors: list[str] = []
    axes = load(HERE / "classification-axes.json")["axes"]
    records = load_jsonl(HERE / "source-classes.jsonl")
    evidence = load_jsonl(HERE / "evidence-sources.jsonl")
    tests = load(HERE / "verification-tests.json")["tests"]
    coverage = load(HERE / "coverage-report.json")
    gaps = load(HERE / "coverage-gaps.json")
    compiler = load(HERE / "compiler-contract.json")

    # Parse every published schema even when the optional jsonschema package is unavailable.
    schema_files = [
        "source-system-class.schema.json", "evidence-source.schema.json",
        "source-occurrence.schema.json", "connector-capability.schema.json",
        "unknown-source-gap.schema.json",
    ]
    schemas = {name: load(HERE / name) for name in schema_files}
    for name, schema in schemas.items():
        if schema.get("$schema") != "https://json-schema.org/draft/2020-12/schema":
            errors.append(f"{name}: must declare JSON Schema 2020-12")

    class_ids = [record.get("class_id") for record in records]
    if len(class_ids) != len(set(class_ids)):
        errors.append("duplicate source class IDs")
    evidence_ids = {item.get("evidence_id") for item in evidence}
    if len(evidence_ids) != len(evidence):
        errors.append("duplicate evidence IDs")
    test_ids = {item.get("test_id") for item in tests}
    if len(test_ids) != len(tests):
        errors.append("duplicate verification test IDs")

    required_top = {
        "record_kind", "class_id", "edition", "status", "name", "family_id",
        "profile_id", "definition", "not_a_vendor_type", "classification_rule",
        "authority", "object_model", "interfaces", "schema", "temporality",
        "order_finality", "transactions", "security", "limits", "hazards",
        "verification", "evidence_refs", "inherited_seed_refs",
    }
    required_nested = {
        "authority": {"role", "field_level_override_required", "replica_may_lag"},
        "object_model": {"object_kinds", "logical_models", "payload_shapes", "identity_scope", "identity_reuse_must_be_probed"},
        "interfaces": {"discovery_modes", "read_modes", "write_modes", "change_modes", "access_topologies"},
        "schema": {"mode", "compatibility_policy", "registry_or_contract", "unknown_field_policy", "key_and_constraint_discovery_required", "drift_observable"},
        "temporality": {"time_axes", "clock_model", "timezone_and_calendar_required", "watermark_or_cursor", "late_data", "retention"},
        "order_finality": {"ordering_scope", "ordering_key", "gap_signal", "duplicate_semantics", "finality_model", "corrections", "deletion_semantics"},
        "transactions": {"boundary", "consistency_model", "snapshot_cut", "cross_object_atomicity"},
        "security": {"authentication", "authorization", "encryption", "tenant_boundary", "auditability", "sensitivity_default", "write_or_command_default"},
        "limits": {"class_values_are_portable", "must_probe", "hard_limit_behavior"},
    }
    for index, record in enumerate(records, 1):
        class_id = record.get("class_id", f"line:{index}")
        missing = sorted(required_top - set(record))
        if missing:
            errors.append(f"{class_id}: missing top-level {missing}")
            continue
        if class_id != f"source.{record['family_id']}.{class_id.rsplit('.', 1)[-1]}":
            errors.append(f"{class_id}: family and class ID disagree")
        if record["record_kind"] != "source_system_capability_class" or record["not_a_vendor_type"] is not True:
            errors.append(f"{class_id}: invalid record kind/vendor law")
        for section, required in required_nested.items():
            missing_nested = sorted(required - set(record[section]))
            if missing_nested:
                errors.append(f"{class_id}: {section} missing {missing_nested}")
        if record["family_id"] not in axes["family_id"]:
            errors.append(f"{class_id}: unknown family {record['family_id']}")
        axis_bindings = [
            ("authority_role", [record["authority"]["role"]]),
            ("logical_model", record["object_model"]["logical_models"]),
            ("payload_shape", record["object_model"]["payload_shapes"]),
            ("discovery_mode", record["interfaces"]["discovery_modes"]),
            ("read_mode", record["interfaces"]["read_modes"]),
            ("write_mode", record["interfaces"]["write_modes"]),
            ("change_mode", record["interfaces"]["change_modes"]),
            ("schema_mode", [record["schema"]["mode"]]),
            ("compatibility_policy", [record["schema"]["compatibility_policy"]]),
            ("time_axis", record["temporality"]["time_axes"]),
            ("clock_model", [record["temporality"]["clock_model"]]),
            ("ordering_scope", [record["order_finality"]["ordering_scope"]]),
            ("finality_model", [record["order_finality"]["finality_model"]]),
            ("deletion_semantics", record["order_finality"]["deletion_semantics"]),
            ("transaction_boundary", [record["transactions"]["boundary"]]),
            ("consistency_model", [record["transactions"]["consistency_model"]]),
            ("access_topology", record["interfaces"]["access_topologies"]),
            ("sensitivity_default", [record["security"]["sensitivity_default"]]),
        ]
        for axis, values in axis_bindings:
            unknown = sorted(set(values) - set(axes[axis]))
            if unknown:
                errors.append(f"{class_id}: unknown {axis} values {unknown}")
        unknown_evidence = sorted(set(record["evidence_refs"]) - evidence_ids)
        if unknown_evidence:
            errors.append(f"{class_id}: unknown evidence {unknown_evidence}")
        unknown_tests = sorted(set(record["verification"]) - test_ids)
        if unknown_tests:
            errors.append(f"{class_id}: unknown verification tests {unknown_tests}")
        if len(record["hazards"]) < 5:
            errors.append(f"{class_id}: fewer than five hazards")
        if len(record["verification"]) < 6:
            errors.append(f"{class_id}: fewer than six verification obligations")
        if record["limits"]["class_values_are_portable"] is not False:
            errors.append(f"{class_id}: numerical class limits must not be portable defaults")
        forbidden = ("openai", "anthropic", "snowflake", "salesforce", "sap", "oracle", "microsoft")
        searchable = f"{class_id} {record['name']} {record['definition']}".lower()
        if any(token in searchable for token in forbidden):
            errors.append(f"{class_id}: vendor-shaped class identity")
        llm_forbidden = ("large language model", "prompt store", "rag store", "agent memory")
        if any(token in searchable for token in llm_forbidden):
            errors.append(f"{class_id}: LLM-specific meaning leaked into core class")

    for item in evidence:
        if item.get("authority") != "primary":
            errors.append(f"{item.get('evidence_id')}: non-primary evidence")
        if not item.get("url", "").startswith("https://"):
            errors.append(f"{item.get('evidence_id')}: non-HTTPS evidence URL")
        if not item.get("supports_surfaces"):
            errors.append(f"{item.get('evidence_id')}: no supported surfaces")

    if len(records) < 100:
        errors.append(f"expected >=100 source classes, found {len(records)}")
    if len(evidence) < 25:
        errors.append(f"expected >=25 primary sources, found {len(evidence)}")
    if set(record["family_id"] for record in records) != set(axes["family_id"]):
        errors.append("not every declared family has a record")
    if coverage.get("class_records") != len(records) or coverage.get("primary_evidence_records") != len(evidence):
        errors.append("coverage report counts are stale")
    if coverage.get("completion_claim") is not False or gaps.get("completion_claim") is not False:
        errors.append("open-world corpus must not claim completion before saturation evidence")
    if not compiler.get("forbidden_dispatch_keys") or not compiler.get("rules"):
        errors.append("compiler contract missing dispatch refusals or rules")

    # Honest inherited audit and complete stable crosswalk.
    legacy = load(LEGACY)
    legacy_ids = {item["id"] for item in legacy["source_classes"]}
    replacements: dict[str, list[str]] = defaultdict(list)
    for record in records:
        for inherited_id in record["inherited_seed_refs"]:
            replacements[inherited_id].append(record["class_id"])
    unmapped = sorted(legacy_ids - set(replacements))
    unknown_legacy_refs = sorted(set(replacements) - legacy_ids)
    if unmapped:
        errors.append(f"unmapped inherited source classes: {unmapped}")
    if unknown_legacy_refs:
        errors.append(f"unknown inherited source refs: {unknown_legacy_refs}")

    legacy_axis_map = {
        "family": "family", "logical_models": "logical_model", "read_modes": "read_mode",
        "write_modes": "write_mode", "schema_mode": "schema_mode", "ordering": "ordering",
        "consistency": "consistency", "temporal_support": "temporal_support",
    }
    legacy_unknown_values: dict[str, list[str]] = defaultdict(list)
    for record in legacy["source_classes"]:
        for field, legacy_axis in legacy_axis_map.items():
            values = record.get(field, [])
            if not isinstance(values, list):
                values = [values]
            declared = set(legacy["axes"].get(legacy_axis, []))
            for value in values:
                if value not in declared:
                    legacy_unknown_values[legacy_axis].append(value)

    crosswalk = [
        {
            "legacy_id": legacy_id,
            "replacement_class_ids": sorted(replacements.get(legacy_id, [])),
            "migration_kind": "split" if len(replacements.get(legacy_id, [])) > 1 else "refined",
            "note": "The inherited label is retained only as migration evidence; use stable replacement class IDs for new mappings."
        }
        for legacy_id in sorted(legacy_ids)
    ]
    inherited_audit = {
        "audit_id": "san.domain-atlas.source-system-inherited-audit",
        "edition": 1,
        "as_of": "2026-08-25",
        "legacy_records": len(legacy_ids),
        "legacy_metadata_status": legacy["metadata"].get("status"),
        "legacy_declared_axis_value_violations": {key: sorted(set(values)) for key, values in sorted(legacy_unknown_values.items())},
        "legacy_missing_required_universe_surfaces": ["authority", "objects", "discovery", "security", "limits", "cost", "verification", "evidence"],
        "legacy_records_mapped": len(set(replacements) & legacy_ids),
        "legacy_records_unmapped": unmapped,
        "unknown_legacy_refs": unknown_legacy_refs,
        "crosswalk": crosswalk,
        "replacement_class_records": len(records),
        "standing": "superseded_seed_with_complete_crosswalk" if not unmapped and not unknown_legacy_refs else "incomplete_crosswalk",
    }
    (HERE / "inherited-audit.json").write_text(json.dumps(inherited_audit, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    # If jsonschema is present, run the normative schemas too; manual checks above remain dependency-free.
    try:
        import jsonschema  # type: ignore
    except ImportError:
        jsonschema = None
    if jsonschema:
        validator = jsonschema.Draft202012Validator(schemas["source-system-class.schema.json"])
        for record in records:
            for error in validator.iter_errors(record):
                errors.append(f"{record['class_id']}: schema: {error.message}")
        evidence_validator = jsonschema.Draft202012Validator(schemas["evidence-source.schema.json"])
        for item in evidence:
            for error in evidence_validator.iter_errors(item):
                errors.append(f"{item['evidence_id']}: schema: {error.message}")

    if errors:
        print("FAIL source-system universe")
        for error in errors:
            print(f"- {error}")
        return 1
    print(
        "PASS source-system universe: "
        f"{len(records)} classes, {len(axes['family_id'])} families, {len(axes)} axes, "
        f"{len(evidence)} primary sources/{len({item['issuer'] for item in evidence})} issuers, "
        f"{len(legacy_ids)} inherited classes mapped"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
