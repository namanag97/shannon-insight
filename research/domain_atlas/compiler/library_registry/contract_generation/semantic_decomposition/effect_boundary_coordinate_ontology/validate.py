#!/usr/bin/env python3
"""Validate effect-boundary coordinate ontology and exact member routing."""
import hashlib,json
from build_effect_boundary_coordinate_ontology import HERE,build,outputs
def main():
 for n,t in outputs().items():assert (HERE/n).is_file(),f"missing {n}";assert (HERE/n).read_text()==t,f"stale {n}"
 manifest=json.loads((HERE/"manifest.json").read_text())
 for n,c in manifest["files"].items():data=(HERE/n).read_bytes();assert len(data)==c["bytes"];assert hashlib.sha256(data).hexdigest()==c["sha256"]
 b=build();s=b["summary"]
 assert len(b["archetypes"])==len({r["archetype_id"] for r in b["archetypes"]})==42
 assert len(b["kernels"])==len({r["kernel_id"] for r in b["kernels"]})==60
 assert len(b["dockets"])==len(b["extensions"])==23
 assert len(b["members"])==len({r["library_ref"] for r in b["members"]})==674 and sum(r["library_count"] for r in b["clusters"])==674
 assert s["routes_with_explicit_source_effect_projection"]==674 and s["routes_with_no_effect_projection"]==0
 assert s["family_source_evidence_bindings_supplied"]==s["member_applicability_decisions"]==s["owner_decisions"]==s["canonical_gaps_closed"]==0 and not s["completion_claim"]
 print(f"PASS effect-boundary coordinate ontology: 674 exact members partition losslessly into {s['research_clusters']} effect-stage clusters; all evidence bindings and decisions remain open");return 0
if __name__=="__main__":raise SystemExit(main())
