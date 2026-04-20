"""Contract tests: verify the live FPL API still matches our Pydantic models.

Run before the ETL in CI so schema drift fails fast, before any writes.
"""

from fplstat.fpl_client import (
    fetch_bootstrap,
    fetch_fixtures,
    fetch_player_histories,
)
from fplstat.models import (
    Fixture,
    Gameweek,
    Player,
    PlayerGameweekStat,
    Team,
)
from fplstat.transforms import _parse


def test_bootstrap_and_fixtures_match_schema():
    """bootstrap-static (teams, events, elements) and fixtures parse cleanly."""
    bootstrap = fetch_bootstrap()
    _parse(Team, bootstrap["teams"], "teams")
    _parse(Gameweek, bootstrap["events"], "gameweeks")
    _parse(Player, bootstrap["elements"], "players")

    fixtures = fetch_fixtures()
    _parse(Fixture, fixtures, "fixtures")


def test_player_history_matches_schema():
    """element-summary history rows parse cleanly for a sample of players."""
    bootstrap = fetch_bootstrap()
    # Small sample keeps the test fast and polite to the FPL API.
    sample_ids = [p["id"] for p in bootstrap["elements"][:5]]
    histories = fetch_player_histories(sample_ids)
    rows = [row for history in histories.values() for row in history]
    # Histories can legitimately be empty early in a season.
    if rows:
        _parse(PlayerGameweekStat, rows, "player_gameweek_stats")
