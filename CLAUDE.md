# fplstat — Claude Code Notes

## Package Management

This project uses [uv](https://docs.astral.sh/uv/) for Python package management.

- Add packages: `uv add <package>`
- Remove packages: `uv remove <package>`
- Run scripts: `uv run <script>`
- Never use `pip install` directly.

## Frontend (SvelteKit)

- Directory: `frontend/`
- Dev server: `cd frontend && pnpm dev`
- Type check: `cd frontend && pnpm run check`
- Uses `pnpm` for package management (not uv — that's Python only)
- API base URL configured via `frontend/.env` → `PUBLIC_API_BASE=http://localhost:8000`
- Backend must be running: `uv run fastapi dev api/main.py`
