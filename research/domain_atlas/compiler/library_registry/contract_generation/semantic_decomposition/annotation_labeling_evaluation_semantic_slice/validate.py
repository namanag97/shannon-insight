#!/usr/bin/env python3
"""Validate the annotation, labeling and reference-evaluation semantic slice."""
import hashlib
import json

from build_annotation_labeling_evaluation_semantic_slice import (
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
        assert len(data) == claim["bytes"] and hashlib.sha256(data).hexdigest() == claim["sha256"]

    built = build(); source_ids = {r["source_id"] for r in built["sources"]}; module_ids = {r["module_id"] for r in built["modules"]}
    assert len(source_ids) == len(built["sources"]) == 41
    assert len(module_ids) == len(built["modules"]) == 52
    assert all(r["primary_or_official"] and r["supported_claim"] and r["authority_limit"] for r in built["sources"])
    assert all(set(r["source_refs"]) <= source_ids and set(r["dependency_refs"]) <= module_ids for r in built["modules"])
    assert_acyclic(built["modules"])

    direct = declared_product_libraries()
    frontier = next(r for r in load_jsonl(HERE.parent / "analytical_formalism_frontier/formalism-frontier-clusters.jsonl") if r["cluster_id"] == "formalism.annotation_labeling_evaluation")
    assert set(frontier["declared_concrete_library_refs"]) == direct and set(frontier["product_refs"]) == PRODUCTS
    assert len(direct) == 24 and len(NEIGHBORS) == 36 and len(LIBRARIES) == 60 and not (direct & NEIGHBORS)
    registry_refs = {r["library_id"] for r in load_jsonl(HERE.parents[2] / "library-contributions.jsonl")}
    assert set(LIBRARIES) <= registry_refs

    assert len({r["law_id"] for r in built["laws"]}) == len(built["laws"]) == 58
    assert len({r["method_type_id"] for r in built["methods"]}) == len(built["methods"]) == 149
    assert len({r["expert_id"] for r in built["experts"]}) == len(built["experts"]) == 26
    assert len({r["innovation_id"] for r in built["innovations"]}) == len(built["innovations"]) == 15
    assert all(set(r["source_refs"]) <= source_ids for r in built["methods"] + built["experts"] + built["innovations"])
    assert all(r["llm_dependency"] == "none" for r in built["methods"])
    assert sum(r["ai_or_llm_dependency"] == "none" for r in built["innovations"]) >= 12

    bindings = built["libraries"]
    assert len(bindings) == 60 and {r["library_ref"] for r in bindings} == set(LIBRARIES)
    assert all(r["semantic_module_refs"] and set(r["semantic_module_refs"]) <= module_ids and set(r["evidence_refs"]) <= source_ids for r in bindings)
    assert all(r["compiler_binding"] == "REFUSED" and not r["completion_claim"] for r in bindings)
    axes = built["axes"]
    assert len(axes) == len(LIBRARIES) * len(AXES) == 960
    assert len({(r["library_ref"], r["axis"]) for r in axes}) == len(axes)
    assert all(not r["coordinate_answers"] and r["owner_decision"] == "UNRATIFIED" and r["canonical_gaps_closed"] == 0 for r in axes)

    findings = built["findings"]; vacancy_refs = {ref for ref, _ in VACANCIES}
    assert len(vacancy_refs) == len(VACANCIES) == 31 and vacancy_refs.isdisjoint(LIBRARIES)
    assert {r.get("proposed_library_ref") for r in findings if r["candidate_disposition"] == "NEW_LIBRARY_BOUNDARY_CANDIDATE_UNRATIFIED"} == vacancy_refs
    dataset = next(r for r in findings if r["finding_id"] == "finding.annotation.dataset-curation-product.v1")
    assert dataset["product_ref"] == "product.dataset_curation_workbench"
    assert dataset["candidate_disposition"] == "RETAIN_DATASET_CURATION_WORKBENCH_WITH_EXACT_IMPORTED_OWNERS"
    assert next(r for r in findings if r["finding_id"] == "finding.annotation.ground-truth-rename.v1")["candidate_disposition"] == "RENAME_GROUND_TRUTH_TO_ACCEPTED_REFERENCE_EDITION"
    assert all(r["owner_decision"] == "UNRATIFIED" and r["canonical_gaps_closed"] == 0 for r in findings)
    assert built["context"]["product_boundary_candidates"] == [
        {"product_ref": "product.annotation_operations", "status": "RETAIN_BUT_NARROW_UNRATIFIED"},
        {"product_ref": "product.dataset_curation_workbench", "status": "RETAIN_WITH_EXACT_IMPORTS_UNRATIFIED"},
    ]
    s = built["summary"]
    assert s["bound_libraries"] == 60 and s["library_axis_decision_candidates"] == 960
    assert s["retained_products"] == 2 and s["candidate_new_products"] == 0 and s["candidate_new_library_vacancies"] == 31
    assert s["owner_decisions"] == s["exact_contracts_selected"] == s["qualified_implementations"] == s["canonical_gaps_closed"] == 0 and not s["completion_claim"]
    print("PASS annotation/labeling/evaluation semantic slice: 52 modules, 149 methods, 26 experts and 15 innovations preserve Annotation Operations and Dataset Curation as separate retained products, bind 24 existing product libraries plus 36 justified neighbors, expose 31 exact library vacancies including 14 Dataset Curation seams, replace absolute ground truth with accepted reference editions, and preserve 960 unresolved axis decisions")
    return 0


if __name__ == "__main__": raise SystemExit(main())
