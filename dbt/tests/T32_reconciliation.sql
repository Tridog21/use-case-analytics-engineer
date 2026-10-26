{{ config(tags=['pipeline', 'revenue', 'dtr']) }}
select record_key from {{ ref('dtr_company_mrr_month') }} where model_run_id={{ ch_literal(var('test_model_run_id','')) }} and (sum_reconciliation_gap is not null and sum_reconciliation_gap!=0)
