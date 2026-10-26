"""Resume publication of an accepted, unchanged candidate without rebuilding it.

Reuse the successful full recomposition and physical-contract receipts, verify
their stored rows/checksums, then run only the remaining publication checks.
Disable dbt's eager relation-cache population to avoid unnecessary metadata scans.
"""
import json,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'dbt/tools'))
from runtime import *
from catalogue import MODELS
from run_case import relation,verify_published
from quality import summarize

def execute(run):
    with writer_lock():
        folder=STATE/'runs'/run
        vars=json.loads((folder/'vars.json').read_text(encoding='utf-8'))
        accepted=json.loads((folder/'candidate_acceptance.json').read_text(encoding='utf-8'))
        if accepted.get('status')!='accepted' or accepted['model_run_id']!=run:raise RuntimeError('Candidate not accepted')
        if code_fingerprint()!=vars['code_hash']:raise RuntimeError('Accepted code changed')
        recompositions=json.loads((folder/'recompositions.json').read_text(encoding='utf-8'))
        contracts=json.loads((folder/'contracts.json').read_text(encoding='utf-8'))
        if len(recompositions)!=37 or len(contracts)!=73:raise RuntimeError('Required successful receipts missing')
        previous=json.loads((folder/'execution.json').read_text(encoding='utf-8'))
        atomic_json(folder/('execution_'+str(time.time_ns())+'.json'),previous)
        manifest={k:v for k,v in previous.items() if k not in ['error','end','observed_publication_after_failure']}
        manifest.update(status='running',start=now(),phase='publish',resume_method='accepted_rows_and_checksums_then_remaining_publication_controls')
        for p in folder.glob('execution_*.json'):
            evidence=json.loads(p.read_text(encoding='utf-8'))
            if evidence.get('candidate_tests_passed') and evidence.get('status')=='success':manifest['fixture_code_hash']=evidence.get('fixture_code_hash')
        atomic_json(folder/'execution.json',manifest)
        c=client()
        def command(label,args):
            if code_fingerprint()!=vars['code_hash']:raise RuntimeError('Code changed during publication')
            for attempt in range(3):
                try:
                    event=dbt(args+['--no-populate-cache'],vars,folder,label)
                    if args[0] in ['run','test']:
                        results=json.loads((folder/(label+'.run_results.json')).read_text(encoding='utf-8'))['results']
                        if not results or any(r['status'] not in ['success','pass'] for r in results):raise RuntimeError('Required node not successful: '+label)
                    manifest['commands'].append(event);atomic_json(folder/'execution.json',manifest)
                    return
                except RuntimeError as e:
                    if 'MEMORY_LIMIT_EXCEEDED' not in str(e) or attempt==2:raise
                    print('Retry publication metadata rejection',label,attempt+1,flush=True)
        def analyses(label):
            command(label,['compile','--select','resource_type:analysis'])
            checks={}
            for source in sorted((DBT/'analyses').glob('*.sql')):
                path=DBT/'target/compiled/use_case/analyses'/source.name
                sql=path.read_text(encoding='utf-8');started=time.monotonic()
                result=c.query(sql)
                checks[source.stem]=dict(status='success',nb_rows=len(result.result_rows),elapsed_seconds=time.monotonic()-started)
            atomic_json(folder/'analysis_contracts.json',checks)
        try:
            unchanged={}
            for name,receipt in recompositions.items():
                m=MODELS[name]
                rows=c.query('select record_key,row_hash from '+relation(m)+' where model_run_id={run:String} order by record_key',parameters={'run':run}).result_rows
                cols=','.join('`'+x['name']+'`' for x in m['columns'])
                count,checksum=c.query('select count(),sum(cityHash64(tuple('+cols+'))) from '+relation(m)+' where model_run_id={run:String}',parameters={'run':run}).first_row
                if len(rows)!=receipt['nb_loaded'] or digest(rows)!=receipt['digest'] or count!=contracts[name]['nb_rows'] or checksum!=contracts[name]['evaluation_checksum']:raise RuntimeError('Accepted candidate changed: '+name)
                unchanged[name]=dict(nb_rows=count,digest=receipt['digest'],evaluation_checksum=checksum)
            atomic_json(folder/'publication_resume_integrity.json',dict(status='success',at=now(),checks=unchanged))
            print('Accepted snapshot unchanged: 37 models',flush=True)
            # The two preceding deployment attempts already created the eleven views
            # and passed the 73 physical schema/value checks and dataset-contract test.
            prior_test=json.loads((folder/'dataset_contracts.run_results.json').read_text(encoding='utf-8'))['results']
            if not prior_test or any(x['status']!='pass' for x in prior_test):raise RuntimeError('Dataset contract not accepted')
            analyses('analysis_compile')
            quality=summarize(vars,c);atomic_json(folder/'quality.json',quality)
            saved=folder/'publish.vars.json'
            if saved.exists():
                request=json.loads(saved.read_text(encoding='utf-8'))
                if request['publication_model_run_id']!=run or json.loads(request['publication_quality_json'])!=quality:raise RuntimeError('Publication request changed')
                vars=request
            else:vars=dict(vars,publication_model_run_id=run,publication_at=now(),publication_quality_json=json.dumps(quality,ensure_ascii=False))
            atomic_json(saved,vars)
            manifest['previous_publication']=c.query('select model_run_id,publication_key from dwh_common.int_publication').result_rows
            command('quality_candidate',['test','--select','assert_publication_quality_candidate'])
            command('publish',['run','--select','int_publication','--threads','1'])
            verify_published(vars,folder)
            command('published_tests',['test','--select','assert_published_datasets_one_run'])
            analyses('analysis_compile_published')
            manifest.update(status='success',end=now());atomic_json(folder/'execution.json',manifest)
            print('SUCCESS published',run,flush=True)
        except Exception as e:
            manifest.update(status='failed',end=now(),error=str(e))
            try:manifest['observed_publication_after_failure']=c.query('select model_run_id,publication_key,published_at from dwh_common.int_publication').result_rows
            except Exception as read_error:manifest['publication_read_error']=str(read_error)
            atomic_json(folder/'execution.json',manifest);raise

if __name__=='__main__':execute(sys.argv[1])
