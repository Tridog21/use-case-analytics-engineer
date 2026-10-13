-- Pipe commercial par semaine et par équipe : deals en cours, montant du pipe, signatures.
-- Requête historique de l'équipe sales, lancée avant chaque point pipe du lundi.

WITH
    days AS (
        SELECT toDate('2024-01-01') + number AS day
        FROM numbers(dateDiff('day', toDate('2024-01-01'), today()) + 1)
    ),

    versions AS (
        SELECT
            o.id,
            o.`meta.ts`                             AS valid_from,
            o.state,
            o.turnoverEstimatedExcludingTax         AS amount,
            o.`relationships.mainManager.data.id`   AS manager_id
        FROM raw.opportunities AS o
        WHERE o.`meta.deleted` = 0
          AND o.typeOf = 4
          AND o.creationDate >= '2024-01-01'
    ),

    intervals AS (
        SELECT
            v.id,
            v.valid_from,
            any(v.state)        AS state,
            any(v.amount)       AS amount,
            any(v.manager_id)   AS manager_id,
            minOrNull(n.valid_from) AS valid_to
        FROM versions AS v
        LEFT JOIN versions AS n ON n.id = v.id AND n.valid_from > v.valid_from
        GROUP BY v.id, v.valid_from
    ),

    teams AS (
        SELECT
            JSONExtractInt(member, 'id')    AS manager_id,
            replaceOne(bu.name, 'Team BA - ', '') AS team
        FROM raw.businessunits AS bu
        ARRAY JOIN JSONExtractArrayRaw(bu.`relationships.includedManagers.data`) AS member
        WHERE bu.name LIKE 'Team BA%'
    ),

    daily AS (
        SELECT
            d.day,
            i.id,
            i.state,
            i.amount,
            t.team
        FROM days AS d
        CROSS JOIN intervals AS i
        LEFT JOIN teams AS t ON t.manager_id = i.manager_id
        WHERE d.day >= toDate(i.valid_from)
          AND (i.valid_to IS NULL OR d.day < toDate(i.valid_to))
    )

SELECT
    toMonday(day)                                                   AS week,
    ifNull(team, 'Autre')                                           AS team,
    uniqExactIf(id, state IN (0, 20, 21, 22, 23, 24, 25, 26, 28))   AS open_deals,
    sumIf(amount, state IN (0, 20, 21, 22, 23, 24, 25, 26, 28))
        / uniqExact(day)                                            AS pipe_amount,
    uniqExactIf(id, state = 1)                                      AS signed_deals,
    sumIf(amount, state = 1) / uniqExact(day)                       AS signed_amount
FROM daily
GROUP BY week, team
ORDER BY week DESC, team
