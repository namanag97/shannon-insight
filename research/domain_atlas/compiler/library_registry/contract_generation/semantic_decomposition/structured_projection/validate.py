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
    library_count=len(contracts);family_count=len(b["families"]);axis_count=len({x["axis"] for x in rows})
    assert axis_count==16 and len(rows)==library_count*axis_count
    assert len({(x["library_ref"],x["axis"]) for x in rows})==library_count*axis_count
    assert len({x["library_ref"] for x in contracts})==library_count
    assert all(x["api_contract_candidate"]["types"] and x["api_contract_candidate"]["traits"] and x["api_contract_candidate"]["operations"] for x in contracts)
    assert all(x["applicability_decision"]=="UNRESOLVED" and "NOT_AUTHORITY" in x["status"] for x in rows)
    assert all(x["source_projection_is_canonical"] is False and "NOT_EXACT_CONTRACT" in x["status"] for x in contracts)
    assert sum(x["axis_rows"] for x in b["families"])==library_count*axis_count and sum(x["libraries"] for x in b["families"])==library_count
    assert b["summary"]["libraries_with_nonempty_types_traits_operations"]==library_count
    packages=b["vacancy_packages"]
    assert len(packages)==b["summary"]["targeted_evidence_work_packages"]
    assert len({x["work_package_id"] for x in packages})==len(packages)
    assert len({x["axis"] for x in packages})==b["summary"]["targeted_evidence_vacancy_axes"]
    assert sum(x["library_count"] for x in packages)==b["summary"]["generic_context_rows_requiring_targeted_evidence"]
    assert all(x["completion_effect"] and x["status"]=="TARGETED_RESEARCH_AND_OWNER_ADJUDICATION_REQUIRED" for x in packages)
    source_packages=b["source_packages"]
    assert len(source_packages)==b["summary"]["upstream_source_authority_work_packages"]==family_count
    assert sum(x["library_count"] for x in source_packages)==library_count
    assert len({x["source_path"] for x in source_packages})==family_count
    assert all(x["source_schema_currently_canonical"] is False and x["source_file_sha256"] and x["completion_effect"] for x in source_packages)
    dag=b["dag"];node_ids={x["node_id"] for x in dag["nodes"]}
    assert len(node_ids)==b["summary"]["execution_dag_nodes"]==11
    assert len(dag["edges"])==b["summary"]["execution_dag_edges"]==16
    assert all(x["from"] in node_ids and x["to"] in node_ids for x in dag["edges"])
    assert b["summary"]["canonical_upstream_sources"]==b["summary"]["automatic_applicability_decisions"]==b["summary"]["canonical_exact_gaps_closed"]==0
    print(f"PASS global structured projection: all {library_count} libraries have rich source-projected API inputs and {len(rows)} axis rows; source authority, semantic ratification and exact gaps remain open")
    return 0

if __name__=="__main__":raise SystemExit(main())
