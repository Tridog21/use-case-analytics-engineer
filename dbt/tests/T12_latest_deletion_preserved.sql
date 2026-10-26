{{ config(tags=['pipeline','dtr']) }}
with latest as (
 select src_tenant_id,src_id,argMax(tuple(src_is_deleted),src_published_at).1 as was_deleted
 from {{ ref('stg_boond_actions') }}
 where capture_at<={{ utc_var('input_cutoff_at') }}
 group by src_tenant_id,src_id
)
select d.record_key from {{ ref('dtr_sales_actions') }} d
inner join latest s on d.tenant_id=s.src_tenant_id and d.action_id=s.src_id
where d.model_run_id={{ ch_literal(var('test_model_run_id','')) }}
and d.is_source_deleted!=s.was_deleted
