# Superset local : installation, utilisation et reproduction

Cette extension ajoute Superset au projet fourni sans modifier les modèles dbt.
Elle est destinée au développement et à la démonstration locale. Aucun service
n’est publié sur Internet. Le port Superset est lié à `127.0.0.1`.

## Prérequis

- Docker Desktop démarré, moteur Linux prêt (WSL 2 sur Windows).
- Git pour cloner le dépôt et les fichiers `seed/` fournis dans ce case.
- PowerShell 5.1 ou supérieur pour les scripts Windows.
- Internet au premier lancement pour télécharger et construire les images.
- Ports 8088, 8123 et 9000 disponibles. Prévoir plusieurs Go de disque pour Docker.

## Démarrer sur Windows

Depuis la racine du véritable projet (double niveau de dossiers) :

```powershell
cd C:\Users\orest\Desktop\use-case-analytics-engineer\use-case-analytics-engineer
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\start-superset.ps1
```

Sur une autre machine : cloner le dépôt privé autorisé, se placer dans sa racine
et lancer la même commande de script. Aucun Python local n’est nécessaire à
Superset. Le premier lancement est plus long (téléchargement, construction,
migrations). Les lancements suivants réutilisent les images et les volumes.

Le script génère une seule fois `.env.superset`, exclu de Git, avec des secrets
propres à cette machine. Ne pas supprimer ce fichier : sa clé chiffre les
connexions conservées par Superset, et les mots de passe correspondent aux volumes.

Ouvrir **http://localhost:8088**, identifiant **admin**. Pour lire le mot de passe
local, ouvrir `.env.superset` dans l’éditeur et lire `SUPERSET_ADMIN_PASSWORD`.
Ne pas copier ce fichier dans les livrables ou les échanges avec l’IA.

## Ce que le démarrage prépare

1. ClickHouse et le chargement des seeds prévus par le dépôt, si son volume est vide.
2. PostgreSQL pour les métadonnées Superset, dans un volume distinct.
3. Les migrations et les rôles Superset, puis le compte administrateur.
4. Le schéma `analytics` s’il n’existe pas encore ; aucune table métier n’est créée.
5. Un utilisateur ClickHouse `superset_reader`, avec `SELECT` sur `analytics`,
   `raw`, `hubspot` et `ref`, et `readonly = 1`.
6. Une connexion Superset **ClickHouse - case**, utilisant le nom de service Docker
   `clickhouse:8123`, et non `localhost` à l’intérieur du conteneur.

Les trois dashboards métier sont maintenant livrés : **Synthèse, Durées et Cohortes**.
Ils interrogent les vues publiées dans `dtr_sales` et le pointeur `dwh_common.int_publication`.
Le lecteur dispose des droits SELECT correspondants. Les modèles dbt doivent être construits
et leur publication acceptée avant la génération des dashboards. Le démarrage seul ne relance pas dbt.
Voir [les assets et la reproduction](../superset/README.md).

## Travailler dans l’interface

1. **SQL > SQL Lab** : choisir `ClickHouse - case`, puis un schéma et exécuter
   une requête (par exemple `SELECT 1 AS connection_ok`).
2. **Data > Datasets** : ajouter une table existante depuis cette connexion.
3. **Charts > + Chart** : choisir le dataset, le type, les métriques et les filtres.
4. Enregistrer le graphique, puis l’ajouter à un dashboard.
5. Les transformations restent dans dbt ; relancer dbt après une modification de modèle.
   Rafraîchir le dashboard pour consulter les résultats actualisés (sous réserve du cache).

## Conservation et partage du dashboard

Les graphiques, dashboards et comptes sont conservés dans `superset-metadata`.
Les données ClickHouse restent dans le volume existant `clickhouse-data`.
Un arrêt ou redémarrage ne supprime pas ces volumes.

Git ne contient pas les volumes Docker. Avant la restitution : exporter le dashboard,
retirer les secrets, conserver les assets et automatiser un import utilisant la
connexion locale. Voir [superset/README.md](../superset/README.md).
Ne pas copier un volume local ou `.env.superset` dans Git.

Cette configuration ne crée ni lien Cloudflare ni accès anonyme. Un recruteur
qui lance le projet sur sa machine utilise son propre `localhost:8088`.

## Vérifier et diagnostiquer

```powershell
docker compose --env-file .env.superset -f docker-compose.yml -f docker-compose.superset.yml ps -a
docker compose --env-file .env.superset -f docker-compose.yml -f docker-compose.superset.yml logs --tail 80 superset-init superset
Invoke-WebRequest http://localhost:8088/health -UseBasicParsing
# Contrôle d’intégration (authentification, connexion, compte en lecture seule, 15 tables)
docker compose --env-file .env.superset -f docker-compose.yml -f docker-compose.superset.yml exec -T superset python /app/case/verify.py
```

Résultats attendus : `clickhouse`, `superset-db` et `superset` healthy ;
`superset-init` terminé avec code 0 ; `/health` répond HTTP 200.

Éviter de publier les logs complets s’ils contiennent des requêtes ou des données.
Ne pas exécuter `docker compose config` dans un partage d’écran : cette commande
peut afficher les variables secrètes résolues.

## Arrêter et reprendre

```powershell
# Arrêter Superset et ses métadonnées ; conserver ClickHouse actif
.\scripts\stop-superset.ps1

# Arrêter aussi ClickHouse
.\scripts\stop-superset.ps1 -IncludeClickHouse

# Reprendre
.\scripts\start-superset.ps1
```

Si PowerShell bloque un script, utiliser la forme `powershell -NoProfile
-ExecutionPolicy Bypass -File ...` pour cette exécution uniquement.
Ne jamais utiliser `docker compose down -v` pour un arrêt ordinaire.

## Versions et périmètre

- Apache Superset 6.1.0 (image épinglée par digest dans le Dockerfile).
- clickhouse-connect 1.8.0 et psycopg2-binary 2.9.10 (versions fixées).
- PostgreSQL 16 Alpine (image épinglée par digest dans le fichier Compose).
- ClickHouse et dépendances dbt : versions fournies par le dépôt, inchangées.

Les dépendances ajoutées sont fixées dans `docker/superset/requirements.txt`,
les autres proviennent de l’image de base épinglée. Les scripts sont Windows ; Compose peut être
utilisé sur Linux/macOS avec un fichier d’environnement généré localement et
les mêmes paramètres `-f` / `--env-file`.

## Références

- [Superset : images Docker](https://superset.apache.org/admin-docs/installation/docker-builds/)
- [Superset : connexion ClickHouse](https://superset.apache.org/user-docs/databases/supported/clickhouse/)
