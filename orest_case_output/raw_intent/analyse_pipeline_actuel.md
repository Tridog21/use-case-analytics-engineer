# Analyse de la requête actuelle de pipeline

Cette analyse explicite ce que la requête calcule, les limites de lecture des chiffres et les décisions métier à clarifier. Elle sert au cadrage de l'intention. Elle ne fixe pas les modèles de la future solution et ne valide pas les définitions actuelles comme définitions cibles.

**Constat principal :** la requête produit, par semaine et par équipe, des nombres de besoins observés dans certains états et des montants moyens issus de lignes journalières. Ses colonnes de signatures ne mesurent pas des signatures nouvelles sur la période. Aucune formule explicite de MRR, de conversion ou de pipeline pondéré n'y est définie. Cette lecture du calcul doit être distinguée de son résultat effectif, qui dépend aussi des jointures, des données et des réglages ClickHouse détaillés plus bas.

Source principale : [requête complète, lignes 1–69](../../legacy/pipeline_actuel.sql).

## 1. Périmètre de lecture et niveaux de preuve

Les constats sont classés selon leur origine :

- **Code vérifié :** règle directement lisible dans le SQL ou le schéma fourni.
- **Information documentée :** sens d'un champ ou besoin décrit dans le README ou le modèle ; cela prouve ce qui est documenté, sans garantir la qualité de chaque valeur.
- **Observation du corpus hors ligne :** ligne présente dans `window.MODEL_DATA`, embarqué dans `docs/model/model.js`. Ce contenu n'a pas été comparé aux fichiers Parquet ni à une base ClickHouse chargée.
- **Risque conditionnel :** conséquence qui dépend de données particulières, de doublons, de l'historique disponible ou de réglages du moteur.
- **Hypothèse d'intention :** interprétation plausible du besoin, qui reste à faire valider par les métiers.

La documentation indique une photographie au **30/09/2026** ; `today()` reste pourtant la date du moteur au moment où la requête est exécutée. Ce sont deux notions différentes. Sources : [modèle, ligne 3](../../docs/model/model.json) et [SQL, lignes 5–8](../../legacy/pipeline_actuel.sql).

| Source locale | Utilisation et repères |
|---|---|
| [legacy/pipeline_actuel.sql](../../legacy/pipeline_actuel.sql) | Code intégral analysé : lignes 1–69. |
| [README.md](../../README.md) | Contexte et équipes : 28–34 ; définitions contradictoires : 49–63 ; usage et lenteur de la requête : 72 ; conventions CDC : 122–126. |
| [docs/model/model.json](../../docs/model/model.json) | Opportunités : 19–207 ; équipes : 692–756 ; étapes : 914–917 ; abonnements : 1078–1177 ; HubSpot : 1293–1410 ; objectifs et probabilités : 1415–1487. |
| [docs/model/model.js](../../docs/model/model.js) | Ligne 1 : contenu déclaré comme documentation et lignes brutes ; ligne 3 : `window.MODEL_DATA`. Les chemins JSON précis figurent dans les observations ci-dessous. |
| [docker/init/01_schema.sql](../../docker/init/01_schema.sql) | Opportunités : 7–36 ; business units : 118–130 ; objectifs et probabilités : 257–274. |
| [docker-compose.yml](../../docker-compose.yml) | Ligne 3 : image ClickHouse déclarée en version 25.11. |
| [docs/besoin/expression-de-besoin.md](../../docs/besoin/expression-de-besoin.md) | Ancienneté dans le stage, cohortes et pipeline pondéré : 9–16 ; dispositif provisoire : 20. |

**Méthode :** lecture statique des fichiers, examen ciblé des exemples hors ligne et vérification de la documentation officielle ClickHouse. Aucune requête exécutée dans ClickHouse, aucun service lancé, aucune correction du SQL et aucun benchmark.

## 2. Code original intégral

Le bloc suivant reproduit l'intégralité de `legacy/pipeline_actuel.sql`, sans modification ni numéros ajoutés. Les numéros cités dans l'analyse se rapportent au fichier source.

```sql
-- Pipe commercial par semaine et par équipe : deals en cours, montant du pipe, signatures.
-- Requête historique de l'équipe sales, lancée avant chaque point pipe du lundi.

WITH
    days AS (
        SELECT toDate('2024-01-01') + number AS day
        FROM numbers(dateDiff('day', toDate('2024-01-01'), today()) + 1)
    ),

    versions AS (
        SELECT
            o.id,
            o.`meta.ts`                             AS valid_from,
            o.state,
            o.turnoverEstimatedExcludingTax         AS amount,
            o.`relationships.mainManager.data.id`   AS manager_id
        FROM raw.opportunities AS o
        WHERE o.`meta.deleted` = 0
          AND o.typeOf = 4
          AND o.creationDate >= '2024-01-01'
    ),

    intervals AS (
        SELECT
            v.id,
            v.valid_from,
            any(v.state)        AS state,
            any(v.amount)       AS amount,
            any(v.manager_id)   AS manager_id,
            minOrNull(n.valid_from) AS valid_to
        FROM versions AS v
        LEFT JOIN versions AS n ON n.id = v.id AND n.valid_from > v.valid_from
        GROUP BY v.id, v.valid_from
    ),

    teams AS (
        SELECT
            JSONExtractInt(member, 'id')    AS manager_id,
            replaceOne(bu.name, 'Team BA - ', '') AS team
        FROM raw.businessunits AS bu
        ARRAY JOIN JSONExtractArrayRaw(bu.`relationships.includedManagers.data`) AS member
        WHERE bu.name LIKE 'Team BA%'
    ),

    daily AS (
        SELECT
            d.day,
            i.id,
            i.state,
            i.amount,
            t.team
        FROM days AS d
        CROSS JOIN intervals AS i
        LEFT JOIN teams AS t ON t.manager_id = i.manager_id
        WHERE d.day >= toDate(i.valid_from)
          AND (i.valid_to IS NULL OR d.day < toDate(i.valid_to))
    )

SELECT
    toMonday(day)                                                   AS week,
    ifNull(team, 'Autre')                                           AS team,
    uniqExactIf(id, state IN (0, 20, 21, 22, 23, 24, 25, 26, 28))   AS open_deals,
    sumIf(amount, state IN (0, 20, 21, 22, 23, 24, 25, 26, 28))
        / uniqExact(day)                                            AS pipe_amount,
    uniqExactIf(id, state = 1)                                      AS signed_deals,
    sumIf(amount, state = 1) / uniqExact(day)                       AS signed_amount
FROM daily
GROUP BY week, team
ORDER BY week DESC, team
```

## 3. Décomposition détaillée

### 3.1. Contexte déclaré par les commentaires

Les deux premières lignes annoncent un « pipe commercial par semaine et par équipe » et une requête lancée avant le point pipe du lundi. Le README confirme son utilisation actuelle par les Sales et le fait que sa signification n'est plus bien comprise. Cela documente son usage ; cela ne garantit pas que ses formules répondent à l'attente des utilisateurs.

Sources : [SQL, lignes 1–2](../../legacy/pipeline_actuel.sql) ; [README, ligne 72](../../README.md).

### 3.2. `days` — le calendrier d'observation

**Code vérifié.** Le calendrier commence au 01/01/2024 et se termine au jour d'exécution inclus. Le `+ 1` inclut la date courante. Aucun paramètre métier de période n'est exposé dans cette requête.

**Sens du grain.** Une ligne de ce bloc représente un jour civil, avant tout lien avec un besoin ou une équipe.

**Conséquences pour la lecture :**

- La borne basse est fixe ; elle ne signifie pas « conserver les deux dernières années ».
- La semaine courante peut être incomplète et le jour courant peut être en cours.
- Le calendrier ne s'arrête pas à la date maximale de données effectivement reçues. La fiabilité d'une projection jusqu'à aujourd'hui dépend de la fraîcheur du corpus et du traitement de la dernière version.
- Un calendrier complet en amont ne garantit pas que tous ses jours restent présents après les filtres de `daily`.

Source : [SQL, lignes 5–8](../../legacy/pipeline_actuel.sql). La différence entre date documentaire et date d'exécution est présentée en section 1.

### 3.3. `versions` — les versions de besoins éligibles

**Code vérifié.** Le bloc lit `raw.opportunities`, conserve `id`, l'horodatage CDC, l'état, le montant et le responsable, puis applique simultanément trois filtres : version non supprimée, type de besoin `4`, création du besoin à partir du 01/01/2024.

| Élément | Règle présente | Sens et limite |
|---|---|---|
| `id` | Identifiant du besoin. | On compte un besoin/opportunité, pas une personne ou une société. |
| `valid_from` | `meta.ts`. | Début d'observation de la version dans le flux CDC. |
| `state` | État de cette version. | L'état est saisi dans Boond ; sa signification vient du référentiel. |
| `amount` | `turnoverEstimatedExcludingTax`. | Montant estimé HT, sans conversion en MRR ni normalisation temporelle explicite. |
| `manager_id` | Responsable de cette version. | Il peut changer avec les versions ; l'équipe est rejointe plus tard. |
| `meta.deleted = 0` | Retire les versions de suppression. | Les événements supprimés ne peuvent plus fermer un intervalle dans le bloc suivant. |
| `typeOf = 4` | Conserve un seul type. | Le référentiel hors ligne le libelle « New Client Boond » ; tous les types de besoins ne sont pas couverts. |
| `creationDate >= '2024-01-01'` | Filtre la création de l'objet. | Un besoin créé avant 2024 est exclu même s'il est encore ouvert pendant la période analysée. |

Sources du code : [SQL, lignes 10–21](../../legacy/pipeline_actuel.sql). Sens des champs : [modèle, lignes 25–58](../../docs/model/model.json), [78–111](../../docs/model/model.json) et [149–156](../../docs/model/model.json). Référentiel du type : [model.js, ligne 3](../../docs/model/model.js), chemin précisé en section 5.2.

**Distinction sur le temps.** La documentation définit `meta.ts` comme le moment de publication d'une modification par le flux CDC. Elle définit séparément `creationDate`, `updateDate` et `closingDate`. Employer `meta.ts` ne prouve pas que l'on connaît la date métier exacte de chaque événement. La requête ne consulte pas `closingDate` pour reconnaître une signature.

Sources : [modèle, lignes 38–41](../../docs/model/model.json), [78–105](../../docs/model/model.json) ; [SQL, lignes 11–20](../../legacy/pipeline_actuel.sql).

### 3.4. `intervals` — la recherche de la version suivante

**Logique statique.** Chaque version `v` est jointe à toutes les versions `n` du même besoin ayant un `valid_from` strictement supérieur. Le minimum de ces timestamps est utilisé comme fin d'intervalle. Le regroupement se fait sur `(v.id, v.valid_from)`.

**Intention probable, à distinguer du résultat moteur :** considérer qu'une version reste valable jusqu'à la version suivante et que la dernière reste valable sans date de fin. Le nom `valid_to`, le `minOrNull` et le test ultérieur `valid_to IS NULL` soutiennent cette interprétation. La gestion effective de cette dernière version est cependant fragile sous les réglages ClickHouse détaillés en section 5.3.

Source : [SQL, lignes 23–34](../../legacy/pipeline_actuel.sql) et [55–56](../../legacy/pipeline_actuel.sql).

**Ce qui est regroupé.** Il s'agit de versions d'enregistrement, pas uniquement de changements de stage. Une modification de montant ou de responsable peut créer une version supplémentaire sans changement d'état. Le bloc ne teste jamais `state précédent != state suivant`. Un début de version n'est donc pas automatiquement un début de séjour dans le stage.

Sources : [README, lignes 122–126](../../README.md) ; [SQL, lignes 11–16](../../legacy/pipeline_actuel.sql), [30–33](../../legacy/pipeline_actuel.sql).

**Rôle de `any`.** Les trois expressions `any(v.state)`, `any(v.amount)` et `any(v.manager_id)` récupèrent ces attributs après regroupement. Si une seule valeur cohérente existe par `(id, meta.ts)`, les répétitions créées par la jointure n'introduisent pas à elles seules d'ambiguïté sur ces attributs. Si plusieurs lignes contradictoires partagent exactement cette clé, `any` ne définit aucun arbitrage métier : chaque colonne peut être choisie séparément et les NULL sont ignorés en présence de valeurs non nulles. Ce risque est conditionnel : aucun doublon contradictoire n'a été recherché exhaustivement.

Sources : [SQL, lignes 27–33](../../legacy/pipeline_actuel.sql) ; [documentation officielle de `any`, version 25.11](https://raw.githubusercontent.com/ClickHouse/ClickHouse/v25.11.1.558-stable/docs/en/sql-reference/aggregate-functions/reference/any.md), lignes 9–16 et 35–41.

**Suppressions et sorties de périmètre.** Puisque la jointure se fait sur `versions`, tout événement retiré par les filtres amont est absent des bornes : suppression, éventuelle version passée dans un autre type ou avec une création hors filtre. Une borne logique manque alors à la reconstitution. Cela ne prouve pas, à lui seul, qu'un deal supprimé apparaît dans les résultats : il faut aussi tenir compte du traitement de la dernière version par le moteur.

Source : [SQL, lignes 17–20](../../legacy/pipeline_actuel.sql), [30–32](../../legacy/pipeline_actuel.sql).

### 3.5. `teams` — le référentiel d'équipes reconstruit

**Code vérifié.** Le bloc conserve les business units dont le nom commence par `Team BA`, déplie leur tableau JSON de membres, extrait les identifiants de responsables et retire le préfixe `Team BA - ` du nom affiché.

**Ce que le code ne fait pas :** sélectionner la dernière version d'une business unit, choisir la version valable au jour observé, retirer ses versions supprimées, dédoublonner `(manager_id, team)` ou retrouver l'Espagne à partir de l'agence. Les données brutes sont pourtant versionnées, y compris les équipes.

Sources : [SQL, lignes 36–43](../../legacy/pipeline_actuel.sql) ; [modèle, lignes 692–739](../../docs/model/model.json) ; [schéma, lignes 118–130](../../docker/init/01_schema.sql).

Le grain obtenu est **une occurrence de membre par version de business unit retenue**, et non nécessairement une ligne unique par responsable. L'exemple hors ligne du membre `3006` démontre trois occurrences dans LA ; le cas `3005` démontre que les appartenances de périodes différentes peuvent être mélangées. Ils sont détaillés en section 5.2.

**Conséquence métier conditionnelle.** Sous une jointure `ALL`, les montants peuvent être multipliés et un même besoin peut être attribué à plusieurs équipes. Les compteurs distincts ne sont pas multipliés dans une même équipe, mais peuvent apparaître dans plusieurs équipes. Un total obtenu en additionnant les équipes ne constitue alors pas nécessairement un total de besoins uniques.

Sources : [SQL, ligne 54](../../legacy/pipeline_actuel.sql), [62–68](../../legacy/pipeline_actuel.sql) ; réglage de strictness expliqué en section 5.3.

### 3.6. `daily` — la projection des versions sur des jours

**Logique statique.** Le bloc combine le calendrier et les intervalles, rattache chaque intervalle aux équipes de son responsable, puis conserve les jours vérifiant :

- `day >= toDate(valid_from)` ;
- `valid_to` absent, ou `day < toDate(valid_to)`.

Source : [SQL, lignes 45–57](../../legacy/pipeline_actuel.sql).

**Grain visé :** un besoin par jour, avec son état, son montant et son équipe. **Grain garanti par le code :** une ligne par combinaison jour × intervalle retenu × correspondance d'équipe. L'unicité `(jour, besoin)` n'est pas assurée par une contrainte ou un dédoublonnage de ce bloc.

**Perte des heures.** Les timestamps sont convertis en dates avant comparaison. Si une version débute et se termine le même jour, elle ne peut satisfaire les deux bornes. Une étape traversée uniquement entre deux mises à jour du même jour disparaît de la vue journalière.

**Exemple fictif :** un besoin est ouvert lundi à 09 h, passe à l'état `1` lundi à 16 h, puis reçoit une autre version mardi. La version ouverte du lundi a une fin le lundi : elle n'est retenue pour aucun jour. La version à l'état `1` peut être affectée au lundi entier. Cet exemple décrit la logique de troncature ; ce n'est pas un cas mesuré dans les données et il ne lève pas le risque sur les intervalles terminaux.

Source : [SQL, lignes 55–56](../../legacy/pipeline_actuel.sql).

**Interprétation prudente.** Dans un historique complet et cohérent, hors problèmes d'intervalle terminal, cette projection tend à retenir le dernier état observé d'une journée. Elle ne mesure pas le temps exact passé dans chaque état au cours de cette journée. Pour aujourd'hui, il s'agit au mieux du dernier état disponible au moment de l'exécution, pas d'une fin de journée future déjà connue.

**Jours manquants.** Un jour sans aucune ligne éligible dans une équipe disparaît du groupe. À l'inverse, un jour comportant uniquement des besoins dans d'autres états peut rester présent dans le dénominateur des montants. Il n'existe pas de grille finale exhaustive semaine × équipe contenant explicitement tous les zéros.

Sources : [SQL, lignes 52–56](../../legacy/pipeline_actuel.sql), [63–68](../../legacy/pipeline_actuel.sql).

### 3.7. Agrégation finale — une ligne par semaine et équipe

`toMonday(day)` donne le lundi de rattachement. Toutes les lignes de la semaine représentées dans `daily` contribuent au groupe : le SQL ne filtre pas les seuls lundis. Il applique ensuite quatre calculs différents.

Source : [SQL, lignes 59–69](../../legacy/pipeline_actuel.sql).

**Nombre de besoins ouverts (`open_deals`).** Il s'agit du nombre d'identifiants distincts ayant au moins une ligne journalière dans la liste d'états ouverts codée en dur. Un besoin ouvert seulement une partie de la semaine compte une fois. Un besoin fermé avant la fin de la semaine peut quand même compter comme ouvert dans cette semaine. Cette mesure n'est pas une photo au lundi, une photo de fin de semaine ni une moyenne de nombre de deals.

Source : [SQL, ligne 62](../../legacy/pipeline_actuel.sql).

**Montant du pipe (`pipe_amount`).** Le numérateur additionne les montants de toutes les lignes journalières dont l'état est dans cette liste. Le dénominateur compte les jours distincts du groupe semaine-équipe, tous états confondus. Sans duplication de lignes et avec un montant correctement renseigné, cela se lit comme un montant moyen de pipe sur les jours représentés. Ces conditions ne sont pas garanties par la requête.

Source : [SQL, lignes 63–64](../../legacy/pipeline_actuel.sql).

**Nombre de besoins signés (`signed_deals`).** Le critère est seulement `state = 1`. Aucune condition ne vérifie que l'entrée dans cet état a eu lieu pendant la semaine. Si un besoin reste observé dans cet état pendant plusieurs semaines, il peut compter une fois dans chacune. Un passage vers l'état `14` cesse de satisfaire le critère, même si cet état est également libellé « Signé » dans le référentiel hors ligne.

Sources : [SQL, ligne 65](../../legacy/pipeline_actuel.sql) ; [model.js, ligne 3](../../docs/model/model.js), chemin des étapes en section 5.2. La persistance d'une dernière version reste dépendante du moteur.

**Montant signé (`signed_amount`).** Même principe que le pipe : addition des montants journaliers à l'état `1`, divisée par les jours représentés dans le groupe. Cela ne verrouille ni le montant au premier passage signé ni la date d'une signature nouvelle. Une modification ultérieure de montant, si l'état reste `1` et si les versions sont retenues, peut modifier le montant observé.

Sources : [SQL, ligne 15](../../legacy/pipeline_actuel.sql), [27–30](../../legacy/pipeline_actuel.sql) et [66](../../legacy/pipeline_actuel.sql).

**Exemples fictifs de lecture des montants :**

| Situation simplifiée, sans doublons ni valeurs manquantes | Lecture du résultat |
|---|---|
| Un besoin ouvert à 100 € est présent les sept jours. | `open_deals = 1` et `pipe_amount = 100 €`. |
| Ce besoin est ouvert deux jours ; les cinq autres jours du groupe restent représentés par des états fermés. | `open_deals = 1` et `pipe_amount = 200 / 7`, soit environ 28,57 €. |
| Seuls deux jours existent dans `daily` pour l'équipe, tous deux ouverts à 100 €. | `open_deals = 1` et `pipe_amount = 200 / 2 = 100 €` : les cinq jours absents ne deviennent pas des zéros. |
| Une ligne journalière de 100 € est jointe trois fois à la même équipe. | Le numérateur vaut 300 € pour ce jour ; les distincts `day` et `id` restent chacun à un. |

Ces exemples illustrent les formules, sans annoncer des résultats mesurés. Source : [SQL, lignes 62–66](../../legacy/pipeline_actuel.sql).

## 4. Synthèse 1 — KPI, granularités, périodes, dénominateurs et populations

### 4.1. Contrat de lecture des quatre colonnes

| Colonne | Ce qui est compté ou additionné | Dénominateur | Lecture métier justifiée par le code |
|---|---|---|---|
| `open_deals` | Besoins distincts observés ouverts au moins un jour de la semaine. | Aucun. | Présence dans le pipe au cours des jours observés de la semaine. |
| `pipe_amount` | Montants de toutes les lignes journalières dans les états ouverts listés. | Jours distincts présents, tous états confondus, dans la semaine-équipe. | Moyenne de montants journaliers représentés, sous réserve d'absence de duplication et de données suffisantes. |
| `signed_deals` | Besoins distincts observés à l'état `1` au moins un jour. | Aucun. | Présence dans cet état pendant la semaine, sans date d'entrée requise. |
| `signed_amount` | Montants de toutes les lignes journalières à l'état `1`. | Les mêmes jours présents du groupe, pas uniquement les jours signés. | Montant moyen observé dans cet état, sans calcul de signatures nouvelles. |

Source : [SQL, lignes 62–68](../../legacy/pipeline_actuel.sql).

### 4.2. Population et temps

| Dimension | Règle actuelle | Ce qu'elle ne permet pas de conclure |
|---|---|---|
| Unité de compte | Identifiant d'opportunité Boond. | Ce n'est pas un nombre de personnes, de sociétés ou de contacts uniques. |
| Type de besoin | `typeOf = 4`, libellé « New Client Boond » dans le corpus documentaire. | Aucune couverture démontrée des autres types, dont upsell ou formation. |
| Création | Besoins créés depuis le 01/01/2024. | Les besoins antérieurs encore ouverts ne sont pas repris. |
| Calendrier | Du 01/01/2024 au jour d'exécution inclus. | Aucune politique de conservation n'est formulée et aucune fraîcheur n'est garantie par ce calendrier. |
| Temps d'observation | `meta.ts`, publication CDC de chaque version. | Pas une preuve automatique de la date métier exacte de passage dans un stage. |
| Projection | Jour civil après troncature des heures. | Pas de mesure des passages et durées à l'intérieur d'une journée. |
| Restitution | Semaine rattachée au lundi × équipe. | Pas une photo prise seulement le lundi. |
| Équipe | Appartenance du responsable dans toutes les versions BA correspondantes. | Pas une appartenance historique unique et datée garantie. |
| Population ouverte | États `(0,20,21,22,23,24,25,26,28)`. | Pas une lecture dynamique du référentiel `active`. |
| Population signée | État `1` seulement. | Pas l'ensemble des états libellés signés dans le référentiel documentaire. |

Sources : [SQL, lignes 5–20](../../legacy/pipeline_actuel.sql), [36–68](../../legacy/pipeline_actuel.sql) ; [modèle, lignes 38–58](../../docs/model/model.json) ; [model.js, ligne 3](../../docs/model/model.js), chemins détaillés en section 5.2.

### 4.3. Stock, présence et flux : des mesures différentes

Une **photo de stock** répond à « combien de besoins sont ouverts à une date précise ? ». Un **flux** répond à « combien sont entrés ou sortis pendant la période ? ». Un **nombre de présences sur une période** répond à « combien de besoins ont été observés dans cet état au moins une fois ? ».

Le SQL produit cette troisième lecture pour ses nombres distincts et une moyenne de stocks journaliers pour ses montants. Le rapprochement direct entre les deux peut tromper : le nombre de deals ouverts n'est pas calculé au même instant que le montant affiché, puisqu'aucun instant unique n'est choisi.

Un besoin peut compter à la fois dans `open_deals` et `signed_deals` au cours d'une même semaine. Il peut être recompté les semaines suivantes, ou contribuer à plusieurs équipes en cas de changement de responsable ou d'appartenance multiple. Les nombres distincts **ne sont pas additifs entre semaines ni nécessairement entre équipes**. On ne peut pas additionner librement semaines, états ou équipes pour obtenir un nombre unique de besoins.

Sources : [SQL, lignes 49–56](../../legacy/pipeline_actuel.sql), [62–68](../../legacy/pipeline_actuel.sql). Ces conclusions décrivent les règles d'agrégation ; leur amplitude réelle n'a pas été mesurée.

### 4.4. MRR et pondération : ce qui est disponible dans le calcul

**Le champ utilisé est documenté comme montant estimé HT.** Son caractère mensuel, récurrent, contractualisé ou facturé n'est pas défini par cette requête. Aucun calcul ne le convertit en revenu récurrent mensuel et le code ne compare pas Boond à HubSpot.

Le modèle documente séparément les lignes d'abonnement et précise que le champ `averageDailyPriceExcludingTax` y contient, dans ce contexte, le prix mensuel, avec quantité et prix unitaire dans `attributes`. Cette information aide à poser la question du MRR recherché ; elle ne permet pas de décider seule qu'une définition d'abonnement doit remplacer un objectif de nouvelles ventes.

Sources : [SQL, lignes 15–17](../../legacy/pipeline_actuel.sql) ; [modèle, lignes 108–111](../../docs/model/model.json), [1078–1082](../../docs/model/model.json), [1133–1148](../../docs/model/model.json), [1174–1177](../../docs/model/model.json) ; [README, lignes 53–55](../../README.md).

**Le montant n'est pas pondéré.** Les champs de pondération des besoins et les probabilités par stage et segment existent dans le modèle documentaire, mais ne sont pas utilisés. Les objectifs mensuels ne sont pas rejoints non plus. La requête ne calcule donc ni pipe pondéré ni réalisation d'objectif.

Sources : [SQL complet](../../legacy/pipeline_actuel.sql) ; [modèle, lignes 114–123](../../docs/model/model.json), [1415–1487](../../docs/model/model.json).

## 5. Synthèse 2 — erreurs, limites prouvées et risques conditionnels

### 5.1. Constats certains du code et limites d'usage

| Constat vérifié | Conséquence démontrable ou limite à ne pas dépasser | Source |
|---|---|---|
| Les signatures ne sont pas filtrées par date d'entrée dans l'état. | `signed_deals` ne constitue pas un nombre de signatures nouvelles hebdomadaires. | [SQL, L65–L66](../../legacy/pipeline_actuel.sql). |
| Le critère signé est seulement `state = 1`. | L'état `14` est absent ; son importance métier est corroborée par le référentiel documentaire, pas arbitrée par le SQL. | [SQL, L65–L66](../../legacy/pipeline_actuel.sql) et section 5.2. |
| Les états ouverts sont codés en dur. | Les anciens états `30–35` ne contribuent jamais au pipe ouvert calculé. | [SQL, L62–L64](../../legacy/pipeline_actuel.sql) et section 5.2. |
| La création du besoin est filtrée depuis 2024. | Les besoins plus anciens sont exclus, même pendant une période ultérieure. À distinguer d'un filtre d'affichage. | [SQL, L20](../../legacy/pipeline_actuel.sql). |
| Les suppressions sont retirées avant recherche des versions suivantes. | Elles ne ferment pas les intervalles ; le devenir final dépend aussi du traitement des versions terminales. | [SQL, L18 et L30–L32](../../legacy/pipeline_actuel.sql). |
| Toutes les versions des équipes BA sont lues. | Aucune unicité ni validité historique de l'appartenance n'est garantie. | [SQL, L36–L42](../../legacy/pipeline_actuel.sql). |
| Les dates sont tronquées au jour. | Certains passages intrajournaliers disparaissent ; les durées exactes ne sont pas préservées. | [SQL, L55–L56](../../legacy/pipeline_actuel.sql). |
| Le dénominateur est `uniqExact(day)` dans le groupe présent. | Il varie selon les jours conservés ; les jours absents ne valent pas automatiquement zéro. | [SQL, L63–L66](../../legacy/pipeline_actuel.sql). |
| Les dates de closing, raisons de perte, actions et contacts ne sont pas analysés. | Pas d'analyse des démos, de la conversion du cycle complet, des raisons de perte ou des durées par étape. | [SQL complet](../../legacy/pipeline_actuel.sql). |
| Aucun indicateur de complétude du montant n'est fourni. | Un nombre de deals ne prouve pas que tous leurs montants sont renseignés ; l'ampleur des montants manquants n'a pas été mesurée. | [SQL, L15 et L62–L66](../../legacy/pipeline_actuel.sql) ; [schéma, L22](../../docker/init/01_schema.sql). |
| Le taux de change n'est pas utilisé. | Aucune normalisation de devise explicite. Une erreur supposerait des montants non comparables, ce qui n'est pas démontré ici. | [SQL, L11–L16](../../legacy/pipeline_actuel.sql) ; [modèle, L126–L129](../../docs/model/model.json). |
| Jointures et regroupements n'utilisent pas `meta.customer`. | Pas une anomalie démontrée ici : un seul tenant est documenté. À vérifier avant tout usage multi-tenant. | [SQL, L32–L33 et L54](../../legacy/pipeline_actuel.sql) ; [modèle, L19–L22](../../docs/model/model.json). |

Une règle peut être certainement présente dans le code sans être une erreur métier certaine. Commencer aux créations de 2024 peut être volontaire. Ce qui est prouvé est le périmètre calculé ; son adéquation avec le besoin reste à confirmer.

### 5.2. Observations précises du corpus hors ligne

Les chemins suivants sont à lire dans `window.MODEL_DATA`, sur la [ligne 3 de model.js](../../docs/model/model.js). Pour chaque table, `columns` donne l'ordre des cellules de chaque entrée de `rows`. Les index sont **à partir de zéro**. Les champs dictionnaires contiennent eux-mêmes du JSON sous forme de chaîne : il faut le décoder pour sélectionner les entrées par `id`.

**A. Type de besoin `4`.**

Chemin : `window.MODEL_DATA['raw.dictionaries'].rows[0]`, champ nommé `setting.typeOf.project` via `columns`, puis tableau JSON décodé, entrée `id=4`.

La valeur est `New Client Boond`. Le même tableau contient `id=7 → Upsell Boond` et `id=2 → Formation`. Ce référentiel documente le sens du filtre `typeOf=4`. Il ne suffit pas à confirmer que chaque fiche est correctement typée ni que tous les besoins nouveaux clients souhaités sont présents.

Sources : [model.js, L3](../../docs/model/model.js) ; [SQL, L19](../../legacy/pipeline_actuel.sql) ; [modèle, L55–L62](../../docs/model/model.json).

**B. Deux états libellés signés, un seul retenu.**

Chemin : `window.MODEL_DATA['raw.dictionaries'].rows[0]`, champ `setting.state.opportunity`, tableau JSON décodé, entrées `id=1` et `id=14`. Les mêmes deux entrées figurent dans les versions françaises `rows[1]` et `rows[2]`.

| État | Libellé documentaire | `active` | `isEnabled` | Traitement du SQL |
|---|---|---|---|---|
| `1` | Signé - formalités à finaliser | `false` | `true` | Compté dans les deux mesures de signature. |
| `14` | Signé - formalités finalisées | `false` | `true` | Absent de ces deux mesures. |

Passer de formalités à finaliser à formalités finalisées fait sortir le besoin de la catégorie signée calculée par ce SQL. Cela ne prouve pas quelle date doit constituer la signature officielle : il faut la définir.

Sources : [model.js, L3](../../docs/model/model.js) ; [SQL, L65–L66](../../legacy/pipeline_actuel.sql).

**C. Anciens états `30–35` : `active` et `isEnabled` ne disent pas la même chose.**

Chemins : `window.MODEL_DATA['raw.dictionaries'].rows[0]`, `[1]` et `[2]`, champ `setting.state.opportunity`, tableau JSON décodé, entrées `id ∈ {30,31,32,33,34,35}`.

- Les versions françaises `rows[0]` et `rows[1]`, publiées le 12/06/2023 et le 10/03/2025, comportent ces anciens états d'en cours ou de closing avec `active=true` et `isEnabled=true`.
- Dans `rows[2]`, publiée le 08/12/2025, les libellés sont préfixés `SUPP -`, avec `active=true` et `isEnabled=false`.
- Le modèle définit `active` comme « le besoin est encore en cours » et `isEnabled` comme « étape proposée dans l'interface ». Une étape désactivée dans l'interface n'est donc pas, par ce seul fait, un état historiquement fermé.
- Aucun de ces six codes n'est inclus dans les états ouverts de la requête, quelle que soit la date analysée.

Sources : [model.js, L3](../../docs/model/model.js) ; [modèle, L914–L917](../../docs/model/model.json) ; [SQL, L62–L64](../../legacy/pipeline_actuel.sql).

**Conclusion limitée :** le code peut sous-représenter le pipe historique défini par `active`, lorsqu'un besoin éligible est observé dans ces états. L'ampleur n'a pas été calculée. Une règle de correspondance historique reste à discuter ; il ne suffit pas de retirer les étapes actuellement désactivées.

**D. Exemple minimal de multiplication des montants par les versions d'équipe.**

Chemin : `window.MODEL_DATA['raw.businessunits'].rows[0]`, `[1]`, `[2]`, colonnes `id`, `meta.ts`, `name`, `relationships.includedManagers.data`. Après décodage du tableau des membres, rechercher l'entrée `id=3006`.

| Version documentaire de la BU `id=12` | Nom | Présence du membre `3006` |
|---|---|---|
| 13/06/2023 à 16:44:51.333 | `Team BA - LA` | Oui. |
| 06/08/2025 à 17:00:00.000 | `Team BA - LA` | Oui. |
| 14/03/2026 à 10:00:00.000 | `Team BA - LA` | Oui. |

Le CTE `teams` produit trois occurrences identiques `(manager_id=3006, team=LA)`. Sous la strictness `ALL`, une ligne journalière de besoin pour ce responsable trouve trois correspondances. Le montant peut donc être multiplié par trois dans le numérateur, tandis que `uniqExact(day)` et `uniqExactIf(id, ...)` ne sont pas multipliés dans le même groupe.

Il s'agit d'une preuve structurelle à partir du corpus documentaire et des règles de jointure, pas d'un écart financier mesuré dans le serveur. L'exemple n'expose aucun nom de personne.

Sources : [model.js, L3](../../docs/model/model.js) ; [SQL, L36–L42, L54 et L62–L66](../../legacy/pipeline_actuel.sql) ; strictness en section 5.3.

**E. Changements d'équipe mélangés entre périodes.**

Chemin : `window.MODEL_DATA['raw.businessunits'].rows[2]`, `[3]`, `[4]`, colonne `relationships.includedManagers.data`, entrée JSON `id=3005`.

Le membre figure dans une version de LA et dans d'anciennes versions de SMB. Comme la jointure ne compare jamais le jour analysé à la validité de l'équipe, ces appartenances peuvent s'appliquer simultanément et rétroactivement à un besoin. Ni « équipe actuelle » ni « équipe au moment de l'événement » n'est garantie par le code.

Sources : [model.js, L3](../../docs/model/model.js) ; [SQL, L36–L42 et L54](../../legacy/pipeline_actuel.sql).

**F. Couverture Espagne non démontrée par le référentiel retenu.**

Chemin : ensemble de `window.MODEL_DATA['raw.businessunits'].rows`, colonne `name`. Le corpus contient neuf versions : trois LA, trois SMB et trois `Team KAM`. Aucun nom de business unit Espagne n'y figure. `Team KAM` ne passe pas le filtre `Team BA%`.

Le README décrit trois équipes Sales : SMB, Large Accounts et Espagne. Le SQL ne prévoit aucune règle alternative fondée sur l'agence pour reconstituer l'Espagne. Cela démontre une limite de couverture du corpus documentaire et de cette logique ; cela ne prouve pas l'absence d'une équipe ou d'un paramétrage Espagne dans tout environnement réel.

Sources : [model.js, L3](../../docs/model/model.js) ; [modèle, L692–L698](../../docs/model/model.json) ; [README, L32](../../README.md) ; [SQL, L36–L42 et L54](../../legacy/pipeline_actuel.sql).

### 5.3. Comportements dépendant des réglages ClickHouse

**Version et limite de vérification.** Le dépôt déclare `clickhouse/clickhouse-server:25.11`. Les sources officielles citées ici sont figées au tag `v25.11.1.558-stable`, cohérent avec cette branche. Cela permet de vérifier des comportements et valeurs par défaut de cette version ; aucun serveur ni profil de session effectif n'a été interrogé.

Sources : [docker-compose.yml, L3](../../docker-compose.yml) ; [code officiel des réglages 25.11](https://raw.githubusercontent.com/ClickHouse/ClickHouse/v25.11.1.558-stable/src/Core/Settings.cpp).

#### Dernier intervalle : l'intention d'une fin absente ne suffit pas

Dans la source officielle citée, `join_use_nulls` a la valeur par défaut `false` — ligne 1918 — et `join_default_strictness` vaut `All` — ligne 1929. Avec `join_use_nulls=0`, les colonnes non appariées d'une jointure externe reçoivent la valeur par défaut de leur type ; avec `1`, elles deviennent Nullable et reçoivent NULL.

Le `n.valid_from` de la requête provient d'un `DateTime64(3)` non Nullable. Sous le comportement par défaut, une version sans successeur ne fournit donc pas nécessairement un NULL à `minOrNull`. La ligne externe existe et peut contenir une date par défaut. `minOrNull` renvoie NULL quand il n'y a pas de valeur à agréger ; il ne transforme pas une valeur par défaut existante en absence de valeur.

**Conséquence déduite sous ces conditions :** `valid_to` peut être une borne artificielle ancienne, au lieu d'être absent ; le filtre de `daily` rejette alors la dernière version. C'est un risque majeur de disparition de l'état le plus récent, distinct de l'intention de prolonger la dernière version jusqu'à aujourd'hui. Le résultat exact n'a pas été observé par exécution.

Sources locales : [SQL, L30–L32 et L55–L56](../../legacy/pipeline_actuel.sql) ; [schéma, L12](../../docker/init/01_schema.sql). Sources moteur : [réglages officiels, L1918–L1929](https://github.com/ClickHouse/ClickHouse/blob/v25.11.1.558-stable/src/Core/Settings.cpp#L1918-L1929) ; [combinateur `OrNull`, L171–L193](https://github.com/ClickHouse/ClickHouse/blob/v25.11.1.558-stable/docs/en/sql-reference/aggregate-functions/combinators.md#L171-L193).

**Aucune correction n'est proposée ici.** En particulier, on ne peut pas conclure qu'il suffit d'activer `join_use_nulls=1` : la documentation de la même version indique que les jointures avec inégalité ne le supportent pas. La jointure de recherche du successeur utilise précisément une inégalité entre tables.

Sources : [SQL, L32](../../legacy/pipeline_actuel.sql) ; [documentation JOIN 25.11, L161–L163](https://github.com/ClickHouse/ClickHouse/blob/v25.11.1.558-stable/docs/en/sql-reference/statements/select/join.md#L161-L163).

#### Équipe inconnue : une chaîne vide peut subsister

Avec `join_use_nulls=0`, une équipe sans correspondance peut recevoir une chaîne vide. `ifNull(team, 'Autre')` remplace un NULL, pas une chaîne vide. La présence du libellé `Autre` dans le code ne garantit donc pas que tous les responsables non rattachés apparaissent sous ce libellé. Le cas exact dépend des réglages réellement utilisés.

Sources : [SQL, L54 et L61](../../legacy/pipeline_actuel.sql) ; [réglage officiel `join_use_nulls`](https://github.com/ClickHouse/ClickHouse/blob/v25.11.1.558-stable/src/Core/Settings.cpp#L1918-L1925).

#### Strictness `ALL` : multiplication des correspondances

La requête n'écrit ni `ALL` ni `ANY` dans ses deux `LEFT JOIN`. Sous le défaut officiel `ALL`, toutes les correspondances d'équipe participent au calcul, d'où l'exemple des montants multipliés par trois. Si un réglage externe imposait `ANY`, ce résultat de jointure pourrait changer ; cela ne constituerait pas pour autant une attribution historique validée. De plus, la recherche de la version suivante elle-même dépend de la conservation des correspondances avant le minimum.

Sources : [SQL, L32 et L54](../../legacy/pipeline_actuel.sql) ; [défaut officiel de strictness](https://github.com/ClickHouse/ClickHouse/blob/v25.11.1.558-stable/src/Core/Settings.cpp#L1929-L1940).

#### `any` : choix d'attributs et NULL

La documentation de `any` indique un choix dépendant de l'ordre de lecture et l'ignorance des NULL en présence de valeurs exploitables, sauf demande explicite de respect des NULL. Aucun ordre ni règle de priorité n'est spécifié dans le SQL pour départager des versions contradictoires à timestamp identique.

**Risque conditionnel :** en présence de tels doublons, les attributs retenus peuvent ne pas définir une version métier cohérente. En l'absence de doublon contradictoire par `(id, meta.ts)`, ce constat ne suffit pas à déclarer les valeurs fausses. Une valeur manquante ne doit pas être confondue avec une règle métier d'imputation : le SQL n'en définit aucune.

Sources : [SQL, L27–L33](../../legacy/pipeline_actuel.sql) ; [documentation officielle `any` 25.11, L9–L16 et L35–L41](https://github.com/ClickHouse/ClickHouse/blob/v25.11.1.558-stable/docs/en/sql-reference/aggregate-functions/reference/any.md#L9-L41).

### 5.4. Croissance structurelle et performance : diagnostic sans benchmark

Le README rapporte que la requête passe sur ce jeu mais ralentit sur de gros volumes. Cette appréciation est une information de consigne ; aucun temps ni seuil n'est donné. L'analyse suivante explique des facteurs structurels compatibles avec ce symptôme, sans mesurer leur coût réel.

Source : [README, L72](../../README.md).

1. **Recherche de toutes les versions ultérieures.** Sous `ALL`, pour un besoin ayant `k` versions distinctes en temps, la jointure peut produire `k × (k - 1) / 2` correspondances de versions ultérieures, avant la réduction par minimum. Cette croissance est quadratique par besoin ; l'algorithme moteur exact n'a pas été inspecté. Source : [SQL, L30–L33](../../legacy/pipeline_actuel.sql).
2. **Calendrier de plus en plus long.** Sa borne de départ reste 2024 et sa borne de fin avance avec le temps. Le volume de combinaisons logiques jour × intervalle augmente. Sources : [SQL, L5–L7](../../legacy/pipeline_actuel.sql), [L52–L56](../../legacy/pipeline_actuel.sql).
3. **Multiplication par les équipes versionnées.** Les occurrences supplémentaires d'un membre augmentent les lignes traitées et peuvent fausser les montants. Source : [SQL, L36–L42 et L54](../../legacy/pipeline_actuel.sql) ; cas documentaire en section 5.2.
4. **Recalcul de la période complète.** Le code réexprime toute la reconstitution et les agrégations à chaque lancement ; il ne contient ni période demandée en paramètre ni résultat intermédiaire explicitement matérialisé. Source : [SQL complet](../../legacy/pipeline_actuel.sql).

Le SQL contient bien un `CROSS JOIN`, mais cette seule lecture **ne prouve pas que le moteur matérialise toujours le produit cartésien complet** : des réécritures et optimisations sont possibles. Aucun `EXPLAIN`, benchmark ou objectif de performance n'a été exécuté ou fixé. La priorité de cadrage reste de déterminer les bons chiffres avant de chercher à les accélérer.

## 6. Synthèse 3 — définitions implicites et arbitrages métier

Cette section relève les choix imposés ou suggérés par la requête. Les décisions proposées sous forme de questions restent ouvertes ; ce sont des sujets de précision d'intention, pas une spécification technique.

| Sujet | Définition implicite ou limitation actuelle | Arbitrage métier à obtenir |
|---|---|---|
| Finalité du point pipe | Commentaire de pilotage hebdomadaire par équipe ; quatre mesures seulement. | Quelle décision doit permettre chaque chiffre : charge de pipe, performance de vente, prévision, suivi d'objectif ou détection de stagnation ? |
| Unité du tunnel | On compte des besoins Boond. | Le funnel attendu porte-t-il sur les personnes, sociétés, demandes, besoins ou opportunités ? Comment relier ces objets sans confondre leurs volumes ? |
| Périmètre des ventes | Type `4` et créations depuis 2024. | Ce périmètre de nouveaux clients correspond-il à la V1 ? La borne concerne-t-elle l'affichage, la population ou une disponibilité historique ? |
| Sens de « ouvert » | Liste d'états codée en dur, incluant Nurturing mais omettant les anciens `30–35`. | Quels états restent dans le pipe actif, le pipe à travailler ou le pipe prévisionnel ? Comment lire les anciens stages ? |
| Sens de « signé » | Seul l'état `1` est reconnu. | La signature correspond-elle à l'engagement commercial, à l'entrée dans `1`, à la fin des formalités (`14`) ou à un autre événement ? Comment traiter réouvertures ou annulations ? |
| Nombre et montant du pipe | Nombre distinct sur une période et montant moyen sur des jours présents. | Veut-on une photo à date, une moyenne, des entrées/sorties ou des présences pendant la semaine ? Les utilisateurs doivent distinguer ces lectures. |
| Nouvelles signatures | Aucune détection d'événement de signature. | Recherche-t-on les signatures nouvelles de la période, le portefeuille signé observé ou les abonnements actifs ? |
| MRR | Montant estimé du besoin sans définition mensuelle explicite. | Distinguer MRR commercial signé, montant du deal HubSpot et MRR des abonnements : quelle définition sert quel usage et quel objectif ? Qui valide le rapprochement ? |
| Pondération | Ni probabilités par stage ni pondération du besoin utilisées. | Quelle probabilité est retenue, pour quelle équipe, à quelle date et pour quelle décision ? Les valeurs du cabinet sont-elles acceptées ou à challenger ? |
| Attribution des résultats | Responsable versionné du besoin, rejoint à toutes les appartenances d'équipe. | Équipe actuelle, équipe de l'événement ou équipe de chaque date observée ? Comment attribuer un deal transféré sans doubler un total ? |
| Couverture des équipes | Règle fondée sur les seuls noms `Team BA%`. | Quelle règle métier couvre SMB, LA et Espagne de façon exhaustive ? Que doit afficher un responsable non rattaché ? |
| Temporalité métier | Publication CDC puis projection au jour. | Pour chaque indicateur, faut-il la date métier ou la date observée ? Quelle précision suffit pour l'ancienneté et les durées par stage ? |
| Suppressions | Événements de suppression écartés du calcul. | Quelle conséquence sur la photo actuelle et les chiffres historiques ? Le SQL ne permet pas d'inférer une politique de conservation ou d'effacement. |
| Calendrier et fraîcheur | Jusqu'à aujourd'hui, semaine éventuellement incomplète, pas d'indicateur de fraîcheur. | Quand un jour ou une semaine est-il complet ? Quand les chiffres sont-ils assez frais pour chaque décision ? |
| Qualité et validation | Pas d'indicateur de montant absent, d'appartenance ambiguë ou de rapprochement inter-outils. | Qui valide les définitions et sur quels cas concrets rapproche-t-on les chiffres avec Sales, Marketing et, si nécessaire, Finance ? |

Sources des choix actuels : [SQL complet](../../legacy/pipeline_actuel.sql). Besoins et désalignements explicitement formulés : [README, L32, L49–L63 et L67](../../README.md) ; [expression de besoin, L9–L16](../../docs/besoin/expression-de-besoin.md). Sens de Nurturing et des types : [model.js, L3](../../docs/model/model.js), champs décrits en section 5.2. Probabilités : [modèle, L1454–L1487](../../docs/model/model.json).

**Hypothèse d'usage à valider :** les Sales peuvent chercher simultanément une photographie du pipe, les nouvelles signatures sur une période et une prévision de montant pondéré. Cette hypothèse est cohérente avec la combinaison du point pipe, des objectifs et de l'expression de besoin, mais la requête actuelle ne permet pas de l'établir comme besoin exhaustif accepté.

Sources : [SQL, L1–L2](../../legacy/pipeline_actuel.sql) ; [modèle, L1415–L1487](../../docs/model/model.json) ; [expression de besoin, L9–L16](../../docs/besoin/expression-de-besoin.md).

**Points à conserver pour la suite du cadrage :** séparer stock, flux et durée ; distinguer signature, finalisation des formalités et abonnement ; définir l'unité de compte et l'attribution historique ; expliciter les lacunes et faire valider les définitions. Les futurs modèles et le dashboard devront être cohérents avec ces décisions.

## 7. Vérifications de ce document

- Le bloc SQL intégral a été comparé octet par octet au fichier source UTF-8 lors de la création.
- Les cibles des liens Markdown locaux ont été contrôlées ; les repères de lignes cités ont été vérifiés dans les fichiers du dépôt.
- Les chemins JSON des exemples hors ligne ont été contrôlés sur les lignes embarquées dans `model.js` ; ces exemples n'ont pas été assimilés à une lecture du serveur.
- Les comportements ClickHouse discutés sont sourcés à la version officielle 25.11 citée et présentés séparément du calcul métier voulu.
- Aucun résultat commercial réel, écart chiffré Boond/HubSpot, temps d'exécution ou correction de requête n'est prétendu validé par cette analyse.
