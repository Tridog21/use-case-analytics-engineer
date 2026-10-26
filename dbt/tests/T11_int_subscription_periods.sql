{{ config(tags=['revenue']) }}
select record_key from {{ ref('int_subscription_periods') }} where model_run_id={{ ch_literal(var('test_model_run_id','')) }} and valid_to_at is not null and valid_from_at>=valid_to_at
