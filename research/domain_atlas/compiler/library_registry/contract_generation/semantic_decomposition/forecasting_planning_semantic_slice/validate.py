#!/usr/bin/env python3
"""Validate the forecasting and integrated-planning semantic slice."""
import hashlib
import json

from build_forecasting_planning_semantic_slice import (
    AXES, HERE, LIBRARIES, NEIGHBORS, PRODUCTS, VACANCIES,
    build, declared_product_libraries, load_jsonl, outputs,
)


def assert_acyclic(rows: list[dict]) -> None:
    deps = {row["module_id"]: set(row["dependency_refs"]) for row in rows}
    remaining = set(deps)
    while remaining:
        ready = {node for node in remaining if not (deps[node] & remaining)}
        assert ready, f"semantic module dependency cycle: {sorted(remaining)}"
        remaining -= ready


def main() -> int:
    expected = outputs()
    for name, value in expected.items():
        path = HERE / name
        assert path.is_file(), f"missing {name}"
        assert path.read_text() == value, f"stale {name}"
    manifest = json.loads((HERE / "manifest.json").read_text())
    assert set(manifest["files"]) == set(expected) - {"manifest.json"}
    for name, claim in manifest["files"].items():
        data = (HERE / name).read_bytes()
        assert len(data) == claim["bytes"]
        assert hashlib.sha256(data).hexdigest() == claim["sha256"]

    built = build()
    source_ids = {row["source_id"] for row in built["sources"]}
    module_ids = {row["module_id"] for row in built["modules"]}
    assert len(source_ids) == len(built["sources"]) == 40
    assert len(module_ids) == len(built["modules"]) == 53
    assert all(row["primary_or_official"] and row["supported_claim"] and row["authority_limit"] for row in built["sources"])
    assert all(set(row["source_refs"]) <= source_ids for row in built["modules"])
    assert all(set(row["dependency_refs"]) <= module_ids for row in built["modules"])
    assert_acyclic(built["modules"])

    direct = declared_product_libraries()
    frontier = next(row for row in load_jsonl(HERE.parent / "analytical_formalism_frontier/formalism-frontier-clusters.jsonl") if row["cluster_id"] == "formalism.forecasting_planning")
    assert set(frontier["declared_concrete_library_refs"]) == direct
    assert set(frontier["product_refs"]) == PRODUCTS
    assert len(direct) == 12 and len(NEIGHBORS) == 28 and len(LIBRARIES) == 40
    assert not (direct & NEIGHBORS)
    registry_refs = {row["library_id"] for row in load_jsonl(HERE.parents[2] / "library-contributions.jsonl")}
    assert set(LIBRARIES) <= registry_refs

    assert len({row["law_id"] for row in built["laws"]}) == len(built["laws"]) == 57
    assert len({row["method_type_id"] for row in built["methods"]}) == len(built["methods"]) == 137
    assert len({row["expert_id"] for row in built["experts"]}) == len(built["experts"]) == 26
    assert len({row["innovation_id"] for row in built["innovations"]}) == len(built["innovations"]) == 15
    assert all(set(row["source_refs"]) <= source_ids for row in built["methods"] + built["experts"] + built["innovations"])
    assert all(row["llm_dependency"] == "none" for row in built["methods"])
    assert sum(row["ai_or_llm_dependency"] == "none" for row in built["innovations"]) >= 10

    bindings = built["libraries"]
    assert len(bindings) == len(LIBRARIES)
    assert {row["library_ref"] for row in bindings} == set(LIBRARIES)
    assert all(row["semantic_module_refs"] and set(row["semantic_module_refs"]) <= module_ids for row in bindings)
    assert all(set(row["evidence_refs"]) <= source_ids for row in bindings)
    assert all(row["compiler_binding"] == "REFUSED" and not row["completion_claim"] for row in bindings)

    axes = built["axes"]
    assert len(axes) == len(LIBRARIES) * len(AXES) == 640
    assert len({(row["library_ref"], row["axis"]) for row in axes}) == len(axes)
    assert all(not row["coordinate_answers"] and row["owner_decision"] == "UNRATIFIED" for row in axes)
    assert all(row["canonical_gaps_closed"] == 0 and not row["completion_claim"] for row in axes)

    findings = built["findings"]
    vacancy_refs = {ref for ref, _ in VACANCIES}
    assert len(vacancy_refs) == len(VACANCIES) == 26
    assert vacancy_refs.isdisjoint(LIBRARIES)
    assert {row.get("proposed_library_ref") for row in findings if row["candidate_disposition"] == "NEW_LIBRARY_BOUNDARY_CANDIDATE_UNRATIFIED"} == vacancy_refs
    planning = next(row for row in findings if row["finding_id"] == "finding.foreplan.integrated-planning-product.v1")
    assert planning["product_ref"] == "product.integrated_planning_workbench"
    assert planning["candidate_disposition"] == "RETAIN_INTEGRATED_PLANNING_WORKBENCH_WITH_EXACT_IMPORTED_OWNERS"
    assert next(row for row in findings if row["finding_id"] == "finding.foreplan.forecasting-product.v1")["candidate_disposition"] == "RETAIN_FORECASTING_WORKBENCH_BUT_NARROW_IMPORTED_OWNERS"
    assert next(row for row in findings if row["finding_id"] == "finding.foreplan.frontier-cluster-split.v1")["candidate_disposition"] == "SPLIT_FORECASTING_AND_PLANNING_PRODUCT_FORMALISMS"
    assert all(row["owner_decision"] == "UNRATIFIED" and row["canonical_gaps_closed"] == 0 for row in findings)

    context = built["context"]
    assert context["product_boundary_candidates"] == [
        {"product_ref": "product.forecasting_workbench", "status": "RETAIN_BUT_NARROW_UNRATIFIED"},
        {"product_ref": "product.integrated_planning_workbench", "status": "RETAIN_WITH_EXACT_IMPORTS_UNRATIFIED"},
    ]
    summary = built["summary"]
    assert summary["bound_libraries"] == 40 and summary["declared_product_libraries"] == 12
    assert summary["retained_products"] == 2 and summary["candidate_new_products"] == 0 and summary["candidate_new_library_vacancies"] == 26
    assert summary["library_axis_decision_candidates"] == 640
    assert summary["owner_decisions"] == summary["exact_contracts_selected"] == summary["qualified_implementations"] == summary["canonical_gaps_closed"] == 0
    assert not summary["completion_claim"]
    print("PASS forecasting/planning semantic slice: 53 modules, 137 methods, 26 experts and 15 innovations preserve two retained product boundaries, bind the exact 12-library forecasting product plus 28 justified neighbors, expose 26 compiler-library vacancies including 13 integrated-planning seams, and preserve 640 unresolved axis decisions")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
