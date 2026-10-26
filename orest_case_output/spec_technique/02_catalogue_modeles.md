# Catalogue des modèles — version 0.2

Spécification finalisée v0.2 du25octobre2026 ; aucun modèle SQL/YAML créé. Les décisions D16–D30 du document01§7 sont normatives et ferment les arbitrages de la version précédente. Voir [architecture et décisions](01_specification_technique.md) et [exécution/tests](03_execution_tests.md). Les 73 fiches ci-dessous distinguent champs certains, candidats et sorties non calculables. Les colonnes héritées sont des listes finies : elles ne permettent jamais un SELECT étoile.

## A. Contrats communs

### A.0 Contrat de finalisation v0.2 — décisions obligatoires

Lire01§7 avant de coder : les arbitrages D16–D30 y sont fermés sous délégation. Les descriptions ci-dessous appliquent ce contrat ; les raisons génériques missing_* restent des contrôles de donnée/configuration invalide, pas des questions métier laissées à résoudre. Tous les73 modèles restent à implémenter avec leur schéma, y compris les familles sans preuve dont les mesures sont NULL et dont dataset_publication_status explique l’indisponibilité.

La couverture jusqu’à2026-09-30T22:00Z et EUR sont des hypothèses de case, jamais des constats de complétude/devise prouvés. Les lacunes antérieures à la première trace, les194 créations incohérentes et les dates de signature non observées restent inconnues. Le barème ref est appliqué au passé PAR RECALCUL D21, sans falsifier sa date de capture. Les montants CRM gardent leur nature non confirmée, les RDV passés ne prouvent pas tenue.



### A.1 Implantation et conventions

Chaque modèle <nom> correspond au fichier SQL <nom>.sql et à son entrée dans _models.yml du dossier indiqué. Les sources ont _sources.yml. Chemins de projet complets relatifs à la racine connue dans 01 ; aucune implémentation n'est ajoutée par ce catalogue. Toutes descriptions YAML doivent reprendre finalité, grain, histoire, rafraîchissement manuel/non planifié et description de chaque colonne de cette fiche.

Sources : source('boond',table) pour raw ; source('hubspot',table) ; source('case_reference',table) pour ref. Bases sources inchangées. Relations modèles via ref(nom), jamais base physique codée en dur ; this pour cible incrémentale. SQL explicite une SELECT avec CTE/Jinja ; dbt gère DDL. Les jointures incluent tenant quand disponible, model_run_id pour dérivés et la borne temporelle pertinente ; LEFT JOIN et join_use_nulls=1 préservent les inconnus.

### A.1 bis Tags et sélections dbt normatifs

Les tags des modèles ET des tests associés doivent rendre les commandes03 exactes : les 15 staging portent capture ; les 11 dimensions et les 2 int de dwh_common portent common ; les 8 int de dwh_pipeline portent pipeline ; les 6 int de dwh_revenue portent revenue ; les 9 faits portent mart (et leur module pipeline/revenue si utile) ; les 10 DTR portent dtr ; les 11 datasets portent dataset. int_publication porte uniquement publication, jamais common. Les nombres de cette partition sont ceux de l'index ; int_signature_probabilities est dwh_pipeline. La sélection union pipeline/revenue/mart laisse dbt ordonner les faits Pipeline avant int_sales_objectives_month qui les consomme. Les tests singuliers transversaux portent les tags de leur phase et filtrent test_model_run_id.

### A.2 Colonnes techniques communes de staging (ST)

Cette liste ST est ajoutée aux colonnes source de CHAQUE staging ; elle n'est pas une extraction d'un champ CRM.

| Colonne | Type / NULL | Définition |
|---|---|---|
| source_identity_key | String / non | SHA256 hex minuscule d'une sérialisation typée ordonnée du domaine logique source qualifié (boond.opportunities,hubspot.contacts,case_reference.sales_targets,etc.) puis de l'identité source décrite par fiche ; aucun identifiant source n'est remplacé. |
| source_payload_hash | String / non | SHA256 du tuple de toutes colonnes physiques source dans l'ordre de la fiche, type compris ; distingue NULL/chaîne vide/zéro. |
| source_version_key | String / non | CDC : hash(identité,src_published_at,payload_hash). Capture : hash(identité,capture_key,payload_hash,is_source_present). |
| imported_at | DateTime64(3,'UTC') / non | Instant d'import de la version, figé au début de tentative ; distinct de publication et métier. |
| capture_key | String / non | Identifiant de capture/tentative conservé dans manifest ; CDC : provenance du premier import de cette version. |
| capture_at | DateTime64(3,'UTC') / non | Instant de capture source figé, distinct de source updatedAt. |
| is_source_present | Bool / non | true pour une version effectivement lue, y compris une suppression CDC ; false pour une absence détectée par capture complète nonCDC seulement. |

ST n'introduit ni qualification ni filtre métier. Une absence technique nonCDC conserve les dernières colonnes source connues mais is_source_present=false ; l'identité ne disparaît pas de l'histoire. Les dates sources restent fidèles aux instants UTC ; conserver Float64 des montants, JSON physiques et colonnes toujours NULL.

### A.3 Contrat dérivé (R), clés et matérialisations

R est la liste finie : model_run_id String,record_key String,record_version_key String,row_hash String,calculated_at DateTime64(3,'UTC'),rule_version String,input_cutoff_at DateTime64(3,'UTC'), tous non NULL. Clé physique=(model_run_id,record_key), version=hash de ce tuple. row_hash exclut R et porte le contenu métier ordonné typé. Les clés de dimensions stables incluent identité/validité source ; le run complète chaque jointure, sans modifier l'identité métier. La clé record_key de chaque fiche reprend exactement son grain décrit.

Tables dim/int/DTR : incremental append, MergeTree, full_refresh=false,on_schema_change=fail,unique_key='record_version_key',inserts_only non activé ; SELECT complet des résultats du run candidat, puis anti-jointure run+record_key sous is_incremental(). Pas de filtre max date sur les résultats dérivés. ORDER BY au minimum(model_run_id,record_key), enrichi de clés d'usage selon fiche sans confondre tri et unicité. Jamais de suppression/replacement des anciens runs. Même empreinte d'entrées/code/params=>même run ; rerun sans doublon. Cadence manuelle à la demande, aucune fréquence quotidienne décidée. Faits/datasets sont vues explicites sur ces histoires : pas de copie ni d'incrémental imposé à toutes les couches.

Un nouveau run contient TOUS les résultats logiques, y compris inconnus ; un échec partiel ne constitue pas un snapshot complet. Publication unique contrôlée après tests ; int_publication n'est un parent d'aucune préparation métier. Pour construction candidat, filtres model_run_id var ; pour datasets courants, run lu au pointeur publié. Captures nonCDC admises via source_capture_keys et cutoff, jamais simple hash de contenu qui perdrait A→B→A.

### A.4 Mesures, qualité et domaines

Montants canoniques Nullable(Decimal(38,4)), conversion depuis Float par chaîne dans intermédiaire, pas staging. Une contribution inconnue n'est pas remplacée par0. Taux Nullable(Float64), numérateur/dénominateur et statut conservés. Temps UTC ms, clôtures Paris, jours écoulés exacts pour durées ; horizons calendaires Paris. Colonnes de période [valid_from_at,valid_to_at) uniquement si modèle d'intervalle. Fin de contrat date inclusive=>borne exclusive du lendemain ;2099 conservé.

Statuts génériques et raisons sont définis dans 01§4.3. Chaque mesure peut avoir son statut propre. Sous source_currency non confirmée, ne pas afficher EUR ni agréger un total financier certifié. Démos réalisées NULL sans preuve ; montant opportunité conservé comme candidat sans mensualité certifiée. Les sources HubSpot/ref sans tenant sont attribuées au périmètre source_tenant_id='demo_crm' déclaré pour ce case mono-tenant, dans int/dim seulement. Ce paramètre n'est pas une nouvelle colonne source du staging.

### A.4 bis Date observée CDC admise par D15

Politique de calcul case_rules.event_time_policy=observed_cdc_allowed. Les changements d'état effectivement constatés entre versions peuvent utiliser meta.ts comme date observée dans entered_at/exited_at/event_at et les calculs dérivés. Le champ de provenance reste cdc_transition_proxy ; is_event_time_accepted=true quand la transition est démontrée et la date connue. Une mise à jour sans changement d'étape n'est pas une nouvelle entrée. La date métier de création reste creationDate. Les premières observations avancées et les lacunes restent inconnues ; aucune signature datée n'est inventée pour les17 dossiers14 sans1.

L'admission de ce proxy ne ferme pas les questions de réouvertures, populations, couverture et montants. Elle retire seulement le blocage «proxy CDC non accepté» des contributions concernées. Les datasets de durée/conversion/signature conservent les libellés et indicateurs de qualité de date ; afficher «temps observé» quand la provenance l'exige.

### A.5 Contrôles minimaux attachés à chaque fiche

Not_null sur clés physiques et métadonnées requises ; unicité à la version complète, domaines des statuts et types ; relationships au run+versionkey quand connu ; cardinalité de chaque jointure ; nb_keys et digest comparés à la recomposition attendue. Périodes non inversées/non chevauchantes par unité quand exigé. Échec bloquant avant publication pour doublon/conflit/fan-out/montant incohérent ; historique ou règle absente donne indisponibilité traçable, pas suppression silencieuse de population. Scénarios et gravités détaillés dans 03. Aucun test dbt de ce catalogue n'a été exécuté.


### A.6 Index exhaustif des 73 fiches et relations futures

Les chemins SQL/YAML et les colonnes sont détaillés dans chaque fiche. Les sources brutes, vues de faits, registres de résultats et contrôles techniques ne sont pas confondus.

| Modèle / fiche | Base ClickHouse | Nature |
|---|---|---|
| [stg_boond_opportunities](#stg_boond_opportunities) | `stg_boond` | capture source |
| [stg_boond_actions](#stg_boond_actions) | `stg_boond` | capture source |
| [stg_boond_companies](#stg_boond_companies) | `stg_boond` | capture source |
| [stg_boond_contacts](#stg_boond_contacts) | `stg_boond` | capture source |
| [stg_boond_resources](#stg_boond_resources) | `stg_boond` | capture source |
| [stg_boond_businessunits](#stg_boond_businessunits) | `stg_boond` | capture source |
| [stg_boond_agencies](#stg_boond_agencies) | `stg_boond` | capture source |
| [stg_boond_poles](#stg_boond_poles) | `stg_boond` | capture source |
| [stg_boond_dictionaries](#stg_boond_dictionaries) | `stg_boond` | capture source |
| [stg_boond_projects](#stg_boond_projects) | `stg_boond` | capture source |
| [stg_boond_deliveries](#stg_boond_deliveries) | `stg_boond` | capture source |
| [stg_hubspot_contacts](#stg_hubspot_contacts) | `stg_hubspot` | capture source |
| [stg_hubspot_deals](#stg_hubspot_deals) | `stg_hubspot` | capture source |
| [stg_ref_sales_targets](#stg_ref_sales_targets) | `stg_reference` | capture source |
| [stg_ref_stage_probabilities](#stg_ref_stage_probabilities) | `stg_reference` | capture source |
| [dim_date](#dim_date) | `dtm_common` | dimension historisée par run |
| [dim_country](#dim_country) | `dtm_common` | dimension historisée par run |
| [dim_company](#dim_company) | `dtm_common` | dimension historisée par run |
| [dim_employee](#dim_employee) | `dtm_common` | dimension historisée par run |
| [dim_team](#dim_team) | `dtm_common` | dimension historisée par run |
| [dim_stage](#dim_stage) | `dtm_common` | dimension historisée par run |
| [dim_sale_type](#dim_sale_type) | `dtm_common` | dimension historisée par run |
| [dim_channel](#dim_channel) | `dtm_common` | dimension historisée par run |
| [dim_action_type](#dim_action_type) | `dtm_common` | dimension historisée par run |
| [dim_followup_definition](#dim_followup_definition) | `dtm_common` | dimension historisée par run |
| [dim_metric](#dim_metric) | `dtm_common` | dimension historisée par run |
| [int_crm_identity_links](#int_crm_identity_links) | `dwh_common` | préparation historique par run |
| [int_team_membership_periods](#int_team_membership_periods) | `dwh_common` | préparation historique par run |
| [int_signature_probabilities](#int_signature_probabilities) | `dwh_pipeline` | préparation historique par run |
| [int_opportunity_stage_visits](#int_opportunity_stage_visits) | `dwh_pipeline` | préparation historique par run |
| [int_opportunity_periods](#int_opportunity_periods) | `dwh_pipeline` | préparation historique par run |
| [int_opportunity_events](#int_opportunity_events) | `dwh_pipeline` | préparation historique par run |
| [int_opportunity_followup](#int_opportunity_followup) | `dwh_pipeline` | préparation historique par run |
| [int_actions_prepared](#int_actions_prepared) | `dwh_pipeline` | préparation historique par run |
| [int_demo_intervals](#int_demo_intervals) | `dwh_pipeline` | préparation historique par run |
| [int_visit_responsibility](#int_visit_responsibility) | `dwh_pipeline` | préparation historique par run |
| [int_subscription_periods](#int_subscription_periods) | `dwh_revenue` | préparation historique par run |
| [int_subscription_changes](#int_subscription_changes) | `dwh_revenue` | préparation historique par run |
| [int_subscription_month_end](#int_subscription_month_end) | `dwh_revenue` | préparation historique par run |
| [int_client_activity_context](#int_client_activity_context) | `dwh_revenue` | préparation historique par run |
| [int_mrr_movements](#int_mrr_movements) | `dwh_revenue` | préparation historique par run |
| [int_sales_objectives_month](#int_sales_objectives_month) | `dwh_revenue` | préparation historique par run |
| [fct_opportunity_period](#fct_opportunity_period) | `dtm_pipeline` | fait en vue |
| [fct_stage_visit](#fct_stage_visit) | `dtm_pipeline` | fait en vue |
| [fct_opportunity_event](#fct_opportunity_event) | `dtm_pipeline` | fait en vue |
| [fct_opportunity_followup](#fct_opportunity_followup) | `dtm_pipeline` | fait en vue |
| [fct_action](#fct_action) | `dtm_pipeline` | fait en vue |
| [fct_demo_interval](#fct_demo_interval) | `dtm_pipeline` | fait en vue |
| [fct_mrr_movement](#fct_mrr_movement) | `dtm_revenue` | fait en vue |
| [fct_subscription_month_end](#fct_subscription_month_end) | `dtm_revenue` | fait en vue |
| [fct_sales_objectives_month](#fct_sales_objectives_month) | `dtm_revenue` | fait en vue |
| [dtr_sales_objectives_month](#dtr_sales_objectives_month) | `dtr_sales` | DTR historique par run |
| [dataset_sales_objectives_month](#dataset_sales_objectives_month) | `dtr_sales` | dataset publié |
| [dtr_funnel_progress](#dtr_funnel_progress) | `dtr_sales` | DTR historique par run |
| [dataset_funnel_progress](#dataset_funnel_progress) | `dtr_sales` | dataset publié |
| [dtr_company_mrr_month](#dtr_company_mrr_month) | `dtr_sales` | DTR historique par run |
| [dataset_company_mrr_month](#dataset_company_mrr_month) | `dtr_sales` | dataset publié |
| [dtr_stage_visits](#dtr_stage_visits) | `dtr_sales` | DTR historique par run |
| [dataset_stage_visits](#dataset_stage_visits) | `dtr_sales` | dataset publié |
| [dtr_cohort_outcomes](#dtr_cohort_outcomes) | `dtr_sales` | DTR historique par run |
| [dataset_cohort_outcomes](#dataset_cohort_outcomes) | `dtr_sales` | dataset publié |
| [dtr_opportunity_timeline](#dtr_opportunity_timeline) | `dtr_sales` | DTR historique par run |
| [dataset_opportunity_timeline](#dataset_opportunity_timeline) | `dtr_sales` | dataset publié |
| [dtr_pipeline_periods](#dtr_pipeline_periods) | `dtr_sales` | DTR historique par run |
| [dataset_pipeline_periods](#dataset_pipeline_periods) | `dtr_sales` | dataset publié |
| [dtr_sales_events](#dtr_sales_events) | `dtr_sales` | DTR historique par run |
| [dataset_sales_events](#dataset_sales_events) | `dtr_sales` | dataset publié |
| [dtr_sales_actions](#dtr_sales_actions) | `dtr_sales` | DTR historique par run |
| [dataset_sales_actions](#dataset_sales_actions) | `dtr_sales` | dataset publié |
| [dtr_demo_intervals](#dtr_demo_intervals) | `dtr_sales` | DTR historique par run |
| [dataset_demo_intervals](#dataset_demo_intervals) | `dtr_sales` | dataset publié |
| [int_publication](#int_publication) | `dwh_common` | pointeur technique |
| [dataset_publication_status](#dataset_publication_status) | `dtr_sales` | vue technique de disponibilité |

## B. Quinze staging — 179 colonnes source exhaustives

<a id="stg_boond_opportunities"></a>

### stg_boond_opportunities

- **Couche/finalité** : staging technique, Besoins commerciaux (opportunités) : un besoin suit un prospect de la première demande jusqu'à la signature ou la perte. C'est l'objet que les commerciaux font avancer d'étape en étape. Reprise de toutes les 25 colonnes, sans sélection métier.
- **Objet futur** : `dbt/models/staging/boond/stg_boond_opportunities.sql`, YAML `_models.yml` du même dossier ; relation `stg_boond.stg_boond_opportunities` ; source `{{ source('boond', 'opportunities') }}` déclarée dans `_sources.yml`.
- **Grain** : une version CDC par identité/publication/contenu. Identité source : `meta.customer`, `id` ; source_version_key unique, ST non NULL. Grain historique distinct du dernier état.
- **Historique/calcul** : lire toutes versions et suppressions ; normaliser seulement noms/types de présentation. Premier chargement/cible vide complet. Reprise src_published_at >= borne typée calculée une seule fois depuis maxOrNull cible, recouvrement48 h paramétrable ; replay de la borne tentée ou full scan anti-jointure. Préserver collisions de contenu dans source_version_key, bloquer la lecture métier sur conflit identité+publication.
- **Physique** : incremental append/MergeTree, ORDER BY(src_tenant_id, src_id, src_published_at, source_version_key), sans partitionnement/TTL en v0.1 ; anti-jointure source_version_key sous is_incremental(), full_refresh=false,on_schema_change=fail,unique_key='source_version_key',inserts_only non activé. Le volume observé ne justifie pas de partitionnement supplémentaire sans mesure.
- **Rafraîchissement** : manuel ; complétude du lot vérifiée, aucun SLA automatique pour ce case D29. Source() seule en amont, lecture this pour anti-jointure ; aucune jointure métier.
- **Tests** : contrat ST, colonnes source exhaustives, source_version_key unique, clé candidate CDC sans conflit (ou identité unique par capture nonCDC), suppression conservée, relecture sans doublons, reprise/cible vide/arrivée hors fenêtre ; erreurs bloquent capture/publication.

| Colonne physique source | Colonne staging | Type final | NULL permis | Description / provenance / contraintes |
|---|---|---|---|---|
| `meta.customer` | `src_tenant_id` | `String` | non | Code du client Boond (tenant) dont vient la ligne. Un seul tenant dans ce jeu. |
| `id` | `src_id` | `Int64` | non | Identifiant de l'enregistrement dans Boond. Le même `id` revient à chaque version. |
| `meta.deleted` | `src_is_deleted` | `Bool` | non | Vrai sur la version qui enregistre la suppression de l'enregistrement dans Boond. |
| `meta.ts` | `src_published_at` | `DateTime64(3,'UTC')` | non | Horodatage de la version : moment où la modification a été publiée par le flux CDC. |
| `state` | `src_state_id` | `Nullable(Int64)` | oui | Étape du besoin. Libellés et propriétés de chaque code dans le référentiel des étapes. Référence documentaire : raw.dictionaries.setting.state.opportunity ; intégrité temporelle à contrôler hors staging. |
| `typeOf` | `src_type_id` | `Nullable(Int64)` | oui | Type de besoin : nouveau client, upsell, formation… Référence documentaire : raw.dictionaries.setting.typeOf.project ; intégrité temporelle à contrôler hors staging. |
| `title` | `src_title` | `String` | non | Intitulé libre du besoin. |
| `reference` | `src_reference` | `String` | non | Référence lisible générée par Boond à la création. |
| `creationDate` | `src_created_at` | `Nullable(DateTime64(3,'UTC'))` | oui | Date de création du besoin dans Boond. |
| `updateDate` | `src_updated_at` | `Nullable(DateTime64(3,'UTC'))` | oui | Date de la dernière modification de la fiche. |
| `startDate` | `src_started_at` | `Nullable(DateTime64(3,'UTC'))` | oui | Date de démarrage souhaitée par le prospect. |
| `answerDate` | `src_answer_due_at` | `Nullable(DateTime64(3,'UTC'))` | oui | Date limite de réponse au prospect. |
| `closingDate` | `src_closing_at` | `Nullable(DateTime64(3,'UTC'))` | oui | Date de closing saisie par le commercial sur la fiche. |
| `turnoverEstimatedExcludingTax` | `src_estimated_amount_excluding_tax` | `Nullable(Float64)` | oui | Montant estimé du besoin, hors taxes, saisi par le commercial. |
| `weighting` | `src_weighting_percent` | `Nullable(Int64)` | oui | Pondération du besoin en pourcentage. |
| `turnoverWeightedExcludingTax` | `src_weighted_amount_excluding_tax` | `Nullable(Float64)` | oui | Montant pondéré : montant estimé × pondération. |
| `exchangeRate` | `src_exchange_rate` | `Nullable(Float64)` | oui | Taux de change entre la devise du besoin et celle de l'agence. |
| `origin.typeOf` | `src_origin_type_id` | `Nullable(Int64)` | oui | Origine du besoin (canal par lequel il est arrivé). Référence documentaire : raw.dictionaries.setting.origin ; intégrité temporelle à contrôler hors staging. |
| `origin.detail` | `src_origin_detail` | `String` | non | Précision libre sur l'origine. |
| `relationships.mainManager.data.id` | `src_main_manager_id` | `Nullable(Int64)` | oui | Responsable de l'enregistrement : le collaborateur qui le porte. Référence documentaire : raw.ressources.id ; intégrité temporelle à contrôler hors staging. |
| `relationships.createdBy.data.id` | `src_created_by_id` | `Nullable(Int64)` | oui | Collaborateur (ou robot) qui a créé l'enregistrement. Référence documentaire : raw.ressources.id ; intégrité temporelle à contrôler hors staging. |
| `relationships.company.data.id` | `src_company_id` | `Nullable(Int64)` | oui | Société prospect ou cliente du besoin. Référence documentaire : raw.companies.id ; intégrité temporelle à contrôler hors staging. |
| `relationships.contact.data.id` | `src_contact_id` | `Nullable(Int64)` | oui | Contact principal du besoin. Référence documentaire : raw.contacts.id ; intégrité temporelle à contrôler hors staging. |
| `relationships.agency.data.id` | `src_agency_id` | `Nullable(Int64)` | oui | Agence Boond qui porte le besoin. Référence documentaire : raw.agencies.id ; intégrité temporelle à contrôler hors staging. |
| `attributes` | `src_attributes` | `String` | non | Attributs complémentaires en JSON, dont `stateReason` : la raison de perte choisie dans la liste de l'étape. |

**Colonnes techniques ajoutées** : les 7 colonnes ST, toutes décrites enA.2. **Extraction SQL de présentation à coder** (liste complète ci-dessous, ST calculé dans CTE technique selon01 ; aucune extraction JSON métier) :

```sql
SELECT
    `meta.customer` AS src_tenant_id,
    `id` AS src_id,
    `meta.deleted` AS src_is_deleted,
    CAST(`meta.ts` AS DateTime64(3,'UTC')) AS src_published_at,
    `state` AS src_state_id,
    `typeOf` AS src_type_id,
    `title` AS src_title,
    `reference` AS src_reference,
    CAST(`creationDate` AS Nullable(DateTime64(3,'UTC'))) AS src_created_at,
    CAST(`updateDate` AS Nullable(DateTime64(3,'UTC'))) AS src_updated_at,
    CAST(`startDate` AS Nullable(DateTime64(3,'UTC'))) AS src_started_at,
    CAST(`answerDate` AS Nullable(DateTime64(3,'UTC'))) AS src_answer_due_at,
    CAST(`closingDate` AS Nullable(DateTime64(3,'UTC'))) AS src_closing_at,
    `turnoverEstimatedExcludingTax` AS src_estimated_amount_excluding_tax,
    `weighting` AS src_weighting_percent,
    `turnoverWeightedExcludingTax` AS src_weighted_amount_excluding_tax,
    `exchangeRate` AS src_exchange_rate,
    `origin.typeOf` AS src_origin_type_id,
    `origin.detail` AS src_origin_detail,
    `relationships.mainManager.data.id` AS src_main_manager_id,
    `relationships.createdBy.data.id` AS src_created_by_id,
    `relationships.company.data.id` AS src_company_id,
    `relationships.contact.data.id` AS src_contact_id,
    `relationships.agency.data.id` AS src_agency_id,
    `attributes` AS src_attributes
FROM {{ source('boond', 'opportunities') }}
```

<a id="stg_boond_actions"></a>

### stg_boond_actions

- **Couche/finalité** : staging technique, Actions du CRM : appels, demandes de démo, démos, rendez-vous, notes. Une action est rattachée à une fiche (le plus souvent un contact) et porte une date dans l'agenda. Reprise de toutes les 16 colonnes, sans sélection métier.
- **Objet futur** : `dbt/models/staging/boond/stg_boond_actions.sql`, YAML `_models.yml` du même dossier ; relation `stg_boond.stg_boond_actions` ; source `{{ source('boond', 'actions') }}` déclarée dans `_sources.yml`.
- **Grain** : une version CDC par identité/publication/contenu. Identité source : `meta.customer`, `id` ; source_version_key unique, ST non NULL. Grain historique distinct du dernier état.
- **Historique/calcul** : lire toutes versions et suppressions ; normaliser seulement noms/types de présentation. Premier chargement/cible vide complet. Reprise src_published_at >= borne typée calculée une seule fois depuis maxOrNull cible, recouvrement48 h paramétrable ; replay de la borne tentée ou full scan anti-jointure. Préserver collisions de contenu dans source_version_key, bloquer la lecture métier sur conflit identité+publication.
- **Physique** : incremental append/MergeTree, ORDER BY(src_tenant_id, src_id, src_published_at, source_version_key), sans partitionnement/TTL en v0.1 ; anti-jointure source_version_key sous is_incremental(), full_refresh=false,on_schema_change=fail,unique_key='source_version_key',inserts_only non activé. Le volume observé ne justifie pas de partitionnement supplémentaire sans mesure.
- **Rafraîchissement** : manuel ; complétude du lot vérifiée, aucun SLA automatique pour ce case D29. Source() seule en amont, lecture this pour anti-jointure ; aucune jointure métier.
- **Tests** : contrat ST, colonnes source exhaustives, source_version_key unique, clé candidate CDC sans conflit (ou identité unique par capture nonCDC), suppression conservée, relecture sans doublons, reprise/cible vide/arrivée hors fenêtre ; erreurs bloquent capture/publication.

| Colonne physique source | Colonne staging | Type final | NULL permis | Description / provenance / contraintes |
|---|---|---|---|---|
| `meta.customer` | `src_tenant_id` | `String` | non | Code du client Boond (tenant) dont vient la ligne. Un seul tenant dans ce jeu. |
| `id` | `src_id` | `Int64` | non | Identifiant de l'enregistrement dans Boond. Le même `id` revient à chaque version. |
| `meta.deleted` | `src_is_deleted` | `Bool` | non | Vrai sur la version qui enregistre la suppression de l'enregistrement dans Boond. |
| `meta.ts` | `src_published_at` | `DateTime64(3,'UTC')` | non | Horodatage de la version : moment où la modification a été publiée par le flux CDC. |
| `typeOf` | `src_type_id` | `Nullable(Int64)` | oui | Type d'action : appel, démo, demande de démo… Référence documentaire : raw.dictionaries.setting.action.contact ; intégrité temporelle à contrôler hors staging. |
| `title` | `src_title` | `String` | non | Intitulé de l'action. |
| `startDate` | `src_started_at` | `Nullable(DateTime64(3,'UTC'))` | oui | Début de l'action dans l'agenda. |
| `endDate` | `src_ended_at` | `Nullable(DateTime64(3,'UTC'))` | oui | Fin de l'action dans l'agenda. |
| `creationDate` | `src_created_at` | `Nullable(DateTime64(3,'UTC'))` | oui | Date de création de l'action. |
| `updateDate` | `src_updated_at` | `Nullable(DateTime64(3,'UTC'))` | oui | Date de la dernière modification. |
| `relationships.mainManager.data.id` | `src_main_manager_id` | `Nullable(Int64)` | oui | Responsable de l'enregistrement : le collaborateur qui le porte. Référence documentaire : raw.ressources.id ; intégrité temporelle à contrôler hors staging. |
| `relationships.createdBy.data.id` | `src_created_by_id` | `Nullable(Int64)` | oui | Collaborateur (ou robot) qui a créé l'enregistrement. Référence documentaire : raw.ressources.id ; intégrité temporelle à contrôler hors staging. |
| `relationships.company.data.id` | `src_company_id` | `Nullable(Int64)` | oui | Société de la fiche à laquelle l'action est rattachée. Référence documentaire : raw.companies.id ; intégrité temporelle à contrôler hors staging. |
| `relationships.dependsOn.data.id` | `src_depends_on_id` | `Nullable(Int64)` | oui | Identifiant de la fiche à laquelle l'action est rattachée. Le type de fiche est dans la colonne suivante. Référence documentaire : raw.contacts.id ; intégrité temporelle à contrôler hors staging. |
| `relationships.dependsOn.data.type` | `src_depends_on_type` | `LowCardinality(String)` | non | Type de la fiche rattachée : `contact`, `opportunity`, `company`… |
| `attributes` | `src_attributes` | `String` | non | Attributs en JSON, dont `text` : le contenu de l'action (HTML). |

**Colonnes techniques ajoutées** : les 7 colonnes ST, toutes décrites enA.2. **Extraction SQL de présentation à coder** (liste complète ci-dessous, ST calculé dans CTE technique selon01 ; aucune extraction JSON métier) :

```sql
SELECT
    `meta.customer` AS src_tenant_id,
    `id` AS src_id,
    `meta.deleted` AS src_is_deleted,
    CAST(`meta.ts` AS DateTime64(3,'UTC')) AS src_published_at,
    `typeOf` AS src_type_id,
    `title` AS src_title,
    CAST(`startDate` AS Nullable(DateTime64(3,'UTC'))) AS src_started_at,
    CAST(`endDate` AS Nullable(DateTime64(3,'UTC'))) AS src_ended_at,
    CAST(`creationDate` AS Nullable(DateTime64(3,'UTC'))) AS src_created_at,
    CAST(`updateDate` AS Nullable(DateTime64(3,'UTC'))) AS src_updated_at,
    `relationships.mainManager.data.id` AS src_main_manager_id,
    `relationships.createdBy.data.id` AS src_created_by_id,
    `relationships.company.data.id` AS src_company_id,
    `relationships.dependsOn.data.id` AS src_depends_on_id,
    `relationships.dependsOn.data.type` AS src_depends_on_type,
    `attributes` AS src_attributes
FROM {{ source('boond', 'actions') }}
```

<a id="stg_boond_companies"></a>

### stg_boond_companies

- **Couche/finalité** : staging technique, Sociétés : prospects et clients. Reprise de toutes les 14 colonnes, sans sélection métier.
- **Objet futur** : `dbt/models/staging/boond/stg_boond_companies.sql`, YAML `_models.yml` du même dossier ; relation `stg_boond.stg_boond_companies` ; source `{{ source('boond', 'companies') }}` déclarée dans `_sources.yml`.
- **Grain** : une version CDC par identité/publication/contenu. Identité source : `meta.customer`, `id` ; source_version_key unique, ST non NULL. Grain historique distinct du dernier état.
- **Historique/calcul** : lire toutes versions et suppressions ; normaliser seulement noms/types de présentation. Premier chargement/cible vide complet. Reprise src_published_at >= borne typée calculée une seule fois depuis maxOrNull cible, recouvrement48 h paramétrable ; replay de la borne tentée ou full scan anti-jointure. Préserver collisions de contenu dans source_version_key, bloquer la lecture métier sur conflit identité+publication.
- **Physique** : incremental append/MergeTree, ORDER BY(src_tenant_id, src_id, src_published_at, source_version_key), sans partitionnement/TTL en v0.1 ; anti-jointure source_version_key sous is_incremental(), full_refresh=false,on_schema_change=fail,unique_key='source_version_key',inserts_only non activé. Le volume observé ne justifie pas de partitionnement supplémentaire sans mesure.
- **Rafraîchissement** : manuel ; complétude du lot vérifiée, aucun SLA automatique pour ce case D29. Source() seule en amont, lecture this pour anti-jointure ; aucune jointure métier.
- **Tests** : contrat ST, colonnes source exhaustives, source_version_key unique, clé candidate CDC sans conflit (ou identité unique par capture nonCDC), suppression conservée, relecture sans doublons, reprise/cible vide/arrivée hors fenêtre ; erreurs bloquent capture/publication.

| Colonne physique source | Colonne staging | Type final | NULL permis | Description / provenance / contraintes |
|---|---|---|---|---|
| `meta.customer` | `src_tenant_id` | `String` | non | Code du client Boond (tenant) dont vient la ligne. Un seul tenant dans ce jeu. |
| `id` | `src_id` | `Int64` | non | Identifiant de l'enregistrement dans Boond. Le même `id` revient à chaque version. |
| `meta.deleted` | `src_is_deleted` | `Bool` | non | Vrai sur la version qui enregistre la suppression de l'enregistrement dans Boond. |
| `meta.ts` | `src_published_at` | `DateTime64(3,'UTC')` | non | Horodatage de la version : moment où la modification a été publiée par le flux CDC. |
| `name` | `src_name` | `String` | non | Raison sociale. |
| `state` | `src_state_id` | `Nullable(Int64)` | oui | État de la société : prospect, client lancé, client en risque… Référence documentaire : raw.dictionaries.setting.state.company ; intégrité temporelle à contrôler hors staging. |
| `country` | `src_country` | `String` | non | Pays. |
| `staff` | `src_staff` | `Nullable(Int64)` | oui | Effectif de la société. |
| `origin.typeOf` | `src_origin_type_id` | `Nullable(Int64)` | oui | Origine de la société. Référence documentaire : raw.dictionaries.setting.origin ; intégrité temporelle à contrôler hors staging. |
| `creationDate` | `src_created_at` | `Nullable(DateTime64(3,'UTC'))` | oui | Date de création de la fiche. |
| `updateDate` | `src_updated_at` | `Nullable(DateTime64(3,'UTC'))` | oui | Date de la dernière modification. |
| `relationships.pole.data.id` | `src_pole_id` | `Nullable(Int64)` | oui | Pôle de la société (profil client cible). Référence documentaire : raw.poles.id ; intégrité temporelle à contrôler hors staging. |
| `relationships.mainManager.data.id` | `src_main_manager_id` | `Nullable(Int64)` | oui | Responsable de l'enregistrement : le collaborateur qui le porte. Référence documentaire : raw.ressources.id ; intégrité temporelle à contrôler hors staging. |
| `relationships.agency.data.id` | `src_agency_id` | `Nullable(Int64)` | oui | Agence Boond de rattachement. Référence documentaire : raw.agencies.id ; intégrité temporelle à contrôler hors staging. |

**Colonnes techniques ajoutées** : les 7 colonnes ST, toutes décrites enA.2. **Extraction SQL de présentation à coder** (liste complète ci-dessous, ST calculé dans CTE technique selon01 ; aucune extraction JSON métier) :

```sql
SELECT
    `meta.customer` AS src_tenant_id,
    `id` AS src_id,
    `meta.deleted` AS src_is_deleted,
    CAST(`meta.ts` AS DateTime64(3,'UTC')) AS src_published_at,
    `name` AS src_name,
    `state` AS src_state_id,
    `country` AS src_country,
    `staff` AS src_staff,
    `origin.typeOf` AS src_origin_type_id,
    CAST(`creationDate` AS Nullable(DateTime64(3,'UTC'))) AS src_created_at,
    CAST(`updateDate` AS Nullable(DateTime64(3,'UTC'))) AS src_updated_at,
    `relationships.pole.data.id` AS src_pole_id,
    `relationships.mainManager.data.id` AS src_main_manager_id,
    `relationships.agency.data.id` AS src_agency_id
FROM {{ source('boond', 'companies') }}
```

<a id="stg_boond_contacts"></a>

### stg_boond_contacts

- **Couche/finalité** : staging technique, Contacts : les personnes chez les prospects et les clients. Reprise de toutes les 14 colonnes, sans sélection métier.
- **Objet futur** : `dbt/models/staging/boond/stg_boond_contacts.sql`, YAML `_models.yml` du même dossier ; relation `stg_boond.stg_boond_contacts` ; source `{{ source('boond', 'contacts') }}` déclarée dans `_sources.yml`.
- **Grain** : une version CDC par identité/publication/contenu. Identité source : `meta.customer`, `id` ; source_version_key unique, ST non NULL. Grain historique distinct du dernier état.
- **Historique/calcul** : lire toutes versions et suppressions ; normaliser seulement noms/types de présentation. Premier chargement/cible vide complet. Reprise src_published_at >= borne typée calculée une seule fois depuis maxOrNull cible, recouvrement48 h paramétrable ; replay de la borne tentée ou full scan anti-jointure. Préserver collisions de contenu dans source_version_key, bloquer la lecture métier sur conflit identité+publication.
- **Physique** : incremental append/MergeTree, ORDER BY(src_tenant_id, src_id, src_published_at, source_version_key), sans partitionnement/TTL en v0.1 ; anti-jointure source_version_key sous is_incremental(), full_refresh=false,on_schema_change=fail,unique_key='source_version_key',inserts_only non activé. Le volume observé ne justifie pas de partitionnement supplémentaire sans mesure.
- **Rafraîchissement** : manuel ; complétude du lot vérifiée, aucun SLA automatique pour ce case D29. Source() seule en amont, lecture this pour anti-jointure ; aucune jointure métier.
- **Tests** : contrat ST, colonnes source exhaustives, source_version_key unique, clé candidate CDC sans conflit (ou identité unique par capture nonCDC), suppression conservée, relecture sans doublons, reprise/cible vide/arrivée hors fenêtre ; erreurs bloquent capture/publication.

| Colonne physique source | Colonne staging | Type final | NULL permis | Description / provenance / contraintes |
|---|---|---|---|---|
| `meta.customer` | `src_tenant_id` | `String` | non | Code du client Boond (tenant) dont vient la ligne. Un seul tenant dans ce jeu. |
| `id` | `src_id` | `Int64` | non | Identifiant de l'enregistrement dans Boond. Le même `id` revient à chaque version. |
| `meta.deleted` | `src_is_deleted` | `Bool` | non | Vrai sur la version qui enregistre la suppression de l'enregistrement dans Boond. |
| `meta.ts` | `src_published_at` | `DateTime64(3,'UTC')` | non | Horodatage de la version : moment où la modification a été publiée par le flux CDC. |
| `firstName` | `src_first_name` | `String` | non | Prénom. |
| `lastName` | `src_last_name` | `String` | non | Nom. |
| `email1` | `src_primary_email` | `String` | non | Adresse e-mail principale. |
| `function` | `src_job_function` | `String` | non | Fonction du contact. |
| `state` | `src_state_id` | `Nullable(Int64)` | oui | État du contact. Référence documentaire : raw.dictionaries.setting.state.contact ; intégrité temporelle à contrôler hors staging. |
| `origin.typeOf` | `src_origin_type_id` | `Nullable(Int64)` | oui | Origine du contact. Référence documentaire : raw.dictionaries.setting.origin ; intégrité temporelle à contrôler hors staging. |
| `creationDate` | `src_created_at` | `Nullable(DateTime64(3,'UTC'))` | oui | Date de création de la fiche. |
| `updateDate` | `src_updated_at` | `Nullable(DateTime64(3,'UTC'))` | oui | Date de la dernière modification. |
| `relationships.company.data.id` | `src_company_id` | `Nullable(Int64)` | oui | Société du contact. Référence documentaire : raw.companies.id ; intégrité temporelle à contrôler hors staging. |
| `relationships.mainManager.data.id` | `src_main_manager_id` | `Nullable(Int64)` | oui | Responsable de l'enregistrement : le collaborateur qui le porte. Référence documentaire : raw.ressources.id ; intégrité temporelle à contrôler hors staging. |

**Colonnes techniques ajoutées** : les 7 colonnes ST, toutes décrites enA.2. **Extraction SQL de présentation à coder** (liste complète ci-dessous, ST calculé dans CTE technique selon01 ; aucune extraction JSON métier) :

```sql
SELECT
    `meta.customer` AS src_tenant_id,
    `id` AS src_id,
    `meta.deleted` AS src_is_deleted,
    CAST(`meta.ts` AS DateTime64(3,'UTC')) AS src_published_at,
    `firstName` AS src_first_name,
    `lastName` AS src_last_name,
    `email1` AS src_primary_email,
    `function` AS src_job_function,
    `state` AS src_state_id,
    `origin.typeOf` AS src_origin_type_id,
    CAST(`creationDate` AS Nullable(DateTime64(3,'UTC'))) AS src_created_at,
    CAST(`updateDate` AS Nullable(DateTime64(3,'UTC'))) AS src_updated_at,
    `relationships.company.data.id` AS src_company_id,
    `relationships.mainManager.data.id` AS src_main_manager_id
FROM {{ source('boond', 'contacts') }}
```

<a id="stg_boond_resources"></a>

### stg_boond_resources

- **Couche/finalité** : staging technique, Collaborateurs de Boond : commerciaux, account managers, direction, administratif, ainsi que les comptes robots des automatisations. Reprise de toutes les 12 colonnes, sans sélection métier.
- **Objet futur** : `dbt/models/staging/boond/stg_boond_resources.sql`, YAML `_models.yml` du même dossier ; relation `stg_boond.stg_boond_resources` ; source `{{ source('boond', 'ressources') }}` déclarée dans `_sources.yml`.
- **Grain** : une version CDC par identité/publication/contenu. Identité source : `meta.customer`, `id` ; source_version_key unique, ST non NULL. Grain historique distinct du dernier état.
- **Historique/calcul** : lire toutes versions et suppressions ; normaliser seulement noms/types de présentation. Premier chargement/cible vide complet. Reprise src_published_at >= borne typée calculée une seule fois depuis maxOrNull cible, recouvrement48 h paramétrable ; replay de la borne tentée ou full scan anti-jointure. Préserver collisions de contenu dans source_version_key, bloquer la lecture métier sur conflit identité+publication.
- **Physique** : incremental append/MergeTree, ORDER BY(src_tenant_id, src_id, src_published_at, source_version_key), sans partitionnement/TTL en v0.1 ; anti-jointure source_version_key sous is_incremental(), full_refresh=false,on_schema_change=fail,unique_key='source_version_key',inserts_only non activé. Le volume observé ne justifie pas de partitionnement supplémentaire sans mesure.
- **Rafraîchissement** : manuel ; complétude du lot vérifiée, aucun SLA automatique pour ce case D29. Source() seule en amont, lecture this pour anti-jointure ; aucune jointure métier.
- **Tests** : contrat ST, colonnes source exhaustives, source_version_key unique, clé candidate CDC sans conflit (ou identité unique par capture nonCDC), suppression conservée, relecture sans doublons, reprise/cible vide/arrivée hors fenêtre ; erreurs bloquent capture/publication.

| Colonne physique source | Colonne staging | Type final | NULL permis | Description / provenance / contraintes |
|---|---|---|---|---|
| `meta.customer` | `src_tenant_id` | `String` | non | Code du client Boond (tenant) dont vient la ligne. Un seul tenant dans ce jeu. |
| `id` | `src_id` | `Int64` | non | Identifiant de l'enregistrement dans Boond. Le même `id` revient à chaque version. |
| `meta.deleted` | `src_is_deleted` | `Bool` | non | Vrai sur la version qui enregistre la suppression de l'enregistrement dans Boond. |
| `meta.ts` | `src_published_at` | `DateTime64(3,'UTC')` | non | Horodatage de la version : moment où la modification a été publiée par le flux CDC. |
| `firstName` | `src_first_name` | `String` | non | Prénom. |
| `lastName` | `src_last_name` | `String` | non | Nom. |
| `title` | `src_title` | `String` | non | Intitulé de poste. |
| `email1` | `src_primary_email` | `String` | non | Adresse e-mail. |
| `state` | `src_state_id` | `Nullable(Int64)` | oui | État du collaborateur (en poste, sorti). Référence documentaire : raw.dictionaries.setting.state.resource ; intégrité temporelle à contrôler hors staging. |
| `creationDate` | `src_created_at` | `Nullable(DateTime64(3,'UTC'))` | oui | Date de création de la fiche. |
| `updateDate` | `src_updated_at` | `Nullable(DateTime64(3,'UTC'))` | oui | Date de la dernière modification. |
| `relationships.agency.data.id` | `src_agency_id` | `Nullable(Int64)` | oui | Agence du collaborateur. Référence documentaire : raw.agencies.id ; intégrité temporelle à contrôler hors staging. |

**Colonnes techniques ajoutées** : les 7 colonnes ST, toutes décrites enA.2. **Extraction SQL de présentation à coder** (liste complète ci-dessous, ST calculé dans CTE technique selon01 ; aucune extraction JSON métier) :

```sql
SELECT
    `meta.customer` AS src_tenant_id,
    `id` AS src_id,
    `meta.deleted` AS src_is_deleted,
    CAST(`meta.ts` AS DateTime64(3,'UTC')) AS src_published_at,
    `firstName` AS src_first_name,
    `lastName` AS src_last_name,
    `title` AS src_title,
    `email1` AS src_primary_email,
    `state` AS src_state_id,
    CAST(`creationDate` AS Nullable(DateTime64(3,'UTC'))) AS src_created_at,
    CAST(`updateDate` AS Nullable(DateTime64(3,'UTC'))) AS src_updated_at,
    `relationships.agency.data.id` AS src_agency_id
FROM {{ source('boond', 'ressources') }}
```

<a id="stg_boond_businessunits"></a>

### stg_boond_businessunits

- **Couche/finalité** : staging technique, Business units : les équipes dans Boond, avec la liste de leurs membres. Reprise de toutes les 8 colonnes, sans sélection métier.
- **Objet futur** : `dbt/models/staging/boond/stg_boond_businessunits.sql`, YAML `_models.yml` du même dossier ; relation `stg_boond.stg_boond_businessunits` ; source `{{ source('boond', 'businessunits') }}` déclarée dans `_sources.yml`.
- **Grain** : une version CDC par identité/publication/contenu. Identité source : `meta.customer`, `id` ; source_version_key unique, ST non NULL. Grain historique distinct du dernier état.
- **Historique/calcul** : lire toutes versions et suppressions ; normaliser seulement noms/types de présentation. Premier chargement/cible vide complet. Reprise src_published_at >= borne typée calculée une seule fois depuis maxOrNull cible, recouvrement48 h paramétrable ; replay de la borne tentée ou full scan anti-jointure. Préserver collisions de contenu dans source_version_key, bloquer la lecture métier sur conflit identité+publication.
- **Physique** : incremental append/MergeTree, ORDER BY(src_tenant_id, src_id, src_published_at, source_version_key), sans partitionnement/TTL en v0.1 ; anti-jointure source_version_key sous is_incremental(), full_refresh=false,on_schema_change=fail,unique_key='source_version_key',inserts_only non activé. Le volume observé ne justifie pas de partitionnement supplémentaire sans mesure.
- **Rafraîchissement** : manuel ; complétude du lot vérifiée, aucun SLA automatique pour ce case D29. Source() seule en amont, lecture this pour anti-jointure ; aucune jointure métier.
- **Tests** : contrat ST, colonnes source exhaustives, source_version_key unique, clé candidate CDC sans conflit (ou identité unique par capture nonCDC), suppression conservée, relecture sans doublons, reprise/cible vide/arrivée hors fenêtre ; erreurs bloquent capture/publication.

| Colonne physique source | Colonne staging | Type final | NULL permis | Description / provenance / contraintes |
|---|---|---|---|---|
| `meta.customer` | `src_tenant_id` | `String` | non | Code du client Boond (tenant) dont vient la ligne. Un seul tenant dans ce jeu. |
| `id` | `src_id` | `Int64` | non | Identifiant de l'enregistrement dans Boond. Le même `id` revient à chaque version. |
| `meta.deleted` | `src_is_deleted` | `Bool` | non | Vrai sur la version qui enregistre la suppression de l'enregistrement dans Boond. |
| `meta.ts` | `src_published_at` | `DateTime64(3,'UTC')` | non | Horodatage de la version : moment où la modification a été publiée par le flux CDC. |
| `name` | `src_name` | `String` | non | Nom de l'équipe. |
| `relationships.includedManagers.data` | `src_included_managers_json` | `String` | non | Membres de l'équipe, en JSON : liste de `{"id": …, "type": "resource"}`. Référence documentaire : raw.ressources.id ; intégrité temporelle à contrôler hors staging. |
| `creationDate` | `src_created_at` | `Nullable(DateTime64(3,'UTC'))` | oui | Date de création. |
| `updateDate` | `src_updated_at` | `Nullable(DateTime64(3,'UTC'))` | oui | Date de la dernière modification. |

**Colonnes techniques ajoutées** : les 7 colonnes ST, toutes décrites enA.2. **Extraction SQL de présentation à coder** (liste complète ci-dessous, ST calculé dans CTE technique selon01 ; aucune extraction JSON métier) :

```sql
SELECT
    `meta.customer` AS src_tenant_id,
    `id` AS src_id,
    `meta.deleted` AS src_is_deleted,
    CAST(`meta.ts` AS DateTime64(3,'UTC')) AS src_published_at,
    `name` AS src_name,
    `relationships.includedManagers.data` AS src_included_managers_json,
    CAST(`creationDate` AS Nullable(DateTime64(3,'UTC'))) AS src_created_at,
    CAST(`updateDate` AS Nullable(DateTime64(3,'UTC'))) AS src_updated_at
FROM {{ source('boond', 'businessunits') }}
```

<a id="stg_boond_agencies"></a>

### stg_boond_agencies

- **Couche/finalité** : staging technique, Agences Boond : les entités juridiques et commerciales (France, Espagne). Reprise de toutes les 7 colonnes, sans sélection métier.
- **Objet futur** : `dbt/models/staging/boond/stg_boond_agencies.sql`, YAML `_models.yml` du même dossier ; relation `stg_boond.stg_boond_agencies` ; source `{{ source('boond', 'agencies') }}` déclarée dans `_sources.yml`.
- **Grain** : une version CDC par identité/publication/contenu. Identité source : `meta.customer`, `id` ; source_version_key unique, ST non NULL. Grain historique distinct du dernier état.
- **Historique/calcul** : lire toutes versions et suppressions ; normaliser seulement noms/types de présentation. Premier chargement/cible vide complet. Reprise src_published_at >= borne typée calculée une seule fois depuis maxOrNull cible, recouvrement48 h paramétrable ; replay de la borne tentée ou full scan anti-jointure. Préserver collisions de contenu dans source_version_key, bloquer la lecture métier sur conflit identité+publication.
- **Physique** : incremental append/MergeTree, ORDER BY(src_tenant_id, src_id, src_published_at, source_version_key), sans partitionnement/TTL en v0.1 ; anti-jointure source_version_key sous is_incremental(), full_refresh=false,on_schema_change=fail,unique_key='source_version_key',inserts_only non activé. Le volume observé ne justifie pas de partitionnement supplémentaire sans mesure.
- **Rafraîchissement** : manuel ; complétude du lot vérifiée, aucun SLA automatique pour ce case D29. Source() seule en amont, lecture this pour anti-jointure ; aucune jointure métier.
- **Tests** : contrat ST, colonnes source exhaustives, source_version_key unique, clé candidate CDC sans conflit (ou identité unique par capture nonCDC), suppression conservée, relecture sans doublons, reprise/cible vide/arrivée hors fenêtre ; erreurs bloquent capture/publication.

| Colonne physique source | Colonne staging | Type final | NULL permis | Description / provenance / contraintes |
|---|---|---|---|---|
| `meta.customer` | `src_tenant_id` | `String` | non | Code du client Boond (tenant) dont vient la ligne. Un seul tenant dans ce jeu. |
| `id` | `src_id` | `Int64` | non | Identifiant de l'enregistrement dans Boond. Le même `id` revient à chaque version. |
| `meta.deleted` | `src_is_deleted` | `Bool` | non | Vrai sur la version qui enregistre la suppression de l'enregistrement dans Boond. |
| `meta.ts` | `src_published_at` | `DateTime64(3,'UTC')` | non | Horodatage de la version : moment où la modification a été publiée par le flux CDC. |
| `name` | `src_name` | `String` | non | Nom de l'agence. |
| `country` | `src_country` | `String` | non | Pays de l'agence. |
| `creationDate` | `src_created_at` | `Nullable(DateTime64(3,'UTC'))` | oui | Date de création. |

**Colonnes techniques ajoutées** : les 7 colonnes ST, toutes décrites enA.2. **Extraction SQL de présentation à coder** (liste complète ci-dessous, ST calculé dans CTE technique selon01 ; aucune extraction JSON métier) :

```sql
SELECT
    `meta.customer` AS src_tenant_id,
    `id` AS src_id,
    `meta.deleted` AS src_is_deleted,
    CAST(`meta.ts` AS DateTime64(3,'UTC')) AS src_published_at,
    `name` AS src_name,
    `country` AS src_country,
    CAST(`creationDate` AS Nullable(DateTime64(3,'UTC'))) AS src_created_at
FROM {{ source('boond', 'agencies') }}
```

<a id="stg_boond_poles"></a>

### stg_boond_poles

- **Couche/finalité** : staging technique, Pôles : la segmentation des sociétés par profil de client cible. Reprise de toutes les 7 colonnes, sans sélection métier.
- **Objet futur** : `dbt/models/staging/boond/stg_boond_poles.sql`, YAML `_models.yml` du même dossier ; relation `stg_boond.stg_boond_poles` ; source `{{ source('boond', 'poles') }}` déclarée dans `_sources.yml`.
- **Grain** : une version CDC par identité/publication/contenu. Identité source : `meta.customer`, `id` ; source_version_key unique, ST non NULL. Grain historique distinct du dernier état.
- **Historique/calcul** : lire toutes versions et suppressions ; normaliser seulement noms/types de présentation. Premier chargement/cible vide complet. Reprise src_published_at >= borne typée calculée une seule fois depuis maxOrNull cible, recouvrement48 h paramétrable ; replay de la borne tentée ou full scan anti-jointure. Préserver collisions de contenu dans source_version_key, bloquer la lecture métier sur conflit identité+publication.
- **Physique** : incremental append/MergeTree, ORDER BY(src_tenant_id, src_id, src_published_at, source_version_key), sans partitionnement/TTL en v0.1 ; anti-jointure source_version_key sous is_incremental(), full_refresh=false,on_schema_change=fail,unique_key='source_version_key',inserts_only non activé. Le volume observé ne justifie pas de partitionnement supplémentaire sans mesure.
- **Rafraîchissement** : manuel ; complétude du lot vérifiée, aucun SLA automatique pour ce case D29. Source() seule en amont, lecture this pour anti-jointure ; aucune jointure métier.
- **Tests** : contrat ST, colonnes source exhaustives, source_version_key unique, clé candidate CDC sans conflit (ou identité unique par capture nonCDC), suppression conservée, relecture sans doublons, reprise/cible vide/arrivée hors fenêtre ; erreurs bloquent capture/publication.

| Colonne physique source | Colonne staging | Type final | NULL permis | Description / provenance / contraintes |
|---|---|---|---|---|
| `meta.customer` | `src_tenant_id` | `String` | non | Code du client Boond (tenant) dont vient la ligne. Un seul tenant dans ce jeu. |
| `id` | `src_id` | `Int64` | non | Identifiant de l'enregistrement dans Boond. Le même `id` revient à chaque version. |
| `meta.deleted` | `src_is_deleted` | `Bool` | non | Vrai sur la version qui enregistre la suppression de l'enregistrement dans Boond. |
| `meta.ts` | `src_published_at` | `DateTime64(3,'UTC')` | non | Horodatage de la version : moment où la modification a été publiée par le flux CDC. |
| `name` | `src_name` | `String` | non | Nom du pôle. |
| `state` | `src_is_active` | `Bool` | non | Pôle actif. |
| `creationDate` | `src_created_at` | `Nullable(DateTime64(3,'UTC'))` | oui | Date de création. |

**Colonnes techniques ajoutées** : les 7 colonnes ST, toutes décrites enA.2. **Extraction SQL de présentation à coder** (liste complète ci-dessous, ST calculé dans CTE technique selon01 ; aucune extraction JSON métier) :

```sql
SELECT
    `meta.customer` AS src_tenant_id,
    `id` AS src_id,
    `meta.deleted` AS src_is_deleted,
    CAST(`meta.ts` AS DateTime64(3,'UTC')) AS src_published_at,
    `name` AS src_name,
    `state` AS src_is_active,
    CAST(`creationDate` AS Nullable(DateTime64(3,'UTC'))) AS src_created_at
FROM {{ source('boond', 'poles') }}
```

<a id="stg_boond_dictionaries"></a>

### stg_boond_dictionaries

- **Couche/finalité** : staging technique, Référentiels de Boond : listes de valeurs paramétrées par le client (étapes, types d'action, origines…). Chaque colonne `setting.*` contient un tableau JSON d'entrées `{"id", "value", …}`. Reprise de toutes les 12 colonnes, sans sélection métier.
- **Objet futur** : `dbt/models/staging/boond/stg_boond_dictionaries.sql`, YAML `_models.yml` du même dossier ; relation `stg_boond.stg_boond_dictionaries` ; source `{{ source('boond', 'dictionaries') }}` déclarée dans `_sources.yml`.
- **Grain** : une version CDC par identité/publication/contenu. Identité source : `meta.customer`, `meta.language` ; source_version_key unique, ST non NULL. Grain historique distinct du dernier état.
- **Historique/calcul** : lire toutes versions et suppressions ; normaliser seulement noms/types de présentation. Premier chargement/cible vide complet. Reprise src_published_at >= borne typée calculée une seule fois depuis maxOrNull cible, recouvrement48 h paramétrable ; replay de la borne tentée ou full scan anti-jointure. Préserver collisions de contenu dans source_version_key, bloquer la lecture métier sur conflit identité+publication.
- **Physique** : incremental append/MergeTree, ORDER BY(src_tenant_id, src_language, src_published_at, source_version_key), sans partitionnement/TTL en v0.1 ; anti-jointure source_version_key sous is_incremental(), full_refresh=false,on_schema_change=fail,unique_key='source_version_key',inserts_only non activé. Le volume observé ne justifie pas de partitionnement supplémentaire sans mesure.
- **Rafraîchissement** : manuel ; complétude du lot vérifiée, aucun SLA automatique pour ce case D29. Source() seule en amont, lecture this pour anti-jointure ; aucune jointure métier.
- **Tests** : contrat ST, colonnes source exhaustives, source_version_key unique, clé candidate CDC sans conflit (ou identité unique par capture nonCDC), suppression conservée, relecture sans doublons, reprise/cible vide/arrivée hors fenêtre ; erreurs bloquent capture/publication.

| Colonne physique source | Colonne staging | Type final | NULL permis | Description / provenance / contraintes |
|---|---|---|---|---|
| `meta.customer` | `src_tenant_id` | `String` | non | Code du client Boond (tenant) dont vient la ligne. Un seul tenant dans ce jeu. |
| `meta.deleted` | `src_is_deleted` | `Bool` | non | Vrai sur la version qui enregistre la suppression de l'enregistrement dans Boond. |
| `meta.ts` | `src_published_at` | `DateTime64(3,'UTC')` | non | Horodatage de la version : moment où la modification a été publiée par le flux CDC. |
| `meta.language` | `src_language` | `String` | non | Langue des libellés de la version. |
| `setting.state.opportunity` | `src_setting_state_opportunity_json` | `Nullable(String)` | oui | Étapes des besoins. Chaque entrée : `id`, `value` (libellé), `active` (le besoin est encore en cours), `isEnabled` (étape proposée dans l'interface), `weighting` (pondération), `reason` (raisons proposées quand on choisit cette étape). |
| `setting.typeOf.project` | `src_setting_type_of_project_json` | `LowCardinality(String)` | non | Types de besoin et de projet. |
| `setting.origin` | `src_setting_origin_json` | `String` | non | Origines : canaux d'arrivée des besoins, sociétés et contacts. |
| `setting.action.contact` | `src_setting_action_contact_json` | `String` | non | Types d'action possibles sur un contact. |
| `setting.state.company` | `src_setting_state_company_json` | `Nullable(String)` | oui | États des sociétés. |
| `setting.state.contact` | `src_setting_state_contact_json` | `Nullable(String)` | oui | États des contacts. |
| `setting.state.resource` | `src_setting_state_resource_json` | `Nullable(String)` | oui | États des collaborateurs. |
| `setting.state.delivery` | `src_setting_state_delivery_json` | `Nullable(String)` | oui | États des livraisons. |

**Colonnes techniques ajoutées** : les 7 colonnes ST, toutes décrites enA.2. **Extraction SQL de présentation à coder** (liste complète ci-dessous, ST calculé dans CTE technique selon01 ; aucune extraction JSON métier) :

```sql
SELECT
    `meta.customer` AS src_tenant_id,
    `meta.deleted` AS src_is_deleted,
    CAST(`meta.ts` AS DateTime64(3,'UTC')) AS src_published_at,
    `meta.language` AS src_language,
    `setting.state.opportunity` AS src_setting_state_opportunity_json,
    `setting.typeOf.project` AS src_setting_type_of_project_json,
    `setting.origin` AS src_setting_origin_json,
    `setting.action.contact` AS src_setting_action_contact_json,
    `setting.state.company` AS src_setting_state_company_json,
    `setting.state.contact` AS src_setting_state_contact_json,
    `setting.state.resource` AS src_setting_state_resource_json,
    `setting.state.delivery` AS src_setting_state_delivery_json
FROM {{ source('boond', 'dictionaries') }}
```

<a id="stg_boond_projects"></a>

### stg_boond_projects

- **Couche/finalité** : staging technique, Projets : quand un besoin est signé, le client est équipé dans Boond sous la forme d'un projet qui regroupe ses lignes d'abonnement. Reprise de toutes les 13 colonnes, sans sélection métier.
- **Objet futur** : `dbt/models/staging/boond/stg_boond_projects.sql`, YAML `_models.yml` du même dossier ; relation `stg_boond.stg_boond_projects` ; source `{{ source('boond', 'projects') }}` déclarée dans `_sources.yml`.
- **Grain** : une version CDC par identité/publication/contenu. Identité source : `meta.customer`, `id` ; source_version_key unique, ST non NULL. Grain historique distinct du dernier état.
- **Historique/calcul** : lire toutes versions et suppressions ; normaliser seulement noms/types de présentation. Premier chargement/cible vide complet. Reprise src_published_at >= borne typée calculée une seule fois depuis maxOrNull cible, recouvrement48 h paramétrable ; replay de la borne tentée ou full scan anti-jointure. Préserver collisions de contenu dans source_version_key, bloquer la lecture métier sur conflit identité+publication.
- **Physique** : incremental append/MergeTree, ORDER BY(src_tenant_id, src_id, src_published_at, source_version_key), sans partitionnement/TTL en v0.1 ; anti-jointure source_version_key sous is_incremental(), full_refresh=false,on_schema_change=fail,unique_key='source_version_key',inserts_only non activé. Le volume observé ne justifie pas de partitionnement supplémentaire sans mesure.
- **Rafraîchissement** : manuel ; complétude du lot vérifiée, aucun SLA automatique pour ce case D29. Source() seule en amont, lecture this pour anti-jointure ; aucune jointure métier.
- **Tests** : contrat ST, colonnes source exhaustives, source_version_key unique, clé candidate CDC sans conflit (ou identité unique par capture nonCDC), suppression conservée, relecture sans doublons, reprise/cible vide/arrivée hors fenêtre ; erreurs bloquent capture/publication.

| Colonne physique source | Colonne staging | Type final | NULL permis | Description / provenance / contraintes |
|---|---|---|---|---|
| `meta.customer` | `src_tenant_id` | `String` | non | Code du client Boond (tenant) dont vient la ligne. Un seul tenant dans ce jeu. |
| `id` | `src_id` | `Int64` | non | Identifiant de l'enregistrement dans Boond. Le même `id` revient à chaque version. |
| `meta.deleted` | `src_is_deleted` | `Bool` | non | Vrai sur la version qui enregistre la suppression de l'enregistrement dans Boond. |
| `meta.ts` | `src_published_at` | `DateTime64(3,'UTC')` | non | Horodatage de la version : moment où la modification a été publiée par le flux CDC. |
| `reference` | `src_reference` | `String` | non | Référence du projet. |
| `typeOf` | `src_type_id` | `Nullable(Int64)` | oui | Type de projet. Référence documentaire : raw.dictionaries.setting.typeOf.project ; intégrité temporelle à contrôler hors staging. |
| `startDate` | `src_started_at` | `Nullable(DateTime64(3,'UTC'))` | oui | Début du projet. |
| `endDate` | `src_ended_at` | `Nullable(DateTime64(3,'UTC'))` | oui | Fin du projet. |
| `creationDate` | `src_created_at` | `Nullable(DateTime64(3,'UTC'))` | oui | Date de création. |
| `updateDate` | `src_updated_at` | `Nullable(DateTime64(3,'UTC'))` | oui | Date de la dernière modification. |
| `relationships.opportunity.data.id` | `src_opportunity_id` | `Nullable(Int64)` | oui | Besoin d'origine du projet. Référence documentaire : raw.opportunities.id ; intégrité temporelle à contrôler hors staging. |
| `relationships.company.data.id` | `src_company_id` | `Nullable(Int64)` | oui | Société cliente. Référence documentaire : raw.companies.id ; intégrité temporelle à contrôler hors staging. |
| `relationships.mainManager.data.id` | `src_main_manager_id` | `Nullable(Int64)` | oui | Responsable de l'enregistrement : le collaborateur qui le porte. Référence documentaire : raw.ressources.id ; intégrité temporelle à contrôler hors staging. |

**Colonnes techniques ajoutées** : les 7 colonnes ST, toutes décrites enA.2. **Extraction SQL de présentation à coder** (liste complète ci-dessous, ST calculé dans CTE technique selon01 ; aucune extraction JSON métier) :

```sql
SELECT
    `meta.customer` AS src_tenant_id,
    `id` AS src_id,
    `meta.deleted` AS src_is_deleted,
    CAST(`meta.ts` AS DateTime64(3,'UTC')) AS src_published_at,
    `reference` AS src_reference,
    `typeOf` AS src_type_id,
    CAST(`startDate` AS Nullable(DateTime64(3,'UTC'))) AS src_started_at,
    CAST(`endDate` AS Nullable(DateTime64(3,'UTC'))) AS src_ended_at,
    CAST(`creationDate` AS Nullable(DateTime64(3,'UTC'))) AS src_created_at,
    CAST(`updateDate` AS Nullable(DateTime64(3,'UTC'))) AS src_updated_at,
    `relationships.opportunity.data.id` AS src_opportunity_id,
    `relationships.company.data.id` AS src_company_id,
    `relationships.mainManager.data.id` AS src_main_manager_id
FROM {{ source('boond', 'projects') }}
```

<a id="stg_boond_deliveries"></a>

### stg_boond_deliveries

- **Couche/finalité** : staging technique, Livraisons : les lignes d'un projet. Pour un client Boond, une ligne = un abonnement facturé chaque mois sur sa période. Reprise de toutes les 13 colonnes, sans sélection métier.
- **Objet futur** : `dbt/models/staging/boond/stg_boond_deliveries.sql`, YAML `_models.yml` du même dossier ; relation `stg_boond.stg_boond_deliveries` ; source `{{ source('boond', 'deliveries') }}` déclarée dans `_sources.yml`.
- **Grain** : une version CDC par identité/publication/contenu. Identité source : `meta.customer`, `id` ; source_version_key unique, ST non NULL. Grain historique distinct du dernier état.
- **Historique/calcul** : lire toutes versions et suppressions ; normaliser seulement noms/types de présentation. Premier chargement/cible vide complet. Reprise src_published_at >= borne typée calculée une seule fois depuis maxOrNull cible, recouvrement48 h paramétrable ; replay de la borne tentée ou full scan anti-jointure. Préserver collisions de contenu dans source_version_key, bloquer la lecture métier sur conflit identité+publication.
- **Physique** : incremental append/MergeTree, ORDER BY(src_tenant_id, src_id, src_published_at, source_version_key), sans partitionnement/TTL en v0.1 ; anti-jointure source_version_key sous is_incremental(), full_refresh=false,on_schema_change=fail,unique_key='source_version_key',inserts_only non activé. Le volume observé ne justifie pas de partitionnement supplémentaire sans mesure.
- **Rafraîchissement** : manuel ; complétude du lot vérifiée, aucun SLA automatique pour ce case D29. Source() seule en amont, lecture this pour anti-jointure ; aucune jointure métier.
- **Tests** : contrat ST, colonnes source exhaustives, source_version_key unique, clé candidate CDC sans conflit (ou identité unique par capture nonCDC), suppression conservée, relecture sans doublons, reprise/cible vide/arrivée hors fenêtre ; erreurs bloquent capture/publication.

| Colonne physique source | Colonne staging | Type final | NULL permis | Description / provenance / contraintes |
|---|---|---|---|---|
| `meta.customer` | `src_tenant_id` | `String` | non | Code du client Boond (tenant) dont vient la ligne. Un seul tenant dans ce jeu. |
| `id` | `src_id` | `Int64` | non | Identifiant de l'enregistrement dans Boond. Le même `id` revient à chaque version. |
| `meta.deleted` | `src_is_deleted` | `Bool` | non | Vrai sur la version qui enregistre la suppression de l'enregistrement dans Boond. |
| `meta.ts` | `src_published_at` | `DateTime64(3,'UTC')` | non | Horodatage de la version : moment où la modification a été publiée par le flux CDC. |
| `title` | `src_title` | `String` | non | Intitulé de la ligne. |
| `state` | `src_state_id` | `Nullable(Int64)` | oui | État de la livraison. Référence documentaire : raw.dictionaries.setting.state.delivery ; intégrité temporelle à contrôler hors staging. |
| `startDate` | `src_started_at` | `Nullable(DateTime64(3,'UTC'))` | oui | Début de la période facturée. |
| `endDate` | `src_ended_at` | `Nullable(DateTime64(3,'UTC'))` | oui | Fin de la période facturée. |
| `averageDailyPriceExcludingTax` | `src_average_daily_price_excluding_tax` | `Nullable(Float64)` | oui | Tarif de vente journalier moyen HT. Pour une ligne d'abonnement, Boond y range le prix mensuel (quantité facturée × prix unitaire, détail dans `attributes`). |
| `creationDate` | `src_created_at` | `Nullable(DateTime64(3,'UTC'))` | oui | Date de création. |
| `updateDate` | `src_updated_at` | `Nullable(DateTime64(3,'UTC'))` | oui | Date de la dernière modification. |
| `relationships.project.data.id` | `src_project_id` | `Nullable(Int64)` | oui | Projet de la ligne. Référence documentaire : raw.projects.id ; intégrité temporelle à contrôler hors staging. |
| `attributes` | `src_attributes` | `String` | non | Attributs en JSON : `subscriptionQuantityCharged` (licences facturées) et `subscriptionPriceExcludingTax` (prix unitaire mensuel). |

**Colonnes techniques ajoutées** : les 7 colonnes ST, toutes décrites enA.2. **Extraction SQL de présentation à coder** (liste complète ci-dessous, ST calculé dans CTE technique selon01 ; aucune extraction JSON métier) :

```sql
SELECT
    `meta.customer` AS src_tenant_id,
    `id` AS src_id,
    `meta.deleted` AS src_is_deleted,
    CAST(`meta.ts` AS DateTime64(3,'UTC')) AS src_published_at,
    `title` AS src_title,
    `state` AS src_state_id,
    CAST(`startDate` AS Nullable(DateTime64(3,'UTC'))) AS src_started_at,
    CAST(`endDate` AS Nullable(DateTime64(3,'UTC'))) AS src_ended_at,
    `averageDailyPriceExcludingTax` AS src_average_daily_price_excluding_tax,
    CAST(`creationDate` AS Nullable(DateTime64(3,'UTC'))) AS src_created_at,
    CAST(`updateDate` AS Nullable(DateTime64(3,'UTC'))) AS src_updated_at,
    `relationships.project.data.id` AS src_project_id,
    `attributes` AS src_attributes
FROM {{ source('boond', 'deliveries') }}
```

<a id="stg_hubspot_contacts"></a>

### stg_hubspot_contacts

- **Couche/finalité** : staging technique, Contacts HubSpot (marketing). Copie du portail HubSpot reconstruite chaque nuit : une ligne par contact, dans son état du jour. Reprise de toutes les 15 colonnes, sans sélection métier.
- **Objet futur** : `dbt/models/staging/hubspot/stg_hubspot_contacts.sql`, YAML `_models.yml` du même dossier ; relation `stg_hubspot.stg_hubspot_contacts` ; source `{{ source('hubspot', 'contacts') }}` déclarée dans `_sources.yml`.
- **Grain** : une observation changée de contenu ou présence par identité/capture complète. Identité source : `id` ; source_version_key unique, ST non NULL. Grain historique distinct du dernier état.
- **Historique/calcul** : capture complète ; comparer chaque identité à la dernière capture COMPLÈTE autorisée par source_capture_keys. Insérer changement, réapparition ou absence observée, sans règle métier. Mettre archived à disposition, ne pas exclure les archivés. Même contenu après un état différent=>nouvelle capture ; lecture échouée/incomplète=>pas de marqueur de disparition validé. Ne pas utiliser updatedAt comme unique fenêtre de capture.
- **Physique** : incremental append/MergeTree, ORDER BY(src_id, capture_at, source_version_key), sans partitionnement/TTL en v0.1 ; anti-jointure source_version_key sous is_incremental(), full_refresh=false,on_schema_change=fail,unique_key='source_version_key',inserts_only non activé. Le volume observé ne justifie pas de partitionnement supplémentaire sans mesure.
- **Rafraîchissement** : manuel ; complétude du lot vérifiée, aucun SLA automatique pour ce case D29. Source() seule en amont, lecture this pour anti-jointure ; aucune jointure métier.
- **Tests** : contrat ST, colonnes source exhaustives, source_version_key unique, clé candidate CDC sans conflit (ou identité unique par capture nonCDC), suppression conservée, relecture sans doublons, reprise/cible vide/arrivée hors fenêtre ; erreurs bloquent capture/publication.

| Colonne physique source | Colonne staging | Type final | NULL permis | Description / provenance / contraintes |
|---|---|---|---|---|
| `id` | `src_id` | `String` | non | Identifiant HubSpot du contact. |
| `properties_email` | `src_email` | `String` | non | Adresse e-mail. |
| `properties_createdate` | `src_created_at` | `Nullable(DateTime64(3,'UTC'))` | oui | Date de création du contact dans HubSpot. |
| `properties_lifecyclestage` | `src_lifecycle_stage` | `String` | non | Étape du cycle de vie HubSpot : subscriber, lead, opportunity, customer, other. |
| `properties_hs_latest_source` | `src_latest_source` | `String` | non | Dernière source de trafic connue (ORGANIC_SEARCH, PAID_SEARCH, PAID_SOCIAL, OFFLINE…). |
| `properties_utm_source` | `src_utm_source` | `String` | non | Paramètre `utm_source` capté par le formulaire. |
| `properties_utm_campaign` | `src_utm_campaign` | `String` | non | Paramètre `utm_campaign` capté par le formulaire. |
| `properties_first_conversion_event_name` | `src_first_conversion_name` | `String` | non | Nom du premier formulaire rempli. |
| `properties_first_conversion_date` | `src_first_conversion_at` | `Nullable(DateTime64(3,'UTC'))` | oui | Date du premier formulaire rempli. |
| `properties_boondid` | `src_boond_contact_id` | `String` | non | Identifiant du contact dans Boond. Référence documentaire : raw.contacts.id ; intégrité temporelle à contrôler hors staging. |
| `properties_statut_boond` | `src_boond_state_id` | `String` | non | Code d'état du contact dans Boond. |
| `properties_creation_boond` | `src_boond_created_at` | `Nullable(DateTime64(3,'UTC'))` | oui | Date de création du contact dans Boond. |
| `properties_hubspot_owner_id` | `src_hubspot_owner_id` | `String` | non | Propriétaire HubSpot du contact. |
| `archived` | `src_is_archived` | `Bool` | non | Contact archivé dans HubSpot. |
| `updatedAt` | `src_updated_at` | `DateTime64(3,'UTC')` | non | Dernière modification dans HubSpot. |

**Colonnes techniques ajoutées** : les 7 colonnes ST, toutes décrites enA.2. **Extraction SQL de présentation à coder** (liste complète ci-dessous, ST calculé dans CTE technique selon01 ; aucune extraction JSON métier) :

```sql
SELECT
    `id` AS src_id,
    `properties_email` AS src_email,
    CAST(`properties_createdate` AS Nullable(DateTime64(3,'UTC'))) AS src_created_at,
    `properties_lifecyclestage` AS src_lifecycle_stage,
    `properties_hs_latest_source` AS src_latest_source,
    `properties_utm_source` AS src_utm_source,
    `properties_utm_campaign` AS src_utm_campaign,
    `properties_first_conversion_event_name` AS src_first_conversion_name,
    CAST(`properties_first_conversion_date` AS Nullable(DateTime64(3,'UTC'))) AS src_first_conversion_at,
    `properties_boondid` AS src_boond_contact_id,
    `properties_statut_boond` AS src_boond_state_id,
    CAST(`properties_creation_boond` AS Nullable(DateTime64(3,'UTC'))) AS src_boond_created_at,
    `properties_hubspot_owner_id` AS src_hubspot_owner_id,
    `archived` AS src_is_archived,
    CAST(`updatedAt` AS DateTime64(3,'UTC')) AS src_updated_at
FROM {{ source('hubspot', 'contacts') }}
```

<a id="stg_hubspot_deals"></a>

### stg_hubspot_deals

- **Couche/finalité** : staging technique, Deals HubSpot. Ils reflètent les besoins Boond pour le marketing : une ligne par deal, dans son état du jour. Reprise de toutes les 16 colonnes, sans sélection métier.
- **Objet futur** : `dbt/models/staging/hubspot/stg_hubspot_deals.sql`, YAML `_models.yml` du même dossier ; relation `stg_hubspot.stg_hubspot_deals` ; source `{{ source('hubspot', 'deals') }}` déclarée dans `_sources.yml`.
- **Grain** : une observation changée de contenu ou présence par identité/capture complète. Identité source : `id` ; source_version_key unique, ST non NULL. Grain historique distinct du dernier état.
- **Historique/calcul** : capture complète ; comparer chaque identité à la dernière capture COMPLÈTE autorisée par source_capture_keys. Insérer changement, réapparition ou absence observée, sans règle métier. Mettre archived à disposition, ne pas exclure les archivés. Même contenu après un état différent=>nouvelle capture ; lecture échouée/incomplète=>pas de marqueur de disparition validé. Ne pas utiliser updatedAt comme unique fenêtre de capture.
- **Physique** : incremental append/MergeTree, ORDER BY(src_id, capture_at, source_version_key), sans partitionnement/TTL en v0.1 ; anti-jointure source_version_key sous is_incremental(), full_refresh=false,on_schema_change=fail,unique_key='source_version_key',inserts_only non activé. Le volume observé ne justifie pas de partitionnement supplémentaire sans mesure.
- **Rafraîchissement** : manuel ; complétude du lot vérifiée, aucun SLA automatique pour ce case D29. Source() seule en amont, lecture this pour anti-jointure ; aucune jointure métier.
- **Tests** : contrat ST, colonnes source exhaustives, source_version_key unique, clé candidate CDC sans conflit (ou identité unique par capture nonCDC), suppression conservée, relecture sans doublons, reprise/cible vide/arrivée hors fenêtre ; erreurs bloquent capture/publication.

| Colonne physique source | Colonne staging | Type final | NULL permis | Description / provenance / contraintes |
|---|---|---|---|---|
| `id` | `src_id` | `String` | non | Identifiant HubSpot du deal. |
| `properties_dealname` | `src_deal_name` | `String` | non | Nom du deal. |
| `properties_pipeline` | `src_pipeline_id` | `String` | non | Pipeline HubSpot du deal. |
| `properties_dealstage` | `src_stage_id` | `String` | non | Étape du deal dans son pipeline HubSpot. |
| `properties_hs_is_closed` | `src_is_closed` | `Bool` | non | HubSpot considère le deal comme fermé. |
| `properties_amount` | `src_amount` | `Nullable(Float64)` | oui | Montant du deal. |
| `properties_createdate` | `src_created_at` | `Nullable(DateTime64(3,'UTC'))` | oui | Date de création du deal dans HubSpot. |
| `properties_closedate` | `src_closed_at` | `Nullable(DateTime64(3,'UTC'))` | oui | Date de fermeture du deal dans HubSpot. |
| `properties_boond_id_num` | `src_boond_opportunity_id` | `Nullable(Float64)` | oui | Identifiant du besoin dans Boond. Référence documentaire : raw.opportunities.id ; intégrité temporelle à contrôler hors staging. |
| `properties_statut_boond` | `src_boond_state_id` | `String` | non | Code d'étape du besoin dans Boond. Référence documentaire : raw.dictionaries.setting.state.opportunity ; intégrité temporelle à contrôler hors staging. |
| `properties_provenance_boond` | `src_boond_origin_type_id` | `String` | non | Code d'origine du besoin dans Boond. |
| `properties_creation_dans_boond` | `src_boond_created_at` | `Nullable(DateTime64(3,'UTC'))` | oui | Date de création du besoin dans Boond. |
| `properties_date_de_fermeture_boond` | `src_boond_closing_at` | `Nullable(DateTime64(3,'UTC'))` | oui | Date de closing du besoin dans Boond. |
| `properties_hubspot_owner_id` | `src_hubspot_owner_id` | `String` | non | Propriétaire HubSpot du deal. |
| `archived` | `src_is_archived` | `Bool` | non | Deal archivé dans HubSpot. |
| `updatedAt` | `src_updated_at` | `DateTime64(3,'UTC')` | non | Dernière modification dans HubSpot. |

**Colonnes techniques ajoutées** : les 7 colonnes ST, toutes décrites enA.2. **Extraction SQL de présentation à coder** (liste complète ci-dessous, ST calculé dans CTE technique selon01 ; aucune extraction JSON métier) :

```sql
SELECT
    `id` AS src_id,
    `properties_dealname` AS src_deal_name,
    `properties_pipeline` AS src_pipeline_id,
    `properties_dealstage` AS src_stage_id,
    `properties_hs_is_closed` AS src_is_closed,
    `properties_amount` AS src_amount,
    CAST(`properties_createdate` AS Nullable(DateTime64(3,'UTC'))) AS src_created_at,
    CAST(`properties_closedate` AS Nullable(DateTime64(3,'UTC'))) AS src_closed_at,
    `properties_boond_id_num` AS src_boond_opportunity_id,
    `properties_statut_boond` AS src_boond_state_id,
    `properties_provenance_boond` AS src_boond_origin_type_id,
    CAST(`properties_creation_dans_boond` AS Nullable(DateTime64(3,'UTC'))) AS src_boond_created_at,
    CAST(`properties_date_de_fermeture_boond` AS Nullable(DateTime64(3,'UTC'))) AS src_boond_closing_at,
    `properties_hubspot_owner_id` AS src_hubspot_owner_id,
    `archived` AS src_is_archived,
    CAST(`updatedAt` AS DateTime64(3,'UTC')) AS src_updated_at
FROM {{ source('hubspot', 'deals') }}
```

<a id="stg_ref_sales_targets"></a>

### stg_ref_sales_targets

- **Couche/finalité** : staging technique, Objectifs mensuels de l'équipe commerciale, repris du tableur de la VP Sales. Reprise de toutes les 4 colonnes, sans sélection métier.
- **Objet futur** : `dbt/models/staging/reference/stg_ref_sales_targets.sql`, YAML `_models.yml` du même dossier ; relation `stg_reference.stg_ref_sales_targets` ; source `{{ source('case_reference', 'sales_targets') }}` déclarée dans `_sources.yml`.
- **Grain** : une observation changée de contenu ou présence par identité/capture complète. Identité source : `month`, `segment`, `indicator` ; source_version_key unique, ST non NULL. Grain historique distinct du dernier état.
- **Historique/calcul** : capture complète ; comparer chaque identité à la dernière capture COMPLÈTE autorisée par source_capture_keys. Insérer changement, réapparition ou absence observée, sans règle métier. Même contenu après un état différent=>nouvelle capture ; lecture échouée/incomplète=>pas de marqueur de disparition validé. Cette source ne possède ni archived ni updatedAt ; ne pas inventer ces colonnes, la lecture complète est requise.
- **Physique** : incremental append/MergeTree, ORDER BY(src_month_date, src_segment, src_indicator, capture_at, source_version_key), sans partitionnement/TTL en v0.1 ; anti-jointure source_version_key sous is_incremental(), full_refresh=false,on_schema_change=fail,unique_key='source_version_key',inserts_only non activé. Le volume observé ne justifie pas de partitionnement supplémentaire sans mesure.
- **Rafraîchissement** : manuel ; complétude du lot vérifiée, aucun SLA automatique pour ce case D29. Source() seule en amont, lecture this pour anti-jointure ; aucune jointure métier.
- **Tests** : contrat ST, colonnes source exhaustives, source_version_key unique, clé candidate CDC sans conflit (ou identité unique par capture nonCDC), suppression conservée, relecture sans doublons, reprise/cible vide/arrivée hors fenêtre ; erreurs bloquent capture/publication.

| Colonne physique source | Colonne staging | Type final | NULL permis | Description / provenance / contraintes |
|---|---|---|---|---|
| `month` | `src_month_date` | `Date` | non | Premier jour du mois visé. |
| `segment` | `src_segment` | `String` | non | Équipe : SMB, LA (Large Accounts) ou ES (Espagne). |
| `indicator` | `src_indicator` | `String` | non | Indicateur visé : `mrr_signed`, `pipeline_generated`, `pipeline_weighted`, `demos`. |
| `target` | `src_target` | `Float64` | non | Valeur cible du mois (euros pour les montants, nombre pour les démos). |

**Colonnes techniques ajoutées** : les 7 colonnes ST, toutes décrites enA.2. **Extraction SQL de présentation à coder** (liste complète ci-dessous, ST calculé dans CTE technique selon01 ; aucune extraction JSON métier) :

```sql
SELECT
    `month` AS src_month_date,
    `segment` AS src_segment,
    `indicator` AS src_indicator,
    `target` AS src_target
FROM {{ source('case_reference', 'sales_targets') }}
```

<a id="stg_ref_stage_probabilities"></a>

### stg_ref_stage_probabilities

- **Couche/finalité** : staging technique, Probabilité de signature par étape du besoin et par équipe, proposée par le cabinet externe. Reprise de toutes les 3 colonnes, sans sélection métier.
- **Objet futur** : `dbt/models/staging/reference/stg_ref_stage_probabilities.sql`, YAML `_models.yml` du même dossier ; relation `stg_reference.stg_ref_stage_probabilities` ; source `{{ source('case_reference', 'stage_probabilities') }}` déclarée dans `_sources.yml`.
- **Grain** : une observation changée de contenu ou présence par identité/capture complète. Identité source : `state_id`, `segment` ; source_version_key unique, ST non NULL. Grain historique distinct du dernier état.
- **Historique/calcul** : capture complète ; comparer chaque identité à la dernière capture COMPLÈTE autorisée par source_capture_keys. Insérer changement, réapparition ou absence observée, sans règle métier. Même contenu après un état différent=>nouvelle capture ; lecture échouée/incomplète=>pas de marqueur de disparition validé. Cette source ne possède ni archived ni updatedAt ; ne pas inventer ces colonnes, la lecture complète est requise.
- **Physique** : incremental append/MergeTree, ORDER BY(src_state_id, src_segment, capture_at, source_version_key), sans partitionnement/TTL en v0.1 ; anti-jointure source_version_key sous is_incremental(), full_refresh=false,on_schema_change=fail,unique_key='source_version_key',inserts_only non activé. Le volume observé ne justifie pas de partitionnement supplémentaire sans mesure.
- **Rafraîchissement** : manuel ; complétude du lot vérifiée, aucun SLA automatique pour ce case D29. Source() seule en amont, lecture this pour anti-jointure ; aucune jointure métier.
- **Tests** : contrat ST, colonnes source exhaustives, source_version_key unique, clé candidate CDC sans conflit (ou identité unique par capture nonCDC), suppression conservée, relecture sans doublons, reprise/cible vide/arrivée hors fenêtre ; erreurs bloquent capture/publication.

| Colonne physique source | Colonne staging | Type final | NULL permis | Description / provenance / contraintes |
|---|---|---|---|---|
| `state_id` | `src_state_id` | `Int64` | non | Code de l'étape du besoin. Référence documentaire : raw.dictionaries.setting.state.opportunity ; intégrité temporelle à contrôler hors staging. |
| `segment` | `src_segment` | `String` | non | Équipe : SMB, LA ou ES. |
| `probability` | `src_probability` | `Float64` | non | Probabilité de signature, entre 0 et 1. |

**Colonnes techniques ajoutées** : les 7 colonnes ST, toutes décrites enA.2. **Extraction SQL de présentation à coder** (liste complète ci-dessous, ST calculé dans CTE technique selon01 ; aucune extraction JSON métier) :

```sql
SELECT
    `state_id` AS src_state_id,
    `segment` AS src_segment,
    `probability` AS src_probability
FROM {{ source('case_reference', 'stage_probabilities') }}
```

## C. Catalogue du socle : dimensions, intermédiaires et faits

**Première version de spécification, non implémentée.** Les décisions de ce chat sont prioritaires sur les annotations plus anciennes de la proposition. Les statuts bloqués ne constituent pas des calculs exécutés ni des définitions résolues.

### Contrat de lecture commun aux 36 modèles

- `H(...)` désigne SHA256 hexadécimal d’un tuple typé, ordonné et sérialisé sans ambiguïté ; NULL reste distinct de chaîne vide/0. Les conventions exactes de préimage/domaines/types/NULL sont celles de 01 §4.2 bis, qui prévaut ; hexadécimal minuscule et JSON de composants chaîne. Les mêmes conventions s’appliquent à tous les modèles.
- Les 16 intermédiaires et 11 dimensions sont des tables append de recompositions complètes, identifiées par un `model_run_id` GLOBAL commun. Les 9 faits sont des vues de projections explicites sur ces révisions ; aucune vue ne recalcule un ancien run avec des dimensions du run courant.
- Toute jointure dérivée inclut `model_run_id` et, pour une dimension, sa clé de version ; une jointure sur le seul id métier multiplierait les versions. Les périodes sont `[valid_from_at,valid_to_at)` ; NULL en fin signifie pas de fin observée, pas une date métier infinie certifiée.
- Toutes les dates d’instant sont stockées en UTC. Mois/clôtures et horizons calendaires utilisent Europe/Paris ; une clôture est la limite juste avant le minuit local du premier jour du mois suivant. Une version publiée exactement à cette borne appartient au mois suivant.
- Montants canoniques `Decimal(38,4)`, conversion depuis représentation chaîne de la source, contrôle de validité/dépassement ; ne pas répéter quantité×prix si le montant de ligne est déjà total. Les ratios restent NULL pour dénominateur nul/inconnu. Le formatage monétaire à deux décimales appartient à la restitution ; aucune succession d’arrondis intermédiaires.
- Toutes les listes de colonnes ci-dessous sont FINIES ; les projections dbt SQL et descriptions YAML doivent les énumérer une à une. Aucun wildcard n’est autorisé. Les colonnes de traçabilité font partie du contrat documenté.
- `calculation_status` vaut ready/partial/blocked/not_applicable ; `status_reason` conserve une cause stable. Un résultat nécessaire mais non prouvé reste NULL, jamais 0 par défaut. Les tests indiqués sont à créer et exécuter pendant l’implémentation, pas exécutés dans cette phase. Mapping vers contrat public DTR : ready→available ; partial→partial ; blocked→blocked_definition si règle manque ou blocked_evidence si preuve manque ; not_applicable inchangé ; non_mature et not_observable proviennent des flags dédiés, pas d’un statut global écrasant toutes les mesures.
- Sources documentaires : `00_conventions.md`, `clean_intent/architecture_modele_proposition.md` (fiches et cardinalités), inventaire staging et modèle source `docs/model/model.json`. Les décisions utilisateur de ce chat fixent les nouvelles orientations de calendrier, maturité, issues et activité ; la formule technique max(horizon_at) par mois/type est une proposition de calcul explicite, pas une décision métier supplémentaire ; les preuves de données restent séparées dans la spécification transverse.


## Dimensions partagées — 11 modèles


<a id="dim_date"></a>

### `dim_date`

**Grain métier :** Jour civil du calendrier Europe/Paris. **Grain physique :** `(model_run_id, record_key)`. **Clé du grain :** `date_key` identifie le jour ; `record_key=H(calendar_date)` respecte son type String.

**Amont exact :** `{{ ref('stg_boond_opportunities') }}`, `{{ ref('stg_boond_deliveries') }}`, `{{ ref('stg_ref_sales_targets') }}`. **Destination :** `dtm_common.dim_date`, fichier `dbt/models/marts/common/dim_date.sql` ; descriptions YAML dans `dbt/models/marts/common/_models.yml`.

| Colonne | Type ClickHouse | Nullable | Origine, formule, contraintes |
|---|---|---|---|
| `model_run_id` | `String` | Non | Empreinte SHA256 commune de la recomposition : manifeste des entrées figées, code, référentiels et paramètres ; fournie par orchestration, identique dans tout le DAG. |
| `record_key` | `String` | Non | Identité String H(tuple du grain décrit, domaine/version explicite), sans model_run_id ; égale la clé de grain lorsque cette dernière est déjà hashée. dim_date utilise H(calendar_date), jamais date_key UInt32 brut. |
| `record_version_key` | `String` | Non | H(model_run_id,record_key) ; unicité physique de la révision du modèle. |
| `row_hash` | `String` | Non | H(tuple ordonné de toutes les colonnes métier de la fiche, NULL et types préservés) ; exclut les métadonnées de calcul. |
| `calculated_at` | `DateTime64(3,'UTC')` | Non | Instant de calcul du lot ; fixe pour un même model_run_id, jamais utilisé comme événement métier. |
| `rule_version` | `String` | Non | Empreinte immuable du code et des règles appliquées ; dérivée du manifeste du lot. |
| `input_cutoff_at` | `DateTime64(3,'UTC')` | Non | Date limite de connaissance de la recomposition ; les entrées exactes sont figées par le manifeste, pas par ce timestamp seul. |
| `source_published_at` | `Nullable(DateTime64(3,'UTC'))` | Oui | Maximum de publication CDC des versions contribuant à la ligne ; NULL pour un référentiel exclusivement généré. Les entrées de règles non fournies proviennent du futur dbt/config/case_rules.yml fusionné dans vars, sans seed ou source implicite. Ce maximum ne remplace aucune date métier. |
| `source_version_keys` | `Array(String)` | Non | Clés des versions sources contributrices, triées et sans répétition ; union des lignages amont. Liste vide pour une ligne exclusivement générée. |
| `date_key` | `UInt32` | Non | YYYYMMDD de calendar_date ; clé de date UInt32. record_key=H(calendar_date), String. |
| `calendar_date` | `Date` | Non | Jour civil généré. |
| `day_started_at` | `DateTime64(3,'UTC')` | Non | Minuit Europe/Paris converti en UTC ; tient compte des changements d’heure. |
| `next_day_started_at` | `DateTime64(3,'UTC')` | Non | Minuit local suivant converti en UTC ; intervalle [jour,jour suivant). |
| `week_started_date` | `Date` | Non | Lundi de la semaine ISO. |
| `iso_year` | `UInt16` | Non | Année ISO de la semaine. |
| `iso_week` | `UInt8` | Non | Semaine ISO 1–53. |
| `month_date` | `Date` | Non | Premier jour du mois civil. |
| `month_end_date` | `Date` | Non | Dernier jour du mois civil. |
| `next_month_started_at` | `DateTime64(3,'UTC')` | Non | Premier jour du mois suivant à minuit Paris, converti UTC ; borne exclusive de clôture. |
| `year` | `UInt16` | Non | Année civile. |
| `quarter` | `UInt8` | Non | Trimestre 1–4. |
| `day_of_week` | `UInt8` | Non | Lundi=1 … dimanche=7. |
| `is_week_end` | `Bool` | Non | day_of_week dans 6/7 ; descriptif, aucune exclusion des durées. |
| `is_month_end` | `Bool` | Non | calendar_date=month_end_date. |

**Transformation spécifiée :**

1. Début calendrier = jour précédant le début du mois de la plus ancienne date de création/activation documentée disponible. Fin = max(date Paris du cutoff, dernière fin de mois d’objectif) + max_horizon_days (défaut technique90). Les bornes sont explicites dans le manifeste ; aucune fin contractuelle2099 ne prolonge ce calendrier. Cette extension technique couvre mois/cohortes/clôture précédente sans étendre la couverture des données.
2. Bornes initiale/finale inscrites au manifeste ; source manquante : borne technique explicite, jamais profondeur historique prétendue.
3. Aucun calendrier ouvré ni jour férié n’est introduit.

**Jointures / cardinalités :** Aucune jointure de données par jour pour générer les dates ; un seul calendrier par model_run_id.

**Physique, histoire et reprise :** recomposition complète de l’histoire disponible pour le manifeste, table incrémentale `append`, `MergeTree`, `unique_key=record_version_key`, `on_schema_change=fail`, `full_refresh=false`, `inserts_only` non défini, anti-jointure sur `(model_run_id,record_key)`, `ORDER BY (model_run_id,calendar_date)`. Toutes les versions des anciens runs sont conservées ; partition_by non défini, aucune TTL détaillée sans décision ; query_settings join_use_nulls=1. Avant anti-jointure comparer row_hash des clés/run présentes : divergence bloque reprise. Même run rejoué = aucune ligne ajoutée ; reprise d’un run partiel complète les clés manquantes. Aucun prédicat de date maximal sur les données dérivées. Exécution manuelle D29, sans SLA de production ; production à chaque run explicitement lancé, rafraîchissement des datasets après validation/publication seulement.

**Tests / acceptation :** unicité et non-NULL des clés physiques, hash conforme, un seul payload pour une clé/run ; Unique(model_run_id,date_key) et continuité sans trou ; date_key↔calendar_date bijective. Vérifier février bissextile et jours de 23/25 heures autour des changements d’heure Paris. Échec de grain, cardinalité ou incohérence temporelle : ERROR, publication bloquée ; valeur descriptive non mappée : WARN et statut explicite, sauf si le KPI dépend du mapping.

**Limites / dépendances :** Aucune décision métier supplémentaire créée ; les limites de couverture et de source restent visibles.


<a id="dim_country"></a>

### `dim_country`

**Grain métier :** Code pays source normalisé de présentation, avec mapping vers pays reconnu si fourni. **Grain physique :** `(model_run_id, record_key)`. **Clé du grain :** `country_key` ; `record_key` en est l’alias.

**Amont exact :** `{{ ref('stg_boond_companies') }}`, `{{ ref('stg_boond_agencies') }}`. **Destination :** `dtm_common.dim_country`, fichier `dbt/models/marts/common/dim_country.sql` ; descriptions YAML dans `dbt/models/marts/common/_models.yml`.

| Colonne | Type ClickHouse | Nullable | Origine, formule, contraintes |
|---|---|---|---|
| `model_run_id` | `String` | Non | Empreinte SHA256 commune de la recomposition : manifeste des entrées figées, code, référentiels et paramètres ; fournie par orchestration, identique dans tout le DAG. |
| `record_key` | `String` | Non | Identité String H(tuple du grain décrit, domaine/version explicite), sans model_run_id ; égale la clé de grain lorsque cette dernière est déjà hashée. dim_date utilise H(calendar_date), jamais date_key UInt32 brut. |
| `record_version_key` | `String` | Non | H(model_run_id,record_key) ; unicité physique de la révision du modèle. |
| `row_hash` | `String` | Non | H(tuple ordonné de toutes les colonnes métier de la fiche, NULL et types préservés) ; exclut les métadonnées de calcul. |
| `calculated_at` | `DateTime64(3,'UTC')` | Non | Instant de calcul du lot ; fixe pour un même model_run_id, jamais utilisé comme événement métier. |
| `rule_version` | `String` | Non | Empreinte immuable du code et des règles appliquées ; dérivée du manifeste du lot. |
| `input_cutoff_at` | `DateTime64(3,'UTC')` | Non | Date limite de connaissance de la recomposition ; les entrées exactes sont figées par le manifeste, pas par ce timestamp seul. |
| `source_published_at` | `Nullable(DateTime64(3,'UTC'))` | Oui | Maximum de publication CDC des versions contribuant à la ligne ; NULL pour un référentiel exclusivement généré. Les entrées de règles non fournies proviennent du futur dbt/config/case_rules.yml fusionné dans vars, sans seed ou source implicite. Ce maximum ne remplace aucune date métier. |
| `source_version_keys` | `Array(String)` | Non | Clés des versions sources contributrices, triées et sans répétition ; union des lignages amont. Liste vide pour une ligne exclusivement générée. |
| `country_key` | `String` | Non | H(source_country_code normalisé trim/upper) ; un seul membre par code source normalisé, reconnu ou inconnu. |
| `country_code` | `Nullable(String)` | Oui | Code normalisé explicitement mappé ; NULL pour vide/non reconnu. |
| `source_country_code` | `String` | Non | Valeur source normalisée trim/upper ; le brut exact reste préservé en staging. |
| `country_name` | `Nullable(String)` | Oui | Libellé du mapping fourni avec le case ; NULL sans correspondance. |
| `mapping_status` | `String` | Non | mapped / blank / unmapped ; pas de déduction équipe depuis le pays. |

**Transformation spécifiée :**

1. Regrouper les codes companies et agencies par valeur source normalisée trim/upper AVANT production de la clé, pour éviter FR/fr en deux membres de même clé.
2. Normalisation de présentation trim/upper ; ne pas inventer un code ISO sur la seule forme de la chaîne ; liste de correspondances technique versionnée dans le manifeste.

**Jointures / cardinalités :** Jointure companies/agencies → pays N:1 par valeur source normalisée et même model_run_id ; doublon de mapping = erreur.

**Physique, histoire et reprise :** recomposition complète de l’histoire disponible pour le manifeste, table incrémentale `append`, `MergeTree`, `unique_key=record_version_key`, `on_schema_change=fail`, `full_refresh=false`, `inserts_only` non défini, anti-jointure sur `(model_run_id,record_key)`, `ORDER BY (model_run_id,country_key)`. Toutes les versions des anciens runs sont conservées ; partition_by non défini, aucune TTL détaillée sans décision ; query_settings join_use_nulls=1. Avant anti-jointure comparer row_hash des clés/run présentes : divergence bloque reprise. Même run rejoué = aucune ligne ajoutée ; reprise d’un run partiel complète les clés manquantes. Aucun prédicat de date maximal sur les données dérivées. Exécution manuelle D29, sans SLA de production ; production à chaque run explicitement lancé, rafraîchissement des datasets après validation/publication seulement.

**Tests / acceptation :** unicité et non-NULL des clés physiques, hash conforme, un seul payload pour une clé/run ; Unicité des valeurs source et clés par run ; mapping non ambigu. Une valeur pays inconnue reste NULL et ne produit jamais ES comme équipe. Échec de grain, cardinalité ou incohérence temporelle : ERROR, publication bloquée ; valeur descriptive non mappée : WARN et statut explicite, sauf si le KPI dépend du mapping.

**Limites / dépendances :** Aucune décision métier supplémentaire créée ; les limites de couverture et de source restent visibles.


<a id="dim_company"></a>

### `dim_company`

**Grain métier :** Société × version source observée. **Grain physique :** `(model_run_id, record_key)`. **Clé du grain :** `company_version_key` ; `record_key` en est l’alias.

**Amont exact :** `{{ ref('stg_boond_companies') }}`, `{{ ref('stg_boond_poles') }}`, `{{ ref('dim_country') }}`. **Destination :** `dtm_common.dim_company`, fichier `dbt/models/marts/common/dim_company.sql` ; descriptions YAML dans `dbt/models/marts/common/_models.yml`.

| Colonne | Type ClickHouse | Nullable | Origine, formule, contraintes |
|---|---|---|---|
| `model_run_id` | `String` | Non | Empreinte SHA256 commune de la recomposition : manifeste des entrées figées, code, référentiels et paramètres ; fournie par orchestration, identique dans tout le DAG. |
| `record_key` | `String` | Non | Identité String H(tuple du grain décrit, domaine/version explicite), sans model_run_id ; égale la clé de grain lorsque cette dernière est déjà hashée. dim_date utilise H(calendar_date), jamais date_key UInt32 brut. |
| `record_version_key` | `String` | Non | H(model_run_id,record_key) ; unicité physique de la révision du modèle. |
| `row_hash` | `String` | Non | H(tuple ordonné de toutes les colonnes métier de la fiche, NULL et types préservés) ; exclut les métadonnées de calcul. |
| `calculated_at` | `DateTime64(3,'UTC')` | Non | Instant de calcul du lot ; fixe pour un même model_run_id, jamais utilisé comme événement métier. |
| `rule_version` | `String` | Non | Empreinte immuable du code et des règles appliquées ; dérivée du manifeste du lot. |
| `input_cutoff_at` | `DateTime64(3,'UTC')` | Non | Date limite de connaissance de la recomposition ; les entrées exactes sont figées par le manifeste, pas par ce timestamp seul. |
| `source_published_at` | `Nullable(DateTime64(3,'UTC'))` | Oui | Maximum de publication CDC des versions contribuant à la ligne ; NULL pour un référentiel exclusivement généré. Les entrées de règles non fournies proviennent du futur dbt/config/case_rules.yml fusionné dans vars, sans seed ou source implicite. Ce maximum ne remplace aucune date métier. |
| `source_version_keys` | `Array(String)` | Non | Clés des versions sources contributrices, triées et sans répétition ; union des lignages amont. Liste vide pour une ligne exclusivement générée. |
| `company_key` | `String` | Non | H(tenant_id,company_id) ; identité stable. |
| `company_version_key` | `String` | Non | H(company_key,valid_from_at) ; version temporelle, sans model_run_id. |
| `tenant_id` | `String` | Non | src_tenant_id. |
| `company_id` | `Int64` | Non | Identifiant source conservé. |
| `valid_from_at` | `DateTime64(3,'UTC')` | Non | src_published_at inclus, sans antidatation à la création. |
| `valid_to_at` | `Nullable(DateTime64(3,'UTC'))` | Oui | Publication suivante exclue ; NULL en l’absence de suivante. |
| `is_source_deleted` | `Bool` | Non | Dernière valeur src_is_deleted de cette version ; suppression technique, pas issue métier. |
| `company_name` | `String` | Non | src_name ; chaîne source conservée. |
| `company_state_id` | `Nullable(Int64)` | Oui | src_state_id ; ne définit pas l’activité des abonnements. |
| `source_country_code` | `String` | Non | src_country. |
| `country_key` | `Nullable(String)` | Oui | Clé dim_country, même run ; NULL si absence de mapping. |
| `staff` | `Nullable(Int64)` | Oui | src_staff ; pas de tranche d’effectif inventée. |
| `pole_id` | `Nullable(Int64)` | Oui | src_pole_id. |
| `pole_label` | `Nullable(String)` | Oui | src_name de stg_boond_poles dans la version temporelle correspondante. |
| `main_manager_id` | `Nullable(Int64)` | Oui | src_main_manager_id conservé à titre de contexte. |
| `agency_id` | `Nullable(Int64)` | Oui | src_agency_id ; aucune équipe déduite. |
| `created_at` | `Nullable(DateTime64(3,'UTC'))` | Oui | src_created_at, distinct de valid_from_at. |

**Transformation spécifiée :**

1. Ordonner toutes les versions par tenant/id/publication ; un conflit de timestamp bloque le run.
2. Construire les périodes avant toute exclusion des suppressions.
3. Scinder la période société aux bornes de pôle si son libellé change ; version_key utilise chaque borne finale.
4. Conserver les lacunes de référence : pole_label et country_key restent NULL, sans éliminer la société.

**Jointures / cardinalités :** Société→pôle temporel N:0..1, pays N:0..1 ; ajouter aux bornes société celles du pôle, puis join sur tenant/id et [valid_from,valid_to), join_use_nulls=1.

**Physique, histoire et reprise :** recomposition complète de l’histoire disponible pour le manifeste, table incrémentale `append`, `MergeTree`, `unique_key=record_version_key`, `on_schema_change=fail`, `full_refresh=false`, `inserts_only` non défini, anti-jointure sur `(model_run_id,record_key)`, `ORDER BY (model_run_id,tenant_id,company_id,valid_from_at)`. Toutes les versions des anciens runs sont conservées ; partition_by non défini, aucune TTL détaillée sans décision ; query_settings join_use_nulls=1. Avant anti-jointure comparer row_hash des clés/run présentes : divergence bloque reprise. Même run rejoué = aucune ligne ajoutée ; reprise d’un run partiel complète les clés manquantes. Aucun prédicat de date maximal sur les données dérivées. Exécution manuelle D29, sans SLA de production ; production à chaque run explicitement lancé, rafraîchissement des datasets après validation/publication seulement.

**Tests / acceptation :** unicité et non-NULL des clés physiques, hash conforme, un seul payload pour une clé/run ; Périodes positives non chevauchantes par société ; unicité clé de version. Aucun fan-out après enrichissement pôle/pays ; somme de durées des tranches égale la période initiale. Échec de grain, cardinalité ou incohérence temporelle : ERROR, publication bloquée ; valeur descriptive non mappée : WARN et statut explicite, sauf si le KPI dépend du mapping.

**Limites / dépendances :** Aucune décision métier supplémentaire créée ; les limites de couverture et de source restent visibles.


<a id="dim_employee"></a>

### `dim_employee`

**Grain métier :** Collaborateur × version observée. **Grain physique :** `(model_run_id, record_key)`. **Clé du grain :** `employee_version_key` ; `record_key` en est l’alias.

**Amont exact :** `{{ ref('stg_boond_resources') }}`. **Destination :** `dtm_common.dim_employee`, fichier `dbt/models/marts/common/dim_employee.sql` ; descriptions YAML dans `dbt/models/marts/common/_models.yml`.

| Colonne | Type ClickHouse | Nullable | Origine, formule, contraintes |
|---|---|---|---|
| `model_run_id` | `String` | Non | Empreinte SHA256 commune de la recomposition : manifeste des entrées figées, code, référentiels et paramètres ; fournie par orchestration, identique dans tout le DAG. |
| `record_key` | `String` | Non | Identité String H(tuple du grain décrit, domaine/version explicite), sans model_run_id ; égale la clé de grain lorsque cette dernière est déjà hashée. dim_date utilise H(calendar_date), jamais date_key UInt32 brut. |
| `record_version_key` | `String` | Non | H(model_run_id,record_key) ; unicité physique de la révision du modèle. |
| `row_hash` | `String` | Non | H(tuple ordonné de toutes les colonnes métier de la fiche, NULL et types préservés) ; exclut les métadonnées de calcul. |
| `calculated_at` | `DateTime64(3,'UTC')` | Non | Instant de calcul du lot ; fixe pour un même model_run_id, jamais utilisé comme événement métier. |
| `rule_version` | `String` | Non | Empreinte immuable du code et des règles appliquées ; dérivée du manifeste du lot. |
| `input_cutoff_at` | `DateTime64(3,'UTC')` | Non | Date limite de connaissance de la recomposition ; les entrées exactes sont figées par le manifeste, pas par ce timestamp seul. |
| `source_published_at` | `Nullable(DateTime64(3,'UTC'))` | Oui | Maximum de publication CDC des versions contribuant à la ligne ; NULL pour un référentiel exclusivement généré. Les entrées de règles non fournies proviennent du futur dbt/config/case_rules.yml fusionné dans vars, sans seed ou source implicite. Ce maximum ne remplace aucune date métier. |
| `source_version_keys` | `Array(String)` | Non | Clés des versions sources contributrices, triées et sans répétition ; union des lignages amont. Liste vide pour une ligne exclusivement générée. |
| `employee_key` | `String` | Non | H(tenant_id,employee_id) ; identité stable. |
| `employee_version_key` | `String` | Non | H(employee_key,valid_from_at) ; version temporelle, sans model_run_id. |
| `tenant_id` | `String` | Non | src_tenant_id. |
| `employee_id` | `Int64` | Non | Identifiant source conservé. |
| `valid_from_at` | `DateTime64(3,'UTC')` | Non | src_published_at inclus, sans antidatation à la création. |
| `valid_to_at` | `Nullable(DateTime64(3,'UTC'))` | Oui | Publication suivante exclue ; NULL en l’absence de suivante. |
| `is_source_deleted` | `Bool` | Non | Dernière valeur src_is_deleted de cette version ; suppression technique, pas issue métier. |
| `employee_display_name` | `String` | Non | Assemblage de présentation trim(src_first_name,src_last_name), sans utiliser email comme identité. |
| `first_name` | `String` | Non | src_first_name. |
| `last_name` | `String` | Non | src_last_name. |
| `employee_title` | `String` | Non | src_title. |
| `employee_state_id` | `Nullable(Int64)` | Oui | src_state_id. |
| `agency_id` | `Nullable(Int64)` | Oui | src_agency_id. |
| `is_comparison_eligible` | `Nullable(Bool)` | Oui | NULL jusqu’à définition du périmètre individuel et identification des comptes techniques. |
| `eligibility_status` | `String` | Non | not_decided pour la comparaison individuelle ; descriptive pour l’identité. |

**Transformation spécifiée :**

1. Construire les versions temporelles source, suppressions incluses.
2. Aucune équipe figée dans cette dimension ; l’appartenance historique appartient à int_team_membership_periods.
3. Ne pas déduire robot ou vendeur éligible d’un nom ou d’un titre.

**Jointures / cardinalités :** Pas de jointure métier ; aucune multiplication par les appartenances.

**Physique, histoire et reprise :** recomposition complète de l’histoire disponible pour le manifeste, table incrémentale `append`, `MergeTree`, `unique_key=record_version_key`, `on_schema_change=fail`, `full_refresh=false`, `inserts_only` non défini, anti-jointure sur `(model_run_id,record_key)`, `ORDER BY (model_run_id,tenant_id,employee_id,valid_from_at)`. Toutes les versions des anciens runs sont conservées ; partition_by non défini, aucune TTL détaillée sans décision ; query_settings join_use_nulls=1. Avant anti-jointure comparer row_hash des clés/run présentes : divergence bloque reprise. Même run rejoué = aucune ligne ajoutée ; reprise d’un run partiel complète les clés manquantes. Aucun prédicat de date maximal sur les données dérivées. Exécution manuelle D29, sans SLA de production ; production à chaque run explicitement lancé, rafraîchissement des datasets après validation/publication seulement.

**Tests / acceptation :** unicité et non-NULL des clés physiques, hash conforme, un seul payload pour une clé/run ; Périodes non chevauchantes et clés uniques. Changement d’équipe sans nouvelle version de ressource ne réécrit pas cette dimension. Échec de grain, cardinalité ou incohérence temporelle : ERROR, publication bloquée ; valeur descriptive non mappée : WARN et statut explicite, sauf si le KPI dépend du mapping.

**Limites / dépendances :** QC-14 : comparaison individuelle et traitement des comptes techniques ; is_comparison_eligible=NULL.


<a id="dim_team"></a>

### `dim_team`

**Règle finale v0.2 :** D23 :12→LA,13→SMB,15=KAM connue sans cible ; sales_segment=NULL pour KAM, is_sales_team=false pour comparaisons de cibles. Les cibles ES ne créent pas de BU ES fictive. team_key résolu ne dépend pas de sales_segment.

**Grain métier :** Business unit × version observée, mapping Sales séparé. **Grain physique :** `(model_run_id, record_key)`. **Clé du grain :** `team_version_key` ; `record_key` en est l’alias.

**Amont exact :** `{{ ref('stg_boond_businessunits') }}`, `{{ ref('stg_ref_sales_targets') }}`. **Destination :** `dtm_common.dim_team`, fichier `dbt/models/marts/common/dim_team.sql` ; descriptions YAML dans `dbt/models/marts/common/_models.yml`.

| Colonne | Type ClickHouse | Nullable | Origine, formule, contraintes |
|---|---|---|---|
| `model_run_id` | `String` | Non | Empreinte SHA256 commune de la recomposition : manifeste des entrées figées, code, référentiels et paramètres ; fournie par orchestration, identique dans tout le DAG. |
| `record_key` | `String` | Non | Identité String H(tuple du grain décrit, domaine/version explicite), sans model_run_id ; égale la clé de grain lorsque cette dernière est déjà hashée. dim_date utilise H(calendar_date), jamais date_key UInt32 brut. |
| `record_version_key` | `String` | Non | H(model_run_id,record_key) ; unicité physique de la révision du modèle. |
| `row_hash` | `String` | Non | H(tuple ordonné de toutes les colonnes métier de la fiche, NULL et types préservés) ; exclut les métadonnées de calcul. |
| `calculated_at` | `DateTime64(3,'UTC')` | Non | Instant de calcul du lot ; fixe pour un même model_run_id, jamais utilisé comme événement métier. |
| `rule_version` | `String` | Non | Empreinte immuable du code et des règles appliquées ; dérivée du manifeste du lot. |
| `input_cutoff_at` | `DateTime64(3,'UTC')` | Non | Date limite de connaissance de la recomposition ; les entrées exactes sont figées par le manifeste, pas par ce timestamp seul. |
| `source_published_at` | `Nullable(DateTime64(3,'UTC'))` | Oui | Maximum de publication CDC des versions contribuant à la ligne ; NULL pour un référentiel exclusivement généré. Les entrées de règles non fournies proviennent du futur dbt/config/case_rules.yml fusionné dans vars, sans seed ou source implicite. Ce maximum ne remplace aucune date métier. |
| `source_version_keys` | `Array(String)` | Non | Clés des versions sources contributrices, triées et sans répétition ; union des lignages amont. Liste vide pour une ligne exclusivement générée. |
| `team_key` | `String` | Non | H(tenant_id,team_id) ; identité stable. |
| `team_version_key` | `String` | Non | H(team_key,valid_from_at) ; version temporelle, sans model_run_id. |
| `tenant_id` | `String` | Non | src_tenant_id. |
| `team_id` | `Int64` | Non | Identifiant source conservé. |
| `valid_from_at` | `DateTime64(3,'UTC')` | Non | src_published_at inclus, sans antidatation à la création. |
| `valid_to_at` | `Nullable(DateTime64(3,'UTC'))` | Oui | Publication suivante exclue ; NULL en l’absence de suivante. |
| `is_source_deleted` | `Bool` | Non | Dernière valeur src_is_deleted de cette version ; suppression technique, pas issue métier. |
| `team_name` | `String` | Non | src_name de businessunit. |
| `sales_segment` | `Nullable(String)` | Oui | SMB / LA / ES uniquement si correspondance businessunit→segment explicitement fournie. |
| `mapping_status` | `String` | Non | mapped / unmapped / ambiguous ; pas de rapprochement approximatif du nom. |
| `is_sales_team` | `Nullable(Bool)` | Oui | Vrai si mapping validé vers SMB/LA/ES ; NULL si pas de mapping. |

**Transformation spécifiée :**

1. Construire les versions de businessunits.
2. Rapprocher les codes objectifs à un mapping métier versionné tenant/businessunit/segment ; faute de mapping, conserver la businessunit avec sales_segment=NULL.
3. Ne pas prendre agence, pays ou pôle comme équipe.

**Jointures / cardinalités :** Mapping attendu N:0..1 pour une version d’équipe et un segment ; contrôler l’inverse compatible avec chaque objectif.

**Physique, histoire et reprise :** recomposition complète de l’histoire disponible pour le manifeste, table incrémentale `append`, `MergeTree`, `unique_key=record_version_key`, `on_schema_change=fail`, `full_refresh=false`, `inserts_only` non défini, anti-jointure sur `(model_run_id,record_key)`, `ORDER BY (model_run_id,tenant_id,team_id,valid_from_at)`. Toutes les versions des anciens runs sont conservées ; partition_by non défini, aucune TTL détaillée sans décision ; query_settings join_use_nulls=1. Avant anti-jointure comparer row_hash des clés/run présentes : divergence bloque reprise. Même run rejoué = aucune ligne ajoutée ; reprise d’un run partiel complète les clés manquantes. Aucun prédicat de date maximal sur les données dérivées. Exécution manuelle D29, sans SLA de production ; production à chaque run explicitement lancé, rafraîchissement des datasets après validation/publication seulement.

**Tests / acceptation :** unicité et non-NULL des clés physiques, hash conforme, un seul payload pour une clé/run ; Unicité version ; pas deux segments actifs pour une équipe au même instant. Mapping absent reste visible et bloque les comparaisons par équipe, pas l’historique brut. Échec de grain, cardinalité ou incohérence temporelle : ERROR, publication bloquée ; valeur descriptive non mappée : WARN et statut explicite, sauf si le KPI dépend du mapping.

**Limites / dépendances :** QC-05 : mapping historique équipes Sales non fourni ; les faits conservent responsable et statut sans attribution inventée.


<a id="dim_stage"></a>

### `dim_stage`

**Règle finale v0.2 :** D30 classe0,20–26,28,30–35 ouverts ;1/14 gagnés ;13/27 perdus ;3/9 abandonnés ;2/7 nonqualifiés ;10/19 ou code inconnu unclassified/unknown. Préserver les versions/libellés réellement observables, sans transformer un ancien état en étape moderne. outcome_category utilise le domaine existant, mapping_status=case_rule pour les règles décidées, unclassified pour10/19. Aucune exclusion du dénominateur.

**Grain métier :** Tenant × code du dictionnaire français × intervalle de version utile. **Grain physique :** `(model_run_id, record_key)`. **Clé du grain :** `stage_version_key` ; `record_key` en est l’alias.

**Amont exact :** `{{ ref('stg_boond_dictionaries') }}`. **Destination :** `dtm_common.dim_stage`, fichier `dbt/models/marts/common/dim_stage.sql` ; descriptions YAML dans `dbt/models/marts/common/_models.yml`.

| Colonne | Type ClickHouse | Nullable | Origine, formule, contraintes |
|---|---|---|---|
| `model_run_id` | `String` | Non | Empreinte SHA256 commune de la recomposition : manifeste des entrées figées, code, référentiels et paramètres ; fournie par orchestration, identique dans tout le DAG. |
| `record_key` | `String` | Non | Identité String H(tuple du grain décrit, domaine/version explicite), sans model_run_id ; égale la clé de grain lorsque cette dernière est déjà hashée. dim_date utilise H(calendar_date), jamais date_key UInt32 brut. |
| `record_version_key` | `String` | Non | H(model_run_id,record_key) ; unicité physique de la révision du modèle. |
| `row_hash` | `String` | Non | H(tuple ordonné de toutes les colonnes métier de la fiche, NULL et types préservés) ; exclut les métadonnées de calcul. |
| `calculated_at` | `DateTime64(3,'UTC')` | Non | Instant de calcul du lot ; fixe pour un même model_run_id, jamais utilisé comme événement métier. |
| `rule_version` | `String` | Non | Empreinte immuable du code et des règles appliquées ; dérivée du manifeste du lot. |
| `input_cutoff_at` | `DateTime64(3,'UTC')` | Non | Date limite de connaissance de la recomposition ; les entrées exactes sont figées par le manifeste, pas par ce timestamp seul. |
| `source_published_at` | `Nullable(DateTime64(3,'UTC'))` | Oui | Maximum de publication CDC des versions contribuant à la ligne ; NULL pour un référentiel exclusivement généré. Les entrées de règles non fournies proviennent du futur dbt/config/case_rules.yml fusionné dans vars, sans seed ou source implicite. Ce maximum ne remplace aucune date métier. |
| `source_version_keys` | `Array(String)` | Non | Clés des versions sources contributrices, triées et sans répétition ; union des lignages amont. Liste vide pour une ligne exclusivement générée. |
| `stage_key` | `String` | Non | H(tenant_id,stage_id) ; identité stable du code. |
| `stage_version_key` | `String` | Non | H(stage_key,language,valid_from_at). |
| `tenant_id` | `String` | Non | src_tenant_id. |
| `stage_id` | `Int64` | Non | JSON.id du tableau src_setting_state_opportunity_json. |
| `stage_label` | `String` | Non | JSON.value, libellé source. |
| `language` | `String` | Non | fr retenu pour la restitution ; autres langues préservées dans le staging. |
| `valid_from_at` | `DateTime64(3,'UTC')` | Non | Publication de la version dictionnaire contenant le code, incluse. |
| `valid_to_at` | `Nullable(DateTime64(3,'UTC'))` | Oui | Publication dictionnaire suivante exclue, même si le code disparaît alors. |
| `is_source_json_present` | `Bool` | Non | Champ JSON source non NULL ; absence ne devient pas tableau vide connu. |
| `is_source_json_valid` | `Bool` | Non | JSON syntaxiquement valide et de forme tableau ; faux/absence bloque les mesures dépendantes. |
| `is_source_deleted` | `Bool` | Non | Suppression de la version dictionnaire ; aucun code courant recréé après sa suppression. |
| `documented_active` | `Nullable(Bool)` | Oui | JSON.active ; propriété documentaire « en cours », distincte de l’éligibilité aux KPI. |
| `is_enabled_in_source` | `Nullable(Bool)` | Oui | JSON.isEnabled ; un code désactivé dans l’interface reste dans l’histoire. |
| `documented_weighting_percent` | `Nullable(Int64)` | Oui | JSON.weighting, descriptif ; aucune seconde pondération. |
| `state_reasons_json` | `Nullable(String)` | Oui | JSON.reason sérialisé, conservé sans en faire un KPI. |
| `outcome_category` | `Nullable(String)` | Oui | won pour 1/14 ; lost pour 13 ; abandoned pour 3 ; unqualified pour 2 ; open pour 20 ; autres codes selon mapping explicite versionné. |
| `is_open` | `Nullable(Bool)` | Oui | Dérivé du mapping analytique outcome_category, pas de isEnabled. |
| `mapping_status` | `String` | Non | mapped ou missing_stage_rule ; les anciens codes non classés restent inconnus. |

**Transformation spécifiée :**

1. Lire les versions françaises ; calculer présence/validité AVANT parsing. JSONExtractArrayRaw attend une String non Nullable : utiliser ifNull(colonne_source, tableau_vide_JSON) uniquement comme adaptation technique, tout en préservant is_source_json_present=false pour NULL. Le contenu source exact reste au staging. Déplier seulement JSON de forme tableau valide ; conserver id et value. Une absence ou erreur ne certifie pas un dictionnaire vide : qualité du run et couverture de cette tranche restent inconnues, y compris si aucune ligne de code n’est produite.
2. Calculer la borne suivante du dictionnaire avant dépliage pour fermer aussi les codes absents de la version suivante.
3. Un doublon tenant/langue/publication/code ou JSON malformé bloque publication ; aucun fallback multi-langues implicite.
4. Les codes ne sont pas des rangs ; parcours/ordre dans dim_followup_definition. Correspondance source vérifiée du case : Démo24, Qualification22, Découverte23, Proposition21, Projet validé25, Shortlist26, Closing28, Nurturing20. case_rules.demo_stage_ids=[24] ; cette liste ne fixe pas un parcours obligatoire.
5. Les autres états ouverts doivent être inscrits explicitement dans le mapping de phase ; le drapeau source fournit une preuve documentaire, pas une validation implicite.

**Jointures / cardinalités :** Chaque objet→code courant à sa date attend N:0..1 sur tenant/code, même run et intervalle ; aucun join sur toutes les langues.

**Physique, histoire et reprise :** recomposition complète de l’histoire disponible pour le manifeste, table incrémentale `append`, `MergeTree`, `unique_key=record_version_key`, `on_schema_change=fail`, `full_refresh=false`, `inserts_only` non défini, anti-jointure sur `(model_run_id,record_key)`, `ORDER BY (model_run_id,tenant_id,stage_id,valid_from_at)`. Toutes les versions des anciens runs sont conservées ; partition_by non défini, aucune TTL détaillée sans décision ; query_settings join_use_nulls=1. Avant anti-jointure comparer row_hash des clés/run présentes : divergence bloque reprise. Même run rejoué = aucune ligne ajoutée ; reprise d’un run partiel complète les clés manquantes. Aucun prédicat de date maximal sur les données dérivées. Exécution manuelle D29, sans SLA de production ; production à chaque run explicitement lancé, rafraîchissement des datasets après validation/publication seulement.

**Tests / acceptation :** unicité et non-NULL des clés physiques, hash conforme, un seul payload pour une clé/run ; Unicité clés et codes par période ; non-chevauchement, suppression/absence de code bien bornée. Un code inconnu ne supprime pas un fait et reste identifiable par son id source. Échec de grain, cardinalité ou incohérence temporelle : ERROR, publication bloquée ; valeur descriptive non mappée : WARN et statut explicite, sauf si le KPI dépend du mapping.

**Limites / dépendances :** règles fixées par D16–D30 ; conserver les données non observables/invalides et les indisponibilités de preuve D13/D14/D28. Aucun arbitrage supplémentaire demandé.


<a id="dim_sale_type"></a>

### `dim_sale_type`

**Règle finale v0.2 :** D22 : commercial=4/7 ; formation2 et autres types hors comparaisons commerciales, tous conservés en historique.

**Grain métier :** Tenant × code du dictionnaire français × intervalle de version utile. **Grain physique :** `(model_run_id, record_key)`. **Clé du grain :** `sale_type_version_key` ; `record_key` en est l’alias.

**Amont exact :** `{{ ref('stg_boond_dictionaries') }}`. **Destination :** `dtm_common.dim_sale_type`, fichier `dbt/models/marts/common/dim_sale_type.sql` ; descriptions YAML dans `dbt/models/marts/common/_models.yml`.

| Colonne | Type ClickHouse | Nullable | Origine, formule, contraintes |
|---|---|---|---|
| `model_run_id` | `String` | Non | Empreinte SHA256 commune de la recomposition : manifeste des entrées figées, code, référentiels et paramètres ; fournie par orchestration, identique dans tout le DAG. |
| `record_key` | `String` | Non | Identité String H(tuple du grain décrit, domaine/version explicite), sans model_run_id ; égale la clé de grain lorsque cette dernière est déjà hashée. dim_date utilise H(calendar_date), jamais date_key UInt32 brut. |
| `record_version_key` | `String` | Non | H(model_run_id,record_key) ; unicité physique de la révision du modèle. |
| `row_hash` | `String` | Non | H(tuple ordonné de toutes les colonnes métier de la fiche, NULL et types préservés) ; exclut les métadonnées de calcul. |
| `calculated_at` | `DateTime64(3,'UTC')` | Non | Instant de calcul du lot ; fixe pour un même model_run_id, jamais utilisé comme événement métier. |
| `rule_version` | `String` | Non | Empreinte immuable du code et des règles appliquées ; dérivée du manifeste du lot. |
| `input_cutoff_at` | `DateTime64(3,'UTC')` | Non | Date limite de connaissance de la recomposition ; les entrées exactes sont figées par le manifeste, pas par ce timestamp seul. |
| `source_published_at` | `Nullable(DateTime64(3,'UTC'))` | Oui | Maximum de publication CDC des versions contribuant à la ligne ; NULL pour un référentiel exclusivement généré. Les entrées de règles non fournies proviennent du futur dbt/config/case_rules.yml fusionné dans vars, sans seed ou source implicite. Ce maximum ne remplace aucune date métier. |
| `source_version_keys` | `Array(String)` | Non | Clés des versions sources contributrices, triées et sans répétition ; union des lignages amont. Liste vide pour une ligne exclusivement générée. |
| `sale_type_key` | `String` | Non | H(tenant_id,sale_type_id) ; identité stable du code. |
| `sale_type_version_key` | `String` | Non | H(sale_type_key,language,valid_from_at). |
| `tenant_id` | `String` | Non | src_tenant_id. |
| `sale_type_id` | `Int64` | Non | JSON.id du tableau src_setting_type_of_project_json. |
| `sale_type_label` | `String` | Non | JSON.value, libellé source. |
| `language` | `String` | Non | fr retenu pour la restitution ; autres langues préservées dans le staging. |
| `valid_from_at` | `DateTime64(3,'UTC')` | Non | Publication de la version dictionnaire contenant le code, incluse. |
| `valid_to_at` | `Nullable(DateTime64(3,'UTC'))` | Oui | Publication dictionnaire suivante exclue, même si le code disparaît alors. |
| `is_source_json_present` | `Bool` | Non | Champ JSON source non NULL ; absence ne devient pas tableau vide connu. |
| `is_source_json_valid` | `Bool` | Non | JSON syntaxiquement valide et de forme tableau ; faux/absence bloque les mesures dépendantes. |
| `is_source_deleted` | `Bool` | Non | Suppression de la version dictionnaire ; aucun code courant recréé après sa suppression. |
| `sale_type_code` | `String` | Non | new_sale pour 4 ; upsell pour 7 ; training pour 2 ; other pour tout autre code. |
| `is_commercial_scope` | `Nullable(Bool)` | Oui | true pour4/7, false pour2 et autres types hors périmètre commercial D22 ; tous restent conservés en staging/histoire. |
| `is_objective_population_compatible` | `Nullable(Bool)` | Oui | NULL tant que chaque cible n’a pas de population métier compatible. |

**Transformation spécifiée :**

1. Lire les versions françaises ; calculer présence/validité AVANT parsing. JSONExtractArrayRaw attend une String non Nullable : utiliser ifNull(colonne_source, tableau_vide_JSON) uniquement comme adaptation technique, tout en préservant is_source_json_present=false pour NULL. Le contenu source exact reste au staging. Déplier seulement JSON de forme tableau valide ; conserver id et value. Une absence ou erreur ne certifie pas un dictionnaire vide : qualité du run et couverture de cette tranche restent inconnues, y compris si aucune ligne de code n’est produite.
2. Calculer la borne suivante du dictionnaire avant dépliage pour fermer aussi les codes absents de la version suivante.
3. Un doublon tenant/langue/publication/code ou JSON malformé bloque publication ; aucun fallback multi-langues implicite.
4. Conserver tous les types et leur histoire ; aucune exclusion globale du staging ou des faits.
5. Distinguer type commercial de l’opportunité et composante financière New/Upsell.

**Jointures / cardinalités :** Chaque objet→code courant à sa date attend N:0..1 sur tenant/code, même run et intervalle ; aucun join sur toutes les langues.

**Physique, histoire et reprise :** recomposition complète de l’histoire disponible pour le manifeste, table incrémentale `append`, `MergeTree`, `unique_key=record_version_key`, `on_schema_change=fail`, `full_refresh=false`, `inserts_only` non défini, anti-jointure sur `(model_run_id,record_key)`, `ORDER BY (model_run_id,tenant_id,sale_type_id,valid_from_at)`. Toutes les versions des anciens runs sont conservées ; partition_by non défini, aucune TTL détaillée sans décision ; query_settings join_use_nulls=1. Avant anti-jointure comparer row_hash des clés/run présentes : divergence bloque reprise. Même run rejoué = aucune ligne ajoutée ; reprise d’un run partiel complète les clés manquantes. Aucun prédicat de date maximal sur les données dérivées. Exécution manuelle D29, sans SLA de production ; production à chaque run explicitement lancé, rafraîchissement des datasets après validation/publication seulement.

**Tests / acceptation :** unicité et non-NULL des clés physiques, hash conforme, un seul payload pour une clé/run ; Unicité clés et codes par période ; non-chevauchement, suppression/absence de code bien bornée. Un code inconnu ne supprime pas un fait et reste identifiable par son id source. Échec de grain, cardinalité ou incohérence temporelle : ERROR, publication bloquée ; valeur descriptive non mappée : WARN et statut explicite, sauf si le KPI dépend du mapping.

**Limites / dépendances :** QC-01 : périmètre formation/autres et compatibilité des objectifs ouverts.


<a id="dim_channel"></a>

### `dim_channel`

**Règle finale v0.2 :** D24 : origine opportunity.origin.typeOf à création seulement ; inbound_group=Inbound pour1/2/3,Outbound pour4/5,Other pour6–11 ; is_inbound=false pour les codes connus hors1/2/3 et NULL si non mappé. Ne pas remplacer une origine d’entrée inconnue par contact/HubSpot ou dernière source.

**Grain métier :** Tenant × code du dictionnaire français × intervalle de version utile. **Grain physique :** `(model_run_id, record_key)`. **Clé du grain :** `channel_version_key` ; `record_key` en est l’alias.

**Amont exact :** `{{ ref('stg_boond_dictionaries') }}`. **Destination :** `dtm_common.dim_channel`, fichier `dbt/models/marts/common/dim_channel.sql` ; descriptions YAML dans `dbt/models/marts/common/_models.yml`.

| Colonne | Type ClickHouse | Nullable | Origine, formule, contraintes |
|---|---|---|---|
| `model_run_id` | `String` | Non | Empreinte SHA256 commune de la recomposition : manifeste des entrées figées, code, référentiels et paramètres ; fournie par orchestration, identique dans tout le DAG. |
| `record_key` | `String` | Non | Identité String H(tuple du grain décrit, domaine/version explicite), sans model_run_id ; égale la clé de grain lorsque cette dernière est déjà hashée. dim_date utilise H(calendar_date), jamais date_key UInt32 brut. |
| `record_version_key` | `String` | Non | H(model_run_id,record_key) ; unicité physique de la révision du modèle. |
| `row_hash` | `String` | Non | H(tuple ordonné de toutes les colonnes métier de la fiche, NULL et types préservés) ; exclut les métadonnées de calcul. |
| `calculated_at` | `DateTime64(3,'UTC')` | Non | Instant de calcul du lot ; fixe pour un même model_run_id, jamais utilisé comme événement métier. |
| `rule_version` | `String` | Non | Empreinte immuable du code et des règles appliquées ; dérivée du manifeste du lot. |
| `input_cutoff_at` | `DateTime64(3,'UTC')` | Non | Date limite de connaissance de la recomposition ; les entrées exactes sont figées par le manifeste, pas par ce timestamp seul. |
| `source_published_at` | `Nullable(DateTime64(3,'UTC'))` | Oui | Maximum de publication CDC des versions contribuant à la ligne ; NULL pour un référentiel exclusivement généré. Les entrées de règles non fournies proviennent du futur dbt/config/case_rules.yml fusionné dans vars, sans seed ou source implicite. Ce maximum ne remplace aucune date métier. |
| `source_version_keys` | `Array(String)` | Non | Clés des versions sources contributrices, triées et sans répétition ; union des lignages amont. Liste vide pour une ligne exclusivement générée. |
| `channel_key` | `String` | Non | H(tenant_id,channel_id) ; identité stable du code. |
| `channel_version_key` | `String` | Non | H(channel_key,language,valid_from_at). |
| `tenant_id` | `String` | Non | src_tenant_id. |
| `channel_id` | `Int64` | Non | JSON.id du tableau src_setting_origin_json. |
| `channel_label` | `String` | Non | JSON.value, libellé source. |
| `language` | `String` | Non | fr retenu pour la restitution ; autres langues préservées dans le staging. |
| `valid_from_at` | `DateTime64(3,'UTC')` | Non | Publication de la version dictionnaire contenant le code, incluse. |
| `valid_to_at` | `Nullable(DateTime64(3,'UTC'))` | Oui | Publication dictionnaire suivante exclue, même si le code disparaît alors. |
| `is_source_json_present` | `Bool` | Non | Champ JSON source non NULL ; absence ne devient pas tableau vide connu. |
| `is_source_json_valid` | `Bool` | Non | JSON syntaxiquement valide et de forme tableau ; faux/absence bloque les mesures dépendantes. |
| `is_source_deleted` | `Bool` | Non | Suppression de la version dictionnaire ; aucun code courant recréé après sa suppression. |
| `channel_code` | `String` | Non | Code technique boond_origin_<id>, sans fusion de catégories non arbitrée. |
| `is_inbound` | `Nullable(Bool)` | Oui | NULL avant liste explicite des codes Inbound. |
| `inbound_group` | `Nullable(String)` | Oui | Inbound pour1/2/3 ; Outbound pour4/5 ; Other pour6–11 ; valeur non mappée NULL, selon D24. |
| `mapping_status` | `String` | Non | mapped selon D24 pour les codes connus ; unmapped si valeur absente/inconnue, sans fallback contact/HubSpot. |
| `attribution_rule` | `Nullable(String)` | Oui | opportunity_origin_at_creation selon D24 ; NULL seulement si origine à création non observable. |

**Transformation spécifiée :**

1. Lire les versions françaises ; calculer présence/validité AVANT parsing. JSONExtractArrayRaw attend une String non Nullable : utiliser ifNull(colonne_source, tableau_vide_JSON) uniquement comme adaptation technique, tout en préservant is_source_json_present=false pour NULL. Le contenu source exact reste au staging. Déplier seulement JSON de forme tableau valide ; conserver id et value. Une absence ou erreur ne certifie pas un dictionnaire vide : qualité du run et couverture de cette tranche restent inconnues, y compris si aucune ligne de code n’est produite.
2. Calculer la borne suivante du dictionnaire avant dépliage pour fermer aussi les codes absents de la version suivante.
3. Un doublon tenant/langue/publication/code ou JSON malformé bloque publication ; aucun fallback multi-langues implicite.
4. Publier les origines Boond comme référentiel descriptif, sans attribuer silencieusement leur code au KPI acquisition.
5. Les UTM/dernières sources HubSpot restent dans les intermédiaires de traçabilité, sans écraser le canal fixé à l’entrée.

**Jointures / cardinalités :** Chaque objet→code courant à sa date attend N:0..1 sur tenant/code, même run et intervalle ; aucun join sur toutes les langues.

**Physique, histoire et reprise :** recomposition complète de l’histoire disponible pour le manifeste, table incrémentale `append`, `MergeTree`, `unique_key=record_version_key`, `on_schema_change=fail`, `full_refresh=false`, `inserts_only` non défini, anti-jointure sur `(model_run_id,record_key)`, `ORDER BY (model_run_id,tenant_id,channel_id,valid_from_at)`. Toutes les versions des anciens runs sont conservées ; partition_by non défini, aucune TTL détaillée sans décision ; query_settings join_use_nulls=1. Avant anti-jointure comparer row_hash des clés/run présentes : divergence bloque reprise. Même run rejoué = aucune ligne ajoutée ; reprise d’un run partiel complète les clés manquantes. Aucun prédicat de date maximal sur les données dérivées. Exécution manuelle D29, sans SLA de production ; production à chaque run explicitement lancé, rafraîchissement des datasets après validation/publication seulement.

**Tests / acceptation :** unicité et non-NULL des clés physiques, hash conforme, un seul payload pour une clé/run ; Unicité clés et codes par période ; non-chevauchement, suppression/absence de code bien bornée. Un code inconnu ne supprime pas un fait et reste identifiable par son id source. Échec de grain, cardinalité ou incohérence temporelle : ERROR, publication bloquée ; valeur descriptive non mappée : WARN et statut explicite, sauf si le KPI dépend du mapping.

**Limites / dépendances :** D24 choisit origine du besoin à création et regroupements1/2/3 Inbound,4/5 Outbound,6–11 Autres ; origine non observable reste NULL.


<a id="dim_action_type"></a>

### `dim_action_type`

**Grain métier :** Tenant × code du dictionnaire français × intervalle de version utile. **Grain physique :** `(model_run_id, record_key)`. **Clé du grain :** `action_type_version_key` ; `record_key` en est l’alias.

**Amont exact :** `{{ ref('stg_boond_dictionaries') }}`. **Destination :** `dtm_common.dim_action_type`, fichier `dbt/models/marts/common/dim_action_type.sql` ; descriptions YAML dans `dbt/models/marts/common/_models.yml`.

| Colonne | Type ClickHouse | Nullable | Origine, formule, contraintes |
|---|---|---|---|
| `model_run_id` | `String` | Non | Empreinte SHA256 commune de la recomposition : manifeste des entrées figées, code, référentiels et paramètres ; fournie par orchestration, identique dans tout le DAG. |
| `record_key` | `String` | Non | Identité String H(tuple du grain décrit, domaine/version explicite), sans model_run_id ; égale la clé de grain lorsque cette dernière est déjà hashée. dim_date utilise H(calendar_date), jamais date_key UInt32 brut. |
| `record_version_key` | `String` | Non | H(model_run_id,record_key) ; unicité physique de la révision du modèle. |
| `row_hash` | `String` | Non | H(tuple ordonné de toutes les colonnes métier de la fiche, NULL et types préservés) ; exclut les métadonnées de calcul. |
| `calculated_at` | `DateTime64(3,'UTC')` | Non | Instant de calcul du lot ; fixe pour un même model_run_id, jamais utilisé comme événement métier. |
| `rule_version` | `String` | Non | Empreinte immuable du code et des règles appliquées ; dérivée du manifeste du lot. |
| `input_cutoff_at` | `DateTime64(3,'UTC')` | Non | Date limite de connaissance de la recomposition ; les entrées exactes sont figées par le manifeste, pas par ce timestamp seul. |
| `source_published_at` | `Nullable(DateTime64(3,'UTC'))` | Oui | Maximum de publication CDC des versions contribuant à la ligne ; NULL pour un référentiel exclusivement généré. Les entrées de règles non fournies proviennent du futur dbt/config/case_rules.yml fusionné dans vars, sans seed ou source implicite. Ce maximum ne remplace aucune date métier. |
| `source_version_keys` | `Array(String)` | Non | Clés des versions sources contributrices, triées et sans répétition ; union des lignages amont. Liste vide pour une ligne exclusivement générée. |
| `action_type_key` | `String` | Non | H(tenant_id,action_type_id) ; identité stable du code. |
| `action_type_version_key` | `String` | Non | H(action_type_key,language,valid_from_at). |
| `tenant_id` | `String` | Non | src_tenant_id. |
| `action_type_id` | `Int64` | Non | JSON.id du tableau src_setting_action_contact_json. |
| `action_type_label` | `String` | Non | JSON.value, libellé source. |
| `language` | `String` | Non | fr retenu pour la restitution ; autres langues préservées dans le staging. |
| `valid_from_at` | `DateTime64(3,'UTC')` | Non | Publication de la version dictionnaire contenant le code, incluse. |
| `valid_to_at` | `Nullable(DateTime64(3,'UTC'))` | Oui | Publication dictionnaire suivante exclue, même si le code disparaît alors. |
| `is_source_json_present` | `Bool` | Non | Champ JSON source non NULL ; absence ne devient pas tableau vide connu. |
| `is_source_json_valid` | `Bool` | Non | JSON syntaxiquement valide et de forme tableau ; faux/absence bloque les mesures dépendantes. |
| `is_source_deleted` | `Bool` | Non | Suppression de la version dictionnaire ; aucun code courant recréé après sa suppression. |
| `action_kind` | `String` | Non | demo_request pour 25 ; demo_first pour 60 ; demo_additional pour 68 ; cancellation pour 17 ; other sinon. |
| `is_demo_request_type` | `Bool` | Non | action_type_id=25 dans le mapping versionné. |
| `is_demo_type` | `Bool` | Non | action_type_id dans 60/68 selon mapping documentaire. |
| `is_cancellation_type` | `Bool` | Non | action_type_id=17 ; ne prouve pas le rendez-vous annulé auquel il se rapporte. |

**Transformation spécifiée :**

1. Lire les versions françaises ; calculer présence/validité AVANT parsing. JSONExtractArrayRaw attend une String non Nullable : utiliser ifNull(colonne_source, tableau_vide_JSON) uniquement comme adaptation technique, tout en préservant is_source_json_present=false pour NULL. Le contenu source exact reste au staging. Déplier seulement JSON de forme tableau valide ; conserver id et value. Une absence ou erreur ne certifie pas un dictionnaire vide : qualité du run et couverture de cette tranche restent inconnues, y compris si aucune ligne de code n’est produite.
2. Calculer la borne suivante du dictionnaire avant dépliage pour fermer aussi les codes absents de la version suivante.
3. Un doublon tenant/langue/publication/code ou JSON malformé bloque publication ; aucun fallback multi-langues implicite.
4. Le type conserve sa fonction documentaire ; un type démo ne prouve ni tenue, ni unicité de séance, ni lien à un dossier.

**Jointures / cardinalités :** Chaque objet→code courant à sa date attend N:0..1 sur tenant/code, même run et intervalle ; aucun join sur toutes les langues.

**Physique, histoire et reprise :** recomposition complète de l’histoire disponible pour le manifeste, table incrémentale `append`, `MergeTree`, `unique_key=record_version_key`, `on_schema_change=fail`, `full_refresh=false`, `inserts_only` non défini, anti-jointure sur `(model_run_id,record_key)`, `ORDER BY (model_run_id,tenant_id,action_type_id,valid_from_at)`. Toutes les versions des anciens runs sont conservées ; partition_by non défini, aucune TTL détaillée sans décision ; query_settings join_use_nulls=1. Avant anti-jointure comparer row_hash des clés/run présentes : divergence bloque reprise. Même run rejoué = aucune ligne ajoutée ; reprise d’un run partiel complète les clés manquantes. Aucun prédicat de date maximal sur les données dérivées. Exécution manuelle D29, sans SLA de production ; production à chaque run explicitement lancé, rafraîchissement des datasets après validation/publication seulement.

**Tests / acceptation :** unicité et non-NULL des clés physiques, hash conforme, un seul payload pour une clé/run ; Unicité clés et codes par période ; non-chevauchement, suppression/absence de code bien bornée. Un code inconnu ne supprime pas un fait et reste identifiable par son id source. Échec de grain, cardinalité ou incohérence temporelle : ERROR, publication bloquée ; valeur descriptive non mappée : WARN et statut explicite, sauf si le KPI dépend du mapping.

**Limites / dépendances :** Aucune décision métier supplémentaire créée ; les limites de couverture et de source restent visibles.


<a id="dim_followup_definition"></a>

### `dim_followup_definition`

**Règle finale v0.2 :** Définir pour chaque type4/7 les cohortes J30/J60/J90 (IDs cohort_type4_j30_v1,etc.), les jalons funnel_type4_<stage>_v1/funnel_type7_<stage>_v1 et transitions transition_type<type>_<A>_<B>_v1 des couples adjacents D17. Pour cohort_outcome,horizon_days=30/60/90,ancre création. Pour funnel_reach et stage_transition,horizon_days=NULL, borne d’observation explicite ; transition ancrée à première A observable puis première B après A. Pos0 du tunnel est Création, target_stage_id=0 comme identifiant de présentation, pas preuve de Lead observé : label Création, clé de version d’étape NULL, first_reached_at=created_at. Chemin4:[0,22,23,24,21,28,1],chemin7:[0,21,28,1]. is_enabled=true sur ces définitions ; conserver les anciennes règles par rule_version.

**Grain métier :** Définition de population/parcours × type commercial × horizon ou cible × version de règle. **Grain physique :** `(model_run_id, record_key)`. **Clé du grain :** `followup_definition_version_key` ; `record_key` en est l’alias.

**Amont exact :** référentiel généré versionné dans le manifeste. **Destination :** `dtm_common.dim_followup_definition`, fichier `dbt/models/marts/common/dim_followup_definition.sql` ; descriptions YAML dans `dbt/models/marts/common/_models.yml`.

| Colonne | Type ClickHouse | Nullable | Origine, formule, contraintes |
|---|---|---|---|
| `model_run_id` | `String` | Non | Empreinte SHA256 commune de la recomposition : manifeste des entrées figées, code, référentiels et paramètres ; fournie par orchestration, identique dans tout le DAG. |
| `record_key` | `String` | Non | Identité String H(tuple du grain décrit, domaine/version explicite), sans model_run_id ; égale la clé de grain lorsque cette dernière est déjà hashée. dim_date utilise H(calendar_date), jamais date_key UInt32 brut. |
| `record_version_key` | `String` | Non | H(model_run_id,record_key) ; unicité physique de la révision du modèle. |
| `row_hash` | `String` | Non | H(tuple ordonné de toutes les colonnes métier de la fiche, NULL et types préservés) ; exclut les métadonnées de calcul. |
| `calculated_at` | `DateTime64(3,'UTC')` | Non | Instant de calcul du lot ; fixe pour un même model_run_id, jamais utilisé comme événement métier. |
| `rule_version` | `String` | Non | Empreinte immuable du code et des règles appliquées ; dérivée du manifeste du lot. |
| `input_cutoff_at` | `DateTime64(3,'UTC')` | Non | Date limite de connaissance de la recomposition ; les entrées exactes sont figées par le manifeste, pas par ce timestamp seul. |
| `source_published_at` | `Nullable(DateTime64(3,'UTC'))` | Oui | Maximum de publication CDC des versions contribuant à la ligne ; NULL pour un référentiel exclusivement généré. Les entrées de règles non fournies proviennent du futur dbt/config/case_rules.yml fusionné dans vars, sans seed ou source implicite. Ce maximum ne remplace aucune date métier. |
| `source_version_keys` | `Array(String)` | Non | Clés des versions sources contributrices, triées et sans répétition ; union des lignages amont. Liste vide pour une ligne exclusivement générée. |
| `followup_definition_id` | `String` | Non | Identifiant stable de définition configurée. |
| `tenant_id` | `String` | Non | Var source_tenant_id=demo_crm ; codes de parcours rattachés au tenant. |
| `followup_definition_key` | `String` | Non | H(tenant_id,followup_definition_id), identité stable. |
| `followup_definition_version_key` | `String` | Non | H(followup_definition_key,definition_rule_version), version de règle ; record_key en est alias. |
| `definition_rule_version` | `String` | Non | Version du contenu métier de cette définition, distincte de la version de build. |
| `followup_kind` | `String` | Non | cohort_outcome / funnel_reach / stage_transition. |
| `sale_type_id` | `Int64` | Non | Type auquel s’applique la définition ; nouvelles ventes et upsells séparés. |
| `source_stage_id` | `Nullable(Int64)` | Oui | Étape d’ancrage pour une transition ; NULL pour création. |
| `target_stage_id` | `Nullable(Int64)` | Oui | Étape cible ; NULL pour suivi d’issue globale. |
| `horizon_days` | `Nullable(UInt16)` | Oui | 30,60,90 pour cohort_outcome ; horizon explicite pour transition ; NULL pour funnel à date. |
| `funnel_position` | `Nullable(UInt16)` | Oui | Ordre explicite du parcours configuré, jamais ordre numérique des codes. |
| `previous_target_stage_id` | `Nullable(Int64)` | Oui | Étape précédente du parcours configuré ; NULL première étape. |
| `anchor_rule` | `String` | Non | created_at pour cohorte/funnel ; first_admissible_stage_entry pour transition A→B activée selon D17/D18, une première A observable par dossier. |
| `population_rule` | `String` | Non | Population/type explicitement configurés ; aucune définition universelle de lead. |
| `attribution_rule` | `String` | Non | Contexte d’entrée pour cohortes et génération ; convention de transition restant à préciser. |
| `maturity_rule` | `String` | Non | Tous les membres connus tenant/mois/type/définition/horizon ont atteint leur horizon ; calcul avant filtres équipe/canal. |
| `is_enabled` | `Bool` | Non | true pour les définitions4/7 décidées D17/D18 : cohort_outcome,funnel_reach,stage_transition ; false seulement pour une définition non retenue. |
| `definition_status` | `String` | Non | ready / blocked ; explique la règle encore manquante. |

**Transformation spécifiée :**

1. Créer cohort_outcome pour chaque type analysé séparément, horizons 30/60/90 ; création Boond comme ancrage.
2. Déclarer les parcours funnel_reach et stage_transition dans le même référentiel quand ordre/population/transitions sont explicitement fixés.
3. Ne pas transformer les étapes d’une image en transitions obligatoires.

**Jointures / cardinalités :** Chaque opportunité×définition compatible de son type ; pas de produit avec définitions désactivées pour les mesures publiées. Lignes diagnostiques désactivées possibles avec statut blocked.

**Physique, histoire et reprise :** recomposition complète de l’histoire disponible pour le manifeste, table incrémentale `append`, `MergeTree`, `unique_key=record_version_key`, `on_schema_change=fail`, `full_refresh=false`, `inserts_only` non défini, anti-jointure sur `(model_run_id,record_key)`, `ORDER BY (model_run_id,followup_definition_key)`. Toutes les versions des anciens runs sont conservées ; partition_by non défini, aucune TTL détaillée sans décision ; query_settings join_use_nulls=1. Avant anti-jointure comparer row_hash des clés/run présentes : divergence bloque reprise. Même run rejoué = aucune ligne ajoutée ; reprise d’un run partiel complète les clés manquantes. Aucun prédicat de date maximal sur les données dérivées. Exécution manuelle D29, sans SLA de production ; production à chaque run explicitement lancé, rafraîchissement des datasets après validation/publication seulement.

**Tests / acceptation :** unicité et non-NULL des clés physiques, hash conforme, un seul payload pour une clé/run ; Unicité définition versionnée ; pas deux positions dans un parcours pour la même cible. Horizon cohorte dans 30/60/90 ; les définitions désactivées ne contribuent à aucun total. Échec de grain, cardinalité ou incohérence temporelle : ERROR, publication bloquée ; valeur descriptive non mappée : WARN et statut explicite, sauf si le KPI dépend du mapping.

**Limites / dépendances :** règles fixées par D16–D30 ; conserver les données non observables/invalides et les indisponibilités de preuve D13/D14/D28. Aucun arbitrage supplémentaire demandé.


<a id="dim_metric"></a>

### `dim_metric`

**Grain métier :** Un des quatre indicateurs ciblés. **Grain physique :** `(model_run_id, record_key)`. **Clé du grain :** `metric_version_key` ; `record_key` en est l’alias.

**Amont exact :** référentiel généré versionné dans le manifeste. **Destination :** `dtm_common.dim_metric`, fichier `dbt/models/marts/common/dim_metric.sql` ; descriptions YAML dans `dbt/models/marts/common/_models.yml`.

| Colonne | Type ClickHouse | Nullable | Origine, formule, contraintes |
|---|---|---|---|
| `model_run_id` | `String` | Non | Empreinte SHA256 commune de la recomposition : manifeste des entrées figées, code, référentiels et paramètres ; fournie par orchestration, identique dans tout le DAG. |
| `record_key` | `String` | Non | Identité String H(tuple du grain décrit, domaine/version explicite), sans model_run_id ; égale la clé de grain lorsque cette dernière est déjà hashée. dim_date utilise H(calendar_date), jamais date_key UInt32 brut. |
| `record_version_key` | `String` | Non | H(model_run_id,record_key) ; unicité physique de la révision du modèle. |
| `row_hash` | `String` | Non | H(tuple ordonné de toutes les colonnes métier de la fiche, NULL et types préservés) ; exclut les métadonnées de calcul. |
| `calculated_at` | `DateTime64(3,'UTC')` | Non | Instant de calcul du lot ; fixe pour un même model_run_id, jamais utilisé comme événement métier. |
| `rule_version` | `String` | Non | Empreinte immuable du code et des règles appliquées ; dérivée du manifeste du lot. |
| `input_cutoff_at` | `DateTime64(3,'UTC')` | Non | Date limite de connaissance de la recomposition ; les entrées exactes sont figées par le manifeste, pas par ce timestamp seul. |
| `source_published_at` | `Nullable(DateTime64(3,'UTC'))` | Oui | Maximum de publication CDC des versions contribuant à la ligne ; NULL pour un référentiel exclusivement généré. Les entrées de règles non fournies proviennent du futur dbt/config/case_rules.yml fusionné dans vars, sans seed ou source implicite. Ce maximum ne remplace aucune date métier. |
| `source_version_keys` | `Array(String)` | Non | Clés des versions sources contributrices, triées et sans répétition ; union des lignages amont. Liste vide pour une ligne exclusivement générée. |
| `tenant_id` | `String` | Non | Var source_tenant_id=demo_crm pour le contexte de ce jeu. |
| `metric_key` | `String` | Non | H(tenant_id,metric_code), identité stable. |
| `metric_version_key` | `String` | Non | H(metric_key,definition_rule_version), version de définition ; record_key en est alias. |
| `definition_rule_version` | `String` | Non | Empreinte du contenu explicite de définition dans case_rules, sans timestamp de tentative. |
| `metric_code` | `String` | Non | mrr_signed / pipeline_generated / pipeline_weighted / demos. |
| `metric_label` | `String` | Non | MRR signé / Pipeline généré / Pipeline pondéré / Démos réalisées. |
| `value_unit` | `String` | Non | EUR pour les trois cibles monétaires documentées ; count pour demos. Cette unité de cible ne prouve pas celle du réalisé pipeline. |
| `amount_basis` | `String` | Non | recurring_monthly_excluding_tax pour signé ; pipeline_amount_unconfirmed pour pipelines ; not_applicable pour démos. |
| `aggregation_kind` | `String` | Non | monthly_flow pour signé/généré/démos ; month_end_stock pour pondéré. |
| `definition_status` | `String` | Non | blocked_amount_evidence / blocked_amount_unit / blocked_demo_proof selon mesure. |
| `is_team_targeted` | `Bool` | Non | Vrai pour les quatre mesures ; aucun objectif individuel ni portefeuille ajouté. |

**Transformation spécifiée :**

1. Créer exactement les quatre codes présents dans les objectifs ; ne pas créer une mesure par axe de filtre.
2. La description précise stock/flux et l’unité encore non validée ; elle ne rend pas les réalisés disponibles.

**Jointures / cardinalités :** Cible et réalisé→metric N:1, même model_run_id et metric_version_key ; pas de confusion avec une probabilité.

**Physique, histoire et reprise :** recomposition complète de l’histoire disponible pour le manifeste, table incrémentale `append`, `MergeTree`, `unique_key=record_version_key`, `on_schema_change=fail`, `full_refresh=false`, `inserts_only` non défini, anti-jointure sur `(model_run_id,record_key)`, `ORDER BY (model_run_id,metric_code)`. Toutes les versions des anciens runs sont conservées ; partition_by non défini, aucune TTL détaillée sans décision ; query_settings join_use_nulls=1. Avant anti-jointure comparer row_hash des clés/run présentes : divergence bloque reprise. Même run rejoué = aucune ligne ajoutée ; reprise d’un run partiel complète les clés manquantes. Aucun prédicat de date maximal sur les données dérivées. Exécution manuelle D29, sans SLA de production ; production à chaque run explicitement lancé, rafraîchissement des datasets après validation/publication seulement.

**Tests / acceptation :** unicité et non-NULL des clés physiques, hash conforme, un seul payload pour une clé/run ; Quatre codes uniques ; domaines et unités connus. pipeline_weighted est semi-additif dans le temps ; aucun total inter-mois de stocks. Échec de grain, cardinalité ou incohérence temporelle : ERROR, publication bloquée ; valeur descriptive non mappée : WARN et statut explicite, sauf si le KPI dépend du mapping.

**Limites / dépendances :** Aucune décision métier supplémentaire créée ; les limites de couverture et de source restent visibles.


## Intermédiaires — 16 modèles




<a id="int_crm_identity_links"></a>

### `int_crm_identity_links`

**Grain métier :** Lien direct entre deux identités source × intervalle observé. **Grain physique :** (model_run_id,record_key) ; record_key=link_key.

**Amont exact :** `{{ ref('stg_boond_opportunities') }}`, `{{ ref('stg_boond_actions') }}`, `{{ ref('stg_boond_contacts') }}`, `{{ ref('stg_boond_projects') }}`, `{{ ref('stg_hubspot_contacts') }}`, `{{ ref('stg_hubspot_deals') }}`. **Destination :** `dwh_common.int_crm_identity_links`, `dbt/models/intermediate/common/int_crm_identity_links.sql`, YAML `dbt/models/intermediate/common/_models.yml`.

| Colonne | Type ClickHouse | Nullable | Origine, formule, contraintes |
|---|---|---|---|
| `model_run_id` | `String` | Non | Empreinte SHA256 commune de la recomposition : manifeste des entrées figées, code, référentiels et paramètres ; fournie par orchestration, identique dans tout le DAG. |
| `record_key` | `String` | Non | Identité String H(tuple du grain décrit, domaine/version explicite), sans model_run_id ; égale la clé de grain lorsque cette dernière est déjà hashée. dim_date utilise H(calendar_date), jamais date_key UInt32 brut. |
| `record_version_key` | `String` | Non | H(model_run_id,record_key) ; unicité physique de la révision du modèle. |
| `row_hash` | `String` | Non | H(tuple ordonné de toutes les colonnes métier de la fiche, NULL et types préservés) ; exclut les métadonnées de calcul. |
| `calculated_at` | `DateTime64(3,'UTC')` | Non | Instant de calcul du lot ; fixe pour un même model_run_id, jamais utilisé comme événement métier. |
| `rule_version` | `String` | Non | Empreinte immuable du code et des règles appliquées ; dérivée du manifeste du lot. |
| `input_cutoff_at` | `DateTime64(3,'UTC')` | Non | Date limite de connaissance de la recomposition ; les entrées exactes sont figées par le manifeste, pas par ce timestamp seul. |
| `source_published_at` | `Nullable(DateTime64(3,'UTC'))` | Oui | Maximum de publication CDC des versions contribuant à la ligne ; NULL pour un référentiel exclusivement généré. Les entrées de règles non fournies proviennent du futur dbt/config/case_rules.yml fusionné dans vars, sans seed ou source implicite. Ce maximum ne remplace aucune date métier. |
| `source_version_keys` | `Array(String)` | Non | Clés des versions sources contributrices, triées et sans répétition ; union des lignages amont. Liste vide pour une ligne exclusivement générée. |
| `link_key` | `String` | Non | H(tenant_id,source_system,source_object,source_id,target_system,target_object,target_id,valid_from_at). |
| `tenant_id` | `String` | Non | Tenant Boond ; HubSpot associé par var source_tenant_id=demo_crm pour ce jeu mono-tenant seulement. |
| `source_system` | `String` | Non | boond ou hubspot. |
| `source_object` | `String` | Non | opportunity / action / contact / project / deal. |
| `source_id` | `String` | Non | ID exact converti String pour l’union des systèmes. |
| `target_system` | `String` | Non | boond ou hubspot. |
| `target_object` | `String` | Non | Type exact de cible documentée. |
| `target_id` | `Nullable(String)` | Oui | ID exact ; NULL si ID source invalide ou absent. |
| `valid_from_at` | `DateTime64(3,'UTC')` | Non | Publication CDC ou observation de capture HubSpot incluse. |
| `valid_to_at` | `Nullable(DateTime64(3,'UTC'))` | Oui | Version source suivante exclue. |
| `link_method` | `String` | Non | direct_relationship / boond_id_property / unresolved_contact_candidate. |
| `link_status` | `String` | Non | verified_reference / orphan / invalid_id / ambiguous / missing. |
| `is_source_deleted` | `Bool` | Non | Suppression/archivage technique de l’objet source dans cette version. |
| `target_exists_at_reference` | `Nullable(Bool)` | Oui | Vrai/faux après contrôle à la date de référence ; NULL si couverture cible absente. |
| `calculation_status` | `String` | Non | ready / partial / blocked / not_applicable. |
| `status_reason` | `Nullable(String)` | Oui | Cause précise stable ; NULL si aucune dépendance manquante. |

**Transformation spécifiée :**

1. Émettre les relations explicites besoin→société/contact, action→dependsOn(type,id)/société, projet→société/besoin et identifiants Boond HubSpot.
2. Valider les id HubSpot Float64 : non-NULL, fini, entier et dans Int64 ; ne jamais arrondir un identifiant fractionnaire. Les id contact String doivent être parsables sans perte.
3. Action liée à un contact : conserver ce lien, sans joindre tous ses besoins pour produire des liens action→opportunité.
4. Ne pas fabriquer lien upsell→abonnement absent. Calculer les intervalles depuis les versions source ; une relation retirée se ferme à publication suivante.

**Jointures / cardinalités :** Chaque lien vers cible attend N:0..1 après sélection temporelle tenant/id. Plusieurs deals HubSpot d’un besoin restent plusieurs liens descriptifs ; aucune jointure monétaire.

**Physique, histoire et reprise :** table incrémentale append, MergeTree, unique_key=record_version_key, on_schema_change=fail, full_refresh=false, inserts_only non défini, recomposition COMPLETE de l’histoire disponible pour un manifeste immuable, anti-jointure (model_run_id,record_key) ; ORDER BY (model_run_id,tenant_id,source_system,source_object,source_id,valid_from_at). Réexécution du même run = aucune copie ; reprise partielle complète les clés absentes sans changer le payload existant. Nouvelle empreinte d’entrée/code/règle = nouvelle révision entière. Aucune limite à hier ni watermark métier dans ce modèle. Mono-écrivain ; partition_by non défini, aucune TTL détaillée sans décision ; query_settings join_use_nulls=1. Avant anti-jointure, comparer row_hash de toute clé/run déjà présente : divergence sous même identité bloque reprise ; puis compléter clés absentes. Publication après tests de structure ; manque métier connu donne mesureNULL et qualité, pas blocage automatique du run entier. Exécution manuelle et fraîcheur de capture/publiée D29, sans SLA automatique.

**Tests / acceptation :** unicité/non-NULL des clés physiques, row_hash déterministe et un seul payload par clé/run ; Relation directe univoque par rôle/version ; conflit type/id bloquant. Contrôle d’orphelins par rôle ; cette table ne multiplie aucun compteur ou montant commercial. Défaut de grain, jointure ou réconciliation : ERROR et publication bloquée. Manque connu documenté : valeur NULL et statut, WARN si descriptif, KPI indisponible s’il en dépend.

**Limites / dépendances :** QC-02/QC-11 : chaîne démo et effet upsell non démontrés ; link_status conserve le manque.


<a id="int_team_membership_periods"></a>

### `int_team_membership_periods`

**Règle finale v0.2 :** Résoudre la BU unique indépendamment de la présence d’un segment de cible : KAM est une équipe connue consultable. is_sales_attribution_eligible exige LA/SMB quand comparaison à cible, mais l’échec de ce drapeau ne supprime pas la BU connue des faits génériques. ES non résolue reste cible sans réalisé.

**Grain métier :** Collaborateur × businessunit × tranche de présence et de version dimensionnelle. **Grain physique :** (model_run_id,record_key) ; record_key=membership_period_key.

**Amont exact :** `{{ ref('stg_boond_businessunits') }}`, `{{ ref('dim_employee') }}`, `{{ ref('dim_team') }}`. **Destination :** `dwh_common.int_team_membership_periods`, `dbt/models/intermediate/common/int_team_membership_periods.sql`, YAML `dbt/models/intermediate/common/_models.yml`.

| Colonne | Type ClickHouse | Nullable | Origine, formule, contraintes |
|---|---|---|---|
| `model_run_id` | `String` | Non | Empreinte SHA256 commune de la recomposition : manifeste des entrées figées, code, référentiels et paramètres ; fournie par orchestration, identique dans tout le DAG. |
| `record_key` | `String` | Non | Identité String H(tuple du grain décrit, domaine/version explicite), sans model_run_id ; égale la clé de grain lorsque cette dernière est déjà hashée. dim_date utilise H(calendar_date), jamais date_key UInt32 brut. |
| `record_version_key` | `String` | Non | H(model_run_id,record_key) ; unicité physique de la révision du modèle. |
| `row_hash` | `String` | Non | H(tuple ordonné de toutes les colonnes métier de la fiche, NULL et types préservés) ; exclut les métadonnées de calcul. |
| `calculated_at` | `DateTime64(3,'UTC')` | Non | Instant de calcul du lot ; fixe pour un même model_run_id, jamais utilisé comme événement métier. |
| `rule_version` | `String` | Non | Empreinte immuable du code et des règles appliquées ; dérivée du manifeste du lot. |
| `input_cutoff_at` | `DateTime64(3,'UTC')` | Non | Date limite de connaissance de la recomposition ; les entrées exactes sont figées par le manifeste, pas par ce timestamp seul. |
| `source_published_at` | `Nullable(DateTime64(3,'UTC'))` | Oui | Maximum de publication CDC des versions contribuant à la ligne ; NULL pour un référentiel exclusivement généré. Les entrées de règles non fournies proviennent du futur dbt/config/case_rules.yml fusionné dans vars, sans seed ou source implicite. Ce maximum ne remplace aucune date métier. |
| `source_version_keys` | `Array(String)` | Non | Clés des versions sources contributrices, triées et sans répétition ; union des lignages amont. Liste vide pour une ligne exclusivement générée. |
| `membership_period_key` | `String` | Non | H(tenant_id,employee_id,team_id,valid_from_at). |
| `tenant_id` | `String` | Non | src_tenant_id. |
| `employee_id` | `Int64` | Non | id de chaque élément src_included_managers_json. |
| `employee_key` | `String` | Non | Identité dim_employee. |
| `employee_version_key` | `Nullable(String)` | Oui | Version employé sur toute la tranche, NULL si orphelin. |
| `team_id` | `Int64` | Non | src_id de businessunit. |
| `team_key` | `String` | Non | Identité dim_team. |
| `team_version_key` | `Nullable(String)` | Oui | Version dim_team sur toute la tranche. |
| `sales_segment` | `Nullable(String)` | Oui | Segment du mapping équipe, s’il existe. |
| `valid_from_at` | `DateTime64(3,'UTC')` | Non | Maximum des bornes de présence et de versions employé/équipe. |
| `valid_to_at` | `Nullable(DateTime64(3,'UTC'))` | Oui | Minimum des fins correspondantes ; fin exclue. |
| `nb_simultaneous_memberships` | `UInt16` | Non | Nombre d’équipes observées pour cet employé sur la tranche atomique. |
| `membership_status` | `String` | Non | unique / multiple / orphan_employee / unmapped_sales_segment. |
| `is_sales_attribution_eligible` | `Bool` | Non | Une seule appartenance admissible, dimensions connues et segment mappé. |
| `calculation_status` | `String` | Non | ready / partial / blocked / not_applicable. |
| `status_reason` | `Nullable(String)` | Oui | Cause précise stable ; NULL si aucune dépendance manquante. |

**Transformation spécifiée :**

1. Déplier chaque version complète de liste ; conserver un membre une fois par businessunit/version.
2. Former les intervalles avant dépliage pour fermer les membres retirés ; suppression ferme présences, sans attribution rétroactive.
3. Réunir bornes des listes et dimensions ; produire tranches atomiques positives.
4. Conserver appartenances multiples sans choisir une équipe arbitrairement.
5. Fusion du rôle bridge_employee_team_period : clés dimensionnelles ici, aucune bridge supplémentaire.

**Jointures / cardinalités :** Tranche→employé/équipe N:0..1 sur même run/version ; plusieurs appartenances restent relations de consultation, pas jointure multiplicative aux faits.

**Physique, histoire et reprise :** table incrémentale append, MergeTree, unique_key=record_version_key, on_schema_change=fail, full_refresh=false, inserts_only non défini, recomposition COMPLETE de l’histoire disponible pour un manifeste immuable, anti-jointure (model_run_id,record_key) ; ORDER BY (model_run_id,tenant_id,employee_id,valid_from_at,team_id). Réexécution du même run = aucune copie ; reprise partielle complète les clés absentes sans changer le payload existant. Nouvelle empreinte d’entrée/code/règle = nouvelle révision entière. Aucune limite à hier ni watermark métier dans ce modèle. Mono-écrivain ; partition_by non défini, aucune TTL détaillée sans décision ; query_settings join_use_nulls=1. Avant anti-jointure, comparer row_hash de toute clé/run déjà présente : divergence sous même identité bloque reprise ; puis compléter clés absentes. Publication après tests de structure ; manque métier connu donne mesureNULL et qualité, pas blocage automatique du run entier. Exécution manuelle et fraîcheur de capture/publiée D29, sans SLA automatique.

**Tests / acceptation :** unicité/non-NULL des clés physiques, row_hash déterministe et un seul payload par clé/run ; Non-chevauchement par couple employé/équipe et clé unique. Présence JSON initiale réconciliée ; version dimension valide durant toute tranche. Défaut de grain, jointure ou réconciliation : ERROR et publication bloquée. Manque connu documenté : valeur NULL et statut, WARN si descriptif, KPI indisponible s’il en dépend.

**Limites / dépendances :** QC-05/QC-14 : mapping Sales, appartenances multiples et périmètre individuel.


<a id="int_signature_probabilities"></a>

### `int_signature_probabilities`

**Règle finale v0.2 :** D21 : conserver toutes captures et leur valid_from_at/valid_to_at d’OBSERVATION. Dans le run, sélectionner le dernier barème COMPLET autorisé ; lui seul a applicability_status=applicable_recomputed_case. Les autres restent historical_capture_only. Pour le dernier barème,business_valid_from_at=case_history_start_at (minimum des premières publications d’opportunités importées, figé au manifest),business_valid_to_at=case_as_of_boundary_at ; ce sont bornes de RECALCUL et non dates d’effet historiques prouvées. sale_type_id=NULL signifie barème partagé4/7, explicitement défini. Jointure des périodes sur bornes de recalcul/état/segment et type IN[4,7], pas sur capture_at contre date métier ; une seule référence par état/segment/run. Aucun fallback Boond. Valeur absente=NULL.

**Grain métier :** Étape × segment × source de coefficient × version observée. **Grain physique :** (model_run_id,record_key) ; record_key=probability_version_key.

**Amont exact :** `{{ ref('stg_ref_stage_probabilities') }}`, `{{ ref('dim_stage') }}`, `{{ ref('dim_team') }}`. **Destination :** `dwh_pipeline.int_signature_probabilities`, `dbt/models/intermediate/pipeline/int_signature_probabilities.sql`, YAML `dbt/models/intermediate/pipeline/_models.yml`.

| Colonne | Type ClickHouse | Nullable | Origine, formule, contraintes |
|---|---|---|---|
| `model_run_id` | `String` | Non | Empreinte SHA256 commune de la recomposition : manifeste des entrées figées, code, référentiels et paramètres ; fournie par orchestration, identique dans tout le DAG. |
| `record_key` | `String` | Non | Identité String H(tuple du grain décrit, domaine/version explicite), sans model_run_id ; égale la clé de grain lorsque cette dernière est déjà hashée. dim_date utilise H(calendar_date), jamais date_key UInt32 brut. |
| `record_version_key` | `String` | Non | H(model_run_id,record_key) ; unicité physique de la révision du modèle. |
| `row_hash` | `String` | Non | H(tuple ordonné de toutes les colonnes métier de la fiche, NULL et types préservés) ; exclut les métadonnées de calcul. |
| `calculated_at` | `DateTime64(3,'UTC')` | Non | Instant de calcul du lot ; fixe pour un même model_run_id, jamais utilisé comme événement métier. |
| `rule_version` | `String` | Non | Empreinte immuable du code et des règles appliquées ; dérivée du manifeste du lot. |
| `input_cutoff_at` | `DateTime64(3,'UTC')` | Non | Date limite de connaissance de la recomposition ; les entrées exactes sont figées par le manifeste, pas par ce timestamp seul. |
| `source_published_at` | `Nullable(DateTime64(3,'UTC'))` | Oui | Maximum de publication CDC des versions contribuant à la ligne ; NULL pour un référentiel exclusivement généré. Les entrées de règles non fournies proviennent du futur dbt/config/case_rules.yml fusionné dans vars, sans seed ou source implicite. Ce maximum ne remplace aucune date métier. |
| `source_version_keys` | `Array(String)` | Non | Clés des versions sources contributrices, triées et sans répétition ; union des lignages amont. Liste vide pour une ligne exclusivement générée. |
| `probability_version_key` | `String` | Non | H(tenant_id,source_kind,stage_id,sales_segment,valid_from_at,source_version_key). |
| `tenant_id` | `String` | Non | Var source_tenant_id=demo_crm appliquée à ref pour ce jeu ; pas colonne source ajoutée au staging. |
| `stage_id` | `Int64` | Non | src_state_id. |
| `sales_segment` | `String` | Non | src_segment SMB/LA/ES. |
| `probability` | `Nullable(Decimal(18,8))` | Oui | src_probability converti décimal ; domaine [0,1]. |
| `source_kind` | `String` | Non | stage_probability_reference. |
| `valid_from_at` | `DateTime64(3,'UTC')` | Non | Instant de capture ref, pas date d’effet passée. |
| `valid_to_at` | `Nullable(DateTime64(3,'UTC'))` | Oui | Capture suivante exclue. |
| `business_valid_from_at` | `Nullable(DateTime64(3,'UTC'))` | Oui | Début de fenêtre de recalcul D21 (case_history_start_at), jamais présenté comme date d’effet source prouvée ; NULL pour anciennes captures non appliquées. |
| `business_valid_to_at` | `Nullable(DateTime64(3,'UTC'))` | Oui | Borne exclusive de recalcul case_as_of_boundary_at ; NULL pour anciennes captures non appliquées. |
| `sale_type_id` | `Nullable(Int64)` | Oui | NULL signifie barème partagé explicitement entre types4/7 D21, pas portée indéfinie ; les autres types sont exclus de son application. |
| `applicability_status` | `String` | Non | applicable_recomputed_case pour le dernier barème capturé autorisé ; historical_capture_only pour les anciennes captures ; invalid si coefficient hors domaine. |
| `calculation_status` | `String` | Non | ready / partial / blocked / not_applicable. |
| `status_reason` | `Nullable(String)` | Oui | Cause précise stable ; NULL si aucune dépendance manquante. |

**Transformation spécifiée :**

1. Préserver toutes les captures ; D21 choisit explicitement le recalcul du passé au dernier barème complet autorisé, avec provenance de capture inchangée.
2. Contrôler unicité étape/segment par capture et domaine.
3. Préparer coefficients candidats ; pondération par besoin conservée dans ses périodes.
4. Source/portée/historique sont définis D21 ; coefficient valable pour4/7 et période de recalcul. NULL uniquement si coefficient/segment/état non couvert ou valeur invalide.

**Jointures / cardinalités :** Besoin→coefficient N:0..1 sur tenant/étape/segment/type/temps et même run ; ne jamais joindre toutes les équipes d’une étape.

**Physique, histoire et reprise :** table incrémentale append, MergeTree, unique_key=record_version_key, on_schema_change=fail, full_refresh=false, inserts_only non défini, recomposition COMPLETE de l’histoire disponible pour un manifeste immuable, anti-jointure (model_run_id,record_key) ; ORDER BY (model_run_id,tenant_id,sales_segment,stage_id,valid_from_at). Réexécution du même run = aucune copie ; reprise partielle complète les clés absentes sans changer le payload existant. Nouvelle empreinte d’entrée/code/règle = nouvelle révision entière. Aucune limite à hier ni watermark métier dans ce modèle. Mono-écrivain ; partition_by non défini, aucune TTL détaillée sans décision ; query_settings join_use_nulls=1. Avant anti-jointure, comparer row_hash de toute clé/run déjà présente : divergence sous même identité bloque reprise ; puis compléter clés absentes. Publication après tests de structure ; manque métier connu donne mesureNULL et qualité, pas blocage automatique du run entier. Exécution manuelle et fraîcheur de capture/publiée D29, sans SLA automatique.

**Tests / acceptation :** unicité/non-NULL des clés physiques, row_hash déterministe et un seul payload par clé/run ; Probabilité [0,1], clé complète unique et périodes non chevauchantes. Boond et ref ne sont jamais multipliés entre eux. Défaut de grain, jointure ou réconciliation : ERROR et publication bloquée. Manque connu documenté : valeur NULL et statut, WARN si descriptif, KPI indisponible s’il en dépend.

**Limites / dépendances :** règles fixées par D16–D30 ; conserver les données non observables/invalides et les indisponibilités de preuve D13/D14/D28. Aucun arbitrage supplémentaire demandé.


<a id="int_opportunity_stage_visits"></a>

### `int_opportunity_stage_visits`

**Grain métier :** Opportunité × passage continu observé ; retours distincts. **Grain physique :** (model_run_id,record_key) ; record_key=visit_key.

**Amont exact :** `{{ ref('stg_boond_opportunities') }}`. **Destination :** `dwh_pipeline.int_opportunity_stage_visits`, `dbt/models/intermediate/pipeline/int_opportunity_stage_visits.sql`, YAML `dbt/models/intermediate/pipeline/_models.yml`.

| Colonne | Type ClickHouse | Nullable | Origine, formule, contraintes |
|---|---|---|---|
| `model_run_id` | `String` | Non | Empreinte SHA256 commune de la recomposition : manifeste des entrées figées, code, référentiels et paramètres ; fournie par orchestration, identique dans tout le DAG. |
| `record_key` | `String` | Non | Identité String H(tuple du grain décrit, domaine/version explicite), sans model_run_id ; égale la clé de grain lorsque cette dernière est déjà hashée. dim_date utilise H(calendar_date), jamais date_key UInt32 brut. |
| `record_version_key` | `String` | Non | H(model_run_id,record_key) ; unicité physique de la révision du modèle. |
| `row_hash` | `String` | Non | H(tuple ordonné de toutes les colonnes métier de la fiche, NULL et types préservés) ; exclut les métadonnées de calcul. |
| `calculated_at` | `DateTime64(3,'UTC')` | Non | Instant de calcul du lot ; fixe pour un même model_run_id, jamais utilisé comme événement métier. |
| `rule_version` | `String` | Non | Empreinte immuable du code et des règles appliquées ; dérivée du manifeste du lot. |
| `input_cutoff_at` | `DateTime64(3,'UTC')` | Non | Date limite de connaissance de la recomposition ; les entrées exactes sont figées par le manifeste, pas par ce timestamp seul. |
| `source_published_at` | `Nullable(DateTime64(3,'UTC'))` | Oui | Maximum de publication CDC des versions contribuant à la ligne ; NULL pour un référentiel exclusivement généré. Les entrées de règles non fournies proviennent du futur dbt/config/case_rules.yml fusionné dans vars, sans seed ou source implicite. Ce maximum ne remplace aucune date métier. |
| `source_version_keys` | `Array(String)` | Non | Clés des versions sources contributrices, triées et sans répétition ; union des lignages amont. Liste vide pour une ligne exclusivement générée. |
| `tenant_id` | `String` | Non | Identité du tenant src_tenant_id. |
| `opportunity_id` | `Int64` | Non | src_id du besoin Boond. |
| `opportunity_key` | `String` | Non | H(tenant_id,opportunity_id), identité stable intermodèles. |
| `visit_key` | `String` | Non | H(opportunity_key,first_observed_at,first_source_version_key). |
| `stage_id` | `Nullable(Int64)` | Oui | src_state_id du groupe consécutif. |
| `visit_rank` | `UInt32` | Non | Rang chronologique, jamais ordre des codes. |
| `first_observed_at` | `DateTime64(3,'UTC')` | Non | Première publication prouvant présence dans cet état. |
| `last_observed_at` | `DateTime64(3,'UTC')` | Non | Dernière publication du même passage. |
| `entered_at` | `Nullable(DateTime64(3,'UTC'))` | Oui | Entrée datée ou proxy CDC d’une transition observée ; NULL premier état avancé censuré. |
| `exited_at` | `Nullable(DateTime64(3,'UTC'))` | Oui | Transition suivante observée ; NULL en cours/suppression sans sortie métier. |
| `observation_ended_at` | `Nullable(DateTime64(3,'UTC'))` | Oui | Fin technique d’observation, distincte de exited_at. |
| `previous_stage_id` | `Nullable(Int64)` | Oui | État précédent observé hors lacune. |
| `next_stage_id` | `Nullable(Int64)` | Oui | État suivant observé hors lacune. |
| `first_source_version_key` | `String` | Non | Version source initiale du groupe. |
| `last_source_version_key` | `String` | Non | Version source finale du groupe. |
| `event_time_basis` | `String` | Non | cdc_transition_proxy / business_proven / left_censored / observation_only. |
| `is_left_censored` | `Bool` | Non | Début du passage non observable. |
| `is_right_censored` | `Bool` | Non | Sortie admissible non observée. |
| `is_open_visit` | `Bool` | Non | Pas de transition/suppression suivante ; différent d’étape commercialement ouverte. |
| `has_observation_gap` | `Bool` | Non | Lacune ou suppression/réapparition séparant passages. |
| `completed_duration_seconds` | `Nullable(Float64)` | Oui | Différence millisecondes UTC/1000 pour passage terminé avec début admissible ; NULL sinon. |
| `completed_duration_days` | `Nullable(Float64)` | Oui | completed_duration_seconds/86400. |
| `coverage_start_at` | `Nullable(DateTime64(3,'UTC'))` | Oui | Couverture déclarée ; première observation seule ne prouve pas exhaustivité. |
| `coverage_end_at` | `Nullable(DateTime64(3,'UTC'))` | Oui | Fin déclarée ; jamais max(updateDate) futur. |
| `is_history_complete` | `Nullable(Bool)` | Oui | Couverture de fenêtre vérifiée/configurée ; NULL si non établie. |
| `calculation_status` | `String` | Non | ready / partial / blocked / not_applicable. |
| `status_reason` | `Nullable(String)` | Oui | Cause précise stable ; NULL si aucune dépendance manquante. |

**Transformation spécifiée :**

1. Ordonner tenant/id/publication après test de conflits timestamp.
2. Frontière si état change, suppression ou réapparition ; changements de montant/responsable seuls ne créent aucun passage.
3. Premier état avancé : first_observed_at connu, entered_at=NULL ; ne pas antidater à creationDate.
4. Transition observée : date publication sert de proxy déclaré, pas événement métier certifié.
5. Suppression ferme observation_ended_at ; ne génère aucune sortie métier/perte.
6. Retour dans une étape crée un nouveau passage ; durée par passage, sans cumul implicite.

**Pseudocode normatif de la transformation :**

```text
Trier les versions par (tenant_id,opportunity_id,published_at), après rejet des collisions de contenu.
Pour chaque version i :
  has_previous := i > 1
  same_state := comparaison NULL-safe de state_i et state_previous
  boundary := !has_previous OR !same_state OR deleted_i OR deleted_previous
  visit_group := somme cumulative de boundary
Déduire les bornes de groupe sur TOUTES les versions, suppressions comprises.
Émettre les groupes non supprimés ; une suppression ferme leur observation, pas leur sortie commerciale.
entered_at := publication du groupe seulement si transition précédente observable et proxy explicitement marqué ;
              sinon date métier prouvée ; sinon NULL.
exited_at := publication du groupe d'état suivant seulement si transition sans lacune ;
             sinon NULL.
completed_duration := différence UTC seulement si les deux bornes admissibles ; sinon NULL.
Ne jamais identifier l'absence de précédent au seul résultat NULL d'un lag d'état.
```

**Jointures / cardinalités :** Aucune jointure ; fenêtres par tenant/id. Contexte enrichi plus tard sans changer le grain.

**Physique, histoire et reprise :** table incrémentale append, MergeTree, unique_key=record_version_key, on_schema_change=fail, full_refresh=false, inserts_only non défini, recomposition COMPLETE de l’histoire disponible pour un manifeste immuable, anti-jointure (model_run_id,record_key) ; ORDER BY (model_run_id,tenant_id,opportunity_id,first_observed_at). Réexécution du même run = aucune copie ; reprise partielle complète les clés absentes sans changer le payload existant. Nouvelle empreinte d’entrée/code/règle = nouvelle révision entière. Aucune limite à hier ni watermark métier dans ce modèle. Mono-écrivain ; partition_by non défini, aucune TTL détaillée sans décision ; query_settings join_use_nulls=1. Avant anti-jointure, comparer row_hash de toute clé/run déjà présente : divergence sous même identité bloque reprise ; puis compléter clés absentes. Publication après tests de structure ; manque métier connu donne mesureNULL et qualité, pas blocage automatique du run entier. Exécution manuelle et fraîcheur de capture/publiée D29, sans SLA automatique.

**Tests / acceptation :** unicité/non-NULL des clés physiques, row_hash déterministe et un seul payload par clé/run ; A,A,B,A produit trois passages ; changement de responsable seul aucun passage. Durées non négatives ; censure gauche implique durée exacte NULL ; suppression ne produit pas sortie. Défaut de grain, jointure ou réconciliation : ERROR et publication bloquée. Manque connu documenté : valeur NULL et statut, WARN si descriptif, KPI indisponible s’il en dépend.

**Limites / dépendances :** QC-10 dates exactes / couverture manquantes ; proxy CDC explicite.


<a id="int_opportunity_periods"></a>

### `int_opportunity_periods`

**Règle finale v0.2 :** Appliquer D21/D23/D24/D26 : barème recalculé, BU à la date de la période, canal origine figé à création lorsqu’observable, seuil21jours par défaut. KAM reste une BU connue et filtrable ; sans segment de barème, pondération NULL avec missing_probability_for_segment. Le montant brut reste diagnostique tant que sa nature n’est pas confirmée D13.

**Grain métier :** Opportunité × intervalle de contexte stable, scindé aux bornes des versions jointes. **Grain physique :** (model_run_id,record_key) ; record_key=period_key.

**Amont exact :** `{{ ref('stg_boond_opportunities') }}`, `{{ ref('stg_hubspot_contacts') }}`, `{{ ref('stg_hubspot_deals') }}`, `{{ ref('int_opportunity_stage_visits') }}`, `{{ ref('int_crm_identity_links') }}`, `{{ ref('int_team_membership_periods') }}`, `{{ ref('int_signature_probabilities') }}`, `{{ ref('dim_company') }}`, `{{ ref('dim_employee') }}`, `{{ ref('dim_team') }}`, `{{ ref('dim_stage') }}`, `{{ ref('dim_sale_type') }}`, `{{ ref('dim_channel') }}`. **Destination :** `dwh_pipeline.int_opportunity_periods`, `dbt/models/intermediate/pipeline/int_opportunity_periods.sql`, YAML `dbt/models/intermediate/pipeline/_models.yml`.

| Colonne | Type ClickHouse | Nullable | Origine, formule, contraintes |
|---|---|---|---|
| `model_run_id` | `String` | Non | Empreinte SHA256 commune de la recomposition : manifeste des entrées figées, code, référentiels et paramètres ; fournie par orchestration, identique dans tout le DAG. |
| `record_key` | `String` | Non | Identité String H(tuple du grain décrit, domaine/version explicite), sans model_run_id ; égale la clé de grain lorsque cette dernière est déjà hashée. dim_date utilise H(calendar_date), jamais date_key UInt32 brut. |
| `record_version_key` | `String` | Non | H(model_run_id,record_key) ; unicité physique de la révision du modèle. |
| `row_hash` | `String` | Non | H(tuple ordonné de toutes les colonnes métier de la fiche, NULL et types préservés) ; exclut les métadonnées de calcul. |
| `calculated_at` | `DateTime64(3,'UTC')` | Non | Instant de calcul du lot ; fixe pour un même model_run_id, jamais utilisé comme événement métier. |
| `rule_version` | `String` | Non | Empreinte immuable du code et des règles appliquées ; dérivée du manifeste du lot. |
| `input_cutoff_at` | `DateTime64(3,'UTC')` | Non | Date limite de connaissance de la recomposition ; les entrées exactes sont figées par le manifeste, pas par ce timestamp seul. |
| `source_published_at` | `Nullable(DateTime64(3,'UTC'))` | Oui | Maximum de publication CDC des versions contribuant à la ligne ; NULL pour un référentiel exclusivement généré. Les entrées de règles non fournies proviennent du futur dbt/config/case_rules.yml fusionné dans vars, sans seed ou source implicite. Ce maximum ne remplace aucune date métier. |
| `source_version_keys` | `Array(String)` | Non | Clés des versions sources contributrices, triées et sans répétition ; union des lignages amont. Liste vide pour une ligne exclusivement générée. |
| `tenant_id` | `String` | Non | Identité du tenant src_tenant_id. |
| `opportunity_id` | `Int64` | Non | src_id du besoin Boond. |
| `opportunity_key` | `String` | Non | H(tenant_id,opportunity_id), identité stable intermodèles. |
| `period_key` | `String` | Non | H(opportunity_key,valid_from_at). |
| `visit_key` | `String` | Non | Passage courant. |
| `valid_from_at` | `DateTime64(3,'UTC')` | Non | Borne CDC/contexte incluse. |
| `valid_to_at` | `Nullable(DateTime64(3,'UTC'))` | Oui | Borne suivante exclue. |
| `is_source_deleted` | `Bool` | Non | src_is_deleted, sélection des versions avant exclusion. |
| `created_at` | `Nullable(DateTime64(3,'UTC'))` | Oui | src_created_at ; pas antidatation de l’état. |
| `cohort_month` | `Nullable(Date)` | Oui | Mois de création Paris. |
| `stage_id` | `Nullable(Int64)` | Oui | État source. |
| `stage_key` | `Nullable(String)` | Oui | Identité étape. |
| `stage_version_key` | `Nullable(String)` | Oui | Version dim_stage valable sur toute tranche. |
| `outcome_category` | `Nullable(String)` | Oui | Classe analytique, NULL si code non mappé. |
| `is_open` | `Nullable(Bool)` | Oui | Classe open ; suppression et inconnu distincts. |
| `company_id` | `Nullable(Int64)` | Oui | Société Boond au moment de référence. |
| `company_key` | `Nullable(String)` | Oui | H(tenant_id,company_id) si société connue. |
| `company_version_key` | `Nullable(String)` | Oui | Version dim_company à la date de référence ; jointure sur même run. |
| `sale_type_id` | `Nullable(Int64)` | Oui | Type commercial de la version du besoin. |
| `sale_type_key` | `Nullable(String)` | Oui | Identité stable du code type. |
| `sale_type_version_key` | `Nullable(String)` | Oui | Version dim_sale_type au moment de référence. |
| `employee_id` | `Nullable(Int64)` | Oui | Responsable principal Boond à la date pertinente. |
| `employee_key` | `Nullable(String)` | Oui | Identité stable du responsable. |
| `employee_version_key` | `Nullable(String)` | Oui | Version de dim_employee à la date pertinente. |
| `team_id` | `Nullable(Int64)` | Oui | Équipe businessunit seulement si attribution univoque. |
| `team_key` | `Nullable(String)` | Oui | Identité stable d’équipe ; NULL si ambiguë ou inconnue. |
| `team_version_key` | `Nullable(String)` | Oui | Version dim_team pertinente à la date. |
| `sales_segment` | `Nullable(String)` | Oui | SMB / LA / ES si mapping fourni ; NULL sinon. |
| `is_team_calculable` | `Bool` | Non | Vrai si une seule équipe est historiquement résolue ; KAM reste connue même sans segment de cible D23. |
| `acquisition_channel_key` | `Nullable(String)` | Oui | Canal officiel fixé à création ; NULL avant règle QM-02. |
| `channel_version_key` | `Nullable(String)` | Oui | Version de dim_channel applicable à l’acquisition. |
| `channel_candidate_code` | `Nullable(String)` | Oui | Code origine Boond à création, converti String ; candidat descriptif seulement. |
| `is_channel_calculable` | `Bool` | Non | Vrai seulement si règle canal et mapping appliqués sans ambiguïté. |
| `attribution_status` | `String` | Non | resolved / missing_team_mapping / multiple_teams / missing_channel_rule ; détails conservés. |
| `pipeline_amount` | `Nullable(Decimal(38,4))` | Oui | src_estimated_amount_excluding_tax converti chaîne→Decimal(38,4), sans mensualisation. |
| `amount_basis` | `String` | Non | crm_estimated_unconfirmed tant que nature inconnue. |
| `currency_code` | `Nullable(String)` | Oui | EUR par hypothèse explicite du case D20 ; cette devise ne prouve ni mensualité ni engagement du montant commercial. |
| `source_weighting_percent` | `Nullable(Int64)` | Oui | src_weighting_percent descriptif. |
| `source_weighted_amount` | `Nullable(Decimal(38,4))` | Oui | src_weighted_amount_excluding_tax descriptif. |
| `signature_probability` | `Nullable(Decimal(18,8))` | Oui | Coefficient de ref.stage_probabilities choisi selon D21 ; NULL seulement si état/segment non couvert, pas de fallback Boond. |
| `probability_version_key` | `Nullable(String)` | Oui | Version ref si utilisée. |
| `weighted_pipeline_amount` | `Nullable(Decimal(38,4))` | Oui | Produit intermédiaire Decimal(38,12) à proba Decimal(18,8), contrôle dépassement et égalité exacte au cast retour depuis Decimal(38,4). Aucune perte d’échelle admise : sinon résultat NULL, insufficient_decimal_scale et publication de cette mesure bloquée jusqu’à migration de précision. Aucun arrondi intermédiaire ni double pondération. |
| `expected_close_at` | `Nullable(DateTime64(3,'UTC'))` | Oui | src_closing_at saisi, pas signature réelle. |
| `stage_entered_at` | `Nullable(DateTime64(3,'UTC'))` | Oui | entered_at passage, NULL si censuré. |
| `stage_first_observed_at` | `DateTime64(3,'UTC')` | Non | Présence observée dans passage. |
| `stagnation_threshold_days` | `Nullable(Float64)` | Oui | 21jours continus par défaut, dépassement strict>, paramétrable par étape/type D26 ; NULL uniquement si alerte explicitement désactivée. |
| `stagnant_from_at` | `Nullable(DateTime64(3,'UTC'))` | Oui | Début passage + seuil en jours continus si connus. |
| `is_pipeline_eligible` | `Nullable(Bool)` | Oui | true pour type4/7 et état ouvert D22/D30 ; false si explicitement hors population ; NULL si type/état source inconnu. |
| `source_opportunity_version_key` | `String` | Non | Version source portant attributs. |
| `coverage_start_at` | `Nullable(DateTime64(3,'UTC'))` | Oui | Début déclaré. |
| `coverage_end_at` | `Nullable(DateTime64(3,'UTC'))` | Oui | Fin déclarée. |
| `is_history_complete` | `Nullable(Bool)` | Oui | Complétude déclarée de la fenêtre. |
| `calculation_status` | `String` | Non | ready / partial / blocked / not_applicable. |
| `status_reason` | `Nullable(String)` | Oui | Cause précise stable ; NULL si aucune dépendance manquante. |

**Transformation spécifiée :**

1. Construire périodes CDC, suppressions incluses ; associer passage contenant la tranche.
2. Contexte d’acquisition à création seulement si observable et règle choisie ; candidats CRM conservés sans substitution par dernière interaction.
3. Réunir bornes besoin, appartenance, coefficient et dimensions ; tranches atomiques positives.
4. Résoudre au plus une version dimension/équipe ; ambiguïté→clé NULL/statut, pas choix arbitraire.
5. Montants, pondération et seuil seulement si données/règles connues ; conserver aussi périodes fermées et non commerciales.

**Pseudocode normatif de la transformation :**

```text
Pour chaque opportunité et son intervalle d'observation :
  cuts := union regroupée des bornes besoin, passage, dimensions nécessaires,
          appartenance équipe et coefficient réellement applicable.
  Trier cuts ; pour chaque paire successive (a,b) avec a < b :
    résoudre une version source du besoin et chaque contexte tel que from <= a et a < to (ou to NULL).
    si plusieurs versions éligibles d'un même rôle : erreur cardinalité, pas de DISTINCT correctif.
    si aucun contexte : FK NULL + raison ; conserver la contribution de dossier.
    produire period_key=H(opportunity_key,a), [a,b), mêmes attributs et clés de version sur tout l'intervalle.
La dernière période peut rester ouverte ; elle ne certifie pas de couverture au-delà de la date source déclarée.
Le canal d'acquisition provient de l'entrée observable et de sa règle ; jamais dernière source actuelle.
```

**Jointures / cardinalités :** Besoin→passage N:1 ; dimensions N:0..1 tenant/id/temps/même run ; aucun produit de contacts/deals multiples. Clés version valables sur toute tranche.

**Physique, histoire et reprise :** table incrémentale append, MergeTree, unique_key=record_version_key, on_schema_change=fail, full_refresh=false, inserts_only non défini, recomposition COMPLETE de l’histoire disponible pour un manifeste immuable, anti-jointure (model_run_id,record_key) ; ORDER BY (model_run_id,tenant_id,opportunity_id,valid_from_at). Réexécution du même run = aucune copie ; reprise partielle complète les clés absentes sans changer le payload existant. Nouvelle empreinte d’entrée/code/règle = nouvelle révision entière. Aucune limite à hier ni watermark métier dans ce modèle. Mono-écrivain ; partition_by non défini, aucune TTL détaillée sans décision ; query_settings join_use_nulls=1. Avant anti-jointure, comparer row_hash de toute clé/run déjà présente : divergence sous même identité bloque reprise ; puis compléter clés absentes. Publication après tests de structure ; manque métier connu donne mesureNULL et qualité, pas blocage automatique du run entier. Exécution manuelle et fraîcheur de capture/publiée D29, sans SLA automatique.

**Tests / acceptation :** unicité/non-NULL des clés physiques, row_hash déterministe et un seul payload par clé/run ; Une tranche par besoin/date ; non-chevauchement et couverture d’observation conservée. Montants/contributions inchangés après enrichissement ; transfert ne redémarre pas passage. Défaut de grain, jointure ou réconciliation : ERROR et publication bloquée. Manque connu documenté : valeur NULL et statut, WARN si descriptif, KPI indisponible s’il en dépend.

**Limites / dépendances :** règles fixées par D16–D30 ; conserver les données non observables/invalides et les indisponibilités de preuve D13/D14/D28. Aucun arbitrage supplémentaire demandé.


<a id="int_opportunity_events"></a>

### `int_opportunity_events`

**Règle finale v0.2 :** D18/D19 : premier événement signed observable par opportunité contribue1 seulement sans preuve antérieure de gain1/14 ; les signed ultérieurs contribuent0 mais restent dans la table. Une première trace déjà gagnée sans date de signature empêche une re-signature ultérieure de devenir nouvelle vente ; ancienne date resteNULL. Aucune signature ajoutée à14. Création/entrées/sorties comptent leurs unités propres ; population commerciale4/7. Le cycle est uniquement porté par le premier événement terminal datable canonique : signed/lost/abandoned/unqualified, ou stage_entered14 si issue gagnée observée sans inventer signature. À même instant, préférer l’événement terminal métier à stage_entered pour ne pas doubler la durée. Si première issue censurée,duréeNULL. Les événements suivants ont completed_cycle_duration_seconds=NULL pour ce KPI de première issue, tout en conservant leurs dates.

**Grain métier :** Opportunité × événement distinct ; traces de re-signature séparées des contributions. **Grain physique :** (model_run_id,record_key) ; record_key=event_key.

**Amont exact :** `{{ ref('int_opportunity_stage_visits') }}`, `{{ ref('int_opportunity_periods') }}`, `{{ ref('int_crm_identity_links') }}`, `{{ ref('dim_date') }}`. **Destination :** `dwh_pipeline.int_opportunity_events`, `dbt/models/intermediate/pipeline/int_opportunity_events.sql`, YAML `dbt/models/intermediate/pipeline/_models.yml`.

| Colonne | Type ClickHouse | Nullable | Origine, formule, contraintes |
|---|---|---|---|
| `model_run_id` | `String` | Non | Empreinte SHA256 commune de la recomposition : manifeste des entrées figées, code, référentiels et paramètres ; fournie par orchestration, identique dans tout le DAG. |
| `record_key` | `String` | Non | Identité String H(tuple du grain décrit, domaine/version explicite), sans model_run_id ; égale la clé de grain lorsque cette dernière est déjà hashée. dim_date utilise H(calendar_date), jamais date_key UInt32 brut. |
| `record_version_key` | `String` | Non | H(model_run_id,record_key) ; unicité physique de la révision du modèle. |
| `row_hash` | `String` | Non | H(tuple ordonné de toutes les colonnes métier de la fiche, NULL et types préservés) ; exclut les métadonnées de calcul. |
| `calculated_at` | `DateTime64(3,'UTC')` | Non | Instant de calcul du lot ; fixe pour un même model_run_id, jamais utilisé comme événement métier. |
| `rule_version` | `String` | Non | Empreinte immuable du code et des règles appliquées ; dérivée du manifeste du lot. |
| `input_cutoff_at` | `DateTime64(3,'UTC')` | Non | Date limite de connaissance de la recomposition ; les entrées exactes sont figées par le manifeste, pas par ce timestamp seul. |
| `source_published_at` | `Nullable(DateTime64(3,'UTC'))` | Oui | Maximum de publication CDC des versions contribuant à la ligne ; NULL pour un référentiel exclusivement généré. Les entrées de règles non fournies proviennent du futur dbt/config/case_rules.yml fusionné dans vars, sans seed ou source implicite. Ce maximum ne remplace aucune date métier. |
| `source_version_keys` | `Array(String)` | Non | Clés des versions sources contributrices, triées et sans répétition ; union des lignages amont. Liste vide pour une ligne exclusivement générée. |
| `tenant_id` | `String` | Non | Identité du tenant src_tenant_id. |
| `opportunity_id` | `Int64` | Non | src_id du besoin Boond. |
| `opportunity_key` | `String` | Non | H(tenant_id,opportunity_id), identité stable intermodèles. |
| `event_key` | `String` | Non | H(opportunity_key,event_type,event_origin_key). |
| `event_origin_key` | `String` | Non | Clé création source ou visit_key de transition. |
| `visit_key` | `Nullable(String)` | Oui | Passage si pertinent. |
| `event_type` | `String` | Non | pipeline_created / stage_entered / stage_exited / signed / lost / abandoned / unqualified. |
| `event_at` | `Nullable(DateTime64(3,'UTC'))` | Oui | Date métier création ou transition/proxy admissible ; NULL sans preuve. |
| `event_observed_at` | `DateTime64(3,'UTC')` | Non | Publication prouvant la trace ; différente de date métier. |
| `event_time_basis` | `String` | Non | business_created / cdc_transition_proxy / unknown. |
| `event_date_key` | `Nullable(UInt32)` | Oui | Date Paris de event_at. |
| `from_stage_id` | `Nullable(Int64)` | Oui | Étape quittée. |
| `to_stage_id` | `Nullable(Int64)` | Oui | Étape rejointe. |
| `from_stage_version_key` | `Nullable(String)` | Oui | Version étape avant transition. |
| `to_stage_version_key` | `Nullable(String)` | Oui | Version étape à entrée. |
| `created_at` | `Nullable(DateTime64(3,'UTC'))` | Oui | Création Boond. |
| `cohort_month` | `Nullable(Date)` | Oui | Mois création Paris. |
| `company_id` | `Nullable(Int64)` | Oui | Société Boond au moment de référence. |
| `company_key` | `Nullable(String)` | Oui | H(tenant_id,company_id) si société connue. |
| `company_version_key` | `Nullable(String)` | Oui | Version dim_company à la date de référence ; jointure sur même run. |
| `sale_type_id` | `Nullable(Int64)` | Oui | Type commercial de la version du besoin. |
| `sale_type_key` | `Nullable(String)` | Oui | Identité stable du code type. |
| `sale_type_version_key` | `Nullable(String)` | Oui | Version dim_sale_type au moment de référence. |
| `employee_id` | `Nullable(Int64)` | Oui | Responsable principal Boond à la date pertinente. |
| `employee_key` | `Nullable(String)` | Oui | Identité stable du responsable. |
| `employee_version_key` | `Nullable(String)` | Oui | Version de dim_employee à la date pertinente. |
| `team_id` | `Nullable(Int64)` | Oui | Équipe businessunit seulement si attribution univoque. |
| `team_key` | `Nullable(String)` | Oui | Identité stable d’équipe ; NULL si ambiguë ou inconnue. |
| `team_version_key` | `Nullable(String)` | Oui | Version dim_team pertinente à la date. |
| `sales_segment` | `Nullable(String)` | Oui | SMB / LA / ES si mapping fourni ; NULL sinon. |
| `is_team_calculable` | `Bool` | Non | Vrai si une seule équipe est historiquement résolue ; KAM reste connue même sans segment de cible D23. |
| `acquisition_channel_key` | `Nullable(String)` | Oui | Canal officiel fixé à création ; NULL avant règle QM-02. |
| `channel_version_key` | `Nullable(String)` | Oui | Version de dim_channel applicable à l’acquisition. |
| `channel_candidate_code` | `Nullable(String)` | Oui | Code origine Boond à création, converti String ; candidat descriptif seulement. |
| `is_channel_calculable` | `Bool` | Non | Vrai seulement si règle canal et mapping appliqués sans ambiguïté. |
| `attribution_status` | `String` | Non | resolved / missing_team_mapping / multiple_teams / missing_channel_rule ; détails conservés. |
| `is_event_time_accepted` | `Nullable(Bool)` | Oui | Vrai pour date métier prouvée OU transition CDC réellement observée admise par D15 ; NULL si événement non datable/borne inconnue. Conserver cdc_transition_proxy, sans le présenter comme une date métier certifiée. |
| `nb_events` | `Nullable(UInt8)` | Oui | 1 si événement/population et date admissibles ;0 explicitement non comptable ;NULL si date non admissible ou éligibilité inconnue. Le proxy CDC observé est accepté par D15. |
| `generated_pipeline_amount_candidate` | `Nullable(Decimal(38,4))` | Oui | Valeur à création réellement observable ; NULL si première observation tardive. |
| `sum_generated_pipeline_amount` | `Nullable(Decimal(38,4))` | Oui | Contribution commerciale générée admissible ; nature/unité signalées, pas MRR. |
| `sum_signed_mrr` | `Nullable(Decimal(38,4))` | Oui | NULL sans preuve mensualité récurrente signée ; supplément seul upsell. |
| `amount_basis` | `String` | Non | crm_estimated_unconfirmed / signed_recurring_proven / unknown. |
| `currency_code` | `Nullable(String)` | Oui | EUR par hypothèse explicite du case D20 ; cette devise ne prouve ni mensualité ni engagement du montant commercial. |
| `cycle_started_at` | `Nullable(DateTime64(3,'UTC'))` | Oui | Création Boond pour cycle décidé. |
| `completed_cycle_duration_seconds` | `Nullable(Float64)` | Oui | Issue admissible−création si dates connues. |
| `counting_scope_key` | `String` | Non | H(opportunity_key,event_type), pour dossiers distincts. |
| `is_contribution_eligible` | `Nullable(Bool)` | Oui | Première signature observée et population4/7 admissibles selon D18/D22 ; re-signatures connues=false avec contribution0 ; date/population non observable=NULL. Proxy CDC accepté D15. |
| `calculation_status` | `String` | Non | ready / partial / blocked / not_applicable. |
| `status_reason` | `Nullable(String)` | Oui | Cause précise stable ; NULL si aucune dépendance manquante. |

**Transformation spécifiée :**

1. Une création par besoin à date connue ; jamais première publication substituée. Valeur création inconnue si observation tardive.
2. Entrée/sortie pour transitions observées, rôles séparés pour comptage ; pas addition indiscriminée.
3. Signature à entrée state1 ; 1→14 pas deuxième vente ; premier14 sans1 ne fournit aucune date fictive.
4. Réentrées en state1 restent traces ; contribution de re-signature NULL avant règle ; un count distinct ne protège pas une somme.
5. Perdu/abandonné/nonqualifié séparés ; suppression ne crée aucune issue métier.
6. Contexte génération à création, signature à événement ; rôle sortie prend contexte précédent, entrée suivant.
7. Aucun montant estimé ou HubSpot automatiquement assimilé à MRR signé.

**Jointures / cardinalités :** Événement→contexte N:0..1 ; sur frontière t, entrée prend [t,...), sortie la période fin=t. Dimensions N:0..1 même run.

**Physique, histoire et reprise :** table incrémentale append, MergeTree, unique_key=record_version_key, on_schema_change=fail, full_refresh=false, inserts_only non défini, recomposition COMPLETE de l’histoire disponible pour un manifeste immuable, anti-jointure (model_run_id,record_key) ; ORDER BY (model_run_id,tenant_id,opportunity_id,event_observed_at,event_type). Réexécution du même run = aucune copie ; reprise partielle complète les clés absentes sans changer le payload existant. Nouvelle empreinte d’entrée/code/règle = nouvelle révision entière. Aucune limite à hier ni watermark métier dans ce modèle. Mono-écrivain ; partition_by non défini, aucune TTL détaillée sans décision ; query_settings join_use_nulls=1. Avant anti-jointure, comparer row_hash de toute clé/run déjà présente : divergence sous même identité bloque reprise ; puis compléter clés absentes. Publication après tests de structure ; manque métier connu donne mesureNULL et qualité, pas blocage automatique du run entier. Exécution manuelle et fraîcheur de capture/publiée D29, sans SLA automatique.

**Tests / acceptation :** unicité/non-NULL des clés physiques, row_hash déterministe et un seul payload par clé/run ; Création unique ; 1→14 un signed ; premier14 sans1 non daté/non comptable. Aucune suppression→perte ; pas double somme entre stage_entered et signed ; contributions inconnues gardent NULL. Défaut de grain, jointure ou réconciliation : ERROR et publication bloquée. Manque connu documenté : valeur NULL et statut, WARN si descriptif, KPI indisponible s’il en dépend.

**Limites / dépendances :** règles fixées par D16–D30 ; conserver les données non observables/invalides et les indisponibilités de preuve D13/D14/D28. Aucun arbitrage supplémentaire demandé.


<a id="int_opportunity_followup"></a>

### `int_opportunity_followup`

**Règle finale v0.2 :** D17/D18 : cohorte de création inchangée après retour. Cohort_outcome=état À l’horizon individuel, pas «a déjà gagné». Funnel_reach=chaque jalon atteint une fois. Stage_transition=ancre première A observable, première B STRICTEMENT après cette A ; les retours ne créent pas d’autres dénominateurs. Les17 dossiers14sans1 peuvent être gagnés observés à un horizon couvert, sans fournir signature datée. Horizon/observabilité et états inconnus conservés. Les définitions de transition sont activées ; pas de parcours obligatoire ni d’étape sautée imputée.

**Grain métier :** Opportunité × définition × ancrage × observation/horizon. **Grain physique :** (model_run_id,record_key) ; record_key=followup_key.

**Amont exact :** `{{ ref('int_opportunity_events') }}`, `{{ ref('int_opportunity_periods') }}`, `{{ ref('int_opportunity_stage_visits') }}`, `{{ ref('dim_followup_definition') }}`. **Destination :** `dwh_pipeline.int_opportunity_followup`, `dbt/models/intermediate/pipeline/int_opportunity_followup.sql`, YAML `dbt/models/intermediate/pipeline/_models.yml`.

| Colonne | Type ClickHouse | Nullable | Origine, formule, contraintes |
|---|---|---|---|
| `model_run_id` | `String` | Non | Empreinte SHA256 commune de la recomposition : manifeste des entrées figées, code, référentiels et paramètres ; fournie par orchestration, identique dans tout le DAG. |
| `record_key` | `String` | Non | Identité String H(tuple du grain décrit, domaine/version explicite), sans model_run_id ; égale la clé de grain lorsque cette dernière est déjà hashée. dim_date utilise H(calendar_date), jamais date_key UInt32 brut. |
| `record_version_key` | `String` | Non | H(model_run_id,record_key) ; unicité physique de la révision du modèle. |
| `row_hash` | `String` | Non | H(tuple ordonné de toutes les colonnes métier de la fiche, NULL et types préservés) ; exclut les métadonnées de calcul. |
| `calculated_at` | `DateTime64(3,'UTC')` | Non | Instant de calcul du lot ; fixe pour un même model_run_id, jamais utilisé comme événement métier. |
| `rule_version` | `String` | Non | Empreinte immuable du code et des règles appliquées ; dérivée du manifeste du lot. |
| `input_cutoff_at` | `DateTime64(3,'UTC')` | Non | Date limite de connaissance de la recomposition ; les entrées exactes sont figées par le manifeste, pas par ce timestamp seul. |
| `source_published_at` | `Nullable(DateTime64(3,'UTC'))` | Oui | Maximum de publication CDC des versions contribuant à la ligne ; NULL pour un référentiel exclusivement généré. Les entrées de règles non fournies proviennent du futur dbt/config/case_rules.yml fusionné dans vars, sans seed ou source implicite. Ce maximum ne remplace aucune date métier. |
| `source_version_keys` | `Array(String)` | Non | Clés des versions sources contributrices, triées et sans répétition ; union des lignages amont. Liste vide pour une ligne exclusivement générée. |
| `tenant_id` | `String` | Non | Identité du tenant src_tenant_id. |
| `opportunity_id` | `Int64` | Non | src_id du besoin Boond. |
| `opportunity_key` | `String` | Non | H(tenant_id,opportunity_id), identité stable intermodèles. |
| `followup_key` | `String` | Non | H(opportunity_key,followup_definition_version_key,anchor_key,observation_at). |
| `followup_definition_id` | `String` | Non | ID stable de définition. |
| `followup_definition_key` | `String` | Non | Identité stable H(followup_definition_id). |
| `followup_definition_version_key` | `String` | Non | Version exacte de définition. |
| `followup_kind` | `String` | Non | cohort_outcome / funnel_reach / stage_transition. |
| `funnel_position` | `Nullable(UInt16)` | Oui | Position configurée, pas code numérique. |
| `previous_target_stage_id` | `Nullable(Int64)` | Oui | Cible précédente configurée. |
| `created_at` | `Nullable(DateTime64(3,'UTC'))` | Oui | Création Boond. |
| `cohort_month` | `Nullable(Date)` | Oui | Mois Paris de création, inchangé par réouverture. |
| `anchor_key` | `String` | Non | Création ou passage admissible. |
| `anchor_at` | `Nullable(DateTime64(3,'UTC'))` | Oui | Création pour cohorte/funnel ; entrée en A pour transition. |
| `source_stage_id` | `Nullable(Int64)` | Oui | Source transition, NULL cohorte. |
| `target_stage_id` | `Nullable(Int64)` | Oui | Cible funnel/transition, NULL issuecohorte. |
| `target_stage_key` | `Nullable(String)` | Oui | Identité étape cible. |
| `target_stage_version_key` | `Nullable(String)` | Oui | Version cible pertinente. |
| `horizon_days` | `Nullable(UInt16)` | Oui | 30/60/90 cohorte ; transition configurée ; NULL funnel à date. |
| `horizon_at` | `Nullable(DateTime64(3,'UTC'))` | Oui | addDays(anchor converti Paris,H) puis UTC ; même heure locale. |
| `observation_at` | `Nullable(DateTime64(3,'UTC'))` | Oui | horizon_at cohorte/transition ; cutoff funnel à date. |
| `cohort_mature_at` | `Nullable(DateTime64(3,'UTC'))` | Oui | max(horizon_at) sur tous membres connus tenant/mois/type/définition/horizon AVANT équipe/canal. |
| `is_mature` | `Nullable(Bool)` | Oui | Horizon individuel atteint. |
| `is_cohort_mature` | `Nullable(Bool)` | Oui | Cutoff>=cohort_mature_at et ancrages connus. |
| `is_eligible` | `Nullable(Bool)` | Oui | Population/ancrage admis ; NULL sans règle. |
| `is_observable` | `Nullable(Bool)` | Oui | État à horizon couvert ; maturité ne suffit pas. |
| `coverage_start_at` | `Nullable(DateTime64(3,'UTC'))` | Oui | Début déclaré. |
| `coverage_end_at` | `Nullable(DateTime64(3,'UTC'))` | Oui | Fin déclarée, pas maxdate future. |
| `is_history_complete` | `Nullable(Bool)` | Oui | Complétude déclarée pour fenêtre. |
| `first_reached_at` | `Nullable(DateTime64(3,'UTC'))` | Oui | Premier événement cible daté après ancrage ; NULL présence initiale censurée. |
| `first_reached_observed_at` | `Nullable(DateTime64(3,'UTC'))` | Oui | Première présence cible observée ; atteint au plus tard alors, pas date exacte. |
| `previous_stage_first_reached_at` | `Nullable(DateTime64(3,'UTC'))` | Oui | Atteinte admissible source ; NULL si non prouvée. |
| `reached_target` | `Nullable(Bool)` | Oui | Vrai si preuve cible ; faux seulement fenêtre entièrement couverte sans cible ; sinon NULL. |
| `issue_at_horizon` | `Nullable(String)` | Oui | open / won / lost / abandoned / unqualified / unknown ; NULL immature. |
| `population_count_key` | `String` | Non | H(opportunity_key,followup_definition_version_key,horizon_days). |
| `denominator_contribution` | `Nullable(UInt8)` | Oui | 1 membre connu éligible cohorte mature ; NULL immature/ancrage inconnu. |
| `converted_contribution` | `Nullable(UInt8)` | Oui | 1/0 si conversion calculable ; NULL sinon. |
| `open_contribution` | `Nullable(UInt8)` | Oui | 1 issue open, 0 autres ; NULL immature. |
| `won_contribution` | `Nullable(UInt8)` | Oui | 1 won, 0 autres ; NULL immature. |
| `lost_contribution` | `Nullable(UInt8)` | Oui | 1 lost seulement, NULL immature. |
| `abandoned_contribution` | `Nullable(UInt8)` | Oui | 1 abandoned, distinct lost ; NULL immature. |
| `unqualified_contribution` | `Nullable(UInt8)` | Oui | 1 unqualified, distinct lost ; NULL immature. |
| `unknown_contribution` | `Nullable(UInt8)` | Oui | 1 état/classe non observable mature ; inconnu conservé au dénominateur. |
| `company_id` | `Nullable(Int64)` | Oui | Société Boond au moment de référence. |
| `company_key` | `Nullable(String)` | Oui | H(tenant_id,company_id) si société connue. |
| `company_version_key` | `Nullable(String)` | Oui | Version dim_company à la date de référence ; jointure sur même run. |
| `sale_type_id` | `Nullable(Int64)` | Oui | Type commercial de la version du besoin. |
| `sale_type_key` | `Nullable(String)` | Oui | Identité stable du code type. |
| `sale_type_version_key` | `Nullable(String)` | Oui | Version dim_sale_type au moment de référence. |
| `employee_id` | `Nullable(Int64)` | Oui | Responsable principal Boond à la date pertinente. |
| `employee_key` | `Nullable(String)` | Oui | Identité stable du responsable. |
| `employee_version_key` | `Nullable(String)` | Oui | Version de dim_employee à la date pertinente. |
| `team_id` | `Nullable(Int64)` | Oui | Équipe businessunit seulement si attribution univoque. |
| `team_key` | `Nullable(String)` | Oui | Identité stable d’équipe ; NULL si ambiguë ou inconnue. |
| `team_version_key` | `Nullable(String)` | Oui | Version dim_team pertinente à la date. |
| `sales_segment` | `Nullable(String)` | Oui | SMB / LA / ES si mapping fourni ; NULL sinon. |
| `is_team_calculable` | `Bool` | Non | Vrai si une seule équipe est historiquement résolue ; KAM reste connue même sans segment de cible D23. |
| `acquisition_channel_key` | `Nullable(String)` | Oui | Canal officiel fixé à création ; NULL avant règle QM-02. |
| `channel_version_key` | `Nullable(String)` | Oui | Version de dim_channel applicable à l’acquisition. |
| `channel_candidate_code` | `Nullable(String)` | Oui | Code origine Boond à création, converti String ; candidat descriptif seulement. |
| `is_channel_calculable` | `Bool` | Non | Vrai seulement si règle canal et mapping appliqués sans ambiguïté. |
| `attribution_status` | `String` | Non | resolved / missing_team_mapping / multiple_teams / missing_channel_rule ; détails conservés. |
| `calculation_status` | `String` | Non | ready / partial / blocked / not_applicable. |
| `status_reason` | `Nullable(String)` | Oui | Cause précise stable ; NULL si aucune dépendance manquante. |

**Transformation spécifiée :**

1. Joindre définitions compatibles du type, sans fusion nouvelles ventes/upsells ; contexte fixé à ancrage.
2. Calcul horizons Paris puis maxhorizon du mois/type/définition avant filtres équipe/canal.
3. Immature : contributions et dénominateur NULL, jamais résultats futurs0.
4. Mature : état dans période contenant horizon, pas premier état avancé projeté vers passé ; absence/classe inconnue→unknown.
5. Une seule catégorie par membre connu mature avec denominator1 ; inconnus conservés, population réellement exhaustive non certifiée par nombre de membres connus.
6. A→B : ancrage admissible A puis première cible B postérieure, dans horizon ; cible antérieure ne compte pas pour second passage A.
7. Activer les définitions D17/D18 ; aucun ratio de stocks substitué à une conversion de dossiers suivis.

**Pseudocode normatif de la transformation :**

```text
Population := une ligne par identité d'opportunité et définition compatible ; ancrage non ambigu.
Pour chaque H :
  horizon_at := création en Europe/Paris + H jours calendaires, puis UTC.
  cohort_mature_at := max(horizon_at) par tenant/mois/type/définition/H AVANT équipe/canal.
  si cutoff < cohort_mature_at : toutes contributions NULL ; status non_mature.
  sinon :
    denominator=1 pour chaque membre connu éligible ;
    issue=état classé observé à horizon, ou unknown ;
    exactement une des contributions open/won/lost/abandoned/unqualified/unknown=1, autres=0.
La maturité n'affirme jamais l'exhaustivité de la population source ni l'observabilité de l'état.
Pour A→B, sélectionner d'abord l'ancrage en A, puis premier B >= ancrage et <= horizon ;
un B antérieur à ce passage en A ne peut être réutilisé.
```

**Jointures / cardinalités :** Définition/type N:1 ; horizon→période N:0..1 ; atteintes cibles préagrégées par dossier/ancrage. Même run sur toutes relations ; pas réplication de membres.

**Physique, histoire et reprise :** table incrémentale append, MergeTree, unique_key=record_version_key, on_schema_change=fail, full_refresh=false, inserts_only non défini, recomposition COMPLETE de l’histoire disponible pour un manifeste immuable, anti-jointure (model_run_id,record_key) ; ORDER BY (model_run_id,record_key). Réexécution du même run = aucune copie ; reprise partielle complète les clés absentes sans changer le payload existant. Nouvelle empreinte d’entrée/code/règle = nouvelle révision entière. Aucune limite à hier ni watermark métier dans ce modèle. Mono-écrivain ; partition_by non défini, aucune TTL détaillée sans décision ; query_settings join_use_nulls=1. Avant anti-jointure, comparer row_hash de toute clé/run déjà présente : divergence sous même identité bloque reprise ; puis compléter clés absentes. Publication après tests de structure ; manque métier connu donne mesureNULL et qualité, pas blocage automatique du run entier. Exécution manuelle et fraîcheur de capture/publiée D29, sans SLA automatique.

**Tests / acceptation :** unicité/non-NULL des clés physiques, row_hash déterministe et un seul payload par clé/run ; Clé population unique ; six catégories = dénominateur mature. Horizon futur NULL ; filtres équipe/canal ne changent pas maturité. A→B→A ne réutilise pas ancienB ; censure ne devient pas perte. Défaut de grain, jointure ou réconciliation : ERROR et publication bloquée. Manque connu documenté : valeur NULL et statut, WARN si descriptif, KPI indisponible s’il en dépend.

**Limites / dépendances :** règles fixées par D16–D30 ; conserver les données non observables/invalides et les indisponibilités de preuve D13/D14/D28. Aucun arbitrage supplémentaire demandé.




<a id="int_actions_prepared"></a>

### `int_actions_prepared`

**Grain métier :** Action Boond × intervalle de version et contexte analytique. **Grain physique :** (model_run_id,record_key) ; record_key=action_version_key.

**Amont exact :** `{{ ref('stg_boond_actions') }}`, `{{ ref('int_crm_identity_links') }}`, `{{ ref('int_team_membership_periods') }}`, `{{ ref('dim_company') }}`, `{{ ref('dim_employee') }}`, `{{ ref('dim_team') }}`, `{{ ref('dim_action_type') }}`. **Destination :** `dwh_pipeline.int_actions_prepared`, `dbt/models/intermediate/pipeline/int_actions_prepared.sql`, YAML `dbt/models/intermediate/pipeline/_models.yml`.

| Colonne | Type ClickHouse | Nullable | Origine, formule, contraintes |
|---|---|---|---|
| `model_run_id` | `String` | Non | Empreinte SHA256 commune de la recomposition : manifeste des entrées figées, code, référentiels et paramètres ; fournie par orchestration, identique dans tout le DAG. |
| `record_key` | `String` | Non | Identité String H(tuple du grain décrit, domaine/version explicite), sans model_run_id ; égale la clé de grain lorsque cette dernière est déjà hashée. dim_date utilise H(calendar_date), jamais date_key UInt32 brut. |
| `record_version_key` | `String` | Non | H(model_run_id,record_key) ; unicité physique de la révision du modèle. |
| `row_hash` | `String` | Non | H(tuple ordonné de toutes les colonnes métier de la fiche, NULL et types préservés) ; exclut les métadonnées de calcul. |
| `calculated_at` | `DateTime64(3,'UTC')` | Non | Instant de calcul du lot ; fixe pour un même model_run_id, jamais utilisé comme événement métier. |
| `rule_version` | `String` | Non | Empreinte immuable du code et des règles appliquées ; dérivée du manifeste du lot. |
| `input_cutoff_at` | `DateTime64(3,'UTC')` | Non | Date limite de connaissance de la recomposition ; les entrées exactes sont figées par le manifeste, pas par ce timestamp seul. |
| `source_published_at` | `Nullable(DateTime64(3,'UTC'))` | Oui | Maximum de publication CDC des versions contribuant à la ligne ; NULL pour un référentiel exclusivement généré. Les entrées de règles non fournies proviennent du futur dbt/config/case_rules.yml fusionné dans vars, sans seed ou source implicite. Ce maximum ne remplace aucune date métier. |
| `source_version_keys` | `Array(String)` | Non | Clés des versions sources contributrices, triées et sans répétition ; union des lignages amont. Liste vide pour une ligne exclusivement générée. |
| `action_key` | `String` | Non | H(tenant_id,action_id), identité stable. |
| `action_version_key` | `String` | Non | H(action_key,valid_from_at), grain de version. |
| `tenant_id` | `String` | Non | src_tenant_id. |
| `action_id` | `Int64` | Non | src_id. |
| `valid_from_at` | `DateTime64(3,'UTC')` | Non | Publication CDC et bornes de contexte incluses. |
| `valid_to_at` | `Nullable(DateTime64(3,'UTC'))` | Oui | Version/context suivant exclu. |
| `source_action_published_at` | `DateTime64(3,'UTC')` | Non | Publication CDC exacte de l’action, sans max des autres objets de contexte. |
| `is_source_deleted` | `Bool` | Non | src_is_deleted. |
| `action_type_id` | `Nullable(Int64)` | Oui | src_type_id. |
| `action_type_key` | `Nullable(String)` | Oui | Identité type. |
| `action_type_version_key` | `Nullable(String)` | Oui | Version dim_action_type. |
| `company_id` | `Nullable(Int64)` | Oui | src_company_id ; pas complétion ambiguë. |
| `company_key` | `Nullable(String)` | Oui | Identité société. |
| `company_version_key` | `Nullable(String)` | Oui | Version société à date. |
| `contact_id` | `Nullable(Int64)` | Oui | dependsOn.id si type=contact. |
| `opportunity_id` | `Nullable(Int64)` | Oui | dependsOn.id si type=opportunity ; NULL si seul contact. |
| `opportunity_key` | `Nullable(String)` | Oui | Besoin seulement si lien direct établi. |
| `depends_on_type` | `String` | Non | src_depends_on_type. |
| `depends_on_id` | `Nullable(Int64)` | Oui | src_depends_on_id, lu avec type. |
| `employee_id` | `Nullable(Int64)` | Oui | src_main_manager_id. |
| `employee_key` | `Nullable(String)` | Oui | Identité responsable. |
| `employee_version_key` | `Nullable(String)` | Oui | Version responsable. |
| `team_key` | `Nullable(String)` | Oui | Équipe si règle action et mapping explicites ; NULL sinon. |
| `team_version_key` | `Nullable(String)` | Oui | Version équipe. |
| `is_team_calculable` | `Bool` | Non | Attribution action résolue et univoque. |
| `created_at` | `Nullable(DateTime64(3,'UTC'))` | Oui | src_created_at. |
| `scheduled_start_at` | `Nullable(DateTime64(3,'UTC'))` | Oui | src_started_at, agenda uniquement. |
| `scheduled_end_at` | `Nullable(DateTime64(3,'UTC'))` | Oui | src_ended_at, agenda uniquement. |
| `actual_event_at` | `Nullable(DateTime64(3,'UTC'))` | Oui | NULL sans preuve structurée de tenue. |
| `realization_status` | `String` | Non | unknown sans preuve ; held/planned/cancelled/no_show seulement si prouvé. |
| `is_demo_request` | `Bool` | Non | Type25 selon mapping, sans compter les versions. |
| `is_demo_type` | `Bool` | Non | Type60/68 selon mapping documentaire. |
| `is_realized_demo` | `Nullable(Bool)` | Oui | NULL sans preuve de tenue ; type passé ne suffit pas. |
| `demo_session_key` | `Nullable(String)` | Oui | Séance réelle dédupliquée, NULL sans règle/proof. |
| `counting_date` | `Nullable(Date)` | Oui | Date Paris tenue réelle, NULL sans preuve. |
| `link_status` | `String` | Non | direct_opportunity / contact_only / missing / ambiguous. |
| `calculation_status` | `String` | Non | ready / partial / blocked / not_applicable. |
| `status_reason` | `Nullable(String)` | Oui | Cause précise stable ; NULL si aucune dépendance manquante. |

**Transformation spécifiée :**

1. Conserver toutes actions et versions, pas seulement démos.
2. Résoudre dependsOn avec son type ; un contact ne devient pas un besoin unique par proximité de date.
3. Ne pas utiliser HTML libre comme preuve de tenue sans règle explicite/validation.
4. Agenda et types restent disponibles ; actual_event_at/is_realized_demo/counting_date NULL sans preuve.
5. Suppression technique n’est pas annulation ; une action n’est pas comptée par version. Pour lecture passée corrigée, choisir dernière version pertinente au cutoff, puis traiter suppression ; ne pas ressusciter l’ancienne vivante.

**Jointures / cardinalités :** Action→type/société/responsable N:0..1 temporel et même run ; ambiguïtés en statut, pas lignes supplémentaires.

**Physique, histoire et reprise :** table incrémentale append, MergeTree, unique_key=record_version_key, on_schema_change=fail, full_refresh=false, inserts_only non défini, recomposition COMPLETE de l’histoire disponible pour un manifeste immuable, anti-jointure (model_run_id,record_key) ; ORDER BY (model_run_id,tenant_id,action_id,valid_from_at). Réexécution du même run = aucune copie ; reprise partielle complète les clés absentes sans changer le payload existant. Nouvelle empreinte d’entrée/code/règle = nouvelle révision entière. Aucune limite à hier ni watermark métier dans ce modèle. Mono-écrivain ; partition_by non défini, aucune TTL détaillée sans décision ; query_settings join_use_nulls=1. Avant anti-jointure, comparer row_hash de toute clé/run déjà présente : divergence sous même identité bloque reprise ; puis compléter clés absentes. Publication après tests de structure ; manque métier connu donne mesureNULL et qualité, pas blocage automatique du run entier. Exécution manuelle et fraîcheur de capture/publiée D29, sans SLA automatique.

**Tests / acceptation :** unicité/non-NULL des clés physiques, row_hash déterministe et un seul payload par clé/run ; Une action/date une seule version admissible ; type/id cohérents. Type60 passé sans preuve→is_realized_demo NULL ; deux versions ne font pas deux séances. Défaut de grain, jointure ou réconciliation : ERROR et publication bloquée. Manque connu documenté : valeur NULL et statut, WARN si descriptif, KPI indisponible s’il en dépend.

**Limites / dépendances :** QC-02 preuve de tenue, déduplication, reports et parcours ; réalisé O04 NULL.


<a id="int_demo_intervals"></a>

### `int_demo_intervals`

**Grain métier :** Parcours prouvé × couple ordonné d’événements admissibles. **Grain physique :** (model_run_id,record_key) ; record_key=demo_interval_key.

**Amont exact :** `{{ ref('int_actions_prepared') }}`, `{{ ref('int_crm_identity_links') }}`. **Destination :** `dwh_pipeline.int_demo_intervals`, `dbt/models/intermediate/pipeline/int_demo_intervals.sql`, YAML `dbt/models/intermediate/pipeline/_models.yml`.

| Colonne | Type ClickHouse | Nullable | Origine, formule, contraintes |
|---|---|---|---|
| `model_run_id` | `String` | Non | Empreinte SHA256 commune de la recomposition : manifeste des entrées figées, code, référentiels et paramètres ; fournie par orchestration, identique dans tout le DAG. |
| `record_key` | `String` | Non | Identité String H(tuple du grain décrit, domaine/version explicite), sans model_run_id ; égale la clé de grain lorsque cette dernière est déjà hashée. dim_date utilise H(calendar_date), jamais date_key UInt32 brut. |
| `record_version_key` | `String` | Non | H(model_run_id,record_key) ; unicité physique de la révision du modèle. |
| `row_hash` | `String` | Non | H(tuple ordonné de toutes les colonnes métier de la fiche, NULL et types préservés) ; exclut les métadonnées de calcul. |
| `calculated_at` | `DateTime64(3,'UTC')` | Non | Instant de calcul du lot ; fixe pour un même model_run_id, jamais utilisé comme événement métier. |
| `rule_version` | `String` | Non | Empreinte immuable du code et des règles appliquées ; dérivée du manifeste du lot. |
| `input_cutoff_at` | `DateTime64(3,'UTC')` | Non | Date limite de connaissance de la recomposition ; les entrées exactes sont figées par le manifeste, pas par ce timestamp seul. |
| `source_published_at` | `Nullable(DateTime64(3,'UTC'))` | Oui | Maximum de publication CDC des versions contribuant à la ligne ; NULL pour un référentiel exclusivement généré. Les entrées de règles non fournies proviennent du futur dbt/config/case_rules.yml fusionné dans vars, sans seed ou source implicite. Ce maximum ne remplace aucune date métier. |
| `source_version_keys` | `Array(String)` | Non | Clés des versions sources contributrices, triées et sans répétition ; union des lignages amont. Liste vide pour une ligne exclusivement générée. |
| `demo_interval_key` | `String` | Non | H(demo_journey_key,start_action_key,end_action_key,interval_kind). |
| `demo_journey_key` | `String` | Non | Parcours explicitement relié ; pas génération par contact seul. |
| `tenant_id` | `String` | Non | Tenant commun des deux actions. |
| `start_action_key` | `String` | Non | Action début. |
| `end_action_key` | `String` | Non | Action fin. |
| `start_action_id` | `Int64` | Non | ID source début. |
| `end_action_id` | `Int64` | Non | ID source fin. |
| `opportunity_id` | `Nullable(Int64)` | Oui | Besoin commun prouvé. |
| `opportunity_key` | `Nullable(String)` | Oui | Besoin prouvé seulement. |
| `company_key` | `Nullable(String)` | Oui | Société cohérente des deux actions. |
| `company_version_key` | `Nullable(String)` | Oui | Version société à ancrage. |
| `sale_type_id` | `Nullable(Int64)` | Oui | Type du besoin prouvé. |
| `sale_type_key` | `Nullable(String)` | Oui | Identité type. |
| `sale_type_version_key` | `Nullable(String)` | Oui | Version type. |
| `team_key` | `Nullable(String)` | Oui | NULL avant convention d’attribution délai. |
| `team_version_key` | `Nullable(String)` | Oui | Version équipe si règle ultérieure. |
| `interval_kind` | `String` | Non | request_to_first_demo / first_to_additional. |
| `from_demo_step` | `String` | Non | Sous-étape début. |
| `to_demo_step` | `String` | Non | Sous-étape fin. |
| `started_at` | `DateTime64(3,'UTC')` | Non | Événement début prouvé. |
| `ended_at` | `DateTime64(3,'UTC')` | Non | Événement fin prouvé, >=début. |
| `elapsed_duration_seconds` | `Float64` | Non | Écart millisecondes UTC/1000. |
| `elapsed_duration_days` | `Float64` | Non | Secondes/86400. |
| `time_basis` | `String` | Non | Nature précise événements ; pas durée agenda. |
| `link_status` | `String` | Non | proven pour lignes construites. |
| `calculation_status` | `String` | Non | ready / partial / blocked / not_applicable. |
| `status_reason` | `Nullable(String)` | Oui | Cause précise stable ; NULL si aucune dépendance manquante. |

**Transformation spécifiée :**

1. Sans règle de chaînage et deux événements prouvés : table vide documentée, pas durée0.
2. Quand règle fournie : grouper par parcours prouvé et sélectionner couples admissibles, sans croiser toutes actions d’un contact.
3. Complément non obligatoire ; report non assimilé à tenue.

**Jointures / cardinalités :** Couple→actions N:1 par rôle sur versions retenues ; même run/tenant/parcours ; société/besoin cohérents.

**Physique, histoire et reprise :** table incrémentale append, MergeTree, unique_key=record_version_key, on_schema_change=fail, full_refresh=false, inserts_only non défini, recomposition COMPLETE de l’histoire disponible pour un manifeste immuable, anti-jointure (model_run_id,record_key) ; ORDER BY (model_run_id,tenant_id,demo_journey_key,started_at). Réexécution du même run = aucune copie ; reprise partielle complète les clés absentes sans changer le payload existant. Nouvelle empreinte d’entrée/code/règle = nouvelle révision entière. Aucune limite à hier ni watermark métier dans ce modèle. Mono-écrivain ; partition_by non défini, aucune TTL détaillée sans décision ; query_settings join_use_nulls=1. Avant anti-jointure, comparer row_hash de toute clé/run déjà présente : divergence sous même identité bloque reprise ; puis compléter clés absentes. Publication après tests de structure ; manque métier connu donne mesureNULL et qualité, pas blocage automatique du run entier. Exécution manuelle et fraîcheur de capture/publiée D29, sans SLA automatique.

**Tests / acceptation :** unicité/non-NULL des clés physiques, row_hash déterministe et un seul payload par clé/run ; Couple unique et ordre temporel non négatif. Avec seuls liens contact et dates agenda : aucune ligne analytique admissible. Défaut de grain, jointure ou réconciliation : ERROR et publication bloquée. Manque connu documenté : valeur NULL et statut, WARN si descriptif, KPI indisponible s’il en dépend.

**Limites / dépendances :** QC-02/QC-03 : table conditionnelle, vide actuel signifie non calculable, pas absence de délai réel.


<a id="int_visit_responsibility"></a>

### `int_visit_responsibility`

**Règle finale v0.2 :** D25 active la règle équipe d’entrée pour les quantiles des passages complets. Les tranches restent de vrais segments temporels ; allocated_duration_seconds peut porter leur durée propre connue, jamais la durée complète répétée. Aucune jointure des tranches aux passages pour sommer les durées entières ; la sélection équipe du passage utilise entry_team_key seulement.

**Grain métier :** Passage × intersection d’un contexte responsable/équipe. **Grain physique :** (model_run_id,record_key) ; record_key=responsibility_slice_key.

**Amont exact :** `{{ ref('int_opportunity_stage_visits') }}`, `{{ ref('int_opportunity_periods') }}`, `{{ ref('dim_employee') }}`, `{{ ref('dim_team') }}`. **Destination :** `dwh_pipeline.int_visit_responsibility`, `dbt/models/intermediate/pipeline/int_visit_responsibility.sql`, YAML `dbt/models/intermediate/pipeline/_models.yml`.

| Colonne | Type ClickHouse | Nullable | Origine, formule, contraintes |
|---|---|---|---|
| `model_run_id` | `String` | Non | Empreinte SHA256 commune de la recomposition : manifeste des entrées figées, code, référentiels et paramètres ; fournie par orchestration, identique dans tout le DAG. |
| `record_key` | `String` | Non | Identité String H(tuple du grain décrit, domaine/version explicite), sans model_run_id ; égale la clé de grain lorsque cette dernière est déjà hashée. dim_date utilise H(calendar_date), jamais date_key UInt32 brut. |
| `record_version_key` | `String` | Non | H(model_run_id,record_key) ; unicité physique de la révision du modèle. |
| `row_hash` | `String` | Non | H(tuple ordonné de toutes les colonnes métier de la fiche, NULL et types préservés) ; exclut les métadonnées de calcul. |
| `calculated_at` | `DateTime64(3,'UTC')` | Non | Instant de calcul du lot ; fixe pour un même model_run_id, jamais utilisé comme événement métier. |
| `rule_version` | `String` | Non | Empreinte immuable du code et des règles appliquées ; dérivée du manifeste du lot. |
| `input_cutoff_at` | `DateTime64(3,'UTC')` | Non | Date limite de connaissance de la recomposition ; les entrées exactes sont figées par le manifeste, pas par ce timestamp seul. |
| `source_published_at` | `Nullable(DateTime64(3,'UTC'))` | Oui | Maximum de publication CDC des versions contribuant à la ligne ; NULL pour un référentiel exclusivement généré. Les entrées de règles non fournies proviennent du futur dbt/config/case_rules.yml fusionné dans vars, sans seed ou source implicite. Ce maximum ne remplace aucune date métier. |
| `source_version_keys` | `Array(String)` | Non | Clés des versions sources contributrices, triées et sans répétition ; union des lignages amont. Liste vide pour une ligne exclusivement générée. |
| `responsibility_slice_key` | `String` | Non | H(visit_key,valid_from_at,valid_to_at,employee_key,team_key). |
| `tenant_id` | `String` | Non | Tenant passage. |
| `opportunity_key` | `String` | Non | Besoin. |
| `visit_key` | `String` | Non | Passage. |
| `employee_key` | `Nullable(String)` | Oui | Responsable observé. |
| `employee_version_key` | `Nullable(String)` | Oui | Version employé sur toute tranche. |
| `team_key` | `Nullable(String)` | Oui | Équipe résolue si disponible. |
| `team_version_key` | `Nullable(String)` | Oui | Version équipe. |
| `valid_from_at` | `DateTime64(3,'UTC')` | Non | Maximum débuts observés passage/contexte. |
| `valid_to_at` | `Nullable(DateTime64(3,'UTC'))` | Oui | Minimum fins observées ; NULL encore en cours. |
| `observed_slice_duration_seconds` | `Nullable(Float64)` | Oui | Écart bornes d’observation fermées ; pas durée exacte d’un début censuré. |
| `allocated_duration_seconds` | `Nullable(Float64)` | Oui | NULL avant règle individuelle/équipe. |
| `allocation_status` | `String` | Non | not_decided / observed_context_only. |
| `is_team_filter_available` | `Bool` | Non | true si équipe unique à entrée résolue selon D25 ; false si entrée/équipe inconnue. Ne pas utiliser cette tranche pour dupliquer une durée entière. |
| `calculation_status` | `String` | Non | ready / partial / blocked / not_applicable. |
| `status_reason` | `Nullable(String)` | Oui | Cause précise stable ; NULL si aucune dépendance manquante. |

**Transformation spécifiée :**

1. Intersecter passages et contextes ; retirer intersections vides.
2. Transfert ne crée pas nouveau visit_key.
3. Durée observée de tranche descriptive ; aucune répartition individuelle validée implicitement.
4. Fusion bridge_visit_responsibility : clés dimensions exposées ici, aucune bridge supplémentaire.

**Jointures / cardinalités :** Passage→tranches1:N explicite ; tranche→dimensions N:0..1 même run. Interdit de sommer le montant complet du passage après jointure.

**Physique, histoire et reprise :** table incrémentale append, MergeTree, unique_key=record_version_key, on_schema_change=fail, full_refresh=false, inserts_only non défini, recomposition COMPLETE de l’histoire disponible pour un manifeste immuable, anti-jointure (model_run_id,record_key) ; ORDER BY (model_run_id,tenant_id,visit_key,valid_from_at). Réexécution du même run = aucune copie ; reprise partielle complète les clés absentes sans changer le payload existant. Nouvelle empreinte d’entrée/code/règle = nouvelle révision entière. Aucune limite à hier ni watermark métier dans ce modèle. Mono-écrivain ; partition_by non défini, aucune TTL détaillée sans décision ; query_settings join_use_nulls=1. Avant anti-jointure, comparer row_hash de toute clé/run déjà présente : divergence sous même identité bloque reprise ; puis compléter clés absentes. Publication après tests de structure ; manque métier connu donne mesureNULL et qualité, pas blocage automatique du run entier. Exécution manuelle et fraîcheur de capture/publiée D29, sans SLA automatique.

**Tests / acceptation :** unicité/non-NULL des clés physiques, row_hash déterministe et un seul payload par clé/run ; Tranches non chevauchantes, union égale à la fenêtre observée. Deux responsables successifs ne reçoivent pas chacun durée entière ; allocation officielle NULL. Défaut de grain, jointure ou réconciliation : ERROR et publication bloquée. Manque connu documenté : valeur NULL et statut, WARN si descriptif, KPI indisponible s’il en dépend.

**Limites / dépendances :** règles fixées par D16–D30 ; conserver les données non observables/invalides et les indisponibilités de preuve D13/D14/D28. Aucun arbitrage supplémentaire demandé.


<a id="int_subscription_periods"></a>

### `int_subscription_periods`

**Règle finale v0.2 :** D16/D20 : montants mensuels en EUR par hypothèse du case, état1+période de service ; publication ne prouve pas création fiable et n’efface aucune anomalie. Aucun filtre projet.typeOf=4 ne supprime les variations actives d’un client. currency_unconfirmed n’est plus un blocage générique de cette version ; données invalides/activité inconnue restent bloquantes pour leur contribution.

**Grain métier :** Ligne d’abonnement × intervalle d’attributs et rattachement projet observés. **Grain physique :** (model_run_id,record_key) ; record_key=subscription_period_key.

**Amont exact :** `{{ ref('stg_boond_deliveries') }}`, `{{ ref('stg_boond_projects') }}`, `{{ ref('stg_boond_companies') }}`, `{{ ref('int_crm_identity_links') }}`, `{{ ref('dim_company') }}`. **Destination :** `dwh_revenue.int_subscription_periods`, `dbt/models/intermediate/revenue/int_subscription_periods.sql`, YAML `dbt/models/intermediate/revenue/_models.yml`.

| Colonne | Type ClickHouse | Nullable | Origine, formule, contraintes |
|---|---|---|---|
| `model_run_id` | `String` | Non | Empreinte SHA256 commune de la recomposition : manifeste des entrées figées, code, référentiels et paramètres ; fournie par orchestration, identique dans tout le DAG. |
| `record_key` | `String` | Non | Identité String H(tuple du grain décrit, domaine/version explicite), sans model_run_id ; égale la clé de grain lorsque cette dernière est déjà hashée. dim_date utilise H(calendar_date), jamais date_key UInt32 brut. |
| `record_version_key` | `String` | Non | H(model_run_id,record_key) ; unicité physique de la révision du modèle. |
| `row_hash` | `String` | Non | H(tuple ordonné de toutes les colonnes métier de la fiche, NULL et types préservés) ; exclut les métadonnées de calcul. |
| `calculated_at` | `DateTime64(3,'UTC')` | Non | Instant de calcul du lot ; fixe pour un même model_run_id, jamais utilisé comme événement métier. |
| `rule_version` | `String` | Non | Empreinte immuable du code et des règles appliquées ; dérivée du manifeste du lot. |
| `input_cutoff_at` | `DateTime64(3,'UTC')` | Non | Date limite de connaissance de la recomposition ; les entrées exactes sont figées par le manifeste, pas par ce timestamp seul. |
| `source_published_at` | `Nullable(DateTime64(3,'UTC'))` | Oui | Maximum de publication CDC des versions contribuant à la ligne ; NULL pour un référentiel exclusivement généré. Les entrées de règles non fournies proviennent du futur dbt/config/case_rules.yml fusionné dans vars, sans seed ou source implicite. Ce maximum ne remplace aucune date métier. |
| `source_version_keys` | `Array(String)` | Non | Clés des versions sources contributrices, triées et sans répétition ; union des lignages amont. Liste vide pour une ligne exclusivement générée. |
| `subscription_period_key` | `String` | Non | H(subscription_key,valid_from_at). |
| `tenant_id` | `String` | Non | Tenant ligne/projet. |
| `line_id` | `Int64` | Non | src_id deliveries. |
| `line_created_at` | `Nullable(DateTime64(3,'UTC'))` | Oui | src_created_at de la livraison ; conserver les valeurs source, pas premier meta.ts. |
| `is_creation_date_reliable` | `Bool` | Non | true seulement si création nonNULL constante entre versions, aucun CDC antérieur à cette création et aucun début de service antérieur contradictoire ; false sinon, pas de correction de la source. |
| `subscription_key` | `String` | Non | H(tenant_id,line_id) ; pas continuité inventée entre lignes. |
| `project_id` | `Nullable(Int64)` | Oui | src_project_id. |
| `project_key` | `Nullable(String)` | Oui | H(tenant_id,project_id). |
| `company_id` | `Nullable(Int64)` | Oui | src_company_id du projet à date. |
| `company_key` | `Nullable(String)` | Oui | Identité société. |
| `company_version_key` | `Nullable(String)` | Oui | Version société sur tranche. |
| `opportunity_id` | `Nullable(Int64)` | Oui | src_opportunity_id projet, lien direct descriptif. |
| `valid_from_at` | `DateTime64(3,'UTC')` | Non | Début d’observation/contexte inclus. |
| `valid_to_at` | `Nullable(DateTime64(3,'UTC'))` | Oui | Fin exclue. |
| `is_source_deleted` | `Bool` | Non | Suppression ligne conservée. |
| `is_project_deleted` | `Nullable(Bool)` | Oui | Suppression technique projet, pas résiliation. |
| `service_started_at` | `Nullable(DateTime64(3,'UTC'))` | Oui | src_started_at ligne. |
| `service_ended_at` | `Nullable(DateTime64(3,'UTC'))` | Oui | src_ended_at ligne ; jour local de fin inclus. |
| `service_start_date` | `Nullable(Date)` | Oui | Date Paris début. |
| `service_end_exclusive_at` | `Nullable(DateTime64(3,'UTC'))` | Oui | Minuit Paris lendemain du jour de fin converti UTC ; NULL fin absente. |
| `line_state_id` | `Nullable(Int64)` | Oui | src_state_id ;1=En cours selon règle choisie. |
| `project_type_id` | `Nullable(Int64)` | Oui | src_type_id projet descriptif ; activité selon état/période D12, sans filtre project_type=4 ni exclusion d’expansion. |
| `project_started_at` | `Nullable(DateTime64(3,'UTC'))` | Oui | Début projet séparé. |
| `project_ended_at` | `Nullable(DateTime64(3,'UTC'))` | Oui | Fin projet séparée. |
| `quantity` | `Nullable(Decimal(38,4))` | Oui | JSON subscriptionQuantityCharged valide, NULL sinon. |
| `unit_monthly_price` | `Nullable(Decimal(38,4))` | Oui | JSON subscriptionPriceExcludingTax valide. |
| `line_monthly_amount` | `Nullable(Decimal(38,4))` | Oui | src_average_daily_price_excluding_tax : montant mensuel TOTAL incluant quantité, converti Decimal. |
| `recomputed_quantity_price_amount` | `Nullable(Decimal(38,4))` | Oui | Produit quantity×unit_monthly_price à échelle intermédiaire8, contrôle dépassement et absence de perte avant représentation finale ; contrôle uniquement, jamais contribution supplémentaire. |
| `currency_code` | `Nullable(String)` | Oui | EUR par hypothèse explicite du case D20 ; cette devise ne prouve ni mensualité ni engagement du montant commercial. |
| `monetary_status` | `String` | Non | monthly_amount_known_currency_unknown / ready / missing_amount / invalid_amount. |
| `continuity_key` | `Nullable(String)` | Oui | Continuité remplacement entre lignes uniquement si prouvée, NULL actuellement. |
| `activity_rule_status` | `String` | Non | line_state_1_and_service_dates ; état/dates manquants indéterminés. |
| `source_delivery_version_key` | `String` | Non | Version source ligne. |
| `source_project_version_key` | `Nullable(String)` | Oui | Version projet au même instant. |
| `coverage_start_at` | `Nullable(DateTime64(3,'UTC'))` | Oui | Début déclaré. |
| `coverage_end_at` | `Nullable(DateTime64(3,'UTC'))` | Oui | Fin déclarée. |
| `is_history_complete` | `Nullable(Bool)` | Oui | Complétude des versions/liens déclarée. |
| `calculation_status` | `String` | Non | ready / partial / blocked / not_applicable. |
| `status_reason` | `Nullable(String)` | Oui | Cause précise stable ; NULL si aucune dépendance manquante. |

**Transformation spécifiée :**

1. Périodes CDC lignes/projets, suppressions incluses, sans dernier état actuel appliqué au passé.
2. Scinder aux changements projet/société/dimensions ; référence versionnée observable à date.
3. JSON : contrôles présence/type/validité. Montant total source repris, qty×prix seulement réconciliation.
4. Règle choisie : état 1 En cours et période de service à clôture ; jour de fin inclus. Montant0 en état 1 dans période reste actif et MRR nul connu.
5. Pause non représentée = limite de détection, pas état inventé. Suppression technique ne prouve pas résiliation.
6. Suppression empêchant évaluation fiable→activité inconnue, pas absence commerciale démontrée.

**Jointures / cardinalités :** Ligne→projet N:0..1 tenant/id/temps ; projet→société N:0..1. Orphelin conservé avec company_key NULL et statut bloquant.

**Physique, histoire et reprise :** table incrémentale append, MergeTree, unique_key=record_version_key, on_schema_change=fail, full_refresh=false, inserts_only non défini, recomposition COMPLETE de l’histoire disponible pour un manifeste immuable, anti-jointure (model_run_id,record_key) ; ORDER BY (model_run_id,tenant_id,line_id,valid_from_at). Réexécution du même run = aucune copie ; reprise partielle complète les clés absentes sans changer le payload existant. Nouvelle empreinte d’entrée/code/règle = nouvelle révision entière. Aucune limite à hier ni watermark métier dans ce modèle. Mono-écrivain ; partition_by non défini, aucune TTL détaillée sans décision ; query_settings join_use_nulls=1. Avant anti-jointure, comparer row_hash de toute clé/run déjà présente : divergence sous même identité bloque reprise ; puis compléter clés absentes. Publication après tests de structure ; manque métier connu donne mesureNULL et qualité, pas blocage automatique du run entier. Exécution manuelle et fraîcheur de capture/publiée D29, sans SLA automatique.

**Tests / acceptation :** unicité/non-NULL des clés physiques, row_hash déterministe et un seul payload par clé/run ; Clé et périodes uniques ; zéro multiplication à jointure projets. Montant total non remultiplié quantité ; écart qty×prix signalé. Fin de jour incluse,0 actif conservé,devise non déduite de taux1. Défaut de grain, jointure ou réconciliation : ERROR et publication bloquée. Manque connu documenté : valeur NULL et statut, WARN si descriptif, KPI indisponible s’il en dépend.

**Limites / dépendances :** Devise, couverture et continuité non confirmées ; montant officiel EUR indisponible sans devise prouvée.



**Preuve avant création** : une date CRM seule ne réécrit pas un abonnement rétroactif. La création doit être cohérente avec toutes les versions et dates de service. Le contrôle complémentaire Q12 a trouvé194/214 créations postérieures à une publication : ce défaut de chronologie reste signalé et interdit seulement cette inférence d’absence ; il ne supprime pas une période observée ni ses contributions admissibles.

<a id="int_subscription_changes"></a>

### `int_subscription_changes`

**Grain métier :** Ligne × changement observé ou borne métier candidate. **Grain physique :** (model_run_id,record_key) ; record_key=subscription_change_key.

**Amont exact :** `{{ ref('int_subscription_periods') }}`. **Destination :** `dwh_revenue.int_subscription_changes`, `dbt/models/intermediate/revenue/int_subscription_changes.sql`, YAML `dbt/models/intermediate/revenue/_models.yml`.

| Colonne | Type ClickHouse | Nullable | Origine, formule, contraintes |
|---|---|---|---|
| `model_run_id` | `String` | Non | Empreinte SHA256 commune de la recomposition : manifeste des entrées figées, code, référentiels et paramètres ; fournie par orchestration, identique dans tout le DAG. |
| `record_key` | `String` | Non | Identité String H(tuple du grain décrit, domaine/version explicite), sans model_run_id ; égale la clé de grain lorsque cette dernière est déjà hashée. dim_date utilise H(calendar_date), jamais date_key UInt32 brut. |
| `record_version_key` | `String` | Non | H(model_run_id,record_key) ; unicité physique de la révision du modèle. |
| `row_hash` | `String` | Non | H(tuple ordonné de toutes les colonnes métier de la fiche, NULL et types préservés) ; exclut les métadonnées de calcul. |
| `calculated_at` | `DateTime64(3,'UTC')` | Non | Instant de calcul du lot ; fixe pour un même model_run_id, jamais utilisé comme événement métier. |
| `rule_version` | `String` | Non | Empreinte immuable du code et des règles appliquées ; dérivée du manifeste du lot. |
| `input_cutoff_at` | `DateTime64(3,'UTC')` | Non | Date limite de connaissance de la recomposition ; les entrées exactes sont figées par le manifeste, pas par ce timestamp seul. |
| `source_published_at` | `Nullable(DateTime64(3,'UTC'))` | Oui | Maximum de publication CDC des versions contribuant à la ligne ; NULL pour un référentiel exclusivement généré. Les entrées de règles non fournies proviennent du futur dbt/config/case_rules.yml fusionné dans vars, sans seed ou source implicite. Ce maximum ne remplace aucune date métier. |
| `source_version_keys` | `Array(String)` | Non | Clés des versions sources contributrices, triées et sans répétition ; union des lignages amont. Liste vide pour une ligne exclusivement générée. |
| `subscription_change_key` | `String` | Non | H(subscription_key,trigger_kind,trigger_origin_key). |
| `tenant_id` | `String` | Non | Tenant. |
| `subscription_key` | `String` | Non | Identité ligne. |
| `line_id` | `Int64` | Non | ID ligne. |
| `company_key` | `Nullable(String)` | Oui | Société si connue/cohérente. |
| `continuity_key` | `Nullable(String)` | Oui | Rapprochement lignes si prouvé. |
| `before_period_key` | `Nullable(String)` | Oui | Période précédente. |
| `after_period_key` | `Nullable(String)` | Oui | Période suivante. |
| `observed_change_at` | `Nullable(DateTime64(3,'UTC'))` | Oui | Publication CDC ; NULL si échéance seule. |
| `effective_at` | `Nullable(DateTime64(3,'UTC'))` | Oui | Date d’effet métier prouvée ; NULL sinon. |
| `trigger_kind` | `String` | Non | cdc_attribute_change / service_start_boundary / service_end_boundary. |
| `trigger_origin_key` | `String` | Non | Version/bornes motivant candidat. |
| `amount_before` | `Nullable(Decimal(38,4))` | Oui | Montant mensuel avant. |
| `amount_after` | `Nullable(Decimal(38,4))` | Oui | Montant mensuel après. |
| `delta_amount` | `Nullable(Decimal(38,4))` | Oui | Après−avant si tous deux connus. |
| `is_active_before` | `Nullable(Bool)` | Oui | Activité avant la borne. |
| `is_active_after` | `Nullable(Bool)` | Oui | Activité après, indépendante montant. |
| `change_quality` | `String` | Non | observed_change / scheduled_boundary / incomplete_pair / missing_continuity. |
| `calculation_status` | `String` | Non | ready / partial / blocked / not_applicable. |
| `status_reason` | `Nullable(String)` | Oui | Cause précise stable ; NULL si aucune dépendance manquante. |

**Transformation spécifiée :**

1. Comparer périodes consécutives de même ligne, pas toutes versions entre elles.
2. Candidat si montant OU activité/période change ; delta0 gratuité conservé.
3. Ajouter bornes service même sans nouvelle version CDC ; échéance planifiée différente de réalisation prouvée.
4. Dédupliquer mêmes déclencheurs ; aucun candidat automatiquement New/churn.
5. Table explicative : mouvements du case calculés aux clôtures société.

**Jointures / cardinalités :** Avant/après N:0..1 par rôle même ligne/run ; aucune continuité arbitraire entre line_id.

**Physique, histoire et reprise :** table incrémentale append, MergeTree, unique_key=record_version_key, on_schema_change=fail, full_refresh=false, inserts_only non défini, recomposition COMPLETE de l’histoire disponible pour un manifeste immuable, anti-jointure (model_run_id,record_key) ; ORDER BY (model_run_id,tenant_id,line_id,subscription_change_key). Réexécution du même run = aucune copie ; reprise partielle complète les clés absentes sans changer le payload existant. Nouvelle empreinte d’entrée/code/règle = nouvelle révision entière. Aucune limite à hier ni watermark métier dans ce modèle. Mono-écrivain ; partition_by non défini, aucune TTL détaillée sans décision ; query_settings join_use_nulls=1. Avant anti-jointure, comparer row_hash de toute clé/run déjà présente : divergence sous même identité bloque reprise ; puis compléter clés absentes. Publication après tests de structure ; manque métier connu donne mesureNULL et qualité, pas blocage automatique du run entier. Exécution manuelle et fraîcheur de capture/publiée D29, sans SLA automatique.

**Tests / acceptation :** unicité/non-NULL des clés physiques, row_hash déterministe et un seul payload par clé/run ; Déclencheur unique ; activité sans delta conservée. Changement title seul ne produit pas mouvement financier. Défaut de grain, jointure ou réconciliation : ERROR et publication bloquée. Manque connu documenté : valeur NULL et statut, WARN si descriptif, KPI indisponible s’il en dépend.

**Limites / dépendances :** Continuité et dates d’effet corrections inconnues ; CDC ne certifie pas effet économique.


<a id="int_subscription_month_end"></a>

### `int_subscription_month_end`

**Règle finale v0.2 :** Construire les clôtures jusqu’à septembre2026 inclus (borne exclusive2026-09-30T22:00Z) selon D16 ; ne pas déduire octobre du jour d’exécution. EUR D20 autorise la somme officielle des lignes connues. Une première clôture non comparable ou une ligne censurée reste NULL ; absence avant naissance seulement si preuve fiable. Ne pas globalement bloquer pour une hypothèse de couverture/devise désormais définie.

**Grain métier :** Ligne connue × fin de mois, contribution observable ou inconnue explicite. **Grain physique :** (model_run_id,record_key) ; record_key=subscription_month_key.

**Amont exact :** `{{ ref('int_subscription_periods') }}`, `{{ ref('dim_date') }}`. **Destination :** `dwh_revenue.int_subscription_month_end`, `dbt/models/intermediate/revenue/int_subscription_month_end.sql`, YAML `dbt/models/intermediate/revenue/_models.yml`.

| Colonne | Type ClickHouse | Nullable | Origine, formule, contraintes |
|---|---|---|---|
| `model_run_id` | `String` | Non | Empreinte SHA256 commune de la recomposition : manifeste des entrées figées, code, référentiels et paramètres ; fournie par orchestration, identique dans tout le DAG. |
| `record_key` | `String` | Non | Identité String H(tuple du grain décrit, domaine/version explicite), sans model_run_id ; égale la clé de grain lorsque cette dernière est déjà hashée. dim_date utilise H(calendar_date), jamais date_key UInt32 brut. |
| `record_version_key` | `String` | Non | H(model_run_id,record_key) ; unicité physique de la révision du modèle. |
| `row_hash` | `String` | Non | H(tuple ordonné de toutes les colonnes métier de la fiche, NULL et types préservés) ; exclut les métadonnées de calcul. |
| `calculated_at` | `DateTime64(3,'UTC')` | Non | Instant de calcul du lot ; fixe pour un même model_run_id, jamais utilisé comme événement métier. |
| `rule_version` | `String` | Non | Empreinte immuable du code et des règles appliquées ; dérivée du manifeste du lot. |
| `input_cutoff_at` | `DateTime64(3,'UTC')` | Non | Date limite de connaissance de la recomposition ; les entrées exactes sont figées par le manifeste, pas par ce timestamp seul. |
| `source_published_at` | `Nullable(DateTime64(3,'UTC'))` | Oui | Maximum de publication CDC des versions contribuant à la ligne ; NULL pour un référentiel exclusivement généré. Les entrées de règles non fournies proviennent du futur dbt/config/case_rules.yml fusionné dans vars, sans seed ou source implicite. Ce maximum ne remplace aucune date métier. |
| `source_version_keys` | `Array(String)` | Non | Clés des versions sources contributrices, triées et sans répétition ; union des lignages amont. Liste vide pour une ligne exclusivement générée. |
| `subscription_month_key` | `String` | Non | H(subscription_key,month_date). |
| `tenant_id` | `String` | Non | Tenant. |
| `subscription_key` | `String` | Non | Identité ligne. |
| `line_id` | `Int64` | Non | ID ligne. |
| `line_created_at` | `Nullable(DateTime64(3,'UTC'))` | Oui | Identité ligne issue de int_subscription_periods, indépendamment du succès de la jointure à une période de clôture. |
| `is_creation_date_reliable` | `Bool` | Non | true seulement si création nonNULL constante entre versions, aucun CDC antérieur à cette création et aucun début de service antérieur contradictoire ; false sinon, pas de correction de la source. |
| `is_before_creation` | `Nullable(Bool)` | Oui | Avant la création prouvée à la clôture ; NULL si preuve insuffisante. Une date contradictoire ne prouve aucune absence. |
| `project_id` | `Nullable(Int64)` | Oui | Projet à clôture. |
| `company_id` | `Nullable(Int64)` | Oui | Société à clôture. |
| `company_key` | `Nullable(String)` | Oui | Identité société. |
| `company_version_key` | `Nullable(String)` | Oui | Version société à clôture. |
| `month_date` | `Date` | Non | Premier jour mois Paris. |
| `month_end_date` | `Date` | Non | Dernier jour mois Paris. |
| `closing_exclusive_at` | `DateTime64(3,'UTC')` | Non | Minuit Paris premier jour suivant converti UTC, photo juste avant. |
| `closing_date_key` | `UInt32` | Non | YYYYMMDD de month_end_date. |
| `source_subscription_period_key` | `Nullable(String)` | Oui | Période observée à clôture ; NULL non observable. |
| `is_observable` | `Nullable(Bool)` | Oui | Versions/liens nécessaires connus à clôture. |
| `is_active` | `Nullable(Bool)` | Oui | État1+période ; indépendant MRR>0. |
| `quantity` | `Nullable(Decimal(38,4))` | Oui | Quantité source. |
| `unit_monthly_price` | `Nullable(Decimal(38,4))` | Oui | Prix mensuel unitaire. |
| `line_monthly_amount` | `Nullable(Decimal(38,4))` | Oui | Montant mensuel total. |
| `candidate_active_mrr` | `Nullable(Decimal(38,4))` | Oui | Montant ligne actif ;0 si inactif prouvé ;NULL si inconnu. |
| `sum_active_mrr` | `Nullable(Decimal(38,4))` | Oui | Somme officielle des lignes admissibles en EUR sous hypothèses D16/D20 ;NULL si activité/montant ou inventaire requis inconnus, sans prorata. |
| `currency_code` | `Nullable(String)` | Oui | EUR par hypothèse explicite du case D20 ; cette devise ne prouve ni mensualité ni engagement du montant commercial. |
| `monetary_status` | `String` | Non | ready / currency_unconfirmed / missing_amount / unknown_activity. |
| `is_history_complete` | `Nullable(Bool)` | Oui | Couverture clôture/liens déclarée. |
| `calculation_status` | `String` | Non | ready / partial / blocked / not_applicable. |
| `status_reason` | `Nullable(String)` | Oui | Cause précise stable ; NULL si aucune dépendance manquante. |

**Transformation spécifiée :**

1. Générer mois jusqu’à dernière clôture entièrement passée au cutoff ; pas photo future du mois en cours.
2. Grille ligne×mois : si aucune période observable et création fiable postérieure ou égale à C, absence prouvée avant création : is_before_creation=true,is_observable=true,is_active=false,candidate_active_mrr=0 ; cette ligne ne contribue pas aux inconnus avant sa naissance. Si créée avant C mais première observation tardive, activité et MRR restent NULL. Une création contradictoire avec une publication ou un début de service ne prouve pas absence : ne pas produire de zéro. Une période réellement observée reste évaluée selon état et dates, indépendamment de ce défaut de création.
3. État juste avant C=closing_exclusive_at : valid_from_at<C et (fin NULL ou valid_to_at>=C). Version publiée à C exclue.
4. Activité : état 1 et service_started_at<C, service_end_exclusive_at>=C ou NULL ; début/état inconnu→NULL. FinNULL=pas de fin renseignée.
5. Candidat sans prorata ; devise non confirmée→sum_active_mrr officielNULL, candidattraçable.
6. Suppression sans preuve finmétier→unknown_activity, pas churnautomatique.

**Jointures / cardinalités :** Ligne/mois→période N:0..1 ; calendrier N:1 même run. Sommes société après ce grain garanti.

**Physique, histoire et reprise :** table incrémentale append, MergeTree, unique_key=record_version_key, on_schema_change=fail, full_refresh=false, inserts_only non défini, recomposition COMPLETE de l’histoire disponible pour un manifeste immuable, anti-jointure (model_run_id,record_key) ; ORDER BY (model_run_id,tenant_id,month_date,line_id). Réexécution du même run = aucune copie ; reprise partielle complète les clés absentes sans changer le payload existant. Nouvelle empreinte d’entrée/code/règle = nouvelle révision entière. Aucune limite à hier ni watermark métier dans ce modèle. Mono-écrivain ; partition_by non défini, aucune TTL détaillée sans décision ; query_settings join_use_nulls=1. Avant anti-jointure, comparer row_hash de toute clé/run déjà présente : divergence sous même identité bloque reprise ; puis compléter clés absentes. Publication après tests de structure ; manque métier connu donne mesureNULL et qualité, pas blocage automatique du run entier. Exécution manuelle et fraîcheur de capture/publiée D29, sans SLA automatique.

**Tests / acceptation :** unicité/non-NULL des clés physiques, row_hash déterministe et un seul payload par clé/run ; Unique ligne/mois ; aucune version future. Dernierjour fin inclus,début mois suivant exclu ;NULLnon observable distinct0 ;0 actif conserve true. Défaut de grain, jointure ou réconciliation : ERROR et publication bloquée. Manque connu documenté : valeur NULL et statut, WARN si descriptif, KPI indisponible s’il en dépend.

**Limites / dépendances :** EUR et complétude de case sont des hypothèses D16/D20 ; les lacunes individuelles restent explicites.



**Preuve avant création** : une date CRM seule ne réécrit pas un abonnement rétroactif. La création doit être cohérente avec toutes les versions et dates de service. Le contrôle complémentaire Q12 a trouvé194/214 créations postérieures à une publication : ce défaut de chronologie reste signalé et interdit seulement cette inférence d’absence ; il ne supprime pas une période observée ni ses contributions admissibles.

<a id="int_client_activity_context"></a>

### `int_client_activity_context`

**Règle finale v0.2 :** D27 : first_proven uniquement si activation et absence d’activité antérieure sont établies sur une couverture suffisante ; return_proven si activité antérieure prouvée avant un churn ; unknown sinon. Première clôture active observée n’est pas automatiquement première acquisition. Net financier des entrants conserve les retours même si ce statut est unknown. Couverture de case/EUR D16/D20 ne suppriment pas les inconnus individuels.

**Grain métier :** Société × mois, comparaison de deux clôtures. **Grain physique :** (model_run_id,record_key) ; record_key=client_context_key.

**Amont exact :** `{{ ref('int_subscription_month_end') }}`, `{{ ref('int_subscription_changes') }}`. **Destination :** `dwh_revenue.int_client_activity_context`, `dbt/models/intermediate/revenue/int_client_activity_context.sql`, YAML `dbt/models/intermediate/revenue/_models.yml`.

| Colonne | Type ClickHouse | Nullable | Origine, formule, contraintes |
|---|---|---|---|
| `model_run_id` | `String` | Non | Empreinte SHA256 commune de la recomposition : manifeste des entrées figées, code, référentiels et paramètres ; fournie par orchestration, identique dans tout le DAG. |
| `record_key` | `String` | Non | Identité String H(tuple du grain décrit, domaine/version explicite), sans model_run_id ; égale la clé de grain lorsque cette dernière est déjà hashée. dim_date utilise H(calendar_date), jamais date_key UInt32 brut. |
| `record_version_key` | `String` | Non | H(model_run_id,record_key) ; unicité physique de la révision du modèle. |
| `row_hash` | `String` | Non | H(tuple ordonné de toutes les colonnes métier de la fiche, NULL et types préservés) ; exclut les métadonnées de calcul. |
| `calculated_at` | `DateTime64(3,'UTC')` | Non | Instant de calcul du lot ; fixe pour un même model_run_id, jamais utilisé comme événement métier. |
| `rule_version` | `String` | Non | Empreinte immuable du code et des règles appliquées ; dérivée du manifeste du lot. |
| `input_cutoff_at` | `DateTime64(3,'UTC')` | Non | Date limite de connaissance de la recomposition ; les entrées exactes sont figées par le manifeste, pas par ce timestamp seul. |
| `source_published_at` | `Nullable(DateTime64(3,'UTC'))` | Oui | Maximum de publication CDC des versions contribuant à la ligne ; NULL pour un référentiel exclusivement généré. Les entrées de règles non fournies proviennent du futur dbt/config/case_rules.yml fusionné dans vars, sans seed ou source implicite. Ce maximum ne remplace aucune date métier. |
| `source_version_keys` | `Array(String)` | Non | Clés des versions sources contributrices, triées et sans répétition ; union des lignages amont. Liste vide pour une ligne exclusivement générée. |
| `client_context_key` | `String` | Non | H(company_key,month_date). |
| `tenant_id` | `String` | Non | Tenant. |
| `company_key` | `String` | Non | Société résolue ; orphelins contrôlés, pas société fictive. |
| `company_id` | `Int64` | Non | ID société. |
| `company_version_key` | `Nullable(String)` | Oui | Version société à clôture courante. |
| `month_date` | `Date` | Non | Mois étudié. |
| `month_end_date` | `Date` | Non | Clôture courante. |
| `previous_month_end_date` | `Date` | Non | Clôture précédente. |
| `is_active_before` | `Nullable(Bool)` | Oui | Au moins une ligne active ;false seulement inventaire complet sansactive ;sinon NULL. |
| `is_active_after` | `Nullable(Bool)` | Oui | Même logique après. |
| `nb_active_lines_before` | `Nullable(UInt64)` | Oui | Nombre lignes actives avant si connu. |
| `nb_active_lines_after` | `Nullable(UInt64)` | Oui | Nombre lignes actives après. |
| `candidate_mrr_before` | `Nullable(Decimal(38,4))` | Oui | Somme candidats avant si toutes contributions nécessaires connues. |
| `candidate_mrr_after` | `Nullable(Decimal(38,4))` | Oui | Somme candidats après sans ignorer NULL. |
| `mrr_before` | `Nullable(Decimal(38,4))` | Oui | Somme officielle avant devise prouvée. |
| `mrr_after` | `Nullable(Decimal(38,4))` | Oui | Somme officielle après devise prouvée. |
| `nb_expected_lines_before` | `UInt64` | Non | Nombre de lignes candidates connues attendues avant ; la couverture source complète reste une déclaration séparée. |
| `nb_expected_lines_after` | `UInt64` | Non | Nombre de lignes candidates connues attendues après. |
| `nb_known_active_states_before` | `UInt64` | Non | Nombre de lignes dont is_active est évalué avant, sans compter NULL comme false. |
| `nb_known_active_states_after` | `UInt64` | Non | Même compte après. |
| `nb_known_mrr_lines_before` | `UInt64` | Non | Nombre de contributions monétaires requises connues avant. |
| `nb_known_mrr_lines_after` | `UInt64` | Non | Même compte après. |
| `nb_uncalculable_lines_before` | `UInt64` | Non | Lignes activité/montant/rattachement inconnu avant. |
| `nb_uncalculable_lines_after` | `UInt64` | Non | Même compte après. |
| `first_known_active_date` | `Nullable(Date)` | Oui | Première clôture active observée, pas activation réelle certaine. |
| `first_acquisition_status` | `String` | Non | first_proven / return_proven / unknown. |
| `is_history_complete` | `Nullable(Bool)` | Oui | Deux clôtures et inventaires déclarés complets. |
| `is_comparable` | `Nullable(Bool)` | Oui | Même périmètre/devise et deux clôtures observables. |
| `calculation_status` | `String` | Non | ready / partial / blocked / not_applicable. |
| `status_reason` | `Nullable(String)` | Oui | Cause précise stable ; NULL si aucune dépendance manquante. |

**Transformation spécifiée :**

1. Préagréger lignes par société/clôture avant join N/N−1, compter inconnues.
2. Union sociétés des deux clôtures, pas innerjoin perdant sortants.
3. Au moins une ligne active prouvée ⇒ société active même si d’autres lignes ont une activité inconnue. Aucune active + au moins une activité inconnue ⇒ société active NULL. False uniquement si toutes les lignes sont évaluables inactives ET couverture permettant prouver absence. Cette règle booléenne ne rend pas le montant connu : MRR exige toutes contributions requises connues et compteurs expected/known égaux.
4. sum ignorant NULL interdit comme totalcomplet :contribution requise inconnue→total officielNULL.
5. Société inactive prouvée souscouverture complète→MRR nul ;absence observation≠0.
6. Changements source diagnostic préagrégé, jamais join détail multipliant totaux.

**Pseudocode normatif de la transformation :**

```text
Préagréger par société/clôture ; aucune jointure au détail des lignes après cette étape.
is_active :=
  true si au moins une ligne active prouvée ;
  NULL sinon si au moins une activité inconnue OU couverture ne prouvant pas absence ;
  false sinon (toutes les lignes évaluables inactives, inventaire couvert).
mrr :=
  0 si société inactive prouvée et inventaire complet ;
  somme des contributions requises si chaque contribution requise est connue et devise compatible ;
  NULL sinon.
La connaissance du booléen actif n'implique pas connaissance du montant.
Joindre les agrégats N et N-1 sur l'union des sociétés des deux clôtures.
```

**Jointures / cardinalités :** Clôtures société avant/après 1:1 tenant/company ;diagnostic N:1 aprèsagrégation, jamais totaux par abonnement.

**Physique, histoire et reprise :** table incrémentale append, MergeTree, unique_key=record_version_key, on_schema_change=fail, full_refresh=false, inserts_only non défini, recomposition COMPLETE de l’histoire disponible pour un manifeste immuable, anti-jointure (model_run_id,record_key) ; ORDER BY (model_run_id,tenant_id,month_date,company_key). Réexécution du même run = aucune copie ; reprise partielle complète les clés absentes sans changer le payload existant. Nouvelle empreinte d’entrée/code/règle = nouvelle révision entière. Aucune limite à hier ni watermark métier dans ce modèle. Mono-écrivain ; partition_by non défini, aucune TTL détaillée sans décision ; query_settings join_use_nulls=1. Avant anti-jointure, comparer row_hash de toute clé/run déjà présente : divergence sous même identité bloque reprise ; puis compléter clés absentes. Publication après tests de structure ; manque métier connu donne mesureNULL et qualité, pas blocage automatique du run entier. Exécution manuelle et fraîcheur de capture/publiée D29, sans SLA automatique.

**Tests / acceptation :** unicité/non-NULL des clés physiques, row_hash déterministe et un seul payload par clé/run ; Unique société/mois ;multi-lignes ne multiplientpas société. Actif0 conservé ;aucuneactive+ligneinconnue→activitéNULL. Premièreclôtureobservée pas acquisition automatique niMRR début égal à zéro. Défaut de grain, jointure ou réconciliation : ERROR et publication bloquée. Manque connu documenté : valeur NULL et statut, WARN si descriptif, KPI indisponible s’il en dépend.

**Limites / dépendances :** D16/D20 fixent couverture de case et devise ; inventaire ou activité réellement inconnus bloquent la contribution affectée ; premières acquisitions selon D27.


<a id="int_mrr_movements"></a>

### `int_mrr_movements`

**Règle finale v0.2 :** D16/D20 rendent applicable la réconciliation en EUR pour deux clôtures individuelles observables. New=entrants dont retours ; Upsell=hausse nette des restants ; un entrant n’est pas automatiquement une première acquisition D27. Inactif→inactif comparable=stable/composantes0. Conserver la classification unknown si données requises manquantes.

**Grain métier :** Société × mois × composante nette ; stable/inconnu conservés pour comptages clients. **Grain physique :** (model_run_id,record_key) ; record_key=movement_contribution_key.

**Amont exact :** `{{ ref('int_client_activity_context') }}`, `{{ ref('int_subscription_changes') }}`, `{{ ref('int_crm_identity_links') }}`. **Destination :** `dwh_revenue.int_mrr_movements`, `dbt/models/intermediate/revenue/int_mrr_movements.sql`, YAML `dbt/models/intermediate/revenue/_models.yml`.

| Colonne | Type ClickHouse | Nullable | Origine, formule, contraintes |
|---|---|---|---|
| `model_run_id` | `String` | Non | Empreinte SHA256 commune de la recomposition : manifeste des entrées figées, code, référentiels et paramètres ; fournie par orchestration, identique dans tout le DAG. |
| `record_key` | `String` | Non | Identité String H(tuple du grain décrit, domaine/version explicite), sans model_run_id ; égale la clé de grain lorsque cette dernière est déjà hashée. dim_date utilise H(calendar_date), jamais date_key UInt32 brut. |
| `record_version_key` | `String` | Non | H(model_run_id,record_key) ; unicité physique de la révision du modèle. |
| `row_hash` | `String` | Non | H(tuple ordonné de toutes les colonnes métier de la fiche, NULL et types préservés) ; exclut les métadonnées de calcul. |
| `calculated_at` | `DateTime64(3,'UTC')` | Non | Instant de calcul du lot ; fixe pour un même model_run_id, jamais utilisé comme événement métier. |
| `rule_version` | `String` | Non | Empreinte immuable du code et des règles appliquées ; dérivée du manifeste du lot. |
| `input_cutoff_at` | `DateTime64(3,'UTC')` | Non | Date limite de connaissance de la recomposition ; les entrées exactes sont figées par le manifeste, pas par ce timestamp seul. |
| `source_published_at` | `Nullable(DateTime64(3,'UTC'))` | Oui | Maximum de publication CDC des versions contribuant à la ligne ; NULL pour un référentiel exclusivement généré. Les entrées de règles non fournies proviennent du futur dbt/config/case_rules.yml fusionné dans vars, sans seed ou source implicite. Ce maximum ne remplace aucune date métier. |
| `source_version_keys` | `Array(String)` | Non | Clés des versions sources contributrices, triées et sans répétition ; union des lignages amont. Liste vide pour une ligne exclusivement générée. |
| `movement_contribution_key` | `String` | Non | H(company_key,month_date,movement_kind). |
| `tenant_id` | `String` | Non | Tenant. |
| `client_context_key` | `String` | Non | Contexte société/mois. |
| `company_id` | `Int64` | Non | ID société. |
| `company_key` | `String` | Non | Identité société. |
| `company_version_key` | `Nullable(String)` | Oui | Version à clôture. |
| `month_date` | `Date` | Non | Mois. |
| `month_end_date` | `Date` | Non | Clôture courante. |
| `previous_month_end_date` | `Date` | Non | Clôture précédente. |
| `movement_kind` | `String` | Non | new / upsell / departure / contraction / stable / unknown. |
| `new_mrr_component` | `Nullable(String)` | Oui | New entrants/retours ;Upsell hausse restants ;NULL autres. |
| `sum_new_mrr` | `Nullable(Decimal(38,4))` | Oui | MRR après entrant ;max(après−avant,0) hausse restant ;NULL noncomparable. Aucune ligne total en plus. |
| `sum_departure_mrr` | `Nullable(Decimal(38,4))` | Oui | MRR avant sortant ;0 autres cas comparables. |
| `sum_contraction_mrr` | `Nullable(Decimal(38,4))` | Oui | max(avant−après,0) restant baisse ;0 autres cas comparables. |
| `sum_candidate_new_mrr` | `Nullable(Decimal(38,4))` | Oui | Mêmeformule sur candidats,diagnostic devise inconnue. |
| `sum_candidate_departure_mrr` | `Nullable(Decimal(38,4))` | Oui | Départs candidats. |
| `sum_candidate_contraction_mrr` | `Nullable(Decimal(38,4))` | Oui | Baisses candidates. |
| `is_portfolio_entrant` | `Nullable(Bool)` | Oui | Actifaprès/inactifavant,retours inclus. |
| `is_departure` | `Nullable(Bool)` | Oui | Actifavant/inactifaprès. |
| `is_contraction` | `Nullable(Bool)` | Oui | Actifdeux clôtures et baissenette. |
| `is_active_before` | `Nullable(Bool)` | Oui | Activitéavant. |
| `is_active_after` | `Nullable(Bool)` | Oui | Activitéaprès. |
| `first_acquisition_status` | `String` | Non | Statut contexte,non déduit entrant seul. |
| `is_comparable` | `Nullable(Bool)` | Oui | Deux clôtures/périmètre/devise compatibles. |
| `commercial_link_status` | `String` | Non | not_required_for_financial_classification / proven / missing. |
| `source_lineage_status` | `String` | Non | Clôtures et lignages expliquent montant sans le répéter par ligne. |
| `calculation_status` | `String` | Non | ready / partial / blocked / not_applicable. |
| `status_reason` | `Nullable(String)` | Oui | Cause précise stable ; NULL si aucune dépendance manquante. |

**Transformation spécifiée :**

1. Classer entrants/sortants/restants depuis activité,indépendamment signeMRR.
2. Comparer total de chaque société ;compensation de ses lignes avant classification,aucune compensation entre sociétés.
3. New MRR=New entrants/retours+Upsell hausse nette des restants ;aucun ajout Expansion supplémentaire.
4. Départs+contractions pertes positives ;hausse d’une société ne réduit pas pertes d’une autre.
5. Ligne stable si variation nulle,inconnue sinon ;entrant/départ àMRR nul conserve compteurs clients.
6. Seulement deux clôtures :départ-retour intra-mois hors analyse,versions fines conservées.
7. Candidats peuvent réconcilier mathématiquement,mais officiels NULL avant devise confirmée.

**Cas normatif complémentaire** : deux clôtures comparables avec B=false et A=false donnent movement_kind=stable, contributions New/Upsell/départ/baisse=0 connus, is_entrant=false et is_departed=false ; ne pas classer cette absence d’activité comme unknown.

**Pseudocode normatif de la transformation :**

```text
Pour chaque société/mois comparable, B=actif avant, A=actif après :
  !B et !A : kind=stable ; New=Upsell=départ=baisse=0 ; entrant=false ; sortant=false.
  !B et A : kind=new ; New=MRR_après ; entrant=true (retour inclus).
  B et !A : kind=departure ; départ=MRR_avant ; sortant=true.
  B et A et après>avant : kind=upsell ; Upsell=après-avant.
  B et A et après<avant : kind=contraction ; baisse=avant-après.
  B et A et après=avant : kind=stable.
  activité/comparaison inconnue : kind=unknown ; contributions officielles NULL.
New_total := somme New+Upsell ; churn := somme départs+baisses.
Ne créer AUCUNE ligne de total en plus des composantes.
Faire la même décomposition sur candidats uniquement comme diagnostic clairement nommé,
sans convertir l'absence de devise en devise EUR présumée.
```

**Jointures / cardinalités :** Contexte→mouvement1:1 pour net du case ; pas de jointure de détail changements/lignes. Lien commercial annoté sans multiplication.

**Physique, histoire et reprise :** table incrémentale append, MergeTree, unique_key=record_version_key, on_schema_change=fail, full_refresh=false, inserts_only non défini, recomposition COMPLETE de l’histoire disponible pour un manifeste immuable, anti-jointure (model_run_id,record_key) ; ORDER BY (model_run_id,tenant_id,month_date,company_key,movement_kind). Réexécution du même run = aucune copie ; reprise partielle complète les clés absentes sans changer le payload existant. Nouvelle empreinte d’entrée/code/règle = nouvelle révision entière. Aucune limite à hier ni watermark métier dans ce modèle. Mono-écrivain ; partition_by non défini, aucune TTL détaillée sans décision ; query_settings join_use_nulls=1. Avant anti-jointure, comparer row_hash de toute clé/run déjà présente : divergence sous même identité bloque reprise ; puis compléter clés absentes. Publication après tests de structure ; manque métier connu donne mesureNULL et qualité, pas blocage automatique du run entier. Exécution manuelle et fraîcheur de capture/publiée D29, sans SLA automatique.

**Tests / acceptation :** unicité/non-NULL des clés physiques, row_hash déterministe et un seul payload par clé/run ; 100→150 restant donne Upsell50,churn0 ;entrée150 donne New150. +100/−40 même client donne Upsell60,churn0 ;perte40 autre client reste40. MRR après=avant+New total−départs−baisses quand comparable ;comptages réconciliés même avec MRR nul. Défaut de grain, jointure ou réconciliation : ERROR et publication bloquée. Manque connu documenté : valeur NULL et statut, WARN si descriptif, KPI indisponible s’il en dépend.

**Limites / dépendances :** Activité/devise/coverage inconnues bloquent officiels ;résidu inexpliqué jamais churn.


<a id="int_sales_objectives_month"></a>

### `int_sales_objectives_month`

**Règle finale v0.2 :** D22 : les4 métriques ciblent4/7,formation2 exclue ; joindre les cibles par source_segment/mois/metric, jamais répéter par dossier. ES sans BU résolue : actual/candidate/atteinteNULL, raison missing_team_mapping. KAM n’est pas agrégée à LA/SMB/ES et n’a pas de cible fictive. D13/D14 maintiennent réalisés monétaires non compatibles et démosNULL même si leur population est définie. Un global couvrant ES manquante resteNULL ; un sous-périmètre LA/SMB peut être consulté avec son libellé exact.

**Grain métier :** Mois × segment Sales × indicateur ; cible aprèsagrégation du réalisé. **Grain physique :** (model_run_id,record_key) ; record_key=objective_month_key.

**Amont exact :** `{{ ref('stg_ref_sales_targets') }}`, `{{ ref('fct_opportunity_event') }}`, `{{ ref('fct_opportunity_period') }}`, `{{ ref('fct_action') }}`, `{{ ref('dim_team') }}`, `{{ ref('dim_metric') }}`, `{{ ref('dim_date') }}`. **Destination :** `dwh_revenue.int_sales_objectives_month`, `dbt/models/intermediate/revenue/int_sales_objectives_month.sql`, YAML `dbt/models/intermediate/revenue/_models.yml`.

| Colonne | Type ClickHouse | Nullable | Origine, formule, contraintes |
|---|---|---|---|
| `model_run_id` | `String` | Non | Empreinte SHA256 commune de la recomposition : manifeste des entrées figées, code, référentiels et paramètres ; fournie par orchestration, identique dans tout le DAG. |
| `record_key` | `String` | Non | Identité String H(tuple du grain décrit, domaine/version explicite), sans model_run_id ; égale la clé de grain lorsque cette dernière est déjà hashée. dim_date utilise H(calendar_date), jamais date_key UInt32 brut. |
| `record_version_key` | `String` | Non | H(model_run_id,record_key) ; unicité physique de la révision du modèle. |
| `row_hash` | `String` | Non | H(tuple ordonné de toutes les colonnes métier de la fiche, NULL et types préservés) ; exclut les métadonnées de calcul. |
| `calculated_at` | `DateTime64(3,'UTC')` | Non | Instant de calcul du lot ; fixe pour un même model_run_id, jamais utilisé comme événement métier. |
| `rule_version` | `String` | Non | Empreinte immuable du code et des règles appliquées ; dérivée du manifeste du lot. |
| `input_cutoff_at` | `DateTime64(3,'UTC')` | Non | Date limite de connaissance de la recomposition ; les entrées exactes sont figées par le manifeste, pas par ce timestamp seul. |
| `source_published_at` | `Nullable(DateTime64(3,'UTC'))` | Oui | Maximum de publication CDC des versions contribuant à la ligne ; NULL pour un référentiel exclusivement généré. Les entrées de règles non fournies proviennent du futur dbt/config/case_rules.yml fusionné dans vars, sans seed ou source implicite. Ce maximum ne remplace aucune date métier. |
| `source_version_keys` | `Array(String)` | Non | Clés des versions sources contributrices, triées et sans répétition ; union des lignages amont. Liste vide pour une ligne exclusivement générée. |
| `objective_month_key` | `String` | Non | H(tenant_id,month_date,source_segment,metric_code). |
| `tenant_id` | `String` | Non | Var source_tenant_id=demo_crm,contexte explicite de ce jeu. |
| `month_date` | `Date` | Non | src_month_date,premierjourParis. |
| `month_end_date` | `Date` | Non | Dernierjourmois. |
| `closing_exclusive_at` | `DateTime64(3,'UTC')` | Non | MinuitParis mois suivant reconvertiUTC. |
| `source_segment` | `String` | Non | src_segment SMB/LA/ES. |
| `team_key` | `Nullable(String)` | Oui | Équipe si mappingunivoque. |
| `team_version_key` | `Nullable(String)` | Oui | Version à date pertinente. |
| `metric_code` | `String` | Non | src_indicator,quatre codes. |
| `metric_key` | `String` | Non | Identité dim_metric. |
| `metric_version_key` | `String` | Non | Version définition mesure. |
| `target_version_key` | `String` | Non | source_version_key captureobjectif choisie. |
| `target_value` | `Nullable(Decimal(38,4))` | Oui | src_target convertiDecimal,aucuneventilationpersonnelle. |
| `actual_value` | `Nullable(Decimal(38,4))` | Oui | RéaliséOFFICIEL compatible ;NULL sans preuves montant/unité/tenue. |
| `candidate_actual_value` | `Nullable(Decimal(38,4))` | Oui | Diagnostic réalisé source si possible,jamais substitutofficiel. |
| `value_unit` | `String` | Non | Unitémesure ;compatibilitécible/réalisé àprouver. |
| `variance_value` | `Nullable(Decimal(38,4))` | Oui | actual_value−target_value sicalculable/compatible. |
| `attainment_numerator` | `Nullable(Decimal(38,4))` | Oui | actual_value sicompatible. |
| `attainment_denominator` | `Nullable(Decimal(38,4))` | Oui | target_value sicompatible et>0 ;sinon NULL. |
| `attainment_rate` | `Nullable(Float64)` | Oui | actual/target si>0 etcompatible,sinon NULL. |
| `is_population_compatible` | `Nullable(Bool)` | Oui | Population/type/période/unité compatibles ;NULL sinondéfinies. |
| `nb_source_contributions` | `Nullable(UInt64)` | Oui | Contributionsdistinctes avant somme. |
| `nb_uncalculable_contributions` | `Nullable(UInt64)` | Oui | Contributionsrequises inconnues ;NULL si absence de preuve globale empêche de les dénombrer. |
| `is_month_closed` | `Bool` | Non | Clôtureexclusive<=cutoff. |
| `is_team_calculable` | `Bool` | Non | Mapping équipeunivoque. |
| `target_selection_status` | `String` | Non | capture_selected / ambiguous_target / missing_target. |
| `calculation_status` | `String` | Non | ready / partial / blocked / not_applicable. |
| `status_reason` | `Nullable(String)` | Oui | Cause précise stable ; NULL si aucune dépendance manquante. |

**Transformation spécifiée :**

1. Choisir une captureobjectif par clé selonmanifeste corrigé ;versionexacte conservée.
2. Préagréger chaque réalisé :génération/signature événementsdumois ;pondéré unepériode parbesoin justeavantclôture ;démos séancesréellesdistinctes.
3. Compter entréesinconnues pour éviter sumquiignoreNULL.
4. Sans preuve MRR signé ou naturecompatiblepipeline :actualetattainmentmonétairesNULL ;démos sanstenue→NULL,pas types 60/68.
5. Cible connue reste disponible ;cible nulle/manquante→taux NULL.
6. Filtrecanal/type sans cible ventilée rend comparaisonindisponible.
7. Pas sommepondéré intermois ;global recalculer ratio sommnumérateurs/sommdénominateurs compatibles,pas moyenne taux.

**Jointures / cardinalités :** Réaliséagrégé+cible 1:0..1 mois/segment/indicateur ;dimensions N:0..1 même run ;cible jamais répétée pardossier/action.

**Physique, histoire et reprise :** table incrémentale append, MergeTree, unique_key=record_version_key, on_schema_change=fail, full_refresh=false, inserts_only non défini, recomposition COMPLETE de l’histoire disponible pour un manifeste immuable, anti-jointure (model_run_id,record_key) ; ORDER BY (model_run_id,tenant_id,month_date,source_segment,metric_code). Réexécution du même run = aucune copie ; reprise partielle complète les clés absentes sans changer le payload existant. Nouvelle empreinte d’entrée/code/règle = nouvelle révision entière. Aucune limite à hier ni watermark métier dans ce modèle. Mono-écrivain ; partition_by non défini, aucune TTL détaillée sans décision ; query_settings join_use_nulls=1. Avant anti-jointure, comparer row_hash de toute clé/run déjà présente : divergence sous même identité bloque reprise ; puis compléter clés absentes. Publication après tests de structure ; manque métier connu donne mesureNULL et qualité, pas blocage automatique du run entier. Exécution manuelle et fraîcheur de capture/publiée D29, sans SLA automatique.

**Tests / acceptation :** unicité/non-NULL des clés physiques, row_hash déterministe et un seul payload par clé/run ; Cléunique ;quatre indicateurs selonréférence ;cible nonmultipliée par nombre de dossiers. NULLrequis bloqueofficiel ;cible nulle→NULL ;pas prorataobjectif ni cibleindividuelle. Défaut de grain, jointure ou réconciliation : ERROR et publication bloquée. Manque connu documenté : valeur NULL et statut, WARN si descriptif, KPI indisponible s’il en dépend.

**Limites / dépendances :** règles fixées par D16–D30 ; conserver les données non observables/invalides et les indisponibilités de preuve D13/D14/D28. Aucun arbitrage supplémentaire demandé.


## Faits — 9 vues historiques


<a id="fct_opportunity_period"></a>

### `fct_opportunity_period`

**Grain métier :** Opportunité × intervalle de contexte stable. **Clé :** period_key ; record_key=H(tuple du grain), identique à la clé hashée amont. **Grain de révision :** (model_run_id,record_key).

**Amont exact :** `{{ ref('int_opportunity_periods') }}`, `{{ ref('dim_date') }}`. **Destination :** `dtm_pipeline.fct_opportunity_period`, `dbt/models/marts/pipeline/fct_opportunity_period.sql`, YAML `dbt/models/marts/pipeline/_models.yml`.

| Colonne | Type ClickHouse | Nullable | Origine, formule, contraintes |
|---|---|---|---|
| `model_run_id` | `String` | Non | Métadonnée amont int_opportunity_periods.model_run_id ; row_hash recalculé sur le contrat final du fait si des colonnes techniques sont ajoutées. Empreinte SHA256 commune de la recomposition : manifeste des entrées figées, code, référentiels et paramètres ; fournie par orchestration, identique dans tout le DAG. |
| `record_key` | `String` | Non | Métadonnée amont int_opportunity_periods.record_key ; row_hash recalculé sur le contrat final du fait si des colonnes techniques sont ajoutées. Identité String H(tuple du grain décrit, domaine/version explicite), sans model_run_id ; égale la clé de grain lorsque cette dernière est déjà hashée. dim_date utilise H(calendar_date), jamais date_key UInt32 brut. |
| `record_version_key` | `String` | Non | Métadonnée amont int_opportunity_periods.record_version_key ; row_hash recalculé sur le contrat final du fait si des colonnes techniques sont ajoutées. H(model_run_id,record_key) ; unicité physique de la révision du modèle. |
| `row_hash` | `String` | Non | Métadonnée amont int_opportunity_periods.row_hash ; row_hash recalculé sur le contrat final du fait si des colonnes techniques sont ajoutées. H(tuple ordonné de toutes les colonnes métier de la fiche, NULL et types préservés) ; exclut les métadonnées de calcul. |
| `calculated_at` | `DateTime64(3,'UTC')` | Non | Métadonnée amont int_opportunity_periods.calculated_at ; row_hash recalculé sur le contrat final du fait si des colonnes techniques sont ajoutées. Instant de calcul du lot ; fixe pour un même model_run_id, jamais utilisé comme événement métier. |
| `rule_version` | `String` | Non | Métadonnée amont int_opportunity_periods.rule_version ; row_hash recalculé sur le contrat final du fait si des colonnes techniques sont ajoutées. Empreinte immuable du code et des règles appliquées ; dérivée du manifeste du lot. |
| `input_cutoff_at` | `DateTime64(3,'UTC')` | Non | Métadonnée amont int_opportunity_periods.input_cutoff_at ; row_hash recalculé sur le contrat final du fait si des colonnes techniques sont ajoutées. Date limite de connaissance de la recomposition ; les entrées exactes sont figées par le manifeste, pas par ce timestamp seul. |
| `source_published_at` | `Nullable(DateTime64(3,'UTC'))` | Oui | Métadonnée amont int_opportunity_periods.source_published_at ; row_hash recalculé sur le contrat final du fait si des colonnes techniques sont ajoutées. Maximum de publication CDC des versions contribuant à la ligne ; NULL pour un référentiel exclusivement généré. Les entrées de règles non fournies proviennent du futur dbt/config/case_rules.yml fusionné dans vars, sans seed ou source implicite. Ce maximum ne remplace aucune date métier. |
| `source_version_keys` | `Array(String)` | Non | Métadonnée amont int_opportunity_periods.source_version_keys ; row_hash recalculé sur le contrat final du fait si des colonnes techniques sont ajoutées. Clés des versions sources contributrices, triées et sans répétition ; union des lignages amont. Liste vide pour une ligne exclusivement générée. |
| `tenant_id` | `String` | Non | Projection explicite de int_opportunity_periods.tenant_id ; Identité du tenant src_tenant_id. |
| `opportunity_id` | `Int64` | Non | Projection explicite de int_opportunity_periods.opportunity_id ; src_id du besoin Boond. |
| `opportunity_key` | `String` | Non | Projection explicite de int_opportunity_periods.opportunity_key ; H(tenant_id,opportunity_id), identité stable intermodèles. |
| `period_key` | `String` | Non | Projection explicite de int_opportunity_periods.period_key ; H(opportunity_key,valid_from_at). |
| `visit_key` | `String` | Non | Projection explicite de int_opportunity_periods.visit_key ; Passage courant. |
| `valid_from_at` | `DateTime64(3,'UTC')` | Non | Projection explicite de int_opportunity_periods.valid_from_at ; Borne CDC/contexte incluse. |
| `valid_to_at` | `Nullable(DateTime64(3,'UTC'))` | Oui | Projection explicite de int_opportunity_periods.valid_to_at ; Borne suivante exclue. |
| `is_source_deleted` | `Bool` | Non | Projection explicite de int_opportunity_periods.is_source_deleted ; src_is_deleted, sélection des versions avant exclusion. |
| `created_at` | `Nullable(DateTime64(3,'UTC'))` | Oui | Projection explicite de int_opportunity_periods.created_at ; src_created_at ; pas antidatation de l’état. |
| `cohort_month` | `Nullable(Date)` | Oui | Projection explicite de int_opportunity_periods.cohort_month ; Mois de création Paris. |
| `stage_id` | `Nullable(Int64)` | Oui | Projection explicite de int_opportunity_periods.stage_id ; État source. |
| `stage_key` | `Nullable(String)` | Oui | Projection explicite de int_opportunity_periods.stage_key ; Identité étape. |
| `stage_version_key` | `Nullable(String)` | Oui | Projection explicite de int_opportunity_periods.stage_version_key ; Version dim_stage valable sur toute tranche. |
| `outcome_category` | `Nullable(String)` | Oui | Projection explicite de int_opportunity_periods.outcome_category ; Classe analytique, NULL si code non mappé. |
| `is_open` | `Nullable(Bool)` | Oui | Projection explicite de int_opportunity_periods.is_open ; Classe open ; suppression et inconnu distincts. |
| `company_id` | `Nullable(Int64)` | Oui | Projection explicite de int_opportunity_periods.company_id ; Société Boond au moment de référence. |
| `company_key` | `Nullable(String)` | Oui | Projection explicite de int_opportunity_periods.company_key ; H(tenant_id,company_id) si société connue. |
| `company_version_key` | `Nullable(String)` | Oui | Projection explicite de int_opportunity_periods.company_version_key ; Version dim_company à la date de référence ; jointure sur même run. |
| `sale_type_id` | `Nullable(Int64)` | Oui | Projection explicite de int_opportunity_periods.sale_type_id ; Type commercial de la version du besoin. |
| `sale_type_key` | `Nullable(String)` | Oui | Projection explicite de int_opportunity_periods.sale_type_key ; Identité stable du code type. |
| `sale_type_version_key` | `Nullable(String)` | Oui | Projection explicite de int_opportunity_periods.sale_type_version_key ; Version dim_sale_type au moment de référence. |
| `employee_id` | `Nullable(Int64)` | Oui | Projection explicite de int_opportunity_periods.employee_id ; Responsable principal Boond à la date pertinente. |
| `employee_key` | `Nullable(String)` | Oui | Projection explicite de int_opportunity_periods.employee_key ; Identité stable du responsable. |
| `employee_version_key` | `Nullable(String)` | Oui | Projection explicite de int_opportunity_periods.employee_version_key ; Version de dim_employee à la date pertinente. |
| `team_id` | `Nullable(Int64)` | Oui | Projection explicite de int_opportunity_periods.team_id ; Équipe businessunit seulement si attribution univoque. |
| `team_key` | `Nullable(String)` | Oui | Projection explicite de int_opportunity_periods.team_key ; Identité stable d’équipe ; NULL si ambiguë ou inconnue. |
| `team_version_key` | `Nullable(String)` | Oui | Projection explicite de int_opportunity_periods.team_version_key ; Version dim_team pertinente à la date. |
| `sales_segment` | `Nullable(String)` | Oui | Projection explicite de int_opportunity_periods.sales_segment ; SMB / LA / ES si mapping fourni ; NULL sinon. |
| `is_team_calculable` | `Bool` | Non | Projection explicite de int_opportunity_periods.is_team_calculable ; Vrai si une seule équipe est historiquement résolue ; KAM reste connue même sans segment de cible D23. |
| `acquisition_channel_key` | `Nullable(String)` | Oui | Projection explicite de int_opportunity_periods.acquisition_channel_key ; Canal officiel fixé à création ; NULL avant règle QM-02. |
| `channel_version_key` | `Nullable(String)` | Oui | Projection explicite de int_opportunity_periods.channel_version_key ; Version de dim_channel applicable à l’acquisition. |
| `channel_candidate_code` | `Nullable(String)` | Oui | Projection explicite de int_opportunity_periods.channel_candidate_code ; Code origine Boond à création, converti String ; candidat descriptif seulement. |
| `is_channel_calculable` | `Bool` | Non | Projection explicite de int_opportunity_periods.is_channel_calculable ; Vrai seulement si règle canal et mapping appliqués sans ambiguïté. |
| `attribution_status` | `String` | Non | Projection explicite de int_opportunity_periods.attribution_status ; resolved / missing_team_mapping / multiple_teams / missing_channel_rule ; détails conservés. |
| `pipeline_amount` | `Nullable(Decimal(38,4))` | Oui | Projection explicite de int_opportunity_periods.pipeline_amount ; src_estimated_amount_excluding_tax converti chaîne→Decimal(38,4), sans mensualisation. |
| `amount_basis` | `String` | Non | Projection explicite de int_opportunity_periods.amount_basis ; crm_estimated_unconfirmed tant que nature inconnue. |
| `currency_code` | `Nullable(String)` | Oui | Projection explicite de int_opportunity_periods.currency_code ; EUR par hypothèse explicite du case D20 ; cette devise ne prouve ni mensualité ni engagement du montant commercial. |
| `source_weighting_percent` | `Nullable(Int64)` | Oui | Projection explicite de int_opportunity_periods.source_weighting_percent ; src_weighting_percent descriptif. |
| `source_weighted_amount` | `Nullable(Decimal(38,4))` | Oui | Projection explicite de int_opportunity_periods.source_weighted_amount ; src_weighted_amount_excluding_tax descriptif. |
| `signature_probability` | `Nullable(Decimal(18,8))` | Oui | Projection explicite de int_opportunity_periods.signature_probability ; Coefficient de ref.stage_probabilities choisi selon D21 ; NULL seulement si état/segment non couvert, pas de fallback Boond. |
| `probability_version_key` | `Nullable(String)` | Oui | Projection explicite de int_opportunity_periods.probability_version_key ; Version ref si utilisée. |
| `weighted_pipeline_amount` | `Nullable(Decimal(38,4))` | Oui | Projection explicite de int_opportunity_periods.weighted_pipeline_amount ; Produit intermédiaire Decimal(38,12) à proba Decimal(18,8), contrôle dépassement et égalité exacte au cast retour depuis Decimal(38,4). Aucune perte d’échelle admise : sinon résultat NULL, insufficient_decimal_scale et publication de cette mesure bloquée jusqu’à migration de précision. Aucun arrondi intermédiaire ni double pondération. |
| `expected_close_at` | `Nullable(DateTime64(3,'UTC'))` | Oui | Projection explicite de int_opportunity_periods.expected_close_at ; src_closing_at saisi, pas signature réelle. |
| `stage_entered_at` | `Nullable(DateTime64(3,'UTC'))` | Oui | Projection explicite de int_opportunity_periods.stage_entered_at ; entered_at passage, NULL si censuré. |
| `stage_first_observed_at` | `DateTime64(3,'UTC')` | Non | Projection explicite de int_opportunity_periods.stage_first_observed_at ; Présence observée dans passage. |
| `stagnation_threshold_days` | `Nullable(Float64)` | Oui | Projection explicite de int_opportunity_periods.stagnation_threshold_days ; 21jours continus par défaut, dépassement strict>, paramétrable par étape/type D26 ; NULL uniquement si alerte explicitement désactivée. |
| `stagnant_from_at` | `Nullable(DateTime64(3,'UTC'))` | Oui | Projection explicite de int_opportunity_periods.stagnant_from_at ; Début passage + seuil en jours continus si connus. |
| `is_pipeline_eligible` | `Nullable(Bool)` | Oui | Projection explicite de int_opportunity_periods.is_pipeline_eligible ; true pour type4/7 et état ouvert D22/D30 ; false si explicitement hors population ; NULL si type/état source inconnu. |
| `source_opportunity_version_key` | `String` | Non | Projection explicite de int_opportunity_periods.source_opportunity_version_key ; Version source portant attributs. |
| `coverage_start_at` | `Nullable(DateTime64(3,'UTC'))` | Oui | Projection explicite de int_opportunity_periods.coverage_start_at ; Début déclaré. |
| `coverage_end_at` | `Nullable(DateTime64(3,'UTC'))` | Oui | Projection explicite de int_opportunity_periods.coverage_end_at ; Fin déclarée. |
| `is_history_complete` | `Nullable(Bool)` | Oui | Projection explicite de int_opportunity_periods.is_history_complete ; Complétude déclarée de la fenêtre. |
| `calculation_status` | `String` | Non | Projection explicite de int_opportunity_periods.calculation_status ; ready / partial / blocked / not_applicable. |
| `status_reason` | `Nullable(String)` | Oui | Projection explicite de int_opportunity_periods.status_reason ; Cause précise stable ; NULL si aucune dépendance manquante. |
| `created_date_key` | `Nullable(UInt32)` | Oui | Date Paris created_at ; NULL si inconnue. |
| `period_start_date_key` | `UInt32` | Non | Date Paris valid_from_at. |
| `expected_closing_date_key` | `Nullable(UInt32)` | Oui | Date Paris expected_close_at si dans calendrier ; date de prévision, pas signature. |
| `stage_entered_date_key` | `Nullable(UInt32)` | Oui | Date Paris stage_entered_at, NULL censurée. |

**Transformation / jointures :** Projection de toutes les colonnes amont énumérées ; dates de rôle depuis dim_date N:0..1 sur même run et calendar_date. Aucune jointure contacts/deals/responsabilités. Quand une date métier sort des bornes générées, conserver la date et mettre la clé Nullable à NULL avec statut ; ne pas allonger le calendrier jusqu’à une fin sentinelle2099. Les labels ne remplacent pas les clés. Aucun filtre vers le run publié dans ce fait : l’historique des runs reste consultable.

**Agrégation et usage :** À une date, sélectionner une période pertinente par opportunity_key avant exclusion des suppressions et filtre ouvert. Comptage opportunités par clé, Nb In demo par company_key distincte des dossiers état 24. Stocks non sommables entre dates ; ratio canal recalculé avec dénominateur filtré compatible.

**Matérialisation, histoire, reprise et fraîcheur :** vue dbt, une requête SELECT avec colonnes énumérées ; pas de stockage supplémentaire ni de stratégie incrémentale propre. La vue expose les révisions conservées dans son intermédiaire. Les jointures annexes portent toujours même model_run_id ; aucune relecture d’un ancien run avec dimensions actuelles. Recréation de vue idempotente ; source d’histoire inchangée. Exécution manuelle D29, sans SLA de production ; publication au rythme du lot validé, datasets sélectionnant int_publication. Aucune garantie de performance avant mesure.

**Tests / acceptation :** unicité/non-NULL de (model_run_id,record_key), correspondance exacte des clés/projections amont, relations dimensionnelles au bon run, aucune multiplication de contributions. Conservation du nombre de lignes et montants int→fct ; pas de fan-out date. Une société avec deux dossiers en Démo compte une seule société. Défaut de grain/cardinalité : ERROR, publication bloquée. Limite connue : NULL et statut sans inventer de chiffre.

**Limites / dépendances :** Mapping canal/équipes, coefficients et nature/devise de montant restent qualifiés.


<a id="fct_stage_visit"></a>

### `fct_stage_visit`

**Grain métier :** Opportunité × passage continu dans une étape. **Clé :** visit_key ; record_key=H(tuple du grain), identique à la clé hashée amont. **Grain de révision :** (model_run_id,record_key).

**Amont exact :** `{{ ref('int_opportunity_stage_visits') }}`, `{{ ref('int_opportunity_periods') }}`, `{{ ref('dim_stage') }}`, `{{ ref('dim_company') }}`, `{{ ref('dim_sale_type') }}`, `{{ ref('dim_channel') }}`, `{{ ref('dim_employee') }}`, `{{ ref('dim_team') }}`, `{{ ref('dim_date') }}`. **Destination :** `dtm_pipeline.fct_stage_visit`, `dbt/models/marts/pipeline/fct_stage_visit.sql`, YAML `dbt/models/marts/pipeline/_models.yml`.

| Colonne | Type ClickHouse | Nullable | Origine, formule, contraintes |
|---|---|---|---|
| `model_run_id` | `String` | Non | Métadonnée amont int_opportunity_stage_visits.model_run_id ; row_hash recalculé sur le contrat final du fait si des colonnes techniques sont ajoutées. Empreinte SHA256 commune de la recomposition : manifeste des entrées figées, code, référentiels et paramètres ; fournie par orchestration, identique dans tout le DAG. |
| `record_key` | `String` | Non | Métadonnée amont int_opportunity_stage_visits.record_key ; row_hash recalculé sur le contrat final du fait si des colonnes techniques sont ajoutées. Identité String H(tuple du grain décrit, domaine/version explicite), sans model_run_id ; égale la clé de grain lorsque cette dernière est déjà hashée. dim_date utilise H(calendar_date), jamais date_key UInt32 brut. |
| `record_version_key` | `String` | Non | Métadonnée amont int_opportunity_stage_visits.record_version_key ; row_hash recalculé sur le contrat final du fait si des colonnes techniques sont ajoutées. H(model_run_id,record_key) ; unicité physique de la révision du modèle. |
| `row_hash` | `String` | Non | Métadonnée amont int_opportunity_stage_visits.row_hash ; row_hash recalculé sur le contrat final du fait si des colonnes techniques sont ajoutées. H(tuple ordonné de toutes les colonnes métier de la fiche, NULL et types préservés) ; exclut les métadonnées de calcul. |
| `calculated_at` | `DateTime64(3,'UTC')` | Non | Métadonnée amont int_opportunity_stage_visits.calculated_at ; row_hash recalculé sur le contrat final du fait si des colonnes techniques sont ajoutées. Instant de calcul du lot ; fixe pour un même model_run_id, jamais utilisé comme événement métier. |
| `rule_version` | `String` | Non | Métadonnée amont int_opportunity_stage_visits.rule_version ; row_hash recalculé sur le contrat final du fait si des colonnes techniques sont ajoutées. Empreinte immuable du code et des règles appliquées ; dérivée du manifeste du lot. |
| `input_cutoff_at` | `DateTime64(3,'UTC')` | Non | Métadonnée amont int_opportunity_stage_visits.input_cutoff_at ; row_hash recalculé sur le contrat final du fait si des colonnes techniques sont ajoutées. Date limite de connaissance de la recomposition ; les entrées exactes sont figées par le manifeste, pas par ce timestamp seul. |
| `source_published_at` | `Nullable(DateTime64(3,'UTC'))` | Oui | Métadonnée amont int_opportunity_stage_visits.source_published_at ; row_hash recalculé sur le contrat final du fait si des colonnes techniques sont ajoutées. Maximum de publication CDC des versions contribuant à la ligne ; NULL pour un référentiel exclusivement généré. Les entrées de règles non fournies proviennent du futur dbt/config/case_rules.yml fusionné dans vars, sans seed ou source implicite. Ce maximum ne remplace aucune date métier. |
| `source_version_keys` | `Array(String)` | Non | Métadonnée amont int_opportunity_stage_visits.source_version_keys ; row_hash recalculé sur le contrat final du fait si des colonnes techniques sont ajoutées. Clés des versions sources contributrices, triées et sans répétition ; union des lignages amont. Liste vide pour une ligne exclusivement générée. |
| `tenant_id` | `String` | Non | Projection explicite de int_opportunity_stage_visits.tenant_id ; Identité du tenant src_tenant_id. |
| `opportunity_id` | `Int64` | Non | Projection explicite de int_opportunity_stage_visits.opportunity_id ; src_id du besoin Boond. |
| `opportunity_key` | `String` | Non | Projection explicite de int_opportunity_stage_visits.opportunity_key ; H(tenant_id,opportunity_id), identité stable intermodèles. |
| `visit_key` | `String` | Non | Projection explicite de int_opportunity_stage_visits.visit_key ; H(opportunity_key,first_observed_at,first_source_version_key). |
| `stage_id` | `Nullable(Int64)` | Oui | Projection explicite de int_opportunity_stage_visits.stage_id ; src_state_id du groupe consécutif. |
| `visit_rank` | `UInt32` | Non | Projection explicite de int_opportunity_stage_visits.visit_rank ; Rang chronologique, jamais ordre des codes. |
| `first_observed_at` | `DateTime64(3,'UTC')` | Non | Projection explicite de int_opportunity_stage_visits.first_observed_at ; Première publication prouvant présence dans cet état. |
| `last_observed_at` | `DateTime64(3,'UTC')` | Non | Projection explicite de int_opportunity_stage_visits.last_observed_at ; Dernière publication du même passage. |
| `entered_at` | `Nullable(DateTime64(3,'UTC'))` | Oui | Projection explicite de int_opportunity_stage_visits.entered_at ; Entrée datée ou proxy CDC d’une transition observée ; NULL premier état avancé censuré. |
| `exited_at` | `Nullable(DateTime64(3,'UTC'))` | Oui | Projection explicite de int_opportunity_stage_visits.exited_at ; Transition suivante observée ; NULL en cours/suppression sans sortie métier. |
| `observation_ended_at` | `Nullable(DateTime64(3,'UTC'))` | Oui | Projection explicite de int_opportunity_stage_visits.observation_ended_at ; Fin technique d’observation, distincte de exited_at. |
| `previous_stage_id` | `Nullable(Int64)` | Oui | Projection explicite de int_opportunity_stage_visits.previous_stage_id ; État précédent observé hors lacune. |
| `next_stage_id` | `Nullable(Int64)` | Oui | Projection explicite de int_opportunity_stage_visits.next_stage_id ; État suivant observé hors lacune. |
| `first_source_version_key` | `String` | Non | Projection explicite de int_opportunity_stage_visits.first_source_version_key ; Version source initiale du groupe. |
| `last_source_version_key` | `String` | Non | Projection explicite de int_opportunity_stage_visits.last_source_version_key ; Version source finale du groupe. |
| `event_time_basis` | `String` | Non | Projection explicite de int_opportunity_stage_visits.event_time_basis ; cdc_transition_proxy / business_proven / left_censored / observation_only. |
| `is_left_censored` | `Bool` | Non | Projection explicite de int_opportunity_stage_visits.is_left_censored ; Début du passage non observable. |
| `is_right_censored` | `Bool` | Non | Projection explicite de int_opportunity_stage_visits.is_right_censored ; Sortie admissible non observée. |
| `is_open_visit` | `Bool` | Non | Projection explicite de int_opportunity_stage_visits.is_open_visit ; Pas de transition/suppression suivante ; différent d’étape commercialement ouverte. |
| `has_observation_gap` | `Bool` | Non | Projection explicite de int_opportunity_stage_visits.has_observation_gap ; Lacune ou suppression/réapparition séparant passages. |
| `completed_duration_seconds` | `Nullable(Float64)` | Oui | Projection explicite de int_opportunity_stage_visits.completed_duration_seconds ; Différence millisecondes UTC/1000 pour passage terminé avec début admissible ; NULL sinon. |
| `completed_duration_days` | `Nullable(Float64)` | Oui | Projection explicite de int_opportunity_stage_visits.completed_duration_days ; completed_duration_seconds/86400. |
| `coverage_start_at` | `Nullable(DateTime64(3,'UTC'))` | Oui | Projection explicite de int_opportunity_stage_visits.coverage_start_at ; Couverture déclarée ; première observation seule ne prouve pas exhaustivité. |
| `coverage_end_at` | `Nullable(DateTime64(3,'UTC'))` | Oui | Projection explicite de int_opportunity_stage_visits.coverage_end_at ; Fin déclarée ; jamais max(updateDate) futur. |
| `is_history_complete` | `Nullable(Bool)` | Oui | Projection explicite de int_opportunity_stage_visits.is_history_complete ; Couverture de fenêtre vérifiée/configurée ; NULL si non établie. |
| `calculation_status` | `String` | Non | Projection explicite de int_opportunity_stage_visits.calculation_status ; ready / partial / blocked / not_applicable. |
| `status_reason` | `Nullable(String)` | Oui | Projection explicite de int_opportunity_stage_visits.status_reason ; Cause précise stable ; NULL si aucune dépendance manquante. |
| `stage_key` | `Nullable(String)` | Oui | Identité de l’étape. |
| `stage_version_key` | `Nullable(String)` | Oui | Version dim_stage à first_observed_at ; libellé d’observation, pas état courant réappliqué. |
| `company_id` | `Nullable(Int64)` | Oui | Société au contexte d’entrée si connu, sinon première observation avec réserve explicite. |
| `company_key` | `Nullable(String)` | Oui | Identité société du contexte. |
| `company_version_key` | `Nullable(String)` | Oui | Version de société de ce contexte. |
| `sale_type_id` | `Nullable(Int64)` | Oui | Type commercial du contexte. |
| `sale_type_key` | `Nullable(String)` | Oui | Identité type. |
| `sale_type_version_key` | `Nullable(String)` | Oui | Version type au contexte. |
| `acquisition_channel_key` | `Nullable(String)` | Oui | Canal d’acquisition officiel, NULL sans règle. |
| `channel_version_key` | `Nullable(String)` | Oui | Version canal. |
| `channel_candidate_code` | `Nullable(String)` | Oui | Origine Boond candidate conservée. |
| `is_channel_calculable` | `Bool` | Non | Règle canal effectivement résolue. |
| `entry_employee_key` | `Nullable(String)` | Oui | Responsable observé à entrée admissible ; NULL si entrée non datée. |
| `entry_employee_version_key` | `Nullable(String)` | Oui | Version responsable à entrée admissible. |
| `entry_team_key` | `Nullable(String)` | Oui | Équipe d’entrée résolue si datée/mappée. |
| `entry_team_version_key` | `Nullable(String)` | Oui | Version équipe à entrée. |
| `entry_context_time_basis` | `String` | Non | entered_at / first_observed_at_only / unknown ; les champs entry_* restent NULL si seule première observation censurée. |
| `is_team_filter_available` | `Bool` | Non | true si équipe à entrée du passage connue D25 ; false si attribution non observable. |
| `entered_date_key` | `Nullable(UInt32)` | Oui | Date Paris entrée, NULL censurée. |
| `exited_date_key` | `Nullable(UInt32)` | Oui | Date Paris sortie, NULL encore en cours/non prouvée. |

**Transformation / jointures :** Visite→contexte entrée N:0..1 ; si entered_at NULL, contexte descriptif first_observed_at avec entry_* NULL. Stage et dimensions N:0..1 même run ; aucune jointure 1:N vers tranches de responsabilité. Quand une date métier sort des bornes générées, conserver la date et mettre la clé Nullable à NULL avec statut ; ne pas allonger le calendrier jusqu’à une fin sentinelle2099. Les labels ne remplacent pas les clés. Aucun filtre vers le run publié dans ce fait : l’historique des runs reste consultable.

**Agrégation et usage :** Durées terminées et anciennetés en cours séparées. Médiane et P90 exacts inclusifs recalculés sur les lignes admissibles après filtres, jamais moyenne de médianes. Dossiers revisitant étape gardent plusieurs visit_key ; décompte de dossiers sur opportunity_key. La responsabilité reste descriptive, sans filtre durée équipe officiel.

**Matérialisation, histoire, reprise et fraîcheur :** vue dbt, une requête SELECT avec colonnes énumérées ; pas de stockage supplémentaire ni de stratégie incrémentale propre. La vue expose les révisions conservées dans son intermédiaire. Les jointures annexes portent toujours même model_run_id ; aucune relecture d’un ancien run avec dimensions actuelles. Recréation de vue idempotente ; source d’histoire inchangée. Exécution manuelle D29, sans SLA de production ; publication au rythme du lot validé, datasets sélectionnant int_publication. Aucune garantie de performance avant mesure.

**Tests / acceptation :** unicité/non-NULL de (model_run_id,record_key), correspondance exacte des clés/projections amont, relations dimensionnelles au bon run, aucune multiplication de contributions. Unicité visit_key par run ; aucune duplication au contexte. Durée complète censurée NULL ; changement responsable ne redémarre pas le passage. Défaut de grain/cardinalité : ERROR, publication bloquée. Limite connue : NULL et statut sans inventer de chiffre.

**Limites / dépendances :** Convention d’attribution individuelle/équipe non fixée ; seuil de stagnation non choisi.


<a id="fct_opportunity_event"></a>

### `fct_opportunity_event`

**Grain métier :** Opportunité × événement distinct et rôle de contribution. **Clé :** event_key ; record_key=H(tuple du grain), identique à la clé hashée amont. **Grain de révision :** (model_run_id,record_key).

**Amont exact :** `{{ ref('int_opportunity_events') }}`, `{{ ref('dim_date') }}`. **Destination :** `dtm_pipeline.fct_opportunity_event`, `dbt/models/marts/pipeline/fct_opportunity_event.sql`, YAML `dbt/models/marts/pipeline/_models.yml`.

| Colonne | Type ClickHouse | Nullable | Origine, formule, contraintes |
|---|---|---|---|
| `model_run_id` | `String` | Non | Métadonnée amont int_opportunity_events.model_run_id ; row_hash recalculé sur le contrat final du fait si des colonnes techniques sont ajoutées. Empreinte SHA256 commune de la recomposition : manifeste des entrées figées, code, référentiels et paramètres ; fournie par orchestration, identique dans tout le DAG. |
| `record_key` | `String` | Non | Métadonnée amont int_opportunity_events.record_key ; row_hash recalculé sur le contrat final du fait si des colonnes techniques sont ajoutées. Identité String H(tuple du grain décrit, domaine/version explicite), sans model_run_id ; égale la clé de grain lorsque cette dernière est déjà hashée. dim_date utilise H(calendar_date), jamais date_key UInt32 brut. |
| `record_version_key` | `String` | Non | Métadonnée amont int_opportunity_events.record_version_key ; row_hash recalculé sur le contrat final du fait si des colonnes techniques sont ajoutées. H(model_run_id,record_key) ; unicité physique de la révision du modèle. |
| `row_hash` | `String` | Non | Métadonnée amont int_opportunity_events.row_hash ; row_hash recalculé sur le contrat final du fait si des colonnes techniques sont ajoutées. H(tuple ordonné de toutes les colonnes métier de la fiche, NULL et types préservés) ; exclut les métadonnées de calcul. |
| `calculated_at` | `DateTime64(3,'UTC')` | Non | Métadonnée amont int_opportunity_events.calculated_at ; row_hash recalculé sur le contrat final du fait si des colonnes techniques sont ajoutées. Instant de calcul du lot ; fixe pour un même model_run_id, jamais utilisé comme événement métier. |
| `rule_version` | `String` | Non | Métadonnée amont int_opportunity_events.rule_version ; row_hash recalculé sur le contrat final du fait si des colonnes techniques sont ajoutées. Empreinte immuable du code et des règles appliquées ; dérivée du manifeste du lot. |
| `input_cutoff_at` | `DateTime64(3,'UTC')` | Non | Métadonnée amont int_opportunity_events.input_cutoff_at ; row_hash recalculé sur le contrat final du fait si des colonnes techniques sont ajoutées. Date limite de connaissance de la recomposition ; les entrées exactes sont figées par le manifeste, pas par ce timestamp seul. |
| `source_published_at` | `Nullable(DateTime64(3,'UTC'))` | Oui | Métadonnée amont int_opportunity_events.source_published_at ; row_hash recalculé sur le contrat final du fait si des colonnes techniques sont ajoutées. Maximum de publication CDC des versions contribuant à la ligne ; NULL pour un référentiel exclusivement généré. Les entrées de règles non fournies proviennent du futur dbt/config/case_rules.yml fusionné dans vars, sans seed ou source implicite. Ce maximum ne remplace aucune date métier. |
| `source_version_keys` | `Array(String)` | Non | Métadonnée amont int_opportunity_events.source_version_keys ; row_hash recalculé sur le contrat final du fait si des colonnes techniques sont ajoutées. Clés des versions sources contributrices, triées et sans répétition ; union des lignages amont. Liste vide pour une ligne exclusivement générée. |
| `tenant_id` | `String` | Non | Projection explicite de int_opportunity_events.tenant_id ; Identité du tenant src_tenant_id. |
| `opportunity_id` | `Int64` | Non | Projection explicite de int_opportunity_events.opportunity_id ; src_id du besoin Boond. |
| `opportunity_key` | `String` | Non | Projection explicite de int_opportunity_events.opportunity_key ; H(tenant_id,opportunity_id), identité stable intermodèles. |
| `event_key` | `String` | Non | Projection explicite de int_opportunity_events.event_key ; H(opportunity_key,event_type,event_origin_key). |
| `event_origin_key` | `String` | Non | Projection explicite de int_opportunity_events.event_origin_key ; Clé création source ou visit_key de transition. |
| `visit_key` | `Nullable(String)` | Oui | Projection explicite de int_opportunity_events.visit_key ; Passage si pertinent. |
| `event_type` | `String` | Non | Projection explicite de int_opportunity_events.event_type ; pipeline_created / stage_entered / stage_exited / signed / lost / abandoned / unqualified. |
| `event_at` | `Nullable(DateTime64(3,'UTC'))` | Oui | Projection explicite de int_opportunity_events.event_at ; Date métier création ou transition/proxy admissible ; NULL sans preuve. |
| `event_observed_at` | `DateTime64(3,'UTC')` | Non | Projection explicite de int_opportunity_events.event_observed_at ; Publication prouvant la trace ; différente de date métier. |
| `event_time_basis` | `String` | Non | Projection explicite de int_opportunity_events.event_time_basis ; business_created / cdc_transition_proxy / unknown. |
| `event_date_key` | `Nullable(UInt32)` | Oui | Projection explicite de int_opportunity_events.event_date_key ; Date Paris de event_at. |
| `from_stage_id` | `Nullable(Int64)` | Oui | Projection explicite de int_opportunity_events.from_stage_id ; Étape quittée. |
| `to_stage_id` | `Nullable(Int64)` | Oui | Projection explicite de int_opportunity_events.to_stage_id ; Étape rejointe. |
| `from_stage_version_key` | `Nullable(String)` | Oui | Projection explicite de int_opportunity_events.from_stage_version_key ; Version étape avant transition. |
| `to_stage_version_key` | `Nullable(String)` | Oui | Projection explicite de int_opportunity_events.to_stage_version_key ; Version étape à entrée. |
| `created_at` | `Nullable(DateTime64(3,'UTC'))` | Oui | Projection explicite de int_opportunity_events.created_at ; Création Boond. |
| `cohort_month` | `Nullable(Date)` | Oui | Projection explicite de int_opportunity_events.cohort_month ; Mois création Paris. |
| `company_id` | `Nullable(Int64)` | Oui | Projection explicite de int_opportunity_events.company_id ; Société Boond au moment de référence. |
| `company_key` | `Nullable(String)` | Oui | Projection explicite de int_opportunity_events.company_key ; H(tenant_id,company_id) si société connue. |
| `company_version_key` | `Nullable(String)` | Oui | Projection explicite de int_opportunity_events.company_version_key ; Version dim_company à la date de référence ; jointure sur même run. |
| `sale_type_id` | `Nullable(Int64)` | Oui | Projection explicite de int_opportunity_events.sale_type_id ; Type commercial de la version du besoin. |
| `sale_type_key` | `Nullable(String)` | Oui | Projection explicite de int_opportunity_events.sale_type_key ; Identité stable du code type. |
| `sale_type_version_key` | `Nullable(String)` | Oui | Projection explicite de int_opportunity_events.sale_type_version_key ; Version dim_sale_type au moment de référence. |
| `employee_id` | `Nullable(Int64)` | Oui | Projection explicite de int_opportunity_events.employee_id ; Responsable principal Boond à la date pertinente. |
| `employee_key` | `Nullable(String)` | Oui | Projection explicite de int_opportunity_events.employee_key ; Identité stable du responsable. |
| `employee_version_key` | `Nullable(String)` | Oui | Projection explicite de int_opportunity_events.employee_version_key ; Version de dim_employee à la date pertinente. |
| `team_id` | `Nullable(Int64)` | Oui | Projection explicite de int_opportunity_events.team_id ; Équipe businessunit seulement si attribution univoque. |
| `team_key` | `Nullable(String)` | Oui | Projection explicite de int_opportunity_events.team_key ; Identité stable d’équipe ; NULL si ambiguë ou inconnue. |
| `team_version_key` | `Nullable(String)` | Oui | Projection explicite de int_opportunity_events.team_version_key ; Version dim_team pertinente à la date. |
| `sales_segment` | `Nullable(String)` | Oui | Projection explicite de int_opportunity_events.sales_segment ; SMB / LA / ES si mapping fourni ; NULL sinon. |
| `is_team_calculable` | `Bool` | Non | Projection explicite de int_opportunity_events.is_team_calculable ; Vrai si une seule équipe est historiquement résolue ; KAM reste connue même sans segment de cible D23. |
| `acquisition_channel_key` | `Nullable(String)` | Oui | Projection explicite de int_opportunity_events.acquisition_channel_key ; Canal officiel fixé à création ; NULL avant règle QM-02. |
| `channel_version_key` | `Nullable(String)` | Oui | Projection explicite de int_opportunity_events.channel_version_key ; Version de dim_channel applicable à l’acquisition. |
| `channel_candidate_code` | `Nullable(String)` | Oui | Projection explicite de int_opportunity_events.channel_candidate_code ; Code origine Boond à création, converti String ; candidat descriptif seulement. |
| `is_channel_calculable` | `Bool` | Non | Projection explicite de int_opportunity_events.is_channel_calculable ; Vrai seulement si règle canal et mapping appliqués sans ambiguïté. |
| `attribution_status` | `String` | Non | Projection explicite de int_opportunity_events.attribution_status ; resolved / missing_team_mapping / multiple_teams / missing_channel_rule ; détails conservés. |
| `is_event_time_accepted` | `Nullable(Bool)` | Oui | Projection explicite int_opportunity_events.is_event_time_accepted ; Vrai pour date métier prouvée OU transition CDC réellement observée admise par D15 ; NULL si événement non datable/borne inconnue. Conserver cdc_transition_proxy, sans le présenter comme une date métier certifiée. |
| `nb_events` | `Nullable(UInt8)` | Oui | Projection explicite de int_opportunity_events.nb_events ; 1 si événement/population et date admissibles ;0 explicitement non comptable ;NULL si date non admissible ou éligibilité inconnue. Le proxy CDC observé est accepté par D15. |
| `generated_pipeline_amount_candidate` | `Nullable(Decimal(38,4))` | Oui | Projection explicite de int_opportunity_events.generated_pipeline_amount_candidate ; Valeur à création réellement observable ; NULL si première observation tardive. |
| `sum_generated_pipeline_amount` | `Nullable(Decimal(38,4))` | Oui | Projection explicite de int_opportunity_events.sum_generated_pipeline_amount ; Contribution commerciale générée admissible ; nature/unité signalées, pas MRR. |
| `sum_signed_mrr` | `Nullable(Decimal(38,4))` | Oui | Projection explicite de int_opportunity_events.sum_signed_mrr ; NULL sans preuve mensualité récurrente signée ; supplément seul upsell. |
| `amount_basis` | `String` | Non | Projection explicite de int_opportunity_events.amount_basis ; crm_estimated_unconfirmed / signed_recurring_proven / unknown. |
| `currency_code` | `Nullable(String)` | Oui | Projection explicite de int_opportunity_events.currency_code ; EUR par hypothèse explicite du case D20 ; cette devise ne prouve ni mensualité ni engagement du montant commercial. |
| `cycle_started_at` | `Nullable(DateTime64(3,'UTC'))` | Oui | Projection explicite de int_opportunity_events.cycle_started_at ; Création Boond pour cycle décidé. |
| `completed_cycle_duration_seconds` | `Nullable(Float64)` | Oui | Projection explicite de int_opportunity_events.completed_cycle_duration_seconds ; Issue admissible−création si dates connues. |
| `counting_scope_key` | `String` | Non | Projection explicite de int_opportunity_events.counting_scope_key ; H(opportunity_key,event_type), pour dossiers distincts. |
| `is_contribution_eligible` | `Nullable(Bool)` | Oui | Projection explicite de int_opportunity_events.is_contribution_eligible ; Première signature observée et population4/7 admissibles selon D18/D22 ; re-signatures connues=false avec contribution0 ; date/population non observable=NULL. Proxy CDC accepté D15. |
| `calculation_status` | `String` | Non | Projection explicite de int_opportunity_events.calculation_status ; ready / partial / blocked / not_applicable. |
| `status_reason` | `Nullable(String)` | Oui | Projection explicite de int_opportunity_events.status_reason ; Cause précise stable ; NULL si aucune dépendance manquante. |
| `from_stage_key` | `Nullable(String)` | Oui | H(tenant_id,from_stage_id) si connu. |
| `to_stage_key` | `Nullable(String)` | Oui | H(tenant_id,to_stage_id) si connu. |
| `created_date_key` | `Nullable(UInt32)` | Oui | Date Paris création. |

**Transformation / jointures :** Projection de l’intermédiaire ; clés d’étape et date générées explicitement, sans nouveau classement métier. Quand une date métier sort des bornes générées, conserver la date et mettre la clé Nullable à NULL avec statut ; ne pas allonger le calendrier jusqu’à une fin sentinelle2099. Les labels ne remplacent pas les clés. Aucun filtre vers le run publié dans ce fait : l’historique des runs reste consultable.

**Agrégation et usage :** Filtrer event_type avant agrégation. Les compteurs de dossiers font comptage distinct de opportunity_key sur la période, les sommes sélectionnent contributions admissibles. Génération/signé sont flux, pas stocks d’étapes.

**Matérialisation, histoire, reprise et fraîcheur :** vue dbt, une requête SELECT avec colonnes énumérées ; pas de stockage supplémentaire ni de stratégie incrémentale propre. La vue expose les révisions conservées dans son intermédiaire. Les jointures annexes portent toujours même model_run_id ; aucune relecture d’un ancien run avec dimensions actuelles. Recréation de vue idempotente ; source d’histoire inchangée. Exécution manuelle D29, sans SLA de production ; publication au rythme du lot validé, datasets sélectionnant int_publication. Aucune garantie de performance avant mesure.

**Tests / acceptation :** unicité/non-NULL de (model_run_id,record_key), correspondance exacte des clés/projections amont, relations dimensionnelles au bon run, aucune multiplication de contributions. Égalité des contributions int→fct ; 1→14 une seule signature ; montants signed NULL sans preuve. Défaut de grain/cardinalité : ERROR, publication bloquée. Limite connue : NULL et statut sans inventer de chiffre.

**Limites / dépendances :** Dates de signature exactes et MRR signé non établis ; re-signatures en statut inconnu.


<a id="fct_opportunity_followup"></a>

### `fct_opportunity_followup`

**Grain métier :** Dossier × définition × ancrage × horizon/observation. **Clé :** followup_key ; record_key=H(tuple du grain), identique à la clé hashée amont. **Grain de révision :** (model_run_id,record_key).

**Amont exact :** `{{ ref('int_opportunity_followup') }}`, `{{ ref('dim_date') }}`. **Destination :** `dtm_pipeline.fct_opportunity_followup`, `dbt/models/marts/pipeline/fct_opportunity_followup.sql`, YAML `dbt/models/marts/pipeline/_models.yml`.

| Colonne | Type ClickHouse | Nullable | Origine, formule, contraintes |
|---|---|---|---|
| `model_run_id` | `String` | Non | Métadonnée amont int_opportunity_followup.model_run_id ; row_hash recalculé sur le contrat final du fait si des colonnes techniques sont ajoutées. Empreinte SHA256 commune de la recomposition : manifeste des entrées figées, code, référentiels et paramètres ; fournie par orchestration, identique dans tout le DAG. |
| `record_key` | `String` | Non | Métadonnée amont int_opportunity_followup.record_key ; row_hash recalculé sur le contrat final du fait si des colonnes techniques sont ajoutées. Identité String H(tuple du grain décrit, domaine/version explicite), sans model_run_id ; égale la clé de grain lorsque cette dernière est déjà hashée. dim_date utilise H(calendar_date), jamais date_key UInt32 brut. |
| `record_version_key` | `String` | Non | Métadonnée amont int_opportunity_followup.record_version_key ; row_hash recalculé sur le contrat final du fait si des colonnes techniques sont ajoutées. H(model_run_id,record_key) ; unicité physique de la révision du modèle. |
| `row_hash` | `String` | Non | Métadonnée amont int_opportunity_followup.row_hash ; row_hash recalculé sur le contrat final du fait si des colonnes techniques sont ajoutées. H(tuple ordonné de toutes les colonnes métier de la fiche, NULL et types préservés) ; exclut les métadonnées de calcul. |
| `calculated_at` | `DateTime64(3,'UTC')` | Non | Métadonnée amont int_opportunity_followup.calculated_at ; row_hash recalculé sur le contrat final du fait si des colonnes techniques sont ajoutées. Instant de calcul du lot ; fixe pour un même model_run_id, jamais utilisé comme événement métier. |
| `rule_version` | `String` | Non | Métadonnée amont int_opportunity_followup.rule_version ; row_hash recalculé sur le contrat final du fait si des colonnes techniques sont ajoutées. Empreinte immuable du code et des règles appliquées ; dérivée du manifeste du lot. |
| `input_cutoff_at` | `DateTime64(3,'UTC')` | Non | Métadonnée amont int_opportunity_followup.input_cutoff_at ; row_hash recalculé sur le contrat final du fait si des colonnes techniques sont ajoutées. Date limite de connaissance de la recomposition ; les entrées exactes sont figées par le manifeste, pas par ce timestamp seul. |
| `source_published_at` | `Nullable(DateTime64(3,'UTC'))` | Oui | Métadonnée amont int_opportunity_followup.source_published_at ; row_hash recalculé sur le contrat final du fait si des colonnes techniques sont ajoutées. Maximum de publication CDC des versions contribuant à la ligne ; NULL pour un référentiel exclusivement généré. Les entrées de règles non fournies proviennent du futur dbt/config/case_rules.yml fusionné dans vars, sans seed ou source implicite. Ce maximum ne remplace aucune date métier. |
| `source_version_keys` | `Array(String)` | Non | Métadonnée amont int_opportunity_followup.source_version_keys ; row_hash recalculé sur le contrat final du fait si des colonnes techniques sont ajoutées. Clés des versions sources contributrices, triées et sans répétition ; union des lignages amont. Liste vide pour une ligne exclusivement générée. |
| `tenant_id` | `String` | Non | Projection explicite de int_opportunity_followup.tenant_id ; Identité du tenant src_tenant_id. |
| `opportunity_id` | `Int64` | Non | Projection explicite de int_opportunity_followup.opportunity_id ; src_id du besoin Boond. |
| `opportunity_key` | `String` | Non | Projection explicite de int_opportunity_followup.opportunity_key ; H(tenant_id,opportunity_id), identité stable intermodèles. |
| `followup_key` | `String` | Non | Projection explicite de int_opportunity_followup.followup_key ; H(opportunity_key,followup_definition_version_key,anchor_key,observation_at). |
| `followup_definition_id` | `String` | Non | Projection explicite de int_opportunity_followup.followup_definition_id ; ID stable de définition. |
| `followup_definition_key` | `String` | Non | Projection explicite de int_opportunity_followup.followup_definition_key ; Identité stable H(followup_definition_id). |
| `followup_definition_version_key` | `String` | Non | Projection explicite de int_opportunity_followup.followup_definition_version_key ; Version exacte de définition. |
| `followup_kind` | `String` | Non | Projection explicite de int_opportunity_followup.followup_kind ; cohort_outcome / funnel_reach / stage_transition. |
| `funnel_position` | `Nullable(UInt16)` | Oui | Projection explicite de int_opportunity_followup.funnel_position ; Position configurée, pas code numérique. |
| `previous_target_stage_id` | `Nullable(Int64)` | Oui | Projection explicite de int_opportunity_followup.previous_target_stage_id ; Cible précédente configurée. |
| `created_at` | `Nullable(DateTime64(3,'UTC'))` | Oui | Projection explicite de int_opportunity_followup.created_at ; Création Boond. |
| `cohort_month` | `Nullable(Date)` | Oui | Projection explicite de int_opportunity_followup.cohort_month ; Mois Paris de création, inchangé par réouverture. |
| `anchor_key` | `String` | Non | Projection explicite de int_opportunity_followup.anchor_key ; Création ou passage admissible. |
| `anchor_at` | `Nullable(DateTime64(3,'UTC'))` | Oui | Projection explicite de int_opportunity_followup.anchor_at ; Création pour cohorte/funnel ; entrée en A pour transition. |
| `source_stage_id` | `Nullable(Int64)` | Oui | Projection explicite de int_opportunity_followup.source_stage_id ; Source transition, NULL cohorte. |
| `target_stage_id` | `Nullable(Int64)` | Oui | Projection explicite de int_opportunity_followup.target_stage_id ; Cible funnel/transition, NULL issuecohorte. |
| `target_stage_key` | `Nullable(String)` | Oui | Projection explicite de int_opportunity_followup.target_stage_key ; Identité étape cible. |
| `target_stage_version_key` | `Nullable(String)` | Oui | Projection explicite de int_opportunity_followup.target_stage_version_key ; Version cible pertinente. |
| `horizon_days` | `Nullable(UInt16)` | Oui | Projection explicite de int_opportunity_followup.horizon_days ; 30/60/90 cohorte ; transition configurée ; NULL funnel à date. |
| `horizon_at` | `Nullable(DateTime64(3,'UTC'))` | Oui | Projection explicite de int_opportunity_followup.horizon_at ; addDays(anchor converti Paris,H) puis UTC ; même heure locale. |
| `observation_at` | `Nullable(DateTime64(3,'UTC'))` | Oui | Projection explicite de int_opportunity_followup.observation_at ; horizon_at cohorte/transition ; cutoff funnel à date. |
| `cohort_mature_at` | `Nullable(DateTime64(3,'UTC'))` | Oui | Projection explicite de int_opportunity_followup.cohort_mature_at ; max(horizon_at) sur tous membres connus tenant/mois/type/définition/horizon AVANT équipe/canal. |
| `is_mature` | `Nullable(Bool)` | Oui | Projection explicite de int_opportunity_followup.is_mature ; Horizon individuel atteint. |
| `is_cohort_mature` | `Nullable(Bool)` | Oui | Projection explicite de int_opportunity_followup.is_cohort_mature ; Cutoff>=cohort_mature_at et ancrages connus. |
| `is_eligible` | `Nullable(Bool)` | Oui | Projection explicite de int_opportunity_followup.is_eligible ; Population/ancrage admis ; NULL sans règle. |
| `is_observable` | `Nullable(Bool)` | Oui | Projection explicite de int_opportunity_followup.is_observable ; État à horizon couvert ; maturité ne suffit pas. |
| `coverage_start_at` | `Nullable(DateTime64(3,'UTC'))` | Oui | Projection explicite de int_opportunity_followup.coverage_start_at ; Début déclaré. |
| `coverage_end_at` | `Nullable(DateTime64(3,'UTC'))` | Oui | Projection explicite de int_opportunity_followup.coverage_end_at ; Fin déclarée, pas maxdate future. |
| `is_history_complete` | `Nullable(Bool)` | Oui | Projection explicite de int_opportunity_followup.is_history_complete ; Complétude déclarée pour fenêtre. |
| `first_reached_at` | `Nullable(DateTime64(3,'UTC'))` | Oui | Projection explicite de int_opportunity_followup.first_reached_at ; Premier événement cible daté après ancrage ; NULL présence initiale censurée. |
| `first_reached_observed_at` | `Nullable(DateTime64(3,'UTC'))` | Oui | Projection explicite de int_opportunity_followup.first_reached_observed_at ; Première présence cible observée ; atteint au plus tard alors, pas date exacte. |
| `previous_stage_first_reached_at` | `Nullable(DateTime64(3,'UTC'))` | Oui | Projection explicite de int_opportunity_followup.previous_stage_first_reached_at ; Atteinte admissible source ; NULL si non prouvée. |
| `reached_target` | `Nullable(Bool)` | Oui | Projection explicite de int_opportunity_followup.reached_target ; Vrai si preuve cible ; faux seulement fenêtre entièrement couverte sans cible ; sinon NULL. |
| `issue_at_horizon` | `Nullable(String)` | Oui | Projection explicite de int_opportunity_followup.issue_at_horizon ; open / won / lost / abandoned / unqualified / unknown ; NULL immature. |
| `population_count_key` | `String` | Non | Projection explicite de int_opportunity_followup.population_count_key ; H(opportunity_key,followup_definition_version_key,horizon_days). |
| `denominator_contribution` | `Nullable(UInt8)` | Oui | Projection explicite de int_opportunity_followup.denominator_contribution ; 1 membre connu éligible cohorte mature ; NULL immature/ancrage inconnu. |
| `converted_contribution` | `Nullable(UInt8)` | Oui | Projection explicite de int_opportunity_followup.converted_contribution ; 1/0 si conversion calculable ; NULL sinon. |
| `open_contribution` | `Nullable(UInt8)` | Oui | Projection explicite de int_opportunity_followup.open_contribution ; 1 issue open, 0 autres ; NULL immature. |
| `won_contribution` | `Nullable(UInt8)` | Oui | Projection explicite de int_opportunity_followup.won_contribution ; 1 won, 0 autres ; NULL immature. |
| `lost_contribution` | `Nullable(UInt8)` | Oui | Projection explicite de int_opportunity_followup.lost_contribution ; 1 lost seulement, NULL immature. |
| `abandoned_contribution` | `Nullable(UInt8)` | Oui | Projection explicite de int_opportunity_followup.abandoned_contribution ; 1 abandoned, distinct lost ; NULL immature. |
| `unqualified_contribution` | `Nullable(UInt8)` | Oui | Projection explicite de int_opportunity_followup.unqualified_contribution ; 1 unqualified, distinct lost ; NULL immature. |
| `unknown_contribution` | `Nullable(UInt8)` | Oui | Projection explicite de int_opportunity_followup.unknown_contribution ; 1 état/classe non observable mature ; inconnu conservé au dénominateur. |
| `company_id` | `Nullable(Int64)` | Oui | Projection explicite de int_opportunity_followup.company_id ; Société Boond au moment de référence. |
| `company_key` | `Nullable(String)` | Oui | Projection explicite de int_opportunity_followup.company_key ; H(tenant_id,company_id) si société connue. |
| `company_version_key` | `Nullable(String)` | Oui | Projection explicite de int_opportunity_followup.company_version_key ; Version dim_company à la date de référence ; jointure sur même run. |
| `sale_type_id` | `Nullable(Int64)` | Oui | Projection explicite de int_opportunity_followup.sale_type_id ; Type commercial de la version du besoin. |
| `sale_type_key` | `Nullable(String)` | Oui | Projection explicite de int_opportunity_followup.sale_type_key ; Identité stable du code type. |
| `sale_type_version_key` | `Nullable(String)` | Oui | Projection explicite de int_opportunity_followup.sale_type_version_key ; Version dim_sale_type au moment de référence. |
| `employee_id` | `Nullable(Int64)` | Oui | Projection explicite de int_opportunity_followup.employee_id ; Responsable principal Boond à la date pertinente. |
| `employee_key` | `Nullable(String)` | Oui | Projection explicite de int_opportunity_followup.employee_key ; Identité stable du responsable. |
| `employee_version_key` | `Nullable(String)` | Oui | Projection explicite de int_opportunity_followup.employee_version_key ; Version de dim_employee à la date pertinente. |
| `team_id` | `Nullable(Int64)` | Oui | Projection explicite de int_opportunity_followup.team_id ; Équipe businessunit seulement si attribution univoque. |
| `team_key` | `Nullable(String)` | Oui | Projection explicite de int_opportunity_followup.team_key ; Identité stable d’équipe ; NULL si ambiguë ou inconnue. |
| `team_version_key` | `Nullable(String)` | Oui | Projection explicite de int_opportunity_followup.team_version_key ; Version dim_team pertinente à la date. |
| `sales_segment` | `Nullable(String)` | Oui | Projection explicite de int_opportunity_followup.sales_segment ; SMB / LA / ES si mapping fourni ; NULL sinon. |
| `is_team_calculable` | `Bool` | Non | Projection explicite de int_opportunity_followup.is_team_calculable ; Vrai si une seule équipe est historiquement résolue ; KAM reste connue même sans segment de cible D23. |
| `acquisition_channel_key` | `Nullable(String)` | Oui | Projection explicite de int_opportunity_followup.acquisition_channel_key ; Canal officiel fixé à création ; NULL avant règle QM-02. |
| `channel_version_key` | `Nullable(String)` | Oui | Projection explicite de int_opportunity_followup.channel_version_key ; Version de dim_channel applicable à l’acquisition. |
| `channel_candidate_code` | `Nullable(String)` | Oui | Projection explicite de int_opportunity_followup.channel_candidate_code ; Code origine Boond à création, converti String ; candidat descriptif seulement. |
| `is_channel_calculable` | `Bool` | Non | Projection explicite de int_opportunity_followup.is_channel_calculable ; Vrai seulement si règle canal et mapping appliqués sans ambiguïté. |
| `attribution_status` | `String` | Non | Projection explicite de int_opportunity_followup.attribution_status ; resolved / missing_team_mapping / multiple_teams / missing_channel_rule ; détails conservés. |
| `calculation_status` | `String` | Non | Projection explicite de int_opportunity_followup.calculation_status ; ready / partial / blocked / not_applicable. |
| `status_reason` | `Nullable(String)` | Oui | Projection explicite de int_opportunity_followup.status_reason ; Cause précise stable ; NULL si aucune dépendance manquante. |
| `created_date_key` | `Nullable(UInt32)` | Oui | Date Paris création. |
| `anchor_date_key` | `Nullable(UInt32)` | Oui | Date Paris ancrage. |
| `observation_date_key` | `Nullable(UInt32)` | Oui | Date Paris observation. |
| `horizon_date_key` | `Nullable(UInt32)` | Oui | Date Paris horizon. |
| `cohort_date_key` | `Nullable(UInt32)` | Oui | YYYYMMDD premierjour cohorte. |

**Transformation / jointures :** Projection explicite des contributions calculées ; dates de rôle dim_date N:0..1 même run. Aucun regroupement ni nouvelle maturité dans le fait. Quand une date métier sort des bornes générées, conserver la date et mettre la clé Nullable à NULL avec statut ; ne pas allonger le calendrier jusqu’à une fin sentinelle2099. Les labels ne remplacent pas les clés. Aucun filtre vers le run publié dans ce fait : l’historique des runs reste consultable.

**Agrégation et usage :** Un dénominateur par dossier/population/horizon ; ne pas sommer horizons ou définitions. Taux=somme numérateur/somme dénominateur compatibles. Les six catégories dont unknown gardent même dénominateur, sans renormalisation. Cohorte immature=mesures NULL.

**Matérialisation, histoire, reprise et fraîcheur :** vue dbt, une requête SELECT avec colonnes énumérées ; pas de stockage supplémentaire ni de stratégie incrémentale propre. La vue expose les révisions conservées dans son intermédiaire. Les jointures annexes portent toujours même model_run_id ; aucune relecture d’un ancien run avec dimensions actuelles. Recréation de vue idempotente ; source d’histoire inchangée. Exécution manuelle D29, sans SLA de production ; publication au rythme du lot validé, datasets sélectionnant int_publication. Aucune garantie de performance avant mesure.

**Tests / acceptation :** unicité/non-NULL de (model_run_id,record_key), correspondance exacte des clés/projections amont, relations dimensionnelles au bon run, aucune multiplication de contributions. Égalité int→fct ; six catégories=denominator mature ; filtres équipe/canal ne modifient pas cohort_mature_at. Défaut de grain/cardinalité : ERROR, publication bloquée. Limite connue : NULL et statut sans inventer de chiffre.

**Limites / dépendances :** Définitions de transition/funnel non validées désactivées ; couverture exhaustive séparée de maturité.


<a id="fct_action"></a>

### `fct_action`

**Grain métier :** Action × intervalle de version/contexte ; action_key est l’identité stable. **Clé :** action_version_key ; record_key=H(tuple du grain), identique à la clé hashée amont. **Grain de révision :** (model_run_id,record_key).

**Amont exact :** `{{ ref('int_actions_prepared') }}`, `{{ ref('dim_date') }}`. **Destination :** `dtm_pipeline.fct_action`, `dbt/models/marts/pipeline/fct_action.sql`, YAML `dbt/models/marts/pipeline/_models.yml`.

| Colonne | Type ClickHouse | Nullable | Origine, formule, contraintes |
|---|---|---|---|
| `model_run_id` | `String` | Non | Métadonnée amont int_actions_prepared.model_run_id ; row_hash recalculé sur le contrat final du fait si des colonnes techniques sont ajoutées. Empreinte SHA256 commune de la recomposition : manifeste des entrées figées, code, référentiels et paramètres ; fournie par orchestration, identique dans tout le DAG. |
| `record_key` | `String` | Non | Métadonnée amont int_actions_prepared.record_key ; row_hash recalculé sur le contrat final du fait si des colonnes techniques sont ajoutées. Identité String H(tuple du grain décrit, domaine/version explicite), sans model_run_id ; égale la clé de grain lorsque cette dernière est déjà hashée. dim_date utilise H(calendar_date), jamais date_key UInt32 brut. |
| `record_version_key` | `String` | Non | Métadonnée amont int_actions_prepared.record_version_key ; row_hash recalculé sur le contrat final du fait si des colonnes techniques sont ajoutées. H(model_run_id,record_key) ; unicité physique de la révision du modèle. |
| `row_hash` | `String` | Non | Métadonnée amont int_actions_prepared.row_hash ; row_hash recalculé sur le contrat final du fait si des colonnes techniques sont ajoutées. H(tuple ordonné de toutes les colonnes métier de la fiche, NULL et types préservés) ; exclut les métadonnées de calcul. |
| `calculated_at` | `DateTime64(3,'UTC')` | Non | Métadonnée amont int_actions_prepared.calculated_at ; row_hash recalculé sur le contrat final du fait si des colonnes techniques sont ajoutées. Instant de calcul du lot ; fixe pour un même model_run_id, jamais utilisé comme événement métier. |
| `rule_version` | `String` | Non | Métadonnée amont int_actions_prepared.rule_version ; row_hash recalculé sur le contrat final du fait si des colonnes techniques sont ajoutées. Empreinte immuable du code et des règles appliquées ; dérivée du manifeste du lot. |
| `input_cutoff_at` | `DateTime64(3,'UTC')` | Non | Métadonnée amont int_actions_prepared.input_cutoff_at ; row_hash recalculé sur le contrat final du fait si des colonnes techniques sont ajoutées. Date limite de connaissance de la recomposition ; les entrées exactes sont figées par le manifeste, pas par ce timestamp seul. |
| `source_published_at` | `Nullable(DateTime64(3,'UTC'))` | Oui | Métadonnée amont int_actions_prepared.source_published_at ; row_hash recalculé sur le contrat final du fait si des colonnes techniques sont ajoutées. Maximum de publication CDC des versions contribuant à la ligne ; NULL pour un référentiel exclusivement généré. Les entrées de règles non fournies proviennent du futur dbt/config/case_rules.yml fusionné dans vars, sans seed ou source implicite. Ce maximum ne remplace aucune date métier. |
| `source_version_keys` | `Array(String)` | Non | Métadonnée amont int_actions_prepared.source_version_keys ; row_hash recalculé sur le contrat final du fait si des colonnes techniques sont ajoutées. Clés des versions sources contributrices, triées et sans répétition ; union des lignages amont. Liste vide pour une ligne exclusivement générée. |
| `action_key` | `String` | Non | Projection explicite de int_actions_prepared.action_key ; H(tenant_id,action_id), identité stable. |
| `action_version_key` | `String` | Non | Projection explicite de int_actions_prepared.action_version_key ; H(action_key,valid_from_at), grain de version. |
| `tenant_id` | `String` | Non | Projection explicite de int_actions_prepared.tenant_id ; src_tenant_id. |
| `action_id` | `Int64` | Non | Projection explicite de int_actions_prepared.action_id ; src_id. |
| `valid_from_at` | `DateTime64(3,'UTC')` | Non | Projection explicite de int_actions_prepared.valid_from_at ; Publication CDC et bornes de contexte incluses. |
| `valid_to_at` | `Nullable(DateTime64(3,'UTC'))` | Oui | Projection explicite de int_actions_prepared.valid_to_at ; Version/context suivant exclu. |
| `source_action_published_at` | `DateTime64(3,'UTC')` | Non | Projection explicite de int_actions_prepared.source_action_published_at ; Publication CDC exacte de l’action, sans max des autres objets de contexte. |
| `is_source_deleted` | `Bool` | Non | Projection explicite de int_actions_prepared.is_source_deleted ; src_is_deleted. |
| `action_type_id` | `Nullable(Int64)` | Oui | Projection explicite de int_actions_prepared.action_type_id ; src_type_id. |
| `action_type_key` | `Nullable(String)` | Oui | Projection explicite de int_actions_prepared.action_type_key ; Identité type. |
| `action_type_version_key` | `Nullable(String)` | Oui | Projection explicite de int_actions_prepared.action_type_version_key ; Version dim_action_type. |
| `company_id` | `Nullable(Int64)` | Oui | Projection explicite de int_actions_prepared.company_id ; src_company_id ; pas complétion ambiguë. |
| `company_key` | `Nullable(String)` | Oui | Projection explicite de int_actions_prepared.company_key ; Identité société. |
| `company_version_key` | `Nullable(String)` | Oui | Projection explicite de int_actions_prepared.company_version_key ; Version société à date. |
| `contact_id` | `Nullable(Int64)` | Oui | Projection explicite de int_actions_prepared.contact_id ; dependsOn.id si type=contact. |
| `opportunity_id` | `Nullable(Int64)` | Oui | Projection explicite de int_actions_prepared.opportunity_id ; dependsOn.id si type=opportunity ; NULL si seul contact. |
| `opportunity_key` | `Nullable(String)` | Oui | Projection explicite de int_actions_prepared.opportunity_key ; Besoin seulement si lien direct établi. |
| `depends_on_type` | `String` | Non | Projection explicite de int_actions_prepared.depends_on_type ; src_depends_on_type. |
| `depends_on_id` | `Nullable(Int64)` | Oui | Projection explicite de int_actions_prepared.depends_on_id ; src_depends_on_id, lu avec type. |
| `employee_id` | `Nullable(Int64)` | Oui | Projection explicite de int_actions_prepared.employee_id ; src_main_manager_id. |
| `employee_key` | `Nullable(String)` | Oui | Projection explicite de int_actions_prepared.employee_key ; Identité responsable. |
| `employee_version_key` | `Nullable(String)` | Oui | Projection explicite de int_actions_prepared.employee_version_key ; Version responsable. |
| `team_key` | `Nullable(String)` | Oui | Projection explicite de int_actions_prepared.team_key ; Équipe si règle action et mapping explicites ; NULL sinon. |
| `team_version_key` | `Nullable(String)` | Oui | Projection explicite de int_actions_prepared.team_version_key ; Version équipe. |
| `is_team_calculable` | `Bool` | Non | Projection explicite de int_actions_prepared.is_team_calculable ; Attribution action résolue et univoque. |
| `created_at` | `Nullable(DateTime64(3,'UTC'))` | Oui | Projection explicite de int_actions_prepared.created_at ; src_created_at. |
| `scheduled_start_at` | `Nullable(DateTime64(3,'UTC'))` | Oui | Projection explicite de int_actions_prepared.scheduled_start_at ; src_started_at, agenda uniquement. |
| `scheduled_end_at` | `Nullable(DateTime64(3,'UTC'))` | Oui | Projection explicite de int_actions_prepared.scheduled_end_at ; src_ended_at, agenda uniquement. |
| `actual_event_at` | `Nullable(DateTime64(3,'UTC'))` | Oui | Projection explicite de int_actions_prepared.actual_event_at ; NULL sans preuve structurée de tenue. |
| `realization_status` | `String` | Non | Projection explicite de int_actions_prepared.realization_status ; unknown sans preuve ; held/planned/cancelled/no_show seulement si prouvé. |
| `is_demo_request` | `Bool` | Non | Projection explicite de int_actions_prepared.is_demo_request ; Type25 selon mapping, sans compter les versions. |
| `is_demo_type` | `Bool` | Non | Projection explicite de int_actions_prepared.is_demo_type ; Type60/68 selon mapping documentaire. |
| `is_realized_demo` | `Nullable(Bool)` | Oui | Projection explicite de int_actions_prepared.is_realized_demo ; NULL sans preuve de tenue ; type passé ne suffit pas. |
| `demo_session_key` | `Nullable(String)` | Oui | Projection explicite de int_actions_prepared.demo_session_key ; Séance réelle dédupliquée, NULL sans règle/proof. |
| `counting_date` | `Nullable(Date)` | Oui | Projection explicite de int_actions_prepared.counting_date ; Date Paris tenue réelle, NULL sans preuve. |
| `link_status` | `String` | Non | Projection explicite de int_actions_prepared.link_status ; direct_opportunity / contact_only / missing / ambiguous. |
| `calculation_status` | `String` | Non | Projection explicite de int_actions_prepared.calculation_status ; ready / partial / blocked / not_applicable. |
| `status_reason` | `Nullable(String)` | Oui | Projection explicite de int_actions_prepared.status_reason ; Cause précise stable ; NULL si aucune dépendance manquante. |
| `created_date_key` | `Nullable(UInt32)` | Oui | Date Paris création action. |
| `scheduled_start_date_key` | `Nullable(UInt32)` | Oui | Date Paris agenda. |
| `actual_event_date_key` | `Nullable(UInt32)` | Oui | Date Paris tenue prouvée, NULL sans preuve. |

**Transformation / jointures :** Projection de toutes les versions ; pour lecture passée corrigée à cutoff, sélectionner une version par action_key avant filtre date métier ou suppression. Ne pas choisir la dernière version vivante si la dernière est supprimée. Quand une date métier sort des bornes générées, conserver la date et mettre la clé Nullable à NULL avec statut ; ne pas allonger le calendrier jusqu’à une fin sentinelle2099. Les labels ne remplacent pas les clés. Aucun filtre vers le run publié dans ce fait : l’historique des runs reste consultable.

**Agrégation et usage :** Une action n’est comptée qu’une fois après sélection pertinente ; compteur de séances réelles sur demo_session_key prouvée, pas nombre de versions. Agenda/type restent descriptifs. Suppression ne vaut pas annulation ou séance tenue.

**Matérialisation, histoire, reprise et fraîcheur :** vue dbt, une requête SELECT avec colonnes énumérées ; pas de stockage supplémentaire ni de stratégie incrémentale propre. La vue expose les révisions conservées dans son intermédiaire. Les jointures annexes portent toujours même model_run_id ; aucune relecture d’un ancien run avec dimensions actuelles. Recréation de vue idempotente ; source d’histoire inchangée. Exécution manuelle D29, sans SLA de production ; publication au rythme du lot validé, datasets sélectionnant int_publication. Aucune garantie de performance avant mesure.

**Tests / acceptation :** unicité/non-NULL de (model_run_id,record_key), correspondance exacte des clés/projections amont, relations dimensionnelles au bon run, aucune multiplication de contributions. Conservation de toutes versions ; latest supprimé ne ressuscite pas ancienne version. Sans preuve, réalisé démos NULL. Défaut de grain/cardinalité : ERROR, publication bloquée. Limite connue : NULL et statut sans inventer de chiffre.

**Limites / dépendances :** Preuve de réalisation/chaînage, attribution équipe et déduplication de séance absentes.


<a id="fct_demo_interval"></a>

### `fct_demo_interval`

**Grain métier :** Parcours de démo prouvé × intervalle entre événements. **Clé :** demo_interval_key ; record_key=H(tuple du grain), identique à la clé hashée amont. **Grain de révision :** (model_run_id,record_key).

**Amont exact :** `{{ ref('int_demo_intervals') }}`, `{{ ref('dim_date') }}`. **Destination :** `dtm_pipeline.fct_demo_interval`, `dbt/models/marts/pipeline/fct_demo_interval.sql`, YAML `dbt/models/marts/pipeline/_models.yml`.

| Colonne | Type ClickHouse | Nullable | Origine, formule, contraintes |
|---|---|---|---|
| `model_run_id` | `String` | Non | Métadonnée amont int_demo_intervals.model_run_id ; row_hash recalculé sur le contrat final du fait si des colonnes techniques sont ajoutées. Empreinte SHA256 commune de la recomposition : manifeste des entrées figées, code, référentiels et paramètres ; fournie par orchestration, identique dans tout le DAG. |
| `record_key` | `String` | Non | Métadonnée amont int_demo_intervals.record_key ; row_hash recalculé sur le contrat final du fait si des colonnes techniques sont ajoutées. Identité String H(tuple du grain décrit, domaine/version explicite), sans model_run_id ; égale la clé de grain lorsque cette dernière est déjà hashée. dim_date utilise H(calendar_date), jamais date_key UInt32 brut. |
| `record_version_key` | `String` | Non | Métadonnée amont int_demo_intervals.record_version_key ; row_hash recalculé sur le contrat final du fait si des colonnes techniques sont ajoutées. H(model_run_id,record_key) ; unicité physique de la révision du modèle. |
| `row_hash` | `String` | Non | Métadonnée amont int_demo_intervals.row_hash ; row_hash recalculé sur le contrat final du fait si des colonnes techniques sont ajoutées. H(tuple ordonné de toutes les colonnes métier de la fiche, NULL et types préservés) ; exclut les métadonnées de calcul. |
| `calculated_at` | `DateTime64(3,'UTC')` | Non | Métadonnée amont int_demo_intervals.calculated_at ; row_hash recalculé sur le contrat final du fait si des colonnes techniques sont ajoutées. Instant de calcul du lot ; fixe pour un même model_run_id, jamais utilisé comme événement métier. |
| `rule_version` | `String` | Non | Métadonnée amont int_demo_intervals.rule_version ; row_hash recalculé sur le contrat final du fait si des colonnes techniques sont ajoutées. Empreinte immuable du code et des règles appliquées ; dérivée du manifeste du lot. |
| `input_cutoff_at` | `DateTime64(3,'UTC')` | Non | Métadonnée amont int_demo_intervals.input_cutoff_at ; row_hash recalculé sur le contrat final du fait si des colonnes techniques sont ajoutées. Date limite de connaissance de la recomposition ; les entrées exactes sont figées par le manifeste, pas par ce timestamp seul. |
| `source_published_at` | `Nullable(DateTime64(3,'UTC'))` | Oui | Métadonnée amont int_demo_intervals.source_published_at ; row_hash recalculé sur le contrat final du fait si des colonnes techniques sont ajoutées. Maximum de publication CDC des versions contribuant à la ligne ; NULL pour un référentiel exclusivement généré. Les entrées de règles non fournies proviennent du futur dbt/config/case_rules.yml fusionné dans vars, sans seed ou source implicite. Ce maximum ne remplace aucune date métier. |
| `source_version_keys` | `Array(String)` | Non | Métadonnée amont int_demo_intervals.source_version_keys ; row_hash recalculé sur le contrat final du fait si des colonnes techniques sont ajoutées. Clés des versions sources contributrices, triées et sans répétition ; union des lignages amont. Liste vide pour une ligne exclusivement générée. |
| `demo_interval_key` | `String` | Non | Projection explicite de int_demo_intervals.demo_interval_key ; H(demo_journey_key,start_action_key,end_action_key,interval_kind). |
| `demo_journey_key` | `String` | Non | Projection explicite de int_demo_intervals.demo_journey_key ; Parcours explicitement relié ; pas génération par contact seul. |
| `tenant_id` | `String` | Non | Projection explicite de int_demo_intervals.tenant_id ; Tenant commun des deux actions. |
| `start_action_key` | `String` | Non | Projection explicite de int_demo_intervals.start_action_key ; Action début. |
| `end_action_key` | `String` | Non | Projection explicite de int_demo_intervals.end_action_key ; Action fin. |
| `start_action_id` | `Int64` | Non | Projection explicite de int_demo_intervals.start_action_id ; ID source début. |
| `end_action_id` | `Int64` | Non | Projection explicite de int_demo_intervals.end_action_id ; ID source fin. |
| `opportunity_id` | `Nullable(Int64)` | Oui | Projection explicite de int_demo_intervals.opportunity_id ; Besoin commun prouvé. |
| `opportunity_key` | `Nullable(String)` | Oui | Projection explicite de int_demo_intervals.opportunity_key ; Besoin prouvé seulement. |
| `company_key` | `Nullable(String)` | Oui | Projection explicite de int_demo_intervals.company_key ; Société cohérente des deux actions. |
| `company_version_key` | `Nullable(String)` | Oui | Projection explicite de int_demo_intervals.company_version_key ; Version société à ancrage. |
| `sale_type_id` | `Nullable(Int64)` | Oui | Projection explicite de int_demo_intervals.sale_type_id ; Type du besoin prouvé. |
| `sale_type_key` | `Nullable(String)` | Oui | Projection explicite de int_demo_intervals.sale_type_key ; Identité type. |
| `sale_type_version_key` | `Nullable(String)` | Oui | Projection explicite de int_demo_intervals.sale_type_version_key ; Version type. |
| `team_key` | `Nullable(String)` | Oui | Projection explicite de int_demo_intervals.team_key ; NULL avant convention d’attribution délai. |
| `team_version_key` | `Nullable(String)` | Oui | Projection explicite de int_demo_intervals.team_version_key ; Version équipe si règle ultérieure. |
| `interval_kind` | `String` | Non | Projection explicite de int_demo_intervals.interval_kind ; request_to_first_demo / first_to_additional. |
| `from_demo_step` | `String` | Non | Projection explicite de int_demo_intervals.from_demo_step ; Sous-étape début. |
| `to_demo_step` | `String` | Non | Projection explicite de int_demo_intervals.to_demo_step ; Sous-étape fin. |
| `started_at` | `DateTime64(3,'UTC')` | Non | Projection explicite de int_demo_intervals.started_at ; Événement début prouvé. |
| `ended_at` | `DateTime64(3,'UTC')` | Non | Projection explicite de int_demo_intervals.ended_at ; Événement fin prouvé, >=début. |
| `elapsed_duration_seconds` | `Float64` | Non | Projection explicite de int_demo_intervals.elapsed_duration_seconds ; Écart millisecondes UTC/1000. |
| `elapsed_duration_days` | `Float64` | Non | Projection explicite de int_demo_intervals.elapsed_duration_days ; Secondes/86400. |
| `time_basis` | `String` | Non | Projection explicite de int_demo_intervals.time_basis ; Nature précise événements ; pas durée agenda. |
| `link_status` | `String` | Non | Projection explicite de int_demo_intervals.link_status ; proven pour lignes construites. |
| `calculation_status` | `String` | Non | Projection explicite de int_demo_intervals.calculation_status ; ready / partial / blocked / not_applicable. |
| `status_reason` | `Nullable(String)` | Oui | Projection explicite de int_demo_intervals.status_reason ; Cause précise stable ; NULL si aucune dépendance manquante. |
| `started_date_key` | `UInt32` | Non | Date Paris started_at. |
| `ended_date_key` | `UInt32` | Non | Date Paris ended_at. |

**Transformation / jointures :** Projection explicite, dates de rôle par calendrier N:1 même run. Aucun intervalle supplémentaire construit dans le fait. Quand une date métier sort des bornes générées, conserver la date et mettre la clé Nullable à NULL avec statut ; ne pas allonger le calendrier jusqu’à une fin sentinelle2099. Les labels ne remplacent pas les clés. Aucun filtre vers le run publié dans ce fait : l’historique des runs reste consultable.

**Agrégation et usage :** Moyenne/médiane/P90 recalculés sur délais admissibles après filtres ; pas durée d’agenda ni durée de Show Boond. Le nombre de lignes vides si preuves manquantes ne signifie pas délai0.

**Matérialisation, histoire, reprise et fraîcheur :** vue dbt, une requête SELECT avec colonnes énumérées ; pas de stockage supplémentaire ni de stratégie incrémentale propre. La vue expose les révisions conservées dans son intermédiaire. Les jointures annexes portent toujours même model_run_id ; aucune relecture d’un ancien run avec dimensions actuelles. Recréation de vue idempotente ; source d’histoire inchangée. Exécution manuelle D29, sans SLA de production ; publication au rythme du lot validé, datasets sélectionnant int_publication. Aucune garantie de performance avant mesure.

**Tests / acceptation :** unicité/non-NULL de (model_run_id,record_key), correspondance exacte des clés/projections amont, relations dimensionnelles au bon run, aucune multiplication de contributions. Égalité ligne/clé/durée int→fct ; aucune jointure cartésienne d’actions. Défaut de grain/cardinalité : ERROR, publication bloquée. Limite connue : NULL et statut sans inventer de chiffre.

**Limites / dépendances :** Vide actuellement si preuve/chaînage absents ; état d’indisponibilité porté par publication et datasets.


<a id="fct_mrr_movement"></a>

### `fct_mrr_movement`

**Grain métier :** Société × mois × composante nette de variation. **Clé :** movement_contribution_key ; record_key=H(tuple du grain), identique à la clé hashée amont. **Grain de révision :** (model_run_id,record_key).

**Amont exact :** `{{ ref('int_mrr_movements') }}`, `{{ ref('dim_date') }}`. **Destination :** `dtm_revenue.fct_mrr_movement`, `dbt/models/marts/revenue/fct_mrr_movement.sql`, YAML `dbt/models/marts/revenue/_models.yml`.

| Colonne | Type ClickHouse | Nullable | Origine, formule, contraintes |
|---|---|---|---|
| `model_run_id` | `String` | Non | Métadonnée amont int_mrr_movements.model_run_id ; row_hash recalculé sur le contrat final du fait si des colonnes techniques sont ajoutées. Empreinte SHA256 commune de la recomposition : manifeste des entrées figées, code, référentiels et paramètres ; fournie par orchestration, identique dans tout le DAG. |
| `record_key` | `String` | Non | Métadonnée amont int_mrr_movements.record_key ; row_hash recalculé sur le contrat final du fait si des colonnes techniques sont ajoutées. Identité String H(tuple du grain décrit, domaine/version explicite), sans model_run_id ; égale la clé de grain lorsque cette dernière est déjà hashée. dim_date utilise H(calendar_date), jamais date_key UInt32 brut. |
| `record_version_key` | `String` | Non | Métadonnée amont int_mrr_movements.record_version_key ; row_hash recalculé sur le contrat final du fait si des colonnes techniques sont ajoutées. H(model_run_id,record_key) ; unicité physique de la révision du modèle. |
| `row_hash` | `String` | Non | Métadonnée amont int_mrr_movements.row_hash ; row_hash recalculé sur le contrat final du fait si des colonnes techniques sont ajoutées. H(tuple ordonné de toutes les colonnes métier de la fiche, NULL et types préservés) ; exclut les métadonnées de calcul. |
| `calculated_at` | `DateTime64(3,'UTC')` | Non | Métadonnée amont int_mrr_movements.calculated_at ; row_hash recalculé sur le contrat final du fait si des colonnes techniques sont ajoutées. Instant de calcul du lot ; fixe pour un même model_run_id, jamais utilisé comme événement métier. |
| `rule_version` | `String` | Non | Métadonnée amont int_mrr_movements.rule_version ; row_hash recalculé sur le contrat final du fait si des colonnes techniques sont ajoutées. Empreinte immuable du code et des règles appliquées ; dérivée du manifeste du lot. |
| `input_cutoff_at` | `DateTime64(3,'UTC')` | Non | Métadonnée amont int_mrr_movements.input_cutoff_at ; row_hash recalculé sur le contrat final du fait si des colonnes techniques sont ajoutées. Date limite de connaissance de la recomposition ; les entrées exactes sont figées par le manifeste, pas par ce timestamp seul. |
| `source_published_at` | `Nullable(DateTime64(3,'UTC'))` | Oui | Métadonnée amont int_mrr_movements.source_published_at ; row_hash recalculé sur le contrat final du fait si des colonnes techniques sont ajoutées. Maximum de publication CDC des versions contribuant à la ligne ; NULL pour un référentiel exclusivement généré. Les entrées de règles non fournies proviennent du futur dbt/config/case_rules.yml fusionné dans vars, sans seed ou source implicite. Ce maximum ne remplace aucune date métier. |
| `source_version_keys` | `Array(String)` | Non | Métadonnée amont int_mrr_movements.source_version_keys ; row_hash recalculé sur le contrat final du fait si des colonnes techniques sont ajoutées. Clés des versions sources contributrices, triées et sans répétition ; union des lignages amont. Liste vide pour une ligne exclusivement générée. |
| `movement_contribution_key` | `String` | Non | Projection explicite de int_mrr_movements.movement_contribution_key ; H(company_key,month_date,movement_kind). |
| `tenant_id` | `String` | Non | Projection explicite de int_mrr_movements.tenant_id ; Tenant. |
| `client_context_key` | `String` | Non | Projection explicite de int_mrr_movements.client_context_key ; Contexte société/mois. |
| `company_id` | `Int64` | Non | Projection explicite de int_mrr_movements.company_id ; ID société. |
| `company_key` | `String` | Non | Projection explicite de int_mrr_movements.company_key ; Identité société. |
| `company_version_key` | `Nullable(String)` | Oui | Projection explicite de int_mrr_movements.company_version_key ; Version à clôture. |
| `month_date` | `Date` | Non | Projection explicite de int_mrr_movements.month_date ; Mois. |
| `month_end_date` | `Date` | Non | Projection explicite de int_mrr_movements.month_end_date ; Clôture courante. |
| `previous_month_end_date` | `Date` | Non | Projection explicite de int_mrr_movements.previous_month_end_date ; Clôture précédente. |
| `movement_kind` | `String` | Non | Projection explicite de int_mrr_movements.movement_kind ; new / upsell / departure / contraction / stable / unknown. |
| `new_mrr_component` | `Nullable(String)` | Oui | Projection explicite de int_mrr_movements.new_mrr_component ; New entrants/retours ;Upsell hausse restants ;NULL autres. |
| `sum_new_mrr` | `Nullable(Decimal(38,4))` | Oui | Projection explicite de int_mrr_movements.sum_new_mrr ; MRR après entrant ;max(après−avant,0) hausse restant ;NULL noncomparable. Aucune ligne total en plus. |
| `sum_departure_mrr` | `Nullable(Decimal(38,4))` | Oui | Projection explicite de int_mrr_movements.sum_departure_mrr ; MRR avant sortant ;0 autres cas comparables. |
| `sum_contraction_mrr` | `Nullable(Decimal(38,4))` | Oui | Projection explicite de int_mrr_movements.sum_contraction_mrr ; max(avant−après,0) restant baisse ;0 autres cas comparables. |
| `sum_candidate_new_mrr` | `Nullable(Decimal(38,4))` | Oui | Projection explicite de int_mrr_movements.sum_candidate_new_mrr ; Mêmeformule sur candidats,diagnostic devise inconnue. |
| `sum_candidate_departure_mrr` | `Nullable(Decimal(38,4))` | Oui | Projection explicite de int_mrr_movements.sum_candidate_departure_mrr ; Départs candidats. |
| `sum_candidate_contraction_mrr` | `Nullable(Decimal(38,4))` | Oui | Projection explicite de int_mrr_movements.sum_candidate_contraction_mrr ; Baisses candidates. |
| `is_portfolio_entrant` | `Nullable(Bool)` | Oui | Projection explicite de int_mrr_movements.is_portfolio_entrant ; Actifaprès/inactifavant,retours inclus. |
| `is_departure` | `Nullable(Bool)` | Oui | Projection explicite de int_mrr_movements.is_departure ; Actifavant/inactifaprès. |
| `is_contraction` | `Nullable(Bool)` | Oui | Projection explicite de int_mrr_movements.is_contraction ; Actifdeux clôtures et baissenette. |
| `is_active_before` | `Nullable(Bool)` | Oui | Projection explicite de int_mrr_movements.is_active_before ; Activitéavant. |
| `is_active_after` | `Nullable(Bool)` | Oui | Projection explicite de int_mrr_movements.is_active_after ; Activitéaprès. |
| `first_acquisition_status` | `String` | Non | Projection explicite de int_mrr_movements.first_acquisition_status ; Statut contexte,non déduit entrant seul. |
| `is_comparable` | `Nullable(Bool)` | Oui | Projection explicite de int_mrr_movements.is_comparable ; Deux clôtures/périmètre/devise compatibles. |
| `commercial_link_status` | `String` | Non | Projection explicite de int_mrr_movements.commercial_link_status ; not_required_for_financial_classification / proven / missing. |
| `source_lineage_status` | `String` | Non | Projection explicite de int_mrr_movements.source_lineage_status ; Clôtures et lignages expliquent montant sans le répéter par ligne. |
| `calculation_status` | `String` | Non | Projection explicite de int_mrr_movements.calculation_status ; ready / partial / blocked / not_applicable. |
| `status_reason` | `Nullable(String)` | Oui | Projection explicite de int_mrr_movements.status_reason ; Cause précise stable ; NULL si aucune dépendance manquante. |
| `month_date_key` | `UInt32` | Non | YYYYMMDD du premierjour du mois. |
| `closing_date_key` | `UInt32` | Non | YYYYMMDD de month_end_date. |
| `previous_closing_date_key` | `UInt32` | Non | YYYYMMDD de previous_month_end_date. |

**Transformation / jointures :** Projection explicite ; aucune jointure détail aux lignes. Clés de dates via calendrier N:1 même run. Quand une date métier sort des bornes générées, conserver la date et mettre la clé Nullable à NULL avec statut ; ne pas allonger le calendrier jusqu’à une fin sentinelle2099. Les labels ne remplacent pas les clés. Aucun filtre vers le run publié dans ce fait : l’historique des runs reste consultable.

**Agrégation et usage :** New total=somme sum_new_mrr sur New et Upsell, sans ligne total additionnelle ; churn=somme départs+baisses. Counts clients distinct company_key. Le filtre New/Upsell décrit apport financier, pas type commercial de dossier. Bloc global sans équipe.

**Matérialisation, histoire, reprise et fraîcheur :** vue dbt, une requête SELECT avec colonnes énumérées ; pas de stockage supplémentaire ni de stratégie incrémentale propre. La vue expose les révisions conservées dans son intermédiaire. Les jointures annexes portent toujours même model_run_id ; aucune relecture d’un ancien run avec dimensions actuelles. Recréation de vue idempotente ; source d’histoire inchangée. Exécution manuelle D29, sans SLA de production ; publication au rythme du lot validé, datasets sélectionnant int_publication. Aucune garantie de performance avant mesure.

**Tests / acceptation :** unicité/non-NULL de (model_run_id,record_key), correspondance exacte des clés/projections amont, relations dimensionnelles au bon run, aucune multiplication de contributions. Égalité montants et counts int→fct ; exemples de compensation intra-société/inter-sociétés contrôlés ; NULL officiel conservé. Défaut de grain/cardinalité : ERROR, publication bloquée. Limite connue : NULL et statut sans inventer de chiffre.

**Limites / dépendances :** Devise/coverage conditionnent montants officiels ; mouvements candidates nommés comme diagnostics.


<a id="fct_subscription_month_end"></a>

### `fct_subscription_month_end`

**Grain métier :** Ligne d’abonnement × clôture mensuelle. **Clé :** subscription_month_key ; record_key=H(tuple du grain), identique à la clé hashée amont. **Grain de révision :** (model_run_id,record_key).

**Amont exact :** `{{ ref('int_subscription_month_end') }}`, `{{ ref('dim_date') }}`. **Destination :** `dtm_revenue.fct_subscription_month_end`, `dbt/models/marts/revenue/fct_subscription_month_end.sql`, YAML `dbt/models/marts/revenue/_models.yml`.

| Colonne | Type ClickHouse | Nullable | Origine, formule, contraintes |
|---|---|---|---|
| `model_run_id` | `String` | Non | Métadonnée amont int_subscription_month_end.model_run_id ; row_hash recalculé sur le contrat final du fait si des colonnes techniques sont ajoutées. Empreinte SHA256 commune de la recomposition : manifeste des entrées figées, code, référentiels et paramètres ; fournie par orchestration, identique dans tout le DAG. |
| `record_key` | `String` | Non | Métadonnée amont int_subscription_month_end.record_key ; row_hash recalculé sur le contrat final du fait si des colonnes techniques sont ajoutées. Identité String H(tuple du grain décrit, domaine/version explicite), sans model_run_id ; égale la clé de grain lorsque cette dernière est déjà hashée. dim_date utilise H(calendar_date), jamais date_key UInt32 brut. |
| `record_version_key` | `String` | Non | Métadonnée amont int_subscription_month_end.record_version_key ; row_hash recalculé sur le contrat final du fait si des colonnes techniques sont ajoutées. H(model_run_id,record_key) ; unicité physique de la révision du modèle. |
| `row_hash` | `String` | Non | Métadonnée amont int_subscription_month_end.row_hash ; row_hash recalculé sur le contrat final du fait si des colonnes techniques sont ajoutées. H(tuple ordonné de toutes les colonnes métier de la fiche, NULL et types préservés) ; exclut les métadonnées de calcul. |
| `calculated_at` | `DateTime64(3,'UTC')` | Non | Métadonnée amont int_subscription_month_end.calculated_at ; row_hash recalculé sur le contrat final du fait si des colonnes techniques sont ajoutées. Instant de calcul du lot ; fixe pour un même model_run_id, jamais utilisé comme événement métier. |
| `rule_version` | `String` | Non | Métadonnée amont int_subscription_month_end.rule_version ; row_hash recalculé sur le contrat final du fait si des colonnes techniques sont ajoutées. Empreinte immuable du code et des règles appliquées ; dérivée du manifeste du lot. |
| `input_cutoff_at` | `DateTime64(3,'UTC')` | Non | Métadonnée amont int_subscription_month_end.input_cutoff_at ; row_hash recalculé sur le contrat final du fait si des colonnes techniques sont ajoutées. Date limite de connaissance de la recomposition ; les entrées exactes sont figées par le manifeste, pas par ce timestamp seul. |
| `source_published_at` | `Nullable(DateTime64(3,'UTC'))` | Oui | Métadonnée amont int_subscription_month_end.source_published_at ; row_hash recalculé sur le contrat final du fait si des colonnes techniques sont ajoutées. Maximum de publication CDC des versions contribuant à la ligne ; NULL pour un référentiel exclusivement généré. Les entrées de règles non fournies proviennent du futur dbt/config/case_rules.yml fusionné dans vars, sans seed ou source implicite. Ce maximum ne remplace aucune date métier. |
| `source_version_keys` | `Array(String)` | Non | Métadonnée amont int_subscription_month_end.source_version_keys ; row_hash recalculé sur le contrat final du fait si des colonnes techniques sont ajoutées. Clés des versions sources contributrices, triées et sans répétition ; union des lignages amont. Liste vide pour une ligne exclusivement générée. |
| `subscription_month_key` | `String` | Non | Projection explicite de int_subscription_month_end.subscription_month_key ; H(subscription_key,month_date). |
| `tenant_id` | `String` | Non | Projection explicite de int_subscription_month_end.tenant_id ; Tenant. |
| `subscription_key` | `String` | Non | Projection explicite de int_subscription_month_end.subscription_key ; Identité ligne. |
| `line_id` | `Int64` | Non | Projection explicite de int_subscription_month_end.line_id ; ID ligne. |
| `line_created_at` | `Nullable(DateTime64(3,'UTC'))` | Oui | Projection explicite int_subscription_month_end.line_created_at. |
| `is_creation_date_reliable` | `Bool` | Non | true seulement si création nonNULL constante entre versions, aucun CDC antérieur à cette création et aucun début de service antérieur contradictoire ; false sinon, pas de correction de la source. |
| `is_before_creation` | `Nullable(Bool)` | Oui | Avant la création prouvée à la clôture ; NULL si preuve insuffisante. Une date contradictoire ne prouve aucune absence. |
| `project_id` | `Nullable(Int64)` | Oui | Projection explicite de int_subscription_month_end.project_id ; Projet à clôture. |
| `company_id` | `Nullable(Int64)` | Oui | Projection explicite de int_subscription_month_end.company_id ; Société à clôture. |
| `company_key` | `Nullable(String)` | Oui | Projection explicite de int_subscription_month_end.company_key ; Identité société. |
| `company_version_key` | `Nullable(String)` | Oui | Projection explicite de int_subscription_month_end.company_version_key ; Version société à clôture. |
| `month_date` | `Date` | Non | Projection explicite de int_subscription_month_end.month_date ; Premier jour mois Paris. |
| `month_end_date` | `Date` | Non | Projection explicite de int_subscription_month_end.month_end_date ; Dernier jour mois Paris. |
| `closing_exclusive_at` | `DateTime64(3,'UTC')` | Non | Projection explicite de int_subscription_month_end.closing_exclusive_at ; Minuit Paris premier jour suivant converti UTC, photo juste avant. |
| `closing_date_key` | `UInt32` | Non | Projection explicite de int_subscription_month_end.closing_date_key ; YYYYMMDD de month_end_date. |
| `source_subscription_period_key` | `Nullable(String)` | Oui | Projection explicite de int_subscription_month_end.source_subscription_period_key ; Période observée à clôture ; NULL non observable. |
| `is_observable` | `Nullable(Bool)` | Oui | Projection explicite de int_subscription_month_end.is_observable ; Versions/liens nécessaires connus à clôture. |
| `is_active` | `Nullable(Bool)` | Oui | Projection explicite de int_subscription_month_end.is_active ; État1+période ; indépendant MRR>0. |
| `quantity` | `Nullable(Decimal(38,4))` | Oui | Projection explicite de int_subscription_month_end.quantity ; Quantité source. |
| `unit_monthly_price` | `Nullable(Decimal(38,4))` | Oui | Projection explicite de int_subscription_month_end.unit_monthly_price ; Prix mensuel unitaire. |
| `line_monthly_amount` | `Nullable(Decimal(38,4))` | Oui | Projection explicite de int_subscription_month_end.line_monthly_amount ; Montant mensuel total. |
| `candidate_active_mrr` | `Nullable(Decimal(38,4))` | Oui | Projection explicite de int_subscription_month_end.candidate_active_mrr ; Montant ligne actif ;0 si inactif prouvé ;NULL si inconnu. |
| `sum_active_mrr` | `Nullable(Decimal(38,4))` | Oui | Projection explicite de int_subscription_month_end.sum_active_mrr ; Somme officielle des lignes admissibles en EUR sous hypothèses D16/D20 ;NULL si activité/montant ou inventaire requis inconnus, sans prorata. |
| `currency_code` | `Nullable(String)` | Oui | Projection explicite de int_subscription_month_end.currency_code ; EUR par hypothèse explicite du case D20 ; cette devise ne prouve ni mensualité ni engagement du montant commercial. |
| `monetary_status` | `String` | Non | Projection explicite de int_subscription_month_end.monetary_status ; ready / currency_unconfirmed / missing_amount / unknown_activity. |
| `is_history_complete` | `Nullable(Bool)` | Oui | Projection explicite de int_subscription_month_end.is_history_complete ; Couverture clôture/liens déclarée. |
| `calculation_status` | `String` | Non | Projection explicite de int_subscription_month_end.calculation_status ; ready / partial / blocked / not_applicable. |
| `status_reason` | `Nullable(String)` | Oui | Projection explicite de int_subscription_month_end.status_reason ; Cause précise stable ; NULL si aucune dépendance manquante. |
| `month_date_key` | `Nullable(UInt32)` | Oui | YYYYMMDD du premier jour du mois si présent dans dim_date ; NULL sinon, date métier conservée. Adaptation technique constatée à l’implémentation : le calendrier commence au dernier jour du mois précédent, dont le premier jour peut être hors calendrier. |

**Transformation / jointures :** Projection explicite des clôtures, mêmes clés/qualité ; aucune nouvelle règle d’activité dans ce fait. Quand une date métier sort des bornes générées, conserver la date et mettre la clé Nullable à NULL avec statut ; ne pas allonger le calendrier jusqu’à une fin sentinelle2099. Les labels ne remplacent pas les clés. Aucun filtre vers le run publié dans ce fait : l’historique des runs reste consultable.

**Agrégation et usage :** MRR stock par mois, jamais somme intermois ; clients actifs distinct company_key dont is_active=true, jamais count lignes ou MRR>0. Montant0 actif reste client. Sommes officielles bloquées si contribution requise inconnue/devise non confirmée.

**Matérialisation, histoire, reprise et fraîcheur :** vue dbt, une requête SELECT avec colonnes énumérées ; pas de stockage supplémentaire ni de stratégie incrémentale propre. La vue expose les révisions conservées dans son intermédiaire. Les jointures annexes portent toujours même model_run_id ; aucune relecture d’un ancien run avec dimensions actuelles. Recréation de vue idempotente ; source d’histoire inchangée. Exécution manuelle D29, sans SLA de production ; publication au rythme du lot validé, datasets sélectionnant int_publication. Aucune garantie de performance avant mesure.

**Tests / acceptation :** unicité/non-NULL de (model_run_id,record_key), correspondance exacte des clés/projections amont, relations dimensionnelles au bon run, aucune multiplication de contributions. Égalité int→fct ; pas de double quantité ; nulls non transformés en0 ; compte société multi-lignes unique. Défaut de grain/cardinalité : ERROR, publication bloquée. Limite connue : NULL et statut sans inventer de chiffre.

**Limites / dépendances :** Disponibilité MRR EUR et complétude de clôture restent conditionnelles.



**Preuve avant création** : une date CRM seule ne réécrit pas un abonnement rétroactif. La création doit être cohérente avec toutes les versions et dates de service. Le contrôle complémentaire Q12 a trouvé194/214 créations postérieures à une publication : ce défaut de chronologie reste signalé et interdit seulement cette inférence d’absence ; il ne supprime pas une période observée ni ses contributions admissibles.

<a id="fct_sales_objectives_month"></a>

### `fct_sales_objectives_month`

**Grain métier :** Mois × équipe/segment × indicateur ciblé. **Clé :** objective_month_key ; record_key=H(tuple du grain), identique à la clé hashée amont. **Grain de révision :** (model_run_id,record_key).

**Amont exact :** `{{ ref('int_sales_objectives_month') }}`, `{{ ref('dim_date') }}`. **Destination :** `dtm_revenue.fct_sales_objectives_month`, `dbt/models/marts/revenue/fct_sales_objectives_month.sql`, YAML `dbt/models/marts/revenue/_models.yml`.

| Colonne | Type ClickHouse | Nullable | Origine, formule, contraintes |
|---|---|---|---|
| `model_run_id` | `String` | Non | Métadonnée amont int_sales_objectives_month.model_run_id ; row_hash recalculé sur le contrat final du fait si des colonnes techniques sont ajoutées. Empreinte SHA256 commune de la recomposition : manifeste des entrées figées, code, référentiels et paramètres ; fournie par orchestration, identique dans tout le DAG. |
| `record_key` | `String` | Non | Métadonnée amont int_sales_objectives_month.record_key ; row_hash recalculé sur le contrat final du fait si des colonnes techniques sont ajoutées. Identité String H(tuple du grain décrit, domaine/version explicite), sans model_run_id ; égale la clé de grain lorsque cette dernière est déjà hashée. dim_date utilise H(calendar_date), jamais date_key UInt32 brut. |
| `record_version_key` | `String` | Non | Métadonnée amont int_sales_objectives_month.record_version_key ; row_hash recalculé sur le contrat final du fait si des colonnes techniques sont ajoutées. H(model_run_id,record_key) ; unicité physique de la révision du modèle. |
| `row_hash` | `String` | Non | Métadonnée amont int_sales_objectives_month.row_hash ; row_hash recalculé sur le contrat final du fait si des colonnes techniques sont ajoutées. H(tuple ordonné de toutes les colonnes métier de la fiche, NULL et types préservés) ; exclut les métadonnées de calcul. |
| `calculated_at` | `DateTime64(3,'UTC')` | Non | Métadonnée amont int_sales_objectives_month.calculated_at ; row_hash recalculé sur le contrat final du fait si des colonnes techniques sont ajoutées. Instant de calcul du lot ; fixe pour un même model_run_id, jamais utilisé comme événement métier. |
| `rule_version` | `String` | Non | Métadonnée amont int_sales_objectives_month.rule_version ; row_hash recalculé sur le contrat final du fait si des colonnes techniques sont ajoutées. Empreinte immuable du code et des règles appliquées ; dérivée du manifeste du lot. |
| `input_cutoff_at` | `DateTime64(3,'UTC')` | Non | Métadonnée amont int_sales_objectives_month.input_cutoff_at ; row_hash recalculé sur le contrat final du fait si des colonnes techniques sont ajoutées. Date limite de connaissance de la recomposition ; les entrées exactes sont figées par le manifeste, pas par ce timestamp seul. |
| `source_published_at` | `Nullable(DateTime64(3,'UTC'))` | Oui | Métadonnée amont int_sales_objectives_month.source_published_at ; row_hash recalculé sur le contrat final du fait si des colonnes techniques sont ajoutées. Maximum de publication CDC des versions contribuant à la ligne ; NULL pour un référentiel exclusivement généré. Les entrées de règles non fournies proviennent du futur dbt/config/case_rules.yml fusionné dans vars, sans seed ou source implicite. Ce maximum ne remplace aucune date métier. |
| `source_version_keys` | `Array(String)` | Non | Métadonnée amont int_sales_objectives_month.source_version_keys ; row_hash recalculé sur le contrat final du fait si des colonnes techniques sont ajoutées. Clés des versions sources contributrices, triées et sans répétition ; union des lignages amont. Liste vide pour une ligne exclusivement générée. |
| `objective_month_key` | `String` | Non | Projection explicite de int_sales_objectives_month.objective_month_key ; H(tenant_id,month_date,source_segment,metric_code). |
| `tenant_id` | `String` | Non | Projection explicite de int_sales_objectives_month.tenant_id ; Var source_tenant_id=demo_crm,contexte explicite de ce jeu. |
| `month_date` | `Date` | Non | Projection explicite de int_sales_objectives_month.month_date ; src_month_date,premierjourParis. |
| `month_end_date` | `Date` | Non | Projection explicite de int_sales_objectives_month.month_end_date ; Dernierjourmois. |
| `closing_exclusive_at` | `DateTime64(3,'UTC')` | Non | Projection explicite de int_sales_objectives_month.closing_exclusive_at ; MinuitParis mois suivant reconvertiUTC. |
| `source_segment` | `String` | Non | Projection explicite de int_sales_objectives_month.source_segment ; src_segment SMB/LA/ES. |
| `team_key` | `Nullable(String)` | Oui | Projection explicite de int_sales_objectives_month.team_key ; Équipe si mappingunivoque. |
| `team_version_key` | `Nullable(String)` | Oui | Projection explicite de int_sales_objectives_month.team_version_key ; Version à date pertinente. |
| `metric_code` | `String` | Non | Projection explicite de int_sales_objectives_month.metric_code ; src_indicator,quatre codes. |
| `metric_key` | `String` | Non | Projection explicite de int_sales_objectives_month.metric_key ; Identité dim_metric. |
| `metric_version_key` | `String` | Non | Projection explicite de int_sales_objectives_month.metric_version_key ; Version définition mesure. |
| `target_version_key` | `String` | Non | Projection explicite de int_sales_objectives_month.target_version_key ; source_version_key captureobjectif choisie. |
| `target_value` | `Nullable(Decimal(38,4))` | Oui | Projection explicite de int_sales_objectives_month.target_value ; src_target convertiDecimal,aucuneventilationpersonnelle. |
| `actual_value` | `Nullable(Decimal(38,4))` | Oui | Projection explicite de int_sales_objectives_month.actual_value ; RéaliséOFFICIEL compatible ;NULL sans preuves montant/unité/tenue. |
| `candidate_actual_value` | `Nullable(Decimal(38,4))` | Oui | Projection explicite de int_sales_objectives_month.candidate_actual_value ; Diagnostic réalisé source si possible,jamais substitutofficiel. |
| `value_unit` | `String` | Non | Projection explicite de int_sales_objectives_month.value_unit ; Unitémesure ;compatibilitécible/réalisé àprouver. |
| `variance_value` | `Nullable(Decimal(38,4))` | Oui | Projection explicite de int_sales_objectives_month.variance_value ; actual_value−target_value sicalculable/compatible. |
| `attainment_numerator` | `Nullable(Decimal(38,4))` | Oui | Projection explicite de int_sales_objectives_month.attainment_numerator ; actual_value sicompatible. |
| `attainment_denominator` | `Nullable(Decimal(38,4))` | Oui | Projection explicite de int_sales_objectives_month.attainment_denominator ; target_value sicompatible et>0 ;sinon NULL. |
| `attainment_rate` | `Nullable(Float64)` | Oui | Projection explicite de int_sales_objectives_month.attainment_rate ; actual/target si>0 etcompatible,sinon NULL. |
| `is_population_compatible` | `Nullable(Bool)` | Oui | Projection explicite de int_sales_objectives_month.is_population_compatible ; Population/type/période/unité compatibles ;NULL sinondéfinies. |
| `nb_source_contributions` | `Nullable(UInt64)` | Oui | Projection explicite de int_sales_objectives_month.nb_source_contributions ; Contributionsdistinctes avant somme. |
| `nb_uncalculable_contributions` | `Nullable(UInt64)` | Oui | Projection explicite de int_sales_objectives_month.nb_uncalculable_contributions ; Contributionsrequises inconnues ;NULL si absence de preuve globale empêche de les dénombrer. |
| `is_month_closed` | `Bool` | Non | Projection explicite de int_sales_objectives_month.is_month_closed ; Clôtureexclusive<=cutoff. |
| `is_team_calculable` | `Bool` | Non | Projection explicite de int_sales_objectives_month.is_team_calculable ; Mapping équipeunivoque. |
| `target_selection_status` | `String` | Non | Projection explicite de int_sales_objectives_month.target_selection_status ; capture_selected / ambiguous_target / missing_target. |
| `calculation_status` | `String` | Non | Projection explicite de int_sales_objectives_month.calculation_status ; ready / partial / blocked / not_applicable. |
| `status_reason` | `Nullable(String)` | Oui | Projection explicite de int_sales_objectives_month.status_reason ; Cause précise stable ; NULL si aucune dépendance manquante. |
| `month_date_key` | `UInt32` | Non | YYYYMMDD de month_date. |
| `closing_date_key` | `UInt32` | Non | YYYYMMDD de month_end_date. |

**Transformation / jointures :** Projection explicite des comparaisons déjà préparées ; pas de nouvelle agrégation de faits détaillés. Quand une date métier sort des bornes générées, conserver la date et mettre la clé Nullable à NULL avec statut ; ne pas allonger le calendrier jusqu’à une fin sentinelle2099. Les labels ne remplacent pas les clés. Aucun filtre vers le run publié dans ce fait : l’historique des runs reste consultable.

**Agrégation et usage :** Global compatible : sommeactual/sommetarget, jamais moyenne attainment_rate. Pondéré est stock de fin de mois ; ne pas additionner stocks des mois. Filtres non compatibles rendent comparaison indisponible. Aucune cible personnelle.

**Matérialisation, histoire, reprise et fraîcheur :** vue dbt, une requête SELECT avec colonnes énumérées ; pas de stockage supplémentaire ni de stratégie incrémentale propre. La vue expose les révisions conservées dans son intermédiaire. Les jointures annexes portent toujours même model_run_id ; aucune relecture d’un ancien run avec dimensions actuelles. Recréation de vue idempotente ; source d’histoire inchangée. Exécution manuelle D29, sans SLA de production ; publication au rythme du lot validé, datasets sélectionnant int_publication. Aucune garantie de performance avant mesure.

**Tests / acceptation :** unicité/non-NULL de (model_run_id,record_key), correspondance exacte des clés/projections amont, relations dimensionnelles au bon run, aucune multiplication de contributions. Une cible une fois au grain ; NULL des réalisés/taux conservés ; compteurs inconnus visibles. Défaut de grain/cardinalité : ERROR, publication bloquée. Limite connue : NULL et statut sans inventer de chiffre.

**Limites / dépendances :** Unités/source signée/proof démos/mapping équipe et populations bloquent comparaison officielle.

## D. Couche DTR et datasets — 20 modèles métier

**Statut : spécification, pas implémentation.** Ces fiches appliquent les décisions et contrats transversaux du document 01. Les dix paires constituent six familles pour les trois dashboards et leur navigation, puis quatre familles couvrant le reste du catalogue. Elles ne créent ni un KPI par graphique ni une réduction du besoin aux seules images.

| Famille | DTR historique | Dataset publié | Usage |
|---|---|---|---|
| Trois dashboards — Synthèse | `dtr_sales_objectives_month` | `dataset_sales_objectives_month` | tenant_id × month_date × team_key × metric_code ; une cible et un réalisé compatibles par ligne |
| Trois dashboards — Synthèse / Tunnel | `dtr_funnel_progress` | `dataset_funnel_progress` | tenant_id × opportunity_key × définition de parcours × anchor_at × target_stage_id ; une contribution de dossier par étape cible |
| Trois dashboards — Synthèse / MRR | `dtr_company_mrr_month` | `dataset_company_mrr_month` | tenant_id × company_key × closing_date ; une ligne par société aux deux clôtures comparées |
| Trois dashboards — Durées | `dtr_stage_visits` | `dataset_stage_visits` | tenant_id × visit_key ; un passage continu d'une opportunité dans une étape |
| Trois dashboards — Cohortes | `dtr_cohort_outcomes` | `dataset_cohort_outcomes` | tenant_id × opportunity_key × followup_definition_key × anchor_at × horizon_days ; une opportunité de sa cohorte de création par horizon |
| Trois dashboards — Navigation et investigation | `dtr_opportunity_timeline` | `dataset_opportunity_timeline` | tenant_id × object_kind × object_key ; une unité logique de période/passage/événement/tranche de responsabilité |
| Reste du catalogue — pipeline à date et historique | `dtr_pipeline_periods` | `dataset_pipeline_periods` | tenant_id × period_key ; intervalle analytique stable d'une opportunité |
| Reste du catalogue — flux commerciaux et cycle | `dtr_sales_events` | `dataset_sales_events` | tenant_id × event_key ; un événement commercial admissible d'un dossier |
| Reste du catalogue — demandes et rendez-vous de démo | `dtr_sales_actions` | `dataset_sales_actions` | tenant_id × action_key ; état corrigé pertinent d'une action logique dans le run |
| Reste du catalogue — extension micro-funnel démo | `dtr_demo_intervals` | `dataset_demo_intervals` | tenant_id × demo_interval_key ; intervalle entre deux événements reliés d'un parcours établi |

### Contrat physique, temporel et de publication de ces vingt modèles

- Toutes les relations ci-dessous sont dans la base ClickHouse `dtr_sales` (schema dbt exact, sans préfixe de cible ajouté). Modèles SQL : `dbt/models/reporting/dtr/dtr_<nom>.sql` et `dbt/models/reporting/datasets/dataset_<nom>.sql`. YAML : `_models.yml` dans chacun des deux dossiers ; descriptions complètes du modèle ET de chaque colonne.
- Les dix DTR sont des tables `MergeTree`, `ORDER BY (model_run_id, record_key)`, sans TTL et sans partitionnement supplémentaire en v1 à ce volume. Elles conservent les résultats COMPLETS de chaque empreinte de run ; append incrémental, `unique_key='record_version_key'`, `on_schema_change='fail'`, `full_refresh=false`, sans `inserts_only=true`, anti-jointure idempotente sur run+record_key et protocole de reprise du document 03. Cette configuration de unique_key laisse passer le contrôle de schéma de l'adaptateur1.10.1 ; elle ne garantit aucune déduplication. Le chemin inserts_only court-circuiterait ce contrôle et n'est pas retenu. Ce choix physique est une proposition, pas un gain de performance mesuré.
- Les dix datasets sont des vues de projection explicite de leur DTR, jointes au seul run courant de `int_publication`. Ils ne recalculent aucune règle commerciale. Ils ne disposent pas de paramètres SQL cachés : les paramètres d'observation/période/filtres sont dans les requêtes BI typées.
- Toutes les entrées dérivées d'une DTR portent le MÊME `model_run_id`. Chaque jointure ajoute ce champ ; les dimensions se joignent sur leur clé de version, jamais uniquement sur l'identité. Une jointure attendue N:0..1 conserve l'inconnu avec LEFT JOIN et `join_use_nulls=1`, et échoue au contrôle de cardinalité si plusieurs versions concordent. Aucun DISTINCT ne masque une multiplication.
- Les colonnes techniques communes sont réénumérées dans CHAQUE dictionnaire ci-dessous. `record_key` identifie l'unité logique propre au grain ; `record_version_key=H(model_run_id,record_key)`. `row_hash` porte le payload ordonné, NULL/types préservés. Aucun nouveau run ni nouvelle ligne pour une empreinte identique ; aucune mise à jour du passé stocké. Une ligne absente du nouveau snapshot cesse d'être courante sans effacement des anciens runs.
- Les transformations DTR utilisent le run demandé par `model_run_id` et ne dépendent JAMAIS de `int_publication`. La publication vient après tous contrôles. Pour tester un candidat avant bascule, interroger les DTR avec `test_model_run_id`, pas les datasets courants. Le bootstrap produit des vues vides tant qu'aucun run n'est accepté.
- Lecture par défaut : passé corrigé dans le run publié. Les révisions anciennes restent consultables techniquement via DTR+run explicite. L'observation métier O et le cutoff de connaissance `input_cutoff_at` sont distincts. Le cutoff ne garantit pas la couverture métier jusqu'à cette date. La sérialisation H et l'empreinte immuable du run suivent exactement01§4.2 bis ; tentatives, calculated_at et captures vides sans changement n'y créent pas artificiellement de nouvelles données.
- Les instants sont `DateTime64(3,'UTC')`, les mois et horizons civils utilisent Europe/Paris. Clôture=borne exclusive au début du mois suivant ; pour une période, `valid_from_at < closing_boundary_at` et `valid_to_at >= closing_boundary_at` ou fin NULL. Une observation ponctuelle ordinaire satisfait début<=O<fin. Aucune soustraction arbitraire d'une seconde.
- Les durées sont des millisecondes UTC écoulées /1000, puis /86400 pour les jours continus, sans troncature. Les horizons J+H ajoutent H jours calendaires en Paris à même heure locale, puis reviennent en UTC : un changement d'heure produit23/25 h, pas forcément24 h. `quantileExactInclusive`/`quantilesExactInclusive` définissent médiane/P90 ; le contrôle serveur [1,2,3,4] a donné2.5/3.7. Cela vérifie la fonction, pas les KPI des données métier.
- Montants canoniques `Decimal(38,4)`, probabilités `Decimal(18,8)`, ratios `Nullable(Float64)`. Pas d'arrondis intermédiaires ; formatage final à2 décimales selon la règle Decimal du document 01. Aucun libellé EUR ni somme officielle entre devises non prouvées.
- `calculation_status` de ligne vaut ready/partial/blocked/not_applicable. `status_reason` donne les causes stables. Ce statut ne remplace pas les disponibilités PAR MESURE : un volume peut être calculable quand le montant de la même ligne est bloqué.
- Avant toute carte/agrégation, lire `dataset_publication_status`, vue technique définie dans 01, au grain run×measure_id. Elle existe même si une DTR métier n'a aucune ligne, et expose les états available/partial/blocked_definition/blocked_evidence/non_mature/not_observable/not_applicable, motif, couverture et nb_expected/nb_known. Un dataset vide sans preuve ne devient jamais zéro. Les dix datasets métier ne gagnent aucune ligne artificielle de statut.
- Toutes les réponses BI transportent `model_run_id`. Si plusieurs requêtes d'une page chevauchent une bascule, comparer les runs et recharger l'ensemble des blocs ; ne pas montrer un mélange. La navigation transmet run+tenant+identité et détecte le changement de publication. Une simple égalité sur ancien run dans une vue courante ne permet pas la relecture historique : utiliser la DTR technique correspondante.
- Le rafraîchissement n'a pas de cadence/SLA métier décidés. À chaque run explicitement lancé : construire ces DTR après leurs faits/dimensions, contrôler grain/digest/disponibilités, puis publier atomiquement. Les vues reflètent alors la publication ; aucune promesse de fraîcheur quotidienne inventée.

### Paramètres des requêtes BI et portée

| Paramètre logique | Type | Contrat |
|---|---|---|
| tenant_id | String obligatoire | Toujours lié aux filtres d'identité ; ne pas mélanger tenants par défaut. |
| observation_at | DateTime64(3,'UTC') | Date métier d'observation explicite, UI Europe/Paris puis conversion UTC ; bornée par la couverture déclarée de la famille. NULL/absence impose sélection explicite, sans `now()` caché. |
| period_from_at / period_to_at | DateTime64(3,'UTC') | Intervalle semi-ouvert, converti et validé avant la requête ; la fiche détermine s'il filtre entrée de passage, création, flux ou autre date. |
| cohort_from_month / cohort_to_month | Date | Premiers jours de mois Paris, borne haute exclue ; sans assimilation au mois de signature. |
| sale_type_ids | Array(Int64) | Sélection du type commercial d'ancrage ; un tableau vide signifie aucun filtre seulement si l'UI l'annonce. Ne filtre pas le portefeuille MRR. |
| team_keys / channel_keys | Array(String) | Seulement si disponibilité et attribution de la mesure le permettent. Aucun filtre officiel sur code candidat. Filtre équipe durée activé sur entry_team_key connu D25 ; nonattribués conservés globalement. |
| closing_month | Date | Mois unique pour cartes/cascade portefeuille et objectifs ; plage autorisée uniquement pour série, sans somme des stocks. |
| horizon_days | UInt16 | 30/60/90 pour cohortes ; définition/horizon distincts dans tous regroupements. |
| threshold_days | Nullable(Float64) | Valeur>=0 fournie explicitement et unité compatible. Absence=>résultat d'alerte NULL, availability_reason=missing_threshold ; défaut21jours D26, paramétrable ; désactivation explicite permise. |
| duration_bins | Liste ordonnée de bornes numériques | Classes sans chevauchement, intervalles [borne basse,borne haute), dernière haute ouverte ; jeu explicitement fourni/versionné. Classes décidées D26 :[0,7),[7,14),[14,30),[30,+inf), modifiables explicitement ; aucune borne implicite ou trou. |
| financial_new_mrr_component | New/Upsell/toutes | Détail financier seulement ; ne retire ni stocks ni pertes de la cascade complète. |

Les paramètres sont transmis par l'API de requête du consommateur comme valeurs typées (syntaxe ClickHouse `{nom:Type}` dans les exemples), jamais comme fragments SQL libres ni interpolation des libellés. La BI prépare les bornes calendaires ; les clauses WHERE comparent ensuite directement les colonnes et paramètres. Tous les tris/formatages/arrondis d'affichage, couleurs et libellés français appartiennent à la restitution. Les contributions, clés, bornes, statuts, règles d'éligibilité et preuves restent dans dbt.

Une somme officielle exige la complétude des contributions requises et la disponibilité correspondante : `sum` ignorant les NULL n'est pas une preuve. Un total partiel ne peut être affiché qu'avec libellé explicitement partiel, nb_known/nb_expected et limites. Le dénominateur nul/inconnu donne un ratio NULL. Les filtres indisponibles sont désactivés avec motif, sans envoyer une requête de filtre qui viderait silencieusement l'écran.


<a id="dtr_sales_objectives_month"></a>

### `dtr_sales_objectives_month`

**Couche/module :** DTR, Trois dashboards — Synthèse. **Finalité :** Synthèse : quatre cartes, jauges d'atteinte et écarts ; mois et global/équipe. Les filtres locaux du tunnel et le filtre financier New/Upsell ne s'appliquent pas.

**Grain métier :** tenant_id × month_date × source_segment × metric_code ; segment Sales de la cible, équipe résolue seulement si mapping univoque. **Identité logique :** `record_key=H(tenant_id, month_date, source_segment, metric_code)`. **Grain historique/physique :** `(model_run_id,record_key)` ; version=H(run,key), une seule contribution par unité dans un run. Les clés métier et de dimensions sont conservées ci-dessous.

**Amont exact :** `{{ ref('fct_sales_objectives_month') }}`, `{{ ref('dim_team') }}`, `{{ ref('dim_metric') }}`. **Destination :** `dtr_sales.dtr_sales_objectives_month` ; fichier `dbt/models/reporting/dtr/dtr_sales_objectives_month.sql`, YAML `dbt/models/reporting/dtr/_models.yml`.

| Colonne | Type ClickHouse | Nullable | Origine, formule et contraintes |
|---|---|---|---|
| `model_run_id` | `String` | Non | Identifiant de la recomposition complète et immuable ; hérité des entrées du même run. |
| `record_key` | `String` | Non | SHA256 de la liste ordonnée des éléments du grain indiquée dans la fiche ; sérialisation canonique commune, jamais simple concaténation ambiguë. |
| `record_version_key` | `String` | Non | SHA256 de (model_run_id, record_key). |
| `row_hash` | `String` | Non | SHA256 du payload ordonné de la fiche, hors colonnes techniques communes. |
| `calculated_at` | `DateTime64(3, 'UTC')` | Non | Instant de calcul du run ; aucune substitution à une date métier. |
| `rule_version` | `String` | Non | Version immuable des règles et référentiels utilisés par le run. |
| `input_cutoff_at` | `DateTime64(3, 'UTC')` | Non | Borne des entrées figées ; héritée du manifeste de run. |
| `tenant_id` | `String` | Non | Fait : tenant de la comparaison. |
| `month_date` | `Date` | Non | Fait : premier jour du mois de reporting Europe/Paris. |
| `source_segment` | `String` | Non | fct_sales_objectives_month.source_segment : SMB/LA/ES ; identité du segment de cible sans fabriquer une businessunit. |
| `team_key` | `Nullable(String)` | Oui | fct_sales_objectives_month.team_key ; NULL si mapping source_segment→équipe non résolu. La clé du grain utilise source_segment pour préserver les cibles non rapprochées. |
| `team_version_key` | `Nullable(String)` | Oui | Fait : version pertinente de l'équipe ; NULL si mapping non résolu. |
| `team_name` | `Nullable(String)` | Oui | dim_team.team_name, jointure par model_run_id + team_version_key. |
| `metric_code` | `String` | Non | Fait : mrr_signed, pipeline_generated, pipeline_weighted ou demos. |
| `metric_key` | `String` | Non | Fait : identité de l'indicateur. |
| `metric_version_key` | `String` | Non | Version de dim_metric utilisée par le run. |
| `metric_label` | `Nullable(String)` | Oui | dim_metric.metric_label ; une ligne de dimension au plus. |
| `value_unit` | `String` | Non | fct_sales_objectives_month.value_unit, déclaration attendue de mesure (peut marquer pipeline non confirmé) ; ne prouve pas la comparabilité du réalisé. Ce dernier reste NULL sans unité validée. |
| `actual_value` | `Nullable(Decimal(38,4))` | Oui | Fait : réalisé de la population compatible, jamais un candidat monétaire promu sans validation. |
| `target_value` | `Nullable(Decimal(38,4))` | Oui | Fait : cible versionnée de la même équipe et du même mois. |
| `variance_value` | `Nullable(Decimal(38,4))` | Oui | actual_value - target_value seulement si les deux valeurs et leur comparabilité sont connues. |
| `attainment_rate` | `Nullable(Float64)` | Oui | actual_value / target_value si cible > 0 et valeurs comparables ; affichage ×100 dans la BI. |
| `is_population_compatible` | `Nullable(Bool)` | Oui | Population4/7 décidée D22 ; compatibilité d’unité/date vérifiée séparément, NULL si preuve d’unité manque. |
| `nb_source_contributions` | `Nullable(UInt64)` | Oui | Nombre de contributions logiques examinées dans le réalisé, s'il est disponible dans le fait. |
| `nb_uncalculable_contributions` | `Nullable(UInt64)` | Oui | Nombre de contributions dont le calcul reste inconnu ; ne prouve pas à lui seul la complétude de la source. |
| `calculation_status` | `String` | Non | ready/partial/blocked/not_applicable ; statut transmis et combiné aux contrôles de jointure. |
| `status_reason` | `Nullable(String)` | Oui | Motif explicite : unconfirmed_amount_unit, missing_team_mapping, missing_demo_completion_proof, incompatible_population, missing_target, zero_target, ou motif du fait. |

**Jointures, identités et cardinalités :** Fait → dim_team et dim_metric : N:0..1 sur (model_run_id, <objet>_version_key), LEFT JOIN et join_use_nulls=1. Ne pas rejoindre le détail opportunité/action ni les cibles brutes. Les compteurs de source peuvent être calculés dans int_sales_objectives_month puis transmis : leur absence laisse NULL.

**Étapes du calcul :** Projection du fait canonique. Contrôler une ligne par tenant/mois/équipe/indicateur avant publication. Si une composante financière ou la preuve de réalisation manque, conserver la cible, l'identité et les statuts, avec actual_value, variance_value et attainment_rate NULL pour la mesure concernée. Aucun passage de montant candidat à KPI officiel.

**Filtrage, paramètres et agrégation :** Période : month_date >= début de mois et < mois suivant la fin sélectionnée. Équipe : égalité sur team_key, ou toutes. L'observation n'est pas une date de flux : les cartes contrôlent la clôture du mois. Cohorte, canal, type commercial et seuil ne sont pas des filtres de ces cartes tant que le périmètre des objectifs ne les permet pas. Le segment de cible peut être consulté via source_segment même si team_key=NULL ; aucune assimilation implicite segment↔businessunit. Filtrer un metric_code à la fois. Pour une même clôture et des équipes disjointes/compatibles, somme des réalisés et des cibles, puis écart et taux recalculés. Si une équipe sélectionnée a un réalisé inconnu ou incomplet, résultat officiel global NULL et couverture affichée ; sum() ne doit pas ignorer silencieusement ce NULL. Aucun total entre les quatre indicateurs ; pipeline_weighted ne se somme pas entre mois.

**Matérialisation/histoire :** appliquer le contrat DTR commun ci-dessus : résultats complets du run, incremental append, engine MergeTree, ORDER BY(model_run_id,record_key), unique_key record_version_key, on_schema_change fail, full_refresh false et pas inserts_only. Les tables DTR conservent les anciens runs ; aucun filtre max de date métier ou limite à hier. Au premier chargement/cible vide, calculer l'ensemble ; en reprise, conserver seulement les clés du candidat absentes de la cible, sans modifier un payload existant.

**Contrat de chargement dbt :** une requête SELECT, CTE candidates explicite issue des transformations décrites. Chaque colonne du dictionnaire est produite exactement une fois. Terminer par la projection explicite de candidates ; sous `{% if is_incremental() %}`, LEFT ANTI JOIN de `{{ this }}` sur model_run_id et record_key. Tester absence de deux payloads différents pour une même clé/run AVANT chargement. Le unique_key de configuration assure le chemin de contrôle de schéma de l'adaptateur, pas la déduplication. Les entrées du run et le cutoff sont figés avant toute écriture future ; reprise du même run à empreinte inchangée.

**Construction/rafraîchissement :** après tous amonts du même run ; branches indépendantes parallélisables selon DAG. Exécution manuelle D29 ; fraîcheur de capture/publication déclarée, calcul puis tests/digest et publication contrôlée. Les requêtes de contrôle avant publication utilisent test_model_run_id. Aucun service/modèle n'est créé par la présente fiche.

**Tests/acceptation :** Unicité du grain ; quatre domaines metric_code ; mêmes unités/populations pour actual/target ; cible absente ou nulle donne taux NULL ; aucun facteur de duplication après dimensions ; global compatible = recomposition des composantes. Contrôles communs ERROR de grain, hash, cardinalité et run ; WARN/indisponibilité pour manque descriptif ou preuve comme décrit dans le contrat. Tests métier ci-dessus planifiés, pas exécutés sur une implémentation inexistante.


<a id="dataset_sales_objectives_month"></a>

### `dataset_sales_objectives_month`

**Couche/module :** dataset de restitution, Trois dashboards — Synthèse. **Finalité/consommateurs :** Synthèse : quatre cartes, jauges d'atteinte et écarts ; mois et global/équipe. Les filtres locaux du tunnel et le filtre financier New/Upsell ne s'appliquent pas.

**Grain métier et version :** exactement celui de `dtr_sales_objectives_month` : tenant_id × month_date × source_segment × metric_code ; segment Sales de la cible, équipe résolue seulement si mapping univoque. Une seule publication est visible ; identité et version sont conservées sans recalcul. Aucun total ni ligne artificielle n'est ajouté.

**Amont exact :** `{{ ref('dtr_sales_objectives_month') }}` et `{{ ref('int_publication') }}`. **Destination :** `dtr_sales.dataset_sales_objectives_month` ; fichier `dbt/models/reporting/datasets/dataset_sales_objectives_month.sql`, YAML `dbt/models/reporting/datasets/_models.yml`.

| Colonne | Type ClickHouse | Nullable | Origine, formule et contraintes |
|---|---|---|---|
| `model_run_id` | `String` | Non | Projection sans changement de dtr_sales_objectives_month.model_run_id. Identifiant de la recomposition complète et immuable ; hérité des entrées du même run. |
| `record_key` | `String` | Non | Projection sans changement de dtr_sales_objectives_month.record_key. SHA256 de la liste ordonnée des éléments du grain indiquée dans la fiche ; sérialisation canonique commune, jamais simple concaténation ambiguë. |
| `record_version_key` | `String` | Non | Projection sans changement de dtr_sales_objectives_month.record_version_key. SHA256 de (model_run_id, record_key). |
| `row_hash` | `String` | Non | Projection sans changement de dtr_sales_objectives_month.row_hash. SHA256 du payload ordonné de la fiche, hors colonnes techniques communes. |
| `calculated_at` | `DateTime64(3, 'UTC')` | Non | Projection sans changement de dtr_sales_objectives_month.calculated_at. Instant de calcul du run ; aucune substitution à une date métier. |
| `rule_version` | `String` | Non | Projection sans changement de dtr_sales_objectives_month.rule_version. Version immuable des règles et référentiels utilisés par le run. |
| `input_cutoff_at` | `DateTime64(3, 'UTC')` | Non | Projection sans changement de dtr_sales_objectives_month.input_cutoff_at. Borne des entrées figées ; héritée du manifeste de run. |
| `tenant_id` | `String` | Non | Projection sans changement de dtr_sales_objectives_month.tenant_id. Fait : tenant de la comparaison. |
| `month_date` | `Date` | Non | Projection sans changement de dtr_sales_objectives_month.month_date. Fait : premier jour du mois de reporting Europe/Paris. |
| `source_segment` | `String` | Non | Projection sans changement de dtr_sales_objectives_month.source_segment. fct_sales_objectives_month.source_segment : SMB/LA/ES ; identité du segment de cible sans fabriquer une businessunit. |
| `team_key` | `Nullable(String)` | Oui | Projection sans changement de dtr_sales_objectives_month.team_key. fct_sales_objectives_month.team_key ; NULL si mapping source_segment→équipe non résolu. La clé du grain utilise source_segment pour préserver les cibles non rapprochées. |
| `team_version_key` | `Nullable(String)` | Oui | Projection sans changement de dtr_sales_objectives_month.team_version_key. Fait : version pertinente de l'équipe ; NULL si mapping non résolu. |
| `team_name` | `Nullable(String)` | Oui | Projection sans changement de dtr_sales_objectives_month.team_name. dim_team.team_name, jointure par model_run_id + team_version_key. |
| `metric_code` | `String` | Non | Projection sans changement de dtr_sales_objectives_month.metric_code. Fait : mrr_signed, pipeline_generated, pipeline_weighted ou demos. |
| `metric_key` | `String` | Non | Projection sans changement de dtr_sales_objectives_month.metric_key. Fait : identité de l'indicateur. |
| `metric_version_key` | `String` | Non | Projection sans changement de dtr_sales_objectives_month.metric_version_key. Version de dim_metric utilisée par le run. |
| `metric_label` | `Nullable(String)` | Oui | Projection sans changement de dtr_sales_objectives_month.metric_label. dim_metric.metric_label ; une ligne de dimension au plus. |
| `value_unit` | `String` | Non | Projection sans changement de dtr_sales_objectives_month.value_unit. fct_sales_objectives_month.value_unit, déclaration attendue de mesure (peut marquer pipeline non confirmé) ; ne prouve pas la comparabilité du réalisé. Ce dernier reste NULL sans unité validée. |
| `actual_value` | `Nullable(Decimal(38,4))` | Oui | Projection sans changement de dtr_sales_objectives_month.actual_value. Fait : réalisé de la population compatible, jamais un candidat monétaire promu sans validation. |
| `target_value` | `Nullable(Decimal(38,4))` | Oui | Projection sans changement de dtr_sales_objectives_month.target_value. Fait : cible versionnée de la même équipe et du même mois. |
| `variance_value` | `Nullable(Decimal(38,4))` | Oui | Projection sans changement de dtr_sales_objectives_month.variance_value. actual_value - target_value seulement si les deux valeurs et leur comparabilité sont connues. |
| `attainment_rate` | `Nullable(Float64)` | Oui | Projection sans changement de dtr_sales_objectives_month.attainment_rate. actual_value / target_value si cible > 0 et valeurs comparables ; affichage ×100 dans la BI. |
| `is_population_compatible` | `Nullable(Bool)` | Oui | Projection sans changement de dtr_sales_objectives_month.is_population_compatible. Population4/7 décidée D22 ; compatibilité d’unité/date vérifiée séparément, NULL si preuve d’unité manque. |
| `nb_source_contributions` | `Nullable(UInt64)` | Oui | Projection sans changement de dtr_sales_objectives_month.nb_source_contributions. Nombre de contributions logiques examinées dans le réalisé, s'il est disponible dans le fait. |
| `nb_uncalculable_contributions` | `Nullable(UInt64)` | Oui | Projection sans changement de dtr_sales_objectives_month.nb_uncalculable_contributions. Nombre de contributions dont le calcul reste inconnu ; ne prouve pas à lui seul la complétude de la source. |
| `calculation_status` | `String` | Non | Projection sans changement de dtr_sales_objectives_month.calculation_status. ready/partial/blocked/not_applicable ; statut transmis et combiné aux contrôles de jointure. |
| `status_reason` | `Nullable(String)` | Oui | Projection sans changement de dtr_sales_objectives_month.status_reason. Motif explicite : unconfirmed_amount_unit, missing_team_mapping, missing_demo_completion_proof, incompatible_population, missing_target, zero_target, ou motif du fait. |

**SQL de projection complet :**

```sql
{{ config(materialized='view', schema='dtr_sales') }}

select
    d.model_run_id,
    d.record_key,
    d.record_version_key,
    d.row_hash,
    d.calculated_at,
    d.rule_version,
    d.input_cutoff_at,
    d.tenant_id,
    d.month_date,
    d.source_segment,
    d.team_key,
    d.team_version_key,
    d.team_name,
    d.metric_code,
    d.metric_key,
    d.metric_version_key,
    d.metric_label,
    d.value_unit,
    d.actual_value,
    d.target_value,
    d.variance_value,
    d.attainment_rate,
    d.is_population_compatible,
    d.nb_source_contributions,
    d.nb_uncalculable_contributions,
    d.calculation_status,
    d.status_reason
from {{ ref('dtr_sales_objectives_month') }} as d
inner join {{ ref('int_publication') }} as p
    on d.model_run_id = p.model_run_id
```

**Jointure/publication :** DTR N:1 vers la ligne unique du pointeur, égalité de run ; au bootstrap sans pointeur accepté, zéro ligne. Plus d'une ligne de pointeur est ERROR bloquante. Aucune dépendance inverse DTR→publication. Chaque requête BI conserve model_run_id et vérifie sa cohérence avec dataset_publication_status ; une page ne mélange pas plusieurs runs.

**Contrat BI et filtres :** Période : month_date >= début de mois et < mois suivant la fin sélectionnée. Équipe : égalité sur team_key, ou toutes. L'observation n'est pas une date de flux : les cartes contrôlent la clôture du mois. Cohorte, canal, type commercial et seuil ne sont pas des filtres de ces cartes tant que le périmètre des objectifs ne les permet pas. Le segment de cible peut être consulté via source_segment même si team_key=NULL ; aucune assimilation implicite segment↔businessunit.

**Calculs restants en restitution :** Filtrer un metric_code à la fois. Pour une même clôture et des équipes disjointes/compatibles, somme des réalisés et des cibles, puis écart et taux recalculés. Si une équipe sélectionnée a un réalisé inconnu ou incomplet, résultat officiel global NULL et couverture affichée ; sum() ne doit pas ignorer silencieusement ce NULL. Aucun total entre les quatre indicateurs ; pipeline_weighted ne se somme pas entre mois. Ils utilisent les champs détaillés, pas des ratios/quantiles locaux déjà agrégés. Les dates/arrondis/libellés/couleurs se formatent dans la BI ; les champsNULL restent indisponibles, jamais zéro d'affichage implicite. Avant agrégation, vérifier disponibilité PAR MESURE dans dataset_publication_status, y compris absence de lignes de détail.

**Test du dataset :** compter et comparer clés/payloads à la DTR sur le seul run publié ; égalité exacte attendue, ERROR sinon. Tester bootstrap vide, bascule vers nouveau run, réexécution sans modification, navigation tenant+clé+run et détection de publication différente entre requêtes. Rejouer les scénarios de filtres et d'agrégation de `dtr_sales_objectives_month`, dont Unicité du grain ; quatre domaines metric_code ; mêmes unités/populations pour actual/target ; cible absente ou nulle donne taux NULL ; aucun facteur de duplication après dimensions ; global compatible = recomposition des composantes.

**Rafraîchissement/limites :** la vue reflète le pointeur accepté sans horaire propre ; la fraîcheur dépend des sources, du run et de sa publication. Une règle/preuve manquante dans la DTR n'est pas réparée dans cette vue. Les blocages/limites sont ceux de la DTR et du dataset technique de disponibilité. Une relecture d'ancien run passe par la DTR explicite, sans changement du pointeur.


<a id="dtr_funnel_progress"></a>

### `dtr_funnel_progress`

**Règle finale v0.2 :** D17/D18 : utiliser les définitions activées ; une ligne par opportunité/jalon du chemin. transition_reached_at provient du first_reached_at du suivi stage_transition correctement ancré à première A, pas du premier B global qui peut précéder A. Le filtre O compare ce timestamp pour le numérateur et previous_stage_first_reached_at pour le dénominateur. Le jalon Création est une ancre, label imposé, pas un état0 imputé. Modes actifs opportunités/taux seulement ; jamais forcer décroissance des volumes observés.

**Couche/module :** DTR, Trois dashboards — Synthèse / Tunnel. **Finalité :** Synthèse : choix nouvelles ventes/upsells, cohorte, mesure ; effectifs ayant atteint les étapes, taux adjacents, conversion globale et limites de couverture. Le nombre d'opportunités diffère du stock sociétés In demo. Les largeurs visuelles n'imposent pas une décroissance si les populations ne sont pas démontrées emboîtées.

**Grain métier :** tenant_id × opportunity_key × définition de parcours × anchor_at × target_stage_id ; une contribution de dossier par étape cible. **Identité logique :** `record_key=H(tenant_id, opportunity_key, followup_definition_key, anchor_at, target_stage_id)`. **Grain historique/physique :** `(model_run_id,record_key)` ; version=H(run,key), une seule contribution par unité dans un run. Les clés métier et de dimensions sont conservées ci-dessous.

**Amont exact :** `{{ ref('fct_opportunity_followup') }}`, `{{ ref('dim_followup_definition') }}`, `{{ ref('dim_stage') }}`, `{{ ref('dim_company') }}`, `{{ ref('dim_sale_type') }}`, `{{ ref('dim_channel') }}`, `{{ ref('dim_employee') }}`, `{{ ref('dim_team') }}`. **Destination :** `dtr_sales.dtr_funnel_progress` ; fichier `dbt/models/reporting/dtr/dtr_funnel_progress.sql`, YAML `dbt/models/reporting/dtr/_models.yml`.

| Colonne | Type ClickHouse | Nullable | Origine, formule et contraintes |
|---|---|---|---|
| `model_run_id` | `String` | Non | Identifiant de la recomposition complète et immuable ; hérité des entrées du même run. |
| `record_key` | `String` | Non | SHA256 de la liste ordonnée des éléments du grain indiquée dans la fiche ; sérialisation canonique commune, jamais simple concaténation ambiguë. |
| `record_version_key` | `String` | Non | SHA256 de (model_run_id, record_key). |
| `row_hash` | `String` | Non | SHA256 du payload ordonné de la fiche, hors colonnes techniques communes. |
| `calculated_at` | `DateTime64(3, 'UTC')` | Non | Instant de calcul du run ; aucune substitution à une date métier. |
| `rule_version` | `String` | Non | Version immuable des règles et référentiels utilisés par le run. |
| `input_cutoff_at` | `DateTime64(3, 'UTC')` | Non | Borne des entrées figées ; héritée du manifeste de run. |
| `tenant_id` | `String` | Non | Tenant Boond conservé dans les identités et jointures. |
| `opportunity_key` | `String` | Non | Identité stable tenant + opportunité. |
| `opportunity_id` | `Int64` | Non | Identifiant Boond du dossier, pour investigation. |
| `company_key` | `Nullable(String)` | Oui | Identité stable de société résolue au contexte retenu. |
| `company_version_key` | `Nullable(String)` | Oui | Version de société pertinente au contexte retenu. |
| `company_id` | `Nullable(Int64)` | Oui | Identifiant Boond de la société. |
| `company_name` | `Nullable(String)` | Oui | dim_company.company_name par run+company_version_key, N:0..1. |
| `followup_key` | `String` | Non | Identité de la contribution canonique de suivi. |
| `followup_definition_key` | `String` | Non | Définition versionnée du parcours et de l'étape cible ; ne pas additionner des définitions différentes. |
| `followup_definition_version_key` | `String` | Non | Version de dim_followup_definition utilisée. |
| `created_at` | `Nullable(DateTime64(3, 'UTC'))` | Oui | Création métier Boond, ancrage d'entrée du pipeline. |
| `anchor_at` | `Nullable(DateTime64(3, 'UTC'))` | Oui | Ancrage de définition D17/D18 ; NULL et qualité si date d’entrée non observable, pas règle indécise. |
| `cohort_month` | `Nullable(Date)` | Oui | Mois de création Paris, filtre cohorte du tunnel. |
| `sale_path_code` | `Nullable(String)` | Oui | dim_sale_type.sale_type_code associé au type d'ancrage ; aucune déduction du parcours depuis un code d'étape. |
| `target_stage_id` | `Int64` | Non | Étape cible de la ligne. |
| `target_stage_key` | `Nullable(String)` | Oui | Identité stable de l'étape cible. |
| `target_stage_version_key` | `Nullable(String)` | Oui | Version de la cible. |
| `target_stage_label` | `Nullable(String)` | Oui | Libellé dim_stage de la cible par run+version. |
| `funnel_position` | `Nullable(UInt16)` | Oui | Position explicite dans le parcours validé ; jamais tri du code numérique. |
| `previous_target_stage_id` | `Nullable(Int64)` | Oui | Étape précédente définie du même parcours, NULL pour la première. |
| `first_reached_at` | `Nullable(DateTime64(3, 'UTC'))` | Oui | Première entrée admissible connue dans la cible après ancrage ; NULL n'est pas preuve d'échec. |
| `first_reached_observed_at` | `Nullable(DateTime64(3, 'UTC'))` | Oui | Première preuve d'observation en cible, utilisable comme borne supérieure d'atteinte sans inventer une entrée exacte. |
| `previous_stage_first_reached_at` | `Nullable(DateTime64(3, 'UTC'))` | Oui | Première atteinte admissible de l'étape précédente selon définition. |
| `transition_reached_at` | `Nullable(DateTime64(3, 'UTC'))` | Oui | Alias de first_reached_at du suivi stage_transition sélectionné, après ancrage source ; jointure explicitée, pas colonne supposée du fait. |
| `is_eligible` | `Nullable(Bool)` | Oui | Admissibilité du dossier à la population commune du parcours. |
| `is_definition_enabled` | `Bool` | Non | dim_followup_definition.is_enabled ; false si définition absente/désactivée, avec blocked_definition dans disponibilité. |
| `coverage_start_at` | `Nullable(DateTime64(3, 'UTC'))` | Oui | Borne de couverture historique de la population suivie. |
| `coverage_end_at` | `Nullable(DateTime64(3, 'UTC'))` | Oui | Fin de couverture connue. |
| `is_history_complete` | `Nullable(Bool)` | Oui | Couverture permettant de distinguer non atteinte observée et absence de trace. |
| `reached_target` | `Nullable(Bool)` | Oui | Résultat à l'observation du run ; recalculer par les timestamps pour une autre observation. |
| `denominator_contribution` | `Nullable(UInt8)` | Oui | Contribution du dossier admissible au dénominateur de la définition ; NULL si non calculable. |
| `converted_contribution` | `Nullable(UInt8)` | Oui | Contribution admissible convertie, interprétée avec son ancrage/horizon ; ne pas sommer sans restriction d'observation. |
| `sale_type_id` | `Nullable(Int64)` | Oui | Type commercial du dossier dans le contexte retenu ; ne désigne pas la composante financière New/Upsell. |
| `sale_type_key` | `Nullable(String)` | Oui | Identité stable du type commercial. |
| `sale_type_version_key` | `Nullable(String)` | Oui | Version de dim_sale_type pertinente. |
| `sale_type_label` | `Nullable(String)` | Oui | dim_sale_type.sale_type_label par run+version, N:0..1. |
| `channel_key` | `Nullable(String)` | Oui | Alias explicite de acquisition_channel_key du fait ; canal officiel d'entrée, NULL avant règle validée. |
| `channel_version_key` | `Nullable(String)` | Oui | Version de mapping du canal, indépendante des sources candidates conservées. |
| `channel_label` | `Nullable(String)` | Oui | dim_channel.channel_label par run+version, N:0..1. |
| `channel_candidate_code` | `Nullable(String)` | Oui | Valeur candidate Boond conservée sans la transformer en canal officiel. |
| `is_channel_calculable` | `Bool` | Non | false si origine à création ou mapping de valeur est manquant ; règle D24 définie, filtre disponible sur les lignes résolues. |
| `employee_key` | `Nullable(String)` | Oui | Identité stable du responsable retenu. |
| `employee_version_key` | `Nullable(String)` | Oui | Version descriptive du responsable. |
| `employee_display_name` | `Nullable(String)` | Oui | dim_employee.employee_display_name par run+version, N:0..1. |
| `team_key` | `Nullable(String)` | Oui | Équipe historiquement retenue si mapping et attribution validés. |
| `team_version_key` | `Nullable(String)` | Oui | Version de l'équipe pertinente. |
| `team_name` | `Nullable(String)` | Oui | dim_team.team_name par run+version, N:0..1. |
| `is_team_calculable` | `Bool` | Non | false pour rattachement à entrée/événement inconnu ou ambigu ; sinon true y compris KAM connue, indépendamment de son absence de cible D23. |
| `calculation_status` | `String` | Non | ready/partial/blocked/not_applicable ; ready n'efface pas les réserves distinctes de couverture. |
| `status_reason` | `Nullable(String)` | Oui | Motif explicite, stable et documenté ; plusieurs motifs séparés de façon canonique si nécessaire. |

**Jointures, identités et cardinalités :** Population et milestones des followup funnel_reach, une ligne par grain. LEFT JOIN de la définition et de l'étape cible par run+version N:0..1. Les transitions sont préparées séparément depuis stage_transition et réduites à une contribution admissible par dossier/source/cible/ancrage selon règle avant jointure N:0..1 ; si la sélection d'ancrage est ouverte, laisser NULL/blocked. Si min des visites est nécessaire, GROUP BY run/tenant/opportunity/cible AVANT join, avec bornes/time_basis ; ne jamais joindre toutes visites à toutes lignes du funnel. Dimensions d'entrée N:0..1.

**Étapes du calcul :** Entrée pipeline=création Boond. Même population de dossiers par parcours/cohorte et observation. Pour chaque cible, preuve d'atteinte avant O à partir de first_reached_at ou preuve observée explicitement qualifiée ; absence de trace ne vaut false que si l'histoire pertinente et la définition sont complètes. Sauts/retours restent visibles : ne pas inventer de passage intermédiaire. Pour transition A→B utiliser le suivi défini A puis B, pas le quotient aveugle de deux stocks ou deux effectifs non emboîtés. Les définitions nouvelles ventes et upsells restent séparées. Une définition sans target_stage_id ne peut fournir une ligne du grain : aucune cible 0 factice ; absence de lignes accompagnée du statut de famille blocked_definition dans dataset_publication_status.

**Filtrage, paramètres et agrégation :** Cohorte de création, observation O, parcours/type commercial ; équipe et canal uniquement si calculables selon attribution d'entrée. Le menu du tunnel est local : Opportunités et Taux de passage ont contrat ci-dessus ; Montants/Durées restent indisponibles avec missing_funnel_measure_definition tant que date du montant/population/statistique spécifique ne sont pas définies. Les paramètres ne filtrent pas cartes objectifs ni portefeuille MRR. Effectif atteint=nombre de opportunity_key admissibles avec preuve d'atteinte<=O, au même target et à la même définition. Afficher distinctement les dossiers à couverture insuffisante. Transition=nombre dossiers de la population A ayant B après A et avant O / nombre dossiers éligibles de cette même population A ; NULL si définition/observabilité insuffisantes ou dénominateur0. Conversion globale=signés admissibles parmi la population d'entrée retenue / population d'entrée compatible ; état 14 sans nouvelle victoire. Ne pas sommer les lignes d'étapes pour produire un nombre de dossiers.

**Matérialisation/histoire :** appliquer le contrat DTR commun ci-dessus : résultats complets du run, incremental append, engine MergeTree, ORDER BY(model_run_id,record_key), unique_key record_version_key, on_schema_change fail, full_refresh false et pas inserts_only. Les tables DTR conservent les anciens runs ; aucun filtre max de date métier ou limite à hier. Au premier chargement/cible vide, calculer l'ensemble ; en reprise, conserver seulement les clés du candidat absentes de la cible, sans modifier un payload existant.

**Contrat de chargement dbt :** une requête SELECT, CTE candidates explicite issue des transformations décrites. Chaque colonne du dictionnaire est produite exactement une fois. Terminer par la projection explicite de candidates ; sous `{% if is_incremental() %}`, LEFT ANTI JOIN de `{{ this }}` sur model_run_id et record_key. Tester absence de deux payloads différents pour une même clé/run AVANT chargement. Le unique_key de configuration assure le chemin de contrôle de schéma de l'adaptateur, pas la déduplication. Les entrées du run et le cutoff sont figés avant toute écriture future ; reprise du même run à empreinte inchangée.

**Construction/rafraîchissement :** après tous amonts du même run ; branches indépendantes parallélisables selon DAG. Exécution manuelle D29 ; fraîcheur de capture/publication déclarée, calcul puis tests/digest et publication contrôlée. Les requêtes de contrôle avant publication utilisent test_model_run_id. Aucun service/modèle n'est créé par la présente fiche.

**Tests/acceptation :** Une contribution par dossier/cible ; aucun produit des visites multiples ; étape sautée non inventée ; retour sans doublon de dossier atteint ; B avant A ne valide pas A→B sauf nouvelle atteinte admissible après A ; absence de trace inconnue ; parcours désactivé=>NULL+motif ; 1→14 une seule signature ; taux recalculés après filtre. Contrôles communs ERROR de grain, hash, cardinalité et run ; WARN/indisponibilité pour manque descriptif ou preuve comme décrit dans le contrat. Tests métier ci-dessus planifiés, pas exécutés sur une implémentation inexistante.


<a id="dataset_funnel_progress"></a>

### `dataset_funnel_progress`

**Couche/module :** dataset de restitution, Trois dashboards — Synthèse / Tunnel. **Finalité/consommateurs :** Synthèse : choix nouvelles ventes/upsells, cohorte, mesure ; effectifs ayant atteint les étapes, taux adjacents, conversion globale et limites de couverture. Le nombre d'opportunités diffère du stock sociétés In demo. Les largeurs visuelles n'imposent pas une décroissance si les populations ne sont pas démontrées emboîtées.

**Grain métier et version :** exactement celui de `dtr_funnel_progress` : tenant_id × opportunity_key × définition de parcours × anchor_at × target_stage_id ; une contribution de dossier par étape cible. Une seule publication est visible ; identité et version sont conservées sans recalcul. Aucun total ni ligne artificielle n'est ajouté.

**Amont exact :** `{{ ref('dtr_funnel_progress') }}` et `{{ ref('int_publication') }}`. **Destination :** `dtr_sales.dataset_funnel_progress` ; fichier `dbt/models/reporting/datasets/dataset_funnel_progress.sql`, YAML `dbt/models/reporting/datasets/_models.yml`.

| Colonne | Type ClickHouse | Nullable | Origine, formule et contraintes |
|---|---|---|---|
| `model_run_id` | `String` | Non | Projection sans changement de dtr_funnel_progress.model_run_id. Identifiant de la recomposition complète et immuable ; hérité des entrées du même run. |
| `record_key` | `String` | Non | Projection sans changement de dtr_funnel_progress.record_key. SHA256 de la liste ordonnée des éléments du grain indiquée dans la fiche ; sérialisation canonique commune, jamais simple concaténation ambiguë. |
| `record_version_key` | `String` | Non | Projection sans changement de dtr_funnel_progress.record_version_key. SHA256 de (model_run_id, record_key). |
| `row_hash` | `String` | Non | Projection sans changement de dtr_funnel_progress.row_hash. SHA256 du payload ordonné de la fiche, hors colonnes techniques communes. |
| `calculated_at` | `DateTime64(3, 'UTC')` | Non | Projection sans changement de dtr_funnel_progress.calculated_at. Instant de calcul du run ; aucune substitution à une date métier. |
| `rule_version` | `String` | Non | Projection sans changement de dtr_funnel_progress.rule_version. Version immuable des règles et référentiels utilisés par le run. |
| `input_cutoff_at` | `DateTime64(3, 'UTC')` | Non | Projection sans changement de dtr_funnel_progress.input_cutoff_at. Borne des entrées figées ; héritée du manifeste de run. |
| `tenant_id` | `String` | Non | Projection sans changement de dtr_funnel_progress.tenant_id. Tenant Boond conservé dans les identités et jointures. |
| `opportunity_key` | `String` | Non | Projection sans changement de dtr_funnel_progress.opportunity_key. Identité stable tenant + opportunité. |
| `opportunity_id` | `Int64` | Non | Projection sans changement de dtr_funnel_progress.opportunity_id. Identifiant Boond du dossier, pour investigation. |
| `company_key` | `Nullable(String)` | Oui | Projection sans changement de dtr_funnel_progress.company_key. Identité stable de société résolue au contexte retenu. |
| `company_version_key` | `Nullable(String)` | Oui | Projection sans changement de dtr_funnel_progress.company_version_key. Version de société pertinente au contexte retenu. |
| `company_id` | `Nullable(Int64)` | Oui | Projection sans changement de dtr_funnel_progress.company_id. Identifiant Boond de la société. |
| `company_name` | `Nullable(String)` | Oui | Projection sans changement de dtr_funnel_progress.company_name. dim_company.company_name par run+company_version_key, N:0..1. |
| `followup_key` | `String` | Non | Projection sans changement de dtr_funnel_progress.followup_key. Identité de la contribution canonique de suivi. |
| `followup_definition_key` | `String` | Non | Projection sans changement de dtr_funnel_progress.followup_definition_key. Définition versionnée du parcours et de l'étape cible ; ne pas additionner des définitions différentes. |
| `followup_definition_version_key` | `String` | Non | Projection sans changement de dtr_funnel_progress.followup_definition_version_key. Version de dim_followup_definition utilisée. |
| `created_at` | `Nullable(DateTime64(3, 'UTC'))` | Oui | Projection sans changement de dtr_funnel_progress.created_at. Création métier Boond, ancrage d'entrée du pipeline. |
| `anchor_at` | `Nullable(DateTime64(3, 'UTC'))` | Oui | Projection sans changement de dtr_funnel_progress.anchor_at. Ancrage de définition D17/D18 ; NULL et qualité si date d’entrée non observable, pas règle indécise. |
| `cohort_month` | `Nullable(Date)` | Oui | Projection sans changement de dtr_funnel_progress.cohort_month. Mois de création Paris, filtre cohorte du tunnel. |
| `sale_path_code` | `Nullable(String)` | Oui | Projection sans changement de dtr_funnel_progress.sale_path_code. dim_sale_type.sale_type_code associé au type d'ancrage ; aucune déduction du parcours depuis un code d'étape. |
| `target_stage_id` | `Int64` | Non | Projection sans changement de dtr_funnel_progress.target_stage_id. Étape cible de la ligne. |
| `target_stage_key` | `Nullable(String)` | Oui | Projection sans changement de dtr_funnel_progress.target_stage_key. Identité stable de l'étape cible. |
| `target_stage_version_key` | `Nullable(String)` | Oui | Projection sans changement de dtr_funnel_progress.target_stage_version_key. Version de la cible. |
| `target_stage_label` | `Nullable(String)` | Oui | Projection sans changement de dtr_funnel_progress.target_stage_label. Libellé dim_stage de la cible par run+version. |
| `funnel_position` | `Nullable(UInt16)` | Oui | Projection sans changement de dtr_funnel_progress.funnel_position. Position explicite dans le parcours validé ; jamais tri du code numérique. |
| `previous_target_stage_id` | `Nullable(Int64)` | Oui | Projection sans changement de dtr_funnel_progress.previous_target_stage_id. Étape précédente définie du même parcours, NULL pour la première. |
| `first_reached_at` | `Nullable(DateTime64(3, 'UTC'))` | Oui | Projection sans changement de dtr_funnel_progress.first_reached_at. Première entrée admissible connue dans la cible après ancrage ; NULL n'est pas preuve d'échec. |
| `first_reached_observed_at` | `Nullable(DateTime64(3, 'UTC'))` | Oui | Projection sans changement de dtr_funnel_progress.first_reached_observed_at. Première preuve d'observation en cible, utilisable comme borne supérieure d'atteinte sans inventer une entrée exacte. |
| `previous_stage_first_reached_at` | `Nullable(DateTime64(3, 'UTC'))` | Oui | Projection sans changement de dtr_funnel_progress.previous_stage_first_reached_at. Première atteinte admissible de l'étape précédente selon définition. |
| `transition_reached_at` | `Nullable(DateTime64(3, 'UTC'))` | Oui | Projection sans changement de dtr_funnel_progress.transition_reached_at. Alias de first_reached_at du suivi stage_transition sélectionné, après ancrage source ; jointure explicitée, pas colonne supposée du fait. |
| `is_eligible` | `Nullable(Bool)` | Oui | Projection sans changement de dtr_funnel_progress.is_eligible. Admissibilité du dossier à la population commune du parcours. |
| `is_definition_enabled` | `Bool` | Non | Projection sans changement de dtr_funnel_progress.is_definition_enabled. dim_followup_definition.is_enabled ; false si définition absente/désactivée, avec blocked_definition dans disponibilité. |
| `coverage_start_at` | `Nullable(DateTime64(3, 'UTC'))` | Oui | Projection sans changement de dtr_funnel_progress.coverage_start_at. Borne de couverture historique de la population suivie. |
| `coverage_end_at` | `Nullable(DateTime64(3, 'UTC'))` | Oui | Projection sans changement de dtr_funnel_progress.coverage_end_at. Fin de couverture connue. |
| `is_history_complete` | `Nullable(Bool)` | Oui | Projection sans changement de dtr_funnel_progress.is_history_complete. Couverture permettant de distinguer non atteinte observée et absence de trace. |
| `reached_target` | `Nullable(Bool)` | Oui | Projection sans changement de dtr_funnel_progress.reached_target. Résultat à l'observation du run ; recalculer par les timestamps pour une autre observation. |
| `denominator_contribution` | `Nullable(UInt8)` | Oui | Projection sans changement de dtr_funnel_progress.denominator_contribution. Contribution du dossier admissible au dénominateur de la définition ; NULL si non calculable. |
| `converted_contribution` | `Nullable(UInt8)` | Oui | Projection sans changement de dtr_funnel_progress.converted_contribution. Contribution admissible convertie, interprétée avec son ancrage/horizon ; ne pas sommer sans restriction d'observation. |
| `sale_type_id` | `Nullable(Int64)` | Oui | Projection sans changement de dtr_funnel_progress.sale_type_id. Type commercial du dossier dans le contexte retenu ; ne désigne pas la composante financière New/Upsell. |
| `sale_type_key` | `Nullable(String)` | Oui | Projection sans changement de dtr_funnel_progress.sale_type_key. Identité stable du type commercial. |
| `sale_type_version_key` | `Nullable(String)` | Oui | Projection sans changement de dtr_funnel_progress.sale_type_version_key. Version de dim_sale_type pertinente. |
| `sale_type_label` | `Nullable(String)` | Oui | Projection sans changement de dtr_funnel_progress.sale_type_label. dim_sale_type.sale_type_label par run+version, N:0..1. |
| `channel_key` | `Nullable(String)` | Oui | Projection sans changement de dtr_funnel_progress.channel_key. Alias explicite de acquisition_channel_key du fait ; canal officiel d'entrée, NULL avant règle validée. |
| `channel_version_key` | `Nullable(String)` | Oui | Projection sans changement de dtr_funnel_progress.channel_version_key. Version de mapping du canal, indépendante des sources candidates conservées. |
| `channel_label` | `Nullable(String)` | Oui | Projection sans changement de dtr_funnel_progress.channel_label. dim_channel.channel_label par run+version, N:0..1. |
| `channel_candidate_code` | `Nullable(String)` | Oui | Projection sans changement de dtr_funnel_progress.channel_candidate_code. Valeur candidate Boond conservée sans la transformer en canal officiel. |
| `is_channel_calculable` | `Bool` | Non | Projection sans changement de dtr_funnel_progress.is_channel_calculable. false si origine à création ou mapping de valeur est manquant ; règle D24 définie, filtre disponible sur les lignes résolues. |
| `employee_key` | `Nullable(String)` | Oui | Projection sans changement de dtr_funnel_progress.employee_key. Identité stable du responsable retenu. |
| `employee_version_key` | `Nullable(String)` | Oui | Projection sans changement de dtr_funnel_progress.employee_version_key. Version descriptive du responsable. |
| `employee_display_name` | `Nullable(String)` | Oui | Projection sans changement de dtr_funnel_progress.employee_display_name. dim_employee.employee_display_name par run+version, N:0..1. |
| `team_key` | `Nullable(String)` | Oui | Projection sans changement de dtr_funnel_progress.team_key. Équipe historiquement retenue si mapping et attribution validés. |
| `team_version_key` | `Nullable(String)` | Oui | Projection sans changement de dtr_funnel_progress.team_version_key. Version de l'équipe pertinente. |
| `team_name` | `Nullable(String)` | Oui | Projection sans changement de dtr_funnel_progress.team_name. dim_team.team_name par run+version, N:0..1. |
| `is_team_calculable` | `Bool` | Non | Projection sans changement de dtr_funnel_progress.is_team_calculable. false pour rattachement à entrée/événement inconnu ou ambigu ; sinon true y compris KAM connue, indépendamment de son absence de cible D23. |
| `calculation_status` | `String` | Non | Projection sans changement de dtr_funnel_progress.calculation_status. ready/partial/blocked/not_applicable ; ready n'efface pas les réserves distinctes de couverture. |
| `status_reason` | `Nullable(String)` | Oui | Projection sans changement de dtr_funnel_progress.status_reason. Motif explicite, stable et documenté ; plusieurs motifs séparés de façon canonique si nécessaire. |

**SQL de projection complet :**

```sql
{{ config(materialized='view', schema='dtr_sales') }}

select
    d.model_run_id,
    d.record_key,
    d.record_version_key,
    d.row_hash,
    d.calculated_at,
    d.rule_version,
    d.input_cutoff_at,
    d.tenant_id,
    d.opportunity_key,
    d.opportunity_id,
    d.company_key,
    d.company_version_key,
    d.company_id,
    d.company_name,
    d.followup_key,
    d.followup_definition_key,
    d.followup_definition_version_key,
    d.created_at,
    d.anchor_at,
    d.cohort_month,
    d.sale_path_code,
    d.target_stage_id,
    d.target_stage_key,
    d.target_stage_version_key,
    d.target_stage_label,
    d.funnel_position,
    d.previous_target_stage_id,
    d.first_reached_at,
    d.first_reached_observed_at,
    d.previous_stage_first_reached_at,
    d.transition_reached_at,
    d.is_eligible,
    d.is_definition_enabled,
    d.coverage_start_at,
    d.coverage_end_at,
    d.is_history_complete,
    d.reached_target,
    d.denominator_contribution,
    d.converted_contribution,
    d.sale_type_id,
    d.sale_type_key,
    d.sale_type_version_key,
    d.sale_type_label,
    d.channel_key,
    d.channel_version_key,
    d.channel_label,
    d.channel_candidate_code,
    d.is_channel_calculable,
    d.employee_key,
    d.employee_version_key,
    d.employee_display_name,
    d.team_key,
    d.team_version_key,
    d.team_name,
    d.is_team_calculable,
    d.calculation_status,
    d.status_reason
from {{ ref('dtr_funnel_progress') }} as d
inner join {{ ref('int_publication') }} as p
    on d.model_run_id = p.model_run_id
```

**Jointure/publication :** DTR N:1 vers la ligne unique du pointeur, égalité de run ; au bootstrap sans pointeur accepté, zéro ligne. Plus d'une ligne de pointeur est ERROR bloquante. Aucune dépendance inverse DTR→publication. Chaque requête BI conserve model_run_id et vérifie sa cohérence avec dataset_publication_status ; une page ne mélange pas plusieurs runs.

**Contrat BI et filtres :** Cohorte de création, observation O, parcours/type commercial ; équipe et canal uniquement si calculables selon attribution d'entrée. Le menu du tunnel est local : Opportunités et Taux de passage ont contrat ci-dessus ; Montants/Durées restent indisponibles avec missing_funnel_measure_definition tant que date du montant/population/statistique spécifique ne sont pas définies. Les paramètres ne filtrent pas cartes objectifs ni portefeuille MRR.

**Calculs restants en restitution :** Effectif atteint=nombre de opportunity_key admissibles avec preuve d'atteinte<=O, au même target et à la même définition. Afficher distinctement les dossiers à couverture insuffisante. Transition=nombre dossiers de la population A ayant B après A et avant O / nombre dossiers éligibles de cette même population A ; NULL si définition/observabilité insuffisantes ou dénominateur0. Conversion globale=signés admissibles parmi la population d'entrée retenue / population d'entrée compatible ; état 14 sans nouvelle victoire. Ne pas sommer les lignes d'étapes pour produire un nombre de dossiers. Ils utilisent les champs détaillés, pas des ratios/quantiles locaux déjà agrégés. Les dates/arrondis/libellés/couleurs se formatent dans la BI ; les champsNULL restent indisponibles, jamais zéro d'affichage implicite. Avant agrégation, vérifier disponibilité PAR MESURE dans dataset_publication_status, y compris absence de lignes de détail.

**Test du dataset :** compter et comparer clés/payloads à la DTR sur le seul run publié ; égalité exacte attendue, ERROR sinon. Tester bootstrap vide, bascule vers nouveau run, réexécution sans modification, navigation tenant+clé+run et détection de publication différente entre requêtes. Rejouer les scénarios de filtres et d'agrégation de `dtr_funnel_progress`, dont Une contribution par dossier/cible ; aucun produit des visites multiples ; étape sautée non inventée ; retour sans doublon de dossier atteint ; B avant A ne valide pas A→B sauf nouvelle atteinte admissible après A ; absence de trace inconnue ; parcours désactivé=>NULL+motif ; 1→14 une seule signature ; taux recalculés après filtre.

**Rafraîchissement/limites :** la vue reflète le pointeur accepté sans horaire propre ; la fraîcheur dépend des sources, du run et de sa publication. Une règle/preuve manquante dans la DTR n'est pas réparée dans cette vue. Les blocages/limites sont ceux de la DTR et du dataset technique de disponibilité. Une relecture d'ancien run passe par la DTR explicite, sans changement du pointeur.


<a id="dtr_company_mrr_month"></a>

### `dtr_company_mrr_month`

**Règle finale v0.2 :** EUR et couverture de case D16/D20 ; calcul des montants connus actif/New/Upsell/churn conforme aux2clôtures. is_first_acquisition=true si first_proven,false si return_proven,NULL si unknown D27. Le compteur d’entrants entre clôtures est distinct de nouveaux clients et du montant New MRR.

**Couche/module :** DTR, Trois dashboards — Synthèse / MRR. **Finalité :** Synthèse : MRR actif, churn MRR, cascade début → New → Upsell → départs → baisses → fin, et détail clients partis/en baisse. Le total New MRR peut être affiché comme carte ; ne pas l'ajouter aux deux barres New/Upsell.

**Grain métier :** tenant_id × company_key × closing_date ; une ligne par société aux deux clôtures comparées. **Identité logique :** `record_key=H(tenant_id, company_key, closing_date)`. **Grain historique/physique :** `(model_run_id,record_key)` ; version=H(run,key), une seule contribution par unité dans un run. Les clés métier et de dimensions sont conservées ci-dessous.

**Amont exact :** `{{ ref('fct_subscription_month_end') }}`, `{{ ref('fct_mrr_movement') }}`, `{{ ref('dim_company') }}`. **Destination :** `dtr_sales.dtr_company_mrr_month` ; fichier `dbt/models/reporting/dtr/dtr_company_mrr_month.sql`, YAML `dbt/models/reporting/dtr/_models.yml`.

| Colonne | Type ClickHouse | Nullable | Origine, formule et contraintes |
|---|---|---|---|
| `model_run_id` | `String` | Non | Identifiant de la recomposition complète et immuable ; hérité des entrées du même run. |
| `record_key` | `String` | Non | SHA256 de la liste ordonnée des éléments du grain indiquée dans la fiche ; sérialisation canonique commune, jamais simple concaténation ambiguë. |
| `record_version_key` | `String` | Non | SHA256 de (model_run_id, record_key). |
| `row_hash` | `String` | Non | SHA256 du payload ordonné de la fiche, hors colonnes techniques communes. |
| `calculated_at` | `DateTime64(3, 'UTC')` | Non | Instant de calcul du run ; aucune substitution à une date métier. |
| `rule_version` | `String` | Non | Version immuable des règles et référentiels utilisés par le run. |
| `input_cutoff_at` | `DateTime64(3, 'UTC')` | Non | Borne des entrées figées ; héritée du manifeste de run. |
| `tenant_id` | `String` | Non | Tenant des abonnements et de la société. |
| `company_key` | `String` | Non | Identité stable de société ; aucune clé société inventée pour une ligne non rattachable. |
| `company_id` | `Nullable(Int64)` | Oui | Identifiant Boond lorsque résolu. |
| `company_version_key` | `Nullable(String)` | Oui | Version descriptive de la société à la clôture. |
| `company_name` | `Nullable(String)` | Oui | dim_company.company_name, N:0..1 par run et version. |
| `closing_date` | `Date` | Non | Alias de month_end_date, fct_subscription_month_end/fct_mrr_movement après préagrégation. |
| `previous_closing_date` | `Date` | Non | Alias de fct_mrr_movement.previous_month_end_date ; sinon calendrier Paris du mois précédent. |
| `is_active_begin` | `Nullable(Bool)` | Oui | Au moins une ligne active au début ; NULL si la clôture précédente n'est pas suffisamment observable. |
| `is_active_end` | `Nullable(Bool)` | Oui | Au moins une ligne active à la clôture courante, règle état 1 + service en cours avec date de fin inclusive. |
| `nb_active_lines_begin` | `Nullable(UInt64)` | Oui | Somme des indicateurs d'activité de lignes de la clôture précédente si couverture connue. |
| `nb_active_lines_end` | `Nullable(UInt64)` | Oui | Somme des indicateurs d'activité de lignes de la clôture courante si couverture connue. |
| `sum_mrr_begin` | `Nullable(Decimal(38,4))` | Oui | Somme des sum_active_mrr des lignes de la clôture précédente, après sélection du run et de l'unique version pertinente. |
| `sum_mrr_end` | `Nullable(Decimal(38,4))` | Oui | Somme des sum_active_mrr des lignes de la clôture courante ; aucun prorata. |
| `sum_new_mrr_new` | `Nullable(Decimal(38,4))` | Oui | Somme des contributions du fait de mouvements où new_mrr_component=New, retours compris. |
| `sum_new_mrr_upsell` | `Nullable(Decimal(38,4))` | Oui | Somme des contributions du fait où new_mrr_component=Upsell ; net des sociétés restées actives. |
| `sum_new_mrr` | `Nullable(Decimal(38,4))` | Oui | sum_new_mrr_new + sum_new_mrr_upsell si les deux composantes sont calculables. |
| `sum_departure_mrr` | `Nullable(Decimal(38,4))` | Oui | Perte positive des sociétés sortantes, issue du fait de mouvements. |
| `sum_contraction_mrr` | `Nullable(Decimal(38,4))` | Oui | Perte positive des sociétés actives aux deux clôtures et en baisse nette. |
| `sum_churn_mrr` | `Nullable(Decimal(38,4))` | Oui | sum_departure_mrr + sum_contraction_mrr si les composantes sont calculables. |
| `sum_other_mrr_delta` | `Nullable(Decimal(38,4))` | Oui | Decimal0 uniquement quand les deux clôtures sont comparables et toutes variations classées new/upsell/departure/contraction/stable ; NULL si movement_kind=unknown ou correction non classée. Aucun résidu transformé en correction/churn. |
| `sum_reconciliation_gap` | `Nullable(Decimal(38,4))` | Oui | sum_mrr_end - sum_mrr_begin - sum_new_mrr + sum_churn_mrr - sum_other_mrr_delta, si tous les termes sont calculables. |
| `is_portfolio_entrant` | `Nullable(Bool)` | Oui | Non actif début et actif fin ; retours compris. Activité indépendante d'un montant nul. |
| `is_departure` | `Nullable(Bool)` | Oui | Actif début et non actif fin. |
| `is_contraction` | `Nullable(Bool)` | Oui | Actif aux deux clôtures et MRR total fin < début. |
| `is_first_acquisition` | `Nullable(Bool)` | Oui | true si first_acquisition_status=first_proven, false si return_proven, NULL si unknown selon D27 ; un entrant seul ne prouve jamais première acquisition. |
| `is_begin_observable` | `Bool` | Non | Clôture précédente suffisamment couverte selon le contrôle source déclaré. |
| `is_end_observable` | `Bool` | Non | Clôture courante suffisamment couverte selon le contrôle source déclaré. |
| `calculation_status` | `String` | Non | ready/partial/blocked/not_applicable ; ne pas publier un portefeuille incomplet comme exhaustif. |
| `status_reason` | `Nullable(String)` | Oui | incomplete_history, unknown_activity, unresolved_company, unknown_amount, unclassified_correction, ou motif upstream. |

**Jointures, identités et cardinalités :** 1) Agréger séparément fct_subscription_month_end par run/tenant/company/clôture. 2) Mettre les clôtures N-1 et N au même grain par FULL OUTER JOIN sur run/tenant/company et mois décalé. 3) Pivoter fct_mrr_movement en UNE ligne run/tenant/company/mois avant jointure 1:0..1 aux clôtures. 4) LEFT JOIN dim_company sur run+company_version_key N:0..1. Aucun fait détaillé joint à un autre fait détaillé ; les lignes sans société résolue restent en anomalie de couverture de la publication et ne disparaissent pas du contrôle global.

**Étapes du calcul :** Conserver les montants et l'activité des lignes dans les faits ; cette DTR ne réinterprète pas la règle métier. Une absence de ligne dans un côté du FULL OUTER JOIN vaut zéro/inactif uniquement si la couverture de cette clôture le prouve ; sinon NULL et is_*_observable=false. Les gratuités actives peuvent avoir MRR 0. Aucun départ-retour intra-mois détaillé ajouté au reporting. Pas de ligne 'total' en plus des sociétés ni de total New en plus de ses deux composantes dans une somme.

**Filtrage, paramètres et agrégation :** Un seul mois de clôture pour les cartes et la cascade. Une plage de mois sert à une série chronologique, jamais à une somme des stocks. Le filtre financier New/Upsell porte seulement sur le détail des composantes de croissance ; il ne filtre pas les sociétés, les clôtures ou les pertes de la cascade complète. Aucun filtre équipe, canal ou type commercial. À une clôture, sommer les montants calculables uniquement lorsque le contrôle de complétude de tout le périmètre est satisfait ; sinon total officiel NULL et détail connu/qualité séparés. Compter les company_key pour entrants/départs/baisses admissibles ; une ligne société/mois empêche les doublons. Plusieurs mois : stocks par mois, flux mensuels sommables sous bornes/couverture compatibles, clients distincts à recalculer selon la question.

**Matérialisation/histoire :** appliquer le contrat DTR commun ci-dessus : résultats complets du run, incremental append, engine MergeTree, ORDER BY(model_run_id,record_key), unique_key record_version_key, on_schema_change fail, full_refresh false et pas inserts_only. Les tables DTR conservent les anciens runs ; aucun filtre max de date métier ou limite à hier. Au premier chargement/cible vide, calculer l'ensemble ; en reprise, conserver seulement les clés du candidat absentes de la cible, sans modifier un payload existant.

**Contrat de chargement dbt :** une requête SELECT, CTE candidates explicite issue des transformations décrites. Chaque colonne du dictionnaire est produite exactement une fois. Terminer par la projection explicite de candidates ; sous `{% if is_incremental() %}`, LEFT ANTI JOIN de `{{ this }}` sur model_run_id et record_key. Tester absence de deux payloads différents pour une même clé/run AVANT chargement. Le unique_key de configuration assure le chemin de contrôle de schéma de l'adaptateur, pas la déduplication. Les entrées du run et le cutoff sont figés avant toute écriture future ; reprise du même run à empreinte inchangée.

**Construction/rafraîchissement :** après tous amonts du même run ; branches indépendantes parallélisables selon DAG. Exécution manuelle D29 ; fraîcheur de capture/publication déclarée, calcul puis tests/digest et publication contrôlée. Les requêtes de contrôle avant publication utilisent test_model_run_id. Aucun service/modèle n'est créé par la présente fiche.

**Tests/acceptation :** Rapprochement 1:1 après préagrégations ; société avec plusieurs lignes ne multiplie aucun montant ; compensation intra-société uniquement ; gratuité active ; reprise 0→0 d'activité ; NULL de clôture non transformé en zéro ; réconciliation calculable à 0 avec tolérance Decimal définie ; partitions départ et contraction disjointes. Contrôles communs ERROR de grain, hash, cardinalité et run ; WARN/indisponibilité pour manque descriptif ou preuve comme décrit dans le contrat. Tests métier ci-dessus planifiés, pas exécutés sur une implémentation inexistante.


<a id="dataset_company_mrr_month"></a>

### `dataset_company_mrr_month`

**Couche/module :** dataset de restitution, Trois dashboards — Synthèse / MRR. **Finalité/consommateurs :** Synthèse : MRR actif, churn MRR, cascade début → New → Upsell → départs → baisses → fin, et détail clients partis/en baisse. Le total New MRR peut être affiché comme carte ; ne pas l'ajouter aux deux barres New/Upsell.

**Grain métier et version :** exactement celui de `dtr_company_mrr_month` : tenant_id × company_key × closing_date ; une ligne par société aux deux clôtures comparées. Une seule publication est visible ; identité et version sont conservées sans recalcul. Aucun total ni ligne artificielle n'est ajouté.

**Amont exact :** `{{ ref('dtr_company_mrr_month') }}` et `{{ ref('int_publication') }}`. **Destination :** `dtr_sales.dataset_company_mrr_month` ; fichier `dbt/models/reporting/datasets/dataset_company_mrr_month.sql`, YAML `dbt/models/reporting/datasets/_models.yml`.

| Colonne | Type ClickHouse | Nullable | Origine, formule et contraintes |
|---|---|---|---|
| `model_run_id` | `String` | Non | Projection sans changement de dtr_company_mrr_month.model_run_id. Identifiant de la recomposition complète et immuable ; hérité des entrées du même run. |
| `record_key` | `String` | Non | Projection sans changement de dtr_company_mrr_month.record_key. SHA256 de la liste ordonnée des éléments du grain indiquée dans la fiche ; sérialisation canonique commune, jamais simple concaténation ambiguë. |
| `record_version_key` | `String` | Non | Projection sans changement de dtr_company_mrr_month.record_version_key. SHA256 de (model_run_id, record_key). |
| `row_hash` | `String` | Non | Projection sans changement de dtr_company_mrr_month.row_hash. SHA256 du payload ordonné de la fiche, hors colonnes techniques communes. |
| `calculated_at` | `DateTime64(3, 'UTC')` | Non | Projection sans changement de dtr_company_mrr_month.calculated_at. Instant de calcul du run ; aucune substitution à une date métier. |
| `rule_version` | `String` | Non | Projection sans changement de dtr_company_mrr_month.rule_version. Version immuable des règles et référentiels utilisés par le run. |
| `input_cutoff_at` | `DateTime64(3, 'UTC')` | Non | Projection sans changement de dtr_company_mrr_month.input_cutoff_at. Borne des entrées figées ; héritée du manifeste de run. |
| `tenant_id` | `String` | Non | Projection sans changement de dtr_company_mrr_month.tenant_id. Tenant des abonnements et de la société. |
| `company_key` | `String` | Non | Projection sans changement de dtr_company_mrr_month.company_key. Identité stable de société ; aucune clé société inventée pour une ligne non rattachable. |
| `company_id` | `Nullable(Int64)` | Oui | Projection sans changement de dtr_company_mrr_month.company_id. Identifiant Boond lorsque résolu. |
| `company_version_key` | `Nullable(String)` | Oui | Projection sans changement de dtr_company_mrr_month.company_version_key. Version descriptive de la société à la clôture. |
| `company_name` | `Nullable(String)` | Oui | Projection sans changement de dtr_company_mrr_month.company_name. dim_company.company_name, N:0..1 par run et version. |
| `closing_date` | `Date` | Non | Projection sans changement de dtr_company_mrr_month.closing_date. Alias de month_end_date, fct_subscription_month_end/fct_mrr_movement après préagrégation. |
| `previous_closing_date` | `Date` | Non | Projection sans changement de dtr_company_mrr_month.previous_closing_date. Alias de fct_mrr_movement.previous_month_end_date ; sinon calendrier Paris du mois précédent. |
| `is_active_begin` | `Nullable(Bool)` | Oui | Projection sans changement de dtr_company_mrr_month.is_active_begin. Au moins une ligne active au début ; NULL si la clôture précédente n'est pas suffisamment observable. |
| `is_active_end` | `Nullable(Bool)` | Oui | Projection sans changement de dtr_company_mrr_month.is_active_end. Au moins une ligne active à la clôture courante, règle état 1 + service en cours avec date de fin inclusive. |
| `nb_active_lines_begin` | `Nullable(UInt64)` | Oui | Projection sans changement de dtr_company_mrr_month.nb_active_lines_begin. Somme des indicateurs d'activité de lignes de la clôture précédente si couverture connue. |
| `nb_active_lines_end` | `Nullable(UInt64)` | Oui | Projection sans changement de dtr_company_mrr_month.nb_active_lines_end. Somme des indicateurs d'activité de lignes de la clôture courante si couverture connue. |
| `sum_mrr_begin` | `Nullable(Decimal(38,4))` | Oui | Projection sans changement de dtr_company_mrr_month.sum_mrr_begin. Somme des sum_active_mrr des lignes de la clôture précédente, après sélection du run et de l'unique version pertinente. |
| `sum_mrr_end` | `Nullable(Decimal(38,4))` | Oui | Projection sans changement de dtr_company_mrr_month.sum_mrr_end. Somme des sum_active_mrr des lignes de la clôture courante ; aucun prorata. |
| `sum_new_mrr_new` | `Nullable(Decimal(38,4))` | Oui | Projection sans changement de dtr_company_mrr_month.sum_new_mrr_new. Somme des contributions du fait de mouvements où new_mrr_component=New, retours compris. |
| `sum_new_mrr_upsell` | `Nullable(Decimal(38,4))` | Oui | Projection sans changement de dtr_company_mrr_month.sum_new_mrr_upsell. Somme des contributions du fait où new_mrr_component=Upsell ; net des sociétés restées actives. |
| `sum_new_mrr` | `Nullable(Decimal(38,4))` | Oui | Projection sans changement de dtr_company_mrr_month.sum_new_mrr. sum_new_mrr_new + sum_new_mrr_upsell si les deux composantes sont calculables. |
| `sum_departure_mrr` | `Nullable(Decimal(38,4))` | Oui | Projection sans changement de dtr_company_mrr_month.sum_departure_mrr. Perte positive des sociétés sortantes, issue du fait de mouvements. |
| `sum_contraction_mrr` | `Nullable(Decimal(38,4))` | Oui | Projection sans changement de dtr_company_mrr_month.sum_contraction_mrr. Perte positive des sociétés actives aux deux clôtures et en baisse nette. |
| `sum_churn_mrr` | `Nullable(Decimal(38,4))` | Oui | Projection sans changement de dtr_company_mrr_month.sum_churn_mrr. sum_departure_mrr + sum_contraction_mrr si les composantes sont calculables. |
| `sum_other_mrr_delta` | `Nullable(Decimal(38,4))` | Oui | Projection sans changement de dtr_company_mrr_month.sum_other_mrr_delta. Decimal0 uniquement quand les deux clôtures sont comparables et toutes variations classées new/upsell/departure/contraction/stable ; NULL si movement_kind=unknown ou correction non classée. Aucun résidu transformé en correction/churn. |
| `sum_reconciliation_gap` | `Nullable(Decimal(38,4))` | Oui | Projection sans changement de dtr_company_mrr_month.sum_reconciliation_gap. sum_mrr_end - sum_mrr_begin - sum_new_mrr + sum_churn_mrr - sum_other_mrr_delta, si tous les termes sont calculables. |
| `is_portfolio_entrant` | `Nullable(Bool)` | Oui | Projection sans changement de dtr_company_mrr_month.is_portfolio_entrant. Non actif début et actif fin ; retours compris. Activité indépendante d'un montant nul. |
| `is_departure` | `Nullable(Bool)` | Oui | Projection sans changement de dtr_company_mrr_month.is_departure. Actif début et non actif fin. |
| `is_contraction` | `Nullable(Bool)` | Oui | Projection sans changement de dtr_company_mrr_month.is_contraction. Actif aux deux clôtures et MRR total fin < début. |
| `is_first_acquisition` | `Nullable(Bool)` | Oui | Projection sans changement de dtr_company_mrr_month.is_first_acquisition. true si first_acquisition_status=first_proven, false si return_proven, NULL si unknown selon D27 ; un entrant seul ne prouve jamais première acquisition. |
| `is_begin_observable` | `Bool` | Non | Projection sans changement de dtr_company_mrr_month.is_begin_observable. Clôture précédente suffisamment couverte selon le contrôle source déclaré. |
| `is_end_observable` | `Bool` | Non | Projection sans changement de dtr_company_mrr_month.is_end_observable. Clôture courante suffisamment couverte selon le contrôle source déclaré. |
| `calculation_status` | `String` | Non | Projection sans changement de dtr_company_mrr_month.calculation_status. ready/partial/blocked/not_applicable ; ne pas publier un portefeuille incomplet comme exhaustif. |
| `status_reason` | `Nullable(String)` | Oui | Projection sans changement de dtr_company_mrr_month.status_reason. incomplete_history, unknown_activity, unresolved_company, unknown_amount, unclassified_correction, ou motif upstream. |

**SQL de projection complet :**

```sql
{{ config(materialized='view', schema='dtr_sales') }}

select
    d.model_run_id,
    d.record_key,
    d.record_version_key,
    d.row_hash,
    d.calculated_at,
    d.rule_version,
    d.input_cutoff_at,
    d.tenant_id,
    d.company_key,
    d.company_id,
    d.company_version_key,
    d.company_name,
    d.closing_date,
    d.previous_closing_date,
    d.is_active_begin,
    d.is_active_end,
    d.nb_active_lines_begin,
    d.nb_active_lines_end,
    d.sum_mrr_begin,
    d.sum_mrr_end,
    d.sum_new_mrr_new,
    d.sum_new_mrr_upsell,
    d.sum_new_mrr,
    d.sum_departure_mrr,
    d.sum_contraction_mrr,
    d.sum_churn_mrr,
    d.sum_other_mrr_delta,
    d.sum_reconciliation_gap,
    d.is_portfolio_entrant,
    d.is_departure,
    d.is_contraction,
    d.is_first_acquisition,
    d.is_begin_observable,
    d.is_end_observable,
    d.calculation_status,
    d.status_reason
from {{ ref('dtr_company_mrr_month') }} as d
inner join {{ ref('int_publication') }} as p
    on d.model_run_id = p.model_run_id
```

**Jointure/publication :** DTR N:1 vers la ligne unique du pointeur, égalité de run ; au bootstrap sans pointeur accepté, zéro ligne. Plus d'une ligne de pointeur est ERROR bloquante. Aucune dépendance inverse DTR→publication. Chaque requête BI conserve model_run_id et vérifie sa cohérence avec dataset_publication_status ; une page ne mélange pas plusieurs runs.

**Contrat BI et filtres :** Un seul mois de clôture pour les cartes et la cascade. Une plage de mois sert à une série chronologique, jamais à une somme des stocks. Le filtre financier New/Upsell porte seulement sur le détail des composantes de croissance ; il ne filtre pas les sociétés, les clôtures ou les pertes de la cascade complète. Aucun filtre équipe, canal ou type commercial.

**Calculs restants en restitution :** À une clôture, sommer les montants calculables uniquement lorsque le contrôle de complétude de tout le périmètre est satisfait ; sinon total officiel NULL et détail connu/qualité séparés. Compter les company_key pour entrants/départs/baisses admissibles ; une ligne société/mois empêche les doublons. Plusieurs mois : stocks par mois, flux mensuels sommables sous bornes/couverture compatibles, clients distincts à recalculer selon la question. Ils utilisent les champs détaillés, pas des ratios/quantiles locaux déjà agrégés. Les dates/arrondis/libellés/couleurs se formatent dans la BI ; les champsNULL restent indisponibles, jamais zéro d'affichage implicite. Avant agrégation, vérifier disponibilité PAR MESURE dans dataset_publication_status, y compris absence de lignes de détail.

**Test du dataset :** compter et comparer clés/payloads à la DTR sur le seul run publié ; égalité exacte attendue, ERROR sinon. Tester bootstrap vide, bascule vers nouveau run, réexécution sans modification, navigation tenant+clé+run et détection de publication différente entre requêtes. Rejouer les scénarios de filtres et d'agrégation de `dtr_company_mrr_month`, dont Rapprochement 1:1 après préagrégations ; société avec plusieurs lignes ne multiplie aucun montant ; compensation intra-société uniquement ; gratuité active ; reprise 0→0 d'activité ; NULL de clôture non transformé en zéro ; réconciliation calculable à 0 avec tolérance Decimal définie ; partitions départ et contraction disjointes.

**Rafraîchissement/limites :** la vue reflète le pointeur accepté sans horaire propre ; la fraîcheur dépend des sources, du run et de sa publication. Une règle/preuve manquante dans la DTR n'est pas réparée dans cette vue. Les blocages/limites sont ceux de la DTR et du dataset technique de disponibilité. Une relecture d'ancien run passe par la DTR explicite, sans changement du pointeur.


<a id="dtr_stage_visits"></a>

### `dtr_stage_visits`

**Règle finale v0.2 :** D25/D26 : filtre sur entry_team_key ; is_team_filter_available=true quand l’entrée et son équipe sont observables. Les nonattribués restent dans global/couverture. Seuil par défaut21jours strictement>,classes[0,7),[7,14),[14,30),[30,+inf) modifiables. Ne pas refaire un passage sur transfert ni combler entrée inconnue.

**Couche/module :** DTR, Trois dashboards — Durées. **Finalité :** Durées : bande population passages/opportunités/terminés/en cours ; médiane et P90 terminés ; médiane ancienneté et au-delà du seuil des en-cours ; deux distributions séparées ; médiane par canal recalculée ; liste des passages et navigation vers chronologie. La carte seuil donne NULL + missing_threshold si aucun seuil n'est fourni ; aucune alerte. Les catégories et bornes de distribution restent des paramètres explicites, pas celles de la PNG automatiquement. Afficher nb_entry_date_unknown/nonassignable séparément, avec ce périmètre de couverture hors population filtrée.

**Grain métier :** tenant_id × visit_key ; un passage continu d'une opportunité dans une étape. **Identité logique :** `record_key=H(tenant_id, visit_key)`. **Grain historique/physique :** `(model_run_id,record_key)` ; version=H(run,key), une seule contribution par unité dans un run. Les clés métier et de dimensions sont conservées ci-dessous.

**Amont exact :** `{{ ref('fct_stage_visit') }}`, `{{ ref('dim_company') }}`, `{{ ref('dim_stage') }}`, `{{ ref('dim_sale_type') }}`, `{{ ref('dim_channel') }}`, `{{ ref('dim_employee') }}`, `{{ ref('dim_team') }}`. **Destination :** `dtr_sales.dtr_stage_visits` ; fichier `dbt/models/reporting/dtr/dtr_stage_visits.sql`, YAML `dbt/models/reporting/dtr/_models.yml`.

| Colonne | Type ClickHouse | Nullable | Origine, formule et contraintes |
|---|---|---|---|
| `model_run_id` | `String` | Non | Identifiant de la recomposition complète et immuable ; hérité des entrées du même run. |
| `record_key` | `String` | Non | SHA256 de la liste ordonnée des éléments du grain indiquée dans la fiche ; sérialisation canonique commune, jamais simple concaténation ambiguë. |
| `record_version_key` | `String` | Non | SHA256 de (model_run_id, record_key). |
| `row_hash` | `String` | Non | SHA256 du payload ordonné de la fiche, hors colonnes techniques communes. |
| `calculated_at` | `DateTime64(3, 'UTC')` | Non | Instant de calcul du run ; aucune substitution à une date métier. |
| `rule_version` | `String` | Non | Version immuable des règles et référentiels utilisés par le run. |
| `input_cutoff_at` | `DateTime64(3, 'UTC')` | Non | Borne des entrées figées ; héritée du manifeste de run. |
| `tenant_id` | `String` | Non | Tenant Boond conservé dans les identités et jointures. |
| `opportunity_key` | `String` | Non | Identité stable tenant + opportunité. |
| `opportunity_id` | `Int64` | Non | Identifiant Boond du dossier, pour investigation. |
| `company_key` | `Nullable(String)` | Oui | Identité stable de société résolue au contexte retenu. |
| `company_version_key` | `Nullable(String)` | Oui | Version de société pertinente au contexte retenu. |
| `company_id` | `Nullable(Int64)` | Oui | Identifiant Boond de la société. |
| `company_name` | `Nullable(String)` | Oui | dim_company.company_name par run+company_version_key, N:0..1. |
| `visit_key` | `String` | Non | Identité logique stable du passage ; distincte des versions du run. |
| `visit_rank` | `UInt32` | Non | Rang observé du passage dans le parcours ; NULL si le classement ne peut être établi sans ambiguïté. |
| `stage_id` | `Nullable(Int64)` | Oui | Code de l'étape observée ; les codes ne donnent aucun ordre de funnel. |
| `stage_key` | `Nullable(String)` | Oui | Identité stable de l'étape. |
| `stage_version_key` | `Nullable(String)` | Oui | Version pertinente de dim_stage. |
| `stage_label` | `Nullable(String)` | Oui | dim_stage.stage_label par run+version. |
| `entered_at` | `Nullable(DateTime64(3, 'UTC'))` | Oui | Entrée du passage prouvée ou proxy observé explicitement qualifié ; NULL si début non observable. |
| `exited_at` | `Nullable(DateTime64(3, 'UTC'))` | Oui | Sortie d'étape observée admissible ; une suppression ne crée pas cette sortie métier. |
| `first_observed_at` | `DateTime64(3, 'UTC')` | Non | Première observation disponible du passage ; borne de couverture distincte d'une entrée. |
| `observation_end_at` | `Nullable(DateTime64(3, 'UTC'))` | Oui | Alias explicite de fct_stage_visit.observation_ended_at ; fin technique d'observation, distincte d'une sortie métier. |
| `event_time_basis` | `String` | Non | fct_stage_visit.event_time_basis : cdc_transition_proxy/business_proven/left_censored/observation_only ; aucun proxy rebaptisé date métier certaine. |
| `is_entry_date_known` | `Bool` | Non | entered_at IS NOT NULL ; ce test de connaissance ne donne aucune date aux entrées inconnues. |
| `is_left_censored` | `Bool` | Non | Début du passage non connu avant la première observation. |
| `is_open_visit` | `Bool` | Non | État à la borne du run ; information descriptive, à recalculer pour une observation passée. |
| `completed_duration_seconds` | `Nullable(Float64)` | Oui | (exited_at - entered_at) en millisecondes /1000, si les deux bornes admissibles et la continuité sont connues. |
| `completed_duration_days` | `Nullable(Float64)` | Oui | completed_duration_seconds /86400, sans arrondi intermédiaire. |
| `entry_employee_key` | `Nullable(String)` | Oui | Responsable à l'entrée, descriptif uniquement ; NULL si entrée ou attribution inconnue. |
| `entry_employee_version_key` | `Nullable(String)` | Oui | Version du responsable à l'entrée. |
| `entry_team_key` | `Nullable(String)` | Oui | Équipe à l'entrée, descriptif ; n'autorise pas un filtre de durée sur toute la responsabilité. |
| `entry_team_version_key` | `Nullable(String)` | Oui | Version de l'équipe à l'entrée. |
| `entry_team_name` | `Nullable(String)` | Oui | Libellé descriptif par run+entry_team_version_key. |
| `is_team_filter_available` | `Bool` | Non | true si équipe à entrée connue D25 ; false sinon, sans recours à équipe actuelle. |
| `coverage_start_at` | `Nullable(DateTime64(3, 'UTC'))` | Oui | Début de couverture continue connu pour le passage. |
| `coverage_end_at` | `Nullable(DateTime64(3, 'UTC'))` | Oui | Fin de couverture continue si bornée ; NULL ne prouve pas une couverture infinie. |
| `is_history_complete` | `Nullable(Bool)` | Oui | Complétude déclarée de la séquence utile ; aucune inférence depuis seul min/max CDC. |
| `sale_type_id` | `Nullable(Int64)` | Oui | Type commercial du dossier dans le contexte retenu ; ne désigne pas la composante financière New/Upsell. |
| `sale_type_key` | `Nullable(String)` | Oui | Identité stable du type commercial. |
| `sale_type_version_key` | `Nullable(String)` | Oui | Version de dim_sale_type pertinente. |
| `sale_type_label` | `Nullable(String)` | Oui | dim_sale_type.sale_type_label par run+version, N:0..1. |
| `channel_key` | `Nullable(String)` | Oui | Alias explicite de acquisition_channel_key du fait ; canal officiel d'entrée, NULL avant règle validée. |
| `channel_version_key` | `Nullable(String)` | Oui | Version de mapping du canal, indépendante des sources candidates conservées. |
| `channel_label` | `Nullable(String)` | Oui | dim_channel.channel_label par run+version, N:0..1. |
| `channel_candidate_code` | `Nullable(String)` | Oui | Valeur candidate Boond conservée sans la transformer en canal officiel. |
| `is_channel_calculable` | `Bool` | Non | false si origine à création ou mapping de valeur est manquant ; règle D24 définie, filtre disponible sur les lignes résolues. |
| `calculation_status` | `String` | Non | ready/partial/blocked/not_applicable ; ready n'efface pas les réserves distinctes de couverture. |
| `status_reason` | `Nullable(String)` | Oui | Motif explicite, stable et documenté ; plusieurs motifs séparés de façon canonique si nécessaire. |

**Jointures, identités et cardinalités :** fct_stage_visit porte explicitement le contexte d'entrée et reste propriétaire du grain. LEFT JOIN dimensions N:0..1 par run+version, y compris entry_employee_version_key/entry_team_version_key pour descriptifs. Aucune jointure aux périodes ni aux segments int_visit_responsibility pour calculer les statistiques ; les segments se consultent séparément via opportunity_timeline et run+visit_key.

**Étapes du calcul :** Ne pas recréer de passage sur changement de responsable, montant ou coefficient ; un retour ultérieur est un nouveau visit_key. Conserver bornes, durée finale nullable et couverture. À observation O : terminé si sortie admissible <=O ; en cours si entrée <=O et (sortie absente ou sortie>O) et observation continue jusqu'à O. Une lacune/suppression antérieure à O donne 'non observable', pas 'en cours'. Entrée inconnue : ne pas affecter artificiellement une période d'entrée, garder un compteur qualité hors population mesurable. Compteur séparé nb_entry_date_unknown : entrées NULL parmi tous passages observés avant O pour l'étape/type/canal sélectionnés, SANS filtre de période d'entrée. Étiqueter ce périmètre nonassignable clairement ; il ne fait pas partie des passages entrés dans la période choisie. first_observed_at ne remplace jamais entered_at.

**Filtrage, paramètres et agrégation :** Étape, période d'entrée [entry_from_at, entry_to_at), observation O, type commercial et canal officiel calculable. Filtre équipe sur entry_team_key résolu, selon D25 ; les nonattribués restent visibles globalement, pas réaffectés à l’équipe actuelle. Seuil par défaut21jours strictement dépassé, paramétrable ; classes[0,7),[7,14),[14,30),[30,+inf) selon D26, fournies comme valeurs typées à la requête BI. Une observation ne peut dépasser la couverture admissible du run. Après filtres et séparation terminé/en cours : quantilesExactInclusive(0.5,0.9) sur completed_duration_days des terminés ; quantileExactInclusive(0.5) sur age_days des en-cours. age_days=(O-entered_at en ms)/86400000. Distinguer nb_passages=count du grain et nb_opportunities=distinct opportunity_key ; ne pas les confondre avec sociétés. Aucune moyenne/somme des médianes/P90 de canaux. Distribution et seuil calculés sur valeurs unitaires avant regroupement.

**Matérialisation/histoire :** appliquer le contrat DTR commun ci-dessus : résultats complets du run, incremental append, engine MergeTree, ORDER BY(model_run_id,record_key), unique_key record_version_key, on_schema_change fail, full_refresh false et pas inserts_only. Les tables DTR conservent les anciens runs ; aucun filtre max de date métier ou limite à hier. Au premier chargement/cible vide, calculer l'ensemble ; en reprise, conserver seulement les clés du candidat absentes de la cible, sans modifier un payload existant.

**Contrat de chargement dbt :** une requête SELECT, CTE candidates explicite issue des transformations décrites. Chaque colonne du dictionnaire est produite exactement une fois. Terminer par la projection explicite de candidates ; sous `{% if is_incremental() %}`, LEFT ANTI JOIN de `{{ this }}` sur model_run_id et record_key. Tester absence de deux payloads différents pour une même clé/run AVANT chargement. Le unique_key de configuration assure le chemin de contrôle de schéma de l'adaptateur, pas la déduplication. Les entrées du run et le cutoff sont figés avant toute écriture future ; reprise du même run à empreinte inchangée.

**Construction/rafraîchissement :** après tous amonts du même run ; branches indépendantes parallélisables selon DAG. Exécution manuelle D29 ; fraîcheur de capture/publication déclarée, calcul puis tests/digest et publication contrôlée. Les requêtes de contrôle avant publication utilisent test_model_run_id. Aucun service/modèle n'est créé par la présente fiche.

**Tests/acceptation :** Sortie future par rapport à O => en cours, pas durée finale ; début inconnu=>durées NULL ; retour=>deux passages ; transfert sans nouveau passage ; union terminé/en cours/non observable sans chevauchement ; changement heure Paris ne fausse pas secondes écoulées ; quantiles de [1,2,3,4]=2.5 et3.7 ; mêmes filtres pour cartes/distributions/liste ; seuil absent=>NULL et missing_threshold. Contrôles communs ERROR de grain, hash, cardinalité et run ; WARN/indisponibilité pour manque descriptif ou preuve comme décrit dans le contrat. Tests métier ci-dessus planifiés, pas exécutés sur une implémentation inexistante.


<a id="dataset_stage_visits"></a>

### `dataset_stage_visits`

**Couche/module :** dataset de restitution, Trois dashboards — Durées. **Finalité/consommateurs :** Durées : bande population passages/opportunités/terminés/en cours ; médiane et P90 terminés ; médiane ancienneté et au-delà du seuil des en-cours ; deux distributions séparées ; médiane par canal recalculée ; liste des passages et navigation vers chronologie. La carte seuil donne NULL + missing_threshold si aucun seuil n'est fourni ; aucune alerte. Les catégories et bornes de distribution restent des paramètres explicites, pas celles de la PNG automatiquement. Afficher nb_entry_date_unknown/nonassignable séparément, avec ce périmètre de couverture hors population filtrée.

**Grain métier et version :** exactement celui de `dtr_stage_visits` : tenant_id × visit_key ; un passage continu d'une opportunité dans une étape. Une seule publication est visible ; identité et version sont conservées sans recalcul. Aucun total ni ligne artificielle n'est ajouté.

**Amont exact :** `{{ ref('dtr_stage_visits') }}` et `{{ ref('int_publication') }}`. **Destination :** `dtr_sales.dataset_stage_visits` ; fichier `dbt/models/reporting/datasets/dataset_stage_visits.sql`, YAML `dbt/models/reporting/datasets/_models.yml`.

| Colonne | Type ClickHouse | Nullable | Origine, formule et contraintes |
|---|---|---|---|
| `model_run_id` | `String` | Non | Projection sans changement de dtr_stage_visits.model_run_id. Identifiant de la recomposition complète et immuable ; hérité des entrées du même run. |
| `record_key` | `String` | Non | Projection sans changement de dtr_stage_visits.record_key. SHA256 de la liste ordonnée des éléments du grain indiquée dans la fiche ; sérialisation canonique commune, jamais simple concaténation ambiguë. |
| `record_version_key` | `String` | Non | Projection sans changement de dtr_stage_visits.record_version_key. SHA256 de (model_run_id, record_key). |
| `row_hash` | `String` | Non | Projection sans changement de dtr_stage_visits.row_hash. SHA256 du payload ordonné de la fiche, hors colonnes techniques communes. |
| `calculated_at` | `DateTime64(3, 'UTC')` | Non | Projection sans changement de dtr_stage_visits.calculated_at. Instant de calcul du run ; aucune substitution à une date métier. |
| `rule_version` | `String` | Non | Projection sans changement de dtr_stage_visits.rule_version. Version immuable des règles et référentiels utilisés par le run. |
| `input_cutoff_at` | `DateTime64(3, 'UTC')` | Non | Projection sans changement de dtr_stage_visits.input_cutoff_at. Borne des entrées figées ; héritée du manifeste de run. |
| `tenant_id` | `String` | Non | Projection sans changement de dtr_stage_visits.tenant_id. Tenant Boond conservé dans les identités et jointures. |
| `opportunity_key` | `String` | Non | Projection sans changement de dtr_stage_visits.opportunity_key. Identité stable tenant + opportunité. |
| `opportunity_id` | `Int64` | Non | Projection sans changement de dtr_stage_visits.opportunity_id. Identifiant Boond du dossier, pour investigation. |
| `company_key` | `Nullable(String)` | Oui | Projection sans changement de dtr_stage_visits.company_key. Identité stable de société résolue au contexte retenu. |
| `company_version_key` | `Nullable(String)` | Oui | Projection sans changement de dtr_stage_visits.company_version_key. Version de société pertinente au contexte retenu. |
| `company_id` | `Nullable(Int64)` | Oui | Projection sans changement de dtr_stage_visits.company_id. Identifiant Boond de la société. |
| `company_name` | `Nullable(String)` | Oui | Projection sans changement de dtr_stage_visits.company_name. dim_company.company_name par run+company_version_key, N:0..1. |
| `visit_key` | `String` | Non | Projection sans changement de dtr_stage_visits.visit_key. Identité logique stable du passage ; distincte des versions du run. |
| `visit_rank` | `UInt32` | Non | Projection sans changement de dtr_stage_visits.visit_rank. Rang observé du passage dans le parcours ; NULL si le classement ne peut être établi sans ambiguïté. |
| `stage_id` | `Nullable(Int64)` | Oui | Projection sans changement de dtr_stage_visits.stage_id. Code de l'étape observée ; les codes ne donnent aucun ordre de funnel. |
| `stage_key` | `Nullable(String)` | Oui | Projection sans changement de dtr_stage_visits.stage_key. Identité stable de l'étape. |
| `stage_version_key` | `Nullable(String)` | Oui | Projection sans changement de dtr_stage_visits.stage_version_key. Version pertinente de dim_stage. |
| `stage_label` | `Nullable(String)` | Oui | Projection sans changement de dtr_stage_visits.stage_label. dim_stage.stage_label par run+version. |
| `entered_at` | `Nullable(DateTime64(3, 'UTC'))` | Oui | Projection sans changement de dtr_stage_visits.entered_at. Entrée du passage prouvée ou proxy observé explicitement qualifié ; NULL si début non observable. |
| `exited_at` | `Nullable(DateTime64(3, 'UTC'))` | Oui | Projection sans changement de dtr_stage_visits.exited_at. Sortie d'étape observée admissible ; une suppression ne crée pas cette sortie métier. |
| `first_observed_at` | `DateTime64(3, 'UTC')` | Non | Projection sans changement de dtr_stage_visits.first_observed_at. Première observation disponible du passage ; borne de couverture distincte d'une entrée. |
| `observation_end_at` | `Nullable(DateTime64(3, 'UTC'))` | Oui | Projection sans changement de dtr_stage_visits.observation_end_at. Alias explicite de fct_stage_visit.observation_ended_at ; fin technique d'observation, distincte d'une sortie métier. |
| `event_time_basis` | `String` | Non | Projection sans changement de dtr_stage_visits.event_time_basis. fct_stage_visit.event_time_basis : cdc_transition_proxy/business_proven/left_censored/observation_only ; aucun proxy rebaptisé date métier certaine. |
| `is_entry_date_known` | `Bool` | Non | Projection sans changement de dtr_stage_visits.is_entry_date_known. entered_at IS NOT NULL ; ce test de connaissance ne donne aucune date aux entrées inconnues. |
| `is_left_censored` | `Bool` | Non | Projection sans changement de dtr_stage_visits.is_left_censored. Début du passage non connu avant la première observation. |
| `is_open_visit` | `Bool` | Non | Projection sans changement de dtr_stage_visits.is_open_visit. État à la borne du run ; information descriptive, à recalculer pour une observation passée. |
| `completed_duration_seconds` | `Nullable(Float64)` | Oui | Projection sans changement de dtr_stage_visits.completed_duration_seconds. (exited_at - entered_at) en millisecondes /1000, si les deux bornes admissibles et la continuité sont connues. |
| `completed_duration_days` | `Nullable(Float64)` | Oui | Projection sans changement de dtr_stage_visits.completed_duration_days. completed_duration_seconds /86400, sans arrondi intermédiaire. |
| `entry_employee_key` | `Nullable(String)` | Oui | Projection sans changement de dtr_stage_visits.entry_employee_key. Responsable à l'entrée, descriptif uniquement ; NULL si entrée ou attribution inconnue. |
| `entry_employee_version_key` | `Nullable(String)` | Oui | Projection sans changement de dtr_stage_visits.entry_employee_version_key. Version du responsable à l'entrée. |
| `entry_team_key` | `Nullable(String)` | Oui | Projection sans changement de dtr_stage_visits.entry_team_key. Équipe à l'entrée, descriptif ; n'autorise pas un filtre de durée sur toute la responsabilité. |
| `entry_team_version_key` | `Nullable(String)` | Oui | Projection sans changement de dtr_stage_visits.entry_team_version_key. Version de l'équipe à l'entrée. |
| `entry_team_name` | `Nullable(String)` | Oui | Projection sans changement de dtr_stage_visits.entry_team_name. Libellé descriptif par run+entry_team_version_key. |
| `is_team_filter_available` | `Bool` | Non | Projection sans changement de dtr_stage_visits.is_team_filter_available. true si équipe à entrée connue D25 ; false sinon, sans recours à équipe actuelle. |
| `coverage_start_at` | `Nullable(DateTime64(3, 'UTC'))` | Oui | Projection sans changement de dtr_stage_visits.coverage_start_at. Début de couverture continue connu pour le passage. |
| `coverage_end_at` | `Nullable(DateTime64(3, 'UTC'))` | Oui | Projection sans changement de dtr_stage_visits.coverage_end_at. Fin de couverture continue si bornée ; NULL ne prouve pas une couverture infinie. |
| `is_history_complete` | `Nullable(Bool)` | Oui | Projection sans changement de dtr_stage_visits.is_history_complete. Complétude déclarée de la séquence utile ; aucune inférence depuis seul min/max CDC. |
| `sale_type_id` | `Nullable(Int64)` | Oui | Projection sans changement de dtr_stage_visits.sale_type_id. Type commercial du dossier dans le contexte retenu ; ne désigne pas la composante financière New/Upsell. |
| `sale_type_key` | `Nullable(String)` | Oui | Projection sans changement de dtr_stage_visits.sale_type_key. Identité stable du type commercial. |
| `sale_type_version_key` | `Nullable(String)` | Oui | Projection sans changement de dtr_stage_visits.sale_type_version_key. Version de dim_sale_type pertinente. |
| `sale_type_label` | `Nullable(String)` | Oui | Projection sans changement de dtr_stage_visits.sale_type_label. dim_sale_type.sale_type_label par run+version, N:0..1. |
| `channel_key` | `Nullable(String)` | Oui | Projection sans changement de dtr_stage_visits.channel_key. Alias explicite de acquisition_channel_key du fait ; canal officiel d'entrée, NULL avant règle validée. |
| `channel_version_key` | `Nullable(String)` | Oui | Projection sans changement de dtr_stage_visits.channel_version_key. Version de mapping du canal, indépendante des sources candidates conservées. |
| `channel_label` | `Nullable(String)` | Oui | Projection sans changement de dtr_stage_visits.channel_label. dim_channel.channel_label par run+version, N:0..1. |
| `channel_candidate_code` | `Nullable(String)` | Oui | Projection sans changement de dtr_stage_visits.channel_candidate_code. Valeur candidate Boond conservée sans la transformer en canal officiel. |
| `is_channel_calculable` | `Bool` | Non | Projection sans changement de dtr_stage_visits.is_channel_calculable. false si origine à création ou mapping de valeur est manquant ; règle D24 définie, filtre disponible sur les lignes résolues. |
| `calculation_status` | `String` | Non | Projection sans changement de dtr_stage_visits.calculation_status. ready/partial/blocked/not_applicable ; ready n'efface pas les réserves distinctes de couverture. |
| `status_reason` | `Nullable(String)` | Oui | Projection sans changement de dtr_stage_visits.status_reason. Motif explicite, stable et documenté ; plusieurs motifs séparés de façon canonique si nécessaire. |

**SQL de projection complet :**

```sql
{{ config(materialized='view', schema='dtr_sales') }}

select
    d.model_run_id,
    d.record_key,
    d.record_version_key,
    d.row_hash,
    d.calculated_at,
    d.rule_version,
    d.input_cutoff_at,
    d.tenant_id,
    d.opportunity_key,
    d.opportunity_id,
    d.company_key,
    d.company_version_key,
    d.company_id,
    d.company_name,
    d.visit_key,
    d.visit_rank,
    d.stage_id,
    d.stage_key,
    d.stage_version_key,
    d.stage_label,
    d.entered_at,
    d.exited_at,
    d.first_observed_at,
    d.observation_end_at,
    d.event_time_basis,
    d.is_entry_date_known,
    d.is_left_censored,
    d.is_open_visit,
    d.completed_duration_seconds,
    d.completed_duration_days,
    d.entry_employee_key,
    d.entry_employee_version_key,
    d.entry_team_key,
    d.entry_team_version_key,
    d.entry_team_name,
    d.is_team_filter_available,
    d.coverage_start_at,
    d.coverage_end_at,
    d.is_history_complete,
    d.sale_type_id,
    d.sale_type_key,
    d.sale_type_version_key,
    d.sale_type_label,
    d.channel_key,
    d.channel_version_key,
    d.channel_label,
    d.channel_candidate_code,
    d.is_channel_calculable,
    d.calculation_status,
    d.status_reason
from {{ ref('dtr_stage_visits') }} as d
inner join {{ ref('int_publication') }} as p
    on d.model_run_id = p.model_run_id
```

**Jointure/publication :** DTR N:1 vers la ligne unique du pointeur, égalité de run ; au bootstrap sans pointeur accepté, zéro ligne. Plus d'une ligne de pointeur est ERROR bloquante. Aucune dépendance inverse DTR→publication. Chaque requête BI conserve model_run_id et vérifie sa cohérence avec dataset_publication_status ; une page ne mélange pas plusieurs runs.

**Contrat BI et filtres :** Étape, période d'entrée [entry_from_at, entry_to_at), observation O, type commercial et canal officiel calculable. Filtre équipe sur entry_team_key résolu, selon D25 ; les nonattribués restent visibles globalement, pas réaffectés à l’équipe actuelle. Seuil par défaut21jours strictement dépassé, paramétrable ; classes[0,7),[7,14),[14,30),[30,+inf) selon D26, fournies comme valeurs typées à la requête BI. Une observation ne peut dépasser la couverture admissible du run.

**Calculs restants en restitution :** Après filtres et séparation terminé/en cours : quantilesExactInclusive(0.5,0.9) sur completed_duration_days des terminés ; quantileExactInclusive(0.5) sur age_days des en-cours. age_days=(O-entered_at en ms)/86400000. Distinguer nb_passages=count du grain et nb_opportunities=distinct opportunity_key ; ne pas les confondre avec sociétés. Aucune moyenne/somme des médianes/P90 de canaux. Distribution et seuil calculés sur valeurs unitaires avant regroupement. Ils utilisent les champs détaillés, pas des ratios/quantiles locaux déjà agrégés. Les dates/arrondis/libellés/couleurs se formatent dans la BI ; les champsNULL restent indisponibles, jamais zéro d'affichage implicite. Avant agrégation, vérifier disponibilité PAR MESURE dans dataset_publication_status, y compris absence de lignes de détail.

**Test du dataset :** compter et comparer clés/payloads à la DTR sur le seul run publié ; égalité exacte attendue, ERROR sinon. Tester bootstrap vide, bascule vers nouveau run, réexécution sans modification, navigation tenant+clé+run et détection de publication différente entre requêtes. Rejouer les scénarios de filtres et d'agrégation de `dtr_stage_visits`, dont Sortie future par rapport à O => en cours, pas durée finale ; début inconnu=>durées NULL ; retour=>deux passages ; transfert sans nouveau passage ; union terminé/en cours/non observable sans chevauchement ; changement heure Paris ne fausse pas secondes écoulées ; quantiles de [1,2,3,4]=2.5 et3.7 ; mêmes filtres pour cartes/distributions/liste ; seuil absent=>NULL et missing_threshold.

**Rafraîchissement/limites :** la vue reflète le pointeur accepté sans horaire propre ; la fraîcheur dépend des sources, du run et de sa publication. Une règle/preuve manquante dans la DTR n'est pas réparée dans cette vue. Les blocages/limites sont ceux de la DTR et du dataset technique de disponibilité. Une relecture d'ancien run passe par la DTR explicite, sans changement du pointeur.


<a id="dtr_cohort_outcomes"></a>

### `dtr_cohort_outcomes`

**Règle finale v0.2 :** D18 : état au J+30/60/90 ; gagné rouvert avant J peut être ouvert à J. Dénominateur complet y compris autres/inconnus ; maturité entière du mois/type avant filtre équipe/canal. Pas d’acquisition de connaissance avant sa couverture.

**Couche/module :** DTR, Trois dashboards — Cohortes. **Finalité :** Cohortes : taille et cartes ouvert/gagné/perdu ; matrice mois×horizon ; état non mature grisé et NULL ; évolution de la cohorte sélectionnée ; tableau d'effectifs par canal ; couverture et autres/inconnus visibles ; navigation dossier vers timeline. Les pourcentages à l'horizon prennent le statut corrigé à l'horizon, pas la dernière issue actuelle.

**Grain métier :** tenant_id × opportunity_key × followup_definition_key × anchor_at × horizon_days ; une opportunité de sa cohorte de création par horizon. **Identité logique :** `record_key=H(tenant_id, opportunity_key, followup_definition_key, anchor_key, horizon_days)`. **Grain historique/physique :** `(model_run_id,record_key)` ; version=H(run,key), une seule contribution par unité dans un run. Les clés métier et de dimensions sont conservées ci-dessous.

**Amont exact :** `{{ ref('fct_opportunity_followup') }}`, `{{ ref('dim_followup_definition') }}`, `{{ ref('dim_company') }}`, `{{ ref('dim_sale_type') }}`, `{{ ref('dim_channel') }}`, `{{ ref('dim_employee') }}`, `{{ ref('dim_team') }}`. **Destination :** `dtr_sales.dtr_cohort_outcomes` ; fichier `dbt/models/reporting/dtr/dtr_cohort_outcomes.sql`, YAML `dbt/models/reporting/dtr/_models.yml`.

| Colonne | Type ClickHouse | Nullable | Origine, formule et contraintes |
|---|---|---|---|
| `model_run_id` | `String` | Non | Identifiant de la recomposition complète et immuable ; hérité des entrées du même run. |
| `record_key` | `String` | Non | SHA256 de la liste ordonnée des éléments du grain indiquée dans la fiche ; sérialisation canonique commune, jamais simple concaténation ambiguë. |
| `record_version_key` | `String` | Non | SHA256 de (model_run_id, record_key). |
| `row_hash` | `String` | Non | SHA256 du payload ordonné de la fiche, hors colonnes techniques communes. |
| `calculated_at` | `DateTime64(3, 'UTC')` | Non | Instant de calcul du run ; aucune substitution à une date métier. |
| `rule_version` | `String` | Non | Version immuable des règles et référentiels utilisés par le run. |
| `input_cutoff_at` | `DateTime64(3, 'UTC')` | Non | Borne des entrées figées ; héritée du manifeste de run. |
| `tenant_id` | `String` | Non | Tenant Boond conservé dans les identités et jointures. |
| `opportunity_key` | `String` | Non | Identité stable tenant + opportunité. |
| `opportunity_id` | `Int64` | Non | Identifiant Boond du dossier, pour investigation. |
| `company_key` | `Nullable(String)` | Oui | Identité stable de société résolue au contexte retenu. |
| `company_version_key` | `Nullable(String)` | Oui | Version de société pertinente au contexte retenu. |
| `company_id` | `Nullable(Int64)` | Oui | Identifiant Boond de la société. |
| `company_name` | `Nullable(String)` | Oui | dim_company.company_name par run+company_version_key, N:0..1. |
| `followup_key` | `String` | Non | Identité logique de l'observation du fait. |
| `followup_definition_key` | `String` | Non | Identité de définition de suivi explicitement retenue. |
| `followup_definition_version_key` | `Nullable(String)` | Oui | Version de la définition du même run. |
| `created_at` | `Nullable(DateTime64(3, 'UTC'))` | Oui | Création individuelle Boond, ancrage décidé ; les créations manquantes sont des anomalies de couverture hors cohorte calculable. |
| `anchor_key` | `String` | Non | fct_opportunity_followup.anchor_key ; identité source de l'ancrage, distincte de son timestamp éventuellement inconnu. |
| `anchor_at` | `Nullable(DateTime64(3, 'UTC'))` | Oui | Création individuelle pour cette définition, sans changement de cohorte sur réentrée. |
| `cohort_month` | `Nullable(Date)` | Oui | Premier jour du mois civil de created_at en Europe/Paris. |
| `horizon_days` | `Nullable(UInt16)` | Oui | 30,60 ou90 selon les horizons demandés. |
| `horizon_at` | `Nullable(DateTime64(3, 'UTC'))` | Oui | Ajouter horizon_days jours calendaires à la création en Europe/Paris à même heure locale, puis conserver l'instant UTC. |
| `cohort_mature_at` | `Nullable(DateTime64(3, 'UTC'))` | Oui | max(horizon_at) parmi tous membres connus tenant/mois/type commercial/définition/horizon, AVANT filtres équipe et canal. |
| `issue_at_horizon` | `Nullable(String)` | Oui | open/won/lost/abandoned/unqualified/unknown lorsque horizon évalué ; nurturing=open. NULL si horizon non atteint au run. |
| `is_eligible` | `Nullable(Bool)` | Oui | Admissibilité de l'unique ancrage dans la population de création ; ne pas exclure silencieusement un inconnu. |
| `is_mature` | `Nullable(Bool)` | Oui | horizon_at <= observation du run, conservé pour contrôle ; à recalculer si observation BI différente. |
| `is_cohort_mature` | `Nullable(Bool)` | Oui | cohort_mature_at <= observation du run ; à recalculer pour observation BI différente. |
| `is_observable` | `Nullable(Bool)` | Oui | L'histoire permet de déterminer le statut à horizon_at ; distinct de maturité. |
| `coverage_start_at` | `Nullable(DateTime64(3, 'UTC'))` | Oui | Début observable de l'historique utile du dossier. |
| `coverage_end_at` | `Nullable(DateTime64(3, 'UTC'))` | Oui | Fin observable connue. |
| `is_history_complete` | `Nullable(Bool)` | Oui | Couverture déclarée ; la maturité ne prouve jamais l'exhaustivité des membres ni l'observabilité. |
| `nb_cohort_membership` | `UInt8` | Non | 1 pour cette identité admissible de cohorte/horizon ; effectif de base connu, pas à sommer entre horizons. |
| `denominator_contribution` | `Nullable(UInt8)` | Oui | 1 pour le membre de base à horizon mature ; NULL pour non mature ou inadmissible non résolu. Les inconnus matures restent au dénominateur. |
| `open_contribution` | `Nullable(UInt8)` | Oui | 1 si issue=open à horizon mature, 0 si une autre issue mature, NULL si horizon non mature. |
| `won_contribution` | `Nullable(UInt8)` | Oui | Même convention pour won ; état 1 constitue victoire, état 14 ne crée pas une nouvelle ligne. |
| `lost_contribution` | `Nullable(UInt8)` | Oui | Même convention pour lost, distinct des abandons/nonqualifiés. |
| `abandoned_contribution` | `Nullable(UInt8)` | Oui | Même convention pour abandoned, conservé séparément. |
| `unqualified_contribution` | `Nullable(UInt8)` | Oui | Même convention pour unqualified, conservé séparément. |
| `unknown_contribution` | `Nullable(UInt8)` | Oui | 1 pour mature avec état/couverture non observable ou non classable ; NULL pour non mature. Maintient la base entière, sans classer l'inconnu comme perdu. |
| `sale_type_id` | `Nullable(Int64)` | Oui | Type commercial du dossier dans le contexte retenu ; ne désigne pas la composante financière New/Upsell. |
| `sale_type_key` | `Nullable(String)` | Oui | Identité stable du type commercial. |
| `sale_type_version_key` | `Nullable(String)` | Oui | Version de dim_sale_type pertinente. |
| `sale_type_label` | `Nullable(String)` | Oui | dim_sale_type.sale_type_label par run+version, N:0..1. |
| `channel_key` | `Nullable(String)` | Oui | Alias explicite de acquisition_channel_key du fait ; canal officiel d'entrée, NULL avant règle validée. |
| `channel_version_key` | `Nullable(String)` | Oui | Version de mapping du canal, indépendante des sources candidates conservées. |
| `channel_label` | `Nullable(String)` | Oui | dim_channel.channel_label par run+version, N:0..1. |
| `channel_candidate_code` | `Nullable(String)` | Oui | Valeur candidate Boond conservée sans la transformer en canal officiel. |
| `is_channel_calculable` | `Bool` | Non | false si origine à création ou mapping de valeur est manquant ; règle D24 définie, filtre disponible sur les lignes résolues. |
| `employee_key` | `Nullable(String)` | Oui | Identité stable du responsable retenu. |
| `employee_version_key` | `Nullable(String)` | Oui | Version descriptive du responsable. |
| `employee_display_name` | `Nullable(String)` | Oui | dim_employee.employee_display_name par run+version, N:0..1. |
| `team_key` | `Nullable(String)` | Oui | Équipe historiquement retenue si mapping et attribution validés. |
| `team_version_key` | `Nullable(String)` | Oui | Version de l'équipe pertinente. |
| `team_name` | `Nullable(String)` | Oui | dim_team.team_name par run+version, N:0..1. |
| `is_team_calculable` | `Bool` | Non | false pour rattachement à entrée/événement inconnu ou ambigu ; sinon true y compris KAM connue, indépendamment de son absence de cible D23. |
| `calculation_status` | `String` | Non | ready/partial/blocked/not_applicable ; ready n'efface pas les réserves distinctes de couverture. |
| `status_reason` | `Nullable(String)` | Oui | Motif explicite, stable et documenté ; plusieurs motifs séparés de façon canonique si nécessaire. |

**Jointures, identités et cardinalités :** Sélectionner les followup du même run dont la définition est cohort_outcome ; dim_followup_definition N:0..1 par run+version. Chaque dimension de contexte N:0..1 par run+version. cohort_mature_at provient d'une agrégation par tenant/mois/type/définition/horizon puis jointure N:1 à tous les membres, avant enrichissements/équipe/canal. Ne pas agréger une deuxième fois des définitions/ancrages/horizons différents dans un dénominateur.

**Étapes du calcul :** Une création individuelle, un ancrage canonique et trois horizons. Conserver les autres issues décidées et inconnus. La DTR ne renormalise jamais open/won/lost à100%. Pour observation O, cohort_complete=(cohort_mature_at<=O). Tant que faux, toutes proportions affichées de cet horizon sont NULL et badge non mature ; la taille connue de cohorte peut être affichée. Quand vrai, les inconnus restent au dénominateur avec compteur/part explicite et couverture. La règle max des membres connus par mois/type est une proposition technique d'application de la décision de maturité entière ; elle ne garantit pas qu'aucune création source ne manque. Les lignes dont création/ancrage/horizon sont inconnus sont conservées en diagnostic (colonnesNULL), non affectées artificiellement à un mois ; la couverture globale annonce qu'elles ne sont pas assignables à une cohorte connue.

**Filtrage, paramètres et agrégation :** Mois de création [cohort_from_month,cohort_to_month), observation O, type commercial, équipe et canal calculables, zoom cohorte et horizon30/60/90. Maturité définie AVANT équipe/canal : aucun filtre n'avance la date de maturité. Chaque type commercial conserve sa propre cohorte. Les ratios combinant plusieurs types ne sont publiés que si chaque sous-cohorte sélectionnée est mature ; sinon résultat non mature. Ni seuil ni filtre financier New/Upsell. Pour une cohorte/horizon et même définition, Nbase=sum(nb_cohort_membership). Si cohorte mature, Nissue=sum(contribution), taux=Nissue/Nbase lorsque Nbase>0 et admissibilité connue ; sinon NULL. Les parts open/won/lost peuvent totaliser moins de100% : afficher autres et inconnus. La somme de toutes six catégories mature doit égaler Nbase. Jamais sommer Nbase sur30/60/90 ; réutiliser une seule base. Zoom canal : effectifs et même dénominateur de chaque ligne, total recomposé depuis identités/grain compatible.

**Matérialisation/histoire :** appliquer le contrat DTR commun ci-dessus : résultats complets du run, incremental append, engine MergeTree, ORDER BY(model_run_id,record_key), unique_key record_version_key, on_schema_change fail, full_refresh false et pas inserts_only. Les tables DTR conservent les anciens runs ; aucun filtre max de date métier ou limite à hier. Au premier chargement/cible vide, calculer l'ensemble ; en reprise, conserver seulement les clés du candidat absentes de la cible, sans modifier un payload existant.

**Contrat de chargement dbt :** une requête SELECT, CTE candidates explicite issue des transformations décrites. Chaque colonne du dictionnaire est produite exactement une fois. Terminer par la projection explicite de candidates ; sous `{% if is_incremental() %}`, LEFT ANTI JOIN de `{{ this }}` sur model_run_id et record_key. Tester absence de deux payloads différents pour une même clé/run AVANT chargement. Le unique_key de configuration assure le chemin de contrôle de schéma de l'adaptateur, pas la déduplication. Les entrées du run et le cutoff sont figés avant toute écriture future ; reprise du même run à empreinte inchangée.

**Construction/rafraîchissement :** après tous amonts du même run ; branches indépendantes parallélisables selon DAG. Exécution manuelle D29 ; fraîcheur de capture/publication déclarée, calcul puis tests/digest et publication contrôlée. Les requêtes de contrôle avant publication utilisent test_model_run_id. Aucun service/modèle n'est créé par la présente fiche.

**Tests/acceptation :** Trois horizons par membre/définition ; cohort_month correspond à création Paris ; horizon local même heure autour passages heure été/hiver ; max maturité invariant sous filtre équipe/canal ; aucune valeur future=>0 ; nurturing ouvert ; abandonné/nonqualifié séparés ; somme des six issues=base mature ; inconnus inclus ; état 1→14 une victoire ; réouverture classée par état à horizon. Contrôles communs ERROR de grain, hash, cardinalité et run ; WARN/indisponibilité pour manque descriptif ou preuve comme décrit dans le contrat. Tests métier ci-dessus planifiés, pas exécutés sur une implémentation inexistante.


<a id="dataset_cohort_outcomes"></a>

### `dataset_cohort_outcomes`

**Couche/module :** dataset de restitution, Trois dashboards — Cohortes. **Finalité/consommateurs :** Cohortes : taille et cartes ouvert/gagné/perdu ; matrice mois×horizon ; état non mature grisé et NULL ; évolution de la cohorte sélectionnée ; tableau d'effectifs par canal ; couverture et autres/inconnus visibles ; navigation dossier vers timeline. Les pourcentages à l'horizon prennent le statut corrigé à l'horizon, pas la dernière issue actuelle.

**Grain métier et version :** exactement celui de `dtr_cohort_outcomes` : tenant_id × opportunity_key × followup_definition_key × anchor_at × horizon_days ; une opportunité de sa cohorte de création par horizon. Une seule publication est visible ; identité et version sont conservées sans recalcul. Aucun total ni ligne artificielle n'est ajouté.

**Amont exact :** `{{ ref('dtr_cohort_outcomes') }}` et `{{ ref('int_publication') }}`. **Destination :** `dtr_sales.dataset_cohort_outcomes` ; fichier `dbt/models/reporting/datasets/dataset_cohort_outcomes.sql`, YAML `dbt/models/reporting/datasets/_models.yml`.

| Colonne | Type ClickHouse | Nullable | Origine, formule et contraintes |
|---|---|---|---|
| `model_run_id` | `String` | Non | Projection sans changement de dtr_cohort_outcomes.model_run_id. Identifiant de la recomposition complète et immuable ; hérité des entrées du même run. |
| `record_key` | `String` | Non | Projection sans changement de dtr_cohort_outcomes.record_key. SHA256 de la liste ordonnée des éléments du grain indiquée dans la fiche ; sérialisation canonique commune, jamais simple concaténation ambiguë. |
| `record_version_key` | `String` | Non | Projection sans changement de dtr_cohort_outcomes.record_version_key. SHA256 de (model_run_id, record_key). |
| `row_hash` | `String` | Non | Projection sans changement de dtr_cohort_outcomes.row_hash. SHA256 du payload ordonné de la fiche, hors colonnes techniques communes. |
| `calculated_at` | `DateTime64(3, 'UTC')` | Non | Projection sans changement de dtr_cohort_outcomes.calculated_at. Instant de calcul du run ; aucune substitution à une date métier. |
| `rule_version` | `String` | Non | Projection sans changement de dtr_cohort_outcomes.rule_version. Version immuable des règles et référentiels utilisés par le run. |
| `input_cutoff_at` | `DateTime64(3, 'UTC')` | Non | Projection sans changement de dtr_cohort_outcomes.input_cutoff_at. Borne des entrées figées ; héritée du manifeste de run. |
| `tenant_id` | `String` | Non | Projection sans changement de dtr_cohort_outcomes.tenant_id. Tenant Boond conservé dans les identités et jointures. |
| `opportunity_key` | `String` | Non | Projection sans changement de dtr_cohort_outcomes.opportunity_key. Identité stable tenant + opportunité. |
| `opportunity_id` | `Int64` | Non | Projection sans changement de dtr_cohort_outcomes.opportunity_id. Identifiant Boond du dossier, pour investigation. |
| `company_key` | `Nullable(String)` | Oui | Projection sans changement de dtr_cohort_outcomes.company_key. Identité stable de société résolue au contexte retenu. |
| `company_version_key` | `Nullable(String)` | Oui | Projection sans changement de dtr_cohort_outcomes.company_version_key. Version de société pertinente au contexte retenu. |
| `company_id` | `Nullable(Int64)` | Oui | Projection sans changement de dtr_cohort_outcomes.company_id. Identifiant Boond de la société. |
| `company_name` | `Nullable(String)` | Oui | Projection sans changement de dtr_cohort_outcomes.company_name. dim_company.company_name par run+company_version_key, N:0..1. |
| `followup_key` | `String` | Non | Projection sans changement de dtr_cohort_outcomes.followup_key. Identité logique de l'observation du fait. |
| `followup_definition_key` | `String` | Non | Projection sans changement de dtr_cohort_outcomes.followup_definition_key. Identité de définition de suivi explicitement retenue. |
| `followup_definition_version_key` | `Nullable(String)` | Oui | Projection sans changement de dtr_cohort_outcomes.followup_definition_version_key. Version de la définition du même run. |
| `created_at` | `Nullable(DateTime64(3, 'UTC'))` | Oui | Projection sans changement de dtr_cohort_outcomes.created_at. Création individuelle Boond, ancrage décidé ; les créations manquantes sont des anomalies de couverture hors cohorte calculable. |
| `anchor_key` | `String` | Non | Projection sans changement de dtr_cohort_outcomes.anchor_key. fct_opportunity_followup.anchor_key ; identité source de l'ancrage, distincte de son timestamp éventuellement inconnu. |
| `anchor_at` | `Nullable(DateTime64(3, 'UTC'))` | Oui | Projection sans changement de dtr_cohort_outcomes.anchor_at. Création individuelle pour cette définition, sans changement de cohorte sur réentrée. |
| `cohort_month` | `Nullable(Date)` | Oui | Projection sans changement de dtr_cohort_outcomes.cohort_month. Premier jour du mois civil de created_at en Europe/Paris. |
| `horizon_days` | `Nullable(UInt16)` | Oui | Projection sans changement de dtr_cohort_outcomes.horizon_days. 30,60 ou90 selon les horizons demandés. |
| `horizon_at` | `Nullable(DateTime64(3, 'UTC'))` | Oui | Projection sans changement de dtr_cohort_outcomes.horizon_at. Ajouter horizon_days jours calendaires à la création en Europe/Paris à même heure locale, puis conserver l'instant UTC. |
| `cohort_mature_at` | `Nullable(DateTime64(3, 'UTC'))` | Oui | Projection sans changement de dtr_cohort_outcomes.cohort_mature_at. max(horizon_at) parmi tous membres connus tenant/mois/type commercial/définition/horizon, AVANT filtres équipe et canal. |
| `issue_at_horizon` | `Nullable(String)` | Oui | Projection sans changement de dtr_cohort_outcomes.issue_at_horizon. open/won/lost/abandoned/unqualified/unknown lorsque horizon évalué ; nurturing=open. NULL si horizon non atteint au run. |
| `is_eligible` | `Nullable(Bool)` | Oui | Projection sans changement de dtr_cohort_outcomes.is_eligible. Admissibilité de l'unique ancrage dans la population de création ; ne pas exclure silencieusement un inconnu. |
| `is_mature` | `Nullable(Bool)` | Oui | Projection sans changement de dtr_cohort_outcomes.is_mature. horizon_at <= observation du run, conservé pour contrôle ; à recalculer si observation BI différente. |
| `is_cohort_mature` | `Nullable(Bool)` | Oui | Projection sans changement de dtr_cohort_outcomes.is_cohort_mature. cohort_mature_at <= observation du run ; à recalculer pour observation BI différente. |
| `is_observable` | `Nullable(Bool)` | Oui | Projection sans changement de dtr_cohort_outcomes.is_observable. L'histoire permet de déterminer le statut à horizon_at ; distinct de maturité. |
| `coverage_start_at` | `Nullable(DateTime64(3, 'UTC'))` | Oui | Projection sans changement de dtr_cohort_outcomes.coverage_start_at. Début observable de l'historique utile du dossier. |
| `coverage_end_at` | `Nullable(DateTime64(3, 'UTC'))` | Oui | Projection sans changement de dtr_cohort_outcomes.coverage_end_at. Fin observable connue. |
| `is_history_complete` | `Nullable(Bool)` | Oui | Projection sans changement de dtr_cohort_outcomes.is_history_complete. Couverture déclarée ; la maturité ne prouve jamais l'exhaustivité des membres ni l'observabilité. |
| `nb_cohort_membership` | `UInt8` | Non | Projection sans changement de dtr_cohort_outcomes.nb_cohort_membership. 1 pour cette identité admissible de cohorte/horizon ; effectif de base connu, pas à sommer entre horizons. |
| `denominator_contribution` | `Nullable(UInt8)` | Oui | Projection sans changement de dtr_cohort_outcomes.denominator_contribution. 1 pour le membre de base à horizon mature ; NULL pour non mature ou inadmissible non résolu. Les inconnus matures restent au dénominateur. |
| `open_contribution` | `Nullable(UInt8)` | Oui | Projection sans changement de dtr_cohort_outcomes.open_contribution. 1 si issue=open à horizon mature, 0 si une autre issue mature, NULL si horizon non mature. |
| `won_contribution` | `Nullable(UInt8)` | Oui | Projection sans changement de dtr_cohort_outcomes.won_contribution. Même convention pour won ; état 1 constitue victoire, état 14 ne crée pas une nouvelle ligne. |
| `lost_contribution` | `Nullable(UInt8)` | Oui | Projection sans changement de dtr_cohort_outcomes.lost_contribution. Même convention pour lost, distinct des abandons/nonqualifiés. |
| `abandoned_contribution` | `Nullable(UInt8)` | Oui | Projection sans changement de dtr_cohort_outcomes.abandoned_contribution. Même convention pour abandoned, conservé séparément. |
| `unqualified_contribution` | `Nullable(UInt8)` | Oui | Projection sans changement de dtr_cohort_outcomes.unqualified_contribution. Même convention pour unqualified, conservé séparément. |
| `unknown_contribution` | `Nullable(UInt8)` | Oui | Projection sans changement de dtr_cohort_outcomes.unknown_contribution. 1 pour mature avec état/couverture non observable ou non classable ; NULL pour non mature. Maintient la base entière, sans classer l'inconnu comme perdu. |
| `sale_type_id` | `Nullable(Int64)` | Oui | Projection sans changement de dtr_cohort_outcomes.sale_type_id. Type commercial du dossier dans le contexte retenu ; ne désigne pas la composante financière New/Upsell. |
| `sale_type_key` | `Nullable(String)` | Oui | Projection sans changement de dtr_cohort_outcomes.sale_type_key. Identité stable du type commercial. |
| `sale_type_version_key` | `Nullable(String)` | Oui | Projection sans changement de dtr_cohort_outcomes.sale_type_version_key. Version de dim_sale_type pertinente. |
| `sale_type_label` | `Nullable(String)` | Oui | Projection sans changement de dtr_cohort_outcomes.sale_type_label. dim_sale_type.sale_type_label par run+version, N:0..1. |
| `channel_key` | `Nullable(String)` | Oui | Projection sans changement de dtr_cohort_outcomes.channel_key. Alias explicite de acquisition_channel_key du fait ; canal officiel d'entrée, NULL avant règle validée. |
| `channel_version_key` | `Nullable(String)` | Oui | Projection sans changement de dtr_cohort_outcomes.channel_version_key. Version de mapping du canal, indépendante des sources candidates conservées. |
| `channel_label` | `Nullable(String)` | Oui | Projection sans changement de dtr_cohort_outcomes.channel_label. dim_channel.channel_label par run+version, N:0..1. |
| `channel_candidate_code` | `Nullable(String)` | Oui | Projection sans changement de dtr_cohort_outcomes.channel_candidate_code. Valeur candidate Boond conservée sans la transformer en canal officiel. |
| `is_channel_calculable` | `Bool` | Non | Projection sans changement de dtr_cohort_outcomes.is_channel_calculable. false si origine à création ou mapping de valeur est manquant ; règle D24 définie, filtre disponible sur les lignes résolues. |
| `employee_key` | `Nullable(String)` | Oui | Projection sans changement de dtr_cohort_outcomes.employee_key. Identité stable du responsable retenu. |
| `employee_version_key` | `Nullable(String)` | Oui | Projection sans changement de dtr_cohort_outcomes.employee_version_key. Version descriptive du responsable. |
| `employee_display_name` | `Nullable(String)` | Oui | Projection sans changement de dtr_cohort_outcomes.employee_display_name. dim_employee.employee_display_name par run+version, N:0..1. |
| `team_key` | `Nullable(String)` | Oui | Projection sans changement de dtr_cohort_outcomes.team_key. Équipe historiquement retenue si mapping et attribution validés. |
| `team_version_key` | `Nullable(String)` | Oui | Projection sans changement de dtr_cohort_outcomes.team_version_key. Version de l'équipe pertinente. |
| `team_name` | `Nullable(String)` | Oui | Projection sans changement de dtr_cohort_outcomes.team_name. dim_team.team_name par run+version, N:0..1. |
| `is_team_calculable` | `Bool` | Non | Projection sans changement de dtr_cohort_outcomes.is_team_calculable. false pour rattachement à entrée/événement inconnu ou ambigu ; sinon true y compris KAM connue, indépendamment de son absence de cible D23. |
| `calculation_status` | `String` | Non | Projection sans changement de dtr_cohort_outcomes.calculation_status. ready/partial/blocked/not_applicable ; ready n'efface pas les réserves distinctes de couverture. |
| `status_reason` | `Nullable(String)` | Oui | Projection sans changement de dtr_cohort_outcomes.status_reason. Motif explicite, stable et documenté ; plusieurs motifs séparés de façon canonique si nécessaire. |

**SQL de projection complet :**

```sql
{{ config(materialized='view', schema='dtr_sales') }}

select
    d.model_run_id,
    d.record_key,
    d.record_version_key,
    d.row_hash,
    d.calculated_at,
    d.rule_version,
    d.input_cutoff_at,
    d.tenant_id,
    d.opportunity_key,
    d.opportunity_id,
    d.company_key,
    d.company_version_key,
    d.company_id,
    d.company_name,
    d.followup_key,
    d.followup_definition_key,
    d.followup_definition_version_key,
    d.created_at,
    d.anchor_key,
    d.anchor_at,
    d.cohort_month,
    d.horizon_days,
    d.horizon_at,
    d.cohort_mature_at,
    d.issue_at_horizon,
    d.is_eligible,
    d.is_mature,
    d.is_cohort_mature,
    d.is_observable,
    d.coverage_start_at,
    d.coverage_end_at,
    d.is_history_complete,
    d.nb_cohort_membership,
    d.denominator_contribution,
    d.open_contribution,
    d.won_contribution,
    d.lost_contribution,
    d.abandoned_contribution,
    d.unqualified_contribution,
    d.unknown_contribution,
    d.sale_type_id,
    d.sale_type_key,
    d.sale_type_version_key,
    d.sale_type_label,
    d.channel_key,
    d.channel_version_key,
    d.channel_label,
    d.channel_candidate_code,
    d.is_channel_calculable,
    d.employee_key,
    d.employee_version_key,
    d.employee_display_name,
    d.team_key,
    d.team_version_key,
    d.team_name,
    d.is_team_calculable,
    d.calculation_status,
    d.status_reason
from {{ ref('dtr_cohort_outcomes') }} as d
inner join {{ ref('int_publication') }} as p
    on d.model_run_id = p.model_run_id
```

**Jointure/publication :** DTR N:1 vers la ligne unique du pointeur, égalité de run ; au bootstrap sans pointeur accepté, zéro ligne. Plus d'une ligne de pointeur est ERROR bloquante. Aucune dépendance inverse DTR→publication. Chaque requête BI conserve model_run_id et vérifie sa cohérence avec dataset_publication_status ; une page ne mélange pas plusieurs runs.

**Contrat BI et filtres :** Mois de création [cohort_from_month,cohort_to_month), observation O, type commercial, équipe et canal calculables, zoom cohorte et horizon30/60/90. Maturité définie AVANT équipe/canal : aucun filtre n'avance la date de maturité. Chaque type commercial conserve sa propre cohorte. Les ratios combinant plusieurs types ne sont publiés que si chaque sous-cohorte sélectionnée est mature ; sinon résultat non mature. Ni seuil ni filtre financier New/Upsell.

**Calculs restants en restitution :** Pour une cohorte/horizon et même définition, Nbase=sum(nb_cohort_membership). Si cohorte mature, Nissue=sum(contribution), taux=Nissue/Nbase lorsque Nbase>0 et admissibilité connue ; sinon NULL. Les parts open/won/lost peuvent totaliser moins de100% : afficher autres et inconnus. La somme de toutes six catégories mature doit égaler Nbase. Jamais sommer Nbase sur30/60/90 ; réutiliser une seule base. Zoom canal : effectifs et même dénominateur de chaque ligne, total recomposé depuis identités/grain compatible. Ils utilisent les champs détaillés, pas des ratios/quantiles locaux déjà agrégés. Les dates/arrondis/libellés/couleurs se formatent dans la BI ; les champsNULL restent indisponibles, jamais zéro d'affichage implicite. Avant agrégation, vérifier disponibilité PAR MESURE dans dataset_publication_status, y compris absence de lignes de détail.

**Test du dataset :** compter et comparer clés/payloads à la DTR sur le seul run publié ; égalité exacte attendue, ERROR sinon. Tester bootstrap vide, bascule vers nouveau run, réexécution sans modification, navigation tenant+clé+run et détection de publication différente entre requêtes. Rejouer les scénarios de filtres et d'agrégation de `dtr_cohort_outcomes`, dont Trois horizons par membre/définition ; cohort_month correspond à création Paris ; horizon local même heure autour passages heure été/hiver ; max maturité invariant sous filtre équipe/canal ; aucune valeur future=>0 ; nurturing ouvert ; abandonné/nonqualifié séparés ; somme des six issues=base mature ; inconnus inclus ; état 1→14 une victoire ; réouverture classée par état à horizon.

**Rafraîchissement/limites :** la vue reflète le pointeur accepté sans horaire propre ; la fraîcheur dépend des sources, du run et de sa publication. Une règle/preuve manquante dans la DTR n'est pas réparée dans cette vue. Les blocages/limites sont ceux de la DTR et du dataset technique de disponibilité. Une relecture d'ancien run passe par la DTR explicite, sans changement du pointeur.


<a id="dtr_opportunity_timeline"></a>

### `dtr_opportunity_timeline`

**Couche/module :** DTR, Trois dashboards — Navigation et investigation. **Finalité :** Durées : cliquer un dossier/passage puis voir passages successifs et changements de responsabilité ; Cohortes : inspecter la séquence à l'horizon ; Synthèse tunnel : investigation des dossiers contribuant à une étape. L'onglet individuel demeure conditionnel, sans classement ni cible personnelle.

**Grain métier :** tenant_id × object_kind × object_key ; une unité logique de période/passage/événement/tranche de responsabilité. **Identité logique :** `record_key=H(tenant_id, object_kind, object_key)`. **Grain historique/physique :** `(model_run_id,record_key)` ; version=H(run,key), une seule contribution par unité dans un run. Les clés métier et de dimensions sont conservées ci-dessous.

**Amont exact :** `{{ ref('fct_opportunity_period') }}`, `{{ ref('fct_stage_visit') }}`, `{{ ref('fct_opportunity_event') }}`, `{{ ref('int_visit_responsibility') }}`, `{{ ref('dim_company') }}`, `{{ ref('dim_stage') }}`, `{{ ref('dim_sale_type') }}`, `{{ ref('dim_employee') }}`, `{{ ref('dim_team') }}`. **Destination :** `dtr_sales.dtr_opportunity_timeline` ; fichier `dbt/models/reporting/dtr/dtr_opportunity_timeline.sql`, YAML `dbt/models/reporting/dtr/_models.yml`.

| Colonne | Type ClickHouse | Nullable | Origine, formule et contraintes |
|---|---|---|---|
| `model_run_id` | `String` | Non | Identifiant de la recomposition complète et immuable ; hérité des entrées du même run. |
| `record_key` | `String` | Non | SHA256 de la liste ordonnée des éléments du grain indiquée dans la fiche ; sérialisation canonique commune, jamais simple concaténation ambiguë. |
| `record_version_key` | `String` | Non | SHA256 de (model_run_id, record_key). |
| `row_hash` | `String` | Non | SHA256 du payload ordonné de la fiche, hors colonnes techniques communes. |
| `calculated_at` | `DateTime64(3, 'UTC')` | Non | Instant de calcul du run ; aucune substitution à une date métier. |
| `rule_version` | `String` | Non | Version immuable des règles et référentiels utilisés par le run. |
| `input_cutoff_at` | `DateTime64(3, 'UTC')` | Non | Borne des entrées figées ; héritée du manifeste de run. |
| `tenant_id` | `String` | Non | Tenant Boond conservé dans les identités et jointures. |
| `opportunity_key` | `String` | Non | Identité stable tenant + opportunité. |
| `opportunity_id` | `Int64` | Non | Identifiant Boond du dossier, pour investigation. |
| `company_key` | `Nullable(String)` | Oui | Identité stable de société résolue au contexte retenu. |
| `company_version_key` | `Nullable(String)` | Oui | Version de société pertinente au contexte retenu. |
| `company_id` | `Nullable(Int64)` | Oui | Identifiant Boond de la société. |
| `company_name` | `Nullable(String)` | Oui | dim_company.company_name par run+company_version_key, N:0..1. |
| `object_kind` | `String` | Non | opportunity_period/stage_visit/opportunity_event/responsibility_slice ; distingue les grains qui ne s'additionnent pas. |
| `object_key` | `String` | Non | period_key,visit_key,event_key ou responsibility_slice_key selon object_kind. |
| `source_model_name` | `String` | Non | Nom parmi les quatre modèles amont, pour lineage ; pas un nom SQL à exécuter dynamiquement. |
| `source_record_version_key` | `String` | Non | Clé de version de la ligne source dans le même run. |
| `visit_key` | `Nullable(String)` | Oui | Passage associé lorsqu'il est établi. |
| `event_type` | `Nullable(String)` | Oui | Type d'événement pour object_kind=opportunity_event ; NULL dans les autres cas. |
| `started_at` | `Nullable(DateTime64(3, 'UTC'))` | Oui | Début de période/passage/tranche ; event_at pour événement ; entrée inconnue reste NULL. |
| `ended_at` | `Nullable(DateTime64(3, 'UTC'))` | Oui | Fin de période/passage/tranche ; NULL pour événement ponctuel ou fin inconnue. |
| `stage_key` | `Nullable(String)` | Oui | Étape de période/passage ; pour événement seulement rôle explicitement défini. |
| `stage_version_key` | `Nullable(String)` | Oui | Version de l'étape dans le contexte de l'unité. |
| `stage_label` | `Nullable(String)` | Oui | Libellé descriptif de l'étape. |
| `from_stage_id` | `Nullable(Int64)` | Oui | Étape quittée d'une transition, si pertinente. |
| `to_stage_id` | `Nullable(Int64)` | Oui | Étape rejointe d'une transition, si pertinente. |
| `is_left_censored` | `Nullable(Bool)` | Oui | Censure du passage, NULL si sans objet. |
| `time_basis` | `Nullable(String)` | Oui | Provenance temporelle de la borne/événement ; prouvée/proxy/inconnue conservée. |
| `slice_duration_seconds` | `Nullable(Float64)` | Oui | int_visit_responsibility.allocated_duration_seconds seulement si allocation validée ; NULL sinon. Jamais durée complète répétée du passage. |
| `slice_duration_days` | `Nullable(Float64)` | Oui | slice_duration_seconds/86400, pour object_kind=responsibility_slice ; NULL sinon. |
| `sale_type_id` | `Nullable(Int64)` | Oui | Type commercial du dossier dans le contexte retenu ; ne désigne pas la composante financière New/Upsell. |
| `sale_type_key` | `Nullable(String)` | Oui | Identité stable du type commercial. |
| `sale_type_version_key` | `Nullable(String)` | Oui | Version de dim_sale_type pertinente. |
| `sale_type_label` | `Nullable(String)` | Oui | dim_sale_type.sale_type_label par run+version, N:0..1. |
| `employee_key` | `Nullable(String)` | Oui | Identité stable du responsable retenu. |
| `employee_version_key` | `Nullable(String)` | Oui | Version descriptive du responsable. |
| `employee_display_name` | `Nullable(String)` | Oui | dim_employee.employee_display_name par run+version, N:0..1. |
| `team_key` | `Nullable(String)` | Oui | Équipe historiquement retenue si mapping et attribution validés. |
| `team_version_key` | `Nullable(String)` | Oui | Version de l'équipe pertinente. |
| `team_name` | `Nullable(String)` | Oui | dim_team.team_name par run+version, N:0..1. |
| `is_team_calculable` | `Bool` | Non | false pour rattachement à entrée/événement inconnu ou ambigu ; sinon true y compris KAM connue, indépendamment de son absence de cible D23. |
| `calculation_status` | `String` | Non | ready/partial/blocked/not_applicable ; ready n'efface pas les réserves distinctes de couverture. |
| `status_reason` | `Nullable(String)` | Oui | Motif explicite, stable et documenté ; plusieurs motifs séparés de façon canonique si nécessaire. |

**Jointures, identités et cardinalités :** UNION ALL de quatre projections à colonnes identiques : aucune jointure des quatre faits entre eux. Les lignes d'un même run sont préservées ; leurs record_key propres sont typés par object_kind. Dimensions descriptives N:0..1 par run+version. Les tranches int_visit_responsibility portent leurs propres clés et bornes finales. Une clé de passage dans une ligne ne multiplie jamais la chronologie via un JOIN de tous ses événements. Pour la projection responsabilité seulement, LEFT JOIN de la tranche au fct_stage_visit par run+tenant+visit_key N:0..1 fournit opportunity_id/company/type ; aucune jointure sur le seul dossier. Le role stage estNULL pour événement sans choix explicite, avec from_stage_id/to_stage_id conservés. slice_duration_seconds reprend allocated_duration_seconds uniquement si allocation_status validé ; sinon NULL, observed_slice_duration_seconds reste un détail de preuve dans int.

**Étapes du calcul :** Projection commune à vocation explicative. Trier dans la BI par coalesce(started_at,première observation connue), object_kind puis object_key ; afficher explicitement 'début inconnu' lorsque started_at=NULL. Le coalesce de tri n'est ni une date métier exposée ni une durée. Les événements ponctuels ont ended_at=NULL et gardent leur nature. Pas de KPI global calculé sur l'union.

**Filtrage, paramètres et agrégation :** Navigation obligatoire par tenant+opportunity_key depuis liste ou cohorte. Publication/model_run_id épinglé sur la navigation pour cohérence de lecture. Observation O filtre uniquement les unités pertinentes au détail : événements<=O, intervalles ayant commencé avant O ou unités censurées explicitement signalées ; ne pas dévoiler les transitions futures comme connues à O. Bornes de recherche optionnelles ; filtres type/équipe ne doivent pas supprimer silencieusement des segments du dossier investigué. Aucune mesure multigrain à sommer et aucun 'nombre de dossiers' calculé par count(*) sur cette timeline. Les durées de tranches peuvent être regroupées seulement entre tranches compatibles après convention d'allocation validée. La navigation permet de revenir aux datasets de grain homogène pour leurs KPI.

**Matérialisation/histoire :** appliquer le contrat DTR commun ci-dessus : résultats complets du run, incremental append, engine MergeTree, ORDER BY(model_run_id,record_key), unique_key record_version_key, on_schema_change fail, full_refresh false et pas inserts_only. Les tables DTR conservent les anciens runs ; aucun filtre max de date métier ou limite à hier. Au premier chargement/cible vide, calculer l'ensemble ; en reprise, conserver seulement les clés du candidat absentes de la cible, sans modifier un payload existant.

**Contrat de chargement dbt :** une requête SELECT, CTE candidates explicite issue des transformations décrites. Chaque colonne du dictionnaire est produite exactement une fois. Terminer par la projection explicite de candidates ; sous `{% if is_incremental() %}`, LEFT ANTI JOIN de `{{ this }}` sur model_run_id et record_key. Tester absence de deux payloads différents pour une même clé/run AVANT chargement. Le unique_key de configuration assure le chemin de contrôle de schéma de l'adaptateur, pas la déduplication. Les entrées du run et le cutoff sont figés avant toute écriture future ; reprise du même run à empreinte inchangée.

**Construction/rafraîchissement :** après tous amonts du même run ; branches indépendantes parallélisables selon DAG. Exécution manuelle D29 ; fraîcheur de capture/publication déclarée, calcul puis tests/digest et publication contrôlée. Les requêtes de contrôle avant publication utilisent test_model_run_id. Aucun service/modèle n'est créé par la présente fiche.

**Tests/acceptation :** Chaque paire object_kind/object_key unique dans le run ; nombre de lignes union= somme des quatre projections, sans multiplicateur ; bornes/identifiants conservés ; unités de responsabilité ne dupliquent pas une durée complète ; filtre de navigation inclut tenant et publication ; transitions postérieures à O identifiables et exclues de la lecture à O. Contrôles communs ERROR de grain, hash, cardinalité et run ; WARN/indisponibilité pour manque descriptif ou preuve comme décrit dans le contrat. Tests métier ci-dessus planifiés, pas exécutés sur une implémentation inexistante.


<a id="dataset_opportunity_timeline"></a>

### `dataset_opportunity_timeline`

**Couche/module :** dataset de restitution, Trois dashboards — Navigation et investigation. **Finalité/consommateurs :** Durées : cliquer un dossier/passage puis voir passages successifs et changements de responsabilité ; Cohortes : inspecter la séquence à l'horizon ; Synthèse tunnel : investigation des dossiers contribuant à une étape. L'onglet individuel demeure conditionnel, sans classement ni cible personnelle.

**Grain métier et version :** exactement celui de `dtr_opportunity_timeline` : tenant_id × object_kind × object_key ; une unité logique de période/passage/événement/tranche de responsabilité. Une seule publication est visible ; identité et version sont conservées sans recalcul. Aucun total ni ligne artificielle n'est ajouté.

**Amont exact :** `{{ ref('dtr_opportunity_timeline') }}` et `{{ ref('int_publication') }}`. **Destination :** `dtr_sales.dataset_opportunity_timeline` ; fichier `dbt/models/reporting/datasets/dataset_opportunity_timeline.sql`, YAML `dbt/models/reporting/datasets/_models.yml`.

| Colonne | Type ClickHouse | Nullable | Origine, formule et contraintes |
|---|---|---|---|
| `model_run_id` | `String` | Non | Projection sans changement de dtr_opportunity_timeline.model_run_id. Identifiant de la recomposition complète et immuable ; hérité des entrées du même run. |
| `record_key` | `String` | Non | Projection sans changement de dtr_opportunity_timeline.record_key. SHA256 de la liste ordonnée des éléments du grain indiquée dans la fiche ; sérialisation canonique commune, jamais simple concaténation ambiguë. |
| `record_version_key` | `String` | Non | Projection sans changement de dtr_opportunity_timeline.record_version_key. SHA256 de (model_run_id, record_key). |
| `row_hash` | `String` | Non | Projection sans changement de dtr_opportunity_timeline.row_hash. SHA256 du payload ordonné de la fiche, hors colonnes techniques communes. |
| `calculated_at` | `DateTime64(3, 'UTC')` | Non | Projection sans changement de dtr_opportunity_timeline.calculated_at. Instant de calcul du run ; aucune substitution à une date métier. |
| `rule_version` | `String` | Non | Projection sans changement de dtr_opportunity_timeline.rule_version. Version immuable des règles et référentiels utilisés par le run. |
| `input_cutoff_at` | `DateTime64(3, 'UTC')` | Non | Projection sans changement de dtr_opportunity_timeline.input_cutoff_at. Borne des entrées figées ; héritée du manifeste de run. |
| `tenant_id` | `String` | Non | Projection sans changement de dtr_opportunity_timeline.tenant_id. Tenant Boond conservé dans les identités et jointures. |
| `opportunity_key` | `String` | Non | Projection sans changement de dtr_opportunity_timeline.opportunity_key. Identité stable tenant + opportunité. |
| `opportunity_id` | `Int64` | Non | Projection sans changement de dtr_opportunity_timeline.opportunity_id. Identifiant Boond du dossier, pour investigation. |
| `company_key` | `Nullable(String)` | Oui | Projection sans changement de dtr_opportunity_timeline.company_key. Identité stable de société résolue au contexte retenu. |
| `company_version_key` | `Nullable(String)` | Oui | Projection sans changement de dtr_opportunity_timeline.company_version_key. Version de société pertinente au contexte retenu. |
| `company_id` | `Nullable(Int64)` | Oui | Projection sans changement de dtr_opportunity_timeline.company_id. Identifiant Boond de la société. |
| `company_name` | `Nullable(String)` | Oui | Projection sans changement de dtr_opportunity_timeline.company_name. dim_company.company_name par run+company_version_key, N:0..1. |
| `object_kind` | `String` | Non | Projection sans changement de dtr_opportunity_timeline.object_kind. opportunity_period/stage_visit/opportunity_event/responsibility_slice ; distingue les grains qui ne s'additionnent pas. |
| `object_key` | `String` | Non | Projection sans changement de dtr_opportunity_timeline.object_key. period_key,visit_key,event_key ou responsibility_slice_key selon object_kind. |
| `source_model_name` | `String` | Non | Projection sans changement de dtr_opportunity_timeline.source_model_name. Nom parmi les quatre modèles amont, pour lineage ; pas un nom SQL à exécuter dynamiquement. |
| `source_record_version_key` | `String` | Non | Projection sans changement de dtr_opportunity_timeline.source_record_version_key. Clé de version de la ligne source dans le même run. |
| `visit_key` | `Nullable(String)` | Oui | Projection sans changement de dtr_opportunity_timeline.visit_key. Passage associé lorsqu'il est établi. |
| `event_type` | `Nullable(String)` | Oui | Projection sans changement de dtr_opportunity_timeline.event_type. Type d'événement pour object_kind=opportunity_event ; NULL dans les autres cas. |
| `started_at` | `Nullable(DateTime64(3, 'UTC'))` | Oui | Projection sans changement de dtr_opportunity_timeline.started_at. Début de période/passage/tranche ; event_at pour événement ; entrée inconnue reste NULL. |
| `ended_at` | `Nullable(DateTime64(3, 'UTC'))` | Oui | Projection sans changement de dtr_opportunity_timeline.ended_at. Fin de période/passage/tranche ; NULL pour événement ponctuel ou fin inconnue. |
| `stage_key` | `Nullable(String)` | Oui | Projection sans changement de dtr_opportunity_timeline.stage_key. Étape de période/passage ; pour événement seulement rôle explicitement défini. |
| `stage_version_key` | `Nullable(String)` | Oui | Projection sans changement de dtr_opportunity_timeline.stage_version_key. Version de l'étape dans le contexte de l'unité. |
| `stage_label` | `Nullable(String)` | Oui | Projection sans changement de dtr_opportunity_timeline.stage_label. Libellé descriptif de l'étape. |
| `from_stage_id` | `Nullable(Int64)` | Oui | Projection sans changement de dtr_opportunity_timeline.from_stage_id. Étape quittée d'une transition, si pertinente. |
| `to_stage_id` | `Nullable(Int64)` | Oui | Projection sans changement de dtr_opportunity_timeline.to_stage_id. Étape rejointe d'une transition, si pertinente. |
| `is_left_censored` | `Nullable(Bool)` | Oui | Projection sans changement de dtr_opportunity_timeline.is_left_censored. Censure du passage, NULL si sans objet. |
| `time_basis` | `Nullable(String)` | Oui | Projection sans changement de dtr_opportunity_timeline.time_basis. Provenance temporelle de la borne/événement ; prouvée/proxy/inconnue conservée. |
| `slice_duration_seconds` | `Nullable(Float64)` | Oui | Projection sans changement de dtr_opportunity_timeline.slice_duration_seconds. int_visit_responsibility.allocated_duration_seconds seulement si allocation validée ; NULL sinon. Jamais durée complète répétée du passage. |
| `slice_duration_days` | `Nullable(Float64)` | Oui | Projection sans changement de dtr_opportunity_timeline.slice_duration_days. slice_duration_seconds/86400, pour object_kind=responsibility_slice ; NULL sinon. |
| `sale_type_id` | `Nullable(Int64)` | Oui | Projection sans changement de dtr_opportunity_timeline.sale_type_id. Type commercial du dossier dans le contexte retenu ; ne désigne pas la composante financière New/Upsell. |
| `sale_type_key` | `Nullable(String)` | Oui | Projection sans changement de dtr_opportunity_timeline.sale_type_key. Identité stable du type commercial. |
| `sale_type_version_key` | `Nullable(String)` | Oui | Projection sans changement de dtr_opportunity_timeline.sale_type_version_key. Version de dim_sale_type pertinente. |
| `sale_type_label` | `Nullable(String)` | Oui | Projection sans changement de dtr_opportunity_timeline.sale_type_label. dim_sale_type.sale_type_label par run+version, N:0..1. |
| `employee_key` | `Nullable(String)` | Oui | Projection sans changement de dtr_opportunity_timeline.employee_key. Identité stable du responsable retenu. |
| `employee_version_key` | `Nullable(String)` | Oui | Projection sans changement de dtr_opportunity_timeline.employee_version_key. Version descriptive du responsable. |
| `employee_display_name` | `Nullable(String)` | Oui | Projection sans changement de dtr_opportunity_timeline.employee_display_name. dim_employee.employee_display_name par run+version, N:0..1. |
| `team_key` | `Nullable(String)` | Oui | Projection sans changement de dtr_opportunity_timeline.team_key. Équipe historiquement retenue si mapping et attribution validés. |
| `team_version_key` | `Nullable(String)` | Oui | Projection sans changement de dtr_opportunity_timeline.team_version_key. Version de l'équipe pertinente. |
| `team_name` | `Nullable(String)` | Oui | Projection sans changement de dtr_opportunity_timeline.team_name. dim_team.team_name par run+version, N:0..1. |
| `is_team_calculable` | `Bool` | Non | Projection sans changement de dtr_opportunity_timeline.is_team_calculable. false pour rattachement à entrée/événement inconnu ou ambigu ; sinon true y compris KAM connue, indépendamment de son absence de cible D23. |
| `calculation_status` | `String` | Non | Projection sans changement de dtr_opportunity_timeline.calculation_status. ready/partial/blocked/not_applicable ; ready n'efface pas les réserves distinctes de couverture. |
| `status_reason` | `Nullable(String)` | Oui | Projection sans changement de dtr_opportunity_timeline.status_reason. Motif explicite, stable et documenté ; plusieurs motifs séparés de façon canonique si nécessaire. |

**SQL de projection complet :**

```sql
{{ config(materialized='view', schema='dtr_sales') }}

select
    d.model_run_id,
    d.record_key,
    d.record_version_key,
    d.row_hash,
    d.calculated_at,
    d.rule_version,
    d.input_cutoff_at,
    d.tenant_id,
    d.opportunity_key,
    d.opportunity_id,
    d.company_key,
    d.company_version_key,
    d.company_id,
    d.company_name,
    d.object_kind,
    d.object_key,
    d.source_model_name,
    d.source_record_version_key,
    d.visit_key,
    d.event_type,
    d.started_at,
    d.ended_at,
    d.stage_key,
    d.stage_version_key,
    d.stage_label,
    d.from_stage_id,
    d.to_stage_id,
    d.is_left_censored,
    d.time_basis,
    d.slice_duration_seconds,
    d.slice_duration_days,
    d.sale_type_id,
    d.sale_type_key,
    d.sale_type_version_key,
    d.sale_type_label,
    d.employee_key,
    d.employee_version_key,
    d.employee_display_name,
    d.team_key,
    d.team_version_key,
    d.team_name,
    d.is_team_calculable,
    d.calculation_status,
    d.status_reason
from {{ ref('dtr_opportunity_timeline') }} as d
inner join {{ ref('int_publication') }} as p
    on d.model_run_id = p.model_run_id
```

**Jointure/publication :** DTR N:1 vers la ligne unique du pointeur, égalité de run ; au bootstrap sans pointeur accepté, zéro ligne. Plus d'une ligne de pointeur est ERROR bloquante. Aucune dépendance inverse DTR→publication. Chaque requête BI conserve model_run_id et vérifie sa cohérence avec dataset_publication_status ; une page ne mélange pas plusieurs runs.

**Contrat BI et filtres :** Navigation obligatoire par tenant+opportunity_key depuis liste ou cohorte. Publication/model_run_id épinglé sur la navigation pour cohérence de lecture. Observation O filtre uniquement les unités pertinentes au détail : événements<=O, intervalles ayant commencé avant O ou unités censurées explicitement signalées ; ne pas dévoiler les transitions futures comme connues à O. Bornes de recherche optionnelles ; filtres type/équipe ne doivent pas supprimer silencieusement des segments du dossier investigué.

**Calculs restants en restitution :** Aucune mesure multigrain à sommer et aucun 'nombre de dossiers' calculé par count(*) sur cette timeline. Les durées de tranches peuvent être regroupées seulement entre tranches compatibles après convention d'allocation validée. La navigation permet de revenir aux datasets de grain homogène pour leurs KPI. Ils utilisent les champs détaillés, pas des ratios/quantiles locaux déjà agrégés. Les dates/arrondis/libellés/couleurs se formatent dans la BI ; les champsNULL restent indisponibles, jamais zéro d'affichage implicite. Avant agrégation, vérifier disponibilité PAR MESURE dans dataset_publication_status, y compris absence de lignes de détail.

**Test du dataset :** compter et comparer clés/payloads à la DTR sur le seul run publié ; égalité exacte attendue, ERROR sinon. Tester bootstrap vide, bascule vers nouveau run, réexécution sans modification, navigation tenant+clé+run et détection de publication différente entre requêtes. Rejouer les scénarios de filtres et d'agrégation de `dtr_opportunity_timeline`, dont Chaque paire object_kind/object_key unique dans le run ; nombre de lignes union= somme des quatre projections, sans multiplicateur ; bornes/identifiants conservés ; unités de responsabilité ne dupliquent pas une durée complète ; filtre de navigation inclut tenant et publication ; transitions postérieures à O identifiables et exclues de la lecture à O.

**Rafraîchissement/limites :** la vue reflète le pointeur accepté sans horaire propre ; la fraîcheur dépend des sources, du run et de sa publication. Une règle/preuve manquante dans la DTR n'est pas réparée dans cette vue. Les blocages/limites sont ceux de la DTR et du dataset technique de disponibilité. Une relecture d'ancien run passe par la DTR explicite, sans changement du pointeur.


<a id="dtr_pipeline_periods"></a>

### `dtr_pipeline_periods`

**Couche/module :** DTR, Reste du catalogue — pipeline à date et historique. **Finalité :** Hors trois PNG : pipeline ouvert et pondéré, répartition/canaux, évolution historique, coverage, stagnation et stock sociétés In demo. Préserve détail pour filtres futurs sans figer une agrégation mensuelle.

**Grain métier :** tenant_id × period_key ; intervalle analytique stable d'une opportunité. **Identité logique :** `record_key=H(tenant_id, period_key)`. **Grain historique/physique :** `(model_run_id,record_key)` ; version=H(run,key), une seule contribution par unité dans un run. Les clés métier et de dimensions sont conservées ci-dessous.

**Amont exact :** `{{ ref('fct_opportunity_period') }}`, `{{ ref('dim_company') }}`, `{{ ref('dim_stage') }}`, `{{ ref('dim_sale_type') }}`, `{{ ref('dim_channel') }}`, `{{ ref('dim_employee') }}`, `{{ ref('dim_team') }}`. **Destination :** `dtr_sales.dtr_pipeline_periods` ; fichier `dbt/models/reporting/dtr/dtr_pipeline_periods.sql`, YAML `dbt/models/reporting/dtr/_models.yml`.

| Colonne | Type ClickHouse | Nullable | Origine, formule et contraintes |
|---|---|---|---|
| `model_run_id` | `String` | Non | Identifiant de la recomposition complète et immuable ; hérité des entrées du même run. |
| `record_key` | `String` | Non | SHA256 de la liste ordonnée des éléments du grain indiquée dans la fiche ; sérialisation canonique commune, jamais simple concaténation ambiguë. |
| `record_version_key` | `String` | Non | SHA256 de (model_run_id, record_key). |
| `row_hash` | `String` | Non | SHA256 du payload ordonné de la fiche, hors colonnes techniques communes. |
| `calculated_at` | `DateTime64(3, 'UTC')` | Non | Instant de calcul du run ; aucune substitution à une date métier. |
| `rule_version` | `String` | Non | Version immuable des règles et référentiels utilisés par le run. |
| `input_cutoff_at` | `DateTime64(3, 'UTC')` | Non | Borne des entrées figées ; héritée du manifeste de run. |
| `tenant_id` | `String` | Non | Tenant Boond conservé dans les identités et jointures. |
| `opportunity_key` | `String` | Non | Identité stable tenant + opportunité. |
| `opportunity_id` | `Int64` | Non | Identifiant Boond du dossier, pour investigation. |
| `company_key` | `Nullable(String)` | Oui | Identité stable de société résolue au contexte retenu. |
| `company_version_key` | `Nullable(String)` | Oui | Version de société pertinente au contexte retenu. |
| `company_id` | `Nullable(Int64)` | Oui | Identifiant Boond de la société. |
| `company_name` | `Nullable(String)` | Oui | dim_company.company_name par run+company_version_key, N:0..1. |
| `period_key` | `String` | Non | Clé logique de période préparée dans le fait. |
| `visit_key` | `Nullable(String)` | Oui | Passage continu associé si observable ; plusieurs périodes peuvent partager un passage. |
| `valid_from_at` | `DateTime64(3, 'UTC')` | Non | Début inclus de période analytique observable. |
| `valid_to_at` | `Nullable(DateTime64(3, 'UTC'))` | Oui | Fin exclue ; NULL pour période ouverte, sous couverture déclarée. |
| `created_at` | `Nullable(DateTime64(3, 'UTC'))` | Oui | Création métier Boond ; pas meta.ts par défaut. |
| `stage_id` | `Nullable(Int64)` | Oui | Étape dans l'intervalle. |
| `stage_key` | `Nullable(String)` | Oui | Identité d'étape. |
| `stage_version_key` | `Nullable(String)` | Oui | Version de l'étape valide dans tout l'intervalle. |
| `stage_label` | `Nullable(String)` | Oui | dim_stage.stage_label. |
| `is_open` | `Nullable(Bool)` | Oui | Population ouverte définie par le mapping d'issues ; nurturing ouvert, abandonné/nonqualifié distincts. |
| `is_demo_stage` | `Nullable(Bool)` | Oui | Pour tenant demo_crm, paramètre case_rules.demo_stage_ids=[24]. Q11(document 03) vérifie code24 Show Boond dans les versions fr du 2025-03-10 09:00:00 UTC et du 2025-12-08 10:00:00 UTC. is_demo_stage=true seulement si stage_id=24 ET version dim_stage contenant ce mapping valide à l'instant de la période/observation ; avant première preuve de mapping ou sans version pertinente=>NULL+missing_stage_rule, jamais rétroprojection. Ce code ne définit ni ordre obligatoire ni règle d'un autre tenant. |
| `stage_entered_at` | `Nullable(DateTime64(3, 'UTC'))` | Oui | Entrée du passage courant, inchangée sur modification de contexte. |
| `expected_close_at` | `Nullable(DateTime64(3, 'UTC'))` | Oui | Date de closing prévue dans la version pertinente ; pas date de signature. |
| `pipeline_amount` | `Nullable(Decimal(38,4))` | Oui | Montant candidat du fait, à conserver sans qualifier automatiquement de MRR. |
| `amount_basis` | `Nullable(String)` | Oui | Nature/unité du montant ; NULL tant qu'elle n'est pas validée. |
| `currency_code` | `Nullable(String)` | Oui | EUR par hypothèse explicite du case D20 ; cette devise ne prouve ni mensualité ni engagement du montant commercial. |
| `signature_probability` | `Nullable(Decimal(18,8))` | Oui | Probabilité de signature finale si source, segment, dates et type validés. |
| `weighted_pipeline_amount` | `Nullable(Decimal(38,4))` | Oui | Montant × probabilité avec précision commune, seulement si montant et coefficient admissibles. |
| `is_amount_calculable` | `Bool` | Non | true seulement si pipeline_amount, nature/unité et devise prouvées ET statut spécifique de mesure disponible ; false sinon. Un montant candidat non NULL seul ne suffit pas. |
| `is_probability_calculable` | `Bool` | Non | true si signature_probability est non NULL et probability_rule validée pour étape/segment/type/période ; false sinon. |
| `is_left_censored` | `Bool` | Non | stage_entered_at IS NULL et stage_first_observed_at connu ; début exact absent, sans remplacer par première observation. |
| `coverage_start_at` | `Nullable(DateTime64(3, 'UTC'))` | Oui | Borne basse de couverture utile. |
| `coverage_end_at` | `Nullable(DateTime64(3, 'UTC'))` | Oui | Borne haute de couverture connue. |
| `is_history_complete` | `Nullable(Bool)` | Oui | Contrôle de couverture déclaré. |
| `sale_type_id` | `Nullable(Int64)` | Oui | Type commercial du dossier dans le contexte retenu ; ne désigne pas la composante financière New/Upsell. |
| `sale_type_key` | `Nullable(String)` | Oui | Identité stable du type commercial. |
| `sale_type_version_key` | `Nullable(String)` | Oui | Version de dim_sale_type pertinente. |
| `sale_type_label` | `Nullable(String)` | Oui | dim_sale_type.sale_type_label par run+version, N:0..1. |
| `channel_key` | `Nullable(String)` | Oui | Alias explicite de acquisition_channel_key du fait ; canal officiel d'entrée, NULL avant règle validée. |
| `channel_version_key` | `Nullable(String)` | Oui | Version de mapping du canal, indépendante des sources candidates conservées. |
| `channel_label` | `Nullable(String)` | Oui | dim_channel.channel_label par run+version, N:0..1. |
| `channel_candidate_code` | `Nullable(String)` | Oui | Valeur candidate Boond conservée sans la transformer en canal officiel. |
| `is_channel_calculable` | `Bool` | Non | false si origine à création ou mapping de valeur est manquant ; règle D24 définie, filtre disponible sur les lignes résolues. |
| `employee_key` | `Nullable(String)` | Oui | Identité stable du responsable retenu. |
| `employee_version_key` | `Nullable(String)` | Oui | Version descriptive du responsable. |
| `employee_display_name` | `Nullable(String)` | Oui | dim_employee.employee_display_name par run+version, N:0..1. |
| `team_key` | `Nullable(String)` | Oui | Équipe historiquement retenue si mapping et attribution validés. |
| `team_version_key` | `Nullable(String)` | Oui | Version de l'équipe pertinente. |
| `team_name` | `Nullable(String)` | Oui | dim_team.team_name par run+version, N:0..1. |
| `is_team_calculable` | `Bool` | Non | false pour rattachement à entrée/événement inconnu ou ambigu ; sinon true y compris KAM connue, indépendamment de son absence de cible D23. |
| `calculation_status` | `String` | Non | ready/partial/blocked/not_applicable ; ready n'efface pas les réserves distinctes de couverture. |
| `status_reason` | `Nullable(String)` | Oui | Motif explicite, stable et documenté ; plusieurs motifs séparés de façon canonique si nécessaire. |

**Jointures, identités et cardinalités :** Fait → dimensions N:0..1 sur run+versionkey ; conserver toutes lignes de fait par LEFT JOIN. Aucune jointure de détail avec événements/actions/abonnements. Le fait est déjà découpé aux bornes nécessaires des dimensions ; ne pas réintroduire leur historique complet par identité seule.

**Étapes du calcul :** Projection enrichie des périodes. Observation O admissible : valid_from_at <=O et (valid_to_at>O ou NULL), avec couverture source suffisante. Une seule période par opportunité à O. Les mesures officielles financières restent NULL/non calculables si la nature monétaire et les coefficients manquent ; les montants candidats peuvent apparaître dans une colonne clairement libellée candidate. L'âge du stage se calcule depuis stage_entered_at, pas depuis valid_from_at.

**Filtrage, paramètres et agrégation :** Observation O ; période de série sous forme de liste explicite d'observations (jour/semaine/mois si choisie), type, équipe et canal lorsqu'ils sont calculables. Pour la couverture d'objectif, mois de closing prévu séparé du mois observé. Seuil de stagnation optionnel fourni explicitement ; pas d'alerte si absent. Cohorte=mois de created_at en Paris si demandée. À O, compter opportunity_key au grain résolu, sommer montants comparables, recalculer parts de canal depuis effectifs de la même population. Nb In demo=nombre distinct company_key ayant au moins une période ouverte admissible en étape Démo ; identités société inconnues dans couverture distincte, jamais comptées comme une seule société fictive. Série historique : une mesure par date, pas somme des stocks. Couverture=montant ouvert à closing prévu dans le mois / cible compatible explicitement choisie, sinon NULL+missing_coverage_definition.

**Matérialisation/histoire :** appliquer le contrat DTR commun ci-dessus : résultats complets du run, incremental append, engine MergeTree, ORDER BY(model_run_id,record_key), unique_key record_version_key, on_schema_change fail, full_refresh false et pas inserts_only. Les tables DTR conservent les anciens runs ; aucun filtre max de date métier ou limite à hier. Au premier chargement/cible vide, calculer l'ensemble ; en reprise, conserver seulement les clés du candidat absentes de la cible, sans modifier un payload existant.

**Contrat de chargement dbt :** une requête SELECT, CTE candidates explicite issue des transformations décrites. Chaque colonne du dictionnaire est produite exactement une fois. Terminer par la projection explicite de candidates ; sous `{% if is_incremental() %}`, LEFT ANTI JOIN de `{{ this }}` sur model_run_id et record_key. Tester absence de deux payloads différents pour une même clé/run AVANT chargement. Le unique_key de configuration assure le chemin de contrôle de schéma de l'adaptateur, pas la déduplication. Les entrées du run et le cutoff sont figés avant toute écriture future ; reprise du même run à empreinte inchangée.

**Construction/rafraîchissement :** après tous amonts du même run ; branches indépendantes parallélisables selon DAG. Exécution manuelle D29 ; fraîcheur de capture/publication déclarée, calcul puis tests/digest et publication contrôlée. Les requêtes de contrôle avant publication utilisent test_model_run_id. Aucun service/modèle n'est créé par la présente fiche.

**Tests/acceptation :** Périodes sans chevauchement par opportunité/run ; exactement0/1 ligne à O ; entrée du stage identique sur transfert ; société avec2 dossiers Démo=>1 ; global sociétés recalculé après filtre ; montant inconnu non zéro ; seuil absent aucune classification officielle ; stocks non sommés entre dates. Contrôles communs ERROR de grain, hash, cardinalité et run ; WARN/indisponibilité pour manque descriptif ou preuve comme décrit dans le contrat. Tests métier ci-dessus planifiés, pas exécutés sur une implémentation inexistante.


<a id="dataset_pipeline_periods"></a>

### `dataset_pipeline_periods`

**Couche/module :** dataset de restitution, Reste du catalogue — pipeline à date et historique. **Finalité/consommateurs :** Hors trois PNG : pipeline ouvert et pondéré, répartition/canaux, évolution historique, coverage, stagnation et stock sociétés In demo. Préserve détail pour filtres futurs sans figer une agrégation mensuelle.

**Grain métier et version :** exactement celui de `dtr_pipeline_periods` : tenant_id × period_key ; intervalle analytique stable d'une opportunité. Une seule publication est visible ; identité et version sont conservées sans recalcul. Aucun total ni ligne artificielle n'est ajouté.

**Amont exact :** `{{ ref('dtr_pipeline_periods') }}` et `{{ ref('int_publication') }}`. **Destination :** `dtr_sales.dataset_pipeline_periods` ; fichier `dbt/models/reporting/datasets/dataset_pipeline_periods.sql`, YAML `dbt/models/reporting/datasets/_models.yml`.

| Colonne | Type ClickHouse | Nullable | Origine, formule et contraintes |
|---|---|---|---|
| `model_run_id` | `String` | Non | Projection sans changement de dtr_pipeline_periods.model_run_id. Identifiant de la recomposition complète et immuable ; hérité des entrées du même run. |
| `record_key` | `String` | Non | Projection sans changement de dtr_pipeline_periods.record_key. SHA256 de la liste ordonnée des éléments du grain indiquée dans la fiche ; sérialisation canonique commune, jamais simple concaténation ambiguë. |
| `record_version_key` | `String` | Non | Projection sans changement de dtr_pipeline_periods.record_version_key. SHA256 de (model_run_id, record_key). |
| `row_hash` | `String` | Non | Projection sans changement de dtr_pipeline_periods.row_hash. SHA256 du payload ordonné de la fiche, hors colonnes techniques communes. |
| `calculated_at` | `DateTime64(3, 'UTC')` | Non | Projection sans changement de dtr_pipeline_periods.calculated_at. Instant de calcul du run ; aucune substitution à une date métier. |
| `rule_version` | `String` | Non | Projection sans changement de dtr_pipeline_periods.rule_version. Version immuable des règles et référentiels utilisés par le run. |
| `input_cutoff_at` | `DateTime64(3, 'UTC')` | Non | Projection sans changement de dtr_pipeline_periods.input_cutoff_at. Borne des entrées figées ; héritée du manifeste de run. |
| `tenant_id` | `String` | Non | Projection sans changement de dtr_pipeline_periods.tenant_id. Tenant Boond conservé dans les identités et jointures. |
| `opportunity_key` | `String` | Non | Projection sans changement de dtr_pipeline_periods.opportunity_key. Identité stable tenant + opportunité. |
| `opportunity_id` | `Int64` | Non | Projection sans changement de dtr_pipeline_periods.opportunity_id. Identifiant Boond du dossier, pour investigation. |
| `company_key` | `Nullable(String)` | Oui | Projection sans changement de dtr_pipeline_periods.company_key. Identité stable de société résolue au contexte retenu. |
| `company_version_key` | `Nullable(String)` | Oui | Projection sans changement de dtr_pipeline_periods.company_version_key. Version de société pertinente au contexte retenu. |
| `company_id` | `Nullable(Int64)` | Oui | Projection sans changement de dtr_pipeline_periods.company_id. Identifiant Boond de la société. |
| `company_name` | `Nullable(String)` | Oui | Projection sans changement de dtr_pipeline_periods.company_name. dim_company.company_name par run+company_version_key, N:0..1. |
| `period_key` | `String` | Non | Projection sans changement de dtr_pipeline_periods.period_key. Clé logique de période préparée dans le fait. |
| `visit_key` | `Nullable(String)` | Oui | Projection sans changement de dtr_pipeline_periods.visit_key. Passage continu associé si observable ; plusieurs périodes peuvent partager un passage. |
| `valid_from_at` | `DateTime64(3, 'UTC')` | Non | Projection sans changement de dtr_pipeline_periods.valid_from_at. Début inclus de période analytique observable. |
| `valid_to_at` | `Nullable(DateTime64(3, 'UTC'))` | Oui | Projection sans changement de dtr_pipeline_periods.valid_to_at. Fin exclue ; NULL pour période ouverte, sous couverture déclarée. |
| `created_at` | `Nullable(DateTime64(3, 'UTC'))` | Oui | Projection sans changement de dtr_pipeline_periods.created_at. Création métier Boond ; pas meta.ts par défaut. |
| `stage_id` | `Nullable(Int64)` | Oui | Projection sans changement de dtr_pipeline_periods.stage_id. Étape dans l'intervalle. |
| `stage_key` | `Nullable(String)` | Oui | Projection sans changement de dtr_pipeline_periods.stage_key. Identité d'étape. |
| `stage_version_key` | `Nullable(String)` | Oui | Projection sans changement de dtr_pipeline_periods.stage_version_key. Version de l'étape valide dans tout l'intervalle. |
| `stage_label` | `Nullable(String)` | Oui | Projection sans changement de dtr_pipeline_periods.stage_label. dim_stage.stage_label. |
| `is_open` | `Nullable(Bool)` | Oui | Projection sans changement de dtr_pipeline_periods.is_open. Population ouverte définie par le mapping d'issues ; nurturing ouvert, abandonné/nonqualifié distincts. |
| `is_demo_stage` | `Nullable(Bool)` | Oui | Projection sans changement de dtr_pipeline_periods.is_demo_stage. Pour tenant demo_crm, paramètre case_rules.demo_stage_ids=[24]. Q11(document 03) vérifie code24 Show Boond dans les versions fr du 2025-03-10 09:00:00 UTC et du 2025-12-08 10:00:00 UTC. is_demo_stage=true seulement si stage_id=24 ET version dim_stage contenant ce mapping valide à l'instant de la période/observation ; avant première preuve de mapping ou sans version pertinente=>NULL+missing_stage_rule, jamais rétroprojection. Ce code ne définit ni ordre obligatoire ni règle d'un autre tenant. |
| `stage_entered_at` | `Nullable(DateTime64(3, 'UTC'))` | Oui | Projection sans changement de dtr_pipeline_periods.stage_entered_at. Entrée du passage courant, inchangée sur modification de contexte. |
| `expected_close_at` | `Nullable(DateTime64(3, 'UTC'))` | Oui | Projection sans changement de dtr_pipeline_periods.expected_close_at. Date de closing prévue dans la version pertinente ; pas date de signature. |
| `pipeline_amount` | `Nullable(Decimal(38,4))` | Oui | Projection sans changement de dtr_pipeline_periods.pipeline_amount. Montant candidat du fait, à conserver sans qualifier automatiquement de MRR. |
| `amount_basis` | `Nullable(String)` | Oui | Projection sans changement de dtr_pipeline_periods.amount_basis. Nature/unité du montant ; NULL tant qu'elle n'est pas validée. |
| `currency_code` | `Nullable(String)` | Oui | Projection sans changement de dtr_pipeline_periods.currency_code. EUR par hypothèse explicite du case D20 ; cette devise ne prouve ni mensualité ni engagement du montant commercial. |
| `signature_probability` | `Nullable(Decimal(18,8))` | Oui | Projection sans changement de dtr_pipeline_periods.signature_probability. Probabilité de signature finale si source, segment, dates et type validés. |
| `weighted_pipeline_amount` | `Nullable(Decimal(38,4))` | Oui | Projection sans changement de dtr_pipeline_periods.weighted_pipeline_amount. Montant × probabilité avec précision commune, seulement si montant et coefficient admissibles. |
| `is_amount_calculable` | `Bool` | Non | Projection sans changement de dtr_pipeline_periods.is_amount_calculable. true seulement si pipeline_amount, nature/unité et devise prouvées ET statut spécifique de mesure disponible ; false sinon. Un montant candidat non NULL seul ne suffit pas. |
| `is_probability_calculable` | `Bool` | Non | Projection sans changement de dtr_pipeline_periods.is_probability_calculable. true si signature_probability est non NULL et probability_rule validée pour étape/segment/type/période ; false sinon. |
| `is_left_censored` | `Bool` | Non | Projection sans changement de dtr_pipeline_periods.is_left_censored. stage_entered_at IS NULL et stage_first_observed_at connu ; début exact absent, sans remplacer par première observation. |
| `coverage_start_at` | `Nullable(DateTime64(3, 'UTC'))` | Oui | Projection sans changement de dtr_pipeline_periods.coverage_start_at. Borne basse de couverture utile. |
| `coverage_end_at` | `Nullable(DateTime64(3, 'UTC'))` | Oui | Projection sans changement de dtr_pipeline_periods.coverage_end_at. Borne haute de couverture connue. |
| `is_history_complete` | `Nullable(Bool)` | Oui | Projection sans changement de dtr_pipeline_periods.is_history_complete. Contrôle de couverture déclaré. |
| `sale_type_id` | `Nullable(Int64)` | Oui | Projection sans changement de dtr_pipeline_periods.sale_type_id. Type commercial du dossier dans le contexte retenu ; ne désigne pas la composante financière New/Upsell. |
| `sale_type_key` | `Nullable(String)` | Oui | Projection sans changement de dtr_pipeline_periods.sale_type_key. Identité stable du type commercial. |
| `sale_type_version_key` | `Nullable(String)` | Oui | Projection sans changement de dtr_pipeline_periods.sale_type_version_key. Version de dim_sale_type pertinente. |
| `sale_type_label` | `Nullable(String)` | Oui | Projection sans changement de dtr_pipeline_periods.sale_type_label. dim_sale_type.sale_type_label par run+version, N:0..1. |
| `channel_key` | `Nullable(String)` | Oui | Projection sans changement de dtr_pipeline_periods.channel_key. Alias explicite de acquisition_channel_key du fait ; canal officiel d'entrée, NULL avant règle validée. |
| `channel_version_key` | `Nullable(String)` | Oui | Projection sans changement de dtr_pipeline_periods.channel_version_key. Version de mapping du canal, indépendante des sources candidates conservées. |
| `channel_label` | `Nullable(String)` | Oui | Projection sans changement de dtr_pipeline_periods.channel_label. dim_channel.channel_label par run+version, N:0..1. |
| `channel_candidate_code` | `Nullable(String)` | Oui | Projection sans changement de dtr_pipeline_periods.channel_candidate_code. Valeur candidate Boond conservée sans la transformer en canal officiel. |
| `is_channel_calculable` | `Bool` | Non | Projection sans changement de dtr_pipeline_periods.is_channel_calculable. false si origine à création ou mapping de valeur est manquant ; règle D24 définie, filtre disponible sur les lignes résolues. |
| `employee_key` | `Nullable(String)` | Oui | Projection sans changement de dtr_pipeline_periods.employee_key. Identité stable du responsable retenu. |
| `employee_version_key` | `Nullable(String)` | Oui | Projection sans changement de dtr_pipeline_periods.employee_version_key. Version descriptive du responsable. |
| `employee_display_name` | `Nullable(String)` | Oui | Projection sans changement de dtr_pipeline_periods.employee_display_name. dim_employee.employee_display_name par run+version, N:0..1. |
| `team_key` | `Nullable(String)` | Oui | Projection sans changement de dtr_pipeline_periods.team_key. Équipe historiquement retenue si mapping et attribution validés. |
| `team_version_key` | `Nullable(String)` | Oui | Projection sans changement de dtr_pipeline_periods.team_version_key. Version de l'équipe pertinente. |
| `team_name` | `Nullable(String)` | Oui | Projection sans changement de dtr_pipeline_periods.team_name. dim_team.team_name par run+version, N:0..1. |
| `is_team_calculable` | `Bool` | Non | Projection sans changement de dtr_pipeline_periods.is_team_calculable. false pour rattachement à entrée/événement inconnu ou ambigu ; sinon true y compris KAM connue, indépendamment de son absence de cible D23. |
| `calculation_status` | `String` | Non | Projection sans changement de dtr_pipeline_periods.calculation_status. ready/partial/blocked/not_applicable ; ready n'efface pas les réserves distinctes de couverture. |
| `status_reason` | `Nullable(String)` | Oui | Projection sans changement de dtr_pipeline_periods.status_reason. Motif explicite, stable et documenté ; plusieurs motifs séparés de façon canonique si nécessaire. |

**SQL de projection complet :**

```sql
{{ config(materialized='view', schema='dtr_sales') }}

select
    d.model_run_id,
    d.record_key,
    d.record_version_key,
    d.row_hash,
    d.calculated_at,
    d.rule_version,
    d.input_cutoff_at,
    d.tenant_id,
    d.opportunity_key,
    d.opportunity_id,
    d.company_key,
    d.company_version_key,
    d.company_id,
    d.company_name,
    d.period_key,
    d.visit_key,
    d.valid_from_at,
    d.valid_to_at,
    d.created_at,
    d.stage_id,
    d.stage_key,
    d.stage_version_key,
    d.stage_label,
    d.is_open,
    d.is_demo_stage,
    d.stage_entered_at,
    d.expected_close_at,
    d.pipeline_amount,
    d.amount_basis,
    d.currency_code,
    d.signature_probability,
    d.weighted_pipeline_amount,
    d.is_amount_calculable,
    d.is_probability_calculable,
    d.is_left_censored,
    d.coverage_start_at,
    d.coverage_end_at,
    d.is_history_complete,
    d.sale_type_id,
    d.sale_type_key,
    d.sale_type_version_key,
    d.sale_type_label,
    d.channel_key,
    d.channel_version_key,
    d.channel_label,
    d.channel_candidate_code,
    d.is_channel_calculable,
    d.employee_key,
    d.employee_version_key,
    d.employee_display_name,
    d.team_key,
    d.team_version_key,
    d.team_name,
    d.is_team_calculable,
    d.calculation_status,
    d.status_reason
from {{ ref('dtr_pipeline_periods') }} as d
inner join {{ ref('int_publication') }} as p
    on d.model_run_id = p.model_run_id
```

**Jointure/publication :** DTR N:1 vers la ligne unique du pointeur, égalité de run ; au bootstrap sans pointeur accepté, zéro ligne. Plus d'une ligne de pointeur est ERROR bloquante. Aucune dépendance inverse DTR→publication. Chaque requête BI conserve model_run_id et vérifie sa cohérence avec dataset_publication_status ; une page ne mélange pas plusieurs runs.

**Contrat BI et filtres :** Observation O ; période de série sous forme de liste explicite d'observations (jour/semaine/mois si choisie), type, équipe et canal lorsqu'ils sont calculables. Pour la couverture d'objectif, mois de closing prévu séparé du mois observé. Seuil de stagnation optionnel fourni explicitement ; pas d'alerte si absent. Cohorte=mois de created_at en Paris si demandée.

**Calculs restants en restitution :** À O, compter opportunity_key au grain résolu, sommer montants comparables, recalculer parts de canal depuis effectifs de la même population. Nb In demo=nombre distinct company_key ayant au moins une période ouverte admissible en étape Démo ; identités société inconnues dans couverture distincte, jamais comptées comme une seule société fictive. Série historique : une mesure par date, pas somme des stocks. Couverture=montant ouvert à closing prévu dans le mois / cible compatible explicitement choisie, sinon NULL+missing_coverage_definition. Ils utilisent les champs détaillés, pas des ratios/quantiles locaux déjà agrégés. Les dates/arrondis/libellés/couleurs se formatent dans la BI ; les champsNULL restent indisponibles, jamais zéro d'affichage implicite. Avant agrégation, vérifier disponibilité PAR MESURE dans dataset_publication_status, y compris absence de lignes de détail.

**Test du dataset :** compter et comparer clés/payloads à la DTR sur le seul run publié ; égalité exacte attendue, ERROR sinon. Tester bootstrap vide, bascule vers nouveau run, réexécution sans modification, navigation tenant+clé+run et détection de publication différente entre requêtes. Rejouer les scénarios de filtres et d'agrégation de `dtr_pipeline_periods`, dont Périodes sans chevauchement par opportunité/run ; exactement0/1 ligne à O ; entrée du stage identique sur transfert ; société avec2 dossiers Démo=>1 ; global sociétés recalculé après filtre ; montant inconnu non zéro ; seuil absent aucune classification officielle ; stocks non sommés entre dates.

**Rafraîchissement/limites :** la vue reflète le pointeur accepté sans horaire propre ; la fraîcheur dépend des sources, du run et de sa publication. Une règle/preuve manquante dans la DTR n'est pas réparée dans cette vue. Les blocages/limites sont ceux de la DTR et du dataset technique de disponibilité. Une relecture d'ancien run passe par la DTR explicite, sans changement du pointeur.


<a id="dtr_sales_events"></a>

### `dtr_sales_events`

**Règle finale v0.2 :** D18/D19 : un seul premier signed et un seul premier cycle terminal datable par dossier, via les contributions canoniques du fait. Re-signatures restent visibles avec0 contribution de nouvelle vente, pas un blocage métier global. Les dates de cycle/sortie restent observées D15 et qualifiées.

**Couche/module :** DTR, Reste du catalogue — flux commerciaux et cycle. **Finalité :** Hors trois PNG : génération par canal/Inbound si mapping validé, entrées/sorties, signatures et pertes, MRR signé, durées de cycle, détail du parcours. Les objectifs mensuels consomment le fait canonique dans core ; pas de dépendance core→cette DTR.

**Grain métier :** tenant_id × event_key ; un événement commercial admissible d'un dossier. **Identité logique :** `record_key=H(tenant_id, event_key)`. **Grain historique/physique :** `(model_run_id,record_key)` ; version=H(run,key), une seule contribution par unité dans un run. Les clés métier et de dimensions sont conservées ci-dessous.

**Amont exact :** `{{ ref('fct_opportunity_event') }}`, `{{ ref('dim_company') }}`, `{{ ref('dim_stage') }}`, `{{ ref('dim_sale_type') }}`, `{{ ref('dim_channel') }}`, `{{ ref('dim_employee') }}`, `{{ ref('dim_team') }}`. **Destination :** `dtr_sales.dtr_sales_events` ; fichier `dbt/models/reporting/dtr/dtr_sales_events.sql`, YAML `dbt/models/reporting/dtr/_models.yml`.

| Colonne | Type ClickHouse | Nullable | Origine, formule et contraintes |
|---|---|---|---|
| `model_run_id` | `String` | Non | Identifiant de la recomposition complète et immuable ; hérité des entrées du même run. |
| `record_key` | `String` | Non | SHA256 de la liste ordonnée des éléments du grain indiquée dans la fiche ; sérialisation canonique commune, jamais simple concaténation ambiguë. |
| `record_version_key` | `String` | Non | SHA256 de (model_run_id, record_key). |
| `row_hash` | `String` | Non | SHA256 du payload ordonné de la fiche, hors colonnes techniques communes. |
| `calculated_at` | `DateTime64(3, 'UTC')` | Non | Instant de calcul du run ; aucune substitution à une date métier. |
| `rule_version` | `String` | Non | Version immuable des règles et référentiels utilisés par le run. |
| `input_cutoff_at` | `DateTime64(3, 'UTC')` | Non | Borne des entrées figées ; héritée du manifeste de run. |
| `tenant_id` | `String` | Non | Tenant Boond conservé dans les identités et jointures. |
| `opportunity_key` | `String` | Non | Identité stable tenant + opportunité. |
| `opportunity_id` | `Int64` | Non | Identifiant Boond du dossier, pour investigation. |
| `company_key` | `Nullable(String)` | Oui | Identité stable de société résolue au contexte retenu. |
| `company_version_key` | `Nullable(String)` | Oui | Version de société pertinente au contexte retenu. |
| `company_id` | `Nullable(Int64)` | Oui | Identifiant Boond de la société. |
| `company_name` | `Nullable(String)` | Oui | dim_company.company_name par run+company_version_key, N:0..1. |
| `event_key` | `String` | Non | Identité logique de l'événement ; plusieurs versions CDC ne créent pas plusieurs événements. |
| `visit_key` | `Nullable(String)` | Oui | Passage d'origine si rattachement démontré. |
| `event_type` | `String` | Non | Type canonique du fait : création/entrée pipeline, entrée/sortie étape, signature, perte ou autre événement explicite. |
| `event_at` | `Nullable(DateTime64(3, 'UTC'))` | Oui | Date métier prouvée ou proxy qualifié ; NULL si événement non datable. |
| `event_date` | `Nullable(Date)` | Oui | Date Europe/Paris de event_at préparée dans SELECT ; NULL si event_at inconnu. |
| `event_time_basis` | `String` | Non | Provenance exacte de la date ; meta.ts ne devient pas automatiquement signature. |
| `is_event_time_accepted` | `Nullable(Bool)` | Oui | fct_opportunity_event.is_event_time_accepted ; true pour date métier ou transition CDC observée admissible selon D15, NULL pour événement non datable. |
| `from_stage_id` | `Nullable(Int64)` | Oui | Code d'étape quittée pour une transition. |
| `to_stage_id` | `Nullable(Int64)` | Oui | Code d'étape rejointe pour une transition. |
| `from_stage_version_key` | `Nullable(String)` | Oui | Version pertinente de l'étape quittée. |
| `to_stage_version_key` | `Nullable(String)` | Oui | Version pertinente de l'étape rejointe. |
| `from_stage_label` | `Nullable(String)` | Oui | Libellé de l'étape quittée, N:0..1 par run+version. |
| `to_stage_label` | `Nullable(String)` | Oui | Libellé de l'étape rejointe, N:0..1 par run+version. |
| `nb_events` | `Nullable(UInt8)` | Oui | Contribution admissible canonique 0/1 du fait ; pas nombre de versions sources. |
| `sum_generated_pipeline_amount` | `Nullable(Decimal(38,4))` | Oui | Montant de génération admissible pour4/7 ; NULL si unité/date/valeur non prouvées ; périmètre décidé D22. |
| `sum_signed_mrr` | `Nullable(Decimal(38,4))` | Oui | Mensualité récurrente engagée, supplément seul pour upsell ; NULL sans source prouvée. |
| `amount_basis` | `Nullable(String)` | Oui | Nature du montant financier, sans assimilation automatique montant CRM/MRR. |
| `currency_code` | `Nullable(String)` | Oui | EUR par hypothèse explicite du case D20 ; cette devise ne prouve ni mensualité ni engagement du montant commercial. |
| `is_generated_amount_calculable` | `Bool` | Non | true si sum_generated_pipeline_amount est non NULL ET les règles unité/devise/périmètre sont validées pour cette contribution ; false sinon. |
| `is_signed_mrr_calculable` | `Bool` | Non | true si sum_signed_mrr est non NULL ET preuve du montant signé mensuel et population validées ; false sinon. |
| `cycle_started_at` | `Nullable(DateTime64(3, 'UTC'))` | Oui | Création/entrée retenue pour le cycle commercial. |
| `completed_cycle_duration_seconds` | `Nullable(Float64)` | Oui | Écart en millisecondes event_at-cycle_started_at /1000 pour issue admissible connue. |
| `completed_cycle_duration_days` | `Nullable(Float64)` | Oui | fct_opportunity_event.completed_cycle_duration_seconds/86400.0, sans arrondi. |
| `is_eligible` | `Nullable(Bool)` | Oui | Alias explicite de fct_opportunity_event.is_contribution_eligible ; NULL si la contribution n'est pas admissible de façon déterminée. |
| `sale_type_id` | `Nullable(Int64)` | Oui | Type commercial du dossier dans le contexte retenu ; ne désigne pas la composante financière New/Upsell. |
| `sale_type_key` | `Nullable(String)` | Oui | Identité stable du type commercial. |
| `sale_type_version_key` | `Nullable(String)` | Oui | Version de dim_sale_type pertinente. |
| `sale_type_label` | `Nullable(String)` | Oui | dim_sale_type.sale_type_label par run+version, N:0..1. |
| `channel_key` | `Nullable(String)` | Oui | Alias explicite de acquisition_channel_key du fait ; canal officiel d'entrée, NULL avant règle validée. |
| `channel_version_key` | `Nullable(String)` | Oui | Version de mapping du canal, indépendante des sources candidates conservées. |
| `channel_label` | `Nullable(String)` | Oui | dim_channel.channel_label par run+version, N:0..1. |
| `channel_candidate_code` | `Nullable(String)` | Oui | Valeur candidate Boond conservée sans la transformer en canal officiel. |
| `is_channel_calculable` | `Bool` | Non | false si origine à création ou mapping de valeur est manquant ; règle D24 définie, filtre disponible sur les lignes résolues. |
| `employee_key` | `Nullable(String)` | Oui | Identité stable du responsable retenu. |
| `employee_version_key` | `Nullable(String)` | Oui | Version descriptive du responsable. |
| `employee_display_name` | `Nullable(String)` | Oui | dim_employee.employee_display_name par run+version, N:0..1. |
| `team_key` | `Nullable(String)` | Oui | Équipe historiquement retenue si mapping et attribution validés. |
| `team_version_key` | `Nullable(String)` | Oui | Version de l'équipe pertinente. |
| `team_name` | `Nullable(String)` | Oui | dim_team.team_name par run+version, N:0..1. |
| `is_team_calculable` | `Bool` | Non | false pour rattachement à entrée/événement inconnu ou ambigu ; sinon true y compris KAM connue, indépendamment de son absence de cible D23. |
| `calculation_status` | `String` | Non | ready/partial/blocked/not_applicable ; ready n'efface pas les réserves distinctes de couverture. |
| `status_reason` | `Nullable(String)` | Oui | Motif explicite, stable et documenté ; plusieurs motifs séparés de façon canonique si nécessaire. |

**Jointures, identités et cardinalités :** Fait → société/type/canal/responsable/équipe et deux rôles de dim_stage : N:0..1 pour chacun, sur run+versionkey. Pas de jointure brute aux périodes, actions ou cibles pour produire les montants. Le contexte est déjà celui de l'événement ; ne pas le remplacer par l'équipe actuelle.

**Étapes du calcul :** Exposer les événements préparés une fois dans le module Pipeline. Création=génération de dossier unique ; qualification reste distincte. Signature état 1, formalités état 14 sans nouvelle vente. Dédupliquer au grain de la contribution monétaire admissible avant somme ; compter les dossiers distincts selon mesure/période plutôt que les transitions multiples. D18 conserve la cohorte et ne compte que la première signature observée ; traces suivantes conservées avec contribution de vente0.

**Filtrage, paramètres et agrégation :** Période de flux [period_from_at,period_to_at), observation O éventuelle imposant event_at<=O, type commercial, équipe de l'événement, canal d'entrée calculable ; étape source/cible selon mesure. Cohorte éventuelle = mois de création via contexte canonique conservé ou filtre de population de followup, jamais mois event_at rebaptisé cohorte. Seuil sans objet. Flux admissibles : somme des contributions financières comparables, contrôlée pour inconnus ; nombre de dossiers distincts pour génération/signature/perte/entrée-sortie d'étape. nb_events s'additionne seulement pour dénombrer événements homogènes, pas dossiers uniques. Cycle : quantiles exacts sur observations unitaires comparables ; ne pas mélanger cycle terminé et ancienneté courante.

**Matérialisation/histoire :** appliquer le contrat DTR commun ci-dessus : résultats complets du run, incremental append, engine MergeTree, ORDER BY(model_run_id,record_key), unique_key record_version_key, on_schema_change fail, full_refresh false et pas inserts_only. Les tables DTR conservent les anciens runs ; aucun filtre max de date métier ou limite à hier. Au premier chargement/cible vide, calculer l'ensemble ; en reprise, conserver seulement les clés du candidat absentes de la cible, sans modifier un payload existant.

**Contrat de chargement dbt :** une requête SELECT, CTE candidates explicite issue des transformations décrites. Chaque colonne du dictionnaire est produite exactement une fois. Terminer par la projection explicite de candidates ; sous `{% if is_incremental() %}`, LEFT ANTI JOIN de `{{ this }}` sur model_run_id et record_key. Tester absence de deux payloads différents pour une même clé/run AVANT chargement. Le unique_key de configuration assure le chemin de contrôle de schéma de l'adaptateur, pas la déduplication. Les entrées du run et le cutoff sont figés avant toute écriture future ; reprise du même run à empreinte inchangée.

**Construction/rafraîchissement :** après tous amonts du même run ; branches indépendantes parallélisables selon DAG. Exécution manuelle D29 ; fraîcheur de capture/publication déclarée, calcul puis tests/digest et publication contrôlée. Les requêtes de contrôle avant publication utilisent test_model_run_id. Aucun service/modèle n'est créé par la présente fiche.

**Tests/acceptation :** Création unique malgré versions ; 1→14 une signature ; contribution upsell100→150 égale50 si source prouvée ; aucun montant officiel depuis unité inconnue ; contextes historiques bons ; réouverture tracée, même cohorte et une seule première signature selon D18 ; quantiles recomposés depuis événements admissibles. Contrôles communs ERROR de grain, hash, cardinalité et run ; WARN/indisponibilité pour manque descriptif ou preuve comme décrit dans le contrat. Tests métier ci-dessus planifiés, pas exécutés sur une implémentation inexistante.



**Garde G04 normative de restitution** : pour chaque flux officiel, flag monétaire et cycle terminé, exiger is_event_time_accepted=true ET is_eligible=true ET nb_events=1. Sinon contribution officielle NULL et motif de date/éligibilité, avec nb_expected/nb_known ; ne pas exclure silencieusement les inconnus du dénominateur. Un compteur de traces/proxies peut être diagnostique avec un libellé distinct, jamais rebaptisé flux officiel.

<a id="dataset_sales_events"></a>

### `dataset_sales_events`

**Couche/module :** dataset de restitution, Reste du catalogue — flux commerciaux et cycle. **Finalité/consommateurs :** Hors trois PNG : génération par canal/Inbound si mapping validé, entrées/sorties, signatures et pertes, MRR signé, durées de cycle, détail du parcours. Les objectifs mensuels consomment le fait canonique dans core ; pas de dépendance core→cette DTR.

**Grain métier et version :** exactement celui de `dtr_sales_events` : tenant_id × event_key ; un événement commercial admissible d'un dossier. Une seule publication est visible ; identité et version sont conservées sans recalcul. Aucun total ni ligne artificielle n'est ajouté.

**Amont exact :** `{{ ref('dtr_sales_events') }}` et `{{ ref('int_publication') }}`. **Destination :** `dtr_sales.dataset_sales_events` ; fichier `dbt/models/reporting/datasets/dataset_sales_events.sql`, YAML `dbt/models/reporting/datasets/_models.yml`.

| Colonne | Type ClickHouse | Nullable | Origine, formule et contraintes |
|---|---|---|---|
| `model_run_id` | `String` | Non | Projection sans changement de dtr_sales_events.model_run_id. Identifiant de la recomposition complète et immuable ; hérité des entrées du même run. |
| `record_key` | `String` | Non | Projection sans changement de dtr_sales_events.record_key. SHA256 de la liste ordonnée des éléments du grain indiquée dans la fiche ; sérialisation canonique commune, jamais simple concaténation ambiguë. |
| `record_version_key` | `String` | Non | Projection sans changement de dtr_sales_events.record_version_key. SHA256 de (model_run_id, record_key). |
| `row_hash` | `String` | Non | Projection sans changement de dtr_sales_events.row_hash. SHA256 du payload ordonné de la fiche, hors colonnes techniques communes. |
| `calculated_at` | `DateTime64(3, 'UTC')` | Non | Projection sans changement de dtr_sales_events.calculated_at. Instant de calcul du run ; aucune substitution à une date métier. |
| `rule_version` | `String` | Non | Projection sans changement de dtr_sales_events.rule_version. Version immuable des règles et référentiels utilisés par le run. |
| `input_cutoff_at` | `DateTime64(3, 'UTC')` | Non | Projection sans changement de dtr_sales_events.input_cutoff_at. Borne des entrées figées ; héritée du manifeste de run. |
| `tenant_id` | `String` | Non | Projection sans changement de dtr_sales_events.tenant_id. Tenant Boond conservé dans les identités et jointures. |
| `opportunity_key` | `String` | Non | Projection sans changement de dtr_sales_events.opportunity_key. Identité stable tenant + opportunité. |
| `opportunity_id` | `Int64` | Non | Projection sans changement de dtr_sales_events.opportunity_id. Identifiant Boond du dossier, pour investigation. |
| `company_key` | `Nullable(String)` | Oui | Projection sans changement de dtr_sales_events.company_key. Identité stable de société résolue au contexte retenu. |
| `company_version_key` | `Nullable(String)` | Oui | Projection sans changement de dtr_sales_events.company_version_key. Version de société pertinente au contexte retenu. |
| `company_id` | `Nullable(Int64)` | Oui | Projection sans changement de dtr_sales_events.company_id. Identifiant Boond de la société. |
| `company_name` | `Nullable(String)` | Oui | Projection sans changement de dtr_sales_events.company_name. dim_company.company_name par run+company_version_key, N:0..1. |
| `event_key` | `String` | Non | Projection sans changement de dtr_sales_events.event_key. Identité logique de l'événement ; plusieurs versions CDC ne créent pas plusieurs événements. |
| `visit_key` | `Nullable(String)` | Oui | Projection sans changement de dtr_sales_events.visit_key. Passage d'origine si rattachement démontré. |
| `event_type` | `String` | Non | Projection sans changement de dtr_sales_events.event_type. Type canonique du fait : création/entrée pipeline, entrée/sortie étape, signature, perte ou autre événement explicite. |
| `event_at` | `Nullable(DateTime64(3, 'UTC'))` | Oui | Projection sans changement de dtr_sales_events.event_at. Date métier prouvée ou proxy qualifié ; NULL si événement non datable. |
| `event_date` | `Nullable(Date)` | Oui | Projection sans changement de dtr_sales_events.event_date. Date Europe/Paris de event_at préparée dans SELECT ; NULL si event_at inconnu. |
| `event_time_basis` | `String` | Non | Projection sans changement de dtr_sales_events.event_time_basis. Provenance exacte de la date ; meta.ts ne devient pas automatiquement signature. |
| `is_event_time_accepted` | `Nullable(Bool)` | Oui | Projection explicite de dtr_sales_events.is_event_time_accepted ; aucune décision de date ajoutée. |
| `from_stage_id` | `Nullable(Int64)` | Oui | Projection sans changement de dtr_sales_events.from_stage_id. Code d'étape quittée pour une transition. |
| `to_stage_id` | `Nullable(Int64)` | Oui | Projection sans changement de dtr_sales_events.to_stage_id. Code d'étape rejointe pour une transition. |
| `from_stage_version_key` | `Nullable(String)` | Oui | Projection sans changement de dtr_sales_events.from_stage_version_key. Version pertinente de l'étape quittée. |
| `to_stage_version_key` | `Nullable(String)` | Oui | Projection sans changement de dtr_sales_events.to_stage_version_key. Version pertinente de l'étape rejointe. |
| `from_stage_label` | `Nullable(String)` | Oui | Projection sans changement de dtr_sales_events.from_stage_label. Libellé de l'étape quittée, N:0..1 par run+version. |
| `to_stage_label` | `Nullable(String)` | Oui | Projection sans changement de dtr_sales_events.to_stage_label. Libellé de l'étape rejointe, N:0..1 par run+version. |
| `nb_events` | `Nullable(UInt8)` | Oui | Projection sans changement de dtr_sales_events.nb_events. Contribution admissible canonique 0/1 du fait ; pas nombre de versions sources. |
| `sum_generated_pipeline_amount` | `Nullable(Decimal(38,4))` | Oui | Projection sans changement de dtr_sales_events.sum_generated_pipeline_amount. Montant de génération admissible pour4/7 ; NULL si unité/date/valeur non prouvées ; périmètre décidé D22. |
| `sum_signed_mrr` | `Nullable(Decimal(38,4))` | Oui | Projection sans changement de dtr_sales_events.sum_signed_mrr. Mensualité récurrente engagée, supplément seul pour upsell ; NULL sans source prouvée. |
| `amount_basis` | `Nullable(String)` | Oui | Projection sans changement de dtr_sales_events.amount_basis. Nature du montant financier, sans assimilation automatique montant CRM/MRR. |
| `currency_code` | `Nullable(String)` | Oui | Projection sans changement de dtr_sales_events.currency_code. EUR par hypothèse explicite du case D20 ; cette devise ne prouve ni mensualité ni engagement du montant commercial. |
| `is_generated_amount_calculable` | `Bool` | Non | Projection sans changement de dtr_sales_events.is_generated_amount_calculable. true si sum_generated_pipeline_amount est non NULL ET les règles unité/devise/périmètre sont validées pour cette contribution ; false sinon. |
| `is_signed_mrr_calculable` | `Bool` | Non | Projection sans changement de dtr_sales_events.is_signed_mrr_calculable. true si sum_signed_mrr est non NULL ET preuve du montant signé mensuel et population validées ; false sinon. |
| `cycle_started_at` | `Nullable(DateTime64(3, 'UTC'))` | Oui | Projection sans changement de dtr_sales_events.cycle_started_at. Création/entrée retenue pour le cycle commercial. |
| `completed_cycle_duration_seconds` | `Nullable(Float64)` | Oui | Projection sans changement de dtr_sales_events.completed_cycle_duration_seconds. Écart en millisecondes event_at-cycle_started_at /1000 pour issue admissible connue. |
| `completed_cycle_duration_days` | `Nullable(Float64)` | Oui | Projection sans changement de dtr_sales_events.completed_cycle_duration_days. fct_opportunity_event.completed_cycle_duration_seconds/86400.0, sans arrondi. |
| `is_eligible` | `Nullable(Bool)` | Oui | Projection sans changement de dtr_sales_events.is_eligible. Alias explicite de fct_opportunity_event.is_contribution_eligible ; NULL si la contribution n'est pas admissible de façon déterminée. |
| `sale_type_id` | `Nullable(Int64)` | Oui | Projection sans changement de dtr_sales_events.sale_type_id. Type commercial du dossier dans le contexte retenu ; ne désigne pas la composante financière New/Upsell. |
| `sale_type_key` | `Nullable(String)` | Oui | Projection sans changement de dtr_sales_events.sale_type_key. Identité stable du type commercial. |
| `sale_type_version_key` | `Nullable(String)` | Oui | Projection sans changement de dtr_sales_events.sale_type_version_key. Version de dim_sale_type pertinente. |
| `sale_type_label` | `Nullable(String)` | Oui | Projection sans changement de dtr_sales_events.sale_type_label. dim_sale_type.sale_type_label par run+version, N:0..1. |
| `channel_key` | `Nullable(String)` | Oui | Projection sans changement de dtr_sales_events.channel_key. Alias explicite de acquisition_channel_key du fait ; canal officiel d'entrée, NULL avant règle validée. |
| `channel_version_key` | `Nullable(String)` | Oui | Projection sans changement de dtr_sales_events.channel_version_key. Version de mapping du canal, indépendante des sources candidates conservées. |
| `channel_label` | `Nullable(String)` | Oui | Projection sans changement de dtr_sales_events.channel_label. dim_channel.channel_label par run+version, N:0..1. |
| `channel_candidate_code` | `Nullable(String)` | Oui | Projection sans changement de dtr_sales_events.channel_candidate_code. Valeur candidate Boond conservée sans la transformer en canal officiel. |
| `is_channel_calculable` | `Bool` | Non | Projection sans changement de dtr_sales_events.is_channel_calculable. false si origine à création ou mapping de valeur est manquant ; règle D24 définie, filtre disponible sur les lignes résolues. |
| `employee_key` | `Nullable(String)` | Oui | Projection sans changement de dtr_sales_events.employee_key. Identité stable du responsable retenu. |
| `employee_version_key` | `Nullable(String)` | Oui | Projection sans changement de dtr_sales_events.employee_version_key. Version descriptive du responsable. |
| `employee_display_name` | `Nullable(String)` | Oui | Projection sans changement de dtr_sales_events.employee_display_name. dim_employee.employee_display_name par run+version, N:0..1. |
| `team_key` | `Nullable(String)` | Oui | Projection sans changement de dtr_sales_events.team_key. Équipe historiquement retenue si mapping et attribution validés. |
| `team_version_key` | `Nullable(String)` | Oui | Projection sans changement de dtr_sales_events.team_version_key. Version de l'équipe pertinente. |
| `team_name` | `Nullable(String)` | Oui | Projection sans changement de dtr_sales_events.team_name. dim_team.team_name par run+version, N:0..1. |
| `is_team_calculable` | `Bool` | Non | Projection sans changement de dtr_sales_events.is_team_calculable. false pour rattachement à entrée/événement inconnu ou ambigu ; sinon true y compris KAM connue, indépendamment de son absence de cible D23. |
| `calculation_status` | `String` | Non | Projection sans changement de dtr_sales_events.calculation_status. ready/partial/blocked/not_applicable ; ready n'efface pas les réserves distinctes de couverture. |
| `status_reason` | `Nullable(String)` | Oui | Projection sans changement de dtr_sales_events.status_reason. Motif explicite, stable et documenté ; plusieurs motifs séparés de façon canonique si nécessaire. |

**SQL de projection complet :**

```sql
{{ config(materialized='view', schema='dtr_sales') }}

select
    d.model_run_id,
    d.record_key,
    d.record_version_key,
    d.row_hash,
    d.calculated_at,
    d.rule_version,
    d.input_cutoff_at,
    d.tenant_id,
    d.opportunity_key,
    d.opportunity_id,
    d.company_key,
    d.company_version_key,
    d.company_id,
    d.company_name,
    d.event_key,
    d.visit_key,
    d.event_type,
    d.event_at,
    d.event_date,
    d.event_time_basis,
    d.is_event_time_accepted,
    d.from_stage_id,
    d.to_stage_id,
    d.from_stage_version_key,
    d.to_stage_version_key,
    d.from_stage_label,
    d.to_stage_label,
    d.nb_events,
    d.sum_generated_pipeline_amount,
    d.sum_signed_mrr,
    d.amount_basis,
    d.currency_code,
    d.is_generated_amount_calculable,
    d.is_signed_mrr_calculable,
    d.cycle_started_at,
    d.completed_cycle_duration_seconds,
    d.completed_cycle_duration_days,
    d.is_eligible,
    d.sale_type_id,
    d.sale_type_key,
    d.sale_type_version_key,
    d.sale_type_label,
    d.channel_key,
    d.channel_version_key,
    d.channel_label,
    d.channel_candidate_code,
    d.is_channel_calculable,
    d.employee_key,
    d.employee_version_key,
    d.employee_display_name,
    d.team_key,
    d.team_version_key,
    d.team_name,
    d.is_team_calculable,
    d.calculation_status,
    d.status_reason
from {{ ref('dtr_sales_events') }} as d
inner join {{ ref('int_publication') }} as p
    on d.model_run_id = p.model_run_id
```

**Jointure/publication :** DTR N:1 vers la ligne unique du pointeur, égalité de run ; au bootstrap sans pointeur accepté, zéro ligne. Plus d'une ligne de pointeur est ERROR bloquante. Aucune dépendance inverse DTR→publication. Chaque requête BI conserve model_run_id et vérifie sa cohérence avec dataset_publication_status ; une page ne mélange pas plusieurs runs.

**Contrat BI et filtres :** Période de flux [period_from_at,period_to_at), observation O éventuelle imposant event_at<=O, type commercial, équipe de l'événement, canal d'entrée calculable ; étape source/cible selon mesure. Cohorte éventuelle = mois de création via contexte canonique conservé ou filtre de population de followup, jamais mois event_at rebaptisé cohorte. Seuil sans objet.

**Calculs restants en restitution :** Flux admissibles : somme des contributions financières comparables, contrôlée pour inconnus ; nombre de dossiers distincts pour génération/signature/perte/entrée-sortie d'étape. nb_events s'additionne seulement pour dénombrer événements homogènes, pas dossiers uniques. Cycle : quantiles exacts sur observations unitaires comparables ; ne pas mélanger cycle terminé et ancienneté courante. Ils utilisent les champs détaillés, pas des ratios/quantiles locaux déjà agrégés. Les dates/arrondis/libellés/couleurs se formatent dans la BI ; les champsNULL restent indisponibles, jamais zéro d'affichage implicite. Avant agrégation, vérifier disponibilité PAR MESURE dans dataset_publication_status, y compris absence de lignes de détail.

**Test du dataset :** compter et comparer clés/payloads à la DTR sur le seul run publié ; égalité exacte attendue, ERROR sinon. Tester bootstrap vide, bascule vers nouveau run, réexécution sans modification, navigation tenant+clé+run et détection de publication différente entre requêtes. Rejouer les scénarios de filtres et d'agrégation de `dtr_sales_events`, dont Création unique malgré versions ; 1→14 une signature ; contribution upsell100→150 égale50 si source prouvée ; aucun montant officiel depuis unité inconnue ; contextes historiques bons ; réouverture tracée, même cohorte et une seule première signature selon D18 ; quantiles recomposés depuis événements admissibles.

**Rafraîchissement/limites :** la vue reflète le pointeur accepté sans horaire propre ; la fraîcheur dépend des sources, du run et de sa publication. Une règle/preuve manquante dans la DTR n'est pas réparée dans cette vue. Les blocages/limites sont ceux de la DTR et du dataset technique de disponibilité. Une relecture d'ancien run passe par la DTR explicite, sans changement du pointeur.



**Garde G04 normative de restitution** : pour chaque flux officiel, flag monétaire et cycle terminé, exiger is_event_time_accepted=true ET is_eligible=true ET nb_events=1. Sinon contribution officielle NULL et motif de date/éligibilité, avec nb_expected/nb_known ; ne pas exclure silencieusement les inconnus du dénominateur. Un compteur de traces/proxies peut être diagnostique avec un libellé distinct, jamais rebaptisé flux officiel.

<a id="dtr_sales_actions"></a>

### `dtr_sales_actions`

**Couche/module :** DTR, Reste du catalogue — demandes et rendez-vous de démo. **Finalité :** Hors trois PNG : demandes et séances de démo, répartition première/complémentaire si pertinente ; détail explicatif du compteur O04. Les cartes O04 officielles restent bloquées sans preuve/source suffisante, même si des actions planifiées existent.

**Grain métier :** tenant_id × action_key ; état corrigé pertinent d'une action logique dans le run. **Identité logique :** `record_key=H(tenant_id, action_key)`. **Grain historique/physique :** `(model_run_id,record_key)` ; version=H(run,key), une seule contribution par unité dans un run. Les clés métier et de dimensions sont conservées ci-dessous.

**Amont exact :** `{{ ref('fct_action') }}`, `{{ ref('fct_opportunity_period') }}`, `{{ ref('dim_action_type') }}`, `{{ ref('dim_company') }}`, `{{ ref('dim_sale_type') }}`, `{{ ref('dim_employee') }}`, `{{ ref('dim_team') }}`. **Destination :** `dtr_sales.dtr_sales_actions` ; fichier `dbt/models/reporting/dtr/dtr_sales_actions.sql`, YAML `dbt/models/reporting/dtr/_models.yml`.

| Colonne | Type ClickHouse | Nullable | Origine, formule et contraintes |
|---|---|---|---|
| `model_run_id` | `String` | Non | Identifiant de la recomposition complète et immuable ; hérité des entrées du même run. |
| `record_key` | `String` | Non | SHA256 de la liste ordonnée des éléments du grain indiquée dans la fiche ; sérialisation canonique commune, jamais simple concaténation ambiguë. |
| `record_version_key` | `String` | Non | SHA256 de (model_run_id, record_key). |
| `row_hash` | `String` | Non | SHA256 du payload ordonné de la fiche, hors colonnes techniques communes. |
| `calculated_at` | `DateTime64(3, 'UTC')` | Non | Instant de calcul du run ; aucune substitution à une date métier. |
| `rule_version` | `String` | Non | Version immuable des règles et référentiels utilisés par le run. |
| `input_cutoff_at` | `DateTime64(3, 'UTC')` | Non | Borne des entrées figées ; héritée du manifeste de run. |
| `tenant_id` | `String` | Non | Tenant de l'action. |
| `action_key` | `String` | Non | Identité stable tenant+action ; le nombre de versions ne crée pas plusieurs séances. |
| `action_id` | `Int64` | Non | Identifiant Boond de l'action. |
| `source_action_version_key` | `String` | Non | Alias explicite de fct_action.action_version_key de la tranche retenue. |
| `action_state_valid_from_at` | `DateTime64(3, 'UTC')` | Non | Alias explicite de fct_action.valid_from_at de la tranche retenue. |
| `action_state_valid_to_at` | `Nullable(DateTime64(3, 'UTC'))` | Oui | Alias explicite de fct_action.valid_to_at de la tranche retenue. |
| `is_source_deleted` | `Bool` | Non | Marqueur de la dernière version pertinente ; sélectionner cette version AVANT de traiter la suppression. Aucune résurrection d'une ancienne version vivante. |
| `action_type_id` | `Nullable(Int64)` | Oui | Type source de l'action, distinct d'une preuve de réalisation. |
| `action_type_key` | `Nullable(String)` | Oui | Identité du type d'action. |
| `action_type_version_key` | `Nullable(String)` | Oui | Version de dim_action_type pertinente. |
| `action_type_label` | `Nullable(String)` | Oui | Libellé dim_action_type par run+version. |
| `company_key` | `Nullable(String)` | Oui | Société rattachée par lien direct/prouvé. |
| `company_version_key` | `Nullable(String)` | Oui | Version descriptive de la société. |
| `company_id` | `Nullable(Int64)` | Oui | Identifiant Boond de société. |
| `company_name` | `Nullable(String)` | Oui | dim_company.company_name. |
| `contact_id` | `Nullable(Int64)` | Oui | Contact source ; un contact partagé ne prouve pas le dossier. |
| `opportunity_key` | `Nullable(String)` | Oui | Dossier relié directement ou selon règle démontrée ; NULL si candidat/ambigu. |
| `opportunity_id` | `Nullable(Int64)` | Oui | Identifiant du dossier prouvé, NULL sinon. |
| `link_status` | `String` | Non | fct_action.link_status : direct_opportunity/contact_only/missing/ambiguous ; seuls liens démontrés fournissent dossier. |
| `created_at` | `Nullable(DateTime64(3, 'UTC'))` | Oui | Création de la fiche action, distincte de l'agenda et d'un événement tenu. |
| `scheduled_start_at` | `Nullable(DateTime64(3, 'UTC'))` | Oui | Début planifié de rendez-vous, sans preuve de tenue. |
| `scheduled_end_at` | `Nullable(DateTime64(3, 'UTC'))` | Oui | Fin planifiée de rendez-vous. |
| `actual_event_at` | `Nullable(DateTime64(3, 'UTC'))` | Oui | Date de tenue prouvée, jamais agenda automatiquement. |
| `realization_status` | `String` | Non | fct_action.realization_status : unknown sans preuve ; held/planned/cancelled/no_show seulement si prouvé. Ne pas inventer domaine différent. |
| `is_demo_request` | `Nullable(Bool)` | Oui | Action de demande admissible selon référentiel ; NULL si type non interprétable. |
| `is_realized_demo` | `Nullable(Bool)` | Oui | true/false seulement selon preuve de réalisation/nonréalisation ; NULL sans preuve. |
| `request_counting_at` | `Nullable(DateTime64(3, 'UTC'))` | Oui | created_at pour action de demande type25 admise : demande enregistrée ; NULL si type/date manquant. |
| `demo_session_key` | `Nullable(String)` | Oui | fct_action.demo_session_key : identité de séance tenue prouvée, NULL sans règle/preuve ; déduplication au-delà de l'identité de fiche action. |
| `demo_counting_at` | `Nullable(DateTime64(3, 'UTC'))` | Oui | actual_event_at seulement pour séance réellement tenue prouvée ; NULL sinon. |
| `nb_demo_request_contribution` | `Nullable(UInt8)` | Oui | 1 si demande admissible datée, 0 si autre action connue, NULL si type/date inconnus. |
| `nb_realized_demo_contribution` | `Nullable(UInt8)` | Oui | NULL sans tenue/session prouvée. Pour séance prouvée :1 seulement sur représentant canonique de demo_session_key (action_key minimale pour décompte technique),0 autres fiches de même séance ; preuve d'attribution équipe univoque requise pour ventilation. |
| `sale_type_id` | `Nullable(Int64)` | Oui | Type commercial du dossier dans le contexte retenu ; ne désigne pas la composante financière New/Upsell. |
| `sale_type_key` | `Nullable(String)` | Oui | Identité stable du type commercial. |
| `sale_type_version_key` | `Nullable(String)` | Oui | Version de dim_sale_type pertinente. |
| `sale_type_label` | `Nullable(String)` | Oui | dim_sale_type.sale_type_label par run+version, N:0..1. |
| `employee_key` | `Nullable(String)` | Oui | Identité stable du responsable retenu. |
| `employee_version_key` | `Nullable(String)` | Oui | Version descriptive du responsable. |
| `employee_display_name` | `Nullable(String)` | Oui | dim_employee.employee_display_name par run+version, N:0..1. |
| `team_key` | `Nullable(String)` | Oui | Équipe historiquement retenue si mapping et attribution validés. |
| `team_version_key` | `Nullable(String)` | Oui | Version de l'équipe pertinente. |
| `team_name` | `Nullable(String)` | Oui | dim_team.team_name par run+version, N:0..1. |
| `is_team_calculable` | `Bool` | Non | false pour rattachement à entrée/événement inconnu ou ambigu ; sinon true y compris KAM connue, indépendamment de son absence de cible D23. |
| `calculation_status` | `String` | Non | ready/partial/blocked/not_applicable ; ready n'efface pas les réserves distinctes de couverture. |
| `status_reason` | `Nullable(String)` | Oui | Motif explicite, stable et documenté ; plusieurs motifs séparés de façon canonique si nécessaire. |

**Jointures, identités et cardinalités :** fct_action expose les versions/périodes de l'action dans un run. Réduire d'abord à UNE tranche pertinente par action_key à input_cutoff_at, selon valid_from_at/valid_to_at et ordre source prouvé ; collisions contradictoires à même instant = blocked, jamais choix arbitraire par hash. Conserver le tombstone sélectionné avec is_source_deleted=true pour diagnostic, sans revenir à la version vivante antérieure. Puis LEFT JOIN dim_action_type/company/employee/team N:0..1 sur run+version. Type commercial depuis dossier prouvé N:0..1 ; aucun développement des dossiers d'un contact. Le type commercial absent du fait action est repris par LEFT JOIN à fct_opportunity_period sur run/opportunity_key et période contenant created_at pour une demande, actual_event_at pour une tenue, seulement si lien direct/prouvé. N:0..1 ; timestamp absent=>typeNULL, pas dernière version actuelle.

**Étapes du calcul :** Les types demande, Démo1, complément et annulation sont conservés. Une séance compte une fois ; complément n'est pas obligatoire. L'agenda ou le fait que la date prévue soit passée ne prouve pas une tenue. Sans preuve, is_realized_demo et nb_realized_demo_contribution=NULL, actual_event_at=NULL et missing_demo_completion_proof. Ne pas convertir le nombre de types60/68 en démos réellement tenues. La sélection de version utilise la borne de CONNAISSANCE input_cutoff_at (lecture passée corrigée), distincte de l'observation métier O qui filtre ensuite les événements. Les tombstones ne constituent ni annulation ni nonréalisation prouvées ; conserver diagnostic et contributionsNULL tant que la règle/observabilité correspondante n'est pas établie.

**Filtrage, paramètres et agrégation :** Deux dates de flux séparées : request_counting_at pour demandes, demo_counting_at pour séances. Période [from,to) et O éventuel ; équipe de l'action seulement si attribution calculable ; type commercial seulement pour dossiers reliés, les nonrattachés restent visibles séparément. Canal non transmis depuis contact sans convention et non disponible comme filtre officiel de cette famille. Cohorte de création dossier seulement si lien prouvé et besoin explicite, jamais création action rebaptisée cohorte. Compter action_key distinctes admissibles, ou sommer les contributions0/1 après unicité. Si la disponibilité de la preuve de tenue n'est pas déclarée complète pour le périmètre, nombre officiel de démos=NULL ; afficher séparément candidats, prouvés et inconnus, sans transformer l'absence de preuve en0. Les demandes et séances ne s'additionnent pas en volume de prospects ; Nb In demo vient de pipeline_periods au grain société. Le compteur de RDV utilise demo_session_key prouvée et unique : grouper les fiches d'une même séance avant compteur/attribution. Un représentant technique ne tranche pas un conflit d'équipes ; conflit=>ventilation indisponible. Aucun lien de séance prouvée=>compteurNULL.

**Matérialisation/histoire :** appliquer le contrat DTR commun ci-dessus : résultats complets du run, incremental append, engine MergeTree, ORDER BY(model_run_id,record_key), unique_key record_version_key, on_schema_change fail, full_refresh false et pas inserts_only. Les tables DTR conservent les anciens runs ; aucun filtre max de date métier ou limite à hier. Au premier chargement/cible vide, calculer l'ensemble ; en reprise, conserver seulement les clés du candidat absentes de la cible, sans modifier un payload existant.

**Contrat de chargement dbt :** une requête SELECT, CTE candidates explicite issue des transformations décrites. Chaque colonne du dictionnaire est produite exactement une fois. Terminer par la projection explicite de candidates ; sous `{% if is_incremental() %}`, LEFT ANTI JOIN de `{{ this }}` sur model_run_id et record_key. Tester absence de deux payloads différents pour une même clé/run AVANT chargement. Le unique_key de configuration assure le chemin de contrôle de schéma de l'adaptateur, pas la déduplication. Les entrées du run et le cutoff sont figés avant toute écriture future ; reprise du même run à empreinte inchangée.

**Construction/rafraîchissement :** après tous amonts du même run ; branches indépendantes parallélisables selon DAG. Exécution manuelle D29 ; fraîcheur de capture/publication déclarée, calcul puis tests/digest et publication contrôlée. Les requêtes de contrôle avant publication utilisent test_model_run_id. Aucun service/modèle n'est créé par la présente fiche.

**Tests/acceptation :** Trois versions d'une action=>une séance logique ; deux séances distinctes=>deux ; contact avec plusieurs dossiers ne multiplie pas l'action ; agenda passé seul=>réalisationNULL ; annulation prouvée=>pas tenue ; action sans lien dossier ne disparaît pas ; aucune somme partielle des seuls prouvés présentée comme total exhaustif. Contrôles communs ERROR de grain, hash, cardinalité et run ; WARN/indisponibilité pour manque descriptif ou preuve comme décrit dans le contrat. Tests métier ci-dessus planifiés, pas exécutés sur une implémentation inexistante.


<a id="dataset_sales_actions"></a>

### `dataset_sales_actions`

**Couche/module :** dataset de restitution, Reste du catalogue — demandes et rendez-vous de démo. **Finalité/consommateurs :** Hors trois PNG : demandes et séances de démo, répartition première/complémentaire si pertinente ; détail explicatif du compteur O04. Les cartes O04 officielles restent bloquées sans preuve/source suffisante, même si des actions planifiées existent.

**Grain métier et version :** exactement celui de `dtr_sales_actions` : tenant_id × action_key ; état corrigé pertinent d'une action logique dans le run. Une seule publication est visible ; identité et version sont conservées sans recalcul. Aucun total ni ligne artificielle n'est ajouté.

**Amont exact :** `{{ ref('dtr_sales_actions') }}` et `{{ ref('int_publication') }}`. **Destination :** `dtr_sales.dataset_sales_actions` ; fichier `dbt/models/reporting/datasets/dataset_sales_actions.sql`, YAML `dbt/models/reporting/datasets/_models.yml`.

| Colonne | Type ClickHouse | Nullable | Origine, formule et contraintes |
|---|---|---|---|
| `model_run_id` | `String` | Non | Projection sans changement de dtr_sales_actions.model_run_id. Identifiant de la recomposition complète et immuable ; hérité des entrées du même run. |
| `record_key` | `String` | Non | Projection sans changement de dtr_sales_actions.record_key. SHA256 de la liste ordonnée des éléments du grain indiquée dans la fiche ; sérialisation canonique commune, jamais simple concaténation ambiguë. |
| `record_version_key` | `String` | Non | Projection sans changement de dtr_sales_actions.record_version_key. SHA256 de (model_run_id, record_key). |
| `row_hash` | `String` | Non | Projection sans changement de dtr_sales_actions.row_hash. SHA256 du payload ordonné de la fiche, hors colonnes techniques communes. |
| `calculated_at` | `DateTime64(3, 'UTC')` | Non | Projection sans changement de dtr_sales_actions.calculated_at. Instant de calcul du run ; aucune substitution à une date métier. |
| `rule_version` | `String` | Non | Projection sans changement de dtr_sales_actions.rule_version. Version immuable des règles et référentiels utilisés par le run. |
| `input_cutoff_at` | `DateTime64(3, 'UTC')` | Non | Projection sans changement de dtr_sales_actions.input_cutoff_at. Borne des entrées figées ; héritée du manifeste de run. |
| `tenant_id` | `String` | Non | Projection sans changement de dtr_sales_actions.tenant_id. Tenant de l'action. |
| `action_key` | `String` | Non | Projection sans changement de dtr_sales_actions.action_key. Identité stable tenant+action ; le nombre de versions ne crée pas plusieurs séances. |
| `action_id` | `Int64` | Non | Projection sans changement de dtr_sales_actions.action_id. Identifiant Boond de l'action. |
| `source_action_version_key` | `String` | Non | Projection sans changement de dtr_sales_actions.source_action_version_key. Alias explicite de fct_action.action_version_key de la tranche retenue. |
| `action_state_valid_from_at` | `DateTime64(3, 'UTC')` | Non | Projection sans changement de dtr_sales_actions.action_state_valid_from_at. Alias explicite de fct_action.valid_from_at de la tranche retenue. |
| `action_state_valid_to_at` | `Nullable(DateTime64(3, 'UTC'))` | Oui | Projection sans changement de dtr_sales_actions.action_state_valid_to_at. Alias explicite de fct_action.valid_to_at de la tranche retenue. |
| `is_source_deleted` | `Bool` | Non | Projection sans changement de dtr_sales_actions.is_source_deleted. Marqueur de la dernière version pertinente ; sélectionner cette version AVANT de traiter la suppression. Aucune résurrection d'une ancienne version vivante. |
| `action_type_id` | `Nullable(Int64)` | Oui | Projection sans changement de dtr_sales_actions.action_type_id. Type source de l'action, distinct d'une preuve de réalisation. |
| `action_type_key` | `Nullable(String)` | Oui | Projection sans changement de dtr_sales_actions.action_type_key. Identité du type d'action. |
| `action_type_version_key` | `Nullable(String)` | Oui | Projection sans changement de dtr_sales_actions.action_type_version_key. Version de dim_action_type pertinente. |
| `action_type_label` | `Nullable(String)` | Oui | Projection sans changement de dtr_sales_actions.action_type_label. Libellé dim_action_type par run+version. |
| `company_key` | `Nullable(String)` | Oui | Projection sans changement de dtr_sales_actions.company_key. Société rattachée par lien direct/prouvé. |
| `company_version_key` | `Nullable(String)` | Oui | Projection sans changement de dtr_sales_actions.company_version_key. Version descriptive de la société. |
| `company_id` | `Nullable(Int64)` | Oui | Projection sans changement de dtr_sales_actions.company_id. Identifiant Boond de société. |
| `company_name` | `Nullable(String)` | Oui | Projection sans changement de dtr_sales_actions.company_name. dim_company.company_name. |
| `contact_id` | `Nullable(Int64)` | Oui | Projection sans changement de dtr_sales_actions.contact_id. Contact source ; un contact partagé ne prouve pas le dossier. |
| `opportunity_key` | `Nullable(String)` | Oui | Projection sans changement de dtr_sales_actions.opportunity_key. Dossier relié directement ou selon règle démontrée ; NULL si candidat/ambigu. |
| `opportunity_id` | `Nullable(Int64)` | Oui | Projection sans changement de dtr_sales_actions.opportunity_id. Identifiant du dossier prouvé, NULL sinon. |
| `link_status` | `String` | Non | Projection sans changement de dtr_sales_actions.link_status. fct_action.link_status : direct_opportunity/contact_only/missing/ambiguous ; seuls liens démontrés fournissent dossier. |
| `created_at` | `Nullable(DateTime64(3, 'UTC'))` | Oui | Projection sans changement de dtr_sales_actions.created_at. Création de la fiche action, distincte de l'agenda et d'un événement tenu. |
| `scheduled_start_at` | `Nullable(DateTime64(3, 'UTC'))` | Oui | Projection sans changement de dtr_sales_actions.scheduled_start_at. Début planifié de rendez-vous, sans preuve de tenue. |
| `scheduled_end_at` | `Nullable(DateTime64(3, 'UTC'))` | Oui | Projection sans changement de dtr_sales_actions.scheduled_end_at. Fin planifiée de rendez-vous. |
| `actual_event_at` | `Nullable(DateTime64(3, 'UTC'))` | Oui | Projection sans changement de dtr_sales_actions.actual_event_at. Date de tenue prouvée, jamais agenda automatiquement. |
| `realization_status` | `String` | Non | Projection sans changement de dtr_sales_actions.realization_status. fct_action.realization_status : unknown sans preuve ; held/planned/cancelled/no_show seulement si prouvé. Ne pas inventer domaine différent. |
| `is_demo_request` | `Nullable(Bool)` | Oui | Projection sans changement de dtr_sales_actions.is_demo_request. Action de demande admissible selon référentiel ; NULL si type non interprétable. |
| `is_realized_demo` | `Nullable(Bool)` | Oui | Projection sans changement de dtr_sales_actions.is_realized_demo. true/false seulement selon preuve de réalisation/nonréalisation ; NULL sans preuve. |
| `request_counting_at` | `Nullable(DateTime64(3, 'UTC'))` | Oui | Projection sans changement de dtr_sales_actions.request_counting_at. created_at pour action de demande type25 admise : demande enregistrée ; NULL si type/date manquant. |
| `demo_session_key` | `Nullable(String)` | Oui | Projection sans changement de dtr_sales_actions.demo_session_key. fct_action.demo_session_key : identité de séance tenue prouvée, NULL sans règle/preuve ; déduplication au-delà de l'identité de fiche action. |
| `demo_counting_at` | `Nullable(DateTime64(3, 'UTC'))` | Oui | Projection sans changement de dtr_sales_actions.demo_counting_at. actual_event_at seulement pour séance réellement tenue prouvée ; NULL sinon. |
| `nb_demo_request_contribution` | `Nullable(UInt8)` | Oui | Projection sans changement de dtr_sales_actions.nb_demo_request_contribution. 1 si demande admissible datée, 0 si autre action connue, NULL si type/date inconnus. |
| `nb_realized_demo_contribution` | `Nullable(UInt8)` | Oui | Projection sans changement de dtr_sales_actions.nb_realized_demo_contribution. NULL sans tenue/session prouvée. Pour séance prouvée :1 seulement sur représentant canonique de demo_session_key (action_key minimale pour décompte technique),0 autres fiches de même séance ; preuve d'attribution équipe univoque requise pour ventilation. |
| `sale_type_id` | `Nullable(Int64)` | Oui | Projection sans changement de dtr_sales_actions.sale_type_id. Type commercial du dossier dans le contexte retenu ; ne désigne pas la composante financière New/Upsell. |
| `sale_type_key` | `Nullable(String)` | Oui | Projection sans changement de dtr_sales_actions.sale_type_key. Identité stable du type commercial. |
| `sale_type_version_key` | `Nullable(String)` | Oui | Projection sans changement de dtr_sales_actions.sale_type_version_key. Version de dim_sale_type pertinente. |
| `sale_type_label` | `Nullable(String)` | Oui | Projection sans changement de dtr_sales_actions.sale_type_label. dim_sale_type.sale_type_label par run+version, N:0..1. |
| `employee_key` | `Nullable(String)` | Oui | Projection sans changement de dtr_sales_actions.employee_key. Identité stable du responsable retenu. |
| `employee_version_key` | `Nullable(String)` | Oui | Projection sans changement de dtr_sales_actions.employee_version_key. Version descriptive du responsable. |
| `employee_display_name` | `Nullable(String)` | Oui | Projection sans changement de dtr_sales_actions.employee_display_name. dim_employee.employee_display_name par run+version, N:0..1. |
| `team_key` | `Nullable(String)` | Oui | Projection sans changement de dtr_sales_actions.team_key. Équipe historiquement retenue si mapping et attribution validés. |
| `team_version_key` | `Nullable(String)` | Oui | Projection sans changement de dtr_sales_actions.team_version_key. Version de l'équipe pertinente. |
| `team_name` | `Nullable(String)` | Oui | Projection sans changement de dtr_sales_actions.team_name. dim_team.team_name par run+version, N:0..1. |
| `is_team_calculable` | `Bool` | Non | Projection sans changement de dtr_sales_actions.is_team_calculable. false pour rattachement à entrée/événement inconnu ou ambigu ; sinon true y compris KAM connue, indépendamment de son absence de cible D23. |
| `calculation_status` | `String` | Non | Projection sans changement de dtr_sales_actions.calculation_status. ready/partial/blocked/not_applicable ; ready n'efface pas les réserves distinctes de couverture. |
| `status_reason` | `Nullable(String)` | Oui | Projection sans changement de dtr_sales_actions.status_reason. Motif explicite, stable et documenté ; plusieurs motifs séparés de façon canonique si nécessaire. |

**SQL de projection complet :**

```sql
{{ config(materialized='view', schema='dtr_sales') }}

select
    d.model_run_id,
    d.record_key,
    d.record_version_key,
    d.row_hash,
    d.calculated_at,
    d.rule_version,
    d.input_cutoff_at,
    d.tenant_id,
    d.action_key,
    d.action_id,
    d.source_action_version_key,
    d.action_state_valid_from_at,
    d.action_state_valid_to_at,
    d.is_source_deleted,
    d.action_type_id,
    d.action_type_key,
    d.action_type_version_key,
    d.action_type_label,
    d.company_key,
    d.company_version_key,
    d.company_id,
    d.company_name,
    d.contact_id,
    d.opportunity_key,
    d.opportunity_id,
    d.link_status,
    d.created_at,
    d.scheduled_start_at,
    d.scheduled_end_at,
    d.actual_event_at,
    d.realization_status,
    d.is_demo_request,
    d.is_realized_demo,
    d.request_counting_at,
    d.demo_session_key,
    d.demo_counting_at,
    d.nb_demo_request_contribution,
    d.nb_realized_demo_contribution,
    d.sale_type_id,
    d.sale_type_key,
    d.sale_type_version_key,
    d.sale_type_label,
    d.employee_key,
    d.employee_version_key,
    d.employee_display_name,
    d.team_key,
    d.team_version_key,
    d.team_name,
    d.is_team_calculable,
    d.calculation_status,
    d.status_reason
from {{ ref('dtr_sales_actions') }} as d
inner join {{ ref('int_publication') }} as p
    on d.model_run_id = p.model_run_id
```

**Jointure/publication :** DTR N:1 vers la ligne unique du pointeur, égalité de run ; au bootstrap sans pointeur accepté, zéro ligne. Plus d'une ligne de pointeur est ERROR bloquante. Aucune dépendance inverse DTR→publication. Chaque requête BI conserve model_run_id et vérifie sa cohérence avec dataset_publication_status ; une page ne mélange pas plusieurs runs.

**Contrat BI et filtres :** Deux dates de flux séparées : request_counting_at pour demandes, demo_counting_at pour séances. Période [from,to) et O éventuel ; équipe de l'action seulement si attribution calculable ; type commercial seulement pour dossiers reliés, les nonrattachés restent visibles séparément. Canal non transmis depuis contact sans convention et non disponible comme filtre officiel de cette famille. Cohorte de création dossier seulement si lien prouvé et besoin explicite, jamais création action rebaptisée cohorte.

**Calculs restants en restitution :** Compter action_key distinctes admissibles, ou sommer les contributions0/1 après unicité. Si la disponibilité de la preuve de tenue n'est pas déclarée complète pour le périmètre, nombre officiel de démos=NULL ; afficher séparément candidats, prouvés et inconnus, sans transformer l'absence de preuve en0. Les demandes et séances ne s'additionnent pas en volume de prospects ; Nb In demo vient de pipeline_periods au grain société. Le compteur de RDV utilise demo_session_key prouvée et unique : grouper les fiches d'une même séance avant compteur/attribution. Un représentant technique ne tranche pas un conflit d'équipes ; conflit=>ventilation indisponible. Aucun lien de séance prouvée=>compteurNULL. Ils utilisent les champs détaillés, pas des ratios/quantiles locaux déjà agrégés. Les dates/arrondis/libellés/couleurs se formatent dans la BI ; les champsNULL restent indisponibles, jamais zéro d'affichage implicite. Avant agrégation, vérifier disponibilité PAR MESURE dans dataset_publication_status, y compris absence de lignes de détail.

**Test du dataset :** compter et comparer clés/payloads à la DTR sur le seul run publié ; égalité exacte attendue, ERROR sinon. Tester bootstrap vide, bascule vers nouveau run, réexécution sans modification, navigation tenant+clé+run et détection de publication différente entre requêtes. Rejouer les scénarios de filtres et d'agrégation de `dtr_sales_actions`, dont Trois versions d'une action=>une séance logique ; deux séances distinctes=>deux ; contact avec plusieurs dossiers ne multiplie pas l'action ; agenda passé seul=>réalisationNULL ; annulation prouvée=>pas tenue ; action sans lien dossier ne disparaît pas ; aucune somme partielle des seuls prouvés présentée comme total exhaustif.

**Rafraîchissement/limites :** la vue reflète le pointeur accepté sans horaire propre ; la fraîcheur dépend des sources, du run et de sa publication. Une règle/preuve manquante dans la DTR n'est pas réparée dans cette vue. Les blocages/limites sont ceux de la DTR et du dataset technique de disponibilité. Une relecture d'ancien run passe par la DTR explicite, sans changement du pointeur.


<a id="dtr_demo_intervals"></a>

### `dtr_demo_intervals`

**Couche/module :** DTR, Reste du catalogue — extension micro-funnel démo. **Finalité :** Hors trois PNG : extension U03 délais demande→séance et éventuellement séance→complément. Les faits génériques de pipeline/durée restent utilisables si cette extension n'est pas calculable.

**Grain métier :** tenant_id × demo_interval_key ; intervalle entre deux événements reliés d'un parcours établi. **Identité logique :** `record_key=H(tenant_id, demo_interval_key)`. **Grain historique/physique :** `(model_run_id,record_key)` ; version=H(run,key), une seule contribution par unité dans un run. Les clés métier et de dimensions sont conservées ci-dessous.

**Amont exact :** `{{ ref('fct_demo_interval') }}`, `{{ ref('dim_company') }}`, `{{ ref('dim_sale_type') }}`, `{{ ref('dim_team') }}`. **Destination :** `dtr_sales.dtr_demo_intervals` ; fichier `dbt/models/reporting/dtr/dtr_demo_intervals.sql`, YAML `dbt/models/reporting/dtr/_models.yml`.

| Colonne | Type ClickHouse | Nullable | Origine, formule et contraintes |
|---|---|---|---|
| `model_run_id` | `String` | Non | Identifiant de la recomposition complète et immuable ; hérité des entrées du même run. |
| `record_key` | `String` | Non | SHA256 de la liste ordonnée des éléments du grain indiquée dans la fiche ; sérialisation canonique commune, jamais simple concaténation ambiguë. |
| `record_version_key` | `String` | Non | SHA256 de (model_run_id, record_key). |
| `row_hash` | `String` | Non | SHA256 du payload ordonné de la fiche, hors colonnes techniques communes. |
| `calculated_at` | `DateTime64(3, 'UTC')` | Non | Instant de calcul du run ; aucune substitution à une date métier. |
| `rule_version` | `String` | Non | Version immuable des règles et référentiels utilisés par le run. |
| `input_cutoff_at` | `DateTime64(3, 'UTC')` | Non | Borne des entrées figées ; héritée du manifeste de run. |
| `tenant_id` | `String` | Non | Tenant du parcours établi. |
| `demo_interval_key` | `String` | Non | Identité logique de l'intervalle canonique ; jamais construit depuis simple ordre d'actions d'un contact ambigu. |
| `demo_journey_id` | `Nullable(String)` | Oui | Alias explicite de fct_demo_interval.demo_journey_key ; identité de parcours démontré, jamais id naturel inventé. |
| `start_action_id` | `Nullable(Int64)` | Oui | Action du premier événement, avec tenant. |
| `end_action_id` | `Nullable(Int64)` | Oui | Action du second événement. |
| `start_action_key` | `Nullable(String)` | Oui | Identité stable de l'action initiale. |
| `end_action_key` | `Nullable(String)` | Oui | Identité stable de l'action finale. |
| `opportunity_key` | `Nullable(String)` | Oui | Dossier prouvé du parcours. |
| `opportunity_id` | `Nullable(Int64)` | Oui | Identifiant Boond du dossier. |
| `company_key` | `Nullable(String)` | Oui | Société cohérente des événements reliés. |
| `company_version_key` | `Nullable(String)` | Oui | Version descriptive de société au contexte retenu. |
| `company_name` | `Nullable(String)` | Oui | dim_company.company_name. |
| `from_demo_step` | `Nullable(String)` | Oui | Étape de sous-parcours explicitement définie : demande/séance1/complément, sans les confondre avec phase commerciale. |
| `to_demo_step` | `Nullable(String)` | Oui | Étape finale explicitement définie. |
| `started_at` | `Nullable(DateTime64(3, 'UTC'))` | Oui | Événement initial admissible selon sa preuve et sa date. |
| `ended_at` | `Nullable(DateTime64(3, 'UTC'))` | Oui | Événement final admissible et relié. |
| `elapsed_duration_seconds` | `Nullable(Float64)` | Oui | (ended_at-started_at en ms)/1000 si les deux dates/événements et leur lien sont admissibles. |
| `elapsed_duration_days` | `Nullable(Float64)` | Oui | elapsed_duration_seconds/86400 ; NULL sans intervalle démontré. |
| `time_basis` | `String` | Non | Provenance des événements et dates, sans assimilation agenda/tenue. |
| `link_status` | `String` | Non | proven/candidate/ambiguous/missing selon le chaînage. |
| `is_interval_calculable` | `Bool` | Non | link_status prouvé ET bornes connues/ordonnées ET événements admissibles ET statut de mesure valide ; false sinon. |
| `is_team_filter_available` | `Bool` | Non | false dans cette v1 sans duration_team_rule de sous-parcours explicitement validée ; team_key descriptive n'autorise pas le filtre. |
| `sale_type_id` | `Nullable(Int64)` | Oui | Type commercial du dossier dans le contexte retenu ; ne désigne pas la composante financière New/Upsell. |
| `sale_type_key` | `Nullable(String)` | Oui | Identité stable du type commercial. |
| `sale_type_version_key` | `Nullable(String)` | Oui | Version de dim_sale_type pertinente. |
| `sale_type_label` | `Nullable(String)` | Oui | dim_sale_type.sale_type_label par run+version, N:0..1. |
| `team_key` | `Nullable(String)` | Oui | Équipe proposée/prouvée seulement si attribution spécifique établie. |
| `team_version_key` | `Nullable(String)` | Oui | Version pertinente de l'équipe. |
| `team_name` | `Nullable(String)` | Oui | dim_team.team_name. |
| `calculation_status` | `String` | Non | ready/partial/blocked/not_applicable ; ready n'efface pas les réserves distinctes de couverture. |
| `status_reason` | `Nullable(String)` | Oui | Motif explicite, stable et documenté ; plusieurs motifs séparés de façon canonique si nécessaire. |

**Jointures, identités et cardinalités :** fct_demo_interval → dimensions N:0..1 par run+version. Les start_action_key/end_action_key sont des rôles de lineage déjà publiés dans le fait ; aucun JOIN aux actions n'est nécessaire dans cette DTR. Le détail d'une action peut être consulté séparément au même run, sans multiplier les intervalles.

**Étapes du calcul :** Projection des seuls intervalles démontrés, ou candidats avec is_interval_calculable=false et duréesNULL si le fait conserve ces candidats. Une table vide ne prouve pas qu'aucun délai existe : lire la disponibilité de la famille dans le manifeste de run. Ne pas fabriquer un parcours par ordre chronologique si plusieurs dossiers ou demandes sont possibles. Une suppression/absence d'action ne devient pas durée0.

**Filtrage, paramètres et agrégation :** Sous-étapes de début/fin, période d'entrée d'intervalle [from,to), observation O avec ended_at<=O pour terminés. Type commercial et équipe uniquement si lien/attribution prouvés. Canal et seuil sans contrat métier ici, donc indisponibles par défaut. Ne pas confondre durée séance=endDate-startDate de l'agenda avec attente entre événements de sous-parcours. Distributions/médiane/P90 depuis elapsed_duration_days des intervalles calculables après filtres. Compter intervalles distincts et dossiers distincts séparément. Ne pas moyenner les quantiles de groupes ni additionner délai de phase commerciale et délai du sous-parcours comme même mesure.

**Matérialisation/histoire :** appliquer le contrat DTR commun ci-dessus : résultats complets du run, incremental append, engine MergeTree, ORDER BY(model_run_id,record_key), unique_key record_version_key, on_schema_change fail, full_refresh false et pas inserts_only. Les tables DTR conservent les anciens runs ; aucun filtre max de date métier ou limite à hier. Au premier chargement/cible vide, calculer l'ensemble ; en reprise, conserver seulement les clés du candidat absentes de la cible, sans modifier un payload existant.

**Contrat de chargement dbt :** une requête SELECT, CTE candidates explicite issue des transformations décrites. Chaque colonne du dictionnaire est produite exactement une fois. Terminer par la projection explicite de candidates ; sous `{% if is_incremental() %}`, LEFT ANTI JOIN de `{{ this }}` sur model_run_id et record_key. Tester absence de deux payloads différents pour une même clé/run AVANT chargement. Le unique_key de configuration assure le chemin de contrôle de schéma de l'adaptateur, pas la déduplication. Les entrées du run et le cutoff sont figés avant toute écriture future ; reprise du même run à empreinte inchangée.

**Construction/rafraîchissement :** après tous amonts du même run ; branches indépendantes parallélisables selon DAG. Exécution manuelle D29 ; fraîcheur de capture/publication déclarée, calcul puis tests/digest et publication contrôlée. Les requêtes de contrôle avant publication utilisent test_model_run_id. Aucun service/modèle n'est créé par la présente fiche.

**Tests/acceptation :** Chaînage ambigu=>duréeNULL ; ordre de dates invalide=>échec calcul bloquant ; mêmes actions révisées ne dupliquent pas intervalle ; plusieurs séances admissibles conservent identités distinctes selon règle ; absence de preuve de tenue ne produit pas un délai tenu ; intervalle absent sous source inconnue n'est pas0. Contrôles communs ERROR de grain, hash, cardinalité et run ; WARN/indisponibilité pour manque descriptif ou preuve comme décrit dans le contrat. Tests métier ci-dessus planifiés, pas exécutés sur une implémentation inexistante.


<a id="dataset_demo_intervals"></a>

### `dataset_demo_intervals`

**Couche/module :** dataset de restitution, Reste du catalogue — extension micro-funnel démo. **Finalité/consommateurs :** Hors trois PNG : extension U03 délais demande→séance et éventuellement séance→complément. Les faits génériques de pipeline/durée restent utilisables si cette extension n'est pas calculable.

**Grain métier et version :** exactement celui de `dtr_demo_intervals` : tenant_id × demo_interval_key ; intervalle entre deux événements reliés d'un parcours établi. Une seule publication est visible ; identité et version sont conservées sans recalcul. Aucun total ni ligne artificielle n'est ajouté.

**Amont exact :** `{{ ref('dtr_demo_intervals') }}` et `{{ ref('int_publication') }}`. **Destination :** `dtr_sales.dataset_demo_intervals` ; fichier `dbt/models/reporting/datasets/dataset_demo_intervals.sql`, YAML `dbt/models/reporting/datasets/_models.yml`.

| Colonne | Type ClickHouse | Nullable | Origine, formule et contraintes |
|---|---|---|---|
| `model_run_id` | `String` | Non | Projection sans changement de dtr_demo_intervals.model_run_id. Identifiant de la recomposition complète et immuable ; hérité des entrées du même run. |
| `record_key` | `String` | Non | Projection sans changement de dtr_demo_intervals.record_key. SHA256 de la liste ordonnée des éléments du grain indiquée dans la fiche ; sérialisation canonique commune, jamais simple concaténation ambiguë. |
| `record_version_key` | `String` | Non | Projection sans changement de dtr_demo_intervals.record_version_key. SHA256 de (model_run_id, record_key). |
| `row_hash` | `String` | Non | Projection sans changement de dtr_demo_intervals.row_hash. SHA256 du payload ordonné de la fiche, hors colonnes techniques communes. |
| `calculated_at` | `DateTime64(3, 'UTC')` | Non | Projection sans changement de dtr_demo_intervals.calculated_at. Instant de calcul du run ; aucune substitution à une date métier. |
| `rule_version` | `String` | Non | Projection sans changement de dtr_demo_intervals.rule_version. Version immuable des règles et référentiels utilisés par le run. |
| `input_cutoff_at` | `DateTime64(3, 'UTC')` | Non | Projection sans changement de dtr_demo_intervals.input_cutoff_at. Borne des entrées figées ; héritée du manifeste de run. |
| `tenant_id` | `String` | Non | Projection sans changement de dtr_demo_intervals.tenant_id. Tenant du parcours établi. |
| `demo_interval_key` | `String` | Non | Projection sans changement de dtr_demo_intervals.demo_interval_key. Identité logique de l'intervalle canonique ; jamais construit depuis simple ordre d'actions d'un contact ambigu. |
| `demo_journey_id` | `Nullable(String)` | Oui | Projection sans changement de dtr_demo_intervals.demo_journey_id. Alias explicite de fct_demo_interval.demo_journey_key ; identité de parcours démontré, jamais id naturel inventé. |
| `start_action_id` | `Nullable(Int64)` | Oui | Projection sans changement de dtr_demo_intervals.start_action_id. Action du premier événement, avec tenant. |
| `end_action_id` | `Nullable(Int64)` | Oui | Projection sans changement de dtr_demo_intervals.end_action_id. Action du second événement. |
| `start_action_key` | `Nullable(String)` | Oui | Projection sans changement de dtr_demo_intervals.start_action_key. Identité stable de l'action initiale. |
| `end_action_key` | `Nullable(String)` | Oui | Projection sans changement de dtr_demo_intervals.end_action_key. Identité stable de l'action finale. |
| `opportunity_key` | `Nullable(String)` | Oui | Projection sans changement de dtr_demo_intervals.opportunity_key. Dossier prouvé du parcours. |
| `opportunity_id` | `Nullable(Int64)` | Oui | Projection sans changement de dtr_demo_intervals.opportunity_id. Identifiant Boond du dossier. |
| `company_key` | `Nullable(String)` | Oui | Projection sans changement de dtr_demo_intervals.company_key. Société cohérente des événements reliés. |
| `company_version_key` | `Nullable(String)` | Oui | Projection sans changement de dtr_demo_intervals.company_version_key. Version descriptive de société au contexte retenu. |
| `company_name` | `Nullable(String)` | Oui | Projection sans changement de dtr_demo_intervals.company_name. dim_company.company_name. |
| `from_demo_step` | `Nullable(String)` | Oui | Projection sans changement de dtr_demo_intervals.from_demo_step. Étape de sous-parcours explicitement définie : demande/séance1/complément, sans les confondre avec phase commerciale. |
| `to_demo_step` | `Nullable(String)` | Oui | Projection sans changement de dtr_demo_intervals.to_demo_step. Étape finale explicitement définie. |
| `started_at` | `Nullable(DateTime64(3, 'UTC'))` | Oui | Projection sans changement de dtr_demo_intervals.started_at. Événement initial admissible selon sa preuve et sa date. |
| `ended_at` | `Nullable(DateTime64(3, 'UTC'))` | Oui | Projection sans changement de dtr_demo_intervals.ended_at. Événement final admissible et relié. |
| `elapsed_duration_seconds` | `Nullable(Float64)` | Oui | Projection sans changement de dtr_demo_intervals.elapsed_duration_seconds. (ended_at-started_at en ms)/1000 si les deux dates/événements et leur lien sont admissibles. |
| `elapsed_duration_days` | `Nullable(Float64)` | Oui | Projection sans changement de dtr_demo_intervals.elapsed_duration_days. elapsed_duration_seconds/86400 ; NULL sans intervalle démontré. |
| `time_basis` | `String` | Non | Projection sans changement de dtr_demo_intervals.time_basis. Provenance des événements et dates, sans assimilation agenda/tenue. |
| `link_status` | `String` | Non | Projection sans changement de dtr_demo_intervals.link_status. proven/candidate/ambiguous/missing selon le chaînage. |
| `is_interval_calculable` | `Bool` | Non | Projection sans changement de dtr_demo_intervals.is_interval_calculable. link_status prouvé ET bornes connues/ordonnées ET événements admissibles ET statut de mesure valide ; false sinon. |
| `is_team_filter_available` | `Bool` | Non | Projection sans changement de dtr_demo_intervals.is_team_filter_available. false dans cette v1 sans duration_team_rule de sous-parcours explicitement validée ; team_key descriptive n'autorise pas le filtre. |
| `sale_type_id` | `Nullable(Int64)` | Oui | Projection sans changement de dtr_demo_intervals.sale_type_id. Type commercial du dossier dans le contexte retenu ; ne désigne pas la composante financière New/Upsell. |
| `sale_type_key` | `Nullable(String)` | Oui | Projection sans changement de dtr_demo_intervals.sale_type_key. Identité stable du type commercial. |
| `sale_type_version_key` | `Nullable(String)` | Oui | Projection sans changement de dtr_demo_intervals.sale_type_version_key. Version de dim_sale_type pertinente. |
| `sale_type_label` | `Nullable(String)` | Oui | Projection sans changement de dtr_demo_intervals.sale_type_label. dim_sale_type.sale_type_label par run+version, N:0..1. |
| `team_key` | `Nullable(String)` | Oui | Projection sans changement de dtr_demo_intervals.team_key. Équipe proposée/prouvée seulement si attribution spécifique établie. |
| `team_version_key` | `Nullable(String)` | Oui | Projection sans changement de dtr_demo_intervals.team_version_key. Version pertinente de l'équipe. |
| `team_name` | `Nullable(String)` | Oui | Projection sans changement de dtr_demo_intervals.team_name. dim_team.team_name. |
| `calculation_status` | `String` | Non | Projection sans changement de dtr_demo_intervals.calculation_status. ready/partial/blocked/not_applicable ; ready n'efface pas les réserves distinctes de couverture. |
| `status_reason` | `Nullable(String)` | Oui | Projection sans changement de dtr_demo_intervals.status_reason. Motif explicite, stable et documenté ; plusieurs motifs séparés de façon canonique si nécessaire. |

**SQL de projection complet :**

```sql
{{ config(materialized='view', schema='dtr_sales') }}

select
    d.model_run_id,
    d.record_key,
    d.record_version_key,
    d.row_hash,
    d.calculated_at,
    d.rule_version,
    d.input_cutoff_at,
    d.tenant_id,
    d.demo_interval_key,
    d.demo_journey_id,
    d.start_action_id,
    d.end_action_id,
    d.start_action_key,
    d.end_action_key,
    d.opportunity_key,
    d.opportunity_id,
    d.company_key,
    d.company_version_key,
    d.company_name,
    d.from_demo_step,
    d.to_demo_step,
    d.started_at,
    d.ended_at,
    d.elapsed_duration_seconds,
    d.elapsed_duration_days,
    d.time_basis,
    d.link_status,
    d.is_interval_calculable,
    d.is_team_filter_available,
    d.sale_type_id,
    d.sale_type_key,
    d.sale_type_version_key,
    d.sale_type_label,
    d.team_key,
    d.team_version_key,
    d.team_name,
    d.calculation_status,
    d.status_reason
from {{ ref('dtr_demo_intervals') }} as d
inner join {{ ref('int_publication') }} as p
    on d.model_run_id = p.model_run_id
```

**Jointure/publication :** DTR N:1 vers la ligne unique du pointeur, égalité de run ; au bootstrap sans pointeur accepté, zéro ligne. Plus d'une ligne de pointeur est ERROR bloquante. Aucune dépendance inverse DTR→publication. Chaque requête BI conserve model_run_id et vérifie sa cohérence avec dataset_publication_status ; une page ne mélange pas plusieurs runs.

**Contrat BI et filtres :** Sous-étapes de début/fin, période d'entrée d'intervalle [from,to), observation O avec ended_at<=O pour terminés. Type commercial et équipe uniquement si lien/attribution prouvés. Canal et seuil sans contrat métier ici, donc indisponibles par défaut. Ne pas confondre durée séance=endDate-startDate de l'agenda avec attente entre événements de sous-parcours.

**Calculs restants en restitution :** Distributions/médiane/P90 depuis elapsed_duration_days des intervalles calculables après filtres. Compter intervalles distincts et dossiers distincts séparément. Ne pas moyenner les quantiles de groupes ni additionner délai de phase commerciale et délai du sous-parcours comme même mesure. Ils utilisent les champs détaillés, pas des ratios/quantiles locaux déjà agrégés. Les dates/arrondis/libellés/couleurs se formatent dans la BI ; les champsNULL restent indisponibles, jamais zéro d'affichage implicite. Avant agrégation, vérifier disponibilité PAR MESURE dans dataset_publication_status, y compris absence de lignes de détail.

**Test du dataset :** compter et comparer clés/payloads à la DTR sur le seul run publié ; égalité exacte attendue, ERROR sinon. Tester bootstrap vide, bascule vers nouveau run, réexécution sans modification, navigation tenant+clé+run et détection de publication différente entre requêtes. Rejouer les scénarios de filtres et d'agrégation de `dtr_demo_intervals`, dont Chaînage ambigu=>duréeNULL ; ordre de dates invalide=>échec calcul bloquant ; mêmes actions révisées ne dupliquent pas intervalle ; plusieurs séances admissibles conservent identités distinctes selon règle ; absence de preuve de tenue ne produit pas un délai tenu ; intervalle absent sous source inconnue n'est pas0.

**Rafraîchissement/limites :** la vue reflète le pointeur accepté sans horaire propre ; la fraîcheur dépend des sources, du run et de sa publication. Une règle/preuve manquante dans la DTR n'est pas réparée dans cette vue. Les blocages/limites sont ceux de la DTR et du dataset technique de disponibilité. Une relecture d'ancien run passe par la DTR explicite, sans changement du pointeur.


### Mapping des statuts de calcul vers la disponibilité publique

Les datasets métier ne supposent aucune colonne `availability_status`/`availability_reason` dans les faits. Le runner prépare le résumé de publication PAR MESURE depuis les contrôles et les `calculation_status/status_reason`, puis la vue technique `dataset_publication_status` l'expose. La décision suit cet ordre pour chaque mesure, pas pour toute la ligne :

1. Mesure hors sujet pour le périmètre : not_applicable.
2. Règle nécessaire manquante (unité, coefficient, périmètre de cible, parcours, mapping ou filtre demandé) : blocked_definition, motif exact.
3. Horizon de cohorte non atteint : non_mature, taux NULL.
4. Preuve nécessaire absente (tenue, montant signé, devise source) : blocked_evidence.
5. Horizon atteint mais état/période non reconstructible à l'observation : not_observable.
6. Résultat limité à une population connue ou contribution partielle explicitement exploitable : partial et couverture déclarée.
7. Tous les prérequis/contrôles nécessaires satisfaits : available.

`calculation_status=ready` est nécessaire mais ne suffit pas pour available sans couverture validée ; partial reste partial ; blocked se classe blocked_definition ou blocked_evidence selon la cause et not_applicable conserve son sens. Les paramètres UI ajoutent une disponibilité de requête (par exemple missing_threshold) sans réécrire la publication. Les raisons internes éventuelles sont normalisées vers les codes publics du document 01 : missing_demo_completion_proof, unconfirmed_amount_unit, unconfirmed_currency, missing_target_scope, missing_probability_rule, missing_team_mapping, missing_channel_rule, missing_duration_team_rule, missing_threshold, unknown_event_date, incomplete_history, source_coverage_unconfirmed. Un défaut d'étiquette peut laisser un volume calculable ; un défaut de preuve monétaire bloque le montant sans transformer le volume en NULL.

### Requêtes BI de référence et opérations complexes

Ces exemples sont des contrats de calcul à implémenter et tester, pas des requêtes métier déjà exécutées. Les projections de modèles dbt restent explicites et sans wildcard.

**Durées — mêmes passages, deux populations.** Après contrôle de disponibilité et préparation des paramètres UTC, projeter depuis dataset_stage_visits les champs nécessaires (run,tenant,visit,opportunity,entered/exited,observation_end,coverage,completed_duration_days) et filtrer directement entered_at dans l'intervalle d'entrée choisi. Préparer dans une CTE :
- completed : entrée connue<=O, sortie connue<=O et continuité entre les deux ;
- current : entrée connue<=O, sortie absente ou>O et continuité observée jusqu'à O ;
- not_observable : bornes/couverture insuffisantes, notamment observation_end_at<=O sans sortie métier ;
- hors population : entrée future ; début inconnu conservé dans couverture, pas daté artificiellement.

```sql
-- Extrait d'agrégation ; measured est la CTE explicite définie ci-dessus.
select
    model_run_id,
    quantilesExactInclusive(0.5, 0.9)(completed_duration_days) as completed_quantiles
from measured
where observation_population = 'completed'
group by model_run_id
```

L'ancienneté est préparée dans la CTE comme `dateDiff('millisecond', entered_at, observation_at)/86400000.0` pour les en-cours admissibles uniquement. Le seuil compare cette valeur au paramètre préparé ; seuilNULL=>alerteNULL+missing_threshold. Médiane d'ancienneté et effectif au-delà du seuil utilisent exactement les mêmes filtres/populations ; distribution des terminés et distribution des en-cours restent séparées. D26 retient désormais21jours comme défaut de case et classes continues[0,7),[7,14),[14,30),[30,+inf) ; ce choix délégué ne provient pas d’une preuve empirique. En particulier, des classes de jours continus doivent avoir des bornes numériques continues explicites, sans trou artificiel entre7 et8.

**Cohortes — calcul compatible des dénominateurs.** Pour une sélection tenant/mois/type/définition/horizon, appliquer ensuite les filtres équipe/canal autorisés. Conserver cohort_mature_at préparé avant ces filtres. Au regroupement, si O<max(cohort_mature_at), toutes proportions de cette cellule sont NULL. Sinon Nbase=sum(nb_cohort_membership), puis Nissue depuis chaque contribution ; taux=Nissue/Nbase si Nbase>0. Exposer abandoned/unqualified/unknown et couverture. Ne jamais diviser ouvert/gagné/perdu par leur seule somme.

```text
pour chaque groupe compatible (run, tenant, cohort_month, sale_type_id, définition, horizon_days):
    n_base := somme(nb_cohort_membership)
    entière_mature := observation_at >= maximum(cohort_mature_at)
    si non entière_mature:
        six effectifs d'issue et six ratios := NULL ; disponibilité := non_mature
    sinon:
        conserver une catégorie par membre connu ; non observable => unknown
        vérifier somme(six catégories) = n_base
        ratio_issue := n_issue / n_base si n_base>0 ; sinon NULL
```

**MRR — préagréger avant de rapprocher.** Sélectionner le même run ; réduire les lignes d'abonnement par tenant/company/clôture, avec montants officiels NULL si une contribution nécessaire est inconnue. Mettre N-1/N au grain société/mois par FULL OUTER JOIN. Pivoter les mouvements par company/mois en six contributions financières (New,Upsell,départ,baisse,autre,statut), puis LEFT JOIN 1:0..1 aux clôtures. La présence/absence d'un côté n'autorise0/inactif qu'avec couverture prouvée. Vérifier delta=New+Upsell-départ-baisse+autre. Ajouter une seule fois chacune des deux composantes de croissance. Les identifiants de lignes ne deviennent pas la clé de cette DTR et aucun montant société n'est répété sur ses liens.

**Tunnel — population et transitions.** Une ligne par dossier/étape cible dans une définition activée. Pour le nombre ayant atteint l'étape, utiliser la preuve d'atteinte<=O, pas l'état courant. Pour A→B, prendre une définition stage_transition autorisant un ancrage admissible et rechercher B APRÈS cet ancrage ; les répétitions sont réduites selon cette définition avant jointure au funnel. Si la règle des réentrées est manquante, tauxNULL+blocked_definition ; on ne choisit pas arbitrairement le premier/dernier ancrage. Un B antérieur à A ne valide pas la transition, même s'il peut prouver que B a été atteint dans le parcours global.

**Actions — version pertinente puis événement.** La vue fct_action expose plusieurs versions/périodes par action. Sélectionner l'intervalle pertinent à la borne de connaissance du run, après résolution des collisions, et conserver le tombstone éventuel ; ne pas rechercher d'abord une version vivante. Une seule action_key dans DTR. Ensuite seulement filtrer request_counting_at ou demo_counting_at par période et observation métier. Sans preuve de tenue, contribution démoNULL et disponibilité blocked_evidence, même si une action porte un type Démo et une date passée.

### Contrôles communs et critères de livraison de cette couche

- ERROR bloquant publication : unicité run+record_key, cohérence hash/grain, clés techniques non NULL, unicité pointeur, un seul run dans chaque jointure, cardinalité N:0..1, contributions multipliées, intervalles négatifs/chevauchants incompatibles, réconciliation calculable non nulle ou incohérence des dénominateurs.
- ERROR de contrat si une mesure bloquée est publiée disponible, si un total financier ignore des NULL nécessaires, si un horizon immature devient0, si un seuil absent génère une alerte, si un agenda devient preuve de tenue ou si New total et ses composantes sont additionnés.
- WARN avec disponibilité explicite pour un descriptif non mappé ou un volume partiel documenté ; si la mesure dépend du mapping/preuve, elle reste bloquée. Une publication d'un run contenant des mesures bloquées est permise seulement si ces disponibilités sont enregistrées et respectées par la BI.
- Premier chargement : tous résultats du run acceptés au grain ; réexécution de la même empreinte : aucune ligne supplémentaire ; reprise partielle : compléter les clés manquantes puis vérifier digest/comptages ; correction tardive : nouveau run complet et ancien toujours consultable ; bascule de publication après tests seulement.
- Les mesures de performance restent à exécuter sur l'implémentation : temps, lignes/octets lus, plan. Aucun benchmark ni test de transformation dbt n'a été exécuté pour ces vingt fiches pendant la rédaction.




## E. Deux modèles techniques de publication et disponibilité

Ces objets complètent les 71 modèles métier. Ils ne changent ni leurs grains ni leurs KPI.

<a id="int_publication"></a>

### int_publication

**Couche/module/finalité** : intermédiaire de contrôle, dwh_common, pointeur unique vers un run candidat entièrement construit et testé. Fichier futur `dbt/models/intermediate/common/int_publication.sql`, YAML `_models.yml` ; tag `publication` seul, matérialisation `table`, moteur MergeTree, ORDER BY tuple(), sans partition/TTL. Actualisation uniquement par commande isolée après validation du manifest ; remplacement via matérialisation dbt et échange Atomic. Aucun DDL manuel.

**Grain et clés** : zéro ligne au bootstrap initial, exactement une ligne en publication. publication_key unique ; model_run_id pointe vers un snapshot complet présent dans toutes les familles requises ou explicitement vides/non calculables selon leur statut. Pas de colonnes R supplémentaires : ce contrôle n'est pas un registre de résultats métier. Les manifests conservent son historique de publication ; les runs métier restent persistés.

| Colonne | Type | NULL | Description / origine / contrainte |
|---|---|---|---|
| model_run_id | String | non | Run candidat validé ; empreinte immuable correspondant aux entrées, règles et paramètres, pas identifiant aléatoire d'une tentative. |
| publication_key | String | non | SHA256 de run et published_at ; identifie la bascule. |
| published_at | DateTime64(3,'UTC') | non | Var publication_at figée après tests ; pas une date métier. |
| input_cutoff_at | DateTime64(3,'UTC') | non | Cutoff d'import du run, distinct de couverture métier. |
| rule_version | String | non | Empreinte code/règles du run accepté. |
| quality_json | String | non | Tableau JSON validé, une entrée par measure_id du registre ci-dessous, y compris familles sans aucune ligne de détail. |

**Amont et jointures** : pas de ref vers les modèles métier ; le runner vérifie le manifest externe candidat et passe les constantes validées. Cette absence de dépendance évite une publication involontaire via sélecteur de descendants. Les datasets joignent ce pointeur aux DTR sur model_run_id, relation N:1 ; plus d'une ligne de pointeur est une erreur bloquante.

**Calcul/pseudocode** : SELECT de constantes typées rendues par une macro ch_literal qui échappe les chaînes selon ClickHouse (apostrophes et antislashs), jamais concaténation SQL non échappée. Bootstrap : mêmes colonnes typées mais filtre constant0, uniquement si relation absente. publication_model_run_id=null est interdit par runner si un pointeur existe. Publication : vérifier candidat complet, schema/nb_keys/digest/tests et quality_json, puis remplacer ce seul modèle via dbt. Snapshot métier antérieur et pointeur précédent restent disponibles pour rollback documenté dans le manifest.

**Qualité JSON** : chaque entrée porte measure_id String,dataset_family String,availability_status String,availability_reason Nullable(String),coverage_status String,nb_expected Nullable(UInt64),nb_known Nullable(UInt64),data_coverage_end_at Nullable(String ISO UTC ms). NULL est écrit comme JSON null, pas chaîne «null». Champs manquants/type invalide/doublon ID : erreur bloquante. Un blocked_definition/blocked_evidence déclaré est un résultat valide de disponibilité ; il n'autorise pas un zéro financier.

**Tests/acceptation** : 0 ligne seulement bootstrap, puis1 ; non NULL clés ; run accepté complet ; statut de chaque mesure attendu présent exactement1fois ; pas de publication si incohérence/échec ; reprise d'une bascule après interruption selon pointeur réellement observé. Aucun de ces tests d'écriture n'a été exécuté.

<a id="dataset_publication_status"></a>

### dataset_publication_status

**Couche/finalité** : dataset technique dtr_sales, fichier futur `dbt/models/reporting/datasets/dataset_publication_status.sql`, YAML `_models.yml`, tag dataset, matérialisation view. Grain publication/model_run_id × measure_id ; unicité du tuple. Expose les statuts même si un dataset de détail est vide, sans ligne artificielle dans celui-ci. Rafraîchissement par lecture du pointeur, aucune capture métier supplémentaire.

| Colonne | Type | NULL | Description / origine / règle |
|---|---|---|---|
| model_run_id | String | non | int_publication.model_run_id. |
| publication_key | String | non | int_publication.publication_key ; détecte une bascule entre plusieurs requêtes d'une page. |
| published_at | DateTime64(3,'UTC') | non | Instant de publication. |
| input_cutoff_at | DateTime64(3,'UTC') | non | Cutoff des entrées du run publié. |
| rule_version | String | non | Version de règles/calcul. |
| measure_id | String | non | Identifiant du registre technique de disponibilité ci-dessous. |
| dataset_family | String | non | Famille métier cible ; ne modifie pas le grain de ses lignes. |
| availability_status | String | non | Domaine A.4/01 ; même statut que le contrôle candidat. |
| availability_reason | Nullable(String) | oui | Code de motif ou NULL si available ; pas chaîne vide. |
| coverage_status | String | non | complete/partial/unconfirmed/not_applicable, indépendamment de maturité. |
| nb_expected | Nullable(UInt64) | oui | Population attendue quand déterminable ; pas0 par défaut. |
| nb_known | Nullable(UInt64) | oui | Population avec preuve/mesure admissible ; NULL si non déterminable. |
| data_coverage_end_at | Nullable(DateTime64(3,'UTC')) | oui | Dernière borne de couverture déclarée et justifiée ; max(updateDate) ne la fournit pas. |

**Amont/calcul** : ref('int_publication') uniquement ; ARRAY JOIN du tableau quality_json, puis extraction typée des champs. Une entrée=>une ligne, pas de jointure avec les faits. Les valeurs numériques nulles sont extraites en Nullable(UInt64), pas JSONExtractUInt qui remplacerait une absence par0. Les dates JSON sont parsées UTC avec validation ; les chaînes «null» sont interdites en amont. Les 13 colonnes de sortie ci-dessus sont explicitement projetées.

**Contrat BI** : consulter une fois par page et vérifier model_run_id sur chaque résultat métier ; lire publication_key dans dataset_publication_status avant et après les requêtes, et recharger l'ensemble si changement. Mesure indisponible=>afficher motif, pas0. Mesure available avec nb_expected=0 connu=>zéro possible pour un compteur, ratio NULL si dénominateur0. Bootstrap sans pointeur=>«Aucune publication disponible», pas tableau chiffré à0. Une relecture de run ancien utilise les DTR et son manifeste accepté, pas un filtre sur les vues courantes.

**Registre fermé de disponibilité v0.1** (famille à gauche ; IDs à droite, une entrée par ID, sous-mesures possibles ultérieurement avec version du registre) :

| Famille | measure_id attendus |
|---|---|
| sales_objectives_month | objectives.mrr_signed ; objectives.pipeline_generated ; objectives.pipeline_weighted ; objectives.demos |
| funnel_progress | funnel.opportunities ; funnel.transition ; funnel.global |
| company_mrr_month | revenue.active_mrr ; revenue.new_mrr ; revenue.churn_mrr ; revenue.active_clients |
| stage_visits | durations.completed ; durations.current_age ; durations.threshold |
| cohort_outcomes | cohorts.outcomes |
| pipeline_periods | pipeline.open_count ; pipeline.open_amount ; pipeline.weighted_amount ; pipeline.coverage ; pipeline.stagnation ; pipeline.in_demo |
| sales_events | events.generated_count ; events.generated_amount ; events.signed_count ; events.signed_mrr ; events.cycle |
| sales_actions | actions.requests ; actions.realized_demos |
| demo_intervals | demo_intervals.duration |
| opportunity_timeline | timeline.detail |

Le registre contient30 IDs. L'extraction ne renomme pas ces IDs en libellés métier : les libellés de restitution restent dans la configuration du dashboard. Une raison précise manquante pour une mesure indisponible, un comptage incohérent ou une différence de run avec les familles publiées bloque l'acceptation. Les moyennes/ratios ne se recalculent jamais depuis ce dataset de contrôle.

## F. Registre des adaptations et lecture de la v0.2

Les 71 modèles métier +2 techniques =73 fiches. Les propositions techniques (snapshot complet par run, bases et suffixes, horizon Paris, durée en secondes écoulées, maturité avant équipe/canal, fenêtre48 h) sont explicites et ne sont pas enregistrées comme anciennes décisions utilisateur. Aucun fichier SQL/YAML de modèle n'est créé.

Les anciens G01–G10 sont clôturés par01§7 ; les preuves manquantes ont un comportement volontairement indisponible, aucun arbitrage métier n’est laissé à l’implémentation. Le catalogue spécifie le comportement en leur absence, pas une autorisation de compléter le métier par intuition. Les attendus sans formule (M07/BP/U09/U14) restent dans la matrice, sans modèle chiffré inventé ; les sources et contributions utiles restent conservées.
