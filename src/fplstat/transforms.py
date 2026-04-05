from datetime import datetime, timezone

import polars as pl

# Fields the FPL API returns as strings but should be numeric
_PLAYER_STRING_COLS = ["influence", "creativity", "threat", "ict_index"]
_PLAYER_NUMERIC_COLS = ["form", "points_per_game", "selected_by_percent"]
_STAT_STRING_COLS = [
    "influence", "creativity", "threat", "ict_index",
    "expected_goals", "expected_assists",
    "expected_goal_involvements", "expected_goals_conceded",
]


def transform_teams(bootstrap: dict) -> pl.DataFrame:
    return pl.DataFrame(bootstrap["teams"]).select([
        "id", "name", "short_name",
        "strength_overall_home", "strength_overall_away",
        "strength_attack_home", "strength_attack_away",
        "strength_defence_home", "strength_defence_away",
    ])


def transform_gameweeks(bootstrap: dict) -> pl.DataFrame:
    return pl.DataFrame(bootstrap["events"]).select([
        "id", "name", "deadline_time", "finished", "is_current",
        "average_entry_score", "highest_score",
    ])


def transform_players(bootstrap: dict) -> pl.DataFrame:
    df = pl.DataFrame(bootstrap["elements"])

    cast_cols = _PLAYER_STRING_COLS + _PLAYER_NUMERIC_COLS
    df = df.with_columns([
        pl.col(c).cast(pl.Float64) for c in cast_cols if c in df.columns
    ])

    # Keep original API field names — renaming to last_name / team_id happens in public.players view
    return df.select([
        "id",
        "first_name",
        "second_name",   # renamed to last_name in public.players view
        "web_name",
        "team",          # renamed to team_id in public.players view
        "element_type",
        "now_cost",
        "status",
        "news",
        "total_points",
        "form",
        "points_per_game",
        "selected_by_percent",
        "minutes",
        "goals_scored",
        "assists",
        "clean_sheets",
        "bonus",
        "bps",
        "influence",
        "creativity",
        "threat",
        "ict_index",
        "transfers_in",
        "transfers_out",
        pl.lit(datetime.now(timezone.utc)).alias("updated_at"),
    ])


def transform_fixtures(fixtures: list[dict]) -> pl.DataFrame:
    # Keep original API field names — renaming to gameweek_id / team_h_id / team_a_id
    # happens in public.fixtures view
    return pl.DataFrame(fixtures).select([
        "id",
        "event",       # renamed to gameweek_id in public.fixtures view
        "team_h",      # renamed to team_h_id in public.fixtures view
        "team_a",      # renamed to team_a_id in public.fixtures view
        "team_h_score",
        "team_a_score",
        "finished",
        "kickoff_time",
        "team_h_difficulty",
        "team_a_difficulty",
    ])


def transform_player_gameweek_stats(histories: dict[int, list[dict]]) -> pl.DataFrame:
    rows = [
        {**row, "player_id": player_id}
        for player_id, history in histories.items()
        for row in history
    ]

    if not rows:
        return pl.DataFrame()

    df = pl.DataFrame(rows)

    df = df.with_columns([
        pl.col(c).cast(pl.Float64) for c in _STAT_STRING_COLS if c in df.columns
    ])

    # Keep original API field names — renaming to fixture_id / gameweek_id / opponent_team_id
    # happens in public.player_gameweek_stats view
    return df.select([
        "player_id",
        "fixture",        # renamed to fixture_id in public.player_gameweek_stats view
        "round",          # renamed to gameweek_id in public.player_gameweek_stats view
        "opponent_team",  # renamed to opponent_team_id in public.player_gameweek_stats view
        "was_home",
        "minutes",
        "total_points",
        "goals_scored",
        "assists",
        "clean_sheets",
        "bonus",
        "bps",
        "influence",
        "creativity",
        "threat",
        "ict_index",
        "expected_goals",
        "expected_assists",
        "expected_goal_involvements",
        "expected_goals_conceded",
        "value",
        "selected",
        "transfers_in",
        "transfers_out",
    ])
