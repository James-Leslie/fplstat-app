-- Per-gameweek stats for a single player, ordered most-recent first.
-- Returns one row per finished fixture with opponent info, result scores,
-- and all key per-game stats needed for the player detail modal.

CREATE OR REPLACE FUNCTION public.player_history(p_player_id int)
RETURNS TABLE (
    gameweek_id      int,
    opponent         text,
    opponent_code    int,
    was_home         boolean,
    home_score       int,
    away_score       int,
    pts              int,
    starts           int,
    minutes          int,
    goals_scored     int,
    assists          int,
    xg               numeric,
    xa               numeric,
    xgi              numeric,
    cs               int,
    goals_conceded   int,
    xgc              numeric,
    own_goals        int,
    penalties_saved  int,
    penalties_missed int,
    yellow_cards     int,
    red_cards        int,
    saves            int,
    bonus            int,
    bps              int,
    influence        numeric,
    creativity       numeric,
    threat           numeric,
    ict_index        numeric,
    xpts             numeric
)
LANGUAGE sql STABLE SECURITY DEFINER AS $$
    SELECT
        v.gameweek_id,
        t.short_name                               AS opponent,
        t.code                                     AS opponent_code,
        v.was_home,
        f.team_h_score                             AS home_score,
        f.team_a_score                             AS away_score,
        v.total_points                             AS pts,
        v.starts,
        v.minutes,
        v.goals_scored,
        v.assists,
        ROUND(v.expected_goals, 2)                 AS xg,
        ROUND(v.expected_assists, 2)               AS xa,
        ROUND(v.expected_goal_involvements, 2)     AS xgi,
        v.clean_sheets                             AS cs,
        v.goals_conceded,
        ROUND(v.expected_goals_conceded, 2)        AS xgc,
        v.own_goals,
        v.penalties_saved,
        v.penalties_missed,
        v.yellow_cards,
        v.red_cards,
        v.saves,
        v.bonus,
        v.bps,
        ROUND(v.influence, 2)                      AS influence,
        ROUND(v.creativity, 2)                     AS creativity,
        ROUND(v.threat, 2)                         AS threat,
        ROUND(v.ict_index, 2)                      AS ict_index,
        ROUND(v.xpts, 2)                           AS xpts
    FROM public.player_gameweek_stats v
    JOIN raw.fixtures f ON f.id = v.fixture_id
    JOIN raw.teams    t ON t.id = v.opponent_team_id
    WHERE v.player_id = p_player_id
      AND f.finished = true
    ORDER BY v.gameweek_id DESC
$$;
