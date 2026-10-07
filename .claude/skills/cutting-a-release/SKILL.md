---
name: cutting-a-release
description: Choose a version number and tag a release. Use when the user asks to release, version, or tag the project.
---

# Cutting a Release

1. Confirm `main` is green: `cd backend && ../.venv/bin/python -m pytest -q`.
2. Pick the version with SemVer:
   - **major** — breaking change to the `/api/*` shapes or the report JSON
   - **minor** — new capability (a new review dimension, input type, dashboard view)
   - **patch** — fixes, and prompt tweaks to `code-reviewer.md` that keep the schema
3. Summarize the changes since the last tag (`git log <last-tag>..HEAD --oneline`).
4. **Ask for explicit approval** before tagging. Then: `git tag -a vX.Y.Z -m "<summary>"`.
5. Never push the tag without separate explicit approval.
