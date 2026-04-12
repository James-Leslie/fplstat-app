---
name: commit-changes
description: Commit unstaged changes to git. Use this when you have made changes to files and want to create a git commit with those changes.
---

Please commit unstaged changes to the git repository.

Follow these steps exactly:

1. Run `git status` and `git diff` to review what has changed.
2. Review whether all staged changes belong to the same logical unit of work. A commit should represent a single, complete, describable change — cohesion matters more than file count. If unrelated changes are present, stage selectively rather than committing everything at once.
3. Stage the appropriate changes and run `uv run prek run` to apply pre-commit hooks.
4. Commit with a meaningful, present-tense message describing what and why.
