# AI Code Reviewer & Quality Dashboard

Give it a GitHub file URL, pasted code, or an uploaded file. The **`code-reviewer` agent**
(`.claude/agents/code-reviewer.md`, run by the Claude Agent SDK) returns:

- **Style review** · **Bug detection** · **Security warnings** · **Suggested refactors** · **Auto-generated tests**

The agent also **runs the generated tests** in a sandbox before reporting. The dashboard shows a
0–100 quality score, findings by severity, the source with flagged lines highlighted, before/after
refactors, and the test file with its run result.

## Setup

Requires Python 3.12+ (installed here via `uv python install 3.12`).

```bash
python3.12 -m venv .venv
.venv/bin/pip install -r backend/requirements.txt
cp .env.example .env        # then set ANTHROPIC_API_KEY
```

## Run

```bash
.venv/bin/python -m uvicorn app.server:app --app-dir backend --port 3000   # dashboard: http://localhost:3000
cd backend && ../.venv/bin/python -m app.cli <github file url>              # headless review → reports/
cd backend && ../.venv/bin/python -m pytest -q                              # test suite
```

## Changing how reviews work

Edit **`.claude/agents/code-reviewer.md`**, not Python. Its frontmatter sets `model`, `effort`,
`tools` and `maxTurns`, and its body is the agent's instructions. The backend loads it on
every review.

## Repository map

| Path | Purpose |
|---|---|
| `AGENTS.md` | Canonical rules and guardrails for all agents |
| `CLAUDE.md` | Loads `AGENTS.md` into Claude Code |
| `.doc/` | Product definition, architecture, glossary |
| `.plan/` | Backlog (`000-backlog.md`) and implementation plans |
| `.claude/agents/` | `code-reviewer` (the product's AI) + orchestrator, backend, frontend, qa, security-reviewer |
| `.claude/rules/` | Always-on code style, naming, UI, git rules |
| `.claude/skills/` | writing-plans, writing-tests, error-handling, cutting-a-release |
| `.claude/hooks/` | Python guardrails: secret-file access, destructive commands, agent write boundaries |
| `.claude/settings.json` | Wires the hooks and permission denies |
| `.orchestrate/` | Generated agent reports (gitignored) |
| `backend/` | FastAPI app (`backend/app/`) and tests (`backend/tests/`) |
| `frontend/` | Dashboard (HTML/CSS/JS) |
| `reports/` | Generated code-review reports (gitignored) |

See `.doc/architecture.md` for the data flow and the sandbox design.

## run
http://localhost:3000/

.venv/bin/python -m uvicorn app.server:app --app-dir backend --port 3000

url: https://github.com/zehavit1986/ai4dev-agent-files


https://github.com/zehavit1986/cr_agent


