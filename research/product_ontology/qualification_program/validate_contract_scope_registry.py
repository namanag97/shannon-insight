#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json
from collections import defaultdict
from pathlib import Path
HERE=Path(__file__).resolve().parent

def load_jsonl(p): return [json.loads(x) for x in Path(p).read_text(encoding='utf-8').splitlines() if x.strip()]
def canon(x): return json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=False)
def digest(x): return hashlib.sha256(canon(x).encode()).hexdigest()

def main():
    errors=[]
    subjects=load_jsonl(HERE/'library-qualification-subjects.jsonl')
    scopes=load_jsonl(HERE/'semantic-contract-scopes.jsonl')
    bindings=load_jsonl(HERE/'qualification-subject-scope-bindings.jsonl')
    conflicts=load_jsonl(HERE/'contract-scope-conflicts.jsonl')
    summary=json.loads((HERE/'contract-scope-summary.json').read_text(encoding='utf-8'))
    subject_by_id={s['subject_id']:s for s in subjects}; scope_by_id={s['contract_scope_id']:s for s in scopes}
    if len(subject_by_id)!=len(subjects): errors.append('duplicate source subject id')
    if len(bindings)!=len(subjects) or {b['subject_id'] for b in bindings}!=set(subject_by_id): errors.append('every subject must bind exactly one scope')
    if len(scope_by_id)!=len(scopes): errors.append('duplicate contract scope id')
    recomputed_by_library=defaultdict(set)
    for b in bindings:
        s=subject_by_id[b['subject_id']]
        scope=scope_by_id.get(b['semantic_contract_scope_ref'])
        if not scope: errors.append(f"unknown scope {b['subject_id']}"); continue
        payload={
            'abstract_library_ref':s['abstract_library_ref'],'semantic_owner_ref':s.get('semantic_owner_ref'),
            'library_class':s.get('library_class'),'effect_boundary':s.get('effect_boundary'),
            'provided_capability_refs':s.get('provided_capability_refs',[]),'contract':s['contract'],
            'required_conformance_context_refs':s['required_conformance_context_refs'],
            'required_evidence_classes':s['required_evidence_classes'],
        }
        fp=digest(payload); recomputed_by_library[s['abstract_library_ref']].add(fp)
        if scope['semantic_fingerprint_sha256']!=fp or scope['semantic_payload']!=payload: errors.append(f"semantic fingerprint drift {b['subject_id']}")
        compiler_fp=digest({'semantic_contract_scope_ref':scope['contract_scope_id'],'compiler_projection':s['compiler_projection']})
        if b['compiler_binding_fingerprint_sha256']!=compiler_fp: errors.append(f"compiler fingerprint drift {b['subject_id']}")
        if b['execution_evidence_reuse']!='PROHIBITED_UNTIL_ALL_TEMPLATE_DIMENSIONS_EXACT': errors.append(f"premature evidence reuse {b['subject_id']}")
        if set(b['execution_scope_template'].values())!={'REQUIRED'}: errors.append(f"incomplete execution scope {b['subject_id']}")
        if b['completion_claim']: errors.append(f"completion overclaim {b['subject_id']}")
    expected_conflict_libs={lib for lib,fps in recomputed_by_library.items() if len(fps)>1}
    if {c['abstract_library_ref'] for c in conflicts}!=expected_conflict_libs: errors.append('contract conflict projection drift')
    if any(c['status']!='BLOCKING_IDENTITY_CONFLICT' or c['completion_claim'] for c in conflicts): errors.append('conflict posture drift')
    expected_unique_libs=len({s['abstract_library_ref'] for s in subjects})
    expected={
      'product_attributed_subject_count':len(subjects),'unique_abstract_library_ref_count':expected_unique_libs,
      'semantic_contract_scope_count':len(scopes),'subject_scope_binding_count':len(bindings),
      'abstract_library_identity_conflict_count':len(conflicts),'execution_evidence_reuse_currently_authorized_count':0,
      'ratified_contract_scope_count':0,
    }
    for k,v in expected.items():
        if summary.get(k)!=v: errors.append(f"summary drift {k}: {summary.get(k)} != {v}")
    if summary.get('completion_claim'): errors.append('summary completion overclaim')
    if errors:
        for e in errors: print('ERROR: '+e)
        return 1
    print(f"PASS exact contract scopes: {len(subjects)} product-attributed subjects -> {len(scopes)} semantic scopes across {expected_unique_libs} abstract library ids; {len(conflicts)} identity conflicts; evidence reuse remains withheld")
    return 0
if __name__=='__main__': raise SystemExit(main())
