from .schema import SEVERITIES, Review, Score

PENALTY = {"critical": 25, "high": 12, "medium": 6, "low": 2, "info": 0}


def score(review: Review) -> Score:
    counts = {s: 0 for s in SEVERITIES}
    for finding in [*review.style, *review.bugs, *review.security]:
        counts[finding.severity] += 1

    value = max(0, min(100, 100 - sum(counts[s] * PENALTY[s] for s in SEVERITIES)))
    grade = "A" if value >= 90 else "B" if value >= 80 else "C" if value >= 70 else "D" if value >= 60 else "F"
    return Score(value=value, grade=grade, counts=counts)
