import polars as pl
from pydantic import ValidationError

from fplstat.models import Fixture, Gameweek, Player, PlayerGameweekStat, Team


def _parse(model_cls, items: list[dict], label: str) -> list[dict]:
    """Validate a list of raw API dicts through a Pydantic model.

    Collects all failures before raising so one bad row doesn't hide others.
    """
    errors: list[str] = []
    parsed: list[dict] = []
    for i, item in enumerate(items):
        try:
            parsed.append(model_cls.model_validate(item).model_dump())
        except ValidationError as exc:
            errors.append(f"  [{label}] row {i} id={item.get('id', '?')}: {exc}")
    if errors:
        raise ValueError(
            f"Validation failed for {len(errors)} {label} row(s):\n" + "\n".join(errors)
        )
    return parsed


def transform_teams(bootstrap: dict) -> pl.DataFrame:
    return pl.DataFrame(_parse(Team, bootstrap["teams"], "teams"))


def transform_gameweeks(bootstrap: dict) -> pl.DataFrame:
    return pl.DataFrame(_parse(Gameweek, bootstrap["events"], "gameweeks"))


def transform_players(bootstrap: dict) -> pl.DataFrame:
    return pl.DataFrame(_parse(Player, bootstrap["elements"], "players"))


def transform_fixtures(fixtures: list[dict]) -> pl.DataFrame:
    return pl.DataFrame(_parse(Fixture, fixtures, "fixtures"))


def transform_player_gameweek_stats(histories: dict[int, list[dict]]) -> pl.DataFrame:
    rows = [row for history in histories.values() for row in history]
    if not rows:
        return pl.DataFrame()
    return pl.DataFrame(_parse(PlayerGameweekStat, rows, "player_gameweek_stats"))
