{{ config(tags=['pipeline', 'revenue', 'dtr']) }}
select record_key from {{ ref('int_subscription_month_end') }} where model_run_id={{ ch_literal(var('test_model_run_id','')) }} and (closing_exclusive_at>{{ utc_var('case_as_of_boundary_at') }})
