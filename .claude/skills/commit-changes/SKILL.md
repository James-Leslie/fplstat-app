---
name: commit-changes
description: Commit unstaged changes to git. Use this when you have made changes to files and want to create a git commit with those changes.
---

Please commit unstaged changes to the git repository.

Follow these steps exactly:

1. Ensure we are on a safe branch (not `main` or `master`). If on a protected branch, stop and ask which branch to use.
1. Run `git status` and `git diff` to review what has changed.
1. Run `uv run pytest` if any Python source files have changed.
1. Review whether all staged changes belong to the same logical unit of work. A commit should represent a single, complete, describable change — cohesion matters more than file count. If unrelated changes are present, stage selectively rather than committing everything at once.
1. Stage the appropriate changes and run `uv run prek run` to apply pre-commit hooks.
1. Commit with a meaningful, present-tense message describing what and why.
1. Push the branch to the remote: `git push origin $(git branch --show-current)`
