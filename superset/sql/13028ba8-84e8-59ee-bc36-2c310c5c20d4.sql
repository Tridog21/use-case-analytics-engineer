{% set selected = filter_values('dossier',remove_filter=True) %}
{% set obs = filter_values('date_observation', remove_filter=True) %}
{% set obs = obs[0] if obs else '2026-09-30' %}
{% set thresholds = filter_values('seuil', remove_filter=True) %}
{% set threshold = thresholds[0] if thresholds else '21 jours' %}
with parameters as (select
 least(toTimeZone(toDateTime64(addDays(ifNull(toDateOrNull({{ [obs]|where_in }}),toDate('2026-09-30')),1),3,'Europe/Paris'),'UTC'),toDateTime64('2026-09-30 22:00:00',3,'UTC')) as observed,
 {% if threshold == 'Désactivé' %}CAST(NULL AS Nullable(Float64)){% else %}toNullable(toFloat64({{ threshold.split(' ')[0]|int }})){% endif %} as threshold)

 select model_run_id,concat('OPP-',toString(opportunity_id)) as dossier,ifNull(company_name,'Société inconnue') as societe,
 object_kind as objet,event_type as evenement,stage_label as etape,started_at as debut,if(ended_at<p.observed,ended_at,NULL) as fin,
 team_name as equipe,time_basis as preuve,is_left_censored as debut_inconnu,status_reason as limite,
 toString(toDate(p.observed-interval 1 millisecond,'Europe/Paris')) as date_observation
 from dtr_sales.dataset_opportunity_timeline cross join parameters p
 where started_at<p.observed and {% if selected %}concat('OPP-',toString(opportunity_id)) in {{ selected|where_in }}{% else %}false{% endif %}