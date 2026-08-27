#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json
from build_matrices import HERE,build,outputs

def main()->int:
    for n,t in outputs().items():
        p=HERE/n;assert p.is_file() and p.read_text()==t,f"stale {n}"
    manifest=json.loads((HERE/"manifest.json").read_text())
    for n,c in manifest["files"].items():
        data=(HERE/n).read_bytes();assert len(data)==c["bytes"] and hashlib.sha256(data).hexdigest()==c["sha256"]
    b=build();rows=b["rows"];clusters=b["clusters"];matrices=b["matrices"]
    assert len(rows)==10784 and len(matrices)==368 and len({x["preclassification_id"] for x in rows})==10784
    assert len({(x["library_ref"],x["axis"]) for x in rows})==10784
    assert len({(x["family_id"],x["axis"]) for x in matrices})==368
    rowrefs={x["preclassification_id"] for x in rows};clusterrefs={x["cluster_id"] for x in clusters}
    member_cluster_refs=[ref for x in clusters for ref in x["member_preclassification_refs"]]
    assert len(member_cluster_refs)==len(set(member_cluster_refs))==10784 and set(member_cluster_refs)==rowrefs
    matrix_cluster_refs=[ref for x in matrices for ref in x["candidate_cluster_refs"]]
    assert len(matrix_cluster_refs)==len(set(matrix_cluster_refs))==len(clusters) and set(matrix_cluster_refs)==clusterrefs
    assert all(x["owner_decision"]=="UNRESOLVED" and "NOT_AUTHORITY" in x["status"] for x in rows)
    assert all(x["owner_decision"]=="UNRESOLVED" and "NOT_AUTHORITY" in x["status"] for x in clusters)
    assert all(x["family_default_decision"]=="UNRESOLVED" for x in matrices)
    assert b["summary"]["automatic_owner_decisions"]==b["summary"]["canonical_exact_gaps_closed"]==0
    assert len(b["waves"])==5 and sum(x["member_rows"] for x in b["waves"])==10784
    print(f"PASS semantic applicability matrices: 10,784 cells covered exactly once by 368 family matrices and {len(clusters)} conservative candidate clusters; no implicit applicability or closure")
    return 0

if __name__=="__main__":raise SystemExit(main())
