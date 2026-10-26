{{ config(tags=['revenue','dtr']) }}
with lines as (
 select tenant_id,company_key,month_end_date,
 if(countIf(sum_active_mrr is null)=0,sum(sum_active_mrr),NULL) as mrr
 from {{ ref('fct_subscription_month_end') }}
 where model_run_id={{ ch_literal(var('test_model_run_id','')) }} and company_key is not null
 group by tenant_id,company_key,month_end_date
)
select d.record_key from {{ ref('dtr_company_mrr_month') }} d
inner join lines l on d.tenant_id=l.tenant_id and d.company_key=l.company_key and d.closing_date=l.month_end_date
where d.model_run_id={{ ch_literal(var('test_model_run_id','')) }} and not isNotDistinctFrom(d.sum_mrr_end,l.mrr)
