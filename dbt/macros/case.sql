{% macro generate_schema_name(custom_schema_name, node) -%}
  {{ (custom_schema_name if custom_schema_name else target.schema) ~ var('validation_schema_suffix','') }}
{%- endmacro %}

{% macro ch_literal(value) -%}
 {%- if value is none -%}NULL
 {%- elif value is boolean -%}{{ 'true' if value else 'false' }}
 {%- elif value is number -%}{{ value }}
 {%- else -%}'{{ (value|string).replace('\\', '\\\\').replace("'", "\\'") }}'
 {%- endif -%}
{%- endmacro %}

{% macro utc_var(name, default='1970-01-01T00:00:00.000Z') -%}
parseDateTime64BestEffort({{ ch_literal(var(name, default)) }},3,'UTC')
{%- endmacro %}

{% macro typed_hash(domain, columns) -%}
lower(hex(SHA256(toJSONString(materialize(tuple({{ ch_literal(domain) }}
{%- for c in columns -%}
, tuple({{ ch_literal(c.name) }}, {{ ch_literal(c.type) }}, if(isNull({{ c.expr }}),'1','0'),
 {%- if 'DateTime' in c.type -%}ifNull(toString(toUnixTimestamp64Milli({{ c.expr }})),'')
 {%- elif 'Bool' in c.type -%}ifNull(toString(toUInt8({{ c.expr }})),'')
 {%- elif 'Decimal' in c.type -%}ifNull(toDecimalString({{ c.expr }},{{ c.type.split(',')[-1].replace(')','')|int }}),'')
 {%- else -%}ifNull(toString({{ c.expr }}),''){%- endif -%})
{%- endfor -%}
))))))
{%- endmacro %}

{% macro source_identity_key(domain, columns) -%}{{ typed_hash('source_identity_v1:' ~ domain, columns) }}{%- endmacro %}
{% macro source_version_key(domain, columns) -%}{{ typed_hash('source_version_v1:' ~ domain, columns) }}{%- endmacro %}
{% macro record_key(domain, columns) -%}{{ typed_hash(domain ~ '_v1', columns) }}{%- endmacro %}

{% macro cdc_watermark() %}
 {% if var('cdc_full_scan', false) %}{{ return(none) }}{% endif %}
 {% if var('cdc_replay_from_at',none) is not none %}{{ return(var('cdc_replay_from_at')) }}{% endif %}
 {% if execute and is_incremental() %}
  {% set result=run_query('select maxOrNull(src_published_at) - INTERVAL ' ~ (var('cdc_overlap_hours',48)|int) ~ ' HOUR from ' ~ this) %}
  {% if result.rows[0][0] is not none %}{{ return(result.rows[0][0]|string) }}{% endif %}
 {% endif %}
 {{ return(none) }}
{% endmacro %}

{% macro complete_run_rows(cte, columns) -%}
select {% for c in columns %}r.{{ adapter.quote(c) }}{{ ',' if not loop.last }}{% endfor %}
from {{ cte }} r
{% if is_incremental() %}
left anti join {{ this }} t on r.model_run_id=t.model_run_id and r.record_key=t.record_key
{% endif %}
{%- endmacro %}

{% macro explicit_projection(columns, alias='') -%}
{% for c in columns %}{{ alias ~ '.' if alias }}{{ adapter.quote(c) }}{{ ',' if not loop.last }}{% endfor %}
{%- endmacro %}

{% macro assert_case_vars() %}
 {% if execute %}
 {% for name in ['model_run_id','calculated_at','input_cutoff_at','rule_version'] %}
  {% if not var(name,none) %}{{ exceptions.raise_compiler_error('Missing immutable run variable: ' ~ name) }}{% endif %}
 {% endfor %}
 {% if var('business_timezone','Europe/Paris') != 'Europe/Paris' %}{{ exceptions.raise_compiler_error('Unsupported business timezone') }}{% endif %}
 {% if var('write_batch_count',1)|int < 1 or var('write_batch_index',0)|int < 0 or var('write_batch_index',0)|int >= var('write_batch_count',1)|int %}{{ exceptions.raise_compiler_error('Invalid technical write partition') }}{% endif %}
 {% endif %}
{% endmacro %}

{% macro case_threshold(stage_expr, type_expr) -%}
multiIf(
{% for selector, value in var('stagnation_thresholds', {}).items() %}
 ({{ type_expr }}={{ selector.split(':')[0]|int }} and {{ stage_expr }}={{ selector.split(':')[1]|int }}),
 CAST({{ ch_literal(value) }} AS Nullable(Float64)),
{% endfor %}
 true, CAST({{ ch_literal(var('default_stagnation_threshold_days',21)) }} AS Nullable(Float64)),
 CAST(NULL AS Nullable(Float64)))
{%- endmacro %}

{% macro duration_bin(expr) -%}
multiIf({{ expr }} is null,NULL,{{ expr }}<0,NULL,{{ expr }}<7,'[0,7)',{{ expr }}<14,'[7,14)',{{ expr }}<30,'[14,30)','[30,+inf)')
{%- endmacro %}

{% macro case_outcome(stage_expr) -%}
multiIf({{ stage_expr }} is null,NULL,
{% for category in ['open','won','lost','abandoned','unqualified'] %}
 {% set ids=var('outcome_stage_ids',{}).get(category,[]) %}
 {% if ids %}{{ stage_expr }} in ({{ ids|join(',') }}),{{ ch_literal(category) }},{% endif %}
{% endfor %}
'unknown')
{%- endmacro %}

{% test case_grain(model, key, run_scoped=false) %}
select {{ key }}, count() as nb_rows from {{ model }}
{% if run_scoped %}where model_run_id={{ ch_literal(var('test_model_run_id','')) }}{% endif %}
group by {{ key }} having count()>1 or {{ key }} is null
{% endtest %}
