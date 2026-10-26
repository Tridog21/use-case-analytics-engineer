{{ config(tags=['pipeline', 'revenue', 'dtr']) }}
select record_key from {{ ref('int_opportunity_followup') }} where model_run_id={{ ch_literal(var('test_model_run_id','')) }} and (followup_kind='cohort_outcome' and not is_cohort_mature and (denominator_contribution is not null or won_contribution is not null))
