{{ config(tags=['pipeline', 'revenue', 'dtr']) }}
select record_key from {{ ref('int_subscription_periods') }} where model_run_id={{ ch_literal(var('test_model_run_id','')) }} and (abs(line_monthly_amount-recomputed_quantity_price_amount)>toDecimal128('0.005',4))
