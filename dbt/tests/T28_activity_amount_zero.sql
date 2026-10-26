{{ config(tags=['pipeline', 'revenue', 'dtr']) }}
select record_key from {{ ref('int_subscription_month_end') }} where model_run_id={{ ch_literal(var('test_model_run_id','')) }} and (is_active and candidate_active_mrr!=line_monthly_amount)
