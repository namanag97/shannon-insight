#!/usr/bin/env python3
"""Validate the evidence-backed operations research semantic slice."""
import hashlib
import json
from build_operations_research_semantic_slice import HERE, AXES, LIBRARIES, build, outputs


def main() -> int:
    for name, expected in outputs().items():
        path=HERE/name
        assert path.is_file(), f"missing {name}"
        assert path.read_text()==expected, f"stale {name}"
    manifest=json.loads((HERE/"manifest.json").read_text())
    for name, claim in manifest["files"].items():
        data=(HERE/name).read_bytes()
        assert len(data)==claim["bytes"] and hashlib.sha256(data).hexdigest()==claim["sha256"]
    b=build(); source_ids={x["source_id"] for x in b["sources"]}; module_ids={x["module_id"] for x in b["modules"]}
    assert len(source_ids)==17 and len(module_ids)==24 and len(b["laws"])==26 and len(b["methods"])==35
    assert len(b["experts"])==12 and len(b["innovations"])==7 and all(not x["ai_or_llm_dependency"] for x in b["innovations"])
    assert len(b["libraries"])==len({x["library_ref"] for x in b["libraries"]})==len(LIBRARIES)==22
    assert all(set(x["semantic_module_refs"])<=module_ids and set(x["evidence_refs"])<=source_ids for x in b["libraries"])
    assert len(b["axes"])==len(LIBRARIES)*len(AXES)==352
    assert {(x["library_ref"],x["axis"]) for x in b["axes"]}=={(lib,axis) for lib in LIBRARIES for axis in AXES}
    assert all(not x["coordinate_answers"] and x["owner_decision"]=="UNRATIFIED" for x in b["axes"])
    assert all(x["compiler_binding"]=="REFUSED" for x in b["libraries"])
    assert len(b["findings"])==5 and any(x["finding_id"].endswith("queue-capability-boundary.v1") for x in b["findings"])
    assert {p for x in b["libraries"] for p in x["downstream_product_refs"]}=={"product.optimization_solver","product.simulation_environment"}
    s=b["summary"]
    assert s["libraries_without_declared_product_consumer"]==7
    assert s["owner_decisions"]==s["exact_contracts_selected"]==s["qualified_implementations"]==s["canonical_gaps_closed"]==0 and not s["completion_claim"]
    print("PASS operations research semantic slice: 24 evidence-backed modules bind 22 exact libraries and 352 unresolved axis decisions while optimization, queueing and simulation boundaries remain explicit")
    return 0


if __name__=="__main__": raise SystemExit(main())
