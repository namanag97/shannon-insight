#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path
HERE=Path(__file__).resolve().parent

def jl(name): return [json.loads(x) for x in (HERE/name).read_text(encoding='utf-8').splitlines() if x.strip()]
def main():
    summary=json.loads((HERE/'program-work-surfaces-summary.json').read_text(encoding='utf-8'))
    b16=jl('b16-coverage-sampling-frame.jsonl'); b17=jl('b17-intent-solution-challenges.jsonl'); b18=jl('b18-human-effect-obligations.jsonl'); b19=jl('b19-system-fault-obligations.jsonl'); b20=jl('b20-invalidation-obligations.jsonl')
    errors=[]
    if summary['b16_coverage_coordinates']!=len(b16): errors.append('B16 summary drift')
    if summary['b17_seeded_solution_challenges']!=len(b17): errors.append('B17 summary drift')
    if summary['b18_human_effect_obligations']!=len(b18): errors.append('B18 summary drift')
    if summary['b19_system_fault_obligations']!=len(b19): errors.append('B19 summary drift')
    if summary['b20_invalidation_obligations']!=len(b20): errors.append('B20 summary drift')
    if not any(r.get('dimension')=='profession_occupation' and r.get('assessment_state')=='MISSING_CANONICAL_FOUNDATION' for r in b16): errors.append('B16 must expose profession/occupation foundation gap until a canonical scheme exists')
    laws={r['non_collapse_law'] for r in b18}; modes={r['scenario_mode'] for r in b18}
    if len(laws)!=8 or len(modes)!=8: errors.append('B18 law/mode matrix incomplete')
    if len(b18)!=len(b17)*8*8: errors.append('B18 obligations must equal B17 challenges x 8 laws x 8 modes')
    faults={r['fault_class'] for r in b19}
    if len(faults)!=11 or len(b19)!=len(b17)*11: errors.append('B19 fault matrix incomplete')
    changes={r['change_class'] for r in b20}; arts={r['affected_artifact_class'] for r in b20}
    if len(changes)!=13 or len(arts)!=8 or len(b20)!=13*8: errors.append('B20 invalidation matrix incomplete')
    for rows,label in [(b16,'B16'),(b17,'B17'),(b18,'B18'),(b19,'B19'),(b20,'B20')]:
        if any(r.get('completion_claim') is not False for r in rows): errors.append(label+' completion overclaim')
    if summary.get('program_gate_acceptance_results')!=0 or summary.get('completion_claim') is not False: errors.append('summary overclaim')
    if errors:
        for e in errors: print('ERROR:',e)
        return 1
    print(f"PASS program work surfaces: B16={len(b16)} coordinates, B17={len(b17)} challenges, B18={len(b18)} obligations, B19={len(b19)} faults, B20={len(b20)} invalidations; 0 acceptance claims")
    return 0
if __name__=='__main__': raise SystemExit(main())
