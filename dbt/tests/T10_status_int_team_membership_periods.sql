{{ config(tags=['common']) }}
select record_key from {{ ref('int_team_membership_periods') }} where model_run_id={{ ch_literal(var('test_model_run_id','')) }} and calculation_status not in ('ready','partial','blocked','not_applicable')
