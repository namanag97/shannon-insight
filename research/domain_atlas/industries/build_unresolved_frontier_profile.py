#!/usr/bin/env python3
"""Profile the *remaining* B07 canonical-reference frontier for research batching.

This is routing and prioritization only. It never creates a semantic mapping. It subtracts all
manual adjudications and conservative exact-candidate layers, then reports the true unresolved
population by domain, industry pack, frequency and research-campaign vocabulary.
"""
from __future__ import annotations
import json,re,unicodedata
from collections import Counter,defaultdict
from pathlib import Path

HERE=Path(__file__).resolve().parent

def L(path):
    p=Path(path)
    if not p.exists(): return []
    return [json.loads(x) for x in p.read_text(encoding='utf-8').splitlines() if x.strip()]

def norm(s):
    s=unicodedata.normalize('NFKC',str(s)).casefold()
    s=s.replace('_',' ').replace('-',' ')
    s=re.sub(r'[^a-z0-9]+',' ',s)
    return ' '.join(s.split())

STOP={
 'a','an','and','or','of','for','to','in','on','by','with','from','using','based','model','models',
 'method','methods','analysis','analytics','calculation','approach','system','data','process','case',
 'index','score','metric','metrics','rate','value','values','test','testing','rule','rules'
}

# Routing-only lexical campaigns. A match says what evidence/search team should review the row;
# it does NOT assert canonical semantic equivalence.
CAMPAIGNS={
 'method.statistical_process_monitoring':('cusum','ewma','hotelling','spc','control chart','shewhart','process capability','statistical process'),
 'method.bayesian_inference_calibration':('bayesian','posterior','prior','markov chain monte carlo','mcmc'),
 'method.causal_experimentation':('causal','difference in differences','synthetic control','propensity','instrumental variable','randomized','experiment','interrupted time series','regression discontinuity'),
 'method.forecasting_time_series':('forecast','arima','ets','exponential smoothing','time series','seasonal','croston','prophet','state space'),
 'method.optimization_operations_research':('optimization','optimisation','linear programming','integer programming','mixed integer','milp','mip','constraint programming','network flow','assignment','scheduling','routing','knapsack','newsvendor'),
 'method.simulation':('simulation','monte carlo','discrete event','agent based','system dynamics','digital twin'),
 'method.queueing_flow':('queue','little law','waiting time','throughput','wip','queueing'),
 'method.reliability_survival_risk':('survival','hazard','weibull','reliability','failure rate','fault tree','fmea','markov reliability','availability model'),
 'method.anomaly_change_detection':('anomaly','change point','changepoint','drift','outlier','novelty detection'),
 'method.predictive_ml':('machine learning','classification','regression','random forest','gradient boosting','xgboost','neural','deep learning','svm','support vector','predictive'),
 'method.clustering_segmentation':('cluster','clustering','segmentation','k means','hierarchical clustering'),
 'method.graph_network':('graph','network analysis','centrality','community detection','path analysis','knowledge graph'),
 'method.process_mining':('process mining','conformance checking','variant analysis','process discovery','token replay','alignment'),
 'method.geospatial_spatial':('geospatial','spatial','gis','kriging','geostat','raster','geocod','route accessibility','trajectory','terrain','hydrology'),
 'method.text_document':('text mining','nlp','natural language','topic model','sentiment','document analysis','information extraction'),
 'method.signal_media':('signal processing','spectral','fft','wavelet','image analysis','computer vision','audio','video'),
 'method.financial_economic':('discounted cash flow','dcf','var','value at risk','expected shortfall','duration','convexity','npv','irr','portfolio optimization','option pricing'),
 'method.scientific_engineering_domain':('power flow','contingency','load flow','finite element','cfd','computational fluid','thermodynamic','mass balance','energy balance','reaction kinetics','hydraulic','reservoir','seismic'),
 'operation.join_match_link':('join','match','link','resolve','entity resolution','deduplicate'),
 'operation.aggregate_summarize':('aggregate','rollup','group','summarize','summarise','cube'),
 'operation.filter_select_project':('filter','select','project','slice','subset'),
 'operation.transform_convert_normalize':('transform','convert','normalize','normalise','standardize','standardise','encode','decode'),
 'operation.reconcile_validate_compare':('reconcile','validate','compare','verify','check','balance'),
 'operation.rank_score_prioritize':('rank','score','prioritize','prioritise','order'),
 'operation.estimate_infer':('estimate','infer','fit','calibrate'),
 'operation.detect_classify_segment':('detect','classify','segment','cluster'),
 'operation.forecast_predict':('forecast','predict'),
 'operation.optimize_plan_schedule':('optimize','optimise','plan','schedule','route','allocate'),
 'operation.simulate_scenario':('simulate','scenario'),
 'source.database_repository':('database','db','sql','warehouse','lakehouse','data lake','repository'),
 'source.erp_enterprise_application':('erp','sap','oracle erp','accounting','crm','salesforce','workday','wms','tms','mes','eam','scm'),
 'source.event_stream_cdc':('kafka','event','stream','cdc','change data','queue','message','log'),
 'source.file_object':('file','csv','excel','spreadsheet','s3','object storage','parquet','avro','json'),
 'source.api_saas':('api','odata','graphql','rest','soap','saas','webhook'),
 'source.document_collaboration':('document','email','sharepoint','chat','calendar','pdf'),
 'source.telemetry_iot_industrial':('sensor','iot','scada','historian','opc','telemetry','plc','dcs'),
 'source.scientific_regulated':('ehr','fhir','dicom','lims','instrument','clinical','market data','trading','claims'),
}

def campaign_for(row):
    domain=row['reference_domain']; text=norm(row['raw_ref'])
    prefixes={
      'analytical_practice':'method.', 'typed_operation':'operation.', 'source_system_class':'source.'
    }
    prefix=prefixes.get(domain)
    hits=[]
    if prefix:
        for cid,terms in CAMPAIGNS.items():
            if not cid.startswith(prefix): continue
            if any(norm(term) in text for term in terms): hits.append(cid)
    if len(hits)==1: return hits[0]
    if len(hits)>1: return 'routing.multiple_candidates'
    if domain=='industry_classification':
        packs=row.get('origin_packs',[])
        return 'industry.'+(packs[0] if len(packs)==1 else 'cross_pack')
    return domain+'.unclassified'

def main():
    queue=L(HERE/'canonical-reference-review-queue.jsonl')
    manual=L(HERE/'canonical-reference-adjudications.jsonl')
    auto=L(HERE/'canonical-reference-auto-alias-candidates.jsonl')
    current=L(HERE/'canonical-reference-current-method-candidates.jsonl')
    resolved={r['queue_id'] for r in manual+auto+current}
    remaining=[r for r in queue if r['queue_id'] not in resolved]

    by_domain=Counter(r['reference_domain'] for r in remaining)
    occurrences_by_domain=Counter()
    by_pack=Counter(); campaign_counts=Counter(); campaign_occ=Counter()
    token_counts=defaultdict(Counter)
    for r in remaining:
        occurrences_by_domain[r['reference_domain']]+=r['occurrence_count']
        for p in r.get('origin_packs',[]): by_pack[(r['reference_domain'],p)]+=1
        cid=campaign_for(r); campaign_counts[cid]+=1; campaign_occ[cid]+=r['occurrence_count']
        for tok in norm(r['raw_ref']).split():
            if len(tok)>2 and tok not in STOP: token_counts[r['reference_domain']][tok]+=r['occurrence_count']

    top=[]
    for domain in sorted(by_domain):
        rows=sorted((r for r in remaining if r['reference_domain']==domain), key=lambda r:(-r['occurrence_count'],r['raw_ref']))[:100]
        for rank,r in enumerate(rows,1):
            top.append({'record_kind':'b07_unresolved_priority_ref','reference_domain':domain,'rank':rank,'queue_id':r['queue_id'],'raw_ref':r['raw_ref'],'occurrence_count':r['occurrence_count'],'origin_packs':r.get('origin_packs',[]),'example_origin_records':r.get('example_origin_records',[]),'research_campaign':campaign_for(r),'completion_claim':False})
    (HERE/'unresolved-frontier-top-refs.jsonl').write_text(''.join(json.dumps(r,sort_keys=True)+'\n' for r in top),encoding='utf-8')

    campaigns=[]
    for cid,count in sorted(campaign_counts.items(),key=lambda kv:(-campaign_occ[kv[0]],-kv[1],kv[0])):
        campaigns.append({'record_kind':'b07_research_campaign_route','campaign_id':cid,'unresolved_reference_count':count,'unresolved_occurrence_count':campaign_occ[cid],'routing_only':True,'semantic_decisions_created':0,'completion_claim':False})
    (HERE/'unresolved-frontier-research-campaigns.jsonl').write_text(''.join(json.dumps(r,sort_keys=True)+'\n' for r in campaigns),encoding='utf-8')

    tokens=[]
    for domain,c in sorted(token_counts.items()):
        for tok,n in c.most_common(100): tokens.append({'record_kind':'b07_unresolved_token_frequency','reference_domain':domain,'token':tok,'weighted_occurrence_count':n,'completion_claim':False})
    (HERE/'unresolved-frontier-token-frequency.jsonl').write_text(''.join(json.dumps(r,sort_keys=True)+'\n' for r in tokens),encoding='utf-8')

    summary={
      'report_id':'b07_unresolved_frontier_profile','as_of':'2026-08-27','raw_queue_records':len(queue),
      'manual_adjudications':len(manual),'machine_exact_candidates':len(auto),'current_method_exact_candidates':len(current),
      'remaining_unresolved_records':len(remaining),'remaining_unresolved_occurrences':sum(r['occurrence_count'] for r in remaining),
      'remaining_records_by_domain':dict(sorted(by_domain.items())),
      'remaining_occurrences_by_domain':dict(sorted(occurrences_by_domain.items())),
      'research_campaign_count':len(campaigns),'top_research_campaigns':campaigns[:20],
      'semantic_decisions_created_by_this_profile':0,'completion_claim':False,
      'status':'PROFILED_FOR_RESEARCH_BATCHING_NOT_SEMANTIC_CLOSURE'
    }
    (HERE/'unresolved-frontier-profile-summary.json').write_text(json.dumps(summary,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    print(json.dumps(summary,sort_keys=True)); return 0
if __name__=='__main__': raise SystemExit(main())
