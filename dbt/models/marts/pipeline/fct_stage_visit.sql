-- depends_on: {{ ref('int_opportunity_stage_visits') }}
-- depends_on: {{ ref('int_opportunity_periods') }}
-- depends_on: {{ ref('dim_stage') }}
-- depends_on: {{ ref('dim_company') }}
-- depends_on: {{ ref('dim_sale_type') }}
-- depends_on: {{ ref('dim_channel') }}
-- depends_on: {{ ref('dim_employee') }}
-- depends_on: {{ ref('dim_team') }}
-- depends_on: {{ ref('dim_date') }}
{{ config(materialized='view', schema='dtm_pipeline', tags=['mart']) }}
select
    CAST(f.model_run_id AS String) AS `model_run_id`,
    CAST(f.record_key AS String) AS `record_key`,
    CAST(f.record_version_key AS String) AS `record_version_key`,
    CAST(f.row_hash AS String) AS `row_hash`,
    CAST(f.calculated_at AS DateTime64(3,'UTC')) AS `calculated_at`,
    CAST(f.rule_version AS String) AS `rule_version`,
    CAST(f.input_cutoff_at AS DateTime64(3,'UTC')) AS `input_cutoff_at`,
    CAST(greatest(f.source_published_at,p.source_published_at) AS Nullable(DateTime64(3,'UTC'))) AS `source_published_at`,
    CAST(arraySort(arrayDistinct(arrayConcat(f.source_version_keys,ifNull(p.source_version_keys,[])))) AS Array(String)) AS `source_version_keys`,
    CAST(f.tenant_id AS String) AS `tenant_id`,
    CAST(f.opportunity_id AS Int64) AS `opportunity_id`,
    CAST(f.opportunity_key AS String) AS `opportunity_key`,
    CAST(f.visit_key AS String) AS `visit_key`,
    CAST(f.stage_id AS Nullable(Int64)) AS `stage_id`,
    CAST(f.visit_rank AS UInt32) AS `visit_rank`,
    CAST(f.first_observed_at AS DateTime64(3,'UTC')) AS `first_observed_at`,
    CAST(f.last_observed_at AS DateTime64(3,'UTC')) AS `last_observed_at`,
    CAST(f.entered_at AS Nullable(DateTime64(3,'UTC'))) AS `entered_at`,
    CAST(f.exited_at AS Nullable(DateTime64(3,'UTC'))) AS `exited_at`,
    CAST(f.observation_ended_at AS Nullable(DateTime64(3,'UTC'))) AS `observation_ended_at`,
    CAST(f.previous_stage_id AS Nullable(Int64)) AS `previous_stage_id`,
    CAST(f.next_stage_id AS Nullable(Int64)) AS `next_stage_id`,
    CAST(f.first_source_version_key AS String) AS `first_source_version_key`,
    CAST(f.last_source_version_key AS String) AS `last_source_version_key`,
    CAST(f.event_time_basis AS String) AS `event_time_basis`,
    CAST(f.is_left_censored AS Bool) AS `is_left_censored`,
    CAST(f.is_right_censored AS Bool) AS `is_right_censored`,
    CAST(f.is_open_visit AS Bool) AS `is_open_visit`,
    CAST(f.has_observation_gap AS Bool) AS `has_observation_gap`,
    CAST(f.completed_duration_seconds AS Nullable(Float64)) AS `completed_duration_seconds`,
    CAST(f.completed_duration_days AS Nullable(Float64)) AS `completed_duration_days`,
    CAST(f.coverage_start_at AS Nullable(DateTime64(3,'UTC'))) AS `coverage_start_at`,
    CAST(f.coverage_end_at AS Nullable(DateTime64(3,'UTC'))) AS `coverage_end_at`,
    CAST(f.is_history_complete AS Nullable(Bool)) AS `is_history_complete`,
    CAST(f.calculation_status AS String) AS `calculation_status`,
    CAST(f.status_reason AS Nullable(String)) AS `status_reason`,
    CAST(p.stage_key AS Nullable(String)) AS `stage_key`,
    CAST(p.stage_version_key AS Nullable(String)) AS `stage_version_key`,
    CAST(p.company_id AS Nullable(Int64)) AS `company_id`,
    CAST(p.company_key AS Nullable(String)) AS `company_key`,
    CAST(p.company_version_key AS Nullable(String)) AS `company_version_key`,
    CAST(p.sale_type_id AS Nullable(Int64)) AS `sale_type_id`,
    CAST(p.sale_type_key AS Nullable(String)) AS `sale_type_key`,
    CAST(p.sale_type_version_key AS Nullable(String)) AS `sale_type_version_key`,
    CAST(p.acquisition_channel_key AS Nullable(String)) AS `acquisition_channel_key`,
    CAST(p.channel_version_key AS Nullable(String)) AS `channel_version_key`,
    CAST(p.channel_candidate_code AS Nullable(String)) AS `channel_candidate_code`,
    CAST(ifNull(p.is_channel_calculable,false) AS Bool) AS `is_channel_calculable`,
    CAST(if(f.entered_at is not null,p.employee_key,NULL) AS Nullable(String)) AS `entry_employee_key`,
    CAST(if(f.entered_at is not null,p.employee_version_key,NULL) AS Nullable(String)) AS `entry_employee_version_key`,
    CAST(if(f.entered_at is not null,p.team_key,NULL) AS Nullable(String)) AS `entry_team_key`,
    CAST(if(f.entered_at is not null,p.team_version_key,NULL) AS Nullable(String)) AS `entry_team_version_key`,
    CAST(if(f.entered_at is null,'first_observed_at_only','entered_at') AS String) AS `entry_context_time_basis`,
    CAST(f.entered_at is not null and p.team_key is not null AS Bool) AS `is_team_filter_available`,
    CAST(date_entered_date_key.date_key AS Nullable(UInt32)) AS `entered_date_key`,
    CAST(date_exited_date_key.date_key AS Nullable(UInt32)) AS `exited_date_key`
from {{ ref('int_opportunity_stage_visits') }} f left join {{ ref('dim_date') }} date_entered_date_key on f.model_run_id=date_entered_date_key.model_run_id and date_entered_date_key.calendar_date=toDate(f.entered_at,'Europe/Paris') left join {{ ref('dim_date') }} date_exited_date_key on f.model_run_id=date_exited_date_key.model_run_id and date_exited_date_key.calendar_date=toDate(f.exited_at,'Europe/Paris') left join {{ ref('int_opportunity_periods') }} p on f.model_run_id=p.model_run_id and f.tenant_id=p.tenant_id and f.opportunity_key=p.opportunity_key and ifNull(f.entered_at,f.first_observed_at)>=p.valid_from_at and (p.valid_to_at is null or ifNull(f.entered_at,f.first_observed_at)<p.valid_to_at)
