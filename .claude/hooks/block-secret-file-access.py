#!/usr/bin/env python3
"""PreToolUse guardrail: hard-blocks any tool access to env/secret files.

permissions.deny only covers the exact tool+pattern listed and can't see inside a Bash
command string. This hook inspects the target of every call, so `cat .env`, `Read(.env)`
and `grep -r KEY .env` are all caught the same way. `.env.example` is deliberately allowed:
it is committed template content.

Only fields that NAME a target are inspected - a Write's `content` may legitimately mention
an env file (setup docs, this hook's own source) without touching one.
"""
import json
import re
import sys

SECRET_FILE = re.compile(r"(^|[/\\])\.env(\.local|\.development|\.production)?(?![\w.-])", re.I)
SECRET_IN_COMMAND = re.compile(r"(^|[\s\"'=/\\])[\w./\\-]*\.env(\.local|\.development|\.production)?(?![\w.-])", re.I)
PATH_FIELDS = ("file_path", "path", "notebook_path")


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except ValueError:
        return 0

    tool_input = payload.get("tool_input") or {}
    blocked_path = next(
        (v for v in (tool_input.get(f) for f in PATH_FIELDS) if isinstance(v, str) and SECRET_FILE.search(v)),
        None,
    )
    command = tool_input.get("command") if isinstance(tool_input.get("command"), str) else ""
    if blocked_path or SECRET_IN_COMMAND.search(command):
        target = f": {blocked_path}" if blocked_path else ""
        print(f"[guardrail] Blocked {payload.get('tool_name', 'tool')} call touching an env/secret file{target}. "
              "Use .env.example instead.", file=sys.stderr)
        return 2  # exit code 2 = block the tool call
    return 0


if __name__ == "__main__":
    sys.exit(main())
