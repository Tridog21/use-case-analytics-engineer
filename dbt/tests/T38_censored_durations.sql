{{ config(tags=['pipeline', 'revenue', 'dtr']) }}
select record_key from {{ ref('fct_stage_visit') }} where model_run_id={{ ch_literal(var('test_model_run_id','')) }} and (completed_duration_seconds is not null and (entered_at is null or exited_at is null))
