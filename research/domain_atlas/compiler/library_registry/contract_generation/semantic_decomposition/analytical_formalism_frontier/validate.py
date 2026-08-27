#!/usr/bin/env python3
"""Validate the retained-product analytical-formalism frontier."""
import hashlib
import json

from build_frontier import CLUSTERS, DEPENDENCIES, HERE, build, outputs, product_refs, slice_universes


def main() -> int:
    for name, expected in outputs().items():
        path = HERE / name
        assert path.is_file(), f"missing {name}"
        assert path.read_text() == expected, f"stale {name}"
    manifest = json.loads((HERE / "manifest.json").read_text())
    for name, claim in manifest["files"].items():
        data = (HERE / name).read_bytes()
        assert len(data) == claim["bytes"] and hashlib.sha256(data).hexdigest() == claim["sha256"]
    built = build()
    retained = product_refs()
    slices = slice_universes()
    assert len(retained) == len(built["products"])
    assert {row["product_ref"] for row in built["products"]} == retained
    assert len(slices) == 19 and len(built["clusters"]) == len(CLUSTERS) == 19
    assert len({row["cluster_id"] for row in built["clusters"]}) == 19
    assert len(built["dependencies"]) == len(DEPENDENCIES) == 25
    assert len({row["dependency_ref"] for row in built["dependencies"]}) == len(built["dependencies"])
    cluster_refs = {row["cluster_id"] for row in built["clusters"]}
    assert all(row["prerequisite_cluster_ref"] in cluster_refs and row["consumer_cluster_ref"] in cluster_refs for row in built["dependencies"])
    assert all(row["dependency_kind"] in {"MANDATORY_SEMANTIC_FOUNDATION", "CONDITIONAL_METHOD_IMPORT"} for row in built["dependencies"])
    assert all(row["research_status"] == "CANDIDATE_UNRATIFIED" and row["canonical_gaps_closed"] == 0 and not row["completion_claim"] for row in built["dependencies"])
    assert all(set(row["covered_concrete_library_refs"]) <= set(row["concrete_library_refs"]) for row in built["products"])
    assert all(set(row["covered_concrete_library_refs"]) | set(row["uncovered_concrete_library_refs"]) == set(row["concrete_library_refs"]) for row in built["products"])
    assert all(not (set(row["covered_concrete_library_refs"]) & set(row["uncovered_concrete_library_refs"])) for row in built["products"])
    assert all(row["compiler_binding"] == "REFUSED" and not row["completion_claim"] for row in built["products"])
    assert all(set(row["product_refs"]) <= retained and row["canonical_gaps_closed"] == 0 and not row["completion_claim"] for row in built["clusters"])
    assert all(set(row["mandatory_prerequisite_cluster_refs"]) <= cluster_refs for row in built["clusters"])
    assert all(set(row["conditional_import_cluster_refs"]) <= cluster_refs for row in built["clusters"])
    assert all(set(row["mandatory_dependent_cluster_refs"]) <= cluster_refs for row in built["clusters"])
    assert all(set(row["conditional_dependent_cluster_refs"]) <= cluster_refs for row in built["clusters"])
    assert all(set(row["dependent_cluster_refs"]) <= cluster_refs for row in built["clusters"])
    assert all(row["foundation_fanout"] == len(row["dependent_cluster_refs"]) for row in built["clusters"])
    assert all(set(row["mandatory_dependent_cluster_refs"]) | set(row["conditional_dependent_cluster_refs"]) == set(row["dependent_cluster_refs"]) for row in built["clusters"])
    assert all(not (set(row["mandatory_dependent_cluster_refs"]) & set(row["conditional_dependent_cluster_refs"])) for row in built["clusters"])
    assert all(row["mandatory_research_wave"] >= 0 for row in built["clusters"])
    for row in built["clusters"]:
        if row["semantic_slice_package"]:
            assert row["semantic_slice_package"] in slices
            assert row["research_status"] == "SLICE_ENCODED_UNRATIFIED"
        else:
            assert row["research_status"].startswith("OPEN_")
    summary = built["summary"]
    assert summary["live_semantic_slices"] == 19
    assert summary["slice_library_union"] == 527
    assert summary["encoded_unratified_clusters"] == 19
    assert summary["open_high_priority_clusters"] == 0 and summary["open_medium_priority_clusters"] == 0
    assert summary["formalism_dependency_candidates"] == 25
    assert summary["mandatory_semantic_foundations"] == 10
    assert summary["conditional_method_imports"] == 15
    assert summary["highest_foundation_fanout_cluster_refs"] == ["formalism.general_statistical_inference"]
    clustered_products = {ref for row in built["clusters"] for ref in row["product_refs"]}
    assert summary["products_represented_in_formalism_clusters"] == len(clustered_products)
    assert summary["products_not_yet_assigned_to_formalism_cluster"] == sorted(retained - clustered_products)
    assert summary["products_with_full_structural_slice_overlap"] == sum(
        bool(row["concrete_library_refs"]) and not row["uncovered_concrete_library_refs"]
        for row in built["products"]
    )
    assert summary["products_with_zero_structural_slice_overlap"] == sum(
        not row["covered_concrete_library_refs"] for row in built["products"]
    )
    assert summary["owner_decisions"] == summary["canonical_gaps_closed"] == 0 and not summary["completion_claim"]
    print(
        f"PASS analytical formalism frontier: all {len(retained)} retained products project "
        f"losslessly against {len(slices)} unratified slices, {len(built['clusters'])} formalism "
        f"clusters and {len(built['dependencies'])} typed prerequisite candidates; graph methods "
        "remain distinct from the Graph Analysis Workbench and all analytical-formalism quotients "
        "are encoded; 0 open research quotients remain"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
