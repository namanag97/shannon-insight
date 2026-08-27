#!/usr/bin/env python3
"""Validate the entity-resolution, master-data and reference-data semantic slice."""
import hashlib
import json

from build_entity_resolution_mastering_semantic_slice import (
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

    built = build()
    source_ids = {r["source_id"] for r in built["sources"]}
    module_ids = {r["module_id"] for r in built["modules"]}
    assert len(source_ids) == len(built["sources"]) == 42
    assert len(module_ids) == len(built["modules"]) == 55
    assert all(r["primary_or_official"] and r["supported_claim"] and r["authority_limit"] and r["url"].startswith("https://") for r in built["sources"])
    assert all(set(r["source_refs"]) <= source_ids and set(r["dependency_refs"]) <= module_ids for r in built["modules"])
    assert_acyclic(built["modules"])

    direct = declared_product_libraries()
    frontier = next(r for r in load_jsonl(HERE.parent / "analytical_formalism_frontier/formalism-frontier-clusters.jsonl") if r["cluster_id"] == "formalism.entity_resolution_mastering")
    assert set(frontier["declared_concrete_library_refs"]) == direct and set(frontier["product_refs"]) == PRODUCTS
    assert len(direct) == 20 and len(NEIGHBORS) == 32 and len(LIBRARIES) == 52 and not (direct & NEIGHBORS)
    registry_refs = {r["library_id"] for r in load_jsonl(HERE.parents[2] / "library-contributions.jsonl")}
    assert set(LIBRARIES) <= registry_refs

    assert len({r["law_id"] for r in built["laws"]}) == len(built["laws"]) == 65
    assert len({r["method_type_id"] for r in built["methods"]}) == len(built["methods"]) == 179
    assert len({r["expert_id"] for r in built["experts"]}) == len(built["experts"]) == 26
    assert len({r["innovation_id"] for r in built["innovations"]}) == len(built["innovations"]) == 15
    assert all(set(r["source_refs"]) <= source_ids for r in built["methods"] + built["experts"] + built["innovations"])
    assert all(r["llm_dependency"] == "none" for r in built["methods"])
    assert sum(r["ai_or_llm_dependency"] == "none" for r in built["innovations"]) >= 14

    bindings = built["libraries"]
    assert len(bindings) == 52 and {r["library_ref"] for r in bindings} == set(LIBRARIES)
    assert all(r["semantic_module_refs"] and set(r["semantic_module_refs"]) <= module_ids and set(r["evidence_refs"]) <= source_ids for r in bindings)
    assert all(r["compiler_binding"] == "REFUSED" and not r["completion_claim"] for r in bindings)
    axes = built["axes"]
    assert len(axes) == len(LIBRARIES) * len(AXES) == 832
    assert len({(r["library_ref"], r["axis"]) for r in axes}) == len(axes)
    assert all(not r["coordinate_answers"] and r["owner_decision"] == "UNRATIFIED" and r["canonical_gaps_closed"] == 0 for r in axes)

    findings = built["findings"]
    vacancy_refs = {ref for ref, _ in VACANCIES}
    assert len(vacancy_refs) == len(VACANCIES) == 23 and vacancy_refs.isdisjoint(LIBRARIES)
    assert {r.get("proposed_library_ref") for r in findings if r["candidate_disposition"] == "NEW_LIBRARY_BOUNDARY_CANDIDATE_UNRATIFIED"} == vacancy_refs
    split = next(r for r in findings if r["finding_id"] == "finding.entity.product.split-master-reference.v1")
    assert split["candidate_disposition"] == "RETAIN_INDEPENDENT_PRODUCT_BOUNDARIES_AFTER_SPLIT"
    assert split["product_refs"] == ["product.master_data_governance", "product.reference_data_governance"]
    assert split["legacy_product_ref"] == "product.master_reference_data"
    assert next(r for r in findings if r["finding_id"] == "finding.entity.binding.reclassify-master.v1")["candidate_disposition"] == "RECLASSIFY_MASTER_LIBRARIES_FROM_ENTITY_PRODUCT_OWNERSHIP_TO_CAPABILITY_IMPORTS"
    assert next(r for r in findings if r["finding_id"] == "finding.entity.canonicalization-homonym.v1")["candidate_disposition"] == "SPLIT_CANONICALIZATION_HOMONYM_INTO_TYPED_OPERATIONS"
    assert all(r["owner_decision"] == "UNRATIFIED" and r["canonical_gaps_closed"] == 0 for r in findings)
    assert built["context"]["product_boundary_candidates"] == [
        {"product_ref": "product.entity_resolution", "status": "RETAIN_BUT_NARROW_UNRATIFIED"},
        {"product_ref": "product.master_data_governance", "status": "RETAINED_BOUNDARY_UNRATIFIED"},
        {"product_ref": "product.reference_data_governance", "status": "RETAINED_BOUNDARY_UNRATIFIED"},
    ]
    s = built["summary"]
    assert s["bound_libraries"] == 52 and s["library_axis_decision_candidates"] == 832
    assert s["retained_split_products"] == 2 and s["candidate_new_library_vacancies"] == 23
    assert s["owner_decisions"] == s["exact_contracts_selected"] == s["qualified_implementations"] == s["canonical_gaps_closed"] == 0 and not s["completion_claim"]
    print("PASS entity-resolution/master/reference semantic slice: 55 modules, 179 methods, 26 experts and 15 innovations bind the exact 20-library union of three retained product boundaries plus 32 justified neighbors, preserve the master/reference split, narrow entity-resolution ownership, expose 23 library vacancies and preserve 832 unresolved axis decisions")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
