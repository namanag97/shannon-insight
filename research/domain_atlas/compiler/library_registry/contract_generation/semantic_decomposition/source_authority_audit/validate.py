#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json
from build_audit import HERE,build,outputs,tree_digest,REPO

def main()->int:
    for n,t in outputs().items():
        p=HERE/n;assert p.is_file() and p.read_text()==t,f"stale {n}"
    manifest=json.loads((HERE/"manifest.json").read_text())
    for n,c in manifest["files"].items():
        d=(HERE/n).read_bytes();assert len(d)==c["bytes"] and hashlib.sha256(d).hexdigest()==c["sha256"]
    b=build();audits=b["audits"];receipts={x["receipt_id"]:x for x in b["receipts"]}
    assert len(audits)==len(receipts)==23 and sum(x["library_count"] for x in audits)==674
    assert all(x["validator_receipt_ref"] in receipts and x["canonical"] is False and x["authority_decision"]=="UNRESOLVED" for x in audits)
    assert all(x["validator_result"]=="PASS" and x["status"]=="SOURCE_AUTHORITY_DECISION_REQUIRED" for x in audits)
    for x in audits:
        receipt=receipts[x["validator_receipt_ref"]];assert receipt["tree_digest_before"]==receipt["tree_digest_after"]==tree_digest(REPO/x["source_directory"])
    assert b["summary"]["validator_passes"]==23 and b["summary"]["ratified_source_authorities"]==b["summary"]["canonical_source_corpora"]==0
    print(f"PASS source-authority audit: 23 current validator receipts cover 674 libraries; {b['summary']['structurally_strong_candidates']} structurally strong candidates, authority remains unresolved")
    return 0

if __name__=="__main__":raise SystemExit(main())
