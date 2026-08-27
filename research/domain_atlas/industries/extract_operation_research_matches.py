#!/usr/bin/env python3
"""Extract compact canonical-operation evidence for high-impact B07 typed-operation research.

No mapping is inferred. The output is a search aid over the committed 1,062-operation candidate
universe so semantic adjudication can compare actual definitions instead of labels alone.
"""
from __future__ import annotations
import json,re,unicodedata
from pathlib import Path
HERE=Path(__file__).resolve().parent
OPS=HERE.parent/'universes/operations/operation-candidates.jsonl'
QUERIES={
 'asof_identity_dimension_join':['asof','as-of','temporal join','join','dimension','identity'],
 'authorized_source_cut':['authorize','authorized','source cut','cut','snapshot','admit','govern'],
 'estimate_with_uncertainty':['estimate','estimation','uncertainty','confidence','interval','credible'],
 'issue_evidence_bound_proposal':['proposal','recommend','recommendation','evidence','publish','issue'],
 'observe_action_outcome':['outcome','observe','observation','effect','feedback','action'],
 'reconcile_native_grains':['reconcile','reconciliation','grain','granularity','aggregate','disaggregate'],
 'identify_quantify_stress_risk':['risk','stress','identify','quantify','scenario'],
 'trace_change_point':['trace','lineage','change point','changepoint','drift'],
}
def L(p): return [json.loads(x) for x in Path(p).read_text(encoding='utf-8').splitlines() if x.strip()]
def norm(s):
 s=unicodedata.normalize('NFKC',str(s)).casefold().replace('_',' ').replace('-',' ')
 return ' '.join(re.sub(r'[^a-z0-9]+',' ',s).split())
def main():
 ops=L(OPS); out=[]
 for qid,terms in QUERIES.items():
  scored=[]
  for op in ops:
   text=' '.join(norm(op.get(k,'')) for k in ('operation_id','name','definition','semantic_owner_candidate','family_id'))
   hits=sorted({t for t in terms if norm(t) and norm(t) in text})
   if not hits: continue
   score=sum(3 if norm(t) in norm(op.get('name','')) else 1 for t in hits)
   scored.append((score,op,hits))
  for rank,(score,op,hits) in enumerate(sorted(scored,key=lambda x:(-x[0],x[1]['operation_id']))[:40],1):
   out.append({'record_kind':'operation_research_match','query_id':qid,'rank':rank,'score':score,'matched_terms':hits,'operation_id':op['operation_id'],'name':op['name'],'family_id':op['family_id'],'operation_kind':op.get('operation_kind'),'semantic_owner_candidate':op.get('semantic_owner_candidate'),'definition':op.get('definition'),'inputs':op.get('inputs'),'outputs':op.get('outputs'),'preconditions':op.get('preconditions'),'postconditions':op.get('postconditions'),'failure_modes':op.get('failure_modes'),'completion_claim':False})
 (HERE/'operation-research-matches.jsonl').write_text(''.join(json.dumps(r,sort_keys=True)+'\n' for r in out),encoding='utf-8')
 summary={'report_id':'b07_operation_research_matches','as_of':'2026-08-27','query_count':len(QUERIES),'canonical_operation_count':len(ops),'match_rows':len(out),'semantic_decisions_created':0,'completion_claim':False}
 (HERE/'operation-research-matches-summary.json').write_text(json.dumps(summary,indent=2,sort_keys=True)+'\n',encoding='utf-8')
 print(json.dumps(summary,sort_keys=True)); return 0
if __name__=='__main__': raise SystemExit(main())
