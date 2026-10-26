{{ config(tags=['common']) }}
select record_key from {{ ref('int_crm_identity_links') }}
where model_run_id={{ ch_literal(var('test_model_run_id','')) }}
and source_system='hubspot' and target_id is not null and toInt64OrNull(target_id) is null
