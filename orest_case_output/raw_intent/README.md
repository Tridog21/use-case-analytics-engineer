# Dossier raw_intent — cadrage établi

L’établissement du raw intent est terminé à la demande de l’utilisateur. Ce dossier regroupe les travaux de cadrage et leurs preuves. Les questions métier ouvertes restent ouvertes : la clôture documentaire ne vaut pas validation de toutes les définitions ni sélection d’une V1.

## Ordre de lecture

1. [Raw intent](raw_intent.md) : contexte, hypothèses, questions et décisions ; section 12 pour la liste exhaustive des souhaits, section 13 pour la réponse Q10 et la clôture de cette phase.
2. [Questions métier](questions_metiers.md) : les six arbitrages restant à poser/confirmer, dont les conventions financières, les probabilités et l’entrée dans le pipeline qualifié.
3. [État des lieux Q10](etat_des_lieux_Q10.md) : désaccord entre cycle, maquette et SQL existant ; observations enregistrées et limites ; aucune frontière qualifiée imposée.
4. [Analyse du SQL historique](analyse_pipeline_actuel.md) : code original, explication par bloc, KPI/grains/périodes, limites et définitions implicites.
5. [Funnel global](cycle_hypotheses/01-parcours-et-frictions.html) et [tunnels par étape](cycle_hypotheses/02-tunnels-par-etape.html) : supports hypothétiques, sans taux ou volumes représentés comme mesurés. [PDF global](cycle_hypotheses/01-parcours-et-frictions.pdf), [PDF détaillé](cycle_hypotheses/02-tunnels-par-etape.pdf), [hypothèses structurées](cycle_hypotheses/hypotheses-source.json) et [trace de création](cycle_hypotheses/trace-creation.md).

## Preuves et reproduction Q10

- [Résultats enregistrés](preuves_Q10.json) : résultats du contrôle de l’autre discussion, datés du 24 octobre 2026, session UTC. Leur population et leurs limites sont décrites dans le diagnostic.
- [SQL joint au dossier](explore_q10_pipeline_entry.sql) : copie exacte de [la source technique](../../docs/sql/explore_q10_pipeline_entry.sql), maintenue dans son emplacement du projet. La commande du diagnostic utilise cet original depuis la racine du dépôt.
- [Exploration des compteurs et démos](../../docs/sql/explore_counting_grains.sql) : autre source technique citée par le diagnostic ; elle reste dans le projet.

Les fichiers JSON, PDF et images ont été conservés sans modification. Le déplacement des documents Markdown a seulement nécessité le recalcul des liens ; le raw intent a ensuite reçu la réponse de Q10 et la clôture. Aucune requête n’a été relancée pendant cette organisation.

## Suite du rendu

Le [guide général](../how_to_read.md) et l’[historique de ce chat](../ia_assistant_story.md) restent à la racine du dossier de restitution. Les modèles et autres fichiers techniques restent dans les emplacements du projet. La prochaine phase attend les instructions de l’utilisateur.
