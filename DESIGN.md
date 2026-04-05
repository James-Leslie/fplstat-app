# FPL Web Application — Phased Build Plan

## Stack Summary

| Layer | Tool |
|---|---|
| Frontend | SvelteKit |
| Backend / API | FastAPI (Python) |
| Data Transformation | Polars |
| Database | Supabase (Postgres) |
| Deployment | FastAPI Cloud |
| ETL / Scheduling | GitHub Actions (Phase 1) → Meltano (Phase 2+) |

---

## Phase 0 — API Exploration & Data Mapping

**Goal:** Understand what the FPL API actually provides before writing a single line of application code.

- Fetch a sample of real data from the FPL public API
  - Bootstrap endpoint (`/bootstrap-static/`) — players, teams, gameweeks
  - Player history endpoint (`/element-summary/{player_id}/`) — per-gameweek stats
  - Fixtures endpoint (`/fixtures/`) — match data
- Document the shape of each response (fields, types, nulls)
- Identify what data is available vs what needs to be derived (e.g. rolling 3/5 GW points)
- Define a target data model for Supabase — what tables, what columns
- **Deliverable:** Data dictionary + Supabase schema draft

---

## Phase 1 — Data Layer & ELT Pipeline

**Goal:** Get real FPL data flowing into Supabase on a schedule, with enrichments computed in SQL.

**Pattern: ELT (Extract → Load → Transform in SQL)**
- Python is a dumb loader: extract from FPL API, load into `raw.*` schema using original API field names
- All field renaming, enrichment, and derived columns live as SQL views in `public.*`

**Database layout:**
- `raw.*` — 5 tables (teams, gameweeks, players, fixtures, player_gameweek_stats) storing API data as-fetched
- `public.*` — views over raw with renamed columns, transparent to the API layer
- `public.player_gameweek_enriched` — enriched view adding:
  - `fdr` — opposition fixture difficulty rating (joined from fixtures)
  - `xpts` — expected points: `xG × goal_pts_by_position + xA × 3 + xGC × −0.5 (GK/DEF only)`

**Decisions made:**
- Prices stored ×10 (FPL convention), divided in API/frontend layer
- Rolling points windows (last N GWs) computed at query time, not stored
- PK for player_gameweek_stats is `(player_id, fixture_id)` — not `(player_id, gameweek_id)` — to correctly handle double gameweeks
- Pipeline is full-refresh for now; incremental (re-fetch only players who played in latest GW) is a future optimisation

**FastAPI endpoints (`api/main.py`):** `/teams`, `/gameweeks`, `/fixtures`, `/players`, `/players/{id}`, `/players/{id}/stats`, `/leaderboard?last_n=N`. Run locally with `uv run fastapi dev api/main.py`.

**Deliverable:** Supabase populated with enriched data + FastAPI serving it locally — **Phase 1 complete.**

---

## Phase 2 — Frontend Skeleton with Real Data

**Goal:** Stand up a SvelteKit app connected to real data from the FastAPI layer.

- Initialise SvelteKit project
- Connect to FastAPI endpoints
- Build core pages:
  - Player leaderboard (most points in last N gameweeks — configurable)
  - Player detail view (gameweek-by-gameweek breakdown)
  - Team overview
- Keep styling minimal at this stage — focus on data correctness
- **Deliverable:** Working app with real FPL data rendered in the browser

---

## Phase 3 — UI Polish & Feature Expansion

**Goal:** Make the app genuinely useful and enjoyable to use.

- Improve styling and UX
- Add filtering and sorting controls (by position, team, price, ownership)
- Add comparison views (e.g. player A vs player B over last 5 GWs)
- Add visualisations (e.g. form charts, points over time)
- Mobile responsiveness
- **Deliverable:** Polished, feature-rich UI

---

## Phase 4 — Deployment

**Goal:** Get the app live and accessible.

- Deploy FastAPI backend to FastAPI Cloud
- Deploy SvelteKit frontend (Vercel or similar)
- Confirm GitHub Actions pipeline runs correctly against production Supabase
- Set up environment variables and secrets management
- **Deliverable:** Publicly accessible app

---

## Phase 5 — ETL Maturity (Optional)

**Goal:** Replace the hand-rolled GitHub Actions pipeline with a more structured ETL tool.

- Evaluate Meltano as a replacement for the custom pipeline
- Implement proper incremental sync, change data capture, and pipeline observability
- Consider adding dbt for SQL-based transformation models alongside Polars
- **Deliverable:** Production-grade, maintainable ETL pipeline

---

## Key Principles

- **Data-first:** Understand the source before building the UI
- **Incremental delivery:** Each phase produces something working and usable
- **Keep it simple:** Start with GitHub Actions; only introduce Meltano when the complexity justifies it
- **Use Claude Code:** Lean on it to learn SvelteKit and explore patterns you wouldn't attempt solo