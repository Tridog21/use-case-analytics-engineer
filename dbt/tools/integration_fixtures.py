"""Exercise capture/retry/collision behavior using analytical fixture tables only."""
from runtime import *
from catalogue import MODELS
from generate import q

def fixture_code_hash():
    paths=['tools/integration_fixtures.py','tools/runtime.py','macros/case.sql','models/staging/boond/stg_boond_opportunities.sql','models/staging/reference/stg_ref_sales_targets.sql','models/marts/common/dim_metric.sql']
    return digest([(p,(DBT/p).read_text(encoding='utf-8')) for p in paths])

def execute():
    c=client();stamp=str(time.time_ns());schema='stg_validation_'+stamp;suffix='_validation_'+stamp;folder=STATE/'fixtures'/stamp
    c.command('CREATE DATABASE IF NOT EXISTS `'+schema+'` ENGINE=Atomic')
    results=[]
    def check(name,actual,expected):
        results.append(dict(test=name,actual=actual,expected=expected,status='pass' if actual==expected else 'fail'))
        atomic_json(folder/'results.json',results)
        if actual!=expected:raise AssertionError(name+': '+str(actual)+' != '+str(expected))
    def command(label,model,variables,expected_failure=False,action=None):
        try:
            dbt([action or ('run' if not expected_failure else 'test'),'--select',model,'--exclude','tag:publication','--threads','1'],variables,folder,label)
            if expected_failure:raise AssertionError('Expected validation failure '+label)
        except RuntimeError:
            if not expected_failure:raise
    # Source fixture is typed from the read-only source schema, with synthetic content.
    c.command('CREATE TABLE `'+schema+'`.opportunities AS raw.opportunities ENGINE=MergeTree ORDER BY tuple()')
    names=[x['source'] for x in MODELS['stg_boond_opportunities']['columns']]
    def opportunity(identifier,time,state=22,deleted=False,amount=100):
        values=[]
        overrides={'meta.customer':'fixture','id':identifier,'meta.deleted':deleted,'meta.ts':'2026-09-01 '+time+':00:00.123','creationDate':'2026-09-01 01:00:00.123','state':state,'typeOf':4,'turnoverEstimatedExcludingTax':amount,'attributes':'{}'}
        for col in MODELS['stg_boond_opportunities']['columns']:
            typ=col['type'];values.append(overrides.get(col['source'],None if typ.startswith('Nullable(') else '' if 'String' in typ else 0))
        # clickhouse-connect requires native datetimes for DateTime64 inserts.
        for idx,col in enumerate(MODELS['stg_boond_opportunities']['columns']):
            if 'DateTime' in col['type'] and values[idx] is not None:values[idx]=datetime.datetime.fromisoformat(values[idx]).replace(tzinfo=datetime.UTC)
        return values
    c.insert(schema+'.opportunities',[opportunity(1,'08'),opportunity(1,'10',24)],column_names=names)
    v=dict(validation_schema_suffix=suffix,boond_source_schema=schema,capture_key='cdc1',capture_at=now(),cdc_full_scan=True,cdc_overlap_hours=1)
    target='stg_boond'+suffix+'.stg_boond_opportunities'
    command('S01_first_load','stg_boond_opportunities',v);check('S01_first_load',c.query('select count() from '+target).first_row[0],2)
    command('S03_exact_rerun','stg_boond_opportunities',v);check('S03_exact_rerun',c.query('select count() from '+target).first_row[0],2)
    c.insert(schema+'.opportunities',[opportunity(1,'09',23),opportunity(1,'05',20)],column_names=names)
    v.update(cdc_full_scan=False,capture_key='cdc2',capture_at=now())
    command('S09_inside_window','stg_boond_opportunities',v);check('S09_inside_window',c.query('select count() from '+target).first_row[0],3)
    v.update(cdc_full_scan=True,capture_key='cdc3',capture_at=now());command('S10_outside_reconciliation','stg_boond_opportunities',v);check('S10_outside_reconciliation',c.query('select count() from '+target).first_row[0],4)
    c.insert(schema+'.opportunities',[opportunity(1,'11',24,True)],column_names=names);v.update(capture_key='cdc4',capture_at=now());command('S07_tombstone','stg_boond_opportunities',v);check('S07_tombstone',c.query('select countIf(src_is_deleted) from '+target).first_row[0],1)
    # A different target begins with a deliberately partial write, replayed from its durable bound.
    partial_suffix=suffix+'_partial';partial='stg_boond'+partial_suffix+'.stg_boond_opportunities'
    c.command('CREATE DATABASE `stg_boond'+partial_suffix+'` ENGINE=Atomic');c.command('CREATE TABLE '+partial+' AS '+target+' ENGINE=MergeTree ORDER BY (source_identity_key,source_version_key)')
    c.command('INSERT INTO '+partial+' SELECT '+','.join('`'+x[0]+'`' for x in c.query('DESCRIBE TABLE '+target).result_rows)+' FROM '+target+' ORDER BY src_published_at DESC LIMIT 1')
    pv=dict(v,validation_schema_suffix=partial_suffix,cdc_full_scan=False,cdc_replay_from_at='2026-09-01T00:00:00.000Z');command('S11_partial_replay','stg_boond_opportunities',pv);check('S11_partial_replay',c.query('select count() from '+partial).first_row[0],5)
    c.insert(schema+'.opportunities',[opportunity(1,'10',24,amount=200)],column_names=names);v.update(capture_key='collision',capture_at=now());command('S06_collision_capture','stg_boond_opportunities',v);command('S06_collision_blocked','T03_stg_boond_opportunities',v,expected_failure=True);check('S06_payloads_preserved',c.query('select count() from '+target+" where src_published_at=toDateTime64('2026-09-01 10:00:00.123',3,'UTC')").first_row[0],2)
    # Three complete reference captures A -> B -> A, with fixed capture keys and times.
    c.command('CREATE TABLE `'+schema+'`.sales_targets AS ref.sales_targets ENGINE=MergeTree ORDER BY tuple()')
    c.insert(schema+'.sales_targets',[[datetime.date(2026,9,1),'SMB','demos',100.]],column_names=['month','segment','indicator','target'])
    rv=dict(validation_schema_suffix=suffix,case_reference_source_schema=schema,source_capture_keys={'case_reference.sales_targets':[]},capture_key='snapshot_A',capture_at='2026-10-01T00:00:00.000Z')
    starget='stg_reference'+suffix+'.stg_ref_sales_targets';command('S13_A','stg_ref_sales_targets',rv)
    for token,value,at in [('snapshot_B',200,'2026-10-02T00:00:00.000Z'),('snapshot_A2',100,'2026-10-03T00:00:00.000Z')]:
        c.command('ALTER TABLE `'+schema+'`.sales_targets UPDATE target='+str(value)+' WHERE 1 SETTINGS mutations_sync=1')
        rv['source_capture_keys']['case_reference.sales_targets'].append(rv['capture_key']);rv.update(capture_key=token,capture_at=at);command('S13_'+token,'stg_ref_sales_targets',rv)
    check('S13_A_B_A',c.query('select src_target from '+starget+' order by capture_at').result_rows,[(100.,),(200.,),(100.,)])
    command('S13_retry_same_capture','stg_ref_sales_targets',rv);check('S13_idempotent',c.query('select count() from '+starget).first_row[0],3)
    # Disappearance is observed in an explicit successful empty fixture capture.
    c.command('ALTER TABLE `'+schema+'`.sales_targets DELETE WHERE 1 SETTINGS mutations_sync=1')
    rv['source_capture_keys']['case_reference.sales_targets'].append(rv['capture_key']);rv.update(capture_key='snapshot_empty',capture_at='2026-10-04T00:00:00.000Z');command('S14_complete_absence','stg_ref_sales_targets',rv)
    check('S14_tombstone',c.query('select is_source_present from '+starget+' order by capture_at desc limit 1').first_row[0],False)
    # Target-empty incremental branch, separate relation and complete history.
    empty_suffix=suffix+'_empty';empty='stg_boond'+empty_suffix+'.stg_boond_opportunities'
    c.command('CREATE DATABASE `stg_boond'+empty_suffix+'` ENGINE=Atomic');c.command('CREATE TABLE '+empty+' AS '+target+' ENGINE=MergeTree ORDER BY (source_identity_key,source_version_key)')
    ev=dict(v,validation_schema_suffix=empty_suffix,cdc_full_scan=False);command('S02_empty_target','stg_boond_opportunities',ev);check('S02_empty_target',c.query('select count() from '+empty).first_row[0],6)
    dv=dict(validation_schema_suffix=suffix,model_run_id='f'*64,test_model_run_id='f'*64,rule_version='fixture',calculated_at='2026-10-01T00:00:00.000Z',input_cutoff_at='2026-10-01T00:00:00.000Z')
    dtarget='dtm_common'+suffix+'.dim_metric';command('S16_derived_first','dim_metric',dv);command('S16_same_run','dim_metric',dv);check('S16_no_copy',c.query('select count() from '+dtarget).first_row[0],4)
    partial_d='dtm_common'+partial_suffix+'.dim_metric'
    c.command('CREATE DATABASE IF NOT EXISTS `dtm_common'+partial_suffix+'` ENGINE=Atomic');c.command('CREATE TABLE '+partial_d+' AS '+dtarget+' ENGINE=MergeTree ORDER BY (model_run_id,record_key)')
    columns=','.join('`'+x[0]+'`' for x in c.query('DESCRIBE TABLE '+dtarget).result_rows)
    c.command('INSERT INTO '+partial_d+' SELECT '+columns+' FROM '+dtarget+' LIMIT 1')
    command('S17_derived_partial','dim_metric',dict(dv,validation_schema_suffix=partial_suffix));check('S17_completed',c.query('select count() from '+partial_d).first_row[0],4)
    old_digest=digest(c.query('select record_key,row_hash,calculated_at from '+dtarget+' order by record_key').result_rows)
    command('S19_new_revision','dim_metric',dict(dv,model_run_id='e'*64,rule_version='fixture_v2'));check('S19_revision_retained',c.query('select count() from '+dtarget).first_row[0],8)
    check('S20_old_run_unchanged',digest(c.query('select record_key,row_hash,calculated_at from '+dtarget+" where model_run_id='"+'f'*64+"' order by record_key").result_rows),old_digest)
    c.command('ALTER TABLE '+dtarget+" UPDATE row_hash='tampered' WHERE metric_code='demos' AND model_run_id='"+'f'*64+"' SETTINGS mutations_sync=1")
    command('S17_divergence_blocked','dim_metric',dv,expected_failure=True,action='run')
    check('S17_no_duplicate_on_divergence',c.query('select count() from '+dtarget).first_row[0],8)
    # Publication lock refuses a second writer without touching a pointer.
    try:
        with writer_lock():pass
    except FileExistsError:check('S26_concurrent_writer',True,True)
    else:raise AssertionError('Second writer lock unexpectedly acquired')
    atomic_json(folder/'complete.json',dict(status='success',schema=schema,at=now(),nb_assertions=len(results),fixture_code_hash=fixture_code_hash()))
    return folder

if __name__=='__main__':
    with writer_lock():print(execute())
