{% set obs = filter_values('date_observation', remove_filter=True) %}
{% set obs = obs[0] if obs else '2026-09-30' %}
{% set thresholds = filter_values('seuil', remove_filter=True) %}
{% set threshold = thresholds[0] if thresholds else '21 jours' %}
with parameters as (select
 least(toTimeZone(toDateTime64(addDays(ifNull(toDateOrNull({{ [obs]|where_in }}),toDate('2026-09-30')),1),3,'Europe/Paris'),'UTC'),toDateTime64('2026-09-30 22:00:00',3,'UTC')) as observed,
 {% if threshold == 'Désactivé' %}CAST(NULL AS Nullable(Float64)){% else %}toNullable(toFloat64({{ threshold.split(' ')[0]|int }})){% endif %} as threshold)

 select model_run_id,opportunity_key,opportunity_id,concat('OPP-',toString(opportunity_id)) as dossier,
 ifNull(company_name,'Société inconnue') as societe,toDate(created_at,'Europe/Paris') as date_creation,toString(cohort_month) as cohorte,
 if(sale_type_id=4,'Nouvelles ventes','Upsells') as type_vente,ifNull(team_name,'Non attribuée') as equipe,ifNull(channel_label,'Inconnu') as canal,
 horizon_days as horizon,concat('J+',toString(horizon_days)) as horizon_label,cohort_mature_at,horizon_at,
 cohort_mature_at<=p.observed as mature,
 if(cohort_mature_at<=p.observed,ifNull(issue_at_horizon,'unknown'),NULL) as issue,
 if(cohort_mature_at<=p.observed,is_observable,NULL) as observable,
 multiIf(cohort_mature_at>p.observed,'Non mature',issue_at_horizon='open','Ouvert',issue_at_horizon='won','Gagné',issue_at_horizon='lost','Perdu',issue_at_horizon='abandoned','Abandonné',issue_at_horizon='unqualified','Non qualifié','Inconnu') as issue_libelle,
 p.observed,toString(toDate(p.observed-interval 1 millisecond,'Europe/Paris')) as date_observation
 from dtr_sales.dataset_cohort_outcomes cross join parameters p where sale_type_id in (4,7) and created_at<p.observed