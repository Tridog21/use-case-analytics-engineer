{{ config(tags=['pipeline', 'revenue', 'dtr']) }}
select record_key from {{ ref('dim_stage') }} where model_run_id={{ ch_literal(var('test_model_run_id','')) }} and (stage_id in (10,19) and outcome_category!='unknown')
