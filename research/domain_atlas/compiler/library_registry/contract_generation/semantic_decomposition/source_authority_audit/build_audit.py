#!/usr/bin/env python3
"""Audit and receipt the 23 upstream family corpora without granting semantic authority."""

from __future__ import annotations
import argparse,collections,hashlib,json,subprocess,sys
from pathlib import Path
from typing import Any

HERE=Path(__file__).resolve().parent
SEMANTIC=HERE.parent
REPO=HERE.parents[6]
PACKAGES=SEMANTIC/"structured_projection/source-authority-work-packages.jsonl"
RECEIPTS=HERE/"validator-receipts.jsonl"
AS_OF="2026-08-26"

def canonical(v:Any)->str:return json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(",",":"))
def load_jsonl(p:Path)->list[dict[str,Any]]:return [json.loads(x) for x in p.read_text().splitlines() if x.strip()]
def sha(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def relevant_files(directory:Path)->list[Path]:return sorted(p for p in directory.rglob("*") if p.is_file() and "__pycache__" not in p.parts and p.name not in {".DS_Store"})
def tree_digest(directory:Path)->str:
    h=hashlib.sha256()
    for p in relevant_files(directory):
        h.update(str(p.relative_to(directory)).encode()+b"\0"+p.read_bytes()+b"\0")
    return h.hexdigest()
def validator_for(directory:Path)->Path:
    candidates=sorted(directory.glob("validate*.py"));assert candidates,f"no validator in {directory}";return candidates[0]

def refresh_receipts()->list[dict[str,Any]]:
    receipts=[]
    for package in load_jsonl(PACKAGES):
        directory=(REPO/package["source_path"]).parent;validator=validator_for(directory);before=tree_digest(directory)
        completed=subprocess.run([sys.executable,str(validator)],cwd=REPO,text=True,capture_output=True,check=False,timeout=120)
        after=tree_digest(directory);output=(completed.stdout+completed.stderr).strip()
        receipts.append({"record_kind":"family_corpus_validator_receipt","receipt_id":f"receipt.source-validator.{package['family_id'].replace('constitution.family.','')}.v1","edition":1,"family_id":package["family_id"],"source_directory":str(directory.relative_to(REPO)),"validator_path":str(validator.relative_to(REPO)),"validator_sha256":sha(validator),"tree_digest_before":before,"tree_digest_after":after,"validator_exit_code":completed.returncode,"output_sha256":hashlib.sha256(output.encode()).hexdigest(),"output_tail":output.splitlines()[-1][:500] if output else "","validator_result":"PASS" if completed.returncode==0 and before==after else "FAIL_OR_MUTATION","authority_limit":"A passing validator proves only the rules encoded by that exact validator over the bound tree. It does not prove source authority, semantic completeness, primary-evidence sufficiency, boundary correctness or implementation conformance.","status":"CURRENT_STRUCTURAL_VALIDATION_RECEIPT" if completed.returncode==0 and before==after else "SOURCE_CORPUS_REPAIR_REQUIRED"})
    RECEIPTS.write_text("".join(canonical(x)+"\n" for x in receipts));return receipts

def decision_schema()->dict[str,Any]:
    return {"$schema":"https://json-schema.org/draft/2020-12/schema","$id":"https://san.example/spec/family-source-authority-decision-v1.schema.json","type":"object","additionalProperties":False,"required":["record_kind","decision_id","edition","family_id","source_path","source_digest","decision","schema_authority_refs","record_authority_refs","evidence_claim_refs","adopted_fields","rejected_fields","transformations","conflicts","unresolved_items","ratifier_refs","status"],"properties":{"record_kind":{"const":"family_source_authority_decision"},"decision_id":{"type":"string","minLength":1},"edition":{"type":"integer","minimum":1},"family_id":{"type":"string","minLength":1},"source_path":{"type":"string","minLength":1},"source_digest":{"type":"string","pattern":"^[0-9a-f]{64}$"},"decision":{"enum":["ADOPT_CANONICAL","ADOPT_WITH_TRANSFORM","SPLIT","MERGE","REPLACE","REJECT","UNRESOLVED"]},"schema_authority_refs":{"type":"array","items":{"type":"string"},"uniqueItems":True},"record_authority_refs":{"type":"array","items":{"type":"string"},"uniqueItems":True},"evidence_claim_refs":{"type":"array","items":{"type":"string"},"uniqueItems":True},"adopted_fields":{"type":"array","items":{"type":"string"},"uniqueItems":True},"rejected_fields":{"type":"array","items":{"type":"string"},"uniqueItems":True},"transformations":{"type":"array","items":{"type":"object"}},"conflicts":{"type":"array","items":{"type":"object"}},"unresolved_items":{"type":"array","items":{"type":"string"}},"ratifier_refs":{"type":"array","items":{"type":"string"},"uniqueItems":True},"status":{"enum":["DRAFT","PROPOSED","RATIFIED","REJECTED","SUPERSEDED"]}},"allOf":[{"if":{"properties":{"status":{"const":"RATIFIED"}}},"then":{"properties":{"schema_authority_refs":{"minItems":1},"record_authority_refs":{"minItems":1},"evidence_claim_refs":{"minItems":1},"ratifier_refs":{"minItems":1}}}},{"if":{"properties":{"decision":{"const":"UNRESOLVED"}}},"then":{"properties":{"unresolved_items":{"minItems":1}}}}]}

def build()->dict[str,Any]:
    packages=load_jsonl(PACKAGES);receipts={x["family_id"]:x for x in load_jsonl(RECEIPTS)};assert len(packages)==len(receipts)==23
    audits=[]
    for package in packages:
        directory=(REPO/package["source_path"]).parent;receipt=receipts[package["family_id"]]
        schemas=sorted(p for p in relevant_files(directory) if "schema" in p.name.lower() or "schema" in p.parts)
        builders=sorted(directory.glob("build*.py"));validators=sorted(directory.glob("validate*.py"))
        evidence=sorted(p for p in directory.glob("*.json*") if any(x in p.name.lower() for x in ("source","evidence")))
        gaps=sorted(p for p in directory.glob("*gap*.json*"))
        manifests=sorted(directory.glob("manifest.json"));readmes=sorted(directory.glob("README.md"))
        validator_text="\n".join(x.read_text(errors="ignore").lower() for x in validators)
        builder_text="\n".join(x.read_text(errors="ignore").lower() for x in builders)
        dimensions={
          "source_file_presence":"PASS" if (REPO/package["source_path"]).is_file() else "MISSING",
          "builder_presence":"PASS" if builders else "MISSING",
          "validator_receipt":"PASS" if receipt["validator_result"]=="PASS" else "FAIL",
          "schema_presence":"PASS" if schemas else "MISSING",
          "schema_validator_binding_signal":"PASS" if schemas and "schema" in validator_text else "MISSING_OR_UNDETECTED",
          "manifest_presence":"PASS" if manifests else "MISSING",
          "manifest_builder_validator_binding_signal":"PASS" if manifests and "manifest" in validator_text and "manifest" in builder_text else "MISSING_OR_UNDETECTED",
          "evidence_presence":"PASS" if evidence else "MISSING",
          "evidence_validator_binding_signal":"PASS" if evidence and ("source" in validator_text or "evidence" in validator_text) else "MISSING_OR_UNDETECTED",
          "gaps_presence":"PASS" if gaps else "MISSING",
          "gaps_validator_binding_signal":"PASS" if gaps and "gap" in validator_text else "MISSING_OR_UNDETECTED",
          "deterministic_rebuild_binding_signal":"PASS" if any(x in validator_text for x in ("build","output","drift","rebuild")) else "MISSING_OR_UNDETECTED",
          "readme_presence":"PASS" if readmes else "MISSING",
        }
        missing=[k for k,v in dimensions.items() if v!="PASS"]
        readiness="STRUCTURALLY_STRONG_SOURCE_CANDIDATE_NOT_CANONICAL" if not missing else "VALIDATED_SOURCE_CANDIDATE_WITH_MISSING_OR_UNDETECTED_CONTROLS"
        audits.append({"record_kind":"family_source_authority_readiness_audit","audit_id":f"audit.source-authority.{package['family_id'].replace('constitution.family.','')}.v1","edition":1,"family_id":package["family_id"],"source_path":package["source_path"],"source_file_sha256":sha(REPO/package["source_path"]),"source_directory":str(directory.relative_to(REPO)),"tree_digest":tree_digest(directory),"library_count":package["library_count"],"dimension_results":dimensions,"missing_or_failed_controls":missing,"binding_detection_method":"Static token signals in exact builder/validator sources; PASS is useful routing evidence, not proof that coverage is complete.","builder_paths":[str(x.relative_to(REPO)) for x in builders],"validator_paths":[str(x.relative_to(REPO)) for x in validators],"schema_paths":[str(x.relative_to(REPO)) for x in schemas],"manifest_paths":[str(x.relative_to(REPO)) for x in manifests],"evidence_paths":[str(x.relative_to(REPO)) for x in evidence],"gap_paths":[str(x.relative_to(REPO)) for x in gaps],"validator_receipt_ref":receipt["receipt_id"],"validator_result":receipt["validator_result"],"readiness":readiness,"authority_decision":"UNRESOLVED","canonical":False,"authority_limit":"Structural readiness and deterministic validation do not establish who may define the schema or records, whether evidence claims are sufficient, whether boundaries are correct, or whether source fields should be adopted.","status":"SOURCE_AUTHORITY_DECISION_REQUIRED"})
    counts=collections.Counter(x["readiness"] for x in audits);missing=collections.Counter(k for x in audits for k in x["missing_or_failed_controls"])
    summary={"program_id":"program.family-source-authority-audit.v1","edition":1,"as_of":AS_OF,"status":"ACTIVE_AUTHORITY_DECISIONS_OPEN","completion_claim":False,"families":23,"libraries":sum(x["library_count"] for x in audits),"validator_passes":sum(x["validator_result"]=="PASS" for x in audits),"structurally_strong_candidates":sum(not x["missing_or_failed_controls"] for x in audits),"readiness_counts":dict(sorted(counts.items())),"missing_control_counts":dict(sorted(missing.items())),"ratified_source_authorities":0,"canonical_source_corpora":0,"finding":"Validation coverage is broad, but structural controls and source authority remain separate. Missing schemas/manifests are explicit rather than hidden by passing domain validators."}
    return {"audits":audits,"summary":summary,"schema":decision_schema(),"receipts":list(receipts.values())}

def outputs()->dict[str,str]:
    b=build();files={"source-authority-decision.schema.json":json.dumps(b["schema"],ensure_ascii=False,sort_keys=True,indent=2)+"\n","readiness-audits.jsonl":"".join(canonical(x)+"\n" for x in b["audits"]),"summary.json":json.dumps(b["summary"],ensure_ascii=False,sort_keys=True,indent=2)+"\n"};manifest={n:{"sha256":hashlib.sha256(t.encode()).hexdigest(),"bytes":len(t.encode())} for n,t in files.items()};manifest["validator-receipts.jsonl"]={"sha256":sha(RECEIPTS),"bytes":len(RECEIPTS.read_bytes())};files["manifest.json"]=json.dumps({"manifest_id":"manifest.family-source-authority-audit.v1","as_of":AS_OF,"files":manifest},sort_keys=True,indent=2)+"\n";return files

def main()->int:
    p=argparse.ArgumentParser();p.add_argument("--check",action="store_true");p.add_argument("--refresh-receipts",action="store_true");a=p.parse_args()
    if a.refresh_receipts or not RECEIPTS.is_file():refresh_receipts()
    stale=[]
    for n,t in outputs().items():
        q=HERE/n
        if a.check:
            if not q.is_file() or q.read_text()!=t:stale.append(n)
        else:q.write_text(t)
    if stale:print("STALE "+", ".join(stale));return 1
    s=build()["summary"];print(f"{'CHECK' if a.check else 'BUILD'} PASS source-authority audit: {s['families']} families, {s['validator_passes']} validator receipts, {s['structurally_strong_candidates']} structurally strong candidates, zero authorities ratified");return 0

if __name__=="__main__":raise SystemExit(main())
