from runtime import *
c=client()
for name in ['int_subscription_periods','int_actions_prepared','int_opportunity_events']:
    schema='dwh_revenue' if name.startswith('int_subscription') else 'dwh_pipeline'
    print(name,c.query('select model_run_id,count() from '+schema+'.'+name+' group by model_run_id').result_rows)
print(c.query("select name,value from system.settings where name in ('max_threads','max_block_size','max_memory_usage')").result_rows)
print(c.query("SELECT event_time,read_rows,result_rows,memory_usage,exception_code,Settings['max_threads'],Settings['max_block_size'],substring(query,1,120) FROM system.query_log WHERE type IN ('ExceptionWhileProcessing','QueryFinish') AND query LIKE '%Immutable run content%' ORDER BY event_time DESC LIMIT 8").result_rows)
print(c.query("SELECT event_time,read_rows,written_rows,memory_usage,exception_code,substring(exception,1,180),substring(query,1,100) FROM system.query_log WHERE type='ExceptionWhileProcessing' AND exception_code=241 ORDER BY event_time DESC LIMIT 6").result_rows)
print('metrics',c.query("select metric,value from system.metrics where metric in ('MemoryTracking','MemoryTrackingUncorrected','BackgroundMergesAndMutationsPoolTask','Query','GlobalThread')").result_rows)
print('asynchronous',c.query("select metric,value from system.asynchronous_metrics where metric in ('MemoryResident','MemoryVirtual','MemoryTracked','UncompressedCacheBytes','MarkCacheBytes')").result_rows)
print('running',c.query('select elapsed,read_rows,memory_usage,substring(query,1,120) from system.processes').result_rows)
