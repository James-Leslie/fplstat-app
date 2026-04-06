---
name: python-project-management
description: Python project management with uv. Use for all things to do with python scripts and virtual environments.
---

# Python Development

Use `uv` for ALL Python operations. Never use bare `pip`, `python`, or `poetry` commands.

## Common Commands

| Task | Command |
|------|---------|
| Run a script | `uv run <script.py>` |
| Add dependency | `uv add <package>` |
| Add dev dependency | `uv add --dev <package>` |
| Remove dependency | `uv remove <package>` |
| Sync dependencies | `uv sync` |
| Type check | `uvx ty check` |
| Run tests | `uv run pytest` |
| Bump version | `uv version --bump patch` (or `minor`/`major`) |
| Edit notebook | `uv run marimo edit notebooks/<name>.py` |
| Check notebooks | `uv run marimo check notebooks/` |

Prefer the `uv` CLI over editing `pyproject.toml` directly.

> Reference: [uv Documentation](https://docs.astral.sh/uv/)
