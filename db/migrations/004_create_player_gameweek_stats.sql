-- NOTE: amended by migration 006 — fixture_id added, PK changed to (player_id, fixture_id)
-- to correctly handle double gameweeks where a player plays twice in one gameweek.
-- Rolling points windows (last N GWs) are derived at query time, not stored.
CREATE TABLE player_gameweek_stats (
    player_id                  int4    NOT NULL REFERENCES players(id),
    gameweek_id                int4    NOT NULL REFERENCES gameweeks(id),
    opponent_team_id           int4    NOT NULL REFERENCES teams(id),
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
    PRIMARY KEY (player_id, gameweek_id)
);

CREATE INDEX idx_pgs_player   ON player_gameweek_stats(player_id);
CREATE INDEX idx_pgs_gameweek ON player_gameweek_stats(gameweek_id);
