{{ config(tags=['capture']) }}
select source_version_key from {{ ref('stg_ref_sales_targets') }} where (src_target is not null and not isFinite(src_target))
