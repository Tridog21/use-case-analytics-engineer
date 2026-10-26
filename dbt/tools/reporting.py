"""Fact projections and publication datasets with explicit contracts."""
from business import *

def view(n,expr,fr,ctes=''):
    m=MODELS[n];missing=set(fields(n))-set(expr)
    if missing:raise ValueError(n+' missing: '+','.join(sorted(missing)))
    select=',\n    '.join('CAST('+expr[c['name']]+' AS '+c['type']+') AS `'+c['name']+'`' for c in m['columns'])
    write(m['path'],'\n'.join('-- depends_on: '+ref(dep) for dep in m['refs'])+'\n'+j("config(materialized='view', schema="+repr(m['schema'])+", tags="+repr(['mart'] if n.startswith('fct_') else ['dataset'])+")")+'\n'+('with '+ctes+'\n' if ctes else '')+'select\n    '+select+'\nfrom '+fr+'\n')

def facts():
    date_roles={
        'fct_opportunity_period':{'created_date_key':'created_at','period_start_date_key':'valid_from_at','expected_closing_date_key':'expected_close_at','stage_entered_date_key':'stage_entered_at'},
        'fct_stage_visit':{'entered_date_key':'entered_at','exited_date_key':'exited_at'},
        'fct_opportunity_event':{'created_date_key':'created_at'},
        'fct_opportunity_followup':{'created_date_key':'created_at','anchor_date_key':'anchor_at','observation_date_key':'observation_at','horizon_date_key':'horizon_at','cohort_date_key':'cohort_month'},
        'fct_action':{'created_date_key':'created_at','scheduled_start_date_key':'scheduled_start_at','actual_event_date_key':'actual_event_at'},
        'fct_demo_interval':{'started_date_key':'started_at','ended_date_key':'ended_at'},
        'fct_mrr_movement':{'month_date_key':'month_date','closing_date_key':'month_end_date','previous_closing_date_key':'previous_month_end_date'},
        'fct_subscription_month_end':{'month_date_key':'month_date'},
        'fct_sales_objectives_month':{'month_date_key':'month_date','closing_date_key':'month_end_date'}}
    for n,roles in date_roles.items():
        src=MODELS[n]['refs'][0];e={c:'f.'+c for c in fields(n) if c in fields(src)};fr=ref(src)+' f'
        for output,col in roles.items():
            a='date_'+output;fr+=' left join '+ref('dim_date')+' '+a+' on f.model_run_id='+a+'.model_run_id and '+a+'.calendar_date=toDate(f.'+col+",'Europe/Paris')";e[output]=a+'.date_key'
        if n=='fct_stage_visit':
            fr+=' left join '+ref('int_opportunity_periods')+' p on f.model_run_id=p.model_run_id and f.tenant_id=p.tenant_id and f.opportunity_key=p.opportunity_key and ifNull(f.entered_at,f.first_observed_at)>=p.valid_from_at and (p.valid_to_at is null or ifNull(f.entered_at,f.first_observed_at)<p.valid_to_at)'
            for c in ['stage_key','stage_version_key','company_id','company_key','company_version_key','sale_type_id','sale_type_key','sale_type_version_key','acquisition_channel_key','channel_version_key','channel_candidate_code']:e[c]='p.'+c
            e['is_channel_calculable']='ifNull(p.is_channel_calculable,false)'
            for obj in ['employee','team']:
                for suffix in ['key','version_key']:e['entry_'+obj+'_'+suffix]='if(f.entered_at is not null,p.'+obj+'_'+suffix+',NULL)'
            e.update(entry_context_time_basis="if(f.entered_at is null,'first_observed_at_only','entered_at')",is_team_filter_available='f.entered_at is not null and p.team_key is not null')
            e['source_published_at']='greatest(f.source_published_at,p.source_published_at)'
            e['source_version_keys']='arraySort(arrayDistinct(arrayConcat(f.source_version_keys,ifNull(p.source_version_keys,[]))))'
        if n=='fct_opportunity_event':
            for role in ['from','to']:e[role+'_stage_key']='if(f.'+role+'_stage_id is not null,'+key('stage_v1',('tenant_id','String','f.tenant_id'),('stage_id','Int64','f.'+role+'_stage_id'))+',NULL)'
        view(n,e,fr)

def enriched(n,src,e=None,fr=None,ctes=''):
    e={} if e is None else e
    for c in fields(n):
        if c not in R and c in fields(src) and c not in e:e[c]='f.'+c
    fr=ref(src)+' f' if fr is None else fr
    # Only N:0..1 joins, keyed by model_run_id and dimension version.
    additions={
        'company_name':('dim_company','co','company_version_key','company_version_key','company_name'),
        'stage_label':('dim_stage','st','stage_version_key','stage_version_key','stage_label'),
        'target_stage_label':('dim_stage','tst','target_stage_version_key','stage_version_key','stage_label'),
        'from_stage_label':('dim_stage','fst','from_stage_version_key','stage_version_key','stage_label'),
        'to_stage_label':('dim_stage','tost','to_stage_version_key','stage_version_key','stage_label'),
        'sale_type_label':('dim_sale_type','ty','sale_type_version_key','sale_type_version_key','sale_type_label'),
        'sale_path_code':('dim_sale_type','typ','sale_type_version_key','sale_type_version_key','sale_type_code'),
        'channel_label':('dim_channel','ch','channel_version_key','channel_version_key','channel_label'),
        'employee_display_name':('dim_employee','em','employee_version_key','employee_version_key','employee_display_name'),
        'team_name':('dim_team','tm','team_version_key','team_version_key','team_name'),
        'entry_team_name':('dim_team','etm','entry_team_version_key','team_version_key','team_name'),
        'metric_label':('dim_metric','mt','metric_version_key','metric_version_key','metric_label'),
        'action_type_label':('dim_action_type','at','action_type_version_key','action_type_version_key','action_type_label')}
    for c,(dim,a,fk,pk,label) in additions.items():
        if c not in fields(n) or c in e:continue
        if fk not in fields(src):raise ValueError(n+' missing join key '+fk)
        fr+=' left join '+ref(dim)+' '+a+' on f.model_run_id='+a+'.model_run_id and f.'+fk+'='+a+'.'+pk
        e[c]=a+'.'+label
    if 'channel_key' in fields(n) and 'channel_key' not in e:e['channel_key']='f.acquisition_channel_key'
    fr+=(' and ' if ' where ' in fr else ' where ')+'f.model_run_id='+RUN
    return e,fr,ctes

def dtrs():
    n='dtr_sales_objectives_month';e,fr,c=enriched(n,'fct_sales_objectives_month');build(n,e,fr,c,['tenant_id','month_date','source_segment','metric_code'])
    n='dtr_pipeline_periods';e=dict(is_demo_stage='if(f.stage_version_key is not null,f.stage_id=24,NULL)',is_amount_calculable='false',is_probability_calculable='f.signature_probability is not null',is_left_censored='f.stage_entered_at is null')
    e,fr,c=enriched(n,'fct_opportunity_period',e);build(n,e,fr,c,['tenant_id','period_key'])
    n='dtr_stage_visits';e=dict(observation_end_at='f.observation_ended_at',is_entry_date_known='f.entered_at is not null');e,fr,c=enriched(n,'fct_stage_visit',e);build(n,e,fr,c,['tenant_id','visit_key'])
    n='dtr_sales_events';e=dict(event_date="toDate(f.event_at,'Europe/Paris')",is_generated_amount_calculable='false',is_signed_mrr_calculable='false',completed_cycle_duration_days='f.completed_cycle_duration_seconds/86400.',is_eligible='f.is_contribution_eligible');e,fr,c=enriched(n,'fct_opportunity_event',e);build(n,e,fr,c,['tenant_id','event_key'])
    n='dtr_cohort_outcomes';e=dict(nb_cohort_membership='1');e,fr,c=enriched(n,'fct_opportunity_followup',e);fr+=" and f.followup_kind='cohort_outcome'";build(n,e,fr,c,['tenant_id','opportunity_key','followup_definition_key','anchor_key','horizon_days'])
    n='dtr_funnel_progress';e=dict(is_definition_enabled='true',transition_reached_at='tr.first_reached_at',previous_stage_first_reached_at='tr.anchor_at');e,fr,c=enriched(n,'fct_opportunity_followup',e)
    e['target_stage_label']="if(f.target_stage_id=0,'Création',tst.stage_label)"
    # Stage-transition definitions use first A, independently of first B in funnel reach.
    fr=fr.replace(' where f.model_run_id=', ' left join '+ref('fct_opportunity_followup')+" tr on f.model_run_id=tr.model_run_id and f.tenant_id=tr.tenant_id and f.opportunity_key=tr.opportunity_key and tr.followup_kind='stage_transition' and tr.source_stage_id=f.previous_target_stage_id and tr.target_stage_id=f.target_stage_id where f.model_run_id=")
    fr+=" and f.followup_kind='funnel_reach'";build(n,e,fr,c,['tenant_id','opportunity_key','followup_definition_key','anchor_at','target_stage_id'])
    n='dtr_sales_actions';src='fct_action'
    cte='latest as (select '+cols_sql(list(fields(src)))+' from '+ref(src)+' qualify row_number() over (partition by model_run_id,tenant_id,action_key order by valid_from_at desc)=1)'
    e=dict(source_action_version_key='f.action_version_key',action_state_valid_from_at='f.valid_from_at',action_state_valid_to_at='f.valid_to_at',request_counting_at='if(f.is_demo_request and not f.is_source_deleted,f.created_at,NULL)',demo_counting_at='NULL',nb_demo_request_contribution='multiIf(f.is_source_deleted,0,f.action_type_id is null or (f.is_demo_request and f.created_at is null),NULL,f.is_demo_request,1,0)',nb_realized_demo_contribution='NULL',sale_type_id='p.sale_type_id',sale_type_key='p.sale_type_key',sale_type_version_key='p.sale_type_version_key',sale_type_label='ty.sale_type_label')
    fr='latest f left join '+ref('fct_opportunity_period')+' p on f.model_run_id=p.model_run_id and f.tenant_id=p.tenant_id and f.opportunity_key=p.opportunity_key and if(f.is_demo_request,f.created_at,f.actual_event_at)>=p.valid_from_at and (p.valid_to_at is null or if(f.is_demo_request,f.created_at,f.actual_event_at)<p.valid_to_at) left join '+ref('dim_sale_type')+' ty on p.model_run_id=ty.model_run_id and p.sale_type_version_key=ty.sale_type_version_key'
    e,fr,c=enriched(n,src,e,fr,cte);build(n,e,fr,c,['tenant_id','action_key'])
    n='dtr_demo_intervals';e=dict(demo_journey_id='f.demo_journey_key',is_interval_calculable='false',is_team_filter_available='false');e,fr,c=enriched(n,'fct_demo_interval',e);build(n,e,fr,c,['tenant_id','demo_interval_key'])

def revenue_dtr():
    src='fct_mrr_movement';n='dtr_company_mrr_month'
    cte='totals as (select model_run_id,tenant_id,company_key,month_date,count() as expected,countIf(is_active is not null) as known_states,countIf(is_active) as active_lines,if(active_lines>0,true,if(known_states=expected,false,NULL)) as active,if(countIf(sum_active_mrr is not null)=expected,sum(sum_active_mrr),NULL) as mrr from '+ref('fct_subscription_month_end')+' where model_run_id='+RUN+' and company_key is not null group by model_run_id,tenant_id,company_key,month_date)'
    fr=ref(src)+' f left join totals a on f.model_run_id=a.model_run_id and f.tenant_id=a.tenant_id and f.company_key=a.company_key and f.month_date=a.month_date left join totals b on f.model_run_id=b.model_run_id and f.tenant_id=b.tenant_id and f.company_key=b.company_key and b.month_date=addMonths(f.month_date,-1)'
    e=dict(closing_date='f.month_end_date',previous_closing_date='f.previous_month_end_date',is_active_begin='b.active',is_active_end='a.active',nb_active_lines_begin='b.active_lines',nb_active_lines_end='a.active_lines',sum_mrr_begin='b.mrr',sum_mrr_end='a.mrr',sum_new_mrr_new="if(f.is_comparable,if(f.new_mrr_component='New',f.sum_new_mrr,toDecimal128(0,4)),NULL)",sum_new_mrr_upsell="if(f.is_comparable,if(f.new_mrr_component='Upsell',f.sum_new_mrr,toDecimal128(0,4)),NULL)",sum_churn_mrr='f.sum_departure_mrr+f.sum_contraction_mrr',sum_other_mrr_delta='if(f.is_comparable,toDecimal128(0,4),NULL)',sum_reconciliation_gap='a.mrr-b.mrr-f.sum_new_mrr+f.sum_departure_mrr+f.sum_contraction_mrr-sum_other_mrr_delta',is_first_acquisition="multiIf(f.first_acquisition_status='first_proven',true,f.first_acquisition_status='return_proven',false,NULL)",is_begin_observable='b.expected is not null and b.expected=b.known_states',is_end_observable='a.expected is not null and a.expected=a.known_states')
    e,fr,c=enriched(n,src,e,fr,cte);build(n,e,fr,c,['tenant_id','company_key','closing_date'])

def timeline():
    n='dtr_opportunity_timeline';out=fields(n);projections=[]
    branch=[('fct_opportunity_period','opportunity_period','period_key','valid_from_at','valid_to_at'),('fct_stage_visit','stage_visit','visit_key','entered_at','exited_at'),('fct_opportunity_event','opportunity_event','event_key','event_at',None),('int_visit_responsibility','responsibility_slice','responsibility_slice_key','valid_from_at','valid_to_at')]
    label_cols={'company_name','stage_label','sale_type_label','employee_display_name','team_name'}
    for src,kind,obj,start,end in branch:
        src_cols=fields(src);e={c:'f.'+c for c in out if c not in R and c in src_cols};fr=ref(src)+' f'
        e.update(object_kind=q(kind),object_key='f.'+obj,source_model_name=q(src),source_record_version_key='f.record_version_key',started_at='f.'+start,ended_at='f.'+end if end else 'NULL',slice_duration_seconds='NULL',slice_duration_days='NULL')
        if kind=='stage_visit':
            e.update(employee_key='f.entry_employee_key',employee_version_key='f.entry_employee_version_key',team_key='f.entry_team_key',team_version_key='f.entry_team_version_key',is_team_calculable='f.is_team_filter_available',time_basis='f.event_time_basis')
        elif kind=='opportunity_event':e.update(stage_key='NULL',stage_version_key='NULL',time_basis='f.event_time_basis')
        elif kind=='opportunity_period':e.update(is_left_censored='f.stage_entered_at is null',time_basis="'observed_context'")
        else:
            fr+=' left join '+ref('fct_stage_visit')+' v on f.model_run_id=v.model_run_id and f.tenant_id=v.tenant_id and f.visit_key=v.visit_key'
            for c in ['opportunity_id','company_key','company_version_key','company_id','stage_key','stage_version_key','sale_type_id','sale_type_key','sale_type_version_key']:e[c]='v.'+c
            e.update(is_team_calculable='f.is_team_filter_available',time_basis="'observed_responsibility_slice'",slice_duration_seconds="if(f.allocation_status='validated',f.allocated_duration_seconds,NULL)",slice_duration_days='slice_duration_seconds/86400.')
        for c,d in out.items():
            if c not in R and c not in e and c not in label_cols:
                if d['nullable']:e[c]='NULL'
                else:raise ValueError('Timeline missing '+kind+' '+c)
        # Enrich against the explicit expressions of each branch, preserving its grain.
        for col,dim,pk in [('company_name','dim_company','company_version_key'),('stage_label','dim_stage','stage_version_key'),('sale_type_label','dim_sale_type','sale_type_version_key'),('employee_display_name','dim_employee','employee_version_key'),('team_name','dim_team','team_version_key')]:
            a='label_'+col;fr+=' left join '+ref(dim)+' '+a+' on f.model_run_id='+a+'.model_run_id and '+e[pk]+'='+a+'.'+pk;e[col]=a+'.'+col
        cols=[c for c in out if c not in R]
        projections.append('select '+',\n'.join('CAST('+e[c]+' AS '+out[c]['type']+') AS '+c for c in cols)+' from '+fr+' where f.model_run_id='+RUN)
    e={c:c for c in out if c not in R};build(n,e,'timeline','timeline as ('+' union all '.join(projections)+')',['tenant_id','object_kind','object_key'])

def publication():
    m=MODELS['int_publication']
    sql=j("config(materialized='table',schema='dwh_common',engine='MergeTree()',order_by='tuple()',tags=['publication'])")+'\nselect\n'
    e=dict(model_run_id=j("ch_literal(var('publication_model_run_id',''))"),published_at=ts('publication_at'),input_cutoff_at=CUTOFF,rule_version=RULE,quality_json=j("ch_literal(var('publication_quality_json','[]'))"))
    # Bootstrap constants are typed; no source relation is required.
    e['model_run_id']="ifNull("+e['model_run_id']+",'')"
    e['publication_key']=key('publication_v1',('model_run_id','String','model_run_id'),('published_at',"DateTime64(3,'UTC')",'published_at'))
    sql+=',\n'.join('CAST('+e[c['name']]+' AS '+c['type']+') AS '+c['name'] for c in m['columns'])+"\n{% if var('publication_model_run_id',none) is none %}where false{% endif %}\n"
    write(m['path'],sql)
    for n,m in MODELS.items():
        if not n.startswith('dataset_') or n=='dataset_publication_status':continue
        src=m['refs'][0];view(n,{c:'f.'+c for c in fields(n)},ref(src)+' f inner join '+ref('int_publication')+' p on f.model_run_id=p.model_run_id')
    n='dataset_publication_status';e={c:'p.'+c for c in ['model_run_id','publication_key','published_at','input_cutoff_at','rule_version']}
    for c in ['measure_id','dataset_family','availability_status','coverage_status']:e[c]="JSONExtractString(item,'"+c+"')"
    e['availability_reason']="JSONExtract(item,'availability_reason','Nullable(String)')"
    for c in ['nb_expected','nb_known']:e[c]="JSONExtract(item,'"+c+"','Nullable(UInt64)')"
    e['data_coverage_end_at']="parseDateTime64BestEffortOrNull(JSONExtract(item,'data_coverage_end_at','Nullable(String)'),3,'UTC')"
    view(n,e,ref('int_publication')+' p array join JSONExtractArrayRaw(p.quality_json) as item')

if __name__=='__main__':facts();dtrs();revenue_dtr();timeline();publication()
