#!/usr/bin/env python3
"""Validate closure, distinctions and deterministic regeneration for the CSP corpus."""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
FAMILIES = {"intent", "identity", "time", "quantity", "authority", "decision"}
JSONL_FILES = [
    "sources.jsonl", "bounded-contexts.jsonl", "semantic-records.jsonl",
    "invariants-refusals.jsonl", "lifecycles.jsonl", "context-acls.jsonl",
    "compiler-contracts.jsonl", "library-boundaries.jsonl", "rust-applicability.jsonl",
    "innovations-2021-2026.jsonl", "experts.jsonl", "vertical-examples.jsonl", "gaps.jsonl",
]


def load_jsonl(name: str) -> list[dict[str, Any]]:
    rows = []
    for line_no, line in enumerate((ROOT / name).read_text(encoding="utf-8").splitlines(), 1):
        value = json.loads(line)
        assert isinstance(value, dict), f"{name}:{line_no}: object required"
        rows.append(value)
    return rows


def ids(rows: list[dict[str, Any]], label: str) -> set[str]:
    values = [row["id"] for row in rows]
    duplicate = [value for value, count in Counter(values).items() if count > 1]
    assert not duplicate, f"{label}: duplicate ids {duplicate[:5]}"
    return set(values)


def refs(rows: list[dict[str, Any]], field: str) -> set[str]:
    result: set[str] = set()
    for row in rows:
        value = row.get(field, [])
        if isinstance(value, str):
            result.add(value)
        elif isinstance(value, list):
            result.update(item for item in value if isinstance(item, str))
    return result


def digests(names: list[str]) -> dict[str, str]:
    return {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in names}


def schema_validate(rows: list[dict[str, Any]], schema_name: str, label: str) -> None:
    try:
        import jsonschema
    except ImportError:
        return
    schema = json.loads((ROOT / "schema" / schema_name).read_text(encoding="utf-8"))
    validator = jsonschema.Draft202012Validator(schema, format_checker=jsonschema.FormatChecker())
    for index, row in enumerate(rows, 1):
        errors = sorted(validator.iter_errors(row), key=lambda error: list(error.path))
        assert not errors, f"{label}:{index}: {errors[0].message}"


def main() -> None:
    data = {name: load_jsonl(name) for name in JSONL_FILES}
    sources = data["sources.jsonl"]
    contexts = data["bounded-contexts.jsonl"]
    semantic = data["semantic-records.jsonl"]
    rules = data["invariants-refusals.jsonl"]
    compiler = data["compiler-contracts.jsonl"]
    libraries = data["library-boundaries.jsonl"]
    innovations = data["innovations-2021-2026.jsonl"]
    experts = data["experts.jsonl"]
    source_ids = ids(sources, "sources")
    context_ids = ids(contexts, "contexts")
    for name, rows in data.items():
        if name != "sources.jsonl":
            ids(rows, name)
            assert all(row["status"] == "candidate" for row in rows), f"{name}: non-candidate row"

    schema_validate(sources, "source.schema.json", "sources")
    for name, rows in data.items():
        if name != "sources.jsonl":
            schema_validate(rows, "candidate.schema.json", name)

    assert len(sources) >= 120
    assert len({row["url"] for row in sources}) == len(sources), "source URLs are not unique"
    assert {row["family"] for row in contexts} == FAMILIES
    family_contexts = Counter(row["family"] for row in contexts)
    assert all(family_contexts[family] >= 20 for family in FAMILIES)
    assert len(contexts) >= 80
    assert len(semantic) >= 500
    kinds = Counter(row["kind"] for row in semantic)
    assert kinds["type"] >= 150 and kinds["operation"] >= 400 and kinds["decision"] >= 150 and kinds["law"] >= 150
    assert len(rules) >= 100 and all(row["invariant"] and row["refusal"] for row in rules)
    assert len(data["lifecycles.jsonl"]) >= 20
    assert len(data["context-acls.jsonl"]) >= 20
    assert len(libraries) >= 50
    assert {row["layer"] for row in libraries} >= {"pure", "runtime", "adapter", "test"}
    assert len(data["rust-applicability.jsonl"]) >= 30
    assert all("not the domain source of truth" in row["boundary_law"] for row in data["rust-applicability.jsonl"])
    assert len(innovations) >= 30 and all(2021 <= row["year"] <= 2026 and row["non_llm"] is True for row in innovations)
    assert {2021, 2022, 2023, 2024, 2025, 2026} <= {row["year"] for row in innovations}
    assert len(experts) >= 40 and {row["family"] for row in experts} == FAMILIES
    assert all(row["artifact_refs"] and row["learn"] and row["misuse_warning"] for row in experts)
    assert len(data["vertical-examples.jsonl"]) >= 2
    assert len({row["industry"] for row in data["vertical-examples.jsonl"]}) >= 2
    assert all(row["negative_twin"] for row in data["vertical-examples.jsonl"])

    # Referential closure and evidence scope.
    for name, rows in data.items():
        unknown_sources = refs(rows, "evidence_refs") - source_ids
        assert not unknown_sources, f"{name}: unknown evidence {sorted(unknown_sources)[:5]}"
    for name in ["semantic-records.jsonl", "invariants-refusals.jsonl", "compiler-contracts.jsonl"]:
        unknown_contexts = refs(data[name], "context_ref") - context_ids
        assert not unknown_contexts, f"{name}: unknown contexts {sorted(unknown_contexts)[:5]}"

    compiler_kinds = Counter(row["kind"] for row in compiler)
    assert all(compiler_kinds[kind] == len(contexts) for kind in ["compiler_requirement", "capability_offer", "compiler_mapping", "proof_obligation"])
    assert all(row["contract"] for row in compiler)

    model = json.loads((ROOT / "metamodel.json").read_text(encoding="utf-8"))
    assert model["completion_claim"] is False and model["status"] == "candidate"
    pairs = {(row["left"], row["right"]) for row in model["non_collapsible_distinctions"]}
    required_pairs = {
        ("identifier", "identity"), ("proof_of_control", "identity"),
        ("instant", "local_date_time"), ("elapsed_duration", "calendar_period"),
        ("valid_time", "recording_time"), ("number", "quantity"),
        ("probability", "confidence"), ("probability", "score"), ("missing", "zero"),
        ("approval", "issuance"), ("authority", "responsibility"),
        ("decision", "action"), ("action", "effect"), ("observation", "fact"),
    }
    assert required_pairs <= pairs, f"missing constitutional pairs: {required_pairs - pairs}"
    assert len(model["equality_stack"]) >= 6 and len(model["representation_stack"]) >= 6

    forbidden = re.compile(r"(?i)\b(prompt engineering|large language model|chatbot|generative ai)\b")
    for name in ["bounded-contexts.jsonl", "semantic-records.jsonl", "compiler-contracts.jsonl", "library-boundaries.jsonl"]:
        assert not any(forbidden.search(json.dumps(row)) for row in data[name]), f"{name}: generative/LLM core leaked in"

    manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
    schema_validate([manifest], "manifest.schema.json", "manifest")
    expected_counts = {
        "sources": len(sources), "bounded_contexts": len(contexts), "semantic_records": len(semantic),
        "invariants_refusals": len(rules), "lifecycles": len(data["lifecycles.jsonl"]),
        "context_acls": len(data["context-acls.jsonl"]), "compiler_contracts": len(compiler),
        "library_boundaries": len(libraries), "rust_applicability": len(data["rust-applicability.jsonl"]),
        "innovations_2021_2026": len(innovations), "vertical_examples": len(data["vertical-examples.jsonl"]),
        "expert_learning_routes": len(experts),
        "gaps": len(data["gaps.jsonl"]),
    }
    assert manifest["counts"] == expected_counts
    generated = manifest["generated_files"]
    assert manifest["sha256"] == digests(generated)
    before = digests(generated + ["manifest.json"])
    subprocess.run([sys.executable, str(ROOT / "build_corpus.py")], check=True, cwd=ROOT)
    after = digests(generated + ["manifest.json"])
    assert before == after, "builder output is not deterministic"
    print(
        "PASS core semantic primitives: "
        f"{len(sources)} sources, {len(contexts)} contexts, {len(semantic)} semantic records, "
        f"{len(rules)} invariants/refusals, {len(compiler)} compiler contracts, "
        f"{len(libraries)} libraries, {len(innovations)} innovations, {len(experts)} expert routes"
    )


if __name__ == "__main__":
    main()
