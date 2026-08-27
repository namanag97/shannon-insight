#!/usr/bin/env python3
"""Validate structure, references and constitutional laws of the QCK corpus."""

from __future__ import annotations

import json
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SCHEMA = ROOT / "schema"


def load_jsonl(name: str) -> list[dict]:
    path = ROOT / name
    records = []
    for line_no, line in enumerate(path.read_text().splitlines(), 1):
        if not line.strip():
            continue
        try:
            records.append(json.loads(line))
        except json.JSONDecodeError as exc:
            raise AssertionError(f"{name}:{line_no}: invalid JSON: {exc}") from exc
    return records


def require_unique(records: list[dict], field: str, name: str) -> set[str]:
    values = [record[field] for record in records]
    duplicates = [value for value, count in Counter(values).items() if count > 1]
    assert not duplicates, f"{name}: duplicate {field}: {duplicates}"
    return set(values)


def validate_schema(records: list[dict], schema_name: str, label: str) -> None:
    schema = json.loads((SCHEMA / schema_name).read_text())
    try:
        import jsonschema
    except ImportError:
        required = set(schema.get("required", []))
        for index, record in enumerate(records, 1):
            assert required <= set(record), f"{label}:{index}: schema-required fields missing"
        return
    validator = jsonschema.Draft202012Validator(schema, format_checker=jsonschema.FormatChecker())
    for index, record in enumerate(records, 1):
        errors = sorted(validator.iter_errors(record), key=lambda error: list(error.path))
        if errors:
            messages = "; ".join(f"{list(error.path)}: {error.message}" for error in errors[:5])
            raise AssertionError(f"{label}:{index}: {messages}")


def refs(records: list[dict], fields: list[str]) -> set[str]:
    result: set[str] = set()
    for record in records:
        for field in fields:
            value = record.get(field, [])
            if isinstance(value, str):
                result.add(value)
            else:
                result.update(value)
    return result


def main() -> None:
    before_rebuild = {str(path.relative_to(ROOT)): path.read_bytes() for path in ROOT.rglob("*.json*")}
    rebuilt = subprocess.run([sys.executable, str(ROOT / "build_corpus.py")], capture_output=True, text=True, check=False)
    after_rebuild = {str(path.relative_to(ROOT)): path.read_bytes() for path in ROOT.rglob("*.json*")}
    assert rebuilt.returncode == 0 and before_rebuild == after_rebuild, "deterministic rebuild drift or builder failure"
    sources = load_jsonl("sources.jsonl")
    contexts = load_jsonl("context-candidates.jsonl")
    operators = load_jsonl("logical-operators.jsonl")
    kernels = load_jsonl("kernel-contracts.jsonl")
    providers = load_jsonl("provider-capabilities.jsonl")
    targets = load_jsonl("target-profiles.jsonl")
    mappings = load_jsonl("compiler-mappings.jsonl")
    libraries = load_jsonl("library-boundaries.jsonl")
    innovations = load_jsonl("innovations.jsonl")
    gaps = load_jsonl("gaps.jsonl")

    validate_schema(sources, "source.schema.json", "sources")
    validate_schema(contexts, "context-candidate.schema.json", "contexts")
    validate_schema(operators, "logical-operator.schema.json", "operators")
    validate_schema(kernels, "kernel-contract.schema.json", "kernels")
    validate_schema(providers, "provider-capability.schema.json", "providers")
    validate_schema(targets, "target-profile.schema.json", "targets")
    validate_schema(mappings, "compiler-mapping.schema.json", "mappings")
    validate_schema(innovations, "innovation.schema.json", "innovations")
    validate_schema(gaps, "gap.schema.json", "gaps")

    # The shared compiler schema is authoritative for library contribution boundaries.
    global_library_schema = ROOT.parents[1] / "compiler" / "library-contribution.schema.json"
    if global_library_schema.exists():
        try:
            import jsonschema
        except ImportError:
            pass
        else:
            validator = jsonschema.Draft202012Validator(json.loads(global_library_schema.read_text()))
            for index, record in enumerate(libraries, 1):
                errors = list(validator.iter_errors(record))
                assert not errors, f"libraries:{index}: {errors[0].message}"

    source_ids = require_unique(sources, "source_id", "sources")
    context_ids = require_unique(contexts, "context_id", "contexts")
    operator_ids = require_unique(operators, "operator_id", "operators")
    kernel_ids = require_unique(kernels, "kernel_id", "kernels")
    require_unique(providers, "provider_capability_id", "providers")
    require_unique(targets, "target_profile_id", "targets")
    require_unique(mappings, "mapping_id", "mappings")
    require_unique(libraries, "library_id", "libraries")
    require_unique(innovations, "innovation_id", "innovations")
    require_unique(gaps, "gap_id", "gaps")

    assert len(sources) >= 40, "40+ authoritative primary sources required"
    assert len({source["url"] for source in sources}) == len(sources), "source URLs must be unique"
    assert {source["source_kind"] for source in sources} >= {"standard", "official_spec", "official_docs", "paper"}
    assert len(contexts) >= 30 and len(operators) >= 60 and len(kernels) >= 60 and len(libraries) >= 25

    required_operator_families = {"relational", "stream", "graph", "spatial", "numerical", "approximate", "encoding", "control"}
    assert {record["family"] for record in operators} == required_operator_families
    required_kernel_roles = {"expression", "vector", "relational", "approximate", "distributed", "stream", "external_memory", "graph", "spatial", "numerical", "codec", "runtime_primitive"}
    assert {record["kernel_role"] for record in kernels} == required_kernel_roles

    missing_operator_refs = refs(kernels, ["operation_refs"]) - operator_ids
    assert not missing_operator_refs, f"kernel operation refs missing: {sorted(missing_operator_refs)}"
    assert not ({record["subject_ref"] for record in mappings} - operator_ids), "mapping subject must be a logical operator"
    assert not (refs(providers, ["context_refs"]) - context_ids), "provider context ref missing"
    assert not (refs(libraries, ["contributes_to_context_refs", "semantic_owner_refs"]) - context_ids), "library context ref missing"
    assert not (refs(libraries, ["operation_refs"]) - operator_ids), "library operation ref missing"

    evidence_refs = set()
    for group, fields in [
        (contexts, ["evidence_refs"]), (operators, ["evidence_refs"]), (kernels, ["evidence_refs"]),
        (providers, ["evidence_refs"]), (targets, ["evidence_refs"]), (mappings, ["evidence_refs"]),
        (libraries, ["evidence_refs"]), (innovations, ["evidence_refs"]), (gaps, ["evidence_refs"]),
    ]:
        evidence_refs.update(refs(group, fields))
    assert not (evidence_refs - source_ids), f"unknown evidence refs: {sorted(evidence_refs - source_ids)}"

    # Preserve the five-level identity split. Algorithms are strings on kernels; providers and targets
    # have their own records; logical operators contain no physical algorithm/provider/target field.
    forbidden_logical_fields = {"algorithm_family", "kernel_id", "provider_ref", "target_profile_id"}
    assert all(not (forbidden_logical_fields & set(record)) for record in operators)
    assert all(record["algorithm_family"] and record["kernel_id"] for record in kernels)

    # Every executable contract exposes the concerns that prevent unsafe silent fallback.
    kernel_fields = {
        "exactness", "determinism_posture", "numeric_posture", "error_model", "information_loss",
        "ordering_behavior", "memory_contract", "complexity_contract", "parallelism_contract",
        "supported_target_classes", "cancellation_contract", "failure_modes", "fallback_law",
    }
    assert all(kernel_fields <= set(record) for record in kernels)
    assert all(record["fallback_law"] for record in kernels)

    # Approximate kernels must never masquerade as exact and require error declarations.
    for record in kernels:
        if record["kernel_role"] == "approximate" or record["exactness"] != "exact":
            assert record["exactness"] in {"bounded_approximation", "empirical_approximation"}
            assert record["error_model"] != "none beyond declared numeric representation"

    # Compression is not a single feature: semantic ops, codecs, physical targets and mappings exist.
    assert {"operator.qck.encoding.encode", "operator.qck.encoding.decode", "operator.qck.encoding.compress", "operator.qck.encoding.decompress"} <= operator_ids
    codec_algorithms = {record["algorithm_family"] for record in kernels if record["kernel_role"] == "codec"}
    assert {"dictionary_encoding", "delta_binary_packed", "run_length_bitpack_hybrid", "zstandard", "lz4_block_or_frame", "adaptive_lossless_float"} <= codec_algorithms
    assert "mapping.qck.lossless_codec" in {record["mapping_id"] for record in mappings}

    # Recent innovation catalog is explicitly non-LLM and evidence backed.
    assert innovations and all(2021 <= record["year"] <= 2026 for record in innovations)
    assert all(record["non_llm"] is True and record["evidence_refs"] for record in innovations)

    # Core semantic/execution records may not introduce quarantined generative dependencies.
    forbidden = re.compile(r"(?i)\\b(prompt|rag|agent[_ -]?memory|large language model|generative model)\\b")
    for label, records in [("operators", operators), ("kernels", kernels), ("providers", providers), ("libraries", libraries), ("mappings", mappings)]:
        for index, record in enumerate(records, 1):
            assert not forbidden.search(json.dumps(record)), f"{label}:{index}: forbidden generative dependency"

    manifest = json.loads((ROOT / "manifest.json").read_text())
    actual_counts = {
        "sources": len(sources), "context_candidates": len(contexts), "logical_operators": len(operators),
        "kernel_contracts": len(kernels), "provider_capability_classes": len(providers),
        "target_profiles": len(targets), "compiler_mapping_patterns": len(mappings),
        "library_boundaries": len(libraries), "innovations_2021_2026": len(innovations), "open_gaps": len(gaps),
    }
    assert manifest["counts"] == actual_counts, "manifest counts are stale"
    assert manifest["completion_claim"] is False, "finite seed must not claim universal completeness"

    print(
        "PASS query-compute-kernel universe: "
        f"{len(sources)} sources, {len(contexts)} contexts, {len(operators)} logical operators, "
        f"{len(kernels)} kernels, {len(providers)} provider classes, {len(targets)} targets, "
        f"{len(mappings)} mappings, {len(libraries)} library boundaries, "
        f"{len(innovations)} innovations, {len(gaps)} open gaps"
    )


if __name__ == "__main__":
    try:
        main()
    except AssertionError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1)
