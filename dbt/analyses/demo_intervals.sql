select model_run_id,demo_interval_key,demo_journey_id,company_name,started_at,ended_at,elapsed_duration_days,is_interval_calculable,status_reason
from {{ ref('dataset_demo_intervals') }}
