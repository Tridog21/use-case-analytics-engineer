{{ config(materialized='incremental', incremental_strategy='append', engine='MergeTree()', schema='stg_boond', unique_key='source_version_key', order_by=['source_identity_key','source_version_key'], full_refresh=false, on_schema_change='fail', tags=['capture']) }}
{% set lower_bound=cdc_watermark() %}
with extracted as (
select
    CAST(`meta.customer` AS String) AS src_tenant_id,
    CAST(`meta.deleted` AS Bool) AS src_is_deleted,
    CAST(`meta.ts` AS DateTime64(3,'UTC')) AS src_published_at,
    CAST(`meta.language` AS String) AS src_language,
    CAST(`setting.state.opportunity` AS Nullable(String)) AS src_setting_state_opportunity_json,
    CAST(`setting.typeOf.project` AS LowCardinality(String)) AS src_setting_type_of_project_json,
    CAST(`setting.origin` AS String) AS src_setting_origin_json,
    CAST(`setting.action.contact` AS String) AS src_setting_action_contact_json,
    CAST(`setting.state.company` AS Nullable(String)) AS src_setting_state_company_json,
    CAST(`setting.state.contact` AS Nullable(String)) AS src_setting_state_contact_json,
    CAST(`setting.state.resource` AS Nullable(String)) AS src_setting_state_resource_json,
    CAST(`setting.state.delivery` AS Nullable(String)) AS src_setting_state_delivery_json
from {{ source('boond', 'dictionaries') }}
{% if lower_bound is not none %}where `meta.ts` >= parseDateTime64BestEffort({{ ch_literal(lower_bound) }},3,'UTC'){% endif %}
), hashed as (select
    `src_tenant_id`,
    `src_is_deleted`,
    `src_published_at`,
    `src_language`,
    `src_setting_state_opportunity_json`,
    `src_setting_type_of_project_json`,
    `src_setting_origin_json`,
    `src_setting_action_contact_json`,
    `src_setting_state_company_json`,
    `src_setting_state_contact_json`,
    `src_setting_state_resource_json`,
    `src_setting_state_delivery_json`,
    {{ typed_hash('source_identity_v1:boond.dictionaries', [{'name': 'src_tenant_id', 'type': 'String', 'expr': 'src_tenant_id'}, {'name': 'src_language', 'type': 'String', 'expr': 'src_language'}]) }} AS source_identity_key,
    {{ typed_hash('source_payload_v1:boond.dictionaries', [{'name': 'src_tenant_id', 'type': 'String', 'expr': 'src_tenant_id'}, {'name': 'src_is_deleted', 'type': 'Bool', 'expr': 'src_is_deleted'}, {'name': 'src_published_at', 'type': "DateTime64(3,'UTC')", 'expr': 'src_published_at'}, {'name': 'src_language', 'type': 'String', 'expr': 'src_language'}, {'name': 'src_setting_state_opportunity_json', 'type': 'Nullable(String)', 'expr': 'src_setting_state_opportunity_json'}, {'name': 'src_setting_type_of_project_json', 'type': 'LowCardinality(String)', 'expr': 'src_setting_type_of_project_json'}, {'name': 'src_setting_origin_json', 'type': 'String', 'expr': 'src_setting_origin_json'}, {'name': 'src_setting_action_contact_json', 'type': 'String', 'expr': 'src_setting_action_contact_json'}, {'name': 'src_setting_state_company_json', 'type': 'Nullable(String)', 'expr': 'src_setting_state_company_json'}, {'name': 'src_setting_state_contact_json', 'type': 'Nullable(String)', 'expr': 'src_setting_state_contact_json'}, {'name': 'src_setting_state_resource_json', 'type': 'Nullable(String)', 'expr': 'src_setting_state_resource_json'}, {'name': 'src_setting_state_delivery_json', 'type': 'Nullable(String)', 'expr': 'src_setting_state_delivery_json'}]) }} AS source_payload_hash
from extracted
group by src_tenant_id, src_is_deleted, src_published_at, src_language, src_setting_state_opportunity_json, src_setting_type_of_project_json, src_setting_origin_json, src_setting_action_contact_json, src_setting_state_company_json, src_setting_state_contact_json, src_setting_state_resource_json, src_setting_state_delivery_json
), changes as (select
    `src_tenant_id`,
    `src_is_deleted`,
    `src_published_at`,
    `src_language`,
    `src_setting_state_opportunity_json`,
    `src_setting_type_of_project_json`,
    `src_setting_origin_json`,
    `src_setting_action_contact_json`,
    `src_setting_state_company_json`,
    `src_setting_state_contact_json`,
    `src_setting_state_resource_json`,
    `src_setting_state_delivery_json`,
    `source_identity_key`,
    `source_payload_hash`,
    true AS is_source_present
from hashed), run_constants as (select {{ ch_literal(var('capture_key','parse_only')) }} as capture_token), candidate as (select
    `src_tenant_id`,
    `src_is_deleted`,
    `src_published_at`,
    `src_language`,
    `src_setting_state_opportunity_json`,
    `src_setting_type_of_project_json`,
    `src_setting_origin_json`,
    `src_setting_action_contact_json`,
    `src_setting_state_company_json`,
    `src_setting_state_contact_json`,
    `src_setting_state_resource_json`,
    `src_setting_state_delivery_json`,
    `source_identity_key`,
    `source_payload_hash`,
    {{ typed_hash('source_version_v1:boond.dictionaries', [{'name': 'identity', 'type': 'String', 'expr': 'source_identity_key'}, {'name': 'publication', 'type': "DateTime64(3,'UTC')", 'expr': 'src_published_at'}, {'name': 'payload', 'type': 'String', 'expr': 'source_payload_hash'}]) }} AS source_version_key,
    {{ utc_var('capture_at') }} AS imported_at,
    {{ ch_literal(var('capture_key','parse_only')) }} AS capture_key,
    {{ utc_var('capture_at') }} AS capture_at,
    is_source_present
from changes cross join run_constants)
select
    c.`src_tenant_id` AS `src_tenant_id`,
    c.`src_is_deleted` AS `src_is_deleted`,
    c.`src_published_at` AS `src_published_at`,
    c.`src_language` AS `src_language`,
    c.`src_setting_state_opportunity_json` AS `src_setting_state_opportunity_json`,
    c.`src_setting_type_of_project_json` AS `src_setting_type_of_project_json`,
    c.`src_setting_origin_json` AS `src_setting_origin_json`,
    c.`src_setting_action_contact_json` AS `src_setting_action_contact_json`,
    c.`src_setting_state_company_json` AS `src_setting_state_company_json`,
    c.`src_setting_state_contact_json` AS `src_setting_state_contact_json`,
    c.`src_setting_state_resource_json` AS `src_setting_state_resource_json`,
    c.`src_setting_state_delivery_json` AS `src_setting_state_delivery_json`,
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
