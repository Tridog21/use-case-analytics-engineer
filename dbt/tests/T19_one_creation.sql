{{ config(tags=['pipeline']) }}
select opportunity_key from {{ ref('int_opportunity_events') }} where model_run_id={{ ch_literal(var('test_model_run_id','')) }} and event_type='pipeline_created' group by opportunity_key having count()!=1
