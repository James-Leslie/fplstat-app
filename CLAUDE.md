# fplstat

A self-service analytics app for Fantasy Premier League players.

See @README.md for project overview and @ARCHITECTURE.md for an outline of the stack used in this project.

# Development environment:

- **Git**: Use `gh` and `git`
- **Supabase** Use the supabase mcp server for interacting with the backend, including database migrations
- **Python**: Use `uv` for ALL operations - see the **python-project-management** skill for details, or use `uv help`
- **Streamlit**: Use `uv run streamlit run app/app.py` to launch the app for you or the user to view in the browser

# Code style

- **Comments**: Prefer well-commented code. Add a comment whenever the intent behind a block of code is not immediately obvious from reading it — explain *why*, not just *what*.
- **YAGNI**: Don't build for hypothetical future requirements. Implement what is needed now; extend later when the need is real.
- **DRY**: Avoid duplicating logic. Extract shared behaviour into a reusable function or module rather than copying code across files.

# Workflow

All work is to be done in the following loop:

1. Plan: devise a detailed implementation plan to be signed off by the user
2. Implement: make considered, surgical changes, keep the user involved as you go if they can do UX testing or provide general feedback
3. Test: for any new functionality, add coverage in @/test
4. Commit: make targeted commits with short messages, commits should be small and often
5. Repeat steps 3-5 until all steps in the implementation plan are complete
6. Push: push all commits and ensure there are no unstaged changes before moving on
