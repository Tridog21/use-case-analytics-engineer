{{ config(tags=['common']) }}
select 'decimal_hash_scale' as failure
where {{ typed_hash('decimal_fixture',[{'name':'value','type':'Decimal(38,4)','expr':'toDecimal128(1,4)'}]) }}
!=lower(hex(SHA256(toJSONString(tuple('decimal_fixture',tuple('value','Decimal(38,4)','0','1.0000'))))))
