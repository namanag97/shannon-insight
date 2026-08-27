#!/usr/bin/env python3
"""Validate the signal/condition semantic slice."""
import hashlib
import json

from build_signal_condition_semantic_slice import AXES, HERE, LIBRARIES, NEIGHBORS, PRODUCT, build, outputs


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
    source_ids = {row["source_id"] for row in b["sources"]}
    module_ids = {row["module_id"] for row in b["modules"]}
    assert len(source_ids) == 38 and len(module_ids) == 43
    assert len(b["laws"]) == 50 and len(b["methods"]) == 67
    assert len(b["experts"]) == 16 and len(b["innovations"]) == 8
    assert all(not row["ai_or_llm_dependency"] for row in b["innovations"])
    assert len(LIBRARIES) == len(set(LIBRARIES)) == len(b["libraries"]) == 35
    assert len(NEIGHBORS) == 9 and NEIGHBORS <= set(LIBRARIES)
    assert {row["library_ref"] for row in b["libraries"]} == set(LIBRARIES)
    assert all(set(row["source_refs"]) <= source_ids and set(row["dependency_refs"]) <= module_ids for row in b["modules"])
    assert all(set(row["semantic_module_refs"]) <= module_ids and set(row["evidence_refs"]) <= source_ids for row in b["libraries"])
    assert len(b["axes"]) == len(LIBRARIES) * len(AXES) == 560
    assert {(row["library_ref"], row["axis"]) for row in b["axes"]} == {(lib, axis) for lib in LIBRARIES for axis in AXES}
    assert all(not row["coordinate_answers"] and row["owner_decision"] == "UNRATIFIED" for row in b["axes"])
    assert all(row["compiler_binding"] == "REFUSED" and not row["completion_claim"] for row in b["libraries"])
    assert sum(PRODUCT in row["downstream_product_refs"] for row in b["libraries"]) == 26
    assert sum(row["downstream_contract_route"].startswith("MISSING") for row in b["libraries"]) == 11
    assert all("DOWNSTREAM_CONTRACT_ROUTE_MISSING" in row["refusal_reasons"] for row in b["libraries"] if row["downstream_contract_route"].startswith("MISSING"))
    assert next(row for row in b["libraries"] if row["library_ref"] == "library.method_kernels.time_series_semantics")["downstream_product_refs"] == ["product.forecasting_workbench"]
    assert all(next(row for row in b["libraries"] if row["library_ref"] == ref)["boundary_disposition_candidate"] == "COMPOSITION_FACADE_ONLY_NO_SEMANTIC_OWNERSHIP" for ref in ("library.method_kernels.numerical_kernel_facade", "library.method_kernels.forecasting_methods"))
    assert len(b["findings"]) == 10
    assert any(row["finding_id"] == "finding.signal.quality-homonyms.v1" for row in b["findings"])
    assert any(row["finding_id"] == "finding.signal.causal-seam.v1" for row in b["findings"])
    s = b["summary"]
    assert s["declared_product_libraries"] == 26 and s["formalism_neighbor_libraries"] == 9
    assert s["libraries_without_declared_product_consumer"] == 4 and s["missing_downstream_contract_routes"] == 11
    assert s["owner_decisions"] == s["exact_contracts_selected"] == s["qualified_implementations"] == s["canonical_gaps_closed"] == 0
    assert not s["completion_claim"]
    print("PASS signal condition semantic slice: 43 evidence-backed modules bind 35 exact libraries and 560 unresolved axis decisions while measurement, signal, anomaly, change, event-history, forecast, prognosis, diagnosis, causality, quality, telemetry and action seams remain explicit")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
