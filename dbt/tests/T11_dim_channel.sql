{{ config(tags=['common']) }}
select record_key from {{ ref('dim_channel') }} where model_run_id={{ ch_literal(var('test_model_run_id','')) }} and valid_to_at is not null and valid_from_at>=valid_to_at
