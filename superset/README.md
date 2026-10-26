> Présentation actualisée le 26 octobre : voir [la refonte visuelle](README_presentation.md). Le générateur applique automatiquement les styles. Les vérifications chiffrées ci-dessous sont historiques.

# Dashboards Superset livrés — 26 octobre 2026

Les trois dashboards sont publiés dans Superset local et branchés aux datasets publiés :

- Synthèse : http://localhost:8088/superset/dashboard/case-synthese/
- Durées : http://localhost:8088/superset/dashboard/case-durees/
- Cohortes : http://localhost:8088/superset/dashboard/case-cohortes/

21 datasets enregistrés (11 vues publiées et 10 datasets de présentation), 38 graphiques/cartes/tableaux. Filtres natifs, onglets du tunnel et navigation entre dashboards. Accès avec le compte Superset local existant ; aucun accès anonyme ajouté.

Les maquettes guident la disposition, les couleurs et les blocs. La spécification v0.2 guide les calculs et les indisponibilités. Le tunnel utilise des barres ordonnées pour conserver les étapes même si leurs effectifs ne décroissent pas. La cascade MRR affiche les composantes indisponibles en tableau, sans inventer de montants. Les parcours détaillés sont des tableaux chronologiques. Les indicateurs sans preuve suffisante restent indisponibles.

## Reproduction

Après démarrage de Superset et publication des modèles dbt :

```powershell
docker exec use-case-analytics-engineer-superset-1 python /app/case-assets/build_dashboards.py
```

Le générateur met à jour les mêmes objets grâce à des UUID stables. Il utilise la connexion locale `ClickHouse - case`. Le lecteur doit avoir SELECT sur `dtr_sales.*` et `dwh_common.int_publication` ; ces droits sont intégrés au bootstrap. La configuration active les templates SQL nécessaires aux filtres d’observation.

L’export natif `exports/dashboards_superset.zip` contient les dashboards et leurs dépendances. Les secrets de connexion sont retirés ; sur une autre installation, utiliser les identifiants locaux lors de l’import. La génération sur la connexion existante est la méthode privilégiée.

## Résultats déjà obtenus

Avant la demande d’arrêt des contrôles : 38/38 requêtes de graphiques et 25/25 contrôles ciblés réussis. Résultats réels conservés dans `validation_results.json` et `interaction_results.json`. La comparaison des quantiles avec ClickHouse natif a réussi ; l’écriture équivalente utilisée contourne une limite du parseur SQL de Superset.

Vérifications visuelles effectuées : affichage des trois dashboards, onglets du tunnel, ordre chronologique de la matrice, passage de juin à août avec masquage des taux non matures et maintien de la matrice comparative. Aucun contrôle supplémentaire de données après la demande utilisateur « check pas les données j'ai juste besoin des dash ».
