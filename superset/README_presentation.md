# Refonte visuelle Superset — 26 octobre 2026

Les trois dashboards locaux ont été repris à partir des maquettes :

- Synthèse : cartes objectif/réalisé regroupées, tunnel centré bleu–turquoise avec taux de passage, carte de conversion, bloc MRR/churn compact.
- Durées : bandeau de population, quatre KPI alignés, histogrammes terminés/en cours différenciés, axes sans chevauchement, canaux et tableaux agrandis.
- Cohortes : matrice avec barres empilées, six issues conservées, cellules non matures hachurées, évolution horizontale avec pourcentages, zoom par canal compact.

Typographie, espaces, bordures, couleurs, formats de dates et états vides harmonisés. Les tableaux détaillés restent consultables avec pagination ou défilement. Les segments trop petits portent leurs pourcentages au survol. La navigation et les filtres restent ceux de Superset.

Aucune correction de données, reconstruction dbt ou campagne de contrôle de qualité n’a été effectuée pendant cette refonte. Les expressions de présentation formatent les mesures existantes. Les valeurs manquantes restent indisponibles. La cascade sans montants affiche ses composantes sans inventer de barres.

La revue a porté sur le rendu effectif dans Superset : captures des trois dashboards, cartes sans coupure, tunnel et taux, matrice et légende, histogrammes, pagination et état vide du parcours. Les anciens résultats de tests de données concernent la livraison précédente et ne constituent pas une nouvelle validation de cette présentation.

## Reproduction

`build_dashboards.py` applique désormais automatiquement `style_dashboards.py` après la construction des objets. Pour réappliquer uniquement la présentation :

```powershell
docker exec use-case-analytics-engineer-superset-1 python /app/case-assets/style_dashboards.py
```

Export de métadonnées uniquement :

```powershell
docker exec use-case-analytics-engineer-superset-1 python /app/case-assets/export_dashboards.py
```

La configuration Superset fournie autorise les classes CSS sur les éléments de présentation ; la désinfection HTML reste activée, sans autoriser les scripts, gestionnaires d’événements ou styles inline. Conserver cette configuration lors d’une reproduction. Le lecteur ClickHouse est limité à deux threads par requête pour éviter les erreurs de chargement liées à la mémoire lors du rendu simultané des graphiques.

Les dashboards sont accessibles sur :
- http://localhost:8088/superset/dashboard/case-synthese/
- http://localhost:8088/superset/dashboard/case-durees/
- http://localhost:8088/superset/dashboard/case-cohortes/
