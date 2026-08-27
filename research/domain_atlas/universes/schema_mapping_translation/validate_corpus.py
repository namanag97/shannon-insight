#!/usr/bin/env python3
"""Validate schema-mapping boundary, exact APIs, decisions and non-collapse laws."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import build_corpus


ROOT = Path(__file__).resolve().parent


def load(name: str) -> list[dict]:
    return [json.loads(line) for line in (ROOT / name).read_text(encoding="utf-8").splitlines() if line.strip()]


def main() -> None:
    manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
    data = {name: load(name) for name in build_corpus.FILES}
    for name, rows in data.items():
        assert manifest["files"][name]["records"] == len(rows), name
        assert manifest["files"][name]["sha256"] == hashlib.sha256((ROOT / name).read_bytes()).hexdigest(), name
    assert len(data["sources.jsonl"]) == 20 and all(row["url"].startswith("https://") for row in data["sources.jsonl"])
    assert [row["context_id"] for row in data["bounded-contexts.jsonl"]] == ["context.schema_mapping.translation"]
    assert len(data["boundary-lens-adjudication.jsonl"]) == 12
    assert {row["lens"] for row in data["boundary-lens-adjudication.jsonl"]} == {name for name, *_ in build_corpus.LENSES}
    verdicts = data["boundary-verdicts.jsonl"]
    assert len(verdicts) == 1 and verdicts[0]["disposition"] == "retain_split_with_shared_published_plan_contract"
    assert verdicts[0]["subject_refs"] == ["library.schema_mapping.compiler", "library.schema_mapping.executor"]
    decisions = data["decision-points.jsonl"]
    assert len(decisions) == 35 and all(row["default"] is None and row["default_law"] == "forbidden" for row in decisions)
    libraries = {row["library_id"]: row for row in data["library-contracts.jsonl"]}
    assert set(libraries) == {"library.schema_mapping.compiler", "library.schema_mapping.executor"}
    compiler = libraries["library.schema_mapping.compiler"]
    executor = libraries["library.schema_mapping.executor"]
    assert compiler["effect_boundary"] == executor["effect_boundary"] == "pure_no_io"
    assert len(compiler["operations"]) == 9 and len(executor["operations"]) == 5
    assert len(compiler["decision_refs"]) == 27 and len(executor["decision_refs"]) == 8
    assert "library.schema_registry.reference_closure" in compiler["dependencies"]
    assert executor["dependencies"] == ["library.schema_mapping.compiler"]
    for library in libraries.values():
        assert set(library["operation_refs"]) == {op["operation_ref"] for op in library["operations"]}
        assert all(op["input_types"] and op["output_type"].startswith("Result<") and op["purity"] == "pure" for op in library["operations"])
        assert len(library["public_types"]) >= 30 and library["gaps"]
    laws = " ".join(compiler["laws"] + executor["laws"]).lower()
    for phrase in ["schema mapping, schema compatibility", "absent, missing, null", "target default constructs", "unqualified local time is not utc", "change semantics", "cannot infer, extend, repair"]:
        assert phrase in laws, phrase
    exclusions = " ".join(compiler["must_not_own"] + executor["must_not_own"]).lower()
    for phrase in ["ontology", "reference", "unit", "source capture", "delivery", "provider qualification"]:
        assert phrase in exclusions, phrase
    compiler_rows = data["compiler-contracts.jsonl"]
    offers = [row for row in compiler_rows if row["record_kind"] == "capability_offer"]
    assert len(compiler_rows) == 6 and len(offers) == 2
    assert all(row["qualified_implementation_count"] == 0 and not row["portable"] and not row["selectable"] for row in offers)
    assert len(data["negative-twins.jsonl"]) == 26 and manifest["completion_claim"] is False
    print("VALIDATION PASS schema mapping translation: 2 libraries, 35 no-default decisions, 14 pure operations, 12 lenses, 0 qualified offers")


if __name__ == "__main__":
    main()
