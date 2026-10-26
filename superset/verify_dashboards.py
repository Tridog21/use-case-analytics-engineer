"""Execute saved chart queries through authenticated Superset, without printing secrets."""
import json,os,time,requests
from pathlib import Path
ROOT=Path(__file__).resolve().parent
base='http://localhost:8088'
manifest=json.loads((ROOT/'assets_manifest.json').read_text())
s=requests.Session()
r=s.post(base+'/api/v1/security/login',json=dict(username=os.environ['SUPERSET_ADMIN_USERNAME'],password=os.environ['SUPERSET_ADMIN_PASSWORD'],provider='db',refresh=False));r.raise_for_status()
s.headers['Authorization']='Bearer '+r.json()['access_token']
csrf=s.get(base+'/api/v1/security/csrf_token/');csrf.raise_for_status();s.headers['X-CSRFToken']=csrf.json()['result']
results={}
for key,chart in manifest['charts'].items():
    start=time.monotonic()
    for attempt in range(3):
        r=s.post(base+'/api/v1/chart/data',json=chart['query_context'],timeout=120)
        payload=r.json()
        if r.ok and all(x.get('status')=='success' for x in payload.get('result',[])):break
        if 'MEMORY_LIMIT_EXCEEDED' not in r.text:break
    ok=r.ok and bool(payload.get('result')) and all(x.get('status')=='success' for x in payload['result'])
    results[key]=dict(status='success' if ok else 'error',http_status=r.status_code,elapsed_seconds=time.monotonic()-start,
                      data=[x.get('data') for x in payload.get('result',[])] if ok else payload,
                      query=[x.get('query') for x in payload.get('result',[])] if ok else None)
    print(key,'OK' if ok else json.dumps(payload,ensure_ascii=False)[:1800],flush=True)
    (ROOT/'validation_results.json').write_text(json.dumps(results,ensure_ascii=False,indent=2))
errors=[k for k,v in results.items() if v['status']!='success']
print('VALIDATION',len(results)-len(errors),'/',len(results),'errors:',errors)
if errors:raise SystemExit(1)
