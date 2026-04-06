# fplstat

A Streamlit dashboard for Fantasy Premier League player statistics.

## Overview

fplstat fetches data from the official FPL API, stores it in Supabase, and exposes it through an interactive player stats table. Filters let you slice by team, position, price, minutes played, and gameweek range.

## Stack

- **Frontend**: Streamlit
- **Database**: Supabase (PostgreSQL)
- **ETL**: Python + httpx (async) + Polars
- **Package manager**: uv

## Project structure

```
app/
  app.py                  # Streamlit frontend
src/fplstat/
  fpl_client.py           # FPL API client
  models.py               # Pydantic models for API validation
  transforms.py           # API response → Polars DataFrames
  db.py                   # Supabase upsert helpers
etl/
  pipeline.py             # ETL orchestrator
db/
  tables/raw.sql          # raw schema + tables
  views/public.sql        # public views (type casts, derived columns, xpts)
  functions/player_stats.sql  # player_stats() RPC function
  grants/raw_schema.sql   # service_role grants
```

## Database design

Raw FPL API data lands in a `raw` schema (five tables: `teams`, `gameweeks`, `players`, `fixtures`, `player_gameweek_stats`). A `public` schema sits on top with views that rename columns, cast string-numeric fields, and add derived columns — including `xpts` (expected points) and `fdr` (fixture difficulty rating).

The `player_stats()` Postgres function aggregates per-game stats into a single row per player, with optional filtering by gameweek range or last N gameweeks.

### xpts formula

Expected points are calculated per game using a mix of expected stats (xG, xA, xGC) and actual counts for components that have no expected equivalent:

| Component | Source |
|---|---|
| Appearance (1 or 2 pts) | actual minutes |
| Goals | xG × position multiplier (6/5/4) |
| Assists | xA × 3 |
| Clean sheet probability | Poisson: e^(−xGC) × position multiplier (4/4/1/0) |
| Goals conceded deduction | ⌊xGC / 2⌋ × −1 (GK/DEF only) |
| Saves bonus | ⌊saves / 3⌋ (GK only) |
| Cards, own goals, penalties, bonus | actual counts |

## Setup

### Prerequisites

- [uv](https://docs.astral.sh/uv/)
- A Supabase project

### Environment variables

Create a `.env` file:

```
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-service-role-key
```

### Apply database schema

Run each file in `db/` against your Supabase project (via the SQL editor or `mcp__supabase__apply_migration`):

1. `db/tables/raw.sql`
2. `db/grants/raw_schema.sql`
3. `db/views/public.sql`
4. `db/functions/player_stats.sql`

### Run the ETL

```bash
uv run python etl/pipeline.py
```

Fetches current season data from the FPL API and upserts into Supabase. Safe to re-run — all upserts use `ON CONFLICT`.

### Run the app

```bash
uv run streamlit run app/app.py
```
