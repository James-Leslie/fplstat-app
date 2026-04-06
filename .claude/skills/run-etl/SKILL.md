---
name: run-etl
description: Run the FPL ETL pipeline, either locally or by triggering the GitHub Actions workflow.
---

Run the FPL ETL pipeline using one of the two methods below.

## Local run

Use this when you want to fetch fresh data immediately in your local environment:

```bash
uv run etl/pipeline.py
```

Requires a `.env` file in the project root with:

```
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-service-role-key
```

The pipeline is idempotent — safe to re-run at any time, all upserts use `ON CONFLICT DO UPDATE`.

## Remote run (GitHub Actions)

Use this to trigger the production ETL run via GitHub Actions:

```bash
gh workflow run etl.yml
```

To watch the run as it executes:

```bash
gh run watch
```

Or to view recent runs:

```bash
gh run list --workflow=etl.yml
```

The workflow also runs automatically on a daily schedule at **07:00 UTC**.
