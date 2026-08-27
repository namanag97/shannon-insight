#!/usr/bin/env python3
"""Validate the graph, network, ontology and knowledge semantic slice."""
import hashlib
import json

from build_graph_network_knowledge_semantic_slice import (
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
        assert len(data) == claim["bytes"] and hashlib.sha256(data).hexdigest() == claim["sha256"]

    built = build()
    source_ids = {row["source_id"] for row in built["sources"]}
    module_ids = {row["module_id"] for row in built["modules"]}
    assert len(source_ids) == len(built["sources"]) == 27
    assert len(module_ids) == len(built["modules"]) == 49
    assert all(row["primary_or_official"] and row["supported_claim"] and row["authority_limit"] for row in built["sources"])
    assert all(set(row["source_refs"]) <= source_ids for row in built["modules"])
    assert all(set(row["dependency_refs"]) <= module_ids for row in built["modules"])
    assert_acyclic(built["modules"])

    frontier = next(row for row in load_jsonl(HERE.parent / "analytical_formalism_frontier/formalism-frontier-clusters.jsonl") if row["cluster_id"] == "formalism.graph_network_knowledge")
    direct = declared_product_libraries()
    assert set(frontier["declared_concrete_library_refs"]) == direct
    assert set(frontier["product_refs"]) == PRODUCTS
    assert len(direct) == 11 and len(NEIGHBORS) == 23 and len(LIBRARIES) == 34
    assert not (direct & NEIGHBORS)
    assert set(LIBRARIES) == direct | NEIGHBORS
    assert direct == {
        "library.ontology_model.axiom_profile", "library.ontology_model.identity_import_closure",
        "library.ontology_model.knowledge_graph_release", "library.ontology_model.ontology_mapping",
        "library.ontology_model.reasoning_entailment", "library.ontology_model.shape_validation",
        "library.method_kernels.graph_semantics", "library.method_kernels.graph_traversal_path_methods",
        "library.method_kernels.graph_centrality_methods", "library.method_kernels.graph_community_methods",
        "library.method_kernels.graph_semiring_kernel_facade",
    }

    assert len({row["law_id"] for row in built["laws"]}) == len(built["laws"]) == 36
    assert len({row["method_type_id"] for row in built["methods"]}) == len(built["methods"]) == 108
    assert len({row["expert_id"] for row in built["experts"]}) == len(built["experts"]) == 20
    assert len({row["innovation_id"] for row in built["innovations"]}) == len(built["innovations"]) == 10
    assert all(set(row["source_refs"]) <= source_ids for row in built["methods"] + built["experts"] + built["innovations"])
    assert all(row["authority_limit"] for row in built["experts"])
    assert all(not row["ai_or_llm_dependency"] for row in built["innovations"])

    bindings = built["libraries"]
    assert len(bindings) == len(LIBRARIES) == 34
    assert {row["library_ref"] for row in bindings} == set(LIBRARIES)
    assert all(row["semantic_module_refs"] and set(row["semantic_module_refs"]) <= module_ids for row in bindings)
    assert all(set(row["evidence_refs"]) <= source_ids for row in bindings)
    assert all(row["compiler_binding"] == "REFUSED" and not row["completion_claim"] for row in bindings)
    assert all("OWNER_RATIFICATION_MISSING" in row["refusal_reasons"] for row in bindings)
    assert all(set(row["downstream_product_refs"]) & PRODUCTS for row in bindings if row["library_ref"] in direct)
    assert sum(row["downstream_contract_route"].startswith("MISSING") for row in bindings) == 10

    axis_rows = built["axes"]
    assert len(axis_rows) == len(LIBRARIES) * len(AXES) == 544
    assert len({(row["library_ref"], row["axis"]) for row in axis_rows}) == len(axis_rows)
    assert all(row["semantic_module_refs"] and set(row["semantic_module_refs"]) <= module_ids for row in axis_rows)
    assert all(set(row["evidence_refs"]) <= source_ids for row in axis_rows)
    assert all(not row["coordinate_answers"] and row["owner_decision"] == "UNRATIFIED" for row in axis_rows)
    assert all(row["canonical_gaps_closed"] == 0 and not row["completion_claim"] for row in axis_rows)

    vacancy_refs = {ref for ref, _ in VACANCIES}
    findings = built["findings"]
    assert len(vacancy_refs) == len(VACANCIES) == 11
    assert vacancy_refs.isdisjoint(LIBRARIES)
    assert {row.get("proposed_library_ref") for row in findings if row["candidate_disposition"] == "NEW_LIBRARY_BOUNDARY_CANDIDATE_UNRATIFIED"} == vacancy_refs
    assert all(row["owner_decision"] == "UNRATIFIED" for row in findings)
    analysis_product = next(row for row in findings if row["finding_id"] == "finding.graph.analysis-product-boundary.v1")
    assert analysis_product["current_product_refs"] == ["product.graph_analysis_workbench"]
    assert analysis_product["candidate_disposition"] == "RETAIN_GRAPH_ANALYSIS_WORKBENCH_WITH_METHOD_IMPORTS_AND_EXPLICIT_OWNER_SEAMS"
    assert set(analysis_product["library_refs"]) == {
        "library.method_kernels.graph_semantics",
        "library.method_kernels.graph_traversal_path_methods", "library.method_kernels.graph_centrality_methods",
        "library.method_kernels.graph_community_methods", "library.method_kernels.graph_semiring_kernel_facade",
    }
    assert analysis_product["excluded_library_refs"] == ["library.method_kernels.graph_methods"]
    ontology = next(row for row in findings if row["finding_id"] == "finding.graph.ontology-product.v1")
    assert ontology["candidate_disposition"] == "RETAIN_ONTOLOGY_KNOWLEDGE_MODEL_GOVERNANCE_PRODUCT_WITH_SIX_DECLARED_LIBRARIES"

    context = built["context"]
    assert context["product_boundary_candidates"] == [
        {"product_ref": "product.ontology_knowledge_model", "status": "RETAIN_UNRATIFIED"},
        {"product_ref": "product.graph_analysis_workbench", "status": "RETAIN_SEPARATE_WORKBENCH_UNRATIFIED"},
    ]
    summary = built["summary"]
    assert summary["bound_libraries"] == 34 and summary["declared_product_libraries"] == 11
    assert summary["candidate_new_products"] == 0 and summary["candidate_new_library_vacancies"] == 11
    assert summary["library_axis_decision_candidates"] == 544
    assert summary["owner_decisions"] == summary["exact_contracts_selected"] == summary["qualified_implementations"] == summary["canonical_gaps_closed"] == 0
    assert not summary["completion_claim"]
    print("PASS graph/network/knowledge semantic slice: 49 evidence-backed modules bind the exact 11-library union of the ontology and graph-workbench products plus 23 justified neighbors, preserve the method/product seam and 11 library vacancies, and retain 544 unresolved axis decisions while graph, query/storage, ontology, prediction, specialized-domain and authority seams remain explicit")
    return 0


if __name__ == "__main__": raise SystemExit(main())
