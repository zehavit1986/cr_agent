import pytest
from fastapi.testclient import TestClient

from app import reviewer
from app.server import app

client = TestClient(app)


def test_paste_review_returns_full_report(fake_agent):
    res = client.post("/api/review", json={"kind": "paste", "code": "x = 1\n", "filename": "a.py"})
    assert res.status_code == 200
    report = res.json()
    assert set(report["review"]) >= {"style", "bugs", "security", "refactors", "tests", "metrics"}
    assert report["score"] == {"value": 92, "grade": "A",
                               "counts": {"critical": 0, "high": 0, "medium": 1, "low": 1, "info": 0}}
    assert report["source"] == {"kind": "paste", "url": None, "filename": "a.py"}
    assert fake_agent[0]["language"] == "Python"


def test_review_is_saved_listed_and_exportable(fake_agent):
    created = client.post("/api/review", json={"kind": "upload", "code": "x = 1", "filename": "b.py"}).json()

    listed = client.get("/api/reviews").json()
    assert [r["id"] for r in listed] == [created["id"]]

    fetched = client.get(f"/api/reviews/{created['id']}")
    assert fetched.status_code == 200 and fetched.json()["id"] == created["id"]

    md = client.get(f"/api/reviews/{created['id']}?format=md")
    assert md.status_code == 200
    assert md.headers["content-type"].startswith("text/markdown")
    assert "# Code Review: b.py" in md.text and "**Result:** 1 passed" in md.text


def test_github_review_rejects_other_hosts(fake_agent):
    res = client.post("/api/review", json={"kind": "github", "url": "https://evil.example.com/a.py"})
    assert res.status_code == 400
    assert res.json() == {"error": "Only github.com and raw.githubusercontent.com URLs are allowed."}
    assert fake_agent == []


def test_empty_paste_is_rejected(fake_agent):
    res = client.post("/api/review", json={"kind": "paste", "code": "   "})
    assert res.status_code == 400
    assert res.json() == {"error": "No code provided."}


def test_invalid_body_uses_error_shape():
    res = client.post("/api/review", json={"kind": "bogus"})
    assert res.status_code == 422
    assert res.json()["error"].startswith("Invalid request: kind")


@pytest.mark.parametrize("report_id", ["..", "..%2F..%2Fsecret", "a%2Fb", "missing"])
def test_unknown_or_traversal_report_ids_return_404(report_id):
    assert client.get(f"/api/reviews/{report_id}").status_code == 404


def test_missing_api_key_returns_401(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    res = client.post("/api/review", json={"kind": "paste", "code": "x = 1", "filename": "a.py"})
    assert res.status_code == 401
    assert "ANTHROPIC_API_KEY" in res.json()["error"]


def test_agent_errors_are_returned_in_error_shape(monkeypatch):
    async def failing_review(*args):
        raise reviewer.ReviewError("Rate limited by the Anthropic API. Try again in a moment.", 429)

    monkeypatch.setattr("app.service.review_code", failing_review)
    res = client.post("/api/review", json={"kind": "paste", "code": "x = 1", "filename": "a.py"})
    assert res.status_code == 429
    assert res.json() == {"error": "Rate limited by the Anthropic API. Try again in a moment."}


def test_dashboard_is_served():
    res = client.get("/")
    assert res.status_code == 200 and "AI Code Reviewer" in res.text
