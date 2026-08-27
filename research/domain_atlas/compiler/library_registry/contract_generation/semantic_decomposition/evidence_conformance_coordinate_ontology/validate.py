#!/usr/bin/env python3
"""Validate evidence/conformance coordinate ontology and exact member routing."""
import hashlib,json
from build_evidence_conformance_coordinate_ontology import HERE,build,outputs
def main():
 for n,t in outputs().items():assert (HERE/n).is_file(),f"missing {n}";assert (HERE/n).read_text()==t,f"stale {n}"
 manifest=json.loads((HERE/"manifest.json").read_text())
 for n,c in manifest["files"].items():data=(HERE/n).read_bytes();assert len(data)==c["bytes"];assert hashlib.sha256(data).hexdigest()==c["sha256"]
 b=build();s=b["summary"]
 assert len(b["archetypes"])==len({r["archetype_id"] for r in b["archetypes"]})==44
 assert len(b["kernels"])==len({r["kernel_id"] for r in b["kernels"]})==59
 assert len(b["dockets"])==len(b["extensions"])==s["structural_family_dockets"]
 assert len(b["members"])==len({r["library_ref"] for r in b["members"]})==s["target_member_routes"] and sum(r["library_count"] for r in b["clusters"])==len(b["members"])
 assert s["routes_with_lexical_discovery_projection"]+s["routes_with_no_member_evidence_signal"]==len(b["members"])
 assert s["family_source_evidence_bindings_supplied"]==s["member_applicability_decisions"]==s["owner_decisions"]==s["canonical_gaps_closed"]==0 and not s["completion_claim"]
 print(f"PASS evidence/conformance coordinate ontology: {len(b['members'])} exact members partition losslessly into {s['research_clusters']} proof-scope clusters; all evidence bindings and decisions remain open");return 0
if __name__=="__main__":raise SystemExit(main())
