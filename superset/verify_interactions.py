"""Read-only behavioral checks against the installed Superset and published data."""
import copy, io, json, os, zipfile
from pathlib import Path
import requests, clickhouse_connect, yaml
ROOT=Path(__file__).resolve().parent
m=json.loads((ROOT/'assets_manifest.json').read_text())
baseline=json.loads((ROOT/'validation_results.json').read_text())
s=requests.Session();base='http://localhost:8088'
r=s.post(base+'/api/v1/security/login',json=dict(username=os.environ['SUPERSET_ADMIN_USERNAME'],password=os.environ['SUPERSET_ADMIN_PASSWORD'],provider='db'));r.raise_for_status()
s.headers['Authorization']='Bearer '+r.json()['access_token']
r=s.get(base+'/api/v1/security/csrf_token/');r.raise_for_status();s.headers['X-CSRFToken']=r.json()['result']
c=clickhouse_connect.get_client(host='clickhouse',username='superset_reader',password=os.environ['CLICKHOUSE_SUPERSET_PASSWORD'])
checks=[]
def check(name,ok,evidence):
    checks.append(dict(name=name,passed=bool(ok),evidence=evidence));print(name,'PASS' if ok else 'FAIL',flush=True)
    (ROOT/'interaction_results.json').write_text(json.dumps(checks,ensure_ascii=False,indent=2,default=str))
def run(key,changes=None,time_range=None):
    q=copy.deepcopy(m['charts'][key]['query_context']);query=q['queries'][0]
    for col,val in (changes or {}).items():
        query['filters']=[f for f in query['filters'] if f['col']!=col]+[dict(col=col,op='IN',val=[val])]
    if time_range:query['time_range']=time_range
    for attempt in range(3):
        r=s.post(base+'/api/v1/chart/data',json=q,timeout=120)
        if 'MEMORY_LIMIT_EXCEEDED' not in r.text:break
    r.raise_for_status();result=r.json()['result'][0]
    assert result['status']=='success',result
    return result
def value(result):return next(iter(result['data'][0].values()))
before=c.query('select publication_key from dwh_common.int_publication').result_rows
for key,col,p in [('duration_median','duree_terminee',.5),('duration_p90','duree_terminee',.9),('age_median','anciennete',.5)]:
    for label,filters in [('default',{}),('team',{'equipe':'Team BA - SMB'}),('earlier',{'date_observation':'2026-07-31'})]:
        result=run(key,filters);tail=result['query'].split('FROM (',1)[1]
        ref=c.query(f'SELECT if(countIf({col} is not null)=0,NULL,quantileExactInclusiveIf({p})({col},{col} is not null)) FROM ('+tail).first_row[0]
        actual=value(result);check(key+'_'+label,actual==ref or (actual is not None and ref is not None and abs(actual-ref)<1e-9),dict(actual=actual,native_exact_inclusive=ref))
t=run('funnel',{'type_vente':'Upsells'})['data'];check('upsell_path',len(t)==4 and len({r['etape'] for r in t})==4,t)
t=baseline['funnel']['data'][0];check('new_sales_path',len(t)==7 and len({r['etape'] for r in t})==7,t)
a=value(run('over_threshold'));b=value(run('over_threshold',{'seuil':'30 jours'}));d=value(run('over_threshold',{'seuil':'Désactivé'}))
check('threshold_monotonic_and_disabled',b<=a and d is None,dict(days21=a,days30=b,disabled=d))
for key in ['cohort_open','cohort_won','cohort_lost']:
    r=value(run(key,{'cohorte':'2026-08-01','equipe':'Team BA - SMB'}));check(key+'_immature_team',r is None,r)
rows=run('cohort_evolution')['data'];names=['Ouvert','Gagné','Perdu','Abandonné','Non qualifié','Inconnu']
check('six_outcomes_sum_to_one',all(abs(sum(row[n] for n in names)-1)<1e-9 for row in rows),rows)
matrix=run('cohort_matrix')['data'];sep=[r for r in matrix if r['cohorte']=='2026-09-01'][0]
check('matrix_six_cohorts_and_immaturity',len(matrix)==6 and all(sep[h]=='Non mature' for h in ['J+30','J+60','J+90']),matrix)
obj=value(run('obj_mrr_signed',{'equipe_objectif':'ES'}));target=value(run('target_mrr_signed',{'equipe_objectif':'ES'}))
check('ES_target_preserved_actual_null',obj is None and target is not None and target>0,dict(actual=obj,target=target))
deal=baseline['open_detail']['data'][0][0]['dossier'];timeline=run('duration_timeline',{'dossier':deal})['data']
check('selected_timeline',len(timeline)>0 and all(r['dossier']==deal for r in timeline),dict(dossier=deal,rows=len(timeline)))
early=run('duration_timeline',{'dossier':deal,'date_observation':'2021-09-01'})['data'];check('timeline_future_mask',early==[],dict(rows=len(early)))
unknown=run('duration_population',time_range='No filter')['data'];check('unknown_entries_visible',unknown[0]['Débuts inconnus']>0,unknown)
syn=m['dashboards']['synthese'];financial={m['charts'][k]['id'] for k in ['mrr','churn','cascade','losses']}
check('financial_scope_global',all(not financial.intersection(f['chartsInScope']) for f in syn['filters'] if f['id'] in ['NATIVE_FILTER-syn-team','NATIVE_FILTER-syn-team-tunnel','NATIVE_FILTER-syn-type']),[f['name'] for f in syn['filters']])
coh=m['dashboards']['cohortes'];matrixid=m['charts']['cohort_matrix']['id']
check('matrix_immune_to_zoom',all(matrixid not in f['chartsInScope'] for f in coh['filters'] if f['id'] in ['NATIVE_FILTER-coh-zoom','NATIVE_FILTER-coh-horizon']),matrixid)
after=c.query('select publication_key from dwh_common.int_publication').result_rows;check('publication_unchanged',before==after,after)
# Native portable export. Explicitly strip authentication fields from database YAML.
r=s.get(base+'/api/v1/dashboard/export/',params={'q':'!(1,2,3)'});r.raise_for_status()
source=zipfile.ZipFile(io.BytesIO(r.content));out=ROOT/'exports';out.mkdir(exist_ok=True)
with zipfile.ZipFile(out/'dashboards_superset.zip','w',zipfile.ZIP_DEFLATED) as dest:
    for entry in source.infolist():
        data=source.read(entry.filename)
        if '/databases/' in entry.filename and entry.filename.endswith('.yaml'):
            db=yaml.safe_load(data)
            db['sqlalchemy_uri']='clickhousedb://superset_reader@clickhouse:8123/default'
            for key in ['password','encrypted_extra','ssh_tunnel']:db.pop(key,None)
            data=yaml.safe_dump(db,allow_unicode=True).encode()
        dest.writestr(entry.filename,data)
check('native_export_created',(out/'dashboards_superset.zip').stat().st_size>0,dict(files=len(source.infolist())))
if any(not x['passed'] for x in checks):raise SystemExit(1)
print('ALL',len(checks),'CHECKS PASSED')
