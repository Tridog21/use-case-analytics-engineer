{% set obs = filter_values('date_observation', remove_filter=True) %}
{% set obs = obs[0] if obs else '2026-09-30' %}
{% set thresholds = filter_values('seuil', remove_filter=True) %}
{% set threshold = thresholds[0] if thresholds else '21 jours' %}
with parameters as (select
 least(toTimeZone(toDateTime64(addDays(ifNull(toDateOrNull({{ [obs]|where_in }}),toDate('2026-09-30')),1),3,'Europe/Paris'),'UTC'),toDateTime64('2026-09-30 22:00:00',3,'UTC')) as observed,
 {% if threshold == 'Désactivé' %}CAST(NULL AS Nullable(Float64)){% else %}toNullable(toFloat64({{ threshold.split(' ')[0]|int }})){% endif %} as threshold)
, detail as (select model_run_id,opportunity_key,opportunity_id,toString(cohort_month) as cohorte,
 if(sale_type_id=4,'Nouvelles ventes','Upsells') as type_vente,ifNull(team_name,'Non attribuée') as equipe,ifNull(channel_label,'Inconnu') as canal,
 concat(leftPad(toString(funnel_position),2,'0'),' · ',multiIf(target_stage_id=0,'Création',target_stage_id=22,'Qualification',target_stage_id=23,'Découverte',target_stage_id=24,'Démo',target_stage_id=21,'Proposition',target_stage_id=28,'Closing',target_stage_id=1,'Signé',concat('État ',toString(target_stage_id)))) as etape,
 funnel_position,target_stage_id,first_reached_observed_at,previous_stage_first_reached_at,transition_reached_at,created_at,is_history_complete,p.observed
 from dtr_sales.dataset_funnel_progress cross join parameters p where sale_type_id in (4,7))
 select model_run_id,opportunity_key,opportunity_id,cohorte,type_vente,equipe,canal,etape,funnel_position,target_stage_id,
 first_reached_observed_at is not null and first_reached_observed_at<observed as atteint,
 previous_stage_first_reached_at is not null and previous_stage_first_reached_at<observed as base_transition,
 transition_reached_at is not null and transition_reached_at<observed as converti,
 is_history_complete,observed,toString(toDate(observed-interval 1 millisecond,'Europe/Paris')) as date_observation
 from detail where created_at<observed