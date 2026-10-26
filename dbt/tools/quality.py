"""Closed per-measure availability registry, derived from candidate evidence."""
from catalogue import MODELS
from runtime import *

REGISTRY={
 'sales_objectives_month':['objectives.mrr_signed','objectives.pipeline_generated','objectives.pipeline_weighted','objectives.demos'],
 'funnel_progress':['funnel.opportunities','funnel.transition','funnel.global'],
 'company_mrr_month':['revenue.active_mrr','revenue.new_mrr','revenue.churn_mrr','revenue.active_clients'],
 'stage_visits':['durations.completed','durations.current_age','durations.threshold'],
 'cohort_outcomes':['cohorts.outcomes'],
 'pipeline_periods':['pipeline.open_count','pipeline.open_amount','pipeline.weighted_amount','pipeline.coverage','pipeline.stagnation','pipeline.in_demo'],
 'sales_events':['events.generated_count','events.generated_amount','events.signed_count','events.signed_mrr','events.cycle'],
 'sales_actions':['actions.requests','actions.realized_demos'],
 'demo_intervals':['demo_intervals.duration'],'opportunity_timeline':['timeline.detail']}
BLOCKED={
 'objectives.mrr_signed':'unconfirmed_amount_unit','objectives.pipeline_generated':'unconfirmed_amount_unit','objectives.pipeline_weighted':'unconfirmed_amount_unit','objectives.demos':'missing_demo_completion_proof',
 'events.signed_mrr':'unconfirmed_amount_unit','events.generated_amount':'unconfirmed_amount_unit','pipeline.open_amount':'unconfirmed_amount_unit','pipeline.weighted_amount':'unconfirmed_amount_unit',
 'actions.realized_demos':'missing_demo_completion_proof','demo_intervals.duration':'unproven_demo_intervals','pipeline.coverage':'feature_not_activated'}
KNOWN={
 'revenue.active_mrr':'sum_mrr_end is not null','revenue.new_mrr':'sum_new_mrr is not null','revenue.churn_mrr':'sum_churn_mrr is not null','revenue.active_clients':'is_active_end is not null',
 'durations.completed':'entered_at is not null and exited_at is not null and is_history_complete','durations.current_age':'entered_at is not null and observation_end_at is null','durations.threshold':'entered_at is not null',
 'cohorts.outcomes':'is_cohort_mature and is_observable',
 'pipeline.open_count':'is_open is not null','pipeline.stagnation':'stage_entered_at is not null','pipeline.in_demo':'is_demo_stage is not null',
 'events.generated_count':"event_type='pipeline_created' and nb_events is not null",'events.signed_count':"event_type='signed' and nb_events is not null",'events.cycle':'completed_cycle_duration_seconds is not null',
 'actions.requests':'nb_demo_request_contribution is not null','timeline.detail':'true',
 'funnel.opportunities':'first_reached_observed_at is not null','funnel.transition':'previous_stage_first_reached_at is not null','funnel.global':'is_history_complete'}

def summarize(vars,c=None):
    c=c or client();run=vars['model_run_id'];result=[]
    orphan_months=c.query('select count() from dwh_revenue.int_subscription_month_end where model_run_id={run:String} and company_key is null and (is_active is null or is_active)',parameters={'run':run}).first_row[0]
    for family,measures in REGISTRY.items():
        relation='dtr_sales.dtr_'+family
        for measure in measures:
            expected=c.query('select count() from '+relation+' where model_run_id={run:String}',parameters={'run':run}).first_row[0]
            if measure in BLOCKED:
                status='blocked_definition' if measure=='pipeline.coverage' else 'blocked_evidence';reason=BLOCKED[measure];known=None
            else:
                known=c.query('select countIf('+KNOWN[measure]+') from '+relation+' where model_run_id={run:String}',parameters={'run':run}).first_row[0]
                status='available' if known==expected else 'partial';reason=None if status=='available' else 'incomplete_history'
            row=dict(measure_id=measure,dataset_family=family,availability_status=status,availability_reason=reason,coverage_status='complete' if status=='available' else 'partial' if status=='partial' else 'not_applicable',nb_expected=expected,nb_known=known,data_coverage_end_at=vars['case_as_of_boundary_at'])
            if family=='company_mrr_month' and orphan_months:
                row.update(availability_status='partial',availability_reason='incomplete_history',coverage_status='partial',nb_expected=None,nb_known=None,nb_evaluated_company_months=expected,nb_unassigned_line_months=orphan_months,availability_obstacles=['unresolved_company_history','incomplete_history'])
            result.append(row)
    validate_quality(result)
    return result

def validate_quality(value):
    expected={x for xs in REGISTRY.values() for x in xs}
    if not isinstance(value,list) or {x['measure_id'] for x in value}!=expected or len(value)!=len(expected):raise ValueError('Availability registry must contain exactly 30 unique measure IDs')
    for row in value:
        if row['dataset_family'] not in REGISTRY or row['measure_id'] not in REGISTRY[row['dataset_family']]:raise ValueError('Invalid measure family')
        if row['availability_status'] not in ['available','partial','blocked_definition','blocked_evidence','non_mature','not_observable','not_applicable']:raise ValueError('Invalid availability status')
        if row['availability_status']!='available' and not row['availability_reason']:raise ValueError('Unavailable measure requires an explicit reason')
        if row['measure_id'] in BLOCKED and row['availability_status'] not in ['blocked_definition','blocked_evidence']:raise ValueError('Missing proof cannot be promoted')
        for name in ['nb_expected','nb_known']:
            if row[name] is not None and (type(row[name])!=int or row[name]<0):raise ValueError('Count must be integer or null')
        if row['nb_known'] is not None and row['nb_expected'] is not None and row['nb_known']>row['nb_expected']:raise ValueError('Known count exceeds expected')
    return value
