{{ config(materialized='table',schema='dwh_common',engine='MergeTree()',order_by='tuple()',tags=['publication']) }}
select
CAST(ifNull({{ ch_literal(var('publication_model_run_id','')) }},'') AS String) AS model_run_id,
CAST(lower(hex(SHA256(toJSONString(materialize(tuple('publication_v1',tuple('model_run_id','String',if(isNull(model_run_id),'1','0'),ifNull(toString(model_run_id),'')),tuple('published_at','DateTime64(3,\'UTC\')',if(isNull(published_at),'1','0'),ifNull(toString(toUnixTimestamp64Milli(published_at)),'')))))))) AS String) AS publication_key,
CAST({{ utc_var('publication_at') }} AS DateTime64(3,'UTC')) AS published_at,
CAST({{ utc_var('input_cutoff_at') }} AS DateTime64(3,'UTC')) AS input_cutoff_at,
CAST({{ ch_literal(var('rule_version','parse_only')) }} AS String) AS rule_version,
CAST({{ ch_literal(var('publication_quality_json','[]')) }} AS String) AS quality_json
{% if var('publication_model_run_id',none) is none %}where false{% endif %}
