# Catalogue détaillé — référence IA

**Règle actuelle — échange 24 : New MRR inclut les upsells.** `New MRR total = composante New + composante Upsell`. Filtre demandé : **New / Upsell**. New conserve les entrants et retours après churn déjà retenus ; Upsell correspond à la hausse nette active des sociétés restées actives. L’expansion est donc une composante du total New MRR, pas un montant à ajouter une deuxième fois. `MRR fin = MRR début + New MRR total − churn MRR`, à périmètre et unité identiques, corrections explicites. [Décision DU-38](questions_decisions.md#du-38).

**Nomenclature résolue à l’échange 24 :** l’utilisateur inclut explicitement les upsells dans New MRR, avec filtre New / Upsell. Le supplément de 50 € reste la valeur retenue pour l’upsell 100 → 150 €/mois. MRR signé et effet actif restent distincts ; la hausse active figure une seule fois dans New MRR total. [DU-38](questions_decisions.md#du-38).

**Échange 23 :** « Nb In demo » compte les **sociétés distinctes** ayant au moins une opportunité en phase Démo à la date observée : deux dossiers de la même société = un prospect. Pour l’upsell de 100 à 150 €/mois, seule la contribution **supplémentaire de 50 €/mois** est retenue pour le case. Dans sa réponse au montant signé, l’utilisateur écrit « 50 euros en new mrr » : le montant incrémental est décidé ; l’échange 24 inclut ensuite les upsells dans New MRR avec filtre New / Upsell. [Décisions et clarification](questions_decisions.md#du-36).

**Mise à jour métier — échange 22 :** entrée à la création Boond après soumission du formulaire ; démos réellement réalisées distinctes de « Nb In demo » ; signature dès « Signé — formalités à finaliser » ; client actif = société avec au moins un abonnement en cours à clôture. Pour le case : réactivations incluses dans New MRR, variation nette par société entre clôtures, départ-retour intra-mois hors périmètre, bloc MRR actif/churn global sans filtre équipe. [Décisions de l’échange 22](questions_decisions.md#du-28). Le supplément signé d’upsell et le grain société de Nb In demo sont précisés à l’échange 23 ; données sources des montants et critères d’activité restent à préciser ; nomenclature New MRR résolue à l’échange 24.

**Formules communes :** [R03 — MRR par société et clôture](intent_ia.md#mrr-client-cloture). U04-S/U04-P sont des sous-repères de U04, pas des demandes source nouvelles.

**Échange 19 — historisation de toute la chaîne :** l’exigence couvre staging, intermédiaires, faits, dimensions et liaisons. Distinguer l’unité métier de ses versions et sélectionner les versions pertinentes avant agrégation. Les modalités de révision/restitution et la rétention détaillée restent à spécifier. [Règle commune et deux vues détaillées](architecture_modele_proposition.md#historisation-toutes-couches), [DCI-17](questions_decisions.md#dci-17).

**Échange 18 — organisation modulaire proposée :** intégrer la Démo dans les tables génériques du pipeline et garder son micro-funnel en extension locale. Deux modules — Pipeline/parcours et Revenus/performance — réutilisent les identités et dimensions communes. Les objectifs consomment les réalisés commerciaux publiés ; les abonnements alimentent directement MRR/churn. [Proposition et visuel](architecture_modele_proposition.md#architecture-modulaire), [DCI-16](questions_decisions.md#dci-16). Les définitions métier ouvertes restent ouvertes.

**Précision de l’échange 16 :** l’utilisateur suggère « Administration des ventes » pour ADV et conteste son classement comme KPI. Le sigle n’est plus présenté comme une mesure. La maquette source, zone 7, emploie « ADV / MRR potentiel du pipeline » et décrit un MRR potentiel moyen par deal : cette attente distincte reste tracée, sans formule validée. Le sens exact du sigle dans le brief reste à confirmer.

**Échange 15 :** la [liste courte des KPI, définitions et formules](liste_kpi_humaine.md) devient la lecture humaine approuvée. La [nouvelle proposition de modèle](architecture_modele_proposition.md) décrit l’intermédiaire, les faits et les dimensions à partir du staging recensé. Les DTR restent hors de cette proposition ; les règles ouvertes ne sont pas arbitrées par le schéma. [DCI-14](questions_decisions.md#dci-14).

**Distinction KPI / analyse — échange 14 :** ce catalogue conserve aussi des axes et des usages. Une cohorte, un parcours, une évolution historique ou une comparaison individu/équipe ne constitue pas en soi un KPI distinct : on y applique les volumes, montants, taux et durées définis ci-dessous. Les déclinaisons par étape, canal ou type ne doivent pas doubler la liste des mesures.

**Version actualisée après l’échange 19.** Ce catalogue décrit le besoin complet actuellement documenté. Il reste exhaustif au-delà de la synthèse choisie comme base V1 à l’échange 9. L’inventaire des champs a remplacé la première architecture et fonde la nouvelle proposition de l’échange 15. Ce catalogue ne constitue ni une promesse de faisabilité ni une spécification de calcul prête à implémenter. Une définition ouverte reste ouverte même lorsque des données ou du SQL permettent de produire un nombre.

Pour une revue accessible, lire le [catalogue humain](catalogue_indicateurs.md) et l’[intent humain](intent.md). Ce catalogue appartient à la version IA. Lire avec [l’intent détaillé](intent_ia.md), le [registre des questions et décisions](questions_decisions.md) et le [journal de ce chat](ia_assistant_story.md). Les sources antérieures restent dans [raw_intent](../raw_intent/README.md).

## 1. Mode de lecture et références communes

Les **24 identifiants M01–M08, B01–B03, O01–O04 et U01–U09** du catalogue raw sont conservés. Ce sont des repères de couverture, pas 24 KPI indépendants et entièrement validés : certains désignent une analyse, une cible ou une lecture historique de la même mesure ; U09 reste une option. U10/U11 ajoutent les churns ; U12/U13 sont leurs quantités auxiliaires de clientèle. U08 est désormais exclu, sa trace conservée. Les **10 hypothèses H01–H10** et les **4 mesures historiques L01–L04** sont inventoriées séparément.

La présence d’un élément de la maquette signifie « demande/proposition documentée à conserver ». Les mentions originales « standard », « à valider » et « question ouverte » ne prouvent pas une validation métier. Les décisions utilisateur établissent l’orientation souhaitée ; une observation enregistrée décrit son périmètre d’observation. Les règles de preuve figurent dans [R06 — Certitude](intent_ia.md#r06-certitude).

Les fiches reprennent uniquement les précisions disponibles. Leurs finalités expriment les questions de lecture soutenues par les sources ; elles ne prescrivent pas une action commerciale automatique. **« Inconnu » n’est ni zéro, ni non applicable.** Chaque manque renvoie à une question qui précise ce qu’il empêche de définir.

| Règle commune | Application au catalogue |
| --- | --- |
| [R01 — Identités et grains](intent_ia.md#r01-identites) | Distinguer société, interlocuteur, dossier commercial, représentation HubSpot, séance et ligne d’abonnement. Plusieurs contacts ne multiplient pas les dossiers ; plusieurs opportunités d’une société ne sont pas fusionnées. |
| [R02 — Temps](intent_ia.md#r02-temps) | Distinguer stock à date, flux sur période, durée, cohorte et horizon ; distinguer granularité d’analyse, recalcul et fraîcheur. |
| [R03 — Montants](intent_ia.md#r03-montants) | Séparer valeur de pipeline, MRR actif, MRR signé, New MRR et churn ; encaissements désormais exclus et tracés ; ne pas inventer la nature récurrente d’un montant de deal. |
| [R04 — Axes](intent_ia.md#r04-axes) | Lecture stratégique équipe/global ; les axes ne sont associés qu’avec un sens et un rattachement justifiés. |
| [R05 — Histoire](intent_ia.md#r05-histoire) | Distinguer état observé, événement métier et historique incomplet ; ne pas assimiler absence de trace et absence réelle d’événement. |
| [R06 — Certitude](intent_ia.md#r06-certitude) | Identifier provenance, statut et décisions ; préserver les contradictions et propositions non validées. |

**Comparaisons et agrégations non définies.** Aucune convention par défaut n’est ajoutée pour les moyennes de ratios, les totaux de stocks dans le temps, les cibles sur période partielle, les devises, les arrondis ou les dénominateurs nuls/manquants. Leur absence doit être résolue dans la définition concernée avant de spécifier son résultat. Les jours/semaine/mois envisagés ne fixent pas automatiquement la date métier de chaque indicateur. Voir [QC-04](questions_decisions.md#qc-04), [QC-06](questions_decisions.md#qc-06), [QC-09](questions_decisions.md#qc-09) et [QC-10](questions_decisions.md#qc-10).

### Sources utilisées

| Repère | Source précise | Portée |
| --- | --- | --- |
| S-M | [Maquette Pipeline](../../docs/besoin/maquette-pipeline.png), inspectée visuellement : guide, filtres, zones 1–8 | Demandes et formes proposées ; arbitrages éditoriaux explicitement ouverts. |
| S-B | [Expression de besoin](../../docs/besoin/expression-de-besoin.md), lignes 9–16 et 20 | Historisation, ancienneté, cohortes, évolution du pondéré et dispositif d’attente. |
| S-O | [Modèle](../../docs/model/model.json), lignes 1418–1449 | Objectifs mensuels de `ref.sales_targets`, équipe × indicateur. |
| S-P | [Modèle](../../docs/model/model.json), lignes 114–123 et 1457–1487 | Pondération du besoin et probabilités proposées par le cabinet ; sens documentaire « signature ». |
| S-U | [Raw intent](../raw_intent/raw_intent.md), Q1–Q16, sections 10, 12 et 13 | Précisions et décisions utilisateur enregistrées ; la section la plus récente fait foi pour l’état de la discussion, sans effacer une contradiction factuelle. |
| S-H | [Hypothèses structurées](../raw_intent/cycle_hypotheses/hypotheses-source.json), objets `n=1` à `n=10` ; [funnel global](../raw_intent/cycle_hypotheses/01-parcours-et-frictions.html), [tunnels par étape](../raw_intent/cycle_hypotheses/02-tunnels-par-etape.html), [trace](../raw_intent/cycle_hypotheses/trace-creation.md) | Mesures et frictions candidates. Les formes visuelles ne représentent aucun volume ou taux mesuré. |
| S-L | [SQL historique](../../legacy/pipeline_actuel.sql), lignes 59–68 ; [analyse enregistrée](../raw_intent/analyse_pipeline_actuel.md) | Fonctionnement de l’existant, sans valeur de norme cible. |
| S-N | [Journal actuel](ia_assistant_story.md), échanges 5–6 ; [DU-17 à DU-25](questions_decisions.md#du-17) | Nouveaux arbitrages du case. |
| S-UP | [Analyse upsell](../raw_intent/analyse_funnel_upsell.md), §1–7 ; [preuves](../raw_intent/preuves_upsell.json), Q1–Q6 | Population observée et limites ; aucune réexécution. |
| S-Q10 | [Diagnostic Q10](../raw_intent/etat_des_lieux_Q10.md), [preuves enregistrées](../raw_intent/preuves_Q10.json), [raw section 13](../raw_intent/raw_intent.md#13-q10--diagnostic-repris-et-clôture-du-cadrage) | Diagnostic documentaire disponible ; frontière qualifiée non confirmée, [QM-06](questions_decisions.md#qm-06) ouverte. |

<a id="conventions"></a>
### Conventions communes actualisées

- **Populations :** conserver les types ; séparer nouveaux clients et upsells pour les funnels. Affectation type 4/7/autres à chaque montant et objectif en QC-01/QC-11. Pas de filtre global `typeOf=4` hérité du SQL.
- **Équipes :** convention de travail utilisateur : génération à l’entrée, signature à la signature, pipe à la date observée. Mapping et exceptions en QC-05 ; pas de transposition automatique aux actions/abonnements.
- **Canal :** un canal par opportunité fixé à l’entrée ; autres origines conservées séparément. Champ de référence et codes Inbound ouverts (QM-02/QC-05).
- **Clôture :** MRR actif à fin de mois sans prorata journalier ; signé et mouvements du mois arrêtés à cette clôture. Quatre objectifs vérifiés à fin de mois par équipe Sales.
- **Pondération :** signature finale, pas transition suivante ; source/calibration ouvertes. Le résultat garde l’unité du montant initial.
- **Churn :** nombre de départs clients distinct des pertes de MRR ; pertes MRR = départs + baisses, sans compensation par New MRR/expansion. Voir [R03](intent_ia.md#churn).

N désigne le mois étudié et N−1 le précédent. `Σ` signifie somme ; `nombre distinct` compte une identité une fois dans la population définie ; identité Boond = tenant + ID. Une formule générale n’arrête pas les conditions encore ouvertes. Aucun dénominateur nul ni événement absent ne reçoit une valeur inventée.

<a id="tables"></a>
### Tables documentées : repères pour les fiches

Ces références orientent la future spécification ; elles ne prouvent ni complétude des liens ni faisabilité et ne choisissent pas d’architecture.

| Repère | Tables et champs | Sens et précaution |
| --- | --- | --- |
| T-OPP | `raw.opportunities` : `id`, `meta.customer`, `meta.ts`, `meta.deleted`, `state`, `typeOf`, `creationDate`, `closingDate`, `turnoverEstimatedExcludingTax`, `weighting`, `turnoverWeightedExcludingTax`, `origin.typeOf`, relations responsable/société/contact | Dossiers et versions. Closing saisi ≠ preuve de signature ; montant estimé ≠ MRR par défaut. |
| T-ETAT | `raw.dictionaries` : `setting.state.opportunity`, `setting.typeOf.project`, `setting.origin` | Codes et propriétés ; ne définissent pas seuls la qualification. |
| T-ACT | `raw.actions` : identité/version, `typeOf`, `creationDate`, `startDate`, `endDate`, `relationships.dependsOn.data.id` et `.type`, responsable/société ; dictionnaire `setting.action.contact` | Actions et agenda ; lire type + ID du lien ensemble. Agenda et réalisation distincts. |
| T-MRR | `raw.deliveries` : identité/version, `state`, `startDate`, `endDate`, `averageDailyPriceExcludingTax`, `attributes` (subscriptionQuantityCharged, subscriptionPriceExcludingTax), relation projet ; `raw.projects` : relations société/opportunité, dates/versions ; `raw.companies` | Lignes d’abonnement. Le champ nommé prix journalier contient selon le modèle un montant mensuel de ligne, quantité déjà incluse. |
| T-TEAM | `raw.opportunities.relationships.mainManager.data.id`, `raw.ressources`, référentiels d’organisation ; `ref.sales_targets.segment` | Mapping responsable → SMB/LA/ES à vérifier, y compris dans le temps. Pôle société/agence ne remplacent pas cette règle. |
| T-HS | `hubspot.deals.properties_boond_id_num`, `hubspot.contacts` (premières conversions, UTM, dernière source) | Acquisition et représentations ; pas addition des deux CRM ni couverture upsell présumée. |
| T-OBJ | `ref.sales_targets.month`, `segment`, `indicator`, `target` | Cible mois × équipe × indicateur ; month désigne le mois. |
| T-PROB | `ref.stage_probabilities.state_id`, `segment`, `probability` ; alternative Boond `raw.opportunities.weighting` | Source à choisir ; ne pas multiplier deux pondérations. |

Source : [modèle fourni](../../docs/model/model.json). `id` revient à chaque version, `meta.ts` date la publication CDC et `meta.deleted` la suppression. L’histoire raw existe déjà ; sa couverture et les dates métier restent à vérifier. La version actuelle ne suffit pas à représenter tout le passé.

## 2. Demandes de la maquette — M01 à M08

<a id="m01"></a>
### M01 — Objectif versus réalisé du pipeline

| Champ | Définition consolidée et limites |
| --- | --- |
| Lecture simple, grain et calcul | Grain dossier créé dans Boond, agrégé mois × équipe. Somme des montants à création ; taux = valeur / cible O02 × 100. Événement décidé échange 22, montant encore ouvert. |
| Tables documentées | T-OPP/T-OBJ/T-TEAM ; [repères](#tables), [conventions](#conventions). |
| Statut et provenance | Proposition documentée, à arbitrer avec la VP Sales selon S-M zone 1 ; S-U section 12, ligne 647. Lecture équipe/global retenue par l’utilisateur ; lecture individuelle désormais souhaitée dans U14, hors synthèse ; cible individuelle non fournie. |
| Finalité | Voir si le pipeline généré sur la période est au niveau de l’objectif et qualifier un éventuel manque de génération. |
| Nature et unité | Trois éléments liés : montant de pipeline généré, montant cible [O02](#o02), taux d’atteinte en %. Le réalisé est un flux de valeur générée, distinct du stock ouvert M05. La base monétaire du réalisé reste à définir. |
| Population, grain, décompte | Dossiers créés dans Boond pendant la période ; identité complète tenant/dossier, pas contacts. Types éligibles, réouvertures et traitement des montants après création à préciser. Une version CDC supplémentaire n’est pas une création. |
| Date, période, histoire | Date métier de création Boond, candidate raw.opportunities.creationDate, à distinguer de meta.ts. Cible mensuelle vérifiée en fin de mois par équipe ; pas ventilation quotidienne. Preuve/date de formulaire ne constitue pas un filtre excluant les dossiers sans formulaire retrouvé. |
| Formule et comparaison | **Pipeline généré / objectif × 100**, explicitement fourni par la maquette. Numérateur monétaire à définir ; dénominateur à rapprocher d’O02 sur une période et une population compatibles. Pas de proratisation de cible demandée ; cible nulle/manquante sans pourcentage inventé. |
| Axes et restitution | Équipe/global et période justifiés. Canal/segment sont des filtres proposés transversalement ; disponibilité d’une cible au même découpage et règle de comparaison non établies. Jauge de progression proposée, sans figer la restitution. |
| Référence métier et dépendances | Maquette et objectifs ; décision utilisateur échange 22 point 1 choisit création Boond. QM-06 résolue pour la frontière ; QC-01/04/05/09 restent ouverts pour populations, montants, axes et cibles. |

<a id="m02"></a>
### M02 — Nombre d’opportunités générées par source

| Champ | Définition consolidée et limites |
| --- | --- |
| Lecture simple, grain et calcul | **Grain :** Opportunité distincte entrant sur une période. **Définition/formule :** Nombre distinct de dossiers éligibles générés, par source. |
| Tables documentées | T-OPP/T-ETAT/T-HS/T-TEAM ; [repères](#tables), [conventions](#conventions). |
| Statut et provenance | Demande maquette S-M zone 2 / S-U §12 L648. Échange 22 point 1 retient Boond et sa création comme événement de génération ; canal et types par mesure restent ouverts. |
| Finalité | Comprendre le volume de dossiers alimentant le pipeline et leur origine ; comparer les contributions des canaux et équipes. |
| Nature et unité | Flux, nombre de dossiers commerciaux générés pendant une période. Ce volume ne remplace pas le montant de M01/O02. |
| Population, grain, décompte | La maquette parle de deals créés. Grain : dossier/opportunité, pas contact ni société. Plusieurs dossiers d’une société restent distincts ; plusieurs interlocuteurs ne multiplient pas les dossiers. Types éligibles, doublons entre CRM et réentrées à définir. |
| Date, période, histoire | Date de création du dossier Boond, décision échange 22. Pas démo ni qualification comme condition d’entrée. Qualité de creationDate et couverture historique à vérifier, sans remplacer par le premier meta.ts observé. |
| Calcul et comparaison | Comptage des dossiers éligibles, regroupés par canal et segment. Pas de taux ou de dénominateur demandé dans cette fiche. Comparabilité historique de la population et de l’attribution non définie ; ne pas additionner deux représentations CRM du même dossier. |
| Axes et restitution | Canal/source, segment, équipe/global, période. Barres par canal empilées par période proposées. La vue Direction demande une agrégation en « Inbound » ; la dimension exacte et la liste des catégories à réunir restent à confirmer. |
| Référence métier et dépendances | Boond retenu par la dernière décision utilisateur ; la demande initiale de choisir Boond/HubSpot reste tracée. Origine du contact et origine du besoin non assimilées ; QM-02, QC-01/05/10 ouverts. |

<a id="m03"></a>
### M03 — Opportunités en cours par source : nombre et répartition

| Champ | Définition consolidée et limites |
| --- | --- |
| Lecture simple, grain et calcul | **Grain :** Dossier ouvert à une date. **Définition/formule :** Nombre distinct ouvert ; part source = effectif source / effectif ouvert de référence × 100, dénominateur après filtres à préciser. |
| Tables documentées | T-OPP/T-ETAT/T-HS ; [repères](#tables), [conventions](#conventions). |
| Statut et provenance | Proposition documentée S-M zone 3, à valider avec la VP Sales ; S-U section 12, ligne 649. |
| Finalité | Lire la composition du portefeuille commercial ouvert et la contribution relative des sources. |
| Nature et unité | Stock de dossiers à une date, exprimé en nombre, et parts en %. Ce n’est pas le nombre de dossiers passés par un état ouvert pendant une semaine. |
| Population, grain, décompte | Dossiers considérés ouverts à la date d’observation. États, types éligibles et traitement d’abandon/nurturing/réouverture non définis. Grain : dossier ; société et contacts restent des rattachements. |
| Date, période, histoire | Photo à date. Une lecture de ce stock à des dates passées reste à préciser dans le besoin général d’historique ; elle n’est pas spécifiée par cette seule zone. La période d’un filtre ne remplace pas la date du stock. |
| Calcul et comparaison | Comptage des dossiers ouverts par source. Les parts doivent rapporter une catégorie à une population de référence explicite ; dénominateur exact après filtres et traitement des sources multiples/non renseignées ouverts. Aucune moyenne temporelle du stock ou des parts n’est validée. |
| Axes et restitution | Canal/source, segment, filtres SMB/LA/Espagne ; équipe/global. Tableau et répartition en % proposés. Aucun objectif propre à ce nombre de dossiers n’est fourni. |
| Référence métier et dépendances | Maquette : Boond/HubSpot ; choix et rapprochement à préciser par usage. [QM-01](questions_decisions.md#qm-01), [QM-02](questions_decisions.md#qm-02), [QM-06](questions_decisions.md#qm-06), [QC-01](questions_decisions.md#qc-01), [QC-04](questions_decisions.md#qc-04), [QC-05](questions_decisions.md#qc-05), [QC-10](questions_decisions.md#qc-10). |

<a id="m04"></a>
### M04 — Pipeline pondéré versus objectif

| Champ | Définition consolidée et limites |
| --- | --- |
| Lecture simple, grain et calcul | **Grain :** Contribution d’un dossier ouvert à une date. **Définition/formule :** Σ(montant × probabilité de signature finale). Pas deux pondérations successives. |
| Tables documentées | T-OPP/T-PROB/T-OBJ ; [repères](#tables), [conventions](#conventions). |
| Statut et provenance | Proposition S-M zone 4, explicitement non figée avant examen des win rates historiques et échange avec la VP Sales ; S-U section 12, ligne 650. |
| Finalité | Lire la valeur pondérée du portefeuille et la mettre en regard de la cible pour éclairer l’appréciation du pipeline. |
| Nature et unité | Montant pondéré à une date et cible monétaire [O03](#o03). Nature mensuelle/contractuelle du montant de départ à confirmer. Le coefficient n’est ni un objectif ni un taux d’atteinte. |
| Population, grain, décompte | Dossiers du périmètre de pipeline à définir ; contribution au grain du dossier et du stage retenu à la date. États ouverts, types, montants absents et déduplication entre représentations restent à préciser. |
| Date, période, histoire | Date d’observation et mois de comparaison à la cible ; évolution historique demandée par [B03](#b03). Équipe à la date observée selon DU-23 ; état et montant pertinents à cette date. Validité historique des coefficients et corrections ouvertes. Contrôle de cible à clôture mensuelle. |
| Formule et comparaison | **Somme, pour les deals retenus, de (montant du deal × probabilité associée à son stage)**, proposition de la maquette. L’échange 5 retient la probabilité de signature finale depuis l’étape actuelle ; le désaccord de sens est clos. Choix entre coefficients cabinet et pondération saisie sur le besoin, calibration et convention historique non arbitrés. Le mode exact d’écart/taux versus cible n’est pas fourni. |
| Axes et restitution | Stage, équipe/segment et global ; date/période. Les filtres canal proposés par la maquette restent soumis à une attribution et à une cible comparables. Montant et jauge proposés ; série historique B03. |
| Référence métier et dépendances | Boond + référentiels selon la maquette ; S-P décrit les deux sources de pondération possibles sans en valider une. [QM-05](questions_decisions.md#qm-05), [QM-06](questions_decisions.md#qm-06), [QC-01](questions_decisions.md#qc-01), [QC-04](questions_decisions.md#qc-04), [QC-05](questions_decisions.md#qc-05), [QC-09](questions_decisions.md#qc-09), [QC-10](questions_decisions.md#qc-10). |

<a id="m05"></a>
### M05 — Pipeline total non pondéré

| Champ | Définition consolidée et limites |
| --- | --- |
| Lecture simple, grain et calcul | **Grain :** Contribution d’un dossier ouvert à une date. **Définition/formule :** Σ(montants des dossiers ouverts éligibles). |
| Tables documentées | T-OPP/T-ETAT ; [repères](#tables), [conventions](#conventions). |
| Statut et provenance | Proposition S-M zone 5, étiquetée « standard » dans la maquette ; S-U section 12, ligne 651. Ce libellé éditorial ne règle pas ses définitions manquantes. |
| Finalité | Apprécier la valeur du portefeuille ouvert et son évolution. |
| Nature et unité | Stock monétaire à date, non pondéré. Montant mensuel récurrent, montant contractuel ou autre base : inconnu. |
| Population, grain, décompte | Dossiers ouverts à la date retenue ; une contribution monétaire par dossier selon une règle à définir. États, types, doublons, montants manquants et changements de valeur à confirmer. |
| Date, période, histoire | Photo à date et tendance dans le temps souhaitées. Une somme des stocks de plusieurs dates ne constitue pas la définition demandée ; toute synthèse de période reste à définir. |
| Formule et comparaison | **Somme des montants des deals au statut ouvert**, selon la maquette. Aucun coefficient ; aucun objectif spécifique n’est nommé pour cette mesure. Comparaison de dates sous population, base monétaire et attribution cohérentes à préciser. |
| Axes et restitution | Équipe/global ; canal, segment et période selon filtres proposés et sens métier. Indicateur de montant et tendance proposés. |
| Référence métier et dépendances | Boond/HubSpot cités par la maquette ; aucun montant de deal n’est appelé MRR par défaut. [QM-01](questions_decisions.md#qm-01), [QM-06](questions_decisions.md#qm-06), [QC-01](questions_decisions.md#qc-01), [QC-04](questions_decisions.md#qc-04), [QC-05](questions_decisions.md#qc-05), [QC-10](questions_decisions.md#qc-10). |

<a id="m06"></a>
### M06 — Pipeline coverage / couverture de l’objectif

| Champ | Définition consolidée et limites |
| --- | --- |
| Lecture simple, grain et calcul | **Grain :** Dossier ouvert, date observée et mois de closing prévu. **Définition/formule :** Σ(montants ouverts dont closing prévu ce mois) / objectif mensuel à identifier. |
| Tables documentées | T-OPP.closingDate, T-OBJ ; [repères](#tables), [conventions](#conventions). |
| Statut et provenance | Proposition S-M zone 6, étiquetée « standard » ; S-U section 12, ligne 652. Dénominateur non défini assez précisément pour choisir une cible. |
| Finalité | Mettre en regard la valeur du pipeline attendu en clôture dans le mois et l’objectif correspondant. |
| Nature et unité | Ratio de couverture ; numérateur et dénominateur monétaires. Présentation en multiple ou pourcentage non précisée. |
| Population, grain, décompte | Dossiers ouverts à la date d’observation dont la clôture est prévue dans le mois retenu. Grain du numérateur : dossier. États ouverts, types, date prévue absente ou modifiée et montants éligibles non définis. |
| Date, période, histoire | Deux repères nécessaires : date d’observation du stock et mois de clôture prévue. Ne pas remplacer cette dernière par une signature effective. Tendance souhaitée ; convention de prévision historique à définir. |
| Formule et comparaison | **Somme des montants des deals ouverts closing ce mois / objectif du mois**, selon la maquette. Aucun coefficient n’est indiqué dans cette formule. L’objectif n’est pas identifié : ne pas choisir automatiquement O01, O02 ou O03. La compatibilité du montant de pipeline avec la cible, les dénominateurs nuls et l’agrégation des ratios restent ouverts. |
| Axes et restitution | Équipe/global, mois et date d’observation. Canal/segment proposés transversalement ; cible au même découpage non prouvée. Indicateur de ratio et tendance proposés. |
| Référence métier et dépendances | Boond/HubSpot + référentiels dans la maquette. [QM-01](questions_decisions.md#qm-01), [QC-01](questions_decisions.md#qc-01), [QC-04](questions_decisions.md#qc-04), [QC-05](questions_decisions.md#qc-05), [QC-09](questions_decisions.md#qc-09), [QC-10](questions_decisions.md#qc-10). |

<a id="m07"></a>
### M07 — MRR potentiel moyen du pipeline — proposition source

| Champ | Définition consolidée et limites |
| --- | --- |
| Lecture simple, grain et calcul | **Grain :** Dossier du portefeuille de référence. **Définition/formule :** MRR potentiel moyen annoncé par dossier ; formule ouverte : récurrence, pondération, population et dénominateur manquent (QC-04). |
| Tables documentées | T-OPP/T-PROB candidats, pas source MRR validée ; [repères](#tables), [conventions](#conventions). |
| Statut et provenance | Proposition S-M zone 7 : nouveau KPI, dépendant des probabilités, non figé avant la session de challenge ; S-U section 12, ligne 653. |
| Finalité | Examiner la valeur mensuelle potentielle moyenne annoncée par dossier et ses différences entre canaux/segments. Le libellé source « ADV » est conservé comme ambiguïté terminologique, pas comme mesure distincte (échange 16). |
| Nature et unité | La maquette annonce un **MRR potentiel moyen par deal**. Nature monétaire moyenne souhaitée ; signification d’ADV et caractère récurrent mensuel des montants non confirmés. Aucun rapprochement automatique avec ARPU ou U05. |
| Population, grain, décompte | Grain annoncé : deal/dossier. Population du pipeline, dossiers inclus au dénominateur, montants absents et répétitions inconnus. |
| Date, période, histoire | Date ou période de calcul à formaliser ; tendance proposée. Convention historique du portefeuille et des probabilités non définie. |
| Formule et comparaison | Formule complète inconnue. La source cite montant, stage et probabilité, sans préciser comment calculer la moyenne ni où intervient la pondération. Numérateur, dénominateur, règles de comparaison et d’agrégation ouverts. Aucun objectif spécifique fourni. |
| Axes et restitution | Global, canal et segment explicitement demandés ; équipe/global pour le grain de lecture. Montant et tendance proposés ; application éventuelle à U14 à définir, sans propagation automatique à chaque mesure. |
| Référence métier et dépendances | Boond + référentiels dans la maquette ; aucune source de MRR potentiel validée. [QM-05](questions_decisions.md#qm-05), [QC-01](questions_decisions.md#qc-01), [QC-04](questions_decisions.md#qc-04), [QC-05](questions_decisions.md#qc-05), [QC-10](questions_decisions.md#qc-10). |

<a id="m08"></a>
### M08 — Deals stagnants : nombre et montant

| Champ | Définition consolidée et limites |
| --- | --- |
| Lecture simple, grain et calcul | **Grain :** Dossier/passage d’état courant. **Définition/formule :** Nombre distinct et Σ(montants) des dossiers d’ancienneté > X ; seuil/unité/population ouverts. |
| Tables documentées | T-OPP/T-ETAT, versions ; [repères](#tables), [conventions](#conventions). |
| Statut et provenance | Proposition S-M zone 8 ; S-U section 12, ligne 654. Besoin de durées et lecture stratégique confirmés par l’utilisateur. |
| Finalité | Repérer où des dossiers et leur valeur restent bloqués pour orienter la discussion sur le fonctionnement du pipeline. |
| Nature et unité | Stock de dossiers stagnants à date : nombre et montant, avec ancienneté en durée. Le seuil X est un paramètre à valider, pas un objectif commercial. |
| Population, grain, décompte | Dossiers sans changement de stage depuis X jours. Grain : dossier à la date d’observation ; population ouverte/qualifiée, types et traitement du nurturing/pauses/retours à préciser. Compter plusieurs fois un dossier à cause de contacts ou séances ne répond pas à cette demande. |
| Date, période, histoire | Date d’observation et entrée/dernier changement du stage ; dépend de [B01](#b01). Seuil commun ou par étape, jours calendaires/ouvrés et traitement d’un historique commençant en cours de stage ouverts. |
| Calcul et comparaison | Compter les dossiers répondant à la règle de stagnation et sommer leurs montants compatibles. **« > 30 jours » est un exemple interrogatif**, pas une règle retenue. Comparaisons entre étapes/équipes et statistiques de répartition à préciser ; aucun taux de stagnation additionnel n’est inventé. |
| Axes et restitution | Stage, équipe/segment, ancienneté, global. La maquette propose une liste, une alerte visuelle et une vue par stage/segment ; le besoin stratégique conserve volumes, montants et répartitions. L’utilité d’un détail de dossier reste ouverte ; aucun pilotage individuel implicite. |
| Référence métier et dépendances | Boond + historique des stages selon S-M ; observations techniques ne suffisent pas à certifier une date métier. [QM-01](questions_decisions.md#qm-01), [QC-01](questions_decisions.md#qc-01), [QC-03](questions_decisions.md#qc-03), [QC-04](questions_decisions.md#qc-04), [QC-08](questions_decisions.md#qc-08), [QC-10](questions_decisions.md#qc-10). |

## 3. Analyses historiques — B01 à B03

<a id="b01"></a>
### B01 — Ancienneté dans le stage actuel

| Champ | Définition consolidée et limites |
| --- | --- |
| Lecture simple, grain et calcul | **Grain :** Passage courant d’une opportunité. **Définition/formule :** Observation − entrée dans l’étape actuelle ; dates métier et retours à préciser. |
| Tables documentées | T-OPP/T-ETAT, versions ; [repères](#tables), [conventions](#conventions). |
| Statut et provenance | Demande explicite S-B ligne 9 ; S-M zone 8 ; S-U section 12, ligne 660, et Q9. |
| Finalité | Comprendre depuis combien de temps les dossiers se trouvent dans leur étape actuelle ; fournir la durée utilisée pour repérer la stagnation M08. |
| Nature et unité | Durée courante à une date, par dossier et étape actuelle. Unité de temps et calendrier à confirmer. Ce n’est ni la durée d’un passage terminé, ni le cumul de plusieurs passages U03. |
| Population, grain, décompte | Dossiers observés à date ; population de types et d’états à préciser. Grain : séjour courant d’un dossier dans une étape. Retour dans une étape, pause et ouverture de l’historique en cours de séjour non réglés. |
| Date, période, histoire | Début du séjour courant jusqu’à la date d’observation, sans formule technique imposée. Date métier de début ou proxy d’observation à distinguer ; calcul pour une date passée souhaité par le besoin d’historisation. |
| Calcul et agrégation | Principe de durée depuis l’entrée pertinente ; événements, bornes, fuseau, calendrier et traitement des inconnus ouverts. Moyenne, médiane, quantiles et classes ne sont pas sélectionnés. |
| Axes, cible et restitution | Stage, équipe/segment et global ; ancienneté. Aucun objectif de durée validé ; X de M08 à définir. Le détail de dossier peut servir à expliquer l’agrégat, mais son inclusion dans le cockpit n’est pas décidée. |
| Référence métier et dépendances | Historisation des changements demandée, sans supposer une complétude des versions disponibles. [QM-01](questions_decisions.md#qm-01), [QC-01](questions_decisions.md#qc-01), [QC-03](questions_decisions.md#qc-03), [QC-06](questions_decisions.md#qc-06), [QC-08](questions_decisions.md#qc-08), [QC-10](questions_decisions.md#qc-10). |

<a id="b02"></a>
### B02 — Cohortes de pipeline : ouvert, gagné et perdu

| Champ | Définition consolidée et limites |
| --- | --- |
| Lecture simple, grain et calcul | **Grain :** Dossier de cohorte mensuelle observé à un horizon. **Définition/formule :** Nombre par issue à J+30/60/90 ; part = effectif issue / cohorte retenue × 100 ; J, maturité et catégories à définir. |
| Tables documentées | T-OPP.creationDate/state, versions ; [repères](#tables), [conventions](#conventions). |
| Statut et provenance | Demande explicite S-B lignes 10 et 15 ; S-U section 12, ligne 661. |
| Finalité | Comprendre ce que deviennent les dossiers issus d’une même période de création et comparer leur progression à âge comparable. |
| Nature et unité | Analyse de cohorte : effectifs et proportions ouverts/gagnés/perdus à plusieurs horizons. Nombre de dossiers et %. |
| Population, grain, décompte | Opportunités groupées par **mois de création** ; grain observé : dossier dans sa cohorte. Événement de création Boond retenu échange 22 ; vérifier la date métier et sa couverture, sans substituer automatiquement meta.ts. Types éligibles, sorties, suppressions, abandon, nurturing et réouvertures non arbitrés. |
| Date, période, histoire | Horizons demandés **J+30, J+60 et J+90**. La source ne précise pas assez l’ancrage exact de J dans une cohorte mensuelle ; ne pas choisir silencieusement entre âge de chaque dossier et horizon du groupe mensuel. Une cohorte trop récente n’est pas automatiquement observée à tous les horizons. |
| Formule et comparaison | Effectifs par état/issue à l’horizon et pourcentages sur un dénominateur de cohorte à expliciter. Règles sur dossiers sans observation, historique tronqué, événements multiples et issue après réouverture ouvertes. Ne pas prétendre que trois catégories couvrent nécessairement tous les cas avant classification métier. |
| Axes et restitution | Mois de cohorte, horizon/âge, issue ; équipe/segment et canal à articuler avec les filtres et leur attribution temporelle. Vue cohortes souhaitée, forme finale non fixée. Aucun objectif de conversion de cohorte fourni. |
| Référence métier et dépendances | Expression de besoin ; diagnostic Q10 documente les limites, sans choisir la cohorte cible. [QM-01](questions_decisions.md#qm-01), [QM-02](questions_decisions.md#qm-02), [QM-06](questions_decisions.md#qm-06), [QC-01](questions_decisions.md#qc-01), [QC-05](questions_decisions.md#qc-05), [QC-06](questions_decisions.md#qc-06), [QC-10](questions_decisions.md#qc-10). |

<a id="b03"></a>
### B03 — Évolution historique du pipeline pondéré / « pipe projeté »

| Champ | Définition consolidée et limites |
| --- | --- |
| Lecture simple, grain et calcul | **Grain :** Dossier × date, agrégé en série. **Définition/formule :** M04 à chaque date pertinente ; stocks non additionnés entre dates. |
| Tables documentées | T-OPP/T-PROB, versions ; [repères](#tables), [conventions](#conventions). |
| Statut et provenance | Demande explicite S-B lignes 11 et 16 ; S-U section 12, ligne 662. |
| Finalité | Suivre l’évolution de la valeur pondérée au fur et à mesure que les dossiers changent de stage, au-delà d’une photographie actuelle. |
| Nature et unité | Série temporelle de montants pondérés. Le terme source « pipe projeté » désigne ici l’évolution du pipeline pondéré ; il ne définit pas à lui seul un modèle de prévision future distinct. |
| Population, grain, décompte | Réutilise la définition de [M04](#m04) à chaque date. Pas de second pipeline calculé sur une autre population sans justification. |
| Date, période, histoire | Historique réel demandé et recalcul automatique souhaité. Pas cible validée de fréquence : le snapshot quotidien manuel de S-B ligne 20 est provisoire. Versions historiques des montants, équipes, stages et coefficients à arbitrer. |
| Calcul et comparaison | Mesure M04 reproduite selon des conventions historiques explicites ; ni somme automatique de stocks sur une période ni remplacement du passé par le seul état actuel. Les comparaisons avant/après changement de coefficient restent à définir. |
| Axes, cible et restitution | Date/période, stage, équipe/segment et global. Cible O03 uniquement si la comparaison historique est définie de façon compatible. Tendance/vue « pipe projeté » demandée. |
| Référence métier et dépendances | Même base métier que M04 ; capacité d’historisation demandée. [QM-05](questions_decisions.md#qm-05), [QC-04](questions_decisions.md#qc-04), [QC-05](questions_decisions.md#qc-05), [QC-06](questions_decisions.md#qc-06), [QC-09](questions_decisions.md#qc-09), [QC-10](questions_decisions.md#qc-10). |

## 4. Objectifs mensuels — O01 à O04

Les quatre objectifs sont documentés dans S-O : **une cible par mois × équipe × indicateur**, équipes SMB, LA et ES. Ce sont des objectifs de pilotage, distincts de la valeur réalisée et des probabilités. Aucun objectif individuel n’est créé. Contrôle fixé à fin de mois par équipe Sales (échange 5), sans proratisation jour/semaine. Le réalisé compatible reste à définir ; [QC-09](questions_decisions.md#qc-09) ne réouvre pas la cadence. Les montants d’exemple du modèle ne sont pas reproduits comme engagement actuel.

<a id="o01"></a>
### O01 — Objectif de MRR signé (`mrr_signed`)

| Champ | Définition consolidée et limites |
| --- | --- |
| Lecture simple, grain et calcul | **Grain :** Mois × équipe × indicateur. **Définition/formule :** Cible mrr_signed comparée au réalisé U06 à clôture. |
| Tables documentées | T-OBJ ; [repères](#tables), [conventions](#conventions). |
| Statut et source | Cible documentée S-O, issue du tableur VP Sales ; S-U section 12, ligne 670. |
| Finalité et nature | Comparer le MRR signé réalisé à l’ambition mensuelle de l’équipe. Nature : objectif ; unité : euros pour le montant cible. |
| Population et grain | Équipe × mois pour `mrr_signed`. Population de signatures et convention de montant doivent être compatibles avec [U06](#u06), encore à définir. Aucun décompte de personnes n’est associé. |
| Temps et axes | Mois visé (`month`, premier jour du mois) ; équipe SMB/LA/ES, global souhaité. Pas de cible par canal ou société documentée. |
| Calcul et comparaison | La valeur cible est fournie ; sa méthode de construction n’est pas décrite. Réalisé U06 distinct. Comparaison réalisé/cible à fin de mois par équipe ; aucun coefficient de probabilité appliqué à la cible. |
| Inconnues bloquantes | Définition du MRR signé, événement/date, normalisation mensuelle, périmètre, comparabilité et historique des objectifs : [QM-04](questions_decisions.md#qm-04), [QC-01](questions_decisions.md#qc-01), [QC-09](questions_decisions.md#qc-09). |

<a id="o02"></a>
### O02 — Objectif de pipeline généré (`pipeline_generated`)

| Champ | Définition consolidée et limites |
| --- | --- |
| Lecture simple, grain et calcul | **Grain :** Mois × équipe × indicateur. **Définition/formule :** Cible pipeline_generated comparée au montant M01, pas volume M02. |
| Tables documentées | T-OBJ ; [repères](#tables), [conventions](#conventions). |
| Statut et source | Cible documentée S-O ; S-U section 12, ligne 671. |
| Finalité et nature | Apprécier la génération de valeur de pipeline au regard de l’ambition mensuelle. Nature : objectif ; unité : euros, pas nombre de deals. |
| Population et grain | Équipe × mois pour `pipeline_generated`. Population et valeur générée doivent correspondre au réalisé de [M01](#m01) ; M02 est un volume distinct. |
| Temps et axes | Mois visé, équipe SMB/LA/ES, global souhaité. Ni objectif individuel ni ventilation par source documentés. |
| Calcul et comparaison | Cible fournie, construction non décrite. M01 porte la formule explicitement demandée réalisé/objectif × 100. Événement de génération, montant retenu et périmètre comparables à confirmer ; un stock ouvert M05 ne remplace pas ce flux. |
| Inconnues bloquantes | [QM-06](questions_decisions.md#qm-06), [QC-01](questions_decisions.md#qc-01), [QC-04](questions_decisions.md#qc-04), [QC-05](questions_decisions.md#qc-05), [QC-09](questions_decisions.md#qc-09). |

<a id="o03"></a>
### O03 — Objectif de pipeline pondéré (`pipeline_weighted`)

| Champ | Définition consolidée et limites |
| --- | --- |
| Lecture simple, grain et calcul | **Grain :** Mois × équipe × indicateur. **Définition/formule :** Cible pipeline_weighted comparée à M04 à fin de mois. |
| Tables documentées | T-OBJ ; [repères](#tables), [conventions](#conventions). |
| Statut et source | Cible documentée S-O ; S-U section 12, ligne 672. |
| Finalité et nature | Comparer une mesure de pipeline pondéré à l’ambition mensuelle de l’équipe. Nature : objectif ; unité : euros. |
| Population et grain | Équipe × mois pour `pipeline_weighted`. La population sous-jacente du réalisé relève de [M04](#m04). |
| Temps et axes | Mois cible et équipe SMB/LA/ES ; global souhaité. Réalisé observé à la fin du mois cible, selon l’arbitrage utilisateur. |
| Calcul et comparaison | Valeur cible fournie. Les probabilités de signature finale servent à construire le réalisé M04, pas à transformer la cible en probabilité. Mode exact de comparaison, convention historique et agrégation des cibles restent ouverts. |
| Inconnues bloquantes | Définition/validation des coefficients, montant/population et date comparable : [QM-05](questions_decisions.md#qm-05), [QC-04](questions_decisions.md#qc-04), [QC-09](questions_decisions.md#qc-09), [QC-10](questions_decisions.md#qc-10). |

<a id="o04"></a>
### O04 — Objectif de démos (`demos`)

| Champ | Définition consolidée et limites |
| --- | --- |
| Lecture simple, grain et calcul | Grain mois × équipe × indicateur. Cible demos comparée à U04-S, nombre de RDV de démo réellement réalisés pendant le mois, échange 22. |
| Tables documentées | T-OBJ/T-ACT/T-OPP ; [repères](#tables), [conventions](#conventions). |
| Statut et source | Cible documentée S-O ; S-U section 12, ligne 673. |
| Finalité et nature | Mettre la volumétrie de démonstration réalisée en regard d’un objectif mensuel d’équipe. Nature : objectif ; unité : nombre. |
| Population et grain | Équipe × mois pour la cible demos. Réalisé = U04-S, RDV de démo réellement tenus (échange 22), pas stock U04-P. Dédupliquer les séances et leurs versions. |
| Temps et axes | Mois cible et équipe SMB/LA/ES ; global souhaité. Date métier du réalisé, séance prévue ou tenue, et gestion des reports à préciser. |
| Calcul et comparaison | Valeur cible fournie, sans formule validée du réalisé ou du taux d’atteinte. Aucune division arbitraire de l’objectif entre commerciaux ni déduction du nombre obligatoire de séances par dossier. |
| Inconnues bloquantes | Preuve/date de réalisation, liens et attribution : QC-02/QC-05/QC-09. Le choix réalisé/plannifié est tranché : réalisé. |

## 5. Attentes précisées par l’utilisateur — U01 à U14

<a id="u01"></a>
### U01 — Conversions et déperdition par étape

| Champ | Définition consolidée et limites |
| --- | --- |
| Lecture simple, grain et calcul | **Grain :** Dossier d’une population d’entrée, intervalle d’observation. **Définition/formule :** Conversion A→B = dossiers de A ayant atteint B / dossiers éligibles entrés en A × 100. Perte définie séparément, pas automatiquement 1−conversion. |
| Tables documentées | T-OPP/T-ETAT ; T-ACT si sous-parcours validé ; [repères](#tables), [conventions](#conventions). |
| Statut et provenance | Demande utilisateur retenue Q11 ; S-U section 12, lignes 681 et 786–794. |
| Finalité | Localiser les endroits où la déperdition paraît trop importante et éclairer une discussion stratégique sur le parcours commercial. Une baisse de conversion ne prouve pas sa cause. |
| Nature et unité | Volumes entrants/sortants, progression, pertes et taux associés : nombres et ratios. Les flux/cohortes suivis doivent être définis ; une répartition de stocks par étape n’est pas un taux de conversion. |
| Population, grain, décompte | Dossiers ou autre unité explicitement pertinente pour une partie du parcours, à déterminer par mesure ; pas de compteur universel société/contact/dossier/séance. Éligibilité, passage multiple, étapes sautées, attente, abandon et réouverture ouverts. |
| Date, période, histoire | Période d’entrée/sortie ou cohorte comparable ; fenêtres de conversion et maturité non choisies. Entrée à la création Boond décidée échange 22 ; preuve des événements et populations conditionnent la lecture. |
| Formule et comparaison | Numérateurs et dénominateurs de chaque transition à préciser. Aucun taux issu des supports H n’est automatiquement validé. Référence ou seuil de « trop important » inconnu ; aucun objectif chiffré inventé. |
| Axes et restitution | Étape, période/cohorte, équipe/global, segment et canal selon attribution définie. Forme de tunnel possible dans les supports, mais pas retenue comme encodage obligatoire. |
| Référence métier et dépendances | Sources de parcours et décisions utilisateur ; analyse du workflow nécessaire. [QM-01](questions_decisions.md#qm-01), [QM-02](questions_decisions.md#qm-02), [QM-06](questions_decisions.md#qm-06), [QC-01](questions_decisions.md#qc-01), [QC-02](questions_decisions.md#qc-02), [QC-03](questions_decisions.md#qc-03), [QC-05](questions_decisions.md#qc-05), [QC-10](questions_decisions.md#qc-10). |

<a id="u02"></a>
### U02 — Cycle de vie d’un deal / besoin commercial

| Champ | Définition consolidée et limites |
| --- | --- |
| Lecture simple, grain et calcul | **Grain :** Opportunité et succession de passages. **Définition/formule :** Séquence ordonnée des états/événements sans répétitions consécutives du même état. Pas formule unique pour une analyse de parcours. |
| Tables documentées | T-OPP/T-ETAT/T-HS ; types séparés ; [repères](#tables), [conventions](#conventions). |
| Statut et provenance | Demande utilisateur Q11 ; hypothèse de rattachement Q12 conservée avec son statut ; S-U section 12, lignes 682 et 752–766. |
| Finalité | Comprendre la progression des dossiers, les étapes atteintes et les issues, puis comparer les parcours à l’échelle des équipes et cohortes. |
| Nature et unité | Analyse de parcours, avec événements/états et volumes nécessaires à sa lecture ; pas une formule scalaire unique ni un objectif chiffré. |
| Population, grain, décompte | Grain principal : dossier commercial lié à une société. Chaîne de travail : deal HubSpot → besoin Boond → société ; relations documentées mais intégrité et multiplicité non prouvées. Plusieurs contacts ne créent pas plusieurs dossiers ; plusieurs dossiers d’une société restent distincts. |
| Date, période, histoire | Suite d’événements métier ou d’observations explicitement qualifiées comme telles. Début du cycle, retours, sauts, pauses et fin du parcours ouverts. |
| Calcul et comparaison | Définir les événements et issues avant de compter les parcours ou leurs conversions. Aucun ordre linéaire obligatoire, aucun passage Show Boond universel, aucune équivalence entre état actuel et histoire complète. |
| Axes et restitution | Étape, issue, équipe/global et cohorte ; société comme rattachement. Détail de dossier explicatif éventuel à confirmer, lecture individuelle dédiée désormais demandée dans U14, périmètre par métrique à préciser. |
| Référence métier et dépendances | Cycle fourni, modèle et diagnostic Q10 ; aucune preuve d’absence d’événement déduite de l’absence de trace. [QM-01](questions_decisions.md#qm-01), [QM-06](questions_decisions.md#qm-06), [QC-01](questions_decisions.md#qc-01), [QC-02](questions_decisions.md#qc-02), [QC-08](questions_decisions.md#qc-08), [QC-10](questions_decisions.md#qc-10). |

<a id="u03"></a>
### U03 — Durées commerciales et sous-parcours de démo

| Champ | Définition consolidée et limites |
| --- | --- |
| Statut / finalité | Q9/Q11 conservés ; S-N échange 5 point 3 confirme les deux lectures de démo. Localiser les attentes, nouveaux clients et upsells séparés ; sous-parcours secondaire souhaité. |
| Grains / unité | Passage d’une opportunité dans un état ; dossier pour le cycle ; intervalle entre événements du même parcours de démo. Durée, unité/calendrier à confirmer. Durée de séance d’agenda distincte de l’attente entre étapes. |
| Définitions / formules | Passage terminé = sortie − entrée. En cours = observation − entrée (B01). Cycle = issue retenue − entrée retenue. Phase démo = sortie Show Boond − entrée Show Boond, ou ancienneté si en cours. Étape du sous-parcours démo = événement de fin − événement de début après chaînage validé. Événements et bornes encore ouverts. |
| Décompte / population | Séparer passages terminés/en cours ; retours, pauses et cumuls à définir. Plusieurs versions au même état ne créent pas plusieurs passages. Ne pas chaîner toutes les actions du contact comme un seul dossier. |
| Date / histoire | Dates métier retenues ; CDC utilisable seulement sous convention explicite de proxy. Aucune durée antérieure à la couverture inventée ; absence de Show upsell ≠ durée nulle réelle. |
| Axes / agrégation | Étape, type de vente, équipe/global, cohorte/période selon règle. Moyenne/médiane/quantile et seuils non décidés ; pas d’objectif de durée ajouté. |
| Sources / questions | T-OPP/T-ETAT, T-ACT, S-UP §2/5. [QC-02](questions_decisions.md#qc-02), [QC-03](questions_decisions.md#qc-03), [QM-01](questions_decisions.md#qm-01), [QM-06](questions_decisions.md#qm-06), [QC-10](questions_decisions.md#qc-10). |


<a id="u04"></a>
### U04 — Volumes de démo : actions et opportunités

| Champ | Définition consolidée et limites |
| --- | --- |
| Statut / finalité | Deux grains confirmés échanges 5 et 22. U04-S « Nombre de démos » = RDV réellement tenus ; U04-P « Nb In demo » = prospects dans la phase. Un flux de séances et un stock de prospects ne s’additionnent pas. |
| Grains / formules | U04-S = nombre distinct de séances réellement tenues dans la période. U04-P = nombre distinct de sociétés ayant au moins une opportunité dans la phase Démo à la date observée (échange 23). Deux opportunités d’une même société = un prospect. Chemin candidat : raw.opportunities.state=24 et relationships.company.data.id ; identité tenant+société, versions pertinentes, pas contacts. Flux d’entrées par étape conservé séparément. |
| Unité / décompte | Nombre d’actions/séances ou de dossiers ; flux/stock nommés. Plusieurs contacts ne multiplient pas une séance ; plusieurs séances ne multiplient pas les dossiers. |
| Codes / observations | Utilisateur rapporte : type 60 Démo 1 = 533 ; 68 complémentaire = 74 ; 25 demande = 700 ; 17 RDV annulé = 75. Autres types : 122 appel abouti 2646 ; 75 appel manqué 1040 ; 58 SEO 73 ; 57 SEA 41. Observations transmises, pas nouvelle extraction ni étapes obligatoires. Première ligne « Appel non abouti » mal formée : code non inventé. Show Boond = état 24 de l’opportunité. |
| Temps / exclusions | U04-S utilise la tenue effective pendant la période : prévu seul, annulé ou no-show ne comptent pas comme réalisé. Preuve/date à établir dans raw.actions, type 60/68 et attributs candidats ; code d’action et date d’agenda ne suffisent pas. Conserver les types de séances ; éviter doubles traces et reports comptés plusieurs fois. |
| Objectif / axes | O04 compare U04-S à la cible de fin de mois par équipe Sales. Attribution équipe et preuve de tenue restent à établir ; H06 n’est pas adopté comme taux obligatoire. |
| Relations / questions | T-ACT : dependsOn.type + id, contact fréquent, pas attribution à tous ses dossiers. T-OPP/T-ETAT : phase. [QC-02](questions_decisions.md#qc-02), [QC-05](questions_decisions.md#qc-05), [QC-09](questions_decisions.md#qc-09), [QC-10](questions_decisions.md#qc-10). Durées U03. |


<a id="u05"></a>
### U05 — MRR actif à fin de mois

| Champ | Définition consolidée et limites |
| --- | --- |
| Statut / finalité | Retenu ; Boond DU-06, clôture sans prorata S-N échange 5 point 4. Valeur récurrente mensuelle du portefeuille actif. |
| Nature / unité | Stock à clôture ; euros mensuels HT sous convention monétaire compatible, ni somme des jours ni encaissement. |
| Population / grain | Une contribution par ligne active à clôture ; regroupement société/projet/global sans double compte. États, bornes, remplacements et chevauchements ouverts. |
| Formule | MRR actif_N = Σ(montants mensuels des lignes actives à fin N). Sans prorata journalier. Montant mensuel de ligne ou quantité × prix mensuel selon sémantique confirmée ; ne pas remultiplier la quantité. |
| Sources / histoire | T-MRR : deliveries via projects ; version pertinente à clôture avant exclusion des suppressions. Historique existant, complétude et date d’effet à vérifier ; pas de dernier état actuel appliqué au passé. |
| Axes / agrégation | Fin de mois/global ; société/projet/ligne pour expliquer. Bloc MRR actif/churn sans filtre équipe, échange 22 point 8. Pas canal généralisé ; ne pas sommer les stocks mensuels. Pas de cible propre. |
| Questions | [QM-04](questions_decisions.md#qm-04) états/montants ; [QC-10](questions_decisions.md#qc-10) histoire ; [QC-12](questions_decisions.md#qc-12) mouvements. |


<a id="u06"></a>
### U06 — MRR signé pendant le mois

| Champ | Définition consolidée et limites |
| --- | --- |
| Statut / finalité | Retenu, réaffirmé S-N échange 5 point 4 ; mesurer l’engagement récurrent signé, comparer à O01. |
| Nature / grain | Flux d’engagements du mois arrêté à clôture ; une contribution par engagement admissible lié au dossier ; euros de MRR HT, pas valeur totale de contrat par défaut. |
| Formule | MRR signé_N = somme des montants mensuels récurrents engagés à l’entrée dans « Signé — formalités à finaliser » (state=1) pendant N. Passage ultérieur en 14 ≠ seconde signature. Montant et preuve de date à établir. |
| Population / temps | Nouvelles ventes/upsells distingués ; upsell signé au supplément mensuel vendu (150 − 100 = 50 €/mois, échange 23). L’activation effective alimente la composante Upsell de New MRR (échange 24), sans assimiler signature et activation. Cibles, preuves de montant/date, réouvertures et histoire restent à qualifier. |
| Axes / cible | Équipe à signature selon DU-23 ; mois/global/type. O01 à fin de mois ; pas objectif individuel. |
| Sources candidates | T-OPP : state, closingDate, montants/versions ; T-MRR/T-HS si sens établi. Référence du montant récurrent non tranchée : ni montant HubSpot ni estimé Boond automatiquement MRR. |
| Questions | [QM-04](questions_decisions.md#qm-04), [QC-11](questions_decisions.md#qc-11), [QC-01](questions_decisions.md#qc-01), [QC-09](questions_decisions.md#qc-09), [QC-10](questions_decisions.md#qc-10). |


<a id="u07"></a>
### U07 — New MRR du mois

| Champ | Définition consolidée et limites |
| --- | --- |
| Statut / finalité | Besoin confirmé ; nomenclature précisée échange 24 / DU-38 : New MRR total regroupe les apports New et Upsell, filtrables séparément. La clarification de l’échange 23 est close pour le case. |
| Nature / grain | Flux de MRR supplémentaire actif mesuré entre clôtures, euros mensuels ; contribution société × mois × composante New/Upsell. Détail source des lignes conservé ; pas une nouvelle vente par version CDC. |
| Définition / formule | New MRR total_N = New MRR[New]_N + New MRR[Upsell]_N. New = somme MRR fin N des sociétés entrantes (retours compris). Upsell = somme max(MRR_N − MRR_N−1,0) chez les sociétés actives aux deux clôtures. Formules communes R03 ; pas ajout séparé d’Expansion au total. |
| Population / cas multiples | New : A_N hors A_N−1, retours après churn inclus. Upsell : restants A_N ∩ A_N−1 dont MRR net augmente. Groupes disjoints pour la comparaison du case. Départ-retour intra-mois hors scope ; activité non déduite du seul montant positif. Première acquisition et retour restent distincts en connaissance métier. |
| Temps / sources | Événement d’activation à définir, distinct de signature ; T-MRR et histoire clients/projets/lignes. T-OPP seul ne prouve pas une hausse active. |
| Axes / comparaison | Mois/global ; filtre dédié type d’apport = New ou Upsell, sans filtre = total. Le filtre est une catégorie financière dérivée, pas automatiquement raw.opportunities.typeOf. Aucun objectif New MRR ajouté ; bloc portefeuille toujours global, sans filtre équipe. |
| Questions | Nomenclature résolue DU-38. Restent états/bornes d’activité, qualité des montants, couverture et corrections (QM-04/QC-10/QC-12), liens éventuels aux upsells commerciaux QC-11. Question réelle RAW-E23-01 conservée avec réponse case consignée. |


<a id="u08"></a>
### U08 — Encaissements mensuels — hors périmètre

| Champ | Définition consolidée et limites |
| --- | --- |
| Statut | Ancienne demande Q2 conservée ; exclue explicitement S-N échange 5 point 4, pour le scope. Pas une suppression due au manque de données. |
| Définition / grain | Paiements réellement reçus pendant le mois ; grain règlement/transaction, pas abonnement/opportunité. |
| Formule de sens | Somme des règlements reçus du mois ; conventions avoirs/remboursements non définies car hors scope. Aucun calcul ni nouvel objectif attendu. |
| Sources / limites | Aucune source de règlements fournie ; T-MRR ne prouve pas un paiement. Ni MRR ni chiffre d’affaires par équivalence. |
| Questions | Aucune dépendance bloquante du périmètre actuel. Réintégration soumise à nouvelle décision ; DU-05 remplacée par DU-18 pour ce besoin. |


<a id="u09"></a>
### U09 — Scénario de revenu à portefeuille supposé constant

| Champ | Définition consolidée et limites |
| --- | --- |
| Lecture simple, grain et calcul | **Grain :** Portefeuille à date, horizon fin du mois. **Définition/formule :** Scénario optionnel sans churn/New MRR ; variable et autres mouvements ouverts, aucune formule forcée. |
| Tables documentées | T-MRR candidat ; [repères](#tables), [conventions](#conventions). |
| Statut et provenance | **Option à préciser**, idée utilisateur conservée, pas KPI obligatoire validé. S-U section 10, ligne 541, et section 12, ligne 689 ; ancien libellé « MRR hypothétique signé ». |
| Finalité | Examiner ce que pourrait représenter le revenu à fin de mois à partir d’une date N sous certaines hypothèses de stabilité du portefeuille. L’utilité exacte reste à confirmer. |
| Nature et unité | Scénario, distinct du réalisé, d’un objectif et d’un paiement garanti. Variable projetée et unité exacte encore inconnues. |
| Population, grain, décompte | Portefeuille de départ à définir, probablement relié au besoin U05 mais non arrêté comme formule. Aucun grain de mouvement ou règle d’agrégation validés. |
| Date, période, horizon | Point de départ N vers fin du mois, selon l’idée utilisateur ; date de référence du portefeuille et conventions de clôture ouvertes. |
| Hypothèses et calcul | « Zéro churn et zéro New MRR » proposés par l’utilisateur. Avec la nouvelle définition, zéro churn exclurait aussi les baisses d’abonnement ; extensions, réactivations et changements de prix restent à préciser. L’option n’est pas validée pour autant. Formule, autres conditions et nom à valider ; ne pas assimiler à U05, U06 ou U08. |
| Axes et comparaison | Global envisagé par le contexte, sans ventilation supplémentaire définie. Aucun objectif ou coefficient de probabilité associé. Lecture comparée au réalisé éventuelle non décidée. |
| Dépendances | Confirmer l’intérêt, la variable projetée et les mouvements : [QM-04](questions_decisions.md#qm-04), [QC-08](questions_decisions.md#qc-08). La présence de cette fiche préserve l’idée sans en décider la livraison. |

<a id="u10"></a>
### U10 — Churn en nombre de clients

| Champ | Définition consolidée et limites |
| --- | --- |
| Statut / finalité | Retenu S-N échanges 5–6 ; convention case, définition officielle Boond inconnue. Identifier les clients partis par arrêt/non-renouvellement, distincts des baisses chez les clients restants. |
| Nature / grain / unité | Nombre de sociétés distinctes sortantes entre clôtures. Client = société avec au moins un abonnement en cours à la clôture, échange 22 point 4 ; pas nombre de lignes ou de contacts. |
| Définition / formule | Churn clients_N = nombre distinct de sociétés actives à fin N−1 et inactives à fin N. Une fermeture de ligne ne suffit pas si une autre reste active. R03 définit les ensembles et l’activité séparément du montant. |
| Réconciliation | Clients_N = Clients_N−1 + entrants entre clôtures_N − sortants entre clôtures_N, sur populations compatibles et observables. Les entrants comprennent les retours ; le KPI « nouveaux clients » au sens première acquisition reste à qualifier en U13. |
| Temps / limites | Comparaison fins N−1/N ; départ-retour dans le même mois hors scope (échange 22 point 7). Ne pas présenter cette lecture comme inventaire exhaustif des événements du mois. Historique absent ≠ zéro. |
| Axes / sources | Mois/global, T-MRR et sociétés ; filtre équipe exclu pour le bloc MRR actif/churn, échange 22 point 8. Pas cible ni taux ajouté ; cumul mensuel ≠ clients uniques sur plusieurs mois. |
| Questions | [QM-04](questions_decisions.md#qm-04), [QC-12](questions_decisions.md#qc-12), [QC-10](questions_decisions.md#qc-10). Quantités auxiliaires U12/U13. |

<a id="u11"></a>
### U11 — Churn MRR : départs et baisses d’abonnement

| Champ | Définition consolidée et limites |
| --- | --- |
| Statut / finalité | Retenu échange 5, affiné échange 6 : pertes par départ et par baisse, hors New MRR/upsells. Distinguer fuite de clients et baisse de leur abonnement. Convention case, pas définition officielle Boond. |
| Nature / unité / grain | Contribution de société × mois × composante, calculée après somme de ses lignes aux deux clôtures. Euros de MRR positifs pour une perte ; versions historiques distinctes du grain métier. |
| Formule principale | Churn MRR = départs + baisses. Départs = somme MRR fin N−1 des sociétés sorties ; baisses = somme max(MRR fin N−1 − MRR fin N,0) chez celles actives aux deux clôtures. Formules communes R03 ; net au sein d’une société, pas compensation entre sociétés. |
| Composantes | <a id="u11-d"></a>U11-D : pertes des sortants. <a id="u11-b"></a>U11-B : baisses nettes des restants. <a id="u11-c"></a>U11-C : sociétés actives aux deux clôtures avec MRR_N < MRR_N−1. Populations disjointes départ/restant pour ce case ; pas décompte des mouvements intermédiaires. |
| Réconciliation | MRR_N = MRR_N−1 + NewMRR_total_N − U11-D_N − U11-B_N à périmètre/unité identiques. NewMRR_total inclut New (retours compris) et Upsell. Ne pas ajouter Expansion une seconde fois. Corrections et écarts de périmètre restent explicites. R03 / échange 24. |
| Expansion auxiliaire | Sous-composante Upsell de U07, plus KPI indépendant à additionner au New MRR. Somme max(MRR_N − MRR_N−1,0) des restants ; +100/−40 au sein d’une société = +60 Upsell, 0 churn. Lien au dossier commercial précis non démontré par la seule variation. |
| Exemple fictif | 1 000 € initiaux + 250 € New MRR total (200 € New + 50 € Upsell) − 100 € départs − 40 € baisses = 1 110 € finaux ; churn 140 €. Ajouter encore 50 € d’Expansion au total de 250 € serait un double compte. |
| Temps / agrégation | Mois, deux clôtures sans prorata. Compensation au sein de chaque société décidée échange 22 point 6 ; détail lignes conservé. Départ-retour intra-mois hors scope. Ne pas additionner les stocks pour produire un flux. |
| Sources / axes / objectifs | T-MRR/versions, liens société via projets ; mois/global et détails explicatifs. Pas filtre équipe sur ce bloc pour le moment. Lien T-OPP seulement si prouvé ; pas objectif de churn. |
| Questions | [QC-12](questions_decisions.md#qc-12), [QC-13](questions_decisions.md#qc-13), [QC-11](questions_decisions.md#qc-11), [QM-04](questions_decisions.md#qm-04), [QC-10](questions_decisions.md#qc-10). |

<a id="u12"></a>
### U12 — Clients actifs à fin de mois — quantité auxiliaire

| Champ | Définition consolidée et limites |
| --- | --- |
| Statut / usage | Nécessaire à la comparaison N/N−1 du churn clients demandée échange 5 ; pas un nouvel objectif ajouté. |
| Définition / grain / formule | Décision utilisateur échange 22 point 4 : nombre distinct de sociétés ayant au moins un abonnement en cours à clôture. Plusieurs lignes ne multiplient pas les clients ; états/bornes de ligne encore à préciser. Activité ≠ nécessairement MRR strictement positif. |
| Temps / unité / sources | Fin de mois, nombre de clients ; T-MRR via projets/sociétés, mêmes critères d’activité que U05. Mois/global ; stocks non sommables entre mois. |
| Questions | Client actif, gratuités/pauses, identité : [QM-04](questions_decisions.md#qm-04), [QC-12](questions_decisions.md#qc-12). Activité et MRR strictement positif ne sont pas automatiquement équivalents. Pas de cible. |

<a id="u13"></a>
### U13 — Nouveaux clients actifs — quantité auxiliaire

| Champ | Définition consolidée et limites |
| --- | --- |
| Statut / usage | Entrants à isoler du churn clients, demandés échange 5 point 0. Complément en nombre des apports nouveaux ; distinct des opportunités générées M02. |
| Définition / grain / formule | Nombre distinct de clients devenant nouvellement actifs pendant N selon règle d’entrée retenue. Plusieurs lignes activées ne font pas plusieurs clients. Actifs_N privés des Actifs_N−1 mesure seulement les entrants entre deux clôtures, pas forcément les seuls nouveaux clients ni tous les événements du mois. |
| Temps / unité / sources | Flux mensuel, nombre de clients ; T-MRR et historique société/abonnements. Nouvelle signature ≠ activation. Mois/global ; pas d’objectif. |
| Questions | Le retour après churn est inclus dans New MRR monétaire, pas explicitement dans « nouveaux clients » au sens première acquisition. Conserver cette distinction ouverte. Pour la réconciliation, entrants entre clôtures = A_N hors A_N−1, retours compris. Départ-retour intra-mois hors scope ; états et couverture en QM-04/QC-10. |

<a id="u14"></a>
### U14 — Analyse individuelle comparée à l’équipe

| Champ | Définition consolidée et limites |
| --- | --- |
| Statut / provenance | Besoin explicite échanges 8–9, remplace l’exclusion générale DU-02 ; feuille dédiée hors synthèse, faisabilité non acquise. |
| Finalité | Approfondir les résultats et contributions d’une personne dans son équipe, à périmètre et période comparables. |
| Grain | Responsable × période × métrique dans la restitution ; grain dossier/passage/action conservé dans le socle, sans mélanger ces unités. |
| Définition / formule | Réutiliser les métriques choisies avec attribution temporelle correcte ; définition de la référence d’équipe encore ouverte. Total, moyenne, médiane ou distribution ne sont pas interchangeables. Aucun ratio ou classement imposé. |
| Temps / attribution | Génération à l’entrée, signature à l’événement, pipe à observation selon DU-23. Répartition d’une durée pendant un transfert à définir ; changement de responsable seul ne redémarre pas l’étape. |
| Sources candidates | T-OPP/T-ACT : mainManager ; raw.ressources ; raw.businessunits.relationships.includedManagers.data et leurs versions. Mapping équipe, membres multiples, robots et historique non vérifiés globalement. |
| Axes / objectifs | Personne, équipe de référence, période, type de vente selon pertinence. Pas de cible individuelle déduite de ref.sales_targets ; pas division arbitraire d’une cible collective. |
| Questions | [QC-14](questions_decisions.md#qc-14), [QC-05](questions_decisions.md#qc-05), [QC-10](questions_decisions.md#qc-10) et règles de chaque mesure sélectionnée. |

## 6. Mesures candidates des visualisations — H01 à H10

**Statut d’origine : hypothèse/proposition à valider.** Le sous-parcours démo (U03/U04) et le churn (U10/U11) sont depuis retenus par l’utilisateur. Cela ne valide ni tous les taux H06 ni toutes les analyses H10. Les supports représentent des sous-parcours et des frictions possibles ; aucun taux, volume, ordre obligatoire ou événement disponible n’est établi par leur dessin. S-H, objets `n=1` à `n=10`, champs `question`, `measure` et `caveat`, et S-U section 12, lignes 720–737, sont les références. Leurs associations avec U/M/B indiquent un sujet commun, pas une validation de leur formule.

Pour toutes les propositions ci-dessous : fréquence de suivi, seuils, calendrier, règles d’agrégation, populations exactement comparables et données disponibles restent à confirmer. Aucun objectif numérique n’est fourni. Les contrôles techniques ne deviennent pas des conversions commerciales ; Produit/Tech restent hors du périmètre de réalisation actuel rappelé dans le raw.

| ID | Proposition, finalité et nature | Grain, population, date et axes proposés | Formule candidate et limites | Liens avec le besoin / questions |
| --- | --- | --- | --- | --- |
| <a id="h01"></a>H01 | Formulaire : observer volumes d’affichages, clics, débuts et envois, puis abandon avant envoi. Flux de volumes et ratio candidat. | Événements du formulaire, canal/campagne/cohorte. Un envoi peut mettre à jour un contact existant. Dates, unité de session/demande et déduplication inconnues. | Envois / débuts de formulaire proposé ; suivi amont non établi disponible. Pas comptage automatique de nouveaux contacts. | Découverte amont liée à U01, sans demande validée de tous ces événements. [QM-02](questions_decisions.md#qm-02), [QC-08](questions_decisions.md#qc-08). |
| <a id="h02"></a>H02 | Transmission vers Boond : demandes reçues dans un délai, absences, retards et doublons. Contrôle de circulation de l’information. | Demande à transmettre et identifiant de liaison ; temps émission/réception, délai acceptable inconnu. | Demandes reçues dans le délai / demandes à transmettre, candidat. Les contacts uniques ne sont pas le dénominateur des demandes. Un incident de transmission n’est pas une perte commerciale prouvée. | Contexte du parcours, hors taux commercial U01. [QC-06](questions_decisions.md#qc-06), [QC-08](questions_decisions.md#qc-08). |
| <a id="h03"></a>H03 | Attribution : taux de prise en charge dans un délai et ancienneté des demandes non attribuées. Ratio/durée candidats. | Demande à attribuer, équipe/global ; date d’attribution et délai à définir. Statut intermédiaire « pending » hypothétique. | Attribution dans le délai proposée ; définition de pris en charge et population éligible inconnues. Une attente ne prouve pas une perte ; aucune lecture individuelle retenue. | U01/U03 pour le sujet seulement. [QC-03](questions_decisions.md#qc-03), [QC-05](questions_decisions.md#qc-05), [QC-08](questions_decisions.md#qc-08). |
| <a id="h04"></a>H04 | Contact/qualification : distinguer joignabilité et qualification. Volumes et conversions candidats. | Prospect/dossier à préciser ; cohortes comparables, équipe. Plusieurs appels ne sont pas plusieurs prospects. | Prospects joints / contactés, puis qualifiés / joints proposés. Preuve d’échange et critères de qualification non établis ; « lead froid » non confirmé comme état. | U01/U02 ; [QM-01](questions_decisions.md#qm-01), [QM-06](questions_decisions.md#qm-06), [QC-01](questions_decisions.md#qc-01). |
| <a id="h05"></a>H05 | Découverte : acceptation de RDV puis réalisation. Volumes et ratios candidats. | Lead/dossier et rendez-vous à distinguer ; période/cohorte et type de RDV. Découverte et démo potentiellement distinctes, à confirmer. | RDV acceptés / leads qualifiés puis découvertes réalisées / RDV prévus proposés. Reports, annulations, échéance des RDV et répétitions à définir. | U01/U02 ; [QM-06](questions_decisions.md#qm-06), [QC-02](questions_decisions.md#qc-02), [QC-10](questions_decisions.md#qc-10). |
| <a id="h06"></a>H06 | Démo : tenue effective et présence du dossier dans la phase. Volumes/ratio candidats. | Séance distincte et dossier ayant une séance tenue ; première démo, compléments et absences. Date prévue arrivée à échéance pour le candidat de présence. | Démos tenues / démos prévues arrivées à échéance proposé ; preuve de tenue, rattachement et reports inconnus. Démo complémentaire non obligatoire par défaut. | Même sujet que U04/O04, **formule H06 non validée**. [QC-02](questions_decisions.md#qc-02), [QC-09](questions_decisions.md#qc-09). |
| <a id="h07"></a>H07 | Proposition : remise de l’offre et durées. Ratio/durées candidats. | Dossier éligible, cohorte comparable ; date de remise et étapes à confirmer. | Besoins avec proposition remise / besoins éligibles proposé. Preuve de remise et éligibilité inconnues ; étapes possiblement sautées ou revisitées. | U01/U03 ; [QM-01](questions_decisions.md#qm-01), [QC-03](questions_decisions.md#qc-03), [QC-10](questions_decisions.md#qc-10). |
| <a id="h08"></a>H08 | Issues : taux de gain et motifs de perte possibles. Ratio et analyse qualitative candidats. | Dossiers clos éligibles, période/cohorte à préciser ; issues alternatives. | Taux de gain sur clos éligibles proposé ; inclusions abandon/réouverture inconnues. Nurturing n’est pas une perte définitive par défaut ; motifs à examiner si pertinents. | U01/U02/B02 ; [QM-01](questions_decisions.md#qm-01), [QC-01](questions_decisions.md#qc-01), [QC-10](questions_decisions.md#qc-10). |
| <a id="h09"></a>H09 | Synchronisation HubSpot : concordance des deals, délais et écarts de statuts/dates. Contrôle transversal. | Besoin à synchroniser et deal rapproché à même date ; identités et délai attendu à définir. | Deals correctement synchronisés / besoins à synchroniser proposé. Une discordance ne constitue ni un étage du tunnel ni une perte commerciale établie. | Risque de désalignement documenté, pas ampleur mesurée. [QC-06](questions_decisions.md#qc-06), [QC-08](questions_decisions.md#qc-08), [QC-10](questions_decisions.md#qc-10). |
| <a id="h10"></a>H10 | Vie client : activation, puis rétention/churn éventuels. Ratio d’activation et analyses candidates distinctes. | Société/projet/abonnement ; signés dont le démarrage est attendu, période d’activation/service. Plusieurs lignes peuvent relever d’un projet. | Abonnements démarrés / deals signés dont le démarrage est attendu proposé, grains à réconcilier. Fin de ligne ≠ churn certain ; démarrage ≠ paiement. Churn désormais retenu en U10/U11 ; rétention et taux d’activation restent candidats. | Règles U05/U07/U10/U11 retenues selon leurs fiches ; cela ne valide pas tout H10. [QM-04](questions_decisions.md#qm-04), [QC-08](questions_decisions.md#qc-08), [QC-10](questions_decisions.md#qc-10). |

## 7. Mesures du SQL historique — L01 à L04

**Statut commun : observations issues d’une analyse statique enregistrée.** Les identifiants L01–L04 sont ajoutés ici pour assurer la correspondance avec les noms du SQL ; ils ne créent aucune demande cible. Source : S-L et S-U section 12, lignes 739–748. Grain de restitution actuel : **semaine × équipe**, semaine calculée par `toMonday(day)`. Le code remplace une équipe NULL par « Autre » ; une chaîne vide peut subsister selon les réglages de jointure, donc ce libellé n’est pas garanti pour tous les dossiers non rattachés (analyse SQL §5.3). Ces choix décrivent l’existant, sans être adoptés pour le cockpit.

La population historique est limitée aux versions non supprimées de besoins `typeOf = 4`, créés depuis le 1er janvier 2024 ; le calendrier va de cette date au jour d’exécution. Le montant utilisé est estimé HT, sans normalisation mensuelle explicite. Filtrage des suppressions avant reconstitution, rattachement aux versions d’équipes et traitement des intervalles limitent l’interprétation des résultats ; aucune de ces conventions n’est reconduite comme règle cible (SQL lignes 5–20 et analyse §3–5).

| ID et nom historique | Définition effectivement observée dans le SQL | Unité, population et temporalité | Rapport au besoin cible et limites |
| --- | --- | --- | --- |
| <a id="l01"></a>L01 — `open_deals` | `uniqExactIf(id, state IN (0, 20, 21, 22, 23, 24, 25, 26, 28))`, lignes 62–64. | Nombre d’identifiants de besoins observés dans ces états au moins une fois pendant la semaine du groupe. Inclut des états avant démo et nurturing. | Proche de la thématique M03, **pas une photo à date**. La liste d’états n’est pas une définition cible d’ouvert ou de qualifié. Populations du SQL et risques de rapprochement à lire dans son analyse. |
| <a id="l02"></a>L02 — `pipe_amount` | Somme des montants journaliers des états listés, divisée par `uniqExact(day)` du groupe, lignes 63–64. | Montant issu d’une moyenne sur les jours représentés du groupe semaine/équipe ; dénominateur dépend des lignes présentes, pas nécessairement de tous les jours calendaires attendus. | Thématique M05, **pas formule validée du stock ni de sa moyenne cible**. Risques de duplications, rattachements et changement intra-journée décrits dans l’analyse ; nature monétaire non validée par le nom. |
| <a id="l03"></a>L03 — `signed_deals` | `uniqExactIf(id, state = 1)`, ligne 65. | Nombre de besoins vus à l’état 1 pendant la semaine ; mesure de présence dans cet état sur la fenêtre, pas stock à un instant unique. | **Pas nombre d’événements de nouvelles signatures**. Ne règle ni l’événement de signature U06 ni toutes les issues gagnées B02. |
| <a id="l04"></a>L04 — `signed_amount` | Somme des montants journaliers à l’état 1 / jours représentés, ligne 66. | Montant moyen selon le groupe semaine/équipe du SQL. | **Ni MRR signé, ni MRR actif, ni encaissements par définition**. Ne devient pas le réalisé O01 parce que son nom contient `signed`. |

Les arbitrages de [QC-01](questions_decisions.md#qc-01), [QC-04](questions_decisions.md#qc-04), [QC-06](questions_decisions.md#qc-06) et [QC-10](questions_decisions.md#qc-10), ainsi que [QM-04](questions_decisions.md#qm-04) et [QM-06](questions_decisions.md#qm-06), restent indépendants du fonctionnement historique. Aucune requête n’a été relancée pour écrire ces fiches.

## 8. Matrice de couverture et correspondances

### 8.1. Familles M, B, O et U : correspondance exhaustive

| Attente source / repère raw | Reprise dans ce catalogue | Regroupement et état de couverture |
| --- | --- | --- |
| S-M zone 1 / M01 | [M01](#m01), [O02](#o02) | Réalisé monétaire, cible et taux liés, non confondus ; définition ouverte. |
| S-M zone 2 / M02 | [M02](#m02) | Volume de génération conservé séparément de M01 ; génération/source/Inbound ouverts. |
| S-M zone 3 / M03 | [M03](#m03) | Nombre à date et parts conservés ; ouvert/dénominateur ouverts. |
| S-M zone 4 / M04 | [M04](#m04), [B03](#b03), [O03](#o03) | Même mesure de base, sa lecture historique et sa cible ; coefficients non validés. |
| S-M zone 5 / M05 | [M05](#m05) | Stock non pondéré et tendance conservés ; base monétaire ouverte. |
| S-M zone 6 / M06 | [M06](#m06) | Ratio de couverture distinct de M05 ; objectif et compatibilité ouverts. |
| S-M zone 7 / M07 | [M07](#m07) | Proposition conservée avec sens/formule incomplets ; aucun remplacement par U05. |
| S-M zone 8 / M08 | [M08](#m08), [B01](#b01), [U03](#u03) | Stagnation, durée courante et autres durées reliées mais distinctes ; seuil ouvert. |
| S-B ligne 9 / B01 | [B01](#b01) et règle [R05](intent_ia.md#r05-histoire) | Ancienneté et capacité d’historisation conservées ; pas double KPI ajouté à M08. |
| S-B lignes 10 et 15 / B02 | [B02](#b02) | Cohortes mensuelles, effectifs/% et trois horizons conservés ; conventions ouvertes. |
| S-B lignes 11 et 16 / B03 | [B03](#b03), [M04](#m04) | Historique/recalcul souhaités ; pas prévision supplémentaire inventée. |
| S-O `mrr_signed` / O01 | [O01](#o01), [U06](#u06) | Cible et réalisé reliés ; signature/normalisation ouvertes. |
| S-O `pipeline_generated` / O02 | [O02](#o02), [M01](#m01) | Cible monétaire du flux ; ne remplace pas M02. |
| S-O `pipeline_weighted` / O03 | [O03](#o03), [M04](#m04) | Cible séparée des probabilités ; comparaison fin de mois par équipe. |
| S-O `demos` / O04 | [O04](#o04), [U04](#u04) | Cible en nombre ; grain du réalisé non choisi. |
| S-U Q11 / U01 | [U01](#u01) | Entrées, sorties, conversions et pertes conservées ; seuils/populations ouverts. |
| S-U Q11 et Q12 / U02 | [U02](#u02), [R01](intent_ia.md#r01-identites) | Analyse des parcours et hypothèse de rattachement société conservées. |
| S-U Q9 et Q11 / U03 | [U03](#u03), [B01](#b01) | Durées courantes, passages/cumuls/cycle distingués ; statistiques ouvertes. |
| S-U Q3 / U04 | [U04](#u04), [O04](#o04) | Distinction action/phase acquise ; règles opérationnelles ouvertes. |
| S-U Q2, cycle 2 / U05 | [U05](#u05) | Boond retenu ; photo fin de mois sans prorata ; états/bornes/histoire ouverts. |
| S-U Q2, cycle 2 / U06 | [U06](#u06), [O01](#o01) | MRR signé distinct du MRR actif/paiement ; calcul ouvert. |
| S-U Q2, cycle 2 / U07 | [U07](#u07) | Besoin d’ajout au MRR actif conservé ; mouvements ouverts. |
| S-U Q2, cycle 2 / U08 | [U08](#u08) | Demande initiale tracée, exclue par décision utilisateur échange 5 point 4. |
| S-U Q2, idée complémentaire / U09 | [U09](#u09) | Option à discuter, pas KPI obligatoire ; pas assimilée au réalisé. |

### 8.2. Demandes transversales et éléments qui ne sont pas des KPI isolés

| Attente source | Reprise | État, regroupement ou limite |
| --- | --- | --- |
| S-M guide : santé du pipeline ; volume, conversion, valeur, stagnation | [M02](#m02), [M03](#m03), [M04](#m04), [M05](#m05), [M08](#m08), [U01](#u01) ; [intent](intent_ia.md) | Usages conservés. Une mesure ne suffit pas à attribuer la cause d’un problème. |
| S-M guide : « Combien d’activité/pipe faut-il générer pour atteindre le BP ? » | [M01](#m01), [M06](#m06), [U01](#u01) ; [QC-04](questions_decisions.md#qc-04) | Question d’usage documentée conservée ; sens de BP, raisonnement inverse, horizon et hypothèses inconnus. Aucun nouvel indicateur/formule inversée validé. |
| S-M guide : opportunité démarrant à la démo ; lead amont distinct | [M02](#m02), [B02](#b02), [U02](#u02), [U03](#u03) ; [QM-06](questions_decisions.md#qm-06) | Contradiction cycle/maquette/historique conservée ; diagnostic Q10 n’impose pas la frontière qualifiée. |
| S-M zone 2 : agrégation Direction en « Inbound » | [M02](#m02) ; [QC-05](questions_decisions.md#qc-05) | Demande originale conservée ; dimension et correspondances à confirmer. |
| S-M filtres : segment, canal/source, période | Fiches associées et [R04](intent_ia.md#r04-axes) | Applications justifiées décrites ; aucune propagation universelle aux indicateurs de revenu. |
| S-M filtres/grains : individu, IC, Manager, Direction | [R04](intent_ia.md#r04-axes), section 1 et fiches M | Exclusion générale initiale remplacée aux échanges 8–9 : analyse individu/équipe U14 dans une feuille dédiée, faisabilité à vérifier ; synthèse équipe/global et objectifs collectifs conservés. |
| S-U section 12 E : équipe SMB/LA/ES, société, étape, issue, dates et cohortes | Fiches concernées ; [R01](intent_ia.md#r01-identites), [R02](intent_ia.md#r02-temps), [R04](intent_ia.md#r04-axes) | Grains des objets et axes de regroupement distingués. `segment` référentiel = équipe documentée ; pas toute segmentation société. |
| S-M zones 1/4 : jauges ; zone 2 : barres ; zone 3 : tableau/parts | M01–M04 | Formes proposées conservées, pas choix final de dashboard. |
| S-M zones 5/6/7 : indicateur et tendance ; zone 8 : liste, alerte, vue stage/segment | M05–M08 ; [QC-08](questions_decisions.md#qc-08) | Formes proposées conservées ; place du détail de dossier à discuter dans l’orientation stratégique. |
| S-B : historiser changements de stage | [B01](#b01), [B02](#b02), [B03](#b03), [U02](#u02), [U03](#u03), [R05](intent_ia.md#r05-histoire) | Capacité métier nécessaire au besoin ; aucune méthode d’implémentation sélectionnée. |
| S-B ligne 20 : snapshot manuel quotidien et append-only en attendant | [B03](#b03), [R02](intent_ia.md#r02-temps), [QC-06](questions_decisions.md#qc-06) | Dispositif provisoire documenté ; ni cadence cible ni disponibilité quotidienne de toutes les sources. |
| S-B ligne 5 et S-U Q4 : possibilité de livrer plus tard, liste complète avant faisabilité | Préambule et ensemble du catalogue | Aucun besoin supprimé pour manque de données. La base visuelle V1 retenue à l’échange 9 ne limite pas le catalogue ni le détail du modèle. |
| S-U Q1/Q7 : cinq ans d’agrégats, rétention détaillée/hypothèses de traitement | [intent](intent_ia.md), [QC-07](questions_decisions.md#qc-07) | Contrainte transverse, pas horizon J+30/J+60/J+90 ni preuve juridique. |
| S-U Q8 : lectures jour/semaine/mois, fréquence et fraîcheur | [R02](intent_ia.md#r02-temps), [QC-06](questions_decisions.md#qc-06) | Trois sujets distincts ; calendrier et usages restant à préciser. |
| S-U Q5 : Sales dans Boond, Marketing dans HubSpot ; risque de désalignement | [intent](intent_ia.md), [QC-08](questions_decisions.md#qc-08), [H09](#h09) | Fonctionnement compris ; rapports Marketing exacts inconnus, décalage non mesuré. Pas ajout automatique d’un KPI d’écart. |
| S-U Q15 : séparation objectifs/probabilités et conflit de sens | O01–O04, [M04](#m04), [M07](#m07), [QM-05](questions_decisions.md#qm-05) | Séparation acquise ; signature finale retenue échange 5, validité/source des valeurs ouvertes. |
| S-U Q16 : définitions communes et arbitrage | [intent](intent_ia.md), [QM-03](questions_decisions.md#qm-03) | Alignement conservé ; utilisateur arbitre du case, QM-03 résolue. |

### 8.3. Hypothèses et existant : aucune promotion implicite en exigence

| Source / identifiant | Reprise | Statut dans le clean intent |
| --- | --- | --- |
| S-H `n=1` / H01 | [H01](#h01) | Proposition de suivi formulaire ; non validée. |
| S-H `n=2` / H02 | [H02](#h02) | Contrôle de transmission proposé ; non conversion commerciale. |
| S-H `n=3` / H03 | [H03](#h03) | Attribution/délai proposés ; non pilotage individuel. |
| S-H `n=4` / H04 | [H04](#h04) | Conversions contact/qualification candidates. |
| S-H `n=5` / H05 | [H05](#h05) | Découverte candidate ; événements à confirmer. |
| S-H `n=6` / H06 | [H06](#h06), liens U04/O04 | Sujet lié, formule candidate non validée. |
| S-H `n=7` / H07 | [H07](#h07), liens U01/U03 | Sujet lié, preuve de remise/dénominateur non validés. |
| S-H `n=8` / H08 | [H08](#h08), liens U01/U02/B02 | Sujet lié, taux de gain/motifs candidats. |
| S-H `n=9` / H09 | [H09](#h09) | Contrôle de synchronisation proposé ; pas perte commerciale. |
| S-H `n=10` / H10 | [H10](#h10), liens U05/U07 | Churn retenu en U10/U11 par échanges 5–6 ; autres mesures H10 encore candidates. Pas de double compte. |
| S-L `open_deals` | [L01](#l01), comparaison M03 | Fonctionnement observé, pas définition cible. |
| S-L `pipe_amount` | [L02](#l02), comparaison M05 | Fonctionnement observé, pas définition cible. |
| S-L `signed_deals` | [L03](#l03), lien thématique U06 | Fonctionnement observé, pas demande de flux validée. |
| S-L `signed_amount` | [L04](#l04), distinction U05/U06/U08 | Fonctionnement observé, aucune équivalence financière retenue. |

### 8.4. Précisions des échanges 5 et 6

| Attente / décision | Reprise | État |
| --- | --- | --- |
| Churn clients | [U10](#u10), [U12](#u12)/[U13](#u13) auxiliaires | Retenu ; grain/cas multiples à préciser. |
| Churn MRR départs + baisses hors expansions/New MRR | [U11](#u11), [R03](intent_ia.md#churn) | Retenu après correction du solde initial ; détails en QC-12. |
| Distinguer clients partis et abonnements moins chers | U10, U11-D/U11-B/U11-C | Besoin retenu échange 6 ; effectif des baisses QC-13 ; pas de doublon des totaux. |
| New MRR nécessaire | [U07](#u07) | Déjà présent, confirmé sans nouveau doublon. |
| Encaissements exclus | [U08](#u08) | Exclusion utilisateur, pas contrainte de faisabilité. |
| MRR fin de mois sans prorata | U05–U07/U10–U13 | Cadence/convention acquises ; événements encore ouverts. |
| Versions raw existantes | R05, T-OPP/T-ACT/T-MRR | Fait ; couverture des événements à vérifier. |
| Deux grains et durées de démo | U03/U04, B01, O04 | Retenu ; échange 22 fixe les RDV tenus et le stock In demo ; grain société du stock fixé échange 23 ; chaînage/preuve ouverts. |
| Pondération signature finale | M04/B03/O03, QM-05 | Sens clos ; valeurs à confirmer, aucune conversion d’unité. |
| Funnels nouveaux clients/upsells | U01–U03, M/B selon périmètre, QC-11 | Séparation et conservation retenues ; filtre de vue proposé, pas filtre new global. |
| Objectifs simples à fin de mois pour Sales | O01–O04, M01/M04 | Cadence/niveau clos ; réalisés à définir. |
| Attribution équipe et canal | Conventions, R04, QM-02/QC-05 | Proposition utilisateur de travail ; mappings/codes ouverts. |
| Utilisateur arbitre | QM-03/DU-17 | Résolu pour le case. |

### 8.5. Échanges 8–9 : synthèse et profondeur du modèle

| Attente | Reprise | Statut |
| --- | --- | --- |
| Garder objectifs/réalisé et MRR/churn | O01–O04, M01/M04, U05–U07/U10/U11 | Présentation validée, chiffres fictifs, définitions ouvertes non fermées. |
| Grand tunnel avec sélecteur de mesure | U01–U03 ; maquette v2 | Organisation demandée ; modes montant/durée à définir sans les transformer en conversions. |
| Individu vs équipe hors synthèse | [U14](#u14) | Besoin souhaité, faisabilité et référence d’équipe à préciser. |
| Base dashboard V1, modèle fin réutilisable | Tous les grains du catalogue ; [table des champs et correspondances ClickHouse](correspondance_champs_clickhouse.md) | Orientation utilisateur : garder versions, passages, actions, dimensions et mouvements observables, pas seulement les agrégats de synthèse. |

## 9. Dépendances avant spécification

Tous les anciens repères M/B/O/U, H et L sont conservés. U10–U13 explicitent churn et quantités de clientèle ; U11 sépare départs et baisses. U08 est exclu ; U09 reste optionnel ; H06/H10 ne sont promus que pour les besoins explicitement repris. U14 ajoute l’analyse individuelle dédiée. Les deux catalogues partagent les IDs.

Restent ouverts : populations/réouvertures et montants d’entrée (QC-01/QC-11), preuve/liens de démo et attribution (QC-02), délais/seuils (QC-03), états/montants signés et libellé des nouveaux clients (QM-04), continuité/corrections du churn (QC-12/QC-13), valeurs des probabilités (QM-05), MRR potentiel moyen/couverture (QC-04), champ canal/mappings (QM-02/QC-05), histoire/fraîcheur/conservation (QC-06/QC-07/QC-10). Cadence des objectifs, sens de la pondération et arbitre du case ne sont plus ouverts.

Ces références aux tables restent documentaires. Aucune requête en base n’a été lancée. La première architecture est retirée à l’échange 10 ; la [table des champs et correspondances ClickHouse](correspondance_champs_clickhouse.md) devient le support de travail, avec les inconnues préservées.

**Préparation du staging — échange 11 :** la [table des correspondances](correspondance_champs_clickhouse.md) décompose chaque champ calculé, partiel ou ouvert en entrées sources et paramètres. L’[inventaire des sources du staging](inventaire_sources_staging.md) déduplique les colonnes physiques par table ; champs JSON, clés, versions et sources candidates sont explicités. Aucune règle métier ouverte n’est résolue par cette seule cartographie.

**Construction des données — échange 12.** Nous pouvons historiser les sources qui ne le sont pas, ajouter les métadonnées d’import, construire les référentiels techniques utiles (date/country) et produire les champs dérivés/KPI par transformations et croisements entre staging, intermédiaire et mart. L’absence d’une colonne KPI ou d’un calendrier source n’est pas un blocage. Les dates d’import restent distinctes des dates métier ; l’historique créé ne reconstitue pas un passé jamais capturé. Les règles métier et preuves manquantes restent signalées. [Décision DCI-12](questions_decisions.md#dci-12) · [Travail à notre charge](inventaire_sources_staging.md#constructions-techniques).

**Préservation des versions — échange 13 :** le [cadre incrémental CDC](inventaire_sources_staging.md#incremental-cdc) consigne les principes utilisateur de chargement complet puis reprise avec recouvrement, déduplication et conservation des suppressions. La méthode par table et ses tests restent à valider ; les définitions des KPI restent inchangées. [DCI-13](questions_decisions.md#dci-13).

### Couverture des précisions de l’échange 22

| Point utilisateur | Reprise | Statut |
| --- | --- | --- |
| 1 — Entrée à création Boond après formulaire | M01/M02, B02, U02/U03, DU-28 | Retenu ; création ≠ qualification, lien formulaire non présumé universel. |
| 2 — Nombre de démos et Nb In demo | U04-S/U04-P, O04 | Réalisé et stock distincts ; grain société distincte fixé échange 23. |
| 3 — Signé formalités à finaliser | U06/O01, événements pipeline | État 1 retenu ; montant mensuel et date observable ouverts. |
| 4 — Société avec abonnement en cours | U05/U10/U12, R03 | Grain client retenu ; états/bornes de lignes ouverts. |
| 5 — Retour après churn dans New MRR | U07, R03, RAW-E22-01 | Hypothèse case ; pas décision sur le compteur de premières acquisitions U13. |
| 6 — Calcul au niveau client | U11 et expansion, R03, RAW-E22-02 | Net par société entre clôtures ; détail fin conservé. |
| 7 — Départ-retour intra-mois exclu | U07/U10/U11, RAW-E22-03 | Hors scope du case ; question réelle conservée, pas résolue. |
| 8 — Pas de filtre équipe pour MRR/churn | U05/U07/U10/U11/U12, R04 | Bloc portefeuille global ; MRR signé/objectifs commerciaux par équipe inchangés. |

### Couverture de l’échange 23

| Précision | Reprise et statut |
| --- | --- |
| Un prospect pour deux dossiers en Démo de la même société | U04-P / DU-36 : société distincte, résolu. |
| 50 € supplémentaires pour l’upsell de 100 à 150 € | U06 / DU-37 : montant incrémental retenu pour le case ; New MRR inclut les upsells à l’échange 24 ; confirmation réelle conservée dans RAW-E23-01. |

### Couverture de l’échange 24

U07 inclut les upsells et propose le filtre New / Upsell : **DU-38, décision utilisateur**. Expansion devient le détail Upsell de U07, sans nouveau KPI additionnel. U11/R03 utilisent le total New MRR une seule fois ; le choix de granularité client, l’inclusion des retours et le scope intra-mois restent inchangés.
