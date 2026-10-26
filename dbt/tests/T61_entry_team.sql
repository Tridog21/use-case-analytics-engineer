{{ config(tags=['pipeline', 'revenue', 'dtr']) }}
select record_key from {{ ref('fct_stage_visit') }} where model_run_id={{ ch_literal(var('test_model_run_id','')) }} and (entered_at is null and (entry_team_key is not null or entry_employee_key is not null))
