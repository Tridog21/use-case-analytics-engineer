{{ config(tags=['pipeline', 'revenue', 'dtr']) }}
select record_key from {{ ref('int_mrr_movements') }} where model_run_id={{ ch_literal(var('test_model_run_id','')) }} and (movement_kind='unknown' and (sum_new_mrr is not null or sum_departure_mrr is not null or sum_contraction_mrr is not null))
