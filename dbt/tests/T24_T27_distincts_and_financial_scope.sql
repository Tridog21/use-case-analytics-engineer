{{ config(tags=['pipeline','revenue','dtr']) }}
with dossiers as (
 select 'company_A' as company_key,1 as opportunity_id,'LA' as team
 union all select 'company_A',2,'SMB'
), measured as (
 select uniqExact(company_key) as nb_companies,count() as nb_opportunities from dossiers
)
select 'distinct_company_scope' as failure from measured where nb_companies!=1 or nb_opportunities!=2
union all
select 'financial_scope_has_team_or_sale_filter' from system.columns
where database='dtr_sales' and table='dtr_company_mrr_month' and name in ('team_key','sales_segment','sale_type_id')
having count()>0
