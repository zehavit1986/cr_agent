# 001 — AI Code Reviewer & Quality Dashboard

Status: done
Owner: zehavit
Last updated: 2026-10-07

## Goal
A web app where a developer submits a source file (GitHub URL, paste, or upload) and an AI
agent returns a style review, bug detection, security warnings, suggested refactors and
auto-generated tests, shown on a quality dashboard. First target:
`https://github.com/zehavit1986/ai4dev-agent-files/blob/main/10-messages.py`.

## Scope
- Backend: Python 3.12 + FastAPI in `backend/app/`.
- AI: the `code-reviewer` agent defined in `.claude/agents/code-reviewer.md`, run with the
  Claude Agent SDK — no direct Anthropic SDK calls in application code.
- Frontend: static dashboard in `frontend/`.
- Workspace structure modeled on `vyaron/ai4dev-agent-files`: `AGENTS.md`, `CLAUDE.md`,
  `.doc/`, `.plan/`, `.claude/{agents,rules,skills,hooks}`, `.orchestrate/`.

## Assumptions
- Single-user local tool; reports stored as files in `reports/`.
- `ANTHROPIC_API_KEY` in `.env`; `GITHUB_TOKEN` optional.
- macOS/Linux, so the agent's Bash sandbox is available.

## Open Que
stions
- Q1: Review whole repositories? — Recommended: not in this plan; backlog item added.
- Q2: Keep the reference repo's "Hopa!" reply rule and Hooha output style? — Answered: no.

## Steps
1. GitHub fetcher with host allow-list and size cap (`backend/app/github.py`).
2. Pydantic `Review` schema; deterministic scoring (`schema.py`, `scoring.py`).
3. `code-reviewer.md` agent; loader (`agent.py`); SDK runner in a sandboxed temp workspace
   with structured output (`reviewer.py`).
4. Pipeline, storage, Markdown export, API and CLI (`service.py`, `store.py`, `server.py`, `cli.py`).
5. Dashboard (`frontend/`).
6. Workspace structure, Python guardrail hooks, role agents, rules, skills, docs.
7. Backend test suite (`backend/tests/`).

## Validation
- `cd backend && ../.venv/bin/python -m pytest -q` passes (AC01–AC07).
- `python -m app.cli <target URL>` produces a report with all five dimensions (AC04, AC08).
- The generated `test_10_messages.py` passes offline with no API key (AC09).
- Dashboard at 375px has `scrollWidth == innerWidth`; dark mode tokens apply (AC10).
- Each hook blocks its case and allows the safe case when fed a sample payload.

## Risks
- Executing untrusted code: mitigated by the OS sandbox with no unsandboxed escape.
- Prompt injection inside reviewed code: the agent has no network, no secrets, and output is
  schema-validated and rendered as text.
- Cost/latency (~1 min per review): capped by `maxTurns` and `REVIEW_MAX_BUDGET_USD`.

## Rollout Order
Backend → agent → frontend → workspace docs/hooks → tests.

## Rollback
Remove `.claude/settings.json` hooks if they misfire; reports are disposable.
