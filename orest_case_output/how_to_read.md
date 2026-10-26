# Guide de lecture du rendu

Commencer par [la restitution](START_HERE.pdf), puis [la préparation de lecture et de Superset](PREPARATION_RECRUTEUR.pdf).

La restitution commence par l’explication du candidat à destination des recruteurs, suivie du guide de lecture. Le cycle final autonome de tests/recette n’a pas été réalisé ; les contrôles déjà effectués pendant l’implémentation restent documentés.

## Les quatre étapes

1. [Raw intent : récapitulatif](raw_intent/recap_etape.pdf), [historique complet](raw_intent/historique_discussion.pdf), [cadrage](raw_intent/raw_intent.md).
2. [Clean intent : récapitulatif](clean_intent/recap_etape.pdf), [historique complet](clean_intent/historique_discussion.pdf), [intent humain](clean_intent/intent.md), [KPI](clean_intent/liste_kpi_humaine.md).
3. [Spécification : récapitulatif](spec_technique/recap_etape.pdf), [historique complet](spec_technique/historique_discussion.pdf), [spécification v0.2](spec_technique/01_specification_technique.md).
4. [Implémentation : récapitulatif](implementation/recap_etape.pdf), [historique complet](implementation/historique_discussion.pdf), [rapport d’exécution](implementation/rapport_execution.md).

## Regarder les dashboards

Sans installation : [Synthèse](clean_intent/maquettes/dashboard_synthese_v2.png), [Durées](clean_intent/maquettes/dashboard_durees_etapes_v1.png), [Cohortes](clean_intent/maquettes/dashboard_cohortes_v1.png).

Avec interaction : suivre [PREPARATION_RECRUTEUR.pdf](PREPARATION_RECRUTEUR.pdf). Le code reste dans [dbt](../dbt/) et les assets dans [superset](../superset/). Le dépôt complet est nécessaire. Les trois dashboards ont été construits ; le démarrage de l’environnement seul ne reconstruit pas les modèles sur une nouvelle machine.

## Organisation et traces

Chaque étape contient son récapitulatif et sa transcription PDF, ainsi que leurs versions texte. Les journaux synthétiques existants sont conservés. Le journal initial de raw_intent est également disponible dans raw_intent/ia_assistant_story.md ; sa copie historique à la racine reste présente pour conserver les anciens liens.

Les conventions préparées en fin de clean intent restent classées dans spec_technique/00_conventions.md. L’ancien guide est conservé dans archives_documentaires/. Voir ORGANISATION_DOSSIER.txt et MANIFESTE_HISTORIQUES.json pour les détails.

## Questions métier et décisions clés

[Questions pour les métiers et quinze questions critiques approfondies](raw_intent/QUESTIONS_METIERS_ET_CRITIQUES.pdf) : complément en deux parties, avec les réponses retenues et leurs limites.
