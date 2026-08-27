#!/usr/bin/env python3
"""Validate transformation-build seams, exact APIs, decisions and authority laws."""

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
    assert len(sources) == 27 and all(row["url"].startswith("https://") for row in sources)
    assert all(row["source_kind"] == "primary_or_official" and row["does_not_prove"] for row in sources)

    contexts = {row["context_id"] for row in data["bounded-contexts.jsonl"]}
    assert contexts == {
        "context.transform_build.definition_selection",
        "context.transform_build.materialization",
        "context.transform_build.evidence",
    }

    methods = {
        json.loads(line)["method_id"]
        for line in (ROOT.parents[2] / "product_ontology/boundary_method_ensemble/methods.jsonl").read_text(encoding="utf-8").splitlines()
        if line.strip()
    }
    lenses = data["boundary-lens-adjudication.jsonl"]
    assert len(lenses) == 12
    assert {row["lens"] for row in lenses} == {name for name, *_ in build_corpus.LENSES}
    assert all(row["method_refs"] and set(row["method_refs"]) <= methods for row in lenses)

    decisions = data["decision-points.jsonl"]
    assert len(decisions) == 93
    assert all(row["default"] is None and row["default_law"] == "forbidden" for row in decisions)
    assert len({row["decision_id"] for row in decisions}) == len(decisions)

    libraries = {row["library_id"]: row for row in data["library-contracts.jsonl"]}
    assert set(libraries) == {
        "library.transform_definition.compiler",
        "library.transform_selection.closure",
        "library.materialization.incremental_planner",
        "library.materialization.mutation_protocol",
        "library.transform_build.evidence",
    }
    expected_ops = {
        "library.transform_definition.compiler": 8,
        "library.transform_selection.closure": 7,
        "library.materialization.incremental_planner": 10,
        "library.materialization.mutation_protocol": 7,
        "library.transform_build.evidence": 7,
    }
    expected_decisions = {
        "library.transform_definition.compiler": 23,
        "library.transform_selection.closure": 15,
        "library.materialization.incremental_planner": 25,
        "library.materialization.mutation_protocol": 15,
        "library.transform_build.evidence": 15,
    }
    for library_id, library in libraries.items():
        assert len(library["operations"]) == expected_ops[library_id]
        assert len(library["decision_refs"]) == expected_decisions[library_id]
        assert len(library["public_types"]) >= 40
        assert set(library["operation_refs"]) == {row["operation_ref"] for row in library["operations"]}
        assert all(row["input_types"] and row["output_type"].startswith("Result<") and row["purity"] == "pure" for row in library["operations"])
        assert library["gaps"] and not library["qualification_required"]
    assert libraries["library.materialization.mutation_protocol"]["effect_boundary"] == "pure_effect_intents"
    assert all(
        row["effect_boundary"] == "pure_no_io"
        for key, row in libraries.items() if key != "library.materialization.mutation_protocol"
    )

    verdicts = {row["verdict_id"]: row for row in data["boundary-verdicts.jsonl"]}
    assert set(verdicts) == {
        "verdict.transform-build.transform-manifest-split",
        "verdict.transform-build.materialization-split",
        "verdict.transform-build.imported-neighbors",
    }
    assert verdicts["verdict.transform-build.transform-manifest-split"]["supersedes_abstract_ref"] == "library.transform_manifest"
    assert verdicts["verdict.transform-build.materialization-split"]["supersedes_abstract_ref"] == "library.materialization"

    laws = " ".join(law for row in libraries.values() for law in row["laws"]).lower()
    for phrase in [
        "definition compilation, invocation selection", "disabled, unselected, deferred", "full refresh and incremental",
        "late arrival, correction, deletion", "append, merge, delete-insert", "unknown mutation completion",
        "publication candidate", "model or agent may propose",
    ]:
        assert phrase in laws, phrase
    exclusions = " ".join(value for row in libraries.values() for value in row["must_not_own"]).lower()
    for phrase in ["package", "query", "scheduling", "physical", "quality", "publication", "provider qualification"]:
        assert phrase in exclusions, phrase

    compiler_rows = data["compiler-contracts.jsonl"]
    offers = [row for row in compiler_rows if row["record_kind"] == "capability_offer"]
    assert len(compiler_rows) == 15 and len(offers) == 5
    assert all(row["qualified_implementation_count"] == 0 and not row["portable"] and not row["selectable"] for row in offers)
    assert len(data["negative-twins.jsonl"]) == 32
    assert manifest["completion_claim"] is False and manifest["qualified_implementation_count"] == 0
    print("VALIDATION PASS transformation build: 5 libraries, 93 no-default decisions, 39 pure operations, 12 lenses, 32 negative twins, 0 qualified offers")


if __name__ == "__main__":
    main()
