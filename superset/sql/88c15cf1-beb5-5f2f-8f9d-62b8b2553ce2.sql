select publication_key,model_run_id,published_at,input_cutoff_at,
 toDateTime64('2026-09-30 22:00:00',3,'UTC') as borne_case,
 'Publication acceptée · couverture de case au 30 septembre 2026' as statut
 from dwh_common.int_publication