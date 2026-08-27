#!/usr/bin/env python3
"""Factor unresolved B07 references into semantic research campaigns without inferring mappings.

Every raw queue record remains independently adjudicated. Campaign assignment is only workflow
routing, never a canonical-reference verdict.
"""
from __future__ import annotations
import hashlib,json,re,unicodedata
from collections import Counter,defaultdict
from pathlib import Path

HERE=Path(__file__).resolve().parent

def jl(p): return [json.loads(x) for x in Path(p).read_text(encoding='utf-8').splitlines() if x.strip()]
def norm(s):
    s=unicodedata.normalize('NFKC',str(s)).casefold().replace('_',' ').replace('-',' ')
    return ' '.join(re.sub(r'[^a-z0-9]+',' ',s).split())
def hid(s): return hashlib.sha256(s.encode()).hexdigest()[:16]

METHOD_RULES=[
 ('causal_experimental',('causal','difference in difference','instrumental','propensity','synthetic control','randomized','experiment','treatment effect','uplift','counterfactual')),
 ('forecast_time_series',('forecast','time series','arima','ets','exponential smoothing','seasonal','trend','nowcast','demand prediction')),
 ('statistical_inference',('hypothesis','regression','anova','distribution','confidence','bayesian','bootstrap','sampling','variance','correlation','estimation','statistical')),
 ('survival_reliability_risk',('survival','hazard','reliability','failure rate','actuarial','credit risk','market risk','var','expected shortfall','default')),
 ('optimization_operations_research',('optim','linear program','integer program','constraint','routing','scheduling','allocation','knapsack','network flow','inventory policy')),
 ('simulation_scenario',('simulation','monte carlo','discrete event','agent based','scenario','digital twin')),
 ('process_object_centric',('process mining','conformance','process discovery','case variant','object centric','bottleneck','cycle time')),
 ('graph_network',('graph','network','centrality','community','path','link prediction','knowledge graph')),
 ('geospatial_spatiotemporal',('spatial','geospatial','geographic','gis','raster','geocod','trajectory','location','kriging','hotspot')),
 ('anomaly_change_quality',('anomaly','outlier','change point','control chart','cusum','spc','quality control','drift detection')),
 ('predictive_machine_learning',('machine learning','classification','classifier','prediction','predictive','neural','random forest','gradient boosting','clustering','embedding','feature selection')),
 ('text_document_language',('text','document','nlp','language','topic model','sentiment','entity extraction','information extraction','ocr')),
 ('signal_image_media',('signal','image','video','audio','spectral','wavelet','computer vision','segmentation')),
 ('descriptive_metric_decomposition',('descriptive','aggregation','metric','ratio','rate','decomposition','drilldown','pareto','cohort','funnel')),
 ('planning_decision_analysis',('planning','decision analysis','multi criteria','mcda','portfolio','what if','sensitivity analysis','scenario comparison')),
]
OP_RULES=[
 ('identity_join_alignment',('join','match','link','identity','align','map','crosswalk','resolve')),
 ('filter_select_project',('filter','select','project','slice','subset','sample')),
 ('aggregate_measure',('aggregate','sum','count','average','mean','metric','measure','rollup','group')),
 ('transform_normalize_convert',('transform','normalize','convert','parse','encode','decode','cast','reshape','pivot','unpivot')),
 ('temporal_window_order',('window','time','temporal','order','sort','watermark','as of','lag','lead')),
 ('quality_validate_reconcile',('validate','quality','reconcile','compare','check','verify','conformance','completeness')),
 ('estimate_infer_score',('estimate','infer','score','predict','classify','detect','test')),
 ('optimize_plan_schedule',('optimize','plan','schedule','allocate','route','solve')),
 ('simulate_generate',('simulate','generate','sample','scenario')),
 ('publish_export_present',('publish','export','report','render','present','visual','notify')),
 ('govern_authorize_effect',('authorize','approve','admit','policy','grant','revoke','recall','execute','dispatch','effect')),
 ('persist_version_commit',('persist','store','commit','snapshot','version','restore','delete','migrate')),
]
SOURCE_RULES=[
 ('enterprise_application',('erp','crm','hr','hcm','wms','tms','mes','eam','accounting','billing','claims','trade capture','order management')),
 ('operational_database',('database','postgres','mysql','oracle db','sql server','mongodb','cassandra','redis','neo4j')),
 ('analytical_repository',('warehouse','lakehouse','data lake','cube','semantic layer','feature store')),
 ('file_object_content',('file','csv','excel','spreadsheet','parquet','avro','object store','s3','document repository')),
 ('api_remote_service',('api','odata','graphql','rest','soap','web service','endpoint')),
 ('event_messaging_cdc',('kafka','event','queue','cdc','change data','webhook','message bus','mqtt')),
 ('collaboration_productivity',('email','calendar','chat','slack','teams','sharepoint','wiki','form')),
 ('telemetry_observability',('log','metric','trace','telemetry','clickstream','web analytics','mobile analytics')),
 ('industrial_iot',('sensor','scada','historian','opc','plc','iot','meter','machine','equipment')),
 ('scientific_regulated',('ehr','clinical','lims','instrument','genomic','laboratory','regulatory','filing')),
 ('geospatial_media',('gis','raster','satellite','image','video','audio','cad','bim','point cloud','weather')),
 ('public_reference',('public data','government register','reference feed','market data','filing','catalog')),
]

def choose(text,rules,default):
    n=norm(text); hits=[]
    for name,terms in rules:
        score=sum(1 for t in terms if t in n)
        if score: hits.append((score,name))
    if not hits:return default
    hits.sort(key=lambda x:(-x[0],x[1])); return hits[0][1]

def main():
    queue=jl(HERE/'canonical-reference-review-queue.jsonl')
    resolved={r['queue_id'] for r in jl(HERE/'canonical-reference-adjudications.jsonl')}
    resolved|={r['queue_id'] for r in jl(HERE/'canonical-reference-auto-alias-candidates.jsonl')}
    p=HERE/'canonical-reference-current-method-candidates.jsonl'
    if p.exists(): resolved|={r['queue_id'] for r in jl(p)}
    remaining=[q for q in queue if q['queue_id'] not in resolved]
    assignments=[]; grouped=defaultdict(list)
    for q in remaining:
        d=q['reference_domain']; raw=q['raw_ref']
        if d=='analytical_practice': campaign=choose(raw,METHOD_RULES,'method_other_specialist')
        elif d=='typed_operation': campaign=choose(raw,OP_RULES,'operation_other_specialist')
        elif d=='source_system_class': campaign=choose(raw,SOURCE_RULES,'source_other_specialist')
        elif d=='industry_classification': campaign='industry_pack.'+'+'.join(sorted(q.get('origin_packs',[])))
        else: campaign='other'
        cid=f"campaign.b07.{d}.{campaign}"
        row={'record_kind':'canonical_reference_research_campaign_assignment','assignment_id':'b07assign.'+hid(q['queue_id']),'queue_id':q['queue_id'],'reference_domain':d,'raw_ref':raw,'occurrence_count':q['occurrence_count'],'origin_packs':q.get('origin_packs',[]),'research_campaign_ref':cid,'assignment_purpose':'WORK_ROUTING_ONLY','canonical_mapping_inferred':False,'status':'OPEN_SEMANTIC_RESEARCH','completion_claim':False}
        assignments.append(row); grouped[cid].append(row)
    campaigns=[]
    for cid,members in sorted(grouped.items()):
        campaigns.append({'record_kind':'canonical_reference_unresolved_research_campaign','campaign_id':cid,'reference_domain':members[0]['reference_domain'],'queue_refs':sorted(m['queue_id'] for m in members),'distinct_reference_count':len(members),'occurrence_count':sum(m['occurrence_count'] for m in members),'origin_packs':sorted({x for m in members for x in m['origin_packs']}),'required_verdicts':['exact_alias','narrower_profile','broader_parent','split_required','new_canonical_concept','no_match_or_external_concept'],'research_protocol':['inspect all occurrences and exact industry intent','use primary theory/standard/technical evidence','compare identity grain time authority assumptions inputs outputs and refusal laws','never infer canonical mapping from campaign membership','retain one verdict per queue record'],'status':'OPEN_BULK_RESEARCH_CAMPAIGN','completion_claim':False})
    assignments.sort(key=lambda r:r['queue_id'])
    (HERE/'canonical-reference-unresolved-campaign-assignments.jsonl').write_text(''.join(json.dumps(r,sort_keys=True)+'\n' for r in assignments),encoding='utf-8')
    (HERE/'canonical-reference-unresolved-research-campaigns.jsonl').write_text(''.join(json.dumps(r,sort_keys=True)+'\n' for r in campaigns),encoding='utf-8')
    by_domain=Counter(r['reference_domain'] for r in assignments)
    summary={'report_id':'b07_unresolved_reference_campaign_factoring','as_of':'2026-08-27','raw_review_queue_count':len(queue),'already_resolved_or_exact_candidate_count':len(resolved),'remaining_reference_count':len(remaining),'assigned_reference_count':len(assignments),'research_campaign_count':len(campaigns),'remaining_by_domain':dict(sorted(by_domain.items())),'canonical_mappings_inferred':0,'completion_claim':False,'status':'ALL_REMAINING_REFERENCES_ROUTED_TO_BULK_RESEARCH_CAMPAIGNS_NO_SEMANTIC_VERDICTS_INFERRED'}
    (HERE/'canonical-reference-unresolved-campaign-summary.json').write_text(json.dumps(summary,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    print(json.dumps(summary,sort_keys=True)); return 0
if __name__=='__main__': raise SystemExit(main())
