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

    return df.select([
        "id",
        "first_name",
        pl.col("second_name").alias("last_name"),
        "web_name",
        pl.col("team").alias("team_id"),
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
    return pl.DataFrame(fixtures).select([
        "id",
        pl.col("event").alias("gameweek_id"),
        pl.col("team_h").alias("team_h_id"),
        pl.col("team_a").alias("team_a_id"),
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

    return df.select([
        "player_id",
        pl.col("fixture").alias("fixture_id"),
        pl.col("round").alias("gameweek_id"),
        pl.col("opponent_team").alias("opponent_team_id"),
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
