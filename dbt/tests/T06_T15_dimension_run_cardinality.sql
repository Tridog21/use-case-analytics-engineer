{{ config(tags=['pipeline','common']) }}
with matches as (
 select f.model_run_id,f.record_key,countIf(c.company_version_key is not null) as nb_matches
 from {{ ref('int_opportunity_periods') }} f
 left join {{ ref('dim_company') }} c on f.model_run_id=c.model_run_id and f.company_version_key=c.company_version_key
 where f.model_run_id={{ ch_literal(var('test_model_run_id','')) }}
 group by f.model_run_id,f.record_key
)
select record_key from matches where nb_matches>1
