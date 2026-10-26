"""Run selected candidate phases with archived artifacts and stable input metadata."""
import argparse,hashlib,json,yaml
from catalogue import ROOT
from runtime import *

def prepare():
    capture=json.loads((STATE/'last_capture.json').read_text(encoding='utf-8'))
    rules=yaml.safe_load((DBT/'config/case_rules.yml').read_text(encoding='utf-8'))
    code=code_fingerprint()
    c=client()
    import importlib.metadata
    versions=dict(server=c.query('select version()').first_row[0],serialization='typed_json_v1',dbt_core=importlib.metadata.version('dbt-core'),dbt_clickhouse=importlib.metadata.version('dbt-clickhouse'))
    first_date=c.query("select min(d) from (select min(toDate(src_created_at,'Europe/Paris')) as d from stg_boond.stg_boond_opportunities union all select min(toDate(src_started_at,'Europe/Paris')) as d from stg_boond.stg_boond_deliveries)").first_row[0]
    target_end=c.query('select toLastDayOfMonth(max(src_month_date)) from stg_reference.stg_ref_sales_targets').first_row[0]
    calendar=dict(calendar_start_date=(first_date.replace(day=1)-datetime.timedelta(days=1)).isoformat(),calendar_end_date=(max(datetime.datetime.now(datetime.UTC).date(),target_end)+datetime.timedelta(days=90)).isoformat())
    admitted={n:{k:v for k,v in fp.items() if k in ['keys_digest','nb_keys']} for n,fp in capture['fingerprints'].items()}
    run=digest(dict(inputs=admitted,code=code,rules=rules,versions=versions,calendar=calendar))
    folder=STATE/'runs'/run
    if (folder/'vars.json').exists():return json.loads((folder/'vars.json').read_text(encoding='utf-8')),folder
    minimum=c.query('select min(src_published_at) from stg_boond.stg_boond_opportunities').first_row[0]
    vars=dict(rules,**calendar,model_run_id=run,test_model_run_id=run,calculated_at=now(),input_cutoff_at=now(),rule_version=digest(dict(code=code,versions=versions)),code_hash=code,source_capture_keys=capture['source_capture_keys'],case_history_start_at=minimum.isoformat(timespec='milliseconds')+'Z',publication_model_run_id=None,server_version=versions['server'],serialization_version=versions['serialization'])
    # Calendar bounds from source dates and target horizon; sentinel service ends excluded.
    atomic_json(folder/'vars.json',vars);atomic_json(folder/'inputs.json',capture)
    atomic_json(STATE/'candidate.json',dict(model_run_id=run,folder=str(folder)))
    return vars,folder

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('select');parser.add_argument('--test',action='store_true');args=parser.parse_args()
    with writer_lock():
        vars,folder=prepare();print('candidate',vars['model_run_id'],flush=True)
        dbt(['test' if args.test else 'run','--select',args.select,'--exclude','tag:publication','--threads','1'],vars,folder,'check_'+str(time.time_ns()))
