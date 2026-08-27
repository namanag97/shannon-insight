#!/usr/bin/env python3
"""Generate conservative family defaults, candidate clusters and member exception rows."""

from __future__ import annotations
import argparse,collections,hashlib,json
from pathlib import Path
from typing import Any

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
AS_OF="2026-08-26"

def canonical(v:Any)->str:return json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(",",":"))
def load_jsonl(p:Path)->list[dict[str,Any]]:return [json.loads(x) for x in p.read_text().splitlines() if x.strip()]
def slug(s:str)->str:return s.replace("constitution.family.","").replace("library.","").replace("_","-").replace(".","-")

def decision_schema()->dict[str,Any]:
    return {
      "$schema":"https://json-schema.org/draft/2020-12/schema","$id":"https://san.example/spec/semantic-axis-owner-decision-v1.schema.json","title":"Semantic axis owner decision","type":"object","additionalProperties":False,
      "required":["record_kind","decision_id","edition","subject_kind","subject_ref","family_id","axis","constitution_ref","module_ref","decision","rationale","ratifier_refs","evidence_claim_refs","exceptions","unresolved_items","status"],
      "properties":{
        "record_kind":{"const":"semantic_axis_owner_decision"},"decision_id":{"type":"string","minLength":1},"edition":{"type":"integer","minimum":1},
        "subject_kind":{"enum":["family_default","candidate_cluster","library_exception"]},"subject_ref":{"type":"string","minLength":1},"family_id":{"type":"string","minLength":1},
        "axis":{"enum":["semantic_object","semantic_role","identity_and_equality","grain_and_cardinality","state_and_change","time","order_and_topology","partiality_and_uncertainty","authority_and_trust","effect_boundary","representation","composition_algebra","compatibility_and_evolution","resources_and_failure","evidence_and_conformance","privacy_security_safety"]},
        "constitution_ref":{"type":"string","minLength":1},"module_ref":{"type":"string","minLength":1},
        "decision":{"enum":["APPLICABLE_AS_IS","APPLICABLE_WITH_EXCEPTION","CONDITIONAL","INAPPLICABLE_WITH_REASON","PROHIBITED_WITH_REASON","UNRESOLVED"]},
        "rationale":{"type":"string","minLength":1},"ratifier_refs":{"type":"array","items":{"type":"string","minLength":1},"uniqueItems":True},
        "evidence_claim_refs":{"type":"array","items":{"type":"string","minLength":1},"uniqueItems":True},"exceptions":{"type":"array","items":{"type":"object"}},
        "unresolved_items":{"type":"array","items":{"type":"string","minLength":1}},"status":{"enum":["DRAFT","PROPOSED","RATIFIED","REJECTED","SUPERSEDED"]},
      },
      "allOf":[
        {"if":{"properties":{"status":{"const":"RATIFIED"}}},"then":{"properties":{"ratifier_refs":{"minItems":1},"evidence_claim_refs":{"minItems":1}}}},
        {"if":{"properties":{"decision":{"enum":["INAPPLICABLE_WITH_REASON","PROHIBITED_WITH_REASON"]}}},"then":{"properties":{"rationale":{"minLength":20}}}},
        {"if":{"properties":{"decision":{"const":"UNRESOLVED"}}},"then":{"properties":{"unresolved_items":{"minItems":1}}}},
      ],
    }

def build()->dict[str,Any]:
    signatures=load_jsonl(ROOT/"library-semantic-signatures.jsonl")
    realizations={x["realization_id"]:x for x in load_jsonl(ROOT/"facet-realizations.jsonl")}
    coverage=json.loads((ROOT/"constitution-coverage.json").read_text())
    binding={x["axis"]:x for x in coverage["axis_bindings"]}
    rows=[]
    grouped:dict[tuple[str,str],list[dict[str,Any]]]=collections.defaultdict(list)
    for sig in signatures:
        for sel in sig["axis_selections"]:
            axis=sel["axis"]; facets=sel["candidate_facets"]
            facet_key=tuple(sorted((x["facet"],x["confidence"],x["realization_ref"]) for x in facets))
            if not facets: preclass="NO_DISCOVERY_SIGNAL_UNRESOLVED"
            elif all(x["confidence"]=="EXPLICIT_SOURCE_FIELD" for x in facets): preclass="EXPLICIT_SOURCE_CANDIDATE_UNRATIFIED"
            else: preclass="LEXICAL_CANDIDATE_UNRATIFIED"
            local=[];imports=[]
            for f in facets:
                realization=realizations[f["realization_ref"]]
                if realization["domain_overlay_required"]:local.append(f["facet"])
                imports.extend(realization["foundation_or_archetype_refs"])
            row={
                "record_kind":"library_axis_preclassification","preclassification_id":f"preclass.{slug(sig['library_ref'])}.{axis.replace('_','-')}","edition":1,
                "library_ref":sig["library_ref"],"family_id":sig["family_id"],"source_gap_ref":sig["source_gap_ref"],"signature_ref":sig["signature_id"],"axis":axis,
                "phase":binding[axis]["phase"],"constitution_ref":binding[axis]["constitution_ref"],"module_ref":binding[axis]["module_ref"],
                "candidate_facets":facets,"candidate_key":[list(x) for x in facet_key],"preclassification":preclass,
                "candidate_import_refs":sorted(set(imports)),"local_profile_slots":sorted(set(local)),
                "owner_decision":"UNRESOLVED","owner_decision_prohibition":"Discovery signals cannot establish applicability, inapplicability, prohibition, semantic identity or exact-contract closure.",
                "required_exception_fields":["rationale","bounded evidence","addition or changed coordinate","refusal/precedence delta","negative twin","conformance delta"] if facets else [],
                "status":"MECHANICAL_PRECLASSIFICATION_NOT_AUTHORITY_DOES_NOT_CLOSE_GAP",
            }
            rows.append(row);grouped[(sig["family_id"],axis)].append(row)
    clusters=[];matrices=[]
    for (family,axis),members in sorted(grouped.items()):
        buckets:dict[str,list[dict[str,Any]]]=collections.defaultdict(list)
        for row in members:buckets[canonical(row["candidate_key"])].append(row)
        cluster_refs=[];largest=max(len(x) for x in buckets.values())
        modal=[k for k,v in buckets.items() if len(v)==largest]
        default_key=modal[0] if len(modal)==1 else None
        for index,(key,bucket) in enumerate(sorted(buckets.items(),key=lambda kv:(-len(kv[1]),kv[0])),1):
            sample=bucket[0];cid=f"cluster.{slug(family)}.{axis.replace('_','-')}.{index:03d}";cluster_refs.append(cid)
            clusters.append({
                "record_kind":"family_axis_candidate_cluster","cluster_id":cid,"edition":1,"family_id":family,"axis":axis,
                "constitution_ref":sample["constitution_ref"],"module_ref":sample["module_ref"],"member_count":len(bucket),
                "member_preclassification_refs":[x["preclassification_id"] for x in bucket],"candidate_key":json.loads(key),
                "preclassification_counts":dict(sorted(collections.Counter(x["preclassification"] for x in bucket).items())),
                "is_unique_modal_candidate":key==default_key,"proposed_use":"FAMILY_DEFAULT_CANDIDATE" if key==default_key else "MEMBER_EXCEPTION_CLUSTER_CANDIDATE",
                "owner_decision":"UNRESOLVED","required_review":"Ratify, reject or split this cluster using owned semantics and bounded evidence; lexical co-membership is not semantic equivalence.",
                "status":"CLUSTER_NOT_AUTHORITY_DOES_NOT_CLOSE_GAP",
            })
        matrices.append({
            "record_kind":"family_axis_applicability_matrix","matrix_id":f"matrix.{slug(family)}.{axis.replace('_','-')}","edition":1,"family_id":family,"axis":axis,
            "phase":members[0]["phase"],"constitution_ref":members[0]["constitution_ref"],"module_ref":members[0]["module_ref"],"library_count":len(members),
            "candidate_cluster_refs":cluster_refs,"candidate_cluster_count":len(cluster_refs),"unique_modal_cluster_ref":cluster_refs[0] if default_key is not None else None,
            "family_default_decision":"UNRESOLVED","defaulting_prohibition":"The modal discovery cluster is a workload optimization only. It is not an applicable default until a named family owner ratifies it with evidence.",
            "required_outputs":["family default owner decision","cluster decisions","member exceptions","evidence vacancies and source conflicts","negative-twin outcomes","exact-contract import readiness"],
            "status":"OWNER_FAMILY_DEFAULT_AND_EXCEPTION_REVIEW_REQUIRED",
        })
    waves=[]
    for phase in range(1,6):
        ms=[x for x in matrices if x["phase"]==phase];cs=[x for x in clusters if binding[x["axis"]]["phase"]==phase];rs=[x for x in rows if x["phase"]==phase]
        waves.append({"record_kind":"semantic_applicability_review_wave","wave_id":f"wave.semantic-applicability.phase{phase}","edition":1,"phase":phase,"depends_on_wave_refs":[] if phase==1 else [f"wave.semantic-applicability.phase{phase-1}"],"matrix_refs":[x["matrix_id"] for x in ms],"matrices":len(ms),"clusters":len(cs),"member_rows":len(rs),"exit_gate":"Every matrix has a ratified family default or explicit unresolved reason; every nondefault member has an exception decision; evidence and negative twins remain traceable.","status":"PLANNED_OWNER_REVIEW"})
    counts=collections.Counter(x["preclassification"] for x in rows)
    summary={"program_id":"program.semantic-axis.applicability-matrices.v1","edition":1,"as_of":AS_OF,"status":"ACTIVE_OWNER_REVIEW_NOT_RATIFIED","completion_claim":False,"libraries":len(signatures),"axes":16,"raw_member_axis_cells":len(rows),"families":len({x["family_id"] for x in rows}),"family_axis_matrices":len(matrices),"candidate_clusters":len(clusters),"singleton_candidate_clusters":sum(x["member_count"]==1 for x in clusters),"preclassification_counts":dict(sorted(counts.items())),"automatic_owner_decisions":0,"canonical_exact_gaps_closed":0,"work_reduction_claim":"Matrices and clusters reduce repeated presentation and authoring only; they do not reduce required semantic accountability or evidence."}
    return {"rows":rows,"clusters":clusters,"matrices":matrices,"waves":waves,"summary":summary,"schema":decision_schema()}

def outputs()->dict[str,str]:
    b=build();files={"owner-decision.schema.json":json.dumps(b["schema"],ensure_ascii=False,sort_keys=True,indent=2)+"\n","member-preclassifications.jsonl":"".join(canonical(x)+"\n" for x in b["rows"]),"family-axis-decision-clusters.jsonl":"".join(canonical(x)+"\n" for x in b["clusters"]),"family-axis-applicability-matrices.jsonl":"".join(canonical(x)+"\n" for x in b["matrices"]),"review-waves.jsonl":"".join(canonical(x)+"\n" for x in b["waves"]),"summary.json":json.dumps(b["summary"],ensure_ascii=False,sort_keys=True,indent=2)+"\n"};manifest={n:{"sha256":hashlib.sha256(t.encode()).hexdigest(),"bytes":len(t.encode())} for n,t in files.items()};files["manifest.json"]=json.dumps({"manifest_id":"manifest.semantic-axis.applicability-matrices.v1","as_of":AS_OF,"files":manifest},sort_keys=True,indent=2)+"\n";return files

def main()->int:
    p=argparse.ArgumentParser();p.add_argument("--check",action="store_true");a=p.parse_args();stale=[]
    for n,t in outputs().items():
        q=HERE/n
        if a.check:
            if not q.is_file() or q.read_text()!=t:stale.append(n)
        else:q.write_text(t)
    if stale:print("STALE "+", ".join(stale));return 1
    s=build()["summary"];print(f"{'CHECK' if a.check else 'BUILD'} PASS applicability matrices: {s['raw_member_axis_cells']} cells -> {s['family_axis_matrices']} matrices / {s['candidate_clusters']} candidate clusters; zero owner decisions and zero gaps closed");return 0

if __name__=="__main__":raise SystemExit(main())
