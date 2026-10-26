# Maquette de synthèse — proposition graphique 2

**Actualisation métier — échange 24 :** la PNG et son prompt ci-dessous sont conservés comme historique. New MRR inclut désormais New et Upsell, filtrables. Une future révision devra afficher soit le total New MRR, soit New + Upsell, sans ajouter Expansion au total. Les valeurs fictives de la cascade 20 k€ New + 5 k€ Expansion deviennent 25 k€ de New MRR total, décomposé en 20 k€ New et 5 k€ Upsell. [DU-38](../questions_decisions.md#du-38).

[Visuel v2](dashboard_synthese_v2.png) · Version précédente : fichier absent lors de la vérification de l’échange 13 · [Intent](../intent.md) · [Catalogue](../catalogue_indicateurs.md)

## Changements demandés à l’échange 8

- Conserver les quatre comparaisons réalisé/objectif et le bloc MRR/churn, appréciés explicitement par l’utilisateur. Les chiffres restent fictifs ; l’approbation de présentation ne valide pas les définitions ouvertes.
- Remplacer toute la partie centrale par un seul grand tunnel de conversion.
- Ajouter un sélecteur de mesure propre au tunnel, ainsi que le choix nouveaux clients/upsells.
- Garder la synthèse globale/par équipe ; introduire un onglet distinct « Analyse individuelle » pour comparer individu et équipe, sous réserve de faisabilité. Cette dernière demande remplace l’exclusion générale précédente, mais ne crée pas d’objectifs individuels.

## Proposition représentée

Le mode affiché est « Opportunités ». Exemple fictif d’une même cohorte de 100 dossiers observée au 30 septembre : 100 ont atteint Qualification, 70 Découverte, 50 Démo, 35 Proposition, 25 Closing et 20 Signé. Les pourcentages de passage sont 70 %, 71 % arrondi, 70 %, 71 % arrondi et 80 %. La conversion totale illustrative est 20/100 = 20 %.

C’est un exemple de parcours, pas une décision de frontière qualifiée ni d’ordre obligatoire des étapes. Les dossiers n’ayant pas atteint l’étape suivante peuvent être en attente ou avoir quitté le parcours. L’exemple suppose les populations emboîtées ; les sauts, retours et différences de couverture nécessitent leurs règles avant calcul réel. Les largeurs du visuel généré sont schématiques, pas une échelle analytique certifiée.

Les options « Taux de passage », « Montants », « Durées » sont des **propositions IA de modes**, à définir. Un montant ou une durée ne devient pas un taux de conversion. Pour ces modes, conserver le parcours comme structure de lecture mais adapter les valeurs et la représentation : ne pas imposer un rétrécissement monotone à des durées ou à des montants, ne pas calculer automatiquement les taux sur ces mesures. La date du montant, le calendrier et les statistiques de durée restent ouverts. Le menu n’annonce aucune formule déjà validée.

Le changement de type doit adapter le parcours aux upsells, sans leur imposer le funnel nouvelles ventes. Le filtre du tunnel ne filtre pas implicitement le portefeuille d’abonnements ni les quatre objectifs. Le périmètre de chaque réalisé/objectif reste à définir conformément au catalogue.

Les cohortes détaillées, les démos, l’évolution du pipeline pondéré, la génération par source, la stagnation, la couverture et l’ADV restent au catalogue et dans les onglets d’approfondissement : les retirer du centre de la synthèse ne supprime pas ces attentes.

L’onglet individuel est un emplacement proposé, pas une page construite. Comparateur d’équipe, mesures admissibles, règle d’attribution et faisabilité restent en QC-14. Aucune cible personnelle, aucun classement ni score de personnes ajouté.

## MRR et objectifs conservés

Objectifs illustratifs : 18 000/20 000 = 90 %, 240 000/300 000 = 80 %, 162 000/180 000 = 90 %, 42/50 = 84 %. Le compteur de démos reste à confirmer.

MRR : 100 000 + 20 000 + 5 000 − 10 000 − 4 000 = 111 000 €. Churn MRR = 14 000 €, composé de départs (10 000 €) et de baisses (4 000 €), sans compensation par nouvelles entrées ou expansions. Les nombres de clients illustratifs sont sans chevauchement.

## Statut et génération

Version graphique v2, pas sélection de livraison V2. Édition par **imagegen intégré**, à partir de la première maquette non annotée, suivant les zones indiquées par l’utilisateur. Image originale et première maquette conservées. Aucun changement des sources, données, SQL ou services.

## Prompt final utilisé

```text
Edit the supplied unannotated dashboard mockup to produce VERSION 2. Use the reference as the exact visual design foundation: clean white cards, navy French typography, teal, blue and restrained orange, high-quality legible enterprise analytics UI. Same flat front-facing landscape screen, same visual hierarchy. Preserve the top monthly target cards and the bottom MRR & churn section, including their correct fictional numbers. Replace ALL of the middle charts with ONE LARGE CONVERSION FUNNEL CARD. No red/blue/brown pen marks, no annotations copied from the user's drawing. The edited deliverable must be a clean finished mockup, not annotated.

KEEP:
Header "BOOND / ANALYTICS", "Cockpit commercial", subtitle "Comprendre le pipeline. Expliquer les mouvements du revenu."
Badge "MAQUETTE • DONNÉES FICTIVES".
Top filters "Septembre 2026", "Vue globale" with small "Équipes : SMB · Large Accounts · Espagne". Global/team filtering only on this screen. No individual selector here.
Navigation: "Synthèse" active, "Pipeline", "Parcours & démos", "Cohortes", "MRR & churn", ADD final tab "Analyse individuelle" with subtle small "À explorer" badge. It represents a future dedicated individual-versus-team analysis, subject to feasibility, not a KPI ranking on this overview.

KEEP TOP SECTION practically unchanged:
"Objectifs mensuels" / "Équipes Sales · contrôle à fin de mois"
MRR signé 18 000 € / Objectif 20 000 € /90%.
Pipeline généré 240 000 € /Objectif300 000 €/80%.
Pipeline pondéré162 000 €/Objectif180 000 €/90%.
Démos42 /Objectif50 /84% with "Compteur à confirmer".
Progress bars same as original. Caption "Montants et périmètres illustratifs, à confirmer."

REPLACE THE ENTIRE MIDDLE AREA (all previous bar/line charts, cohort chart, demo timelines and three amber placeholder strips) WITH ONE LARGE SPACIOUS WHITE PANEL:
Title "Tunnel de conversion"
A compact local filter row:
Segmented control "Nouveaux clients" active / "Upsells" inactive.
Dropdown "Mesure : Opportunités ▾".
Small visible alternate measure choices beside it: "Taux de passage · Montants · Durées". These are local visualization modes, not global filters.
Dropdown "Cohorte : juin 2026 ▾".
Subtitle "Exemple fictif • même cohorte de 100 dossiers • observation au 30 septembre".

Main visual: ONE LARGE VERTICAL FUNNEL made from SIX stacked aligned trapezoidal horizontal bands. It must dominate the middle space (no other dashboard charts in this panel). Symmetrical, beautifully aligned, blue gradually transitioning to teal at the bottom, white numeric text in each segment. Widths proportionate to the six values. Do not use current-stage stock counts for this conversion funnel: these are distinct dossiers of one cohort that reached each stage at least once.
Six stage labels aligned at the left:
"Qualification" — inside the funnel "100"
"Découverte" — "70"
"Démo" — "50"
"Proposition" — "35"
"Closing" — "25"
"Signé" — "20"
A discreet label over the numeric funnel column: "Dossiers ayant atteint l’étape".
On the right a single tidy column called "Passage à l’étape suivante" aligned to the stages:
Qualification→Découverte:70%;
Découverte→Démo:71%;
Démo→Proposition:70%;
Proposition→Closing:71%;
Closing→Signé:80%;
final stage no subsequent percentage, use em dash.
Use small connector arrows for the passage-rate column. All percentages 71% are rounded from 50/70 and25/35.
In an upper-right or lower-right compact inset WITHIN SAME PANEL, one strong callout:
"Conversion globale"
"20 %"
"20 signés / 100 dossiers"
and a smaller line "Parcours et population à confirmer".
At bottom of panel, a clear readable neutral footnote:
"Un dossier non passé peut être encore en attente ou sorti du parcours."
and a discreet orange note:
"Exemple de parcours • étapes et entrée qualifiée à valider".
Do not call differences between stages losses, do not add fake conversion thresholds, do not imply every deal must follow these steps. The upsell switch is visible but not selected; never show the same funnel as mandatory for upsells.
No pipeline total/open-stock KPIs inside the funnel panel, as they belong to a different population. Remove the old 96/480000 header.

PRESERVE THE BOTTOM MRR SECTION with all following exact content, spacing can be adjusted:
Title "MRR & churn", subtitle "Portefeuille d’abonnements · tous clients · photographie de fin de mois sans prorata".
MRR actif111 000 €, Churn MRR14 000 €.
Waterfall "Évolution du MRR actif", secondary line "Expansion effective des abonnements".
Bars labels: Début100 k€, New MRR+20 k€, Expansion+5 k€, Départs−10 k€, Baisses−4 k€, Fin111 k€. Mathematically correct levels100→120→125→115→111.
Loss breakdown: "Comprendre les pertes"; "Clients partis : 8"; "Clients avec une baisse : 12"; "Départs : 10 000 €"; "Baisses d’abonnement : 4 000 €"; "Effectifs illustratifs sans chevauchement".
Footnote "Churn MRR = départs + baisses. New MRR et expansions ne compensent pas les pertes."

Global bottom footer "Proposition de lecture • chiffres fictifs • définitions ouvertes signalées en ambre".
Make the new funnel satisfy a concise SYNTHESIS page: generous whitespace, clean labels, easy to scan, very clear main story. No dense explanatory paragraphs or developer/SQL text. Keep all text legible French. All figures are fictitious. This is a visual proposal, not an executable dashboard.
```

