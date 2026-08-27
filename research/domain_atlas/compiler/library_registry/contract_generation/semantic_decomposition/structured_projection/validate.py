#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json
from build_projection import HERE,build,outputs

def main()->int:
    for n,t in outputs().items():
        p=HERE/n;assert p.is_file() and p.read_text()==t,f"stale {n}"
    manifest=json.loads((HERE/"manifest.json").read_text())
    for n,c in manifest["files"].items():
        data=(HERE/n).read_bytes();assert len(data)==c["bytes"] and hashlib.sha256(data).hexdigest()==c["sha256"]
    b=build();rows=b["rows"];contracts=b["contracts"]
    assert len(rows)==674*16 and len(contracts)==674 and len(b["families"])==23
    assert len({(x["library_ref"],x["axis"]) for x in rows})==674*16
    assert len({x["library_ref"] for x in contracts})==674
    assert all(x["api_contract_candidate"]["types"] and x["api_contract_candidate"]["traits"] and x["api_contract_candidate"]["operations"] for x in contracts)
    assert all(x["applicability_decision"]=="UNRESOLVED" and "NOT_AUTHORITY" in x["status"] for x in rows)
    assert all(x["source_projection_is_canonical"] is False and "NOT_EXACT_CONTRACT" in x["status"] for x in contracts)
    assert sum(x["axis_rows"] for x in b["families"])==674*16 and sum(x["libraries"] for x in b["families"])==674
    assert b["summary"]["libraries_with_nonempty_types_traits_operations"]==674
    packages=b["vacancy_packages"]
    assert len(packages)==b["summary"]["targeted_evidence_work_packages"]==103
    assert len({x["axis"] for x in packages})==b["summary"]["targeted_evidence_vacancy_axes"]==6
    assert sum(x["library_count"] for x in packages)==b["summary"]["generic_context_rows_requiring_targeted_evidence"]==2805
    assert all(x["completion_effect"] and x["status"]=="TARGETED_RESEARCH_AND_OWNER_ADJUDICATION_REQUIRED" for x in packages)
    source_packages=b["source_packages"]
    assert len(source_packages)==b["summary"]["upstream_source_authority_work_packages"]==23
    assert sum(x["library_count"] for x in source_packages)==674
    assert len({x["source_path"] for x in source_packages})==23
    assert all(x["source_schema_currently_canonical"] is False and x["source_file_sha256"] and x["completion_effect"] for x in source_packages)
    dag=b["dag"];node_ids={x["node_id"] for x in dag["nodes"]}
    assert len(node_ids)==b["summary"]["execution_dag_nodes"]==11
    assert len(dag["edges"])==b["summary"]["execution_dag_edges"]==16
    assert all(x["from"] in node_ids and x["to"] in node_ids for x in dag["edges"])
    assert b["summary"]["canonical_upstream_sources"]==b["summary"]["automatic_applicability_decisions"]==b["summary"]["canonical_exact_gaps_closed"]==0
    print("PASS global structured projection: all 674 libraries have rich source-projected API inputs and 10,784 axis rows; source authority, semantic ratification and exact gaps remain open")
    return 0

if __name__=="__main__":raise SystemExit(main())
