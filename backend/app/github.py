import os
from pathlib import PurePosixPath
from typing import Tuple
from urllib.parse import urlparse

import httpx

MAX_BYTES = 500_000

LANGUAGES = {
    "py": "Python", "js": "JavaScript", "mjs": "JavaScript", "cjs": "JavaScript", "jsx": "JavaScript",
    "ts": "TypeScript", "tsx": "TypeScript", "java": "Java", "kt": "Kotlin", "go": "Go", "rb": "Ruby",
    "rs": "Rust", "cs": "C#", "cpp": "C++", "cc": "C++", "c": "C", "h": "C", "php": "PHP", "swift": "Swift",
    "scala": "Scala", "sh": "Shell", "sql": "SQL",
}


class FetchError(Exception):
    def __init__(self, message: str, status: int = 400):
        super().__init__(message)
        self.status = status


def detect_language(filename: str) -> str:
    return LANGUAGES.get(PurePosixPath(filename).suffix.lstrip(".").lower(), "Unknown")


def to_raw_url(url: str) -> Tuple[str, str]:
    """Convert a GitHub file URL (blob or raw) into a raw.githubusercontent.com URL. Returns (raw_url, filename)."""
    parsed = urlparse(url.strip())
    if parsed.scheme != "https" or not parsed.netloc:
        raise FetchError("Not a valid https URL.")

    parts = [p for p in parsed.path.split("/") if p]
    if parsed.netloc == "github.com":
        # /{owner}/{repo}/blob/{ref}/{path...}
        if len(parts) < 5 or parts[2] not in ("blob", "raw"):
            raise FetchError("Expected a GitHub file URL like https://github.com/owner/repo/blob/branch/path/file.py")
        owner, repo, _, ref, *path = parts
        return f"https://raw.githubusercontent.com/{owner}/{repo}/{ref}/{'/'.join(path)}", path[-1]
    if parsed.netloc == "raw.githubusercontent.com":
        if len(parts) < 4:
            raise FetchError("Incomplete raw.githubusercontent.com URL.")
        return parsed._replace(query="", fragment="").geturl(), parts[-1]
    raise FetchError("Only github.com and raw.githubusercontent.com URLs are allowed.")


def fetch_github_file(url: str) -> Tuple[str, str]:
    """Download a file from GitHub. Returns (code, filename)."""
    raw_url, filename = to_raw_url(url)
    headers = {}
    if os.getenv("GITHUB_TOKEN"):
        headers["Authorization"] = f"Bearer {os.environ['GITHUB_TOKEN']}"

    try:
        res = httpx.get(raw_url, headers=headers, timeout=20, follow_redirects=False)
    except httpx.HTTPError:
        raise FetchError("Could not reach GitHub.", 502)
    if res.status_code == 404:
        raise FetchError("File not found (404). Check the path, or set GITHUB_TOKEN for private repos.", 404)
    if res.status_code != 200:
        raise FetchError(f"GitHub returned HTTP {res.status_code}.", 502)
    if len(res.content) > MAX_BYTES:
        raise FetchError("File is larger than 500 KB.", 413)
    return res.text, filename
