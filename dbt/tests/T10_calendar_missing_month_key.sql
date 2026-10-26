{{ config(tags=['revenue','mart']) }}
select f.record_key
from {{ ref('fct_subscription_month_end') }} f
left join {{ ref('dim_date') }} d on f.model_run_id=d.model_run_id and f.month_date=d.calendar_date
where f.model_run_id={{ ch_literal(var('test_model_run_id','')) }}
and d.date_key is null and f.month_date_key is not null
