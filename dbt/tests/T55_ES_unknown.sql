{{ config(tags=['pipeline', 'revenue', 'dtr']) }}
select record_key from {{ ref('int_sales_objectives_month') }} where model_run_id={{ ch_literal(var('test_model_run_id','')) }} and (source_segment='ES' and (team_key is not null or actual_value is not null or candidate_actual_value is not null))
