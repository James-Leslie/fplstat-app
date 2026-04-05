-- Public views over raw.* tables with clean, renamed columns.
-- These are what the API layer and frontend consume.
-- Renaming lives here so the ETL stays a dumb loader.

CREATE VIEW public.teams AS
SELECT
    id,
    name,
    short_name,
    strength_overall_home,
    strength_overall_away,
    strength_attack_home,
    strength_attack_away,
    strength_defence_home,
    strength_defence_away
FROM raw.teams;

CREATE VIEW public.gameweeks AS
SELECT
    id,
    name,
    deadline_time,
    finished,
    is_current,
    average_entry_score,
    highest_score
FROM raw.gameweeks;

CREATE VIEW public.players AS
SELECT
    id,
    first_name,
    second_name         AS last_name,
    web_name,
    team                AS team_id,
    element_type,
    now_cost,
    status,
    news,
    total_points,
    form,
    points_per_game,
    selected_by_percent,
    minutes,
    goals_scored,
    assists,
    clean_sheets,
    bonus,
    bps,
    influence,
    creativity,
    threat,
    ict_index,
    transfers_in,
    transfers_out,
    updated_at
FROM raw.players;

CREATE VIEW public.fixtures AS
SELECT
    id,
    event             AS gameweek_id,
    team_h            AS team_h_id,
    team_a            AS team_a_id,
    team_h_score,
    team_a_score,
    finished,
    kickoff_time,
    team_h_difficulty,
    team_a_difficulty
FROM raw.fixtures;

-- Enriched view adding derived columns over player_gameweek_stats.
--
-- fdr  — fixture difficulty the player's team faced (1–5 scale from FPL)
-- xpts — expected points:
--           xG × goal_pts_by_position  (GK/DEF=6, MID=5, FWD=4)
--         + xA × 3
--         + xGC × -0.5  (GK and DEF only)

CREATE VIEW public.player_gameweek_stats AS
SELECT
    s.player_id,
    s.fixture                       AS fixture_id,
    s.round                         AS gameweek_id,
    s.opponent_team                 AS opponent_team_id,
    s.was_home,
    s.minutes,
    s.total_points,
    s.goals_scored,
    s.assists,
    s.clean_sheets,
    s.bonus,
    s.bps,
    s.influence,
    s.creativity,
    s.threat,
    s.ict_index,
    s.expected_goals,
    s.expected_assists,
    s.expected_goal_involvements,
    s.expected_goals_conceded,
    s.value,
    s.selected,
    s.transfers_in,
    s.transfers_out,
    -- FDR from the player's perspective
    CASE
        WHEN s.was_home THEN f.team_h_difficulty
        ELSE f.team_a_difficulty
    END AS fdr,
    -- Expected points
    ROUND(
        COALESCE(s.expected_goals, 0) * CASE p.element_type
            WHEN 1 THEN 6  -- GK
            WHEN 2 THEN 6  -- DEF
            WHEN 3 THEN 5  -- MID
            ELSE 4         -- FWD
        END
        + COALESCE(s.expected_assists, 0) * 3
        + CASE
            WHEN p.element_type IN (1, 2)
            THEN COALESCE(s.expected_goals_conceded, 0) * -0.5
            ELSE 0
          END
    , 2) AS xpts
FROM raw.player_gameweek_stats s
JOIN raw.fixtures f ON f.id = s.fixture
JOIN raw.players  p ON p.id = s.player_id;
