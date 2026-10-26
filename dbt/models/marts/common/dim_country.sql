-- depends_on: {{ ref('stg_boond_companies') }}
-- depends_on: {{ ref('stg_boond_agencies') }}
{{ config(materialized='incremental', incremental_strategy='append', engine='MergeTree()', schema='dtm_common', unique_key='record_version_key', order_by=['model_run_id','record_key'], full_refresh=false, on_schema_change='fail', tags=['common']) }}
{{ assert_case_vars() }}
with countries as (select upper(trim(src_country)) as code, source_version_key, src_published_at from {{ ref('stg_boond_companies') }} where capture_at <= {{ utc_var('input_cutoff_at') }} union all select upper(trim(src_country)), source_version_key,src_published_at from {{ ref('stg_boond_agencies') }} where capture_at <= {{ utc_var('input_cutoff_at') }}),
business as (select
    CAST(max(src_published_at) AS Nullable(DateTime64(3,'UTC'))) AS `source_published_at`,
    CAST(arraySort(groupUniqArray(source_version_key)) AS Array(String)) AS `source_version_keys`,
    CAST(lower(hex(SHA256(toJSONString(materialize(tuple('country_v1',tuple('source_country_code','String',if(isNull(code),'1','0'),ifNull(toString(code),'')))))))) AS String) AS `country_key`,
    CAST(if(code in ('FR','ES','BE','CH'),toNullable(code),NULL) AS Nullable(String)) AS `country_code`,
    CAST(code AS String) AS `source_country_code`,
    CAST(multiIf(code='FR','France',code='ES','Espagne',code='BE','Belgique',code='CH','Suisse',NULL) AS Nullable(String)) AS `country_name`,
    CAST(multiIf(code='','blank',code in ('FR','ES','BE','CH'),'mapped','unmapped') AS String) AS `mapping_status`
from countries group by code),
keyed as (select
    `source_published_at`,
    `source_version_keys`,
    `country_key`,
    `country_code`,
    `source_country_code`,
    `country_name`,
    `mapping_status`,
    {{ ch_literal(var('model_run_id','parse_only')) }} as model_run_id,
    country_key as record_key,
    {{ utc_var('calculated_at') }} as calculated_at,
    {{ ch_literal(var('rule_version','parse_only')) }} as rule_version,
    {{ utc_var('input_cutoff_at') }} as input_cutoff_at,
    cityHash64(record_key) % {{ var('write_batch_count',1)|int }} as __write_bucket
from business),
selected_rows as (select `source_published_at`,
    `source_version_keys`,
    `country_key`,
    `country_code`,
    `source_country_code`,
    `country_name`,
    `mapping_status`,
    `model_run_id`,
    `record_key`,
    `calculated_at`,
    `rule_version`,
    `input_cutoff_at` from keyed where __write_bucket={{ var('write_batch_index',0)|int }}),
identified as (select `source_published_at`,
    `source_version_keys`,
    `country_key`,
    `country_code`,
    `source_country_code`,
    `country_name`,
    `mapping_status`,
    `model_run_id`,
    `record_key`,
    `calculated_at`,
    `rule_version`,
    `input_cutoff_at`,
    {{ typed_hash('dim_country:row_v1', [{'name': 'source_published_at', 'type': "Nullable(DateTime64(3,'UTC'))", 'expr': 'source_published_at'}, {'name': 'source_version_keys', 'type': 'Array(String)', 'expr': 'source_version_keys'}, {'name': 'country_key', 'type': 'String', 'expr': 'country_key'}, {'name': 'country_code', 'type': 'Nullable(String)', 'expr': 'country_code'}, {'name': 'source_country_code', 'type': 'String', 'expr': 'source_country_code'}, {'name': 'country_name', 'type': 'Nullable(String)', 'expr': 'country_name'}, {'name': 'mapping_status', 'type': 'String', 'expr': 'mapping_status'}]) }} as row_hash from selected_rows),
candidate as (select
    `model_run_id`,
    `record_key`,
    `row_hash`,
    `calculated_at`,
    `rule_version`,
    `input_cutoff_at`,
    `source_published_at`,
    `source_version_keys`,
    `country_key`,
    `country_code`,
    `source_country_code`,
    `country_name`,
    `mapping_status`,
    lower(hex(SHA256(toJSONString(materialize(tuple('record_version_v1',tuple('model_run_id','String',if(isNull(model_run_id),'1','0'),ifNull(toString(model_run_id),'')),tuple('record_key','String',if(isNull(record_key),'1','0'),ifNull(toString(record_key),'')))))))) as record_version_key
from identified)
select
    c.`model_run_id` AS `model_run_id`,
    c.`record_key` AS `record_key`,
    c.`record_version_key` AS `record_version_key`,
    c.`row_hash` AS `row_hash`,
    c.`calculated_at` AS `calculated_at`,
    c.`rule_version` AS `rule_version`,
    c.`input_cutoff_at` AS `input_cutoff_at`,
    c.`source_published_at` AS `source_published_at`,
    c.`source_version_keys` AS `source_version_keys`,
    c.`country_key` AS `country_key`,
    c.`country_code` AS `country_code`,
    c.`source_country_code` AS `source_country_code`,
    c.`country_name` AS `country_name`,
    c.`mapping_status` AS `mapping_status`
from candidate c
{% if is_incremental() %}
left join (select model_run_id,record_key,row_hash from {{ this }} where model_run_id={{ ch_literal(var('model_run_id','parse_only')) }}) t on c.model_run_id=t.model_run_id and c.record_key=t.record_key
where if(t.record_key is null,true,throwIf(c.row_hash!=t.row_hash,'Immutable run content diverged')!=0)
{% endif %}
