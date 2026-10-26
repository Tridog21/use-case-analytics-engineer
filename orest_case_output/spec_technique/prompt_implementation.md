# Prompt de démarrage — implémentation de la spécification technique v0.2

Copier le texte ci-dessous dans un nouveau chat disposant d’un mode d’exécution. Ce fichier lance l’implémentation, pas une nouvelle phase de cadrage.

````text
Implémente maintenant la spécification technique finalisée de mon case Analytics Engineer, avec dbt et ClickHouse.

Racine du projet :
C:\Users\orest\Desktop\use-case-analytics-engineer\use-case-analytics-engineer

Lis intégralement, dans cet ordre :
1. orest_case_output/spec_technique/00_conventions.md
2. orest_case_output/spec_technique/01_specification_technique.md
3. orest_case_output/spec_technique/02_catalogue_modeles.md
4. orest_case_output/spec_technique/03_execution_tests.md

Les chemins relatifs partent de la racine ci-dessus. Inspecte également les instructions locales applicables, l’état Git, le projet dbt, les connexions et les sources réellement présentes. Préserve toutes les modifications préexistantes et les travaux sans rapport. Consulte le clean_intent, les maquettes et le journal de spécification si un détail nécessite sa provenance ; les décisions finales de 01§7/D16–D30 prévalent sur les anciennes questions encore visibles dans ces sources.

OBJECTIF ET AUTORISATION

Le cadrage est terminé. Les arbitrages ont été tranchés sous ma délégation ; ne relance pas un questionnaire métier. Commence directement à coder et poursuis jusqu’à une implémentation testée et documentée. Si le mode Plan est imposé par l’application, respecte-le et signale uniquement cette contrainte réelle.

Produis dans dbt/ les73 modèles et leurs YAML complets, les sources, macros, paramètres versionnés, tests de données/unitaires, requêtes de contrôle et le runner manuel à manifests/reprises/publication prévu par la spécification. Les datasets et leurs contrats de requête couvrent les trois dashboards ; cette demande n’inclut pas la construction de l’interface Superset.

Tu peux utiliser les connexions et services déjà disponibles, créer/mettre à jour les modèles dans les bases analytiques stg_*,dwh_*,dtm_*,dtr_* spécifiées, et exécuter dbt ainsi que les objets temporaires de test/validation de l’adaptateur dans les cibles analytiques. raw,hubspot,ref restent strictement en lecture seule. Les scénarios de modification/suppression/retard doivent utiliser des fixtures et relations de test, sans modifier les sources du case. N’installe ni ne démarre de service pour contourner un manque ; utilise d’abord le venv et ClickHouse existants, sans exposer de secrets.

CONTRATS À APPLIQUER

- Quinze staging1pour1,179 colonnes source, aliases src_ documentés ; aucune règle métier au staging. SQL explicite sans SELECT étoile, source()/ref()/this, descriptions YAML de toutes les tables/colonnes.
- Historique CDC complet et suppressions conservées ; reprise>=watermark−recouvrement, cible vide, anti-jointure idempotente, borne de tentative durable et scan complet de rattrapage. Aucun filtre limité à hier ni contrainte updateDate=jourCDC.
- Captures complètes HubSpot/ref, changements et retoursA→B→A ; ne pas produire une disparition à partir d’une capture échouée. Révisions dérivées par empreinte immuable de run, mêmes métadonnées à la reprise ; faits en vues, datasets sur publication acceptée. Publier int_publication uniquement après tous les contrôles, avec disponibilités par mesure même sur détail vide.
- D15 admet meta.ts comme date OBSERVÉE des transitions/signatures constatées, avec qualité CDC. Aucune date inventée pour les premières traces avancées ou les17 dossiers14sans1.
- D16 : hypothèse de couverture jusqu’au30septembre2026, clôture Europe/Paris, borne exclusive2026-09-30T22:00Z ; aucune reconstitution des lacunes individuelles. D20 : EUR par hypothèse de case, sans en déduire la mensualité d’un montant CRM.
- Applique exactement les règles finalisées01§7 : premières signatures/réouvertures, états à horizon, chemins observés du tunnel, barème ref rétrospectif tracé, populations4/7, BU12LA/13SMB/15KAM distincte, ES nonattribuée, origine à création/Inbound1,2,3, équipe à entrée du passage, seuil21jours strict et classes continues. Aucun fallback implicite vers une autre source.
- Les preuves manquantes ne sont pas de nouveaux arbitrages : MRR signé, démos réellement tenues et chaînage non prouvé restent NULL/statuts explicites. Les fonctionnalités non activées D28 restent inventoriées ; implémente leurs schémas et disponibilités, sans chiffres fictifs ni table oubliée. Une comparaison avec cible reste indisponible si l’unité ou le réalisé n’est pas prouvé ; ES ne devient pas0.

EXÉCUTION ET VALIDATION

Vérifie les versions réellement installées avant toute stratégie spécifique. Les versions précédemment observées étaient ClickHouse25.11.9.34,dbt-core1.11.12,dbt-clickhouse1.10.1 ; ce sont des constats antérieurs, pas une garantie sur ce nouveau chat.

Suis les phases03 : captures par source et succès manifest, vars de calcul figées, construction topologique des dimensions/intermédiaires/faits, DTR, tests du candidat, bootstrap initial du pointeur si absent, vues, contrôle de qualité puis publication isolée. Les commandes et scripts de la spécification sont des prescriptions à implémenter, pas des fichiers supposés exister ni des tests déjà passés.

Teste notamment premier chargement/cible vide, réexécution sans doublons, collisions, suppressions, retards dans/hors fenêtre, reprises après écriture partielle, A→B→A, corrections, bornes Paris/changements d’heure, jointures sans multiplication, seuils/quantiles, cohortes immatures et MRR net par société. Les testsT01–T65 incluent les décisions finales. Un cas non vérifiable sur les sources se vérifie par fixture ; ne présente pas un résultat attendu comme exécuté.

Vérifie les73 relations,179 colonnes source, types/nullabilités, clés/grains, sources/ref et DAG, métadonnées de run, conservation des révisions, couverture des KPI et trois dashboards, ratios/distincts/stocks non additifs et les indisponibilités intentionnelles. Distingue complétude de code et disponibilité des mesures. Ne supprime pas un modèle difficile ni une limitation pour obtenir artificiellement des tests verts.

JOURNAL ET LIVRAISON

Crée orest_case_output/implementation/ia_assistant_story.md pour ce NOUVEAU chat : conserve chaque message utilisateur accessible intégralement, numérote les échanges et résume les réponses IA, décisions, fichiers et vérifications. N’y recopie pas les anciens journaux et n’y enregistre aucun raisonnement interne ni information supposée sur le modèle ou son contexte.

Consigne les commandes/résultats réels, prérequis et reprises dans orest_case_output/implementation/rapport_execution.md. Corrige les erreurs techniques rencontrées sans remettre les définitions métier en discussion. Si une incompatibilité impose une adaptation du contrat, apporte la correction minimale sourcée dans les documents et son test, avec justification ; ne prétends pas avoir validé une étape bloquée.

À la fin, livre les fichiers, les résultats de build/tests effectivement obtenus, les commandes de reproduction, les mesures volontairement indisponibles et les seuls blocages techniques externes éventuels. Un plan, un squelette ou une liste de tâches ne constitue pas l’implémentation terminée.
````
