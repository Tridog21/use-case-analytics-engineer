{{ config(tags=['pipeline', 'revenue', 'dtr']) }}
select record_key from {{ ref('int_signature_probabilities') }} where model_run_id={{ ch_literal(var('test_model_run_id','')) }} and (probability<0 or probability>1)
