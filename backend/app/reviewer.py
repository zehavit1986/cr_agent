"""Runs the code-reviewer agent (.claude/agents/code-reviewer.md) with the Claude Agent SDK."""
import os
import sys
import tempfile
from pathlib import Path

from claude_agent_sdk import (
    ClaudeAgentOptions,
    ClaudeSDKError,
    CLIConnectionError,
    ProcessError,
    ResultMessage,
    query,
)
from pydantic import ValidationError

from .agent import load_agent
from .schema import Review

AGENT_NAME = "code-reviewer"
MAX_BUDGET_USD = float(os.getenv("REVIEW_MAX_BUDGET_USD", "2.0"))


class ReviewError(Exception):
    def __init__(self, message: str, status: int = 500):
        super().__init__(message)
        self.status = status


def _forward_stderr(line: str) -> None:
    # The runtime warns that claude.ai connectors are off whenever an API key is set. That is
    # expected here (the agent uses no connectors), so drop it and pass everything else through.
    if "claude.ai connectors are disabled" not in line:
        print(line, file=sys.stderr)


def agent_model() -> str:
    return os.getenv("REVIEW_MODEL") or load_agent(AGENT_NAME).model or "default"


async def review_code(code: str, filename: str, language: str) -> Review:
    if not os.getenv("ANTHROPIC_API_KEY"):
        raise ReviewError("Anthropic API key is missing. Set ANTHROPIC_API_KEY in .env.", 401)

    spec = load_agent(AGENT_NAME)
    safe_name = Path(filename).name or "snippet.txt"

    with tempfile.TemporaryDirectory(prefix="review-") as workspace:
        Path(workspace, safe_name).write_text(code)

        options = ClaudeAgentOptions(
            system_prompt=spec.prompt,
            model=os.getenv("REVIEW_MODEL") or spec.model,
            effort=spec.effort,
            max_turns=spec.max_turns,
            max_budget_usd=MAX_BUDGET_USD,
            tools=spec.tools,
            allowed_tools=spec.tools,
            permission_mode="dontAsk",
            cwd=workspace,
            # Bash runs the generated tests against untrusted code: keep it in the OS sandbox,
            # with no escape hatch. The sandbox also limits writes to the workspace and has no network.
            sandbox={"enabled": True, "autoAllowBashIfSandboxed": True, "allowUnsandboxedCommands": False},
            # Don't load user/project settings from the machine: the agent .md is the whole config.
            setting_sources=[],
            # Put this project's Python (with pytest) first on PATH for the agent's Bash tool.
            env={"PATH": f"{Path(sys.executable).parent}{os.pathsep}{os.environ.get('PATH', '')}"},
            output_format={"type": "json_schema", "schema": Review.model_json_schema()},
            stderr=_forward_stderr,
        )
        prompt = (
            f"Review the file `{safe_name}` (language: {language}) in the current directory. "
            "Follow your workflow: read it, review it, write and run the tests, then return the structured review."
        )

        result = None
        try:
            async for message in query(prompt=prompt, options=options):
                if isinstance(message, ResultMessage):
                    result = message
        except CLIConnectionError:
            raise ReviewError("Could not start the Claude agent runtime.", 502)
        except ProcessError as err:
            raise ReviewError(f"The review agent exited with an error (code {err.exit_code}).", 502)
        except ClaudeSDKError as err:
            raise ReviewError(f"Agent error: {err}", 502)

    if result is None:
        raise ReviewError("The review agent finished without a result.", 502)
    if result.is_error:
        detail = "; ".join(result.errors or []) or result.subtype
        if result.api_error_status == 401:
            raise ReviewError("Anthropic API key is invalid. Check ANTHROPIC_API_KEY in .env.", 401)
        if result.api_error_status == 429:
            raise ReviewError("Rate limited by the Anthropic API. Try again in a moment.", 429)
        raise ReviewError(f"The review agent failed: {detail}", 502)

    try:
        return Review.model_validate(result.structured_output)
    except ValidationError:
        raise ReviewError("The agent returned a review that did not match the expected format.", 502)
