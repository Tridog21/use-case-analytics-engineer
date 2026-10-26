{{ config(tags=['capture']) }}
select source_version_key from {{ ref('stg_boond_deliveries') }} where (src_average_daily_price_excluding_tax is not null and not isFinite(src_average_daily_price_excluding_tax))
