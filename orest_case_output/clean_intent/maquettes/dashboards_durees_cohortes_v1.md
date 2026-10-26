# Maquettes — Durées par étape et cohortes

**Statut : propositions de restitution, échange 29.** Deux images statiques générées avec l’outil intégré **imagegen**, skill imagegen. Leurs chiffres sont entièrement fictifs. Elles ne valident pas les hypothèses de calcul encore ouvertes et ne constituent pas des dashboards exécutables.

- [Durées par étape](dashboard_durees_etapes_v1.png)
- [Cohortes commerciales](dashboard_cohortes_v1.png)

Les images reprennent le style de la [synthèse V2](dashboard_synthese_v2.png) : fond clair, titres bleu marine, contrôles bleus, accents turquoise. La synthèse est une référence graphique ; ses anciennes annotations ne remplacent pas les décisions métier récentes.

## 1. Durées par étape : approfondir les attentes

L’utilisateur parle de durée de vie d’un lead. Le modèle proposé observe ici **l’opportunité × passage continu dans une étape**, pas le contact ni la société. L’étape Démo est l’exemple sélectionné ; la vue est conçue pour toute étape. Les séances de démonstration restent des événements distincts.

La population fictive comporte 100 passages entrés entre avril et septembre 2026, appartenant à 96 opportunités ; observation au 30 septembre. Un retour dans une étape peut expliquer plusieurs passages pour une même opportunité. Ce n’est pas un décompte de 100 prospects distincts.

| Bloc | Lecture | Support proposé |
| --- | --- | --- |
| Filtres étape, période d’entrée, observation, équipe, canal, nouvelles ventes/upsells | Sélection d’une population de passages et d’une date d’observation ; la période ne filtre pas implicitement les seules dates de sortie | `fct_stage_visit`, dimensions étape/date/type/canal/société ; attribution équipe selon convention à préciser |
| Médiane et P90 des passages terminés | Durée = sortie − entrée ; uniquement 72 passages avec entrée et sortie connues | `int_opportunity_stage_visits` → `fct_stage_visit.completed_duration` |
| Ancienneté et seuil des passages en cours | Ancienneté = observation − entrée ; 28 passages encore ouverts dans la même population d’entrée | Passages et périodes à la date observée ; ne pas appliquer le dernier état actuel à une observation passée |
| Distributions séparées | Terminés : 20/24/22/6 ; en cours : 4/6/10/8 dans les classes 0–7, 8–14, 15–30 et >30 jours | Même fait, populations distinctes ; les durées finales et anciennetés ne sont pas mélangées |
| Comparaison par canal | Médiane recalculée sur les passages terminés de chaque canal ; effectifs 18/26/16/12 = 72 | Fait de passages et `dim_channel` ; ne pas moyenner les médianes pour obtenir la médiane globale |
| Détail de dossiers | Extrait de cinq des 28 passages en cours ; navigation suggérée vers les passages successifs d’un dossier | `fct_stage_visit`, `fct_opportunity_period`, `fct_opportunity_event` et identités société/opportunité |

**Propositions, pas règles adoptées :** jours calendaires ; médiane et P90 ; seuil d’alerte >21 jours ; classes d’ancienneté ; sélection des passages par leur entrée. Le P90 est affiché comme « 90 % des passages terminés en 29 j ou moins ». La méthode exacte du quantile reste à spécifier si ce choix de restitution est retenu.

Le titre « Au-delà du seuil » porte sur 12 des 28 passages en cours. Le seuil ne s’applique pas rétrospectivement comme définition des passages terminés. Les comparaisons par équipe ne doivent pas attribuer silencieusement toute une durée à un seul responsable lorsqu’il y a transfert : `bridge_visit_responsibility` fournit une base possible, règle encore ouverte.

**Qualité :** la maquette suppose 100 débuts de passage connus sur 100. En réel, garder visibles les débuts inconnus et la couverture ; absence de début observé ne donne pas une durée nulle. Les pauses, le nurturing, les retours, la définition d’une sortie et le calendrier restent en [QC-03](../questions_decisions.md#qc-03) et [QC-10](../questions_decisions.md#qc-10). La somme des passages ne doit pas être assimilée au nombre de sociétés.

## 2. Cohortes : devenir des opportunités créées

Reprise directe de l’[expression de besoin](../../../docs/besoin/expression-de-besoin.md) : opportunités groupées par **mois de création**, pourcentages encore ouverts/gagnés/perdus à **J+30, J+60 et J+90**. L’entrée du pipeline à la création Boond est déjà décidée. La durée jusqu’à J reste une convention d’horizon à préciser : la maquette propose J depuis la date de création individuelle.

La matrice comporte six cohortes, avril à septembre 2026 ; observation au 30 septembre 2026. Chaque cellule mature présente le même ordre de lecture **Ouvert / Gagné / Perdu**. Les pourcentages fictifs reposent sur des statuts entièrement connus et classés pour les dossiers matures.

| Cohorte | Taille | J+30 : O/G/P | J+60 : O/G/P | J+90 : O/G/P |
| --- | ---: | --- | --- | --- |
| Avril 2026 | 100 | 65 / 15 / 20 % | 35 / 35 / 30 % | 20 / 45 / 35 % |
| Mai 2026 | 120 | 70 / 10 / 20 % | 45 / 25 / 30 % | 25 / 40 / 35 % |
| Juin 2026 | 100 | 70 / 15 / 15 % | 45 / 30 / 25 % | 25 / 40 / 35 % |
| Juillet 2026 | 140 | 75 / 10 / 15 % | 50 / 25 / 25 % | Non mature |
| Août 2026 | 120 | 80 / 5 / 15 % | Non mature | Non mature |
| Septembre 2026 | 160 | Non mature | Non mature | Non mature |

**Proposition de maturité pour cette maquette :** n’afficher un horizon que lorsque toute la cohorte l’a atteint. Les cellules grisées ne sont ni des zéros ni des opportunités perdues. Une autre présentation des cohortes partiellement matures reste possible ; ne pas adopter ce choix sans décision.

**Zoom juin à J+60 :** base de 100 opportunités, 45 ouvertes, 30 gagnées, 25 perdues. Le détail par canal utilise des effectifs, pas des pourcentages :

| Canal | Dossiers | Ouverts | Gagnés | Perdus |
| --- | ---: | ---: | ---: | ---: |
| Paid Search | 40 | 14 | 20 | 6 |
| Organique | 30 | 16 | 9 | 5 |
| Outbound | 30 | 15 | 1 | 14 |
| Total | 100 | 45 | 30 | 25 |

**Calcul illustré :** pour une issue, nombre d’opportunités dans cette issue à l’horizon / nombre d’opportunités de la cohorte de référence × 100. La maquette utilise une population totalement observable et classée ; en réel, préciser le traitement des autres états, inconnus, suppressions, réouvertures et dossiers non observables. Ne pas renormaliser silencieusement les trois catégories à 100 % en supprimant les inconnus. Abandonné, non qualifié et nurturing ne sont pas classés implicitement comme perdu.

| Bloc | Support proposé |
| --- | --- |
| Cohorte et horizons | `int_opportunity_followup` → `fct_opportunity_followup` : `cohort_month`, `anchor_at`, `horizon_days`, `observation_at` |
| Maturité et observabilité | `is_mature`, `is_observable`, `is_eligible` ; garder les inconnus séparés d’un échec |
| Ouvert/gagné/perdu | Contributions et `issue_at_horizon` ; une observation admissible par opportunité/cohorte/horizon |
| Zoom et filtres | `dim_followup_definition`, dates, type commercial, équipe et canal ; attribution historique à préciser |
| Investigation du parcours | Faits d’événements, périodes et passages ; ne pas déduire le passé du statut courant seul |

Filtres Nouvelles ventes/Upsells : **type commercial du dossier**, distinct du filtre financier New/Upsell de New MRR. Les conventions d’équipe et de canal doivent conserver les populations comparables ; le dessin n’impose pas un nouveau mode d’attribution.

Questions restantes : [QC-10](../questions_decisions.md#qc-10) (ancrage, maturité, couverture), [QM-01](../questions_decisions.md#qm-01) (issues), [QM-02](../questions_decisions.md#qm-02) et [QC-05](../questions_decisions.md#qc-05) (axes). La signature à « Signé — formalités à finaliser » reste la décision de référence ; le passage aux formalités finalisées ne crée pas une seconde victoire.

## 3. Traçabilité et vérification

Sources lues : expression de besoin ; catalogue IA B01/B02/U03 ; registre QC-03/QC-10 ; proposition `fct_stage_visit` et `fct_opportunity_followup`. Référence graphique inspectée visuellement : synthèse V2.

Les deux images ont été inspectées après génération : présence des deux populations de durée, concordance des chiffres des tableaux, couleurs d’issues constantes, horizons non matures gris et données fictives signalées. Les sommes des distributions et du tableau de canal sont cohérentes. Aucun calcul sur les données réelles, aucun service ou modèle modifié.

Les sélecteurs et liens dessinés indiquent les interactions souhaitées ; les PNG ne sont pas interactives. Leurs charts sont des rendus de maquette ; les valeurs chiffrées et la présente note font foi pour la proposition.

## 4. Prompts de génération

Mode : outil intégré `image_gen.imagegen`, deux générations indépendantes ; aucune API CLI. Images originales conservées dans le répertoire de génération ; copies projet disponibles ci-dessus.

### Durées par étape

```text
Use case: ui-mockup.
Create ONE polished STATIC desktop business dashboard mockup in FRENCH, large landscape 4:3 canvas, ideally 2400x1800, excellent crisp readable typography. This is one page of the existing BOOND / ANALYTICS commercial cockpit. White / very pale blue background, navy titles, royal blue controls, teal data accents, orange for illustrative alerts, fine pale blue borders, softly rounded cards, generous whitespace. Professional analytics SaaS, restrained, no device frame, no perspective, no decorative illustration. All data is fictional. Make every text readable; do not cram small text.

Top left small "BOOND / ANALYTICS", main title "Durées par étape", subtitle "Comprendre les attentes et repérer les dossiers qui stagnent."
Top right orange outlined badge "MAQUETTE • DONNÉES FICTIVES".
Compact navigation "Synthèse   Pipeline   Durées par étape   Cohortes   MRR & churn", Durées par étape highlighted in blue.

Filters in one/two neat rows: "Étape : Démo ▾", "Entrées : avril–sept. 2026 ▾", "Observation : 30 sept. 2026", "Équipe : Toutes ▾", "Canal : Tous ▾", segmented "Nouvelles ventes" selected / "Upsells".
Population strip: "100 passages • 96 opportunités • 72 terminés • 28 en cours".
Important scope line: "Même population : passages entrés dans l’étape sur la période sélectionnée."

Four equal KPI cards:
1 "Durée médiane" value "12 j" sublabel "72 passages terminés".
2 "90 % des passages terminés en" value "29 j ou moins" sublabel "Statistique proposée".
3 "Ancienneté médiane" value "18 j" sublabel "28 passages en cours".
4 "Au-delà du seuil illustratif" value "12 / 28" sublabel "En cours depuis plus de 21 j", small orange "Seuil à valider".

Middle row two equal generous panels. Left titled "Durées des passages terminés", subtitle "72 passages • entrée → sortie". A clean vertical bar histogram with x labels "0–7 j", "8–14 j", "15–30 j", "> 30 j", exact heights/count labels 20,24,22,6, y label "Passages". Teal bars. Right titled "Ancienneté des passages en cours", subtitle "28 passages • entrée → date d’observation". Bar histogram same duration bins, exact counts 4,6,10,8, royal blue bars with last orange. y label "Passages". Small clear line between these panels and next row: "Une ancienneté en cours n’est pas une durée finale."

Lower row: left third panel "Comparer les canaux", subtitle "Durée médiane • passages terminés". Four horizontal bars and count labels:
"Paid Search" / "10 j" / "18 passages"
"Organique" / "12 j" / "26 passages"
"Outbound" / "16 j" / "16 passages"
"Direct" / "9 j" / "12 passages".
Use navy/teal bars with proportional length.
Right two-thirds panel "Explorer les dossiers", selected pill "En cours", table headers "Dossier", "Société", "Entrée Démo", "Ancienneté".
Rows:
"OPP-1042" "Alpine" "25 août" "36 j"
"OPP-1068" "Boréal" "28 août" "33 j"
"OPP-1091" "Cirrus" "1 sept." "29 j"
"OPP-1124" "Delta" "8 sept." "22 j"
"OPP-1160" "Éole" "15 sept." "15 j"
First row lightly selected blue; first four age pills orange, last neutral. Bottom clickable-looking text "Voir les passages successifs du dossier →", supporting label "Extrait de 5 dossiers sur 28".
Small bottom definition band, readable, not dense: "Grain : opportunité × passage continu dans une étape."
Footer orange small note: "Propositions à valider : jours calendaires, médiane/P90, pauses, retours et seuils."
Additional coverage text: "Exemple : débuts de passage connus pour 100 / 100."
Do not show SQL, model names, implementation details, unvalidated individual rankings, revenue figures, or a cohort conversion funnel. Do not confuse demo meetings with the commercial demo stage. Accurate labels and values required. Design must feel like the clean BOOND white/navy/blue/teal dashboard previously described, no scribbles or annotations.
```

### Cohortes commerciales

```text
Use case: ui-mockup.
Create ONE polished STATIC desktop business dashboard mockup in FRENCH, large landscape 4:3 canvas ideally 2400x1800, readable crisp typography. Matching BOOND / ANALYTICS cockpit: white and very pale blue background, navy titles, royal blue controls, teal for won, coral for lost, faint borders, rounded cards, generous spacing. This image is a companion to "Durées par étape", same professional SaaS style. No device frame/perspective. All data fictional.

Top left small "BOOND / ANALYTICS", large title "Cohortes commerciales", subtitle "Que deviennent les opportunités après leur création ?".
Top right orange outlined badge "MAQUETTE • DONNÉES FICTIVES".
Nav "Synthèse   Pipeline   Durées par étape   Cohortes   MRR & churn", Cohortes selected.
Filters: "Créations : avril–sept. 2026 ▾", "Observation : 30 sept. 2026", "Équipe : Toutes ▾", "Canal : Tous ▾", type toggle "Nouvelles ventes" selected / "Upsells".
Definition strip "Une cohorte = les opportunités créées dans Boond pendant le même mois."
Focus control "Zoom : juin 2026 ▾" and "Horizon : J+60 ▾".
Four aligned summary cards for selected cohort at J+60:
"Cohorte sélectionnée" / "100 opportunités" / "Créations de juin 2026"
"Encore ouvertes" / "45 %" / "45 dossiers" in blue
"Gagnées" / "30 %" / "30 dossiers" in teal
"Perdues" / "25 %" / "25 dossiers" in coral.

Main very generous wide panel titled "Comparer les cohortes à maturité égale".
Legend at top: blue dot "Ouvert" teal "Gagné" coral "Perdu". Prominent instruction "Dans chaque cellule : Ouvert / Gagné / Perdu".
Table columns "Mois de création", "Taille", "J+30", "J+60", "J+90".
Each horizon cell shows a tiny proportional 100% stacked horizontal strip plus large clearly legible three colored percentage labels beneath, always same order open / won / lost. Six rows EXACT:
"Avril 2026", "100", J30 "65 % / 15 % / 20 %", J60 "35 % / 35 % / 30 %", J90 "20 % / 45 % / 35 %".
"Mai 2026", "120", J30 "70 % / 10 % / 20 %", J60 "45 % / 25 % / 30 %", J90 "25 % / 40 % / 35 %".
"Juin 2026", "100", J30 "70 % / 15 % / 15 %", J60 "45 % / 30 % / 25 %", J90 "25 % / 40 % / 35 %".
"Juillet 2026", "140", J30 "75 % / 10 % / 15 %", J60 "50 % / 25 % / 25 %", J90 gray hatched "Non mature".
"Août 2026", "120", J30 "80 % / 5 % / 15 %", J60 gray hatched "Non mature", J90 gray hatched "Non mature".
"Septembre 2026", "160", all three horizon cells gray hatched "Non mature".
Highlight the June row with pale blue and outline its J+60 cell. All labels fit cleanly; avoid tiny printing. Grey cells must NOT be 0%.
Under table line "Non mature : l’horizon n’est pas encore atteint par toute la cohorte."

Lower row two panels. Left 55% titled "Devenir de la cohorte de juin" and subtitle "Même base de 100 opportunités". Three large horizontal 100% stacked bars:
"J+30": blue70%, teal15%, coral15%.
"J+60": blue45%, teal30%, coral25%.
"J+90": blue25%, teal40%, coral35%.
Label percentages clearly inside bar segments with contrast. Same fixed color semantics.
Right45% titled "Zoom par canal à J+60", subtitle "Cohorte de juin • mêmes 100 dossiers". Table headers "Canal", "Dossiers", "Ouverts", "Gagnés", "Perdus". Here values are COUNTS not percentages:
"Paid Search" 40 14 20 6
"Organique" 30 16 9 5
"Outbound" 30 15 1 14
"Total" 100 45 30 25
Table caption "Effectifs — appliquer les filtres conserve le même périmètre."

Footer readable two lines:
"Exemple : 100 % des dossiers matures ont un statut connu. Autres états / non observables à traiter séparément."
"Propositions à valider : J depuis chaque création ; affichage après maturité complète ; classement des issues."
Do not invent facts from missing history or label abandoned/nonqualified as lost. Do not show model names or SQL. Do not use revenue or company counts: unit is opportunities. This is a visual suggestion, not an operational dashboard. Clean analytical layout, impeccable French typography.
```

