from datetime import datetime

import polars as pl
from supabase import Client

_BATCH_SIZE = 500


def _serialize(value: object) -> object:
    if isinstance(value, datetime):
        return value.isoformat()
    return value


def _upsert(client: Client, table: str, df: pl.DataFrame) -> None:
    records = [
        {k: _serialize(v) for k, v in row.items()}
        for row in df.to_dicts()
    ]
    for i in range(0, len(records), _BATCH_SIZE):
        client.table(table).upsert(records[i : i + _BATCH_SIZE]).execute()


def upsert_teams(client: Client, df: pl.DataFrame) -> None:
    _upsert(client, "teams", df)


def upsert_gameweeks(client: Client, df: pl.DataFrame) -> None:
    _upsert(client, "gameweeks", df)


def upsert_players(client: Client, df: pl.DataFrame) -> None:
    _upsert(client, "players", df)


def upsert_fixtures(client: Client, df: pl.DataFrame) -> None:
    _upsert(client, "fixtures", df)


def upsert_player_gameweek_stats(client: Client, df: pl.DataFrame) -> None:
    _upsert(client, "player_gameweek_stats", df)
