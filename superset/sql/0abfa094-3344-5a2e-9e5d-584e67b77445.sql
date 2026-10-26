with quality as (select model_run_id,countIf(measure_id like 'revenue.%' and availability_status!='available')=0 as complete from dtr_sales.dataset_publication_status where dataset_family='company_mrr_month' group by model_run_id)
 select d.model_run_id,toString(toStartOfMonth(closing_date)) as mois,closing_date,company_key,company_name,
 if(q.complete,sum_mrr_begin,NULL) as mrr_debut,if(q.complete,sum_mrr_end,NULL) as mrr_fin,
 if(q.complete,sum_new_mrr_new,NULL) as new_mrr,if(q.complete,sum_new_mrr_upsell,NULL) as upsell_mrr,
 if(q.complete,sum_departure_mrr,NULL) as depart_mrr,if(q.complete,sum_contraction_mrr,NULL) as baisse_mrr,
 if(q.complete,sum_churn_mrr,NULL) as churn_mrr,if(q.complete,is_departure,NULL) as depart_client,
 if(q.complete,is_contraction,NULL) as baisse_client,if(q.complete,is_active_begin,NULL) as client_debut,
 if(q.complete,is_active_end,NULL) as client_fin,
 if(q.complete,'Complète','Incomplète : historique société non résolu') as couverture
 from dtr_sales.dataset_company_mrr_month d inner join quality q on d.model_run_id=q.model_run_id