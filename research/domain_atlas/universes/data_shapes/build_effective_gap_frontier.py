#!/usr/bin/env python3
"""Rebase the historical data-shape gap ledger onto current committed work.

The historical gaps remain intact. This projection narrows their current meaning without
claiming semantic ratification, implementation qualification, independent review, or saturation.
"""
from __future__ import annotations
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent

DISPOSITIONS={
'DSG-001':('OPEN_SEMANTIC_AND_EXECUTION','B09_DATA_SHAPE_OPERATION_TOTALITY','carrier interoperability matrix and round-trip conformance still open'),
'DSG-002':('RESEARCH_PROFILE_TRANCHE_RESOLVED_DOWNSTREAM_GATED','B09_DATA_SHAPE_OPERATION_TOTALITY','seven versioned equality/order/canonicalization profiles and executable local boundary vectors now exist; full UCA/RDFC suites, independent implementations and authority remain open'),
'DSG-003':('OPEN_DEPENDS_ON_VERTICAL_REFERENCE_CLOSURE','B07_INDUSTRY_CANONICAL_REFERENCE_CLOSURE','vertical quantity/code/observation/composite extensions must resolve or emit typed extension gaps'),
'DSG-004':('OPEN_SEMANTIC_AND_EXECUTION','B09_DATA_SHAPE_OPERATION_TOTALITY','operation overload pre/postconditions, residuals, complexity and exact failure algebra remain incomplete'),
'DSG-005':('OPEN_SEMANTIC','B09_DATA_SHAPE_OPERATION_TOTALITY','RDF/property/temporal/hypergraph relation-level loss/refusal crosswalks remain incomplete'),
'DSG-006':('OPEN_SEMANTIC_AND_CONFORMANCE','B09_DATA_SHAPE_OPERATION_TOTALITY','dynamic CRS, coordinate epoch, moving geometry, topology, mesh and coverage evolution laws remain incomplete'),
'DSG-007':('OPEN_EXTENSION_FRONTIER','B09_DATA_SHAPE_OPERATION_TOTALITY','global media/scientific/domain representation inventory is intentionally open and must map with declared loss'),
'DSG-008':('OPEN_SEMANTIC_AND_METHOD_CONFORMANCE','B09_DATA_SHAPE_OPERATION_TOTALITY','dependence, compound/imprecise probability, censoring/truncation and propagation profiles remain incomplete'),
'DSG-009':('OPEN_DOWNSTREAM_IMPLEMENTATION_AND_PORTABILITY','B10_IMPLEMENTATION_IDENTITY_AND_BUILD','solver/simulator transformations, tolerances, certificates and checkpoint portability require concrete provider qualification and differential execution'),
'DSG-010':('REHOMED_GOVERNED_EXTENSION_PACKS','B14_TWO_VERTICAL_EXECUTED_ACCEPTANCE','horizontal core intentionally remains jurisdiction-law-neutral; legal/anonymization sufficiency belongs to governed jurisdiction/vertical packs with accountable legal authority'),
'DSG-011':('OPEN_DOWNSTREAM_PHYSICAL_EVIDENCE','B13_PHYSICAL_BINDING_SLO_SECURITY_COST','shape/operation/workload performance and cost envelopes require measured provider occurrences'),
'DSG-012':('OPEN_INDEPENDENT_REVIEW_REQUIRED','B15_TWO_RELEASE_CHANGE_AND_RATIFICATION','open-world saturation requires disjoint independent review and repeated no-new-core cycles; agent self-attestation cannot close it'),
'DSG-013':('OPEN_SOURCE_OCCURRENCE_AND_CONFORMANCE','B08_SOURCE_SYSTEM_AND_OCCURRENCE_CLOSURE','mailbox identity/threading/authentication/export fidelity requires at least two independent mail-store occurrences and adversarial round trips'),
'DSG-014':('OPEN_SOURCE_OCCURRENCE_AND_CONFORMANCE','B08_SOURCE_SYSTEM_AND_OCCURRENCE_CLOSURE','document logical/layout/render/extraction fidelity requires independent format implementations and adversarial corpora'),
'DSG-015':('OPEN_GOVERNED_EXTENSION_PACKS','B09_DATA_SHAPE_OPERATION_TOTALITY','language/ABI/package/executable/configuration semantics require explicit extension packs and typed unsupported constructs'),
'DSG-016':('OPEN_SECURITY_LAWS_AND_EXECUTION','B11_EXACT_SCOPE_CONFORMANCE_AND_INDEPENDENT_APPRAISAL','archive traversal/link/bomb/encryption/active-content policies require executable law oracles and two bounded implementations'),
'DSG-017':('OPEN_CROSSWALK_EXECUTION','B11_EXACT_SCOPE_CONFORMANCE_AND_INDEPENDENT_APPRAISAL','every representation crosswalk still needs positive, negative, boundary and lossy round-trip receipts'),
'DSG-018':('OPEN_COMPILER_ENFORCEMENT','B11_EXACT_SCOPE_CONFORMANCE_AND_INDEPENDENT_APPRAISAL','invalid-inference rows must be compiled into ingestion/conversion/planning refusal tests'),
}

def main():
    source=json.loads((HERE/'coverage-gaps.json').read_text(encoding='utf-8'))
    profiles=(HERE/'semantic-equality-profiles.jsonl')
    vectors=(HERE/'semantic-equality-test-vectors.jsonl')
    rows=[]
    for gap in source['gaps']:
        gid=gap['gap_id']
        status,batch,remaining=DISPOSITIONS[gid]
        refs=[]
        if gid=='DSG-002':
            if not profiles.exists() or not vectors.exists(): raise SystemExit('DSG-002 cannot be narrowed without committed profiles and vectors')
            refs=['research/domain_atlas/universes/data_shapes/semantic-equality-profiles.jsonl','research/domain_atlas/universes/data_shapes/semantic-equality-test-vectors.jsonl','research/domain_atlas/universes/data_shapes/validate_semantic_equality_profiles.py']
        rows.append({'record_kind':'effective_data_shape_gap_disposition','gap_id':gid,'historical_area':gap['area'],'historical_severity':gap['severity'],'effective_status':status,'owning_batch':batch,'remaining_work':remaining,'evidence_refs':refs,'completion_claim':False})
    (HERE/'effective-gap-frontier.jsonl').write_text(''.join(json.dumps(r,sort_keys=True)+'\n' for r in rows),encoding='utf-8')
    counts={}
    for r in rows: counts[r['effective_status']]=counts.get(r['effective_status'],0)+1
    summary={'report_id':'data_shape_effective_gap_frontier','as_of':'2026-08-27','historical_gap_count':len(rows),'effective_status_counts':dict(sorted(counts.items())),'end_to_end_closed_gap_count':0,'completion_claim':False,'status':'CURRENT_GAP_DISPOSITIONS_EXPLICIT_NO_END_TO_END_COMPLETION_CLAIM'}
    (HERE/'effective-gap-summary.json').write_text(json.dumps(summary,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    print(json.dumps(summary,sort_keys=True));return 0
if __name__=='__main__': raise SystemExit(main())
