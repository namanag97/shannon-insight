#!/usr/bin/env python3
"""Build lossless package/file/JSON-record routes into the synthesis architecture."""
from __future__ import annotations
import hashlib, json, mimetypes
from collections import defaultdict
from pathlib import Path
from typing import Any
from source_model import RULES, DECLARED_TOP_LEVEL_PREFIXES, IDENTITY_FIELDS

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
RESEARCH=ROOT/"research"
SELF_PREFIX="research/product_ontology/corpus_architecture_router/"

def canonical(x:Any)->str: return json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(",",":"))
def digest_bytes(b:bytes)->str: return hashlib.sha256(b).hexdigest()
def jsonl(name:str, rows:list[dict])->dict:
    text="".join(canonical(r)+"\n" for r in rows); (HERE/name).write_text(text)
    return {"path":name,"records":len(rows),"sha256":digest_bytes(text.encode())}
def research_files()->list[Path]:
    return sorted(p for p in RESEARCH.rglob("*") if p.is_file() and "__pycache__" not in p.parts and p.suffix!=".pyc" and not str(p.relative_to(ROOT)).startswith(SELF_PREFIX))
def matching_rules(rel:str)->list[dict]: return [r for r in RULES if rel.startswith(r["path_prefix"])]
def select_rule(rel:str)->tuple[dict|None,list[str]]:
    matches=matching_rules(rel)
    if not matches:return None,[]
    width=max(len(r["path_prefix"]) for r in matches); winners=[r for r in matches if len(r["path_prefix"])==width]
    return (winners[0] if len(winners)==1 else None),[r["rule_id"] for r in winners]
def route_fields(rule:dict)->dict:
    return {k:rule[k] for k in ("rule_id","component_ref","input_ir_ref","output_ir_ref","frontier_class_ref","binding_phase_ref","authority")}
def parse_records(path:Path)->tuple[str,list[tuple[int,Any]],str|None]:
    try:
        if path.suffix==".jsonl":
            return "PARSED_JSONL",[(i,json.loads(line)) for i,line in enumerate(path.read_text(encoding="utf-8").splitlines(),1) if line.strip()],None
        if path.suffix==".json":
            value=json.loads(path.read_text(encoding="utf-8"))
            if isinstance(value,list): return "PARSED_JSON_ARRAY",list(enumerate(value,1)),None
            return "PARSED_JSON_DOCUMENT",[(1,value)],None
        return "NOT_JSON",[],None
    except Exception as exc: return "PARSE_REFUSED",[],f"{type(exc).__name__}: {exc}"
def source_identity(value:Any,index:int)->tuple[str,str]:
    if isinstance(value,dict):
        for field in IDENTITY_FIELDS:
            if field in value and value[field] not in (None,"") and not isinstance(value[field],(dict,list)):
                return f"{field}:{value[field]}",f"DECLARED_FIELD:{field}"
    return f"occurrence:{index}","OCCURRENCE_ONLY"

def build()->dict[str,Any]:
    file_routes=[]; record_routes=[]; identity_findings=[]; parse_findings=[]; ambiguities=[]; unrouted=[]
    package_members:dict[str,list[dict]]=defaultdict(list)
    for path in research_files():
        rel=str(path.relative_to(ROOT)); rule,winners=select_rule(rel)
        if rule is None:
            (ambiguities if winners else unrouted).append({"path":rel,"candidate_rule_refs":winners})
            continue
        data=path.read_bytes(); file_id="file-route."+digest_bytes(rel.encode())[:20]
        status,records,error=parse_records(path)
        identities=[(index,value,*source_identity(value,index)) for index,value in records]
        declared=sum(basis.startswith("DECLARED_FIELD") for _,_,_,basis in identities)
        occurrence_only=len(identities)-declared
        record_set_sha256=digest_bytes("".join(
            f"{index}:{digest_bytes(canonical(value).encode())}\n" for index,value,_,_ in identities
        ).encode())
        row={"file_route_id":file_id,"path":rel,"sha256":digest_bytes(data),"bytes":len(data),"media_type":mimetypes.guess_type(path.name)[0] or "application/octet-stream","parse_status":status,"parse_error":error,"record_count":len(records),"declared_identity_count":declared,"occurrence_only_count":occurrence_only,"record_set_sha256":record_set_sha256,"route_precision":"EXPLICIT_PACKAGE_PREFIX","invalidation_triggers":rule["invalidation_triggers"],**route_fields(rule),"completion_claim":False}
        file_routes.append(row); package_members[rule["rule_id"]].append(row)
        if error: parse_findings.append({"finding_id":f"parse-finding.{file_id}","file_route_ref":file_id,"path":rel,"status":status,"error":error,"blocks_file_routing":False,"blocks_record_routing":True,"completion_claim":False})
        if occurrence_only:
            identity_findings.append({"finding_id":f"identity-finding.{file_id}","file_route_ref":file_id,"path":rel,"record_count":len(records),"declared_identity_count":declared,"occurrence_only_count":occurrence_only,"addressing_rule":"file_route_ref plus one-based record_index; content integrity is covered by record_set_sha256","stability":"POSITIONAL_OCCURRENCE_IDENTITY_CHANGES_WHEN_RECORD_ORDER_CHANGES","requires_schema_identity_adjudication":True,"completion_claim":False})
        # Only declared identities need a reverse-index row. Every parsed occurrence remains
        # addressable through file_route_ref + one-based index and covered by record_set_sha256.
        for index,value,identity,basis in identities:
            if basis=="OCCURRENCE_ONLY": continue
            record_routes.append({"record_route_id":f"record-route.{digest_bytes((rel+'#'+str(index)).encode())[:24]}","file_route_ref":file_id,"record_index":index,"source_identity":identity,"identity_basis":basis,"content_sha256":digest_bytes(canonical(value).encode()),"completion_claim":False})
    packages=[]
    for rule in sorted(RULES,key=lambda r:r["rule_id"]):
        members=package_members.get(rule["rule_id"],[])
        combined=digest_bytes("".join(f"{r['path']}:{r['sha256']}\n" for r in sorted(members,key=lambda x:x["path"])).encode())
        packages.append({"package_route_id":rule["rule_id"].replace("route-rule.","package-route."),"rule_ref":rule["rule_id"],"path_prefix":rule["path_prefix"],"purpose":rule["purpose"],"file_count":len(members),"total_bytes":sum(r["bytes"] for r in members),"content_set_sha256":combined,"dependency_rule_refs":rule["dependency_rule_refs"],"invalidation_triggers":rule["invalidation_triggers"],**{k:rule[k] for k in ("component_ref","input_ir_ref","output_ir_ref","frontier_class_ref","binding_phase_ref","authority")},"completion_claim":False})
    return {"rules":sorted(RULES,key=lambda r:r["rule_id"]),"packages":packages,"files":sorted(file_routes,key=lambda r:r["path"]),"records":sorted(record_routes,key=lambda r:(r["file_route_ref"],r["record_index"])),"identity_findings":sorted(identity_findings,key=lambda r:r["path"]),"parse_findings":parse_findings,"ambiguities":ambiguities,"unrouted":unrouted}

def main():
    built=build(); outputs=[]
    for name,key in [("routing-rules.jsonl","rules"),("package-routes.jsonl","packages"),("file-routes.jsonl","files"),("record-routes.jsonl","records"),("record-identity-findings.jsonl","identity_findings"),("parse-findings.jsonl","parse_findings"),("ambiguous-routes.jsonl","ambiguities"),("unrouted-files.jsonl","unrouted")]: outputs.append(jsonl(name,built[key]))
    routed_record_count=sum(r["record_count"] for r in built["files"])
    occurrence_only_count=sum(r["occurrence_only_count"] for r in built["files"])
    summary={"rules":len(built["rules"]),"packages":len(built["packages"]),"nonempty_packages":sum(r["file_count"]>0 for r in built["packages"]),"routed_files":len(built["files"]),"routed_record_occurrences":routed_record_count,"declared_identity_routes":len(built["records"]),"occurrence_only_records":occurrence_only_count,"files_requiring_schema_identity_adjudication":len(built["identity_findings"]),"parse_findings":len(built["parse_findings"]),"ambiguous_files":len(built["ambiguities"]),"unrouted_files":len(built["unrouted"]),"self_hosting_exclusion":SELF_PREFIX,"completion_claim":False}
    (HERE/"summary.json").write_text(json.dumps(summary,indent=2,sort_keys=True)+"\n"); (HERE/"manifest.json").write_text(json.dumps({"files":outputs,"summary":summary},indent=2,sort_keys=True)+"\n")
    print(json.dumps(summary,indent=2,sort_keys=True)); return 0
if __name__=="__main__": raise SystemExit(main())
