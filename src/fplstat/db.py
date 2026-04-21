import os
from datetime import datetime, timezone

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
        client.schema("raw").table(table).upsert(
            batch, on_conflict=on_conflict
        ).execute()


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


def insert_etl_run(client: Client) -> int:
    """Insert a new ETL run row and return its id."""
    row = client.schema("raw").table("etl_runs").insert({}).execute().data[0]
    return row["id"]


def complete_etl_run(client: Client, run_id: int) -> None:
    """Mark an ETL run as finished."""
    client.schema("raw").table("etl_runs").update(
        {"finished_at": datetime.now(timezone.utc).isoformat()}
    ).eq("id", run_id).execute()
