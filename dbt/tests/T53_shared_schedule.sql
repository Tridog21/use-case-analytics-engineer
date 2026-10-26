{{ config(tags=['pipeline', 'revenue', 'dtr']) }}
select record_key from {{ ref('int_signature_probabilities') }} where model_run_id={{ ch_literal(var('test_model_run_id','')) }} and (applicability_status='applicable_recomputed_case' and (business_valid_from_at!={{ utc_var('case_history_start_at') }} or business_valid_to_at!={{ utc_var('case_as_of_boundary_at') }}))
