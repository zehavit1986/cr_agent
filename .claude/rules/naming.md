# Naming

Applies to API routes, Pydantic models, modules, files, and JSON fields.

- Use the canonical term from `.doc/glossary.md`, never a synonym:
  - `review` — the agent's structured output (not `analysis`, `audit`)
  - `report` — a stored review plus source, score and metadata (not `result`)
  - `finding` — one style/bug/security issue (not `issue`, `problem`)
  - `severity` — `critical | high | medium | low | info` (not `level`, `priority`)
  - `score` / `grade` — the deterministic 0–100 value and its letter
- Routes are under `/api/`: `/api/review` (create), `/api/reviews` (list), `/api/reviews/{id}`.
- Python: `snake_case` functions and modules, `PascalCase` models. JSON fields from the agent
  stay `snake_case` (`line_start`); report metadata keeps its existing `createdAt`.
- Document a new shared term in `.doc/glossary.md` before using it broadly.
