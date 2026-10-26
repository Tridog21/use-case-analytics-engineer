# Raw intent — consignes et découverte du besoin

## 1. Informations connues

### Contexte et utilisateurs

Boond édite un ERP/CRM SaaS destiné aux ESN et aux sociétés de conseil. Le sujet porte sur le pilotage du pipeline commercial dans un parcours d’acquisition B2B, de la demande d’un prospect à l’abonnement client. La VP Sales porte la demande de cockpit, préparée avec un cabinet externe. Le dashboard Pipeline est le livrable demandé ; le cycle de vie sert à en comprendre le contexte, sans présumer que toute l’acquisition sera couverte par la V1. [S1]

| Équipe / acteur | Informations connues | Origine et portée |
| --- | --- | --- |
| Sales | Utilisateurs directs. Trois équipes : **SMB, Large Accounts et Espagne**. Utilisent Boond comme CRM. | Cadrage utilisateur et README. Équipes, segments et pays ne sont pas automatiquement équivalents. |
| Marketing | Utilisateurs directs selon le cadrage utilisateur. Travaille dans HubSpot. Aucune subdivision à retenir à ce stade. | Cadrage utilisateur ; le README ne décrit pas de sous-équipes marketing. |
| VP Sales | Demande un délai de livraison et porte la proposition initiale de cockpit. | README. |
| Data | Construit la réponse au besoin : cadrage, proposition de dashboard et modélisation. | README. La formulation utilisateur « Equipe Data est au mieux. » reste à préciser ; aucun rôle supplémentaire n’en est déduit. |
| Produit | Peut être concerné si des pertes de conversion proviennent du produit. | Hypothèse du cadrage utilisateur ; hors périmètre. Aucune cause produit établie. |
| Tech | Peut être concerné si des pertes proviennent des automatisations ou de la plateforme. | Hypothèse du cadrage utilisateur ; hors périmètre. Aucun incident établi. |

La finance est également citée dans le README parmi les interlocuteurs joignables : elle peut contribuer à des arbitrages, sans être ajoutée aux utilisateurs directs définis par le cadrage. [S1]

### Systèmes et circulation de l’information

- **HubSpot** reçoit les formulaires et porte la vision marketing des contacts et des deals.
- **Boond** porte les sociétés, contacts, besoins/opportunités, actions commerciales, projets et lignes d’abonnement.
- Les **automatisations** transmettent les demandes vers Boond et recopient des informations des besoins vers HubSpot.
- Les données Boond arrivent dans **ClickHouse** par un flux en temps réel. Dans les tables `raw`, une ligne représente une version d’un enregistrement ; `meta.ts` date la version et `meta.deleted` indique une suppression.
- **dbt** sert aux transformations. **Superset** est l’outil de restitution de l’entreprise, mais ne sera pas utilisé dans cet exercice. [S1, S5]

Il s’agit du fonctionnement documenté, sans validation à ce stade de la complétude, de la qualité ou de la synchronisation des données chargées.

### Désalignements déjà identifiés

| Sujet | Versions présentes dans les sources | Statut |
| --- | --- | --- |
| Ouverture du besoin | Le cycle de vie ouvre le besoin à « Lead à traiter », avant qualification et démo. La maquette fait démarrer l’opportunité à la démo, associée à la création du besoin. | Divergence explicitement signalée dans le README ; à arbitrer. |
| MRR | Un responsable Sales parle du montant signé sur le deal Boond ; le marketing parle du montant du deal HubSpot. Le cycle décrit aussi des lignes d’abonnement avec montant mensuel et période. | Définitions à réconcilier ; aucune équivalence entre ces montants n’est retenue. |
| Démo | Passage du deal en « Show Boond » pour un commercial ; actions d’agenda « Démo 1 » et « Démo complémentaire » pour un autre. | Événement et comptage à définir. |
| CRM de référence | La maquette laisse ouverte la référence Boond ou HubSpot pour les deals. | À décider ; ne pas additionner les deux visions sans règle. |

Sources : [S1, S2, S5].

## 2. Intention de travail et hypothèses de départ

**Intention exprimée par l’utilisateur :** comprendre le parcours de conversion et ses points de déperdition pour aider les équipes concernées à augmenter la part des entrants qui deviennent clients.

Le cycle de vie est envisagé comme un **tunnel global**, dont chaque étape peut comporter un **micro-tunnel**, ou ne pas en comporter. Cette grille de lecture vient de l’utilisateur et est désormais explicitée par les deux supports de `cycle_hypotheses/` : vue globale du parcours et décomposition par étape. Des sorties commerciales, incidents de transmission ou attentes peuvent survenir au fil du parcours ; ils ne représentent pas la même forme de déperdition. [S6, S7, S8]

La conversion de 100 % des entrants en clients est un **idéal théorique**, explicitement considéré comme impossible par l’utilisateur. Elle donne une direction de travail ; elle n’est ni une cible chiffrée validée ni un critère de réussite du dashboard.

Pour définir des indicateurs, il faudra préciser l’unité suivie, la population d’entrée, l’événement de conversion et l’horizon de mesure. Le terme « personnes » ne permet pas encore de choisir entre contacts, sociétés, demandes et opportunités ; ces objets ne sont pas considérés comme interchangeables.

Le dashboard doit aider à localiser les pertes et explorer leurs causes possibles. Une baisse de conversion ne suffit pas à démontrer une cause marketing, commerciale, produit ou technique.

## 3. Cycle de vie documenté et reformulation exploratoire

### 3.1. Socle fourni dans le case

Cette séquence reprend `docs/cycle-de-vie.html`. Elle est conservée comme référence, en regard de la reformulation exploratoire présentée ensuite. La source mélange étapes commerciales et échanges entre systèmes : ses dix étapes ne sont pas automatiquement dix niveaux du futur tunnel analytique. [S5]

| Ordre dans la source | Étape | Informations principales |
| --- | --- | --- |
| 1 | Formulaire rempli | Site, LinkedIn ou Meta ; création ou mise à jour du contact HubSpot avec formulaire et paramètres de campagne. |
| 2 | Transmission dans Boond | Contact retrouvé ou créé ; action « Demande de démo » avec paramètres de campagne dans son texte. |
| 3 | Prise en charge commerciale | Attribution à un commercial ; ouverture du besoin à « Lead à traiter ». |
| 4 | Premier contact et qualification | Appels consignés comme actions ; passage en « Qualification ». |
| 5 | Rendez-vous de découverte | Exploration du contexte ; passage en « RDV découverte ». |
| 6 | Démo | Actions « Démo 1 » puis éventuellement « Démo complémentaire », rattachées au contact ; passage en « Show Boond ». |
| 7 | Proposition | Montant estimé et date de signature prévue ; « Proposition remise », puis « Projet validé » et « Closing ». |
| 8 | Issue du deal | « Signé », « Perdu » ou « Abandonné » ; raison en cas de perte. Possibilité de « Nurturing » pour un prospect pas encore prêt. |
| 9 | Répercussion dans HubSpot | Copie de l’état et des dates du besoin vers le pipeline de deals lu par le marketing. |
| 10 | Démarrage du client | Création du projet et de lignes d’abonnement portant montant mensuel et période. |

La position 9 de la synchronisation dans la source ne démontre pas qu’elle intervient uniquement après fermeture du deal. « Nurturing » ne sera pas assimilé à une perte définitive sans règle explicite.

### 3.2. Les deux supports du candidat

- **Parcours global et frictions** : [version interactive](cycle_hypotheses/01-parcours-et-frictions.html) et [version PDF](cycle_hypotheses/01-parcours-et-frictions.pdf). La vue principale va du formulaire envoyé au deal signé ; elle distingue le contrôle de synchronisation HubSpot et le prolongement vers la vie client.
- **Tunnels par étape** : [version interactive](cycle_hypotheses/02-tunnels-par-etape.html) et [version PDF](cycle_hypotheses/02-tunnels-par-etape.pdf). Ce support détaille dix étapes, avec sous-parcours, frictions possibles, questions et mesures conditionnelles.

Ces supports reformulent les croquis du candidat. La [trace de création](cycle_hypotheses/trace-creation.md) précise qu’un travail éditorial assisté par IA a également ajouté des questions et mesures candidates. Leur présence dans les supports ne constitue donc pas une validation métier de toutes les propositions. Le [fichier structuré des hypothèses](cycle_hypotheses/hypotheses-source.json) permet d’en retrouver le détail. [S6–S9]

**Règle de lecture : les largeurs des tunnels sont schématiques. Elles ne représentent ni volumes, ni taux, ni attrition mesurés.**

### 3.3. Hypothèses par étape et découverte associée

Les identifiants H01 à H10 reprennent la numérotation des supports. Les sous-étapes et causes ci-dessous restent des propositions à confronter au métier et aux données. [S7, S8]

| Repère | Reformulation / hypothèse | Friction possible | À vérifier avant de mesurer |
| --- | --- | --- | --- |
| H01 — Acquisition / collecte | Communication affichée → CTA affiché → CTA cliqué → formulaire commencé → envoyé → contact créé ou mis à jour. L’amont du formulaire est ajouté au cycle fourni. | Abandon avant envoi ou échec de collecte après envoi. | Existence des impressions, clics et débuts de formulaire, identifiants de rapprochement. Un envoi peut mettre à jour un contact existant. |
| H02 — Arrivée dans Boond | Demande transmise → contact retrouvé ou créé → action « Demande de démo » enregistrée. Le « lead créé » du croquis désigne ici une demande traçable, pas une nouvelle table. | Demande absente, doublon ou retard de transmission. | Clé reliant soumission, contact et action ; délai de réception acceptable. Les contacts uniques ne sont pas le dénominateur des demandes. |
| H03 — Attribution | Demande à attribuer → attente → responsable identifié → besoin « Lead à traiter » pris en charge. Le statut intermédiaire « pending » reste hypothétique. | Blocage ou retard de prise en charge ; une perte commerciale n’est pas attendue du seul fait de l’attribution. | Horodatages d’attribution et de prise en charge, traitement des demandes sans responsable. Besoin créé ne signifie pas opportunité qualifiée. |
| H04 — Contact / qualification | Tentative de contact → échange abouti → qualification effectuée → lead qualifié selon une règle à définir. Joignabilité et qualification sont distinctes. | Coordonnées inutilisables, prospect injoignable, inadéquation ou refus. | Preuve d’un échange réussi, critères de qualification, distinction attente/refus. Plusieurs appels ne représentent pas plusieurs prospects ; « lead froid » n’est pas un statut confirmé. |
| H05 — Découverte / RDV | Lead qualifié → proposition de rendez-vous → rendez-vous accepté et planifié → découverte réalisée → poursuite vers une démo. | Refus de rendez-vous ou absence de suite après découverte. | Découverte et démo sont-elles distinctes ? Quel événement fait entrer dans le pipeline qualifié ? La frontière reste ouverte. |
| H06 — Démo | Démo programmée → première démo tenue → proposition envisagée ; une démo complémentaire est facultative. | No-show ou refus de poursuivre après la démo. | Preuve de tenue effective, sens de « Show Boond », rattachement de l’action au bon besoin et traitement des reports. Actions d’agenda et besoins ayant eu une démo sont deux grains différents. |
| H07 — Proposition | Préparation → remise → projet validé → closing, avec possibilité de sauts ou de retours entre étapes. | Erreur de chiffrage, inadéquation de l’offre ou rupture du processus. | Preuve de remise et ordre réel des étapes. Ce schéma ne résout pas la définition du montant ou du revenu mensuel. |
| H08 — Issue | Signature, perte et abandon sont des issues alternatives ; nurturing correspond à une attente possible, avec retour à examiner. | Perte ou abandon commercial ; motifs à qualifier. | Statuts terminaux, réouvertures, motifs et traitement du nurturing. Ne pas lire ces issues comme une chaîne « Signé → Perdu → Abandonné → Nurturing ». |
| H09 — Synchronisation HubSpot | État et dates Boond → transmission → deal HubSpot mis à jour → concordance vérifiée. Contrôle transversal, hors conversion commerciale. | Deal absent, état obsolète, dates incohérentes. | Identifiant de liaison, fréquence, délai et règles de mise à jour. Un écart de synchronisation ne prouve pas la perte du prospect. |
| H10 — Activation / rétention | Deal signé → projet et lignes créés → abonnement actif. Le suivi client et le churn prolongent le cycle fourni à titre hypothétique. | Incident de démarrage, puis éventuelle résiliation ; deux phénomènes distincts. | Preuve du démarrage et sens d’une fin de ligne : renouvellement, changement d’offre ou résiliation. Une ligne mensuelle ne prouve pas un paiement ; plusieurs lignes peuvent relever d’un projet. |

### 3.4. Conséquences pour l’intention et les futures mesures

Trois lectures doivent rester distinctes :

1. **Conversion commerciale** : progression, décisions de poursuite et issues du prospect ou du besoin.
2. **Contrôle opérationnel** : réception, attribution, synchronisation et délais. Les étapes H02, H03 et H09 ne supposent pas une attrition normale ; une attente n’est pas automatiquement une perte.
3. **Activation et rétention** : passage du signé à l’abonnement actif, puis suivi client. Le churn est une extension exploratoire et n’élargit pas automatiquement la V1 Pipeline.

Les supports proposent des pistes de mesure conditionnelles :

- **Acquisition** : envois / débuts de formulaire, uniquement si les événements sont suivis ; les seuls contacts ne permettent pas de calculer ce taux.
- **Transmission et attribution** : demandes reçues ou attribuées dans le délai / demandes éligibles ; suivi séparé des retards et des demandes en attente.
- **Qualification et rendez-vous** : prospects joints / contactés, puis qualifiés / joints ; rendez-vous réalisés / rendez-vous prévus, avec déduplication et fenêtres comparables.
- **Démo et signature** : démos tenues / démos prévues arrivées à échéance ; taux de gain à définir sur une population de deals clos, en explicitant abandons et réouvertures.
- **Synchronisation et activation** : concordance des deals avec les besoins à synchroniser ; démarrages / deals signés dont le démarrage est attendu à la date d’observation. Rétention et churn doivent ensuite être définis séparément.

Ce sont des **candidats à la spécification**, pas des KPI déjà validés ou calculés. Grain, dates, rattachements et maturité des cohortes restent à établir. Les taux locaux ne seront pas multipliés pour produire un taux global sans vérifier la continuité des populations. Les causes produit ou technique restent des hypothèses explicatives, sans ajout de travaux pour ces équipes au périmètre actuel.

## 4. Demande et consignes issues des documents

### Attentes de pilotage

La maquette cherche à suivre la constitution et la santé du pipeline : volume, conversion, valeur et stagnation. Elle constitue une **proposition à challenger**, pas une spécification figée. [S1, S2]

| Besoin proposé | Contenu à retenir pour le cadrage |
| --- | --- |
| Objectif versus réalisé | Comparer le pipeline généré à un objectif. |
| Opportunités générées et en cours | Suivre les volumes par source/canal et segment. |
| Pipeline total et pondéré | Suivre la valeur ouverte et la valeur pondérée par des probabilités de signature. |
| Pipeline coverage | Mettre en regard le pipeline prévu en clôture sur le mois et l’objectif du mois. |
| ADV / MRR potentiel | Préciser la signification et les règles de cet indicateur proposé. |
| Deals stagnants | Suivre volume et montant des deals sans changement de stade depuis un seuil à définir. |

La maquette prévoit des lectures individuelles, par équipe et globales, avec des filtres segment, individu, canal et période. Plusieurs blocs sont « à valider » ou en « question ouverte ». Probabilités par stade, stagnation et certains indicateurs de revenu restent à arbitrer. [S2]

L’expression de besoin ajoute l’historique des changements de stade, les cohortes d’opportunités par période de création avec suivi ouvert/gagné/perdu à J+30, J+60 et J+90, et l’évolution historique du pipeline pondéré. Elle décrit une solution d’attente par snapshots quotidiens manuels et historisation append-only. Ces évolutions peuvent être livrées après la mission du cabinet ; cela ne les rend pas automatiquement obligatoires dans la V1 du case. [S3]

### Travaux attendus dans le case

1. **Communication et organisation** : rédiger les messages qui seraient envoyés, en précisant destinataires, canal, moment et objectif ; proposer un ordre de réalisation et un délai en réponse à « Je l’ai quand ? ». Il s’agit de messages documentés, sans envoi réel.
2. **Maquette du dashboard Pipeline** : proposer onglets, filtres et graphiques, avec leur forme et la question traitée ; outil libre.
3. **Modélisation dans `dbt/`** : alimenter une V1 dont le périmètre est choisi et justifié.
4. **Requête actuelle** : examiner son sens et son comportement sur de gros volumes, puis décider de son devenir. À ce stade, elle a uniquement été lue. [S1, S4]

La requête legacy se présente comme un reporting hebdomadaire par équipe des deals en cours, montants de pipe et signatures, utilisé au point pipe du lundi. Cette description ne valide pas le sens effectif de ses agrégations. [S4]

### Contraintes de travail et de rendu

- Rendu trois jours après l’accès au dépôt, à la même heure. L’heure d’accès n’étant pas établie ici, aucune échéance absolue n’est déduite.
- Aucun retour métier prévu pendant le case : documenter hypothèses et questions pour la restitution.
- Privilégier des éléments aboutis et justifiés ; aucun volume minimum ou maximum imposé.
- Restitution de 1 h 30, dont 30 à 40 minutes de présentation.
- Conserver la trace des échanges avec l’IA et vérifier ses propositions. Dans ce chat : messages utilisateur intacts et interventions IA brièvement résumées.
- Le README prévoit un dépôt privé ou un bundle pour le rendu. Le cadrage utilisateur impose de ne rien publier, pousser ou envoyer sans instruction explicite.
- Dossier de rendu : `orest_case_output/`. Modèles et fichiers techniques restent aux emplacements appropriés du véritable projet.
- Préserver versions verrouillées, modifications préexistantes et volume Docker. Aucun démarrage de service n’est nécessaire pour ce travail documentaire.

## 5. Découverte à poursuivre et points à clarifier

| Point ouvert | Pourquoi il compte | Suite attendue |
| --- | --- | --- |
| Reformulation du tunnel reçue | Les supports S6 à S8 précisent le parcours global et les micro-tunnels. | Hypothèses intégrées en section 3 ; vérifier les sous-étapes et leur mesurabilité avant de figer le tunnel. |
| Rôle de Data | « Equipe Data est au mieux. » est ambigu. | Préciser l’intention de cette formulation. |
| Entrée, sortie et unité du tunnel | Déterminent populations, dénominateurs et taux. | Définir objets suivis et rattachements, sans supposer un parcours univoque. |
| Ouverture du besoin | Modifie volumes, cohortes et lecture de l’amont. | Arbitrer l’écart entre cycle de vie et maquette. |
| Démo, MRR et ADV | Ne désignent pas encore des mesures partagées. | Distinguer événements et montants ; expliciter les conventions retenues. |
| Sources de référence et synchronisation | Les systèmes représentent différemment un même parcours. | Vérifier les correspondances et choisir les références par usage. |
| Événements marketing et délais de prise en charge | Les supports ajoutent des événements et états non confirmés dans les données. | Vérifier la disponibilité du suivi amont, des demandes individuelles et des dates d’attribution ; définir les délais attendus. |
| Branches, retours et maturité des cohortes | Une attente, un report ou une démo facultative ne sont pas une perte définitive. | Définir nurturing, réouvertures, no-shows et fenêtres de mesure ; ne pas imposer un parcours strictement linéaire. |
| Activation, rétention et churn | Prolongement hypothétique au-delà du pipeline commercial. | Définir événements et grain client/projet/ligne ; décider séparément de leur éventuelle inclusion dans une future version. |
| Historique disponible | Conditionne ancienneté de stade, cohortes et pipe passé. | Vérifier ce que les versions `raw` permettent de reconstituer. L’absence d’historique natif Boond ne prouve pas son impossibilité dans ClickHouse. |
| Pondération et stagnation | La maquette demande des arbitrages explicites. | Définir probabilités et seuils ; ne pas transformer les exemples en règles validées. |
| Périmètre et délai de V1 | La réponse peut dépasser la reproduction du tableur. | Prioriser après clarification de l’intention et vérification de faisabilité. |

**État de la découverte :** les sources du case S1 à S5 ont été consultées, dont la maquette visuelle. Les supports HTML, les dix hypothèses structurées et leur trace éditoriale S6 à S9 ont ensuite été lus ; les versions PDF sont référencées comme supports de restitution, sans nouvel audit de leur mise en page. Aucune requête n’a été exécutée sur les données ; aucun résultat chiffré, diagnostic de qualité, arbitrage métier ou modèle dbt n’est validé par ce document. Les observations documentaires, le cadrage utilisateur et les hypothèses sont distingués ci-dessus.

## 6. Sources de référence

| Référence | Document | Utilité |
| --- | --- | --- |
| S1 | [README](../../README.md) | Contexte, équipes, divergences et attentes du case. |
| S2 | [Maquette Pipeline](../../docs/besoin/maquette-pipeline.png) | Proposition de cockpit, indicateurs, filtres et arbitrages ouverts. |
| S3 | [Expression de besoin](../../docs/besoin/expression-de-besoin.md) | Historisation, cohortes et évolution du pipeline pondéré. |
| S4 | [Requête actuelle](../../legacy/pipeline_actuel.sql) | Point de départ pour comprendre et évaluer le reporting existant. |
| S5 | [Cycle de vie](../../docs/cycle-de-vie.html) | Interactions métier et écritures dans les systèmes. |
| S6 | [Parcours global et frictions](cycle_hypotheses/01-parcours-et-frictions.html) | Reformulation du candidat : parcours global, frictions et contrôles transversaux. |
| S7 | [Tunnels par étape](cycle_hypotheses/02-tunnels-par-etape.html) | Sous-parcours hypothétiques, branches, questions et mesures candidates. |
| S8 | [Hypothèses structurées](cycle_hypotheses/hypotheses-source.json) | Détail des dix étapes, hypothèses, risques, conditions de mesure et limites. |
| S9 | [Trace de création des supports](cycle_hypotheses/trace-creation.md) | Origine dans les croquis du candidat et apports éditoriaux assistés par IA. |

Ce document prépare la formulation de l’intention et de la future spécification. Il sera enrichi au fil des découvertes ; il ne vaut pas spécification validée.


## 7. Précision de l’intention — premier cycle de questions

**Statut : questions ouvertes, réponses à construire lors de la prochaine itération.**

Le bloc des informations connues est clos pour cette itération. Les sections précédentes sont conservées en l’état. Les questions de l’utilisateur sont reprises sans correction ni réponse ajoutée. Les suggestions de l’IA retenues par l’utilisateur figurent dans une sous-section distincte.

### Questions de l’utilisateur

1\. Sur quel période on a besoin de garde l'historique des données? Est ce que cette duré est différant entre marketing et Sales ?

2\. C'est quoi la formue du MRR? Ou est et de combien est la differance entre MRR Boond(Sales) et MRR Hubsport(market)? C'est quoi la formule qui existe aujourd'hui dans le code SQL?  Laquel est la plus logique a utilisé?

3\. C'est quoi la définition exacte de Demo et de quoi elle se compose ? (plusieurs demo, peut etre funnel que j'avais préciser?)

4\. C'est quoi le périmetre exhaustive de ce que les métiers ont besoin d'avoir comme informations, analyse, granularité,KPI?

&#x20;  1\. A tacler dans un 2eme temps, qu'est ce qu'on a réellement comme données? (étape spec)

5."L'équipe sales sort aujourd'hui ses chiffres de pipe avec [\`legacy/pipeline_actuel.sql\`]" Et l'équipe marketing elle fait l'analyse comment ?&#x20;

6. [`legacy/pipeline_actuel.sql` ] Il faut decomposer le code et comprendre exactement ce qu'est fait dedans.&#x20;
7. Des contraintes RGPD / consent particulier sur le pipe ?
8. Est ce que toutes les équipes ont besoin des updates au même moment et tous les jours ? Refresh + critical/non critical.
9. "- **\*\*Historisation des changements de stage des opportunités\*\*** : Boond n'expose pas nativement un historique des mouvements de stage. Sans ça, impossible de calculer proprement l'ancienneté d'un deal dans son stage actuel (deals stagnants) ou de reconstituer une cohorte." Ce passage a garder en tête car il faut inclure un KPI pas seulement de conversion, mais aussi il y a un besoin d'anlayse de duré de vie dans les differantes étapes du pipe.A garder and tete et inclure dans les specs model + dash.
10. "Tu verras que la maquette et [\`docs/cycle-de-vie.html\`]\(docs/cycle-de-vie.html) ne situent pas l'ouverture du besoin au même moment. Ce n'est pas une coquille : c'est une vraie question chez nous". Je ne comprends pas cette phrase et qu'est ce qu'elle veut dire.&#x20;


### Suggestions de l’IA retenues par l’utilisateur

**Origine : suggestions de l’IA, retenues par l’utilisateur pour approfondir le cadrage.** Cette sélection valide leur pertinence, sans apporter de réponse ni fixer de règle métier. Elle reprend les suggestions initiales 1, 2, 4, 7 et 8, ainsi que la seule question sur le passage par plusieurs canaux dans la suggestion 6. Les suggestions 3 et 5 ne sont pas ajoutées.

1. **Quelles décisions le dashboard doit-il permettre de prendre ?** Pour la VP Sales, les managers, les commerciaux et le marketing : quelle action doit découler de chaque constat ? Lesquelles sont prioritaires en V1 ?

2. **Qu’est-ce qu’on compte dans le tunnel ?** Une personne, une société, une demande ou une opportunité ? Comment traiter plusieurs demandes d’un même contact ou plusieurs opportunités d’une même société ?

3. **Quelles sont les règles de passage entre étapes ?** Peut-on sauter une étape, revenir en arrière ou rouvrir un deal ? Comment distinguer nurturing, abandon, perte et simple attente ?

4. **Que fait-on lorsqu’un prospect passe par plusieurs canaux ?**

5. **Comment sont définis les objectifs et les probabilités de signature ?** Qui les fixe, à quelle granularité, et sur quelle base ? Les montants comparés ont-ils la même définition ?

6. **Qui arbitre les définitions et valide le résultat ?** Qui tranche un désaccord Sales/Marketing ? Quels exemples, rapprochements et critères permettront de déclarer les chiffres fiables et la V1 livrable ?


## 8. Réponses — cycle 1

Les questions originales de la section 7 et les informations connues sont conservées. La numérotation Q1 à Q10 désigne les questions initiales ; Q11 à Q16 désigne les six suggestions IA retenues, dans leur ordre de présentation. Les formulations ci-dessous sont des synthèses lisibles des précisions utilisateur ; les messages originaux sont conservés dans l’historique.

Les statuts distinguent une décision de cadrage de l’utilisateur, une hypothèse de travail, un fait documentaire et une réponse encore attendue. Un point reporté ou confié au métier ne devient pas résolu.

### Q1 — Profondeur d’historique et conservation

- **Source documentaire :** cohortes mensuelles suivies à J+30/J+60/J+90 : S3, lignes 9–16. Ces horizons ne fixent pas la durée de conservation.
- **Hypothèse IA conservée :** distinguer la profondeur utile à l’analyse et la conservation des données détaillées.
- **Précision utilisateur :** conserver **cinq ans de données agrégées au niveau data mart** pour comparer plusieurs saisonnalités. Une profondeur supérieure semble moins pertinente au regard de l’évolution importante du produit : après trois à cinq ans, le contexte peut rendre les analyses anciennes moins comparables. Cette justification est un choix de cadrage utilisateur, pas une propriété mesurée du produit.
- **Point encore ouvert :** conservation du staging et des intermédiaires selon contraintes légales, volumétrie, coût et besoin potentiel de backfill. L’agrégation n’est pas assimilée automatiquement à une anonymisation ; l’articulation avec Q7 reste à définir avant implémentation.
- **Statut :** choix des cinq ans retenu pour le cadrage ; conservation détaillée ouverte.

### Q2 — MRR

- **Source documentaire :** définitions concurrentes Sales et Marketing dans S1, lignes 53–55 ; montant estimé HT du besoin dans le modèle, lignes 108–111 ; montant HubSpot, lignes 1337–1340 ; montant mensuel des abonnements, lignes 1144–1177.
- **Hypothèse IA :** distinguer valeur de pipeline, nouveau revenu mensuel signé et revenu mensuel des abonnements actifs ; aucune formule métier n’est retenue à ce stade.
- **Précision utilisateur :** question critique, reportée au cycle 2 ; y ajouter la définition classique du MRR.
- **Point encore ouvert :** usage attendu, formule, dates, périmètre et écart Sales/Marketing.
- **Statut :** ouvert — cycle 2.

### Q3 — Démo : action et phase du parcours

- **Source documentaire :** S1, lignes 57–59, oppose passage en « Show Boond » et actions « Démo 1 » / « Démo complémentaire ». S5, lignes 107–109, décrit une action liée au contact et l’évolution du besoin.
- **Hypothèse IA reformulée :** une **action de démonstration** est une séance particulière ; la **phase démo du tunnel** est une partie du parcours d’un besoin commercial et peut contenir plusieurs actions. Compter les séances et compter les besoins ayant franchi la phase répond à deux questions différentes.
- **Précision utilisateur :** cette distinction correspond à son intention. Deux définitions seront potentiellement nécessaires, l’une pour le tunnel et l’autre pour l’action. Un même tunnel de démo pourrait comprendre démo 1, démo 2, etc. La mise en œuvre n’a pas encore été examinée.
- **Point encore ouvert :** événements d’entrée et de sortie de la phase, preuve de réalisation d’une séance, rattachement au besoin, reports, annulations et éventuels compléments. Un ordre ou un nombre obligatoire de séances n’est pas décidé.
- **Statut :** orientation confirmée ; règles opérationnelles ouvertes.

### Q4 — Périmètre exhaustif des besoins

- **Source documentaire :** besoins proposés dans S2, zones 1 à 8, et S3, lignes 9–16. La V1 reste à choisir et justifier : S1, ligne 71.
- **Hypothèse IA :** inventorier les besoins métier avant de les confronter à la disponibilité des données.
- **Précision utilisateur :** point critique à traiter au prochain cycle. Le relevé des données réellement disponibles vient dans un second temps, à l’étape de spécification.
- **Point encore ouvert :** informations, analyses, KPI, granularités, utilisateurs, priorités et frontières de la V1.
- **Statut :** ouvert — cycle 2.

### Q5 — Vue Marketing et vue Sales

- **Source documentaire :** S1, ligne 32 ; S5, lignes 116–118.
- **Hypothèse IA :** des rapports HubSpot peuvent être utilisés, mais leur existence et leurs règles ne sont pas démontrées.
- **Précision utilisateur :** conserver la piste précédente mais la reformuler plus simplement pour une confirmation au cycle 2.
- **Reformulation à confirmer :** les Sales travaillent sur les dossiers commerciaux dans Boond ; le Marketing retrouve dans HubSpot les contacts et les deals recopiés depuis Boond. Les deux équipes peuvent regarder un même parcours depuis leurs outils respectifs. Le fonctionnement des outils est décrit ; les analyses exactes du Marketing ne le sont pas.
- **Point encore ouvert :** rapports, filtres, indicateurs et conventions réellement utilisés par le Marketing.
- **Statut :** ouvert — clarification au cycle 2.

### Q6 — Analyse de la requête actuelle

- **Source documentaire :** S4 ; S1, ligne 72.
- **Précision utilisateur :** consacrer un document distinct au code complet, à son explication bloc par bloc, aux KPI/grains/périodes, aux problèmes et aux définitions implicites.
- **Réponse :** se référer à [analyse_pipeline_actuel.md](analyse_pipeline_actuel.md).
- **Limite :** analyse statique et exemples documentaires uniquement ; aucune correction, exécution ClickHouse ou mesure de performance.
- **Statut :** traitement documentaire séparé ; les arbitrages métier révélés par le SQL restent ouverts.

### Q7 — Autorisation de traitement, rôle et rétention

- **Source documentaire :** les consignes du case ne fournissent pas de politique de consentement ou de conservation. Le modèle décrit des données identifiantes, sans preuve de leur cadre juridique.
- **Hypothèse utilisateur pour le case :** les données sont consenties et leur traitement est autorisé. Il distingue les données de la relation commerciale propre à l’entreprise de celles qu’elle traite pour ses clients. Pour le premier périmètre, il retient le rôle de **responsable du traitement** (data controller), par opposition au rôle de sous-traitant (data processor) pour des traitements effectués pour le compte des clients.
- **Précision utilisateur :** proposer **trois ans après le churn pour les clients**, et **trois ans pour les leads**. Garder une approche simple ; l’implémentation de la rétention n’est pas promise dans le temps du case.
- **Hypothèse IA de qualification :** conserver ces règles comme hypothèses explicites du case, sans les présenter comme une conformité juridique vérifiée ni comme une règle universelle pour toutes les finalités. Aucun consentement n’a été contrôlé.
- **Point encore ouvert :** événement de départ du délai des leads, définition du churn et articulation entre données détaillées et agrégats conservés cinq ans. Pour le périmètre de prospection, le référentiel CNIL distingue notamment fin de relation commerciale et collecte/dernier contact venant du prospect ; il ne fixe pas une rétention unique pour tout l’entrepôt.
- **Statut :** hypothèses utilisateur consignées ; modalités et éventuelle implémentation ouvertes.

### Q8 — Granularité, recalcul et fraîcheur

- **Source documentaire :** S1, ligne 34, décrit Boond en temps réel ; le modèle, lignes 1185–1187, décrit les contacts HubSpot recopiés chaque nuit ; S3, ligne 20, mentionne un snapshot manuel quotidien. S4, lignes 60 et 68, agrège les résultats par semaine et équipe. Les objectifs sont mensuels : modèle, lignes 1418–1449.
- **Précision utilisateur :** envisager des lectures jour, semaine et mois et préciser leurs usages lors de l’intention finale puis de la spécification.
- **Hypothèse IA reformulée :** distinguer **période affichée** (jour/semaine/mois), **fréquence de recalcul** et **fraîcheur des sources**. Une série hebdomadaire peut être recalculée tous les jours. Le SQL hebdomadaire ne prouve pas une exécution hebdomadaire exclusive ni un rafraîchissement quotidien de toutes les sources.
- **Point encore ouvert :** calendrier attendu par équipe, heure de disponibilité, retard acceptable et criticité des usages. La phrase utilisateur sur la mise à jour quotidienne reste une compréhension à préciser, pas une propriété confirmée de toutes les sources.
- **Statut :** ouvert — intention finale et spécification.

### Q9 — Durée dans les étapes et stagnation

- **Source documentaire :** S3, lignes 9–16 ; S2, zone 8. Les versions CDC et leur horodatage sont décrits dans S1, ligne 34, et dans le modèle, lignes 38–41.
- **Hypothèse IA conservée :** distinguer ancienneté dans l’étape actuelle, durée des passages terminés ou cumulés et durée totale du cycle. Le CDC pourrait permettre une reconstitution, sous réserve de complétude et de sens des horodatages.
- **Précision utilisateur :** conserver cette réponse ; les KPI de durée sont importants pour les futurs modèles et le dashboard.
- **Point encore ouvert :** règles de calcul en cas de retour, pauses, seuils par étape et différence entre première observation technique et entrée métier réelle. Le seuil « > 30 jours » reste un exemple de la maquette.
- **Statut :** besoin de durée retenu ; définitions détaillées ouvertes.

### Q10 — Moment d’ouverture du besoin

- **Source documentaire :** S2, guide de lecture en haut, situe la création à la démo ; S5, lignes 98–109, l’ouvre à « Lead à traiter », avant qualification et démo ; S1, ligne 49, signale explicitement ce désaccord.
- **Hypothèse IA :** création d’une fiche CRM et reconnaissance d’une opportunité qualifiée peuvent être deux événements distincts. Cette lecture n’est pas prouvée comme pratique réelle.
- **Précision utilisateur :** explication encore non comprise, à reprendre au cycle 2.
- **Point encore ouvert :** frontière métier à retenir et effets sur volumes, conversions et durées.
- **Statut :** ouvert — cycle 2.

### Q11 — Décisions attendues du cockpit

- **Source documentaire :** S2, guide de lecture, vise volume, conversion, valeur et stagnation ; S1, ligne 71, laisse la V1 à argumenter.
- **Hypothèse IA :** relancer certains deals, ajuster l’effort de génération ou revoir une prévision sont des usages possibles, non validés.
- **Précision utilisateur :** question critique reportée au prochain cycle.
- **Point encore ouvert :** décisions visées pour chaque utilisateur et priorités de livraison.
- **Statut :** ouvert — cycle 2, sans choix de priorité imposé.

### Q12 — Unité comptée dans le tunnel

- **Source documentaire :** le besoin est un objet commercial versionné ; il porte un contact principal et une société : modèle, lignes 9–10 et 171–185. Les actions sont des objets distincts : lignes 215 et 324–338.
- **Hypothèse IA :** séparer les compteurs de sociétés, contacts, besoins et actions, sans retenir encore un unique compteur pour tout le cycle.
- **Précision utilisateur :** explication non comprise ; demande d’un exemple plus détaillé. Sa réponse au questionnaire n’a validé aucune unité.
- **Point encore ouvert :** ce que chaque taux doit compter ; l’exemple fictif du cycle 2 servira à expliquer la différence avant tout arbitrage.
- **Statut :** ouvert — clarification au cycle 2.

### Q13 — Règles de passage entre étapes

- **Source documentaire :** S5 décrit un parcours nominal ; le modèle, ligne 917, définit `active` et `isEnabled` sans établir un workflow obligatoire.
- **Précision utilisateur :** poser cette question aux métiers.
- **Réponse :** voir [QM-01 — Passages entre étapes](questions_metiers.md#qm-01--passages-entre-étapes).
- **Point encore ouvert :** sauts, retours, réouvertures, nurturing, attente et perte.
- **Statut :** à poser au métier.

### Q14 — Prospect passant par plusieurs canaux

- **Source documentaire :** le modèle décrit une origine du besoin, lignes 132–146, et plusieurs informations de provenance HubSpot, lignes 1220–1247, sans règle commune d’attribution.
- **Précision utilisateur :** question ouverte à ajouter à la liste métier.
- **Réponse :** voir [QM-02 — Plusieurs canaux](questions_metiers.md#qm-02--plusieurs-canaux).
- **Point encore ouvert :** canal crédité pour le prospect et pour l’opportunité ; éventuel partage d’attribution et risque de double comptage.
- **Statut :** à poser au métier.

### Q15 — Objectifs et probabilités : précisions disponibles

- **Source documentaire — objectifs :** `ref.sales_targets`, modèle lignes 1418–1449 : objectifs du tableur de la VP Sales, au grain **mois × segment × indicateur**. Les segments sont SMB, LA et ES ; les indicateurs sont `mrr_signed`, `pipeline_generated`, `pipeline_weighted`, `demos`. Les montants cibles sont exprimés en euros ; les démos en nombre. Aucun objectif individuel n’est décrit.
- **Source documentaire — probabilités :** `ref.stage_probabilities`, modèle lignes 1457–1487 : coefficients proposés par le cabinet, au grain **étape × segment**, entre 0 et 1. Ils ne sont pas décrits comme des taux de gain mesurés ou approuvés.
- **Constat dans les exemples hors ligne :** `window.MODEL_DATA["ref.sales_targets"]`, dans `docs/model/model.js`, ligne 3, contient pour janvier 2026 / SMB : MRR signé 9 000 €, pipeline généré 36 000 €, pipeline pondéré 27 000 €, démos 60. La table documentaire couvre les mois de 2026.
- **Autre constat documentaire :** au stade `24`, « Show Boond », les probabilités proposées sont **35 % pour SMB, 20 % pour LA et 15 % pour ES**. Ces exemples décrivent les références fournies, sans prouver leur validation, leur calibration ou leur présence inchangée dans la base chargée.
- **Autre convention présente :** Boond possède aussi une pondération saisie par besoin, en pourcentage, et un montant pondéré calculé ; modèle lignes 114–123. La source de pondération retenue pour le cockpit n’est donc pas encore arbitrée.
- **Précision utilisateur :** approfondir les informations disponibles, sans supposer que la réponse métier est déjà connue.
- **Point encore ouvert :** formule exacte de chaque objectif, coefficients à retenir et approbation, application aux périodes passées, allocation individuelle éventuelle. La zone 4 de S2 demande un audit des taux historiques et un échange avec la VP Sales avant de figer les probabilités. Le dénominateur « objectif du mois » de la couverture doit aussi être identifié.
- **Statut :** constats enrichis ; décisions ouvertes au cycle 2 et au métier selon le sujet.

### Q16 — Gouvernance et définitions partagées

- **Source documentaire :** la VP Sales porte le cockpit ; plusieurs zones de S2 prévoient des arbitrages avec elle. S1, ligne 67, cite Marketing, Finance, managers et commerciaux comme interlocuteurs.
- **Hypothèse IA conservée :** VP Sales pour les priorités commerciales, Marketing pour acquisition/attribution, Finance pour les définitions de revenu ; Data documente et vérifie la traduction des règles. Cette répartition n’est pas une organisation officiellement validée.
- **Précision utilisateur :** les définitions doivent de préférence être synchronisées entre équipes. Poser explicitement la question de la personne ou instance qui tranche un conflit.
- **Réponse :** voir [QM-03 — Définitions communes et arbitrage](questions_metiers.md#qm-03--définitions-communes-et-arbitrage).
- **Point encore ouvert :** responsable des définitions partagées, arbitre final et critères de validation des résultats.
- **Statut :** objectif d’alignement retenu ; gouvernance à poser au métier.

## 9. Cycle 2 — explications et questions encore ouvertes

Cette section ouvre le cycle 2 sans réponses imposées. L’utilisateur pourra répondre, commenter ou reporter chacun des points. Les hypothèses du cycle 1 restent identifiées ; une reformulation ne vaut pas validation métier.

### Q2 — Comprendre le MRR avant de choisir un usage

**Définition classique externe :** le MRR représente le revenu récurrent des abonnements, normalisé sur un mois. Exemple fictif : un abonnement de 1 200 € par an représente 100 € mensuels ; un abonnement de 100 € par mois représente également 100 € mensuels. Il ne correspond pas nécessairement à la trésorerie encaissée pendant le mois. Référence : [Stripe — définition et exemple du MRR](https://docs.stripe.com/billing/subscriptions/analytics#monthly-recurring-revenue-mrr). Les conventions précises de Stripe ne sont pas automatiquement adoptées pour le case.

Pour le cockpit, trois questions distinctes se présentent : quelle est la valeur des opportunités encore ouvertes ? Quelle valeur mensuelle vient-on de signer ? Quel revenu récurrent représente le portefeuille actif ? Les documents ne démontrent pas que le montant Boond ou HubSpot répond sans retraitement à ces trois usages.

**À traiter dans ce cycle :** préciser le ou les usages attendus, puis la frontière entre montant estimé, montant signé et abonnement actif. Aucun choix n’est retenu ici et aucun écart chiffré Sales/Marketing n’est annoncé.

#### Complément utilisateur — hypothèse sur le MRR et les encaissements

Formulation originale conservée comme hypothèse à discuter, pas comme définition métier validée :

> Déjà il y a deux choses distinctes: Le MRR réel qu'est le Revenu Recurrent Mensuel que reçoit l'entreprise dans un mois N.  Et le New MRR. C'est le nouveau MRR que l'entreprise a rajouter a son MRR réel durant le mois N.  Donc hypothese le MRR doit se cacluler basé sur l'état des revenu RELLEMENT reçu sur le compte bancaire de l'entreprise le dernier jour du mois. Mais on peut aussi reflechir dans un MRR hypothetique. C'est a dire ce revenu reçu à la fin du mois a condition d'avoir zero churn et zero new MRR. Le churn peut théoriquement arrivé en cours du mois, dans cas je n'ai pas l'information comment se passe le payement et la résilitation. Par exemple un client peut s'abonner le 15 mars et resilier le 15 avril. Dans ce cas comment On repartie le MRR? Au prorata entre deux mois ou on compte 100% pour le mois de mars ou avril et zero pour l'autre mois ? C'est une questions à rajouter dans notre liste de questions. Rensegne tous ce que j'ai dis plus haut dans la repense à la question et rajoute la question de repartition à la liste.

L’utilisateur précise également son intuition : « et au faite ce qui fait le plus foi c'est la ou l'argent tombe sur le compte de l'entreprise toute en fin du cycle de vie. » Il demande à quel événement prendre le montant pour calculer le « MRR réel ».

#### Clarification IA — trois mesures différentes

La banque apporte une preuve d’encaissement. Elle ne prouve pas, seule, la nature récurrente du montant ni la période de service à laquelle il se rapporte. Le solde bancaire à la clôture est encore une autre mesure : il inclut d’autres mouvements, notamment les dépenses.

- **MRR à une date :** valeur mensuelle normalisée du portefeuille d’abonnements retenus comme actifs à cette date. Proposition à valider : une observation à chaque fin de mois. Ce n’est ni une somme des paiements du mois ni une garantie de recette future.
- **Encaissements sur une période :** paiements reçus pendant cette période, avec règles de rapprochement des factures, remboursements et taxes. Leur date peut différer de la période de service.
- **Chiffre d’affaires reconnu sur une période :** revenu rattaché au service fourni selon les règles comptables applicables ; ce n’est pas automatiquement le montant encaissé ou facturé. La Finance doit confirmer ces règles ; aucune écriture comptable n’est proposée ici.

Exemple fictif : 1 200 € HT pour douze mois d’abonnement représentent 100 € de MRR lorsqu’il est actif, même si les 1 200 € sont encaissés en une fois. La normalisation et la photographie du portefeuille ne constituent donc pas une prévision « zéro churn / zéro new MRR ». Une telle prévision peut être un scénario séparé, avec ses propres hypothèses.

**New MRR et croissance nette :** proposition de vocabulaire à valider : réserver New MRR aux nouveaux clients dont l’abonnement devient actif pendant le mois ; distinguer les extensions de clients existants, réactivations, réductions et churn. Le changement net du MRR tient compte de tous ces mouvements, ainsi que d’un éventuel effet de change. Un contrat signé en mars pour un début en avril peut contribuer au « nouveau MRR signé » de mars et au New MRR activé d’avril : deux événements à nommer séparément.

**Exemple de mi-mois :** pour un abonnement de 100 € HT/mois commençant le 15 mars et se terminant effectivement le 15 avril, une convention de photographie à la clôture donne 100 € au 31 mars et 0 € au 30 avril. Avec ces hypothèses, le mouvement est +100 € de New MRR en mars et 100 € de churn MRR en avril. Aucun prorata des jours n’est appliqué à cette photographie. Le montant facturé, le remboursement éventuel, la répartition du revenu de service entre mars et avril et les encaissements sont des calculs distincts. Une demande de résiliation le 15 avril avec fin effective ultérieure ne donnerait pas nécessairement ce résultat.

**Source candidate dans le case, sans validation de données :** `docs/cycle-de-vie.html` décrit au démarrage du client un projet et des lignes avec montant mensuel et période ; le dictionnaire `docs/model/model.json` décrit `raw.deliveries` comme les lignes d’abonnement mensuelles. Malgré son nom, `averageDailyPriceExcludingTax` y porte le prix mensuel ; `startDate`, `endDate` et les attributs de quantité/prix sont documentés. Ces lignes sont une meilleure candidate pour le MRR actif que les seuls montants des deals, à condition de vérifier les statuts, doublons/versions, suppressions, chevauchements, remises et fins effectives. Elles ne démontrent pas un encaissement. Aucune source bancaire, de règlement ou de factures n’est identifiée parmi les tables fournies ; ne pas présenter cet indicateur comme un revenu encaissé ou certifié par la Finance.

**Recommandation IA, non arbitrée :** conserver trois indicateurs explicitement nommés si leur utilité est confirmée : potentiel du pipeline, nouveau revenu mensuel signé, MRR des abonnements actifs en fin de mois. Pour ce dernier, partir des abonnements effectivement en vigueur, plutôt que de la seule signature ou de la date de réception bancaire. La politique d’impayés, le déclenchement à l’activation ou au premier paiement, et les conventions de montant restent à confirmer. L’ajout d’un indicateur d’encaissements nécessiterait une source supplémentaire.

**Questions métier ajoutées :** [QM-04 — début, fin, prorata et paiements](questions_metiers.md#qm-04--mrr-début-fin-prorata-et-paiements). L’hypothèse utilisateur est enregistrée ; la recommandation IA et les conventions de calcul ne constituent pas une validation métier ou une décision d’implémentation.

Références externes de cette clarification : [Stripe — MRR, mouvements et conventions d’activation](https://docs.stripe.com/billing/subscriptions/analytics) ; [ChartMogul — normalisation des factures proratisées](https://dev.chartmogul.com/docs/importing-subscription-data/prorated-invoices/). Les conventions de ces outils ne sont pas automatiquement celles de Boond.

### Q4 — Délimiter le besoin avant la faisabilité

L’inventaire actuel comprend les huit zones de la maquette, les cohortes et l’historique pondéré, ainsi que les durées retenues en Q9. Le dashboard n’a pas encore de périmètre exhaustif validé, surtout pour les besoins propres au Marketing.

**À traiter :** ce que chaque équipe doit pouvoir voir, comprendre et décider ; les KPI et granularités indispensables ; les éléments à reporter. La disponibilité détaillée des données vient après cette clarification.

### Q5 — Deux outils pour suivre un même parcours

**Exemple fictif :** Alice remplit un formulaire ; elle existe comme contact dans HubSpot. Un commercial suit son besoin dans Boond, y consigne les échanges et fait évoluer le dossier. Des informations de ce besoin sont recopiées dans HubSpot. Les Sales peuvent donc consulter le dossier dans Boond, tandis que le Marketing en retrouve une représentation dans HubSpot.

C’est le fonctionnement documenté. En revanche, les consignes ne disent pas quels rapports le Marketing ouvre ni quelles formules il utilise. Une « vue Marketing » complète ne peut donc pas être décrite comme un fait établi.

**À confirmer :** cette explication du même parcours représenté dans deux outils est-elle claire ? Garder ouverte la demande d’un exemple réel du reporting Marketing.

### Q10 — Deux dates possibles derrière le mot « opportunité »

**Exemple fictif :** une fiche besoin est créée le 1er du mois lors de l’arrivée de la demande. La démo a lieu le 10. Le cycle fourni reconnaît une fiche besoin dès le début ; la maquette parle de création d’opportunité à la démo.

Une interprétation possible est que la fiche CRM existe au 1er, mais que l’équipe ne la considère comme opportunité qualifiée que le 10. Cette distinction expliquerait le désaccord sans le résoudre. Si l’on mesure le délai à la signature ou le taux de conversion, choisir le 1er ou le 10 change le résultat.

**À traiter :** comprendre cette différence, puis déterminer plus tard l’événement correspondant à chaque indicateur. Ne pas imposer un événement unique à tous les usages.

### Q11 — Décisions attendues, sans priorité présélectionnée

**À traiter :** quelles décisions le cockpit doit-il permettre à la VP Sales, aux managers, aux commerciaux et au Marketing ? La liste n’est pas réduite à une seule finalité. Les pistes de la maquette — manque de volume, conversion, valeur ou stagnation — sont des points de départ, pas des priorités déjà choisies.

### Q12 — Exemple détaillé des compteurs

**Exemple fictif, sans donnée réelle :** la société Alpha possède deux contacts, Alice et Benoît. Elle porte deux besoins commerciaux indépendants, A et B. Deux séances de démo concernent A et une séance concerne B ; les deux contacts peuvent assister à une même séance.

| Ce qui est compté | Valeur dans cet exemple | Question à laquelle cela peut répondre |
| --- | --- | --- |
| Sociétés distinctes | 1 | Combien d’entreprises sont concernées ? |
| Contacts distincts | 2 | Avec combien de personnes est-on en relation ? |
| Besoins / opportunités distincts | 2 | Combien de dossiers commerciaux suit-on ? |
| Séances de démo | 3 | Combien d’actions de démonstration a-t-on réalisées ? |
| Besoins ayant eu au moins une démo | 2, si les trois séances sont réalisées et correctement rattachées | Combien de dossiers ont atteint cette phase ? |

Ces nombres sont tous cohérents : ils mesurent des objets différents. Deux personnes présentes à une séance ne signifient pas deux séances. Deux séances sur A ne signifient pas deux opportunités. Choisir un compteur pour un KPI ne supprime pas les autres compteurs.

**À traiter :** partir des questions métier avant de définir ce qui entre au numérateur et au dénominateur d’un taux. Aucune réponse à choix forcé ni unité universelle n’est imposée.

### Q15 — Lire séparément les deux référentiels

Un **objectif** est une valeur à atteindre : par exemple 9 000 € de MRR signé pour SMB en janvier 2026 dans le corpus documentaire. Une **probabilité** est un coefficient proposé pour estimer une signature : par exemple 35 % à « Show Boond » pour SMB. Ce ne sont ni le même objet ni le même niveau de détail.

À titre d’illustration arithmétique seulement, un montant comparable de 1 000 € pondéré à 35 % produit 350 €. Cela ne prouve pas que 35 % est correctement calibré, que le montant de 1 000 € serait du MRR, ni que la pondération du cabinet doit prévaloir sur celle du besoin Boond.

**À traiter :** ce que vise chaque objectif, quelle convention de pondération utiliser, qui valide les coefficients, comment les comparer aux résultats et comment traiter les analyses historiques. Une lecture individuelle des objectifs nécessiterait une règle supplémentaire, non fournie par le référentiel mensuel par équipe.

### Autres précisions restant à suivre

| Question | Partie encore ouverte | Suivi |
| --- | --- | --- |
| Q1 | Staging/intermédiaires, backfill et articulation des conservations. | À préciser avant la spécification de la rétention. |
| Q3 | Entrée/sortie de la phase démo et critères des actions. | Orientation à transformer ultérieurement en règles. |
| Q6 | Arbitrages révélés par le document SQL, pas sa correction technique. | Analyse séparée à consulter. |
| Q7 | Départ du délai des leads, définition du churn et détail/agrégats. | Hypothèses du case, modalités ouvertes. |
| Q8 | Jour/semaine/mois, fréquence de recalcul, fraîcheur et criticité. | À préciser pour l’intention finale. |
| Q9 | Définitions des durées, retours et seuils de stagnation. | Besoin retenu ; règles ouvertes. |
| Q13 | Workflow et issues commerciales. | QM-01, à poser. |
| Q14 | Attribution multicanal. | QM-02, à poser. |
| Q16 | Définitions synchronisées, arbitrage et validation. | QM-03, à poser. |

### Références complémentaires de cette itération

- [Modèle de données](../../docs/model/model.json) : lignes 38–41, 108–123, 171–185, 215, 324–338, 917, 1144–1177, 1185–1187, 1220–1247, 1337–1340 et 1418–1487.
- [Corpus documentaire hors ligne](../../docs/model/model.js), ligne 3 : objets `window.MODEL_DATA["ref.sales_targets"]`, `window.MODEL_DATA["ref.stage_probabilities"]` et dictionnaires associés. Les valeurs n’ont pas été comparées à la base chargée.
- [CNIL — durées de conservation en gestion commerciale](https://www.cnil.fr/fr/questions-reponses-sur-les-referentiels-relatifs-la-gestion-des-activites-commerciales-et-des), rubrique sur la prospection : repère externe pour qualifier la portée de Q7, sans validation juridique du case.


## 10. Réponses — cycle 2

Les sections précédentes conservent les étapes de la discussion. Le présent bloc indique le dernier état des décisions de Q2 et Q5 : il remplace, pour ces points, les anciennes mentions « source candidate », « non arbitré » ou « à confirmer » lorsqu’elles sont explicitement levées ci-dessous. Les questions originales, les anciennes hypothèses et les messages utilisateur ne sont pas réécrits.

### Q2 — Quatre indicateurs de revenu à distinguer

**Précision utilisateur :** distinguer **MRR actif / MRR signé / New MRR / MRR encaissé (ou chiffre d’affaire, dans sa formulation)**. La source du MRR actif est désormais choisie. Les conventions qui ne sont pas confirmées restent identifiées comme ouvertes.

| Indicateur demandé | Intention exprimée par l’utilisateur | État de définition |
| --- | --- | --- |
| **MRR actif à une date N** | Valeur mensuelle récurrente des abonnements actifs du portefeuille à cette date. | Concept et source Boond retenus. États et bornes de période à confirmer. Ce montant n’est pas une preuve d’encaissement. |
| **MRR signé** | Valeur mensuelle récurrente engagée commercialement, à distinguer du démarrage de l’abonnement et du paiement. | Indicateur à conserver ; événement de signature, date de rattachement, périmètre et normalisation mensuelle encore à définir. |
| **New MRR pendant le mois N** | Nouveau MRR que l’entreprise ajoute à sa base de MRR actif durant ce mois. | Intention retenue ; préciser les mouvements inclus et la date d’entrée. Ne pas lui imposer sans confirmation la définition limitée aux nouveaux clients proposée auparavant par l’IA. |
| **« MRR encaissé » — libellé utilisateur** | Mesurer ce que l’entreprise a réellement encaissé pendant le mois, en observant la période à sa clôture. | Besoin de suivi des encaissements conservé. La terminologie et les règles restent à préciser ; il ne s’agit pas automatiquement de MRR ni de chiffre d’affaires reconnu. Source de paiements absente du modèle fourni. |

#### Source de référence retenue pour le MRR actif

**Décision de l’utilisateur : utiliser Boond**, à partir de `raw.deliveries` reliée à `raw.projects`. Ce choix n’est plus une simple recommandation IA.

Le modèle documente :

- une ligne de livraison comme une ligne d’abonnement mensuelle : `docs/model/model.json`, lignes 1078–1083 ;
- l’identifiant et les versions/suppressions de la ligne : lignes 1097–1113 ;
- l’état et les dates de début/fin de la période : lignes 1122–1142 ;
- le montant mensuel HT rangé, pour une ligne d’abonnement, dans `averageDailyPriceExcludingTax` malgré le nom générique de ce champ : lignes 1144–1148 ;
- quantité facturée et prix unitaire mensuel dans `attributes` : lignes 1174–1177 ;
- la liaison de la ligne au projet : lignes 1163–1170 ;
- les liens du projet vers le besoin d’origine et la société cliente : lignes 1043–1062.

**Principes de calcul demandés par l’utilisateur, sans implémentation à ce stade :**

1. Conserver la dernière version pertinente de chaque ligne, puis exclure les lignes supprimées. Filtrer les versions supprimées avant d’identifier la dernière pourrait faire réapparaître une ancienne version ; l’ordre logique fait donc partie de l’intention à préserver.
2. Identifier les abonnements actifs à la date d’observation avec leur période et leur état.
3. Additionner leurs montants mensuels HT sans compter plusieurs fois le même abonnement.

**États actifs, sens des dates de début/fin et règles de déduplication métier restent à confirmer avant l’implémentation.** La seule présence d’une ligne ou d’un projet ne suffit pas à décider qu’il est actif. Pour reconstituer une date passée, « dernière version » devra être précisé par rapport à la date observée : le dernier état connu aujourd’hui ne décrit pas nécessairement le portefeuille historique. Les détails seront traités dans la spécification, sans fixer ici de SQL ni de modèle dbt.

#### Pourquoi HubSpot ne fait pas référence pour le MRR actif

**Justification retenue par l’utilisateur et cohérente avec le modèle fourni :** HubSpot décrit contacts et deals, avec origine, montant, étape et dates. Il ne fournit pas ici les lignes d’abonnement ni leur historique de vie après la vente. Un deal gagné ne suffit donc pas à connaître l’activité actuelle d’un abonnement, un changement de montant ou une résiliation. Référence : `docs/model/model.json`, lignes 1293–1410, à comparer aux projets et livraisons, lignes 964–1177.

HubSpot reste utile pour l’acquisition et la conversion commerciale. Dans une certaine mesure, ses deals gagnés sur une période sont plus proches d’un **flux de ventes ou de nouveau MRR signé** que d’un stock de MRR actif. C’est une proximité d’usage, pas une formule déjà validée. Il faut notamment vérifier que `properties_amount`, décrit seulement comme « montant du deal » aux lignes 1337–1340, représente une valeur mensuelle récurrente. Un total contractuel, un montant annuel ou des frais ponctuels ne deviennent pas directement du MRR.

#### Encaissements, chiffre d’affaires et scénario hypothétique

**Intention utilisateur conservée :** suivre les revenus réellement encaissés pendant le mois et observer la période au dernier jour du mois. Cela ne signifie pas ne compter que les paiements du dernier jour ni utiliser le solde du compte bancaire : le mois est une période de flux, tandis qu’un solde est une position à une date.

**Clarification IA, pour éviter une équivalence non démontrée :** les encaissements, le chiffre d’affaires rattaché à une période et le MRR ne sont pas automatiquement égaux. Une vente ou un service peut être payé avant ou après sa période de réalisation. Le libellé utilisateur « MRR encaissé (ou chiffre d’affaire) » est préservé comme besoin exprimé ; l’intitulé de travail **encaissements mensuels** est proposé pour la partie paiement, sans déclarer les règles comptables validées. Références externes : [Insee — chiffre d’affaires](https://www.insee.fr/fr/metadonnees/definition/c1703) ; [Stripe — reconnaissance du revenu et moment du paiement](https://docs.stripe.com/revenue-recognition/methodology).

**Limite documentaire :** les quinze tables décrites dans `docs/model/model.json` ne comprennent pas de source de règlements bancaires ou de paiements rapprochés. Projets et livraisons ne prouvent donc pas un encaissement. Calculer le KPI de paiements nécessiterait une source supplémentaire, à confirmer ; aucune donnée de paiement n’a été inventée ou calculée.

**Autre idée utilisateur conservée :** un scénario de revenu attendu à la fin du mois à partir d’une date N, sous hypothèses de zéro churn et zéro New MRR, évoqué sous le terme de « MRR hypothétique signé ». Ce scénario doit être distingué de la photographie de MRR actif et du MRR effectivement signé. Il ne garantit aucun encaissement. Son éventuelle utilité, son nom et le traitement des autres mouvements — extensions, réductions, réactivations ou changements de prix — restent ouverts. Aucun cinquième KPI obligatoire n’est ajouté au périmètre.

#### Question de mi-mois et questions métier restantes

**Exemple et interrogation utilisateur :** un client s’abonne le **15 mars** et résilie le **15 avril**. Comment répartir le montant entre mars et avril : prorata, mensualité complète rattachée à un des mois ou autre règle ? La date de demande de résiliation doit être distinguée de la fin effective du service et de la facturation.

La question était déjà présente dans [QM-04 — MRR : début, fin, prorata et paiements](questions_metiers.md#qm-04--mrr-début-fin-prorata-et-paiements). Elle est complétée avec la sélection de Boond, les quatre indicateurs et les bornes/statuts à confirmer. **Aucune convention de prorata n’est retenue.** L’exemple de photographie en fin de mois proposé précédemment par l’IA reste une illustration conditionnelle, pas une réponse du métier.

**New MRR reste à préciser :** nouveaux clients seulement ou aussi nouvelles lignes, extensions et réactivations ? Quel événement fait entrer le montant : signature, démarrage ou premier paiement ? La variation nette du MRR peut aussi inclure des sorties et des réductions ; elle ne doit pas être assimilée automatiquement aux ajouts appelés New MRR par l’utilisateur. Ces points sont suivis dans QM-04, sans imposer la convention d’un outil externe.

**Statut de Q2 :** distinction des quatre indicateurs et référence Boond pour le MRR actif retenues. Les montants et conventions ne sont pas implémentés ; statuts, bornes, signature, New MRR, répartition, paiements et scénario éventuel restent à préciser selon les sujets. Aucun écart Boond/HubSpot chiffré n’est établi.

### Q5 — Compréhension du fonctionnement Sales/Marketing confirmée

**Réponse utilisateur :** l’explication précédente est jugée suffisante. Les Sales suivent les dossiers dans Boond et le Marketing en retrouve une représentation dans HubSpot. Sources du fonctionnement : `README.md`, ligne 32 ; `docs/cycle-de-vie.html`, lignes 116–118.

**Hypothèse utilisateur conservée :** il existe potentiellement un désalignement important entre les analyses Sales/Boond et Marketing/HubSpot. Le mot « potentiellement » est important : l’ampleur et les causes de ce décalage n’ont pas été mesurées. Les définitions concurrentes de MRR sont documentées, sans démontrer un montant d’écart à elles seules.

Les rapports précis, filtres et formules réellement utilisés par le Marketing restent non renseignés. Cette limite est conservée ; elle ne rouvre pas la demande de compréhension que l’utilisateur considère suffisante.

**Statut de Q5 :** compréhension suffisante confirmée pour le cadrage. Ne pas reproposer cette même question au cycle 3 ; conserver le risque de désalignement pour le rapprochement et les questions métier.

## 11. Cycle 3 — questions encore ouvertes

Le cycle 2 a apporté des décisions sur Q2 et une confirmation sur Q5. Le cycle 3 reprend **Q4, Q10, Q11, Q12 et Q15**, avec leur contexte, sans rouvrir le choix de Boond pour le MRR actif ni la compréhension de Q5. L’utilisateur peut répondre, préciser ou reporter chacun des points ; aucun choix n’est présélectionné.

### Q4 — Quel contenu métier le cockpit doit-il fournir ?

La maquette propose objectifs/réalisé, opportunités générées et ouvertes, pipeline total et pondéré, couverture des objectifs, revenu potentiel et deals stagnants. L’expression de besoin ajoute cohortes et historique ; l’utilisateur a retenu l’importance des durées et distingué quatre indicateurs de revenu. Cet inventaire n’est pas encore un périmètre de V1 validé.

**Question complète :** quelles informations et analyses sont indispensables pour Sales et Marketing ? À quels niveaux faut-il les lire — global, équipe, commercial, segment, canal, période ? Quels éléments doivent être présents dès la V1 et lesquels peuvent venir ensuite ? L’existence d’un besoin ne prouve pas encore sa faisabilité avec les données ; cette confrontation viendra après la clarification d’intention.

### Q10 — Quand une fiche besoin devient-elle une opportunité qualifiée ?

Le cycle fourni crée un besoin à « Lead à traiter », avant qualification et démo. La maquette associe l’ouverture de l’opportunité à la démo. Le README signale explicitement ce désaccord. Il peut s’agir de deux événements : création de la fiche CRM et reconnaissance d’une opportunité qualifiée ; cette interprétation n’est pas confirmée.

**Exemple fictif :** fiche créée le 1er, démo le 10, signature le 20. Le début retenu change les durées et les populations des taux de conversion.

**Question complète :** faut-il distinguer ces deux événements ? Quel événement fait entrer un dossier dans le pipeline commercial qualifié et lequel sert au comptage des opportunités générées, aux cohortes et au début du cycle ? Une date unique n’est pas imposée à tous les indicateurs.

### Q11 — Quelles décisions le dashboard doit-il permettre ?

Un graphique peut signaler un manque de pipe, des deals stagnants ou un écart d’objectif. Il reste à expliciter ce que chaque utilisateur doit pouvoir faire de cette information.

**Question complète :** quelles décisions la VP Sales, les managers, les commerciaux et le Marketing cherchent-ils à prendre ? Quels problèmes doivent-ils détecter, quelles actions ou discussions doivent en découler, et quels usages sont attendus en V1 ? Relancer des deals, adapter la génération de demandes ou réviser une prévision sont des illustrations possibles, pas des choix déjà faits.

### Q12 — Quel objet compte chaque indicateur ?

**Exemple fictif :** Alpha est une société avec deux contacts, Alice et Benoît. Deux dossiers commerciaux indépendants A et B sont suivis. A donne lieu à deux séances de démo et B à une séance. On obtient une société, deux contacts, deux opportunités et trois actions de démo. Si les séances sont réalisées et correctement rattachées, deux opportunités ont atteint la phase démo.

Ces compteurs peuvent coexister : plusieurs personnes présentes à une séance ne créent pas plusieurs séances ; plusieurs séances pour A ne créent pas plusieurs opportunités. Deux dossiers signés d’une même société ne représentent pas nécessairement deux nouveaux clients.

**Question complète :** pour chaque volume et chaque conversion, veut-on compter sociétés, contacts, demandes, dossiers ou actions ? Quand on parle de conversion après démo, suit-on les besoins ayant eu une démo ou les séances ? Comment traiter les répétitions pour obtenir des populations comparables ? Aucun compteur universel n’est demandé.

### Q15 — Comment utiliser et valider objectifs et probabilités ?

Les objectifs fournis sont mensuels, par équipe et indicateur. Exemple documentaire : SMB, janvier 2026, MRR signé 9 000 €. Les probabilités sont proposées par étape et équipe : à « Show Boond », 35 % pour SMB, 20 % pour LA et 15 % pour ES. Boond possède aussi une pondération saisie sur chaque besoin. Ces informations décrivent les références fournies, sans prouver leur validation ou leur calibration.

**Question complète :** quelle définition de résultat comparer à chaque objectif ? Quelle pondération doit faire référence et qui la valide ? Comment confronter les probabilités aux résultats historiques, et quelle convention appliquer aux périodes passées ? Une lecture des objectifs par commercial est-elle attendue, sachant que la référence disponible est au niveau équipe ?

Sources : `docs/model/model.json`, lignes 114–123 et 1418–1487 ; `docs/model/model.js`, ligne 3, objets `ref.sales_targets` et `ref.stage_probabilities` ; maquette, zone 4. Les exemples n’ont pas été comparés à une exécution de la base.

### Points suivis hors de cette série de réponses

| Point | Décision ou orientation conservée | Ce qui reste ouvert |
| --- | --- | --- |
| Q1 | Cinq ans pour les agrégats du data mart. | Staging/intermédiaires, backfill et articulation des conservations, à préciser pour la spécification. |
| Q2 | Quatre indicateurs distingués ; Boond fait référence pour le MRR actif. | QM-04 : états, bornes, répartition, signature, New MRR, règlements et source de paiement. |
| Q3 | Action de démo et phase du parcours distinguées. | Entrée/sortie de phase, réalisation des actions, reports et compléments. |
| Q5 | Compréhension du fonctionnement confirmée. | Risque de désalignement et connaissance des rapports Marketing, sans relancer la même question de compréhension. |
| Q6 | Analyse statique détaillée livrée. | Arbitrages métier du document ; aucune correction technique décidée. |
| Q7 | Hypothèses de traitement et de conservation du case consignées. | Modalités détaillées, sans validation juridique ou implémentation présumée. |
| Q8 | Lectures jour/semaine/mois envisagées. | Fréquence, fraîcheur, calendrier et criticité, à préciser ensuite. |
| Q9 | Besoin de durées retenu. | Définitions, retours et seuils de stagnation. |
| Q13 / Q14 / Q16 | Questions confiées au métier. | QM-01 / QM-02 / QM-03, à poser. |


## 12. Réponses — cycle 3 et liste exhaustive des souhaits

Les sections précédentes restent l’historique du cadrage. Ce bloc consigne les dernières précisions utilisateur sur Q4, Q12, Q15, Q11 et Q10. Il ne sélectionne aucun périmètre de V1 et n’engage aucune implémentation. La faisabilité, les priorités de livraison et les choix techniques seront examinés dans la spécification.

### Q4 — Inventaire des attentes, sans sélection de livraison

**Décision de méthode de l’utilisateur :** produire une liste exhaustive des souhaits métier, comprenant KPI, objectifs, volumes, analyses, dimensions, granularités et filtres. Ne plus demander à ce stade de choisir ce que la V1 doit contenir. Cette liste décrit les attentes ; elle ne prouve ni disponibilité des données ni formule définitive.

**Lecture stratégique retenue :** global et équipes, avec analyse du tunnel, de la déperdition et des durées. Les demandes individuelles présentes dans la maquette sont conservées pour la traçabilité de l’expression initiale, mais **le pilotage opérationnel par personne et les objectifs individuels ne font pas partie du cadrage actuel**. Ce choix vient de l’utilisateur, pas d’une limitation technique démontrée.

#### Sources et niveaux de statut

| Repère | Source | Ce qu’elle permet d’établir |
| --- | --- | --- |
| W-M | [Maquette Pipeline](../../docs/besoin/maquette-pipeline.png), guide, ligne des filtres et zones 1 à 8 | Indicateurs proposés, formules, formes de restitution et arbitrages ouverts. |
| W-B | [Expression de besoin](../../docs/besoin/expression-de-besoin.md), lignes 9–16 et 20 | Historisation, ancienneté, cohortes et évolution du pipeline pondéré ; dispositif provisoire distinct du KPI. |
| W-O | [Modèle](../../docs/model/model.json), lignes 1418–1449 | Quatre objectifs mensuels par équipe et indicateur, issus du tableur de la VP Sales. |
| W-U | Précisions utilisateur des cycles 1 à 3 | Lecture stratégique, déperdition, cycle de vie, durées, distinctions démo et revenu, sociétés comme rattachement. |
| W-H | [Hypothèses du cycle](cycle_hypotheses/hypotheses-source.json) et [supports](cycle_hypotheses/02-tunnels-par-etape.html) | Mesures candidates sous conditions déjà discutées ; elles ne deviennent pas des demandes validées du métier. |
| W-L | [Requête actuelle](../../legacy/pipeline_actuel.sql), lignes 59–68 ; [analyse](analyse_pipeline_actuel.md) | Mesures actuellement calculées, à ne pas confondre avec des définitions cibles. |

Les mentions « standard », « à valider » et « question ouverte » de la maquette décrivent son statut éditorial. Elles ne constituent pas, à elles seules, une validation métier dans ce chat.

#### A. Les huit blocs explicitement proposés dans la maquette

Les axes transverses de la partie E s’appliquent aux lectures demandées, sous réserve de leur sens métier. Le grain indiqué ici est un grain d’analyse souhaité, pas le schéma d’une future table.

| ID | KPI ou analyse souhaité | Définition / méthode exprimée | Période, axes et grain souhaités | Restitution proposée et statut |
| --- | --- | --- | --- | --- |
| M01 | **Objectif versus réalisé du pipeline** | Pipeline généré / objectif × 100. Montant cible et réalisé nécessaires pour interpréter le taux. | Période sélectionnée, objectif mensuel de référence, équipe/global ; définition du pipeline généré à confirmer. | Jauge de progression, bloc d’ouverture. W-M zone 1 : arbitrage VP Sales. La maquette mentionne aussi une lecture individuelle, hors cadrage actuel. |
| M02 | **Nombre d’opportunités générées par source** | Comptage des deals créés sur la période, regroupés par canal et segment. | Période de création, canal/source, segment/équipe ; global. Le moment de « génération » reste lié à Q10. | Barres par canal, empilées par période. W-M zone 2 : CRM de référence ouvert ; dans la vue Direction, la maquette demande une agrégation de la dimension en « Inbound », dont les règles restent à préciser. |
| M03 | **Nombre d’opportunités en cours par source et répartition en %** | Comptage des deals ouverts à la date d’observation ; parts de la population par canal. Le dénominateur exact dépend de la population filtrée. | Photo à date, canal, segment ; filtre SMB/LA/Espagne ; équipe/global. La définition de « ouvert » reste à confirmer. | Tableau, répartition en %. W-M zone 3 : à valider avec VP Sales. |
| M04 | **Pipeline pondéré versus objectif** | Somme des montants des deals × probabilité du stage, comparée à une cible. Sens des coefficients et convention à confirmer, voir Q15/QM-05. | Étape, équipe/segment, global, date/période ; lecture historique ajoutée par W-B. | Montant et jauge versus objectif. W-M zone 4 : ne pas figer avant audit des win rates historiques et échange avec la VP Sales. |
| M05 | **Pipeline total non pondéré** | Somme des montants des deals ouverts. L’unité mensuelle ou contractuelle de ces montants ne se déduit pas du seul intitulé « pipeline ». | Photo à date et évolution dans le temps ; canal/segment/équipe selon filtres ; global. | Indicateur de montant et tendance. W-M zone 5, indiqué « standard » dans la maquette, sans validation supplémentaire présumée. |
| M06 | **Pipeline coverage / couverture de l’objectif** | Somme des montants des deals ouverts dont la clôture est prévue dans le mois / objectif du mois. Identifier quel objectif et vérifier la compatibilité des mesures avant calcul. | Mois de clôture prévue, date d’observation, équipe/global ; axes transverses. | Ratio et tendance. W-M zone 6. Le dénominateur « objectif du mois » n’est pas suffisamment défini pour le choisir ici. |
| M07 | **ADV / MRR potentiel du pipeline** | La maquette indique un « MRR potentiel moyen par deal », en global / canal / segment, et cite montant, stage et probabilité. La formule complète n’est pas fournie ; le sens d’ADV n’est pas défini. | Global, canal, segment/équipe ; période/date à formaliser. | Montant et tendance. W-M zone 7 : KPI non figé, dépendant des probabilités. Ne pas l’assimiler au MRR actif ou à une formule d’ARPU sans validation. |
| M08 | **Deals stagnants : nombre et montant** | Nombre et montant des deals sans changement de stage depuis X jours. Date d’entrée ou dernier changement de stage et ancienneté nécessaires. | Photo à date, stage, segment/équipe, ancienneté ; seuil X à définir. | W-M zone 8 propose liste avec alerte et tri par ancienneté. Pour le cadrage stratégique : conserver les volumes, montants et répartitions par étape/équipe ; la place éventuelle du détail de dossier reste à définir dans la restitution. « > 30 jours » est un exemple interrogatif, pas un seuil validé. |

#### B. Historique et analyses explicitement demandés en complément

| ID | Besoin / indicateurs | Grain, période et axes souhaités | Précisions et source |
| --- | --- | --- | --- |
| B01 | **Ancienneté dans le stage actuel** et repérage des dossiers stagnants | Besoin observé à une date, puis lecture agrégée par stage/équipe/segment ; ancienneté exprimable en durée. | W-B ligne 9 et W-M zone 8. Historique des changements nécessaire ; seuils et règles sur les retours restent ouverts. |
| B02 | **Cohortes de pipeline : encore ouvert, gagné, perdu** — effectifs nécessaires et pourcentages à différents horizons | Cohorte d’opportunités par **mois de création** ; observations à **J+30, J+60 et J+90**. Axes de segment/équipe et canal à articuler avec les filtres souhaités, sans supposer des cohortes toutes déjà matures. | W-B lignes 10 et 15. Dénominateur de cohorte, gestion des abandons/réouvertures et frontière de création à définir. |
| B03 | **Évolution historique du pipeline pondéré / « pipe projeté »** | Série temporelle et date d’observation ; stage et équipe/segment pour la pondération ; global. | W-B lignes 11 et 16 : un vrai historique, au-delà d’une photo actuelle. Le snapshot manuel quotidien est un dispositif d’attente, pas une fréquence cible définitivement imposée. |

#### C. Les quatre objectifs mensuels fournis par équipe

Il s’agit de **cibles de pilotage**, indépendantes des probabilités. Leur présence dans le modèle ne les rend pas interchangeables et ne démontre pas la formule du réalisé correspondant.

| ID | Indicateur cible | Ce que le référentiel fournit | Lecture souhaitée et réserves |
| --- | --- | --- | --- |
| O01 | `mrr_signed` — objectif de MRR signé | Montant en euros, par mois et équipe. | Comparaison au résultat de signature défini de façon compatible ; signature, normalisation mensuelle et date restent à confirmer. |
| O02 | `pipeline_generated` — objectif de pipeline généré | Montant en euros, par mois et équipe. | À rapprocher de la génération de pipeline, pas d’un nombre de deals. Ne pas confondre flux généré et stock ouvert à date. |
| O03 | `pipeline_weighted` — objectif de pipeline pondéré | Montant en euros, par mois et équipe. | À rapprocher d’un pipe pondéré avec une convention explicite et une date comparable. |
| O04 | `demos` — objectif de démos | Nombre, par mois et équipe. | La définition du réalisé doit préciser actions de démo, premières démos ou dossiers ayant franchi la phase ; orientation Q3 conservée. |

Source W-O : `ref.sales_targets`, colonnes `month`, `segment`, `indicator`, `target`, modèle lignes 1418–1449. Équipes documentées : SMB, LA et ES. La comparaison objectif/réalisé est souhaitée ; **seule la formule pipeline généré / objectif × 100 est explicitement donnée dans la zone 1**. Les autres taux d’atteinte ou écarts ne reçoivent pas de formule inventée ici. Aucun objectif individuel n’est créé ou réparti entre personnes.

#### D. Attentes précisées par l’utilisateur au cours du cadrage

| ID | KPI / analyse à conserver dans la liste des souhaits | Axes et granularité d’intention | État de définition |
| --- | --- | --- | --- |
| U01 | **Conversions et déperdition par étape** : volumes entrants/sortants, progression et pertes, taux associés | Étape du tunnel, période/cohorte, équipe, segment, canal ; global. | Demande utilisateur Q11 : localiser les pertes trop importantes. Les événements, populations comparables et seuils de « trop important » restent à définir ; aucun taux mesuré n’est produit. |
| U02 | **Cycle de vie d’un deal / besoin** : progression, étapes atteintes et issues | Dossier relié à une société pour le suivi ; restitution stratégique agrégée par étape/équipe/cohorte. | Demande utilisateur Q11 et hypothèse Q12. La création/qualification reste en Q10, reportée. |
| U03 | **Durée dans les différentes étapes et durée du cycle** | Durées par dossier/passage, puis agrégation par stage, équipe, cohorte et période. | Besoin retenu en Q9 et réaffirmé en Q11. Ancienneté courante, temps d’un passage et cumul après retours doivent être distingués ; moyenne, médiane ou autres statistiques ne sont pas choisies ici. |
| U04 | **Volumétrie des démos : actions et dossiers dans la phase démo** | Mois/période, équipe/global ; première démo et compléments à distinguer si pertinents. | Q3 et objectif `demos`. Une séance et un dossier ayant eu une démo ne sont pas le même compteur ; réalisation et bornes de phase à confirmer. |
| U05 | **MRR actif à une date** | Date d’observation, global et société comme rattachement ; axes analytiques selon les futurs besoins. | Source Boond retenue en Q2 : `raw.deliveries` via `raw.projects`. Montants mensuels HT ; états et périodes actifs à confirmer. Aucun encaissement déduit. |
| U06 | **MRR signé** | Période de signature, équipe/global ; source commerciale et rattachement à définir. | Indicateur retenu en Q2 et objectif O01. Événement de signature et unité mensuelle à confirmer ; ne pas assimiler au MRR actif. |
| U07 | **New MRR** | Mois d’ajout à la base active, équipe/global selon attribution à définir. | Intention retenue en Q2. Mouvements inclus, nouveaux clients/extensions/réactivations et événement d’entrée non arbitrés. |
| U08 | **Encaissements mensuels**, exprimés par l’utilisateur sous « MRR encaissé » | Mois du paiement, observation à la clôture, global ; ventilation à définir. | Souhait conservé malgré l’absence de source de règlements dans le modèle fourni. Ne pas l’assimiler automatiquement au MRR ou au chiffre d’affaires reconnu. La faisabilité sera traitée plus tard. |
| U09 | **Scénario de revenu à portefeuille supposé constant** | Projection à partir d’une date N vers la fin du mois. | Idée utilisateur : sans churn ni New MRR, précédemment évoquée comme « MRR hypothétique signé ». Option à préciser, pas un KPI obligatoire déjà validé ; aucun paiement futur garanti. |

La liste est exhaustive au regard des attentes documentées et des précisions utilisateur consultées à cette étape. Elle restera enrichissable si une nouvelle demande apparaît. Les mesures candidates des supports et les mesures du SQL existant sont séparées ci-dessous pour ne pas les présenter comme des demandes métier validées.

#### E. Dimensions, granularités et filtres

| Axe / dimension | Application métier souhaitée | Origine et limites |
| --- | --- | --- |
| **Équipe commerciale** | SMB, Large Accounts / LA, Espagne / ES ; comparaison entre équipes et vue consolidée globale. | Maquette, zones 1 à 8 ; objectifs et probabilités. Les alias seront réconciliés dans la spécification. Axe stratégique central retenu par l’utilisateur. |
| **Segment** | Répartitions des opportunités, montants et analyses du tunnel par segment ; comparaison des performances. | Filtre transversal de la maquette. `segment` dans `ref.sales_targets` et `ref.stage_probabilities` est décrit comme équipe SMB/LA/ES. Ne pas inventer une équivalence avec toute autre segmentation des sociétés. |
| **Canal / source / origine** | Opportunités générées et ouvertes par source, valeur et revenu potentiel par canal, conversions et déperdition selon origine. | Maquette zones 2, 3 et 7 et filtre transversal. Origine du contact, dernier canal et origine du besoin ne sont pas fusionnés sans règle ; QM-02. Agrégation Direction en « Inbound » demandée dans la zone 2, à préciser. |
| **Période d’analyse** | Comparer et suivre les volumes, montants, objectifs, conversions et durées dans le temps. | Filtre transversal de la maquette. Jour/semaine/mois sont des pistes retenues au cadrage ; les objectifs sont mensuels. Ne pas confondre granularité de restitution, fraîcheur des sources et fréquence d’exécution. |
| **Date d’observation** | Photos de pipe ouvert, MRR actif, ancienneté et stagnation ; reconstitution d’une situation passée. | Maquette zones 3, 5 et 8 ; historique W-B et Q2. Le stock à une date est distinct des événements sur une période. |
| **Date de création / génération** | Opportunités générées sur une période et cohortes mensuelles de création. | Maquette zone 2 et W-B ligne 15. La frontière d’ouverture du besoin en Q10 est reportée, pas tranchée par cet inventaire. |
| **Date de signature / clôture effective** | Signatures et MRR signé d’une période, issues des cohortes. | Objectif O01, Q2 et expression de besoin. Événement exact et distinction signature/fin des formalités à confirmer. |
| **Date de clôture prévue** | Couverture de l’objectif du mois et analyse du pipe attendu. | Maquette zone 6 ; elle ne doit pas être remplacée sans explication par une date de signature effective. |
| **Dates d’activité de l’abonnement et de paiement** | MRR actif selon période de service ; encaissements selon paiements reçus. | Q2 et QM-04. Les dates et états d’abonnement ne prouvent pas des paiements ; les conventions de début/fin restent ouvertes. |
| **Stage / étape du tunnel** | Volumes, conversion, déperdition, ancienneté, durées et pondération selon le stage. | Maquette zones 4 et 8, expression de besoin et Q11. Q10/QM-01 encadreront les entrées/sorties, sauts et retours ; le sens des probabilités est traité séparément en Q15/QM-05. |
| **Issue / état métier** | Ouvert, gagné, perdu pour les cohortes ; distinctions abandon et nurturing à confirmer. | W-B lignes 10 et 15, cycle de vie. Ne pas convertir d’office un nurturing ou une attente en perte définitive. |
| **Cohorte et âge de cohorte** | Mois de création × horizon J+30/J+60/J+90 ; comparaison des proportions encore ouvertes/gagnées/perdues. | W-B lignes 10 et 15. Les cohortes trop récentes pour un horizon ne reçoivent pas automatiquement un résultat à cet horizon. |
| **Ancienneté / durée / seuil de stagnation** | Répartitions et comparaisons de durées ; identification des montants et volumes bloqués. | Maquette zone 8, Q9 et Q11. Seuil X, jours calendaires/ouvrés, fenêtres et statistiques restent à préciser, pas à choisir ici. |
| **Indicateur d’objectif** | Choisir l’un des quatre indicateurs O01 à O04, puis comparer des mesures compatibles. | Référentiel des objectifs mensuels ; ne pas comparer un nombre de démos à un montant de pipe ou assimiler toutes les cibles. |
| **Société / entreprise** | Rattacher opportunités et deals à une entité commerciale, indépendamment du nombre d’interlocuteurs ; regrouper les montants ou les dossiers selon l’analyse. | Hypothèse utilisateur Q12. C’est un rattachement d’identité ; aucun filtre d’interface ou tableau nominatif de sociétés n’est imposé par cette seule précision. |
| **Individu / commercial** | La maquette initiale le mentionne comme filtre transversal et grain individuel sur plusieurs zones. | **Demande d’origine conservée, hors cadrage actuel** : l’utilisateur retient une lecture stratégique équipe/global et exclut le pilotage par personne. Aucun objectif individuel ou classement de commerciaux n’est ajouté. |

**Grains à distinguer :** dossier/opportunité, société, action de démo et ligne d’abonnement décrivent les objets suivis ; équipe/global, canal, stage et période décrivent les regroupements et découpages de lecture. Le choix de sociétés comme rattachement n’efface pas les besoins multiples d’une même société. Les identifiants de contacts servent aux liens si nécessaire, sans multiplier le nombre de deals.

**Découpages transverses :** appliquer les filtres seulement lorsque l’axe a un sens pour l’indicateur et un rattachement défini. Par exemple, une attribution canal du MRR actif ne se déduit pas automatiquement du dernier canal d’un contact. Les règles de propagation et de compatibilité seront écrites dans la spécification.

**Restitutions proposées dans les sources :** jauge d’atteinte, barres par canal empilées par période, tableau et parts en %, indicateurs de montant ou ratio avec tendance, évolution historique, vues de cohortes, répartition par étape et ancienneté. La forme finale, les onglets et les alertes ne sont pas sélectionnés ici. Les formes de tunnel des supports sont qualitatives et n’encodent aucun volume observé.

#### F. Mesures candidates déjà présentes dans les supports — hypothèses, pas demandes validées

Les dix étapes de W-H proposent les mesures suivantes. Elles sont conservées comme pistes de découverte afin de ne pas perdre leur trace, **séparément du socle métier demandé**. La disponibilité des événements et leur intérêt final ne sont pas supposés. Les contrôles techniques ne sont pas assimilés à une attrition commerciale normale ; Produit et Tech restent hors du périmètre de réalisation actuel.

| Repère | Mesures candidates sous conditions | Dimensions / précautions présentes dans les supports |
| --- | --- | --- |
| H01 — Formulaire | Envois / débuts de formulaire ; volumes d’affichages, clics et débuts comme événements candidats du sous-parcours. | Canal, campagne et cohorte ; ces événements ne sont pas établis comme disponibles. Un envoi n’est pas forcément un nouveau contact. |
| H02 — Transmission vers Boond | Demandes reçues dans le délai / demandes à transmettre ; retards, absences et doublons comme contrôles. | Demande et identifiant de liaison ; pas un dénominateur de contacts uniques. Contrôle de transmission. |
| H03 — Attribution | Taux d’attribution dans le délai et ancienneté des demandes non attribuées. | Demandes à attribuer, équipe/global et délai ; pas de suivi individuel retenu. Une attente n’est pas une perte établie. |
| H04 — Contact / qualification | Prospects joints / contactés, puis qualifiés / joints. | Population comparable, cohorte et équipe ; dédupliquer les tentatives. Le nombre d’appels n’est pas celui des prospects. |
| H05 — Découverte | RDV acceptés / leads qualifiés, puis découvertes réalisées / RDV prévus. | Période/cohorte et type de RDV ; distinguer découverte et démo et confirmer les événements. |
| H06 — Démo | Démos tenues / démos prévues arrivées à échéance ; actions distinctes et dossiers avec une démo tenue. | Première démo, compléments et absences ; une démo complémentaire n’est pas une étape obligatoire par défaut. |
| H07 — Proposition | Besoins avec proposition remise / besoins éligibles ; durée par étape. | Cohorte comparable et preuves de remise ; étapes possiblement sautées ou revisitées. |
| H08 — Issue | Taux de gain sur les deals clos éligibles ; motifs de perte à examiner si pertinents. | Issues alternatives, abandons et réouvertures à définir ; nurturing non assimilé à une signature ou une perte définitive. |
| H09 — Synchronisation HubSpot | Deals correctement synchronisés / besoins à synchroniser ; délais et écarts de statut/dates. | Identité Boond/HubSpot et même date de comparaison ; ce n’est pas une marche du tunnel commercial. |
| H10 — Vie client | Abonnements démarrés / deals signés dont le démarrage est attendu ; suivi de rétention/churn à définir séparément. | Société/projet/abonnement, période d’activation et période de service ; une fin de ligne ne prouve pas toujours le churn. |

Source : W-H, chaque objet `n=1` à `n=10`, champs `question`, `measure` et `caveat`. Cette section n’ajoute pas automatiquement dix nouveaux chantiers au case.

#### G. Mesures du reporting actuel — inventoriées, sans les reprendre comme normes cibles

| Mesure du SQL existant | Ce qu’elle représente actuellement | Pourquoi la distinguer d’un KPI souhaité |
| --- | --- | --- |
| `open_deals` | Besoins distincts observés dans les états ouverts listés pendant la semaine. | Ce n’est pas une photo à date ni un volume moyen ; M03 décrit une attente de photo à date. |
| `pipe_amount` | Montants journaliers ouverts divisés par les jours représentés du groupe semaine/équipe. | Dénominateur et duplications possibles doivent être compris ; ce n’est pas automatiquement M05. |
| `signed_deals` | Besoins observés à l’état 1 pendant la semaine. | Ce n’est pas un comptage d’événements de nouvelles signatures. |
| `signed_amount` | Montants journaliers à l’état 1 divisés par les jours représentés. | Ce n’est pas une formule validée de MRR signé, actif ou encaissé. |

Source W-L ; voir [analyse_pipeline_actuel.md](analyse_pipeline_actuel.md), synthèses 1 à 3. La restitution actuelle est hebdomadaire × équipe, alors que les cibles sont mensuelles : la spécification décidera de la lecture et du calendrier appropriés après la formulation d’intention.

**Statut de Q4 :** inventaire des souhaits produit. Aucun KPI n’est promis, écarté pour manque de données ou sélectionné comme périmètre V1 dans ce bloc. Les précisions stratégiques de l’utilisateur encadrent la restitution ; les demandes individuelles de la maquette restent tracées comme demandes d’origine hors du cadrage actuel.

### Q12 — Rattachement des dossiers à une société

**Hypothèse utilisateur retenue pour poursuivre :** chaque société possède un identifiant dans `raw.companies` ; les opportunités sont reliées à une société par cet identifiant ; les deals doivent être associés à une société indépendamment du nombre d’interlocuteurs. L’intégrité réelle et les règles de rapprochement seront approfondies dans la spécification technique.

**Ce que les sources documentent :**

- Le besoin Boond porte `relationships.company.data.id` vers `raw.companies.id` : [modèle, lignes 171–178](../../docs/model/model.json).
- Un deal HubSpot reflète un besoin Boond : modèle, lignes 1293–1298. Son champ `properties_boond_id_num` est décrit comme l’identifiant de l’opportunité Boond et référence `raw.opportunities.id` : lignes 1355–1362.
- Le README, contexte, précise que les besoins/opportunités sont aussi appelés deals par les équipes. Dans Boond, ces mots ne prouvent donc pas deux objets commerciaux distincts ; pour HubSpot, un objet deal est représenté séparément et doit être rapproché du besoin.

**Chaîne d’identité de travail :** deal HubSpot → opportunité/besoin Boond → société Boond. Plusieurs contacts ne doivent pas multiplier le nombre de dossiers ou leurs montants.

**Limite :** une relation déclarée dans le modèle ne prouve ni que chaque valeur est renseignée, ni une correspondance strictement un pour un, ni l’absence de doublons/orphelins. Le rattachement société n’implique pas non plus de fusionner toutes ses opportunités indépendantes en une seule. Ces contrôles sont reportés à la spécification, sans rouvrir ici le questionnaire abstrait sur les compteurs.

**Statut :** hypothèse de rattachement retenue ; vérification des données et définition des grains par KPI à approfondir dans la spécification.

### Q15 — Objectifs et probabilités : séparation confirmée, sens des coefficients à confirmer

**Précision utilisateur retenue :** `sales_targets` porte quatre objectifs mensuels par équipe, sur lesquels les équipes sont censées agir. Ces objectifs sont distincts des probabilités proposées par le cabinet ; il n’existe pas d’équivalence ou de lien direct automatique entre une valeur cible et un coefficient.

Le modèle confirme : [lignes 1418–1449](../../docs/model/model.json), grain mois × segment/équipe × indicateur, avec `mrr_signed`, `pipeline_generated`, `pipeline_weighted` et `demos`. Les cibles sont exprimées en euros pour les montants et en nombre pour les démos.

**Interprétation utilisateur conservée comme point à vérifier :** les probabilités représenteraient le passage à la prochaine étape.

**Information documentaire différente :** [le modèle](../../docs/model/model.json), ligne 1457, dit explicitement « Probabilité de signature par étape du besoin et par équipe, proposée par le cabinet externe » ; la colonne `probability`, ligne 1487, est décrite comme « Probabilité de signature, entre 0 et 1 ». La maquette, zone 4, utilise un montant × probabilité de stage pour proposer le pipeline pondéré et demande de challenger les win rates historiques.

**Conséquence :** sur la base de la documentation seule, les coefficients sont décrits comme des probabilités de signature depuis un stage, pas comme des taux de transition vers le stage suivant. Le second sens ne sera pas enregistré comme un fait établi. Ni la validité empirique du premier sens ni sa calibration ne sont démontrées. Voir [QM-05 — Sens des probabilités](questions_metiers.md#qm-05--sens-des-probabilités) pour la confirmation métier.

Un coefficient de transition et une probabilité de signature finale répondent à des questions différentes ; l’un ne sera pas substitué silencieusement à l’autre pour pondérer une valeur de vente. L’usage éventuel des probabilités dans le réalisé `pipeline_weighted`, puis la comparaison de ce réalisé à sa cible, sont deux opérations distinctes. Le taux d’atteinte d’un objectif n’est pas une probabilité de passage ou de signature.

**Niveau de restitution :** l’utilisateur privilégie une vue **stratégique équipe/global**. Les analyses par personne relèvent du pilotage opérationnel et ne concernent pas le cadrage actuel. Aucun objectif individuel n’est déduit des cibles d’équipe.

**Statut :** séparation objectifs/probabilités et lecture stratégique retenues. Le sens des coefficients comporte un désaccord entre interprétation utilisateur et documentation ; il est à confirmer avec le métier/cabinet, pas tranché par une hypothèse IA.

### Q11 — Finalité stratégique du cockpit

**Intention utilisateur retenue :** permettre de voir à quel endroit du tunnel la déperdition devient trop importante, d’analyser le cycle de vie d’un deal et les durées d’un lead ou dossier dans les différents stages. Les autres besoins du document d’expression de besoin — historique, cohortes, évolution du pipeline pondéré — font partie de l’inventaire Q4.

Les décisions visées sont éclairées par une lecture des volumes, conversions, montants, anciennetés et durées, à l’échelle des équipes et du global. Aucune règle de relance automatique ou d’évaluation individuelle n’est ajoutée.

**Points de définition encore ouverts :** seuil ou référence de « trop important », populations comparables, événements d’étape, durées et traitement de l’attente/nurturing. Une baisse de conversion observée ne prouve pas sa cause ; les frictions des supports restent des hypothèses à investiguer.

**Statut :** finalité de cadrage précisée ; pas de nouvelle demande de choisir une priorité unique ou un périmètre V1 à ce stade.

### Q10 — Ouverture du besoin : report explicite

**Complément du 24 octobre 2026 :** à la demande de l’utilisateur, un [état des lieux Q10](etat_des_lieux_Q10.md) rapproche maintenant cycle, maquette, SQL historique et observations en base. Il documente le désaccord et ses conséquences sans choisir la frontière qualifiée. Les questions sont consignées en QM-06 ; le diagnostic ne vaut pas réponse ou validation métier.

**Instruction utilisateur :** cette question, accentuée dans les consignes, doit mûrir à l’étape suivante et être reprise au prochain cycle. Elle est **reportée**, pas résolue. L’hypothèse distinguant création de fiche et opportunité qualifiée reste une interprétation non confirmée.

Ce report concerne Q10 uniquement et ne met pas en pause le travail documentaire demandé dans ce tour. Aucun calcul de génération, de cohorte ou de durée n’adopte silencieusement une frontière d’ouverture définitive.

### Dernier état après le cycle 3

| Question / sujet | État retenu | Suite |
| --- | --- | --- |
| Q4 | Liste exhaustive des souhaits disponible, avec provenance et axes ; pas de sélection de livraison. | Faisabilité et périmètre livré à décider dans la spécification. |
| Q12 | Rattachement des dossiers à la société retenu comme hypothèse de travail. | Tester les relations et définir les grains des KPI dans la spécification. |
| Q15 | Objectifs distincts des probabilités ; lecture équipe/global. | Confirmer le sens des probabilités en QM-05, puis leurs usages. |
| Q11 | Déperdition, cycle de vie et durées retenus comme finalités. | Définir ultérieurement populations, seuils et règles de calcul. |
| Q10 | Reportée à la prochaine étape / prochain cycle. | Ne pas la réouvrir dans ce tour et ne pas la déclarer tranchée. |
| Q2 / Q5 | Décisions et confirmation du cycle 2 conservées. | Conventions financières en QM-04 ; pas de réouverture des points déjà retenus. |
| Q13 / Q14 / Q16 | Questions métier maintenues. | QM-01 à QM-03, à poser. |

**Limite de ce tour :** inventaire et cadrage uniquement. Aucun taux, montant ou délai réel calculé ; aucun modèle dbt, dashboard, service, source ou requête legacy modifié.


## 13. Q10 — diagnostic repris et clôture du cadrage

### Réponse retenue pour Q10

**Instruction utilisateur :** utiliser l’analyse produite dans une autre discussion comme réponse documentaire à Q10. Le diagnostic remplace le simple report de cette question dans les cycles précédents ; il ne constitue pas une validation métier de la frontière qualifiée.

**Réponse de synthèse :** la fiche besoin existe avant la démo. En revanche, l’événement qui fait entrer ce besoin dans un pipeline commercial qualifié n’a pas de définition commune confirmée dans les sources. Création CRM et entrée qualifiée peuvent être deux dates distinctes ; les données ne permettent pas de choisir seules la convention métier.

Voir [l’analyse complète de Q10](etat_des_lieux_Q10.md), les [requêtes SQL de vérification](explore_q10_pipeline_entry.sql) et leurs [résultats enregistrés](preuves_Q10.json). Les arbitrages restant à confirmer figurent dans [QM-06 — Entrée dans le pipeline qualifié](questions_metiers.md#qm-06--entrée-dans-le-pipeline-qualifié). L’[analyse du SQL historique](analyse_pipeline_actuel.md) détaille le fonctionnement actuel et ses limites.

### Éléments de preuve et limites

Les résultats fournis sont datés du **24 octobre 2026**, session UTC, sur une population définie comme dernière version par tenant/identifiant puis exclusion des suppressions, tous types et toutes dates de création. Ils proviennent du contrôle de l’autre discussion. Dans ce tour, les fichiers ont été lus et leur cohérence documentaire contrôlée ; **aucune requête n’a été relancée et aucun serveur n’a été interrogé**.

| Constat enregistré | Valeur | Repère dans `preuves_Q10.json` | Conclusion permise |
| --- | ---: | --- | --- |
| Besoins de la population actuelle du contrôle | 1 376 | `queries`, entrée `query="Q3"`, ligne de résultat, `nb_besoins` | Périmètre des observations ci-dessous, pas nombre de clients. |
| Premier état enregistré « Lead à traiter », code 0 | 1 271 | Entrée `query="Q2"`, résultat `first_state=0`, `nb_besoins` | Les fiches observées existent largement en amont de la démo. La première observation n’est pas toujours la création réelle. |
| Besoins ayant au moins un Show Boond enregistré | 317 | `Q3`, `show_boond_observe` | Présence d’un passage enregistré, pas preuve suffisante de tenue d’une démo. |
| Besoins actuellement signés | 227 | `Q3`, `actuellement_signes` | Stock d’issues actuelles, pas flux mensuel de signatures. |
| Parmi ces signés, aucun Show Boond dans l’historique fourni | 121 | `Q3`, `signes_sans_show_boond_observe` | Impossible d’imposer un passage enregistré à la démo comme séquence universelle sans règle sur les cas manquants. Absence de trace ne prouve pas absence de démo réelle. |

Le cycle crée le besoin à « Lead à traiter » ; la maquette place le démarrage de l’opportunité à la démo ; le SQL historique inclut des états avant démo ainsi que nurturing. La classification `active` du référentiel désigne un besoin en cours, pas une qualification réussie ou un abonnement actif. `isEnabled` indique une proposition dans l’interface, pas un rang dans un parcours obligatoire.

Les dates CDC restent des dates d’observation/publication. Une entrée à Show Boond observée peut servir de proxy explicitement nommé, pas de date métier certifiée sans vérification. Les sauts apparents, retours, nurturing et débuts d’historique incomplets restent à traiter selon QM-01 et QM-06. Une répartition des stocks par étape n’est pas, à elle seule, un taux de conversion entre populations suivies.

**Statut final de Q10 dans le raw intent : diagnostic documenté disponible, convention métier d’entrée qualifiée encore ouverte.** La sélection de l’événement, des dates de cohortes et du début des durées est transmise aux arbitrages métier et à la spécification ; aucune frontière n’est choisie silencieusement.

### Clôture de l’établissement du raw intent

**À la demande de l’utilisateur, l’établissement du raw intent est terminé.** Le dossier constitue le socle de cadrage : informations connues, hypothèses, souhaits exhaustifs, décisions explicites et arbitrages restants. Cette clôture ne transforme pas les hypothèses ou questions métier en réponses confirmées et ne vaut pas spécification technique validée.

Les documents de cette phase, les preuves Q10 et les supports du cycle de vie sont regroupés dans `orest_case_output/raw_intent/`. Le [guide local du dossier](README.md) donne le parcours de lecture. Le guide général du rendu et l’historique intégral de ce chat restent à la racine de `orest_case_output/` pour accompagner la suite du case.

La copie [explore_q10_pipeline_entry.sql](explore_q10_pipeline_entry.sql) incluse au dossier est identique à [l’original technique](../../docs/sql/explore_q10_pipeline_entry.sql), conservé dans `docs/sql/`. Elle permet de consulter la preuve avec le cadrage sans déplacer le code technique du projet. La commande de reproduction du diagnostic continue à utiliser l’original depuis la racine du dépôt, avec un ClickHouse disponible ; aucune exécution n’est effectuée pendant ce regroupement.

Les questions encore ouvertes sont conservées dans [questions_metiers.md](questions_metiers.md), notamment QM-04 pour les conventions de revenu, QM-05 pour le sens des probabilités et QM-06 pour l’entrée qualifiée. Aucun nouveau cycle de questions, modèle, dashboard ou service n’est lancé dans ce tour.
