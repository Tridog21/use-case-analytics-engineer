{{ config(tags=['capture']) }}
select source_identity_key,capture_key from {{ ref('stg_hubspot_deals') }} group by source_identity_key,capture_key having count()>1
