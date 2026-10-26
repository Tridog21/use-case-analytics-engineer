# Questions à poser aux métiers

Cette liste conserve les arbitrages explicitement confiés au métier. Les questions sont préparées pour la restitution : aucun message n’a été envoyé et aucune réponse n’est présumée. Référence : [questions et réponses de cadrage](raw_intent.md), Q2, Q13, Q14, Q15 et Q16. Dernier état : réponses du cycle 3 ; Q10 reportée au prochain cycle.

## QM-01 — Passages entre étapes

- **Origine :** Q13, suggestion IA retenue puis explicitement confiée au métier par l’utilisateur au cycle 1.
- **Statut :** à poser.
- **Interlocuteurs proposés, non confirmés :** responsables Sales et commerciaux, avec la VP Sales pour les arbitrages transversaux.
- **Question :** quel est le workflow réel des besoins ? Peut-on sauter une étape, revenir en arrière, rouvrir un deal fermé ou revenir depuis nurturing ? Comment distinguer attente, refus, perte et abandon ?
- **Pourquoi cela compte :** population du pipe ouvert, conversions, dates d’entrée/sortie, durées et cohortes dépendent de ces règles. La séquence illustrée dans le cycle ne prouve pas un ordre obligatoire.
- **Appui documentaire :** `docs/cycle-de-vie.html`, lignes 98–114 ; `docs/model/model.json`, ligne 917, distingue `active` (encore en cours) et `isEnabled` (étape proposée dans l’interface).
- **Réponse et décision :** en attente.

## QM-02 — Plusieurs canaux

- **Origine :** Q14, question IA retenue sur le passage d’un prospect par plusieurs canaux, confiée au métier au cycle 1.
- **Statut :** à poser.
- **Interlocuteurs proposés, non confirmés :** Marketing et responsables Sales.
- **Question :** lorsqu’un prospect passe par plusieurs canaux, quel canal reçoit le crédit pour l’acquisition du contact puis pour l’opportunité ? Retient-on un seul canal ou un partage ? À quel moment fixe-t-on cette attribution ?
- **Pourquoi cela compte :** lecture des performances par canal, cohérence Sales/Marketing et prévention du double comptage. Premier formulaire, dernière source connue et origine du besoin ne désignent pas automatiquement la même attribution.
- **Appui documentaire :** `docs/model/model.json`, lignes 132–146 et 1220–1247 ; aucune règle commune d’attribution n’y est fournie.
- **Réponse et décision :** en attente.

## QM-03 — Définitions communes et arbitrage

- **Origine :** Q16, proposition IA de gouvernance conservée et complétée par l’utilisateur : préférer des définitions synchronisées entre équipes.
- **Statut :** à poser.
- **Interlocuteurs proposés, non confirmés :** VP Sales, Marketing et Finance, avec Data pour documenter les définitions et leurs traductions.
- **Question :** qui valide les définitions partagées et qui tranche en cas de conflit Sales/Marketing ou entre équipes ? Comment valide-t-on les règles puis les résultats du cockpit ?
- **Pourquoi cela compte :** éviter que démo, opportunité, MRR ou conversion aient plusieurs significations non explicitées. Aligner les mots communs n’interdit pas des indicateurs différents pour des usages différents, à condition de les nommer clairement.
- **Appui documentaire :** `README.md`, lignes 38, 53–59 et 67 ; maquette Pipeline, zones 1, 3, 4 et 8. Aucun arbitre final ou protocole de validation complet n’y est formalisé.
- **Réponse et décision :** en attente.

<a id="qm-04--mrr-début-fin-prorata-et-paiements"></a>

## QM-04 — MRR : début, fin, prorata et paiements

- **Origine :** Q2, hypothèse utilisateur sur le MRR « réel », le New MRR, la preuve d’encaissement et l’exemple d’un abonnement du 15 mars au 15 avril ; clarification IA distinguant portefeuille actif, facturation, revenu reconnu et encaissements.
- **Statut :** à poser ; aucune convention n’est validée.
- **Interlocuteurs proposés, non confirmés :** Finance et responsable des abonnements/facturation, avec Sales/Marketing pour les usages et Data pour la traduction.
- **Question principale :** pour un abonnement qui commence le 15 mars et se termine le 15 avril, quelle est la date de fin effective du service et de la facturation ? Y a-t-il prorata, remboursement ou mois commencé dû ? Comment répartit-on le revenu de service entre les deux mois et comment distingue-t-on cette répartition du MRR observé à chaque clôture ?
- **Conventions complémentaires à confirmer :**
  - Un abonnement entre-t-il dans le MRR à sa signature, au début effectif du service ou au premier paiement ? Distingue-t-on MRR signé et MRR activé ?
  - La date de résiliation indique-t-elle la demande ou la fin effective ? `endDate` est-elle inclusive, exclusive, et peut-elle indiquer un renouvellement ou un changement d’offre plutôt qu’un churn ? Quel fuseau et quel instant de clôture utiliser ?
  - Quels états de projet/ligne permettent d’identifier un abonnement actif ? Comment traiter essais, gratuités, pauses, impayés et annulations ?
  - Quels montants mensuels HT retenir après remises, avec quelles règles de devises ? `averageDailyPriceExcludingTax` est-il déjà égal à la quantité multipliée par le prix unitaire mensuel ?
  - Souhaite-t-on aussi mesurer le revenu reconnu et les encaissements ? Quelles sources de factures, avoirs et règlements permettent de les calculer et de les rapprocher des abonnements ?
  - Le New MRR désigne-t-il les nouveaux clients activés, les signatures ou la croissance nette incluant extensions, réductions, réactivations et churn ?
- **Pourquoi cela compte :** ne pas appliquer un prorata de facturation au MRR de clôture, ne pas confondre signature et activation, et ne pas qualifier les lignes d’abonnement de preuve de paiement. Une résiliation demandée et une résiliation effective peuvent appartenir à des mois différents.
- **Appui documentaire :** `docs/cycle-de-vie.html`, étape de démarrage du client ; `docs/model/model.json`, description et colonnes de `raw.deliveries`. Montant mensuel et période sont documentés ; les règles de prorata, de paiement et de résiliation ne le sont pas.
- **Réponse et décision :** en attente. La photographie en fin de mois est une proposition IA, pas une réponse du métier.

### Complément du cycle 2 — décision de source et exemple de répartition

**Dernière précision utilisateur :** distinguer MRR actif, MRR signé, New MRR et « MRR encaissé (ou chiffre d’affaire) » dans sa formulation. Boond devient la source de référence du MRR actif, via les lignes d’abonnement de `raw.deliveries` et les projets de `raw.projects`. Cette décision ne valide pas encore les états actifs, les bornes de période ou la preuve de paiement.

**Question de répartition à poser, à partir de l’exemple utilisateur :** pour un client qui s’abonne le **15 mars** et résilie le **15 avril**, quelles périodes sont effectivement couvertes ? Applique-t-on un prorata entre mars et avril, une mensualité complète rattachée à un mois ou une autre règle ? Quel montant relève de la photographie de MRR actif à chaque date, du montant facturé, du revenu rattaché au service et des paiements réellement reçus ? La question reste ouverte ; le fait d’utiliser Boond ne permet pas de choisir une règle de facturation.

**Précisions attendues du métier :**

- Quels états et quelles dates rendent une ligne active ? La fin du 15 avril est-elle une demande de résiliation ou une fin effective ? Le statut du projet ajoute-t-il une condition ?
- Quel événement constitue le MRR signé et à quelle période le rattacher ? Comment distinguer signature et démarrage ?
- Le New MRR correspond-il aux nouveaux clients uniquement, à toute nouvelle contribution active ou à une autre règle ? Comment nommer extensions, réactivations, réductions et variation nette ?
- Quelles données prouvent les règlements et permettent de les rapprocher des abonnements ? Le modèle fourni n’apporte pas cette preuve. « Encaissements mensuels » et chiffre d’affaires reconnu ne sont pas automatiquement synonymes.
- Si un scénario sans churn et sans New MRR est souhaité, que mesure-t-il exactement et comment traite-t-il les autres mouvements ? Ce scénario ne sera pas assimilé à un encaissement garanti.

**Suivi :** source Boond retenue pour le MRR actif ; états, dates, prorata, autres conventions et paiements **à poser / à confirmer** avant implémentation. Les mesures de paiements restent conditionnées à une source appropriée. Aucune règle financière ou convention de clôture n’est déduite du seul exemple.

## QM-05 — Sens des probabilités

- **Origine :** Q15, cycle 3. L’utilisateur interprète les coefficients comme une probabilité de passage à la prochaine étape ; le modèle les décrit comme une probabilité de signature par étape et par équipe. Cette question explicite le désaccord plutôt que de choisir silencieusement une interprétation.
- **Statut :** à confirmer avec le métier / cabinet ; pas de calibration ou de signification réelle validée.
- **Interlocuteurs proposés, non confirmés :** cabinet auteur des coefficients, VP Sales et responsables Sales ; Data pour documenter la définition et vérifier son usage.
- **Question :** que représente exactement `ref.stage_probabilities.probability` : la probabilité d’atteindre l’étape suivante, la probabilité de signer depuis l’étape actuelle, ou une autre convention ? Quelle population, quelle période et quelle méthode ont produit ces valeurs ? Quel usage est prévu dans le pipeline pondéré et qui les valide ?
- **Pourquoi cela compte :** une probabilité de transition et une probabilité de signature finale ne sont pas interchangeables pour pondérer le montant d’une vente. Elles sont aussi distinctes d’une cible mensuelle et d’un taux d’atteinte d’objectif.
- **Preuve documentaire :** [modèle](../../docs/model/model.json), ligne 1457 : « Probabilité de signature par étape du besoin et par équipe, proposée par le cabinet externe » ; ligne 1487 : « Probabilité de signature, entre 0 et 1 ». Grain : étape × segment/équipe, ligne 1458. Maquette Pipeline, zone 4 : montant × probabilité du stage et audit des win rates à challenger avec la VP Sales.
- **Décision conservée :** les quatre objectifs de `ref.sales_targets` sont des cibles mensuelles par équipe et indicateur. Ils ne sont pas des probabilités et aucun lien direct automatique avec un coefficient n’est posé. La restitution actuelle est stratégique, équipe/global ; aucun objectif individuel n’est inventé.
- **Réponse et décision :** en attente. La documentation reste citée pour son sens déclaré ; la lecture « passage au prochain stage » reste une interprétation utilisateur à confirmer.

## QM-06 — Entrée dans le pipeline qualifié

- **Origine :** Q10 ; demande utilisateur d’un état des lieux complet, sans présumer une réponse ferme.
- **Statut :** à poser ; aucune frontière qualifiée n’est choisie par le diagnostic.
- **Question :** qu’est-ce qui valide la qualification du besoin, et quel événement marque son entrée dans le pipeline qualifié : qualification réussie, découverte, démo planifiée, démo réalisée ou autre validation ? Distingue-t-on cette entrée de la création CRM ?
- **Conséquences à arbitrer :** date des opportunités générées, cohortes, début des durées, nurturing, anciens états, réentrées et dossiers sans passage observable. Les sauts et retours sont également suivis dans QM-01.
- **Interlocuteurs proposés, non confirmés :** VP Sales et responsables Sales, avec Marketing pour la comparaison des populations et Data pour la traduction.
- **Constat :** le cycle crée le besoin en état 0, la maquette fait démarrer l’opportunité à la démo, le SQL inclut des états avant démo et nurturing. `active` et `isEnabled` ne désignent pas une qualification acquise.
- **Éléments de réponse préparés :** [diagnostic Q10](etat_des_lieux_Q10.md), chiffres, sources et requêtes reproductibles. L’absence de passage observé ne prouve pas l’absence de l’événement réel.
- **Réponse et décision :** en attente.

## Suivi

Les interlocuteurs ci-dessus sont des propositions de l’IA, pas une organisation validée. Lors d’une réponse, conserver la formulation reçue, l’auteur ou l’instance qui arbitre, la décision et ses conséquences pour les indicateurs. Ne pas transformer l’absence de réponse métier pendant le case en validation implicite.


<a id="complements-echange-22"></a>
## Compléments demandés pendant le clean intent — échange 22

Ajout explicitement demandé par l’utilisateur, points 5, 6 et 7. Les sections précédentes conservent leur état historique ; les règles actuelles du case sont dans le [registre clean](../clean_intent/questions_decisions.md#du-28). Les questions ci-dessous restent à poser aux métiers dans une situation réelle. Les conventions de travail ne sont pas des définitions officielles Boond.

<a id="raw-e22-01"></a>
### RAW-E22-01 — Comment classer le retour d’un client après churn ?

**Question :** lorsqu’une société a arrêté tous ses abonnements puis revient, son MRR doit-il être classé en New MRR ou dans une catégorie Réactivation séparée ? Faut-il aussi la compter parmi les nouveaux clients, ou distinguer première acquisition et retour ?

**Pourquoi :** cela change la lecture de l’acquisition et la décomposition de la croissance ; le même apport ne doit pas être compté deux fois.

**Pour le case :** l’utilisateur retient l’hypothèse que le retour contribue au **New MRR**. Il ne tranche pas explicitement le compteur de premières acquisitions. **Statut réel : à confirmer métier.** Liens : clean QM-04/QC-12, U07/U13, DU-32 ; [message source](../clean_intent/ia_assistant_story.md#echange-22).

<a id="raw-e22-02"></a>
### RAW-E22-02 — Mesurer les variations par abonnement ou par société ?

**Question :** un client augmente une ligne de 100 €/mois et réduit une autre de 40 €/mois. Veut-on afficher 100 € d’expansion et 40 € de contraction, ou seulement 60 € d’expansion nette au niveau du client ? Comment distinguer un remplacement d’abonnement d’une vraie hausse ou baisse ?

**Pourquoi :** le calcul net décrit l’évolution totale du client, mais masque des baisses compensées entre ses lignes ; un calcul brut exige de reconnaître les continuités pour éviter les faux mouvements.

**Pour le case :** comparaison du **MRR total par société** entre deux fins de mois ; dans l’exemple, expansion de 60 € et churn MRR nul pour ce client. Les gains d’autres sociétés ne compensent pas les pertes de celle-ci. Le détail des lignes reste conservé. **Statut réel : à confirmer métier.** Liens : clean QC-12/QC-13, U11, DU-33.

<a id="raw-e22-03"></a>
### RAW-E22-03 — Montrer les départs et retours à l’intérieur du mois ?

**Question :** une société active fin janvier part le 10 février puis revient le 20 février au même montant. Faut-il afficher un départ et une réactivation dans le mois, ou uniquement la variation entre clôtures, qui ne montre aucun mouvement dans cet exemple ?

**Pourquoi :** deux clôtures ne décrivent pas tous les événements du mois ; les compteurs de départs et de retours diffèrent selon la lecture. La même question devra être examinée pour une arrivée suivie d’un départ avant clôture.

**Pour le case :** l’utilisateur exclut le traitement détaillé du scénario départ-retour intra-mois, jugé trop spécifique. Les clôtures restent observées ; l’historique source n’est pas effacé. **Statut réel : à poser ; non résolu. Statut case : hors périmètre explicite.** Liens : clean QC-12, DU-34.


<a id="raw-e23-01"></a>
## RAW-E23-01 — Valeur et nom du MRR apporté par un upsell

**Ajout demandé par l’utilisateur, échange 23.** Si un abonnement passe de 100 à 150 €/mois, faut-il retenir le supplément de 50 € ou le total de 150 € pour le montant commercial signé de cet upsell ? Comment ce supplément est-il ensuite classé lors de l’activation : Expansion MRR séparée, ou composante d’un New MRR défini plus largement ? Quel événement et quelle donnée prouvent le montant mensuel supplémentaire vendu ?

**Pourquoi :** ne pas recompter l’abonnement initial, ne pas confondre engagement signé et hausse active, et ne pas additionner le même apport dans New MRR et Expansion.

**Convention du case :** l’utilisateur retient **50 € supplémentaires**, pas 150 €. Sa réponse utilise aussi « 50 euros en new mrr » : l’intention sur le libellé reste à clarifier par rapport à la séparation New MRR/Expansion retenue précédemment. Le montant est décidé ; la nomenclature ne l’est pas encore.

**Statut réel : à confirmer métier.** Le choix de 50 € pour le case n’attend pas cette confirmation externe. [Décision et question clean](../clean_intent/questions_decisions.md#du-37) · [message intégral](../clean_intent/ia_assistant_story.md#echange-23).


### Suivi de RAW-E23-01 — décision du case à l’échange 24

L’utilisateur précise explicitement que **l’upsell est inclus dans New MRR**, avec possibilité de filtrer par **New ou Upsell**. La question de nomenclature ouverte à l’échange 23 est donc résolue pour le case : total New MRR = New + Upsell. Le retour après churn reste dans la composante New, conformément au choix antérieur. L’upsell de 100 à 150 €/mois contribue pour 50 € supplémentaires, lorsqu’il est actif pour le calcul de revenu.

La confirmation de la pratique réelle reste à poser aux métiers ; ce statut ne bloque pas la convention du case. Ne pas ajouter Expansion une deuxième fois au total New MRR. [Décision actuelle DU-38](../clean_intent/questions_decisions.md#du-38) · [message intégral](../clean_intent/ia_assistant_story.md#echange-24).
