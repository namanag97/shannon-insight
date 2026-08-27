#!/usr/bin/env python3
"""Validate the decision-automation and assurance semantic slice."""
import hashlib
import json

from build_decision_automation_assurance_semantic_slice import (
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
    assert len(source_ids) == len(built["sources"]) == 43
    assert len(module_ids) == len(built["modules"]) == 44
    assert all(row["primary_or_official"] and row["supported_claim"] and row["authority_limit"] and row["url"].startswith("https://") for row in built["sources"])
    assert all(set(row["source_refs"]) <= source_ids and set(row["dependency_refs"]) <= module_ids for row in built["modules"])
    assert_acyclic(built["modules"])

    direct = declared_product_libraries()
    frontier = next(row for row in load_jsonl(HERE.parent / "analytical_formalism_frontier/formalism-frontier-clusters.jsonl") if row["cluster_id"] == "formalism.decision_automation_assurance")
    assert set(frontier["declared_concrete_library_refs"]) == direct
    assert set(frontier["product_refs"]) == PRODUCTS
    assert len(direct) == 20 and len(NEIGHBORS) == 48 and len(LIBRARIES) == 68
    assert not (direct & NEIGHBORS)
    registry_refs = {row["library_id"] for row in load_jsonl(HERE.parents[2] / "library-contributions.jsonl")}
    assert set(LIBRARIES) <= registry_refs

    assert len({row["law_id"] for row in built["laws"]}) == len(built["laws"]) == 65
    assert len({row["method_type_id"] for row in built["methods"]}) == len(built["methods"]) == 170
    assert len({row["expert_id"] for row in built["experts"]}) == len(built["experts"]) == 26
    assert len({row["innovation_id"] for row in built["innovations"]}) == len(built["innovations"]) == 15
    assert all(set(row["source_refs"]) <= source_ids for row in built["methods"] + built["experts"] + built["innovations"])
    assert all(row["llm_dependency"] == "none" for row in built["methods"])
    assert sum(row["ai_or_llm_dependency"] == "none" for row in built["innovations"]) >= 14

    bindings = built["libraries"]
    assert len(bindings) == 68 and {row["library_ref"] for row in bindings} == set(LIBRARIES)
    assert all(row["semantic_module_refs"] and set(row["semantic_module_refs"]) <= module_ids and set(row["evidence_refs"]) <= source_ids for row in bindings)
    assert all(row["compiler_binding"] == "REFUSED" and not row["completion_claim"] for row in bindings)
    axes = built["axes"]
    assert len(axes) == len(LIBRARIES) * len(AXES) == 1088
    assert len({(row["library_ref"], row["axis"]) for row in axes}) == len(axes)
    assert all(not row["coordinate_answers"] and row["owner_decision"] == "UNRATIFIED" and row["canonical_gaps_closed"] == 0 for row in axes)

    findings = built["findings"]
    vacancy_refs = {ref for ref, _ in VACANCIES}
    assert len(vacancy_refs) == len(VACANCIES) == 24 and vacancy_refs.isdisjoint(LIBRARIES)
    assert {row.get("proposed_library_ref") for row in findings if row["candidate_disposition"] == "NEW_LIBRARY_BOUNDARY_CANDIDATE_UNRATIFIED"} == vacancy_refs
    expected_dispositions = {
        "finding.decision_assurance.products.retain-separate.v1": "RETAIN_TWO_INDEPENDENT_PRODUCTS_WITH_TYPED_ACL",
        "finding.decision_assurance.decision-authority-seam.v1": "RECLASSIFY_AUTHORIZER_AND_EFFECT_PORT_AS_IMPORTED_AUTHORITY_CAPABILITIES",
        "finding.decision_assurance.generic-evidence-seam.v1": "RECLASSIFY_GENERIC_EVIDENCE_CARRIERS_AS_IMPORTED_CAPABILITIES",
        "finding.decision_assurance.attestation-seam.v1": "SPLIT_ATTESTATION_APPRAISAL_VERDICT_AND_RELIANCE",
        "finding.decision_assurance.policy-homonym.v1": "SPLIT_POLICY_HOMONYM_INTO_TYPED_POLICY_KINDS",
    }
    by_id = {row["finding_id"]: row for row in findings}
    assert all(by_id[key]["candidate_disposition"] == value for key, value in expected_dispositions.items())
    assert all(row["owner_decision"] == "UNRATIFIED" and row["canonical_gaps_closed"] == 0 for row in findings)
    assert built["context"]["product_boundary_candidates"] == [
        {"product_ref": "product.assurance_case_appraisal", "status": "RETAIN_BUT_NARROW_UNRATIFIED"},
        {"product_ref": "product.decision_automation", "status": "RETAIN_BUT_NARROW_UNRATIFIED"},
    ]
    assert built["context"]["candidate_new_products"] == []

    summary = built["summary"]
    assert summary["bound_libraries"] == 68 and summary["library_axis_decision_candidates"] == 1088
    assert summary["candidate_new_products"] == 0 and summary["candidate_new_library_vacancies"] == 24
    assert summary["owner_decisions"] == summary["exact_contracts_selected"] == summary["qualified_implementations"] == summary["canonical_gaps_closed"] == 0
    assert not summary["completion_claim"]
    print("PASS decision-automation/assurance semantic slice: 44 modules, 170 methods, 26 experts and 15 innovations bind the exact 20-library two-product graph plus 48 justified neighbors, retain two independent products, expose 24 library vacancies and preserve 1,088 unresolved axis decisions")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
