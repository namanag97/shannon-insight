#!/usr/bin/env python3
"""Validate product, capability, solution-pack and vertical coordinate projections."""
import hashlib
import json

from build_product_coordinate_binding_projection import HERE, build, outputs


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
    summary = built["summary"]
    assert len(built["subjects"]) == len({row["subject_ref"] for row in built["subjects"]}) == summary["qualification_subjects"]
    assert sum(row["concrete_reference_count"] for row in built["subjects"]) == summary["subject_concrete_reference_edges"]
    all_edges = [edge for row in built["subjects"] for edge in row["concrete_bindings"]]
    unique_refs = {edge["concrete_library_ref"] for edge in all_edges}
    canonical_refs = {edge["concrete_library_ref"] for edge in all_edges if edge["coordinate_binding_docket_ref"]}
    noncanonical_refs = unique_refs - canonical_refs
    assert summary["unique_concrete_references"] == len(unique_refs)
    assert summary["canonical_coordinate_bound_unique_references"] == len(canonical_refs)
    assert summary["noncanonical_resolved_unique_references"] == len(noncanonical_refs)
    assert canonical_refs.isdisjoint(noncanonical_refs) and canonical_refs | noncanonical_refs == unique_refs
    assert len(built["products"]) == len({row["product_ref"] for row in built["products"]}) == summary["retained_products"]
    assert len(built["capabilities"]) == summary["capability_import_obligations"]
    retained_imports = sum(row["retained_product_ref"] is not None for row in built["capabilities"])
    unretained_imports = len(built["capabilities"]) - retained_imports
    assert summary["capability_imports_targeting_retained_products"] == retained_imports
    assert summary["capability_imports_targeting_unretained_candidates"] == unretained_imports
    assert sum(row["boundary_migration_docket_ref"] is not None for row in built["capabilities"]) == unretained_imports
    assert len(built["packs"]) == summary["industry_solution_packs"]
    assert len(built["verticals"]) == summary["vertical_compositions"]
    assert len(built["gates"]) == summary["compiler_assembly_gates"] == len(built["products"]) + len(built["packs"]) + len(built["verticals"])
    assert all(row["compiler_binding"] == "REFUSED" for row in built["subjects"])
    assert all(row["compiler_assembly"] == "REFUSED" for row in built["products"] + built["packs"] + built["verticals"])
    assert all(row["compiler_action"] == "REFUSE_CAPABILITY_IMPORT" for row in built["capabilities"])
    assert all(row["verdict"] == "REFUSE_ASSEMBLY" for row in built["gates"])
    assert summary["compiler_assemblies_permitted"] == summary["semantic_authority_receipts"] == summary["qualification_receipts"] == summary["vertical_acceptance_receipts"] == summary["canonical_gaps_closed"] == 0
    assert not summary["completion_claim"]
    print(
        f"PASS product coordinate binding projection: {len(built['subjects'])} explicit subjects "
        f"and all {len(built['products'])} retained product, {len(built['packs'])} pack and "
        f"{len(built['verticals'])} vertical assemblies remain fail-closed; no name joins or "
        "semantic gates bypassed"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
