# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

# fplstat

A self-service analytics app for Fantasy Premier League players.

## Development environment

- **Python**: Use `uv` for ALL operations — see the **python-project-management** skill, or run `uv help`
- **Streamlit**: `uv run streamlit run app/app.py`
- **ETL**: `uv run python etl/pipeline.py`
- **Lint/format**: `uv run prek run` (runs ruff check + format via pre-commit hooks)
- **Supabase**: Use the Supabase MCP server for all database migrations
- **Git**: Use `gh` and `git`

There are no automated tests; the `/test` directory is a placeholder for future coverage.

## Architecture

```
FPL API → etl/pipeline.py → raw.* (Supabase) → public.* views/functions → app/app.py
```

**ETL copies, SQL transforms.** Python fetches and validates (Pydantic); all renaming, casting, and derived columns live in SQL. Never rename or derive in Python.

**Views are the contract.** The frontend consumes `public.*` only. `raw.*` is internal to the ETL.

### Key layers

| Layer | Location | Purpose |
|---|---|---|
| FPL API client | `src/fplstat/fpl_client.py` | `httpx` sync + async fetch |
| Validation | `src/fplstat/models.py` | Pydantic models with `extra="allow"` |
| Transform | `src/fplstat/transforms.py` | API response → Polars DataFrames |
| DB upsert | `src/fplstat/db.py` | Batched upserts (500 rows) to `raw.*` |
| ETL entry point | `etl/pipeline.py` | Orchestrates fetch → validate → upsert |
| Raw schema | `db/tables/raw.sql` | Five raw tables (teams, gameweeks, players, fixtures, player_gameweek_stats) |
| Public views | `db/views/public.sql` | Column renames, numeric casts, `fdr` and `xpts` derived columns |
| RPC functions | `db/functions/` | `player_stats()` and `player_history()` |
| Data cache | `app/data.py` | Supabase client + `@st.cache_data(ttl=300)` fetchers |
| Frontend | `app/pages/stats.py`, `app/pages/fdr_matrix.py` | Streamlit UI |

### Database schema design

- `raw.*` stores every FPL API field as-is. String-typed numeric fields (e.g. `expected_goals`, `influence`) are stored as `text` in raw and cast to `numeric` in the public views.
- `raw.player_gameweek_stats` PK is `(element, fixture)` — not `(element, round)` — to correctly handle double gameweeks.
- `public.player_gameweek_stats` derives `fdr` (fixture difficulty rating) and `xpts` (expected points). The `xpts` formula uses xG/xA/xGC via position multipliers plus actual counts for saves, bonus, cards, etc. — see `db/views/public.sql` for the full expression.
- `public.player_stats(gw_from, gw_to, last_n, include_current)` is the main RPC called by the frontend. It returns one aggregated row per player with per-game and per-90 rates plus a `pp90` breakdown by scoring category.

### Frontend structure

`app/app.py` is a thin router using `st.navigation()`. Pages live in `app/pages/`.

`app/data.py` centralises all Supabase calls and caching — add new data fetchers here rather than inline in pages.

`app/pages/stats.py` is the largest file (~714 lines). It applies filters client-side on the DataFrame returned by the `player_stats` RPC, handles three view modes (Total / Per Game / Per 90), and renders a player detail modal with fixture strip, charts, and per-gameweek history.

FDR colour constants are defined in `app/style.py` and shared across pages.

## Code style

- **Comments**: Add a comment whenever the intent behind a block of code is not immediately obvious — explain *why*, not *what*.
- **YAGNI**: Implement what is needed now; extend later when the need is real.
- **DRY**: Extract shared behaviour into a reusable function or module rather than copying across files.
- **Maintainability over cleverness**: Follow existing conventions and patterns. If a simpler approach achieves the same result, prefer it.

## Workflow

1. **Plan**: devise a detailed implementation plan to be signed off by the user
2. **Implement**: make considered, surgical changes; keep the user involved for UX feedback
3. **Test**: add coverage in `/test` for any new functionality
4. **Commit**: small, targeted commits with short messages
5. Repeat steps 3–4 until all plan steps are complete
6. **Push**: push all commits; ensure no unstaged changes before moving on
