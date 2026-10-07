from pathlib import Path
from typing import Literal, Optional

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

load_dotenv()

from .github import FetchError  # noqa: E402
from .reviewer import ReviewError  # noqa: E402
from .service import run_review, to_markdown  # noqa: E402
from .store import list_reports, load_report  # noqa: E402

FRONTEND_DIR = Path(__file__).resolve().parents[2] / "frontend"

app = FastAPI(title="AI Code Reviewer")


class ReviewRequest(BaseModel):
    kind: Literal["github", "paste", "upload"]
    url: Optional[str] = None
    code: Optional[str] = None
    filename: Optional[str] = None


@app.exception_handler(FetchError)
@app.exception_handler(ReviewError)
async def _known_error(_: Request, err: Exception) -> JSONResponse:
    return JSONResponse({"error": str(err)}, status_code=getattr(err, "status", 500))


@app.exception_handler(HTTPException)
async def _http_error(_: Request, err: HTTPException) -> JSONResponse:
    return JSONResponse({"error": err.detail}, status_code=err.status_code)


@app.exception_handler(RequestValidationError)
async def _validation_error(_: Request, err: RequestValidationError) -> JSONResponse:
    first = err.errors()[0] if err.errors() else {}
    field = ".".join(str(p) for p in first.get("loc", [])[1:]) or "body"
    return JSONResponse({"error": f"Invalid request: {field} — {first.get('msg', 'bad input')}"}, status_code=422)


@app.post("/api/review")
async def create_review(body: ReviewRequest):
    return await run_review(body.kind, url=body.url, code=body.code, filename=body.filename)


@app.get("/api/reviews")
def get_reviews():
    return list_reports()


@app.get("/api/reviews/{report_id}")
def get_review(report_id: str, format: Optional[str] = None):
    report = load_report(report_id)
    if report is None:
        raise HTTPException(404, "Report not found.")
    if format == "md":
        return PlainTextResponse(
            to_markdown(report),
            media_type="text/markdown",
            headers={"Content-Disposition": f'attachment; filename="{report.id}.md"'},
        )
    return report


app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
