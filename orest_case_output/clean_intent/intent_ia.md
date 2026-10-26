# Intent métier — référence détaillée pour l’IA

**Statut de phase — échange 25 :** consolidation de l’intent terminée à la demande de l’utilisateur. Préparation des spécifications dans [spec_technique — étape 0, conventions](../spec_technique/00_conventions.md), limitées aux règles définies par l’utilisateur à l’échange 26. Les questions métier encore ouvertes restent tracées dans le registre ; cette clôture ne les résout pas automatiquement.

**Règle actuelle — échange 24 : New MRR inclut les upsells.** `New MRR total = composante New + composante Upsell`. Filtre demandé : **New / Upsell**. New conserve les entrants et retours après churn déjà retenus ; Upsell correspond à la hausse nette active des sociétés restées actives. L’expansion est donc une composante du total New MRR, pas un montant à ajouter une deuxième fois. `MRR fin = MRR début + New MRR total − churn MRR`, à périmètre et unité identiques, corrections explicites. [Décision DU-38](questions_decisions.md#du-38).

**Nomenclature résolue à l’échange 24 :** l’utilisateur inclut explicitement les upsells dans New MRR, avec filtre New / Upsell. Le supplément de 50 € reste la valeur retenue pour l’upsell 100 → 150 €/mois. MRR signé et effet actif restent distincts ; la hausse active figure une seule fois dans New MRR total. [DU-38](questions_decisions.md#du-38).

**Échange 23 :** « Nb In demo » compte les **sociétés distinctes** ayant au moins une opportunité en phase Démo à la date observée : deux dossiers de la même société = un prospect. Pour l’upsell de 100 à 150 €/mois, seule la contribution **supplémentaire de 50 €/mois** est retenue pour le case. Dans sa réponse au montant signé, l’utilisateur écrit « 50 euros en new mrr » : le montant incrémental est décidé ; l’échange 24 inclut ensuite les upsells dans New MRR avec filtre New / Upsell. [Décisions et clarification](questions_decisions.md#du-36).

**Démos — échange 22 :** U04-S = séances réellement tenues, un RDV réel compté une fois ; U04-P = « Nb In demo », stock de prospects en phase Démo. U04-P compte les sociétés distinctes, précision de l’échange 23, sans compter les contacts ou les dossiers à leur place. O04 compare les séances réalisées à la cible. Preuve de tenue et chaînage restent à établir. **Filtres :** bloc MRR actif/churn global, sans filtre équipe ; MRR signé et objectifs Sales restent par équipe.

**Mise à jour métier — échange 22 :** entrée à la création Boond après soumission du formulaire ; démos réellement réalisées distinctes de « Nb In demo » ; signature dès « Signé — formalités à finaliser » ; client actif = société avec au moins un abonnement en cours à clôture. Pour le case : réactivations incluses dans New MRR, variation nette par société entre clôtures, départ-retour intra-mois hors périmètre, bloc MRR actif/churn global sans filtre équipe. [Décisions de l’échange 22](questions_decisions.md#du-28). Le supplément signé d’upsell et le grain société de Nb In demo sont précisés à l’échange 23 ; données sources des montants et critères d’activité restent à préciser ; nomenclature New MRR résolue à l’échange 24.

**Échange 19 — historisation de toute la chaîne :** l’exigence couvre staging, intermédiaires, faits, dimensions et liaisons. Distinguer l’unité métier de ses versions et sélectionner les versions pertinentes avant agrégation. Les modalités de révision/restitution et la rétention détaillée restent à spécifier. [Règle commune et deux vues détaillées](architecture_modele_proposition.md#historisation-toutes-couches), [DCI-17](questions_decisions.md#dci-17).

**Échange 18 — organisation modulaire proposée :** intégrer la Démo dans les tables génériques du pipeline et garder son micro-funnel en extension locale. Deux modules — Pipeline/parcours et Revenus/performance — réutilisent les identités et dimensions communes. Les objectifs consomment les réalisés commerciaux publiés ; les abonnements alimentent directement MRR/churn. [Proposition et visuel](architecture_modele_proposition.md#architecture-modulaire), [DCI-16](questions_decisions.md#dci-16). Les définitions métier ouvertes restent ouvertes.

**Précision de l’échange 16 :** l’utilisateur suggère « Administration des ventes » pour ADV et conteste son classement comme KPI. Le sigle n’est plus présenté comme une mesure. La maquette source, zone 7, emploie « ADV / MRR potentiel du pipeline » et décrit un MRR potentiel moyen par deal : cette attente distincte reste tracée, sans formule validée. Le sens exact du sigle dans le brief reste à confirmer.

**Échange 15 :** la [liste courte des KPI, définitions et formules](liste_kpi_humaine.md) devient la lecture humaine approuvée. La [nouvelle proposition de modèle](architecture_modele_proposition.md) décrit l’intermédiaire, les faits et les dimensions à partir du staging recensé. Les DTR restent hors de cette proposition ; les règles ouvertes ne sont pas arbitrées par le schéma. [DCI-14](questions_decisions.md#dci-14).

**État consolidé après l’échange 19, définitions restantes à préciser.** Ce document présente l'état actuel du besoin. La maquette v2 constitue la base du dashboard V1. La première architecture reste retirée ; l’inventaire des champs et sources sert de base à la nouvelle proposition de l’échange 15. Ce document ne constitue pas une spécification technique finale. Les définitions ouvertes sont identifiées avec leurs conséquences ; la clôture du raw intent ne vaut pas validation métier.

Cette version est la référence détaillée destinée à préparer les spécifications techniques. La [version de revue humaine](intent.md) présente le même besoin dans un langage plus accessible.

**Parcours de lecture IA :** ce document → [catalogue complet et matrice de couverture](catalogue_indicateurs_ia.md) → [questions et décisions](questions_decisions.md). Le [journal commun](ia_assistant_story.md) conserve les échanges ; il n'est pas une liste de règles métier à appliquer sans consolidation.

**Consignes de lecture :** préserver les IDs, la provenance et les distinctions de certitude ; utiliser les règles communes ci-dessous ; ne pas compléter les champs inconnus par des conventions supposées. Avant de spécifier une mesure, consulter ses dépendances ouvertes. Une décision de rédaction ou de format ne constitue pas une nouvelle règle métier. La base visuelle V1 est choisie à l’échange 9. À l’échange 10, la première architecture est retirée ; le travail reprend alors par l’inventaire des champs nécessaires et des correspondances sources. L’échange 15 autorise une nouvelle proposition intermédiaire/faits/dimensions, encore à discuter.

**Synchronisation :** après chaque arbitrage, mettre à jour le registre, les fiches concernées et les deux versions au cours de la même itération. Si elles divergent, revenir à la décision sourcée la plus récente et signaler le désaccord ; aucun format n'autorise à inventer une réponse.

<a id="point-b"></a>
## Point B — Résultat métier cible

Disposer d'un cockpit partagé par Sales et Marketing, lisible au niveau global et par équipe, pour comprendre la génération du pipeline, ses conversions, ses durées et sa valeur. La cible fonctionnelle comprend les cohortes mensuelles aux horizons demandés, l'évolution du pipeline pondéré, les comparaisons aux quatre objectifs mensuels et MRR actif, MRR signé, New MRR et churn, décomposé en départs et baisses d’abonnement. Les encaissements sont désormais hors périmètre par décision utilisateur. Les indicateurs et objectifs restent ceux du catalogue ; il ne s'agit pas d'en ajouter.

Un lecteur doit pouvoir comprendre ce qui est compté, sur quelle population et à quelle date, puis distinguer manque de volume, perte de conversion, stagnation et variation de valeur. L'usage attendu est d'orienter les investigations et discussions de pilotage ; les actions précises et les seuils d'intervention restent à définir. Aucun gain chiffré, automatisme de relance ou objectif individuel n'est retenu.

**Pour la présente phase, le résultat à atteindre est un besoin suffisamment explicite et traçable pour spécifier séparément chaque mesure, avec les inconnues qui l'empêchent encore.** Les besoins sans données disponibles restent visibles. Voir la [section consacrée aux manques avant les spécifications](#avant-specifications) et son [explication humaine](intent.md#avant-specifications).

## 1. Problème et résultat recherché

Boond commercialise un ERP/CRM SaaS auprès des ESN et sociétés de conseil. Les Sales suivent leurs dossiers dans Boond ; le Marketing travaille dans HubSpot, qui reçoit les formulaires et une représentation des besoins commerciaux. La VP Sales porte une demande de cockpit préparée avec un cabinet. Les termes « opportunité », « démo » et « MRR » recouvrent aujourd'hui des lectures différentes dans les sources. Le reporting SQL existant fournit certains nombres et montants, sans établir les définitions cibles. **[Documenté]** Sources : [README du projet](../../README.md), §1–3, lignes 32–76 ; [analyse du SQL](../raw_intent/analyse_pipeline_actuel.md), §4.

L'intention est de rendre lisibles la constitution, la progression et la santé du pipeline, afin de comprendre où la conversion se dégrade, combien de temps les dossiers restent dans les étapes et comment évoluent les cohortes et les montants. La lecture retenue est **stratégique, globale et par équipe**. **[Décision utilisateur]** Sources : [raw intent](../raw_intent/raw_intent.md), §12 Q4 et Q11, lignes 624–626 et 786–794 ; décisions [DU-02](questions_decisions.md#du-02) et [DU-03](questions_decisions.md#du-03).

Le cockpit doit permettre de répondre aux questions suivantes, sans prédéterminer l'action à entreprendre :

- Le problème observé vient-il du volume de pipeline, de la conversion, de la valeur des dossiers ou de leur stagnation ? **[Demande maquette : guide supérieur.]**
- À quels endroits du parcours se situent les pertes et les attentes, et comment évoluent-elles entre équipes, périodes et populations comparables ? **[Demande utilisateur : Q11 ; U01–U03.]**
- Que deviennent les dossiers d'une même cohorte à J+30, J+60 et J+90 ? **[Demande expression de besoin : lignes 10 et 15 ; B02.]**
- Quelle valeur de pipeline est ouverte, pondérée ou attendue en clôture, et comment la mettre en regard des objectifs compatibles ? **[Demande maquette : zones 1, 4–7 ; M01, M04–M07.]**
- Comment distinguer MRR actif, MRR signé, New MRR, départs de clients et baisses d’abonnement ? **[Décisions utilisateur : échanges 5–6 ; U05–U07, U10–U13.]** Les encaissements U08 restent tracés mais exclus.
- Combien d'activité ou de pipeline faudrait-il générer pour atteindre le « BP » ? **[Demande maquette : guide supérieur.]** Le sens de BP, la méthode et les hypothèses de cette analyse restent ouverts en [QC-04](questions_decisions.md#qc-04) ; aucun calcul inverse n'est adopté.

Les actions précises découlant de chaque diagnostic et les critères de « déperdition trop importante » restent à expliciter. Une conversion de 100 % a été évoquée par l'utilisateur comme un idéal théorique impossible, pas comme un objectif de résultat. Une baisse de conversion ne prouve pas sa cause. **[Précisions utilisateur et limite d'interprétation]** Source : raw intent, §2 et §12 Q11 ; [QC-03](questions_decisions.md#qc-03), [QC-08](questions_decisions.md#qc-08).

## 2. Utilisateurs, périmètre et usages

| Acteur | Place établie dans le besoin | Limite ou question |
| --- | --- | --- |
| VP Sales et responsables Sales | Pilotage commercial et lecture consolidée ; la maquette prévoit des arbitrages avec la VP Sales. | L’utilisateur tranche pour le case ; échanges avec la VP et les métiers nécessaires dans la vie réelle. [QM-03 résolue](questions_decisions.md#qm-03). |
| Sales : SMB, Large Accounts, Espagne | Utilisateurs directs ; lecture par équipe et globale. | Les dates d’attribution sont proposées par l’utilisateur ; le mapping des responsables vers SMB/LA/ES reste à préciser : [QC-05](questions_decisions.md#qc-05). |
| Marketing | Utilisateur direct selon le cadrage ; vision de l'acquisition et de la conversion dans HubSpot. | Les rapports, filtres et conventions réellement utilisés ne sont pas renseignés : [QC-08](questions_decisions.md#qc-08). |
| Data | Construction et clarification de la réponse analytique selon le case. | Aucun rôle métier additionnel n'est déduit de l'ancienne formulation ambiguë « Equipe Data est au mieux. ». |
| Finance | Interlocuteur cité dans le case, pertinent pour les questions de revenu. | Interlocuteur réel possible ; aucun accord externe requis pour ce case dont l’utilisateur est l’arbitre. |
| Produit et Tech | Causes possibles à investiguer si des frictions apparaissent. | Hors périmètre de réalisation actuel ; aucun incident ni chantier pour ces équipes n'est établi. |

**Provenance :** README §1–3 ; raw intent §1 et Q16 ; [DU-01](questions_decisions.md#du-01), [DU-14](questions_decisions.md#du-14).

L'inventaire conserve les attentes de la maquette, de l'expression de besoin, des objectifs et des précisions utilisateur, même lorsqu'une donnée manque. Depuis les échanges 8–9, l’analyse individu/équipe est souhaitée dans une feuille dédiée, hors synthèse et sous réserve de faisabilité. Cette précision remplace l’exclusion générale antérieure. Les cibles individuelles et classements ne sont pas ajoutés par déduction ; les objectifs fournis restent collectifs. Un rattachement à une société ne commande pas, à lui seul, une vue nominative ou un filtre de dashboard. La place d'un détail de dossier pour comprendre un agrégat reste ouverte. **[Décision utilisateur / inconnue]** Raw intent, lignes 626, 711–716 et 782 ; [QC-08](questions_decisions.md#qc-08).

**[Décision utilisateur, échange 5 point 6]** Conserver les types de besoins et séparer les funnels nouveaux clients (`typeOf=4`) et upsells (`typeOf=7`). Une restitution filtrée par type est proposée. Ne pas généraliser le filtre nouveaux clients du SQL historique ; chaque population de KPI doit être explicite. La formation (`typeOf=2`) reste identifiable ; sa participation aux analyses n’est pas tranchée. [DU-24](questions_decisions.md#du-24), [QC-01](questions_decisions.md#qc-01), [QC-11](questions_decisions.md#qc-11). Cette orientation ne fixe pas encore les tables à construire.

Les contrôles de transmission et la plupart des hypothèses H restent proposés. Le sous-parcours démo et le churn ont désormais une demande utilisateur explicite : leurs parties retenues sont reprises dans U03/U04 et U10/U11, sans valider automatiquement les autres métriques H06/H10.

## 3. Parcours commercial et vocabulaire

### Parcours documentaire

Le [cycle fourni](../../docs/cycle-de-vie.html), étapes 1–10, décrit : formulaire envoyé → contact retrouvé ou créé et demande transmise à Boond → prise en charge et besoin « Lead à traiter » → qualification → découverte → démo → proposition et négociation → issue commerciale → démarrage d'un projet et de lignes d'abonnement. La copie vers HubSpot accompagne la représentation marketing du dossier ; sa position dans le dessin ne prouve pas qu'elle intervient uniquement après la fermeture.

Cette séquence est une **description nominale documentée**, pas un workflow obligatoire. « Signé », « Perdu » et « Abandonné » sont des issues alternatives. Le nurturing est une situation à qualifier, pas automatiquement une perte définitive. Les sauts, retours, réouvertures et anciens états restent en [QM-01](questions_decisions.md#qm-01).

| Terme | Sens à conserver | Ce qui reste ouvert |
| --- | --- | --- |
| Société / entreprise | Entité commerciale à laquelle des dossiers peuvent se rattacher. | Ne pas fusionner plusieurs opportunités indépendantes de la même société. |
| Contact / interlocuteur | Personne en relation avec une société ; distincte du dossier commercial. | Plusieurs contacts ou demandes ne fixent pas un nombre équivalent d'opportunités. |
| Demande / soumission | Manifestation d'intérêt pouvant créer ou mettre à jour un contact. | Événement, identité et rapprochement de chaque demande non complètement définis. |
| Besoin / opportunité Boond / deal dans le vocabulaire Sales | Dossier commercial représenté dans Boond ; les équipes emploient aussi « deal ». | La création de la fiche ne prouve pas une qualification acquise. |
| Deal HubSpot | Représentation commerciale distincte dans HubSpot, documentée comme reflétant un besoin Boond. | Son rapprochement n'est pas une équivalence garantie entre toutes les lignes des systèmes. |
| Entrée pipeline / qualification | Entrée à la création du besoin Boond après formulaire ; qualification commerciale distincte. | Échange 22, DU-28 ; pas filtre obligatoire sur un formulaire retrouvé ni preuve de qualification automatique. |
| Action / séance de démonstration | Séance particulière, distincte des personnes présentes et du besoin concerné. | Preuve de réalisation, reports, annulations et rattachement au bon dossier : [QC-02](questions_decisions.md#qc-02). |
| Phase démo | Partie du parcours d'un besoin pouvant comporter plusieurs actions. | Bornes d'entrée/sortie et relation avec « Show Boond » : QC-02. |
| Projet et ligne d'abonnement | Après la vente, objets Boond portant rattachement client, montant mensuel et période. | Une ligne ou un projet ne prouve ni activité effective ni paiement. |
| Pipeline ouvert, qualifié, pondéré | Populations ou lectures distinctes à nommer selon leur objet. | États inclus, dates et montant de référence ne sont pas interchangeables : QM-01, QM-05, QM-06, QC-04. |

**Provenance :** README §1 ; modèle, descriptions de `raw.opportunities`, `raw.contacts`, `raw.actions`, `raw.projects`, `raw.deliveries`, `hubspot.deals` ; raw intent Q3 et §12 Q12. « Lead » reste ambigu sans unité et étape précisées : ne pas l'utiliser seul comme définition de compteur.

### Ce que Q10 établit, et ce qu'il ne tranche pas

**[Observation enregistrée]** Le diagnostic du 24 octobre 2026 décrit une population de 1 376 besoins non supprimés après sélection de la dernière version par tenant/identifiant, tous types et dates de création. Parmi eux, 1 271 ont « Lead à traiter » comme premier état enregistré. Il appuie l'existence des fiches en amont de la démo. Le jeu est une photographie fournie, pas une mesure opérationnelle au jour du contrôle.

**[Limite]** Parmi 227 besoins actuellement signés dans cette population, 121 n'ont aucun Show Boond enregistré dans l'historique fourni. Cela ne prouve pas qu'aucune démo n'a eu lieu. La première observation peut être tardive et une date CDC n'est pas nécessairement une date métier.

**[Décision utilisateur, échange 22 point 1]** L’entrée du pipeline du cockpit est la création du besoin dans Boond après soumission du formulaire. QM-06 est résolue pour cette frontière ; ne pas appeler toutes ces entrées « qualifiées ». Le récit du formulaire n’établit pas qu’un formulaire existe pour chaque upsell ou canal. La qualification commerciale peut être suivie séparément sans bloquer la génération. Le diagnostic est la réponse documentaire actuelle à Q10 ; l'ancien en-tête du registre raw qui la dit simplement reportée n'est plus l'état complet du sujet. Sources : [diagnostic Q10](../raw_intent/etat_des_lieux_Q10.md), §1, §5 et §8 ; [preuves](../raw_intent/preuves_Q10.json), entrées `queries` Q2/Q3 ; raw intent §13, lignes 823–845.

### Démonstration et upsell : précisions des échanges 5–6

**[Précision utilisateur]** `raw.opportunities.state=24` décrit le statut commercial Show Boond ; `raw.actions` décrit des actions, dont demande, Démo 1 et complémentaire. Deux grains et deux durées sont souhaités : passage d’un dossier dans le statut démo ; délais entre les étapes du sous-parcours d’actions de démo. Un type d’action est un événement à interpréter, pas automatiquement un état avec une durée. La durée d’agenda d’une séance est encore différente. Les codes 25/60/68/17 et volumes 700/533/74/75 sont rapportés par l’utilisateur (échange 5) ; pas recomptés ici. Rattachement, réalisation, chaînage et compteur O04 restent en QC-02.

**[Observation enregistrée, pas règle universelle]** L’[analyse upsell](../raw_intent/analyse_funnel_upsell.md) et ses [preuves](../raw_intent/preuves_upsell.json) décrivent 52 dossiers pour 51 sociétés. Les dossiers progressant vont de 0 à 21 sans états qualification/découverte/Show Boond observés. Au moins une fois : 52 en 0, 47 en 21, 39 en 25, 37 en 26, 27 en 28, 26 en 1, dont 21 en 14. À la dernière version : 26 signés, 15 ouverts, 7 perdus, 3 abandonnés, 1 non qualifié. Les 21 en 14 ne sont pas des signatures supplémentaires ; les différences entre étapes ne sont pas toutes des pertes.

Une signature nouvelle vente antérieure est enregistrée pour toutes les sociétés, sans prouver leur activité à la création de l’upsell. Aucun deal HubSpot non archivé ni projet actuel n’est explicitement relié aux upsells par les liens contrôlés. Cela ne démontre pas l’absence d’expansion : un projet initial peut être modifié. Des actions de démo sur un contact commun ne prouvent pas une démo pour l’upsell. La vente additionnelle signée et son effet sur le MRR actif doivent rester séparés. Les preuves concernent le jeu fourni et n’ont pas été réexécutées. [QC-11](questions_decisions.md#qc-11).

## 4. Règles communes aux fiches du catalogue

<a id="r01-identites"></a>
### R01 — Identités, comptages et cas multiples

- **[Hypothèse utilisateur de travail]** Rapprocher deal HubSpot → besoin/opportunité Boond → société Boond par les identifiants documentés. L'intégrité réelle, les cardinalités, doublons et orphelins ne sont pas validés. Source : raw intent §12 Q12, lignes 754–766 ; modèle lignes 171–185 et 1355–1362 ; [DU-07](questions_decisions.md#du-07).
- **[Distinction retenue]** Compter séparément sociétés, contacts, demandes, dossiers et séances. Plusieurs contacts ne multiplient pas les deals ou leurs montants ; plusieurs séances ne deviennent pas plusieurs opportunités. Chaque fiche précise son unité ; aucune unité universelle n'est imposée au tunnel.
- **[Orientation utilisateur]** Action démo et phase démo restent distinctes. Le lien d'une action à un contact n'autorise pas son attribution à tous les besoins de ce contact. Le diagnostic décrit ce risque, sans fixer de règle d'affectation : Q10 §5 E ; QC-02.
- **[Inconnu]** Traitement des doublons métier, réentrées et renouvellements de dossiers : QC-01, QM-01 et QM-06. Une règle technique de jointure ne tient pas lieu de réponse métier.

<a id="r02-temps"></a>
### R02 — Temps, stocks, flux, durées et cohortes

Un **stock** décrit une situation à une date ; un **flux** décrit des événements ou mouvements sur une période ; une **durée** décrit un temps entre événements ou dans un état. Le nombre de dossiers vus au moins une fois dans un état pendant une période est encore une autre mesure. Ces distinctions sont nécessaires pour lire les demandes sources et l'existant sans les confondre. Source : analyse SQL §4.3 ; raw intent §12 E.

- **[Demande documentée]** Les cohortes sont regroupées par mois de création et suivies à J+30/J+60/J+90, avec effectifs et proportions encore ouverts/gagnés/perdus. Le sens métier de la création et le calcul des horizons restent à préciser ; ne pas substituer silencieusement la démo à la création. Une cohorte non mature n'a pas de résultat observé à l'horizon futur. B02 ; expression de besoin lignes 10 et 15 ; QM-06 et QC-10.
- **[Besoin retenu]** Distinguer ancienneté dans l'étape actuelle, durée d'un passage terminé, cumul des passages après retour et durée totale du cycle. Seuil, pauses, jours calendaires/ouvrés et statistiques ne sont pas choisis. B01, M08, U03 ; raw Q9 ; QC-03.
- **[Pistes utilisateur]** Jour, semaine et mois sont envisagés pour la lecture. **[Fait documentaire]** Les objectifs sont mensuels. Le contrôle des objectifs est fixé à fin de mois par équipe Sales (échange 5 point 7) ; aucune ventilation jour/semaine n’est demandée. QC-06 et QC-09.
- **[Distinction acquise]** Granularité d'analyse, fréquence de recalcul et fraîcheur des sources sont trois sujets séparés. Boond est documenté en flux temps réel ; les contacts HubSpot sont décrits comme copiés chaque nuit. Cela ne prouve pas une fraîcheur quotidienne de toutes les sources. Le snapshot manuel quotidien décrit un dispositif d'attente. Sources : README ligne 38 ; modèle lignes 1185–1187 ; expression de besoin ligne 20 ; QC-06.
- **[Inconnu]** Fuseau métier, instant exact de clôture et fuseau, historique « connu à l'époque » ou corrigé ensuite, dates métier observables de signature et d’activation (statut de signature décidé à l’échange 22) : QC-06, QC-10 et QM-04. La session UTC des preuves Q10 n'est pas une décision de calendrier cible.

<a id="r03-montants"></a>
### R03 — Montants, revenus, objectifs et coefficients

| Mesure | Intention retenue | Statut de définition |
| --- | --- | --- |
| Valeur du pipeline | Montants des dossiers selon la population et la date de chaque analyse. | Unité mensuelle ou contractuelle et référence commerciale ouvertes. |
| MRR actif | Valeur mensuelle récurrente des abonnements actifs en fin de mois, sans prorata journalier. | Source Boond et cadence retenues ; états/bornes ouverts. |
| MRR signé | Valeur mensuelle récurrente engagée commercialement à l’entrée en « Signé — formalités à finaliser » (état 1). | Événement décidé échange 22 ; preuve de date, montant, réouvertures et incrément upsell ouverts. |
| New MRR | MRR supplémentaire actif entre clôtures : composante New (entrants/retours) + composante Upsell (hausses nettes des restants). | Décision utilisateur échange 24, filtre New / Upsell ; pas double ajout d’Expansion. |
| Churn clients | Sociétés actives à fin N−1 et inactives à fin N. | Client actif = au moins un abonnement en cours ; départ-retour intra-mois hors scope du case, échange 22. |
| Churn MRR | MRR perdu par départ complet + baisse d’abonnement chez les clients restants. | Retenu, hors New MRR et expansions upsell ; distinguer les deux composantes. |
| Encaissements mensuels | Sommes réellement reçues. | Exclu du périmètre par l’utilisateur, échange 5 point 4 ; trace U08 conservée. |
| Scénario sans churn ni New MRR | Projection envisagée à partir d'une date N vers la fin du mois. | Proposition utilisateur U09 ; utilité, nom et autres mouvements à préciser. |

**[Décision utilisateur]** Boond fait référence pour le MRR actif, via les lignes d'abonnement reliées aux projets. Préserver la dernière version pertinente de chaque ligne, puis exclure les suppressions ; déterminer l'activité selon période et état ; sommer les montants mensuels HT sans double compte. Les règles historiques, états actifs, chevauchements, remises et bornes ne sont pas déduits de ce principe. Sources : raw intent §10 Q2, lignes 507–525 ; [DU-06](questions_decisions.md#du-06).

**[Distinctions retenues]** Un abonnement actif ne prouve pas un paiement ; un montant de deal HubSpot n'est pas du MRR sans vérifier sa nature mensuelle récurrente. Les encaissements ne désignent ni le solde bancaire ni les seuls paiements du dernier jour. Le chiffre d'affaires reconnu et le prorata de service ne sont pas assimilés aux encaissements ou au MRR. La convention antérieure était ouverte ; l’échange 5 fixe désormais le MRR actif à fin de mois sans prorata journalier. Elle ne décide pas des règles de facturation ou de paiement, hors périmètre. Source : raw intent §10 Q2, lignes 531–551 ; [QM-04](questions_decisions.md#qm-04).

**[Décision utilisateur / fait documentaire]** Les quatre objectifs de `sales_targets` sont mensuels, par équipe et indicateur : MRR signé, pipeline généré, pipeline pondéré, démos. Les cibles monétaires sont en euros, les démos en nombre. Une cible, un réalisé et un coefficient sont des objets distincts. Contrôle à fin de mois par équipe Sales (échange 5 point 7), sans objectif individuel. Source : raw intent §12 Q15 ; modèle lignes 1418–1449 ; O01–O04.

**[Désaccord résolu sur le sens, échange 5 point 5]** Le montant pondéré vise la signature finale depuis l’étape actuelle : `Σ(montant du dossier ouvert × probabilité de signature)`. L’ancienne interprétation « passage suivant » est conservée dans DU-09 comme historique et remplacée par DU-20. L’usage prévu des valeurs fournies, la calibration, la priorité cabinet/Boond, les coefficients des upsells et la convention historique restent ouverts en [QM-05](questions_decisions.md#qm-05). Le résultat conserve la nature du montant initial et n’est pas automatiquement du MRR ni un revenu acquis.

<a id="churn"></a>
#### Churn et réconciliation du portefeuille

**[Décisions utilisateur, échanges 5–6 puis 22 ; DU-19 et DU-31 à DU-34]** Le churn comprend départs complets et baisses chez les clients restants. Pour le case, comparer le MRR total **par société** entre deux clôtures : les hausses/baisses des lignes se compensent à l’intérieur d’une société, jamais entre sociétés. Ce choix affine la règle antérieure de non-compensation. Les réactivations après churn sont incluses dans New MRR, hypothèse du case à confirmer dans la vie réelle. Les départs-retours à l’intérieur du même mois sont hors périmètre d’analyse, sans suppression des versions sources.

<a id="mrr-client-cloture"></a>
**Règle commune de calcul.** `A_N` = ensemble des sociétés ayant au moins un abonnement en cours à fin N ; `m(c,N)` = somme des montants mensuels des lignes actives de la société c à cette clôture. Une société peut être active avec un MRR nul si la gratuité est admise : ne pas remplacer l’activité par `MRR > 0`. États, bornes et gratuités restent en QM-04. Une période non observable n’est pas un montant nul.

- Entrants `E = A_N \ A_N−1` ; sortants `D = A_N−1 \ A_N` ; restants `R = A_N ∩ A_N−1`.
- `MRR actif_N = Σ[c ∈ A_N] m(c,N)`.
- `New MRR [New]_N = Σ[c ∈ E] m(c,N)` : entrants et retours après churn (convention du case), sans seconde barre Réactivation.
- `New MRR [Upsell]_N = Σ[c ∈ R] max(m(c,N) − m(c,N−1), 0)` : hausse nette active des sociétés restées actives ; ancien nom Expansion.
- `New MRR total_N = New MRR [New]_N + New MRR [Upsell]_N`. Le filtre choisit une composante ; sans filtre, sommer les deux. Ne jamais ajouter Upsell/Expansion une deuxième fois au total.
- `Départs MRR_N = Σ[c ∈ D] m(c,N−1)`.
- `Baisses MRR_N = Σ[c ∈ R] max(m(c,N−1) − m(c,N), 0)`.
- `Churn MRR_N = Départs MRR_N + Baisses MRR_N`.
- `Churn clients_N = nombre distinct de sociétés dans D` ; `Clients en baisse_N = nombre distinct de sociétés dans R avec m(c,N) < m(c,N−1)`.

**Déduction de calcul, pas nouvelle décision métier :** à périmètre et unité identiques, sur deux clôtures observables, ces groupes permettent `MRR_N = MRR_N−1 + New MRR total_N − Départs MRR_N − Baisses MRR_N`. Les corrections, écarts de périmètre ou conversions monétaires doivent rester identifiés ; un résidu ne devient pas du churn. Le suivi en nombre peut utiliser `|A_N| = |A_N−1| + |E| − |D|`. Le libellé « nouveaux clients » ne signifie pas encore que les retours doivent être comptés comme premières acquisitions : U13 reste partiellement ouvert.

**Exemple fictif :** +100 € sur une ligne et −40 € sur une autre de la même société donnent +60 € d’expansion nette, 0 € de churn pour cette société. Une perte de 40 € chez une autre société reste un churn de 40 €, même si le portefeuille total augmente. La composante financière Upsell (expansion nette active) ne prouve pas le lien à un dossier commercial d’upsell précis ; une hausse ne doit pas être supprimée faute de lien prouvé. Le champ de filtre est une catégorie analytique dérivée, distincte de raw.opportunities.typeOf. La preuve d’un upsell commercial lié reste QC-11.

Le détail des lignes et des versions est conservé pour permettre des analyses plus fines ultérieures. Le reporting simplifié ne prétend pas montrer tous les événements entre clôtures. Questions réelles : [RAW-E22-01 à 03](../raw_intent/questions_metiers.md#complements-echange-22).

Les montants, ratios et objectifs ne seront comparés qu'après définition de populations, unités et périodes compatibles. La couverture M06 ne reçoit pas automatiquement O01 comme dénominateur ; le MRR potentiel moyen proposé M07 ne devient pas une formule d'ARPU ou de MRR actif. Ces inconnues sont détaillées en QC-04 et QC-09.

<a id="r04-axes"></a>
### R04 — Axes, filtres et agrégations

**[Demande source / orientation utilisateur]** Équipe/global constitue la lecture centrale ; canal/source, segment, étape, issue, période, date d'observation, cohorte et ancienneté complètent les analyses selon chaque fiche. Une dimension pertinente pour une opportunité ne s'applique pas automatiquement au MRR actif. Source : raw intent §12 E, lignes 697–716.

**[Fait documentaire]** Le champ `segment` des référentiels désigne SMB/LA/ES ; cela ne prouve pas son équivalence avec un pôle de société, une tranche d'effectif ou un pays. L'Espagne ne sera pas reconstituée par l'agence sans règle métier. **[Convention de travail utilisateur, échange 5 point 8]** Pipe : équipe à la date observée ; signature : équipe à la signature ; génération : équipe à l’entrée retenue. Mapping responsable/équipe et non-attribués restent en QC-05 ; ne pas appliquer sans justification cette règle aux lignes d’abonnement ou aux actions.

**[Arbitrage métier]** Origine du contact, dernière source et origine du besoin ne sont pas des conventions d'attribution équivalentes. Un canal unique d’acquisition par opportunité, fixé à l’entrée, est proposé par l’utilisateur ; les autres origines sont conservées séparément. Le choix du champ et les conflits restent en QM-02. Inbound est proposé pour les demandes initiées par les prospects via marketing ; sa liste explicite de codes reste à confirmer. Aucun partage de crédit ni rattachement canal du revenu n'est inventé.

**[Limite analytique]** Un nombre distinct peut ne pas être additif entre périodes ou groupes qui se recouvrent ; un stock ne s'additionne pas en flux ; les taux locaux ne se multiplient pas en taux global sans continuité des populations. Les règles finales de consolidation et comparaison restent à définir par mesure. Source : analyse SQL §4.3 ; raw intent lignes 116 et 716.

<a id="r05-histoire"></a>
### R05 — Historique disponible et portée des observations

**[Fait documentaire]** Les tables raw contiennent déjà un historique de versions : `id` revient à chaque version, à identifier avec `meta.customer` ; `meta.ts` date la publication CDC et `meta.deleted` une suppression. Une nouvelle version peut être un changement de montant ou de responsable sans changement d'étape. Les codes d'étape sont des identifiants, pas des rangs. `active` du dictionnaire signifie « encore en cours », pas « qualifié » ou « abonnement actif » ; `isEnabled` indique une disponibilité dans l'interface. Sources : README conventions raw ; modèle lignes 38–41 et 917 ; Q10 §3.

**[Observation limitée]** Les preuves Q10 portent sur le jeu fourni : créations de septembre 2021 à septembre 2026, versions observées de juin 2023 à septembre 2026. Une histoire absente, partielle ou débutant dans un état avancé ne prouve pas l'absence d'un événement réel. Une date de premier passage observé ne sera pas présentée comme date métier certifiée. Sources : Q10 §5 et §9 ; QC-10.

**[Existant distinct de la cible]** Le SQL historique restitue des présences hebdomadaires dans des états et des moyennes de montants sur les jours représentés. Ses signatures ne sont pas un flux de nouvelles signatures ; il ne définit ni MRR, ni conversion, ni pondération cible. Ses filtres de type, états et création depuis 2024 ne sont pas adoptés pour le futur besoin. Le catalogue conserve séparément L01–L04. Source : analyse SQL §4 et §6.

Les observations enregistrées éclairent la faisabilité et les précautions futures. Elles ne résolvent ni la définition de l'opportunité qualifiée ni les conventions commerciales. Aucune base n'a été interrogée dans ce nouveau chat.

<a id="r06-certitude"></a>
### R06 — Certitude, provenance et résolution

Chaque définition importante conserve son origine : **demande/fait documenté**, **décision/précision utilisateur**, **observation enregistrée**, **hypothèse/proposition**, **contradiction/inconnu**. Une décision de cadrage peut être retenue alors que ses détails restent ouverts ; l'origine et l'état de résolution doivent donc être indiqués séparément.

Le registre conserve les décisions, reports et dépendances. Une réponse partielle ne ferme que la partie répondue. Une absence de réponse ou la reprise de l'exécution n'est pas une validation. Les décisions explicites les plus récentes orientent le besoin ; une affirmation factuelle contredite reste visible avec les deux sources. Les observations de données ne sont pas généralisées au-delà de leur population. **Source : instructions du présent chat ; DCI-01 à DCI-08 ; DU-17 à DU-25 pour les échanges 5–6.**

La matrice du catalogue maintient une correspondance explicite avec chaque attente source : reprise, regroupement, proposition non validée, exclusion décidée ou définition ouverte. Un besoin difficile ou sans source disponible reste dans l'inventaire. Les règles et questions communes sont référencées, sans copies divergentes.

<a id="r07-conservation"></a>
### R07 — Conservation et contraintes du case

**[Décision utilisateur]** Conserver cinq ans d'agrégats du data mart pour permettre les comparaisons de saisonnalité. La profondeur réellement disponible et la comparabilité des périodes ne sont pas garanties par cette décision. La rétention du staging et des intermédiaires, les reprises historiques et leur articulation restent ouverts. Raw intent Q1, lignes 243–249 ; [QC-07](questions_decisions.md#qc-07).

**[Hypothèses utilisateur du case]** Traitement supposé autorisé, rôle de responsable du traitement pour la relation commerciale propre, conservation envisagée de trois ans après churn pour les clients et de trois ans pour les leads. Le départ du délai des leads, l’événement de départ de conservation après churn et les finalités et l'articulation avec les agrégats restent à préciser. Aucune conformité juridique n'est vérifiée ; une agrégation n'est pas automatiquement une anonymisation. Raw intent Q7, lignes 292–299 ; DU-11 et QC-07.

Le case prévoit une communication et une organisation de livraison, une maquette, des modèles et l'examen de la requête actuelle. Ces travaux ultérieurs restent distincts de cette phase. La consigne des trois jours est relative à l'accès au dépôt, dont l'heure n'est pas établie ici ; aucune date de livraison n'est inventée. Les sources de l’entreprise restent intactes. À l’échange 22, l’utilisateur autorise uniquement l’ajout de trois questions en annexe de raw_intent/questions_metiers.md ; les autres sources raw restent intactes. Aucun service, installation, benchmark ou modification technique n'est nécessaire à cette consolidation.

<a id="avant-specifications"></a>
## 5. Ce qui manque avant les spécifications correspondantes

La finalité, les utilisateurs et la liste des attentes sont suffisamment établis pour cadrer la préparation des spécifications. Les calculs ci-dessous ne peuvent cependant pas être présentés comme définis tant que leurs règles manquantes ne sont pas arbitrées. Il ne s’agit pas d’un blocage global : les parties indépendantes peuvent avancer. Les décisions suivantes doivent être confirmées, ou rester explicitement signalées comme ouvertes dans les parties correspondantes :

| Définition restant à obtenir | Parties dépendantes |
| --- | --- |
| États/réouvertures, populations par mesure et parcours upsell ; montant à la création | Génération, conversions, cohortes : QM-01, QC-01/QC-11 ; entrée création Boond décidée en QM-06. |
| Chaînage des actions, preuve de tenue des RDV et rattachement aux sociétés pour Nb In demo | U03/U04/O04 : QC-02 ; délais, pauses, seuils : QC-03. |
| États/bornes des abonnements, pauses/gratuités, montant signé et supplément upsell | U05–U07/O01 : QM-04. Signature état 1, fin de mois, sans prorata et New MRR avec retours déjà décidés. |
| Continuité des lignes, corrections, couverture de deux clôtures et compteur de premières acquisitions | QC-12/QC-13 et U13 ; net par société choisi, départ-retour intra-mois hors scope du case. |
| Nature des montants pipeline, MRR potentiel moyen, objectif de couverture ; validité des coefficients | QC-04/QM-05. Sens « signature finale » déjà décidé. |
| Champ canal, codes Inbound, mapping équipes, couverture historique et fraîcheur | QM-02/QC-05/QC-06/QC-10. Dates d’attribution proposées par l’utilisateur. |
| Conservation intermédiaire et détails | QC-07 ; cinq ans d’agrégats déjà décidés. |

L’utilisateur tranche pour le case (QM-03 résolue). Les objectifs se contrôlent à fin de mois par équipe Sales ; la définition des réalisés reste nécessaire mais pas une ventilation quotidienne. Les encaissements exclus n’exigent plus de clarification pour préparer ces spécifications. Les parties indépendantes avancent sans combler artificiellement les inconnues.

## 6. Sources et contrôle de cette version

| Source | Portée et repères |
| --- | --- |
| [README projet](../../README.md) | §1–3 : contexte, divergences, utilisateurs et livrables. Les lignes actuelles sont vérifiées ; certains anciens renvois du raw sont décalés. |
| [Maquette Pipeline](../../docs/besoin/maquette-pipeline.png) | Inspection visuelle : guide, filtres et huit zones. Le statut « standard » ne signifie pas validation métier du chat. |
| [Expression de besoin](../../docs/besoin/expression-de-besoin.md) | Lignes 9–16 : historique, cohortes, pondération ; ligne 20 : dispositif provisoire. |
| [Cycle de vie](../../docs/cycle-de-vie.html) | Étapes 1–10, notamment création avant démo et vie de l'abonnement. |
| [Modèle](../../docs/model/model.json), [interface](../../docs/model/index.html), [documentation et exemples embarqués](../../docs/model/model.js) | Sens documenté des objets et colonnes ; exemples hors ligne distincts des observations en base. |
| [Raw intent](../raw_intent/raw_intent.md) | Q1–Q16 ; §10 et §12 pour les dernières précisions ; §13 pour l'état actuel de Q10. |
| [Questions métier raw](../raw_intent/questions_metiers.md) | QM-01 à QM-06 ; conserver les inconnues sans recopier les anciens statuts devenus incomplets. |
| [Analyse du SQL](../raw_intent/analyse_pipeline_actuel.md), [SQL original](../../legacy/pipeline_actuel.sql) | Sens du reporting existant, limites et questions révélées. Aucune exécution de cette requête dans ce chat. |
| [Diagnostic Q10](../raw_intent/etat_des_lieux_Q10.md), [preuves JSON](../raw_intent/preuves_Q10.json), [SQL de contrôle enregistré](../raw_intent/explore_q10_pipeline_entry.sql) | Résultats antérieurs, méthode, population et limites ; contrôles non relancés. |
| [Hypothèses structurées](../raw_intent/cycle_hypotheses/hypotheses-source.json), [trace éditoriale](../raw_intent/cycle_hypotheses/trace-creation.md) | H01–H10 ; questions et mesures ajoutées avec assistance IA, non validées par leur seule présence. |
| [Support global HTML](../raw_intent/cycle_hypotheses/01-parcours-et-frictions.html), [détaillé HTML](../raw_intent/cycle_hypotheses/02-tunnels-par-etape.html), [PDF global](../raw_intent/cycle_hypotheses/01-parcours-et-frictions.pdf), [PDF détaillé](../raw_intent/cycle_hypotheses/02-tunnels-par-etape.pdf) | Sources HTML lues et PDF inspectés visuellement (1 + 10 pages). Largeurs schématiques, branches, compléments facultatifs et contrôles transversaux ne sont pas des mesures. |
| [Analyse upsell](../raw_intent/analyse_funnel_upsell.md), [preuves](../raw_intent/preuves_upsell.json) | §1–7 et Q1–Q6 : observation de 52 upsells, parcours, liens et limites ; contrôles non relancés. |
| [Journal actuel](ia_assistant_story.md) | Échanges 5–6 : nouvelles décisions, propositions d’attribution et définition du churn. |
| [Ancien historique](../ia_assistant_story.md) | Consultation ciblée des messages d'origine pour vérifier la provenance des décisions. Il n'est pas recopié dans le nouveau journal. |

Toutes les sources expressément demandées ont été trouvées. Aucun `AGENTS.md` applicable n'a été trouvé dans les parents examinés ou le dépôt. Les modifications préexistantes du dépôt sont préservées. Les contrôles de couverture, de cohérence et de liens de cette version sont documentaires ; ils ne certifient ni calcul métier ni disponibilité opérationnelle.

**Échanges 8–10 :** [maquette v2](maquettes/dashboard_synthese_v2.png), [note de lecture](maquettes/dashboard_synthese_v2.md) et [table des champs et correspondances ClickHouse](correspondance_champs_clickhouse.md). La première architecture produite à l’échange 9 est retirée à l’échange 10. La synthèse est acceptée comme base V1, mais le modèle doit préserver le grain utile disponible des versions, passages, actions, responsables/canaux et mouvements d’abonnement. Les règles et la faisabilité restent qualifiées. [DU-26/27](questions_decisions.md#du-26), [QC-14](questions_decisions.md#qc-14).

**Préparation du staging — échange 11 :** la [table des correspondances](correspondance_champs_clickhouse.md) décompose chaque champ calculé, partiel ou ouvert en entrées sources et paramètres. L’[inventaire des sources du staging](inventaire_sources_staging.md) déduplique les colonnes physiques par table ; champs JSON, clés, versions et sources candidates sont explicités. Aucune règle métier ouverte n’est résolue par cette seule cartographie.

**Construction des données — échange 12.** Nous pouvons historiser les sources qui ne le sont pas, ajouter les métadonnées d’import, construire les référentiels techniques utiles (date/country) et produire les champs dérivés/KPI par transformations et croisements entre staging, intermédiaire et mart. L’absence d’une colonne KPI ou d’un calendrier source n’est pas un blocage. Les dates d’import restent distinctes des dates métier ; l’historique créé ne reconstitue pas un passé jamais capturé. Les règles métier et preuves manquantes restent signalées. [Décision DCI-12](questions_decisions.md#dci-12) · [Travail à notre charge](inventaire_sources_staging.md#constructions-techniques).

**Préservation des versions — échange 13 :** le [cadre incrémental CDC](inventaire_sources_staging.md#incremental-cdc) consigne les principes utilisateur de chargement complet puis reprise avec recouvrement, déduplication et conservation des suppressions. La méthode par table et ses tests restent à valider ; les définitions des KPI restent inchangées. [DCI-13](questions_decisions.md#dci-13).
