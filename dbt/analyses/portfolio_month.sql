-- A single closing stock; team filters do not apply to portfolio measures.
-- Whole-population evidence is required: unresolved-company lines cannot disappear in a global sum.
with coverage as (
 select model_run_id,
 countIf(measure_id='revenue.active_mrr' and availability_status='available')=1 as active_mrr_available,
 countIf(measure_id='revenue.new_mrr' and availability_status='available')=1 as new_mrr_available,
 countIf(measure_id='revenue.churn_mrr' and availability_status='available')=1 as churn_mrr_available,
 countIf(measure_id='revenue.active_clients' and availability_status='available')=1 as active_clients_available,
 max(coverage_status) as revenue_coverage_status
 from {{ ref('dataset_publication_status') }} where dataset_family='company_mrr_month'
 group by model_run_id
)
select d.model_run_id,d.closing_date,
 if(any(q.active_mrr_available) and countIf(sum_mrr_end is null)=0,sum(sum_mrr_end),NULL) as sum_active_mrr,
 if(any(q.new_mrr_available) and countIf(sum_new_mrr is null)=0,sum(sum_new_mrr),NULL) as sum_new_mrr,
 if(any(q.churn_mrr_available) and countIf(sum_churn_mrr is null)=0,sum(sum_churn_mrr),NULL) as sum_churn_mrr,
 if(any(q.active_clients_available) and countIf(is_active_end is null)=0,countIf(is_active_end),NULL) as nb_active_clients,
 if(any(q.active_clients_available) and countIf(is_active_begin is null)=0,countIf(is_departure)/nullIf(countIf(is_active_begin),0),NULL) as client_churn_rate,
 any(q.revenue_coverage_status) as revenue_coverage_status
from {{ ref('dataset_company_mrr_month') }} d inner join coverage q on d.model_run_id=q.model_run_id
group by d.model_run_id,d.closing_date
