{{ config(materialized='incremental', incremental_strategy='append', engine='MergeTree()', schema='stg_hubspot', unique_key='source_version_key', order_by=['source_identity_key','source_version_key'], full_refresh=false, on_schema_change='fail', tags=['capture']) }}
with extracted as (
select
    CAST(`id` AS String) AS src_id,
    CAST(`properties_email` AS String) AS src_email,
    CAST(`properties_createdate` AS Nullable(DateTime64(3,'UTC'))) AS src_created_at,
    CAST(`properties_lifecyclestage` AS String) AS src_lifecycle_stage,
    CAST(`properties_hs_latest_source` AS String) AS src_latest_source,
    CAST(`properties_utm_source` AS String) AS src_utm_source,
    CAST(`properties_utm_campaign` AS String) AS src_utm_campaign,
    CAST(`properties_first_conversion_event_name` AS String) AS src_first_conversion_name,
    CAST(`properties_first_conversion_date` AS Nullable(DateTime64(3,'UTC'))) AS src_first_conversion_at,
    CAST(`properties_boondid` AS String) AS src_boond_contact_id,
    CAST(`properties_statut_boond` AS String) AS src_boond_state_id,
    CAST(`properties_creation_boond` AS Nullable(DateTime64(3,'UTC'))) AS src_boond_created_at,
    CAST(`properties_hubspot_owner_id` AS String) AS src_hubspot_owner_id,
    CAST(`archived` AS Bool) AS src_is_archived,
    CAST(`updatedAt` AS DateTime64(3,'UTC')) AS src_updated_at
from {{ source('hubspot', 'contacts') }}
), hashed as (select
    `src_id`,
    `src_email`,
    `src_created_at`,
    `src_lifecycle_stage`,
    `src_latest_source`,
    `src_utm_source`,
    `src_utm_campaign`,
    `src_first_conversion_name`,
    `src_first_conversion_at`,
    `src_boond_contact_id`,
    `src_boond_state_id`,
    `src_boond_created_at`,
    `src_hubspot_owner_id`,
    `src_is_archived`,
    `src_updated_at`,
    {{ typed_hash('source_identity_v1:hubspot.contacts', [{'name': 'src_id', 'type': 'String', 'expr': 'src_id'}]) }} AS source_identity_key,
    {{ typed_hash('source_payload_v1:hubspot.contacts', [{'name': 'src_id', 'type': 'String', 'expr': 'src_id'}, {'name': 'src_email', 'type': 'String', 'expr': 'src_email'}, {'name': 'src_created_at', 'type': "Nullable(DateTime64(3,'UTC'))", 'expr': 'src_created_at'}, {'name': 'src_lifecycle_stage', 'type': 'String', 'expr': 'src_lifecycle_stage'}, {'name': 'src_latest_source', 'type': 'String', 'expr': 'src_latest_source'}, {'name': 'src_utm_source', 'type': 'String', 'expr': 'src_utm_source'}, {'name': 'src_utm_campaign', 'type': 'String', 'expr': 'src_utm_campaign'}, {'name': 'src_first_conversion_name', 'type': 'String', 'expr': 'src_first_conversion_name'}, {'name': 'src_first_conversion_at', 'type': "Nullable(DateTime64(3,'UTC'))", 'expr': 'src_first_conversion_at'}, {'name': 'src_boond_contact_id', 'type': 'String', 'expr': 'src_boond_contact_id'}, {'name': 'src_boond_state_id', 'type': 'String', 'expr': 'src_boond_state_id'}, {'name': 'src_boond_created_at', 'type': "Nullable(DateTime64(3,'UTC'))", 'expr': 'src_boond_created_at'}, {'name': 'src_hubspot_owner_id', 'type': 'String', 'expr': 'src_hubspot_owner_id'}, {'name': 'src_is_archived', 'type': 'Bool', 'expr': 'src_is_archived'}, {'name': 'src_updated_at', 'type': "DateTime64(3,'UTC')", 'expr': 'src_updated_at'}]) }} AS source_payload_hash
from extracted
group by src_id, src_email, src_created_at, src_lifecycle_stage, src_latest_source, src_utm_source, src_utm_campaign, src_first_conversion_name, src_first_conversion_at, src_boond_contact_id, src_boond_state_id, src_boond_created_at, src_hubspot_owner_id, src_is_archived, src_updated_at
)
{% if is_incremental() %}, previous as (select
    `src_id`,
    `src_email`,
    `src_created_at`,
    `src_lifecycle_stage`,
    `src_latest_source`,
    `src_utm_source`,
    `src_utm_campaign`,
    `src_first_conversion_name`,
    `src_first_conversion_at`,
    `src_boond_contact_id`,
    `src_boond_state_id`,
    `src_boond_created_at`,
    `src_hubspot_owner_id`,
    `src_is_archived`,
    `src_updated_at`,
    `source_identity_key`,
    `source_payload_hash`,
    `is_source_present`
from {{ this }}
where capture_key in ({% for key in var('source_capture_keys', {}).get('hubspot.contacts', []) %}{{ ch_literal(key) }}{{ ',' if not loop.last }}{% else %}''{% endfor %})
qualify row_number() over (partition by source_identity_key order by capture_at desc,capture_key desc)=1
)
{% endif %}, changes as (
select
    h.`src_id` AS `src_id`,
    h.`src_email` AS `src_email`,
    h.`src_created_at` AS `src_created_at`,
    h.`src_lifecycle_stage` AS `src_lifecycle_stage`,
    h.`src_latest_source` AS `src_latest_source`,
    h.`src_utm_source` AS `src_utm_source`,
    h.`src_utm_campaign` AS `src_utm_campaign`,
    h.`src_first_conversion_name` AS `src_first_conversion_name`,
    h.`src_first_conversion_at` AS `src_first_conversion_at`,
    h.`src_boond_contact_id` AS `src_boond_contact_id`,
    h.`src_boond_state_id` AS `src_boond_state_id`,
    h.`src_boond_created_at` AS `src_boond_created_at`,
    h.`src_hubspot_owner_id` AS `src_hubspot_owner_id`,
    h.`src_is_archived` AS `src_is_archived`,
    h.`src_updated_at` AS `src_updated_at`,
    h.`source_identity_key` AS `source_identity_key`,
    h.`source_payload_hash` AS `source_payload_hash`,
    true AS is_source_present
from hashed h
{% if is_incremental() %}
left join previous p on h.source_identity_key=p.source_identity_key
where p.source_identity_key is null or p.source_payload_hash!=h.source_payload_hash or not p.is_source_present
union all
select
    p.`src_id` AS `src_id`,
    p.`src_email` AS `src_email`,
    p.`src_created_at` AS `src_created_at`,
    p.`src_lifecycle_stage` AS `src_lifecycle_stage`,
    p.`src_latest_source` AS `src_latest_source`,
    p.`src_utm_source` AS `src_utm_source`,
    p.`src_utm_campaign` AS `src_utm_campaign`,
    p.`src_first_conversion_name` AS `src_first_conversion_name`,
    p.`src_first_conversion_at` AS `src_first_conversion_at`,
    p.`src_boond_contact_id` AS `src_boond_contact_id`,
    p.`src_boond_state_id` AS `src_boond_state_id`,
    p.`src_boond_created_at` AS `src_boond_created_at`,
    p.`src_hubspot_owner_id` AS `src_hubspot_owner_id`,
    p.`src_is_archived` AS `src_is_archived`,
    p.`src_updated_at` AS `src_updated_at`,
    p.`source_identity_key` AS `source_identity_key`,
    p.`source_payload_hash` AS `source_payload_hash`,
    false AS is_source_present
from previous p
left anti join hashed h on p.source_identity_key=h.source_identity_key
where p.is_source_present
{% endif %}
), run_constants as (select {{ ch_literal(var('capture_key','parse_only')) }} as capture_token), candidate as (select
    `src_id`,
    `src_email`,
    `src_created_at`,
    `src_lifecycle_stage`,
    `src_latest_source`,
    `src_utm_source`,
    `src_utm_campaign`,
    `src_first_conversion_name`,
    `src_first_conversion_at`,
    `src_boond_contact_id`,
    `src_boond_state_id`,
    `src_boond_created_at`,
    `src_hubspot_owner_id`,
    `src_is_archived`,
    `src_updated_at`,
    `source_identity_key`,
    `source_payload_hash`,
    {{ typed_hash('source_version_v1:hubspot.contacts', [{'name': 'identity', 'type': 'String', 'expr': 'source_identity_key'}, {'name': 'capture_key', 'type': 'String', 'expr': 'capture_token'}, {'name': 'payload', 'type': 'String', 'expr': 'source_payload_hash'}, {'name': 'presence', 'type': 'Bool', 'expr': 'is_source_present'}]) }} AS source_version_key,
    {{ utc_var('capture_at') }} AS imported_at,
    {{ ch_literal(var('capture_key','parse_only')) }} AS capture_key,
    {{ utc_var('capture_at') }} AS capture_at,
    is_source_present
from changes cross join run_constants)
select
    c.`src_id` AS `src_id`,
    c.`src_email` AS `src_email`,
    c.`src_created_at` AS `src_created_at`,
    c.`src_lifecycle_stage` AS `src_lifecycle_stage`,
    c.`src_latest_source` AS `src_latest_source`,
    c.`src_utm_source` AS `src_utm_source`,
    c.`src_utm_campaign` AS `src_utm_campaign`,
    c.`src_first_conversion_name` AS `src_first_conversion_name`,
    c.`src_first_conversion_at` AS `src_first_conversion_at`,
    c.`src_boond_contact_id` AS `src_boond_contact_id`,
    c.`src_boond_state_id` AS `src_boond_state_id`,
    c.`src_boond_created_at` AS `src_boond_created_at`,
    c.`src_hubspot_owner_id` AS `src_hubspot_owner_id`,
    c.`src_is_archived` AS `src_is_archived`,
    c.`src_updated_at` AS `src_updated_at`,
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
