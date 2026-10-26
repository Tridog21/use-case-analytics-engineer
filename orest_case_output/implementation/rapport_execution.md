# Rapport d’exécution réel — spécification v0.2

Généré le 2026-10-25T22:57:28.677Z.

Publication acceptée : `8dc77da1cff3bfd498c1477c796f5c7b768c50bfa7fcce3b85b67a70c6cbf6fa`.
Clé de publication : `3eb9e7b9fd1d7c77d71db25ea96c59a7073ee1716e8c469e5c3abece2205223e` ; instant UTC : 2026-10-25 22:55:30.299000.

## Résultat

État du runner : **success**. 73 relations et leurs contrats physiques vérifiés ; 37 recompositions persistées comparées exactement aux clés et empreintes attendues. Quinze sources et 179 colonnes conservées. Les faits et datasets restent des vues ; les révisions persistées sont conservées.

## Commandes et résultats

| Phase | Résultats dbt réels | Durée (s) |
|---|---|---:|
| capture_tests | pass=51 | 4.93 |
| common | success=13 | 9.95 |
| business | success=23 | 62.93 |
| dtr | success=10 | 21.26 |
| unit_tests | pass=13 | 113.70 |
| candidate_tests | pass=232 | 33.85 |
| dataset_contracts | pass=1 | 1.78 |
| quality_candidate | pass=1 | 0.93 |
| publish | success=1 | 1.60 |
| published_tests | pass=1 | 1.03 |

Les essais en erreur et reprises mémoire antérieurs sont conservés dans les journaux et `history/`. Le succès final ne les efface pas. Les résultats du tableau consolident le dernier résultat natif de chaque nœud, y compris ses reprises. Après trois rejets mémoire, le runner peut écrire un modèle en huit partitions techniques de clé : les fenêtres métier restent complètes et la recomposition totale doit être identique avant publication. Les commandes natives échouées conservent leur exit code ; les reçus `*.completion.json` distinguent la réussite orchestrée. Une collision source contradictoire et une divergence de contenu ont volontairement provoqué des échecs dans les fixtures ; ce sont des contrôles négatifs attendus, distincts des tests du candidat.

## Recette isolée

- `dbt\state\fixtures\1792964305870925400\complete.json` : 12 assertions, statut success.
- `dbt\state\fixtures\1792965524266112200\complete.json` : 17 assertions, statut success.
- `dbt\state\fixtures\1792966064788707200\complete.json` : 17 assertions, statut success.
- `dbt\state\fixtures\1792966639167740000\complete.json` : 17 assertions, statut success.
- `dbt\state\fixtures\1792968109882690500\complete.json` : 17 assertions, statut success.
- Publication isolée `orest_case_output\implementation\publication_validation\cd7dd7146eaf\complete.json` : 8 assertions, 71 lectures concurrentes ; statut success.

Les fixtures couvrent premier chargement, cible vide, relecture, bornes inclusives, retards dans/hors fenêtre, suppressions, reprise source et dérivée partielle, collisions, A→B→A, disparition sur capture complète, révisions et contrôle de divergence. Les fixtures dbt couvrent aussi états anciens, populations 4/7, KAM/ES, canaux, signatures/réouvertures, première issue, transitions B avant A, maturité entière, changement d’heure, fin inclusive, zéro actif et équipe à entrée. Des erreurs SQL ont été injectées avant et après l’échange de publication ; le pointeur a été relu, la reprise idempotente et le retour à la publication précédente ont été vérifiés. Aucun arrêt brutal du système d’exploitation ni panne matérielle réelle n’est revendiqué.

## Disponibilité des mesures

| Mesure | Statut | Motif | Connues / attendues |
|---|---|---|---|
| objectives.mrr_signed | blocked_evidence | unconfirmed_amount_unit | None / 144 |
| objectives.pipeline_generated | blocked_evidence | unconfirmed_amount_unit | None / 144 |
| objectives.pipeline_weighted | blocked_evidence | unconfirmed_amount_unit | None / 144 |
| objectives.demos | blocked_evidence | missing_demo_completion_proof | None / 144 |
| funnel.opportunities | partial | incomplete_history | 3635 / 9158 |
| funnel.transition | partial | incomplete_history | 3430 / 9158 |
| funnel.global | partial | incomplete_history | 9077 / 9158 |
| revenue.active_mrr | partial | incomplete_history | None / None |
| revenue.new_mrr | partial | incomplete_history | None / None |
| revenue.churn_mrr | partial | incomplete_history | None / None |
| revenue.active_clients | partial | incomplete_history | None / None |
| durations.completed | partial | incomplete_history | 4331 / 5778 |
| durations.current_age | partial | incomplete_history | 1327 / 5778 |
| durations.threshold | partial | incomplete_history | 5671 / 5778 |
| cohorts.outcomes | partial | incomplete_history | 3113 / 3993 |
| pipeline.open_count | partial | incomplete_history | 9528 / 9728 |
| pipeline.open_amount | blocked_evidence | unconfirmed_amount_unit | None / 9728 |
| pipeline.weighted_amount | blocked_evidence | unconfirmed_amount_unit | None / 9728 |
| pipeline.coverage | blocked_definition | feature_not_activated | None / 9728 |
| pipeline.stagnation | partial | incomplete_history | 9109 / 9728 |
| pipeline.in_demo | partial | incomplete_history | 9697 / 9728 |
| events.generated_count | partial | incomplete_history | 1283 / 12437 |
| events.generated_amount | blocked_evidence | unconfirmed_amount_unit | None / 12437 |
| events.signed_count | partial | incomplete_history | 209 / 12437 |
| events.signed_mrr | blocked_evidence | unconfirmed_amount_unit | None / 12437 |
| events.cycle | partial | incomplete_history | 748 / 12437 |
| actions.requests | available |  | 8864 / 8864 |
| actions.realized_demos | blocked_evidence | missing_demo_completion_proof | None / 8864 |
| demo_intervals.duration | blocked_evidence | unproven_demo_intervals | None / 0 |
| timeline.detail | available |  | 37645 / 37645 |

Les démos réellement tenues, le MRR signé et les délais de démo sans preuve ne sont pas chiffrés. Couverture/potentiel/BP/scénario/comparateur individuel restent non activés. Une première acquisition sans preuve suffisante reste inconnue ; un entrant n’est pas automatiquement un nouveau client. EUR et la couverture jusqu’à `2026-09-30T22:00:00.000Z` sont des hypothèses de case D16/D20, avec lacunes individuelles conservées.

## Reproduction et reprise

Depuis la racine du dépôt :

```powershell
.\dbt\.venv\Scripts\python.exe -X utf8 dbt/tools/static_audit.py
.\dbt\.venv\Scripts\python.exe -X utf8 dbt/tools/run_case.py --params dbt/config/manual_full.json
```

Pour reprendre ce candidat, placer son identifiant ci-dessus dans un JSON avec `phase` et `resume_model_run_id`, puis fournir ce JSON à `--params`. Les manifests figent les timestamps, les captures complètes admises, les paramètres et les empreintes. Ne pas utiliser `--full-refresh`, effacer une capture ou modifier les sources du case.

## Preuves, limites et fichiers

Les commandes détaillées, exit codes, vars et artefacts sont dans `dbt/state/runs/8dc77da1cff3bfd498c1477c796f5c7b768c50bfa7fcce3b85b67a70c6cbf6fa/`. Les captures complètes sont dans `dbt/state/captures/`. Les contrats de requête des trois dashboards sont sous `dbt/analyses/` et `dbt/config/dashboard_contracts.yml`. Aucun service ni interface Superset n’a été installé ou démarré. Les modifications Git préexistantes ont été préservées.

Les adaptations et erreurs techniques rencontrées figurent dans `decisions_techniques.md`. Les performances observées sur ce petit jeu ne garantissent aucun comportement à gros volume. La complétude du code et la disponibilité des mesures sont deux vérifications distinctes.
