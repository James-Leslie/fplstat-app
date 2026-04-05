-- Raw tables store FPL API data as-fetched, using original API field names.
-- All renaming and enrichment lives in public.* views (see 003, 004).

CREATE TABLE raw.teams (
    id                    int4  PRIMARY KEY,
    name                  text  NOT NULL,
    short_name            text  NOT NULL,
    strength_overall_home int4,
    strength_overall_away int4,
    strength_attack_home  int4,
    strength_attack_away  int4,
    strength_defence_home int4,
    strength_defence_away int4
);

CREATE TABLE raw.gameweeks (
    id                   int4        PRIMARY KEY,
    name                 text        NOT NULL,
    deadline_time        timestamptz NOT NULL,
    finished             bool        NOT NULL DEFAULT false,
    is_current           bool        NOT NULL DEFAULT false,
    average_entry_score  int4,       -- null for future gameweeks
    highest_score        int4        -- null for future gameweeks
);

CREATE TABLE raw.players (
    id                  int4        PRIMARY KEY,
    first_name          text        NOT NULL,
    second_name         text        NOT NULL,   -- API name for last name
    web_name            text        NOT NULL,
    team                int4        NOT NULL REFERENCES raw.teams(id),  -- API name for team_id
    element_type        int4        NOT NULL,   -- 1=GK 2=DEF 3=MID 4=FWD
    now_cost            int4        NOT NULL,   -- price x10 (e.g. 95 = £9.5m)
    status              text        NOT NULL,   -- a/d/i/s/u
    news                text,
    total_points        int4        NOT NULL DEFAULT 0,
    form                numeric,
    points_per_game     numeric,
    selected_by_percent numeric,
    minutes             int4        NOT NULL DEFAULT 0,
    goals_scored        int4        NOT NULL DEFAULT 0,
    assists             int4        NOT NULL DEFAULT 0,
    clean_sheets        int4        NOT NULL DEFAULT 0,
    bonus               int4        NOT NULL DEFAULT 0,
    bps                 int4        NOT NULL DEFAULT 0,
    influence           numeric,
    creativity          numeric,
    threat              numeric,
    ict_index           numeric,
    transfers_in        int4        NOT NULL DEFAULT 0,
    transfers_out       int4        NOT NULL DEFAULT 0,
    updated_at          timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX idx_raw_players_team ON raw.players(team);

CREATE TABLE raw.fixtures (
    id                int4        PRIMARY KEY,
    event             int4        REFERENCES raw.gameweeks(id),  -- API name for gameweek_id; null for blank gameweeks
    team_h            int4        NOT NULL REFERENCES raw.teams(id),
    team_a            int4        NOT NULL REFERENCES raw.teams(id),
    team_h_score      int4,       -- null until played
    team_a_score      int4,       -- null until played
    finished          bool        NOT NULL DEFAULT false,
    kickoff_time      timestamptz,
    team_h_difficulty int4,       -- FDR 1-5
    team_a_difficulty int4        -- FDR 1-5
);

CREATE INDEX idx_raw_fixtures_event ON raw.fixtures(event);

-- One row per player per fixture. PK is (player_id, fixture) — not (player_id, round) —
-- so double gameweeks (two fixtures in one gameweek) are handled correctly.
CREATE TABLE raw.player_gameweek_stats (
    player_id                  int4    NOT NULL REFERENCES raw.players(id),
    fixture                    int4    NOT NULL REFERENCES raw.fixtures(id),  -- API name for fixture_id
    round                      int4    NOT NULL REFERENCES raw.gameweeks(id), -- API name for gameweek_id
    opponent_team              int4    NOT NULL REFERENCES raw.teams(id),     -- API name for opponent_team_id
    was_home                   bool    NOT NULL,
    minutes                    int4    NOT NULL DEFAULT 0,
    total_points               int4    NOT NULL DEFAULT 0,
    goals_scored               int4    NOT NULL DEFAULT 0,
    assists                    int4    NOT NULL DEFAULT 0,
    clean_sheets               int4    NOT NULL DEFAULT 0,
    bonus                      int4    NOT NULL DEFAULT 0,
    bps                        int4    NOT NULL DEFAULT 0,
    influence                  numeric,
    creativity                 numeric,
    threat                     numeric,
    ict_index                  numeric,
    expected_goals             numeric,
    expected_assists           numeric,
    expected_goal_involvements numeric,
    expected_goals_conceded    numeric,
    value                      int4,   -- price at time of GW (x10)
    selected                   int4,   -- ownership count at time of GW
    transfers_in               int4    NOT NULL DEFAULT 0,
    transfers_out              int4    NOT NULL DEFAULT 0,
    PRIMARY KEY (player_id, fixture)
);

CREATE INDEX idx_raw_pgs_player  ON raw.player_gameweek_stats(player_id);
CREATE INDEX idx_raw_pgs_fixture ON raw.player_gameweek_stats(fixture);
CREATE INDEX idx_raw_pgs_round   ON raw.player_gameweek_stats(round);
