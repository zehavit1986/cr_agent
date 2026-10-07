# System Architecture

## Purpose
A concise reference for components, data flow, and where responsibilities live.

## Primary Components
| Component | Path | Responsibility |
|---|---|---|
| Dashboard | `frontend/` | Static HTML/CSS/JS. Submits reviews, renders reports and history |
| API | `backend/app/server.py` | FastAPI routes, error handlers, serves `frontend/` |
| Review pipeline | `backend/app/service.py` | Fetch/validate input → run agent → score → save |
| GitHub fetcher | `backend/app/github.py` | Blob URL → raw URL, host allow-list, 500 KB cap |
| Agent loader | `backend/app/agent.py` | Parses `.claude/agents/<name>.md` (YAML frontmatter + prompt) |
| Agent runner | `backend/app/reviewer.py` | Runs `code-reviewer` with the Claude Agent SDK, returns `Review` |
| Review agent | `.claude/agents/code-reviewer.md` | The review instructions, model, effort, tools, turn limit |
| Scoring | `backend/app/scoring.py` | Deterministic 0–100 score and A–F grade |
| Store | `backend/app/store.py` | Reports as JSON in `reports/` |
| CLI | `backend/app/cli.py` | Headless review → JSON, Markdown and test file |

## Data Flow
1. Dashboard `POST /api/review` with `{kind: github|paste|upload, url | code, filename}`.
2. `service.run_review` fetches the file (GitHub) or validates the pasted code.
3. `reviewer.review_code` creates a temp workspace containing only the file, then runs the
   `code-reviewer` agent there via `claude_agent_sdk.query()`:
   - system prompt, model, effort, tools and max turns come from the agent `.md`
   - `output_format` is the JSON Schema of `schema.Review`, so the result is structured
   - the agent reads the file, reviews it, writes a test file and runs it with pytest
4. The `ResultMessage.structured_output` is validated into `Review`, scored, saved to
   `reports/<id>.json` and returned. The workspace is deleted.

## Auth
- No user auth (local tool). The agent authenticates to Anthropic with `ANTHROPIC_API_KEY`
  from `.env`. `GITHUB_TOKEN` is optional, for private repos.

## External Dependencies
- Anthropic API, through the Claude Agent SDK (bundled Claude Code runtime).
- GitHub raw content (`raw.githubusercontent.com`).
- highlight.js from cdnjs in the browser.

## Operational Concerns
- **Sandbox:** the agent's Bash runs in the OS sandbox with `allowUnsandboxedCommands: False`
  — no network, writes limited to the workspace. Code under review is never run outside it.
- **Cost:** each review is capped by `maxTurns` (agent `.md`) and `REVIEW_MAX_BUDGET_USD`
  (default $2). Reviews are never auto-retried.
- **Failures:** mapped to the `{ "error": ... }` shape per the `error-handling` skill.

## Change Log
- 2026-10-07 — Initial build. Review moved from a direct Anthropic SDK call to the
  `code-reviewer` Markdown agent run by the Claude Agent SDK; backend ported to Python/FastAPI.
