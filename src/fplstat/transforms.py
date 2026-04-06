import polars as pl


def transform_teams(bootstrap: dict) -> pl.DataFrame:
    return pl.DataFrame(bootstrap["teams"])


def transform_gameweeks(bootstrap: dict) -> pl.DataFrame:
    return pl.DataFrame(bootstrap["events"])


def transform_players(bootstrap: dict) -> pl.DataFrame:
    return pl.DataFrame(bootstrap["elements"])


def transform_fixtures(fixtures: list[dict]) -> pl.DataFrame:
    return pl.DataFrame(fixtures)


def transform_player_gameweek_stats(histories: dict[int, list[dict]]) -> pl.DataFrame:
    rows = [row for history in histories.values() for row in history]
    if not rows:
        return pl.DataFrame()
    return pl.DataFrame(rows)
