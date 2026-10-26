-- Recompute quantiles after filtering passages; entry team remains the attribution rule.
with parameters as (
 select {{ utc_var('observation_at',var('case_as_of_boundary_at','2026-09-30T22:00:00.000Z')) }} as observed,
 CAST({{ ch_literal(var('duration_threshold_days',21)) }} AS Nullable(Float64)) as threshold
), measured as (
 select d.model_run_id,d.visit_key,d.entry_team_key,d.entered_at,d.exited_at,
 d.completed_duration_days,p.threshold,
 multiIf(d.entered_at is null,'not_observable',d.entered_at>p.observed,'future',
 d.exited_at<=p.observed,'completed',d.observation_end_at<=p.observed,'not_observable','current') as population,
 if(population='current',dateDiff('millisecond',d.entered_at,p.observed)/86400000.,NULL) as current_age_days,
 if(population='current' and p.threshold is not null,current_age_days>p.threshold,NULL) as is_above_threshold,
 {{ duration_bin('current_age_days') }} as duration_class
 from {{ ref('dataset_stage_visits') }} d cross join parameters p
 where ({{ ch_literal(var('team_key',none)) }} is null or d.entry_team_key={{ ch_literal(var('team_key',none)) }})
)
select model_run_id,population,count() as nb_visits,
 if(countIf(population='completed')>0,quantileExactInclusiveIf(0.5)(completed_duration_days,population='completed'),NULL) as median_completed,
 if(countIf(population='completed')>0,quantileExactInclusiveIf(0.9)(completed_duration_days,population='completed'),NULL) as p90_completed,
 if(countIf(population='current')>0,quantileExactInclusiveIf(0.5)(current_age_days,population='current'),NULL) as median_current_age,
 if(population='current' and any(threshold) is not null,countIf(is_above_threshold),NULL) as nb_above_threshold
from measured
group by model_run_id,population
