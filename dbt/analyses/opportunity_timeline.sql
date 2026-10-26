select model_run_id,tenant_id,opportunity_id,object_kind,object_key,started_at,ended_at,stage_label,event_type,
from_stage_id,to_stage_id,time_basis,is_left_censored,employee_display_name,team_name,slice_duration_days
from {{ ref('dataset_opportunity_timeline') }}
where opportunity_id={{ ch_literal(var('opportunity_id',0)) }}
order by started_at,object_kind,object_key
