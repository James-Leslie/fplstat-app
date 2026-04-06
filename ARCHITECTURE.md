# fplstat — Architecture

## Stack

| Layer | Tool |
|---|---|
| Frontend | Streamlit |
| Database | Supabase (Postgres) |
| Transformation | SQL views + Postgres functions |
| ETL | Python (`uv`) + httpx + Polars |
| Scheduling | GitHub Actions |

---

## Data flow

```
FPL API → etl/pipeline.py → raw.* (Supabase) → public.* views/functions → app/app.py
```

No API server layer. Streamlit connects directly to Supabase using the Python client.

---

## Repository layout

```
app/
  app.py                    # Streamlit frontend
etl/
  pipeline.py               # ETL entry point
src/fplstat/
  fpl_client.py             # FPL API fetch (sync + async httpx)
  transforms.py             # Raw API response → Polars DataFrames
  db.py                     # Supabase upsert helpers
db/
  tables/raw.sql            # raw schema + raw.* table definitions
  views/public.sql          # public.* views
  functions/player_stats.sql
  grants/raw_schema.sql
.github/workflows/
  etl.yml                   # Scheduled ETL (daily 07:00 UTC)
```

---

## ETL

**Principle: the ETL is a dumb loader.** Python fetches and copies; all transformation lives in SQL.

- Every field returned by the FPL API is stored in the raw schema as-is.
- No renaming, no derived columns, no dropped fields.
- All upserts use `ON CONFLICT DO UPDATE` — safe to rerun at any time.
- Player histories are fetched with `asyncio` + a semaphore (10 concurrent requests).
- Upserts are batched at 500 rows.

**Sources → raw tables:**

| FPL API endpoint | Raw table |
|---|---|
| `/bootstrap-static/` → `teams` | `raw.teams` |
| `/bootstrap-static/` → `events` | `raw.gameweeks` |
| `/bootstrap-static/` → `elements` | `raw.players` |
| `/fixtures/` | `raw.fixtures` |
| `/element-summary/{id}/` → `history` | `raw.player_gameweek_stats` |

---

## Database

### Schemas

```
raw.*     — FPL API data, as-fetched, no modifications
public.*  — Clean views and functions consumed by the frontend
```

### Views (`db/views/public.sql`)

| View | Purpose |
|---|---|
| `public.teams` | Passthrough with clean column names |
| `public.gameweeks` | Passthrough with clean column names |
| `public.players` | Renamed columns (`second_name → last_name`, `team → team_id`), string numerics cast to numeric, derived `price` |
| `public.fixtures` | Renamed FK columns |
| `public.player_gameweek_stats` | Renamed columns + derived `fdr` + `xpts` |

### Functions (`db/functions/player_stats.sql`)

| Function | Purpose |
|---|---|
| `public.player_stats(gw_from, gw_to, last_n)` | Season or GW-range aggregate per player. Pass `last_n` to select the N most recent finished gameweeks; pass `gw_from`/`gw_to` for an explicit range; omit all for full season. |

### Notes

- `raw.player_gameweek_stats` PK is `(element, fixture)`, not `(element, round)` — handles double gameweeks correctly.
- Prices are stored ×10 (FPL convention) and divided in `public.player_stats`.
- String-typed numeric fields (e.g. `influence`, `expected_goals`) are stored as `text` in raw tables and cast in views.

---

## Frontend

`app/app.py` connects to Supabase and renders a filterable player stats table.

- Supabase client cached with `@st.cache_resource`.
- Stats fetched with `@st.cache_data(ttl=300)` (5-minute cache).
- Filters (team, position, max price, min minutes, last N gameweeks) applied client-side after fetch.
- `last_n` passed to `player_stats` RPC; all other filters applied in-process on the returned DataFrame.

---

## Scheduling

GitHub Actions runs `etl/pipeline.py` daily at 07:00 UTC via `SUPABASE_URL` and `SUPABASE_KEY` repository secrets. Manual dispatch is also available.

---

## Key principles

- **ETL copies, SQL transforms.** Python never renames or derives — that is SQL's job.
- **No fields dropped.** Every API field lands in the raw schema, even if not currently used.
- **Views are the contract.** The frontend depends on `public.*` only; raw is internal.
- **Idempotent by default.** All upserts use `ON CONFLICT DO UPDATE`.
- **Simple scheduling.** GitHub Actions cron — no orchestration framework needed at this scale.
