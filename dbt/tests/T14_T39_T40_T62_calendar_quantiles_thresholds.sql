{{ config(tags=['common']) }}
with times as (
 select toTimeZone(toDateTime64('2026-03-29 00:00:00.123',3,'Europe/Paris'),'UTC') as before_spring,
 toTimeZone(toDateTime64('2026-03-30 00:00:00.123',3,'Europe/Paris'),'UTC') as after_spring,
 toTimeZone(toDateTime64('2026-10-25 00:00:00.123',3,'Europe/Paris'),'UTC') as before_fall,
 toTimeZone(toDateTime64('2026-10-26 00:00:00.123',3,'Europe/Paris'),'UTC') as after_fall,
 toTimeZone(toDateTime64('2026-10-01 00:00:00',3,'Europe/Paris'),'UTC') as september_boundary
), quantiles as (
 select quantilesExactInclusive(0.5,0.9)(duration) as values
 from (select arrayJoin([10.,20.]) as duration)
), bins as (
 select arrayJoin([0.,6.999,7.,13.999,14.,29.999,30.]) as days,
 {{ duration_bin('days') }} as bin
)
select 'spring_elapsed_23_hours' as failure from times where dateDiff('millisecond',before_spring,after_spring)!=23*3600000
union all select 'fall_elapsed_25_hours' from times where dateDiff('millisecond',before_fall,after_fall)!=25*3600000
union all select 'case_closing_exclusive' from times where september_boundary!=toDateTime64('2026-09-30 22:00:00',3,'UTC')
union all select 'inclusive_quantiles' from quantiles where values!=[15.,19.]
union all select 'continuous_bins' from bins where (days=7 and bin!='[7,14)') or (days=14 and bin!='[14,30)') or (days=30 and bin!='[30,+inf)')
union all select 'strict_threshold' where (21.>21.) or not (21.000001>21.)
union all select 'calendar_horizon_DST' where toTimeZone(addDays(toDateTime64('2026-03-01 12:00:00',3,'Europe/Paris'),30),'UTC')!=toDateTime64('2026-03-31 10:00:00',3,'UTC')
union all select 'null_ratio' where (toFloat64(1)/nullIf(toFloat64(0),0)) is not null
union all select 'global_ratio' where abs((1.+9.)/(2.+10.)-10./12.)>0.000000001
union all select 'decimal_rounding' where round(toDecimal128('1.005',4),2)!=toDecimal128('1.01',2) or round(toDecimal128('-1.005',4),2)!=toDecimal128('-1.01',2)
