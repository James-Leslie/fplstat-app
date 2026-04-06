# FPL Stat — Design

## Stack

| Layer | Tool |
|---|---|
| Frontend | Streamlit |
| Database | Supabase (Postgres) |
| Data transformation | SQL views + Postgres functions |
| ETL | Python (uv) → Supabase |
| Scheduling | GitHub Actions |

---

## Architecture

```
FPL API → Python ETL → raw.* schema → public.* views/functions → Streamlit
```

No API server layer. Streamlit connects directly to Supabase using the Python client.

---

## ETL — Extract & Load

**Principle: the ETL is a dumb loader. It copies the FPL API response into Supabase with zero field dropping and zero transformation.**

- Every field returned by the FPL API is stored in the raw schema.
- Field names are kept exactly as the API returns them.
- No renaming, no casting beyond what Postgres requires, no derived columns.
- Upserts are idempotent — safe to rerun at any time.

**Sources:**

| Endpoint | Raw table |
|---|---|
| `/bootstrap-static/` → `teams` | `raw.teams` |
| `/bootstrap-static/` → `events` | `raw.gameweeks` |
| `/bootstrap-static/` → `elements` | `raw.players` |
| `/fixtures/` | `raw.fixtures` |
| `/element-summary/{id}/` → `history` | `raw.player_gameweek_stats` |

---

## Transformation — SQL Views & Functions

All renaming, enrichment, and derived columns live in `public.*`. Raw tables are never queried directly by the frontend.

**Views:**

| View | Purpose |
|---|---|
| `public.teams` | Passthrough with clean column names |
| `public.gameweeks` | Passthrough with clean column names |
| `public.players` | Passthrough with clean column names (`second_name → last_name`, `team → team_id`, etc.) |
| `public.fixtures` | Passthrough with clean column names + derived `fdr` |
| `public.player_gameweek_stats` | Enriched per-GW stats: renamed columns + `fdr` + `xpts` |

**Functions:**

| Function | Purpose |
|---|---|
| `public.player_stats(gw_from, gw_to)` | Season or GW-range aggregate per player: per-90 stats, starts, xG, xA, CS, TSB%, etc. Matches the Streamlit player stats table. |

---

## Frontend — Streamlit

The existing Streamlit app connects to Supabase and queries `public.*` views and functions.

**Key interactions:**
- Player stats table: `supabase.rpc('player_stats', {})` — full season
- GW-filtered stats: `supabase.rpc('player_stats', {'gw_from': N, 'gw_to': M})`
- Filters (team, position, price, minutes) applied client-side in Streamlit after fetching

---

## Database Layout

```
raw.*          — FPL API data, as-fetched, no modifications
public.*       — Clean views and functions consumed by the frontend
```

**Primary keys:**
- `raw.player_gameweek_stats`: `(player_id, fixture)` — not `(player_id, round)` — so double gameweeks are handled correctly.

**Prices** stored ×10 (FPL convention), divided to £ in the `public.player_stats` function.

---

## Migrations

Stored in `db/migrations/` and applied via Supabase MCP. Numbered sequentially.

| File | Description |
|---|---|
| `001_create_raw_schema.sql` | Create `raw` schema |
| `002_create_raw_tables.sql` | Raw tables |
| `003_create_public_views.sql` | Public views |
| `004_player_stats_function.sql` | `player_stats` aggregate function |
| `005_add_starts_to_player_gameweek_stats.sql` | Add `starts` column |

---

## Key Principles

- **ETL copies, SQL transforms.** Python never derives or renames — that is SQL's job.
- **No fields dropped.** Every API field lands in the raw schema, even if not currently used.
- **Views are the contract.** The Streamlit app depends on `public.*` only; raw schema is internal.
- **Idempotent by default.** All upserts use `ON CONFLICT DO UPDATE` — rerunning is always safe.
- **Simple scheduling.** GitHub Actions triggers the ETL on a cron. No orchestration framework needed at this scale.
