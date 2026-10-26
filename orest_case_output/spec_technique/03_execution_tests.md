# Exécution, contrôles et critères d’acceptation

Spécification v0.2 finalisée le25octobre2026 sous délégation utilisateur ; arbitrages D16–D30 dans01§7. Ce document distingue les contrôles de lecture effectivement réalisés dans ce nouveau chat et les tests/commandes à exécuter lors de l’implémentation. Les modèles dbt ne sont pas implémentés à ce stade. Les décisions transversales et les grains de référence sont définis dans la [spécification](01_specification_technique.md) et le [catalogue](02_catalogue_modeles.md).

## 1. État vérifié et limites de l’audit

### 1.1 Périmètre exécuté

Les inspections de ce chat ont utilisé les fichiers présents et le ClickHouse local déjà démarré, avec des requêtes `SELECT`, `readonly=1`, `max_execution_time=15` et, pour le client HTTP, `max_result_rows=5000`. Les agrégations ont couvert les petites tables du case en entier ; les résultats ont été limités aux agrégats et métadonnées utiles. Aucune donnée nominative de personne n’est nécessaire aux preuves ci-dessous.

Aucune installation, aucun démarrage de service, aucune modification de source et aucun modèle n’ont été exécutés. Aucun `dbt debug`, `dbt run`, `dbt build`, `dbt test`, snapshot ou benchmark de modèles n’a été lancé. Les contrôles SQL décrits comme exécutés ne sont pas des tests dbt déjà construits.

Les versions réellement présentes ont été vérifiées par `importlib.metadata` dans `dbt/.venv`, séparément des déclarations de `pyproject.toml` et `uv.lock` :

| Élément | Déclaré/documentaire | Réellement vérifié |
| --- | --- | --- |
| Python | `>=3.11,<3.14` | 3.12.12 dans `dbt/.venv` |
| dbt-core | 1.11.12 | 1.11.12 installé |
| dbt-clickhouse | 1.10.1 | 1.10.1 installé |
| ClickHouse | Image `clickhouse/clickhouse-server:25.11` | Serveur 25.11.9.34 |
| Fuseau | Aucun fuseau explicite dans les types source | Serveur UTC ; types `DateTime64(3)` sans fuseau explicite |
| Projet dbt | Canevas du dépôt | `dbt/models/.gitkeep` uniquement ; aucun modèle métier |
| Sources | 15 tables documentées | Les 15 existent, moteur `MergeTree` |
| Bases | `raw`, `hubspot`, `ref`, profil `analytics` | Les quatre bases existent et sont de moteur `Atomic` |

La décision utilisateur fixe **Europe/Paris** pour les clôtures. Le fuseau serveur UTC n’est pas une décision de reporting. Les conversions doivent donc être explicites.

### 1.2 Précautions liées à l’adaptateur installé

Le code installé de dbt-clickhouse a été lu, sans ouverture de connexion dbt :

- `dbt/adapters/clickhouse/dbclient.py`, méthode `_run_exchange_test` : avec `check_exchange=True` par défaut, l’ouverture peut créer deux tables `__dbt_exchange_test_*`, exécuter un échange puis les supprimer. **`dbt debug` ne constitue pas un contrôle strictement en lecture seule dans cet environnement.**
- `credentials.py` et `relation.py` : le `schema` dbt désigne une base ClickHouse ; `database` doit être omis ou identique au schéma, puis n’est pas rendu comme un niveau supplémentaire de qualification.
- `impl.py`, `calculate_incremental_strategy` et `validate_incremental_strategy` : stratégies reconnues `legacy`, `append`, `delete_insert`, `insert_overwrite`, `microbatch`. Le profil ne demande pas `use_lw_deletes`, dont la valeur par défaut est `False` ; une stratégie implicite devient donc `legacy`.
- La stratégie `legacy` reconstruit une relation de remplacement, copie les anciennes lignes dont la clé n’est pas reprise, insère les nouvelles puis remplace la cible. Ce comportement ne déduplique pas arbitrairement plusieurs entrées de même clé dans le lot entrant : la requête du modèle doit traiter les répétitions exactes et détecter les collisions.
- `delete_insert` supprime avant d’insérer ; `append` ajoute sans garantir l’unicité ; `insert_overwrite` exige un partitionnement et refuse `unique_key`. Aucun de ces comportements n’a été validé par une écriture dans ce chat.
- `dbt/include/clickhouse/macros/materializations/unit.sql` fournit une matérialisation de tests unitaires. Elle crée une table temporaire interne pour déterminer les types. Sa présence établit un support dans le code installé ; l’exécution des fixtures du case reste à valider lors de l’implémentation, dans une cible de test.

Un second audit statique a confirmé les points suivants dans `dbt/include/clickhouse/macros/materializations/snapshot.sql` de la version installée : lignes 117/232, filtre littéral `dbt_valid_to is null` et noms de métadonnées codés dans les overrides ; clé `strategy.unique_key` interpolée comme expression ; branches de suppression pilotées par `invalidate_hard_deletes`, sans branche spécifique `hard_deletes=new_record` dans ce fichier. La ligne 30 crée une relation `__snapshot_upsert` avec `IF NOT EXISTS`, sans nettoyage initial dans cette macro : un résidu après échec constitue un cas de reprise à tester. La macro d’horodatage de l’adaptateur retourne `now()` à la seconde. Le hash snapshot transforme aussi NULL en chaîne vide avant concaténation ; notre sérialisation canonique distingue explicitement ces valeurs.

Ces constats de code motivent le choix conservateur de captures append explicites pour maîtriser clés, précision, présence et reprise. Ils ne démontrent pas une panne exécutée ni une impossibilité générale d’utiliser les snapshots : une telle solution demanderait une validation dédiée des options retenues. Aucune commande snapshot n’a été exécutée.

Autre point confirmé dans `incremental.sql` : `inserts_only=true` ou l’absence de `unique_key` peut prendre la branche d’insertion directe avant le contrôle de `on_schema_change`. Pour la configuration append du case, renseigner la clé de version (`source_version_key` en staging, `record_version_key` pour les recompositions), ne pas activer `inserts_only`, et garder l’anti-jointure explicite. Le runner contrôle aussi le schéma source complet avant extraction : un nouveau champ source non projeté ne serait pas détecté par la seule comparaison du schéma SQL compilé avec la cible.

Les tables temporaires internes créées par dbt ne sont pas des tables temporaires écrites manuellement dans les modèles. Les modèles du case restent une requête `SELECT` avec CTE/Jinja, conformément aux conventions.

## 2. Résultats des contrôles source exécutés

### 2.1 Schémas, colonnes et clés

Le DDL, `model.json` et les colonnes live concordent : **179 colonnes physiques**, alors que l’inventaire préparatoire en sélectionne 159. Le staging 1 pour 1 doit conserver les 179. La présence d’une colonne ne prouve ni sa complétude métier ni la fiabilité d’un calcul qui l’utilise.

| Source | Colonnes | Lignes/versions | Identités distinctes | Versions `meta.deleted=true` | Groupes de clé de version répétés |
| --- | ---: | ---: | ---: | ---: | ---: |
| `raw.opportunities` | 25 | 7 020 | 1 390 | 14 | 0 |
| `raw.actions` | 16 | 8 980 | 8 864 | 55 | 0 |
| `raw.companies` | 14 | 1 464 | 1 300 | 0 | 0 |
| `raw.contacts` | 14 | 2 391 | 2 391 | 0 | 0 |
| `raw.ressources` | 12 | 22 | 20 | 0 | 0 |
| `raw.businessunits` | 8 | 9 | 3 | 0 | 0 |
| `raw.agencies` | 7 | 2 | 2 | 0 | 0 |
| `raw.poles` | 7 | 6 | 6 | 0 | 0 |
| `raw.dictionaries` | 12 | 6 | 2 couples tenant/langue | 0 | 0 |
| `raw.projects` | 13 | 171 | 171 | 0 | 0 |
| `raw.deliveries` | 13 | 326 | 214 | 0 | 0 |
| `hubspot.contacts` | 15 | 2 254 | 2 254 id | Sans CDC raw | 0 id répété |
| `hubspot.deals` | 16 | 1 190 | 1 190 id | Sans CDC raw | 0 id répété |
| `ref.sales_targets` | 4 | 144 | 144 mois/segment/indicateur | Sans CDC raw | 0 clé répétée |
| `ref.stage_probabilities` | 3 | 33 | 33 état/segment | Sans CDC raw | 0 clé répétée |

Pour les objets raw avec id, la clé testée est `(meta.customer,id,meta.ts)`. Pour les dictionnaires, elle est `(meta.customer,meta.language,meta.ts)`. Un contrôle complémentaire des contenus complets énumérés n’a trouvé aucun conflit sous ces clés. Un seul tenant est observé ; il reste une composante obligatoire des clés et jointures.

### 2.2 Couverture historique

| Source raw | Premier `meta.ts` | Dernier `meta.ts` |
| --- | --- | --- |
| opportunities | 12/06/2023 02:23:16.391 | 30/09/2026 21:33:28.935 |
| actions | 12/06/2023 02:02:12.076 | 30/09/2026 16:14:38.000 |
| companies | 12/06/2023 02:04:31.197 | 24/09/2026 13:46:44.097 |
| contacts | 12/06/2023 02:05:33.444 | 30/09/2026 18:23:13.368 |
| ressources | 12/06/2023 02:22:38.525 | 02/03/2026 10:00:00.000 |
| businessunits | 12/06/2023 14:29:57.079 | 18/03/2026 10:00:00.000 |
| agencies | 12/06/2023 04:44:06.453 | 14/06/2023 21:14:23.069 |
| poles | 12/06/2023 05:30:24.363 | 14/06/2023 21:39:12.644 |
| dictionaries | 12/06/2023 03:00:00.000 | 08/12/2025 10:00:00.000 |
| projects | 12/06/2023 04:06:34.454 | 23/08/2026 18:40:40.089 |
| deliveries | 12/06/2023 05:19:47.375 | 29/09/2026 22:00:00.000 |

Horaires ci-dessus dans le contexte UTC du serveur. Ces maximums sont des dernières publications présentes, pas une preuve qu’une ingestion exhaustive a réussi jusqu’à cette date. Une table de référence stable peut légitimement n’avoir aucun changement récent. La cadence et la fraîcheur attendues restent à décider ; on ne peut pas diagnostiquer une panne d’un jeu de case statique à partir de la date du jour.

Les dates métier peuvent précéder les premières publications CDC :

| Champ | Minimum | Maximum | Valeurs NULL |
| --- | --- | --- | ---: |
| Opportunité, création | 06/09/2021 | 28/09/2026 | 0 / 7 020 versions |
| Opportunité, closing | 08/09/2023 | 01/12/2026 | 6 388 / 7 020 |
| Opportunité, startDate et answerDate | Absents | Absents | 7 020 / 7 020 chacun |
| Action, création et début agenda | 30/09/2021 | 30/09/2026 | 0 / 8 980 chacun |
| Projet, début | 01/12/2021 | 01/09/2026 | 0 / 171 |
| Projet, fin | Absente | Absente | 171 / 171 |
| Livraison, début | 01/12/2021 | 01/09/2026 12:11:15.039 | 0 / 326 |
| Livraison, fin | 27/12/2022 | 31/12/2099 | 273 / 326 |
| HubSpot contact, création | 02/08/2024 | 29/09/2026 | 0 / 2 254 |
| HubSpot contact, première conversion | 02/08/2024 | 28/09/2026 | 1 578 / 2 254 |
| HubSpot deal, création | 01/08/2025 | 28/09/2026 | 0 / 1 190 |
| HubSpot deal, clôture | 01/08/2025 | 30/09/2026 | 669 / 1 190 |

Sur 1 390 opportunités, 106 ont un premier état observé autre que Lead ; 107 ont une création antérieure au premier `meta.ts` (dont un Lead). Dix-sept dossiers ont un état 14 sans jamais avoir un état 1 et n’ont pas de `closingDate` à leur première version. Leur signature exacte n’est pas reconstituable à partir des champs vérifiés. Il faut conserver la connaissance d’un dossier gagné séparément de la disponibilité de sa date exacte de vente.

Les journées de `updateDate` et de `meta.ts` diffèrent pour 119 versions d’opportunités, 273 actions et 227 livraisons. Quelques écarts sont négatifs. `raw.deliveries.updateDate` atteint même le 24/12/2026 alors que son dernier `meta.ts` est le 29/09/2026. Ni l’égalité des journées ni le maximum de `updateDate` ne doivent piloter l’extraction CDC. Sans horodatage d’arrivée dans notre traitement, ces écarts ne permettent pas de mesurer un retard d’arrivée ni de valider une fenêtre de recouvrement.

### 2.3 Preuve et rattachement des démos

Le dictionnaire donne : 25=Demande de démo, 60=Démo 1, 68=Démo complémentaire, 17=RDV annulé. Les 16 colonnes de `raw.actions` ne contiennent pas de statut de tenue. La seule clé JSON observée dans `attributes` est `text`, présente sur 1 406 versions. Le texte libre n’est pas une preuve de réalisation homologuée.

Toutes les actions du jeu sont rattachées à un contact par le lien polymorphe ; aucune ne porte directement un lien de type opportunité. Sur les 607 actions courantes non supprimées de type 60/68, une jointure au contact, sans règle temporelle supplémentaire, produit 151 actions sans opportunité candidate, 298 avec une candidate et 158 avec plusieurs. Ce contrôle montre l’insuffisance du contact seul ; il ne valide pas une attribution automatique des 298 cas et ne prouve pas la réalisation des 607 séances.

Conséquence : conserver les actions candidates et les indicateurs de couverture ; ne pas publier les rendez-vous d’agenda comme `nb_demos` réalisés. Les compteurs d’actions candidates sont des diagnostics séparés.

### 2.4 Livraisons, montants et activité

Le dictionnaire donne 0=Signée, 1=En cours, 2=Terminée, 3=Annulée. Sur les 214 lignes courantes, 176 sont en état 1 et 38 en état 2. Les 176 en cours comprennent 161 fins absentes et 15 fins futures ; les 38 terminées ont toutes une fin antérieure à octobre 2026. Toutes les lignes ont un début ; aucune période inversée ni aucun montant absent, nul ou négatif n’a été observé.

Les 326 versions possèdent les deux propriétés JSON de quantité/prix. Le montant mensuel documenté dans `averageDailyPriceExcludingTax` égale quantité × prix unitaire à 0,005 près sur les 326 versions. Les quantités sont entières (1–592), les prix unitaires entre 8,64 et 30, avec au plus deux décimales. Cela vérifie une égalité arithmétique dans le jeu et confirme la correspondance documentaire des colonnes ; cela ne règle pas l’unité du montant d’opportunité.

Les 53 fins renseignées sont toutes à minuit, dont seulement 15 au dernier jour du mois. Vingt-sept débuts ne sont pas à minuit. Parmi les fins futures, une est au 24/12/2026 et quatorze au 31/12/2099. Conserver cette date 2099 sans la remplacer automatiquement par NULL. La **fin calendaire inclusive** et l’activité fondée sur l’état 1 à la date observée plus les bornes sont des décisions utilisateur de ce chat.

Toutes les livraisons rejoignent un projet existant avec société et opportunité renseignées. Les 171 projets observés sont de type 4 ; le dictionnaire contient aussi 7=Upsell Boond et 2=Formation. Le type du projet ne suffit donc pas à identifier les mouvements de MRR du case.

| Champ financier | Versions/lignes | NULL | Minimum renseigné | Maximum absolu |
| --- | ---: | ---: | ---: | ---: |
| Opportunité, estimé HT | 7 020 | 3 032 | 18 | 81 720 |
| Opportunité, pondéré HT | 7 020 | 3 032 | 18 | 81 720 |
| Livraison, montant mensuel documenté | 326 | 0 | 18 | 14 805,92 |
| Objectif | 144 | 0 | 8 | 56 540 |

Aucune valeur renseignée ne dépasse deux décimales avec une tolérance de `1e-7`. `exchangeRate=1` sur les 7 020 versions ; cela ne prouve ni une devise EUR universelle ni une unité mensuelle. Le montant d’opportunité est décrit comme « montant estimé HT saisi » : son unité mensuelle et sa nature de montant signé restent non confirmées. Sur les versions état 1, 6/189 versions New, 1/27 Upsell et 1/6 Formation ont un montant absent ; ce sont des versions, pas des nombres de ventes.

**Conversion décimale vérifiée :** une conversion directe du `Float64` de livraison vers `Decimal128` diffère de la conversion via `toString` pour 15/326 versions à l’échelle 2 et 12/326 à l’échelle 4. Prévoir une conversion depuis la représentation chaîne, puis des calculs décimaux sans arrondis successifs. La précision finale et l’arrondi sont normés dans les documents 01/02.

### 2.5 Référentiels et attribution

- Les objectifs couvrent janvier–décembre 2026, les segments SMB/LA/ES et les indicateurs `mrr_signed`, `demos`, `pipeline_generated`, `pipeline_weighted`. Aucune valeur négative.
- Les probabilités couvrent seulement les états `0,1,14,20,21,22,23,24,25,26,28` × SMB/LA/ES, avec des valeurs de 0,05 à 1. Aucun historique de validité ni distinction New/Upsell n’est présent dans la table source.
- Les BU sont 12=`Team BA - LA`, 13=`Team BA - SMB`, 15=`Team KAM`. Les dix membres actuels sont rattachés à l’agence France, sans chevauchement de BU actuel. Aucune BU Espagne n’est observée ; ne pas assimiler KAM à ES.
- Sociétés, toutes versions : FR=1 178, ES=182, BE=65, CH=39. Agences : 1=FR, 8=ES. Le pays ne prouve ni l’équipe ni la devise.
- Liens externes HubSpot renseignés : 1 166 deals vers Boond, 2 175 contacts vers Boond, uniques sur leur identifiant externe dans le jeu. Il reste 24 deals sans identifiant et 79 contacts avec identifiant vide. Aucun identifiant numérique de deal fractionnaire observé.

Les décisions utilisateur de ce chat maintiennent Nurturing parmi les ouverts, classent Abandonné et Non qualifié dans « Autres issues », retiennent la maturité entière d’une cohorte et des horizons J+30/J+60/J+90 depuis la création individuelle. Ces règles ne proviennent pas de la fréquence des valeurs source.

## 3. Requêtes de contrôle exécutées et reproductibles

Les noms physiques ci-dessous sont intentionnels dans des diagnostics de sources. Le client ajoutait `FORMAT JSONEachRow` aux requêtes ; ce seul suffixe de restitution est omis dans les blocs ci-dessous. Dans les futurs modèles, employer `source()`/`ref()`/`this`, et les paramètres/référentiels prévus au catalogue. Les constantes utilisées pour constater les valeurs du jeu ne deviennent pas des filtres métier codés en dur.

### Q01 — Versions, bases et métadonnées

```sql
SELECT version() AS version, timezone() AS timezone,
       currentDatabase() AS current_database;

SELECT database, name, engine, total_rows, sorting_key
FROM system.tables
WHERE database IN ('raw', 'hubspot', 'ref')
ORDER BY database, name;

SELECT database, table, name, type, position
FROM system.columns
WHERE database IN ('raw', 'hubspot', 'ref')
ORDER BY database, table, position;

SELECT name, engine
FROM system.databases
WHERE name IN ('raw', 'hubspot', 'ref', 'analytics');
```

Résultats : versions et schémas de §1/§2.1. `total_rows` est une métadonnée, recoupée par les comptages exacts Q02 ; ce n’est pas la mesure d’un nombre d’identités métier.

### Q02 — Clés de versions, suppressions et couverture des onze sources raw

Les onze requêtes suivantes ont été exécutées en développant les noms et les clés de chaque table ; elles sont regroupées ici avec leurs colonnes explicites.

```sql
SELECT count() AS nb_rows, uniqExact(tuple(`meta.customer`,id)) AS nb_objects,
       uniqExact(tuple(`meta.customer`,id,`meta.ts`)) AS nb_versions,
       countIf(`meta.deleted`) AS nb_deleted, min(`meta.ts`) AS first_meta_ts,
       max(`meta.ts`) AS last_meta_ts, uniqExact(`meta.customer`) AS nb_tenants
FROM raw.opportunities;

SELECT count() AS nb_rows, uniqExact(tuple(`meta.customer`,id)) AS nb_objects,
       uniqExact(tuple(`meta.customer`,id,`meta.ts`)) AS nb_versions,
       countIf(`meta.deleted`) AS nb_deleted, min(`meta.ts`) AS first_meta_ts,
       max(`meta.ts`) AS last_meta_ts, uniqExact(`meta.customer`) AS nb_tenants
FROM raw.actions;

SELECT count() AS nb_rows, uniqExact(tuple(`meta.customer`,id)) AS nb_objects,
       uniqExact(tuple(`meta.customer`,id,`meta.ts`)) AS nb_versions,
       countIf(`meta.deleted`) AS nb_deleted, min(`meta.ts`) AS first_meta_ts,
       max(`meta.ts`) AS last_meta_ts, uniqExact(`meta.customer`) AS nb_tenants
FROM raw.companies;

SELECT count() AS nb_rows, uniqExact(tuple(`meta.customer`,id)) AS nb_objects,
       uniqExact(tuple(`meta.customer`,id,`meta.ts`)) AS nb_versions,
       countIf(`meta.deleted`) AS nb_deleted, min(`meta.ts`) AS first_meta_ts,
       max(`meta.ts`) AS last_meta_ts, uniqExact(`meta.customer`) AS nb_tenants
FROM raw.contacts;

SELECT count() AS nb_rows, uniqExact(tuple(`meta.customer`,id)) AS nb_objects,
       uniqExact(tuple(`meta.customer`,id,`meta.ts`)) AS nb_versions,
       countIf(`meta.deleted`) AS nb_deleted, min(`meta.ts`) AS first_meta_ts,
       max(`meta.ts`) AS last_meta_ts, uniqExact(`meta.customer`) AS nb_tenants
FROM raw.ressources;

SELECT count() AS nb_rows, uniqExact(tuple(`meta.customer`,id)) AS nb_objects,
       uniqExact(tuple(`meta.customer`,id,`meta.ts`)) AS nb_versions,
       countIf(`meta.deleted`) AS nb_deleted, min(`meta.ts`) AS first_meta_ts,
       max(`meta.ts`) AS last_meta_ts, uniqExact(`meta.customer`) AS nb_tenants
FROM raw.businessunits;

SELECT count() AS nb_rows, uniqExact(tuple(`meta.customer`,id)) AS nb_objects,
       uniqExact(tuple(`meta.customer`,id,`meta.ts`)) AS nb_versions,
       countIf(`meta.deleted`) AS nb_deleted, min(`meta.ts`) AS first_meta_ts,
       max(`meta.ts`) AS last_meta_ts, uniqExact(`meta.customer`) AS nb_tenants
FROM raw.agencies;

SELECT count() AS nb_rows, uniqExact(tuple(`meta.customer`,id)) AS nb_objects,
       uniqExact(tuple(`meta.customer`,id,`meta.ts`)) AS nb_versions,
       countIf(`meta.deleted`) AS nb_deleted, min(`meta.ts`) AS first_meta_ts,
       max(`meta.ts`) AS last_meta_ts, uniqExact(`meta.customer`) AS nb_tenants
FROM raw.poles;

SELECT count() AS nb_rows, uniqExact(tuple(`meta.customer`,`meta.language`)) AS nb_objects,
       uniqExact(tuple(`meta.customer`,`meta.language`,`meta.ts`)) AS nb_versions,
       countIf(`meta.deleted`) AS nb_deleted, min(`meta.ts`) AS first_meta_ts,
       max(`meta.ts`) AS last_meta_ts, uniqExact(`meta.customer`) AS nb_tenants
FROM raw.dictionaries;

SELECT count() AS nb_rows, uniqExact(tuple(`meta.customer`,id)) AS nb_objects,
       uniqExact(tuple(`meta.customer`,id,`meta.ts`)) AS nb_versions,
       countIf(`meta.deleted`) AS nb_deleted, min(`meta.ts`) AS first_meta_ts,
       max(`meta.ts`) AS last_meta_ts, uniqExact(`meta.customer`) AS nb_tenants
FROM raw.projects;

SELECT count() AS nb_rows, uniqExact(tuple(`meta.customer`,id)) AS nb_objects,
       uniqExact(tuple(`meta.customer`,id,`meta.ts`)) AS nb_versions,
       countIf(`meta.deleted`) AS nb_deleted, min(`meta.ts`) AS first_meta_ts,
       max(`meta.ts`) AS last_meta_ts, uniqExact(`meta.customer`) AS nb_tenants
FROM raw.deliveries;
```

Résultats exacts en §2.1/§2.2. Les clés candidates sont uniques sur l’instantané inspecté, sans garantie que des futurs flux n’introduiront pas de collision.

### Q03 — Contenus sous une même clé : contrôle de collision

La requête suivante reproduit le contrôle exécuté sur les opportunités, avec leurs 25 colonnes énumérées. Les dix autres sources ont été contrôlées de la même manière avec leur liste réelle de colonnes et leur clé Q02. Résultat pour chacune : zéro groupe répété et zéro conflit.

```sql
SELECT count() AS nb_collision_groups,
       sum(nb_rows-1) AS nb_excess_rows,
       countIf(nb_payloads>1) AS nb_conflicts
FROM (
    SELECT `meta.customer`, id, `meta.ts`, count() AS nb_rows,
           uniqExact(tuple(
               `meta.customer`,id,`meta.deleted`,`meta.ts`,state,typeOf,title,reference,
               creationDate,updateDate,startDate,answerDate,closingDate,
               turnoverEstimatedExcludingTax,weighting,turnoverWeightedExcludingTax,
               exchangeRate,`origin.typeOf`,`origin.detail`,
               `relationships.mainManager.data.id`,`relationships.createdBy.data.id`,
               `relationships.company.data.id`,`relationships.contact.data.id`,
               `relationships.agency.data.id`,attributes
           )) AS nb_payloads
    FROM raw.opportunities
    GROUP BY `meta.customer`,id,`meta.ts`
    HAVING nb_rows>1
);
```

### Q04 — Historique initial incomplet et signature non datable

```sql
WITH o AS (
    SELECT `meta.customer` AS tenant, id,
           min(`meta.ts`) AS first_version_at,
           argMin(tuple(state,creationDate,`meta.deleted`),`meta.ts`) AS first_version
    FROM raw.opportunities
    GROUP BY tenant,id
)
SELECT first_version.1 AS first_state, count() AS nb_opportunities,
       countIf(isNull(first_version.2)) AS nb_missing_creation,
       countIf(first_version.2<first_version_at) AS nb_created_before_first_version,
       countIf(first_version.2>first_version_at) AS nb_created_after_first_version,
       min(dateDiff('second',first_version.2,first_version_at)) AS min_creation_to_first_meta_seconds,
       max(dateDiff('second',first_version.2,first_version_at)) AS max_creation_to_first_meta_seconds
FROM o
GROUP BY first_state
ORDER BY first_state;

WITH o AS (
    SELECT `meta.customer` AS tenant,id,
           countIf(state=1) AS nb_state1, countIf(state=14) AS nb_state14,
           argMin(tuple(state,closingDate,creationDate),`meta.ts`) AS first_v,
           min(`meta.ts`) AS first_meta_ts
    FROM raw.opportunities
    GROUP BY tenant,id
)
SELECT count() AS nb_only14,
       countIf(isNull(first_v.2)) AS nb_missing_closing,
       countIf(first_v.2<first_meta_ts) AS nb_closing_before_first_meta
FROM o
WHERE nb_state1=0 AND nb_state14>0;
```

Résultats : 106 premiers états autres que Lead, 107 créations antérieures ; 17 dossiers uniquement état 14 sans date closing disponible à leur première version.

### Q05 — Dictionnaires et propriétés JSON réellement présentes

```sql
SELECT `meta.language` AS language,
       argMax(tuple(`setting.state.opportunity`,`setting.action.contact`,
                    `setting.state.delivery`,`setting.typeOf.project`,`setting.origin`),
              `meta.ts`) AS config
FROM raw.dictionaries
GROUP BY `meta.customer`,`meta.language`;

SELECT attribute_key,count() AS nb_rows
FROM raw.actions
ARRAY JOIN JSONExtractKeys(attributes) AS attribute_key
GROUP BY attribute_key
ORDER BY nb_rows DESC;

SELECT attribute_key,count() AS nb_rows
FROM raw.deliveries
ARRAY JOIN JSONExtractKeys(attributes) AS attribute_key
GROUP BY attribute_key
ORDER BY nb_rows DESC;

SELECT attribute_key,count() AS nb_rows
FROM raw.opportunities
ARRAY JOIN JSONExtractKeys(attributes) AS attribute_key
GROUP BY attribute_key
ORDER BY nb_rows DESC;
```

Résultats : deux langues fr/en ; actions `text`=1 406 versions ; livraisons les deux clés quantité/prix=326 chacune ; opportunités `stateReason`=174 versions. Aucun indicateur de tenue de séance ni montant mensuel d’opportunité supplémentaire constaté.

### Q06 — Rattachement candidat des actions de démo

```sql
WITH actions AS (
    SELECT `meta.customer` AS tenant,id,
           argMax(tuple(typeOf,`relationships.dependsOn.data.id`,`meta.deleted`),
                  `meta.ts`) AS v
    FROM raw.actions
    GROUP BY tenant,id
), opps AS (
    SELECT `meta.customer` AS tenant,id,
           argMax(tuple(`relationships.contact.data.id`,`meta.deleted`),`meta.ts`) AS v
    FROM raw.opportunities
    GROUP BY tenant,id
), contact_counts AS (
    SELECT tenant,v.1 AS contact_id,count() AS nb_opportunities
    FROM opps
    WHERE v.2=false
    GROUP BY tenant,contact_id
)
SELECT count() AS nb_demo_actions,
       countIf(ifNull(c.nb_opportunities,0)=0) AS nb_no_candidate,
       countIf(c.nb_opportunities=1) AS nb_one_candidate,
       countIf(c.nb_opportunities>1) AS nb_multiple_candidates
FROM actions AS a
LEFT JOIN contact_counts AS c
    ON a.tenant=c.tenant AND a.v.2=c.contact_id
WHERE a.v.1 IN (60,68) AND a.v.3=false;
```

Résultat : 607 candidates, 151 sans opportunité, 298 avec une, 158 avec plusieurs. L’usage d’un tuple dans `argMax` conserve les valeurs NULL de la même version ; des `argMax` indépendants par colonne ne garantiraient pas cette cohérence.

### Q07 — Égalité montant/quantité/prix et conversions décimales

```sql
SELECT count() AS nb_versions,
       countIf(JSONHas(attributes,'subscriptionQuantityCharged')) AS nb_qty,
       countIf(JSONHas(attributes,'subscriptionPriceExcludingTax')) AS nb_price,
       countIf(abs(
           averageDailyPriceExcludingTax
           - JSONExtractFloat(attributes,'subscriptionQuantityCharged')
             * JSONExtractFloat(attributes,'subscriptionPriceExcludingTax')
       )>0.005) AS nb_amount_difference
FROM raw.deliveries;

SELECT count() AS nb_rows,
       countIf(toDecimal128(averageDailyPriceExcludingTax,2)
               !=toDecimal128(toString(averageDailyPriceExcludingTax),2))
           AS nb_float_cast_diff_at_scale2,
       countIf(toDecimal128(averageDailyPriceExcludingTax,4)
               !=toDecimal128(toString(averageDailyPriceExcludingTax),4))
           AS nb_float_cast_diff_at_scale4
FROM raw.deliveries;
```

Résultats : 326 quantités, 326 prix, zéro différence de montant à 0,005 ; 15 différences de cast à l’échelle 2 et 12 à l’échelle 4. Le diagnostic utilise les Float64 sources ; les futurs calculs financiers doivent utiliser les Decimal spécifiés.

### Q08 — États et bornes des livraisons

```sql
WITH current_deliveries AS (
    SELECT `meta.customer` AS tenant,id,
           argMax(tuple(state,startDate,endDate,averageDailyPriceExcludingTax,
                        attributes,`meta.deleted`,`relationships.project.data.id`),
                  `meta.ts`) AS v
    FROM raw.deliveries
    GROUP BY tenant,id
)
SELECT v.1 AS state,count() AS nb_deliveries,
       countIf(isNull(v.2)) AS nb_missing_start,
       countIf(isNull(v.3)) AS nb_missing_end,
       countIf(v.2>v.3) AS nb_reversed_dates,
       countIf(isNull(v.4)) AS nb_missing_amount,
       countIf(v.4=0) AS nb_zero_amount,
       countIf(v.4<0) AS nb_negative_amount,
       min(v.4) AS min_amount,max(v.4) AS max_amount
FROM current_deliveries
GROUP BY state
ORDER BY state;

SELECT count() AS nb_versions,
       countIf(isNull(startDate)) AS nb_null_starts,
       countIf(isNull(endDate)) AS nb_null_ends,
       countIf(startDate!=toStartOfDay(startDate)) AS nb_start_not_midnight,
       countIf(endDate!=toStartOfDay(endDate)) AS nb_end_not_midnight,
       countIf(endDate=toDateTime64(toLastDayOfMonth(endDate),3))
           AS nb_end_month_last_day_midnight,
       countIf(startDate=toDateTime64(toStartOfMonth(startDate),3))
           AS nb_start_month_first_day_midnight,
       min(startDate) AS min_start,max(startDate) AS max_start,
       min(endDate) AS min_end,max(endDate) AS max_end
FROM raw.deliveries;

SELECT endDate,count() AS nb_versions
FROM raw.deliveries
WHERE endDate>='2026-10-01 00:00:00'
GROUP BY endDate
ORDER BY endDate
LIMIT 30;
```

Résultats en §2.4. Les conversions dans les expressions de projection servent ici à profiler les données ; aucun filtre de modèle ne doit appliquer ces conversions à la colonne source.

### Q09 — Objectifs, probabilités et organisations

```sql
SELECT min(month) AS min_month,max(month) AS max_month,
       groupUniqArray(segment) AS segments,
       groupUniqArray(indicator) AS indicators,countIf(target<0) AS nb_negative
FROM ref.sales_targets;

SELECT state_id,groupArray(tuple(segment,probability)) AS probabilities
FROM ref.stage_probabilities
GROUP BY state_id
ORDER BY state_id;

SELECT id,name,`meta.ts` AS version_at,
       JSONLength(`relationships.includedManagers.data`) AS nb_members
FROM raw.businessunits
ORDER BY id,version_at;

SELECT country,count() AS nb_versions
FROM raw.companies
GROUP BY country
ORDER BY country;

SELECT id,country,count() AS nb_versions
FROM raw.agencies
GROUP BY id,country
ORDER BY id,country;
```

Les BU sont historisées (trois versions chacune), contrairement aux objectifs et probabilités fournis. L’absence actuelle de chevauchement des membres n’exclut pas un contrôle historique des périodes de rattachement.

### Q10 — Fonction de médiane/P90 disponible

```sql
SELECT quantileExactInclusive(0.5)(duration) AS median,
       quantileExactInclusive(0.9)(duration) AS p90
FROM (SELECT arrayJoin([10.,20.]) AS duration);
```

Résultat réellement observé sur ClickHouse 25.11.9.34 : médiane=15, P90=19. Il s’agit d’une vérification de fonction sur deux valeurs, pas d’un benchmark. La convention technique retenue pour la V1 est l’interpolation linéaire inclusive (R7) ; elle doit être utilisée de manière identique pour tous les graphiques de durée concernés, à partir des valeurs détaillées après filtre.

### Q11 — Mapping de la phase Démo et garde JSON nullable

Contrôle complémentaire exécuté pendant la rédaction, en HTTP readonly=1 et maximum10 s. La première tentative a passé directement une Nullable(String) à JSONExtractArrayRaw : erreur43 ILLEGAL_TYPE_OF_ARGUMENT, car Array(String) ne peut pas être imbriqué dans Nullable. Aucun résultat métier n'en a été tiré. La requête corrigée ci-dessous a été exécutée ; ifNull sert uniquement à rendre le parseur typable, pas à établir qu'un dictionnaire absent est un tableau vide connu.

```sql
WITH d AS (
    SELECT argMax(tuple(`setting.state.opportunity`), `meta.ts`) AS v
    FROM raw.dictionaries
    WHERE `meta.language` = 'fr'
)
SELECT
    JSONExtractInt(stage, 'id') AS stage_id,
    JSONExtractString(stage, 'value') AS stage_label
FROM d
ARRAY JOIN JSONExtractArrayRaw(ifNull(v.1, '[]')) AS stage
ORDER BY stage_id;
```

Constats dernière version française :24=Show Boond,22=Qualification,23=RDV découverte,21=Proposition remise,25=Projet validé par la direction,26=Shortlist,28=Closing ;20=Nurturing,1=Signé/formalités à finaliser,14=Signé/formalités finalisées. Ces codes ne sont PAS un ordre numérique de parcours.

```sql
SELECT
    `meta.ts` AS published_at,
    JSONExtractString(stage, 'value') AS stage_label
FROM raw.dictionaries
ARRAY JOIN JSONExtractArrayRaw(ifNull(`setting.state.opportunity`, '[]')) AS stage
WHERE `meta.language` = 'fr'
  AND JSONExtractInt(stage, 'id') = 24
ORDER BY published_at;
```

Ce second SELECT d'exploration a rendu deux lignes :2025-03-10 09:00:00.000 UTC et2025-12-08 10:00:00.000 UTC, libellé Show Boond identique. La fonction dans WHERE est utilisée ici pour un contrôle ad hoc du petit JSON source ; dans les modèles, préparer id/validité du JSON en CTE puis filtrer les colonnes préparées. case_rules.demo_stage_ids=[24] pour demo_crm est donc une correspondance source vérifiée, avec admissibilité temporelle par dim_stage ; ne pas extrapoler avant le premier dictionnaire qui contient ce code. Les parseurs des modèles conservent les drapeaux de présence/validité avant le fallback technique [] : JSON absent/invalide≠dictionnaire vide connu.

Autre SELECT complémentaire exécuté pendant la préparation : quantilesExactInclusive(0.5,0.9) sur1,2,3,4 a donné2,5 et3,7. round(toDecimal128('1.005',4),2)=1,01 et la variante−1.005=−1,01 ont été vérifiés par lecture. Cela vérifie les conventions de fonction et d'arrondi, aucun KPI réel ni performance.

### Q12 — Chronologie des créations de ligne et tri Nullable

Contrôle de rédaction exécuté par SELECT HTTP readonly=1,10 s maximum :

```sql
SELECT
    count() AS nb_lines,
    countIf(nb_created_values != 1) AS nb_creation_conflicts,
    countIf(created_at > first_published_at) AS nb_creation_after_first_publish,
    countIf(first_started_at < created_at) AS nb_backdated_service_start
FROM (
    SELECT
        `meta.customer`, id,
        uniqExact(creationDate) AS nb_created_values,
        min(creationDate) AS created_at,
        min(`meta.ts`) AS first_published_at,
        min(startDate) AS first_started_at
    FROM raw.deliveries
    GROUP BY `meta.customer`, id
);
```

Résultat214 lignes,0 dates de création variables,194 créations après première publication,0 début de service avant création. Ce défaut de chronologie ne fournit pas sa cause. Il interdit d'utiliser automatiquement creationDate pour prouver absence avant création ; les périodes observées restent évaluables selon état et service. La spécification ajoute line_created_at/is_creation_date_reliable et le cas conditionnel is_before_creation pour ne pas transformer toutes les lignes futures en contributions inconnues des mois antérieurs.

```sql
SELECT name, value
FROM system.merge_tree_settings
WHERE name = 'allow_nullable_key';
```

Valeur0 réellement vérifiée. int_opportunity_followup était proposé avec deux champs Nullable en ORDER BY ; le catalogue a été corrigé vers(model_run_id,record_key), non nullables. Aucun essai de création de table ni modification de ce setting n'a été réalisé.

Scénarios complémentaires aux 60 cas : (a) ligne créée après clôture, création fiable et aucune contradiction : contribution 0 avant naissance ; (b) ligne créée avant clôture mais première version tardive : NULL ; (c) création postérieure à une publication : preuve de naissance non fiable, pas de zéro inventé ; (d) société inactive aux DEUX clôtures comparables : mouvementstable et composantes0 connues. Étendre T13/T29/T30/T31 et les scénarios d'activité/MRR correspondants, sans présenter ces tests de transformation comme exécutés.

## 4. Contrat d’exécution cible — proposé pour la V1, non implémenté

### 4.1 Captures, calculs et publication

La capture conserve l’historique source. Les modèles dérivés recomposent **tout l’historique logique disponible** pour un jeu d’entrées figé, sous un nouveau `model_run_id`. Les faits exposent ces intermédiaires ; les DTR préparent les restitutions ; les datasets ne lisent que le run accepté par `int_publication`.

Cette stratégie privilégie la vérifiabilité des corrections sur le petit case. Elle n’est pas une optimisation de performance démontrée. L’append peut augmenter le stockage ; aucune purge des détails ni des anciens runs n’est introduite. La rétention de cinq ans concerne les agrégats.

| Famille | Écriture cible | Reprise et lecture |
| --- | --- | --- |
| 11 staging Boond | Incrémental append, `full_refresh=false` | Anti-jointure sur `source_version_key` ; premier chargement complet, ensuite recouvrement ; suppressions conservées |
| 2 staging HubSpot et 2 staging ref | Scan complet, changements/retours/absences techniques conservés, `full_refresh=false` | Clé de capture propre à la source ; disparition seulement à partir de captures complètes |
| 16 intermédiaires métier + 11 dimensions | Append de recompositions complètes, `full_refresh=false` | Même run et entrées figées ; aucune borne temporelle sur le recalcul logique |
| 9 faits | Vues de projection des intermédiaires | Tous les runs accessibles pour les tests/audits ; pas de bascule implicite de publication |
| 10 DTR | Append de recompositions complètes, `full_refresh=false` | Même contrat de run ; détail nécessaire aux filtres conservé |
| 10 datasets métier | Vues | Projection des DTR et sélection du run via `int_publication` |
| `dataset_publication_status` | Vue technique | Déplie les disponibilités de `quality_json` au grain run/mesure ; utile même si les datasets métier sont vides |
| `dwh_common.int_publication` | Table dbt monoligne, remplacement contrôlé | Pointeur unique changé après validation ; vide uniquement au bootstrap initial |

Total : 73 modèles futurs, dont 71 objets métier et 2 techniques. Les sept colonnes communes des dérivés sont `model_run_id`, `record_key`, `record_version_key`, `row_hash`, `calculated_at`, `rule_version`, `input_cutoff_at`. Chaque jointure versionnée inclut `model_run_id` en plus des clés métier/temporelles. Une ligne d’un ancien run ne complète pas silencieusement une absence dans le nouveau.

`model_run_id` est le SHA-256 du fingerprint canonique des entrées figées, règles/code et paramètres de calcul, selon 01. Les dates de calcul du run sont figées pour sa reprise. Une nouvelle tentative du même run ajoute seulement les enregistrements manquants. **L’existence d’une première ligne n’est pas une preuve que le modèle est complet.** Le succès exige le contrôle du nombre/digest attendus puis l’enregistrement du succès dans le manifeste durable du runner futur.

### 4.2 Variables du runner futur

Le runner et ses manifests sont à implémenter selon 01. Aucun script d’exécution existant n’est prétendu disponible. Il produit un JSON de variables dbt validé avant les commandes de §5.

| Variable | Type et règle |
| --- | --- |
| `model_run_id` | String SHA-256 hex minuscule, stable pour les entrées/règles/paramètres du run |
| `test_model_run_id` | String identique au candidat pour les tests avant publication |
| `input_cutoff_at` | ISO UTC avec millisecondes ; borne d’observation figée |
| `calculated_at` | ISO UTC ms ; horodatage figé du calcul |
| `rule_version` | String : hash des règles/code retenus |
| `source_capture_keys` | Dictionnaire source → liste de captures **complètes** HubSpot/ref autorisées pour le run |
| `cdc_overlap_hours` | Entier≥0 ; défaut technique explicite **48**, paramétrable et non garanti par une mesure de retard |
| `cdc_replay_from_at` | NULL ou borne ISO UTC ms imposée pour une reprise |
| `cdc_full_scan` | Booléen false par défaut ; true pour réconciliation complète |
| `capture_key` / `capture_at` | Identifiant et instant UTC ms figés par source |
| `source_tenant_id` | `demo_crm`, périmètre explicitement vérifié ; injecté dans les intermédiaires/dimensions des sources non tenantées, jamais ajouté comme champ source de staging |
| `business_timezone` | Europe/Paris, verrouillé pour cette version |
| `data_coverage_end_at` | Borne de case2026-09-30T22:00Z selon D16, ou borne individuelle si lacune ; pas inférée du dernier changement |
| `publication_model_run_id` | NULL seulement au bootstrap inexistant ; sinon run validé à publier |
| `publication_at` | ISO UTC ms fixé lors de la demande de publication |
| `publication_quality_json` | String JSON requis à la publication ; `[]` au bootstrap ; disponibilités exhaustives par mesure |

Les variables métier encore non confirmées — devise, canal, probabilités, portée des objectifs, seuils et attribution d’équipe des durées — restent NULL/non définies avec les motifs de 01/02. Une capture échouée ne figure pas dans `source_capture_keys`. Un hash fondé seulement sur le maximum de `meta.ts` serait insuffisant : une arrivée tardive peut porter un ancien timestamp.

Le 25/10/2026, le contrôle supplémentaire exécuté par lecture seule a donné `demo_crm`, 7 020 lignes :

```sql
SELECT `meta.customer` AS tenant_id,count() AS nb_rows
FROM raw.opportunities
GROUP BY tenant_id;
```

Cette observation justifie un scope explicite pour le case. Elle ne résout pas un rapprochement universel de sources sans tenant dans un environnement multitenant.

### 4.3 Incrémental CDC et reprise

1. Premier chargement ou cible vide : tout l’historique et les suppressions. Un maximum absent ne produit pas un filtre `>= NULL`.
2. Lire une fois le maximum cible de `src_published_at`. Enregistrer dans le manifeste la borne choisie **avant** toute écriture.
3. Calculer `max_cible - cdc_overlap_hours`. Comparer directement `meta.ts >= borne_constante_typée`, sans tronquer les millisecondes ni imposer la journée de `updateDate`.
4. Regrouper les répétitions strictement identiques du lot, puis anti-jointure sur `source_version_key`. Conserver toutes les versions et tombstones. Une collision tenant/id/timestamp avec contenu divergent bloque les traitements métier concernés, sans choisir arbitrairement un dernier état.
5. Après échec, rejouer la borne durable initiale et les mêmes entrées. Si elle est perdue/inconnue, scan complet ; le maximum cible peut avoir avancé partiellement.
6. Une arrivée antérieure à la fenêtre n’est pas garantie par le recouvrement. Une **réconciliation complète est obligatoire avant chaque publication mensuelle et, pour le case statique, avant chaque publication candidate**. Une différence conduit à compléter le staging puis recomposer et tester un run corrigé.
7. Un changement de source/règle produit un nouveau run complet ; le passé corrigé devient le défaut après publication, les anciens runs restant consultables.

`source_payload_hash` porte le tuple ordonné de toutes les colonnes source avec types et distinction NULL/chaîne vide. `source_version_key` inclut identité, publication et hash de contenu. `imported_at` n’entre pas dans ce hash et n’est pas réécrit lors d’une reprise. Une évolution de schéma provoque `on_schema_change=fail` et une migration explicite.

Une clé de version ne rend pas le DAG transactionnel. Le runner sérialise les écritures/publications par cible. Un échec conserve le pointeur précédent. Une capture non CDC dont la source change pendant la reprise est abandonnée au profit d’une nouvelle clé ; ses lignes physiques antérieures restent non publiées. Une source vide exige fin de lecture réussie et validation de la baisse anormale avant validation de capture complète.

### 4.4 Bootstrap, qualité et publication finale

Au premier lancement, `int_publication` doit exister vide et typé avant les vues qui le référencent. Le runner autorise `publication_model_run_id=null` seulement si la relation n’existe pas. Le `SELECT` typé filtré par 0 initialise zéro ligne. Si un pointeur existe, la demande de bootstrap échoue avant modification : elle ne vide jamais une publication.

Après les tests candidats, les vues de datasets sont créées et leurs contrats validés ; puis le pointeur est remplacé par une ligne du run accepté. L’échange atomique effectif est à vérifier en cible de test. Sans cette propriété, bloquer la publication et revoir l’implémentation avant de garantir une bascule indivisible.

Les tests avant publication ciblent `test_model_run_id` sur faits/intermédiaires/DTR. Les datasets lisent encore le run publié précédent : leur interrogation seule ne valide pas le nouveau candidat. Après bascule, vérifier la lecture publiée sans confondre ce contrôle avec les tests préalables.

`quality_json` est un tableau complet de statuts par `measure_id`, avec `dataset_family,availability_status,availability_reason,coverage_status,nb_expected,nb_known,data_coverage_end_at`. Les inconnus restent NULL, pas 0. Le garde valide JSON, unicité et exhaustivité des mesures, domaines et cohérence avec les données du candidat. `dataset_publication_status` déplie cette information sans dépendre d’un fichier local en BI et sans injecter une fausse ligne de grain différent dans les datasets métier. Il distingue ainsi jeu connu vide, indicateur bloqué et horizon non mature.

`int_publication` n’a pas de `ref()` amont vers les modèles métier : le garde final utilise le manifeste et les tests. Son tag distinct est `publication`. Toutes les constructions métier l’excluent explicitement. Ne pas utiliser une construction globale ou des ancêtres de datasets qui exécuteraient ce modèle trop tôt. La cohérence du pointeur s’entend pour une requête ; plusieurs requêtes BI de part et d’autre de la bascule peuvent voir deux publications successives.

## 5. Ordre et commandes futures — aucune exécutée dans ce chat

### 5.1 Prérequis et ordre

Implémenter d’abord les modèles/YAML/macros/tests du catalogue et le runner de 01 avec manifeste durable, empreintes, sérialisation et gardes de publication/reprise. Vérifier en cible de test les droits des seules bases de couches, l’append, les tests unitaires et l’échange atomique. Le profil du case n’est pas un déploiement validé. Les fréquences et SLA restent non décidés ; la V1 prévoit une exécution manuelle à la demande.

Les tags des modèles sont `capture`, `common`, `pipeline`, `revenue`, `mart`, `dtr`, `dataset`, et `publication` uniquement pour le modèle de pointeur. Le catalogue définit les `ref()` obligatoires. Les faits commerciaux doivent précéder le calcul des objectifs qui les utilise : construire l’union pipeline/revenus/mart permet à dbt de les intercaler correctement au premier lancement.

| Ordre | Phase | Dépendances / passage |
| ---: | --- | --- |
| 1 | Capture des 15 sources | Manifestes et clés valides ; aucune capture partielle utilisée |
| 2 | Dimensions/règles communes | Entrées complètes figées et référentiels partagés |
| 3 | Pipeline/revenus/mart, union topologique | Branches indépendantes après leurs dépendances communes ; objectifs après leurs faits de contribution |
| 4 | Dix DTR | Faits/dimensions du même run ; recomposition complète |
| 5 | Tests candidats | Données, fixtures et réconciliations ; échec bloquant ⇒ aucune publication |
| 6 | Bootstrap initial puis 11 vues datasets | Pointeur vide initial seulement ; dix métiers et une vue de qualité |
| 7 | Publication | JSON de qualité validé ; pointeur basculé en dernière étape |
| 8 | Contrôle de lecture | Pointeur et datasets cohérents ; artefacts/manifeste conservés |

Le runner peut paralléliser ultérieurement après mesure ; la recette V1 commence avec un seul thread. Il n’existe pas encore de script wrapper dont une commande pourrait être invoquée.

### 5.2 Commandes PowerShell à utiliser après implémentation

Depuis le dossier `dbt`, le futur runner prépare une séquence `$taskCaptureJobs` de quinze objets locaux contenant `model_name` et `vars_path`, un pour chaque staging du catalogue. Ce ne sont pas des variables dbt supplémentaires : ils désignent le modèle autorisé et le JSON de sa capture. Chaque JSON porte les `capture_key/capture_at` propres à la source, sa borne de reprise et ses paramètres de scan. Le runner vérifie la liste exhaustive des quinze modèles avant l’appel.

Les JSON de capture, de calcul et de publication sont distincts. Ils ne désignent pas des fichiers déjà livrés ici. Les commandes suivantes sont futures, après implémentation des modèles/tests/macros et du runner.

```powershell
$taskDbt = '.\.venv\Scripts\dbt.exe'
foreach ($taskCaptureJob in $taskCaptureJobs) {
    $taskCaptureVars = Get-Content -Raw -LiteralPath $taskCaptureJob.vars_path
    & $taskDbt run --profiles-dir . --select $taskCaptureJob.model_name --exclude 'tag:publication' --threads 1 --vars $taskCaptureVars
    if ($LASTEXITCODE -ne 0) { throw 'Capture source en échec : conserver sa borne.' }
    & $taskDbt test --profiles-dir . --select $taskCaptureJob.model_name --exclude 'tag:publication' --indirect-selection cautious --vars $taskCaptureVars
    if ($LASTEXITCODE -ne 0) { throw 'Contrôles de capture source en échec.' }
}
```

Après réussite complète et contrôle des nombres/digests de chaque source, le runner enregistre les captures complètes dans son manifeste. Il fige les entrées, puis produit `$taskVarsPath`, chemin absolu du **nouveau JSON de calcul** : listes `source_capture_keys` mises à jour, empreintes et `model_run_id` calculés après ces succès. Le manifeste complet et le JSON de variables sont distincts. Les assertions Jinja doivent vérifier les variables nécessaires aux modèles sélectionnés à leur compilation/exécution, sans rendre l’analyse des modèles non sélectionnés impossible pendant une phase de capture.

```powershell
$taskVars = Get-Content -Raw -LiteralPath $taskVarsPath
$taskVarsObject = $taskVars | ConvertFrom-Json
if ($taskVarsObject.test_model_run_id -ne $taskVarsObject.model_run_id) {
    throw 'Le run testé doit être le candidat.'
}
if ($null -ne $taskVarsObject.publication_model_run_id) {
    throw 'La construction ne doit pas demander de publication.'
}

& $taskDbt parse --profiles-dir . --no-partial-parse --vars $taskVars
if ($LASTEXITCODE -ne 0) { throw 'Analyse dbt en échec.' }

& $taskDbt test --profiles-dir . --select 'tag:capture' --exclude 'tag:publication' --indirect-selection cautious --vars $taskVars
if ($LASTEXITCODE -ne 0) { throw 'Tests de capture en échec.' }

& $taskDbt run --profiles-dir . --select 'tag:common' --exclude 'tag:publication' --threads 1 --vars $taskVars
if ($LASTEXITCODE -ne 0) { throw 'Dépendances communes en échec.' }
& $taskDbt run --profiles-dir . --select 'tag:pipeline tag:revenue tag:mart' --exclude 'tag:publication' --threads 1 --vars $taskVars
if ($LASTEXITCODE -ne 0) { throw 'Construction métier en échec.' }
& $taskDbt run --profiles-dir . --select 'tag:dtr' --exclude 'tag:publication' --threads 1 --vars $taskVars
if ($LASTEXITCODE -ne 0) { throw 'Construction DTR en échec.' }

& $taskDbt test --profiles-dir . --select 'test_type:unit' --exclude 'tag:publication' --vars $taskVars
if ($LASTEXITCODE -ne 0) { throw 'Tests unitaires en échec : publication interdite.' }
& $taskDbt test --profiles-dir . --select 'tag:common tag:pipeline tag:revenue tag:mart tag:dtr' --exclude 'tag:publication' --vars $taskVars
if ($LASTEXITCODE -ne 0) { throw 'Tests candidats en échec : publication interdite.' }
```

Le runner vérifie les nombres/digests attendus, tous les contrôles bloquants et l’absence de tests requis oubliés ou sautés. Le mode `cautious` limite les tests indirects des phases de capture pour ne pas sélectionner des dépendances encore absentes ; les contrôles finaux couvrent les réconciliations entre branches. Les tests doivent explicitement filtrer le candidat, sans supposer que le pointeur a déjà basculé.

Bootstrap suivant **seulement après constat de l’absence de la relation** par le runner, au premier lancement ; omettre si le pointeur existe :

```powershell
& $taskDbt run --profiles-dir . --select 'int_publication' --threads 1 --vars $taskVars
if ($LASTEXITCODE -ne 0) { throw 'Bootstrap du pointeur vide en échec.' }
```

Puis créer les vues et vérifier leur structure :

```powershell
& $taskDbt run --profiles-dir . --select 'tag:dataset' --exclude 'tag:publication' --threads 1 --vars $taskVars
if ($LASTEXITCODE -ne 0) { throw 'Création des vues dataset en échec.' }
& $taskDbt test --profiles-dir . --select 'assert_dataset_contracts' --vars $taskVars
if ($LASTEXITCODE -ne 0) { throw 'Contrats de restitution en échec.' }
```

`assert_dataset_contracts` est un test futur : onze vues présentes, noms/types conformes, dépendance au pointeur, JSON qualité bien déplié et validation des projections candidates depuis les DTR. Il ne prétend pas que les datasets avant publication exposent déjà le candidat.

La phase finale reçoit un **nouveau JSON validé** du runner, via `$taskPublishVarsPath`, avec identifiant accepté, instant de publication et `publication_quality_json` exhaustif. Un simple succès des modèles n’autorise pas cette phase sans les tests :

```powershell
$taskPublishVars = Get-Content -Raw -LiteralPath $taskPublishVarsPath
$taskPublishObject = $taskPublishVars | ConvertFrom-Json
if ($taskPublishObject.publication_model_run_id -ne $taskVarsObject.model_run_id) {
    throw 'La publication doit viser exactement le run accepté.'
}
& $taskDbt test --profiles-dir . --select 'assert_publication_quality_candidate' --vars $taskPublishVars
if ($LASTEXITCODE -ne 0) { throw 'Qualité candidate incohérente : publication interdite.' }
& $taskDbt run --profiles-dir . --select 'int_publication' --threads 1 --vars $taskPublishVars
if ($LASTEXITCODE -ne 0) { throw 'Publication en échec : lire le pointeur avant reprise.' }
& $taskDbt test --profiles-dir . --select 'assert_published_datasets_one_run' --vars $taskPublishVars
if ($LASTEXITCODE -ne 0) { throw 'Lecture publiée incohérente : diagnostiquer immédiatement.' }
```

Les tests nommés sont des objets **à créer**. `assert_publication_quality_candidate` valide le JSON de la demande finale contre le catalogue et les DTR du candidat, avant toute modification du pointeur ; il ne dépend pas du contenu déjà publié. Le runner archive les artefacts après chaque commande : plusieurs invocations remplacent `run_results.json`, ce qui impose de conserver les résultats intermédiaires pour le garde final. Aucun secret ne figure dans les documents/manifests publiables.

La syntaxe des [tests dbt](https://docs.getdbt.com/reference/commands/test) et les [modes de sélection indirecte](https://docs.getdbt.com/reference/node-selection/test-selection-examples) sont documentés officiellement. La matérialisation unitaire installée doit encore être validée avec les types du case.

### 5.3 Reprise et reconstruction

- Même run après échec dérivé : reprendre manifeste, variables et entrées figées ; rejouer phases manquantes puis contrôles dépendants. Ne pas changer `calculated_at` tout en prétendant reprendre le même run.
- Borne CDC connue : `cdc_replay_from_at` reprend la borne durable initiale, comparaison inclusive et anti-jointure. Borne inconnue : `cdc_full_scan=true`.
- Arrivée hors fenêtre/publication mensuelle/candidat du case : scan complet ; après capture réussie, recalculer l’empreinte d’entrées et générer le JSON du run corrigé. Ne pas changer les entrées d’un run déjà calculé sans changer son identifiant.
- Nouvelle logique : nouveau `rule_version` et run complet, puis tests/bascule. Les captures et anciens runs restent conservés.
- Rejeu d’une ancienne publication : vérifier complétude, schéma compatible et tests avant demande explicite de bascule ; aucune lecture ancienne ne nécessite de changer le pointeur.
- Schéma incompatible : migration explicite en cible de validation. Ne pas contourner `full_refresh=false` en supprimant l’historique.

Aucune commande `--full-refresh`, aucun nettoyage de capture et aucune destruction de cible ne font partie de la procédure normale. Le nouveau run assure le recalcul sans supprimer les versions précédentes.

## 6. Registre des tests de données à implémenter

Tous les contrôles ci-dessous sont **planifiés, non exécutés**. `ERROR` bloque la publication du candidat et conserve le pointeur précédent. `WARN` signale un manque de couverture à qualifier/exposer ; il n’autorise pas à afficher une valeur inconnue comme zéro ou un total complet. Un avertissement incompatible avec une couverture promise bloque cette publication.

Utiliser les tests génériques `unique`, `not_null`, `accepted_values`, `relationships` là où leur grain convient. Les contrôles composites/temporels/de cardinalité/réconciliation sont des tests SQL de données singuliers, avec colonnes énumérées. Une clé composite peut être testée par `GROUP BY ... HAVING count()>1`, sans installation de package. Les lignes testées et le run candidat sont explicitement bornés ; un contrôle d’historique complet indique ce périmètre.

### 6.1 Structure et traçabilité

| ID | Objet/périmètre | Attendu | Gravité | Action si échec |
| --- | --- | --- | --- | --- |
| T01 | Sources/staging | Quinze correspondances 1 pour 1 ; 179 colonnes sous les noms `src_` documentés ; types/nullabilité préservés ou adaptation technique explicite | ERROR | Corriger mapping/type sans éliminer de colonne |
| T02 | Chaque staging | `source_version_key` non NULL unique ; versions et tombstones conservés | ERROR | Diagnostiquer répétition/collision, compléter sans écraser |
| T03 | Clé candidate CDC | Aucun contenu divergent non résolu sous tenant/id/publication ; dictionnaire tenant/langue/publication | ERROR | Conserver preuve et bloquer état courant ambigu |
| T04 | Captures HubSpot/ref | Manifestes complets ; A→B→A conservé ; absence déduite seulement d’un scan complet | ERROR | Refaire capture ou nouvelle tentative complète si source changée |
| T05 | Chaque dérivé persisté | `record_version_key` unique ; une ligne par `(model_run_id,record_key)` au grain du catalogue ; contrat commun complet | ERROR | Corriger grain/clé ou remplir lignes manquantes |
| T06 | Jointures de dérivés | Même `model_run_id` candidat ; pas de complément silencieux d’un ancien run | ERROR | Ajouter clé de run et recomposer descendants |
| T07 | Run/manifeste | Fingerprint conforme ; nombres/digests de clés ET row_hash attendus atteints ; métadonnées calculated_at/input_cutoff_at/rule_version figées identiques ; résultat valide vide reconnu | ERROR | Reprendre les manquants ; bloquer une divergence de contenu avant anti-jointure, présence d’une ligne ne prouve pas succès |
| T08 | YAML/SQL compilé | Chaque modèle/colonne décrit ; noms/schémas et projections explicites conformes ; source/ref/this ; pas de DDL/DML manuel | ERROR | Corriger documentation/SQL avant recette |
| T09 | DAG/runner | Pas de cycle ; tag publication distinct et exclu des constructions métier | ERROR | Corriger DAG/sélection ; refuser construction globale dangereuse |
| T10 | Schémas | Compatibilité des colonnes/types attendus ; aucun changement silencieux de précision/sens/nullabilité | ERROR | Migration explicite puis validation |

### 6.2 Temporalités et cardinalités

| ID | Objet/périmètre | Attendu | Gravité | Action si échec |
| --- | --- | --- | --- | --- |
| T11 | Intervalles objet/run | Début<fin si fin présente ; `[début,fin[` ; pas de chevauchement ni double état à date | ERROR | Corriger séquencement/collision et périodes |
| T12 | Lecture courante | Dernière version puis suppression ; ancien actif d’un objet supprimé ne réapparaît pas | ERROR | Corriger lecture et descendants |
| T13 | Dates d’événements | D15 admet le proxy CDC pour transition réellement observée ; métier/publication/import distincts ; aucun événement inventé avant première trace ni pour17 cas14 sans1 | ERROR si date fabriquée ; WARN si absence | is_event_time_accepted=true pour proxy admissible ; conserver event_time_basis=cdc_transition_proxy et lacunes NULL |
| T14 | Calendrier/clôtures | Europe/Paris ; minuit mois suivant exclu ; conversion UTC explicite ; aucune durée fixe de mois | ERROR | Refaire bornes et mois concernés |
| T15 | Jointure plusieurs-à-un | Au plus un match temporel dans le même run ; lignes/sommes du fait conservées | ERROR | Corriger référentiel/intervalle ; pas de regroupement masquant fan-out |
| T16 | Équipes/membres | Pas de double attribution non résolue à l’imputation ; pays/agence non assimilés à équipe | ERROR si double contribution ; WARN si inconnu | Mapping validé ou inconnu et couverture |
| T17 | HubSpot→Boond | Conversion entière exacte ; tenant explicite ; cardinalité documentée ; non-appariés conservés | ERROR si jointure fausse ; WARN si lien absent | Rejeter conversion non sûre, exposer manque |
| T18 | Montants | Decimal38,4 via chaîne ; NULL préservé ; pas d’arrondi intermédiaire/dépassement ; unité/devise explicites | ERROR | Corriger conversion/règle, jamaisNULL→0 |

### 6.3 Pipeline, signatures, démos et objectifs

| ID | Objet/périmètre | Attendu | Gravité | Action si échec |
| --- | --- | --- | --- | --- |
| T19 | Entrée pipeline | Une entrée par opportunité à création Boond, qualification distincte ; types New/Upsell séparables | ERROR | Corriger événement/grain et cohortes/flux |
| T20 | Signature | Entrée état 1 reconnue ; passage1→14 ne compte pas deux ventes | ERROR | Corriger événement, pas de comptage de versions CDC |
| T21 | Montant commercial | Aucun MRR signé officiel sans unité/source confirmée ; supplément upsell distinct du total abonnement | ERROR si chiffre/libellé faux ; WARN si indisponible | GarderNULL et motif, décision métier ciblée |
| T22 | Démos réalisées | Chaque séance comptée a une preuve de tenue validée ; agenda/phase seule insuffisants | ERROR si candidate publiée comme réalisée | Retirer réalisé/taux officiels, garder diagnostic séparé |
| T23 | Action→opportunité | Pas de duplication d’action entre dossiers sans règle validée ; ambiguïtés explicites | ERROR si multiplication ; WARN si ambiguïté | Corriger règle ou rester au grain action/contact |
| T24 | Nb In demo | Une société par date/périmètre, même avec plusieurs dossiers Démo | ERROR | Recompter identités détail, pas somme de distincts locaux |
| T25 | Pondération | Coefficient0–1 dans contexte valide ; manque/historique non capturé explicites | ERROR si coefficient inventé ; WARN si manque | Pas de probabilité absente→0, limiter périmètre calculable |
| T26 | Objectifs/réalisés | Même mois/équipe/indicateur/unité/définition/portée ; cible équipe non répétée sur individus | ERROR | Corriger grain/jointure ; taux non comparableNULL |
| T27 | Filtres synthèse | MRR/churn global identifié ; équipe ne change pas ce bloc ; New/Upsell appliqué au bon concept | ERROR | Corriger portée et libellés |

### 6.4 MRR et clientèle

| ID | Objet/périmètre | Attendu | Gravité | Action si échec |
| --- | --- | --- | --- | --- |
| T28 | Activité à date | État 1 de la version pertinente, début atteint, fin civile inclusive ; NULL ouvert, pas de prorata | ERROR | Corriger version/bornes et mois touchés |
| T29 | MRR ligne→société | Une contribution par livraison active ; projet/société sans multiplication ; somme ligne=société au même mois/run | ERROR | Corriger liaison puis agrégation |
| T30 | Client actif | Au moins une ligne active admissible, sans se fonder sur statut CRM ni sur montant > 0 | ERROR | Corriger activité et comptage société |
| T31 | Mouvement société/clôtures | New entrant/retour, Upsell hausse nette si société restée active, baisse/départ en churn | ERROR | Corriger comparaison des clôtures et activités |
| T32 | Réconciliation | Par société et au global, `MRR_fin = MRR_début + New + Upsell − churn_MRR`, même périmètre/devise/run | ERROR | Isoler société/mois et remonter contributions ; bloquer publication |
| T33 | Net par société | Agrégation avant mouvement ; pas de compensation entre sociétés ; intra-mois non détaillé | ERROR | Recalculer au grain société/clôtures |
| T34 | New MRR total | New+Upsell, expansion non ajoutée deux fois | ERROR | Corriger total/composantes et cartes |
| T35 | Churn clientèle/taux | Départs/base début compatibles ; dénominateur0/inconnu⇒NULL ; nombre de départs distinct des montants | ERROR | Recalculer depuis numérateur/dénominateur, jamais moyenne de taux |
| T36 | Couverture clôture précédente | Premier mois sans base fiable non comparable ; passé absent non remplacé par zéro | ERROR si faux mouvement ; WARN si manque explicite | Étendre preuve ou maintenir indisponibilité |

### 6.5 Durées, cohortes et restitution

| ID | Objet/périmètre | Attendu | Gravité | Action si échec |
| --- | --- | --- | --- | --- |
| T37 | Passages | Une ligne par passage ; retour=nouveau passage ; simple mise à jour CDC ne crée pas d’étape | ERROR | Corriger segmentation et clés |
| T38 | Durée/ancienneté | Durée terminée seulement si sortie connue ; courant exclu des quantiles terminés et inclus dans ancienneté | ERROR | Corriger populations ; pas de fermeture artificielle à observation |
| T39 | Quantiles | ExactInclusive recalculé après filtre sur les passages ; pas moyenne de médianes/P90 ou quantiles locaux | ERROR | Recalculer depuis détail et conserver effectif |
| T40 | Seuils | Paramètres et comparaison explicites ; inconnus distincts ; aucun seuil silencieux | ERROR si seuil inventé ; WARN si absent exposé | Fournir paramètre ou affichage sans classe de stagnation |
| T41 | Cohorte/horizon | Une opportunité par définition/horizon/run ; mois de création Boond et J depuis création individuelle | ERROR | Corriger calendrier/clé/dénominateur |
| T42 | Maturité | Calculée pour toute la cohorte avant filtres équipe/canal ; horizon non atteint indisponible, jamais0 | ERROR | Qualifier/masquer horizon, garder détail futur |
| T43 | Issues | Nurturing ouvert ; Abandonné/Non qualifié autres issues ; pas d’inconnu forcé en Perdu | ERROR si faux classement ; WARN si inconnu | Mapping correct ou issue indéterminée explicite |
| T44 | Dénominateurs/coverage | Comptes réconciliés ; numérateur≤base ; autres issues/inconnus inclus dans base complète ; couverture distincte de maturité | ERROR | Corriger population/base, pas de passé complété par 0 |
| T45 | Dix DTR/datasets métier | Grains, filtres et projections du catalogue ; objectifs/montants/taux/distincts préservés | ERROR | Comparer au détail factuel et corriger agrégation |
| T46 | Pointeur/lecture publiée | Monoligne vers run complet accepté ; tous datasets lisent ce run, aucune variable BI de run | ERROR | Bloquer ou basculer seulement vers run compatible validé |
| T47 | Révisions | Ancien run inchangé ; nouveau reflète correction/retrait, sans reprise de ligne ancienne | ERROR | Corriger append/sélection ; préserver preuves |
| T48 | Fraîcheur | Cutoff/capture complète/qualité exposables ; aucun SLA inventé | WARN ; ERROR si promesse fausse | Qualifier livraison et faire décider les fréquences |
| T49 | JSON qualité / vue technique | JSON valide, `measure_id` unique/exhaustif, statuts du domaine ; `nb_known≤nb_expected` si connus ; NULL conservé ; cohérence avec candidat | ERROR | Corriger agrégation de qualité avant publication |
| T50 | Jeu vide / indisponible | Vue de statut utile sans ligne métier ; vide connu peut compter0, indisponible/non mature reste NULL avec motif | ERROR | Corriger qualité et lecture BI, sans faux enregistrement multigrain |

## 7. Fixtures et scénarios de recette à implémenter

Les valeurs ci-dessous sont des **jeux de test futurs**, distincts des maquettes. Les fixtures SQL doivent typer les NULL, DateTime64 UTC et Decimal pour éviter une inférence incompatible. Tester `is_incremental()` vrai/faux en contrôlant macros/variables et l’entrée `this`. Les tests unitaires portent sur les transformations difficiles, pas sur des projections triviales. Ils ne prouvent pas la résistance à un arrêt de processus : les scénarios d’échec nécessitent une recette d’intégration isolée.

### 7.1 Captures et reprises

| Scénario | Entrée / arrêt simulé | Résultat attendu |
| --- | --- | --- |
| S01 — Premier chargement | Cible absente ; objets et plusieurs versions dont tombstone | Toutes versions distinctes, suppressions incluses, unicité du registre |
| S02 — Cible vide | Relation présente sans ligne | Maximum absent⇒scan complet, pas filtre NULL |
| S03 — Rejeu | Même extraction deux fois | Même ensemble de clés, aucun doublon ni premier import réécrit |
| S04 — Borne inclusive | Objets/versions distincts exactement à borne | Toutes versions de borne reprises, identités conservées |
| S05 — Répétition exacte | Deux copies identiques et copie déjà en cible | Une seule version et cardinalité d’entrée expliquée |
| S06 — Conflit temporel | Même tenant/id/instant, deux contenus | Preuves conservées ; conflit bloquant, pas d’ordre inventé |
| S07 — Suppression | Actif puis tombstone | Historique complet ; ancien actif absent de lecture courante |
| S08 — Dates décalées | updateDate autre jour/futur par rapport au CDC | Capture pilotée par publication, version conservée |
| S09 — Retard dans fenêtre | Timestamp à l’intérieur du recouvrement | Version ajoutée, correction dans nouveau run |
| S10 — Retard hors fenêtre | Timestamp antérieur à borne | Scan complet détecte/complète ; publication interdite avant réconciliation |
| S11 — Échec partiel CDC | Lignes insérées puis arrêt et maximum avancé | Borne durable initiale rejouée ; complément sans perte/doublon |
| S12 — Borne perdue | Manifeste de borne inconnu | Scan complet, pas nouvelle petite fenêtre arbitraire |
| S13 — A→B→A non CDC | Trois captures complètes | Trois versions/changements ; retourA pas éliminé par son ancien hash |
| S14 — Disparition | Absence dans scan partiel puis scan complet | Partiel ne clôt rien ; disparition seulement après capture complète |
| S15 — Source vide | Lecture complète réussie à zéro | Capture vide traçable, baisse anormale validée ; vide distinct d’échec |

### 7.2 Recomposition et publication

| Scénario | Entrée / arrêt simulé | Résultat attendu |
| --- | --- | --- |
| S16 — Même fingerprint | Relance entrées/règles/paramètres identiques à une nouvelle heure | Même run et lignes, aucune copie ; réutiliser calculated_at/input_cutoff_at/rule_version initiaux, pas les nouveaux timestamps de tentative |
| S17 — Append partiel | Arrêt après fraction du candidat ; seconde variante même clé/run avec row_hash différent | Présence≠succès ; reprise complète les manquants avec métadonnées figées et vérifie nombre/digest ; divergence de payload sous même clé/run bloque AVANT anti-jointure |
| S18 — Ancien timestamp | Source tardive sans hausse du maximum CDC | Fingerprint changé par entrées complètes ; nouveau run et ancien conservé |
| S19 — Correction passée | Valeur/règle d’un ancien mois corrigée | Recomposition complète ; passé corrigé après tests/bascule |
| S20 — Retrait logique | Contribution ancienne absente du nouveau run | Ancien inchangé, pas de reprise automatique d’ancienne ligne |
| S21 — Échec avant pointeur | Intermédiaire/DTR/test échoue | Ancien publié conservé, candidat diagnostic/rejeu possible |
| S22 — Bootstrap | Aucune relation de pointeur | Table vide typée, vues créables, aucune publication fictive |
| S23 — Bootstrap interdit | NULL demandé avec pointeur existant | Échec avant modification, pointeur inchangé |
| S24 — Bascule acceptée | Nouveau run complet et validé | Pointeur unique vers accepté ; toutes vues même run ; passé conservé |
| S25 — Arrêt autour échange | Arrêt avant/après bascule | Lire pointeur pour décider reprise idempotente ; jamais autre candidat |
| S26 — Concurrence | Deux écrivains/publications simultanés | Garde refuse second, pas de mélange d’entrées/IDs |
| S27 — Sélection dangereuse | Construction globale/ancêtres datasets | Runner refuse ou exclut publication, aucun pointeur anticipé |
| S28 — Ancien schéma | Bascule vers ancien run incompatible | Refus avant bascule, migration/validation nécessaires |
| S29 — Qualité sans lignes | Aucun résultat métier mais mesure bloquée/non mature | Statut présent dans JSON/vue technique ; valeurNULL, pas 0 |
| S30 — Vide connu | Population connue vide et définition disponible | Statut adapté et compte 0 explicite ; pas confondu avec manque source |

### 7.3 Règles métier et doubles comptes

| Scénario | Données synthétiques | Attendu |
| --- | --- | --- |
| S31 — Formalités | Une opportunité passe 1 puis 14 | Une signature observée, aucune seconde vente à finalisation |
| S32 — Signature sans date | D’abord 14, jamais 1, sans closing | Gagné observé possible, date exacteNULL ; pas de vente datée au premier CDC |
| S33 — Démo/société | Deux dossiers Démo d’une société, trois actions sans preuve | In demo=1, aucun nb_demos réalisé déduit de l’agenda |
| S34 — Contact multiple | Une action liée à contact de deux dossiers | Une candidate ambiguë, pas deux contributions |
| S35 — Upsell | Société active 100→150 | Upsell=50, New=0, churn=0, New MRR total=50 |
| S36 — Baisse | Société active 100→70 | Churn MRR=30, aucun départ client |
| S37 — Départ/retour | 100→inactif 0 puis mois suivant actif 80 | Churn=100 et départ, puis New=80 comme retour |
| S38 — Sociétés distinctes | A 100→70, B 100→140 | Churn=30 et Upsell=40, pas hausse globale de 10 classée upsell |
| S39 — Lignes internes | Même société : ligne 100→50 et ligne 100→130 | Société 200→180, churn net=20 ; pas churn=50 et upsell=30 |
| S40 — Intra-mois | Départ/retour à MRR identique entre deux clôtures actives | Aucun détail intra-mois ajouté ; comparaison nette conservée |
| S41 — Fin inclusive | Ligne état 1 fin 30/09 ; clôtures 30/09 puis 31/10 | Active à première, inactive à seconde ; pas exclusion dès minuit 30/09 |
| S42 — Fuseau/bornes | Événement minuit Paris du 1 er ; clôtures mars/octobre | Nouveau mois ; bornes UTC adaptées au fuseau |
| S43 — Montant absent | Une contribution inconnue, une connue | NULL/qualité conservés ; total officielNULL si contribution requise manque |
| S44 — Taux global | Groupes 1/2 et 9/10 | Taux 10/12, pas moyenne de 50 % et 90 % |
| S45 — Cible équipe | Objectif 100, deux réalisations 30 et 40 | Équipe 70 / cible 100 une fois ; pas cible individuelle inventée |
| S46 — Stocks | MRR 100 puis 150 sur deux mois | Stocks de clôture séparés, jamais carte 250 par somme des mois |
| S47 — Actif à zéro | Ligne en cours admissible, montant 0 connu | Client actif ; pas activité fondée sur MRR>0 ; taux à base 0 reste NULL |

### 7.4 Durées, filtres et cohortes

| Scénario | Données synthétiques | Attendu |
| --- | --- | --- |
| S48 — Retour d’étape | A→B→A, deux mises à jour sans changement dans premier A | Trois passages dont deux A, sans passage supplémentaire pour simple CDC |
| S49 — Passage courant | Un terminé et un en cours | Distribution terminés distincte d’anciennetés, pas fermeture fictive |
| S50 — Quantiles pairs | Durées 10 et 20 | Médiane=15/P90=19 via ExactInclusive |
| S51 — Filtres | Sous-populations équipe/canal d’effectifs différents | Quantiles recalculés depuis détail filtré, pas moyenne locale |
| S52 — Seuil | Ancienneté sous/égale/au-dessus d’un seuil de test | Comparaison du catalogue ; changement de seuil ne change pas durée |
| S53 — Maturité entière | Créations début/fin du mois ; seule première âgée de 30 jours | Cohorte J+30 indisponible jusqu’à maturité entière, avant filtres |
| S54 — Horizons | Cohorte mûre à 30 jours mais pas 60 | J+30 calculable sous couverture ; J+60 non mature, pas 0 |
| S55 — Couverture | Horizon atteint avant première preuve d’état | Inconnu/non observable distinct d’ouvert et non mature ; base complète conservée |
| S56 — Issues | Nurturing, Abandonné, Non qualifié, Perdu, Signé | Nurturing ouvert ; deux autres issues séparées de Perdu ; classes restantes conservées |
| S57 — Issue évolutive | Même dossier change entre 30 et 60 jours | Une issue par dossier/horizon, dénominateur non multiplié par événements |
| S58 — Distinct filtré | Même société dans plusieurs dossiers/équipes | Recompter identité au périmètre choisi, pas somme des distincts |
| S59 — Cohérence de run | Branches pipeline/revenus avec IDs différents | T06 bloque avant publication, aucune jointure à ancien run |
| S60 — Changement d’heure | Instants autour des bascules Paris | Durée=(sortie_UTC_ms−entrée_UTC_ms)/1000, jours=secondes/86400 ; horizon=ajout de jours civils au timestamp Paris puis UTC, pas H×86400 |

Ces fixtures ne fixent aucun seuil métier par défaut. Les dates doivent inclure des millisecondes et les changements d’heure. Les quantiles suivent [ExactInclusive](https://clickhouse.com/docs/reference/functions/aggregate-functions/quantileExactInclusive), interpolation R7, vérifiée sur la fonction Q10. Les tests de reprises/publication manipulent une cible de test isolée, jamais les sources de preuve du case.

## 8. Acceptation et mesure des performances

La spécification est prête à coder quand les 73 fiches et 179 colonnes source sont couvertes, les noms/types/grains/clés/jointures/temporalités concordent entre 01/02/03, les trois dashboards sont couverts et aucun choix technique essentiel n’est implicite. Les manques métier sont associés aux objets et aux sortiesNULL/qualifiées, sans valeurs fictives. Le statut v0.2 est finalisé pour implémentation, avec décisions déléguées01§7 et indisponibilités intentionnelles ; aucune décision métier essentielle ne reste à inventer.

La recette après implémentation exige :

1. Tous les contrôles ERROR réussissent sur le candidat ; chaque WARN possède périmètre, conséquence de restitution et traitement enregistré.
2. Les scénarios critiques de capture/reprise/publication sont exécutés en cible isolée avec résultats/artefacts conservés.
3. Les trois dashboards recalculent distincts, taux, montants et quantiles après filtre ; objectifs/réalisés restent comparables et portée globale du MRR/churn visible.
4. Chaque publication du case statique a une réconciliation CDC complète et des captures non CDC complètes reconnues par manifeste.
5. Tous les modèles attendus sont complets, leurs tests non omis ; JSON qualité exhaustif/cohérent et onze vues de restitution valides avant bascule.
6. Les démos réalisées, montants commerciaux non confirmés et historiques absents restent indisponibles avec motifs. Une livraison partielle des indicateurs calculables ne prétend pas livrer ceux bloqués.
7. Le pointeur bascule en dernier ; la vérification de lecture confirme le run accepté, son JSON qualité et les datasets, sans supprimer d’ancien run.

**Aucune comparaison de performance n’a été exécutée dans ce chat.** Lors de l’implémentation, mesurer sur même requête/entrées : EXPLAIN, lignes/octets lus, durée, lignes retournées et résultats financiers/compteurs. Conserver versions, paramètres, état de cache et répétitions avant de conclure à un gain. Le petit case ne prouve pas le comportement à fort volume. Une optimisation préserve les résultats, l’historique et les filtres.

La documentation officielle de l’[adaptateur ClickHouse](https://clickhouse.com/docs/integrations/connectors/data-ingestion/etl-tools/dbt/features-and-configurations) confirme schema/base et options de profil ; les [matérialisations](https://clickhouse.com/docs/integrations/connectors/data-ingestion/etl-tools/dbt/materializations) sont à confronter au code réellement installé. Ces références ne remplacent pas la recette sur les versions du case. Aucun support statique n’est présenté ici comme un test d’écriture déjà exécuté.

## 9. Complément de validation — décision D15, réponse1.A

Contrôle à implémenter, non exécuté : policy observed_cdc_allowed fait partie des règles/empreinte du run. Fixture : version à09h en étape22, à11h en étape24 sans date métier de transition ; puis à12h même étape24 avec simple changement de montant. Attendu : une entrée observée en24 à11h, qualité cdc_transition_proxy, aucune nouvelle entrée à12h. is_event_time_accepted=true sur l'événement observé ; le comptage reste soumis aux autres règles de population/couverture.

Seconde fixture : transition réellement observée vers1 sans date métier, puis passage14 ; première signature datée par meta.ts de la transition vers1, provenance CDC et pas de seconde vente à14. Premier état déjà14 sans1 : aucune date de signature reconstruite. Premier état avancé sans état antérieur : entrée de passage inconnue et absence de durée finale inventée. Les cas de re-signature restent soumis à l'arbitrage distinct G04.

Cette décision ne rend ni les démos réalisées ni le montant signé calculables sans leur preuve. D16 fixe désormais une hypothèse explicite de complétude du case jusqu’à la clôture du30septembre2026 ; les lacunes individuelles restent conservées. Aucun nouveau test dbt ni contrôle ClickHouse n'a été exécuté lors de cet arbitrage documentaire.

## 10. Recette normative v0.2 — arbitrages délégués finalisés

Les anciens G ne nécessitent aucune question à l’utilisateur pendant l’implémentation : appliquer01§7/D16–D30. Les trois documents se lisent ensemble ; les faits d’audit historique ci-dessus ne sont pas réécrits pour faire croire que devise/exhaustivité ont été vérifiées. EUR et clôture du case sont des hypothèses maintenant autorisées par délégation. Les tests ci-dessous sont des tests futurs, pas des exécutions déclarées réussies.

La configuration de recette utilise exactement le YAML de01§7.1, event_time_policy=observed_cdc_allowed et case_as_of_boundary_at=2026-09-30T22:00:00.000Z. Le runner calcule case_history_start_at, fige capture keys/cutoff/rule hash et reconstruit model_run_id après succès des captures. Ce run diffère d’un run v0.1 dont règles/probabilités/couverture diffèrent ; aucune ancienne révision n’est remplacée. Vérifier le jeu vivant avant exécution : si les sources ne correspondent plus à l’extrait décrit, conserver les nouveaux événements sans les faire entrer dans les analyses de fin septembre et signaler l’écart d’extrait.

### 10.1 Contrôles supplémentaires obligatoires

| ID | Objet / scénario | Résultat attendu | Gravité / action |
|---|---|---|---|
| T51 | Couverture de case, première observation tardive et date exactement à la borne | SeptembreParis clôture exclusive ; aucune analyse d’octobre déduite du jour de calcul ; lacunes restentNULL | ERROR si état/événement inventé ; corriger bornes |
| T52 | Devise EUR sous hypothèse de case, montant CRM estimé | MRR actif en EUR calculable si lignes connues ; mensualité commerciale et MRR signé restentnonprouvés | ERROR si EUR rend artificiellement signé/calcul compatible |
| T53 | Dernier barème ref capturé appliqué au passé/types4et7 | Un coefficient par état/segment ; provenance capture réelle conservée ; barème manquantNULL, pas0 ni fallbackBoond | ERROR si fan-out ou histoire source falsifiée |
| T54 | Quatre objectifs et type2 formation | Périmètre4/7 pour chacun ; type2 conservé mais exclu des cibles ; preuve d’unité/tenue contrôlée séparément | ERROR si formation supprimée de l’histoire ou objectif alimenté sans preuve |
| T55 | BU12/13/15 et cibles ES | LA/SMB mappées ; KAM connue sanscible ; ES cible conservée, réaliséNULL ; aucun global complet inventé | ERROR si KAM=ES ou réaliséES=0 sans preuve |
| T56 | Origine à création, origine ultérieure et marketing | Choisir origine du besoin à création observable ; aucune substitution tardive/contactHS ;1/2/3Inbound,4/5Outbound,6–11Other | ERROR si crédit marketing inventé |
| T57 | Codes anciens et statuts | Classification D30 ; aucun vieuxcode assimilé à un jalon moderne ;10/19unknown inclus dans base | ERROR si dossiers cachés/renormalisés |
| T58 | Signé→rouvert→signé et cohorte | Une première signature seulement ; premièretrace1/14nondatable empêche re-signature comptéecomme nouvelle ; tracesconservées ; mêmecohorte et étatàJ courant | ERROR si doublevente ou victoire absorbante dans cohorte |
| T59 | Perdu→réouvert→gagné, cycle | Un seul tempsjusqu’àpremièreissueobservéedatable ; épisodes ultérieurs conservés, pas deux durées mélangées | ERROR si doublecontribution ou date censurée fabriquée |
| T60 | Chemins New/Upsell, sauts/retours et B avantA | Seulement étapes observées ; transition exige Baprès premièreA ; volume de palier peut augmenter ; aucuneétape fictive | ERROR si tunnel forcé ou ordre des codes utilisé |
| T61 | Transfert équipe pendant passage | Filtre sur équipe entrée ; même durée complète et un seul passage ; tranches restent séparées | ERROR si multiplication/réattribution silencieuse |
| T62 | Seuil21 et bornes7/14/30 | Alerte strictement>21 ; classe7 dans[7,14),14dans[14,30),30dans[30,+inf) ; paramètres modifiables | ERROR si trous/troncature ou ancienneté mélangée àdurée finale |
| T63 | Premièreactivation, retour, histoire inconnue | first_proven/return_proven/unknown ; retour exclu premièreacquisition mais inclus entrant etNewMRR | ERROR si premièreobservation=nouveauclient automatique |
| T64 | Familles sans preuve et fonctions non activées | Schémas complets, mesuresNULL/statuts ; aucune table manquante remplacée par une promesse ; pasde zéro surdétailvide | ERROR si données/attributioninventées ou contrat absent |
| T65 | Exécution/rétention | Commandes manuelles, aucune purge ni scheduler installés ; reprises et anciennesrévisions conservées | ERROR si pertehistorique ou altérationdessources |

Ces15contrôles complètent T01–T50. Pour les choix de case, chaque test inclut une fixture d’entrée et une sortie attendue, pas une simple assertion que la configuration répète la valeur du fichier. Les tests d’intégration vérifient également relations, populations, anti-jointures et réconciliation sur le jeu disponible. Le résultat d’une fixture ne devient pas un résultat commercial réel.

### 10.2 Vérification documentaire des arbitrages

Les73 modèles et179 colonnes source restent l’inventaire cible. Aucune nouvelle colonne physique CRM ni nouvelle table source n’est supposée. Les familles M06/M07/BP/U09/U14 non activées restent inventoriées ; démos réalisées/MRR signé/chaînage non prouvés restent indisponibles même si un calcul numérique opportuniste serait possible. Accepter l’implémentation avec ces statuts correctement exposés ; ne pas exiger une invention pour faire passer les tests.

### Q13 — Origines disponibles, contrôle exécuté lors de la préparation du questionnaire interrompu

```sql
WITH d AS (
    SELECT argMax(tuple(`setting.origin`), `meta.ts`) AS v
    FROM raw.dictionaries
    WHERE `meta.language` = 'fr'
)
SELECT JSONExtractInt(origin, 'id') AS origin_id,
       JSONExtractString(origin, 'value') AS origin_label
FROM d
ARRAY JOIN JSONExtractArrayRaw(v.1) AS origin
ORDER BY origin_id;
```

Lecture HTTP readonly=1, limite100lignes,10secondes, réellement exécutée dans le chat. Résultats :1 Formulaire site ;2 LinkedIn Ads ;3 Webinar ;4 Prospection téléphonique ;5 LinkedIn Sales ;6 SDR ;7 Import externe ES ;8 Partenaire ;9 Referral client ;10 Salon ;11 Boucheàoreille. Le regroupement Inbound/Outbound/Other et le choix du champ relèvent de D24, pas d’une propriété supposée du JSON ou des données fictives des maquettes. Aucune donnée nominative n’est reproduite.
