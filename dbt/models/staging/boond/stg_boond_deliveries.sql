{{ config(materialized='incremental', incremental_strategy='append', engine='MergeTree()', schema='stg_boond', unique_key='source_version_key', order_by=['source_identity_key','source_version_key'], full_refresh=false, on_schema_change='fail', tags=['capture']) }}
{% set lower_bound=cdc_watermark() %}
with extracted as (
select
    CAST(`meta.customer` AS String) AS src_tenant_id,
    CAST(`id` AS Int64) AS src_id,
    CAST(`meta.deleted` AS Bool) AS src_is_deleted,
    CAST(`meta.ts` AS DateTime64(3,'UTC')) AS src_published_at,
    CAST(`title` AS String) AS src_title,
    CAST(`state` AS Nullable(Int64)) AS src_state_id,
    CAST(`startDate` AS Nullable(DateTime64(3,'UTC'))) AS src_started_at,
    CAST(`endDate` AS Nullable(DateTime64(3,'UTC'))) AS src_ended_at,
    CAST(`averageDailyPriceExcludingTax` AS Nullable(Float64)) AS src_average_daily_price_excluding_tax,
    CAST(`creationDate` AS Nullable(DateTime64(3,'UTC'))) AS src_created_at,
    CAST(`updateDate` AS Nullable(DateTime64(3,'UTC'))) AS src_updated_at,
    CAST(`relationships.project.data.id` AS Nullable(Int64)) AS src_project_id,
    CAST(`attributes` AS String) AS src_attributes
from {{ source('boond', 'deliveries') }}
{% if lower_bound is not none %}where `meta.ts` >= parseDateTime64BestEffort({{ ch_literal(lower_bound) }},3,'UTC'){% endif %}
), hashed as (select
    `src_tenant_id`,
    `src_id`,
    `src_is_deleted`,
    `src_published_at`,
    `src_title`,
    `src_state_id`,
    `src_started_at`,
    `src_ended_at`,
    `src_average_daily_price_excluding_tax`,
    `src_created_at`,
    `src_updated_at`,
    `src_project_id`,
    `src_attributes`,
    {{ typed_hash('source_identity_v1:boond.deliveries', [{'name': 'src_tenant_id', 'type': 'String', 'expr': 'src_tenant_id'}, {'name': 'src_id', 'type': 'Int64', 'expr': 'src_id'}]) }} AS source_identity_key,
    {{ typed_hash('source_payload_v1:boond.deliveries', [{'name': 'src_tenant_id', 'type': 'String', 'expr': 'src_tenant_id'}, {'name': 'src_id', 'type': 'Int64', 'expr': 'src_id'}, {'name': 'src_is_deleted', 'type': 'Bool', 'expr': 'src_is_deleted'}, {'name': 'src_published_at', 'type': "DateTime64(3,'UTC')", 'expr': 'src_published_at'}, {'name': 'src_title', 'type': 'String', 'expr': 'src_title'}, {'name': 'src_state_id', 'type': 'Nullable(Int64)', 'expr': 'src_state_id'}, {'name': 'src_started_at', 'type': "Nullable(DateTime64(3,'UTC'))", 'expr': 'src_started_at'}, {'name': 'src_ended_at', 'type': "Nullable(DateTime64(3,'UTC'))", 'expr': 'src_ended_at'}, {'name': 'src_average_daily_price_excluding_tax', 'type': 'Nullable(Float64)', 'expr': 'src_average_daily_price_excluding_tax'}, {'name': 'src_created_at', 'type': "Nullable(DateTime64(3,'UTC'))", 'expr': 'src_created_at'}, {'name': 'src_updated_at', 'type': "Nullable(DateTime64(3,'UTC'))", 'expr': 'src_updated_at'}, {'name': 'src_project_id', 'type': 'Nullable(Int64)', 'expr': 'src_project_id'}, {'name': 'src_attributes', 'type': 'String', 'expr': 'src_attributes'}]) }} AS source_payload_hash
from extracted
group by src_tenant_id, src_id, src_is_deleted, src_published_at, src_title, src_state_id, src_started_at, src_ended_at, src_average_daily_price_excluding_tax, src_created_at, src_updated_at, src_project_id, src_attributes
), changes as (select
    `src_tenant_id`,
    `src_id`,
    `src_is_deleted`,
    `src_published_at`,
    `src_title`,
    `src_state_id`,
    `src_started_at`,
    `src_ended_at`,
    `src_average_daily_price_excluding_tax`,
    `src_created_at`,
    `src_updated_at`,
    `src_project_id`,
    `src_attributes`,
    `source_identity_key`,
    `source_payload_hash`,
    true AS is_source_present
from hashed), run_constants as (select {{ ch_literal(var('capture_key','parse_only')) }} as capture_token), candidate as (select
    `src_tenant_id`,
    `src_id`,
    `src_is_deleted`,
    `src_published_at`,
    `src_title`,
    `src_state_id`,
    `src_started_at`,
    `src_ended_at`,
    `src_average_daily_price_excluding_tax`,
    `src_created_at`,
    `src_updated_at`,
    `src_project_id`,
    `src_attributes`,
    `source_identity_key`,
    `source_payload_hash`,
    {{ typed_hash('source_version_v1:boond.deliveries', [{'name': 'identity', 'type': 'String', 'expr': 'source_identity_key'}, {'name': 'publication', 'type': "DateTime64(3,'UTC')", 'expr': 'src_published_at'}, {'name': 'payload', 'type': 'String', 'expr': 'source_payload_hash'}]) }} AS source_version_key,
    {{ utc_var('capture_at') }} AS imported_at,
    {{ ch_literal(var('capture_key','parse_only')) }} AS capture_key,
    {{ utc_var('capture_at') }} AS capture_at,
    is_source_present
from changes cross join run_constants)
select
    c.`src_tenant_id` AS `src_tenant_id`,
    c.`src_id` AS `src_id`,
    c.`src_is_deleted` AS `src_is_deleted`,
    c.`src_published_at` AS `src_published_at`,
    c.`src_title` AS `src_title`,
    c.`src_state_id` AS `src_state_id`,
    c.`src_started_at` AS `src_started_at`,
    c.`src_ended_at` AS `src_ended_at`,
    c.`src_average_daily_price_excluding_tax` AS `src_average_daily_price_excluding_tax`,
    c.`src_created_at` AS `src_created_at`,
    c.`src_updated_at` AS `src_updated_at`,
    c.`src_project_id` AS `src_project_id`,
    c.`src_attributes` AS `src_attributes`,
    c.`source_identity_key` AS `source_identity_key`,
    c.`source_payload_hash` AS `source_payload_hash`,
    c.`source_version_key` AS `source_version_key`,
    c.`imported_at` AS `imported_at`,
    c.`capture_key` AS `capture_key`,
    c.`capture_at` AS `capture_at`,
    c.`is_source_present` AS `is_source_present`
from candidate c
{% if is_incremental() %}
left anti join {{ this }} t on c.source_version_key=t.source_version_key
{% endif %}
