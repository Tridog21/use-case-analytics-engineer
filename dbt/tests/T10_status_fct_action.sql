{{ config(tags=['mart']) }}
select record_key from {{ ref('fct_action') }} where model_run_id={{ ch_literal(var('test_model_run_id','')) }} and calculation_status not in ('ready','partial','blocked','not_applicable')
