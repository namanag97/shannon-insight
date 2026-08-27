#!/usr/bin/env python3
"""Validate semantic-role coordinate ontology and exact member routing."""
import hashlib,json
from build_semantic_role_coordinate_ontology import HERE,build,outputs
def main():
 for n,t in outputs().items(): assert (HERE/n).is_file(),f"missing {n}"; assert (HERE/n).read_text()==t,f"stale {n}"
 manifest=json.loads((HERE/"manifest.json").read_text())
 for n,c in manifest["files"].items(): data=(HERE/n).read_bytes(); assert len(data)==c["bytes"]; assert hashlib.sha256(data).hexdigest()==c["sha256"]
 b=build();s=b["summary"]
 assert len(b["archetypes"])==len({r["archetype_id"] for r in b["archetypes"]})==46
 assert len(b["kernels"])==len({r["kernel_id"] for r in b["kernels"]})==54
 assert len(b["dockets"])==len(b["extensions"])==23
 assert len(b["members"])==len({r["library_ref"] for r in b["members"]})==674
 assert sum(r["library_count"] for r in b["clusters"])==674
 assert s["routes_with_lexical_discovery_projection"]==391 and s["routes_with_no_member_role_evidence"]==283
 assert s["family_source_evidence_bindings_supplied"]==s["member_applicability_decisions"]==s["owner_decisions"]==s["canonical_gaps_closed"]==0 and not s["completion_claim"]
 print(f"PASS semantic-role coordinate ontology: 674 exact members partition losslessly into {s['research_clusters']} interaction-role clusters; all evidence bindings and decisions remain open");return 0
if __name__=="__main__":raise SystemExit(main())
