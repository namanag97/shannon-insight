#!/usr/bin/env python3
"""Validate the quality, reconciliation and control semantic slice."""
import hashlib
import json

from build_quality_reconciliation_controls_semantic_slice import (
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
    expected_outputs = outputs()
    for name, expected in expected_outputs.items():
        path = HERE / name
        assert path.is_file(), f"missing {name}"
        assert path.read_text() == expected, f"stale {name}"
    manifest = json.loads((HERE / "manifest.json").read_text())
    assert set(manifest["files"]) == set(expected_outputs) - {"manifest.json"}
    for name, claim in manifest["files"].items():
        data = (HERE / name).read_bytes()
        assert len(data) == claim["bytes"]
        assert hashlib.sha256(data).hexdigest() == claim["sha256"]

    built = build()
    source_ids = {row["source_id"] for row in built["sources"]}
    module_ids = {row["module_id"] for row in built["modules"]}
    assert len(source_ids) == len(built["sources"]) == 80
    assert len(module_ids) == len(built["modules"]) == 37
    assert all(row["primary_or_official"] and row["supported_claim"] and row["authority_limit"] for row in built["sources"])
    assert all(set(row["source_refs"]) <= source_ids for row in built["modules"])
    assert all(set(row["dependency_refs"]) <= module_ids for row in built["modules"])
    assert_acyclic(built["modules"])

    frontier = next(
        row for row in load_jsonl(HERE.parent / "analytical_formalism_frontier/formalism-frontier-clusters.jsonl")
        if row["cluster_id"] == "formalism.quality_reconciliation_controls"
    )
    direct = declared_product_libraries()
    assert set(frontier["declared_concrete_library_refs"]) == direct
    assert set(frontier["product_refs"]) == PRODUCTS
    assert len(direct) == 33
    assert not (direct & NEIGHBORS)
    assert set(LIBRARIES) == direct | NEIGHBORS
    assert len(LIBRARIES) == 72 and len(NEIGHBORS) == 39

    product_sets = {}
    for product in PRODUCTS:
        product_sets[product] = {
            edge["concrete_library_ref"]
            for row in load_jsonl(HERE.parent / "product_coordinate_binding_projection/subject-coordinate-binding-projections.jsonl")
            if row["product_ref"] == product
            for edge in row["concrete_bindings"]
        }
    assert len(product_sets["product.data_quality_operations"]) == 30
    assert len(product_sets["product.reconciliation_control_operations"]) == 9
    assert len(set.intersection(*product_sets.values())) == 6
    assert set.union(*product_sets.values()) == direct
    excluded_legacy = {
        "library.qor.contract_declaration_kernel",
        "library.qor.reference_master_alignment_kernel",
        "library.qor.accounting_control_reconciliation_kernel",
        "library.qor.duplicate_entity_resolution_kernel",
    }
    assert excluded_legacy.isdisjoint(LIBRARIES)

    assert len({row["law_id"] for row in built["laws"]}) == len(built["laws"]) == 92
    assert len({row["method_type_id"] for row in built["methods"]}) == len(built["methods"]) == 148
    assert len({row["expert_id"] for row in built["experts"]}) == len(built["experts"]) == 20
    assert len({row["innovation_id"] for row in built["innovations"]}) == len(built["innovations"]) == 26
    assert all(set(row["source_refs"]) <= source_ids for row in built["methods"] + built["experts"] + built["innovations"])
    assert all(row["effect_class"] in {"pure", "effectful_evidence_io"} for row in built["methods"])
    assert all(row["authority_limit"] for row in built["experts"])
    assert all(not row["ai_or_llm_dependency"] for row in built["innovations"])

    bindings = built["libraries"]
    assert len(bindings) == len(LIBRARIES) == 72
    assert {row["library_ref"] for row in bindings} == set(LIBRARIES)
    assert all(row["semantic_module_refs"] and set(row["semantic_module_refs"]) <= module_ids for row in bindings)
    assert all(set(row["evidence_refs"]) <= source_ids for row in bindings)
    assert all(row["compiler_binding"] == "REFUSED" and not row["completion_claim"] for row in bindings)
    assert all("OWNER_RATIFICATION_MISSING" in row["refusal_reasons"] for row in bindings)
    assert all(set(row["downstream_product_refs"]) & PRODUCTS for row in bindings if row["library_ref"] in direct)
    assert sum(row["downstream_contract_route"].startswith("MISSING") for row in bindings) == 17

    axis_rows = built["axes"]
    assert len(axis_rows) == len(LIBRARIES) * len(AXES) == 1152
    assert len({(row["library_ref"], row["axis"]) for row in axis_rows}) == len(axis_rows)
    assert all(row["semantic_module_refs"] and set(row["semantic_module_refs"]) <= module_ids for row in axis_rows)
    assert all(set(row["evidence_refs"]) <= source_ids for row in axis_rows)
    assert all(not row["coordinate_answers"] and row["owner_decision"] == "UNRATIFIED" for row in axis_rows)
    assert all(row["canonical_gaps_closed"] == 0 and not row["completion_claim"] for row in axis_rows)

    vacancy_refs = {ref for ref, _ in VACANCIES}
    findings = built["findings"]
    assert len(vacancy_refs) == len(VACANCIES) == 10
    assert vacancy_refs.isdisjoint(LIBRARIES)
    assert {
        row.get("proposed_library_ref") for row in findings
        if row["candidate_disposition"] == "NEW_LIBRARY_BOUNDARY_CANDIDATE_UNRATIFIED"
    } == vacancy_refs
    assert all(row["owner_decision"] == "UNRATIFIED" for row in findings)
    dispositions = {row["finding_id"]: row["candidate_disposition"] for row in findings}
    assert dispositions["finding.quality.product-split.v1"] == "RETAIN_TWO_PRODUCTS_QUALITY_OPERATIONS_AND_RECONCILIATION_CONTROL_OPERATIONS"
    assert dispositions["finding.quality.observability-capability.v1"] == "RETAIN_DATA_QUALITY_OBSERVABILITY_AS_COMPOSABLE_CAPABILITIES_NOT_A_THIRD_SEMANTIC_OWNER"
    assert dispositions["finding.quality.accounting-vertical.v1"] == "ACCOUNTING_CONTROL_RECONCILIATION_IS_A_VERTICAL_PROFILE_NOT_UNIVERSAL_HORIZONTAL_TRUTH"
    assert dispositions["finding.quality.repair-authority.v1"].startswith("REPAIR_METHODS_PRODUCE_PROPOSALS_")

    summary = built["summary"]
    assert summary["bound_libraries"] == 72
    assert summary["declared_product_libraries"] == 33
    assert summary["candidate_new_library_vacancies"] == 10
    assert summary["library_axis_decision_candidates"] == 1152
    assert summary["owner_decisions"] == summary["exact_contracts_selected"] == summary["qualified_implementations"] == summary["canonical_gaps_closed"] == 0
    assert not summary["completion_claim"]
    print("PASS quality/reconciliation/controls semantic slice: 37 evidence-backed modules bind the exact 33-library two-product graph plus 39 justified neighbors, expose 10 typed vacancies and retain 1,152 unresolved axis decisions while requirement, observation, signal, defect, break, correction, certificate and decision/effect seams remain explicit")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
