"""Headless review: python -m app.cli <github file url>"""
import asyncio
import sys
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

from .github import FetchError  # noqa: E402
from .reviewer import ReviewError  # noqa: E402
from .service import run_review, to_markdown  # noqa: E402
from .store import REPORTS_DIR, slug  # noqa: E402


def main(argv: "list[str]") -> int:
    if len(argv) != 1:
        print("Usage: python -m app.cli <github file url>", file=sys.stderr)
        return 1
    url = argv[0]
    print(f"Reviewing {url} ...")
    try:
        report = asyncio.run(run_review("github", url=url))
    except (FetchError, ReviewError) as err:
        print(f"Error: {err}", file=sys.stderr)
        return 1

    base = slug(report.source.filename)
    test_file = Path(report.review.tests.filename).name or f"test_{base}.py"
    (REPORTS_DIR / f"{base}.md").write_text(to_markdown(report))
    (REPORTS_DIR / test_file).write_text(report.review.tests.code)

    print(f"\nScore: {report.score.value}/100 ({report.score.grade})")
    print(f"Findings: {report.score.counts}")
    print(f"Saved: reports/{report.id}.json, reports/{base}.md, reports/{test_file}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
