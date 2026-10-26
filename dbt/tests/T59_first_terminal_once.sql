{{ config(tags=['pipeline']) }}
select opportunity_key from {{ ref('int_opportunity_events') }} where model_run_id={{ ch_literal(var('test_model_run_id','')) }} and completed_cycle_duration_seconds is not null group by opportunity_key having count()>1
