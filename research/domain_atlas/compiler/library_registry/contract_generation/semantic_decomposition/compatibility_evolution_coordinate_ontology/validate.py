#!/usr/bin/env python3
"""Validate compatibility/evolution coordinate ontology and exact routing."""
import hashlib,json
from build_compatibility_evolution_coordinate_ontology import HERE,build,outputs
def main():
 for n,t in outputs().items():assert (HERE/n).is_file(),f"missing {n}";assert (HERE/n).read_text()==t,f"stale {n}"
 m=json.loads((HERE/"manifest.json").read_text())
 for n,c in m["files"].items():d=(HERE/n).read_bytes();assert len(d)==c["bytes"] and hashlib.sha256(d).hexdigest()==c["sha256"]
 b=build();s=b["summary"]
 assert len(b["sources"])==len({r["source_id"] for r in b["sources"]})==14
 assert len(b["archetypes"])==len({r["archetype_id"] for r in b["archetypes"]})==50
 assert len(b["kernels"])==len({r["kernel_id"] for r in b["kernels"]})==72
 assert len(b["dockets"])==len(b["extensions"])==23
 assert len(b["members"])==len({r["library_ref"] for r in b["members"]})==674 and sum(r["library_count"] for r in b["clusters"])==674
 assert s["routes_with_lexical_evolution_projection"]==61 and s["routes_with_no_evolution_projection"]==613
 assert s["family_source_evidence_bindings_supplied"]==s["member_applicability_decisions"]==s["owner_decisions"]==s["canonical_gaps_closed"]==0 and not s["completion_claim"]
 print(f"PASS compatibility/evolution coordinate ontology: 674 exact members partition losslessly into {s['research_clusters']} directional-change clusters; all evidence bindings and decisions remain open");return 0
if __name__=="__main__":raise SystemExit(main())
