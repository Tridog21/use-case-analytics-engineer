"""Durable local execution primitives. No sources are mutated."""
import contextlib,datetime,hashlib,json,os,shutil,subprocess,time
from pathlib import Path
import clickhouse_connect
from catalogue import ROOT

DBT=ROOT/'dbt'
STATE=DBT/'state'
def now():return datetime.datetime.now(datetime.UTC).isoformat(timespec='milliseconds').replace('+00:00','Z')
def digest(value):return hashlib.sha256(json.dumps(value,ensure_ascii=False,separators=(',',':'),sort_keys=True,default=str).encode()).hexdigest()
def atomic_json(path,value):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    temp=path.with_suffix(path.suffix+'.tmp');temp.write_text(json.dumps(value,ensure_ascii=False,indent=2,default=str),encoding='utf-8');os.replace(temp,path)
def code_fingerprint():
    paths=sorted(p for folder in ['models','macros','config','tools','tests'] for p in (DBT/folder).rglob('*') if p.is_file() and p.suffix in ['.sql','.py','.yml'] and '__pycache__' not in str(p))
    paths+= [DBT/'dbt_project.yml',DBT/'profiles.yml']
    return digest([(str(p.relative_to(DBT)),hashlib.sha256(p.read_bytes()).hexdigest()) for p in paths])
class AnalyticalClient:
    """Retry read-only statements after transient shared-server memory rejection."""
    def __init__(self):
        self.connection=clickhouse_connect.get_client(host='localhost',port=8123,database='analytics',settings={'max_threads':1,'max_block_size':64,'join_use_nulls':1})
    def query(self,sql,**kwargs):
        for attempt in range(6):
            try:return self.connection.query(sql,**kwargs)
            except Exception as error:
                if 'MEMORY_LIMIT_EXCEEDED' not in str(error) or attempt==5:raise
                print('Retry transient memory rejection on read',attempt+1,flush=True);time.sleep(.25)
    def __getattr__(self,name):return getattr(self.connection,name)
def client():return AnalyticalClient()
@contextlib.contextmanager
def writer_lock():
    STATE.mkdir(parents=True,exist_ok=True);p=STATE/'writer.lock'
    fd=os.open(p,os.O_CREAT|os.O_EXCL|os.O_WRONLY)
    try:
        os.write(fd,str(os.getpid()).encode());yield
    finally:os.close(fd);p.unlink()
def dbt(args,vars,folder,label,_retry=0):
    folder=Path(folder);folder.mkdir(parents=True,exist_ok=True)
    previous=list(folder.glob(label+'.*'))
    if previous:
        archive=folder/'history'/(label+'_'+str(time.time_ns()));archive.mkdir(parents=True)
        for p in previous:
            if p.is_file():shutil.copyfile(p,archive/p.name)
    atomic_json(folder/(label+'.vars.json'),vars)
    cmd=[str(DBT/'.venv/Scripts/dbt.exe'),*args,'--profiles-dir',str(DBT),'--project-dir',str(DBT),'--vars',json.dumps(vars)]
    start=now();t=time.monotonic()
    environment=dict(os.environ,PYTHONUTF8='1',PYTHONIOENCODING='utf-8')
    result=subprocess.run(cmd,cwd=DBT,capture_output=True,text=True,encoding='utf-8',errors='replace',env=environment)
    (folder/(label+'.log')).write_text(result.stdout+'\n'+result.stderr,encoding='utf-8')
    for name in ['manifest.json','run_results.json']:
        p=DBT/'target'/name
        if p.exists():shutil.copyfile(p,folder/(label+'.'+name))
    event=dict(command=args,start=start,end=now(),exit_code=result.returncode,elapsed_seconds=time.monotonic()-t)
    atomic_json(folder/(label+'.command.json'),event)
    print(label,result.returncode,round(event['elapsed_seconds'],2),flush=True)
    if result.returncode:
        output=result.stdout+result.stderr
        if _retry<3 and args[0] in ['run','test'] and 'MEMORY_LIMIT_EXCEEDED' in output:
            rr=json.loads((DBT/'target/run_results.json').read_text(encoding='utf-8'))
            manifest=json.loads((folder/(label+'.manifest.json')).read_text(encoding='utf-8'))
            selectable=dict(manifest.get('nodes',{}),**manifest.get('unit_tests',{}))
            failures=[selectable[r['unique_id']]['name'] for r in rr['results'] if r['status'] in ['error','skipped']]
            if failures and not any(r['status']=='fail' for r in rr['results']):
                retry_args=[args[0],'--select',' '.join(failures),'--threads','1']
                if '--exclude' in args:retry_args+=['--exclude',args[args.index('--exclude')+1]]
                retried=dbt(retry_args,vars,folder,label,_retry+1)
                retry_result=json.loads((DBT/'target/run_results.json').read_text(encoding='utf-8'))
                if not retry_result.get('results'):raise RuntimeError('Retry selected no required nodes')
                return dict(retried,recovered_memory_attempts=_retry+1)
        if args[0]=='run' and 'MEMORY_LIMIT_EXCEEDED' in output and vars.get('write_batch_count',1)==1:
            rr=json.loads((folder/(label+'.run_results.json')).read_text(encoding='utf-8'))
            nodes=json.loads((folder/(label+'.manifest.json')).read_text(encoding='utf-8'))['nodes']
            errors=[r for r in rr['results'] if r['status']=='error']
            if errors and all('MEMORY_LIMIT_EXCEEDED' in r.get('message','') and '__write_bucket' in nodes[r['unique_id']].get('raw_code','') for r in errors):
                completed=[]
                for row in errors:
                    name=nodes[row['unique_id']]['name']
                    for index in range(8):
                        batch_label=label+'.batch.'+name+'.'+str(index)
                        dbt(['run','--select',name,'--threads','1'],dict(vars,write_batch_count=8,write_batch_index=index),folder,batch_label)
                        completed.append(batch_label)
                skipped=[nodes[r['unique_id']]['name'] for r in rr['results'] if r['status']=='skipped']
                if skipped:
                    remaining=label+'.remaining'
                    dbt(['run','--select',' '.join(skipped),'--threads','1'],vars,folder,remaining)
                    completed.append(remaining)
                receipt=dict(event,phase_completed=True,completion_method='8_key_shards',completion_labels=completed)
                atomic_json(folder/(label+'.completion.json'),receipt)
                return receipt
        raise RuntimeError(output[-7000:])
    return event
