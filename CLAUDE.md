# fplstat

## Package Management

This project uses [uv](https://docs.astral.sh/uv/) for Python package management.

- Add packages: `uv add <package>`
- Remove packages: `uv remove <package>`
- Run scripts: `uv run <script>`
- Never use `pip install` directly.

## Frontend (Streamlit)

- Launch the app: `uv run streamlit run app/app.py`

## Database

- Canonical SQL source files live in `db/` subdirectories (`db/views/`, `db/functions/`, `db/tables/`, `db/grants/`).
- To apply schema changes: edit the canonical source file, then apply via `mcp__supabase__apply_migration`.
