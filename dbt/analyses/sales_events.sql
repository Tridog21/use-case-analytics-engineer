select model_run_id,event_type,sale_type_id,countIf(nb_events=1) as nb_events,
 if(countIf(is_generated_amount_calculable)=count(),sum(sum_generated_pipeline_amount),NULL) as generated_amount,
 if(countIf(is_signed_mrr_calculable)=count(),sum(sum_signed_mrr),NULL) as signed_mrr,
 if(countIf(completed_cycle_duration_days is not null)>0,quantileExactInclusiveIf(0.5)(completed_cycle_duration_days,completed_cycle_duration_days is not null),NULL) as median_observed_cycle,
 if(countIf(completed_cycle_duration_days is not null)>0,quantileExactInclusiveIf(0.9)(completed_cycle_duration_days,completed_cycle_duration_days is not null),NULL) as p90_observed_cycle
from {{ ref('dataset_sales_events') }}
where event_at>={{ utc_var('period_start_at','2026-09-01T00:00:00.000Z') }}
and event_at<{{ utc_var('period_end_at','2026-09-30T22:00:00.000Z') }}
group by model_run_id,event_type,sale_type_id
