{{ config(tags=['capture']) }}
select source_version_key from {{ ref('stg_hubspot_deals') }} where (src_amount is not null and not isFinite(src_amount)) or (src_boond_opportunity_id is not null and not isFinite(src_boond_opportunity_id))
