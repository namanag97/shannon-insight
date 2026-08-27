#!/usr/bin/env python3
"""Validate the general statistical inference semantic slice."""
import hashlib
import json

from build_statistical_inference_semantic_slice import (
    AXES,
    HERE,
    LIBRARIES,
    MODULE_MAP,
    NEIGHBORS,
    PRODUCT,
    VACANCIES,
    build,
    outputs,
)


def main() -> int:
    for name, expected in outputs().items():
        path = HERE / name
        assert path.is_file(), f"missing {name}"
        assert path.read_text() == expected, f"stale {name}"
    manifest = json.loads((HERE / "manifest.json").read_text())
    for name, claim in manifest["files"].items():
        data = (HERE / name).read_bytes()
        assert len(data) == claim["bytes"]
        assert hashlib.sha256(data).hexdigest() == claim["sha256"]

    built = build()
    source_ids = {row["source_id"] for row in built["sources"]}
    module_ids = {row["module_id"] for row in built["modules"]}
    assert len(source_ids) == len(built["sources"]) == 30
    assert len(module_ids) == len(built["modules"]) == 41
    assert all(set(row["source_refs"]) <= source_ids for row in built["modules"])
    assert all(set(row["dependency_refs"]) <= module_ids for row in built["modules"])
    assert all(set(refs) <= {ref.removeprefix("module.statistics.") for ref in module_ids} for refs in MODULE_MAP.values())

    law_ids = {row["law_id"] for row in built["laws"]}
    method_ids = {row["method_type_id"] for row in built["methods"]}
    expert_ids = {row["expert_id"] for row in built["experts"]}
    innovation_ids = {row["innovation_id"] for row in built["innovations"]}
    assert len(law_ids) == len(built["laws"]) == 46
    assert len(method_ids) == len(built["methods"]) == 78
    assert len(expert_ids) == len(built["experts"]) == 16
    assert len(innovation_ids) == len(built["innovations"]) == 10
    assert all(set(row["source_refs"]) <= source_ids for row in built["experts"] + built["innovations"])
    assert all(not row["ai_or_llm_dependency"] for row in built["innovations"])

    bindings = built["libraries"]
    assert len(LIBRARIES) == len(bindings) == 22
    assert {row["library_ref"] for row in bindings} == set(LIBRARIES)
    assert len(NEIGHBORS) == 21
    assert all(set(row["semantic_module_refs"]) <= module_ids for row in bindings)
    assert all(set(row["evidence_refs"]) <= source_ids for row in bindings)
    assert all(row["compiler_binding"] == "REFUSED" and not row["completion_claim"] for row in bindings)
    assert sum(PRODUCT in row["downstream_product_refs"] for row in bindings) == 1
    assert sum(row["downstream_contract_route"].startswith("MISSING") for row in bindings) == 3

    axis_rows = built["axes"]
    assert len(axis_rows) == len(LIBRARIES) * len(AXES) == 352
    assert len({(row["library_ref"], row["axis"]) for row in axis_rows}) == len(axis_rows)
    assert all(not row["coordinate_answers"] and row["owner_decision"] == "UNRATIFIED" for row in axis_rows)
    assert all(row["canonical_gaps_closed"] == 0 and not row["completion_claim"] for row in axis_rows)

    vacancy_refs = {ref for ref, _ in VACANCIES}
    findings = built["findings"]
    assert len(vacancy_refs) == len(VACANCIES) == 8
    assert vacancy_refs.isdisjoint(LIBRARIES)
    assert {row.get("proposed_library_ref") for row in findings if row["candidate_disposition"] == "NEW_LIBRARY_BOUNDARY_CANDIDATE_UNRATIFIED"} == vacancy_refs
    assert all(row["owner_decision"] == "UNRATIFIED" for row in findings)

    summary = built["summary"]
    assert summary["bound_libraries"] == 22
    assert summary["candidate_new_library_vacancies"] == 8
    assert summary["library_axis_decision_candidates"] == 352
    assert summary["owner_decisions"] == summary["exact_contracts_selected"] == summary["qualified_implementations"] == summary["canonical_gaps_closed"] == 0
    assert not summary["completion_claim"]
    print("PASS statistical inference semantic slice: 41 evidence-backed modules bind 22 exact libraries, expose 8 typed library-boundary vacancies and retain 352 unresolved axis decisions while population, sample, estimand, estimator, uncertainty, evidence, reproducibility and authority seams remain explicit")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
