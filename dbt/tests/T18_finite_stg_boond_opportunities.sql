{{ config(tags=['capture']) }}
select source_version_key from {{ ref('stg_boond_opportunities') }} where (src_estimated_amount_excluding_tax is not null and not isFinite(src_estimated_amount_excluding_tax)) or (src_weighted_amount_excluding_tax is not null and not isFinite(src_weighted_amount_excluding_tax)) or (src_exchange_rate is not null and not isFinite(src_exchange_rate))
