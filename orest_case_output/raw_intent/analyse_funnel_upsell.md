# Upsells : parcours commercial observé dans les données

Analyse en lecture seule du **25 octobre 2026**, sur le jeu local fourni.
**Conclusion : les upsells observés utilisent le même objet CRM et le même
référentiel d’étapes que les nouveaux clients, mais pas le même parcours.**
Ils entrent directement en proposition après « Lead à traiter », sans qualification,
découverte ou démo enregistrées comme états intermédiaires.

## 1. Population et contrôles

La dernière version française de `raw.dictionaries.setting.typeOf.project` donne :

| Code `typeOf` | Libellé | Opportunités actuelles non supprimées |
| --- | --- | ---: |
| 4 | New Client Boond | 1 267 |
| 7 | Upsell Boond | 52 |
| 2 | Formation | 57 |

Les clés sont `meta.customer` + `id`. La sélection de la dernière version précède
l’exclusion des suppressions. Les parcours utilisent ensuite les versions historiques
des 52 upsells retenus, classées par `meta.ts`, en supprimant les répétitions
consécutives d’un même état. Plusieurs modifications de montant ou de responsable
au même état ne sont donc pas plusieurs passages de funnel.

Pour les upsells :

- **52 opportunités**, **51 sociétés**, **364 versions** ; aucune n’est limitée à une seule version.
- Créations du **19 février 2024** au **28 septembre 2026**, toutes périodes réunies.
- Aucun changement de `typeOf` observé, aucun horodatage ex aequo par clé et aucune
  version de suppression dans les historiques sélectionnés.
- Le premier enregistrement correspond à la date de création, dans l’état 0,
  pour chacun des 52 dossiers.
- Les 13 parcours distincts observés couvrent exactement les 52 dossiers.

Ce sont des constats sur le jeu fourni. Ils ne démontrent pas que tout le processus
réel est saisi ni que le comportement se généralise à l’ensemble de l’entreprise.

## 2. Leur funnel commercial

Voici les **opportunités distinctes ayant atteint chaque état au moins une fois** :

| Étape | Code | Upsells ayant atteint l’étape |
| --- | ---: | ---: |
| Lead à traiter | 0 | **52** |
| Proposition remise | 21 | **47** |
| Projet validé par la direction | 25 | **39** |
| Shortlist | 26 | **37** |
| Closing | 28 | **27** |
| Signé — formalités à finaliser | 1 | **26** |
| Signé — formalités finalisées | 14 | **21** |

Les 21 dossiers passés par 14 font partie des 26 passés par 1 : **ce ne sont pas
47 signatures**. La signature commerciale observée concerne **26 dossiers distincts**.

La trajectoire gagnante observée est :

```text
Lead à traiter (0)
  → Proposition remise (21)
  → Projet validé (25)
  → Shortlist (26)
  → Closing (28)
  → Signé, formalités à finaliser (1)
  → Signé, formalités finalisées (14)
```

**21 dossiers** ont parcouru cette séquence complète. **5 autres** s’arrêtent pour
l’instant à l’état signé 1. Tous les parcours ayant progressé au-delà de 0 passent
directement de 0 à 21 dans l’historique disponible.

Des sorties Perdu et Abandonné se produisent à différents endroits. Un dossier
présente la succession `0 → 21 → 25 → 26 → 3 → 2` : il passe d’Abandonné à Non
qualifié. Il ne faut donc pas compter ses deux états historiques comme deux pertes
de dossiers distincts. Ce cas montre aussi qu’un état fermé peut encore être modifié.

Ces effectifs ne forment pas des taux de conversion de cohortes matures : les
dates de création diffèrent et certains dossiers sont encore ouverts. L’écart
entre deux étapes inclut des dossiers en attente, pas seulement des pertes.

## 3. Où en sont-ils actuellement ?

| Situation actuelle | Upsells |
| --- | ---: |
| Signés — 1 ou 14 | **26** : 5 en état 1, 21 en état 14 |
| Perdus — 13 | **7** |
| Abandonnés — 3 | **3** |
| Non qualifiés — 2 | **1** |
| Encore ouverts | **15** : 5 au stade 0, 4 au stade 21, 1 au stade 25, 4 au stade 26, 1 au stade 28 |
| **Total** | **52** |

Aucun upsell n’est actuellement en nurturing et aucun passage à cet état n’est
observé dans leur historique. Le regroupement « encore ouverts » ci-dessus correspond
aux étapes présentes et actives dans le référentiel ; il ne définit pas un pipe qualifié validé.

## 4. Comparaison avec les nouveaux clients

| Passage observé au moins une fois | Nouveaux clients, type 4 | Upsells, type 7 |
| --- | ---: | ---: |
| Qualification — 22 | 897 | **0** |
| RDV découverte — 23 | 497 | **0** |
| Show Boond — 24 | 304 | **0** |

Le référentiel d’étapes est partagé, mais les upsells du jeu **ne suivent pas le
sous-parcours acquisition/qualification/démo des nouveaux clients**. Cette différence
est observée dans les états, pas seulement déduite du libellé « Upsell ».

Cela ne prouve pas qu’aucune discussion, qualification ou démonstration n’a eu lieu
dans la réalité. Cela signifie qu’elles ne sont pas enregistrées comme ces états
dans les parcours de ces dossiers. Ces volumes bruts ne doivent pas servir à comparer
des performances entre populations ayant des périodes et couvertures différentes.

## 5. Ce que disent les liens vers les autres tables

### Sociétés et clients existants

Les 52 upsells possèdent une société et un contact principal. Pour chacun, une
version de besoin New Client Boond de la même société est observée signée **avant
la création de l’upsell**. Cela soutient l’interprétation d’une vente additionnelle
après acquisition. Une signature antérieure ne prouve toutefois pas que l’abonnement
était encore actif à la date de l’upsell.

### Actions de démo

Les contacts principaux de **33 upsells** ont au moins une action de type Demo 1
ou Follow-up demo dans les données. Ce comptage ne rattache pas ces séances à
l’upsell : une démo peut appartenir à l’acquisition initiale ou à une autre affaire.
Il ne faut donc pas conclure « 33 upsells ont eu une démo ». Les actions sont
rattachées au contact, pas directement à ces opportunités.

### HubSpot

**Aucun deal HubSpot non archivé n’est relié à ces 52 upsells** par
`properties_boond_id_num`. Le rapprochement utilise une référence positive entière,
dans le contexte mono-tenant du case. Cela établit une absence dans l’extrait fourni,
pas une règle générale d’exclusion des upsells de tout HubSpot réel.

Conséquence : les deals HubSpot fournis ne couvrent pas ce portefeuille upsell.
Une comparaison globale Sales/Marketing doit donc contrôler le type d’opportunité,
en plus de la définition des montants et des dates.

### Projets et lignes d’abonnement

**Aucun projet actuel non supprimé ne référence explicitement l’un de ces upsells**
via `relationships.opportunity.data.id`. Aucune ligne d’abonnement n’est donc reliée
par ce chemin explicite `upsell → projet → livraison` dans le contrôle effectué.

Cela ne prouve pas qu’il n’existe aucun abonnement pour ces sociétés, ni qu’aucune
extension n’a été appliquée : un projet existant peut rester rattaché à la vente
initiale. Il faut examiner les changements des lignes existantes et leur provenance
avant de conclure à une absence d’expansion réelle. L’impact sur le MRR n’est pas
établi par cette analyse et le montant de l’upsell n’est pas automatiquement du MRR additionnel.

## 6. Conséquences proposées pour le cockpit

- Séparer nouveaux clients, upsells et formations via `typeOf`, en conservant les
  identifiants et libellés. Le SQL historique filtre `typeOf = 4` et exclut les upsells.
- Pour les upsells observés, suivre les étapes 0, 21, 25, 26, 28 et les issues.
  Ne pas imposer une demande de démo, Qualification ou Show Boond comme entrée obligatoire.
- Distinguer les volumes ayant atteint une étape des stocks actuellement à cette
  étape. Ne pas additionner les deux états signés pour compter les passages historiques.
- Faire confirmer les probabilités de signature pour les upsells : un coefficient
  par étape/équipe n’est pas démontré comme adapté à cette population.
- Garder distincts signature d’un upsell, démarrage effectif d’une extension et
  expansion MRR. La chaîne de preuve entre affaire et modification d’abonnement reste à établir.

**Question métier à ajouter :** le parcours court `Lead à traiter → Proposition`
est-il le workflow attendu des upsells ? Comment relie-t-on un upsell gagné à une
modification d’abonnement existant, et les upsells doivent-ils être synchronisés
dans HubSpot ? Ces propositions ne constituent pas une règle métier validée.

## 7. Preuves et reproduction

- [Six requêtes SQL indépendantes](../../docs/sql/explore_upsell_funnel.sql).
- [Résultats et contrôles de cohérence](preuves_upsell.json) : résultats par requête,
  sans modification des données ; tous les contrôles enregistrés passent.
- [Référentiel documentaire](../../docs/model/model.json).
- [Requête historique](../../legacy/pipeline_actuel.sql), filtre `typeOf = 4`.

Avec Docker et ClickHouse démarrés, depuis la racine du dépôt :

```powershell
Get-Content .\docs\sql\explore_upsell_funnel.sql -Raw |
    docker exec -i use-case-clickhouse clickhouse-client --multiquery --format JSONEachRow
```

Les contrôles concernent la population actuelle non supprimée du jeu fourni,
sans filtre de période. Les valeurs changeront si les données changent. Les dates
de versions CDC sont des dates de publication, pas des dates métier certifiées.
