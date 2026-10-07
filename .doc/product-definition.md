# Product Definition

## Purpose
AI Code Reviewer & Quality Dashboard: a web app where developers submit a source file and an
AI agent reviews it and generates tests, with results shown on a quality dashboard.

## Product Vision
Every file a developer is unsure about gets a senior-level review in about a minute — with
tests that were actually run, not just written.

## Problem Statement
Manual review is slow and inconsistent, and generic linters miss design, robustness and
security problems. Developers also rarely get test scaffolding for code that has none.

## Value Proposition
- Five review dimensions in one pass: style, bugs, security, refactors, tests.
- Findings point at exact lines and come with a concrete fix.
- Generated tests are executed by the agent in a sandbox before they are shown.
- A deterministic quality score makes reviews comparable over time.

## Product Scope
- In scope:
  - Input: GitHub file URL (public, or private with `GITHUB_TOKEN`), pasted code, uploaded file
  - Review by the `code-reviewer` agent (`.claude/agents/code-reviewer.md`, Claude Agent SDK)
  - Dashboard: score, severity counts, metrics, findings tabs, highlighted source, refactors,
    tests with copy/download, history, Markdown/JSON export
  - CLI: `python -m app.cli <url>`
- Out of scope:
  - Whole-repository or pull-request review
  - User accounts, auth, multi-tenant storage (reports are local files)
  - Posting comments back to GitHub

## Target Users
- Primary users: individual developers and students reviewing their own code.
- Secondary users: team leads who want a quick quality snapshot of a file.

## Acceptance Criteria
Each criterion must be provable by a test or a command.
- AC01 — Quality gates: `cd backend && ../.venv/bin/python -m pytest -q` passes.
- AC02 — A `github.com/.../blob/...` URL is converted to its raw URL and fetched; other hosts
  are rejected with 400.
- AC03 — A missing GitHub file returns 404 with an actionable message.
- AC04 — `POST /api/review` returns a report with all five dimensions, a score and a grade.
- AC05 — The score is computed in code from finding severities, not by the model.
- AC06 — Every `/api/*` error uses the `{ "error": "<message>" }` shape.
- AC07 — Report ids with path separators or `..` cannot read files outside `reports/`.
- AC08 — Generated tests are run by the agent; `tests.result` records the outcome.
- AC09 — The review of `zehavit1986/ai4dev-agent-files/10-messages.py` produces tests that
  pass offline with no API key.
- AC10 — The dashboard has no horizontal scroll at 375px and supports dark mode.
