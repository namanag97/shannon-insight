#!/usr/bin/env python3
"""Validate privacy/security/safety coordinate ontology and exact routing."""
import hashlib,json
from build_privacy_security_safety_coordinate_ontology import HERE,build,outputs
def main():
 for n,t in outputs().items():assert (HERE/n).is_file(),f"missing {n}";assert (HERE/n).read_text()==t,f"stale {n}"
 m=json.loads((HERE/"manifest.json").read_text())
 for n,c in m["files"].items():d=(HERE/n).read_bytes();assert len(d)==c["bytes"] and hashlib.sha256(d).hexdigest()==c["sha256"]
 b=build();s=b["summary"]
 assert len(b["sources"])==len({r["source_id"] for r in b["sources"]})==17
 assert len(b["archetypes"])==len({r["archetype_id"] for r in b["archetypes"]})==60
 assert len(b["kernels"])==len({r["kernel_id"] for r in b["kernels"]})==80
 assert len(b["dockets"])==len(b["extensions"])==s["structural_family_dockets"]
 assert len(b["members"])==len({r["library_ref"] for r in b["members"]})==s["target_member_routes"] and sum(r["library_count"] for r in b["clusters"])==len(b["members"])
 assert s["routes_with_lexical_privacy_security_safety_projection"]+s["routes_with_no_privacy_security_safety_projection"]==len(b["members"])
 assert s["family_source_evidence_bindings_supplied"]==s["member_applicability_decisions"]==s["owner_decisions"]==s["canonical_gaps_closed"]==0
 assert s["privacy_profiles_supplied"]==s["security_profiles_supplied"]==s["safety_profiles_supplied"]==0 and not s["completion_claim"]
 print(f"PASS privacy/security/safety coordinate ontology: {len(b['members'])} exact members partition losslessly into {s['research_clusters']} cross-concern clusters; all evidence bindings and decisions remain open");return 0
if __name__=="__main__":raise SystemExit(main())
