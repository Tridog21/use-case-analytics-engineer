{{ config(materialized='incremental', incremental_strategy='append', engine='MergeTree()', schema='stg_reference', unique_key='source_version_key', order_by=['source_identity_key','source_version_key'], full_refresh=false, on_schema_change='fail', tags=['capture']) }}
with extracted as (
select
    CAST(`state_id` AS Int64) AS src_state_id,
    CAST(`segment` AS String) AS src_segment,
    CAST(`probability` AS Float64) AS src_probability
from {{ source('case_reference', 'stage_probabilities') }}
), hashed as (select
    `src_state_id`,
    `src_segment`,
    `src_probability`,
    {{ typed_hash('source_identity_v1:case_reference.stage_probabilities', [{'name': 'src_state_id', 'type': 'Int64', 'expr': 'src_state_id'}, {'name': 'src_segment', 'type': 'String', 'expr': 'src_segment'}]) }} AS source_identity_key,
    {{ typed_hash('source_payload_v1:case_reference.stage_probabilities', [{'name': 'src_state_id', 'type': 'Int64', 'expr': 'src_state_id'}, {'name': 'src_segment', 'type': 'String', 'expr': 'src_segment'}, {'name': 'src_probability', 'type': 'Float64', 'expr': 'src_probability'}]) }} AS source_payload_hash
from extracted
group by src_state_id, src_segment, src_probability
)
{% if is_incremental() %}, previous as (select
    `src_state_id`,
    `src_segment`,
    `src_probability`,
    `source_identity_key`,
    `source_payload_hash`,
    `is_source_present`
from {{ this }}
where capture_key in ({% for key in var('source_capture_keys', {}).get('case_reference.stage_probabilities', []) %}{{ ch_literal(key) }}{{ ',' if not loop.last }}{% else %}''{% endfor %})
qualify row_number() over (partition by source_identity_key order by capture_at desc,capture_key desc)=1
)
{% endif %}, changes as (
select
    h.`src_state_id` AS `src_state_id`,
    h.`src_segment` AS `src_segment`,
    h.`src_probability` AS `src_probability`,
    h.`source_identity_key` AS `source_identity_key`,
    h.`source_payload_hash` AS `source_payload_hash`,
    true AS is_source_present
from hashed h
{% if is_incremental() %}
left join previous p on h.source_identity_key=p.source_identity_key
where p.source_identity_key is null or p.source_payload_hash!=h.source_payload_hash or not p.is_source_present
union all
select
    p.`src_state_id` AS `src_state_id`,
    p.`src_segment` AS `src_segment`,
    p.`src_probability` AS `src_probability`,
    p.`source_identity_key` AS `source_identity_key`,
    p.`source_payload_hash` AS `source_payload_hash`,
    false AS is_source_present
from previous p
left anti join hashed h on p.source_identity_key=h.source_identity_key
where p.is_source_present
{% endif %}
), run_constants as (select {{ ch_literal(var('capture_key','parse_only')) }} as capture_token), candidate as (select
    `src_state_id`,
    `src_segment`,
    `src_probability`,
    `source_identity_key`,
    `source_payload_hash`,
    {{ typed_hash('source_version_v1:case_reference.stage_probabilities', [{'name': 'identity', 'type': 'String', 'expr': 'source_identity_key'}, {'name': 'capture_key', 'type': 'String', 'expr': 'capture_token'}, {'name': 'payload', 'type': 'String', 'expr': 'source_payload_hash'}, {'name': 'presence', 'type': 'Bool', 'expr': 'is_source_present'}]) }} AS source_version_key,
    {{ utc_var('capture_at') }} AS imported_at,
    {{ ch_literal(var('capture_key','parse_only')) }} AS capture_key,
    {{ utc_var('capture_at') }} AS capture_at,
    is_source_present
from changes cross join run_constants)
select
    c.`src_state_id` AS `src_state_id`,
    c.`src_segment` AS `src_segment`,
    c.`src_probability` AS `src_probability`,
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
