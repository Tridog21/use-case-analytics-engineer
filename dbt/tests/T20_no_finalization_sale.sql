{{ config(tags=['pipeline', 'revenue', 'dtr']) }}
select record_key from {{ ref('int_opportunity_events') }} where model_run_id={{ ch_literal(var('test_model_run_id','')) }} and (event_type='signed' and to_stage_id!=1)
