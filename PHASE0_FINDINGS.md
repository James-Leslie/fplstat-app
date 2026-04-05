# Phase 0 — FPL API Exploration: Findings & Recommendations

## Endpoints Explored

| Endpoint | Purpose |
|---|---|
| `GET /api/bootstrap-static/` | Players, teams, gameweek metadata |
| `GET /api/element-summary/{player_id}/` | Per-gameweek stats for a single player |
| `GET /api/fixtures/` | All match fixtures |

All endpoints are public and require no authentication.

---

## Data Summary

| Source | Rows | Columns | Notes |
|---|---|---|---|
| `bootstrap["elements"]` (players) | 825 | 105 | 0 nulls |
| `bootstrap["teams"]` | 20 | 23 | 0 nulls |
| `bootstrap["events"]` (gameweeks) | 38 | 29 | 7 nulls in `highest_score` (future GWs) |
| `fixtures` | 380 | 23 | Scores null until played |
| `element-summary[].history` | ~30/player | 42 | Per-GW, one API call per player |

Season started **2025-08-15**. At time of exploration: 1 current gameweek, 1 next gameweek, 36 finished.

---

## Key Findings

### 1. String fields that look numeric

Several fields in `element-summary` history come back as **String**, not Float:

- `influence`, `creativity`, `threat`, `ict_index`
- `expected_goals`, `expected_assists`, `expected_goal_involvements`, `expected_goals_conceded`

**Action:** Cast all of these to `Float64` in the ETL transform before writing to Supabase.

### 2. Price is stored × 10

`now_cost` and `value` (in history) are integers scaled by 10. £9.5m is stored as `95`.

**Action:** Either store raw (and divide in the frontend), or normalise in ETL. Recommend storing raw and handling in the API/frontend layer for precision.

### 3. Player status codes

`status` field uses single-character codes:

| Code | Meaning |
|---|---|
| `a` | Available |
| `d` | Doubtful |
| `i` | Injured |
| `s` | Suspended |
| `u` | Unavailable |

### 4. element-summary requires one request per player

There is no bulk history endpoint. Fetching all 825 players would require 825 sequential (or batched parallel) HTTP requests.

**Action:** In Phase 1, parallelise with `asyncio` + `httpx.AsyncClient`, or batch with a thread pool. Rate-limit to avoid bans (~5–10 req/s is safe in practice).

### 5. Rolling points windows are derivable

`pts_rolling_3gw` and `pts_rolling_5gw` are not provided by the API — they must be computed. Polars `rolling_sum(...).over("player_id")` handles this cleanly after sorting by round.

### 6. Fixture difficulty ratings (FDR) are available

`team_h_difficulty` and `team_a_difficulty` (1–5 scale) are on the fixtures endpoint. Useful for future "schedule difficulty" features.

### 7. No incremental endpoint

The API has no "changes since timestamp" endpoint. Every refresh requires a full fetch of `bootstrap-static` and fixtures. Player history only needs re-fetching for players who played in the latest gameweek.

**Action:** In ETL, track `current_gameweek_id` between runs. Only re-fetch `element-summary` for players with `minutes > 0` in the newly completed gameweek.

---

## Recommendations for Phase 1

1. **Fetch strategy:** Fetch `bootstrap-static` and `fixtures` on every ETL run (cheap, ~2 requests). Only re-fetch `element-summary` for players who appeared in the latest finished gameweek.

2. **Parallelise player history fetches** using `asyncio` + `httpx.AsyncClient` — target ~10 concurrent requests to stay well within rate limits.

3. **Cast string numerics early** in the Polars transform pipeline, before any downstream calculations.

4. **Upsert, don't insert** — use Supabase's `upsert` (on conflict do update) for all tables. The FPL API can retroactively correct scores for several hours after a gameweek finishes.

5. **Schedule ETL hourly during active gameweeks**, daily otherwise. A gameweek is "active" when `is_current = True` and `deadline_time < now`.

6. **Store `updated_at` on the `players` table** to make it easy to detect staleness and debug ETL runs.
