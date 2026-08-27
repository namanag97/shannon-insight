#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path
HERE=Path(__file__).resolve().parent

def load_jsonl(p): return [json.loads(x) for x in Path(p).read_text(encoding='utf-8').splitlines() if x.strip()]
def main():
    source=json.loads((HERE/'coverage-gaps.json').read_text(encoding='utf-8'))
    rows=load_jsonl(HERE/'effective-gap-frontier.jsonl')
    summary=json.loads((HERE/'effective-gap-summary.json').read_text(encoding='utf-8'))
    expected=[g['gap_id'] for g in source['gaps']]
    assert [r['gap_id'] for r in rows]==expected
    assert len(rows)==len(expected)==18
    assert all(r['completion_claim'] is False for r in rows)
    assert summary['historical_gap_count']==18 and summary['end_to_end_closed_gap_count']==0 and summary['completion_claim'] is False
    dsg2=next(r for r in rows if r['gap_id']=='DSG-002')
    assert dsg2['effective_status']=='RESEARCH_PROFILE_TRANCHE_RESOLVED_DOWNSTREAM_GATED'
    for ref in dsg2['evidence_refs']:
        assert (HERE.parents[3]/ref).exists(), ref
    dsg10=next(r for r in rows if r['gap_id']=='DSG-010')
    assert dsg10['effective_status']=='REHOMED_GOVERNED_EXTENSION_PACKS'
    assert not any(r['effective_status'] in {'CLOSED','COMPLETE','SATISFIED'} for r in rows)
    print('PASS effective data-shape gap frontier: 18/18 historical gaps dispositioned; DSG-002 narrowed; no end-to-end closure claimed')
    return 0
if __name__=='__main__': raise SystemExit(main())
