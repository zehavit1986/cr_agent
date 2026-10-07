"""Load an agent definition from .claude/agents/<name>.md (YAML frontmatter + Markdown instructions)."""
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

import yaml

AGENTS_DIR = Path(__file__).resolve().parents[2] / ".claude" / "agents"


@dataclass(frozen=True)
class AgentSpec:
    name: str
    description: str
    prompt: str
    tools: List[str]
    model: Optional[str]
    effort: Optional[str]
    max_turns: Optional[int]


def load_agent(name: str) -> AgentSpec:
    text = (AGENTS_DIR / f"{name}.md").read_text()
    if not text.startswith("---"):
        raise ValueError(f"{name}.md has no YAML frontmatter")
    _, frontmatter, body = text.split("---", 2)
    meta = yaml.safe_load(frontmatter) or {}

    tools = meta.get("tools") or []
    if isinstance(tools, str):
        tools = [t.strip() for t in tools.split(",") if t.strip()]

    return AgentSpec(
        name=meta.get("name", name),
        description=meta.get("description", ""),
        prompt=body.strip(),
        tools=tools,
        model=meta.get("model"),
        effort=meta.get("effort"),
        max_turns=meta.get("maxTurns"),
    )
