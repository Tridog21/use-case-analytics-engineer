with eligible as (
 select model_run_id,opportunity_key,company_key,team_key,is_open,is_demo_stage,sale_type_id,pipeline_amount,weighted_pipeline_amount,is_amount_calculable
 from {{ ref('dataset_pipeline_periods') }}
 where valid_from_at<{{ utc_var('observation_at','2026-09-30T22:00:00.000Z') }}
 and (valid_to_at is null or valid_to_at>={{ utc_var('observation_at','2026-09-30T22:00:00.000Z') }})
 and ({{ ch_literal(var('team_key',none)) }} is null or team_key={{ ch_literal(var('team_key',none)) }})
)
select model_run_id,countIf(is_open and sale_type_id in (4,7)) as nb_open_opportunities,
 uniqExactIf(company_key,is_open and is_demo_stage and company_key is not null and sale_type_id in (4,7)) as nb_in_demo_companies,
 if(countIf(not is_amount_calculable)=0,sumIf(pipeline_amount,is_open),NULL) as sum_open_amount
from eligible group by model_run_id
