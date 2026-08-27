#!/usr/bin/env python3
"""Validate the BI, visualization, semantic-metric and formula semantic slice."""
import hashlib
import json

from build_bi_visualization_metrics_semantic_slice import (
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
    for name, expected in outputs().items():
        path = HERE / name
        assert path.is_file(), f"missing {name}"
        assert path.read_text() == expected, f"stale {name}"
    manifest = json.loads((HERE / "manifest.json").read_text())
    assert set(manifest["files"]) == set(outputs()) - {"manifest.json"}
    for name, claim in manifest["files"].items():
        data = (HERE / name).read_bytes()
        assert len(data) == claim["bytes"]
        assert hashlib.sha256(data).hexdigest() == claim["sha256"]

    built = build()
    source_ids = {row["source_id"] for row in built["sources"]}
    module_ids = {row["module_id"] for row in built["modules"]}
    assert len(source_ids) == len(built["sources"]) == 50
    assert len({row["source_registry_ref"] for row in built["sources"]}) == 50
    assert len(module_ids) == len(built["modules"]) == 65
    assert all(row["primary_or_official"] for row in built["sources"])
    assert all(row["supported_claim"] and row["authority_limit"] for row in built["sources"])
    assert all(set(row["source_refs"]) <= source_ids for row in built["modules"])
    assert all(set(row["dependency_refs"]) <= module_ids for row in built["modules"])
    assert_acyclic(built["modules"])

    frontier = next(
        row for row in load_jsonl(HERE.parent / "analytical_formalism_frontier/formalism-frontier-clusters.jsonl")
        if row["cluster_id"] == "formalism.bi_visualization_metrics"
    )
    direct = declared_product_libraries()
    assert set(frontier["declared_concrete_library_refs"]) == direct
    assert set(frontier["product_refs"]) == PRODUCTS
    assert len(direct) == 39
    assert not (direct & NEIGHBORS)
    assert set(LIBRARIES) == direct | NEIGHBORS
    assert len(LIBRARIES) == 70 and len(NEIGHBORS) == 31

    law_ids = {row["law_id"] for row in built["laws"]}
    method_ids = {row["method_type_id"] for row in built["methods"]}
    expert_ids = {row["expert_id"] for row in built["experts"]}
    innovation_ids = {row["innovation_id"] for row in built["innovations"]}
    assert len(law_ids) == len(built["laws"]) == 74
    assert len(method_ids) == len(built["methods"]) == 158
    assert len(expert_ids) == len(built["experts"]) == 24
    assert len(innovation_ids) == len(built["innovations"]) == 14
    assert all(set(row["source_refs"]) <= source_ids for row in built["experts"] + built["innovations"])
    assert all(row["authority_limit"] for row in built["experts"])
    assert all(not row["ai_or_llm_dependency"] for row in built["innovations"])

    bindings = built["libraries"]
    assert len(bindings) == len(LIBRARIES) == 70
    assert {row["library_ref"] for row in bindings} == set(LIBRARIES)
    assert all(row["semantic_module_refs"] and set(row["semantic_module_refs"]) <= module_ids for row in bindings)
    assert all(set(row["evidence_refs"]) <= source_ids for row in bindings)
    assert all(row["compiler_binding"] == "REFUSED" and not row["completion_claim"] for row in bindings)
    assert all("OWNER_RATIFICATION_MISSING" in row["refusal_reasons"] for row in bindings)
    assert all(set(row["downstream_product_refs"]) & PRODUCTS for row in bindings if row["library_ref"] in direct)
    assert sum(row["downstream_contract_route"].startswith("MISSING") for row in bindings) == 9

    axis_rows = built["axes"]
    assert len(axis_rows) == len(LIBRARIES) * len(AXES) == 1120
    assert len({(row["library_ref"], row["axis"]) for row in axis_rows}) == len(axis_rows)
    assert all(row["semantic_module_refs"] and set(row["semantic_module_refs"]) <= module_ids for row in axis_rows)
    assert all(set(row["evidence_refs"]) <= source_ids for row in axis_rows)
    assert all(not row["coordinate_answers"] and row["owner_decision"] == "UNRATIFIED" for row in axis_rows)
    assert all(row["canonical_gaps_closed"] == 0 and not row["completion_claim"] for row in axis_rows)

    vacancy_refs = {ref for ref, _ in VACANCIES}
    findings = built["findings"]
    assert len(vacancy_refs) == len(VACANCIES) == 12
    assert vacancy_refs.isdisjoint(LIBRARIES)
    assert {
        row.get("proposed_library_ref") for row in findings
        if row["candidate_disposition"] == "NEW_LIBRARY_BOUNDARY_CANDIDATE_UNRATIFIED"
    } == vacancy_refs
    assert all(row["owner_decision"] == "UNRATIFIED" for row in findings)
    dispositions = {row["finding_id"]: row["candidate_disposition"] for row in findings}
    assert dispositions["finding.bi.metric-product.v1"].startswith("SEMANTIC_METRIC_SERVICE_OWNS_")
    assert dispositions["finding.bi.reporting-product.v1"].startswith("BI_REPORTING_OWNS_")
    assert dispositions["finding.bi.embedded-product.v1"].startswith("EMBEDDED_ANALYTICS_OWNS_")
    assert dispositions["finding.bi.decision-seam.v1"] == "ANALYTICAL_PRESENTATION_AND_METRIC_FINDINGS_STOP_BEFORE_DECISION_AND_EFFECT_AUTHORITY"

    summary = built["summary"]
    assert summary["bound_libraries"] == 70
    assert summary["declared_product_libraries"] == 39
    assert summary["candidate_new_library_vacancies"] == 12
    assert summary["library_axis_decision_candidates"] == 1120
    assert summary["owner_decisions"] == summary["exact_contracts_selected"] == summary["qualified_implementations"] == summary["canonical_gaps_closed"] == 0
    assert not summary["completion_claim"]
    print("PASS BI/visualization/metrics semantic slice: 65 evidence-backed modules bind the exact 39-library product graph plus 31 justified neighbors, expose 12 typed vacancies and retain 1,120 unresolved axis decisions while metric, query, presentation, embed, notification and decision-authority seams remain explicit")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
