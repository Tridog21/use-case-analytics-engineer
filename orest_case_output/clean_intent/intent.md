# Le cockpit commercial — version de revue humaine

**Statut de phase — échange 25 :** consolidation de l’intent terminée à la demande de l’utilisateur. Préparation des spécifications dans [spec_technique — étape 0, conventions](../spec_technique/00_conventions.md), limitées aux règles définies par l’utilisateur à l’échange 26. Les questions métier encore ouvertes restent tracées dans le registre ; cette clôture ne les résout pas automatiquement.

**Échange 19 — historisation de toute la chaîne :** l’exigence couvre staging, intermédiaires, faits, dimensions et liaisons. Distinguer l’unité métier de ses versions et sélectionner les versions pertinentes avant agrégation. Les modalités de révision/restitution et la rétention détaillée restent à spécifier. [Règle commune et deux vues détaillées](architecture_modele_proposition.md#historisation-toutes-couches), [DCI-17](questions_decisions.md#dci-17).

**Échange 18 — organisation modulaire proposée :** intégrer la Démo dans les tables génériques du pipeline et garder son micro-funnel en extension locale. Deux modules — Pipeline/parcours et Revenus/performance — réutilisent les identités et dimensions communes. Les objectifs consomment les réalisés commerciaux publiés ; les abonnements alimentent directement MRR/churn. [Proposition et visuel](architecture_modele_proposition.md#architecture-modulaire), [DCI-16](questions_decisions.md#dci-16). Les définitions métier ouvertes restent ouvertes.

**Échange 15 :** la [liste courte des KPI, définitions et formules](liste_kpi_humaine.md) devient la lecture humaine approuvée. La [nouvelle proposition de modèle](architecture_modele_proposition.md) décrit l’intermédiaire, les faits et les dimensions à partir du staging recensé. Les DTR restent hors de cette proposition ; les règles ouvertes ne sont pas arbitrées par le schéma. [DCI-14](questions_decisions.md#dci-14).

Ce document explique le besoin. Le [catalogue humain](catalogue_indicateurs.md) détaille les indicateurs avec leur définition, leur grain et leur formule. La [version IA](intent_ia.md) conserve les sources et les règles détaillées.

**État :** les décisions métier sont actualisées jusqu’à l’échange 22 ; voir les [arbitrages récents](questions_decisions.md#du-28). Les décisions des échanges 5 à 9 restent conservées lorsqu’elles ne sont pas précisées ou remplacées ensuite. À l’échange 10, la première architecture est retirée et remplacée par un inventaire des champs nécessaires et de leurs sources. À l’échange 11, les calculs sont décomposés pour préparer le staging. Les points encore ouverts restent regroupés à la fin.

<a id="point-b"></a>
## 1. Le point B : ce que nous voulons obtenir

**Un tableau de bord partagé pour comprendre comment les affaires avancent et comment le revenu récurrent évolue.**

La VP Sales, les équipes Sales et le Marketing doivent pouvoir :

- voir combien d’affaires et de valeur entrent dans le pipeline ;
- repérer les étapes où les dossiers se perdent ou restent longtemps ;
- suivre les dossiers d’un même mois de création et l’évolution du pipeline ;
- comparer les résultats aux objectifs mensuels des équipes ;
- distinguer acquisition de nouveaux clients et ventes additionnelles (*upsells*) ;
- comprendre si le revenu progresse grâce aux nouveaux clients ou aux extensions, et s’il baisse à cause de départs ou d’abonnements moins chers.

Le *pipeline* est le portefeuille de dossiers commerciaux suivis dans le parcours de vente. Un dossier y entre dès sa création dans Boond après soumission du formulaire (échange 22). Cette entrée ne signifie pas que sa qualification commerciale est déjà acquise. Le lien au formulaire doit être vérifié ; il ne devient pas un filtre excluant les upsells ou les dossiers sans formulaire retrouvé.

**La synthèse reste globale et par équipe : SMB, Large Accounts et Espagne.** Une feuille dédiée comparera aussi individu et équipe, sous réserve de faisabilité. Cette orientation remplace l’exclusion générale antérieure ; aucun objectif personnel n’est ajouté. Les chiffres doivent orienter les investigations ; ils ne prouvent pas, seuls, la cause d’un problème.

La maquette v2 est désormais la base souhaitée du dashboard V1. Le data mart doit conserver un détail plus fin pour les futurs dashboards : passages d’étapes, durées, canaux, responsables, actions et mouvements d’abonnement. Les attentes restent visibles même si les données manquent. La première architecture est retirée à l’échange 10. L’inventaire des champs et sources sert désormais de base à la proposition logique de l’échange 15 ; les règles ouvertes restent à préciser.

## 2. Le point de départ et les règles déjà choisies

Les Sales suivent leurs dossiers dans **Boond**. Le Marketing utilise **HubSpot**. Une maquette décrit les analyses souhaitées ; un ancien SQL fournit un reporting existant. Ces sources n’imposent pas toutes les définitions du futur cockpit.

Les tables `raw` de Boond **contiennent déjà plusieurs versions des mêmes objets** : `id` identifie l’objet, `meta.ts` date la publication de la version et `meta.deleted` signale une suppression. Elles ne contiennent donc pas seulement le dernier état. En revanche, une date de publication n’est pas toujours la date réelle de l’événement métier.

Pour ce case, **l’utilisateur tranche les définitions**. Dans la vie réelle, ces décisions seraient discutées avec la VP Sales et les métiers. Il n’est pas nécessaire d’attendre leur validation pour avancer ici.

Les objectifs se vérifient **en fin de mois, pour les équipes Sales**. Les quatre cibles sont : MRR signé, pipeline généré, pipeline pondéré et démos. Nous n’ajoutons pas de découpage quotidien des objectifs.

## 3. Comprendre le parcours et ce que l’on compte

Le parcours documentaire d’une nouvelle vente passe par la demande, la prise en charge, la qualification, la découverte, la démo, la proposition et la décision. Il peut comporter des attentes, des pertes et des retours : toutes les étapes ne sont pas supposées obligatoires.

Une **société** est l’entreprise prospecte ou cliente. Un **contact** est un interlocuteur. Une **opportunité**, ou besoin commercial, est un dossier de vente. Un **deal HubSpot** peut représenter ce même dossier ; ce n’est pas une vente supplémentaire à additionner.

> Une société peut avoir deux contacts, deux opportunités et trois séances de démo. Cela fait une société, deux interlocuteurs, deux dossiers et trois séances : quatre unités différentes.

### Deux lectures complémentaires de la démo

- **Nb In demo :** stock de prospects dans la phase commerciale « Show Boond » à une date. On compte les **sociétés distinctes** ayant au moins une opportunité dans cette phase à la date observée : une société avec deux dossiers en Démo compte pour **un prospect** (échange 23). Le temps passé dans cette phase est une mesure distincte.
- **Nombre de démos :** nombre de rendez-vous de démonstration réellement tenus pendant la période, une séance comptée une fois. C’est le réalisé à comparer à l’objectif de démos ; une séance simplement planifiée n’est pas comptée comme tenue.
- **Le sous-parcours de démo :** des actions décrivent une demande, une Démo 1, une démo complémentaire ou une annulation. On souhaite aussi comprendre les délais entre ces étapes.

Ces deux lectures sont utiles et correspondent à des grains différents. Le sous-parcours d’actions est une information secondaire souhaitée pour le data mart. Il reste à définir ses événements et à rattacher correctement les actions au dossier concerné.

Le temps d’attente avant une séance, sa durée dans l’agenda et le temps du dossier au statut démo ne sont pas la même mesure. Une action planifiée ou un statut ne prouvent pas, seuls, que la séance a été tenue.

### Séparer nouvelles ventes et upsells

Un **upsell** est une vente additionnelle à un client existant. Nous conservons les types de dossiers et séparons leurs funnels ; un filtre par type dans le dashboard est l’orientation proposée. Le filtre « nouveaux clients » ne doit pas éliminer les upsells de toutes les analyses.

L’analyse enregistrée porte sur **52 upsells et 51 sociétés**. Ceux qui avancent passent directement de « Lead à traiter » à « Proposition remise », sans qualification, découverte ou démo enregistrée comme état. Cela ne prouve pas que ces échanges n’ont jamais eu lieu.

**26 sont signés**, dont 21 avec formalités finalisées : ces 21 ne sont pas des signatures supplémentaires. D’autres dossiers sont encore en cours ; un écart entre étapes n’est donc pas automatiquement une perte.

Aucun projet actuel n’est explicitement relié à ces upsells par le lien contrôlé. Leur effet sur les abonnements reste à établir : une extension peut modifier un projet existant. **Un upsell signé n’est pas automatiquement une hausse de MRR déjà active.**

<a id="analyses-attendues"></a>
## 4. Les analyses à conserver

Le cockpit doit couvrir quatre familles :

- **Pipeline :** dossiers et valeur générés, portefeuille ouvert, répartition par source, montant total, montant pondéré, couverture d’objectif et valeur potentielle moyenne annoncée dans la maquette.
- **Progression :** entrées, sorties, conversions, parcours, durées et dossiers stagnants, en nombre et en montant.
- **Histoire :** évolution du pipeline et cohortes de création mensuelles, observées à J+30, J+60 et J+90, en nombres et proportions ouverts/gagnés/perdus.
- **Revenus :** MRR actif, MRR signé, New MRR et churn, avec séparation des effets nouveaux clients, expansions, départs et baisses.

Une *cohorte* regroupe les dossiers créés pendant un même mois. Une *conversion* mesure le passage d’une population vers une étape ou une issue définie. Diviser deux stocks d’étapes différentes ne suffit pas à mesurer une conversion.

La couverture d’objectif, le MRR potentiel moyen proposé dans le brief et le calcul d’activité nécessaire pour atteindre le « BP » restent à préciser. ADV n’est pas traité comme un KPI ; l’utilisateur suggère « Administration des ventes », sens à confirmer dans ce brief.

### Pondérer le pipeline

Toutes les opportunités ouvertes ne seront pas gagnées. La pondération utilise donc la **probabilité de signer finalement depuis l’étape actuelle**, et non la probabilité de passer seulement à l’étape suivante.

**Pipeline pondéré = somme de (montant de chaque dossier ouvert × probabilité de signature).**

Exemple fictif : deux affaires de 1 000 €, pondérées à 20 % et 80 %, donnent 1 000 € pondérés pour 2 000 € potentiels. C’est une estimation, pas du revenu acquis. Si le montant initial est une valeur totale de contrat, le résultat reste une valeur de contrat estimée : il ne devient pas du MRR.

Le sens de la probabilité est décidé. La pertinence des coefficients fournis, leur source et leur application aux upsells restent à confirmer.

<a id="revenus"></a>
## 5. MRR et churn : expliquer les mouvements du portefeuille

Le **MRR** est un montant de revenu récurrent ramené à un mois. Le MRR actif sera une **photographie de fin de mois, sans prorata journalier**, fondée sur les lignes d’abonnement Boond reliées aux projets.

| Mesure | Question à laquelle elle répond |
| --- | --- |
| MRR actif | Quelle valeur mensuelle représentent les abonnements actifs à la clôture ? |
| MRR signé | Quelle valeur mensuelle récurrente a été engagée commercialement pendant le mois ? |
| New MRR | Quel MRR supplémentaire est actif à la clôture, venant des entrants/retours (New) et des hausses des clients existants (Upsell) ? |
| New MRR filtré sur Upsell | Quelle hausse nette a effectivement été ajoutée au MRR des clients restants ? Cette composante est incluse dans le New MRR total. |
| Churn clients | Combien de clients ont arrêté ou n’ont pas renouvelé leur abonnement ? |
| Churn MRR | Combien de MRR avons-nous perdu par départs et par baisses d’abonnement ? |

Le signé et les mouvements sont les valeurs **du mois**, arrêtées à sa clôture ; ce ne sont pas des stocks cumulés d’anciennes signatures. Une signature est reconnue dès l’entrée dans « Signé — formalités à finaliser ». Pour un upsell, le montant retenu dans l’exemple est le supplément mensuel vendu : 150 − 100 = **50 €/mois**. La donnée source prouvant ce montant reste à établir. Pour le case, les clients qui reviennent après un churn contribuent au **New MRR**, comme les nouveaux entrants dans la base active. Cela ne transforme pas automatiquement un ancien client en client acquis pour la première fois. **New MRR total = New + Upsell.** Le filtre **New / Upsell** permet d’analyser les composantes : New comprend les entrants et retours après churn ; Upsell comprend les hausses nettes des clients restants. L’ancien libellé Expansion reste un synonyme de la composante Upsell, pas un apport à additionner au total.

**Les encaissements sont exclus du périmètre**, par décision utilisateur. Une ligne d’abonnement ne prouve pas un paiement. Le scénario ancien « sans churn ni New MRR » reste une option, pas un indicateur obligatoire.

<a id="churn"></a>
**Nomenclature résolue à l’échange 24 :** l’utilisateur inclut explicitement les upsells dans New MRR, avec filtre New / Upsell. Le supplément de 50 € reste la valeur retenue pour l’upsell 100 → 150 €/mois. MRR signé et effet actif restent distincts ; la hausse active figure une seule fois dans New MRR total. [DU-38](questions_decisions.md#du-38).

### Deux explications possibles d’une baisse de revenu

Nous retenons pour le case :

**Churn MRR = MRR perdu avec les clients partis + MRR perdu par baisse d’abonnement chez les clients restants.**

Un **client actif** est une société ayant au moins un abonnement en cours à la clôture. Une baisse peut produire du churn en euros sans départ de client.

Pour ce case, les mouvements sont calculés sur le **MRR total de chaque société entre deux fins de mois**. On additionne ses lignes avant de comparer : +100 € sur une ligne et −40 € sur une autre donnent **60 € d’expansion nette**, sans churn MRR pour cette société. En revanche, les gains d’un client ne compensent pas les pertes d’un autre. Le New MRR total regroupe New (entrants et retours) et Upsell (hausses nettes des restants) ; aucune de ces composantes ne réduit le montant des pertes des autres sociétés.

> **Exemple fictif :** on part de 1 000 € de MRR. On ajoute 250 € de New MRR total : 200 € de composante New et 50 € de composante Upsell active. On perd 100 € avec des clients partis et 40 € avec des abonnements réduits. Le MRR final est de **1 110 €**, mais le churn MRR est de **140 €**, décomposé en 100 € et 40 €.

Dans cet exemple, le New MRR total vaut désormais 250 € : `1 000 + 250 − 1 110 = 140 €` de churn. Ne retrancher que la composante New de 200 € masquerait les 50 € d’upsell. Les deux composantes restent accessibles séparément par filtre.

L’analyse doit montrer **les clients partis et les clients qui réduisent leur abonnement**, ainsi que les montants associés. Les départs suivis d’un retour dans le même mois sont **hors périmètre de l’analyse des mouvements du case**. Les photos de clôture restent conservées ; cette simplification ne signifie pas qu’aucun événement n’a eu lieu. Les questions sur les réactivations, le calcul par ligne ou par client et les mouvements intra-mois sont ajoutées au [registre métier raw](../raw_intent/questions_metiers.md#complements-echange-22) pour une confirmation en situation réelle.

## 6. Lire et comparer les résultats

Un **stock** est une photo à une date ; un **flux** décrit les événements d’une période ; une **durée** mesure un temps entre événements. Les stocks de plusieurs mois ne s’additionnent pas comme des ventes du mois.

Les conventions d’attribution proposées par l’utilisateur sont :

- pipeline : équipe responsable à la date observée ;
- signature : équipe au moment de la signature ;
- génération : équipe à l’entrée retenue dans le funnel ;
- acquisition : un canal par opportunité, fixé à cette entrée, avec les autres origines conservées séparément.

Le champ qui donnera ce canal et les codes inclus dans « Inbound » restent à choisir. Les axes équipe, source, type de vente, étape et cohorte s’appliquent seulement aux mesures où ils ont un sens. **Le bloc MRR actif et churn reste global : le filtre équipe ne s’y applique pas pour le moment.** Le MRR signé et ses objectifs commerciaux restent suivis par équipe.

**Cinq ans d’agrégats** sont retenus. La conservation des détails reste ouverte. Jour/semaine/mois d’analyse, fréquence de recalcul et fraîcheur des sources restent trois sujets distincts. Les hypothèses de conservation ne constituent pas une conformité juridique vérifiée.

<a id="avant-specifications"></a>
## 7. Ce qui manque avant les spécifications techniques

**Nous pouvons avancer avec les décisions prises. Les points ci-dessous empêchent encore de fixer certains calculs, pas tout le projet.**

1. **Les populations et les montants du pipeline.** L’entrée est fixée à la création Boond, sans attendre la démo. Restent les types inclus dans chaque objectif, la valeur à cette entrée, les réouvertures et la preuve des dates. [Questions](questions_decisions.md#qm-06).
2. **Les preuves de démo et les durées.** Le compteur d’objectif porte sur les RDV réellement réalisés. Il reste à identifier la preuve de tenue, dédupliquer/relier les actions et vérifier leur lien aux sociétés. « Nb In demo » compte les sociétés distinctes, décision de l’échange 23. Les événements et calendriers des durées restent à définir. [Questions](questions_decisions.md#qc-02).
3. **Les règles d’abonnement et les montants signés.** Quels états/bornes rendent une ligne active, notamment pause ou gratuité ? Quelle donnée prouve le montant mensuel signé ? Pour un upsell de 100 à 150 €/mois, le case retient le supplément de 50 €, pas le total de 150 €. L’échange 24 précise que l’upsell est une composante de New MRR, filtrable séparément. L’événement de signature, le client actif et l’inclusion des retours dans New MRR sont désormais décidés pour le case. [Questions](questions_decisions.md#qm-04).
4. **La continuité et les corrections du portefeuille.** Comment relier une extension commerciale à son effet réel, identifier les lignes qui se remplacent et traiter les corrections rétroactives ? Le calcul net par société est choisi ; les départs-retours dans le même mois sont exclus de l’analyse du case. [Upsells](questions_decisions.md#qc-11) · [Churn](questions_decisions.md#qc-12).
5. **Les conventions restantes de comparaison.** Choisir les coefficients, le champ canal, les codes Inbound, le mapping des équipes, l’objectif de couverture et la formule du MRR potentiel moyen proposé. Les objectifs restent contrôlés simplement à fin de mois. [Registre](questions_decisions.md).
6. **La couverture de l’histoire et les contraintes.** Vérifier ensuite les liens, les dates disponibles, la fraîcheur et la conservation des détails. Une absence de trace ne prouve pas l’absence d’un événement ; une limite de données n’efface pas le besoin.

Les seuils de stagnation et de perte « trop importante » restent aussi ouverts. L’utilisateur peut arbitrer ces sujets par étapes ; une réponse partielle ne ferme pas le reste.

## 8. Les deux niveaux de lecture

- **Pour relire le besoin :** cet intent et le [catalogue humain](catalogue_indicateurs.md).
- **Pour préparer les spécifications :** [intent IA](intent_ia.md), [catalogue IA](catalogue_indicateurs_ia.md) et [questions/décisions](questions_decisions.md).
- **Pour retrouver les échanges :** [journal commun](ia_assistant_story.md).

Les pistes supplémentaires des visualisations et les mesures de l’ancien SQL restent identifiées séparément dans les catalogues. Elles ne deviennent pas des obligations par leur seule présence.

**Base visuelle du dashboard V1 :** [maquette v2](maquettes/dashboard_synthese_v2.png) et [note de lecture](maquettes/dashboard_synthese_v2.md). Objectifs et MRR/churn conservés ; grand tunnel central avec choix local de mesure. Les chiffres et le parcours illustratif ne valident pas les règles encore ouvertes.

**Inventaire de travail :** [table des champs et correspondances ClickHouse](correspondance_champs_clickhouse.md). Quatre colonnes : champ théorique, équivalents ou calculs, tables sources et décomposition des entrées nécessaires. L’[inventaire des sources du staging](inventaire_sources_staging.md) regroupe ensuite les colonnes physiques par table, avec les clés et l’historique utiles. La synthèse ne limite pas le détail souhaité. Une nouvelle architecture est proposée à l’échange 15 ; elle n’est pas encore validée ni implémentée.

**Construction des données — échange 12.** Nous pouvons historiser les sources qui ne le sont pas, ajouter les métadonnées d’import, construire les référentiels techniques utiles (date/country) et produire les champs dérivés/KPI par transformations et croisements entre staging, intermédiaire et mart. L’absence d’une colonne KPI ou d’un calendrier source n’est pas un blocage. Les dates d’import restent distinctes des dates métier ; l’historique créé ne reconstitue pas un passé jamais capturé. Les règles métier et preuves manquantes restent signalées. [Décision DCI-12](questions_decisions.md#dci-12) · [Travail à notre charge](inventaire_sources_staging.md#constructions-techniques).

**Préservation des versions — échange 13 :** le [cadre incrémental CDC](inventaire_sources_staging.md#incremental-cdc) consigne les principes utilisateur de chargement complet puis reprise avec recouvrement, déduplication et conservation des suppressions. La méthode par table et ses tests restent à valider ; les définitions des KPI restent inchangées. [DCI-13](questions_decisions.md#dci-13).
