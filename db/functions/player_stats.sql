-- Season or GW-range aggregate per player.
-- Call with no args for full season; pass gw_from/gw_to to filter by range,
-- or last_n to select the N most recent finished gameweeks.
-- Matches the Streamlit player stats table: pos, team, player, price, st, mp, pts,
-- p90, gs90, a90, gi90, xg90, xa90, xgi90, cs, xgc, xgc90, tsb.

-- Drop the old 2-parameter signature before replacing.
DROP FUNCTION IF EXISTS public.player_stats(int, int);

CREATE OR REPLACE FUNCTION public.player_stats(
    gw_from int DEFAULT NULL,
    gw_to   int DEFAULT NULL,
    last_n  int DEFAULT NULL
)
RETURNS TABLE (
    player_id int, pos text, team text, player text, price numeric,
    st bigint, mp bigint, pts bigint,
    p90 numeric, gs90 numeric, a90 numeric, gi90 numeric,
    xg90 numeric, xa90 numeric, xgi90 numeric,
    cs bigint, xgc numeric, xgc90 numeric, tsb numeric
)
LANGUAGE sql STABLE AS $$
    SELECT
        p.id AS player_id,
        CASE p.element_type
            WHEN 1 THEN 'GK' WHEN 2 THEN 'DEF' WHEN 3 THEN 'MID' ELSE 'FWD'
        END                                                                              AS pos,
        t.short_name                                                                     AS team,
        p.web_name                                                                       AS player,
        p.now_cost / 10.0                                                                AS price,
        SUM(s.starts)                                                                    AS st,
        SUM(s.minutes)                                                                   AS mp,
        SUM(s.total_points)                                                              AS pts,
        ROUND(SUM(s.total_points) * 90.0 / NULLIF(SUM(s.minutes), 0), 1)                AS p90,
        ROUND(SUM(s.goals_scored) * 90.0 / NULLIF(SUM(s.minutes), 0), 2)                AS gs90,
        ROUND(SUM(s.assists) * 90.0 / NULLIF(SUM(s.minutes), 0), 2)                     AS a90,
        ROUND((SUM(s.goals_scored) + SUM(s.assists)) * 90.0
              / NULLIF(SUM(s.minutes), 0), 2)                                            AS gi90,
        ROUND(SUM(s.expected_goals::numeric) * 90.0 / NULLIF(SUM(s.minutes), 0), 2)     AS xg90,
        ROUND(SUM(s.expected_assists::numeric) * 90.0 / NULLIF(SUM(s.minutes), 0), 2)   AS xa90,
        ROUND(SUM(s.expected_goal_involvements::numeric) * 90.0
              / NULLIF(SUM(s.minutes), 0), 2)                                            AS xgi90,
        SUM(s.clean_sheets)                                                              AS cs,
        ROUND(SUM(s.expected_goals_conceded::numeric), 2)                                AS xgc,
        ROUND(SUM(s.expected_goals_conceded::numeric) * 90.0
              / NULLIF(SUM(s.minutes), 0), 2)                                            AS xgc90,
        p.selected_by_percent::numeric                                                   AS tsb
    FROM raw.player_gameweek_stats s
    JOIN raw.players   p ON p.id = s.element
    JOIN raw.teams     t ON t.id = p.team
    JOIN raw.gameweeks g ON g.id = s.round
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
                (gw_from IS NULL OR s.round >= gw_from)
                AND (gw_to IS NULL OR s.round <= gw_to)
        END
      )
    GROUP BY p.id, p.element_type, t.short_name, p.web_name, p.now_cost, p.selected_by_percent
    HAVING SUM(s.minutes) > 0
    ORDER BY SUM(s.total_points) DESC
$$;
