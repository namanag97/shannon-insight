#!/usr/bin/env python3
"""Offline structural, cross-reference, semantic-gate, and determinism validator."""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent

FILE_SCHEMAS = {
    "sources.jsonl": "source.schema.json",
    "contexts.jsonl": "context.schema.json",
    "ir-nodes.jsonl": "ir-node.schema.json",
    "ir-edges.jsonl": "ir-edge.schema.json",
    "pass-contracts.jsonl": "pass-contract.schema.json",
    "invariants.jsonl": "invariant.schema.json",
    "diagnostics.jsonl": "diagnostic.schema.json",
    "proof-obligations.jsonl": "proof.schema.json",
    "rewrite-equivalences.jsonl": "rewrite-equivalence.schema.json",
    "decision-trace-contracts.jsonl": "decision-trace.schema.json",
    "incremental-rules.jsonl": "incremental-rule.schema.json",
    "migrations.jsonl": "migration.schema.json",
    "extension-boundaries.jsonl": "extension-boundary.schema.json",
    "artifact-receipt-contracts.jsonl": "artifact-receipt.schema.json",
    "library-boundaries.jsonl": "library-boundary.schema.json",
    "rust-applicability.jsonl": "rust-applicability.schema.json",
    "innovations.jsonl": "innovation.schema.json",
    "gaps.jsonl": "gap.schema.json",
    "lowering-traces.jsonl": "lowering-trace.schema.json",
}


IDENTITY_KEYS = (
    "source_id", "context_id", "node_id", "edge_id", "pass_id", "invariant_id", "diagnostic_id",
    "proof_id", "rewrite_id", "decision_trace_id", "incremental_rule_id", "migration_id", "extension_id",
    "artifact_id", "library_id", "mapping_id", "innovation_id", "gap_id", "trace_id",
)


def load_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def load_jsonl(path: Path, errors: list[str]) -> list[dict]:
    rows: list[dict] = []
    with path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            if not line.endswith("\n"):
                errors.append(f"{path.name}:{line_number}: line is not LF terminated")
            try:
                value = json.loads(line)
            except json.JSONDecodeError as exc:
                errors.append(f"{path.name}:{line_number}: invalid JSON: {exc}")
                continue
            if not isinstance(value, dict):
                errors.append(f"{path.name}:{line_number}: record is not an object")
                continue
            rows.append(value)
    return rows


def identity(record: dict) -> str:
    keys = [key for key in IDENTITY_KEYS if key in record]
    if len(keys) != 1:
        raise ValueError(f"expected one identity key, got {keys}")
    return str(record[keys[0]])


def resolve_pointer(schema: dict, pointer: str) -> object:
    if not pointer.startswith("#/"):
        raise ValueError(f"only local schema references supported: {pointer}")
    current: object = schema
    for raw in pointer[2:].split("/"):
        token = raw.replace("~1", "/").replace("~0", "~")
        if not isinstance(current, dict) or token not in current:
            raise ValueError(f"unresolved schema reference: {pointer}")
        current = current[token]
    return current


def check_schema(value: object, rule: dict, root: dict, at: str, errors: list[str]) -> None:
    if "$ref" in rule:
        target = resolve_pointer(root, rule["$ref"])
        if not isinstance(target, dict):
            errors.append(f"{at}: schema reference is not an object")
            return
        check_schema(value, target, root, at, errors)
        return
    if "const" in rule and value != rule["const"]:
        errors.append(f"{at}: expected const {rule['const']!r}, got {value!r}")
    if "enum" in rule and value not in rule["enum"]:
        errors.append(f"{at}: value {value!r} not in enum")
    expected = rule.get("type")
    if expected:
        options = expected if isinstance(expected, list) else [expected]
        valid = any(
            (kind == "object" and isinstance(value, dict))
            or (kind == "array" and isinstance(value, list))
            or (kind == "string" and isinstance(value, str))
            or (kind == "integer" and isinstance(value, int) and not isinstance(value, bool))
            or (kind == "number" and isinstance(value, (int, float)) and not isinstance(value, bool))
            or (kind == "boolean" and isinstance(value, bool))
            or (kind == "null" and value is None)
            for kind in options
        )
        if not valid:
            errors.append(f"{at}: expected type {expected!r}, got {type(value).__name__}")
            return
    if isinstance(value, str):
        if len(value) < rule.get("minLength", 0):
            errors.append(f"{at}: string shorter than minLength")
        if "pattern" in rule and re.fullmatch(rule["pattern"], value) is None:
            errors.append(f"{at}: value {value!r} does not match {rule['pattern']!r}")
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        if "minimum" in rule and value < rule["minimum"]:
            errors.append(f"{at}: value below minimum")
        if "maximum" in rule and value > rule["maximum"]:
            errors.append(f"{at}: value above maximum")
    if isinstance(value, list):
        if len(value) < rule.get("minItems", 0):
            errors.append(f"{at}: array shorter than minItems")
        if rule.get("uniqueItems"):
            encoded = [json.dumps(item, sort_keys=True) for item in value]
            if len(encoded) != len(set(encoded)):
                errors.append(f"{at}: array items are not unique")
        if "items" in rule:
            for index, item in enumerate(value):
                check_schema(item, rule["items"], root, f"{at}[{index}]", errors)
    if isinstance(value, dict):
        required = rule.get("required", [])
        missing = [key for key in required if key not in value]
        if missing:
            errors.append(f"{at}: missing required keys {missing}")
        properties = rule.get("properties", {})
        if rule.get("additionalProperties") is False:
            extras = sorted(set(value) - set(properties))
            if extras:
                errors.append(f"{at}: additional properties {extras}")
        for key, subrule in properties.items():
            if key in value:
                check_schema(value[key], subrule, root, f"{at}.{key}", errors)


def file_digest(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    errors: list[str] = []
    manifest = load_json(ROOT / "manifest.json")
    data: dict[str, list[dict]] = {}

    # Schema syntax and schema-subset validation for every JSONL registry.
    for filename, schema_name in FILE_SCHEMAS.items():
        path = ROOT / filename
        schema_path = ROOT / "schemas" / schema_name
        if not path.exists():
            errors.append(f"missing generated file: {filename}")
            continue
        if not schema_path.exists():
            errors.append(f"missing schema: {schema_name}")
            continue
        schema = load_json(schema_path)
        rows = load_jsonl(path, errors)
        data[filename] = rows
        for index, row in enumerate(rows, 1):
            check_schema(row, schema, schema, f"{filename}:{index}", errors)
        try:
            identities = [identity(row) for row in rows]
        except ValueError as exc:
            errors.append(f"{filename}: {exc}")
            identities = []
        if identities != sorted(identities):
            errors.append(f"{filename}: records are not sorted by stable identity")
        if len(identities) != len(set(identities)):
            errors.append(f"{filename}: duplicate identities")

    # Candidate-only posture.
    for filename, rows in data.items():
        for row in rows:
            status = row.get("status")
            if not isinstance(status, str) or "candidate" not in status:
                errors.append(f"{filename}:{identity(row)}: status is not candidate-only: {status!r}")
    if manifest.get("completion_claim") is not False or "candidate" not in manifest.get("status", ""):
        errors.append("manifest must be candidate status with completion_claim=false")

    # Minimum scope gates.
    counts = manifest.get("counts", {})
    actual = {
        "primary_or_official_sources": len(data.get("sources.jsonl", [])),
        "bounded_context_candidates": len(data.get("contexts.jsonl", [])),
        "ir_node_candidates": len(data.get("ir-nodes.jsonl", [])),
        "ir_edge_candidates": len(data.get("ir-edges.jsonl", [])),
        "pass_candidates": len(data.get("pass-contracts.jsonl", [])),
        "invariant_candidates": len(data.get("invariants.jsonl", [])),
        "diagnostic_candidates": len(data.get("diagnostics.jsonl", [])),
        "proof_candidates": len(data.get("proof-obligations.jsonl", [])),
        "rewrite_equivalence_candidates": len(data.get("rewrite-equivalences.jsonl", [])),
        "decision_trace_contracts": len(data.get("decision-trace-contracts.jsonl", [])),
        "incremental_rules": len(data.get("incremental-rules.jsonl", [])),
        "migration_candidates": len(data.get("migrations.jsonl", [])),
        "extension_boundaries": len(data.get("extension-boundaries.jsonl", [])),
        "artifact_receipt_contracts": len(data.get("artifact-receipt-contracts.jsonl", [])),
        "library_boundaries": len(data.get("library-boundaries.jsonl", [])),
        "rust_type_trait_typestate_mappings": len(data.get("rust-applicability.jsonl", [])),
        "innovations_2021_2026": len(data.get("innovations.jsonl", [])),
        "honest_gaps": len(data.get("gaps.jsonl", [])),
        "lowering_traces": len(data.get("lowering-traces.jsonl", [])),
    }
    actual["ir_node_edge_pass_diagnostic_proof_candidates"] = sum(
        actual[key] for key in ("ir_node_candidates", "ir_edge_candidates", "pass_candidates", "diagnostic_candidates", "proof_candidates")
    )
    for key, value in actual.items():
        if counts.get(key) != value:
            errors.append(f"manifest count mismatch {key}: declared={counts.get(key)!r} actual={value}")
    for key, minimum in {
        "primary_or_official_sources": 50, "bounded_context_candidates": 35,
        "ir_node_edge_pass_diagnostic_proof_candidates": 150, "innovations_2021_2026": 20,
    }.items():
        if actual.get(key, 0) < minimum:
            errors.append(f"minimum not met {key}: {actual.get(key, 0)} < {minimum}")

    # Source and local cross-reference closure.
    source_ids = {row["source_id"] for row in data.get("sources.jsonl", [])}
    pass_ids = {row["pass_id"] for row in data.get("pass-contracts.jsonl", [])}
    diagnostic_ids = {row["diagnostic_id"] for row in data.get("diagnostics.jsonl", [])}
    gap_ids = {row["gap_id"] for row in data.get("gaps.jsonl", [])}
    for filename, rows in data.items():
        for row in rows:
            for source_ref in row.get("source_refs", []):
                if source_ref not in source_ids:
                    errors.append(f"{filename}:{identity(row)}: unresolved source ref {source_ref}")
    for proof in data.get("proof-obligations.jsonl", []):
        if proof["failure_diagnostic"] not in diagnostic_ids:
            errors.append(f"{proof['proof_id']}: unresolved diagnostic {proof['failure_diagnostic']}")
    for trace in data.get("lowering-traces.jsonl", []):
        for step in trace["steps"]:
            if step.get("pass_ref") not in pass_ids:
                errors.append(f"{trace['trace_id']}: unresolved pass {step.get('pass_ref')}")
        for gap_ref in trace["terminal_gaps"]:
            if gap_ref not in gap_ids:
                errors.append(f"{trace['trace_id']}: unresolved gap {gap_ref}")

    # Compiler-semantic laws with direct structural checks.
    passes = data.get("pass-contracts.jsonl", [])
    for compiler_pass in passes:
        preserves = " ".join(compiler_pass["preserves"]).lower()
        if "rejected alternatives" not in preserves or "source anchors" not in preserves:
            errors.append(f"{compiler_pass['pass_id']}: does not preserve rejected alternatives/source anchors")
        if compiler_pass["pass_kind"] == "optimization" and compiler_pass["input_stage"] != compiler_pass["output_stage"]:
            errors.append(f"{compiler_pass['pass_id']}: optimization crosses semantic stage boundary")
    if not any(row["pass_kind"] == "semantic_lowering" for row in passes):
        errors.append("no semantic-lowering pass contracts")
    if not any(row["pass_kind"] == "optimization" for row in passes):
        errors.append("no separately typed optimization passes")

    default_nodes = [row for row in data.get("ir-nodes.jsonl", []) if "default" in row["name"].lower()]
    if not default_nodes or any("authority" not in row["default_law"].lower() for row in default_nodes):
        errors.append("default nodes do not all state authority-bound default law")
    decision_traces = data.get("decision-trace-contracts.jsonl", [])
    if not decision_traces or any("rejected" not in " ".join(row["required_outcome_fields"]).lower() for row in decision_traces):
        errors.append("decision traces do not retain rejected alternatives")

    traces = data.get("lowering-traces.jsonl", [])
    positive = [row for row in traces if row["trace_id"].endswith(".positive")]
    negative = [row for row in traces if row["trace_id"].endswith(".negative")]
    if len(positive) < 2 or len({row["vertical"] for row in positive}) < 2:
        errors.append("fewer than two unrelated positive vertical lowering traces")
    if len(negative) < 2 or any("refused" not in row["expected_result"] for row in negative):
        errors.append("negative lowering failures missing or do not refuse")
    for trace in positive:
        serialized = json.dumps(trace, sort_keys=True).lower()
        if "provider_bindings_absent" not in serialized or "unbound" not in serialized:
            errors.append(f"{trace['trace_id']}: positive trace fabricates or fails to refuse provider binding")

    # Recent innovation posture and LLM/generative semantic quarantine.
    innovations = data.get("innovations.jsonl", [])
    if any(not row["non_llm"] or not (2021 <= row["year"] <= 2026) for row in innovations):
        errors.append("innovation record outside 2021-2026 or not marked non-LLM")
    source_years = {row["source_id"]: row["publication_or_live_year"] for row in data.get("sources.jsonl", [])}
    for innovation in innovations:
        if not any(source_years.get(ref) == innovation["year"] for ref in innovation["source_refs"]):
            errors.append(f"{innovation['innovation_id']}: year lacks matching primary/official source-year evidence")
    forbidden = ("large_language_model", "agent_memory", "prompt_dispatch", "rag_dispatch", "generative_dispatch")
    semantic_files = ("ir-nodes.jsonl", "pass-contracts.jsonl", "rewrite-equivalences.jsonl", "library-boundaries.jsonl")
    for filename in semantic_files:
        compact = (ROOT / filename).read_text(encoding="utf-8").lower()
        for term in forbidden:
            if term in compact:
                errors.append(f"{filename}: forbidden generative semantic dependency {term}")

    # Generated-file/digest closure.
    expected_generated = set(manifest.get("generated_files", []))
    declared_digests = manifest.get("file_digests", {})
    if expected_generated != set(declared_digests):
        errors.append("manifest generated_files and file_digests keys differ")
    for filename in sorted(expected_generated):
        path = ROOT / filename
        if not path.exists():
            errors.append(f"manifest references missing generated file {filename}")
        elif declared_digests.get(filename) != file_digest(path):
            errors.append(f"digest mismatch for {filename}")

    # The plan is explicit and remains candidate.
    conformance = load_json(ROOT / "conformance-plan.json")
    if conformance.get("completion_claim") is not False or conformance.get("status") != "candidate":
        errors.append("conformance plan must remain candidate/non-complete")
    level_names = {level.get("level") for level in conformance.get("levels", [])}
    required_levels = {"schema", "identity", "determinism", "semantic", "rewrite", "incremental", "extensions", "vertical", "artifact", "review"}
    if not required_levels.issubset(level_names):
        errors.append(f"conformance plan missing levels: {sorted(required_levels - level_names)}")

    alignment = load_json(ROOT / "upstream-alignment.json")
    alignment_schema = load_json(ROOT / "schemas" / "upstream-alignment.schema.json")
    check_schema(alignment, alignment_schema, alignment_schema, "upstream-alignment.json", errors)
    project_root = ROOT.parents[3]
    for relative in alignment.get("read_only_inputs", []):
        if not (project_root / relative).is_file():
            errors.append(f"upstream alignment input missing: {relative}")
    upstream_metamodel = load_json(project_root / "research/domain_atlas/compiler/compiler-metamodel.json")
    upstream_stage_ids = {stage["stage_id"] for stage in upstream_metamodel.get("ir_stages", [])}
    aligned_stage_ids = {stage["upstream_stage"] for stage in alignment.get("stage_alignment", [])}
    if upstream_stage_ids != aligned_stage_ids:
        errors.append(f"upstream stage alignment mismatch: upstream={sorted(upstream_stage_ids)} aligned={sorted(aligned_stage_ids)}")
    upstream_proofs = load_json(project_root / "research/domain_atlas/compiler/proof-obligations.json")
    if len(upstream_proofs.get("proofs", [])) < 40 or "do not replace" not in alignment.get("proof_posture", ""):
        errors.append("upstream proof catalog is not retained as mandatory input")

    # Re-run the deterministic generator and demand byte-identical generated output.
    before = {name: file_digest(ROOT / name) for name in expected_generated | {"manifest.json"}}
    process = subprocess.run([sys.executable, str(ROOT / "build_corpus.py")], cwd=ROOT, text=True, capture_output=True, check=False)
    if process.returncode != 0:
        errors.append(f"deterministic regeneration failed: {process.stderr.strip() or process.stdout.strip()}")
    else:
        after = {name: file_digest(ROOT / name) for name in before}
        changed = sorted(name for name in before if before[name] != after[name])
        if changed:
            errors.append(f"deterministic regeneration changed files: {changed}")

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print(
        "PASS ir-lowering candidate corpus: "
        f"{actual['bounded_context_candidates']} contexts, "
        f"{actual['ir_node_edge_pass_diagnostic_proof_candidates']} node/edge/pass/diagnostic/proof candidates "
        f"({actual['ir_node_candidates']} nodes, {actual['ir_edge_candidates']} edges, "
        f"{actual['pass_candidates']} passes, {actual['diagnostic_candidates']} diagnostics, {actual['proof_candidates']} proofs), "
        f"{actual['primary_or_official_sources']} primary/official sources, "
        f"{actual['innovations_2021_2026']} recent non-LLM innovations, "
        f"{actual['rust_type_trait_typestate_mappings']} Rust applicability mappings, "
        f"{actual['lowering_traces']} traces, {actual['honest_gaps']} gaps; deterministic regeneration verified"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
