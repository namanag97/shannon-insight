#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json
from pathlib import Path
HERE=Path(__file__).resolve().parent

def load_jsonl(p): return [json.loads(x) for x in Path(p).read_text(encoding='utf-8').splitlines() if x.strip()]
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    errors=[]
    classes={r['class_id'] for r in load_jsonl(HERE/'source-classes.jsonl')}
    rows=load_jsonl(HERE/'source-occurrences.jsonl')
    summary=json.loads((HERE/'occurrence-registry-summary.json').read_text(encoding='utf-8'))
    if len(rows)!=len({r['occurrence_id'] for r in rows}): errors.append('duplicate occurrence ids')
    for r in rows:
        if r['source_class_id'] not in classes: errors.append(f"unknown class {r['occurrence_id']}")
        packet=HERE/r['execution_packet_ref']; op=packet/'source-occurrence.json'; rp=packet/'probe-receipt.json'; sp=packet/'summary.json'
        if not all(p.exists() for p in (op,rp,sp)): errors.append(f"missing packet files {r['occurrence_id']}"); continue
        if sha(op)!=r['occurrence_sha256'] or sha(rp)!=r['probe_receipt_sha256'] or sha(sp)!=r['summary_sha256']: errors.append(f"digest drift {r['occurrence_id']}")
        occ=json.loads(op.read_text(encoding='utf-8'))
        if occ['occurrence_id']!=r['occurrence_id'] or occ['source_class_id']!=r['source_class_id']: errors.append(f"identity drift {r['occurrence_id']}")
        if r['production_qualified'] or r['independently_appraised'] or r['completion_claim']: errors.append(f"registry overclaim {r['occurrence_id']}")
    expected={'retained_occurrence_count':len(rows),'source_class_count_with_retained_occurrence':len({r['source_class_id'] for r in rows}),'production_qualified_occurrence_count':0,'independently_appraised_occurrence_count':0}
    for k,v in expected.items():
        if summary.get(k)!=v: errors.append(f"summary drift {k}")
    if summary.get('completion_claim'): errors.append('summary completion overclaim')
    if errors:
        for e in errors: print('ERROR: '+e)
        return 1
    print(f"PASS source occurrence registry: {len(rows)} retained occurrences across {expected['source_class_count_with_retained_occurrence']} source classes; production qualification/appraisal withheld")
    return 0
if __name__=='__main__': raise SystemExit(main())
