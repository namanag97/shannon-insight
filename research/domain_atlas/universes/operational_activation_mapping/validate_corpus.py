#!/usr/bin/env python3
"""Validate activation-mapping seams, exact APIs, decisions and authority laws."""

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
    sources = data["sources.jsonl"]
    assert len(sources) >= 25 and all(row["url"].startswith("https://") for row in sources)
    assert all(row["source_kind"] == "primary_or_official" and row["does_not_prove"] for row in sources)
    assert len(data["bounded-contexts.jsonl"]) == 3
    methods = {json.loads(line)["method_id"] for line in (ROOT.parents[2] / "product_ontology/boundary_method_ensemble/methods.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()}
    lenses = data["boundary-lens-adjudication.jsonl"]
    assert len(lenses) == 12 and all(row["method_refs"] and set(row["method_refs"]) <= methods for row in lenses)
    decisions = data["decision-points.jsonl"]
    assert len(decisions) == 80 and all(row["default"] is None and row["default_law"] == "forbidden" for row in decisions)
    libraries = {row["library_id"]: row for row in data["library-contracts.jsonl"]}
    assert set(libraries) == {"library.activation.destination_profile.compiler", "library.activation.mapping.compiler", "library.activation.mapping.evaluator"}
    expected_ops = {"library.activation.destination_profile.compiler": 8, "library.activation.mapping.compiler": 9, "library.activation.mapping.evaluator": 9}
    expected_decisions = {"library.activation.destination_profile.compiler": 26, "library.activation.mapping.compiler": 34, "library.activation.mapping.evaluator": 20}
    for library_id, library in libraries.items():
        assert len(library["operations"]) == expected_ops[library_id]
        assert len(library["decision_refs"]) == expected_decisions[library_id]
        assert len(library["public_types"]) >= 38
        assert set(library["operation_refs"]) == {row["operation_ref"] for row in library["operations"]}
        assert all(row["input_types"] and row["output_type"].startswith("Result<") and row["purity"] == "pure" for row in library["operations"])
        assert library["gaps"] and not library["qualification_required"]
    assert libraries["library.activation.mapping.evaluator"]["effect_boundary"] == "pure_effect_proposals"
    assert all(row["effect_boundary"] == "pure_no_io" for key, row in libraries.items() if key != "library.activation.mapping.evaluator")
    verdicts = {row["verdict_id"]: row for row in data["boundary-verdicts.jsonl"]}
    assert verdicts["verdict.activation-mapping.split"]["supersedes_abstract_ref"] == "library.activation_mapping"
    laws = " ".join(law for row in libraries.values() for law in row["laws"]).lower()
    for phrase in ["proposal is not authorization", "zero, one and many", "identity resolution evidence", "unknown completion", "partial failure", "model or agent may propose"]:
        assert phrase in laws, phrase
    exclusions = " ".join(value for row in libraries.values() for value in row["must_not_own"]).lower()
    for phrase in ["credential", "identity", "policy", "authorization", "effect execution", "business outcome"]:
        assert phrase in exclusions, phrase
    compiler_rows = data["compiler-contracts.jsonl"]
    offers = [row for row in compiler_rows if row["record_kind"] == "capability_offer"]
    assert len(compiler_rows) == 9 and len(offers) == 3
    assert all(row["qualified_implementation_count"] == 0 and not row["portable"] and not row["selectable"] for row in offers)
    assert len(data["negative-twins.jsonl"]) == 32
    assert manifest["completion_claim"] is False and manifest["qualified_implementation_count"] == 0
    print("VALIDATION PASS activation mapping: 3 libraries, 80 no-default decisions, 26 pure operations, 12 lenses, 32 negative twins, 0 qualified offers")


if __name__ == "__main__":
    main()
