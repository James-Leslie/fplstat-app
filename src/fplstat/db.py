import os

import polars as pl
from supabase import Client, create_client

_BATCH_SIZE = 500


def get_client() -> Client:
    return create_client(
        os.environ["SUPABASE_URL"],
        os.environ["SUPABASE_KEY"],
    )


def _upsert(client: Client, table: str, df: pl.DataFrame, on_conflict: str) -> None:
    records = df.to_dicts()
    if not records:
        return
    for i in range(0, len(records), _BATCH_SIZE):
        batch = records[i : i + _BATCH_SIZE]
        client.schema("raw").table(table).upsert(batch, on_conflict=on_conflict).execute()


def upsert_teams(client: Client, df: pl.DataFrame) -> None:
    _upsert(client, "teams", df, "id")


def upsert_gameweeks(client: Client, df: pl.DataFrame) -> None:
    _upsert(client, "gameweeks", df, "id")


def upsert_players(client: Client, df: pl.DataFrame) -> None:
    _upsert(client, "players", df, "id")


def upsert_fixtures(client: Client, df: pl.DataFrame) -> None:
    _upsert(client, "fixtures", df, "id")


def upsert_player_gameweek_stats(client: Client, df: pl.DataFrame) -> None:
    _upsert(client, "player_gameweek_stats", df, "element,fixture")
