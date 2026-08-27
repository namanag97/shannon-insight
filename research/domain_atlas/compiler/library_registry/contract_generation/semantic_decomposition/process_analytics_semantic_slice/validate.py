#!/usr/bin/env python3
"""Validate the evidence-backed process analytics semantic slice."""
import hashlib,json
from build_process_analytics_semantic_slice import HERE,AXES,LIBRARIES,build,outputs

def main()->int:
    for name,expected in outputs().items():
        path=HERE/name;assert path.is_file(),f"missing {name}";assert path.read_text()==expected,f"stale {name}"
    manifest=json.loads((HERE/"manifest.json").read_text())
    for name,claim in manifest["files"].items():
        data=(HERE/name).read_bytes();assert len(data)==claim["bytes"] and hashlib.sha256(data).hexdigest()==claim["sha256"]
    b=build(); source_ids={row["source_id"] for row in b["sources"]}; module_ids={row["module_id"] for row in b["modules"]}
    assert len(source_ids)==10 and len(module_ids)==10 and len(b["laws"])==18 and len(b["methods"])==20
    assert len(b["experts"])==8 and len(b["innovations"])==7 and all(not row["ai_or_llm_dependency"] for row in b["innovations"])
    assert len(b["libraries"])==len({row["library_ref"] for row in b["libraries"]})==len(LIBRARIES)==8
    assert all(set(row["semantic_module_refs"])<=module_ids and set(row["evidence_refs"])<=source_ids for row in b["libraries"])
    assert len(b["axes"])==len(LIBRARIES)*len(AXES)==128
    assert {(row["library_ref"],row["axis"]) for row in b["axes"]}=={(lib,axis) for lib in LIBRARIES for axis in AXES}
    assert all(not row["coordinate_answers"] and row["owner_decision"]=="UNRATIFIED" for row in b["axes"])
    assert all(row["compiler_binding"]=="REFUSED" for row in b["libraries"])
    s=b["summary"];assert s["owner_decisions"]==s["exact_contracts_selected"]==s["qualified_implementations"]==s["canonical_gaps_closed"]==0 and not s["completion_claim"]
    print("PASS process analytics semantic slice: evidence-backed modules and non-collapse laws bind eight exact libraries and 128 unresolved axis decisions without promoting research to authority")
    return 0
if __name__=="__main__":raise SystemExit(main())
