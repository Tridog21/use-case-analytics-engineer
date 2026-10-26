# Catalogue des indicateurs — version humaine

**Échange 24 :** U07 regroupe désormais New et Upsell dans le total New MRR, avec filtre dédié. Les deux composantes ne s’ajoutent pas une seconde fois au total. [DU-38](questions_decisions.md#du-38).

**Échange 23 :** « Nb In demo » compte les **sociétés distinctes** ayant au moins une opportunité en phase Démo à la date observée : deux dossiers de la même société = un prospect. Pour l’upsell de 100 à 150 €/mois, seule la contribution **supplémentaire de 50 €/mois** est retenue pour le case. Dans sa réponse au montant signé, l’utilisateur écrit « 50 euros en new mrr » : le montant incrémental est décidé ; l’échange 24 inclut ensuite les upsells dans New MRR avec filtre New / Upsell. [Décisions et clarification](questions_decisions.md#du-36).

**Conventions actualisées :** [Décisions de l’échange 22](questions_decisions.md#du-28). MRR actif/churn global sans filtre équipe ; calcul net par société entre clôtures. Les détails et l’historique de toutes les couches restent conservés.

**Échange 19 — historisation de toute la chaîne :** l’exigence couvre staging, intermédiaires, faits, dimensions et liaisons. Distinguer l’unité métier de ses versions et sélectionner les versions pertinentes avant agrégation. Les modalités de révision/restitution et la rétention détaillée restent à spécifier. [Règle commune et deux vues détaillées](architecture_modele_proposition.md#historisation-toutes-couches), [DCI-17](questions_decisions.md#dci-17).

**Échange 18 — organisation modulaire proposée :** intégrer la Démo dans les tables génériques du pipeline et garder son micro-funnel en extension locale. Deux modules — Pipeline/parcours et Revenus/performance — réutilisent les identités et dimensions communes. Les objectifs consomment les réalisés commerciaux publiés ; les abonnements alimentent directement MRR/churn. [Proposition et visuel](architecture_modele_proposition.md#architecture-modulaire), [DCI-16](questions_decisions.md#dci-16). Les définitions métier ouvertes restent ouvertes.

**Échange 15 :** la [liste courte des KPI, définitions et formules](liste_kpi_humaine.md) devient la lecture humaine approuvée. La [nouvelle proposition de modèle](architecture_modele_proposition.md) décrit l’intermédiaire, les faits et les dimensions à partir du staging recensé. Les DTR restent hors de cette proposition ; les règles ouvertes ne sont pas arbitrées par le schéma. [DCI-14](questions_decisions.md#dci-14).

**Distinction KPI / analyse — échange 14 :** ce catalogue conserve aussi des axes et des usages. Une cohorte, un parcours, une évolution historique ou une comparaison individu/équipe ne constitue pas en soi un KPI distinct : on y applique les volumes, montants, taux et durées définis ci-dessous. Les déclinaisons par étape, canal ou type ne doivent pas doubler la liste des mesures.

Ce catalogue répond à trois questions : **que mesure-t-on, que compte-t-on une seule fois, et comment le calcule-t-on ?**

Il reprend toutes les familles du catalogue initial. Les IDs permettent de retrouver chaque fiche dans le [catalogue IA](catalogue_indicateurs_ia.md), où figurent les sources, les références aux tables et les règles détaillées. L’[intent humain](intent.md) explique le projet ; le [registre](questions_decisions.md) rassemble les arbitrages restants.

## 1. Les mots utiles avant de lire les indicateurs

Le **grain** est l’unité élémentaire observée. Ce n’est pas forcément le niveau d’affichage du dashboard.

| Grain | Ce qu’une unité représente |
| --- | --- |
| Société / client | Une entreprise. Active si elle a au moins un abonnement en cours à la clôture ; états d’abonnement à préciser. |
| Opportunité / besoin | Un dossier commercial. Une société peut en avoir plusieurs. |
| Action / séance | Un événement CRM, par exemple une démo. Une opportunité peut avoir plusieurs séances. |
| Passage dans une étape | Une entrée d’un dossier dans un état, jusqu’à sa sortie. Un retour peut créer un autre passage. |
| Ligne d’abonnement | Une composante d’abonnement reliée à un projet. Plusieurs lignes peuvent appartenir au même client. |
| Mouvement de MRR | Un ajout, une hausse, une baisse ou une sortie de valeur récurrente. Ce n’est pas toute modification technique d’une ligne. |
| Mois × équipe × indicateur | Le niveau auquel un objectif mensuel est fourni. |

Un **stock** est une photo à date. Un **flux** décrit ce qui arrive pendant une période. Une **durée** mesure le temps entre deux événements. Une **cohorte** regroupe les dossiers d’un même mois de création.

**Règles communes :**

- Les funnels nouveaux clients et upsells sont séparés. On garde les types ; on ne filtre pas partout sur les seules nouvelles ventes.
- Équipe proposée : à l’entrée pour la génération, à la signature pour le signé, à la date observée pour le pipeline.
- Un canal d’acquisition par opportunité est proposé, fixé à son entrée. Champ source et codes « Inbound » restent ouverts.
- MRR actif photographié à fin de mois, sans prorata journalier. Objectifs vérifiés à fin de mois par équipe Sales.
- Une formule avec une population ou une date « à préciser » n’est pas encore prête à être implémentée.

`Somme` additionne les valeurs ; `nombre distinct` compte une identité une seule fois. Une cible nulle ou absente ne permet pas de fabriquer un taux d’atteinte. Aucune statistique de durée ni seuil de stagnation n’est choisi implicitement.

## 2. L’alimentation et la valeur du pipeline

<a id="m01"></a>
### M01 — Pipeline généré face à l’objectif

Vérifier si la valeur entrée dans le pipeline atteint la cible mensuelle. Ce montant est distinct du nombre de dossiers.

**Grain :** un dossier entrant ; restitution par mois et équipe.

**Calcul :** Valeur générée = somme des montants des dossiers entrés dans le mois. Atteinte = valeur générée ÷ objectif O02 × 100.

**Décidé :** entrée à la création Boond après formulaire (échange 22). **À préciser :** le montant retenu à cette entrée et les populations éligibles. [Fiche détaillée](catalogue_indicateurs_ia.md#m01).

<a id="m02"></a>
### M02 — Nombre d’opportunités générées

Comprendre combien de dossiers alimentent le pipeline, par source.

**Grain :** une opportunité, pas un contact ni une société.

**Calcul :** Nombre distinct d’opportunités éligibles entrées sur la période.

**Décidé :** entrée à la création du dossier dans Boond, sans attendre la qualification ou la démo. **À préciser :** les réouvertures et le champ d’acquisition ; une nouvelle version CDC n’est pas une nouvelle création. [Fiche détaillée](catalogue_indicateurs_ia.md#m02).

<a id="m03"></a>
### M03 — Opportunités ouvertes et répartition

Lire le nombre d’affaires en cours et le poids de chaque source.

**Grain :** une opportunité ouverte à une date.

**Calcul :** Nombre distinct ouvert. Part d’une source = ses dossiers ouverts ÷ total ouvert de référence × 100.

**À préciser :** les états ouverts, le total après filtres et les sources inconnues. [Fiche détaillée](catalogue_indicateurs_ia.md#m03).

<a id="m04"></a>
### M04 — Pipeline pondéré face à l’objectif

Estimer la valeur du portefeuille en tenant compte de la chance de signature finale. Ce n’est pas du revenu acquis.

**Grain :** une contribution par opportunité ouverte à la date observée.

**Calcul :** Somme de (montant du dossier × probabilité de signature finale depuis son étape). Comparaison à O03 à fin de mois.

**À préciser :** la nature du montant et la validité/source des coefficients, notamment pour les upsells. Le sens « signature finale » est décidé. [Fiche détaillée](catalogue_indicateurs_ia.md#m04).

<a id="m05"></a>
### M05 — Pipeline total

Connaître la valeur des dossiers ouverts, sans probabilité.

**Grain :** une contribution par opportunité ouverte à une date.

**Calcul :** Somme des montants des dossiers ouverts éligibles.

**À préciser :** la population ouverte et la nature mensuelle ou contractuelle du montant. [Fiche détaillée](catalogue_indicateurs_ia.md#m05).

<a id="m06"></a>
### M06 — Couverture de l’objectif

Comparer les affaires attendues en clôture dans le mois à l’objectif correspondant.

**Grain :** un dossier encore ouvert ; date observée et mois de closing prévu.

**Calcul :** Somme des montants ouverts dont la clôture est prévue dans le mois ÷ objectif mensuel correspondant.

**À préciser :** quel objectif utiliser et si son unité est compatible. Ne pas choisir automatiquement l’objectif de MRR signé. [Fiche détaillée](catalogue_indicateurs_ia.md#m06).

<a id="m07"></a>
### M07 — MRR potentiel moyen par dossier — proposition du brief

La zone 7 de la maquette propose une valeur mensuelle potentielle moyenne par dossier. Ce besoin est conservé séparément du sigle ADV, que l’utilisateur rapproche de l’Administration des ventes à l’échange 16.

**Grain :** un dossier du portefeuille de référence.

**Calcul :** **Formule non établie.** Montant, probabilité et moyenne sont évoqués, mais leur combinaison n’est pas définie.

**À préciser :** la population, le numérateur, le dénominateur et la preuve que la valeur est bien récurrente mensuelle. [Fiche détaillée](catalogue_indicateurs_ia.md#m07).

<a id="m08"></a>
### M08 — Dossiers stagnants : nombre et montant

Repérer les affaires qui restent longtemps dans une étape.

**Grain :** une opportunité dans son étape actuelle.

**Calcul :** Nombre distinct de dossiers dont l’ancienneté dépasse X ; somme de leurs montants.

**À préciser :** le seuil X, l’unité de temps, les pauses et la population. [Fiche détaillée](catalogue_indicateurs_ia.md#m08).

## 3. Progression, durées et histoire

<a id="u01"></a>
### U01 — Conversions et pertes par étape

Comprendre où les dossiers progressent et où ils sortent du parcours.

**Grain :** un dossier d’une population d’entrée définie, sur une fenêtre définie.

**Calcul :** Conversion A → B = dossiers entrés en A ayant atteint B ÷ dossiers éligibles entrés en A × 100. Pertes = dossiers ayant une issue de perte définie.

**À préciser :** les populations, les horizons et les issues. Un dossier peut encore attendre : perte ≠ automatiquement 100 % − conversion. [Fiche détaillée](catalogue_indicateurs_ia.md#u01).

<a id="u02"></a>
### U02 — Parcours commerciaux

Voir la succession des étapes, les retours, les raccourcis et les issues. Distinguer nouvelles ventes et upsells.

**Grain :** une opportunité et ses passages successifs.

**Calcul :** Ordonner les passages ; les modifications répétées au même état ne créent pas de nouvelle étape. Il s’agit d’une analyse, sans formule numérique unique.

**À préciser :** le workflow admis et le traitement des états absents. L’absence de trace ne prouve pas l’absence réelle. [Fiche détaillée](catalogue_indicateurs_ia.md#u02).

<a id="b01"></a>
### B01 — Ancienneté dans l’étape actuelle

Mesurer depuis combien de temps un dossier est dans son état courant.

**Grain :** le passage actuel d’une opportunité dans une étape.

**Calcul :** Date d’observation − date d’entrée dans cette étape.

**À préciser :** la date d’entrée fiable et la règle après un retour dans l’étape. [Fiche détaillée](catalogue_indicateurs_ia.md#b01).

<a id="u03"></a>
### U03 — Durées du cycle et de la démo

Localiser les temps d’attente, avec deux lectures de la démo : statut commercial et sous-parcours d’actions.

**Grain :** un passage d’état ; un dossier pour le cycle ; un intervalle entre étapes d’un même parcours de démo.

**Calcul :** Passage terminé = sortie − entrée. Cycle = issue − entrée retenue. Phase démo = sortie Show Boond − entrée Show Boond. Étape du sous-parcours démo = événement de fin − événement de début.

**À préciser :** les événements, le chaînage des actions, les pauses/retours, l’unité et les statistiques. La durée d’une séance d’agenda est différente du délai entre étapes. [Fiche détaillée](catalogue_indicateurs_ia.md#u03).

<a id="b02"></a>
### B02 — Cohortes à J+30, J+60 et J+90

Suivre ce que deviennent les dossiers créés pendant un même mois.

**Grain :** une opportunité de sa cohorte, observée à un horizon.

**Calcul :** Compter les dossiers ouverts/gagnés/perdus à l’horizon ; proportion = effectif de l’issue ÷ effectif de cohorte retenu × 100.

**À préciser :** l’ancrage de J, les autres issues et les dossiers non observables. Une cohorte trop récente n’a pas encore de résultat à un horizon futur. [Fiche détaillée](catalogue_indicateurs_ia.md#b02).

<a id="b03"></a>
### B03 — Évolution du pipeline pondéré

Voir l’évolution historique du montant pondéré au fil des changements de dossiers.

**Grain :** une contribution de dossier à chaque date observée.

**Calcul :** Recalculer M04 à chaque date, sous des conventions historiques cohérentes. Ne pas additionner ces stocks entre dates.

**À préciser :** les coefficients historiques et les corrections tardives. Les versions raw existent déjà ; leur couverture doit être vérifiée. [Fiche détaillée](catalogue_indicateurs_ia.md#b03).

## 4. Les démonstrations

<a id="u04"></a>
### U04 — Actions de démo et dossiers en phase démo

Deux KPI distincts sont retenus à l’échange 22 :

| KPI | Grain et définition | Calcul |
| --- | --- | --- |
| **U04-S — Nombre de démos** | Un rendez-vous de démonstration réellement réalisé ; flux sur la période. | Nombre distinct de RDV de démo tenus pendant la période. |
| **U04-P — Nb In demo** | Une société ayant au moins une opportunité dans la phase Démo à la date ; stock. | Nombre distinct de sociétés concernées, même si chacune a plusieurs dossiers en Démo. |

O04 compare **U04-S** à l’objectif de démos. Les demandes, séances planifiées et annulations ne prouvent pas la réalisation. Préserver Démo 1 et complémentaire dans le détail ; dédupliquer une séance représentée plusieurs fois.

**À préciser :** preuve de tenue, chaînage et attribution équipe. U04-P compte les sociétés distinctes (échange 23), pas les dossiers ; un total de sociétés ne s’obtient pas en additionnant des groupes qui se recouvrent. Les entrées dans la phase sont un flux distinct déjà couvert par les mesures par étape. [Fiche IA](catalogue_indicateurs_ia.md#u04).

## 5. Revenus et santé du portefeuille

**Convention du case :** clôture mensuelle sans prorata journalier. Dans les formules, N désigne le mois étudié et N−1 le mois précédent. Le MRR actif est un stock ; le signé et les mouvements restent des valeurs du mois arrêtées à la clôture.

<a id="u05"></a>
### U05 — MRR actif

Connaître la valeur mensuelle des abonnements actifs à la fin du mois.

**Grain :** une ligne d’abonnement active, puis regroupement sans double compte.

**Calcul :** Somme des montants mensuels des lignes actives à la clôture, à partir de Boond. Pas de prorata journalier.

**À préciser :** les états actifs, bornes, remplacements de lignes, remises et devises. Ne pas remultiplier une quantité déjà incluse dans le montant. [Fiche détaillée](catalogue_indicateurs_ia.md#u05).

<a id="u06"></a>
### U06 — MRR signé

Mesurer le MRR engagé commercialement pendant le mois.

**Grain :** une signature admissible de dossier. **Événement décidé :** entrée dans « Signé — formalités à finaliser » (état 1), sans seconde vente au passage aux formalités finalisées (état 14).

**Calcul :** somme des montants mensuels récurrents engagés par ces signatures du mois.

**À préciser :** donnée source du montant mensuel signé, annulations/réouvertures et preuve de date. Le case retient la valeur incrémentale des upsells : 150 − 100 = 50 €/mois, décision échange 23. L’échange 24 inclut les upsells dans New MRR, avec distinction New / Upsell. Un montant estimé n’est pas automatiquement du MRR. [Fiche IA](catalogue_indicateurs_ia.md#u06).

<a id="u07"></a>
### U07 — New MRR : total et détail New / Upsell

Mesurer le MRR supplémentaire actif entre deux fins de mois. **L’upsell appartient au New MRR**, décision utilisateur de l’échange 24.

**Grain :** société × mois × composante, détail des abonnements conservé.

| Filtre | Définition | Formule |
| --- | --- | --- |
| **New** | Sociétés entrantes, retours après churn inclus par convention du case. | Somme du MRR à fin N des sociétés actives à fin N et inactives à fin N−1. |
| **Upsell** | Hausse nette active des sociétés restées actives ; ancien libellé Expansion. | Pour les sociétés actives aux deux clôtures : somme de `max(MRR fin N − MRR fin N−1, 0)`. |
| **Tous** | Total du KPI New MRR. | `New + Upsell`. |

Le filtre sert à expliquer le total, pas à créer des montants à lui rajouter. Un upsell passant de 100 à 150 €/mois contribue à hauteur de 50 € lorsqu’il est actif dans la comparaison de clôtures. La signature et son activation restent deux événements différents.

**Limites :** critères d’activité, dates et couverture restent à vérifier. La catégorie financière Upsell ne prouve pas le lien à un dossier commercial précis ; ce rattachement reste à établir. Retours dans New ne signifie pas premières acquisitions dans le compteur de clients. [Règle commune](intent_ia.md#mrr-client-cloture) · [Fiche IA](catalogue_indicateurs_ia.md#u07).

<a id="u10"></a>
### U10 — Churn clients

Compter les départs complets du portefeuille entre deux clôtures.

**Grain :** société × mois. Une société est active si elle a au moins un abonnement en cours à clôture.

**Calcul :** nombre distinct de sociétés actives à fin N−1 et inactives à fin N. Arrêter une ligne tout en gardant une autre n’est pas un départ client.

**Limites :** états d’abonnement et couverture historique à vérifier. Départs-retours dans le même mois exclus du case ; ils ne sont pas déclarés inexistants. [Fiche IA](catalogue_indicateurs_ia.md#u10).

<a id="u11"></a>
### U11 — Churn MRR et ses composantes

Mesurer les pertes par départ et par baisse chez les clients restants. **Convention de l’échange 22 : calcul net par société**, après addition de ses abonnements, entre deux fins de mois. Les gains d’une société ne compensent pas les pertes d’une autre.

| Repère | Définition | Calcul |
| --- | --- | --- |
| <a id="u11-d"></a>U11-D | MRR perdu avec les sociétés sorties | Somme du MRR à fin N−1 des sociétés actives à fin N−1 et inactives à fin N. |
| <a id="u11-b"></a>U11-B | Baisse nette des sociétés restées actives | Pour les sociétés actives aux deux clôtures : somme de `max(MRR fin N−1 − MRR fin N, 0)`. |
| <a id="u11-c"></a>U11-C | Clients en baisse | Nombre distinct de sociétés actives aux deux clôtures dont le MRR total diminue. |

**Churn MRR = U11-D + U11-B.** Les populations de départ et de baisse sont disjointes dans cette lecture par clôtures. La composante Upsell de New MRR (ancien nom Expansion) est, chez les sociétés restées actives, la somme de `max(MRR fin N − MRR fin N−1, 0)`. Elle est déjà incluse dans le total New MRR.

Exemple : une société augmente une ligne de 100 € et réduit une autre de 40 € : **60 € d’expansion, aucun churn MRR** pour cette société. Le détail des lignes reste conservé pour d’autres analyses.

**Réconciliation :** `MRR final = MRR initial + New MRR total (New + Upsell) − départs − baisses`, à périmètre et unité identiques. Une correction ou un écart de couverture ne doit pas être caché dans le churn. [Règle commune](intent_ia.md#mrr-client-cloture).

**À préciser :** critères d’activité, continuité et corrections. La granularité réelle ligne/client est une question métier conservée dans [RAW-E22-02](../raw_intent/questions_metiers.md#raw-e22-02), mais elle ne bloque plus le case. Départs-retours intra-mois hors périmètre. [Fiche IA](catalogue_indicateurs_ia.md#u11).

<a id="u12"></a>
### U12 — Clients actifs — quantité utile au churn

Connaître la taille du portefeuille à chaque clôture. Ce compteur soutient U10.

**Grain décidé :** une société ayant au moins un abonnement en cours à la clôture (échange 22).

**Calcul :** Nombre distinct de clients actifs à la fin du mois ; plusieurs lignes ne multiplient pas les clients.

**À préciser :** la définition opérationnelle du client actif, notamment pauses et gratuité. Ce n’est pas forcément « MRR strictement positif ». [Fiche détaillée](catalogue_indicateurs_ia.md#u12).

<a id="u13"></a>
### U13 — Nouveaux clients actifs — quantité utile au churn

Isoler les entrants pour ne pas confondre variation du nombre de clients et départs.

**Grain :** un client nouvellement actif.

**Calcul :** Nombre distinct de nouveaux clients activés pendant le mois. En l’absence d’autres mouvements : départs = clients initiaux + entrants − clients finaux.

**À préciser :** l’inclusion des retours dans le libellé « nouveaux clients » au sens acquisition ; leur inclusion monétaire dans New MRR est acquise pour le case. Pour réconcilier les effectifs de clôture, compter séparément les entrants `actifs_N hors actifs_N−1`, retours compris. Cette quantité n’est pas automatiquement un nombre de premières acquisitions. Les départs-retours intra-mois sont exclus de l’analyse du case. [Fiche détaillée](catalogue_indicateurs_ia.md#u13).

<a id="u08"></a>
### U08 — Encaissements mensuels : exclus

Sommes réellement reçues pendant le mois, au grain **règlement**. La définition de sens serait la somme des paiements reçus, sous conventions de remboursements à définir si le besoin revenait.

**Hors périmètre par décision utilisateur**, pas à cause du manque de données. L’ancienne demande reste tracée. Un abonnement ne prouve pas un paiement. [Fiche détaillée](catalogue_indicateurs_ia.md#u08).

<a id="u09"></a>
### U09 — Scénario sans churn ni New MRR : option

Examiner un portefeuille supposé stable jusqu’à la fin du mois. **Grain :** portefeuille à une date et horizon de projection.

**Pas de formule validée :** la variable à projeter et les autres mouvements autorisés restent inconnus. Cette idée n’est pas une mesure obligatoire ni une garantie de paiement. [Fiche détaillée](catalogue_indicateurs_ia.md#u09).

<a id="u14"></a>
### U14 — Analyse individuelle comparée à l’équipe

Comprendre la contribution et les résultats d’une personne dans le contexte de son équipe, dans une **feuille dédiée**, hors synthèse. Besoin ajouté aux échanges 8–9, sous réserve de faisabilité.

**Grain :** responsable × période × indicateur, en conservant dessous les dossiers, passages et actions qui expliquent le résultat.

**Calcul :** réutiliser les mesures admissibles du catalogue avec le bon responsable à l’événement. La référence d’équipe reste à choisir : total, moyenne par membre éligible, médiane ou distribution. Aucun ratio individu/équipe ni cible personnelle n’est imposé.

**À préciser :** indicateurs comparés, membres éligibles, transferts, répartition des durées et disponibilité historique. Les objectifs fournis restent des objectifs d’équipe. [Fiche IA](catalogue_indicateurs_ia.md#u14) · [Question QC-14](questions_decisions.md#qc-14).

## 6. Les quatre objectifs mensuels

Une cible est une valeur fournie, pas une probabilité. **Grain commun : mois × équipe Sales × indicateur.** Contrôle à fin de mois, sans répartition quotidienne ou individuelle.

| Repère | Objectif et unité | Réalisé à lui comparer |
| --- | --- | --- |
| <a id="o01"></a>O01 | MRR signé, euros | U06 du mois ; événement décidé (état 1), montant mensuel encore à définir. |
| <a id="o02"></a>O02 | Pipeline généré, euros | Valeur générée M01 ; pas nombre de dossiers M02. |
| <a id="o03"></a>O03 | Pipeline pondéré, euros | M04 observé à la clôture du mois. |
| <a id="o04"></a>O04 | Démos, nombre | U04-S : RDV de démo réellement réalisés ; preuve de tenue à établir. |

**Calcul des cibles :** lire la valeur du mois et de l’équipe dans le référentiel fourni. Leur méthode de construction n’est pas à réinventer. M01 demande explicitement `réalisé ÷ cible × 100`. Ailleurs, comparer réalisé et cible suppose la même population, période et unité. [Détail des objectifs](catalogue_indicateurs_ia.md#o01).

## 7. Pistes des visualisations et chiffres historiques

### Hypothèses H : des propositions, pas toutes des exigences

Les formules ci-dessous restent **candidates**. Elles nécessitent des populations, événements et données compatibles. Les volumes dessinés dans les schémas ne sont pas des mesures.

| Repère | Définition simple et grain | Calcul candidat / limite |
| --- | --- | --- |
| <a id="h01"></a>H01 | Parcours formulaire ; session/demande à préciser | Volumes affichages/clics/débuts/envois ; envois ÷ débuts. Pas nombre de nouveaux contacts par défaut. |
| <a id="h02"></a>H02 | Transmission d’une demande vers Boond | Reçues dans le délai ÷ demandes à transmettre. Un retard technique n’est pas une perte commerciale. |
| <a id="h03"></a>H03 | Prise en charge ; demande à attribuer | Attribuées dans le délai ÷ demandes éligibles ; âge des non attribuées. Délai ouvert. |
| <a id="h04"></a>H04 | Joignabilité puis qualification ; prospect/dossier | Joints ÷ contactés, puis qualifiés ÷ joints. Plusieurs appels ne sont pas plusieurs prospects. |
| <a id="h05"></a>H05 | Rendez-vous de découverte ; dossier/RDV | Acceptés ÷ leads qualifiés, puis réalisés ÷ prévus. Grains, reports et répétitions à réconcilier. |
| <a id="h06"></a>H06 | Présence aux démos ; séance distincte | Tenues ÷ prévues arrivées à échéance. Ce taux reste candidat ; les deux grains et durées sont déjà retenus en U03/U04. |
| <a id="h07"></a>H07 | Remise d’une proposition ; dossier éligible | Dossiers avec proposition ÷ éligibles ; durée jusqu’à remise. Preuve et éligibilité ouvertes. |
| <a id="h08"></a>H08 | Gain et motifs de perte ; dossier clos | Gagnés ÷ dossiers clos éligibles ; répartition des motifs. Issues et réouvertures à définir. |
| <a id="h09"></a>H09 | Synchronisation HubSpot ; dossier attendu | Correctement synchronisés ÷ dossiers à synchroniser. Un écart n’est pas une perte commerciale. |
| <a id="h10"></a>H10 | Activation/rétention ; société/projet/abonnement | Activation proposée : abonnements démarrés ÷ dossiers signés attendus, grains à réconcilier. **Churn repris comme besoin en U10/U11**, sans valider toute H10. |

[Détail et sources des hypothèses](catalogue_indicateurs_ia.md#h01).

### Mesures L : ce que fait l’ancien SQL

Ces quatre mesures sont conservées pour comparer l’existant au besoin, **sans adopter leurs calculs pour le futur cockpit**. Leur grain de restitution est semaine × équipe, sur une population historique limitée aux nouvelles ventes et aux créations depuis 2024.

| Repère | Définition et calcul observés | Limite essentielle |
| --- | --- | --- |
| <a id="l01"></a>L01 — open_deals | Dossiers distincts vus au moins une fois dans la liste d’états du SQL pendant la semaine | Présence sur période, pas stock à date. |
| <a id="l02"></a>L02 — pipe_amount | Somme des montants journaliers concernés ÷ jours représentés dans le groupe | Moyenne historique selon le SQL, pas définition du pipeline cible. |
| <a id="l03"></a>L03 — signed_deals | Dossiers distincts vus à l’état 1 pendant la semaine | Pas nombre de nouvelles signatures. |
| <a id="l04"></a>L04 — signed_amount | Montants journaliers à l’état 1 ÷ jours représentés | Ni MRR signé ni MRR actif par définition. |

[Formules exactes et limites de l’ancien SQL](catalogue_indicateurs_ia.md#l01).

## 8. Couverture et questions qui restent ouvertes

Les repères M01–M08, B01–B03, O01–O04 et U01–U09 sont tous conservés. U10/U11 ajoutent le churn, U12/U13 explicitent ses compteurs de clientèle, U14 ajoute l’analyse individuelle dédiée. La [matrice détaillée](catalogue_indicateurs_ia.md) relie chaque attente à sa source, son statut et ses éventuels regroupements.

| Demande transversale | Où la retrouver / statut |
| --- | --- |
| Santé du pipeline : volume, conversion, valeur, stagnation | M01–M08, U01–U03 ; pas cause prouvée par un indicateur isolé. |
| Activité nécessaire pour atteindre le « BP » | Question conservée ; sens de BP et calcul inverse ouverts en QC-04. |
| Vue Direction « Inbound », filtres source/segment/période | M02/M03 et règles communes ; codes et associations à définir. |
| Demandes individuelles de la maquette | Désormais reprises dans U14, feuille dédiée ; synthèse équipe/global. Pas de cibles individuelles ajoutées. |
| Détail dossier, graphiques, alertes proposés | Attentes conservées ; pas format final ni seuil décidé. |
| Histoire des étapes, recalcul et snapshot manuel provisoire | B01–B03/U02/U03 ; fréquence de source/recalcul distincte de la période analysée. |
| Cinq ans d’agrégats et conservation des détails | Intent et QC-07 ; rétention détaillée ouverte. |
| Alignement Sales/Marketing et validation | Intent ; utilisateur arbitre du case, rapports Marketing précis encore ouverts. |
| Upsells et effets sur les abonnements | U01–U03/U06/U07/U11 ; questions propres en QC-11. |

**Pour la suite :** préciser preuve des RDV tenus et liens aux sociétés, états d’abonnement, montant signé/upsell, libellé des nouveaux clients, effets des upsells et corrections. Les décisions de l’échange 22 fixent déjà création Boond, état de signature, New MRR avec retours, calcul net par société et MRR/churn global. Puis compléter coefficients, canaux, seuils, MRR potentiel moyen/couverture et histoire. Les décisions déjà prises ne sont pas redemandées. [Questions complètes](questions_decisions.md).

**Champs nécessaires :** la synthèse V1 ne limite pas le détail souhaité. La [table des champs et correspondances ClickHouse](correspondance_champs_clickhouse.md) couvre aussi stagnation, canaux, durées et analyse individuelle. La première architecture est retirée à l’échange 10.

**Préparation du staging — échange 11 :** la [table des correspondances](correspondance_champs_clickhouse.md) décompose chaque champ calculé, partiel ou ouvert en entrées sources et paramètres. L’[inventaire des sources du staging](inventaire_sources_staging.md) déduplique les colonnes physiques par table ; champs JSON, clés, versions et sources candidates sont explicités. Aucune règle métier ouverte n’est résolue par cette seule cartographie.

**Construction des données — échange 12.** Nous pouvons historiser les sources qui ne le sont pas, ajouter les métadonnées d’import, construire les référentiels techniques utiles (date/country) et produire les champs dérivés/KPI par transformations et croisements entre staging, intermédiaire et mart. L’absence d’une colonne KPI ou d’un calendrier source n’est pas un blocage. Les dates d’import restent distinctes des dates métier ; l’historique créé ne reconstitue pas un passé jamais capturé. Les règles métier et preuves manquantes restent signalées. [Décision DCI-12](questions_decisions.md#dci-12) · [Travail à notre charge](inventaire_sources_staging.md#constructions-techniques).

**Préservation des versions — échange 13 :** le [cadre incrémental CDC](inventaire_sources_staging.md#incremental-cdc) consigne les principes utilisateur de chargement complet puis reprise avec recouvrement, déduplication et conservation des suppressions. La méthode par table et ses tests restent à valider ; les définitions des KPI restent inchangées. [DCI-13](questions_decisions.md#dci-13).
