#!/usr/bin/env python3
"""Factor unresolved typed-operation refs by vertical-pack reuse.

This finds pipeline vocabulary repeated across many cases in the same pack. It is prioritization
only: common wording does not imply semantic equivalence or a new universal operation.
"""
from __future__ import annotations
import json
from collections import defaultdict
from pathlib import Path
HERE=Path(__file__).resolve().parent

def L(p): return [json.loads(x) for x in Path(p).read_text(encoding='utf-8').splitlines() if x.strip()]
def J(p): return json.loads(Path(p).read_text(encoding='utf-8'))
def main():
    queue=L(HERE/'canonical-reference-review-queue.jsonl')
    manual=L(HERE/'canonical-reference-adjudications.jsonl')
    auto=L(HERE/'canonical-reference-auto-alias-candidates.jsonl')
    current=L(HERE/'canonical-reference-current-method-candidates.jsonl')
    resolved={r['queue_id'] for r in manual+auto+current}
    audit=J(HERE/'integration-audit.json')
    pack_cases={p['pack_id']:p['cases'] for p in audit['packs']}
    rows=[]
    for r in queue:
        if r['reference_domain']!='typed_operation' or r['queue_id'] in resolved: continue
        for pack in r.get('origin_packs',[]):
            cases=pack_cases.get(pack)
            if not cases: continue
            # occurrence_count is global; for multi-pack refs this is only an upper bound on pack reuse.
            # Single-pack refs provide exact pack-local coverage and are the high-confidence batching surface.
            if len(r.get('origin_packs',[]))!=1: continue
            coverage=min(1.0,r['occurrence_count']/cases)
            if coverage < 0.25: continue
            rows.append({'record_kind':'b07_pack_common_operation_frontier','pack_id':pack,'pack_case_count':cases,'queue_id':r['queue_id'],'raw_ref':r['raw_ref'],'occurrence_count':r['occurrence_count'],'case_coverage_ratio':round(coverage,6),'coverage_band':'all_cases' if coverage==1 else ('majority' if coverage>=0.5 else 'quarter_to_half'),'status':'OPEN_RESEARCH','completion_claim':False})
    rows.sort(key=lambda x:(x['pack_id'],-x['case_coverage_ratio'],-x['occurrence_count'],x['raw_ref']))
    (HERE/'pack-common-operation-frontier.jsonl').write_text(''.join(json.dumps(r,sort_keys=True)+'\n' for r in rows),encoding='utf-8')
    by=defaultdict(list)
    for r in rows: by[r['pack_id']].append(r)
    summary={'report_id':'b07_pack_common_operation_frontier','as_of':'2026-08-27','completion_claim':False,'pack_count':len(pack_cases),'common_operation_rows':len(rows),'packs':[]}
    for pack in sorted(pack_cases):
        rs=by.get(pack,[])
        summary['packs'].append({'pack_id':pack,'case_count':pack_cases[pack],'common_operation_rows':len(rs),'all_case_operation_rows':sum(r['coverage_band']=='all_cases' for r in rs),'represented_occurrences':sum(r['occurrence_count'] for r in rs),'top_refs':[{'queue_id':r['queue_id'],'raw_ref':r['raw_ref'],'occurrence_count':r['occurrence_count'],'coverage_ratio':r['case_coverage_ratio']} for r in rs[:20]]})
    (HERE/'pack-common-operation-summary.json').write_text(json.dumps(summary,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    print(json.dumps(summary,sort_keys=True)); return 0
if __name__=='__main__': raise SystemExit(main())
