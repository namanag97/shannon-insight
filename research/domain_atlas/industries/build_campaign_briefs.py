#!/usr/bin/env python3
"""Materialize compact per-campaign B07 research briefs from exact unresolved queue rows."""
from __future__ import annotations
import json,re
from collections import defaultdict
from pathlib import Path
HERE=Path(__file__).resolve().parent
OUT=HERE/'campaign_briefs'
def jl(p): return [json.loads(x) for x in Path(p).read_text(encoding='utf-8').splitlines() if x.strip()]
def slug(s): return re.sub(r'[^a-z0-9]+','_',s.casefold()).strip('_')
def main():
    assignments=jl(HERE/'canonical-reference-unresolved-campaign-assignments.jsonl')
    by=defaultdict(list)
    for a in assignments: by[a['research_campaign_ref']].append(a)
    OUT.mkdir(exist_ok=True)
    expected=set()
    index=[]
    for cid,members in sorted(by.items()):
        name=slug(cid.removeprefix('campaign.b07.'))+'.jsonl'; expected.add(name)
        rows=[{'queue_id':m['queue_id'],'raw_ref':m['raw_ref'],'reference_domain':m['reference_domain'],'occurrence_count':m['occurrence_count'],'origin_packs':m['origin_packs'],'status':m['status']} for m in sorted(members,key=lambda x:(-x['occurrence_count'],x['raw_ref'],x['queue_id']))]
        (OUT/name).write_text(''.join(json.dumps(r,sort_keys=True)+'\n' for r in rows),encoding='utf-8')
        index.append({'record_kind':'b07_campaign_brief_index','campaign_id':cid,'brief_path':'research/domain_atlas/industries/campaign_briefs/'+name,'distinct_reference_count':len(rows),'occurrence_count':sum(r['occurrence_count'] for r in rows),'top_raw_refs':[r['raw_ref'] for r in rows[:10]],'completion_claim':False})
    for p in OUT.glob('*.jsonl'):
        if p.name not in expected: p.unlink()
    (HERE/'campaign-brief-index.jsonl').write_text(''.join(json.dumps(r,sort_keys=True)+'\n' for r in sorted(index,key=lambda r:(-r['distinct_reference_count'],r['campaign_id']))),encoding='utf-8')
    summary={'report_id':'b07_campaign_briefs','as_of':'2026-08-27','campaign_count':len(index),'reference_count':len(assignments),'largest_campaigns':[{'campaign_id':r['campaign_id'],'distinct_reference_count':r['distinct_reference_count'],'occurrence_count':r['occurrence_count']} for r in sorted(index,key=lambda r:-r['distinct_reference_count'])[:10]],'completion_claim':False}
    (HERE/'campaign-brief-summary.json').write_text(json.dumps(summary,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    print(json.dumps(summary,sort_keys=True)); return 0
if __name__=='__main__': raise SystemExit(main())
