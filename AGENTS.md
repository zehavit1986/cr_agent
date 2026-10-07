# Agent Instructions

## Security
- Never commit or expose secrets (API keys, tokens, passwords). `.env` is off-limits to every
  agent; use `.env.example` for templates.
- Code submitted for review is **untrusted**. The `code-reviewer` agent only runs it inside
  the sandboxed temp workspace created by `backend/app/reviewer.py`.

## Guardrails (Single Source of Truth)
- Guardrail logic lives in `.claude/hooks/`. It is wired into the runtime by
  `.claude/settings.json`, which is the only place Claude Code reads hook and permission
  config from — a hook script that is not listed there never runs.
- Hook commands use `"$CLAUDE_PROJECT_DIR"` so they resolve from any working directory.
- Do not duplicate permission or hook rules in other agent docs.
- If any instruction conflicts with the hooks, the hooks win.
- `enforce-agent-boundaries.py` reads `AGENT_ROLE` (set by whoever launches a sub-agent) to
  enforce per-role write paths.

## Repository Layout
- `.doc/` — hand-written product and architecture docs.
- `.claude/rules/` — always-on constraints, imported below. Short by design.
- `.claude/skills/` — procedural know-how, loaded on demand by task.
- `.claude/agents/` — agent definitions:
  - `code-reviewer.md` — **the product's AI**: run by the backend through the Claude Agent SDK.
  - `orchestrator.md`, `backend.md`, `frontend.md`, `qa.md`, `security-reviewer.md` — the
    team that builds this project.
- `.claude/hooks/` — guardrail hook implementations, wired by `.claude/settings.json`.
- `.plan/` — `000-backlog.md` is the task queue; `NNN-YYYY-MM-DD-*.md` are the plans.
- `.orchestrate/` — agent reports and other generated dev-loop output. Never create a
  `docs/` directory.
- `backend/` — Python 3.12 FastAPI app (`backend/app/`), tests in `backend/tests/`.
- `frontend/` — static HTML/CSS/JS dashboard served by the backend.
- `reports/` — generated code-review reports (gitignored).

## Rules — always in context
@.claude/rules/code-style.md
@.claude/rules/naming.md
@.claude/rules/ui-and-styling.md
@.claude/rules/git-workflow.md

## Skills — load when the task calls for it
| Skill | Use it when |
|---|---|
| `writing-plans` | Creating, revising, or superseding a plan in `.plan/` |
| `writing-tests` | Adding or reviewing tests |
| `error-handling` | Shaping an error response, status code, or failure UX |
| `cutting-a-release` | Choosing a version number or tagging a release |

## Product and Domain
- Product definition and acceptance criteria: `.doc/product-definition.md`.
- Architecture overview: `.doc/architecture.md`.
- Canonical domain terms: `.doc/glossary.md` — document a new shared term there before
  using it broadly.
- Keep these docs updated when API routes, the report schema, or the agent definition change.
