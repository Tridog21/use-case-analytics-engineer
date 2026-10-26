{{ config(tags=['capture']) }}
select source_identity_key,capture_key from {{ ref('stg_ref_sales_targets') }} group by source_identity_key,capture_key having count()>1
