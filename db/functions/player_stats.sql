-- Season or GW-range aggregate per player.
-- Call with no args for full season; pass gw_from/gw_to to filter by range,
-- or last_n to select the N most recent finished gameweeks.
-- include_current (default true) controls whether fixtures from an in-progress
-- gameweek are included; last_n always counts only fully-finished gameweeks.
-- Returns: pos, team, team_code, player, price, gp, st, mp, mp_pct, pts,
--          ppg, p90, xppg, xp90, gs, a, gi, gs90, a90, gi90, xg90, xa90, xgi90,
--          cs, xgc, xgc90, tsb.
-- Queries public.player_gameweek_stats so the xpts formula isn't duplicated.

DROP FUNCTION IF EXISTS public.player_stats(int, int, int);
DROP FUNCTION IF EXISTS public.player_stats(int, int);

CREATE OR REPLACE FUNCTION public.player_stats(
    gw_from         int  DEFAULT NULL,
    gw_to           int  DEFAULT NULL,
    last_n          int  DEFAULT NULL,
    include_current bool DEFAULT true
)
RETURNS TABLE (
    player_id int,
    pos       text,
    team      text,
    team_code int,
    player    text,
    price     numeric,
    gp        bigint,
    st        bigint,
    mp        bigint,
    mp_pct    numeric,
    pts       bigint,
    ppg       numeric,
    p90       numeric,
    gs        bigint,
    a         bigint,
    gi        bigint,
    gs90      numeric,
    a90       numeric,
    gi90      numeric,
    xg90      numeric,
    xa90      numeric,
    xgi90     numeric,
    cs        bigint,
    xgc       numeric,
    xgc90     numeric,
    tsb       numeric,
    xppg      numeric,
    xp90      numeric,
    goals_pp90      numeric,
    assists_pp90    numeric,
    defensive_pp90  numeric,
    bonus_pp90      numeric,
    appearance_pp90 numeric,
    saves_pp90      numeric,
    deductions_pp90 numeric
)
LANGUAGE sql STABLE SECURITY DEFINER AS $$
    SELECT
        p.id                                                                             AS player_id,
        CASE p.element_type
            WHEN 1 THEN 'GK' WHEN 2 THEN 'DEF' WHEN 3 THEN 'MID' ELSE 'FWD'
        END                                                                              AS pos,
        t.short_name                                                                     AS team,
        t.code                                                                           AS team_code,
        p.web_name                                                                       AS player,
        p.now_cost / 10.0                                                                AS price,
        COUNT(*)                                                                         AS gp,
        SUM(v.starts)                                                                    AS st,
        SUM(v.minutes)                                                                   AS mp,
        ROUND(SUM(v.minutes) * 100.0 / NULLIF(COUNT(*) * 90, 0), 1)                     AS mp_pct,
        SUM(v.total_points)                                                              AS pts,
        ROUND(SUM(v.total_points) * 1.0 / COUNT(*), 1)                                  AS ppg,
        ROUND(SUM(v.total_points) * 90.0 / NULLIF(SUM(v.minutes), 0), 1)                AS p90,
        SUM(v.goals_scored)                                                              AS gs,
        SUM(v.assists)                                                                   AS a,
        SUM(v.goals_scored) + SUM(v.assists)                                             AS gi,
        ROUND(SUM(v.goals_scored) * 90.0 / NULLIF(SUM(v.minutes), 0), 2)                AS gs90,
        ROUND(SUM(v.assists) * 90.0 / NULLIF(SUM(v.minutes), 0), 2)                     AS a90,
        ROUND((SUM(v.goals_scored) + SUM(v.assists)) * 90.0
              / NULLIF(SUM(v.minutes), 0), 2)                                            AS gi90,
        ROUND(SUM(v.expected_goals) * 90.0 / NULLIF(SUM(v.minutes), 0), 2)              AS xg90,
        ROUND(SUM(v.expected_assists) * 90.0 / NULLIF(SUM(v.minutes), 0), 2)            AS xa90,
        ROUND(SUM(v.expected_goal_involvements) * 90.0
              / NULLIF(SUM(v.minutes), 0), 2)                                            AS xgi90,
        SUM(v.clean_sheets)                                                              AS cs,
        ROUND(SUM(v.expected_goals_conceded), 2)                                         AS xgc,
        ROUND(SUM(v.expected_goals_conceded) * 90.0
              / NULLIF(SUM(v.minutes), 0), 2)                                            AS xgc90,
        p.selected_by_percent::numeric                                                   AS tsb,
        ROUND(SUM(v.xpts) * 1.0 / COUNT(*), 2)                                          AS xppg,
        ROUND(SUM(v.xpts) * 90.0 / NULLIF(SUM(v.minutes), 0), 2)                        AS xp90,
        -- PP90 breakdown columns
        ROUND(SUM(v.goals_scored)
              * CASE p.element_type WHEN 1 THEN 6 WHEN 2 THEN 6 WHEN 3 THEN 5 ELSE 4 END
              * 90.0 / NULLIF(SUM(v.minutes), 0), 2)                                     AS goals_pp90,
        ROUND(SUM(v.assists) * 3 * 90.0 / NULLIF(SUM(v.minutes), 0), 2)                 AS assists_pp90,
        ROUND((
            SUM(v.clean_sheets * CASE p.element_type
                WHEN 1 THEN 4 WHEN 2 THEN 4 WHEN 3 THEN 1 ELSE 0 END)
            + SUM(CASE WHEN p.element_type IN (1, 2)
                  THEN FLOOR(v.goals_conceded / 2.0) * -1 ELSE 0 END)
            + SUM(CASE
                  WHEN p.element_type IN (1, 2) AND v.defensive_contribution >= 10 THEN 2
                  WHEN p.element_type IN (3, 4) AND v.defensive_contribution >= 12 THEN 2
                  ELSE 0 END)
        ) * 90.0 / NULLIF(SUM(v.minutes), 0), 2)                                        AS defensive_pp90,
        ROUND(SUM(v.bonus) * 90.0 / NULLIF(SUM(v.minutes), 0), 2)                       AS bonus_pp90,
        ROUND(SUM(CASE WHEN v.minutes >= 60 THEN 2 WHEN v.minutes >= 1 THEN 1 ELSE 0 END)
              * 90.0 / NULLIF(SUM(v.minutes), 0), 2)                                     AS appearance_pp90,
        ROUND(SUM(CASE WHEN p.element_type = 1 THEN FLOOR(v.saves / 3.0) ELSE 0 END)
              * 90.0 / NULLIF(SUM(v.minutes), 0), 2)                                     AS saves_pp90,
        ROUND(SUM(v.yellow_cards * -1 + v.red_cards * -3
                  + v.own_goals * -2 + v.penalties_missed * -2)
              * 90.0 / NULLIF(SUM(v.minutes), 0), 2)                                     AS deductions_pp90
    FROM public.player_gameweek_stats v
    JOIN raw.players   p ON p.id = v.player_id
    JOIN raw.teams     t ON t.id = p.team
    JOIN raw.fixtures  f ON f.id = v.fixture_id
    JOIN raw.gameweeks g ON g.id = v.gameweek_id
    WHERE f.finished = true
      AND (include_current OR g.finished = true)
      AND (
        CASE
            WHEN last_n IS NOT NULL
                THEN g.id IN (
                    SELECT id FROM raw.gameweeks
                    WHERE finished = true
                    ORDER BY id DESC
                    LIMIT last_n
                ) OR (include_current AND g.is_current = true)
            ELSE
                (gw_from IS NULL OR v.gameweek_id >= gw_from)
                AND (gw_to   IS NULL OR v.gameweek_id <= gw_to)
        END
      )
    GROUP BY p.id, p.element_type, t.short_name, t.code, p.web_name, p.now_cost, p.selected_by_percent
    HAVING SUM(v.minutes) > 0
    ORDER BY SUM(v.total_points) DESC
$$;
