# Q10 — Création du besoin et entrée dans le pipeline qualifié

État des lieux établi le **24 octobre 2026**, par lecture des documents et requêtes
en lecture seule sur ClickHouse. Aucun modèle métier ou SQL historique n’a été modifié.
**Statut : diagnostic documenté, définition métier encore ouverte.**

## 1. Ce que l’on peut répondre aujourd’hui

Le besoin existe dans le CRM avant la démo. En revanche, les sources ne donnent pas
de définition commune de l’événement qui transforme ce besoin en opportunité qualifiée
pour le cockpit. Une création de fiche et une entrée dans un périmètre de pilotage
peuvent être deux dates différentes. C’est une interprétation possible du désaccord,
pas une explication confirmée par les métiers.

Trois visions coexistent :

| Source | Début / périmètre décrit | Conclusion permise |
| --- | --- | --- |
| Cycle de vie fourni | Besoin ouvert à « Lead à traiter », puis qualification, découverte et démo | L’objet CRM existe en amont de la démo. |
| Maquette, guide de lecture | L’opportunité démarre au stage démo dans Boond, associé à la création du besoin | La proposition du cabinet place la frontière commerciale à la démo, en contradiction avec la création décrite dans le cycle. |
| SQL historique | Créations depuis 2024, type 4 ; pipe ouvert incluant Lead à traiter, Qualification, Découverte et Nurturing | Le code ne limite pas le pipe aux seuls dossiers entrés à la démo. |

Le README signale lui-même le désaccord. Il ne demande pas de présumer qu’un des
documents fait déjà autorité sur l’autre.

## 2. Le parcours décrit dans le cycle

```text
Formulaire → contact / demande de démo → prise en charge commerciale
→ création du besoin : Lead à traiter (0)
→ Qualification (22) → RDV découverte (23) → Show Boond (24)
→ Proposition remise (21) → Projet validé (25) → Closing (28)
→ Issue : signé / perdu / abandonné ; nurturing possible
```

C’est une lecture du parcours documentaire, pas un workflow obligatoire démontré
par les données. Le référentiel comporte aussi Shortlist (26) et des étapes anciennes.
On ne peut pas supposer que tous les dossiers passent par toutes les étapes dans
cet ordre, ni interpréter les issues alternatives comme une suite linéaire.

Le nom « Qualification » décrit une étape ; il ne démontre pas à lui seul que la
qualification est déjà réussie à son entrée. De même, « Show Boond » est un état
de fiche, pas une preuve indépendante de présence à une démo.

## 3. Comment lire `state`, `active` et `isEnabled`

- `state` : état du besoin saisi dans Boond, interprété via le dictionnaire du tenant.
- `active` : le besoin est encore en cours dans ce référentiel. Ce champ ne signifie
  ni « qualifié » ni « abonnement actif ». Nurturing et Lead à traiter ont `active = true`.
- `isEnabled` : l’étape est proposée dans l’interface. Une étape désactivée peut
  rester présente sur des dossiers ou dans leur historique.
- `SUPP` et `isEnabled = false` ne constituent pas une suppression CDC de la fiche.
  La suppression d’un enregistrement est portée par `meta.deleted`.
- Les codes sont des identifiants, pas des rangs : la démo est 24, la proposition 21,
  la qualification 22, et les états signés 1 et 14. Ne pas utiliser `state >= 24`
  pour signifier « a atteint la démo ».

La dernière version française disponible du dictionnaire est datée du **8 décembre
2025 à 10:00 UTC**. Elle décrit le référentiel fourni ; elle ne prouve pas qu’il
n’a jamais évolué auparavant ou qu’il serait celui d’un environnement réel actuel.

## 4. Ce que fait précisément le SQL historique

Source : [legacy/pipeline_actuel.sql](../../legacy/pipeline_actuel.sql).
Cette partie est une lecture statique ; la requête historique complète n’a pas
été exécutée pour produire les chiffres du présent diagnostic.

1. Il lit les versions non supprimées de `raw.opportunities`, avec `typeOf = 4`
   (« New Client Boond » selon le référentiel) et `creationDate >= '2024-01-01'`.
2. Il essaie de former des intervalles à partir de `meta.ts`, puis de reconstruire
   des états quotidiens et des indicateurs par semaine et équipe.
3. Sa liste de pipe ouvert est `(0, 20, 21, 22, 23, 24, 25, 26, 28)`.
4. Il compte les signatures uniquement avec `state = 1`, sans inclure `14`.
5. Il ne calcule aucune date d’entrée dans un pipeline qualifié et ne produit pas
   de compteur de nouvelles opportunités fondé sur un premier passage à la démo.

Il faut distinguer le filtre de population sur `creationDate` du début des intervalles
sur `meta.ts`. Le SQL ne démontre pas que ces deux dates désignent le même événement.
Ses comptes hebdomadaires portent sur des états observés sur la semaine, pas sur
des entrées commerciales définies et datées comme telles.

Deux écarts visibles :

- Les anciens états 30–35 sont encore « en cours » selon le dictionnaire, mais
  absents de sa liste ouverte. Décider de leur exclusion exige une règle explicite.
- Nurturing est inclus dans le pipe ouvert ; cela ne décide pas s’il doit compter
  dans un pipe qualifié activement travaillé ou dans un portefeuille séparé.

La méthode historique a aussi des limites de versions, suppressions, intervalles
et agrégations : voir [l’analyse détaillée existante](analyse_pipeline_actuel.md).
Le comportement du code ne constitue pas à lui seul une validation métier.

## 5. Ce qui est observé dans les données

### Population et méthode

- Table brute : **7 020 versions**, pour **1 390 clés distinctes tenant × id**.
- Photographie après dernière version par clé, puis exclusion des suppressions :
  **1 376 besoins**. Les chiffres ci-dessous portent sur tous les types et toutes
  les dates de création, sauf mention contraire.
- Créations présentes : du **6 septembre 2021** au **28 septembre 2026**.
- Versions CDC présentes : du **12 juin 2023** au **30 septembre 2026**.
- Il s’agit du jeu fourni, pas d’une observation opérationnelle au 24 octobre 2026.
- Pas de doublon tenant × id × `meta.ts` dans `raw.opportunities` lors du contrôle
  précédent. Le SQL d’exploration suppose cet ordre sans égalité conflictuelle.

### A. Une fiche existe avant la démo

Parmi les 1 376 besoins non supprimés, **1 271 ont l’état 0, Lead à traiter, comme
premier état enregistré**. Pour **1 270** d’entre eux, le premier `meta.ts` est égal
à `creationDate` ; pour le dernier, il est postérieur. Cela appuie fortement le
cycle fourni : la création de fiche ne désigne pas systématiquement une démo.

Les **105 autres** commencent leur historique disponible dans un autre état. Cela
ne démontre pas qu’ils ont été créés directement dans cet état : leur première
observation est postérieure à leur date de création.

### B. Répartition actuelle des besoins

| État ou groupe d’états | Besoins non supprimés |
| --- | ---: |
| Lead à traiter — 0 | 32 |
| Qualification — 22 | 73 |
| RDV découverte — 23 | 38 |
| Show Boond — 24 | 21 |
| Proposition remise — 21 | 13 |
| Projet validé — 25 | 3 |
| Shortlist — 26 | 11 |
| Closing — 28 | 4 |
| Nurturing — 20 | 338 |
| Anciens états encore « en cours » — 30, 31, 32, 33 | 8 |
| Signé, deux états réunis — 1 et 14 | 227 |
| Perdu — 13 | 260 |
| Non qualifié — 2 | 146 |
| Abandonné — 3 | 172 |
| Anciens états fermés présents — 7, 10, 19 | 30 |
| **Total** | **1 376** |

Ce tableau est un stock d’états actuels, **pas un tunnel de conversion**. Les 73
en qualification et les 21 en Show Boond ne permettent pas de calculer un taux de
passage : ce ne sont pas nécessairement les mêmes dossiers suivis dans le temps.

### C. Les étapes observées dans l’historique

Sur les mêmes 1 376 besoins :

| Observation d’au moins une version à ce stade | Besoins |
| --- | ---: |
| Qualification — 22 | 942 |
| RDV découverte — 23 | 518 |
| Show Boond — 24 | 317 |

**121 des 227 besoins actuellement signés n’ont aucune version Show Boond dans
l’historique fourni.** Et **14 des 317 dossiers avec Show Boond n’ont aucune
version Qualification observée**.

Ces constats interdisent d’imposer sans précaution une séquence complète et
obligatoire. Ils ne permettent pas de choisir entre étapes sautées, saisie
incomplète, changement de processus, reprise de dossiers ou historique incomplet.
L’absence d’une étape enregistrée ne prouve pas l’absence de l’événement réel.

### D. Une observation CDC n’est pas une date métier certifiée

`creationDate` décrit la création de la fiche ; `meta.ts` date la publication d’une
version dans le flux. `updateDate` est la dernière modification de la fiche,
pas une date dédiée de qualification. `closingDate` est une date de closing saisie,
à qualifier avant d’en faire une date de signature effective.

La première version observée avec `state = 24` peut servir de **proxy de premier
passage enregistré à Show Boond**. Elle ne doit pas être présentée sans réserve
comme l’heure de la démo réelle ou du passage effectif, ni comme une première
entrée certaine si l’historique commence tard.

Exemple réel du jeu : besoin **200813**, créé le **5 juin 2024**, premier état
observé 0 à cette date, puis première observation de Show Boond le **18 décembre
2025**. La différence atteint **561 jours calendaires** selon `dateDiff('day', ...)`.
Ce n’est pas une durée de vente « validée » : cet écart demande une investigation
de la saisie et de la couverture historique.

### E. Les actions de démo ne lèvent pas automatiquement l’ambiguïté

Le contrôle précédent a trouvé **607 actions** de types Demo 1 / Follow-up demo
pour **504 contacts distincts**. Toutes pointent vers un contact, sans lien direct
vers une opportunité. Certains contacts sont référencés par plusieurs besoins.
Une date d’action ne peut donc pas être transférée à chaque opportunité de ce
contact sans règle d’attribution. Le type démo et une date passée ne suffisent pas
non plus à prouver la tenue de la séance.

## 6. Pourquoi HubSpot ne tranche pas la question

`hubspot.deals` reflète les besoins Boond et contient notamment sa propre date de
création, une étape, une date de fermeture et des champs Boond recopiés. La date
de création HubSpot peut être une date de création de la copie : elle n’est pas
automatiquement la qualification du besoin ni sa création Boond.

Le modèle fourni est une photographie des deals dans leur état du jour, sans
historique complet de leurs étapes. Le stade du contact HubSpot (`lead`,
`opportunity`, `customer`…) concerne un contact, pas l’entrée qualifiée de chaque
besoin commercial. Aucune équivalence entre ces événements n’est documentée.

## 7. Options et conséquences sur les indicateurs

| Événement candidat | Ce qu’il permettrait de mesurer | Limite à expliciter |
| --- | --- | --- |
| Création CRM — `creationDate` | Nouveaux besoins enregistrés ; délai global depuis prise en charge CRM | Inclut les besoins pas encore qualifiés. |
| Entrée dans Qualification — état 22 | Début du travail de qualification | Ne prouve pas la qualification réussie. |
| Entrée en RDV découverte — état 23 | Dossiers arrivés à la découverte | Ni la tenue du RDV ni les critères de qualification ne sont prouvés par le libellé seul. |
| Premier Show Boond — état 24 | Dossiers ayant un passage enregistré au stade démo ; proche de la frontière annoncée par la maquette | Date CDC et couverture historique à qualifier ; tenue de démo à confirmer. |
| Démo effectivement réalisée | Événement commercial concret si documenté et attribuable | Preuve de réalisation et rattachement au besoin insuffisants à ce stade. |

Exemple fictif : fiche créée le 1er, démo le 10, signature le 20. La durée depuis
création est de 19 jours écoulés ; depuis démo, 10 jours. Pour un dossier créé en
fin de mois et démontré le mois suivant, la cohorte change également. Les deux
indicateurs sont possibles, mais ils ne racontent pas la même chose.

**Recommandation de spécification, pas décision métier :** conserver distinctement
la création CRM et les passages enregistrés dans les étapes. Nommer les compteurs
« besoins créés » et « opportunités entrées dans le pipe qualifié » seulement
après définition de ce second périmètre. Pour chaque KPI, préciser événement,
population, date et grain. Ne pas remplacer silencieusement `creationDate` par
une date de démo, ni inventer une date de qualification pour les dossiers sans preuve.

## 8. Arbitrages encore nécessaires

1. Qu’est-ce qu’un besoin qualifié : quels critères et quelle validation ? À quelle
   étape cela se produit-il, et la démo marque-t-elle planification ou réalisation ?
2. L’indicateur « opportunités générées » mesure-t-il les créations de fiches ou
   les premières entrées dans ce périmètre ? Quelle date utilise chaque cohorte ?
3. Nurturing est-il suivi dans le pipe actif, séparément ou dans les deux avec
   des libellés distincts ? Que fait-on des anciens états encore présents ?
4. Comment gérer les sauts, retours, réouvertures et qualifications perdues ?
   Un dossier réentrant compte-t-il à nouveau ou reste-t-il dans sa cohorte initiale ?
5. Comment traiter les dossiers dont le début d’historique ou la démo manque ?
   Prévoit-on une catégorie « non observable » et une date de début de couverture ?

Le métier ne répondant pas pendant l’exercice, ces points doivent rester des
questions ou des hypothèses explicitement nommées. Aucun seuil n’est adopté dans
ce diagnostic. Voir [QM-06](questions_metiers.md#qm-06--entrée-dans-le-pipeline-qualifié).

## 9. Sources et reproduction

- [README](../../README.md) : désaccord explicitement signalé et disponibilité du métier.
- [Cycle de vie](../../docs/cycle-de-vie.html) : création du besoin et étapes commerciales.
- [Maquette](../../docs/besoin/maquette-pipeline.png) : guide de lecture, zone 2 et zones de pipe.
- [Expression de besoin](../../docs/besoin/expression-de-besoin.md) : cohortes par mois de création,
  états à J+30/J+60/J+90 et besoin d’historisation.
- [Modèle de données](../../docs/model/model.json) : sens des champs et relations.
- [SQL historique](../../legacy/pipeline_actuel.sql) et [analyse existante](analyse_pipeline_actuel.md).
- [Requêtes de vérification Q10](explore_q10_pipeline_entry.sql) : quatre
  requêtes indépendantes, testées le 24 octobre 2026 sur ClickHouse 25.11.
- [Résultats des quatre requêtes](preuves_Q10.json) : valeurs du jeu local lors du contrôle.
- [Exploration des compteurs et démos](../../docs/sql/explore_counting_grains.sql).

Depuis la racine du dépôt, avec ClickHouse démarré :

```powershell
Get-Content .\docs\sql\explore_q10_pipeline_entry.sql -Raw |
    docker exec -i use-case-clickhouse clickhouse-client --multiquery --format JSONEachRow
```

Les dates affichées par cette session ClickHouse sont en UTC. L’exploration utilise
la dernière version disponible pour la population actuelle et toutes les versions
pour les passages observés ; elle ne constitue pas une reconstruction certifiée
des populations à toutes les dates passées. Les nombres évolueront si le jeu change.
