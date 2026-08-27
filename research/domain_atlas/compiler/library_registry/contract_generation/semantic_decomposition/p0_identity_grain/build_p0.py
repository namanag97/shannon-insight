#!/usr/bin/env python3
"""Mine P0 identity/equality and grain/cardinality candidates from all rich API inputs."""

from __future__ import annotations
import argparse,collections,hashlib,json,re
from pathlib import Path
from typing import Any

HERE=Path(__file__).resolve().parent
SEMANTIC=HERE.parent
INPUTS=SEMANTIC/"structured_projection/exact-contract-input-candidates.jsonl"
EVIDENCE=SEMANTIC/"structured_projection/structured-axis-evidence.jsonl"
WORK=SEMANTIC/"structured_projection/targeted-evidence-work-packages.jsonl"
AS_OF="2026-08-26"

def canonical(v:Any)->str:return json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(",",":"))
def load_jsonl(p:Path)->list[dict[str,Any]]:return [json.loads(x) for x in p.read_text().splitlines() if x.strip()]
def slug(s:str)->str:return s.replace("constitution.family.","").replace("library.","").replace(".","-").replace("_","-")

IDENTITY_SUFFIX={"Identity":"identity carrier candidate","Identifier":"identifier candidate","Id":"opaque identifier candidate","Key":"key candidate","Ref":"reference candidate","Digest":"content/representation digest candidate","Fingerprint":"fingerprint candidate","Canonical":"canonical representation candidate","Equivalence":"equivalence relation candidate","Version":"version-continuity candidate","Edition":"edition identity candidate","Occurrence":"occurrence identity candidate","Handle":"opaque handle candidate","Token":"token/capability candidate"}
GRAIN_SUFFIX={"Record":"record grain candidate","Row":"row grain candidate","Item":"item grain candidate","Element":"element grain candidate","Event":"event grain candidate","Observation":"observation grain candidate","Batch":"batch grain candidate","Window":"window grain candidate","Partition":"partition grain candidate","Group":"group grain candidate","Entity":"entity grain candidate","Collection":"collection grain candidate","Dataset":"dataset grain candidate","Table":"table grain candidate","Stream":"stream grain candidate","Graph":"graph grain candidate","Node":"node grain candidate","Edge":"edge grain candidate","Tile":"tile grain candidate","Feature":"feature grain candidate","Sample":"sample grain candidate","Population":"population grain candidate","Page":"page grain candidate","Frame":"frame grain candidate","Message":"message grain candidate","Document":"document grain candidate","Artifact":"artifact grain candidate","Result":"result grain candidate","Plan":"plan grain candidate","Receipt":"receipt grain candidate"}
OP_PATTERNS={"identity_and_equality":re.compile(r"(?:compare|equal|equiv|canonical|resolve|identify|match|dedup|digest|fingerprint)",re.I),"grain_and_cardinality":re.compile(r"(?:group|aggregate|partition|window|batch|page|explode|join|regrain|rollup|drill|sample|collect|split|merge)",re.I)}

def suffix_match(name:str,mapping:dict[str,str])->tuple[str,str]|None:
    for suffix,role in sorted(mapping.items(),key=lambda x:-len(x[0])):
        if name.endswith(suffix):return suffix,role
    return None

def build()->dict[str,Any]:
    inputs=load_jsonl(INPUTS);evidence=load_jsonl(EVIDENCE);work=load_jsonl(WORK)
    bindings={x["axis"]:x for x in json.loads((SEMANTIC/"constitution-coverage.json").read_text())["axis_bindings"]}
    candidates=[];type_occurrences:dict[str,list[dict[str,Any]]]=collections.defaultdict(list)
    for contract in inputs:
        for t in contract["api_contract_candidate"]["types"]:
            type_occurrences[t["name"]].append({"family_id":contract["family_id"],"library_ref":contract["library_ref"],"type_id":t["type_id"],"type_origin":t.get("origin"),"type_role":t.get("role")})
            for axis,mapping in (("identity_and_equality",IDENTITY_SUFFIX),("grain_and_cardinality",GRAIN_SUFFIX)):
                match=suffix_match(t["name"],mapping)
                if match:
                    suffix,role=match;candidates.append({"record_kind":"p0_semantic_type_candidate","candidate_id":f"candidate.p0.{axis.replace('_','-')}.{slug(contract['library_ref'])}.{slug(t['name'])}","edition":1,"axis":axis,"family_id":contract["family_id"],"library_ref":contract["library_ref"],"type_id":t["type_id"],"type_name":t["name"],"source_origin":t.get("origin"),"source_role":t.get("role"),"lexical_signal":suffix,"candidate_role":role,"owner_decision":"UNRESOLVED","required_coordinates":["owned subject and meaning","identity/equality relation and scope","grain/cardinality and boundedness","time/version scope","authority and evidence","non-collapse and refusal cases"] if axis=="identity_and_equality" else ["observation/identity/analysis/update grains","cardinality and collection kind","partition/window/cut","legal regrain operations","loss/residual and evidence","non-collapse and refusal cases"],"authority_limit":"Public type naming is a candidate routing signal only. Suffixes such as Id, Ref, Key, Record or Result do not establish semantic identity, equality, grain or shared ownership.","status":"P0_CANDIDATE_NOT_AUTHORITY"})
        for op in contract["api_contract_candidate"]["operations"]:
            for axis,pattern in OP_PATTERNS.items():
                if pattern.search(op["name"]):candidates.append({"record_kind":"p0_semantic_operation_candidate","candidate_id":f"candidate.p0.{axis.replace('_','-')}.{slug(contract['library_ref'])}.operation.{slug(op['name'])}","edition":1,"axis":axis,"family_id":contract["family_id"],"library_ref":contract["library_ref"],"operation_ref":op["operation_ref"],"operation_name":op["name"],"input_types":op["input_types"],"output_type":op["output_type"],"refusal_types":op["refusal_types"],"owner_decision":"UNRESOLVED","authority_limit":"Operation naming does not prove the comparison or regrain algebra, preservation, loss, totality or authority required by the constitution.","status":"P0_CANDIDATE_NOT_AUTHORITY"})
    collisions=[]
    for name,occ in sorted(type_occurrences.items()):
        families=sorted({x["family_id"] for x in occ})
        if len(families)>1:
            collisions.append({"record_kind":"cross_family_public_type_name_collision","collision_id":f"collision.p0.public-type.{slug(name)}","edition":1,"public_type_name":name,"family_count":len(families),"family_refs":families,"occurrences":occ,"allowed_dispositions":["SHARED_FOUNDATION_WITH_PROFILES","SAME_CARRIER_DIFFERENT_MEANING","HOMONYM_RENAME","ANTI_CORRUPTION_TRANSLATION","INTENTIONAL_DUPLICATE_REJECT_ONE","UNRESOLVED"],"decision":"UNRESOLVED","non_collapse_law":"An identical public type name does not prove common identity, equality, invariants, representation, ownership or substitutability.","status":"CROSS_OWNER_ADJUDICATION_REQUIRED"})
    symbol_collisions=[]
    for symbol_kind,collection,key in (("type","types","type_id"),("trait","traits","trait_id"),("operation","operations","operation_ref")):
        occurrences:dict[str,list[dict[str,Any]]]=collections.defaultdict(list)
        for contract in inputs:
            for definition in contract["api_contract_candidate"][collection]:
                occurrences[definition[key]].append({"family_id":contract["family_id"],"library_ref":contract["library_ref"],"definition_digest":hashlib.sha256(canonical(definition).encode()).hexdigest(),"name":definition.get("name")})
        for symbol_ref,items in sorted(occurrences.items()):
            libraries={x["library_ref"] for x in items}
            if len(libraries)<=1:continue
            families=sorted({x["family_id"] for x in items});definition_digests=sorted({x["definition_digest"] for x in items})
            identical=len(definition_digests)==1
            symbol_collisions.append({"record_kind":"global_public_symbol_ownership_collision","collision_id":f"collision.p0.symbol.{symbol_kind}.{slug(symbol_ref)}","edition":1,"symbol_kind":symbol_kind,"symbol_ref":symbol_ref,"library_count":len(libraries),"family_count":len(families),"family_refs":families,"definition_digest_count":len(definition_digests),"definition_digests":definition_digests,"occurrences":items,"collision_class":"IDENTICAL_REPEATED_DEFINITION_CANDIDATE_IMPORT_REQUIRED" if identical else "CONFLICTING_REPEATED_DEFINITION","priority":"P0" if len(families)>1 or not identical else "P1","allowed_dispositions":["CANONICAL_SHARED_OWNER_AND_IMPORTS","FAMILY_SHARED_OWNER_AND_IMPORTS","QUALIFY_LOCAL_SYMBOL_IDS","HOMONYM_RENAME","MERGE_DUPLICATE_LIBRARIES","REJECT_DUPLICATE_DEFINITION","UNRESOLVED"],"decision":"UNRESOLVED","compiler_refusal":"AMBIGUOUS_PUBLIC_SYMBOL_OWNER","non_collapse_law":"Equal symbol identifiers or definitions do not establish a canonical semantic owner; repeated definitions must become imports or receive unambiguous qualified identities.","status":"SYMBOL_OWNERSHIP_ADJUDICATION_REQUIRED"})
    candidate_by_pair:dict[tuple[str,str],list[str]]=collections.defaultdict(list)
    for x in candidates:candidate_by_pair[(x["family_id"],x["axis"])].append(x["candidate_id"])
    collision_by_family:dict[str,list[str]]=collections.defaultdict(list)
    for x in collisions:
        for family in x["family_refs"]:collision_by_family[family].append(x["collision_id"])
    symbol_collision_by_family:dict[str,list[str]]=collections.defaultdict(list)
    for x in symbol_collisions:
        for family in x["family_refs"]:symbol_collision_by_family[family].append(x["collision_id"])
    evidence_by_pair={(x["family_id"],x["axis"]):x for x in evidence if x["axis"] in {"identity_and_equality","grain_and_cardinality"}}
    work_by_pair={(x["family_id"],x["axis"]):x["work_package_id"] for x in work if x["axis"] in {"identity_and_equality","grain_and_cardinality"}}
    packets=[]
    for family in sorted({x["family_id"] for x in inputs}):
        libs=sorted(x["library_ref"] for x in inputs if x["family_id"]==family)
        for axis in ("identity_and_equality","grain_and_cardinality"):
            ers=[x for x in evidence if x["family_id"]==family and x["axis"]==axis];states=collections.Counter(x["evidence_state"] for x in ers)
            packets.append({"record_kind":"p0_family_axis_adjudication_packet","packet_id":f"packet.p0.{slug(family)}.{axis.replace('_','-')}","edition":1,"family_id":family,"axis":axis,"constitution_ref":bindings[axis]["constitution_ref"],"module_ref":bindings[axis]["module_ref"],"library_count":len(libs),"library_refs":libs,"candidate_refs":sorted(candidate_by_pair[(family,axis)]),"candidate_count":len(candidate_by_pair[(family,axis)]),"structured_evidence_state_counts":dict(sorted(states.items())),"targeted_evidence_work_package_ref":work_by_pair.get((family,axis)),"cross_family_collision_refs":sorted(collision_by_family[family]),"global_symbol_collision_refs":sorted(symbol_collision_by_family[family]),"required_outputs":["family ubiquitous-language definitions","owned carrier/relation/grain decisions","shared-foundation imports versus domain profiles","library exceptions and prohibited collapses","cross-family collision dispositions","negative twins and executable law oracles","remaining evidence vacancies and residual owners"],"family_default_decision":"UNRESOLVED","completion_effect":"Ratifies this P0 axis for one family only; exact public contracts, implementations and products remain separately gated.","status":"P0_OWNER_RESEARCH_AND_ADJUDICATION_REQUIRED"})
    symbol_counts=collections.Counter(x["symbol_kind"] for x in symbol_collisions)
    summary={"program_id":"program.semantic-axis.p0-identity-grain.v1","edition":1,"as_of":AS_OF,"status":"ACTIVE_OWNER_ADJUDICATION_REQUIRED","completion_claim":False,"families":23,"libraries":674,"family_axis_packets":len(packets),"type_and_operation_candidates":len(candidates),"identity_candidates":sum(x["axis"]=="identity_and_equality" for x in candidates),"grain_candidates":sum(x["axis"]=="grain_and_cardinality" for x in candidates),"cross_family_exact_type_name_collisions":len(collisions),"global_duplicate_symbol_ids":len(symbol_collisions),"duplicate_symbol_counts":dict(sorted(symbol_counts.items())),"conflicting_duplicate_symbol_definitions":sum(x["definition_digest_count"]>1 for x in symbol_collisions),"automatic_owner_decisions":0,"canonical_exact_gaps_closed":0,"finding":"Public API vocabulary supplies bounded candidate carriers and operations, but exact-name collisions, ambiguous global symbol ownership and suffix ambiguity require shared-foundation versus homonym adjudication before compiler type unification."}
    return {"candidates":candidates,"collisions":collisions,"symbol_collisions":symbol_collisions,"packets":packets,"summary":summary}

def outputs()->dict[str,str]:
    b=build();files={"type-operation-candidates.jsonl":"".join(canonical(x)+"\n" for x in b["candidates"]),"cross-family-type-collisions.jsonl":"".join(canonical(x)+"\n" for x in b["collisions"]),"global-symbol-collisions.jsonl":"".join(canonical(x)+"\n" for x in b["symbol_collisions"]),"family-axis-packets.jsonl":"".join(canonical(x)+"\n" for x in b["packets"]),"summary.json":json.dumps(b["summary"],ensure_ascii=False,sort_keys=True,indent=2)+"\n"};manifest={n:{"sha256":hashlib.sha256(t.encode()).hexdigest(),"bytes":len(t.encode())} for n,t in files.items()};files["manifest.json"]=json.dumps({"manifest_id":"manifest.semantic-axis.p0-identity-grain.v1","as_of":AS_OF,"files":manifest},sort_keys=True,indent=2)+"\n";return files

def main()->int:
    p=argparse.ArgumentParser();p.add_argument("--check",action="store_true");a=p.parse_args();stale=[]
    for n,t in outputs().items():
        q=HERE/n
        if a.check:
            if not q.is_file() or q.read_text()!=t:stale.append(n)
        else:q.write_text(t)
    if stale:print("STALE "+", ".join(stale));return 1
    s=build()["summary"];print(f"{'CHECK' if a.check else 'BUILD'} PASS P0 identity/grain mining: {s['family_axis_packets']} packets, {s['type_and_operation_candidates']} candidates, {s['cross_family_exact_type_name_collisions']} cross-family collisions, zero decisions");return 0

if __name__=="__main__":raise SystemExit(main())
