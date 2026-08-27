#!/usr/bin/env python3
"""Deduplicate product-attributed library qualification subjects into exact contract scopes.

Evidence may be reused only when the semantic contract identity is exact. Compiler binding,
implementation, configuration, target occurrence and oracle/population identities remain separate
scope dimensions and must also match before an execution receipt can be reused.
"""
from __future__ import annotations
import hashlib, json
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent


def load_jsonl(path: Path):
    return [json.loads(x) for x in path.read_text(encoding='utf-8').splitlines() if x.strip()]

def canon(x): return json.dumps(x, sort_keys=True, separators=(',', ':'), ensure_ascii=False)
def digest(x): return hashlib.sha256(canon(x).encode()).hexdigest()

def main() -> int:
    subjects=load_jsonl(HERE/'library-qualification-subjects.jsonl')
    by_library=defaultdict(list)
    for s in subjects: by_library[s['abstract_library_ref']].append(s)
    scopes=[]; subject_bindings=[]; conflicts=[]
    for library_ref, rows in sorted(by_library.items()):
        fingerprints=defaultdict(list)
        for s in rows:
            semantic_payload={
                'abstract_library_ref': s['abstract_library_ref'],
                'semantic_owner_ref': s.get('semantic_owner_ref'),
                'library_class': s.get('library_class'),
                'effect_boundary': s.get('effect_boundary'),
                'provided_capability_refs': s.get('provided_capability_refs', []),
                'contract': s['contract'],
                'required_conformance_context_refs': s['required_conformance_context_refs'],
                'required_evidence_classes': s['required_evidence_classes'],
            }
            semantic_fp=digest(semantic_payload)
            fingerprints[semantic_fp].append((s, semantic_payload))
        if len(fingerprints)>1:
            conflicts.append({
                'record_kind':'contract_scope_identity_conflict',
                'abstract_library_ref':library_ref,
                'semantic_fingerprints':sorted(fingerprints),
                'subject_refs':sorted(s['subject_id'] for s in rows),
                'status':'BLOCKING_IDENTITY_CONFLICT',
                'completion_claim':False,
            })
        for semantic_fp, entries in sorted(fingerprints.items()):
            sample,payload=entries[0]
            scope_id='contractscope.'+semantic_fp[:24]
            compiler_groups=defaultdict(list)
            for s,_ in entries:
                compiler_payload={
                    'semantic_contract_scope_ref':scope_id,
                    'compiler_projection':s['compiler_projection'],
                }
                compiler_groups[digest(compiler_payload)].append(s)
            scopes.append({
                'record_kind':'semantic_contract_scope',
                'contract_scope_id':scope_id,
                'edition':1,
                'abstract_library_ref':library_ref,
                'semantic_fingerprint_sha256':semantic_fp,
                'semantic_payload':payload,
                'subject_refs':sorted(s['subject_id'] for s,_ in entries),
                'candidate_product_refs':sorted({s['candidate_id'] for s,_ in entries}),
                'compiler_binding_scope_count':len(compiler_groups),
                'reuse_law':'Semantic-law/oracle evidence may be referenced across product-attributed subjects only when this exact semantic fingerprint and evidence validity scope match. Implementation/execution evidence additionally requires exact implementation, build, configuration, target, oracle and population identities.',
                'ratification':'WITHHELD',
                'completion_claim':False,
            })
            for compiler_fp, compiler_subjects in sorted(compiler_groups.items()):
                compiler_scope_id='compilerscope.'+compiler_fp[:24]
                for s in compiler_subjects:
                    subject_bindings.append({
                        'record_kind':'qualification_subject_scope_binding',
                        'subject_id':s['subject_id'],
                        'candidate_id':s['candidate_id'],
                        'abstract_library_ref':library_ref,
                        'semantic_contract_scope_ref':scope_id,
                        'compiler_binding_scope_ref':compiler_scope_id,
                        'compiler_binding_fingerprint_sha256':compiler_fp,
                        'execution_scope_template':{
                            'implementation_artifact_digest':'REQUIRED',
                            'source_provenance_digest':'REQUIRED',
                            'dependency_lock_digest':'REQUIRED',
                            'toolchain_target_digest':'REQUIRED',
                            'configuration_digest':'REQUIRED',
                            'target_occurrence_id':'REQUIRED',
                            'oracle_edition_digest':'REQUIRED',
                            'population_or_corpus_digest':'REQUIRED',
                            'authority_scope_digest':'REQUIRED',
                            'validity_interval':'REQUIRED',
                        },
                        'execution_evidence_reuse':'PROHIBITED_UNTIL_ALL_TEMPLATE_DIMENSIONS_EXACT',
                        'completion_claim':False,
                    })
    scopes.sort(key=lambda x:x['contract_scope_id']); subject_bindings.sort(key=lambda x:x['subject_id']); conflicts.sort(key=lambda x:x['abstract_library_ref'])
    (HERE/'semantic-contract-scopes.jsonl').write_text(''.join(canon(x)+'\n' for x in scopes),encoding='utf-8')
    (HERE/'qualification-subject-scope-bindings.jsonl').write_text(''.join(canon(x)+'\n' for x in subject_bindings),encoding='utf-8')
    (HERE/'contract-scope-conflicts.jsonl').write_text(''.join(canon(x)+'\n' for x in conflicts),encoding='utf-8')
    multi=[s for s in scopes if len(s['subject_refs'])>1]
    summary={
        'report_id':'qualification_contract_scope_registry',
        'as_of':'2026-08-27',
        'completion_claim':False,
        'product_attributed_subject_count':len(subjects),
        'unique_abstract_library_ref_count':len(by_library),
        'semantic_contract_scope_count':len(scopes),
        'shared_semantic_contract_scope_count':len(multi),
        'subjects_in_shared_semantic_contract_scopes':sum(len(s['subject_refs']) for s in multi),
        'abstract_library_identity_conflict_count':len(conflicts),
        'subject_scope_binding_count':len(subject_bindings),
        'execution_evidence_reuse_currently_authorized_count':0,
        'ratified_contract_scope_count':0,
        'status':'EXACT_SCOPE_DEDUPLICATION_BUILT_RATIFICATION_AND_EXECUTION_EVIDENCE_WITHHELD',
    }
    (HERE/'contract-scope-summary.json').write_text(json.dumps(summary,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    print(json.dumps(summary,sort_keys=True)); return 0
if __name__=='__main__': raise SystemExit(main())
