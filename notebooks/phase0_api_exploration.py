# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "marimo",
#   "httpx",
#   "polars",
# ]
# ///

import marimo

__generated_with = "0.22.3"
app = marimo.App(width="full")


@app.cell
def _():
    import marimo as mo
    import httpx
    import polars as pl

    return httpx, mo, pl


@app.cell
def _(mo):
    mo.md("""
    # FPL API Exploration — Phase 0
    """)
    return


@app.cell
def _(mo):
    mo.md("""
    ## Endpoints under investigation

    | Endpoint | Purpose |
    |---|---|
    | `/bootstrap-static/` | Players, teams, gameweek meta |
    | `/element-summary/{player_id}/` | Per-gameweek player stats |
    | `/fixtures/` | Match data |
    """)
    return


@app.cell
def _(httpx, mo):
    BASE_URL = "https://fantasy.premierleague.com/api"
    with mo.status.spinner(title="Fetching bootstrap-static..."):
        bootstrap_resp = httpx.get(f"{BASE_URL}/bootstrap-static/", timeout=30)
        bootstrap = bootstrap_resp.json()
    mo.md(f"**bootstrap-static** — status `{bootstrap_resp.status_code}`, keys: `{list(bootstrap.keys())}`")
    return BASE_URL, bootstrap


@app.cell
def _(bootstrap, mo, pl):
    players_df = pl.DataFrame(bootstrap["elements"])
    mo.md(f"### Players (`elements`) — {len(players_df)} rows × {len(players_df.columns)} columns")
    return (players_df,)


@app.cell
def _(mo, pl, players_df):
    schema_df = pl.DataFrame([
        {"column": c, "dtype": str(t)} for c, t in players_df.schema.items()
    ])
    mo.vstack([
        mo.md("#### Players schema"),
        mo.ui.table(schema_df),
    ])
    return


@app.cell
def _(mo, pl, players_df):
    null_counts = players_df.null_count()
    nulls_with_data = null_counts.unpivot(
        variable_name="column", value_name="null_count"
    ).filter(pl.col("null_count") > 0)
    if len(nulls_with_data) == 0:
        mo.md("**No null values** in players table.")
    else:
        mo.vstack([
            mo.md("#### Columns with nulls"),
            mo.ui.table(nulls_with_data),
        ])
    return


@app.cell
def _(mo, players_df):
    key_cols = [
        "id", "web_name", "team", "element_type",
        "total_points", "now_cost", "selected_by_percent",
        "form", "points_per_game", "minutes", "goals_scored",
        "assists", "clean_sheets", "bonus", "bps",
        "influence", "creativity", "threat", "ict_index",
        "transfers_in", "transfers_out", "status", "news",
    ]
    available = [c for c in key_cols if c in players_df.columns]
    top_players = players_df.select(available).sort("total_points", descending=True).head(10)
    mo.vstack([
        mo.md("#### Top 10 players by total points"),
        mo.ui.table(top_players),
    ])
    return


@app.cell
def _(bootstrap, mo, pl):
    teams_df = pl.DataFrame(bootstrap["teams"])
    teams_preview = teams_df.select([
        c for c in ["id", "name", "short_name", "strength", "strength_overall_home", "strength_overall_away"]
        if c in teams_df.columns
    ])
    mo.vstack([
        mo.md(f"### Teams — {len(teams_df)} rows × {len(teams_df.columns)} columns"),
        mo.ui.table(teams_preview),
    ])
    return


@app.cell
def _(bootstrap, mo, pl):
    events_df = pl.DataFrame(bootstrap["events"])
    gw_cols = [
        c for c in ["id", "name", "deadline_time", "finished", "is_current", "is_next",
                    "average_entry_score", "highest_score"]
        if c in events_df.columns
    ]
    mo.vstack([
        mo.md(f"### Gameweeks (`events`) — {len(events_df)} rows × {len(events_df.columns)} columns"),
        mo.ui.table(events_df.select(gw_cols)),
    ])
    return


@app.cell
def _(httpx, mo, pl):
    with mo.status.spinner(title="Fetching fixtures..."):
        fixtures_resp = httpx.get("https://fantasy.premierleague.com/api/fixtures/", timeout=30)
        fixtures_df = pl.DataFrame(fixtures_resp.json())
    mo.md(f"### Fixtures — {len(fixtures_df)} rows × {len(fixtures_df.columns)} columns")
    return (fixtures_df,)


@app.cell
def _(fixtures_df, mo):
    fix_cols = [
        c for c in ["id", "event", "team_h", "team_a", "team_h_score", "team_a_score",
                    "finished", "kickoff_time", "team_h_difficulty", "team_a_difficulty"]
        if c in fixtures_df.columns
    ]
    mo.vstack([
        mo.md("#### Fixtures sample (first 10)"),
        mo.ui.table(fixtures_df.select(fix_cols).head(10)),
    ])
    return


@app.cell
def _(BASE_URL, bootstrap, httpx, mo, pl):
    _top_ids = (
        pl.DataFrame(bootstrap["elements"])
        .sort("total_points", descending=True)
        .head(3)
        .select("id")["id"]
        .to_list()
    )
    _histories = []
    with mo.status.spinner(title=f"Fetching element-summary for player IDs {_top_ids}..."):
        for _pid in _top_ids:
            _resp = httpx.get(f"{BASE_URL}/element-summary/{_pid}/", timeout=30)
            _data = _resp.json()
            for _row in _data.get("history", []):
                _row["player_id"] = _pid
            _histories.extend(_data.get("history", []))
    history_df = pl.DataFrame(_histories) if _histories else pl.DataFrame()
    mo.md(f"### Player History (top 3 players) — {len(history_df)} rows × {len(history_df.columns)} columns")
    return (history_df,)


@app.cell
def _(history_df, mo):
    mo.vstack([
        mo.md("#### History schema"),
        mo.plain_text("\n".join(f"  {c}: {t}" for c, t in history_df.schema.items())),
    ])
    return


@app.cell
def _(history_df, mo):
    key_hist_cols = [c for c in [
        "player_id", "round", "total_points", "minutes", "goals_scored",
        "assists", "clean_sheets", "bonus", "bps", "influence",
        "creativity", "threat", "ict_index", "value", "selected",
        "transfers_in", "transfers_out", "was_home", "opponent_team",
    ] if c in history_df.columns]
    mo.vstack([
        mo.md("#### History sample (15 rows)"),
        mo.ui.table(history_df.select(key_hist_cols).head(15)),
    ])
    return


@app.cell
def _(history_df, mo, pl):
    rolling_df = (
        history_df.sort(["player_id", "round"])
        .with_columns([
            pl.col("total_points")
              .rolling_sum(window_size=3, min_samples=1)
              .over("player_id")
              .alias("pts_rolling_3gw"),
            pl.col("total_points")
              .rolling_sum(window_size=5, min_samples=1)
              .over("player_id")
              .alias("pts_rolling_5gw"),
        ])
    )
    mo.vstack([
        mo.md("#### Rolling GW points (derivable in ETL)"),
        mo.ui.table(rolling_df.select(
            ["player_id", "round", "total_points", "pts_rolling_3gw", "pts_rolling_5gw"]
        )),
    ])
    return


@app.cell
def _(mo):
    mo.md("""
    ---

    ## Proposed Supabase Schema

    ### `teams`
    | column | type | notes |
    |---|---|---|
    | id | int4 PK | FPL team id |
    | name | text | Full name |
    | short_name | text | 3-char code |
    | strength_overall_home | int4 | |
    | strength_overall_away | int4 | |
    | strength_attack_home | int4 | |
    | strength_attack_away | int4 | |
    | strength_defence_home | int4 | |
    | strength_defence_away | int4 | |

    ### `gameweeks`
    | column | type | notes |
    |---|---|---|
    | id | int4 PK | GW number (1–38) |
    | name | text | e.g. "Gameweek 1" |
    | deadline_time | timestamptz | |
    | finished | bool | |
    | is_current | bool | |
    | average_entry_score | int4 | nullable |
    | highest_score | int4 | nullable |

    ### `players`
    | column | type | notes |
    |---|---|---|
    | id | int4 PK | FPL element id |
    | web_name | text | |
    | team_id | int4 FK → teams.id | |
    | element_type | int4 | 1=GK 2=DEF 3=MID 4=FWD |
    | now_cost | int4 | price x 10 (e.g. 95 = 9.5m) |
    | status | text | a/d/i/s/u |
    | news | text | nullable |
    | total_points | int4 | season total |
    | form | numeric | rolling avg |
    | points_per_game | numeric | |
    | selected_by_percent | numeric | |
    | minutes | int4 | |
    | goals_scored | int4 | |
    | assists | int4 | |
    | clean_sheets | int4 | |
    | bonus | int4 | |
    | bps | int4 | |
    | influence | numeric | |
    | creativity | numeric | |
    | threat | numeric | |
    | ict_index | numeric | |
    | transfers_in | int4 | season total |
    | transfers_out | int4 | season total |
    | updated_at | timestamptz | set by ETL |

    ### `player_gameweek_stats`
    | column | type | notes |
    |---|---|---|
    | id | int8 PK | surrogate |
    | player_id | int4 FK -> players.id | |
    | gameweek_id | int4 FK -> gameweeks.id | |
    | opponent_team_id | int4 FK -> teams.id | |
    | was_home | bool | |
    | minutes | int4 | |
    | total_points | int4 | |
    | goals_scored | int4 | |
    | assists | int4 | |
    | clean_sheets | int4 | |
    | bonus | int4 | |
    | bps | int4 | |
    | influence | numeric | |
    | creativity | numeric | |
    | threat | numeric | |
    | ict_index | numeric | |
    | value | int4 | price at time of GW |
    | selected | int4 | ownership count |
    | transfers_in | int4 | GW transfers in |
    | transfers_out | int4 | GW transfers out |
    | pts_rolling_3gw | int4 | derived -- sum of last 3 GWs |
    | pts_rolling_5gw | int4 | derived -- sum of last 5 GWs |

    ### `fixtures`
    | column | type | notes |
    |---|---|---|
    | id | int4 PK | FPL fixture id |
    | gameweek_id | int4 FK -> gameweeks.id | nullable (BGW) |
    | team_h_id | int4 FK -> teams.id | |
    | team_a_id | int4 FK -> teams.id | |
    | team_h_score | int4 | nullable until played |
    | team_a_score | int4 | nullable until played |
    | finished | bool | |
    | kickoff_time | timestamptz | |
    | team_h_difficulty | int4 | FDR 1-5 |
    | team_a_difficulty | int4 | FDR 1-5 |

    ---
    Derived columns (pts_rolling_3gw, pts_rolling_5gw) are computed in Polars during ETL and written directly to player_gameweek_stats.
    """)
    return


if __name__ == "__main__":
    app.run()
