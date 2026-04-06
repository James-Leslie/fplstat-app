import json

import polars as pl


def _prep_jsonb(value: object) -> object:
    """Serialize dict/list values to JSON strings for jsonb columns."""
    if isinstance(value, (dict, list)):
        return json.dumps(value)
    return value


def transform_teams(bootstrap: dict) -> pl.DataFrame:
    return pl.DataFrame(bootstrap["teams"])


def transform_gameweeks(bootstrap: dict) -> pl.DataFrame:
    jsonb_cols = {"overrides", "chip_plays", "top_element_info"}
    rows = [
        {k: _prep_jsonb(v) if k in jsonb_cols else v for k, v in row.items()}
        for row in bootstrap["events"]
    ]
    return pl.DataFrame(rows)


def transform_players(bootstrap: dict) -> pl.DataFrame:
    jsonb_cols = {"scout_risks"}
    rows = [
        {k: _prep_jsonb(v) if k in jsonb_cols else v for k, v in row.items()}
        for row in bootstrap["elements"]
    ]
    return pl.DataFrame(rows)


def transform_fixtures(fixtures: list[dict]) -> pl.DataFrame:
    jsonb_cols = {"stats"}
    rows = [
        {k: _prep_jsonb(v) if k in jsonb_cols else v for k, v in row.items()}
        for row in fixtures
    ]
    return pl.DataFrame(rows)


def transform_player_gameweek_stats(histories: dict[int, list[dict]]) -> pl.DataFrame:
    rows = [row for history in histories.values() for row in history]
    if not rows:
        return pl.DataFrame()
    return pl.DataFrame(rows)
