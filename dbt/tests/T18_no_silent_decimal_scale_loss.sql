{{ config(tags=['pipeline','revenue']) }}
select record_key from {{ ref('int_opportunity_periods') }}
where model_run_id={{ ch_literal(var('test_model_run_id','')) }} and status_reason='insufficient_decimal_scale'
union all
select record_key from {{ ref('int_subscription_periods') }}
where model_run_id={{ ch_literal(var('test_model_run_id','')) }}
and quantity is not null and unit_monthly_price is not null and recomputed_quantity_price_amount is null
