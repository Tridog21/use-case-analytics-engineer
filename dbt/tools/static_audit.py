"""Validate catalogue coverage, docs, dependency graph and protected-source boundaries."""
import json,re,yaml
from catalogue import ROOT,MODELS
from runtime import DBT,STATE,atomic_json,now

def execute():
    results=[]
    def check(id,condition,detail):
        results.append(dict(id=id,status='pass' if condition else 'fail',detail=detail))
        if not condition:raise AssertionError(id+': '+detail)
    sqlfiles=list((DBT/'models').rglob('*.sql'));check('T01',len(sqlfiles)==len(MODELS)==73,'73 model SQL files, closed catalogue')
    staging=[m for n,m in MODELS.items() if n.startswith('stg_')];check('T01_source_columns',len(staging)==15 and sum(len(m['columns']) for m in staging)==179,'15 one-to-one staging / 179 source columns')
    yaml_models={m['name']:m for p in (DBT/'models').rglob('*.yml') for m in (yaml.safe_load(p.read_text(encoding='utf-8')).get('models') or [])}
    for n,m in MODELS.items():
        check('T01_schema_'+n,m['schema'] in ['stg_boond','stg_hubspot','stg_reference','dtm_common','dwh_common','dwh_pipeline','dwh_revenue','dtm_pipeline','dtm_revenue','dtr_sales'],n+' explicit analytical destination')
        text=(ROOT/m['path']).read_text(encoding='utf-8')
        check('T08_'+n,not re.search(r'\bselect\s+(?:\w+\.)?\*',text,re.I),n+' explicit SQL projections')
        check('T08_docs_'+n,bool(yaml_models[n].get('description')) and all(c.get('description') for c in yaml_models[n]['columns']),n+' all table/column descriptions')
        check('T65_'+n,not re.search(r'\b(?:drop|truncate|delete|insert|create)\s+(?:table|into|from|view|database)',text,re.I),n+' SELECT model, no manual DDL/DML')
        if n!='int_publication':check('T09_'+n,"tags=['publication']" not in text,n+' publication isolated')
    graph={n:list(dict.fromkeys(re.findall(r"ref\('([^']+)'\)",(ROOT/m['path']).read_text(encoding='utf-8')))) for n,m in MODELS.items()}
    for n,m in MODELS.items():check('T09_contract_dependencies_'+n,set(m['refs'])<=set(graph[n]),n+' all catalogue dependencies declared')
    visiting=set();done=set()
    def visit(n):
        if n in done:return
        if n in visiting:raise AssertionError('DAG cycle '+n)
        visiting.add(n)
        for d in graph[n]:
            if d not in graph:raise AssertionError('Unknown model ref '+d)
            visit(d)
        visiting.remove(n);done.add(n)
    for n in graph:visit(n)
    check('T09_DAG',len(done)==73,'DAG without cycles; all refs resolve')
    check('T09_pointer',graph['int_publication']==[],'Publication model has no upstream ref; runner authorizes final isolated command')
    atomic_json(STATE/'static_audit.json',dict(at=now(),status='success',checks=results))
    print('Static audit:',len(results),'checks passed')

if __name__=='__main__':execute()
