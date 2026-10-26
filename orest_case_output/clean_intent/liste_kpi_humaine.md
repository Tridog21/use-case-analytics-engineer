# Liste des KPI — lecture humaine

**Précision de l’échange 16 :** l’utilisateur suggère « Administration des ventes » pour ADV et conteste son classement comme KPI. Le sigle n’est plus présenté comme une mesure. La maquette source, zone 7, emploie « ADV / MRR potentiel du pipeline » et décrit un MRR potentiel moyen par deal : cette attente distincte reste tracée, sans formule validée. Le sens exact du sigle dans le brief reste à confirmer.

Version présentée à l’échange 14, approuvée et sauvegardée à l’échange 15 ; libellé ADV corrigé à l’échange 16. Les définitions encore ouvertes restent indiquées.

**Cohorte, canal, équipe, individu et type de vente sont des axes d’analyse, pas des KPI.** Les mesures ci-dessous se déclinent selon ces axes, sans créer de doublons.

`N(...)` = nombre d’objets distincts. Les flux portent sur une période ; les stocks sur une date.

**Pipeline et conversion**

| KPI | Définition | Formule |
|---|---|---|
| **Nombre d’opportunités générées** | Dossiers créés dans Boond pendant la période, dès leur création après formulaire. | `N(opportunités dont création Boond appartient à la période)` |
| **Valeur du pipeline généré** | Valeur commerciale apportée par ces entrées. | `Σ montants des opportunités à leur entrée` |
| **Nombre d’opportunités ouvertes** | Dossiers encore en cours à la date observée, globalement ou par étape. | `N(opportunités ouvertes à la date)` |
| **Valeur du pipeline ouvert** | Valeur non pondérée des dossiers ouverts. | `Σ montants des opportunités ouvertes` |
| **Valeur du pipeline pondéré** | Valeur estimée compte tenu des chances de signature finale. | `Σ(montant de l’opportunité × probabilité de signature)` |
| **Part d’un canal dans le pipeline ouvert** | Poids du canal en nombre de dossiers ouverts. | `N(opportunités ouvertes du canal) / N(total ouvert) × 100` |
| **Couverture de l’objectif** | Valeur des affaires ouvertes prévues en clôture dans le mois, rapportée à une cible compatible. | `Σ montants ouverts à clôture prévue dans le mois / objectif correspondant` |
| **Nombre d’entrées dans une étape** | Dossiers ayant rejoint une étape pendant la période. | `N(opportunités entrées dans l’étape sur la période)` |
| **Nombre de sorties d’une étape** | Dossiers ayant quitté une étape pendant la période, quelle que soit leur destination. | `N(opportunités sorties de l’étape sur la période)` |
| **Nombre de signatures** | Dossiers entrés dans « Signé — formalités à finaliser » pendant la période, sans recompter la finalisation. | `N(opportunités signées sur la période)` |
| **Nombre d’opportunités perdues** | Dossiers ayant enregistré une issue de perte pendant la période. | `N(opportunités perdues sur la période)` |
| **Taux de conversion A → B** | Part des dossiers entrés en A ayant atteint B dans l’horizon retenu. | `N(dossiers entrés en A puis ayant atteint B) / N(dossiers éligibles entrés en A) × 100` |
| **Taux de perte après l’entrée en A** | Part de cette population ayant été perdue à l’horizon retenu. | `N(dossiers de cette population perdus à l’horizon) / N(dossiers éligibles entrés en A) × 100` |
| **Nombre de dossiers ouverts / gagnés / perdus à un horizon** | Effectif de chaque issue dans une population suivie, notamment à J+30, J+60 et J+90. | Pour chaque issue : `N(dossiers dans cette issue à l’horizon)` |
| **Proportion de dossiers ouverts / gagnés / perdus à un horizon** | Poids de chaque issue dans cette même population. | Pour chaque issue : `N(dossiers dans cette issue à l’horizon) / N(population suivie éligible) × 100` |

Le taux de perte n’est **pas** automatiquement `100 % − taux de conversion` : des dossiers peuvent rester en cours. Le passage de « signé » à « formalités finalisées » ne crée pas une seconde signature.

**Durées et stagnation**

| KPI | Définition | Formule |
|---|---|---|
| **Ancienneté dans l’étape actuelle** | Temps déjà passé par un dossier dans son passage actuel. | `Date d’observation − date d’entrée dans ce passage` |
| **Durée d’un passage terminé** | Temps passé entre l’entrée et la sortie d’une étape, notamment la phase Démo. | `Date de sortie − date d’entrée du passage` |
| **Durée du cycle commercial** | Temps entre l’entrée retenue dans le parcours et son issue. | `Date de l’issue − date d’entrée retenue` |
| **Délai entre deux étapes du sous-parcours de démo** | Temps entre deux événements reliés : demande → Démo 1, puis éventuellement complément. | `Date de l’événement suivant − date de l’événement précédent` |
| **Nombre de dossiers stagnants** | Dossiers dont l’ancienneté dépasse le seuil applicable. | `N(opportunités dont ancienneté > seuil)` |
| **Valeur des dossiers stagnants** | Valeur commerciale immobilisée dans ces dossiers. | `Σ montants des opportunités stagnantes à la date observée` |

Les seuils, les pauses et la statistique de synthèse des durées — moyenne, médiane… — restent à choisir.

**Démonstrations**

| KPI | Définition | Formule |
|---|---|---|
| **Nombre de demandes de démo** | Actions distinctes de demande enregistrées pendant la période. | `N(actions admissibles de type « demande de démo »)` |
| **Nombre de démos** | Rendez-vous de démo réellement réalisés pendant la période ; une séance comptée une fois, types de démo conservés. | `N(RDV distincts de démo tenus pendant la période)` |
| **Nb In demo** | Sociétés distinctes ayant au moins une opportunité dans l’étape Démo à la date observée ; deux dossiers d’une société comptent pour un prospect. | `N(sociétés distinctes avec au moins une opportunité en Démo à la date)` |

Les **dossiers en phase Démo** et les **entrées dans cette phase** sont les déclinaisons des compteurs par étape ci-dessus. Ils ne se confondent pas avec le nombre de séances. L’objectif démos porte sur les RDV réellement réalisés (échange 22). La preuve de tenue reste à préciser ; le grain société de « Nb In demo » est décidé à l’échange 23.

**MRR et clientèle**

| KPI | Définition | Formule |
|---|---|---|
| **MRR actif** | Valeur mensuelle des abonnements actifs à la clôture, sans prorata journalier. | `Σ montants mensuels des lignes actives en fin de mois` |
| **MRR signé** | Valeur mensuelle récurrente engagée à l’entrée en « Signé — formalités à finaliser » pendant le mois ; pour un upsell, seul le supplément vendu est retenu (150 − 100 = 50 €/mois) ; donnée source à vérifier. | `Σ MRR engagé des signatures admissibles du mois` |
| **New MRR total** | Ensemble du MRR supplémentaire actif entre clôtures, avec filtre **New / Upsell**. | `New MRR [New] + New MRR [Upsell]` |
| **New MRR — New** | MRR des sociétés entrantes à la clôture, retours après churn inclus pour le case. | `Σ MRR fin N des sociétés actives à fin N et inactives à fin N−1` |
| **New MRR — Upsell (expansion)** | Hausse nette active des sociétés présentes aux deux clôtures ; composante du New MRR total, distincte de l’engagement signé. | `Σ max(MRR client fin N − MRR client fin N−1, 0)` pour les clients restants |
| **MRR perdu par départs** | MRR de la clôture précédente des sociétés qui ne sont plus actives. | `Σ MRR client fin N−1` pour les sociétés actives à fin N−1 et inactives à fin N |
| **MRR perdu par baisses d’abonnement** | Baisse nette du MRR total des sociétés actives aux deux clôtures. | `Σ max(MRR client fin N−1 − MRR client fin N, 0)` pour les clients restants |
| **Churn MRR total** | Pertes par départs et baisses nettes par société, sans compensation entre clients. | `MRR perdu par départs + MRR perdu par baisses` |
| **Nombre de clients actifs** | Sociétés ayant au moins un abonnement en cours à la clôture. | `N(clients actifs en fin de mois)` |
| **Nombre de nouveaux clients actifs** | Clients nouvellement activés pendant le mois. | `N(nouveaux clients activés dans le mois)` |
| **Churn clients** | Sociétés actives à la clôture précédente et inactives à la clôture courante. | `N(sociétés actives à fin N−1 et inactives à fin N)` |
| **Nombre de clients ayant réduit leur abonnement** | Sociétés toujours actives dont le MRR total a baissé entre clôtures. | `N(sociétés actives aux deux clôtures avec MRR fin N < MRR fin N−1)` |

**Conventions du case — échange 22 :** calcul net par société entre fins de mois ; les retours après churn contribuent au New MRR ; les départs-retours intra-mois sont hors périmètre. Le bloc MRR actif/churn reste global, sans filtre équipe. Les montants sont calculés à partir des lignes conservées en détail. Voir la [règle commune et ses formules](intent_ia.md#mrr-client-cloture).

**Encore ouvert :** classer un retour dans New MRR ne tranche pas son inclusion dans le KPI « nouveaux clients » au sens première acquisition. On peut compter les entrants entre clôtures pour réconcilier la clientèle, sans les appeler tous nouveaux clients.

**Nomenclature résolue à l’échange 24 :** l’utilisateur inclut explicitement les upsells dans New MRR, avec filtre New / Upsell. Le supplément de 50 € reste la valeur retenue pour l’upsell 100 → 150 €/mois. MRR signé et effet actif restent distincts ; la hausse active figure une seule fois dans New MRR total. [DU-38](questions_decisions.md#du-38).

**Réconciliation :** `MRR fin = MRR début + New MRR total − Churn MRR`, à périmètre et unité identiques. New et Upsell sont des composantes filtrables du même KPI ; ne pas ajouter Upsell une deuxième fois au total.

**Comparaison aux objectifs**

| KPI | Définition | Formule |
|---|---|---|
| **Taux d’atteinte de chaque objectif** | Atteinte mensuelle, par équipe, pour chacun des quatre indicateurs : MRR signé, pipeline généré, pipeline pondéré et démos. | Pour chacun : `Réalisé compatible / objectif mensuel × 100` |
| **Écart à chaque objectif** | Surperformance ou manque, dans l’unité de l’indicateur. | Pour chacun : `Réalisé compatible − objectif mensuel` |

**Deux attentes restent sans formule validée :**

- **MRR potentiel moyen par dossier — proposition du brief** : valeur mensuelle potentielle moyenne par dossier ; population, montant et pondération à préciser.
- **Volume d’activité nécessaire pour atteindre le BP** : activité à produire pour atteindre le résultat attendu ; définition du BP et formule inverse à préciser.

Je n’ajoute pas les hypothèses encore non validées, les anciens calculs SQL ou les encaissements exclus. Pour les ratios, un dénominateur nul ou inconnu ne donne pas automatiquement `0 %`.

[Catalogue détaillé et traçabilité](catalogue_indicateurs_ia.md) · [Questions et décisions](questions_decisions.md)
