{{ config(tags=['capture']) }}
select source_version_key from {{ ref('stg_ref_stage_probabilities') }} where (src_probability is not null and not isFinite(src_probability))
