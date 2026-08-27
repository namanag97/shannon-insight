#!/usr/bin/env python3
"""Validate the semantic-object coordinate ontology and exact member rebase."""
import hashlib
import json
from build_semantic_object_coordinate_ontology import HERE, build, outputs


def main() -> int:
    expected=outputs()
    for n,t in expected.items():
        assert (HERE/n).is_file(), f"missing {n}"
        assert (HERE/n).read_text()==t, f"stale {n}"
    manifest=json.loads((HERE/"manifest.json").read_text())
    for n,c in manifest["files"].items():
        data=(HERE/n).read_bytes(); assert len(data)==c["bytes"]; assert hashlib.sha256(data).hexdigest()==c["sha256"]
    b=build(); s=b["summary"]
    assert len(b["archetypes"])==len({r["archetype_id"] for r in b["archetypes"]})==33
    assert len(b["kernels"])==len({r["kernel_id"] for r in b["kernels"]})==55
    assert len(b["dockets"])==len(b["extensions"])==23
    assert len(b["members"])==len({r["library_ref"] for r in b["members"]})==674
    assert sum(r["library_count"] for r in b["clusters"])==674
    assert s["routes_with_lexical_discovery_projection"]==312 and s["routes_with_no_member_subject_kind_evidence"]==362
    assert s["family_source_evidence_bindings_supplied"]==s["member_applicability_decisions"]==s["owner_decisions"]==s["canonical_gaps_closed"]==0
    assert not s["completion_claim"] and all(not r["completion_claim"] for r in b["members"])
    print(f"PASS semantic-object coordinate ontology: 674 exact members partition losslessly into {s['research_clusters']} subject-kind clusters; all evidence bindings and decisions remain open")
    return 0


if __name__ == "__main__": raise SystemExit(main())
