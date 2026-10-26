# Branchement des dashboards — publication locale active

Publication du 25 octobre 2026 à 22:55:30 UTC. Les onze vues sont déployées et interrogables sur la connexion ClickHouse locale du case.

- Serveur depuis Windows : `localhost`, port HTTP `8123`.
- Schéma des datasets : `dtr_sales`.
- Pointeur accepté : `dwh_common.int_publication` (une ligne).
- Statuts des mesures : `dtr_sales.dataset_publication_status` (30 lignes).
- Run publié : `8dc77da1cff3bfd498c1477c796f5c7b768c50bfa7fcce3b85b67a70c6cbf6fa`.

Réutiliser la connexion ClickHouse du case dans l’outil BI. L’adresse ci-dessus décrit l’accès depuis Windows ; un outil BI exécuté dans un conteneur doit utiliser l’adresse ClickHouse de son réseau existant.

## Datasets à enregistrer

Toutes les relations ci-dessous se trouvent dans `dtr_sales`.

| Dashboard | Datasets | Requêtes de référence dans `dbt/analyses/` |
|---|---|---|
| Synthèse | `dataset_sales_objectives_month`, `dataset_funnel_progress`, `dataset_company_mrr_month` | `objective_attainment.sql`, `funnel_progress.sql`, `portfolio_month.sql` |
| Durées | `dataset_stage_visits`, `dataset_opportunity_timeline` | `stage_durations.sql`, `opportunity_timeline.sql` |
| Cohortes | `dataset_cohort_outcomes`, `dataset_opportunity_timeline` | `cohort_outcomes.sql`, `opportunity_timeline.sql` |
| Consultations auxiliaires | `dataset_pipeline_periods`, `dataset_sales_events`, `dataset_sales_actions`, `dataset_demo_intervals` | Les quatre analyses correspondantes |
| Disponibilité commune | `dataset_publication_status` | Lire le statut et le motif de chaque mesure avant l’affichage |

Les vues sélectionnent automatiquement le run accepté. Aucun paramètre BI `model_run_id` n’est nécessaire. Les fichiers d’analyse sont des modèles Jinja dbt ; les SQL exécutés sont disponibles dans `dbt/target/compiled/use_case/analyses/`.

## Contrôles réellement exécutés

- Contrats physiques des 73 relations vérifiés.
- Intégrité des 37 modèles persistés confirmée avant la reprise ciblée.
- JSON de qualité validé avant publication.
- Les dix datasets métier ont été comparés intégralement aux DTR du run accepté après publication.
- Le pointeur monoligne, les onze vues et les trente mesures de statut ont été vérifiés.
- Les dix requêtes de consultation ont réussi sur la publication active. La requête de timeline attend une clé d’opportunité ; son résultat sans sélection est vide. Les intervalles de démo sans preuve sont également vides et explicitement indisponibles.

Les suites métier précédemment acceptées n’ont pas été relancées pendant ce déploiement. Un test de grain isolé a complété la preuve native d’une reprise mémoire ; l’unicité était déjà contrôlée par les recompositions et la comparaison d’intégrité.

## Règles de lecture

La couverture de case s’arrête à la borne exclusive `2026-09-30T22:00:00.000Z`, soit le 1er octobre à minuit en Europe/Paris. Consulter les disponibilités avant d’interpréter une absence comme zéro. Le MRR signé, les démos réellement tenues et le chaînage de démo non prouvé restent indisponibles. Les totaux globaux du portefeuille sont NULL lorsque la couverture société est incomplète ; les contributions détaillées restent consultables.

Les stocks ne s’additionnent pas entre mois. Les taux et quantiles se recalculent depuis leurs contributions. Les filtres d’équipe ne s’appliquent pas au portefeuille global. Le contrat complet figure dans `dbt/config/dashboard_contracts.yml`.

Lire la clé de publication avant et après les requêtes d’une page ; recharger la page si elle change :

```sql
SELECT publication_key, model_run_id, published_at
FROM dwh_common.int_publication;

SELECT measure_id, availability_status, availability_reason,
       nb_expected, nb_known, data_coverage_end_at
FROM dtr_sales.dataset_publication_status
ORDER BY measure_id;
```

Les rejets mémoire du serveur local rencontrés pendant les essais sont conservés dans le rapport. La reprise finale a utilisé `--no-populate-cache` pour éviter le chargement anticipé des métadonnées par dbt. Les lectures finales ont réussi ; aucun plafond mémoire serveur n’a été changé.
