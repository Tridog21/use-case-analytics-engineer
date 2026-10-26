-- depends_on: {{ ref('int_publication') }}
{{ config(materialized='view', schema='dtr_sales', tags=['dataset']) }}
select
    CAST(p.model_run_id AS String) AS `model_run_id`,
    CAST(p.publication_key AS String) AS `publication_key`,
    CAST(p.published_at AS DateTime64(3,'UTC')) AS `published_at`,
    CAST(p.input_cutoff_at AS DateTime64(3,'UTC')) AS `input_cutoff_at`,
    CAST(p.rule_version AS String) AS `rule_version`,
    CAST(JSONExtractString(item,'measure_id') AS String) AS `measure_id`,
    CAST(JSONExtractString(item,'dataset_family') AS String) AS `dataset_family`,
    CAST(JSONExtractString(item,'availability_status') AS String) AS `availability_status`,
    CAST(JSONExtract(item,'availability_reason','Nullable(String)') AS Nullable(String)) AS `availability_reason`,
    CAST(JSONExtractString(item,'coverage_status') AS String) AS `coverage_status`,
    CAST(JSONExtract(item,'nb_expected','Nullable(UInt64)') AS Nullable(UInt64)) AS `nb_expected`,
    CAST(JSONExtract(item,'nb_known','Nullable(UInt64)') AS Nullable(UInt64)) AS `nb_known`,
    CAST(parseDateTime64BestEffortOrNull(JSONExtract(item,'data_coverage_end_at','Nullable(String)'),3,'UTC') AS Nullable(DateTime64(3,'UTC'))) AS `data_coverage_end_at`
from {{ ref('int_publication') }} p array join JSONExtractArrayRaw(p.quality_json) as item
