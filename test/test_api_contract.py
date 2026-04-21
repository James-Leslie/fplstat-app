"""Contract tests: verify the live FPL API still matches our Pydantic models.

Run before the ETL in CI so schema drift fails fast, before any writes.

Two layers of checking per endpoint:
1. Pydantic validation via ``transforms._parse`` — catches type flips and
   missing required fields.
2. Field-set snapshot via ``_check_field_set`` — flags *new* fields FPL
   has added, which the ``extra="allow"`` models would otherwise let
   through silently (and blow up later at the Supabase upsert).

See test/README.md for how to update the snapshots when FPL legitimately
adds a field.
"""

import json
import os
from pathlib import Path


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

SCHEMAS = Path(__file__).parent / "schemas"
_UPDATE_ENV = "UPDATE_SNAPSHOTS"


def _check_field_set(rows: list[dict], snapshot_path: Path, label: str) -> None:
    """Assert the union of keys across ``rows`` matches the committed snapshot.

    New fields (in API, not in snapshot) fail with a readable per-field
    report. Missing fields (in snapshot, not in API) are not flagged here —
    those surface via Pydantic when a required model field disappears.

    If ``UPDATE_SNAPSHOTS=1`` is set, writes the snapshot and skips. Used
    for first-time bootstrap and for intentional updates.
    """
    actual = set()
    for row in rows:
        actual.update(row.keys())

    update_mode = os.environ.get(_UPDATE_ENV) == "1"

    if update_mode:
        snapshot_path.parent.mkdir(parents=True, exist_ok=True)
        snapshot_path.write_text(json.dumps(sorted(actual), indent=2) + "\n")
        return

    if not snapshot_path.exists():
        raise AssertionError(
            f"Missing snapshot for {label}: {snapshot_path}\n"
            f"Bootstrap it with:\n"
            f"  {_UPDATE_ENV}=1 uv run --group dev pytest test/ -v\n"
            f"then commit the file. See test/README.md."
        )

    expected = set(json.loads(snapshot_path.read_text()))
    new_fields = actual - expected
    if not new_fields:
        return

    lines = [
        f"New fields detected in {label}",
        "-" * 60,
        f"{len(new_fields)} field(s) not in {snapshot_path.relative_to(Path.cwd()) if snapshot_path.is_absolute() else snapshot_path}:",
        "",
    ]
    for field in sorted(new_fields):
        example = next(
            (row[field] for row in rows if field in row and row[field] is not None),
            None,
        )
        lines.append(f"  - {field!r:30s} (example value: {example!r})")
    lines += [
        "",
        "If these are intentional FPL additions, update the snapshot:",
        f"  {_UPDATE_ENV}=1 uv run --group dev pytest test/ -v",
        "and commit the regenerated file. See test/README.md.",
    ]
    raise AssertionError("\n".join(lines))


def test_bootstrap_and_fixtures_match_schema():
    """bootstrap-static (teams, events, elements) and fixtures parse cleanly."""
    bootstrap = fetch_bootstrap()
    _parse(Team, bootstrap["teams"], "teams")
    _check_field_set(
        bootstrap["teams"], SCHEMAS / "bootstrap_teams.json", "bootstrap.teams"
    )

    _parse(Gameweek, bootstrap["events"], "gameweeks")
    _check_field_set(
        bootstrap["events"], SCHEMAS / "bootstrap_events.json", "bootstrap.events"
    )

    _parse(Player, bootstrap["elements"], "players")
    _check_field_set(
        bootstrap["elements"], SCHEMAS / "bootstrap_elements.json", "bootstrap.elements"
    )

    fixtures = fetch_fixtures()
    _parse(Fixture, fixtures, "fixtures")
    _check_field_set(fixtures, SCHEMAS / "fixtures.json", "fixtures")


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
        _check_field_set(
            rows, SCHEMAS / "element_summary_history.json", "element_summary.history"
        )
