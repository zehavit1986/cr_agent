---
name: writing-tests
description: Write or review tests for this repository. Use when adding tests for a new feature, writing a regression test for a bug fix, or judging whether coverage is good enough. Covers what must be covered, how to mock the review agent, and how to run the suite.
---

# Writing Tests

## Principles
- Test **behavior**, not implementation details.
- Deterministic and isolated: no network, no real Anthropic API calls, no shared state.
- Every bug fix gets a regression test that fails before the fix and passes after.

## Must be covered
- `github.py`: URL conversion, host allow-list, 404 and size-cap errors (mock `httpx.get`).
- `scoring.py`: score and grade boundaries.
- `store.py`: save/load/list, and that ids containing `/` or `..` are rejected.
- `server.py`: every route's happy path and its error shape (FastAPI `TestClient`).
- `agent.py`: frontmatter parsing of `.claude/agents/code-reviewer.md`.

## Mocking the review agent
Never run the real agent in tests. Patch the function the service awaits:

```python
async def fake_review_code(code, filename, language):
    return Review(...)  # minimal valid Review

monkeypatch.setattr("app.service.review_code", fake_review_code)
```

Point `app.store.REPORTS_DIR` at `tmp_path` so tests never touch `reports/`.

## Structure
- Setup → action → assertion. Descriptive names: `test_rejects_non_github_host`.
- One primary assertion intent per test. Minimal fixtures; never real secrets.

## Running
| Suite | Location | Command |
|---|---|---|
| Backend | `backend/tests/` | `cd backend && ../.venv/bin/python -m pytest -q` |

When a test fails, fix the code — not the test.
