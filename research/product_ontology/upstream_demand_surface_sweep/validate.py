#!/usr/bin/env python3
import json
from pathlib import Path
HERE=Path(__file__).resolve().parent
def load(n): return [json.loads(x) for x in (HERE/n).read_text().splitlines() if x.strip()]
sources={r['source_id'] for r in load('evidence.jsonl')}
surfaces=load('demand-surfaces.jsonl'); laws=load('universal-laws.jsonl'); boundaries=load('boundary-hypotheses.jsonl'); contracts=load('library-contract-hypotheses.jsonl'); packs=load('vertical-pack-requirements.jsonl')
assert len(surfaces)==8 and all(r['required_artifact_classes'] for r in surfaces)
assert len(laws)>=12 and all(set(r['source_refs'])<=sources for r in laws)
assert len(boundaries)==10 and all(set(r['source_refs'])<=sources for r in boundaries)
assert len(contracts)>=50 and len({r['contract_hypothesis_id'] for r in contracts})==len(contracts)
assert len(packs)==5
assert all(r['completion_claim'] is False for rows in (laws,boundaries,contracts,packs) for r in rows)
print(f"PASS upstream demand-surface sweep: {len(sources)} sources, {len(surfaces)} detectors, {len(laws)} laws, {len(boundaries)} boundaries, {len(contracts)} contract seams, {len(packs)} vertical deltas")
