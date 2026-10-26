with grouped as (
 select model_run_id,tenant_id,cohort_month,sale_type_id,followup_definition_key,horizon_days,
 max(cohort_mature_at) as mature_at,sum(nb_cohort_membership) as nb_base,
 sum(open_contribution) as nb_open,sum(won_contribution) as nb_won,sum(lost_contribution) as nb_lost,
 sum(abandoned_contribution) as nb_abandoned,sum(unqualified_contribution) as nb_unqualified,sum(unknown_contribution) as nb_unknown
 from {{ ref('dataset_cohort_outcomes') }}
 where ({{ ch_literal(var('team_key',none)) }} is null or team_key={{ ch_literal(var('team_key',none)) }})
 group by model_run_id,tenant_id,cohort_month,sale_type_id,followup_definition_key,horizon_days
)
select model_run_id,tenant_id,cohort_month,sale_type_id,followup_definition_key,horizon_days,nb_base,
 if(mature_at<={{ utc_var('observation_at','2026-09-30T22:00:00.000Z') }},nb_won/nullIf(nb_base,0),NULL) as won_rate,
 if(mature_at<={{ utc_var('observation_at','2026-09-30T22:00:00.000Z') }},nb_open/nullIf(nb_base,0),NULL) as open_rate,
 if(mature_at<={{ utc_var('observation_at','2026-09-30T22:00:00.000Z') }},nb_lost,NULL) as nb_lost,
 if(mature_at<={{ utc_var('observation_at','2026-09-30T22:00:00.000Z') }},nb_abandoned,NULL) as nb_abandoned,
 if(mature_at<={{ utc_var('observation_at','2026-09-30T22:00:00.000Z') }},nb_unqualified,NULL) as nb_unqualified,
 if(mature_at<={{ utc_var('observation_at','2026-09-30T22:00:00.000Z') }},nb_unknown,NULL) as nb_unknown
from grouped
