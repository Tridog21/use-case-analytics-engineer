{{ config(tags=['common','pipeline','revenue','dtr']) }}
select database,name from system.tables
where database in ('stg_boond','stg_hubspot','stg_reference','dwh_common','dwh_pipeline','dwh_revenue','dtm_common','dtm_pipeline','dtm_revenue','dtr_sales')
and create_table_query like '% TTL %'
