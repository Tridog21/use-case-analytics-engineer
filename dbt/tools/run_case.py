"""Manual case runner. Captures -> frozen candidate -> tests -> isolated publication."""
import argparse,json,re
from catalogue import ROOT,MODELS
from runtime import *
from capture import capture_all
from validate import prepare
from quality import summarize,validate_quality,REGISTRY

def relation(m):return '`'+m['schema']+'`.`'+m['name']+'`'

def verify_recompositions(vars,folder):
    c=client();checks={}
    dbt(['compile','--select','tag:common tag:pipeline tag:revenue tag:mart tag:dtr','--exclude','tag:publication'],vars,folder,'recomposition_compile')
    for n,m in MODELS.items():
        if not (n.startswith(('dim_','int_','dtr_'))) or n=='int_publication':continue
        compiled=DBT/'target/compiled/use_case'/Path(m['path']).relative_to('dbt')
        sql=compiled.read_text(encoding='utf-8')
        prefix=sql.rsplit('\nselect\n    c.`model_run_id`',1)[0]
        if prefix==sql:raise RuntimeError('Missing candidate CTE '+n)
        expected=c.query(prefix+'\nselect record_key,row_hash from candidate order by record_key',settings={'max_threads':1,'max_block_size':64}).result_rows
        loaded=c.query('select record_key,row_hash from '+relation(m)+' where model_run_id={run:String} order by record_key',parameters={'run':vars['model_run_id']},settings={'max_threads':1}).result_rows
        if expected!=loaded:raise RuntimeError('Incomplete or divergent candidate '+n)
        if len({r[0] for r in loaded})!=len(loaded):raise RuntimeError('Duplicate grain '+n)
        checks[n]=dict(nb_expected=len(expected),nb_loaded=len(loaded),digest=digest(expected))
    atomic_json(folder/'recompositions.json',checks);return checks

def verify_contracts(vars,folder):
    c=client();checks={}
    for n,m in MODELS.items():
        actual=c.query('select name,type from system.columns where database={db:String} and table={table:String} order by position',parameters={'db':m['schema'],'table':n}).result_rows
        cols=m['columns']
        if n.startswith('stg_'):
            from generate import ST
            cols=cols+[dict(name=k,type=t) for k,t,d in ST]
        canonical=lambda t:t.replace(' ','')
        exp=[(x['name'],canonical(x['type'])) for x in cols]
        act=[(x[0],canonical(x[1])) for x in actual]
        if exp!=act:raise RuntimeError('Physical schema mismatch '+n+' '+str([(a,b) for a,b in zip(exp,act) if a!=b]))
        projection=', '.join('`'+x['name']+'`' for x in cols)
        where=' where model_run_id={run:String}' if n.startswith(('dim_','fct_','dtr_')) or (n.startswith('int_') and n!='int_publication') else ''
        evaluated=c.query('select count(),sum(cityHash64(tuple('+projection+'))) from '+relation(m)+where,parameters={'run':vars['model_run_id']}).first_row
        checks[n]=dict(nb_columns=len(actual),nb_rows=evaluated[0],evaluation_checksum=evaluated[1])
    atomic_json(folder/'contracts.json',checks);return checks

def verify_published(vars,folder):
    c=client();run=vars['model_run_id'];ptr=c.query('select model_run_id from dwh_common.int_publication').result_rows
    if ptr!=[(run,)]:raise RuntimeError('Publication pointer does not match accepted candidate')
    for n,m in MODELS.items():
        if not n.startswith('dataset_') or n=='dataset_publication_status':continue
        src=m['refs'][0];cols=', '.join('`'+x['name']+'`' for x in m['columns'])
        published=c.query('select '+cols+' from '+relation(m)+' order by record_key').result_rows
        candidate=c.query('select '+cols+' from '+relation(MODELS[src])+' where model_run_id={run:String} order by record_key',parameters={'run':run}).result_rows
        if published!=candidate:raise RuntimeError('Published projection differs '+n)
    quality=c.query('select measure_id from dtr_sales.dataset_publication_status').result_rows
    if len(quality)!=30:raise RuntimeError('Publication quality registry incomplete')
    atomic_json(folder/'published_read_check.json',dict(status='success',at=now(),model_run_id=run,nb_datasets=11,nb_measures=30))

def verify_analysis_contracts(vars,folder):
    dbt(['compile','--select','resource_type:analysis'],vars,folder,'analysis_compile')
    c=client();checks={}
    for source in sorted((DBT/'analyses').glob('*.sql')):
        path=DBT/'target/compiled/use_case/analyses'/source.name
        sql=path.read_text(encoding='utf-8');started=time.monotonic()
        result=c.query(sql);plan=c.query('EXPLAIN PIPELINE '+sql).result_rows
        checks[source.stem]=dict(status='success',nb_rows=len(result.result_rows),elapsed_seconds=time.monotonic()-started,plan=[r[0] for r in plan])
    atomic_json(folder/'analysis_contracts.json',checks)

def execute(params):
    phase=params.get('phase','full')
    if phase not in ['full','capture','build','test','publish']:raise ValueError('Unsupported phase')
    with writer_lock():
        if phase in ['full','capture']:
            allowed,fingerprints,jobs=capture_all();atomic_json(STATE/'last_capture.json',dict(source_capture_keys=allowed,fingerprints=fingerprints,jobs=jobs))
            if phase=='capture':return
        if params.get('resume_model_run_id'):
            folder=STATE/'runs'/params['resume_model_run_id'];vars=json.loads((folder/'vars.json').read_text(encoding='utf-8'))
        else:vars,folder=prepare()
        manifest=dict(model_run_id=vars['model_run_id'],status='running',start=now(),phase=phase,commands=[],code_hash=vars['code_hash'],rule_version=vars['rule_version'],vars_hash=digest(vars),input_cutoff_at=vars['input_cutoff_at'],source_capture_keys=vars['source_capture_keys'])
        previous=folder/'execution.json'
        previous_execution=json.loads(previous.read_text(encoding='utf-8')) if previous.exists() else {}
        if previous.exists():atomic_json(folder/('execution_'+str(time.time_ns())+'.json'),previous_execution)
        atomic_json(previous,manifest)
        def command(label,args):
            if code_fingerprint()!=vars['code_hash']:raise RuntimeError('Code changed during immutable candidate execution; prepare a new run')
            result=dbt(args,vars,folder,label);manifest['commands'].append(result);atomic_json(previous,manifest)
            if args[0] in ['run','test']:
                results=json.loads((folder/(label+'.run_results.json')).read_text(encoding='utf-8'))
                if not result.get('phase_completed') and any(r['status'] in ['skipped','fail','error'] for r in results.get('results',[])):raise RuntimeError('Required checks skipped or failed in '+label)
        try:
            if phase in ['full','build']:
                command('parse',['parse','--no-partial-parse'])
                command('capture_tests',['test','--select','tag:capture','--exclude','tag:publication','--indirect-selection','cautious'])
                command('common',['run','--select','tag:common','--exclude','tag:publication','--threads','1'])
                command('business',['run','--select','tag:pipeline tag:revenue tag:mart','--exclude','tag:publication','--threads','1'])
                command('dtr',['run','--select','tag:dtr','--exclude','tag:publication','--threads','1'])
            if phase in ['full','build','test']:
                from integration_fixtures import execute as integration_execute,fixture_code_hash
                fixture_manifests=[json.loads(p.read_text(encoding='utf-8')) for p in (STATE/'fixtures').glob('*/complete.json')]
                if not any(x.get('status')=='success' and x.get('fixture_code_hash')==fixture_code_hash() for x in fixture_manifests):integration_execute()
                manifest['fixture_code_hash']=fixture_code_hash();atomic_json(previous,manifest)
                command('unit_tests',['test','--select','test_type:unit','--exclude','tag:publication'])
                command('candidate_tests',['test','--select','tag:common tag:pipeline tag:revenue tag:mart tag:dtr','--exclude','tag:publication test_type:unit'])
                verify_recompositions(vars,folder)
                manifest['candidate_tests_passed']=True;atomic_json(previous,manifest)
            if phase in ['full','publish']:
                if phase=='publish':
                    prior=json.loads((folder/'candidate_acceptance.json').read_text(encoding='utf-8'))
                    if prior['model_run_id']!=vars['model_run_id'] or prior['status']!='accepted':raise RuntimeError('Publication requires accepted candidate manifest')
                    verify_recompositions(vars,folder)
                c=client();exists=c.query("select count() from system.tables where database='dwh_common' and name='int_publication'").first_row[0]
                if not exists:command('bootstrap',['run','--select','int_publication','--threads','1'])
                command('datasets',['run','--select','tag:dataset','--exclude','tag:publication','--threads','1'])
                verify_contracts(vars,folder)
                command('dataset_contracts',['test','--select','assert_dataset_contracts'])
                verify_analysis_contracts(vars,folder)
                quality=summarize(vars,c);atomic_json(folder/'quality.json',quality)
                atomic_json(folder/'candidate_acceptance.json',dict(model_run_id=vars['model_run_id'],status='accepted',at=now()))
                old=c.query('select model_run_id,publication_key from dwh_common.int_publication').result_rows
                saved_path=folder/'publish.vars.json'
                saved=json.loads(saved_path.read_text(encoding='utf-8')) if saved_path.exists() else None
                if previous_execution.get('status')=='failed' and saved:
                    if saved['publication_model_run_id']!=vars['model_run_id'] or json.loads(saved['publication_quality_json'])!=quality:raise RuntimeError('Retry publication request diverges from frozen request')
                    vars=saved
                else:
                    vars=dict(vars,publication_model_run_id=vars['model_run_id'],publication_at=now(),publication_quality_json=json.dumps(quality,ensure_ascii=False))
                atomic_json(saved_path,vars)
                manifest['previous_publication']=old;atomic_json(previous,manifest)
                command('quality_candidate',['test','--select','assert_publication_quality_candidate'])
                command('publish',['run','--select','int_publication','--threads','1'])
                verify_published(vars,folder)
                command('published_tests',['test','--select','assert_published_datasets_one_run'])
                verify_analysis_contracts(vars,folder)
            manifest.update(status='success',end=now());atomic_json(previous,manifest)
            if phase in ['build','test']:atomic_json(folder/'candidate_acceptance.json',dict(model_run_id=vars['model_run_id'],status='accepted',at=now()))
            print('SUCCESS',phase,vars['model_run_id'])
        except Exception as e:
            try:
                c=client()
                if c.query("select count() from system.tables where database='dwh_common' and name='int_publication'").first_row[0]:manifest['observed_publication_after_failure']=c.query('select model_run_id,publication_key,published_at from dwh_common.int_publication').result_rows
            except Exception as read_error:manifest['publication_read_error']=str(read_error)
            manifest.update(status='failed',end=now(),error=str(e));atomic_json(previous,manifest);raise

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--params',required=True,type=Path);a=p.parse_args();execute(json.loads(a.params.read_text(encoding='utf-8')))
