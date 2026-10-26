-- One metric and month per group; incomplete segments remain unknown.
select model_run_id,month_date,metric_code,sum(target_value) as sum_target,
 if(countIf(actual_value is null)=0,sum(actual_value),NULL) as sum_actual,
 sum_actual/nullIf(sum_target,0) as attainment_rate
from {{ ref('dataset_sales_objectives_month') }}
group by model_run_id,month_date,metric_code
