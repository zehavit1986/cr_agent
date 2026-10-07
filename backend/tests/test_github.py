import httpx
import pytest

from app import github
from app.github import FetchError, detect_language, fetch_github_file, to_raw_url

TARGET = "https://github.com/zehavit1986/ai4dev-agent-files/blob/main/10-messages.py"


def test_converts_blob_url_to_raw_url():
    raw, filename = to_raw_url(TARGET)
    assert raw == "https://raw.githubusercontent.com/zehavit1986/ai4dev-agent-files/main/10-messages.py"
    assert filename == "10-messages.py"


def test_keeps_nested_paths():
    raw, filename = to_raw_url("https://github.com/o/r/blob/dev/src/pkg/mod.py")
    assert raw == "https://raw.githubusercontent.com/o/r/dev/src/pkg/mod.py"
    assert filename == "mod.py"


def test_accepts_raw_url_as_is():
    raw, filename = to_raw_url("https://raw.githubusercontent.com/o/r/main/a.py")
    assert raw == "https://raw.githubusercontent.com/o/r/main/a.py"
    assert filename == "a.py"


@pytest.mark.parametrize("url", [
    "https://evil.example.com/a.py",
    "https://github.com.evil.com/o/r/blob/main/a.py",
    "http://github.com/o/r/blob/main/a.py",
    "file:///etc/passwd",
    "not a url",
])
def test_rejects_non_github_or_insecure_urls(url):
    with pytest.raises(FetchError) as err:
        to_raw_url(url)
    assert err.value.status == 400


def test_rejects_repo_url_without_file_path():
    with pytest.raises(FetchError):
        to_raw_url("https://github.com/o/r")


def _mock_get(monkeypatch, status=200, body=b"print('hi')\n"):
    def fake_get(url, **kwargs):
        assert kwargs.get("follow_redirects") is False
        return httpx.Response(status, content=body, request=httpx.Request("GET", url))
    monkeypatch.setattr(github.httpx, "get", fake_get)


def test_fetches_file_contents(monkeypatch):
    _mock_get(monkeypatch)
    code, filename = fetch_github_file(TARGET)
    assert code == "print('hi')\n"
    assert filename == "10-messages.py"


def test_missing_file_returns_404_error(monkeypatch):
    _mock_get(monkeypatch, status=404)
    with pytest.raises(FetchError) as err:
        fetch_github_file(TARGET)
    assert err.value.status == 404
    assert "not found" in str(err.value).lower()


def test_rejects_files_over_size_cap(monkeypatch):
    _mock_get(monkeypatch, body=b"x" * (github.MAX_BYTES + 1))
    with pytest.raises(FetchError) as err:
        fetch_github_file(TARGET)
    assert err.value.status == 413


def test_detects_language_from_extension():
    assert detect_language("a.py") == "Python"
    assert detect_language("b.TS") == "TypeScript"
    assert detect_language("README") == "Unknown"
