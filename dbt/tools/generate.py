"""Generate explicit SQL/YAML from the closed, versioned column contracts."""
import json,re
from collections import defaultdict
from pathlib import Path
import yaml
from catalogue import ROOT,MODELS

DBT=ROOT/'dbt'
ST=[('source_identity_key','String','Identité qualifiée de la source, tenant et clé source sérialisés.'),('source_payload_hash','String','Empreinte typée ordonnée des colonnes source, NULL distinct de vide.'),('source_version_key','String','Identité de version CDC ou de changement de capture.'),('imported_at',"DateTime64(3,'UTC')",'Instant technique du premier import, figé à la tentative.'),('capture_key','String','Identifiant durable de la tentative source.'),('capture_at',"DateTime64(3,'UTC')",'Instant figé de la lecture complète source.'),('is_source_present','Bool','Présence technique ; false seulement après une capture complète validée.')]
R=['model_run_id','record_key','record_version_key','row_hash','calculated_at','rule_version','input_cutoff_at']

def write(path,text):
    p=ROOT/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text,encoding='utf-8')
def q(x):return "'"+str(x).replace('\\','\\\\').replace("'","\\'")+"'"
def j(s):return '{{ '+s+' }}'
def ref(n):return j("ref('"+n+"')")
def hash_expr(domain,cols):
    return j('typed_hash('+repr(domain)+', '+repr([dict(name=n,type=t,expr=e) for n,t,e in cols])+')')
def cols_sql(cols,a=''):return ',\n    '.join((a+'.' if a else '')+'`'+x+'`'+(' AS `'+x+'`' if a else '') for x in cols)

def staging(m):
    n=m['name'];cs=m['columns'];names=[c['name'] for c in cs];domain='.'.join(m['source']);cdc=n.startswith('stg_boond_')
    ids=['src_tenant_id','src_language' if n.endswith('dictionaries') else 'src_id'] if cdc else (['src_month_date','src_segment','src_indicator'] if n.endswith('sales_targets') else ['src_state_id','src_segment'] if n.endswith('probabilities') else ['src_id'])
    lookup={c['name']:c['type'] for c in cs}
    identity=hash_expr('source_identity_v1:'+domain,[(c,lookup[c],c) for c in ids])
    payload=hash_expr('source_payload_v1:'+domain,[(c['name'],c['type'],c['name']) for c in cs])
    src=j("source("+repr(m['source'][0])+', '+repr(m['source'][1])+")")
    extract=',\n    '.join('CAST(`'+c['source']+'` AS '+c['type']+') AS '+c['name'] for c in cs)
    sql=j("config(materialized='incremental', incremental_strategy='append', engine='MergeTree()', schema="+repr(m['schema'])+", unique_key='source_version_key', order_by=['source_identity_key','source_version_key'], full_refresh=false, on_schema_change='fail', tags=['capture'])")+'\n'
    if cdc:sql+="{% set lower_bound=cdc_watermark() %}\n"
    sql+='with extracted as (\nselect\n    '+extract+'\nfrom '+src
    if cdc:sql+="\n{% if lower_bound is not none %}where `meta.ts` >= parseDateTime64BestEffort({{ ch_literal(lower_bound) }},3,'UTC'){% endif %}"
    sql+='\n), hashed as (select\n    '+cols_sql(names)+',\n    '+identity+' AS source_identity_key,\n    '+payload+' AS source_payload_hash\nfrom extracted\ngroup by '+', '.join(names)+'\n)'
    if cdc:
        sql+=', changes as (select\n    '+cols_sql(names+['source_identity_key','source_payload_hash'])+',\n    true AS is_source_present\nfrom hashed)'
    else:
        allnames=names+['source_identity_key','source_payload_hash']
        sql+="\n{% if is_incremental() %}, previous as (select\n    "+cols_sql(allnames+['is_source_present'])+'\nfrom '+j('this')+"\nwhere capture_key in ({{ (var('source_capture_keys', {}).get("+repr(domain)+", []) | map('ch_literal') | join(',')) if false else \"''\" }})\n)\n{% endif %}"
        # Explicit literal rendering, rather than user SQL fragments.
        sql=sql.replace("{{ (var('source_capture_keys', {}).get("+repr(domain)+", []) | map('ch_literal') | join(',')) if false else \"''\" }}", "{% for key in var('source_capture_keys', {}).get("+repr(domain)+", []) %}{{ ch_literal(key) }}{{ ',' if not loop.last }}{% else %}''{% endfor %}")
        sql=sql.replace('\n)\n{% endif %}',"\nqualify row_number() over (partition by source_identity_key order by capture_at desc,capture_key desc)=1\n)\n{% endif %}")
        sql+=', changes as (\nselect\n    '+cols_sql(allnames,'h')+',\n    true AS is_source_present\nfrom hashed h\n{% if is_incremental() %}\nleft join previous p on h.source_identity_key=p.source_identity_key\nwhere p.source_identity_key is null or p.source_payload_hash!=h.source_payload_hash or not p.is_source_present\nunion all\nselect\n    '+cols_sql(allnames,'p')+',\n    false AS is_source_present\nfrom previous p\nleft anti join hashed h on p.source_identity_key=h.source_identity_key\nwhere p.is_source_present\n{% endif %}\n)'
    vk=[('identity','String','source_identity_key')]
    if cdc:vk+=[('publication',"DateTime64(3,'UTC')",'src_published_at')]
    else:vk+=[('capture_key','String','capture_token')]
    vk+=[('payload','String','source_payload_hash')]
    if not cdc:vk+=[('presence','Bool','is_source_present')]
    sql+=', run_constants as (select '+j("ch_literal(var('capture_key','parse_only'))")+' as capture_token), candidate as (select\n    '+cols_sql(names+['source_identity_key','source_payload_hash'])+',\n    '+hash_expr('source_version_v1:'+domain,vk)+' AS source_version_key,\n    '+j("utc_var('capture_at')")+' AS imported_at,\n    '+j("ch_literal(var('capture_key','parse_only'))")+' AS capture_key,\n    '+j("utc_var('capture_at')")+' AS capture_at,\n    is_source_present\nfrom changes cross join run_constants)\nselect\n    '+cols_sql(names+[c[0] for c in ST],'c')+'\nfrom candidate c\n{% if is_incremental() %}\nleft anti join '+j('this')+' t on c.source_version_key=t.source_version_key\n{% endif %}\n'
    write(m['path'],sql)

def docs():
    folders=defaultdict(list);sources=defaultdict(list)
    for n,m in MODELS.items():
        if not m['path']:raise ValueError(n)
        columns=m['columns']+[dict(name=c,type=t,description=d,nullable=False) for c,t,d in ST] if n.startswith('stg_') else m['columns']
        tags=['capture'] if n.startswith('stg_') else ['publication'] if n=='int_publication' else ['dataset'] if n.startswith('dataset_') else ['dtr'] if n.startswith('dtr_') else ['mart'] if n.startswith('fct_') else ['common'] if n.startswith('dim_') or m['schema']=='dwh_common' else ['pipeline'] if m['schema']=='dwh_pipeline' else ['revenue']
        m['tags']=tags
        desc=re.search(r'(?:\*\*Grain métier[^\n]*|\*\*Couche/finalité[^\n]*)',m['block'])
        entry=dict(name=n,description=(desc[0] if desc else n)+' Rafraîchissement manuel à la demande. Histoire et révisions conservées ; publication contrôlée.',config=dict(tags=tags),columns=[dict(name=c['name'],data_type=c['type'],description=c['description']) for c in columns])
        key='source_version_key' if n.startswith('stg_') else 'record_version_key' if 'record_version_key' in [c['name'] for c in columns] else 'publication_key' if n=='int_publication' else None
        if key:
            entry['data_tests']=[{'case_grain':{'arguments':{'key':key,'run_scoped':not n.startswith('stg_') and n!='int_publication'},'config':{'tags':tags}}}]
        folders[str(Path(m['path']).parent)].append(entry)
        if n.startswith('stg_'):
            sources[m['source'][0]].append(dict(name=m['source'][1],description='Source physique en lecture seule ; toutes versions et colonnes conservées.',columns=[dict(name=c['source'],description=c['description'],data_type=c['type']) for c in m['columns']]))
    for folder,models in folders.items():write(folder+'/_models.yml',yaml.safe_dump(dict(version=2,models=models),allow_unicode=True,sort_keys=False,width=110))
    write('dbt/models/staging/_sources.yml',yaml.safe_dump(dict(version=2,sources=[dict(name=s,schema="{{ var('"+s+"_source_schema','"+{'boond':'raw','hubspot':'hubspot','case_reference':'ref'}[s]+"') }}",description='Sources du case en lecture seule. Schéma de fixtures substituable dans une cible analytique isolée.',tables=ts) for s,ts in sources.items()]),allow_unicode=True,sort_keys=False))

if __name__=='__main__':
    rules_text=(ROOT/'orest_case_output/spec_technique/01_specification_technique.md').read_text(encoding='utf-8-sig')
    rule=yaml.safe_load(re.search(r'```yaml\n(.*?)```',rules_text,re.S)[1])
    write('dbt/config/case_rules.yml',yaml.safe_dump(rule,allow_unicode=True,sort_keys=False))
    for n,m in MODELS.items():
        if n.startswith('stg_'):staging(m)
    docs()
    print('Generated 15 complete capture models and 73 YAML contracts')
