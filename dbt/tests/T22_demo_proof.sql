{{ config(tags=['pipeline', 'revenue', 'dtr']) }}
select record_key from {{ ref('fct_action') }} where model_run_id={{ ch_literal(var('test_model_run_id','')) }} and (is_realized_demo is not null or actual_event_at is not null)
