from app.agent import load_agent
from app.schema import Finding
from app.scoring import score

from .conftest import make_review


def finding(severity: str) -> Finding:
    return Finding(title="t", severity=severity, line_start=1, line_end=1, description="d", suggestion="s")


def test_clean_review_scores_100_a():
    result = score(make_review(style=[], bugs=[], security=[]))
    assert (result.value, result.grade) == (100, "A")


def test_score_subtracts_weighted_penalties():
    review = make_review(style=[finding("low")], bugs=[finding("high"), finding("medium")], security=[finding("info")])
    result = score(review)
    assert result.value == 100 - 2 - 12 - 6 - 0
    assert result.counts == {"critical": 0, "high": 1, "medium": 1, "low": 1, "info": 1}


def test_score_never_drops_below_zero():
    result = score(make_review(security=[finding("critical")] * 10))
    assert (result.value, result.grade) == (0, "F")


def test_grade_boundaries():
    assert score(make_review(style=[finding("low")] * 5, bugs=[], security=[])).grade == "A"   # 90
    assert score(make_review(style=[finding("low")] * 6, bugs=[], security=[])).grade == "B"   # 88
    assert score(make_review(style=[finding("low")] * 15, bugs=[], security=[])).grade == "C"  # 70
    assert score(make_review(style=[finding("low")] * 20, bugs=[], security=[])).grade == "D"  # 60
    assert score(make_review(style=[finding("low")] * 21, bugs=[], security=[])).grade == "F"  # 58


def test_loads_code_reviewer_agent_definition():
    spec = load_agent("code-reviewer")
    assert spec.name == "code-reviewer"
    assert spec.model
    assert set(spec.tools) >= {"Read", "Write", "Bash"}
    assert spec.max_turns and spec.max_turns > 0
    assert "## Workflow" in spec.prompt
    assert not spec.prompt.startswith("---")
