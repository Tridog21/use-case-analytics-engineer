{{ config(tags=['capture']) }}
select source_identity_key,src_published_at from {{ ref('stg_boond_agencies') }} group by source_identity_key,src_published_at having uniqExact(source_payload_hash)>1
