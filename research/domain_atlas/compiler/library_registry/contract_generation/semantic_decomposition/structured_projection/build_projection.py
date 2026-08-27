#!/usr/bin/env python3
"""Project all structured library contributions into semantic-axis evidence and contract inputs."""

from __future__ import annotations
import argparse,collections,hashlib,json,re
from pathlib import Path
from typing import Any

HERE=Path(__file__).resolve().parent
SEMANTIC=HERE.parent
REGISTRY=HERE.parents[2]
REPO=REGISTRY.parents[3]
AS_OF="2026-08-26"

def canonical(v:Any)->str:return json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(",",":"))
def load_jsonl(p:Path)->list[dict[str,Any]]:return [json.loads(x) for x in p.read_text().splitlines() if x.strip()]
def dig(v:Any)->str:return hashlib.sha256(canonical(v).encode()).hexdigest()
def flatten(v:Any)->list[str]:
    if isinstance(v,str):return [v]
    if isinstance(v,list):return [s for x in v for s in flatten(x)]
    if isinstance(v,dict):return [s for x in v.values() for s in flatten(x)]
    return []
def at(v:dict[str,Any],path:str)->Any:
    cur:Any=v
    for part in path.split("."):
        if not isinstance(cur,dict):return None
        cur=cur.get(part)
    return cur
def matching(values:list[str],terms:list[str])->list[str]:
    pattern=re.compile(r"(?:^|[^a-z0-9])(?:"+"|".join(re.escape(x) for x in terms)+r")(?:[^a-z0-9]|$)",re.I)
    return sorted(set(x for x in values if pattern.search(x)))

def profiles()->list[dict[str,Any]]:
    return [
      {"axis":"semantic_object","direct_paths":["api_contract.types","scope.responsibilities"],"context_paths":[],"terms":[]},
      {"axis":"semantic_role","direct_paths":["library_class","api_contract.traits","api_contract.operations"],"context_paths":[],"terms":[]},
      {"axis":"identity_and_equality","direct_paths":[],"context_paths":["api_contract.types","behavior.laws","typed_inputs.decision_refs"],"terms":["identity","identifier","key","digest","canonical","equality","equal","equivalence","match","co-reference","occurrence"]},
      {"axis":"grain_and_cardinality","direct_paths":[],"context_paths":["api_contract.types","behavior.laws","typed_inputs.decision_refs"],"terms":["grain","cardinality","population","sampling","grouping","observation","record","row","batch","window","partition","many","one"]},
      {"axis":"state_and_change","direct_paths":[],"context_paths":["api_contract.types","behavior.laws","typed_inputs.decision_refs"],"terms":["state","lifecycle","transition","snapshot","version","revision","plan","attempt","job","receipt","checkpoint","history","correction"]},
      {"axis":"time","direct_paths":[],"context_paths":["api_contract.types","behavior.laws","typed_inputs.decision_refs","bounds.time"],"terms":["time","temporal","deadline","ttl","expiry","validity","recording","occurrence","window","calendar","schedule","watermark","duration","horizon"]},
      {"axis":"order_and_topology","direct_paths":[],"context_paths":["api_contract.types","behavior.laws","typed_inputs.decision_refs"],"terms":["order","sequence","graph","topology","path","causal","partition","spatial","coordinate","geometry","direction","edge","node"]},
      {"axis":"partiality_and_uncertainty","direct_paths":[],"context_paths":["api_contract.types","behavior.refusals","behavior.laws","api_contract.operations"],"terms":["missing","null","unknown","partial","uncertainty","invalid","unsupported","inconclusive","confidence","residual","censored","truncated","nan","indeterminate"]},
      {"axis":"authority_and_trust","direct_paths":["semantic_owners"],"context_paths":["api_contract.types","behavior.laws","typed_inputs.decision_refs"],"terms":["authority","authorize","policy","purpose","consent","delegation","issuer","approval","permission","entitlement","revocation","trust","mandate"]},
      {"axis":"effect_boundary","direct_paths":["effects.boundary","effects.intents","effects.receipts"],"context_paths":[],"terms":[]},
      {"axis":"representation","direct_paths":["boundaries.serialization","boundaries.abi","boundaries.anti_corruption","boundaries.dtos","api_contract.types"],"context_paths":[],"terms":[]},
      {"axis":"composition_algebra","direct_paths":[],"context_paths":["behavior.laws","api_contract.types","api_contract.operations","feature_dependency_graph.dependency_refs"],"terms":["compose","composition","merge","join","algebra","combine","fold","reduce","aggregate","monotonic","associative","commutative","idempotent","fixed point","semiring","overlay","override"]},
      {"axis":"compatibility_and_evolution","direct_paths":["evolution.compatibility","evolution.compatibility_dimensions","evolution.deprecation","evolution.migration","replacement.seams","replacement.substitution_law"],"context_paths":[],"terms":[]},
      {"axis":"resources_and_failure","direct_paths":["bounds","execution","behavior.errors","behavior.refusals"],"context_paths":[],"terms":[]},
      {"axis":"evidence_and_conformance","direct_paths":["evidence_refs","conformance","gaps"],"context_paths":[],"terms":[]},
      {"axis":"privacy_security_safety","direct_paths":[],"context_paths":["api_contract.types","behavior.laws","scope.exclusions","code_risk","evidence_refs","typed_inputs.decision_refs"],"terms":["privacy","security","safety","secret","unsafe","ffi","threat","hazard","encrypt","retention","residency","redaction","disclosure","least privilege","supply chain"]},
    ]

def build()->dict[str,Any]:
    sigs=load_jsonl(SEMANTIC/"library-semantic-signatures.jsonl")
    contribs={x["library_id"]:x for x in load_jsonl(REGISTRY/"library-contributions.jsonl")}
    coverage=json.loads((SEMANTIC/"constitution-coverage.json").read_text());bindings={x["axis"]:x for x in coverage["axis_bindings"]}
    ps={x["axis"]:x for x in profiles()};assert set(ps)==set(bindings)
    rows=[];contracts=[]
    for sig in sigs:
        lib=contribs[sig["library_ref"]];record_digest=dig(lib)
        for axis in sorted(bindings,key=lambda a:(bindings[a]["phase"],a)):
            profile=ps[axis];direct=[];context=[];matches=[]
            for path in profile["direct_paths"]:
                value=at(lib,path)
                if value not in (None,[],{},""):direct.append({"source_field":path,"value_digest":dig(value),"value_count":len(value) if isinstance(value,(list,dict)) else 1})
            for path in profile["context_paths"]:
                value=at(lib,path);values=flatten(value)
                if values:
                    context.append({"source_field":path,"value_digest":dig(value),"value_count":len(values)})
                    matches.extend({"source_field":path,"value":x} for x in matching(values,profile["terms"]))
            if direct:evidence_state="DIRECT_STRUCTURED_SOURCE_EVIDENCE_CANDIDATE_UNRATIFIED"
            elif matches:evidence_state="TARGETED_STRUCTURED_SOURCE_EVIDENCE_CANDIDATE_UNRATIFIED"
            elif context:evidence_state="GENERIC_STRUCTURAL_CONTEXT_ONLY_AXIS_EVIDENCE_VACANCY"
            else:evidence_state="AXIS_EVIDENCE_VACANCY"
            rows.append({"record_kind":"global_structured_library_axis_evidence_candidate","projection_id":f"projection.structured.{sig['library_ref'].replace('library.','')}.{axis.replace('_','-')}","edition":1,"library_ref":sig["library_ref"],"family_id":sig["family_id"],"source_gap_ref":sig["source_gap_ref"],"signature_ref":sig["signature_id"],"archetype_refs":sig["archetype_refs"],"axis":axis,"phase":bindings[axis]["phase"],"constitution_ref":bindings[axis]["constitution_ref"],"module_ref":bindings[axis]["module_ref"],"contribution_record_digest":record_digest,"upstream_source_projection":lib["source_projection"],"direct_evidence_fields":direct,"targeted_evidence":matches,"structural_context_fields":context,"evidence_state":evidence_state,"applicability_decision":"UNRESOLVED","authority_limit":"Structured source projection supersedes lexical discovery for research routing only. It cannot ratify the source schema, boundary, semantic completeness, applicability, public API or implementation.","status":"STRUCTURED_PROJECTION_NOT_AUTHORITY_DOES_NOT_CLOSE_GAP"})
        contracts.append({"record_kind":"global_exact_library_contract_input_candidate","contract_input_id":f"input.exact-contract.{sig['library_ref'].replace('library.','')}.v1","edition":1,"library_ref":sig["library_ref"],"family_id":sig["family_id"],"source_gap_ref":sig["source_gap_ref"],"archetype_refs":sig["archetype_refs"],"contribution_record_digest":record_digest,"upstream_source_projection":lib["source_projection"],"source_projection_is_canonical":bool(lib["source_projection"].get("source_schema_is_canonical",False)),"library_class_candidate":lib["library_class"],"semantic_owner_candidates":lib["semantic_owners"],"scope_candidate":lib["scope"],"typed_input_candidates":lib["typed_inputs"],"api_contract_candidate":lib["api_contract"],"behavior_candidate":lib["behavior"],"effects_candidate":lib["effects"],"boundaries_candidate":lib["boundaries"],"bounds_candidate":lib["bounds"],"execution_candidate":lib["execution"],"evolution_candidate":lib["evolution"],"conformance_candidate":lib["conformance"],"evidence_refs":lib["evidence_refs"],"dependency_feature_candidate":lib["feature_dependency_graph"],"replacement_candidate":lib["replacement"],"platform_candidate":lib["platform"],"code_risk_candidate":lib["code_risk"],"known_gaps":lib["gaps"],"remaining_gates":["upstream source schema and record authority","boundary disposition and semantic owner ratification","16-axis applicability/defaults/exceptions","exact type/trait/operation signature adjudication","laws/refusals/defaults/precedence and finite bounds","negative twins and conformance oracles","two unrelated verticals","qualified implementations and acceptance"],"status":"RICH_SOURCE_INPUT_CANDIDATE_NOT_EXACT_CONTRACT_DOES_NOT_CLOSE_GAP"})
    by_family=[]
    for family in sorted({x["family_id"] for x in rows}):
        rs=[x for x in rows if x["family_id"]==family];cs=[x for x in contracts if x["family_id"]==family];states=collections.Counter(x["evidence_state"] for x in rs)
        by_family.append({"record_kind":"family_structured_projection_readiness","readiness_id":f"readiness.structured.{family.replace('constitution.family.','')}","edition":1,"family_id":family,"libraries":len(cs),"axis_rows":len(rs),"evidence_state_counts":dict(sorted(states.items())),"rich_contract_input_candidates":len(cs),"canonical_upstream_sources":sum(x["source_projection_is_canonical"] for x in cs),"owner_decisions":0,"exact_gaps_closed":0,"status":"RICH_STRUCTURED_INPUTS_AVAILABLE_OWNER_ADJUDICATION_REQUIRED"})
    research_questions={
      "identity_and_equality":"Define subject identity, equality, canonical equivalence, co-reference, version/occurrence continuity and comparison refusals for this family.",
      "grain_and_cardinality":"Define observation, identity, analysis, update, authority, storage, partition, ordering and completeness grains plus legal regrain operations.",
      "state_and_change":"Define lifecycle identities, commands/events, legal transitions, concurrency, history cuts, corrections, snapshots and compensation semantics.",
      "order_and_topology":"Define owned total/partial/causal orders, sequence scope and graph/spatial topology plus legal reorder/projection operations.",
      "partiality_and_uncertainty":"Define information states, missingness reasons, partial/unknown completion, uncertainty carriers and propagation/refusal rules.",
      "composition_algebra":"Define exact composition operators, operand/result types, closure, identities/zeros, algebraic laws, conflicts, loss, termination and optimization permissions.",
    }
    vacancy_groups:dict[tuple[str,str],list[dict[str,Any]]]=collections.defaultdict(list)
    for row in rows:
        if row["evidence_state"]=="GENERIC_STRUCTURAL_CONTEXT_ONLY_AXIS_EVIDENCE_VACANCY":vacancy_groups[(row["family_id"],row["axis"])].append(row)
    priority={1:"P0",2:"P1",3:"P1",4:"P2",5:"P2"};vacancy_packages=[]
    for index,((family,axis),members) in enumerate(sorted(vacancy_groups.items(),key=lambda kv:(bindings[kv[0][1]]["phase"],-len(kv[1]),kv[0])),1):
        archetypes=collections.Counter(x for row in members for x in row["archetype_refs"])
        context_fields=collections.Counter(x["source_field"] for row in members for x in row["structural_context_fields"])
        vacancy_packages.append({"record_kind":"global_family_axis_targeted_evidence_work_package","work_package_id":f"work.structured-axis-evidence.{index:03d}","edition":1,"family_id":family,"axis":axis,"phase":bindings[axis]["phase"],"priority":priority[bindings[axis]["phase"]],"constitution_ref":bindings[axis]["constitution_ref"],"module_ref":bindings[axis]["module_ref"],"library_count":len(members),"library_refs":sorted(x["library_ref"] for x in members),"archetype_counts":dict(sorted(archetypes.items())),"available_generic_context_field_counts":dict(sorted(context_fields.items())),"sovereign_research_question":research_questions[axis],"required_outputs":["family-shared coordinate claims with bounded primary evidence and authority limits","applicability and prohibition decisions","library exception clusters","cross-owner collision adjudication","negative/adversarial twins","remaining vacancies and residual owners"],"completion_effect":"Upgrades generic context into targeted evidence candidates only; owner applicability, exact contracts, conformance and product acceptance remain separate.","status":"TARGETED_RESEARCH_AND_OWNER_ADJUDICATION_REQUIRED"})
    source_groups:dict[str,list[dict[str,Any]]]=collections.defaultdict(list)
    for contract in contracts:source_groups[contract["upstream_source_projection"]["path"]].append(contract)
    source_packages=[]
    for index,(path,members) in enumerate(sorted(source_groups.items()),1):
        source_file=REPO/path
        source_packages.append({"record_kind":"family_upstream_source_authority_work_package","work_package_id":f"work.source-authority.{index:03d}","edition":1,"family_id":members[0]["family_id"],"source_path":path,"source_file_sha256":hashlib.sha256(source_file.read_bytes()).hexdigest(),"source_schema_currently_canonical":False,"source_status_counts":dict(sorted(collections.Counter(x["upstream_source_projection"].get("source_status","unknown") for x in members).items())),"library_count":len(members),"library_refs":sorted(x["library_ref"] for x in members),"required_outputs":["named schema and record authority","editioned source schema and invariant validation","record-by-record retain/narrow/split/merge/rename/replace/retire disposition","field-level adopted/rejected/modified decisions","conflicting source evidence and anti-corruption decisions","canonical source digest and supersession policy"],"completion_effect":"Authorizes an editioned source corpus for exact-contract adjudication; it does not ratify library semantics, APIs, implementations or products.","status":"SOURCE_AUTHORITY_AND_SCHEMA_ADJUDICATION_REQUIRED"})
    phase_packages={phase:[x["work_package_id"] for x in vacancy_packages if x["phase"]==phase] for phase in (1,2,5)}
    dag_nodes=[
      {"node_id":"dag.semantic.constitutions","work_kind":"global_constitution_ratification","work_refs":[x["constitution_ref"] for x in coverage["phases"]],"count":5,"exit_gate":"All five constitutions have named ratifiers, bounded evidence and explicit unresolved items."},
      {"node_id":"dag.semantic.source-authority","work_kind":"family_source_authority","work_refs":[x["work_package_id"] for x in source_packages],"count":len(source_packages),"exit_gate":"Each family has an editioned canonical source schema or an explicit unresolved/rejected disposition."},
      {"node_id":"dag.semantic.targeted-evidence.phase1","work_kind":"targeted_evidence","work_refs":phase_packages[1],"count":len(phase_packages[1]),"exit_gate":"P0 identity/equality and grain/cardinality evidence vacancies are decided or remain explicitly owned."},
      {"node_id":"dag.semantic.targeted-evidence.phase2","work_kind":"targeted_evidence","work_refs":phase_packages[2],"count":len(phase_packages[2]),"exit_gate":"State/change, order/topology and partiality/uncertainty evidence vacancies are decided or remain explicitly owned."},
      {"node_id":"dag.semantic.targeted-evidence.phase5","work_kind":"targeted_evidence","work_refs":phase_packages[5],"count":len(phase_packages[5]),"exit_gate":"Composition laws, losses, conflicts and optimization permissions are decided or remain explicitly owned."},
      {"node_id":"dag.semantic.p0-family-identity-grain","work_kind":"p0_family_identity_grain_adjudication","work_refs":["p0_identity_grain/family-axis-packets.jsonl"],"count":len(by_family)*2,"exit_gate":"Every family has explicit identity/equality and grain/cardinality defaults, exceptions, evidence and unresolved owners."},
      {"node_id":"dag.semantic.global-symbol-ownership","work_kind":"global_public_symbol_ownership_adjudication","work_refs":["p0_identity_grain/global-symbol-collisions.jsonl"],"count":210,"exit_gate":"Every duplicated type, trait and operation identifier has one canonical owner/import graph or unambiguous qualified local identities."},
      {"node_id":"dag.semantic.family-applicability","work_kind":"family_axis_owner_decisions","work_refs":["applicability_matrices/family-axis-applicability-matrices.jsonl"],"count":len(by_family)*len(ps),"exit_gate":"Every family-axis has a ratified default or unresolved reason and all member exceptions are explicit."},
      {"node_id":"dag.semantic.exact-contracts","work_kind":"exact_library_contract_adjudication","work_refs":["structured_projection/exact-contract-input-candidates.jsonl"],"count":len(contracts),"exit_gate":"Every retained library has an exact editioned API, laws, refusals, bounds, evidence and dependency contract or remains rejected/unresolved."},
      {"node_id":"dag.semantic.implementation-conformance","work_kind":"implementation_and_provider_qualification","work_refs":["research/product_ontology/qualification_program"],"count":len(contracts),"exit_gate":"Exact implementations pass scoped conformance; portability claims require independent implementations."},
      {"node_id":"dag.semantic.vertical-acceptance","work_kind":"unrelated_vertical_and_product_acceptance","work_refs":["research/product_ontology/composition_pilots"],"count":len(contracts),"exit_gate":"Boundary generality and product acceptance are evidenced in at least two unrelated verticals where required."},
    ]
    dag={"record_kind":"semantic_closure_execution_dag","dag_id":"dag.semantic-closure.v1","edition":1,"as_of":AS_OF,"status":"ACTIVE_INCOMPLETE","completion_claim":False,"nodes":dag_nodes,"edges":[
      {"from":"dag.semantic.constitutions","to":"dag.semantic.targeted-evidence.phase1"},
      {"from":"dag.semantic.targeted-evidence.phase1","to":"dag.semantic.targeted-evidence.phase2"},
      {"from":"dag.semantic.targeted-evidence.phase2","to":"dag.semantic.targeted-evidence.phase5"},
      {"from":"dag.semantic.targeted-evidence.phase1","to":"dag.semantic.p0-family-identity-grain"},
      {"from":"dag.semantic.p0-family-identity-grain","to":"dag.semantic.family-applicability"},
      {"from":"dag.semantic.p0-family-identity-grain","to":"dag.semantic.global-symbol-ownership"},
      {"from":"dag.semantic.source-authority","to":"dag.semantic.global-symbol-ownership"},
      {"from":"dag.semantic.global-symbol-ownership","to":"dag.semantic.exact-contracts"},
      {"from":"dag.semantic.constitutions","to":"dag.semantic.family-applicability"},
      {"from":"dag.semantic.targeted-evidence.phase1","to":"dag.semantic.family-applicability"},
      {"from":"dag.semantic.targeted-evidence.phase2","to":"dag.semantic.family-applicability"},
      {"from":"dag.semantic.targeted-evidence.phase5","to":"dag.semantic.family-applicability"},
      {"from":"dag.semantic.source-authority","to":"dag.semantic.exact-contracts"},
      {"from":"dag.semantic.family-applicability","to":"dag.semantic.exact-contracts"},
      {"from":"dag.semantic.exact-contracts","to":"dag.semantic.implementation-conformance"},
      {"from":"dag.semantic.implementation-conformance","to":"dag.semantic.vertical-acceptance"},
    ],"parallelism":"Source-authority packages run in parallel with constitution/evidence work. Independent families and packages within a semantic phase run in parallel. Exact contracts begin per family only after that family's source authority and semantic decisions pass.","closure_law":"No downstream green state upgrades an unresolved upstream semantic, authority, evidence or acceptance gate."}
    states=collections.Counter(x["evidence_state"] for x in rows)
    summary={"program_id":"program.semantic-axis.global-structured-projection.v1","edition":1,"as_of":AS_OF,"status":"ACTIVE_OWNER_ADJUDICATION_REQUIRED","completion_claim":False,"families":len(by_family),"libraries":len(contracts),"axis_rows":len(rows),"projection_profiles":len(ps),"rich_exact_contract_input_candidates":len(contracts),"libraries_with_nonempty_types_traits_operations":sum(bool(x["api_contract_candidate"]["types"] and x["api_contract_candidate"]["traits"] and x["api_contract_candidate"]["operations"]) for x in contracts),"canonical_upstream_sources":sum(x["source_projection_is_canonical"] for x in contracts),"upstream_source_authority_work_packages":len(source_packages),"evidence_state_counts":dict(sorted(states.items())),"targeted_evidence_vacancy_axes":len({x["axis"] for x in vacancy_packages}),"targeted_evidence_work_packages":len(vacancy_packages),"generic_context_rows_requiring_targeted_evidence":sum(x["library_count"] for x in vacancy_packages),"execution_dag_nodes":len(dag_nodes),"execution_dag_edges":len(dag["edges"]),"automatic_applicability_decisions":0,"canonical_exact_gaps_closed":0,"finding":"All open libraries have rich typed source projections. Remaining work is authority, semantic adjudication, exact signature review, conformance and acceptance—not blank-slate API invention."}
    profile_doc={"record_kind":"structured_axis_projection_profile_set","profile_set_id":"profile-set.semantic-axis.structured.v1","edition":1,"as_of":AS_OF,"profiles":profiles(),"state_precedence":["DIRECT_STRUCTURED_SOURCE_EVIDENCE_CANDIDATE_UNRATIFIED","TARGETED_STRUCTURED_SOURCE_EVIDENCE_CANDIDATE_UNRATIFIED","GENERIC_STRUCTURAL_CONTEXT_ONLY_AXIS_EVIDENCE_VACANCY","AXIS_EVIDENCE_VACANCY"],"matching_limit":"Term matching is research routing only. Direct fields are structurally relevant but remain unratified. Family-specific projection profiles may narrow or override this global profile without weakening authority gates."}
    return {"rows":rows,"contracts":contracts,"families":by_family,"vacancy_packages":vacancy_packages,"source_packages":source_packages,"dag":dag,"summary":summary,"profiles":profile_doc}

def outputs()->dict[str,str]:
    b=build();files={"projection-profiles.json":json.dumps(b["profiles"],ensure_ascii=False,sort_keys=True,indent=2)+"\n","structured-axis-evidence.jsonl":"".join(canonical(x)+"\n" for x in b["rows"]),"exact-contract-input-candidates.jsonl":"".join(canonical(x)+"\n" for x in b["contracts"]),"family-readiness.jsonl":"".join(canonical(x)+"\n" for x in b["families"]),"targeted-evidence-work-packages.jsonl":"".join(canonical(x)+"\n" for x in b["vacancy_packages"]),"source-authority-work-packages.jsonl":"".join(canonical(x)+"\n" for x in b["source_packages"]),"execution-dag.json":json.dumps(b["dag"],ensure_ascii=False,sort_keys=True,indent=2)+"\n","summary.json":json.dumps(b["summary"],ensure_ascii=False,sort_keys=True,indent=2)+"\n"};manifest={n:{"sha256":hashlib.sha256(t.encode()).hexdigest(),"bytes":len(t.encode())} for n,t in files.items()};files["manifest.json"]=json.dumps({"manifest_id":"manifest.semantic-axis.global-structured-projection.v1","as_of":AS_OF,"files":manifest},sort_keys=True,indent=2)+"\n";return files

def main()->int:
    p=argparse.ArgumentParser();p.add_argument("--check",action="store_true");a=p.parse_args();stale=[]
    for n,t in outputs().items():
        q=HERE/n
        if a.check:
            if not q.is_file() or q.read_text()!=t:stale.append(n)
        else:q.write_text(t)
    if stale:print("STALE "+", ".join(stale));return 1
    s=build()["summary"];print(f"{'CHECK' if a.check else 'BUILD'} PASS global structured projection: {s['families']} families, {s['libraries']} libraries, {s['axis_rows']} axis rows, {s['rich_exact_contract_input_candidates']} rich inputs, zero gaps closed");return 0

if __name__=="__main__":raise SystemExit(main())
