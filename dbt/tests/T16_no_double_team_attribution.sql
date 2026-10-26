{{ config(tags=['pipeline','common']) }}
select record_key from {{ ref('int_opportunity_periods') }}
where model_run_id={{ ch_literal(var('test_model_run_id','')) }}
and ((is_team_calculable and team_key is null) or (not is_team_calculable and team_key is not null))
