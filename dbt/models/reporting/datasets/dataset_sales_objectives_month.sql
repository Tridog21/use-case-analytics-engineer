-- depends_on: {{ ref('dtr_sales_objectives_month') }}
-- depends_on: {{ ref('int_publication') }}
{{ config(materialized='view', schema='dtr_sales', tags=['dataset']) }}
select
    CAST(f.model_run_id AS String) AS `model_run_id`,
    CAST(f.record_key AS String) AS `record_key`,
    CAST(f.record_version_key AS String) AS `record_version_key`,
    CAST(f.row_hash AS String) AS `row_hash`,
    CAST(f.calculated_at AS DateTime64(3, 'UTC')) AS `calculated_at`,
    CAST(f.rule_version AS String) AS `rule_version`,
    CAST(f.input_cutoff_at AS DateTime64(3, 'UTC')) AS `input_cutoff_at`,
    CAST(f.tenant_id AS String) AS `tenant_id`,
    CAST(f.month_date AS Date) AS `month_date`,
    CAST(f.source_segment AS String) AS `source_segment`,
    CAST(f.team_key AS Nullable(String)) AS `team_key`,
    CAST(f.team_version_key AS Nullable(String)) AS `team_version_key`,
    CAST(f.team_name AS Nullable(String)) AS `team_name`,
    CAST(f.metric_code AS String) AS `metric_code`,
    CAST(f.metric_key AS String) AS `metric_key`,
    CAST(f.metric_version_key AS String) AS `metric_version_key`,
    CAST(f.metric_label AS Nullable(String)) AS `metric_label`,
    CAST(f.value_unit AS String) AS `value_unit`,
    CAST(f.actual_value AS Nullable(Decimal(38,4))) AS `actual_value`,
    CAST(f.target_value AS Nullable(Decimal(38,4))) AS `target_value`,
    CAST(f.variance_value AS Nullable(Decimal(38,4))) AS `variance_value`,
    CAST(f.attainment_rate AS Nullable(Float64)) AS `attainment_rate`,
    CAST(f.is_population_compatible AS Nullable(Bool)) AS `is_population_compatible`,
    CAST(f.nb_source_contributions AS Nullable(UInt64)) AS `nb_source_contributions`,
    CAST(f.nb_uncalculable_contributions AS Nullable(UInt64)) AS `nb_uncalculable_contributions`,
    CAST(f.calculation_status AS String) AS `calculation_status`,
    CAST(f.status_reason AS Nullable(String)) AS `status_reason`
from {{ ref('dtr_sales_objectives_month') }} f inner join {{ ref('int_publication') }} p on f.model_run_id=p.model_run_id
