#!/usr/bin/env python3
"""PreToolUse guardrail: blocks destructive shell patterns before they run.

Enforces a hard boundary even if the agent's plan or prompt would have allowed the
command, and even under --permission-mode bypassPermissions. Access to env/secret
FILES is handled by block-secret-file-access.py.
"""
import json
import re
import sys

DENY_PATTERNS = [
    re.compile(r"\brm\s+-rf\b", re.I),
    re.compile(r"\bgit\s+push\s+--force", re.I),
    re.compile(r"\bgit\s+reset\s+--hard", re.I),
    re.compile(r"\bgit\s+clean\s+-[a-z]*f", re.I),
]


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except ValueError:
        return 0

    command = (payload.get("tool_input") or {}).get("command") or ""
    match = next((p for p in DENY_PATTERNS if p.search(command)), None)
    if match:
        print(f"[guardrail] Blocked command matching {match.pattern}: {command}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
