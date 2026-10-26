{{ config(tags=['capture']) }}
{% set columns=['src_setting_state_opportunity_json','src_setting_type_of_project_json','src_setting_origin_json','src_setting_action_contact_json','src_setting_state_company_json','src_setting_state_contact_json','src_setting_state_resource_json','src_setting_state_delivery_json'] %}
with fields as (
{% for name in columns %}
select source_version_key,{{ ch_literal(name) }} as field_name,{{ name }} as payload
from {{ ref('stg_boond_dictionaries') }}
{{ 'union all' if not loop.last }}
{% endfor %}
), evaluated as (
select source_version_key,field_name,payload is not null as is_present,
isValidJSON(ifNull(payload,'')) and startsWith(trim(ifNull(payload,'')),'[') as is_array,
arrayExists(item -> not JSONHas(item,'id') or toString(JSONType(item,'id')) not in ('Int64','UInt64'),
 JSONExtractArrayRaw(if(is_array,ifNull(payload,'[]'),'[]'))) as has_invalid_id
from fields
)
select source_version_key,field_name from evaluated where is_present and (not is_array or has_invalid_id)
