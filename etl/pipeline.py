import time

from dotenv import load_dotenv

from fplstat.db import (
    get_connection,
    upsert_fixtures,
    upsert_gameweeks,
    upsert_player_gameweek_stats,
    upsert_players,
    upsert_teams,
)
from fplstat.fpl_client import fetch_bootstrap, fetch_fixtures, fetch_player_histories
from fplstat.transforms import (
    transform_fixtures,
    transform_gameweeks,
    transform_player_gameweek_stats,
    transform_players,
    transform_teams,
)


def _step(label: str) -> float:
    print(f"  {label}...", end=" ", flush=True)
    return time.monotonic()


def _done(t0: float) -> None:
    print(f"done ({time.monotonic() - t0:.1f}s)")


def run() -> None:
    load_dotenv()

    pipeline_start = time.monotonic()
    print("=== FPL ETL pipeline ===")

    t = _step("Fetching bootstrap-static")
    bootstrap = fetch_bootstrap()
    _done(t)

    t = _step("Fetching fixtures")
    fixtures = fetch_fixtures()
    _done(t)

    player_ids = [p["id"] for p in bootstrap["elements"]]
    t = _step(f"Fetching histories for {len(player_ids)} players (async, 10 concurrent)")
    histories = fetch_player_histories(player_ids)
    _done(t)

    print("  Transforming...", end=" ", flush=True)
    t = time.monotonic()
    teams_df = transform_teams(bootstrap)
    gameweeks_df = transform_gameweeks(bootstrap)
    players_df = transform_players(bootstrap)
    fixtures_df = transform_fixtures(fixtures)
    stats_df = transform_player_gameweek_stats(histories)
    _done(t)

    t = _step("Connecting to database")
    conn = get_connection()
    _done(t)

    t = _step(f"Upserting {len(teams_df)} teams")
    upsert_teams(conn, teams_df)
    _done(t)

    t = _step(f"Upserting {len(gameweeks_df)} gameweeks")
    upsert_gameweeks(conn, gameweeks_df)
    _done(t)

    t = _step(f"Upserting {len(players_df)} players")
    upsert_players(conn, players_df)
    _done(t)

    t = _step(f"Upserting {len(fixtures_df)} fixtures")
    upsert_fixtures(conn, fixtures_df)
    _done(t)

    t = _step(f"Upserting {len(stats_df)} player_gameweek_stats rows")
    upsert_player_gameweek_stats(conn, stats_df)
    _done(t)

    conn.close()
    print(f"=== Done in {time.monotonic() - pipeline_start:.1f}s ===")


if __name__ == "__main__":
    run()
