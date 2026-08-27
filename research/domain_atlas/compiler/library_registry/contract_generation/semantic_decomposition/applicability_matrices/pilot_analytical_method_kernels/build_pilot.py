#!/usr/bin/env python3
"""Project the existing method-kernel source corpus into structured axis evidence and exact-contract inputs."""

from __future__ import annotations
import argparse,collections,hashlib,json
from pathlib import Path
from typing import Any

HERE=Path(__file__).resolve().parent
SEMANTIC=HERE.parent.parent
REPO=HERE.parents[7]
SOURCE=REPO/"research/domain_atlas/universes/method_kernels/library-boundaries.jsonl"
FAMILY="constitution.family.analytical_method_kernels"
AS_OF="2026-08-26"

def canonical(v:Any)->str:return json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(",",":"))
def load_jsonl(p:Path)->list[dict[str,Any]]:return [json.loads(x) for x in p.read_text().splitlines() if x.strip()]
def terms(values:list[str],needles:tuple[str,...])->list[str]:return [x for x in values if any(n in x.lower() for n in needles)]

def axis_evidence(lib:dict[str,Any])->dict[str,list[dict[str,Any]]]:
    fields={
      "semantic_object":[("public_types",lib["public_types"])],
      "semantic_role":[("library_kind",lib["library_kind"]),("public_traits",lib["public_traits"]),("operation_refs",lib["operation_refs"])],
      "identity_and_equality":[("identity_equality_type_candidates",terms(lib["public_types"],("id","identity","key","equivalence","digest")))],
      "grain_and_cardinality":[("grain_decision_refs",terms(lib["decision_refs"],("grain","population","sampling","cardinality","group")))],
      "state_and_change":[("state_type_candidates",terms(lib["public_types"],("state","plan","artifact","model","index","assignment","exposure","baseline")))],
      "time":[("time_candidates",terms(lib["decision_refs"]+lib["public_types"],("time","temporal","window","calendar","survival","horizon","cut","stopping")))],
      "order_and_topology":[("order_topology_candidates",terms(lib["decision_refs"]+lib["public_types"],("order","graph","spatial","topology","coordinate","path","sequence","geometry","grid")))],
      "partiality_and_uncertainty":[("partiality_uncertainty_candidates",terms(lib["decision_refs"]+lib["public_types"]+lib["error_contracts"],("missing","uncertainty","confidence","probability","invalid","unsupported","assumption","numerical")))],
      "authority_and_trust":[("semantic_owner_refs",lib["semantic_owner_refs"])],
      "effect_boundary":[("effect_boundary",lib["effect_boundary"]),("effect_intents",lib["effect_intents"]),("runtime_receipts",lib["runtime_receipts"])],
      "representation":[("targets",lib["targets"]),("configuration_contracts",lib["configuration_contracts"]),("unsafe_ffi_generated_policy",lib["unsafe_ffi_generated_policy"])],
      "composition_algebra":[("laws",lib["laws"]),("algebra_candidates",terms(lib["decision_refs"]+lib["public_types"],("algebra","merge","aggregation","compose","formula","semiring","reconciliation")))],
      "compatibility_and_evolution":[("compatibility",lib["compatibility"]),("removal_seams",lib["removal_seams"])],
      "resources_and_failure":[("resource_contracts",lib["resource_contracts"]),("cancellation",lib["cancellation"]),("concurrency",lib["concurrency"]),("error_contracts",lib["error_contracts"])],
      "evidence_and_conformance":[("evidence_refs",lib["evidence_refs"]),("oracles",lib["oracles"]),("gaps",lib["gaps"])],
      "privacy_security_safety":[("trust_harm_candidates",terms(lib["forbidden_responsibilities"]+lib["unsafe_ffi_generated_policy"],("unsafe","ffi","safety","privacy","security","authority","ambient")))],
    }
    out={}
    for axis,items in fields.items():
        records=[]
        for path,value in items:
            vals=value if isinstance(value,list) else [value]
            if vals:records.append({"source_field":path,"values":vals})
        out[axis]=records
    return out

def build()->dict[str,Any]:
    libs=load_jsonl(SOURCE);assert len(libs)==72
    coverage=json.loads((SEMANTIC/"constitution-coverage.json").read_text());bindings={x["axis"]:x for x in coverage["axis_bindings"]}
    signatures={x["library_ref"]:x for x in load_jsonl(SEMANTIC/"library-semantic-signatures.jsonl") if x["family_id"]==FAMILY}
    records=[];contracts=[];per_lib=[]
    library_kind_by_ref={x["library_id"]:x["library_kind"] for x in libs}
    source_digest=hashlib.sha256(SOURCE.read_bytes()).hexdigest()
    for lib in libs:
        lid=lib["library_id"];assert lid in signatures
        evidence=axis_evidence(lib);vacant=[]
        for axis in sorted(bindings,key=lambda a:(bindings[a]["phase"],a)):
            items=evidence[axis]
            if not items:vacant.append(axis)
            records.append({
              "record_kind":"structured_library_axis_evidence_candidate","evidence_projection_id":f"projection.axis-evidence.{lid.replace('library.','')}.{axis.replace('_','-')}","edition":1,
              "library_ref":lid,"family_id":FAMILY,"axis":axis,"phase":bindings[axis]["phase"],"constitution_ref":bindings[axis]["constitution_ref"],"module_ref":bindings[axis]["module_ref"],
              "source_record_ref":lid,"source_path":"research/domain_atlas/universes/method_kernels/library-boundaries.jsonl","source_file_sha256":source_digest,
              "structured_evidence":items,"evidence_state":"STRUCTURED_SOURCE_EVIDENCE_CANDIDATE_UNRATIFIED" if items else "AXIS_EVIDENCE_VACANCY",
              "applicability_decision":"UNRESOLVED","interpretation_limit":"Source fields narrow owner research but do not prove axis applicability, completeness, semantic equivalence or constitution conformance.",
              "status":"SOURCE_PROJECTION_NOT_AUTHORITY_DOES_NOT_CLOSE_GAP",
            })
        contracts.append({
          "record_kind":"exact_library_contract_input_candidate","contract_input_id":f"input.exact-contract.{lid.replace('library.','')}.v1","edition":1,"library_ref":lid,"family_id":FAMILY,
          "source_gap_ref":signatures[lid]["source_gap_ref"],"source_path":"research/domain_atlas/universes/method_kernels/library-boundaries.jsonl","source_file_sha256":source_digest,"source_record_edition":lib["edition"],
          "semantic_owner_refs":lib["semantic_owner_refs"],"library_kind":lib["library_kind"],"effect_boundary":lib["effect_boundary"],
          "exact_public_type_names":lib["public_types"],"exact_public_trait_names":lib["public_traits"],"exact_operation_refs":lib["operation_refs"],
          "law_candidates":lib["laws"],"refusal_type_candidates":lib["error_contracts"],"dependency_refs":lib["dependencies"],"requirement_refs":lib["requirement_refs"],"offer_refs":lib["offer_refs"],
          "configuration_contracts":lib["configuration_contracts"],"resource_contracts":lib["resource_contracts"],"cancellation_contracts":lib["cancellation"],"concurrency_contracts":lib["concurrency"],
          "evidence_refs":lib["evidence_refs"],"oracle_candidates":lib["oracles"],"removal_seams":lib["removal_seams"],"known_source_gaps":lib["gaps"],
          "remaining_ratification_gates":["boundary disposition","full 16-axis applicability and exceptions","exact signatures and visibility","law/refusal/default/precedence ownership","evidence claim adoption","negative twins","two unrelated verticals","implementation conformance"],
          "status":"SOURCE_EXTRACTED_INPUT_CANDIDATE_NOT_EXACT_CONTRACT_DOES_NOT_CLOSE_GAP",
        })
        per_lib.append({"record_kind":"method_kernel_semantic_readiness","readiness_id":f"readiness.semantic.{lid.replace('library.','')}","edition":1,"library_ref":lid,"structured_axis_evidence_count":16-len(vacant),"axis_evidence_vacancies":vacant,"exact_names_available":{"types":len(lib["public_types"]),"traits":len(lib["public_traits"]),"operations":len(lib["operation_refs"])},"exact_contract_input_ref":contracts[-1]["contract_input_id"],"readiness":"SOURCE_INPUT_COMPLETE_OWNER_RATIFICATION_OPEN" if not vacant else "SOURCE_INPUT_WITH_AXIS_EVIDENCE_VACANCIES","canonical_gap_closed":False})
    defaults=[]
    for axis in sorted(bindings,key=lambda a:(bindings[a]["phase"],a)):
        rs=[x for x in records if x["axis"]==axis];covered=sum(bool(x["structured_evidence"]) for x in rs)
        fingerprints=collections.Counter(canonical(x["structured_evidence"]) for x in rs)
        common_fields=set.intersection(*(set(item["source_field"] for item in x["structured_evidence"]) for x in rs)) if rs else set()
        defaults.append({"record_kind":"method_kernel_family_axis_default_candidate","default_candidate_id":f"default-candidate.method-kernels.{axis.replace('_','-')}","edition":1,"family_id":FAMILY,"axis":axis,"phase":bindings[axis]["phase"],"constitution_ref":bindings[axis]["constitution_ref"],"module_ref":bindings[axis]["module_ref"],"libraries":72,"libraries_with_structured_evidence":covered,"coverage_bps":covered*10000//72,"distinct_evidence_fingerprints":len(fingerprints),"fields_present_for_every_member":sorted(common_fields),"default_candidate":"SHARED_EVIDENCE_FIELD_PATTERN_PENDING_SEMANTIC_REVIEW" if common_fields else "NO_SAFE_FAMILY_DEFAULT_CANDIDATE","owner_decision":"UNRESOLVED","status":"CANDIDATE_NOT_AUTHORITY_DOES_NOT_CLOSE_GAP"})
    research_questions={
      "identity_and_equality":"Which exact subjects have identity, which equality/co-reference/version-continuity relations exist, and where must comparisons refuse?",
      "grain_and_cardinality":"What are the observation, identity, analysis, update, authority, storage, partition, ordering and completeness grains and legal regrain operations?",
      "state_and_change":"Which artifacts have lifecycle identity, legal transitions, history cuts, concurrency rules, snapshots, corrections and compensation semantics?",
      "time":"Which occurrence, observation, validity, recording, processing, decision, correction, deadline, TTL and calendar roles are applicable and under which clock authority?",
      "order_and_topology":"Which total/partial/causal orders and graph/spatial topology relations are owned, and which reorderings or projections preserve meaning?",
      "authority_and_trust":"Who owns definitions, facts, decisions, issuance, execution and acceptance; what mandate, delegation, evidence, defeaters and revocation apply?",
    }
    vacancy_groups:dict[tuple[str,str],list[str]]=collections.defaultdict(list)
    for record in records:
        if record["evidence_state"]=="AXIS_EVIDENCE_VACANCY":vacancy_groups[(record["axis"],library_kind_by_ref[record["library_ref"]])].append(record["library_ref"])
    priority={1:"P0",2:"P1",3:"P1",4:"P2",5:"P2"}
    vacancy_packages=[]
    for index,((axis,kind),member_refs) in enumerate(sorted(vacancy_groups.items(),key=lambda kv:(bindings[kv[0][0]]["phase"],-len(kv[1]),kv[0])),1):
        vacancy_packages.append({"record_kind":"method_kernel_axis_evidence_vacancy_work_package","work_package_id":f"work.method-kernels.axis-evidence.{index:03d}","edition":1,"family_id":FAMILY,"axis":axis,"phase":bindings[axis]["phase"],"priority":priority[bindings[axis]["phase"]],"library_kind":kind,"library_count":len(member_refs),"library_refs":sorted(member_refs),"constitution_ref":bindings[axis]["constitution_ref"],"module_ref":bindings[axis]["module_ref"],"sovereign_research_question":research_questions[axis],"required_outputs":["bounded primary evidence claims and authority limits","family-shared coordinate decisions","library-specific exceptions and prohibitions","cross-owner collisions","negative/adversarial twins","remaining unresolved coordinates and owner"],"parallelism":"Independent library-kind packages within an axis may run in parallel after the phase constitution is accepted.","completion_effect":"Fills structured evidence vacancies only; applicability, exact contracts and implementation qualification remain separately gated.","status":"RESEARCH_AND_OWNER_ADJUDICATION_REQUIRED"})
    summary={"program_id":"program.semantic-axis.pilot.method-kernels.v1","edition":1,"as_of":AS_OF,"status":"ACTIVE_OWNER_RATIFICATION_OPEN","completion_claim":False,"libraries":72,"axis_evidence_rows":len(records),"family_default_candidates":len(defaults),"exact_contract_input_candidates":len(contracts),"libraries_with_exact_type_trait_operation_names":sum(bool(x["exact_public_type_names"] and x["exact_public_trait_names"] and x["exact_operation_refs"]) for x in contracts),"total_axis_evidence_vacancies":sum(len(x["axis_evidence_vacancies"]) for x in per_lib),"vacancy_axes":len({x["axis"] for x in vacancy_packages}),"vacancy_work_packages":len(vacancy_packages),"automatic_owner_decisions":0,"canonical_exact_gaps_closed":0,"advance":"The previously generic missing types/traits/operations dimension now has source-extracted exact-name candidates for every method-kernel library; remaining axis vacancies are grouped into role-aware work packages and all semantic decisions still require owner ratification."}
    return {"records":records,"contracts":contracts,"per_lib":per_lib,"defaults":defaults,"vacancy_packages":vacancy_packages,"summary":summary}

def outputs()->dict[str,str]:
    b=build();files={"structured-axis-evidence.jsonl":"".join(canonical(x)+"\n" for x in b["records"]),"family-default-candidates.jsonl":"".join(canonical(x)+"\n" for x in b["defaults"]),"exact-contract-input-candidates.jsonl":"".join(canonical(x)+"\n" for x in b["contracts"]),"library-readiness.jsonl":"".join(canonical(x)+"\n" for x in b["per_lib"]),"evidence-vacancy-work-packages.jsonl":"".join(canonical(x)+"\n" for x in b["vacancy_packages"]),"summary.json":json.dumps(b["summary"],ensure_ascii=False,sort_keys=True,indent=2)+"\n"};manifest={n:{"sha256":hashlib.sha256(t.encode()).hexdigest(),"bytes":len(t.encode())} for n,t in files.items()};files["manifest.json"]=json.dumps({"manifest_id":"manifest.semantic-axis.pilot.method-kernels.v1","as_of":AS_OF,"source_sha256":hashlib.sha256(SOURCE.read_bytes()).hexdigest(),"files":manifest},sort_keys=True,indent=2)+"\n";return files

def main()->int:
    p=argparse.ArgumentParser();p.add_argument("--check",action="store_true");a=p.parse_args();stale=[]
    for n,t in outputs().items():
        q=HERE/n
        if a.check:
            if not q.is_file() or q.read_text()!=t:stale.append(n)
        else:q.write_text(t)
    if stale:print("STALE "+", ".join(stale));return 1
    s=build()["summary"];print(f"{'CHECK' if a.check else 'BUILD'} PASS method-kernel pilot: {s['libraries']} libraries, {s['axis_evidence_rows']} axis evidence rows, {s['exact_contract_input_candidates']} exact-name input candidates, {s['total_axis_evidence_vacancies']} evidence vacancies, zero gaps closed");return 0

if __name__=="__main__":raise SystemExit(main())
