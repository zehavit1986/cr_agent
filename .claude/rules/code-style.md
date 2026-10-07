# Code Style

## Python (`backend/`)
- PEP 8, 4-space indent, max line length 120.
- Type hints on every function signature. Pydantic models for anything that crosses the API.
- Module docstring when the module's job is not obvious from its name.
- No module-level side effects beyond constants and `app = FastAPI(...)`.

## JavaScript (`frontend/`)
- Plain ES2020+, no build step. `const` by default, `let` when reassigned.
- Semicolons on, double quotes, 2-space indent — match `frontend/app.js`.

Match the surrounding code for everything this file does not cover.
