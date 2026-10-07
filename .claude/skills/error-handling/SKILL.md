---
name: error-handling
description: Design or review how errors are detected, classified, logged, and returned. Use when adding an API error response, choosing an HTTP status code, handling an agent or GitHub failure, or surfacing a failure in the dashboard.
---

# Error Handling

## Principles
- Fail fast on invalid input.
- Return safe, actionable messages; keep internal details (stack traces, agent stderr,
  API keys) in logs only.
- One error shape everywhere.

## API response shape
Every non-2xx response from `/api/*` is:

```json
{ "error": "human-readable, actionable message" }
```

The dashboard shows `error` verbatim, so write it for the user.

Raise `FetchError(message, status)` for input/GitHub problems and `ReviewError(message, status)`
for agent problems; the handlers in `server.py` turn them into this shape. Request validation
failures are converted to the same shape with status 422.

## Status codes
| Code | Use for |
|---|---|
| `400` | Malformed input, bad URL, disallowed host, empty code |
| `401` | Missing or invalid `ANTHROPIC_API_KEY` |
| `404` | GitHub file or report not found |
| `413` | File over 500 KB |
| `422` | Request validation failure; agent refused or hit its turn limit |
| `429` | Anthropic rate limit |
| `502` | GitHub or the agent runtime failed, or the agent returned an invalid review |

## Retry
- Do not auto-retry a review: each run costs money. Let the user press Review again.
- Never retry validation errors.

## Tests
Every new error path gets a test asserting both the status and the `error` message.
