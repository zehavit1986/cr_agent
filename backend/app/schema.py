from typing import Dict, List, Literal, Optional

from pydantic import BaseModel, Field

Severity = Literal["critical", "high", "medium", "low", "info"]
SEVERITIES: List[str] = ["critical", "high", "medium", "low", "info"]


class Finding(BaseModel):
    title: str = Field(description="Short headline for the issue")
    severity: Severity
    line_start: int = Field(description="1-based first line the issue applies to")
    line_end: int = Field(description="1-based last line the issue applies to")
    description: str = Field(description="What is wrong and why it matters")
    suggestion: str = Field(description="Concrete fix, may include a short code snippet")


class Refactor(BaseModel):
    title: str
    rationale: str
    before: str = Field(description="Original code excerpt")
    after: str = Field(description="Refactored code")


class Tests(BaseModel):
    framework: str = Field(description="e.g. pytest, jest, go test")
    filename: str = Field(description="Suggested file name for the test file")
    code: str = Field(description="Complete, runnable test file contents")
    notes: str = Field(description="How to run the tests and any assumptions")
    result: str = Field(description="Outcome of actually running the tests, e.g. '6 passed' or 'not run: no toolchain'")


class Metrics(BaseModel):
    maintainability: int = Field(description="1-10")
    readability: int = Field(description="1-10")
    testability: int = Field(description="1-10")


class Review(BaseModel):
    language: str
    summary: str = Field(description="2-4 sentence overview of the code and its overall quality")
    style: List[Finding]
    bugs: List[Finding]
    security: List[Finding]
    refactors: List[Refactor]
    tests: Tests
    metrics: Metrics


class Source(BaseModel):
    kind: Literal["github", "paste", "upload"]
    url: Optional[str] = None
    filename: str


class Score(BaseModel):
    value: int
    grade: str
    counts: Dict[str, int]


class ReviewReport(BaseModel):
    id: str
    createdAt: str
    source: Source
    code: str
    model: str
    review: Review
    score: Score
