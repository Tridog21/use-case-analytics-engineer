# Inventaire des sources pour préparer le staging

**Règle actuelle — échange 24 : New MRR inclut les upsells.** `New MRR total = composante New + composante Upsell`. Filtre demandé : **New / Upsell**. New conserve les entrants et retours après churn déjà retenus ; Upsell correspond à la hausse nette active des sociétés restées actives. L’expansion est donc une composante du total New MRR, pas un montant à ajouter une deuxième fois. `MRR fin = MRR début + New MRR total − churn MRR`, à périmètre et unité identiques, corrections explicites. [Décision DU-38](questions_decisions.md#du-38). Aucune source physique supplémentaire n’est nécessaire du seul fait de ce regroupement : catégorie dérivée depuis le contexte société/clôtures, à préparer dans l’intermédiaire, pas champ source à inventer.

**Échange 23 :** « Nb In demo » compte les **sociétés distinctes** ayant au moins une opportunité en phase Démo à la date observée : deux dossiers de la même société = un prospect. Pour l’upsell de 100 à 150 €/mois, seule la contribution **supplémentaire de 50 €/mois** est retenue pour le case. Dans sa réponse au montant signé, l’utilisateur écrit « 50 euros en new mrr » : le montant incrémental est décidé ; l’échange 24 inclut ensuite les upsells dans New MRR avec filtre New / Upsell. [Décisions et clarification](questions_decisions.md#du-36).

**Mise à jour métier — échange 22 :** entrée à la création Boond après soumission du formulaire ; démos réellement réalisées distinctes de « Nb In demo » ; signature dès « Signé — formalités à finaliser » ; client actif = société avec au moins un abonnement en cours à clôture. Pour le case : réactivations incluses dans New MRR, variation nette par société entre clôtures, départ-retour intra-mois hors périmètre, bloc MRR actif/churn global sans filtre équipe. [Décisions de l’échange 22](questions_decisions.md#du-28). Le supplément signé d’upsell et le grain société de Nb In demo sont précisés à l’échange 23 ; données sources des montants et critères d’activité restent à préciser ; nomenclature New MRR résolue à l’échange 24.

**Incidence sur cet inventaire :** aucune colonne physique ou table n’est retirée. `raw.opportunities.creationDate` devient le candidat de date d’entrée, `state=1` l’événement de signature à reconstruire ; `raw.actions` doit prouver la tenue d’une démo. Les colonnes de lignes Boond restent nécessaires, mais les contributions de New MRR/expansion/churn du case sont calculées après regroupement société et comparaison de clôtures ([R03](intent_ia.md#mrr-client-cloture)). Les mentions antérieures « entrée/compteur/grain/réactivation à choisir » dans les décompositions sont remplacées sur ces seuls points par DU-28 à DU-35 ; les preuves, dates, critères d’activité et montants signés restent à établir. Ne pas sommer directement des pertes brutes de lignes pour ce churn net par société.

**Échange 19 — historisation de toute la chaîne :** l’exigence couvre staging, intermédiaires, faits, dimensions et liaisons. Distinguer l’unité métier de ses versions et sélectionner les versions pertinentes avant agrégation. Les modalités de révision/restitution et la rétention détaillée restent à spécifier. [Règle commune et deux vues détaillées](architecture_modele_proposition.md#historisation-toutes-couches), [DCI-17](questions_decisions.md#dci-17).

**Échange 15 :** la [liste courte des KPI, définitions et formules](liste_kpi_humaine.md) devient la lecture humaine approuvée. La [nouvelle proposition de modèle](architecture_modele_proposition.md) décrit l’intermédiaire, les faits et les dimensions à partir du staging recensé. Les DTR restent hors de cette proposition ; les règles ouvertes ne sont pas arbitrées par le schéma. [DCI-14](questions_decisions.md#dci-14).

**Échanges 11–13 — champs sources, constructions à notre charge et cadre incrémental CDC.** Cet inventaire vient de la [décomposition des champs métier](correspondance_champs_clickhouse.md). Il ne définit pas encore les modèles dbt ou une architecture ; il conserve désormais les principes incrémentaux fournis par l’utilisateur, avec leurs validations préalables. Aucune requête en base n’a été exécutée.

L’objectif est de savoir **quelles colonnes de quelles tables conserver pour préparer les analyses**. Les données correspondant aux choix encore ouverts restent visibles : une source candidate n’est pas transformée en source métier validée. Les suggestions H et le scénario U09 restent optionnels ; les paiements restent exclus.

## Comment lire ce regroupement

- Une colonne physique apparaît une seule fois dans sa table. Les liens indiquent les champs métier qui justifient son usage.
- Les colonnes calculées (durée, MRR actif, churn, canal retenu…) ne sont pas des extractions : elles renvoient à la table de décomposition.
- Pour chaque objet Boond, conserver l’identité tenant + id et les versions meta.ts/meta.deleted. Les dictionnaires n’ont pas d’id d’objet documenté : tenant, langue et version servent à les repérer.
- Les propriétés JSON à extraire sont précisées sous leur colonne conteneur. Aucun sous-champ absent du modèle n’est inventé.
- Les dates de modification/publication ne constituent pas une date de chargement ni une preuve universelle d’événement métier. La rétention détaillée reste à arbitrer ; préparer les colonnes ne décide pas de leur durée de conservation.

Les types et noms ci-dessous sont vérifiés dans [model.json](../../docs/model/model.json), instantané documentaire du 30 septembre 2026. Les métadonnées d’historique et les clés ajoutées sont des dépendances de préparation, pas de nouveaux KPI.

<a id="constructions-techniques"></a>
## Ce que nous construisons en complément des sources

**Décision utilisateur, échange 12.** Les 159 colonnes réparties dans les 15 tables ci-dessous sont des colonnes documentées à exploiter. Elles ne comprennent pas les colonnes techniques, tables de référence et résultats que nous avons la liberté de produire.

| Élément | Travail à notre charge | Distinction à conserver |
| --- | --- | --- |
| Timestamp d’import | Ajouter un horodatage à la capture des sources concernées ; `imported_at` est un nom proposé, pas un champ déjà présent | Date d’import ≠ `meta.ts`/`updatedAt` ≠ date métier |
| Historique d’une source non versionnée | Conserver les versions/états observés via un mécanisme adapté : imports conservés ou capture incrémentale des changements | Un incrémental peut aussi écraser ; l’historisation exige que les anciennes valeurs restent disponibles |
| Traçabilité des imports | Produire les informations de lot, réussite et couverture nécessaires au suivi des chargements, selon la conception retenue | Ne pas prendre le dernier changement source pour une preuve d’import complet réussi |
| Référentiel date | Générer les dates et leurs attributs de jour/semaine/mois/clôture/horizon si utile | La date métier choisie et les conventions d’analyse restent explicites |
| Référentiel country | Construire les codes/libellés normalisés et les correspondances aux pays présents dans les sources | Garder les valeurs d’origine et les inconnus ; pays ≠ équipe commerciale |
| Champs dérivés et KPI | Nettoyer, croiser et transformer les données dans le staging, l’intermédiaire et le mart selon le rôle du calcul | Une durée ou un churn peut être calculé sans exister comme colonne CRM ; sa règle métier doit cependant être définie |

Cette répartition décrit des capacités de construction, pas des modèles techniques définitifs. Nous ne faisons pas dépendre le projet de l’existence préalable d’une table date/country ou d’un champ KPI source.

### Historisation à considérer par famille de sources

| Famille | Situation documentée | Orientation à prendre en compte |
| --- | --- | --- |
| `raw.*` Boond | Versions CDC déjà présentes, avec tenant, identité si applicable, `meta.ts` et `meta.deleted` | Préserver et exploiter ces versions ; métadonnées de notre import ajoutables séparément. Ne pas réduire tout l’historique au dernier état |
| `hubspot.contacts`, `hubspot.deals` | État courant fourni, pas d’historique complet documenté | Construire notre histoire observée à partir des captures conservées, avec timestamp d’import. Choisir cadence et mécanisme selon chaque source ; aucune cadence uniforme présumée |
| `ref.sales_targets` | Mois/équipe/indicateur, mais pas d’historique des révisions d’une même cible | Prévoir de conserver les versions reçues si les cibles sont révisées ; mois cible et date d’import sont distincts |
| `ref.stage_probabilities` | Étape/équipe/valeur, sans dates de validité documentées | Prévoir l’historisation des versions importées ; date observée et date d’effet métier restent distinctes |
| Référentiels date/country créés par nous | Aucune table source obligatoire pour les créer | Générer/maintenir leur contenu selon le besoin ; historisation seulement si pertinente pour le référentiel, pas ajout systématique à toute table |

**Limite temporelle précise :** l’histoire ainsi construite commence aux observations capturées. Elle permet les analyses futures ; elle ne prouve pas les états ni les événements antérieurs, ni les changements intermédiaires jamais capturés. La fréquence de capture et la conservation des versions seront précisées dans les spécifications. La rétention détaillée reste ouverte.

<a id="incremental-cdc"></a>
## Cadre de référence pour l’incrémental CDC de raw

**Provenance : instruction utilisateur, échange 13 — [DCI-13](questions_decisions.md#dci-13).** Ces principes s’appliquent aux modèles pour lesquels une matérialisation incrémentale des versions CDC sera retenue. Ils ne rendent pas toutes les tables de staging incrémentales : une vue reste possible, et le faible volume du case impose de justifier chaque matérialisation. Les modèles ne sont pas encore construits ; aucune stratégie dbt-clickhouse ni performance n’a été vérifiée dans cette étape.

### Chargement et reprise attendus

1. **Premier lancement :** charger tout l’historique disponible, sans ne garder que la dernière version ni filtrer les suppressions.
2. **Lancements suivants :** lire une seule fois le maximum de `meta.ts` déjà chargé dans la table cible du modèle, puis calculer la borne de reprise en retranchant une fenêtre de recouvrement paramétrable.
3. **Fenêtre :** deux jours est un exemple, pas une valeur validée ni une garantie de complétude. La durée doit être justifiée au regard des retards observés et de la reprise souhaitée.
4. **Prédicat inclusif :** reprendre `meta.ts >= borne`, afin d’inclure les versions partageant l’horodatage de la borne. Comparer directement la colonne à une constante typée, en préservant sa précision temporelle et le fuseau retenu.
5. **Réexécution sans doublons :** dédupliquer les versions reprises à l’intérieur de l’extraction et vis-à-vis de celles déjà chargées, selon la stratégie validée. Dédupliquer une version répétée ne signifie pas réduire un objet à son dernier état.
6. **Suppressions conservées :** garder les lignes `meta.deleted = true` dans l’historique. Elles sont nécessaires à la reconstruction des états et suppressions.
7. **Cible vide :** si le maximum est absent, reprendre tout l’historique disponible ; ne pas laisser une comparaison avec une borne NULL exclure les lignes.

La logique de borne est, en notation de principe : `borne = max_cible(meta.ts) − fenêtre`. Le filtre attendu, illustratif et non SQL prêt à exécuter, est :

```sql
WHERE `meta.ts` >= <borne_constante_typee>
```

**Aucun filtrage limité à « hier ».** Ne pas exiger non plus que `updateDate` soit le même jour que `meta.ts` : modification de la fiche et publication CDC peuvent avoir des dates différentes. Une autre date d’import créée par nos traitements reste distincte de ces dates source.

### Identités de version et conflits

| Objet | Clé candidate / principe | Validation encore nécessaire |
| --- | --- | --- |
| Objet raw possédant un `id` | Tuple `meta.customer`, `id`, `meta.ts` | Vérifier son unicité réelle pour chaque table. Les versions d’un même objet à des dates différentes doivent toutes rester présentes |
| Plusieurs lignes identiques d’une même version | Répétitions à dédupliquer | La réexécution doit garder le même ensemble de versions |
| Plusieurs contenus différents sous la même clé candidate | Collision à traiter explicitement | Définir une règle et, si nécessaire, une clé complétée à partir d’informations réellement disponibles ; ne pas éliminer arbitrairement une version ni inventer un ordre temporel |
| `raw.dictionaries` | Pas d’`id` d’objet documenté ; tenant, langue et horodatage sont des composantes candidates selon le grain de la table | Adapter et vérifier la clé, y compris les conflits de contenu ; ne pas appliquer mécaniquement la clé des objets avec id |

Un **modèle de lecture courante séparé** pourra sélectionner la dernière version de chaque objet, puis exclure les objets supprimés. Inverser cet ordre risquerait de faire réapparaître une ancienne version d’un objet supprimé. Les collisions d’horodatage doivent aussi être résolues avant de prétendre connaître un dernier état unique.

### Retards et échecs : ce que la borne ne garantit pas

- Une version nouvellement reçue avec un `meta.ts` ancien, situé avant la fenêtre de recouvrement, peut être manquée. Prévoir une réconciliation ou une reprise adaptée ; mécanisme, fréquence et périmètre à choisir avant implémentation.
- Le maximum de la cible est une borne simple calculée sur son contenu, **pas un journal indépendant des exécutions réussies**. Vérifier si un échec partiel peut faire avancer ce maximum tout en laissant des lignes manquantes, et définir la reprise correspondante.
- La préservation de toutes les versions reste l’objectif ; la fenêtre seule n’en constitue pas la preuve. Les cas limites doivent être vérifiés sur la stratégie retenue.

### Choix techniques et contrôles avant implémentation

| Sujet | Travail prévu, non exécuté à ce stade |
| --- | --- |
| Compatibilité dbt-clickhouse | Vérifier les versions installées et choisir une stratégie réellement supportée qui conserve les versions et assure la déduplication. Aucune stratégie particulière n’est encore retenue |
| Utilité de l’incrémental | Décider par modèle si une vue suffit ou si une table incrémentale apporte un bénéfice justifié ; ne pas matérialiser chaque couche par principe |
| Borne et performance | Calculer la borne une fois, filtrer la colonne sans transformation et vérifier les lectures ainsi que le plan ClickHouse. Une conversion `toDateTime64` sur une constante n’est pas en soi un problème ; déplacer le calcul dans Jinja n’est pas réputé plus rapide sans mesure |
| Premier chargement / cible vide | Vérifier le chargement de tout l’historique disponible et le traitement du maximum absent |
| Réexécution / recouvrement | Vérifier l’absence de doublons et la conservation de l’ensemble des versions après plusieurs lancements |
| Horodatages identiques | Tester la borne inclusive, les objets distincts au même timestamp et les contenus différents sous une même clé candidate |
| Suppressions | Vérifier leur conservation historique et le résultat « dernière version puis suppression » de la lecture courante |
| Dates source distinctes | Vérifier qu’une publication CDC un autre jour que `updateDate` est bien reprise |
| Arrivées tardives | Tester les cas à l’intérieur et hors de la fenêtre, avec la réconciliation/reprise prévue |
| Échec partiel | Vérifier le contenu réellement écrit, l’évolution du maximum cible et la reprise sans perte ni doublon |

**Portée :** ce protocole préserve un historique CDC déjà présent dans `raw`. La constitution d’un historique à partir des états courants HubSpot ou des références reste un chantier distinct décrit plus haut ; ne pas leur attribuer un `meta.ts` ou une clé CDC qu’ils ne possèdent pas. Ces principes ne tranchent ni la rétention détaillée ni les règles métier des KPI.

## Tables à couvrir

| Table source | Colonnes physiques identifiées | Usage principal |
| --- | ---: | --- |
| [raw.opportunities](#raw-opportunities) | 24 | Dossiers, états, valeurs, responsables, origines et parcours observés. |
| [raw.actions](#raw-actions) | 16 | Actions, demandes/séances de démo, agenda et liens polymorphes. |
| [raw.companies](#raw-companies) | 11 | Identité cliente, contexte société et origine candidate. |
| [raw.contacts](#raw-contacts) | 9 | Identité de contact, liens société et sources d’acquisition candidates. |
| [raw.ressources](#raw-ressources) | 9 | Collaborateurs et contexte de la comparaison individuelle. |
| [raw.businessunits](#raw-businessunits) | 6 | Équipes et listes historisées de membres. |
| [raw.agencies](#raw-agencies) | 6 | Contexte agence/pays ; différent de l’équipe commerciale. |
| [raw.poles](#raw-poles) | 6 | Profil de société ; différent de l’équipe commerciale. |
| [raw.dictionaries](#raw-dictionaries) | 11 | Libellés et propriétés des codes, par version et langue. |
| [raw.projects](#raw-projects) | 11 | Liens abonnement/projet/client/dossier et périodes projet. |
| [raw.deliveries](#raw-deliveries) | 13 | Lignes d’abonnement, prix/quantités, états et périodes. |
| [hubspot.contacts](#hubspot-contacts) | 14 | Identités CRM, provenance marketing et première conversion connue. |
| [hubspot.deals](#hubspot-deals) | 16 | Représentation HubSpot du dossier, montants et statuts candidats. |
| [ref.sales_targets](#ref-sales_targets) | 4 | Objectifs mensuels équipe × indicateur ; nécessaires malgré le périmètre raw/hubspot initial. |
| [ref.stage_probabilities](#ref-stage_probabilities) | 3 | Probabilités de signature par étape × segment ; pas d’historique de validité documenté. |

## Colonnes regroupées par table

<a id="raw-opportunities"></a>
### raw.opportunities

Dossiers, états, valeurs, responsables, origines et parcours observés.

| Colonne physique | Type documenté | Utilité / dépendances / extractions JSON |
| --- | --- | --- |
| `meta.customer` | `String` | Identité, version, suppression/archivage ou repérage de la source.<br>Champ ou source candidate du périmètre — repères : [I01](correspondance_champs_clickhouse.md#i01) ; autres usages dans la décomposition. |
| `id` | `Int64` | Identité, version, suppression/archivage ou repérage de la source.<br>Champ ou source candidate du périmètre — repères : [I02](correspondance_champs_clickhouse.md#i02), [I14](correspondance_champs_clickhouse.md#i14), [T03](correspondance_champs_clickhouse.md#t03), [E01](correspondance_champs_clickhouse.md#e01), [E14](correspondance_champs_clickhouse.md#e14) ; autres usages dans la décomposition. |
| `meta.deleted` | `Bool` | Identité, version, suppression/archivage ou repérage de la source.<br>Champ ou source candidate du périmètre — repères : [T02](correspondance_champs_clickhouse.md#t02), [T03](correspondance_champs_clickhouse.md#t03), [E04](correspondance_champs_clickhouse.md#e04) ; autres usages dans la décomposition. |
| `meta.ts` | `DateTime64(3)` | Identité, version, suppression/archivage ou repérage de la source.<br>Champ ou source candidate du périmètre — repères : [I14](correspondance_champs_clickhouse.md#i14), [T01](correspondance_champs_clickhouse.md#t01), [T03](correspondance_champs_clickhouse.md#t03), [T06](correspondance_champs_clickhouse.md#t06), [T08](correspondance_champs_clickhouse.md#t08) ; autres usages dans la décomposition. |
| `state` | `Nullable(Int64)` | Étape du besoin. Libellés et propriétés de chaque code dans le référentiel des étapes.<br>Champ ou source candidate du périmètre — repères : [I14](correspondance_champs_clickhouse.md#i14), [P04](correspondance_champs_clickhouse.md#p04), [P06](correspondance_champs_clickhouse.md#p06), [P07](correspondance_champs_clickhouse.md#p07), [P13](correspondance_champs_clickhouse.md#p13) ; autres usages dans la décomposition. |
| `typeOf` | `Nullable(Int64)` | Type de besoin : nouveau client, upsell, formation…<br>Champ ou source candidate du périmètre — repères : [P02](correspondance_champs_clickhouse.md#p02), [E14](correspondance_champs_clickhouse.md#e14), [A14](correspondance_champs_clickhouse.md#a14) ; autres usages dans la décomposition. |
| `title` | `String` | Intitulé libre du besoin.<br>Champ ou source candidate du périmètre — repères : [P01](correspondance_champs_clickhouse.md#p01). |
| `reference` | `String` | Référence lisible générée par Boond à la création.<br>Champ ou source candidate du périmètre — repères : [P01](correspondance_champs_clickhouse.md#p01). |
| `creationDate` | `Nullable(DateTime64(3))` | Date de création du besoin dans Boond.<br>Champ ou source candidate du périmètre — repères : [T06](correspondance_champs_clickhouse.md#t06), [P03](correspondance_champs_clickhouse.md#p03), [P07](correspondance_champs_clickhouse.md#p07), [E10](correspondance_champs_clickhouse.md#e10), [E11](correspondance_champs_clickhouse.md#e11) ; autres usages dans la décomposition. |
| `updateDate` | `Nullable(DateTime64(3))` | Date de la dernière modification de la fiche.<br>Champ ou source candidate du périmètre — repères : [T04](correspondance_champs_clickhouse.md#t04). |
| `startDate` | `Nullable(DateTime64(3))` | Date de démarrage souhaitée par le prospect.<br>Proposition ou option seulement — repères : [X09](correspondance_champs_clickhouse.md#x09). |
| `closingDate` | `Nullable(DateTime64(3))` | Date de closing saisie par le commercial sur la fiche.<br>Champ ou source candidate du périmètre — repères : [P12](correspondance_champs_clickhouse.md#p12), [P13](correspondance_champs_clickhouse.md#p13) ; autres usages dans la décomposition. |
| `turnoverEstimatedExcludingTax` | `Nullable(Float64)` | Montant estimé du besoin, hors taxes, saisi par le commercial.<br>Champ ou source candidate du périmètre — repères : [P08](correspondance_champs_clickhouse.md#p08), [P09](correspondance_champs_clickhouse.md#p09), [P11](correspondance_champs_clickhouse.md#p11), [A12](correspondance_champs_clickhouse.md#a12), [A16](correspondance_champs_clickhouse.md#a16) ; autres usages dans la décomposition. |
| `weighting` | `Nullable(Int64)` | Pondération du besoin en pourcentage.<br>Champ ou source candidate du périmètre — repères : [P10](correspondance_champs_clickhouse.md#p10), [P11](correspondance_champs_clickhouse.md#p11), [K13](correspondance_champs_clickhouse.md#k13) ; autres usages dans la décomposition. |
| `turnoverWeightedExcludingTax` | `Nullable(Float64)` | Montant pondéré : montant estimé × pondération.<br>Champ ou source candidate du périmètre — repères : [P11](correspondance_champs_clickhouse.md#p11). |
| `exchangeRate` | `Nullable(Float64)` | Taux de change entre la devise du besoin et celle de l'agence.<br>Champ ou source candidate du périmètre — repères : [P14](correspondance_champs_clickhouse.md#p14). |
| `origin.typeOf` | `Nullable(Int64)` | Origine du besoin (canal par lequel il est arrivé).<br>Champ ou source candidate du périmètre — repères : [C01](correspondance_champs_clickhouse.md#c01). |
| `origin.detail` | `String` | Précision libre sur l'origine.<br>Champ ou source candidate du périmètre — repères : [C01](correspondance_champs_clickhouse.md#c01). |
| `relationships.mainManager.data.id` | `Nullable(Int64)` | Responsable de l'enregistrement : le collaborateur qui le porte.<br>Champ ou source candidate du périmètre — repères : [R01](correspondance_champs_clickhouse.md#r01), [R07](correspondance_champs_clickhouse.md#r07), [R10](correspondance_champs_clickhouse.md#r10), [X04](correspondance_champs_clickhouse.md#x04). |
| `relationships.createdBy.data.id` | `Nullable(Int64)` | Collaborateur (ou robot) qui a créé l'enregistrement.<br>Champ ou source candidate du périmètre — repères : [R12](correspondance_champs_clickhouse.md#r12). |
| `relationships.company.data.id` | `Nullable(Int64)` | Société prospect ou cliente du besoin.<br>Champ ou source candidate du périmètre — repères : [I04](correspondance_champs_clickhouse.md#i04) ; autres usages dans la décomposition. |
| `relationships.contact.data.id` | `Nullable(Int64)` | Contact principal du besoin.<br>Champ ou source candidate du périmètre — repères : [I05](correspondance_champs_clickhouse.md#i05), [I09](correspondance_champs_clickhouse.md#i09) ; autres usages dans la décomposition. |
| `relationships.agency.data.id` | `Nullable(Int64)` | Agence Boond qui porte le besoin.<br>Champ ou source candidate du périmètre — repères : [P14](correspondance_champs_clickhouse.md#p14), [R08](correspondance_champs_clickhouse.md#r08). |
| `attributes` | `String` | Attributs complémentaires en JSON, dont `stateReason` : la raison de perte choisie dans la liste de l'étape.<br>Proposition ou option seulement — repères : [P15](correspondance_champs_clickhouse.md#p15), [X07](correspondance_champs_clickhouse.md#x07).<br>Clé documentée : stateReason (motif, analyse candidate). |

<a id="raw-actions"></a>
### raw.actions

Actions, demandes/séances de démo, agenda et liens polymorphes.

| Colonne physique | Type documenté | Utilité / dépendances / extractions JSON |
| --- | --- | --- |
| `meta.customer` | `String` | Identité, version, suppression/archivage ou repérage de la source.<br>Champ ou source candidate du périmètre — repères : [I01](correspondance_champs_clickhouse.md#i01) ; autres usages dans la décomposition. |
| `id` | `Int64` | Identité, version, suppression/archivage ou repérage de la source.<br>Champ ou source candidate du périmètre — repères : [I07](correspondance_champs_clickhouse.md#i07), [D08](correspondance_champs_clickhouse.md#d08), [D11](correspondance_champs_clickhouse.md#d11) ; autres usages dans la décomposition. |
| `meta.deleted` | `Bool` | Identité, version, suppression/archivage ou repérage de la source.<br>Champ ou source candidate du périmètre — repères : [T02](correspondance_champs_clickhouse.md#t02) ; autres usages dans la décomposition. |
| `meta.ts` | `DateTime64(3)` | Identité, version, suppression/archivage ou repérage de la source.<br>Champ ou source candidate du périmètre — repères : [T01](correspondance_champs_clickhouse.md#t01), [D07](correspondance_champs_clickhouse.md#d07) ; autres usages dans la décomposition. |
| `typeOf` | `Nullable(Int64)` | Type d'action : appel, démo, demande de démo…<br>Champ ou source candidate du périmètre — repères : [D01](correspondance_champs_clickhouse.md#d01), [D06](correspondance_champs_clickhouse.md#d06), [D07](correspondance_champs_clickhouse.md#d07), [D08](correspondance_champs_clickhouse.md#d08), [D11](correspondance_champs_clickhouse.md#d11) ; autres usages dans la décomposition. |
| `title` | `String` | Intitulé de l'action.<br>Champ ou source candidate du périmètre — repères : [D02](correspondance_champs_clickhouse.md#d02). |
| `startDate` | `Nullable(DateTime64(3))` | Début de l'action dans l'agenda.<br>Champ ou source candidate du périmètre — repères : [D04](correspondance_champs_clickhouse.md#d04), [D05](correspondance_champs_clickhouse.md#d05), [D07](correspondance_champs_clickhouse.md#d07), [D08](correspondance_champs_clickhouse.md#d08), [X06](correspondance_champs_clickhouse.md#x06). |
| `endDate` | `Nullable(DateTime64(3))` | Fin de l'action dans l'agenda.<br>Champ ou source candidate du périmètre — repères : [D04](correspondance_champs_clickhouse.md#d04), [D05](correspondance_champs_clickhouse.md#d05), [D07](correspondance_champs_clickhouse.md#d07), [X06](correspondance_champs_clickhouse.md#x06) ; autres usages dans la décomposition. |
| `creationDate` | `Nullable(DateTime64(3))` | Date de création de l'action.<br>Champ ou source candidate du périmètre — repères : [D03](correspondance_champs_clickhouse.md#d03), [D08](correspondance_champs_clickhouse.md#d08). |
| `updateDate` | `Nullable(DateTime64(3))` | Date de la dernière modification.<br>Champ ou source candidate du périmètre — repères : [T04](correspondance_champs_clickhouse.md#t04). |
| `relationships.mainManager.data.id` | `Nullable(Int64)` | Responsable de l'enregistrement : le collaborateur qui le porte.<br>Champ ou source candidate du périmètre — repères : [R02](correspondance_champs_clickhouse.md#r02). |
| `relationships.createdBy.data.id` | `Nullable(Int64)` | Collaborateur (ou robot) qui a créé l'enregistrement.<br>Champ ou source candidate du périmètre — repères : [R12](correspondance_champs_clickhouse.md#r12). |
| `relationships.company.data.id` | `Nullable(Int64)` | Société de la fiche à laquelle l'action est rattachée.<br>Champ ou source candidate du périmètre — repères : [I04](correspondance_champs_clickhouse.md#i04) ; autres usages dans la décomposition. |
| `relationships.dependsOn.data.id` | `Nullable(Int64)` | Identifiant de la fiche à laquelle l'action est rattachée. Le type de fiche est dans la colonne suivante.<br>Champ ou source candidate du périmètre — repères : [I08](correspondance_champs_clickhouse.md#i08), [I09](correspondance_champs_clickhouse.md#i09), [T07](correspondance_champs_clickhouse.md#t07), [D08](correspondance_champs_clickhouse.md#d08). |
| `relationships.dependsOn.data.type` | `LowCardinality(String)` | Type de la fiche rattachée : `contact`, `opportunity`, `company`…<br>Champ ou source candidate du périmètre — repères : [I08](correspondance_champs_clickhouse.md#i08), [I09](correspondance_champs_clickhouse.md#i09), [T07](correspondance_champs_clickhouse.md#t07), [D08](correspondance_champs_clickhouse.md#d08). |
| `attributes` | `String` | Attributs en JSON, dont `text` : le contenu de l'action (HTML).<br>Champ ou source candidate du périmètre — repères : [D06](correspondance_champs_clickhouse.md#d06).<br>Clé documentée : text (HTML). Source candidate pour examiner les preuves ; aucune règle fiable de réalisation validée. |

<a id="raw-companies"></a>
### raw.companies

Identité cliente, contexte société et origine candidate.

| Colonne physique | Type documenté | Utilité / dépendances / extractions JSON |
| --- | --- | --- |
| `meta.customer` | `String` | Identité, version, suppression/archivage ou repérage de la source.<br>Champ ou source candidate du périmètre — repères : [I01](correspondance_champs_clickhouse.md#i01) ; autres usages dans la décomposition. |
| `id` | `Int64` | Identité, version, suppression/archivage ou repérage de la source.<br>Champ ou source candidate du périmètre — repères : [I04](correspondance_champs_clickhouse.md#i04) ; autres usages dans la décomposition. |
| `meta.deleted` | `Bool` | Identité, version, suppression/archivage ou repérage de la source.<br>Champ ou source candidate du périmètre — repères : [C09](correspondance_champs_clickhouse.md#c09). |
| `meta.ts` | `DateTime64(3)` | Identité, version, suppression/archivage ou repérage de la source.<br>Champ ou source candidate du périmètre — repères : [C09](correspondance_champs_clickhouse.md#c09). |
| `name` | `String` | Raison sociale.<br>Champ ou source candidate du périmètre — repères : [C11](correspondance_champs_clickhouse.md#c11). |
| `country` | `String` | Pays.<br>Champ ou source candidate du périmètre — repères : [C11](correspondance_champs_clickhouse.md#c11). |
| `staff` | `Nullable(Int64)` | Effectif de la société.<br>Champ ou source candidate du périmètre — repères : [C11](correspondance_champs_clickhouse.md#c11). |
| `origin.typeOf` | `Nullable(Int64)` | Origine de la société.<br>Champ ou source candidate du périmètre — repères : [C03](correspondance_champs_clickhouse.md#c03). |
| `relationships.pole.data.id` | `Nullable(Int64)` | Pôle de la société (profil client cible).<br>Champ ou source candidate du périmètre — repères : [C12](correspondance_champs_clickhouse.md#c12). |
| `relationships.mainManager.data.id` | `Nullable(Int64)` | Responsable de l'enregistrement : le collaborateur qui le porte.<br>Champ ou source candidate du périmètre — repères : [R02](correspondance_champs_clickhouse.md#r02). |
| `relationships.agency.data.id` | `Nullable(Int64)` | Agence Boond de rattachement.<br>Champ ou source candidate du périmètre — repères : [R08](correspondance_champs_clickhouse.md#r08). |

<a id="raw-contacts"></a>
### raw.contacts

Identité de contact, liens société et sources d’acquisition candidates.

| Colonne physique | Type documenté | Utilité / dépendances / extractions JSON |
| --- | --- | --- |
| `meta.customer` | `String` | Identité, version, suppression/archivage ou repérage de la source.<br>Champ ou source candidate du périmètre — repères : [I01](correspondance_champs_clickhouse.md#i01) ; autres usages dans la décomposition. |
| `id` | `Int64` | Identité, version, suppression/archivage ou repérage de la source.<br>Champ ou source candidate du périmètre — repères : [I05](correspondance_champs_clickhouse.md#i05) ; autres usages dans la décomposition. |
| `meta.deleted` | `Bool` | Identité, version, suppression/archivage ou repérage de la source.<br>Champ ou source candidate du périmètre — repères : [C09](correspondance_champs_clickhouse.md#c09), [X04](correspondance_champs_clickhouse.md#x04). |
| `meta.ts` | `DateTime64(3)` | Identité, version, suppression/archivage ou repérage de la source.<br>Champ ou source candidate du périmètre — repères : [X04](correspondance_champs_clickhouse.md#x04) ; autres usages dans la décomposition. |
| `state` | `Nullable(Int64)` | État du contact.<br>Champ ou source candidate du périmètre — repères : [C07](correspondance_champs_clickhouse.md#c07). |
| `origin.typeOf` | `Nullable(Int64)` | Origine du contact.<br>Champ ou source candidate du périmètre — repères : [C03](correspondance_champs_clickhouse.md#c03). |
| `creationDate` | `Nullable(DateTime64(3))` | Date de création de la fiche.<br>Champ ou source candidate du périmètre — repères : [C08](correspondance_champs_clickhouse.md#c08) ; autres usages dans la décomposition. |
| `relationships.company.data.id` | `Nullable(Int64)` | Société du contact.<br>Champ ou source candidate du périmètre — repères : [I04](correspondance_champs_clickhouse.md#i04) ; autres usages dans la décomposition. |
| `relationships.mainManager.data.id` | `Nullable(Int64)` | Responsable de l'enregistrement : le collaborateur qui le porte.<br>Proposition ou option seulement — repères : [X04](correspondance_champs_clickhouse.md#x04). |

<a id="raw-ressources"></a>
### raw.ressources

Collaborateurs et contexte de la comparaison individuelle.

| Colonne physique | Type documenté | Utilité / dépendances / extractions JSON |
| --- | --- | --- |
| `meta.customer` | `String` | Identité, version, suppression/archivage ou repérage de la source.<br>Champ ou source candidate du périmètre — repères : [R04](correspondance_champs_clickhouse.md#r04), [R06](correspondance_champs_clickhouse.md#r06), [R09](correspondance_champs_clickhouse.md#r09). |
| `id` | `Int64` | Identité, version, suppression/archivage ou repérage de la source.<br>Champ ou source candidate du périmètre — repères : [R03](correspondance_champs_clickhouse.md#r03), [R09](correspondance_champs_clickhouse.md#r09) ; autres usages dans la décomposition. |
| `meta.deleted` | `Bool` | Identité, version, suppression/archivage ou repérage de la source.<br>Champ ou source candidate du périmètre — repères : [R04](correspondance_champs_clickhouse.md#r04). |
| `meta.ts` | `DateTime64(3)` | Identité, version, suppression/archivage ou repérage de la source.<br>Champ ou source candidate du périmètre — repères : [T01](correspondance_champs_clickhouse.md#t01) ; autres usages dans la décomposition. |
| `firstName` | `String` | Prénom.<br>Champ ou source candidate du périmètre — repères : [R03](correspondance_champs_clickhouse.md#r03). |
| `lastName` | `String` | Nom.<br>Champ ou source candidate du périmètre — repères : [R03](correspondance_champs_clickhouse.md#r03). |
| `title` | `String` | Intitulé de poste.<br>Champ ou source candidate du périmètre — repères : [R04](correspondance_champs_clickhouse.md#r04). |
| `state` | `Nullable(Int64)` | État du collaborateur (en poste, sorti).<br>Champ ou source candidate du périmètre — repères : [R04](correspondance_champs_clickhouse.md#r04). |
| `relationships.agency.data.id` | `Nullable(Int64)` | Agence du collaborateur.<br>Champ ou source candidate du périmètre — repères : [R08](correspondance_champs_clickhouse.md#r08). |

<a id="raw-businessunits"></a>
### raw.businessunits

Équipes et listes historisées de membres.

| Colonne physique | Type documenté | Utilité / dépendances / extractions JSON |
| --- | --- | --- |
| `meta.customer` | `String` | Identité, version, suppression/archivage ou repérage de la source.<br>Champ ou source candidate du périmètre — repères : [R06](correspondance_champs_clickhouse.md#r06), [R13](correspondance_champs_clickhouse.md#r13). |
| `id` | `Int64` | Identité, version, suppression/archivage ou repérage de la source.<br>Champ ou source candidate du périmètre — repères : [R05](correspondance_champs_clickhouse.md#r05), [R13](correspondance_champs_clickhouse.md#r13) ; autres usages dans la décomposition. |
| `meta.deleted` | `Bool` | Identité, version, suppression/archivage ou repérage de la source.<br>Champ ou source candidate du périmètre — repères : [R06](correspondance_champs_clickhouse.md#r06). |
| `meta.ts` | `DateTime64(3)` | Identité, version, suppression/archivage ou repérage de la source.<br>Champ ou source candidate du périmètre — repères : [T01](correspondance_champs_clickhouse.md#t01), [R06](correspondance_champs_clickhouse.md#r06), [R07](correspondance_champs_clickhouse.md#r07). |
| `name` | `String` | Nom de l'équipe.<br>Champ ou source candidate du périmètre — repères : [R05](correspondance_champs_clickhouse.md#r05), [R13](correspondance_champs_clickhouse.md#r13). |
| `relationships.includedManagers.data` | `String` | Membres de l'équipe, en JSON : liste de `{"id": …, "type": "resource"}`.<br>Champ ou source candidate du périmètre — repères : [R06](correspondance_champs_clickhouse.md#r06), [R07](correspondance_champs_clickhouse.md#r07).<br>Tableau JSON ; membres avec id et type. Le nom de la colonne contient des points ; id/type sont des propriétés du contenu. |

<a id="raw-agencies"></a>
### raw.agencies

Contexte agence/pays ; différent de l’équipe commerciale.

| Colonne physique | Type documenté | Utilité / dépendances / extractions JSON |
| --- | --- | --- |
| `meta.customer` | `String` | Identité, version, suppression/archivage ou repérage de la source.<br>Champ ou source candidate du périmètre — repères : [P14](correspondance_champs_clickhouse.md#p14). |
| `id` | `Int64` | Identité, version, suppression/archivage ou repérage de la source.<br>Champ ou source candidate du périmètre — repères : [R08](correspondance_champs_clickhouse.md#r08) ; autres usages dans la décomposition. |
| `meta.deleted` | `Bool` | Identité, version, suppression/archivage ou repérage de la source. |
| `meta.ts` | `DateTime64(3)` | Identité, version, suppression/archivage ou repérage de la source. |
| `name` | `String` | Nom de l'agence.<br>Champ ou source candidate du périmètre — repères : [R08](correspondance_champs_clickhouse.md#r08). |
| `country` | `String` | Pays de l'agence.<br>Champ ou source candidate du périmètre — repères : [R08](correspondance_champs_clickhouse.md#r08). |

<a id="raw-poles"></a>
### raw.poles

Profil de société ; différent de l’équipe commerciale.

| Colonne physique | Type documenté | Utilité / dépendances / extractions JSON |
| --- | --- | --- |
| `meta.customer` | `String` | Identité, version, suppression/archivage ou repérage de la source. |
| `id` | `Int64` | Identité, version, suppression/archivage ou repérage de la source.<br>Champ ou source candidate du périmètre — repères : [C12](correspondance_champs_clickhouse.md#c12). |
| `meta.deleted` | `Bool` | Identité, version, suppression/archivage ou repérage de la source. |
| `meta.ts` | `DateTime64(3)` | Identité, version, suppression/archivage ou repérage de la source. |
| `name` | `String` | Nom du pôle.<br>Champ ou source candidate du périmètre — repères : [C12](correspondance_champs_clickhouse.md#c12). |
| `state` | `Bool` | Pôle actif.<br>Champ ou source candidate du périmètre — repères : [C12](correspondance_champs_clickhouse.md#c12). |

<a id="raw-dictionaries"></a>
### raw.dictionaries

Libellés et propriétés des codes, par version et langue.

| Colonne physique | Type documenté | Utilité / dépendances / extractions JSON |
| --- | --- | --- |
| `meta.customer` | `String` | Identité, version, suppression/archivage ou repérage de la source.<br>Champ ou source candidate du périmètre — repères : [T09](correspondance_champs_clickhouse.md#t09), [P06](correspondance_champs_clickhouse.md#p06), [P10](correspondance_champs_clickhouse.md#p10), [P15](correspondance_champs_clickhouse.md#p15), [A10](correspondance_champs_clickhouse.md#a10). |
| `meta.deleted` | `Bool` | Identité, version, suppression/archivage ou repérage de la source.<br>Champ ou source candidate du périmètre — repères : [T09](correspondance_champs_clickhouse.md#t09), [P06](correspondance_champs_clickhouse.md#p06), [P10](correspondance_champs_clickhouse.md#p10), [P15](correspondance_champs_clickhouse.md#p15), [A10](correspondance_champs_clickhouse.md#a10). |
| `meta.ts` | `DateTime64(3)` | Identité, version, suppression/archivage ou repérage de la source.<br>Champ ou source candidate du périmètre — repères : [T09](correspondance_champs_clickhouse.md#t09) ; autres usages dans la décomposition. |
| `meta.language` | `String` | Identité, version, suppression/archivage ou repérage de la source.<br>Champ ou source candidate du périmètre — repères : [P05](correspondance_champs_clickhouse.md#p05) ; autres usages dans la décomposition. |
| `setting.state.opportunity` | `Nullable(String)` | Étapes des besoins. Chaque entrée : `id`, `value` (libellé), `active` (le besoin est encore en cours), `isEnabled` (étape proposée dans l'interface), `weighting` (pondération), `reason` (raisons proposées quand on choisit cette étape).<br>Champ ou source candidate du périmètre — repères : [P05](correspondance_champs_clickhouse.md#p05), [P06](correspondance_champs_clickhouse.md#p06), [P10](correspondance_champs_clickhouse.md#p10), [P15](correspondance_champs_clickhouse.md#p15) ; autres usages dans la décomposition.<br>Entrées JSON : id, value, active, isEnabled, weighting, reason ; codes/libellés et propriétés distincts. |
| `setting.typeOf.project` | `LowCardinality(String)` | Types de besoin et de projet.<br>Champ ou source candidate du périmètre — repères : [P02](correspondance_champs_clickhouse.md#p02), [A05](correspondance_champs_clickhouse.md#a05) ; autres usages dans la décomposition.<br>Référentiel JSON à décoder par code et libellé ; ne pas confondre la colonne conteneur avec une colonne physique par propriété. |
| `setting.origin` | `String` | Origines : canaux d'arrivée des besoins, sociétés et contacts.<br>Champ ou source candidate du périmètre — repères : [C02](correspondance_champs_clickhouse.md#c02), [C10](correspondance_champs_clickhouse.md#c10).<br>Référentiel JSON à décoder par code et libellé ; ne pas confondre la colonne conteneur avec une colonne physique par propriété. |
| `setting.action.contact` | `String` | Types d'action possibles sur un contact.<br>Champ ou source candidate du périmètre — repères : [D01](correspondance_champs_clickhouse.md#d01), [X05](correspondance_champs_clickhouse.md#x05).<br>Référentiel JSON à décoder par code et libellé ; ne pas confondre la colonne conteneur avec une colonne physique par propriété. |
| `setting.state.contact` | `Nullable(String)` | États des contacts.<br>Champ ou source candidate du périmètre — repères : [C07](correspondance_champs_clickhouse.md#c07).<br>Référentiel JSON à décoder par code et libellé ; ne pas confondre la colonne conteneur avec une colonne physique par propriété. |
| `setting.state.resource` | `Nullable(String)` | États des collaborateurs.<br>Champ ou source candidate du périmètre — repères : [R04](correspondance_champs_clickhouse.md#r04).<br>Référentiel JSON à décoder par code et libellé ; ne pas confondre la colonne conteneur avec une colonne physique par propriété. |
| `setting.state.delivery` | `Nullable(String)` | États des livraisons.<br>Champ ou source candidate du périmètre — repères : [A02](correspondance_champs_clickhouse.md#a02) ; autres usages dans la décomposition.<br>Référentiel JSON à décoder par code et libellé ; ne pas confondre la colonne conteneur avec une colonne physique par propriété. |

<a id="raw-projects"></a>
### raw.projects

Liens abonnement/projet/client/dossier et périodes projet.

| Colonne physique | Type documenté | Utilité / dépendances / extractions JSON |
| --- | --- | --- |
| `meta.customer` | `String` | Identité, version, suppression/archivage ou repérage de la source.<br>Champ ou source candidate du périmètre — repères : [I01](correspondance_champs_clickhouse.md#i01) ; autres usages dans la décomposition. |
| `id` | `Int64` | Identité, version, suppression/archivage ou repérage de la source.<br>Champ ou source candidate du périmètre — repères : [I10](correspondance_champs_clickhouse.md#i10) ; autres usages dans la décomposition. |
| `meta.deleted` | `Bool` | Identité, version, suppression/archivage ou repérage de la source.<br>Champ ou source candidate du périmètre — repères : [T02](correspondance_champs_clickhouse.md#t02) ; autres usages dans la décomposition. |
| `meta.ts` | `DateTime64(3)` | Identité, version, suppression/archivage ou repérage de la source.<br>Champ ou source candidate du périmètre — repères : [T01](correspondance_champs_clickhouse.md#t01) ; autres usages dans la décomposition. |
| `reference` | `String` | Référence du projet.<br>Champ ou source candidate du périmètre — repères : [A01](correspondance_champs_clickhouse.md#a01). |
| `typeOf` | `Nullable(Int64)` | Type de projet.<br>Champ ou source candidate du périmètre — repères : [A05](correspondance_champs_clickhouse.md#a05) ; autres usages dans la décomposition. |
| `startDate` | `Nullable(DateTime64(3))` | Début du projet.<br>Champ ou source candidate du périmètre — repères : [A04](correspondance_champs_clickhouse.md#a04) ; autres usages dans la décomposition. |
| `endDate` | `Nullable(DateTime64(3))` | Fin du projet.<br>Champ ou source candidate du périmètre — repères : [A04](correspondance_champs_clickhouse.md#a04) ; autres usages dans la décomposition. |
| `relationships.opportunity.data.id` | `Nullable(Int64)` | Besoin d'origine du projet.<br>Champ ou source candidate du périmètre — repères : [I11](correspondance_champs_clickhouse.md#i11), [A12](correspondance_champs_clickhouse.md#a12), [A14](correspondance_champs_clickhouse.md#a14). |
| `relationships.company.data.id` | `Nullable(Int64)` | Société cliente.<br>Champ ou source candidate du périmètre — repères : [I04](correspondance_champs_clickhouse.md#i04), [F01](correspondance_champs_clickhouse.md#f01) ; autres usages dans la décomposition. |
| `relationships.mainManager.data.id` | `Nullable(Int64)` | Responsable de l'enregistrement : le collaborateur qui le porte.<br>Champ ou source candidate du périmètre — repères : [R02](correspondance_champs_clickhouse.md#r02). |

<a id="raw-deliveries"></a>
### raw.deliveries

Lignes d’abonnement, prix/quantités, états et périodes.

| Colonne physique | Type documenté | Utilité / dépendances / extractions JSON |
| --- | --- | --- |
| `meta.customer` | `String` | Identité, version, suppression/archivage ou repérage de la source.<br>Champ ou source candidate du périmètre — repères : [I01](correspondance_champs_clickhouse.md#i01) ; autres usages dans la décomposition. |
| `id` | `Int64` | Identité, version, suppression/archivage ou repérage de la source.<br>Champ ou source candidate du périmètre — repères : [I12](correspondance_champs_clickhouse.md#i12), [I13](correspondance_champs_clickhouse.md#i13) ; autres usages dans la décomposition. |
| `meta.deleted` | `Bool` | Identité, version, suppression/archivage ou repérage de la source.<br>Champ ou source candidate du périmètre — repères : [T02](correspondance_champs_clickhouse.md#t02), [A10](correspondance_champs_clickhouse.md#a10) ; autres usages dans la décomposition. |
| `meta.ts` | `DateTime64(3)` | Identité, version, suppression/archivage ou repérage de la source.<br>Champ ou source candidate du périmètre — repères : [T01](correspondance_champs_clickhouse.md#t01), [T06](correspondance_champs_clickhouse.md#t06), [A09](correspondance_champs_clickhouse.md#a09), [A10](correspondance_champs_clickhouse.md#a10), [A13](correspondance_champs_clickhouse.md#a13) ; autres usages dans la décomposition. |
| `title` | `String` | Intitulé de la ligne.<br>Champ ou source candidate du périmètre — repères : [A01](correspondance_champs_clickhouse.md#a01). |
| `state` | `Nullable(Int64)` | État de la livraison.<br>Champ ou source candidate du périmètre — repères : [A02](correspondance_champs_clickhouse.md#a02), [A10](correspondance_champs_clickhouse.md#a10), [A13](correspondance_champs_clickhouse.md#a13), [F05](correspondance_champs_clickhouse.md#f05) ; autres usages dans la décomposition. |
| `startDate` | `Nullable(DateTime64(3))` | Début de la période facturée.<br>Champ ou source candidate du périmètre — repères : [T06](correspondance_champs_clickhouse.md#t06), [A03](correspondance_champs_clickhouse.md#a03), [A10](correspondance_champs_clickhouse.md#a10), [A13](correspondance_champs_clickhouse.md#a13), [F05](correspondance_champs_clickhouse.md#f05) ; autres usages dans la décomposition. |
| `endDate` | `Nullable(DateTime64(3))` | Fin de la période facturée.<br>Champ ou source candidate du périmètre — repères : [A03](correspondance_champs_clickhouse.md#a03), [A10](correspondance_champs_clickhouse.md#a10), [A13](correspondance_champs_clickhouse.md#a13), [F05](correspondance_champs_clickhouse.md#f05) ; autres usages dans la décomposition. |
| `averageDailyPriceExcludingTax` | `Nullable(Float64)` | Tarif de vente journalier moyen HT. Pour une ligne d'abonnement, Boond y range le prix mensuel (quantité facturée × prix unitaire, détail dans `attributes`).<br>Champ ou source candidate du périmètre — repères : [A06](correspondance_champs_clickhouse.md#a06), [A11](correspondance_champs_clickhouse.md#a11), [A12](correspondance_champs_clickhouse.md#a12), [A15](correspondance_champs_clickhouse.md#a15), [F05](correspondance_champs_clickhouse.md#f05) ; autres usages dans la décomposition. |
| `creationDate` | `Nullable(DateTime64(3))` | Date de création.<br>Champ ou source candidate du périmètre — repères : [A09](correspondance_champs_clickhouse.md#a09) ; autres usages dans la décomposition. |
| `updateDate` | `Nullable(DateTime64(3))` | Date de la dernière modification.<br>Champ ou source candidate du périmètre — repères : [T04](correspondance_champs_clickhouse.md#t04), [A09](correspondance_champs_clickhouse.md#a09) ; autres usages dans la décomposition. |
| `relationships.project.data.id` | `Nullable(Int64)` | Projet de la ligne.<br>Champ ou source candidate du périmètre — repères : [I10](correspondance_champs_clickhouse.md#i10), [I13](correspondance_champs_clickhouse.md#i13), [A14](correspondance_champs_clickhouse.md#a14), [F01](correspondance_champs_clickhouse.md#f01) ; autres usages dans la décomposition. |
| `attributes` | `String` | Attributs en JSON : `subscriptionQuantityCharged` (licences facturées) et `subscriptionPriceExcludingTax` (prix unitaire mensuel).<br>Champ ou source candidate du périmètre — repères : [A07](correspondance_champs_clickhouse.md#a07), [A08](correspondance_champs_clickhouse.md#a08), [A15](correspondance_champs_clickhouse.md#a15) ; autres usages dans la décomposition.<br>Clés documentées : subscriptionQuantityCharged, subscriptionPriceExcludingTax. Conserver la colonne physique et distinguer ces deux extractions. |

<a id="hubspot-contacts"></a>
### hubspot.contacts

Identités CRM, provenance marketing et première conversion connue.

| Colonne physique | Type documenté | Utilité / dépendances / extractions JSON |
| --- | --- | --- |
| `id` | `String` | Identité, version, suppression/archivage ou repérage de la source.<br>Champ ou source candidate du périmètre — repères : [I06](correspondance_champs_clickhouse.md#i06) ; autres usages dans la décomposition. |
| `properties_createdate` | `Nullable(DateTime64(3))` | Date de création du contact dans HubSpot.<br>Champ ou source candidate du périmètre — repères : [C08](correspondance_champs_clickhouse.md#c08), [X03](correspondance_champs_clickhouse.md#x03). |
| `properties_lifecyclestage` | `String` | Étape du cycle de vie HubSpot : subscriber, lead, opportunity, customer, other.<br>Champ ou source candidate du périmètre — repères : [C07](correspondance_champs_clickhouse.md#c07). |
| `properties_hs_latest_source` | `String` | Dernière source de trafic connue (ORGANIC_SEARCH, PAID_SEARCH, PAID_SOCIAL, OFFLINE…).<br>Champ ou source candidate du périmètre — repères : [C04](correspondance_champs_clickhouse.md#c04), [C10](correspondance_champs_clickhouse.md#c10). |
| `properties_utm_source` | `String` | Paramètre `utm_source` capté par le formulaire.<br>Champ ou source candidate du périmètre — repères : [C05](correspondance_champs_clickhouse.md#c05), [C10](correspondance_champs_clickhouse.md#c10). |
| `properties_utm_campaign` | `String` | Paramètre `utm_campaign` capté par le formulaire.<br>Champ ou source candidate du périmètre — repères : [C05](correspondance_champs_clickhouse.md#c05). |
| `properties_first_conversion_event_name` | `String` | Nom du premier formulaire rempli.<br>Champ ou source candidate du périmètre — repères : [C06](correspondance_champs_clickhouse.md#c06), [X02](correspondance_champs_clickhouse.md#x02). |
| `properties_first_conversion_date` | `Nullable(DateTime64(3))` | Date du premier formulaire rempli.<br>Champ ou source candidate du périmètre — repères : [C06](correspondance_champs_clickhouse.md#c06), [X02](correspondance_champs_clickhouse.md#x02). |
| `properties_boondid` | `String` | Identifiant du contact dans Boond.<br>Champ ou source candidate du périmètre — repères : [I05](correspondance_champs_clickhouse.md#i05), [T07](correspondance_champs_clickhouse.md#t07) ; autres usages dans la décomposition. |
| `properties_statut_boond` | `String` | Code d'état du contact dans Boond.<br>Champ ou source candidate du périmètre — repères : [C07](correspondance_champs_clickhouse.md#c07). |
| `properties_creation_boond` | `Nullable(DateTime64(3))` | Date de création du contact dans Boond.<br>Champ ou source candidate du périmètre — repères : [C08](correspondance_champs_clickhouse.md#c08), [X03](correspondance_champs_clickhouse.md#x03). |
| `properties_hubspot_owner_id` | `String` | Propriétaire HubSpot du contact.<br>Champ ou source candidate du périmètre — repères : [R09](correspondance_champs_clickhouse.md#r09). |
| `archived` | `Bool` | Identité, version, suppression/archivage ou repérage de la source.<br>Champ ou source candidate du périmètre — repères : [T02](correspondance_champs_clickhouse.md#t02) ; autres usages dans la décomposition. |
| `updatedAt` | `DateTime64(3)` | Identité, version, suppression/archivage ou repérage de la source.<br>Champ ou source candidate du périmètre — repères : [T04](correspondance_champs_clickhouse.md#t04), [T08](correspondance_champs_clickhouse.md#t08) ; autres usages dans la décomposition. |

<a id="hubspot-deals"></a>
### hubspot.deals

Représentation HubSpot du dossier, montants et statuts candidats.

| Colonne physique | Type documenté | Utilité / dépendances / extractions JSON |
| --- | --- | --- |
| `id` | `String` | Identité, version, suppression/archivage ou repérage de la source.<br>Champ ou source candidate du périmètre — repères : [I03](correspondance_champs_clickhouse.md#i03) ; autres usages dans la décomposition. |
| `properties_dealname` | `String` | Nom du deal.<br>Champ ou source candidate du périmètre — repères : [P01](correspondance_champs_clickhouse.md#p01). |
| `properties_pipeline` | `String` | Pipeline HubSpot du deal.<br>Champ ou source candidate du périmètre — repères : [P04](correspondance_champs_clickhouse.md#p04). |
| `properties_dealstage` | `String` | Étape du deal dans son pipeline HubSpot.<br>Champ ou source candidate du périmètre — repères : [P04](correspondance_champs_clickhouse.md#p04). |
| `properties_hs_is_closed` | `Bool` | HubSpot considère le deal comme fermé.<br>Champ ou source candidate du périmètre — repères : [P06](correspondance_champs_clickhouse.md#p06). |
| `properties_amount` | `Nullable(Float64)` | Montant du deal.<br>Champ ou source candidate du périmètre — repères : [P08](correspondance_champs_clickhouse.md#p08), [A12](correspondance_champs_clickhouse.md#a12), [A16](correspondance_champs_clickhouse.md#a16). |
| `properties_createdate` | `Nullable(DateTime64(3))` | Date de création du deal dans HubSpot.<br>Champ ou source candidate du périmètre — repères : [P03](correspondance_champs_clickhouse.md#p03). |
| `properties_closedate` | `Nullable(DateTime64(3))` | Date de fermeture du deal dans HubSpot.<br>Champ ou source candidate du périmètre — repères : [P12](correspondance_champs_clickhouse.md#p12). |
| `properties_boond_id_num` | `Nullable(Float64)` | Identifiant du besoin dans Boond.<br>Champ ou source candidate du périmètre — repères : [I02](correspondance_champs_clickhouse.md#i02), [T07](correspondance_champs_clickhouse.md#t07), [X08](correspondance_champs_clickhouse.md#x08) ; autres usages dans la décomposition. |
| `properties_statut_boond` | `String` | Code d'étape du besoin dans Boond.<br>Champ ou source candidate du périmètre — repères : [P04](correspondance_champs_clickhouse.md#p04), [X08](correspondance_champs_clickhouse.md#x08). |
| `properties_provenance_boond` | `String` | Code d'origine du besoin dans Boond.<br>Champ ou source candidate du périmètre — repères : [C01](correspondance_champs_clickhouse.md#c01). |
| `properties_creation_dans_boond` | `Nullable(DateTime64(3))` | Date de création du besoin dans Boond.<br>Champ ou source candidate du périmètre — repères : [P03](correspondance_champs_clickhouse.md#p03) ; autres usages dans la décomposition. |
| `properties_date_de_fermeture_boond` | `Nullable(DateTime64(3))` | Date de closing du besoin dans Boond.<br>Champ ou source candidate du périmètre — repères : [P12](correspondance_champs_clickhouse.md#p12) ; autres usages dans la décomposition. |
| `properties_hubspot_owner_id` | `String` | Propriétaire HubSpot du deal.<br>Champ ou source candidate du périmètre — repères : [R09](correspondance_champs_clickhouse.md#r09). |
| `archived` | `Bool` | Identité, version, suppression/archivage ou repérage de la source.<br>Champ ou source candidate du périmètre — repères : [T02](correspondance_champs_clickhouse.md#t02) ; autres usages dans la décomposition. |
| `updatedAt` | `DateTime64(3)` | Identité, version, suppression/archivage ou repérage de la source.<br>Champ ou source candidate du périmètre — repères : [T04](correspondance_champs_clickhouse.md#t04), [T08](correspondance_champs_clickhouse.md#t08), [X08](correspondance_champs_clickhouse.md#x08) ; autres usages dans la décomposition. |

<a id="ref-sales_targets"></a>
### ref.sales_targets

Objectifs mensuels équipe × indicateur ; nécessaires malgré le périmètre raw/hubspot initial.

| Colonne physique | Type documenté | Utilité / dépendances / extractions JSON |
| --- | --- | --- |
| `month` | `Date` | Premier jour du mois visé.<br>Champ ou source candidate du périmètre — repères : [K01](correspondance_champs_clickhouse.md#k01) ; autres usages dans la décomposition. |
| `segment` | `String` | Équipe : SMB, LA (Large Accounts) ou ES (Espagne).<br>Champ ou source candidate du périmètre — repères : [R13](correspondance_champs_clickhouse.md#r13), [K02](correspondance_champs_clickhouse.md#k02) ; autres usages dans la décomposition. |
| `indicator` | `String` | Indicateur visé : `mrr_signed`, `pipeline_generated`, `pipeline_weighted`, `demos`.<br>Champ ou source candidate du périmètre — repères : [K03](correspondance_champs_clickhouse.md#k03) ; autres usages dans la décomposition. |
| `target` | `Float64` | Valeur cible du mois (euros pour les montants, nombre pour les démos).<br>Champ ou source candidate du périmètre — repères : [K03](correspondance_champs_clickhouse.md#k03), [K11](correspondance_champs_clickhouse.md#k11). |

<a id="ref-stage_probabilities"></a>
### ref.stage_probabilities

Probabilités de signature par étape × segment ; pas d’historique de validité documenté.

| Colonne physique | Type documenté | Utilité / dépendances / extractions JSON |
| --- | --- | --- |
| `state_id` | `Int64` | Code de l'étape du besoin.<br>Champ ou source candidate du périmètre — repères : [P10](correspondance_champs_clickhouse.md#p10) ; autres usages dans la décomposition. |
| `segment` | `String` | Équipe : SMB, LA ou ES.<br>Champ ou source candidate du périmètre — repères : [P10](correspondance_champs_clickhouse.md#p10), [R13](correspondance_champs_clickhouse.md#r13) ; autres usages dans la décomposition. |
| `probability` | `Float64` | Probabilité de signature, entre 0 et 1.<br>Champ ou source candidate du périmètre — repères : [T09](correspondance_champs_clickhouse.md#t09), [P10](correspondance_champs_clickhouse.md#p10), [P11](correspondance_champs_clickhouse.md#p11), [K13](correspondance_champs_clickhouse.md#k13). |

## Ce qui reste une règle ou une preuve à préciser

Une donnée absente de la source peut être un résultat à construire ou un vrai manque métier. Les capacités techniques ci-dessus sont désormais retenues ; elles ne règlent pas seules les conventions ou preuves ci-dessous.

| Élément | Conséquence pour les calculs | Références |
| --- | --- | --- |
| Date d’observation, fuseau, calendrier, horizons | Calendrier et repères à construire librement ; conventions temporelles à documenter, pas de table source à attendre | [T05](correspondance_champs_clickhouse.md#t05), QC-03/QC-10 |
| Entrée qualifiée, issues, seuil de stagnation, pauses/retours | États et dates disponibles ; leurs conventions métier restent à fixer | P06/P07/E08, QM-01/QM-06/QC-03 |
| Preuve de séance tenue, chaînage démo et lien action→opportunité | L’agenda et le contact ne suffisent pas à garantir le fait métier | I09/D06–D09, QC-02 |
| États/bornes d’activité, continuité de lignes, événements d’activation/arrêt | Nécessaires aux MRR, New MRR et churn ; suppression CDC différente d’une résiliation | I13/A10/A13/F, QM-04/QC-12 |
| Nature mensuelle signée, montant incrémental upsell, devise/remises | Aucun champ dédié ne règle ces notions ; rapprochements et preuves à obtenir | A12/A15/A16/P14, QM-04/QC-11 |
| Canal retenu, codes Inbound, mapping équipes, référence individu/équipe | Règles d’attribution/calcul, sans équivalent direct unique | C09/C10/R/K15, QM-02/QC-05/QC-14 |
| Historique des probabilités ref | Versions importées à conserver par nos traitements ; dates d’effet métier et passé non capturé restent à qualifier | T09, QM-05 |
| Date et état du chargement des sources | Métadonnées à produire à l’import ; ne plus les traiter comme un champ à obtenir des CRM. Fréquence et suivi du chargement à choisir | T08, QC-06 |
| Événements formulaire/transmission amont | Champs non documentés ; concernent des propositions encore ouvertes | X02–X04, QC-08 |

Les valeurs manquantes et les règles ne sont pas toutes équivalentes : certaines attendent une décision de l’utilisateur, d’autres une donnée ou une preuve absente du modèle. Les détails sont conservés dans la quatrième colonne de la [table métier](correspondance_champs_clickhouse.md) et dans le [registre](questions_decisions.md).
