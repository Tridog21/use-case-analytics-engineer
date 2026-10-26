{{ config(tags=['pipeline', 'revenue', 'dtr']) }}
select record_key from {{ ref('int_opportunity_stage_visits') }} where model_run_id={{ ch_literal(var('test_model_run_id','')) }} and (is_left_censored and (entered_at is not null or completed_duration_seconds is not null))
