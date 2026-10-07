#!/usr/bin/env python3
"""PreToolUse guardrail: enforces the "Allowed paths" sections in .claude/agents/*.md.

The agent files only *ask* an agent to stay in its lane. This hook reads the AGENT_ROLE env
var (set by whoever launches a sub-agent, e.g. `AGENT_ROLE=qa claude --agent qa`) and blocks
any Edit/Write outside that role's allowed paths. With no AGENT_ROLE (interactive sessions,
the orchestrator) it does nothing.
"""
import json
import os
import sys
from pathlib import Path

ALLOWED_WRITE_PREFIXES = {
    "backend": ["backend/", ".claude/agents/code-reviewer.md", ".orchestrate/backend-agent-report.md"],
    "frontend": ["frontend/", ".orchestrate/frontend-agent-report.md"],
    # QA writes its report plus tests - it may add coverage but never feature source.
    "qa": [".orchestrate/qa-report.md", "backend/tests/"],
    "security-reviewer": [".orchestrate/security-report.md"],
}


def to_repo_relative(raw_path: str, root: str) -> str:
    p = Path(raw_path)
    rel = os.path.relpath(p, root) if p.is_absolute() else raw_path
    return rel.replace("\\", "/").removeprefix("./")


def main() -> int:
    role = os.environ.get("AGENT_ROLE")
    allowed = ALLOWED_WRITE_PREFIXES.get(role or "")
    if not allowed:
        return 0

    try:
        payload = json.load(sys.stdin)
    except ValueError:
        return 0

    raw_path = (payload.get("tool_input") or {}).get("file_path") or ""
    if not raw_path:
        return 0

    file_path = to_repo_relative(raw_path, payload.get("cwd") or os.getcwd())
    escapes_repo = file_path.startswith("../") or os.path.isabs(file_path)
    if escapes_repo or not any(file_path.startswith(prefix) for prefix in allowed):
        print(f'[guardrail] "{role}" agent tried to write outside its allowed paths: "{file_path}". '
              f"Allowed: {', '.join(allowed)}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
