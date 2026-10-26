{{ config(tags=['pipeline', 'revenue', 'dtr']) }}
select record_key from {{ ref('fct_sales_objectives_month') }} where model_run_id={{ ch_literal(var('test_model_run_id','')) }} and (actual_value is not null or attainment_rate is not null)
