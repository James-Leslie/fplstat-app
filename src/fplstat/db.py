import os
from datetime import datetime

import polars as pl
import psycopg2
import psycopg2.extras


def get_connection() -> psycopg2.extensions.connection:
    return psycopg2.connect(os.environ["DATABASE_URL"])


def _serialize(value: object) -> object:
    if isinstance(value, datetime):
        return value.isoformat()
    return value


def _upsert(
    conn: psycopg2.extensions.connection,
    table: str,
    df: pl.DataFrame,
    pk_cols: list[str],
) -> None:
    cols = df.columns
    records = [
        tuple(_serialize(row[c]) for c in cols)
        for row in df.to_dicts()
    ]

    col_list = ", ".join(cols)
    conflict_cols = ", ".join(pk_cols)
    non_pk_cols = [c for c in cols if c not in pk_cols]
    update_clause = ", ".join(f"{c} = EXCLUDED.{c}" for c in non_pk_cols)

    sql = f"""
        INSERT INTO raw.{table} ({col_list})
        VALUES %s
        ON CONFLICT ({conflict_cols}) DO UPDATE SET {update_clause}
    """

    with conn.cursor() as cur:
        psycopg2.extras.execute_values(cur, sql, records, page_size=500)
    conn.commit()


def upsert_teams(conn: psycopg2.extensions.connection, df: pl.DataFrame) -> None:
    _upsert(conn, "teams", df, ["id"])


def upsert_gameweeks(conn: psycopg2.extensions.connection, df: pl.DataFrame) -> None:
    _upsert(conn, "gameweeks", df, ["id"])


def upsert_players(conn: psycopg2.extensions.connection, df: pl.DataFrame) -> None:
    _upsert(conn, "players", df, ["id"])


def upsert_fixtures(conn: psycopg2.extensions.connection, df: pl.DataFrame) -> None:
    _upsert(conn, "fixtures", df, ["id"])


def upsert_player_gameweek_stats(conn: psycopg2.extensions.connection, df: pl.DataFrame) -> None:
    _upsert(conn, "player_gameweek_stats", df, ["element", "fixture"])
