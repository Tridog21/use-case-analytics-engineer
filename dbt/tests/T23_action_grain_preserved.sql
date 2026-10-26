{{ config(tags=['pipeline','dtr']) }}
select action_key from {{ ref('dtr_sales_actions') }}
where model_run_id={{ ch_literal(var('test_model_run_id','')) }}
group by action_key having count()>1
