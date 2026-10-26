# Guide de lecture du rendu

Statut : établissement du raw intent terminé ; dossier regroupé dans `raw_intent/`. Le rendu général reste en cours : modèles, résultats finaux et reproduction du travail à compléter avant la restitution.

## Par où commencer

Commencer par [le dossier raw_intent](raw_intent/README.md), puis [le document de cadrage](raw_intent/raw_intent.md). La section 12 contient la liste exhaustive des souhaits ; la section 13 reprend le diagnostic Q10 et clôt l’établissement du raw intent. Les arbitrages métier encore ouverts sont conservés dans la liste dédiée, notamment QM-06 pour l’entrée dans le pipeline qualifié. La clôture du cadrage ne vaut pas spécification technique validée. Le présent guide et l’historique de ce chat restent à la racine pour la suite du case.

## Ordre de consultation

1. [Cadrage et cycles de questions/réponses](raw_intent/raw_intent.md) : comprendre ce qui est connu, retenu, hypothétique ou encore ouvert.
2. Les deux supports du cycle de vie, détaillés plus bas : visualiser le parcours et ses sous-étapes hypothétiques.
3. [Questions à poser aux métiers](raw_intent/questions_metiers.md) : passages entre étapes, attribution multicanal, arbitrage des définitions, conventions MRR/paiements et sens des probabilités, dont le cas du 15 mars au 15 avril ; questions encore à poser, aucun envoi effectué.
4. [Analyse de la requête actuelle](raw_intent/analyse_pipeline_actuel.md) : code original, explication par bloc, KPI, grains, périodes, limites et définitions implicites. Il s’agit d’une analyse statique, sans correction ni benchmark.
5. [Diagnostic Q10 et preuves enregistrées](raw_intent/etat_des_lieux_Q10.md) : création du besoin, frontière qualifiée encore ouverte, requêtes et résultats du contrôle de l’autre discussion.
6. [Historique de ce chat avec l’IA](ia_assistant_story.md) : messages utilisateur intacts, interventions IA résumées et changements de configuration connus.

À compléter : insérer dans ce parcours les modèles et résultats lorsqu’ils seront livrés.

## Modèles et résultats

Pour les ventes additionnelles, lire [l’analyse du funnel upsell](raw_intent/analyse_funnel_upsell.md) :
parcours observés, comparaison aux nouveaux clients, issues et limites des liens vers
HubSpot et les abonnements. Les requêtes et résultats de contrôle sont liés au document.

Pour comprendre le désaccord sur l’ouverture du besoin et du pipeline qualifié,
lire [l’état des lieux Q10](raw_intent/etat_des_lieux_Q10.md) : sources, logique SQL existante,
observations en base, limites historiques et arbitrages encore ouverts. Les preuves
et les requêtes de reproduction y sont liées ; aucune frontière métier n’est imposée.

À compléter : chemins des modèles dans le projet et emplacements des résultats, avec leur rôle. Les fichiers techniques restent dans les emplacements appropriés du projet.

## Reproduire et tester

L’environnement Superset local est documenté dans [le guide d’installation](../docs/superset.md).
Il configure l’accès en lecture seule à ClickHouse ; aucun dashboard métier ni modèle
dbt n’est fourni par cette installation. Le parcours de reproduction des résultats
devra être complété une fois ces éléments réalisés.

À compléter : prérequis, versions verrouillées, préparation de l’environnement, commandes à exécuter dans l’ordre et contrôles attendus. Vérifier l’état de Docker et de ClickHouse avant toute commande nécessitant la base. Le diagnostic Q10 cite un contrôle exécuté dans une autre discussion ; ses requêtes et résultats sont conservés dans le dossier de cadrage. Aucune commande de base n’a été relancée pendant le regroupement.

## Hypothèses et limites

Les hypothèses du cycle de vie, les décisions de cadrage utilisateur et les questions encore ouvertes figurent dans [raw_intent.md](raw_intent/raw_intent.md). Les arbitrages confiés aux métiers sont suivis dans [questions_metiers.md](raw_intent/questions_metiers.md). Les limites propres au reporting existant et leurs preuves sont détaillées dans [analyse_pipeline_actuel.md](raw_intent/analyse_pipeline_actuel.md).

À compléter : actualiser ces références et leurs statuts à la clôture des prochains cycles et lors de la livraison des modèles.

## Échanges avec l’IA

L’historique de ce chat et le suivi de la configuration connue sont conservés dans [ia_assistant_story.md](ia_assistant_story.md).

À compléter : rôle de l’IA dans les travaux effectivement réalisés et vérifications effectuées par le candidat.

## Vérification avant restitution

- [ ] Renseigner toutes les sections « À compléter ».
- [ ] Vérifier l’ordre de lecture et tous les chemins et liens.
- [ ] Documenter les commandes de reproduction et les tests réellement exécutés.
- [ ] Renseigner les hypothèses et limites.
- [ ] Vérifier que l’historique de l’IA est à jour.

Rappel : ce guide est encore incomplet. Il doit être terminé avant la restitution finale.

## Supports issus des croquis du candidat - 24 octobre 2026

Deux supports complémentaires, présentant des hypothèses et non des résultats mesurés :

1. [Funnel global et points de friction - version interactive](raw_intent/cycle_hypotheses/01-parcours-et-frictions.html) : lecture globale du cycle, incidents possibles et frontières à clarifier. Cliquer une étape pour consulter les détails. [Version PDF, une page paysage](raw_intent/cycle_hypotheses/01-parcours-et-frictions.pdf).
2. [Funnels par étape - version interactive](raw_intent/cycle_hypotheses/02-tunnels-par-etape.html) : dix vues détaillées, avec les sous-étapes envisagées, les questions et des mesures candidates sous conditions. [Version PDF, dix pages paysage](raw_intent/cycle_hypotheses/02-tunnels-par-etape.pdf).

Ouvrir les fichiers HTML dans un navigateur : ils fonctionnent hors ligne, sans Docker, installation ni connexion. Conserver les deux fichiers dans le même dossier pour utiliser leur lien de navigation réciproque. Les PDF sont directement joignables à la restitution.

Les éléments issus du cycle fourni sont distingués des hypothèses personnelles. Aucun taux ni volume n'a été calculé pour ces supports. Les mesures et questions ajoutées sont des propositions de cadrage ; elles n'attestent pas la disponibilité des événements dans les données.

