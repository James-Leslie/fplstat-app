CREATE TABLE fixtures (
    id                int4        PRIMARY KEY,
    gameweek_id       int4        REFERENCES gameweeks(id),  -- nullable (blank/double gameweeks)
    team_h_id         int4        NOT NULL REFERENCES teams(id),
    team_a_id         int4        NOT NULL REFERENCES teams(id),
    team_h_score      int4,       -- null until played
    team_a_score      int4,       -- null until played
    finished          bool        NOT NULL DEFAULT false,
    kickoff_time      timestamptz,
    team_h_difficulty int4,       -- FDR 1-5
    team_a_difficulty int4        -- FDR 1-5
);

CREATE INDEX idx_fixtures_gw ON fixtures(gameweek_id);
