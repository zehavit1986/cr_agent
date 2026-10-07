import secrets
import time
from datetime import datetime, timezone
from typing import Optional

from .github import FetchError, detect_language, fetch_github_file
from .reviewer import agent_model, review_code
from .schema import Finding, ReviewReport, Source
from .scoring import score
from .store import save_report, slug

MAX_BYTES = 500_000


async def run_review(kind: str, url: Optional[str] = None, code: Optional[str] = None,
               filename: Optional[str] = None) -> ReviewReport:
    if kind == "github":
        if not url:
            raise FetchError("A GitHub URL is required.")
        code, filename = fetch_github_file(url)
    else:
        code = code or ""
        filename = (filename or "").strip() or "snippet.txt"
        if not code.strip():
            raise FetchError("No code provided.")
        if len(code.encode()) > MAX_BYTES:
            raise FetchError("Code is larger than 500 KB.", 413)
        url = None

    review = await review_code(code, filename, detect_language(filename))
    report = ReviewReport(
        id=f"{slug(filename)}-{int(time.time() * 1000):x}{secrets.token_hex(2)}",
        createdAt=datetime.now(timezone.utc).isoformat(),
        source=Source(kind=kind, url=url, filename=filename),
        code=code,
        model=agent_model(),
        review=review,
        score=score(review),
    )
    save_report(report)
    return report


def _findings(title: str, items: "list[Finding]") -> str:
    out = f"## {title} ({len(items)})\n\n"
    if not items:
        return out + "_No issues found._\n"
    return out + "\n".join(
        f"### [{f.severity.upper()}] {f.title} — lines {f.line_start}-{f.line_end}\n\n"
        f"{f.description}\n\n**Suggestion:** {f.suggestion}\n"
        for f in items
    )


def to_markdown(r: ReviewReport) -> str:
    rv, s = r.review, r.score
    c = s.counts
    parts = [
        f"# Code Review: {r.source.filename}",
        "",
        f"- Source: {r.source.url or r.source.kind}",
        f"- Reviewed: {r.createdAt} with `{r.model}`",
        f"- **Quality score: {s.value}/100 ({s.grade})** — critical {c['critical']}, high {c['high']}, "
        f"medium {c['medium']}, low {c['low']}, info {c['info']}",
        f"- Metrics: maintainability {rv.metrics.maintainability}/10, readability {rv.metrics.readability}/10, "
        f"testability {rv.metrics.testability}/10",
        "",
        f"## Summary\n\n{rv.summary}\n",
        _findings("Bugs", rv.bugs),
        _findings("Security", rv.security),
        _findings("Style", rv.style),
        f"## Suggested Refactors ({len(rv.refactors)})\n",
        *(
            f"### {x.title}\n\n{x.rationale}\n\n**Before**\n\n```\n{x.before}\n```\n\n**After**\n\n```\n{x.after}\n```\n"
            for x in rv.refactors
        ),
        f"## Generated Tests ({rv.tests.framework}) — `{rv.tests.filename}`\n\n**Result:** {rv.tests.result}\n\n{rv.tests.notes}\n\n```\n{rv.tests.code}\n```\n",
    ]
    return "\n".join(parts)
