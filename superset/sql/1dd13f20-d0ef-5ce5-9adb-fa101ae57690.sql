{% set obs = filter_values('date_observation', remove_filter=True) %}
{% set obs = obs[0] if obs else '2026-09-30' %}
{% set thresholds = filter_values('seuil', remove_filter=True) %}
{% set threshold = thresholds[0] if thresholds else '21 jours' %}
with parameters as (select
 least(toTimeZone(toDateTime64(addDays(ifNull(toDateOrNull({{ [obs]|where_in }}),toDate('2026-09-30')),1),3,'Europe/Paris'),'UTC'),toDateTime64('2026-09-30 22:00:00',3,'UTC')) as observed,
 {% if threshold == 'Désactivé' %}CAST(NULL AS Nullable(Float64)){% else %}toNullable(toFloat64({{ threshold.split(' ')[0]|int }})){% endif %} as threshold)
, measured as (select model_run_id,visit_key,opportunity_id,concat('OPP-',toString(opportunity_id)) as dossier,
 ifNull(company_name,'Société inconnue') as societe,ifNull(stage_label,'Étape inconnue') as etape,if(sale_type_id=4,'Nouvelles ventes','Upsells') as type_vente,
 ifNull(entry_team_name,'Non attribuée') as equipe,ifNull(channel_label,'Inconnu') as canal,
 entered_at,exited_at,first_observed_at,observation_end_at,is_history_complete,p.observed,p.threshold,
 toDate(coalesce(entered_at,first_observed_at),'Europe/Paris') as date_entree_filtre,
 multiIf(entered_at is null,'Début inconnu',entered_at>=p.observed,'Futur',exited_at<p.observed,'Terminé',observation_end_at<p.observed,'Non observable','En cours') as population,
 if(population='Terminé',dateDiff('millisecond',entered_at,exited_at)/86400000.,NULL) as duree_terminee,
 if(population='En cours',dateDiff('millisecond',entered_at,p.observed)/86400000.,NULL) as anciennete
 from dtr_sales.dataset_stage_visits cross join parameters p where sale_type_id in (4,7) and first_observed_at<p.observed)
 select model_run_id,visit_key,opportunity_id,dossier,societe,etape,type_vente,equipe,canal,entered_at,exited_at,date_entree_filtre,population,
 duree_terminee,anciennete,multiIf(duree_terminee is null,NULL,duree_terminee<0,NULL,duree_terminee<7,'01 · [0,7) j',duree_terminee<14,'02 · [7,14) j',duree_terminee<30,'03 · [14,30) j','04 · [30,+∞) j') as classe_duree,multiIf(anciennete is null,NULL,anciennete<0,NULL,anciennete<7,'01 · [0,7) j',anciennete<14,'02 · [7,14) j',anciennete<30,'03 · [14,30) j','04 · [30,+∞) j') as classe_anciennete,
 if(threshold is null,NULL,anciennete>threshold) as au_dela_seuil,threshold,
 toString(toDate(observed-interval 1 millisecond,'Europe/Paris')) as date_observation,
 if(threshold is null,'Désactivé',concat(toString(toInt64(threshold)),' jours')) as seuil
 from measured