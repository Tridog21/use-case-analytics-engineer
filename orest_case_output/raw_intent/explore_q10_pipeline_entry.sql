-- Q10. Read-only profiling of the supplied snapshot; not a definition of qualification.
-- Last version is selected BEFORE excluding deleted records. Keys include tenant.
-- All types/dates unless explicitly filtered. Run numbered queries separately.

-- Q1: Current state distribution, dictionary properties and legacy open-pipe rule.
WITH
current_opportunities AS (
    SELECT * FROM (
        SELECT * FROM raw.opportunities
        ORDER BY `meta.ts` DESC LIMIT 1 BY `meta.customer`, id
    ) WHERE NOT `meta.deleted`
),
latest_dictionary AS (
    SELECT * FROM (
        SELECT * FROM raw.dictionaries WHERE `meta.language` = 'fr'
        ORDER BY `meta.ts` DESC LIMIT 1 BY `meta.customer`, `meta.language`
    ) WHERE NOT `meta.deleted`
),
states AS (
    SELECT `meta.customer` AS tenant,
        JSONExtractInt(item, 'id') AS state_id,
        JSONExtractString(item, 'value') AS label,
        JSONExtractBool(item, 'active') AS active,
        JSONExtractBool(item, 'isEnabled') AS enabled
    FROM latest_dictionary
    ARRAY JOIN JSONExtractArrayRaw(ifNull(`setting.state.opportunity`, '[]')) AS item
)
SELECT o.state, s.label, s.active AS besoin_encore_en_cours,
       s.enabled AS etape_proposee_dans_interface,
       o.state IN (0,20,21,22,23,24,25,26,28) AS inclus_liste_ouverte_legacy,
       count() AS nb_besoins,
       countIf(o.typeOf = 4 AND o.creationDate >= '2024-01-01') AS nb_dans_perimetre_type_date_legacy
FROM current_opportunities AS o
LEFT JOIN states AS s ON s.tenant = o.`meta.customer` AND s.state_id = o.state
GROUP BY o.state, s.label, s.active, s.enabled
ORDER BY o.state;

-- Q2: First recorded state among currently non-deleted opportunities.
-- An initial observed state is NOT necessarily the state at CRM creation.
WITH
current_opportunities AS (
    SELECT * FROM (
        SELECT * FROM raw.opportunities
        ORDER BY `meta.ts` DESC LIMIT 1 BY `meta.customer`, id
    ) WHERE NOT `meta.deleted`
),
first_observation AS (
    SELECT `meta.customer` AS tenant, id,
           argMin(tuple(state), `meta.ts`).1 AS first_state,
           min(`meta.ts`) AS first_cdc_ts
    FROM raw.opportunities GROUP BY tenant, id
)
SELECT f.first_state, count() AS nb_besoins,
       countIf(f.first_cdc_ts > o.creationDate) AS premiere_observation_apres_creation,
       countIf(f.first_cdc_ts < o.creationDate) AS premiere_observation_avant_creation,
       round(median(dateDiff('second', o.creationDate, f.first_cdc_ts)) / 86400, 2) AS delai_median_creation_premiere_observation_jours
FROM current_opportunities AS o
INNER JOIN first_observation AS f ON f.tenant = o.`meta.customer` AND f.id = o.id
GROUP BY f.first_state ORDER BY nb_besoins DESC;

-- Q3: Coverage of candidate qualification/demo events in the raw history.
-- First observed CDC timestamps are proxies, not certified event timestamps.
WITH
current_opportunities AS (
    SELECT * FROM (
        SELECT * FROM raw.opportunities
        ORDER BY `meta.ts` DESC LIMIT 1 BY `meta.customer`, id
    ) WHERE NOT `meta.deleted`
),
observed_events AS (
    SELECT `meta.customer` AS tenant, id,
        minOrNullIf(`meta.ts`, state = 22 AND NOT `meta.deleted`) AS first_qualification,
        minOrNullIf(`meta.ts`, state = 23 AND NOT `meta.deleted`) AS first_discovery,
        minOrNullIf(`meta.ts`, state = 24 AND NOT `meta.deleted`) AS first_show_boond
    FROM raw.opportunities GROUP BY tenant, id
)
SELECT count() AS nb_besoins,
       countIf(isNotNull(e.first_qualification)) AS qualification_observee,
       countIf(isNotNull(e.first_discovery)) AS decouverte_observee,
       countIf(isNotNull(e.first_show_boond)) AS show_boond_observe,
       countIf(o.state IN (1,14)) AS actuellement_signes,
       countIf(o.state IN (1,14) AND isNull(e.first_show_boond)) AS signes_sans_show_boond_observe,
       countIf(isNotNull(e.first_show_boond) AND isNull(e.first_qualification)) AS show_boond_sans_qualification_observee,
       countIf(e.first_show_boond < o.creationDate) AS show_boond_observe_avant_creation
FROM current_opportunities AS o
INNER JOIN observed_events AS e ON e.tenant = o.`meta.customer` AND e.id = o.id;

-- Q4: Concrete trajectories, for manual investigation (current non-deleted objects).
WITH
current_opportunities AS (
    SELECT * FROM (
        SELECT * FROM raw.opportunities
        ORDER BY `meta.ts` DESC LIMIT 1 BY `meta.customer`, id
    ) WHERE NOT `meta.deleted`
),
observed_events AS (
    SELECT `meta.customer` AS tenant, id,
        argMin(tuple(state), `meta.ts`).1 AS first_state,
        min(`meta.ts`) AS first_cdc_ts,
        minOrNullIf(`meta.ts`, state = 22 AND NOT `meta.deleted`) AS first_qualification,
        minOrNullIf(`meta.ts`, state = 23 AND NOT `meta.deleted`) AS first_discovery,
        minOrNullIf(`meta.ts`, state = 24 AND NOT `meta.deleted`) AS first_show_boond
    FROM raw.opportunities GROUP BY tenant, id
)
SELECT o.`meta.customer` AS tenant, o.id, o.creationDate,
       e.first_cdc_ts, e.first_state, e.first_qualification,
       e.first_discovery, e.first_show_boond, o.state AS current_state,
       dateDiff('day', o.creationDate, e.first_show_boond) AS jours_creation_vers_show_boond_observe
FROM current_opportunities AS o
INNER JOIN observed_events AS e ON e.tenant = o.`meta.customer` AND e.id = o.id
WHERE isNotNull(e.first_show_boond)
ORDER BY jours_creation_vers_show_boond_observe DESC, o.id
LIMIT 10;
