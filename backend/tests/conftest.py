import pytest

from app import store
from app.schema import Finding, Metrics, Refactor, Review, Tests


def make_review(**overrides) -> Review:
    data = dict(
        language="Python",
        summary="A small script.",
        style=[Finding(title="camelCase", severity="low", line_start=1, line_end=1,
                       description="d", suggestion="s")],
        bugs=[Finding(title="unchecked index", severity="medium", line_start=2, line_end=3,
                      description="d", suggestion="s")],
        security=[],
        refactors=[Refactor(title="extract main", rationale="r", before="a()", after="def main(): a()")],
        tests=Tests(framework="pytest", filename="test_x.py", code="def test_ok(): pass",
                    notes="run pytest", result="1 passed"),
        metrics=Metrics(maintainability=6, readability=7, testability=4),
    )
    data.update(overrides)
    return Review(**data)


@pytest.fixture(autouse=True)
def isolated_reports(tmp_path, monkeypatch):
    """Never touch the real reports/ directory."""
    monkeypatch.setattr(store, "REPORTS_DIR", tmp_path / "reports")
    return tmp_path / "reports"


@pytest.fixture
def fake_agent(monkeypatch):
    """Replace the agent run so tests never call the Anthropic API."""
    calls = []

    async def fake_review_code(code, filename, language):
        calls.append({"code": code, "filename": filename, "language": language})
        return make_review()

    monkeypatch.setattr("app.service.review_code", fake_review_code)
    monkeypatch.setattr("app.service.agent_model", lambda: "test-model")
    return calls
