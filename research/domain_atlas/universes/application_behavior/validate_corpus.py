#!/usr/bin/env python3
"""Fail-closed validation for the application-behavior candidate universe."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from collections.abc import Iterable
from pathlib import Path
from typing import Any

try:
    import jsonschema
except ImportError as exc:  # pragma: no cover - the validator must not degrade silently
    raise SystemExit("FAIL application_behavior: jsonschema is required; refusing schema-less validation") from exc

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from build_corpus import GENERATED_JSONL, record_key  # noqa: E402

SPEC_FIELDS = {
    "sources.jsonl": {"source_id", "title", "authority", "source_kind", "url", "retrieved", "supports", "does_not_prove"},
    "bounded-contexts.jsonl": {"context_id", "name", "sovereign_question", "inside", "outside", "imports", "exports", "semantic_owner", "required_adjudications"},
    "semantic-contracts.jsonl": {"contract_id", "owner_context_ref", "kind", "definition", "identity_rules", "lifecycle_states", "imports", "forbidden_collapses", "allowed_compositions"},
    "state-machines.jsonl": {"state_machine_id", "owner_context_ref", "states", "initial_state", "terminal_states"},
    "state-transitions.jsonl": {"transition_id", "state_machine_ref", "from_state", "to_state", "trigger", "guard", "result_observation", "refusal_observation"},
    "library-contracts.jsonl": {"library_id", "semantic_owner_context_ref", "responsibility", "public_types", "public_operations", "configuration_points", "compatibility_laws", "imports", "forbidden_responsibilities"},
    "operations.jsonl": {"operation_id", "owner_library_ref", "input_contract_refs", "output_contract_refs", "purity", "determinism", "idempotency", "preconditions", "postconditions", "failure_states", "configuration_points", "side_effect_contract", "refusal_precedence"},
    "boundary-decisions.jsonl": {"boundary_id", "left_concept", "right_concept", "decision", "required_adjudication"},
    "crosswalks.jsonl": {"crosswalk_id", "source_ref", "target_refs", "direction", "preservation", "losses", "prerequisites"},
    "requirements-offers.jsonl": set(),
    "conformance-tests.jsonl": {"test_id", "purpose", "subject_refs", "oracle", "fixture_refs", "required_receipt_fields", "execution_status", "receipt_refs", "failure_behavior"},
    "negative-twins.jsonl": {"negative_twin_id", "paired_test_ref", "unsafe_inference", "expected_refusal"},
    "assembly-edges.jsonl": {"assembly_edge_id", "source_ref", "target_ref", "resolution_mechanism", "semantic_owner_ref", "required_decisions", "loss_or_refusal", "time_rule"},
    "gaps.jsonl": {"gap_id", "category", "scope_refs", "blocking_outputs", "evidence_needed", "completion_effect"},
}


def load_jsonl(name: str) -> list[dict[str, Any]]:
    path = ROOT / name
    if not path.exists():
        raise ValueError(f"missing generated file: {name}")
    rows: list[dict[str, Any]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            raise ValueError(f"{name}:{line_number}: blank JSONL line is not allowed")
        try:
            value = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"{name}:{line_number}: invalid JSON: {exc}") from exc
        if not isinstance(value, dict):
            raise ValueError(f"{name}:{line_number}: JSONL record must be an object")
        rows.append(value)
    if not rows:
        raise ValueError(f"{name}: empty record set")
    keys = [record_key(row) for row in rows]
    if keys != sorted(keys):
        raise ValueError(f"{name}: records are not sorted by stable identifier")
    if len(keys) != len(set(keys)):
        raise ValueError(f"{name}: duplicate stable identifier")
    return rows


def all_strings(value: Any) -> Iterable[str]:
    if isinstance(value, str):
        yield value
    elif isinstance(value, list):
        for item in value:
            yield from all_strings(item)
    elif isinstance(value, dict):
        for item in value.values():
            yield from all_strings(item)


def validate() -> tuple[list[str], dict[str, list[dict[str, Any]]]]:
    errors: list[str] = []
    rows: dict[str, list[dict[str, Any]]] = {}
    try:
        for name in GENERATED_JSONL:
            rows[name] = load_jsonl(name)
    except ValueError as exc:
        return [str(exc)], rows

    schema_path = ROOT / "schemas/record.schema.json"
    try:
        record_schema = json.loads(schema_path.read_text(encoding="utf-8"))
        validator = jsonschema.Draft202012Validator(record_schema, format_checker=jsonschema.FormatChecker())
        for name, records in rows.items():
            required = SPEC_FIELDS[name]
            for row in records:
                identifier = record_key(row)
                missing = sorted(required - set(row))
                if missing:
                    errors.append(f"{name}:{identifier}: missing fields {missing}")
                for error in validator.iter_errors(row):
                    errors.append(f"{name}:{identifier}: schema: {error.message}")
                if row.get("completion_claim") is not False:
                    errors.append(f"{name}:{identifier}: completion_claim must be false")
                if row.get("edition") != 1:
                    errors.append(f"{name}:{identifier}: unsupported edition")
                if "time_model" in row and row.get("time_model", {}).get("ambient_time_allowed") is not False:
                    errors.append(f"{name}:{identifier}: ambient time must be forbidden")
                if name != "sources.jsonl" and not row.get("evidence_refs"):
                    errors.append(f"{name}:{identifier}: evidence_refs must be non-empty")
    except OSError as exc:
        errors.append(f"cannot load record schema: {exc}")

    source_ids = {row["source_id"] for row in rows.get("sources.jsonl", [])}
    context_ids = {row["context_id"] for row in rows.get("bounded-contexts.jsonl", [])}
    contract_ids = {row["contract_id"] for row in rows.get("semantic-contracts.jsonl", [])}
    machine_ids = {row["state_machine_id"] for row in rows.get("state-machines.jsonl", [])}
    library_ids = {row["library_id"] for row in rows.get("library-contracts.jsonl", [])}
    operation_ids = {row["operation_id"] for row in rows.get("operations.jsonl", [])}
    test_ids = {row["test_id"] for row in rows.get("conformance-tests.jsonl", [])}
    application_refs = context_ids | contract_ids | machine_ids | library_ids | operation_ids | test_ids

    for source in rows.get("sources.jsonl", []):
        if not source["url"].startswith("https://"):
            errors.append(f"{source['source_id']}: evidence URL is not HTTPS")
        if not source["supports"] or not source["does_not_prove"]:
            errors.append(f"{source['source_id']}: evidence must include support and limitation")

    def check_refs(name: str, row: dict[str, Any], field: str, allowed: set[str]) -> None:
        values = row.get(field, [])
        if isinstance(values, str):
            values = [values]
        for value in values:
            if value.startswith("context.application.") or value.startswith("contract.application.") or value.startswith("machine.application.") or value.startswith("library.application.") or value.startswith("operation.application.") or value.startswith("test.application."):
                if value not in allowed:
                    errors.append(f"{name}:{record_key(row)}: unknown {field} reference {value}")

    for name, records in rows.items():
        for row in records:
            for field in ("evidence_refs",):
                for value in row.get(field, []):
                    if value not in source_ids:
                        errors.append(f"{name}:{record_key(row)}: unknown evidence reference {value}")
            for field in ("imports", "exports", "owner_context_ref", "semantic_owner_context_ref", "state_machine_ref", "subject_refs", "required_contract_refs", "required_operation_refs", "claimed_contract_refs", "claimed_operation_refs", "input_contract_refs", "output_contract_refs", "owner_library_ref", "public_types", "public_operations", "target_refs", "scope_refs", "paired_test_ref", "subject_ref", "semantic_owner_ref"):
                if field in row:
                    check_refs(name, row, field, application_refs)

    for row in rows["bounded-contexts.jsonl"]:
        if not row["inside"] or not row["outside"]:
            errors.append(f"{row['context_id']}: inside/outside boundaries must be explicit")
        if row["semantic_owner"].startswith("provider."):
            errors.append(f"{row['context_id']}: provider cannot own application semantics")

    for row in rows["semantic-contracts.jsonl"]:
        if row["owner_context_ref"] not in context_ids:
            errors.append(f"{row['contract_id']}: unknown owner context")
        if not row["identity_rules"] or not row["lifecycle_states"] or not row["forbidden_collapses"]:
            errors.append(f"{row['contract_id']}: identity, lifecycle and boundary rules are required")

    for row in rows["state-machines.jsonl"]:
        if row["owner_context_ref"] not in context_ids or row["initial_state"] not in row["states"] or not set(row["terminal_states"]).issubset(set(row["states"])):
            errors.append(f"{row['state_machine_id']}: invalid state-machine ownership or states")
    for row in rows["state-transitions.jsonl"]:
        if row["state_machine_ref"] not in machine_ids:
            errors.append(f"{row['transition_id']}: unknown state machine")
        else:
            machine = next(machine for machine in rows["state-machines.jsonl"] if machine["state_machine_id"] == row["state_machine_ref"])
            if row["from_state"] not in machine["states"] or row["to_state"] not in machine["states"]:
                errors.append(f"{row['transition_id']}: state is outside machine")

    for row in rows["library-contracts.jsonl"]:
        if row["semantic_owner_context_ref"] not in context_ids:
            errors.append(f"{row['library_id']}: unknown semantic owner")
        if not set(row["public_types"]).issubset(contract_ids) or not set(row["public_operations"]).issubset(operation_ids):
            errors.append(f"{row['library_id']}: public references are not closed")
        if row["qualification_status"] != "unqualified":
            errors.append(f"{row['library_id']}: only unqualified status is evidenced")
        if any("provider" in value.lower() for value in row["forbidden_responsibilities"] + [row["responsibility"]]):
            errors.append(f"{row['library_id']}: provider-specific responsibility leaked into library boundary")

    for row in rows["operations.jsonl"]:
        if row["owner_library_ref"] not in library_ids or not set(row["input_contract_refs"]).issubset(contract_ids) or not set(row["output_contract_refs"]).issubset(contract_ids):
            errors.append(f"{row['operation_id']}: operation references are not closed")
        if row["purity"] not in {"pure", "observation", "effect_intent", "effect_observation", "pure_then_intent", "pure_graph_then_explicit_handoff"}:
            errors.append(f"{row['operation_id']}: invalid purity {row['purity']}")
        if not row["failure_states"] or not row["configuration_points"]:
            errors.append(f"{row['operation_id']}: failures and configuration points are required")

    req_rows = [row for row in rows["requirements-offers.jsonl"] if "requirement_id" in row]
    offer_rows = [row for row in rows["requirements-offers.jsonl"] if "offer_id" in row]
    if len(req_rows) != len(library_ids) or len(offer_rows) != len(library_ids):
        errors.append("requirements-offers.jsonl: every library must have exactly one requirement and one offer")
    for row in req_rows:
        if row["subject_ref"] not in library_ids or row["fallback_law"] != "refuse" or row["qualification_receipt_refs"]:
            errors.append(f"{row['requirement_id']}: unqualified requirement must fail closed")
    for row in offer_rows:
        if row["subject_ref"] not in library_ids or row["binding_eligible"] is not False or row["portable"] is not False or row["qualification_status"] != "unqualified" or row["implementation_refs"] or row["qualification_receipt_refs"]:
            errors.append(f"{row['offer_id']}: offer cannot be bindable without qualification")

    if not rows["conformance-tests.jsonl"] or not rows["negative-twins.jsonl"]:
        errors.append("conformance tests and negative twins are both required")
    for row in rows["conformance-tests.jsonl"]:
        if row["execution_status"] != "not_executed" or row["receipt_refs"]:
            errors.append(f"{row['test_id']}: execution evidence is absent and must remain unexecuted")
    for row in rows["negative-twins.jsonl"]:
        if row["paired_test_ref"] not in test_ids:
            errors.append(f"{row['negative_twin_id']}: unknown paired test")

    edges = rows["assembly-edges.jsonl"]
    mechanisms = {row["resolution_mechanism"] for row in edges}
    if len(mechanisms) < 3 or mechanisms == {"compiler_candidate"}:
        errors.append("assembly must expose at least three mechanisms and cannot be compiler-only")
    if any(not row["required_decisions"] or not row["loss_or_refusal"] for row in edges):
        errors.append("every assembly edge must name decisions and loss/refusal")
    if any("compiler" in row["resolution_mechanism"] for row in edges) and len(mechanisms) < 3:
        errors.append("compiler mechanism is not allowed to be the only assembly mechanism")

    for row in rows["gaps.jsonl"]:
        if row["status"] != "OPEN" or row["completion_claim"] is not False or not row["evidence_needed"]:
            errors.append(f"{row['gap_id']}: unresolved gap must stay open with evidence obligations")

    coverage_path = ROOT / "coverage-report.json"
    manifest_path = ROOT / "manifest.json"
    try:
        coverage = json.loads(coverage_path.read_text(encoding="utf-8"))
        coverage_validator = jsonschema.Draft202012Validator(json.loads((ROOT / "schemas/coverage-report.schema.json").read_text(encoding="utf-8")), format_checker=jsonschema.FormatChecker())
        errors.extend(f"coverage-report.json: schema: {error.message}" for error in coverage_validator.iter_errors(coverage))
        if coverage["counts"]["libraries"] != len(library_ids) or coverage["counts"]["operations"] != len(rows["operations.jsonl"]):
            errors.append("coverage-report.json: counts do not match JSONL")
        if coverage["qualification"]["qualified_implementations"] != 0 or coverage["qualification"]["binding_eligible_offers"] != 0 or coverage["qualification"]["executed_conformance_tests"] != 0:
            errors.append("coverage-report.json: qualification claims must remain zero")
    except (OSError, KeyError, json.JSONDecodeError) as exc:
        errors.append(f"coverage-report.json: unreadable or incomplete: {exc}")
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest_validator = jsonschema.Draft202012Validator(json.loads((ROOT / "schemas/manifest.schema.json").read_text(encoding="utf-8")), format_checker=jsonschema.FormatChecker())
        errors.extend(f"manifest.json: schema: {error.message}" for error in manifest_validator.iter_errors(manifest))
        for name in GENERATED_JSONL:
            if name not in manifest.get("files", {}):
                errors.append(f"manifest.json: missing file entry {name}")
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"manifest.json: unreadable: {exc}")
    return errors, rows


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--determinism", action="store_true", help="also run the no-drift generator check")
    args = parser.parse_args()
    if args.determinism:
        result = subprocess.run([sys.executable, str(ROOT / "build_corpus.py"), "--check"], capture_output=True, text=True)
        if result.returncode:
            print(result.stdout.strip() or result.stderr.strip())
            return 1
    errors, rows = validate()
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print(f"PASS application_behavior: {sum(len(value) for value in rows.values())} records; 0 qualified implementations; 0 executed tests")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
