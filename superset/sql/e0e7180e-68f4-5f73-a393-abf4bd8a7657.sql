select model_run_id,toString(month_date) as mois,source_segment as equipe_objectif,metric_code,
 metric_label,target_value,actual_value,attainment_rate,
 multiIf(status_reason='missing_team_mapping','Équipe ES non attribuée',metric_code='demos','Tenue des démos non prouvée','Unité du réalisé non prouvée') as disponibilite
 from dtr_sales.dataset_sales_objectives_month