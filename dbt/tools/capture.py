"""Source-by-source complete reconciliation and immutable capture manifests."""
import json,uuid
from pathlib import Path
from catalogue import ROOT,MODELS
from runtime import *

def capture_all():
    c=client();allowed={};fingerprints={};jobs=[]
    for n,m in MODELS.items():
        if not n.startswith('stg_'):continue
        domain='.'.join(m['source']);history=STATE/'captures'/domain
        manifests=[json.loads(p.read_text(encoding='utf-8')) for p in sorted(history.glob('*/manifest.json'))]
        complete=[x for x in manifests if x['status']=='success']
        keys=[x['capture_key'] for x in complete]
        source_schema={'boond':'raw','case_reference':'ref','hubspot':'hubspot'}[m['source'][0]]
        columns=m['columns'];physical=source_schema+'.`'+m['source'][1]+'`'
        read_sql='select '+', '.join('`'+x['source']+'`' for x in columns)+' from '+physical
        rows=c.query(read_sql).result_rows
        # Exact ordered source payload set, including NULL and types; never logs payloads.
        source_digest=digest(sorted([digest([str(v) if v is not None else None for v in r]) for r in rows]))
        actual=c.query("select name,type from system.columns where database={db:String} and table={table:String} order by position",parameters={'db':source_schema,'table':m['source'][1]}).result_rows
        if [r[0] for r in actual]!=[x['source'] for x in columns]:raise RuntimeError('Source schema changed: '+domain)
        schema_hash=digest(actual)
        if complete and complete[-1]['schema_hash']!=schema_hash:raise RuntimeError('Schema migration required: '+domain)
        if complete and len(rows)<complete[-1]['nb_rows_read']*.5:raise RuntimeError('Anomalous source decrease requires explicit validated capture: '+domain)
        pending=[x for x in manifests if x['status']!='success']
        retry=pending[-1] if pending and pending[-1]['source_digest']==source_digest else None
        key=retry['capture_key'] if retry else now().replace(':','').replace('.','')+'_'+uuid.uuid4().hex[:10]
        folder=history/key;at=retry['capture_at'] if retry else now()
        vars={'capture_key':key,'capture_at':at,'cdc_full_scan':True,'cdc_overlap_hours':48,'source_capture_keys':{domain:keys}}
        manifest=dict(source=domain,model=n,capture_key=key,capture_at=at,status='running',source_digest=source_digest,schema_hash=schema_hash,nb_rows_read=len(rows),lower_bound=None,upper_bound=at,full_scan=True,started_at=now())
        atomic_json(folder/'manifest.json',manifest)
        try:
            target=m['schema']+'.'+n
            exists=c.query('select count() from system.tables where database={db:String} and name={name:String}',parameters={'db':m['schema'],'name':n}).first_row[0]
            before_count=c.query('select count() from '+target).first_row[0] if exists else 0
            manifest['commands']=[dbt(['run','--select',n,'--exclude','tag:publication','--threads','1'],vars,folder,'capture')]
            manifest['commands'].append(dbt(['test','--select',n,'--exclude','tag:publication','--indirect-selection','cautious'],vars,folder,'tests'))
            after=c.query(read_sql).result_rows
            if digest(sorted([digest([str(v) if v is not None else None for v in r]) for r in after]))!=source_digest:raise RuntimeError('Source changed during capture; abandon and retry new capture')
            target=m['schema']+'.'+n
            loaded=c.query('select source_version_key from '+target+' order by source_version_key').result_rows
            physical_count=len(loaded)
            compiled=DBT/'target/compiled/use_case'/Path(m['path']).relative_to('dbt')
            sql=compiled.read_text(encoding='utf-8');prefix=sql.rsplit('\nselect\n    c.',1)[0]
            if prefix==sql:raise RuntimeError('Capture candidate SQL missing '+n)
            if n.startswith('stg_boond_'):
                expected=c.query(prefix+'\nselect source_version_key from candidate order by source_version_key').result_rows
                if set(expected)-set(loaded):raise RuntimeError('Full CDC reconciliation found missing source versions '+domain)
                manifest['nb_expected_source_keys']=len(expected)
                manifest['expected_keys_digest']=digest([r[0] for r in expected])
            else:
                expected=c.query(prefix+'\nselect source_identity_key,source_payload_hash from hashed order by source_identity_key').result_rows
                accepted=keys+[key]
                current=c.query('select source_identity_key,source_payload_hash,is_source_present from '+target+' where capture_key in {captures:Array(String)} qualify row_number() over (partition by source_identity_key order by capture_at desc,capture_key desc)=1',parameters={'captures':accepted}).result_rows
                actual=sorted([(i,h) for i,h,present in current if present])
                if actual!=sorted(expected):raise RuntimeError('Complete snapshot reconstruction mismatch '+domain)
                manifest['nb_expected_source_keys']=len(expected);manifest['expected_payload_digest']=digest(expected)
                loaded=c.query('select source_version_key from '+target+' where capture_key in {captures:Array(String)} order by source_version_key',parameters={'captures':accepted}).result_rows
            manifest.update(status='success',ended_at=now(),nb_rows_written=physical_count-before_count,physical_nb_keys=physical_count,nb_keys=len(loaded),keys_digest=digest([r[0] for r in loaded]))
            atomic_json(folder/'manifest.json',manifest)
        except Exception as e:
            manifest.update(status='failed',error=str(e),ended_at=now());atomic_json(folder/'manifest.json',manifest);raise
        if not n.startswith('stg_boond_'):allowed[domain]=keys+[key]
        fingerprints[n]=dict(keys_digest=manifest['keys_digest'],nb_keys=manifest['nb_keys'],source_digest=source_digest)
        jobs.append(str(folder/'manifest.json'))
    return allowed,fingerprints,jobs

if __name__=='__main__':
    with writer_lock():
        allowed,fingerprints,jobs=capture_all()
        atomic_json(STATE/'last_capture.json',dict(source_capture_keys=allowed,fingerprints=fingerprints,jobs=jobs))
