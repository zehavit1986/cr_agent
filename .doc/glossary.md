# Glossary

## Purpose
Canonical domain terms used across code, API routes, docs, and plans.

## Core Terms
| Term | Meaning |
|---|---|
| `review` | The agent's structured output for one file: summary, findings, refactors, tests, metrics |
| `report` | A stored review plus its source, code, model, score and timestamp (`reports/<id>.json`) |
| `finding` | One style, bug or security issue, with severity, line range, description and suggestion |
| `dimension` | One of the five review areas: `style`, `bugs`, `security`, `refactors`, `tests` |
| `severity` | `critical`, `high`, `medium`, `low`, `info` — see `code-reviewer.md` for meanings |
| `refactor` | A suggested before/after rewrite with its rationale |
| `metrics` | 1–10 ratings for maintainability, readability, testability |
| `score` | Deterministic 0–100 value: 100 minus severity penalties (25/12/6/2/0) |
| `grade` | Letter for the score: A ≥ 90, B ≥ 80, C ≥ 70, D ≥ 60, else F |
| `source` | Where the code came from: `github` (with URL), `paste`, or `upload` |
| `workspace` | The temp directory the agent runs in for one review, deleted afterwards |

## Naming Alignment
- Keep this glossary aligned with `../.claude/rules/naming.md`.
- Add a new domain term here before using it broadly. Avoid synonyms for existing terms.
