-- Season or GW-range aggregate per player.
-- Call with no args for full season; pass gw_from/gw_to to filter by range,
-- or last_n to select the N most recent finished gameweeks.
-- Returns: pos, team, team_code, player, price, st, mp, pts,
--          p90, gs90, a90, gi90, xg90, xa90, xgi90,
--          cs, xgc, xgc90, tsb, xp90.
-- Queries public.player_gameweek_stats so the xpts formula isn't duplicated.

DROP FUNCTION IF EXISTS public.player_stats(int, int, int);
DROP FUNCTION IF EXISTS public.player_stats(int, int);

CREATE OR REPLACE FUNCTION public.player_stats(
    gw_from int DEFAULT NULL,
    gw_to   int DEFAULT NULL,
    last_n  int DEFAULT NULL
)
RETURNS TABLE (
    player_id int,
    pos       text,
    team      text,
    team_code int,
    player    text,
    price     numeric,
    st        bigint,
    mp        bigint,
    pts       bigint,
    p90       numeric,
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
    xp90      numeric
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
        SUM(v.starts)                                                                    AS st,
        SUM(v.minutes)                                                                   AS mp,
        SUM(v.total_points)                                                              AS pts,
        ROUND(SUM(v.total_points) * 90.0 / NULLIF(SUM(v.minutes), 0), 1)                AS p90,
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
        ROUND(SUM(v.xpts) * 90.0 / NULLIF(SUM(v.minutes), 0), 2)                        AS xp90
    FROM public.player_gameweek_stats v
    JOIN raw.players   p ON p.id = v.player_id
    JOIN raw.teams     t ON t.id = p.team
    JOIN raw.gameweeks g ON g.id = v.gameweek_id
    WHERE g.finished = true
      AND (
        CASE
            WHEN last_n IS NOT NULL
                THEN g.id IN (
                    SELECT id FROM raw.gameweeks
                    WHERE finished = true
                    ORDER BY id DESC
                    LIMIT last_n
                )
            ELSE
                (gw_from IS NULL OR v.gameweek_id >= gw_from)
                AND (gw_to   IS NULL OR v.gameweek_id <= gw_to)
        END
      )
    GROUP BY p.id, p.element_type, t.short_name, t.code, p.web_name, p.now_cost, p.selected_by_percent
    HAVING SUM(v.minutes) > 0
    ORDER BY SUM(v.total_points) DESC
$$;
