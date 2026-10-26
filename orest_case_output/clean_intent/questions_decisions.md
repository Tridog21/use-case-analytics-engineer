# Questions et décisions — référence détaillée

**État actuel — échange 24 :** New MRR = New + Upsell, avec filtre dédié ; clarification de l’échange 23 résolue. Les questions de pratique réelle conservées en raw ne bloquent pas ce choix du case. [DU-38](#du-38).

La [version humaine](intent.md#avant-specifications) explique simplement les manques avant les spécifications. Le présent registre en conserve le détail et la provenance pour l’IA et les relecteurs qui souhaitent approfondir. Il accompagne l'[intent détaillé](intent_ia.md) et le [catalogue des indicateurs](catalogue_indicateurs_ia.md). Il décrit l'état actuel des décisions, les désaccords à préserver et ce qui manque pour définir les mesures. L'[historique de ce nouveau chat](ia_assistant_story.md) conserve les messages utilisateur ; les messages de l'ancien chat ne sont pas recopiés ici.

**État après les échanges 5 à 13 :** utilisateur arbitre du case ; objectifs à fin de mois par équipe ; MRR actif à fin de mois sans prorata journalier ; signature finale comme sens de la pondération ; encaissements exclus ; churn clients et churn MRR retenus, ce dernier incluant les baisses d’abonnement mais excluant New MRR et upsells. Les populations nouveaux clients/upsells et les deux grains de démo sont distingués. Les questions restantes portent uniquement sur les détails encore non décidés. La synthèse v2 est la base souhaitée du dashboard V1 ; modèle détaillé et analyse individuelle dédiée demandés. La première architecture est retirée à l’échange 10 ; travail repris par inventaire des champs et correspondances sources, puis décomposition des calculs et regroupement par table pour préparer le staging à l’échange 11. L’échange 12 confirme notre latitude pour historiser, produire les métadonnées, calculer les indicateurs et créer les référentiels techniques utiles. Aucun métier n’a été contacté.

## 1. Lecture du registre et provenance

La **nature de la preuve** et l'**état de résolution** sont deux informations distinctes, selon la [règle R06](intent_ia.md#r06-certitude). Une demande explicitement documentée peut avoir une définition ouverte ; une hypothèse utilisateur peut être retenue pour poursuivre sans devenir un fait vérifié.

| Axe | Valeurs utilisées | Sens |
| --- | --- | --- |
| Provenance / certitude | Document source ; décision ou précision utilisateur ; observation enregistrée ; hypothèse ou proposition ; contradiction ; information inconnue | Indique pourquoi l'information est présente et ce qu'elle permet d'affirmer. |
| Résolution | Retenu ; partiellement défini ; ouvert ; à confirmer par le métier ; reporté explicitement ; remplacé par une précision ultérieure | Décrit ce qui reste à décider. Une absence de réponse ne vaut ni validation ni report explicite. |
| Responsable de réponse | Utilisateur ; métiers ; utilisateur puis confirmation métier | Distingue l'orientation du case que l'utilisateur peut préciser et une pratique réelle qui exige une confirmation. Pour le case, l’utilisateur tranche toutes les conventions (DU-17). Les interlocuteurs métier mentionnés sont des interlocuteurs réels à consulter hors exercice, pas une approbation requise ici. |

Les identifiants **QM-01 à QM-06** sont conservés du raw intent. **QC-01 à QC-14** rendent visibles les autres définitions ouvertes déjà présentes dans les sources, sans dupliquer les arbitrages QM. Les identifiants M, B, O, U, H et L renvoient au catalogue ; H garde ses propositions d’origine ; les éléments démo/churn explicitement retenus depuis sont rapprochés de U03/U04/U10/U11. L décrit seulement l’existant.

### Sources utilisées

| Repère | Source et usage |
| --- | --- |
| R | [Raw intent](../raw_intent/raw_intent.md), notamment §8 à §13 : décisions successives, catalogue et dernier statut Q10. Les sections ultérieures peuvent remplacer un statut antérieur explicitement. |
| J | [Ancien journal](../ia_assistant_story.md), messages utilisateur des tours 4, 9, 13, 14 et 15 : vérification de provenance, sans reprise de leurs messages dans le nouveau journal. |
| QM | [Questions métier raw](../raw_intent/questions_metiers.md) : origine de QM-01 à QM-06 et questions transmises à la restitution. |
| Q10 | [Diagnostic Q10](../raw_intent/etat_des_lieux_Q10.md) et [preuves enregistrées](../raw_intent/preuves_Q10.json) : observations limitées à leur population et à leur historique disponible. |
| SQL | [Analyse du SQL historique](../raw_intent/analyse_pipeline_actuel.md) et [requête source](../../legacy/pipeline_actuel.sql) : fonctionnement existant, jamais définition cible par défaut. |
| E | [Expression de besoin](../../docs/besoin/expression-de-besoin.md), L9–20 : ancienneté, cohortes, historique du pipeline pondéré et dispositif d'attente. |
| M | [Maquette Pipeline](../../docs/besoin/maquette-pipeline.png), guide supérieur et zones 1 à 8 : demandes et questions du cabinet. |
| C | [Cycle de vie](../../docs/cycle-de-vie.html), L91–121 : parcours décrit et circulation des objets. |
| D | [Modèle documentaire](../../docs/model/model.json) et [exemples embarqués](../../docs/model/model.js) : sens déclaré des champs et observations du corpus ; ils ne remplacent pas une règle métier. |
| N | [Journal du nouveau chat](ia_assistant_story.md) : prompt initial, échanges 1–6 ; échanges 5 et 6 pour les nouveaux arbitrages. |
| UP | [Analyse upsell](../raw_intent/analyse_funnel_upsell.md), §1–7, et [preuves](../raw_intent/preuves_upsell.json), Q1–Q6 et contrôles : résultats enregistrés, non réexécutés. |

Les références de lignes concernent les fichiers lus pour cette consolidation. Le README actuel a un décalage de quatre lignes par rapport à plusieurs références du raw intent ; les repères vérifiés figurent dans le registre des désaccords ci-dessous.

## 2. Décisions et précisions conservées

### 2.1. Instructions de consolidation de ce chat

Ces décisions **DCI** organisent le travail documentaire. Elles ne créent pas de définition commerciale supplémentaire.

<a id="dci-01"></a>
**DCI-01 — Quatre documents et travail par itérations.** Créer `intent.md`, `catalogue_indicateurs.md`, `questions_decisions.md` et `ia_assistant_story.md`, reliés entre eux. La première version est substantielle et révisable. **Provenance :** instruction utilisateur, N, prompt initial §1 et §4. **État :** principe des rôles documentaires conservé ; organisation en deux versions actualisée par DCI-07.

<a id="dci-02"></a>
**DCI-02 — Exhaustivité avant faisabilité et sélection de livraison.** Conserver chaque attente, même sans données permettant de la mesurer. Identifier les regroupements et le statut courant des demandes individuelles. La consigne initiale différait la sélection d’une V1, l’architecture et les spécifications d’implémentation. **Provenance :** instruction utilisateur, N §1, §6 et §10 ; déjà exprimée dans J tour 14, L481. **État :** exhaustivité conservée ; base visuelle V1 retenue par DU-27. Proposition d’architecture autorisée à l’échange 9 puis retirée à l’échange 10 ; inventaire des champs en cours selon DCI-10. Les détails d’implémentation restent à spécifier.

<a id="dci-03"></a>
**DCI-03 — Provenance explicite et inconnues visibles.** Distinguer demandes, décisions utilisateur, observations, propositions et contradictions. Une hypothèse, une suggestion IA, une absence de trace ou le SQL historique ne deviennent pas une règle validée. Les dernières décisions orientent le besoin sans effacer un désaccord factuel. **Provenance :** instruction utilisateur, N §5–7. **État :** retenu ; règle commune [R06](intent_ia.md#r06-certitude).

<a id="dci-04"></a>
**DCI-04 — Préservation des sources et périmètre documentaire.** Conserver `raw_intent` et les sources de l'entreprise intacts. Aucun modèle, SQL, jeu de données ou service n'est modifié pour combler une définition manquante ; aucune installation, requête sur une base ou mesure de performance n'est demandée à cette étape. **Provenance :** instruction utilisateur, N §2–3 et §10. **État :** retenu.

<a id="dci-05"></a>
**DCI-05 — Journal propre au nouveau chat.** Conserver intégralement les messages utilisateur accessibles de ce chat, y compris le prompt initial ; résumer brièvement les réponses IA, numéroter les échanges et distinguer décisions, reports et documents modifiés. Consigner rétroactivement les échanges du mode Plan après passage effectif en exécution. Ne recopier ni l'ancien historique ni un raisonnement interne. **Provenance :** instruction utilisateur, N §3 et §9. **État :** retenu.

<a id="dci-06"></a>
**DCI-06 — Reprise de la rédaction sans réponse implicite aux questions.** La demande de reprendre l'exécution porte sur la poursuite du travail. Les questions de population, qualification et démonstration restent sans réponse ; les parties indépendantes avancent. **Provenance :** message utilisateur de reprise dans N, rapproché du prompt initial §8. **État :** retenu pour la méthode ; aucune nouvelle décision métier.

<a id="dci-07"></a>
**DCI-07 — Deux versions pour deux usages.** La version humaine devient le point d'entrée `intent.md` : langage technique simple, lecture aérée, objectif final « point B » et section séparée sur les manques avant les spécifications. La version IA comprend `intent_ia.md`, le catalogue détaillé et ce registre ; elle conserve exhaustivité, règles, sources, IDs, statuts et dépendances. Le journal reste commun. La simplification change la présentation, pas les décisions métier. Toute nouvelle précision doit être répercutée dans les deux versions. **Provenance :** nouvelle demande utilisateur, N, échange 4. **État :** retenu ; remplace la contrainte initiale de quatre fichiers par cinq fichiers nécessaires aux deux usages ; étendue au catalogue par DCI-08.

<a id="dci-08"></a>
**DCI-08 — Deux catalogues complémentaires.** `catalogue_indicateurs.md` devient la lecture humaine : définition simple, grain, formule lorsqu’elle est établie, question si elle ne l’est pas. `catalogue_indicateurs_ia.md` conserve la couverture exhaustive, les champs détaillés, les sources et les références aux tables documentées. Les deux intents, les deux catalogues, le registre et le journal forment six fichiers synchronisés. **Provenance :** N échange 5, demande finale. **État :** retenu ; ne crée pas de règle de calcul manquante.

<a id="dci-09"></a>
**DCI-09 — Première architecture désormais demandée.** L’échange 9 accepte la maquette v2 comme base du dashboard V1 et demande une première idée d’architecture fondée sur le besoin et les données. Cette demande remplace le report de toute architecture de DCI-02. Elle n’autorise pas à inventer les règles manquantes ni à prétendre les modèles déjà construits. Sources conservées, aucune requête en base/installation nécessaire à cette proposition. **État :** autorisation historique ; proposition retirée à l’échange 10, démarche remplacée par DCI-10.

<a id="dci-10"></a>
**DCI-10 — Repartir des champs nécessaires et de leurs correspondances.** À l’échange 10, l’utilisateur demande de retirer la première architecture et de construire une table à trois colonnes : tous les champs théoriques utiles au périmètre, leurs équivalents dans le modèle ClickHouse (plusieurs si nécessaire), puis les tables sources. **État à l’échange 10 :** démarche retenue ; aucune architecture de remplacement alors demandée. L’échange 15 autorise ensuite la nouvelle proposition DCI-14. Champs présents, calculs et manques distingués ; les tables ref indispensables sont signalées en complément de raw/hubspot. Source de travail : [table de correspondance](correspondance_champs_clickhouse.md). Les définitions métier antérieures, dont la granularité fine souhaitée, restent valables.

<a id="dci-11"></a>
**DCI-11 — Décomposer les champs et préparer le regroupement pour le staging.** Échange 11 : l’utilisateur demande d’ajouter une colonne aux champs à calculer/à définir pour lister leurs sous-champs nécessaires, puis relier ces entrées aux vrais champs et tables. La finalité est un regroupement complet des tables/colonnes utiles au staging. **État :** réalisé comme inventaire documentaire, sans création de modèles. La décomposition couvre aussi les champs partiels et sources à choisir ; elle sépare colonnes physiques, propriétés JSON, résultats calculés et paramètres/règles absents. Les sources alternatives et hypothèses optionnelles restent qualifiées. **Supports :** [table de décomposition](correspondance_champs_clickhouse.md), [regroupement staging](inventaire_sources_staging.md). Cette décision étend DCI-10 ; elle ne valide aucune règle métier encore ouverte ni la rétention des versions.

<a id="dci-12"></a>
**DCI-12 — Construire l’historique, les champs calculés et les référentiels techniques nécessaires.** Échange 12 : l’utilisateur précise que certaines tables doivent être historisées par nos traitements, éventuellement via incrémental et timestamp d’import ; les KPI sont à produire par transformations/croisements dans staging, intermédiaire/mart ; les tables techniques date/country peuvent être créées de zéro selon les besoins. **État : latitude technique retenue.** Le choix détaillé de méthode et de couche reste à concevoir ; aucun modèle n’est implémenté par cette précision. Une colonne absente mais calculable ou générable ne constitue pas une attente de donnée CRM. Les versions antérieures doivent être conservées pour que le traitement historise réellement. Le timestamp d’import ne remplace pas une date métier et ne reconstitue pas le passé non capturé. Conventions métier, preuves manquantes et rétention détaillée restent ouvertes. T05/T08/T09 et l’inventaire staging sont actualisés en conséquence.

<a id="dci-13"></a>
**DCI-13 — Principes incrémentaux pour conserver les versions CDC raw.** Échange 13 : chargement initial de tout l’historique ; reprise depuis le maximum `meta.ts` cible moins une fenêtre paramétrable, prédicat inclusif `>=`, déduplication des versions et conservation des suppressions. Clé candidate tenant/id/timestamp à vérifier et adapter aux dictionnaires ; lecture courante séparée, dernière version avant exclusion des supprimés. Pas de filtre « hier » ni d’égalité de jour updateDate/meta.ts. Borne calculée une fois et comparaison à une constante typée ; performances à vérifier sans présumer un bénéfice de Jinja. **État : cadre de référence utilisateur retenu, implémentation non effectuée.** Deux jours est un exemple non validé. Choix des modèles réellement incrémentaux, compatibilité dbt-clickhouse, clés/conflits, cible vide, retards hors fenêtre, réconciliation et reprise après échec restent à vérifier. Le maximum de cible n’est pas un journal des exécutions réussies. [Principes et contrôles complets](inventaire_sources_staging.md#incremental-cdc). Aucun benchmark ou test de données n’a été exécuté dans cette itération.

<a id="dci-14"></a>
**DCI-14 — Liste humaine approuvée et nouvelle proposition de modèle.** Échange 15 : l’utilisateur approuve la présentation des KPI de l’échange 14 et demande de la sauvegarder comme [liste humaine](liste_kpi_humaine.md). Il demande ensuite de préparer les KPI dans la couche intermédiaire, de proposer les faits/dimensions à sa sortie et de générer un visuel de leurs tables et contenus, en partant du staging déjà recensé. **Périmètre : intermédiaire, faits et dimensions ; aucun DTR à concevoir maintenant. État : demande exécutée sous forme de proposition logique, non implémentée et non encore approuvée.** La nouvelle [proposition](architecture_modele_proposition.md) conserve les grains fins, les contributions recalculables et les règles ouvertes. Elle ne restaure pas l’architecture retirée de l’échange 9. L’approbation de la liste ne résout pas ADV/BP, les cas de mouvements MRR ou les autres définitions explicitement ouvertes.

<a id="dci-15"></a>
**DCI-15 — Vue statique d’ensemble et clarification du sigle ADV.** Échange 16 : l’utilisateur juge la présentation interactive illisible et demande une image statique permettant de voir toute l’architecture d’un coup d’œil. Une vue par couches et domaines est produite, avec noms raccourcis et relations regroupées, sans changement implicite des grains détaillés. La présentation interactive précédente n’est plus la vue de revue recommandée ; les sources et la proposition documentaire restent conservées. L’utilisateur indique « ADV c’est L’Administration des Ventes je crois » et estime que ce n’est pas un KPI. **Statut :** interprétation utilisateur tentative du sigle, classement d’ADV comme KPI supprimé ; désaccord documentaire conservé avec la zone 7 de la maquette, qui décrit séparément un MRR potentiel moyen par deal. M07 reste une proposition source à définir, pas une nouvelle mesure validée. [Vue statique](maquettes/architecture_vue_ensemble_v1.png).

<a id="dci-16"></a>
**DCI-16 — Pipeline générique, extension démo et deux modules partageant leurs dimensions.** Échange 18 : l’utilisateur propose d’intégrer la démonstration au pipeline, car les mêmes analyses s’appliquent aux autres étapes ; son micro-funnel peut rester dans une table distincte. Il demande de prendre en compte deux micro-marts parcours/traitement et MRR/churn/performance, avec dimensions partagées, et un visuel statique clair. **Orientation utilisateur retenue dans la proposition :** mutualiser les faits d’étape et rendre les frontières de modules explicites. **Choix de conception IA à discuter :** ensemble nommé « Data mart commercial & revenu », module Pipeline (cinq faits génériques + extension démo) et module Revenus/performance (deux faits d’abonnement + un fait d’objectifs), sans troisième copie centrale ni base supplémentaire imposée. Le MRR signé reste produit dans l’événement commercial ; les comparaisons mensuelles consomment ces sorties publiées. MRR actif/churn restent alimentés directement par les abonnements. Une nouvelle étape standard complète référentiels et règles sans nouvelle table ; un grain spécifique peut justifier une extension. La modularité ne vaut ni preuve de fiabilité ni validation de définition métier. [Architecture actuelle](architecture_modele_proposition.md#architecture-modulaire).

<a id="dci-17"></a>
**DCI-17 — Toute la chaîne historisée et deux vues détaillées par module.** Échange 19 : l’utilisateur précise que l’historisation concerne tout le modèle, et pas seulement le staging. Il demande deux visualisations statiques du même style, une par module, montrant clairement les KPI/informations calculés et leur granularité, avec davantage de place et une bonne lisibilité. **Exigence retenue :** histoire disponible dans staging, intermédiaires, faits, dimensions et liaisons ; pas de réduction généralisée au dernier état. **Distinction de conception :** grain métier et grain de version ne sont pas confondus ; les clés physiques et les modalités de conservation/reproduction restent à définir. Les versions ne sont pas des unités supplémentaires à sommer. Les règles de révision, la vue corrigée ou connue à une date et la rétention détaillée restent ouvertes ; les cinq ans d’agrégats ne sont pas étendus sans décision à tout le détail. [Règle commune](architecture_modele_proposition.md#historisation-toutes-couches), [vues détaillées](architecture_modele_proposition.md#vues-detaillees-modules).

### 2.2. Orientations héritées : provenance et état actuel

Les décisions **DU** ci-dessous ne sont pas toutes des règles opérationnelles résolues. Leur nature et leur limite sont indiquées séparément.

<a id="du-01"></a>
**DU-01 — Utilisateurs et périmètre humain.** Sales et Marketing sont les utilisateurs directs ; Sales comprend SMB, Large Accounts et Espagne. Produit et Tech peuvent contribuer à l'explication d'une friction mais restent hors périmètre de réalisation. Finance est un interlocuteur possible de définition financière, pas un utilisateur direct ajouté sans décision. Le rôle complémentaire attendu de Data reste ouvert en [QC-08](#qc-08). **Provenance :** précision utilisateur, J L161–164 ; fait documentaire, README L36 et L71 ; R §1. **État :** orientation retenue.

<a id="du-02"></a>
**DU-02 — Orientation initiale stratégique, par équipe et globale.** L’exclusion initiale de l’individuel est remplacée par DU-26 aux échanges 8–9 : feuille dédiée individu/équipe souhaitée, hors synthèse. Les demandes individuelles de la maquette restent tracées, sans objectif individuel ni classement de commerciaux ajouté. Un éventuel accès explicatif à un dossier est une autre question, suivie en [QC-08](#qc-08). **Provenance :** décision utilisateur, J tour 14 L485–486 ; R §12 Q15, L782–784. **État :** retenu.

<a id="du-03"></a>
**DU-03 — Finalité : pertes de conversion, cycle de vie et durées.** Le cockpit doit aider à localiser les pertes trop importantes, comprendre les étapes et issues d'un dossier, analyser les durées et suivre les attentes historiques/cohortes de l'expression de besoin. « Trop important » n'a pas encore de seuil ou référence validé ; aucune cause n'est prouvée par une baisse de conversion. **Provenance :** précision utilisateur, J L490 ; R §12 Q11, L786–794. **État :** besoin retenu, définitions ouvertes en [QC-03](#qc-03), [QM-01](#qm-01), [QM-06](#qm-06) et [QC-10](#qc-10).

<a id="du-04"></a>
**DU-04 — Action de démo et phase démo distinctes.** Une séance est une action ; la phase commerciale d'un besoin peut contenir plusieurs séances. Ni nombre obligatoire ni ordre fixe de séances ne sont décidés. **Provenance :** précision utilisateur, J L288 ; R §8 Q3, L259–265. **État :** distinction retenue, règles opérationnelles ouvertes en [QC-02](#qc-02).

**Actualisation échanges 5–6 :** Complétée par DU-21 : phase opportunité et sous-parcours d’actions, avec deux familles de durées.

<a id="du-05"></a>
**DU-05 — Quatre besoins financiers distincts.** Conserver MRR actif à une date, MRR signé, New MRR du mois et suivi des sommes réellement encaissées pendant le mois. Le libellé utilisateur « MRR encaissé (ou chiffre d'affaire) » ne prouve pas l'équivalence de ces notions. La clôture sert à observer le flux du mois ; elle ne limite pas le comptage aux paiements du dernier jour. **Provenance :** précision utilisateur, J L443 ; R §10 Q2, L494–503 et L533–549. **État actuel :** MRR actif/signé/New MRR conservés ; encaissements remplacés par une exclusion DU-18. Conventions restantes en [QM-04](#qm-04).

**Actualisation échanges 5–6 :** Remplacée pour le périmètre actuel par DU-18/DU-19 : U08 exclu par décision, churn ajouté, New MRR maintenu.

<a id="du-06"></a>
**DU-06 — Boond est la référence du MRR des abonnements actifs.** Partir des lignes d'abonnement reliées aux projets ; retenir la version pertinente puis exclure les suppressions ; identifier l'activité à la date observée ; additionner les montants mensuels HT sans compter plusieurs fois le même abonnement. Les états actifs, bornes, chevauchements et interprétation historique restent à confirmer. Une ligne d'abonnement n'est pas une preuve d'encaissement. **Provenance :** décision et principes utilisateur, J L443–457 ; R §10, L505–525. **État :** choix de source retenu, définition partielle ; [QM-04](#qm-04), [QC-10](#qc-10), règles [R03](intent_ia.md#r03-montants) et [R05](intent_ia.md#r05-histoire).

<a id="du-07"></a>
**DU-07 — Rattachement des dossiers à la société.** Chaîne de travail : deal HubSpot → besoin/opportunité Boond → société Boond, indépendamment du nombre d'interlocuteurs. Plusieurs opportunités d'une société restent distinctes. Les relations documentées ne prouvent pas la complétude, l'unicité ou l'intégrité de tous les liens. **Provenance :** hypothèse utilisateur explicitement retenue pour poursuivre, J L483 ; R §12 Q12, L752–766 ; relations documentées D L171–178 et L1355–1362. **État :** hypothèse de travail, intégrité à vérifier ultérieurement ; règle [R01](intent_ia.md#r01-identites).

<a id="du-08"></a>
**DU-08 — Objectifs mensuels distincts des probabilités.** Les quatre cibles `mrr_signed`, `pipeline_generated`, `pipeline_weighted`, `demos` sont mensuelles par équipe et indicateur. Elles ne sont pas des probabilités ; aucun lien direct automatique ne les remplace l'une par l'autre. **Provenance :** précision utilisateur J L485 ; D L1418–1449 ; R §12 Q15, L768–780. **État :** séparation retenue ; formules des réalisés et comparaisons en [QC-09](#qc-09).

**Actualisation échanges 5–6 :** Complétée par DU-22 : contrôle à fin de mois par équipe Sales, pas de ventilation journalière à définir.

<a id="du-09"></a>
**DU-09 — Ancienne interprétation des probabilités, remplacée.** L'utilisateur les interprète comme un passage à l'étape suivante ; le modèle les décrit comme une probabilité de signature depuis un stade. Les deux formulations sont conservées ; aucune des valeurs proposées n'est présumée calibrée. **Provenance :** interprétation utilisateur J L485 confrontée à D L1457–1487 ; R L774–784. **État actuel :** sens remplacé par DU-20, signature finale retenue ; calibration/source encore en [QM-05](#qm-05).

**Actualisation échanges 5–6 :** Désaccord de sens résolu par DU-20 ; seule la validité et la source des coefficients restent ouvertes.

<a id="du-10"></a>
**DU-10 — Conservation de cinq ans des agrégats du data mart.** Cette profondeur est retenue par l'utilisateur pour plusieurs saisonnalités, avec une prudence de comparaison liée à l'évolution du produit. Elle ne prouve pas cinq ans d'historique actuellement disponibles et ne fixe pas la rétention des données détaillées. **Provenance :** décision utilisateur J L286 ; R §8 Q1, L243–249. **État :** retenu ; articulation détaillée en [QC-07](#qc-07).

<a id="du-11"></a>
**DU-11 — Hypothèses de traitement et de rétention détaillée.** L'utilisateur suppose, pour le case, un traitement autorisé et le rôle de responsable du traitement pour la relation commerciale propre ; il suggère trois ans après churn pour les clients et trois ans pour les leads. Le point de départ des leads reste inconnu ; le churn analytique est maintenant défini par DU-19, sans fixer le départ d’un délai de conservation. **Provenance :** hypothèses utilisateur J L292 ; R §8 Q7, L292–299. **État :** hypothèses, aucune conformité juridique vérifiée ; [QC-07](#qc-07).

**Actualisation échanges 5–6 :** La définition analytique du churn est désormais fixée par DU-19 ; son éventuel usage comme départ d’une durée de conservation reste distinct et ouvert.

<a id="du-12"></a>
**DU-12 — Jour, semaine et mois comme lectures à préciser.** L'utilisateur envisage ces trois périodes. Sa compréhension d'une mise à jour quotidienne n'établit pas une fraîcheur identique de toutes les sources. **Provenance :** précision utilisateur J L293 ; R §8 Q8, L301–307. **État :** pistes de lecture retenues, calendrier et disponibilité ouverts en [QC-06](#qc-06) ; règle [R02](intent_ia.md#r02-temps).

<a id="du-13"></a>
**DU-13 — Compréhension Sales/Marketing suffisante pour poursuivre.** Les Sales suivent leurs dossiers dans Boond et le Marketing en retrouve une représentation dans HubSpot. Le désalignement potentiel est conservé sans amplitude mesurée ; les rapports effectivement utilisés restent inconnus. **Provenance :** confirmation utilisateur J L465 ; R §10 Q5, L553–561. **État :** clarification générale acquise, sans rouvrir la même question ; détails en [QC-08](#qc-08).

<a id="du-14"></a>
**DU-14 — Définitions de préférence synchronisées entre équipes.** L'utilisateur souhaite l'alignement et confie au métier la désignation de l'arbitre en cas de conflit. **Provenance :** précision utilisateur J L301 ; R §8 Q16, L368–375. **État actuel :** intention d’alignement conservée ; DU-17 résout [QM-03](#qm-03) pour le case, utilisateur arbitre.

<a id="du-15"></a>
**DU-15 — Q10 dispose d'une réponse documentaire, sans frontière qualifiée validée.** Le diagnostic enregistré a été accepté pour répondre à Q10 et clôturer le raw intent. Son résultat ne ferme pas QM-06. **Provenance :** instruction utilisateur J tour 15 L502–516 ; R §13 L819–845. **État :** diagnostic accepté comme base, définition métier ouverte en [QM-06](#qm-06).

<a id="du-16"></a>
**DU-16 — Scénario sans churn et sans New MRR.** L'idée d'un revenu attendu en fin de mois à partir d'une date N reste une option à préciser : utilité, nom, autres mouvements et nature du résultat sont inconnus. Ce n'est ni un cinquième KPI obligatoire ni un paiement garanti. **Provenance :** idée utilisateur J L443 ; R §10 L541, §12 U09 L689. **État :** proposition utilisateur ouverte en [QM-04](#qm-04).

### 2.3. Arbitrages des échanges 5 et 6

<a id="du-17"></a>
**DU-17 — Autorité de décision.** L’utilisateur tranche les définitions et hypothèses de ce case. Dans une situation réelle, il faudrait échanger avec la VP Sales et les métiers. **Provenance :** N échange 5, point 2. **État :** retenu ; QM-03 résolue pour l’exercice, aucune validation externe exigée ici.

<a id="du-18"></a>
**DU-18 — Revenus et calendrier.** Conserver MRR actif, MRR signé, New MRR et churn ; sortir les encaissements U08 du périmètre par choix métier, tout en conservant la demande initiale. MRR calculé à chaque fin de mois, sans prorata journalier. Le stock actif est une photo de clôture ; le signé et les mouvements restent des valeurs du mois arrêtées à cette clôture, non des stocks à additionner. **Provenance :** N échange 5, points 0 et 4. **État :** retenu ; états actifs, événement de signature et périmètre des entrées restent en QM-04. New MRR était déjà dans U07 ; il est confirmé et non dupliqué.

<a id="du-19"></a>
**DU-19 — Churn clients et churn MRR.** Convention du case, pas définition officielle Boond : clients actifs qui ne renouvellent pas ou cessent leur abonnement pendant le mois. U10 compte les clients perdus ; U11 mesure le MRR perdu. L’échange 6 précise que **U11 inclut aussi les baisses d’abonnement chez les clients restants**, et exclut les apports New MRR et upsell. Décomposer U11 en MRR perdu par départ complet et MRR perdu par baisse permet de distinguer fuite de clients et réduction de leurs abonnements. La différence de stocks corrigée des seuls nouveaux entrants, proposée initialement, est donc insuffisante dès qu’il existe des expansions ; elle est remplacée par la décomposition en mouvements. **Provenance :** N échange 5 point 0 puis réponse intégrale échange 6. **État :** concept et décomposition retenus ; réactivations, mouvements multiples et grain de compensation encore ouverts en QC-12. Aucun taux de churn supplémentaire demandé.

<a id="du-20"></a>
**DU-20 — Probabilité de signature finale.** Pour M04/B03, multiplier le montant d’une opportunité ouverte par sa probabilité de signer finalement depuis l’étape actuelle, puis sommer. Un taux de transition suivante n’est pas cette probabilité. Le résultat conserve la nature du montant initial et n’est ni du revenu acquis ni automatiquement du MRR. **Provenance :** N échange 5 point 5. **État :** sens tranché, remplace DU-09 ; pertinence des valeurs, priorité cabinet/Boond, validité historique et application aux upsells ouvertes en QM-05.

<a id="du-21"></a>
**DU-21 — Deux grains de démo.** Une opportunité au statut Show Boond et une action de démo sont deux objets légitimes. Suivre séparément le temps dans le statut démo d’un dossier et le temps entre étapes du sous-parcours de démo. Le sous-parcours d’actions est une information secondaire souhaitée pour le data mart, sans préjuger de sa faisabilité. **Provenance :** N échange 5 point 3. **État :** retenu ; correspondance précise actions/étapes, chaînage, rattachement et objectif O04 ouverts en QC-02. Une action n’est pas un état durable par défaut.

<a id="du-22"></a>
**DU-22 — Objectifs simples.** Vérifier les quatre objectifs à la fin de chaque mois pour les équipes Sales. Aucune répartition journalière, hebdomadaire ou période partielle n’est demandée pour ces objectifs. **Provenance :** N échange 5 point 7. **État :** retenu ; réalisé compatible et compteur de démos restent à définir, sans rouvrir la fréquence.

<a id="du-23"></a>
**DU-23 — Attribution proposée comme convention de travail du case.** Pipe actuel : équipe à la date observée. Signature : équipe à la signature. Génération : équipe à l’entrée retenue du funnel. Un canal d’acquisition par opportunité, fixé à cette entrée ; conserver séparément les autres origines sans écrasement par la dernière interaction. Inbound proposé : demandes initiées par les prospects via marketing, liste de codes à confirmer. **Provenance :** N échange 5 point 8, tableau intitulé « Règle proposée ». **État :** convention utilisateur de travail, pas pratique réelle vérifiée ; mapping équipe, choix du champ canal et codes Inbound restent ouverts. Ne pas généraliser aux abonnements ou actions sans règle.

<a id="du-24"></a>
**DU-24 — Nouveaux clients et upsells séparés.** Conserver les types de dossiers et distinguer leurs funnels ; une vue filtrée par type est l’orientation de restitution proposée. Ne pas éliminer globalement les autres types au profit des seules nouvelles ventes. La condition « nouveaux clients » doit être explicite pour les mesures qui la nécessitent. **Provenance :** N échange 5 point 6. **État :** séparation et conservation retenues ; pas d’architecture de tables décidée, formation et affectation de chaque mesure encore en QC-01/QC-11.

<a id="du-25"></a>
**DU-25 — Versions raw déjà présentes.** `id` revient sur plusieurs versions, `meta.ts` date la publication CDC, `meta.deleted` signale une suppression ; conserver aussi le tenant dans l’identité. Ce n’est pas seulement le dernier état. **Provenance :** N échange 5 point 1, corroboré par le modèle et Q10. **État :** fait documentaire confirmé ; cela ne certifie pas une histoire métier complète ni la date réelle d’un événement.

<a id="du-26"></a>
**DU-26 — Nouvelle organisation du cockpit et analyse individuelle.** Échange 8 : conserver comparaisons réalisé/objectif et MRR/churn ; remplacer le centre par un grand tunnel, avec sélecteur de mesure local. Synthèse globale/par équipe ; feuille individuelle dédiée comparant individu/équipe sous réserve de faisabilité. **État :** orientation retenue, remplace l’exclusion générale DU-02. L’approbation des blocs ne valide pas leurs chiffres fictifs ni toutes les règles. Les modes précis du tunnel restent une proposition de présentation.

<a id="du-27"></a>
**DU-27 — Dashboard V1 limité, modèle détaillé réutilisable.** Échange 9 : maquette v2 acceptée comme base V1 ; data mart au grain maximal utile disponible pour stagnation, durée des étapes, canaux et analyses individuelles futures. **État :** retenu. Garder les données fines, leurs dates et leur provenance ; ne pas inventer un détail absent ni déduire une rétention illimitée. Le souhait de détail est conservé ; la proposition d’architecture demandée alors est retirée à l’échange 10. DCI-10 remplace la démarche par l’inventaire des champs.


### 2.4. Arbitrages de l’échange 22

Provenance commune : [message utilisateur intégral, échange 22](ia_assistant_story.md#echange-22). Une hypothèse retenue pour le case ne constitue pas une définition officielle Boond.

<a id="du-28"></a>
**DU-28 — Entrée du pipeline.** Dès la création du besoin dans Boond après soumission du formulaire (point 1). Frontière du cockpit retenue, QM-06 résolue pour le case ; ne pas appeler automatiquement le dossier « qualifié ». Pas filtre d’exclusion exigeant un formulaire retrouvé pour chaque upsell/canal. Dates et liaisons restent à vérifier.

<a id="du-29"></a>
**DU-29 — Deux KPI démo.** « Nombre de démos » = volume de RDV de démo réellement réalisés ; « Nb In demo » = stock de prospects à l’étape Démo (point 2). O04 utilise les RDV tenus. Preuve de réalisation, chaînage, attribution et identité société/opportunité du stock restent ouverts en QC-02. Pas équivalence automatique avec un nombre de contacts.

<a id="du-30"></a>
**DU-30 — Événement de signature.** Entrée dans « Signé — formalités à finaliser » (état 1), point 3. Passage en 14 sans deuxième vente. Montant mensuel et incrément/total upsell non répondus ; ne pas fermer ces points de QM-04/QC-11.

<a id="du-31"></a>
**DU-31 — Client actif.** Société ayant au moins un abonnement en cours à la clôture, point 4. Grain société retenu ; états/bornes, pause et gratuité non précisés. Activité distincte du test MRR > 0.

<a id="du-32"></a>
**DU-32 — Réactivation dans New MRR.** Hypothèse explicite du case, point 5 : un client qui revient après churn contribue à New MRR. Question à confirmer en réalité ajoutée à RAW-E22-01 à la demande utilisateur. Le statut de retour dans le KPI « nouveaux clients » au sens acquisition reste ouvert ; aucune réponse sur ce compteur ne doit être inventée.

<a id="du-33"></a>
**DU-33 — Mouvements nets au niveau société.** Pour le case, comparer les MRR totaux de chaque client entre clôtures, point 6. +100 € et −40 € sur deux lignes d’une même société = +60 € d’expansion, pas 40 € de churn. Pas compensation des pertes d’une société par les gains d’une autre. Les détails restent historisés. Confirmation réelle ligne/client dans RAW-E22-02 ; règles de calcul en R03.

<a id="du-34"></a>
**DU-34 — Départ-retour intra-mois hors périmètre.** Point 7 : scénario jugé trop spécifique pour le case, question conservée dans RAW-E22-03. Exclusion du traitement détaillé, pas résolution de la règle réelle ni suppression de l’historique. Photos de clôture conservées ; ne pas annoncer une couverture de tous les événements intra-mois.

<a id="du-35"></a>
**DU-35 — Portefeuille global.** Point 8 : le filtre équipe n’agit pas sur le bloc MRR actif/churn pour le moment, y compris ses composantes explicatives. Le MRR signé et les objectifs Sales restent par équipe. Pas besoin de décider maintenant une attribution financière aux équipes.

**Périmètre documentaire autorisé :** l’utilisateur demande explicitement l’ajout de trois questions dans raw_intent ; seule une annexe de `raw_intent/questions_metiers.md` est ajoutée. Les autres sources raw et entreprise restent intactes. Le texte historique du raw conserve son statut d’époque ; le clean porte les décisions actuelles.

### 2.5. Arbitrages de l’échange 23

<a id="du-36"></a>
**DU-36 — Nb In demo au grain société.** En réponse à « une société ayant deux opportunités en phase Démo : un prospect ou deux dossiers ? », l’utilisateur répond « un prospect ». Calcul : nombre distinct de sociétés ayant au moins une opportunité dans la phase à la date observée. QC-02 résolue sur ce grain ; preuve des liens et attribution restent à vérifier. Les groupes par équipe/canal peuvent se recouvrir : ne pas additionner leurs distincts pour fabriquer le total.

<a id="du-37"></a>
**DU-37 — Supplément d’upsell de 50 €/mois.** En réponse à la question du montant de MRR signé pour un abonnement passant de 100 à 150 €/mois, l’utilisateur retient « 50 euros supplémentaires » pour le case et demande de conserver la question dans raw_intent. Le montant incrémental est retenu, pas le total après extension. La donnée source qui le prouve et sa date d’activation restent à établir.

<a id="clarification-new-mrr-e23"></a>
**Clarification posée à l’échange 23 — résolue à l’échange 24 par DU-38.** La réponse contient exactement « 50 euros en new mrr ». Jusqu’à l’échange 22, New MRR = entrants/réactivations dans la base active ; expansion = hausse chez les clients restants ; MRR signé = engagement commercial. Ce libellé peut indiquer un élargissement souhaité de New MRR ou simplement le supplément vendu. Ne pas corriger silencieusement l’utilisateur, ni additionner le même supplément à New MRR et Expansion.

**Question historique, ne plus relancer :** quand tu écris « 50 € en New MRR », veux-tu inclure les hausses des clients existants dans le KPI New MRR, ou désignes-tu les 50 € supplémentaires vendus, qui restent séparés comme expansion lors de leur activation ? Le montant de 50 € est déjà décidé ; seule la catégorie est à clarifier. **Réponse échange 24 :** inclure les upsells dans New MRR, filtre New / Upsell. La formule U07 et la réconciliation sont actualisées ; la formulation précédente est conservée ici comme historique.

**Question réelle ajoutée sur demande :** [RAW-E23-01](../raw_intent/questions_metiers.md#raw-e23-01), incrément/total et nomenclature, sans bloquer le choix de 50 € du case. **Provenance :** [message intégral échange 23](ia_assistant_story.md#echange-23).

### 2.6. Arbitrage de l’échange 24

<a id="du-38"></a>
**DU-38 — New MRR inclut les upsells, filtre New / Upsell.** L’utilisateur précise : « upsell est dans le new mrr, avec la possibilité de filtrer par new ou upsell ». Cette décision résout la clarification de l’échange 23 et élargit le total U07, sans ajouter un troisième montant aux deux composantes.

**Définition actuelle :** New MRR total = composante New + composante Upsell. New reprend les entrants et retours après churn (DU-32) ; Upsell reprend l’expansion nette active des sociétés restées actives (DU-33). Le filtre permet de consulter chaque composante ou le total. Le regroupement des retours dans New résulte du maintien de DU-32 dans cette nomenclature ; il ne les transforme pas en premières acquisitions.

**Conséquence de calcul :** MRR fin = MRR début + New MRR total − churn MRR, à périmètre et unité identiques ; corrections explicites. Si les composantes sont affichées, utiliser New + Upsell à la place du total, jamais en plus. Le filtre New/Upsell qualifie l’apport financier ; un lien à raw.opportunities.typeOf=7 ne se déduit pas de la seule hausse d’abonnement.

**Invariants :** signé distinct d’actif, fin de mois sans prorata, net par société, détail/historisation conservés, bloc portefeuille global sans filtre équipe. Aucun objectif supplémentaire. [Formules R03](intent_ia.md#mrr-client-cloture) · [message intégral](ia_assistant_story.md#echange-24).

## 3. Désaccords et états documentaires à ne pas effacer

| ID | Désaccord ou risque de lecture | Traitement consolidé | Dépendance |
| --- | --- | --- | --- |
| C-01 | Cycle : besoin ouvert avant démo ; maquette : opportunité démarrant à la démo ; SQL : plusieurs états avant démo inclus. | Conserver les trois descriptions. La création CRM reste distincte d’une qualification commerciale. La décision utilisateur échange 22 fixe l’entrée du cockpit à la création ; le SQL n’est pas sa justification. | QM-06 |
| C-02 | Probabilité de passage suivant selon l'utilisateur, de signature selon le modèle. | Ancien désaccord conservé comme historique : échange 5 retient la signature finale. Calibration et source des valeurs restent ouvertes. | QM-05 |
| C-03 | MRR décrit comme montant signé Boond ou montant du deal HubSpot dans le README ; formulation utilisateur rapprochant MRR encaissé et chiffre d'affaires. | Conserver la distinction ; encaissements exclus à l’échange 5. Boond reste la référence du MRR actif ; les autres montants demandent leurs propres règles. | QM-04, QC-04 |
| C-04 | Démo assimilée à un stade par un commercial et à des actions d'agenda par un autre. | La distinction action/phase est décidée ; la réalisation, l'attribution et les compteurs restent ouverts. | QC-02 |
| C-05 | Le raw contient des mentions anciennes de Q10 « reportée », y compris QM L3 ; sa section 13 adopte ensuite le diagnostic. | État actuel : diagnostic disponible ; échange 22 tranche la frontière du cockpit à la création Boond. La qualification commerciale n’est pas assimilée à la création. | DU-15, QM-06 |
| C-06 | Anciennes références au README décalées après modification préexistante du fichier. | Repères actuels : équipes/outils L36 ; CDC L38 ; désaccord d'ouverture L53 ; MRR L57–59 ; démos L61–63 ; pas de réponse métier pendant l'exercice L67 ; SQL legacy L76. | Traçabilité de tout le dossier |
| C-07 | Mise à jour quotidienne supposée, alors que les documents décrivent plusieurs circuits et un snapshot manuel d'attente. | Distinguer période affichée, recalcul et fraîcheur par source ; ne pas généraliser une cadence. | QC-06 |
| C-08 | Demandes individuelles de la maquette et orientation stratégique ultérieure. | Dernière orientation : synthèse équipe/global, feuille individu/équipe demandée aux échanges 8–9. Les cibles personnelles ne sont pas déduites des cibles collectives. | DU-02, QC-08 |
| C-09 | SQL utilisant des présences hebdomadaires et montants moyens, noms pouvant évoquer des stocks ou signatures nouvelles. | Conserver L01–L04 comme observations de l'existant ; aucune équivalence automatique avec les cibles M/O/U. | QC-04, QM-04 |
| C-11 | Différence de stocks corrigée des seules entrées appelée churn ; upsells pouvant masquer les pertes. | Échange 6 : churn MRR = départs + baisses, hors New MRR et expansions ; réconciliation et cas multiples en QC-12. | DU-19, QC-12 |
| C-10 | « Sans historique natif, impossible » dans E L9, alors que le flux CDC conserve des versions. | Le besoin d'histoire est explicite ; la possibilité d'une reconstruction dépend de la couverture et du sens des dates. Ni impossibilité générale ni reconstruction certifiée ne sont acquises. | QC-10 |

## 4. Questions métier héritées

<a id="qm-01"></a>
### QM-01 — Passages, retours et issues du parcours

**Provenance :** demande de clarification IA confiée explicitement au métier par l'utilisateur ; J L298, R §8 Q13, QM L5–13. **État :** ouvert pour les règles restantes. **Arbitre du case :** utilisateur, selon DU-17. Dans la vie réelle : responsables Sales/commerciaux puis VP Sales. Les observations upsell de QC-11 enrichissent les constats sans valider un workflow universel.

**Ce qui est établi.** Le cycle fournit un parcours nominal. Il ne prouve pas que chaque dossier traverse toutes les étapes ni que les issues constituent une chaîne linéaire. Nurturing figure comme attente possible. Les observations Q10 comportent des passages non enregistrés ; elles ne permettent pas de savoir pourquoi ils manquent.

**Question autonome.** Quel workflow commercial veut-on reconnaître : peut-on sauter une étape, revenir dans une étape précédente, rouvrir une affaire signée/perdue/abandonnée ou sortir du nurturing ? Quels événements distinguent une simple attente, une qualification refusée, une perte et un abandon ? Quels états font partie du pipeline activement travaillé et lesquels doivent être suivis séparément, notamment nurturing et anciens états désactivés dans l'interface ?

**Précisions nécessaires.** Pour les retours et réouvertures, distinguer le devenir du même besoin d'un nouveau besoin commercial ; préciser si une nouvelle entrée compte comme un nouveau flux ou comme la poursuite du dossier initial. Le choix du début qualifié relève de [QM-06](#qm-06), les règles de durée de [QC-03](#qc-03) et les cohortes de [QC-10](#qc-10).

**Pourquoi cela compte.** Les populations ouvertes, transitions et issues, les dénominateurs de conversion, les séjours dans les étapes et la cohorte d'un dossier dépendent de ces règles. Aucun ordre strict n'est déduit des codes numériques.

**Éléments dépendants :** M03–M08, B01–B03, U01–U03 ; H04–H08 restent conditionnels. **Sources :** C L98–114 ; D L914–917 ; Q10 §2–5 et §8 ; SQL §6. **Réponse/validation :** pas de convention générale arrêtée ; les précisions nouvelles sont prises en compte dans les questions dédiées.

<a id="qm-02"></a>
### QM-02 — Choisir le champ du canal d’acquisition

**État : partiellement défini.** Un canal par opportunité, fixé à son entrée dans le funnel, est la convention de travail proposée par l’utilisateur (N échange 5 point 8 ; DU-23). Les autres informations sont conservées séparément ; la dernière interaction ne remplace pas automatiquement le canal d’entrée.

**Question restante — à l’utilisateur pour le case.** Pour fixer ce canal, quel champ privilégier entre `raw.opportunities.origin.typeOf`, les données de première conversion et les UTM HubSpot ? En cas de désaccord, d’absence ou de contact commun à plusieurs dossiers, quelle règle appliquer ?

**Pourquoi cela compte.** La convention temporelle est connue, mais elle ne suffit pas à attribuer un code source à chaque dossier. Les volumes, montants et conversions par canal dépendent de cette règle. Inbound reste en QC-05 ; aucun modèle multicanal n’est ajouté. **Sources :** modèle, anciens R Q14, N échange 5. **Dépendances :** M02/M03, analyses par canal explicitement retenues.


<a id="qm-03"></a>
### QM-03 — Validation des définitions dans le case

**État : résolu pour l’exercice.** L’utilisateur tranche les conventions et valide leurs modifications (N échange 5 point 2 ; DU-17). Ne plus attendre une réponse de la VP Sales pour avancer dans ce case.

Dans la vie réelle, les définitions devraient être discutées avec la VP Sales et les métiers concernés. Ce rappel ne crée pas une dépendance bloquante dans l’exercice. Les exemples d’acceptation pourront être précisés au moment des spécifications, sans rouvrir la question de l’autorité.

**Provenance conservée :** anciens R Q16 / QM-03 demandaient une gouvernance partagée ; N échange 5 fournit maintenant la convention de l’exercice.


<a id="qm-04"></a>
### QM-04 — Montants récurrents, activité, signature et New MRR

**Échanges 23–24 :** supplément upsell retenu (50 €/mois dans l’exemple), donnée source encore à vérifier. La nomenclature est résolue : l’upsell est une composante de New MRR, filtrable séparément (DU-38).

**Mise à jour de l’échange 22 :** état 1 retenu pour la signature ; client actif = société avec au moins un abonnement en cours à clôture ; retours après churn inclus dans New MRR pour le case. Les anciennes formulations ci-dessous sur le choix de l’événement et des réactivations sont remplacées par DU-30/31/32. Restent le montant signé/incrément upsell, les états/bornes, gratuités/pauses et corrections.

**État : partiellement défini.** MRR actif, signé, New MRR et churn retenus. Encaissements U08 exclus. Observation à fin de mois, sans prorata journalier. Churn MRR = pertes par départ + baisses d’abonnement, hors New MRR et upsells. Arbitrage utilisateur pour le case : DU-17 à DU-19 ; N échanges 5–6. Ne plus redemander si l’on veut ces mesures ni si l’on prorate les jours.

**Questions encore ouvertes :**

1. **Actif à la clôture.** Quels états de lignes/projets et quelles bornes début/fin définissent un abonnement actif ? Comment traiter pause, gratuité et plusieurs lignes se remplaçant ? La date d’observation est fixée à fin de mois ; ce sont les critères d’éligibilité qui manquent.
2. **Montant mensuel.** Le modèle décrit `raw.deliveries.averageDailyPriceExcludingTax` comme montant mensuel d’abonnement incluant quantité × prix unitaire. Confirmer les exceptions, remises et devises à prendre en compte ; ne pas multiplier une deuxième fois par la quantité. Un montant estimé de besoin n’est pas nécessairement un MRR.
3. **Montant signé.** L’événement est décidé : entrée à l’état 1, sans deuxième vente en 14. Pour l’upsell, le supplément est décidé à l’échange 23 (150 − 100 = 50 €/mois). Quelle donnée source prouve le montant mensuel engagé ? Le libellé est résolu à l’échange 24 : Upsell appartient au total New MRR, filtrable séparément. Restent preuve de date, annulations et réouvertures ; le choix 1/14 n’est plus à poser.
4. **Nouveaux clients et activité.** New MRR inclut les retours après churn pour le case. Le compteur « nouveaux clients » doit-il désigner uniquement les premières acquisitions ou tous les entrants, retours compris ? Les critères d’activité des lignes restent à préciser. Les nouvelles lignes d’une société restée active contribuent à sa variation nette, pas automatiquement au New MRR.
5. **Scénario U09.** L’idée de portefeuille constant reste facultative. L’exclusion des encaissements n’en précise ni la variable ni l’utilité ; ne pas la convertir en KPI obligatoire.

**Pourquoi cela compte.** Ces réponses définissent les populations et montants de U05–U07 et U10–U13. La règle de churn est complétée en QC-12 et celle des upsells en QC-11. Les paiements et proratas journaliers ne sont plus des questions à résoudre pour ce périmètre. **Sources :** N échanges 5–6 ; modèle raw.deliveries/projects/opportunities ; R §10.


<a id="qm-05"></a>
### QM-05 — Validité et source des probabilités de signature

**État : sens résolu, valeurs encore à confirmer.** La probabilité attendue est la chance de signature finale depuis l’étape actuelle (DU-20, N échange 5 point 5). Le désaccord ancien sur la probabilité de transition suivante est clos, sa provenance reste dans DU-09/C-02.

**Question restante — utilisateur pour le case.** Retient-on `ref.stage_probabilities.probability` ou la pondération saisie dans Boond ? Les coefficients fournis ont-ils été construits pour l’usage retenu, pour quelles équipes, périodes et types de vente ? Sont-ils pertinents pour les upsells au parcours court ?

**Compléments nécessaires.** Quelle convention appliquer au passé, aux coefficients manquants et aux changements de valeur ? La maquette propose une confrontation aux taux observés ; aucune requête n’est relancée dans cette phase. La probabilité conserve l’unité du montant initial et ne transforme pas une valeur de contrat en MRR.

**Dépendances :** M04/B03/O03, M07 si sa définition utilise une pondération. **Sources :** modèle `ref.stage_probabilities`, `raw.opportunities.weighting` ; N échange 5 ; analyse upsell §6.


<a id="qm-06"></a>
### QM-06 — Entrée dans le pipeline commercial qualifié

**État actuel : résolu pour la frontière du cockpit, échange 22 point 1 / DU-28.** Le dossier entre dans le pipeline dès sa création dans Boond après soumission du formulaire. Aucune qualification ou démo ultérieure n’est requise pour cette entrée.

**Distinction :** création et qualification commerciale restent deux notions différentes. On ne rebaptise pas automatiquement toute fiche créée « opportunité qualifiée ». La règle ne prouve pas que tous les dossiers, notamment upsells, ont un formulaire ; ne pas les exclure faute de formulaire lié.

**Provenance et désaccord conservés :** Q10 documente 1 271 premiers états Lead à traiter sur 1 376 besoins courants, sans décider de la règle cible. Le cycle décrit la création avant démo ; la maquette faisait démarrer l’opportunité à la démo ; le SQL inclut d’autres états. La décision utilisateur définit maintenant l’orientation du cockpit, sans rendre ces documents identiques ni inventer des événements.

**Dépendances encore ouvertes :** qualité/date métier de création (`raw.opportunities.creationDate` candidate, pas `meta.ts` par défaut), montant au moment de l’entrée, populations par cible, sauts/réouvertures, attribution canal et cas d’historique manquant. Pas de nouvelle génération du même dossier à chaque version CDC. Cohorte de création et début du cycle se rattachent à cette entrée ; une mesure de qualification séparée ne bloque plus M01/M02.

**Sources :** N échange 22 point 1 ; Q10 §1–5/8 et preuves Q2/Q3 ; R §13 ; maquette et cycle conservés en C-01. **Éléments concernés :** M01/M02, B02, U01–U03, O02, QC-01/QC-11.

## 5. Questions complémentaires nécessaires à la définition

<a id="qc-01"></a>
### QC-01 — Populations commerciales selon les analyses

**État : partiellement défini.** Nouveaux clients (`typeOf=4`) et upsells (`typeOf=7`) sont conservés et leurs funnels séparés ; le filtre de dashboard par type est l’orientation souhaitée. Ne pas appliquer partout un filtre nouveaux clients. **Source :** N échange 5 point 6, DU-24 ; UP §1/6.

**Question restante — utilisateur.** Pour chaque montant et objectif, veut-on une lecture nouveaux clients, upsells ou globale ? Les formations (`typeOf=2`) restent-elles seulement conservées ou doivent-elles participer à certaines analyses ? Quel critère distingue un nouveau client d’un client réactivé ?

**Conséquence.** M01–M08, B01–B03, O01–O04 et les conversions ont besoin d’une population explicite. Cette question ne remet pas en cause la conservation des types ni leur distinction. Les règles de revenu des upsells sont en QC-11 et QM-04.


<a id="qc-02"></a>
### QC-02 — Deux niveaux de démo et leur chaînage

**Échange 23 :** identité In demo résolue : société distincte (DU-36). Ne plus poser le choix société/opportunité. Les preuves, liens et durées restent ouverts.

**Mise à jour de l’échange 22 / DU-29 :** deux KPI : RDV de démo réellement réalisés (réalisé O04) et stock « Nb In demo ». Le choix prévu/tenu est tranché. Restent la preuve de tenue, la déduplication, le chaînage et l’attribution ; identité société/opportunité du prospect In demo à préciser. Les demandes de choix de compteur dans le détail antérieur ne sont plus à relancer.

**État : grains et deux durées retenus, détails ouverts.** Opportunité au statut Show Boond : grain dossier/passage d’état. Actions de demande, démo 1 et complémentaire : grain action, avec un sous-parcours secondaire souhaité. L’un mesure le temps dans le statut commercial ; l’autre le temps entre étapes du parcours de démo (N échange 5 point 3 ; DU-21).

**Questions restantes — utilisateur :**

1. Quelles actions et dates marquent chaque étape du sous-parcours : demande, planification, séance, complément, annulation ? La durée d’une séance d’agenda (`endDate − startDate`) est différente de l’attente entre deux étapes. Quelle preuve distingue prévu, tenu, reporté et annulé ?
2. Comment chaîner plusieurs actions en un même parcours, puis les relier à la bonne opportunité quand le contact en porte plusieurs ? `dependsOn.data.type` doit être lu avec son identifiant ; un lien contact n’est pas un lien opportunité.
3. **Résolu échange 23 :** « Nb In demo » compte les sociétés distinctes ; deux dossiers d’une société en Démo = un prospect. Restent la qualité du rattachement société et l’attribution aux axes. O04 reste le nombre de RDV réellement tenus.

**Observation reçue, pas nouveau comptage :** l’utilisateur rapporte 533 actions Démo 1 (type 60), 74 complémentaires (68), 700 demandes (25) et 75 RDV annulés (17). Les 607 actions de types démo sont cohérentes avec Q10. Ce n’est ni 607 opportunités ni une preuve de tenue. Le tableau transmis contient une première ligne mal formée : aucun code n’est inventé pour « Appel non abouti ». L’analyse upsell montre des actions sur contacts communs, sans rattachement démontré aux upsells.

**Dépendances :** U04, U03, B01, O04 ; H06 reste candidat pour les taux non explicitement retenus. **Sources :** N échange 5 ; modèle raw.actions ; Q10 §5 E ; UP §5.


<a id="qc-03"></a>
### QC-03 — Durées, stagnation et pertes jugées trop importantes

**Provenance :** besoins utilisateur Q9/Q11 et demandes M08/B01 ; J L294 et L490 ; R L309–315, L788–792. **État :** analyses souhaitées, conventions ouvertes. **Destinataires :** utilisateur pour les lectures et décisions recherchées ; Sales/VP Sales pour seuils et conventions métier.

**Ce qui est établi.** Ancienneté dans le stage courant, durée d'un passage terminé, durée cumulée après retours et durée totale du cycle répondent à des questions différentes. La maquette donne « > 30 jours » comme exemple interrogatif. Les seuils de stagnation et de perte « trop importante » ne sont pas validés.

**Question autonome.** Pour chaque lecture de durée, quels événements ouvrent et ferment la période mesurée ? Comment traiter un retour dans une étape, une pause ou le nurturing : temps continu, suspension ou autre convention à expliciter ? La durée s'exprime-t-elle en jours calendaires, ouvrés ou une autre unité ? Quelles statistiques ou répartitions aideraient la décision — moyenne, médiane, quantiles ou classes de durée — et sur quels dossiers comparables, en séparant si nécessaire les séjours encore ouverts des séjours terminés ?

**Seuils et interprétation.** À partir de quelle règle un dossier devient-il stagnant : seuil commun, seuil par étape/équipe ou comparaison à une référence historique ? Selon quel repère une conversion est-elle jugée insuffisante et sur quelle fenêtre ? Les possibilités citées servent à expliquer les choix, pas à fixer un défaut. Une durée élevée ou une baisse de conversion ne démontre pas sa cause.

**Pourquoi cela compte.** Le classement des étapes problématiques et le montant immobilisé peuvent changer selon les pauses, retours, statistiques et seuils. L'événement initial dépend de [QM-06](#qm-06) et la qualité des dates de [QC-10](#qc-10).

**Éléments dépendants :** M08, B01, U01–U03 ; H03/H07 conditionnels. **Sources :** M zone 8 ; E L9 ; R L312–314, L683, L709 et L792. **Réponse :** inconnue ; aucun seuil de 30 jours adopté.

<a id="qc-04"></a>
### QC-04 — Génération, stock, montants commerciaux, couverture, ADV et BP

**Provenance :** demandes de la maquette et définitions manquantes ; M guide supérieur et zones 1–7 ; R §12 M01–M07 ; analyse SQL §4 et §6. **État :** besoins recensés, conventions ouvertes. **Destinataires :** utilisateur pour la décision analytique recherchée ; VP Sales/cabinet pour le sens du brief ; Finance si une unité de revenu est retenue.

**Ce qui est établi.** M02 compte des opportunités générées ; O02 est une cible monétaire de pipeline généré. M03/M05 concernent un pipe ouvert à date, distinct d'un flux généré. Le legacy produit des présences hebdomadaires et des montants moyens, pas des définitions cibles. À l’échange 16, l’utilisateur suggère qu’ADV désigne l’Administration des ventes ; ce sens reste à confirmer dans le brief. La zone 7 décrit cependant explicitement un MRR potentiel moyen par deal : cette proposition reste distincte du sigle. Le guide de la maquette demande aussi combien d'activité/de pipe générer pour atteindre le « BP ».

**Questions autonomes liées aux mesures commerciales :**

1. **Pipeline généré.** Quel événement crée le montant de pipeline généré, à quelle date et avec quelle valeur du dossier ? Comment traiter un montant saisi ou corrigé après l'entrée, une réouverture, une réentrée, une annulation et une génération négative éventuelle ? La frontière du volume M02 reste en QM-06 ; les deux mesures ne sont pas assimilées.
2. **Pipe ouvert.** Quelle population constitue le stock à une date et quel montant exprime chaque dossier : potentiel mensuel récurrent, valeur contractuelle totale, autre unité ? À quelle date de référence comparer les photos et comment présenter un montant absent sans le confondre avec zéro ? Nurturing et états anciens relèvent de QM-01 ; les règles de devises et de MRR de QM-04.
3. **Pipeline coverage.** Quel objectif mensuel est le dénominateur de la zone 6 ? Le numérateur est-il le pipe ouvert dont la clôture est prévue dans ce mois, avec quelle nature de montant et quelle date d'observation ? Comment lire les dates prévues manquantes, dépassées ou modifiées, et quel horizon de comparaison est pertinent ? Aucun objectif O01/O02/O03 n'est choisi silencieusement.
4. **MRR potentiel moyen proposé par le brief.** L’interprétation utilisateur « Administration des ventes » pour ADV reste à confirmer ; le sigle n’est plus présenté comme KPI. Indépendamment de ce sigle, quel potentiel moyen veut-on connaître, sur quelle population et avec quel rôle du stage et de la probabilité ? Le montant est-il mensuel récurrent, et quels sont numérateur et dénominateur ? Aucune formule d'ARPU ou de moyenne pondérée n'est substituée sans confirmation.
5. **Activité nécessaire pour atteindre le BP.** Que désigne le BP, quelle cible et quel horizon sont concernés, et quelle activité souhaite-t-on estimer ? Quels taux, montants moyens ou scénarios seraient légitimes pour remonter de la cible à un besoin d'activité/pipe ? Il s'agit d'une attente source à définir, pas d'une formule inverse déjà validée ni d'un KPI chiffré ajouté.

**Pourquoi cela compte.** Stock, flux et moyenne n'ont pas les mêmes agrégations ; nombre et montant ne partagent pas automatiquement la même règle. Un ratio de couverture ou une estimation d'activité est trompeur si les unités et populations de la cible diffèrent.

**Éléments dépendants :** M01–M07, O02/O03 et besoin BP du guide ; rapprochement avec L01–L04 sans adoption de leurs calculs. **Sources :** M guide supérieur, zones 1–7 ; R L647–653 et L670–675 ; SQL L62–66 ; analyse SQL L243–291, L443–458. **Renvois :** [QM-05](#qm-05) pour pondération, [QC-09](#qc-09) pour objectifs, [R03](intent_ia.md#r03-montants). **Réponse :** inconnue.

<a id="qc-05"></a>
### QC-05 — Rattachements d’équipe et codes Inbound restant à préciser

**Périmètre décidé échange 22 / DU-35 :** le bloc MRR actif/churn reste global, sans filtre équipe pour le moment. Son attribution aux équipes n’est plus un prérequis du case. Les conventions commerciales génération/signature/pipe restent pertinentes ; mappings et canaux restent à préciser.

**État : conventions temporelles proposées par l’utilisateur, correspondances ouvertes.** Pipe : équipe à date observée ; signature : équipe à l’événement ; génération : équipe à l’entrée du funnel. Un canal par dossier fixé à l’entrée, autres origines conservées à part. Source : DU-23, N échange 5 point 8.

**Questions restantes.** Quelle correspondance du responsable vers SMB/LA/ES utiliser à la date pertinente ? Comment présenter les dossiers sans rattachement connu ? Pour les actions et abonnements, quelle attribution appliquer si une analyse par équipe est attendue ? La règle d’opportunité ne se propage pas automatiquement à ces objets.

**Inbound.** La proposition couvre les demandes initiées par les prospects via les canaux marketing. Quelle liste explicite de codes sources inclure ? L’origine Boond et les UTM ne doivent pas être regroupées sans correspondance. Le choix du champ de référence relève de QM-02.

**Conséquence.** Ventilations et comparaison aux objectifs ; les équipes doivent former des populations compatibles sans doubler le global. Les conventions déjà proposées ne sont pas redemandées. **Sources :** N échange 5 ; modèle responsables/référentiels ; R §12 E.


<a id="qc-06"></a>
### QC-06 — Périodes d'analyse, fréquence de recalcul et fraîcheur attendue

**Provenance :** précision utilisateur Q8 et circuits documentés ; J L293 ; R L301–307. **État :** pistes jour/semaine/mois, exigences opérationnelles ouvertes. **Destinataires :** utilisateur et utilisateurs Sales/Marketing pour le rythme des décisions ; responsables des sources pour la disponibilité réelle, à confirmer sans test de service pendant cette phase.

**Ce qui est établi.** Les cibles sont mensuelles, le SQL regroupe par semaine, les cohortes sont mensuelles avec horizons J+30/J+60/J+90. Boond est décrit en flux temps réel ; les contacts HubSpot sont décrits comme recopiés chaque nuit. Le snapshot manuel quotidien de l'expression de besoin est un dispositif d'attente. La cadence de chaque autre source n'est pas démontrée par ces informations.

**Question autonome.** Quels usages nécessitent une lecture au jour, à la semaine ou au mois, à quel moment les chiffres doivent-ils être disponibles et quel retard reste acceptable ? Pour chaque mesure, quelle date métier filtre la période, quel fuseau et quelles bornes définissent le jour, la semaine et le mois ? Comment distinguer une période en cours d'une période complète et signaler une source trop ancienne pour la décision ?

**Précisions nécessaires.** La fréquence de recalcul doit servir l'usage et tenir compte de la disponibilité des sources ; elle n'est pas déduite du grain du graphique. MRR actif et contrôle des objectifs sont déjà fixés à fin de mois ; l’heure/fuseau de clôture et la disponibilité des sources restent à préciser. QM-04 traite les états/bornes et QC-09 les réalisés compatibles, sans remettre en question cette cadence.

**Pourquoi cela compte.** Une mesure hebdomadaire peut être recalculée quotidiennement ; un résultat calculé aujourd'hui peut décrire des données antérieures. Mélanger les trois notions rend les comparaisons et les alertes ambiguës.

**Éléments dépendants :** toutes les familles affichées dans le temps. **Sources :** README L38 ; D L1185–1187 ; E L9–20 ; SQL L60–68 ; R L700–708. **Renvoi :** [R02](intent_ia.md#r02-temps). **Réponse :** cadence mensuelle de clôture MRR/objectifs acquise à l’échange 5 ; autres usages et fraîcheur encore ouverts.

<a id="qc-07"></a>
### QC-07 — Rétention détaillée, cinq ans d'agrégats et usages autorisés

**Provenance :** décisions/hypothèses utilisateur Q1/Q7 ; J L286 et L292 ; R L243–249 et L292–299. **État :** cinq ans d'agrégats retenus ; rétention détaillée et cadre de traitement à confirmer. **Destinataires :** utilisateur pour les hypothèses du case ; responsables compétents de la donnée et de la protection des données pour les règles réelles. Aucun rôle juridique précis n'est assigné sans confirmation.

**Ce qui est établi.** DU-10 fixe cinq ans pour les agrégats. DU-11 conserve des hypothèses de traitement autorisé et une durée envisagée de trois ans après churn pour les clients, ainsi que de trois ans pour les leads, sans définir précisément les données et finalités couvertes. La conservation des données intermédiaires reste à arbitrer selon les finalités, contraintes, volumes, coûts et besoins de reconstitution. Une agrégation ne prouve pas une anonymisation.

**Question autonome.** À partir de quel événement commence le délai des leads et quel événement de départ complet déclencherait celui des clients ? Le churn analytique en euros inclut désormais les baisses, qui ne signifient pas départ du client : ne pas les utiliser automatiquement comme point de départ de conservation. Quelles données détaillées ou intermédiaires doivent rester disponibles pour recalculer, expliquer ou corriger les agrégats, pendant combien de temps et pour quelles finalités ? Comment articuler leur retrait avec les cinq ans d'agrégats et avec les dossiers commerciaux réouverts ou les clients réactivés ? Quelles règles réelles de traitement et de conservation restent à faire confirmer ?

**Pourquoi cela compte.** Une profondeur analytique de cinq ans n'autorise pas automatiquement la conservation de chaque détail pendant cinq ans. Inversement, l'effacement du détail peut limiter la reconstitution. Aucune conformité juridique ni implémentation de rétention n'est déclarée acquise ou promise ici.

**Éléments dépendants :** histoire B01–B03, U02/U03/U05, capacité future de correction, règles communes de conservation. **Renvois :** [DU-19](#du-19) pour le churn analytique et [QC-12](#qc-12) pour les cas de départ/retour ; [QC-10](#qc-10) et [R05](intent_ia.md#r05-histoire) pour l'histoire. **Réponse :** définition analytique du churn actualisée ; événement de conservation et durées détaillées toujours ouverts.

<a id="qc-08"></a>
### QC-08 — Usages Marketing, détail explicatif des dossiers et rôle de Data

**Provenance :** utilisateurs définis, clarification Q5 acquise et détails encore absents ; J L161 et L465 ; R §1, §10 Q5, §12 M08. **État :** orientation générale retenue, usages complémentaires ouverts. **Destinataires :** utilisateur pour l'intention du cockpit et le rôle souhaité de Data ; Marketing pour ses rapports/pratiques effectifs ; Sales pour le détail utile à l'explication des agrégats.

**Ce qui est établi.** Sales et Marketing sont utilisateurs directs et regardent des représentations du parcours dans leurs outils. La synthèse est stratégique, par équipe/global ; une analyse individuelle dédiée est désormais demandée, précisée en QC-14. M08 propose une liste de dossiers stagnants, dont la place dans cette orientation n'est pas encore définie. La phrase initiale sur Data ne précise pas un rôle supplémentaire.

**Question autonome.** Quelles décisions Marketing doivent être éclairées par les analyses communes, et quels rapports, définitions et filtres actuels sont à rapprocher ? Dans la lecture stratégique, faut-il pouvoir examiner certains dossiers pour comprendre un agrégat ou une stagnation, et avec quel niveau de détail utile ? Quel rôle de consultation ou d'analyse Data souhaite-t-on au-delà de la construction et de la documentation du cockpit ?

**Limites de la question.** Elle ne rouvre pas la compréhension générale Sales/Marketing ; l’analyse individuelle dédiée est traitée dans QC-14 selon la nouvelle orientation. Les motifs de perte et les parties encore candidates de H01–H10 peuvent être discutés pour leur utilité ; le sous-parcours démo et le churn explicitement retenus ne sont pas remis en question ; leur présence dans les visualisations ne valide ni causes ni chantiers Produit/Tech. Aucun nouvel utilisateur direct, dispositif d'accès ou parcours d'interface n'est inventé.

**Pourquoi cela compte.** La même donnée peut servir un diagnostic global, une comparaison de canaux ou une explication de dossier. Clarifier l'usage évite d'étendre le périmètre par défaut ou d'écarter une attente source sans trace.

**Éléments dépendants :** M02/M03/M07/M08, U01/U02, hypothèses H et associations d'axes. **Sources :** R L9–18, L553–561, L654, L712 et L718 ; M guide et zone 8. **Réponse :** inconnue ; aucune réouverture de DU-02/DU-13.

<a id="qc-09"></a>
### QC-09 — Réalisés compatibles avec les quatre objectifs

**Actualisation échange 22 :** entrée à création Boond, signature à l’état 1 et démos réellement tenues pour O04. Restent compatibilité des populations/montants et rattachements aux équipes ; cadence mensuelle acquise.

**État : cadence et niveau résolus.** Contrôle en fin de mois pour les équipes Sales, quatre cibles de `ref.sales_targets` : MRR signé, pipeline généré, pipeline pondéré, démos. Pas de découpage quotidien ou hebdomadaire à ajouter. Source : DU-22, N échange 5 point 7.

**Reste à définir.** Le réalisé compatible avec chaque cible : événement/montant de signature U06 ; événement/valeur de génération M01 ; montant et coefficient de M04 observé à la clôture ; compteur de démos U04. Les questions sont portées par QM-04, QM-06, QC-04, QM-05 et QC-02, pas par une nouvelle gouvernance des objectifs.

**Lecture simple.** Présenter réalisé et cible du même mois et de la même équipe. M01 possède déjà la formule `réalisé / cible × 100`. Si un taux est utilisé ailleurs, sa base doit être compatible ; cible nulle ou absente ne produit pas un pourcentage inventé. Aucune nouvelle cible churn/New MRR n’est fournie.

**Conséquence :** O01–O04 et comparaisons M01/M04. La globalisation doit préserver la compatibilité des unités ; les stocks de plusieurs fins de mois ne s’additionnent pas en flux.


<a id="qc-10"></a>
### QC-10 — Histoire incomplète, cohortes et comparabilité dans le temps

**Précision de l’échange 19 :** l’historisation de toutes les couches est désormais explicitement requise, ce point n’est plus à arbitrer. Restent à préciser la lecture des corrections (passé corrigé, tel que connu à une date, ou les deux), les métadonnées/règles de version, la sélection cohérente pour les KPI et la couverture effectivement observable. La rétention détaillée reste en QC-07.

**Provenance :** demande E, observations Q10, limites du SQL et besoin de cinq ans ; R §13 et analyse SQL. **État :** besoin historique explicite, conventions d'observation et de comparaison ouvertes. **Destinataires :** utilisateur pour la lecture souhaitée et les limites acceptables du case ; métiers pour les événements et règles historiques ; Data pour qualifier ensuite la couverture effective, sans inventer les événements absents.

**Ce qui est établi.** E demande des cohortes par mois de création, observées à J+30/J+60/J+90, et une évolution du pipe pondéré. Le jeu Q10 comporte des créations antérieures à sa première observation CDC. Parmi 227 besoins actuellement signés, 121 n'ont pas de Show Boond enregistré. Ces constats n'établissent ni un saut réel ni une absence de démo. Le contrôle courant n'est pas une reconstruction certifiée de toutes les populations passées.

**Questions autonomes :**

1. **Événement et horizon de cohorte.** Une fois QM-06 tranchée, comment nommer et maintenir la cohorte de création CRM et, si souhaitée, celle d'entrée qualifiée ? Les horizons J+30/J+60/J+90 se mesurent-ils depuis chaque événement d'entrée ou selon une convention commune de fin/début de mois ? Comment gérer les réentrées sans changer silencieusement la cohorte ?
2. **Population et issues.** Quel dénominateur conserve-t-on pour comparer ouvert/gagné/perdu dans une cohorte ? Où figurent abandons, non-qualifiés, nurturing, suppressions et dossiers non observables ? Les catégories doivent être explicitement définies ; leur absence dans les trois libellés d'E ne vaut pas exclusion automatique.
3. **Historique incomplet.** Comment présenter un début ou un passage non observable : catégorie distincte, indicateur de couverture, analyse limitée à une fenêtre documentée ou autre convention ? Si une date CDC sert de proxy, quel nom et quelle réserve permettent de la distinguer d'une date métier certaine ? Aucun événement ni durée antérieure à la couverture n'est inventé.
4. **Maturité et correction.** Comment identifier les cohortes trop récentes pour un horizon et comparer des populations de maturité compatible ? Quel sens donner à une reconstitution corrigée après réception tardive ou modification rétroactive, par rapport à ce qui était connu à l'époque ? Cette question concerne l'interprétation des chiffres, pas un choix de technologie.
5. **Référentiels dans le temps.** Comment traiter les étapes anciennes, changements d'équipe et évolutions du produit lorsque l'on compare plusieurs années ? La convention d'états relève de QM-01, celle d'équipe de QC-05 et celle des probabilités de QM-05. Pour le MRR actif passé, la dernière version connue aujourd'hui ne suffit pas nécessairement à décrire le portefeuille à la date observée.

**Pourquoi cela compte.** Une absence de trace ne peut être comptée comme échec automatique ; une cohorte encore immature ne peut recevoir un résultat futur. Ces choix conditionnent les dénominateurs, durées et séries historiques, tout en permettant de conserver le besoin complet même si sa couverture actuelle est limitée.

**Éléments dépendants :** B01–B03, U01–U03/U05, lectures historiques M03–M08, O03 selon comparaison. **Sources :** E L9–16 ; Q10 L95–116, L143–178, L223–238 et L261–264 ; preuves Q2/Q3 ; R L525 et L829–845 ; analyse SQL L273–281. **Renvoi :** [R05](intent_ia.md#r05-histoire). **Réponse :** aucune convention nouvelle retenue.

<a id="qc-11"></a>
### QC-11 — Upsells : parcours, valeur et effets sur les abonnements

**Échange 23 :** incrément upsell décidé pour le case ; le choix incrément/total n’est plus ouvert ici, mais reste une question réelle dans RAW-E23-01. Nomenclature New MRR/expansion résolue par DU-38 : Upsell dans le total New MRR.

**Actualisation échange 22 :** entrée du pipeline à création Boond ; aucun passage par démo imposé aux upsells. Signature dès état 1. Montant incrémental/total signé et lien vers expansion effective non répondus. Ne pas présumer un formulaire lié à chaque upsell.

**État : séparation acquise, règles propres ouvertes.** Dans l’analyse enregistrée : 52 upsells, 51 sociétés ; les dossiers avancés vont de Lead à traiter à Proposition remise, sans qualification/découverte/Show Boond enregistrés. Les 21 formalités finalisées font partie des 26 signatures. À la dernière version : 26 signés, 15 ouverts, 7 perdus, 3 abandonnés, 1 non qualifié. Source UP §1–4, preuves Q1–Q4 ; pas nouvelle exécution.

**Questions à l’utilisateur pour le case :**

1. Quelles étapes comparer dans le funnel upsell ? Faut-il adopter le parcours court observé comme convention du case ou seulement comme constat ? L’entrée est fixée à création Boond ; Show Boond et un formulaire retrouvé ne sont pas des conditions d’inclusion déduites de la décision.
2. **Montant résolu pour le case échange 23 :** retenir le supplément vendu (100 → 150 = 50 €/mois). Reste la donnée source, le périmètre des objectifs et la catégorie New MRR/expansion mentionnée dans la réponse ; voir la clarification de nomenclature et RAW-E23-01.
3. Quelle preuve relie un upsell à une hausse effective d’abonnement, à quelle date et pour quel montant ? Le signé upsell et l’expansion active sont déjà distingués ; il manque leur rattachement concret, à vérifier dans les données sans inventer de preuve.
4. Les coefficients du funnel nouvelles ventes conviennent-ils aux upsells ? QM-05 en porte la validation. La couverture HubSpot est-elle attendue pour ces dossiers ou faut-il assumer des périmètres distincts dans les comparaisons ?

**Limites de preuve.** Une signature nouvelle vente antérieure est observée pour chaque société, sans prouver un abonnement actif à la création de l’upsell. Aucun deal HubSpot non archivé ni projet actuel ne leur est relié par les clés contrôlées. Cela ne prouve pas l’absence d’impact : une extension peut modifier un projet existant. Les démos présentes sur le contact ne sont pas attribuables automatiquement à l’upsell. **Dépendances :** U01–U03, M01–M07, U06/U07/U11 et objectifs selon périmètre.

<a id="qc-12"></a>
### QC-12 — Churn : cas multiples, réactivations et réconciliation mensuelle

**État : conventions principales résolues pour le case à l’échange 22 ; trois questions réelles conservées en raw.**

- Société active = au moins un abonnement en cours à clôture (DU-31).
- Réactivation après churn incluse dans New MRR, hypothèse DU-32 ; pas de deuxième ajout Réactivation.
- Net par société entre clôtures, DU-33. Les variations des lignes se compensent à l’intérieur d’une société, jamais entre sociétés. Conserver les détails.
- Départ-retour dans le même mois hors périmètre de l’analyse du case, DU-34 ; pas absence d’événement prouvée.

Les [formules communes R03](intent_ia.md#mrr-client-cloture) séparent entrants, sortants et restants. Le churn MRR comprend le MRR de la clôture précédente des sortants et la baisse nette des restants. Le compteur des clients en baisse porte sur les restants avec baisse nette, sans chevauchement avec les sortants à cette clôture.

**Encore ouvert pour le case :** critères d’activité des lignes, pauses/gratuités, continuité et corrections rétroactives, comparabilité des clôtures, preuve des identités et date de couverture. Retour dans le KPI « nouveaux clients » au sens première acquisition non tranché par le choix de New MRR. Ne pas relancer la granularité société ou l’inclusion monétaire des retours.

**Questions de pratique réelle à poser :** [RAW-E22-01](../raw_intent/questions_metiers.md#raw-e22-01), [RAW-E22-02](../raw_intent/questions_metiers.md#raw-e22-02), [RAW-E22-03](../raw_intent/questions_metiers.md#raw-e22-03). Leur statut reste « à confirmer métier », pas « résolu en production ».

**Dépendances :** U05/U07/U10–U13, QM-04, QC-10/QC-11. Source : échanges 5–6 puis 22 points 4–7. Une réconciliation inexpliquée ne devient pas une perte par défaut.

<a id="qc-13"></a>
### QC-13 — Détail explicatif de la baisse du MRR

**État : besoin retenu, convention de comptage fixée pour le case par DU-33/DU-34 à l’échange 22.**

Compter les sociétés actives aux deux clôtures dont le **MRR total baisse entre clôtures**. Calcul U11-C : nombre distinct de ces sociétés. Les sortants constituent une population distincte U10 ; les pertes monétaires U11-D/U11-B ne se chevauchent pas dans cette lecture.

Une baisse de ligne compensée par une hausse supérieure chez la même société ne compte pas comme client en baisse pour le case. Le détail reste conservé pour une analyse future. Le traitement brut des mouvements ligne par ligne est à confirmer en réalité dans RAW-E22-02 ; les départs-retours intra-mois sont hors périmètre du case.

**Encore ouvert :** seuil d’alerte « en masse » (QC-03), critères d’activité et corrections (QM-04/QC-12). La demande de distinguer départs et réductions reste acquise depuis l’échange 6.

<a id="qc-14"></a>
### QC-14 — Comparaison individuelle et équipe : règles et faisabilité

**Établi.** Une feuille dédiée est souhaitée, hors synthèse (échanges 8–9). Les dossiers/actions ont un responsable, les ressources décrivent les collaborateurs et les business units leurs membres, avec des versions. Cela rend l’analyse envisageable, sans certifier une attribution historique complète. Les objectifs restent ceux des équipes.

**Questions restantes — utilisateur.** Quelles mesures comparer pour une personne ? La référence d’équipe doit-elle être un total, une moyenne par membre éligible, une médiane ou une distribution ? Comment traiter les transferts, membres multiples, périodes de présence et comptes techniques ? Pour une durée d’étape couvrant deux responsables, répartit-on le temps ou attribue-t-on le passage selon une convention unique ?

**Conséquence.** U14, données d’attribution temporelle et datasets individu/équipe. Pas de classement ni d’objectif personnel ajouté automatiquement. La faisabilité des liens et de l’historique sera contrôlée pendant l’implémentation, sans transformer une absence de rattachement en performance nulle. [table des champs et correspondances ClickHouse](correspondance_champs_clickhouse.md), groupe R ; aucune architecture retenue.

## 6. Dépendances et prochaines itérations

| Famille | Déjà décidé | Reste à spécifier |
| --- | --- | --- |
| Périmètre et parcours | Conserver les types, séparer nouveaux clients et upsells | Entrée création Boond décidée échange 22 ; populations par mesure QC-01, workflow QM-01 et montants upsell QC-11 restent ouverts |
| Démo | Deux grains et deux durées ; sous-parcours secondaire souhaité | RDV tenus pour cible décidé ; preuve, chaînage et rattachement société QC-02 (grain décidé échange 23) ; durées QC-03 |
| Revenus | Boond actif ; fin de mois sans prorata ; signé/New MRR/churn retenus ; paiements exclus | État signature et conventions churn tranchés pour le case ; états des abonnements, montants signés, corrections et premières acquisitions encore ouverts |
| Pondération | Signature finale, somme des produits | Source, valeurs et histoire QM-05 |
| Objectifs | Fin de mois, équipes Sales | Réalisés compatibles QC-09 et leurs questions dédiées |
| Attribution | Conventions proposées de DU-23 | Champ canal QM-02 ; mapping équipes et codes Inbound QC-05 |
| Histoire et conservation | Versions raw présentes ; cinq ans d’agrégats | Couverture/dates/corrections QC-10 ; rétention détaillée QC-07 ; fraîcheur QC-06 |
| Validation du case | L’utilisateur tranche, QM-03 close | Aucune attente de validation externe pour poursuivre |

Après l’échange 24, la nomenclature New MRR/expansion est résolue : Upsell est une composante filtrable de New MRR. Les données sources du supplément signé et les critères d’activité des abonnements restent à préciser. Le grain société de Nb In demo et le montant supplémentaire de l’upsell sont décidés. La frontière création Boond et le compteur de RDV réellement réalisés sont décidés. Elle organise les questions, sans sélectionner la livraison. Les décisions et les deux versions de chaque document sont mises à jour ensemble. Toute réponse partielle ne ferme que les points effectivement tranchés.

<a id="questions-simples-echange-21"></a>
### Questions simples présentées à l’échange 21 — première série

**Réponses reçues à l’échange 22 :** 1 résolue pour l’entrée ; 2 réalisé/stock décidés, identité In demo encore ouverte ; 3 événement résolu, montant non répondu ; 4 société active décidée, critères de ligne ouverts ; 5 hypothèse retour inclus en New MRR ; 6 calcul net client pour le case ; 7 hors scope case et question réelle conservée ; 8 portefeuille global sans filtre équipe. Voir DU-28 à DU-35. Les formulations ci-dessous sont conservées comme questions posées, pas comme toutes encore ouvertes.

Cette série concerne les définitions qui changent directement les chiffres de la synthèse. Elle reformule les questions existantes, sans créer de nouvelles décisions ni remplacer le registre complet. Leur statut actuel est celui indiqué dans le bilan de l’échange 22 ; une réponse partielle ne résout que le point explicitement traité. Les vérifications de données, de clés et de couverture historique restent à la charge de l’analyse technique.

1. **À quel moment un dossier entre-t-il dans le pipeline que nous mesurons ?** Une fiche peut exister dans Boond avant d’être réellement qualifiée. Quel événement doit marquer son entrée : qualification validée, première démo, ou un autre événement ? Pour les upsells, qui suivent un parcours différent, quel serait ce point de départ ? Cela fixe le volume et le montant de pipeline généré. Références : QM-06, QC-11. La cohorte de création CRM demandée reste distincte.

2. **Que doit compter le KPI « Nombre de démos » comparé à l’objectif ?** Compte-t-on les séances planifiées ou celles effectivement réalisées ? Un prospect qui reçoit une première démo puis une démo complémentaire représente-t-il une ou deux démos pour cet objectif ? Cela fixe le compteur à utiliser, sans le confondre avec le nombre d’opportunités dans l’étape Démo. Référence : QC-02.

3. **Quand reconnaît-on une signature, et quel montant lui attribue-t-on ?** Compte-t-on la vente dès « Signé — formalités à finaliser », ou seulement à « Formalités finalisées » ? Pour le MRR signé, quel montant mensuel fait foi à cette date ? Exemple d’upsell : un abonnement passe de 100 à 150 €/mois ; le MRR signé de cette vente doit-il être 50 € ou 150 € ? Le passage entre les deux statuts ne sera pas compté comme deux ventes. Références : QM-04, QC-11.

4. **Qu’est-ce qu’un client actif à la fin du mois ?** Peut-on retenir : une société ayant au moins un abonnement en cours à la clôture ? Comment traiter les abonnements en pause ou gratuits ? Si une société arrête un abonnement mais en conserve un autre, reste-t-elle un client actif, avec uniquement une perte de MRR ? Cela détermine le nombre de clients actifs et les départs. Références : QM-04, QC-12.

5. **Le New MRR correspond-il uniquement à la première activation d’un nouveau client ?** Un ancien client qui revient doit-il entrer dans le New MRR ou dans une catégorie « Réactivation » ? Et un abonnement supplémentaire chez un client déjà actif doit-il toujours être classé en expansion ? Cela permet de séparer nouveaux clients, retours et développement des clients existants. Références : QM-04, QC-12.

6. **Faut-il mesurer les hausses et baisses abonnement par abonnement, ou sur le total de chaque client ?** Exemple : un même client augmente un abonnement de 100 € et réduit un autre de 40 €. Veux-tu afficher 100 € d’expansion et 40 € de churn MRR, ou seulement 60 € d’expansion nette pour ce client ? Le principe acquis reste que les gains ne compensent pas les pertes entre clients ; il manque ici le niveau de détail à l’intérieur d’un même client. Références : QC-12, QC-13.

7. **Que fait-on des départs et retours à l’intérieur d’un même mois ?** Un client présent fin janvier part le 10 février puis revient le 20 février au même montant. Veux-tu montrer un départ et une réactivation en février, ou aucun mouvement puisqu’il est présent aux deux clôtures ? Les photographies de fin de mois sans prorata restent acquises ; la question porte sur les événements à montrer en complément. Référence : QC-12. Les mêmes conventions devront ensuite couvrir une arrivée suivie d’un départ avant clôture.

8. **Le filtre équipe doit-il aussi agir sur le bloc MRR actif et churn ?** Ce bloc décrit le portefeuille d’abonnements, alors que le reste décrit l’activité commerciale. Veux-tu le garder global ou le répartir par équipe ? Si tu souhaites une répartition, à quelle équipe rattacher l’abonnement : celle qui a vendu, celle qui gère actuellement le client, ou une autre ? Cela évite d’attribuer arbitrairement un départ client à une équipe commerciale. Référence : QC-05, revue de couverture de la maquette à l’échange 20.

**Séries suivantes, conservées ouvertes :** canaux et regroupement Inbound ; probabilités retenues et périmètre des objectifs ; populations et transitions du funnel ; calcul des durées et seuils de stagnation ; comparaison individuelle/équipe ; présentation des corrections historiques et rétention détaillée. Les autres cas particuliers du registre ne sont ni supprimés ni implicitement tranchés par cette première série.

## 7. Propositions de restitution visuelle

**MAQ-01 — Synthèse et onglets d’approfondissement.** Première maquette et note/prompt produits à la demande de l’échange 7. **Disponibilité :** `maquettes/dashboard_synthese_v1.png` et `maquettes/dashboard_synthese_v1.md` sont absents lors de la vérification de l’échange 13 ; ils ne sont pas recréés. La V2 reste disponible ci-dessous. **Statut initial : proposition IA de présentation, à discuter.** La demande utilisateur autorisait sa création, sans valider automatiquement son organisation. Tous les chiffres étaient fictifs ; les points ouverts restaient ouverts. Filtre de type proposé localement au pipeline, périmètre abonnements affiché séparément. Les indicateurs non affichés dans la synthèse restent au catalogue. Le suffixe v1 désignait une version graphique, pas une sélection de livraison.


**MAQ-02 — Tunnel central et blocs conservés.** [Maquette v2](maquettes/dashboard_synthese_v2.png), [note/prompt](maquettes/dashboard_synthese_v2.md). L’échange 8 garde objectifs/réalisé et MRR/churn et demande un tunnel unique ; l’échange 9 accepte cette base pour V1. Les modes proposés sont Opportunités, Taux de passage, Montants, Durées ; seuls la demande d’un sélecteur et le principe du tunnel sont explicites, pas les formules de tous ces modes. Les autres analyses ne sont pas supprimées du catalogue.

**ARCH-01 — Proposition retirée.** La première architecture et son visuel, produits à l’échange 9, sont retirés à la demande explicite de l’échange 10. Aucun de leurs modèles proposés n’est retenu. L’historique de l’échange reste dans le journal ; la démarche a ensuite suivi DCI-10 à DCI-13, puis la nouvelle demande DCI-14.

**ARCH-02 — Nouvelle proposition après inventaire du staging.** [Modèle intermédiaire, faits et dimensions](architecture_modele_proposition.md), accompagné d’un visuel interactif dans l’échange 15. Statut : proposition IA autorisée par DCI-14, pas décision de construction. Les grains, champs principaux, relations, couverture KPI et dépendances ouvertes sont documentés. Aucune table DTR ni modification dbt/SQL/service.

**ARCH-03 — Vue statique d’ensemble.** [Image](maquettes/architecture_vue_ensemble_v1.png) générée à l’échange 16 à la demande de l’utilisateur. Vue des trois couches et des dimensions communes, quatre domaines visibles simultanément. Noms/grains raccourcis ; aucune jointure détaillée ni architecture physique prétendue. DCI-15 remplace la présentation interactive comme support principal de revue.

**ARCH-04 — Schéma relationnel.** Échange 17 : demande utilisateur d’une lecture relationnelle complémentaire. [Schémas, clés et cardinalités](architecture_modele_proposition.md#schema-relationnel), par domaine. Les cardinalités sont des cibles logiques sur clés résolues, pas des observations validées en base. Les liens incertains, rôles de dates/étapes et jointures de détail sont distingués des chemins d’agrégation. Les clés de tranches des liaisons sont proposées explicitement ; aucune nouvelle règle métier ni contrainte physique n’est prétendue.

**ARCH-05 — Architecture modulaire révisée.** [Image statique V2](maquettes/architecture_modulaire_v2.png), échange 18. Deux modules frères, démo intégrée au pipeline et extension locale, dimensions/identités communes. Le schéma de l’échange 16 reste conservé mais son organisation en quatre bandes est remplacée. Les clés des schémas relationnels sont maintenues ; leurs sous-vues sont rattachées aux deux modules. Aucun DTR, modèle physique ou déploiement créé.

**ARCH-06 — Deux vues détaillées par module.** Échange 19 : [Pipeline](maquettes/module_pipeline_detail_v1.png), [Revenus et performance](maquettes/module_revenus_detail_v1.png). Même structure : informations préparées, fait et grain métier, KPI obtenus. Les deux images affichent l’historisation sur toute la chaîne ; aucune nouvelle mesure ou règle métier manquante n’est validée par leurs formules abrégées.


**MAQ-03 — Durées par étape.** Échange 29 : [image](maquettes/dashboard_durees_etapes_v1.png), [note et prompts](maquettes/dashboards_durees_cohortes_v1.md). Approfondissement au grain opportunité × passage, applicable à toute étape, exemple Démo. Terminé et en cours séparés ; médiane/P90, seuil >21 jours, classes, période d’entrée et calendrier sont des propositions. Données fictives, aucune preuve de calculabilité nouvelle. Dépendances B01/U03/M08, QC-03/QC-10 et attribution historique.

**MAQ-04 — Cohortes commerciales.** Échange 29 : [image](maquettes/dashboard_cohortes_v1.png), [note et prompts](maquettes/dashboards_durees_cohortes_v1.md). Reprend B02 : opportunités groupées par mois de création et ouvert/gagné/perdu à J+30/J+60/J+90. Zoom juin/J+60 et canal, maturité visible. La règle J depuis chaque création et l’affichage après maturité complète sont proposés, pas validés. Classement des autres états et absence d’observation restent ouverts ; aucune renormalisation silencieuse des inconnus. Dépendances QC-10/QM-01, QM-02/QC-05. Ni les images ni leurs chiffres fictifs ne ferment ces questions.
