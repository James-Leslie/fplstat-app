# test/

Contract tests that verify the live FPL API matches our expected shape.

## What runs here

`test_api_contract.py` hits the real FPL endpoints and checks two things
per shape:

1. **Pydantic validation** (via `transforms._parse`) — types and required
   fields still match `src/fplstat/models.py`.
2. **Field-set snapshot** (via `_check_field_set`) — the full set of keys
   returned by the API is still a subset of what we've seen before.

Step 2 exists because all models use `ConfigDict(extra="allow")`, so a
new FPL field would slip through validation and then fail at Supabase
upsert with a confusing `PGRST204: column "foo" not found`. The snapshot
check flags it early with a readable message.

## Snapshots

`test/schemas/*.json` — one sorted list of known field names per endpoint
shape:

| File | Endpoint shape |
| --- | --- |
| `bootstrap_teams.json` | `/bootstrap-static/` → `teams[*]` |
| `bootstrap_events.json` | `/bootstrap-static/` → `events[*]` |
| `bootstrap_elements.json` | `/bootstrap-static/` → `elements[*]` |
| `fixtures.json` | `/fixtures/` → `[*]` |
| `element_summary_history.json` | `/element-summary/{id}/` → `history[*]` |

## When a contract test fails with "New fields detected …"

FPL has added a field we haven't seen before. Because every model uses
`extra="allow"`, unknown fields flow through `model_dump()` → Polars →
Supabase upsert, which then 400s with `PGRST204: column "foo" not found`.
So **updating the snapshot alone is not enough** — you also need to
decide what to do with the field downstream:

1. **Ingest it** — it's a stat we want:
   - Add the field to the relevant Pydantic model in `src/fplstat/models.py`.
   - Add the column to the matching `raw.*` table via a Supabase migration.
   - Extend the `public.*` view/RPC if it should be exposed to the app.
   - Update the snapshot (see below).

2. **Drop it** — we don't want to ingest it:
   - Add it to the Pydantic model and immediately drop it in
     `transforms.py` (e.g. via `df.drop("field_name")`) before it reaches
     `db._upsert`. This keeps the ETL resilient without bloating `raw.*`.
   - Update the snapshot.

### Updating the snapshot

```bash
UPDATE_SNAPSHOTS=1 uv run --group dev pytest test/ -v
git add test/schemas/
git commit -m "Update FPL field snapshot: add <field_name>"
```

The test will write each snapshot and skip. Commit the regenerated files.
Next run (without the env var) should pass.

## Running locally

```bash
# Steady-state: diff against committed snapshots.
uv run --group dev pytest test/ -v

# First-time bootstrap, or intentional refresh.
UPDATE_SNAPSHOTS=1 uv run --group dev pytest test/ -v
```

## CI

- `.github/workflows/tests.yml` runs on every PR and push to `main`.
- `.github/workflows/etl.yml` runs the same tests immediately before the
  daily ETL, so schema drift blocks ingest.
