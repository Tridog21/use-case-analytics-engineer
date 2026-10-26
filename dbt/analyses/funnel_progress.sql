with observed as (
 select model_run_id,sale_type_id,target_stage_id,target_stage_label,funnel_position,opportunity_key,
 first_reached_observed_at,previous_stage_first_reached_at,transition_reached_at
 from {{ ref('dataset_funnel_progress') }}
 where ({{ ch_literal(var('sale_type_id',none)) }} is null or sale_type_id={{ ch_literal(var('sale_type_id',none)) }})
 and ({{ ch_literal(var('team_key',none)) }} is null or team_key={{ ch_literal(var('team_key',none)) }})
)
select model_run_id,sale_type_id,target_stage_id,target_stage_label,funnel_position,
 uniqExactIf(opportunity_key,first_reached_observed_at<{{ utc_var('observation_at','2026-09-30T22:00:00.000Z') }}) as nb_reached,
 countIf(previous_stage_first_reached_at<{{ utc_var('observation_at','2026-09-30T22:00:00.000Z') }}) as nb_transition_base,
 countIf(transition_reached_at<{{ utc_var('observation_at','2026-09-30T22:00:00.000Z') }})/nullIf(nb_transition_base,0) as transition_rate
from observed group by model_run_id,sale_type_id,target_stage_id,target_stage_label,funnel_position
