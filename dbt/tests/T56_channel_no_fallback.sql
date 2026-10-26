{{ config(tags=['pipeline', 'revenue', 'dtr']) }}
select record_key from {{ ref('int_opportunity_periods') }} where model_run_id={{ ch_literal(var('test_model_run_id','')) }} and (channel_candidate_code is null and acquisition_channel_key is not null)
