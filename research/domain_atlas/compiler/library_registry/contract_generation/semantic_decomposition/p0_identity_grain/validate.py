#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json
from collections import Counter
from build_p0 import HERE,build,outputs

def main()->int:
    for n,t in outputs().items():
        p=HERE/n;assert p.is_file() and p.read_text()==t,f"stale {n}"
    m=json.loads((HERE/"manifest.json").read_text())
    for n,c in m["files"].items():
        d=(HERE/n).read_bytes();assert len(d)==c["bytes"] and hashlib.sha256(d).hexdigest()==c["sha256"]
    b=build();packets=b["packets"];candidates=b["candidates"];collisions=b["collisions"];symbols=b["symbol_collisions"]
    family_count=len({x["family_id"] for x in packets})
    assert len(packets)==family_count*2 and len({(x["family_id"],x["axis"]) for x in packets})==len(packets)
    assert {x["axis"] for x in packets}=={"identity_and_equality","grain_and_cardinality"}
    candidate_ids={x["candidate_id"] for x in candidates};assert len(candidate_ids)==len(candidates)
    assert all(set(x["candidate_refs"])<=candidate_ids and x["family_default_decision"]=="UNRESOLVED" for x in packets)
    assert len({x["collision_id"] for x in collisions})==len(collisions) and all(x["decision"]=="UNRESOLVED" and x["family_count"]>=2 for x in collisions)
    assert len({x["collision_id"] for x in symbols})==len(symbols)==b["summary"]["global_duplicate_symbol_ids"]
    assert all(x["library_count"]>=2 and x["decision"]=="UNRESOLVED" and x["compiler_refusal"]=="AMBIGUOUS_PUBLIC_SYMBOL_OWNER" for x in symbols)
    assert b["summary"]["duplicate_symbol_counts"]==dict(sorted(Counter(x["symbol_kind"] for x in symbols).items()))
    assert b["summary"]["families"]==family_count and b["summary"]["libraries"]==sum(x["library_count"] for x in packets if x["axis"]=="identity_and_equality")
    assert b["summary"]["automatic_owner_decisions"]==b["summary"]["canonical_exact_gaps_closed"]==0
    print(f"PASS P0 identity/grain corpus: {len(packets)} family-axis packets, {len(candidates)} bounded candidates and {len(collisions)} cross-family name collisions; no type unification or owner decision inferred")
    return 0

if __name__=="__main__":raise SystemExit(main())
