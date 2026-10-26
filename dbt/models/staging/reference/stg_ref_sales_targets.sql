{{ config(materialized='incremental', incremental_strategy='append', engine='MergeTree()', schema='stg_reference', unique_key='source_version_key', order_by=['source_identity_key','source_version_key'], full_refresh=false, on_schema_change='fail', tags=['capture']) }}
with extracted as (
select
    CAST(`month` AS Date) AS src_month_date,
    CAST(`segment` AS String) AS src_segment,
    CAST(`indicator` AS String) AS src_indicator,
    CAST(`target` AS Float64) AS src_target
from {{ source('case_reference', 'sales_targets') }}
), hashed as (select
    `src_month_date`,
    `src_segment`,
    `src_indicator`,
    `src_target`,
    {{ typed_hash('source_identity_v1:case_reference.sales_targets', [{'name': 'src_month_date', 'type': 'Date', 'expr': 'src_month_date'}, {'name': 'src_segment', 'type': 'String', 'expr': 'src_segment'}, {'name': 'src_indicator', 'type': 'String', 'expr': 'src_indicator'}]) }} AS source_identity_key,
    {{ typed_hash('source_payload_v1:case_reference.sales_targets', [{'name': 'src_month_date', 'type': 'Date', 'expr': 'src_month_date'}, {'name': 'src_segment', 'type': 'String', 'expr': 'src_segment'}, {'name': 'src_indicator', 'type': 'String', 'expr': 'src_indicator'}, {'name': 'src_target', 'type': 'Float64', 'expr': 'src_target'}]) }} AS source_payload_hash
from extracted
group by src_month_date, src_segment, src_indicator, src_target
)
{% if is_incremental() %}, previous as (select
    `src_month_date`,
    `src_segment`,
    `src_indicator`,
    `src_target`,
    `source_identity_key`,
    `source_payload_hash`,
    `is_source_present`
from {{ this }}
where capture_key in ({% for key in var('source_capture_keys', {}).get('case_reference.sales_targets', []) %}{{ ch_literal(key) }}{{ ',' if not loop.last }}{% else %}''{% endfor %})
qualify row_number() over (partition by source_identity_key order by capture_at desc,capture_key desc)=1
)
{% endif %}, changes as (
select
    h.`src_month_date` AS `src_month_date`,
    h.`src_segment` AS `src_segment`,
    h.`src_indicator` AS `src_indicator`,
    h.`src_target` AS `src_target`,
    h.`source_identity_key` AS `source_identity_key`,
    h.`source_payload_hash` AS `source_payload_hash`,
    true AS is_source_present
from hashed h
{% if is_incremental() %}
left join previous p on h.source_identity_key=p.source_identity_key
where p.source_identity_key is null or p.source_payload_hash!=h.source_payload_hash or not p.is_source_present
union all
select
    p.`src_month_date` AS `src_month_date`,
    p.`src_segment` AS `src_segment`,
    p.`src_indicator` AS `src_indicator`,
    p.`src_target` AS `src_target`,
    p.`source_identity_key` AS `source_identity_key`,
    p.`source_payload_hash` AS `source_payload_hash`,
    false AS is_source_present
from previous p
left anti join hashed h on p.source_identity_key=h.source_identity_key
where p.is_source_present
{% endif %}
), run_constants as (select {{ ch_literal(var('capture_key','parse_only')) }} as capture_token), candidate as (select
    `src_month_date`,
    `src_segment`,
    `src_indicator`,
    `src_target`,
    `source_identity_key`,
    `source_payload_hash`,
    {{ typed_hash('source_version_v1:case_reference.sales_targets', [{'name': 'identity', 'type': 'String', 'expr': 'source_identity_key'}, {'name': 'capture_key', 'type': 'String', 'expr': 'capture_token'}, {'name': 'payload', 'type': 'String', 'expr': 'source_payload_hash'}, {'name': 'presence', 'type': 'Bool', 'expr': 'is_source_present'}]) }} AS source_version_key,
    {{ utc_var('capture_at') }} AS imported_at,
    {{ ch_literal(var('capture_key','parse_only')) }} AS capture_key,
    {{ utc_var('capture_at') }} AS capture_at,
    is_source_present
from changes cross join run_constants)
select
    c.`src_month_date` AS `src_month_date`,
    c.`src_segment` AS `src_segment`,
    c.`src_indicator` AS `src_indicator`,
    c.`src_target` AS `src_target`,
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
