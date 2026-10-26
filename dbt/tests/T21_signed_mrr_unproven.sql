{{ config(tags=['pipeline', 'revenue', 'dtr']) }}
select record_key from {{ ref('fct_opportunity_event') }} where model_run_id={{ ch_literal(var('test_model_run_id','')) }} and (sum_signed_mrr is not null)
