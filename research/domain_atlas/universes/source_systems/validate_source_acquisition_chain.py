#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path
HERE=Path(__file__).resolve().parent

def load_jsonl(name): return [json.loads(x) for x in (HERE/name).read_text(encoding='utf-8').splitlines() if x.strip()]
def main():
    errors=[]
    classes={r['class_id'] for r in load_jsonl('source-classes.jsonl')}
    occurrences={r['occurrence_id']:r for r in load_jsonl('source-occurrences.jsonl')}
    offers={r['offer_id']:r for r in load_jsonl('provider-product-offers.jsonl')}
    surfaces={r['surface_id']:r for r in load_jsonl('access-surfaces.jsonl')}
    connectors={r['adapter_id']:r for r in load_jsonl('connector-capabilities.jsonl')}
    plans={r['plan_id']:r for r in load_jsonl('acquisition-plans.jsonl')}
    cuts={r['cut_id']:r for r in load_jsonl('governed-data-cuts.jsonl')}
    topology=json.loads((HERE/'source-acquisition-topology.json').read_text(encoding='utf-8'))
    reference_summary=json.loads((HERE/'source-acquisition-reference-summary.json').read_text(encoding='utf-8'))
    registry_summary=json.loads((HERE/'acquisition-registry-summary.json').read_text(encoding='utf-8'))
    if len(topology['nodes'])!=7: errors.append('topology must retain seven distinct identities')
    kinds=[n['kind'] for n in topology['nodes']]
    if len(kinds)!=len(set(kinds)): errors.append('topology node identity duplicated')
    if len(topology['forbidden_collapses'])<10: errors.append('non-collapse law set too weak')
    for o in offers.values():
        if not set(o['source_class_refs'])<=classes: errors.append(f"{o['offer_id']}: unknown source class")
        if o.get('completion_claim') is not False: errors.append(f"{o['offer_id']}: completion overclaim")
    for s in surfaces.values():
        if s['occurrence_ref'] not in occurrences: errors.append(f"{s['surface_id']}: unknown occurrence")
        if s.get('completion_claim') is not False: errors.append(f"{s['surface_id']}: completion overclaim")
    for c in connectors.values():
        if not set(c['source_class_ids'])<=classes: errors.append(f"{c['adapter_id']}: unknown source class")
        if not c['conformance_receipts']: errors.append(f"{c['adapter_id']}: no conformance receipts")
    for p in plans.values():
        if p['occurrence_ref'] not in occurrences: errors.append(f"{p['plan_id']}: unknown occurrence")
        if p['access_surface_ref'] not in surfaces: errors.append(f"{p['plan_id']}: unknown access surface")
        if p['connector_ref'] not in connectors: errors.append(f"{p['plan_id']}: unknown connector")
        if not set(p['requested_source_class_refs'])<=classes: errors.append(f"{p['plan_id']}: unknown requested class")
        if p.get('completion_claim') is not False: errors.append(f"{p['plan_id']}: completion overclaim")
    for c in cuts.values():
        if c['occurrence_ref'] not in occurrences: errors.append(f"{c['cut_id']}: unknown occurrence")
        if c['acquisition_plan_ref'] not in plans: errors.append(f"{c['cut_id']}: unknown plan")
        plan=plans.get(c['acquisition_plan_ref'])
        if plan and c['occurrence_ref']!=plan['occurrence_ref']: errors.append(f"{c['cut_id']}: occurrence differs from plan")
        lineage=c['lineage']
        if lineage['source_occurrence']!=c['occurrence_ref']: errors.append(f"{c['cut_id']}: lineage occurrence drift")
        if plan and lineage['access_surface']!=plan['access_surface_ref']: errors.append(f"{c['cut_id']}: lineage surface drift")
        if plan and lineage['connector']!=plan['connector_ref']: errors.append(f"{c['cut_id']}: lineage connector drift")
        if plan and lineage['plan']!=plan['plan_id']: errors.append(f"{c['cut_id']}: lineage plan drift")
        ri=c['record_identity']
        if ri.get('population_digest_basis')=='PHYSICAL_DATABASE_BYTES_NOT_LOGICAL_ROWSET' and ri.get('logical_rowset_digest') is not None:
            errors.append(f"{c['cut_id']}: physical digest falsely paired with logical rowset digest")
        if c['completeness']['state']=='COMPLETE_FOR_DECLARED_SCOPE' and not c['completeness']['known_residuals']:
            errors.append(f"{c['cut_id']}: bounded completeness lacks residuals")
        if c.get('completion_claim') is not False: errors.append(f"{c['cut_id']}: completion overclaim")
    registry_counts=registry_summary['registry_counts']
    if registry_counts['provider-product-offers.jsonl']!=len(offers) or registry_counts['access-surfaces.jsonl']!=len(surfaces) or registry_counts['connector-capabilities.jsonl']!=len(connectors) or registry_counts['acquisition-plans.jsonl']!=len(plans) or registry_counts['governed-data-cuts.jsonl']!=len(cuts):
        errors.append('summary count drift')
    if registry_summary['refused_packet_count'] or registry_summary['completion_claim']: errors.append('registry summary refusal or promotion overclaim')
    # The reference summary is deliberately scoped to one SQLite exemplar; it
    # must not be compared with the growing canonical occurrence registry.
    if any(reference_summary[key] != 1 for key in ('source_classes','provider_offers','source_occurrences','access_surfaces','connector_implementations','acquisition_plans','governed_data_cuts')):
        errors.append('SQLite reference summary scope drift')
    if reference_summary['production_qualified'] or reference_summary['independently_appraised'] or reference_summary['completion_claim']: errors.append('reference summary promotion overclaim')
    try:
        import jsonschema
        for filename,schema_name in [('provider-product-offers.jsonl','provider-product-offer.schema.json'),('access-surfaces.jsonl','access-surface.schema.json'),('connector-capabilities.jsonl','connector-capability.schema.json'),('acquisition-plans.jsonl','acquisition-plan.schema.json'),('governed-data-cuts.jsonl','governed-data-cut.schema.json')]:
            schema=json.loads((HERE/schema_name).read_text(encoding='utf-8'))
            for row in load_jsonl(filename): jsonschema.Draft202012Validator(schema).validate(row)
    except ImportError:
        pass
    if errors:
        for e in errors: print('ERROR: '+e)
        return 1
    print(f"PASS source acquisition chain: classes={len(classes)} offers={len(offers)} occurrences={len(occurrences)} surfaces={len(surfaces)} connectors={len(connectors)} plans={len(plans)} cuts={len(cuts)}; seven identities remain non-collapsed")
    return 0
if __name__=='__main__': raise SystemExit(main())
