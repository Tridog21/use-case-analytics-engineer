{{ config(tags=['capture']) }}
select source_identity_key,src_published_at from {{ ref('stg_boond_projects') }} group by source_identity_key,src_published_at having uniqExact(source_payload_hash)>1
