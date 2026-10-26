with quality as (select model_run_id,countIf(measure_id like 'revenue.%' and availability_status!='available')=0 as complete from dtr_sales.dataset_publication_status where dataset_family='company_mrr_month' group by model_run_id)
 select d.model_run_id,toString(toStartOfMonth(closing_date)) as mois,company_key,
 component.1 as composante,if(q.complete,component.2,NULL) as montant,
 if(q.complete,'Calculable','Indisponible : couverture incomplète') as disponibilite
 from dtr_sales.dataset_company_mrr_month d inner join quality q on d.model_run_id=q.model_run_id
 array join [('01 · Début',sum_mrr_begin),('02 · New',sum_new_mrr_new),('03 · Upsell',sum_new_mrr_upsell),('04 · Départs',-sum_departure_mrr),('05 · Baisses',-sum_contraction_mrr),('06 · Fin',sum_mrr_end)] as component