-- Upsells in the supplied case. Read-only, ClickHouse 25.11.
-- Scope: current non-deleted opportunities; tenant + id keys. All dates.
-- Raw versions are deduplicated BEFORE applying the current deletion filter.
-- Types 4=New Client Boond, 7=Upsell Boond, 2=Formation, checked in latest French dictionary.

-- Q1: Current types, number of versions, changed types and tied timestamps.
WITH current AS (
    SELECT * FROM (
        SELECT * FROM raw.opportunities ORDER BY `meta.ts` DESC
        LIMIT 1 BY `meta.customer`, id
    ) WHERE NOT `meta.deleted`
), history AS (
    SELECT `meta.customer` AS tenant, id, count() AS nb_versions,
        uniqExact(`meta.ts`) AS nb_timestamps,
        uniqExact(tuple(typeOf)) AS nb_types,
        countIf(`meta.deleted`) AS deletion_versions,
        min(`meta.ts`) AS first_ts
    FROM raw.opportunities GROUP BY tenant,id
)
SELECT c.typeOf, count() AS nb_opportunites,
    sum(h.nb_versions) AS nb_versions,
    countIf(h.nb_versions=1) AS une_seule_version,
    countIf(h.nb_timestamps<h.nb_versions) AS horodatages_ex_aequo,
    countIf(h.nb_types>1) AS type_modifie,
    countIf(h.deletion_versions>0) AS suppression_historique,
    countIf(h.first_ts>c.creationDate) AS premiere_observation_apres_creation,
    countIf(h.first_ts!=c.creationDate OR isNull(c.creationDate)) AS premiere_observation_differe_creation,
    min(c.creationDate) AS premiere_creation, max(c.creationDate) AS derniere_creation
FROM current c INNER JOIN history h ON h.tenant=c.`meta.customer` AND h.id=c.id
GROUP BY c.typeOf ORDER BY c.typeOf;

-- Q2: Current state for upsells. Terminal codes 1 and 14 are separate states of a won deal.
WITH current AS (
    SELECT * FROM (
        SELECT * FROM raw.opportunities ORDER BY `meta.ts` DESC
        LIMIT 1 BY `meta.customer`,id
    ) WHERE NOT `meta.deleted` AND typeOf=7
)
SELECT state, count() AS nb_upsells, groupArray(id) AS ids
FROM current GROUP BY state ORDER BY state;

-- Q3: Collapsed observed state sequences. Consecutive repetitions removed.
-- Compare sequences of current upsells; not all paths are mandatory.
WITH current AS (
    SELECT * FROM (
        SELECT * FROM raw.opportunities ORDER BY `meta.ts` DESC
        LIMIT 1 BY `meta.customer`,id
    ) WHERE NOT `meta.deleted` AND typeOf=7
), journeys AS (
    SELECT `meta.customer` AS tenant, id,
        arrayCompact(arrayMap(x -> x.2,
            arraySort(x -> x.1, groupArray(tuple(`meta.ts`,state))))) AS states
    FROM raw.opportunities WHERE NOT `meta.deleted` GROUP BY tenant,id
)
SELECT j.states, count() AS nb_upsells, groupArray(c.id) AS ids
FROM current c INNER JOIN journeys j ON j.tenant=c.`meta.customer` AND j.id=c.id
GROUP BY j.states ORDER BY nb_upsells DESC,j.states;

-- Q4: Distinct opportunities EVER observed at each state, by CURRENT type.
-- Not a cohort conversion rate: all creation dates and still-open opportunities included.
-- A missing state is not necessarily a missing real-life interaction.
WITH current AS (
    SELECT * FROM (
        SELECT * FROM raw.opportunities ORDER BY `meta.ts` DESC
        LIMIT 1 BY `meta.customer`,id
    ) WHERE NOT `meta.deleted` AND typeOf IN (4,7)
)
SELECT c.typeOf, h.state AS state,
    uniqExact(tuple(c.`meta.customer`,c.id)) AS nb_opportunites_ayant_etat_observe
FROM current c INNER JOIN raw.opportunities h
    ON h.`meta.customer`=c.`meta.customer` AND h.id=c.id
WHERE NOT h.`meta.deleted`
GROUP BY c.typeOf,h.state ORDER BY c.typeOf,h.state;

-- Q5: CRM links and earlier observed new-client wins for the same company.
-- Earlier recorded win is evidence of an earlier commercial win, not active subscription proof.
-- Demo counts concern the principal CONTACT, not the upsell itself.
WITH
opportunities AS (
    SELECT * FROM (
        SELECT * FROM raw.opportunities ORDER BY `meta.ts` DESC
        LIMIT 1 BY `meta.customer`,id
    ) WHERE NOT `meta.deleted`
),
upsells AS (SELECT * FROM opportunities WHERE typeOf=7),
first_new_win AS (
    SELECT `meta.customer` AS tenant, `relationships.company.data.id` AS company_id,
        min(`meta.ts`) AS first_observed_win
    FROM raw.opportunities
    WHERE NOT `meta.deleted` AND typeOf=4 AND state IN (1,14)
    GROUP BY tenant,company_id
),
demos AS (
    SELECT `meta.customer` AS tenant, `relationships.dependsOn.data.id` AS contact_id,
        count() AS nb_contact_demos
    FROM (
        SELECT * FROM raw.actions ORDER BY `meta.ts` DESC
        LIMIT 1 BY `meta.customer`,id
    ) WHERE NOT `meta.deleted` AND typeOf IN (60,68)
      AND `relationships.dependsOn.data.type`='contact'
    GROUP BY tenant,contact_id
),
deals AS (
    SELECT accurateCastOrNull(properties_boond_id_num,'Int64') AS opportunity_id,
        count() AS nb_deals
    FROM hubspot.deals WHERE NOT archived
        AND properties_boond_id_num>0
        AND properties_boond_id_num=floor(properties_boond_id_num)
    GROUP BY opportunity_id
)
SELECT count() AS nb_upsells,
    uniqExactIf(tuple(u.`meta.customer`,u.`relationships.company.data.id`),
        isNotNull(u.`relationships.company.data.id`)) AS nb_societes,
    countIf(isNull(u.`relationships.company.data.id`)) AS sans_societe_id,
    countIf(isNull(u.`relationships.contact.data.id`)) AS sans_contact_principal,
    countIf(w.first_observed_win<u.creationDate) AS avec_signature_new_client_observee_avant_creation,
    countIf(ifNull(d.nb_contact_demos,0)>0) AS avec_demo_sur_contact_principal,
    countIf(ifNull(h.nb_deals,0)>0) AS avec_deal_hubspot,
    sum(ifNull(h.nb_deals,0)) AS nb_deals_hubspot_lies
FROM upsells u
LEFT JOIN first_new_win w ON w.tenant=u.`meta.customer` AND w.company_id=u.`relationships.company.data.id`
LEFT JOIN demos d ON d.tenant=u.`meta.customer` AND d.contact_id=u.`relationships.contact.data.id`
LEFT JOIN deals h ON h.opportunity_id=u.id
SETTINGS join_use_nulls=1;

-- Q6: Explicit project/subscription-line links per upsell. No inference from amounts alone.
-- A row in deliveries is not proof of payment or incremental revenue relative to a prior contract.
WITH
upsells AS (
    SELECT * FROM (
        SELECT * FROM raw.opportunities ORDER BY `meta.ts` DESC
        LIMIT 1 BY `meta.customer`,id
    ) WHERE NOT `meta.deleted` AND typeOf=7
),
projects AS (
    SELECT * FROM (
        SELECT * FROM raw.projects ORDER BY `meta.ts` DESC
        LIMIT 1 BY `meta.customer`,id
    ) WHERE NOT `meta.deleted`
),
deliveries AS (
    SELECT * FROM (
        SELECT * FROM raw.deliveries ORDER BY `meta.ts` DESC
        LIMIT 1 BY `meta.customer`,id
    ) WHERE NOT `meta.deleted`
),
project_counts AS (
    SELECT `meta.customer` AS tenant, `relationships.opportunity.data.id` AS opportunity_id,
        count() AS nb_projects, groupArray(id) AS project_ids
    FROM projects GROUP BY tenant,opportunity_id
),
line_counts AS (
    SELECT p.`meta.customer` AS tenant, p.`relationships.opportunity.data.id` AS opportunity_id,
        count() AS nb_lines, sum(d.averageDailyPriceExcludingTax) AS montant_mensuel_lignes
    FROM projects p INNER JOIN deliveries d
        ON d.`meta.customer`=p.`meta.customer` AND d.`relationships.project.data.id`=p.id
    GROUP BY tenant,opportunity_id
)
SELECT u.id AS upsell_id,u.state,u.creationDate,
    u.`relationships.company.data.id` AS company_id,
    ifNull(p.nb_projects,0) AS nb_projets_lies,p.project_ids,
    ifNull(l.nb_lines,0) AS nb_lignes_abonnement_liees,
    l.montant_mensuel_lignes
FROM upsells u
LEFT JOIN project_counts p ON p.tenant=u.`meta.customer` AND p.opportunity_id=u.id
LEFT JOIN line_counts l ON l.tenant=u.`meta.customer` AND l.opportunity_id=u.id
ORDER BY u.id
SETTINGS join_use_nulls=1;
