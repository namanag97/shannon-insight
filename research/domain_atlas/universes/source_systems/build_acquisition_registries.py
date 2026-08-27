#!/usr/bin/env python3
"""Aggregate per-execution source acquisition packets into canonical B08 registries.

Each execution directory may publish these exact files:
  provider-offer.json
  access-surface.json
  connector-capability.json
  acquisition-plan.json
  governed-data-cut.json

The aggregator rejects duplicate identities with different bodies and never upgrades any
qualification/authority state. Source occurrences are aggregated separately by
build_occurrence_registry.py because they have their own evidence admission rules.
"""
from __future__ import annotations
import hashlib,json
from pathlib import Path
HERE=Path(__file__).resolve().parent
EXEC=HERE/'executions'
KINDS={
 'provider-offer.json':('offer_id','provider-product-offers.jsonl'),
 'access-surface.json':('surface_id','access-surfaces.jsonl'),
 'connector-capability.json':('adapter_id','connector-capabilities.jsonl'),
 'acquisition-plan.json':('plan_id','acquisition-plans.jsonl'),
 'governed-data-cut.json':('cut_id','governed-data-cuts.jsonl'),
}
def canonical(x): return json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=False)
def main():
    counts={}; refused=[]
    for filename,(idfield,outfile) in KINDS.items():
        by_id={}
        for path in sorted(EXEC.glob(f'*/{filename}')):
            row=json.loads(path.read_text(encoding='utf-8'))
            ident=row[idfield]
            body=canonical(row)
            if ident in by_id and by_id[ident][0]!=body:
                refused.append({'identity':ident,'kind':filename,'first':by_id[ident][1],'conflict':str(path.relative_to(HERE)),'reason':'DUPLICATE_IDENTITY_DIFFERENT_BODY'})
                continue
            by_id[ident]=(body,str(path.relative_to(HERE)))
        rows=[json.loads(v[0]) for _,v in sorted(by_id.items())]
        (HERE/outfile).write_text(''.join(json.dumps(r,sort_keys=True)+'\n' for r in rows),encoding='utf-8')
        counts[outfile]=len(rows)
    summary={'report_id':'source_acquisition_canonical_registries','as_of':'2026-08-27','registry_counts':counts,'refused_packet_count':len(refused),'refused_packets':refused,'completion_claim':False,'status':'AGGREGATED_EXECUTION_PACKETS_AUTHORITY_AND_QUALIFICATION_UNCHANGED'}
    (HERE/'acquisition-registry-summary.json').write_text(json.dumps(summary,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    print(json.dumps(summary,sort_keys=True)); return 1 if refused else 0
if __name__=='__main__': raise SystemExit(main())
