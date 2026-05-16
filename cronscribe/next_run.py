"""next_run.py – Compute and format the next N run times for a cron expression."""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from cronscribe.preview import get_next_executions
from cronscribe.validator import validate


class NextRunResult:
    """Holds the result of a next-run query."""

    def __init__(
        self,
        expression: str,
        runs: List[datetime],
        is_valid: bool,
        error: Optional[str] = None,
    ) -> None:
        self.expression = expression
        self.runs = runs
        self.is_valid = is_valid
        self.error = error

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"NextRunResult(expression={self.expression!r}, "
            f"runs={self.runs!r}, is_valid={self.is_valid})"
        )


def get_next_runs(
    expression: str,
    count: int = 5,
    after: Optional[datetime] = None,
) -> NextRunResult:
    """Return the next *count* execution datetimes for *expression*.

    Parameters
    ----------
    expression:
        A valid 5-field cron expression.
    count:
        How many future datetimes to return (1-50).
    after:
        Compute runs after this moment; defaults to ``datetime.now()``.
    """
    if count < 1 or count > 50:
        raise ValueError("count must be between 1 and 50")

    result = validate(expression)
    if not result.is_valid:
        return NextRunResult(
            expression=expression,
            runs=[],
            is_valid=False,
            error="; ".join(result.errors),
        )

    base = after or datetime.now()
    runs = get_next_executions(expression, count=count, after=base)
    return NextRunResult(expression=expression, runs=runs, is_valid=True)


def format_next_runs(result: NextRunResult, fmt: str = "%Y-%m-%d %H:%M") -> str:
    """Render a :class:`NextRunResult` as a human-readable string."""
    if not result.is_valid:
        return f"Invalid expression '{result.expression}': {result.error}"

    lines = [f"Next {len(result.runs)} run(s) for '{result.expression}':"]
    for i, dt in enumerate(result.runs, start=1):
        lines.append(f"  {i:>2}. {dt.strftime(fmt)}")
    return "\n".join(lines)
