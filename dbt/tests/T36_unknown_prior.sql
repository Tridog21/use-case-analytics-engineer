{{ config(tags=['pipeline', 'revenue', 'dtr']) }}
select record_key from {{ ref('int_client_activity_context') }} where model_run_id={{ ch_literal(var('test_model_run_id','')) }} and (not is_comparable and mrr_before is null and calculation_status='ready')
