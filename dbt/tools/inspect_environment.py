from pathlib import Path
import json, sys, importlib.metadata
import clickhouse_connect
from catalogue import MODELS,ROOT

c=clickhouse_connect.get_client(host='localhost',port=8123,username='default',password='',database='analytics')
report={'python':sys.version,'packages':{p:importlib.metadata.version(p) for p in ['dbt-core','dbt-clickhouse','clickhouse-connect']}}
report['server']=c.query('SELECT version(), timezone()').result_rows
report['sources']=c.query("SELECT database, name, engine, total_rows FROM system.tables WHERE database IN ('raw','hubspot','ref') ORDER BY database,name").result_rows
report['columns']=c.query("SELECT database,table,name,type,position FROM system.columns WHERE database IN ('raw','hubspot','ref') ORDER BY database,table,position").result_rows
out=ROOT/'orest_case_output/implementation'
out.mkdir(parents=True,exist_ok=True)
(out/'environment.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in report.items() if k!='columns'},indent=2))
assert len(report['columns'])==179
for n,m in MODELS.items():
    if n.startswith('stg_'):
        db={'boond':'raw','case_reference':'ref','hubspot':'hubspot'}[m['source'][0]]
        actual=[(x[2],x[3]) for x in report['columns'] if x[0]==db and x[1]==m['source'][1]]
        assert [x[0] for x in actual]==[x['source'] for x in m['columns']],n
print('15 source contracts / 179 columns verified in source order')
