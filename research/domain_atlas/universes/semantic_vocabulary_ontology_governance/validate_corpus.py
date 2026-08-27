#!/usr/bin/env python3
"""Validate glossary/ontology exact boundaries and non-collapse laws."""

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
        assert manifest["files"][name]["records"] == len(rows)
        assert manifest["files"][name]["sha256"] == hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
    assert len(data["sources.jsonl"]) == 17 and all(row["url"].startswith("https://") for row in data["sources.jsonl"])
    assert len(data["bounded-contexts.jsonl"]) == 11
    decisions = data["decision-points.jsonl"]
    assert len(decisions) == 55 and all(row["default"] is None and row["default_law"] == "forbidden" for row in decisions)
    libs = data["library-contracts.jsonl"]
    assert len(libs) == 11 and len({row["library_id"] for row in libs}) == 11
    assert sum(row["library_id"].startswith("library.business_glossary.") for row in libs) == 5
    assert sum(row["library_id"].startswith("library.ontology_model.") for row in libs) == 6
    decision_ids = {row["decision_id"] for row in decisions}
    for lib in libs:
        assert len(lib["public_types"]) >= 12 and len(lib["operations"]) == 4
        assert set(lib["operation_refs"]) == {op["operation_ref"] for op in lib["operations"]}
        assert set(lib["decision_refs"]) <= decision_ids and len(lib["decision_refs"]) == 5
        assert all(op["input_types"] and op["output_type"].startswith("Result<") for op in lib["operations"])
    reasoning = next(row for row in libs if row["library_id"] == "library.ontology_model.reasoning_entailment")
    shapes = next(row for row in libs if row["library_id"] == "library.ontology_model.shape_validation")
    imports = next(row for row in libs if row["library_id"] == "library.ontology_model.identity_import_closure")
    assert reasoning["effect_boundary"] == shapes["effect_boundary"] == "pure_no_io"
    assert imports["effect_boundary"] == "pure_effect_intents"
    laws = " ".join(law for lib in libs for law in lib["laws"]).lower()
    for phrase in ["same character sequence does not prove", "does not merge designation identity", "is not owl class subsumption", "ontology iri, version iri", "profile membership is a structural result", "open-world unknown", "shape conformance", "canonicalization and digest", "does not own source facts"]:
        assert phrase in laws, phrase
    offers = [row for row in data["compiler-contracts.jsonl"] if row["record_kind"] == "capability_offer"]
    assert len(data["compiler-contracts.jsonl"]) == 33 and len(offers) == 11
    assert all(not row["portable"] and not row["selectable"] and row["qualified_implementation_count"] == 0 for row in offers)
    assert len(data["negative-twins.jsonl"]) == 16 and manifest["completion_claim"] is False
    print("VALIDATION PASS semantic vocabulary/ontology: 11 exact boundaries, 55 no-default decisions, 0 qualified offers")


if __name__ == "__main__":
    main()
