"""Repair qualification in newly created development tables without deleting history."""
from runtime import *
c=client()
changes=c.query("SELECT database,table,name FROM system.columns WHERE (startsWith(database,'stg_') OR startsWith(database,'dtm_') OR startsWith(database,'dwh_') OR startsWith(database,'dtr_')) AND startsWith(name,'c.')").result_rows
events=[]
for db,table,col in changes:
    sql='ALTER TABLE `'+db+'`.`'+table+'` RENAME COLUMN `'+col+'` TO `'+col[2:]+'`'
    c.command(sql);events.append(sql)
atomic_json(STATE/'projection_column_migration.json',dict(at=now(),commands=events,reason='Explicit aliases required for qualified outer projection'))
print('Renamed',len(events),'columns; rows and revisions preserved')
