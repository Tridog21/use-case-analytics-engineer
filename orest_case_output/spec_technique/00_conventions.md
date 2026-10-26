# Étape 0 — Conventions techniques

**Référence pour ce case, définie par l’utilisateur à l’échange 26 et complétée à l’échange 28.** Ce document remplace le précédent canevas. Il se limite aux règles ci-dessous ; les définitions métier restent dans le [clean intent](../clean_intent/intent_ia.md).

## 1. Nommage des modèles et des schémas

| Objet | Nom du modèle / de la table | Préfixe du schéma |
| --- | --- | --- |
| Staging | `stg_<nom>` | `stg_` |
| Intermédiaire | `int_<regle_metier_objet>` | `dwh_` |
| Fait | `fct_<nom>` | `dtm_` |
| Dimension | `dim_<nom>` | `dtm_` |
| Table DTR | `dtr_<nom>` | `dtr_` |
| Dataset directement consommé par le dashboard | `dataset_<nom>` | `dtr_` |

Le libellé utilisateur « dataset » est écrit `dataset_<nom>` pour former les noms. Les suffixes des schémas seront précisés avec les modèles ; aucun schéma supplémentaire n’est imposé ici.

## 2. Nommage des colonnes

| Nature de la colonne | Convention | Exemple |
| --- | --- | --- |
| Colonne reprise de la source dans le staging | Préfixe `src_` | `created_at` → `src_created_at` |
| Colonne ajoutée dans le staging | Sans préfixe `src_` | `imported_at` |
| Booléen | Préfixe `is_`, `has_` ou `was_` | `is_active`, `has_demo`, `was_deleted` |
| Timestamp | Suffixe `_at` | `created_at`, `deleted_at` |
| Date | Suffixe `_date` | `closing_date` |
| Résultat d’un comptage | Préfixe `nb_` | `nb_demos` |
| Résultat d’une somme | Préfixe `sum_` | `sum_mrr` |
| Ratio | Suffixe `_rate` ou `_ratio` | `conversion_rate` |

Dans le staging, `src_` identifie l’origine et vient devant le nom : une colonne source `is_active` devient `src_is_active`. Les marqueurs de type s’apprécient après ce préfixe. Les correspondances avec les noms sources sont documentées ; une colonne ajoutée ne reçoit jamais `src_`.

## 3. Staging et modélisation

- **Une table source correspond à un staging, en reprise 1 pour 1** : conserver ses colonnes et son niveau de détail. Ce principe reste compatible avec le chargement incrémental et la conservation des versions déjà définis ; il ne signifie pas sélectionner uniquement le dernier état.
- **Aucune règle métier dans le staging.** Seules les adaptations de format, de type et de présentation technique sont autorisées, sans changement de sens métier. Les colonnes techniques ajoutées restent identifiables.
- Autant que possible, **une règle métier par fichier intermédiaire**, nommé `int_<regle_metier_objet>`, pour localiser et corriger facilement cette règle.
- Concevoir les `fct_` et `dim_` pour le **self-service des métiers** : grain compréhensible, champs explicites et relations faciles à utiliser.

## 4. SQL et dbt

- **Jamais de `SELECT *`**, y compris `alias.*`. Énumérer les colonnes nécessaires.
- **Éviter les fonctions dans les clauses `WHERE`.** Préparer les conversions, normalisations et bornes en amont, puis comparer directement les colonnes aux valeurs préparées. Ne pas appliquer une fonction à la colonne filtrée pour reconstruire la période.
- **Pas de tables temporaires écrites manuellement** dans les modèles du case.
- Un fichier de modèle SQL dbt contient **une requête `SELECT`**, éventuellement avec des CTE et du Jinja. **Pas de `DROP`, `CREATE` ou `INSERT` manuels** : dbt gère la matérialisation. Il s’agit d’une convention de rédaction des modèles, pas d’une interdiction de ces opérations internes à dbt.
- Référencer les sources avec **`{{ source('source', 'table') }}`** et les modèles avec **`{{ ref('nom_modele') }}`**. Ne jamais coder les noms physiques de tables ou de schémas en dur dans les appels SQL. Pour relire la cible d’un incrémental, utiliser `{{ this }}`.
- Autant que possible, **ne pas coder les valeurs de filtrage en dur** dans les `WHERE` : utiliser les paramètres ou référentiels appropriés.
- Chaque modèle incrémental comporte sa **condition Jinja `{% if is_incremental() %}`** pour appliquer le filtre de reprise. Le SQL doit également fonctionner au premier chargement, quand cette condition est fausse.
- Les commentaires expliquent **ce que fait le code ou la logique métier**. Aucune référence à l’IA, aux auteurs du code, aux personnes ou aux numéros de tickets.

La fonction dbt s’écrit `source()` au singulier ; `sources:` est le nom de la section YAML. [Référence dbt](https://docs.getdbt.com/reference/dbt-jinja-functions/source). Le fonctionnement de `is_incremental()` est décrit dans la [documentation des modèles incrémentaux](https://docs.getdbt.com/docs/build/incremental-models).

## 5. Tests et documentation dbt

- Prévoir **par défaut les tests nécessaires à chaque modèle**, notamment l’unicité et l’absence de doublons **au grain de la table**. Une table historisée se teste sur sa clé de version, pas sur l’identifiant métier seul.
- Dans le vocabulaire dbt, les contrôles `unique` et de doublons sont des **tests de données**. Les **tests unitaires** vérifient une logique de transformation sur des entrées et sorties attendues ; les prévoir lorsque cette logique le nécessite. [Référence dbt sur les tests](https://docs.getdbt.com/docs/build/data-tests).
- **Chaque table et chaque colonne sont décrites dans la configuration YAML dbt**, via `description`.
- La description d’une table rend explicites **son objectif, son fonctionnement, sa granularité et son mode/fréquence de rafraîchissement**. Une fréquence non décidée doit être indiquée comme telle, sans inventer un rafraîchissement quotidien.
- La description d’une colonne précise **son rôle, les valeurs possibles et, si nécessaire, les particularités techniques de son calcul**.

## 6. Huit conventions complémentaires

1. **Noms homogènes.** Écrire les noms techniques en anglais et en `snake_case`. Utiliser `_id` pour un identifiant métier/source et `_key` pour une clé technique du modèle : `company_id`, `company_version_key`. Conserver la correspondance avec les noms sources et les règles `src_` du staging.

2. **Jointures maîtrisées.** Déclarer la relation attendue de chaque jointure : un-à-un, plusieurs-à-un, etc. Vérifier son effet sur les lignes et les montants. Joindre trois contacts à une opportunité ne doit pas tripler son montant. Ni `DISTINCT` ni `GROUP BY` ne doivent masquer une jointure incorrecte.

3. **Périodes historiques cohérentes.** Pour les modèles représentant des périodes, utiliser `valid_from_at` inclus et `valid_to_at` exclu. Distinguer date métier, publication CDC et import. Définir explicitement le fuseau utilisé pour les clôtures ; cette convention ne choisit pas encore sa valeur. Ne pas imposer des colonnes de période à un modèle qui représente des événements.

4. **Valeur inconnue distincte de zéro.** `NULL` représente une valeur inconnue ou non renseignée ; `0` représente une valeur connue égale à zéro. Ne pas remplacer automatiquement les valeurs manquantes par zéro. Un ratio dont le dénominateur est nul ou inconnu ne devient pas automatiquement `0 %`.

5. **Montants décimaux.** Privilégier `Decimal` pour les montants financiers calculés. Définir la précision et la règle d’arrondi ; éviter les arrondis successifs dans les intermédiaires. Le type exact sera choisi selon les montants et calculs attendus. [Documentation ClickHouse](https://clickhouse.com/docs/reference/data-types/decimal).

6. **Agrégations explicites pour le self-service.** Documenter comment chaque mesure peut être regroupée. Un MRR de clôture ne se somme pas entre plusieurs mois. Un nombre distinct de sociétés ne s’additionne pas forcément entre équipes. Un taux global se recalcule depuis ses numérateurs et dénominateurs, plutôt que par moyenne des taux locaux.

7. **Performance justifiée par les usages.** Choisir vue, table ou incrémental selon le besoin. Pour une table ClickHouse, choisir la clé de tri physique `ORDER BY` selon les filtres et lectures fréquents. Vérifier le plan, les lignes/octets lus et le temps d’exécution avant de conclure à un gain et d’optimiser davantage ; aucun benchmark n’est lancé par la seule adoption de cette règle. [Clés de tri ClickHouse](https://clickhouse.com/docs/concepts/best-practices/choosing-a-primary-key).

8. **Pas de `DISTINCT` sauf nécessité justifiée.** Privilégier `GROUP BY` lorsque le regroupement produit le résultat attendu au bon grain. Documenter tout recours nécessaire à `DISTINCT`. Ne pas remplacer un comptage distinct par un simple comptage de lignes sans avoir obtenu une ligne par identité concernée. La préférence pour `GROUP BY` est une convention du projet visant la performance, **pas une garantie qu’il soit toujours plus rapide** : comparer les comportements à résultat équivalent si nécessaire. ClickHouse documente des différences d’exécution entre les deux formes, notamment avec `LIMIT`. [DISTINCT et alternatives](https://clickhouse.com/docs/reference/statements/select/distinct#alternatives).

Ces conventions s’appliquent à la rédaction des spécifications et du code. Elles n’ajoutent aucune règle métier aux KPI. Messages utilisateur : [règles initiales](../clean_intent/ia_assistant_story.md#echange-26) et [compléments adoptés](../clean_intent/ia_assistant_story.md#echange-28).
