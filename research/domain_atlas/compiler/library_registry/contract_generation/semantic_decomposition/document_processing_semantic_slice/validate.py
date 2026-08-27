#!/usr/bin/env python3
"""Validate the evidence-backed document-processing semantic slice."""
import hashlib
import json

from build_document_processing_semantic_slice import AXES, HERE, LIBRARIES, NATIVE, PRODUCT, TEXT_NEIGHBOR, build, outputs


def main() -> int:
    for name, expected in outputs().items():
        path = HERE / name
        assert path.is_file(), f"missing {name}"
        assert path.read_text() == expected, f"stale {name}"
    manifest = json.loads((HERE / "manifest.json").read_text())
    for name, claim in manifest["files"].items():
        data = (HERE / name).read_bytes()
        assert len(data) == claim["bytes"]
        assert hashlib.sha256(data).hexdigest() == claim["sha256"]

    built = build()
    source_ids = {row["source_id"] for row in built["sources"]}
    module_ids = {row["module_id"] for row in built["modules"]}
    assert len(source_ids) == 40 and len(module_ids) == 38
    assert len(built["laws"]) == 47 and len(built["methods"]) == 63
    assert len(built["experts"]) == 16 and len(built["innovations"]) == 10
    assert all(not row["ai_or_llm_dependency"] for row in built["innovations"])
    assert len(LIBRARIES) == len(set(LIBRARIES)) == len(built["libraries"]) == 28
    assert set(NATIVE) <= set(LIBRARIES) and len(NATIVE) == 13 and TEXT_NEIGHBOR in LIBRARIES
    assert set(built_ref["library_ref"] for built_ref in built["libraries"]) == set(LIBRARIES)
    assert set(row["source_refs"][0].split("source.document.")[0] for row in built["modules"]) == {""}
    assert all(set(row["source_refs"]) <= source_ids for row in built["modules"])
    assert all(set(row["dependency_refs"]) <= module_ids for row in built["modules"])
    assert all(set(row["semantic_module_refs"]) <= module_ids and set(row["evidence_refs"]) <= source_ids for row in built["libraries"])

    assert len(built["axes"]) == len(LIBRARIES) * len(AXES) == 448
    assert {(row["library_ref"], row["axis"]) for row in built["axes"]} == {(lib, axis) for lib in LIBRARIES for axis in AXES}
    assert all(not row["coordinate_answers"] and row["owner_decision"] == "UNRATIFIED" for row in built["axes"])
    assert all(row["compiler_binding"] == "REFUSED" and not row["completion_claim"] for row in built["libraries"])

    product_libraries = [row for row in built["libraries"] if PRODUCT in row["downstream_product_refs"]]
    assert len(product_libraries) == 27
    text = next(row for row in built["libraries"] if row["library_ref"] == TEXT_NEIGHBOR)
    assert not text["downstream_product_refs"]
    assert text["boundary_disposition_candidate"] == "BIND_AS_SHARED_TEXT_FOUNDATION_CANDIDATE"
    assert sum(row["downstream_contract_route"] == "MISSING_P5_AND_COORDINATE_DOCKET_TYPED_VACANCY" for row in built["libraries"]) == 10
    assert all("DOWNSTREAM_CONTRACT_ROUTE_MISSING" in row["refusal_reasons"] for row in built["libraries"] if row["downstream_contract_route"].startswith("MISSING"))
    assert len(built["findings"]) == 10
    assert any(row["finding_id"] == "finding.document.search-seam.v1" for row in built["findings"])
    assert any(row["finding_id"] == "finding.document.annotation-seam.v1" for row in built["findings"])

    summary = built["summary"]
    assert summary["document_native_libraries"] == 13
    assert summary["shared_import_libraries"] == 14
    assert summary["unconsumed_shared_foundation_candidates"] == 1
    assert summary["owner_decisions"] == summary["exact_contracts_selected"] == summary["qualified_implementations"] == summary["canonical_gaps_closed"] == 0
    assert not summary["completion_claim"]
    print("PASS document processing semantic slice: 38 evidence-backed modules bind 28 exact libraries and 448 unresolved axis decisions while carrier, text, rendition, OCR, layout, extraction, review, provenance, search, annotation, release and authority seams remain explicit")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
