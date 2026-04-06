-- Public views and functions over raw.* tables.
-- Renames FK columns to clean names, casts string-numeric fields to numeric,
-- and adds derived columns (price, fdr, xpts).
-- These are what the Streamlit frontend consumes.

CREATE VIEW public.teams AS
SELECT
    id, code, draw, form, loss, name, played, points, position,
    short_name, strength, team_division, unavailable, win,
    strength_overall_home, strength_overall_away,
    strength_attack_home, strength_attack_away,
    strength_defence_home, strength_defence_away,
    pulse_id
FROM raw.teams;

CREATE VIEW public.gameweeks AS
SELECT
    id, name, deadline_time, release_time, average_entry_score, finished,
    data_checked, highest_scoring_entry, deadline_time_epoch,
    deadline_time_game_offset, highest_score, is_previous, is_current,
    is_next, cup_leagues_created, h2h_ko_matches_created, can_enter,
    can_manage, released, ranked_count, most_selected, most_transferred_in,
    top_element, transfers_made, most_captained, most_vice_captained,
    overrides, chip_plays, top_element_info
FROM raw.gameweeks;

-- Renames: second_name → last_name, team → team_id
-- Casts:   string numeric fields → numeric
-- Adds:    price (now_cost / 10.0)
CREATE VIEW public.players AS
SELECT
    id, code, can_transact, can_select,
    chance_of_playing_next_round, chance_of_playing_this_round,
    cost_change_event, cost_change_event_fall, cost_change_start, cost_change_start_fall,
    price_change_percent::numeric,
    dreamteam_count, element_type,
    ep_next::numeric, ep_this::numeric,
    event_points, first_name, form::numeric,
    in_dreamteam, news, news_added,
    now_cost, now_cost / 10.0           AS price,
    photo, points_per_game::numeric,
    removed,
    second_name                         AS last_name,
    selected_by_percent::numeric,
    special, squad_number, status,
    team                                AS team_id,
    team_code, total_points,
    transfers_in, transfers_in_event, transfers_out, transfers_out_event,
    value_form::numeric, value_season::numeric,
    web_name, known_name, region, team_join_date, birth_date,
    has_temporary_code, opta_code,
    minutes, goals_scored, assists, clean_sheets, goals_conceded,
    own_goals, penalties_saved, penalties_missed, yellow_cards, red_cards,
    saves, bonus, bps,
    influence::numeric, creativity::numeric, threat::numeric, ict_index::numeric,
    clearances_blocks_interceptions, recoveries, tackles, defensive_contribution, starts,
    expected_goals::numeric, expected_assists::numeric,
    expected_goal_involvements::numeric, expected_goals_conceded::numeric,
    corners_and_indirect_freekicks_order, corners_and_indirect_freekicks_text,
    direct_freekicks_order, direct_freekicks_text,
    penalties_order, penalties_text,
    influence_rank, influence_rank_type, creativity_rank, creativity_rank_type,
    threat_rank, threat_rank_type, ict_index_rank, ict_index_rank_type,
    expected_goals_per_90, saves_per_90, expected_assists_per_90,
    expected_goal_involvements_per_90, expected_goals_conceded_per_90, goals_conceded_per_90,
    now_cost_rank, now_cost_rank_type, form_rank, form_rank_type,
    points_per_game_rank, points_per_game_rank_type,
    selected_rank, selected_rank_type,
    starts_per_90, clean_sheets_per_90, defensive_contribution_per_90,
    scout_risks, scout_news_link
FROM raw.players;

-- Renames: event → gameweek_id, team_h → team_h_id, team_a → team_a_id
CREATE VIEW public.fixtures AS
SELECT
    id, code,
    event                AS gameweek_id,
    finished, finished_provisional, kickoff_time, minutes, provisional_start_time, started,
    team_a               AS team_a_id,
    team_a_score,
    team_h               AS team_h_id,
    team_h_score,
    stats, team_h_difficulty, team_a_difficulty, pulse_id
FROM raw.fixtures;

-- Renames: element → player_id, round → gameweek_id, opponent_team → opponent_team_id
-- Casts:   string numeric fields → numeric
-- Adds:    match_price (value / 10.0), fdr, xpts
CREATE VIEW public.player_gameweek_stats AS
SELECT
    s.element                               AS player_id,
    s.fixture                               AS fixture_id,
    s.opponent_team                         AS opponent_team_id,
    s.total_points, s.was_home, s.kickoff_time, s.team_h_score, s.team_a_score,
    s.round                                 AS gameweek_id,
    s.modified, s.minutes, s.goals_scored, s.assists, s.clean_sheets,
    s.goals_conceded, s.own_goals, s.penalties_saved, s.penalties_missed,
    s.yellow_cards, s.red_cards, s.saves, s.bonus, s.bps,
    s.influence::numeric, s.creativity::numeric, s.threat::numeric, s.ict_index::numeric,
    s.clearances_blocks_interceptions, s.recoveries, s.tackles, s.defensive_contribution,
    s.starts,
    s.expected_goals::numeric, s.expected_assists::numeric,
    s.expected_goal_involvements::numeric, s.expected_goals_conceded::numeric,
    s.value,
    s.value / 10.0                          AS match_price,
    s.transfers_balance, s.selected, s.transfers_in, s.transfers_out,
    -- FDR from the player's perspective
    CASE
        WHEN s.was_home THEN f.team_h_difficulty
        ELSE f.team_a_difficulty
    END                                     AS fdr,
    -- Expected points: xG × goal pts by position + xA × 3 + xGC × -0.5 (GK/DEF only)
    ROUND(
        COALESCE(s.expected_goals::numeric, 0) * CASE p.element_type
            WHEN 1 THEN 6
            WHEN 2 THEN 6
            WHEN 3 THEN 5
            ELSE 4
        END
        + COALESCE(s.expected_assists::numeric, 0) * 3
        + CASE
            WHEN p.element_type IN (1, 2)
            THEN COALESCE(s.expected_goals_conceded::numeric, 0) * -0.5
            ELSE 0
          END
    , 2)                                    AS xpts
FROM raw.player_gameweek_stats s
JOIN raw.fixtures f ON f.id = s.fixture
JOIN raw.players  p ON p.id = s.element;

-- Season or GW-range aggregate per player.
-- Call with no args for full season; pass gw_from/gw_to to filter.
-- Matches the Streamlit player stats table: pos, team, player, price, st, mp, pts,
-- p90, gs90, a90, gi90, xg90, xa90, xgi90, cs, xgc, xgc90, tsb.
CREATE OR REPLACE FUNCTION public.player_stats(
    gw_from int DEFAULT NULL,
    gw_to   int DEFAULT NULL
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
      AND (gw_from IS NULL OR s.round >= gw_from)
      AND (gw_to   IS NULL OR s.round <= gw_to)
    GROUP BY p.id, p.element_type, t.short_name, p.web_name, p.now_cost, p.selected_by_percent
    HAVING SUM(s.minutes) > 0
    ORDER BY SUM(s.total_points) DESC
$$;
