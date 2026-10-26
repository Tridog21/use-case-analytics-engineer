-- ClickHouse 25.11. Read-only exploration. Run each numbered query separately.
-- Current snapshot = last version per tenant + id, THEN exclude deleted records.
-- LIMIT 1 BY is deliberate: filtering deleted rows before deduplication revives records.
-- Equal meta.ts for different versions would need an additional ordering rule.
-- No reporting period filter: this is an inventory of the supplied snapshot.

-- Q1: Companies with multiple contacts/opportunities and the corresponding HubSpot deals.
-- Aggregate each child table BEFORE joining, to avoid multiplying counts.
-- A HubSpot deal and a Boond opportunity represent linked commercial records,
-- not two independent sales. Positive integer Boond references only.
WITH
companies AS (
    SELECT * FROM (
        SELECT * FROM raw.companies
        ORDER BY `meta.ts` DESC LIMIT 1 BY `meta.customer`, id
    ) WHERE NOT `meta.deleted`
),
contacts AS (
    SELECT * FROM (
        SELECT * FROM raw.contacts
        ORDER BY `meta.ts` DESC LIMIT 1 BY `meta.customer`, id
    ) WHERE NOT `meta.deleted`
),
opportunities AS (
    SELECT * FROM (
        SELECT * FROM raw.opportunities
        ORDER BY `meta.ts` DESC LIMIT 1 BY `meta.customer`, id
    ) WHERE NOT `meta.deleted`
),
contact_counts AS (
    SELECT `meta.customer` AS tenant,
           `relationships.company.data.id` AS company_id,
           count() AS nb_contacts
    FROM contacts GROUP BY tenant, company_id
),
opportunity_counts AS (
    SELECT `meta.customer` AS tenant,
           `relationships.company.data.id` AS company_id,
           count() AS nb_opportunites,
           groupArray(id) AS opportunite_ids
    FROM opportunities GROUP BY tenant, company_id
),
deal_counts AS (
    SELECT o.`meta.customer` AS tenant,
           o.`relationships.company.data.id` AS company_id,
           uniqExact(d.id) AS nb_deals_hubspot
    FROM opportunities AS o
    INNER JOIN hubspot.deals AS d
        ON o.id = accurateCastOrNull(d.properties_boond_id_num, 'Int64')
    WHERE NOT d.archived
      AND d.properties_boond_id_num > 0
      AND d.properties_boond_id_num = floor(d.properties_boond_id_num)
    GROUP BY tenant, company_id
)
SELECT c.`meta.customer` AS tenant, c.id AS company_id, c.name AS societe,
       ifNull(cc.nb_contacts, 0) AS nb_contacts,
       ifNull(oc.nb_opportunites, 0) AS nb_opportunites,
       oc.opportunite_ids,
       ifNull(dc.nb_deals_hubspot, 0) AS nb_deals_hubspot
FROM companies AS c
LEFT JOIN contact_counts AS cc ON cc.tenant = c.`meta.customer` AND cc.company_id = c.id
LEFT JOIN opportunity_counts AS oc ON oc.tenant = c.`meta.customer` AND oc.company_id = c.id
LEFT JOIN deal_counts AS dc ON dc.tenant = c.`meta.customer` AND dc.company_id = c.id
WHERE ifNull(oc.nb_opportunites, 0) > 1
ORDER BY nb_opportunites DESC, nb_contacts DESC, company_id
LIMIT 30;

-- Q2: Which records do demo actions point to? Codes checked in raw.dictionaries:
-- 60 = Demo 1, 68 = Follow-up demo. 25 = Demo request, excluded.
-- An action of a demo type is NOT proof of attendance/completion.
WITH actions AS (
    SELECT * FROM (
        SELECT * FROM raw.actions
        ORDER BY `meta.ts` DESC LIMIT 1 BY `meta.customer`, id
    ) WHERE NOT `meta.deleted`
)
SELECT typeOf AS type_action,
       `relationships.dependsOn.data.type` AS type_fiche_rattachee,
       count() AS nb_actions_demo,
       uniqExactIf(tuple(`meta.customer`, `relationships.dependsOn.data.id`),
           isNotNull(`relationships.dependsOn.data.id`)) AS nb_fiches_distinctes
FROM actions
WHERE typeOf IN (60, 68)
GROUP BY type_action, type_fiche_rattachee
ORDER BY type_action, type_fiche_rattachee;

-- Q3: For each contact with demo actions, how many CURRENT opportunities could match?
-- Same principal contact + tenant. This lists candidates, NOT a validated attribution.
-- 0 = no matching current opportunity; 1 = one candidate; >1 = ambiguous.
-- Temporal ownership/contact changes and deleted records can affect this join.
WITH
actions AS (
    SELECT * FROM (
        SELECT * FROM raw.actions
        ORDER BY `meta.ts` DESC LIMIT 1 BY `meta.customer`, id
    ) WHERE NOT `meta.deleted`
),
opportunities AS (
    SELECT * FROM (
        SELECT * FROM raw.opportunities
        ORDER BY `meta.ts` DESC LIMIT 1 BY `meta.customer`, id
    ) WHERE NOT `meta.deleted`
),
demos_by_contact AS (
    SELECT `meta.customer` AS tenant,
           `relationships.dependsOn.data.id` AS contact_id,
           count() AS nb_actions_demo,
           groupArray(id) AS action_ids,
           min(startDate) AS premiere_date_agenda,
           max(startDate) AS derniere_date_agenda
    FROM actions
    WHERE typeOf IN (60, 68)
      AND `relationships.dependsOn.data.type` = 'contact'
      AND isNotNull(`relationships.dependsOn.data.id`)
    GROUP BY tenant, contact_id
),
opportunities_by_contact AS (
    SELECT `meta.customer` AS tenant,
           `relationships.contact.data.id` AS contact_id,
           count() AS nb_opportunites_candidates,
           groupArray(id) AS opportunite_ids,
           groupUniqArray(`relationships.company.data.id`) AS company_ids
    FROM opportunities
    WHERE isNotNull(`relationships.contact.data.id`)
    GROUP BY tenant, contact_id
)
SELECT d.tenant, d.contact_id, d.nb_actions_demo, d.action_ids,
       d.premiere_date_agenda, d.derniere_date_agenda,
       ifNull(o.nb_opportunites_candidates, 0) AS nb_opportunites_candidates,
       o.opportunite_ids, o.company_ids,
       multiIf(ifNull(o.nb_opportunites_candidates, 0) = 0, 'Aucun candidat',
               o.nb_opportunites_candidates = 1, 'Un candidat, a valider',
               'Plusieurs candidats : attribution ambigue') AS diagnostic
FROM demos_by_contact AS d
LEFT JOIN opportunities_by_contact AS o
    ON o.tenant = d.tenant AND o.contact_id = d.contact_id
ORDER BY nb_opportunites_candidates DESC, nb_actions_demo DESC, d.contact_id
LIMIT 50;

-- Q4: Alternate definition: current opportunities with a recorded Show Boond version.
-- 24 = Show Boond; 1 and 14 = won states, checked in dictionaries.
-- Historical states do not prove a meeting took place. Missing CDC transitions mean
-- absence of an observed state is NOT proof that this stage was never reached.
-- Current company/principal contact and current won state; no conversion time window.
WITH
opportunities AS (
    SELECT * FROM (
        SELECT * FROM raw.opportunities
        ORDER BY `meta.ts` DESC LIMIT 1 BY `meta.customer`, id
    ) WHERE NOT `meta.deleted`
),
observed_stage AS (
    SELECT `meta.customer` AS tenant, id,
           max(ifNull(state = 24, 0) AND NOT `meta.deleted`) AS show_boond_observe
    FROM raw.opportunities
    GROUP BY tenant, id
)
SELECT count() AS nb_opportunites_actuelles_non_supprimees,
       countIf(h.show_boond_observe = 1) AS nb_opportunites_show_boond_observe,
       uniqExactIf(tuple(o.`meta.customer`, o.`relationships.company.data.id`),
           h.show_boond_observe = 1 AND isNotNull(o.`relationships.company.data.id`)) AS nb_societes_concernees,
       countIf(h.show_boond_observe = 1 AND o.state IN (1, 14)) AS nb_devenues_gagnees_ou_deja_gagnees,
       round(100.0 * countIf(h.show_boond_observe = 1 AND o.state IN (1, 14))
           / nullIf(countIf(h.show_boond_observe = 1), 0), 2) AS pct_gagnees_parmi_show_boond_observes
FROM opportunities AS o
INNER JOIN observed_stage AS h ON h.tenant = o.`meta.customer` AND h.id = o.id;

-- Q5: Audit the assumption that every unarchived HubSpot deal has a Boond opportunity.
-- HubSpot has no tenant column in the supplied schema; matching IDs here assumes
-- the single Boond tenant documented in this case. Do not reuse unchanged for multitenancy.
WITH opportunities AS (
    SELECT *, 1 AS found FROM (
        SELECT * FROM raw.opportunities
        ORDER BY `meta.ts` DESC LIMIT 1 BY `meta.customer`, id
    ) WHERE NOT `meta.deleted`
)
SELECT count() AS nb_deals_non_archives,
       countIf(isNull(d.properties_boond_id_num)) AS nb_sans_reference_boond,
       countIf(isNotNull(d.properties_boond_id_num) AND
           (d.properties_boond_id_num <= 0 OR d.properties_boond_id_num != floor(d.properties_boond_id_num))) AS nb_references_non_valides,
       countIf(ifNull(o.found, 0) = 1) AS nb_deals_avec_opportunite_actuelle,
       countIf(isNotNull(d.properties_boond_id_num)
           AND d.properties_boond_id_num > 0
           AND d.properties_boond_id_num = floor(d.properties_boond_id_num)
           AND ifNull(o.found, 0) = 0) AS nb_references_valides_sans_opportunite_actuelle
FROM hubspot.deals AS d
LEFT JOIN opportunities AS o
    ON o.id = accurateCastOrNull(d.properties_boond_id_num, 'Int64')
    AND d.properties_boond_id_num > 0
    AND d.properties_boond_id_num = floor(d.properties_boond_id_num)
WHERE NOT d.archived;
