#!/usr/bin/env python3
"""Validate the evidence-backed geospatial analytics semantic slice."""
import hashlib
import json

from build_geospatial_analytics_semantic_slice import AXES, HERE, LIBRARIES, build, outputs


def main() -> int:
    for name, expected in outputs().items():
        path = HERE / name
        assert path.is_file(), f"missing {name}"
        assert path.read_text() == expected, f"stale {name}"
    manifest = json.loads((HERE / "manifest.json").read_text())
    for name, claim in manifest["files"].items():
        data = (HERE / name).read_bytes()
        assert len(data) == claim["bytes"] and hashlib.sha256(data).hexdigest() == claim["sha256"]
    b = build()
    source_ids = {x["source_id"] for x in b["sources"]}
    module_ids = {x["module_id"] for x in b["modules"]}
    assert len(source_ids) == 40 and len(module_ids) == 39
    assert len(b["laws"]) == 43 and len(b["methods"]) == 51
    assert len(b["experts"]) == 16 and len(b["innovations"]) == 9
    assert all(not x["ai_or_llm_dependency"] for x in b["innovations"])
    assert len(LIBRARIES) == len(set(LIBRARIES)) == len(b["libraries"]) == 27
    assert {x["library_ref"] for x in b["libraries"]} == set(LIBRARIES)
    assert all(set(x["source_refs"]) <= source_ids for x in b["modules"])
    assert all(set(x["dependency_refs"]) <= module_ids for x in b["modules"])
    assert all(set(x["semantic_module_refs"]) <= module_ids and set(x["evidence_refs"]) <= source_ids for x in b["libraries"])
    assert len(b["axes"]) == len(LIBRARIES) * len(AXES) == 432
    assert {(x["library_ref"], x["axis"]) for x in b["axes"]} == {(lib, axis) for lib in LIBRARIES for axis in AXES}
    assert all(not x["coordinate_answers"] and x["owner_decision"] == "UNRATIFIED" for x in b["axes"])
    assert all(x["compiler_binding"] == "REFUSED" and not x["completion_claim"] for x in b["libraries"])
    workbench = [x for x in b["libraries"] if "product.geospatial_workbench" in x["downstream_product_refs"]]
    assert len(workbench) == 23
    transform = next(x for x in b["libraries"] if x["library_ref"] == "library.method_kernels.coordinate_transform_methods")
    assert transform["downstream_product_refs"] == ["product.geospatial_workbench", "product.visual_inspection_operations"]
    assert next(x for x in b["libraries"] if x["library_ref"] == "library.method_kernels.spatial_methods")["boundary_disposition_candidate"] == "COMPOSITION_FACADE_ONLY_NO_SEMANTIC_OWNERSHIP"
    assert all(next(x for x in b["libraries"] if x["library_ref"] == ref)["boundary_disposition_candidate"] == "MOVE_TO_QUERY_ENGINE_SPATIAL_ACL" for ref in ("library.qck.spatial-kernels", "library.qck.spatial-semantics"))
    assert len(b["findings"]) == 8 and any(x["finding_id"] == "finding.geospatial.product-completeness.v1" for x in b["findings"])
    s = b["summary"]
    assert s["downstream_products"] == 2 and s["libraries_without_declared_product_consumer"] == 4
    assert s["owner_decisions"] == s["exact_contracts_selected"] == s["qualified_implementations"] == s["canonical_gaps_closed"] == 0 and not s["completion_claim"]
    print("PASS geospatial analytics semantic slice: 39 evidence-backed modules bind 27 exact libraries and 432 unresolved axis decisions while feature, observation, reference, geometry, coverage, query, prediction, workflow, publication and authority seams remain explicit")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
