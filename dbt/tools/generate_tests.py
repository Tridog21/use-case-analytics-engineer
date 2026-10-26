"""Executable data contracts and typed transformation fixtures."""
from reporting import *

def test_file(name,sql,tags):
    write('dbt/tests/'+name+'.sql',j('config(tags='+repr(tags)+')')+'\n'+sql+'\n')

def data_tests():
    for n,m in MODELS.items():
        if n in ['int_publication','dataset_publication_status'] or n.startswith('dataset_'):continue
        names=list(fields(n));capture=n.startswith('stg_');tags=['capture'] if capture else ['common'] if n.startswith('dim_') or m['schema']=='dwh_common' else ['mart'] if n.startswith('fct_') else ['dtr'] if n.startswith('dtr_') else ['pipeline'] if m['schema']=='dwh_pipeline' else ['revenue']
        if capture:
            expected=hash_expr('source_payload_v1:'+'.'.join(m['source']),[(c['name'],c['type'],c['name']) for c in m['columns']])
            test_file('T02_payload_'+n,'select source_version_key from '+ref(n)+' where source_payload_hash!='+expected,tags)
            floats=[c['name'] for c in m['columns'] if 'Float' in c['type']]
            if floats:test_file('T18_finite_'+n,'select source_version_key from '+ref(n)+' where '+' or '.join('('+c+' is not null and not isFinite('+c+'))' for c in floats),tags)
            if n.startswith('stg_boond_'):
                test_file('T03_'+n,'select source_identity_key,src_published_at from '+ref(n)+' group by source_identity_key,src_published_at having uniqExact(source_payload_hash)>1',tags)
            else:
                test_file('T04_'+n,'select source_identity_key,capture_key from '+ref(n)+' group by source_identity_key,capture_key having count()>1',tags)
            continue
        if n.startswith(('dim_','int_','dtr_')):
            expected=hash_expr(n+':row_v1',[(c['name'],c['type'],c['name']) for c in m['columns'] if c['name'] not in R])
            test_file('T07_content_'+n,'select record_key from '+ref(n)+' where model_run_id='+j("ch_literal(var('test_model_run_id',''))")+' and row_hash!='+expected,tags)
        test_file('T07_'+n,'select record_key from '+ref(n)+' where model_run_id='+j("ch_literal(var('test_model_run_id',''))")+' and (calculated_at!='+ts('calculated_at')+' or input_cutoff_at!='+CUTOFF+' or rule_version!='+RULE+' or length(record_key)!=64 or length(record_version_key)!=64 or length(row_hash)!=64)',tags)
        if 'calculation_status' in names:test_file('T10_status_'+n,'select record_key from '+ref(n)+' where model_run_id='+j("ch_literal(var('test_model_run_id',''))")+" and calculation_status not in ('ready','partial','blocked','not_applicable')",tags)
        if 'valid_from_at' in names and 'valid_to_at' in names:
            test_file('T11_'+n,'select record_key from '+ref(n)+' where model_run_id='+j("ch_literal(var('test_model_run_id',''))")+' and valid_to_at is not null and valid_from_at>=valid_to_at',tags)
            identities={'dim_company':['tenant_id','company_id'],'dim_employee':['tenant_id','employee_id'],'dim_team':['tenant_id','team_id'],'dim_stage':['tenant_id','language','stage_id'],'dim_sale_type':['tenant_id','language','sale_type_id'],'dim_channel':['tenant_id','language','channel_id'],'dim_action_type':['tenant_id','language','action_type_id'],'int_opportunity_periods':['tenant_id','opportunity_id'],'int_actions_prepared':['tenant_id','action_id'],'int_subscription_periods':['tenant_id','line_id'],'int_team_membership_periods':['tenant_id','employee_id','team_id']}
            if n in identities:
                partition=','.join(identities[n])
                sql='with sequenced as (select record_key,valid_from_at,lagInFrame(valid_to_at) over w as prior_end,row_number() over w as row_rank from '+ref(n)+' where model_run_id='+j("ch_literal(var('test_model_run_id',''))")+' window w as (partition by '+partition+' order by valid_from_at rows between unbounded preceding and unbounded following)) select record_key from sequenced where row_rank>1 and (prior_end is null or prior_end>valid_from_at)'
                test_file('T11_nonoverlap_'+n,sql,tags)
    checks={
        'T13_unknown_entry_dates':("int_opportunity_stage_visits",'is_left_censored and (entered_at is not null or completed_duration_seconds is not null)'),
        'T18_decimal_no_multiplication':('int_subscription_periods','abs(line_monthly_amount-recomputed_quantity_price_amount)>toDecimal128(\'0.005\',4)'),
        'T20_no_finalization_sale':('int_opportunity_events',"event_type='signed' and to_stage_id!=1"),
        'T21_signed_mrr_unproven':('fct_opportunity_event','sum_signed_mrr is not null'),
        'T22_demo_proof':('fct_action','is_realized_demo is not null or actual_event_at is not null'),
        'T25_probability_domain':('int_signature_probabilities','probability<0 or probability>1'),
        'T26_objective_incompatible':('fct_sales_objectives_month','actual_value is not null or attainment_rate is not null'),
        'T28_activity_amount_zero':('int_subscription_month_end','is_active and candidate_active_mrr!=line_monthly_amount'),
        'T31_unknown_movement':('int_mrr_movements',"movement_kind='unknown' and (sum_new_mrr is not null or sum_departure_mrr is not null or sum_contraction_mrr is not null)"),
        'T32_reconciliation':('dtr_company_mrr_month','sum_reconciliation_gap is not null and sum_reconciliation_gap!=0'),
        'T34_growth_components':('dtr_company_mrr_month','sum_new_mrr!=sum_new_mrr_new+sum_new_mrr_upsell'),
        'T36_unknown_prior':('int_client_activity_context','not is_comparable and mrr_before is null and calculation_status=\'ready\''),
        'T38_censored_durations':('fct_stage_visit','completed_duration_seconds is not null and (entered_at is null or exited_at is null)'),
        'T42_immature_contributions':('int_opportunity_followup',"followup_kind='cohort_outcome' and not is_cohort_mature and (denominator_contribution is not null or won_contribution is not null)"),
        'T44_outcome_denominator':('int_opportunity_followup',"followup_kind='cohort_outcome' and denominator_contribution is not null and denominator_contribution!=open_contribution+won_contribution+lost_contribution+abandoned_contribution+unqualified_contribution+unknown_contribution"),
        'T51_closing_boundary':('int_subscription_month_end','closing_exclusive_at>'+BOUND),
        'T52_EUR_not_signed':('int_subscription_periods',"currency_code!='EUR'"),
        'T53_shared_schedule':('int_signature_probabilities',"applicability_status='applicable_recomputed_case' and (business_valid_from_at!="+ts('case_history_start_at')+' or business_valid_to_at!='+BOUND+')'),
        'T55_ES_unknown':('int_sales_objectives_month',"source_segment='ES' and (team_key is not null or actual_value is not null or candidate_actual_value is not null)"),
        'T56_channel_no_fallback':('int_opportunity_periods','channel_candidate_code is null and acquisition_channel_key is not null'),
        'T57_old_unknown':('dim_stage',"stage_id in (10,19) and outcome_category!='unknown'"),
        'T61_entry_team':('fct_stage_visit','entered_at is null and (entry_team_key is not null or entry_employee_key is not null)'),
        'T63_first_acquisition':('dtr_company_mrr_month','is_first_acquisition=true'),
        'T64_no_invented_intervals':('dtr_demo_intervals','true')}
    for name,(n,predicate) in checks.items():
        test_file(name,'select record_key from '+ref(n)+' where model_run_id='+j("ch_literal(var('test_model_run_id',''))")+' and ('+predicate+')',['pipeline','revenue','dtr'])
    test_file('T19_one_creation',"select opportunity_key from "+ref('int_opportunity_events')+" where model_run_id="+j("ch_literal(var('test_model_run_id',''))")+" and event_type='pipeline_created' group by opportunity_key having count()!=1",['pipeline'])
    test_file('T58_first_signature_once',"select opportunity_key from "+ref('int_opportunity_events')+" where model_run_id="+j("ch_literal(var('test_model_run_id',''))")+" and event_type='signed' group by opportunity_key having sum(nb_events)>1",['pipeline'])
    test_file('T59_first_terminal_once',"select opportunity_key from "+ref('int_opportunity_events')+" where model_run_id="+j("ch_literal(var('test_model_run_id',''))")+" and completed_cycle_duration_seconds is not null group by opportunity_key having count()>1",['pipeline'])

def fixture_sql(n,rows):
    cols=MODELS[n]['columns']+([dict(name=c,type=t,nullable=False) for c,t,d in ST] if n.startswith('stg_') else [])
    statements=[]
    for row in rows:
        values=[]
        for c in cols:
            name=c['name'];typ=c['type']
            value=row.get(name,None if typ.startswith('Nullable(') else [] if typ.startswith('Array(') else '2026-01-01 00:00:00.000' if 'DateTime' in typ else '2026-01-01' if typ=='Date' else '' if 'String' in typ else 0)
            literal='NULL' if value is None else '['+','.join(q(x) for x in value)+']' if isinstance(value,list) else q(value) if isinstance(value,str) else str(int(value)) if isinstance(value,bool) else str(value)
            values.append('CAST('+literal+' AS '+typ+') AS `'+name+'`')
        statements.append('select '+',\n'.join(values))
    return '\nunion all\n'.join(statements)

def unit_tests():
    # Fixtures exercise the actual production model, including its window segmentation and keys.
    n='stg_boond_opportunities';rows=[]
    for idx,(stage,time,deleted) in enumerate([(22,'09',False),(22,'10',False),(24,'11',False),(22,'12',False),(22,'13',True),(22,'14',False),(1,'15',False),(14,'16',False)]):
        rows.append(dict(src_tenant_id='fixture',src_id=1,src_state_id=stage,src_type_id=4,src_published_at='2026-01-01 '+time+':00:00.123',src_created_at='2025-12-31 09:00:00.123',src_is_deleted=deleted,source_version_key=str(idx),source_identity_key='fixture:1',capture_at='2026-01-02 00:00:00.000'))
    write('dbt/tests/fixtures/visits_input.sql',fixture_sql(n,rows))
    expected=[dict(stage_id=22,visit_rank=1,entered_at=None,exited_at='2026-01-01 11:00:00.123',completed_duration_seconds=None),dict(stage_id=24,visit_rank=2,entered_at='2026-01-01 11:00:00.123',exited_at='2026-01-01 12:00:00.123',completed_duration_seconds=3600),dict(stage_id=22,visit_rank=3,entered_at='2026-01-01 12:00:00.123',exited_at=None,completed_duration_seconds=None),dict(stage_id=22,visit_rank=5,entered_at=None,exited_at='2026-01-01 15:00:00.123',completed_duration_seconds=None),dict(stage_id=1,visit_rank=6,entered_at='2026-01-01 15:00:00.123',exited_at='2026-01-01 16:00:00.123',completed_duration_seconds=3600),dict(stage_id=14,visit_rank=7,entered_at='2026-01-01 16:00:00.123',exited_at=None,completed_duration_seconds=None)]
    tests=[dict(name='T13_T37_T58_observed_visits_returns_deletion',model='int_opportunity_stage_visits',overrides=dict(macros={'is_incremental':False},vars={'model_run_id':'f'*64,'rule_version':'fixture','calculated_at':'2026-10-01T00:00:00.000Z','input_cutoff_at':'2026-10-01T00:00:00.000Z','case_as_of_boundary_at':'2026-09-30T22:00:00.000Z'}),given=[dict(input="ref('stg_boond_opportunities')",format='sql',fixture='visits_input')],expect=dict(rows=expected))]
    n='int_client_activity_context';rows=[];expected=[]
    cases=[('upsell',True,True,100,150,50,0,0),('contraction',True,True,100,70,0,0,30),('departure',True,False,100,0,0,100,0),('new',False,True,0,80,80,0,0),('stable',True,True,0,0,0,0,0),('stable',False,False,0,0,0,0,0),('unknown',None,True,None,80,None,None,None)]
    for idx,(kind,before,after,a,b,new,dep,con) in enumerate(cases):
        rows.append(dict(model_run_id='f'*64,tenant_id='fixture',company_id=idx,company_key=str(idx),client_context_key='context'+str(idx),month_date='2026-09-01',month_end_date='2026-09-30',previous_month_end_date='2026-08-31',is_active_before=before,is_active_after=after,mrr_before=a,mrr_after=b,candidate_mrr_before=a,candidate_mrr_after=b,is_comparable=kind!='unknown',first_acquisition_status='unknown',calculation_status='ready' if kind!='unknown' else 'partial'))
        expected.append(dict(company_id=idx,movement_kind=kind,sum_new_mrr=new,sum_departure_mrr=dep,sum_contraction_mrr=con))
    write('dbt/tests/fixtures/mrr_context_input.sql',fixture_sql(n,rows))
    test=dict(name='T30_T31_T33_T34_T52_net_company_mrr',model='int_mrr_movements',overrides=tests[0]['overrides'],given=[dict(input="ref('int_client_activity_context')",format='sql',fixture='mrr_context_input'),dict(input="ref('int_subscription_changes')",rows=[]),dict(input="ref('int_crm_identity_links')",rows=[])],expect=dict(rows=expected));tests.append(test)
    import json
    base=dict(src_tenant_id='fixture',src_language='fr',src_published_at='2026-01-01 00:00:00.000',capture_at='2026-01-02 00:00:00.000',source_identity_key='dict:fr',source_version_key='dict:1')
    codes=[0,1,2,3,7,9,10,13,14,19,20,21,22,23,24,25,26,27,28,30,31,32,33,34,35,999]
    stage_json=json.dumps([dict(id=x,value='stage'+str(x),isEnabled=False,active=False) for x in codes])
    origin_json=json.dumps([dict(id=x,value='origin'+str(x)) for x in range(1,13)])
    sale_json=json.dumps([dict(id=x,value='sale'+str(x)) for x in [2,4,7,99]])
    row=dict(base,src_setting_state_opportunity_json=stage_json,src_setting_origin_json=origin_json,src_setting_type_of_project_json=sale_json,src_setting_action_contact_json='[]')
    write('dbt/tests/fixtures/dictionaries_input.sql',fixture_sql('stg_boond_dictionaries',[row]))
    categories={'open':[0,20,21,22,23,24,25,26,28,30,31,32,33,34,35],'won':[1,14],'lost':[13,27],'abandoned':[3,9],'unqualified':[2,7]}
    expected=[dict(stage_id=x,outcome_category=next((k for k,v in categories.items() if x in v),'unknown')) for x in codes]
    tests.append(dict(name='T43_T57_old_states_never_infer_modern_stage',model='dim_stage',overrides=tests[0]['overrides'],given=[dict(input="ref('stg_boond_dictionaries')",format='sql',fixture='dictionaries_input')],expect=dict(rows=expected)))
    expected=[dict(channel_id=x,is_inbound=x in (1,2,3) if x<=11 else None,inbound_group='Inbound' if x<=3 else 'Outbound' if x<=5 else 'Other' if x<=11 else None) for x in range(1,13)]
    tests.append(dict(name='T56_inbound_outbound_other_no_marketing_fallback',model='dim_channel',overrides=tests[0]['overrides'],given=[dict(input="ref('stg_boond_dictionaries')",format='sql',fixture='dictionaries_input')],expect=dict(rows=expected)))
    tests.append(dict(name='T54_commercial_scope_training_preserved',model='dim_sale_type',overrides=tests[0]['overrides'],given=[dict(input="ref('stg_boond_dictionaries')",format='sql',fixture='dictionaries_input')],expect=dict(rows=[dict(sale_type_id=x,is_commercial_scope=x in (4,7)) for x in [2,4,7,99]])))
    rows=[dict(src_tenant_id='fixture',src_id=x,src_name=str(x),src_published_at='2026-01-01 00:00:00.000',capture_at='2026-01-02 00:00:00.000',source_identity_key=str(x),source_version_key=str(x)) for x in [12,13,15,99]]
    write('dbt/tests/fixtures/teams_input.sql',fixture_sql('stg_boond_businessunits',rows))
    tests.append(dict(name='T55_KAM_never_ES',model='dim_team',overrides=tests[0]['overrides'],given=[dict(input="ref('stg_boond_businessunits')",format='sql',fixture='teams_input'),dict(input="ref('stg_ref_sales_targets')",rows=[])],expect=dict(rows=[dict(team_id=x,sales_segment={12:'LA',13:'SMB'}.get(x),is_sales_team=True if x in [12,13] else False if x==15 else None) for x in [12,13,15,99]])))
    # Month-end activity: inclusive local end date, zero amount, reliable future birth,
    # contradictory creation chronology and the source 2099 sentinel all remain distinct.
    rows=[]
    for line,amount,reliable,created,first,start,end in [
        (1,100,True,'2026-01-01 00:00:00.000','2026-01-01 00:00:00.000','2026-01-01 00:00:00.000','2026-09-30 22:00:00.000'),
        (2,0,True,'2026-01-01 00:00:00.000','2026-01-01 00:00:00.000','2026-01-01 00:00:00.000',None),
        (3,80,True,'2026-10-02 00:00:00.000','2026-11-02 00:00:00.000','2026-10-02 00:00:00.000',None),
        (4,50,False,'2026-10-02 00:00:00.000','2026-08-01 00:00:00.000','2026-08-01 00:00:00.000',None),
        (5,25,True,'2026-01-01 00:00:00.000','2026-01-01 00:00:00.000','2026-01-01 00:00:00.000','2099-12-31 23:00:00.000')]:
        rows.append(dict(model_run_id='f'*64,tenant_id='fixture',line_id=line,subscription_key='line'+str(line),subscription_period_key='period'+str(line),line_created_at=created,is_creation_date_reliable=reliable,valid_from_at=first,valid_to_at=None,line_state_id=1,service_started_at=start,service_end_exclusive_at=end,line_monthly_amount=amount,is_history_complete=True,company_id=1,company_key='company',company_version_key='company1'))
    write('dbt/tests/fixtures/subscription_periods_input.sql',fixture_sql('int_subscription_periods',rows))
    dates=[dict(model_run_id='f'*64,calendar_date='2026-09-30',month_date='2026-09-01',month_end_date='2026-09-30',next_month_started_at='2026-09-30 22:00:00.000',is_month_end=True),dict(model_run_id='f'*64,calendar_date='2026-10-31',month_date='2026-10-01',month_end_date='2026-10-31',next_month_started_at='2026-10-31 23:00:00.000',is_month_end=True)]
    write('dbt/tests/fixtures/months_input.sql',fixture_sql('dim_date',dates))
    expected=[]
    for month in ['2026-09-01','2026-10-01']:
        for line in range(1,6):
            active=False if line==1 and month=='2026-10-01' else None if line==3 and month=='2026-10-01' else False if line==3 else True
            amount=None if active is None else 0 if not active else {1:100,2:0,4:50,5:25}[line]
            expected.append(dict(line_id=line,month_date=month,is_active=active,sum_active_mrr=amount))
    overrides=dict(macros={'is_incremental':False},vars=dict(tests[0]['overrides']['vars'],case_as_of_boundary_at='2026-10-31T23:00:00.000Z'))
    tests.append(dict(name='T13_T28_T30_T51_zero_inclusive_end_birth_and_2099',model='int_subscription_month_end',overrides=overrides,given=[dict(input="ref('int_subscription_periods')",format='sql',fixture='subscription_periods_input'),dict(input="ref('dim_date')",format='sql',fixture='months_input')],expect=dict(rows=expected)))
    visit_rows=[];period_rows=[];expected=[]
    for opp,stages in [(1,[0,1,14,22,1]),(2,[14,22,1]),(3,[0,13,22,1])]:
        first_terminal={1:2,2:1,3:2}[opp]
        for idx,stage in enumerate(stages):
            day=idx+1;at=f'2026-01-{day:02} 00:00:00.000';end=f'2026-01-{day+1:02} 00:00:00.000' if idx<len(stages)-1 else None
            entered=None if opp==2 and idx==0 else at
            visit_rows.append(dict(model_run_id='f'*64,tenant_id='fixture',opportunity_id=opp,opportunity_key='o'+str(opp),visit_key=f'v{opp}_{idx}',stage_id=stage,first_observed_at=at,last_observed_at=at,entered_at=entered,exited_at=end,previous_stage_id=stages[idx-1] if idx else None,next_stage_id=stages[idx+1] if idx<len(stages)-1 else None,event_time_basis='left_censored' if entered is None else 'cdc_transition_proxy'))
            period_rows.append(dict(model_run_id='f'*64,tenant_id='fixture',opportunity_id=opp,opportunity_key='o'+str(opp),period_key=f'p{opp}_{idx}',stage_id=stage,valid_from_at=at,valid_to_at=end,created_at='2026-01-01 00:00:00.000',sale_type_id=4,pipeline_amount=100,is_history_complete=True,attribution_status='resolved'))
            expected.append(dict(opportunity_id=opp,event_type='stage_entered',event_at=entered,nb_events=None if entered is None else 1,completed_cycle_duration_seconds=None))
            if end:expected.append(dict(opportunity_id=opp,event_type='stage_exited',event_at=end,nb_events=1,completed_cycle_duration_seconds=None))
            if stage in [1,13]:
                kind='signed' if stage==1 else 'lost';count=0 if stage==1 and (opp==2 or (opp==1 and idx==4)) else 1
                cycle=86400. if day==first_terminal and opp!=2 else None
                expected.append(dict(opportunity_id=opp,event_type=kind,event_at=entered,nb_events=count,completed_cycle_duration_seconds=cycle))
        expected.append(dict(opportunity_id=opp,event_type='pipeline_created',event_at='2026-01-01 00:00:00.000',nb_events=1,completed_cycle_duration_seconds=None))
    write('dbt/tests/fixtures/events_visits_input.sql',fixture_sql('int_opportunity_stage_visits',visit_rows));write('dbt/tests/fixtures/events_periods_input.sql',fixture_sql('int_opportunity_periods',period_rows))
    tests.append(dict(name='T20_T58_T59_first_signature_and_terminal_not_absorbing',model='int_opportunity_events',overrides=tests[0]['overrides'],given=[dict(input="ref('int_opportunity_stage_visits')",format='sql',fixture='events_visits_input'),dict(input="ref('int_opportunity_periods')",format='sql',fixture='events_periods_input'),dict(input="ref('int_crm_identity_links')",rows=[]),dict(input="ref('dim_date')",rows=[])],expect=dict(rows=expected)))
    periods=[];visits=[]
    sequences={1:[0,24,22],2:[0,24,22,24],3:[0,22,24,22,24]}
    for opp,stages in sequences.items():
        for idx,stage in enumerate(stages):
            at=f'2026-01-{idx+1:02} 00:00:00.000';end=f'2026-01-{idx+2:02} 00:00:00.000' if idx<len(stages)-1 else None
            periods.append(dict(model_run_id='f'*64,tenant_id='fixture',opportunity_id=opp,opportunity_key='o'+str(opp),period_key=f'p{opp}_{idx}',valid_from_at=at,valid_to_at=end,created_at='2026-01-01 00:00:00.000',sale_type_id=4,stage_id=stage,outcome_category='open',is_history_complete=True))
            visits.append(dict(model_run_id='f'*64,tenant_id='fixture',opportunity_id=opp,opportunity_key='o'+str(opp),visit_key=f'v{opp}_{idx}',first_observed_at=at,last_observed_at=at,stage_id=stage,entered_at=at,exited_at=end))
    definition=dict(model_run_id='f'*64,tenant_id='fixture',followup_definition_id='transition_type4_22_24_v1',followup_definition_key='d1',followup_definition_version_key='dv1',followup_kind='stage_transition',sale_type_id=4,source_stage_id=22,target_stage_id=24,previous_target_stage_id=22,horizon_days=None,is_enabled=True)
    write('dbt/tests/fixtures/transitions_periods.sql',fixture_sql('int_opportunity_periods',periods));write('dbt/tests/fixtures/transitions_visits.sql',fixture_sql('int_opportunity_stage_visits',visits));write('dbt/tests/fixtures/transitions_definitions.sql',fixture_sql('dim_followup_definition',[definition]))
    expected=[dict(opportunity_id=1,anchor_at='2026-01-03 00:00:00.000',first_reached_at=None,reached_target=False,converted_contribution=0),dict(opportunity_id=2,anchor_at='2026-01-03 00:00:00.000',first_reached_at='2026-01-04 00:00:00.000',reached_target=True,converted_contribution=1),dict(opportunity_id=3,anchor_at='2026-01-02 00:00:00.000',first_reached_at='2026-01-03 00:00:00.000',reached_target=True,converted_contribution=1)]
    tests.append(dict(name='T60_B_before_A_and_returns_do_not_duplicate_transitions',model='int_opportunity_followup',overrides=tests[0]['overrides'],given=[dict(input="ref('int_opportunity_periods')",format='sql',fixture='transitions_periods'),dict(input="ref('int_opportunity_stage_visits')",format='sql',fixture='transitions_visits'),dict(input="ref('dim_followup_definition')",format='sql',fixture='transitions_definitions'),dict(input="ref('int_opportunity_events')",rows=[])],expect=dict(rows=expected)))
    periods=[];visits=[]
    scenarios=[(1,'2026-08-01 10:00:00.000',[('2026-08-01 10:00:00.000',0,'open'),('2026-08-05 10:00:00.000',1,'won'),('2026-08-20 10:00:00.000',22,'open')]),(2,'2026-08-31 10:00:00.000',[('2026-08-31 10:00:00.000',14,'won')]),(3,'2026-03-01 11:00:00.000',[('2026-03-01 11:00:00.000',0,'open')]),(4,'2026-07-01 10:00:00.000',[('2026-08-15 10:00:00.000',14,'won')])]
    for opp,created,steps in scenarios:
        for idx,(at,stage,category) in enumerate(steps):
            end=steps[idx+1][0] if idx+1<len(steps) else None
            periods.append(dict(model_run_id='f'*64,tenant_id='fixture',opportunity_id=opp,opportunity_key='o'+str(opp),period_key=f'p{opp}_{idx}',valid_from_at=at,valid_to_at=end,created_at=created,sale_type_id=4,stage_id=stage,outcome_category=category,is_history_complete=True))
            visits.append(dict(model_run_id='f'*64,tenant_id='fixture',opportunity_id=opp,opportunity_key='o'+str(opp),visit_key=f'v{opp}_{idx}',first_observed_at=at,last_observed_at=at,stage_id=stage,entered_at=None if stage==14 and idx==0 else at,exited_at=end))
    defs=[dict(model_run_id='f'*64,tenant_id='fixture',followup_definition_id='cohort_j'+str(h),followup_definition_key='d'+str(h),followup_definition_version_key='dv'+str(h),followup_kind='cohort_outcome',sale_type_id=4,horizon_days=h,is_enabled=True) for h in [30,60]]
    for name,model,rows in [('cohort_periods','int_opportunity_periods',periods),('cohort_visits','int_opportunity_stage_visits',visits),('cohort_definitions','dim_followup_definition',defs)]:write('dbt/tests/fixtures/'+name+'.sql',fixture_sql(model,rows))
    expected=[dict(opportunity_id=1,horizon_days=30,issue_at_horizon='open',is_cohort_mature=True,denominator_contribution=1,horizon_at='2026-08-31 10:00:00.000'),dict(opportunity_id=1,horizon_days=60,issue_at_horizon=None,is_cohort_mature=False,denominator_contribution=None,horizon_at='2026-09-30 10:00:00.000'),dict(opportunity_id=2,horizon_days=30,issue_at_horizon='won',is_cohort_mature=True,denominator_contribution=1,horizon_at='2026-09-30 10:00:00.000'),dict(opportunity_id=2,horizon_days=60,issue_at_horizon=None,is_cohort_mature=False,denominator_contribution=None,horizon_at='2026-10-30 11:00:00.000'),dict(opportunity_id=3,horizon_days=30,issue_at_horizon='open',is_cohort_mature=True,denominator_contribution=1,horizon_at='2026-03-31 10:00:00.000'),dict(opportunity_id=3,horizon_days=60,issue_at_horizon='open',is_cohort_mature=True,denominator_contribution=1,horizon_at='2026-04-30 10:00:00.000'),dict(opportunity_id=4,horizon_days=30,issue_at_horizon='unknown',is_cohort_mature=True,denominator_contribution=1,horizon_at='2026-07-31 10:00:00.000'),dict(opportunity_id=4,horizon_days=60,issue_at_horizon='won',is_cohort_mature=True,denominator_contribution=1,horizon_at='2026-08-30 10:00:00.000')]
    tests.append(dict(name='T41_T42_T44_T58_cohort_horizon_reopened_DST_and_censoring',model='int_opportunity_followup',overrides=tests[0]['overrides'],given=[dict(input="ref('int_opportunity_periods')",format='sql',fixture='cohort_periods'),dict(input="ref('int_opportunity_stage_visits')",format='sql',fixture='cohort_visits'),dict(input="ref('dim_followup_definition')",format='sql',fixture='cohort_definitions'),dict(input="ref('int_opportunity_events')",rows=[])],expect=dict(rows=expected)))
    visit=dict(model_run_id='f'*64,tenant_id='fixture',opportunity_key='o1',opportunity_id=1,visit_key='v1',stage_id=22,first_observed_at='2026-01-01 00:00:00.000',last_observed_at='2026-01-02 00:00:00.000',entered_at='2026-01-01 00:00:00.000',exited_at='2026-01-03 00:00:00.000',completed_duration_seconds=172800.,completed_duration_days=2.)
    periods=[dict(model_run_id='f'*64,tenant_id='fixture',opportunity_key='o1',opportunity_id=1,period_key='p1',visit_key='v1',valid_from_at='2026-01-01 00:00:00.000',valid_to_at='2026-01-02 00:00:00.000',team_key='LA',team_version_key='LA_v1',employee_key='employeeA',employee_version_key='A_v1'),dict(model_run_id='f'*64,tenant_id='fixture',opportunity_key='o1',opportunity_id=1,period_key='p2',visit_key='v1',valid_from_at='2026-01-02 00:00:00.000',valid_to_at=None,team_key='SMB',team_version_key='SMB_v1',employee_key='employeeB',employee_version_key='B_v1')]
    write('dbt/tests/fixtures/transfer_visit.sql',fixture_sql('int_opportunity_stage_visits',[visit]));write('dbt/tests/fixtures/transfer_periods.sql',fixture_sql('int_opportunity_periods',periods))
    given=[dict(input="ref('int_opportunity_stage_visits')",format='sql',fixture='transfer_visit'),dict(input="ref('int_opportunity_periods')",format='sql',fixture='transfer_periods')]+[dict(input="ref('"+n+"')",rows=[]) for n in MODELS['fct_stage_visit']['refs'] if n not in ['int_opportunity_stage_visits','int_opportunity_periods']]
    tests.append(dict(name='T61_transfer_preserves_visit_and_entry_team',model='fct_stage_visit',overrides=tests[0]['overrides'],given=given,expect=dict(rows=[dict(visit_key='v1',entry_team_key='LA',entry_employee_key='employeeA',completed_duration_seconds=172800.,is_team_filter_available=True)])))
    write('dbt/tests/fixtures/calendar_month_edge.sql',fixture_sql('int_subscription_month_end',[dict(model_run_id='f'*64,tenant_id='fixture',line_id=1,subscription_key='s1',subscription_month_key='sm1',month_date='2026-08-01',month_end_date='2026-08-31',closing_exclusive_at='2026-08-31 22:00:00.000',closing_date_key=20260831)]))
    write('dbt/tests/fixtures/calendar_day_edge.sql',fixture_sql('dim_date',[dict(model_run_id='f'*64,calendar_date='2026-08-31',date_key=20260831)]))
    tests.append(dict(name='T10_outside_calendar_nullable_role_key',model='fct_subscription_month_end',overrides=tests[0]['overrides'],given=[dict(input="ref('int_subscription_month_end')",format='sql',fixture='calendar_month_edge'),dict(input="ref('dim_date')",format='sql',fixture='calendar_day_edge')],expect=dict(rows=[dict(month_date='2026-08-01',month_date_key=None)])))
    units=[dict(src_tenant_id='fixture',src_id=x,src_published_at='2026-01-01 00:00:00.000',capture_at='2026-01-02 00:00:00.000',source_identity_key='bu'+str(x),source_version_key='bu'+str(x),src_included_managers_json='[{"id":1,"type":"resource"}]') for x in [12,13]]
    employees=[dict(model_run_id='f'*64,tenant_id='fixture',employee_id=1,employee_key='e1',employee_version_key='ev1',valid_from_at='2026-01-01 00:00:00.000',valid_to_at=None)]
    teams=[dict(model_run_id='f'*64,tenant_id='fixture',team_id=x,team_key='t'+str(x),team_version_key='tv'+str(x),sales_segment={12:'LA',13:'SMB'}[x],valid_from_at='2026-01-01 00:00:00.000',valid_to_at=None) for x in [12,13]]
    for name,model,rows in [('multi_bu','stg_boond_businessunits',units),('multi_employees','dim_employee',employees),('multi_teams','dim_team',teams)]:write('dbt/tests/fixtures/'+name+'.sql',fixture_sql(model,rows))
    tests.append(dict(name='T16_multiple_memberships_remain_unattributed',model='int_team_membership_periods',overrides=tests[0]['overrides'],given=[dict(input="ref('stg_boond_businessunits')",format='sql',fixture='multi_bu'),dict(input="ref('dim_employee')",format='sql',fixture='multi_employees'),dict(input="ref('dim_team')",format='sql',fixture='multi_teams')],expect=dict(rows=[dict(employee_id=1,team_id=x,nb_simultaneous_memberships=2,membership_status='multiple',is_sales_attribution_eligible=False) for x in [12,13]])))
    # Ref dependencies declared only for lineage are not referenced at execution; supply empty fixtures.
    write('dbt/models/_unit_tests.yml',yaml.safe_dump(dict(version=2,unit_tests=tests),allow_unicode=True,sort_keys=False))

def publication_tests():
    from quality import REGISTRY,BLOCKED
    ids=[x for values in REGISTRY.values() for x in values]
    # Validate the candidate JSON before touching the pointer; no dependency on a previous publication.
    sql="with entries as (select arrayJoin(JSONExtractArrayRaw({{ ch_literal(var('publication_quality_json','[]')) }})) as item), parsed as (select JSONExtractString(item,'measure_id') as id, JSONExtractString(item,'availability_status') as status,JSONExtract(item,'availability_reason','Nullable(String)') as reason,JSONExtract(item,'nb_expected','Nullable(UInt64)') as expected,JSONExtract(item,'nb_known','Nullable(UInt64)') as known from entries) select 'invalid_quality_registry' as failure from parsed having count()!=30 or uniqExact(id)!=30 or countIf(id not in ("+','.join(q(x) for x in ids)+"))>0 or countIf(status not in ('available','partial','blocked_definition','blocked_evidence','non_mature','not_observable','not_applicable'))>0 or countIf(status!='available' and reason is null)>0 or countIf(known>expected)>0 or countIf(id in ("+','.join(q(x) for x in BLOCKED)+") and status='available')>0"
    test_file('assert_publication_quality_candidate',sql,['publication_guard'])
    branches=[]
    for n,m in MODELS.items():
        if not n.startswith('dataset_'):continue
        branches.append('select '+q(n)+' as dataset from '+ref(n)+' where model_run_id!='+j("ch_literal(var('publication_model_run_id',''))")+' having count()>0')
    branches.append("select 'pointer_count' as dataset from "+ref('int_publication')+' having count()!=1')
    branches.append("select 'measure_count' as dataset from "+ref('dataset_publication_status')+' having count()!=30')
    test_file('assert_published_datasets_one_run',' union all '.join(branches),['published_guard'])
    branches=[]
    for n,m in MODELS.items():
        if not n.startswith('dataset_'):continue
        branches.append('select '+q(n)+" as dataset from system.columns where database='dtr_sales' and table="+q(n)+' having count()!='+str(len(m['columns'])))
    test_file('assert_dataset_contracts',' union all '.join(branches),['dataset_contract'])

if __name__=='__main__':data_tests();unit_tests();publication_tests()
