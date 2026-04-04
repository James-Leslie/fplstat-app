-- Double gameweeks mean a player can appear twice in the same gameweek (one row per fixture).
-- (player_id, gameweek_id) is therefore not unique.
-- Fix: add fixture_id and use (player_id, fixture_id) as the primary key instead.

ALTER TABLE player_gameweek_stats
    ADD COLUMN fixture_id int4 NOT NULL REFERENCES fixtures(id);

ALTER TABLE player_gameweek_stats
    DROP CONSTRAINT player_gameweek_stats_pkey;

ALTER TABLE player_gameweek_stats
    ADD PRIMARY KEY (player_id, fixture_id);
