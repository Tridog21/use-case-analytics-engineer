{{ config(tags=['pipeline', 'revenue', 'dtr']) }}
select record_key from {{ ref('int_subscription_periods') }} where model_run_id={{ ch_literal(var('test_model_run_id','')) }} and (currency_code!='EUR')
