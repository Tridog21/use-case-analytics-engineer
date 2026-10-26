{{ config(tags=['common']) }}
with keys as (
 select
 {{ typed_hash('source_identity_v1:boond.companies',[{'name':'id','type':'Int64','expr':'toInt64(1)'}]) }} as company,
 {{ typed_hash('source_identity_v1:boond.actions',[{'name':'id','type':'Int64','expr':'toInt64(1)'}]) }} as action,
 {{ typed_hash('payload_v1',[{'name':'text','type':'Nullable(String)','expr':'CAST(NULL AS Nullable(String))'}]) }} as missing,
 {{ typed_hash('payload_v1',[{'name':'text','type':'Nullable(String)','expr':"CAST('' AS Nullable(String))"}]) }} as empty,
 {{ typed_hash('tuple_v1',[{'name':'a','type':'String','expr':"'a|b'"},{'name':'b','type':'String','expr':"'c'"}]) }} as first_tuple,
 {{ typed_hash('tuple_v1',[{'name':'a','type':'String','expr':"'a'"},{'name':'b','type':'String','expr':"'b|c'"}]) }} as second_tuple
)
select 'hash_serialization_collision' as failure from keys
where company=action or missing=empty or first_tuple=second_tuple or length(company)!=64
