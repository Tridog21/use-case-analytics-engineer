# Exécution manuelle du case v0.2

Depuis la racine du dépôt, utiliser le venv existant ; ne pas installer ou démarrer de service.

```powershell
.\dbt\.venv\Scripts\python.exe -X utf8 dbt/tools/static_audit.py
.\dbt\.venv\Scripts\python.exe -X utf8 dbt/tools/run_case.py --params dbt/config/manual_full.json
```

Le runner capture et réconcilie les quinze sources, fige le candidat, construit les treize modèles communs, les vingt-trois objets métier/faits et les dix DTR, puis exécute les fixtures et les tests. Il compare chaque recomposition persistée à ses clés et `row_hash` attendus. Il initialise le pointeur vide seulement si absent, crée les onze vues, contrôle les contrats physiques et les trente disponibilités, puis publie isolément. Aucun `dbt build` global ou `--full-refresh` ne fait partie de cette procédure.

`dbt/state/captures/` conserve les bornes, schémas, empreintes, commandes et captures complètes. `dbt/state/runs/<model_run_id>/` conserve les vars immuables, artefacts dbt, recompositions attendues, acceptation et lecture publiée. `dbt/state/fixtures/` contient uniquement les tests synthétiques dans des cibles analytiques suffixées. Les sources `raw`, `hubspot`, `ref` du case ne sont jamais modifiées.

Pour reprendre un candidat précis, créer un JSON contenant `phase` (`build`, `test` ou `publish`) et `resume_model_run_id` (SHA-256 du candidat). Une publication exige son manifeste d’acceptation, ses recompositions exactes et une qualité cohérente. Une simple relance avec les mêmes entrées réutilise le même run et ses timestamps. Les écritures sont sérialisées par `dbt/state/writer.lock` ; après un arrêt brutal du processus, vérifier que son PID n’existe plus avant de retirer ce seul fichier de verrou et relancer. Ne pas effacer les captures ou révisions.

Les rejets mémoire transitoires du serveur sont archivés. Le runner peut reprendre uniquement les modèles en erreur ou dépendances sautées, avec les mêmes vars ; leur présence partielle ne suffit pas à les accepter. Une divergence de contenu sous une même clé de run bloque la reprise.

Les dix fichiers `dbt/analyses/` et `config/dashboard_contracts.yml` définissent les requêtes des trois dashboards (Synthèse, Durées, Cohortes) et leurs consultations auxiliaires. Lire `dataset_publication_status` avant les agrégats. Vérifier `publication_key` avant et après les requêtes d’une page ; si la publication change, recharger ses résultats. Les faits montrent toutes les révisions ; les datasets montrent uniquement le pointeur accepté.

MRR signé, démos tenues et chaînage démo sans preuve restent NULL. Couverture/potentiel/BP/scénario/comparateur individuel restent non activés. EUR et la couverture de clôture du 30 septembre 2026 sont des hypothèses de case ; les lacunes individuelles restent explicites. Les stocks ne se somment pas entre mois ; les taux et quantiles se recalculent depuis leurs contributions après filtres. Les filtres équipe ne s’appliquent pas au portefeuille.

Les générateurs sont reproductibles : `tools/generate.py`, `tools/business.py`, `tools/reporting.py`, `tools/generate_tests.py`. Les SQL et YAML produits sont livrés explicitement ; le runner ne les régénère pas implicitement. La modification du code ou des règles entraîne un nouveau candidat, sans écraser les révisions précédentes.

Après trois rejets mémoire, les modèles persistés autorisent huit partitions techniques de record_key, sans tronquer les fenêtres métier. Le runner termine toutes les partitions du modèle avant ses descendants puis compare la recomposition totale. Les commandes natives échouées et les reçus de complétion orchestrée restent distincts.
