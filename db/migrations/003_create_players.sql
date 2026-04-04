CREATE TABLE players (
    id                  int4        PRIMARY KEY,
    first_name          text        NOT NULL,
    last_name           text        NOT NULL,
    web_name            text        NOT NULL,
    team_id             int4        NOT NULL REFERENCES teams(id),
    element_type        int4        NOT NULL,  -- 1=GK 2=DEF 3=MID 4=FWD
    now_cost            int4        NOT NULL,  -- price x10 (e.g. 95 = £9.5m)
    status              text        NOT NULL,  -- a/d/i/s/u
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
    influence           numeric,    -- cast from string in ETL
    creativity          numeric,    -- cast from string in ETL
    threat              numeric,    -- cast from string in ETL
    ict_index           numeric,    -- cast from string in ETL
    transfers_in        int4        NOT NULL DEFAULT 0,
    transfers_out       int4        NOT NULL DEFAULT 0,
    updated_at          timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX idx_players_team ON players(team_id);
