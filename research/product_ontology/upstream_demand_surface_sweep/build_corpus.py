#!/usr/bin/env python3
import hashlib, json
from pathlib import Path
from source_model import SOURCES, DEMAND_SURFACES, UNIVERSAL_LAWS, BOUNDARY_HYPOTHESES, CONTRACTS, VERTICAL_PACKS

HERE = Path(__file__).resolve().parent
def write(name, rows):
    path=HERE/name
    path.write_text(''.join(json.dumps(r,sort_keys=True)+'\n' for r in sorted(rows,key=lambda x:next(v for k,v in x.items() if k.endswith('_id')))))
    return {"path":name,"records":len(rows),"sha256":hashlib.sha256(path.read_bytes()).hexdigest()}

def main():
    evidence=[{"source_id":i,"title":t,"authority":a,"url":u,"bounded_claim":c,"status":"PRIMARY_OR_OFFICIAL_SOURCE","completion_claim":False} for i,t,a,u,c in SOURCES]
    surfaces=[{"surface_id":"demand-surface."+i,"name":i,"required_artifact_classes":a,"scope":"EVERY_INDUSTRY_AND_SUBINDUSTRY","status":"REQUIRED_COVERAGE_DETECTOR","completion_claim":False} for i,a in DEMAND_SURFACES]
    laws=[{"law_id":"law.upstream."+i,"statement":s,"source_refs":refs,"status":"EVIDENCE_BACKED_GLOBAL_NON_COLLAPSE_CANDIDATE","completion_claim":False} for i,s,refs in UNIVERSAL_LAWS]
    boundaries=[{"hypothesis_id":"boundary.upstream."+i,"name":n,"disposition":d,"bounded_rationale":r,"source_refs":refs,"status":"PROPOSED_UNRATIFIED","completion_claim":False} for i,n,d,r,refs in BOUNDARY_HYPOTHESES]
    contracts=[{"contract_hypothesis_id":"contract.upstream."+i,"semantic_name":i,"kind":"PURE_COMPOSABLE_CONTRACT","decisions_exposed_required":True,"effect_authority_forbidden_by_default":True,"status":"UNRATIFIED_LIBRARY_BOUNDARY","completion_claim":False} for i in CONTRACTS]
    packs=[{"pack_id":"vertical-pack.upstream."+i,"vertical":i,"required_distinct_artifacts":a,"status":"VERTICAL_COVERAGE_DELTA","completion_claim":False} for i,a in VERTICAL_PACKS]
    files=[write("evidence.jsonl",evidence),write("demand-surfaces.jsonl",surfaces),write("universal-laws.jsonl",laws),write("boundary-hypotheses.jsonl",boundaries),write("library-contract-hypotheses.jsonl",contracts),write("vertical-pack-requirements.jsonl",packs)]
    summary={"sources":len(evidence),"demand_surfaces":len(surfaces),"universal_laws":len(laws),"boundary_hypotheses":len(boundaries),"library_contract_hypotheses":len(contracts),"vertical_pack_deltas":len(packs),"promote_strong":sum(r[2].startswith("PROMOTE_STRONG") for r in BOUNDARY_HYPOTHESES),"promote_presumptive":sum("PROMOTE_PRESUMPTIVE" in r[2] for r in BOUNDARY_HYPOTHESES),"canonical_mutations":0,"completion_claim":False}
    (HERE/"summary.json").write_text(json.dumps(summary,indent=2,sort_keys=True)+'\n')
    (HERE/"manifest.json").write_text(json.dumps({"files":files,"summary":summary},indent=2,sort_keys=True)+'\n')
    print(json.dumps(summary,indent=2,sort_keys=True))
if __name__=='__main__': main()
