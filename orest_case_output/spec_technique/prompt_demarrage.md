# Prompt de démarrage — nouvelle discussion de spécification

Copier le texte ci-dessous dans une nouvelle discussion. Ce fichier est une consigne de démarrage, pas la spécification technique.

```text
Nous commençons la spécification technique de mon case Analytics Engineer.

La consolidation de l’intent est terminée. Ce nouveau chat doit s’appuyer sur les documents du projet, sans supposer qu’il connaît l’historique. Certaines questions métier restent ouvertes : la clôture de l’intent ne les a pas automatiquement résolues.

OBJECTIF

Produire une spécification technique complète, cohérente et directement utilisable par une IA pour coder les modèles dbt/ClickHouse : sources, staging, intermédiaire, faits, dimensions, DTR et datasets alimentant les dashboards.

La spécification doit expliquer précisément quoi construire, pourquoi, avec quelles données, quels calculs, dans quel ordre et comment vérifier le résultat. Elle doit permettre une implémentation sans avoir à inventer des clés, jointures, règles de calcul ou conventions temporelles.

Le travail de ce chat porte sur la spécification, pas encore sur l’implémentation des modèles.

1. EMPLACEMENTS

Racine du projet :
C:\Users\orest\Desktop\use-case-analytics-engineer\use-case-analytics-engineer

Dossier de travail existant :
C:\Users\orest\Desktop\use-case-analytics-engineer\use-case-analytics-engineer\orest_case_output\spec_technique

Tous les chemins relatifs ci-dessous partent de la racine du projet.

Inspecte les instructions locales applicables, l’état Git et les fichiers existants. Préserve le travail présent et les modifications sans rapport avec cette tâche. Ne recrée pas le dossier et n’écrase pas son contenu.

2. DOCUMENTS À LIRE

Commence par les conventions :
- orest_case_output/spec_technique/00_conventions.md

Puis lis le besoin et ses décisions actuelles :
- orest_case_output/clean_intent/intent.md
- orest_case_output/clean_intent/intent_ia.md
- orest_case_output/clean_intent/liste_kpi_humaine.md
- orest_case_output/clean_intent/catalogue_indicateurs_ia.md
- orest_case_output/clean_intent/questions_decisions.md

Lis ensuite les correspondances, le staging et l’architecture proposée :
- orest_case_output/clean_intent/correspondance_champs_clickhouse.md
- orest_case_output/clean_intent/inventaire_sources_staging.md
- orest_case_output/clean_intent/architecture_modele_proposition.md

Inspecte VISUELLEMENT les trois maquettes de dashboards et lis leurs notes :
- orest_case_output/clean_intent/maquettes/dashboard_synthese_v2.png
- orest_case_output/clean_intent/maquettes/dashboard_synthese_v2.md
- orest_case_output/clean_intent/maquettes/dashboard_durees_etapes_v1.png
- orest_case_output/clean_intent/maquettes/dashboard_cohortes_v1.png
- orest_case_output/clean_intent/maquettes/dashboards_durees_cohortes_v1.md

Les visuels d’architecture peuvent aider à comprendre les modules :
- orest_case_output/clean_intent/maquettes/architecture_modulaire_v2.png
- orest_case_output/clean_intent/maquettes/module_pipeline_detail_v1.png
- orest_case_output/clean_intent/maquettes/module_revenus_detail_v1.png

Ils sont antérieurs à certains arbitrages. Les décisions écrites les plus récentes prévalent sur leurs noms, grains et annotations.

Vérifie également les sources et l’environnement du dépôt :
- README.md
- docs/besoin/expression-de-besoin.md
- docs/besoin/maquette-pipeline.png
- docs/cycle-de-vie.html
- docs/model/model.json
- docs/model/index.html
- docs/model/model.js
- legacy/pipeline_actuel.sql
- dbt/dbt_project.yml
- dbt/pyproject.toml
- dbt/uv.lock
- dbt/profiles.yml
- dbt/models/
- docker/init/01_schema.sql
- Les fichiers de configuration et de connexion utiles effectivement présents.

L’ancien journal du clean intent peut être consulté pour retrouver une décision :
orest_case_output/clean_intent/ia_assistant_story.md

Le dossier raw_intent contient des analyses et preuves complémentaires. Consulte son README et les documents pertinents si une question nécessite de revenir à la source. Ne recopie pas les anciens journaux dans le nouveau.

Signale une source absente. Ne devine ni son contenu ni la disponibilité des données.

3. PRIORITÉS ET CONVENTIONS

Applique 00_conventions.md. Les instructions utilisateur les plus récentes déterminent les choix du case.

Notamment : préfixes de modèles et de schémas, staging 1 pour 1 et colonnes src_, absence de règles métier dans le staging, SQL explicite sans SELECT *, source()/ref(), une règle métier par intermédiaire autant que possible, tests adaptés au grain et descriptions YAML complètes.

Ne transforme pas une proposition d’architecture, une donnée fictive de maquette ou un calcul SQL historique en règle métier validée.

L’architecture préparée constitue le point de départ. Tu peux proposer les adaptations nécessaires pour obtenir un modèle cohérent et couvrir les dashboards ; explique leur justification et leurs conséquences. N’ajoute pas de complexité sans besoin identifiable.

Conserve la granularité utile et l’historisation de toutes les couches. Une décision de reporting au mois n’autorise pas à supprimer les détails nécessaires aux analyses futures. Distingue grain métier et versions techniques.

4. POINTS MÉTIER À NE PAS RÉOUVRIR SANS RAISON

- Entrée du pipeline dès la création dans Boond, après soumission du formulaire ; création et qualification restent distinctes.
- Signature dès « Signé — formalités à finaliser » ; la finalisation des formalités n’est pas une deuxième vente.
- Nombre de démos = RDV réellement réalisés. Nb In demo = sociétés distinctes ayant au moins une opportunité dans la phase Démo.
- Nouvelles ventes et upsells restent distinguables dans le parcours commercial.
- Client actif = société avec au moins un abonnement en cours à la clôture ; critères d’activité des lignes à préciser selon les questions restantes.
- MRR actif fondé sur Boond, photographie de fin de mois, sans prorata journalier.
- Pour le case, mouvements de MRR nets par société entre clôtures ; les gains d’une société ne compensent pas les pertes d’une autre.
- New MRR total = composante New + composante Upsell, avec filtre New / Upsell. New comprend les entrants et retours après churn ; Upsell comprend les hausses nettes actives des clients restants. Ne pas ajouter l’expansion une deuxième fois au total.
- Un upsell de 100 à 150 €/mois apporte 50 € supplémentaires, pas 150 €. Signature et activation restent distinctes.
- Churn MRR = pertes par départs + baisses nettes des clients restants.
- Départs-retours intra-mois exclus du traitement détaillé du case ; encaissements exclus.
- Le bloc MRR actif/churn reste global, sans filtre équipe. Les objectifs commerciaux restent mensuels, par équipe.
- Une cohorte regroupe les opportunités par mois de création ; suivre ouvert/gagné/perdu à J+30/J+60/J+90. Les détails de maturité, d’horizon et de classement encore ouverts doivent être traités explicitement.

Ces rappels ne remplacent pas la lecture des définitions, de leurs limites et des décisions sourcées.

5. INSPECTION DES DONNÉES AUTORISÉE

Tu peux interroger directement ClickHouse et inspecter les tables, schémas et métadonnées si nécessaire. Utilise les connexions/configurations déjà disponibles et des requêtes en lecture seule, ciblées et bornées autant que possible.

Cette autorisation couvre la vérification des types, clés, versions, suppressions, valeurs de statuts, cardinalités, liens entre sources, dates, couverture historique et montants nécessaires à la spécification. N’attends pas ma confirmation pour chaque contrôle de lecture.

Ne lance pas d’installation, d’écriture en base, de modification des sources, de service ou de modèle pour cette phase. N’affiche pas de secrets de connexion.

Conserve les requêtes de contrôle utiles et un résumé de leurs résultats dans la documentation technique, avec leur périmètre. Distingue :
- constat vérifié dans les données ;
- fait documentaire ;
- décision métier ;
- proposition technique ;
- hypothèse ou manque restant.

Une observation ne suffit pas à établir une règle métier générale. Si la base est inaccessible, avance sur les documents et indique précisément ce qui n’a pas pu être vérifié.

Vérifie les versions réellement disponibles avant de recommander une fonction ou une stratégie propre à dbt-clickhouse. Consulte la documentation officielle lorsque nécessaire. Ne confonds pas une version déclarée dans le dépôt avec une version installée.

6. CONTENU ATTENDU DE LA SPÉCIFICATION

A. Vue d’ensemble et dépendances
- Architecture cible par couche et module, avec les dimensions partagées.
- DAG lisible des dépendances et matrice source → modèle → KPI → dashboard.
- Inventaire exhaustif des objets à créer, réutiliser ou adapter.
- Noms et emplacements finaux : fichiers SQL/YAML, modèles dbt et relations ClickHouse. Expliquer la correspondance des schémas dbt avec les bases ClickHouse.
- Ordre de construction et ordre d’exécution, en distinguant dépendances obligatoires et branches indépendantes.

B. Fiche de CHAQUE modèle
- Nom, couche, module, finalité et besoins couverts.
- Grain métier, grain historique, clés d’identité/version et unicité attendue.
- Sources et modèles amont ; correspondances de colonnes, jointures, cardinalités et règles temporelles.
- Liste complète des colonnes : nom, type, nullabilité, description, origine ou formule, valeurs possibles et contraintes.
- Étapes du calcul, conditions, filtres, inclusions/exclusions, cas multiples, inconnus, suppressions et corrections.
- SQL ou pseudocode suffisamment précis pour coder sans inventer de logique ; fournir le SQL détaillé lorsque la transformation est délicate.
- Matérialisation, paramètres, configuration dbt/ClickHouse et justification des choix physiques.
- Historisation, premier chargement, incrémental, recalcul et reprise.
- Mode/fréquence de rafraîchissement et fraîcheur attendue, en signalant les valeurs non décidées.
- Tests, critères d’acceptation, limites et dépendances encore ouvertes.

C. Historisation et incrémental
Reprendre le protocole utilisateur existant : chargement initial complet, reprise depuis le maximum chargé de meta.ts avec recouvrement paramétrable, comparaison >=, déduplication et conservation des suppressions.

Préciser les clés réelles par table, les collisions de timestamps, le cas d’une cible vide, les retards hors fenêtre, les reprises après échec et les corrections rétroactives. Ne pas limiter le flux à hier ni imposer updateDate dans la même journée que meta.ts.

Distinguer historique complet et vue courante : sélectionner la dernière version pertinente avant d’exclure les objets supprimés. Adapter le protocole aux tables particulières et aux sources à historiser nous-mêmes. Ne pas imposer l’incrémental à tous les modèles.

La rétention de cinq ans concerne les agrégats ; la rétention détaillée n’est pas automatiquement décidée.

7. DTR ET DATASETS DES TROIS DASHBOARDS

Le détail des DTR n’a pas été défini dans l’intent. Leur conception fait explicitement partie de cette demande : tu as le besoin, le modèle proposé et les trois maquettes pour les établir.

Pour chaque graphique, carte, tableau, filtre et navigation utile :
- Identifier les faits/dimensions nécessaires.
- Définir la table DTR et le dataset destiné au dashboard, en respectant les préfixes dtr_ et dataset_ et le schéma de couche prévu.
- Préciser le grain, les colonnes, les clés, les dates, les dimensions filtrables et les règles d’agrégation.
- Expliquer ce qui est préparé en dbt et ce qui reste un calcul ou un formatage de restitution.
- Mutualiser les datasets quand cela conserve un grain et des règles compatibles ; ne pas créer automatiquement une table par graphique.

Traiter explicitement :
- Synthèse : objectifs/réalisés, tunnel et ses lectures, MRR/churn, portée des filtres.
- Durées : passages terminés distincts des passages en cours, distributions, ancienneté, seuils paramétrables, canaux et détail des dossiers.
- Cohortes : mois de création, horizons, issues, maturité, couverture et dénominateurs comparables ; ne pas transformer un horizon non atteint en zéro.

Préserver les comptages de sociétés distinctes, les ratios et les montants lors des regroupements et filtres. Ne pas sommer des ratios locaux, des stocks mensuels ou des distincts qui se recouvrent. Pour les statistiques de durée, déterminer le niveau de détail nécessaire à leur recalcul après filtre.

Les chiffres des maquettes sont fictifs. Médiane/P90, seuils, jours calendaires, maturité complète et catégories d’issues encore proposées ne deviennent pas des décisions simplement parce qu’ils figurent dans une image.

8. TESTS, EXÉCUTION ET ACCEPTATION

Définir :
- Tests dbt de données et tests unitaires pertinents, en vérifiant le support effectif de l’adaptateur/version.
- Unicité au bon grain, valeurs obligatoires, domaines, relations et contrôles de cardinalité.
- Cohérence historique, couverture et absence de multiplication des contributions.
- Réconciliation MRR, compatibilité réalisé/objectif, cohérence des cohortes et séparation durée/ancienneté.
- Scénarios de premier chargement, réexécution sans doublons, timestamps identiques, suppression, arrivée tardive, correction et reprise après échec.
- Pour chaque contrôle : objet testé, résultat attendu, gravité d’échec et action prévue.
- Commandes et sélections dbt pour construire, tester, reprendre et reconstruire, avec prérequis et ordre précis.

Ne présente pas un test planifié comme exécuté. Les comparaisons de performance doivent être fondées sur des mesures lorsque disponibles, pas sur une garantie théorique.

9. DOCUMENTS ET NOUVEAU JOURNAL

Travaille dans le dossier spec_technique existant. Garde une organisation simple ; proposition de départ :
- 00_conventions.md : conventions existantes, à appliquer.
- 01_specification_technique.md : architecture, décisions transversales, couverture des besoins et questions restantes.
- 02_catalogue_modeles.md : fiches détaillées de tous les modèles, y compris DTR/datasets.
- 03_execution_tests.md : ordre, commandes, contrôles, scénarios et critères d’acceptation.
- ia_assistant_story.md : historique propre à ce NOUVEAU chat.

Adapte cette organisation seulement si cela améliore réellement la lisibilité, sans multiplier inutilement les documents.

Dans le nouveau journal :
- Conserver intégralement chaque message utilisateur accessible de ce chat, y compris ce prompt.
- Numéroter les échanges et résumer brièvement les réponses IA.
- Distinguer décisions, propositions, questions reportées, fichiers modifiés et vérifications exécutées.
- Ne pas copier les anciens journaux, ni enregistrer de raisonnement interne.
- Ne pas inventer d’information sur le modèle, son effort ou le contexte consommé.

Si le mode Plan est effectivement actif, lire et préparer sans écrire de fichiers. Après passage effectif en exécution, créer les documents et consigner rétroactivement les échanges accessibles de ce nouveau chat. En exécution, commencer directement.

10. FAÇON DE TRAVAILLER

Nous travaillons par itérations. Produis une première version substantielle et concrète, pas seulement un plan ou une liste de questions.

Résous les choix techniques courants avec les preuves disponibles et explique les choix structurants. Pose des questions simples et autonomes uniquement lorsqu’une information métier manque ou qu’un arbitrage change réellement le résultat. N’invente pas la réponse et ne rouvre pas une décision déjà prise sans raison.

Avance sur les parties indépendantes. Pour chaque point restant ouvert, indique les modèles/calculs concernés, la conséquence et ce qui permettrait de le résoudre.

Avant de déclarer la spécification prête à coder, vérifier :
- couverture des KPI et des trois dashboards ;
- cohérence des noms, types, grains, clés, jointures et temporalités ;
- absence de doubles comptes et de cycles de dépendance ;
- stratégie historique et incrémentale définie par modèle concerné ;
- DTR/datasets utilisables avec les filtres attendus ;
- tests et ordre d’exécution exploitables ;
- conventions respectées ;
- choix métier et hypothèses clairement distingués ;
- absence de décisions techniques essentielles laissées implicitement à l’IA qui codera.

Commence par inspecter le dossier, lire les sources et vérifier les points de données nécessaires. Construis ensuite la première version de la spécification et présente les quelques arbitrages qui restent réellement bloquants.
```
