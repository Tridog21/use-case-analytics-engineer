# Expression de besoin Superset

*Page du tableur de la VP Sales, rédigée par le cabinet externe.*

Ce cockpit est construit en Google Sheets / Excel. Certains besoins dépassent ce qu'un tableur peut faire proprement : cette page sert de brief pour prioriser un ticket produit. La livraison peut venir après la fin de la mission du cabinet, ce n'est pas bloquant pour le cockpit V1.

## Ce qu'on n'arrive pas à faire proprement en Excel

- **Historisation des changements de stage des opportunités** : Boond n'expose pas nativement un historique des mouvements de stage. Sans ça, impossible de calculer proprement l'ancienneté d'un deal dans son stage actuel (deals stagnants) ou de reconstituer une cohorte.
- **Cohortes de pipeline (% encore ouvert dans le temps)** : suivre, pour une cohorte d'opportunités créées sur une période donnée, combien sont encore ouvertes / gagnées / perdues à J+30, J+60, J+90.
- **Weighted pipeline dynamique** : recalcul automatique du pipeline pondéré à mesure que les deals changent de stage, avec un vrai historique (pas un simple snapshot quotidien manuel).

## Vues souhaitées

- **Vue cohortes** : opportunités groupées par mois de création, % encore ouvert / gagné / perdu à différents horizons.
- **Vue « pipe projeté »** : évolution du pipeline pondéré dans le temps, pas seulement une photo à date.

## En attendant

La structure Excel et les premiers calculs (snapshot quotidien manuel du pipeline, historisation append-only des deals) sont construits par le cabinet en attendant la solution Superset.
