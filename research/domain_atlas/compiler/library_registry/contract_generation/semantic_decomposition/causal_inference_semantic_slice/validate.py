#!/usr/bin/env python3
"""Validate the evidence-backed causal inference semantic slice."""
import hashlib
import json

from build_causal_inference_semantic_slice import AXES, HERE, LIBRARIES, build, outputs


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
    b = build()
    source_ids = {x["source_id"] for x in b["sources"]}
    module_ids = {x["module_id"] for x in b["modules"]}
    assert len(source_ids) == 30 and len(module_ids) == 36
    assert len(b["laws"]) == 42 and len(b["methods"]) == 46
    assert len(b["experts"]) == 16 and len(b["innovations"]) == 8
    assert all(not x["ai_or_llm_dependency"] for x in b["innovations"])
    assert len(b["libraries"]) == len(set(LIBRARIES)) == 16
    assert {x["library_ref"] for x in b["libraries"]} == set(LIBRARIES)
    assert all(set(x["semantic_module_refs"]) <= module_ids for x in b["libraries"])
    assert all(set(x["evidence_refs"]) <= source_ids for x in b["libraries"])
    assert len(b["axes"]) == len(LIBRARIES) * len(AXES) == 256
    assert {(x["library_ref"], x["axis"]) for x in b["axes"]} == {(lib, axis) for lib in LIBRARIES for axis in AXES}
    assert all(not x["coordinate_answers"] and x["owner_decision"] == "UNRATIFIED" for x in b["axes"])
    assert all(x["compiler_binding"] == "REFUSED" and not x["completion_claim"] for x in b["libraries"])
    predictive = next(x for x in b["libraries"] if x["library_ref"] == "library.predictive.causal_effect_learners")
    assert predictive["boundary_disposition_candidate"] == "MOVE_SEMANTIC_OWNERSHIP_TO_CAUSAL_HETEROGENEOUS_EFFECTS"
    facade = next(x for x in b["libraries"] if x["library_ref"] == "library.method_kernels.causal_methods")
    assert facade["boundary_disposition_candidate"] == "COMPOSITION_FACADE_ONLY_NO_SEMANTIC_OWNERSHIP"
    consumed = [x for x in b["libraries"] if x["downstream_product_refs"]]
    assert len(consumed) == 11 and {p for x in consumed for p in x["downstream_product_refs"]} == {"product.experimentation_platform"}
    assert len(b["findings"]) == 8
    assert any(x["finding_id"] == "finding.causal.causal-toolkit-not-yet-product.v1" for x in b["findings"])
    assert any(x["finding_id"] == "finding.causal.root-cause-acl.v1" for x in b["findings"])
    s = b["summary"]
    assert s["libraries_without_declared_product_consumer"] == 5
    assert s["owner_decisions"] == s["exact_contracts_selected"] == s["qualified_implementations"] == s["canonical_gaps_closed"] == 0
    assert not s["completion_claim"]
    print("PASS causal inference semantic slice: 36 evidence-backed modules bind 16 exact libraries and 256 unresolved axis decisions while experiment, identification, estimation, sensitivity, diagnosis, prediction and decision seams remain explicit")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
