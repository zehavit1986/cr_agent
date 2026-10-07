# Git Workflow

## Approval gates — no exceptions
- **Never commit** until the user explicitly approves committing.
- **Never merge** a branch without explicit approval.
- **Never push a release tag** without explicit approval.

## Branches
- Do implementation work on a dedicated branch, never on `main`.
- One plan or workstream per branch. Lowercase names:
  `feat/<topic>`, `fix/<topic>`, `chore/<topic>`, `docs/<topic>`.

## Commits
- Imperative subject, concise: `add paste-code review input`.
- One intent per commit. Never commit `.env`, `.venv/`, `reports/` output or `.orchestrate/` output.

Release tagging and version numbers are a separate procedure — see the `cutting-a-release` skill.
