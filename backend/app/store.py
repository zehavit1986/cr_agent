import json
import re
from pathlib import Path
from typing import List, Optional

from .schema import ReviewReport

REPORTS_DIR = Path(__file__).resolve().parents[2] / "reports"
_ID_RE = re.compile(r"^[\w.-]+$")


def slug(filename: str) -> str:
    stem = re.sub(r"\.[^.]+$", "", filename)
    return re.sub(r"[^\w.-]+", "-", stem) or "snippet"


def save_report(report: ReviewReport) -> None:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    (REPORTS_DIR / f"{report.id}.json").write_text(report.model_dump_json(indent=2))


def load_report(report_id: str) -> Optional[ReviewReport]:
    if not _ID_RE.match(report_id):
        return None
    try:
        return ReviewReport.model_validate_json((REPORTS_DIR / f"{report_id}.json").read_text())
    except (OSError, ValueError):
        return None


def list_reports() -> List[dict]:
    if not REPORTS_DIR.exists():
        return []
    reports = [load_report(p.stem) for p in REPORTS_DIR.glob("*.json")]
    items = [
        {"id": r.id, "createdAt": r.createdAt, "filename": r.source.filename, "score": r.score.value, "grade": r.score.grade}
        for r in reports
        if r is not None
    ]
    return sorted(items, key=lambda i: i["createdAt"], reverse=True)
